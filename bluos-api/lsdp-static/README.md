# lsdp-static

A static LSDP responder: it answers BluOS discovery queries on UDP 11430 from a
list of players in a config file, the way an avahi static service file answers
mDNS. No BluOS hardware is involved — it speaks for players that are named, not
found.

It exists to answer one question before any more work goes into Musica:

> **If discovery answers instantly and consistently, is discovery still a
> problem worth building around?**

So the tool also measures. `measure` runs discovery over and over and reports
the spread, which is the number that actually decides this — "two to three
seconds, consistently" is a different product from "usually fast, sometimes
never".

Written against `../bluos-http-api.md` §12.1. `selftest` checks the encoder
against the real Bluesound Node N130 announce captured in that section, byte for
byte, so what goes on the wire is what a real player puts there.

## Build

Two ways to the same program. Linux only either way — it uses `SO_REUSEPORT` and
`getifaddrs(3)` directly.

### Without a Rust toolchain, using podman

```sh
./build-with-podman.sh
sudo install -m755 ./lsdp-static /usr/local/sbin/
```

Compiles inside a throwaway `rust:1-alpine` container and copies one binary out.
Rootless podman is fine: nothing here needs root, and the binary lands owned by
you. `ENGINE=docker ./build-with-podman.sh` if that is what is installed.

That image targets musl, so the result is **statically linked** — no runtime
dependencies and nothing that has to stay in step with the host's glibc. The
image is multi-arch, so an arm64 host builds an arm64 binary with no
cross-compilation setup. The build runs `selftest` and fails if the wire codec
is wrong, so a green build means the announce bytes are right on that machine.

Without the script, it is one command:

```sh
podman run --rm -v "$PWD:/src:Z" -w /src docker.io/library/rust:1-alpine \
    sh -c 'apk add --no-cache musl-dev && cargo build --release --locked'
# -> ./target/release/lsdp-static, static, owned by you
```

`:Z` relabels the mount for SELinux and does nothing where SELinux is not in use.

The plainest version works too, and is worth knowing because nothing about it is
specific to this project:

```sh
podman run --rm -v "$PWD:/project" -w /project docker.io/library/rust:latest cargo build
```

That gives a debug build linked against the image's glibc, so keep it for a quick
check and use one of the above when the binary has to run outside a container:
`--release` for a build worth measuring with, and the alpine image when you would
rather not care whether the host's glibc matches.

### Or run it as a container and install nothing

`build-with-podman.sh` leaves an image behind whose entrypoint is the binary.
LSDP is broadcast on real interfaces, so it needs the host's network namespace:

```sh
podman run -d --name lsdp-static --network=host \
    -v /etc/lsdp-static/players.conf:/players.conf:ro,Z \
    localhost/lsdp-static:built \
    serve --config /players.conf --iface lan --iface iot --iface guest
podman logs -f lsdp-static
```

Port 11430 is unprivileged, so this works rootless too.

### With cargo, if you have it

```sh
cargo build --release          # no dependencies: a single compile
./target/release/lsdp-static selftest
sudo install -m755 target/release/lsdp-static /usr/local/sbin/
```

`cargo` from Debian/Ubuntu (`apt install cargo`) is new enough, on arm64 too.

## The experiment, end to end

Run all of this from a host on the **controller's** VLAN, not from `ek-arm`,
unless you are testing the relay box talking to itself.

**1. Baseline — what discovery costs today, with the relay running.**

```sh
lsdp-static measure --rounds 20 --expect 4
```

`--expect 4` is however many players you have; a round stops as soon as it has
that many, so a round that never gets there burns the full `--timeout` and shows
up as an incomplete round. That count — complete rounds out of 20 — is the
headline. The median is the comfortable case; the p95 and the incomplete rounds
are the ones that make an app feel broken.

**2. Capture the players into a config, while they are still findable.**

```sh
lsdp-static discover > players.conf      # progress goes to stderr, config to stdout
```

Or, if discovery is too unreliable to trust for this, ask each player directly —
`/SyncStatus` only needs the address:

