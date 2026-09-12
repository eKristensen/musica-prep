# Does better LSDP make the controller apps faster?

**Reliability: yes, visibly.** With a static responder answering instantly, the
four players appear in the Android app **all at once** instead of trickling in
one or two at a time.

**Timing: no.** The full list still takes 3–5 seconds, and the desktop app is
unchanged at 5–6 seconds. The answers are on the wire in milliseconds, and the
app is already on screen showing its cached player while the other three wait.
The wait is not discovery.

Testing from 2026-09-12 onward, four players, three VLANs on `ek-arm`, with
`lsdp-static` v1.0. Confidence markers follow `bluos-http-api.md`:
**[V hardware]** observed directly here, **[U]** unverified — test first. Later
rounds have corrected earlier ones; where that happened it is called out rather
than quietly edited.

---

## What each number measures

These are not the same measurement, and conflating them is how the first draft
of this document got it wrong.

| | measured from | to |
|---|---|---|
| **Android** | pressing the **Players** tab | all four players listed |
| **Windows / Linux** | launching the app | players listed |

The Android number deliberately excludes app startup. It is the number that
matters: on Android the app is pushed out of memory constantly, so this is the
wait a user actually pays, over and over, all day. The desktop number includes
startup because on the desktop the app stays running and discovery happens once.

## Android **[V hardware]**

Three network positions have now been tested, on two phones:

| # | position | discovery source | time to full list |
|---|---|---|---|
| 1 | different VLAN from the players | the static responder on `ek-arm` | 3–4 s |
| 2 | same VLAN as the players, Wi-Fi | the players directly | 3–4 s |
| 3 | **same layer 2 as the players, wired** (USB Ethernet) | the players directly | 3–5 s |

**Nothing about the network path changes the answer.** Cross-VLAN through a
static responder, same subnet over Wi-Fi, and same segment over cable all land
in the same three-to-five seconds. Whether the app even uses the USB Ethernet
interface is unconfirmed **[U]** — but since wired and wireless agree, it does
not matter much either way.

### The shape of the wait, which is the real finding

On the wired same-segment test, pressing the player-list button, five times
back to back:

- **4 times out of 5**: the **previously selected player is already on screen**,
  with no wait at all. The other three appear **together, about 4 seconds
  later**.
- **1 time out of 5**: previously selected player instant, then two more, then
  the last one about a second after those.

The first part is the important half. **The app shows the last-selected player
instantly**, which means it has that player cached and does not discover it at
all. The network is therefore demonstrably fine at t ≈ 0 — the app is on screen
and usable with one player before a single discovery answer could have arrived.

The other three then wait about four seconds. They cannot be waiting for the
protocol: measured on the same segment, all four announces are in hand within
750 ms at worst, and within milliseconds against a static responder. So roughly
three seconds of the wait is the app holding results it already has **[U]** —
which matches the "forced wait time" noted independently in
`musica/MOTIVATION.md`.

### This corrects the earlier explanation in this file

An earlier draft blamed the one-by-one trickle on the players' random 0–750 ms
reply delay. **That does not survive this data**: 750 ms is comfortably inside
the app's own four-second hold, so a spread that small cannot produce a visible
trickle.

The account that fits all three tests is simpler. The app renders its list on
its own schedule, around three to four seconds in. Anything that has arrived by
then appears together; anything still in flight appears when it lands.

| setup | when answers arrive | what the screen does |
|---|---|---|
| static responder | all within ms | all together |
| same segment, real players | all within 750 ms | all together, ~4 s in |
| the old UDP broadcast relay | spread out, some lost and only recovered by the t = 1, 2, 3, 5, 7, 10 s query retries | trickles in, one or two at a time |

So the trickle was the **relay** losing and delaying datagrams past the app's
render, not the players' reply delay. And the static responder's real
contribution is now clear: it gets every answer in well before the app's
deadline, every time. That is exactly "a positive result in reliability, a
negative result in timing".

The 1-in-5 variant — two, then one more a second later — says the render is not
a single fixed timer in every case, and is unexplained **[U]**.

## Desktop: Windows and Linux **[V hardware]**

**5–6 seconds from launch, unchanged**, with the static responder in place and
the host firewall opened so the datagrams could arrive.

