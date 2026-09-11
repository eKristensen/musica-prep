# Element and attribute inventory

Harvested automatically from every XML body captured in this run.
Values are already redacted. Counts are occurrences across all
captures for that endpoint, so an attribute with a low count
relative to its element is optional in practice.

Compare this against the response-shape tables in the
specification: anything here that is not documented there is a
gap, and anything documented that never appears here is either
conditional or historical.

## `/Alarms`

| element path | n | attributes (n) | sample text |
|---|---|---|---|
| `alarms` | 4 | `supportsEndTime`(4) | - |
| `alarms/alarm` | 1 | `days`(1), `duration`(1), `enable`(1), `fadein`(1), `hour`(1), `id`(1), `image`(1), `minute`(1), `service`(1), `source`(1), `url`(1), `useBackup`(1), `voldb`(1), `volume`(1) | - |

<details><summary>attribute value samples</summary>

- `alarms@supportsEndTime` = `true`
- `alarms/alarm@days` = `0000000`
- `alarms/alarm@duration` = `60`
- `alarms/alarm@enable` = `0`
- `alarms/alarm@fadein` = `1`
- `alarms/alarm@hour` = `7`
- `alarms/alarm@id` = `1`
- `alarms/alarm@image` = `https://img.radioparadise.com/channels/0/0/cover_512x512/0.j`
- `alarms/alarm@minute` = `15`
- `alarms/alarm@service` = `RadioParadise`
- `alarms/alarm@source` = `The Main Mix`
- `alarms/alarm@url` = `RadioParadise:/0:20`
- `alarms/alarm@useBackup` = `true`
- `alarms/alarm@voldb` = `-53.1`
- `alarms/alarm@volume` = `22`

</details>

## `/Artwork`

| element path | n | attributes (n) | sample text |
|---|---|---|---|
| `artwork` | 3 | - | `none found` |

## `/BTDevices`

| element path | n | attributes (n) | sample text |
|---|---|---|---|
| `btdevices` | 3 | `connecting`(3), `etag`(3) | - |

<details><summary>attribute value samples</summary>

- `btdevices@connecting` = `false`
- `btdevices@etag` = `14`, `7`

</details>

## `/Browse`

| element path | n | attributes (n) | sample text |
|---|---|---|---|
| `browse` | 69 | `nextKey`(9), `searchKey`(59), `serviceIcon`(61), `serviceName`(61), `type`(69) | - |
| `browse/category` | 23 | `nextKey`(1), `text`(23) | - |
| `browse/category/item` | 332 | `browseKey`(112), `contextMenuKey`(311), `image`(331), `playURL`(220), `text`(332), `text2`(274), `type`(332) | - |
| `browse/item` | 655 | `autoplayURL`(27), `browseKey`(346), `contextMenuKey`(327), `duration`(27), `image`(413), `inputType`(7), `isFavourite`(27), `playURL`(329), `text`(655), `text2`(396), `tracks`(20), `type`(655) | - |

<details><summary>attribute value samples</summary>

- `browse@nextKey` = `Airable:BrowseMenu/%2FRadioBrowse%3Fservice=Airable&url=http`, `Airable:BrowseMenu/%2FRadioBrowse%3Fservice=Airable&url=http`, `Airable:BrowseMenu/%2FRadioBrowse%3Fservice=Airable&url=http`
- `browse@searchKey` = `LocalMusic:Search`, `Airable:Search`, `Tidal:Search`
- `browse@serviceIcon` = `/images/BluOSIcon.png`, `/images/LibraryIcon.png`, `/Sources/images/BluOSRadioIcon.png`
- `browse@serviceName` = `BluOS`, `Library`, `Radio`
- `browse@type` = `menu`, `playlists`, `items`
- `browse/category@nextKey` = `TuneIn:BrowseMenu/%2FRadioBrowse%3Fservice=TuneIn&url=https%`
- `browse/category@text` = `MQA`, `CD Quality`, `Popular Stations in Your Area`
- `browse/category/item@browseKey` = `TuneIn:BrowseMenu/%2FRadioBrowse%3Fservice=TuneIn&url=https%`, `TuneIn:BrowseMenu/%2FRadioBrowse%3Fservice=TuneIn&url=https%`, `TuneIn:BrowseMenu/%2FRadioBrowse%3Fservice=TuneIn&url=https%`
- `browse/category/item@contextMenuKey` = `RadioParadise:CM/RadioParadise-Item?URL=RadioParadise%3A%2F0`, `RadioParadise:CM/RadioParadise-Item?URL=RadioParadise%3A%2F1`, `RadioParadise:CM/RadioParadise-Item?URL=RadioParadise%3A%2F2`
- `browse/category/item@image` = `https://img.radioparadise.com/channels/0/0/cover_512x512/0.j`, `https://img.radioparadise.com/channels/0/1/cover_512x512/0.j`, `https://img.radioparadise.com/channels/0/2/cover_512x512/0.j`
- `browse/category/item@playURL` = `/Play?url=RadioParadise%3A%2F0%3A20&title=The+Main+Mix&image`, `/Play?url=RadioParadise%3A%2F1%3A20%2FMellow%2520Mix&title=M`, `/Play?url=RadioParadise%3A%2F2%3A20%2FRockIt%2521&title=Rock`
- `browse/category/item@text` = `The Main Mix`, `Mellow Mix`, `RockIt!`
- `browse/category/item@text2` = `Copenhagen`, `Tankevækkende radio`, `Denmark`
- `browse/category/item@type` = `audio`, `link`
- `browse/item@autoplayURL` = `/Add?service=Tidal&listindex=0&nextlist=1&where=last&cursor=`, `/Add?service=Tidal&listindex=1&nextlist=1&where=last&cursor=`, `/Add?service=Tidal&listindex=2&nextlist=1&where=last&cursor=`
- `browse/item@browseKey` = `BluOS:`, `LocalMusic:`, `Airable:`
- `browse/item@contextMenuKey` = `Airable:CM/Airable-Item?URL=Airable%3Aradio%3Ahttps%3A%2F%02`, `Airable:CM/Airable-Item?URL=Airable%3Aradio%3Ahttps%3A%2F%02`, `Airable:CM/Airable-Item?URL=Airable%3Aradio%3Ahttps%3A%2F%02`
- `browse/item@duration` = `259`, `261`, `265`
- `browse/item@image` = `/images/ci_myplaylists.png`, `/images/capture/ic_tv.png`, `/images/LibraryIcon.png`
- `browse/item@inputType` = `arc`
- `browse/item@isFavourite` = `true`
- `browse/item@playURL` = `/Play?url=Capture%3Ahw%3Aimxspdif%2C0%2F1%2F25%2F2%3Fid%3Din`, `/Play?url=Spotify%3Aplay`, `/Play?url=Capture%3Ahw%3Aimxspdif%2C0%2F1%2F25%2F2%3Fid%3Din`
- `browse/item@text` = `Playlists`, `HDMI ARC`, `Library`
- `browse/item@text2` = `3`, `1`, `2`
- `browse/item@tracks` = `10`, `14`, `21`
- `browse/item@type` = `link`, `audio`, `section`

</details>

## `/GitVersion`

| element path | n | attributes (n) | sample text |
|---|---|---|---|
| `version` | 4 | - | `4.16.22` |

## `/Name`

| element path | n | attributes (n) | sample text |
|---|---|---|---|
| `name` | 4 | - | `Stue`; `Kontor`; `Køkken` |

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

## `/Playlists`

| element path | n | attributes (n) | sample text |
|---|---|---|---|
| `playlists` | 1 | `service`(1) | - |

<details><summary>attribute value samples</summary>

- `playlists@service` = `BluOS`

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

## `/RadioBrowse`

| element path | n | attributes (n) | sample text |
|---|---|---|---|
| `radiotime` | 8 | `service`(8) | - |
| `radiotime/category` | 2 | `key`(2), `text`(2) | - |
| `radiotime/category/item` | 14 | `URL`(14), `image`(14), `text`(14), `type`(14) | - |
| `radiotime/item` | 23 | `URL`(23), `id`(7), `image`(17), `inputType`(4), `key`(6), `serviceType`(3), `text`(23), `type`(23), `typeIndex`(4) | - |

<details><summary>attribute value samples</summary>

- `radiotime@service` = `Airable`, `Capture`, `RadioParadise`
- `radiotime/category@key` = `20`, `4`
- `radiotime/category@text` = `MQA`, `CD Quality`
- `radiotime/category/item@URL` = `RadioParadise%3A%2F0%3A20`, `RadioParadise%3A%2F1%3A20%2FMellow%2520Mix`, `RadioParadise%3A%2F2%3A20%2FRockIt%2521`
- `radiotime/category/item@image` = `https://img.radioparadise.com/channels/0/0/cover_512x512/0.j`, `https://img.radioparadise.com/channels/0/1/cover_512x512/0.j`, `https://img.radioparadise.com/channels/0/2/cover_512x512/0.j`
- `radiotime/category/item@text` = `The Main Mix`, `Mellow Mix`, `RockIt!`
- `radiotime/category/item@type` = `audio`
- `radiotime/item@URL` = `https%3A%2F%02000000003C.airable.io%2Fradio%2Fstations%2Fcha`, `https%3A%2F%02000000003C.airable.io%2Fradio%2Fplace%2F414702`, `https%3A%2F%02000000003C.airable.io%2Fradio%2Flocal`
- `radiotime/item@id` = `input2`, `Spotify`
- `radiotime/item@image` = `/images/capture/ic_tv.png`, `/Sources/images/SpotifyIcon.png`, `https://cdn-profiles.tunein.com/RootMenu/Logo_754o.png?t=169`
- `radiotime/item@inputType` = `arc`
- `radiotime/item@key` = `directory`
- `radiotime/item@serviceType` = `CloudService`
- `radiotime/item@text` = `Most popular stations`, `Denmark`, `Local stations`
- `radiotime/item@type` = `link`, `audio`
- `radiotime/item@typeIndex` = `arc-1`

</details>

## `/RadioPresets`

| element path | n | attributes (n) | sample text |
|---|---|---|---|
| `error` | 1 | `service`(1) | - |
| `error/message` | 1 | - | `unknown channel "presets"` |
| `radiotime` | 2 | `service`(2) | - |
| `radiotime/category` | 2 | `key`(2), `text`(2) | - |
| `radiotime/category/item` | 14 | `URL`(14), `image`(14), `text`(14), `type`(14) | - |
| `radiotime/item` | 6 | `URL`(6), `key`(6), `text`(6), `type`(6) | - |

<details><summary>attribute value samples</summary>

