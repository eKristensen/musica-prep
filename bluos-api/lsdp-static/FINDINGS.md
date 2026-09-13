# Did a static LSDP responder help?

**No.** `lsdp-static` answers discovery queries instantly, which is as fast as
the protocol can possibly go, and no controller app showed players any sooner
for it. It is also, on reflection, the wrong shape of solution even where it
does work.

This file is the verdict on the experiment. The numbers are in
[`../controller-discovery-timings.md`](../controller-discovery-timings.md) and
the causes, read out of the apps themselves, are in
[`../controller-code-notes.md`](../controller-code-notes.md). Nothing is
repeated here that lives in either.

---

## What the experiment was

A real player answers a query after a random 0–750 ms (`../bluos-http-api.md`
§12.1), and a UDP broadcast relay adds loss and delay on top. `serve` removes
both: answers go out in microseconds, from a list that cannot be wrong about
who exists. If discovery were what made players slow to appear, that should have
been visible on screen.

It was not, on any of the three controllers tested. The Android app's wait turned
out to be a fixed delay in its own code, and the desktop's is not in discovery
at all.

## What it did change

Players arrive **together** rather than one or two at a time, and the
`udp-broadcast-relay-redux` setup's unreliability goes with it. A phone on
another VLAN ends up in the same position as one on the players' own segment.

That is a real improvement in how the list fills. It is not an improvement in
when the list is complete, which is what a user waits for.

## Why it would be the wrong answer anyway

Even a responder that *had* been fast enough is the wrong shape, and reading
`players.conf` is enough to see why: **it goes stale, and it goes stale
silently.**

Every field in the file — address, port, name, model, firmware version — is a
hand-kept copy of something that lives on a player. A firmware update, a renamed
room, a player added or sold, a DHCP lease that moves: each leaves the file
describing a network that no longer exists, with nothing to notice. Most of that
is cosmetic, because a controller reads the truth from `/SyncStatus` and an
announce only ever yields an address and a port (§12). The address is not
cosmetic — announce a player where it no longer is and the controller shows an
entry it cannot reach.

**And the stale copy wins the race.** The real players answer the same queries
under the same node ids after their random 0–750 ms. This responder answers in
microseconds, so it arrives first, every time. The better it performs, the more
reliably its stale data beats the fresh data right behind it. A responder merely
as fast as a real player would at least lose sometimes.

So the tool built to test the approach carries the argument against it: a fast
static answer is a fast wrong answer the moment anything changes, and the
protocol will not tell you it has.

## `C-19`: a unicast query is not answered **[V hardware]**

`../bluos-http-api.md` §12.4 proposes sending an `R` query **unicast** to a
known player address as a way to reach players across a subnet boundary, where
broadcast cannot go. It does not work, and neither does the `Q` form.

Three runs, one session, nothing else on the network answering:

| run | query | sent to | rounds | answered |
|---|---|---|---|---|
| [`…171249Z`](../test-runs/lsdp-measure-20260913T171249Z/) | `Q` broadcast | the interfaces' broadcast addresses | 10 | **10/10, all four players**, 21–746 ms |
| [`…171402Z`](../test-runs/lsdp-measure-20260913T171402Z/) | **`R` unicast** | one player | 20 | **0/20 — not one datagram** |
| [`…171517Z`](../test-runs/lsdp-measure-20260913T171517Z/) | **`Q` unicast** | the same player | 20 | 2/20, and both explained by background |

The first run is what makes the other two mean anything: the same players, minutes
earlier, answering every broadcast query with the full 0–750 ms spread §12.1
describes. They were awake, reachable and replying normally.

Each unicast round sent **one** query and listened for **one second**, so an
unsolicited announce — every 57 s per player, about a 7 % chance of landing in
any given window — cannot be mistaken for a reply. Across 20 rounds that
predicts ~1.4 stray sightings. The `Q` run produced 2: one from a player that
was not the one addressed, and so cannot be a reply to it at all, and one from
the addressed player. Neither carries the 0–750 ms answer delay, and a run where
the query were being answered would have hit nearly every round, not one.

So **`C-19` is refuted**: an `R` query sent by unicast is not answered. The
sharper finding is the one the control adds — the failure is not in the `R`
form, because `Q` fares no better. **Players act on queries that arrive by
broadcast, and ignore queries addressed to them directly.**

That closes the cross-subnet question §12.4 left open. Of the two ideas it
offered, this was the one that needed no cooperation from the network; it is
gone, and what remains is forwarding broadcasts (which is what
`udp-broadcast-relay-redux` does here) or a configured address list plus
`/SyncStatus`, which is what the vendor's own desktop clients fall back to.

One alternative explanation is not fully excluded **[U]**: the `R` reply is
unicast to the port the query was sent from, and that run used an ephemeral one,
so a stateful firewall that did not treat it as return traffic would look
identical to silence. The `Q` run does not share the doubt — its answers would
arrive by broadcast on 11430, the port the positive control had just proved open
— and it is the run the conclusion rests on. Re-running `R` with
`--listen-port 11430` would settle even that.
