# Element and attribute inventory

Harvested automatically from every XML body captured in this run.
Values are already redacted. Counts are occurrences across all
captures for that endpoint, so an attribute with a low count
relative to its element is optional in practice.

Compare this against the response-shape tables in the
specification: anything here that is not documented there is a
gap, and anything documented that never appears here is either
conditional or historical.

## `/AddSlave`

| element path | n | attributes (n) | sample text |
|---|---|---|---|
| `addSlave` | 6 | - | - |
| `addSlave/slave` | 5 | `id`(5), `port`(5) | - |
| `error` | 1 | - | `failed, invalid channel-mode configuration` |

<details><summary>attribute value samples</summary>

- `addSlave/slave@id` = `192.0.2.12`, `192.0.2.11`, `192.0.2.13`
- `addSlave/slave@port` = `11000`

</details>

## `/Browse`

| element path | n | attributes (n) | sample text |
|---|---|---|---|
| `browse` | 1 | `type`(1) | - |
| `browse/item` | 8 | `browseKey`(6), `image`(8), `inputType`(1), `playURL`(2), `text`(8), `type`(8) | - |

<details><summary>attribute value samples</summary>

- `browse@type` = `menu`
- `browse/item@browseKey` = `BluOS:`, `LocalMusic:`, `Airable:`
- `browse/item@image` = `/images/ci_myplaylists.png`, `/images/capture/ic_tv.png`, `/images/LibraryIcon.png`
- `browse/item@inputType` = `arc`
- `browse/item@playURL` = `/Play?url=Capture%3Ahw%3Aimxspdif%2C0%2F1%2F25%2F2%3Fid%3Din`, `/Play?url=Spotify%3Aplay`
- `browse/item@text` = `Playlists`, `HDMI ARC`, `Library`
- `browse/item@type` = `link`, `audio`

</details>

## `/Name`

| element path | n | attributes (n) | sample text |
|---|---|---|---|
| `name` | 2 | - | `ProbeTest`; `ProbeTest2` |

## `/Pause`

| element path | n | attributes (n) | sample text |
|---|---|---|---|
| `state` | 8 | - | `pause`; `play` |

## `/Play`

| element path | n | attributes (n) | sample text |
|---|---|---|---|
| `state` | 5 | - | `play`; `stream` |

## `/Preset`

| element path | n | attributes (n) | sample text |
|---|---|---|---|
| `loaded` | 1 | `service`(1) | - |
| `loaded/entries` | 1 | - | `20` |
| `state` | 1 | - | `stream` |

<details><summary>attribute value samples</summary>

- `loaded@service` = `Tidal`

</details>

## `/Presets`

| element path | n | attributes (n) | sample text |
|---|---|---|---|
| `presets` | 1 | `prid`(1) | - |
| `presets/preset` | 2 | `id`(2), `image`(2), `name`(2), `url`(2), `volume`(1) | - |

<details><summary>attribute value samples</summary>

- `presets@prid` = `0`
- `presets/preset@id` = `1`, `2`
- `presets/preset@image` = `https://img.radioparadise.com/source/27/channel_logo/chan_0.`, `/Artwork?service=Tidal&playlistimage=6793e3e6-0a62-4921-8158`
- `presets/preset@name` = `RP Main Mix`, `Rolig musik`
- `presets/preset@url` = `RadioParadise:/0:4`, `/Load?service=Tidal&id=9977e64f-8df5-4967-9219-020000000001`
- `presets/preset@volume` = `6`

</details>

## `/RadioBrowse`

| element path | n | attributes (n) | sample text |
|---|---|---|---|
| `radiotime` | 1 | `service`(1) | - |
| `radiotime/item` | 2 | `URL`(2), `id`(2), `image`(2), `inputType`(1), `serviceType`(1), `text`(2), `type`(2), `typeIndex`(1) | - |

<details><summary>attribute value samples</summary>

- `radiotime@service` = `Capture`
- `radiotime/item@URL` = `Capture%3Ahw%3Aimxspdif%2C0%2F1%2F25%2F2%3Fid%3Dinput2`, `Spotify%3Aplay`
- `radiotime/item@id` = `input2`, `Spotify`
- `radiotime/item@image` = `/images/capture/ic_tv.png`, `/Sources/images/SpotifyIcon.png`
- `radiotime/item@inputType` = `arc`
- `radiotime/item@serviceType` = `CloudService`
- `radiotime/item@text` = `HDMI ARC`, `Spotify`
- `radiotime/item@type` = `audio`
- `radiotime/item@typeIndex` = `arc-1`

