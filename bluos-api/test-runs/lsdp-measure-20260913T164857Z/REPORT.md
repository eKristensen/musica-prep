# LSDP discovery timing

How long a BluOS controller would wait to see every player, measured with
`lsdp-static` v1.0 `measure` on 2026-09-13T16:48:57.219Z.

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
| round ends early at | 1 players |
| sent to | 192.0.2.11 |
| complete rounds | 6/10 |
| most players seen in one round | 1 |

## Rounds

| round | players | first (ms) | all (ms) | announce datagrams |
|---:|---:|---:|---:|---:|
| 1 | 1 | 11136 | 11136 | 1 |
| 2 | 1 | 2602 | 2602 | 1 |
| 3 | 0 | 0 | 0 | 0 |
| 4 | 0 | 0 | 0 | 0 |
| 5 | 1 | 11867 | 11867 | 1 |
| 6 | 1 | 10279 | 10279 | 1 |
| 7 | 1 | 1549 | 1549 | 1 |
| 8 | 1 | 886 | 886 | 1 |
| 9 | 0 | 0 | 0 | 0 |
| 10 | 0 | 0 | 0 | 0 |

## Spread

| | min | median | p95 | max |
|---|---:|---:|---:|---:|
| first player (ms) | 886 | 10279 | 11867 | 11867 |
| all players (ms) | 886 | 10279 | 11867 | 11867 |

Time until every expected player had answered:

```
      0-999   ms  ####################                     1
   1000-1999  ms  ####################                     1
   2000-2999  ms  ####################                     1
   3000-3999  ms                                           0
   4000-4999  ms                                           0
   5000-5999  ms                                           0
   6000-6999  ms                                           0
   7000-7999  ms                                           0
   8000-8999  ms                                           0
   9000-9999  ms                                           0
  10000-10999 ms  ####################                     1
  11000-11999 ms  ######################################## 2
```

Time until the first player answered:

```
      0-999   ms  ####################                     1
   1000-1999  ms  ####################                     1
   2000-2999  ms  ####################                     1
   3000-3999  ms                                           0
   4000-4999  ms                                           0
   5000-5999  ms                                           0
   6000-6999  ms                                           0
   7000-7999  ms                                           0
   8000-8999  ms                                           0
   9000-9999  ms                                           0
  10000-10999 ms  ####################                     1
  11000-11999 ms  ######################################## 2
```

## Per player

| player | rounds seen | min | median | p95 | max |
|---|---:|---:|---:|---:|---:|
| 192.0.2.11 [02000000000b] Room-A 0x0001+0x0004 | 2/10 | 886 | 11867 | 11867 | 11867 |
| 192.0.2.12 [02000000000c] Room-B 0x0001+0x0004 | 2/10 | 10279 | 11136 | 11136 | 11136 |
| 192.0.2.13 [02000000000d] Room-C 0x0001+0x0004 | 2/10 | 1549 | 2602 | 2602 | 2602 |

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

3 address(es), 3 node id(s) and 3 player name(s) were replaced.
Originals appear nowhere in this file; `lsdp-static measure --key` writes the
mapping to a separate file, which is not for sharing.
