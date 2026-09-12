# Does better LSDP make the controller apps faster?

**No — and the reason has changed twice as the data came in.**

Making LSDP answer instantly does not shorten the wait in any controller app.
What it changes is *how* the players arrive: together, rather than one or two at
a time. But the wait itself turned out not to be the protocol's, and — as of the
latest round — probably not the app's either. It looks like the **link**.

All the numbers are in
[`../controller-discovery-timings.md`](../controller-discovery-timings.md),
which is the data; this file is the reasoning over it. Confidence markers follow
`bluos-http-api.md`: **[V hardware]** observed directly here, **[V]** verified
in client code or a vendor document, **[U]** unverified — a claim about
behaviour nobody has tested yet.

---

## What the experiment was

`lsdp-static serve` answers LSDP queries instantly from a static player list,
where a real player waits a random 0–750 ms and a UDP broadcast relay adds loss
and delay on top. If discovery were the bottleneck, removing it entirely should
have been visible on screen.

It was not. The Android app still took 3–5 s over Wi-Fi, and Windows and Linux
still took 5–6 s from launch, with or without the responder.

## What actually moves the number

| link | time for the remaining players | complete runs |
|---|---|---|
| **Android, Wi-Fi** | 3–5 s | about 4 in 5 |
| **Android, wired, no Wi-Fi in the path** | **1–1.5 s** | **every run, three devices** |
| Android, wired, **and** a responder answering instantly | **1–1.5 s, unchanged** | every run |
| **iOS, Wi-Fi or wired** | **instant** (not timed) | **every run** |

That is not a small finding. The same app, the same players, the same second —
a different link, and discovery stops being a problem.

The wired number now rests on three devices: both phones with Wi-Fi explicitly
disabled, and a bridged Waydroid guest. That third one carries weight out of
proportion to being one more run, because it differs in everything except the
link — LineageOS rather than a vendor Android, **no Google Play services**, a
different app build (4.16.3 against whatever the Play Store gave the phones),
and virtualised hardware. None of it moved the number. The fast result is not a
property of one phone, one Android, one app version, or real hardware.

Two earlier runs were recorded as "wired" and are now suspect: an adapter was
plugged in but Wi-Fi was never turned off, and nothing confirmed which interface
the app used. Until that is redone, treat them as Wi-Fi measurements.

### Where the penalty lives **[V hardware]**, and what causes it **[U]**

Broadcast delivery over Wi-Fi to the controller is the weak point, and it is
**an Android-side weakness, not the network's**. The same house, the same
players and the same access point serve an iPhone with no delay and no
"Discovering…" stage at all, on Wi-Fi exactly as on a cable. That removes the
network, the access point, and Wi-Fi as such from the list of suspects.

That much is a result, not a hypothesis: the iPhone and the Mi 9 sit on the same
Wi-Fi, the same access point and the same players, one variable differs, and the
outcome flips. And on the iPhone it holds however many times the app is
restarted, so it is not a warm cache either.

What is still open is *which* Android-side cause: Android's own broadcast
handling, the app's Android code, or the vendor Wi-Fi stack. One suspect is
specific enough to name — Android filters multicast and broadcast not addressed
to the device while the Wi-Fi radio is in power save, unless an app holds a
`WifiManager.MulticastLock`, and iOS has no equivalent requirement. That one
difference would produce precisely this pattern, and telling it apart from the
alternatives takes any Bonjour browser app on the same phone and the same
Wi-Fi **[U]**.

Everything else that could plausibly have explained the slow runs has now been
varied without effect.

This is a hypothesis, not a measurement. It is worth stating because it is
cheap to test and because it points somewhere useful: **the protocol already has
a unicast path.** An `R` query (§12.1) asks responders to answer by unicast
instead of broadcast, which sidesteps Wi-Fi broadcast handling entirely. No
shipping client sends one. `lsdp-static serve` answers them, and Musica could
send them.

