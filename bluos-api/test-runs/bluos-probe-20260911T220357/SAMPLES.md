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
| `/Alarms` | `042-env` | 200 | 363 | verbatim |
| `/Artwork` | `187-errors` | 200 | 68 | verbatim |
| `/BTDevices` | `010-env` | 200 | 91 | verbatim |
| `/Browse` | `341-browse` | 200 | 66394 | verbatim |
| `/GitVersion` | `003-env` | 200 | 65 | verbatim |
| `/Info` | `131-ports` | 302 | 24 | verbatim |
| `/Name` | `041-env` | 200 | 64 | verbatim |
| `/Playlist` | `017-env` | 200 | 62326 | verbatim |
| `/Playlists` | `261-browse` | 200 | 78 | verbatim |
| `/Presets` | `016-env` | 200 | 67 | verbatim |
| `/RadioBrowse` | `216-claims` | 200 | 2452 | verbatim |
| `/RadioPresets` | `215-claims` | 200 | 2452 | verbatim |
| `/Services` | `004-env` | 200 | 62497 | verbatim |
| `/Settings` | `412-settings` | 200 | 4753 | verbatim |
| `/Shares` | `205-claims` | 200 | 186 | 2 edit(s) |
| `/Songs` | `374-browse` | 200 | 17417 | verbatim |
| `/Status` | `035-env` | 200 | 1448 | verbatim |
| `/SyncStatus` | `001-env` | 200 | 410 | 2 edit(s) |
| `/Version` | `134-ports` | 200 | 65 | verbatim |
| `/Volume` | `007-env` | 200 | 142 | verbatim |
| `/ui/Configuration` | `116-ports` | 200 | 709 | verbatim |
| `/ui/Favourites` | `146-ports` | 200 | 1137 | verbatim |
| `/ui/Home` | `143-ports` | 200 | 19588 | 11 edit(s) |
| `/ui/News` | `145-ports` | 200 | 271 | verbatim |
| `/ui/Queue` | `152-ports` | 200 | 10182 | verbatim |
| `/ui/RecentlyPlayed` | `144-ports` | 200 | 89658 | 70 edit(s) |
| `/ui/Search` | `148-ports` | 200 | 1280 | verbatim |
| `/ui/Sources` | `147-ports` | 200 | 3286 | verbatim |
| `/ui/nowPlayingCM` | `149-ports` | 200 | 2109 | 1 edit(s) |
| `/ui/presets` | `153-ports` | 200 | 1309 | 3 edit(s) |

## `/Alarms`

GET `/Alarms` — probe `042-env`, application/xml, byte-for-byte what the device sent.

```xml
<?xml version="1.0" ?>
<alarms supportsEndTime="true">
  <alarm hour="7" minute="15" days="0000000" duration="60" volume="22" voldb="-53.1" fadein="1" enable="0" id="1" source="The Main Mix" url="RadioParadise:/0:20" service="RadioParadise" image="https://img.radioparadise.com/channels/0/0/cover_512x512/0.jpg" useBackup="true"/>
</alarms>
```

## `/Artwork`

GET `/Artwork` — probe `187-errors`, application/xml, byte-for-byte what the device sent.

```xml
<?xml version="1.0" ?>
<artwork>none found</artwork>
```

## `/BTDevices`

GET `/BTDevices?timeout=1` — probe `010-env`, application/xml, byte-for-byte what the device sent.

```xml
<?xml version="1.0" ?>
<btdevices etag="14" connecting="false"/>
```

## `/Browse`

GET `/Browse?key=TuneIn%3ABrowseMenu%2F%252FRadioBrowse%253Fservice%3DTuneIn%26url%3Dhttps%25253A%25252F%25252Fapi.radiotime.com%25252Fcategories%25252Fc100000088%25253Fserial%25253DC0%2525253a74%2525253a2B%2525253aFF%2525253a2C%2525253a1E%252526partnerId%25253D8OeGua6y%252526version%25253D2%252526formats%25253Dwma%2525252cmp3%2525252caac%2525252cogg%2525252chls%252526viewModel%25253DFalse%252526itemToken%25253DBggIAAYABgABAAEAAQEAAQgAAA` — probe `341-browse`, application/xml, byte-for-byte what the device sent.

```xml
<?xml version="1.0" ?>
<browse serviceIcon="/Sources/images/TuneInIcon.png" serviceName="TuneIn" searchKey="TuneIn:Search" type="items">
  <category text="Top 10 Podcasts">
    <item contextMenuKey="TuneIn:CM/TuneIn-Item?URL=TuneIn%3At576168051&amp;image=http%3A%2F%2Fcdn-profiles.tunein.com%2Fp134942%2Fimages%2Flogog.png%3Ft%3D638882611680000000&amp;preset_id=p134942&amp;text=Global+News+Podcast" playURL="/Play?url=TuneIn%3At576168051&amp;title=Global+News+Podcast&amp;image=http%3A%2F%2Fcdn-profiles.tunein.com%2Fp134942%2Fimages%2Flogog.png%3Ft%3D638882611680000000" text="Global News Podcast" image="http://cdn-profiles.tunein.com/p134942/images/logog.png?t=638882611680000000" type="audio"/>
    <item contextMenuKey="TuneIn:CM/TuneIn-Item?URL=TuneIn%3At576045985&amp;image=http%3A%2F%2Fcdn-profiles.tunein.com%2Fp591437%2Fimages%2Flogog.png%3Ft%3D638986523900000000&amp;preset_id=p591437&amp;text=No+Such+Thing+As+A+Fish" playURL="/Play?url=TuneIn%3At576045985&amp;title=No+Such+Thing+As+A+Fish&amp;image=http%3A%2F%2Fcdn-profiles.tunein.com%2Fp591437%2Fimages%2Flogog.png%3Ft%3D638986523900000000" text="No Such Thing As A Fish" image="http://cdn-profiles.tunein.com/p591437/images/logog.png?t=638986523900000000" type="audio"/>
    <item contextMenuKey="TuneIn:CM/TuneIn-Item?URL=TuneIn%3At576170079&amp;image=http%3A%2F%2Fcdn-profiles.tunein.com%2Fp998531%2Fimages%2Flogog.png%3Ft%3D638816837330000000&amp;preset_id=p998531&amp;text=Newscast" playURL="/Play?url=TuneIn%3At576170079&amp;title=Newscast&amp;image=http%3A%2F%2Fcdn-profiles.tunein.com%2Fp998531%2Fimages%2Flogog.png%3Ft%3D638816837330000000" text="Newscast" image="http://cdn-profiles.tunein.com/p998531/images/logog.png?t=638816837330000000" type="audio"/>
    <item contextMenuKey="TuneIn:CM/TuneIn-Item?URL=TuneIn%3At576150757&amp;image=http%3A%2F%2Fcdn-profiles.tunein.com%2Fp1456799%2Fimages%2Flogog.png%3Ft%3D639018417460000000&amp;preset_id=p1456799&amp;text=That+UFO+Podcast" playURL="/Play?url=TuneIn%3At576150757&amp;title=That+UFO+Podcast&amp;image=http%3A%2F%2Fcdn-profiles.tunein.com%2Fp1456799%2Fimages%2Flogog.png%3Ft%3D639018417460000000" text="That UFO Podcast" image="http://cdn-profiles.tunein.com/p1456799/images/logog.png?t=639018417460000000" type="audio"/>
    <item contextMenuKey="TuneIn:CM/TuneIn-Item?URL=TuneIn%3At538418721&amp;image=http%3A%2F%2Fcdn-profiles.tunein.com%2Fp238460%2Fimages%2Flogog.png%3Ft%3D638930132350000000&amp;preset_id=p238460&amp;text=The+Infinite+Monkey+Cage" playURL="/Play?url=TuneIn%3At538418721&amp;title=The+Infinite+Monkey+Cage&amp;image=http%3A%2F%2Fcdn-profiles.tunein.com%2Fp238460%2Fimages%2Flogog.png%3Ft%3D638930132350000000" text="The Infinite Monkey Cage" image="http://cdn-profiles.tunein.com/p238460/images/logog.png?t=638930132350000000" type="audio"/>
    <item contextMenuKey="TuneIn:CM/TuneIn-Item?URL=TuneIn%3At576175004&amp;image=http%3A%2F%2Fcdn-profiles.tunein.com%2Fp1375081%2Fimages%2Flogog.png%3Ft%3D638690554580000000&amp;preset_id=p1375081&amp;text=Americast" playURL="/Play?url=TuneIn%3At576175004&amp;title=Americast&amp;image=http%3A%2F%2Fcdn-profiles.tunein.com%2Fp1375081%2Fimages%2Flogog.png%3Ft%3D638690554580000000" text="Americast" image="http://cdn-profiles.tunein.com/p1375081/images/logog.png?t=638690554580000000" type="audio"/>
    <item contextMenuKey="TuneIn:CM/TuneIn-Item?URL=TuneIn%3At576076242&amp;image=http%3A%2F%2Fcdn-profiles.tunein.com%2Fp1319784%2Fimages%2Flogog.png%3Ft%3D639211135680000000&amp;preset_id=p1319784&amp;text=F1+Nation" playURL="/Play?url=TuneIn%3At576076242&amp;title=F1+Nation&amp;image=http%3A%2F%2Fcdn-profiles.tunein.com%2Fp1319784%2Fimages%2Flogog.png%3Ft%3D639211135680000000" text="F1 Nation" image="http://cdn-profiles.tunein.com/p1319784/images/logog.png?t=639211135680000000" type="audio"/>
    <item contextMenuKey="TuneIn:CM/TuneIn-Item?URL=TuneIn%3At575576541&amp;image=http%3A%2F%2Fcdn-profiles.tunein.com%2Fp962944%2Fimages%2Flogog.png%3Ft%3D638907827910000000&amp;preset_id=p962944&amp;text=Rugby+Union+Weekly" playURL="/Play?url=TuneIn%3At575576541&amp;title=Rugby+Union+Weekly&amp;image=http%3A%2F%2Fcdn-profiles.tunein.com%2Fp962944%2Fimages%2Flogog.png%3Ft%3D638907827910000000" text="Rugby Union Weekly" image="http://cdn-profiles.tunein.com/p962944/images/logog.png?t=638907827910000000" type="audio"/>
    <item contextMenuKey="TuneIn:CM/TuneIn-Item?URL=TuneIn%3At576123495&amp;image=http%3A%2F%2Fcdn-profiles.tunein.com%2Fp3971612%2Fimages%2Flogog.png%3Ft%3D639115371480000000&amp;preset_id=p3971612&amp;text=The+Global+Story" playURL="/Play?url=TuneIn%3At576123495&amp;title=The+Global+Story&amp;image=http%3A%2F%2Fcdn-profiles.tunein.com%2Fp3971612%2Fimages%2Flogog.png%3Ft%3D639115371480000000" text="The Global Story" image="http://cdn-profiles.tunein.com/p3971612/images/logog.png?t=639115371480000000" type="audio"/>
  </category>
  <category text="Cumulus Podcasts">
    <item contextMenuKey="TuneIn:CM/TuneIn-Item?URL=TuneIn%3At576079732&amp;image=http%3A%2F%2Fcdn-profiles.tunein.com%2Fp1713368%2Fimages%2Flogog.png%3Ft%3D638935630110000000&amp;preset_id=p1713368&amp;text=Untraditionally+Lala" playURL="/Play?url=TuneIn%3At576079732&amp;title=Untraditionally+Lala&amp;image=http%3A%2F%2Fcdn-profiles.tunein.com%2Fp1713368%2Fimages%2Flogog.png%3Ft%3D638935630110000000" text="Untraditionally Lala" text2="You’ve seen LaLa Kent laugh, cry, and even scream for eight seasons as she broke ALL the Vanderpump Rules,now she sets and sometimes bends her own rules on her new podcast “Untraditionally Lala.”She invites you to a whole new Lala land, where mistakes..." image="http://cdn-profiles.tunein.com/p1713368/images/logog.png?t=638935630110000000" type="audio"/>
    <item contextMenuKey="TuneIn:CM/TuneIn-Item?URL=TuneIn%3At575945106&amp;image=http%3A%2F%2Fcdn-profiles.tunein.com%2Fp1280746%2Fimages%2Flogog.png%3Ft%3D639096279450000000&amp;preset_id=p1280746&amp;text=The+Shawn+Ryan+Show" playURL="/Play?url=TuneIn%3At575945106&amp;title=The+Shawn+Ryan+Show&amp;image
... truncated; the whole body is in raw/341-browse.xml
```

