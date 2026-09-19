# Why Bluesound?

With the official android app discovery mechanism in chaos why stick around with
Bluesound? Why not find an alternative with a working Andorid app and be happy?

**THIS DOCUMENT IS NOT FINISHED AND IS NOT READY FOR AI REVEIW**

TODO:
- Look at Joplin notes. AI Summary to generate some of the text below removed the essence of my requirements
- Refer back to motivation.
- Verify the Roon citations against the live pages before publishing. The
  roonlabs.com domains were unreachable when the section below was written,
  so the Roon-official claims come from search summaries of those pages
  rather than the pages themselves.

#### My first Bluesound Player.

The first Bluesound player came because music playback from my old ThinkPad T530 did not work well. The audio playback had holes. I thought it was Jitter, so I tried an expensive AudioQuest JitterBug, but it did not make any difference so it was returned. Upon reflection I realized that a JitterBug could never have made any difference. The next step I tried was Chromecast Audio. It was much better than digital audio out of my T530, but it was disappointing. I could clearly hear when i turned down the volume the quality dropped. I ended up only using my amp to change the volume, but even then something felt off. A Chromecast is a small indpendent computer, but connecting to it is somewhat unreliable making it harder to use than it should be. I use Tidal and as i remember it I always had to wait for the Chromecast to show up, and it did not always start to play music. Even though the Chromecast was not a very good independent player I realized from using it that I liked having the music playback be independent of whatever I do on my computer. I want the music to just keep going always. I needed something more stable, something better, something that support at least as high resolution audio as the Chromecast, something that works independently. 

I looked at Sonos Connect and Bluesound Node. The hifi audio story matches what I wanted to acheive. The limit to 16bit/44.1 kHz felt off to me, I did not want to buy a new player to be limited by the specs. I was blown away, very happy with the sound quality and stability. With one player only many elements of the flawed discovery mechanism on Android does not matter as much. On top of that I cannot remember what my exact setup was. I used to have an iPhone, maybe I still used it back then. I used to have Windows on my laptop, so getting BluOS Controller up and running was tivial. I had issues, but all minor ones, mostly related to how local music files was loaded into Bluesound. I talked with the support and there was nothing they could do. Despite that I was happy.

#### Multi-Room audio-player system requirements

Years later I move to a place with more rooms and I want to build out the system. However at this point even with one player I wonder why the player is not just available in the app. It could take several seconds for my one player to show up, so I considered alternatives. In order to judge whether alternatives work for me I need to set up some requirements, and here is the list I end up using, slightly adjusted in hindsight to make my point more clear:

- Native support for high resolution audio
- Genuine hi-res multiroom sync
- Decent room correction built-in. Audassy on my Denon AVR 4308A works great, but with several players to get room sync, delays after the output of the player is not something that is easy to accept. OR a way to set delays to match room correction systems.
- Mature, stable, native Tidal implementation. Not Tidal Connect. Tidal Connect is not stable enough to use without frustration in my experience.
- Sleep timer
- I want to connect my own speakers and amplifiers. I want to avoid any more vendor lock-in that absolutely nessasary. If one day I want to change to something else I would like it to be as much of a drop-in replacement as possible.
- 12V trigger output to work with external amplifier
- HDMI eARC player

It turns out it was relativly easy to eleminate alternatives:

- **Roon**: the first candidate, and the only one actually run. It is
  hardware-agnostic and its per-zone delay survives grouping, which BluOS does
  not offer. Against that it has no room correction of its own, cannot use the
  HDMI eARC input as a source, replaces Tidal's radios with its own, discovers
  players by multicast only, cannot be given a player's address, is unsupported
  across VLANs, has no Linux client, and needs a second always-on x86 machine
  and a subscription. It moves the discovery problem rather than solving it.
  Examined at length below.

- **Sonos**: 

- **WiiM**: 

- **Denon HEOS** / **Yamaha MusicCast**: Too much vendor lock in. The multi room system here is to provide added value to existing products, it is not the core product. Bluesound is also vendor lock in for sure, but it is more of a stand alone product than any of these.


#### Roon, examined in detail

Roon was the first candidate and the only one taken as far as actually running
it. It is also the only alternative where the failure is worth writing down at
length, because it fails for reasons that look like solutions.