- `error@service` = `TuneIn`
- `radiotime@service` = `Airable`, `RadioParadise`
- `radiotime/category@key` = `20`, `4`
- `radiotime/category@text` = `MQA`, `CD Quality`
- `radiotime/category/item@URL` = `RadioParadise%3A%2F0%3A20`, `RadioParadise%3A%2F1%3A20%2FMellow%2520Mix`, `RadioParadise%3A%2F2%3A20%2FRockIt%2521`
- `radiotime/category/item@image` = `https://img.radioparadise.com/channels/0/0/cover_512x512/0.j`, `https://img.radioparadise.com/channels/0/1/cover_512x512/0.j`, `https://img.radioparadise.com/channels/0/2/cover_512x512/0.j`
- `radiotime/category/item@text` = `The Main Mix`, `Mellow Mix`, `RockIt!`
- `radiotime/category/item@type` = `audio`
- `radiotime/item@URL` = `https%3A%2F%02000000003C.airable.io%2Fradio%2Fstations%2Fcha`, `https%3A%2F%02000000003C.airable.io%2Fradio%2Fplace%2F414702`, `https%3A%2F%02000000003C.airable.io%2Fradio%2Flocal`
- `radiotime/item@key` = `directory`
- `radiotime/item@text` = `Most popular stations`, `Denmark`, `Local stations`
- `radiotime/item@type` = `link`

</details>

## `/Services`

| element path | n | attributes (n) | sample text |
|---|---|---|---|
| `services` | 5 | `schemaVersion`(5), `sid`(5), `url`(5) | - |
| `services/service` | 40 | `backgroundImage`(5), `displayname`(40), `hasStableBrowse`(30), `icon`(30), `label`(5), `name`(40), `type`(40) | - |
| `services/service/artworkRequest` | 10 | `url`(10) | - |
| `services/service/artworkRequest/requestItemParameter` | 30 | `name`(30), `optional`(25) | - |
| `services/service/menu` | 40 | - | - |
| `services/service/menu/filter` | 5 | `class`(5), `displayName`(5), `name`(5) | - |
| `services/service/menu/filter/value` | 15 | `displayName`(15), `name`(15), `type`(15) | - |
| `services/service/menu/genreGroup` | 15 | `displayName`(15), `minimumSchemaVersion`(15) | - |
| `services/service/menu/genreGroup/browseRequest` | 15 | `resultType`(15), `url`(15) | - |
| `services/service/menu/genreGroup/browseRequest/requestParameter` | 5 | - | `category=moods` |
| `services/service/menu/genreGroup/menuEntry` | 40 | `displayName`(40), `inlineRows`(35) | - |
| `services/service/menu/genreGroup/menuEntry/browseRequest` | 40 | `grouped`(20), `resultType`(40), `url`(40) | - |
| `services/service/menu/genreGroup/menuEntry/browseRequest/genreItemParameter` | 40 | `name`(40), `source`(20) | - |
| `services/service/menu/genreGroup/menuEntry/browseRequest/requestParameter` | 15 | - | `category=new` |
| `services/service/menu/genreGroup/menuEntry/nofilter` | 10 | - | - |
| `services/service/menu/genreGroup/menuEntry/sort` | 5 | `default`(5), `minimumSchemaVersion`(5), `name`(5) | - |
| `services/service/menu/genreGroup/menuEntry/sort/value` | 30 | `displayName`(30), `name`(30) | - |
| `services/service/menu/inlineEntry` | 10 | `displayName`(10), `inlineRows`(5), `minimumSchemaVersion`(10) | - |
| `services/service/menu/inlineEntry/browseRequest` | 10 | `resultType`(10), `url`(10) | - |
| `services/service/menu/inlineEntry/browseRequest/requestParameter` | 20 | - | `recent=1`; `category=FAVOURITES`; `inline=1` |
| `services/service/menu/menuEntry` | 50 | `defaultView`(10), `displayName`(50), `inlineRows`(5), `minimumSchemaVersion`(10) | - |
| `services/service/menu/menuEntry/browseRequest` | 50 | `grouped`(20), `myPlaylistsFilter`(10), `resultType`(50), `type`(5), `url`(50) | - |
| `services/service/menu/menuEntry/browseRequest/requestItemParameter` | 5 | `name`(5), `optional`(5) | - |
| `services/service/menu/menuEntry/browseRequest/requestParameter` | 15 | - | `all=1`; `imported=1`; `url=presets` |
| `services/service/menu/menuEntry/nofilter` | 15 | - | - |
| `services/service/menu/menuEntry/sort` | 10 | `default`(10), `minimumSchemaVersion`(10), `name`(10) | - |
| `services/service/menu/menuEntry/sort/value` | 40 | `displayName`(40), `name`(40) | - |
| `services/service/menu/menuGroup` | 160 | `context`(115), `displayName`(30), `id`(55), `mainMenu`(20), `minimumSchemaVersion`(35) | - |
| `services/service/menu/menuGroup/menuEntry` | 635 | `displayName`(635), `inlineRows`(135), `minimumSchemaVersion`(75) | - |
| `services/service/menu/menuGroup/menuEntry/browseRequest` | 255 | `myPlaylistsFilter`(5), `resultType`(255), `type`(65), `url`(255), `xmlRequestParameter`(10) | - |
| `services/service/menu/menuGroup/menuEntry/browseRequest/requestItemParameter` | 170 | `name`(170), `optional`(30), `source`(20) | - |
| `services/service/menu/menuGroup/menuEntry/browseRequest/requestParameter` | 155 | - | `service=LocalMusic`; `category=technical`; `category=FAVOURITES` |
| `services/service/menu/menuGroup/menuEntry/confirmAction` | 10 | `text`(10) | - |
| `services/service/menu/menuGroup/menuEntry/confirmAction/textItemSubstitution` | 10 | `attribute`(10), `source`(10) | - |
| `services/service/menu/menuGroup/menuEntry/contextRequest` | 30 | `resultType`(30), `type`(30), `url`(30) | - |
| `services/service/menu/menuGroup/menuEntry/contextRequest/requestItemParameter` | 35 | `name`(35) | - |
| `services/service/menu/menuGroup/menuEntry/disableOnAttribute` | 75 | `name`(75) | - |
| `services/service/menu/menuGroup/menuEntry/enableOnAttribute` | 80 | `name`(80) | - |
| `services/service/menu/menuGroup/menuEntry/enableOnAttribute/value` | 10 | - | `station` |
| `services/service/menu/menuGroup/menuEntry/filter` | 5 | `class`(5), `default`(5), `displayName`(5), `minimumSchemaVersion`(5), `name`(5), `required`(5) | - |
| `services/service/menu/menuGroup/menuEntry/filter/value` | 10 | `displayName`(10), `name`(10), `type`(10) | - |
| `services/service/menu/menuGroup/menuEntry/nofilter` | 10 | - | - |
| `services/service/menu/menuGroup/menuEntry/request` | 340 | `preset_image`(20), `preset_name`(20), `preset_url`(20), `subtype`(290), `type`(340), `url`(340) | - |
| `services/service/menu/menuGroup/menuEntry/request/requestItemParameter` | 435 | `name`(435), `optional`(30), `source`(140) | - |
| `services/service/menu/menuGroup/menuEntry/request/requestParameter` | 460 | - | `playnow=1`; `clear=0`; `shuffle=0` |
| `services/service/menu/menuGroup/menuEntry/searchRequest` | 10 | `resultType`(10), `service`(10), `subtitleParameter`(10), `type`(10), `url`(10), `view`(10) | - |
| `services/service/menu/menuGroup/menuEntry/searchRequest/requestItemParameter` | 10 | `name`(10), `source`(10) | - |
| `services/service/menu/menuGroup/menuEntry/sort` | 30 | `default`(30), `minimumSchemaVersion`(30), `name`(30) | - |
| `services/service/menu/menuGroup/menuEntry/sort/value` | 85 | `displayName`(85), `name`(85) | - |
| `services/service/menu/menuGroup/menuEntry/textItemSubstitution` | 5 | `attribute`(5), `source`(5) | - |
| `services/service/menu/menuGroup/menuGroup` | 40 | `context`(40) | - |
| `services/service/menu/menuGroup/menuGroup/menuEntry` | 215 | `displayName`(215), `minimumSchemaVersion`(60) | - |
| `services/service/menu/menuGroup/menuGroup/menuEntry/browseRequest` | 75 | `resultType`(75), `type`(75), `url`(75) | - |
| `services/service/menu/menuGroup/menuGroup/menuEntry/browseRequest/requestItemParameter` | 165 | `name`(165), `optional`(30), `source`(25) | - |
| `services/service/menu/menuGroup/menuGroup/menuEntry/browseRequest/requestParameter` | 25 | - | `category=technical`; `c=selectStream`; `service=Tidal` |
| `services/service/menu/menuGroup/menuGroup/menuEntry/contextRequest` | 20 | `resultType`(20), `type`(20), `url`(20) | - |
| `services/service/menu/menuGroup/menuGroup/menuEntry/contextRequest/requestItemParameter` | 25 | `name`(25) | - |
| `services/service/menu/menuGroup/menuGroup/menuEntry/disableOnAttribute` | 30 | `name`(30) | - |
| `services/service/menu/menuGroup/menuGroup/menuEntry/enableOnAttribute` | 30 | `name`(30) | - |
| `services/service/menu/menuGroup/menuGroup/menuEntry/request` | 90 | `preset_image`(20), `preset_name`(20), `preset_url`(20), `subtype`(60), `type`(90), `url`(90) | - |
| `services/service/menu/menuGroup/menuGroup/menuEntry/request/requestItemParameter` | 130 | `name`(130), `optional`(20), `source`(110) | - |
| `services/service/menu/menuGroup/menuGroup/menuEntry/request/requestParameter` | 20 | - | `action=addFavourite`; `action=deleteFavourite` |
| `services/service/menu/menuGroup/menuGroup/menuEntry/searchRequest` | 30 | `resultType`(30), `service`(30), `subtitleParameter`(30), `type`(30), `url`(30), `view`(30) | - |
| `services/service/menu/menuGroup/menuGroup/menuEntry/searchRequest/requestItemParameter` | 30 | `name`(30), `source`(30) | - |
| `services/service/menu/menuGroup/menuGroup/menuEntry/textItemSubstitution` | 30 | `attribute`(30), `source`(30) | - |
| `services/service/menu/menuGroup/nofilter` | 15 | - | - |
| `services/service/menu/menuGroup/search` | 10 | `parameterName`(10), `prompt`(10) | - |
| `services/service/menu/menuGroup/search/browseRequest` | 5 | `resultType`(5), `url`(5) | - |
| `services/service/menu/menuGroup/search/menuGroup` | 5 | `minimumSchemaVersion`(5) | - |
| `services/service/menu/menuGroup/search/menuGroup/menuEntry` | 10 | `displayName`(10) | - |
| `services/service/menu/menuGroup/search/menuGroup/menuEntry/browseRequest` | 10 | `resultType`(10), `url`(10) | - |
| `services/service/menu/menuGroup/search/menuGroup/menuEntry/browseRequest/requestParameter` | 10 | - | `c=station`; `c=podcast` |
| `services/service/menu/search` | 10 | `hasSuggestions`(5), `parameterName`(10), `prompt`(10) | - |
| `services/service/menu/search/browseRequest` | 10 | `resultType`(10), `url`(10) | - |
| `services/service/menu/search/menuGroup` | 10 | `context`(10), `minimumSchemaVersion`(10) | - |
| `services/service/menu/search/menuGroup/menuEntry` | 40 | `displayName`(40), `inlineRows`(20), `minimumSchemaVersion`(5) | - |
| `services/service/menu/search/menuGroup/menuEntry/browseRequest` | 40 | `resultType`(40), `url`(40) | - |
| `services/service/menu/search/menuGroup/menuEntry/nofilter` | 10 | - | - |