## `/GitVersion`

GET `/GitVersion` — probe `003-env`, application/xml, byte-for-byte what the device sent.

```xml
<?xml version="1.0" ?>
<version>4.16.22</version>
```

## `/Info`

GET `/Info` — probe `131-ports`, text/html; charset=utf-8, byte-for-byte what the device sent.

```xml
<a href="/">Found</a>.


```

## `/Name`

GET `/Name` — probe `041-env`, application/xml, byte-for-byte what the device sent.

```xml
<?xml version="1.0" ?>
<name>Soveværelse</name>
```

## `/Playlist`

GET `/Playlist` — probe `017-env`, application/xml, byte-for-byte what the device sent.

```xml
<?xml version="1.0" ?>
<playlist length="125" id="235" shuffle="1" repeat="2">
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
... truncated; the whole body is in raw/017-env.xml
```

## `/Playlists`

GET `/Playlists` — probe `261-browse`, application/xml, byte-for-byte what the device sent.

```xml
<?xml version="1.0" ?>
<playlists service="BluOS"/>
```

## `/Presets`

GET `/Presets` — probe `016-env`, application/xml, byte-for-byte what the device sent.

```xml
<?xml version="1.0" ?>
<presets prid="0"/>
```

## `/RadioBrowse`

GET `/RadioBrowse?service=RadioParadise` — probe `216-claims`, application/xml, byte-for-byte what the device sent.

```xml
<?xml version="1.0" ?>
<radiotime service="RadioParadise">
  <category text="MQA" key="20">
    <item text="The Main Mix" type="audio" URL="RadioParadise%3A%2F0%3A20" image="https://img.radioparadise.com/channels/0/0/cover_512x512/0.jpg"/>
    <item text="Mellow Mix" type="audio" URL="RadioParadise%3A%2F1%3A20%2FMellow%2520Mix" image="https://img.radioparadise.com/channels/0/1/cover_512x512/0.jpg"/>
    <item text="RockIt!" type="audio" URL="RadioParadise%3A%2F2%3A20%2FRockIt%2521" image="https://img.radioparadise.com/channels/0/2/cover_512x512/0.jpg"/>
    <item text="The Globe" type="audio" URL="RadioParadise%3A%2F3%3A20%2FThe%2520Globe" image="https://img.radioparadise.com/channels/0/3/cover_512x512/0.jpg"/>
    <item text="Beyond..." type="audio" URL="RadioParadise%3A%2F5%3A20%2FBeyond..." image="https://img.radioparadise.com/channels/0/5/cover_512x512/0.jpg"/>
    <item text="Serenity" type="audio" URL="RadioParadise%3A%2F42%3A20%2FSerenity" image="https://img.radioparadise.com/channels/0/42/cover_512x512/0.jpg"/>
    <item text="KFAT" type="audio" URL="RadioParadise%3A%2F945%3A20%2FKFAT" image="https://img.radioparadise.com/channels/0/945/cover_512x512/0.jpg"/>
  </category>
  <category text="CD Quality" key="4">
    <item text="The Main Mix" type="audio" URL="RadioParadise%3A%2F0%3A4" image="https://img.radioparadise.com/channels/0/0/cover_512x512/0.jpg"/>
    <item text="Mellow Mix" type="audio" URL="RadioParadise%3A%2F1%3A4%2FMellow%2520Mix" image="https://img.radioparadise.com/channels/0/1/cover_512x512/0.jpg"/>
    <item text="RockIt!" type="audio" URL="RadioParadise%3A%2F2%3A4%2FRockIt%2521" image="https://img.radioparadise.com/channels/0/2/cover_512x512/0.jpg"/>
    <item text="The Globe" type="audio" URL="RadioParadise%3A%2F3%3A4%2FThe%2520Globe" image="https://img.radioparadise.com/channels/0/3/cover_512x512/0.jpg"/>
    <item text="Beyond..." type="audio" URL="RadioParadise%3A%2F5%3A4%2FBeyond..." image="https://img.radioparadise.com/channels/0/5/cover_512x512/0.jpg"/>
    <item text="Serenity" type="audio" URL="RadioParadise%3A%2F42%3A4%2FSerenity" image="https://img.radioparadise.com/channels/0/42/cover_512x512/0.jpg"/>
    <item text="KFAT" type="audio" URL="RadioParadise%3A%2F945%3A4%2FKFAT" image="https://img.radioparadise.com/channels/0/945/cover_512x512/0.jpg"/>
  </category>
</radiotime>
```

## `/RadioPresets`

GET `/RadioPresets?service=RadioParadise` — probe `215-claims`, application/xml, byte-for-byte what the device sent.

```xml
<?xml version="1.0" ?>
<radiotime service="RadioParadise">
  <category text="MQA" key="20">
    <item text="The Main Mix" type="audio" URL="RadioParadise%3A%2F0%3A20" image="https://img.radioparadise.com/channels/0/0/cover_512x512/0.jpg"/>
    <item text="Mellow Mix" type="audio" URL="RadioParadise%3A%2F1%3A20%2FMellow%2520Mix" image="https://img.radioparadise.com/channels/0/1/cover_512x512/0.jpg"/>
    <item text="RockIt!" type="audio" URL="RadioParadise%3A%2F2%3A20%2FRockIt%2521" image="https://img.radioparadise.com/channels/0/2/cover_512x512/0.jpg"/>
    <item text="The Globe" type="audio" URL="RadioParadise%3A%2F3%3A20%2FThe%2520Globe" image="https://img.radioparadise.com/channels/0/3/cover_512x512/0.jpg"/>
    <item text="Beyond..." type="audio" URL="RadioParadise%3A%2F5%3A20%2FBeyond..." image="https://img.radioparadise.com/channels/0/5/cover_512x512/0.jpg"/>
    <item text="Serenity" type="audio" URL="RadioParadise%3A%2F42%3A20%2FSerenity" image="https://img.radioparadise.com/channels/0/42/cover_512x512/0.jpg"/>
    <item text="KFAT" type="audio" URL="RadioParadise%3A%2F945%3A20%2FKFAT" image="https://img.radioparadise.com/channels/0/945/cover_512x512/0.jpg"/>
  </category>
  <category text="CD Quality" key="4">
    <item text="The Main Mix" type="audio" URL="RadioParadise%3A%2F0%3A4" image="https://img.radioparadise.com/channels/0/0/cover_512x512/0.jpg"/>
    <item text="Mellow Mix" type="audio" URL="RadioParadise%3A%2F1%3A4%2FMellow%2520Mix" image="https://img.radioparadise.com/channels/0/1/cover_512x512/0.jpg"/>
    <item text="RockIt!" type="audio" URL="RadioParadise%3A%2F2%3A4%2FRockIt%2521" image="https://img.radioparadise.com/channels/0/2/cover_512x512/0.jpg"/>
    <item text="The Globe" type="audio" URL="RadioParadise%3A%2F3%3A4%2FThe%2520Globe" image="https://img.radioparadise.com/channels/0/3/cover_512x512/0.jpg"/>
    <item text="Beyond..." type="audio" URL="RadioParadise%3A%2F5%3A4%2FBeyond..." image="https://img.radioparadise.com/channels/0/5/cover_512x512/0.jpg"/>
    <item text="Serenity" type="audio" URL="RadioParadise%3A%2F42%3A4%2FSerenity" image="https://img.radioparadise.com/channels/0/42/cover_512x512/0.jpg"/>
    <item text="KFAT" type="audio" URL="RadioParadise%3A%2F945%3A4%2FKFAT" image="https://img.radioparadise.com/channels/0/945/cover_512x512/0.jpg"/>
  </category>
</radiotime>
```

