# BluOS probe run -- results

| | |
|---|---|
| harness | bluos-probe.py 1.6 |
| started | 2026-09-11T22:03:57 |
| duration | 111.8 s |
| timezone declared to devices | `Europe/Copenhagen` (`X-Sovi-Tz`) |
| harness host clock | CEST (UTC+0200) |
| probes | 450 |
| verdicts | INFO 357, OK 86, UNEXPECTED 7 |
| safety classes run | read, probe |

`OK` means the result matched what the specification predicts.
`UNEXPECTED` means it did not -- those rows are the interesting ones.
`INFO` means no prediction was recorded, so the capture is the result.

## Players

| label | name | model | firmware | schema | topology |
|---|---|---|---|---|---|
| A | Stue | Bluesound N132 | 4.16.22 | 34 | standalone |
| B | Kontor | Bluesound N130 | 4.16.22 | 34 | standalone |
| C | Køkken | Bluesound N132 | 4.16.22 | 34 | standalone |
| D | Soveværelse | Bluesound N110 | 4.16.22 | 34 | standalone |

## Results that did not match the specification

| id | player | request | status | expected | note |
|---|---|---|---|---|---|
| `011-env` | A | `:11000 /GetUnpairedSlaves` | 400 | `status=200` | pairable speakers |
| `022-env` | B | `:11000 /GetUnpairedSlaves` | 400 | `status=200` | pairable speakers |
| `033-env` | C | `:11000 /GetUnpairedSlaves` | 400 | `status=200` | pairable speakers |
| `043-env` | D | `:11000 /BTDevices?timeout=1` | 503 | `status=200` | bluetooth device list |
| `044-env` | D | `:11000 /GetUnpairedSlaves` | 400 | `status=200` | pairable speakers |
| `137-ports` | A | `:11000 /ExternalSource` | 200 | `status=404` | does this path exist at all? |
| `434-discovery` | - | `:0 (analysis)` | - | `` | no player answered a UNICAST LSDP query of either form |

## Claim checks

Every probe aimed at a marked claim in the specification, so the
register in section 17 can be updated from one table. `root` and
`bytes` are usually enough to tell a real answer from a 404.

| id | claim | verdict | player | port | request | status | root | note |
|---|---|---|---|---|---|---|---|---|
| `009-env` | `C-15-alarms-bitmask` | INCONCLUSIVE | A | 11000 | `/Alarms` | 200 | `alarms` | alarm list; days bitmask claim (times are in Europe/Copenhagen) |
| `020-env` | `C-15-alarms-bitmask` | INCONCLUSIVE | B | 11000 | `/Alarms` | 200 | `alarms` | alarm list; days bitmask claim (times are in Europe/Copenhagen) |
| `031-env` | `C-15-alarms-bitmask` | INCONCLUSIVE | C | 11000 | `/Alarms` | 200 | `alarms` | alarm list; days bitmask claim (times are in Europe/Copenhagen) |
| `042-env` | `C-15-alarms-bitmask` | CONFIRMED | D | 11000 | `/Alarms` | 200 | `alarms` | alarm list; days bitmask claim (times are in Europe/Copenhagen) |
| `137-ports` | `C-24-player-enumeration` | CONFIRMED | A | 11000 | `/ExternalSource` | 200 | `error` | does this path exist at all? |
| `138-ports` | `C-24-player-enumeration` | DISCONFIRMED | A | 11000 | `/Players` | 404 | `` | does this path exist at all? |
| `139-ports` | `C-24-player-enumeration` | DISCONFIRMED | A | 11000 | `/Devices` | 404 | `` | does this path exist at all? |
| `140-ports` | `C-24-player-enumeration` | DISCONFIRMED | A | 11000 | `/Zones` | 404 | `` | does this path exist at all? |
| `141-ports` | `C-24-player-enumeration` | DISCONFIRMED | A | 11000 | `/Groups` | 404 | `` | does this path exist at all? |
| `195-claims` | `C-01-diagnostics-80` | CONFIRMED | A | 80 | `/diagnostics` | 200 | `html` | [T blutui-rs] /diagnostics on port 80 |
| `196-claims` | `C-02-diagnostics-11000` | CONFIRMED | A | 11000 | `/diagnostics` | 404 | `` | /diagnostics on 11000 (expected 404) |
| `197-claims` | `C-01-diagnostics-80` | CONFIRMED | B | 80 | `/diagnostics` | 200 | `html` | [T blutui-rs] /diagnostics on port 80 |
| `198-claims` | `C-02-diagnostics-11000` | CONFIRMED | B | 11000 | `/diagnostics` | 404 | `` | /diagnostics on 11000 (expected 404) |
| `199-claims` | `C-03-audiomodes-read` | INCONCLUSIVE | A | 11000 | `/audiomodes` | 200 | `` | [T BluShell] bare GET /audiomodes returns <audiomode> |
| `200-claims` | `C-03-audiomodes-read` | INCONCLUSIVE | B | 11000 | `/audiomodes` | 200 | `` | [T BluShell] bare GET /audiomodes returns <audiomode> |
| `201-claims` | `C-06-getsettings` | DISCONFIRMED | A | 11000 | `/GetSettings` | 404 | `` | [V] /GetSettings absent on current firmware |
| `203-claims` | `C-06-getsettings` | DISCONFIRMED | B | 11000 | `/GetSettings` | 404 | `` | [V] /GetSettings absent on current firmware |
| `206-claims` | `C-16-shares-11000` | DISCONFIRMED | A | 11000 | `/Shares` | 404 | `` | has /Shares migrated to 11000? |
| `208-claims` | `C-16-shares-11000` | DISCONFIRMED | B | 11000 | `/Shares` | 404 | `` | has /Shares migrated to 11000? |
| `209-claims` | `C-04-proxytoslave` | CONFIRMED | A | 11000 | `/proxyToSlave` | 400 | `` | [T blutui-rs] does /proxyToSlave exist? (no params, nothing relayed) |
| `210-claims` | `C-05-sync-legacy` | DISCONFIRMED | A | 11000 | `/Sync` | 404 | `` | [T bluos-dashboard] does the legacy /Sync path exist? (no params) |
| `211-claims` | `C-11-radio-attrs` | DISCONFIRMED | A | 11000 | `/RadioPresets?service=Airable` | 200 | `radiotime` | [T Blu4Net/BluShell] radio item attributes for Airable |
| `212-claims` | `C-12-radio-totalcount` | DISCONFIRMED | A | 11000 | `/RadioBrowse?service=Airable` | 200 | `radiotime` | [T] total_count / key / is_active on <radiotime> items |
| `213-claims` | `C-11-radio-attrs` | INCONCLUSIVE | A | 11000 | `/RadioPresets?service=Capture` | 404 | `` | [T Blu4Net/BluShell] radio item attributes for Capture |
| `214-claims` | `C-12-radio-totalcount` | DISCONFIRMED | A | 11000 | `/RadioBrowse?service=Capture` | 200 | `radiotime` | [T] total_count / key / is_active on <radiotime> items |
| `215-claims` | `C-11-radio-attrs` | DISCONFIRMED | A | 11000 | `/RadioPresets?service=RadioParadise` | 200 | `radiotime` | [T Blu4Net/BluShell] radio item attributes for RadioParadise |
| `216-claims` | `C-12-radio-totalcount` | DISCONFIRMED | A | 11000 | `/RadioBrowse?service=RadioParadise` | 200 | `radiotime` | [T] total_count / key / is_active on <radiotime> items |
| `217-claims` | `C-11-radio-attrs` | DISCONFIRMED | A | 11000 | `/RadioPresets?service=TuneIn` | 200 | `error` | [T Blu4Net/BluShell] radio item attributes for TuneIn |
| `218-claims` | `C-12-radio-totalcount` | DISCONFIRMED | A | 11000 | `/RadioBrowse?service=TuneIn` | 200 | `radiotime` | [T] total_count / key / is_active on <radiotime> items |
| `219-claims` | `C-13-search-containers` | DISCONFIRMED | A | 11000 | `/Search?service=LocalMusic&expr=a` | 404 | `` | [T BluShell] /Search container shape for LocalMusic |
| `220-claims` | `C-13-search-containers` | DISCONFIRMED | A | 11000 | `/Search?service=Tidal&expr=a` | 404 | `` | [T BluShell] /Search container shape for Tidal |
| `221-claims` | `C-17-is-preset` | DISCONFIRMED | A | 11000 | `/Status` | 200 | `status` | [T Blu4Net] <is_preset>/<preset_name> in /Status (read-only; recall itself is a round-2 test) |
| `223-inputs` | `C-11-radio-attrs` | DISCONFIRMED | A | 11000 | `/RadioBrowse?service=Capture` | 200 | `radiotime` | the Capture service: the input list the app builds its picker from |
| `230-inputs` | `C-11-radio-attrs` | DISCONFIRMED | B | 11000 | `/RadioBrowse?service=Capture` | 200 | `radiotime` | the Capture service: the input list the app builds its picker from |
| `237-inputs` | `C-11-radio-attrs` | DISCONFIRMED | C | 11000 | `/RadioBrowse?service=Capture` | 200 | `radiotime` | the Capture service: the input list the app builds its picker from |
| `244-inputs` | `C-11-radio-attrs` | DISCONFIRMED | D | 11000 | `/RadioBrowse?service=Capture` | 200 | `radiotime` | the Capture service: the input list the app builds its picker from |
| `250-artwork` | `C-07-artwork-cors` | CONFIRMED | A | 11000 | `/Artwork?service=Tidal&amp;songid=Tidal%3A48513985` | 200 | `artwork` | [T BluShepherd 2016] artwork headers: CORS? ETag? Cache-Control? |
| `251-artwork` | `C-08-artwork-noetag` | CONFIRMED | A | 11000 | `/Artwork?service=Tidal&amp;songid=Tidal%3A48513985` | 200 | `` | [T BluShepherd 2016] artwork sends no ETag and no Last-Modified |
| `255-artwork` | `C-09-artwork-nonefound` | INCONCLUSIVE | A | 11000 | `/Artwork?service=LocalMusic&fn=%2Fdoes%2Fnot%2Fexist.flac` | 301 | `a` | [T BluShell] <artwork>none found</artwork> -- record the Content-Type |
| `257-artwork` | `C-10-artwork-byname` | INCONCLUSIVE | A | 11000 | `/Artwork?service=LocalMusic&album=Heaven&artist=Alex%20Adair` | 301 | `a` | [T 2015/2016] /Artwork?album=&artist= by name, using a real album |
| `372-browse` | `C-22-page-cap-50` | CONFIRMED | A | 11000 | `/Songs?service=Tidal&category=FAVOURITES&start=0&end=999` | 200 | `songs` | [V] is browse paging capped at 50? |
| `393-browse` | `C-20-browse-sid` | DISCONFIRMED | A | 11000 | `/Browse?sid=0` | 200 | `browse` | does /Browse accept a bogus sid? |
| `423-settings` | `C-23-11001-settings-only` | CONFIRMED | A | 11001 | `/Status` | 404 | `` | does 11001 serve anything but settings? |
| `424-settings` | `C-23-11001-settings-only` | CONFIRMED | A | 11001 | `/SyncStatus` | 404 | `` | does 11001 serve anything but settings? |
| `425-settings` | `C-23-11001-settings-only` | CONFIRMED | A | 11001 | `/Shares` | 404 | `` | does 11001 serve anything but settings? |
| `426-settings` | `C-23-11001-settings-only` | CONFIRMED | A | 11001 | `/ui/Configuration` | 404 | `` | does 11001 serve anything but settings? |
| `427-settings` | `C-23-11001-settings-only` | CONFIRMED | A | 11001 | `/Services` | 404 | `` | does 11001 serve anything but settings? |
| `431-discovery` | `C-19-lsdp-unicast-R` | INCONCLUSIVE | - | 11430 | `LSDP R unicast to player A (T-26)` | - | `` | LSDP R unicast to player A (T-26) |
| `433-discovery` | `C-19-lsdp-unicast-R` | INCONCLUSIVE | - | 11430 | `LSDP R unicast to player B (T-26)` | - | `` | LSDP R unicast to player B (T-26) |

## suite: artwork

| id | v | player | port | request | status | ms | type | root | bytes | note |
|---|---|---|---|---|---|---|---|---|---|---|
| `250-artwork` | I | A | 11000 | `/Artwork?service=Tidal&amp;songid=Tidal%3A48513985` | 200 | 10 | xml | `artwork` | 68 | [T BluShepherd 2016] artwork headers: CORS? ETag? Cache-Control? |
| `251-artwork` | I | A | 11000 | `HEAD /Artwork?service=Tidal&amp;songid=Tidal%3A48513985` | 200 | 9 | none | `` | 0 | [T BluShepherd 2016] artwork sends no ETag and no Last-Modified |
| `252-artwork` | I | A | 11000 | `/Artwork?service=Tidal&amp;songid=Tidal%3A48513985&followRedirects=1` | 200 | 10 | xml | `artwork` | 68 | followRedirects=1 as the spec advises |
| `253-artwork` | I | A | 11000 | `HEAD /Artwork?service=Tidal&amp;songid=Tidal%3A48513985` | 200 | 14 | none | `` | 0 | HEAD on artwork (cheap validator check) |
| `254-artwork` | I | A | 11000 | `/Artwork?service=Tidal&amp;songid=Tidal%3A48513985` | 200 | 9 | xml | `artwork` | 68 | artwork with an Origin header: is CORS still open? |
| `255-artwork` | I | A | 11000 | `/Artwork?service=LocalMusic&fn=%2Fdoes%2Fnot%2Fexist.flac` | 301 | 9 | xml | `a` | 130 | [T BluShell] <artwork>none found</artwork> -- record the Content-Type |
| `256-artwork` | I | A | 11000 | `/Artwork?service=NoSuchService&albumid=0` | 200 | 9 | xml | `artwork` | 68 | artwork for an unknown service |
| `257-artwork` | I | A | 11000 | `/Artwork?service=LocalMusic&album=Heaven&artist=Alex%20Adair` | 301 | 9 | xml | `a` | 135 | [T 2015/2016] /Artwork?album=&artist= by name, using a real album |
| `258-artwork` | I | A | 11000 | `/Artwork?service=LocalMusic&album=NoSuchAlbum&artist=NoSuchArtist` | 301 | 9 | xml | `a` | 142 | by-name artwork for an album that does not exist, as a control |

