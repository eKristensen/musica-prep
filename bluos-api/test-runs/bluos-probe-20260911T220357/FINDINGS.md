# Findings

Generated from this run. Nothing here is inferred: every row cites the
probe that produced it, and the response body is in `raw/`.

| | |
|---|---|
| bundle | `bluos-probe-20260911T220357` |
| date | 2026-09-11 |
| fleet | Bluesound N110, Bluesound N130, Bluesound N132 |
| firmware | 4.16.22 |
| schemaVersion | 34 |

## Claim results

| claim | verdict | what was claimed | source | § | evidence |
|---|---|---|---|---|---|
| `C-05-sync-legacy` | **DISCONFIRMED** | the legacy /Sync grouping endpoint still exists | bluos-dashboard | 5.2 | `210-claims` |
| `C-06-getsettings` | **DISCONFIRMED** | /GetSettings exists and returns JSON | BluOS Integration Utility 1.8.1 | 10.1 | `201-claims`, `203-claims` |
| `C-11-radio-attrs` | **DISCONFIRMED** | radio items carry key / is_active / guide_id / preset_id / subtext | Blu4Net, BluShell | 11.10 | `211-claims`, `213-claims`, `215-claims`, `217-claims`, `223-inputs`, `230-inputs` |
| `C-12-radio-totalcount` | **DISCONFIRMED** | <radiotime> carries a total_count attribute | Blu4Net | 11.10 | `212-claims`, `214-claims`, `216-claims`, `218-claims` |
| `C-13-search-containers` | **DISCONFIRMED** | /Search returns per-type containers | BluShell (schema 25) | 11.10 | `219-claims`, `220-claims` |
| `C-16-shares-11000` | **DISCONFIRMED** | /Shares has migrated to port 11000 | conjecture (ms -> ms-go migration) | 13 | `206-claims`, `208-claims` |
| `C-17-is-preset` | **DISCONFIRMED** | <is_preset> appears as a /Status element | Blu4Net | 2.2 | `221-claims` |
| `C-20-browse-sid` | **DISCONFIRMED** | sid is required on /Browse | bluos-api-rs | 15.1 | `393-browse` |
| `C-01-diagnostics-80` | **CONFIRMED** | /diagnostics answers on port 80 | blutui (Rust) | 13 | `195-claims`, `197-claims` |
| `C-02-diagnostics-11000` | **CONFIRMED** | /diagnostics does NOT answer on port 11000 | hardware, this project | 13 | `196-claims`, `198-claims` |
| `C-04-proxytoslave` | **CONFIRMED** | /proxyToSlave exists as a POST relay to a slave | blutui (Rust) | 10.0 | `209-claims` |
| `C-07-artwork-cors` | **CONFIRMED** | /Artwork sends Access-Control-Allow-Origin: * | BluShepherd (2016, fw 2.8.3) | 9 | `250-artwork` |
| `C-08-artwork-noetag` | **CONFIRMED** | /Artwork sends no ETag and no Last-Modified | BluShepherd (2016) | 9 | `251-artwork` |
| `C-21-schema-headers` | **CONFIRMED** | omitting X-Sovi-Schema-Version changes the response | inference in the specification | 1.4 | `077-transport` |
| `C-22-page-cap-50` | **CONFIRMED** | browse paging is capped server-side at 50 items | hardware, this project | 8.2 | `372-browse` |
| `C-23-11001-settings-only` | **CONFIRMED** | port 11001 serves settings and nothing else | hardware, this project | 10.3 | `423-settings`, `424-settings`, `425-settings`, `426-settings`, `427-settings` |
| `C-24-player-enumeration` | **CONFIRMED** | some endpoint enumerates players outside a group | open question 7 | 16 | `137-ports`, `138-ports`, `139-ports`, `140-ports`, `141-ports` |
| `C-03-audiomodes-read` | **INCONCLUSIVE** | bare GET /audiomodes is a read returning <audiomode> | BluShell (schema 25) | 10.4 | `199-claims`, `200-claims` |
| `C-09-artwork-nonefound` | **INCONCLUSIVE** | /Artwork answers <artwork>none found</artwork> when there is none | BluShell | 9 | `255-artwork` |
| `C-10-artwork-byname` | **INCONCLUSIVE** | /Artwork?album=&artist= selects artwork by name | 2015 forum, BluShepherd | 9 | `257-artwork` |
| `C-15-alarms-bitmask` | **INCONCLUSIVE** | /Alarms encodes days as a bitmask | BluShell (schema 25) | 11.6 | `009-env`, `020-env`, `031-env`, `042-env` |
| `C-18-sort-descending` | **INCONCLUSIVE** | a descending sort value is accepted (reverseName) | Android controller reads the attribute | 8.2 | `390-browse` |
| `C-19-lsdp-unicast-R` | **INCONCLUSIVE** | an R query sent by unicast is answered | vendor wire format; no client sends it | 12.1 | `431-discovery`, `433-discovery` |
| `C-52-disabled-input-hidden` | **INCONCLUSIVE** | an input disabled in the app still appears in some API surface | raised by the tester | 8.1 | `228-inputs`, `235-inputs`, `242-inputs`, `249-inputs` |