</details>

## `/RemoveSlave`

| element path | n | attributes (n) | sample text |
|---|---|---|---|
| `SyncStatus` | 2 | `brand`(2), `class`(2), `db`(2), `etag`(2), `group`(2), `hasSubwoofer`(1), `icon`(2), `id`(2), `initialized`(2), `mac`(2), `model`(2), `modelName`(2), `name`(2), `schemaVersion`(2), `syncStat`(2), `version`(2), `volume`(2) | - |
| `SyncStatus/bluetoothOutput` | 2 | - | - |
| `SyncStatus/pairWithSub` | 2 | - | - |
| `SyncStatus/slave` | 3 | `icon`(3), `id`(3), `model`(3), `name`(3), `port`(3) | - |

<details><summary>attribute value samples</summary>

- `SyncStatus@brand` = `Bluesound`
- `SyncStatus@class` = `streamer`
- `SyncStatus@db` = `-62.2`, `-44.3`
- `SyncStatus@etag` = `248`, `1019`
- `SyncStatus@group` = `Stue+Kontor`, `Kontor + 2`
- `SyncStatus@hasSubwoofer` = `true`
- `SyncStatus@icon` = `/images/players/N125_sub.png`, `/images/players/N125_nt.png`
- `SyncStatus@id` = `192.0.2.11:11000`, `192.0.2.12:11000`
- `SyncStatus@initialized` = `true`
- `SyncStatus@mac` = `02:00:00:00:00:0B`, `02:00:00:00:00:0C`
- `SyncStatus@model` = `N132`, `N130`
- `SyncStatus@modelName` = `NODE`
- `SyncStatus@name` = `Stue`, `Kontor`
- `SyncStatus@schemaVersion` = `34`
- `SyncStatus@syncStat` = `248`, `1019`
- `SyncStatus@version` = `4.16.22`
- `SyncStatus@volume` = `10`
- `SyncStatus/slave@icon` = `/images/players/N125_nt.png`
- `SyncStatus/slave@id` = `192.0.2.12`, `192.0.2.13`, `192.0.2.11`
- `SyncStatus/slave@model` = `N130`, `N132`
- `SyncStatus/slave@name` = `Kontor`, `Køkken`, `Stue`
- `SyncStatus/slave@port` = `11000`

</details>

## `/Repeat`

| element path | n | attributes (n) | sample text |
|---|---|---|---|
| `error` | 4 | - | - |
| `error/message` | 4 | - | `invalid state` |

## `/SetMaster`

| element path | n | attributes (n) | sample text |
|---|---|---|---|
| `SyncStatus` | 2 | `brand`(2), `class`(2), `db`(2), `etag`(2), `group`(1), `hasSubwoofer`(1), `icon`(2), `id`(2), `initialized`(2), `mac`(2), `model`(2), `modelName`(2), `name`(2), `schemaVersion`(2), `syncStat`(2), `version`(2), `volume`(2) | - |
| `SyncStatus/bluetoothOutput` | 2 | - | - |
| `SyncStatus/master` | 1 | `port`(1) | `192.0.2.11` |
| `SyncStatus/pairWithSub` | 2 | - | - |
| `SyncStatus/slave` | 1 | `icon`(1), `id`(1), `model`(1), `name`(1), `port`(1) | - |

<details><summary>attribute value samples</summary>

- `SyncStatus@brand` = `Bluesound`
- `SyncStatus@class` = `streamer`
- `SyncStatus@db` = `-62.2`, `-44.3`
- `SyncStatus@etag` = `245`, `1001`
- `SyncStatus@group` = `Stue+Kontor`
- `SyncStatus@hasSubwoofer` = `true`
- `SyncStatus@icon` = `/images/players/N125_sub.png`, `/images/players/N125_nt.png`
- `SyncStatus@id` = `192.0.2.11:11000`, `192.0.2.12:11000`
- `SyncStatus@initialized` = `true`
- `SyncStatus@mac` = `02:00:00:00:00:0B`, `02:00:00:00:00:0C`
- `SyncStatus@model` = `N132`, `N130`
- `SyncStatus@modelName` = `NODE`
- `SyncStatus@name` = `Stue`, `Kontor`
- `SyncStatus@schemaVersion` = `34`
- `SyncStatus@syncStat` = `245`, `1001`
- `SyncStatus@version` = `4.16.22`
- `SyncStatus@volume` = `10`
- `SyncStatus/master@port` = `11000`
- `SyncStatus/slave@icon` = `/images/players/N125_nt.png`
- `SyncStatus/slave@id` = `192.0.2.12`
- `SyncStatus/slave@model` = `N130`
- `SyncStatus/slave@name` = `Kontor`
- `SyncStatus/slave@port` = `11000`

