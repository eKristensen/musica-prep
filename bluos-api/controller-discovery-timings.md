# Controller discovery timings

How long a BluOS controller takes to show every player, measured on real
devices. **This file holds the measurements and what each run shows** — the
conditions a run was taken under, the numbers it produced, and the reading those
numbers support.

Two neighbouring files lean on it and neither restates it.
[`controller-code-notes.md`](controller-code-notes.md) carries the causes behind
these numbers once one can be traced to a line in a shipping app, read out of
the Android and Windows builds; a *why* that is answered from code belongs
there, and is referred to from here rather than copied.
[`lsdp-static/FINDINGS.md`](lsdp-static/FINDINGS.md) carries only the verdict on
the static-responder experiment. Keeping them apart means a later correction in
one place does not quietly rewrite the observations here.

Four players, all on one VLAN. One of them is on Wi-Fi; the rest are wired.

What varies between runs is where the *controller* sits. On the players' own
VLAN it reaches them directly. On any other VLAN its traffic is routed, and
LSDP's broadcasts only cross the boundary because `ek-arm` forwards them —
`udp-broadcast-relay-redux` on UDP 11430 before these tests, and during some of
them `lsdp-static serve` in its place. The *discovery path* column of each run
says where that run's controller was and what answered it.

Confidence markers follow `bluos-http-api.md`: **[V hardware]** observed
directly here, **[U]** unverified — a claim about behaviour that has not been
tested. Detail that was simply never written down is marked *not recorded*
in plain words; that is a gap in the notes, not an untested claim, and the
markers are not used for it.

---

## Devices

