# Findings

Generated from this run. Nothing here is inferred: every row cites the
probe that produced it, and the response body is in `raw/`.

| | |
|---|---|
| bundle | `bluos-probe-20260911T220626` |
| date | 2026-09-11 |
| fleet | Bluesound N110, Bluesound N130, Bluesound N132 |
| firmware | 4.16.22 |
| schemaVersion | 34 |

## Claim results

| claim | verdict | what was claimed | source | § | evidence |
|---|---|---|---|---|---|

### Not exercised by this run

Recorded so the gap stays visible. `INCONCLUSIVE` and `untested` are
different things and neither should be read as `DISCONFIRMED`.

- `C-01-diagnostics-80` — /diagnostics answers on port 80 (blutui (Rust), §13)
- `C-02-diagnostics-11000` — /diagnostics does NOT answer on port 11000 (hardware, this project, §13)
- `C-03-audiomodes-read` — bare GET /audiomodes is a read returning <audiomode> (BluShell (schema 25), §10.4)
- `C-04-proxytoslave` — /proxyToSlave exists as a POST relay to a slave (blutui (Rust), §10.0)
- `C-05-sync-legacy` — the legacy /Sync grouping endpoint still exists (bluos-dashboard, §5.2)
- `C-06-getsettings` — /GetSettings exists and returns JSON (BluOS Integration Utility 1.8.1, §10.1)
- `C-07-artwork-cors` — /Artwork sends Access-Control-Allow-Origin: * (BluShepherd (2016, fw 2.8.3), §9)
- `C-08-artwork-noetag` — /Artwork sends no ETag and no Last-Modified (BluShepherd (2016), §9)
- `C-09-artwork-nonefound` — /Artwork answers <artwork>none found</artwork> when there is none (BluShell, §9)
- `C-10-artwork-byname` — /Artwork?album=&artist= selects artwork by name (2015 forum, BluShepherd, §9)
- `C-11-radio-attrs` — radio items carry key / is_active / guide_id / preset_id / subtext (Blu4Net, BluShell, §11.10)
- `C-12-radio-totalcount` — <radiotime> carries a total_count attribute (Blu4Net, §11.10)
- `C-13-search-containers` — /Search returns per-type containers (BluShell (schema 25), §11.10)
- `C-14-songs-album-wrapper` — album-scoped /Songs nests <song> inside <album>, with <discno>n/m</discno> (BluShepherd (2016), §11.10)
- `C-15-alarms-bitmask` — /Alarms encodes days as a bitmask (BluShell (schema 25), §11.6)
- `C-16-shares-11000` — /Shares has migrated to port 11000 (conjecture (ms -> ms-go migration), §13)
- `C-17-is-preset` — <is_preset> appears as a /Status element (Blu4Net, §2.2)
- `C-18-sort-descending` — a descending sort value is accepted (reverseName) (Android controller reads the attribute, §8.2)
- `C-19-lsdp-unicast-R` — an R query sent by unicast is answered (vendor wire format; no client sends it, §12.1)
- `C-20-browse-sid` — sid is required on /Browse (bluos-api-rs, §15.1)
- `C-21-schema-headers` — omitting X-Sovi-Schema-Version changes the response (inference in the specification, §1.4)
- `C-22-page-cap-50` — browse paging is capped server-side at 50 items (hardware, this project, §8.2)
- `C-23-11001-settings-only` — port 11001 serves settings and nothing else (hardware, this project, §10.3)
- `C-24-player-enumeration` — some endpoint enumerates players outside a group (open question 7, §16)
- `C-30-removeslave-bare` — a bare /RemoveSlave ungroups every slave (bluos HA integration (Pimmeke1989), §17)
- `C-31-channelmode-numeric` — /AddSlave takes channelMode=0|1|2 (bluos HA integration (Pimmeke1989), §17)
- `C-32-addslave-noport` — port is optional in the singular /AddSlave form (2015 forum, §5)
- `C-33-slavevolume-combined` — /SlaveVolume accepts slave=<ip>:<port> (blutui (Rust), §4)
- `C-34-name-post` — /Name accepts a POST body of nodename= (blutui (Rust), §10)
- `C-35-setting-post` — setting writes are POST form, not GET query (blutui (Rust) vs pyblu, §10.3)
- `C-36-mute-polarity` — mute=1 mutes and mute=0 unmutes (vendor doc is inverted) (Android app vs CI API v1.7 3.1, §4)
- `C-37-play-inputtype` — /Play?inputType=&index= selects an input (bluos-api-rs, §15.2)
- `C-38-play-roots` — the play response has four possible root elements (Blu4Net, §7.3)
- `C-39-master-swap` — master and slave roles can be swapped without ungrouping first (open question raised by the tester, §5.3)
- `C-40-repeat-shuffle-read` — bare /Repeat and /Shuffle read rather than write (untested, §3)
- `C-41-setmaster-bare-standalone` — a bare /SetMaster on a standalone player is a no-op (hardware, single pass, §5.3)
- `C-42-setmaster-bare-master` — a bare /SetMaster on a master is a no-op and does not dissolve its group (hardware, single pass, §5.3)
- `C-43-setmaster-bare-slave` — a bare /SetMaster on a slave leaves the group (hardware, single pass, §5.3)
- `C-44-setmaster-master-param` — /SetMaster?master= joins that player's group (hardware, single pass, §5.3)
- `C-45-setmaster-slave-param` — /SetMaster ignores a slave= parameter (hardware, single pass, §5.3)
- `C-46-setmaster-stale-response` — /SetMaster?master= answers with the PRE-call SyncStatus, same etag (hardware, single pass, §5.3)
- `C-47-setmaster-noport` — port is optional on /SetMaster?master= (untested, §5.3)
- `C-48-setmaster-self` — /SetMaster?master=<own address> is handled gracefully (untested, §5.3)
- `C-49-setmaster-badtarget` — /SetMaster?master=<not a player> is handled gracefully (untested, §5.3)
- `C-50-setmaster-reparent` — a slave can be reparented onto another master with ?master= (bluos-dashboard (orphan recovery), §5.1)
- `C-51-setmaster-nested` — a bare /SetMaster on a nested master detaches it cleanly (untested, §14)
- `C-52-disabled-input-hidden` — an input disabled in the app still appears in some API surface (raised by the tester, §8.1)
- `C-53-disabled-input-playable` — an input disabled in the app can still be selected through the API (raised by the tester, §15.2)
- `C-54-setmaster-one-sided` — a group formed by /SetMaster?master= is one-sided: the master does not list the joiner as a <slave> (hardware, this project, §5.3)
- `C-55-setmaster-bare-fresh` — a bare /SetMaster answers with the POST-call SyncStatus (fresh etag) (hardware, this project, §5.3)