```sh
./from-syncstatus.sh 192.168.10.10 192.168.10.11 192.168.10.12 > players.conf
```

Check it over; `players.conf.example` explains every field.

**3. Swap the relay for the static responder on `ek-arm`.**

```sh
sudo systemctl stop udp-broadcast-relay-bluos
sudo lsdp-static serve --config players.conf --iface lan --iface iot --iface guest
```

`lsdp-static.service` is the systemd unit if you want it to survive a reboot.
Leave the relay stopped: if both run, the relay re-broadcasts these answers onto
the other VLANs and you are measuring the two together.

**4. Measure again, from the same place as step 1.**

```sh
lsdp-static measure --rounds 20 --expect 4
lsdp-static measure --rounds 20 --expect 4 --schedule 0   # one query, no retries
```

The second one is the interesting variant. The seven-packet query burst at
t = 0,1,2,3,5,7,10 s exists because UDP is lossy and players take up to 750 ms to
answer; against a responder that answers immediately, a single query should be
enough. If `--schedule 0` is reliably fast, discovery is solved and the retry
schedule is dead weight. If it is not, the loss is on the network, not in the
protocol, and no amount of client-side cleverness fixes it.

Then open the real BluOS app and see whether it finds the players — the measure
numbers are the evidence, the app is the sanity check.

## Reading the output

```
round   7: 3 player(s)    first      2 ms  last     14 ms  (9 announce datagrams)

complete rounds: 20/20 (most players seen in one round: 3)
                    min     median      p95       max
first player         1          2        4         9  ms
all players          6         13       21        34  ms
```

`first player` is how long until the app could show something; `all players` is
when the list stops changing. `announce datagrams` counts every announce heard,
including the deliberate repeats — if that is far below `players × repeats ×
queries`, datagrams are being dropped, and that is worth knowing on its own.

## Keeping the results

A measurement run is evidence about how BluOS players behave, which makes it
worth keeping and worth publishing — and it is full of the addresses, MACs and
room names of the house it was measured in. So `--report` writes the run as a
markdown document with all of that replaced:

```sh
lsdp-static measure --rounds 20 --expect 4 --report ../test-runs/lsdp-timing-2026-09-12.md
```

The redaction is the scheme `bluos-probe.py` uses, so a measurement from here
and a capture from there mean the same thing in the same bundle: addresses
become RFC 5737 documentation addresses starting at `192.0.2.11`, node ids
become `02:00:00:00:xx:yy`, player names become `Room-A`, `Room-B`. Placeholders
are stable within a run, so the same player is the same name in every line, and
the relationships between the numbers survive.

The report is **always** redacted, whether or not `--redact` was given — a file
that exists to be shared should not depend on remembering a flag. After writing
it, the tool scans its own output for anything that still parses as an address,
a MAC or a bare-hex node id, and refuses to finish quietly if it finds one.

Add `--redact` to redact the terminal output as well, which also works for
`serve` (its log) and `discover`. To keep the mapping for yourself:

```sh
lsdp-static measure --rounds 20 --expect 4 \
    --report ../test-runs/lsdp-timing-2026-09-12.md --key ../test-runs/DO-NOT-SHARE-key-2026-09-12.txt
```

`../test-runs/` is where `bluos-probe.py` already puts its bundles, so timing
runs and protocol captures end up side by side.

The key file maps placeholders back to the originals and says so at the top. It
is the one file that must not be published. The `DO-NOT-SHARE-` prefix is the
name the probe uses for the same thing, and the repository's `.gitignore` covers
both that prefix and `*.key`, so neither can be committed by accident.

What the report contains: the run's settings, a per-round table, min/median/p95/max
for both "first player answered" and "all players answered", a histogram of each,
a per-player table, and the protocol's own documented timings so the numbers can
be read against what they should be.

## The node id trap

The node id is the cache key a controller dedupes on, and it is the player's
MAC. If `lsdp-static` announces a player under a different id while the real
player is also announcing, the controller shows that player **twice**.

So: use the real MACs. `discover` and `from-syncstatus.sh` both give you them.
`node auto <ip>` invents a stable id from the address, which is fine for a
throwaway test on a network where the real players are asleep or absent, and
wrong otherwise.

