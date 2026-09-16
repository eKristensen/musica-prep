# Why Musica exists

This document describes the motivation for building Musica. It has two
parts: 1) several daily annoyances while using the official Android app,
and 2) the lack of an alternative to the official app that meets my
requirements.

---

## Open ends — working notes, delete before publishing

Things the argument does not close yet. The first four could still end with
nothing being built, which is the outcome I would rather have.

1. **Ask Bluesound.** The document says I never did, and gives "it can be hard
   to prove where the problem lies" as the reason. That reason no longer holds:
   there is a controlled comparison (iPhone against Android, same access point,
   same players), a toggle that makes the delay come and go on the same cable,
   and twenty rounds of on-wire timings showing the protocol is not at fault.
   That is a better bug report than most vendors get. Cheapest way to not build
   anything.
Note: Bluesound-ticket.txt has been sent on September 16, 2026.

2. **Fixing an existing project is never considered.** The survey asks whether
   each candidate meets the requirements and moves on when it does not. It
   never asks whether one could be fixed. BluOS NAD remote is open source, on
   Android, and fails on sorting, search and grouping. Amp is open source, web,
   and fails on search and multi-player. Adding sorting to something that
   exists may be less work than a server plus a frontend. If the answer is that
   I do not want to adopt someone else's stack, that is a decision worth
   writing down rather than leaving unasked.

3. **Four candidates were never actually run.** Kindofblu was never started,
   Amp was not looked at in depth, BluRemote could not be tested without a Mac,
   and the Home Assistant Core integration was dismissed as "mostly the same"
   as bluesound_alt without being tried. Amp is the one I would test first: it
   is a web interface, so R1, R2 and the Linux bonus come free, and the
   multi-player judgement is a guess from the repository rather than a result.

4. **A whole ecosystem category is missing from the survey.** ECOSYSTEM.md
   lists CLIs and TUIs, and BluOS Dashboard, none of which appear here. R2
   rules CLIs out by definition, but that is never said, so a reader comparing
   the two files finds a dozen unaddressed projects. BluOS Dashboard is worth
   an actual look before dismissing; the name does not sound like a CLI.

5. **The document never argues that Musica fixes any of this.** Eight problems,
   a requirements filter nothing passes, and then a conclusion about being one
   more entry in the collection. A reader never learns that holding state on a
   server means no discovery at launch, no staleness timer dropping players,
   and that manual addresses mean no discovery at all. README says it; this
   document does not.

6. **An argument I am not making.** If Bluesound fixed Android tomorrow, R4 and
   R5 would still be unmet. The browsing half of the motivation survives the
   best case of item 1, and neither a bug report nor a fork reaches it. That
   strengthens the case and is currently left out.

7. **Desktop is a preference, not a need,** by my own evidence: the AppImage
   works, the startup wait is paid once, the list stays put. The document
   half-concedes this and then argues past it. Saying it plainly costs nothing.

In the hardware section, before it goes public: the Onkyo bankruptcy claim
needs a date and ideally a source, the Roon discovery claim is load-bearing for
rejecting Roon and should be backed, and WiiM is listed as evaluated without a
reason — that lineup moves fast on room correction, so it is worth recording
which models were considered and when. Also, when that section is merged, its
hardware requirements must not end up reading as R8 onwards; they are a
different kind of thing from the controller requirements.

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

### What the measurements show

The wait breaks into three parts, and only one of them can be removed.

- **About a second and a half belongs to the app.** Putting a responder on the
  network that answers discovery queries instantly does not shorten it, so
  nothing done to the network will.
- **Two to four seconds sit on top whenever the Wi-Fi radio is enabled**, even
  with a cable attached and the radio carrying none of the traffic. The
  incomplete lists live here too: over Wi-Fi roughly one attempt in five comes
  back short of all four players, and with the radio switched off I have not
  seen that happen once.
- **The discovery protocol contributes none of it.** Queried from a wired
  machine on the same network, all four players answer within about
  three-quarters of a second, in every one of twenty rounds. That finishes well
  inside the app's own floor.

**The list does not hold what it finds.** Probing stops ten to twelve seconds
after the player screen opens (observation 1), and a player nobody probes
announces itself only about once a minute. Between the two there is a long
window in which nothing refreshes an entry, which is what observations 2 and 3
look like from the outside. Observation 7 is the same thing across a restart —
a screen that has just found every player, then a screen showing one.

