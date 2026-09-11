#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
bluos-probe.py -- systematic, self-redacting probe harness for the BluOS HTTP API.

Read-only by default. State-changing suites exist and are opt-in via
--allow-state; nothing destructive is implemented at all.

Produces a shareable evidence bundle:

    bluos-probe-<timestamp>/
        README.md          what this is, how it was produced
        REPORT.md          human-readable results, one table per suite
        MANIFEST.json      every request/response as structured data
        SHAPES.md          element/attribute inventory harvested from all XML
        REDACTIONS.md      what was redacted, and how (counts only, no originals)
        raw/<id>.<ext>     redacted response bodies
        raw/<id>.head.txt  redacted status line + response headers
    DO-NOT-SHARE-key-<timestamp>.json   placeholder -> original mapping (kept OUTSIDE the bundle)

Everything written inside the bundle is passed through the redactor, and the
bundle is re-scanned afterwards; the run fails loudly if anything that looks
like an address, MAC or secret survives.

Requires only the Python 3.8+ standard library.

    ./bluos-probe.py --discover
    ./bluos-probe.py --player A=192.168.1.10 --player B=192.168.1.11
    ./bluos-probe.py --player A=192.168.1.10 --suite env,transport,longpoll
    ./bluos-probe.py --suite round2 --allow-state   # reversible state changes
    ./bluos-probe.py --verify-harness              # checks this script, not BluOS

Safety classes
    read        certainly no side effects
    probe       believed harmless; unknown endpoint, called with no parameters
    state       reversible state change            -- NOT IN THIS ROUND
    destructive irreversible or config-changing    -- NOT IN THIS ROUND

Only `read` and `probe` are implemented. `--no-probe` drops the second class.
"""

from __future__ import annotations

import argparse
import binascii
import concurrent.futures
import datetime
import hashlib
import http.client
import html
import ipaddress
import json
import os
import re
import socket
import struct
import sys
import threading
import time
import urllib.parse
import zipfile
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Sequence, Tuple

VERSION = "1.6"

# Fixture convention, so this file stays shareable.
#
# Everything identifying in the tests and fixtures below is synthetic:
#   MAC addresses  00:00:5E:00:53:xx   RFC 7042 documentation range
#   IPv4 fixtures  10.255.255.x        valid RFC 1918, but a block nobody runs
#   placeholders   02:00:00:00:xx:xx and 192.0.2.x / 2001:db8::x
# An earlier version embedded a real device MAC lifted from a capture, which
# meant the harness itself could not be shared. If you add a fixture, take the
# values from these ranges.

MAX_BODY_BYTES = 8 * 1024 * 1024
CONTROL_PORT = 11000
SETTINGS_PORT = 11001
WEB_PORT = 80
LSDP_PORT = 11430

SAFETY_READ = "read"
SAFETY_PROBE = "probe"
SAFETY_STATE = "state"
SAFETY_DESTRUCTIVE = "destructive"

# The zone declared to the device in X-Sovi-Tz.
#
# Fixed rather than derived. The device uses it for time-dependent answers --
# alarm times above all -- so it has to be a known, recorded constant, not
# whatever the machine running the harness happens to be set to. It is written
# into MANIFEST.json, REPORT.md and README.md of every bundle, so a capture can
# always be read against the zone it was requested in. --timezone overrides it.
PROBE_TZ = "Europe/Copenhagen"


def _offset_for_zone(zone: str) -> str:
    """Current UTC offset for a named zone, or "" if it cannot be resolved."""
    try:
        from zoneinfo import ZoneInfo
        return datetime.datetime.now(ZoneInfo(zone)).strftime("%z")
    except Exception:
        return ""


def tz_context() -> Dict[str, str]:
    """What was declared, and what the harness host's clock actually was.

    Recorded together because they can disagree: if the machine running this is
    on UTC while the device is told Europe/Copenhagen, an alarm at 07:00 local
    is not 07:00 by the harness's own clock, and a reader needs to see both to
    interpret the capture.
    """
    now = datetime.datetime.now().astimezone()
    return {
        "declared_to_device": SOVI_HEADERS.get("X-Sovi-Tz", PROBE_TZ),
        "harness_host_offset": now.strftime("%z") or "+0000",
        "harness_host_tzname": now.tzname() or "unknown",
        "harness_local_time": now.replace(microsecond=0).isoformat(),
    }


# Headers the official Android controller sends on every request (spec 1.4).
SOVI_HEADERS = {
    "X-Sovi-Schema-Version": "35",
    "X-Sovi-Ui-Schema-Version": "7",
    "X-Sovi-Ui-Autofill": "0",
    "X-Sovi-Tz": PROBE_TZ,
    "Accept-Language": "en-GB",
    "User-Agent": "bluos-probe/%s (protocol research harness)" % VERSION,
}


# --------------------------------------------------------------------------
# Redaction
# --------------------------------------------------------------------------

# RFC 5737 TEST-NET-1 / RFC 3849 documentation prefixes. Structure-preserving,
# so redacted captures remain valid, parseable fixtures, while being obviously
# non-routable documentation addresses.
IPV4_POOL_BASE = "192.0.2."
IPV6_POOL_BASE = "2001:db8::"
MAC_POOL_PREFIX = "02:00:00:00:"

# Addresses that are protocol constants, not anybody's network.
IPV4_DOC_PREFIXES = ("192.0.2.", "198.51.100.", "203.0.113.")
IPV4_KEEP = {
    "0.0.0.0",
    "127.0.0.1",
    "255.255.255.255",
    "224.0.0.251",  # mDNS
    "239.255.255.250",  # SSDP
    "1.1.1.1",
    "8.8.8.8",
    "8.8.4.4",
}

MAC_RE = re.compile(
    r"\b[0-9A-Fa-f]{2}(?P<sep>[:-])(?:[0-9A-Fa-f]{2}(?P=sep)){4}[0-9A-Fa-f]{2}\b"
)
MAC_PCT_RE = re.compile(r"(?i)\b[0-9A-F]{2}(?:%3A[0-9A-F]{2}){5}\b")
# An LSDP Announce carries node_id as twelve bare hex digits -- 00005e005301 --
# which is a MAC with the separators removed. MAC_RE cannot see it, so every
# shared discovery capture contained real device MACs.
MAC_HEX_RE = re.compile(r"(?i)(?<![0-9a-f])(?:[0-9a-f]{2}){6}(?![0-9a-f])")
# Do not use \b here.  Browse keys percent-encode path separators, so an IP can
# immediately follow the ``F`` in ``%2F`` (for example
# ``%2Fvar%2Fmnt%2F192.168.1.5-music``).  ``F`` and the leading digit are both
# regex "word" characters, therefore \b fails at exactly the place local-library
# browse keys put NAS addresses.  Numeric/dot lookarounds prevent partial dotted-
# quad matches without treating surrounding URL-encoding hex digits as part of
# the address.
IPV4_RE = re.compile(r"(?<![0-9.])(?:\d{1,3}\.){3}\d{1,3}(?![0-9.])")
IPV6_CAND_RE = re.compile(r"(?<![0-9A-Fa-f:.])(?:[0-9A-Fa-f]{0,4}:){2,7}[0-9A-Fa-f]{0,4}(?![0-9A-Fa-f:])")
EMAIL_RE = re.compile(r"\b[\w.+-]+@[\w-]+\.[\w.-]{2,}\b")
# Host component of a UNC or SMB/CIFS-style share path:
# \\HOST\share, //HOST/share, smb://HOST/share, cifs://HOST/share.
UNC_HOST_RE = re.compile(
    r"(?P<lead>(?i:smb://|cifs://)|\\\\|(?<![:\w])//)(?P<host>[A-Za-z0-9._-]{2,63})(?=[\\/])"
)

# Query-string / attribute style key=value where the key names a secret.
SENSITIVE_KEYS = (
    "password", "passwd", "pwd", "pass",
    "token", "access_token", "refresh_token", "id_token", "authtoken",
    "secret", "client_secret", "apikey", "api_key",
    "signature", "sig", "hmac",
    "session", "sessionid", "sessionkey",
    "ssid", "psk", "wpa", "passphrase",
    "email", "mail",
    "userid", "user_id", "username", "user", "account", "login",
    "serial", "serialno", "serialnumber",
    "latitude", "longitude", "postcode",
)
_SENSITIVE_ALT = "|".join(sorted(SENSITIVE_KEYS, key=len, reverse=True))

# A key may carry a prefix, because BluOS uses camelCase throughout:
# wifiPassword, accessToken, authToken, deviceSerial all end in a listed word.
# Over-redaction is the acceptable direction of error here.
_KEY = r"[A-Za-z0-9_.-]{0,24}?(?:%s)" % _SENSITIVE_ALT

# key="value" / key='value' / key=value(&|space|end)
KV_RE = re.compile(
    r"(?i)\b(?P<key>%s)(?P<eq>\s*=\s*)(?P<val>\"[^\"]*\"|'[^']*'|[^&\s<>\"'\\]*)" % _KEY
)
# JSON: "key": "value" and "key": 1234
JSON_KV_RE = re.compile(
    r'(?i)"(?P<key>%s)"(?P<sep>\s*:\s*)(?P<val>"(?:[^"\\]|\\.)*"|-?\d+(?:\.\d+)?|true|false)' % _KEY
)
# HTML form fields: <input name="password" value="...">
FORM_RE = re.compile(
    r'(?i)(?P<lead>name\s*=\s*"%s"[^>]*?\bvalue\s*=\s*")(?P<val>[^"]*)(?P<tail>")' % _KEY
)
# <username>value</username>, including <wifiPassword>...</wifiPassword>
ELEM_RE = re.compile(
    r"(?i)(?P<open><(?P<tag>%s)(?:\s[^>]*)?>)(?P<val>[^<]*)(?P<close></(?P=tag)>)" % _KEY
)
# Headers whose whole value is credential material. Redacted BY NAME where
# headers are captured -- never by pattern-matching the body, because a pattern
# for "nonce|response" has no word boundary and rewrote any prose containing
# the word "response", including this harness's own analysis notes.
SENSITIVE_HEADERS = frozenset({
    "authorization", "proxy-authorization", "www-authenticate",
    "proxy-authenticate", "cookie", "set-cookie", "x-api-key", "x-auth-token",
})

# Bluetooth device names commonly carry a person's name.
BT_NAME_RE = re.compile(
    r"(?i)(<(?:device|btdevice|bluetoothOutput|bluetoothInput|pairWithSub)\b[^>]*?\bname\s*=\s*)\"([^\"]*)\"")


class Redactor:
    """Deterministic, structure-preserving redaction with a reversible key.

    Placeholders are stable within a run, so `192.0.2.11` always means the same
    original host everywhere in the bundle and relationships between captures
    survive.
    """

    def __init__(self, redact_names: bool = False, redact_bt_names: bool = True):
        self.redact_names = redact_names
        self.redact_bt_names = redact_bt_names
        self._lock = threading.Lock()
        self.map: Dict[str, Dict[str, str]] = {
            "ipv4": {}, "ipv6": {}, "mac": {}, "host": {}, "email": {},
            "literal": {}, "name": {}, "value": {},
        }
        self._counters: Dict[str, int] = dict.fromkeys(self.map, 0)
        self.hits: Dict[str, int] = dict.fromkeys(self.map, 0)
        self._literals: List[Tuple[str, str]] = []  # (original, placeholder), longest first
        self._reserved_ipv4: set = set()

    # -- registration -----------------------------------------------------

    def register_ipv4(self, original: str) -> str:
        """Map an address seen in a response, without caring what it becomes."""
        return self._alloc("ipv4", original)

    def reserve_ipv4(self, original: str, placeholder: str) -> None:
        with self._lock:
            self.map["ipv4"][original] = placeholder
            self._reserved_ipv4.add(placeholder)

    def reserve_mac(self, original: str, placeholder: str) -> None:
        with self._lock:
            self.map["mac"][original.lower()] = placeholder

    def add_literal(self, original: str, placeholder: str) -> None:
        """Scrub an exact string everywhere (share host, SSID, real name...).

        Also registers the encoded forms. Browse keys, image URLs and playURLs
        are percent-encoded and XML attributes may be entity-encoded, so a room
        name such as "Stue+Kokken" travels as "Stue%2BKokken" and a name with a
        non-ASCII character travels as "K%C3%B8kken" or "K&#248;kken". Exact
        string replacement alone missed all of those.
        """
        if not original or len(original) < 3:
            return
        variants = {original}
        try:
            variants.add(urllib.parse.quote(original, safe=""))
            variants.add(urllib.parse.quote_plus(original))
            variants.add(urllib.parse.quote(original))
        except Exception:
            pass
        variants.add(html.escape(original, quote=True))
        variants.add("".join(("&#%d;" % ord(c)) if ord(c) > 127 else c for c in original))
        with self._lock:
            for v in variants:
                if len(v) < 3 or v in self.map["literal"]:
                    continue
                self.map["literal"][v] = placeholder
                self._literals.append((v, placeholder))
            self._literals.sort(key=lambda t: len(t[0]), reverse=True)

    def add_player_name(self, original: str, placeholder: str) -> None:
        if not self.redact_names or not original:
            return
        with self._lock:
            self.map["name"][original] = placeholder
        self.add_literal(original, placeholder)

    # -- allocation -------------------------------------------------------

    def _alloc(self, kind: str, original: str) -> str:
        with self._lock:
            existing = self.map[kind].get(original)
            if existing:
                return existing
            self._counters[kind] += 1
            n = self._counters[kind]
            if kind == "ipv4":
                # skip any slot already reserved for a named player
                while True:
                    ph = "%s%d" % (IPV4_POOL_BASE, 100 + n)
                    if ph not in self._reserved_ipv4:
                        break
                    self._counters[kind] += 1
                    n = self._counters[kind]
            elif kind == "ipv6":
                ph = "%s%x" % (IPV6_POOL_BASE, n)
            elif kind == "mac":
                # Two octets: a Wi-Fi scan in a block of flats can list far more
                # than 127 BSSIDs, and one octet produced "…:00:102", which is
                # not a MAC and which MAC_RE would not even match.
                ph = MAC_POOL_PREFIX + "%02x:%02x" % divmod(n, 256)
            elif kind == "host":
                ph = "host-%d.invalid" % n
            elif kind == "email":
                ph = "user%d@example.invalid" % n
            elif kind == "name":
                ph = "Room-%d" % n
            else:
                ph = "[REDACTED-%s-%d]" % (kind, n)
            self.map[kind][original] = ph
            return ph

    def _count(self, kind: str) -> None:
        with self._lock:
            self.hits[kind] += 1

    # -- the pass ---------------------------------------------------------

    def scrub_counted(self, text: Optional[str]) -> Tuple[str, int]:
        """scrub(), plus how many substitutions it made. A count of zero means
        the capture is byte-for-byte what the device sent."""
        with self._lock:
            before = sum(self.hits.values())
        out = self.scrub(text)
        with self._lock:
            after = sum(self.hits.values())
        return out, after - before

    def scrub(self, text: Optional[str]) -> str:
        if not text:
            return text or ""

        # 1. user-supplied and harvested literals first (longest match wins)
        for original, placeholder in list(self._literals):
            if original in text:
                text = text.replace(original, placeholder)
                self._count("literal")

        # 2. MACs before IPv6, so 00:00:5e:00:53:02 is never read as an address
        def _mac(m: re.Match) -> str:
            orig = m.group(0)
            # Already a placeholder. Without this, re-scrubbing an already
            # redacted note allocated a NEW placeholder and recorded the old one
            # as an original -- after which verify_bundle found it in the raw
            # bodies and refused to build the zip.
            if orig.lower().replace("-", ":").startswith(MAC_POOL_PREFIX):
                return orig
            sep = m.group("sep")
            ph = self._alloc("mac", orig.lower())
            self._count("mac")
            if sep == "-":
                ph = ph.replace(":", "-")
            if orig.isupper() or orig == orig.upper():
                ph = ph.upper()
            return ph

        text = MAC_RE.sub(_mac, text)

        # 2b. percent-encoded MACs, which appear inside Capture/bluez URLs
        def _mac_pct(m: re.Match) -> str:
            plain = m.group(0).replace("%3A", ":").replace("%3a", ":")
            if plain.lower().startswith(MAC_POOL_PREFIX):
                return m.group(0)
            self._count("mac")
            return self._alloc("mac", plain.lower()).replace(":", "%3A")

        text = MAC_PCT_RE.sub(_mac_pct, text)

        # 2c. bare-hex MACs (LSDP node_id)
        def _mac_hex(m: re.Match) -> str:
            raw = m.group(0)
            plain = ":".join(raw[i:i + 2] for i in range(0, 12, 2)).lower()
            if plain.startswith(MAC_POOL_PREFIX):
                return raw
            ph = self._alloc("mac", plain)
            self._count("mac")
            out = ph.replace(":", "")
            return out.upper() if raw.isupper() else out

        text = MAC_HEX_RE.sub(_mac_hex, text)

        # 3. IPv6, validated so hex-ish strings are not mangled
        def _ipv6(m: re.Match) -> str:
            orig = m.group(0)
            try:
                addr = ipaddress.IPv6Address(orig)
            except ValueError:
                return orig
            if addr.is_loopback or addr.is_unspecified:
                return orig
            if orig.lower().startswith("2001:db8"):
                return orig
            self._count("ipv6")
            return self._alloc("ipv6", orig.lower())

        text = IPV6_CAND_RE.sub(_ipv6, text)

        # 4. IPv4
        def _ipv4(m: re.Match) -> str:
            orig = m.group(0)
            try:
                ipaddress.IPv4Address(orig)
            except ValueError:
                return orig
            known = self.map["ipv4"].get(orig)
            if known:
                self._count("ipv4")
                return known
            if orig in IPV4_KEEP or orig.startswith(IPV4_DOC_PREFIXES):
                return orig      # already a documentation address
            # A dotted quad in a version-like context is a version, not a host.
            lead = text[max(0, m.start() - 24):m.start()]
            if re.search(r'(?i)(version|firmware|build|revision|oid|schema)\W{0,3}$', lead):
                return orig
            self._count("ipv4")
            return self._alloc("ipv4", orig)

        text = IPV4_RE.sub(_ipv4, text)

        # 5. UNC / share hosts
        def _unc(m: re.Match) -> str:
            host = m.group("host")
            if host.startswith(IPV4_POOL_BASE) or host.endswith(".invalid"):
                return m.group(0)
            self._count("host")
            ph = self._alloc("host", host.lower())
            # A browse response can show the same NAS hostname once as a display
            # string and later as \\host\share or smb://host/share.  The host is
            # only learned when this callback reaches the path, so register it as
            # a literal too; the final literal sweep below catches occurrences
            # that appeared earlier in this same body.
            self.add_literal(host, ph)
            return m.group("lead") + ph

        text = UNC_HOST_RE.sub(_unc, text)

        # 6. e-mail
        def _email(m: re.Match) -> str:
            orig = m.group(0)
            if orig.endswith(".invalid"):
                return orig
            self._count("email")
            return self._alloc("email", orig.lower())

        text = EMAIL_RE.sub(_email, text)

        # 7. key=value pairs naming a secret
        def _kv(m: re.Match) -> str:
            val = m.group("val")
            if not val or val in ('""', "''"):
                return m.group(0)
            quote = ""
            bare = val
            if len(val) >= 2 and val[0] in "\"'" and val[-1] == val[0]:
                quote, bare = val[0], val[1:-1]
            if not bare or bare.startswith("[REDACTED"):
                return m.group(0)
            self._count("value")
            ph = self._alloc("value", "%s=%s" % (m.group("key").lower(), bare))
            return "%s%s%s%s%s" % (m.group("key"), m.group("eq"), quote, ph, quote)

        text = KV_RE.sub(_kv, text)

        # 7b. JSON objects. /GetSettings is documented as JSON and sniff_body_kind
        #     already recognises it, so a JSON secret was previously untouched.
        def _json_kv(m: re.Match) -> str:
            bare = m.group("val").strip('"')
            if not bare or bare.startswith("[REDACTED"):
                return m.group(0)
            self._count("value")
            ph = self._alloc("value", "%s:%s" % (m.group("key").lower(), bare))
            return '"%s"%s"%s"' % (m.group("key"), m.group("sep"), ph)

        text = JSON_KV_RE.sub(_json_kv, text)

        # 7c. HTML form fields, which the port 11001 settings pages use
        def _form(m: re.Match) -> str:
            bare = m.group("val")
            if not bare or bare.startswith("[REDACTED"):
                return m.group(0)
            self._count("value")
            ph = self._alloc("value", "form:%s" % bare)
            return m.group("lead") + ph + m.group("tail")

        text = FORM_RE.sub(_form, text)

        # 8. <username>value</username>
        def _elem(m: re.Match) -> str:
            val = m.group("val").strip()
            if not val or val.startswith("[REDACTED"):
                return m.group(0)
            self._count("value")
            ph = self._alloc("value", "%s:%s" % (m.group("tag").lower(), val))
            return "%s%s%s" % (m.group("open"), ph, m.group("close"))

        text = ELEM_RE.sub(_elem, text)

        # 9. Bluetooth device names
        if self.redact_bt_names:
            def _bt(m: re.Match) -> str:
                val = m.group(2)
                if not val or val.startswith("[REDACTED"):
                    return m.group(0)
                self._count("value")
                ph = self._alloc("value", "btname:%s" % val)
                return '%s"%s"' % (m.group(1), ph)

            text = BT_NAME_RE.sub(_bt, text)

        # 10. A pattern later in this pass may have taught us a new literal
        # (notably a NAS/share hostname).  Sweep literals once more so a plain
        # occurrence that appeared earlier in the same body cannot survive.
        for original, placeholder in list(self._literals):
            if original in text:
                text = text.replace(original, placeholder)
                self._count("literal")

        return text

    def scrub_header(self, name: str, value: str) -> str:
        """Header values are redacted by header name. A whole Authorization or
        Cookie value is credential material regardless of its shape."""
        if (name or "").lower().strip() in SENSITIVE_HEADERS:
            self._count("value")
            return self._alloc("value", "hdr:%s:%s" % (name.lower(), value))
        return self.scrub(value)

    # -- reporting --------------------------------------------------------

    def key_material(self) -> Dict[str, Any]:
        """Reversible for addresses; one-way for secrets.

        Reversing an address placeholder is useful when reading your own
        results. Reversing a password placeholder is not, so the `value` class
        -- passwords, tokens, SSIDs, serials -- is stored as a salted digest
        that still supports "is this the same secret twice?" without keeping
        the secret anywhere on disk.
        """
        salt = os.urandom(16).hex()
        # `literal` includes user-supplied --secret strings and encoded variants.
        # Player names and discovered hosts already have reversible entries in
        # their own classes, so serialising `literal` adds risk without utility.
        mapping = {k: v for k, v in self.map.items()
                   if v and k not in ("value", "literal")}
        digests = {ph: hashlib.sha256((salt + orig).encode("utf-8")).hexdigest()[:16]
                   for orig, ph in self.map["value"].items()}
        return {
            "note": "DO NOT SHARE. Maps redaction placeholders back to the "
                    "original values observed on the tester's network.",
            "mapping": mapping,
            "value_class": {
                "note": "Secrets are NOT stored. Each placeholder maps to a "
                        "salted digest, so two identical secrets share a digest "
                        "but no secret can be recovered. The salt is per-run and "
                        "is not recorded.",
                "digests": digests,
            },
        }

    def summary(self) -> Dict[str, Dict[str, int]]:
        return {
            kind: {"distinct": len(self.map[kind]), "replacements": self.hits[kind]}
            for kind in self.map
            if self.map[kind] or self.hits[kind]
        }


# --------------------------------------------------------------------------
# Verification -- does anything sensitive survive in the bundle?
# --------------------------------------------------------------------------

PRIVATE_NETS = [
    ipaddress.ip_network("10.0.0.0/8"),
    ipaddress.ip_network("172.16.0.0/12"),
    ipaddress.ip_network("192.168.0.0/16"),
    ipaddress.ip_network("169.254.0.0/16"),
    ipaddress.ip_network("100.64.0.0/10"),
]


def _text_line_col(text: str, offset: int) -> Tuple[int, int]:
    """Return 1-based line and column for a character offset."""
    line = text.count("\n", 0, offset) + 1
    line_start = text.rfind("\n", 0, offset) + 1
    return line, offset - line_start + 1


def _finding_at(rel: Path, text: str, offset: int, message: str) -> str:
    line, col = _text_line_col(text, max(0, offset))
    return "%s:%d:%d (char %d): %s" % (rel, line, col, offset, message)


def verify_bundle(bundle: Path, redactor: Redactor) -> List[str]:
    """Re-scan every text file in the bundle. Returns location-rich findings.

    Findings deliberately identify the class of leaked value and its line/column
    without echoing the sensitive value itself back to the terminal or report.
    """
    findings: List[str] = []
    originals: List[Tuple[str, str, str]] = []
    for kind in ("ipv4", "ipv6", "mac", "host", "email", "literal", "name"):
        for original, placeholder in redactor.map[kind].items():
            if original:
                originals.append((kind, original, placeholder))

    for f in sorted(bundle.rglob("*")):
        if not f.is_file():
            continue
        try:
            text = f.read_text(encoding="utf-8", errors="replace")
        except Exception:
            continue
        rel = f.relative_to(bundle)

        # Report the first surviving occurrence of each known original in this
        # file.  Hostnames are DNS-case-insensitive, so check those that way.
        for kind, original, placeholder in originals:
            if kind == "host":
                pos = text.lower().find(original.lower())
            else:
                pos = text.find(original)
            if pos >= 0:
                findings.append(_finding_at(
                    rel, text, pos,
                    "leaked original value [%s; expected %s]" % (kind, placeholder)))

        for m in IPV4_RE.finditer(text):
            try:
                addr = ipaddress.IPv4Address(m.group(0))
            except ValueError:
                continue
            if m.group(0) in IPV4_KEEP or m.group(0).startswith(IPV4_DOC_PREFIXES):
                continue
            if any(addr in net for net in PRIVATE_NETS):
                findings.append(_finding_at(rel, text, m.start(),
                                            "unredacted private IPv4 address"))

        for m in MAC_RE.finditer(text):
            if not m.group(0).lower().replace("-", ":").startswith(MAC_POOL_PREFIX):
                findings.append(_finding_at(rel, text, m.start(),
                                            "unredacted MAC-shaped string"))
        for m in MAC_HEX_RE.finditer(text):
            plain = ":".join(m.group(0)[i:i + 2] for i in range(0, 12, 2)).lower()
            if not plain.startswith(MAC_POOL_PREFIX):
                findings.append("%s: unredacted bare-hex MAC-shaped string" % rel)
        for m in MAC_PCT_RE.finditer(text):
            if not m.group(0).lower().replace("%3a", ":").startswith(MAC_POOL_PREFIX):
                findings.append(_finding_at(rel, text, m.start(),
                                            "unredacted percent-encoded MAC"))

        # A secret the redactor never recognised cannot be in `originals`, so
        # matching known values alone would report "clean" while a password sat
        # in the bundle. Flag any sensitive-looking key whose value is not a
        # placeholder, whatever produced it.
        for rx in (KV_RE, JSON_KV_RE, ELEM_RE, FORM_RE):
            for m in rx.finditer(text):
                val = (m.groupdict().get("val") or "").strip().strip("\"'")
                if not val or val.startswith("[REDACTED") or val in ("0", "1", "true", "false"):
                    continue
                if val.startswith(IPV4_DOC_PREFIXES) or val.endswith(".invalid"):
                    continue
                where = m.start("val") if "val" in m.groupdict() and m.start("val") >= 0 else m.start()
                findings.append(_finding_at(
                    rel, text, where,
                    "sensitive key `%s` still has a value" % m.groupdict().get("key", "?")))

    return sorted(set(findings))


# --------------------------------------------------------------------------
# HTTP layer
# --------------------------------------------------------------------------

@dataclass
class Probe:
    id: str
    suite: str
    safety: str
    player: str
    method: str
    port: int
    path: str                       # already-encoded path + query, redacted for output
    note: str = ""
    spec_ref: str = ""
    status: Optional[int] = None
    reason: str = ""
    http_version: str = ""
    headers: List[List[str]] = field(default_factory=list)
    elapsed_ms: Optional[float] = None
    body_bytes: Optional[int] = None          # bytes AS WRITTEN to the bundle
    body_bytes_wire: Optional[int] = None     # bytes as received, before redaction
    body_sha256: str = ""                     # digest of the REDACTED body
    verbatim: bool = True                     # true = redaction changed nothing
    redaction_edits: int = 0
    claim: str = ""
    claim_verdict: str = ""
    content_type: str = ""
    root_element: str = ""
    body_file: str = ""
    body_kind: str = ""             # xml | json | text | html | binary | none
    error: str = ""
    verdict_note: str = ""
    expect: str = ""
    verdict: str = ""               # OK | UNEXPECTED | ERROR | INFO
    extra: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Player:
    label: str
    host: str
    port: int = CONTROL_PORT
    name: str = ""
    model: str = ""
    model_name: str = ""
    brand: str = ""
    version: str = ""
    schema: str = ""
    mac: str = ""
    group: str = ""
    is_master: bool = False
    is_slave: bool = False
    reachable: bool = False

    

class RawResponse:
    __slots__ = ("status", "reason", "version", "headers", "body", "elapsed", "error")

    def __init__(self):
        self.status: Optional[int] = None
        self.reason = ""
        self.version = ""
        self.headers: List[Tuple[str, str]] = []
        self.body: bytes = b""
        self.elapsed: float = 0.0
        self.error: str = ""


def http_call(host: str, port: int, path: str, method: str = "GET",
              body: Optional[bytes] = None, extra_headers: Optional[Dict[str, str]] = None,
              timeout: float = 20.0, send_sovi_headers: bool = True,
              max_body: int = MAX_BODY_BYTES) -> RawResponse:
    """One HTTP request with full control over method, headers and timing."""
    out = RawResponse()
    headers: Dict[str, str] = {}
    if send_sovi_headers:
        headers.update(SOVI_HEADERS)
    else:
        headers["User-Agent"] = SOVI_HEADERS["User-Agent"]
    if extra_headers:
        headers.update(extra_headers)
    if body is not None and "Content-Type" not in headers:
        headers["Content-Type"] = "application/x-www-form-urlencoded"

    # http.client encodes the request line as ASCII. Several paths come from
    # the device itself -- the /Status <image>, browse url= attributes,
    # playURLs -- so an artist or album with a non-ASCII character raised
    # UnicodeEncodeError, which was not in the except clause and killed the suite.
    try:
        path.encode("ascii")
    except UnicodeEncodeError:
        path = urllib.parse.quote(path, safe="".join(map(chr, range(33, 127))))

    start = time.monotonic()
    conn = None
    try:
        conn = http.client.HTTPConnection(host, port, timeout=timeout)
        conn.request(method, path, body=body, headers=headers)
        resp = conn.getresponse()
        out.status = resp.status
        out.reason = resp.reason or ""
        out.version = "HTTP/1.1" if resp.version == 11 else "HTTP/1.0"
        out.headers = [(k, v) for k, v in resp.getheaders()]
        out.body = resp.read(max_body)
    except socket.timeout:
        out.error = "timeout after %.1fs" % timeout
    except (http.client.HTTPException, OSError, ValueError) as exc:
        # ValueError covers UnicodeEncodeError and http.client's own checks on
        # malformed request lines, both reachable from device-supplied paths.
        out.error = "%s: %s" % (type(exc).__name__, exc)
    finally:
        out.elapsed = time.monotonic() - start
        if conn is not None:
            try:
                conn.close()
            except Exception:
                pass
    return out


def sniff_body_kind(body: bytes, content_type: str) -> str:
    if not body:
        return "none"
    head = body[:512].lstrip()
    ct = (content_type or "").lower()
    if head.startswith(b"<?xml") or (head.startswith(b"<") and not head[:20].lower().startswith(b"<!doctype html") and b"html" not in head[:20].lower()):
        return "xml"
    if head[:1] in (b"{", b"[") or "json" in ct:
        return "json"
    if b"<html" in head[:200].lower() or b"<!doctype html" in head[:200].lower() or head.startswith(b"<h1"):
        return "html"
    if ct.startswith("text/") or ct.startswith("application/xml"):
        return "text"
    # binary sniff
    if body[:2] == b"\xff\xd8" or body[:8] == b"\x89PNG\r\n\x1a\n" or body[:6] in (b"GIF87a", b"GIF89a") or body[:4] == b"RIFF":
        return "binary"
    if b"\x00" in body[:512]:
        return "binary"
    return "text"


def root_element_of(text: str) -> str:
    m = re.search(r"<\s*([A-Za-z_][\w.:-]*)", text[:4096])
    return m.group(1) if m else ""




# --------------------------------------------------------------------------
# Claim registry
#
# A stable id per claim, so a result is comparable across runs, firmwares and
# models, and so a DISCONFIRMED result can be recorded permanently rather than
# rediscovered. Ids never change and are never reused; a retired claim keeps its
# id and gains a verdict.
# --------------------------------------------------------------------------

CLAIMS: Dict[str, Dict[str, str]] = {
    "C-01-diagnostics-80":   {"claim": "/diagnostics answers on port 80",
                              "source": "blutui (Rust)", "spec": "13"},
    "C-02-diagnostics-11000": {"claim": "/diagnostics does NOT answer on port 11000",
                              "source": "hardware, this project", "spec": "13"},
    "C-03-audiomodes-read":  {"claim": "bare GET /audiomodes is a read returning <audiomode>",
                              "source": "BluShell (schema 25)", "spec": "10.4"},
    "C-04-proxytoslave":     {"claim": "/proxyToSlave exists as a POST relay to a slave",
                              "source": "blutui (Rust)", "spec": "10.0"},
    "C-05-sync-legacy":      {"claim": "the legacy /Sync grouping endpoint still exists",
                              "source": "bluos-dashboard", "spec": "5.2"},
    "C-06-getsettings":      {"claim": "/GetSettings exists and returns JSON",
                              "source": "BluOS Integration Utility 1.8.1", "spec": "10.1"},
    "C-07-artwork-cors":     {"claim": "/Artwork sends Access-Control-Allow-Origin: *",
                              "source": "BluShepherd (2016, fw 2.8.3)", "spec": "9"},
    "C-08-artwork-noetag":   {"claim": "/Artwork sends no ETag and no Last-Modified",
                              "source": "BluShepherd (2016)", "spec": "9"},
    "C-09-artwork-nonefound": {"claim": "/Artwork answers <artwork>none found</artwork> when there is none",
                              "source": "BluShell", "spec": "9"},
    "C-10-artwork-byname":   {"claim": "/Artwork?album=&artist= selects artwork by name",
                              "source": "2015 forum, BluShepherd", "spec": "9"},
    "C-11-radio-attrs":      {"claim": "radio items carry key / is_active / guide_id / preset_id / subtext",
                              "source": "Blu4Net, BluShell", "spec": "11.10"},
    "C-12-radio-totalcount": {"claim": "<radiotime> carries a total_count attribute",
                              "source": "Blu4Net", "spec": "11.10"},
    "C-13-search-containers": {"claim": "/Search returns per-type containers",
                              "source": "BluShell (schema 25)", "spec": "11.10"},
    "C-14-songs-album-wrapper": {"claim": "album-scoped /Songs nests <song> inside <album>, with <discno>n/m</discno>",
                              "source": "BluShepherd (2016)", "spec": "11.10"},
    "C-15-alarms-bitmask":   {"claim": "/Alarms encodes days as a bitmask",
                              "source": "BluShell (schema 25)", "spec": "11.6"},
    "C-16-shares-11000":     {"claim": "/Shares has migrated to port 11000",
                              "source": "conjecture (ms -> ms-go migration)", "spec": "13"},
    "C-17-is-preset":        {"claim": "<is_preset> appears as a /Status element",
                              "source": "Blu4Net", "spec": "2.2"},
    "C-18-sort-descending":  {"claim": "a descending sort value is accepted (reverseName)",
                              "source": "Android controller reads the attribute", "spec": "8.2"},
    "C-19-lsdp-unicast-R":   {"claim": "an R query sent by unicast is answered",
                              "source": "vendor wire format; no client sends it", "spec": "12.1"},
    "C-20-browse-sid":       {"claim": "sid is required on /Browse",
                              "source": "bluos-api-rs", "spec": "15.1"},
    "C-21-schema-headers":   {"claim": "omitting X-Sovi-Schema-Version changes the response",
                              "source": "inference in the specification", "spec": "1.4"},
    "C-22-page-cap-50":      {"claim": "browse paging is capped server-side at 50 items",
                              "source": "hardware, this project", "spec": "8.2"},
    "C-23-11001-settings-only": {"quantifier": "no_counterexample", "claim": "port 11001 serves settings and nothing else",
                              "source": "hardware, this project", "spec": "10.3"},
    "C-24-player-enumeration": {"quantifier": "any", "claim": "some endpoint enumerates players outside a group",
                              "source": "open question 7", "spec": "16"},
    # round 2
    "C-30-removeslave-bare": {"claim": "a bare /RemoveSlave ungroups every slave",
                              "source": "bluos HA integration (Pimmeke1989)", "spec": "17"},
    "C-31-channelmode-numeric": {"claim": "/AddSlave takes channelMode=0|1|2",
                              "source": "bluos HA integration (Pimmeke1989)", "spec": "17"},
    "C-32-addslave-noport":  {"claim": "port is optional in the singular /AddSlave form",
                              "source": "2015 forum", "spec": "5"},
    "C-33-slavevolume-combined": {"claim": "/SlaveVolume accepts slave=<ip>:<port>",
                              "source": "blutui (Rust)", "spec": "4"},
    "C-34-name-post":        {"claim": "/Name accepts a POST body of nodename=",
                              "source": "blutui (Rust)", "spec": "10"},
    "C-35-setting-post":     {"claim": "setting writes are POST form, not GET query",
                              "source": "blutui (Rust) vs pyblu", "spec": "10.3"},
    "C-36-mute-polarity":    {"claim": "mute=1 mutes and mute=0 unmutes (vendor doc is inverted)",
                              "source": "Android app vs CI API v1.7 3.1", "spec": "4"},
    "C-37-play-inputtype":   {"claim": "/Play?inputType=&index= selects an input",
                              "source": "bluos-api-rs", "spec": "15.2"},
    "C-38-play-roots":       {"claim": "the play response has four possible root elements",
                              "source": "Blu4Net", "spec": "7.3"},
    "C-54-setmaster-one-sided": {"claim": "a group formed by /SetMaster?master= is one-sided: the master does not list the joiner as a <slave>",
                              "source": "hardware, this project", "spec": "5.3"},
    "C-39-master-swap":      {"claim": "master and slave roles can be swapped without ungrouping first",
                              "source": "open question raised by the tester", "spec": "5.3"},
    "C-41-setmaster-bare-standalone": {"claim": "a bare /SetMaster on a standalone player is a no-op",
                              "source": "hardware, single pass", "spec": "5.3"},
    "C-42-setmaster-bare-master": {"claim": "a bare /SetMaster on a master is a no-op and does not dissolve its group",
                              "source": "hardware, single pass", "spec": "5.3"},
    "C-43-setmaster-bare-slave": {"claim": "a bare /SetMaster on a slave leaves the group",
                              "source": "hardware, single pass", "spec": "5.3"},
    "C-44-setmaster-master-param": {"claim": "/SetMaster?master= joins that player's group",
                              "source": "hardware, single pass", "spec": "5.3"},
    "C-45-setmaster-slave-param": {"claim": "/SetMaster ignores a slave= parameter",
                              "source": "hardware, single pass", "spec": "5.3"},
    "C-55-setmaster-bare-fresh": {"claim": "a bare /SetMaster answers with the POST-call SyncStatus (fresh etag)",
                              "source": "hardware, this project", "spec": "5.3"},
    "C-46-setmaster-stale-response": {"claim": "/SetMaster?master= answers with the PRE-call SyncStatus, same etag",
                              "source": "hardware, single pass", "spec": "5.3"},
    "C-47-setmaster-noport": {"claim": "port is optional on /SetMaster?master=",
                              "source": "untested", "spec": "5.3"},
    "C-48-setmaster-self":   {"claim": "/SetMaster?master=<own address> is handled gracefully",
                              "source": "untested", "spec": "5.3"},
    "C-49-setmaster-badtarget": {"claim": "/SetMaster?master=<not a player> is handled gracefully",
                              "source": "untested", "spec": "5.3"},
    "C-50-setmaster-reparent": {"claim": "a slave can be reparented onto another master with ?master=",
                              "source": "bluos-dashboard (orphan recovery)", "spec": "5.1"},
    "C-51-setmaster-nested": {"claim": "a bare /SetMaster on a nested master detaches it cleanly",
                              "source": "untested", "spec": "14"},
    "C-52-disabled-input-hidden": {"quantifier": "any", "claim": "an input disabled in the app still appears in some API surface",
                              "source": "raised by the tester", "spec": "8.1"},
    "C-53-disabled-input-playable": {"quantifier": "any", "claim": "an input disabled in the app can still be selected through the API",
                              "source": "raised by the tester", "spec": "15.2"},
    "C-40-repeat-shuffle-read": {"quantifier": "no_counterexample", "claim": "bare /Repeat and /Shuffle read rather than write",
                              "source": "untested", "spec": "3"},
}



# --------------------------------------------------------------------------
# Response parsing
#
# One implementation each for /SyncStatus and /Status. There were three
# SyncStatus parsers before, and a restore path that depends on reading
# <slave id=...> correctly must not be able to drift from the path that read it
# in the first place.
# --------------------------------------------------------------------------

ROOT_TAG_RE = re.compile(r"\s*(?:<\?xml[^>]*\?>\s*)?<(?P<tag>[A-Za-z_][\w.:-]*)\b[^>]*>")
SLAVE_ID_RE = re.compile(r'<slave\b[^>]*\bid="([^"]+)"')
SLAVE_TAG_RE = re.compile(r"<slave\b[^>]*/?>")
def mac_placeholder(n: int) -> str:
    return MAC_POOL_PREFIX + "%02x:%02x" % divmod(n, 256)


MASTER_RE = re.compile(r"<master[^>]*>([^<]*)</master>|<master[^>]*/>")


def root_attrs(text: str) -> Dict[str, str]:
    """Attributes of the ROOT element only.

    Scanning a slice of the document instead lets a child win: <slave name=...>
    and <bluetoothOutput name=...> both carry `name`, so a master would report
    its slave's name as its own.
    """
    m = ROOT_TAG_RE.match(text or "")
    if not m:
        return {}
    # Unescape: a player called "Stue & Kokken" arrives as "Stue &amp; Kokken",
    # and the rename restore wrote that literal string back to the device.
    return {k: html.unescape(v) for k, v in ATTR_RE.findall(m.group(0))}


def xml_unescape(value: str) -> str:
    """One implementation. There were five copies of ,
    which handled that one entity and no other."""
    return html.unescape(value or "")


def element_text(text: str, name: str) -> str:
    m = re.search(r"<%s>([^<]*)</%s>" % (name, name), text or "")
    return html.unescape(m.group(1)).strip() if m else ""


def element_int(text: str, name: str) -> Optional[int]:
    try:
        return int(element_text(text, name))
    except ValueError:
        return None


@dataclass
class SlaveRef:
    """A slave as its master describes it. The port and channelMode matter:
    rebuilding a stereo pair or a CI580 secondary zone with defaults turns it
    into a plain group at the wrong port."""
    id: str
    port: str = ""
    channel_mode: str = ""

    def with_port(self, fallback: int) -> str:
        return self.port or str(fallback)


@dataclass
class SyncInfo:
    etag: str = ""
    name: str = ""
    group: str = ""
    master: str = ""
    slaves: List[str] = field(default_factory=list)
    slave_refs: List[SlaveRef] = field(default_factory=list)
    attrs: Dict[str, str] = field(default_factory=dict)
    reachable: bool = True

    @property
    def grouped(self) -> bool:
        return bool(self.master or self.slaves)

    @property
    def topology(self) -> Tuple[str, Tuple[str, ...]]:
        """Both halves. Comparing slaves alone let a player that began as
        someone's slave and ended standalone count as restored."""
        return (self.master, tuple(sorted(self.slaves)))