| device | detail |
|---|---|
| **Fairphone 5 5G** | Android 15 (API 35), build `FP5.VT31.C.114.20260804`. App **4.16.3 build 3224** from the Play Store. **Background usage allowed** for the BluOS app |
| **Xiaomi Mi 9** | MIUI Global 12.5.1, Android 11 (API 30), `RKQ1.200826.002`. App **4.16.2 build 3217** from the Play Store. **No battery-saver restrictions** on the BluOS app |
| **Waydroid** | LineageOS 20 — Android 13 — image `20-20260403-VANILLA-waydroid_x86_64`, minimal Android with **no Google Play**. App **4.16.3**, APK from APKMirror. Bridged to the host's network, with its own address on the players' VLAN |
| **iPhone 16** | iOS 26.6.2. BluOS Controller **4.16.2** |
| **Windows** | BluOS Controller 4.16.0 (Electron) |
| **Linux** | [`bluos-controller-linux`](https://gitlab.com/zquestz/bluos-controller-linux) — the same official 4.16.0 Electron app, repackaged as an AppImage |

USB Ethernet on the phones is a wired adapter; "Wi-Fi" means the phone's own
radio. The Waydroid guest is wired throughout — a host bridge, no radio anywhere
in its path.

All four controllers report a BluOS version of **4.16.22**, which is the
players' firmware rather than anything about the controller: the number is the
same across three different controller builds on three operating systems.

## Method

**Android**, one run:

1. Open the BluOS app.
2. Wait for the menu bar.
3. Tap the player icon — **timer starts**.
4. Stop when all four players are listed.
5. Open the app drawer, **swipe the app away**, start again.

Step 5 is meant to force a cold start, and **the measurements show it worked**:
a process that survives the swipe still holds the whole player list in memory
and renders it in under a second, so any run that took seconds was a genuine
cold start. Android does not actually promise to kill a process on a swipe — see
[`controller-code-notes.md`](controller-code-notes.md) — which is why the
instant-list behaviour was hard to provoke on demand, and why the timing itself
is better evidence that a run was cold than the swipe is.

The currently selected player survives a real kill regardless: it is the one
player written to storage, and it is read back at startup rather than
rediscovered.

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
| R1 | one Android phone (which one not recorded) | Wi-Fi | `lsdp-static serve`, different VLAN | counted | 3–4 s | 9 of 10 |
| R2 | the other Android phone | Wi-Fi | players directly, same VLAN | counted | no difference from R1 | — |
| R3 | both phones | USB Ethernet — **but see the note** | players directly, same layer 2 | counted | 3–5 s | 4 of 5 |
| R4 | Fairphone 5 5G | airplane mode + USB Ethernet | players directly | **timer** | **2.9–3.4 s** | 4 of 5 |
| R5 | Xiaomi Mi 9 | airplane mode + USB Ethernet | — | — | **Ethernet did not work at all**, no discovery | none |
| R6 | **both phones** | **Wi-Fi disabled** + USB Ethernet | players directly | **timer** | **≈1 s, a little above** | **always, every run, both devices** |
| R7 | **Waydroid** (LineageOS, no Google Play, app 4.16.3) | **bridged, wired**, own IP on the players' VLAN | players directly | **timer** | **1.0–1.5 s** | **always, however many times tried** |
| R8 | **Waydroid**, same as R7 | same as R7 | **`lsdp-static serve` on the players' network**, answering instantly | **timer** | **1.0–1.5 s — no difference** | always |
| R9 | **iPhone** | **Wi-Fi**, and separately wired with Wi-Fi off | players directly, same VLAN | **not timed** — impression only | **instant, no "Discovering…" at all** | **always, on either link** |
| D1 | Windows | wired LAN | with and without `lsdp-static serve` | counted | 5–6 s from launch | — |
| D2 | Linux AppImage | wired LAN | with and without `lsdp-static serve` | counted | 5–6 s from launch, no measurable difference | — |
| D3 | Windows | wired LAN | **`staticPlayers.txt`, with mDNS and LSDP discovery disabled** | counted | **no faster than before** | only the listed players appear |

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
**different Android** (LineageOS 20, not a vendor build), with **no Google Play
services at all**, on **virtualised hardware**, and with the app sideloaded from
APKMirror rather than installed from the Play Store. None of that moved the
number.

The app build is *not* one of the differences: R7 runs 4.16.3, the same version
the Fairphone runs. The Mi 9 runs 4.16.2 — but the two builds' discovery code is
byte-identical, so no result in this file turns on which of them a device ran.
See [`controller-code-notes.md`](controller-code-notes.md) for how that was
checked.

So the fast-on-wire result does not depend on the vendor Android, on Google Play
services, or on real hardware. The one thing every fast run has in common is a
**wired path with no Wi-Fi in it**; the one thing every slow run has in common
is Wi-Fi.

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

### R9: iOS does not have the problem, on either link

On the iPhone the app simply works. Players are there, immediately, with no
"Discovering…" stage — **the same on Wi-Fi as on a cable with Wi-Fi off**. Only
the same VLAN was tested, which is enough for the question being asked.

Not timed, so "instant" is an impression rather than a number, and the device
and iOS version are recorded loosely. It is corroborated by a family member
running Bluesound from iOS who reports never having seen any of the behaviour
described on Android — hearsay, and worth having.

**This is the most informative single observation in the file**, because of what
it removes. The same house, the same players, the same access point, and the
Wi-Fi penalty does not appear. So the 2–4 seconds and the one-in-five
incompleteness are **not a property of the network, the access point, or Wi-Fi
as such**. They belong to the Android side — either to Android's handling of
multicast and broadcast, or to what the Android app does about it.

### R9 is a controlled comparison, not an anecdote

The iPhone and the Mi 9 are on **the same Wi-Fi, the same access point and the
same players**, and they behave completely differently. One variable changed —
the operating system — and the outcome flipped. That is a control, and it
carries a result: **the Wi-Fi penalty is on the Android side [V hardware]**. The
network, the access point and Wi-Fi as a medium are ruled out, not merely
suspected.

It also disposes of the cache confound that made an earlier Android observation
unusable. On the iPhone the players are there immediately **however many times
the app is restarted**, so this is cold-start behaviour and not a warm cache
surviving between launches.

### Which Android-side cause — answered from the code

The app delays discovery by a hard-coded two seconds whenever the Wi-Fi radio is
enabled, whatever interface is actually carrying traffic. That is what the rows
above are measuring, and it is read out of the app in
[`controller-code-notes.md`](controller-code-notes.md), which also disposes of
the multicast-lock guess this section used to carry.

**Battery management is not the explanation.** The app is allowed background
usage on the Fairphone and exempt from battery-saver restrictions on the Mi 9,
and both still show the penalty — so Android, and MIUI especially, killing or
throttling background apps is ruled out.

### D3: the desktop delay is not waiting for answers

With `staticPlayers.txt` in place and **mDNS and LSDP discovery both switched
off**, only the listed players appear — so the file took effect — and startup is
**no faster than before [V hardware]**.

**Why it changed nothing** is settled in the Windows source rather than by the
vendor's framing of the feature: the file is read by a module that runs
*alongside* LSDP and Bonjour rather than instead of them, and delivers its
players on its own three-second timer — see
[`controller-code-notes.md`](controller-code-notes.md). The measurement stands
on its own as well: with no discovery mechanism running there were no answers to
wait for, and the wait was unchanged.

The desktop is at least stable once up: none of the list-emptying seen on
Android **[V hardware]**.

### `staticPlayers.txt` is built for a different problem

Bluesound Professional documents it for reaching players across subnets, scopes
it to Windows and macOS only — not Android, which is where the problem is — and
excludes grouping. Path, format and the quoted limits are in
`bluos-http-api.md` §12.3; what the code does with the file is in
[`controller-code-notes.md`](controller-code-notes.md).

### R3 is now suspect

R3 was recorded as "wired": an adapter was plugged in, but the Wi-Fi radio was
never switched off. Its numbers sit with the Wi-Fi rows and that is where they
are filed.

**A plugged-in adapter is not a wired test**, and the reason is sharper than
mislabelling. The app's two-second delay keys on the radio being *enabled*, not
on which interface carries traffic
([`controller-code-notes.md`](controller-code-notes.md)), so a run with the
adapter in and the radio on was not a mislabelled wired test — it was measuring
the wrong variable. Confirm the radio is off, or confirm the interface from the
source address of the query, or the label is a guess.

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
empties the list is not the players being unreachable.

**It refills with no discovery mechanism running.** With LSDP and mDNS both off,
a tap repopulates the whole list in under a second — nothing could have been
discovered in that second by either protocol.

**The timings are not arbitrary, and neither is the refill.** The app's own
constants account for the ~30 s and ~50 s marks exactly, for why players age out
long before they would next announce, and for why a tap restores the list
without touching the network: see
[`controller-code-notes.md`](controller-code-notes.md).

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

All of it is accounted for by the app's own code — the ~30 s and ~50 s marks,
why players age out long before they would next announce, and what puts the list
back on screen in under a second with both discovery protocols off. See
[`controller-code-notes.md`](controller-code-notes.md). Nothing goes out on the
network at that moment; the list never left memory.

### Why it matters more than the timing does

A slow list fills eventually. A list that empties itself while the app is open
is a failure the user meets mid-task, with no obvious cause and no action to
take except tapping again. It also shows the app's own cache is already capable
of holding the list and rendering it instantly — and that the app discards it
anyway.

---

## What is established, and what is not

Established **[V hardware]**:

- Over a cable with Wi-Fi off, discovery takes about a second and never failed —
  on three devices now, including one with no Google Play services and a
  different app version, so it is not a property of one phone or one build.
- That remaining second is **the app's own** and not the protocol's: answering
  instantly does not shorten it (R8). Nothing measured here requires it to exist.
- Used over Wi-Fi, the app is much worse than over a cable, in both speed and
  reliability. The cause is now read out of the app itself — see
  [`controller-code-notes.md`](controller-code-notes.md).
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
- The desktop's 5–6 s is not spent waiting for discovery **answers**: with no
  discovery mechanism running at all, startup took the same time (D3), and
  `staticPlayers.txt` never replaced discovery in the first place. The desktop
  is stable once up.
- **iOS does not have the Wi-Fi problem at all**, on the same network and the
  same players, which rules the network and the access point out as the cause.
- Android battery management is not the cause either: the app has background
  usage allowed on the Fairphone and no battery-saver restrictions on the Mi 9,
  and both still show the penalty.

Not established:

- **Which interface each of R1–R4 actually used** — though it now matters less
  than it seemed to, since the app's delay keys on the Wi-Fi radio being
  enabled rather than on which interface carries traffic, and the radio was
  never switched off in those runs.
- Whether Waydroid being a few tenths slower than the phones means anything; a
  virtualised display is the dull explanation.
- **What the iOS controller actually does.** `bluos-http-api.md` is built from
  the Android, Windows and macOS controllers; no iOS client is among its
  sources. So the client that behaves best here is the one nothing is known
  about, and claims in that document about what "the clients" do are claims
  about the other three.
- *What* the app spends its 1.0–1.5 s floor on, once the two-second delay is
  out of the picture. R8 establishes that it is
  app-side; it does not say whether the app queries late, renders late, or waits
  deliberately.
- What empties the list, what refills it in under a second with no discovery
  running, and whether the ~30 s / ~50 s marks are fixed.
- Whether the desktop apps would also improve with Wi-Fi off — they were on
  wired LAN throughout, so the comparison has not been run.
- What the desktop spends its 5–6 s on, and whether the static list is added to
  discovery's results rather than replacing them.
- Whether the Linux AppImage reads `staticPlayers.txt`; the vendor supports the
  file on Windows and macOS only.

## What is left

The measuring is done. Nothing here is a prerequisite for anything, and the two
suspect runs need no redoing — the wired figure rests on three later runs that
are not in doubt, and R3 and R4's own numbers sit with the Wi-Fi rows, which is
where they are filed.

"App or platform?" is no longer one of them: the Wi-Fi penalty is the app's own
two-second delay. One question stays open because nobody has looked, not because
anything waits on it:

- **Does a real player answer a unicast `R` query?** `lsdp-static measure --query R`
  aimed at a player settles claim `C-19` in `bluos-http-api.md`, currently
  INCONCLUSIVE. A protocol question rather than a timing one.

Smaller unknowns, recorded above where they arose and not worth a trip on their
own: what the Android app spends its 1.0–1.5 s floor on, what empties its player
list, whether the Linux AppImage reads `staticPlayers.txt`, and why Waydroid is
a couple of tenths slower than the phones.
