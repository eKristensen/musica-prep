# BluOS probe run -- results

| | |
|---|---|
| harness | bluos-probe.py 1.4 |
| started | 2026-09-10T22:51:09 |
| duration | 25.1 s |
| timezone declared to devices | `Europe/Copenhagen` (`X-Sovi-Tz`) |
| harness host clock | CEST (UTC+0200) |
| probes | 8 |
| verdicts | INFO 5, OK 2, UNEXPECTED 1 |
| safety classes run | read, probe |

`OK` means the result matched what the specification predicts.
`UNEXPECTED` means it did not -- those rows are the interesting ones.
`INFO` means no prediction was recorded, so the capture is the result.

## Players

| label | name | model | firmware | schema | topology |
|---|---|---|---|---|---|
| A | Stue | Bluesound N132 | 4.16.22 | 34 | standalone |
| B | Kontor | Bluesound N130 | 4.16.22 | 34 | standalone |
| C | Køkken | Bluesound N132 | 4.16.22 | 34 | standalone |
| D | Soveværelse | Bluesound N110 | 4.16.22 | 34 | standalone |

## Results that did not match the specification

| id | player | request | status | expected | note |
|---|---|---|---|---|---|
| `007-discovery` | - | `:0 (analysis)` | - | `` | no player answered a UNICAST LSDP query of either form |

## Claim checks

Every probe aimed at a marked claim in the specification, so the
register in section 17 can be updated from one table. `root` and
`bytes` are usually enough to tell a real answer from a 404.

| id | claim | verdict | player | port | request | status | root | note |
|---|---|---|---|---|---|---|---|---|
| `004-discovery` | `C-19-lsdp-unicast-R` | INCONCLUSIVE | - | 11430 | `LSDP R unicast to player A (T-26)` | - | `` | LSDP R unicast to player A (T-26) |
| `006-discovery` | `C-19-lsdp-unicast-R` | INCONCLUSIVE | - | 11430 | `LSDP R unicast to player B (T-26)` | - | `` | LSDP R unicast to player B (T-26) |

## suite: discovery

| id | v | player | port | request | status | ms | type | root | bytes | note |
|---|---|---|---|---|---|---|---|---|---|---|
| `001-discovery` | O | - | 11430 | `UDP LSDP Q on interface broadcasts, listening on 11430 (class 0xFFFF)` | - | - |  | `` | - | LSDP Q on interface broadcasts, listening on 11430 (class 0xFFFF) |
| `002-discovery` | O | - | 11430 | `UDP LSDP Q broadcast, four player classes` | - | - |  | `` | - | LSDP Q broadcast, four player classes |
| `003-discovery` | I | - | 11430 | `UDP LSDP Q unicast to player A (control for T-26)` | - | - |  | `` | - | LSDP Q unicast to player A (control for T-26) |
| `004-discovery` | I | - | 11430 | `UDP LSDP R unicast to player A (T-26)` | - | - |  | `` | - | LSDP R unicast to player A (T-26) |
| `005-discovery` | I | - | 11430 | `UDP LSDP Q unicast to player B (control for T-26)` | - | - |  | `` | - | LSDP Q unicast to player B (control for T-26) |
| `006-discovery` | I | - | 11430 | `UDP LSDP R unicast to player B (T-26)` | - | - |  | `` | - | LSDP R unicast to player B (T-26) |
| `007-discovery` | U | | | *analysis* | | | | | | **no player answered a UNICAST LSDP query of either form** |
| `008-discovery` | I | | | *analysis* | | | | | | **mDNS is not probed by this harness** |

### discovery -- analysis detail

**no player answered a UNICAST LSDP query of either form** (`007-discovery`)

```
So T-26 is inconclusive rather than disconfirmed: the datagrams may never have arrived. Check the host firewall and subnet, then re-run.
```

**mDNS is not probed by this harness** (`008-discovery`)

```
Run separately:  avahi-browse -rt _musc._tcp   or   dns-sd -B _musc._tcp
```

## Bodies

Response bodies are in `raw/`, one file per probe id, alongside a
`.head.txt` with the status line and response headers. Binary
bodies (artwork) are not stored: only their length, content type
and first bytes are recorded here, so no embedded metadata can
leak. Their SHA-256 is in the do-not-share key file, not in this
bundle.