## suite: browse

| id | v | player | port | request | status | ms | type | root | bytes | note |
|---|---|---|---|---|---|---|---|---|---|---|
| `259-browse` | I | A | 11000 | `/Browse` | 200 | 12 | xml | `browse` | 983 | typed browse entry point |
| `260-browse` | I | A | 11000 | `/Sources` | 404 | 31 | text | `` | 19 | typed browse entry point |
| `261-browse` | I | A | 11000 | `/Playlists` | 200 | 9 | xml | `playlists` | 78 | typed browse entry point |
| `262-browse` | I | A | 11000 | `/RadioPresets` | 404 | 9 | text | `` | 1 | typed browse entry point |
| `263-browse` | I | A | 11000 | `/Albums?service=Airable` | 200 | 11 | xml | `error` | 121 | typed entry point /Albums for service Airable |
| `264-browse` | I | A | 11000 | `/Artists?service=Airable` | 200 | 9 | xml | `error` | 121 | typed entry point /Artists for service Airable |
| `265-browse` | I | A | 11000 | `/Genres?service=Airable` | 200 | 8 | xml | `error` | 121 | typed entry point /Genres for service Airable |
| `266-browse` | I | A | 11000 | `/Composers?service=Airable` | 200 | 8 | xml | `error` | 121 | typed entry point /Composers for service Airable |
| `267-browse` | I | A | 11000 | `/Folders?service=Airable` | 404 | 8 | text | `` | 8 | typed entry point /Folders for service Airable |
| `268-browse` | I | A | 11000 | `/Playlists?service=Airable` | 200 | 8 | xml | `error` | 121 | typed entry point /Playlists for service Airable |
| `269-browse` | I | A | 11000 | `/Albums?service=Alarms` | 404 | 10 | text | `` | 7 | typed entry point /Albums for service Alarms |
| `270-browse` | I | A | 11000 | `/Artists?service=Alarms` | 404 | 8 | text | `` | 7 | typed entry point /Artists for service Alarms |
| `271-browse` | I | A | 11000 | `/Genres?service=Alarms` | 404 | 11 | text | `` | 7 | typed entry point /Genres for service Alarms |
| `272-browse` | I | A | 11000 | `/Composers?service=Alarms` | 404 | 7 | text | `` | 7 | typed entry point /Composers for service Alarms |
| `273-browse` | I | A | 11000 | `/Folders?service=Alarms` | 404 | 8 | text | `` | 7 | typed entry point /Folders for service Alarms |
| `274-browse` | I | A | 11000 | `/Playlists?service=Alarms` | 404 | 8 | text | `` | 7 | typed entry point /Playlists for service Alarms |
| `275-browse` | I | A | 11000 | `/Albums?service=BluOS` | 404 | 7 | text | `` | 6 | typed entry point /Albums for service BluOS |
| `276-browse` | I | A | 11000 | `/Artists?service=BluOS` | 404 | 8 | text | `` | 6 | typed entry point /Artists for service BluOS |
| `277-browse` | I | A | 11000 | `/Genres?service=BluOS` | 404 | 11 | text | `` | 6 | typed entry point /Genres for service BluOS |
| `278-browse` | I | A | 11000 | `/Composers?service=BluOS` | 404 | 9 | text | `` | 6 | typed entry point /Composers for service BluOS |
| `279-browse` | I | A | 11000 | `/Folders?service=BluOS` | 404 | 8 | text | `` | 6 | typed entry point /Folders for service BluOS |
| `280-browse` | I | A | 11000 | `/Playlists?service=BluOS` | 200 | 8 | xml | `playlists` | 78 | typed entry point /Playlists for service BluOS |
| `281-browse` | I | A | 11000 | `/Albums?service=Capture` | 404 | 8 | text | `` | 8 | typed entry point /Albums for service Capture |
| `282-browse` | I | A | 11000 | `/Artists?service=Capture` | 404 | 10 | text | `` | 8 | typed entry point /Artists for service Capture |
| `283-browse` | I | A | 11000 | `/Genres?service=Capture` | 404 | 9 | text | `` | 8 | typed entry point /Genres for service Capture |
| `284-browse` | I | A | 11000 | `/Composers?service=Capture` | 404 | 9 | text | `` | 8 | typed entry point /Composers for service Capture |
| `285-browse` | I | A | 11000 | `/Folders?service=Capture` | 404 | 10 | text | `` | 8 | typed entry point /Folders for service Capture |
| `286-browse` | I | A | 11000 | `/Playlists?service=Capture` | 404 | 9 | text | `` | 8 | typed entry point /Playlists for service Capture |
| `287-browse` | I | A | 11000 | `/Albums?service=LocalMusic` | 302 | 9 | xml | `a` | 83 | typed entry point /Albums for service LocalMusic |
| `288-browse` | I | A | 11000 | `/Artists?service=LocalMusic` | 302 | 8 | xml | `a` | 84 | typed entry point /Artists for service LocalMusic |
| `289-browse` | I | A | 11000 | `/Genres?service=LocalMusic` | 302 | 9 | xml | `a` | 83 | typed entry point /Genres for service LocalMusic |
| `290-browse` | I | A | 11000 | `/Composers?service=LocalMusic` | 302 | 9 | xml | `a` | 86 | typed entry point /Composers for service LocalMusic |
| `291-browse` | I | A | 11000 | `/Folders?service=LocalMusic` | 302 | 9 | xml | `a` | 84 | typed entry point /Folders for service LocalMusic |
| `292-browse` | I | A | 11000 | `/Playlists?service=LocalMusic` | 200 | 8 | xml | `playlists` | 78 | typed entry point /Playlists for service LocalMusic |
| `293-browse` | I | A | 11000 | `/Albums?service=RadioParadise` | 200 | 9 | xml | `error` | 127 | typed entry point /Albums for service RadioParadise |
| `294-browse` | I | A | 11000 | `/Artists?service=RadioParadise` | 200 | 9 | xml | `error` | 127 | typed entry point /Artists for service RadioParadise |
| `295-browse` | I | A | 11000 | `/Genres?service=RadioParadise` | 200 | 9 | xml | `error` | 127 | typed entry point /Genres for service RadioParadise |
| `296-browse` | I | A | 11000 | `/Composers?service=RadioParadise` | 200 | 9 | xml | `error` | 127 | typed entry point /Composers for service RadioParadise |
| `297-browse` | I | A | 11000 | `/Folders?service=RadioParadise` | 404 | 12 | text | `` | 14 | typed entry point /Folders for service RadioParadise |
| `298-browse` | I | A | 11000 | `/Playlists?service=RadioParadise` | 200 | 9 | xml | `error` | 127 | typed entry point /Playlists for service RadioParadise |
| `299-browse` | I | A | 11000 | `/Albums?service=Tidal` | 200 | 1001 | xml | `error` | 119 | typed entry point /Albums for service Tidal |
| `300-browse` | I | A | 11000 | `/Artists?service=Tidal` | 200 | 612 | xml | `error` | 119 | typed entry point /Artists for service Tidal |
| `301-browse` | I | A | 11000 | `/Genres?service=Tidal` | 200 | 145 | xml | `genres` | 2748 | typed entry point /Genres for service Tidal |
| `302-browse` | I | A | 11000 | `/Composers?service=Tidal` | 200 | 24 | xml | `error` | 119 | typed entry point /Composers for service Tidal |
| `303-browse` | I | A | 11000 | `/Folders?service=Tidal` | 404 | 9 | text | `` | 6 | typed entry point /Folders for service Tidal |
| `304-browse` | I | A | 11000 | `/Playlists?service=Tidal` | 200 | 413 | xml | `playlists` | 6425 | typed entry point /Playlists for service Tidal |
| `305-browse` | I | A | 11000 | `/Albums?service=TuneIn` | 200 | 12 | xml | `error` | 120 | typed entry point /Albums for service TuneIn |
| `306-browse` | I | A | 11000 | `/Artists?service=TuneIn` | 200 | 6 | xml | `error` | 120 | typed entry point /Artists for service TuneIn |
| `307-browse` | I | A | 11000 | `/Genres?service=TuneIn` | 200 | 7 | xml | `error` | 120 | typed entry point /Genres for service TuneIn |
| `308-browse` | I | A | 11000 | `/Composers?service=TuneIn` | 200 | 7 | xml | `error` | 120 | typed entry point /Composers for service TuneIn |
| `309-browse` | I | A | 11000 | `/Folders?service=TuneIn` | 404 | 8 | text | `` | 7 | typed entry point /Folders for service TuneIn |
| `310-browse` | I | A | 11000 | `/Playlists?service=TuneIn` | 200 | 8 | xml | `error` | 120 | typed entry point /Playlists for service TuneIn |
| `311-browse` | I | A | 11000 | `/Browse` | 200 | 9 | xml | `browse` | 983 | browse crawl depth 0 |
| `312-browse` | I | A | 11000 | `/Browse?key=BluOS%3A` | 200 | 8 | xml | `browse` | 129 | browse crawl depth 1 |
| `313-browse` | I | A | 11000 | `/Browse?key=LocalMusic%3A` | 200 | 8 | xml | `browse` | 996 | browse crawl depth 1 |
| `314-browse` | I | A | 11000 | `/Browse?key=Airable%3A` | 200 | 55 | xml | `browse` | 1290 | browse crawl depth 1 |
| `315-browse` | I | A | 11000 | `/Browse?key=RadioParadise%3A` | 200 | 718 | xml | `browse` | 7052 | browse crawl depth 1 |
| `316-browse` | I | A | 11000 | `/Browse?key=Tidal%3A` | 200 | 11 | xml | `browse` | 784 | browse crawl depth 1 |
| `317-browse` | I | A | 11000 | `/Browse?key=TuneIn%3A` | 200 | 374 | xml | `browse` | 4827 | browse crawl depth 1 |
| `318-browse` | I | A | 11000 | `/Browse?key=LocalMusic%3AbySection%3AArtist%2F%252Flibrary%252Fv1%252FArtists%253Fservice%3DLocalMusic` | 200 | 14 | xml | `browse` | 2971 | browse crawl depth 2 |
| `319-browse` | I | A | 11000 | `/Browse?key=LocalMusic%3AbySection%3AAlbum%2F%252Flibrary%252Fv1%252FAlbums%253Fservice%3DLocalMusic` | 200 | 25 | xml | `browse` | 2784 | browse crawl depth 2 |
| `320-browse` | I | A | 11000 | `/Browse?key=LocalMusic%3AbySection%3ASong%2F%252Flibrary%252Fv1%252FSongs%253Fall%3D1%26service%3DLocalMusic` | 200 | 16 | xml | `browse` | 4403 | browse crawl depth 2 |
| `321-browse` | I | A | 11000 | `/Browse?key=LocalMusic%3AGG%2FGenres` | 200 | 27 | xml | `browse` | 1808 | browse crawl depth 2 |
| `322-browse` | I | A | 11000 | `/Browse?key=LocalMusic%3APlaylist%2F%252Flibrary%252Fv1%252FPlaylists%253Fimported%3D1%26service%3DLocalMusic` | 200 | 10 | xml | `browse` | 163 | browse crawl depth 2 |
| `323-browse` | I | A | 11000 | `/Browse?key=LocalMusic%3AbySection%3AComposer%2F%252Flibrary%252Fv1%252FComposers%253Fservice%3DLocalMusic` | 200 | 15 | xml | `browse` | 3690 | browse crawl depth 2 |
| `324-browse` | I | A | 11000 | `/Browse?key=Airable%3ABrowseMenu%2F%252FRadioBrowse%253Fservice%3DAirable%26url%3Dhttps%25253A%25252F%25252F7818664144.airable.io%25252Fradio%25252Fstations%25252Fcharts` | 200 | 100 | xml | `browse` | 18327 | browse crawl depth 2 |
| `325-browse` | I | A | 11000 | `/Browse?key=Airable%3ABrowseMenu%2F%252FRadioBrowse%253Fservice%3DAirable%26url%3Dhttps%25253A%25252F%25252F7818664144.airable.io%25252Fradio%25252Fplace%25252F4147028435952962` | 200 | 79 | xml | `browse` | 1900 | browse crawl depth 2 |
| `326-browse` | I | A | 11000 | `/Browse?key=Airable%3ABrowseMenu%2F%252FRadioBrowse%253Fservice%3DAirable%26url%3Dhttps%25253A%25252F%25252F7818664144.airable.io%25252Fradio%25252Flocal` | 200 | 639 | xml | `browse` | 17559 | browse crawl depth 2 |
| `327-browse` | I | A | 11000 | `/Browse?key=Airable%3ABrowseMenu%2F%252FRadioBrowse%253Fservice%3DAirable%26url%3Dhttps%25253A%25252F%25252F7818664144.airable.io%25252Fradio%25252Fpodcasts` | 200 | 279 | xml | `browse` | 2043 | browse crawl depth 2 |
| `328-browse` | I | A | 11000 | `/Browse?key=Airable%3ABrowseMenu%2F%252FRadioBrowse%253Fservice%3DAirable%26url%3Dhttps%25253A%25252F%25252F7818664144.airable.io%25252Fradio%25252Fgenres` | 200 | 227 | xml | `browse` | 4308 | browse crawl depth 2 |
| `329-browse` | I | A | 11000 | `/Browse?key=Airable%3ABrowseMenu%2F%252FRadioBrowse%253Fservice%3DAirable%26url%3Dhttps%25253A%25252F%25252F7818664144.airable.io%25252Fradio%25252Fplaces` | 200 | 323 | xml | `browse` | 5770 | browse crawl depth 2 |
| `330-browse` | I | A | 11000 | `/Browse?key=Tidal%3AMG%2FTidal-New` | 200 | 10 | xml | `browse` | 503 | browse crawl depth 2 |
| `331-browse` | I | A | 11000 | `/Browse?key=Tidal%3AMG%2FTidal-TIDAL%2520Rising` | 200 | 9 | xml | `browse` | 379 | browse crawl depth 2 |
| `332-browse` | I | A | 11000 | `/Browse?key=Tidal%3AMG%2FTidal-Recommendations` | 200 | 9 | xml | `browse` | 551 | browse crawl depth 2 |
| `333-browse` | I | A | 11000 | `/Browse?key=Tidal%3AMG%2FTidal-Popular` | 200 | 10 | xml | `browse` | 389 | browse crawl depth 2 |
| `334-browse` | I | A | 11000 | `/Browse?key=Tidal%3AMG%2FTidal-Dansk` | 200 | 11 | xml | `browse` | 497 | browse crawl depth 2 |
| `335-browse` | I | A | 11000 | `/Browse?key=Tidal%3AGG%2FMoods` | 200 | 140 | xml | `browse` | 998 | browse crawl depth 2 |
| `336-browse` | I | A | 11000 | `/Browse?key=TuneIn%3ABrowseMenu%2F%252FRadioBrowse%253Fservice%3DTuneIn%26url%3Dhttps%25253A%25252F%25252Fapi.radiotime.com%25252Fcategories%25252Fhome%25253Fserial%25253DC0%2525253a74%2525253a2B%2525253aFF%2525253a2C%2525253a1E%252526partnerId%25253D8OeGua6y%252526version%25253D2%252526formats%25253Dwma%2525252cmp3%2525252caac%2525252cogg%2525252chls%252526viewModel%25253DFalse%252526itemToken%25253DBggIAAEAAQABAAEAAQEAAQgAAA` | 200 | 968 | xml | `browse` | 48572 | browse crawl depth 2 |
| `337-browse` | I | A | 11000 | `/Browse?key=TuneIn%3ABrowseMenu%2F%252FRadioBrowse%253Fservice%3DTuneIn%26url%3Dpresets` | 200 | 405 | xml | `browse` | 161 | browse crawl depth 2 |
| `338-browse` | I | A | 11000 | `/Browse?key=TuneIn%3ABrowseMenu%2F%252FRadioBrowse%253Fservice%3DTuneIn%26url%3Dhttps%25253A%25252F%25252Fapi.radiotime.com%25252Fcategories%25252Flocal%25253Fserial%25253DC0%2525253a74%2525253a2B%2525253aFF%2525253a2C%2525253a1E%252526partnerId%25253D8OeGua6y%252526version%25253D2%252526formats%25253Dwma%2525252cmp3%2525252caac%2525252cogg%2525252chls%252526viewModel%25253DFalse%252526itemToken%25253DBggIAAMAAwABAAEAAQEAAQgAAA` | 200 | 640 | xml | `browse` | 39297 | browse crawl depth 2 |
| `339-browse` | I | A | 11000 | `/Browse?key=TuneIn%3ABrowseMenu%2F%252FRadioBrowse%253Fservice%3DTuneIn%26url%3Dhttps%25253A%25252F%25252Fapi.radiotime.com%25252Fcategories%25252Fsports%25253Fserial%25253DC0%2525253a74%2525253a2B%2525253aFF%2525253a2C%2525253a1E%252526partnerId%25253D8OeGua6y%252526version%25253D2%252526formats%25253Dwma%2525252cmp3%2525252caac%2525252cogg%2525252chls%252526viewModel%25253DFalse%252526itemToken%25253DBggIAAQABAABAAEAAQEAAQgAAA` | 200 | 1062 | xml | `browse` | 71193 | browse crawl depth 2 |
| `340-browse` | I | A | 11000 | `/Browse?key=TuneIn%3ABrowseMenu%2F%252FRadioBrowse%253Fservice%3DTuneIn%26url%3Dhttps%25253A%25252F%25252Fapi.radiotime.com%25252Fcategories%020000000075%25253Fserial%25253DC0%2525253a74%2525253a2B%2525253aFF%2525253a2C%2525253a1E%252526partnerId%25253D8OeGua6y%252526version%25253D2%252526formats%25253Dwma%2525252cmp3%2525252caac%2525252cogg%2525252chls%252526viewModel%25253DFalse%252526itemToken%25253DBggIAAUABQABAAEAAQEAAQgAAA` | 200 | 465 | xml | `browse` | 4115 | browse crawl depth 2 |
| `341-browse` | I | A | 11000 | `/Browse?key=TuneIn%3ABrowseMenu%2F%252FRadioBrowse%253Fservice%3DTuneIn%26url%3Dhttps%25253A%25252F%25252Fapi.radiotime.com%25252Fcategories%25252Fc100000088%25253Fserial%25253DC0%2525253a74%2525253a2B%2525253aFF%2525253a2C%2525253a1E%252526partnerId%25253D8OeGua6y%252526version%25253D2%252526formats%25253Dwma%2525252cmp3%2525252caac%2525252cogg%2525252chls%252526viewModel%25253DFalse%252526itemToken%25253DBggIAAYABgABAAEAAQEAAQgAAA` | 200 | 583 | xml | `browse` | 66394 | browse crawl depth 2 |
| `342-browse` | I | A | 11000 | `/Browse?key=LocalMusic%3AS%3AArtist%2F%252Flibrary%252Fv1%252FArtists%253Fservice%3DLocalMusic%26limit%3D50%26section%3DA` | 200 | 12 | xml | `browse` | 771 | browse crawl depth 3 |
| `343-browse` | I | A | 11000 | `/Browse?key=LocalMusic%3AS%3AArtist%2F%252Flibrary%252Fv1%252FArtists%253Fservice%3DLocalMusic%26limit%3D50%26section%3DB` | 200 | 10 | xml | `browse` | 699 | browse crawl depth 3 |
| `344-browse` | I | A | 11000 | `/Browse?key=LocalMusic%3AS%3AArtist%2F%252Flibrary%252Fv1%252FArtists%253Fservice%3DLocalMusic%26limit%3D50%26section%3DC` | 200 | 23 | xml | `browse` | 321 | browse crawl depth 3 |
| `345-browse` | I | A | 11000 | `/Browse?key=LocalMusic%3AS%3AArtist%2F%252Flibrary%252Fv1%252FArtists%253Fservice%3DLocalMusic%26limit%3D50%26section%3DD` | 200 | 10 | xml | `browse` | 345 | browse crawl depth 3 |
| `346-browse` | I | A | 11000 | `/Browse?key=LocalMusic%3AS%3AArtist%2F%252Flibrary%252Fv1%252FArtists%253Fservice%3DLocalMusic%26limit%3D50%26section%3DE` | 200 | 15 | xml | `browse` | 519 | browse crawl depth 3 |
| `347-browse` | I | A | 11000 | `/Browse?key=LocalMusic%3AS%3AArtist%2F%252Flibrary%252Fv1%252FArtists%253Fservice%3DLocalMusic%26limit%3D50%26section%3DG` | 200 | 11 | xml | `browse` | 336 | browse crawl depth 3 |
| `348-browse` | I | A | 11000 | `/Browse?key=LocalMusic%3AS%3AAlbum%2F%252Flibrary%252Fv1%252FAlbums%253Fservice%3DLocalMusic%26limit%3D50%26section%3D%2523` | 200 | 19 | xml | `browse` | 538 | browse crawl depth 3 |
| `349-browse` | I | A | 11000 | `/Browse?key=LocalMusic%3AS%3AAlbum%2F%252Flibrary%252Fv1%252FAlbums%253Fservice%3DLocalMusic%26limit%3D50%26section%3DA` | 200 | 16 | xml | `browse` | 3043 | browse crawl depth 3 |
| `350-browse` | I | A | 11000 | `/Browse?key=LocalMusic%3AS%3AAlbum%2F%252Flibrary%252Fv1%252FAlbums%253Fservice%3DLocalMusic%26limit%3D50%26section%3DB` | 200 | 12 | xml | `browse` | 3006 | browse crawl depth 3 |
| `351-browse` | I | A | 11000 | `/Browse?key=LocalMusic%3AS%3AAlbum%2F%252Flibrary%252Fv1%252FAlbums%253Fservice%3DLocalMusic%26limit%3D50%26section%3DD` | 200 | 12 | xml | `browse` | 718 | browse crawl depth 3 |
| `352-browse` | I | A | 11000 | `/Browse?key=LocalMusic%3AS%3AAlbum%2F%252Flibrary%252Fv1%252FAlbums%253Fservice%3DLocalMusic%26limit%3D50%26section%3DE` | 200 | 11 | xml | `browse` | 1166 | browse crawl depth 3 |
| `353-browse` | I | A | 11000 | `/Browse?key=LocalMusic%3AS%3AAlbum%2F%252Flibrary%252Fv1%252FAlbums%253Fservice%3DLocalMusic%26limit%3D50%26section%3DG` | 200 | 15 | xml | `browse` | 2686 | browse crawl depth 3 |
| `354-browse` | I | A | 11000 | `/Browse?key=LocalMusic%3AS%3ASong%2F%252Flibrary%252Fv1%252FSongs%253Fall%3D1%26service%3DLocalMusic%26limit%3D50%26section%3D%2523` | 200 | 9 | xml | `browse` | 160 | browse crawl depth 3 |
| `355-browse` | I | A | 11000 | `/Browse?key=LocalMusic%3AS%3ASong%2F%252Flibrary%252Fv1%252FSongs%253Fall%3D1%26service%3DLocalMusic%26limit%3D50%26section%3DA` | 200 | 33 | xml | `browse` | 30931 | browse crawl depth 3 |
| `356-browse` | I | A | 11000 | `/Browse?key=LocalMusic%3AS%3ASong%2F%252Flibrary%252Fv1%252FSongs%253Fall%3D1%26service%3DLocalMusic%26limit%3D50%26section%3DB` | 200 | 35 | xml | `browse` | 31880 | browse crawl depth 3 |
| `357-browse` | I | A | 11000 | `/Browse?key=LocalMusic%3AS%3ASong%2F%252Flibrary%252Fv1%252FSongs%253Fall%3D1%26service%3DLocalMusic%26limit%3D50%26section%3DC` | 200 | 35 | xml | `browse` | 31512 | browse crawl depth 3 |
| `358-browse` | I | A | 11000 | `/Browse?key=LocalMusic%3AS%3ASong%2F%252Flibrary%252Fv1%252FSongs%253Fall%3D1%26service%3DLocalMusic%26limit%3D50%26section%3DD` | 200 | 56 | xml | `browse` | 30277 | browse crawl depth 3 |
| `359-browse` | I | A | 11000 | `/Browse?key=LocalMusic%3AS%3ASong%2F%252Flibrary%252Fv1%252FSongs%253Fall%3D1%26service%3DLocalMusic%26limit%3D50%26section%3DE` | 200 | 25 | xml | `browse` | 20523 | browse crawl depth 3 |
| `360-browse` | I | A | 11000 | `/Browse?key=LocalMusic%3AMG%2FGenres%3Fgenre%3DAlternative` | 200 | 10 | xml | `browse` | 764 | browse crawl depth 3 |
| `361-browse` | I | A | 11000 | `/Browse?key=LocalMusic%3AMG%2FGenres%3Fgenre%3DChildren%2527s` | 200 | 9 | xml | `browse` | 776 | browse crawl depth 3 |
| `362-browse` | I | A | 11000 | `/Browse?key=LocalMusic%3AMG%2FGenres%3Fgenre%3DClassical` | 200 | 8 | xml | `browse` | 756 | browse crawl depth 3 |
| `363-browse` | I | A | 11000 | `/Browse?key=LocalMusic%3AMG%2FGenres%3Fgenre%3DEasy%2BListening` | 200 | 9 | xml | `browse` | 776 | browse crawl depth 3 |
| `364-browse` | I | A | 11000 | `/Browse?key=LocalMusic%3AMG%2FGenres%3Fgenre%3DElectronic` | 200 | 11 | xml | `browse` | 760 | browse crawl depth 3 |
| `365-browse` | I | A | 11000 | `/Browse?key=LocalMusic%3AMG%2FGenres%3Fgenre%3DEurovision` | 200 | 11 | xml | `browse` | 760 | browse crawl depth 3 |
| `366-browse` | I | A | 11000 | `/Browse?key=LocalMusic%3AS%3AComposer%2F%252Flibrary%252Fv1%252FComposers%253Fservice%3DLocalMusic%26limit%3D50%26section%3DA` | 200 | 12 | xml | `browse` | 1360 | browse crawl depth 3 |
| `367-browse` | I | A | 11000 | `/Browse?key=LocalMusic%3AS%3AComposer%2F%252Flibrary%252Fv1%252FComposers%253Fservice%3DLocalMusic%26limit%3D50%26section%3DB` | 200 | 12 | xml | `browse` | 1362 | browse crawl depth 3 |
| `368-browse` | I | A | 11000 | `/Browse?key=LocalMusic%3AS%3AComposer%2F%252Flibrary%252Fv1%252FComposers%253Fservice%3DLocalMusic%26limit%3D50%26section%3DC` | 200 | 11 | xml | `browse` | 666 | browse crawl depth 3 |
| `369-browse` | I | A | 11000 | `/Browse?key=LocalMusic%3AS%3AComposer%2F%252Flibrary%252Fv1%252FComposers%253Fservice%3DLocalMusic%26limit%3D50%26section%3DD` | 200 | 14 | xml | `browse` | 514 | browse crawl depth 3 |
| `370-browse` | I | A | 11000 | `/Browse?key=LocalMusic%3AS%3AComposer%2F%252Flibrary%252Fv1%252FComposers%253Fservice%3DLocalMusic%26limit%3D50%26section%3DE` | 200 | 13 | xml | `browse` | 1376 | browse crawl depth 3 |
| `371-browse` | I | | | *analysis* | | | | | | **crawl visited 60 nodes (depth<=3, fanout<=6)** |
| `372-browse` | I | A | 11000 | `/Songs?service=Tidal&category=FAVOURITES&start=0&end=999` | 200 | 164 | xml | `songs` | 17417 | [V] is browse paging capped at 50? |
| `373-browse` | I | A | 11000 | `/Songs?service=Tidal&category=FAVOURITES` | 200 | 175 | xml | `songs` | 10920 | paging: default |
| `374-browse` | I | A | 11000 | `/Songs?service=Tidal&category=FAVOURITES&start=0&end=999` | 200 | 161 | xml | `songs` | 17417 | paging: &start=0&end=999 |
| `375-browse` | I | A | 11000 | `/Songs?service=Tidal&category=FAVOURITES&start=0&end=49` | 200 | 148 | xml | `songs` | 17417 | paging: &start=0&end=49 |
| `376-browse` | I | A | 11000 | `/Songs?service=Tidal&category=FAVOURITES&start=50&end=99` | 200 | 146 | xml | `songs` | 19062 | paging: &start=50&end=99 |
| `377-browse` | I | A | 11000 | `/Songs?service=Tidal&category=FAVOURITES&start=100&end=100` | 200 | 203 | xml | `songs` | 10700 | paging: &start=100&end=100 |
| `378-browse` | I | A | 11000 | `/Songs?service=Tidal&category=FAVOURITES&start=-1&end=10` | 200 | 194 | xml | `error` | 112 | paging: &start=-1&end=10 |
| `379-browse` | I | A | 11000 | `/Songs?service=Tidal&category=FAVOURITES&start=10&end=5` | 200 | 194 | xml | `songs` | 11194 | paging: &start=10&end=5 |
| `380-browse` | I | A | 11000 | `/Songs?service=Tidal&category=FAVOURITES&start=abc&end=def` | 200 | 128 | xml | `songs` | 10920 | paging: &start=abc&end=def |
| `381-browse` | I | A | 11000 | `/Songs?service=Tidal&category=FAVOURITES&sort=name` | 200 | 130 | xml | `songs` | 10946 | sort=name: does the root echo it back and does order change? |
| `382-browse` | I | A | 11000 | `/Songs?service=Tidal&category=FAVOURITES&sort=recent` | 200 | 210 | xml | `songs` | 12406 | sort=recent: does the root echo it back and does order change? |
| `383-browse` | I | A | 11000 | `/Songs?service=Tidal&category=FAVOURITES&sort=album` | 200 | 182 | xml | `songs` | 10887 | sort=album: does the root echo it back and does order change? |
| `384-browse` | I | A | 11000 | `/Songs?service=Tidal&category=FAVOURITES&sort=artist` | 200 | 300 | xml | `songs` | 11255 | sort=artist: does the root echo it back and does order change? |
| `385-browse` | I | A | 11000 | `/Songs?service=Tidal&category=FAVOURITES&sort=nosuchsort` | 200 | 292 | xml | `songs` | 10958 | sort=nosuchsort: does the root echo it back and does order change? |
| `386-browse` | I | A | 11000 | `/Songs?service=Tidal&category=FAVOURITES&sort=recentDesc` | 200 | 159 | xml | `songs` | 10958 | sort=recentDesc: does the root echo it back and does order change? |
| `387-browse` | I | A | 11000 | `/Songs?service=Tidal&category=FAVOURITES&sort=-recent` | 200 | 145 | xml | `songs` | 10952 | sort=-recent: does the root echo it back and does order change? |
| `388-browse` | I | A | 11000 | `/Songs?service=Tidal&category=FAVOURITES&sort=recent%3Adesc` | 200 | 158 | xml | `songs` | 10962 | sort=recent:desc: does the root echo it back and does order change? |
| `389-browse` | I | A | 11000 | `/Songs?service=Tidal&category=FAVOURITES&sort=reverseName` | 200 | 128 | xml | `songs` | 10960 | sort=reverseName: does the root echo it back and does order change? |
| `390-browse` | I | | | *analysis* | | | | | | **C-18: cannot test descending sort against a list of 60 item(s)** |
| `391-browse` | I | A | 11000 | `/Browse?key=Tidal%3ASong%2F%252FSongs%253Fcategory%3DFAVOURITES%2526service%3DTidal` | 200 | 146 | xml | `browse` | 17585 | browse key with %26 for the inner ampersand (correct) |
| `392-browse` | I | A | 11000 | `/Browse?key=Tidal%3ASong%2F%252FSongs%253Fcategory%3DFAVOURITES%26amp%3Bservice%3DTidal` | 200 | 18 | xml | `browse` | 159 | browse key with &amp; instead (silent empty result) |
| `393-browse` | I | A | 11000 | `/Browse?sid=0` | 200 | 12 | xml | `browse` | 983 | does /Browse accept a bogus sid? |

