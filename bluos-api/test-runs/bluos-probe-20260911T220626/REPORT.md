# BluOS probe run -- results

| | |
|---|---|
| harness | bluos-probe.py 1.6 |
| started | 2026-09-11T22:06:26 |
| duration | 42.0 s |
| timezone declared to devices | `Europe/Copenhagen` (`X-Sovi-Tz`) |
| harness host clock | CEST (UTC+0200) |
| probes | 66 |
| verdicts | INFO 61, OK 5 |
| safety classes run | read, probe, state |

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

## suite: restore

| id | v | player | port | request | status | ms | type | root | bytes | note |
|---|---|---|---|---|---|---|---|---|---|---|
| `064-restore` | O | | | *analysis* | | | | | | **restore the original topology (all standalone)** |
| `065-restore` | O | | | *analysis* | | | | | | **A: restore transport state to 'play'** |
| `066-restore` | O | | | *analysis* | | | | | | **A: restore volume to 20** |

### restore -- analysis detail

**restore the original topology (all standalone)** (`064-restore`)

```
restored
```

**A: restore transport state to 'play'** (`065-restore`)

```
restored
```

**A: restore volume to 20** (`066-restore`)

```
restored
```

## suite: state_capture

| id | v | player | port | request | status | ms | type | root | bytes | note |
|---|---|---|---|---|---|---|---|---|---|---|
| `001-state_capture` | I | A | 11000 | `/SyncStatus` | 200 | 40 | xml | `SyncStatus` | 410 | [capture] playing as-found: Tidal mqa -- /SyncStatus on A |
| `002-state_capture` | I | A | 11000 | `/Status` | 200 | 13 | xml | `status` | 1340 | [capture] playing as-found: Tidal mqa -- /Status on A |
| `003-state_capture` | I | | | *analysis* | | | | | | **captured state: playing as-found: Tidal mqa** |
| `004-state_capture` | I | | | *analysis* | | | | | | **captured the source that was already playing on A** |
| `005-state_capture` | I | A | 11000 | `/SyncStatus` | 200 | 11 | xml | `SyncStatus` | 410 | [capture] standalone -- /SyncStatus on A |
| `006-state_capture` | I | A | 11000 | `/Status` | 200 | 9 | xml | `status` | 1340 | [capture] standalone -- /Status on A |
| `007-state_capture` | I | A | 11000 | `/Presets` | 200 | 8 | xml | `presets` | 294 | [capture] standalone -- /Presets on A |
| `008-state_capture` | I | A | 11000 | `/Playlist` | 200 | 17 | xml | `playlist` | 18246 | [capture] standalone -- /Playlist on A |
| `009-state_capture` | I | A | 11000 | `/Volume` | 200 | 9 | xml | `volume` | 142 | [capture] standalone -- /Volume on A |
| `010-state_capture` | I | B | 11000 | `/SyncStatus` | 200 | 8 | xml | `SyncStatus` | 393 | [capture] standalone -- /SyncStatus on B |
| `011-state_capture` | I | B | 11000 | `/Status` | 200 | 8 | xml | `status` | 1254 | [capture] standalone -- /Status on B |
| `012-state_capture` | I | B | 11000 | `/Presets` | 200 | 9 | xml | `presets` | 67 | [capture] standalone -- /Presets on B |
| `013-state_capture` | I | B | 11000 | `/Playlist` | 200 | 22 | xml | `playlist` | 62326 | [capture] standalone -- /Playlist on B |
| `014-state_capture` | I | B | 11000 | `/Volume` | 200 | 9 | xml | `volume` | 142 | [capture] standalone -- /Volume on B |
| `015-state_capture` | I | C | 11000 | `/SyncStatus` | 200 | 9 | xml | `SyncStatus` | 390 | [capture] standalone -- /SyncStatus on C |
| `016-state_capture` | I | C | 11000 | `/Status` | 200 | 9 | xml | `status` | 1251 | [capture] standalone -- /Status on C |
| `017-state_capture` | I | C | 11000 | `/Presets` | 200 | 9 | xml | `presets` | 67 | [capture] standalone -- /Presets on C |
| `018-state_capture` | I | C | 11000 | `/Playlist` | 200 | 12 | xml | `playlist` | 15105 | [capture] standalone -- /Playlist on C |
| `019-state_capture` | I | C | 11000 | `/Volume` | 200 | 10 | xml | `volume` | 140 | [capture] standalone -- /Volume on C |
| `020-state_capture` | I | D | 11000 | `/SyncStatus` | 200 | 14 | xml | `SyncStatus` | 387 | [capture] standalone -- /SyncStatus on D |
| `021-state_capture` | I | D | 11000 | `/Status` | 200 | 16 | xml | `status` | 1448 | [capture] standalone -- /Status on D |
| `022-state_capture` | I | D | 11000 | `/Presets` | 200 | 14 | xml | `presets` | 424 | [capture] standalone -- /Presets on D |
| `023-state_capture` | I | D | 11000 | `/Playlist` | 200 | 22 | xml | `playlist` | 10138 | [capture] standalone -- /Playlist on D |
| `024-state_capture` | I | D | 11000 | `/Volume` | 200 | 17 | xml | `volume` | 141 | [capture] standalone -- /Volume on D |
| `025-state_capture` | I | | | *analysis* | | | | | | **captured state: standalone** |
| `026-state_capture` | I | A | 11000 | `/Volume?level=10` | 200 | 11 | xml | `volume` | 142 | cap A at level 10 before starting audio (was 20) |
| `027-state_capture` | I | | | *analysis* | | | | | | **A volume lowered from 20 to the --max-volume ceiling of 10** |
| `028-state_capture` | I | A | 11000 | `/Preset?id=1` | 200 | 315 | xml | `loaded` | 93 | capture setup: start playback on A from preset 1 |
| `029-state_capture` | I | A | 11000 | `/SyncStatus` | 200 | 11 | xml | `SyncStatus` | 410 | [capture] playing (preset recall) -- /SyncStatus on A |
| `030-state_capture` | I | A | 11000 | `/Status` | 200 | 12 | xml | `status` | 1323 | [capture] playing (preset recall) -- /Status on A |
| `031-state_capture` | I | | | *analysis* | | | | | | **captured state: playing (preset recall)** |
| `032-state_capture` | I | A | 11000 | `/AddSlave?slaves=192.0.2.12&ports=11000` | 200 | 24 | xml | `addSlave` | 104 | set up: A takes B |
| `033-state_capture` | I | A | 11000 | `/SyncStatus` | 200 | 9 | xml | `SyncStatus` | 536 | [capture] group: A master, B slave -- /SyncStatus on A |
| `034-state_capture` | I | A | 11000 | `/Status` | 200 | 10 | xml | `status` | 1386 | [capture] group: A master, B slave -- /Status on A |
| `035-state_capture` | I | B | 11000 | `/SyncStatus` | 200 | 10 | xml | `SyncStatus` | 433 | [capture] group: A master, B slave -- /SyncStatus on B |
| `036-state_capture` | I | B | 11000 | `/Status` | 200 | 18 | xml | `status` | 1386 | [capture] group: A master, B slave -- /Status on B |
| `037-state_capture` | I | | | *analysis* | | | | | | **captured state: group: A master, B slave** |
| `038-state_capture` | I | A | 11000 | `/AddSlave?slaves=192.0.2.13&ports=11000` | 200 | 26 | xml | `addSlave` | 104 | set up: A takes C |
| `039-state_capture` | I | A | 11000 | `/RemoveSlave?slaves=192.0.2.12,192.0.2.13&ports=11000,11000` | 200 | 9 | xml | `SyncStatus` | 640 | teardown: free the slaves of A |
| `040-state_capture` | I | | | *analysis* | | | | | | **reset topology before 'before nesting': freed A, B, C** |
| `041-state_capture` | I | B | 11000 | `/AddSlave?slaves=192.0.2.13&ports=11000` | 200 | 26 | xml | `addSlave` | 104 | set up: B takes C |
| `042-state_capture` | I | A | 11000 | `/AddSlave?slave=192.0.2.12&port=11000` | 200 | 28 | xml | `addSlave` | 104 | capture setup: nest B (a master) under A |
| `043-state_capture` | I | A | 11000 | `/SyncStatus` | 200 | 10 | xml | `SyncStatus` | 536 | [capture] nested: A -> B -> C -- /SyncStatus on A |
| `044-state_capture` | I | A | 11000 | `/Status` | 200 | 14 | xml | `status` | 1387 | [capture] nested: A -> B -> C -- /Status on A |
| `045-state_capture` | I | B | 11000 | `/SyncStatus` | 200 | 10 | xml | `SyncStatus` | 563 | [capture] nested: A -> B -> C -- /SyncStatus on B |
| `046-state_capture` | I | B | 11000 | `/Status` | 200 | 19 | xml | `status` | 1387 | [capture] nested: A -> B -> C -- /Status on B |
| `047-state_capture` | I | C | 11000 | `/SyncStatus` | 200 | 10 | xml | `SyncStatus` | 432 | [capture] nested: A -> B -> C -- /SyncStatus on C |
| `048-state_capture` | I | C | 11000 | `/Status` | 200 | 20 | xml | `status` | 1387 | [capture] nested: A -> B -> C -- /Status on C |
| `049-state_capture` | I | | | *analysis* | | | | | | **captured state: nested: A -> B -> C** |
| `050-state_capture` | I | A | 11000 | `/RemoveSlave?slaves=192.0.2.12&ports=11000` | 200 | 15 | xml | `SyncStatus` | 536 | teardown: free the slaves of A |
| `051-state_capture` | I | B | 11000 | `/RemoveSlave?slaves=192.0.2.13&ports=11000` | 200 | 10 | xml | `SyncStatus` | 523 | teardown: free the slaves of B |
| `052-state_capture` | I | | | *analysis* | | | | | | **reset topology before 'before the one-sided join': freed A, B, C** |
| `053-state_capture` | I | D | 11000 | `/SetMaster?master=192.0.2.11&port=11000` | 200 | 79 | xml | `SyncStatus` | 387 | capture setup: D joins A slave-side |
| `054-state_capture` | I | A | 11000 | `/SyncStatus` | 200 | 17 | xml | `SyncStatus` | 410 | [capture] one-sided: D joined A via ?master= -- /SyncStatus on A |
| `055-state_capture` | I | A | 11000 | `/Status` | 200 | 15 | xml | `status` | 1324 | [capture] one-sided: D joined A via ?master= -- /Status on A |
| `056-state_capture` | I | D | 11000 | `/SyncStatus` | 200 | 40 | xml | `SyncStatus` | 447 | [capture] one-sided: D joined A via ?master= -- /SyncStatus on D |
| `057-state_capture` | I | D | 11000 | `/Status` | 200 | 40 | xml | `status` | 1324 | [capture] one-sided: D joined A via ?master= -- /Status on D |
| `058-state_capture` | I | | | *analysis* | | | | | | **captured state: one-sided: D joined A via ?master=** |
| `059-state_capture` | I | D | 11000 | `/SetMaster` | 200 | 140 | xml | `SyncStatus` | 387 | teardown fallback: D leaves its group |
| `060-state_capture` | I | | | *analysis* | | | | | | **reset topology before 'capture teardown': freed D** |
| `061-state_capture` | O | | | *analysis* | | | | | | **D could only be freed by a bare /SetMaster** |
| `062-state_capture` | O | | | *analysis* | | | | | | **original topology restored: yes** |
| `063-state_capture` | I | | | *analysis* | | | | | | **38 labelled captures across 6 states** |

