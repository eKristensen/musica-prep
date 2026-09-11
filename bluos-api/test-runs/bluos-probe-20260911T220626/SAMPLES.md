# Canonical response samples

One representative response per endpoint from this run, so the
specification can show the actual bytes rather than send a reader to
a decompiler. Every sample is already redacted; the `fidelity` column
says whether redaction touched it at all.

A sample is **not** a confidence marker and never contradicts one. An
element documented from first-party code but absent here is
conditional, not wrong: it appears when there is content to carry it.
Never delete a documented field because one capture lacks it.

| endpoint | probe | status | bytes | fidelity |
|---|---|---|---|---|
| `/Playlist` | `013-state_capture` | 200 | 62326 | verbatim |
| `/Presets` | `012-state_capture` | 200 | 67 | verbatim |
| `/Status` | `021-state_capture` | 200 | 1448 | verbatim |
| `/SyncStatus` | `045-state_capture` | 200 | 563 | 4 edit(s) |
| `/Volume` | `009-state_capture` | 200 | 142 | verbatim |

## `/Playlist`

GET `/Playlist` — probe `013-state_capture`, application/xml, byte-for-byte what the device sent.

```xml
<?xml version="1.0" ?>
<playlist repeat="2" length="125" id="235" shuffle="1">
  <song albumid="482411342" artistid="65040" songid="Tidal:482411348" isFavourite="1" service="Tidal" similarstationid="Tidal:radio:artist/65040" trackstationid="Tidal:radio:track/482411348" id="0">
    <art>Metric</art>
    <alb>Romanticize The Dive</alb>
    <title>Moral Compass</title>
    <track>6</track>
    <discno>1</discno>
    <time>268</time>
    <fn>Tidal:482411348</fn>
    <quality>hd</quality>
    <image>/Artwork?service=Tidal&amp;songid=Tidal%3A482411348</image>
  </song>
  <song albumid="44223966" artistid="3641492" songid="Tidal:44223968" isFavourite="1" service="Tidal" similarstationid="Tidal:radio:artist/3641492" trackstationid="Tidal:radio:track/44223968" id="1">
    <art>Tove Styrke</art>
    <alb>Borderline (Vanic Remix)</alb>
    <title>Borderline</title>
    <track>1</track>
    <discno>1</discno>
    <time>256</time>
    <fn>Tidal:44223968</fn>
    <quality>cd</quality>
    <image>/Artwork?service=Tidal&amp;songid=Tidal%3A44223968</image>
  </song>
  <song albumid="5203374" artistid="34533387" songid="Tidal:5203380" isFavourite="1" service="Tidal" similarstationid="Tidal:radio:artist/34533387" trackstationid="Tidal:radio:track/5203380" id="2">
    <art>Koan</art>
    <alb>When The Silence Is Speaking</alb>
    <title>Odysseus Under The Old Tree</title>
    <track>6</track>
    <discno>1</discno>
    <time>554</time>
    <fn>Tidal:5203380</fn>
    <image>/Artwork?service=Tidal&amp;songid=Tidal%3A5203380</image>
  </song>
  <song albumid="140280295" artistid="6053768" songid="Tidal:140280296" isFavourite="1" service="Tidal" similarstationid="Tidal:radio:artist/6053768" trackstationid="Tidal:radio:track/140280296" id="3">
    <art>Zola Blood</art>
    <alb>Two Hearts</alb>
    <title>Two Hearts</title>
    <track>1</track>
    <discno>1</discno>
    <time>257</time>
    <fn>Tidal:140280296</fn>
    <quality>cd</quality>
    <image>/Artwork?service=Tidal&amp;songid=Tidal%3A140280296</image>
  </song>
  <song albumid="71819320" artistid="8266580" songid="Tidal:71819326" isFavourite="1" service="Tidal" similarstationid="Tidal:radio:artist/8266580" trackstationid="Tidal:radio:track/71819326" id="4">
    <art>Cigarettes After Sex</art>
    <alb>Cigarettes After Sex</alb>
    <title>Sweet</title>
    <track>6</track>
    <discno>1</discno>
    <time>292</time>
    <fn>Tidal:71819326</fn>
    <quality>cd</quality>
    <image>/Artwork?service=Tidal&amp;songid=Tidal%3A71819326</image>
  </song>
  <song albumid="425879086" artistid="10444" songid="Tidal:425879088" isFavourite="1" service="Tidal" similarstationid="Tidal:radio:artist/10444" trackstationid="Tidal:radio:track/425879088" id="5">
    <art>Loreena McKennitt</art>
    <alb>An Ancient Muse</alb>
    <title>The Gates of Istanbul</title>
    <track>2</track>
    <discno>1</discno>
    <time>421</time>
    <fn>Tidal:425879088</fn>
    <quality>cd</quality>
    <image>/Artwork?service=Tidal&amp;songid=Tidal%3A425879088</image>
  </song>
  <song albumid="80689300" artistid="3714733" songid="Tidal:80689303" isFavourite="1" service="Tidal" similarstationid="Tidal:radio:artist/3714733" trackstationid="Tidal:radio:track/80689303" id="6">
    <art>aether</art>
    <alb>Nexus</alb>
    <title>Gloom.8 (feat. Ekcle)</title>
    <track>3</track>
    <discno>1</discno>
    <time>370</time>
    <fn>Tidal:80689303</fn>
    <quality>cd</quality>
    <image>/Artwork?service=Tidal&amp;songid=Tidal%3A80689303</image>
  </song>
  <song albumid="140768092" artistid="15706940" songid="Tidal:140768093" isFavourite="1" service="Tidal" similarstationid="Tidal:radio:artist/15706940" trackstationid="Tidal:radio:track/140768093" id="7">
    <art>AK</art>
    <alb>Peace of Mind</alb>
    <title>Peace of Mind</title>
    <track>1</track>
    <discno>1</discno>
    <time>210</time>
    <fn>Tidal:140768093</fn>
    <quality>cd</quality>
    <image>/Artwork?service=Tidal&amp;songid=Tidal%3A140768093</image>
  </song>
  <song albumid="76226961" artistid="3930594" songid="Tidal:76226962" isFavourite="1" service="Tidal" similarstationid="Tidal:radio:artist/3930594" trackstationid="Tidal:radio:track/76226962" id="8">
    <art>Direct</art>
    <alb>Abandon</alb>
    <title>Abandon</title>
    <track>1</track>
    <discno>1</discno>
    <time>204</time>
    <fn>Tidal:76226962</fn>
    <quality>cd</quality>
    <image>/Artwork?service=Tidal&amp;songid=Tidal%3A76226962</image>
  </song>
  <song albumid="254084095" artistid="8995825" songid="Tidal:254084106" isFavourite="1" service="Tidal" similarstationid="Tidal:radio:artist/8995825" trackstationid="Tidal:radio:track/254084106" id="9">
    <art>Andy Leech</art>
    <alb>The Path So Far</alb>
    <title>Thinking of You</title>
    <track>11</track>
    <discno>1</discno>
    <time>322</time>
    <fn>Tidal:254084106</fn>
    <quality>cd</quality>
    <image>/Artwork?service=Tidal&amp;songid=Tidal%3A254084106</image>
  </song>
  <song albumid="75643820" artistid="4562290" songid="Tidal:75643821" isFavourite="1" service="Tidal" similarstationid="Tidal:radio:artist/4562290" trackstationid="Tidal:radio:track/75643821" id="10">
    <art>SubLab</art>
    <alb>Polarity Waves</alb>
    <title>Polarity Waves</title>
    <track>1</track>
    <discno>1</discno>
    <time>242</time>
    <fn>Tidal:75643821</fn>
    <quality>cd</quality>
    <image>/Artwork?service=Tidal&amp;songid=Tidal%3A75643821</image>
  </song>
  <song albumid="106600730" artistid="4656760" songid="Tidal:106600734" isFavourite="1" service="Tidal" similarstationid="Tidal:radio:artist/4656760" trackstationid="Tidal:radio:track/106600734" id="11">
    <art>Heilung</art>
    <alb>Futha</alb>
    <title>Traust</title>
    <track>4</track>
    <discno>1</discno>
    <time>589</time>
    <fn>Tidal:106600734</fn>
    <quality>cd</quality>
    <image>/Artwork?service=Tidal&amp;songid=Tidal%3A106600734</image>
  </song>
  <song albumid="98214465" artistid="6748205" songid="Tidal:98214475
... truncated; the whole body is in raw/013-state_capture.xml
```

