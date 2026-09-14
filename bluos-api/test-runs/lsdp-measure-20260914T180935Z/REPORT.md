# LSDP discovery timing

How long a BluOS controller would wait to see every player, measured with
`lsdp-static` v1.0 `measure` on 2026-09-14T18:09:35.982Z.

Addresses, node ids and player names are replaced with documentation
placeholders (RFC 5737 for addresses, a locally administered pool for node
ids), using the same scheme as `bluos-probe.py`. Placeholders are stable
within this run, so the same player is the same name in every line.

## Run

| setting | value |
|---|---|
| tool | `lsdp-static` v1.0 |
| rounds | 20 |
| query | `R` for class 0xFFFF |
| query sent at | 0 s |
| listen timeout | 1 s |
| round ends early at | 1 players |
| sent to | 192.0.2.13 |
| complete rounds | 2/20 |
| most players seen in one round | 1 |

## Note added by hand, 2026-09-14

This run was produced by `lsdp-static` v1.0, which did not record the port
replies were listened for on. That is the setting this run turns on, so it is
written down here rather than left to be inferred. The field is printed by the
tool from v1.2.0; nothing else in this file has been altered.

**Replies were listened for on UDP 11430.**

An `R` answer is unicast back to the port the query was sent from, so that is
where an answer from `192.0.2.13` would have arrived. 11430 is also the port the
broadcast control run minutes earlier was answered on, so it is known to have
been open and reachable at the time.

The two datagrams below corroborate it independently: both are broadcast
announces from *other* players, and a broadcast to 11430 cannot be delivered to
a socket bound to an ephemeral port. The socket was on 11430, and the player
addressed still never answered.

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
| 9 | 0 | 0 | 0 | 0 |
| 10 | 0 | 0 | 0 | 0 |
| 11 | 0 | 0 | 0 | 0 |
| 12 | 0 | 0 | 0 | 0 |
| 13 | 0 | 0 | 0 | 0 |
| 14 | 0 | 0 | 0 | 0 |
| 15 | 0 | 0 | 0 | 0 |
| 16 | 0 | 0 | 0 | 0 |
| 17 | 0 | 0 | 0 | 0 |
| 18 | 1 | 455 | 455 | 1 |
| 19 | 1 | 153 | 153 | 1 |
| 20 | 0 | 0 | 0 | 0 |

## Spread

| | min | median | p95 | max |
|---|---:|---:|---:|---:|
| first player (ms) | 153 | 455 | 455 | 455 |
| all players (ms) | 153 | 455 | 455 | 455 |

Time until every expected player had answered:

```
      0-49    ms                                           0
     50-99    ms                                           0
    100-149   ms                                           0
    150-199   ms  ######################################## 1
    200-249   ms                                           0
    250-299   ms                                           0
    300-349   ms                                           0
    350-399   ms                                           0
    400-449   ms                                           0
    450-499   ms  ######################################## 1
```

Time until the first player answered:

```
      0-49    ms                                           0
     50-99    ms                                           0
    100-149   ms                                           0
    150-199   ms  ######################################## 1
    200-249   ms                                           0
    250-299   ms                                           0
    300-349   ms                                           0
    350-399   ms                                           0
    400-449   ms                                           0
    450-499   ms  ######################################## 1
```

## Per player

| player | rounds seen | min | median | p95 | max |
|---|---:|---:|---:|---:|---:|
| 192.0.2.11 [02000000000b] Room-A 0x0001+0x0004 | 1/20 | 153 | 153 | 153 | 153 |
| 192.0.2.12 [02000000000c] Room-B 0x0001+0x0004 | 1/20 | 455 | 455 | 455 | 455 |

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

3 address(es), 2 node id(s) and 2 player name(s) were replaced.
Originals appear nowhere in this file; `lsdp-static measure --key` writes the
mapping to a separate file, which is not for sharing.