**The cause being open does not make the effect open.** Whether the penalty
lives in the app, in Android's Wi-Fi stack, or in the access point is unsettled
and may stay that way — but the observable fact needs none of that resolved:
**used over Wi-Fi, the BluOS Controller is much worse than over a cable**, in
both speed and reliability. Nor is the cause this project's to chase. The
same BluOS app on an iPhone, on the same network, does not have the problem at
all; and a Sonos system in the family does not behave this way either. Neither
is measured here, but together they settle that the experience is achievable on
this kind of home network — the BluOS app itself achieves it, just not on
Android.
Solving it inside somebody else's app or inside Android is not a thing Musica is
expected to do. What Musica can do is not depend on the part that fails.

## What the static responder did change

Players arrive **together** instead of one or two at a time, and the relay's
unreliability is gone. A phone on another VLAN behaves like one on the players'
own segment.

That is a real improvement in how the list fills. It is not an improvement in
when it is complete.

## Desktop: Windows and Linux **[V hardware]**

**5–6 s from launch, unchanged**, with the static responder in place and the
firewall opened.

The two are one result. The Linux client repackages the **official Windows
installer's** Electron app, version **4.16.0** — the exact build
`bluos-http-api.md` was written from. Same code, two operating systems, same
number, which is corroboration rather than coincidence.

Both were on wired LAN throughout, so the Wi-Fi comparison above has never been
run against them.

**And that 5–6 s is not discovery either.** `staticPlayers.txt` makes the
desktop builds use a configured address list and skip discovery entirely
(§12.3). With it in place and mDNS and LSDP both switched off, only the listed
players appeared — so the file took effect — and startup was no faster. Removing
discovery outright did not move the number. The desktop is at least stable once
up: none of the list-emptying seen on Android.

## Corrections this file has been through

Recorded rather than quietly edited, because the wrong version was acted on for
a while each time.

1. **The trickle is not the players' 0–750 ms reply delay.** 750 ms is far
   inside the wait, so it cannot produce a visible trickle. The trickle was the
   UDP broadcast relay pushing datagrams past the app's render.
2. **The instantly-shown player is not fast discovery.** It is not discovery at
   all: the app's shutdown cache clear leaves the currently selected player
   alone, so it is restored from storage. An earlier draft also claimed this
   proved the network was fine at t ≈ 0 — it proves nothing of the kind.
3. **"Nothing about the network path changes the answer" was wrong.** It held
   across three configurations that now all look like Wi-Fi. A cable with Wi-Fi
   genuinely off takes about a second.

Correction 3 undermines the inference that the app holds results it already has
for several seconds. Over a cable it does not. That inference is withdrawn
pending the measurement below.

That inference is now **partly restored, at a smaller size**. Running
`lsdp-static serve` against the wired Waydroid guest — answers available in
milliseconds — did not move its 1.0–1.5 s at all. So there *is* an app-side
floor; it is about a second rather than about four.

## Where the 0–750 ms comes from, and why it exists

The figure is quoted often enough in these notes to be worth sourcing.

**Provenance: unknown, and this file should not pretend otherwise.** The only
place the figure appears in this repository is `../bluos-http-api.md` §12.1
under "Timing", in a section marked **[V]**, alongside the 57 s ± 6 s announce
cycle and the announce-timer reset rule. `bluos-probe.py` calls it "the
documented 0–750 ms response", pointing back at the same claim. No vendor
document is in this repository at all, so nothing here traces the number to a
primary source — **[V]** in §12.1 covers client code, the vendor spec and
hardware without saying which applied, and the sources table's only vendor spec
is the *BluOS Custom Integration API* v1.7 (09/04/2025), which nothing states
covers LSDP.

Whoever wrote §12.1 knows where it came from; this file does not. Worth pinning
down, because it is the number every measurement here is checked against.