## `/Services`

GET `/Services` — probe `004-env`, application/xml, byte-for-byte what the device sent.

```xml
<?xml version="1.0" ?>
<services schemaVersion="34" sid="50" url="/redirectToCp?href=%2Fservices%3Fnoheader%3D1%26schemaVersion%3D35">
  <service hasStableBrowse="true" name="BluOS" type="BluOSPlaylists" displayname="BluOS" icon="/images/BluOSIcon.png">
    <menu>
      <menuEntry displayName="Playlists" inlineRows="5">
        <sort name="sort" default="alpha" minimumSchemaVersion="19">
          <value name="recent" displayName="Date added"/>
          <value name="alpha" displayName="A → Z"/>
        </sort>
        <browseRequest url="/Playlists" resultType="Playlist" myPlaylistsFilter="myPlaylists=1">
			</browseRequest>
      </menuEntry>
      <menuGroup context="Playlist">
        <nofilter/>
        <menuEntry displayName="Songs">
          <browseRequest url="/Songs" resultType="Song">
            <requestItemParameter name="playlist"/>
          </browseRequest>
        </menuEntry>
        <menuEntry displayName="Play now">
          <disableOnAttribute name="playlistid"/>
          <request url="/Add" type="add" subtype="now">
            <requestItemParameter name="playlist"/>
            <requestParameter>playnow=1</requestParameter>
            <requestParameter>clear=0</requestParameter>
            <requestParameter>shuffle=0</requestParameter>
          </request>
        </menuEntry>
        <menuEntry displayName="Shuffle">
          <disableOnAttribute name="playlistid"/>
          <request url="/Add" type="add" subtype="shuffle">
            <requestItemParameter name="playlist"/>
            <requestParameter>shuffle=1</requestParameter>
            <requestParameter>playnow=1</requestParameter>
          </request>
        </menuEntry>
        <menuEntry displayName="Add next">
          <request url="/Add" type="add" subtype="next">
            <requestItemParameter name="playlist"/>
            <requestItemParameter name="playlistid" optional="true"/>
            <requestParameter>playnow=-1</requestParameter>
            <requestParameter>where=next</requestParameter>
          </request>
        </menuEntry>
        <menuEntry displayName="Add last">
          <request url="/Add" type="add" subtype="last">
            <requestItemParameter name="playlist"/>
            <requestItemParameter name="playlistid" optional="true"/>
            <requestParameter>playnow=-1</requestParameter>
            <requestParameter>where=last</requestParameter>
          </request>
        </menuEntry>
        <menuEntry displayName="Delete">
          <disableOnAttribute name="playlistid"/>
          <confirmAction text="Delete playlist: %s?">
            <textItemSubstitution attribute="text" source="playlist"/>
          </confirmAction>
          <request url="/Delete" type="delete">
            <requestItemParameter name="name" source="playlist"/>
          </request>
        </menuEntry>
      </menuGroup>
    </menu>
  </service>
  <service displayname="" name="Capture" type="AudioInputs">
    <menu>
      <menuGroup mainMenu="true">
        <menuEntry displayName="Inputs">
          <browseRequest url="/RadioBrowse" resultType="BrowseMenu"/>
        </menuEntry>
      </menuGroup>
    </menu>
  </service>
  <service displayname="" name="Alarms" type="Alarms">
    <menu>
      <menuEntry displayName="Alarms">
        <browseRequest url="/Alarms" resultType="Alarms"/>
      </menuEntry>
      <menuEntry displayName="Alarm Sound">
        <browseRequest url="/RadioBrowse" resultType="BrowseMenu"/>
      </menuEntry>
    </menu>
  </service>
  <service label="No Label" icon="/images/LibraryIcon.png" hasStableBrowse="true" type="LocalMusic" name="LocalMusic" displayname="Library">
    <menu>
      <search prompt="Search..." parameterName="expr">
        <menuGroup context="Search" minimumSchemaVersion="2">
          <menuEntry displayName="Artists" inlineRows="4">
            <nofilter/>
            <browseRequest url="/library/v1/Artists" resultType="Artist"/>
          </menuEntry>
          <menuEntry displayName="Albums" inlineRows="1">
            <browseRequest url="/library/v1/Albums" resultType="Album"/>
          </menuEntry>
          <menuEntry displayName="Songs" inlineRows="4">
            <browseRequest url="/library/v1/Songs" resultType="Song"/>
          </menuEntry>
          <menuEntry displayName="Composers" minimumSchemaVersion="12" inlineRows="4">
            <nofilter/>
            <browseRequest url="/library/v1/Composers" resultType="Composer"/>
          </menuEntry>
        </menuGroup>
        <browseRequest url="/library/v1/Search" resultType="Search"/>
      </search>
      <filter name="quality" displayName="Filter by quality" class="multiple">
        <value name="mqa" displayName="MQA" type="mqa"/>
        <value name="hr" displayName="High Resolution" type="hr"/>
        <value name="cd" displayName="CD" type="cd"/>
      </filter>
      <menuEntry displayName="Artists">
        <nofilter/>
        <browseRequest url="/library/v1/Artists" resultType="Artist" grouped="true"/>
      </menuEntry>
      <menuEntry displayName="Albums" defaultView="true">
        <sort name="sort" default="alpha" minimumSchemaVersion="19">
          <value name="alpha" displayName="A → Z"/>
          <value name="recent" displayName="Recent"/>
          <value name="year" displayName="Year"/>
          <value name="decade" displayName="Decade"/>
          <value name="artist" displayName="Artist"/>
          <value name="artistDate" displayName="Artist, release-date"/>
        </sort>
        <browseRequest url="/library/v1/Albums" resultType="Album" grouped="true"/>
      </menuEntry>
      <menuEntry displayName="Songs">
        <browseRequest url="/library/v1/Songs" resultType="Song" grouped="true">
          <requestParameter>all=1</requestParameter>
          <!-- helper for GetSongIds() -->
        </browseRequest>
      </menuEntry>
      <genreGroup displayName="Genres" minimumSchemaVersion="20">
        <browseRequest url="/library/v1/Genres" resultType=
... truncated; the whole body is in raw/004-env.xml
```

## `/Settings`

GET `/Settings?id=audio&schemaVersion=35` — probe `412-settings`, text/xml; charset=utf-8, byte-for-byte what the device sent.