### state_capture -- analysis detail

**captured state: playing as-found: Tidal mqa** (`003-state_capture`)

```
players: A
```

**captured the source that was already playing on A** (`004-state_capture`)

```
service=Tidal quality=mqa. Anything content-dependent -- MQA fields, <actions> on a radio stream -- can only be captured this way: start the stream, then run this suite.
```

**captured state: standalone** (`025-state_capture`)

```
players: A, B, C, D
```

**A volume lowered from 20 to the --max-volume ceiling of 10** (`027-state_capture`)

```
restored from the ledger at the end of the run
```

**captured state: playing (preset recall)** (`031-state_capture`)

```
players: A
```

**captured state: group: A master, B slave** (`037-state_capture`)

```
players: A, B
```

**captured state: nested: A -> B -> C** (`049-state_capture`)

```
players: A, B, C
```

**captured state: one-sided: D joined A via ?master=** (`058-state_capture`)

```
players: A, D
```

**D could only be freed by a bare /SetMaster** (`061-state_capture`)

```
Expected: after a slave-side join with /SetMaster?master=, no master lists this player as a <slave>, so /RemoveSlave has nothing to act on. The self-unjoin is the only way out. This does not invalidate the case that follows.
```

**original topology restored: yes** (`062-state_capture`)

```
A: before master=- slaves=[] / after master=- slaves=[]
B: before master=- slaves=[] / after master=- slaves=[]
C: before master=- slaves=[] / after master=- slaves=[]
D: before master=- slaves=[] / after master=- slaves=[]
```

