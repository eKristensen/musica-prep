# Element and attribute inventory

Harvested automatically from every XML body captured in this run.
Values are already redacted. Counts are occurrences across all
captures for that endpoint, so an attribute with a low count
relative to its element is optional in practice.

Compare this against the response-shape tables in the
specification: anything here that is not documented there is a
gap, and anything documented that never appears here is either
conditional or historical.

## `/SetMaster`

| element path | n | attributes (n) | sample text |
|---|---|---|---|
| `SyncStatus` | 12 | `brand`(12), `class`(12), `db`(12), `etag`(12), `group`(4), `hasSubwoofer`(5), `icon`(12), `id`(12), `initialized`(12), `mac`(12), `model`(12), `modelName`(12), `name`(12), `schemaVersion`(12), `syncStat`(12), `version`(12), `volume`(12) | - |
| `SyncStatus/bluetoothOutput` | 12 | - | - |
| `SyncStatus/master` | 1 | `port`(1) | `192.0.2.11` |
| `SyncStatus/pairWithSub` | 12 | - | - |
| `SyncStatus/slave` | 4 | `icon`(4), `id`(4), `model`(4), `name`(4), `port`(4) | - |

<details><summary>attribute value samples</summary>

- `SyncStatus@brand` = `Bluesound`
- `SyncStatus@class` = `streamer`
- `SyncStatus@db` = `-34`, `-26.9`, `-27`
- `SyncStatus@etag` = `182`, `186`, `946`
- `SyncStatus@group` = `Stue+Kontor`, `Kontor+Køkken`
- `SyncStatus@hasSubwoofer` = `true`
- `SyncStatus@icon` = `/images/players/N125_sub.png`, `/images/players/N125_nt.png`
- `SyncStatus@id` = `192.0.2.11:11000`, `192.0.2.12:11000`
- `SyncStatus@initialized` = `true`
- `SyncStatus@mac` = `02:00:00:00:00:0B`, `02:00:00:00:00:0C`
- `SyncStatus@model` = `N132`, `N130`
- `SyncStatus@modelName` = `NODE`
- `SyncStatus@name` = `Stue`, `Kontor`
- `SyncStatus@schemaVersion` = `34`
- `SyncStatus@syncStat` = `182`, `186`, `946`
- `SyncStatus@version` = `4.16.22`
- `SyncStatus@volume` = `46`, `28`, `27`
- `SyncStatus/master@port` = `11000`
- `SyncStatus/slave@icon` = `/images/players/N125_nt.png`
- `SyncStatus/slave@id` = `192.0.2.12`, `192.0.2.13`
- `SyncStatus/slave@model` = `N130`, `N132`
- `SyncStatus/slave@name` = `Kontor`, `Køkken`
- `SyncStatus/slave@port` = `11000`

</details>
