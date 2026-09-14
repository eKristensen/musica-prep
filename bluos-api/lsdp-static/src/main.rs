// lsdp-static -- a static LSDP responder, and the measuring tape to go with it.
//
// LSDP (Lenbrook Service Discovery Protocol, UDP broadcast on port 11430) is how
// BluOS players are found.  This program answers LSDP queries on behalf of players
// listed in a config file -- "static LSDP", the equivalent of a static mDNS record
// published by avahi.  It replies immediately instead of after the 0-750 ms random
// delay a real player uses, repeats the reply to survive packet loss, and can serve
// several subnets from one host, which is what a UDP broadcast relay is usually
// there to work around.
//
// Three subcommands:
//   serve     answer queries from a static player list (the point of the exercise)
//   discover  run one real discovery round and print a config file for what replied
//   measure   time discovery repeatedly and report how consistent it is
//   selftest  check the wire codec against real captured packets
//
// Protocol reference: bluos-api/bluos-http-api.md section 12.1.  The encoder is
// checked in `selftest` against the captured Bluesound Node N130 announce from
// that section, byte for byte apart from the redacted node id, so the structure
// this program puts on the wire is what a real player puts there.
//
// Linux only: it uses SO_REUSEPORT and getifaddrs(3) directly.  No dependencies.

#![allow(clippy::needless_range_loop)]

use std::collections::HashMap;
use std::fmt::Write as _;
use std::net::{Ipv4Addr, SocketAddr, SocketAddrV4, UdpSocket};
use std::time::{Duration, Instant, SystemTime, UNIX_EPOCH};

#[cfg(not(target_os = "linux"))]
compile_error!("lsdp-static targets Linux (SO_REUSEPORT and getifaddrs are used directly)");

/// Shown in every report and log banner, so a saved run says what produced it.
/// Taken from Cargo.toml rather than written twice: a hand-kept copy drifts the
/// moment someone changes the code without remembering to bump it, and then
/// every saved run claims a version that never produced it.
const VERSION: &str = env!("CARGO_PKG_VERSION");

const LSDP_PORT: u16 = 11430;
const LSDP_HEADER: [u8; 6] = [0x06, b'L', b'S', b'D', b'P', 0x01];
const MSG_QUERY_BROADCAST: u8 = 0x51; // 'Q' -- responders answer by broadcast
const MSG_QUERY_UNICAST: u8 = 0x52; // 'R' -- responders answer by unicast
const MSG_ANNOUNCE: u8 = 0x41; // 'A'
const MSG_DELETE: u8 = 0x44; // 'D'
const CLASS_ALL: u16 = 0xFFFF;
// Controllers accept these four classes only; the check is class[0] == 0 &&
// class[1] in {1, 3, 6, 8}.
const PLAYER_CLASSES: [u16; 4] = [0x0001, 0x0003, 0x0006, 0x0008];

// ---------------------------------------------------------------------------
// wire format
// ---------------------------------------------------------------------------

#[derive(Clone, Debug, PartialEq)]
struct Record {
    class: u16,
    txt: Vec<(String, String)>, // ordered: the wire has no notion of a map
}

#[derive(Clone, Debug, PartialEq)]
struct Node {
    id: Vec<u8>,
    addr: Ipv4Addr,
    records: Vec<Record>,
}

#[derive(Debug, PartialEq)]
enum Msg {
    Query { unicast_reply: bool, classes: Vec<u16> },
    Announce(Node),
    Delete { id: Vec<u8>, classes: Vec<u16> },
    Unhandled { kind: u8 },
}

impl Record {
    fn encoded_len(&self) -> usize {
        let mut n = 3; // class (2) + txt count (1)
        for (k, v) in &self.txt {
            n += 1 + k.len() + 1 + v.len();
        }
        n
    }

    fn get(&self, key: &str) -> Option<&str> {
        self.txt.iter().find(|(k, _)| k == key).map(|(_, v)| v.as_str())
    }
}

fn encode_record(out: &mut Vec<u8>, r: &Record) {
    out.extend_from_slice(&r.class.to_be_bytes());
    out.push(r.txt.len() as u8);
    for (k, v) in &r.txt {
        out.push(k.len() as u8);
        out.extend_from_slice(k.as_bytes());
        out.push(v.len() as u8);
        out.extend_from_slice(v.as_bytes());
    }
}

/// Encode one Announce message (no datagram header).  The caller guarantees the
/// records fit: every message is length-prefixed with a single byte, so a message
/// body cannot exceed 255 bytes including that byte.
fn encode_announce_msg(node: &Node, records: &[Record]) -> Vec<u8> {
    let mut body = vec![MSG_ANNOUNCE];
    body.push(node.id.len() as u8);
    body.extend_from_slice(&node.id);
    body.push(4);
    body.extend_from_slice(&node.addr.octets());
    body.push(records.len() as u8);
    for r in records {
        encode_record(&mut body, r);
    }
    let mut out = Vec::with_capacity(body.len() + 1);
    out.push((body.len() + 1) as u8); // length byte counts itself
    out.extend_from_slice(&body);
    out
}

/// Fixed cost of an Announce message before any records: length, type, node id,
/// address and record count.
fn announce_overhead(node: &Node) -> usize {
    1 + 1 + 1 + node.id.len() + 1 + 4 + 1
}

/// Build the datagram announcing `node`.  Records are packed greedily into as
/// many Announce messages as it takes -- the spec allows an announcement to be
/// split across several messages when one node's info does not fit (the CI580
/// case), and a single length byte caps a message at 255 bytes.
fn encode_announce(node: &Node) -> Result<Vec<u8>, String> {
    let mut out = LSDP_HEADER.to_vec();
    let overhead = announce_overhead(node);
    let mut batch: Vec<Record> = Vec::new();
    let mut used = overhead;
    for r in &node.records {
        let rlen = r.encoded_len();
        if overhead + rlen > 255 {
            return Err(format!(
                "node {}: the record for class 0x{:04X} is {} bytes and cannot fit in one \
                 LSDP message (255 byte limit) -- shorten its TXT values",
                hex(&node.id),
                r.class,
                rlen
            ));
        }
        if used + rlen > 255 || batch.len() == 255 {
            out.extend_from_slice(&encode_announce_msg(node, &batch));
            batch.clear();
            used = overhead;
        }
        used += rlen;
        batch.push(r.clone());
    }
    if !batch.is_empty() || node.records.is_empty() {
        out.extend_from_slice(&encode_announce_msg(node, &batch));
    }
    Ok(out)
}

fn encode_query(kind: u8, classes: &[u16]) -> Vec<u8> {
    let mut body = vec![kind, classes.len() as u8];
    for c in classes {
        body.extend_from_slice(&c.to_be_bytes());
    }
    let mut out = LSDP_HEADER.to_vec();
    out.push((body.len() + 1) as u8);
    out.extend_from_slice(&body);
    out
}

struct Cursor<'a> {
    b: &'a [u8],
    i: usize,
}

impl<'a> Cursor<'a> {
    fn u8(&mut self) -> Result<u8, String> {
        let v = *self.b.get(self.i).ok_or("truncated")?;
        self.i += 1;
        Ok(v)
    }
    fn u16(&mut self) -> Result<u16, String> {
        let hi = self.u8()? as u16;
        let lo = self.u8()? as u16;
        Ok((hi << 8) | lo)
    }
    fn take(&mut self, n: usize) -> Result<&'a [u8], String> {
        if self.i + n > self.b.len() {
            return Err("truncated".into());
        }
        let s = &self.b[self.i..self.i + n];
        self.i += n;
        Ok(s)
    }
    fn lp_string(&mut self) -> Result<String, String> {
        let n = self.u8()? as usize;
        Ok(String::from_utf8_lossy(self.take(n)?).into_owned())
    }
}

/// Parse a datagram into its messages.  Every message is length-prefixed so an
/// unrecognised type is skipped rather than aborting the parse -- the version byte
/// is only bumped for incompatible changes, so a parser must tolerate new types.
fn parse(data: &[u8]) -> Result<Vec<Msg>, String> {
    if data.len() < 6 || &data[1..5] != b"LSDP" {
        return Err("not an LSDP datagram".into());
    }
    let hlen = data[0] as usize;
    if hlen < 6 || hlen > data.len() {
        return Err("bad header length".into());
    }
    let mut msgs = Vec::new();
    let mut i = hlen;
    while i < data.len() {
        let mlen = data[i] as usize;
        if mlen == 0 || i + mlen > data.len() {
            return Err(format!("truncated message at offset {i}"));
        }
        let body = &data[i + 1..i + mlen];
        i += mlen;
        if body.is_empty() {
            continue;
        }
        let mut c = Cursor { b: body, i: 0 };
        let kind = c.u8()?;
        match kind {
            MSG_QUERY_BROADCAST | MSG_QUERY_UNICAST => {
                let n = c.u8()? as usize;
                let mut classes = Vec::with_capacity(n);
                for _ in 0..n {
                    classes.push(c.u16()?);
                }
                msgs.push(Msg::Query { unicast_reply: kind == MSG_QUERY_UNICAST, classes });
            }
            MSG_DELETE => {
                let n = c.u8()? as usize;
                let id = c.take(n)?.to_vec();
                let n = c.u8()? as usize;
                let mut classes = Vec::with_capacity(n);
                for _ in 0..n {
                    classes.push(c.u16()?);
                }
                msgs.push(Msg::Delete { id, classes });
            }
            MSG_ANNOUNCE => {
                let n = c.u8()? as usize;
                let id = c.take(n)?.to_vec();
                let alen = c.u8()? as usize;
                let a = c.take(alen)?;
                // Everything observed is IPv4 and every first-party client filters
                // to IPv4 explicitly; anything else is rejected rather than guessed at.
                if alen != 4 {
                    return Err(format!("announce with a {alen}-byte address (expected IPv4)"));
                }
                let addr = Ipv4Addr::new(a[0], a[1], a[2], a[3]);
                let n = c.u8()? as usize;
                let mut records = Vec::with_capacity(n);
                for _ in 0..n {
                    let class = c.u16()?;
                    let tn = c.u8()? as usize;
                    let mut txt = Vec::with_capacity(tn);
                    for _ in 0..tn {
                        let k = c.lp_string()?;
                        let v = c.lp_string()?;
                        txt.push((k, v));
                    }
                    records.push(Record { class, txt });
                }
                msgs.push(Msg::Announce(Node { id, addr, records }));
            }
            other => msgs.push(Msg::Unhandled { kind: other }),
        }
    }
    Ok(msgs)
}

fn hex(b: &[u8]) -> String {
    let mut s = String::with_capacity(b.len() * 2);
    for x in b {
        let _ = write!(s, "{x:02x}");
    }
    s
}

fn hex_spaced(b: &[u8]) -> String {
    b.iter().map(|x| format!("{x:02X}")).collect::<Vec<_>>().join(" ")
}

// ---------------------------------------------------------------------------
// config file
// ---------------------------------------------------------------------------
//
//   # a comment
//   node 00:00:5e:00:53:03 192.168.10.10
//     service 0x0001 name="Bluesound Node" port=11000 model=N130 version=3.20.52 zs=0
//     service 0x0004 name="Bluesound Node" port=11431
//
// `service` lines attach to the node above them.  Values may be quoted; TXT keys
// keep the order they are written in.  The node id is the player's MAC (any of
// 00:00:5e:00:53:03, 00-00-5e-00-53-03, 00005e005303) or the word `auto`, which
// derives a stable id from the address.

fn parse_class(s: &str) -> Result<u16, String> {
    let t = s.trim();
    let named = match t.to_ascii_lowercase().as_str() {
        "player" => Some(0x0001),
        "server" => Some(0x0002),
        "secondary" => Some(0x0003),
        "sovi-mfg" => Some(0x0004),
        "sovi-keypad" => Some(0x0005),
        "pair-slave" => Some(0x0006),
        "remote-web-ui" => Some(0x0007),
        "hub" => Some(0x0008),
        _ => None,
    };
    if let Some(c) = named {
        return Ok(c);
    }
    let v = if let Some(h) = t.strip_prefix("0x").or_else(|| t.strip_prefix("0X")) {
        u16::from_str_radix(h, 16)
    } else {
        t.parse::<u16>()
    };
    v.map_err(|_| format!("bad class {t:?} (use 0x0001, 1, or a name like `player`)"))
}

