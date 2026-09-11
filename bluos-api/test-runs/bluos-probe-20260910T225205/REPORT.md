# BluOS probe run -- results

| | |
|---|---|
| harness | bluos-probe.py 1.4 |
| started | 2026-09-10T22:52:05 |
| duration | 103.7 s |
| timezone declared to devices | `Europe/Copenhagen` (`X-Sovi-Tz`) |
| harness host clock | CEST (UTC+0200) |
| probes | 70 |
| verdicts | INFO 62, OK 8 |
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
| `070-restore` | O | | | *analysis* | | | | | | **restore the original topology (all standalone)** |

### restore -- analysis detail

**restore the original topology (all standalone)** (`070-restore`)

```
restored
```

## suite: state_setmaster

| id | v | player | port | request | status | ms | type | root | bytes | note |
|---|---|---|---|---|---|---|---|---|---|---|
| `001-state_setmaster` | I | A | 11000 | `/SetMaster` | 200 | 10 | xml | `SyncStatus` | 408 | bare /SetMaster on a standalone player -- addressed to A |
| `002-state_setmaster` | I | | | *analysis* | | | | | | **bare /SetMaster on a standalone player: response etag EQUALS the pre-call etag** |
| `003-state_setmaster` | I | | | *analysis* | | | | | | **bare /SetMaster on a standalone player: topology unchanged (the claim predicts no change)** |
| `004-state_setmaster` | I | A | 11000 | `/AddSlave?slaves=192.0.2.12&ports=11000` | 200 | 27 | xml | `addSlave` | 104 | set up: A takes B |
| `005-state_setmaster` | I | A | 11000 | `/SetMaster` | 200 | 8 | xml | `SyncStatus` | 534 | bare /SetMaster on a master (does it dissolve its own group?) -- addressed to A |
| `006-state_setmaster` | I | | | *analysis* | | | | | | **bare /SetMaster on a master (does it dissolve its own group?): response etag EQUALS the pre-call etag** |
| `007-state_setmaster` | I | | | *analysis* | | | | | | **bare /SetMaster on a master (does it dissolve its own group?): topology unchanged (the claim predicts no change)** |
| `008-state_setmaster` | I | A | 11000 | `/RemoveSlave?slaves=192.0.2.12&ports=11000` | 200 | 9 | xml | `SyncStatus` | 534 | teardown: free the slaves of A |
| `009-state_setmaster` | I | | | *analysis* | | | | | | **reset topology before 'bare /SetMaster on a slave (the documented self-unjoin)': freed A, B** |
| `010-state_setmaster` | I | A | 11000 | `/AddSlave?slaves=192.0.2.12&ports=11000` | 200 | 24 | xml | `addSlave` | 104 | set up: A takes B |
| `011-state_setmaster` | I | B | 11000 | `/SetMaster` | 200 | 42 | xml | `SyncStatus` | 391 | bare /SetMaster on a slave (the documented self-unjoin) -- addressed to B |
| `012-state_setmaster` | I | | | *analysis* | | | | | | **bare /SetMaster on a slave (the documented self-unjoin): response etag differs from the pre-call etag** |
| `013-state_setmaster` | I | | | *analysis* | | | | | | **bare /SetMaster on a slave (the documented self-unjoin): topology CHANGED (the claim predicts a change)** |
| `014-state_setmaster` | I | B | 11000 | `/SetMaster?master=192.0.2.11&port=11000` | 200 | 13 | xml | `SyncStatus` | 391 | ?master= on a standalone player: join that group -- addressed to B |
| `015-state_setmaster` | I | | | *analysis* | | | | | | **?master= on a standalone player: join that group: response etag EQUALS the pre-call etag** |
| `016-state_setmaster` | I | | | *analysis* | | | | | | **?master= on a standalone player: join that group: topology CHANGED (the claim predicts a change)** |
| `017-state_setmaster` | I | | | *analysis* | | | | | | **C-54: B reports A as its master; A does NOT list B as a slave** |
| `018-state_setmaster` | I | B | 11000 | `/SetMaster` | 200 | 44 | xml | `SyncStatus` | 391 | teardown fallback: B leaves its group |
| `019-state_setmaster` | I | | | *analysis* | | | | | | **reset topology before '?master= with port omitted': freed B** |
| `020-state_setmaster` | O | | | *analysis* | | | | | | **B could only be freed by a bare /SetMaster** |
| `021-state_setmaster` | I | B | 11000 | `/SetMaster?master=192.0.2.11` | 200 | 13 | xml | `SyncStatus` | 391 | ?master= with port omitted -- addressed to B |
| `022-state_setmaster` | I | | | *analysis* | | | | | | **?master= with port omitted: response etag EQUALS the pre-call etag** |
| `023-state_setmaster` | I | | | *analysis* | | | | | | **?master= with port omitted: topology CHANGED (the claim predicts a change)** |
| `024-state_setmaster` | I | B | 11000 | `/SetMaster` | 200 | 44 | xml | `SyncStatus` | 391 | teardown fallback: B leaves its group |
| `025-state_setmaster` | I | | | *analysis* | | | | | | **reset topology before '?master= pointing at the player itself': freed B** |
| `026-state_setmaster` | O | | | *analysis* | | | | | | **B could only be freed by a bare /SetMaster** |
| `027-state_setmaster` | I | B | 11000 | `/SetMaster?master=192.0.2.12&port=11000` | 200 | 13 | xml | `SyncStatus` | 391 | ?master= pointing at the player itself -- addressed to B |
| `028-state_setmaster` | I | | | *analysis* | | | | | | **?master= pointing at the player itself: response etag EQUALS the pre-call etag** |
| `029-state_setmaster` | I | | | *analysis* | | | | | | **?master= pointing at the player itself: topology CHANGED (the claim predicts no change)** |
| `030-state_setmaster` | I | B | 11000 | `/SetMaster` | 200 | 43 | xml | `SyncStatus` | 391 | teardown fallback: B leaves its group |
| `031-state_setmaster` | I | | | *analysis* | | | | | | **reset topology before '?master= pointing at an address that is not a player': freed B** |
| `032-state_setmaster` | O | | | *analysis* | | | | | | **B could only be freed by a bare /SetMaster** |
| `033-state_setmaster` | I | B | 11000 | `/SetMaster?master=203.0.113.9&port=11000` | 200 | 13 | xml | `SyncStatus` | 391 | ?master= pointing at an address that is not a player -- addressed to B |
| `034-state_setmaster` | I | | | *analysis* | | | | | | **?master= pointing at an address that is not a player: response etag EQUALS the pre-call etag** |
| `035-state_setmaster` | I | | | *analysis* | | | | | | **?master= pointing at an address that is not a player: topology CHANGED (the claim predicts no change)** |
| `036-state_setmaster` | I | B | 11000 | `/SetMaster` | 200 | 43 | xml | `SyncStatus` | 391 | teardown fallback: B leaves its group |
| `037-state_setmaster` | I | | | *analysis* | | | | | | **reset topology before '?master= issued by a player that is already a slave of someone else': freed B** |
| `038-state_setmaster` | O | | | *analysis* | | | | | | **B could only be freed by a bare /SetMaster** |
| `039-state_setmaster` | I | A | 11000 | `/AddSlave?slaves=192.0.2.12&ports=11000` | 200 | 40 | xml | `addSlave` | 104 | set up: A takes B |
| `040-state_setmaster` | I | B | 11000 | `/SetMaster?master=192.0.2.13&port=11000` | 200 | 14 | xml | `SyncStatus` | 429 | ?master= issued by a player that is already a slave of someone else -- addressed to B |
| `041-state_setmaster` | I | | | *analysis* | | | | | | **?master= issued by a player that is already a slave of someone else: response etag EQUALS the pre-call etag** |
| `042-state_setmaster` | I | | | *analysis* | | | | | | **?master= issued by a player that is already a slave of someone else: topology CHANGED (the claim predicts a change)** |
| `043-state_setmaster` | I | B | 11000 | `/SetMaster` | 200 | 43 | xml | `SyncStatus` | 389 | teardown fallback: B leaves its group |
| `044-state_setmaster` | I | | | *analysis* | | | | | | **reset topology before '?master= issued by a MASTER: the role reversal that keeps failing': freed B** |
| `045-state_setmaster` | O | | | *analysis* | | | | | | **B could only be freed by a bare /SetMaster** |
| `046-state_setmaster` | I | A | 11000 | `/AddSlave?slaves=192.0.2.12&ports=11000` | 200 | 23 | xml | `addSlave` | 104 | set up: A takes B |
| `047-state_setmaster` | I | A | 11000 | `/SetMaster?master=192.0.2.12&port=11000` | 200 | 13 | xml | `SyncStatus` | 534 | ?master= issued by a MASTER: the role reversal that keeps failing -- addressed to A |
| `048-state_setmaster` | I | | | *analysis* | | | | | | **?master= issued by a MASTER: the role reversal that keeps failing: response etag EQUALS the pre-call etag** |
| `049-state_setmaster` | I | | | *analysis* | | | | | | **?master= issued by a MASTER: the role reversal that keeps failing: topology CHANGED (the claim predicts a change)** |
| `050-state_setmaster` | I | A | 11000 | `/RemoveSlave?slaves=192.0.2.12&ports=11000` | 200 | 12 | xml | `SyncStatus` | 594 | teardown: free the slaves of A |
| `051-state_setmaster` | I | A | 11000 | `/SetMaster` | 200 | 43 | xml | `SyncStatus` | 408 | teardown fallback: A leaves its group |
| `052-state_setmaster` | I | | | *analysis* | | | | | | **reset topology before '?slave= on a master (reported ignored)': freed A, B** |
| `053-state_setmaster` | O | | | *analysis* | | | | | | **A could only be freed by a bare /SetMaster** |
| `054-state_setmaster` | I | A | 11000 | `/AddSlave?slaves=192.0.2.12&ports=11000` | 200 | 26 | xml | `addSlave` | 104 | set up: A takes B |
| `055-state_setmaster` | I | A | 11000 | `/SetMaster?slave=192.0.2.12&port=11000` | 200 | 10 | xml | `SyncStatus` | 534 | ?slave= on a master (reported ignored) -- addressed to A |
| `056-state_setmaster` | I | | | *analysis* | | | | | | **?slave= on a master (reported ignored): response etag EQUALS the pre-call etag** |
| `057-state_setmaster` | I | | | *analysis* | | | | | | **?slave= on a master (reported ignored): topology unchanged (the claim predicts no change)** |
| `058-state_setmaster` | I | A | 11000 | `/RemoveSlave?slaves=192.0.2.12&ports=11000` | 200 | 7 | xml | `SyncStatus` | 534 | teardown: free the slaves of A |
| `059-state_setmaster` | I | | | *analysis* | | | | | | **reset topology before '?slave= on a standalone player': freed A, B** |
| `060-state_setmaster` | I | A | 11000 | `/SetMaster?slave=192.0.2.12&port=11000` | 200 | 10 | xml | `SyncStatus` | 408 | ?slave= on a standalone player -- addressed to A |
| `061-state_setmaster` | I | | | *analysis* | | | | | | **?slave= on a standalone player: response etag EQUALS the pre-call etag** |
| `062-state_setmaster` | I | | | *analysis* | | | | | | **?slave= on a standalone player: topology unchanged** |
| `063-state_setmaster` | I | B | 11000 | `/AddSlave?slaves=192.0.2.13&ports=11000` | 200 | 23 | xml | `addSlave` | 104 | set up: B takes C |
| `064-state_setmaster` | I | A | 11000 | `/AddSlave?slave=192.0.2.12&port=11000` | 200 | 23 | xml | `addSlave` | 104 | set up: attach master B under A to create a nested group |
| `065-state_setmaster` | I | B | 11000 | `/SetMaster` | 200 | 44 | xml | `SyncStatus` | 521 | bare /SetMaster on a NESTED master (both <master> and <slave> present) -- addressed to B |
| `066-state_setmaster` | I | | | *analysis* | | | | | | **bare /SetMaster on a NESTED master (both <master> and <slave> present): response etag differs from the pre-call etag** |
| `067-state_setmaster` | I | | | *analysis* | | | | | | **bare /SetMaster on a NESTED master (both <master> and <slave> present): topology CHANGED (the claim predicts a change)** |
| `068-state_setmaster` | I | B | 11000 | `/RemoveSlave?slaves=192.0.2.13&ports=11000` | 200 | 7 | xml | `SyncStatus` | 521 | teardown: free the slaves of B |
| `069-state_setmaster` | O | | | *analysis* | | | | | | **original topology restored: yes** |