```xml
<?xml version="1.0" ?>
<settings pageId="audio" schemaVersion="35">
  <menuGroup id="audio" defaults="false" displayName="Audio" icon="/images/settings/ic_audio.png" url="/audiomodes">
    <setting id="eq-dirac" name="eq-dirac" displayName="Dirac Live" url="/alsa_setting" icon="/images/settings/ic_dirac.png" class="list" value="5" refresh="true" hideIfDisabled="true">
      <value displayName="Off" name="0"/>
      <value displayName="Solo v2 &lt;300 Hz Default" name="1"/>
      <value displayName="Solo v3 &lt;421 Hz default" name="2"/>
      <value displayName="SVS &lt;420 Hz default" name="3"/>
      <value displayName="SVS &lt;420 Hz + mere bass" name="4"/>
      <value displayName="SVS &lt;422 Hz target curve" name="5"/>
    </setting>
    <setting id="eq-switch" name="eq-switch" displayName="Tone Controls" url="/alsa_setting" icon="/images/settings/ic_eqonoff.png" class="boolean" value="OFF" hideIfDisabled="true">
      <dependsOn name="mqaDisable" value="OFF"/>
    </setting>
    <setting id="eq-treble" name="eq-treble" displayName="Treble" url="/alsa_setting" icon="/images/settings/icon_treble.png" class="range" value="0" hideIfDisabled="true">
      <value min="-6" max="6" step="0.5" units="dB"/>
      <dependsOn name="eq-switch" value="ON"/>
    </setting>
    <setting id="eq-bass" name="eq-bass" displayName="Bass" url="/alsa_setting" icon="/images/settings/icon_bass.png" class="range" value="0" hideIfDisabled="true">
      <value min="-6" max="6" step="0.5" units="dB"/>
      <dependsOn name="eq-switch" value="ON"/>
    </setting>
    <setting id="subwoofer" name="subwoofer" displayName="Subwoofer" url="/audiomodes" icon="/images/settings/icon_subwoofer.png" class="boolean" value="withsub">
      <value displayName="Off" name="default"/>
      <value displayName="On" name="withsub"/>
    </setting>
    <setting id="eq-crossover" name="eq-crossover" displayName="Crossover" url="/alsa_setting" icon="/images/settings/ic_crossover.png" class="range" value="60" hideIfDisabled="true">
      <value min="40" max="200" step="10" units="Hz"/>
      <dependsOn name="subwoofer" value="withsub"/>
    </setting>
    <setting id="replayGainMode" name="replayGainMode" displayName="Replay-gain" url="/audiomodes" icon="/images/settings/ic_replaygain.png" class="list" value="none" description="Disabled">
      <value displayName="Disabled" name="none"/>
      <value displayName="Track gain" name="track"/>
      <value displayName="Album gain" name="album"/>
      <value displayName="Smart gain" name="smart"/>
      <dependsOn name="mqaDisable" value="OFF"/>
    </setting>
    <setting id="channelMode" name="channelMode" displayName="Output mode" url="/audiomodes" icon="/images/settings/ic_channelmode.png" class="list" value="default" description="Stereo" hideIfDisabled="true">
      <value displayName="Stereo" name="default"/>
      <value displayName="Left" name="left"/>
      <value displayName="Right" name="right"/>
      <value displayName="Mono" name="mono"/>
    </setting>
    <setting id="mqaDisable" name="mqaDisable" displayName="Digital Passthrough" url="/audiomodes" icon="/images/settings/ic_mqadisable.png" class="boolean" value="OFF" explanation="When Digital Passthrough is turned ON, BluOS sends the original audio stream to an external DAC, bypassing BluOS's internal MQA decoder.">
      <dependsOn name="replayGainMode" value="none"/>
      <dependsOn name="fixedVolume" value="ON"/>
      <dependsOn name="eq-switch" value="OFF"/>
    </setting>
    <setting id="fixedVolume" name="fixedVolume" displayName="Output level fixed" icon="/images/settings/ic_fixedvolume.png" class="boolean" value="OFF">
      <dependsOn name="mqaDisable" value="OFF"/>
    </setting>
    <setting id="volumeLimits" name="volumeLimits" displayName="Volume limits (dB)" icon="/images/settings/ic_volumelimits.png" class="dual-range" value="-75,-10" hideIfDisabled="true">
      <value min="-90" max="0" minRange="30" units="dB"/>
      <dependsOn name="fixedVolume" value="OFF"/>
    </setting>
    <setting id="enableClockTrim" name="enableClockTrim" displayName="Audio clock trim" url="/audiomodes" icon="/images/settings/ic_audioclocktrim.png" class="boolean" value="ON" explanation="BluOS uses small adjustments to the audio clock to maintain glitch-free audio synchronization. Disable this when using an external DAC that cannot cope with these adjustments."/>
    <setting id="reset" name="reset" displayName="Reset All" url="/alsa_setting" icon="/images/settings/icon_reset.png" class="button" style="center"/>
  </menuGroup>
</settings>
```

## `/Shares`

GET `/Shares` — probe `205-claims`, text/xml; charset=utf-8, 2 redaction edit(s).

```xml
<?xml version="1.0" ?>
<shares count="1">
  <share>
    <sharename>\\192.0.2.102\music</sharename>
    <username>[REDACTED-value-1]</username>
  </share>
</shares>
```

## `/Songs`

GET `/Songs?service=Tidal&category=FAVOURITES&start=0&end=999` — probe `374-browse`, application/xml, byte-for-byte what the device sent.

```xml
<?xml version="1.0" ?>
<songs service="Tidal" end="99" category="FAVOURITES" start="50">
  <song albumid="146345182" artistid="17603073" songid="Tidal:146345183" isFavourite="1" similarstationid="Tidal:radio:artist/17603073" trackstationid="Tidal:radio:track/146345183">
    <art>YOASOBI</art>
    <alb>たぶん</alb>
    <title>たぶん</title>
    <track>1</track>
    <discno>1</discno>
    <time>259</time>
    <fn>Tidal:146345183</fn>
    <quality>hd</quality>
  </song>
  <song albumid="100745453" artistid="6437711" songid="Tidal:100745454" isFavourite="1" similarstationid="Tidal:radio:artist/6437711" trackstationid="Tidal:radio:track/100745454">
    <art>Azaleh</art>
    <alb>04.49 Uhr</alb>
    <title>04.49 Uhr</title>
    <track>1</track>
    <discno>1</discno>
    <time>261</time>
    <fn>Tidal:100745454</fn>
    <quality>cd</quality>
  </song>
  <song albumid="176976280" artistid="688" songid="Tidal:176976290" isFavourite="1" similarstationid="Tidal:radio:artist/688" trackstationid="Tidal:radio:track/176976290">
    <art>Chicane</art>
    <alb>Everything We Had To Leave Behind</alb>
    <title>1000 More Suns</title>
    <track>8</track>
    <discno>1</discno>
    <time>265</time>
    <fn>Tidal:176976290</fn>
    <quality>hd</quality>
  </song>
  <song albumid="40984904" artistid="3833068" songid="Tidal:40984906" isFavourite="1" similarstationid="Tidal:radio:artist/3833068" trackstationid="Tidal:radio:track/40984906">
    <art>Portico</art>
    <alb>Living Fields</alb>
    <title>101</title>
    <track>2</track>
    <discno>1</discno>
    <time>285</time>
    <fn>Tidal:40984906</fn>
    <quality>cd</quality>
  </song>
  <song albumid="390529622" artistid="3915082" songid="Tidal:390529623" isFavourite="1" similarstationid="Tidal:radio:artist/3915082" trackstationid="Tidal:radio:track/390529623">
    <art>ZEDD</art>
    <alb>1685</alb>
    <title>1685</title>
    <track>1</track>
    <discno>1</discno>
    <time>236</time>
    <fn>Tidal:390529623</fn>
    <quality>hd</quality>
  </song>
  <song albumid="60262018" artistid="6810208" songid="Tidal:60262019" isFavourite="1" similarstationid="Tidal:radio:artist/6810208" trackstationid="Tidal:radio:track/60262019">
    <art>Page Four</art>
    <alb>Page Four</alb>
    <title>17 år</title>
    <track>1</track>
    <discno>1</discno>
    <time>227</time>
    <fn>Tidal:60262019</fn>
    <quality>cd</quality>
  </song>
  <song albumid="67237700" artistid="3658521" songid="Tidal:67237701" isFavourite="1" similarstationid="Tidal:radio:artist/3658521" trackstationid="Tidal:radio:track/67237701">
    <art>Bruno Mars</art>
    <alb>24K Magic</alb>
    <title>24K Magic</title>
    <track>1</track>
    <discno>1</discno>
    <time>226</time>
    <fn>Tidal:67237701</fn>
    <quality>cd</quality>
  </song>
  <song albumid="398883774" artistid="9380062" songid="Tidal:398883776" isFavourite="1" similarstationid="Tidal:radio:artist/9380062" trackstationid="Tidal:radio:track/398883776">
    <art>Tate McRae</art>
    <alb>2 hands</alb>
    <title>2 hands</title>
    <track>1</track>
    <discno>1</discno>
    <time>182</time>
    <fn>Tidal:398883776</fn>
    <quality>hd</quality>
  </song>
  <song albumid="22125592" artistid="11004" songid="Tidal:22125593" isFavourite="1" similarstationid="Tidal:radio:artist/11004" trackstationid="Tidal:radio:track/22125593">
    <art>Carpark North</art>
    <alb>32</alb>
    <title>32</title>
    <track>1</track>
    <discno>1</discno>
    <time>251</time>
    <fn>Tidal:22125593</fn>
    <quality>cd</quality>
  </song>
  <song albumid="2618165" artistid="3667" songid="Tidal:2618174" isFavourite="1" similarstationid="Tidal:radio:artist/3667" trackstationid="Tidal:radio:track/2618174">
    <art>Joshua Bell</art>
    <alb>Angels &amp; Demons (Original Motion Picture Soundtrack)</alb>
    <title>503 (From "Angels &amp; Demons" Soundtrack)</title>
    <track>9</track>
    <discno>1</discno>
    <time>134</time>
    <fn>Tidal:2618174</fn>
    <quality>cd</quality>
  </song>
  <song albumid="288467" artistid="34474" songid="Tidal:288477" isFavourite="1" similarstationid="Tidal:radio:artist/34474" trackstationid="Tidal:radio:track/288477">
    <art>David Holmes</art>
    <alb>Ocean's Twelve (Music from the Motion Picture)</alb>
    <title>7-29-04 The Day Of</title>
    <track>10</track>
    <discno>1</discno>
    <time>192</time>
    <fn>Tidal:288477</fn>
    <quality>cd</quality>
  </song>
  <song albumid="34178238" artistid="3957214" songid="Tidal:34178241" isFavourite="1" similarstationid="Tidal:radio:artist/3957214" trackstationid="Tidal:radio:track/34178241">
    <art>The Connells</art>
    <alb>Ring</alb>
    <title>'74-'75</title>
    <track>3</track>
    <discno>1</discno>
    <time>279</time>
    <fn>Tidal:34178241</fn>
    <quality>cd</quality>
  </song>
  <song albumid="93204558" artistid="8177845" songid="Tidal:93204559" isFavourite="1" similarstationid="Tidal:radio:artist/8177845" trackstationid="Tidal:radio:track/93204559">
    <art>Why Don't We</art>
    <alb>8 Letters</alb>
    <title>8 Letters</title>
    <track>1</track>
    <discno>1</discno>
    <time>190</time>
    <fn>Tidal:93204559</fn>
    <quality>cd</quality>
  </song>
  <song albumid="103386824" artistid="3560792" songid="Tidal:103386825" isFavourite="1" similarstationid="Tidal:radio:artist/3560792" trackstationid="Tidal:radio:track/103386825">
    <art>Ólafur Arnalds</art>
    <alb>Stare</alb>
    <title>a1</title>
    <track>1</track>
    <discno>1</discno>
    <time>425</time>
    <fn>Tidal:103386825</fn>
    <quality>cd</quality>
  </song>
  <song albumid="76226961" artistid="3930594" songid="Tidal:76226962" isFavourite="1" similarstationid="Tidal:radio:artist/3930594" trackstationid="Tidal:radio:track/76226962">
    <art>Direct</art>
    <alb>Abandon</alb>
    <title>Abandon</title>
    <track>1</track>
    <discno>1</discno>
    <time>204</time>
    <fn>Tidal:76226962</fn>
    <quality>cd</quality>
  </song>
  <song albumid="125079029" artistid="3853899" so
... truncated; the whole body is in raw/374-browse.xml
```