<details><summary>attribute value samples</summary>

- `services@schemaVersion` = `34`
- `services@sid` = `50`, `83`, `72`
- `services@url` = `/redirectToCp?href=%2Fservices%3Fnoheader%3D1%26schemaVersio`, `/redirectToCp?href=%2Fservices%3Fnoheader%3D1%26schemaVersio`, `/redirectToCp?href=%2Fservices%3Fnoheader%3D1%26schemaVersio`
- `services/service@backgroundImage` = `/Sources/images/RPBackground.png`
- `services/service@displayname` = `BluOS`, `Library`, `TuneIn`
- `services/service@hasStableBrowse` = `true`
- `services/service@icon` = `/images/BluOSIcon.png`, `/images/LibraryIcon.png`, `/Sources/images/TuneInIcon.png`
- `services/service@label` = `No Label`
- `services/service@name` = `BluOS`, `Capture`, `Alarms`
- `services/service@type` = `BluOSPlaylists`, `AudioInputs`, `Alarms`
- `services/service/artworkRequest@url` = `/library/v1/Artwork`, `/Artwork`
- `services/service/artworkRequest/requestItemParameter@name` = `album`, `artist`, `albumid`
- `services/service/artworkRequest/requestItemParameter@optional` = `true`
- `services/service/menu/filter@class` = `multiple`
- `services/service/menu/filter@displayName` = `Filter by quality`
- `services/service/menu/filter@name` = `quality`
- `services/service/menu/filter/value@displayName` = `MQA`, `High Resolution`, `CD`
- `services/service/menu/filter/value@name` = `mqa`, `hr`, `cd`
- `services/service/menu/filter/value@type` = `mqa`, `hr`, `cd`
- `services/service/menu/genreGroup@displayName` = `Genres`, `Moods`
- `services/service/menu/genreGroup@minimumSchemaVersion` = `20`
- `services/service/menu/genreGroup/browseRequest@resultType` = `Genre`
- `services/service/menu/genreGroup/browseRequest@url` = `/library/v1/Genres`, `/Genres`
- `services/service/menu/genreGroup/menuEntry@displayName` = `Songs`, `Artists`, `Albums`
- `services/service/menu/genreGroup/menuEntry@inlineRows` = `5`, `1`
- `services/service/menu/genreGroup/menuEntry/browseRequest@grouped` = `true`
- `services/service/menu/genreGroup/menuEntry/browseRequest@resultType` = `Song`, `Artist`, `Album`
- `services/service/menu/genreGroup/menuEntry/browseRequest@url` = `/library/v1/Songs`, `/library/v1/Artists`, `/library/v1/Albums`
- `services/service/menu/genreGroup/menuEntry/browseRequest/genreItemParameter@name` = `genre`, `mood`
- `services/service/menu/genreGroup/menuEntry/browseRequest/genreItemParameter@source` = `genreid`
- `services/service/menu/genreGroup/menuEntry/sort@default` = `alpha`
- `services/service/menu/genreGroup/menuEntry/sort@minimumSchemaVersion` = `19`
- `services/service/menu/genreGroup/menuEntry/sort@name` = `sort`
- `services/service/menu/genreGroup/menuEntry/sort/value@displayName` = `A → Z`, `Recent`, `Year`
- `services/service/menu/genreGroup/menuEntry/sort/value@name` = `alpha`, `recent`, `year`
- `services/service/menu/inlineEntry@displayName` = `New`, `Recent Favourites`
- `services/service/menu/inlineEntry@inlineRows` = `1`
- `services/service/menu/inlineEntry@minimumSchemaVersion` = `19`
- `services/service/menu/inlineEntry/browseRequest@resultType` = `Album`
- `services/service/menu/inlineEntry/browseRequest@url` = `/library/v1/Albums`, `/Albums`
- `services/service/menu/menuEntry@defaultView` = `true`
- `services/service/menu/menuEntry@displayName` = `Playlists`, `Alarms`, `Alarm Sound`
- `services/service/menu/menuEntry@inlineRows` = `5`
- `services/service/menu/menuEntry@minimumSchemaVersion` = `12`, `5`
- `services/service/menu/menuEntry/browseRequest@grouped` = `true`
- `services/service/menu/menuEntry/browseRequest@myPlaylistsFilter` = `myPlaylists=1`
- `services/service/menu/menuEntry/browseRequest@resultType` = `Playlist`, `Alarms`, `BrowseMenu`
- `services/service/menu/menuEntry/browseRequest@type` = `favourite`
- `services/service/menu/menuEntry/browseRequest@url` = `/Playlists`, `/Alarms`, `/RadioBrowse`
- `services/service/menu/menuEntry/browseRequest/requestItemParameter@name` = `path`
- `services/service/menu/menuEntry/browseRequest/requestItemParameter@optional` = `true`
- `services/service/menu/menuEntry/sort@default` = `alpha`
- `services/service/menu/menuEntry/sort@minimumSchemaVersion` = `19`
- `services/service/menu/menuEntry/sort@name` = `sort`
- `services/service/menu/menuEntry/sort/value@displayName` = `Date added`, `A → Z`, `Recent`
- `services/service/menu/menuEntry/sort/value@name` = `recent`, `alpha`, `year`
- `services/service/menu/menuGroup@context` = `Playlist`, `Artist`, `Composer`
- `services/service/menu/menuGroup@displayName` = `New`, `TIDAL Rising`, `Recommendations`
- `services/service/menu/menuGroup@id` = `LocalMusic-Artist`, `LocalMusic-Composer`, `LocalMusic-Album`
- `services/service/menu/menuGroup@mainMenu` = `true`
- `services/service/menu/menuGroup@minimumSchemaVersion` = `12`, `3`, `10`
- `services/service/menu/menuGroup/menuEntry@displayName` = `Songs`, `Play now`, `Shuffle`
- `services/service/menu/menuGroup/menuEntry@inlineRows` = `2`, `5`, `1`
- `services/service/menu/menuGroup/menuEntry@minimumSchemaVersion` = `13`, `14`, `7`
- `services/service/menu/menuGroup/menuEntry/browseRequest@myPlaylistsFilter` = `myPlaylists=1`
- `services/service/menu/menuGroup/menuEntry/browseRequest@resultType` = `Song`, `BrowseMenu`, `Info`
- `services/service/menu/menuGroup/menuEntry/browseRequest@type` = `info`, `addtoplaylist`, `relatedStations`
- `services/service/menu/menuGroup/menuEntry/browseRequest@url` = `/Songs`, `/RadioBrowse`, `/Info`
- `services/service/menu/menuGroup/menuEntry/browseRequest@xmlRequestParameter` = `format=xml`
- `services/service/menu/menuGroup/menuEntry/browseRequest/requestItemParameter@name` = `playlist`, `artist`, `composer`
- `services/service/menu/menuGroup/menuEntry/browseRequest/requestItemParameter@optional` = `true`
- `services/service/menu/menuGroup/menuEntry/browseRequest/requestItemParameter@source` = `filename`, `preset_id`, `URL`
- `services/service/menu/menuGroup/menuEntry/confirmAction@text` = `Delete playlist: %s?`
- `services/service/menu/menuGroup/menuEntry/confirmAction/textItemSubstitution@attribute` = `text`
- `services/service/menu/menuGroup/menuEntry/confirmAction/textItemSubstitution@source` = `playlist`
- `services/service/menu/menuGroup/menuEntry/contextRequest@resultType` = `Artist`, `Album`
- `services/service/menu/menuGroup/menuEntry/contextRequest@type` = `gotoartist`, `gotoalbum`
- `services/service/menu/menuGroup/menuEntry/contextRequest@url` = `/library/v1/Artists`, `/library/v1/Albums`, `/Artists`
- `services/service/menu/menuGroup/menuEntry/contextRequest/requestItemParameter@name` = `artist`, `album`, `artistid`
- `services/service/menu/menuGroup/menuEntry/disableOnAttribute@name` = `playlistid`, `isFavourite`, `is_preset`
- `services/service/menu/menuGroup/menuEntry/enableOnAttribute@name` = `isFavourite`, `is_preset`, `inputType`
- `services/service/menu/menuGroup/menuEntry/filter@class` = `alternative`
- `services/service/menu/menuGroup/menuEntry/filter@default` = `20`
- `services/service/menu/menuGroup/menuEntry/filter@displayName` = `Filter by quality`
- `services/service/menu/menuGroup/menuEntry/filter@minimumSchemaVersion` = `35`
- `services/service/menu/menuGroup/menuEntry/filter@name` = `quality`
- `services/service/menu/menuGroup/menuEntry/filter@required` = `true`
- `services/service/menu/menuGroup/menuEntry/filter/value@displayName` = `MQA`, `CD Quality`
- `services/service/menu/menuGroup/menuEntry/filter/value@name` = `20`, `4`
- `services/service/menu/menuGroup/menuEntry/filter/value@type` = `mqa`, `cd`
- `services/service/menu/menuGroup/menuEntry/request@preset_image` = `image`
- `services/service/menu/menuGroup/menuEntry/request@preset_name` = `text`, `title1`, `playlist`
- `services/service/menu/menuGroup/menuEntry/request@preset_url` = `URL`, `preset_url`
- `services/service/menu/menuGroup/menuEntry/request@subtype` = `now`, `shuffle`, `next`
- `services/service/menu/menuGroup/menuEntry/request@type` = `add`, `delete`, `favourite`
- `services/service/menu/menuGroup/menuEntry/request@url` = `/Add`, `/Delete`, `/AddFavourite`
- `services/service/menu/menuGroup/menuEntry/request/requestItemParameter@name` = `playlist`, `playlistid`, `name`
- `services/service/menu/menuGroup/menuEntry/request/requestItemParameter@optional` = `true`
- `services/service/menu/menuGroup/menuEntry/request/requestItemParameter@source` = `playlist`, `filename`, `preset_id`
- `services/service/menu/menuGroup/menuEntry/searchRequest@resultType` = `Search`
- `services/service/menu/menuGroup/menuEntry/searchRequest@service` = `Tidal`
- `services/service/menu/menuGroup/menuEntry/searchRequest@subtitleParameter` = `expr`
- `services/service/menu/menuGroup/menuEntry/searchRequest@type` = `searchOn`
- `services/service/menu/menuGroup/menuEntry/searchRequest@url` = `/Search`
- `services/service/menu/menuGroup/menuEntry/searchRequest@view` = `artists`, `albums`
- `services/service/menu/menuGroup/menuEntry/searchRequest/requestItemParameter@name` = `expr`
- `services/service/menu/menuGroup/menuEntry/searchRequest/requestItemParameter@source` = `artist`, `album`
- `services/service/menu/menuGroup/menuEntry/sort@default` = `alpha`, `name`
- `services/service/menu/menuGroup/menuEntry/sort@minimumSchemaVersion` = `19`
- `services/service/menu/menuGroup/menuEntry/sort@name` = `sort`
- `services/service/menu/menuGroup/menuEntry/sort/value@displayName` = `A → Z`, `Release date`, `Recent`
- `services/service/menu/menuGroup/menuEntry/sort/value@name` = `alpha`, `date`, `recent`
- `services/service/menu/menuGroup/menuEntry/textItemSubstitution@attribute` = `displayName`
- `services/service/menu/menuGroup/menuEntry/textItemSubstitution@source` = `artist`
- `services/service/menu/menuGroup/menuGroup@context` = `Song`, `NowPlaying`
- `services/service/menu/menuGroup/menuGroup/menuEntry@displayName` = `Favourite`, `Remove favourite`, `Add to playlist…`
- `services/service/menu/menuGroup/menuGroup/menuEntry@minimumSchemaVersion` = `7`, `14`, `11`
- `services/service/menu/menuGroup/menuGroup/menuEntry/browseRequest@resultType` = `AddToPlaylistOptions`, `Info`, `BriefInfo`
- `services/service/menu/menuGroup/menuGroup/menuEntry/browseRequest@type` = `addtoplaylist`, `info`, `selectStream`
- `services/service/menu/menuGroup/menuGroup/menuEntry/browseRequest@url` = `/AddToPlaylistOptions`, `/Info`, `/RadioBrowse`
- `services/service/menu/menuGroup/menuGroup/menuEntry/browseRequest/requestItemParameter@name` = `songid`, `artist`, `album`
- `services/service/menu/menuGroup/menuGroup/menuEntry/browseRequest/requestItemParameter@optional` = `true`
- `services/service/menu/menuGroup/menuGroup/menuEntry/browseRequest/requestItemParameter@source` = `filename`, `preset_id`, `songid`
- `services/service/menu/menuGroup/menuGroup/menuEntry/contextRequest@resultType` = `Album`, `Artist`
- `services/service/menu/menuGroup/menuGroup/menuEntry/contextRequest@type` = `gotoalbum`, `gotoartist`
- `services/service/menu/menuGroup/menuGroup/menuEntry/contextRequest@url` = `/library/v1/Albums`, `/library/v1/Artists`, `/Albums`
- `services/service/menu/menuGroup/menuGroup/menuEntry/contextRequest/requestItemParameter@name` = `artist`, `album`, `albumid`
- `services/service/menu/menuGroup/menuGroup/menuEntry/disableOnAttribute@name` = `isFavourite`, `is_preset`
- `services/service/menu/menuGroup/menuGroup/menuEntry/enableOnAttribute@name` = `isFavourite`, `is_preset`
- `services/service/menu/menuGroup/menuGroup/menuEntry/request@preset_image` = `image`, `stationImage`
- `services/service/menu/menuGroup/menuGroup/menuEntry/request@preset_name` = `preset_name`, `title1`
- `services/service/menu/menuGroup/menuGroup/menuEntry/request@preset_url` = `streamUrl`, `preset_url`
- `services/service/menu/menuGroup/menuGroup/menuEntry/request@subtype` = `add`, `delete`
- `services/service/menu/menuGroup/menuGroup/menuEntry/request@type` = `favourite`, `preset`, `playRadio`
- `services/service/menu/menuGroup/menuGroup/menuEntry/request@url` = `/AddFavourite`, `/DeleteFavourite`, `/Action`
- `services/service/menu/menuGroup/menuGroup/menuEntry/request/requestItemParameter@name` = `fn`, `preset_id`, `id`
- `services/service/menu/menuGroup/menuGroup/menuEntry/request/requestItemParameter@optional` = `true`
- `services/service/menu/menuGroup/menuGroup/menuEntry/request/requestItemParameter@source` = `filename`, `preset_id`, `preset_name`
- `services/service/menu/menuGroup/menuGroup/menuEntry/searchRequest@resultType` = `Search`
- `services/service/menu/menuGroup/menuGroup/menuEntry/searchRequest@service` = `Tidal`
- `services/service/menu/menuGroup/menuGroup/menuEntry/searchRequest@subtitleParameter` = `expr`
- `services/service/menu/menuGroup/menuGroup/menuEntry/searchRequest@type` = `searchOn`
- `services/service/menu/menuGroup/menuGroup/menuEntry/searchRequest@url` = `/Search`
- `services/service/menu/menuGroup/menuGroup/menuEntry/searchRequest@view` = `artists`, `songs`
- `services/service/menu/menuGroup/menuGroup/menuEntry/searchRequest/requestItemParameter@name` = `expr`
- `services/service/menu/menuGroup/menuGroup/menuEntry/searchRequest/requestItemParameter@source` = `artist`, `title2`
- `services/service/menu/menuGroup/menuGroup/menuEntry/textItemSubstitution@attribute` = `displayName`
- `services/service/menu/menuGroup/menuGroup/menuEntry/textItemSubstitution@source` = `artist`, `title2`
- `services/service/menu/menuGroup/search@parameterName` = `expr`
- `services/service/menu/menuGroup/search@prompt` = `Search stations, shows, podcasts`, `Search stations and podcasts`
- `services/service/menu/menuGroup/search/browseRequest@resultType` = `BrowseMenu`
- `services/service/menu/menuGroup/search/browseRequest@url` = `/RadioBrowse`
- `services/service/menu/menuGroup/search/menuGroup@minimumSchemaVersion` = `2`
- `services/service/menu/menuGroup/search/menuGroup/menuEntry@displayName` = `Stations`, `Podcasts`
- `services/service/menu/menuGroup/search/menuGroup/menuEntry/browseRequest@resultType` = `BrowseMenu`
- `services/service/menu/menuGroup/search/menuGroup/menuEntry/browseRequest@url` = `/RadioBrowse`
- `services/service/menu/search@hasSuggestions` = `true`
- `services/service/menu/search@parameterName` = `expr`
- `services/service/menu/search@prompt` = `Search...`, `Search TIDAL...`
- `services/service/menu/search/browseRequest@resultType` = `Search`
- `services/service/menu/search/browseRequest@url` = `/library/v1/Search`, `/Search`
- `services/service/menu/search/menuGroup@context` = `Search`
- `services/service/menu/search/menuGroup@minimumSchemaVersion` = `2`
- `services/service/menu/search/menuGroup/menuEntry@displayName` = `Artists`, `Albums`, `Songs`
- `services/service/menu/search/menuGroup/menuEntry@inlineRows` = `4`, `1`
- `services/service/menu/search/menuGroup/menuEntry@minimumSchemaVersion` = `12`
- `services/service/menu/search/menuGroup/menuEntry/browseRequest@resultType` = `Artist`, `Album`, `Song`
- `services/service/menu/search/menuGroup/menuEntry/browseRequest@url` = `/library/v1/Artists`, `/library/v1/Albums`, `/library/v1/Songs`