### state_setmaster -- analysis detail

**bare /SetMaster on a standalone player: response etag EQUALS the pre-call etag** (`002-state_setmaster`)

```
pre=182 response=182 -- the topology did not move, so an unchanged etag proves nothing
```

**bare /SetMaster on a standalone player: topology unchanged (the claim predicts no change)** (`003-state_setmaster`)

```
| player | master before | slaves before | master after | slaves after | group after |
|---|---|---|---|---|---|
| A | - | - | - | - | - |
```

**bare /SetMaster on a master (does it dissolve its own group?): response etag EQUALS the pre-call etag** (`006-state_setmaster`)

```
pre=186 response=186 -- the topology did not move, so an unchanged etag proves nothing
```

**bare /SetMaster on a master (does it dissolve its own group?): topology unchanged (the claim predicts no change)** (`007-state_setmaster`)

```
| player | master before | slaves before | master after | slaves after | group after |
|---|---|---|---|---|---|
| A | - | 192.0.2.12 | - | 192.0.2.12 | Stue+Kontor |
| B | 192.0.2.11 | - | 192.0.2.11 | - | - |
```

**bare /SetMaster on a slave (the documented self-unjoin): response etag differs from the pre-call etag** (`012-state_setmaster`)

```
pre=945 response=946 -- the response already reflected the change
```