## `/Status`

GET `/Status` — probe `035-env`, application/xml, byte-for-byte what the device sent.

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

GET `/SyncStatus` — probe `001-env`, application/xml, 2 redaction edit(s).

```xml
<?xml version="1.0" ?>
<SyncStatus etag="523" syncStat="523" version="4.16.22" id="192.0.2.11:11000" db="-49.1" volume="20" name="Stue" model="N132" modelName="NODE" class="streamer" icon="/images/players/N125_sub.png" brand="Bluesound" schemaVersion="34" initialized="true" mac="02:00:00:00:00:0B" hasSubwoofer="true">
  <pairWithSub/>
  <bluetoothOutput/>
</SyncStatus>
```

## `/Version`

GET `/Version` — probe `134-ports`, application/xml, byte-for-byte what the device sent.

```xml
<?xml version="1.0" ?>
<version>v0.4.13</version>
```

## `/Volume`

GET `/Volume` — probe `007-env`, application/xml, byte-for-byte what the device sent.

```xml
<?xml version="1.0" ?>
<volume db="-49.1" offsetDb="10" mute="0" etag="a79f2e9d2881ae370f00800f9d0a2c26" source="">20</volume>
```

## `/ui/Configuration`

GET `/ui/Configuration` — probe `116-ports`, application/xml, byte-for-byte what the device sent.

```xml
<?xml version="1.0" ?>
<configuration>
  <item id="home" URI="/ui/Home"/>
  <item id="recentlyPlayed" URI="/ui/RecentlyPlayed"/>
  <item id="news" URI="/ui/News"/>
  <item id="favourites" URI="/ui/Favourites"/>
  <item id="sources" URI="/ui/Sources"/>
  <item id="search" URI="/ui/Search"/>
  <item id="nowPlayingContextMenu" URI="/ui/nowPlayingCM" resultType="contextMenu"/>
  <item id="queueItemContextMenu" URI="/ui/queueItemCM" resultType="contextMenu"/>
  <item id="resolveSoviURL" URI="/ui/resolveSoviURL"/>
  <item id="queue" URI="/ui/Queue" resultType="queue"/>
  <item id="presets" URI="/ui/presets"/>
</configuration>
```

## `/ui/Favourites`

GET `/ui/Favourites` — probe `146-ports`, application/xml, byte-for-byte what the device sent.

```xml
<?xml version="1.0" ?>
<screen xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:noNamespaceSchemaLocation="screen.xsd" version="1" screenTitle="Favourites" id="screen-LocalMusic-Favourites" service="LocalMusic">
  <selectorMenu menuTitle="Select Service" replaceScreen="false">
    <item icon="/images/LibraryIcon.png?style=Default" text="Library" selected="true">
      <action type="player-link" URI="/ui/action?CfavouritesService=LocalMusic" refreshScreen="true"/>
    </item>
    <item icon="/Sources/images/TidalIcon.png?style=Default" text="TIDAL">
      <action type="player-link" URI="/ui/action?CfavouritesService=Tidal" refreshScreen="true"/>
    </item>
    <item icon="/Sources/images/TuneInIcon.png?style=Default" text="TuneIn">
      <action type="player-link" URI="/ui/action?CfavouritesService=TuneIn" refreshScreen="true"/>
    </item>
  </selectorMenu>
  <infoPanel icon="/images/ui/ic_info_favourites.png" text="You don't have any Favourites on Library" subText="You can add any content within Library as a favourite to have it show up here."/>
</screen>
```

## `/ui/Home`

GET `/ui/Home` — probe `143-ports`, application/xml, 11 redaction edit(s).

```xml
<?xml version="1.0" ?>
<screen xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:noNamespaceSchemaLocation="screen.xsd" version="1" screenTitle="Home" id="screen-home" refreshOnPlayerChange="true">
  <refreshOnStatusChange key="prid" value="1"/>
  <menuAction type="settings">
    <action type="deep-link" URI="/settings"/>
  </menuAction>
  <row id="teaser" scrollable="true" solidBackground="false" noReorder="true">
    <teaser id="add-service" title="Add your Music Service" body="BluOS supports a broad number of music services." backgroundImage="/images/ui/ic_teaser_add_service.png" closable="true">
      <action type="webpage" URI="/redirectToCp?href=%2Fservices%3Fnoheader%3D1%26schemaVersion%3D35"/>
      <button text="Add Music Service" backgroundColor="#00a4cb" textColor="#ffffff">
        <action type="webpage" URI="/redirectToCp?href=%2Fservices%3Fnoheader%3D1%26schemaVersion%3D35"/>
      </button>
    </teaser>
    <teaser id="qbm-education" title="Queue Builder Mode" body="This BluOS version adds an enhanced way of creating &amp; managing your Play Queues and Playlists within BluOS." backgroundImage="/images/ui/ic_teaser_queue_builder.png" closable="true">
      <action type="deep-link" URI="/qbm-education"/>
      <button text="Explore Queue Builder Mode" backgroundColor="#00a4cb" textColor="#ffffff">
        <action type="deep-link" URI="/qbm-education"/>
      </button>
    </teaser>
  </row>
  <row id="mostUsed" title="Most Used" scrollable="true" solidBackground="false">
    <source icon="/images/capture/ic_tv.png" title="HDMI ARC">
      <button text="Play" backgroundColor="#43a4ce" textColor="#ffffff">
        <action type="player-link" URI="/Play?url=Capture%3Ahw%3Aimxspdif%2C0%2F1%2F25%2F2%3Fid%3Dinput2" haptic="true"/>
      </button>
      <button text="Settings" backgroundColor="#292D2F" textColor="#ffffff" icon="/image/icon_settings.png">
        <action type="setting" URI="/Settings?id=capture-input2"/>
      </button>
      <action type="player-link" URI="/Play?url=Capture%3Ahw%3Aimxspdif%2C0%2F1%2F25%2F2%3Fid%3Dinput2" haptic="true"/>
      <nowPlayingMatch key="inputId" value="input2"/>
    </source>
    <source icon="/images/ui/Source/TidalLogo.png">
      <button text="My Music" backgroundColor="#ffffff" textColor="#1e2223">
        <action type="browse" URI="/ui/Favourites?service=Tidal&amp;singleService=1&amp;title=My+Music" resultType="screen" title="My Music" service="Tidal"/>
      </button>
      <button text="New" backgroundColor="#292D2F" textColor="#ffffff">
        <action type="browse" URI="/ui/browseMenuGroup?service=Tidal&amp;menuGroupId=Tidal-New" resultType="screen" title="New"/>
      </button>
      <action type="browse" URI="/ui/browseMenuGroup?service=Tidal" resultType="screen" title="TIDAL" service="Tidal"/>
    </source>
    <source icon="/images/ui/Source/RadioParadiseLogo.png">
      <button text="Play Main Mix" backgroundColor="#f8cc82" textColor="#1e2223">
        <action type="player-link" URI="/Play?url=RadioParadise%3A" haptic="true"/>
      </button>
      <button text="Browse" backgroundColor="#292D2F" textColor="#ffffff">
        <action type="browse" URI="/ui/browseMenuGroup?service=RadioParadise" resultType="screen" title="Radio Paradise" service="RadioParadise"/>
      </button>
      <action type="browse" URI="/ui/browseMenuGroup?service=RadioParadise" resultType="screen" title="Radio Paradise" service="RadioParadise"/>
    </source>
  </row>
  <row id="presets" title="Presets" solidBackground="true">
    <menuAction text="View All">
      <action type="browse" URI="/ui/presets" resultType="screen" title="Presets"/>
    </menuAction>
    <smallThumbnail title="Sunday Chill Mix: Ministry of Sound" icon="/Artwork?service=Tidal&amp;playlistimage=f8601f52-6d31-43bd-97a7-020000000002">
      <action type="player-link" URI="/Preset?id=1" haptic="true"/>
    </smallThumbnail>
    <smallThumbnail icon="/images/ui/ic_small_thumbnail_add.png">
      <action type="deep-link" URI="/add-preset"/>
    </smallThumbnail>
  </row>
  <row id="recent-stations" title="Recent Stations" scrollable="true" solidBackground="false">
    <menuAction text="Clear">
      <action type="player-link" URI="/ui/clearUsageHistory?stations=1" refreshScreen="true" haptic="true"/>
    </menuAction>
    <largeThumbnail image="https://img.radioparadise.com/channels/0/0/cover_512x512/0.jpg" title="The Main Mix" icon="/Sources/images/RadioParadiseIcon.png?style=Default">
      <action type="player-link" URI="/ui/prf?u=%2FPlay%3Furl%3DRadioParadise%253A%252F0%253A20%26title1%3DThe%2BMain%2BMix%26image%3Dhttps%253A%252F%252Fimg.radioparadise.com%252Fchannels%252F0%252F0%252Fcover_512x512%252F0.jpg" haptic="true"/>
      <playAction type="player-link" URI="/ui/prf?u=%2FPlay%3Furl%3DRadioParadise%253A%252F0%253A20%26title1%3DThe%2BMain%2BMix%26image%3Dhttps%253A%252F%252Fimg.radioparadise.com%252Fchannels%252F0%252F0%252Fcover_512x512%252F0.jpg" haptic="true"/>
      <nowPlayingMatch key="streamUrl" value="RadioParadise:/0:20"/>
    </largeThumbnail>
    <largeThumbnail image="https://img.radioparadise.com/channels/0/0/cover_512x512/0.jpg" title="The Main Mix (CD)" icon="/Sources/images/RadioParadiseIcon.png?style=Default">
      <action type="player-link" URI="/ui/prf?u=%2FPlay%3Furl%3DRadioParadise%253A%252F0%253A4%26title1%3DThe%2520Main%2520Mix%26image%3Dhttps%253A%252F%252Fimg.radioparadise.com%252Fchannels%252F0%252F0%252Fcover_512x512%252F0.jpg" haptic="true"/>
      <playAction type="player-link" URI="/ui/prf?u=%2FPlay%3Furl%3DRadioParadise%253A%252F0%253A4%26title1%3DThe%2520Main%2520Mix%26image%3Dhttps%253A%252F%252Fimg.radioparadise.com%252Fchannels%252F0%252F0%252Fcover_512x512%252F0.jpg" haptic="true"/>
      <nowPlayingMatch key="streamUrl" value="RadioParadise:/0:4"/>
    </largeThumbnail>
    <largeThumbnail image="/Artwork?service=Tidal&amp;albumid=366537329" title="My Name Radio" icon="/Sources/images/TidalIcon.png?style=Default">
      <action 
... truncated; the whole body is in raw/143-ports.xml
```

