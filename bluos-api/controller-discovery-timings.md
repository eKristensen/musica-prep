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

### R7 is also a much better test rig

The guest is bridged on the host, so `lsdp-static sniff` can watch the same
segment from that host, and the guest's screen can be recorded there too. Query
out, announces in, and screen filling can finally be put on one timeline —
without a phone, a stopwatch, or a person counting.

That makes one experiment cheap that was not before: run `lsdp-static serve`
against this guest and see whether 1.0–1.5 s drops. A real player answers after
a random 0–750 ms, so roughly a second is about what the protocol alone would
cost, and there may be very little app-side delay left to find on a good link
**[U]**. If the number falls to a few hundred milliseconds against a responder
answering instantly, that is the protocol's cost measured directly; if it stays
near a second, the remainder is the app's.

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

## Anomaly: players vanishing while the app is open

Seen on the Fairphone during R4 (airplane mode + cable), several times
**[V hardware]**:

- The app was left open and idle, roughly 30–45 seconds (estimated, not timed).
- **All players disappeared** from the list.
- They did not come back on their own. Tapping Players ran what looked like a
  normal discovery, and then they were gone again a few seconds later.
- On one occasion they simply kept disappearing.

Not seen in R6. Worth relating to two things already established about
controllers in `bluos-http-api.md` §12.1:

- **Departure is detected by failing to reach a player, not by being told** — no
  controller acts on an LSDP Delete. So something was failing, either the
  players stopping being reachable over HTTP or their announces not arriving.
- Players re-announce unprompted every **57 s ± 6 s**, which is the same order
  of magnitude as the 30–45 s to disappearance, though nothing here ties the two
  together **[U]**.

This is a separate phenomenon from slow discovery and should not be folded into
it.

---

## What is established, and what is not

Established **[V hardware]**:

- Over a cable with Wi-Fi off, discovery takes about a second and never failed —
  on three devices now, including one with no Google Play services and a
  different app version, so it is not a property of one phone or one build.
- That remaining second is **the app's own** and not the protocol's: answering
  instantly does not shorten it (R8).
- A player on Wi-Fi answers a query no slower than one on a cable.
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
- What causes the vanishing players.
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
