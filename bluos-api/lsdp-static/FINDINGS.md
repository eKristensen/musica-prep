# Does better LSDP make the controller apps faster?

**No — and the reason has changed twice as the data came in.**

Making LSDP answer instantly does not shorten the wait in any controller app.
What it changes is *how* the players arrive: together, rather than one or two at
a time. But the wait itself turned out not to be the protocol's, and — as of the
latest round — probably not the app's either. It looks like the **link**.

All the numbers are in
[`../controller-discovery-timings.md`](../controller-discovery-timings.md),
which is the data; this file is the reasoning over it. Confidence markers follow
`bluos-http-api.md`: **[V hardware]** observed directly, **[U]** unverified.

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
| **Wi-Fi** | 3–5 s | about 4 in 5 |
| **cable, Wi-Fi explicitly disabled** | **≈1 s** | **every run, both phones** |

That is the finding the latest round produced, and it is not a small one. The
same app, the same players, the same second — a different link, and discovery
stops being a problem.

Two earlier runs were recorded as "wired" and are now suspect: an adapter was
plugged in but Wi-Fi was never turned off, and nothing confirmed which interface
the app used. Until that is redone, treat them as Wi-Fi measurements.

### The leading explanation **[U]**

Broadcast delivery over Wi-Fi to a phone is the weak point — power save,
DTIM buffering, and access points handling broadcast badly are all well known,
and LSDP is broadcast by design. On a cable none of that applies.

This is a hypothesis, not a measurement. It is worth stating because it is
cheap to test and because it points somewhere useful: **the protocol already has
a unicast path.** An `R` query (§12.1) asks responders to answer by unicast
instead of broadcast, which sidesteps Wi-Fi broadcast handling entirely. No
shipping client sends one. `lsdp-static serve` answers them, and Musica could
send them.

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

## What this means for Musica

The justification is intact, and the reason for it is sharper.

A phone is on Wi-Fi in real life. Over Wi-Fi, discovery costs 3–5 seconds and
fails to complete about one run in five, and nothing done to the network side —
a relay, a static responder answering in microseconds — changed either number.
Broadcast discovery on Wi-Fi is simply not dependable.

A controller that keeps its own player list does not discover at all on the path
that matters, so none of this applies to it. The BluOS app already does exactly
that for one player, the selected one, which survives its shutdown cache clear.
**Musica's design target is to do that for every player** — and, where discovery
is unavoidable, to prefer the unicast `R` query over broadcast.

## The measurements that would close this

1. **`lsdp-static sniff` beside every run.** It answers nothing and timestamps
   every datagram. The source address of the phone's query says which interface
   it really used, which resolves the two suspect runs outright; the gap between
   the announces arriving and the screen filling says whether anything is being
   held back.
2. **Redo the wired runs with Wi-Fi confirmed off**, so the comparison rests on
   confirmed configurations rather than plugged-in adapters.
3. **`staticPlayers.txt` on the desktop** (§12.3), which makes the desktop apps
   skip discovery entirely. If Windows still takes 5–6 s, its delay is
   definitively not discovery. Path and format are in the data file's companion
   notes below.
4. **`--query R` against a real player**, which would settle claim `C-19` and, if
   the Wi-Fi hypothesis holds, demonstrate the way around it.

### Where `staticPlayers.txt` lives

Documented by **Bluesound Professional** for the remote-subnet case, and
independently **[V]** in the client code (§12.3).

| platform | path |
|---|---|
| Windows | `C:\Users\<you>\AppData\Roaming\BluOS Controller\staticPlayers.txt` |
| Linux AppImage | `~/.config/BluOS Controller/staticPlayers.txt` **[U]** |
| macOS | `~/Library/Application Support/BluOS Controller/staticPlayers.txt` **[U]** |

One comma-separated line of `ip:port`, no spaces:

```
192.168.0.1:11000,192.168.0.2:11000,192.168.0.3:11000
```

The port matters: it is how a multi-zone chassis such as a CI580 is addressed,
each node on its own port (`:11000,:11010,:11020,:11030`) at one address.
Players listed here are used directly, **with no discovery at all**.

Sources: [How to Discover and Control Players from a Remote
Subnet](https://support.bluesoundprofessional.com/hc/en-us/articles/360060411413-How-to-Discover-and-Control-Players-from-a-Remote-Subnet)
(Bluesound Professional) · [`bluos-controller-linux`
README](https://gitlab.com/zquestz/bluos-controller-linux/-/raw/main/README.md)
