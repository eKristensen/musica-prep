# Why Musica exists

This document describes the motivation for building Musica. It has two
parts: 1) several daily annoyances while using the official Android app,
and 2) the lack of an alternative to the official app that meets my
requirements.

It describes the situation as of September 2026, on firmware 4.16.22 with
BluOS Controller 4.16.2 and 4.16.3. Everything dated here — the measurements,
the state of the projects I looked at, what has and has not been fixed — is a
record of that moment rather than a standing claim.

---

## Open ends — working notes, delete before publishing

What the argument still does not close.

1. **Waiting on Bluesound.** The support ticket went in on 16 September 2026.
   If it comes back with a fix, or a reason, most of this document changes.
   Nothing else here is worth finishing until there is an answer or a decent
   interval of silence.

2. **Two decisions are promised to `DESIGN_PRINCIPLES.md` and have to actually
   land there:** whether to build on somebody else's project rather than start
   over, and whether one solution should cover both desktop and phone. The
   first is pointed at from here, so a dangling pointer is worse than the gap
   was. The second is no longer mentioned in this document at all.

3. **One elimination rests on an assumption rather than on the scope tests.**
   The Home Assistant Core integration is dismissed as "mostly the same" as
   bluesound_alt. That is probably right, and it is not demonstrated.

4. **`WHY_BLUESOUND.md` needs its claims dated and sourced before it is
   public** — the Onkyo bankruptcy, the Roon discovery problems, and which WiiM
   models were considered and when.

---

## My setup

- Four Bluesound players (2 x N132, 1 x N130 and 1 x N110) on a dedicated VLAN.
- mDNS reflection configured between VLANs.
- UDP replication for the LSDP protocol across VLANs.

---

## My challenges with the BluOS Controller for Android

The common element in my problems is the player discovery mechanism in the
official BluOS Controller for Android. Discovery there is asynchronous,
distributed and spread across two protocols, which makes it hard to prove
where the fault lies. I know nobody else running Bluesound with Android
phones who could tell me whether it is specific to my setup.

---

### 1. Discovery is forgetful, slow and unreliable

There is always a delay before the first player appears, and usually another
wait before the rest arrive. The app seems to be in search mode for a fixed
amount of time, and any player that does not answer inside that search window
never appears at all. On Wi-Fi a lost broadcast or multicast frame is common
enough for that to happen regularly. Backing out of the player list and
re-entering is the only way to trigger another attempt.

Worse, the whole process has to be repeated as soon as the app stops running
actively — after the lock screen, or after using the phone for something else.
In essence the app appears to have no memory. If discovery were fast that would
not matter, but it is not.

**Impact:** it easily takes ten to fifteen seconds before I can do anything
with my players. I often find myself opening the app, putting the phone down
to do something else, and coming back hoping the players I need this time have
turned up. I gave up expecting all four a long time ago.

### 2. The player list and the topology are unreliable

**Players sometimes disappear and come back.** A player that is present and
playing sometimes vanishes from the list for a while and then returns, with no
action on my part. Even the currently selected player can disappear — while I
am still controlling it, with play, pause and volume all working, it is simply
absent from the list.

**Partial lists that differ depending on what you select.** With several
players and groups, selecting one player sometimes shows one subset; selecting
another shows a different subset.

**A new group is not shown as a group.** Sometimes when I create a player
group, the player list does not change for several seconds even though the
group has formed.

**Ungrouping leaves a player unusable for a while.** After removing a player
from a group, that player often cannot be selected for about ten to twenty
seconds. The app behaves as though it is still a group member for a short
while, even though the player itself has already left the group. Ungrouping
sometimes makes other players vanish from the list too, including players that
were not part of the group I was changing.

**Impact:** it makes grouping harder than it needs to be. The list reflows as
players come and go, so the entry under my thumb can change between the moment
I decide to tap and the moment the tap registers, and I end up grouping a
player I did not mean to. Removing the wrong one then locks up the player
list, which often makes players disappear, which in turn means more waiting.
And because a group that has formed does not always show up as one right
away, I make it again to no effect, and a genuine failure to group is hard to
tell apart from a player list that is simply out of date. When the selected
player is the one that vanishes, which happens far too often, grouping becomes
awkward for a simpler reason: a player I cannot see is a player I cannot
group. Recovery means backing out of the player list and
re-entering, waiting through discovery again and retrying. Controlling a
player that the app does not show is hard, and because most actions on the
player list screen change what that screen shows, it is not a pleasant screen
to use.