**38 labelled captures across 6 states** (`063-state_capture`)

```
playing as-found: Tidal mqa                    A   001-state_capture      raw/001-state_capture.xml
playing as-found: Tidal mqa                    A   002-state_capture      raw/002-state_capture.xml
standalone                                     A   005-state_capture      raw/005-state_capture.xml
standalone                                     A   006-state_capture      raw/006-state_capture.xml
standalone                                     A   007-state_capture      raw/007-state_capture.xml
standalone                                     A   008-state_capture      raw/008-state_capture.xml
standalone                                     A   009-state_capture      raw/009-state_capture.xml
standalone                                     B   010-state_capture      raw/010-state_capture.xml
standalone                                     B   011-state_capture      raw/011-state_capture.xml
standalone                                     B   012-state_capture      raw/012-state_capture.xml
standalone                                     B   013-state_capture      raw/013-state_capture.xml
standalone                                     B   014-state_capture      raw/014-state_capture.xml
standalone                                     C   015-state_capture      raw/015-state_capture.xml
standalone                                     C   016-state_capture      raw/016-state_capture.xml
standalone                                     C   017-state_capture      raw/017-state_capture.xml
standalone                                     C   018-state_capture      raw/018-state_capture.xml
standalone                                     C   019-state_capture      raw/019-state_capture.xml
standalone                                     D   020-state_capture      raw/020-state_capture.xml
standalone                                     D   021-state_capture      raw/021-state_capture.xml
standalone                                     D   022-state_capture      raw/022-state_capture.xml
standalone                                     D   023-state_capture      raw/023-state_capture.xml
standalone                                     D   024-state_capture      raw/024-state_capture.xml
playing (preset recall)                        A   029-state_capture      raw/029-state_capture.xml
playing (preset recall)                        A   030-state_capture      raw/030-state_capture.xml
group: A master, B slave                       A   033-state_capture      raw/033-state_capture.xml
group: A master, B slave                       A   034-state_capture      raw/034-state_capture.xml
group: A master, B slave                       B   035-state_capture      raw/035-state_capture.xml
group: A master, B slave                       B   036-state_capture      raw/036-state_capture.xml
nested: A -> B -> C                            A   043-state_capture      raw/043-state_capture.xml
nested: A -> B -> C                            A   044-state_capture      raw/044-state_capture.xml
nested: A -> B -> C                            B   045-state_capture      raw/045-state_capture.xml
nested: A -> B -> C                            B   046-state_capture      raw/046-state_capture.xml
nested: A -> B -> C                            C   047-state_capture      raw/047-state_capture.xml
nested: A -> B -> C                            C   048-state_capture      raw/048-state_capture.xml
one-sided: D joined A via ?master=             A   054-state_capture      raw/054-state_capture.xml
one-sided: D joined A via ?master=             A   055-state_capture      raw/055-state_capture.xml
one-sided: D joined A via ?master=             D   056-state_capture      raw/056-state_capture.xml
one-sided: D joined A via ?master=             D   057-state_capture      raw/057-state_capture.xml
```

## Play-response root elements observed

Blu4Net reports four possible roots for a play-type response. Observed in this run: `loaded`. An HTTP 200 alone says nothing about which arrived, so this is collected from the bodies rather than from status codes.

## Bodies

Response bodies are in `raw/`, one file per probe id, alongside a
`.head.txt` with the status line and response headers. Binary
bodies (artwork) are not stored: only their length, content type
and first bytes are recorded here, so no embedded metadata can
leak. Their SHA-256 is in the do-not-share key file, not in this
bundle.