</details>

## `/Settings`

| element path | n | attributes (n) | sample text |
|---|---|---|---|
| `settings` | 17 | `pageId`(10), `schemaVersion`(17) | - |
| `settings/menuGroup` | 38 | `defaults`(8), `displayName`(38), `icon`(38), `id`(38), `url`(13) | - |
| `settings/menuGroup/menuGroup` | 17 | `description`(1), `displayName`(17), `icon`(17), `id`(17), `url`(16) | - |
| `settings/menuGroup/setting` | 55 | `class`(46), `description`(42), `displayName`(55), `explanation`(25), `helpUrl`(8), `hideIfDisabled`(7), `icon`(55), `id`(55), `name`(47), `pattern`(1), `patternError`(1), `refresh`(8), `style`(1), `url`(44), `value`(36) | - |
| `settings/menuGroup/setting/dependsOn` | 10 | `name`(10), `value`(10) | - |
| `settings/menuGroup/setting/value` | 47 | `displayName`(43), `max`(4), `min`(4), `minRange`(1), `name`(43), `step`(3), `units`(4) | - |
| `settings/menuGroup/setting/webview` | 9 | `url`(9) | - |
| `settings/setting` | 14 | `class`(14), `count`(7), `displayName`(14), `enabled`(7), `icon`(14), `id`(14), `sleep`(7) | - |

<details><summary>attribute value samples</summary>

- `settings@pageId` = `capture`, `audio`, `player`
- `settings@schemaVersion` = `35`, `99`
- `settings/menuGroup@defaults` = `false`
- `settings/menuGroup@displayName` = `Customize sources`, `Audio`, `Player`
- `settings/menuGroup@icon` = `/images/settings/ic_capture.png`, `/images/settings/ic_audio.png`, `/images/players/N125_sub.png`
- `settings/menuGroup@id` = `capture`, `audio`, `player`
- `settings/menuGroup@url` = `/setting`, `/audiomodes`
- `settings/menuGroup/menuGroup@description` = `On`
- `settings/menuGroup/menuGroup@displayName` = `Analog Input`, `Optical Input`, `HDMI ARC`
- `settings/menuGroup/menuGroup@icon` = `/images/capture/ic_analoginput.png`, `/images/capture/ic_opticalinput.png`, `/images/capture/ic_tv.png`
- `settings/menuGroup/menuGroup@id` = `capture-input0`, `capture-input1`, `capture-input2`
- `settings/menuGroup/menuGroup@url` = `/setting`
- `settings/menuGroup/setting@class` = `list`, `button`, `boolean`
- `settings/menuGroup/setting@description` = `Disabled`, `//192.0.2.102/music`, `Reindex your library music collection in case you have recen`
- `settings/menuGroup/setting@displayName` = `Bluetooth`, `Network shares`, `Reindex music collection`
- `settings/menuGroup/setting@explanation` = `Manual mode allows you to switch between sources in the navi`, `Manual mode allows you to switch between sources in the navi`, `Manual mode allows you to switch between sources in the navi`
- `settings/menuGroup/setting@helpUrl` = `https://support.bluos.net/hc/en-us/articles/020000000008`
- `settings/menuGroup/setting@hideIfDisabled` = `true`
- `settings/menuGroup/setting@icon` = `/images/settings/ic_bluetooth.png`, `/images/settings/ic_networkshares.png`, `/images/settings/ic_reindex.png`
- `settings/menuGroup/setting@id` = `bluetoothAutoplay`, `sharecfg`, `reindex`
- `settings/menuGroup/setting@name` = `bluetoothAutoplay`, `reindex`, `resizeall`
- `settings/menuGroup/setting@pattern` = `.{1,255}`
- `settings/menuGroup/setting@patternError` = `Maximum 255 characters.`
- `settings/menuGroup/setting@refresh` = `true`
- `settings/menuGroup/setting@style` = `center`
- `settings/menuGroup/setting@url` = `/audiomodes`, `/Reindex`, `/setting`
- `settings/menuGroup/setting@value` = `3`, `ON`, `OFF`
- `settings/menuGroup/setting/dependsOn@name` = `mqaDisable`, `eq-switch`, `subwoofer`
- `settings/menuGroup/setting/dependsOn@value` = `OFF`, `ON`, `withsub`
- `settings/menuGroup/setting/value@displayName` = `Manual`, `Automatic`, `Guest`
- `settings/menuGroup/setting/value@max` = `6`, `200`, `0`
- `settings/menuGroup/setting/value@min` = `-6`, `40`, `-90`
- `settings/menuGroup/setting/value@minRange` = `30`
- `settings/menuGroup/setting/value@name` = `0`, `1`, `2`
- `settings/menuGroup/setting/value@step` = `0.5`, `10`
- `settings/menuGroup/setting/value@units` = `dB`, `Hz`
- `settings/menuGroup/setting/webview@url` = `http://192.0.2.11:80/sharecfg?noheader=1`, `http://192.0.2.12:80/sharecfg?noheader=1`, `http://192.0.2.13:80/sharecfg?noheader=1`
- `settings/setting@class` = `alarms`, `sleep`
- `settings/setting@count` = `0`, `1`
- `settings/setting@displayName` = `Alarms`, `Sleep timer`
- `settings/setting@enabled` = `0`
- `settings/setting@icon` = `/images/settings/ic_alarms.png`, `/images/settings/ic_sleeptimer.png`
- `settings/setting@id` = `alarms`, `sleep`