fn parse_node_id(s: &str, addr: Ipv4Addr) -> Result<Vec<u8>, String> {
    if s.eq_ignore_ascii_case("auto") {
        // A locally-administered 6-byte id derived from the address: unique on the
        // network and stable across restarts, which is what a cache key needs.
        let o = addr.octets();
        return Ok(vec![0x02, 0x00, o[0], o[1], o[2], o[3]]);
    }
    let clean: String = s.chars().filter(|c| *c != ':' && *c != '-' && *c != '.').collect();
    if clean.len() % 2 != 0 || clean.is_empty() || clean.len() > 510 {
        return Err(format!("bad node id {s:?}"));
    }
    let mut out = Vec::with_capacity(clean.len() / 2);
    let b = clean.as_bytes();
    for i in (0..b.len()).step_by(2) {
        let pair = &clean[i..i + 2];
        out.push(u8::from_str_radix(pair, 16).map_err(|_| format!("bad node id {s:?}"))?);
    }
    Ok(out)
}

/// Split a line into whitespace-separated tokens, honouring "double quotes".
fn tokenize(line: &str) -> Result<Vec<String>, String> {
    let mut out = Vec::new();
    let mut cur = String::new();
    let mut in_quotes = false;
    let mut has = false;
    for ch in line.chars() {
        match ch {
            '"' => {
                in_quotes = !in_quotes;
                has = true;
            }
            c if c.is_whitespace() && !in_quotes => {
                if has {
                    out.push(std::mem::take(&mut cur));
                    has = false;
                }
            }
            c => {
                cur.push(c);
                has = true;
            }
        }
    }
    if in_quotes {
        return Err("unterminated quote".into());
    }
    if has {
        out.push(cur);
    }
    Ok(out)
}

fn parse_config(text: &str) -> Result<Vec<Node>, String> {
    let mut nodes: Vec<Node> = Vec::new();
    for (lineno, raw) in text.lines().enumerate() {
        let line = match raw.find('#') {
            // '#' only starts a comment outside quotes; values rarely contain one,
            // but a quoted value is respected.
            Some(_) if raw.matches('"').count() % 2 == 0 => &raw[..raw.find('#').unwrap()],
            _ => raw,
        };
        let toks = tokenize(line).map_err(|e| format!("line {}: {e}", lineno + 1))?;
        if toks.is_empty() {
            continue;
        }
        let err = |e: String| format!("line {}: {e}", lineno + 1);
        match toks[0].as_str() {
            "node" => {
                if toks.len() != 3 {
                    return Err(err("expected: node <id|auto> <ipv4>".into()));
                }
                let addr: Ipv4Addr =
                    toks[2].parse().map_err(|_| err(format!("bad IPv4 address {:?}", toks[2])))?;
                let id = parse_node_id(&toks[1], addr).map_err(err)?;
                if nodes.iter().any(|n| n.id == id) {
                    return Err(err(format!(
                        "duplicate node id {} -- ids are the cache key and must be unique",
                        hex(&id)
                    )));
                }
                nodes.push(Node { id, addr, records: Vec::new() });
            }
            "service" => {
                let node = nodes
                    .last_mut()
                    .ok_or_else(|| err("`service` before any `node` line".into()))?;
                if toks.len() < 2 {
                    return Err(err("expected: service <class> [key=value ...]".into()));
                }
                let class = parse_class(&toks[1]).map_err(err)?;
                let mut txt: Vec<(String, String)> = Vec::new();
                for t in &toks[2..] {
                    let (k, v) = t
                        .split_once('=')
                        .ok_or_else(|| err(format!("expected key=value, got {t:?}")))?;
                    if k.is_empty() || k.len() > 255 || v.len() > 255 {
                        return Err(err(format!("TXT key/value out of range in {t:?}")));
                    }
                    if txt.iter().any(|(ek, _)| ek == k) {
                        return Err(err(format!("duplicate TXT key {k:?}")));
                    }
                    txt.push((k.to_string(), v.to_string()));
                }
                // A player class with no port is what a client would have to guess at;
                // the documented default is 11000, so say it out loud.
                if PLAYER_CLASSES.contains(&class) && !txt.iter().any(|(k, _)| k == "port") {
                    txt.push(("port".into(), "11000".into()));
                }
                node.records.push(Record { class, txt });
            }
            other => return Err(err(format!("unknown directive {other:?}"))),
        }
    }
    for n in &nodes {
        if n.records.is_empty() {
            return Err(format!("node {} has no `service` lines", hex(&n.id)));
        }
        encode_announce(n)?; // surface any oversize record now, not at 3am
    }
    Ok(nodes)
}

/// Render nodes back out as a config file -- used by `discover`.
fn emit_config(nodes: &[Node], red: &Redactor) -> String {
    let mut s = String::new();
    for n in nodes {
        let id = red.node_id(&n.id);
        let mac: Vec<String> = id.iter().map(|b| format!("{b:02x}")).collect();
        let name = match n.records.iter().find_map(|r| r.get("name")) {
            Some(v) => red.name(v),
            None => String::new(),
        };
        if !name.is_empty() {
            let _ = writeln!(s, "# {name}");
        }
        let _ = writeln!(s, "node {} {}", mac.join(":"), red.ip(n.addr));
        for r in &n.records {
            let mut line = format!("  service 0x{:04X}", r.class);
            for (k, v) in &r.txt {
                let v = &if k == "name" { red.name(v) } else { v.clone() };
                if v.chars().any(|c| c.is_whitespace() || c == '"' || c == '#') {
                    let _ = write!(line, " {k}=\"{}\"", v.replace('"', ""));
                } else {
                    let _ = write!(line, " {k}={v}");
                }
            }
            let _ = writeln!(s, "{line}");
        }
        s.push('\n');
    }
    s
}

// ---------------------------------------------------------------------------
// sockets and interfaces (Linux)
// ---------------------------------------------------------------------------

#[allow(non_camel_case_types)]
type c_void = std::ffi::c_void;

const AF_INET: u16 = 2;
const SOCK_DGRAM: i32 = 2;
const SOL_SOCKET: i32 = 1;
const SO_REUSEADDR: i32 = 2;
const SO_BROADCAST: i32 = 6;
const SO_REUSEPORT: i32 = 15;
const IFF_UP: u32 = 0x1;
const IFF_BROADCAST: u32 = 0x2;
const IFF_LOOPBACK: u32 = 0x8;

#[repr(C)]
struct SockaddrIn {
    sin_family: u16,
    sin_port: u16,
    sin_addr: [u8; 4],
    sin_zero: [u8; 8],
}

#[repr(C)]
struct IfAddrs {
    ifa_next: *mut IfAddrs,
    ifa_name: *const std::ffi::c_char,
    ifa_flags: u32,
    ifa_addr: *const SockaddrIn,
    ifa_netmask: *const SockaddrIn,
    ifa_ifu: *const SockaddrIn, // broadaddr for a broadcast interface
    ifa_data: *mut c_void,
}

extern "C" {
    fn socket(domain: i32, ty: i32, protocol: i32) -> i32;
    fn setsockopt(fd: i32, level: i32, name: i32, val: *const c_void, len: u32) -> i32;
    fn bind(fd: i32, addr: *const SockaddrIn, len: u32) -> i32;
    fn close(fd: i32) -> i32;
    fn getifaddrs(list: *mut *mut IfAddrs) -> i32;
    fn freeifaddrs(list: *mut IfAddrs);
}

#[derive(Clone, Debug)]
struct Iface {
    name: String,
    addr: Ipv4Addr,
    netmask: Ipv4Addr,
    broadcast: Ipv4Addr,
}

impl Iface {
    fn contains(&self, ip: Ipv4Addr) -> bool {
        let (a, m, b) = (u32::from(self.addr), u32::from(self.netmask), u32::from(ip));
        a & m == b & m
    }
}

fn interfaces() -> Result<Vec<Iface>, String> {
    let mut list: *mut IfAddrs = std::ptr::null_mut();
    let mut out = Vec::new();
    unsafe {
        if getifaddrs(&mut list) != 0 {
            return Err(format!("getifaddrs: {}", std::io::Error::last_os_error()));
        }
        let mut p = list;
        while !p.is_null() {
            let e = &*p;
            p = e.ifa_next;
            if e.ifa_addr.is_null() || (*e.ifa_addr).sin_family != AF_INET {
                continue;
            }
            if e.ifa_flags & IFF_UP == 0 || e.ifa_flags & IFF_LOOPBACK != 0 {
                continue;
            }
            if e.ifa_flags & IFF_BROADCAST == 0 || e.ifa_ifu.is_null() {
                continue;
            }
            let name = std::ffi::CStr::from_ptr(e.ifa_name).to_string_lossy().into_owned();
            let addr = Ipv4Addr::from((*e.ifa_addr).sin_addr);
            let netmask = if e.ifa_netmask.is_null() {
                Ipv4Addr::new(255, 255, 255, 0)
            } else {
                Ipv4Addr::from((*e.ifa_netmask).sin_addr)
            };
            let broadcast = Ipv4Addr::from((*e.ifa_ifu).sin_addr);
            if broadcast.is_unspecified() {
                continue;
            }
            out.push(Iface { name, addr, netmask, broadcast });
        }
        freeifaddrs(list);
    }
    Ok(out)
}

/// Bind a UDP socket with the options LSDP needs.  std cannot set socket options
/// before bind(), and SO_REUSEPORT is what lets this run next to another listener
/// on 11430 -- a packet capture, or the controller being tested.
fn bind_socket(port: u16, reuseport: bool) -> Result<UdpSocket, String> {
    use std::os::fd::FromRawFd;
    unsafe {
        let fd = socket(AF_INET as i32, SOCK_DGRAM, 0);
        if fd < 0 {
            return Err(format!("socket: {}", std::io::Error::last_os_error()));
        }
        let on: i32 = 1;
        let p = &on as *const i32 as *const c_void;
        let len = std::mem::size_of::<i32>() as u32;
        let set = |name: i32, what: &str| -> Result<(), String> {
            if setsockopt(fd, SOL_SOCKET, name, p, len) != 0 {
                let e = std::io::Error::last_os_error();
                close(fd);
                return Err(format!("setsockopt {what}: {e}"));
            }
            Ok(())
        };
        set(SO_REUSEADDR, "SO_REUSEADDR")?;
        if reuseport {
            set(SO_REUSEPORT, "SO_REUSEPORT")?;
        }
        set(SO_BROADCAST, "SO_BROADCAST")?;
        let sa = SockaddrIn {
            sin_family: AF_INET,
            sin_port: port.to_be(),
            sin_addr: [0, 0, 0, 0],
            sin_zero: [0; 8],
        };
        if bind(fd, &sa, std::mem::size_of::<SockaddrIn>() as u32) != 0 {
            let e = std::io::Error::last_os_error();
            close(fd);
            return Err(format!("bind 0.0.0.0:{port}: {e}"));
        }
        Ok(UdpSocket::from_raw_fd(fd))
    }
}

// ---------------------------------------------------------------------------
// small utilities
// ---------------------------------------------------------------------------

struct Rng(u64);

impl Rng {
    fn new() -> Self {
        let n = SystemTime::now().duration_since(UNIX_EPOCH).unwrap_or_default().subsec_nanos();
        Rng(n as u64 ^ (std::process::id() as u64) << 21 ^ 0x9E3779B97F4A7C15)
    }
    fn next(&mut self) -> u64 {
        // xorshift64*: plenty for announce jitter
        let mut x = self.0;
        x ^= x >> 12;
        x ^= x << 25;
        x ^= x >> 27;
        self.0 = x;
        x.wrapping_mul(0x2545F4914F6CDD1D)
    }
    fn below(&mut self, n: u64) -> u64 {
        if n == 0 {
            0
        } else {
            self.next() % n
        }
    }
}

/// Broken-down UTC: (year, month, day, hour, minute, second, millisecond).
fn utc_parts() -> (i64, i64, i64, i64, i64, i64, u32) {
    let d = SystemTime::now().duration_since(UNIX_EPOCH).unwrap_or_default();
    let secs = d.as_secs() as i64;
    let days = secs.div_euclid(86_400);
    let sod = secs.rem_euclid(86_400);
    // civil date from days since epoch (Howard Hinnant's algorithm)
    let z = days + 719_468;
    let era = z.div_euclid(146_097);
    let doe = z.rem_euclid(146_097);
    let yoe = (doe - doe / 1460 + doe / 36_524 - doe / 146_096) / 365;
    let y = yoe + era * 400;
    let doy = doe - (365 * yoe + yoe / 4 - yoe / 100);
    let mp = (5 * doy + 2) / 153;
    let day = doy - (153 * mp + 2) / 5 + 1;
    let month = if mp < 10 { mp + 3 } else { mp - 9 };
    let year = if month <= 2 { y + 1 } else { y };
    (year, month, day, sod / 3600, (sod % 3600) / 60, sod % 60, d.subsec_millis())
}

