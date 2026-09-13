# LSDP discovery timing

How long a BluOS controller would wait to see every player, measured with
`lsdp-static` v1.0 `measure` on 2026-09-13T17:12:49.630Z.

Addresses, node ids and player names are replaced with documentation
placeholders (RFC 5737 for addresses, a locally administered pool for node
ids), using the same scheme as `bluos-probe.py`. Placeholders are stable
within this run, so the same player is the same name in every line.

## Run

| setting | value |
|---|---|
| tool | `lsdp-static` v1.0 |
| rounds | 10 |
| query | `Q` for class 0xFFFF |
| query sent at | 0, 1, 2, 3, 5, 7, 10 s |
| listen timeout | 12 s |
| round ends early at | 4 players |
| sent to | 192.0.2.15, 192.0.2.16, 192.0.2.17, 192.0.2.18, 192.0.2.19, 192.0.2.20, 192.0.2.21 |
| complete rounds | 10/10 |
| most players seen in one round | 4 |

## Rounds

| round | players | first (ms) | all (ms) | announce datagrams |
|---:|---:|---:|---:|---:|
| 1 | 4 | 97 | 228 | 4 |
| 2 | 4 | 21 | 607 | 4 |
| 3 | 4 | 186 | 746 | 4 |
| 4 | 4 | 48 | 567 | 4 |
| 5 | 4 | 151 | 430 | 4 |
| 6 | 4 | 286 | 635 | 4 |
| 7 | 4 | 195 | 486 | 4 |
| 8 | 4 | 214 | 410 | 4 |
| 9 | 4 | 17 | 528 | 4 |
| 10 | 4 | 169 | 560 | 4 |

## Spread

| | min | median | p95 | max |
|---|---:|---:|---:|---:|
| first player (ms) | 17 | 169 | 286 | 286 |
| all players (ms) | 228 | 560 | 746 | 746 |

Time until every expected player had answered:

```
      0-99    ms                                           0
    100-199   ms                                           0
    200-299   ms  ##############                           1
    300-399   ms                                           0
    400-499   ms  ######################################## 3
    500-599   ms  ######################################## 3
    600-699   ms  ###########################              2
    700-799   ms  ##############                           1
```

Time until the first player answered:

```
      0-24    ms  ######################################## 2
     25-49    ms  ####################                     1
     50-74    ms                                           0
     75-99    ms  ####################                     1
    100-124   ms                                           0
    125-149   ms                                           0
    150-174   ms  ######################################## 2
    175-199   ms  ######################################## 2
    200-224   ms  ####################                     1
    225-249   ms                                           0
    250-274   ms                                           0
    275-299   ms  ####################                     1
```

## Per player

| player | rounds seen | min | median | p95 | max |
|---|---:|---:|---:|---:|---:|
| 192.0.2.11 [02000000000b] Room-A 0x0001+0x0004 | 10/10 | 119 | 337 | 607 | 607 |
| 192.0.2.12 [02000000000c] Room-B 0x0001+0x0004 | 10/10 | 17 | 357 | 635 | 635 |
| 192.0.2.13 [02000000000d] Room-C 0x0001+0x0004 | 10/10 | 76 | 195 | 746 | 746 |
| 192.0.2.14 [02000000000e] Room-D 0x0001+0x0004 | 10/10 | 48 | 293 | 560 | 560 |

All times in milliseconds. Every individual sighting is in
`observations.csv` next to this file, and every round in `rounds.csv`,
so none of this has to be taken on trust or recomputed by hand.

## Reading these numbers

From `bluos-http-api.md` section 12.1, for context rather than as a
conclusion:

- a player delays its answer to a query by a **random 0-750 ms**, so a
  spread up to about 750 ms is the protocol working as specified, not
  the network struggling;
- controllers send the query **seven times**, at t = 0, 1, 2, 3, 5, 7
  and 10 s, because UDP is lossy -- a first-answer time above one
  second means a query or an answer was lost, not that a player was
  slow;
- a player also announces unprompted every **57 s +/- 6 s**, which is
  the fallback when every query in a burst is lost.

## Redaction

11 address(es), 4 node id(s) and 4 player name(s) were replaced.
Originals appear nowhere in this file; `lsdp-static measure --key` writes the
mapping to a separate file, which is not for sharing.