## `/ui/News`

GET `/ui/News` — probe `145-ports`, application/xml, byte-for-byte what the device sent.

```xml
<?xml version="1.0" ?>
<screen xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:noNamespaceSchemaLocation="screen.xsd" version="1" screenTitle="News &amp; Updates" id="screen-news" refreshOnPlayerChange="true">
  <list id="news"/>
</screen>
```

## `/ui/Queue`

GET `/ui/Queue` — probe `152-ports`, application/xml, byte-for-byte what the device sent.

```xml
<?xml version="1.0" ?>
<queue offset="0" total="37" id="1193" modified="false">
  <refreshOnStatusChange key="pid" value="1193"/>
  <button text="Save" backgroundColor="#2A2A2A" textColor="#ffffff" icon="/images/ui/btn_save_queue.png">
    <action type="browse" URI="/AddToPlaylistOptions?saveQueue=1" resultType="SaveQueueOptions" title="Save playlist"/>
  </button>
  <button text="Edit" backgroundColor="#2A2A2A" textColor="#ffffff" icon="/images/ui/btn_edit_queue.png">
    <action type="deep-link" URI="/edit-queue"/>
  </button>
  <button text="Clear" backgroundColor="#2A2A2A" textColor="#ffffff" icon="/images/ui/btn_clear_queue.png">
    <action type="player-link" URI="/Clear" refreshScreen="true" haptic="true" notification="Play Queue cleared"/>
  </button>
  <button text="Queue builder mode" backgroundColor="#2A2A2A" textColor="#ffffff" icon="/images/ui/btn_qbm.png">
    <action type="player-link" URI="/ui/action?CBQ=true" event="qbm_toggle:qbm=true" refreshScreen="true"/>
  </button>
  <item image="/Artwork?service=Tidal&amp;songid=Tidal%3A122288231" icon="/Sources/images/TidalIcon.png?style=Default" title="How Many Times" subTitle="Andhim" subSubTitle="Simmer Down" quality="cd" duration="4:27">
    <action type="player-link" URI="/Play?id=0" haptic="true"/>
    <contextMenu type="browse" URI="/ui/queueItemCM?id=0" resultType="contextMenu"/>
    <nowPlayingMatch key="song" value="0"/>
  </item>
  <item image="/Artwork?service=Tidal&amp;songid=Tidal%3A64753254" icon="/Sources/images/TidalIcon.png?style=Default" title="I'm In Control" subTitle="AlunaGeorge" subSubTitle="I Remember" quality="cd" duration="3:29">
    <action type="player-link" URI="/Play?id=1" haptic="true"/>
    <contextMenu type="browse" URI="/ui/queueItemCM?id=1" resultType="contextMenu"/>
    <nowPlayingMatch key="song" value="1"/>
  </item>
  <item image="/Artwork?service=Tidal&amp;songid=Tidal%3A53780764" icon="/Sources/images/TidalIcon.png?style=Default" title="Blind (feat. Emmi) [Radio Edit]" subTitle="Feder" quality="cd" duration="3:14">
    <action type="player-link" URI="/Play?id=2" haptic="true"/>
    <contextMenu type="browse" URI="/ui/queueItemCM?id=2" resultType="contextMenu"/>
    <nowPlayingMatch key="song" value="2"/>
  </item>
  <item image="/Artwork?service=Tidal&amp;songid=Tidal%3A42943871" icon="/Sources/images/TidalIcon.png?style=Default" title="Ain't Nobody (Loves Me Better)" subTitle="Felix Jaehn" quality="cd" duration="3:06">
    <action type="player-link" URI="/Play?id=3" haptic="true"/>
    <contextMenu type="browse" URI="/ui/queueItemCM?id=3" resultType="contextMenu"/>
    <nowPlayingMatch key="song" value="3"/>
  </item>
  <item image="/Artwork?service=Tidal&amp;songid=Tidal%3A48537288" icon="/Sources/images/TidalIcon.png?style=Default" title="Sugar (feat. Francesco Yates)" subTitle="Robin Schulz" quality="cd" duration="3:39">
    <action type="player-link" URI="/Play?id=4" haptic="true"/>
    <contextMenu type="browse" URI="/ui/queueItemCM?id=4" resultType="contextMenu"/>
    <nowPlayingMatch key="song" value="4"/>
  </item>
  <item image="/Artwork?service=Tidal&amp;songid=Tidal%3A52891347" icon="/Sources/images/TidalIcon.png?style=Default" title="Gold" subTitle="Kiiara" quality="cd" duration="3:46">
    <action type="player-link" URI="/Play?id=5" haptic="true"/>
    <contextMenu type="browse" URI="/ui/queueItemCM?id=5" resultType="contextMenu"/>
    <nowPlayingMatch key="song" value="5"/>
  </item>
  <item image="/Artwork?service=Tidal&amp;songid=Tidal%3A51557046" icon="/Sources/images/TidalIcon.png?style=Default" title="Lay It All on Me (feat. Ed Sheeran)" subTitle="Rudimental" subSubTitle="We the Generation (Deluxe Edition)" quality="cd" duration="4:02">
    <action type="player-link" URI="/Play?id=6" haptic="true"/>
    <contextMenu type="browse" URI="/ui/queueItemCM?id=6" resultType="contextMenu"/>
    <nowPlayingMatch key="song" value="6"/>
  </item>
  <item image="/Artwork?service=Tidal&amp;songid=Tidal%3A177600702" icon="/Sources/images/TidalIcon.png?style=Default" title="Don't Be so Shy" subTitle="Imany" subSubTitle="The Wrong Kind of War" quality="cd" duration="3:11">
    <action type="player-link" URI="/Play?id=7" haptic="true"/>
    <contextMenu type="browse" URI="/ui/queueItemCM?id=7" resultType="contextMenu"/>
    <nowPlayingMatch key="song" value="7"/>
  </item>
  <item image="/Artwork?service=Tidal&amp;songid=Tidal%3A243118147" icon="/Sources/images/TidalIcon.png?style=Default" title="Stay Lost" subTitle="Joe Hertz" subSubTitle="Chapter One" quality="cd" duration="3:50">
    <action type="player-link" URI="/Play?id=8" haptic="true"/>
    <contextMenu type="browse" URI="/ui/queueItemCM?id=8" resultType="contextMenu"/>
    <nowPlayingMatch key="song" value="8"/>
  </item>
  <item image="/Artwork?service=Tidal&amp;songid=Tidal%3A117920814" icon="/Sources/images/TidalIcon.png?style=Default" title="Moments" subTitle="Kidnap" quality="cd" duration="5:03">
    <action type="player-link" URI="/Play?id=9" haptic="true"/>
    <contextMenu type="browse" URI="/ui/queueItemCM?id=9" resultType="contextMenu"/>
    <nowPlayingMatch key="song" value="9"/>
  </item>
  <item image="/Artwork?service=Tidal&amp;songid=Tidal%3A58439724" icon="/Sources/images/TidalIcon.png?style=Default" title="All My Friends (feat. Tinashe &amp; Chance the Rapper)" subTitle="Snakehips" subSubTitle="All My Friends (The Remixes) (feat. Tinashe &amp; Chance the Rapper)" quality="cd" duration="5:55">
    <action type="player-link" URI="/Play?id=10" haptic="true"/>
    <contextMenu type="browse" URI="/ui/queueItemCM?id=10" resultType="contextMenu"/>
    <nowPlayingMatch key="song" value="10"/>
  </item>
  <item image="/Artwork?service=Tidal&amp;songid=Tidal%3A59413016" icon="/Sources/images/TidalIcon.png?style=Default" title="Who Am I" subTitle="Katy B" subSubTitle="Honey" quality="cd" duration="3:24">
    <action type="player-link" URI="/Play?id=11" haptic="true"/>
    <contextMenu type="browse" URI="/ui/queueItemCM?i
... truncated; the whole body is in raw/152-ports.xml
```