fn now_stamp() -> String {
    let (y, mo, d, h, mi, sec, ms) = utc_parts();
    format!("{y:04}-{mo:02}-{d:02}T{h:02}:{mi:02}:{sec:02}.{ms:03}Z")
}

/// The form used in directory names: 20260912T113923Z.  UTC, and it says so,
/// because a local stamp is ambiguous twice a year and these are meant to be
/// filed and read back much later.
fn file_stamp() -> String {
    let (y, mo, d, h, mi, sec, _) = utc_parts();
    format!("{y:04}{mo:02}{d:02}T{h:02}{mi:02}{sec:02}Z")
}

fn describe(node: &Node, red: &Redactor) -> String {
    let name = match node.records.iter().find_map(|r| r.get("name")) {
        Some(n) => red.name(n),
        None => "(unnamed)".to_string(),
    };
    let classes: Vec<String> = node.records.iter().map(|r| format!("0x{:04X}", r.class)).collect();
    format!("{} [{}] {} {}", red.ip(node.addr), hex(&red.node_id(&node.id)), name, classes.join("+"))
}

/// Watch the segment and print every LSDP datagram, decoded and timestamped.
/// Answers nothing, so it changes nothing -- which is the point: it says when a
/// client asked, when the answers actually arrived, and which address asked.
/// Compare those timestamps against when a controller's screen fills and the
/// difference is the client's own, not the network's.
fn sniff(sock: &UdpSocket, red: &Redactor, run_for: Option<Duration>) -> Result<(), String> {
    let start = Instant::now();
    let mut prev: Option<Instant> = None;
    let mut buf = [0u8; 65_535];
    loop {
        if let Some(limit) = run_for {
            let left = limit.saturating_sub(start.elapsed());
            if left.is_zero() {
                return Ok(());
            }
            sock.set_read_timeout(Some(left)).map_err(|e| e.to_string())?;
        }
        let (n, from) = match sock.recv_from(&mut buf) {
            Ok(v) => v,
            Err(e)
                if e.kind() == std::io::ErrorKind::WouldBlock
                    || e.kind() == std::io::ErrorKind::TimedOut =>
            {
                continue;
            }
            Err(e) => return Err(format!("recv: {e}")),
        };
        let now = Instant::now();
        let delta = prev.map(|p| now.duration_since(p).as_secs_f64()).unwrap_or(0.0);
        prev = Some(now);
        let head = format!(
            "{}  +{:>6.3}  {:<22}",
            &now_stamp()[11..23],
            delta,
            red.sockaddr(from)
        );
        match parse(&buf[..n]) {
            Err(e) => println!("{head} unparseable ({e})"),
            Ok(msgs) => {
                let mut first = true;
                for m in msgs {
                    let lead = if first { head.clone() } else { " ".repeat(head.len()) };
                    first = false;
                    match m {
                        Msg::Query { unicast_reply, classes } => {
                            let c: Vec<String> =
                                classes.iter().map(|x| format!("0x{x:04X}")).collect();
                            println!(
                                "{lead} {} query   classes [{}]",
                                if unicast_reply { 'R' } else { 'Q' },
                                c.join(",")
                            );
                        }
                        Msg::Announce(node) => {
                            println!("{lead} A announce {}", describe(&node, red));
                        }
                        Msg::Delete { id, classes } => {
                            let c: Vec<String> =
                                classes.iter().map(|x| format!("0x{x:04X}")).collect();
                            println!(
                                "{lead} D delete   {} classes [{}]",
                                hex(&red.node_id(&id)),
                                c.join(",")
                            );
                        }
                        Msg::Unhandled { kind } => {
                            println!("{lead} ? type 0x{kind:02X} (not a type this tool knows)");
                        }
                    }
                }
            }
        }
    }
}

// ---------------------------------------------------------------------------
// redaction
// ---------------------------------------------------------------------------
//
// The same scheme bluos-probe.py uses, so a measurement from here and a capture
// from there can sit in one published bundle and mean the same thing: RFC 5737
// TEST-NET-1 for addresses, a locally-administered 02:00:00:00:xx:yy pool for
// node ids, Room-A.. for player names.  Structure-preserving, so the output is
// still a valid, readable record; deterministic within a run, so the same player
// is the same placeholder in every line; and not reversible from the output
// alone -- `--key` writes the mapping to a separate file that is not for sharing.

#[derive(Default)]
struct RedactInner {
    ipv4: HashMap<Ipv4Addr, Ipv4Addr>,
    node: HashMap<Vec<u8>, Vec<u8>>,
    name: HashMap<String, String>,
    /// (kind, placeholder, original), in allocation order -- only ever written
    /// to the key file, never to a report.
    key: Vec<(&'static str, String, String)>,
}

struct Redactor {
    on: bool,
    inner: std::cell::RefCell<RedactInner>,
}

/// Addresses that are protocol constants rather than anybody's network.
fn keep_ipv4(a: Ipv4Addr) -> bool {
    let o = a.octets();
    a.is_unspecified()
        || a.is_loopback()
        || a.is_broadcast()
        || a.is_multicast()
        // already a documentation address: redacting it again would be a lie
        || o[..3] == [192, 0, 2]
        || o[..3] == [198, 51, 100]
        || o[..3] == [203, 0, 113]
}

/// The n-th documentation address.  Players start at .11, matching the probe,
/// and spill into the other two documentation ranges if a house somehow has more
/// than 244 of them.
fn doc_addr(n: u32) -> Ipv4Addr {
    match n {
        0..=243 => Ipv4Addr::new(192, 0, 2, 11 + n as u8),
        244..=497 => Ipv4Addr::new(198, 51, 100, (n - 243) as u8),
        _ => Ipv4Addr::new(203, 0, 113, ((n - 497) % 254 + 1) as u8),
    }
}

impl Redactor {
    fn new(on: bool) -> Redactor {
        Redactor { on, inner: std::cell::RefCell::new(RedactInner::default()) }
    }

    fn ip(&self, a: Ipv4Addr) -> Ipv4Addr {
        if !self.on || keep_ipv4(a) {
            return a;
        }
        let mut i = self.inner.borrow_mut();
        if let Some(p) = i.ipv4.get(&a) {
            return *p;
        }
        let ph = doc_addr(i.ipv4.len() as u32);
        i.ipv4.insert(a, ph);
        i.key.push(("address", ph.to_string(), a.to_string()));
        ph
    }

    fn sockaddr(&self, a: SocketAddr) -> String {
        match a {
            SocketAddr::V4(v4) => format!("{}:{}", self.ip(*v4.ip()), v4.port()),
            other => other.to_string(),
        }
    }

    /// Node ids are always a six-byte MAC in practice, so the placeholder is one
    /// too -- 02:00:00:00:xx:yy, locally administered and obviously not real.
    fn node_id(&self, id: &[u8]) -> Vec<u8> {
        if !self.on {
            return id.to_vec();
        }
        let mut i = self.inner.borrow_mut();
        if let Some(p) = i.node.get(id) {
            return p.clone();
        }
        let n = 11 + i.node.len() as u32;
        let ph = vec![0x02, 0x00, 0x00, 0x00, (n >> 8) as u8, n as u8];
        i.node.insert(id.to_vec(), ph.clone());
        i.key.push(("node id", hex(&ph), hex(id)));
        ph
    }

    fn name(&self, n: &str) -> String {
        if !self.on || n.is_empty() {
            return n.to_string();
        }
        let mut i = self.inner.borrow_mut();
        if let Some(p) = i.name.get(n) {
            return p.clone();
        }
        let k = i.name.len();
        let ph = if k < 26 {
            format!("Room-{}", (b'A' + k as u8) as char)
        } else {
            format!("Room-{}", k + 1)
        };
        i.name.insert(n.to_string(), ph.clone());
        i.key.push(("name", ph.clone(), n.to_string()));
        ph
    }

    fn counts(&self) -> (usize, usize, usize) {
        let i = self.inner.borrow();
        (i.ipv4.len(), i.node.len(), i.name.len())
    }

    fn key_file(&self) -> String {
        let mut s = String::from(
            "# DO NOT SHARE. Maps the placeholders in the report back to this\n\
             # network's real addresses, node ids and player names.\n\n",
        );
        for (kind, ph, orig) in &self.inner.borrow().key {
            let _ = writeln!(s, "{kind:<8} {ph:<20} {orig}");
        }
        s
    }
}

/// Scan text for anything that still looks like a real address, MAC or bare-hex
/// node id.  The same idea as the probe's bundle verification: the redactor is
/// only trustworthy if something independent checks its output before it is
/// published.
fn find_unredacted(text: &str) -> Vec<String> {
    const SET: &str = "0123456789abcdefABCDEF.:-";
    let mut out: Vec<String> = Vec::new();
    let mut token = String::new();
    let flush = |t: &str, out: &mut Vec<String>| {
        if t.is_empty() {
            return;
        }
        // a whole token may be a MAC, with either separator
        if let Some(bytes) = mac_shaped(t) {
            if bytes[..4] != [0x02, 0x00, 0x00, 0x00] {
                out.push(format!("MAC-shaped string {t:?}"));
            }
        }
        // ... and each colon-separated piece may be an address or a bare-hex id
        for piece in t.split(':') {
            if let Ok(a) = piece.parse::<Ipv4Addr>() {
                if !keep_ipv4(a) {
                    out.push(format!("IPv4 address {piece:?}"));
                }
            } else if piece.len() == 12 && piece.chars().all(|c| c.is_ascii_hexdigit()) {
                if !piece.to_ascii_lowercase().starts_with("02000000") {
                    out.push(format!("bare-hex node id {piece:?}"));
                }
            }
        }
    };
    for ch in text.chars() {
        if SET.contains(ch) {
            token.push(ch);
        } else {
            flush(&token, &mut out);
            token.clear();
        }
    }
    flush(&token, &mut out);
    out.sort();
    out.dedup();
    out
}

/// Six hex pairs joined by one consistent separator.
fn mac_shaped(t: &str) -> Option<Vec<u8>> {
    for sep in [':', '-'] {
        let parts: Vec<&str> = t.split(sep).collect();
        if parts.len() == 6 && parts.iter().all(|p| p.len() == 2 && p.chars().all(|c| c.is_ascii_hexdigit())) {
            return Some(parts.iter().map(|p| u8::from_str_radix(p, 16).unwrap()).collect());
        }
    }
    None
}

// ---------------------------------------------------------------------------
// serve
// ---------------------------------------------------------------------------

#[derive(Clone, Copy, PartialEq)]
enum Dest {
    /// Answer by broadcast, remembering who asked so --reply-scope arrival
    /// can keep the answer on the subnet the query came from.
    Broadcast(Ipv4Addr),
    To(SocketAddr),
}

struct Job {
    at: Instant,
    node: usize,
    dest: Dest,
    tag: &'static str,
}

struct Serve {
    nodes: Vec<Node>,
    packets: Vec<Vec<u8>>, // encoded announce per node
    dests: Vec<Ipv4Addr>,
    ifaces: Vec<Iface>,
    port: u16,
    arrival_scope: bool,
    /// low and high bounds, in ms: a fixed `--delay-ms 400`, or a range like
    /// `--delay-ms 0-750` to imitate a real player's random reply delay
    delay_ms: (u64, u64),
    repeat: u32,
    spacing_ms: u64,
    interval: u64,
    unicast_echo: bool,
    min_gap: Duration,
    startup: bool,
    verbose: bool,
    red: Redactor,
}

impl Serve {
    fn log(&self, s: &str) {
        println!("{} {}", now_stamp(), s);
    }

    /// Broadcast targets for a reply.  With --reply-scope arrival only the subnet
    /// the query came from is used, which keeps a three-VLAN host from echoing
    /// every answer onto every VLAN.
    fn targets_for(&self, src: Ipv4Addr) -> Vec<Ipv4Addr> {
        if !self.arrival_scope {
            return self.dests.clone();
        }
        let local: Vec<Ipv4Addr> = self
            .ifaces
            .iter()
            .filter(|i| i.contains(src))
            .map(|i| i.broadcast)
            .filter(|b| self.dests.contains(b))
            .collect();
        if local.is_empty() {
            self.dests.clone()
        } else {
            local
        }
    }

    /// Identifies where an answer is going, for the duplicate-query collapse.
    fn dest_key(&self, dest: Dest) -> String {
        match dest {
            Dest::To(a) => format!("u:{a}"),
            Dest::Broadcast(src) => {
                let t: Vec<String> = self.targets_for(src).iter().map(|d| d.to_string()).collect();
                format!("b:{}", t.join(","))
            }
        }
    }