</details>

## `/Shares`

| element path | n | attributes (n) | sample text |
|---|---|---|---|
| `shares` | 2 | `count`(2) | - |
| `shares/share` | 2 | - | - |
| `shares/share/sharename` | 2 | - | `\\192.0.2.102\music` |
| `shares/share/username` | 2 | - | `[REDACTED-value-1]` |

<details><summary>attribute value samples</summary>

- `shares@count` = `1`

</details>

## `/Songs`

| element path | n | attributes (n) | sample text |
|---|---|---|---|
| `songs` | 5 | `category`(5), `end`(5), `service`(5), `sort`(3), `start`(5) | - |
| `songs/nextlink` | 5 | - | `/Songs?category=FAVOURITES&end=79&service=Tidal&start=30`; `/Songs?category=FAVOURITES&end=99&service=Tidal&start=50`; `/Songs?category=FAVOURITES&end=79&service=Tidal&sort=recent&` |
| `songs/song` | 154 | `albumid`(154), `artistid`(154), `isFavourite`(154), `similarstationid`(154), `songid`(154), `trackstationid`(154) | - |
| `songs/song/alb` | 154 | - | `たぶん`; `04.49 Uhr`; `Everything We Had To Leave Behind` |
| `songs/song/art` | 154 | - | `YOASOBI`; `Azaleh`; `Chicane` |
| `songs/song/date` | 5 | - | `2016-12-16`; `2019-06-26` |
| `songs/song/discno` | 154 | - | `1` |
| `songs/song/fn` | 154 | - | `Tidal:146345183`; `Tidal:100745454`; `Tidal:176976290` |
| `songs/song/quality` | 154 | - | `hd`; `cd` |
| `songs/song/time` | 154 | - | `259`; `261`; `265` |
| `songs/song/title` | 154 | - | `たぶん`; `04.49 Uhr`; `1000 More Suns` |
| `songs/song/track` | 154 | - | `1`; `8`; `2` |

<details><summary>attribute value samples</summary>

- `songs@category` = `FAVOURITES`
- `songs@end` = `79`, `99`
- `songs@service` = `Tidal`
- `songs@sort` = `recent`, `recentDesc`, `-recent`
- `songs@start` = `30`, `50`
- `songs/song@albumid` = `146345182`, `100745453`, `176976280`
- `songs/song@artistid` = `17603073`, `6437711`, `688`
- `songs/song@isFavourite` = `1`
- `songs/song@similarstationid` = `Tidal:radio:artist/17603073`, `Tidal:radio:artist/6437711`, `Tidal:radio:artist/688`
- `songs/song@songid` = `Tidal:146345183`, `Tidal:100745454`, `Tidal:176976290`
- `songs/song@trackstationid` = `Tidal:radio:track/146345183`, `Tidal:radio:track/100745454`, `Tidal:radio:track/176976290`

</details>

## `/Status`

| element path | n | attributes (n) | sample text |
|---|---|---|---|
| `status` | 8 | `etag`(8) | - |
| `status/actions` | 1 | - | - |
| `status/actions/action` | 4 | `icon`(2), `name`(4), `state`(4), `text`(2), `type`(2), `url`(3) | - |
| `status/album` | 7 | - | `Heaven`; `Romanticize The Dive`; `Chasing Time` |
| `status/albumid` | 7 | - | `48513984`; `482411342`; `169319097` |
| `status/artist` | 7 | - | `Alex Adair`; `Metric`; `Oscuro` |
| `status/artistid` | 7 | - | `6081277`; `65040`; `32670299` |
| `status/autofill` | 1 | - | `6` |
| `status/canMovePlayback` | 8 | - | `true` |
| `status/canSeek` | 8 | - | `1`; `0` |
| `status/cursor` | 8 | - | `36`; `124`; `29` |
| `status/db` | 8 | - | `-49.1`; `-27.5`; `-38` |
| `status/dirac` | 7 | - | `1` |
| `status/fn` | 7 | - | `Tidal:48513985`; `Tidal:482411348`; `Tidal:169319098` |
| `status/image` | 8 | - | `/Artwork?service=Tidal&songid=Tidal%3A48513985`; `/Artwork?service=Tidal&songid=Tidal%3A482411348`; `/Artwork?service=Tidal&songid=Tidal%3A169319098` |
| `status/indexing` | 8 | - | `0` |
| `status/isFavourite` | 7 | - | `0`; `1` |
| `status/mid` | 8 | - | `19` |
| `status/mode` | 8 | - | `1` |
| `status/mqaOFS` | 5 | - | `44100` |
| `status/mute` | 8 | - | `0` |
| `status/name` | 7 | - | `Heaven`; `Moral Compass`; `Chasing Time` |
| `status/pid` | 8 | - | `1193`; `235`; `273` |
| `status/prid` | 8 | - | `1`; `0` |
| `status/quality` | 8 | - | `mqaAuthored`; `hd`; `cd` |
| `status/repeat` | 8 | - | `2` |
| `status/secs` | 8 | - | `47`; `0`; `26` |
| `status/service` | 8 | - | `Tidal`; `RadioParadise` |
| `status/serviceIcon` | 8 | - | `/Sources/images/TidalIcon.png`; `/Sources/images/RadioParadiseIcon.png` |
| `status/serviceName` | 8 | - | `TIDAL`; `Radio Paradise` |
| `status/serviceType` | 8 | - | `CloudService`; `RadioService` |
| `status/shuffle` | 8 | - | `1`; `0` |
| `status/sid` | 8 | - | `50`; `83`; `72` |
| `status/similarstationid` | 7 | - | `Tidal:radio:artist/6081277`; `Tidal:radio:artist/65040`; `Tidal:radio:artist/32670299` |
| `status/sleep` | 8 | - | - |
| `status/song` | 8 | - | `17`; `0`; `5` |
| `status/songid` | 7 | - | `Tidal:48513985`; `Tidal:482411348`; `Tidal:169319098` |
| `status/state` | 8 | - | `play`; `stop`; `pause` |
| `status/stationImage` | 1 | - | `https://img.radioparadise.com/channels/0/0/cover_512x512/0.j` |
| `status/streamFormat` | 6 | - | `16/44.1`; `FLAC 16/44.1` |
| `status/streamUrl` | 1 | - | `RadioParadise:/0:4` |
| `status/syncStat` | 8 | - | `523`; `1025`; `963` |
| `status/title1` | 8 | - | `Heaven`; `Moral Compass`; `Chasing Time` |
| `status/title2` | 7 | - | `Alex Adair`; `Metric`; `Oscuro` |
| `status/title3` | 7 | - | `Heaven`; `Romanticize The Dive`; `Chasing Time` |
| `status/totlen` | 8 | - | `177`; `268`; `228` |
| `status/trackstationid` | 7 | - | `Tidal:radio:track/48513985`; `Tidal:radio:track/482411348`; `Tidal:radio:track/169319098` |
| `status/twoline_title1` | 8 | - | `Heaven`; `Moral Compass`; `Chasing Time` |
| `status/twoline_title2` | 7 | - | `Alex Adair • Heaven`; `Metric • Romanticize The Dive`; `Oscuro • Chasing Time` |
| `status/volume` | 8 | - | `20`; `27`; `38` |

<details><summary>attribute value samples</summary>

- `status@etag` = `61bbe2e9764ecaa8b1e8a6a87503b2c3`, `d35ca671f17d35551e6a24c758354d9f`, `1dc868bf9aa88bfaf4c822f054a820ec`
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
| `SyncStatus` | 4 | `brand`(4), `class`(4), `db`(4), `etag`(4), `hasSubwoofer`(2), `icon`(4), `id`(4), `initialized`(4), `mac`(4), `model`(4), `modelName`(4), `name`(4), `schemaVersion`(4), `syncStat`(4), `version`(4), `volume`(4) | - |
| `SyncStatus/bluetoothOutput` | 3 | - | - |
| `SyncStatus/pairWithSub` | 4 | - | - |

<details><summary>attribute value samples</summary>

- `SyncStatus@brand` = `Bluesound`
- `SyncStatus@class` = `streamer`
- `SyncStatus@db` = `-49.1`, `-27.5`, `-38`
- `SyncStatus@etag` = `523`, `1025`, `963`
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

</details>

## `/Version`

| element path | n | attributes (n) | sample text |
|---|---|---|---|
| `version` | 1 | - | `v0.4.13` |

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

## `/ui/Configuration`

| element path | n | attributes (n) | sample text |
|---|---|---|---|
| `configuration` | 1 | - | - |
| `configuration/item` | 11 | `URI`(11), `id`(11), `resultType`(3) | - |

<details><summary>attribute value samples</summary>

- `configuration/item@URI` = `/ui/Home`, `/ui/RecentlyPlayed`, `/ui/News`
- `configuration/item@id` = `home`, `recentlyPlayed`, `news`
- `configuration/item@resultType` = `contextMenu`, `queue`

</details>

## `/ui/Favourites`

| element path | n | attributes (n) | sample text |
|---|---|---|---|
| `screen` | 1 | `id`(1), `screenTitle`(1), `service`(1), `version`(1), `{http://www.w3.org/2001/XMLSchema-instance}noNamespaceSchemaLocation`(1) | - |
| `screen/infoPanel` | 1 | `icon`(1), `subText`(1), `text`(1) | - |
| `screen/selectorMenu` | 1 | `menuTitle`(1), `replaceScreen`(1) | - |
| `screen/selectorMenu/item` | 3 | `icon`(3), `selected`(1), `text`(3) | - |
| `screen/selectorMenu/item/action` | 3 | `URI`(3), `refreshScreen`(3), `type`(3) | - |

<details><summary>attribute value samples</summary>

