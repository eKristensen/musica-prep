# Why Musica exists

This document describes the motivation for building Musica and consists of two
major types of motivation: 1) Several daily annoyances while using the official Android app and 2) a lack of an alternative to the official app that fulfill my requirements.

---

## My setup

- Four Bluesound players (2 x N132, 1 x N130 and 1 x N110) on a dedicated VLAN.
- mDNS reflection configured between VLANs, verified working — `avahi-browse`
  on a laptop resolves the players quickly and reliably.
- UDP replication for the LSDP protocol across VLANs.

---

## My Challenges with BluOS Controller for Android

A summary of the problems I run into with the official Android app running on
a smartphone.

I have not asked Bluesound to solve any of these problems and I do not know
anyone else with Bluesound using Android to check whether the problem is just
on my setup. Due to this I do not whether I am the only one with these
problems. The discovery mechanism Bluesound use is fairly complex and it can be
hard to prove where the problem lies. I decided I would rather build look for
another solution than trying to get Bluesound to acknowledge any of these
problems.

I have only been able to replicate the problems with the official app an
Android phone. Windows and iOS apps does not appear to have the problems when
I test in my setup.

---

### 1. Discovery is a slightly delayed short burst, then silence

Watching UDP traffic while opening the player list, the app waits for two
seconds then sends a small number of discovery probes over roughly the first
ten to twelve seconds, and then stops. After that it appears to listen
passively only.

**Impact:** there is almost always a delay before all players show up and a
player that doesn't answer within that window — because a broadcast frame was
lost, which on Wi-Fi is common — does not appear at all. Waiting doesn't help.
Backing out of the player list and re-entering is the only way to trigger
another attempt.

### 2. Players sometimes disappear and come back

A player that is present and playing sometimes vanish from the list for a while
and then return, with no action on my part. Blocking a player's HTTP port (to
simulate it) and timed it, the entry disappears after roughly fifteen seconds.
Normal status updates appear to arrive on a cycle of about ten seconds, so the
margin between "healthy" and "removed" is only a few seconds. Any hiccup — a
roaming event, a slow response, a moment of power saving — crosses it.

**Impact:** this is the single most disruptive issue. It makes the list feel
unreliable even when every player is online and reachable.

### 3. The currently selected player is sometimes missing from the list

I can be connected to a player, with working controls and volume,
while that same player is absent from the player overview. It appears later,
seconds after everything else.

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
players by other means throughout - e.g. built in player web UI. The
restriction appears to be based on connection type rather than on whether the
players are actually reachable.

**Impact:** no remote control of my own equipment on my own network, for no
technical reason I can identify. Furthermore, this make sit impossible to build
an alternative potentially more stable path for the discovery packages via VPN.

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

Restarting the iOS app, reloading, refreshing, closing and opening from the
home screen - no matter what I do players show up instantly and rock solid on
iOS. I wonder why I cannot get the same experience on Android.

I have family with Sonos. Discovery on Android for Sonos is rock solid.

---

### What I ruled out

I want to be fair about this, because "it's your network" is the natural first
response and in many cases it would be correct.

- **Not mDNS reflection.** Reproduced with the phone on the same VLAN as the
  players.
- **Not missing or slow mDNS records.** I published static IPv4 host and
  service entries with Avahi and confirmed from a laptop that they resolved
  quickly and consistently. Two android phone's from different vendors
  behaviour did not measurably improve: still the last-connected player first,
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
- **Not the app's logic.** Running the same Android app in a container on a
  wired laptop, discovery is instant and completely reliable.

  That last comparison is the most informative one. The same app, given a
  stable wired link and a network stack that isn't power-managing a radio,
  behaves perfectly. On a phone over Wi-Fi it does not. Wireless multicast
  loss and mobile power management are genuine constraints — but they are
  ordinary, expected conditions for a phone app, and the difference in
  behaviour suggests the controller has very little tolerance for them.

---

### What I think is going on

This section is interpretation rather than observation. I may be wrong about
the causes; the symptoms above are what I would stand behind.