---

## Rows for the specification's disconfirmation register

Append these. Do not delete a row when a later firmware changes the
answer -- add a second row. The point of the register is that a reader
who meets the same claim in a third-party project can see it was already
checked, when, against what, and with what result.

```markdown
(nothing disconfirmed or inconclusive in this run)
```

Column order: claim id - claim - source - verdict - tested against -
the request and its answer - evidence pointer.

---

## Capture fidelity

21 captured bodies are **byte-for-byte what the device sent** -- redaction changed nothing in them, so they are usable as parser fixtures and as evidence about byte lengths without qualification.

17 were modified. For each, `body_bytes_wire` in `MANIFEST.json` gives the original length and `redaction_edits` the number of substitutions, so a length-sensitive claim can still be checked. The digest recorded in the bundle is of the **redacted** body; because redaction is deterministic and stable within a run, two redacted digests still compare correctly against each other. Digests of the original bodies are in the do-not-share key file only, because for a templated body they would recover the redacted values by brute force.

| probe | endpoint | wire bytes | written bytes | edits |
|---|---|---|---|---|
| `001-state_capture` | `/SyncStatus` | 414 | 410 | 2 |
| `005-state_capture` | `/SyncStatus` | 414 | 410 | 2 |
| `007-state_capture` | `/Presets` | 294 | 294 | 2 |
| `008-state_capture` | `/Playlist` | 18246 | 18246 | 1 |
| `010-state_capture` | `/SyncStatus` | 397 | 393 | 2 |
| `015-state_capture` | `/SyncStatus` | 394 | 390 | 2 |
| `020-state_capture` | `/SyncStatus` | 391 | 387 | 2 |
| `022-state_capture` | `/Presets` | 424 | 424 | 2 |
| `023-state_capture` | `/Playlist` | 10138 | 10138 | 1 |
| `029-state_capture` | `/SyncStatus` | 414 | 410 | 2 |
| `033-state_capture` | `/SyncStatus` | 544 | 536 | 3 |
| `035-state_capture` | `/SyncStatus` | 441 | 433 | 3 |
| `043-state_capture` | `/SyncStatus` | 544 | 536 | 3 |
| `045-state_capture` | `/SyncStatus` | 575 | 563 | 4 |
| `047-state_capture` | `/SyncStatus` | 440 | 432 | 3 |
| `054-state_capture` | `/SyncStatus` | 414 | 410 | 2 |
| `056-state_capture` | `/SyncStatus` | 455 | 447 | 3 |