    fn send(&self, sock: &UdpSocket, job: &Job) {
        let pkt = &self.packets[job.node];
        let mut targets: Vec<SocketAddr> = Vec::new();
        match job.dest {
            Dest::To(a) => targets.push(a),
            Dest::Broadcast(src) => {
                for d in self.targets_for(src) {
                    targets.push(SocketAddr::V4(SocketAddrV4::new(d, self.port)));
                }
            }
        }
        for t in targets {
            match sock.send_to(pkt, t) {
                Ok(_) => {
                    if self.verbose {
                        self.log(&format!(
                            "  -> {} {} announce {} ({} bytes)",
                            self.red.sockaddr(t),
                            job.tag,
                            describe(&self.nodes[job.node], &self.red),
                            pkt.len()
                        ));
                    }
                }
                Err(e) => {
                    self.log(&format!("  !! send to {} failed: {e}", self.red.sockaddr(t)))
                }
            }
        }
    }

    fn schedule_burst(
        &self,
        jobs: &mut Vec<Job>,
        now: Instant,
        node: usize,
        dest: Dest,
        tag: &'static str,
        delay_ms: u64,
    ) {
        for k in 0..self.repeat.max(1) {
            let at = now + Duration::from_millis(delay_ms + k as u64 * self.spacing_ms);
            jobs.push(Job { at, node, dest, tag });
        }
    }

    /// One draw from the configured reply delay, per query and per node, the way
    /// a real player draws its own.
    fn draw_delay(&self, rng: &mut Rng) -> u64 {
        let (lo, hi) = self.delay_ms;
        lo + rng.below(hi.saturating_sub(lo) + 1)
    }