## `/ui/RecentlyPlayed`

GET `/ui/RecentlyPlayed` — probe `144-ports`, application/xml, 70 redaction edit(s).

```xml
<?xml version="1.0" ?>
<screen xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:noNamespaceSchemaLocation="screen.xsd" version="1" screenTitle="Recently Played" id="screen-recentlyPlayed" refreshOnPlayerChange="true">
  <menuAction text="Clear">
    <action type="player-link" URI="/ui/clearUsageHistory?queued=1" refreshScreen="true" closeScreen="true" haptic="true"/>
  </menuAction>
  <list id="recent">
    <item image="/Artwork?service=Tidal&amp;playlistimage=f8601f52-6d31-43bd-97a7-020000000002" objectType="playlist" icon="/Sources/images/TidalIcon.png?style=Default" title="Sunday Chill Mix: Ministry of Sound" subSubTitle="51 Tracks • 3:11:42">
      <action type="browse" URI="/ui/browseContext?service=Tidal&amp;title=Sunday+Chill+Mix%3A+Ministry+of+Sound&amp;type=Playlist&amp;url=%2FPlaylists%3Fservice%3DTidal%26playlist%3DSunday%2BChill%2BMix%253A%2BMinistry%2Bof%2BSound%26playlistid%3Df6bddb25-a5dc-4658-993d-020000000001" resultType="screen" title="Sunday Chill Mix: Ministry of Sound" service="Tidal"/>
      <contextMenu type="browse" URI="/ui/ContextMenu?context=Playlist&amp;image=%2FArtwork%3Fservice%3DTidal%26playlistimage%3Df8601f52-6d31-43bd-97a7-020000000002&amp;isFavourite=1&amp;playlist=Sunday+Chill+Mix%3A+Ministry+of+Sound&amp;playlistid=f6bddb25-a5dc-4658-993d-020000000001&amp;preset_url=%2FLoad%3Fservice%3DTidal%26id%3Df6bddb25-a5dc-4658-993d-020000000001&amp;service=Tidal&amp;title=Sunday+Chill+Mix%3A+Ministry+of+Sound&amp;noFavCMItems=1" resultType="contextMenu"/>
    </item>
    <item image="/Artwork?service=Tidal&amp;songid=Tidal%3A140768093" objectType="song" icon="/Sources/images/TidalIcon.png?style=Default" title="Peace of Mind" subTitle="AK • Peace of Mind" quality="cd" duration="3:30">
      <action type="player-link" URI="/ui/prf?u=%2FAdd%3Fplaynow%3D1%26file%3DTidal%253A140768093" haptic="true"/>
      <contextMenu type="browse" URI="/ui/ContextMenu?album=Peace+of+Mind&amp;albumid=140768092&amp;artist=AK&amp;artistid=15706940&amp;context=Song&amp;filename=Tidal%3A140768093&amp;isFavourite=1&amp;service=Tidal&amp;similarstationid=Tidal%3Aradio%3Aartist%2F15706940&amp;songid=Tidal%3A140768093&amp;title=Peace+of+Mind&amp;trackstationid=Tidal%3Aradio%3Atrack%2F140768093&amp;noFavCMItems=1" resultType="contextMenu"/>
    </item>
    <item image="/Artwork?service=Tidal&amp;songid=Tidal%3A106600734" objectType="song" icon="/Sources/images/TidalIcon.png?style=Default" title="Traust" subTitle="Heilung • Futha" quality="cd" duration="9:49">
      <action type="player-link" URI="/ui/prf?u=%2FAdd%3Fplaynow%3D1%26file%3DTidal%253A106600734" haptic="true"/>
      <contextMenu type="browse" URI="/ui/ContextMenu?album=Futha&amp;albumid=106600730&amp;artist=Heilung&amp;artistid=4656760&amp;context=Song&amp;filename=Tidal%3A106600734&amp;isFavourite=1&amp;service=Tidal&amp;similarstationid=Tidal%3Aradio%3Aartist%2F4656760&amp;songid=Tidal%3A106600734&amp;title=Traust&amp;trackstationid=Tidal%3Aradio%3Atrack%2F106600734&amp;noFavCMItems=1" resultType="contextMenu"/>
    </item>
    <item image="https://images.tidal.com/0/EIAFGIAFIMACKMAC/CAEaJDQ2MTI4MTUxLzhlOWYvNDJhMC84ZjgwLzlmMjY3ZDViZWZlZRokYmUyMDA4ODQvZDliOC80MjA1L2IzM2IvZWI0YzMxNWFjODM4GiRkODVmOTkwMS83OWNhLzRmMDcvODQ5OC9mODc1Zjk5ZmFmYWQiATIqByNEOERCRjEwAg?token=[REDACTED-value-2]" objectType="playlist" icon="/Sources/images/TidalIcon.png?style=Default" title="My Mix 2">
      <action type="browse" URI="/ui/browseContext?service=Tidal&amp;title=My+Mix+2&amp;type=Playlist&amp;url=%2FPlaylists%3Fservice%3DTidal%26playlist%3DMy%2BMix%2B2%26playlistid%3Dmix%253A00221fe70fc48ccb410e4f67956209" resultType="screen" title="My Mix 2" service="Tidal"/>
      <contextMenu type="browse" URI="/ui/ContextMenu?context=Playlist&amp;image=https%3A%2F%2Fimages.tidal.com%2F0%2FEIAFGIAFIMACKMAC%2FCAEaJDQ2MTI4MTUxLzhlOWYvNDJhMC84ZjgwLzlmMjY3ZDViZWZlZRokYmUyMDA4ODQvZDliOC80MjA1L2IzM2IvZWI0YzMxNWFjODM4GiRkODVmOTkwMS83OWNhLzRmMDcvODQ5OC9mODc1Zjk5ZmFmYWQiATIqByNEOERCRjEwAg%3Ftoken%3D46d73575b3a1f5f93961b247d0181c8da7e80133&amp;mymix=1&amp;playlist=My+Mix+2&amp;playlistid=mix%3A00221fe70fc48ccb410e4f67956209&amp;preset_url=%2FLoad%3Fservice%3DTidal%26id%3Dmix%3A00221fe70fc48ccb410e4f67956209&amp;service=Tidal&amp;title=My+Mix+2&amp;noFavCMItems=1" resultType="contextMenu"/>
    </item>
    <item image="/Artwork?service=Tidal&amp;songid=Tidal%3A118256186" objectType="song" icon="/Sources/images/TidalIcon.png?style=Default" title="Daydreaming" subTitle="Marion • Daydreaming" quality="cd" duration="4:19">
      <action type="player-link" URI="/ui/prf?u=%2FAdd%3Fplaynow%3D1%26file%3DTidal%253A118256186" haptic="true"/>
      <contextMenu type="browse" URI="/ui/ContextMenu?album=Daydreaming&amp;albumid=118256185&amp;artist=Marion&amp;artistid=31563632&amp;context=Song&amp;filename=Tidal%3A118256186&amp;isFavourite=1&amp;service=Tidal&amp;similarstationid=Tidal%3Aradio%3Aartist%2F31563632&amp;songid=Tidal%3A118256186&amp;title=Daydreaming&amp;trackstationid=Tidal%3Aradio%3Atrack%2F118256186&amp;noFavCMItems=1" resultType="contextMenu"/>
    </item>
    <item image="/Artwork?service=Tidal&amp;songid=Tidal%3A92063044" objectType="song" icon="/Sources/images/TidalIcon.png?style=Default" title="Nightfall (feat. 4lienetic)" subTitle="Andy Leech • Nightfall (feat. 4lienetic)" quality="cd" duration="4:48">
      <action type="player-link" URI="/ui/prf?u=%2FAdd%3Fplaynow%3D1%26file%3DTidal%020000000009" haptic="true"/>
      <contextMenu type="browse" URI="/ui/ContextMenu?album=Nightfall+%28feat.+4lienetic%29&amp;albumid=92063043&amp;artist=Andy+Leech&amp;artistid=8995825&amp;context=Song&amp;filename=Tidal%3A92063044&amp;isFavourite=1&amp;service=Tidal&amp;similarstationid=Tidal%3Aradio%3Aartist%2F8995825&amp;songid=Tidal%3A92063044&amp;title=Nightfall+%28feat.+4lienetic%29&amp;trackstationid=Tidal%3Aradio%3Atrack%2F92063044&amp;noFavCMItems=1" resultType="contextMenu"/>
    </item>
    <item image="/Artwork?service=Tidal&amp;songid=Tidal%3A482411348" obje
... truncated; the whole body is in raw/144-ports.xml
```