**bare /SetMaster on a slave (the documented self-unjoin): topology CHANGED (the claim predicts a change)** (`013-state_setmaster`)

```
| player | master before | slaves before | master after | slaves after | group after |
|---|---|---|---|---|---|
| A | - | 192.0.2.12 | - | - | - |
| B | 192.0.2.11 | - | - | - | - |
```

**?master= on a standalone player: join that group: response etag EQUALS the pre-call etag** (`015-state_setmaster`)

```
pre=946 response=946 -- the response carried the pre-call state, so a client must re-read rather than trust it
```

**?master= on a standalone player: join that group: topology CHANGED (the claim predicts a change)** (`016-state_setmaster`)

```
| player | master before | slaves before | master after | slaves after | group after |
|---|---|---|---|---|---|
| A | - | - | - | - | - |
| B | - | - | 192.0.2.11 | - | - |
```

**C-54: B reports A as its master; A does NOT list B as a slave** (`017-state_setmaster`)

```
A.slaves=[] group='' / B.master=192.0.2.11 group=''

If the master does not list the joiner, membership created by /SetMaster?master= is one-sided: build topology from the master's <slave> list alone and this member is invisible. /AddSlave by contrast produces both halves and a group name.
```

**B could only be freed by a bare /SetMaster** (`020-state_setmaster`)