**Roon has been trialled twice and rejected twice.** Both times with a single
player, and before the living room needed HDMI eARC or multiroom that holds
sync against a picture. Neither rejection was written down, so each later round
started from scratch: install, subscribe, configure, discover the same
objections, cancel. The third evaluation was done on paper instead, which is
what this section is.

**The conditions have moved against Roon each time, not toward it.** The
requirement list has grown a television input, a room whose correction must
cover every source, and four players across VLANs. Every one of those is a test
Roon did not have to pass before and does not pass now. A fourth trial would
cost a subscription, an evening of setup, a machine to run the server on, and
would fail on requirements that can be checked without installing anything.
Spending it anyway is the mistake this section exists to prevent.

The short version: Roon fails in the living room, where the NODE serves films
and television as well as music, and it keeps the discovery problem in a
stricter form with no escape hatch. Two of the five problems in
[MOTIVATION.md](MOTIVATION.md) reproduce on it. The case for Roon is argued at
the end of this section rather than left out.

##### What Roon does better

These are real and are not disputed here.

- **Grouped zones keep their DSP, and each zone has a delay.** Roon's DSP
  engine stays active on grouped RAAT zones; it is disabled only for AirPlay,
  Sonos, Squeezebox, KEF, Devialet AIR and Meridian zones
  ([Roon KB](https://kb.roonlabs.com/DSP_Engine:_Disabled_During_Zone_Grouping)).
  With a per-zone resync delay in milliseconds
  ([Roon KB](https://help.roonlabs.com/portal/en/kb/articles/audio-setup-basics#Resync_delay)),
  that meets the second half of the room-correction requirement — the way to
  set delays that match an external correction system. It does not meet the
  first half; see below.
- **A sleep timer exists**, on any zone from any device, from the moon icon in
  the zone's volume popup
  ([Roon 1.7](https://blog.roonlabs.com/roon-1-7-sleep-timer/)). Only Roon ARC
  lacks one
  ([open request](https://community.roonlabs.com/t/sleep-timer-in-roon-arc/216705)).
- **Least lock-in of any candidate.** Roon is hardware-agnostic, and Roon Ready
  costs manufacturers nothing beyond the integration work and the certification
  process itself
  ([certification](https://community.roonlabs.com/t/roon-ready-certification/91655)).
  Replacing the players later would not mean replacing the controller, and the
  N110, N130 and N132 are all certified
  ([Bluesound on Roon](https://roon.app/en/partners/14/bluesound)). On the
  drop-in-replacement requirement Roon scores better than BluOS.
- **VPN works.** Roon Remote auto-discovers and streams over Tailscale with
  no extra configuration
  ([community](https://community.roonlabs.com/t/success-with-tailscale-vpn/166068)),
  and Roon documents Tailscale officially as the answer to CG-NAT
  ([Roon KB](https://help.roonlabs.com/portal/en/kb/articles/arc-and-tailscale-connect-to-roonserver-without-port-forwarding)).
  The BluOS app's refusal to work over a tunnel that demonstrably carries the
  traffic has no Roon equivalent.

##### How many of the documented problems repeat

| # | The problem with BluOS on Android, as numbered in `MOTIVATION.md` | On Roon |
|---|---|---|
| 1 | Discovery slow, and forgotten after the lock screen | **Repeats.** The Android remote loses its connection to the server when the phone wakes from a dark screen, and when the app has been in the background. Startup delays of 55 seconds are reported, and "waiting for Roon core" is a standing Android complaint |
| 2 | Players vanish from the list and come back | **Repeats.** Zones disappear intermittently, and after updates. Roon has a standing KB article for it |
| 3 | Opens with a different player selected | **No clear match.** Zone-switching and zone-persistence complaints exist, but nothing with this signature |
| 4 | Full rediscovery whose results are discarded | **No match found.** Roon has no equivalent two-stage discovery screen |
| 5 | Refuses to work over VPN | **Does not repeat.** See above |
| — | iOS reliable, Android not, same network | **Unproven.** Roon's Android and iOS clients both draw heavy complaint; see below |

Sources for the repeats:
[connection lost on wake](https://community.roonlabs.com/t/roon-remote-android-loses-connection-to-core/127567),
[daily disconnects](https://community.roonlabs.com/t/android-roon-remote-looses-connection-to-core-daily/61650),
[laggy to the point of uselessness](https://community.roonlabs.com/t/android-roon-remote-laggy-to-the-point-of-uselessness/256777),
[waiting for core](https://community.roonlabs.com/t/keep-getting-waiting-for-roon-core-on-android-remote/229002),
[55-second startup](https://community.roonlabs.com/t/slow-startup-of-roon-app-55-seconds/209073),
[freeze and hang at startup](https://community.roonlabs.com/t/android-remote-app-freeze-or-start-up-or-hang-issue/153162),
[zones sometimes disappear](https://community.roonlabs.com/t/zones-sometimes-disappear/120119),
[zones gone after an update](https://community.roonlabs.com/t/network-zones-disappeared-after-roon-update-ref-l9bl61/291006),
[Roon's own FAQ for it](https://help.roonlabs.com/portal/en/kb/articles/faq-why-did-all-my-zones-disappear).

**On whether Roon repeats the Android-versus-iOS asymmetry: it does not, as
far as this can be shown.** Roon's iOS client draws the same class of
complaint as its Android one, at the same volume — crashing on launch on both
iPhone and iPad, crashing on return from another app, losing the server every
minute or so
([crashes on launch](https://community.roonlabs.com/t/latest-roon-ios-remote-crashes-immediately-after-opening-on-both-iphone-and-ipad/234531),
[crashes on iPad, long thread](https://community.roonlabs.com/t/remote-crashes-on-ipad/187943),
[cannot connect to core](https://community.roonlabs.com/t/roon-remote-app-on-iphone-and-ipad-unable-to-connect-to-roon-core/141819)).
Roon's clients are unreliable on both platforms rather than on one.

The store ratings point the same way. As of September 2026 the BluOS
Controller scores 4.0 on Google Play and 4.4 on the App Store; Roon scores 3.4
and 3.6. Both apps rate lower on Android, but BluOS has the wider gap of the
two — 0.4 against 0.2 — and BluOS outscores Roon on both platforms. Star
ratings across two stores are a weak instrument, since the populations and the
rating cultures differ, but they do not support Roon having a specifically
Android-shaped weakness.

**What does hold** is that Roon's clients are no better than the BluOS one, and
rate worse. What does not hold is the neat story that Android is the common
cause. The asymmetry documented in `MOTIVATION.md` remains specific to BluOS,
and unexplained.

##### The requirements Roon does not meet

**Room correction is not built in.** Roon's DSP engine, MUSE, applies
convolution filters and parametric EQ, but it does not measure anything. There
is no microphone step, no guided setup, no equivalent of Audyssey or Dirac.
Producing a filter means measuring the room yourself with REW and a calibrated
microphone, or HouseCurve on an iPhone, or Acourate, or paying a calibration
service, and then importing the result
([Roon's own guide](https://blog.roonlabs.com/digital-room-correction/),
[REW guide](https://community.roonlabs.com/t/a-guide-to-advanced-room-correction-with-rew-and-rephase-using-convolution-filters/90990),
[HouseCurve](https://housecurve.com/docs/appnotes/roon)). Automatic room
correction is [an open feature
request](https://community.roonlabs.com/t/automatic-room-correction/131516).

So on "decent room correction built-in", Roon scores worse than Bluesound, not
better. The N132 and NODE ICON are Dirac Live Ready, with the filters applied
before the internal DAC so an external DAC gets the same benefit
([Bluesound](https://www.bluesound.com/eur/news/dirac-live-ready-now-available-on-select-bluesound-players)).
Dirac measures the room and builds the filter. Roon plays a filter somebody
else built.

Roon's engine is *more capable* and *less convenient* than Dirac for anyone
willing to own a measurement microphone. What it can apply is broad:
convolution from a zip of impulse responses matched to the source's sample rate
and channel layout
([Roon KB](https://kb.roonlabs.com/DSP_Engine:_Convolution)), parametric EQ with
shelves and low- and high-pass filters, so crossovers and subwoofer integration
can be built by hand, and Procedural EQ for per-channel curves, channel mixing
and phase inversion
([Roon KB](https://help.roonlabs.com/portal/en/kb/articles/dsp-engine-procedural-equalizer)).
The ceiling is set by the tool that made the filter, not by Roon: REW alone
produces minimum-phase IIR correction, where changing the magnitude drags the
phase with it, while Dirac Live is mixed-phase and corrects the time domain as
well
([comparison](https://www.minidsp.com/applications/digital-room-correction/dirac-live-vs-rew),
[how Dirac works](https://www.diymobileaudio.com/threads/how-dirac-live-works-a-mix-phase-filtering-iir-fir-approach-to-room-correction.421271/)).
Matching Dirac means REW plus rePhase for linear-phase FIR, or Acourate;
Dirac Live Bass Control and ART have no filter to export and cannot be
reproduced at all.

**But the decisive limit is not capability, it is scope.** Roon's DSP applies
to Roon's own playback and to nothing else. Dirac on the player sits in the
player's output chain, so it corrects every source the player has — Roon
included, and the television included. In the living room the NODE carries
films and television as well as music, and correction that stops working the
moment the source is the TV is not correction. Convolution also cannot be
applied while keeping DSD
([Roon KB](https://community.roonlabs.com/t/muse-and-dsd/280817)), and running
both engines at once would correct twice, so the choice is exclusive.

This is what settles the requirement. Roon's DSP is better at what it covers
and covers the wrong set of outputs.

**HDMI eARC is not usable as a source.** Roon has no concept of a hardware
input. It plays a library and streaming services to endpoints; an endpoint's
own analogue, optical or HDMI input is invisible to it. Line-in as a source has
been [requested since 2015](https://community.roonlabs.com/t/line-in-input-as-source/738)
and [repeatedly since](https://community.roonlabs.com/t/select-analog-optical-input-to-core/64295).

BluOS does this. A player with the TV connected becomes the primary of a group
and its input is broadcast to the rest, with an A/V mode that adds a short
buffer to hold sync against the picture
([external input to multiple players](https://support.bluos.net/hc/en-us/articles/360035971273-How-do-I-play-external-Input-to-multiple-Players),
[A/V mode](https://support.bluos.net/hc/en-us/articles/360021056034-Grouping-Players-using-A-V-Mode)).
Under Roon, the Node's HDMI eARC input still works — but only as a BluOS
function, controlled from the BluOS app, with Roon unaware of it. Television
audio in other rooms would mean keeping the BluOS app for that one job.

Roon Ready Relay, announced in 2025, is the intended answer: a certification
that lets a device digitise an external source and distribute it across Roon
([Roon Labs](https://blog.roonlabs.com/the-next-evolution-in-roon-technology-roon-ready-relay-expands-your-audio-possibilities/),
[coverage](https://stereonet.com/news/roon-adds-vinyl-playback-with-roon-ready-relay)).
It is per-device and the launch device was a Victrola turntable. No Bluesound
player has it.

It would not solve this even if one did. The problem is latency, not sync
between rooms. Relay digitises at the relay device and sends the audio *to the
server*, which then distributes it to the zones — an extra hop through a server
on top of RAAT's own buffering, in a transport built for robustness across a
home network rather than for low latency. Roon claims no lip-sync capability
anywhere, has no equivalent of A/V mode, and is
[unaware of hardware latency in its sync calculations](https://forum.wiimhome.com/threads/sync-delay-is-it-used-when-playing-from-roon.5121/);
multiroom delay under Roon is
[already a complaint on Bluesound hardware](https://support1.bluesound.com/hc/en-us/community/posts/14905349476759-Multiroom-Delay-using-Roon-since-BluOs-update).
BluOS holds the group *and* the player driving the TV inside lip-sync tolerance
of the picture, which is what A/V mode exists to do. Published latency figures
for RAAT or Relay were not found, so this is architecture and the absence of
any claim rather than a measurement — but nothing suggests Roon is built for
audio that has to match a picture.

##### Discovery: strictly worse than BluOS

Roon discovers everything by multicast. It is
[not supported across subnets or VLANs](https://community.roonlabs.com/t/roon-across-vlans/262545/4),
its own documentation
[asks you to put everything on one subnet](https://help.roonlabs.com/portal/en/kb/articles/how-do-i-know-my-devices-are-on-the-same-subnet-ip-range),
and there is
[no way to add an endpoint by IP address](https://community.roonlabs.com/t/any-way-to-auto-discovery-or-manually-add-audio-endpoints-on-a-different-vlan/121589)
when discovery fails —
[including for certified devices](https://community.roonlabs.com/t/roon-certified-device-not-appearing-as-audio-source-or-allowing-manual-ip-entry-ref-pk6ejo/274492/4).
The marketing calls this
[zero configuration](https://roon.app/en/compatibility/audio); for a network
with an IoT VLAN it means zero options.

|  | BluOS | Roon |
|---|---|---|
| Discovery | LSDP broadcast + mDNS | mDNS multicast only |
| Across VLANs | Works with reflection and UDP replication | Not supported |
| Pin a player by address | `ip:port`, documented HTTP API | No mechanism |
| Build a better client | Possible — this project | Endpoints cannot be addressed |

Multicast really is the common failure in segmented home networks, and IGMP
snooping without a querier really does break it for Sonos and Chromecast too
([background](https://keystoneintegration.us/blog/multicast-mdns-igmp-home-network/)).
The difference is what happens next: BluOS answers direct HTTP on a static
address whatever the discovery layer is doing, which is what makes this project
possible. Roon has no such fallback, which is why so many of those threads end
with the network being blamed — there is nothing else left to blame.

##### New problems Roon brings

- **No ARM build of Roon Server.** Roon Bridge runs on armv7hf and armv8; the
  server is x86-64 only on Linux
  ([standing request](https://community.roonlabs.com/t/roon-server-on-linux-on-arm64-platform-including-but-not-limited-to-raspberry-pi-5/257502)).
  The Orange Pi 5 Plus that is already on cannot host it, so Roon means buying
  and running a second always-on machine.
- **The platform floor moves.** Roon Server moved to .NET 10 on 20 April 2026,
  raising the Linux minimum to glibc 2.27 and OpenSSL 1.1.1
  ([announcement](https://community.roonlabs.com/t/understanding-what-will-happen-to-nas-users-after-the-net-10-based-roon-server-20-april-2026/317959)).
  QNAP QTS 5.x and QuTS hero h5.x do not meet it, because QNAP's glibc has not
  moved since 2018
  ([QNAP](https://community.qnap.com/t/new-roon-system-requirments-not-supported-by-qnap-qts-firmware/5696));
  Synology, ASUSTOR, Unraid and older Macs were caught to varying degrees
  ([summary](https://stereoguide.com/guides/streaming-en/roon-server-no-longer-running-update-renders-many-macs-qnap-synology-and-high-end-servers-unusable/)).
  Hardware bought to run Roon can stop being able to.
- **No Linux client at all.** Roon Server runs headless on Linux, but there is
  [no native Roon remote for Linux](https://community.roonlabs.com/t/no-proper-roon-remote-available-for-linux-pcs/68684)
  — Windows, macOS, iOS and Android only. From a Linux desktop the options are
  Wine or nothing
  ([one approach](https://florib779.github.io/Roon/articles/roon-wine.html)).
  A browser-reachable controller is the entire point of the alternative being
  built here, and Roon is the one candidate that cannot offer one.
- **Two vendors can break the setup instead of one.** BluOS firmware updates
  have taken Bluesound devices out of Roon Ready and left them working only as
  Roon Tested over AirPlay, and a fixed home-theatre group stopped playing from
  Roon after BluOS 4.8.17
  ([Roon forum](https://community.roonlabs.com/t/bluesound-update-issues/302665),
  [Bluesound forum](https://support1.bluesound.com/hc/en-us/community/posts/18441526800919-Roon-still-unreliable-after-upgrading-to-4-0)).
  Crackling and dropouts that appear only under Roon and not under BluOS are a
  recurring report
  ([Roon forum](https://community.roonlabs.com/t/sound-crackling-and-dropping-out-bluesound-node-only-using-roon/202809),
  [Bluesound forum](https://support1.bluesound.com/hc/en-us/community/posts/8005729095575-Crackling-on-N130-Node-using-Roon-with-USB-out)).
- **More traffic to each player.** Roon decodes centrally and sends the result
  to the endpoint, where BluOS has each player fetch and decode its own stream.
  On Wi-Fi that difference shows up as dropouts and slow starts.
- **Cost.** $14.99 per month, about $149 per year, or $829.99 once — very
  roughly 100 DKK per month, 1.000 DKK per year, or 5.500 DKK for the lifetime
  licence, before any Danish VAT
  ([pricing](https://getpulsesignal.com/pricing/roon)). Unchanged since Harman,
  a Samsung subsidiary, bought Roon in November 2023
  ([announcement](https://news.harman.com/releases/harman-acquires-roon-a-popular-multi-device-multi-room-audio-technology-platform)),
  and existing lifetime licences are being honoured. The metadata is what that
  price buys, and the metadata is the part I do not want.
- **Database corruption is a recurring theme**, with restores that fail from
  several backup points and a standing request for a repair tool
  ([corruption on upgrade](https://community.roonlabs.com/t/database-corruption-after-upgrade-restore-attempts-fail-ref-c617vq/320248),
  [repair request](https://community.roonlabs.com/t/automated-database-corruption-repair/168441)).
  This one matters less here than to most who report it, because the library is
  mostly streamed rather than local and curated.

##### Tidal under Roon

Roon does not pass through Tidal's own radios. Roon Radio is Roon's own engine,
Valence, and it picks tracks from the Tidal catalogue rather than asking Tidal
what to play
([Valence](https://blog.roonlabs.com/roon-1-7-valence/),
[Roon KB](https://help.roonlabs.com/portal/en/kb/articles/valence)). The
request to use Tidal's track radio instead
[is open and unimplemented](https://community.roonlabs.com/t/option-to-use-tidals-track-radio-selections-rather-than-roon-radios/99744),
and Valence's output is reported to vary with which services are connected
([example](https://community.roonlabs.com/t/roon-radio-with-qobuz-not-as-good-as-with-tidal/129267)).

So the difficulty getting Tidal radios to play under Roon was not a
misconfiguration. Song, album, playlist and artist radio as Tidal generates
them are not available through Roon at all, and they are the feature used most
here.

Separately, Tidal library sync into Roon misfires often enough to have its own
long-running threads: favourites that do not appear, playlists that do not
update, partial syncs
([favourites](https://community.roonlabs.com/t/roon-does-not-sync-correctly-with-tidal-favorites/91616),
[sync failures](https://community.roonlabs.com/t/tidal-favorites-not-syncing-with-roon-ref-82v4m3/279965)).

Roon does now accept natural-language control through Claude or ChatGPT
([January 2026](https://community.roonlabs.com/t/ai-assistant-integration-for-roon/314508)),
and third-party LLM front-ends exist
([rooAIDJ](https://sellcodes.com/DrCWO/use-ai-to-chat-with-roon)). That is a
different feature from radio, and it does not restore Tidal's own selections.

##### Which of Roon's claims hold

Worth separating, because Roon sits in a market where a lot does not survive
contact with a measurement.

- **Bit-perfect delivery over RAAT: true, and unremarkable.** Roon transports
  audio to the endpoint without alteration
  ([Roon](https://roon.app/en/sound-quality)). So does BluOS, and so does any
  competent UPnP path. It is a correctness claim, not an advantage.
- **Bypassing the OS mixer: true where it applies.** On Windows and macOS the
  system mixer can resample, and avoiding it is a real improvement. It is
  irrelevant to a network player like a Node, which never involves a desktop
  mixer.
- **"AirPlay for audiophiles" is about RAAT, not AirPlay.** The phrase is
  Roon's description of its own transport
  ([Roon KB](https://help.roonlabs.com/portal/en/kb/articles/raat)) — as
  convenient as AirPlay, without the resolution ceiling. Roon cannot change
  AirPlay and does not claim to: an AirPlay zone under Roon is still capped at
  16-bit/44.1 kHz, with Roon downsampling anything higher, and it loses DSP
  when grouped
  ([Roon KB](https://help.roonlabs.com/portal/en/kb/articles/airplay-setup)).
  As a slogan it is fair; as a description of AirPlay it would be false, and
  Roon does not make that claim. RAAT's genuine engineering contribution is
  clock synchronisation across zones, which is a multi-room problem rather
  than a fidelity one.
- **DSP and room correction: real.** Convolution, parametric EQ and per-zone
  delay are ordinary signal processing done competently, and they are the
  strongest technical argument for Roon.
- **Nucleus hardware: this is where it goes wrong.** The Nucleus Titan is a
  standard Intel NUC at $3,699 with the CPU and RAM left off the product page
  ([Tom's Hardware](https://www.tomshardware.com/desktops/mini-pcs/dollar3699-audiophile-media-server-is-powered-by-a-standard-nuc-with-by-a-mystery-cpu-you-still-have-to-buy-your-own-storage-too)).
  A server that feeds a bit-perfect network stream cannot influence what comes
  out of the endpoint's DAC, so there is no mechanism by which it sounds
  better than a NUC running the same software.
- **Sound-quality differences between software builds**, argued at length on
  audiophile forums
  ([example](https://www.whatsbestforum.com/threads/sound-quality-of-new-roon-versions-builds.34593/)),
  are not a Roon claim and should not be held against Roon. Roon's own
  statements on sound quality are the modest, technically correct ones above.

The verdict on snake oil: **the software's claims are mostly accurate and
mostly mundane; the hardware line is where the audiophile pricing appears.**
Buying Roon the software is not buying a fidelity claim. Nothing about Roon
would make the system sound better than a correctly configured BluOS one —
apart from the DSP, which does real work.

##### The case for Roon

An elimination is worth more when the other side has been argued properly. The
strongest arguments for Roon are not about audio, which is itself the finding.
Each is given with the answer it gets here.

**"It exists."** Roon is a working controller on four platforms, maintained by
a company. Musica is a plan. The real comparison is Roon this weekend against
Musica in a year, maintained by one person forever, and every evening spent
building is an evening not spent listening.

*Answer: accepted as a cost, and the money is not the obstacle.* Paying for
something that did the job would be easy. Nothing on offer does the job.

**"Flatten the network and the problem disappears."** Roon needs one L2
segment. Four music players are not the threat class the IoT VLAN exists to
contain. Move them, and the mDNS reflection, the LSDP replication and the
static record service all become unnecessary — for either controller.

*Answer: the separation is not only about threat class.* Separate segments are
what make the players observable and firewallable; on one L2 segment there is
nothing to filter between and much less to see. The relays are not pure
overhead, they are where the control is. Flattening is a real loss, acceptable
only if everything else pulled hard toward it. It does not.

**"Musica deepens the lock-in it exists to escape."** The requirement list asks
for as little vendor lock-in as possible and for drop-in replacement. Roon is
the only candidate that delivers it: over a thousand certified devices,
certification free to manufacturers, so replacing the players later would not
mean replacing the controller. A hand-written client for a protocol one vendor
speaks does the opposite, and every hour invested makes leaving more expensive.

*Answer: true, and it costs less than it looks, because the work is not only
a client.* What the investment buys is knowledge of BluOS — the protocol, the
discovery behaviour, the traps, what the players actually do under load — and
that knowledge keeps paying for as long as the hardware stays. Switching
platforms does not avoid that cost, it restarts it: a different ecosystem means
learning a different one from nothing, whichever controller sits on top. Roon
does not save the research, it relocates it.

BluOS earns the investment in a way the alternatives do not. The players are
stable, and the platform permits a custom client at all — a documented control
API, answering on a fixed address, which is the thing that makes any of this
possible. The scenario where the lock-in bites is leaving Bluesound, and in
that case the replacement would be chosen for not having these problems, so a
BluOS client would be discarded along with the hardware it was written for. The
wasted work is bounded by the hardware's life, and the knowledge is not wasted
at all.

**"The DSP is a tier above, and cheaper."** Convolution, procedural EQ,
per-channel processing and per-zone delay, configured once and applied across
every zone. Dirac Live for Bluesound is a licence bought per device; Roon's DSP
is included and applies to every zone ever added.

*Answer: this is the argument that fails hardest on inspection.* The living
room NODE plays films and television as well as music, and Dirac matters most
for the films. Roon's DSP does not touch anything Roon is not playing. Better
processing over a smaller set of outputs is not an upgrade here.

**"Losing Tidal's radios matters less than it used to."** Valence draws from
the Tidal catalogue and learns from listening history — history a short trial
never built. The comparison that condemned it was Valence cold against a habit.

*Answer: conceded, and it moves.* Tidal is used less now than when the
requirement was written, and recommendations spanning streaming and local music
together could be better than Tidal's own. This is no longer a reason to
eliminate Roon. It is not a reason to adopt it either.

**"The server machine is not a Roon expense."** An always-on x86-64 box is
generally useful and would earn its keep whatever else runs on it.

*Answer: partly.* The Orange Pi is due for replacement anyway, but the
replacement is unlikely to be x86-64, and there is no x86-64 machine here now
with the power to run a Roon server. Long-term this is close to neutral. Today
it is a purchase made for one piece of software.

**"Roon will outlive Musica."** Harman's ownership means a balance sheet behind
it. A one-person project depends on one person continuing to care.

*Answer: conceded on the comparison, doubted as a guarantee.* A long life so
far promises nothing, and hardware and platforms have been dropped before. But
Musica will probably not outlive Roon, and pretending otherwise would be
dishonest.

**What survives.** Two things. Tidal radio is no longer a reason to reject
Roon. And Musica's lifespan is a genuine risk with no answer beyond keeping its
scope small enough that the official app remains a usable fallback for
everything it does not do (D18).

Neither touches the reasons Roon is not usable here.

**The proportion is the point.** BluOS does most of what is wanted, a few
things could be better, and one thing is genuinely infuriating — the Android
controller, described in `MOTIVATION.md`. Replacing an ecosystem that works to
fix one client is the wrong size of answer. Replacing the client is the right
one.

##### Does anyone else report these BluOS problems?

Partly. That players stop appearing in the BluOS Controller is reported often
enough to have an official support article
([BluOS](https://support.bluos.net/hc/en-us/articles/360000303528-Players-not-appearing-in-BluOS-Controller-App))
and long community threads
([looking for players forever](https://support1.bluesound.com/hc/en-us/community/posts/360034808754-Looking-for-Players-forever)),
and a discovery timeout was added to the "Looking For Players" screen in
response.

What is not corroborated anywhere found so far is the Android-versus-iOS
asymmetry. Public reports describe discovery failing on iOS, Android and the
desktop controllers alike, without singling Android out. The measurements in
`MOTIVATION.md` remain the only systematic evidence for that specific claim,
which is an argument for keeping them rather than a reason to doubt them.

##### Conclusion

Roon fails in the living room before the network is even considered. That NODE
plays films, television and music; correction has to apply to all of it, and
Roon's DSP applies only to what Roon plays. The HDMI eARC input is invisible to
Roon, so television audio in other rooms stays a BluOS function. Audio that has
to match a picture is not what RAAT is built for. Three independent failures in
the one room that matters most, and none of them is a configuration problem.

The rest follows: the discovery problem kept in a stricter form with no
endpoint by IP, no supported VLAN story and no control API to build against; a
subscription; an x86-64 server where none exists here; no Linux client; a
second vendor able to break the setup; clients that rate below the BluOS ones
on both mobile platforms.

What Roon does better is real but does not reach: per-zone delay with DSP that
survives grouping, and the least lock-in of any candidate.

**Revisit if** Roon gains hardware inputs as sources, or endpoints addressable
by IP. Both are long-standing requests rather than announced work, so this is
close to never. The trial would still mean one flat L2 segment, a machine
bought to run the server, and the BluOS app kept for the living room.

---

In order to understand why other solutions are not a good fit, it makes sense
to first make a clear list of the requirements that this system is set out to
solve in my home.




The BluOS Android app has real, well-documented problems. But it's worth being
explicit that the app is a *software* complaint, not a *hardware* or *platform*
one — and it's important not to conflate the two when deciding whether to keep
the Node N110/N130/N132 units this project is meant to control.

Over the course of researching this, the following were evaluated as potential
replacements:

Sonos, Denon HEOS, Yamaha MusicCast, WiiM, Naim, Cambridge Audio,
Arcam (ST5, SA35/45, and the new AVP45 processor), Lyngdorf's TDAI-1120,
Onkyo's P-80, StormAudio's processors, Volumio, and a Roon-based DIY approach.
None of them combine, in one product, the specific things this setup depends
on:



**A platform switch doesn't even solve the original complaint.** The BluOS app
itself works noticeably better on iOS than on Android — discovery is more
reliable, fewer of the rough edges show up. That's telling: it confirms the
underlying BluOS platform and protocol aren't inherently broken, since the same
software works fine on different client hardware. It also means switching to an
Apple-centric setup to "fix" this by using AirPlay would be solving a problem
that iOS's *native BluOS app* already solves on its own — there'd be no reason
to route through AirPlay at all, and doing so would only reintroduce the
resolution/bit-depth compromises AirPlay carries anyway.

Given all this, the pragmatic conclusion is: **the hardware and BluOS platform
are doing their job well — the failure point is specifically the Android
client.** That failure is narrow and self-contained enough to fix directly, by
building a better controller against BluOS's existing control API, rather than
by replacing an ecosystem that already works correctly everywhere except one
app.
