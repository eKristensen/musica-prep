# Findings

Generated from this run. Nothing here is inferred: every row cites the
probe that produced it, and the response body is in `raw/`.

| | |
|---|---|
| bundle | `bluos-probe-20260910T225427` |
| date | 2026-09-10 |
| fleet | Bluesound N110, Bluesound N130, Bluesound N132 |
| firmware | 4.16.22 |
| schemaVersion | 34 |

## Claim results

| claim | verdict | what was claimed | source | § | evidence |
|---|---|---|---|---|---|
| `C-17-is-preset` | **DISCONFIRMED** | <is_preset> appears as a /Status element | Blu4Net | 2.2 | `167-state_preset`, `169-state_preset` |
| `C-30-removeslave-bare` | **DISCONFIRMED** | a bare /RemoveSlave ungroups every slave | bluos HA integration (Pimmeke1989) | 17 | `280-state_grouping` |
| `C-35-setting-post` | **DISCONFIRMED** | setting writes are POST form, not GET query | blutui (Rust) vs pyblu | 10.3 | `162-state_setting` |
| `C-40-repeat-shuffle-read` | **DISCONFIRMED** | bare /Repeat and /Shuffle read rather than write | untested | 3 | `087-state_playback`, `103-state_playback`, `119-state_playback`, `135-state_playback` |
| `C-53-disabled-input-playable` | **DISCONFIRMED** | an input disabled in the app can still be selected through the API | raised by the tester | 15.2 | `193-state_source`, `195-state_source`, `197-state_source`, `199-state_source`, `201-state_source` |
| `C-34-name-post` | **CONFIRMED** | /Name accepts a POST body of nodename= | blutui (Rust) | 10 | `152-state_name` |
| `C-37-play-inputtype` | **CONFIRMED** | /Play?inputType=&index= selects an input | bluos-api-rs | 15.2 | `189-state_source` |
| `C-33-slavevolume-combined` | **INCONCLUSIVE** | /SlaveVolume accepts slave=<ip>:<port> | blutui (Rust) | 4 | `259-state_grouping` |
| `C-36-mute-polarity` | **INCONCLUSIVE** | mute=1 mutes and mute=0 unmutes (vendor doc is inverted) | Android app vs CI API v1.7 3.1 | 4 | `008-state_volume`, `026-state_volume`, `044-state_volume`, `062-state_volume` |

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
- `C-18-sort-descending` — a descending sort value is accepted (reverseName) (Android controller reads the attribute, §8.2)
- `C-19-lsdp-unicast-R` — an R query sent by unicast is answered (vendor wire format; no client sends it, §12.1)
- `C-20-browse-sid` — sid is required on /Browse (bluos-api-rs, §15.1)
- `C-21-schema-headers` — omitting X-Sovi-Schema-Version changes the response (inference in the specification, §1.4)
- `C-22-page-cap-50` — browse paging is capped server-side at 50 items (hardware, this project, §8.2)
- `C-23-11001-settings-only` — port 11001 serves settings and nothing else (hardware, this project, §10.3)
- `C-24-player-enumeration` — some endpoint enumerates players outside a group (open question 7, §16)
- `C-31-channelmode-numeric` — /AddSlave takes channelMode=0|1|2 (bluos HA integration (Pimmeke1989), §17)
- `C-32-addslave-noport` — port is optional in the singular /AddSlave form (2015 forum, §5)
- `C-38-play-roots` — the play response has four possible root elements (Blu4Net, §7.3)
- `C-39-master-swap` — master and slave roles can be swapped without ungrouping first (open question raised by the tester, §5.3)
- `C-41-setmaster-bare-standalone` — a bare /SetMaster on a standalone player is a no-op (hardware, single pass, §5.3)
- `C-42-setmaster-bare-master` — a bare /SetMaster on a master is a no-op and does not dissolve its group (hardware, single pass, §5.3)
- `C-43-setmaster-bare-slave` — a bare /SetMaster on a slave leaves the group (hardware, single pass, §5.3)
- `C-44-setmaster-master-param` — /SetMaster?master= joins that player's group (hardware, single pass, §5.3)
- `C-45-setmaster-slave-param` — /SetMaster ignores a slave= parameter (hardware, single pass, §5.3)
- `C-46-setmaster-stale-response` — /SetMaster answers with the PRE-call SyncStatus, same etag (hardware, single pass, §5.3)
- `C-47-setmaster-noport` — port is optional on /SetMaster?master= (untested, §5.3)
- `C-48-setmaster-self` — /SetMaster?master=<own address> is handled gracefully (untested, §5.3)
- `C-49-setmaster-badtarget` — /SetMaster?master=<not a player> is handled gracefully (untested, §5.3)
- `C-50-setmaster-reparent` — a slave can be reparented onto another master with ?master= (bluos-dashboard (orphan recovery), §5.1)
- `C-51-setmaster-nested` — a bare /SetMaster on a nested master detaches it cleanly (untested, §14)
- `C-52-disabled-input-hidden` — an input disabled in the app still appears in some API surface (raised by the tester, §8.1)
- `C-54-setmaster-one-sided` — a group formed by /SetMaster?master= is one-sided: the master does not list the joiner as a <slave> (hardware, this project, §5.3)

### Not answerable on this hardware

Distinct from both `INCONCLUSIVE` and `untested`. These could not be
decided by this fleet, and a negative result for any of them would be a
fact about the hardware rather than about the protocol. **Do not record
any of these as `DISCONFIRMED`.**

- input selection is weakened: no player advertises two inputs, so 'it switched' cannot be separated from 'it was already there'. Temporarily enabling a second input makes the result conclusive
- T-14 authentication: no way found to set credentials on consumer N-series hardware; the auth path stays source-derived and unexercised
- CI-series multi-zone port offsets: no CI hardware in this fleet

