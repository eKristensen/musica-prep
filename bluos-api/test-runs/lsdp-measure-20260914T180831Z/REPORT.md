# LSDP discovery timing

How long a BluOS controller would wait to see every player, measured with
`lsdp-static` v1.0 `measure` on 2026-09-14T18:08:31.510Z.

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
| 1 | 4 | 305 | 613 | 4 |
| 2 | 4 | 437 | 675 | 4 |
| 3 | 4 | 164 | 555 | 4 |
| 4 | 4 | 55 | 447 | 4 |
| 5 | 4 | 560 | 593 | 4 |
| 6 | 4 | 99 | 525 | 4 |
| 7 | 4 | 55 | 523 | 4 |
| 8 | 4 | 77 | 489 | 4 |
| 9 | 4 | 545 | 743 | 4 |
| 10 | 4 | 154 | 722 | 4 |

## Spread

| | min | median | p95 | max |
|---|---:|---:|---:|---:|
| first player (ms) | 55 | 164 | 560 | 560 |
| all players (ms) | 447 | 593 | 743 | 743 |

Time until every expected player had answered:

```
      0-99    ms                                           0
    100-199   ms                                           0
    200-299   ms                                           0
    300-399   ms                                           0
    400-499   ms  ####################                     2
    500-599   ms  ######################################## 4
    600-699   ms  ####################                     2
    700-799   ms  ####################                     2
```

Time until the first player answered:

```
      0-49    ms                                           0
     50-99    ms  ######################################## 4
    100-149   ms                                           0
    150-199   ms  ####################                     2
    200-249   ms                                           0
    250-299   ms                                           0
    300-349   ms  ##########                               1
    350-399   ms                                           0
    400-449   ms  ##########                               1
    450-499   ms                                           0
    500-549   ms  ##########                               1
    550-599   ms  ##########                               1
```

## Per player

| player | rounds seen | min | median | p95 | max |
|---|---:|---:|---:|---:|---:|
| 192.0.2.11 [02000000000b] Room-A 0x0001+0x0004 | 10/10 | 77 | 447 | 656 | 656 |
| 192.0.2.12 [02000000000c] Room-B 0x0001+0x0004 | 10/10 | 58 | 447 | 743 | 743 |
| 192.0.2.13 [02000000000d] Room-C 0x0001+0x0004 | 10/10 | 164 | 523 | 722 | 722 |
| 192.0.2.14 [02000000000e] Room-D 0x0001+0x0004 | 10/10 | 55 | 501 | 627 | 627 |

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
