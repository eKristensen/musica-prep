# Why Musica exists

This document describes the motivation for building Musica. It has two parts:
1) several daily annoyances while using the official Android app, and 2) the
lack of an alternative to the official app that meets my requirements.

---

## My setup

- Four Bluesound players (2 x N132, 1 x N130 and 1 x N110) on a dedicated VLAN.
- mDNS reflection configured between VLANs, verified working — `avahi-browse`
  on a laptop resolves the players quickly and reliably.
- UDP replication for the LSDP protocol across VLANs.

---

## My challenges with the BluOS Controller for Android

A summary of the problems I run into with the official Android app running on
a smartphone.

I have not asked Bluesound to solve any of these problems, and I do not know
anyone else with Bluesound hardware using Android who could check whether the
problem is specific to my setup. Because of that I do not know whether I am the
only one seeing these problems. The discovery mechanism Bluesound use is fairly
complex and it can be hard to prove where the problem lies. I decided I would
rather look for another solution than try to get Bluesound to acknowledge any
of it.

I have only been able to reproduce the problems with the official app on an
Android phone. The Windows and iOS apps do not appear to have them when I test
in my setup. The Windows app does share the slow start — five to six seconds
from launch to players visible — but the list then stays put. The repackaged
Linux build behaves the same on different hardware, and both machines were on
Wi-Fi throughout. Handing the app a fixed list of players and switching
discovery off does not make either of them faster, so that wait is not time
spent finding players. I have no Mac, so the Mac app is untested.

---

### 1. Discovery is a slightly delayed short burst, then silence

Watching UDP traffic while opening the player list, the app waits for two
seconds then sends a small number of discovery probes over roughly the first
ten to twelve seconds, and then stops. After that it appears to listen
passively only.

**Impact:** there is almost always a delay before all players show up, and a
player that doesn't answer within that window — because a broadcast frame was
lost, which on Wi-Fi is common — does not appear at all. Waiting doesn't help.
Backing out of the player list and re-entering is the only way to trigger
another attempt.

### 2. Players sometimes disappear and come back

A player that is present and playing sometimes vanishes from the list for a
while and then returns, with no action on my part. I blocked a player's HTTP
port to simulate it and timed the result: the entry disappears after roughly
fifteen seconds. Normal status updates appear to arrive on a cycle of about ten
seconds, so the margin between "healthy" and "removed" is only a few seconds.
Any hiccup — a roaming event, a slow response, a moment of power saving —
crosses it.

The whole list does it too, and that one I have timed. With the app open and
untouched, the phone on a different VLAN from the players and the relays that
carry discovery across the boundary switched off — so nothing could reach it —
the list empties after about thirty seconds and settles on "No Player Found" at
about fifty. A single tap brings all four back within a second. The player I
had selected stayed controllable throughout.

**Impact:** this is the single most disruptive issue. It makes the list feel
unreliable even when every player is online and reachable.

It also makes grouping risky rather than merely slow. The list reflows as
players come and go, so the entry under my thumb can change between the moment
I decide to tap and the moment the tap registers, and I have then grouped the
wrong player. That happens far too often. Recovering means backing out,
waiting through discovery again and retrying. Reliable grouping needs a list
that holds still. Creating a group appears to make players disappear as well,
which slows the step after it further — I have not timed that one, but it
happens often enough that I have no doubt it is real.

### 3. The currently selected player is sometimes missing from the list

I can be connected to a player, with working controls and volume, while that
same player is absent from the player overview. It appears later, seconds after
everything else.

**Impact:** confusing, and it makes grouping awkward, because a player you
cannot see is a player you cannot group.

### 4. Partial lists that differ depending on what you select

With several players and groups, selecting one player sometimes shows one
subset; selecting another shows a different subset. Repeatedly refreshing
eventually converges on the full set, but it takes several attempts and a
noticeable amount of time.

### 5. Ungrouping leaves a player unusable for a while

After removing a player from a group, that player often cannot be selected for
another ten to twenty seconds. The app behaves as though it is still a group
member, even though the player itself has already left the group. It resolves
on its own eventually.