### browse -- analysis detail

**crawl visited 60 nodes (depth<=3, fanout<=6)** (`371-browse`)

```
/Browse
/Browse?key=Airable%3A
/Browse?key=Airable%3ABrowseMenu%2F%252FRadioBrowse%253Fservice%3DAirable%26url%3Dhttps%25253A%25252F%25252F7818664144.airable.io%25252Fradio%25252Fgenres
/Browse?key=Airable%3ABrowseMenu%2F%252FRadioBrowse%253Fservice%3DAirable%26url%3Dhttps%25253A%25252F%25252F7818664144.airable.io%25252Fradio%25252Flocal
/Browse?key=Airable%3ABrowseMenu%2F%252FRadioBrowse%253Fservice%3DAirable%26url%3Dhttps%25253A%25252F%25252F7818664144.airable.io%25252Fradio%25252Fplace%25252F4147028435952962
/Browse?key=Airable%3ABrowseMenu%2F%252FRadioBrowse%253Fservice%3DAirable%26url%3Dhttps%25253A%25252F%25252F7818664144.airable.io%25252Fradio%25252Fplaces
/Browse?key=Airable%3ABrowseMenu%2F%252FRadioBrowse%253Fservice%3DAirable%26url%3Dhttps%25253A%25252F%25252F7818664144.airable.io%25252Fradio%25252Fpodcasts
/Browse?key=Airable%3ABrowseMenu%2F%252FRadioBrowse%253Fservice%3DAirable%26url%3Dhttps%25253A%25252F%25252F7818664144.airable.io%25252Fradio%25252Fstations%25252Fcharts
/Browse?key=BluOS%3A
/Browse?key=LocalMusic%3A
/Browse?key=LocalMusic%3AGG%2FGenres
/Browse?key=LocalMusic%3AMG%2FGenres%3Fgenre%3DAlternative
/Browse?key=LocalMusic%3AMG%2FGenres%3Fgenre%3DChildren%2527s
/Browse?key=LocalMusic%3AMG%2FGenres%3Fgenre%3DClassical
/Browse?key=LocalMusic%3AMG%2FGenres%3Fgenre%3DEasy%2BListening
/Browse?key=LocalMusic%3AMG%2FGenres%3Fgenre%3DElectronic
/Browse?key=LocalMusic%3AMG%2FGenres%3Fgenre%3DEurovision
/Browse?key=LocalMusic%3APlaylist%2F%252Flibrary%252Fv1%252FPlaylists%253Fimported%3D1%26service%3DLocalMusic
/Browse?key=LocalMusic%3AS%3AAlbum%2F%252Flibrary%252Fv1%252FAlbums%253Fservice%3DLocalMusic%26limit%3D50%26section%3D%2523
/Browse?key=LocalMusic%3AS%3AAlbum%2F%252Flibrary%252Fv1%252FAlbums%253Fservice%3DLocalMusic%26limit%3D50%26section%3DA
/Browse?key=LocalMusic%3AS%3AAlbum%2F%252Flibrary%252Fv1%252FAlbums%253Fservice%3DLocalMusic%26limit%3D50%26section%3DB
/Browse?key=LocalMusic%3AS%3AAlbum%2F%252Flibrary%252Fv1%252FAlbums%253Fservice%3DLocalMusic%26limit%3D50%26section%3DD
/Browse?key=LocalMusic%3AS%3AAlbum%2F%252Flibrary%252Fv1%252FAlbums%253Fservice%3DLocalMusic%26limit%3D50%26section%3DE
/Browse?key=LocalMusic%3AS%3AAlbum%2F%252Flibrary%252Fv1%252FAlbums%253Fservice%3DLocalMusic%26limit%3D50%26section%3DG
/Browse?key=LocalMusic%3AS%3AArtist%2F%252Flibrary%252Fv1%252FArtists%253Fservice%3DLocalMusic%26limit%3D50%26section%3DA
/Browse?key=LocalMusic%3AS%3AArtist%2F%252Flibrary%252Fv1%252FArtists%253Fservice%3DLocalMusic%26limit%3D50%26section%3DB
/Browse?key=LocalMusic%3AS%3AArtist%2F%252Flibrary%252Fv1%252FArtists%253Fservice%3DLocalMusic%26limit%3D50%26section%3DC
/Browse?key=LocalMusic%3AS%3AArtist%2F%252Flibrary%252Fv1%252FArtists%253Fservice%3DLocalMusic%26limit%3D50%26section%3DD
/Browse?key=LocalMusic%3AS%3AArtist%2F%252Flibrary%252Fv1%252FArtists%253Fservice%3DLocalMusic%26limit%3D50%26section%3DE
/Browse?key=LocalMusic%3AS%3AArtist%2F%252Flibrary%252Fv1%252FArtists%253Fservice%3DLocalMusic%26limit%3D50%26section%3DG
/Browse?key=LocalMusic%3AS%3AComposer%2F%252Flibrary%252Fv1%252FComposers%253Fservice%3DLocalMusic%26limit%3D50%26section%3DA
/Browse?key=LocalMusic%3AS%3AComposer%2F%252Flibrary%252Fv1%252FComposers%253Fservice%3DLocalMusic%26limit%3D50%26section%3DB
/Browse?key=LocalMusic%3AS%3AComposer%2F%252Flibrary%252Fv1%252FComposers%253Fservice%3DLocalMusic%26limit%3D50%26section%3DC
/Browse?key=LocalMusic%3AS%3AComposer%2F%252Flibrary%252Fv1%252FComposers%253Fservice%3DLocalMusic%26limit%3D50%26section%3DD
/Browse?key=LocalMusic%3AS%3AComposer%2F%252Flibrary%252Fv1%252FComposers%253Fservice%3DLocalMusic%26limit%3D50%26section%3DE
/Browse?key=LocalMusic%3AS%3ASong%2F%252Flibrary%252Fv1%252FSongs%253Fall%3D1%26service%3DLocalMusic%26limit%3D50%26section%3D%2523
/Browse?key=LocalMusic%3AS%3ASong%2F%252Flibrary%252Fv1%252FSongs%253Fall%3D1%26service%3DLocalMusic%26limit%3D50%26section%3DA
/Browse?key=LocalMusic%3AS%3ASong%2F%252Flibrary%252Fv1%252FSongs%253Fall%3D1%26service%3DLocalMusic%26
```