- `screen@id` = `screen-LocalMusic-Favourites`
- `screen@screenTitle` = `Favourites`
- `screen@service` = `LocalMusic`
- `screen@version` = `1`
- `screen@{http://www.w3.org/2001/XMLSchema-instance}noNamespaceSchemaLocation` = `screen.xsd`
- `screen/infoPanel@icon` = `/images/ui/ic_info_favourites.png`
- `screen/infoPanel@subText` = `You can add any content within Library as a favourite to hav`
- `screen/infoPanel@text` = `You don't have any Favourites on Library`
- `screen/selectorMenu@menuTitle` = `Select Service`
- `screen/selectorMenu@replaceScreen` = `false`
- `screen/selectorMenu/item@icon` = `/images/LibraryIcon.png?style=Default`, `/Sources/images/TidalIcon.png?style=Default`, `/Sources/images/TuneInIcon.png?style=Default`
- `screen/selectorMenu/item@selected` = `true`
- `screen/selectorMenu/item@text` = `Library`, `TIDAL`, `TuneIn`
- `screen/selectorMenu/item/action@URI` = `/ui/action?CfavouritesService=LocalMusic`, `/ui/action?CfavouritesService=Tidal`, `/ui/action?CfavouritesService=TuneIn`
- `screen/selectorMenu/item/action@refreshScreen` = `true`
- `screen/selectorMenu/item/action@type` = `player-link`

</details>

## `/ui/Home`

| element path | n | attributes (n) | sample text |
|---|---|---|---|
| `screen` | 1 | `id`(1), `refreshOnPlayerChange`(1), `screenTitle`(1), `version`(1), `{http://www.w3.org/2001/XMLSchema-instance}noNamespaceSchemaLocation`(1) | - |
| `screen/customiseScreen` | 1 | `text`(1) | - |
| `screen/customiseScreen/action` | 1 | `URI`(1), `refreshScreen`(1), `title`(1), `type`(1) | - |
| `screen/menuAction` | 1 | `type`(1) | - |
| `screen/menuAction/action` | 1 | `URI`(1), `type`(1) | - |
| `screen/refreshOnStatusChange` | 1 | `key`(1), `value`(1) | - |
| `screen/row` | 7 | `id`(7), `noReorder`(1), `scrollable`(6), `solidBackground`(7), `title`(6) | - |
| `screen/row/fetch` | 2 | `itemType`(2), `unlikely`(1), `url`(2) | - |
| `screen/row/largeThumbnail` | 14 | `icon`(14), `image`(14), `objectType`(10), `subTitle`(8), `title`(14) | - |
| `screen/row/largeThumbnail/action` | 14 | `URI`(14), `haptic`(11), `resultType`(3), `service`(3), `title`(3), `type`(14) | - |
| `screen/row/largeThumbnail/contextMenu` | 10 | `URI`(10), `resultType`(10), `type`(10) | - |
| `screen/row/largeThumbnail/nowPlayingMatch` | 4 | `key`(4), `value`(4) | - |
| `screen/row/largeThumbnail/playAction` | 14 | `URI`(14), `haptic`(14), `type`(14) | - |
| `screen/row/menuAction` | 5 | `text`(5) | - |
| `screen/row/menuAction/action` | 5 | `URI`(5), `haptic`(1), `refreshScreen`(1), `resultType`(4), `title`(4), `type`(5) | - |
| `screen/row/smallThumbnail` | 2 | `icon`(2), `title`(1) | - |
| `screen/row/smallThumbnail/action` | 2 | `URI`(2), `haptic`(1), `type`(2) | - |
| `screen/row/source` | 3 | `icon`(3), `title`(1) | - |
| `screen/row/source/action` | 3 | `URI`(3), `haptic`(1), `resultType`(2), `service`(2), `title`(2), `type`(3) | - |
| `screen/row/source/button` | 6 | `backgroundColor`(6), `icon`(1), `text`(6), `textColor`(6) | - |
| `screen/row/source/button/action` | 6 | `URI`(6), `haptic`(2), `resultType`(3), `service`(2), `title`(3), `type`(6) | - |
| `screen/row/source/nowPlayingMatch` | 1 | `key`(1), `value`(1) | - |
| `screen/row/teaser` | 2 | `backgroundImage`(2), `body`(2), `closable`(2), `id`(2), `title`(2) | - |
| `screen/row/teaser/action` | 2 | `URI`(2), `type`(2) | - |
| `screen/row/teaser/button` | 2 | `backgroundColor`(2), `text`(2), `textColor`(2) | - |
| `screen/row/teaser/button/action` | 2 | `URI`(2), `type`(2) | - |

<details><summary>attribute value samples</summary>

- `screen@id` = `screen-home`
- `screen@refreshOnPlayerChange` = `true`
- `screen@screenTitle` = `Home`
- `screen@version` = `1`
- `screen@{http://www.w3.org/2001/XMLSchema-instance}noNamespaceSchemaLocation` = `screen.xsd`
- `screen/customiseScreen@text` = `Customise Home`
- `screen/customiseScreen/action@URI` = `/customise-screen`
- `screen/customiseScreen/action@refreshScreen` = `true`
- `screen/customiseScreen/action@title` = `Customise Home`
- `screen/customiseScreen/action@type` = `deep-link`
- `screen/menuAction@type` = `settings`
- `screen/menuAction/action@URI` = `/settings`
- `screen/menuAction/action@type` = `deep-link`
- `screen/refreshOnStatusChange@key` = `prid`
- `screen/refreshOnStatusChange@value` = `1`
- `screen/row@id` = `teaser`, `mostUsed`, `presets`
- `screen/row@noReorder` = `true`
- `screen/row@scrollable` = `true`
- `screen/row@solidBackground` = `false`, `true`
- `screen/row@title` = `Most Used`, `Presets`, `Recent Stations`
- `screen/row/fetch@itemType` = `largeThumbnail`
- `screen/row/fetch@unlikely` = `true`
- `screen/row/fetch@url` = `/ui/myPlaylistsRow?service=LocalMusic`, `/ui/myPlaylistsRow?service=Tidal`
- `screen/row/largeThumbnail@icon` = `/Sources/images/RadioParadiseIcon.png?style=Default`, `/Sources/images/TidalIcon.png?style=Default`
- `screen/row/largeThumbnail@image` = `https://img.radioparadise.com/channels/0/0/cover_512x512/0.j`, `https://img.radioparadise.com/channels/0/0/cover_512x512/0.j`, `/Artwork?service=Tidal&albumid=366537329`
- `screen/row/largeThumbnail@objectType` = `playlist`, `song`, `album`
- `screen/row/largeThumbnail@subTitle` = `AK • Peace of Mind`, `Heilung • Futha`, `Marion • Daydreaming`
- `screen/row/largeThumbnail@title` = `The Main Mix`, `The Main Mix (CD)`, `My Name Radio`
- `screen/row/largeThumbnail/action@URI` = `/ui/prf?u=%2FPlay%3Furl%3DRadioParadise%253A%252F0%253A20%26`, `/ui/prf?u=%2FPlay%3Furl%3DRadioParadise%253A%252F0%253A4%26t`, `/ui/prf?u=%2FPlay%3Furl%3DTidal%253Aradio%253Atrack%252F3665`
- `screen/row/largeThumbnail/action@haptic` = `true`
- `screen/row/largeThumbnail/action@resultType` = `screen`
- `screen/row/largeThumbnail/action@service` = `Tidal`
- `screen/row/largeThumbnail/action@title` = `Sunday Chill Mix: Ministry of Sound`, `My Mix 2`, `KPop Demon Hunters (Soundtrack from the Netflix Film)`
- `screen/row/largeThumbnail/action@type` = `player-link`, `browse`
- `screen/row/largeThumbnail/contextMenu@URI` = `/ui/ContextMenu?context=Playlist&image=%2FArtwork%3Fservice%`, `/ui/ContextMenu?album=Peace+of+Mind&albumid=140768092&artist`, `/ui/ContextMenu?album=Futha&albumid=106600730&artist=Heilung`
- `screen/row/largeThumbnail/contextMenu@resultType` = `contextMenu`
- `screen/row/largeThumbnail/contextMenu@type` = `browse`
- `screen/row/largeThumbnail/nowPlayingMatch@key` = `streamUrl`
- `screen/row/largeThumbnail/nowPlayingMatch@value` = `RadioParadise:/0:20`, `RadioParadise:/0:4`, `Tidal:radio:track/366537361`
- `screen/row/largeThumbnail/playAction@URI` = `/ui/prf?u=%2FPlay%3Furl%3DRadioParadise%253A%252F0%253A20%26`, `/ui/prf?u=%2FPlay%3Furl%3DRadioParadise%253A%252F0%253A4%26t`, `/ui/prf?u=%2FPlay%3Furl%3DTidal%253Aradio%253Atrack%252F3665`
- `screen/row/largeThumbnail/playAction@haptic` = `true`
- `screen/row/largeThumbnail/playAction@type` = `player-link`
- `screen/row/menuAction@text` = `View All`, `Clear`
- `screen/row/menuAction/action@URI` = `/ui/presets`, `/ui/clearUsageHistory?stations=1`, `/ui/RecentlyPlayed`
- `screen/row/menuAction/action@haptic` = `true`
- `screen/row/menuAction/action@refreshScreen` = `true`
- `screen/row/menuAction/action@resultType` = `screen`
- `screen/row/menuAction/action@title` = `Presets`, `Recently Played`, `Playlists`
- `screen/row/menuAction/action@type` = `browse`, `player-link`
- `screen/row/smallThumbnail@icon` = `/Artwork?service=Tidal&playlistimage=f8601f52-6d31-43bd-97a7`, `/images/ui/ic_small_thumbnail_add.png`
- `screen/row/smallThumbnail@title` = `Sunday Chill Mix: Ministry of Sound`
- `screen/row/smallThumbnail/action@URI` = `/Preset?id=1`, `/add-preset`
- `screen/row/smallThumbnail/action@haptic` = `true`
- `screen/row/smallThumbnail/action@type` = `player-link`, `deep-link`
- `screen/row/source@icon` = `/images/capture/ic_tv.png`, `/images/ui/Source/TidalLogo.png`, `/images/ui/Source/RadioParadiseLogo.png`
- `screen/row/source@title` = `HDMI ARC`
- `screen/row/source/action@URI` = `/Play?url=Capture%3Ahw%3Aimxspdif%2C0%2F1%2F25%2F2%3Fid%3Din`, `/ui/browseMenuGroup?service=Tidal`, `/ui/browseMenuGroup?service=RadioParadise`
- `screen/row/source/action@haptic` = `true`
- `screen/row/source/action@resultType` = `screen`
- `screen/row/source/action@service` = `Tidal`, `RadioParadise`
- `screen/row/source/action@title` = `TIDAL`, `Radio Paradise`
- `screen/row/source/action@type` = `player-link`, `browse`
- `screen/row/source/button@backgroundColor` = `#43a4ce`, `#292D2F`, `#ffffff`
- `screen/row/source/button@icon` = `/image/icon_settings.png`
- `screen/row/source/button@text` = `Play`, `Settings`, `My Music`
- `screen/row/source/button@textColor` = `#ffffff`, `#1e2223`
- `screen/row/source/button/action@URI` = `/Play?url=Capture%3Ahw%3Aimxspdif%2C0%2F1%2F25%2F2%3Fid%3Din`, `/Settings?id=capture-input2`, `/ui/Favourites?service=Tidal&singleService=1&title=My+Music`
- `screen/row/source/button/action@haptic` = `true`
- `screen/row/source/button/action@resultType` = `screen`
- `screen/row/source/button/action@service` = `Tidal`, `RadioParadise`
- `screen/row/source/button/action@title` = `My Music`, `New`, `Radio Paradise`
- `screen/row/source/button/action@type` = `player-link`, `setting`, `browse`
- `screen/row/source/nowPlayingMatch@key` = `inputId`
- `screen/row/source/nowPlayingMatch@value` = `input2`
- `screen/row/teaser@backgroundImage` = `/images/ui/ic_teaser_add_service.png`, `/images/ui/ic_teaser_queue_builder.png`
- `screen/row/teaser@body` = `BluOS supports a broad number of music services.`, `This BluOS version adds an enhanced way of creating & managi`
- `screen/row/teaser@closable` = `true`
- `screen/row/teaser@id` = `add-service`, `qbm-education`
- `screen/row/teaser@title` = `Add your Music Service`, `Queue Builder Mode`
- `screen/row/teaser/action@URI` = `/redirectToCp?href=%2Fservices%3Fnoheader%3D1%26schemaVersio`, `/qbm-education`
- `screen/row/teaser/action@type` = `webpage`, `deep-link`
- `screen/row/teaser/button@backgroundColor` = `#00a4cb`
- `screen/row/teaser/button@text` = `Add Music Service`, `Explore Queue Builder Mode`
- `screen/row/teaser/button@textColor` = `#ffffff`
- `screen/row/teaser/button/action@URI` = `/redirectToCp?href=%2Fservices%3Fnoheader%3D1%26schemaVersio`, `/qbm-education`
- `screen/row/teaser/button/action@type` = `webpage`, `deep-link`