</details>

## `/Shuffle`

| element path | n | attributes (n) | sample text |
|---|---|---|---|
| `playlist` | 4 | `id`(4), `length`(4), `repeat`(4), `shuffle`(4) | - |

<details><summary>attribute value samples</summary>

- `playlist@id` = `1188`, `234`, `273`
- `playlist@length` = `30`, `125`
- `playlist@repeat` = `2`
- `playlist@shuffle` = `0`

</details>

## `/SlaveVolume`

| element path | n | attributes (n) | sample text |
|---|---|---|---|
| `error` | 2 | - | `not valid on non-zone-slave player` |

## `/Status`

| element path | n | attributes (n) | sample text |
|---|---|---|---|
| `status` | 2 | `etag`(2) | - |
| `status/actions` | 1 | - | - |
| `status/actions/action` | 4 | `icon`(2), `name`(4), `state`(4), `text`(2), `type`(2), `url`(3) | - |
| `status/album` | 2 | - | `Eternal Sunshine of the Spotless Mind: Original Soundtrack`; `Another Landing` |
| `status/albumid` | 1 | - | `185331971` |
| `status/artist` | 2 | - | `Beck`; `Cult With No Name` |
| `status/artistid` | 1 | - | `5481574` |
| `status/autofill` | 1 | - | `10` |
| `status/canMovePlayback` | 2 | - | `true` |
| `status/canSeek` | 2 | - | `0`; `1` |
| `status/currentImage` | 1 | - | `https://img.radioparadise.com/covers/l/13074.jpg` |
| `status/cursor` | 2 | - | `29`; `19` |
| `status/db` | 2 | - | `-62.5`; `-68.6` |
| `status/fn` | 1 | - | `Tidal:185331984` |
| `status/image` | 2 | - | `https://img.radioparadise.com/covers/l/13074.jpg`; `/Artwork?service=Tidal&songid=Tidal%3A185331984` |
| `status/indexing` | 2 | - | `0` |
| `status/infourl` | 1 | - | `https://en.wikipedia.org/wiki/` |
| `status/isFavourite` | 1 | - | `1` |
| `status/lyricsid` | 1 | - | `37763` |
| `status/mid` | 2 | - | `19` |
| `status/mode` | 2 | - | `1` |
| `status/mute` | 2 | - | `0` |
| `status/name` | 1 | - | `A Pound of Penny Gaffs` |
| `status/pid` | 2 | - | `3062`; `3063` |
| `status/prid` | 2 | - | `0` |
| `status/quality` | 1 | - | `cd` |
| `status/repeat` | 2 | - | `2` |
| `status/secs` | 2 | - | `0`; `1` |
| `status/service` | 2 | - | `RadioParadise`; `Tidal` |
| `status/serviceIcon` | 2 | - | `/Sources/images/RadioParadiseIcon.png`; `/Sources/images/TidalIcon.png` |
| `status/serviceName` | 2 | - | `Radio Paradise`; `TIDAL` |
| `status/serviceType` | 2 | - | `RadioService`; `CloudService` |
| `status/shuffle` | 2 | - | `0` |
| `status/sid` | 2 | - | `49` |
| `status/similarstationid` | 1 | - | `Tidal:radio:artist/5481574` |
| `status/sleep` | 2 | - | - |
| `status/song` | 2 | - | `0` |
| `status/songid` | 1 | - | `Tidal:185331984` |
| `status/state` | 2 | - | `connecting`; `play` |
| `status/stationImage` | 1 | - | `https://img.radioparadise.com/channels/0/0/cover_512x512/0.j` |
| `status/streamFormat` | 1 | - | `FLAC 16/44.1` |
| `status/streamUrl` | 1 | - | `RadioParadise:/0:4` |
| `status/syncStat` | 2 | - | `1847`; `1849` |
| `status/title1` | 2 | - | `The Main Mix`; `A Pound of Penny Gaffs` |
| `status/title2` | 2 | - | `Everybody's Got To Learn Sometime`; `Cult With No Name` |
| `status/title3` | 2 | - | `Beck • Eternal Sunshine of the Spotless Mind: Original Sound`; `Another Landing` |
| `status/totlen` | 2 | - | `322`; `214` |
| `status/trackstationid` | 1 | - | `Tidal:radio:track/185331984` |
| `status/twoline_title1` | 2 | - | `The Main Mix`; `A Pound of Penny Gaffs` |
| `status/twoline_title2` | 2 | - | `Everybody's Got To Learn Sometime • Beck`; `Cult With No Name • Another Landing` |
| `status/volume` | 2 | - | `10`; `6` |

