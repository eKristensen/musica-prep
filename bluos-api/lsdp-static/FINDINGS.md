# Does better LSDP make the controller apps faster?

**No.** Discovery reliability improves; the time before players appear does not.

That is the result the tool was built to get, and it is worth writing down
plainly because it is the opposite of what a faster responder should have
produced. Notes below are from early testing on 2026-09-12, four players, three
VLANs on `ek-arm`, against the first-party BluOS Controller apps.

Confidence markers follow `bluos-http-api.md`: **[V hardware]** observed
directly here, **[U]** unverified, test first.

---

## What was measured

Two things, and keeping them apart is the whole point:

- **On the wire** — `lsdp-static measure`. How long until an announce carrying
  each player arrives. This is the protocol.
- **On screen** — stopping and restarting a controller app and watching for the
  player list to fill. This is what a user experiences.

The tool only measures the first. The apps were timed by hand.

## Results

### Android, two phones **[V hardware]**

Stopping and restarting the BluOS Controller repeatedly, back to back:

- **3–4 seconds** before all four players appear.
- All four appeared **9 times out of 10**.
- Rediscovery was "somewhat more stable with the relay running, but always
  slow".

The reliability is the good part: 9/10 complete, and the misses are one player
short rather than an empty list.

> The baseline that "more stable with the relay running" was compared against
> is not recorded — relay versus nothing, or relay versus the static responder.
> Worth settling before this line is quoted anywhere, because the two readings
> support opposite conclusions about whether the relay is still needed.

### Windows **[V hardware]**

**5–6 seconds**, unchanged. Retested after the static responder was in place;
no measurable difference.

### Linux **[V hardware]**

No measurable difference either, with the host firewall opened so the datagrams
could arrive.

Two caveats worth carrying:

- `bluos-http-api.md` surveys the **Android, Windows and macOS** controllers.
  Whatever Linux client this was is outside that survey, so its behaviour is not
  corroborated by anything in the specification.
- The suspicion is that it **still discovers over mDNS** rather than LSDP
  **[U]**. Untested — an answered LSDP query it ignores and an unanswered one it
  never sent look identical from the outside.

## What this means

The protocol's own cost is known, and it is not the problem:

| | time to all four players |
|---|---|
| measured on the wire, real players | ~640 ms median, ~730 ms p95 |
| the same, as predicted by a random 0–750 ms reply delay per player | ~630 ms median |
| measured on the wire, static responder answering immediately | ~0 ms |
| **Android app, on screen** | **3–4 s** |
| **Windows app, on screen** | **5–6 s** |

So between 3 and 6 seconds pass while the answers are already in hand — over
five seconds of it on Windows. Discovery is not what the user is waiting for.
Whatever the apps are doing (mDNS resolution round trips, the ten-second
Bonjour browser reset the desktop clients run, UI or session startup, a
deliberate settling delay), it is not waiting for LSDP, and making LSDP
instantaneous cannot shorten it.

**A faster responder cannot fix a slow client.** That is the finding, and it is
what justifies continuing with Musica: a controller that keeps its own player
list and does not rediscover on every launch is the only thing that removes
this wait.

## What this does not say

- It does not say the relay is unnecessary. Reliability did improve, and the
  ambiguity above means the relay's own contribution is still unquantified.
- It does not say the apps are badly built. 3–6 s to a usable list is a
  reasonable product decision when discovery is genuinely unreliable; it is
  only a problem for someone who wants a controller that is instant.
- It does not measure anything about **control** latency after discovery, which
  is a separate question and the one Musica actually lives in.

## Next tests, cheapest first

1. **`staticPlayers.txt`** (§12.3). The desktop controllers read a
   comma-separated list of player addresses from their user-data directory and
   use them **with no discovery at all**. If Windows still takes 5–6 s with that
   file in place, the delay is definitively not discovery — that single test
   would settle this whole question for the desktop apps.
2. **Settle the Android baseline.** Three runs of ten restarts — relay only,
   static responder only, neither — recorded the same way.
3. **Test the Linux mDNS hypothesis.** `avahi-browse -a` while the app starts,
   or block UDP 5353 and see whether it stops finding players. Either answers it
   in a minute.
4. **`--query R` at a real player** to settle claim `C-19`, which is unrelated
   to timing but is the other open question this tool can answer.