```
Expected: after a slave-side join with /SetMaster?master=, no master lists this player as a <slave>, so /RemoveSlave has nothing to act on. The self-unjoin is the only way out. This does not invalidate the case that follows.
```

**?master= with port omitted: response etag EQUALS the pre-call etag** (`022-state_setmaster`)

```
pre=949 response=949 -- the response carried the pre-call state, so a client must re-read rather than trust it
```

**?master= with port omitted: topology CHANGED (the claim predicts a change)** (`023-state_setmaster`)

```
| player | master before | slaves before | master after | slaves after | group after |
|---|---|---|---|---|---|
| A | - | - | - | - | - |
| B | - | - | 192.0.2.11 | - | - |
```

**B could only be freed by a bare /SetMaster** (`026-state_setmaster`)

```
Expected: after a slave-side join with /SetMaster?master=, no master lists this player as a <slave>, so /RemoveSlave has nothing to act on. The self-unjoin is the only way out. This does not invalidate the case that follows.
```

**?master= pointing at the player itself: response etag EQUALS the pre-call etag** (`028-state_setmaster`)

```
pre=952 response=952 -- the response carried the pre-call state, so a client must re-read rather than trust it
```

**?master= pointing at the player itself: topology CHANGED (the claim predicts no change)** (`029-state_setmaster`)

```
| player | master before | slaves before | master after | slaves after | group after |
|---|---|---|---|---|---|
| B | - | - | 192.0.2.12 | - | - |
```

**B could only be freed by a bare /SetMaster** (`032-state_setmaster`)

```
Expected: after a slave-side join with /SetMaster?master=, no master lists this player as a <slave>, so /RemoveSlave has nothing to act on. The self-unjoin is the only way out. This does not invalidate the case that follows.
```

**?master= pointing at an address that is not a player: response etag EQUALS the pre-call etag** (`034-state_setmaster`)

```
pre=955 response=955 -- the response carried the pre-call state, so a client must re-read rather than trust it
```

**?master= pointing at an address that is not a player: topology CHANGED (the claim predicts no change)** (`035-state_setmaster`)

```
| player | master before | slaves before | master after | slaves after | group after |
|---|---|---|---|---|---|
| B | - | - | 203.0.113.9 | - | - |
```

**B could only be freed by a bare /SetMaster** (`038-state_setmaster`)

