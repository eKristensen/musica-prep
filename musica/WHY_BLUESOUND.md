# Why Bluesound?

With the official android app discovery mechanism in chaos why stick around with
Bluesound? Why not find an alternative with a working Andorid app and be happy?

**THIS DOCUMENT IS NOT FINISHED AND IS NOT READY FOR AI REVEIW**

TODO:
- Look at Joplin notes. AI Summary to generate some of the text below removed the essence of my requirements
- Refer back to motivation.

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

- **Roon**: Was my first candidate. Roon run on many types of hardware (not just Bluesound) and provide a beuitiful interface. It requires a server to run, which is hard to understand when you only have one device, but could make more sense with more than one device. There is no ARM build of Roon Server, so it cannot run on the Orange Pi 5 Plus that is already on in my house. Hosting Roon means buying a machine for it, and the cheapest route I can find is a used Mac mini M1 — which will not be flawless either. Extra hardware bought for one piece of software is a real drawback. My existing player would work with it. I tried it and it never felt right; I use Tidal Song/Album/Playlist/Artist radios quite extensively and getting that to play was harder than it should have been. The Roon Server requires mDNS to discover all players dynamically. There is no way to have a list of players you own. Given all the problems I had over the years, and all the effort I have spent trying to make the one Bluesound player I own show up in a more reliable manner, I am especially sensitive to mDNS problems. Not being able to set static players is a unreasonable big downside for me. I read online that Roon accross VLANs is a battle, and it is a batter I do not want to keep fighting in plus Roon is very expensive software. I do not care about the metadata which is one of their main selling points. It just ends up coming short.
https://community.roonlabs.com/t/roon-across-vlans/262545/4
https://roon.app/en/partners/14/bluesound
https://roon.app/en/compatibility/audio: "Zero configuration" is a direct negative
https://community.roonlabs.com/t/roon-certified-device-not-appearing-as-audio-source-or-allowing-manual-ip-entry-ref-pk6ejo/274492/4
https://help.roonlabs.com/portal/en/kb/articles/audio-setup-basics#Resync_delay <-- Properly one thing that would make retrying Roon worth it.
Roon assumes all devices af on the same L2 network. Not something I want. It goes against my policy for IoT device seperation and this is a big negative. Making IoT network setups will always be a battle with Roon.: https://help.roonlabs.com/portal/en/kb/articles/how-do-i-know-my-devices-are-on-the-same-subnet-ip-range#Why_Do_Subnets_Matter

- **Sonos**: 

- **WiiM**: 

- **Denon HEOS** / **Yamaha MusicCast**: Too much vendor lock in. The multi room system here is to provide added value to existing products, it is not the core product. Bluesound is also vendor lock in for sure, but it is more of a stand alone product than any of these.



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
