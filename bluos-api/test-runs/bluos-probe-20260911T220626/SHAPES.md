# Element and attribute inventory

Harvested automatically from every XML body captured in this run.
Values are already redacted. Counts are occurrences across all
captures for that endpoint, so an attribute with a low count
relative to its element is optional in practice.

Compare this against the response-shape tables in the
specification: anything here that is not documented there is a
gap, and anything documented that never appears here is either
conditional or historical.

## `/Playlist`

| element path | n | attributes (n) | sample text |
|---|---|---|---|
| `playlist` | 4 | `id`(4), `length`(4), `playlistid`(2), `repeat`(4), `shuffle`(4) | - |
| `playlist/song` | 212 | `albumid`(212), `artistid`(212), `id`(212), `isFavourite`(178), `service`(212), `similarstationid`(212), `songid`(212), `trackstationid`(212) | - |
| `playlist/song/alb` | 212 | - | `Simmer Down`; `I Remember`; `Blind (feat. Emmi) [Radio Edit]` |
| `playlist/song/art` | 212 | - | `Andhim`; `AlunaGeorge`; `Feder` |
| `playlist/song/date` | 10 | - | `2017-06-04`; `2019-06-26`; `2020-06-24` |
| `playlist/song/discno` | 212 | - | `1`; `2` |
| `playlist/song/fn` | 212 | - | `Tidal:122288231`; `Tidal:64753254`; `Tidal:53780764` |
| `playlist/song/image` | 212 | - | `/Artwork?service=Tidal&songid=Tidal%3A122288231`; `/Artwork?service=Tidal&songid=Tidal%3A64753254`; `/Artwork?service=Tidal&songid=Tidal%3A53780764` |
| `playlist/song/quality` | 209 | - | `cd`; `hd` |
| `playlist/song/time` | 212 | - | `267`; `209`; `194` |
| `playlist/song/title` | 212 | - | `How Many Times`; `I'm In Control`; `Blind (feat. Emmi) [Radio Edit]` |
| `playlist/song/track` | 212 | - | `4`; `7`; `1` |

<details><summary>attribute value samples</summary>

- `playlist@id` = `1193`, `235`, `273`
- `playlist@length` = `37`, `125`, `30`
- `playlist@playlistid` = `Tidal:f6bddb25-a5dc-4658-993d-020000000001`, `Tidal:9977e64f-8df5-4967-9219-020000000003`
- `playlist@repeat` = `2`
- `playlist@shuffle` = `1`, `0`
- `playlist/song@albumid` = `122288227`, `64753247`, `53780763`
- `playlist/song@artistid` = `3685073`, `3933761`, `4801103`
- `playlist/song@id` = `0`, `1`, `2`
- `playlist/song@isFavourite` = `1`
- `playlist/song@service` = `Tidal`
- `playlist/song@similarstationid` = `Tidal:radio:artist/3685073`, `Tidal:radio:artist/3933761`, `Tidal:radio:artist/4801103`
- `playlist/song@songid` = `Tidal:122288231`, `Tidal:64753254`, `Tidal:53780764`
- `playlist/song@trackstationid` = `Tidal:radio:track/122288231`, `Tidal:radio:track/64753254`, `Tidal:radio:track/53780764`

</details>

## `/Presets`

| element path | n | attributes (n) | sample text |
|---|---|---|---|
| `presets` | 4 | `prid`(4) | - |
| `presets/preset` | 3 | `id`(3), `image`(3), `name`(3), `url`(3), `volume`(1) | - |

<details><summary>attribute value samples</summary>

- `presets@prid` = `1`, `0`
- `presets/preset@id` = `1`, `2`
- `presets/preset@image` = `/Artwork?service=Tidal&playlistimage=f8601f52-6d31-43bd-97a7`, `https://img.radioparadise.com/source/27/channel_logo/chan_0.`, `/Artwork?service=Tidal&playlistimage=6793e3e6-0a62-4921-8158`
- `presets/preset@name` = `Sunday Chill Mix: Ministry of Sound`, `RP Main Mix`, `Rolig musik`
- `presets/preset@url` = `/Load?service=Tidal&id=f6bddb25-a5dc-4658-993d-020000000001`, `RadioParadise:/0:4`, `/Load?service=Tidal&id=9977e64f-8df5-4967-9219-020000000003`
- `presets/preset@volume` = `6`

</details>

