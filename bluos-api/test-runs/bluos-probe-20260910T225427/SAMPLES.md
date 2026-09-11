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
| `/AddSlave` | `261-state_grouping` | 200 | 96 | verbatim |
| `/Browse` | `173-state_source` | 200 | 983 | verbatim |
| `/Name` | `152-state_name` | 200 | 62 | verbatim |
| `/Pause` | `076-state_playback` | 200 | 59 | verbatim |
| `/Play` | `177-state_source` | 200 | 60 | verbatim |
| `/Preset` | `168-state_preset` | 200 | 93 | verbatim |
| `/Presets` | `164-state_preset` | 200 | 424 | 2 edit(s) |
| `/RadioBrowse` | `174-state_source` | 200 | 412 | verbatim |
| `/RemoveSlave` | `273-state_grouping` | 200 | 623 | 4 edit(s) |
| `/Repeat` | `084-state_playback` | 200 | 86 | verbatim |
| `/SetMaster` | `230-state_grouping` | 200 | 536 | 3 edit(s) |
| `/Shuffle` | `085-state_playback` | 200 | 105 | verbatim |
| `/SlaveVolume` | `259-state_grouping` | 200 | 88 | verbatim |
| `/Status` | `167-state_preset` | 200 | 1862 | verbatim |
| `/SyncStatus` | `272-state_grouping` | 200 | 623 | 4 edit(s) |
| `/Volume` | `008-state_volume` | 200 | 171 | verbatim |

## `/AddSlave`

GET `/AddSlave?slave=192.0.2.11&port=11000&channelMode=1` — probe `261-state_grouping`, application/xml, byte-for-byte what the device sent.

```xml
<?xml version="1.0" ?>
<error>failed, invalid channel-mode configuration</error>
```

## `/Browse`

GET `/Browse` — probe `173-state_source`, application/xml, byte-for-byte what the device sent.

```xml
<?xml version="1.0" ?>
<browse type="menu">
  <item browseKey="BluOS:" text="Playlists" image="/images/ci_myplaylists.png" type="link"/>
  <item playURL="/Play?url=Capture%3Ahw%3Aimxspdif%2C0%2F1%2F25%2F2%3Fid%3Dinput2" text="HDMI ARC" image="/images/capture/ic_tv.png" type="audio" inputType="arc"/>
  <item browseKey="LocalMusic:" text="Library" image="/images/LibraryIcon.png" type="link"/>
  <item browseKey="Airable:" text="Radio" image="/Sources/images/BluOSRadioIcon.png" type="link"/>
  <item browseKey="RadioParadise:" text="Radio Paradise" image="/Sources/images/RadioParadiseIcon.png" type="link"/>
  <item playURL="/Play?url=Spotify%3Aplay" text="Spotify" image="/Sources/images/SpotifyIcon.png" type="audio"/>
  <item browseKey="Tidal:" text="TIDAL" image="/Sources/images/TidalIcon.png" type="link"/>
  <item browseKey="TuneIn:" text="TuneIn" image="/Sources/images/TuneInIcon.png" type="link"/>
</browse>
```

## `/Name`

POST `/Name` — probe `152-state_name`, application/xml, byte-for-byte what the device sent.

```xml
<?xml version="1.0" ?>
<name>ProbeTest2</name>
```

## `/Pause`

GET `/Pause` — probe `076-state_playback`, application/xml, byte-for-byte what the device sent.

```xml
<?xml version="1.0" ?>
<state>pause</state>
```

## `/Play`

GET `/Play?url=Capture%3Ahw%3Aimxspdif%2C0%2F1%2F25%2F2%3Fid%3Dinput2` — probe `177-state_source`, application/xml, byte-for-byte what the device sent.

```xml
<?xml version="1.0" ?>
<state>stream</state>
```

## `/Preset`

GET `/Preset?id=2` — probe `168-state_preset`, application/xml, byte-for-byte what the device sent.

