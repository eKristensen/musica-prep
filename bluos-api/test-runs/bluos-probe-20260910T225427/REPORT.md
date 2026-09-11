# BluOS probe run -- results

| | |
|---|---|
| harness | bluos-probe.py 1.4 |
| started | 2026-09-10T22:54:27 |
| duration | 114.5 s |
| timezone declared to devices | `Europe/Copenhagen` (`X-Sovi-Tz`) |
| harness host clock | CEST (UTC+0200) |
| probes | 312 |
| verdicts | ERROR 1, INFO 261, OK 45, UNEXPECTED 5 |
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

## Results that did not match the specification

| id | player | request | status | expected | note |
|---|---|---|---|---|---|
| `088-state_playback` | - | `:0 (analysis)` | - | `` | A restore: state stop -> pause |
| `104-state_playback` | - | `:0 (analysis)` | - | `` | B restore: state stop -> pause |
| `120-state_playback` | - | `:0 (analysis)` | - | `` | C restore: state stop -> pause |
| `179-state_source` | - | `:0 (analysis)` | - | `` | fewer than two distinguishable inputs were learned (1) |
| `280-state_grouping` | - | `:0 (analysis)` | - | `` | C-30: slaves remaining after a bare /RemoveSlave: 2 |

## Claim checks

Every probe aimed at a marked claim in the specification, so the
register in section 17 can be updated from one table. `root` and
`bytes` are usually enough to tell a real answer from a 404.