### 3. The app opens with a different player selected

Sometimes the app comes back with a different player selected than the one I
was using when I closed it. Nothing I did changed the selection; it changes on
its own between one session and the next.

**Impact:** getting back to the player I actually wanted means going through
the list, and so through the slow and unreliable discovery process.

### 4. A full rediscovery whose results are then thrown away

Occasionally the app opens with a message saying BluOS lost connection to my
player, and the normal interface is replaced by a full-screen discovery view.
I waited through it once: it found every player, slowly, one at a time, and
then the normal interface appeared — showing **only** the player I had selected
before closing the app. Everything the previous screen had just found was gone,
and had to be discovered again from scratch.

**Impact:** it is hard to see what the first discovery accomplished, and
nothing else has done as much to make me distrust the code behind discovery in
this app. It is also the most conspicuous version of the problem, because the
app visibly finds all the players and then visibly forgets them a second later.

### 5. The app refuses to work over VPN, even though the network works

Over VPN the app sometimes works for a while, and then stops for no apparent
reason. I can still reach the players' own web interface through the tunnel
throughout. The restriction appears to be based on connection type rather than
on whether the players are actually reachable.

**Impact:** if I forget to pause the music before leaving home, my only native
option is to reboot the player from its web UI, which is hardly elegant. The
case that bites most often is forgotten Tidal playback, which then blocks Tidal
on my phone while I am out. It also makes it impossible to build an
alternative, potentially more stable, path for the discovery packets over VPN.

### Two discovery protocols

The players are discovered using two protocols: mDNS, and a Lenbrook-specific
UDP broadcast protocol (LSDP). Lenbrook has been reported as saying they wrote
their own because
[their customers cannot be relied on to configure their networks](https://content-bluesound-com.s3.amazonaws.com/uploads/BluOS-Custom-Integration-API_v1.7.pdf),
a statement that goes back
[as far as 2020](https://web.archive.org/web/20210120042844/https://nadelectronics.com/wp-content/uploads/2020/12/Custom-Integration-API-v1.0_Dec_2020.pdf).
A developer who implemented both protocols in 2022 found the BluOS mDNS
announcements slow and unreliable, which matches what I see years later
([reference](https://blog.jonasbengtson.se/lsdp-lenbrook-service-discovery-protocol)).
Neither protocol is the bottleneck, but having two of them means more than one
mechanism can add or remove a player from the list.

### The iOS BluOS Controller is faster and more reliable

The BluOS controller on an iPhone, on the same network, through the same access
point, to the same players, shows all four immediately and keeps them.
Restarting the app, reloading, refreshing, closing it and opening it again from
the home screen — whatever I do, the list is there and it is complete. I have
confirmed with packet captures that the iOS app uses both mDNS and LSDP to
discover players.

What I have tested hardest on iOS is exactly that: cold starts, and whether the
player list fills. I have also tried grouping and ungrouping there, though only
briefly — I could not provoke any of the trouble I run into regularly on
Android, and it was noticeably smoother, but a short session is not daily use.
I have not lived with the iPhone as my everyday controller, so the rest of the
problems above are untested there rather than absent.

When a group is formed on iOS, the players appear grouped instantly. The
Android app is often fast, but never that immediate. On iOS a group can also be
broken apart without selecting it first, which means fewer steps when
rearranging groups. Say I have two groups of two and want to add a player
from the other group to the one I am using: on iOS I can break the other group
apart without selecting it, then add the player directly. On Android, changing
the other group means selecting it first, which often triggers the problems
described above.

---

### What I ruled out

I want to be fair about this, because "it's your network" is the natural first
response and in many cases it would be correct.

- **Not mDNS reflection.** Reproduced with the phone on the same VLAN as the
  players.
- **Not missing or slow mDNS records.** I published static IPv4 host and
  service entries. None of the phones behaved measurably better for it: still
  the last-connected player first, then a pause, then the rest.
- **Not slow LSDP discovery.** Serving static LSDP records instantly, from a
  central service rather than from the players, does not make the list appear
  any sooner. It does make it slightly more often complete — players arrive
  together rather than one at a time — but not by enough to change anything in
  practice, and simple tests suggest that even a more stable version of it
  would not.
- **Not the players.** They respond promptly to direct HTTP requests
  throughout, including while the app shows them as missing.
- **Not one bad player.** The problems move around between players rather than
  sticking to one.
- **Not one bad Android device.** Three phones from three manufacturers, on
  Android 11, 12 and 15, all behave the same way. So does the app under
  Waydroid on a fourth Android version, with no Google Play at all.
- **Not mobile data or cellular.** Two of the three phones have no cellular
  radio at all and behave the same as the one that has. On that one, airplane
  mode with Wi-Fi switched back on — Wi-Fi up, no mobile data — changed nothing
  across four runs.
- **Not one access point, switch, router or firmware.** The same behaviour has
  followed me across several access points, switches and routers, and many
  firmware versions, over a long period.
- **Not general network health.** A wired machine on the same network sees the
  discovery traffic and resolves the players quickly and consistently over both
  mDNS and LSDP. Wired and wireless players are indistinguishable in response
  time.
- **Not Android app settings.** The app has unrestricted background usage, is
  exempt from battery optimisation, and has been granted the location
  permission it asks for. The usual OS restrictions are not what is in the way.
- **A better app exists.** On the same network the iOS app on an iPhone is much
  more reliable than any of the four Android devices I tried. The mix of mDNS
  and LSDP is not a problem for the iOS app.

Some of my family use Sonos, and discovery on Android is rock solid there. I
wonder why the BluOS Controller on iOS is so much more reliable than the one on
Android, and why I cannot get a reliable experience on Android with Bluesound.

---

### BluOS Controller for Android measurements

I measured on three Android phones from different manufacturers and one
virtualised Android instance, both on the same L2 network as the players and on
a separate VLAN with an mDNS and LSDP relay carrying the player information
across. The results vary very little between runs and consistently show the
same pattern.

The test is meant to reproduce how I meet the app most often: pulled back open
after having been closed for a while. 1) Swipe the BluOS Controller closed,
2) open it again, 3) press the player list icon, 4) measure the time until the
players show. Each scenario was repeated five times. Time to a full player
list:

- A wired Android device without Wi-Fi, or with Wi-Fi turned off: between 1.0
  and 1.5 seconds.
- A wired Android device with Wi-Fi turned on but not connected: between 3 and
  5 seconds.
- A Wi-Fi connected Android device: between 3 and 5 seconds.

The interesting part is that having Wi-Fi turned on increases the wait even
when the device is on a cable and the radio carries none of the traffic. The
wait breaks into two parts:

- **About a second and a half belongs to the app.** Putting a responder on the
  network that answers discovery queries instantly does not shorten it, so
  nothing done to the network will.
- **Two to four seconds sit on top whenever the Wi-Fi radio is enabled**, even
  with a cable attached and the radio carrying none of the traffic. The
  incomplete lists live here too: over Wi-Fi roughly one attempt in five comes
  back short of all four players, and with the radio switched off I have not
  seen that happen once.

---

## Finding an alternative

Having decided the official app was too frustrating to keep using, I went
looking for alternatives. The full list of alternatives found can be seen in
[ECOSYSTEM.md](ECOSYSTEM.md).

### Scope

The ecosystem is large. Before a project is worth measuring against the
requirements below, it has to clear two much lower bars:

- **Be alive.** There must be activity, or some evidence that the project is
  actively developed. Examples of elimination: more than two years since the
  last commit, fewer than ten commits in total, a single author.
- **Look like it could replace a controller.** Many projects set out to solve
  one narrow task, and I need more than that. Examples of elimination:
  dashboards, single-purpose tools, and libraries that do not amount to a
  controller on their own.

Most of the [ECOSYSTEM.md](ECOSYSTEM.md) list falls at one of those two, and
arguing against each project individually would take far longer than it is
worth, so I do not. Any project not discussed further down can be taken to
have failed one of the two tests above.

---

### Requirements

What survives that first cut is then measured against what I actually need.

**R1: At least as stable as the official BluOS Controller.** Frustrating as its
discovery is, the official app never crashes, never makes my phone heat up,
never drains the battery and never locks up. This one is hard to judge in
advance, so any crash has to be weighed on its own — but most of them will be
disqualifying.

**R2: Must work on Android.** An alternative is not relevant to me if I cannot
use it on my Android phone; if I moved to an iPhone I would not be looking for
one at all. A browser variant may be acceptable — but not the players' own: the
web UI on port 80 exposes settings only, with no playback control, so there is
no vendor-provided way to control a player without an official app.