**Two discovery protocols are in use** — mDNS, and a Lenbrook-specific UDP
broadcast protocol (LSDP). Lenbrook has been reported as saying they wrote
their own because
[their customers cannot be relied on to configure their networks](https://content-bluesound-com.s3.amazonaws.com/uploads/BluOS-Custom-Integration-API_v1.7.pdf),
a statement that goes back
[as far as 2020](https://web.archive.org/web/20210120042844/https://nadelectronics.com/wp-content/uploads/2020/12/Custom-Integration-API-v1.0_Dec_2020.pdf).
A developer who implemented both protocols in 2022 found the BluOS mDNS
announcements slow and unreliable, which matches what I see years later
([reference](https://blog.jonasbengtson.se/lsdp-lenbrook-service-discovery-protocol)).
Neither protocol is the bottleneck, but two of them means more than one
mechanism can add or remove a player from the list.

**Why iOS is different.** I captured traffic and the iOS controller sends the
same UDP broadcast discovery packets, so both platforms use both mechanisms. An
iPhone and an Android phone on the same Wi-Fi, through the same access point,
to the same players, then behave completely differently. One variable changed
and the outcome flipped, so it is not the protocols, the players, the network,
the access point, or Wi-Fi as a medium.

**Why desktop is different.** Both desktop machines were on Wi-Fi for every
run, so whatever the desktop has going for it, a wired link is not it. What it
has is that the app stays running: discovery happens once at startup and the
list then stays, so the app's behaviour under lossy conditions is never
exercised. The startup wait is still there — it is simply paid once, and it is
not discovery.

**There is a configuration in which the official app is fine.** A cable, with
the Wi-Fi radio switched off, gives all four players in about a second, every
time. That is a real result and it is not a solution: a phone is a phone
because it is not plugged into anything, and an adapter I have to carry and a
radio I have to remember to disable is a worse daily experience than the
problem it fixes. It does tell me the app can be fast, and that what stands
between me and that speed is not my network.

What I cannot explain is why enabling a radio that carries none of the traffic
costs several seconds, or why none of this happens on iOS, so many years after
the first BluOS controller shipped.

---

## Finding an alternative

With the official app declared too frustrating to use, I decided to look for
alternatives. The full list of alternatives found can be seen in
[ECOSYSTEM.md](ECOSYSTEM.md).

### Scope (TODO: This is my way to solve open end number 2, 3 and 4. Does it work? Does it make sense to keep seperate from Requirements?)

In order for an alternative to be interesting it must fulfill som basic requirements. This is what the project need to do before I even consider the project as a candidate:

- Be alive. There must be some activity or evidence that the project is activly developed. Example elemination: 2+ years since last commit, fewer than 10 commits in general, single arthur.
- Look like it can be a controller replacement. Many projects go out to solve one very specific narrow task. I need more. Example eleminations: Dashboards, single purpose tools, libaries that do not form a controller on their own.

Several candidates from the [ECOSYSTEM.md](ECOSYSTEM.md) list are eleminated based on these two requirements. As the ecosystem is huge it would take a lot of time to argue against projects that trivially does not meet the requirements above, therefore there are specific arguments for projects not considered below. All projects not mentioned below can be assumed to not have passed the requirements above.

### Requirements

**R0: Be at least as stable as the official BluOS Controller** While the discovery mechanism is frustrating the official app does never crash, my phone heat up, spend too much battery power or lock up. This is hard to judge. Any crashes must be evaluated but most likely it will be deemed unacceptable. 

**R1: Must work on Android.** It is not relevant to me if I cannot use it on my
Android phone. A browser variant may be acceptable.

**R2: A GUI with basic controls.** I want to be able to click on what I want to
search for, see album covers, and interact with players visually at a glance.
Listing the current playback queue is a nice bonus to R2, but not a requirement.

**R3: Manual player entry.** Auto discovery is a major pain point with the
official app. If I could enter the players manually and not depend on the
discovery mechanism, I would have been very happy with the official app.
Needless to say, I do not want to deal with forced auto discovery anymore.

**R4: Fast content browsing with sorting.** I spend a lot of time waiting for
Tidal playlists to load. I use my favourite songs on Tidal a lot, and being
able to pick the sorting to get them in the order I added them rather than in
alphabetical order is essential for me.

**R5: Search.** It must be possible to search Tidal in an easy and intuitive
way.

**R6: Grouping.** Grouping in the BluOS controller app is fairly reliable,
however it is not that easy to group players that do not show up. I use
grouping fairly often, so that feature must be present and easy to use.

**R7: Easy player selection.** I switch between players often, so it should be
easy to change to another player. On a side note: sometimes the official app
forgets which player I had selected when I open it again.

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

---

# Why Bluesound?

With the official android app discovery mechanism in chaos why stick around with
Bluesound? See [WHY_BLUESOUND.md](WHY_BLUESOUND.md).

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

With none of the existing Android options matching my needs as is, the next
step is to consider how to build a new solution that meet the requirements. See
[DESIGN_PRINCIPLES.md](DESIGN_PRINCIPLES.md).