def parse_sync(text: str) -> SyncInfo:
    attrs = root_attrs(text)
    m = MASTER_RE.search(text or "")
    return SyncInfo(
        etag=attrs.get("etag", ""),
        name=attrs.get("name", ""),
        group=attrs.get("group", ""),
        master=((m.group(1) or "present") if m else ""),
        slaves=SLAVE_ID_RE.findall(text or ""),
        slave_refs=[
            SlaveRef(id=a.get("id", ""), port=a.get("port", ""),
                     channel_mode=a.get("channelMode", ""))
            for a in (dict(ATTR_RE.findall(tag)) for tag in SLAVE_TAG_RE.findall(text or ""))
            if a.get("id")
        ],
        attrs=attrs,
    )


def fetch_sync(p: Player, timeout: float = 10.0) -> SyncInfo:
    """An unreachable player is UNKNOWN, not standalone.

    Returning an empty SyncInfo on a transport error made a player that had
    simply stopped answering read as "no master, no slaves", which teardown and
    verification both took for success.
    """
    raw = http_call(p.host, p.port, "/SyncStatus", timeout=timeout)
    if raw.error or raw.status != 200 or not raw.body:
        return SyncInfo(reachable=False)
    info = parse_sync(raw.body.decode("utf-8", "replace"))
    info.reachable = True
    return info


# --------------------------------------------------------------------------
# Runner
# --------------------------------------------------------------------------

class Runner:
    def __init__(self, opts, redactor: Redactor, outdir: Path):
        self.opts = opts
        self.red = redactor
        self.out = outdir
        self.raw = outdir / "raw"
        self.raw.mkdir(parents=True, exist_ok=True)
        self.results: List[Probe] = []
        # Raw, UNREDACTED bodies, for control flow only: following a browse key,
        # picking a playURL, reading a preset id. Lives on the Runner and never
        # on a Probe, so it cannot reach the manifest. Bounded, because a browse
        # crawl plus a settings sweep would otherwise hold everything in memory.
        self.raw_bodies: Dict[str, str] = {}
        self._raw_bytes = 0
        self.restores: List[Dict[str, Any]] = []
        self.wire_hashes: Dict[str, str] = {}
        self.players: Dict[str, Player] = {}
        self.synthetic = False
        self.facts: Dict[str, Any] = {}     # things later suites need (songids, services...)
        self._n = 0
        self._lock = threading.Lock()
        self.current_suite = "misc"

    # -- helpers ----------------------------------------------------------

    def _next_id(self, suite: str) -> str:
        with self._lock:
            self._n += 1
            return "%03d-%s" % (self._n, suite)

    def allowed(self, safety: str) -> bool:
        if safety == SAFETY_READ:
            return True
        if safety == SAFETY_PROBE:
            return not self.opts.no_probe
        if safety == SAFETY_STATE:
            return bool(getattr(self.opts, "allow_state", False))
        return False   # destructive is not implemented

    def player(self, label: str) -> Optional[Player]:
        return self.players.get(label)

    def targets(self) -> List[Player]:
        return [p for p in self.players.values() if p.reachable]

    def writable(self) -> List[Player]:
        """Players this run is permitted to change. --preserve keeps a player
        read-only even in round 2; use it for the one holding presets you care
        about, or anything driving a live system."""
        keep = {x.strip().upper() for x in (self.opts.preserve or [])}
        return [p for p in self.targets() if p.label not in keep]

    # -- the one call every suite uses ------------------------------------

    def call(self, player: Optional[Player], path: str, *, port: Optional[int] = None,
             method: str = "GET", body: Optional[bytes] = None,
             headers: Optional[Dict[str, str]] = None, timeout: float = 20.0,
             safety: str = SAFETY_READ, note: str = "", spec_ref: str = "",
             expect: str = "", claim: str = "", claim_confirm: str = "",
             claim_disconfirm: str = "status=404", save: bool = True, sovi_headers: bool = True,
             host: Optional[str] = None, suite: Optional[str] = None,
             quiet: bool = False) -> Probe:

        suite = suite or self.current_suite
        if port is None:
            port = player.port if player else CONTROL_PORT
        label = player.label if player else "-"
        target = host or (player.host if player else "")
        pid = self._next_id(suite)

        pr = Probe(id=pid, suite=suite, safety=safety, player=label, method=method,
                   port=port, path=self.red.scrub(path), note=self.red.scrub(note),
                   spec_ref=spec_ref, expect=expect, claim=claim)

        if not self.allowed(safety):
            pr.verdict = "SKIPPED"
            pr.error = "safety class '%s' not enabled" % safety
            self.results.append(pr)
            return pr

        if not target:
            pr.verdict = "ERROR"
            pr.error = "no target host"
            self.results.append(pr)
            return pr

        raw = http_call(target, port, path, method=method, body=body,
                        extra_headers=headers, timeout=timeout,
                        send_sovi_headers=sovi_headers)

        pr.elapsed_ms = round(raw.elapsed * 1000, 1)
        pr.status = raw.status
        pr.reason = raw.reason
        pr.http_version = raw.version
        pr.error = raw.error
        pr.headers = [[k, self.red.scrub_header(k, v)] for k, v in raw.headers]
        pr.content_type = next((v for k, v in raw.headers if k.lower() == "content-type"), "")

        if raw.body:
            pr.body_bytes_wire = len(raw.body)
            if len(raw.body) >= MAX_BODY_BYTES:
                pr.extra["truncated"] = True
                pr.verdict_note = "body hit the %d-byte read cap" % MAX_BODY_BYTES
            # The digest of the ORIGINAL body is a de-anonymisation vector: for a
            # structured body such as /SyncStatus the only unknown is the address,
            # a 2^16 search. It is kept in the do-not-share key file, never here.
            self.wire_hashes[pr.id] = hashlib.sha256(raw.body).hexdigest()
            kind = sniff_body_kind(raw.body, pr.content_type)
            pr.body_kind = kind
            if kind == "binary":
                # never store binary: it may carry EXIF or other embedded data
                pr.extra["binary_first_bytes"] = binascii.hexlify(raw.body[:16]).decode()
                pr.body_bytes = 0
            else:
                text = raw.body.decode("utf-8", errors="replace")
                clean, edits = self.red.scrub_counted(text)
                pr.redaction_edits = edits
                pr.verbatim = (edits == 0)
                pr.body_bytes = len(clean.encode("utf-8"))
                pr.body_sha256 = hashlib.sha256(clean.encode("utf-8")).hexdigest()
                if kind in ("xml", "html"):
                    pr.root_element = root_element_of(clean)
                if save and not self.opts.no_bodies:
                    ext = {"xml": "xml", "json": "json", "html": "html"}.get(kind, "txt")
                    fname = "%s.%s" % (pid, ext)
                    (self.raw / fname).write_text(clean, encoding="utf-8")
                    pr.body_file = "raw/" + fname
                pr.extra["body_preview"] = clean[:400]
                # The RAW body, for control flow only. Never serialised: it is
                # popped before the probe reaches the manifest. Decisions must
                # not be made from redacted text, or a placeholder gets sent
                # back to the device as a browse key or a playURL.
                pr.extra["body_full"] = text
                pr.extra["body_redacted"] = clean
        else:
            pr.body_bytes = 0
            pr.body_bytes_wire = 0
            pr.body_kind = "none"

        if save and not self.opts.no_bodies:
            head_lines = ["%s %s %s" % (raw.version or "HTTP/?", raw.status, raw.reason)]
            head_lines += ["%s: %s" % (k, self.red.scrub_header(k, v)) for k, v in raw.headers]
            head_lines.append("")
            head_lines.append("# request: %s %s:%d%s" % (method, self.red.scrub(target), port, self.red.scrub(path)))
            (self.raw / ("%s.head.txt" % pid)).write_text("\n".join(head_lines), encoding="utf-8")

        body_text = pr.extra.get("body_full", "")
        pr.verdict = self._verdict(pr, body_text)
        if claim:
            pr.claim_verdict = self._claim_verdict(pr, claim_confirm, claim_disconfirm, body_text)
        raw_text = pr.extra.pop("body_full", None)   # never serialised
        pr.extra.pop("body_redacted", None)
        if raw_text and len(raw_text) <= 512 * 1024 and self._raw_bytes < 32 * 1024 * 1024:
            self.raw_bodies[pr.id] = raw_text
            self._raw_bytes += len(raw_text)
        self.results.append(pr)
        if not quiet:
            self._echo(pr)
        return pr

    def _match(self, pr: Probe, rule: str, text: str) -> bool:
        """Clauses, all ANDed, separated by ';':
             status=200|404     root=browse      kind=xml|json
             header=ETag        header=Access-Control-Allow-Origin:*
             contains=<substring in the body>    absent=<substring>
        """
        for clause in [c.strip() for c in rule.split(";") if c.strip()]:
            if clause.startswith("status="):
                if pr.status not in {int(x) for x in clause.split("=", 1)[1].split("|")}:
                    return False
            elif clause.startswith("root="):
                if pr.root_element not in set(clause.split("=", 1)[1].split("|")):
                    return False
            elif clause.startswith("kind="):
                if pr.body_kind not in set(clause.split("=", 1)[1].split("|")):
                    return False
            elif clause.startswith("header="):
                spec = clause.split("=", 1)[1]
                name, _, want = spec.partition(":")
                got = next((v for k, v in pr.headers if k.lower() == name.lower().strip()), None)
                if got is None:
                    return False
                if want and want.strip() not in got:
                    return False
            elif clause.startswith("noheader="):
                name = clause.split("=", 1)[1].strip()
                if any(k.lower() == name.lower() for k, v in pr.headers):
                    return False
            elif clause.startswith("contains="):
                if clause.split("=", 1)[1] not in text:
                    return False
            elif clause.startswith("absent="):
                if clause.split("=", 1)[1] in text:
                    return False
            else:
                # "stauts=200" used to match anything, so a typo turned into a
                # silent pass and a wrong verdict.
                raise ValueError("unknown expectation clause %r" % clause)
        return True

    def _verdict(self, pr: Probe, text: str = "") -> str:
        if pr.error:
            return "ERROR"
        if not pr.expect:
            return "INFO"
        return "OK" if self._match(pr, pr.expect, text) else "UNEXPECTED"

    def _claim_verdict(self, pr: Probe, confirm: str, disconfirm: str, text: str = "") -> str:
        """CONFIRMED / DISCONFIRMED / INCONCLUSIVE. INCONCLUSIVE is a real
        answer and is recorded as such; it is not the same as untested."""
        if pr.error:
            return "INCONCLUSIVE"
        if confirm and self._match(pr, confirm, text):
            return "CONFIRMED"
        if disconfirm and self._match(pr, disconfirm, text):
            return "DISCONFIRMED"
        return "INCONCLUSIVE"

    def _echo(self, pr: Probe) -> None:
        mark = {"OK": "ok ", "UNEXPECTED": "!! ", "ERROR": "ERR", "INFO": "-  ", "SKIPPED": "sk "}.get(pr.verdict, "?  ")
        status = pr.status if pr.status is not None else (pr.error[:24] or "-")
        line = "  %s %-11s %-4s :%-5d %-58s %s" % (
            mark, pr.id, pr.player, pr.port, pr.path[:58], status)
        print(line, flush=True)

    def note(self, suite: str, note: str, detail: str = "", verdict: str = "INFO",
             extra=None, claim: str = "", claim_verdict: str = "",
             quiet: bool = False) -> Probe:
        """Record an observation that is not a single HTTP request."""
        pr = Probe(id=self._next_id(suite), suite=suite, safety=SAFETY_READ, player="-",
                   method="-", port=0, path="(analysis)", note=self.red.scrub(note),
                   verdict=verdict,
                   claim=claim, claim_verdict=claim_verdict)
        pr.extra["detail"] = self.red.scrub(detail)
        if extra:
            pr.extra.update(extra)
        self.results.append(pr)
        if not quiet:
            print("  -   %-11s %s" % (pr.id, pr.note[:96]), flush=True)
        return pr

    # -- restore ledger ---------------------------------------------------
    #
    # A suite that changes something registers how to undo it AT THE MOMENT IT
    # CHANGES IT, not at the end of the suite. main() runs the ledger in a
    # finally block, so a crash, an exception or Ctrl-C still puts the hardware
    # back. Restores must be idempotent: the normal path runs them too.

    def write(self, player: Player, path: str, note: str, *, port: Optional[int] = None,
              timeout: float = 15.0) -> Probe:
        """A state-changing GET that is recorded like any other probe.

        Teardown, rebuild, trial resets and ledger undos used to call http_call
        directly. That bypassed the safety gate and left them out of the
        manifest, so the bundle README undercounted what the run had changed.
        """
        return self.call(player, path, port=port, safety=SAFETY_STATE, note=note,
                         spec_ref="5", save=False, quiet=True, timeout=timeout)

    def defer(self, description: str, undo: Callable[[], None]) -> Dict[str, Any]:
        entry = {"description": self.red.scrub(description), "undo": undo,
                 "done": False, "error": ""}
        self.restores.append(entry)
        return entry

    def defer_get(self, player: Player, path: str, description: str,
                  verify: Optional[Callable[[], bool]] = None) -> Dict[str, Any]:
        """The common case: undoing a change is one GET.

        http_call never raises -- it reports transport errors in `.error` and
        returns whatever status arrived. An undo that ignored both was marked
        `done` and printed `ok` after a timeout or a 500, so the ledger
        verified nothing at all.
        """
        def undo() -> None:
            r = http_call(player.host, player.port, path, timeout=15)
            if r.error or not (r.status and 200 <= r.status < 300):
                raise RuntimeError("GET %s -> %s" % (path, r.error or r.status))
            if verify is not None and not verify():
                raise RuntimeError("%s: readback does not match after %s"
                                   % (player.label, path))
        return self.defer(description, undo)

    def run_restores(self) -> List[Dict[str, Any]]:
        pending = [e for e in self.restores if not e["done"]]
        if not pending:
            return []
        print("\n== restoring %d change(s)" % len(pending), flush=True)
        for entry in reversed(pending):        # unwind in reverse order
            try:
                entry["undo"]()
                entry["done"] = True
                print("  ok  %s" % entry["description"][:88], flush=True)
            except KeyboardInterrupt:
                entry["error"] = "interrupted"
                print("  !!  interrupted during: %s" % entry["description"][:70], flush=True)
            except Exception as exc:
                entry["error"] = "%s: %s" % (type(exc).__name__, exc)
                print("  ERR %s -- %s" % (entry["description"][:66], entry["error"]), flush=True)
        return [e for e in self.restores if e["error"] or not e["done"]]

    def banner(self, title: str) -> None:
        print("\n== %s" % title, flush=True)


# --------------------------------------------------------------------------
# Pre-flight: identify players, seed the redactor
# --------------------------------------------------------------------------

ATTR_RE = re.compile(r'(\w+)\s*=\s*"([^"]*)"')


def preflight(run: Runner, specs: List[Tuple[str, str, int]]) -> None:
    """Fetch /SyncStatus from each player BEFORE anything is written, so every
    address, MAC and (optionally) room name in the run is already mapped."""
    run.banner("Pre-flight: identifying players and seeding the redactor")
    for idx, (label, host, port) in enumerate(specs):
        p = Player(label=label, host=host, port=port)
        run.players[label] = p
        # reserve a stable, human-meaningful placeholder for this player
        run.red.reserve_ipv4(host, "%s%d" % (IPV4_POOL_BASE, 11 + idx))

        raw = http_call(host, port, "/SyncStatus", timeout=8.0)
        if raw.status != 200 or not raw.body:
            print("  !! %-4s %s:%d unreachable (%s)" % (label, host, port, raw.error or raw.status))
            continue
        text = raw.body.decode("utf-8", errors="replace")
        p.reachable = True
        info = parse_sync(text)
        attrs = info.attrs
        p.name = attrs.get("name", "")
        p.model = attrs.get("model", "")
        p.model_name = attrs.get("modelName", "")
        p.brand = attrs.get("brand", "")
        p.version = attrs.get("version", "")
        p.schema = attrs.get("schemaVersion", "")
        p.mac = attrs.get("mac", "")
        p.group = attrs.get("group", "")
        p.is_slave = bool(info.master)
        p.is_master = bool(info.slaves)

        if p.mac:
            run.red.reserve_mac(p.mac, mac_placeholder(11 + idx))
        if p.name:
            run.red.add_player_name(p.name, "Room-%s" % label)
        for m in re.finditer(r'<(?:slave|master)[^>]*(?:id="([^"]+)"|>([^<]+)<)', text):
            addr = (m.group(1) or m.group(2) or "").split(":")[0].strip()
            if addr:
                try:
                    ipaddress.IPv4Address(addr)
                    run.red.register_ipv4(addr)
                except ValueError:
                    pass

        print("  ok  %-4s %-10s %-8s fw %-9s schema %-3s %s" % (
            label, p.name if not run.red.redact_names else "Room-" + label,
            p.model, p.version, p.schema,
            "master" if p.is_master else ("slave" if p.is_slave else "standalone")))

    for extra in run.opts.secret or []:
        run.red.add_literal(extra, "[REDACTED-USER-SUPPLIED]")

    # the tester's own address will show up in LSDP and auth headers
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("192.0.2.1", 9))
        run.red.register_ipv4(s.getsockname()[0])
        s.close()
    except Exception:
        pass


# --------------------------------------------------------------------------
# Capability detection
#
# A test whose result is decided by what the hardware lacks is not a test. If a
# player has no capture inputs, "the input selector did nothing" says nothing
# about the selector. Detect the gap, skip the suite, and say so -- an explicit
# NOT APPLICABLE is honest, whereas a DISCONFIRMED would be a lie about the
# protocol drawn from a fact about the fleet.
# --------------------------------------------------------------------------

def detect_capabilities(run: Runner) -> Dict[str, Dict[str, Any]]:
    caps: Dict[str, Dict[str, Any]] = {}
    for p in run.targets():
        c: Dict[str, Any] = {}
        sy = http_call(p.host, p.port, "/SyncStatus", timeout=10)
        sytext = sy.body.decode("utf-8", "replace") if sy.body else ""
        br = http_call(p.host, p.port, "/Browse", timeout=20)
        brtext = br.body.decode("utf-8", "replace") if br.body else ""
        pr = http_call(p.host, p.port, "/Presets", timeout=10)
        bt = http_call(p.host, p.port, "/BTDevices?timeout=1", timeout=15)

        c["inputs"] = len(re.findall(r'inputType="', brtext))
        c["bluetooth"] = (bt.status == 200 and b"<" in (bt.body or b"")) or "bluetooth" in sytext.lower()
        c["presets"] = len(re.findall(r"<preset\b", pr.body.decode("utf-8", "replace") if pr.body else ""))
        c["subwoofer"] = 'hasSubwoofer="true"' in sytext
        c["fixed_volume"] = "<volume>-1</volume>" in sytext
        c["model"] = p.model
        caps[p.label] = c
    run.facts["capabilities"] = caps

    rows = ["| player | model | capture inputs | bluetooth | presets | subwoofer |",
            "|---|---|---|---|---|---|"]
    for lbl, c in caps.items():
        rows.append("| %s | %s | %d | %s | %d | %s |" % (
            lbl, c["model"], c["inputs"], "yes" if c["bluetooth"] else "no",
            c["presets"], "yes" if c["subwoofer"] else "no"))
    run.note("env", "fleet capabilities, used to skip tests this hardware cannot answer",
             "\n".join(rows))

    untestable: List[str] = []
    if not any(c["inputs"] for c in caps.values()):
        untestable.append("C-37 / C-53 input selection: no player advertises a capture input, "
                          "so nothing distinguishes 'the selector failed' from 'there is no "
                          "input to select'")
    elif not any(c["inputs"] >= 2 for c in caps.values()):
        untestable.append("input selection is weakened: no player advertises two inputs, so "
                          "'it switched' cannot be separated from 'it was already there'. "
                          "Temporarily enabling a second input makes the result conclusive")
    if not any(c["presets"] for c in caps.values()):
        untestable.append("C-17 <is_preset>: no player has a preset configured")
    if not any(c["subwoofer"] for c in caps.values()):
        untestable.append("subwoofer pairing (/GetUnpairedSlaves, pairWithSub): no paired "
                          "subwoofer in this fleet")
    if not any(c["bluetooth"] for c in caps.values()):
        untestable.append("/BTDevices and Bluetooth output: not available on this hardware")
    if len(run.targets()) < 3:
        untestable.append("nested grouping (T-16, C-51): needs three players")
    untestable.append("T-14 authentication: no way found to set credentials on consumer "
                      "N-series hardware; the auth path stays source-derived and unexercised")
    untestable.append("CI-series multi-zone port offsets: no CI hardware in this fleet")

    run.facts["untestable"] = untestable
    run.note("env", "%d thing(s) this fleet cannot answer" % len(untestable),
             "\n".join("- " + u for u in untestable) +
             "\n\nThese are recorded as NOT APPLICABLE rather than left to look like "
             "failures. A claim untestable on this hardware must never be written into the "
             "register as DISCONFIRMED.")
    return caps


# --------------------------------------------------------------------------
# Suites
# --------------------------------------------------------------------------

def suite_env(run: Runner) -> None:
    """Inventory. Establishes what this fleet is and captures the core reads."""
    run.current_suite = "env"
    run.banner("env -- player inventory and core state reads")
    for p in run.targets():
        run.call(p, "/SyncStatus", note="player identity and group topology",
                 spec_ref="2.1", expect="status=200;root=SyncStatus|UpgradeStatusStage1|UpgradeStatusStage2")
        run.call(p, "/Status", note="full player state", spec_ref="2.2",
                 expect="status=200;root=status")
        run.call(p, "/GitVersion", note="firmware build", spec_ref="2.5", expect="status=200")
        run.call(p, "/Services", note="service and menu tree (the sort/filter vocabulary)",
                 spec_ref="2.6;8.3", expect="status=200;root=services")
        run.call(p, "/Presets", note="preset list", spec_ref="6.1", expect="status=200")
        run.call(p, "/Playlist", note="current queue", spec_ref="7.1", expect="status=200")
        run.call(p, "/Volume", note="bare /Volume as a read (bluesound_alt)", spec_ref="4",
                 expect="status=200")
        run.call(p, "/Name", note="bare /Name reads rather than writes", spec_ref="10",
                 expect="status=200")
        run.call(p, "/Alarms",
                 note="alarm list; days bitmask claim (times are in %s)"
                      % SOVI_HEADERS.get("X-Sovi-Tz", PROBE_TZ),
                 spec_ref="11.6",
                 expect="status=200", claim="C-15-alarms-bitmask",
                 claim_confirm="status=200;contains=days",
                 claim_disconfirm="status=200;absent=<alarm")
        run.call(p, "/BTDevices?timeout=1", note="bluetooth device list", spec_ref="11.7",
                 timeout=15, expect="status=200")
        run.call(p, "/GetUnpairedSlaves", note="pairable speakers", spec_ref="11.4",
                 expect="status=200")

    # harvest facts later suites need
    for p in run.targets():
        raw = http_call(p.host, p.port, "/Status", timeout=8)
        if raw.status == 200:
            text = raw.body.decode("utf-8", "replace")
            for tag in ("songid", "album", "artist", "service", "image", "fn"):
                m = re.search(r"<%s>([^<]*)</%s>" % (tag, tag), text)
                if m and m.group(1):
                    run.facts.setdefault(tag, m.group(1))
        raw = http_call(p.host, p.port, "/Presets", timeout=8)
        if raw.status == 200 and b"<preset " in raw.body:
            run.facts.setdefault("preset_player", p.label)
        raw = http_call(p.host, p.port, "/Services", timeout=10)
        if raw.status == 200:
            names = re.findall(r'<service\b[^>]*\bname="([^"]+)"', raw.body.decode("utf-8", "replace"))
            if names:
                run.facts.setdefault("services", sorted(set(names)))
    run.note("env", "harvested facts for later suites",
             json.dumps({k: v for k, v in run.facts.items() if k != "capabilities"},
                        ensure_ascii=False)[:2000])
    detect_capabilities(run)