## `/Presets`

GET `/Presets` — probe `012-state_capture`, application/xml, byte-for-byte what the device sent.

```xml
<?xml version="1.0" ?>
<presets prid="0"/>
```

## `/Status`

GET `/Status` — probe `021-state_capture`, application/xml, byte-for-byte what the device sent.

```xml
<?xml version="1.0" ?>
<status etag="4e5379df8b9b94ba2fd48d3fbdf704c3">
  <actions>
    <action name="back" state="0"/>
    <action name="skip" url="/Action?service=RadioParadise&amp;next=2921536" state="0"/>
    <action name="love" url="/Action?service=RadioParadise&amp;love=53146&amp;reset=0" type="thumbs" state="-1" text="Love" icon="/images/loveban/love.png"/>
    <action name="ban" url="/Action?service=RadioParadise&amp;ban=53146&amp;reset=0" type="thumbs" state="-1" text="Ban" icon="/images/loveban/ban.png"/>
  </actions>
  <canMovePlayback>true</canMovePlayback>
  <canSeek>0</canSeek>
  <cursor>19</cursor>
  <db>-58.5</db>
  <image>https://img.radioparadise.com/channels/0/0/cover_512x512/0.jpg</image>
  <indexing>0</indexing>
  <mid>19</mid>
  <mode>1</mode>
  <mute>0</mute>
  <pid>3064</pid>
  <prid>0</prid>
  <quality>cd</quality>
  <repeat>2</repeat>
  <secs>26</secs>
  <service>RadioParadise</service>
  <serviceIcon>/Sources/images/RadioParadiseIcon.png</serviceIcon>
  <serviceName>Radio Paradise</serviceName>
  <serviceType>RadioService</serviceType>
  <shuffle>0</shuffle>
  <sid>50</sid>
  <sleep/>
  <song>0</song>
  <state>pause</state>
  <stationImage>https://img.radioparadise.com/channels/0/0/cover_512x512/0.jpg</stationImage>
  <streamFormat>FLAC 16/44.1</streamFormat>
  <streamUrl>RadioParadise:/0:4</streamUrl>
  <syncStat>1958</syncStat>
  <title1>The Main Mix</title1>
  <totlen>266</totlen>
  <twoline_title1>The Main Mix</twoline_title1>
  <volume>14</volume>
</status>
```

## `/SyncStatus`

GET `/SyncStatus` — probe `045-state_capture`, application/xml, 4 redaction edit(s).

```xml
<?xml version="1.0" ?>
<SyncStatus etag="1036" syncStat="1036" version="4.16.22" id="192.0.2.12:11000" db="-27.7" volume="26" name="Kontor" model="N130" modelName="NODE" class="streamer" icon="/images/players/N125_nt.png" brand="Bluesound" schemaVersion="34" initialized="true" group="Kontor+Køkken" mac="02:00:00:00:00:0C">
  <master port="11000">192.0.2.11</master>
  <slave id="192.0.2.13" port="11000" name="Køkken" model="N132" icon="/images/players/N125_nt.png"/>
  <pairWithSub/>
  <bluetoothOutput/>
</SyncStatus>
```

## `/Volume`

GET `/Volume` — probe `009-state_capture`, application/xml, byte-for-byte what the device sent.

```xml
<?xml version="1.0" ?>
<volume db="-49.1" offsetDb="10" mute="0" etag="a79f2e9d2881ae370f00800f9d0a2c26" source="">20</volume>
```