**C-18: cannot test descending sort against a list of 60 item(s)** (`390-browse`)

```
an empty or single-item list gives the same first item under every sort order, so 'unchanged' would say nothing. Point this at a service with a populated list to decide the claim.
```

## suite: claims

| id | v | player | port | request | status | ms | type | root | bytes | note |
|---|---|---|---|---|---|---|---|---|---|---|
| `195-claims` | O | A | 80 | `/diagnostics` | 200 | 19 | html | `html` | 3493 | [T blutui-rs] /diagnostics on port 80 |
| `196-claims` | O | A | 11000 | `/diagnostics` | 404 | 9 | text | `` | 19 | /diagnostics on 11000 (expected 404) |
| `197-claims` | O | B | 80 | `/diagnostics` | 200 | 19 | html | `html` | 3492 | [T blutui-rs] /diagnostics on port 80 |
| `198-claims` | O | B | 11000 | `/diagnostics` | 404 | 8 | text | `` | 19 | /diagnostics on 11000 (expected 404) |
| `199-claims` | I | A | 11000 | `/audiomodes` | 200 | 10 | none | `` | 0 | [T BluShell] bare GET /audiomodes returns <audiomode> |
| `200-claims` | I | B | 11000 | `/audiomodes` | 200 | 9 | none | `` | 0 | [T BluShell] bare GET /audiomodes returns <audiomode> |
| `201-claims` | O | A | 11000 | `/GetSettings` | 404 | 8 | text | `` | 19 | [V] /GetSettings absent on current firmware |
| `202-claims` | I | A | 11001 | `/GetSettings` | 404 | 7 | text | `` | 19 | /GetSettings on the settings port |
| `203-claims` | O | B | 11000 | `/GetSettings` | 404 | 8 | text | `` | 19 | [V] /GetSettings absent on current firmware |
| `204-claims` | I | B | 11001 | `/GetSettings` | 404 | 10 | text | `` | 19 | /GetSettings on the settings port |
| `205-claims` | O | A | 80 | `/Shares` | 200 | 12 | xml | `shares` | 186 | share config, read only |
| `206-claims` | I | A | 11000 | `/Shares` | 404 | 18 | text | `` | 19 | has /Shares migrated to 11000? |
| `207-claims` | O | B | 80 | `/Shares` | 200 | 10 | xml | `shares` | 186 | share config, read only |
| `208-claims` | I | B | 11000 | `/Shares` | 404 | 37 | text | `` | 19 | has /Shares migrated to 11000? |
| `209-claims` | I | A | 11000 | `/proxyToSlave` | 400 | 8 | text | `` | 15 | [T blutui-rs] does /proxyToSlave exist? (no params, nothing relayed) |
| `210-claims` | I | A | 11000 | `/Sync` | 404 | 18 | text | `` | 19 | [T bluos-dashboard] does the legacy /Sync path exist? (no params) |
| `211-claims` | I | A | 11000 | `/RadioPresets?service=Airable` | 200 | 304 | xml | `radiotime` | 841 | [T Blu4Net/BluShell] radio item attributes for Airable |
| `212-claims` | I | A | 11000 | `/RadioBrowse?service=Airable` | 200 | 56 | xml | `radiotime` | 841 | [T] total_count / key / is_active on <radiotime> items |
| `213-claims` | I | A | 11000 | `/RadioPresets?service=Capture` | 404 | 9 | text | `` | 8 | [T Blu4Net/BluShell] radio item attributes for Capture |
| `214-claims` | I | A | 11000 | `/RadioBrowse?service=Capture` | 200 | 20 | xml | `radiotime` | 412 | [T] total_count / key / is_active on <radiotime> items |
| `215-claims` | I | A | 11000 | `/RadioPresets?service=RadioParadise` | 200 | 613 | xml | `radiotime` | 2452 | [T Blu4Net/BluShell] radio item attributes for RadioParadise |
| `216-claims` | I | A | 11000 | `/RadioBrowse?service=RadioParadise` | 200 | 216 | xml | `radiotime` | 2452 | [T] total_count / key / is_active on <radiotime> items |
| `217-claims` | I | A | 11000 | `/RadioPresets?service=TuneIn` | 200 | 300 | xml | `error` | 123 | [T Blu4Net/BluShell] radio item attributes for TuneIn |
| `218-claims` | I | A | 11000 | `/RadioBrowse?service=TuneIn` | 200 | 619 | xml | `radiotime` | 3637 | [T] total_count / key / is_active on <radiotime> items |
| `219-claims` | I | A | 11000 | `/Search?service=LocalMusic&expr=a` | 404 | 14 | text | `` | 19 | [T BluShell] /Search container shape for LocalMusic |
| `220-claims` | I | A | 11000 | `/Search?service=Tidal&expr=a` | 404 | 22 | text | `` | 19 | [T BluShell] /Search container shape for Tidal |
| `221-claims` | I | A | 11000 | `/Status` | 200 | 17 | xml | `status` | 1271 | [T Blu4Net] <is_preset>/<preset_name> in /Status (read-only; recall itself is a round-2 test) |