## `/ui/Search`

GET `/ui/Search` — probe `148-ports`, application/xml, byte-for-byte what the device sent.

```xml
<?xml version="1.0" ?>
<screen xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:noNamespaceSchemaLocation="screen.xsd" version="1" screenTitle="Search" id="screen-LocalMusic-Search" service="LocalMusic">
  <selectorMenu replaceScreen="false">
    <item icon="/images/LibraryIcon.png?style=Default" text="Library" selected="true">
      <action type="browse" URI="/ui/Search?CsearchService=LocalMusic" resultType="screen" title="Search"/>
    </item>
    <item icon="/Sources/images/BluOSRadioIcon.png?style=Default" text="Radio">
      <action type="browse" URI="/ui/Search?CsearchService=Airable" resultType="screen" title="Search"/>
    </item>
    <item icon="/Sources/images/TidalIcon.png?style=Default" text="TIDAL">
      <action type="browse" URI="/ui/Search?CsearchService=Tidal" resultType="screen" title="Search"/>
    </item>
    <item icon="/Sources/images/TuneInIcon.png?style=Default" text="TuneIn">
      <action type="browse" URI="/ui/Search?CsearchService=TuneIn" resultType="screen" title="Search"/>
    </item>
  </selectorMenu>
  <search prompt="Search..." parameterName="q" type="browse" URI="/ui/Search?forService=LocalMusic" resultType="screen" title="Search" service="LocalMusic"/>
</screen>
```

## `/ui/Sources`

GET `/ui/Sources` — probe `147-ports`, application/xml, byte-for-byte what the device sent.

```xml
<?xml version="1.0" ?>
<screen xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:noNamespaceSchemaLocation="screen.xsd" version="1" screenTitle="Music Sources" id="screen-sources" refreshOnPlayerChange="true">
  <refreshOnStatusChange key="sid" value="51"/>
  <menuAction type="add">
    <action type="webpage" URI="/redirectToCp?href=%2Fservices%3Fnoheader%3D1%26schemaVersion%3D35" title="Music Services" refreshScreen="true"/>
  </menuAction>
  <row id="inputs" title="Inputs" scrollable="true" solidBackground="false">
    <menuAction text="Customise">
      <action type="setting" URI="/Settings?id=capture" title="Inputs" refreshScreen="true"/>
    </menuAction>
    <input title="HDMI ARC" icon="/images/capture/ic_tv.png">
      <action type="player-link" URI="/Play?url=Capture%3Ahw%3Aimxspdif%2C0%2F1%2F25%2F2%3Fid%3Dinput2&amp;title=HDMI+ARC&amp;image=%2Fimages%2Fcapture%2Fic_tv.png" haptic="true"/>
      <nowPlayingMatch key="inputId" value="input2"/>
    </input>
  </row>
  <row id="services" title="Music Services" solidBackground="false">
    <menuAction text="Manage">
      <action type="webpage" URI="/redirectToCp?href=%2Fservices%3Fnoheader%3D1%26schemaVersion%3D35" title="Music Services" refreshScreen="true"/>
    </menuAction>
    <list>
      <service icon="/images/ui/Source/LibrarySourceIcon.png" title="Library" isLink="true">
        <action type="browse" URI="/ui/browseMenuGroup?service=LocalMusic" resultType="screen" title="Library" service="LocalMusic"/>
        <nowPlayingMatch key="service" value="LocalMusic"/>
      </service>
      <service icon="/images/ui/Source/BluOSRadioSourceIcon.png" title="Radio" isLink="true">
        <action type="browse" URI="/ui/browseMenuGroup?service=Airable" resultType="screen" title="Radio" service="Airable"/>
        <nowPlayingMatch key="service" value="Airable"/>
      </service>
      <service icon="/images/ui/Source/RadioParadiseSourceIcon.png" title="Radio Paradise" isLink="true">
        <action type="browse" URI="/ui/browseMenuGroup?service=RadioParadise" resultType="screen" title="Radio Paradise" service="RadioParadise"/>
        <nowPlayingMatch key="service" value="RadioParadise"/>
      </service>
      <service icon="/images/ui/Source/SpotifySourceIcon.png" title="Spotify" isLink="false">
        <action type="player-link" URI="/Play?url=Spotify%3Aplay&amp;title=Spotify&amp;image=%2FSources%2Fimages%2FSpotifyIcon.png" haptic="true"/>
      </service>
      <service icon="/images/ui/Source/TidalSourceIcon.png" title="TIDAL" isLink="true">
        <action type="browse" URI="/ui/browseMenuGroup?service=Tidal" resultType="screen" title="TIDAL" service="Tidal"/>
        <nowPlayingMatch key="service" value="Tidal"/>
      </service>
      <service icon="/images/ui/Source/TuneInSourceIcon.png" title="TuneIn" isLink="true">
        <action type="browse" URI="/ui/browseMenuGroup?service=TuneIn" resultType="screen" title="TuneIn" service="TuneIn"/>
        <nowPlayingMatch key="service" value="TuneIn"/>
      </service>
    </list>
  </row>
</screen>
```

## `/ui/nowPlayingCM`

GET `/ui/nowPlayingCM` — probe `149-ports`, application/xml, 1 redaction edit(s).

```xml
<?xml version="1.0" ?>
<contextMenu xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" image="/Artwork?service=Tidal&amp;songid=Tidal%3A48513985" subTitle="Alex Adair • Heaven" title="Heaven" version="1" xsi:noNamespaceSchemaLocation="screen.xsd">
  <item icon="/images/ui/cm_favourite_add.png" text="Favourite">
    <action type="player-link" URI="/AddFavourite?service=Tidal&amp;songid=Tidal%3A48513985" refreshScreen="true" haptic="true" notification="Added to favourites" notificationIcon="/images/ui/cm_favourite_add.png"/>
  </item>
  <item icon="/images/ui/cm_addtoplaylist.png" text="Add to playlist…">
    <action type="browse" URI="/AddToPlaylistOptions?service=Tidal&amp;songid=Tidal%3A48513985" resultType="AddToPlaylistOptions" title="Add to playlist…" service="Tidal"/>
  </item>
  <item icon="/images/ui/cm_playRadio.png" text="Track radio">
    <action type="player-link" URI="/ui/prf?u=%2FPlay%3Fservice%3DTidal%26url%3DTidal%253Aradio%253Atrack%02000000003B" haptic="true"/>
  </item>
  <item icon="/images/ui/cm_playRadio.png" text="Related artists radio">
    <action type="player-link" URI="/ui/prf?u=%2FPlay%3Fservice%3DTidal%26url%3DTidal%253Aradio%253Aartist%252F6081277" haptic="true"/>
  </item>
  <item icon="/images/ui/cm_gotoalbum.png" text="Go to album">
    <action type="browse" URI="/ui/browseContext?service=Tidal&amp;title=Heaven&amp;type=Album&amp;url=%2FAlbums%3Falbumid%3D48513984%26service%3DTidal" resultType="screen" title="Heaven" service="Tidal"/>
  </item>
  <item icon="/images/ui/cm_gotoartist.png" text="Go to artist">
    <action type="browse" URI="/ui/browseContext?service=Tidal&amp;title=Alex+Adair&amp;type=Artist&amp;url=%2FArtists%3Fartistid%3D6081277%26service%3DTidal" resultType="screen" title="Alex Adair" service="Tidal"/>
  </item>
  <item icon="/images/ui/cm_info.png" text="Info">
    <action type="browse" URI="/Info?album=Heaven&amp;albumid=48513984&amp;artist=Alex+Adair&amp;service=Tidal" resultType="Info" title="Info" service="Tidal"/>
  </item>
</contextMenu>
```

## `/ui/presets`

GET `/ui/presets` — probe `153-ports`, application/xml, 3 redaction edit(s).

```xml
<?xml version="1.0" ?>
<screen xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:noNamespaceSchemaLocation="screen.xsd" version="1" screenTitle="Presets" id="screen-presets" refreshOnPlayerChange="true" ìsPresets="true">
  <refreshOnStatusChange key="prid" value="1"/>
  <menuAction type="add">
    <action type="deep-link" URI="/add-preset" refreshScreen="true"/>
  </menuAction>
  <list>
    <item image="/Artwork?service=Tidal&amp;playlistimage=f8601f52-6d31-43bd-97a7-020000000002" title="Sunday Chill Mix: Ministry of Sound" counter="1" solidBackground="true">
      <action type="player-link" URI="/Preset?id=1" haptic="true"/>
      <contextMenu type="browse" URI="/ui/ContextMenu?id=1&amp;image=%2FArtwork%3Fservice%3DTidal%26playlistimage%3Df8601f52-6d31-43bd-97a7-020000000002&amp;name=Sunday+Chill+Mix%3A+Ministry+of+Sound&amp;type=preset&amp;url=%2FLoad%3Fservice%3DTidal%26id%3Df6bddb25-a5dc-4658-993d-020000000001" resultType="contextMenu" title="Sunday Chill Mix: Ministry of Sound"/>
    </item>
  </list>
  <footer text="Reorder Presets" type="reorder">
    <action type="deep-link" URI="/reorder-presets?url=%2FPresets%2Fedit%3Fprid%3D1" title="Reorder Presets" refreshScreen="true"/>
  </footer>
</screen>
```
