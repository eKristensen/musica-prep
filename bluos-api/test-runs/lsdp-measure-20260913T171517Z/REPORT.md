# LSDP discovery timing

How long a BluOS controller would wait to see every player, measured with
`lsdp-static` v1.0 `measure` on 2026-09-13T17:15:17.883Z.

Addresses, node ids and player names are replaced with documentation
placeholders (RFC 5737 for addresses, a locally administered pool for node
ids), using the same scheme as `bluos-probe.py`. Placeholders are stable
within this run, so the same player is the same name in every line.

## Run

| setting | value |
|---|---|
| tool | `lsdp-static` v1.0 |
| rounds | 20 |
| query | `Q` for class 0xFFFF |
| query sent at | 0 s |
| listen timeout | 1 s |
| round ends early at | 1 players |
| sent to | 192.0.2.11 |
| complete rounds | 2/20 |
| most players seen in one round | 1 |

## Rounds

| round | players | first (ms) | all (ms) | announce datagrams |
|---:|---:|---:|---:|---:|
| 1 | 0 | 0 | 0 | 0 |
| 2 | 0 | 0 | 0 | 0 |
| 3 | 0 | 0 | 0 | 0 |
| 4 | 0 | 0 | 0 | 0 |
| 5 | 0 | 0 | 0 | 0 |
| 6 | 0 | 0 | 0 | 0 |
| 7 | 0 | 0 | 0 | 0 |
| 8 | 0 | 0 | 0 | 0 |
| 9 | 1 | 990 | 990 | 1 |
| 10 | 0 | 0 | 0 | 0 |
| 11 | 1 | 5 | 5 | 1 |
| 12 | 0 | 0 | 0 | 0 |
| 13 | 0 | 0 | 0 | 0 |
| 14 | 0 | 0 | 0 | 0 |
| 15 | 0 | 0 | 0 | 0 |
| 16 | 0 | 0 | 0 | 0 |
| 17 | 0 | 0 | 0 | 0 |
| 18 | 0 | 0 | 0 | 0 |
| 19 | 0 | 0 | 0 | 0 |
| 20 | 0 | 0 | 0 | 0 |

## Spread

| | min | median | p95 | max |
|---|---:|---:|---:|---:|
| first player (ms) | 5 | 990 | 990 | 990 |
| all players (ms) | 5 | 990 | 990 | 990 |

Time until every expected player had answered:

```
      0-99    ms  ######################################## 1
    100-199   ms                                           0
    200-299   ms                                           0
    300-399   ms                                           0
    400-499   ms                                           0
    500-599   ms                                           0
    600-699   ms                                           0
    700-799   ms                                           0
    800-899   ms                                           0
    900-999   ms  ######################################## 1
```

Time until the first player answered:

```
      0-99    ms  ######################################## 1
    100-199   ms                                           0
    200-299   ms                                           0
    300-399   ms                                           0
    400-499   ms                                           0
    500-599   ms                                           0
    600-699   ms                                           0
    700-799   ms                                           0
    800-899   ms                                           0
    900-999   ms  ######################################## 1
```

## Per player

| player | rounds seen | min | median | p95 | max |
|---|---:|---:|---:|---:|---:|
| 192.0.2.11 [02000000000b] Room-A 0x0001+0x0004 | 1/20 | 5 | 5 | 5 | 5 |
| 192.0.2.12 [02000000000c] Room-B 0x0001+0x0004 | 1/20 | 990 | 990 | 990 | 990 |

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

2 address(es), 2 node id(s) and 2 player name(s) were replaced.
Originals appear nowhere in this file; `lsdp-static measure --key` writes the
mapping to a separate file, which is not for sharing.