---

## Rows for the specification's disconfirmation register

Append these. Do not delete a row when a later firmware changes the
answer -- add a second row. The point of the register is that a reader
who meets the same claim in a third-party project can see it was already
checked, when, against what, and with what result.

```markdown
| `C-17-is-preset` | <is_preset> appears as a /Status element | Blu4Net | DISCONFIRMED | 2026-09-10, fw 4.16.22, schema 34 | `GET :11000/Status` -> 200 | bluos-probe-20260910T225427: 167-state_preset, 169-state_preset |
| `C-30-removeslave-bare` | a bare /RemoveSlave ungroups every slave | bluos HA integration (Pimmeke1989) | DISCONFIRMED | 2026-09-10, fw 4.16.22, schema 34 | `- :0(analysis)` ->  | bluos-probe-20260910T225427: 280-state_grouping |
| `C-33-slavevolume-combined` | /SlaveVolume accepts slave=<ip>:<port> | blutui (Rust) | INCONCLUSIVE | 2026-09-10, fw 4.16.22, schema 34 | `GET :11000/SlaveVolume?slave=192.0.2.11:11000&db=0` -> 200 | bluos-probe-20260910T225427: 259-state_grouping |
| `C-35-setting-post` | setting writes are POST form, not GET query | blutui (Rust) vs pyblu | DISCONFIRMED | 2026-09-10, fw 4.16.22, schema 34 | `- :0(analysis)` ->  | bluos-probe-20260910T225427: 162-state_setting |
| `C-36-mute-polarity` | mute=1 mutes and mute=0 unmutes (vendor doc is inverted) | Android app vs CI API v1.7 3.1 | INCONCLUSIVE | 2026-09-10, fw 4.16.22, schema 34 | `GET :11000/Volume?mute=1` -> 200 | bluos-probe-20260910T225427: 008-state_volume, 026-state_volume, 044-state_volume, 062-state_volume |
| `C-40-repeat-shuffle-read` | bare /Repeat and /Shuffle read rather than write | untested | DISCONFIRMED | 2026-09-10, fw 4.16.22, schema 34 | `- :0(analysis)` ->  | bluos-probe-20260910T225427: 087-state_playback, 103-state_playback, 119-state_playback, 135-state_playback |
| `C-53-disabled-input-playable` | an input disabled in the app can still be selected through the API | raised by the tester | DISCONFIRMED | 2026-09-10, fw 4.16.22, schema 34 | `- :0(analysis)` ->  | bluos-probe-20260910T225427: 193-state_source, 195-state_source, 197-state_source, 199-state_source |
```

Column order: claim id - claim - source - verdict - tested against -
the request and its answer - evidence pointer.

## Promote out of the register

These were confirmed on hardware and can move from the `[T]` register
into the body of the specification as `[V hardware]`, citing this bundle.
The register row itself stays, as provenance.

- `C-34-name-post` -- /Name accepts a POST body of nodename= (section 10)
- `C-37-play-inputtype` -- /Play?inputType=&index= selects an input (section 15.2)

---

## Capture fidelity

63 captured bodies are **byte-for-byte what the device sent** -- redaction changed nothing in them, so they are usable as parser fixtures and as evidence about byte lengths without qualification.

22 were modified. For each, `body_bytes_wire` in `MANIFEST.json` gives the original length and `redaction_edits` the number of substitutions, so a length-sensitive claim can still be checked. The digest recorded in the bundle is of the **redacted** body; because redaction is deterministic and stable within a run, two redacted digests still compare correctly against each other. Digests of the original bodies are in the do-not-share key file only, because for a templated body they would recover the redacted values by brute force.

| probe | endpoint | wire bytes | written bytes | edits |
|---|---|---|---|---|
| `164-state_preset` | `/Presets` | 424 | 424 | 2 |
| `209-state_grouping` | `/AddSlave` | 108 | 104 | 1 |
| `212-state_grouping` | `/SyncStatus` | 544 | 536 | 3 |
| `215-state_grouping` | `/SyncStatus` | 441 | 433 | 3 |
| `223-state_grouping` | `/SyncStatus` | 544 | 536 | 3 |
| `226-state_grouping` | `/SyncStatus` | 441 | 433 | 3 |
| `230-state_grouping` | `/SetMaster` | 544 | 536 | 3 |
| `233-state_grouping` | `/SyncStatus` | 608 | 596 | 4 |
| `236-state_grouping` | `/SyncStatus` | 441 | 433 | 3 |
| `240-state_grouping` | `/RemoveSlave` | 544 | 536 | 3 |
| `241-state_grouping` | `/SetMaster` | 441 | 433 | 3 |
| `245-state_grouping` | `/AddSlave` | 108 | 104 | 1 |
| `248-state_grouping` | `/SyncStatus` | 525 | 517 | 3 |
| `251-state_grouping` | `/SyncStatus` | 458 | 450 | 3 |
| `256-state_grouping` | `/AddSlave` | 108 | 104 | 1 |
| `258-state_grouping` | `/SyncStatus` | 525 | 517 | 3 |
| `263-state_grouping` | `/AddSlave` | 108 | 104 | 1 |
| `269-state_grouping` | `/SyncStatus` | 525 | 517 | 3 |
| `270-state_grouping` | `/AddSlave` | 108 | 104 | 1 |
| `272-state_grouping` | `/SyncStatus` | 635 | 623 | 4 |
| `273-state_grouping` | `/RemoveSlave` | 635 | 623 | 4 |
| `276-state_grouping` | `/SyncStatus` | 635 | 623 | 4 |