</details>

## `/ui/News`

| element path | n | attributes (n) | sample text |
|---|---|---|---|
| `screen` | 1 | `id`(1), `refreshOnPlayerChange`(1), `screenTitle`(1), `version`(1), `{http://www.w3.org/2001/XMLSchema-instance}noNamespaceSchemaLocation`(1) | - |
| `screen/list` | 1 | `id`(1) | - |

<details><summary>attribute value samples</summary>

- `screen@id` = `screen-news`
- `screen@refreshOnPlayerChange` = `true`
- `screen@screenTitle` = `News & Updates`
- `screen@version` = `1`
- `screen@{http://www.w3.org/2001/XMLSchema-instance}noNamespaceSchemaLocation` = `screen.xsd`
- `screen/list@id` = `news`

</details>

## `/ui/Queue`

| element path | n | attributes (n) | sample text |
|---|---|---|---|
| `queue` | 1 | `id`(1), `modified`(1), `offset`(1), `total`(1) | - |
| `queue/button` | 4 | `backgroundColor`(4), `icon`(4), `text`(4), `textColor`(4) | - |
| `queue/button/action` | 4 | `URI`(4), `event`(1), `haptic`(1), `notification`(1), `refreshScreen`(2), `resultType`(1), `title`(1), `type`(4) | - |
| `queue/item` | 20 | `duration`(20), `icon`(20), `image`(20), `quality`(20), `subSubTitle`(7), `subTitle`(20), `title`(20) | - |
| `queue/item/action` | 20 | `URI`(20), `haptic`(20), `type`(20) | - |
| `queue/item/contextMenu` | 20 | `URI`(20), `resultType`(20), `type`(20) | - |
| `queue/item/nowPlayingMatch` | 20 | `key`(20), `value`(20) | - |
| `queue/refreshOnStatusChange` | 1 | `key`(1), `value`(1) | - |

<details><summary>attribute value samples</summary>

- `queue@id` = `1193`
- `queue@modified` = `false`
- `queue@offset` = `0`
- `queue@total` = `37`
- `queue/button@backgroundColor` = `#2A2A2A`
- `queue/button@icon` = `/images/ui/btn_save_queue.png`, `/images/ui/btn_edit_queue.png`, `/images/ui/btn_clear_queue.png`
- `queue/button@text` = `Save`, `Edit`, `Clear`
- `queue/button@textColor` = `#ffffff`
- `queue/button/action@URI` = `/AddToPlaylistOptions?saveQueue=1`, `/edit-queue`, `/Clear`
- `queue/button/action@event` = `qbm_toggle:qbm=true`
- `queue/button/action@haptic` = `true`
- `queue/button/action@notification` = `Play Queue cleared`
- `queue/button/action@refreshScreen` = `true`
- `queue/button/action@resultType` = `SaveQueueOptions`
- `queue/button/action@title` = `Save playlist`
- `queue/button/action@type` = `browse`, `deep-link`, `player-link`
- `queue/item@duration` = `4:27`, `3:29`, `3:14`
- `queue/item@icon` = `/Sources/images/TidalIcon.png?style=Default`
- `queue/item@image` = `/Artwork?service=Tidal&songid=Tidal%3A122288231`, `/Artwork?service=Tidal&songid=Tidal%3A64753254`, `/Artwork?service=Tidal&songid=Tidal%3A53780764`
- `queue/item@quality` = `cd`, `hd`
- `queue/item@subSubTitle` = `Simmer Down`, `I Remember`, `We the Generation (Deluxe Edition)`
- `queue/item@subTitle` = `Andhim`, `AlunaGeorge`, `Feder`
- `queue/item@title` = `How Many Times`, `I'm In Control`, `Blind (feat. Emmi) [Radio Edit]`
- `queue/item/action@URI` = `/Play?id=0`, `/Play?id=1`, `/Play?id=2`
- `queue/item/action@haptic` = `true`
- `queue/item/action@type` = `player-link`
- `queue/item/contextMenu@URI` = `/ui/queueItemCM?id=0`, `/ui/queueItemCM?id=1`, `/ui/queueItemCM?id=2`
- `queue/item/contextMenu@resultType` = `contextMenu`
- `queue/item/contextMenu@type` = `browse`
- `queue/item/nowPlayingMatch@key` = `song`
- `queue/item/nowPlayingMatch@value` = `0`, `1`, `2`
- `queue/refreshOnStatusChange@key` = `pid`
- `queue/refreshOnStatusChange@value` = `1193`

</details>

## `/ui/RecentlyPlayed`

| element path | n | attributes (n) | sample text |
|---|---|---|---|
| `screen` | 1 | `id`(1), `refreshOnPlayerChange`(1), `screenTitle`(1), `version`(1), `{http://www.w3.org/2001/XMLSchema-instance}noNamespaceSchemaLocation`(1) | - |
| `screen/list` | 1 | `id`(1) | - |
| `screen/list/item` | 100 | `duration`(65), `icon`(100), `image`(100), `objectType`(100), `quality`(87), `subSubTitle`(28), `subTitle`(89), `title`(100) | - |
| `screen/list/item/action` | 100 | `URI`(100), `haptic`(65), `resultType`(35), `service`(35), `title`(35), `type`(100) | - |
| `screen/list/item/contextMenu` | 100 | `URI`(100), `resultType`(100), `type`(100) | - |
| `screen/menuAction` | 1 | `text`(1) | - |
| `screen/menuAction/action` | 1 | `URI`(1), `closeScreen`(1), `haptic`(1), `refreshScreen`(1), `type`(1) | - |

<details><summary>attribute value samples</summary>

- `screen@id` = `screen-recentlyPlayed`
- `screen@refreshOnPlayerChange` = `true`
- `screen@screenTitle` = `Recently Played`
- `screen@version` = `1`
- `screen@{http://www.w3.org/2001/XMLSchema-instance}noNamespaceSchemaLocation` = `screen.xsd`
- `screen/list@id` = `recent`
- `screen/list/item@duration` = `3:30`, `9:49`, `4:19`
- `screen/list/item@icon` = `/Sources/images/TidalIcon.png?style=Default`, `/images/LibraryIcon.png?style=Default`
- `screen/list/item@image` = `/Artwork?service=Tidal&playlistimage=f8601f52-6d31-43bd-97a7`, `/Artwork?service=Tidal&songid=Tidal%3A140768093`, `/Artwork?service=Tidal&songid=Tidal%3A106600734`
- `screen/list/item@objectType` = `playlist`, `song`, `album`
- `screen/list/item@quality` = `cd`, `hd`
- `screen/list/item@subSubTitle` = `51 Tracks • 3:11:42`, `12 Tracks • 37:52`, `19 Tracks • 37:14`
- `screen/list/item@subTitle` = `AK • Peace of Mind`, `Heilung • Futha`, `Marion • Daydreaming`
- `screen/list/item@title` = `Sunday Chill Mix: Ministry of Sound`, `Peace of Mind`, `Traust`
- `screen/list/item/action@URI` = `/ui/browseContext?service=Tidal&title=Sunday+Chill+Mix%3A+Mi`, `/ui/prf?u=%2FAdd%3Fplaynow%3D1%26file%3DTidal%253A140768093`, `/ui/prf?u=%2FAdd%3Fplaynow%3D1%26file%3DTidal%253A106600734`
- `screen/list/item/action@haptic` = `true`
- `screen/list/item/action@resultType` = `screen`
- `screen/list/item/action@service` = `Tidal`, `LocalMusic`
- `screen/list/item/action@title` = `Sunday Chill Mix: Ministry of Sound`, `My Mix 2`, `KPop Demon Hunters (Soundtrack from the Netflix Film)`
- `screen/list/item/action@type` = `browse`, `player-link`
- `screen/list/item/contextMenu@URI` = `/ui/ContextMenu?context=Playlist&image=%2FArtwork%3Fservice%`, `/ui/ContextMenu?album=Peace+of+Mind&albumid=140768092&artist`, `/ui/ContextMenu?album=Futha&albumid=106600730&artist=Heilung`
- `screen/list/item/contextMenu@resultType` = `contextMenu`
- `screen/list/item/contextMenu@type` = `browse`
- `screen/menuAction@text` = `Clear`
- `screen/menuAction/action@URI` = `/ui/clearUsageHistory?queued=1`
- `screen/menuAction/action@closeScreen` = `true`
- `screen/menuAction/action@haptic` = `true`
- `screen/menuAction/action@refreshScreen` = `true`
- `screen/menuAction/action@type` = `player-link`

</details>

## `/ui/Search`

| element path | n | attributes (n) | sample text |
|---|---|---|---|
| `screen` | 1 | `id`(1), `screenTitle`(1), `service`(1), `version`(1), `{http://www.w3.org/2001/XMLSchema-instance}noNamespaceSchemaLocation`(1) | - |
| `screen/search` | 1 | `URI`(1), `parameterName`(1), `prompt`(1), `resultType`(1), `service`(1), `title`(1), `type`(1) | - |
| `screen/selectorMenu` | 1 | `replaceScreen`(1) | - |
| `screen/selectorMenu/item` | 4 | `icon`(4), `selected`(1), `text`(4) | - |
| `screen/selectorMenu/item/action` | 4 | `URI`(4), `resultType`(4), `title`(4), `type`(4) | - |

<details><summary>attribute value samples</summary>