def suite_transport(run: Runner) -> None:
    """Routing, methods, headers, encoding. All against read-only endpoints."""
    run.current_suite = "transport"
    run.banner("transport -- routing, methods, headers, encoding")
    ps = run.targets()
    if not ps:
        return
    a = ps[0]

    # -- path case sensitivity. This is a property of one HTTP router in one
    #    firmware build, so it cannot vary between players running the same
    #    build. Full set on the first player; a two-path spot check on the next
    #    few, which is enough to catch a fleet running mixed firmware.
    for path, expect in (("/Status", "status=200"), ("/status", "status=404"),
                         ("/STATUS", "status=404"), ("/SyncStatus", "status=200"),
                         ("/syncstatus", "status=404"), ("/services", "status=404"),
                         ("/Services", "status=200")):
        run.call(a, path, note="path case sensitivity", spec_ref="1.6",
                 expect=expect, save=False)
    for p in ps[1:run.opts.breadth]:
        for path, expect in (("/status", "status=404"), ("/Status", "status=200")):
            run.call(p, path, note="case sensitivity spot check on a second player",
                     spec_ref="1.6", expect=expect, save=False)

    # -- unknown path shape, on all three ports
    for port, expect in ((CONTROL_PORT, "status=404"), (SETTINGS_PORT, "status=404"),
                         (WEB_PORT, "status=404")):
        run.call(a, "/NoSuchEndpointXyz", port=port,
                 note="unknown path: 404 shape and content-type per port", spec_ref="0.1",
                 expect=expect)

    # -- trailing slash, double slash, dot segments
    # Kept because a URL builder that emits a trailing or doubled slash will
    # meet these. Dropped: /./Status and /Status%20, which no client produces.
    for path in ("/Status/", "//Status", "/Status?", "/Status?&", "/Status?timeout=0"):
        run.call(a, path, note="path/query normalisation", spec_ref="1.7", save=False)

    # -- unknown and duplicated parameters
    run.call(a, "/Status?nosuchparam=1", note="unknown parameter is ignored?", spec_ref="1.7", save=False)
    run.call(a, "/Status?timeout=1&timeout=2", note="duplicated parameter: first or last wins?",
             spec_ref="1.7", save=False, timeout=15)
    run.call(a, "/Status?timeout=", note="blank value (client drops these; does the device?)",
             spec_ref="1.7", save=False)

    # -- methods
    # HEAD, OPTIONS and POST are methods a real client or a browser will send.
    # PUT and DELETE are not, and their answer changes nothing.
    for method, expect in (("HEAD", ""), ("OPTIONS", ""), ("POST", "")):
        run.call(a, "/Status", method=method, note="method handling on a GET endpoint",
                 spec_ref="1.2", expect=expect, save=False)

    # -- CORS preflight, which decides whether a browser client can talk direct
    run.call(a, "/Status", method="OPTIONS",
             headers={"Origin": "http://example.invalid",
                      "Access-Control-Request-Method": "GET"},
             note="CORS preflight on the control port", spec_ref="9", save=False)
    run.call(a, "/Status", headers={"Origin": "http://example.invalid"},
             note="CORS: simple GET with an Origin header", spec_ref="9", save=False)

    # -- do the X-Sovi-* schema headers change anything? (spec 1.4 says they may)
    with_h = run.call(a, "/Status", note="with X-Sovi-* schema headers", spec_ref="1.4")
    without_h = run.call(a, "/Status", sovi_headers=False,
                         note="without X-Sovi-* schema headers", spec_ref="1.4")
    sv_with = run.call(a, "/Services", note="/Services with schema headers",
                       spec_ref="1.4", save=False, quiet=True)
    sv_without = run.call(a, "/Services", sovi_headers=False,
                          note="/Services without schema headers", spec_ref="1.4",
                          save=False, quiet=True)
    # /Status carries <secs>, which moves during playback, so comparing two
    # /Status bodies reports a change caused by the clock. /Services is static,
    # so it is the only sound comparison here. Two failed calls both digest to
    # "" and used to read as "no change".
    usable = all(pr.status == 200 and pr.body_sha256
                 for pr in (sv_with, sv_without))
    same = (with_h.body_sha256 == without_h.body_sha256)
    svc_same = (sv_with.body_sha256 == sv_without.body_sha256)
    if not usable:
        run.note("transport",
                 "C-21: could not compare /Services with and without the schema headers",
                 "one or both calls did not return a body, so no verdict is recorded",
                 claim="C-21-schema-headers", claim_verdict="INCONCLUSIVE")
    run.note("transport",
             "omitting the X-Sovi-* headers changes /Services: %s" % ("no" if svc_same else "YES"),
             "with=%s without=%s (digests are of the redacted bodies, which is a valid "
             "comparison because redaction is deterministic)"
             % (sv_with.body_sha256[:12], sv_without.body_sha256[:12]),
             claim="C-21-schema-headers",
             claim_verdict=("" if not usable else
                            ("DISCONFIRMED" if svc_same else "CONFIRMED")))
    run.note("transport",
             "schema-version headers change the response body: %s" % ("no" if same else "YES"),
             "with=%s without=%s" % (with_h.body_sha256[:12], without_h.body_sha256[:12]),
             verdict="OK" if same else "UNEXPECTED")

    # -- schema header sweep on a schema-sensitive endpoint
    # Spot check only: the full sweep lives in the settings suite, which is
    # where schemaVersion actually gates content.
    for sv in ("25", "99"):
        run.call(a, "/Services", headers={"X-Sovi-Schema-Version": sv},
                 note="X-Sovi-Schema-Version=%s gating of /Services" % sv,
                 spec_ref="11.2", save=False)

    # -- Accept-Encoding: is gzip offered?
    run.call(a, "/Services", headers={"Accept-Encoding": "gzip, deflate"},
             note="does the device compress? (matters for /Services at ~62 KB)",
             spec_ref="1.5", save=False)

    # -- connection reuse
    run.call(a, "/Status", headers={"Connection": "close"}, note="Connection: close honoured",
             spec_ref="1.3", save=False)


def suite_ports(run: Runner) -> None:
    """Which of the three ports serves what. Read-only paths only."""
    run.current_suite = "ports"
    run.banner("ports -- endpoint x port matrix (80 / 11000 / 11001)")
    ps = run.targets()
    if not ps:
        return
    a = ps[0]

    read_paths = [
        ("/Status", SAFETY_READ), ("/SyncStatus", SAFETY_READ), ("/Services", SAFETY_READ),
        ("/GitVersion", SAFETY_READ), ("/Presets", SAFETY_READ), ("/Playlist", SAFETY_READ),
        ("/Volume", SAFETY_READ), ("/Name", SAFETY_READ), ("/Alarms", SAFETY_READ),
        ("/Sources", SAFETY_READ), ("/RadioPresets", SAFETY_READ),
        ("/Browse", SAFETY_READ), ("/Shares", SAFETY_READ), ("/diagnostics", SAFETY_READ),
        ("/ui/Configuration", SAFETY_READ), ("/Settings?schemaVersion=35", SAFETY_READ),
        ("/GetSettings", SAFETY_READ),
        # believed-harmless unknowns, no parameters
        ("/audiomodes", SAFETY_PROBE), ("/proxyToSlave", SAFETY_PROBE),
        ("/Info", SAFETY_PROBE), ("/Version", SAFETY_PROBE),
        # deliberately NOT probed bare: /Preset and /SlaveVolume could act on a
        # default target, /SetMaster and /Standalone leave a group, /Sleep
        # cycles the timer, /Reindex and /upgrade start long jobs.
    ]
    already_on_11000 = {"/Status", "/SyncStatus", "/Services", "/GitVersion", "/Presets",
                        "/Playlist", "/Volume", "/Name", "/Alarms"}
    for path, safety in read_paths:
        for port in (CONTROL_PORT, SETTINGS_PORT, WEB_PORT):
            if port == CONTROL_PORT and path in already_on_11000:
                continue          # the env suite already captured these
            run.call(a, path, port=port, safety=safety, save=(port == CONTROL_PORT),
                     note="port matrix", spec_ref="10.3;13", timeout=12)

    # -- speculative: does anything enumerate other players? (open question 7)
    run.banner("ports -- speculative player-enumeration paths")
    # Only names with some grounding: /Zones and /Groups appear in CI-series
    # vocabulary, /Players and /Devices in adjacent vendor APIs. /Fleet, /Hub,
    # /Topology, /Rooms and friends were invention on my part and are dropped --
    # guessing endpoint names is not a test, it is a lottery.
    # /ExternalSource appears in the official desktop Controller's own code
    # (ExternalSource?id=<chassisInputId|changeDirection>) and in no version of
    # the published API document. Existence probe only.
    for path in ("/ExternalSource", "/Players", "/Devices", "/Zones", "/Groups"):
        run.call(a, path, safety=SAFETY_PROBE, note="does this path exist at all?",
                 spec_ref="16.7", expect="status=404", save=False,
                 claim="C-24-player-enumeration", claim_confirm="status=200",
                 claim_disconfirm="status=404")

    # -- the /ui surface below /ui/Configuration
    raw = http_call(a.host, CONTROL_PORT, "/ui/Configuration", timeout=10)
    if raw.status == 200:
        uris = re.findall(r'URI="([^"]+)"', raw.body.decode("utf-8", "replace"))
        run.note("ports", "/ui/Configuration advertises %d URIs" % len(uris),
                 ", ".join(uris[:20]))
        # Only paths under /ui, with no query the device attached. Calling
        # device-supplied URIs verbatim meant a read-only run issued requests
        # with whatever parameters happened to be in them.
        safe_uris, skipped = [], []
        for uri in uris:
            path = uri if uri.startswith("/") else "/" + uri
            base = path.split("?")[0]
            if base.startswith("/ui/") and "?" not in path:
                safe_uris.append(base)
            else:
                skipped.append(path)
        for path in safe_uris[:12]:
            run.call(a, path, safety=SAFETY_PROBE, note="server-driven UI surface",
                     spec_ref="10.2", timeout=12)
        if skipped:
            run.note("ports", "%d advertised URI(s) not called" % len(skipped),
                     "Outside /ui or carrying device-supplied parameters, so not called "
                     "in a read-only run: %s" % ", ".join(sorted(set(skipped))[:20]))


def suite_longpoll(run: Runner) -> None:
    """etag semantics, which endpoints hold, timeout ceiling, concurrency."""
    run.current_suite = "longpoll"
    run.banner("longpoll -- etag semantics and connection holding")
    ps = run.targets()
    if not ps:
        return
    a = ps[0]

    def live_etag(path: str) -> str:
        raw = http_call(a.host, a.port, path, timeout=10)
        if raw.status != 200:
            return ""
        return root_attrs(raw.body.decode("utf-8", "replace")).get("etag", "")

    # -- which endpoints actually honour etag+timeout?
    candidates = ["/Status", "/SyncStatus", "/BTDevices", "/Playlist", "/Presets",
                  "/Services", "/Alarms", "/Volume"]
    for path in candidates:
        etag = live_etag(path)
        if not etag:
            run.note("longpoll", "%s: no etag attribute in the response" % path,
                     "cannot long-poll this endpoint by the documented convention")
            continue
        pr = run.call(a, "%s?etag=%s&timeout=4" % (path, urllib.parse.quote(etag, safe="")),
                      note="does %s hold the connection with a live etag?" % path,
                      spec_ref="1.9", timeout=20, save=False)
        held = (pr.elapsed_ms or 0) > 3000
        run.note("longpoll", "%s long-poll: %s" % (path, "HELD ~%.1fs" % ((pr.elapsed_ms or 0) / 1000.0) if held else "returned immediately"),
                 "etag length %d, elapsed %sms" % (len(etag), pr.elapsed_ms),
                 verdict="OK")

    # -- stale / invented / malformed etags all return immediately (spec 1.9)
    for bogus in ("bogus-etag-value", "0", "", "%20", "1" * 200):
        run.call(a, "/Status?etag=%s&timeout=5" % bogus,
                 note="stale/invalid etag must return immediately", spec_ref="1.9",
                 timeout=20, save=False)

    # -- is the timeout parameter capped, and what does an odd value do?
    etag = live_etag("/Status")
    if etag:
        q = urllib.parse.quote(etag, safe="")
        for tv in ("1", "5"):
            run.call(a, "/Status?etag=%s&timeout=%s" % (q, tv),
                     note="timeout=%s: does the hold match the request?" % tv,
                     spec_ref="1.9", timeout=30, save=False)
        for tv in ("-1", "abc", "0"):
            run.call(a, "/Status?etag=%s&timeout=%s" % (q, tv),
                     note="malformed timeout=%s" % tv, spec_ref="1.9",
                     timeout=25, save=False)
        if run.opts.slow:
            for tv in ("100", "120", "300"):
                pr = run.call(a, "/Status?etag=%s&timeout=%s" % (q, tv),
                              note="is timeout capped at %s?" % tv, spec_ref="1.9",
                              timeout=int(tv) + 30, save=False)
                run.note("longpoll", "requested timeout=%s, held %.1fs" % (tv, (pr.elapsed_ms or 0) / 1000.0))

    # -- concurrency ladder (T-1): how many held long-polls does a player take?
    ladder = [n for n in (8, 24, 32, 48, 64, 96) if n <= run.opts.concurrency_max]
    if not ladder:
        run.note("longpoll", "concurrency ladder skipped (--concurrency-max 0)",
                 "The ceiling on simultaneous long-polls stays unmeasured.")
    for n in ladder:
        etag = live_etag("/Status")
        if not etag:
            break
        q = urllib.parse.quote(etag, safe="")
        path = "/Status?etag=%s&timeout=8" % q
        started = time.monotonic()
        results: List[Tuple[int, Optional[int], float, str]] = []

        def one(i: int, _path: str = path):
            r = http_call(a.host, a.port, _path, timeout=40)
            return (i, r.status, r.elapsed, r.error)

        with concurrent.futures.ThreadPoolExecutor(max_workers=n) as ex:
            for res in ex.map(one, range(n)):
                results.append(res)
        wall = time.monotonic() - started
        n_held = sum(1 for _, _, el, _ in results if el > 6.0)
        early = sum(1 for _, _, el, _ in results if el <= 6.0)
        failed = sum(1 for _, st, _, err in results if err or st != 200)
        verdict = "OK" if n_held == n else "UNEXPECTED"
        run.note("longpoll",
                 "concurrency %d: %d held ~8s, %d returned early, %d failed (wall %.1fs)"
                 % (n, n_held, early, failed, wall),
                 "\n".join("  #%02d status=%s elapsed=%.2fs %s" % (i, st, el, err)
                           for i, st, el, err in sorted(results)),
                 verdict=verdict,
                 extra={"concurrency": n, "held": n_held, "early": early, "failed": failed})
        print("  -   concurrency %d -> %d held, %d early, %d failed" % (n, n_held, early, failed))
        if n_held < n:
            break

    # -- does a state change release a held connection? (read-only version:
    #    hold from two clients and confirm both release together on timeout)
    etag = live_etag("/SyncStatus")
    if etag:
        q = urllib.parse.quote(etag, safe="")
        path = "/SyncStatus?etag=%s&timeout=5" % q
        with concurrent.futures.ThreadPoolExecutor(max_workers=2) as ex:
            futs = [ex.submit(http_call, a.host, a.port, path, timeout=25) for _ in range(2)]
            rs = [f.result() for f in futs]
        run.note("longpoll", "two simultaneous /SyncStatus holds released together",
                 "elapsed: %s" % ", ".join("%.2fs" % r.elapsed for r in rs))


def suite_errors(run: Runner) -> None:
    """What failure looks like. Which convention, which content type."""
    run.current_suite = "errors"
    run.banner("errors -- failure shapes across endpoints")
    ps = run.targets()
    if not ps:
        return
    a = ps[0]

    cases = [
        ("/Songs?service=NoSuchService", "unknown service on a typed browse endpoint", "8.1"),
        ("/Songs", "typed browse endpoint with no service at all", "8.1"),
        ("/Albums?service=NoSuchService", "unknown service", "8.1"),
        ("/Browse?key=NoSuchService%3A", "unknown browse key", "15.1"),
        ("/Browse?key=", "empty browse key", "15.1"),
        ("/Search?service=LocalMusic", "search with no expression", "11.10"),
        ("/Search?expr=", "search with empty expression", "11.10"),
        ("/Artwork", "artwork with no parameters", "9"),
        ("/Artwork?service=NoSuchService&songid=1", "artwork for an unknown service", "9"),
        ("/RadioBrowse?service=NoSuchService", "radio browse, unknown service", "8.1"),
        ("/Settings?id=nosuchpage&schemaVersion=35", "unknown settings page", "10.3"),
        ("/Services?schemaVersion=abc", "malformed schemaVersion", "11.2"),
        ("/Status?timeout=notanumber", "malformed timeout", "1.9"),
    ]
    for path, note, ref in cases:
        run.call(a, path, note=note, spec_ref=ref, timeout=15)

    # same on the settings port, where the router is a different server
    run.call(a, "/Settings?id=nosuchpage&schemaVersion=35", port=SETTINGS_PORT,
             note="unknown settings page, direct on 11001", spec_ref="10.3")

    run.note("errors", "reading guide",
             "Compare: bare 404 text/plain (Go net/http, unknown path) vs "
             "<error type=...> envelope (endpoint exists, refused) vs flat "
             "<error>text</error> vs raw HTML. Spec 0.1 and 11.1.")


def suite_claims(run: Runner) -> None:
    """Every read-only [T] claim from spec section 17, retested as its source
    describes it -- including the port it names."""
    run.current_suite = "claims"
    run.banner("claims -- third-party [T] register, read-only entries")
    ps = run.targets()
    if not ps:
        return
    a = ps[0]

    # /diagnostics: confirmed on port 80 only, and the claim that was nearly lost
    # to a mis-aimed test. Two players is enough to catch a model difference.
    for p in ps[:max(2, run.opts.breadth)]:
        run.call(p, "/diagnostics", port=WEB_PORT, note="[T blutui-rs] /diagnostics on port 80",
                 spec_ref="13;17", expect="status=200", timeout=20,
                 claim="C-01-diagnostics-80", claim_confirm="status=200")
        run.call(p, "/diagnostics", port=CONTROL_PORT, note="/diagnostics on 11000 (expected 404)",
                 spec_ref="13;17", expect="status=404", save=False,
                 claim="C-02-diagnostics-11000", claim_confirm="status=404",
                 claim_disconfirm="status=200")

    # /audiomodes as a read (T-32, BluShell, schema 25 sample)
    for p in ps[:run.opts.breadth]:
        run.call(p, "/audiomodes", safety=SAFETY_PROBE,
                 note="[T BluShell] bare GET /audiomodes returns <audiomode>",
                 spec_ref="10.4;17", timeout=15,
                 claim="C-03-audiomodes-read", claim_confirm="status=200;root=audiomode")

    # /GetSettings (was 404 on 4.16.22 -- confirm it is still absent)
    for p in ps[:run.opts.breadth]:
        run.call(p, "/GetSettings", note="[V] /GetSettings absent on current firmware",
                 spec_ref="10.1", expect="status=404", save=False,
                 claim="C-06-getsettings", claim_confirm="status=200;kind=json")
        run.call(p, "/GetSettings", port=SETTINGS_PORT, note="/GetSettings on the settings port",
                 spec_ref="10.1", save=False)

    # /Shares on port 80 (and does it answer on 11000 yet?)
    for p in ps[:run.opts.breadth]:
        run.call(p, "/Shares", port=WEB_PORT, note="share config, read only",
                 spec_ref="13", expect="status=200")
        run.call(p, "/Shares", port=CONTROL_PORT, note="has /Shares migrated to 11000?",
                 spec_ref="13", save=False,
                 claim="C-16-shares-11000", claim_confirm="status=200;root=shares")

    # /proxyToSlave existence, no parameters, so nothing can be relayed
    run.call(a, "/proxyToSlave", safety=SAFETY_PROBE,
             note="[T blutui-rs] does /proxyToSlave exist? (no params, nothing relayed)",
             spec_ref="10.0;17", claim="C-04-proxytoslave",
             claim_confirm="status=200|400|500")

    # legacy /Sync: existence only. NOT called with slave=/remove=, which would group.
    run.call(a, "/Sync", safety=SAFETY_PROBE,
             note="[T bluos-dashboard] does the legacy /Sync path exist? (no params)",
             spec_ref="5.2;17", claim="C-05-sync-legacy",
             claim_confirm="status=200|400|500")

    # /RadioPresets item attributes: total_count, key, is_active, guide_id, preset_id, subtext
    services = run.facts.get("services") or ["TuneIn", "Capture", "RadioParadise"]
    for svc in services:
        if svc in ("TuneIn", "RadioParadise", "Capture", "Airable"):
            run.call(a, "/RadioPresets?service=%s" % urllib.parse.quote(svc),
                     note="[T Blu4Net/BluShell] radio item attributes for %s" % svc,
                     spec_ref="11.10;17", timeout=20, claim="C-11-radio-attrs",
                     claim_confirm="status=200;contains=is_active",
                     claim_disconfirm="status=200;absent=is_active")
            run.call(a, "/RadioBrowse?service=%s" % urllib.parse.quote(svc),
                     note="[T] total_count / key / is_active on <radiotime> items",
                     spec_ref="11.10;17", timeout=20, claim="C-12-radio-totalcount",
                     claim_confirm="status=200;contains=total_count",
                     claim_disconfirm="status=200;absent=total_count")

    # /Search container shape (BluShell sample, schema 25)
    for svc in ("LocalMusic", "Tidal"):
        if not services or svc in services:
            run.call(a, "/Search?service=%s&expr=a" % svc,
                     note="[T BluShell] /Search container shape for %s" % svc,
                     spec_ref="11.10;17", timeout=25, claim="C-13-search-containers",
                     claim_confirm="status=200;root=search",
                     claim_disconfirm="status=404")

    # album-scoped /Songs wrapper and <discno>n/m</discno> (BluShepherd, 2016)
    raw = http_call(a.host, a.port, "/Albums?service=LocalMusic", timeout=20)
    if raw.status == 200:
        text = raw.body.decode("utf-8", "replace")
        m = re.search(r'<album\b[^>]*\bname="([^"]+)"[^>]*\bartist="([^"]+)"', text)
        if not m:
            m = re.search(r"<album>([^<]+)</album>\s*<artist>([^<]+)</artist>", text)
        if m:
            album, artist = m.group(1), m.group(2)
            run.call(a, "/Songs?service=LocalMusic&album=%s&artist=%s"
                     % (urllib.parse.quote(album), urllib.parse.quote(artist)),
                     note="[T BluShepherd] album-scoped /Songs: nested <song> in <album>? <discno>?",
                     spec_ref="11.10;17", timeout=25, claim="C-14-songs-album-wrapper",
                     claim_confirm="status=200;contains=<discno>",
                     claim_disconfirm="status=200;absent=<discno>")
        else:
            run.note("claims", "no local album found to test the album-scoped /Songs wrapper",
                     "requires a LocalMusic library with at least one album")

    # <is_preset> in /Status (T-22): read-only half only. Recalling a preset is
    # a state change and belongs to round 2 -- but if a preset is already
    # playing, the field is observable now.
    pl = run.facts.get("preset_player")
    if pl and run.player(pl):
        run.call(run.player(pl), "/Status",
                 note="[T Blu4Net] <is_preset>/<preset_name> in /Status "
                      "(read-only; recall itself is a round-2 test)",
                 spec_ref="2.2;17", claim="C-17-is-preset",
                 claim_confirm="contains=<is_preset>",
                 claim_disconfirm="status=200;absent=<is_preset>")
    else:
        run.note("claims", "no player with configured presets found",
                 "T-22 needs a player that has presets; none of the probed players returned any")


def suite_artwork(run: Runner) -> None:
    """Artwork: response headers, the no-artwork case, and the by-name form."""
    run.current_suite = "artwork"
    run.banner("artwork -- headers, missing artwork, by-name form")
    ps = run.targets()
    if not ps:
        return
    a = ps[0]

    image = run.facts.get("image")
    songid = run.facts.get("songid")
    service = run.facts.get("service")

    if image and image.startswith("/"):
        path = image
        run.call(a, path, note="[T BluShepherd 2016] artwork headers: CORS? ETag? Cache-Control?",
                        spec_ref="9;17", timeout=20, claim="C-07-artwork-cors",
                        claim_confirm="status=200;header=Access-Control-Allow-Origin",
                        claim_disconfirm="status=200;noheader=Access-Control-Allow-Origin")
        run.call(a, path, method="HEAD",
                 note="[T BluShepherd 2016] artwork sends no ETag and no Last-Modified",
                 spec_ref="9;17", claim="C-08-artwork-noetag",
                 claim_confirm="status=200;noheader=ETag;noheader=Last-Modified",
                 claim_disconfirm="status=200;header=ETag", save=False)
        run.call(a, path + ("&" if "?" in path else "?") + "followRedirects=1",
                 note="followRedirects=1 as the spec advises", spec_ref="9", save=False)
        run.call(a, path, method="HEAD", note="HEAD on artwork (cheap validator check)",
                 spec_ref="9", save=False)
        run.call(a, path, headers={"Origin": "http://example.invalid"},
                 note="artwork with an Origin header: is CORS still open?", spec_ref="9", save=False)
    elif songid and service:
        run.call(a, "/Artwork?service=%s&songid=%s" % (urllib.parse.quote(service),
                                                       urllib.parse.quote(songid)),
                 note="artwork by service+songid", spec_ref="9", timeout=20)
    else:
        run.note("artwork", "no now-playing artwork URL available",
                 "start playback on any player and re-run this suite to test artwork headers")

    # no-artwork case (T-33): XML where an image is expected
    run.call(a, "/Artwork?service=LocalMusic&fn=%2Fdoes%2Fnot%2Fexist.flac",
             note="[T BluShell] <artwork>none found</artwork> -- record the Content-Type",
             spec_ref="9;17", timeout=15, claim="C-09-artwork-nonefound",
             claim_confirm="status=200;root=artwork")
    run.call(a, "/Artwork?service=NoSuchService&albumid=0",
             note="artwork for an unknown service", spec_ref="9", save=False)

    # by-name form (T, 2015/2016)
    # Asking by name for "NoSuchAlbum" can never return artwork, so this always
    # came out DISCONFIRMED regardless of whether the by-name form works. Use a
    # real album if one is known, and record INCONCLUSIVE if none is.
    album = run.facts.get("album")
    artist = run.facts.get("artist")
    if album and artist:
        run.call(a, "/Artwork?service=LocalMusic&album=%s&artist=%s"
                 % (urllib.parse.quote(album), urllib.parse.quote(artist)),
                 note="[T 2015/2016] /Artwork?album=&artist= by name, using a real album",
                 spec_ref="9;17", timeout=15, claim="C-10-artwork-byname",
                 claim_confirm="status=200;kind=binary",
                 claim_disconfirm="status=200;root=artwork")
    else:
        run.note("artwork", "C-10: no real album name available to ask for",
                 "asking for a name that cannot exist would always look like failure, "
                 "whether or not the by-name form works. Play something from the local "
                 "library and re-run this suite.",
                 claim="C-10-artwork-byname", claim_verdict="INCONCLUSIVE")
    run.call(a, "/Artwork?service=LocalMusic&album=NoSuchAlbum&artist=NoSuchArtist",
             note="by-name artwork for an album that does not exist, as a control",
             spec_ref="9", timeout=15, save=False)


def suite_browse(run: Runner) -> None:
    """Bounded, read-only crawl of the browse tree, plus paging/sort/encoding."""
    run.current_suite = "browse"
    run.banner("browse -- bounded crawl, paging, sort, key encoding")
    ps = run.targets()
    if not ps:
        return
    a = ps[0]

    SAFE_PATHS = {"/Browse", "/Songs", "/Albums", "/Artists", "/Genres", "/Composers",
                  "/Folders", "/Playlists", "/RadioBrowse", "/RadioPresets", "/Sources",
                  "/Search", "/Info"}

    def is_safe(url: str) -> bool:
        try:
            parsed = urllib.parse.urlsplit(url)
        except ValueError:
            return False
        if parsed.scheme or parsed.netloc:
            return False
        path = parsed.path
        return path in SAFE_PATHS

    # typed entry points (spec 8.1)
    for path in ("/Browse", "/Sources", "/Playlists", "/RadioPresets"):
        run.call(a, path, note="typed browse entry point", spec_ref="8.1", timeout=25)
    for svc in (run.facts.get("services") or []):
        q = urllib.parse.quote(svc)
        for path in ("/Albums", "/Artists", "/Genres", "/Composers", "/Folders", "/Playlists"):
            run.call(a, "%s?service=%s" % (path, q),
                     note="typed entry point %s for service %s" % (path, svc),
                     spec_ref="8.1", timeout=25, save=False, quiet=True)

    # bounded crawl of /Browse
    seen: set = set()
    queue: List[Tuple[str, int]] = [("/Browse", 0)]
    max_depth = run.opts.browse_depth
    max_nodes = run.opts.browse_nodes
    crawled = 0
    while queue and crawled < max_nodes:
        path, depth = queue.pop(0)
        if path in seen:
            continue
        seen.add(path)
        pr = run.call(a, path, note="browse crawl depth %d" % depth, spec_ref="15.1",
                      timeout=25, quiet=(depth > 0))
        crawled += 1
        if pr.status != 200 or depth >= max_depth:
            continue
        text = body_of(run, pr)
        keys = re.findall(r'browseKey="([^"]+)"', text)
        for k in keys[: run.opts.browse_fanout]:
            child = "/Browse?key=" + urllib.parse.quote(xml_unescape(k), safe="")
            if child not in seen:
                queue.append((child, depth + 1))
        for url in re.findall(r'\burl="([^"]+)"', text)[: run.opts.browse_fanout]:
            url = xml_unescape(url)
            if is_safe(url) and url not in seen:
                queue.append((url, depth + 1))
    run.note("browse", "crawl visited %d nodes (depth<=%d, fanout<=%d)"
             % (crawled, max_depth, run.opts.browse_fanout),
             "\n".join(sorted(seen)[:200]))

    # paging: is the 50-item server cap still there, and what do edges do?
    svc = "Tidal" if "Tidal" in (run.facts.get("services") or []) else "LocalMusic"
    base = "/Songs?service=%s&category=FAVOURITES" % svc
    run.call(a, base + "&start=0&end=999", note="[V] is browse paging capped at 50?",
             spec_ref="8.2", timeout=25, claim="C-22-page-cap-50",
             claim_confirm="contains=start=50", claim_disconfirm="contains=start=999", save=False)
    for extra in ("", "&start=0&end=999", "&start=0&end=49", "&start=50&end=99",
                  "&start=100&end=100", "&start=-1&end=10", "&start=10&end=5",
                  "&start=abc&end=def"):
        run.call(a, base + extra, note="paging: %s" % (extra or "default"),
                 spec_ref="8.2", timeout=25, save=bool(extra in ("", "&start=0&end=999")))

    # sort: valid, and the descending forms nobody has confirmed (T-25)
    for sort in ("name", "recent", "album", "artist", "nosuchsort",
                 "recentDesc", "-recent", "recent:desc", "reverseName"):
        run.call(a, base + "&sort=" + urllib.parse.quote(sort),
                 note="sort=%s: does the root echo it back and does order change?" % sort,
                 spec_ref="8.2;16.12", timeout=25,
                 save=(sort in ("recent", "recentDesc", "-recent")))

    # descending sort: echoing the parameter back is not the same as sorting by it
    def first_item(path: str) -> str:
        r = http_call(a.host, a.port, path, timeout=25)
        t = r.body.decode("utf-8", "replace") if r.body else ""
        m = re.search(r'<(?:song|item|album|art)\b[^>]*\b(?:title|text|name)="([^"]*)"', t)
        return m.group(1) if m else ""

    def list_length(path: str) -> int:
        r = http_call(a.host, a.port, path, timeout=25)
        t = r.body.decode("utf-8", "replace") if r.body else ""
        return len(re.findall(r"<(?:song|item|album|art)\b", t))

    asc = first_item(base + "&sort=recent")
    n_items = list_length(base + "&sort=recent")
    if not asc or n_items < 2:
        run.note("browse",
                 "C-18: cannot test descending sort against a list of %d item(s)" % n_items,
                 "an empty or single-item list gives the same first item under every sort "
                 "order, so 'unchanged' would say nothing. Point this at a service with a "
                 "populated list to decide the claim.",
                 claim="C-18-sort-descending", claim_verdict="INCONCLUSIVE")
    else:
        for cand in ("recentDesc", "-recent", "recent:desc"):
            got = first_item(base + "&sort=" + urllib.parse.quote(cand))
            if not got:
                run.note("browse", "sort=%s: no first item came back" % cand,
                         "the request failed or returned nothing, so no verdict",
                         claim="C-18-sort-descending", claim_verdict="INCONCLUSIVE")
                continue
            changed = asc != got
            run.note("browse",
                     "sort=%s: first item %s" % (cand, "CHANGED (order really differs)"
                                                 if changed else "unchanged"),
                     "ascending first item vs %s first item across %d items -- if unchanged, "
                     "the parameter is accepted but ignored, and descending must be done "
                     "client-side after paging the whole list" % (cand, n_items),
                     claim="C-18-sort-descending",
                     claim_verdict="CONFIRMED" if changed else "DISCONFIRMED")

    # browse key encoding: the silent-failure case worth keeping documented
    if svc == "Tidal":
        good = "Tidal:Song/%2FSongs%3Fcategory=FAVOURITES%26service=Tidal"
        bad = "Tidal:Song/%2FSongs%3Fcategory=FAVOURITES&amp;service=Tidal"
        run.call(a, "/Browse?key=" + urllib.parse.quote(good, safe=""),
                 note="browse key with %26 for the inner ampersand (correct)",
                 spec_ref="15.1", timeout=25)
        run.call(a, "/Browse?key=" + urllib.parse.quote(bad, safe=""),
                 note="browse key with &amp; instead (silent empty result)",
                 spec_ref="15.1", timeout=25)

    # /Browse with and without sid, since sid was reported as required
    run.call(a, "/Browse?sid=0", note="does /Browse accept a bogus sid?", spec_ref="15.1",
             timeout=20, save=False, claim="C-20-browse-sid",
             claim_confirm="status=404|400", claim_disconfirm="status=200")


def suite_settings(run: Runner) -> None:
    """The 11001 settings surface, read only, with a schemaVersion sweep."""
    run.current_suite = "settings"
    run.banner("settings -- port 11001 tree and schemaVersion gating")
    ps = run.targets()
    if not ps:
        return

    for p in ps:
        run.call(p, "/Settings?schemaVersion=35", port=CONTROL_PORT,
                 note="redirect from 11000 to 11001 (do NOT follow automatically)",
                 spec_ref="10.3", expect="status=301|302|307|308", save=False)
        run.call(p, "/Settings?schemaVersion=35", port=SETTINGS_PORT,
                 note="whole settings tree", spec_ref="10.3", timeout=25)

    a = ps[0]
    for sv in ("0", "15", "25", "28", "34", "35", "36", "40", "99"):
        run.call(a, "/Settings?schemaVersion=%s" % sv, port=SETTINGS_PORT,
                 note="schemaVersion=%s: what appears and disappears" % sv,
                 spec_ref="10.3", timeout=25, save=(sv in ("25", "35", "99")))
    run.call(a, "/Settings", port=SETTINGS_PORT, note="no schemaVersion at all",
             spec_ref="10.3", timeout=25)

    for page in ("audio", "capture", "player", "library", "alarms", "sleep",
                 "network", "managePlaylists", "bluetooth", "upgrade", "about"):
        run.call(a, "/Settings?id=%s&schemaVersion=35" % page, port=SETTINGS_PORT,
                 note="settings page: %s" % page, spec_ref="10.3", timeout=25,
                 quiet=page not in ("audio", "capture", "player"))

    # port 11001 serves settings only -- confirm on this firmware
    for path in ("/Status", "/SyncStatus", "/Shares", "/ui/Configuration", "/Services"):
        run.call(a, path, port=SETTINGS_PORT, note="does 11001 serve anything but settings?",
                 spec_ref="10.3", expect="status=404", save=False,
                 claim="C-23-11001-settings-only", claim_confirm="status=404",
                 claim_disconfirm="status=200")