    fn run(&self, sock: &UdpSocket) -> Result<(), String> {
        let mut rng = Rng::new();
        let mut jobs: Vec<Job> = Vec::new();
        // Keyed by node *and* by where the answer goes: collapsing a relay's echo
        // of one broadcast query is the point, but two clients asking separately
        // must each get their own answer -- especially for unicast 'R', where the
        // second client would otherwise hear nothing at all.
        let mut last_burst: HashMap<(usize, String), Instant> = HashMap::new();
        let start = Instant::now();

        // Startup burst: a node advertising a service sends seven announces at
        // t = 0, 1, 2, 3, 5, 7, 10 s, the same schedule a client uses for queries.
        for (i, _) in self.nodes.iter().enumerate().filter(|_| self.startup) {
            for t in [0.0f64, 1.0, 2.0, 3.0, 5.0, 7.0, 10.0] {
                let j = rng.below(250) as u64;
                jobs.push(Job {
                    at: start + Duration::from_millis((t * 1000.0) as u64 + j),
                    node: i,
                    dest: Dest::Broadcast(Ipv4Addr::UNSPECIFIED),
                    tag: "startup",
                });
            }
        }
        let mut next_periodic = if self.interval > 0 {
            Some(start + Duration::from_secs(self.interval))
        } else {
            None
        };

        let mut buf = [0u8; 65_535];
        loop {
            // Run everything that has come due, then sleep until the next thing.
            let now = Instant::now();
            let mut due: Vec<Job> = Vec::new();
            jobs.retain(|j| {
                if j.at <= now {
                    due.push(Job { at: j.at, node: j.node, dest: j.dest, tag: j.tag });
                    false
                } else {
                    true
                }
            });
            due.sort_by_key(|j| j.at);
            for j in &due {
                self.send(sock, j);
            }
            if let Some(t) = next_periodic {
                if t <= Instant::now() {
                    self.log("periodic announce");
                    for i in 0..self.nodes.len() {
                        self.send(
                            sock,
                            &Job {
                                at: now,
                                node: i,
                                dest: Dest::Broadcast(Ipv4Addr::UNSPECIFIED),
                                tag: "periodic",
                            },
                        );
                    }
                    // steady state is every 57 s +/- 6 s; on a short test interval
                    // the jitter shrinks with it rather than swamping it
                    let j = (self.interval / 2).min(6) as i64;
                    let secs = self.interval as i64 - j + rng.below(2 * j as u64 + 1) as i64;
                    next_periodic =
                        Some(Instant::now() + Duration::from_secs(secs.max(1) as u64));
                }
            }

            let now = Instant::now();
            let mut wake = jobs.iter().map(|j| j.at).min();
            if let Some(t) = next_periodic {
                wake = Some(wake.map_or(t, |w: Instant| w.min(t)));
            }
            let timeout = wake.map(|w| w.saturating_duration_since(now).max(Duration::from_millis(1)));
            sock.set_read_timeout(timeout).map_err(|e| e.to_string())?;

            let (n, from) = match sock.recv_from(&mut buf) {
                Ok(v) => v,
                Err(e)
                    if e.kind() == std::io::ErrorKind::WouldBlock
                        || e.kind() == std::io::ErrorKind::TimedOut =>
                {
                    continue;
                }
                Err(e) => return Err(format!("recv: {e}")),
            };
            let src_v4 = match from {
                SocketAddr::V4(a) => *a.ip(),
                _ => continue,
            };
            let msgs = match parse(&buf[..n]) {
                Ok(m) => m,
                Err(e) => {
                    if self.verbose {
                        self.log(&format!(
                            "<- {} unparseable ({e}): {}",
                            self.red.sockaddr(from),
                            hex_spaced(&buf[..n])
                        ));
                    }
                    continue;
                }
            };
            for m in msgs {
                // Announce and Delete from other nodes are none of our business; we
                // only answer queries.  That is also what stops our own broadcasts,
                // which loop back to this socket, from feeding themselves.
                let (unicast_reply, classes) = match m {
                    Msg::Query { unicast_reply, classes } => (unicast_reply, classes),
                    _ => continue,
                };
                let wanted = |c: u16| classes.contains(&CLASS_ALL) || classes.contains(&c);
                let matched: Vec<usize> = (0..self.nodes.len())
                    .filter(|i| self.nodes[*i].records.iter().any(|r| wanted(r.class)))
                    .collect();
                let cls: Vec<String> = classes.iter().map(|c| format!("0x{c:04X}")).collect();
                self.log(&format!(
                    "<- {} query '{}' classes [{}] -> {} node(s)",
                    self.red.sockaddr(from),
                    if unicast_reply { 'R' } else { 'Q' },
                    cls.join(","),
                    matched.len()
                ));
                let now = Instant::now();
                for i in matched {
                    // Collapse duplicates: a relay echoing one query onto three
                    // interfaces should not cost three bursts.
                    let dest =
                        if unicast_reply { Dest::To(from) } else { Dest::Broadcast(src_v4) };
                    let key = (i, self.dest_key(dest));
                    if let Some(t) = last_burst.get(&key) {
                        if now.duration_since(*t) < self.min_gap {
                            continue;
                        }
                    }
                    last_burst.insert(key, now);
                    let d = self.draw_delay(&mut rng);
                    if unicast_reply {
                        self.schedule_burst(&mut jobs, now, i, dest, "unicast", d);
                    } else {
                        self.schedule_burst(&mut jobs, now, i, dest, "reply", d);
                        if self.unicast_echo && !src_v4.is_unspecified() {
                            self.schedule_burst(&mut jobs, now, i, Dest::To(from), "echo", d);
                        }
                    }
                }
            }
        }
    }
}

// ---------------------------------------------------------------------------
// client side: discover and measure
// ---------------------------------------------------------------------------

fn send_query(sock: &UdpSocket, dests: &[Ipv4Addr], port: u16, pkt: &[u8]) -> usize {
    let mut sent = 0;
    for d in dests {
        if sock.send_to(pkt, SocketAddr::V4(SocketAddrV4::new(*d, port))).is_ok() {
            sent += 1;
        }
    }
    sent
}

struct Round {
    first_ms: HashMap<String, (u128, Node)>,
    order: Vec<String>,
    datagrams: usize,
    elapsed_ms: u128,
}

/// One discovery round: send the standard seven-packet query burst and listen.
/// Stops early once `expect` distinct player nodes have answered.
fn discovery_round(
    sock: &UdpSocket,
    dests: &[Ipv4Addr],
    port: u16,
    query_kind: u8,
    schedule: &[f64],
    timeout: Duration,
    expect: usize,
    players_only: bool,
    verbose: bool,
    red: &Redactor,
) -> Result<Round, String> {
    let pkt = encode_query(query_kind, &[CLASS_ALL]);
    let start = Instant::now();
    let mut sched: Vec<Duration> = schedule.iter().map(|t| Duration::from_secs_f64(*t)).collect();
    sched.sort();
    let mut next = 0usize;
    let mut round =
        Round { first_ms: HashMap::new(), order: Vec::new(), datagrams: 0, elapsed_ms: 0 };
    let mut buf = [0u8; 65_535];
    loop {
        let now = Instant::now();
        let el = now.duration_since(start);
        if el >= timeout {
            break;
        }
        while next < sched.len() && sched[next] <= el {
            send_query(sock, dests, port, &pkt);
            next += 1;
        }
        let wake = if next < sched.len() {
            (start + sched[next]).saturating_duration_since(now)
        } else {
            timeout - el
        };
        sock.set_read_timeout(Some(wake.max(Duration::from_millis(1))))
            .map_err(|e| e.to_string())?;
        let (n, from) = match sock.recv_from(&mut buf) {
            Ok(v) => v,
            Err(e)
                if e.kind() == std::io::ErrorKind::WouldBlock
                    || e.kind() == std::io::ErrorKind::TimedOut =>
            {
                continue;
            }
            Err(e) => return Err(format!("recv: {e}")),
        };
        let ms = start.elapsed().as_millis();
        let msgs = match parse(&buf[..n]) {
            Ok(m) => m,
            Err(_) => continue,
        };
        let mut counted = false;
        for m in msgs {
            let node = match m {
                Msg::Announce(node) => node,
                _ => continue,
            };
            if !counted {
                round.datagrams += 1;
                counted = true;
            }
            if players_only && !node.records.iter().any(|r| PLAYER_CLASSES.contains(&r.class)) {
                continue;
            }
            let key = hex(&node.id);
            if !round.first_ms.contains_key(&key) {
                if verbose {
                    // stderr, so `discover > players.conf` stays a clean config file
                    eprintln!(
                        "    {:>6} ms  {}  (via {})",
                        ms,
                        describe(&node, red),
                        red.sockaddr(from)
                    );
                }
                round.order.push(key.clone());
                round.first_ms.insert(key, (ms, node));
            }
        }
        if expect > 0 && round.first_ms.len() >= expect {
            break;
        }
    }
    round.elapsed_ms = start.elapsed().as_millis();
    Ok(round)
}

/// Just the times from (round, ms) pairs, sorted, ready for pct().
fn sorted_times(times: &[(usize, u128)]) -> Vec<u128> {
    let mut v: Vec<u128> = times.iter().map(|(_, ms)| *ms).collect();
    v.sort();
    v
}

fn pct(sorted: &[u128], p: f64) -> u128 {
    if sorted.is_empty() {
        return 0;
    }
    let i = ((sorted.len() - 1) as f64 * p).round() as usize;
    sorted[i.min(sorted.len() - 1)]
}

// ---------------------------------------------------------------------------
// selftest
// ---------------------------------------------------------------------------

/// The Bluesound Node N130 announce captured by the `nightvision` project and
/// decoded field by field in bluos-http-api.md section 12.1, rebuilt here byte by
/// byte from that listing -- with the node id replaced by an RFC 7042
/// documentation MAC, as it is in the specification and in `bluos-probe.py`.
/// Every length is unchanged, so reproducing this exactly means the wire
/// structure is what a real player puts there.
fn fixture_announce() -> Vec<u8> {
    let mut e: Vec<u8> = Vec::new();
    e.extend_from_slice(&[0x06, 0x4C, 0x53, 0x44, 0x50, 0x01]); // header
    e.push(0x73); // message length 115
    e.push(0x41); // 'A'
    e.extend_from_slice(&[0x06, 0x00, 0x00, 0x5E, 0x00, 0x53, 0x03]); // node id
    e.extend_from_slice(&[0x04, 0xC0, 0xA8, 0x0A, 0x0A]); // 192.168.10.10
    e.push(0x02); // 2 records
    e.extend_from_slice(&[0x00, 0x01]); // class 0x0001
    e.push(0x05); // 5 TXT
    e.push(0x04);
    e.extend_from_slice(b"name");
    e.push(0x0E);
    e.extend_from_slice(b"Bluesound Node");
    e.push(0x04);
    e.extend_from_slice(b"port");
    e.push(0x05);
    e.extend_from_slice(b"11000");
    e.push(0x05);
    e.extend_from_slice(b"model");
    e.push(0x04);
    e.extend_from_slice(b"N130");
    e.push(0x07);
    e.extend_from_slice(b"version");
    e.push(0x07);
    e.extend_from_slice(b"3.20.52");
    e.push(0x02);
    e.extend_from_slice(b"zs");
    e.push(0x01);
    e.extend_from_slice(b"0");
    e.extend_from_slice(&[0x00, 0x04]); // class 0x0004
    e.push(0x02); // 2 TXT
    e.push(0x04);
    e.extend_from_slice(b"name");
    e.push(0x0E);
    e.extend_from_slice(b"Bluesound Node");
    e.push(0x04);
    e.extend_from_slice(b"port");
    e.push(0x05);
    e.extend_from_slice(b"11431");
    e
}

const FIXTURE_CONFIG: &str = concat!(
    "node 00:00:5e:00:53:03 192.168.10.10\n",
    "  service 0x0001 name=\"Bluesound Node\" port=11000 model=N130 version=3.20.52 zs=0\n",
    "  service 0x0004 name=\"Bluesound Node\" port=11431\n",
);

fn selftest() -> i32 {
    println!("lsdp-static {VERSION}\n");
    let mut fail = 0;
    let mut check = |name: &str, ok: bool, detail: String| {
        if ok {
            println!("ok    {name}");
        } else {
            fail += 1;
            println!("FAIL  {name}\n      {detail}");
        }
    };

    // encoder vs the real captured announce, node id redacted
    let nodes = match parse_config(FIXTURE_CONFIG) {
        Ok(n) => n,
        Err(e) => {
            println!("FAIL  config for the captured N130 parses\n      {e}");
            return 1;
        }
    };
    let got = encode_announce(&nodes[0]).unwrap();
    let want = fixture_announce();
    check(
        "encoded announce is byte-identical to the captured N130 packet (redacted node id)",
        got == want,
        format!("got  {}\n      want {}", hex_spaced(&got), hex_spaced(&want)),
    );
    check(
        "captured announce is 121 bytes with a 115-byte message",
        want.len() == 121 && want[6] == 0x73,
        format!("len {} msglen {}", want.len(), want[6]),
    );

    // queries the shipping controllers send
    let q = encode_query(MSG_QUERY_BROADCAST, &[CLASS_ALL]);
    check(
        "class-0xFFFF query matches the eleven bytes all three controllers send",
        q == vec![0x06, 0x4C, 0x53, 0x44, 0x50, 0x01, 0x05, 0x51, 0x01, 0xFF, 0xFF],
        hex_spaced(&q),
    );
    let q2 = encode_query(MSG_QUERY_BROADCAST, &[0x0001, 0x0004]);
    check(
        "two-class query matches the captured fixture",
        q2 == vec![0x06, 0x4C, 0x53, 0x44, 0x50, 0x01, 0x07, 0x51, 0x02, 0x00, 0x01, 0x00, 0x04],
        hex_spaced(&q2),
    );

    // parser against the same capture
    match parse(&want) {
        Ok(msgs) => {
            let ok = msgs.len() == 1
                && match &msgs[0] {
                    Msg::Announce(n) => {
                        n.addr == Ipv4Addr::new(192, 168, 10, 10)
                            && hex(&n.id) == "00005e005303"
                            && n.records.len() == 2
                            && n.records[0].get("port") == Some("11000")
                            && n.records[0].get("model") == Some("N130")
                            && n.records[1].class == 0x0004
                            && n.records[1].get("port") == Some("11431")
                    }
                    _ => false,
                };
            check("parser reads the captured announce back correctly", ok, format!("{msgs:?}"));
            if let Msg::Announce(n) = &msgs[0] {
                check(
                    "announce round-trips encode -> parse -> encode",
                    encode_announce(n).unwrap() == want,
                    String::new(),
                );
            }
        }
        Err(e) => check("parser reads the captured announce", false, e),
    }

    // the Delete fixture from the same capture set
    let del = vec![
        0x06, 0x4C, 0x53, 0x44, 0x50, 0x01, 0x0E, 0x44, 0x06, 0x00, 0x00, 0x5E, 0x00, 0x53, 0x03,
        0x02, 0x00, 0x01, 0x00, 0x04,
    ];
    check(
        "parses the captured Delete",
        matches!(parse(&del).as_deref(), Ok([Msg::Delete { classes, .. }]) if classes == &[1, 4]),
        format!("{:?}", parse(&del)),
    );

    // robustness
    check("rejects a non-LSDP datagram", parse(b"not an lsdp packet at all").is_err(), String::new());
    check("rejects a truncated datagram", parse(&want[..20]).is_err(), String::new());
    let mut all = true;
    for cut in 1..want.len() {
        // no input should panic; truncation is an error, never a crash
        let _ = parse(&want[..cut]);
        let mut m = want.clone();
        m[cut] = m[cut].wrapping_add(1);
        let _ = parse(&m);
        all &= true;
    }
    check("no truncation or single-byte mutation panics the parser", all, String::new());
    check(
        "rejects a well-formed announce carrying a 16-byte address, as every \
first-party client does",
        {
            // header, then: len 26, 'A', node id 2 bytes, a 16-byte address,
            // one record of class 0x0001 with no TXT.  Structurally valid,
            // IPv6-shaped, and a parser that guessed would emit a garbage address.
            let mut p = LSDP_HEADER.to_vec();
            p.extend_from_slice(&[0x1A, 0x41, 0x02, 0xAA, 0xBB, 0x10]);
            p.extend_from_slice(&[0x20, 0x01, 0x0D, 0xB8, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1]);
            p.extend_from_slice(&[0x01, 0x00, 0x01, 0x00]);
            match parse(&p) {
                Err(e) => e.contains("address"),
                Ok(_) => false,
            }
        },
        format!("{:?}", {
            let mut p = LSDP_HEADER.to_vec();
            p.extend_from_slice(&[0x1A, 0x41, 0x02, 0xAA, 0xBB, 0x10]);
            p.extend_from_slice(&[0x20, 0x01, 0x0D, 0xB8, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1]);
            p.extend_from_slice(&[0x01, 0x00, 0x01, 0x00]);
            parse(&p)
        }),
    );

    // config handling
    check(
        "a player service with no port gets the documented 11000 default",
        parse_config("node auto 10.0.0.5\n service player name=X\n").unwrap()[0].records[0]
            .get("port")
            == Some("11000"),
        String::new(),
    );
    check(
        "`auto` node ids are locally administered and unique per address",
        {
            let a = parse_config("node auto 10.0.0.5\n service player\n").unwrap();
            let b = parse_config("node auto 10.0.0.6\n service player\n").unwrap();
            a[0].id != b[0].id && a[0].id[0] == 0x02
        },
        String::new(),
    );
    check(
        "duplicate node ids are rejected",
        parse_config("node auto 10.0.0.5\n service player\nnode auto 10.0.0.5\n service player\n")
            .is_err(),
        String::new(),
    );
    check(
        "a config with no service lines is rejected",
        parse_config("node auto 10.0.0.5\n").is_err(),
        String::new(),
    );
    let plain = Redactor::new(false);
    check(
        "emitted config round-trips back to the same nodes",
        parse_config(&emit_config(&nodes, &plain)).unwrap() == nodes,
        emit_config(&nodes, &plain),
    );

    // oversize handling: one node with more records than fit in a 255-byte message
    let mut big = String::from("node auto 10.0.0.9\n");
    for i in 0..8 {
        let _ = writeln!(
            big,
            "  service 0x0001 name=\"Player number {i} with a deliberately long name\" port=1100{i}"
        );
    }
    let big_nodes = parse_config(&big).unwrap();
    let pkt = encode_announce(&big_nodes[0]).unwrap();
    let msgs = parse(&pkt).unwrap();
    let total: usize = msgs
        .iter()
        .map(|m| match m {
            Msg::Announce(n) => n.records.len(),
            _ => 0,
        })
        .sum();
    check(
        "a node too big for one message is split across several announces",
        msgs.len() > 1 && total == 8,
        format!("{} messages, {} records", msgs.len(), total),
    );
    check(
        "a single TXT value too long for any message is rejected with a clear error",
        parse_config(&format!("node auto 10.0.0.9\n service 0x0001 name=\"{}\"\n", "x".repeat(250)))
            .is_err(),
        String::new(),
    );

    // redaction
    let red = Redactor::new(true);
    let real: Ipv4Addr = "10.42.7.9".parse().unwrap();
    let real2: Ipv4Addr = "10.42.7.10".parse().unwrap();
    check(
        "the same address always gets the same placeholder, a different one does not",
        red.ip(real) == red.ip(real) && red.ip(real) != red.ip(real2),
        format!("{} {}", red.ip(real), red.ip(real2)),
    );
    check(
        "address placeholders are RFC 5737 documentation addresses",
        red.ip(real).octets()[..3] == [192, 0, 2],
        red.ip(real).to_string(),
    );
    check(
        "protocol constants are left alone",
        [
            Ipv4Addr::UNSPECIFIED,
            Ipv4Addr::new(127, 0, 0, 1),
            Ipv4Addr::new(255, 255, 255, 255),
            Ipv4Addr::new(224, 0, 0, 251),
            Ipv4Addr::new(192, 0, 2, 50),
        ]
        .iter()
        .all(|a| red.ip(*a) == *a),
        String::new(),
    );
    check(
        "node id placeholders are locally administered six-byte ids",
        {
            let ph = red.node_id(&[0x00, 0x00, 0x5E, 0x00, 0x53, 0x03]);
            ph.len() == 6 && ph[..4] == [0x02, 0x00, 0x00, 0x00]
        },
        hex(&red.node_id(&[0x00, 0x00, 0x5E, 0x00, 0x53, 0x03])),
    );
    check(
        "player names become Room-A, Room-B, ...",
        red.name("Stue") == "Room-A" && red.name("Kitchen") == "Room-B" && red.name("Stue") == "Room-A",
        String::new(),
    );
    check(
        "a redactor that is off changes nothing",
        {
            let off = Redactor::new(false);
            off.ip(real) == real && off.name("Stue") == "Stue" && off.node_id(&[1, 2]) == vec![1, 2]
        },
        String::new(),
    );

    // the leak scanner, which is what makes a report safe to publish
    check(
        "the scanner catches a real address, a MAC and a bare-hex node id",
        {
            let hits = find_unredacted(
                "player at 10.42.7.9:11000 mac de:ad:be:ef:00:01 node deadbeef0001 \
                 also de-ad-be-ef-00-01",
            );
            hits.len() == 4
        },
        format!("{:?}", find_unredacted("10.42.7.9 de:ad:be:ef:00:01 deadbeef0001 de-ad-be-ef-00-01")),
    );
    check(
        "the scanner passes redacted text, timestamps, versions and table rules",
        find_unredacted(
            "2026-09-12T11:19:37.182Z | 192.0.2.11:11430 | 02:00:00:00:00:0b | 02000000000b \
             | 0xFFFF | version 3.20.52 | 0-750 ms | 57 s | |---:|---:|",
        )
        .is_empty(),
        format!(
            "{:?}",
            find_unredacted("2026-09-12T11:19:37.182Z 192.0.2.11:11430 02:00:00:00:00:0b 02000000000b 3.20.52")
        ),
    );
    check(
        "a redacted node description leaks neither address nor id nor name",
        {
            let r = Redactor::new(true);
            let n = parse_config(
                "node de:ad:be:ef:00:01 10.42.7.9\n  service 0x0001 name=\"Stue\" port=11000\n",
            )
            .unwrap();
            let line = describe(&n[0], &r);
            find_unredacted(&line).is_empty()
                && !line.contains("Stue")
                && !line.contains("10.42.7.9")
        },
        describe(
            &parse_config("node de:ad:be:ef:00:01 10.42.7.9\n  service 0x0001 name=\"Stue\"\n")
                .unwrap()[0],
            &Redactor::new(true),
        ),
    );
    check(
        "a redacted config carries no original address, id or name either",
        {
            let r = Redactor::new(true);
            let n = parse_config(
                "node de:ad:be:ef:00:01 10.42.7.9\n  service 0x0001 name=\"Stue\" port=11000\n",
            )
            .unwrap();
            let cfg = emit_config(&n, &r);
            find_unredacted(&cfg).is_empty() && !cfg.contains("Stue")
        },
        emit_config(
            &parse_config("node de:ad:be:ef:00:01 10.42.7.9\n  service 0x0001 name=\"Stue\"\n")
                .unwrap(),
            &Redactor::new(true),
        ),
    );

    // saved-run naming and the report itself
    check(
        "the file stamp is a sortable UTC instant: YYYYMMDDTHHMMSSZ",
        {
            let t = file_stamp();
            t.len() == 16
                && t.ends_with('Z')
                && t.as_bytes()[8] == b'T'
                && t.chars().filter(|c| c.is_ascii_digit()).count() == 14
        },
        file_stamp(),
    );
    {
        let shared = Redactor::new(true);
        let node = parse_config(
            "node de:ad:be:ef:00:01 10.42.7.9\n  service 0x0001 name=\"Stue\" port=11000\n",
        )
        .unwrap();
        let per: Vec<(String, Vec<(usize, u128)>)> =
            vec![(describe(&node[0], &shared), vec![(1, 40), (2, 700), (3, 120)])];
        let text = report_markdown(&Measurement {
            rounds: 3,
            complete: 3,
            seen_max: 1,
            expect: 1,
            schedule: &[0.0, 1.0],
            timeout: Duration::from_secs(12),
            query_kind: MSG_QUERY_BROADCAST,
            listen_port: LSDP_PORT,
            dests: &["192.0.2.255".to_string()],
            rows: &[(1, 1, 40, 40, 1), (2, 1, 700, 700, 1), (3, 1, 120, 120, 1)],
            firsts: &[40, 120, 700],
            alls: &[40, 120, 700],
            per_node: &per,
            red: &shared,
        });
        check(
            "a rendered report names the tool version",
            text.contains(&format!("v{VERSION}")),
            String::new(),
        );
        check(
            "a rendered report carries no address, MAC or node id",
            find_unredacted(&text).is_empty(),
            format!("{:?}", find_unredacted(&text)),
        );
        check(
            "per-player stats are the whole distribution, not just the extremes",
            text.contains("| min | median | p95 | max |")
                && text.contains("| 3/3 | 40 | 120 | 700 | 700 |"),
            text.lines().filter(|l| l.starts_with("| 192.0.2")).collect::<Vec<_>>().join(" / "),
        );
    }

    // interfaces
    match interfaces() {
        Ok(ifs) => {
            check("getifaddrs(3) works", true, String::new());
            for i in &ifs {
                println!(
                    "      interface {} {} mask {} broadcast {}",
                    i.name, i.addr, i.netmask, i.broadcast
                );
            }
            if ifs.is_empty() {
                // Not a fault in the code -- a build container has no broadcast
                // interface and the codec is still correct -- so this warns rather
                // than fails, which lets `selftest` gate a container build.
                println!("warn  no up, broadcast-capable IPv4 interface here;");
                println!("      `serve` would fall back to 255.255.255.255");
            }
        }
        Err(e) => check("getifaddrs(3) works", false, e),
    }

    if fail == 0 {
        println!("\nall checks passed");
    } else {
        println!("\n{fail} check(s) FAILED");
    }
    i32::from(fail > 0)
}

/// A histogram wide enough to show the shape and narrow enough to paste into a
/// document.  The spread is the interesting part of a discovery measurement --
/// the median alone hides the rounds that made the app look broken.
fn histogram(data: &[u128]) -> String {
    if data.is_empty() {
        return String::new();
    }
    let max = *data.iter().max().unwrap();
    let target = (max / 12).max(1);
    let w = [1u128, 2, 5, 10, 20, 25, 50, 100, 200, 250, 500, 1000, 2000, 2500, 5000]
        .into_iter()
        .find(|w| *w >= target)
        .unwrap_or(10_000);
    let n = (max / w) as usize + 1;
    let mut counts = vec![0usize; n];
    for v in data {
        counts[(v / w) as usize] += 1;
    }
    let peak = *counts.iter().max().unwrap_or(&1);
    let mut s = String::new();
    for (i, c) in counts.iter().enumerate() {
        let lo = i as u128 * w;
        let bar = if peak == 0 { 0 } else { (c * 40).div_ceil(peak.max(1)) };
        let _ = writeln!(
            s,
            "  {:>5}-{:<5} ms  {:<40} {}",
            lo,
            lo + w - 1,
            "#".repeat(if *c == 0 { 0 } else { bar.max(1) }),
            c
        );
    }
    s
}

struct Measurement<'a> {
    rounds: usize,
    complete: usize,
    seen_max: usize,
    expect: usize,
    schedule: &'a [f64],
    timeout: Duration,
    query_kind: u8,
    /// The port replies were listened for on.  For an `R` query this is where
    /// the answer comes back, so a run that saw nothing is only interpretable
    /// if the record says which port that was.
    listen_port: u16,
    dests: &'a [String],
    /// round, players seen, first ms, last ms, announce datagrams
    rows: &'a [(usize, usize, u128, u128, usize)],
    firsts: &'a [u128],
    alls: &'a [u128],
    /// player label -> (round, ms) for every sighting, already rendered with the
    /// report's own redactor
    per_node: &'a [(String, Vec<(usize, u128)>)],
    red: &'a Redactor,
}