## suite: discovery

| id | v | player | port | request | status | ms | type | root | bytes | note |
|---|---|---|---|---|---|---|---|---|---|---|
| `428-discovery` | O | - | 11430 | `UDP LSDP Q on interface broadcasts, listening on 11430 (class 0xFFFF)` | - | - |  | `` | - | LSDP Q on interface broadcasts, listening on 11430 (class 0xFFFF) |
| `429-discovery` | O | - | 11430 | `UDP LSDP Q broadcast, four player classes` | - | - |  | `` | - | LSDP Q broadcast, four player classes |
| `430-discovery` | I | - | 11430 | `UDP LSDP Q unicast to player A (control for T-26)` | - | - |  | `` | - | LSDP Q unicast to player A (control for T-26) |
| `431-discovery` | I | - | 11430 | `UDP LSDP R unicast to player A (T-26)` | - | - |  | `` | - | LSDP R unicast to player A (T-26) |
| `432-discovery` | I | - | 11430 | `UDP LSDP Q unicast to player B (control for T-26)` | - | - |  | `` | - | LSDP Q unicast to player B (control for T-26) |
| `433-discovery` | I | - | 11430 | `UDP LSDP R unicast to player B (T-26)` | - | - |  | `` | - | LSDP R unicast to player B (T-26) |
| `434-discovery` | U | | | *analysis* | | | | | | **no player answered a UNICAST LSDP query of either form** |
| `435-discovery` | I | | | *analysis* | | | | | | **mDNS is not probed by this harness** |

### discovery -- analysis detail

**no player answered a UNICAST LSDP query of either form** (`434-discovery`)

```
So T-26 is inconclusive rather than disconfirmed: the datagrams may never have arrived. Check the host firewall and subnet, then re-run.
```

**mDNS is not probed by this harness** (`435-discovery`)

```
Run separately:  avahi-browse -rt _musc._tcp   or   dns-sd -B _musc._tcp
```

## suite: env

| id | v | player | port | request | status | ms | type | root | bytes | note |
|---|---|---|---|---|---|---|---|---|---|---|
| `001-env` | O | A | 11000 | `/SyncStatus` | 200 | 10 | xml | `SyncStatus` | 410 | player identity and group topology |
| `002-env` | O | A | 11000 | `/Status` | 200 | 11 | xml | `status` | 1270 | full player state |
| `003-env` | O | A | 11000 | `/GitVersion` | 200 | 11 | xml | `version` | 65 | firmware build |
| `004-env` | O | A | 11000 | `/Services` | 200 | 32 | xml | `services` | 62497 | service and menu tree (the sort/filter vocabulary) |
| `005-env` | O | A | 11000 | `/Presets` | 200 | 11 | xml | `presets` | 294 | preset list |
| `006-env` | O | A | 11000 | `/Playlist` | 200 | 17 | xml | `playlist` | 18246 | current queue |
| `007-env` | O | A | 11000 | `/Volume` | 200 | 9 | xml | `volume` | 142 | bare /Volume as a read (bluesound_alt) |
| `008-env` | O | A | 11000 | `/Name` | 200 | 14 | xml | `name` | 56 | bare /Name reads rather than writes |
| `009-env` | O | A | 11000 | `/Alarms` | 200 | 16 | xml | `alarms` | 79 | alarm list; days bitmask claim (times are in Europe/Copenhagen) |
| `010-env` | O | A | 11000 | `/BTDevices?timeout=1` | 200 | 15 | xml | `btdevices` | 91 | bluetooth device list |
| `011-env` | U | A | 11000 | `/GetUnpairedSlaves` | 400 | 24 | none | `` | 0 | pairable speakers |
| `012-env` | O | B | 11000 | `/SyncStatus` | 200 | 11 | xml | `SyncStatus` | 393 | player identity and group topology |
| `013-env` | O | B | 11000 | `/Status` | 200 | 9 | xml | `status` | 1254 | full player state |
| `014-env` | O | B | 11000 | `/GitVersion` | 200 | 10 | xml | `version` | 65 | firmware build |
| `015-env` | O | B | 11000 | `/Services` | 200 | 32 | xml | `services` | 62497 | service and menu tree (the sort/filter vocabulary) |
| `016-env` | O | B | 11000 | `/Presets` | 200 | 13 | xml | `presets` | 67 | preset list |
| `017-env` | O | B | 11000 | `/Playlist` | 200 | 55 | xml | `playlist` | 62326 | current queue |
| `018-env` | O | B | 11000 | `/Volume` | 200 | 35 | xml | `volume` | 142 | bare /Volume as a read (bluesound_alt) |
| `019-env` | O | B | 11000 | `/Name` | 200 | 9 | xml | `name` | 58 | bare /Name reads rather than writes |
| `020-env` | O | B | 11000 | `/Alarms` | 200 | 9 | xml | `alarms` | 79 | alarm list; days bitmask claim (times are in Europe/Copenhagen) |
| `021-env` | O | B | 11000 | `/BTDevices?timeout=1` | 200 | 14 | xml | `btdevices` | 91 | bluetooth device list |
| `022-env` | U | B | 11000 | `/GetUnpairedSlaves` | 400 | 9 | none | `` | 0 | pairable speakers |
| `023-env` | O | C | 11000 | `/SyncStatus` | 200 | 8 | xml | `SyncStatus` | 390 | player identity and group topology |
| `024-env` | O | C | 11000 | `/Status` | 200 | 9 | xml | `status` | 1251 | full player state |
| `025-env` | O | C | 11000 | `/GitVersion` | 200 | 8 | xml | `version` | 65 | firmware build |
| `026-env` | O | C | 11000 | `/Services` | 200 | 28 | xml | `services` | 62497 | service and menu tree (the sort/filter vocabulary) |
| `027-env` | O | C | 11000 | `/Presets` | 200 | 12 | xml | `presets` | 67 | preset list |
| `028-env` | O | C | 11000 | `/Playlist` | 200 | 16 | xml | `playlist` | 15105 | current queue |
| `029-env` | O | C | 11000 | `/Volume` | 200 | 9 | xml | `volume` | 140 | bare /Volume as a read (bluesound_alt) |
| `030-env` | O | C | 11000 | `/Name` | 200 | 7 | xml | `name` | 59 | bare /Name reads rather than writes |
| `031-env` | O | C | 11000 | `/Alarms` | 200 | 8 | xml | `alarms` | 79 | alarm list; days bitmask claim (times are in Europe/Copenhagen) |
| `032-env` | O | C | 11000 | `/BTDevices?timeout=1` | 200 | 15 | xml | `btdevices` | 90 | bluetooth device list |
| `033-env` | U | C | 11000 | `/GetUnpairedSlaves` | 400 | 7 | none | `` | 0 | pairable speakers |
| `034-env` | O | D | 11000 | `/SyncStatus` | 200 | 20 | xml | `SyncStatus` | 387 | player identity and group topology |
| `035-env` | O | D | 11000 | `/Status` | 200 | 18 | xml | `status` | 1448 | full player state |
| `036-env` | O | D | 11000 | `/GitVersion` | 200 | 19 | xml | `version` | 65 | firmware build |
| `037-env` | O | D | 11000 | `/Services` | 200 | 91 | xml | `services` | 62497 | service and menu tree (the sort/filter vocabulary) |
| `038-env` | O | D | 11000 | `/Presets` | 200 | 25 | xml | `presets` | 424 | preset list |
| `039-env` | O | D | 11000 | `/Playlist` | 200 | 4232 | xml | `playlist` | 10138 | current queue |
| `040-env` | O | D | 11000 | `/Volume` | 200 | 12 | xml | `volume` | 141 | bare /Volume as a read (bluesound_alt) |
| `041-env` | O | D | 11000 | `/Name` | 200 | 18 | xml | `name` | 64 | bare /Name reads rather than writes |
| `042-env` | O | D | 11000 | `/Alarms` | 200 | 11 | xml | `alarms` | 363 | alarm list; days bitmask claim (times are in Europe/Copenhagen) |
| `043-env` | U | D | 11000 | `/BTDevices?timeout=1` | 503 | 11 | none | `` | 0 | bluetooth device list |
| `044-env` | U | D | 11000 | `/GetUnpairedSlaves` | 400 | 30 | none | `` | 0 | pairable speakers |
| `045-env` | I | | | *analysis* | | | | | | **harvested facts for later suites** |
| `046-env` | I | | | *analysis* | | | | | | **fleet capabilities, used to skip tests this hardware cannot answer** |
| `047-env` | I | | | *analysis* | | | | | | **3 thing(s) this fleet cannot answer** |

### env -- analysis detail

**harvested facts for later suites** (`045-env`)

```
{"songid": "Tidal:48513985", "album": "Heaven", "artist": "Alex Adair", "service": "Tidal", "image": "/Artwork?service=Tidal&amp;songid=Tidal%3A48513985", "fn": "Tidal:48513985", "preset_player": "A", "services": ["Airable", "Alarms", "BluOS", "Capture", "LocalMusic", "RadioParadise", "Tidal", "TuneIn"]}
```

**fleet capabilities, used to skip tests this hardware cannot answer** (`046-env`)

```
| player | model | capture inputs | bluetooth | presets | subwoofer |
|---|---|---|---|---|---|
| A | N132 | 1 | yes | 1 | yes |
| B | N130 | 1 | yes | 0 | no |
| C | N132 | 1 | yes | 0 | no |
| D | N110 | 0 | no | 2 | yes |
```

**3 thing(s) this fleet cannot answer** (`047-env`)

```
- input selection is weakened: no player advertises two inputs, so 'it switched' cannot be separated from 'it was already there'. Temporarily enabling a second input makes the result conclusive
- T-14 authentication: no way found to set credentials on consumer N-series hardware; the auth path stays source-derived and unexercised
- CI-series multi-zone port offsets: no CI hardware in this fleet

These are recorded as NOT APPLICABLE rather than left to look like failures. A claim untestable on this hardware must never be written into the register as DISCONFIRMED.
```

## suite: errors

| id | v | player | port | request | status | ms | type | root | bytes | note |
|---|---|---|---|---|---|---|---|---|---|---|
| `180-errors` | I | A | 11000 | `/Songs?service=NoSuchService` | 404 | 11 | text | `` | 14 | unknown service on a typed browse endpoint |
| `181-errors` | I | A | 11000 | `/Songs` | 302 | 17 | xml | `a` | 63 | typed browse endpoint with no service at all |
| `182-errors` | I | A | 11000 | `/Albums?service=NoSuchService` | 404 | 12 | text | `` | 14 | unknown service |
| `183-errors` | I | A | 11000 | `/Browse?key=NoSuchService%3A` | 404 | 70 | none | `` | 0 | unknown browse key |
| `184-errors` | I | A | 11000 | `/Browse?key=` | 200 | 50 | xml | `browse` | 983 | empty browse key |
| `185-errors` | I | A | 11000 | `/Search?service=LocalMusic` | 404 | 9 | text | `` | 19 | search with no expression |
| `186-errors` | I | A | 11000 | `/Search?expr=` | 404 | 10 | text | `` | 19 | search with empty expression |
| `187-errors` | I | A | 11000 | `/Artwork` | 200 | 7 | xml | `artwork` | 68 | artwork with no parameters |
| `188-errors` | I | A | 11000 | `/Artwork?service=NoSuchService&songid=1` | 200 | 9 | xml | `artwork` | 68 | artwork for an unknown service |
| `189-errors` | I | A | 11000 | `/RadioBrowse?service=NoSuchService` | 404 | 8 | text | `` | 14 | radio browse, unknown service |
| `190-errors` | I | A | 11000 | `/Settings?id=nosuchpage&schemaVersion=35` | 301 | 8 | xml | `a` | 102 | unknown settings page |
| `191-errors` | I | A | 11000 | `/Services?schemaVersion=abc` | 200 | 24 | xml | `services` | 62496 | malformed schemaVersion |
| `192-errors` | I | A | 11000 | `/Status?timeout=notanumber` | 200 | 12 | xml | `status` | 1271 | malformed timeout |
| `193-errors` | I | A | 11001 | `/Settings?id=nosuchpage&schemaVersion=35` | 404 | 7 | text | `` | 26 | unknown settings page, direct on 11001 |
| `194-errors` | I | | | *analysis* | | | | | | **reading guide** |