## `/Status`

| element path | n | attributes (n) | sample text |
|---|---|---|---|
| `status` | 13 | `etag`(13) | - |
| `status/actions` | 1 | - | - |
| `status/actions/action` | 4 | `icon`(2), `name`(4), `state`(4), `text`(2), `type`(2), `url`(3) | - |
| `status/album` | 12 | - | `You Know You Like It`; `Romanticize The Dive`; `Chasing Time` |
| `status/albumid` | 12 | - | `38014822`; `482411342`; `169319097` |
| `status/artist` | 12 | - | `DJ Snake`; `Metric`; `Oscuro` |
| `status/artistid` | 12 | - | `4826235`; `65040`; `32670299` |
| `status/autofill` | 1 | - | `6` |
| `status/canMovePlayback` | 13 | - | `true` |
| `status/canSeek` | 13 | - | `1`; `0` |
| `status/cursor` | 13 | - | `36`; `124`; `29` |
| `status/db` | 13 | - | `-49.1`; `-27.5`; `-38` |
| `status/dirac` | 12 | - | `1` |
| `status/fn` | 12 | - | `Tidal:38014823`; `Tidal:482411348`; `Tidal:169319098` |
| `status/groupName` | 5 | - | `Stue+Kontor` |
| `status/groupVolume` | 5 | - | `10` |
| `status/image` | 13 | - | `/Artwork?service=Tidal&songid=Tidal%3A38014823`; `/Artwork?service=Tidal&songid=Tidal%3A482411348`; `/Artwork?service=Tidal&songid=Tidal%3A169319098` |
| `status/indexing` | 13 | - | `0` |
| `status/isFavourite` | 12 | - | `0`; `1` |
| `status/mid` | 13 | - | `19` |
| `status/mode` | 13 | - | `1` |
| `status/mqaOFS` | 2 | - | `44100` |
| `status/mute` | 13 | - | `0` |
| `status/name` | 12 | - | `You Know You Like It`; `Moral Compass`; `Chasing Time` |
| `status/pid` | 13 | - | `1193`; `235`; `273` |
| `status/prid` | 13 | - | `1`; `0` |
| `status/quality` | 13 | - | `mqa`; `hd`; `cd` |
| `status/repeat` | 13 | - | `2` |
| `status/secs` | 13 | - | `21`; `27`; `0` |
| `status/service` | 13 | - | `Tidal`; `RadioParadise` |
| `status/serviceIcon` | 13 | - | `/Sources/images/TidalIcon.png`; `/Sources/images/RadioParadiseIcon.png` |
| `status/serviceName` | 13 | - | `TIDAL`; `Radio Paradise` |
| `status/serviceType` | 13 | - | `CloudService`; `RadioService` |
| `status/shuffle` | 13 | - | `1`; `0` |
| `status/sid` | 13 | - | `54`; `86`; `74` |
| `status/similarstationid` | 12 | - | `Tidal:radio:artist/4826235`; `Tidal:radio:artist/65040`; `Tidal:radio:artist/32670299` |
| `status/sleep` | 13 | - | - |
| `status/song` | 13 | - | `18`; `0`; `5` |
| `status/songid` | 12 | - | `Tidal:38014823`; `Tidal:482411348`; `Tidal:169319098` |
| `status/state` | 13 | - | `play`; `stop`; `pause` |
| `status/stationImage` | 1 | - | `https://img.radioparadise.com/channels/0/0/cover_512x512/0.j` |
| `status/streamFormat` | 11 | - | `16/44.1`; `FLAC 16/44.1` |
| `status/streamUrl` | 1 | - | `RadioParadise:/0:4` |
| `status/syncStat` | 13 | - | `523`; `1025`; `963` |
| `status/title1` | 13 | - | `You Know You Like It`; `Moral Compass`; `Chasing Time` |
| `status/title2` | 12 | - | `DJ Snake`; `Metric`; `Oscuro` |
| `status/title3` | 12 | - | `You Know You Like It`; `Romanticize The Dive`; `Chasing Time` |
| `status/totlen` | 13 | - | `247`; `268`; `228` |
| `status/trackstationid` | 12 | - | `Tidal:radio:track/38014823`; `Tidal:radio:track/482411348`; `Tidal:radio:track/169319098` |
| `status/twoline_title1` | 13 | - | `You Know You Like It`; `Moral Compass`; `Chasing Time` |
| `status/twoline_title2` | 12 | - | `DJ Snake • You Know You Like It`; `Metric • Romanticize The Dive`; `Oscuro • Chasing Time` |
| `status/volume` | 13 | - | `20`; `27`; `38` |