/// A self-contained, publishable record of one measurement run.  Always
/// redacted, whatever the terminal output was set to -- a file that exists to be
/// shared should not depend on remembering a flag.
fn report_markdown(m: &Measurement) -> String {
    let mut s = String::new();
    let sched: Vec<String> = m.schedule.iter().map(|t| format!("{t}")).collect();
    let _ = writeln!(s, "# LSDP discovery timing\n");
    let _ = writeln!(
        s,
        "How long a BluOS controller would wait to see every player, measured with\n\
         `lsdp-static` v{} `measure` on {}.\n",
        VERSION,
        now_stamp()
    );
    let _ = writeln!(
        s,
        "Addresses, node ids and player names are replaced with documentation\n\
         placeholders (RFC 5737 for addresses, a locally administered pool for node\n\
         ids), using the same scheme as `bluos-probe.py`. Placeholders are stable\n\
         within this run, so the same player is the same name in every line.\n"
    );

    let _ = writeln!(s, "## Run\n");
    let _ = writeln!(s, "| setting | value |");
    let _ = writeln!(s, "|---|---|");
    let _ = writeln!(s, "| tool | `lsdp-static` v{VERSION} |");
    let _ = writeln!(s, "| rounds | {} |", m.rounds);
    let _ = writeln!(
        s,
        "| query | `{}` for class 0xFFFF |",
        if m.query_kind == MSG_QUERY_UNICAST { 'R' } else { 'Q' }
    );
    let _ = writeln!(s, "| query sent at | {} s |", sched.join(", "));
    let _ = writeln!(s, "| listen timeout | {:.0} s |", m.timeout.as_secs_f64());
    let _ = writeln!(
        s,
        "| replies listened for on | UDP {}{} |",
        m.listen_port,
        if m.query_kind == MSG_QUERY_UNICAST {
            " -- an `R` answer is unicast back to this port"
        } else {
            " -- a `Q` answer is broadcast to it"
        }
    );
    let _ = writeln!(
        s,
        "| round ends early at | {} |",
        if m.expect > 0 { format!("{} players", m.expect) } else { "never".into() }
    );
    let _ = writeln!(s, "| sent to | {} |", m.dests.join(", "));
    let _ = writeln!(s, "| complete rounds | {}/{} |", m.complete, m.rounds);
    let _ = writeln!(s, "| most players seen in one round | {} |\n", m.seen_max);

    let _ = writeln!(s, "## Rounds\n");
    let _ = writeln!(s, "| round | players | first (ms) | all (ms) | announce datagrams |");
    let _ = writeln!(s, "|---:|---:|---:|---:|---:|");
    for (i, players, first, last, dg) in m.rows {
        let _ = writeln!(s, "| {i} | {players} | {first} | {last} | {dg} |");
    }
    s.push('\n');

    if !m.alls.is_empty() {
        let _ = writeln!(s, "## Spread\n");
        let _ = writeln!(s, "| | min | median | p95 | max |");
        let _ = writeln!(s, "|---|---:|---:|---:|---:|");
        let _ = writeln!(
            s,
            "| first player (ms) | {} | {} | {} | {} |",
            m.firsts[0],
            pct(m.firsts, 0.5),
            pct(m.firsts, 0.95),
            m.firsts[m.firsts.len() - 1]
        );
        let _ = writeln!(
            s,
            "| all players (ms) | {} | {} | {} | {} |\n",
            m.alls[0],
            pct(m.alls, 0.5),
            pct(m.alls, 0.95),
            m.alls[m.alls.len() - 1]
        );
        let _ = writeln!(s, "Time until every expected player had answered:\n");
        let _ = writeln!(s, "```\n{}```\n", histogram(m.alls));
        let _ = writeln!(s, "Time until the first player answered:\n");
        let _ = writeln!(s, "```\n{}```\n", histogram(m.firsts));
    }

    if !m.per_node.is_empty() {
        // The summary above only ever shows the fastest and the slowest player of
        // each round. One player answering consistently late is invisible there.
        let _ = writeln!(s, "## Per player\n");
        let _ = writeln!(s, "| player | rounds seen | min | median | p95 | max |");
        let _ = writeln!(s, "|---|---:|---:|---:|---:|---:|");
        for (k, times) in m.per_node {
            let v = sorted_times(times);
            let _ = writeln!(
                s,
                "| {} | {}/{} | {} | {} | {} | {} |",
                k,
                v.len(),
                m.rounds,
                v[0],
                pct(&v, 0.5),
                pct(&v, 0.95),
                v[v.len() - 1]
            );
        }
        let _ = writeln!(
            s,
            "\nAll times in milliseconds. Every individual sighting is in\n\
             `observations.csv` next to this file, and every round in `rounds.csv`,\n\
             so none of this has to be taken on trust or recomputed by hand.\n"
        );
    }

    let _ = writeln!(s, "## Reading these numbers\n");
    let _ = writeln!(
        s,
        "From `bluos-http-api.md` section 12.1, for context rather than as a\n\
         conclusion:\n\n\
         - a player delays its answer to a query by a **random 0-750 ms**, so a\n  \
           spread up to about 750 ms is the protocol working as specified, not\n  \
           the network struggling;\n\
         - controllers send the query **seven times**, at t = 0, 1, 2, 3, 5, 7\n  \
           and 10 s, because UDP is lossy -- a first-answer time above one\n  \
           second means a query or an answer was lost, not that a player was\n  \
           slow;\n\
         - a player also announces unprompted every **57 s +/- 6 s**, which is\n  \
           the fallback when every query in a burst is lost.\n"
    );

    let (ips, nodes, names) = m.red.counts();
    let _ = writeln!(s, "## Redaction\n");
    let _ = writeln!(
        s,
        "{ips} address(es), {nodes} node id(s) and {names} player name(s) were replaced.\n\
         Originals appear nowhere in this file; `lsdp-static measure --key` writes the\n\
         mapping to a separate file, which is not for sharing."
    );
    s
}

/// Write one run as a self-contained, publishable directory, named from the
/// clock the way bluos-probe.py names its bundles -- the caller supplies a
/// folder and nothing else.  The redaction key goes *next to* the directory,
/// not inside it, so the directory can be published whole.
fn write_run(
    outroot: &str,
    m: &Measurement,
    red: &Redactor,
) -> Result<(), String> {
    let root = std::path::Path::new(outroot);
    std::fs::create_dir_all(root).map_err(|e| format!("{outroot}: {e}"))?;

    // Two runs started inside one second get -2, -3 ... and the key file carries
    // the same discriminator, or the second run would overwrite the first's key
    // and leave a published directory nobody can map back.
    let mut tag = file_stamp();
    let mut dir = root.join(format!("lsdp-measure-{tag}"));
    let mut n = 1;
    while dir.exists() {
        n += 1;
        tag = format!("{}-{n}", file_stamp());
        dir = root.join(format!("lsdp-measure-{tag}"));
    }
    std::fs::create_dir(&dir).map_err(|e| format!("{}: {e}", dir.display()))?;

    let mut rounds_csv = String::from("round,players_seen,complete,first_ms,last_ms,announce_datagrams\n");
    for (i, players, first, last, dg) in m.rows {
        let complete = if m.expect == 0 || *players >= m.expect { "yes" } else { "no" };
        let _ = writeln!(rounds_csv, "{i},{players},{complete},{first},{last},{dg}");
    }

    let mut obs_csv = String::from("round,player,ms\n");
    let mut obs: Vec<(usize, &str, u128)> = Vec::new();
    for (label, times) in m.per_node {
        for (round, ms) in times {
            obs.push((*round, label.as_str(), *ms));
        }
    }
    obs.sort();
    for (round, label, ms) in obs {
        // labels carry no commas, but quote anyway: a player name reaches this
        // file when the run was not redacted
        let _ = writeln!(obs_csv, "{round},\"{}\",{ms}", label.replace('"', "''"));
    }

    let files: [(&str, String); 3] = [
        ("REPORT.md", report_markdown(m)),
        ("rounds.csv", rounds_csv),
        ("observations.csv", obs_csv),
    ];
    let mut leaks: Vec<String> = Vec::new();
    for (name, text) in &files {
        let path = dir.join(name);
        std::fs::write(&path, text).map_err(|e| format!("{}: {e}", path.display()))?;
        for l in find_unredacted(text) {
            leaks.push(format!("{name}: {l}"));
        }
    }

    println!("\nwrote {}/", dir.display());
    for (name, text) in &files {
        println!("  {:<18} {:>7} bytes", name, text.len());
    }
    if !leaks.is_empty() {
        for l in &leaks {
            println!("  !! possible leak: {l}");
        }
        return Err(format!(
            "{} possible leak(s) -- do not publish this directory until they are explained",
            leaks.len()
        ));
    }
    println!("  checked: no address, MAC or node id left in any of them");

    // Outside the directory, like the probe's DO-NOT-SHARE-key-<stamp>.json, and
    // covered by the repository's .gitignore.
    let keypath = root.join(format!("DO-NOT-SHARE-key-{tag}.txt"));
    std::fs::write(&keypath, red.key_file()).map_err(|e| format!("{}: {e}", keypath.display()))?;
    println!("wrote {} -- DO NOT SHARE: it maps the placeholders back", keypath.display());
    Ok(())
}

