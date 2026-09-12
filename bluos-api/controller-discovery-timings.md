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
- Over Wi-Fi, it takes 3–5 s and fails to complete roughly one run in five.
- The desktop app takes 5–6 s from launch on both Windows and Linux, and a
  static LSDP responder does not change that.
- A static LSDP responder does not change the Android timing either; what it
  changes is that players arrive together rather than one or two at a time.
- The Xiaomi Mi 9 does not bring up USB Ethernet in airplane mode at all.

Not established:

- **Which interface each of R1–R4 actually used.** This is the big one. R3 and
  R4 may both be Wi-Fi measurements mislabelled as wired.
- Whether the remaining ~1 s in R6 and R7 is the protocol's own 0–750 ms reply
  delay, rendering, or something else. The Waydroid rig can answer this.
- Whether Waydroid being a few tenths slower than the phones means anything; a
  virtualised display is the dull explanation.
- What causes the vanishing players.
- Whether the desktop apps would also improve with Wi-Fi off — they were on
  wired LAN throughout, so the comparison has not been run.

## Next measurements

1. **`lsdp-static sniff` beside every future run.** It answers nothing and
   timestamps every datagram, so each run records which interface the phone
   queried from, when the query went out, and when each announce arrived. That
   alone resolves R3 and R4.
2. **Redo R3 with Wi-Fi confirmed off**, to replace a suspect row with a real one.
3. **Screen-record the phone** rather than watching it; Android records natively
   and scrubbing the video resolves the tap and each player's appearance to
   about a tenth of a second.
4. **Run `lsdp-static serve` against the Waydroid guest**, from the host that
   bridges it, with `sniff` alongside. Instant answers to a wired guest is the
   cleanest way to separate the protocol's cost from the app's, and it needs
   neither a phone nor a stopwatch.
5. **Try `--query R`.** Its answers come back by **unicast**, which does not
   depend on Wi-Fi broadcast delivery at all. If the Wi-Fi penalty is broadcast
   handling, a unicast query is the protocol-level way around it — and Musica
   can send one even though no shipping client does.
