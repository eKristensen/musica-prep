# Controller discovery timings

How long a BluOS controller takes to show every player, measured on real
devices. **This file is the data.** The interpretation lives in
[`lsdp-static/FINDINGS.md`](lsdp-static/FINDINGS.md); keeping them apart means a
later correction to the reasoning does not quietly rewrite the observations.

Four players. Three VLANs on `ek-arm`, which previously ran
`udp-broadcast-relay-redux` on UDP 11430 and during these tests sometimes ran
`lsdp-static serve` instead. One player is on Wi-Fi; the rest are wired.

Confidence markers follow `bluos-http-api.md`: **[V hardware]** observed
directly, **[U]** unverified.

---

## Devices

| | |
|---|---|
| **Fairphone 5 Plus** | Android 15, build `FP5.VT31.C.114.20260804`. App from Play Store, version not recorded **[U]** |
| **Xiaomi Mi 9** | MIUI Global 12.5.1, Android 11, `RKQ1.200826.002`. App from Play Store, version not recorded **[U]** |
| **Waydroid** | LineageOS-based Waydroid image (exact version not recorded **[U]**), minimal Android with **no Google Play**. App **4.16.3**, APK from APKMirror. Bridged to the host's network, with its own address on the players' VLAN |
| **Windows** | BluOS Controller 4.16.0 (Electron) |
| **Linux** | [`bluos-controller-linux`](https://gitlab.com/zquestz/bluos-controller-linux) — the same official 4.16.0 Electron app, repackaged as an AppImage |

USB Ethernet on the phones is a wired adapter; "Wi-Fi" means the phone's own
radio. The Waydroid guest is wired throughout — a host bridge, no radio anywhere
in its path.

## Method

**Android**, one run:

1. Open the BluOS app.
2. Wait for the menu bar.
3. Tap the player icon — **timer starts**.
4. Stop when all four players are listed.
5. Open the app drawer, **swipe the app away**, start again.

Step 5 kills the process, so every run is a cold start. The currently selected
player survives it: the app's shutdown cache clear does not clear that one, so
it is restored rather than discovered.

**This method cannot measure first-player discovery.** The player icon only
works once at least one player exists, and the restored player guarantees that.
Every Android number below is therefore *the time for the remaining players to
appear*, never a time from an empty list.

**Desktop**: from launching the app to players listed, which includes app
startup — on the desktop the app stays running, so discovery happens once.

Timing is noted per run: **counted** means counted in the head, worth about
±1 s; **timer** means an actual stopwatch.

---

## Runs

All on 2026-09-12, in the order given.

| # | device | link | discovery path | timing | time to all players | complete |
|---|---|---|---|---|---|---|
| R1 | one Android phone [U: which] | Wi-Fi | `lsdp-static serve`, different VLAN | counted | 3–4 s | 9 of 10 |
| R2 | the other Android phone | Wi-Fi | players directly, same VLAN | counted | no difference from R1 | — |
| R3 | both phones | USB Ethernet — **but see the note** | players directly, same layer 2 | counted | 3–5 s | 4 of 5 |
| R4 | Fairphone 5 Plus | airplane mode + USB Ethernet | players directly | **timer** | **2.9–3.4 s** | 4 of 5 |
| R5 | Xiaomi Mi 9 | airplane mode + USB Ethernet | — | — | **Ethernet did not work at all**, no discovery | none |
| R6 | **both phones** | **Wi-Fi disabled** + USB Ethernet | players directly | **timer** | **≈1 s, a little above** | **always, every run, both devices** |
| R7 | **Waydroid** (LineageOS, no Google Play, app 4.16.3) | **bridged, wired**, own IP on the players' VLAN | players directly | **timer** | **1.0–1.5 s** | **always, however many times tried** |
| R8 | **Waydroid**, same as R7 | same as R7 | **`lsdp-static serve` on the players' network**, answering instantly | **timer** | **1.0–1.5 s — no difference** | always |
| D1 | Windows | wired LAN | with and without `lsdp-static serve` | counted | 5–6 s from launch | — |
| D2 | Linux AppImage | wired LAN | with and without `lsdp-static serve` | counted | 5–6 s from launch, no measurable difference | — |

### R6 is the result that matters

With Wi-Fi **explicitly disabled** and a cable attached, both phones showed all
four players in about a second, every single time, on every test. No failures,
no trickle, nothing to wait for.

Against 3–5 s and one run in five incomplete over Wi-Fi, that is not a
refinement, it is a different regime.

### R7 confirms R6, and rules out several other explanations

A third device, on a third kind of wired path, lands in the same place: about a
second, complete every single time. Slightly slower than the phones on cable,
and that difference is small enough to be the virtualised display rather than
anything about discovery **[U]**.

What makes R7 worth more than a repeat is everything it differs in. A
**different Android** (LineageOS, not a vendor build), with **no Google Play
services at all**, running a **different app version** (4.16.3 from APKMirror,
where the phones run whatever the Play Store gave them), on **virtualised
hardware**. None of that moved the number.

So the fast-on-wire result does not depend on the vendor Android, on Google Play
services, on a particular app build, or on real hardware. The one thing every
fast run has in common is a **wired path with no Wi-Fi in it**; the one thing
every slow run has in common is Wi-Fi.

### R7 is also a better test rig

The guest is bridged on the host, so `lsdp-static sniff` can watch the same
segment from that host and the guest's screen can be recorded there too — query
out, announces in, and screen filling on one timeline, with no phone and no
stopwatch. That is what made R8 cheap to run.

### R8 puts a floor under it, and the floor is the app

R7's 1.0–1.5 s could have been the protocol: a real player answers a query after
a random 0–750 ms, so about a second was roughly what LSDP alone should cost.
R8 tests that directly — the same guest, with `lsdp-static serve` answering
instantly on the same network — and the number **does not move**.

The answers were available in milliseconds and the app still took 1.0–1.5 s.
**That second is the app's own**, and nothing done to discovery will remove it.

Which gives a clean decomposition of the wait a user actually experiences:

| cost | size | removable by |
|---|---|---|
| the app's own floor | **1.0–1.5 s** | nothing on the network — only by not discovering at all |
| Wi-Fi, on top of that floor | **+2 to 4 s**, plus one run in five incomplete | a cable, or not discovering at all |
| the LSDP protocol itself | none of the total — it finishes inside the floor | — |

### On-the-wire measurement, for comparison

[`lsdp-measure-20260912T185206Z/`](lsdp-measure-20260912T185206Z/) — 20 rounds
against the four real players from a wired host, all 20 complete:

| | min | median | p95 | max |
|---|---:|---:|---:|---:|
| first player (ms) | 8 | 124 | 362 | 366 |
| all players (ms) | 448 | 637 | 739 | 749 |

**The 8 ms belongs to the player that is on Wi-Fi**, which looks like it means
something and does not. It is that player's *smallest of twenty draws*, and the
draws are random by design.

Pooling all 80 sightings gives a mean of 390 ms and a median of 393, against the
375/375 a uniform 0–750 ms delay predicts — the four players are plainly drawing
from the same distribution. Per player:

| player | link | min | mean | median | max |
|---|---|---:|---:|---:|---:|
| Room-A | cable | 20 | 427 | 450 | 749 |
| Room-B | cable | 32 | 420 | 458 | 733 |
| Room-C | cable | 15 | 339 | 312 | 714 |
| **Room-D** | **Wi-Fi** | **8** | **373** | **336** | **739** |

The Wi-Fi player's mean of 373 ms is the closest of the four to the theoretical
375. The expected smallest of twenty draws from 0–750 ms is 36 ms, and a draw of
8 ms or less turns up within twenty about 19 % of the time — so across four
players, a minimum that low *somewhere* is more likely than not.

**Comparing minima across players is comparing noise.** The medians are the
comparable figures, and they say a player on Wi-Fi answers a query no slower
than one on a cable. Player-side Wi-Fi is not implicated in anything here; the
Wi-Fi that matters is the link to the **controller**.

### R3 is now suspect

R3 was recorded as "wired", but R6 makes it likely the phones were **actually
using Wi-Fi** — an adapter was plugged in, but Wi-Fi was never turned off, and
nothing confirmed which interface the app used. Treat R3's 3–5 s as a Wi-Fi
number until it is redone with the interface confirmed.

The cheap confirmation: `lsdp-static sniff` on the players' segment prints the
**source address** of the phone's query, which says outright which interface it
asked from.

### R4 versus R6 is unexplained

Both are "cable, no Wi-Fi", and they differ by two seconds. The difference is
airplane mode.

The likeliest explanation is that **airplane mode did not actually turn Wi-Fi
off** — Android can keep Wi-Fi enabled inside airplane mode once it has been
switched on there — so R4 may be another Wi-Fi measurement **[U]**. The
alternative, that airplane mode itself changes what the app does, is not ruled
out. `sniff` settles this the same way it settles R3.

---

## The list empties itself, and a tap brings it back

A second kind of unreliability, separate from how long discovery takes, and
arguably worse for a user: **the player list goes empty while the app is open
and untouched**, and the app says it cannot find anything it was showing a
minute earlier.

This was first seen during R4 and dismissed as an oddity. It has since been
reproduced deliberately and timed, so it is recorded properly here.

### The cycle, timed **[V hardware]**

On the Fairphone over Wi-Fi, with **every discovery mechanism deliberately
switched off** — no UDP broadcast relay, no `lsdp-static`, mDNS relay disabled:

| t | what the app does |
|---|---|
| 0 s | tap Players — **all four appear instantly** |
| ~30 s | the list changes to **"Discovering…"** |
| ~50 s | it settles on **"No Player Found"**, list empty |
| any time after | tap Players — **all four are back within 1 s** |

Then it repeats. Throughout all of it, **the previously selected player stays
fully controllable**.

The R4 sighting was the same cycle under different conditions (airplane mode and
a cable, disappearance estimated at 30–45 s), including the detail that tapping
Players brought them back and they vanished again shortly after. One run there
simply kept emptying.

### Three things about this are strange

**It empties itself with nothing wrong.** The app declares "No Player Found"
while it is simultaneously controlling a player over the network. Whatever
empties the list is not the players being unreachable, because one demonstrably
is not.

**It refills with no discovery mechanism running.** With LSDP and mDNS both
switched off, a tap repopulates the whole list in under a second. Nothing could
have been discovered in that second by either protocol, so the list must come
from somewhere the app already had it — or from reaching the players directly at
addresses it already knew **[U]**. `bluos-http-api.md` §12.1 notes that
controllers detect departure by *failing to reach* a player rather than by being
told, which implies the app does probe known addresses; §12.3 shows the desktop
builds can work from a plain address list with no discovery at all. A cached
address list plus a unicast HTTP check would explain both the emptying and the
one-second refill, but nothing here proves it.

**So the app has a cache it does not trust.** It holds the full list well enough
to render it instantly on demand, and it also throws that list away on a timer
while sitting idle. Those two behaviours are hard to reconcile from the outside.

### What this does and does not affect

It does **not** affect the measured runs R1–R8. Every one of those force-closes
the app between runs — step 5 of the procedure, swipe it out of the app drawer —
which kills the process and any runtime cache with it. They measure a cold start
by construction, which is exactly why they are immune to this.

It does mean one loose observation should be treated as unusable: with nothing
running, the Wi-Fi app on the Fairphone appeared to show all players as fast as
on a cable, roughly three times in four. That was almost certainly the cache
rather than discovery, since the app was not force-closed between attempts. The
same session's impression that a cold start is slower, and that the static
announce therefore helps, is an impression only — `lsdp-static` was not running
during it **[U]**.

### Open questions

- What empties the list. A cache lifetime, a failed background refresh, and a
  discovery-state machine timing out are all consistent with what was seen.
- Whether the ~30 s and ~50 s marks are fixed. Two observations is not a
  pattern, though both sightings agree to within the noise of estimating.
- Whether the 57 s ± 6 s announce cycle is involved. It is the same order of
  magnitude as the time to disappearance, which is suggestive and nothing more
  **[U]**.
- What refills the list in under a second with both discovery protocols off.
  `lsdp-static sniff` would show whether anything goes out on 11430 at all when
  the list refills — and if nothing does, the answer is unicast HTTP to cached
  addresses, which is worth knowing because it is what Musica would do anyway.

### Why it matters more than the timing does

A slow list fills eventually. A list that empties itself while the app is open
is a failure the user meets mid-task, with no obvious cause and no action to
take except tapping again. It also means the app's own cache is already capable
of doing what Musica intends to do — hold the list and render it instantly — and
the app discards it anyway.

---

## What is established, and what is not

Established **[V hardware]**:

- Over a cable with Wi-Fi off, discovery takes about a second and never failed —
  on three devices now, including one with no Google Play services and a
  different app version, so it is not a property of one phone or one build.
- That remaining second is **the app's own** and not the protocol's: answering
  instantly does not shorten it (R8). Nothing measured here requires it to exist.
- Used over Wi-Fi, the app is much worse than over a cable, in both speed and
  reliability. *Why* is not established — app, Android's Wi-Fi stack, or the
  access point are all consistent with the data — but the effect does not depend
  on settling that.
- A player on Wi-Fi answers a query no slower than one on a cable.
- The app empties its own player list after roughly 30–50 seconds sitting idle,
  and refills it in under a second on a tap — with every discovery mechanism
  switched off, and while the selected player stays controllable throughout.
- Over Wi-Fi, it takes 3–5 s and fails to complete roughly one run in five.
- The desktop app takes 5–6 s from launch on both Windows and Linux, and a
  static LSDP responder does not change that.
- A static LSDP responder does not change the Android timing either; what it
  changes is that players arrive together rather than one or two at a time.
- The Xiaomi Mi 9 does not bring up USB Ethernet in airplane mode at all.

Not established:

- **Which interface each of R1–R4 actually used.** This is the big one. R3 and
  R4 may both be Wi-Fi measurements mislabelled as wired.
- Whether Waydroid being a few tenths slower than the phones means anything; a
  virtualised display is the dull explanation.
- *What* the app spends its 1.0–1.5 s floor on. R8 establishes that it is
  app-side; it does not say whether the app queries late, renders late, or waits
  deliberately.
- What empties the list, what refills it in under a second with no discovery
  running, and whether the ~30 s / ~50 s marks are fixed.
- Whether the desktop apps would also improve with Wi-Fi off — they were on
  wired LAN throughout, so the comparison has not been run.

## Next measurements

1. **`lsdp-static sniff` beside a Waydroid run**, if the app's 1.0–1.5 s floor
   is worth breaking down further. It answers nothing and timestamps every
   datagram, so it would show whether the app queries at the moment of the tap
   and renders a second later, or waits a second before querying at all. Both
   are app-side either way, so this is optional. Its other use is on a phone,
   where the source address of the query says which interface was really used —
   which is what would resolve R3 and R4.
2. **Redo R3 with Wi-Fi confirmed off**, to replace a suspect row with a real one.
3. **Screen-record the phone** rather than watching it; Android records natively
   and scrubbing the video resolves the tap and each player's appearance to
   about a tenth of a second.
4. **Try `--query R`.** Its answers come back by **unicast**, which does not
   depend on Wi-Fi broadcast delivery at all. If the Wi-Fi penalty is broadcast
   handling, a unicast query is the protocol-level way around it — and Musica
   can send one even though no shipping client does.