### errors -- analysis detail

**reading guide** (`194-errors`)

```
Compare: bare 404 text/plain (Go net/http, unknown path) vs <error type=...> envelope (endpoint exists, refused) vs flat <error>text</error> vs raw HTML. Spec 0.1 and 11.1.
```

## suite: inputs

| id | v | player | port | request | status | ms | type | root | bytes | note |
|---|---|---|---|---|---|---|---|---|---|---|
| `222-inputs` | I | A | 11000 | `/Browse` | 200 | 27 | xml | `browse` | 983 | browse root: which inputs are offered here? |
| `223-inputs` | I | A | 11000 | `/RadioBrowse?service=Capture` | 200 | 9 | xml | `radiotime` | 412 | the Capture service: the input list the app builds its picker from |
| `224-inputs` | I | A | 11001 | `/Settings?id=capture&schemaVersion=35` | 200 | 11 | xml | `settings` | 1682 | the inputs settings page: where enable/disable actually lives |
| `225-inputs` | I | | | *analysis* | | | | | | **A: settings page markers that may encode enable/disable** |
| `226-inputs` | I | A | 11000 | `/Sources` | 404 | 9 | text | `` | 19 | /Sources: a third enumeration surface |
| `227-inputs` | I | | | *analysis* | | | | | | **A: input visibility across surfaces** |
| `228-inputs` | I | | | *analysis* | | | | | | **A: 3 name(s) differ across surfaces, 1 known to settings but not browsable** |
| `229-inputs` | I | B | 11000 | `/Browse` | 200 | 72 | xml | `browse` | 864 | browse root: which inputs are offered here? |
| `230-inputs` | I | B | 11000 | `/RadioBrowse?service=Capture` | 200 | 12 | xml | `radiotime` | 267 | the Capture service: the input list the app builds its picker from |
| `231-inputs` | I | B | 11001 | `/Settings?id=capture&schemaVersion=35` | 200 | 11 | xml | `settings` | 1682 | the inputs settings page: where enable/disable actually lives |
| `232-inputs` | I | | | *analysis* | | | | | | **B: settings page markers that may encode enable/disable** |
| `233-inputs` | I | B | 11000 | `/Sources` | 404 | 11 | text | `` | 19 | /Sources: a third enumeration surface |
| `234-inputs` | I | | | *analysis* | | | | | | **B: input visibility across surfaces** |
| `235-inputs` | I | | | *analysis* | | | | | | **B: 2 name(s) differ across surfaces, 1 known to settings but not browsable** |
| `236-inputs` | I | C | 11000 | `/Browse` | 200 | 57 | xml | `browse` | 864 | browse root: which inputs are offered here? |
| `237-inputs` | I | C | 11000 | `/RadioBrowse?service=Capture` | 200 | 10 | xml | `radiotime` | 267 | the Capture service: the input list the app builds its picker from |
| `238-inputs` | I | C | 11001 | `/Settings?id=capture&schemaVersion=35` | 200 | 10 | xml | `settings` | 1682 | the inputs settings page: where enable/disable actually lives |
| `239-inputs` | I | | | *analysis* | | | | | | **C: settings page markers that may encode enable/disable** |
| `240-inputs` | I | C | 11000 | `/Sources` | 404 | 9 | text | `` | 19 | /Sources: a third enumeration surface |
| `241-inputs` | I | | | *analysis* | | | | | | **C: input visibility across surfaces** |
| `242-inputs` | I | | | *analysis* | | | | | | **C: 2 name(s) differ across surfaces, 1 known to settings but not browsable** |
| `243-inputs` | I | D | 11000 | `/Browse` | 200 | 27 | xml | `browse` | 813 | browse root: which inputs are offered here? |
| `244-inputs` | I | D | 11000 | `/RadioBrowse?service=Capture` | 200 | 15 | xml | `radiotime` | 226 | the Capture service: the input list the app builds its picker from |
| `245-inputs` | I | D | 11001 | `/Settings?id=capture&schemaVersion=35` | 200 | 21 | xml | `settings` | 1565 | the inputs settings page: where enable/disable actually lives |
| `246-inputs` | I | | | *analysis* | | | | | | **D: settings page markers that may encode enable/disable** |
| `247-inputs` | I | D | 11000 | `/Sources` | 404 | 19 | text | `` | 19 | /Sources: a third enumeration surface |
| `248-inputs` | I | | | *analysis* | | | | | | **D: input visibility across surfaces** |
| `249-inputs` | I | | | *analysis* | | | | | | **D: 2 name(s) differ across surfaces, 1 known to settings but not browsable** |

### inputs -- analysis detail

**A: settings page markers that may encode enable/disable** (`225-inputs`)

```
?=Disabled
```

**A: input visibility across surfaces** (`227-inputs`)

```
| input | /Browse root | /RadioBrowse?service=Capture | /Settings?id=capture | /Sources |
|---|---|---|---|---|
| Bluetooth | - | - | yes | - |
| HDMI ARC | yes | yes | - | - |
| Spotify | - | yes | - | - |
```

**A: 3 name(s) differ across surfaces, 1 known to settings but not browsable** (`228-inputs`)

```
names only some surfaces list: Bluetooth, HDMI ARC, Spotify
input-like names known to the settings tree but offered by neither browse surface: Bluetooth

Name mismatches alone prove nothing -- the surfaces use different display strings. The question is settled by state_source, which tries to select unadvertised input slots directly.
```

**B: settings page markers that may encode enable/disable** (`232-inputs`)

```
?=Disabled
```

**B: input visibility across surfaces** (`234-inputs`)

```
| input | /Browse root | /RadioBrowse?service=Capture | /Settings?id=capture | /Sources |
|---|---|---|---|---|
| Bluetooth | - | - | yes | - |
| HDMI ARC | yes | yes | - | - |
```

**B: 2 name(s) differ across surfaces, 1 known to settings but not browsable** (`235-inputs`)

```
names only some surfaces list: Bluetooth, HDMI ARC
input-like names known to the settings tree but offered by neither browse surface: Bluetooth

Name mismatches alone prove nothing -- the surfaces use different display strings. The question is settled by state_source, which tries to select unadvertised input slots directly.
```

**C: settings page markers that may encode enable/disable** (`239-inputs`)

```
?=Disabled
```

**C: input visibility across surfaces** (`241-inputs`)

```
| input | /Browse root | /RadioBrowse?service=Capture | /Settings?id=capture | /Sources |
|---|---|---|---|---|
| Bluetooth | - | - | yes | - |
| HDMI ARC | yes | yes | - | - |
```

**C: 2 name(s) differ across surfaces, 1 known to settings but not browsable** (`242-inputs`)

```
names only some surfaces list: Bluetooth, HDMI ARC
input-like names known to the settings tree but offered by neither browse surface: Bluetooth

Name mismatches alone prove nothing -- the surfaces use different display strings. The question is settled by state_source, which tries to select unadvertised input slots directly.
```

**D: settings page markers that may encode enable/disable** (`246-inputs`)

```
?=Disabled
```

**D: input visibility across surfaces** (`248-inputs`)

```
| input | /Browse root | /RadioBrowse?service=Capture | /Settings?id=capture | /Sources |
|---|---|---|---|---|
| Bluetooth | - | - | yes | - |
| Spotify | - | yes | - | - |
```

**D: 2 name(s) differ across surfaces, 1 known to settings but not browsable** (`249-inputs`)

```
names only some surfaces list: Bluetooth, Spotify
input-like names known to the settings tree but offered by neither browse surface: Bluetooth

Name mismatches alone prove nothing -- the surfaces use different display strings. The question is settled by state_source, which tries to select unadvertised input slots directly.
```

## suite: longpoll

| id | v | player | port | request | status | ms | type | root | bytes | note |
|---|---|---|---|---|---|---|---|---|---|---|
| `154-longpoll` | I | A | 11000 | `/Status?etag=f01f103508c1be5179fbd3a26a2308ed&timeout=4` | 200 | 4301 | xml | `status` | 1270 | does /Status hold the connection with a live etag? |
| `155-longpoll` | O | | | *analysis* | | | | | | **/Status long-poll: HELD ~4.3s** |
| `156-longpoll` | I | A | 11000 | `/SyncStatus?etag=523&timeout=4` | 200 | 4284 | xml | `SyncStatus` | 410 | does /SyncStatus hold the connection with a live etag? |
| `157-longpoll` | O | | | *analysis* | | | | | | **/SyncStatus long-poll: HELD ~4.3s** |
| `158-longpoll` | I | A | 11000 | `/BTDevices?etag=15&timeout=4` | 200 | 593 | xml | `btdevices` | 91 | does /BTDevices hold the connection with a live etag? |
| `159-longpoll` | O | | | *analysis* | | | | | | **/BTDevices long-poll: returned immediately** |
| `160-longpoll` | I | | | *analysis* | | | | | | **/Playlist: no etag attribute in the response** |
| `161-longpoll` | I | | | *analysis* | | | | | | **/Presets: no etag attribute in the response** |
| `162-longpoll` | I | | | *analysis* | | | | | | **/Services: no etag attribute in the response** |
| `163-longpoll` | I | | | *analysis* | | | | | | **/Alarms: no etag attribute in the response** |
| `164-longpoll` | I | A | 11000 | `/Volume?etag=a79f2e9d2881ae370f00800f9d0a2c26&timeout=4` | 200 | 4223 | xml | `volume` | 142 | does /Volume hold the connection with a live etag? |
| `165-longpoll` | O | | | *analysis* | | | | | | **/Volume long-poll: HELD ~4.2s** |
| `166-longpoll` | I | A | 11000 | `/Status?etag=bogus-etag-value&timeout=5` | 200 | 14 | xml | `status` | 1270 | stale/invalid etag must return immediately |
| `167-longpoll` | I | A | 11000 | `/Status?etag=0&timeout=5` | 200 | 36 | xml | `status` | 1270 | stale/invalid etag must return immediately |
| `168-longpoll` | I | A | 11000 | `/Status?etag=&timeout=5` | 200 | 10 | xml | `status` | 1270 | stale/invalid etag must return immediately |
| `169-longpoll` | I | A | 11000 | `/Status?etag=%20&timeout=5` | 200 | 11 | xml | `status` | 1270 | stale/invalid etag must return immediately |
| `170-longpoll` | I | A | 11000 | `/Status?etag=11111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111&timeout=5` | 200 | 9 | xml | `status` | 1270 | stale/invalid etag must return immediately |
| `171-longpoll` | I | A | 11000 | `/Status?etag=3ad0140b369e1ef1aac10099dec354f8&timeout=1` | 200 | 1010 | xml | `status` | 1270 | timeout=1: does the hold match the request? |
| `172-longpoll` | I | A | 11000 | `/Status?etag=3ad0140b369e1ef1aac10099dec354f8&timeout=5` | 200 | 5013 | xml | `status` | 1270 | timeout=5: does the hold match the request? |
| `173-longpoll` | I | A | 11000 | `/Status?etag=3ad0140b369e1ef1aac10099dec354f8&timeout=-1` | 200 | 11 | xml | `status` | 1270 | malformed timeout=-1 |
| `174-longpoll` | I | A | 11000 | `/Status?etag=3ad0140b369e1ef1aac10099dec354f8&timeout=abc` | 200 | 8 | xml | `status` | 1270 | malformed timeout=abc |
| `175-longpoll` | I | A | 11000 | `/Status?etag=3ad0140b369e1ef1aac10099dec354f8&timeout=0` | 200 | 8 | xml | `status` | 1270 | malformed timeout=0 |
| `176-longpoll` | O | | | *analysis* | | | | | | **concurrency 8: 8 held ~8s, 0 returned early, 0 failed (wall 8.0s)** |
| `177-longpoll` | O | | | *analysis* | | | | | | **concurrency 24: 24 held ~8s, 0 returned early, 0 failed (wall 8.1s)** |
| `178-longpoll` | O | | | *analysis* | | | | | | **concurrency 32: 32 held ~8s, 0 returned early, 0 failed (wall 8.3s)** |
| `179-longpoll` | I | | | *analysis* | | | | | | **two simultaneous /SyncStatus holds released together** |

### longpoll -- analysis detail

**/Status long-poll: HELD ~4.3s** (`155-longpoll`)

```
etag length 32, elapsed 4301.5ms
```

**/SyncStatus long-poll: HELD ~4.3s** (`157-longpoll`)

```
etag length 3, elapsed 4284.0ms
```

**/BTDevices long-poll: returned immediately** (`159-longpoll`)

```
etag length 2, elapsed 593.5ms
```

**/Playlist: no etag attribute in the response** (`160-longpoll`)

```
cannot long-poll this endpoint by the documented convention
```

**/Presets: no etag attribute in the response** (`161-longpoll`)