```xml
<?xml version="1.0" ?>
<loaded service="Tidal">
  <entries>20</entries>
</loaded>
```

## `/Presets`

GET `/Presets` — probe `164-state_preset`, application/xml, 2 redaction edit(s).

```xml
<?xml version="1.0" ?>
<presets prid="0">
  <preset id="1" name="RP Main Mix" url="RadioParadise:/0:4" image="https://img.radioparadise.com/source/27/channel_logo/chan_0.png"/>
  <preset id="2" name="Rolig musik" url="/Load?service=Tidal&amp;id=9977e64f-8df5-4967-9219-020000000001" image="/Artwork?service=Tidal&amp;playlistimage=6793e3e6-0a62-4921-8158-020000000002" volume="6"/>
</presets>
```

## `/RadioBrowse`

GET `/RadioBrowse?service=Capture` — probe `174-state_source`, application/xml, byte-for-byte what the device sent.

```xml
<?xml version="1.0" ?>
<radiotime service="Capture">
  <item text="HDMI ARC" id="input2" type="audio" inputType="arc" URL="Capture%3Ahw%3Aimxspdif%2C0%2F1%2F25%2F2%3Fid%3Dinput2" image="/images/capture/ic_tv.png" typeIndex="arc-1"/>
  <item text="Spotify" id="Spotify" type="audio" URL="Spotify%3Aplay" serviceType="CloudService" image="/Sources/images/SpotifyIcon.png"/>
</radiotime>
```

## `/RemoveSlave`

GET `/RemoveSlave` — probe `273-state_grouping`, application/xml, 4 redaction edit(s).

```xml
<?xml version="1.0" ?>
<SyncStatus etag="1019" syncStat="1019" version="4.16.22" id="192.0.2.12:11000" db="-44.3" volume="10" name="Kontor" model="N130" modelName="NODE" class="streamer" icon="/images/players/N125_nt.png" brand="Bluesound" schemaVersion="34" initialized="true" group="Kontor + 2" mac="02:00:00:00:00:0C">
  <slave id="192.0.2.13" port="11000" name="Køkken" model="N132" icon="/images/players/N125_nt.png"/>
  <slave id="192.0.2.11" port="11000" name="Stue" model="N132" icon="/images/players/N125_nt.png"/>
  <pairWithSub/>
  <bluetoothOutput/>
</SyncStatus>
```

## `/Repeat`

GET `/Repeat` — probe `084-state_playback`, application/xml, byte-for-byte what the device sent.

```xml
<?xml version="1.0" ?>
<error>
  <message>invalid state</message>
</error>
```

## `/SetMaster`

GET `/SetMaster?master=192.0.2.12&port=11000` — probe `230-state_grouping`, application/xml, 3 redaction edit(s).

```xml
<?xml version="1.0" ?>
<SyncStatus etag="245" syncStat="245" version="4.16.22" id="192.0.2.11:11000" db="-62.2" volume="10" name="Stue" model="N132" modelName="NODE" class="streamer" icon="/images/players/N125_sub.png" brand="Bluesound" schemaVersion="34" initialized="true" group="Stue+Kontor" mac="02:00:00:00:00:0B" hasSubwoofer="true">
  <slave id="192.0.2.12" port="11000" name="Kontor" model="N130" icon="/images/players/N125_nt.png"/>
  <pairWithSub/>
  <bluetoothOutput/>
</SyncStatus>
```

## `/Shuffle`

GET `/Shuffle` — probe `085-state_playback`, application/xml, byte-for-byte what the device sent.

```xml
<?xml version="1.0" ?>
<playlist length="30" id="1188" shuffle="0" repeat="2"/>
```

## `/SlaveVolume`

GET `/SlaveVolume?slave=192.0.2.11:11000&db=0` — probe `259-state_grouping`, application/xml, byte-for-byte what the device sent.

```xml
<?xml version="1.0" ?>
<error>not valid on non-zone-slave player</error>
```