// ---------------------------------------------------------------------------
// command line
// ---------------------------------------------------------------------------

const USAGE: &str = r#"lsdp-static vVERSION -- static LSDP responder for BluOS discovery (UDP 11430)

USAGE
  lsdp-static serve    [--config FILE] [--player SPEC].. [options]
  lsdp-static discover [options]            one real discovery round -> a config file
  lsdp-static measure  [options]            time discovery repeatedly, report spread
  lsdp-static sniff    [options]            watch and decode traffic, answering nothing
  lsdp-static selftest                      check the codec against captured packets
  lsdp-static version                       print the version

COMMON
  --port N             UDP port (default 11430)
  --iface NAME         only use this interface; repeatable (default: all up,
                       broadcast-capable, non-loopback interfaces)
  --to ADDR            send to this address instead of the interfaces' broadcast
                       addresses; repeatable, overrides --iface.  Any address:
                       a broadcast address, or a single host for a unicast
                       query.  (`--broadcast` is the old name, still accepted)
  --no-reuseport       do not set SO_REUSEPORT (it is what allows a second
                       listener, e.g. a capture, on the same port)
  -v, --verbose        more detail

SERVE
  --config FILE        player list; see players.conf.example
  --player SPEC        a player without a config file, repeatable:
                         --player 192.168.10.10
                         --player 192.168.10.10,id=00:00:5e:00:53:03,name=Kitchen,port=11000
  --delay-ms N|LO-HI   wait this long before answering (default 0: answer
                       immediately, which is the whole point of serving).
                       A range is drawn per query and per node, so
                       `--delay-ms 0-750` deliberately imitates a real player
                       -- only for reproducing their behaviour to document it,
                       never for normal use
  --repeat N           datagrams per answer (default 3) -- UDP is lossy
  --spacing-ms N       gap between those datagrams (default 40)
  --interval N         unsolicited announce every N s +/- 6 (default 57, 0 = off)
  --no-startup-burst   skip the seven announces sent at startup
  --reply-scope S      `all` (default) broadcasts answers to every interface,
                       `arrival` only to the subnet the query came from
  --unicast-echo       also unicast the answer straight back to the querier,
                       on top of the broadcast the protocol asks for
  --min-gap-ms N       ignore repeat queries for the same node within N ms
                       (default 250; a broadcast relay duplicates queries)
  --quiet              log queries only, not every datagram sent
  --dry-run            print what would be announced, then exit

SNIFF
  --for N              stop after N seconds (default: until interrupted)

  Prints every LSDP datagram with a timestamp and the gap since the previous
  one.  Run it on the players' segment, press the controller's player-list
  button, and compare when the answers actually arrived against when the screen
  filled: whatever is left over is the client's own delay, not the network's.
  The source address also says which interface a phone really asked from.

DISCOVER / MEASURE
  --timeout N          seconds to listen per round (default 12)
  --rounds N           measure: how many rounds (default 20)
  --gap N              measure: seconds between rounds (default 2)
  --expect N           stop a round early once N distinct players have answered
  --schedule LIST      query send times in seconds (default 0,1,2,3,5,7,10 --
                       what the shipping controllers do; try `0` against a
                       static responder)
  --all-classes        keep non-player classes too (default: player classes only)
  --redact             replace addresses, node ids and player names in the
                       output with documentation placeholders, the same scheme
                       bluos-probe.py uses
  --out DIR            measure: save the run under DIR, in a directory named
                       from the clock -- lsdp-measure-<stamp>/ holding REPORT.md,
                       rounds.csv and observations.csv.  Always redacted, and
                       checked afterwards for anything that still looks like an
                       address or a MAC.  The key that maps the placeholders back
                       is written next to that directory as
                       DO-NOT-SHARE-key-<stamp>.txt
  --query Q|R          Q (default) asks for a broadcast answer, R for a unicast
                       one back to this socket.  R plus --to <host> is the
                       cross-subnet probe: no broadcast involved at all.
                       Note that a Q answer is broadcast to --port, so with
                       --query Q a reply cannot be told apart from a player's
                       unsolicited periodic announce arriving in the same
                       window; only R proves the query itself was answered.
  --listen-port N      bind this port instead of --port.  0 picks a free one,
                       which only works with --query R (a broadcast answer goes
                       to 11430 and would never arrive)
"#;

struct Args {
    cmd: String,
    flags: Vec<(String, Option<String>)>,
}

impl Args {
    fn parse() -> Result<Args, String> {
        let mut it = std::env::args().skip(1);
        let cmd = it.next().unwrap_or_else(|| "help".into());
        let takes_value = |f: &str| {
            matches!(
                f,
                "--port" | "--iface" | "--to" | "--broadcast" | "--config" | "--player"
                | "--delay-ms"
                    | "--repeat" | "--spacing-ms" | "--interval" | "--reply-scope" | "--min-gap-ms"
                    | "--timeout" | "--rounds" | "--gap" | "--expect" | "--schedule"
                    | "--query" | "--listen-port" | "--out" | "--for"
            )
        };
        let mut flags = Vec::new();
        while let Some(a) = it.next() {
            if !a.starts_with('-') {
                return Err(format!("unexpected argument {a:?}"));
            }
            let (name, inline) = match a.split_once('=') {
                Some((n, v)) => (n.to_string(), Some(v.to_string())),
                None => (a.clone(), None),
            };
            if takes_value(&name) {
                let v = match inline {
                    Some(v) => v,
                    None => it.next().ok_or_else(|| format!("{name} needs a value"))?,
                };
                flags.push((name, Some(v)));
            } else {
                flags.push((name, inline));
            }
        }
        Ok(Args { cmd, flags })
    }

    fn has(&self, name: &str) -> bool {
        self.flags.iter().any(|(f, _)| f == name)
    }
    fn all(&self, name: &str) -> Vec<String> {
        self.flags
            .iter()
            .filter(|(f, _)| f == name)
            .filter_map(|(_, v)| v.clone())
            .collect()
    }
    fn get(&self, name: &str) -> Option<String> {
        self.all(name).pop()
    }
    fn num<T: std::str::FromStr>(&self, name: &str, default: T) -> Result<T, String> {
        match self.get(name) {
            None => Ok(default),
            Some(v) => v.parse().map_err(|_| format!("{name}: bad value {v:?}")),
        }
    }
    fn check_known(&self) -> Result<(), String> {
        let known = [
            "--port", "--iface", "--to", "--broadcast", "--no-reuseport", "-v", "--verbose",
            "--config",
            "--player", "--delay-ms", "--repeat", "--spacing-ms", "--interval",
            "--no-startup-burst", "--reply-scope", "--unicast-echo", "--min-gap-ms", "--quiet",
            "--dry-run", "--timeout", "--rounds", "--gap", "--expect", "--schedule",
            "--all-classes", "--query", "--listen-port", "--redact", "--out", "--for",
        ];
        for (f, _) in &self.flags {
            if !known.contains(&f.as_str()) {
                return Err(format!("unknown option {f}"));
            }
        }
        Ok(())
    }
}

/// Where queries and announces are sent: --to wins, else the directed broadcast
/// of every selected interface, else the limited broadcast address as a last
/// resort.  --to takes any address, not only a broadcast one: a single host is
/// the whole point of the cross-subnet probe, so the flag is not named for
/// broadcast.  `--broadcast` is kept as an alias for the older name.
fn resolve_dests(args: &Args, ifaces: &[Iface]) -> Result<Vec<Ipv4Addr>, String> {
    let mut explicit = args.all("--to");
    explicit.extend(args.all("--broadcast"));
    if !explicit.is_empty() {
        let mut out = Vec::new();
        for s in explicit {
            out.push(s.parse().map_err(|_| format!("bad --to address {s:?}"))?);
        }
        return Ok(out);
    }
    let mut out: Vec<Ipv4Addr> = ifaces.iter().map(|i| i.broadcast).collect();
    out.sort();
    out.dedup();
    if out.is_empty() {
        out.push(Ipv4Addr::new(255, 255, 255, 255));
    }
    Ok(out)
}

fn select_ifaces(args: &Args) -> Result<Vec<Iface>, String> {
    let all = interfaces()?;
    let want = args.all("--iface");
    if want.is_empty() {
        return Ok(all);
    }
    let mut out = Vec::new();
    for w in &want {
        match all.iter().find(|i| &i.name == w) {
            Some(i) => out.push(i.clone()),
            None => {
                let names: Vec<&str> = all.iter().map(|i| i.name.as_str()).collect();
                return Err(format!(
                    "no up, broadcast-capable IPv4 interface called {w:?} (have: {})",
                    names.join(", ")
                ));
            }
        }
    }
    Ok(out)
}

fn parse_player_spec(spec: &str) -> Result<Node, String> {
    let mut parts = spec.split(',');
    let ip = parts.next().unwrap_or("").trim();
    let addr: Ipv4Addr = ip.parse().map_err(|_| format!("--player {spec:?}: bad IPv4 address"))?;
    let mut id_src = "auto".to_string();
    let mut class = 0x0001u16;
    let mut txt: Vec<(String, String)> = Vec::new();
    for p in parts {
        let (k, v) = p
            .split_once('=')
            .ok_or_else(|| format!("--player {spec:?}: expected key=value, got {p:?}"))?;
        match k.trim() {
            "id" => id_src = v.to_string(),
            "class" => class = parse_class(v)?,
            k => txt.push((k.to_string(), v.to_string())),
        }
    }
    if !txt.iter().any(|(k, _)| k == "port") {
        txt.push(("port".into(), "11000".into()));
    }
    Ok(Node { id: parse_node_id(&id_src, addr)?, addr, records: vec![Record { class, txt }] })
}

fn load_nodes(args: &Args) -> Result<Vec<Node>, String> {
    let mut nodes = Vec::new();
    if let Some(path) = args.get("--config") {
        let text = std::fs::read_to_string(&path).map_err(|e| format!("{path}: {e}"))?;
        nodes.extend(parse_config(&text)?);
    }
    for spec in args.all("--player") {
        nodes.push(parse_player_spec(&spec)?);
    }
    if nodes.is_empty() {
        return Err("nothing to announce: pass --config FILE or --player IP".into());
    }
    for i in 0..nodes.len() {
        for j in 0..i {
            if nodes[i].id == nodes[j].id {
                return Err(format!(
                    "two players share node id {} -- ids are the cache key and must be unique \
                     (set id= explicitly)",
                    hex(&nodes[i].id)
                ));
            }
        }
        encode_announce(&nodes[i])?;
    }
    Ok(nodes)
}

/// `--delay-ms 400` or `--delay-ms 0-750`.
fn parse_delay(spec: Option<&str>) -> Result<(u64, u64), String> {
    let spec = match spec {
        None => return Ok((0, 0)),
        Some(v) => v.trim(),
    };
    let bad = || format!("--delay-ms: expected N or LO-HI, got {spec:?}");
    match spec.split_once('-') {
        Some((lo, hi)) => {
            let lo: u64 = lo.trim().parse().map_err(|_| bad())?;
            let hi: u64 = hi.trim().parse().map_err(|_| bad())?;
            if hi < lo {
                return Err(format!("--delay-ms: {hi} is below {lo}"));
            }
            Ok((lo, hi))
        }
        None => {
            let n: u64 = spec.parse().map_err(|_| bad())?;
            Ok((n, n))
        }
    }
}