```
cannot long-poll this endpoint by the documented convention
```

**/Services: no etag attribute in the response** (`162-longpoll`)

```
cannot long-poll this endpoint by the documented convention
```

**/Alarms: no etag attribute in the response** (`163-longpoll`)

```
cannot long-poll this endpoint by the documented convention
```

**/Volume long-poll: HELD ~4.2s** (`165-longpoll`)

```
etag length 32, elapsed 4223.5ms
```

**concurrency 8: 8 held ~8s, 0 returned early, 0 failed (wall 8.0s)** (`176-longpoll`)

```
  #00 status=200 elapsed=8.02s 
  #01 status=200 elapsed=8.02s 
  #02 status=200 elapsed=8.02s 
  #03 status=200 elapsed=8.02s 
  #04 status=200 elapsed=8.02s 
  #05 status=200 elapsed=8.02s 
  #06 status=200 elapsed=8.02s 
  #07 status=200 elapsed=8.02s 
```

**concurrency 24: 24 held ~8s, 0 returned early, 0 failed (wall 8.1s)** (`177-longpoll`)

```
  #00 status=200 elapsed=8.09s 
  #01 status=200 elapsed=8.09s 
  #02 status=200 elapsed=8.09s 
  #03 status=200 elapsed=8.09s 
  #04 status=200 elapsed=8.08s 
  #05 status=200 elapsed=8.09s 
  #06 status=200 elapsed=8.09s 
  #07 status=200 elapsed=8.08s 
  #08 status=200 elapsed=8.09s 
  #09 status=200 elapsed=8.09s 
  #10 status=200 elapsed=8.09s 
  #11 status=200 elapsed=8.08s 
  #12 status=200 elapsed=8.08s 
  #13 status=200 elapsed=8.08s 
  #14 status=200 elapsed=8.09s 
  #15 status=200 elapsed=8.08s 
  #16 status=200 elapsed=8.08s 
  #17 status=200 elapsed=8.09s 
  #18 status=200 elapsed=8.08s 
  #19 status=200 elapsed=8.07s 
  #20 status=200 elapsed=8.08s 
  #21 status=200 elapsed=8.08s 
  #22 status=200 elapsed=8.08s 
  #23 status=200 elapsed=8.08s 
```

**concurrency 32: 32 held ~8s, 0 returned early, 0 failed (wall 8.3s)** (`178-longpoll`)

```
  #00 status=200 elapsed=8.27s 
  #01 status=200 elapsed=8.27s 
  #02 status=200 elapsed=8.26s 
  #03 status=200 elapsed=8.28s 
  #04 status=200 elapsed=8.26s 
  #05 status=200 elapsed=8.28s 
  #06 status=200 elapsed=8.26s 
  #07 status=200 elapsed=8.27s 
  #08 status=200 elapsed=8.26s 
  #09 status=200 elapsed=8.26s 
  #10 status=200 elapsed=8.27s 
  #11 status=200 elapsed=8.26s 
  #12 status=200 elapsed=8.27s 
  #13 status=200 elapsed=8.26s 
  #14 status=200 elapsed=8.25s 
  #15 status=200 elapsed=8.26s 
  #16 status=200 elapsed=8.26s 
  #17 status=200 elapsed=8.25s 
  #18 status=200 elapsed=8.26s 
  #19 status=200 elapsed=8.26s 
  #20 status=200 elapsed=8.25s 
  #21 status=200 elapsed=8.25s 
  #22 status=200 elapsed=8.25s 
  #23 status=200 elapsed=8.25s 
  #24 status=200 elapsed=8.25s 
  #25 status=200 elapsed=8.26s 
  #26 status=200 elapsed=8.25s 
  #27 status=200 elapsed=8.26s 
  #28 status=200 elapsed=8.25s 
  #29 status=200 elapsed=8.24s 
  #30 status=200 elapsed=8.25s 
  #31 status=200 elapsed=8.25s 
```

**two simultaneous /SyncStatus holds released together** (`179-longpoll`)

```
elapsed: 5.01s, 5.01s
```

## suite: ports

| id | v | player | port | request | status | ms | type | root | bytes | note |
|---|---|---|---|---|---|---|---|---|---|---|
| `083-ports` | I | A | 11001 | `/Status` | 404 | 10 | text | `` | 19 | port matrix |
| `084-ports` | I | A | 80 | `/Status` | 404 | 29 | none | `` | 0 | port matrix |
| `085-ports` | I | A | 11001 | `/SyncStatus` | 404 | 9 | text | `` | 19 | port matrix |
| `086-ports` | I | A | 80 | `/SyncStatus` | 404 | 12 | none | `` | 0 | port matrix |
| `087-ports` | I | A | 11001 | `/Services` | 404 | 10 | text | `` | 19 | port matrix |
| `088-ports` | I | A | 80 | `/Services` | 404 | 9 | none | `` | 0 | port matrix |
| `089-ports` | I | A | 11001 | `/GitVersion` | 404 | 9 | text | `` | 19 | port matrix |
| `090-ports` | I | A | 80 | `/GitVersion` | 404 | 9 | none | `` | 0 | port matrix |
| `091-ports` | I | A | 11001 | `/Presets` | 404 | 9 | text | `` | 19 | port matrix |
| `092-ports` | I | A | 80 | `/Presets` | 404 | 10 | none | `` | 0 | port matrix |
| `093-ports` | I | A | 11001 | `/Playlist` | 404 | 9 | text | `` | 19 | port matrix |
| `094-ports` | I | A | 80 | `/Playlist` | 404 | 11 | none | `` | 0 | port matrix |
| `095-ports` | I | A | 11001 | `/Volume` | 404 | 9 | text | `` | 19 | port matrix |
| `096-ports` | I | A | 80 | `/Volume` | 404 | 8 | none | `` | 0 | port matrix |
| `097-ports` | I | A | 11001 | `/Name` | 404 | 9 | text | `` | 19 | port matrix |
| `098-ports` | I | A | 80 | `/Name` | 404 | 9 | none | `` | 0 | port matrix |
| `099-ports` | I | A | 11001 | `/Alarms` | 404 | 9 | text | `` | 19 | port matrix |
| `100-ports` | I | A | 80 | `/Alarms` | 404 | 24 | none | `` | 0 | port matrix |
| `101-ports` | I | A | 11000 | `/Sources` | 404 | 11 | text | `` | 19 | port matrix |
| `102-ports` | I | A | 11001 | `/Sources` | 404 | 9 | text | `` | 19 | port matrix |
| `103-ports` | I | A | 80 | `/Sources` | 404 | 31 | none | `` | 0 | port matrix |
| `104-ports` | I | A | 11000 | `/RadioPresets` | 404 | 7 | text | `` | 1 | port matrix |
| `105-ports` | I | A | 11001 | `/RadioPresets` | 404 | 9 | text | `` | 19 | port matrix |
| `106-ports` | I | A | 80 | `/RadioPresets` | 404 | 10 | none | `` | 0 | port matrix |
| `107-ports` | I | A | 11000 | `/Browse` | 200 | 9 | xml | `browse` | 983 | port matrix |
| `108-ports` | I | A | 11001 | `/Browse` | 404 | 9 | text | `` | 19 | port matrix |
| `109-ports` | I | A | 80 | `/Browse` | 404 | 10 | none | `` | 0 | port matrix |
| `110-ports` | I | A | 11000 | `/Shares` | 404 | 10 | text | `` | 19 | port matrix |
| `111-ports` | I | A | 11001 | `/Shares` | 404 | 13 | text | `` | 19 | port matrix |
| `112-ports` | I | A | 80 | `/Shares` | 200 | 11 | xml | `shares` | 186 | port matrix |
| `113-ports` | I | A | 11000 | `/diagnostics` | 404 | 9 | text | `` | 19 | port matrix |
| `114-ports` | I | A | 11001 | `/diagnostics` | 404 | 9 | text | `` | 19 | port matrix |
| `115-ports` | I | A | 80 | `/diagnostics` | 200 | 22 | html | `html` | 3492 | port matrix |
| `116-ports` | I | A | 11000 | `/ui/Configuration` | 200 | 11 | xml | `configuration` | 709 | port matrix |
| `117-ports` | I | A | 11001 | `/ui/Configuration` | 404 | 10 | text | `` | 19 | port matrix |
| `118-ports` | I | A | 80 | `/ui/Configuration` | 404 | 9 | none | `` | 0 | port matrix |
| `119-ports` | I | A | 11000 | `/Settings?schemaVersion=35` | 301 | 9 | xml | `a` | 84 | port matrix |
| `120-ports` | I | A | 11001 | `/Settings?schemaVersion=35` | 200 | 13 | xml | `settings` | 2070 | port matrix |
| `121-ports` | I | A | 80 | `/Settings?schemaVersion=35` | 404 | 9 | none | `` | 0 | port matrix |
| `122-ports` | I | A | 11000 | `/GetSettings` | 404 | 9 | text | `` | 19 | port matrix |
| `123-ports` | I | A | 11001 | `/GetSettings` | 404 | 10 | text | `` | 19 | port matrix |
| `124-ports` | I | A | 80 | `/GetSettings` | 404 | 9 | none | `` | 0 | port matrix |
| `125-ports` | I | A | 11000 | `/audiomodes` | 200 | 10 | none | `` | 0 | port matrix |
| `126-ports` | I | A | 11001 | `/audiomodes` | 404 | 10 | text | `` | 19 | port matrix |
| `127-ports` | I | A | 80 | `/audiomodes` | 404 | 9 | none | `` | 0 | port matrix |
| `128-ports` | I | A | 11000 | `/proxyToSlave` | 400 | 29 | text | `` | 15 | port matrix |
| `129-ports` | I | A | 11001 | `/proxyToSlave` | 404 | 9 | text | `` | 19 | port matrix |
| `130-ports` | I | A | 80 | `/proxyToSlave` | 404 | 11 | none | `` | 0 | port matrix |
| `131-ports` | I | A | 11000 | `/Info` | 302 | 38 | xml | `a` | 24 | port matrix |
| `132-ports` | I | A | 11001 | `/Info` | 404 | 10 | text | `` | 19 | port matrix |
| `133-ports` | I | A | 80 | `/Info` | 404 | 11 | none | `` | 0 | port matrix |
| `134-ports` | I | A | 11000 | `/Version` | 200 | 45 | xml | `version` | 65 | port matrix |
| `135-ports` | I | A | 11001 | `/Version` | 404 | 9 | text | `` | 19 | port matrix |
| `136-ports` | I | A | 80 | `/Version` | 404 | 9 | none | `` | 0 | port matrix |
| `137-ports` | U | A | 11000 | `/ExternalSource` | 200 | 8 | xml | `error` | 84 | does this path exist at all? |
| `138-ports` | O | A | 11000 | `/Players` | 404 | 13 | text | `` | 19 | does this path exist at all? |
| `139-ports` | O | A | 11000 | `/Devices` | 404 | 7 | text | `` | 19 | does this path exist at all? |
| `140-ports` | O | A | 11000 | `/Zones` | 404 | 10 | text | `` | 19 | does this path exist at all? |
| `141-ports` | O | A | 11000 | `/Groups` | 404 | 8 | text | `` | 19 | does this path exist at all? |
| `142-ports` | I | | | *analysis* | | | | | | **/ui/Configuration advertises 11 URIs** |
| `143-ports` | I | A | 11000 | `/ui/Home` | 200 | 21 | xml | `screen` | 19588 | server-driven UI surface |
| `144-ports` | I | A | 11000 | `/ui/RecentlyPlayed` | 200 | 35 | xml | `screen` | 89658 | server-driven UI surface |
| `145-ports` | I | A | 11000 | `/ui/News` | 200 | 9 | xml | `screen` | 271 | server-driven UI surface |
| `146-ports` | I | A | 11000 | `/ui/Favourites` | 200 | 13 | xml | `screen` | 1137 | server-driven UI surface |
| `147-ports` | I | A | 11000 | `/ui/Sources` | 200 | 17 | xml | `screen` | 3286 | server-driven UI surface |
| `148-ports` | I | A | 11000 | `/ui/Search` | 200 | 9 | xml | `screen` | 1280 | server-driven UI surface |
| `149-ports` | I | A | 11000 | `/ui/nowPlayingCM` | 200 | 11 | xml | `contextMenu` | 2109 | server-driven UI surface |
| `150-ports` | I | A | 11000 | `/ui/queueItemCM` | 400 | 9 | text | `` | 41 | server-driven UI surface |
| `151-ports` | I | A | 11000 | `/ui/resolveSoviURL` | 400 | 8 | text | `` | 21 | server-driven UI surface |
| `152-ports` | I | A | 11000 | `/ui/Queue` | 200 | 20 | xml | `queue` | 10182 | server-driven UI surface |
| `153-ports` | I | A | 11000 | `/ui/presets` | 200 | 10 | xml | `screen` | 1309 | server-driven UI surface |

### ports -- analysis detail

**/ui/Configuration advertises 11 URIs** (`142-ports`)

```
/ui/Home, /ui/RecentlyPlayed, /ui/News, /ui/Favourites, /ui/Sources, /ui/Search, /ui/nowPlayingCM, /ui/queueItemCM, /ui/resolveSoviURL, /ui/Queue, /ui/presets
```

## suite: settings