### 6. It refuses to work over VPN, even though the network works

Over WireGuard the app sometimes functions for a while, and then stops for no
apparent reason. The tunnel keeps working the whole time — I can reach the
players by other means throughout, for example the built-in web UI on the
player. The restriction appears to be based on connection type rather than on
whether the players are actually reachable.

**Impact:** no remote control of my own equipment on my own network, for no
technical reason I can identify. If I forget to pause the music before leaving
home, fixing that should be no harder from outside the house than it would have
been on my way out the door. It also makes it impossible to build an
alternative, potentially more stable, path for the discovery packets over VPN.

### 7. A full rediscovery whose results are then thrown away

Occasionally the app opens with a message saying BluOS lost connection to my
player, and the normal interface is replaced by a full-screen discovery view.
I waited through it once: it found every player, slowly, one at a time, and
then the normal interface appeared — showing **only** the player I had selected
before closing the app. Everything the previous screen had just found was gone,
and had to be discovered again from scratch.

**Impact:** it is hard to see what the first discovery accomplished. It is also
the most conspicuous version of the problem, because the app visibly finds all
the players and then visibly forgets them a second later.

### 8. None of this happens on iOS

The iOS controller, on the same network, with the same players, exhibits none
of the problems above. Players appear promptly and stay in the list. Whatever
is going wrong is specific to the Android controller rather than to BluOS, to
my network, or to my players.

Restarting the iOS app, reloading, refreshing, closing and opening it from the
home screen — no matter what I do, players show up instantly and stay rock
solid. I wonder why I cannot get the same experience on Android.

I have family with Sonos. Discovery on Android for Sonos is rock solid too.

---

### What I ruled out

I want to be fair about this, because "it's your network" is the natural first
response and in many cases it would be correct.

- **Not mDNS reflection.** Reproduced with the phone on the same VLAN as the
  players.
- **Not missing or slow mDNS records.** I published static IPv4 host and
  service entries with Avahi and confirmed from a laptop that they resolved
  quickly and consistently. The behaviour of two Android phones from different
  vendors did not measurably improve: still the last-connected player first,
  then a pause, then the rest. Making the records better available on the wire
  does not help if the client only asks for a moment.
- **Not the players.** They respond promptly to direct HTTP requests
  throughout, including while the app shows them as missing.
- **Not one access point, or one firmware.** The same behaviour has followed me
  across several access points and many firmware versions over a long period.
- **Not general network health.** A wired machine on the same network sees
  discovery traffic and resolves the players quickly and consistently.
- **Not one bad device.** The problems move around between players rather than
  sticking to one.
- **Not the discovery protocols.** The same Android app, bridged and wired
  under Waydroid, shows all four players in one to one and a half seconds,
  complete every time. A different Android, no Google Play, a sideloaded build,
  virtualised hardware — none of it moved that number. Nor did putting a
  responder on the network that answers discovery queries instantly: the number
  did not change at all, so that remaining second and a half is the app's own
  and nothing done to the network will remove it.

What the measurements do point at is the Wi-Fi radio, and not in the way I
expected. On a cable, with the radio left switched on, the phones take around
three seconds. On the same cable, with Wi-Fi explicitly switched off, they take
about one, complete every single run. The traffic went over the wire either
way. What changed the result was whether a radio that was carrying none of it
happened to be enabled.

---

### What I think is going on

This section is interpretation rather than observation. I may be wrong about
the causes; the symptoms above are what I would stand behind.

**Short version:** the Android controller appears to keep its list of players
only while it is in the foreground, and to have several independent mechanisms
that can each add or remove a player from that list. Each of them most likely
has its own timings. The result is a list that is inconsistent even when every
player is online and reachable.

- **The list is short-lived.** Shortly after the app leaves the foreground it
  seems to forget the players, presumably on the assumption that discovery will
  find them again quickly. When discovery is slow or lossy, that assumption
  fails. Observation 7 is the clearest case: one screen finds every player, and
  the next screen shows one.

