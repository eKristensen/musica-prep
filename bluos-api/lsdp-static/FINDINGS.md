# Does better LSDP make the controller apps faster?

**Reliability: yes, visibly.** With a static responder answering instantly, the
four players appear in the Android app **all at once** instead of trickling in
one at a time.

**Timing: no.** The full list still takes 3–4 seconds to appear, and the desktop
app is unchanged at 5–6 seconds. The answers are on the wire in milliseconds;
the wait is somewhere else.

Early testing, 2026-09-12, four players, three VLANs on `ek-arm`. Confidence
markers follow `bluos-http-api.md`: **[V hardware]** observed directly here,
**[U]** unverified — test first.

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

Two phones, deliberately different:

| phone | network position | discovery source |
|---|---|---|
| A | different VLAN from the players | the static responder on `ek-arm` |
| B | **same VLAN as the players** | the players themselves, directly |

**No difference in timing between them.** Both take 3–4 seconds from the
Players tab to a full list, with all four players present 9 times out of 10,
testing back to back.

That equivalence is the useful part: **a static LSDP responder puts a phone on
another VLAN in the same position as a phone sitting on the players' own
subnet** — and whatever instability the `udp-broadcast-relay-redux` setup was
contributing is gone with it.

### The one clear improvement: all at once, not one by one

Before the static responder, players "almost always show up one-by-one,
sometimes two at once". With it, they appear together.

That is a real quality difference even though the total time did not move, and
the mechanism is measurable rather than mysterious. A real player delays its
answer by a random 0–750 ms (§12.1), independently per player, so four players
answer spread across most of a second — which is exactly what a list filling in
one entry at a time looks like. The static responder answers for all four in one
burst at 0 ms, wins the race against their own announces, and the app has the
whole list in one go.

Measured on the wire, the same responder, the only difference being the reply
delay:

| responder behaviour | time to all four players |
|---|---|
| `--delay-ms 0-750`, imitating real players | 279–743 ms, median 671 |
| `--delay-ms 0` (the default) | ~0 ms, every round |

**A prediction this makes [U]:** phone B, talking to real players directly,
should *still* trickle, because those players still draw their own 0–750 ms.
If both phones show the list appearing all at once, this explanation is wrong.
Watching the two side by side settles it in one try.

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
| **Android, Players tab → full list** | **3–4 s** |
| **Windows / Linux, launch → full list** | **5–6 s** |

Three to four seconds pass on Android with every answer already in hand. Making
discovery instant removed the trickle and it removed the relay's unreliability,
and it moved the total wait by nothing measurable.

**A faster responder cannot fix a slow client.** The discovery process in the
Android app is as slow as it ever was — which is the thing that motivated Musica
in the first place, and this is now measured rather than assumed. A controller
that keeps its own player list and does not rediscover on every launch is the
only thing that removes this wait.

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
2. **Watch both phones side by side** for trickle versus all-at-once, to confirm
   or kill the explanation above.
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