The two are one result, not two. The Linux client is
[`bluos-controller-linux`](https://gitlab.com/zquestz/bluos-controller-linux),
which downloads the **official Windows installer**, extracts the Electron app,
applies a patch and builds an AppImage — of version **4.16.0**, which is the
exact build `bluos-http-api.md` was written from. Same code, two operating
systems, same number. The agreement is corroboration.

So the desktop client is the analysed one, and what is known about it applies:
it browses mDNS *and* sends LSDP queries, rebuilds its entire Bonjour browser
every ten seconds, and resolves mDNS services in two stages (§12.2). The earlier
suspicion that "the Linux app still relies on mDNS" is better stated as: the
desktop client uses both, and nothing here shows which one it acted on **[U]**.

## What this means

| | time to all four players |
|---|---|
| on the wire, real players | ~640 ms median, ~730 ms p95 |
| on the wire, static responder | ~0 ms |
| **Android, Players tab → cached player** | **instant** |
| **Android, Players tab → full list** | **3–5 s** |
| **Windows / Linux, launch → full list** | **5–6 s** |

Three to five seconds pass on Android with every answer already in hand — and
with the app already on screen and usable, showing the player it had cached.
Making discovery instant removed the trickle and removed the relay's
unreliability, and it moved the total wait by nothing measurable.

**A faster responder cannot fix a slow client.** The discovery process in the
Android app is as slow as it ever was — which is the thing that motivated Musica
in the first place, and this is now measured rather than assumed. A controller
that keeps its own player list and does not rediscover on every launch is the
only thing that removes this wait.

The app itself demonstrates the fix, on one player. It shows the last-selected
player instantly, from cache, with no discovery — and then makes the other three
wait four seconds. **Musica's design target is simply to do for every player
what the BluOS app already does for one.**

## Loose ends

**One player is on Wi-Fi, and it is not consistently the slowest.** Expected,
and it supports the model above rather than undermining it: Wi-Fi adds perhaps
tens of milliseconds, while the random reply delay spans 750. The draw swamps
the link. If a Wi-Fi player were *consistently* last, that would be the
interesting result.

**The mDNS + relay baseline was not timed.** Whether the previous setup was
slower than 3–4 s is not recorded, only that it was "most likely not faster".
Nothing here depends on it, but it is the one number missing from the
comparison.

## Next tests, cheapest first

1. **`staticPlayers.txt` on the desktop** — see below. If the app still takes
   5–6 seconds with discovery skipped entirely, the delay is definitively not
   discovery, and the desktop half of this question is closed.
2. **`lsdp-static sniff` while pressing the player-list button.** Run it on the
   players' segment; it answers nothing and prints every datagram with a
   timestamp. Compare when the announces actually arrived against when the
   screen filled. If the answers are all in at 700 ms and the last three players
   appear at 4 s, the app's own delay is measured rather than inferred, and this
   whole question is closed. The source address also says which interface the
   phone really asked from.
3. **Time the old baseline**, ten Players-tab presses with the relay and no
   static responder, to fill in the missing row.
4. **`--query R` at a real player**, to settle claim `C-19`. Unrelated to timing,
   but this tool can answer it.

### Where `staticPlayers.txt` lives

A documented feature, though documented by **Bluesound Professional** for the
remote-subnet case rather than in the consumer app guide — and independently
[V] in the client code (§12.3).

| platform | path |
|---|---|
| Windows | `C:\Users\<you>\AppData\Roaming\BluOS Controller\staticPlayers.txt` |
| Linux AppImage | `~/.config/BluOS Controller/staticPlayers.txt` **[U]** |
| macOS | `~/Library/Application Support/BluOS Controller/staticPlayers.txt` **[U]** |

The Windows path is the documented one. The other two are Electron's standard
`app.getPath('userData')` for the same product name, so they should hold for the
AppImage repack — unverified, but the directory either exists or it does not,
which is a five-second check.

Contents are one comma-separated line of `ip:port`, no spaces:

```
192.168.0.1:11000,192.168.0.2:11000,192.168.0.3:11000
```

The port matters: it is how a multi-zone chassis such as a CI580 is addressed,
each node on its own port (`:11000,:11010,:11020,:11030`) at one address. Players
listed here are used directly, **with no discovery at all**, which is what makes
this the decisive test.

Sources: [How to Discover and Control Players from a Remote
Subnet](https://support.bluesoundprofessional.com/hc/en-us/articles/360060411413-How-to-Discover-and-Control-Players-from-a-Remote-Subnet)
(Bluesound Professional) · [`bluos-controller-linux`
README](https://gitlab.com/zquestz/bluos-controller-linux/-/raw/main/README.md)
