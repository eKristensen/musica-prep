# Redactions

Applied to every response body, response header and request URL
**before** anything was written to disk. Replacements are stable
within the run, so relationships between captures survive: the
same original always becomes the same placeholder.

## Policy

| class | replaced with | why that form |
|---|---|---|
| IPv4 | `192.0.2.x` | RFC 5737 TEST-NET-1: valid, parseable, non-routable, obviously documentation |
| IPv6 | `2001:db8::x` | RFC 3849 documentation prefix |
| MAC | `02:00:00:00:00:xx` | locally administered range; keeps the shape a parser expects |
| share / UNC host | `host-N.invalid` | reserved TLD, cannot resolve |
| e-mail | `userN@example.invalid` | |
| secret-named keys and elements | `[REDACTED-value-N]` | `password`, `token`, `ssid`, `username`, `serial`, `signature`, coordinates and similar |
| Bluetooth device names | `[REDACTED-value-N]` | these routinely contain a person's name |
| binary bodies (artwork) | not stored at all | only length, content type and SHA-256 are kept, so no embedded metadata can travel |

Player and room names are **kept**, because they carry no personal information and make the captures readable. Re-run with `--redact-names` to remove them.

Protocol constants are deliberately kept, because they identify
nobody's network: `0.0.0.0`, `1.1.1.1`, `127.0.0.1`, `224.0.0.251`, `239.255.255.250`, `255.255.255.255`, `8.8.4.4`, `8.8.8.8`. The RFC 5737 documentation ranges
(`192.0.2.0/24`, `198.51.100.0/24`, `203.0.113.0/24`) are also kept,
both because they are where placeholders come from and because the
harness deliberately sends one as an unreachable target.

## Counts

| class | distinct originals | replacements made |
|---|---|---|
| ipv4 | 7 | 844 |
| literal | 2 | 0 |
| mac | 125 | 451 |
| value | 6 | 9 |

The originals themselves are **not** in this bundle. They are in
`DO-NOT-SHARE-key-<timestamp>.json`, written next to the bundle
directory rather than inside it.

## Verification

Every file in the bundle was re-scanned after writing for the
original values, for private-range IPv4 addresses (RFC 1918,
CGNAT and link-local) and for MAC-shaped strings outside the
placeholder range. **Nothing was found.**

## Correction, 2026-09-12

**That verification missed the raw discovery captures.** `raw/428-discovery.txt`
and `raw/429-discovery.txt` carry each LSDP datagram twice: once parsed into
JSON, and once as a `raw_hex` string. The parsed copies were redacted correctly.
The hex copies were not, and inside them 26 fields still held four real device
MACs and the four real player addresses — the MACs as bare hex with no
separators, which is exactly the form the scanner of the day could not see.
`bluos-probe.py` gained `MAC_HEX_RE` for this in v1.4; this bundle predates that
fix and was never reprocessed.

The hex has now been rewritten so each datagram decodes to precisely the
placeholders its own parsed copy already published — the same four MACs
(`02:00:00:00:00:0b`–`0e`) and addresses (`192.0.2.11`–`.14`). Every length is
unchanged, so the packets are still structurally what was captured. All 42
objects were re-checked by decoding the hex and comparing it field by field
against the parsed JSON beside it: no mismatches, and no private address or
out-of-range MAC left anywhere in the bundle.

The claim above stands for every other file; for these two it was wrong, and is
recorded here rather than quietly corrected.