<details><summary>attribute value samples</summary>

- `status@etag` = `ab81771c58c58dcaef900289f9923401`, `d7bac2eccebbf802a96a476ef1ed9ab5`, `f99493bdf725d0c7946e606fdf2827b1`
- `status/actions/action@icon` = `/images/loveban/love.png`, `/images/loveban/ban.png`
- `status/actions/action@name` = `back`, `skip`, `love`
- `status/actions/action@state` = `0`, `-1`
- `status/actions/action@text` = `Love`, `Ban`
- `status/actions/action@type` = `thumbs`
- `status/actions/action@url` = `/Action?service=RadioParadise&next=2921536`, `/Action?service=RadioParadise&love=53146&reset=0`, `/Action?service=RadioParadise&ban=53146&reset=0`

</details>

## `/SyncStatus`

| element path | n | attributes (n) | sample text |
|---|---|---|---|
| `SyncStatus` | 13 | `brand`(13), `class`(13), `db`(13), `etag`(13), `group`(3), `hasSubwoofer`(8), `icon`(13), `id`(13), `initialized`(13), `mac`(13), `model`(13), `modelName`(13), `name`(13), `schemaVersion`(13), `syncStat`(13), `version`(13), `volume`(13) | - |
| `SyncStatus/bluetoothOutput` | 11 | - | - |
| `SyncStatus/master` | 4 | `port`(4), `reconnecting`(1) | `192.0.2.11`; `192.0.2.12` |
| `SyncStatus/pairWithSub` | 13 | - | - |
| `SyncStatus/slave` | 3 | `icon`(3), `id`(3), `model`(3), `name`(3), `port`(3) | - |

<details><summary>attribute value samples</summary>

- `SyncStatus@brand` = `Bluesound`
- `SyncStatus@class` = `streamer`
- `SyncStatus@db` = `-49.1`, `-27.5`, `-38`
- `SyncStatus@etag` = `523`, `1025`, `963`
- `SyncStatus@group` = `Stue+Kontor`, `Kontor+Køkken`
- `SyncStatus@hasSubwoofer` = `true`
- `SyncStatus@icon` = `/images/players/N125_sub.png`, `/images/players/N125_nt.png`, `/images/players/N110_sub.png`
- `SyncStatus@id` = `192.0.2.11:11000`, `192.0.2.12:11000`, `192.0.2.13:11000`
- `SyncStatus@initialized` = `true`
- `SyncStatus@mac` = `02:00:00:00:00:0B`, `02:00:00:00:00:0C`, `02:00:00:00:00:0D`
- `SyncStatus@model` = `N132`, `N130`, `N110`
- `SyncStatus@modelName` = `NODE`, `NODE 2`
- `SyncStatus@name` = `Stue`, `Kontor`, `Køkken`
- `SyncStatus@schemaVersion` = `34`
- `SyncStatus@syncStat` = `523`, `1025`, `963`
- `SyncStatus@version` = `4.16.22`
- `SyncStatus@volume` = `20`, `27`, `38`
- `SyncStatus/master@port` = `11000`
- `SyncStatus/master@reconnecting` = `true`
- `SyncStatus/slave@icon` = `/images/players/N125_nt.png`
- `SyncStatus/slave@id` = `192.0.2.12`, `192.0.2.13`
- `SyncStatus/slave@model` = `N130`, `N132`
- `SyncStatus/slave@name` = `Kontor`, `Køkken`
- `SyncStatus/slave@port` = `11000`

</details>

## `/Volume`

| element path | n | attributes (n) | sample text |
|---|---|---|---|
| `volume` | 4 | `db`(4), `etag`(4), `mute`(4), `offsetDb`(4), `source`(4) | `20`; `27`; `38` |

<details><summary>attribute value samples</summary>

- `volume@db` = `-49.1`, `-27.5`, `-38`
- `volume@etag` = `a79f2e9d2881ae370f00800f9d0a2c26`, `24f7d32b71ec7dfc7c7bef68b0701353`, `68039410a8958fea9444269d4d2c8bc6`
- `volume@mute` = `0`
- `volume@offsetDb` = `10`, `0`

</details>
