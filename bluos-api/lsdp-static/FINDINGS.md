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

## 1.0–1.5 s is not a target to match

With the Android app's two-second delay out of the way, about a second remains,
and it is worth asking why that should be accepted either. Nothing requires it:
with a responder answering in microseconds the number does not move, so the
second is not the network, not the protocol and not the players. A list of
players a controller already knows should appear in the time it takes to draw
it.

## Two traps this work fell into

Kept because both are easy to fall into again.

**A warm app is not a measurement.** The Android app holds the whole player list
within a session and renders it instantly, so any run that does not force-close
the app first measures the cache. Every usable run swipes the app away between
attempts; one observation was discarded for exactly this reason.

**A plugged-in adapter is not a wired test.** Two runs were recorded as "wired"
with the Wi-Fi radio still enabled. That turned out to matter more than expected
— the app's delay keys on the radio being on, not on which interface carries
traffic — so the label was not just imprecise, it was measuring the wrong thing.

## What is left

The experiment is finished in both directions. One protocol question remains,
unrelated to any of the timings: whether a real player answers a unicast `R`
query, which would settle claim `C-19` in `../bluos-http-api.md`. The tool can
send one — `measure --query R` — and no shipping controller does.
