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

## What is left

The experiment is finished in both directions. One protocol question remains,
unrelated to any of the timings: whether a real player answers a unicast `R`
query, which would settle claim `C-19` in `../bluos-http-api.md`. No shipping
controller sends one.

**One attempt has been made and it did not settle the claim**
([`../test-runs/lsdp-measure-20260913T164700Z/`](../test-runs/lsdp-measure-20260913T164700Z/)
and the two runs either side of it). A unicast `R` at a single player drew
**nothing at all** — 10 rounds, 70 query sends, zero datagrams. That is the
result the claim is about, but on its own it cannot distinguish "`R` is not
answered" from "the query never got through", and the run meant to control for
that could not do the job: a `Q` is answered by **broadcast**, which is
indistinguishable from a player's unsolicited 57 s announce arriving in the same
12 s window. Its six sightings were four different players — four of them not
even the one addressed — and their number matches what background announces
alone predict.

A second problem is visible in the broadcast-`Q` control from the same session:
every player answered in **0–2 ms**, where the identical command a day earlier
([`../test-runs/lsdp-measure-20260912T185206Z/`](../test-runs/lsdp-measure-20260912T185206Z/))
produced the expected 8–749 ms spread. Something was answering instantly, which
is what `serve` is for, so it is not established that the real players were the
ones replying during that session at all.

What would settle it, with nothing else on the network answering: a **single**
query and a **one-second** window, so background announces cannot be mistaken
for a reply — `--schedule 0 --timeout 1 --rounds 20`, once with `--query R
--listen-port 0` and once with `--query Q`, both `--to` one player. A real
answer hits nearly every round and comes from the addressed player; background
noise hits about one round in fourteen and comes from anyone.