```
Expected: after a slave-side join with /SetMaster?master=, no master lists this player as a <slave>, so /RemoveSlave has nothing to act on. The self-unjoin is the only way out. This does not invalidate the case that follows.
```

**?master= issued by a player that is already a slave of someone else: response etag EQUALS the pre-call etag** (`041-state_setmaster`)

```
pre=960 response=960 -- the response carried the pre-call state, so a client must re-read rather than trust it
```

**?master= issued by a player that is already a slave of someone else: topology CHANGED (the claim predicts a change)** (`042-state_setmaster`)

```
| player | master before | slaves before | master after | slaves after | group after |
|---|---|---|---|---|---|
| A | - | 192.0.2.12 | - | - | - |
| B | 192.0.2.11 | - | 192.0.2.13 | - | - |
| C | - | - | - | - | - |
```

**B could only be freed by a bare /SetMaster** (`045-state_setmaster`)

```
Expected: after a slave-side join with /SetMaster?master=, no master lists this player as a <slave>, so /RemoveSlave has nothing to act on. The self-unjoin is the only way out. This does not invalidate the case that follows.
```

**?master= issued by a MASTER: the role reversal that keeps failing: response etag EQUALS the pre-call etag** (`048-state_setmaster`)

```
pre=204 response=204 -- the response carried the pre-call state, so a client must re-read rather than trust it
```

**?master= issued by a MASTER: the role reversal that keeps failing: topology CHANGED (the claim predicts a change)** (`049-state_setmaster`)

```
| player | master before | slaves before | master after | slaves after | group after |
|---|---|---|---|---|---|
| A | - | 192.0.2.12 | 192.0.2.12 | 192.0.2.12 | Stue+Kontor |
| B | 192.0.2.11 | - | 192.0.2.11 | - | - |
```

**A could only be freed by a bare /SetMaster** (`053-state_setmaster`)

```
Expected: after a slave-side join with /SetMaster?master=, no master lists this player as a <slave>, so /RemoveSlave has nothing to act on. The self-unjoin is the only way out. This does not invalidate the case that follows.
```

**?slave= on a master (reported ignored): response etag EQUALS the pre-call etag** (`056-state_setmaster`)

```
pre=213 response=213 -- the topology did not move, so an unchanged etag proves nothing
```

**?slave= on a master (reported ignored): topology unchanged (the claim predicts no change)** (`057-state_setmaster`)

```
| player | master before | slaves before | master after | slaves after | group after |
|---|---|---|---|---|---|
| A | - | 192.0.2.12 | - | 192.0.2.12 | Stue+Kontor |
| B | 192.0.2.11 | - | 192.0.2.11 | - | - |
```

**?slave= on a standalone player: response etag EQUALS the pre-call etag** (`061-state_setmaster`)

```
pre=215 response=215 -- the topology did not move, so an unchanged etag proves nothing
```

**?slave= on a standalone player: topology unchanged** (`062-state_setmaster`)

```
| player | master before | slaves before | master after | slaves after | group after |
|---|---|---|---|---|---|
| A | - | - | - | - | - |
| B | - | - | - | - | - |
```

**bare /SetMaster on a NESTED master (both <master> and <slave> present): response etag differs from the pre-call etag** (`066-state_setmaster`)

```
pre=978 response=979 -- the response already reflected the change
```

**bare /SetMaster on a NESTED master (both <master> and <slave> present): topology CHANGED (the claim predicts a change)** (`067-state_setmaster`)

```
| player | master before | slaves before | master after | slaves after | group after |
|---|---|---|---|---|---|
| A | - | 192.0.2.12 | - | - | - |
| B | 192.0.2.11 | 192.0.2.13 | - | 192.0.2.13 | Kontor+Køkken |
| C | 192.0.2.12 | - | 192.0.2.12 | - | - |
```

**original topology restored: yes** (`069-state_setmaster`)

```
A: before master=- slaves=[] / after master=- slaves=[]
B: before master=- slaves=[] / after master=- slaves=[]
C: before master=- slaves=[] / after master=- slaves=[]
D: before master=- slaves=[] / after master=- slaves=[]
```

## Bodies

Response bodies are in `raw/`, one file per probe id, alongside a
`.head.txt` with the status line and response headers. Binary
bodies (artwork) are not stored: only their length, content type
and first bytes are recorded here, so no embedded metadata can
leak. Their SHA-256 is in the do-not-share key file, not in this
bundle.