**The value itself is independently supported**, whatever its paper source: 20
rounds against four players gave a pooled mean of 390 ms and a median of 393
against the 375/375 a uniform 0–750 ms draw predicts, a largest observation of
749 ms, and all four players drawing from the same distribution
([`../test-runs/lsdp-measure-20260912T185206Z/`](../test-runs/lsdp-measure-20260912T185206Z/))
**[V hardware]**.

**Why a player waits at all** is not stated anywhere in the repository, so what
follows is inference **[U]**. A broadcast query reaches every node at once. If
they all answered immediately they would transmit simultaneously on a shared
medium, which on consumer Wi-Fi means collisions, retries and lost answers —
the precise failure the protocol exists to avoid, since LSDP was built because
multicast discovery was unreliable enough to generate product returns (§12).
Spreading the answers randomly across a window fixes that, and the same
technique is standard elsewhere: mDNS requires a randomised 20–120 ms delay
before responding, for the same reason.

The size of the window is the interesting part. 750 ms is roughly six times
mDNS's, which looks generous until it is set against the documented system
limit of **64 players**: 64 answers spread over 750 ms average about 12 ms
apart, which is a sensible spacing for small datagrams on a busy wireless
network. The number reads like it was chosen for a full-sized system, and a
four-player house pays the same price for a spread it does not need.

## The wait, decomposed

Three rounds of measurement now separate cleanly:

| cost | size | what removes it |
|---|---|---|
| the app's own floor | **1.0–1.5 s** | nothing on the network side |
| Wi-Fi, on top of that | **+2 to 4 s**, and one run in five incomplete | a cable |
| the LSDP protocol itself | none of it — it finishes inside the floor | — |

The last row is the answer to the question this experiment was built to ask. The
protocol was never the problem, which is why making it instant changed nothing
anyone can see.

One thing this does *not* say: **a player being on Wi-Fi is fine.** In 20 rounds
against the real players, the one on Wi-Fi answered with a mean of 373 ms against
a theoretical 375, faster than two of the three on cable. It is Wi-Fi between the
*controller* and the network that costs 2–4 seconds, not Wi-Fi at the player.

## Reliability has a second dimension

"Does the list fill" is not the only question. The Android app also **empties
its own list** after roughly 30–50 seconds sitting idle — showing "Discovering…"
and then "No Player Found" — and refills it in under a second when tapped. That
happens with every discovery mechanism switched off, and while the previously
selected player stays fully controllable. It is written up in
[`../controller-discovery-timings.md`](../controller-discovery-timings.md).

Two things follow. A slow list fills eventually, but a list that empties itself
mid-session is a failure the user meets with no cause visible and nothing to do
but tap again — so it may matter more than any of the timings here. And the app
demonstrably holds the whole list well enough to render it instantly on demand,
then discards it on a timer anyway.

## Static LSDP is not the answer either, for a reason the timings do not show

Even if it had been fast, a static player list is the wrong shape of solution,
and reading `players.conf` is enough to see why: **it goes stale, and it goes
stale silently.**

An announce carries the player's address, port, name, model and firmware
version. Every one of those is a copy of something that lives somewhere else,
kept in step by hand. A firmware update, a renamed room, a player added or
sold, a DHCP lease that moves — each one leaves the file describing a network
that no longer exists, with nothing to notice it. Some of that is cosmetic,
because a controller reads the truth from `/SyncStatus` and the announce only
ever yields an address and a port (§12). The address is not cosmetic: announce a
player at an address it has moved from and the controller shows an entry it
cannot reach.

**And the stale copy wins.** The real players are still answering the same
queries under the same node ids, after their random 0–750 ms. The static
responder answers in microseconds, so it arrives first, every time. The better
it performs, the more reliably its stale data beats the fresh data sitting right
behind it. A responder that was merely as fast as a real player would at least
lose the race sometimes.

So the experiment's own tool carries an argument against the approach it was
built to test: a fast static answer is a fast wrong answer the moment anything
changes, and nothing in the protocol will tell you it has.