| id | claim | verdict | player | port | request | status | root | note |
|---|---|---|---|---|---|---|---|---|
| `008-state_volume` | `C-36-mute-polarity` | INCONCLUSIVE | A | 11000 | `/Volume?mute=1` | 200 | `volume` | mute=1 |
| `026-state_volume` | `C-36-mute-polarity` | INCONCLUSIVE | B | 11000 | `/Volume?mute=1` | 200 | `volume` | mute=1 |
| `044-state_volume` | `C-36-mute-polarity` | INCONCLUSIVE | C | 11000 | `/Volume?mute=1` | 200 | `volume` | mute=1 |
| `062-state_volume` | `C-36-mute-polarity` | INCONCLUSIVE | D | 11000 | `/Volume?mute=1` | 200 | `volume` | mute=1 |
| `152-state_name` | `C-34-name-post` | CONFIRMED | A | 11000 | `/Name` | 200 | `name` | [T blutui] write via POST nodename= |
| `167-state_preset` | `C-17-is-preset` | DISCONFIRMED | D | 11000 | `/Status` | 200 | `status` | does /Status carry <is_preset> / <preset_name> while a preset plays? |
| `169-state_preset` | `C-17-is-preset` | DISCONFIRMED | D | 11000 | `/Status` | 200 | `status` | does /Status carry <is_preset> / <preset_name> while a preset plays? |
| `188-state_source` | `-` | - | A | 11000 | `/Play?inputType=arc&index=1` | 200 | `state` | [T bluos-api-rs] inputType=arc&index=1 (from input#1 via playURL) |
| `256-state_grouping` | `-` | - | B | 11000 | `/AddSlave?slave=192.0.2.11` | 200 | `addSlave` | [T 2015 forum] singular /AddSlave with port omitted |
| `259-state_grouping` | `C-33-slavevolume-combined` | INCONCLUSIVE | B | 11000 | `/SlaveVolume?slave=192.0.2.11:11000&db=0` | 200 | `error` | [T blutui] /SlaveVolume with a combined slave=<ip>:<port> |
| `261-state_grouping` | `-` | - | B | 11000 | `/AddSlave?slave=192.0.2.11&port=11000&channelMode=1` | 200 | `error` | [T HA] numeric channelMode=1 |
| `266-state_grouping` | `-` | - | B | 11000 | `/Sync?slave=192.0.2.11` | 404 | `` | [T bluos-dashboard] legacy /Sync?slave= |
| `267-state_grouping` | `-` | - | B | 11000 | `/Sync?remove=192.0.2.11` | 404 | `` | [T bluos-dashboard] legacy /Sync?remove= |
| `273-state_grouping` | `-` | - | B | 11000 | `/RemoveSlave` | 200 | `SyncStatus` | [T HA] does a bare /RemoveSlave drop every slave? |

## suite: env

| id | v | player | port | request | status | ms | type | root | bytes | note |
|---|---|---|---|---|---|---|---|---|---|---|
| `171-env` | I | | | *analysis* | | | | | | **fleet capabilities, used to skip tests this hardware cannot answer** |
| `172-env` | I | | | *analysis* | | | | | | **3 thing(s) this fleet cannot answer** |

### env -- analysis detail

**fleet capabilities, used to skip tests this hardware cannot answer** (`171-env`)

```
| player | model | capture inputs | bluetooth | presets | subwoofer |
|---|---|---|---|---|---|
| A | N132 | 1 | yes | 0 | yes |
| B | N130 | 1 | yes | 0 | no |
| C | N132 | 1 | yes | 0 | no |
| D | N110 | 0 | no | 2 | yes |
```

**3 thing(s) this fleet cannot answer** (`172-env`)

```
- input selection is weakened: no player advertises two inputs, so 'it switched' cannot be separated from 'it was already there'. Temporarily enabling a second input makes the result conclusive
- T-14 authentication: no way found to set credentials on consumer N-series hardware; the auth path stays source-derived and unexercised
- CI-series multi-zone port offsets: no CI hardware in this fleet

These are recorded as NOT APPLICABLE rather than left to look like failures. A claim untestable on this hardware must never be written into the register as DISCONFIRMED.
```

## suite: restore

| id | v | player | port | request | status | ms | type | root | bytes | note |
|---|---|---|---|---|---|---|---|---|---|---|
| `283-restore` | O | | | *analysis* | | | | | | **A: restore volume to 46** |
| `284-restore` | O | | | *analysis* | | | | | | **A: restore mute=0** |
| `285-restore` | O | | | *analysis* | | | | | | **B: restore volume to 27** |
| `286-restore` | O | | | *analysis* | | | | | | **B: restore mute=0** |
| `287-restore` | O | | | *analysis* | | | | | | **C: restore volume to 38** |
| `288-restore` | O | | | *analysis* | | | | | | **C: restore mute=0** |
| `289-restore` | O | | | *analysis* | | | | | | **D: restore volume to 13** |
| `290-restore` | O | | | *analysis* | | | | | | **D: restore mute=0** |
| `291-restore` | O | | | *analysis* | | | | | | **A: restore transport state to 'stop'** |
| `292-restore` | O | | | *analysis* | | | | | | **A: restore volume to 46** |
| `293-restore` | O | | | *analysis* | | | | | | **A: restore repeat=2** |
| `294-restore` | O | | | *analysis* | | | | | | **A: restore shuffle=1** |
| `295-restore` | O | | | *analysis* | | | | | | **B: restore transport state to 'stop'** |
| `296-restore` | O | | | *analysis* | | | | | | **B: restore volume to 27** |
| `297-restore` | O | | | *analysis* | | | | | | **B: restore repeat=2** |
| `298-restore` | O | | | *analysis* | | | | | | **B: restore shuffle=1** |
| `299-restore` | O | | | *analysis* | | | | | | **C: restore transport state to 'stop'** |
| `300-restore` | O | | | *analysis* | | | | | | **C: restore volume to 38** |
| `301-restore` | O | | | *analysis* | | | | | | **C: restore repeat=2** |
| `302-restore` | O | | | *analysis* | | | | | | **C: restore shuffle=0** |
| `303-restore` | O | | | *analysis* | | | | | | **D: restore transport state to 'play'** |
| `304-restore` | O | | | *analysis* | | | | | | **D: restore volume to 13** |
| `305-restore` | O | | | *analysis* | | | | | | **D: restore repeat=2** |
| `306-restore` | O | | | *analysis* | | | | | | **D: restore shuffle=0** |
| `307-restore` | O | | | *analysis* | | | | | | **A: clear the sleep timer** |
| `308-restore` | O | | | *analysis* | | | | | | **A: restore player name** |
| `309-restore` | O | | | *analysis* | | | | | | **A: restore ledbrightness to off** |
| `310-restore` | O | | | *analysis* | | | | | | **D: restore transport state to 'play'** |
| `311-restore` | O | | | *analysis* | | | | | | **A: restore transport state to 'pause'** |
| `312-restore` | O | | | *analysis* | | | | | | **restore the original topology (all standalone)** |

### restore -- analysis detail

**A: restore volume to 46** (`283-restore`)

```
restored
```

**A: restore mute=0** (`284-restore`)

```
restored
```

**B: restore volume to 27** (`285-restore`)

```
restored
```

**B: restore mute=0** (`286-restore`)

```
restored
```

**C: restore volume to 38** (`287-restore`)

```
restored
```

**C: restore mute=0** (`288-restore`)

```
restored
```

**D: restore volume to 13** (`289-restore`)

```
restored
```

**D: restore mute=0** (`290-restore`)

```
restored
```

**A: restore transport state to 'stop'** (`291-restore`)

```
restored
```

**A: restore volume to 46** (`292-restore`)

```
restored
```

**A: restore repeat=2** (`293-restore`)

```
restored
```

**A: restore shuffle=1** (`294-restore`)

```
restored
```

**B: restore transport state to 'stop'** (`295-restore`)

```
restored
```

**B: restore volume to 27** (`296-restore`)

```
restored
```

**B: restore repeat=2** (`297-restore`)

```
restored
```

**B: restore shuffle=1** (`298-restore`)

```
restored
```

**C: restore transport state to 'stop'** (`299-restore`)

```
restored
```

**C: restore volume to 38** (`300-restore`)

```
restored
```

**C: restore repeat=2** (`301-restore`)

```
restored
```

**C: restore shuffle=0** (`302-restore`)

```
restored
```

**D: restore transport state to 'play'** (`303-restore`)

```
restored
```

**D: restore volume to 13** (`304-restore`)

```
restored
```

**D: restore repeat=2** (`305-restore`)

```
restored
```

**D: restore shuffle=0** (`306-restore`)

```
restored
```

**A: clear the sleep timer** (`307-restore`)

```
restored
```

**A: restore player name** (`308-restore`)

```
restored
```

**A: restore ledbrightness to off** (`309-restore`)

```
restored
```

**D: restore transport state to 'play'** (`310-restore`)

```
restored
```

**A: restore transport state to 'pause'** (`311-restore`)

```
restored
```

**restore the original topology (all standalone)** (`312-restore`)

```
restored
```

## suite: state_grouping

| id | v | player | port | request | status | ms | type | root | bytes | note |
|---|---|---|---|---|---|---|---|---|---|---|
| `206-state_grouping` | I | | | *analysis* | | | | | | **baseline \| A: master=- slaves=- group=-** |
| `207-state_grouping` | I | | | *analysis* | | | | | | **baseline \| B: master=- slaves=- group=-** |
| `208-state_grouping` | I | | | *analysis* | | | | | | **baseline \| C: master=- slaves=- group=-** |
| `209-state_grouping` | I | A | 11000 | `/AddSlave?slave=192.0.2.12&port=11000` | 200 | 59 | xml | `addSlave` | 104 | form group: A takes B as slave |
| `210-state_grouping` | I | A | 11000 | `/SyncStatus` | 200 | 9 | xml | `SyncStatus` | 410 | after AddSlave on the master -- settle read 1/3 |
| `211-state_grouping` | I | A | 11000 | `/SyncStatus` | 200 | 9 | xml | `SyncStatus` | 536 | after AddSlave on the master -- settle read 2/3 |
| `212-state_grouping` | I | A | 11000 | `/SyncStatus` | 200 | 9 | xml | `SyncStatus` | 536 | after AddSlave on the master -- settle read 3/3 |
| `213-state_grouping` | I | B | 11000 | `/SyncStatus` | 200 | 7 | xml | `SyncStatus` | 433 | after AddSlave on the slave -- settle read 1/3 |
| `214-state_grouping` | I | B | 11000 | `/SyncStatus` | 200 | 11 | xml | `SyncStatus` | 433 | after AddSlave on the slave -- settle read 2/3 |
| `215-state_grouping` | I | B | 11000 | `/SyncStatus` | 200 | 16 | xml | `SyncStatus` | 433 | after AddSlave on the slave -- settle read 3/3 |
| `216-state_grouping` | I | | | *analysis* | | | | | | **after A<-B \| A: master=- slaves=192.0.2.12 group=Stue+Kontor** |
| `217-state_grouping` | I | | | *analysis* | | | | | | **after A<-B \| B: master=192.0.2.11 slaves=- group=-** |
| `218-state_grouping` | I | | | *analysis* | | | | | | **after A<-B \| C: master=- slaves=- group=-** |
| `219-state_grouping` | I | | | *analysis* | | | | | | **C-39 step 1: reversing without ungrouping first** |
| `220-state_grouping` | I | B | 11000 | `/AddSlave?slave=192.0.2.11&port=11000` | 200 | 9 | xml | `addSlave` | 60 | C-39: slave B tries to take master A as ITS slave |
| `221-state_grouping` | I | A | 11000 | `/SyncStatus` | 200 | 10 | xml | `SyncStatus` | 536 | A after attempted reversal -- settle read 1/3 |
| `222-state_grouping` | I | A | 11000 | `/SyncStatus` | 200 | 11 | xml | `SyncStatus` | 536 | A after attempted reversal -- settle read 2/3 |
| `223-state_grouping` | I | A | 11000 | `/SyncStatus` | 200 | 12 | xml | `SyncStatus` | 536 | A after attempted reversal -- settle read 3/3 |
| `224-state_grouping` | I | B | 11000 | `/SyncStatus` | 200 | 10 | xml | `SyncStatus` | 433 | B after attempted reversal -- settle read 1/3 |
| `225-state_grouping` | I | B | 11000 | `/SyncStatus` | 200 | 13 | xml | `SyncStatus` | 433 | B after attempted reversal -- settle read 2/3 |
| `226-state_grouping` | I | B | 11000 | `/SyncStatus` | 200 | 10 | xml | `SyncStatus` | 433 | B after attempted reversal -- settle read 3/3 |
| `227-state_grouping` | I | | | *analysis* | | | | | | **after direct reversal attempt \| A: master=- slaves=192.0.2.12 group=Stue+Kontor** |
| `228-state_grouping` | I | | | *analysis* | | | | | | **after direct reversal attempt \| B: master=192.0.2.11 slaves=- group=-** |
| `229-state_grouping` | I | | | *analysis* | | | | | | **after direct reversal attempt \| C: master=- slaves=- group=-** |
| `230-state_grouping` | I | A | 11000 | `/SetMaster?master=192.0.2.12&port=11000` | 200 | 12 | xml | `SyncStatus` | 536 | C-39: ask A to join B's group (slave-side form) |
| `231-state_grouping` | I | A | 11000 | `/SyncStatus` | 200 | 8 | xml | `SyncStatus` | 536 | A after SetMaster?master=B -- settle read 1/3 |
| `232-state_grouping` | I | A | 11000 | `/SyncStatus` | 200 | 12 | xml | `SyncStatus` | 596 | A after SetMaster?master=B -- settle read 2/3 |
| `233-state_grouping` | I | A | 11000 | `/SyncStatus` | 200 | 11 | xml | `SyncStatus` | 596 | A after SetMaster?master=B -- settle read 3/3 |
| `234-state_grouping` | I | B | 11000 | `/SyncStatus` | 200 | 8 | xml | `SyncStatus` | 433 | B after SetMaster?master=B -- settle read 1/3 |
| `235-state_grouping` | I | B | 11000 | `/SyncStatus` | 200 | 12 | xml | `SyncStatus` | 433 | B after SetMaster?master=B -- settle read 2/3 |
| `236-state_grouping` | I | B | 11000 | `/SyncStatus` | 200 | 11 | xml | `SyncStatus` | 433 | B after SetMaster?master=B -- settle read 3/3 |
| `237-state_grouping` | I | | | *analysis* | | | | | | **after SetMaster reversal attempt \| A: master=- slaves=192.0.2.12 group=Stue+Kontor** |
| `238-state_grouping` | I | | | *analysis* | | | | | | **after SetMaster reversal attempt \| B: master=192.0.2.11 slaves=- group=-** |
| `239-state_grouping` | I | | | *analysis* | | | | | | **after SetMaster reversal attempt \| C: master=- slaves=- group=-** |
| `240-state_grouping` | I | A | 11000 | `/RemoveSlave?slave=192.0.2.12&port=11000` | 200 | 7 | xml | `SyncStatus` | 536 | ungroup, addressed to the master |
| `241-state_grouping` | I | B | 11000 | `/SetMaster` | 200 | 21 | xml | `SyncStatus` | 433 | bare /SetMaster on the slave: the confirmed self-unjoin |
| `242-state_grouping` | I | | | *analysis* | | | | | | **after ungrouping \| A: master=- slaves=- group=-** |
| `243-state_grouping` | I | | | *analysis* | | | | | | **after ungrouping \| B: master=- slaves=- group=-** |
| `244-state_grouping` | I | | | *analysis* | | | | | | **after ungrouping \| C: master=- slaves=- group=-** |
| `245-state_grouping` | I | B | 11000 | `/AddSlave?slave=192.0.2.11&port=11000` | 200 | 38 | xml | `addSlave` | 104 | C-39 step 2: with both standalone, B takes A -- does the role stick? |
| `246-state_grouping` | I | B | 11000 | `/SyncStatus` | 200 | 14 | xml | `SyncStatus` | 393 | B after forming the reversed group -- settle read 1/3 |
| `247-state_grouping` | I | B | 11000 | `/SyncStatus` | 200 | 9 | xml | `SyncStatus` | 517 | B after forming the reversed group -- settle read 2/3 |
| `248-state_grouping` | I | B | 11000 | `/SyncStatus` | 200 | 15 | xml | `SyncStatus` | 517 | B after forming the reversed group -- settle read 3/3 |
| `249-state_grouping` | I | A | 11000 | `/SyncStatus` | 200 | 10 | xml | `SyncStatus` | 450 | A after forming the reversed group -- settle read 1/3 |
| `250-state_grouping` | I | A | 11000 | `/SyncStatus` | 200 | 14 | xml | `SyncStatus` | 450 | A after forming the reversed group -- settle read 2/3 |
| `251-state_grouping` | I | A | 11000 | `/SyncStatus` | 200 | 10 | xml | `SyncStatus` | 450 | A after forming the reversed group -- settle read 3/3 |
| `252-state_grouping` | I | | | *analysis* | | | | | | **after reversed grouping \| A: master=192.0.2.12 slaves=- group=-** |
| `253-state_grouping` | I | | | *analysis* | | | | | | **after reversed grouping \| B: master=- slaves=192.0.2.11 group=Kontor+Stue** |
| `254-state_grouping` | I | | | *analysis* | | | | | | **after reversed grouping \| C: master=- slaves=- group=-** |
| `255-state_grouping` | O | | | *analysis* | | | | | | **C-39 result: with both players standalone first, B DID become master** |
| `256-state_grouping` | I | B | 11000 | `/AddSlave?slave=192.0.2.11` | 200 | 26 | xml | `addSlave` | 104 | [T 2015 forum] singular /AddSlave with port omitted |
| `257-state_grouping` | I | B | 11000 | `/SyncStatus` | 200 | 8 | xml | `SyncStatus` | 393 | after port-less AddSlave -- settle read 1/2 |
| `258-state_grouping` | I | B | 11000 | `/SyncStatus` | 200 | 9 | xml | `SyncStatus` | 517 | after port-less AddSlave -- settle read 2/2 |
| `259-state_grouping` | I | B | 11000 | `/SlaveVolume?slave=192.0.2.11:11000&db=0` | 200 | 11 | xml | `error` | 88 | [T blutui] /SlaveVolume with a combined slave=<ip>:<port> |
| `260-state_grouping` | I | B | 11000 | `/SlaveVolume?slave=192.0.2.11&port=11000&db=0` | 200 | 12 | xml | `error` | 88 | documented separate slave= and port= form, as a control |
| `261-state_grouping` | I | B | 11000 | `/AddSlave?slave=192.0.2.11&port=11000&channelMode=1` | 200 | 8 | xml | `error` | 96 | [T HA] numeric channelMode=1 |
| `262-state_grouping` | I | A | 11000 | `/SyncStatus` | 200 | 8 | xml | `SyncStatus` | 450 | what channelMode does the slave echo back? |
| `263-state_grouping` | I | B | 11000 | `/AddSlave?slave=192.0.2.11&port=11000&channelMode=left` | 200 | 21 | xml | `addSlave` | 104 | string channelMode=left, as a control |
| `264-state_grouping` | I | A | 11000 | `/SyncStatus` | 200 | 9 | xml | `SyncStatus` | 450 | channelMode after the string form |
| `265-state_grouping` | I | B | 11000 | `/AddSlave?slave=192.0.2.11&port=11000&channelMode=default` | 200 | 12 | xml | `error` | 96 | RESTORE channelMode=default |
| `266-state_grouping` | I | B | 11000 | `/Sync?slave=192.0.2.11` | 404 | 7 | text | `` | 19 | [T bluos-dashboard] legacy /Sync?slave= |
| `267-state_grouping` | I | B | 11000 | `/Sync?remove=192.0.2.11` | 404 | 6 | text | `` | 19 | [T bluos-dashboard] legacy /Sync?remove= |
| `268-state_grouping` | I | B | 11000 | `/SyncStatus` | 200 | 7 | xml | `SyncStatus` | 517 | after the legacy /Sync calls -- settle read 1/2 |
| `269-state_grouping` | I | B | 11000 | `/SyncStatus` | 200 | 12 | xml | `SyncStatus` | 517 | after the legacy /Sync calls -- settle read 2/2 |
| `270-state_grouping` | I | B | 11000 | `/AddSlave?slave=192.0.2.13&port=11000` | 200 | 25 | xml | `addSlave` | 104 | add a second slave so bare /RemoveSlave has something to prove |
| `271-state_grouping` | I | B | 11000 | `/SyncStatus` | 200 | 7 | xml | `SyncStatus` | 517 | two slaves present -- settle read 1/2 |
| `272-state_grouping` | I | B | 11000 | `/SyncStatus` | 200 | 9 | xml | `SyncStatus` | 623 | two slaves present -- settle read 2/2 |
| `273-state_grouping` | I | B | 11000 | `/RemoveSlave` | 200 | 9 | xml | `SyncStatus` | 623 | [T HA] does a bare /RemoveSlave drop every slave? |
| `274-state_grouping` | I | B | 11000 | `/SyncStatus` | 200 | 30 | xml | `SyncStatus` | 623 | after bare /RemoveSlave -- settle read 1/3 |
| `275-state_grouping` | I | B | 11000 | `/SyncStatus` | 200 | 10 | xml | `SyncStatus` | 623 | after bare /RemoveSlave -- settle read 2/3 |
| `276-state_grouping` | I | B | 11000 | `/SyncStatus` | 200 | 10 | xml | `SyncStatus` | 623 | after bare /RemoveSlave -- settle read 3/3 |
| `277-state_grouping` | I | | | *analysis* | | | | | | **after bare /RemoveSlave \| A: master=192.0.2.12 slaves=- group=-** |
| `278-state_grouping` | I | | | *analysis* | | | | | | **after bare /RemoveSlave \| B: master=- slaves=192.0.2.13,192.0.2.11 group=Kontor + 2** |
| `279-state_grouping` | I | | | *analysis* | | | | | | **after bare /RemoveSlave \| C: master=192.0.2.12 slaves=- group=-** |
| `280-state_grouping` | U | | | *analysis* | | | | | | **C-30: slaves remaining after a bare /RemoveSlave: 2** |
| `281-state_grouping` | I | B | 11000 | `/RemoveSlave?slaves=192.0.2.13,192.0.2.11&ports=11000,11000` | 200 | 10 | xml | `SyncStatus` | 623 | teardown: free the slaves of B |
| `282-state_grouping` | O | | | *analysis* | | | | | | **original topology restored: yes** |

### state_grouping -- analysis detail

**C-39 step 1: reversing without ungrouping first** (`219-state_grouping`)

```
the app appears to ungroup before re-forming; this measures what happens if you do not
```

**C-39 result: with both players standalone first, B DID become master** (`255-state_grouping`)

```
If this works and the direct reversal did not, the rule is simply that role is decided at group formation and cannot be transferred while the group exists -- which is exactly what the official app works around by ungrouping first. If A still refuses to be a slave, the cause is a property of the player rather than of the sequence, and the next thing to compare is model, firmware, address ordering and hasSubwoofer.
```

**C-30: slaves remaining after a bare /RemoveSlave: 2** (`280-state_grouping`)

```
Zero means the claim holds. Anything else means a bare /RemoveSlave does NOT drop every slave, and a client must name them.
```

**original topology restored: yes** (`282-state_grouping`)

```
A: before master=- slaves=[] / after master=- slaves=[]
B: before master=- slaves=[] / after master=- slaves=[]
C: before master=- slaves=[] / after master=- slaves=[]
D: before master=- slaves=[] / after master=- slaves=[]
```

## suite: state_name

| id | v | player | port | request | status | ms | type | root | bytes | note |
|---|---|---|---|---|---|---|---|---|---|---|
| `150-state_name` | I | A | 11000 | `/Name?set=ProbeTest` | 200 | 142 | xml | `name` | 61 | write via ?set= |
| `151-state_name` | I | A | 11000 | `/SyncStatus` | 200 | 13 | xml | `SyncStatus` | 415 | name after ?set= |
| `152-state_name` | I | A | 11000 | `POST /Name` | 200 | 143 | xml | `name` | 62 | [T blutui] write via POST nodename= |
| `153-state_name` | I | A | 11000 | `/Name` | 200 | 12 | xml | `name` | 62 | name after POST |
| `154-state_name` | I | A | 11000 | `/Name?set=Stue` | 200 | 139 | xml | `name` | 56 | RESTORE original name |
| `155-state_name` | O | | | *analysis* | | | | | | **A name restored: yes** |
| `156-state_name` | I | | | *analysis* | | | | | | **T-19 reminder** |

### state_name -- analysis detail

**T-19 reminder** (`156-state_name`)

```
whether the name survives a reboot still needs a power cycle; read /Name the next time a player restarts for any other reason
```

## suite: state_playback

| id | v | player | port | request | status | ms | type | root | bytes | note |
|---|---|---|---|---|---|---|---|---|---|---|
| `073-state_playback` | I | A | 11000 | `/Volume?level=10` | 200 | 8 | xml | `volume` | 142 | cap A at level 10 before starting audio (was 46) |
| `074-state_playback` | I | | | *analysis* | | | | | | **A volume lowered from 46 to the --max-volume ceiling of 10** |
| `075-state_playback` | I | | | *analysis* | | | | | | **A starting state=stop service=Tidal secs=0** |
| `076-state_playback` | I | A | 11000 | `/Pause` | 200 | 8 | xml | `state` | 59 | pause |
| `077-state_playback` | I | A | 11000 | `/Status` | 200 | 8 | xml | `status` | 1192 | state after /Pause |
| `078-state_playback` | I | A | 11000 | `/Play` | 200 | 10 | xml | `state` | 58 | bare /Play resumes |
| `079-state_playback` | I | A | 11000 | `/Status` | 200 | 8 | xml | `status` | 1192 | state after /Play |
| `080-state_playback` | I | A | 11000 | `/Pause?toggle=1` | 200 | 13 | xml | `state` | 58 | toggle form |
| `081-state_playback` | I | A | 11000 | `/Status` | 200 | 17 | xml | `status` | 1194 | state after toggle |
| `082-state_playback` | I | A | 11000 | `/Pause?toggle=1` | 200 | 8 | xml | `state` | 59 | toggle back |
| `083-state_playback` | I | A | 11000 | `/Playlist` | 200 | 12 | xml | `playlist` | 14442 | queue flags before bare /Repeat |
| `084-state_playback` | I | A | 11000 | `/Repeat` | 200 | 7 | xml | `error` | 86 | bare /Repeat: read or write? |
| `085-state_playback` | I | A | 11000 | `/Shuffle` | 200 | 8 | xml | `playlist` | 105 | bare /Shuffle: read or write? |
| `086-state_playback` | I | A | 11000 | `/Playlist` | 200 | 18 | xml | `playlist` | 14442 | queue flags after bare /Repeat and /Shuffle |
| `087-state_playback` | I | | | *analysis* | | | | | | **C-40: bare /Repeat and /Shuffle CHANGED the queue flags** |
| `088-state_playback` | U | | | *analysis* | | | | | | **A restore: state stop -> pause** |
| `089-state_playback` | I | B | 11000 | `/Volume?level=10` | 200 | 9 | xml | `volume` | 142 | cap B at level 10 before starting audio (was 27) |
| `090-state_playback` | I | | | *analysis* | | | | | | **B volume lowered from 27 to the --max-volume ceiling of 10** |
| `091-state_playback` | I | | | *analysis* | | | | | | **B starting state=stop service=Tidal secs=0** |
| `092-state_playback` | I | B | 11000 | `/Pause` | 200 | 8 | xml | `state` | 59 | pause |
| `093-state_playback` | I | B | 11000 | `/Status` | 200 | 10 | xml | `status` | 1252 | state after /Pause |
| `094-state_playback` | I | B | 11000 | `/Play` | 200 | 11 | xml | `state` | 58 | bare /Play resumes |
| `095-state_playback` | I | B | 11000 | `/Status` | 200 | 12 | xml | `status` | 1252 | state after /Play |
| `096-state_playback` | I | B | 11000 | `/Pause?toggle=1` | 200 | 10 | xml | `state` | 58 | toggle form |
| `097-state_playback` | I | B | 11000 | `/Status` | 200 | 9 | xml | `status` | 1252 | state after toggle |
| `098-state_playback` | I | B | 11000 | `/Pause?toggle=1` | 200 | 7 | xml | `state` | 59 | toggle back |
| `099-state_playback` | I | B | 11000 | `/Playlist` | 200 | 23 | xml | `playlist` | 62326 | queue flags before bare /Repeat |
| `100-state_playback` | I | B | 11000 | `/Repeat` | 200 | 10 | xml | `error` | 86 | bare /Repeat: read or write? |
| `101-state_playback` | I | B | 11000 | `/Shuffle` | 200 | 15 | xml | `playlist` | 105 | bare /Shuffle: read or write? |
| `102-state_playback` | I | B | 11000 | `/Playlist` | 200 | 22 | xml | `playlist` | 62326 | queue flags after bare /Repeat and /Shuffle |
| `103-state_playback` | I | | | *analysis* | | | | | | **C-40: bare /Repeat and /Shuffle CHANGED the queue flags** |
| `104-state_playback` | U | | | *analysis* | | | | | | **B restore: state stop -> pause** |
| `105-state_playback` | I | C | 11000 | `/Volume?level=10` | 200 | 13 | xml | `volume` | 142 | cap C at level 10 before starting audio (was 38) |
| `106-state_playback` | I | | | *analysis* | | | | | | **C volume lowered from 38 to the --max-volume ceiling of 10** |
| `107-state_playback` | I | | | *analysis* | | | | | | **C starting state=stop service=Tidal secs=0** |
| `108-state_playback` | I | C | 11000 | `/Pause` | 200 | 10 | xml | `state` | 59 | pause |
| `109-state_playback` | I | C | 11000 | `/Status` | 200 | 8 | xml | `status` | 1251 | state after /Pause |
| `110-state_playback` | I | C | 11000 | `/Play` | 200 | 14 | xml | `state` | 58 | bare /Play resumes |
| `111-state_playback` | I | C | 11000 | `/Status` | 200 | 9 | xml | `status` | 1251 | state after /Play |
| `112-state_playback` | I | C | 11000 | `/Pause?toggle=1` | 200 | 11 | xml | `state` | 58 | toggle form |
| `113-state_playback` | I | C | 11000 | `/Status` | 200 | 15 | xml | `status` | 1253 | state after toggle |
| `114-state_playback` | I | C | 11000 | `/Pause?toggle=1` | 200 | 10 | xml | `state` | 59 | toggle back |
| `115-state_playback` | I | C | 11000 | `/Playlist` | 200 | 15 | xml | `playlist` | 15105 | queue flags before bare /Repeat |
| `116-state_playback` | I | C | 11000 | `/Repeat` | 200 | 8 | xml | `error` | 86 | bare /Repeat: read or write? |
| `117-state_playback` | I | C | 11000 | `/Shuffle` | 200 | 8 | xml | `playlist` | 104 | bare /Shuffle: read or write? |
| `118-state_playback` | I | C | 11000 | `/Playlist` | 200 | 16 | xml | `playlist` | 15105 | queue flags after bare /Repeat and /Shuffle |
| `119-state_playback` | I | | | *analysis* | | | | | | **C-40: bare /Repeat and /Shuffle left the queue flags** |
| `120-state_playback` | U | | | *analysis* | | | | | | **C restore: state stop -> pause** |
| `121-state_playback` | I | D | 11000 | `/Volume?level=10` | 200 | 16 | xml | `volume` | 141 | cap D at level 10 before starting audio (was 13) |
| `122-state_playback` | I | | | *analysis* | | | | | | **D volume lowered from 13 to the --max-volume ceiling of 10** |
| `123-state_playback` | I | | | *analysis* | | | | | | **D starting state=play service=Tidal secs=36** |
| `124-state_playback` | I | D | 11000 | `/Pause` | 200 | 18 | xml | `state` | 59 | pause |
| `125-state_playback` | I | D | 11000 | `/Status` | 200 | 18 | xml | `status` | 1276 | state after /Pause |
| `126-state_playback` | I | D | 11000 | `/Play` | 200 | 17 | xml | `state` | 58 | bare /Play resumes |
| `127-state_playback` | I | D | 11000 | `/Status` | 200 | 12 | xml | `status` | 1276 | state after /Play |
| `128-state_playback` | I | D | 11000 | `/Pause?toggle=1` | 200 | 17 | xml | `state` | 59 | toggle form |
| `129-state_playback` | I | D | 11000 | `/Status` | 200 | 11 | xml | `status` | 1276 | state after toggle |
| `130-state_playback` | I | D | 11000 | `/Pause?toggle=1` | 200 | 29 | xml | `state` | 58 | toggle back |
| `131-state_playback` | I | D | 11000 | `/Playlist` | 200 | 45 | xml | `playlist` | 15106 | queue flags before bare /Repeat |
| `132-state_playback` | I | D | 11000 | `/Repeat` | 200 | 11 | xml | `error` | 86 | bare /Repeat: read or write? |
| `133-state_playback` | I | D | 11000 | `/Shuffle` | 200 | 29 | xml | `playlist` | 105 | bare /Shuffle: read or write? |
| `134-state_playback` | I | D | 11000 | `/Playlist` | 200 | 52 | xml | `playlist` | 15106 | queue flags after bare /Repeat and /Shuffle |
| `135-state_playback` | I | | | *analysis* | | | | | | **C-40: bare /Repeat and /Shuffle left the queue flags** |
| `136-state_playback` | I | D | 11000 | `/Play` | 200 | 12 | xml | `state` | 58 | RESTORE playback |
| `137-state_playback` | O | | | *analysis* | | | | | | **D restore: state play -> play** |

### state_playback -- analysis detail

**A volume lowered from 46 to the --max-volume ceiling of 10** (`074-state_playback`)

```
restored from the ledger at the end of the run
```

**C-40: bare /Repeat and /Shuffle CHANGED the queue flags** (`087-state_playback`)

```
before {'repeat': '2', 'shuffle': '1'} / after {'repeat': '2', 'shuffle': '0'} -- a read leaves them alone; a write does not
```

**A restore: state stop -> pause** (`088-state_playback`)

```
track position is not restorable through the API; secs 0 -> 0
```

**B volume lowered from 27 to the --max-volume ceiling of 10** (`090-state_playback`)

```
restored from the ledger at the end of the run
```

**C-40: bare /Repeat and /Shuffle CHANGED the queue flags** (`103-state_playback`)

```
before {'repeat': '2', 'shuffle': '1'} / after {'repeat': '2', 'shuffle': '0'} -- a read leaves them alone; a write does not
```

**B restore: state stop -> pause** (`104-state_playback`)

```
track position is not restorable through the API; secs 0 -> 0
```

**C volume lowered from 38 to the --max-volume ceiling of 10** (`106-state_playback`)

```
restored from the ledger at the end of the run
```

**C-40: bare /Repeat and /Shuffle left the queue flags** (`119-state_playback`)

```
before {'repeat': '2', 'shuffle': '0'} / after {'repeat': '2', 'shuffle': '0'} -- a read leaves them alone; a write does not
```

**C restore: state stop -> pause** (`120-state_playback`)

```
track position is not restorable through the API; secs 0 -> 0
```

**D volume lowered from 13 to the --max-volume ceiling of 10** (`122-state_playback`)

```
restored from the ledger at the end of the run
```

**C-40: bare /Repeat and /Shuffle left the queue flags** (`135-state_playback`)

```
before {'repeat': '2', 'shuffle': '0'} / after {'repeat': '2', 'shuffle': '0'} -- a read leaves them alone; a write does not
```

**D restore: state play -> play** (`137-state_playback`)

```
track position is not restorable through the API; secs 36 -> 38
```

## suite: state_preset

| id | v | player | port | request | status | ms | type | root | bytes | note |
|---|---|---|---|---|---|---|---|---|---|---|
| `164-state_preset` | I | D | 11000 | `/Presets` | 200 | 17 | xml | `presets` | 424 | preset list on the player about to be used |
| `165-state_preset` | I | | | *analysis* | | | | | | **recalling on D -- presets are READ ONLY here, only recalled** |
| `166-state_preset` | I | D | 11000 | `/Preset?id=1` | 200 | 22 | xml | `state` | 60 | recall preset 1 -- record the response root |
| `167-state_preset` | I | D | 11000 | `/Status` | 200 | 28 | xml | `status` | 1862 | does /Status carry <is_preset> / <preset_name> while a preset plays? |
| `168-state_preset` | I | D | 11000 | `/Preset?id=2` | 200 | 607 | xml | `loaded` | 93 | recall preset 2 -- record the response root |
| `169-state_preset` | I | D | 11000 | `/Status` | 200 | 21 | xml | `status` | 1327 | does /Status carry <is_preset> / <preset_name> while a preset plays? |
| `170-state_preset` | I | | | *analysis* | | | | | | **restoring playback state on D** |

### state_preset -- analysis detail

**recalling on D -- presets are READ ONLY here, only recalled** (`165-state_preset`)

```
ids seen: 1, 2
```

**restoring playback state on D** (`170-state_preset`)

```
state was play / Tidal; a recalled preset cannot be un-recalled through the API, so the previous source is restored only if it was a preset itself
```

## suite: state_setting

| id | v | player | port | request | status | ms | type | root | bytes | note |
|---|---|---|---|---|---|---|---|---|---|---|
| `157-state_setting` | I | | | *analysis* | | | | | | **ledbrightness before: off** |
| `158-state_setting` | I | A | 11000 | `/setting?ledbrightness=1` | 200 | 9 | none | `` | 0 | write style A: GET query |
| `159-state_setting` | I | A | 11001 | `/Settings?id=player&schemaVersion=35` | 200 | 9 | xml | `settings` | 1385 | read back after GET-query write |
| `160-state_setting` | I | A | 11000 | `POST /setting` | 200 | 9 | none | `` | 0 | write style B: POST form |
| `161-state_setting` | I | A | 11001 | `/Settings?id=player&schemaVersion=35` | 200 | 12 | xml | `settings` | 1385 | read back after POST-form write |
| `162-state_setting` | I | | | *analysis* | | | | | | **ledbrightness: GET query took effect, POST form did not** |
| `163-state_setting` | I | A | 11000 | `/setting?ledbrightness=off` | 200 | 9 | none | `` | 0 | RESTORE ledbrightness |

### state_setting -- analysis detail

**ledbrightness before: off** (`157-state_setting`)

```
<setting id="ledbrightness" name="ledbrightness" displayName="Indicator brightness" url="/setting" icon="/images/settings/ic_indicatorlight.png" class="list" value="off" description="Off">
```

**ledbrightness: GET query took effect, POST form did not** (`162-state_setting`)

```
before=off after GET=dim (asked 1) after POST=dim (asked 2). The tree reports a display string, so a change of value is the signal, not an echo of the number. blutui says the write must be a POST form; pyblu uses a GET query. Only the readback can tell them apart, because BluOS answers 200 to both.
```

## suite: state_sleep

| id | v | player | port | request | status | ms | type | root | bytes | note |
|---|---|---|---|---|---|---|---|---|---|---|
| `138-state_sleep` | I | A | 11000 | `/Sleep?minutes=15` | 200 | 8 | xml | `sleep` | 56 | set sleep 15 |
| `139-state_sleep` | I | A | 11000 | `/Sleep?minutes=17` | 200 | 9 | xml | `sleep` | 56 | set sleep 17 |
| `140-state_sleep` | I | A | 11000 | `/Sleep?minutes=0` | 200 | 8 | xml | `sleep` | 54 | set sleep 0 |
| `141-state_sleep` | I | A | 11000 | `/Sleep` | 200 | 8 | xml | `sleep` | 56 | bare /Sleep cycle step 1 |
| `142-state_sleep` | I | A | 11000 | `/Sleep` | 200 | 8 | xml | `sleep` | 56 | bare /Sleep cycle step 2 |
| `143-state_sleep` | I | A | 11000 | `/Sleep` | 200 | 8 | xml | `sleep` | 56 | bare /Sleep cycle step 3 |
| `144-state_sleep` | I | A | 11000 | `/Sleep` | 200 | 8 | xml | `sleep` | 56 | bare /Sleep cycle step 4 |
| `145-state_sleep` | I | A | 11000 | `/Sleep` | 200 | 9 | xml | `sleep` | 56 | bare /Sleep cycle step 5 |
| `146-state_sleep` | I | A | 11000 | `/Sleep` | 200 | 8 | xml | `sleep` | 54 | bare /Sleep cycle step 6 |
| `147-state_sleep` | I | A | 11000 | `/Sleep` | 200 | 8 | xml | `sleep` | 56 | bare /Sleep cycle step 7 |
| `148-state_sleep` | I | | | *analysis* | | | | | | **bare /Sleep cycles through: <?xmlversion="1.0"encoding="UTF-8"?><sleep>15</sleep> -> <?xmlversion="1.0"encoding="UTF-8"?><sleep>30</sleep> -> <?xmlversion="1.0"encoding="UTF-8"?><sleep>45</sleep> -> <?xmlversion="1.0"encoding="UTF-8"?><sleep>60</sleep> -> <?xmlversion="1.0"encoding="UTF-8"?><sleep>90</sleep> -> <?xmlversion="1.0"encoding="UTF-8"?><sleep></sleep> -> <?xmlversion="1.0"encoding="UTF-8"?><sleep>15</sleep>** |
| `149-state_sleep` | I | A | 11000 | `/Sleep?minutes=0` | 200 | 7 | xml | `sleep` | 54 | RESTORE sleep off |

### state_sleep -- analysis detail

**bare /Sleep cycles through: <?xmlversion="1.0"encoding="UTF-8"?><sleep>15</sleep> -> <?xmlversion="1.0"encoding="UTF-8"?><sleep>30</sleep> -> <?xmlversion="1.0"encoding="UTF-8"?><sleep>45</sleep> -> <?xmlversion="1.0"encoding="UTF-8"?><sleep>60</sleep> -> <?xmlversion="1.0"encoding="UTF-8"?><sleep>90</sleep> -> <?xmlversion="1.0"encoding="UTF-8"?><sleep></sleep> -> <?xmlversion="1.0"encoding="UTF-8"?><sleep>15</sleep>** (`148-state_sleep`)

```
the Integration Utility offers 0/15/30/45/60; this is the real cycle
```

## suite: state_source

| id | v | player | port | request | status | ms | type | root | bytes | note |
|---|---|---|---|---|---|---|---|---|---|---|
| `173-state_source` | I | A | 11000 | `/Browse` | 200 | 9 | xml | `browse` | 983 | browse root: inputType values and playURLs |
| `174-state_source` | I | A | 11000 | `/RadioBrowse?service=Capture` | 200 | 11 | xml | `radiotime` | 412 | the Capture input list |
| `175-state_source` | I | | | *analysis* | | | | | | **A: 1 advertised input(s), inputType values: arc** |
| `176-state_source` | I | A | 11000 | `/Play` | 200 | 10 | xml | `state` | 58 | start playback, so an ignored parameter cannot masquerade as success |
| `177-state_source` | I | A | 11000 | `/Play?url=Capture%3Ahw%3Aimxspdif%2C0%2F1%2F25%2F2%3Fid%3Dinput2` | 200 | 10 | xml | `state` | 60 | POSITIVE CONTROL: select input 1 by the playURL the device supplied |
| `178-state_source` | I | | | *analysis* | | | | | | **learned input 1: streamUrl=Capture:hw:imxspdif,0/1/25/2?id=input2 title1=HDMI ARC (0.6s)** |
| `179-state_source` | U | | | *analysis* | | | | | | **fewer than two distinguishable inputs were learned (1)** |
| `180-state_source` | I | A | 11000 | `/Play?inputType=zzznotreal&index=1` | 404 | 7 | none | `` | 0 | selector that cannot exist (from input#1 via playURL) |
| `181-state_source` | O | | | *analysis* | | | | | | **NEGATIVE CONTROL /Play?inputType=zzznotreal&index=1 -> IGNORED** |
| `182-state_source` | I | A | 11000 | `/Play?inputTypeIndex=zzznotreal-9` | 404 | 10 | none | `` | 0 | inputTypeIndex that cannot exist (from input#1 via playURL) |
| `183-state_source` | O | | | *analysis* | | | | | | **NEGATIVE CONTROL /Play?inputTypeIndex=zzznotreal-9 -> IGNORED** |
| `184-state_source` | I | A | 11000 | `/Play?inputIndex=99` | 404 | 9 | none | `` | 0 | input index far beyond any real input (from input#1 via playURL) |
| `185-state_source` | O | | | *analysis* | | | | | | **NEGATIVE CONTROL /Play?inputIndex=99 -> IGNORED** |
| `186-state_source` | I | A | 11000 | `/Play?inputIndex=2` | 200 | 93 | xml | `state` | 60 | the confirmed inputIndex form (from input#1 via playURL) |
| `187-state_source` | I | | | *analysis* | | | | | | **/Play?inputIndex=2 -> SELECTED SOMETHING NOT ADVERTISED** |
| `188-state_source` | I | A | 11000 | `/Play?inputType=arc&index=1` | 200 | 95 | xml | `state` | 60 | [T bluos-api-rs] inputType=arc&index=1 (from input#1 via playURL) |
| `189-state_source` | I | | | *analysis* | | | | | | **/Play?inputType=arc&index=1 -> SELECTED SOMETHING NOT ADVERTISED** |
| `190-state_source` | I | A | 11000 | `/Play?inputTypeIndex=arc-1` | 200 | 88 | xml | `state` | 60 | T-18 retest: inputTypeIndex=arc-1 (from input#1 via playURL) |
| `191-state_source` | I | | | *analysis* | | | | | | **/Play?inputTypeIndex=arc-1 -> SELECTED SOMETHING NOT ADVERTISED** |
| `192-state_source` | I | A | 11000 | `/Play?inputTypeIndex=hdmi-1` | 404 | 8 | none | `` | 0 | unadvertised slot hdmi-1: is a disabled input still reachable? (from input#1 via playURL) |
| `193-state_source` | I | | | *analysis* | | | | | | **/Play?inputTypeIndex=hdmi-1 -> IGNORED** |
| `194-state_source` | I | A | 11000 | `/Play?inputTypeIndex=optical-1` | 404 | 8 | none | `` | 0 | unadvertised slot optical-1: is a disabled input still reachable? (from input#1 via playURL) |
| `195-state_source` | I | | | *analysis* | | | | | | **/Play?inputTypeIndex=optical-1 -> IGNORED** |
| `196-state_source` | I | A | 11000 | `/Play?inputTypeIndex=spdif-1` | 404 | 8 | none | `` | 0 | unadvertised slot spdif-1: is a disabled input still reachable? (from input#1 via playURL) |
| `197-state_source` | I | | | *analysis* | | | | | | **/Play?inputTypeIndex=spdif-1 -> IGNORED** |
| `198-state_source` | I | A | 11000 | `/Play?inputTypeIndex=analog-1` | 404 | 12 | none | `` | 0 | unadvertised slot analog-1: is a disabled input still reachable? (from input#1 via playURL) |
| `199-state_source` | I | | | *analysis* | | | | | | **/Play?inputTypeIndex=analog-1 -> IGNORED** |
| `200-state_source` | I | A | 11000 | `/Play?inputTypeIndex=bluetooth-1` | 404 | 7 | none | `` | 0 | unadvertised slot bluetooth-1: is a disabled input still reachable? (from input#1 via playURL) |
| `201-state_source` | I | | | *analysis* | | | | | | **/Play?inputTypeIndex=bluetooth-1 -> IGNORED** |
| `202-state_source` | I | A | 11000 | `/Play?inputType=zzznotreal&index=2` | 404 | 7 | none | `` | 0 | repeat of the impossible selector (from input#1 via playURL) |
| `203-state_source` | O | | | *analysis* | | | | | | **NEGATIVE CONTROL /Play?inputType=zzznotreal&index=2 -> IGNORED** |
| `204-state_source` | I | | | *analysis* | | | | | | **A: source restore is best-effort** |
| `205-state_source` | I | A | 11000 | `/Pause` | 200 | 9 | xml | `state` | 59 | RESTORE paused |

### state_source -- analysis detail

**fewer than two distinguishable inputs were learned (1)** (`179-state_source`)

```
With one input, 'did it switch' cannot be separated from 'it was already there'. Results below are weaker; enable a second input, or read them as suggestive only.
```

**NEGATIVE CONTROL /Play?inputType=zzznotreal&index=1 -> IGNORED** (`181-state_source`)

```
no field in service, inputId, streamUrl, title1, title2, title3, image, streamFormat, quality, song changed, from 1 different starting input(s). state connecting -> connecting.

Good: a meaningless selector moves nothing, so a positive result elsewhere is a real one.
```

**NEGATIVE CONTROL /Play?inputTypeIndex=zzznotreal-9 -> IGNORED** (`183-state_source`)

```
no field in service, inputId, streamUrl, title1, title2, title3, image, streamFormat, quality, song changed, from 1 different starting input(s). state connecting -> connecting.

Good: a meaningless selector moves nothing, so a positive result elsewhere is a real one.
```

**NEGATIVE CONTROL /Play?inputIndex=99 -> IGNORED** (`185-state_source`)

```
no field in service, inputId, streamUrl, title1, title2, title3, image, streamFormat, quality, song changed, from 1 different starting input(s). state connecting -> connecting.

Good: a meaningless selector moves nothing, so a positive result elsewhere is a real one.
```

**/Play?inputIndex=2 -> SELECTED SOMETHING NOT ADVERTISED** (`187-state_source`)

```
landed on a source with no advertised playURL: streamUrl=Capture:hw:imxspdif,0/1/25/2?id=input1 title1=- inputId=-. If that slot is disabled in the Controller app, then 'disabled' is a view filter and not a capability gate.
```

**/Play?inputType=arc&index=1 -> SELECTED SOMETHING NOT ADVERTISED** (`189-state_source`)

```
landed on a source with no advertised playURL: streamUrl=Capture:hw:imxspdif,0/1/25/2?id=input2 title1=- inputId=-. If that slot is disabled in the Controller app, then 'disabled' is a view filter and not a capability gate.
```

**/Play?inputTypeIndex=arc-1 -> SELECTED SOMETHING NOT ADVERTISED** (`191-state_source`)

```
landed on a source with no advertised playURL: streamUrl=Capture:hw:imxspdif,0/1/25/2?id=input2 title1=- inputId=-. If that slot is disabled in the Controller app, then 'disabled' is a view filter and not a capability gate.
```

**/Play?inputTypeIndex=hdmi-1 -> IGNORED** (`193-state_source`)

```
no field in service, inputId, streamUrl, title1, title2, title3, image, streamFormat, quality, song changed, from 1 different starting input(s). state connecting -> connecting.
```

**/Play?inputTypeIndex=optical-1 -> IGNORED** (`195-state_source`)

```
no field in service, inputId, streamUrl, title1, title2, title3, image, streamFormat, quality, song changed, from 1 different starting input(s). state connecting -> connecting.
```

**/Play?inputTypeIndex=spdif-1 -> IGNORED** (`197-state_source`)

```
no field in service, inputId, streamUrl, title1, title2, title3, image, streamFormat, quality, song changed, from 1 different starting input(s). state connecting -> connecting.
```

**/Play?inputTypeIndex=analog-1 -> IGNORED** (`199-state_source`)

```
no field in service, inputId, streamUrl, title1, title2, title3, image, streamFormat, quality, song changed, from 1 different starting input(s). state connecting -> connecting.
```

**/Play?inputTypeIndex=bluetooth-1 -> IGNORED** (`201-state_source`)

```
no field in service, inputId, streamUrl, title1, title2, title3, image, streamFormat, quality, song changed, from 1 different starting input(s). state connecting -> connecting.
```

**NEGATIVE CONTROL /Play?inputType=zzznotreal&index=2 -> IGNORED** (`203-state_source`)

```
no field in service, inputId, streamUrl, title1, title2, title3, image, streamFormat, quality, song changed, from 1 different starting input(s). state connecting -> connecting.

Good: a meaningless selector moves nothing, so a positive result elsewhere is a real one.
```

**A: source restore is best-effort** (`204-state_source`)

```
was service=Tidal songid=Tidal:106600734 state=pause. An input switch cannot be undone through the API without re-selecting the previous source by hand.
```

## suite: state_volume

| id | v | player | port | request | status | ms | type | root | bytes | note |
|---|---|---|---|---|---|---|---|---|---|---|
| `001-state_volume` | I | | | *analysis* | | | | | | **A starting volume 46, mute=0** |
| `002-state_volume` | I | A | 11000 | `/Volume?level=1` | 200 | 9 | xml | `volume` | 141 | set absolute level 1 |
| `003-state_volume` | I | A | 11000 | `/Volume` | 200 | 15 | xml | `volume` | 141 | read back after level=1 |
| `004-state_volume` | I | A | 11000 | `/Volume?level=5` | 200 | 8 | xml | `volume` | 141 | set absolute level 5 |
| `005-state_volume` | I | A | 11000 | `/Volume` | 200 | 7 | xml | `volume` | 141 | read back after level=5 |
| `006-state_volume` | I | A | 11000 | `/Volume?level=10` | 200 | 7 | xml | `volume` | 142 | set absolute level 10 |
| `007-state_volume` | I | A | 11000 | `/Volume` | 200 | 9 | xml | `volume` | 142 | read back after level=10 |
| `008-state_volume` | I | A | 11000 | `/Volume?mute=1` | 200 | 8 | xml | `volume` | 171 | mute=1 |
| `009-state_volume` | I | A | 11000 | `/Volume` | 200 | 8 | xml | `volume` | 171 | read back after mute=1 |
| `010-state_volume` | I | A | 11000 | `/Volume?mute=0` | 200 | 9 | xml | `volume` | 142 | mute=0 |
| `011-state_volume` | I | A | 11000 | `/Volume` | 200 | 8 | xml | `volume` | 142 | read back after mute=0 |
| `012-state_volume` | O | | | *analysis* | | | | | | **A mute polarity: mute=1 -> muted, mute=0 -> unmuted** |
| `013-state_volume` | I | A | 11000 | `/Volume?db=-2` | 200 | 9 | xml | `volume` | 141 | relative db=-2 |
| `014-state_volume` | I | A | 11000 | `/Volume?db=2` | 200 | 10 | xml | `volume` | 142 | relative db=+2 |
| `015-state_volume` | I | A | 11000 | `/Volume` | 200 | 10 | xml | `volume` | 142 | read back after relative db |
| `016-state_volume` | I | A | 11000 | `/Volume?level=46` | 200 | 7 | xml | `volume` | 140 | RESTORE volume to 46 |
| `017-state_volume` | I | A | 11000 | `/Volume?mute=0` | 200 | 11 | xml | `volume` | 140 | RESTORE mute state |
| `018-state_volume` | O | | | *analysis* | | | | | | **A restore verified: yes** |
| `019-state_volume` | I | | | *analysis* | | | | | | **B starting volume 27, mute=0** |
| `020-state_volume` | I | B | 11000 | `/Volume?level=1` | 200 | 9 | xml | `volume` | 141 | set absolute level 1 |
| `021-state_volume` | I | B | 11000 | `/Volume` | 200 | 9 | xml | `volume` | 141 | read back after level=1 |
| `022-state_volume` | I | B | 11000 | `/Volume?level=5` | 200 | 8 | xml | `volume` | 141 | set absolute level 5 |
| `023-state_volume` | I | B | 11000 | `/Volume` | 200 | 6 | xml | `volume` | 141 | read back after level=5 |
| `024-state_volume` | I | B | 11000 | `/Volume?level=10` | 200 | 8 | xml | `volume` | 142 | set absolute level 10 |
| `025-state_volume` | I | B | 11000 | `/Volume` | 200 | 7 | xml | `volume` | 142 | read back after level=10 |
| `026-state_volume` | I | B | 11000 | `/Volume?mute=1` | 200 | 11 | xml | `volume` | 171 | mute=1 |
| `027-state_volume` | I | B | 11000 | `/Volume` | 200 | 13 | xml | `volume` | 171 | read back after mute=1 |
| `028-state_volume` | I | B | 11000 | `/Volume?mute=0` | 200 | 8 | xml | `volume` | 142 | mute=0 |
| `029-state_volume` | I | B | 11000 | `/Volume` | 200 | 7 | xml | `volume` | 142 | read back after mute=0 |
| `030-state_volume` | O | | | *analysis* | | | | | | **B mute polarity: mute=1 -> muted, mute=0 -> unmuted** |
| `031-state_volume` | I | B | 11000 | `/Volume?db=-2` | 200 | 9 | xml | `volume` | 141 | relative db=-2 |
| `032-state_volume` | I | B | 11000 | `/Volume?db=2` | 200 | 9 | xml | `volume` | 142 | relative db=+2 |
| `033-state_volume` | I | B | 11000 | `/Volume` | 200 | 9 | xml | `volume` | 142 | read back after relative db |
| `034-state_volume` | I | B | 11000 | `/Volume?level=27` | 200 | 9 | xml | `volume` | 142 | RESTORE volume to 27 |
| `035-state_volume` | I | B | 11000 | `/Volume?mute=0` | 200 | 8 | xml | `volume` | 142 | RESTORE mute state |
| `036-state_volume` | O | | | *analysis* | | | | | | **B restore verified: yes** |
| `037-state_volume` | I | | | *analysis* | | | | | | **C starting volume 38, mute=0** |
| `038-state_volume` | I | C | 11000 | `/Volume?level=1` | 200 | 9 | xml | `volume` | 141 | set absolute level 1 |
| `039-state_volume` | I | C | 11000 | `/Volume` | 200 | 10 | xml | `volume` | 141 | read back after level=1 |
| `040-state_volume` | I | C | 11000 | `/Volume?level=5` | 200 | 12 | xml | `volume` | 141 | set absolute level 5 |
| `041-state_volume` | I | C | 11000 | `/Volume` | 200 | 8 | xml | `volume` | 141 | read back after level=5 |
| `042-state_volume` | I | C | 11000 | `/Volume?level=10` | 200 | 9 | xml | `volume` | 142 | set absolute level 10 |
| `043-state_volume` | I | C | 11000 | `/Volume` | 200 | 8 | xml | `volume` | 142 | read back after level=10 |
| `044-state_volume` | I | C | 11000 | `/Volume?mute=1` | 200 | 10 | xml | `volume` | 171 | mute=1 |
| `045-state_volume` | I | C | 11000 | `/Volume` | 200 | 8 | xml | `volume` | 171 | read back after mute=1 |
| `046-state_volume` | I | C | 11000 | `/Volume?mute=0` | 200 | 11 | xml | `volume` | 142 | mute=0 |
| `047-state_volume` | I | C | 11000 | `/Volume` | 200 | 8 | xml | `volume` | 142 | read back after mute=0 |
| `048-state_volume` | O | | | *analysis* | | | | | | **C mute polarity: mute=1 -> muted, mute=0 -> unmuted** |
| `049-state_volume` | I | C | 11000 | `/Volume?db=-2` | 200 | 9 | xml | `volume` | 141 | relative db=-2 |
| `050-state_volume` | I | C | 11000 | `/Volume?db=2` | 200 | 9 | xml | `volume` | 142 | relative db=+2 |
| `051-state_volume` | I | C | 11000 | `/Volume` | 200 | 8 | xml | `volume` | 142 | read back after relative db |
| `052-state_volume` | I | C | 11000 | `/Volume?level=38` | 200 | 9 | xml | `volume` | 140 | RESTORE volume to 38 |
| `053-state_volume` | I | C | 11000 | `/Volume?mute=0` | 200 | 8 | xml | `volume` | 140 | RESTORE mute state |
| `054-state_volume` | O | | | *analysis* | | | | | | **C restore verified: yes** |
| `055-state_volume` | I | | | *analysis* | | | | | | **D starting volume 13, mute=0** |
| `056-state_volume` | I | D | 11000 | `/Volume?level=1` | 200 | 26 | xml | `volume` | 140 | set absolute level 1 |
| `057-state_volume` | I | D | 11000 | `/Volume` | 200 | 14 | xml | `volume` | 140 | read back after level=1 |
| `058-state_volume` | I | D | 11000 | `/Volume?level=5` | 200 | 23 | xml | `volume` | 140 | set absolute level 5 |
| `059-state_volume` | I | D | 11000 | `/Volume` | 200 | 12 | xml | `volume` | 140 | read back after level=5 |
| `060-state_volume` | I | D | 11000 | `/Volume?level=10` | 200 | 15 | xml | `volume` | 141 | set absolute level 10 |
| `061-state_volume` | I | D | 11000 | `/Volume` | 200 | 32 | xml | `volume` | 141 | read back after level=10 |
| `062-state_volume` | I | D | 11000 | `/Volume?mute=1` | 200 | 38 | xml | `volume` | 170 | mute=1 |
| `063-state_volume` | I | D | 11000 | `/Volume` | 200 | 11 | xml | `volume` | 170 | read back after mute=1 |
| `064-state_volume` | I | D | 11000 | `/Volume?mute=0` | 200 | 18 | xml | `volume` | 141 | mute=0 |
| `065-state_volume` | I | D | 11000 | `/Volume` | 200 | 18 | xml | `volume` | 141 | read back after mute=0 |
| `066-state_volume` | O | | | *analysis* | | | | | | **D mute polarity: mute=1 -> muted, mute=0 -> unmuted** |
| `067-state_volume` | I | D | 11000 | `/Volume?db=-2` | 200 | 26 | xml | `volume` | 140 | relative db=-2 |
| `068-state_volume` | I | D | 11000 | `/Volume?db=2` | 200 | 34 | xml | `volume` | 141 | relative db=+2 |
| `069-state_volume` | I | D | 11000 | `/Volume` | 200 | 11 | xml | `volume` | 141 | read back after relative db |
| `070-state_volume` | I | D | 11000 | `/Volume?level=13` | 200 | 13 | xml | `volume` | 141 | RESTORE volume to 13 |
| `071-state_volume` | I | D | 11000 | `/Volume?mute=0` | 200 | 13 | xml | `volume` | 141 | RESTORE mute state |
| `072-state_volume` | E | | | *analysis* | | | | | | **D restore verified: NO** |

### state_volume -- analysis detail

**A mute polarity: mute=1 -> muted, mute=0 -> unmuted** (`012-state_volume`)

```
confirms the app and contradicts CI API v1.7 3.1
```

**A restore verified: yes** (`018-state_volume`)

```
before level=46 mute=0 / after level=46 mute=0
```

**B mute polarity: mute=1 -> muted, mute=0 -> unmuted** (`030-state_volume`)

```
confirms the app and contradicts CI API v1.7 3.1
```

**B restore verified: yes** (`036-state_volume`)

```
before level=27 mute=0 / after level=27 mute=0
```

**C mute polarity: mute=1 -> muted, mute=0 -> unmuted** (`048-state_volume`)

```
confirms the app and contradicts CI API v1.7 3.1
```

**C restore verified: yes** (`054-state_volume`)

```
before level=38 mute=0 / after level=38 mute=0
```

**D mute polarity: mute=1 -> muted, mute=0 -> unmuted** (`066-state_volume`)

```
confirms the app and contradicts CI API v1.7 3.1
```

**D restore verified: NO** (`072-state_volume`)

```
before level=13 mute=0 / after level=10 mute=0
```

## Play-response root elements observed

Blu4Net reports four possible roots for a play-type response. Observed in this run: `loaded`, `state`. An HTTP 200 alone says nothing about which arrived, so this is collected from the bodies rather than from status codes.

## Bodies

Response bodies are in `raw/`, one file per probe id, alongside a
`.head.txt` with the status line and response headers. Binary
bodies (artwork) are not stored: only their length, content type
and first bytes are recorded here, so no embedded metadata can
leak. Their SHA-256 is in the do-not-share key file, not in this
bundle.