**R3: A GUI with basic controls.** I want to be able to click on what I want to
search for, see album covers, and interact with players visually at a glance.
Listing the current playback queue is a welcome bonus here, not a requirement.

**R4: Manual player entry.** Auto discovery is a major pain point with the
official app. Were I able to enter players by hand and not depend on discovery
at all, I would have been perfectly happy with it. Needless to say, I do not
want to deal with forced auto discovery any more.

**R5: Content browsing with sorting.** I spend a lot of time waiting for
Tidal playlists to load. I use my favourite songs on Tidal a lot, and being
able to pick the sorting to get them in the order I added them rather than in
alphabetical order is essential for me.

**R6: Search.** It must be possible to search Tidal or my own music collection
in an easy and intuitive way.

**R7: Grouping.** I use grouping fairly often, so that feature must be present
and easy to use.

**R8: Easy player selection.** I switch between players often, so it should be
easy to change to another player.

---

### Full controller apps

**[BluOS NAD remote](https://github.com/crwsolutions/BluOsNadRemote)**: a very
good candidate. It easily checks off R2, R3 and R4. Browsing is possible but
not with custom sorting, making it just barely fail R5. Search is hard to find,
and I managed to make the app crash when I tried to search for something,
failing R1 and R6. I did not find any way to group players, and switching
players requires going to the settings, failing R7 and R8. The focus on NAD
device features that are unusable on Bluesound players, together with the lack
of features I need, means this app does not work out for me.

**[BlueSound Controller](https://github.com/rdOxalis/bluesoundplayer)**: a GUI
app that works on Android, ticking off R2 and R3. Manual player entry is not
possible, failing R4. This app implements its own discovery mechanism that
scans all networks as if they were /24 subnets, completely ignoring any subnet
definitions — which works fine as long as your network actually is a /24.
Detected players are removed automatically when the device is no longer
connected to the scanned subnet. With my players on a separate VLAN, this means
players are not visible. I moved my phone to a Wi-Fi network on the same VLAN
as the players, and discovered that the app is very basic. When players are
detected it is easy to switch between them and create groups, though actual
group creation was not tested, as I found no way to do content browsing or
search. That ticks off R8 and maybe R7, but fails R5 and R6.

**[BluRemote](https://apps.apple.com/dk/app/bluremote-bluos-controller/id6444855562)**:
Mac only, so it fails R2.

### Home Assistant integrations

Unable to find any ready-to-use app, I considered using Home Assistant as my
BluOS controller. I found three integrations:

- [Home Assistant Core](https://github.com/home-assistant/core/tree/dev/homeassistant/components/bluesound)
- [bluesound_alt](https://github.com/aunefyren/bluesound_alt)
- [Pimmeke1989/bluos](https://github.com/Pimmeke1989/bluos)

The positives first: R2 and R3 are fulfilled, as Home Assistant has Android
apps and works in a browser. Players can be added manually, ticking off R4. As
a bonus, this works fine from Linux via the browser.

The interface via Home Assistant turns out to be clumsy — it takes many clicks
to get to the UI where I can control the players — and the integrations are
buggy when grouping players, so this solution fails R7 and R8. I could not find
any search, and at least with bluesound_alt I could not get it to show all the
songs in my Tidal collection, ultimately failing R5 and R6.

I tested most of the functionality with the bluesound_alt integration, and I
went further with that one than with any other candidate: I forked it and
fixed its group playback before concluding that the remaining requirements
would never follow. Whether to build on somebody else's project rather than
start over is a decision in its own right, and it is taken in
[DESIGN_PRINCIPLES.md](DESIGN_PRINCIPLES.md) rather than here. The other two
might fix some of my problems, but the Core integration is mostly the same code
and Pimmeke1989/bluos looks like a two-day rush with no sign of development
since. There is potential in using Home Assistant as
a core, but the UI is not great and I do not believe it can be much better than
what I have already seen. Home Assistant as the primary controller is out.

---

## Why Bluesound?

With the official Android app's discovery mechanism in chaos, why stick with
Bluesound at all? See [WHY_BLUESOUND.md](WHY_BLUESOUND.md).

---

## Wishlist

Aside from the obvious —
[proper Linux support](https://support1.bluesound.com/hc/en-us/community/posts/360033533054-BluOS-controller-app-on-Linux)
and a reliable Android app — I have a handful of smaller annoyances and wishes
that matter much less than my primary motivation for starting this project:

1) Tidal playlist cache. I spend a lot of time waiting for static playlists to
   load. If I could use some sort of caching to make my Tidal playlists show up
   faster, and make them more searchable than they are now, it would be nice.

2) On one of my players I use HDMI to get audio from my television. When HDMI
   audio plays, the playback queue is cleared, and I have to decide what to
   listen to next time I want to hear music. Being able to save the context of
   the playback queue and restore it on demand after HDMI playback would make
   it easier to return to a listening session after watching TV.

3) Moving playback between players does not always work. A Tidal "radio"
   restarts when moved. As a consequence, I usually create a group and then
   mute the master instead of moving the music. If it were possible to make the
   move reliable with Tidal track, album and artist radios, I would value that
   feature a lot more. The result is similar with Radio Paradise: it is as if
   playback simply stops on the source and the destination is then asked to
   start Radio Paradise. The new player might start an entirely different song,
   and the song I was listening to is interrupted and gone. Until that is
   fixed, I consider moving audio a broken feature, because I cannot trust the
   music to actually get moved.

4) Preset and sleep timer in one go. Maybe even an easy way to see whether the
   timer is active, like the Sonos app has.

5) Back up Tidal playlists. With BluOS having full access to my Tidal
   collection, why not use it as an easy way to back up my playlists?

6) The player list in the official apps shows very little about what each
   player is doing, aside from the topology and the volume. It would be nice to
   see playback status, and maybe even pause and start players, from the player
   overview — a quick overview rather than clicking into each player to see
   what it is doing. I am not sure how the UI for that should work, but one
   step at a time.

7) I often go to the same playlist, or the same menu within Tidal in BluOS.
   Presets cover part of this — a Tidal playlist can be saved as one, and so
   can a mix — but not the list I use most. My Music → Songs cannot be a
   preset: a preset has to point at something the service will play on
   request, and that list is offered for browsing only. A shortcut in the
   controller has no such constraint, because it only has to remember where I
   was going. Rather than keep clicking and waiting, why not have one — and
   build it so it is not limited to this one idea, but allows for any shortcut
   I might want in the future?