def suite_stability(run: Runner) -> None:
    """Repeatability: what is stable across calls, players and time."""
    run.current_suite = "stability"
    run.banner("stability -- repeatability and cross-player consistency")
    ps = run.targets()
    if not ps:
        return

    # /Services: identical across calls on one player? across players?
    digests: Dict[str, List[str]] = {}
    for p in ps:
        for i in range(2):
            pr = run.call(p, "/Services", note="repeatability pass %d" % (i + 1),
                          spec_ref="11.2", timeout=25, save=False, quiet=True)
            digests.setdefault(p.label, []).append(pr.body_sha256)
    for label, ds in digests.items():
        stable = len(set(ds)) == 1
        run.note("stability", "/Services on %s is byte-stable across calls: %s"
                 % (label, "yes" if stable else "NO"), " ".join(d[:12] for d in ds),
                 verdict="OK" if stable else "UNEXPECTED")
    across = {ds[0] for ds in digests.values()}
    run.note("stability", "/Services is byte-identical across players: %s"
             % ("yes" if len(across) <= 1 else "no (expected: sid and ordering differ)"),
             "; ".join("%s=%s" % (k, v[0][:12]) for k, v in digests.items()))

    # etag churn while nothing is happening
    a = ps[0]
    etags = []
    for _ in range(3):
        raw = http_call(a.host, a.port, "/Status", timeout=10)
        etags.append(root_attrs(raw.body.decode("utf-8", "replace")).get("etag", "")
                     if raw.body else "")
        time.sleep(1.5)
    run.note("stability", "/Status etag over 3 idle reads: %s"
             % ("stable" if len(set(etags)) == 1 else "CHANGED"),
             " ".join(e[:16] for e in etags))

    # /SyncStatus etag is numeric, /Status is a hash -- record both shapes
    raw = http_call(a.host, a.port, "/SyncStatus", timeout=10)
    attrs = root_attrs(raw.body.decode("utf-8", "replace")) if raw.body else {}
    if "etag" in attrs and "syncStat" in attrs:
        run.note("stability", "/SyncStatus etag=%s syncStat=%s (numeric, and equal?)"
                 % (attrs["etag"], attrs["syncStat"]),
                 "equal: %s -- if these are always equal, a client needs to track only one"
                 % (attrs["etag"] == attrs["syncStat"]))


# --------------------------------------------------------------------------
# LSDP (UDP 11430)
# --------------------------------------------------------------------------

LSDP_HEADER = b"\x06LSDP\x01"


def lsdp_query_packet(msg_type: int = 0x51, classes: Sequence[int] = (0xFFFF,)) -> bytes:
    body = bytes([msg_type, len(classes)]) + b"".join(struct.pack(">H", c) for c in classes)
    return LSDP_HEADER + bytes([len(body) + 1]) + body


def lsdp_parse(data: bytes) -> Dict[str, Any]:
    """Parse one LSDP datagram. Length-prefixed throughout, so unknown message
    types are skipped rather than aborting the parse."""
    out: Dict[str, Any] = {"messages": [], "raw_hex": binascii.hexlify(data).decode()}
    if len(data) < 6 or data[1:5] != b"LSDP":
        out["error"] = "not an LSDP packet"
        return out
    hlen = data[0]
    out["version"] = data[5]
    i = hlen
    while i < len(data):
        mlen = data[i]
        if mlen == 0 or i + mlen > len(data):
            out["error"] = "truncated message at offset %d" % i
            break
        msg = data[i + 1:i + mlen]
        i += mlen
        if not msg:
            continue
        mtype = chr(msg[0])
        entry: Dict[str, Any] = {"type": mtype}
        try:
            if mtype in ("Q", "R"):
                count = msg[1]
                entry["classes"] = [struct.unpack(">H", msg[2 + 2 * k:4 + 2 * k])[0] for k in range(count)]
            elif mtype == "D":
                p = 1
                nlen = msg[p]; p += 1
                entry["node_id"] = binascii.hexlify(msg[p:p + nlen]).decode(); p += nlen
                count = msg[p]; p += 1
                entry["classes"] = [struct.unpack(">H", msg[p + 2 * k:p + 2 + 2 * k])[0] for k in range(count)]
            elif mtype == "A":
                p = 1
                nlen = msg[p]; p += 1
                entry["node_id"] = binascii.hexlify(msg[p:p + nlen]).decode(); p += nlen
                alen = msg[p]; p += 1
                addr = msg[p:p + alen]; p += alen
                entry["address_len"] = alen
                entry["address"] = ".".join(str(b) for b in addr) if alen == 4 else binascii.hexlify(addr).decode()
                count = msg[p]; p += 1
                records = []
                for _ in range(count):
                    cls = struct.unpack(">H", msg[p:p + 2])[0]; p += 2
                    txtn = msg[p]; p += 1
                    txt = {}
                    for _ in range(txtn):
                        klen = msg[p]; p += 1
                        key = msg[p:p + klen].decode("utf-8", "replace"); p += klen
                        vlen = msg[p]; p += 1
                        val = msg[p:p + vlen].decode("utf-8", "replace"); p += vlen
                        txt[key] = val
                    records.append({"class": "0x%04X" % cls, "txt": txt})
                entry["records"] = records
            else:
                entry["unhandled"] = binascii.hexlify(msg).decode()
        except (IndexError, struct.error) as exc:
            entry["parse_error"] = str(exc)
        out["messages"].append(entry)
    return out


LSDP_QUERY_TIMES = (0.0, 1.0, 2.0, 3.0, 5.0, 7.0, 10.0)
LSDP_PLAYER_CLASSES = frozenset(("0x0001", "0x0003", "0x0006", "0x0008"))


def lsdp_broadcast_targets() -> List[str]:
    """IPv4 subnet-directed broadcasts, plus limited broadcast as a fallback.

    The shipping clients send on every usable IPv4 interface.  Python's standard
    library has no portable getifaddrs(), so Linux/other fcntl platforms get the
    real interface netmasks here; other platforms still retain 255.255.255.255.
    """
    targets: List[str] = []
    try:
        import fcntl  # POSIX; intentionally optional
        probe = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            for _idx, ifname in socket.if_nameindex():
                req = struct.pack("256s", ifname.encode("utf-8")[:15])
                try:
                    flags_raw = fcntl.ioctl(probe.fileno(), 0x8913, req)  # SIOCGIFFLAGS
                    flags = struct.unpack("H", flags_raw[16:18])[0]
                    if not (flags & 0x1) or not (flags & 0x2) or (flags & 0x8):
                        continue  # down, no broadcast, or loopback
                    addr = socket.inet_ntoa(
                        fcntl.ioctl(probe.fileno(), 0x8915, req)[20:24])  # SIOCGIFADDR
                    mask = socket.inet_ntoa(
                        fcntl.ioctl(probe.fileno(), 0x891B, req)[20:24])  # SIOCGIFNETMASK
                    net = ipaddress.IPv4Network("%s/%s" % (addr, mask), strict=False)
                    if net.prefixlen >= 31:
                        continue
                    bcast = str(net.broadcast_address)
                    if bcast not in targets:
                        targets.append(bcast)
                except (OSError, ValueError, struct.error):
                    continue
        finally:
            probe.close()
    except (ImportError, AttributeError, OSError):
        pass

    if "255.255.255.255" not in targets:
        targets.append("255.255.255.255")
    return targets


def lsdp_collect(dest: Any, packet: bytes, listen_secs: float = 3.0,
                 broadcast: bool = False, bind_port: int = 0,
                 send_times: Sequence[float] = (0.0,)) -> List[Tuple[str, bytes]]:
    """Send an LSDP packet and collect datagrams on the same socket.

    `dest` may be one address or several.  `send_times` are seconds from socket
    start, allowing the protocol's redundant 0/1/2/3/5/7/10 s query burst.
    """
    replies: List[Tuple[str, bytes]] = []
    destinations = [dest] if isinstance(dest, str) else list(dest)
    schedule = sorted(float(t) for t in (send_times or (0.0,)) if float(t) >= 0)
    if not destinations:
        return replies

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        if broadcast:
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        sock.bind(("0.0.0.0", bind_port))

        started = time.monotonic()
        deadline = started + max(0.0, listen_secs)
        next_send = 0
        last_send_error: Optional[OSError] = None
        sends_ok = 0

        while time.monotonic() < deadline:
            now = time.monotonic()
            elapsed = now - started
            while next_send < len(schedule) and elapsed >= schedule[next_send]:
                this_round_ok = 0
                for target in destinations:
                    try:
                        sock.sendto(packet, (target, LSDP_PORT))
                        sends_ok += 1
                        this_round_ok += 1
                    except OSError as exc:
                        last_send_error = exc
                next_send += 1
                if this_round_ok == 0 and sends_ok == 0 and next_send >= len(schedule):
                    if last_send_error:
                        raise last_send_error
                now = time.monotonic()
                elapsed = now - started

            until_deadline = max(0.0, deadline - time.monotonic())
            if next_send < len(schedule):
                until_send = max(0.0, started + schedule[next_send] - time.monotonic())
                wait = min(0.25, until_deadline, until_send)
            else:
                wait = min(0.25, until_deadline)
            if wait <= 0:
                continue
            sock.settimeout(wait)
            try:
                data, addr = sock.recvfrom(4096)
            except socket.timeout:
                continue
            except OSError:
                break
            replies.append((addr[0], data))

        if sends_ok == 0 and last_send_error:
            raise last_send_error
    finally:
        sock.close()
    return replies


def _lsdp_players(replies: Sequence[Tuple[str, bytes]]) -> List[Tuple[str, str, int]]:
    """Extract unique (address, name, port) player services from Announces."""
    out: Dict[Tuple[str, int], Tuple[str, str, int]] = {}
    for src, data in replies:
        parsed = lsdp_parse(data)
        for msg in parsed.get("messages", []):
            if msg.get("type") != "A" or msg.get("address_len") != 4:
                continue
            addr = msg.get("address") or src
            for rec in msg.get("records", []):
                if rec.get("class") not in LSDP_PLAYER_CLASSES:
                    continue
                txt = rec.get("txt", {})
                try:
                    port = int(txt.get("port", CONTROL_PORT))
                except (TypeError, ValueError):
                    port = CONTROL_PORT
                # CI580 secondary nodes can share one IP, so host alone is not
                # a unique discovery key.  Preserve every advertised port.
                out[(addr, port)] = (addr, txt.get("name", ""), port)
    return sorted(out.values(), key=lambda x: (ipaddress.IPv4Address(x[0]), x[2]))


def suite_discovery(run: Runner) -> List[Tuple[str, str, int]]:
    """LSDP broadcast query, plus the untested unicast R form (T-26)."""
    run.current_suite = "discovery"
    run.banner("discovery -- LSDP on UDP 11430")
    found: List[Tuple[str, str, int]] = []
    unicast_q_answered: Dict[str, bool] = {}

    def record(title: str, dest: Any, packet: bytes, replies: List[Tuple[str, bytes]]) -> None:
        dests = [dest] if isinstance(dest, str) else list(dest)
        lines = ["sent to %s:%d" % (run.red.scrub(", ".join(dests)), LSDP_PORT),
                 "packet: %s" % binascii.hexlify(packet).decode(),
                 "datagrams received: %d" % len(replies), ""]
        players = _lsdp_players(replies)
        found.extend(players)
        for src, data in replies:
            parsed = lsdp_parse(data)
            lines.append("from %s" % run.red.scrub(src))
            lines.append(run.red.scrub(json.dumps(parsed, indent=2, ensure_ascii=False)))
            lines.append("")
        fname = "%s.txt" % run._next_id("discovery")
        (run.raw / fname).write_text("\n".join(lines), encoding="utf-8")
        announces = len(players)
        pr = Probe(id=fname[:-4], suite="discovery", safety=SAFETY_READ, player="-",
                   method="UDP", port=LSDP_PORT, path=title,
                   note=title, spec_ref="12.1", status=None,
                   body_file="raw/" + fname,
                   verdict=("OK" if announces else
                            ("INFO" if "unicast" in title else "UNEXPECTED")))
        if "R unicast" in title:
            pr.claim = "C-19-lsdp-unicast-R"
            if announces:
                pr.claim_verdict = "CONFIRMED"
            else:
                pr.claim_verdict = ("DISCONFIRMED" if unicast_q_answered.get("ok")
                                    else "INCONCLUSIVE")
        if "Q unicast" in title and announces:
            unicast_q_answered["ok"] = True
        pr.extra["datagrams"] = len(replies)
        pr.extra["player_services"] = announces
        run.results.append(pr)
        print("  %s %-11s %-4s :%-5d %-58s %d player service(s)" % (
            "ok " if announces else "!! ", pr.id, "-", LSDP_PORT, title[:58], announces))

    q = lsdp_query_packet(0x51, (0xFFFF,))
    broadcast_dests = lsdp_broadcast_targets()
    try:
        replies = lsdp_collect(broadcast_dests, q, 11.0, broadcast=True,
                               bind_port=LSDP_PORT, send_times=LSDP_QUERY_TIMES)
        record("LSDP Q on interface broadcasts, listening on 11430 (class 0xFFFF)",
               broadcast_dests, q, replies)
    except OSError as exc:
        run.note("discovery", "broadcast discovery could not bind/send",
                 "%s. Q replies are broadcast to UDP 11430, so a listener on that port is required."
                 % exc, verdict="ERROR")

    # A shorter class-specific control after the normal all-classes query.
    q2 = lsdp_query_packet(0x51, (0x0001, 0x0003, 0x0006, 0x0008))
    try:
        record("LSDP Q broadcast, four player classes",
               broadcast_dests, q2,
               lsdp_collect(broadcast_dests, q2, 2.0, broadcast=True,
                            bind_port=LSDP_PORT))
    except OSError as exc:
        run.note("discovery", "class-specific broadcast failed", str(exc), verdict="ERROR")

    # T-26: unicast queries to known players. R should answer unicast; Q is the
    # control that tells us whether a unicast query reached the player at all.
    r = lsdp_query_packet(0x52, (0xFFFF,))
    for p in run.targets()[:2]:
        try:
            record("LSDP Q unicast to player %s (control for T-26)" % p.label, p.host, q,
                   lsdp_collect(p.host, q, 3.0, bind_port=LSDP_PORT))
        except OSError as exc:
            run.note("discovery", "unicast Q to %s failed" % p.label, str(exc), verdict="ERROR")
        try:
            record("LSDP R unicast to player %s (T-26)" % p.label, p.host, r,
                   lsdp_collect(p.host, r, 3.0, bind_port=LSDP_PORT))
        except OSError as exc:
            run.note("discovery", "unicast R to %s failed" % p.label, str(exc), verdict="ERROR")
    if run.targets() and not unicast_q_answered.get("ok"):
        run.note("discovery",
                 "no player answered a UNICAST LSDP query of either form",
                 "So T-26 is inconclusive rather than disconfirmed: the datagrams may "
                 "never have arrived. Check the host firewall and subnet, then re-run.",
                 verdict="UNEXPECTED")

    run.note("discovery", "mDNS is not probed by this harness",
             "Run separately:  avahi-browse -rt _musc._tcp   or   dns-sd -B _musc._tcp")
    # Deduplicate anything learned by multiple queries while retaining same-IP
    # secondary ports.
    return sorted(
        {(addr, port): (addr, name, port) for addr, name, port in found}.values(),
        key=lambda x: (ipaddress.IPv4Address(x[0]), x[2]))


def lsdp_discover(timeout: float = 11.0,
                  diagnostics: Optional[List[str]] = None) -> List[Tuple[str, str, int]]:
    """Standalone discovery used by --discover."""
    diagnostics = diagnostics if diagnostics is not None else []
    q = lsdp_query_packet(0x51, (0xFFFF,))
    dests = lsdp_broadcast_targets()
    diagnostics.append("using %d IPv4 broadcast target(s); listening on UDP %d"
                       % (len(dests), LSDP_PORT))
    # Keep enough tail after the last send for the documented 0-750 ms response
    # delay. A caller may shorten timeout, in which case only sends that fit are
    # scheduled.
    schedule = tuple(t for t in LSDP_QUERY_TIMES if t <= max(0.0, timeout - 0.8))
    if not schedule:
        schedule = (0.0,)
    listen_secs = max(timeout, schedule[-1] + 0.8)
    try:
        replies = lsdp_collect(dests, q, listen_secs, broadcast=True,
                               bind_port=LSDP_PORT, send_times=schedule)
    except OSError as exc:
        diagnostics.append("LSDP listener/send failed: %s" % exc)
        diagnostics.append("Q replies are broadcast to UDP 11430; an ephemeral listener cannot receive them reliably")
        return []
    players = _lsdp_players(replies)
    if not players:
        diagnostics.append("received %d UDP datagram(s), but no BluOS player Announce records" % len(replies))
    return players


# --------------------------------------------------------------------------
# Shape inventory -- what elements and attributes actually arrived
# --------------------------------------------------------------------------

import xml.etree.ElementTree as ET  # noqa: E402

# Every XML body parsed here arrived over the network from a device this harness
# does not control. ElementTree does not fetch external entities, but it does
# expand internal ones, so a malformed or hostile body can exhaust memory
# ("billion laughs"). Bodies are also capped: a response big enough to matter
# has already been recorded in raw/ and its shape can be read from there.
MAX_PARSE_BYTES = 4 * 1024 * 1024
DOCTYPE_RE = re.compile(r"<!DOCTYPE", re.I)


def safe_parse_xml(text: str):
    """Parse a device response, or return None. Never raises."""
    if not text or len(text) > MAX_PARSE_BYTES:
        return None
    if DOCTYPE_RE.search(text[:2048]):
        return None          # no entity declarations, so no expansion attack
    try:
        return ET.fromstring(text)  # nosec B314 - DOCTYPE refused and size capped above
    except (ET.ParseError, ValueError, MemoryError):
        return None


def build_shapes(run: Runner) -> str:
    """Walk every captured XML body and inventory element paths, attributes and
    sample values. This is what finds attributes the specification does not
    mention yet."""
    per_endpoint: Dict[str, Dict[str, Dict[str, Any]]] = {}

    for pr in run.results:
        if pr.body_kind != "xml" or not pr.body_file:
            continue
        f = run.raw / Path(pr.body_file).name
        if not f.exists():
            continue
        root = safe_parse_xml(f.read_text(encoding="utf-8"))
        if root is None:
            continue
        endpoint = pr.path.split("?")[0]
        bucket = per_endpoint.setdefault(endpoint, {})

        def walk(el, prefix: str, depth: int = 0,
                 bucket: Dict[str, Dict[str, Any]] = bucket) -> None:
            if depth > 64:
                return      # a pathological body must not raise RecursionError
                            # from inside report generation
            tag = el.tag.split("}")[-1]
            path = "%s/%s" % (prefix, tag) if prefix else tag
            node = bucket.setdefault(path, {"count": 0, "attrs": {}, "text_samples": []})
            node["count"] += 1
            for k, v in el.attrib.items():
                slot = node["attrs"].setdefault(k, {"count": 0, "samples": []})
                slot["count"] += 1
                v = (v or "").strip()
                if v and len(slot["samples"]) < 3 and v not in slot["samples"]:
                    slot["samples"].append(v[:60])
            text = (el.text or "").strip()
            if text and len(node["text_samples"]) < 3 and text not in node["text_samples"]:
                node["text_samples"].append(text[:60])
            for child in el:
                walk(child, path, depth + 1, bucket)

        walk(root, "")

    lines = ["# Element and attribute inventory",
             "",
             "Harvested automatically from every XML body captured in this run.",
             "Values are already redacted. Counts are occurrences across all",
             "captures for that endpoint, so an attribute with a low count",
             "relative to its element is optional in practice.",
             "",
             "Compare this against the response-shape tables in the",
             "specification: anything here that is not documented there is a",
             "gap, and anything documented that never appears here is either",
             "conditional or historical.",
             ""]
    for endpoint in sorted(per_endpoint):
        lines.append("## `%s`" % endpoint)
        lines.append("")
        lines.append("| element path | n | attributes (n) | sample text |")
        lines.append("|---|---|---|---|")
        for path in sorted(per_endpoint[endpoint]):
            node = per_endpoint[endpoint][path]
            attrs = ", ".join("`%s`(%d)" % (k, v["count"])
                              for k, v in sorted(node["attrs"].items()))
            texts = "; ".join("`%s`" % t.replace("|", "\\|") for t in node["text_samples"])
            lines.append("| `%s` | %d | %s | %s |" % (path, node["count"], attrs or "-", texts or "-"))
        lines.append("")

        detail = []
        for path in sorted(per_endpoint[endpoint]):
            node = per_endpoint[endpoint][path]
            for k, v in sorted(node["attrs"].items()):
                if v["samples"]:
                    detail.append("- `%s@%s` = %s" % (path, k, ", ".join("`%s`" % s.replace("|", "\\|") for s in v["samples"])))
        if detail:
            lines.append("<details><summary>attribute value samples</summary>")
            lines.append("")
            lines.extend(detail[:400])
            lines.append("")
            lines.append("</details>")
            lines.append("")

    return "\n".join(lines)




def build_samples(run: Runner) -> str:
    """One canonical, pretty-printed response per endpoint.

    The point of the specification is that nobody should have to decompile the
    app to learn what a response looks like. A confidence marker says how far to
    trust a claim; it does not show anyone the bytes. This file does.

    Preference order: a verbatim capture (redaction changed nothing) over a
    modified one, a 200 over an error, and the largest body among equals, since
    optional elements only appear when there is content to carry them.
    """
    best: Dict[str, Probe] = {}
    for pr in run.results:
        if not pr.body_file or pr.body_kind not in ("xml", "json"):
            continue
        endpoint = pr.path.split("?")[0]
        cur = best.get(endpoint)
        def rank(x: Probe) -> Tuple[int, int, int]:
            return (1 if x.status == 200 else 0,
                    1 if x.verbatim else 0,
                    x.body_bytes or 0)
        if cur is None or rank(pr) > rank(cur):
            best[endpoint] = pr

    lines = ["# Canonical response samples",
             "",
             "One representative response per endpoint from this run, so the",
             "specification can show the actual bytes rather than send a reader to",
             "a decompiler. Every sample is already redacted; the `fidelity` column",
             "says whether redaction touched it at all.",
             "",
             "A sample is **not** a confidence marker and never contradicts one. An",
             "element documented from first-party code but absent here is",
             "conditional, not wrong: it appears when there is content to carry it.",
             "Never delete a documented field because one capture lacks it.",
             ""]
    if run.synthetic:
        lines[0:0] = ["> **SYNTHETIC RUN — NOT EVIDENCE.** These samples came from a loopback",
                      "> stand-in, not a BluOS player.", ""]

    lines += ["| endpoint | probe | status | bytes | fidelity |", "|---|---|---|---|---|"]
    for ep in sorted(best):
        pr = best[ep]
        lines.append("| `%s` | `%s` | %s | %s | %s |" % (
            ep, pr.id, pr.status, pr.body_bytes,
            "verbatim" if pr.verbatim else "%d edit(s)" % pr.redaction_edits))
    lines.append("")

    for ep in sorted(best):
        pr = best[ep]
        f = run.raw / Path(pr.body_file).name
        if not f.exists():
            continue
        text = f.read_text(encoding="utf-8")
        pretty = text
        if pr.body_kind == "xml" and safe_parse_xml(text) is not None:
            try:
                import xml.dom.minidom as _md
                # nosec B318 - safe_parse_xml above already refused any DOCTYPE
                pretty = _md.parseString(text).toprettyxml(indent="  ")
                pretty = "\n".join(ln for ln in pretty.splitlines() if ln.strip())
            except Exception:
                pretty = text
        elif pr.body_kind == "json":
            try:
                pretty = json.dumps(json.loads(text), indent=2, ensure_ascii=False)
            except Exception:
                pretty = text
        truncated = len(pretty) > 6000
        if truncated:
            pretty = pretty[:6000] + "\n... truncated; the whole body is in %s" % pr.body_file
        lines += ["## `%s`" % ep, "",
                  "%s `%s` — probe `%s`, %s, %s." % (
                      pr.method, pr.path, pr.id, pr.content_type or "no content type",
                      "byte-for-byte what the device sent" if pr.verbatim
                      else "%d redaction edit(s)" % pr.redaction_edits),
                  "",
                  "```" + ("xml" if pr.body_kind == "xml" else "json"),
                  pretty,
                  "```", ""]
    return "\n".join(lines)


# --------------------------------------------------------------------------
# Reports
# --------------------------------------------------------------------------

def _suite_tables(by_suite: Dict[str, List[Probe]]) -> List[str]:
    """One table per suite, plus the analysis notes that belong to it."""
    lines: List[str] = []
    for suite in sorted(by_suite):
        lines.append("## suite: %s" % suite)
        lines.append("")
        lines.append("| id | v | player | port | request | status | ms | type | root | bytes | note |")
        lines.append("|---|---|---|---|---|---|---|---|---|---|---|")
        for pr in by_suite[suite]:
            if pr.method == "-":
                lines.append("| `%s` | %s | | | *analysis* | | | | | | **%s** |" % (
                    pr.id, pr.verdict[0], pr.note.replace("|", "\\|")))
                continue
            req = pr.path if pr.method == "GET" else "%s %s" % (pr.method, pr.path)
            lines.append("| `%s` | %s | %s | %d | `%s` | %s | %s | %s | `%s` | %s | %s |" % (
                pr.id, pr.verdict[0], pr.player, pr.port, req.replace("|", "\\|"),
                pr.status if pr.status is not None else "-",
                int(pr.elapsed_ms) if pr.elapsed_ms is not None else "-",
                pr.body_kind, pr.root_element,
                pr.body_bytes if pr.body_bytes is not None else "-",
                (pr.note + (" -- " + pr.error if pr.error else "")).replace("|", "\\|")))
        lines.append("")

        notes = [pr for pr in by_suite[suite] if pr.method == "-" and pr.extra.get("detail")]
        if notes:
            lines.append("### %s -- analysis detail" % suite)
            lines.append("")
            for pr in notes:
                lines.append("**%s** (`%s`)" % (pr.note, pr.id))
                lines.append("")
                lines.append("```")
                lines.append(str(pr.extra.get("detail", ""))[:4000])
                lines.append("```")
                lines.append("")
    return lines


def build_report(run: Runner, started: datetime.datetime, elapsed: float) -> str:
    by_suite: Dict[str, List[Probe]] = {}
    for pr in run.results:
        by_suite.setdefault(pr.suite, []).append(pr)

    counts: Dict[str, int] = {}
    for pr in run.results:
        counts[pr.verdict] = counts.get(pr.verdict, 0) + 1

    lines = ["# BluOS probe run -- results",
             ""]
    if run.synthetic:
        lines += ["> **SYNTHETIC RUN — NOT EVIDENCE.** The target was loopback, not a",
                  "> BluOS player. This bundle exercises the harness only. Nothing in it",
                  "> says anything about the protocol.", ""]
    lines += [
             "| | |",
             "|---|---|",
             "| harness | bluos-probe.py %s |" % VERSION,
             "| started | %s |" % started.replace(microsecond=0).isoformat(),
             "| duration | %.1f s |" % elapsed,
             "| timezone declared to devices | `%s` (`X-Sovi-Tz`) |"
             % tz_context()["declared_to_device"],
             "| harness host clock | %s (UTC%s) |" % (
                 tz_context()["harness_host_tzname"],
                 tz_context()["harness_host_offset"]),
             "| probes | %d |" % len(run.results),
             "| verdicts | %s |" % ", ".join("%s %d" % (k, v) for k, v in sorted(counts.items())),
             "| safety classes run | %s |" % ", ".join(
                 ["read"] + ([] if run.opts.no_probe else ["probe"]) +
                 (["state"] if any(pr.safety == SAFETY_STATE and pr.status is not None
                                   for pr in run.results) else [])),
             "",
             "`OK` means the result matched what the specification predicts.",
             "`UNEXPECTED` means it did not -- those rows are the interesting ones.",
             "`INFO` means no prediction was recorded, so the capture is the result.",
             "",
             "## Players",
             "",
             "| label | name | model | firmware | schema | topology |",
             "|---|---|---|---|---|---|"]
    for p in run.players.values():
        if not p.reachable:
            lines.append("| %s | unreachable | | | | |" % p.label)
            continue
        name = "Room-%s" % p.label if run.red.redact_names else run.red.scrub(p.name)
        topo = "master" if p.is_master and not p.is_slave else (
            "nested master" if p.is_master and p.is_slave else (
                "slave" if p.is_slave else "standalone"))
        lines.append("| %s | %s | %s %s | %s | %s | %s |" % (
            p.label, name, p.brand, p.model, p.version, p.schema, topo))
    lines.append("")

    tzc = tz_context()
    declared_offset = _offset_for_zone(tzc["declared_to_device"])
    if declared_offset and declared_offset != tzc["harness_host_offset"]:
        lines += ["> **Timezone note.** Devices were told `%s` (currently UTC%s), while the"
                  % (tzc["declared_to_device"], declared_offset),
                  "> machine running the harness is on %s (UTC%s). Any clock-dependent"
                  % (tzc["harness_host_tzname"], tzc["harness_host_offset"]),
                  "> value in these captures -- alarm times above all -- is expressed in the",
                  "> declared zone, not in the harness host's. Read them against `%s`."
                  % tzc["declared_to_device"], ""]

    # things that did not match the specification, up front
    odd = [pr for pr in run.results if pr.verdict == "UNEXPECTED"]
    if odd:
        lines += ["## Results that did not match the specification", "",
                  "| id | player | request | status | expected | note |",
                  "|---|---|---|---|---|---|"]
        for pr in odd:
            lines.append("| `%s` | %s | `:%d %s` | %s | `%s` | %s |" % (
                pr.id, pr.player, pr.port, pr.path.replace("|", "\\|"),
                pr.status if pr.status is not None else (pr.error or "-"),
                pr.expect, pr.note.replace("|", "\\|")))
        lines.append("")

    # Key on the claim id, not on a marker in the note text. Filtering on "[T"
    # dropped every probe that carries a claim id without that prose marker --
    # which was all of state_setmaster and the disabled-input checks.
    claim_rows = [pr for pr in run.results
                  if pr.method != "-" and (pr.claim or "[T" in pr.note or "[V" in pr.note)]
    if claim_rows:
        lines += ["## Claim checks",
                  "",
                  "Every probe aimed at a marked claim in the specification, so the",
                  "register in section 17 can be updated from one table. `root` and",
                  "`bytes` are usually enough to tell a real answer from a 404.",
                  "",
                  "| id | claim | verdict | player | port | request | status | root | note |",
                  "|---|---|---|---|---|---|---|---|---|"]
        for pr in claim_rows:
            lines.append("| `%s` | `%s` | %s | %s | %d | `%s` | %s | `%s` | %s |" % (
                pr.id, pr.claim or "-", pr.claim_verdict or "-", pr.player, pr.port,
                pr.path.replace("|", "\\|"),
                pr.status if pr.status is not None else (pr.error or "-"),
                pr.root_element, pr.note.replace("|", "\\|")))
        lines.append("")

    lines += _suite_tables(by_suite)

    roots = sorted({pr.root_element for pr in run.results
                    if pr.root_element and pr.safety == SAFETY_STATE
                    and pr.path.split("?")[0] in ("/Play", "/Pause", "/Stop", "/Preset",
                                                  "/Skip", "/Back", "/Add", "/Load")})
    if roots:
        lines += ["## Play-response root elements observed", "",
                  "Blu4Net reports four possible roots for a play-type response. Observed "
                  "in this run: %s. An HTTP 200 alone says nothing about which arrived, so "
                  "this is collected from the bodies rather than from status codes."
                  % ", ".join("`%s`" % r for r in roots), ""]

    lines += ["## Bodies", "",
              "Response bodies are in `raw/`, one file per probe id, alongside a",
              "`.head.txt` with the status line and response headers. Binary",
              "bodies (artwork) are not stored: only their length, content type",
              "and first bytes are recorded here, so no embedded metadata can",
              "leak. Their SHA-256 is in the do-not-share key file, not in this",
              "bundle.", ""]
    return "\n".join(lines)


def build_readme(run: Runner, started: datetime.datetime) -> str:
    state_probes = [pr for pr in run.results if pr.safety == SAFETY_STATE
                    and pr.status is not None]
    changed_paths = sorted({pr.path.split("?")[0] for pr in state_probes})
    written_players = sorted({pr.player for pr in state_probes})

    if state_probes:
        scope = [
            "## What was run",
            "",
            "**This run changed player state.** It was invoked with `--allow-state`,",
            "so the `read`, `probe` and `state` safety classes were all enabled.",
            "%d state-changing request(s) were issued against player(s) %s, touching"
            % (len(state_probes), ", ".join(written_players)),
            "these endpoints:",
            "",
            "  " + ", ".join("`%s`" % c for c in changed_paths),
            "",
            "Every change was snapshotted beforehand and restored afterwards; the",
            "`restore` section of `REPORT.md` records whether each restore",
            "succeeded. Nothing irreversible was attempted: no share was modified,",
            "no firmware path was called, and no preset, playlist or streaming",
            "favourite was created or deleted.",
        ]
    else:
        scope = [
            "## What was run",
            "",
            "Only the `read` and `probe` safety classes: requests that cannot change",
            "player state. No grouping call, no transport control, no settings write,",
            "no firmware path and no share modification was issued. Endpoints whose",
            "bare form is known or suspected to act (`/SetMaster`, `/RemoveSlave`,",
            "`/Sleep`, `/Standalone`, `/LeaveGroup`, `/upgrade`, `/Reindex`,",
            "`/Preset`, `/SlaveVolume`) were not called at all.",
            "",
            "Three paths are called with **no parameters** to establish whether they",
            "exist: `/audiomodes`, `/proxyToSlave` and `/Sync`. None can act without",
            "a target. `--no-probe` omits them.",
        ]
    return "\n".join([
        "# BluOS probe bundle",
        "",
        "Automated %s probe of a live BluOS fleet, produced by"
        % ("state-changing" if state_probes else "read-only"),
        "`bluos-probe.py %s` on %s." % (VERSION, started.replace(microsecond=0).isoformat()),
        "",
        "## What is here",
        "",
        "| file | what it is |",
        "|---|---|",
        "| `REPORT.md` | every probe, grouped by suite, with a verdict against the specification |",
        "| `MANIFEST.json` | the same data structured, for diffing between runs |",
        "| `SHAPES.md` | element/attribute inventory harvested from every XML body captured |",
        "| `SAMPLES.md` | one canonical, pretty-printed response per endpoint, for the specification to quote |",
        "| `FINDINGS.md` | claim-by-claim verdicts, including the disconfirmed ones, ready to paste into the register |",
        "| `REDACTIONS.md` | what was removed and what replaced it |",
        "| `raw/` | redacted response bodies and headers, one pair per probe id |",
        "",
        "",
    ] + scope + [
        "",
        "## Reading it",
        "",
        "`REPORT.md` opens with the rows whose result did not match the",
        "specification. Those are the ones worth reading first: each is either a",
        "specification error, a firmware difference, or a test that was aimed",
        "wrongly.",
        "",
        "## Timezone",
        "",
        "Devices were told `%s` in the `X-Sovi-Tz` header on every request."
        % tz_context()["declared_to_device"],
        "That is a fixed, recorded constant rather than whatever the machine",
        "running the harness was set to, because BluOS uses it for",
        "time-dependent answers -- alarm times in particular. Read every clock",
        "value in these captures against that zone. The harness host's own",
        "clock at the time of the run was %s (UTC%s), recorded in" % (
            tz_context()["harness_host_tzname"], tz_context()["harness_host_offset"]),
        "`MANIFEST.json` under `timezone` so the two can be told apart.",
        "",
        "## Privacy",
        "",
        "Addresses, MAC addresses, share hosts, credentials and other identifying",
        "values were replaced before anything was written to disk, and the whole",
        "bundle was re-scanned afterwards to confirm none survived. See",
        "`REDACTIONS.md`. Placeholders are stable within the run, so",
        "`192.0.2.11` is the same player everywhere.",
        "",
    ])