- `screen@id` = `screen-LocalMusic-Search`
- `screen@screenTitle` = `Search`
- `screen@service` = `LocalMusic`
- `screen@version` = `1`
- `screen@{http://www.w3.org/2001/XMLSchema-instance}noNamespaceSchemaLocation` = `screen.xsd`
- `screen/search@URI` = `/ui/Search?forService=LocalMusic`
- `screen/search@parameterName` = `q`
- `screen/search@prompt` = `Search...`
- `screen/search@resultType` = `screen`
- `screen/search@service` = `LocalMusic`
- `screen/search@title` = `Search`
- `screen/search@type` = `browse`
- `screen/selectorMenu@replaceScreen` = `false`
- `screen/selectorMenu/item@icon` = `/images/LibraryIcon.png?style=Default`, `/Sources/images/BluOSRadioIcon.png?style=Default`, `/Sources/images/TidalIcon.png?style=Default`
- `screen/selectorMenu/item@selected` = `true`
- `screen/selectorMenu/item@text` = `Library`, `Radio`, `TIDAL`
- `screen/selectorMenu/item/action@URI` = `/ui/Search?CsearchService=LocalMusic`, `/ui/Search?CsearchService=Airable`, `/ui/Search?CsearchService=Tidal`
- `screen/selectorMenu/item/action@resultType` = `screen`
- `screen/selectorMenu/item/action@title` = `Search`
- `screen/selectorMenu/item/action@type` = `browse`

</details>

## `/ui/Sources`

| element path | n | attributes (n) | sample text |
|---|---|---|---|
| `screen` | 1 | `id`(1), `refreshOnPlayerChange`(1), `screenTitle`(1), `version`(1), `{http://www.w3.org/2001/XMLSchema-instance}noNamespaceSchemaLocation`(1) | - |
| `screen/menuAction` | 1 | `type`(1) | - |
| `screen/menuAction/action` | 1 | `URI`(1), `refreshScreen`(1), `title`(1), `type`(1) | - |
| `screen/refreshOnStatusChange` | 1 | `key`(1), `value`(1) | - |
| `screen/row` | 2 | `id`(2), `scrollable`(1), `solidBackground`(2), `title`(2) | - |
| `screen/row/input` | 1 | `icon`(1), `title`(1) | - |
| `screen/row/input/action` | 1 | `URI`(1), `haptic`(1), `type`(1) | - |
| `screen/row/input/nowPlayingMatch` | 1 | `key`(1), `value`(1) | - |
| `screen/row/list` | 1 | - | - |
| `screen/row/list/service` | 6 | `icon`(6), `isLink`(6), `title`(6) | - |
| `screen/row/list/service/action` | 6 | `URI`(6), `haptic`(1), `resultType`(5), `service`(5), `title`(5), `type`(6) | - |
| `screen/row/list/service/nowPlayingMatch` | 5 | `key`(5), `value`(5) | - |
| `screen/row/menuAction` | 2 | `text`(2) | - |
| `screen/row/menuAction/action` | 2 | `URI`(2), `refreshScreen`(2), `title`(2), `type`(2) | - |

<details><summary>attribute value samples</summary>

- `screen@id` = `screen-sources`
- `screen@refreshOnPlayerChange` = `true`
- `screen@screenTitle` = `Music Sources`
- `screen@version` = `1`
- `screen@{http://www.w3.org/2001/XMLSchema-instance}noNamespaceSchemaLocation` = `screen.xsd`
- `screen/menuAction@type` = `add`
- `screen/menuAction/action@URI` = `/redirectToCp?href=%2Fservices%3Fnoheader%3D1%26schemaVersio`
- `screen/menuAction/action@refreshScreen` = `true`
- `screen/menuAction/action@title` = `Music Services`
- `screen/menuAction/action@type` = `webpage`
- `screen/refreshOnStatusChange@key` = `sid`
- `screen/refreshOnStatusChange@value` = `51`
- `screen/row@id` = `inputs`, `services`
- `screen/row@scrollable` = `true`
- `screen/row@solidBackground` = `false`
- `screen/row@title` = `Inputs`, `Music Services`
- `screen/row/input@icon` = `/images/capture/ic_tv.png`
- `screen/row/input@title` = `HDMI ARC`
- `screen/row/input/action@URI` = `/Play?url=Capture%3Ahw%3Aimxspdif%2C0%2F1%2F25%2F2%3Fid%3Din`
- `screen/row/input/action@haptic` = `true`
- `screen/row/input/action@type` = `player-link`
- `screen/row/input/nowPlayingMatch@key` = `inputId`
- `screen/row/input/nowPlayingMatch@value` = `input2`
- `screen/row/list/service@icon` = `/images/ui/Source/LibrarySourceIcon.png`, `/images/ui/Source/BluOSRadioSourceIcon.png`, `/images/ui/Source/RadioParadiseSourceIcon.png`
- `screen/row/list/service@isLink` = `true`, `false`
- `screen/row/list/service@title` = `Library`, `Radio`, `Radio Paradise`
- `screen/row/list/service/action@URI` = `/ui/browseMenuGroup?service=LocalMusic`, `/ui/browseMenuGroup?service=Airable`, `/ui/browseMenuGroup?service=RadioParadise`
- `screen/row/list/service/action@haptic` = `true`
- `screen/row/list/service/action@resultType` = `screen`
- `screen/row/list/service/action@service` = `LocalMusic`, `Airable`, `RadioParadise`
- `screen/row/list/service/action@title` = `Library`, `Radio`, `Radio Paradise`
- `screen/row/list/service/action@type` = `browse`, `player-link`
- `screen/row/list/service/nowPlayingMatch@key` = `service`
- `screen/row/list/service/nowPlayingMatch@value` = `LocalMusic`, `Airable`, `RadioParadise`
- `screen/row/menuAction@text` = `Customise`, `Manage`
- `screen/row/menuAction/action@URI` = `/Settings?id=capture`, `/redirectToCp?href=%2Fservices%3Fnoheader%3D1%26schemaVersio`
- `screen/row/menuAction/action@refreshScreen` = `true`
- `screen/row/menuAction/action@title` = `Inputs`, `Music Services`
- `screen/row/menuAction/action@type` = `setting`, `webpage`

</details>

## `/ui/nowPlayingCM`

| element path | n | attributes (n) | sample text |
|---|---|---|---|
| `contextMenu` | 1 | `image`(1), `subTitle`(1), `title`(1), `version`(1), `{http://www.w3.org/2001/XMLSchema-instance}noNamespaceSchemaLocation`(1) | - |
| `contextMenu/item` | 7 | `icon`(7), `text`(7) | - |
| `contextMenu/item/action` | 7 | `URI`(7), `haptic`(3), `notification`(1), `notificationIcon`(1), `refreshScreen`(1), `resultType`(4), `service`(4), `title`(4), `type`(7) | - |

<details><summary>attribute value samples</summary>

- `contextMenu@image` = `/Artwork?service=Tidal&songid=Tidal%3A48513985`
- `contextMenu@subTitle` = `Alex Adair • Heaven`
- `contextMenu@title` = `Heaven`
- `contextMenu@version` = `1`
- `contextMenu@{http://www.w3.org/2001/XMLSchema-instance}noNamespaceSchemaLocation` = `screen.xsd`
- `contextMenu/item@icon` = `/images/ui/cm_favourite_add.png`, `/images/ui/cm_addtoplaylist.png`, `/images/ui/cm_playRadio.png`
- `contextMenu/item@text` = `Favourite`, `Add to playlist…`, `Track radio`
- `contextMenu/item/action@URI` = `/AddFavourite?service=Tidal&songid=Tidal%3A48513985`, `/AddToPlaylistOptions?service=Tidal&songid=Tidal%3A48513985`, `/ui/prf?u=%2FPlay%3Fservice%3DTidal%26url%3DTidal%253Aradio%`
- `contextMenu/item/action@haptic` = `true`
- `contextMenu/item/action@notification` = `Added to favourites`
- `contextMenu/item/action@notificationIcon` = `/images/ui/cm_favourite_add.png`
- `contextMenu/item/action@refreshScreen` = `true`
- `contextMenu/item/action@resultType` = `AddToPlaylistOptions`, `screen`, `Info`
- `contextMenu/item/action@service` = `Tidal`
- `contextMenu/item/action@title` = `Add to playlist…`, `Heaven`, `Alex Adair`
- `contextMenu/item/action@type` = `player-link`, `browse`

</details>

## `/ui/presets`

| element path | n | attributes (n) | sample text |
|---|---|---|---|
| `screen` | 1 | `id`(1), `refreshOnPlayerChange`(1), `screenTitle`(1), `version`(1), `{http://www.w3.org/2001/XMLSchema-instance}noNamespaceSchemaLocation`(1), `ìsPresets`(1) | - |
| `screen/footer` | 1 | `text`(1), `type`(1) | - |
| `screen/footer/action` | 1 | `URI`(1), `refreshScreen`(1), `title`(1), `type`(1) | - |
| `screen/list` | 1 | - | - |
| `screen/list/item` | 1 | `counter`(1), `image`(1), `solidBackground`(1), `title`(1) | - |
| `screen/list/item/action` | 1 | `URI`(1), `haptic`(1), `type`(1) | - |
| `screen/list/item/contextMenu` | 1 | `URI`(1), `resultType`(1), `title`(1), `type`(1) | - |
| `screen/menuAction` | 1 | `type`(1) | - |
| `screen/menuAction/action` | 1 | `URI`(1), `refreshScreen`(1), `type`(1) | - |
| `screen/refreshOnStatusChange` | 1 | `key`(1), `value`(1) | - |

<details><summary>attribute value samples</summary>

- `screen@id` = `screen-presets`
- `screen@refreshOnPlayerChange` = `true`
- `screen@screenTitle` = `Presets`
- `screen@version` = `1`
- `screen@{http://www.w3.org/2001/XMLSchema-instance}noNamespaceSchemaLocation` = `screen.xsd`
- `screen@ìsPresets` = `true`
- `screen/footer@text` = `Reorder Presets`
- `screen/footer@type` = `reorder`
- `screen/footer/action@URI` = `/reorder-presets?url=%2FPresets%2Fedit%3Fprid%3D1`
- `screen/footer/action@refreshScreen` = `true`
- `screen/footer/action@title` = `Reorder Presets`
- `screen/footer/action@type` = `deep-link`
- `screen/list/item@counter` = `1`
- `screen/list/item@image` = `/Artwork?service=Tidal&playlistimage=f8601f52-6d31-43bd-97a7`
- `screen/list/item@solidBackground` = `true`
- `screen/list/item@title` = `Sunday Chill Mix: Ministry of Sound`
- `screen/list/item/action@URI` = `/Preset?id=1`
- `screen/list/item/action@haptic` = `true`
- `screen/list/item/action@type` = `player-link`
- `screen/list/item/contextMenu@URI` = `/ui/ContextMenu?id=1&image=%2FArtwork%3Fservice%3DTidal%26pl`
- `screen/list/item/contextMenu@resultType` = `contextMenu`
- `screen/list/item/contextMenu@title` = `Sunday Chill Mix: Ministry of Sound`
- `screen/list/item/contextMenu@type` = `browse`
- `screen/menuAction@type` = `add`
- `screen/menuAction/action@URI` = `/add-preset`
- `screen/menuAction/action@refreshScreen` = `true`
- `screen/menuAction/action@type` = `deep-link`
- `screen/refreshOnStatusChange@key` = `prid`
- `screen/refreshOnStatusChange@value` = `1`

</details>