**Short version:** the Android controller appears to keep its list of players
only while it is in the foreground, and to have several independent mechanisms
that can each add or remove a player from that list. Each of these most likely
have their own independent timings. The result is a list that is inconsistent
even when every player is online and reachable.

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
  [their customers cannot be relied on to configure their networks](https://content-bluesound-com.s3.amazonaws.com/uploads/BluOS-Custom-Integration-API_v1.7.pdf)
  [as early as 2020](https://web.archive.org/web/20210120042844/https://nadelectronics.com/wp-content/uploads/2020/12/Custom-Integration-API-v1.0_Dec_2020.pdf).
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
  players simply stay in the list. My guess is that the mDNS cache on iOS works
  better.

- **Why desktop is different.** Windows machines, and an Android container on a
  laptop, have no aggressive radio power management and no wireless multicast
  filtering. Discovery tends to succeed on the first attempt, so the app's
  behaviour under lossy conditions is never exercised.

What I cannot explain is why the iOS and Android experience is so different so
many years after the first BluOS controller shipped.

---

## Finding an Alternative

With the official app declared too frustrating to use I decided to look for alternatives.

---

### Requirements

**R1: Must work on Android**: It is not relevant if I cannot use it on my Andorid phone. A browser variant can maybe be acceptable.

**R2: A GUI with basic controls**: I want to be able to click on what I want to search for, see album covers and interact with players in a quick glance visually.

**R3: Manual player entry**: Auto discovery is a major pain point with the official app. If you could enter the players in the official app manually and not depend on the discovery mechanism I would have been very happy with the official app. Needless to say I do not want to deal with forced auto discovery anymore.

**R4: Fast content browsing with sorting**: I spend a lot of time waiting for Tidal playlists to load. I use my favorite songs on Tidal a lot, and being able to pick the sorting to get them in the order I added them rather than alphabetical order is essential for me.

**R5: Search**: It must be possible to search Tidal in an easy an intuitive way without having the system crash.

**R6: Grouping**: Groupping in the BluOS controller app is faily reliable, however it is not that easy to group players that do not show up. I use groupping fairly often so that feature must be present and easy to use.

**R7: Easy player selection**: I switch between players often, it should be easy to change to another player. On a side note: Sometimes the official app forgets which player I have selected when i open it again...

**Bonus 1**: If the it can also work on Linux it is a big plus. However, if it works fine on Android only it is acceptable as the status quo will remain unchanged with years of Linux Desktop without Bluesound app for controls.

**Bonus 2**: List playback queue.

---

### Full controller apps

**(BluOS NAD remote)[https://github.com/crwsolutions/BluOsNadRemote]**: A very good candidate: Easily checks off R1, R2 and R3. Browsing is possible but not with custom sorting giving making it just barely fail R4. Search is hard to find and I managed to make the app crash when I tried to search for something failing R5. I did not find any way to group players and switching players requires going to the settings failing R6 and R7. With a focus on NAD device features unusable on Bluesound players and a lack of features I need means that this app does not work out for me.

**(BlueSound Controller)[https://github.com/rdOxalis/bluesoundplayer]**: An GUI app that works on Andorid ticking off R1 and R2. Manual player entry is not possible failing R3. This app implements it's own discovery mechanism that scans all networks as if they are a /24 subnet completly ignoring any subnet defintions - which works fine as long as your network actually is a /24. Detected players are removed automatically when the device is no longer connected to the scanned subnet. With my players on a seperate VLAN this means players are not visible. I moved my phone to a wifi on the same VLAN as the players and I discover the app is very basic. When players are detected it is easy to switch between them and create groups, though actual group creation was not tested as I found no way to do content browsing or search ticking off R7 and maybe R6, but failing R4 and R5. 

**(BluRemote)[https://apps.apple.com/dk/app/bluremote-bluos-controller/id6444855562]**: Mac only, fails R1 and without Mac I cannot even test the app. Not relevant

### Home Assistant integrations

Unable to find any ready to use apps I considered using Home Assistant as my BluOS Controller. I found three integrations:

* (Home Assistant Core)[https://github.com/home-assistant/core/tree/dev/homeassistant/components/bluesound]
* (bluesound_alt)[https://github.com/aunefyren/bluesound_alt] 
* (Pimmeke1989/bluos)[https://github.com/Pimmeke1989/bluos]

Let us take the positive first: R1 and R2 is fulfilled as Home assistant got Android apps and works in a browser. Players can be added manually ticking off R3. As a bonus this works fine from Linux via browser.

The interface via Home Assistant turns out to be clumsy, it takes many clicks to get to the UI where I can control the players and the integrations are buggy when groupping players means this solution fails to get R6 and R7. I could not find any search and at least with bluesound_alt I could not get it to show all my songs in my music in Tidal ultimately failing R4 and R7.

I tested most of the functionality with the bluesond_alt integration, and while the other integration might fix some of my problems I know the Core variant is mostly the same and the last project looks like a two-day rush with no sign of any development since. There is potential in using Home Assistant as a core, but the UI is not great and I do not belive it can be much better than what I have already seen. Home Assistant as the primary controller is out.

### Web interfaces

**(Kindofblu)[https://github.com/mfit/kindofblu]** is very basic, clearly a proof of concept and with no commits since 2020. Even then R1, R2 and Bonus Linux support is easily fulfilled. I did not spin up the app to check anything else though.

**(Amp)[https://github.com/great-horn/amp]** does the basics right, but lacks Tidal search and there is no evidence of work on multi-player support. I did not investigate this one in depth.

The BluOS players got a built in web UI on port 80. I only found settings in version 4.16.22, no player control here.

### Other solutions

I have tried Roon and it have always felt a bit off to me especially considering the price. I do remember a feature that I use a lot was missing the last time I tried roon.

I have not tested any voice assistant. Even if they did work great, they are not a solution for me as I prefer a written and visual format.

### Wishlist

Aside from the obivious: (Prober Linux support)[https://support1.bluesound.com/hc/en-us/community/posts/360033533054-BluOS-controller-app-on-Linux] and a reliable Android app I have a two annoynances that are much more minor than my primary motivation for starting this project:

1) On one of my players I use HDMI to get audio from my television. When HDMI audio plays the playback queue is cleared and I have to decide what to listen to next time I want to hear music. If it possible to somehow save the context of the playback queue and restore it on demand after HDMI playback, it would make it easier to return to my music listening session after watching tv.

2) Moving playback between players does not always work. A Tidal "radio" restarts when moved. As a consquence I usually create a group and then mute the master instead of moving the music. If it is somehow possible to make the move reliable with Tidal track/album/artist radio's then I would value that feature a lot more. The result is similar with Radio Paradise, it is like it just stops playback on the source and then asks the destination to start Radio Paradise playback. The result is that the new player might start an entirely different song and the song I listened to is interrupted and gone into the void. Until then I consider moving audio like a broken feature as I cannot trust the music to actually get moved.

3) Preset + sleep timer in one go. Maybe even the option to easily see whether the timer is active like the Sonos app does.

4) Backup tidal playlists. With BluOS having full access to my Tidal collection why not use it as an easy way to backup my playlists?

5) The player list in the official apps show very little info about what each player is doing aside from the tropology and volume. It would be nice to see playback status and maybe even pause/start players from the player overview. It would be very nice to have a quick overview rather than having to click on each individual player to see what they ar edoing. I am not sure how the UI for that will work, but one step at a time.

6) I often go to the same playlist, or the same menu within Tidal in BluOS. My most often used list is My Songs in Tidal. Rather than keep clicking and waiting why not have a shortcut to go there directly and maybe built it in a way so it is not limited to this idea right now, but allow for any short cut I might want in the future.


### Unofficial official Linux Desktop

While (Bluesound have acknoledged a request for an official Linux client in 2019)[https://support1.bluesound.com/hc/en-us/community/posts/360033533054-BluOS-controller-app-on-Linux] there are not yet in 2026 any official Linux client. There exist a commnity project that takes the official Windows Electron app and repackage it ready to use on Linux in an AppImage: (bluos-controller-linux)[https://gitlab.com/zquestz/bluos-controller-linux]. I have tried it and it works *fine*, however while much better than the Android app is it not free of the issues. I notice the following annoyancens still being present:

- Relativly slow discovery on app startup (5-6 secs including app startup). The forced wait time that the Android app got seems to be present on the unofficial Linux variant as well. At least the app is not forced out of memory all the time as on Andorid and discovery only needs to happen at startup.
- Unstable when open in long time/after standby, though recovery is fast
- Using LSDP requires a firewall opening, and it seems like an ugly solution to keep an UDP port open just for this app. Still, mDNS works much better on the desktop than Android app so there is not much need.

Having an extra browser running (Electron) and the slow-ish startup is less than ideal, but as the app is the official Windows client I assume it is feature complete and about as fast as it can be with an official Bluesound client. The power consumption of the Linux app is not bad, it is like any other browser: You notice it when you see it, but it uses almost nothing when you dont. It is a fantastic community project, sadly I only discovered as part of the reserach I did for creating Musica.

It might seem hypocritical, why am I unhappy about something that works 99%? The Linux Desktop app does not solve all the problems I have on Andorid, and it carries over some of the problems. I have decided to solve the problems with android app on my own, and in my own solution I will include several elements that I wished was different in the official app. Why limit my hopefully quality of life improvements from my wishlist to my phone? I do not see any good argument, thus I target a solution that works on both Android and Linux with as much shared code as possible.

I found evidence that it might be possible to make the desktop app start with a static list of players. It is good to know that if the choice comes up where it becomes very hard to support both desktop and mobile, then it might be possible to accept an Andorid-only foucs.

---

## Conclusion

There exists a wide ecosystem with many interpretations of how it would make sense to interact with BlueOS. Every player speaks plain HTTP with XML bodies over the LAN. No TLS, no handshake, no binary framing, no token exchange, no cloud round trip. Anything that can make an HTTP request can control a player.

With none of the existing andorid options matching my needs, my project will be one of many adding to the collection of the many kind of works with BluOS pieces of software out there.