def build_redactions(run: Runner, findings: List[str]) -> str:
    summary = run.red.summary()
    lines = ["# Redactions",
             "",
             "Applied to every response body, response header and request URL",
             "**before** anything was written to disk. Replacements are stable",
             "within the run, so relationships between captures survive: the",
             "same original always becomes the same placeholder.",
             "",
             "## Policy",
             "",
             "| class | replaced with | why that form |",
             "|---|---|---|",
             "| IPv4 | `192.0.2.x` | RFC 5737 TEST-NET-1: valid, parseable, non-routable, obviously documentation |",
             "| IPv6 | `2001:db8::x` | RFC 3849 documentation prefix |",
             "| MAC | `02:00:00:00:00:xx` | locally administered range; keeps the shape a parser expects |",
             "| share / UNC host | `host-N.invalid` | reserved TLD, cannot resolve |",
             "| e-mail | `userN@example.invalid` | |",
             "| secret-named keys and elements | `[REDACTED-value-N]` | `password`, `token`, `ssid`, `username`, `serial`, `signature`, coordinates and similar |",
             "| Bluetooth device names | `[REDACTED-value-N]` | these routinely contain a person's name |",
             "| binary bodies (artwork) | not stored at all | only length, content type and SHA-256 are kept, so no embedded metadata can travel |",
             "",
             "Player and room names are %s." % (
                 "replaced with `Room-A`, `Room-B`, ..." if run.red.redact_names
                 else "**kept**, because they carry no personal information and make "
                      "the captures readable. Re-run with `--redact-names` to remove them"),
             "",
             "Protocol constants are deliberately kept, because they identify",
             "nobody's network: %s. The RFC 5737 documentation ranges"
             % ", ".join("`%s`" % a for a in sorted(IPV4_KEEP)),
             "(`192.0.2.0/24`, `198.51.100.0/24`, `203.0.113.0/24`) are also kept,",
             "both because they are where placeholders come from and because the",
             "harness deliberately sends one as an unreachable target.",
             "",
             "## Counts",
             "",
             "| class | distinct originals | replacements made |",
             "|---|---|---|"]
    for kind, data in sorted(summary.items()):
        lines.append("| %s | %d | %d |" % (kind, data["distinct"], data["replacements"]))
    lines += ["",
              "The originals themselves are **not** in this bundle. They are in",
              "`DO-NOT-SHARE-key-<timestamp>.json`, written next to the bundle",
              "directory rather than inside it.",
              "",
              "## Verification",
              ""]
    if findings:
        lines += ["**%d finding(s). Do not share this bundle until they are resolved.**" % len(findings), ""]
        lines += ["- %s" % f for f in findings]
    else:
        lines += ["Every file in the bundle was re-scanned after writing for the",
                  "original values, for private-range IPv4 addresses (RFC 1918,",
                  "CGNAT and link-local) and for MAC-shaped strings outside the",
                  "placeholder range. **Nothing was found.**"]
    lines.append("")
    return "\n".join(lines)


# --------------------------------------------------------------------------
# Self-test: a deliberately grubby fake player, so the harness and especially
# the redactor can be validated without touching hardware.
# --------------------------------------------------------------------------

FAKE_SYNCSTATUS = (
    '<?xml version="1.0" encoding="UTF-8"?>'
    '<SyncStatus etag="886" syncStat="886" version="4.16.22" id="10.255.255.21:11000" '
    'db="-41.2" volume="30" name="Stue" model="N132" modelName="NODE" class="streamer" '
    'brand="Bluesound" schemaVersion="34" initialized="true" group="Stue+Kokken" '
    'mac="00:00:5E:00:53:01" hasSubwoofer="true">'
    '<slave id="10.255.255.22" port="11000" name="Kokken" model="N132"></slave>'
    '<bluetoothOutput name="Peter iPhone" codec="aptx"></bluetoothOutput>'
    '</SyncStatus>'
)
FAKE_STATUS = (
    '<?xml version="1.0" encoding="UTF-8"?>'
    '<status etag="abc123"><album>An Album</album><service>Tidal</service>'
    '<image>/Artwork?service=Tidal&amp;songid=Tidal%3A70813938</image>'
    '<songid>Tidal:70813938</songid><volume>24</volume></status>'
)
FAKE_SHARES = (
    '<?xml version="1.0" encoding="UTF-8"?><shares count="1"><share>'
    '<sharename>\\\\fileserver01\\music</sharename><username>bluesound</username>'
    '<password>hunter2</password></share></shares>'
)
FAKE_SERVICES = (
    '<?xml version="1.0" encoding="UTF-8"?><services schemaVersion="34" sid="46">'
    '<service name="Tidal" type="CloudService" displayname="TIDAL">'
    '<menu><menuEntry displayName="Songs">'
    '<browseRequest url="/Songs" resultType="Song"/></menuEntry></menu></service>'
    '</services>'
)




# --------------------------------------------------------------------------
# Harness regression tests
#
# Each of these pins a bug that actually occurred during development. They test
# this script, not BluOS, and produce no bundle and no protocol evidence.
# --------------------------------------------------------------------------

def _unit_tests() -> List[Tuple[str, bool, str]]:
    out: List[Tuple[str, bool, str]] = []

    def check(name: str, ok: bool, detail: str = "") -> None:
        out.append((name, bool(ok), detail))

    # --- root_attrs: a child element must not win over the root.
    # This shipped broken: <bluetoothOutput name=...> and <slave name=...> both
    # carry `name`, so a master reported its slave's name as its own -- and with
    # --redact-names the wrong string was registered, leaving the real player
    # name unredacted in a bundle about to be shared.
    sync = ('<?xml version="1.0"?><SyncStatus etag="886" name="Stue" model="N132" '
            'mac="00:00:5E:00:53:01" group="Stue+Kitchen">'
            '<slave id="10.255.255.22" port="11000" name="Kitchen" model="N125"/>'
            '<bluetoothOutput name="Someone iPhone"/></SyncStatus>')
    a = root_attrs(sync)
    check("root_attrs takes name from the root, not a child", a.get("name") == "Stue",
          "got %r" % a.get("name"))
    check("root_attrs takes model from the root, not a child", a.get("model") == "N132",
          "got %r" % a.get("model"))

    si = parse_sync(sync)
    check("parse_sync finds the slave", si.slaves == ["10.255.255.22"], "got %r" % (si.slaves,))
    check("parse_sync reports the master's own name", si.name == "Stue", "got %r" % si.name)
    check("parse_sync sees a master as grouped", si.grouped)
    check("parse_sync on a standalone player is not grouped",
          not parse_sync('<SyncStatus etag="1" name="X"/>').grouped)
    check("parse_sync handles a self-closing <master/>",
          bool(parse_sync('<SyncStatus etag="1"><master/></SyncStatus>').master))

    # --- element_text must not match a longer element with the same prefix
    check("element_text exact match",
          element_text("<state>play</state><stateExtra>x</stateExtra>", "state") == "play")
    check("element_text missing element returns empty", element_text("<a>1</a>", "zz") == "")
    check("element_int on a non-number returns None",
          element_int("<volume>abc</volume>", "volume") is None)

    # --- redaction
    red = Redactor()
    red.reserve_ipv4("10.255.255.21", "192.0.2.11")
    txt = red.scrub(sync + '<share><sharename>\\\\fileserver01\\music</sharename>'
                           '<password>hunter2</password></share> bob@gmail.com')
    for needle in ("10.255.255.22", "00:00:5E:00:53:01", "fileserver01",
                   "hunter2", "bob@gmail.com"):
        check("redactor removes %s" % needle, needle not in txt)
    check("redacted SyncStatus still parses as XML",
          safe_parse_xml(txt[:txt.index("<share>")]) is not None)
    # A player reserved for redaction must be redacted even if its address is
    # also on the keep-list. The keep-list short-circuited first, so the address
    # was left in the bundle while the verifier flagged it as a leak.
    red2 = Redactor()
    red2.reserve_ipv4("127.0.0.1", "192.0.2.11")
    check("a reserved address is redacted even when on the keep-list",
          red2.scrub("player at 127.0.0.1") == "player at 192.0.2.11",
          "got %r" % red2.scrub("player at 127.0.0.1"))
    check("an unreserved keep-list address is left alone",
          Redactor().scrub("<master>127.0.0.1</master>") == "<master>127.0.0.1</master>")
    check("scrub_counted reports zero edits for clean text",
          red.scrub_counted("<browse type='menu'/>")[1] == 0)
    check("scrub_counted reports edits for dirty text",
          red.scrub_counted("host 10.255.255.9")[1] > 0)
    # LocalMusic browse keys percent-encode '/' as %2F.  The old IPv4 regex used
    # a leading \b, which cannot match between the 'F' in %2F and the first digit
    # of the address because both are regex word characters.
    browse_ip = "10.255.255.41"
    browse_key = (
        'contextMenuKey="LocalMusic:CM/LocalMusic-Song?'
        f'filename=%2Fvar%2Fmnt%2F{browse_ip}-music%2FArtist%2FTrack.flac"'
    )
    red_browse = Redactor()
    scrubbed_browse = red_browse.scrub(browse_key)
    check("IPv4 after a percent-encoded slash is redacted in a browse key",
          browse_ip not in scrubbed_browse, scrubbed_browse)
    check("browse-key IPv4 is replaced with a documentation address",
          "192.0.2." in scrubbed_browse, scrubbed_browse)
    # MANIFEST body_preview contains the same XML inside a JSON string; it must
    # not reintroduce the original address when the manifest is scrubbed.
    manifest_preview = json.dumps({"body_preview": browse_key})
    check("IPv4 after %2F is redacted inside a manifest body_preview",
          browse_ip not in red_browse.scrub(manifest_preview),
          red_browse.scrub(manifest_preview))
    # A hostname first shown as plain browse text and only later in a share URL
    # used to be learned too late, leaving the first occurrence in the bundle.
    red3 = Redactor()
    learned_late = red3.scrub('<item name="fileserver01"/><x url="smb://fileserver01/music"/>')
    check("a share hostname learned late is scrubbed everywhere in the same body",
          "fileserver01" not in learned_late, learned_late)
    secret_key_test = Redactor()
    secret_key_test.add_literal("do-not-store-this", "[REDACTED-USER-SUPPLIED]")
    check("key material does not store --secret literals",
          "do-not-store-this" not in json.dumps(secret_key_test.key_material()))

    # --- safe_parse_xml refuses entity declarations (billion laughs)
    bomb = ('<?xml version="1.0"?><!DOCTYPE x [<!ENTITY a "aaaaaaaaaa">]>'
            '<x>&a;&a;&a;</x>')
    check("safe_parse_xml refuses a DOCTYPE", safe_parse_xml(bomb) is None)
    check("safe_parse_xml refuses an oversized body",
          safe_parse_xml("<x>" + "y" * (MAX_PARSE_BYTES + 1) + "</x>") is None)
    check("safe_parse_xml accepts ordinary XML", safe_parse_xml("<x a='1'/>") is not None)

    # --- expectation clauses
    class _O:
        """Fresh per use, so an assertion cannot depend on an earlier one having
        mutated a class attribute."""
        def __init__(self, allow_state: bool = False, **kw):
            self.no_probe = False
            self.allow_state = allow_state
            self.no_bodies = True
            self.preserve = None
            self.max_volume = 10
            self.__dict__.update(kw)
    import tempfile
    scratch = Path(tempfile.mkdtemp(prefix="bluos-probe-selftest-"))
    verify_dir = scratch / "verify-location"
    verify_dir.mkdir()
    (verify_dir / "leak.txt").write_text("clean\nxx hunter2 yy\n", encoding="utf-8")
    verify_red = Redactor()
    verify_red.add_literal("hunter2", "[REDACTED-USER-SUPPLIED]")
    verify_findings = verify_bundle(verify_dir, verify_red)
    check("verifier reports line and column without echoing the leaked value",
          any("leak.txt:2:4" in f for f in verify_findings) and
          all("hunter2" not in f for f in verify_findings),
          "; ".join(verify_findings))

    rr = Runner(_O(), Redactor(), scratch)
    pr = Probe(id="t", suite="t", safety=SAFETY_READ, player="A", method="GET",
               port=11000, path="/x")
    pr.status, pr.root_element, pr.body_kind = 200, "browse", "xml"
    pr.headers = [["ETag", "886"], ["Content-Type", "text/xml"]]
    check("status clause matches", rr._match(pr, "status=200", ""))
    check("status alternation matches", rr._match(pr, "status=404|200", ""))
    check("status clause rejects", not rr._match(pr, "status=404", ""))
    check("root clause matches", rr._match(pr, "root=browse", ""))
    check("header presence matches", rr._match(pr, "header=ETag", ""))
    check("header presence is case-insensitive", rr._match(pr, "header=etag", ""))
    check("noheader rejects a present header", not rr._match(pr, "noheader=ETag", ""))
    check("noheader accepts an absent header", rr._match(pr, "noheader=Last-Modified", ""))
    check("contains clause reads the body", rr._match(pr, "contains=<item", "<item a='1'/>"))
    check("absent clause reads the body", rr._match(pr, "absent=<item", "<other/>"))
    check("clauses are ANDed", not rr._match(pr, "status=200;root=status", ""))

    # --- claim verdicts, including the distinction that matters most
    pr.expect = ""
    check("claim CONFIRMED", rr._claim_verdict(pr, "status=200", "status=404") == "CONFIRMED")
    pr.status = 404
    check("claim DISCONFIRMED", rr._claim_verdict(pr, "status=200", "status=404") == "DISCONFIRMED")
    pr.status = 500
    check("claim INCONCLUSIVE when neither rule fits",
          rr._claim_verdict(pr, "status=200", "status=404") == "INCONCLUSIVE")
    pr.error = "timeout"
    check("a transport error is never a verdict",
          rr._claim_verdict(pr, "status=200", "status=404") == "INCONCLUSIVE")

    # --- safety gating: state must not run without --allow-state
    check("state is refused by default", not rr.allowed(SAFETY_STATE))
    check("destructive is always refused", not rr.allowed(SAFETY_DESTRUCTIVE))
    allowed_runner = Runner(_O(allow_state=True), Redactor(), scratch)
    check("state runs with --allow-state", allowed_runner.allowed(SAFETY_STATE))
    check("destructive stays refused even with --allow-state",
          not allowed_runner.allowed(SAFETY_DESTRUCTIVE))

    # --- the restore ledger must run undos and survive a failing one
    rr2 = Runner(_O(), Redactor(), scratch)
    fired: List[str] = []
    rr2.defer("first", lambda: fired.append("first"))
    rr2.defer("boom", lambda: (_ for _ in ()).throw(RuntimeError("nope")))
    rr2.defer("third", lambda: fired.append("third"))
    already = rr2.defer("already done", lambda: fired.append("SHOULD NOT RUN"))
    already["done"] = True
    failures = rr2.run_restores()
    check("restores unwind in reverse order", fired == ["third", "first"], "got %r" % (fired,))
    check("a failing restore does not stop the others", len(failures) == 1)
    check("a resolved restore is skipped", "SHOULD NOT RUN" not in fired)

    # --- LSDP wire format
    pkt = lsdp_query_packet(0x51, (0xFFFF,))
    check("LSDP query has the magic header", pkt[:6] == b"\x06LSDP\x01",
          "got %r" % pkt[:6])
    check("LSDP query length byte is self-consistent", pkt[6] == len(pkt) - 6,
          "byte %d, remaining %d" % (pkt[6], len(pkt) - 6))
    check("lsdp_parse rejects a non-LSDP datagram",
          "error" in lsdp_parse(b"not an lsdp packet at all"))
    check("lsdp_parse does not raise on a truncated packet",
          isinstance(lsdp_parse(b"\x06LSDP\x01\x40A\xff"), dict))
    # Real N130 Announce fixture from spec 12.1/nightvision.
    # The node_id and address in these bytes are synthetic: RFC 7042
    # documentation MAC and a 10.255.255.0/24 fixture address. The wire STRUCTURE
    # is the real captured Announce; only the identifying fields were swapped, so
    # this file can be shared.
    announce = bytes.fromhex(
        "06 4C 53 44 50 01 73 41 06 00 00 5E 00 53 03 04 0A FF FF 1E 02 "
        "00 01 05 04 6E 61 6D 65 0E 42 6C 75 65 73 6F 75 6E 64 20 4E 6F 64 65 "
        "04 70 6F 72 74 05 31 31 30 30 30 05 6D 6F 64 65 6C 04 4E 31 33 30 "
        "07 76 65 72 73 69 6F 6E 07 33 2E 32 30 2E 35 32 02 7A 73 01 30 "
        "00 04 02 04 6E 61 6D 65 0E 42 6C 75 65 73 6F 75 6E 64 20 4E 6F 64 65 "
        "04 70 6F 72 74 05 31 31 34 33 31")
    discovered = _lsdp_players([("10.255.255.30", announce)])
    check("real LSDP Announce yields the player service and advertised port",
          discovered == [("10.255.255.30", "Bluesound Node", 11000)],
          "got %r" % (discovered,))

    # --- body sniffing
    check("sniffs XML", sniff_body_kind(b"<?xml version='1.0'?><a/>", "text/xml") == "xml")
    check("sniffs a 404 body as text",
          sniff_body_kind(b"404 page not found", "text/plain") == "text")
    check("sniffs JPEG as binary", sniff_body_kind(b"\xff\xd8\xff\xe0abc", "image/jpeg") == "binary")
    check("sniffs an empty body", sniff_body_kind(b"", "") == "none")

    # --- player argument parsing
    specs = parse_players(["A=10.255.255.1", "10.255.255.2", "C=10.255.255.3:11010"], 11000)
    check("labelled player parsed", specs[0] == ("A", "10.255.255.1", 11000), "got %r" % (specs[0],))
    check("unlabelled player gets a letter", specs[1][0] == "B", "got %r" % (specs[1],))
    check("explicit port honoured", specs[2] == ("C", "10.255.255.3", 11010), "got %r" % (specs[2],))

    # --- the source fingerprint must ignore playback state
    check("state is not part of the source fingerprint", "state" not in SOURCE_FIELDS)
    check("streamUrl is part of the source fingerprint", "streamUrl" in SOURCE_FIELDS)

    # --- report assembly. Splitting build_findings silently dropped the
    # "Promote out of the register" section: the logic tests all still passed
    # because none of them looked at the assembled document.
    rr3 = Runner(_O(), Redactor(), scratch)
    rr3.players["A"] = Player(label="A", host="192.0.2.11", model="N132",
                              version="4.16.22", schema="34", reachable=True)
    ok_probe = Probe(id="001-claims", suite="claims", safety=SAFETY_READ, player="A",
                     method="GET", port=80, path="/diagnostics",
                     claim="C-01-diagnostics-80", claim_verdict="CONFIRMED",
                     status=200, verdict="OK", body_file="raw/001-claims.html",
                     body_bytes=10, body_bytes_wire=10, verbatim=True)
    bad_probe = Probe(id="002-claims", suite="claims", safety=SAFETY_READ, player="A",
                      method="GET", port=11000, path="/GetSettings",
                      claim="C-06-getsettings", claim_verdict="DISCONFIRMED",
                      status=404, verdict="OK")
    rr3.results = [ok_probe, bad_probe]
    rr3.facts["untestable"] = ["T-14 authentication: no way to set credentials"]
    findings = build_findings(rr3, datetime.datetime(2026, 1, 1), "bundle-test")
    for heading in ("## Claim results", "### Not exercised by this run",
                    "### Not answerable on this hardware",
                    "## Rows for the specification's disconfirmation register",
                    "## Promote out of the register", "## Capture fidelity"):
        check("FINDINGS contains %r" % heading, heading in findings)
    check("FINDINGS puts a disconfirmed claim in the register rows",
          "C-06-getsettings" in findings.split("disconfirmation register")[1])
    check("FINDINGS offers a confirmed claim for promotion",
          "C-01-diagnostics-80" in findings.split("Promote out of the register")[1])
    check("FINDINGS marks untestable claims as not answerable",
          "T-14 authentication" in findings)

    report = build_report(rr3, datetime.datetime(2026, 1, 1), 1.0)
    for heading in ("## Players", "## Claim checks", "## suite: claims", "## Bodies"):
        check("REPORT contains %r" % heading, heading in report)
    check("REPORT lists both probes", "001-claims" in report and "002-claims" in report)

    readme_ro = build_readme(rr3, datetime.datetime(2026, 1, 1))
    check("a read-only bundle README says nothing was changed",
          "Only the `read` and `probe` safety classes" in readme_ro)
    rr3.results.append(Probe(id="003-state", suite="state_name", safety=SAFETY_STATE,
                             player="A", method="GET", port=11000, path="/Name?set=X",
                             status=200, verdict="OK"))
    readme_state = build_readme(rr3, datetime.datetime(2026, 1, 1))
    check("a state-changing bundle README says so",
          "This run changed player state" in readme_state)
    check("a state-changing bundle README names the endpoint it touched",
          "`/Name`" in readme_state)

    # --- timezone is a fixed, recorded constant, not the host's setting
    check("X-Sovi-Tz is Europe/Copenhagen by default",
          SOVI_HEADERS["X-Sovi-Tz"] == "Europe/Copenhagen",
          "got %r" % SOVI_HEADERS.get("X-Sovi-Tz"))
    tzc = tz_context()
    check("tz_context records what was declared to the device",
          tzc["declared_to_device"] == SOVI_HEADERS["X-Sovi-Tz"])
    check("tz_context records the harness host clock separately",
          "harness_host_offset" in tzc and "harness_host_tzname" in tzc)
    check("Europe/Copenhagen resolves to a real offset",
          _offset_for_zone("Europe/Copenhagen") in ("+0100", "+0200"),
          "got %r" % _offset_for_zone("Europe/Copenhagen"))
    check("an unknown zone name does not raise", _offset_for_zone("Not/AZone") == "")
    check("the README states the declared zone",
          "Europe/Copenhagen" in build_readme(rr3, datetime.datetime(2026, 1, 1)))
    check("the report header states the declared zone",
          "X-Sovi-Tz" in build_report(rr3, datetime.datetime(2026, 1, 1), 1.0))

    # --- claim registry hygiene: ids are permanent, so they must be unique
    check("every claim has a source and a section",
          all(c.get("claim") and c.get("source") and c.get("spec") for c in CLAIMS.values()))
    check("no suite name collides between read-only and state suites",
          not (set(DEFAULT_SUITES) & set(STATE_SUITES)))
    check("every registered suite name resolves to a function",
          all(n in SUITES for n in DEFAULT_SUITES + STATE_SUITES),
          "missing: %s" % [n for n in DEFAULT_SUITES + STATE_SUITES if n not in SUITES])
    check("round2 alias does not repeat the separately-run SetMaster matrix",
          "state_setmaster" not in ROUND2_SUITES)
    check("round2 alias still contains every other state suite",
          set(ROUND2_SUITES) == set(STATE_SUITES) - {"state_setmaster"})

    return out




def _end_to_end_test(scratch: Path) -> List[Tuple[str, bool, str]]:
    """Run a real, tiny bundle against a fake player.

    The previous self-test started a fake player, printed its port and shut it
    down without ever sending it a request. So Runner.call, write_bundle,
    verify_bundle, zipping and restore-over-HTTP had no coverage at all -- which
    is exactly where the header-redaction, ledger and MAC-idempotence bugs
    lived. The fixtures here are the cases a review reproduced: a non-ASCII
    room name, JSON with a password, a <response> element, a percent-encoded
    MAC, and a restore whose GET returns 500.
    """
    import http.server
    out: List[Tuple[str, bool, str]] = []

    def check(name: str, ok: bool, detail: str = "") -> None:
        out.append((name, bool(ok), detail))

    X = '<?xml version="1.0" encoding="UTF-8"?>'
    SYNC = X + (
        '<SyncStatus etag="886" version="4.16.22" id="10.255.255.21:11000" name="Stue Kokken"'
        ' model="N132" schemaVersion="34" mac="00:00:5E:00:53:01" group="Stue+Kokken">'
        '<slave id="10.255.255.22" port="11010" name="Kokken" model="N125" channelMode="left"/>'
        '<bluetoothOutput name="Someone iPhone"/></SyncStatus>')
    STATUS = X + ('<status etag="s1"><service>Tidal</service><state>play</state>'
                  '<volume>42</volume><album>An Album</album><artist>An Artist</artist>'
                  '<streamUrl>Capture:bluez:90%3A56%3A82%3A98%3A06%3A6E</streamUrl>'
                  '<response>ok</response></status>')
    SHARES = X + ('<shares count="1"><share><sharename>\\\\fileserver01\\music</sharename>'
                  '<username>bluesound</username><password>hunter2</password></share></shares>')
    SETTINGS_JSON = '{"wifiPassword": "hunter2", "ssid": "HomeNet", "nonce": 7}'

    class H(http.server.BaseHTTPRequestHandler):
        protocol_version = "HTTP/1.1"

        def log_message(self, *a):
            pass

        def _send(self, code, body, ctype="text/xml", extra=None):
            b = body.encode() if isinstance(body, str) else body
            self.send_response(code)
            self.send_header("Content-Type", ctype)
            self.send_header("Content-Length", str(len(b)))
            self.send_header("Set-Cookie", "session=abc123secret; Path=/")
            self.send_header("WWW-Authenticate", 'Digest realm="BluOS", nonce="deadbeef"')
            for k, v in (extra or {}).items():
                self.send_header(k, v)
            self.end_headers()
            if self.command != "HEAD":
                self.wfile.write(b)

        def do_GET(self):
            path = self.path.split("?")[0]
            if path == "/SyncStatus":
                return self._send(200, SYNC)
            if path == "/Status":
                return self._send(200, STATUS)
            if path == "/Shares":
                return self._send(200, SHARES)
            if path == "/GetSettings":
                return self._send(200, SETTINGS_JSON, "application/json")
            if path == "/BadRestore":
                return self._send(500, "nope", "text/plain")
            if path == "/GoodRestore":
                return self._send(200, X + "<ok/>")
            return self._send(404, "404 page not found", "text/plain; charset=utf-8")

        do_HEAD = do_GET

    srv = http.server.ThreadingHTTPServer(("127.0.0.1", 0), H)
    port = srv.server_address[1]
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    try:
        bundle = scratch / "e2e-bundle"
        bundle.mkdir(exist_ok=True)
        red = Redactor(redact_names=True)
        red.reserve_ipv4("127.0.0.1", "192.0.2.11")

        class _Opts:
            no_probe = False
            allow_state = True
            no_bodies = False
            preserve = None
            max_volume = 10
            redact_names = True
            keep_bt_names = False
            no_zip = True
            secret = None

        run = Runner(_Opts(), red, bundle)
        p = Player(label="A", host="127.0.0.1", port=port, reachable=True)
        run.players["A"] = p
        red.add_player_name("Stue Kokken", "Room-A")
        red.reserve_mac("00:00:5E:00:53:01", mac_placeholder(11))

        run.call(p, "/SyncStatus", note="e2e sync", expect="status=200;root=SyncStatus")
        run.call(p, "/Status", note="e2e status with a <response> element",
                 expect="status=200;root=status")
        run.call(p, "/Shares", note="e2e shares with credentials", expect="status=200")
        run.call(p, "/GetSettings", note="e2e JSON with a password", expect="status=200")
        run.call(p, "/NoSuchThing", note="e2e 404", expect="status=404")

        # a restore that fails over HTTP must be reported as failed
        run.defer_get(p, "/GoodRestore", "e2e: a restore that works")
        run.defer_get(p, "/BadRestore", "e2e: a restore that returns 500")
        broken = run.run_restores()
        check("a 500 restore is reported as failed", len(broken) == 1,
              "got %d" % len(broken))
        check("a 200 restore is reported as done",
              all(e["done"] for e in run.restores if "works" in e["description"]))

        parsed = parse_sync(run.raw_bodies[run.results[0].id])
        check("e2e parses the slave port", parsed.slave_refs[0].port == "11010",
              "got %r" % parsed.slave_refs[0].port)
        check("e2e parses the slave channelMode",
              parsed.slave_refs[0].channel_mode == "left")

        findings, keyfile = write_bundle(run, red, datetime.datetime.now(), 1.0,
                                         bundle, scratch, "e2e", True, _Opts())
        check("e2e key file is not world-readable",
              keyfile.exists() and (keyfile.stat().st_mode & 0o077) == 0,
              "mode %o" % (keyfile.stat().st_mode & 0o777) if keyfile.exists() else "missing")
        key_blob = keyfile.read_text(encoding="utf-8")
        for secret in ("hunter2", "HomeNet"):
            check("e2e key file does not contain the secret %r" % secret,
                  secret not in key_blob)
        check("e2e key file still maps addresses back", "192.0.2." in key_blob)

        blob = "\n".join(f.read_text(encoding="utf-8", errors="replace")
                          for f in bundle.rglob("*") if f.is_file())
        for secret in ("10.255.255.21", "10.255.255.22", "00:00:5E:00:53:01", "fileserver01",
                       "hunter2", "HomeNet", "Someone iPhone", "abc123secret",
                       "deadbeef", "Stue Kokken"):
            check("e2e bundle does not contain %r" % secret, secret not in blob)
        check("e2e percent-encoded MAC was redacted",
              "90%3A56%3A82" not in blob)
        check("e2e <response> element survived redaction intact",
              "<response>ok</response>" in blob,
              "AUTH_HDR_RE used to rewrite this into a broken attribute")
        check("e2e Set-Cookie value was redacted by header name",
              "session=abc123secret" not in blob)
        check("e2e verifier reports no findings", not findings, "; ".join(findings[:3]))
        for name in ("REPORT.md", "MANIFEST.json", "FINDINGS.md", "SAMPLES.md",
                     "REDACTIONS.md", "README.md"):
            check("e2e bundle contains %s" % name, (bundle / name).exists())
        manifest = json.loads((bundle / "MANIFEST.json").read_text(encoding="utf-8"))
        check("e2e manifest records the probes", len(manifest["probes"]) >= 5)
        check("e2e manifest does not carry raw bodies",
              "body_full" not in json.dumps(manifest))
        check("e2e SyncStatus capture is marked as modified by redaction",
              any(pr["path"] == "/SyncStatus" and not pr["verbatim"]
                  for pr in manifest["probes"]))
        check("e2e 404 capture is verbatim",
              any(pr["path"] == "/NoSuchThing" and pr["verbatim"]
                  for pr in manifest["probes"]))
    finally:
        srv.shutdown()
    return out


def run_selftest() -> int:
    import http.server

    class Handler(http.server.BaseHTTPRequestHandler):
        protocol_version = "HTTP/1.1"

        def log_message(self, *a):
            pass

        def _send(self, code, body: bytes, ctype="text/xml"):
            self.send_response(code)
            self.send_header("Content-Type", ctype)
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def do_GET(self):
            path = self.path.split("?")[0]
            table = {
                "/SyncStatus": FAKE_SYNCSTATUS, "/Status": FAKE_STATUS,
                "/Shares": FAKE_SHARES, "/Services": FAKE_SERVICES,
                "/GitVersion": '<?xml version="1.0"?><gitversion>abc</gitversion>',
                "/Presets": '<?xml version="1.0"?><presets/>',
                "/Playlist": '<?xml version="1.0"?><playlist length="0"/>',
                "/Volume": '<?xml version="1.0"?><volume db="-20">30</volume>',
                "/Name": '<?xml version="1.0"?><name>Stue</name>',
                "/Alarms": '<?xml version="1.0"?><alarms/>',
                "/BTDevices": '<?xml version="1.0"?><bluetooth/>',
                "/GetUnpairedSlaves": '<?xml version="1.0"?><unpairedSlaves/>',
                "/Browse": '<?xml version="1.0"?><browse type="menu"/>',
            }
            if path in table:
                self._send(200, table[path].encode())
            else:
                self._send(404, b"404 page not found", "text/plain; charset=utf-8")

        do_HEAD = do_GET
        do_POST = do_GET
        do_OPTIONS = do_GET
        do_PUT = do_GET
        do_DELETE = do_GET

    srv = http.server.ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    port = srv.server_address[1]
    t = threading.Thread(target=srv.serve_forever, daemon=True)
    t.start()

    print("self-test: fake player on 127.0.0.1:%d" % port)
    red = Redactor(redact_names=False)

    sample = FAKE_SYNCSTATUS + "\n" + FAKE_SHARES + "\n<!-- contact bob.smith@gmail.com -->"
    scrubbed = red.scrub(sample)
    parts = scrubbed.split("\n")
    problems = []
    for needle in ("10.255.255.21", "10.255.255.22", "00:00:5E:00:53:01",
                   "fileserver01", "hunter2", "bob.smith@gmail.com"):
        if needle in scrubbed:
            problems.append("redactor failed to remove %r" % needle)
    if "192.0.2." not in scrubbed:
        problems.append("no IPv4 placeholder appeared")
    if "02:00:00:00:00:" not in scrubbed:
        problems.append("no MAC placeholder appeared")
    for part in parts[:2]:
        if safe_parse_xml(part) is None:
            problems.append("redacted XML no longer parses: %s" % part[:120])

    print("\n--- redactor input")
    for line in sample.split("\n"):
        print("  " + line)
    print("\n--- redactor output")
    for line in scrubbed.split("\n"):
        print("  " + line)

    srv.shutdown()

    import tempfile
    scratch_root = Path(tempfile.mkdtemp(prefix="bluos-probe-e2e-"))
    results = _unit_tests()
    results += _end_to_end_test(scratch_root)
    failed = [(n, d) for n, ok, d in results if not ok]
    print("\n--- harness regression tests")
    for name, ok, detail in results:
        if not ok:
            print("  FAIL  %s%s" % (name, ("  [%s]" % detail) if detail else ""))
    print("  %d passed, %d failed" % (len(results) - len(failed), len(failed)))

    if problems or failed:
        print("\nHARNESS CHECK FAILED -- do not trust a run from this build")
        for pb in problems:
            print("  - %s" % pb)
        return 1
    print("\nHarness check passed. %d assertions covering the response parsers, the "
          "redactor," % len(results))
    print("the expectation matcher, claim verdicts, safety gating, the restore ledger,")
    print("the LSDP codec and argument parsing. This exercised THIS SCRIPT, not BluOS:")
    print("no bundle was written and no protocol evidence was produced.")
    import shutil
    shutil.rmtree(scratch_root, ignore_errors=True)
    return 0


