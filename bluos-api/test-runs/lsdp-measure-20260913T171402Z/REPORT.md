# LSDP discovery timing

How long a BluOS controller would wait to see every player, measured with
`lsdp-static` v1.0 `measure` on 2026-09-13T17:14:02.044Z.

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
| sent to | 192.0.2.11 |
| complete rounds | 0/20 |
| most players seen in one round | 0 |

## Note added by hand, 2026-09-14

This run was produced by `lsdp-static` v1.0, which did not record the port
replies were listened for on. That is the setting this run turns on, so it is
written down here rather than left to be inferred. The field is printed by the
tool from v1.2.0; nothing else in this file has been altered.

**Replies were listened for on an ephemeral port, chosen by the kernel (`--listen-port 0`).**

An `R` answer is unicast back to the port the query was sent from, so an answer
would have arrived there. **This run therefore cannot distinguish a player that
ignores the query from a reply dropped on the way back**, since a stateful
firewall that did not treat it as return traffic would look identical to
silence.

It is also why this run recorded zero datagrams of any kind, where runs
listening on 11430 pick up the occasional unsolicited announce: those are
broadcast to 11430 and never reach an ephemeral port.

The question was settled by re-running from 11430 —
`lsdp-measure-20260914T180935Z/` — which found the same silence with the
firewall explanation ruled out.

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
| 18 | 0 | 0 | 0 | 0 |
| 19 | 0 | 0 | 0 | 0 |
| 20 | 0 | 0 | 0 | 0 |

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

1 address(es), 0 node id(s) and 0 player name(s) were replaced.
Originals appear nowhere in this file; `lsdp-static measure --key` writes the
mapping to a separate file, which is not for sharing.