## 1.0–1.5 s is not a target to match

The wired figure is the best case anyone gets from the BluOS app, and it is
worth asking why it should be accepted at all. **Nothing requires it.** R8
settles that: with a responder answering in microseconds, the number does not
move, so the second is not the network, not the protocol, and not the players.
It is overhead, and there is no technical account of what it buys.

A list of players the controller already knows should appear in the time it
takes to draw it. The right target is not "as good as the app on a cable" — it
is **no wait at all**, with the network touched only to confirm what is already
on screen.

## What this means for Musica

The justification is intact, and the reason for it is sharper.

A phone is on Wi-Fi in real life. Over Wi-Fi, discovery costs 3–5 seconds and
fails to complete about one run in five, and nothing done to the network side —
a relay, a static responder answering in microseconds — changed either number.
Broadcast discovery on Wi-Fi is simply not dependable. On a cable it costs
1.0–1.5 s instead, which is better and still more than a list the app already
holds should ever cost.

A controller that keeps its own player list does not discover at all on the path
that matters, so none of this applies to it. The BluOS app already does exactly
that for one player, the selected one, which survives its shutdown cache clear —
and, within a session, for the whole list, which it then throws away on a timer.
**Musica's design target is to do that for every player and keep it** — and,
where discovery is unavoidable, to prefer the unicast `R` query over broadcast.

## The measurements that would close this

1. **A Bonjour browser app on the Fairphone over the same Wi-Fi**, which
   separates "the Android app" from "Android" as the cause of the Wi-Fi penalty.
   Minutes of work, and it is the last question about the cause that is still
   open.
2. **`--query R` against a real player**, which would settle claim `C-19` and, if
   the Wi-Fi hypothesis holds, demonstrate the protocol-level way around it.

Everything else that was on this list has been answered — including
`staticPlayers.txt`, which showed the desktop delay is not discovery. `sniff`
remains useful for one optional question, whether the app's floor is spent
before or after it sends its query, and for confirming which interface a phone
used, which is all that still separates the two suspect runs from the rest.

### Where `staticPlayers.txt` lives, and what it is actually for

Documented by **Bluesound Professional** for the remote-subnet case, and
independently **[V]** in the client code (§12.3). **It does not make startup
faster** — that was tested, see above — and the vendor scopes it narrowly:
**Windows and macOS only**, and explicitly not for grouping players or grouping
across subnets. It is a professional-install feature for reaching players the
network hides, not a performance setting, and it is unavailable on Android where
the problem actually is.

| platform | path |
|---|---|
| Windows | `C:\Users\<you>\AppData\Roaming\BluOS Controller\staticPlayers.txt` |
| macOS | `~/Library/Application Support/BluOS Controller/staticPlayers.txt` — supported by the vendor, exact path inferred from Electron's conventions **[U]** |
| Linux AppImage | `~/.config/BluOS Controller/staticPlayers.txt` — not supported by the vendor at all, and untested **[U]** |

One comma-separated line of `ip:port`, no spaces:

```
192.168.0.1:11000,192.168.0.2:11000,192.168.0.3:11000
```

The vendor's own example is one address with four ports —
`<ip>:11000,:11010,:11020,:11030` — which is a **four-zone chassis**, not four
players. The specification agrees: LSDP class 0x0003 is "BluOS Player, secondary
node in a multi-zone chassis (e.g. CI580)", and §12.2 notes the SRV port is how
a CI580's four nodes are told apart on one address. Players listed here are used
directly, **with no discovery at all** — which is exactly what made it a useful
test even though it is useless as a fix.

Sources: [How to Discover and Control Players from a Remote
Subnet](https://support.bluesoundprofessional.com/hc/en-us/articles/360060411413-How-to-Discover-and-Control-Players-from-a-Remote-Subnet)
(Bluesound Professional) · [`bluos-controller-linux`
README](https://gitlab.com/zquestz/bluos-controller-linux/-/raw/main/README.md)