# --------------------------------------------------------------------------
# CLI
# --------------------------------------------------------------------------

SUITES: Dict[str, Callable[[Runner], Any]] = {
    "env": suite_env,
    "transport": suite_transport,
    "ports": suite_ports,
    "longpoll": suite_longpoll,
    "errors": suite_errors,
    "claims": suite_claims,
    "artwork": suite_artwork,
    "browse": suite_browse,
    "settings": suite_settings,
    "discovery": suite_discovery,
    "stability": suite_stability,
}
DEFAULT_SUITES = ["env", "transport", "ports", "longpoll", "errors", "claims",
                  "inputs", "artwork", "browse", "settings", "discovery", "stability"]
STATE_SUITES = ["state_capture", "state_volume", "state_playback", "state_sleep", "state_name",
                "state_setting", "state_preset", "state_source",
                "state_setmaster", "state_grouping"]
# `state_setmaster` is deliberately run on its own first (see RUNBOOK.md).
# The `round2` alias means "the rest of round 2" and must not repeat that
# topology matrix. Keep STATE_SUITES as the complete registry so `everything`
# and explicit suite selection still include it.
ROUND2_SUITES = [name for name in STATE_SUITES if name != "state_setmaster"]


class PlayerSpecError(ValueError):
    pass


def _auto_label(taken: set) -> str:
    """A, B, ... Z, then AA, AB. chr(ord('A') + i) produced '[' and '\\' past 26."""
    i = 0
    while True:
        n, name = i, ""
        while True:
            name = chr(ord("A") + n % 26) + name
            n = n // 26 - 1
            if n < 0:
                break
        if name not in taken:
            return name
        i += 1


def parse_players(values: Sequence[str],
                  default_port: int = CONTROL_PORT) -> List[Tuple[str, str, int]]:
    """LABEL=HOST[:PORT], HOST[:PORT], or [v6addr]:PORT.

    Colliding labels used to overwrite each other in run.players, so a player
    silently vanished from the run; and a bare IPv6 address was split on its
    last colon, giving host "fe80:" and port 1.
    """
    out: List[Tuple[str, str, int]] = []
    seen_labels: set = set()
    for v in values:
        v = v.strip()
        label, addr = ("", v)
        if "=" in v and not v.startswith("["):
            label, addr = v.split("=", 1)
        addr = addr.strip()
        port = default_port
        if addr.startswith("["):                     # [2001:db8::1]:11000
            end = addr.find("]")
            if end < 0:
                raise PlayerSpecError("%r: missing closing ] in the IPv6 address" % v)
            host = addr[1:end]
            rest = addr[end + 1:]
            if rest.startswith(":"):
                port = _parse_port(rest[1:], v)
        elif addr.count(":") > 1:                    # bare IPv6, no port
            host = addr
        elif ":" in addr:
            host, port_s = addr.rsplit(":", 1)
            port = _parse_port(port_s, v)
        else:
            host = addr
        host = host.strip()
        if not host:
            raise PlayerSpecError("%r: no host" % v)
        label = (label.strip() or _auto_label(seen_labels)).upper()
        if label in seen_labels:
            raise PlayerSpecError(
                "duplicate player label %r. Labels identify players throughout the "
                "run, so a collision would silently drop one of them." % label)
        seen_labels.add(label)
        out.append((label, host, port))
    return out


def _parse_port(raw: str, spec: str) -> int:
    try:
        port = int(raw)
    except ValueError:
        raise PlayerSpecError("%r: %r is not a port number" % (spec, raw))
    if not 1 <= port <= 65535:
        raise PlayerSpecError("%r: port %d is out of range" % (spec, port))
    return port