## `/Status`

GET `/Status` — probe `167-state_preset`, application/xml, byte-for-byte what the device sent.

```xml
<?xml version="1.0" ?>
<status etag="7515148cb4bb27523b5b2a9c1b302c00">
  <actions>
    <action name="back" state="0"/>
    <action name="skip" url="/Action?service=RadioParadise&amp;next=2921366" state="0"/>
    <action name="love" url="/Action?service=RadioParadise&amp;love=37763&amp;reset=0" type="thumbs" state="-1" text="Love" icon="/images/loveban/love.png"/>
    <action name="ban" url="/Action?service=RadioParadise&amp;ban=37763&amp;reset=0" type="thumbs" state="-1" text="Ban" icon="/images/loveban/ban.png"/>
  </actions>
  <album>Eternal Sunshine of the Spotless Mind: Original Soundtrack</album>
  <artist>Beck</artist>
  <autofill>10</autofill>
  <canMovePlayback>true</canMovePlayback>
  <canSeek>0</canSeek>
  <currentImage>https://img.radioparadise.com/covers/l/13074.jpg</currentImage>
  <cursor>29</cursor>
  <db>-62.5</db>
  <image>https://img.radioparadise.com/covers/l/13074.jpg</image>
  <indexing>0</indexing>
  <infourl>https://en.wikipedia.org/wiki/</infourl>
  <lyricsid>37763</lyricsid>
  <mid>19</mid>
  <mode>1</mode>
  <mute>0</mute>
  <pid>3062</pid>
  <prid>0</prid>
  <repeat>2</repeat>
  <secs>0</secs>
  <service>RadioParadise</service>
  <serviceIcon>/Sources/images/RadioParadiseIcon.png</serviceIcon>
  <serviceName>Radio Paradise</serviceName>
  <serviceType>RadioService</serviceType>
  <shuffle>0</shuffle>
  <sid>49</sid>
  <sleep/>
  <song>0</song>
  <state>connecting</state>
  <stationImage>https://img.radioparadise.com/channels/0/0/cover_512x512/0.jpg</stationImage>
  <streamUrl>RadioParadise:/0:4</streamUrl>
  <syncStat>1847</syncStat>
  <title1>The Main Mix</title1>
  <title2>Everybody's Got To Learn Sometime</title2>
  <title3>Beck • Eternal Sunshine of the Spotless Mind: Original Soundtrack</title3>
  <totlen>322</totlen>
  <twoline_title1>The Main Mix</twoline_title1>
  <twoline_title2>Everybody's Got To Learn Sometime • Beck</twoline_title2>
  <volume>10</volume>
</status>
```

## `/SyncStatus`

GET `/SyncStatus` — probe `272-state_grouping`, application/xml, 4 redaction edit(s).

```xml
<?xml version="1.0" ?>
<SyncStatus etag="1019" syncStat="1019" version="4.16.22" id="192.0.2.12:11000" db="-44.3" volume="10" name="Kontor" model="N130" modelName="NODE" class="streamer" icon="/images/players/N125_nt.png" brand="Bluesound" schemaVersion="34" initialized="true" group="Kontor + 2" mac="02:00:00:00:00:0C">
  <slave id="192.0.2.13" port="11000" name="Køkken" model="N132" icon="/images/players/N125_nt.png"/>
  <slave id="192.0.2.11" port="11000" name="Stue" model="N132" icon="/images/players/N125_nt.png"/>
  <pairWithSub/>
  <bluetoothOutput/>
</SyncStatus>
```

## `/Volume`

GET `/Volume?mute=1` — probe `008-state_volume`, application/xml, byte-for-byte what the device sent.

```xml
<?xml version="1.0" ?>
<volume db="-100" offsetDb="10" mute="1" muteVolume="10" muteDb="-62.2" etag="ed9f0c6e3af33bf7fc75ed8c68f99ad6" source="">0</volume>
```