<details><summary>attribute value samples</summary>

- `status@etag` = `7515148cb4bb27523b5b2a9c1b302c00`, `0fa723cebce041741a502ffedccaa63d`
- `status/actions/action@icon` = `/images/loveban/love.png`, `/images/loveban/ban.png`
- `status/actions/action@name` = `back`, `skip`, `love`
- `status/actions/action@state` = `0`, `-1`
- `status/actions/action@text` = `Love`, `Ban`
- `status/actions/action@type` = `thumbs`
- `status/actions/action@url` = `/Action?service=RadioParadise&next=2921366`, `/Action?service=RadioParadise&love=37763&reset=0`, `/Action?service=RadioParadise&ban=37763&reset=0`

</details>

## `/SyncStatus`

| element path | n | attributes (n) | sample text |
|---|---|---|---|
| `SyncStatus` | 12 | `brand`(12), `class`(12), `db`(12), `etag`(12), `group`(8), `hasSubwoofer`(4), `icon`(12), `id`(12), `initialized`(12), `mac`(12), `model`(12), `modelName`(12), `name`(12), `schemaVersion`(12), `syncStat`(12), `version`(12), `volume`(12) | - |
| `SyncStatus/bluetoothOutput` | 12 | - | - |
| `SyncStatus/master` | 5 | `port`(5), `reconnecting`(1) | `192.0.2.11`; `192.0.2.12` |
| `SyncStatus/pairWithSub` | 12 | - | - |
| `SyncStatus/slave` | 10 | `icon`(10), `id`(10), `model`(10), `name`(10), `port`(10) | - |

<details><summary>attribute value samples</summary>

- `SyncStatus@brand` = `Bluesound`
- `SyncStatus@class` = `streamer`
- `SyncStatus@db` = `-62.2`, `-44.3`, `-62.3`
- `SyncStatus@etag` = `245`, `1001`, `247`
- `SyncStatus@group` = `Stue+Kontor`, `Kontor+Stue`, `Kontor + 2`
- `SyncStatus@hasSubwoofer` = `true`
- `SyncStatus@icon` = `/images/players/N125_sub.png`, `/images/players/N125_nt.png`
- `SyncStatus@id` = `192.0.2.11:11000`, `192.0.2.12:11000`
- `SyncStatus@initialized` = `true`
- `SyncStatus@mac` = `02:00:00:00:00:0B`, `02:00:00:00:00:0C`
- `SyncStatus@model` = `N132`, `N130`
- `SyncStatus@modelName` = `NODE`
- `SyncStatus@name` = `Stue`, `Kontor`
- `SyncStatus@schemaVersion` = `34`
- `SyncStatus@syncStat` = `245`, `1001`, `247`
- `SyncStatus@version` = `4.16.22`
- `SyncStatus@volume` = `10`
- `SyncStatus/master@port` = `11000`
- `SyncStatus/master@reconnecting` = `true`
- `SyncStatus/slave@icon` = `/images/players/N125_nt.png`
- `SyncStatus/slave@id` = `192.0.2.12`, `192.0.2.11`, `192.0.2.13`
- `SyncStatus/slave@model` = `N130`, `N132`
- `SyncStatus/slave@name` = `Kontor`, `Stue`, `Køkken`
- `SyncStatus/slave@port` = `11000`

</details>

## `/Volume`

| element path | n | attributes (n) | sample text |
|---|---|---|---|
| `volume` | 28 | `db`(28), `etag`(28), `mute`(28), `muteDb`(4), `muteVolume`(4), `offsetDb`(28), `source`(28) | `1`; `5`; `10` |

<details><summary>attribute value samples</summary>

- `volume@db` = `-74.1`, `-68.8`, `-62.2`
- `volume@etag` = `881af18291895622161db201685a2723`, `ad871070f92581019a0caf57f60a1f21`, `9e12351ae5fcdac65a5d201f53787375`
- `volume@mute` = `0`, `1`
- `volume@muteDb` = `-62.2`, `-44.2`, `-55.8`
- `volume@muteVolume` = `10`
- `volume@offsetDb` = `10`, `0`

</details>