def write_bundle(run: "Runner", red: Redactor, started: datetime.datetime,
                 elapsed: float, bundle: Path, outroot: Path, stamp: str,
                 synthetic: bool, opts: Any) -> Tuple[List[str], Path]:
    """Serialise everything, then re-scan the result for anything sensitive.

    Kept out of main() deliberately: this is where the redaction guarantee is
    actually enforced, and it should be readable end to end without scrolling
    past argument parsing and suite dispatch.
    """
    # -- write the bundle
    manifest = {
        "harness": "bluos-probe.py",
        "version": VERSION,
        "synthetic_target": synthetic,
        "timezone": tz_context(),
        "body_sha256_is_of": "the redacted body as written to raw/. Digests of the "
                             "original bodies are in the do-not-share key file, because "
                             "for a structured body they would recover the redacted values.",
        "started": started.isoformat(),
        "duration_s": round(elapsed, 1),
        "options": json.loads(red.scrub(json.dumps(
            {k: v for k, v in vars(opts).items() if k != "secret"}, ensure_ascii=False))),
        "secrets_supplied": len(opts.secret or []),
        "players": [
            {k: (("Room-" + p.label) if (k == "name" and red.redact_names) else red.scrub(v) if isinstance(v, str) else v)
             for k, v in asdict(p).items() if k != "host"}
            for p in run.players.values()
        ],
        "facts": json.loads(red.scrub(json.dumps(run.facts, ensure_ascii=False))),
        "redaction": red.summary(),
        "probes": [asdict(pr) for pr in run.results],
    }
    # Defence in depth: Probe fields are redacted at capture time, but a field
    # added later must not be able to bypass that contract.  Scrub the complete
    # serialised manifest once more immediately before it becomes shareable.
    manifest_blob = red.scrub(json.dumps(manifest, indent=2, ensure_ascii=False))
    manifest_clean = json.loads(manifest_blob)
    manifest_clean["redaction"] = red.summary()
    manifest_blob = red.scrub(json.dumps(manifest_clean, indent=2, ensure_ascii=False))
    (bundle / "MANIFEST.json").write_text(manifest_blob, encoding="utf-8")
    (bundle / "REPORT.md").write_text(build_report(run, started, elapsed), encoding="utf-8")
    (bundle / "SHAPES.md").write_text(build_shapes(run), encoding="utf-8")
    (bundle / "FINDINGS.md").write_text(
        build_findings(run, started, bundle.name), encoding="utf-8")
    (bundle / "SAMPLES.md").write_text(build_samples(run), encoding="utf-8")
    capture_library = write_capture_library(run, bundle)
    (bundle / "CAPTURES.md").write_text(
        build_captures_index(run, capture_library), encoding="utf-8")
    (bundle / "README.md").write_text(build_readme(run, started), encoding="utf-8")

    findings = verify_bundle(bundle, red)
    (bundle / "REDACTIONS.md").write_text(build_redactions(run, findings), encoding="utf-8")

    keyfile = outroot / ("DO-NOT-SHARE-key-%s.json" % stamp)
    key = red.key_material()
    key["wire_body_sha256"] = {
        "note": "SHA-256 of the ORIGINAL response bodies. Deliberately kept out of "
                "the bundle: for a templated body such as /SyncStatus the only "
                "unknown is the address, so the digest recovers it by brute force "
                "in milliseconds.",
        "digests": run.wire_hashes,
    }
    # 0600: the default umask usually leaves this world-readable, and --out
    # defaults to the current directory, which may well be a synced folder.
    if keyfile.exists():
        keyfile.unlink()
    fd = os.open(str(keyfile), os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(fd, "w", encoding="utf-8") as fh:
        json.dump(key, fh, indent=2, ensure_ascii=False)

    return findings, keyfile


def _volume_level(raw: str) -> int:
    """0-100. An unvalidated cap meant --max-volume 250 sent level=250, which
    the device clamps to maximum -- the opposite of a ceiling."""
    try:
        v = int(raw)
    except ValueError:
        raise argparse.ArgumentTypeError("%r is not an integer" % raw)
    if not 0 <= v <= 100:
        raise argparse.ArgumentTypeError("must be between 0 and 100, got %d" % v)
    return v


def build_parser() -> argparse.ArgumentParser:
    ap = argparse.ArgumentParser(
        description="Probe harness for the BluOS HTTP API. Read-only unless "
                    "--allow-state is given.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="Without --allow-state only read-only requests are issued. With it, "
               "reversible changes are made, snapshotted and restored. Each undo "
               "re-reads the device and fails loudly if it did not take; anything that "
               "could not be restored is listed at the end and sets a non-zero exit "
               "code. Nothing destructive is implemented.")
    ap.add_argument("--player", action="append", metavar="LABEL=HOST[:PORT]",
                    help="repeatable; LABEL= is optional and defaults to A, B, C...")
    ap.add_argument("--discover", action="store_true",
                    help="find players over LSDP instead of naming them")
    ap.add_argument("--suite", default="all",
                    help="comma-separated suite names, or 'all' (round 1, read-only), "
                         "'round2' (state-changing remainder; excludes state_setmaster, "
                         "which should be run separately first), or 'everything'")
    ap.add_argument("--out", default=".", help="where to write the bundle")
    ap.add_argument("--secret", action="append", metavar="STRING",
                    help="repeatable; an exact string to scrub everywhere "
                         "(NAS hostname, SSID, a person's name...)")
    ap.add_argument("--redact-names", action="store_true",
                    help="also replace player and room names with Room-A, Room-B...")
    ap.add_argument("--keep-bt-names", action="store_true",
                    help="do not redact Bluetooth device names (they often contain a person's name)")
    ap.add_argument("--allow-state", action="store_true",
                    help="enable round 2: reversible state changes (playback, volume, "
                         "grouping, settings). Every change is snapshotted and restored.")
    ap.add_argument("--max-volume", type=_volume_level, default=10, metavar="LEVEL",
                    help="hard ceiling for any volume this run sets, 0-100 scale (default 10). "
                         "Also applied before any suite that can start audio.")
    ap.add_argument("--preserve", action="append", metavar="LABEL",
                    help="repeatable; a player label that must never be written to, "
                         "even in round 2")
    ap.add_argument("--breadth", type=int, default=2, metavar="N",
                    help="how many players get tests whose answer cannot vary between "
                         "players on the same firmware (default 2: one to establish it, "
                         "one to catch a mixed-firmware fleet). Per-player inventory and "
                         "capture are always run on every player.")
    ap.add_argument("--no-probe", action="store_true",
                    help="run only the 'read' safety class, dropping bare-path existence probes")
    ap.add_argument("--slow", action="store_true",
                    help="include long-running checks (timeout ceiling up to 300 s)")
    ap.add_argument("--concurrency-max", type=int, default=32,
                    help="highest simultaneous long-poll count to try (default 32). "
                         "This is real load: while the ladder runs it can briefly "
                         "starve the official app or a Home Assistant integration. "
                         "Set 0 to skip the ladder.")
    ap.add_argument("--browse-depth", type=int, default=3, help="browse crawl depth (default 3)")
    ap.add_argument("--browse-fanout", type=int, default=6, help="children followed per node (default 6)")
    ap.add_argument("--browse-nodes", type=int, default=60, help="max browse nodes visited (default 60)")
    ap.add_argument("--no-bodies", action="store_true", help="record metadata only, no response bodies")
    ap.add_argument("--no-zip", action="store_true", help="do not create the .zip")
    ap.add_argument("--port-control", type=int, default=CONTROL_PORT,
                    help="control port (default 11000; CI580 secondary zones are offset by 10)")
    ap.add_argument("--port-settings", type=int, default=SETTINGS_PORT,
                    help="settings port (default 11001)")
    ap.add_argument("--port-web", type=int, default=WEB_PORT, help="web/legacy port (default 80)")
    ap.add_argument("--timezone", default=PROBE_TZ, metavar="ZONE",
                    help="zone declared to the device in X-Sovi-Tz (default %s). "
                         "Affects time-dependent answers such as alarm times, so it is "
                         "recorded in every bundle." % PROBE_TZ)
    ap.add_argument("--verify-harness", "--selftest", dest="verify_harness",
                    action="store_true",
                    help="check the harness and the redactor itself. Produces NO bundle "
                         "and NO protocol evidence -- it exercises this script, not BluOS.")
    return ap


def resolve_targets(opts, ap: argparse.ArgumentParser) -> List[Tuple[str, str, int]]:
    specs: List[Tuple[str, str, int]] = []
    if opts.player:
        try:
            specs = parse_players(opts.player, opts.port_control)
        except PlayerSpecError as exc:
            ap.error(str(exc))
    if opts.discover or not specs:
        print("Discovering players over LSDP (UDP %d)..." % LSDP_PORT)
        discovery_diag: List[str] = []
        found = lsdp_discover(diagnostics=discovery_diag)
        if found:
            taken = {sp[0] for sp in specs}
            for addr, name, port in found:
                if any(sp[1] == addr and sp[2] == port for sp in specs):
                    continue
                label = _auto_label(taken)
                taken.add(label)
                specs.append((label, addr, port))
                print("  found %s at %s:%d" % (name or "(unnamed)", addr, port))
        else:
            print("  nothing answered.")
            for line in discovery_diag:
                print("  diagnostic: %s" % line)
    if not specs:
        ap.error("no players. Use --player A=192.168.1.10, or --discover on the same subnet.")
    return specs


def resolve_suites(opts, ap: argparse.ArgumentParser) -> List[str]:
    choice = opts.suite.strip()
    if choice == "all":
        wanted = list(DEFAULT_SUITES)
    elif choice == "round2":
        wanted = list(ROUND2_SUITES)
    elif choice == "everything":
        wanted = DEFAULT_SUITES + STATE_SUITES
    else:
        wanted = [x.strip() for x in choice.split(",") if x.strip()]
    unknown = [x for x in wanted if x not in SUITES]
    if unknown:
        ap.error("unknown suite(s): %s" % ", ".join(unknown))
    state_wanted = [x for x in wanted if x in STATE_SUITES]
    if state_wanted and not opts.allow_state:
        ap.error("suite(s) %s change player state. Re-run with --allow-state once you "
                 "are happy with --max-volume %d and --preserve %s."
                 % (", ".join(state_wanted), opts.max_volume,
                    ", ".join(opts.preserve or []) or "(none)"))
    return wanted


def main(argv: Optional[List[str]] = None) -> int:
    global CONTROL_PORT, SETTINGS_PORT, WEB_PORT
    ap = build_parser()
    opts = ap.parse_args(argv)

    if opts.verify_harness:
        return run_selftest()

    CONTROL_PORT, SETTINGS_PORT, WEB_PORT = opts.port_control, opts.port_settings, opts.port_web
    SOVI_HEADERS["X-Sovi-Tz"] = opts.timezone
    specs = resolve_targets(opts, ap)
    wanted = resolve_suites(opts, ap)

    started = datetime.datetime.now()
    stamp = started.strftime("%Y%m%dT%H%M%S")
    outroot = Path(opts.out).expanduser().resolve()
    outroot.mkdir(parents=True, exist_ok=True)

    def _loopback(h: str) -> bool:
        try:
            return ipaddress.ip_address(h).is_loopback
        except ValueError:
            return h.lower() in ("localhost", "localhost.localdomain")

    synthetic = all(_loopback(h) for _, h, _ in specs)
    bundle = outroot / ("bluos-probe-%s%s" % ("SYNTHETIC-" if synthetic else "", stamp))
    suffix = 1
    while bundle.exists():          # two runs started in the same second
        suffix += 1
        bundle = outroot / ("bluos-probe-%s%s-%d"
                            % ("SYNTHETIC-" if synthetic else "", stamp, suffix))
    bundle.mkdir()
    if synthetic:
        print("\n*** SYNTHETIC TARGET: every address is loopback. This bundle is")
        print("*** labelled accordingly and must never be cited as protocol evidence.\n")

    red = Redactor(redact_names=opts.redact_names, redact_bt_names=not opts.keep_bt_names)
    run = Runner(opts, red, bundle)
    run.synthetic = synthetic

    state_wanted = [w for w in wanted if w in STATE_SUITES]
    print("bluos-probe %s -- %s" % (
        VERSION,
        "STATE-CHANGING run (%s); every change is restored and the restore verified"
        % ", ".join(state_wanted) if state_wanted else "read-only run"))
    print("bundle: %s" % bundle)
    print("suites: %s" % ", ".join(wanted))
    print("safety: read%s%s\n" % ("" if opts.no_probe else " + probe",
                                  " + state" if state_wanted else ""))

    t0 = time.monotonic()
    preflight(run, specs)
    if not run.targets():
        print("\nNo player answered /SyncStatus. Nothing to probe.")
        return 2

    interrupted = False
    try:
        for name in wanted:
            try:
                SUITES[name](run)
            except KeyboardInterrupt:
                interrupted = True
                print("\ninterrupted -- restoring, then writing what was collected")
                break
            except Exception as exc:  # a broken suite must not lose the run
                import traceback
                run.note(name, "suite raised an exception and was abandoned",
                         traceback.format_exc()[-3000:], verdict="ERROR")
                print("  !! suite %s failed: %s" % (name, exc))
                # Restore NOW, not at the end of the run. Otherwise the next
                # suite snapshots a half-grouped fleet as its own baseline and
                # every case it runs is measured from the wrong start.
                broken = run.run_restores()
                if broken:
                    run.note(name, "%d restore(s) failed after that crash" % len(broken),
                             "\n".join("- %s: %s" % (e["description"], e["error"])
                                        for e in broken), verdict="ERROR")
    finally:
        # Runs on a clean finish, an exception, and Ctrl-C alike. Restores are
        # idempotent and skip anything a suite already put back, so the normal
        # path costs nothing.
        failed_restores = run.run_restores()
    elapsed = time.monotonic() - t0

    for entry in run.restores:
        run.note("restore", entry["description"],
                 "restored" if entry["done"] else ("FAILED: " + (entry["error"] or "not run")),
                 verdict="OK" if entry["done"] else "ERROR")

    findings, keyfile = write_bundle(run, red, started, elapsed, bundle,
                                     outroot, stamp, synthetic, opts)
    counts: Dict[str, int] = {}
    for pr in run.results:
        counts[pr.verdict] = counts.get(pr.verdict, 0) + 1

    print("\n" + "=" * 72)
    print("%d probes in %.1f s -- %s" % (
        len(run.results), elapsed, ", ".join("%s %d" % kv for kv in sorted(counts.items()))))
    print("bundle:  %s" % bundle)
    print("key:     %s   (keep this, do not share it)" % keyfile.name)

    if findings:
        print("\n!! REDACTION CHECK FAILED -- %d finding(s):" % len(findings))
        for f in findings[:20]:
            print("   %s" % f)
        print("   Do not share the bundle. Add the missed values with --secret and re-run,")
        print("   or edit the files listed above by hand.")
    else:
        print("redaction check: clean -- no address, MAC or supplied secret survived")

    if not opts.no_zip and not findings:
        zpath = outroot / ("%s.zip" % bundle.name)
        with zipfile.ZipFile(zpath, "w", zipfile.ZIP_DEFLATED) as z:
            for item in sorted(bundle.rglob("*")):
                if item.is_file():
                    z.write(item, item.relative_to(outroot))
        print("zip:     %s  (%.1f KB) -- this is the file to share" % (
            zpath.name, zpath.stat().st_size / 1024.0))
    elif findings:
        print("zip:     not created, because the redaction check failed")

    if failed_restores:
        print("\n!! %d RESTORE(S) DID NOT COMPLETE -- the fleet may not be as you left it:"
              % len(failed_restores))
        for e in failed_restores:
            print("   %s -- %s" % (e["description"], e["error"] or "not run"))
        print("   Put these back by hand, or re-run the same suite to let it try again.")

    unexpected = counts.get("UNEXPECTED", 0)
    if unexpected:
        print("\n%d result(s) did not match the specification. REPORT.md lists them first." % unexpected)
    if interrupted:
        print("\nRun was interrupted, so coverage is partial.")

    # Distinct codes, because a redaction failure and a restore failure need
    # different responses and a script cannot tell them apart from 0.
    #   0 clean   3 a restore did not complete   4 redaction findings
    #   7 both    130 interrupted
    if findings and failed_restores:
        return 7
    if findings:
        return 4
    if failed_restores:
        return 3
    return 130 if interrupted else 0




# ==========================================================================
# ROUND 2 -- reversible state changes. Requires --allow-state.
#
# Every suite here snapshots what it will disturb, changes it, reads the result
# back, and restores explicitly. Restoration is verified, not assumed, and a
# failed restore is reported as an ERROR rather than passed over.
# ==========================================================================

@dataclass
class Snapshot:
    label: str
    volume: Optional[int] = None
    mute: Optional[str] = None
    state: str = ""
    service: str = ""
    songid: str = ""
    secs: Optional[int] = None
    name: str = ""
    sleep: str = ""
    master: str = ""
    slaves: List[str] = field(default_factory=list)
    slave_refs: List[SlaveRef] = field(default_factory=list)
    group: str = ""
    raw_status: str = ""
    raw_sync: str = ""


def take_snapshot(p: Player) -> Snapshot:
    """Everything a state suite might need to put back. No probe is recorded:
    a snapshot is bookkeeping, not evidence."""
    snap = Snapshot(label=p.label)
    st = http_call(p.host, p.port, "/Status", timeout=10)
    sy = http_call(p.host, p.port, "/SyncStatus", timeout=10)
    stext = st.body.decode("utf-8", "replace") if st.body else ""
    sytext = sy.body.decode("utf-8", "replace") if sy.body else ""
    snap.raw_status, snap.raw_sync = stext, sytext

    snap.volume = element_int(stext, "volume")
    snap.mute = element_text(stext, "mute")
    snap.state = element_text(stext, "state")
    snap.service = element_text(stext, "service")
    snap.songid = element_text(stext, "songid")
    snap.secs = element_int(stext, "secs")
    snap.sleep = element_text(stext, "sleep")

    info = parse_sync(sytext)
    snap.name, snap.group = info.name, info.group
    snap.master, snap.slaves = info.master, info.slaves
    snap.slave_refs = info.slave_refs
    return snap


def settle(run: Runner, p: Player, what: str = "/SyncStatus", tries: int = 3,
           delay: float = 1.2, note: str = "") -> List[Probe]:
    """Grouping and source changes complete asynchronously, and the immediate
    response is sometimes the pre-call state with the previous etag. So read
    more than once and record every read."""
    out = []
    for i in range(tries):
        if i:
            time.sleep(delay)
        out.append(run.call(p, what, note="%s -- settle read %d/%d" % (note or what, i + 1, tries),
                            spec_ref="5.3", save=(i == tries - 1), quiet=(i < tries - 1)))
    return out


# --------------------------------------------------------------------------
# Group operations
#
# Teardown, rebuild and verification lived in three near-identical copies: the
# pre-clean in state_grouping, the final restore in both grouping suites, and
# the deferred undo. A restore path must not be able to drift from the path
# that set the state up, so there is now one of each.
# --------------------------------------------------------------------------

def slave_query(refs: Sequence[SlaveRef], fallback_port: int) -> str:
    """`slaves=` and `ports=` built from what the master actually reported.

    The port used to come from a default argument bound at definition time, so
    --port-control never reached it and a CI580 secondary zone was rebuilt
    against 11000.
    """
    return "slaves=%s&ports=%s" % (
        ",".join(r.id for r in refs),
        ",".join(r.with_port(fallback_port) for r in refs))


def drop_slaves(run: "Runner", p: Player, refs: Sequence[SlaveRef]) -> None:
    if refs:
        run.write(p, "/RemoveSlave?" + slave_query(refs, CONTROL_PORT),
                  "teardown: free the slaves of %s" % p.label)


def add_slaves(run: "Runner", p: Player, refs: Sequence[SlaveRef]) -> None:
    """Rebuild with the exact port and channelMode each slave was found with."""
    if not refs:
        return
    query = slave_query(refs, CONTROL_PORT)
    modes = {r.channel_mode for r in refs if r.channel_mode}
    if len(modes) == 1:
        query += "&channelMode=" + urllib.parse.quote(modes.pop())
    run.write(p, "/AddSlave?" + query, "rebuild the original group under %s" % p.label)
    for r in refs:
        if r.channel_mode and len(refs) > 1:
            run.write(p, "/AddSlave?slave=%s&port=%s&channelMode=%s"
                      % (r.id, r.with_port(CONTROL_PORT), urllib.parse.quote(r.channel_mode)),
                      "restore channelMode=%s for one slave of %s" % (r.channel_mode, p.label))


def group_conflicts(run: "Runner") -> List[str]:
    """Writable players sharing a group with a player this run may not write to.

    Teardown frees every slave of a writable master, which would write to a
    --preserve'd or unlisted player; and nothing can rebuild a group whose
    master is not writable. Both are refusals, not warnings.
    """
    writable = {p.label for p in run.writable()}
    known = {p.host: p.label for p in run.targets()}
    problems: List[str] = []
    for p in run.targets():
        info = fetch_sync(p)
        if not info.reachable:
            continue
        for ref in info.slave_refs:
            slave_label = known.get(ref.id.split(":")[0])
            if p.label in writable and (slave_label is None or slave_label not in writable):
                problems.append(
                    "%s is a master of %s, which this run may not write to"
                    % (p.label, slave_label or ref.id))
            if slave_label in writable and p.label not in writable:
                problems.append(
                    "%s is a slave of %s, which this run may not write to"
                    % (slave_label, p.label))
    return sorted(set(problems))


def teardown_groups(run: "Runner", ps: Sequence[Player],
                    settle_s: float = 2.0) -> Tuple[List[str], List[str]]:
    """Free every player.

    Returns (still_grouped, needed_fallback). The fallback is a bare
    /SetMaster, which is itself the endpoint under test in one suite, so a case
    that relied on it must be treated as suspect -- which requires knowing it
    happened, not merely that the player ended up free.
    """
    for p in ps:
        info = fetch_sync(p)
        if info.reachable:
            drop_slaves(run, p, info.slave_refs)
    time.sleep(settle_s)
    fallback: List[str] = []
    for p in ps:
        info = fetch_sync(p)
        if info.reachable and info.master:
            fallback.append(p.label)
            run.write(p, "/SetMaster", "teardown fallback: %s leaves its group" % p.label)
    time.sleep(settle_s)
    still = [p.label for p in ps
             if (lambda i: i.grouped or not i.reachable)(fetch_sync(p))]
    return still, fallback


def rebuild_groups(run: "Runner", baseline: Dict[str, "Snapshot"],
                   settle_s: float = 2.0) -> None:
    for lbl, snap in baseline.items():
        p = run.player(lbl)
        if p and snap.slave_refs:
            add_slaves(run, p, snap.slave_refs)
    time.sleep(settle_s)


def topology_matches(run: "Runner", baseline: Dict[str, "Snapshot"]) -> Tuple[bool, str]:
    rows = []
    ok = True
    for lbl, snap in baseline.items():
        p = run.player(lbl)
        now = fetch_sync(p) if p else SyncInfo(reachable=False)
        before = (snap.master, tuple(sorted(snap.slaves)))
        same = now.reachable and now.topology == before
        ok = ok and same
        rows.append("%s: before master=%s slaves=%s / after master=%s slaves=%s%s"
                    % (lbl, snap.master or "-", snap.slaves,
                       now.master or ("unreachable" if not now.reachable else "-"),
                       now.slaves, "" if same else "   <-- differs"))
    return ok, "\n".join(rows)


def defer_topology(run: Runner, ps: List[Player],
                   baseline: Dict[str, Snapshot]) -> Dict[str, Any]:
    """Register the undo for grouping BEFORE anything is grouped, so a crash or
    Ctrl-C halfway through a matrix still leaves the fleet as it was found."""
    def undo() -> None:
        _still, _fb = teardown_groups(run, ps)
        rebuild_groups(run, baseline)

    described = ", ".join("%s<-%s" % (lbl, "+".join(sn.slaves))
                          for lbl, sn in baseline.items() if sn.slaves) or "all standalone"
    return run.defer("restore the original topology (%s)" % described, undo)


def cap_volume(run: Runner, p: Player, snap: Snapshot) -> None:
    """Bring a player down to --max-volume before a suite that can start audio.

    The cap used to apply only inside state_volume, so state_playback,
    state_preset and state_source all started audio at whatever level the
    player happened to be at.
    """
    cap = run.opts.max_volume
    if snap.volume is None or snap.volume < 0 or snap.volume <= cap:
        return
    run.defer_get(p, "/Volume?level=%d" % snap.volume,
                  "%s: restore volume to %d" % (p.label, snap.volume))
    run.write(p, "/Volume?level=%d" % cap,
              "cap %s at level %d before starting audio (was %d)" % (p.label, cap, snap.volume))
    run.note(run.current_suite,
             "%s volume lowered from %d to the --max-volume ceiling of %d"
             % (p.label, snap.volume, cap),
             "restored from the ledger at the end of the run")


def defer_transport(run: Runner, p: Player, snap: Snapshot) -> Dict[str, Any]:
    def undo() -> None:
        if snap.state in ("play", "stream"):
            http_call(p.host, p.port, "/Play", timeout=15)
        elif snap.state in ("pause", "stop"):
            http_call(p.host, p.port, "/Pause", timeout=15)
    return run.defer("%s: restore transport state to '%s'" % (p.label, snap.state or "unknown"),
                     undo)


def suite_state_volume(run: Runner) -> None:
    """Volume, capped. Never exceeds --max-volume, always restored."""
    run.current_suite = "state_volume"
    run.banner("state_volume -- level, mute polarity, tell_slaves (capped at %d)" % run.opts.max_volume)
    cap = run.opts.max_volume
    for p in run.writable():
        before = take_snapshot(p)
        if before.volume is None:
            run.note("state_volume", "%s: could not read a starting volume, skipped" % p.label,
                     verdict="ERROR")
            continue
        if before.volume == -1:
            run.note("state_volume", "%s reports volume -1 (fixed volume), skipped" % p.label)
            continue
        run.note("state_volume", "%s starting volume %d, mute=%s" % (p.label, before.volume, before.mute))
        undo_vol = run.defer_get(p, "/Volume?level=%d" % before.volume,
                                 "%s: restore volume to %d" % (p.label, before.volume))
        undo_mute = run.defer_get(p, "/Volume?mute=%s" % (before.mute or "0"),
                                  "%s: restore mute=%s" % (p.label, before.mute or "0"))

        levels = sorted({1, max(1, cap // 2), cap})
        for lv in levels:
            run.call(p, "/Volume?level=%d" % lv, safety=SAFETY_STATE,
                     note="set absolute level %d" % lv, spec_ref="4")
            run.call(p, "/Volume", note="read back after level=%d" % lv, spec_ref="4", save=False)

        # mute polarity: the vendor document has this inverted (spec 4)
        run.call(p, "/Volume?mute=1", safety=SAFETY_STATE, note="mute=1", spec_ref="4",
                 claim="C-36-mute-polarity")
        m1 = run.call(p, "/Volume", note="read back after mute=1", spec_ref="4", save=False)
        run.call(p, "/Volume?mute=0", safety=SAFETY_STATE, note="mute=0", spec_ref="4")
        m0 = run.call(p, "/Volume", note="read back after mute=0", spec_ref="4", save=False)
        muted_after_1 = 'mute="1"' in body_of(run, m1)
        unmuted_after_0 = 'mute="0"' in body_of(run, m0)
        run.note("state_volume",
                 "%s mute polarity: mute=1 -> %s, mute=0 -> %s" % (
                     p.label, "muted" if muted_after_1 else "NOT muted",
                     "unmuted" if unmuted_after_0 else "NOT unmuted"),
                 "confirms the app and contradicts CI API v1.7 3.1"
                 if (muted_after_1 and unmuted_after_0) else "does NOT match the app's behaviour",
                 verdict="OK" if (muted_after_1 and unmuted_after_0) else "UNEXPECTED")

        # relative dB, documented as official-only
        run.call(p, "/Volume?db=-2", safety=SAFETY_STATE, note="relative db=-2", spec_ref="4")
        run.call(p, "/Volume?db=2", safety=SAFETY_STATE, note="relative db=+2", spec_ref="4")
        run.call(p, "/Volume", note="read back after relative db", spec_ref="4", save=False)

        # restore, then verify
        run.call(p, "/Volume?level=%d" % before.volume, safety=SAFETY_STATE,
                 note="RESTORE volume to %d" % before.volume, spec_ref="4", save=False)
        run.call(p, "/Volume?mute=%s" % (before.mute or "0"), safety=SAFETY_STATE,
                 note="RESTORE mute state", spec_ref="4", save=False)
        undo_vol["done"] = undo_mute["done"] = True
        after = take_snapshot(p)
        ok = (after.volume == before.volume and after.mute == before.mute)
        run.note("state_volume", "%s restore verified: %s" % (p.label, "yes" if ok else "NO"),
                 "before level=%s mute=%s / after level=%s mute=%s" % (
                     before.volume, before.mute, after.volume, after.mute),
                 verdict="OK" if ok else "ERROR")


def suite_state_playback(run: Runner) -> None:
    """Transport control and the polymorphic play response."""
    run.current_suite = "state_playback"
    run.banner("state_playback -- pause, play, stop, toggle; play-response roots")
    for p in run.writable():
        before = take_snapshot(p)
        undo_tp = defer_transport(run, p, before)
        cap_volume(run, p, before)
        run.note("state_playback", "%s starting state=%s service=%s secs=%s" % (
            p.label, before.state, before.service, before.secs))

        run.call(p, "/Pause", safety=SAFETY_STATE, note="pause", spec_ref="3;7.3")
        run.call(p, "/Status", note="state after /Pause", spec_ref="2.2", save=False)
        run.call(p, "/Play", safety=SAFETY_STATE, note="bare /Play resumes", spec_ref="3;7.3")
        run.call(p, "/Status", note="state after /Play", spec_ref="2.2", save=False)
        run.call(p, "/Pause?toggle=1", safety=SAFETY_STATE, note="toggle form", spec_ref="3")
        run.call(p, "/Status", note="state after toggle", spec_ref="2.2", save=False)
        run.call(p, "/Pause?toggle=1", safety=SAFETY_STATE, note="toggle back", spec_ref="3", save=False)

        # bare /Repeat and /Shuffle: read or write? nobody knows (C-40)
        flags_before = run.call(p, "/Playlist", note="queue flags before bare /Repeat",
                                spec_ref="7.1", save=False)
        fb = root_attrs(body_of(run, flags_before))
        # Whether these endpoints write is the claim under test, so the flags
        # have to be put back either way, and from the ledger so a crash in
        # between still restores them.
        for flag in ("repeat", "shuffle"):
            if fb.get(flag) is not None:
                run.defer_get(p, "/%s?state=%s" % (flag.capitalize(), fb[flag]),
                              "%s: restore %s=%s" % (p.label, flag, fb[flag]))
        run.call(p, "/Repeat", safety=SAFETY_STATE, note="bare /Repeat: read or write?",
                 spec_ref="3")
        run.call(p, "/Shuffle", safety=SAFETY_STATE, note="bare /Shuffle: read or write?",
                 spec_ref="3")
        time.sleep(1.0)
        flags_after = run.call(p, "/Playlist", note="queue flags after bare /Repeat and /Shuffle",
                               spec_ref="7.1", save=False)
        fa = root_attrs(body_of(run, flags_after))
        keys = [k for k in ("repeat", "shuffle") if k in fb or k in fa]
        if not keys:
            run.note("state_playback",
                     "C-40: /Playlist carries neither repeat nor shuffle on this player",
                     "nothing to compare, so the claim cannot be decided here",
                     claim="C-40-repeat-shuffle-read", claim_verdict="INCONCLUSIVE")
        else:
            moved = [k for k in keys if fb.get(k) != fa.get(k)]
            run.note("state_playback",
                     "C-40: bare /Repeat and /Shuffle %s the queue flags"
                     % ("CHANGED" if moved else "left"),
                     "before %s / after %s -- a read leaves them alone; a write does not"
                     % ({k: fb.get(k) for k in keys}, {k: fa.get(k) for k in keys}),
                     claim="C-40-repeat-shuffle-read",
                     claim_verdict="CONFIRMED" if not moved else "DISCONFIRMED")

        # restore transport state
        if before.state in ("play", "stream"):
            run.call(p, "/Play", safety=SAFETY_STATE, note="RESTORE playback", save=False)
        elif before.state in ("pause",):
            run.call(p, "/Pause", safety=SAFETY_STATE, note="RESTORE paused", save=False)
        after = take_snapshot(p)
        undo_tp["done"] = (after.state == before.state)
        run.note("state_playback", "%s restore: state %s -> %s" % (p.label, before.state, after.state),
                 "track position is not restorable through the API; secs %s -> %s"
                 % (before.secs, after.secs),
                 verdict="OK" if after.state == before.state else "UNEXPECTED")


def suite_state_sleep(run: Runner) -> None:
    run.current_suite = "state_sleep"
    run.banner("state_sleep -- /Sleep set and cycle")
    for p in run.writable()[:1]:
        undo_sleep = run.defer_get(p, "/Sleep?minutes=0", "%s: clear the sleep timer" % p.label)
        for m in ("15", "17", "0"):
            run.call(p, "/Sleep?minutes=%s" % m, safety=SAFETY_STATE,
                     note="set sleep %s" % m, spec_ref="3", save=False)
        seq = []
        for step in range(7):
            pr = run.call(p, "/Sleep", safety=SAFETY_STATE,
                          note="bare /Sleep cycle step %d" % (step + 1), spec_ref="3",
                          save=False, quiet=True)
            seq.append(re.sub(r"\s+", "", (pr.extra.get("body_preview") or ""))[:60])
        run.note("state_sleep", "bare /Sleep cycles through: %s" % " -> ".join(seq),
                 "the Integration Utility offers 0/15/30/45/60; this is the real cycle")
        run.call(p, "/Sleep?minutes=0", safety=SAFETY_STATE, note="RESTORE sleep off",
                 spec_ref="3", save=False)
        undo_sleep["done"] = True


def suite_state_name(run: Runner) -> None:
    run.current_suite = "state_name"
    run.banner("state_name -- ?set= versus POST nodename=")
    for p in run.writable()[:1]:
        before = take_snapshot(p)
        if not before.name:
            run.note("state_name", "no starting name read; skipped", verdict="ERROR")
            continue
        tmp = "ProbeTest"
        undo_name = run.defer_get(p, "/Name?set=%s" % urllib.parse.quote(before.name),
                                  "%s: restore player name" % p.label)
        run.call(p, "/Name?set=%s" % urllib.parse.quote(tmp), safety=SAFETY_STATE,
                 note="write via ?set=", spec_ref="10")
        run.call(p, "/SyncStatus", note="name after ?set=", spec_ref="2.1", save=False)
        run.call(p, "/Name", method="POST", body=b"nodename=ProbeTest2",
                 safety=SAFETY_STATE, note="[T blutui] write via POST nodename=",
                 spec_ref="10", claim="C-34-name-post", claim_confirm="status=200")
        run.call(p, "/Name", note="name after POST", spec_ref="10", save=False)
        run.call(p, "/Name?set=%s" % urllib.parse.quote(before.name), safety=SAFETY_STATE,
                 note="RESTORE original name", spec_ref="10", save=False)
        undo_name["done"] = True
        after = take_snapshot(p)
        run.note("state_name", "%s name restored: %s" % (p.label, "yes" if after.name == before.name else "NO"),
                 verdict="OK" if after.name == before.name else "ERROR")
        run.note("state_name", "T-19 reminder",
                 "whether the name survives a reboot still needs a power cycle; "
                 "read /Name the next time a player restarts for any other reason")


def suite_state_setting(run: Runner) -> None:
    """T-35: GET query or POST form? LED brightness is visible and reversible."""
    run.current_suite = "state_setting"
    run.banner("state_setting -- /setting write convention (LED brightness)")
    for p in run.writable()[:1]:
        raw = http_call(p.host, SETTINGS_PORT, "/Settings?id=player&schemaVersion=35", timeout=20)
        text = raw.body.decode("utf-8", "replace") if raw.body else ""
        m = re.search(r'<setting\b[^>]*\bid="ledbrightness"[^>]*>', text)
        cur = None
        if m:
            v = re.search(r'\bvalue="([^"]*)"', m.group(0))
            cur = v.group(1) if v else None
        run.note("state_setting", "ledbrightness before: %s" % (cur if cur is not None else "not found"),
                 m.group(0) if m else "no ledbrightness setting on this model")
        if not m:
            continue
        undo_led = (run.defer_get(p, "/setting?ledbrightness=%s" % cur,
                                  "%s: restore ledbrightness to %s" % (p.label, cur))
                    if cur is not None else None)
        def led_now() -> str:
            r = http_call(p.host, SETTINGS_PORT, "/Settings?id=player&schemaVersion=35",
                          timeout=20)
            t = r.body.decode("utf-8", "replace") if r.body else ""
            tag = re.search(r'<setting\b[^>]*\bid="ledbrightness"[^>]*>', t)
            if not tag:
                return ""
            v = re.search(r'\bvalue="([^"]*)"', tag.group(0))
            return v.group(1) if v else ""

        # The claim is that writes are POST form, NOT GET query. It was
        # confirmed when the GET write returned 200 -- the inverse of what it
        # says. Both styles are now tried and decided by readback.
        target_get = "1" if cur != "1" else "2"
        run.call(p, "/setting?ledbrightness=%s" % target_get, safety=SAFETY_STATE,
                 note="write style A: GET query", spec_ref="10.3")
        time.sleep(1.5)
        after_get = led_now()
        run.call(p, "/Settings?id=player&schemaVersion=35", port=SETTINGS_PORT,
                 note="read back after GET-query write", spec_ref="10.3", save=False)

        target_post = "2" if after_get != "2" else "1"
        run.call(p, "/setting", method="POST",
                 body=("ledbrightness=%s" % target_post).encode(), safety=SAFETY_STATE,
                 note="write style B: POST form", spec_ref="10.3")
        time.sleep(1.5)
        after_post = led_now()
        run.call(p, "/Settings?id=player&schemaVersion=35", port=SETTINGS_PORT,
                 note="read back after POST-form write", spec_ref="10.3", save=False)

        # The settings tree reports a DISPLAY string -- off / dim / bright --
        # not the numeric value that was written. Comparing "dim" against the
        # requested "1" scored a write that plainly worked as a failure, and
        # C-35 came out INCONCLUSIVE when the evidence was clear. What matters
        # is whether the value moved, not whether it echoes the number.
        get_worked = bool(after_get) and after_get != cur
        post_worked = bool(after_post) and after_post != after_get
        if not after_get and not after_post:
            verdict = "INCONCLUSIVE"       # could not read the value back at all
        elif post_worked and not get_worked:
            verdict = "CONFIRMED"          # POST form only, as blutui claims
        elif get_worked:
            verdict = "DISCONFIRMED"       # the GET query works, so pyblu is right
        else:
            verdict = "INCONCLUSIVE"
        run.note("state_setting",
                 "ledbrightness: GET query %s, POST form %s"
                 % ("took effect" if get_worked else "did not",
                    "took effect" if post_worked else "did not"),
                 "before=%s after GET=%s (asked %s) after POST=%s (asked %s). "
                 "The tree reports a display string, so a change of value is the "
                 "signal, not an echo of the number. "
                 "blutui says the write must be a POST form; pyblu uses a GET query. "
                 "Only the readback can tell them apart, because BluOS answers 200 to "
                 "both." % (cur, after_get or "?", target_get, after_post or "?", target_post),
                 claim="C-35-setting-post", claim_verdict=verdict)
        if cur is not None:
            run.call(p, "/setting?ledbrightness=%s" % cur, safety=SAFETY_STATE,
                     note="RESTORE ledbrightness", spec_ref="10.3", save=False)
            if undo_led:
                undo_led["done"] = True


def suite_state_preset(run: Runner) -> None:
    """T-22 / C-17: recall a preset and look for <is_preset> on the SAME player."""
    run.current_suite = "state_preset"
    run.banner("state_preset -- recall and <is_preset>")
    target = None
    for p in run.writable():
        raw = http_call(p.host, p.port, "/Presets", timeout=10)
        if raw.status == 200 and b"<preset " in raw.body:
            target = p
            break
    if not target:
        withheld = []
        for p in run.targets():
            if p in run.writable():
                continue
            raw = http_call(p.host, p.port, "/Presets", timeout=10)
            if raw.status == 200 and b"<preset " in raw.body:
                withheld.append(p.label)
        if withheld:
            run.note("state_preset",
                     "the only player with presets (%s) is excluded by --preserve"
                     % ", ".join(withheld),
                     "recalling a preset does not create, delete or alter one -- it only "
                     "starts playing it. If that is acceptable, drop --preserve %s and "
                     "C-17 can be settled." % withheld[0])
        else:
            run.note("state_preset", "no player has presets configured; C-17 cannot be tested")
        return
    before = take_snapshot(target)
    # A recalled preset starts playing and cannot be un-recalled, so at least
    # the transport state and volume are put back -- and from the ledger, so a
    # Ctrl-C mid-suite does not leave a preset playing.
    defer_transport(run, target, before)
    cap_volume(run, target, before)
    pr = run.call(target, "/Presets", note="preset list on the player about to be used",
                  spec_ref="6.1")
    ids = re.findall(r'<preset\b[^>]*\bid="(\d+)"', body_of(run, pr))
    run.note("state_preset",
             "recalling on %s -- presets are READ ONLY here, only recalled" % target.label,
             "ids seen: %s" % ", ".join(ids))
    for pid in ids[:2]:
        run.call(target, "/Preset?id=%s" % pid, safety=SAFETY_STATE,
                 note="recall preset %s -- record the response root" % pid,
                 spec_ref="6;7.3")
        time.sleep(2.0)
        # Was claim_confirm="status=200", so any answering /Status "confirmed"
        # that <is_preset> exists. The element itself has to be present.
        run.call(target, "/Status",
                 note="does /Status carry <is_preset> / <preset_name> while a preset plays?",
                 spec_ref="2.2", claim="C-17-is-preset",
                 claim_confirm="status=200;contains=<is_preset>",
                 claim_disconfirm="status=200;absent=<is_preset>")
    run.note("state_preset", "restoring playback state on %s" % target.label,
             "state was %s / %s; a recalled preset cannot be un-recalled through the API, "
             "so the previous source is restored only if it was a preset itself"
             % (before.state, before.service))
    if before.state in ("pause", "stop"):
        run.call(target, "/Pause", safety=SAFETY_STATE, note="RESTORE paused", save=False)


SOURCE_FIELDS = ("service", "inputId", "streamUrl", "title1", "title2", "title3",
                 "image", "streamFormat", "quality", "song")


def source_fingerprint(p: Player) -> Tuple[Tuple[str, ...], str, str]:
    """What is playing, as a comparable tuple. Returns (fingerprint, state, raw).

    `state` is deliberately kept OUT of the fingerprint. A /Play carrying
    parameters the firmware does not understand degenerates into a bare /Play,
    which resumes playback -- so `state` changing from pause to play is what a
    rejected parameter looks like, not what success looks like.
    """
    raw = http_call(p.host, p.port, "/Status", timeout=10)
    t = raw.body.decode("utf-8", "replace") if raw.body else ""

    return (tuple(element_text(t, f) for f in SOURCE_FIELDS),
            element_text(t, "state"), t)


def await_change(p: Player, before: Tuple[str, ...], seconds: float = 5.0
                 ) -> Tuple[Tuple[str, ...], str, float]:
    """Source changes are asynchronous. Poll until the fingerprint moves or the
    window closes, and report how long it took."""
    t0 = time.monotonic()
    fp, st, _ = source_fingerprint(p)
    while fp == before and (time.monotonic() - t0) < seconds:
        time.sleep(0.6)
        fp, st, _ = source_fingerprint(p)
    return fp, st, time.monotonic() - t0


def suite_state_source(run: Runner) -> None:
    """Input selection, tested against controls.

    The difficulty is not sending the request; it is knowing whether it did
    anything. Three separate false positives are possible, and each has bitten
    someone already:

      1. HTTP 200 means nothing. BluOS answers 200 to parameters it ignores.
      2. A /Play with unrecognised parameters degenerates into a bare /Play and
         resumes playback. Against a paused player that looks exactly like
         success. This is what nearly settled T-6 wrongly.
      3. Two different inputs are both `service=Capture`, so checking the
         service name cannot tell you whether the *right* input was selected --
         or whether anything changed at all, if the previous trial already left
         the player on Capture.

    So: learn each input's fingerprint from the playURL the device itself
    supplies, reset to a known different source before every trial, and
    interleave negative controls whose failure to change anything is what makes
    a positive result meaningful.
    """
    run.current_suite = "state_source"
    run.banner("state_source -- input selection, verified against positive and negative controls")
    caps = run.facts.get("capabilities") or detect_capabilities(run)
    candidates = [p for p in run.writable() if (caps.get(p.label, {}).get("inputs") or 0) > 0]
    if not candidates:
        run.note("state_source",
                 "NOT APPLICABLE: no writable player advertises a capture input",
                 "Every selector would come back IGNORED, and that would say nothing about "
                 "the protocol. Skipped rather than recorded as a row of failures.",
                 verdict="INFO")
        return
    # prefer the player with the most inputs: two inputs make the result conclusive
    candidates.sort(key=lambda p: -(caps.get(p.label, {}).get("inputs") or 0))

    p = candidates[0]
    before = take_snapshot(p)
    defer_transport(run, p, before)
    cap_volume(run, p, before)
    browse_pr = run.call(p, "/Browse", note="browse root: inputType values and playURLs",
                         spec_ref="15.1", timeout=25)
    btext = _body_of(run, browse_pr)
    run.call(p, "/RadioBrowse?service=Capture", note="the Capture input list",
             spec_ref="8.1", timeout=20)

    play_urls = [u
                 for u in re.findall(r'playURL="([^"]*Capture[^"]*)"', btext)]
    types = sorted(set(re.findall(r'inputType="([^"]+)"', btext)))
    run.note("state_source", "%s: %d advertised input(s), inputType values: %s"
             % (p.label, len(play_urls), ", ".join(types) or "none"))

    # Playback must be running throughout, so that a degenerate /Play cannot
    # look like a source change.
    if before.state not in ("play", "stream"):
        run.call(p, "/Play", safety=SAFETY_STATE,
                 note="start playback, so an ignored parameter cannot masquerade as success",
                 spec_ref="15.2", save=False)
        time.sleep(2.5)

    # ---- positive control: learn each input's fingerprint from its own playURL
    known: Dict[Tuple[str, ...], str] = {}
    for i, url in enumerate(play_urls[:4]):
        fp0, _, _ = source_fingerprint(p)
        run.call(p, url, safety=SAFETY_STATE,
                 note="POSITIVE CONTROL: select input %d by the playURL the device supplied" % (i + 1),
                 spec_ref="15.2")
        fp, _state, took = await_change(p, fp0)
        if fp != fp0:
            known[fp] = "input#%d via playURL" % (i + 1)
            run.note("state_source", "learned input %d: streamUrl=%s title1=%s (%.1fs)"
                     % (i + 1, fp[SOURCE_FIELDS.index("streamUrl")] or "-",
                        fp[SOURCE_FIELDS.index("title1")] or "-", took))
        else:
            run.note("state_source",
                     "POSITIVE CONTROL FAILED: the device's own playURL for input %d "
                     "changed nothing" % (i + 1),
                     "If the device cannot select its own advertised input, the detection "
                     "method is broken and every negative result below is worthless. "
                     "Check that something was playing and that the input has signal.",
                     verdict="ERROR")

    if len(known) < 2:
        run.note("state_source",
                 "fewer than two distinguishable inputs were learned (%d)" % len(known),
                 "With one input, 'did it switch' cannot be separated from 'it was "
                 "already there'. Results below are weaker; enable a second input, or "
                 "read them as suggestive only.",
                 verdict="UNEXPECTED")

    # Homes to start a trial from. A trial that starts on the very input it
    # would select is unfalsifiable: "no change" and "already there" look
    # identical. So a trial is only declared IGNORED once it has failed to
    # move the player from EVERY known starting input.
    homes: List[Tuple[str, Tuple[str, ...]]] = []   # (playURL, fingerprint)
    for url in play_urls[:4]:
        http_call(p.host, p.port, url, timeout=15)
        time.sleep(1.5)
        fp, _, _ = source_fingerprint(p)
        if fp in known:
            homes.append((url, fp))
    if not homes:
        homes = [("", source_fingerprint(p)[0])]

    def trial(query: str, note: str, claim: str = "", negative: bool = False) -> str:
        attempts = []
        for home_url, _cached in homes:   # a fresh read is used, not the cache
            if home_url:
                http_call(p.host, p.port, home_url, timeout=15)
                time.sleep(1.5)
            start_fp, state_before, _ = source_fingerprint(p)
            run.call(p, query, safety=SAFETY_STATE,
                     note="%s (from %s)" % (note, known.get(start_fp, "current source")),
                     spec_ref="15.2", save=False, quiet=True)
            fp, state_after, took = await_change(p, start_fp, seconds=4.0)
            attempts.append((start_fp, fp, state_before, state_after, took))
            if fp != start_fp:
                break        # it moved: no need to try another starting point

        start_fp, fp, state_before, state_after, took = attempts[-1]
        if fp == start_fp:
            verdict = "IGNORED"
            detail = ("no field in %s changed, from %d different starting input(s). "
                      "state %s -> %s."
                      % (", ".join(SOURCE_FIELDS), len(attempts), state_before, state_after))
            if state_before != state_after:
                verdict = "RESUMED ONLY"
                detail += (" Playback state moved but the source did not: this is the "
                           "degenerate bare /Play, i.e. the parameters were discarded. "
                           "Against a paused player this is exactly what a working "
                           "selector would look like, which is the trap.")
        elif fp in known:
            verdict = "SELECTED A KNOWN INPUT"
            detail = ("moved from %s to %s in %.1fs"
                      % (known.get(start_fp, "?"), known[fp], took))
        else:
            verdict = "SELECTED SOMETHING NOT ADVERTISED"
            detail = ("landed on a source with no advertised playURL: streamUrl=%s "
                      "title1=%s inputId=%s. If that slot is disabled in the Controller "
                      "app, then 'disabled' is a view filter and not a capability gate."
                      % (fp[SOURCE_FIELDS.index("streamUrl")] or "-",
                         fp[SOURCE_FIELDS.index("title1")] or "-",
                         fp[SOURCE_FIELDS.index("inputId")] or "-"))

        worked = verdict.startswith("SELECTED")
        if negative:
            run.note("state_source", "NEGATIVE CONTROL %s -> %s" % (query, verdict),
                     detail + ("\n\nA negative control that appears to work means the "
                               "method is unsound and no positive result in this suite "
                               "can be trusted." if worked else
                               "\n\nGood: a meaningless selector moves nothing, so a "
                               "positive result elsewhere is a real one."),
                     verdict="ERROR" if worked else "OK")
        else:
            run.note("state_source", "%s -> %s" % (query, verdict), detail,
                     claim=claim,
                     claim_verdict=("CONFIRMED" if worked else "DISCONFIRMED") if claim else "")
        return verdict

    # ---- negative controls, before and after the real trials
    trial("/Play?inputType=zzznotreal&index=1", "selector that cannot exist", negative=True)
    trial("/Play?inputTypeIndex=zzznotreal-9", "inputTypeIndex that cannot exist", negative=True)
    trial("/Play?inputIndex=99", "input index far beyond any real input", negative=True)

    # ---- the competing selectors, each against a fresh known start
    trial("/Play?inputIndex=2", "the confirmed inputIndex form")
    for t in types or ["arc", "spdif", "optical"]:
        trial("/Play?inputType=%s&index=1" % t,
              "[T bluos-api-rs] inputType=%s&index=1" % t,
              claim="C-37-play-inputtype")
        trial("/Play?inputTypeIndex=%s-1" % t, "T-18 retest: inputTypeIndex=%s-1" % t)

    # ---- spellings this player never advertised, and disabled slots
    for t in ("hdmi", "arc", "optical", "spdif", "analog", "bluetooth"):
        if t in types:
            continue
        trial("/Play?inputTypeIndex=%s-1" % t,
              "unadvertised slot %s-1: is a disabled input still reachable?" % t,
              claim="C-53-disabled-input-playable")

    # ---- one more negative control at the end, in case something drifted
    trial("/Play?inputType=zzznotreal&index=2", "repeat of the impossible selector",
          negative=True)

    run.note("state_source", "%s: source restore is best-effort" % p.label,
             "was service=%s songid=%s state=%s. An input switch cannot be undone through "
             "the API without re-selecting the previous source by hand."
             % (before.service, before.songid, before.state))
    if before.state in ("pause", "stop"):
        run.call(p, "/Pause", safety=SAFETY_STATE, note="RESTORE paused", save=False)


def suite_state_grouping(run: Runner) -> None:
    """The headline round-2 suite: grouping semantics, and specifically why the
    same player keeps winning the master role (C-39)."""
    run.current_suite = "state_grouping"
    run.banner("state_grouping -- role assignment, swapping, and the [T] register")
    ps = run.writable()
    held = [p.label for p in run.targets() if p not in ps]
    if held:
        run.note("state_grouping", "excluded by --preserve: %s" % ", ".join(held),
                 "grouping is a write, so a preserved player is left out of it entirely")
    if len(ps) < 2:
        run.note("state_grouping",
                 "fewer than two writable players; suite skipped",
                 "grouping needs two players this run is allowed to change",
                 verdict="ERROR")
        return
    a, b = ps[0], ps[1]

    baseline = {p.label: take_snapshot(p) for p in ps}
    undo_topo = defer_topology(run, ps, baseline)
    grouped = [lbl for lbl, s in baseline.items() if s.master or s.slaves]
    if grouped:
        run.note("state_grouping",
                 "players already grouped at start: %s" % ", ".join(grouped),
                 "ungrouping first so role assignment is measured from a known state",
                 verdict="UNEXPECTED")
        _still, _fb = teardown_groups(run, ps)

    def topo(tag: str) -> Dict[str, Snapshot]:
        out = {}
        for p in ps[:3]:
            snap = take_snapshot(p)
            out[p.label] = snap
            run.note("state_grouping", "%s | %s: master=%s slaves=%s group=%s" % (
                tag, p.label, snap.master or "-", ",".join(snap.slaves) or "-", snap.group or "-"))
        return out

    topo("baseline")

    # --- Step 1: form A <- B, the ordinary direction
    run.call(a, "/AddSlave?slave=%s&port=%d" % (b.host, b.port), safety=SAFETY_STATE,
             note="form group: %s takes %s as slave" % (a.label, b.label), spec_ref="5")
    settle(run, a, "/SyncStatus", note="after AddSlave on the master")
    settle(run, b, "/SyncStatus", note="after AddSlave on the slave")
    topo("after A<-B")

    # --- Step 2: C-39. Reverse WITHOUT ungrouping. This is the case the tester
    #     saw fail while the official app succeeded.
    run.note("state_grouping", "C-39 step 1: reversing without ungrouping first",
             "the app appears to ungroup before re-forming; this measures what happens "
             "if you do not")
    run.call(b, "/AddSlave?slave=%s&port=%d" % (a.host, a.port), safety=SAFETY_STATE,
             note="C-39: slave %s tries to take master %s as ITS slave" % (b.label, a.label),
             spec_ref="5.3")
    settle(run, a, "/SyncStatus", note="A after attempted reversal")
    settle(run, b, "/SyncStatus", note="B after attempted reversal")
    topo("after direct reversal attempt")

    # --- Step 3: the slave-side join form
    run.call(a, "/SetMaster?master=%s&port=%d" % (b.host, b.port), safety=SAFETY_STATE,
             note="C-39: ask %s to join %s's group (slave-side form)" % (a.label, b.label),
             spec_ref="5.3")
    settle(run, a, "/SyncStatus", note="A after SetMaster?master=B")
    settle(run, b, "/SyncStatus", note="B after SetMaster?master=B")
    topo("after SetMaster reversal attempt")

    # --- Step 4: ungroup properly, confirm both standalone
    run.call(a, "/RemoveSlave?slave=%s&port=%d" % (b.host, b.port), safety=SAFETY_STATE,
             note="ungroup, addressed to the master", spec_ref="5")
    run.call(b, "/SetMaster", safety=SAFETY_STATE,
             note="bare /SetMaster on the slave: the confirmed self-unjoin", spec_ref="5.3")
    time.sleep(2)
    topo("after ungrouping")

    # --- Step 5: now form the group the other way round
    run.call(b, "/AddSlave?slave=%s&port=%d" % (a.host, a.port), safety=SAFETY_STATE,
             note="C-39 step 2: with both standalone, %s takes %s -- does the role stick?"
                  % (b.label, a.label), spec_ref="5")
    settle(run, b, "/SyncStatus", note="B after forming the reversed group")
    settle(run, a, "/SyncStatus", note="A after forming the reversed group")
    reversed_topo = topo("after reversed grouping")

    b_is_master = bool(reversed_topo.get(b.label) and reversed_topo[b.label].slaves)
    run.note("state_grouping",
             "C-39 result: with both players standalone first, %s %s master"
             % (b.label, "DID become" if b_is_master else "did NOT become"),
             "If this works and the direct reversal did not, the rule is simply that "
             "role is decided at group formation and cannot be transferred while the "
             "group exists -- which is exactly what the official app works around by "
             "ungrouping first. If %s still refuses to be a slave, the cause is a "
             "property of the player rather than of the sequence, and the next thing to "
             "compare is model, firmware, address ordering and hasSubwoofer."
             % a.label,
             verdict="OK" if b_is_master else "UNEXPECTED")

    # --- Step 6: register claims that need a live group
    run.call(b, "/AddSlave?slave=%s" % a.host, safety=SAFETY_STATE,
             note="[T 2015 forum] singular /AddSlave with port omitted", spec_ref="5")
    settle(run, b, "/SyncStatus", tries=2, note="after port-less AddSlave")

    run.call(b, "/SlaveVolume?slave=%s:%d&db=0" % (a.host, a.port), safety=SAFETY_STATE,
             note="[T blutui] /SlaveVolume with a combined slave=<ip>:<port>", spec_ref="4",
             claim="C-33-slavevolume-combined",
             claim_confirm="status=200;root=slaveVolume",
             claim_disconfirm="status=404|400;absent=slaveVolume")
    run.call(b, "/SlaveVolume?slave=%s&port=%d&db=0" % (a.host, a.port), safety=SAFETY_STATE,
             note="documented separate slave= and port= form, as a control", spec_ref="4")

    run.call(b, "/AddSlave?slave=%s&port=%d&channelMode=1" % (a.host, a.port),
             safety=SAFETY_STATE, note="[T HA] numeric channelMode=1", spec_ref="5")
    run.call(a, "/SyncStatus", note="what channelMode does the slave echo back?",
             spec_ref="2.1", save=False)
    run.call(b, "/AddSlave?slave=%s&port=%d&channelMode=left" % (a.host, a.port),
             safety=SAFETY_STATE, note="string channelMode=left, as a control", spec_ref="5")
    run.call(a, "/SyncStatus", note="channelMode after the string form", spec_ref="2.1", save=False)
    run.call(b, "/AddSlave?slave=%s&port=%d&channelMode=default" % (a.host, a.port),
             safety=SAFETY_STATE, note="RESTORE channelMode=default", spec_ref="5", save=False)

    # T-30 legacy /Sync, only ever with a live group present
    run.call(b, "/Sync?slave=%s" % a.host, safety=SAFETY_STATE,
             note="[T bluos-dashboard] legacy /Sync?slave=", spec_ref="5.2")
    run.call(b, "/Sync?remove=%s" % a.host, safety=SAFETY_STATE,
             note="[T bluos-dashboard] legacy /Sync?remove=", spec_ref="5.2")
    settle(run, b, "/SyncStatus", tries=2, note="after the legacy /Sync calls")

    # --- Step 7: three-player group, then the bare /RemoveSlave claim (T-36a).
    #     Deliberately last, because if it is true it dissolves everything.
    if len(ps) >= 3:
        c = ps[2]
        run.call(b, "/AddSlave?slave=%s&port=%d" % (c.host, c.port), safety=SAFETY_STATE,
                 note="add a second slave so bare /RemoveSlave has something to prove",
                 spec_ref="5")
        settle(run, b, "/SyncStatus", tries=2, note="two slaves present")
    run.call(b, "/RemoveSlave", safety=SAFETY_STATE,
             note="[T HA] does a bare /RemoveSlave drop every slave?", spec_ref="5")
    settle(run, b, "/SyncStatus", tries=3, note="after bare /RemoveSlave")
    final = topo("after bare /RemoveSlave")
    b_final = final.get(b.label)
    still = len(b_final.slaves) if b_final else -1
    run.note("state_grouping",
             "C-30: slaves remaining after a bare /RemoveSlave: %s" % still,
             "Zero means the claim holds. Anything else means a bare /RemoveSlave does "
             "NOT drop every slave, and a client must name them.",
             verdict="OK" if still == 0 else "UNEXPECTED",
             claim="C-30-removeslave-bare",
             claim_verdict=("CONFIRMED" if still == 0 else
                            ("INCONCLUSIVE" if still < 0 else "DISCONFIRMED")))

    # --- Restore: everything standalone, then rebuild whatever was there at start
    run.banner("state_grouping -- restoring the original topology")
    _still, _fb = teardown_groups(run, ps)
    rebuild_groups(run, baseline)
    same, detail = topology_matches(run, baseline)
    undo_topo["done"] = same
    run.note("state_grouping", "original topology restored: %s" % ("yes" if same else "NO"),
             detail,
             verdict="OK" if same else "ERROR")




# --------------------------------------------------------------------------
# FINDINGS.md -- results in a form that can be pasted into the specification,
# including the negative ones.
# --------------------------------------------------------------------------

def _register_rows(by_claim: Dict[str, List[Probe]], resolve: Callable[[List[Probe]], str],
                   date: str, firmwares: str, schemas: str, bundle_id: str) -> List[str]:
    """Rows formatted for the specification's append-only claim register."""
    lines = ["---", "",
             "## Rows for the specification's disconfirmation register", "",
             "Append these. Do not delete a row when a later firmware changes the",
             "answer -- add a second row. The point of the register is that a reader",
             "who meets the same claim in a third-party project can see it was already",
             "checked, when, against what, and with what result.", "",
             "```markdown"]
    any_row = False
    for cid in sorted(by_claim):
        if resolve(by_claim[cid]) not in ("DISCONFIRMED", "MIXED", "INCONCLUSIVE"):
            continue
        any_row = True
        probes = by_claim[cid]
        meta = CLAIMS.get(cid, {})
        p0 = probes[0]
        lines.append("| `%s` | %s | %s | %s | %s, fw %s, schema %s | %s | %s: %s |" % (
            cid, meta.get("claim", "?"), meta.get("source", "?"),
            resolve(probes), date, firmwares or "?", schemas or "?",
            "`%s :%d%s` -> %s" % (p0.method, p0.port, p0.path,
                                  p0.status if p0.status is not None else p0.error),
            bundle_id, ", ".join(p.id for p in probes[:4])))
    if not any_row:
        lines.append("(nothing disconfirmed or inconclusive in this run)")
    lines += ["```", "",
              "Column order: claim id - claim - source - verdict - tested against -",
              "the request and its answer - evidence pointer.", ""]
    return lines


def _promote_section(by_claim: Dict[str, List[Probe]],
                     resolve: Callable[[List[Probe]], str]) -> List[str]:
    confirmed = [c for c in by_claim if resolve(by_claim[c]) == "CONFIRMED"]
    if not confirmed:
        return []
    lines = ["## Promote out of the register", "",
             "These were confirmed on hardware and can move from the `[T]` register",
             "into the body of the specification as `[V hardware]`, citing this bundle.",
             "The register row itself stays, as provenance.", ""]
    for cid in sorted(confirmed):
        meta = CLAIMS.get(cid, {})
        lines.append("- `%s` -- %s (section %s)" % (cid, meta.get("claim", "?"),
                                                    meta.get("spec", "?")))
    lines.append("")
    return lines


def _fidelity_section(run: Runner) -> List[str]:
    mod = [p for p in run.results if p.body_file and not p.verbatim]
    verb = [p for p in run.results if p.body_file and p.verbatim]
    lines = ["---", "",
             "## Capture fidelity", "",
             "%d captured bodies are **byte-for-byte what the device sent** -- redaction "
             "changed nothing in them, so they are usable as parser fixtures and as "
             "evidence about byte lengths without qualification." % len(verb),
             "",
             "%d were modified. For each, `body_bytes_wire` in `MANIFEST.json` gives the "
             "original length and `redaction_edits` the number of substitutions, so a "
             "length-sensitive claim can still be checked. The digest recorded in the "
             "bundle is of the **redacted** body; because redaction is deterministic and "
             "stable within a run, two redacted digests still compare correctly against "
             "each other. Digests of the original bodies are in the do-not-share key file "
             "only, because for a templated body they would recover the redacted values "
             "by brute force." % len(mod),
             ""]
    if mod:
        lines += ["| probe | endpoint | wire bytes | written bytes | edits |",
                  "|---|---|---|---|---|"]
        for p in mod[:60]:
            lines.append("| `%s` | `%s` | %s | %s | %d |" % (
                p.id, p.path.split("?")[0], p.body_bytes_wire, p.body_bytes,
                p.redaction_edits))
        lines.append("")
    return lines


def build_findings(run: Runner, started: datetime.datetime, bundle_id: str) -> str:
    by_claim: Dict[str, List[Probe]] = {}
    for pr in run.results:
        if pr.claim:
            by_claim.setdefault(pr.claim, []).append(pr)

    def resolve(probes: List[Probe]) -> str:
        """CONFIRMED first meant one confirmation buried every counterexample.

        For a universal claim ("port 11001 serves settings and nothing else",
        tested across five paths and two models) a single counterexample should
        decide it -- which was the whole point of testing more than one player.
        Claims that are existential by nature carry quantifier="any".
        """
        vs = {p.claim_verdict for p in probes if p.claim_verdict}
        if not vs:
            return "INCONCLUSIVE"
        cid = probes[0].claim
        quantifier = CLAIMS.get(cid, {}).get("quantifier", "all")
        if quantifier == "any":
            return "CONFIRMED" if "CONFIRMED" in vs else (
                "DISCONFIRMED" if vs == {"DISCONFIRMED"} else "INCONCLUSIVE")
        if quantifier == "no_counterexample":
            # A universal negative: "bare /Repeat does not write". One observed
            # write settles it, and the confirming cases only mean the flag
            # already held the value that would have been written.
            return "DISCONFIRMED" if "DISCONFIRMED" in vs else (
                "CONFIRMED" if vs == {"CONFIRMED"} else "INCONCLUSIVE")
        if "CONFIRMED" in vs and "DISCONFIRMED" in vs:
            return "MIXED"
        if vs == {"CONFIRMED"}:
            return "CONFIRMED"
        if "DISCONFIRMED" in vs:
            return "DISCONFIRMED"
        return "INCONCLUSIVE"

    fleet = ", ".join(sorted({"%s %s" % (p.brand or "", p.model) for p in run.targets() if p.model}))
    firmwares = ", ".join(sorted({p.version for p in run.targets() if p.version}))
    schemas = ", ".join(sorted({p.schema for p in run.targets() if p.schema}))
    date = started.date().isoformat()

    lines = ["# Findings",
             "",
             "Generated from this run. Nothing here is inferred: every row cites the",
             "probe that produced it, and the response body is in `raw/`.",
             "",
             "| | |",
             "|---|---|",
             "| bundle | `%s` |" % bundle_id,
             "| date | %s |" % date,
             "| fleet | %s |" % (fleet or "unknown"),
             "| firmware | %s |" % (firmwares or "unknown"),
             "| schemaVersion | %s |" % (schemas or "unknown"),
             ""]

    if run.synthetic:
        lines[0:0] = ["> **SYNTHETIC RUN — NOT EVIDENCE.**",
                      "> The target was loopback, not a BluOS player. Nothing in this file",
                      "> may be used to support or refute anything about the protocol.",
                      ""]

    lines += ["## Claim results", "",
              "| claim | verdict | what was claimed | source | § | evidence |",
              "|---|---|---|---|---|---|"]
    order = {"DISCONFIRMED": 0, "MIXED": 1, "CONFIRMED": 2, "INCONCLUSIVE": 3}
    for cid in sorted(by_claim, key=lambda c: (order.get(resolve(by_claim[c]), 9), c)):
        probes = by_claim[cid]
        verdict = resolve(probes)
        meta = CLAIMS.get(cid, {})
        ev = ", ".join("`%s`" % p.id for p in probes[:6])
        lines.append("| `%s` | **%s** | %s | %s | %s | %s |" % (
            cid, verdict, meta.get("claim", "?"), meta.get("source", "?"),
            meta.get("spec", "?"), ev))
    lines.append("")

    untested = [c for c in CLAIMS if c not in by_claim]
    if untested:
        lines += ["### Not exercised by this run", "",
                  "Recorded so the gap stays visible. `INCONCLUSIVE` and `untested` are",
                  "different things and neither should be read as `DISCONFIRMED`.", ""]
        for cid in sorted(untested):
            meta = CLAIMS[cid]
            lines.append("- `%s` — %s (%s, §%s)" % (cid, meta["claim"], meta["source"], meta["spec"]))
        lines.append("")

    untestable = run.facts.get("untestable") or []
    if untestable:
        lines += ["### Not answerable on this hardware", "",
                  "Distinct from both `INCONCLUSIVE` and `untested`. These could not be",
                  "decided by this fleet, and a negative result for any of them would be a",
                  "fact about the hardware rather than about the protocol. **Do not record",
                  "any of these as `DISCONFIRMED`.**", ""]
        for u in untestable:
            lines.append("- %s" % u)
        lines.append("")

    lines += _register_rows(by_claim, resolve, date, firmwares, schemas, bundle_id)
    lines += _promote_section(by_claim, resolve)
    lines += _fidelity_section(run)
    return "\n".join(lines)




def suite_inputs(run: Runner) -> None:
    """Which physical inputs each player exposes, on every surface that lists
    them -- and specifically whether an input disabled in the Controller app is
    genuinely disabled or merely hidden from that one view.

    Read-only. The corresponding write test is in state_source.
    """
    run.current_suite = "inputs"
    run.banner("inputs -- enumeration across surfaces; is 'disabled' really disabled?")
    if "capabilities" not in run.facts:
        detect_capabilities(run)

    for p in run.targets():
        surfaces: Dict[str, List[str]] = {}

        br = run.call(p, "/Browse", note="browse root: which inputs are offered here?",
                      spec_ref="15.1", timeout=25)
        text = _body_of(run, br)
        surfaces["/Browse root"] = sorted(set(
            re.findall(r'<item\b[^>]*\btext="([^"]*)"[^>]*\binputType=', text) +
            re.findall(r'<item\b[^>]*\binputType="[^"]*"[^>]*\btext="([^"]*)"', text)))
        run.facts.setdefault("input_playurls", {})[p.label] = [
            u for u in re.findall(r'playURL="([^"]*Capture[^"]*)"', text)]

        rb = run.call(p, "/RadioBrowse?service=Capture",
                      note="the Capture service: the input list the app builds its picker from",
                      spec_ref="8.1", timeout=25, claim="C-11-radio-attrs",
                      claim_confirm="status=200;contains=is_active",
                      claim_disconfirm="status=200;absent=is_active")
        text = _body_of(run, rb)
        surfaces["/RadioBrowse?service=Capture"] = sorted(set(
            re.findall(r'<(?:item|radioitem|remoteitem)\b[^>]*\btext="([^"]*)"', text)))

        st = run.call(p, "/Settings?id=capture&schemaVersion=35", port=SETTINGS_PORT,
                      note="the inputs settings page: where enable/disable actually lives",
                      spec_ref="10.3", timeout=25)
        text = _body_of(run, st)
        surfaces["/Settings?id=capture"] = sorted(set(
            re.findall(r'<setting\b[^>]*\bdisplayName="([^"]*)"', text)))
        disabled_markers = re.findall(
            r'<setting\b[^>]*\b(?:displayName="([^"]*)")?[^>]*\b(?:description|value)="([^"]*)"[^>]*>',
            text)
        run.note("inputs", "%s: settings page markers that may encode enable/disable" % p.label,
                 "; ".join("%s=%s" % (a or "?", b) for a, b in disabled_markers[:20])
                 or "none found")

        so = run.call(p, "/Sources", note="/Sources: a third enumeration surface",
                      spec_ref="8.1", timeout=20)
        text = _body_of(run, so)
        surfaces["/Sources"] = sorted(set(re.findall(r'\btext="([^"]*)"', text)))[:20]

        every = sorted({n for names in surfaces.values() for n in names if n})
        rows = ["| input | " + " | ".join(surfaces) + " |",
                "|---" * (len(surfaces) + 1) + "|"]
        for name in every:
            rows.append("| %s | %s |" % (
                name, " | ".join("yes" if name in surfaces[s] else "-" for s in surfaces)))
        run.note("inputs", "%s: input visibility across surfaces" % p.label, "\n".join(rows))

        # Display names legitimately differ between surfaces, so a mismatch on
        # its own proves nothing. The signal is an input the settings tree knows
        # about that neither browse surface offers.
        browsable = set(surfaces["/Browse root"]) | set(surfaces["/RadioBrowse?service=Capture"])
        # The capture settings page also carries non-input settings -- levels,
        # modes, auto-sense -- so "on the settings page but not in browse" was
        # nearly always non-empty and confirmed the claim by construction.
        # Only names that look like an input are considered, and even then the
        # verdict is left to the write test in state_source.
        input_words = ("hdmi", "arc", "earc", "optical", "spdif", "coax", "analog",
                       "analogue", "aux", "line", "toslink", "input", "bluetooth")
        candidates = [n for n in surfaces["/Settings?id=capture"]
                      if n and any(w in n.lower() for w in input_words)]
        hidden = [n for n in candidates if n not in browsable]
        differ = [n for n in every if not all(n in surfaces[s] for s in surfaces)]
        run.note("inputs",
                 "%s: %d name(s) differ across surfaces, %d known to settings but not browsable"
                 % (p.label, len(differ), len(hidden)),
                 ("names only some surfaces list: %s\n" % ", ".join(differ) if differ else "") +
                 ("input-like names known to the settings tree but offered by neither "
                  "browse surface: %s\n" % ", ".join(hidden) if hidden else "") +
                 "\nName mismatches alone prove nothing -- the surfaces use different display "
                 "strings. The question is settled by state_source, which tries to select "
                 "unadvertised input slots directly.",
                 claim="C-52-disabled-input-hidden",
                 claim_verdict="INCONCLUSIVE")


def body_of(run: Runner, pr: Probe) -> str:
    """The body of a probe, for CONTROL FLOW.

    Prefers the raw text. Reading the redacted file instead meant a browse key
    or playURL containing an address, a MAC or a `user=` parameter was followed
    with the placeholder substituted, so `192.0.2.101` was sent back to the
    player. It also broke entirely under --no-bodies, where the crawl silently
    stopped at the root, and it truncated at 400 characters when no file was
    saved.
    """
    cached = run.raw_bodies.get(pr.id)
    if cached:
        return cached
    if pr.body_file:
        f = run.raw / Path(pr.body_file).name
        if f.exists():
            return f.read_text(encoding="utf-8")
    return pr.extra.get("body_preview", "") or ""


_body_of = body_of     # older call sites


# --------------------------------------------------------------------------
# Grouping helpers -- topology is forced to a known state before each case,
# because a test run against an unknown starting topology is what produced the
# ambiguity in the first place.
# --------------------------------------------------------------------------

def ensure_standalone(run: Runner, ps: List[Player], why: str = "") -> bool:
    """Force every player free before a case runs. Cleanup deliberately prefers
    /RemoveSlave over /SetMaster so that a /SetMaster case is never reset by the
    endpoint it is testing; any case that needed the fallback is flagged."""
    before = [p.label for p in ps if fetch_sync(p).grouped]
    leftover, fallback_used = teardown_groups(run, ps)
    if before:
        run.note(run.current_suite, "reset topology before '%s': freed %s"
                 % (why or "case", ", ".join(before)), quiet=True)
    if fallback_used:
        # One-sided membership is the EXPECTED shape after a slave-side join, so
        # needing the fallback there is not contamination -- it is the only exit.
        # Distinguish the two cases: a fallback needed to free a player whose
        # master never listed it is normal; a fallback needed to free a player
        # from a proper /AddSlave group would mean /RemoveSlave failed.
        one_sided, unexplained = [], []
        for lbl in fallback_used:
            pl = run.player(lbl)
            listed = False
            for other in ps:
                if other is pl:
                    continue
                oi = fetch_sync(other)
                if oi.reachable and any(r.id.split(":")[0] == (pl.host if pl else "")
                                        for r in oi.slave_refs):
                    listed = True
            (unexplained if listed else one_sided).append(lbl)
        if one_sided:
            run.note(run.current_suite,
                     "%s could only be freed by a bare /SetMaster" % ", ".join(one_sided),
                     "Expected: after a slave-side join with /SetMaster?master=, no master "
                     "lists this player as a <slave>, so /RemoveSlave has nothing to act "
                     "on. The self-unjoin is the only way out. This does not invalidate "
                     "the case that follows.",
                     verdict="OK")
        if unexplained:
            run.note(run.current_suite,
                     "the bare /SetMaster fallback was needed to free %s"
                     % ", ".join(unexplained),
                     "That player WAS listed as a slave, so /RemoveSlave should have "
                     "freed it and did not. The endpoint under test was used to reset "
                     "the test, so treat the following case as suspect.",
                     verdict="UNEXPECTED")
    if leftover:
        run.note(run.current_suite,
                 "could not free %s at all" % ", ".join(leftover),
                 "Either the player stopped answering or something re-formed the group.",
                 verdict="ERROR")
    return not leftover


def make_group(run: Runner, master: Player, slaves: List[Player]) -> bool:
    run.call(master, "/AddSlave?slaves=%s&ports=%s" % (
        ",".join(s.host for s in slaves), ",".join(str(s.port) for s in slaves)),
        safety=SAFETY_STATE, note="set up: %s takes %s" % (
            master.label, "+".join(s.label for s in slaves)),
        spec_ref="5", save=False, quiet=True)
    time.sleep(2.0)
    got = fetch_sync(master).slaves
    return len(got) == len(slaves)


def suite_state_setmaster(run: Runner) -> None:
    """A systematic /SetMaster matrix: every role crossed with every parameter
    form, from a forced starting topology, verified from both ends.

    /SetMaster is the endpoint most third-party clients get wrong, and the
    existing findings for it come from a single pass in which grouping was not
    always reset between cases.
    """
    run.current_suite = "state_setmaster"
    run.banner("state_setmaster -- role x parameter matrix, each from a clean topology")
    ps = run.writable()
    if len(ps) < 2:
        run.note("state_setmaster", "needs at least two writable players; skipped", verdict="ERROR")
        return
    a, b = ps[0], ps[1]
    c = ps[2] if len(ps) > 2 else None

    baseline = {p.label: take_snapshot(p) for p in ps}
    undo_topo = defer_topology(run, ps, baseline)

    def case(name: str, setup: Callable[[], bool], target: Player, query: str,
             observe: List[Player], claim: str = "",
             expect_change: Optional[bool] = None) -> None:
        """`expect_change` is what the claim predicts the topology will do.
        None means the case is exploratory and no verdict is recorded."""
        run.banner("  case: %s" % name)
        if not ensure_standalone(run, ps, name):
            run.note("state_setmaster", "%s: could not reach a clean start; case skipped" % name,
                     verdict="ERROR")
            return
        if not setup():
            run.note("state_setmaster", "%s: setup did not produce the intended topology" % name,
                     verdict="ERROR")
            return

        before = {p.label: fetch_sync(p) for p in observe}
        pre_etag = before[target.label].etag

        # No claim on the request itself. HTTP 200 says nothing here: BluOS
        # answers 200 to parameters it ignores, so a status-based verdict made
        # C-42 ("a bare /SetMaster does NOT dissolve its group") come out
        # CONFIRMED whether or not the group survived.
        pr = run.call(target, "/SetMaster" + query, safety=SAFETY_STATE,
                      note="%s -- addressed to %s" % (name, target.label), spec_ref="5.3")

        # T-5 saw /SetMaster answer with the PRE-call SyncStatus, same etag.
        resp_etag = root_attrs(body_of(run, pr)).get("etag", "")
        stale = bool(pre_etag and resp_etag and pre_etag == resp_etag)

        time.sleep(2.5)
        after = {p.label: fetch_sync(p) for p in observe}
        rows = ["| player | master before | slaves before | master after | slaves after | group after |",
                "|---|---|---|---|---|---|"]
        for q in observe:
            b, aft = before[q.label], after[q.label]
            rows.append("| %s | %s | %s | %s | %s | %s |" % (
                q.label, b.master or "-", ",".join(b.slaves) or "-",
                aft.master or "-", ",".join(aft.slaves) or "-", aft.group or "-"))
        changed = any(before[q.label].topology != after[q.label].topology for q in observe)
        unreachable = [q.label for q in observe if not after[q.label].reachable]

        # Staleness is only observable on a case that actually moved the
        # topology. On a no-op, an unchanged etag is exactly what a correct,
        # non-stale response would carry, so it proves nothing either way.
        if not pre_etag or not resp_etag or not changed or unreachable:
            stale_verdict = "INCONCLUSIVE"
            stale_why = ("no etag on one side" if not (pre_etag and resp_etag)
                         else "the topology did not move, so an unchanged etag proves nothing")
        else:
            stale_verdict = "CONFIRMED" if stale else "DISCONFIRMED"
            stale_why = ("the response carried the pre-call state, so a client must re-read "
                         "rather than trust it" if stale
                         else "the response already reflected the change")
        run.note("state_setmaster",
                 "%s: response etag %s the pre-call etag"
                 % (name, "EQUALS" if stale else "differs from"),
                 "pre=%s response=%s -- %s" % (pre_etag[:16] or "-", resp_etag[:16] or "-",
                                               stale_why),
                 claim=("C-55-setmaster-bare-fresh" if not query
                        else "C-46-setmaster-stale-response"),
                 claim_verdict=(("DISCONFIRMED" if stale_verdict == "CONFIRMED"
                                 else "CONFIRMED" if stale_verdict == "DISCONFIRMED"
                                 else stale_verdict) if not query else stale_verdict))

        # The verdict comes from the readback, never from the status line.
        if unreachable:
            verdict = "INCONCLUSIVE"
        elif expect_change is None:
            verdict = ""
        else:
            verdict = "CONFIRMED" if changed == expect_change else "DISCONFIRMED"
        run.note("state_setmaster",
                 "%s: topology %s%s" % (
                     name, "CHANGED" if changed else "unchanged",
                     "" if expect_change is None else
                     " (the claim predicts %s)" % ("a change" if expect_change else "no change")),
                 "\n".join(rows) +
                 ("\n\nunreachable after the call: %s -- verdict withheld"
                  % ", ".join(unreachable) if unreachable else ""),
                 claim=claim, claim_verdict=verdict)

    # --- 1. bare /SetMaster, against each role -----------------------------
    case("bare /SetMaster on a standalone player",
         lambda: True, a, "", [a],
         claim="C-41-setmaster-bare-standalone", expect_change=False)

    case("bare /SetMaster on a master (does it dissolve its own group?)",
         lambda: make_group(run, a, [b]), a, "", [a, b],
         claim="C-42-setmaster-bare-master", expect_change=False)

    case("bare /SetMaster on a slave (the documented self-unjoin)",
         lambda: make_group(run, a, [b]), b, "", [a, b],
         claim="C-43-setmaster-bare-slave", expect_change=True)

    # --- 2. ?master= , the join form ---------------------------------------
    case("?master= on a standalone player: join that group",
         lambda: True, b, "?master=%s&port=%d" % (a.host, a.port), [a, b],
         claim="C-44-setmaster-master-param", expect_change=True)

    # C-54. The 21:47 run showed B taking A as its master while A's <slave> list
    # stayed empty and no group name appeared -- so the two grouping calls are
    # not symmetric, and a client that reads topology only from the master will
    # miss members that joined this way. Measured explicitly rather than being
    # left as an inference from a teardown that needed the fallback.
    b_info, a_info = fetch_sync(b), fetch_sync(a)
    if b_info.reachable and a_info.reachable and b_info.master:
        listed = any(r.id.split(":")[0] == b.host for r in a_info.slave_refs)
        run.note("state_setmaster",
                 "C-54: %s reports %s as its master; %s %s list %s as a slave"
                 % (b.label, a.label, a.label, "DOES" if listed else "does NOT", b.label),
                 "%s.slaves=%s group=%r / %s.master=%s group=%r\n\n"
                 "If the master does not list the joiner, membership created by "
                 "/SetMaster?master= is one-sided: build topology from the master's "
                 "<slave> list alone and this member is invisible. /AddSlave by contrast "
                 "produces both halves and a group name."
                 % (a.label, a_info.slaves, a_info.group,
                    b.label, b_info.master, b_info.group),
                 claim="C-54-setmaster-one-sided",
                 claim_verdict="CONFIRMED" if not listed else "DISCONFIRMED")
    else:
        run.note("state_setmaster", "C-54: could not read both ends after the join",
                 claim="C-54-setmaster-one-sided", claim_verdict="INCONCLUSIVE")

    case("?master= with port omitted",
         lambda: True, b, "?master=%s" % a.host, [a, b],
         claim="C-47-setmaster-noport", expect_change=True)

    case("?master= pointing at the player itself",
         lambda: True, b, "?master=%s&port=%d" % (b.host, b.port), [b],
         claim="C-48-setmaster-self", expect_change=False)

    case("?master= pointing at an address that is not a player",
         lambda: True, b, "?master=203.0.113.9&port=11000", [b],
         claim="C-49-setmaster-badtarget", expect_change=False)

    case("?master= issued by a player that is already a slave of someone else",
         lambda: make_group(run, a, [b]), b,
         "?master=%s&port=%d" % ((c or a).host, (c or a).port),
         [x for x in (a, b, c) if x],
         claim="C-50-setmaster-reparent", expect_change=True)

    # No claim on the case itself: a swap is a specific END STATE, not merely a
    # change. Judged from the readback below.
    case("?master= issued by a MASTER: the role reversal that keeps failing",
         lambda: make_group(run, a, [b]), a, "?master=%s&port=%d" % (b.host, b.port), [a, b])

    a_i, b_i = fetch_sync(a), fetch_sync(b)
    if not (a_i.reachable and b_i.reachable):
        run.note("state_setmaster", "C-39: could not read both ends after the attempt",
                 claim="C-39-master-swap", claim_verdict="INCONCLUSIVE")
    else:
        a_slaves = [r.id.split(":")[0] for r in a_i.slave_refs]
        b_slaves = [r.id.split(":")[0] for r in b_i.slave_refs]
        swapped = (a.host in b_slaves and not a_slaves
                   and a_i.master.split(":")[0] == b.host)
        circular = (a_i.master.split(":")[0] == b.host
                    and b_i.master.split(":")[0] == a.host)
        if swapped:
            verdict, what = "CONFIRMED", "the roles really swapped"
        elif circular:
            verdict, what = ("DISCONFIRMED",
                             "NOT a swap: each player now names the other as its master, "
                             "a mutual master loop that nothing else in the protocol "
                             "produces")
        else:
            verdict, what = "DISCONFIRMED", "the roles did not swap"
        run.note("state_setmaster", "C-39: %s" % what,
                 "%s: master=%s slaves=%s group=%r\n%s: master=%s slaves=%s group=%r\n\n"
                 "A swap would leave %s with no master and %s as its slave. Anything else "
                 "means role is fixed at group formation and the group must be dissolved "
                 "and re-formed from the intended master -- which is what the official "
                 "app does."
                 % (a.label, a_i.master or "-", a_slaves, a_i.group,
                    b.label, b_i.master or "-", b_slaves, b_i.group,
                    b.label, a.label),
                 claim="C-39-master-swap", claim_verdict=verdict)

    # --- 3. ?slave= , reported as not a parameter this endpoint takes -------
    case("?slave= on a master (reported ignored)",
         lambda: make_group(run, a, [b]), a, "?slave=%s&port=%d" % (b.host, b.port), [a, b],
         claim="C-45-setmaster-slave-param", expect_change=False)

    case("?slave= on a standalone player",
         lambda: True, a, "?slave=%s&port=%d" % (b.host, b.port), [a, b])

    # --- 4. the nested case, where <master> and <slave> coexist -------------
    if c:
        def nest() -> bool:
            if not make_group(run, b, [c]):
                return False
            run.call(a, "/AddSlave?slave=%s&port=%d" % (b.host, b.port), safety=SAFETY_STATE,
                     note="set up: attach master %s under %s to create a nested group"
                          % (b.label, a.label), spec_ref="14", save=False, quiet=True)
            time.sleep(2.5)
            nested = fetch_sync(b)
            return bool(nested.master and nested.slaves)

        case("bare /SetMaster on a NESTED master (both <master> and <slave> present)",
             nest, b, "", [a, b, c],
             claim="C-51-setmaster-nested", expect_change=True)

    # --- 5. restore ---------------------------------------------------------
    run.banner("state_setmaster -- restoring the original topology")
    _still, _fb = teardown_groups(run, ps)
    rebuild_groups(run, baseline)
    same, detail = topology_matches(run, baseline)
    undo_topo["done"] = same
    run.note("state_setmaster", "original topology restored: %s" % ("yes" if same else "NO"),
             detail,
             verdict="OK" if same else "ERROR")




def suite_state_capture(run: Runner) -> None:
    """Stage each documented topology and playback state, and capture it.

    The hand-made `captures/` folder exists because someone once set up a nested
    group playing Tidal and saved the XML by hand. That is not reproducible, not
    dated, not redacted, and nobody knows which firmware produced it. This suite
    walks the same states deliberately and captures every player at each one, so
    the reference set is a build artefact rather than a folder of souvenirs.

    Writes CAPTURES.md, an index from state to probe id to file.
    """
    run.current_suite = "state_capture"
    run.banner("state_capture -- stage each topology and capture every player")
    ps = run.writable()
    if len(ps) < 2:
        run.note("state_capture", "needs at least two writable players; skipped",
                 verdict="ERROR")
        return

    baseline = {p.label: take_snapshot(p) for p in ps}
    undo_topo = defer_topology(run, ps, baseline)
    index: List[Tuple[str, str, str, str]] = []      # state, player, probe id, file

    def capture(state: str, players: Sequence[Player], extras: Sequence[str] = ()) -> None:
        """Capture the identity and playback state of each player, labelled."""
        time.sleep(2.0)
        for p in players:
            for path in ("/SyncStatus", "/Status") + tuple(extras):
                pr = run.call(p, path, note="[capture] %s -- %s on %s"
                              % (state, path, p.label), spec_ref="2", timeout=20)
                if pr.body_file:
                    index.append((state, p.label, pr.id, pr.body_file))
        run.note("state_capture", "captured state: %s" % state,
                 "players: %s" % ", ".join(p.label for p in players))

    a, b = ps[0], ps[1]
    c = ps[2] if len(ps) > 2 else None
    d = ps[3] if len(ps) > 3 else None

    # ---- 0. whatever is already playing, captured BEFORE anything is staged.
    #
    # The two status captures in the hand-made set that nothing reproduced were
    # content-dependent: a RadioParadise stream with <actions>, and an MQA
    # stream whose quality fields only exist for that stream. No harness can
    # conjure those. What it can do is capture them if you start them: put the
    # stream on before running this suite and it lands here, labelled with the
    # service and quality it actually found.
    for p in ps:
        snap = take_snapshot(p)
        if snap.state not in ("play", "stream"):
            continue
        raw = http_call(p.host, p.port, "/Status", timeout=10)
        text = raw.body.decode("utf-8", "replace") if raw.body else ""
        quality = element_text(text, "quality") or element_text(text, "streamFormat")
        label = "playing as-found: %s%s" % (snap.service or "unknown service",
                                            (" " + quality) if quality else "")
        capture(label, [p])
        run.note("state_capture",
                 "captured the source that was already playing on %s" % p.label,
                 "service=%s quality=%s. Anything content-dependent -- MQA fields, "
                 "<actions> on a radio stream -- can only be captured this way: start "
                 "the stream, then run this suite."
                 % (snap.service or "-", quality or "-"))

    # ---- 1. every player standalone, the baseline shape
    if not ensure_standalone(run, ps, "capture baseline"):
        run.note("state_capture", "could not reach an all-standalone start",
                 "captures below are labelled but the topology is not what the "
                 "label says; treat them as suspect", verdict="ERROR")
    capture("standalone", ps, extras=("/Presets", "/Playlist", "/Volume"))

    # ---- 2. playback running, so /Status has content rather than <state>stop
    started = False
    for p in ps:
        raw = http_call(p.host, p.port, "/Presets", timeout=10)
        ids = re.findall(r'<preset\b[^>]*\bid="(\d+)"',
                         raw.body.decode("utf-8", "replace") if raw.body else "")
        if ids:
            cap_before = take_snapshot(p)
            defer_transport(run, p, cap_before)
            cap_volume(run, p, cap_before)
            run.write(p, "/Preset?id=%s" % ids[0],
                      "capture setup: start playback on %s from preset %s" % (p.label, ids[0]))
            started = True
            capture("playing (preset recall)", [p])
            break
    if not started:
        run.note("state_capture", "no player has a preset, so no playing-state capture",
                 "A /Status captured while stopped shows none of the now-playing "
                 "elements. Configure one preset on any player to fill this gap.")

    # ---- 3. a simple two-player group, from the master's side
    if make_group(run, a, [b]):
        capture("group: %s master, %s slave" % (a.label, b.label), [a, b])
    else:
        run.note("state_capture", "could not form the two-player group", verdict="ERROR")

    # ---- 4. three players in one group
    if c and make_group(run, a, [c]):
        capture("group: %s master, %s + %s slaves" % (a.label, b.label, c.label), [a, b, c])

    # ---- 5. the nested case: a master that is itself a slave
    ensure_standalone(run, ps, "before nesting")
    if c and make_group(run, b, [c]):
        run.write(a, "/AddSlave?slave=%s&port=%d" % (b.host, b.port),
                  "capture setup: nest %s (a master) under %s" % (b.label, a.label))
        time.sleep(2.5)
        info = fetch_sync(b)
        if info.master and info.slaves:
            capture("nested: %s -> %s -> %s" % (a.label, b.label, c.label), [a, b, c])
        else:
            run.note("state_capture", "nesting did not take",
                     "%s: master=%s slaves=%s" % (b.label, info.master, info.slaves),
                     verdict="UNEXPECTED")

    # ---- 6. the one-sided shape, which no capture in the old set showed
    ensure_standalone(run, ps, "before the one-sided join")
    joiner = d or b
    run.write(joiner, "/SetMaster?master=%s&port=%d" % (a.host, a.port),
              "capture setup: %s joins %s slave-side" % (joiner.label, a.label))
    capture("one-sided: %s joined %s via ?master=" % (joiner.label, a.label), [a, joiner])

    # ---- restore
    ensure_standalone(run, ps, "capture teardown")
    rebuild_groups(run, baseline)
    ok, detail = topology_matches(run, baseline)
    undo_topo["done"] = ok
    run.note("state_capture", "original topology restored: %s" % ("yes" if ok else "NO"),
             detail, verdict="OK" if ok else "ERROR")

    run.facts["capture_index"] = [list(row) for row in index]
    run.note("state_capture", "%d labelled captures across %d states"
             % (len(index), len({r[0] for r in index})),
             "\n".join("%-46s %-3s %-22s %s" % r for r in index))


def _slug(text: str) -> str:
    out = re.sub(r"[^A-Za-z0-9]+", "-", text).strip("-").lower()
    return (out[:58] or "state")


def write_capture_library(run: Runner, bundle: Path) -> List[Tuple[str, str, str, str]]:
    """Copy the staged captures into a browsable tree.

    `raw/019-state_capture.xml` tells a reader nothing. The old hand-made folder
    was navigable precisely because its filenames said what each file was, and
    that is the property worth keeping.

        captures/group-a-master-b-slave/A-SyncStatus.xml
        captures/nested-a-b-c/B-Status.xml
    """
    rows = [tuple(r) for r in (run.facts.get("capture_index") or [])]
    if not rows:
        return []
    out: List[Tuple[str, str, str, str]] = []
    for state, player, pid, relpath in rows:
        src = bundle / relpath
        if not src.exists():
            continue
        endpoint = "root"
        for pr in run.results:
            if pr.id == pid:
                endpoint = pr.path.split("?")[0].strip("/").replace("/", "-") or "root"
                break
        folder = bundle / "captures" / _slug(state)
        folder.mkdir(parents=True, exist_ok=True)
        dest = folder / ("%s-%s%s" % (player, endpoint, src.suffix))
        n = 2
        while dest.exists():
            dest = folder / ("%s-%s-%d%s" % (player, endpoint, n, src.suffix))
            n += 1
        dest.write_text(src.read_text(encoding="utf-8"), encoding="utf-8")
        out.append((state, player, pid, str(dest.relative_to(bundle))))
    return out


def build_captures_index(run: Runner, library: Optional[List[Tuple[str, str, str, str]]] = None) -> str:
    rows = library if library is not None else [tuple(r) for r in (run.facts.get("capture_index") or [])]
    lines = ["# Capture index",
             "",
             "Every response below was captured with the topology or playback state",
             "named in the first column, staged deliberately by the `state_capture`",
             "suite rather than set up by hand. Each is redacted and dated by the",
             "bundle it lives in.",
             ""]
    if not rows:
        lines += ["No staged captures in this run. Add the `state_capture` suite:",
                  "",
                  "```",
                  "bluos-probe.py --discover --allow-state --suite state_capture",
                  "```", ""]
        return "\n".join(lines)
    lines += ["Files are also copied into `captures/<state>/<player>-<endpoint>.xml`,",
              "which is the browsable form. `raw/` keeps the originals under their",
              "probe ids.",
              "",
              "| state | player | probe | file |", "|---|---|---|---|"]
    for state, player, pid, path in rows:
        lines.append("| %s | %s | `%s` | `%s` |" % (state, player, pid, path))
    lines += ["",
              "## What this does not cover",
              "",
              "Third-party sample responses -- BluShell's schema-25 captures and",
              "similar -- are not hardware captures and cannot be regenerated here.",
              "They belong in a separate reference folder, cited as `[T]`, not in a",
              "folder of machine-produced captures.",
              ""]
    return "\n".join(lines)


SUITES.update({
    "state_volume": suite_state_volume,
    "state_playback": suite_state_playback,
    "state_sleep": suite_state_sleep,
    "state_name": suite_state_name,
    "state_setting": suite_state_setting,
    "state_preset": suite_state_preset,
    "state_source": suite_state_source,
    "state_grouping": suite_state_grouping,
    "state_capture": suite_state_capture,
    "state_setmaster": suite_state_setmaster,
    "inputs": suite_inputs,
})


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\ninterrupted")
        sys.exit(130)