fn parse_schedule(args: &Args) -> Result<Vec<f64>, String> {
    let s = args.get("--schedule").unwrap_or_else(|| "0,1,2,3,5,7,10".into());
    let mut out = Vec::new();
    for p in s.split(',').filter(|p| !p.trim().is_empty()) {
        out.push(p.trim().parse::<f64>().map_err(|_| format!("bad --schedule value {p:?}"))?);
    }
    if out.is_empty() {
        out.push(0.0);
    }
    Ok(out)
}

fn main() {
    let code = match run() {
        Ok(()) => 0,
        Err(e) => {
            eprintln!("lsdp-static: {e}");
            1
        }
    };
    std::process::exit(code);
}

fn run() -> Result<(), String> {
    let args = Args::parse()?;
    if matches!(args.cmd.as_str(), "help" | "-h" | "--help") {
        print!("{}", USAGE.replace("vVERSION", &format!("v{VERSION}")));
        return Ok(());
    }
    if matches!(args.cmd.as_str(), "version" | "-V" | "--version") {
        println!("lsdp-static {VERSION}");
        return Ok(());
    }
    args.check_known()?;
    if args.cmd == "selftest" {
        std::process::exit(selftest());
    }

    let port: u16 = args.num("--port", LSDP_PORT)?;
    let verbose = args.has("-v") || args.has("--verbose");
    let ifaces = select_ifaces(&args)?;
    let dests = resolve_dests(&args, &ifaces)?;
    let reuseport = !args.has("--no-reuseport");
    let red = Redactor::new(args.has("--redact"));
    // 'Q' asks responders to answer by broadcast, 'R' by unicast to the querier --
    // the only form that can work from another subnet, sent straight at a host.
    let listen_port: u16 = args.num("--listen-port", port)?;
    let query_kind = match args.get("--query").unwrap_or_else(|| "Q".into()).as_str() {
        "Q" | "q" => MSG_QUERY_BROADCAST,
        "R" | "r" => MSG_QUERY_UNICAST,
        other => return Err(format!("--query must be Q or R, got {other:?}")),
    };
    // display only, so it goes through the redactor like everything else
    let dest_list: Vec<String> = dests.iter().map(|d| red.ip(*d).to_string()).collect();

    match args.cmd.as_str() {
        "serve" => {
            let nodes = load_nodes(&args)?;
            let packets: Vec<Vec<u8>> =
                nodes.iter().map(|n| encode_announce(n).unwrap()).collect();
            if args.has("--dry-run") {
                for (n, p) in nodes.iter().zip(&packets) {
                    println!("{}\n  {} bytes: {}\n", describe(n, &red), p.len(), hex_spaced(p));
                }
                println!("would answer on {}:{}", dest_list.join(", "), port);
                return Ok(());
            }
            let s = Serve {
                nodes,
                packets,
                dests,
                ifaces,
                port,
                arrival_scope: args.get("--reply-scope").as_deref() == Some("arrival"),
                delay_ms: parse_delay(args.get("--delay-ms").as_deref())?,
                repeat: args.num("--repeat", 3u32)?,
                spacing_ms: args.num("--spacing-ms", 40u64)?,
                interval: args.num("--interval", 57u64)?,
                unicast_echo: args.has("--unicast-echo"),
                min_gap: Duration::from_millis(args.num("--min-gap-ms", 250u64)?),
                startup: !args.has("--no-startup-burst"),
                verbose: !args.has("--quiet"),
                red,
            };
            let sock = bind_socket(port, reuseport)?;
            s.log(&format!(
                "lsdp-static v{VERSION} serving {} node(s) on UDP {} -> broadcast {}",
                s.nodes.len(),
                port,
                dest_list.join(", ")
            ));
            for n in &s.nodes {
                s.log(&format!("  announcing {}", describe(n, &s.red)));
            }
            s.log(&format!(
                "answering after {}, {}x every {} ms; unsolicited announce {}",
                if s.delay_ms.0 == s.delay_ms.1 {
                    format!("{} ms", s.delay_ms.0)
                } else {
                    format!("a random {}-{} ms", s.delay_ms.0, s.delay_ms.1)
                },
                s.repeat,
                s.spacing_ms,
                if s.interval > 0 {
                    format!("every {} s +/- {}", s.interval, (s.interval / 2).min(6))
                } else {
                    "disabled".into()
                }
            ));
            s.run(&sock)
        }
        "sniff" => {
            let sock = bind_socket(listen_port, reuseport)?;
            let run_for = match args.get("--for") {
                Some(v) => Some(Duration::from_secs_f64(
                    v.parse::<f64>().map_err(|_| format!("--for: bad value {v:?}"))?,
                )),
                None => None,
            };
            println!(
                "lsdp-static v{VERSION} watching UDP {} -- answering nothing{}",
                port,
                match run_for {
                    Some(d) => format!(", for {:.0} s", d.as_secs_f64()),
                    None => String::new(),
                }
            );
            println!("{:<12}  {:>7}  {:<22} message", "time (UTC)", "gap s", "from");
            sniff(&sock, &red, run_for)
        }
        "discover" => {
            let sock = bind_socket(listen_port, reuseport)?;
            let timeout = Duration::from_secs_f64(args.num("--timeout", 12.0f64)?);
            eprintln!(
                "querying {} for {:.0} s ...",
                dest_list.join(", "),
                timeout.as_secs_f64()
            );
            let r = discovery_round(
                &sock,
                &dests,
                port,
                query_kind,
                &parse_schedule(&args)?,
                timeout,
                args.num("--expect", 0usize)?,
                !args.has("--all-classes"),
                true,
                &red,
            )?;
            let mut nodes: Vec<Node> =
                r.order.iter().filter_map(|k| r.first_ms.get(k).map(|(_, n)| n.clone())).collect();
            nodes.sort_by_key(|n| u32::from(n.addr));
            eprintln!("\n{} node(s) in {} ms\n", nodes.len(), r.elapsed_ms);
            if nodes.is_empty() {
                return Err("nothing answered -- wrong subnet, or a firewall is eating UDP 11430".into());
            }
            if red.on {
                eprintln!(
                    "NOTE: --redact replaced the addresses and node ids below with\n\
                     documentation placeholders. This config is for publishing, not\n\
                     for serving -- rerun without --redact to get a usable one.\n"
                );
            }
            print!("{}", emit_config(&nodes, &red));
            Ok(())
        }
        "measure" => {
            let rounds: usize = args.num("--rounds", 20usize)?;
            let timeout = Duration::from_secs_f64(args.num("--timeout", 12.0f64)?);
            let gap = Duration::from_secs_f64(args.num("--gap", 2.0f64)?);
            let expect: usize = args.num("--expect", 0usize)?;
            let schedule = parse_schedule(&args)?;
            let sched: Vec<String> = schedule.iter().map(|t| format!("{t}")).collect();
            println!(
                "{} rounds, '{}' query at t={} s to {}, {:.0} s timeout, expecting {}",
                rounds,
                if query_kind == MSG_QUERY_UNICAST { 'R' } else { 'Q' },
                sched.join("/"),
                dest_list.join(", "),
                timeout.as_secs_f64(),
                if expect > 0 { expect.to_string() } else { "any number of".into() }
            );
            let mut firsts: Vec<u128> = Vec::new();
            let mut alls: Vec<u128> = Vec::new();
            let mut complete = 0usize;
            let mut seen_max = 0usize;
            // keyed by node id, keeping the node itself, so the terminal and the
            // report can each render it through their own redactor, and keeping the
            // round each sighting came from so the raw data can be written out
            let mut per_node: HashMap<Vec<u8>, (Node, Vec<(usize, u128)>)> = HashMap::new();
            let mut rows: Vec<(usize, usize, u128, u128, usize)> = Vec::new();
            for i in 1..=rounds {
                let sock = bind_socket(listen_port, reuseport)?;
                let r = discovery_round(
                    &sock,
                    &dests,
                    port,
                    query_kind,
                    &schedule,
                    timeout,
                    expect,
                    !args.has("--all-classes"),
                    verbose,
                    &red,
                )?;
                drop(sock);
                let mut times: Vec<u128> = r.first_ms.values().map(|(ms, _)| *ms).collect();
                times.sort();
                seen_max = seen_max.max(r.first_ms.len());
                for (_, (ms, n)) in &r.first_ms {
                    per_node
                        .entry(n.id.clone())
                        .or_insert_with(|| (n.clone(), Vec::new()))
                        .1
                        .push((i, *ms));
                }
                let ok = expect == 0 || r.first_ms.len() >= expect;
                if ok && !times.is_empty() {
                    complete += 1;
                    firsts.push(times[0]);
                    alls.push(*times.last().unwrap());
                }
                rows.push((
                    i,
                    r.first_ms.len(),
                    times.first().copied().unwrap_or(0),
                    times.last().copied().unwrap_or(0),
                    r.datagrams,
                ));
                println!(
                    "round {:>3}: {} player(s){}  first {:>6} ms  last {:>6} ms  ({} announce datagrams)",
                    i,
                    r.first_ms.len(),
                    if ok { "  " } else { " !" },
                    times.first().copied().unwrap_or(0),
                    times.last().copied().unwrap_or(0),
                    r.datagrams
                );
                if i < rounds {
                    std::thread::sleep(gap);
                }
            }
            firsts.sort();
            alls.sort();
            println!(
                "\ncomplete rounds: {}/{} (most players seen in one round: {})",
                complete, rounds, seen_max
            );
            if !alls.is_empty() {
                println!("                    min     median      p95       max");
                println!(
                    "first player  {:>8} {:>10} {:>8} {:>9}  ms",
                    firsts[0],
                    pct(&firsts, 0.5),
                    pct(&firsts, 0.95),
                    firsts[firsts.len() - 1]
                );
                println!(
                    "all players   {:>8} {:>10} {:>8} {:>9}  ms",
                    alls[0],
                    pct(&alls, 0.5),
                    pct(&alls, 0.95),
                    alls[alls.len() - 1]
                );
            }
            let mut nodes_seen: Vec<&(Node, Vec<(usize, u128)>)> = per_node.values().collect();
            nodes_seen.sort_by_key(|(n, _)| u32::from(n.addr));
            if !nodes_seen.is_empty() {
                // Per player, not just the fastest and slowest of each round: one
                // player consistently answering late is invisible in the summary
                // above, and is exactly the kind of thing worth spotting.
                println!("\nper player, time to answer:");
                let labels: Vec<String> =
                    nodes_seen.iter().map(|(n, _)| describe(n, &red)).collect();
                let w = labels.iter().map(|l| l.len()).max().unwrap_or(0);
                println!(
                    "  {:<w$} {:>7} {:>8} {:>8} {:>8} {:>8}",
                    "player", "seen", "min", "median", "p95", "max"
                );
                for ((_, times), label) in nodes_seen.iter().zip(&labels) {
                    let v = sorted_times(times);
                    println!(
                        "  {:<w$} {:>3}/{:<3} {:>6} ms {:>6} ms {:>6} ms {:>6} ms",
                        label,
                        v.len(),
                        rounds,
                        v[0],
                        pct(&v, 0.5),
                        pct(&v, 0.95),
                        v[v.len() - 1]
                    );
                }
            }
            if let Some(out) = args.get("--out") {
                // The saved run is always redacted, whatever the terminal was set
                // to: a directory that exists to be published should not depend on
                // a flag having been remembered.
                let shared = Redactor::new(true);
                let per_player: Vec<(String, Vec<(usize, u128)>)> = nodes_seen
                    .iter()
                    .map(|(n, times)| (describe(n, &shared), times.clone()))
                    .collect();
                let dests_red: Vec<String> =
                    dests.iter().map(|d| shared.ip(*d).to_string()).collect();
                write_run(
                    &out,
                    &Measurement {
                        rounds,
                        complete,
                        seen_max,
                        expect,
                        schedule: &schedule,
                        timeout,
                        query_kind,
                        listen_port,
                        dests: &dests_red,
                        rows: &rows,
                        firsts: &firsts,
                        alls: &alls,
                        per_node: &per_player,
                        red: &shared,
                    },
                    &shared,
                )?;
            }
            Ok(())
        }
        other => Err(format!("unknown command {other:?} -- try `lsdp-static help`")),
    }
}