8) Presets belong to a player, not to me. I added one on a player yesterday
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
have tried both it and the official Windows build, and as far as I can tell
they behave identically. It works *fine*, and it is much better than the
Android app without being free of its problems. These are the ones I still
notice:

- Slow to become usable: five to six seconds from launch, roughly two to three
  of that after the window is up. The official Windows build times the same, so
  this is not the repackaging, and the forced wait the Android app has looks
  like it is present here too. At least the app is not forced out of memory all
  the time as on Android, so discovery only needs to happen at startup.
- Unstable when left open for a long time or after standby, though recovery is
  fast.
- Using LSDP requires a firewall opening, and keeping a UDP port open just for
  this app seems like an ugly solution. Still, mDNS works fine, so there is not
  much need for it.

The desktop app can be given a file of static players. It does not make the app
usable any faster — discovery seems to run no matter what — but players listed
in that file show up even when they answer neither LSDP nor mDNS.

---

## Why I think I can build it

My main advantage is scope. Bluesound has to support every player they have
ever sold, on every phone, on every network, for every customer. I have to
support four players, one network, and the features I actually use. Almost
everything that makes their job hard is something I am allowed to skip.

I have a Master of Science degree in Computer Science, and the work I have done
and enjoyed most is networking, web applications and backend services. I have
not yet worked much with Android. I intend to play to my strengths and avoid
building things I cannot support or understand.

Every player speaks plain HTTP with XML bodies over the LAN. No TLS, no
handshake, no binary framing, no token exchange, no cloud round trip. Anything
that can make an HTTP request can control a player.

AI lets me write more code than I otherwise could in the same amount of time. I
expect to spend most of my time on this project writing project descriptions
and reviewing code.

---

## I hope Bluesound fixes the Android app

I would rather not have to fix this myself. If the Android app stopped losing
players I would most likely leave this project wherever it had got to and go
back to the official app. What is on my wishlist would be a welcome addition
to a controller I was already building; it is not a reason to build one.

---

## Conclusion

The official app clearly has problems; what is not clear is where they come
from. The BluOS ecosystem is wide, and full of different ideas about what
interacting with BluOS should look like. With none of the existing Android
options matching my needs as they stand, the next step is to consider how to
build something that meets the requirements.