### Not exercised by this run

Recorded so the gap stays visible. `INCONCLUSIVE` and `untested` are
different things and neither should be read as `DISCONFIRMED`.

- `C-14-songs-album-wrapper` — album-scoped /Songs nests <song> inside <album>, with <discno>n/m</discno> (BluShepherd (2016), §11.10)
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
- `C-53-disabled-input-playable` — an input disabled in the app can still be selected through the API (raised by the tester, §15.2)
- `C-54-setmaster-one-sided` — a group formed by /SetMaster?master= is one-sided: the master does not list the joiner as a <slave> (hardware, this project, §5.3)
- `C-55-setmaster-bare-fresh` — a bare /SetMaster answers with the POST-call SyncStatus (fresh etag) (hardware, this project, §5.3)

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
| `C-03-audiomodes-read` | bare GET /audiomodes is a read returning <audiomode> | BluShell (schema 25) | INCONCLUSIVE | 2026-09-11, fw 4.16.22, schema 34 | `GET :11000/audiomodes` -> 200 | bluos-probe-20260911T220357: 199-claims, 200-claims |
| `C-05-sync-legacy` | the legacy /Sync grouping endpoint still exists | bluos-dashboard | DISCONFIRMED | 2026-09-11, fw 4.16.22, schema 34 | `GET :11000/Sync` -> 404 | bluos-probe-20260911T220357: 210-claims |
| `C-06-getsettings` | /GetSettings exists and returns JSON | BluOS Integration Utility 1.8.1 | DISCONFIRMED | 2026-09-11, fw 4.16.22, schema 34 | `GET :11000/GetSettings` -> 404 | bluos-probe-20260911T220357: 201-claims, 203-claims |
| `C-09-artwork-nonefound` | /Artwork answers <artwork>none found</artwork> when there is none | BluShell | INCONCLUSIVE | 2026-09-11, fw 4.16.22, schema 34 | `GET :11000/Artwork?service=LocalMusic&fn=%2Fdoes%2Fnot%2Fexist.flac` -> 301 | bluos-probe-20260911T220357: 255-artwork |
| `C-10-artwork-byname` | /Artwork?album=&artist= selects artwork by name | 2015 forum, BluShepherd | INCONCLUSIVE | 2026-09-11, fw 4.16.22, schema 34 | `GET :11000/Artwork?service=LocalMusic&album=Heaven&artist=Alex%20Adair` -> 301 | bluos-probe-20260911T220357: 257-artwork |
| `C-11-radio-attrs` | radio items carry key / is_active / guide_id / preset_id / subtext | Blu4Net, BluShell | DISCONFIRMED | 2026-09-11, fw 4.16.22, schema 34 | `GET :11000/RadioPresets?service=Airable` -> 200 | bluos-probe-20260911T220357: 211-claims, 213-claims, 215-claims, 217-claims |
| `C-12-radio-totalcount` | <radiotime> carries a total_count attribute | Blu4Net | DISCONFIRMED | 2026-09-11, fw 4.16.22, schema 34 | `GET :11000/RadioBrowse?service=Airable` -> 200 | bluos-probe-20260911T220357: 212-claims, 214-claims, 216-claims, 218-claims |
| `C-13-search-containers` | /Search returns per-type containers | BluShell (schema 25) | DISCONFIRMED | 2026-09-11, fw 4.16.22, schema 34 | `GET :11000/Search?service=LocalMusic&expr=a` -> 404 | bluos-probe-20260911T220357: 219-claims, 220-claims |
| `C-15-alarms-bitmask` | /Alarms encodes days as a bitmask | BluShell (schema 25) | INCONCLUSIVE | 2026-09-11, fw 4.16.22, schema 34 | `GET :11000/Alarms` -> 200 | bluos-probe-20260911T220357: 009-env, 020-env, 031-env, 042-env |
| `C-16-shares-11000` | /Shares has migrated to port 11000 | conjecture (ms -> ms-go migration) | DISCONFIRMED | 2026-09-11, fw 4.16.22, schema 34 | `GET :11000/Shares` -> 404 | bluos-probe-20260911T220357: 206-claims, 208-claims |
| `C-17-is-preset` | <is_preset> appears as a /Status element | Blu4Net | DISCONFIRMED | 2026-09-11, fw 4.16.22, schema 34 | `GET :11000/Status` -> 200 | bluos-probe-20260911T220357: 221-claims |
| `C-18-sort-descending` | a descending sort value is accepted (reverseName) | Android controller reads the attribute | INCONCLUSIVE | 2026-09-11, fw 4.16.22, schema 34 | `- :0(analysis)` ->  | bluos-probe-20260911T220357: 390-browse |
| `C-19-lsdp-unicast-R` | an R query sent by unicast is answered | vendor wire format; no client sends it | INCONCLUSIVE | 2026-09-11, fw 4.16.22, schema 34 | `UDP :11430LSDP R unicast to player A (T-26)` ->  | bluos-probe-20260911T220357: 431-discovery, 433-discovery |
| `C-20-browse-sid` | sid is required on /Browse | bluos-api-rs | DISCONFIRMED | 2026-09-11, fw 4.16.22, schema 34 | `GET :11000/Browse?sid=0` -> 200 | bluos-probe-20260911T220357: 393-browse |
| `C-52-disabled-input-hidden` | an input disabled in the app still appears in some API surface | raised by the tester | INCONCLUSIVE | 2026-09-11, fw 4.16.22, schema 34 | `- :0(analysis)` ->  | bluos-probe-20260911T220357: 228-inputs, 235-inputs, 242-inputs, 249-inputs |
```

Column order: claim id - claim - source - verdict - tested against -
the request and its answer - evidence pointer.

## Promote out of the register

These were confirmed on hardware and can move from the `[T]` register
into the body of the specification as `[V hardware]`, citing this bundle.
The register row itself stays, as provenance.

- `C-01-diagnostics-80` -- /diagnostics answers on port 80 (section 13)
- `C-02-diagnostics-11000` -- /diagnostics does NOT answer on port 11000 (section 13)
- `C-04-proxytoslave` -- /proxyToSlave exists as a POST relay to a slave (section 10.0)
- `C-07-artwork-cors` -- /Artwork sends Access-Control-Allow-Origin: * (section 9)
- `C-08-artwork-noetag` -- /Artwork sends no ETag and no Last-Modified (section 9)
- `C-21-schema-headers` -- omitting X-Sovi-Schema-Version changes the response (section 1.4)
- `C-22-page-cap-50` -- browse paging is capped server-side at 50 items (section 8.2)
- `C-23-11001-settings-only` -- port 11001 serves settings and nothing else (section 10.3)
- `C-24-player-enumeration` -- some endpoint enumerates players outside a group (section 16)

---

## Capture fidelity

167 captured bodies are **byte-for-byte what the device sent** -- redaction changed nothing in them, so they are usable as parser fixtures and as evidence about byte lengths without qualification.

43 were modified. For each, `body_bytes_wire` in `MANIFEST.json` gives the original length and `redaction_edits` the number of substitutions, so a length-sensitive claim can still be checked. The digest recorded in the bundle is of the **redacted** body; because redaction is deterministic and stable within a run, two redacted digests still compare correctly against each other. Digests of the original bodies are in the do-not-share key file only, because for a templated body they would recover the redacted values by brute force.

| probe | endpoint | wire bytes | written bytes | edits |
|---|---|---|---|---|
| `001-env` | `/SyncStatus` | 414 | 410 | 2 |
| `005-env` | `/Presets` | 294 | 294 | 2 |
| `006-env` | `/Playlist` | 18246 | 18246 | 1 |
| `012-env` | `/SyncStatus` | 397 | 393 | 2 |
| `023-env` | `/SyncStatus` | 394 | 390 | 2 |
| `034-env` | `/SyncStatus` | 391 | 387 | 2 |
| `038-env` | `/Presets` | 424 | 424 | 2 |
| `039-env` | `/Playlist` | 10138 | 10138 | 1 |
| `119-ports` | `/Settings` | 88 | 84 | 1 |
| `143-ports` | `/ui/Home` | 19610 | 19588 | 11 |
| `144-ports` | `/ui/RecentlyPlayed` | 89768 | 89658 | 70 |
| `149-ports` | `/ui/nowPlayingCM` | 2109 | 2109 | 1 |
| `153-ports` | `/ui/presets` | 1309 | 1309 | 3 |
| `181-errors` | `/Songs` | 67 | 63 | 1 |
| `190-errors` | `/Settings` | 106 | 102 | 1 |
| `195-claims` | `/diagnostics` | 3524 | 3493 | 9 |
| `197-claims` | `/diagnostics` | 3523 | 3492 | 9 |
| `205-claims` | `/Shares` | 180 | 186 | 2 |
| `207-claims` | `/Shares` | 180 | 186 | 2 |
| `211-claims` | `/RadioPresets` | 841 | 841 | 6 |
| `212-claims` | `/RadioBrowse` | 841 | 841 | 6 |
| `218-claims` | `/RadioBrowse` | 3637 | 3637 | 1 |
| `255-artwork` | `/Artwork` | 134 | 130 | 1 |
| `257-artwork` | `/Artwork` | 139 | 135 | 1 |
| `324-browse` | `/Browse` | 18327 | 18327 | 80 |
| `326-browse` | `/Browse` | 17559 | 17559 | 80 |
| `335-browse` | `/Browse` | 998 | 998 | 5 |
| `339-browse` | `/Browse` | 71193 | 71193 | 41 |
| `355-browse` | `/Browse` | 31225 | 30931 | 98 |
| `356-browse` | `/Browse` | 32174 | 31880 | 98 |
| `357-browse` | `/Browse` | 31806 | 31512 | 98 |
| `358-browse` | `/Browse` | 30571 | 30277 | 98 |
| `359-browse` | `/Browse` | 20721 | 20523 | 66 |
| `395-settings` | `/Settings` | 2077 | 2070 | 3 |
| `397-settings` | `/Settings` | 2076 | 2069 | 3 |
| `399-settings` | `/Settings` | 2076 | 2069 | 3 |
| `401-settings` | `/Settings` | 2077 | 2070 | 3 |
| `407-settings` | `/Settings` | 2077 | 2070 | 3 |
| `410-settings` | `/Settings` | 2077 | 2070 | 3 |
| `411-settings` | `/Settings` | 2077 | 2070 | 3 |
| `414-settings` | `/Settings` | 1389 | 1385 | 1 |
| `415-settings` | `/Settings` | 1496 | 1489 | 3 |
| `419-settings` | `/Settings` | 602 | 598 | 1 |