| id | v | player | port | request | status | ms | type | root | bytes | note |
|---|---|---|---|---|---|---|---|---|---|---|
| `394-settings` | O | A | 11000 | `/Settings?schemaVersion=35` | 301 | 11 | xml | `a` | 84 | redirect from 11000 to 11001 (do NOT follow automatically) |
| `395-settings` | I | A | 11001 | `/Settings?schemaVersion=35` | 200 | 15 | xml | `settings` | 2070 | whole settings tree |
| `396-settings` | O | B | 11000 | `/Settings?schemaVersion=35` | 301 | 12 | xml | `a` | 84 | redirect from 11000 to 11001 (do NOT follow automatically) |
| `397-settings` | I | B | 11001 | `/Settings?schemaVersion=35` | 200 | 11 | xml | `settings` | 2069 | whole settings tree |
| `398-settings` | O | C | 11000 | `/Settings?schemaVersion=35` | 301 | 10 | xml | `a` | 84 | redirect from 11000 to 11001 (do NOT follow automatically) |
| `399-settings` | I | C | 11001 | `/Settings?schemaVersion=35` | 200 | 12 | xml | `settings` | 2069 | whole settings tree |
| `400-settings` | O | D | 11000 | `/Settings?schemaVersion=35` | 301 | 16 | xml | `a` | 84 | redirect from 11000 to 11001 (do NOT follow automatically) |
| `401-settings` | I | D | 11001 | `/Settings?schemaVersion=35` | 200 | 20 | xml | `settings` | 2070 | whole settings tree |
| `402-settings` | I | A | 11001 | `/Settings?schemaVersion=0` | 200 | 12 | xml | `settings` | 1946 | schemaVersion=0: what appears and disappears |
| `403-settings` | I | A | 11001 | `/Settings?schemaVersion=15` | 400 | 10 | text | `` | 32 | schemaVersion=15: what appears and disappears |
| `404-settings` | I | A | 11001 | `/Settings?schemaVersion=25` | 400 | 35 | text | `` | 32 | schemaVersion=25: what appears and disappears |
| `405-settings` | I | A | 11001 | `/Settings?schemaVersion=28` | 200 | 11 | xml | `settings` | 1946 | schemaVersion=28: what appears and disappears |
| `406-settings` | I | A | 11001 | `/Settings?schemaVersion=34` | 200 | 13 | xml | `settings` | 1946 | schemaVersion=34: what appears and disappears |
| `407-settings` | I | A | 11001 | `/Settings?schemaVersion=35` | 200 | 13 | xml | `settings` | 2070 | schemaVersion=35: what appears and disappears |
| `408-settings` | I | A | 11001 | `/Settings?schemaVersion=36` | 200 | 11 | xml | `settings` | 2070 | schemaVersion=36: what appears and disappears |
| `409-settings` | I | A | 11001 | `/Settings?schemaVersion=40` | 200 | 16 | xml | `settings` | 2070 | schemaVersion=40: what appears and disappears |
| `410-settings` | I | A | 11001 | `/Settings?schemaVersion=99` | 200 | 16 | xml | `settings` | 2070 | schemaVersion=99: what appears and disappears |
| `411-settings` | I | A | 11001 | `/Settings` | 200 | 14 | xml | `settings` | 2070 | no schemaVersion at all |
| `412-settings` | I | A | 11001 | `/Settings?id=audio&schemaVersion=35` | 200 | 15 | xml | `settings` | 4753 | settings page: audio |
| `413-settings` | I | A | 11001 | `/Settings?id=capture&schemaVersion=35` | 200 | 11 | xml | `settings` | 1682 | settings page: capture |
| `414-settings` | I | A | 11001 | `/Settings?id=player&schemaVersion=35` | 200 | 11 | xml | `settings` | 1385 | settings page: player |
| `415-settings` | I | A | 11001 | `/Settings?id=library&schemaVersion=35` | 200 | 11 | xml | `settings` | 1489 | settings page: library |
| `416-settings` | I | A | 11001 | `/Settings?id=alarms&schemaVersion=35` | 404 | 11 | text | `` | 26 | settings page: alarms |
| `417-settings` | I | A | 11001 | `/Settings?id=sleep&schemaVersion=35` | 404 | 10 | text | `` | 26 | settings page: sleep |
| `418-settings` | I | A | 11001 | `/Settings?id=network&schemaVersion=35` | 404 | 12 | text | `` | 26 | settings page: network |
| `419-settings` | I | A | 11001 | `/Settings?id=managePlaylists&schemaVersion=35` | 200 | 12 | xml | `settings` | 598 | settings page: managePlaylists |
| `420-settings` | I | A | 11001 | `/Settings?id=bluetooth&schemaVersion=35` | 200 | 32 | xml | `settings` | 1286 | settings page: bluetooth |
| `421-settings` | I | A | 11001 | `/Settings?id=upgrade&schemaVersion=35` | 404 | 11 | text | `` | 26 | settings page: upgrade |
| `422-settings` | I | A | 11001 | `/Settings?id=about&schemaVersion=35` | 404 | 8 | text | `` | 26 | settings page: about |
| `423-settings` | O | A | 11001 | `/Status` | 404 | 26 | text | `` | 19 | does 11001 serve anything but settings? |
| `424-settings` | O | A | 11001 | `/SyncStatus` | 404 | 7 | text | `` | 19 | does 11001 serve anything but settings? |
| `425-settings` | O | A | 11001 | `/Shares` | 404 | 9 | text | `` | 19 | does 11001 serve anything but settings? |
| `426-settings` | O | A | 11001 | `/ui/Configuration` | 404 | 34 | text | `` | 19 | does 11001 serve anything but settings? |
| `427-settings` | O | A | 11001 | `/Services` | 404 | 12 | text | `` | 19 | does 11001 serve anything but settings? |

## suite: stability

| id | v | player | port | request | status | ms | type | root | bytes | note |
|---|---|---|---|---|---|---|---|---|---|---|
| `436-stability` | I | A | 11000 | `/Services` | 200 | 52 | xml | `services` | 62497 | repeatability pass 1 |
| `437-stability` | I | A | 11000 | `/Services` | 200 | 29 | xml | `services` | 62497 | repeatability pass 2 |
| `438-stability` | I | B | 11000 | `/Services` | 200 | 51 | xml | `services` | 62497 | repeatability pass 1 |
| `439-stability` | I | B | 11000 | `/Services` | 200 | 29 | xml | `services` | 62497 | repeatability pass 2 |
| `440-stability` | I | C | 11000 | `/Services` | 200 | 64 | xml | `services` | 62497 | repeatability pass 1 |
| `441-stability` | I | C | 11000 | `/Services` | 200 | 34 | xml | `services` | 62497 | repeatability pass 2 |
| `442-stability` | I | D | 11000 | `/Services` | 200 | 63 | xml | `services` | 62497 | repeatability pass 1 |
| `443-stability` | I | D | 11000 | `/Services` | 200 | 88 | xml | `services` | 62497 | repeatability pass 2 |
| `444-stability` | O | | | *analysis* | | | | | | **/Services on A is byte-stable across calls: yes** |
| `445-stability` | O | | | *analysis* | | | | | | **/Services on B is byte-stable across calls: yes** |
| `446-stability` | O | | | *analysis* | | | | | | **/Services on C is byte-stable across calls: yes** |
| `447-stability` | O | | | *analysis* | | | | | | **/Services on D is byte-stable across calls: yes** |
| `448-stability` | I | | | *analysis* | | | | | | **/Services is byte-identical across players: no (expected: sid and ordering differ)** |
| `449-stability` | I | | | *analysis* | | | | | | **/Status etag over 3 idle reads: stable** |
| `450-stability` | I | | | *analysis* | | | | | | **/SyncStatus etag=523 syncStat=523 (numeric, and equal?)** |

### stability -- analysis detail

**/Services on A is byte-stable across calls: yes** (`444-stability`)

```
020000000076 020000000076
```

**/Services on B is byte-stable across calls: yes** (`445-stability`)

```
020000000077 020000000077
```

**/Services on C is byte-stable across calls: yes** (`446-stability`)

```
020000000078 020000000078
```

**/Services on D is byte-stable across calls: yes** (`447-stability`)

```
020000000079 020000000079
```

**/Services is byte-identical across players: no (expected: sid and ordering differ)** (`448-stability`)

```
A=020000000076; B=020000000077; C=020000000078; D=020000000079
```

**/Status etag over 3 idle reads: stable** (`449-stability`)

```
c6ce3689cc15613e c6ce3689cc15613e c6ce3689cc15613e
```

**/SyncStatus etag=523 syncStat=523 (numeric, and equal?)** (`450-stability`)

```
equal: True -- if these are always equal, a client needs to track only one
```

## suite: transport

| id | v | player | port | request | status | ms | type | root | bytes | note |
|---|---|---|---|---|---|---|---|---|---|---|
| `048-transport` | O | A | 11000 | `/Status` | 200 | 35 | xml | `status` | 1270 | path case sensitivity |
| `049-transport` | O | A | 11000 | `/status` | 404 | 10 | text | `` | 19 | path case sensitivity |
| `050-transport` | O | A | 11000 | `/STATUS` | 404 | 8 | text | `` | 19 | path case sensitivity |
| `051-transport` | O | A | 11000 | `/SyncStatus` | 200 | 10 | xml | `SyncStatus` | 410 | path case sensitivity |
| `052-transport` | O | A | 11000 | `/syncstatus` | 404 | 9 | text | `` | 19 | path case sensitivity |
| `053-transport` | O | A | 11000 | `/services` | 404 | 8 | text | `` | 19 | path case sensitivity |
| `054-transport` | O | A | 11000 | `/Services` | 200 | 104 | xml | `services` | 62497 | path case sensitivity |
| `055-transport` | O | B | 11000 | `/status` | 404 | 9 | text | `` | 19 | case sensitivity spot check on a second player |
| `056-transport` | O | B | 11000 | `/Status` | 200 | 11 | xml | `status` | 1254 | case sensitivity spot check on a second player |
| `057-transport` | O | A | 11000 | `/NoSuchEndpointXyz` | 404 | 8 | text | `` | 19 | unknown path: 404 shape and content-type per port |
| `058-transport` | O | A | 11001 | `/NoSuchEndpointXyz` | 404 | 10 | text | `` | 19 | unknown path: 404 shape and content-type per port |
| `059-transport` | O | A | 80 | `/NoSuchEndpointXyz` | 404 | 8 | none | `` | 0 | unknown path: 404 shape and content-type per port |
| `060-transport` | I | A | 11000 | `/Status/` | 404 | 14 | text | `` | 19 | path/query normalisation |
| `061-transport` | I | A | 11000 | `//Status` | 301 | 8 | xml | `a` | 42 | path/query normalisation |
| `062-transport` | I | A | 11000 | `/Status?` | 200 | 9 | xml | `status` | 1270 | path/query normalisation |
| `063-transport` | I | A | 11000 | `/Status?&` | 200 | 10 | xml | `status` | 1270 | path/query normalisation |
| `064-transport` | I | A | 11000 | `/Status?timeout=0` | 200 | 10 | xml | `status` | 1270 | path/query normalisation |
| `065-transport` | I | A | 11000 | `/Status?nosuchparam=1` | 200 | 10 | xml | `status` | 1270 | unknown parameter is ignored? |
| `066-transport` | I | A | 11000 | `/Status?timeout=1&timeout=2` | 200 | 10 | xml | `status` | 1270 | duplicated parameter: first or last wins? |
| `067-transport` | I | A | 11000 | `/Status?timeout=` | 200 | 12 | xml | `status` | 1270 | blank value (client drops these; does the device?) |
| `068-transport` | I | A | 11000 | `HEAD /Status` | 200 | 9 | none | `` | 0 | method handling on a GET endpoint |
| `069-transport` | I | A | 11000 | `OPTIONS /Status` | 200 | 12 | xml | `status` | 1270 | method handling on a GET endpoint |
| `070-transport` | I | A | 11000 | `POST /Status` | 200 | 43 | xml | `status` | 1270 | method handling on a GET endpoint |
| `071-transport` | I | A | 11000 | `OPTIONS /Status` | 200 | 10 | xml | `status` | 1270 | CORS preflight on the control port |
| `072-transport` | I | A | 11000 | `/Status` | 200 | 11 | xml | `status` | 1270 | CORS: simple GET with an Origin header |
| `073-transport` | I | A | 11000 | `/Status` | 200 | 10 | xml | `status` | 1270 | with X-Sovi-* schema headers |
| `074-transport` | I | A | 11000 | `/Status` | 200 | 10 | xml | `status` | 1270 | without X-Sovi-* schema headers |
| `075-transport` | I | A | 11000 | `/Services` | 200 | 27 | xml | `services` | 62497 | /Services with schema headers |
| `076-transport` | I | A | 11000 | `/Services` | 200 | 28 | xml | `services` | 62496 | /Services without schema headers |
| `077-transport` | I | | | *analysis* | | | | | | **omitting the X-Sovi-* headers changes /Services: YES** |
| `078-transport` | O | | | *analysis* | | | | | | **schema-version headers change the response body: no** |
| `079-transport` | I | A | 11000 | `/Services` | 200 | 42 | xml | `services` | 62497 | X-Sovi-Schema-Version=25 gating of /Services |
| `080-transport` | I | A | 11000 | `/Services` | 200 | 50 | xml | `services` | 62497 | X-Sovi-Schema-Version=99 gating of /Services |
| `081-transport` | I | A | 11000 | `/Services` | 200 | 52 | text | `` | 16542 | does the device compress? (matters for /Services at ~62 KB) |
| `082-transport` | I | A | 11000 | `/Status` | 200 | 10 | xml | `status` | 1270 | Connection: close honoured |

### transport -- analysis detail

**omitting the X-Sovi-* headers changes /Services: YES** (`077-transport`)

```
with=020000000005 without=020000000006 (digests are of the redacted bodies, which is a valid comparison because redaction is deterministic)
```

**schema-version headers change the response body: no** (`078-transport`)

```
with=020000000007 without=020000000007
```

## Bodies

Response bodies are in `raw/`, one file per probe id, alongside a
`.head.txt` with the status line and response headers. Binary
bodies (artwork) are not stored: only their length, content type
and first bytes are recorded here, so no embedded metadata can
leak. Their SHA-256 is in the do-not-share key file, not in this
bundle.