- **Several mechanisms, acting independently.** At least two discovery
  protocols are in use — mDNS, and a Lenbrook-specific UDP broadcast protocol
  (LSDP) — plus something separate that decides whether an already-known player
  is still available. Lenbrook has been reported as saying they wrote their own
  because
  [their customers cannot be relied on to configure their networks](https://content-bluesound-com.s3.amazonaws.com/uploads/BluOS-Custom-Integration-API_v1.7.pdf),
  a statement that goes back
  [as far as 2020](https://web.archive.org/web/20210120042844/https://nadelectronics.com/wp-content/uploads/2020/12/Custom-Integration-API-v1.0_Dec_2020.pdf).
  A developer who implemented both protocols in 2022 also found the BluOS mDNS
  announcements slow and unreliable, which matches what I see years later
  ([reference](https://blog.jonasbengtson.se/lsdp-lenbrook-service-discovery-protocol)).

- **Why iOS is different — and it isn't the protocols.** I captured traffic and
  the iOS controller sends the same UDP broadcast discovery packets. Both
  platforms use both discovery mechanisms, on the same network, with the same
  players, and behave completely differently. So the explanation cannot be the
  protocols, the players, or the network. What is left is what each client does
  with the results: how long it retains a player it has already found, whether
  it keeps asking, and what makes it decide a player is gone. On iOS the
  players simply stay in the list. An iPhone and an Android phone on the same
  Wi-Fi, through the same access point, to the same players, behave completely
  differently — one variable changed and the outcome flipped, so it is not the
  network, the access point, or Wi-Fi as a medium.

- **Why desktop is different.** Both desktop machines were on Wi-Fi for every
  run, so whatever the desktop has going for it, a wired link is not it. What
  it has is that the app stays running: discovery happens once at startup and
  the list then stays, so the app's behaviour under lossy conditions is never
  exercised. The startup wait is still there — it is simply paid once, and it
  is not discovery.

What I cannot explain is why the iOS and Android experience is so different so
many years after the first BluOS controller shipped.

---

## Finding an alternative

With the official app declared too frustrating to use, I decided to look for
alternatives.

### Requirements

**R1: Must work on Android.** It is not relevant to me if I cannot use it on my
Android phone. A browser variant may be acceptable.

**R2: A GUI with basic controls.** I want to be able to click on what I want to
search for, see album covers, and interact with players visually at a glance.

**R3: Manual player entry.** Auto discovery is a major pain point with the
official app. If I could enter the players manually and not depend on the
discovery mechanism, I would have been very happy with the official app.
Needless to say, I do not want to deal with forced auto discovery anymore.

**R4: Fast content browsing with sorting.** I spend a lot of time waiting for
Tidal playlists to load. I use my favourite songs on Tidal a lot, and being
able to pick the sorting to get them in the order I added them rather than in
alphabetical order is essential for me.

**R5: Search.** It must be possible to search Tidal in an easy and intuitive
way without the app crashing.

**R6: Grouping.** Grouping in the BluOS controller app is fairly reliable,
however it is not that easy to group players that do not show up. I use
grouping fairly often, so that feature must be present and easy to use.

**R7: Easy player selection.** I switch between players often, so it should be
easy to change to another player. On a side note: sometimes the official app
forgets which player I had selected when I open it again.

**Bonus 1:** working on Linux as well is a big plus. However, if it works fine
on Android only that is acceptable, as the status quo would remain unchanged
after years of Linux desktop use without a Bluesound app for control.

**Bonus 2:** list the playback queue.

---

### Full controller apps

**[BluOS NAD remote](https://github.com/crwsolutions/BluOsNadRemote)**: a very
good candidate. It easily checks off R1, R2 and R3. Browsing is possible but
not with custom sorting, making it just barely fail R4. Search is hard to find,
and I managed to make the app crash when I tried to search for something,
failing R5. I did not find any way to group players, and switching players
requires going to the settings, failing R6 and R7. The focus on NAD device
features that are unusable on Bluesound players, together with the lack of
features I need, means this app does not work out for me.

**[BlueSound Controller](https://github.com/rdOxalis/bluesoundplayer)**: a GUI
app that works on Android, ticking off R1 and R2. Manual player entry is not
possible, failing R3. This app implements its own discovery mechanism that
scans all networks as if they were /24 subnets, completely ignoring any subnet
definitions — which works fine as long as your network actually is a /24.
Detected players are removed automatically when the device is no longer
connected to the scanned subnet. With my players on a separate VLAN, this means
players are not visible. I moved my phone to a Wi-Fi network on the same VLAN
as the players, and discovered that the app is very basic. When players are
detected it is easy to switch between them and create groups, though actual
group creation was not tested, as I found no way to do content browsing or
search. That ticks off R7 and maybe R6, but fails R4 and R5.

**[BluRemote](https://apps.apple.com/dk/app/bluremote-bluos-controller/id6444855562)**:
Mac only, so it fails R1, and without a Mac I cannot even test it. Not
relevant.

### Home Assistant integrations

Unable to find any ready-to-use app, I considered using Home Assistant as my
BluOS controller. I found three integrations:

- [Home Assistant Core](https://github.com/home-assistant/core/tree/dev/homeassistant/components/bluesound)
- [bluesound_alt](https://github.com/aunefyren/bluesound_alt)
- [Pimmeke1989/bluos](https://github.com/Pimmeke1989/bluos)

The positives first: R1 and R2 are fulfilled, as Home Assistant has Android
apps and works in a browser. Players can be added manually, ticking off R3. As
a bonus, this works fine from Linux via the browser.

The interface via Home Assistant turns out to be clumsy — it takes many clicks
to get to the UI where I can control the players — and the integrations are
buggy when grouping players, so this solution fails R6 and R7. I could not find
any search, and at least with bluesound_alt I could not get it to show all the
songs in my Tidal collection, ultimately failing R4 and R5.

I tested most of the functionality with the bluesound_alt integration, and
while the other integrations might fix some of my problems, I know the Core
variant is mostly the same, and the last project looks like a two-day rush with
no sign of any development since. There is potential in using Home Assistant as
a core, but the UI is not great and I do not believe it can be much better than
what I have already seen. Home Assistant as the primary controller is out.

### Web interfaces

**[Kindofblu](https://github.com/mfit/kindofblu)** is very basic, clearly a
proof of concept, and has had no commits since 2020. Even so, R1, R2 and the
Linux bonus are easily fulfilled. I did not spin the app up to check anything
else.

**[Amp](https://github.com/great-horn/amp)** does the basics right, but lacks
Tidal search and there is no evidence of work on multi-player support. I did
not investigate this one in depth.

The BluOS players have a built-in web UI on port 80. In version 4.16.22 I only
found settings there, no player control.

### Other solutions

I have tried Roon, and it has always felt a bit off to me, especially
considering the price. I also remember that a feature I use a lot was missing
the last time I tried Roon.

I have not tested any voice assistant. Even if they did work great, they are
not a solution for me, as I prefer a written and visual format.

---

## Wishlist

Aside from the obvious —
[proper Linux support](https://support1.bluesound.com/hc/en-us/community/posts/360033533054-BluOS-controller-app-on-Linux)
and a reliable Android app — I have a handful of smaller annoyances and wishes
that matter much less than my primary motivation for starting this project:

1) On one of my players I use HDMI to get audio from my television. When HDMI
   audio plays, the playback queue is cleared, and I have to decide what to
   listen to next time I want to hear music. Being able to save the context of
   the playback queue and restore it on demand after HDMI playback would make
   it easier to return to a listening session after watching TV.

2) Moving playback between players does not always work. A Tidal "radio"
   restarts when moved. As a consequence, I usually create a group and then
   mute the master instead of moving the music. If it were possible to make the
   move reliable with Tidal track, album and artist radios, I would value that
   feature a lot more. The result is similar with Radio Paradise: it is as if
   playback simply stops on the source and the destination is then asked to
   start Radio Paradise. The new player might start an entirely different song,
   and the song I was listening to is interrupted and gone. Until that is
   fixed, I consider moving audio a broken feature, because I cannot trust the
   music to actually get moved.

3) Preset and sleep timer in one go. Maybe even an easy way to see whether the
   timer is active, like the Sonos app has.

4) Back up Tidal playlists. With BluOS having full access to my Tidal
   collection, why not use it as an easy way to back up my playlists?

5) The player list in the official apps shows very little about what each
   player is doing, aside from the topology and the volume. It would be nice to
   see playback status, and maybe even pause and start players, from the player
   overview — a quick overview rather than clicking into each player to see
   what it is doing. I am not sure how the UI for that should work, but one
   step at a time.

6) I often go to the same playlist, or the same menu within Tidal in BluOS.
   Presets cover part of this — a Tidal playlist can be saved as one, and so
   can a mix — but not the list I use most. My Music → Songs cannot be a
   preset: a preset has to point at something the service will play on
   request, and that list is offered for browsing only. A shortcut in the
   controller has no such constraint, because it only has to remember where I
   was going. Rather than keep clicking and waiting, why not have one — and
   build it so it is not limited to this one idea, but allows for any shortcut
   I might want in the future?

7) Presets belong to a player, not to me. I added one on a player yesterday
   and it was not there on another player today. What I want is the playlist I
   like being startable on whichever player I happen to have selected. In
   Musica it would not have to be a real BluOS preset at all — the idea is what
   matters, not the mechanism.

---

## The unofficial official Linux desktop

There is one more option, and it deserves an answer of its own: if the
community has already packaged the official desktop app for Linux, why is that
not enough?

[Bluesound acknowledged a request for an official Linux client in 2019](https://support1.bluesound.com/hc/en-us/community/posts/360033533054-BluOS-controller-app-on-Linux),
but as of 2026 there is still no official Linux client. There is a community
project that takes the official Windows Electron app and repackages it ready to
use on Linux as an AppImage:
[bluos-controller-linux](https://gitlab.com/zquestz/bluos-controller-linux). I
have tried it and it works *fine*; however, while it is much better than the
Android app, it is not free of the issues. I still notice the following
annoyances:

- Relatively slow discovery on app startup (5–6 seconds including app startup,
  roughly two to three of it discovery once the window is up). The official
  Windows build times the same, so this is not the repackaging, and the forced
  wait the Android app has looks like it is present here too. At least the app
  is not forced out of memory all the time as on Android, so discovery only
  needs to happen at startup.
- Unstable when left open for a long time or after standby, though recovery is
  fast.
- Using LSDP requires a firewall opening, and keeping a UDP port open just for
  this app seems like an ugly solution. Still, mDNS works much better on the
  desktop than in the Android app, so there is not much need for it.

Having an extra browser running (Electron) and the slow-ish startup is less
than ideal, but as the app is the official Windows client, I assume it is
feature complete and about as fast as an official Bluesound client can be. The
power consumption of the Linux app is not bad; it is like any other browser —
you notice it when you look at it, but it uses almost nothing when you don't.
It is a fantastic community project, and I am only sorry that I discovered it
as part of the research I did for creating Musica.

It might seem hypocritical to be unhappy about something that works 99% of the
time. The Linux desktop app does not solve all the problems I have on Android,
and it carries over some of them. I have decided to solve the problems with the
Android app on my own, and in my own solution I will include several things I
wished were different in the official app. Why limit those quality-of-life
improvements to my phone? I do not see any good argument, so I am targeting a
solution that works on both Android and Linux with as much shared code as
possible.

I found evidence that it might be possible to make the desktop app start with a
static list of players. It is good to know that if the choice comes up where
supporting both desktop and mobile becomes very hard, an Android-only focus
might be acceptable.

---

## Conclusion

There is a wide ecosystem with many interpretations of how it makes sense to
interact with BluOS. Every player speaks plain HTTP with XML bodies over the
LAN. No TLS, no handshake, no binary framing, no token exchange, no cloud round
trip. Anything that can make an HTTP request can control a player.

With none of the existing Android options matching my needs, this project will
be one more entry in the collection of software out there that kind of works
with BluOS.