## Cross-subnet, without a relay at all

The protocol has an `R` query (`0x52`): same query, but the responder answers by
**unicast** to whoever asked, instead of broadcasting. No shipping client sends
it, and the spec notes this as the one part of LSDP with obvious unrealised
value.

`lsdp-static serve` answers `R` — including a unicast `R` sent straight at it
from another subnet, where broadcast never arrives:

```sh
# from a host with no route to the players' broadcast domain at all
lsdp-static measure --query R --broadcast <ek-arm-ip> --rounds 10 --expect 4
```

`--broadcast` here is just "where to send the query", and for `R` that is one
ordinary unicast address. Add `--listen-port 0` if something else on the client
already holds 11430; this responder answers to whatever source port asked.

If that works from the guest VLAN, then Musica pointed at one known address gets
the full player list — node id, class and real port — with no relay, no
broadcast, and no configured address list. Worth ten minutes of testing before
concluding that discovery needs infrastructure.

The same command aimed at a **real player** tests something the probe left open.
`bluos-http-api.md` records claim `C-19` — "an LSDP `R` query sent by unicast is
answered" — as INCONCLUSIVE, because the control was silent too:

```sh
lsdp-static measure --query R --broadcast <player-ip> --rounds 5 --timeout 5 -v
```

An answer settles `C-19` as confirmed, and makes the relay redundant for real.
Silence confirms nothing by itself — a player that ignores unicast and a
firewalled port look identical from here.

## Options worth knowing

| Option | Why |
|---|---|
| `--repeat 3 --spacing-ms 40` | three copies of every answer, 40 ms apart. UDP is lossy; this is the cheapest available fix. `--repeat 1` to measure without it. |
| `--delay-ms 0` | the default: answer immediately. A real player waits a random 0–750 ms; `serve` deliberately does not, which is the whole point. `--delay-ms 0-750` makes it imitate one instead, for reproducing that behaviour in order to document it — never for normal use. |
| `--interval 57` | unsolicited announce every 57 s ± 6, the steady-state rate a real player uses. `--interval 0` turns it off, to test query/response alone. |
| `--reply-scope arrival` | answer only on the subnet the query came from, instead of all three. |
| `--unicast-echo` | also unicast each answer straight back to the querier. Off by default because no real player does it — but it is the one thing that would survive a client whose OS drops broadcast (a macOS Local Network permission denial does exactly that, silently). |
| `--min-gap-ms 250` | collapse duplicate queries, which a broadcast relay produces by design. |
| `--dry-run` | print the exact bytes that would be announced, and exit. |
| `--redact` | replace addresses, node ids and player names in the output with documentation placeholders. Works for `serve`, `measure` and `discover`. |
| `--report FILE` | `measure`: write the run as publishable markdown. Always redacted, and checked afterwards. |
| `--key FILE` | `measure`: write the placeholder → original mapping. Do not publish this one. |

## What this does not prove

- It says nothing about whether a player is actually **reachable** at the
  address being announced. Discovery working and control working are two
  different claims; `/SyncStatus` settles the second.
- It answers for players that are listed, not players that are there. A player
  that has changed address, or that is off, is still announced — and a
  controller only finds out when it tries to talk to it. That is exactly what a
  static configuration means, and it is the cost being weighed against the
  saved seconds.
- The measured numbers are this network's. They are not the number a user on
  someone else's network gets, which is the whole reason discovery is
  unreliable in the first place.

## Running next to something else on 11430

`SO_REUSEPORT` is set, so this coexists with another listener on the same port —
a capture, or `measure` on the same host. One caveat: Linux delivers *broadcast*
to every such socket but load-balances *unicast* between them, so if `serve` and
`measure` share a host, unicast `R` answers may land in the wrong process. Test
`R` from a different machine. `--no-reuseport` turns it off.

`udp-broadcast-relay-redux` uses a raw socket and does not bind 11430, so it
will not refuse to start alongside this — which is why the systemd unit declares
`Conflicts=`. They do not fight over the port; they just quietly invalidate each
other's measurements.
