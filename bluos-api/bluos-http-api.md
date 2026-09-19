# BluOS player HTTP API

A complete description of the protocol spoken by BluOS players (Bluesound, NAD,
DALI and others). Mostly HTTP, plus the UDP discovery protocol in §12, which is
not HTTP but is what a client needs before any HTTP is possible.

**Sources.** Every source this document is built from, roughly in order of
authority:

| Source | Version | Role |
|---|---|---|
| BluOS Controller for Android | 4.16.2 (`sovi-bls-v4.16.2-b3217_release`), jadx 1.5.3 | Widest endpoint coverage; SAX handlers give exact element/attribute names |
| BluOS Controller for Windows | 4.16.0 (Electron/Vue, asar) | Independent parser; confirms shapes and adds fields Android ignores |
| BluOS Controller for macOS | 4.16.0 (same build; ships original TypeScript in its sourcemap) | Authoritative source-level detail for discovery and authentication |
| *BluOS Custom Integration API* | v1.7, 09/04/2025 | Vendor spec for integrators; a deliberate subset, plus `/Browse` |
| BluOS RTI driver | 2.60 | Lenbrook-authored; ships readable JavaScript. Uses `/Browse` and `/Load` |
| BluOS Integration Utility | 1.8.1 (Qt/C++) | Endpoint strings for `/Sleep?minutes=`, `/GetSettings`, `/Reindex` |
| BluOS Crestron / NICE / GIRA / Control4 drivers | various | Mostly compiled or encrypted; confirm CI580 port offsets |
| pyblu | Python | Independent parser; ships **captured device responses** for the audio settings page (N130 and N331, schema 28) |
| Blu4Net | .NET | Independent parser; second non-controller client using `/Browse`. Only source that documents the polymorphic play response |
| bluos-api-rs | Rust | Small independent client; sole source for the `/Play?inputType=` form |
| bluos-dashboard | Python/FastAPI | Operationally the most experienced source: orphaned-group recovery, the legacy `/Sync` endpoint, redirect and pooling behaviour |
| BluShepherd | Swift, 2016 | Historical notes at schema 15 / firmware 2.8.3. Useful for what has **not** changed, and for `/Artwork` response headers |
| nightvision | Node.js | Dedicated LSDP implementation. Ships **real captured packets** as test fixtures — the source of the worked Announce in §12.1 |
| lsdp (Rust) | Rust | Second dedicated LSDP implementation; independent confirmation of the wire format, and the IPv6 address case |
| blucli, bluos-controller | Go, Python | CLI clients. Corroborate the core endpoint set; added nothing new |
| [“Bluesound API decoded” forum thread](https://web.archive.org/web/20190723114444/https://helpdesk.bluesound.com/discussions/viewtopic.php?t=2293) | Nov 2015 | The original public reverse-engineering post, cited by most third-party projects. Cited below as **2015 forum**. The helpdesk site is gone; the link is the web archive snapshot. Historical corroboration only |
| BluShell | PowerShell, schema 25 | Ships **45 sample responses**, several for endpoints never captured locally — `/Alarms`, `/audiomodes`, `/Artwork`, `/Search`, `/RadioPresets` |
| BluOsNadRemote, bluesoundplayer | C#/MAUI, Dart | Consumer apps. The first wraps Blu4Net; neither added anything. Two endpoints from the second were **rejected** — see below |
| blutui (Rust) | Rust TUI | Sole source for `/proxyToSlave` and `/diagnostics`, and for POST-with-form setting writes |
| blutui (Go) | Go TUI | Browse-key forms including `bySection` and `browseIsFavouritesContext` |
| bluos (Home Assistant, Pimmeke1989) | Python | Grouping notes; two claims left out as unverified |
| Home Assistant core `bluesound` | Python | Official HA integration, built on pyblu. Corroborates the independent leader/follower model and adds a fourth long-poll data point |
| bluesound_alt | Python | Independent HA integration. Uses `/Browse` to build its source list and `/Volume` to read a follower's own level |
| Hardware testing | — | Bluesound N110 / N130 / N132, firmware 4.16.22, schema 34 |

**Confidence markers:**
- **[V]** verified — read directly in client code, stated in the vendor spec, or
  observed on hardware.
- **[V hardware]** observed directly on these players, with a row in §17.1.
- **[V official]** read out of a first-party Controller build (macOS 4.16.0
  Electron bundle, or Android 4.16.2 `com.lenbrook.sovi`).
- **[S]** a captured sample exists. Orthogonal to the others: `[V][S]` is normal
  and desirable. A sample shows what arrives; a confidence marker says how far
  to trust the claim.
- **[T]** third-party — reported by an independent library, plausible but not
  corroborated by a first-party source or by hardware. **Treat as a lead to
  test, not as fact.** §17 lists every one of them with its evidence.
- **[U]** unverified — device-side behaviour no source reveals. Test first.

Where a client is named (Android, Windows) it is because the clients differ and
the difference is worth knowing when choosing values. Where nothing is named,
all sources agree.

The macOS and Windows builds are the same application; the macOS `app.asar`
embeds the main process's original TypeScript, including comments, which is
where the discovery and authentication detail in §12 and §1.1 comes from.

**Contents.** §0 parsing conventions and the error envelope · §1 transport,
auth, headers, timeouts · §2 player state · §3–7 transport, volume, grouping,
presets, queue · §8 browsing · §9 artwork · §10 settings and misc · §11 every
response shape · §12 **discovery (LSDP and mDNS)** · §13 the port 80 surface · §14 group topology ·
§15 the vendor Custom Integration API and `/Browse` · §16 what remains
untested.

---

## 0. Reading this document

The SAX handlers all extend `AbstractXmlHandler`, which normalises SAX
callbacks into two methods:

```java
elementStarted(String localName, Attributes attrs)   // from startElement
elementEnded(String localName, String textContent)   // from endElement
```

`inElement("x")` tests whether `x` is anywhere on the open-element stack, so
nesting is matched loosely — a handler that checks `inElement("song")` will
accept `<song>` at any depth.

Three parsing helpers recur and their sentinel values matter **[V]**:

| Helper | Blank / unparseable input returns |
|---|---|
| `parseInt` | `-2` |
| `parseFloat` (rounds to long) | `-1` |
| `parseNumericBoolean` | `true` only for the exact string `"1"` |

So a `-2` in a parsed integer field means "absent or malformed", not a real
value. Booleans are inconsistent across the protocol: some are `"1"`/`"0"`,
others are `"true"`/`"false"`. Each table below states which.

### 0.1 The universal error envelope **[V]**

`AbstractXmlHandler.startElement` special-cases a root element named `error`.
**Any** endpoint can return this instead of its normal payload, and every
handler in the app inherits the behaviour:

```xml
<error type="...">
  <message>Human readable message</message>
  <detail>First detail line</detail>
  <detail>Second detail line</detail>
  <button label="Retry" url="/SomePath" externalBrowse="true"/>
</error>
```

| Element / attribute | Notes |
|---|---|
| `error@type` | Error class string. |
| `message` | Text content. |
| `detail` | Repeatable; the client concatenates multiple occurrences with `\n`. |
| `button@label` | Button caption. |
| `button@url` | Target URL. |
| `button@externalBrowse` | `"true"` opens outside the in-app browser. |

Once the root is `error`, the handler stops dispatching to `elementStarted` /
`elementEnded` entirely — no partial payload is parsed. A client must check
the root element name before anything else.

**Some failures return HTML, not XML [V hardware].** `/Preset?id=<n>` for a
preset that does not exist answers `<h1>Preset Not Found</h1>` — no XML
declaration, no `<error>` root. A client must not assume every 200 response
parses as XML; check that the body starts with `<?xml` or that the root element
is one you expect, and treat anything else as an error.

**An unknown path returns a bare HTTP 404, not an error envelope [V hardware].**
The body is `404 page not found` as `text/plain; charset=utf-8` with
`X-Content-Type-Options: nosniff` — Go's `net/http` default, confirming the
`ms-go` server. So a client distinguishes "endpoint does not exist on this
firmware" (404, plain text) from "endpoint exists and refused" (200 with an
`<error>` root). Probing for optional endpoints is therefore cheap and
unambiguous.

Separately, HTTP-level failures are turned into the same `ResultError` type:
`code` is the HTTP status, and on **HTTP 500 only** the response body is
captured as the error detail. **401** means unauthorised.

---

### 0.4 Hardware verification

Claims marked **[V hardware]** were tested with `bluos-probe`, a harness that
issues each check the way its source describes it — including the port — and
records the request, the response and a verdict. Two lessons are baked into it
and are worth repeating here:

- **HTTP 200 means nothing on a write.** BluOS answers 200 to parameters it
  ignores, and a `/Play` carrying unrecognised parameters degenerates into a
  bare `/Play`, which resumes playback. Against a paused player that is
  indistinguishable from success. Every state-changing claim in §17.1 is judged
  by reading the state back, never by the status line.
- **A claim is not settled until it is tested as its source describes it.**
  `/diagnostics` came from one third-party project, was reported as failing, and
  is real — the check had been aimed at port 11000 instead of 80.

## 1. Transport basics **[V]**

```
http://<ip>:<port>/<Action>?<param>=<value>&...
```

- Plain HTTP (`FORMAT_HOST_PATH = "http://%s:%d/%s"`). No TLS.
- Default port **11000** (`Host.DEFAULT_PORT`). The NAD **CI580** is the
  documented exception: four streamer nodes share one chassis and IP, on ports
  **11000 / 11010 / 11020 / 11030**. The Crestron driver exposes exactly this
  as an "Output 1–4" parameter with values 0/10/20/30 added to the base port.
  This is why `port` accompanies every address in the grouping and topology
  calls, and why discovery must read the advertised port rather than assuming
  11000.
- Responses are **XML**. One exception: `/GetSettings` returns **JSON**
  (§10.1). Everything else in this document is XML.
- HTTP **204** is treated as success with no content.

### 1.1 Authentication — Digest, not "none" **[V]**

Players may require **HTTP Digest authentication**.
On Android, `WebServiceCall.authenticatorProcessor()` extracts the host from the request
URL and, if `Authenticators.get(host)` holds credentials, rebuilds the client
with an okhttp `DigestAuthenticator` plus an authentication cache.

The desktop controllers use the platform HTTP stack's own authentication
handling, so **Basic and Digest are both accepted** at the transport level;
which one a given player demands is up to the player.

Two behaviours worth copying **[V]**:
- Credentials are cached and replayed automatically for a bounded number of
  challenges (the desktop clients allow two) before the user is prompted again.
  This is needed because of the port 80 redirect described in §13.
- The credential cache is scoped to the currently selected player group and is
  **cleared when the selected group changes**. Do not carry credentials from
  one player to another.

A player that answers 401 is treated as present but not selectable
(`syncStatus.setAuthorized(false)`); `canGroup()` and player selection both
require `isAuthorized`.

### 1.2 Methods — GET plus four POST paths **[V]**

Most calls are GET with query parameters. Four are not:

| Class | Method | Body | Target |
|---|---|---|---|
| `WSCReorderPresets` | POST | `application/json` | device-supplied URL |
| `WSCDynamicSettings` | POST when params present, GET when empty | url-encoded form | device-supplied URL |
| `WSCUpdateSetting` | POST | url-encoded form | device-supplied URL |
| `WSCUploadFile` | POST | `multipart/form-data`, part name `file` | device-supplied URL |

There is no literal `/UploadFile` path in the app.

### 1.3 Timeouts and concurrency **[V]**

`NORMAL_TIMEOUT_IN_MILLIS = 15000` is a sentinel, not an effective value:
`getOkHttpClient(j)` returns the shared client unchanged when `j == 15000`,
and that shared client is built with `connectTimeout 5 s, readTimeout 60 s`.

| Setting | Value |
|---|---|
| Connect timeout | 5 s |
| Default read timeout | 60 s |
| `setLongTimeOut()` | 200 s (`LONG_TIMEOUT_IN_MILLIS = 200000`) |
| `/Status` long-poll read timeout | 105 s (set explicitly by `WSCStatus`) |
| Dispatcher max requests | 256 |
| Dispatcher max requests **per host** | 16 |

**Browser clients have a much lower ceiling than the device does.** HTTP/1.1
browsers allow roughly **six connections per host**, so a web UI that holds a
`/Status` long-poll per player will starve its own fetches — `bluos-dashboard`
records exactly this as a cause of spurious request timeouts on transport
controls. Long polls belong on a server that fans out to the browser over one
connection (SSE or WebSocket), which is the same reason §9 recommends proxying
artwork.

The 16-per-host cap is self-imposed by the client, not forced by the device.
**A player holds at least 24 simultaneous long-polls without difficulty
[V hardware]:** 24 concurrent `/Status?timeout=30` requests with a valid etag
all returned 200 at 30.05–30.10 s, i.e. every connection was held for the full
timeout and released on schedule. There is no low connection cap to design
around. The true ceiling is above 24 and was not probed.

### 1.4 Request headers **[V]**

Sent on every request by `SoviHeaderInterceptor` and `UserAgentInterceptor`:

| Header | Value |
|---|---|
| `X-Sovi-Schema-Version` | `35` (hard-coded in 4.16.2) |
| `X-Sovi-Ui-Schema-Version` | `7` (hard-coded) |
| `X-Sovi-Ui-Autofill` | `1` or `0`, from a local preference |
| `X-Sovi-Tz` | Android timezone ID, e.g. `Europe/Copenhagen` |
| `X-Sovi-Ui-Context` | Only when a context string is currently held |
| `Accept-Language` | e.g. `en-GB`, lowercase language + uppercase region |
| `User-Agent` | `Bluesound/<version> (Model: <device>; Android <release>)` |

A device may behave differently, or refuse newer response shapes, if the
schema-version headers are absent. Send them.

### 1.5 Response headers the client reads **[V]**

| Header | Use |
|---|---|
| `x-sovi-ui-context` | Stored and echoed back as `X-Sovi-Ui-Context` on later requests. |
| `content-location` | Cached per request path+query in `ContentLocationCache`. |

### 1.6 Paths are case-sensitive **[V hardware]**

Routing matches the path exactly. Confirmed identically on three players
(N110, N130, N132, firmware 4.16.22):

| Path | Result |
|---|---|
| `/Status` | 200 |
| `/status`, `/STATUS` | 404 |
| `/SyncStatus` | 200 |
| `/syncstatus` | 404 |
| `/upgrade` | 200 |
| `/Upgrade` | 404 |

So the mixed casing in this document is load-bearing, not cosmetic. Most
endpoints are PascalCase; `/upgrade`, `/update`, `/audiomodes` and the `/ui/…`
prefix are genuinely lowercase.

### 1.7 Query-string encoding **[V]**

`RequestParams.toQueryString`:
- Parameters with blank values are **dropped entirely**.
- Values are `Uri.encode`d after all line separators are stripped.
- A key that itself contains `=` is emitted raw, as a pre-formed fragment.

### 1.8 Client-side cache parameters — not protocol **[V]**

`RequestCache` injects `__cache_session__` and `__cache_session_duration__`
query parameters, uses them to synthesise `Cache-Control` on the way out, then
**strips them before the request reaches the device**. If you see these in a
capture they are app-internal. Do not implement them.

### 1.9 Long-poll convention **[V]**

`/SyncStatus`, `/Status` and `/BTDevices` support etag long-polling. The
response carries an `etag` attribute; send it back on the next request and the
player holds the connection until state changes or `timeout` seconds elapse.

**Only a currently-valid etag causes the connection to be held [V hardware].**
Omitting `etag`, or sending a stale or invented one, returns the current state
**immediately** with a 200 — the player reads "your etag does not match" as
"you are already out of date, here is the answer". That is correct behaviour,
but it makes an easy trap: a client that mishandles the etag will poll as fast
as the network allows while appearing to long-poll. It also means a long-poll
load test must fetch a real etag first, or it measures nothing.

The `timeout` value is not uniform across endpoints or clients:

| Endpoint | `timeout` sent | Client read timeout | Pacing |
|---|---|---|---|
| `/SyncStatus` | `10` | 60 s (default) | ≥1 s enforced between polls |
| `/Status` | `100` | 105 s | none — bare `.repeat()` |
| `/BTDevices` | `100` | 60 s (default) | none |

The ≥1 s minimum gap exists only in the SyncStatus loop, and only when an etag
came back: `andSet > 1000 ? just(TRUE) : timer(max(1000 - andSet, 100) ms)`.
When no etag is returned the loop backs off to 10 s, or 1 s while upgrading.

---

## 2. Player state

| Endpoint | Params | Response root | Notes |
|---|---|---|---|
| `/SyncStatus` | `etag`, `timeout` | `<SyncStatus>` or `<UpgradeStatusStage1|2>` | §2.1 |
| `/Status` | `etag`, `timeout` | `<status>` | §2.2 |
| `/SetMaster` | `master`, `port` | `<SyncStatus>` | Slave-side grouping. See §5.1. |
| `/SetInitialized` | — | error envelope only | Marks a player as set up. |
| `/GitVersion` | — | `<version>` text | §2.5. Confirmed on hardware, port 11000. |
| `/Services` | — | `<services>` | Doubles as schema probe, §2.6 |
| `/Settings` | `id` | `<settings>` | Newer settings flow. |

`/Info` is **not** a fixed endpoint — `WSCInfo` builds its URL from a
`BrowseOptions`, so the path always comes from a previous browse response.
Same for `/DynamicSettings`.

### 2.1 `/SyncStatus` **[V]**

Identity and group topology. Changes rarely.

Root element `<SyncStatus>` (matched case-insensitively), attributes:

| Attribute | Type | Notes |
|---|---|---|
| `name` | string | Player name. |
| `id` | string | Usually `ip:port`. |
| `mac` | string | |
| `brand` | string | |
| `model` | string | Model code. |
| `modelName` | string | Display name. |
| `icon` | string | **Relative** path; client prefixes `http://<host>`. |
| `class` | string | Device class. `"streamer"` is a normal player; `"hub"` is a CB130 Control Hub and forces `schemaVersion` to 1 client-side. |
| `etag` | string | Long-poll token. |
| `group` | string | Read into both `group` and `groupName`. |
| `volume` | int | `-1` means fixed-volume. |
| `version` | string | Firmware version. |
| `schemaVersion` | int | |
| `initialized` | `"true"`/`"false"` | **Absent ⇒ treated as an old player**, not as false. |
| `channelMode` | string | |
| `zone` | string | Zone name; falls back to `group` for a zone master. |
| `zoneMaster` | `"true"` | |
| `zoneSlave` | `"true"` | Re-derived at end of parse as `master != null`. |
| `zoneController` | `"true"` | |
| `zoneUngroup` | string | |
| `managedZoneSlave` | `"true"` | |
| `pairSlaveOnly` | `"true"` | |
| `hasSubwoofer` | `"true"` | |
| `waitingToPair` | `"true"` | |
| `waitingToPairDuration` | int | |
| `port` | int | Only meaningful when `id` carries no `:port` suffix. |
| `channelName` | string | Human-readable channel label, alongside `channelMode`. |
| `distance` | float | Home-theatre speaker distance for this player. |

An `id` of `127.0.0.1` is a self-reference placeholder: substitute the address
you actually reached the player on.

Child elements:

| Element | Shape | Notes |
|---|---|---|
| `<master port reconnecting>` | text = master's IP | Present **only on a slave**. Blank text falls back to `1.2.3.4`. `port` defaults to 11000. |
| `<slave id port name model icon>` | empty | Repeatable. `id` is the IP. Present on a master. **The master describes its slaves**, not just their addresses — `name`, `model` and `icon` are included, so one `/SyncStatus` against a master is enough to render the whole group. |
| `<zoneSlave …>` | empty | Repeatable, see below. Distinct from `<slave>`. |
| `<slaveVolume min max step>` | text = current trim | Defaults `min=-10 max=10 step=0.5`. |
| `<externalSource id name isBluos>` | container | Selected source in the attributes. |
| `<externalSource><item id name isBluos>` | empty | Repeatable, the available inputs. |
| `<bluetoothOutput name codec>` | empty | Connected Bluetooth sink and its active codec. |
| `<zoneOptions multi>` | container | `multi` absent ⇒ true. |
| `<zoneOptions><option canHaveCentre zoneMaster>` | text = option name | Repeatable. |
| `<pairWithSub><model>` | text = model code | Repeatable list of pairable subs. |
| `<battery icon>` | empty | Relative icon path. |
| `<audioPresetUrl url>` | empty | Audio-preset settings page. Preferred over `soundbar_settings` when both are present. |
| `<soundbar_settings url>` | empty | **This is where `dynamicSettingsUrl` comes from** — it is not an attribute on `SyncStatus`. |
| `<lrSwap url testSound>` | empty | Both attributes required or the element is ignored. |

`<zoneSlave>` attributes: `id`, `port`, `name`, `model`, `modelName`, `icon`,
`distance`, `channelMode`, `channelName`, `zoneSubnet`, `upgrading`,
`zoneSlave`, `pairSlave`. An upgrading `<zoneSlave>` additionally nests its own
`<UpgradeStatusStage1>` / `<UpgradeStatusStage2>` (§2.1.1).
A `zoneSlave` whose `id` is the literal `10.1.2.3` is discarded as a
placeholder.

**Derived predicates [V]** (`SyncStatus`):
```
isSlave()  = master != null
isMaster() = master == null && slaves.isNotEmpty()
isNormal() = master == null && slaves.isEmpty()
```
`PlayerInfo` adds a subwoofer exclusion:
```
isMaster() = master == null && hasNormalSlaves() && !isSubwoofer()
```

**Three independent clients model these as separate booleans**, not as an
exclusive role: pyblu reads `leader` and `followers` independently, the Home
Assistant core integration derives `is_leader = followers is not None` and
`is_grouped = followers is not None or leader is not None`, and Blu4Net keeps
both. That is the correct model — a nested master reports both at once
(§14) — and it is the Android app's exclusive treatment that is the outlier.

#### 2.1.1 `/SyncStatus` has alternate root elements during upgrade **[V]**

While a player is upgrading,
`/SyncStatus` returns `<UpgradeStatusStage1>` or `<UpgradeStatusStage2>`
**instead of** `<SyncStatus>`. A client that only looks for `<SyncStatus>`
sees nothing at all during an upgrade.

| Root | Attributes | Child text elements |
|---|---|---|
| `<UpgradeStatusStage1>` | `name`, `model` | `format`, `error`, `abortable` |
| `<UpgradeStatusStage2>` | `name`, `model`, `class`, `pairSlaveOnly` | `format`, `total`, `step`, `percent`, `error`, `abortable`, `started` |

Inside a `<zoneSlave>`, the same two elements appear with a fuller attribute
set — `version`, `name`, `model`, `abortable`, `error`, `format`, `retry`,
`git`, and for stage 2 also `percent`, `started`, `step`, `total` — plus child
text elements `format`, `error`, `abortable`, `retry`, and for stage 2
`total`, `step`, `percent`, `started`, `git`.

Client-side derivations worth mirroring:
- `error` with text `"0"` is treated as no error.
- `isUpgrading() = upgradeStatusStage != 0`.
- When `step == total && percent == 100`, the stage is forced to 5.
- A master reports the *slowest* upgrading zone slave's progress as its own.

### 2.2 `/Status` **[V]**

Playback state. Changes constantly. Root element `<status>` with a single
attribute `etag`.

Typed child elements — these are the ones with dedicated handling:

| Element | Type | Notes |
|---|---|---|
| `volume` | int | **`-1` means fixed volume.** There is no `isFixedVolume` flag. |
| `state` | enum | Device sends `play`, `pause`, `stop`, `stream`, `connecting` and others. The app maps `play`/`pause`/`stream`/`connecting` and treats everything else — including `stop` — as idle. `play` and `stream` mean the same thing. |
| `shuffle` | `"1"`/`"0"` | |
| `repeat` | int | **0 = repeat all, 1 = repeat track, 2 = off.** Defaults to 2. |
| `song` | int | Index in the queue; `-1` on parse failure. |
| `secs` | float | Seek position, rounded to a long. |
| `totlen` | float | Track length. |
| `mode` | int | |
| `indexing` | int | `> 0` means the library is indexing. |
| `sleep` | string | Sleep-timer status. |
| `canSeek` | `"1"`/`"0"` | |
| `cursor` | int | |
| `url` | string | |
| `groupVolume` | int | **Presence of this element is `hasGroupVolume`.** |
| `groupName` | string | |
| `autofill` | int | |
| `canMovePlayback` | `"true"`/`"false"` | The one genuine boolean-flag element. |
| `noCoverBackground` | `"true"`/`"false"` | |
| `pid` | string | Play-queue id. Matches `playlist@id` in `/Playlist`; changes whenever the queue changes. |
| `prid` | string | Presets id. Matches `presets@prid`; changes when a preset changes, so cached `/Presets` should be purged. |
| `mid` | string | Metadata id. |

**`<syncStat>`** matches the `syncStat` attribute on `/SyncStatus` and changes
whenever sync status changes. Use it to avoid a second long poll: hold one poll
on `/Status`, and re-fetch `/SyncStatus` only when `<syncStat>` moves. That
halves open connections per player, which matters given the unknown device-side
connection limit (§16). The Windows client does this; the Android client
ignores `syncStat` and polls both endpoints.

**`secs` is excluded from the etag.** Playback progress does *not*
break a long poll and does not change the etag. A client must extrapolate the
position locally from the response timestamp while `state` is `play` or
`stream`. Without this, a progress bar will sit frozen for the whole 100 s
poll window.

Container elements:

| Element | Notes |
|---|---|
| `<actions>` | Wraps repeated `<action>`; see §2.3. |
| `<battery level charging icon>` | Only present on players with a battery. The app reads `icon` alone; the device also sends `level` (percent) and `charging` (`1` while charging). |

**Every other non-blank child element falls into a generic string map.** That
is how these arrive, and a client must not assume the list is closed:

`title1`, `title2`, `title3`, `twoline_title1`, `twoline_title2`, `album`,
`artist`, `work`, `image`, `currentImage`, `service`, `serviceIcon`,
`quality`, `streamFormat`, `streamUrl`, `dolbyProcessing`, `notifyurl`,
`fn`, `sid`, `songid`, `inputId`, `preset_id`, `preset_name`, `stationImage`,
`mute`, `schemaVersion`, `servicesVersion`, `presetsVersion`,
`playlistVersion`, `metaDataVersion`, `androidPackage`, `syncStat`, `name`,
`db`, `muteDb`, `muteVolume`, `alarmsecondsremaining`, `serviceName`,
`serviceType`, `settingsGroupId`, `isFavourite`, `songid`, `inputTypeIndex`,
`albumid`, `artistid`, `dirac`, `infourl`, `lyricsid`, `similarstationid`,
`trackstationid`, `mqaOFS`.

Blu4Net additionally parses `is_preset` and `preset_name` **[T]** — a flag and
label indicating that the current audio was started from a preset. `preset_name`
is corroborated by the Android client; `is_preset` is not, was not present
in any response captured here. Plausible, but read it defensively.

The last group is observed on firmware 4.16.22 and unread by any client:
`albumid` / `artistid` / `songid` are service-scoped ids usable with
`/Artwork` and `/Add`; `similarstationid` and `trackstationid` are ready-made
radio seeds (`Tidal:radio:artist/3937767`, `Tidal:radio:track/70813938`)
playable via `/Play?url=`; `infourl` and `lyricsid` point at track metadata;
`dirac` reports Dirac room correction; `mqaOFS` is the MQA original sample
rate, present when `quality` is `mqa`.

Three carry non-obvious handling:

- **`serviceName`** equal to `usb` (case-insensitive) overrides `service` with
  `usb`.
- **`isFavourite`** is `"1"`/absent, not a boolean string.
- **`inputTypeIndex`** echoes back the selector used by
  `/Play?inputTypeIndex=` (§15.2), so a client can tell which physical input
  is playing.

Three of these carry semantics worth honouring:

- **`title1` / `title2` / `title3`** are the canonical display lines. The
  official document is emphatic that a three-line now-playing UI must use
  these and **not** `album` / `artist` / `name`. Where present,
  `twoline_title1` / `twoline_title2` are the canonical two-line pair.
- **`streamUrl`** is a flag, not a value — treat its content as opaque. When
  present it means the play queue is *not* the audio source (`song` is
  meaningless), `shuffle` and `repeat` are irrelevant and should be hidden,
  and next/previous are unavailable except via `<actions>`.
- **`quality`** takes the fixed strings `cd`, `hd`, `dolbyAudio`, `mqa` and
  `mqaAuthored`; any numeric value is an approximate bitrate.

**Capability flags are derived, not transmitted [V]:**

| App-level flag | Actually derived from |
|---|---|
| `isFixedVolume` | `<volume>` text equals `-1` |
| `canMute` | `<mute>` present and its integer value ≥ 0 |
| `hasGroupVolume` | `<groupVolume>` element present |
| `isIndexing` | `<indexing>` > 0 |
| `hasNothingQueued` | `title1` absent |

None of these three is transmitted as an element. Do not look for them in the
XML.

### 2.3 `<actions>` / `<action>` **[V]**

Populated by `PlayerActionButton.fromAttributes`. Buttons are keyed by `name`,
and any button with a blank `name` is dropped.

| Attribute | Notes |
|---|---|
| `name` | Key. When `name == "cmItem"` the client keys it as `"cmItem" + type`. |
| `type` | Also participates in the key for `cmItem`. |
| `icon` | |
| `state` | int, default 0. |
| `text` | |
| `displayName` | |
| `notification` | |
| `count` | |
| `url` | |
| `interval` | |
| `androidPackage` | Android deep-link target. |
| `androidAction` | Android intent action. |
| `iosApp` | iOS deep-link target. |
| `desktopApp` | Desktop deep-link target. |
| `desktopInstall` | Desktop install URL. |
| `itunesUrl` | Store link. |
| `hide` | `"1"` hides the button. |

Known `name` values: `back`, `skip`, `love`, `ban`, and `shop` (§2.4).
A `type="thumbs"` marks love/ban as a paired rating control, and `state="-1"`
means "not yet rated".

Observed action URLs on firmware 4.16.22 show the `/Action` query is entirely
service-defined — the skip verb is not even called `skip`:

```
/Action?service=RadioParadise&next=2918553
/Action?service=RadioParadise&love=42445&reset=0
/Action?service=RadioParadise&ban=42445&reset=0
```

Take the `url` verbatim. Do not reconstruct it from the `name`.

### 2.4 The `shop` action side-fetch **[V]**

When `/Status` yields an action button named `shop`, the client fires a
**separate GET** to that button's `url` (10 s timeout) and parses the reply
with `ActionHandler`, which reads exactly one element:

```xml
<link>https://…</link>
```

The resulting URL replaces the button's `url` and is memoised in a single-entry
cache. A player implementation only needs this if it advertises a `shop`
action.

### 2.5 `/GitVersion` **[V]**

Returns a firmware build identifier as element text. Trivial handler.

### 2.6 `/Services` **[V]**

Enumerates available sources/services and doubles as the schema-version probe:
`WSCSchemaVersion` hits the same `/Services` path but parses only the schema
version out of it. See §8 — the service entries carry the `url` attributes the
whole browse tree hangs off.

---

## 3. Transport control **[V]**

All simple GETs; most return no useful body.

| Endpoint | Params | Notes |
|---|---|---|
| `/Play` | `seek`, `id`, `url`, `preset_id`, `image`, `title1`, `title2` | No params = resume. `seek` = jump to position, `id` = queue index; they combine, so `?seek=55&id=4` starts 55 s into queue entry 4. The radio/preset form sends the fuller set. |
| `/Pause` | `toggle=1` | **`toggle` is official-only** — toggles the pause state rather than forcing pause. |
| `/Stop` | — | **Official-only; absent from the app.** Returns `<state>stop</state>`. `/Play` resumes from `pause` but **not** from `stop`. |
| `/Skip` | — | Next track. |
| `/Back` | — | Previous track. |
| `/Shuffle` | `state=0\|1` | Returns `<playlist length id shuffle repeat/>`. **Not validated** — `state=3` or `4` is accepted silently and leaves the value unchanged. |
| `/Repeat` | `state=0\|1\|2` | **0 = all, 1 = track, 2 = off.** Returns `<playlist length id repeat/>`. **Validated** — any other value returns `<error><message>invalid state</message></error>`. |
| `/Sleep` | — | Cycles to the next sleep-timer value; returns the new value as text. |
| `/Sleep` | `minutes=<n>` | **Sets** the sleep timer to **any integer** — 5, 17, 90 and 120 are all accepted and echoed back, not only the 0/15/30/45/60 the Integration Utility offers. `minutes=0` cancels and returns an empty `<sleep></sleep>`. Prefer this over cycling. |
| `/MovePlayback` | `id=<target ip>`, `port` | Both required. |
| `/PlayTestSound` | `channel`, `sound`, `type`, `volume` | Speaker positioning. Returns `<testsound></testsound>`. Both parameter forms are accepted but **produce different sounds**: `sound=pinknoise` plays a short repeating alarm-like sequence; `sound=1&type=pinknoise&channel=0` plays actual pink noise. `sound` selects which test sound, `type` its character. Use the second form for speaker positioning. |
| `/Abort` | `slave`, `port` | Aborts a slave upgrade. |
| `/TryAgain` | `slave`, `port` | Retries a slave upgrade. |

---

## 4. Volume **[V]**

| Endpoint | Params | Notes |
|---|---|---|
| `/Volume` | `level=<0-100>` | Set absolute volume. |
| `/Volume` | `mute=1` mutes, `mute=0` unmutes | See the warning below. |
| `/Volume` | `level=…&tell_slaves=1` | Group volume. |
| `/Volume` | `abs_db=<db>` | **Official-only.** Absolute volume on a dB scale. |
| `/Volume` | `db=<±delta>` | **Official-only.** Relative dB change; this is how volume up/down is done (typically ±2 dB). |
| `/Volume` | *(no params)* | Reads the current volume. Supports long-polling. Used by `bluesound_alt` to read a follower's individual level, which differs from the group volume. |
| `/SlaveVolume` | `slave=<ip>`, `port`, `db=<value>` | Per-slave trim. |
| `/SlaveVolume` | `slave=<ip>:<port>`, `db=<value>` | **[T]** A combined-address variant used by `blutui`, matching the form `/proxyToSlave` takes. Untested. |

All variants are clamped to the player's configured volume range (typically
-80..0 dB), which is set in the Controller app under Settings → Player → Audio.

**`/Volume` returns a real body** that the app ignores (it treats volume as
fire-and-forget). For a mock player, the shape is:

```xml
<volume db="-49.9" mute="0" offsetDb="0" etag="6213…">15</volume>
```

Element text is the 0..100 level (`-1` = fixed).

Confirmed on firmware 4.16.22:

```xml
<volume db="-62.2" offsetDb="10" mute="0" etag="9e12351ae5fcdac65a5d201f53787375" source="">10</volume>
```

Attributes: `db`, `offsetDb`, `mute`, `etag`, `source`, plus `muteDb` and
`muteVolume` when muted. `source` is present but empty in normal playback.

> **Warning — an error in the official document.** The parameter table in
> §3.1 of the CI API states "If set to 0, the player is muted. If set to 1,
> the player is unmuted." That is inverted. Its own §3.4/§3.5, its worked
> example, and the Android app all agree that **`mute=1` mutes and `mute=0`
> unmutes**. Follow the app.

`/SlaveVolume` response **[V]** — root `<slaveVolume>`:

| Attribute | Default if absent |
|---|---|
| `min` | `-10` |
| `max` | `10` |
| `step` | `0.5` (parsed as `BigDecimal`) |

Element text is the current trim, parsed as a float.

A fixed-volume player reports `<volume>-1</volume>` in `/Status` and ignores
`level`.

---

## 5. Grouping **[V]**

Both calls are addressed **to the master**. `slaves` and `ports` are
comma-separated positional arrays of equal length.

```
GET /AddSlave?slave=<ip>&port=<port>                            # singular
GET /AddSlave?slaves=<ip>[,<ip>...]&ports=<port>[,<port>...]    # plural
GET /RemoveSlave?slave=<ip>&port=<port>
GET /RemoveSlave?slaves=<ip>[,<ip>...]&ports=<port>[,<port>...]
```

The app only ever emits the **plural** form. The singular `slave`/`port` form
is documented officially and is the simpler choice for a one-player call.

**`port` may be optional in the singular form [T].** The earliest public
descriptions of this API (2015) use `/AddSlave?slave=<ip>&group=<name>` and
`/RemoveSlave?slave=<ip>` with no `port` at all, presumably defaulting to 11000.
Untested on current firmware, and not worth relying on — send `port` explicitly,
if only because a CI580 needs it.

| Param | Applies to | Notes |
|---|---|---|
| `slaves`, `ports` | both | positional, comma-joined |
| `group=<name>` | AddSlave | group display name; blank/whitespace names are dropped |
| `force=1` | RemoveSlave | force removal |
| `channelMode`, `slaveChannelMode` | AddSlave | comma-joined; client throws if length ≠ slave count |
| `distance`, `slaveDistance` | AddSlave | same constraint |
| `pairSlave=1` | AddSlave | subwoofer/stereo pairing |

Zone variants (`addZoneSlave`, `addZoneSlaves`) set the 200 s long timeout;
plain `addSlaves` does not.

**Response shapes [official], and what the app does with them.** The app
discards both bodies, so these were invisible from the APK alone:

```xml
<addSlave><slave id="192.168.1.153" port="11000"></slave></addSlave>
```

**An empty `<addSlave></addSlave>` means the request was rejected [V hardware].**
The player answers 200 with no `<slave>` children rather than an error. This is
how a refused grouping call is signalled — most commonly when the target is
already a slave of some other master, which is a silent no-op. Check for the
presence of `<slave>` children, not just the HTTP status.

**A bare `/RemoveSlave` does not drop every slave [V hardware].** With two
slaves attached, a parameterless `/RemoveSlave` left both in place. The Home
Assistant integration's claim to the contrary (T-36a) is disconfirmed: a client
must name `slave`/`port` or `slaves`/`ports`.

**`force=` and the refusal path [V official].** The Controller removes with
`force=0` first, and on failure matches the error message
`Cannot move input source`, prompts the user to confirm, and retries. The
Android app carries a second string, `Cannot move a group while inserting`, and
a `newRetryRemoveMasterDialogFragment`. A client should expect a removal to be
refused when the slave is the group's active source, and should treat `force=1`
as the user-confirmed retry rather than a default.

`/RemoveSlave` returns a **full `<SyncStatus>` document** reflecting the new
topology. The app parses it with `ResultHandler`, which reads nothing but a
flat `<error>` element — so a genuinely useful response is thrown away. A
custom client should parse it and skip the follow-up `/SyncStatus` poll.

**Removing the primary from a group of three or more** ungroups the primary
and leaves the remaining secondaries as a new group. It does not dissolve the
group.

### 5.1 Orphaned groups **[T]**

When a primary leaves the network without being ungrouped, its slaves keep
reporting `<master reconnecting="true">` and stay stuck there. This is what the
`reconnecting` attribute of §2.1 is for, and it is a state a client will meet in
practice — any power cut to the primary produces it.

`bluos-dashboard` reports that a slave in this state **cannot free itself**: the
self-unjoin call returns

```xml
<error>no slave available as new master</error>
```

(flat `<error>` form, §11.1). Its recovery is a **reparent**: attach the orphan
to a live, standalone player with `/AddSlave`, then `/RemoveSlave` it from that
donor. The orphan ends up free. The same project warns to pick donors that are
themselves free — never a member of another group — or the repair spreads the
problem.

Untested here. If you implement group management, this is the failure mode
worth reproducing deliberately (T-29).

### 5.2 A legacy `/Sync` endpoint — absent on current firmware **[V hardware]**

Older firmware appears to have exposed grouping under a different endpoint:

```
GET /Sync?slave=<ip>       # add
GET /Sync?remove=<ip>      # remove
```

Note there is no `port` parameter. `bluos-dashboard` calls `/Sync` as a fallback
whenever `/AddSlave` or `/RemoveSlave` fails, which suggests it found real
devices needing it once. On 4.16.22 the bare path returns a clean 404 (§0.1) on
all three ports — see `C-05` in §17.1 — so a client of this generation has
nothing to fall back to, but the 404 costs nothing to hit.

That project also addresses `/RemoveSlave` **to the slave** when the master does
not answer, which the vendor document does not mention. Also untested.

### 5.3 `/SetMaster` — slave-side grouping **[V hardware]**

`/AddSlave` is addressed to the master and pushes members in. `/SetMaster` is
the mirror image: addressed to the **player itself**, it controls that player's
own membership. No vendor document mentions it.

| Call | Addressed to | Effect |
|---|---|---|
| `/SetMaster` | a slave | **Leaves the group.** The `<master>` element disappears from its `/SyncStatus`. |
| `/SetMaster` | a master or standalone player | No-op. Returns the current `<SyncStatus>`. |
| `/SetMaster?master=<ip>&port=<port>` | any free player | **Joins that player's group** as a slave — but see the one-sidedness note below. `port` is optional. |
| `/SetMaster?master=<ip>` | any free player | Same; the port defaults. **[V hardware]** |
| `/SetMaster?master=<own address>` | any player | **Accepted, not rejected.** The player records *itself* as its own master. **[V hardware]** |
| `/SetMaster?master=<address that is no player>` | any player | No change. **[V hardware]** |
| `/SetMaster?master=<ip>` | a player already slaved elsewhere | **Reparents** it onto the new master, clearing the old master's slave list. **[V hardware]** |
| `/SetMaster` (bare) | a nested master | Detaches it from its own master while **keeping its own slaves**. **[V hardware]** |
| `/SetMaster?slave=<ip>&port=<port>` | anything | Ignored. `slave` is not a parameter this endpoint accepts. |

**Membership created this way is one-sided [V hardware].** After
`B/SetMaster?master=A` succeeds, B reports `<master>A</master>`, but **A does
not list B in its `<slave>` elements and neither player reports a `group`
name**:

```
A: master=–  slaves=[]  group=""
B: master=A  slaves=[]  group=""
```

Compare `/AddSlave`, which produces both halves and a group name
(`group="Stue+Kontor"`). Two consequences:

1. **A client must read topology from both ends.** Building it from masters'
   `<slave>` lists alone makes a slave-side joiner invisible.
2. **`/RemoveSlave` cannot free such a player**, because no master lists it as a
   slave. The only exit is a bare `/SetMaster` on the player itself. This is
   normal for slave-side joins, not a failure of `/RemoveSlave`.

The official Controller never uses `?master=` to form a group — the only
`/SetMaster` call in either the macOS or Android app is the bare self-unjoin.
`?master=` is real, but it is not the group-formation path.

This gives a client a slave-initiated join and a self-service leave, neither of
which `/AddSlave` and `/RemoveSlave` provide — both of those must be addressed
to the master, which you may not know or may not be able to reach.

**Staleness depends on the form [V hardware].** The `<SyncStatus>` returned by
a successful `?master=` call shows the *pre-call* state with the same `etag` as
the previous response — observed on six separate cases, including the self, the
non-player and the reparent forms. The **bare** self-unjoin is different: it
answers with a fresh `etag` already reflecting the departure.

| form | response body |
|---|---|
| `/SetMaster?master=…` | pre-call state, `etag` unchanged. Re-poll. |
| `/SetMaster` (bare, on a slave) | post-call state, `etag` incremented. Trustworthy. |

Grouping completes asynchronously, so for `?master=` do not parse the response
body to confirm success; re-poll `/SyncStatus` instead.

**Role reversal is not rejected — it corrupts both players [V hardware].**
Pointing a master at its own slave (asking A to become a slave of B while B is
already a slave of A) does **not** produce an error and does not break the
group. It produces a mutual master loop:

| player | master before | slaves before | master after | slaves after | group after |
|---|---|---|---|---|---|
| A | – | B | **B** | **B** | `Stue+Kontor` |
| B | A | – | A | – | – |

A ends up naming B as **both its master and its slave** while B still names A
as its master. Each player considers the other its master, a state nothing else
in the protocol produces. An earlier reading of this document said the device
detected the cycle and reasserted the original master; hardware shows it does
neither.

**Role is fixed at group formation.** There is no swap operation. To reverse the
roles, dissolve the group and re-form it from the intended master — which is
exactly what the Controller app does, and why doing it by hand appears to fail
while the app "just works". A client must never send `/SetMaster?master=` to a
player that is already a master.

**Secondary players proxy to the primary [official].** `/Status`, playback
control, queue management and content browsing sent to a secondary are
internally forwarded to the primary, and a secondary's `/Status` is a copy of
the primary's. Volume is the exception: it stays per-player, which is why
`/SyncStatus` must be polled per secondary to track individual volumes.

**Client behaviour worth knowing [V]:** the per-row "join" action sends a
single-element list and does *not* re-send existing members. The UI forbids
joining a player that is already a master or slave —
`canGroup() = !isSlave() && !isMaster() && initialized && authorized` — so
merging two groups is not reachable through the normal UI.

Android's "Group All" skips the selected master, upgrading players, zone slaves,
uninitialized players (unless the initialized check is disabled) and
unauthorized players. It just does not filter on master/slave status, so it
*can* reach a state the per-row action cannot.

**The device does not merge groups — it nests them.** Adding an existing
master as a slave produces a two-level tree, and the second group's slaves
then disappear from the app's player list. See §14 for the full behaviour and
why. Adding an existing *slave* has no effect at all. A client should treat
`hasMaster` and `hasSlaves` as independent, not mutually exclusive.

Related:
- `/GetUnpairedSlaves` — §6.4.
- `/upgrade` — **lowercase**; `/Upgrade` returns 404. Params `upgrade=old|check`,
  plus optional `slave` and `port`.


---

## 6. Presets **[V]**

| Endpoint | Params | Notes |
|---|---|---|
| `/Presets` | — | List presets. |
| `/Preset` | `id=<n>` | Recall a preset. |
| `/SetPreset` | `id`, `name`, `image`, `volume`, `encoded_url`, `shuffle`, `canShuffle`, `delete` | Create/modify/delete. `delete=1` with an `id` removes a preset. |
| `/ReorderPresets` | — | **POST with a JSON body** to a device-supplied URL. |
| `/ExternalSource` | `id=+` or `id=-` | Cycle external input forward/back. |
| `/ExternalSource` | `id=<chassisInputId>` | Select an input **absolutely**, rather than stepping. **[V official]** — both Controller apps build this call as `id = chassisInputId ?? changeDirection`, and the Android app names the stepping variants `nextExternalSource` / `previousExternalSource`. The absolute form is undocumented by the vendor. |

### 6.1 `/Presets` response **[V]**

```xml
<presets prid="12">
  <preset id="1" name="…" url="…" image="…" volume="30"
          shuffle="1" canShuffle="1"/>
</presets>
```

| Element / attribute | Notes |
|---|---|
| `presets@prid` | Presets version. Matches the `prid` element in `/Status`. |
| `preset` | Repeatable. |

A real response, showing the two forms a preset `url` takes:

```xml
<presets prid="0">
  <preset id="1" name="RP Main Mix" url="RadioParadise:/0:4"
          image="https://img.radioparadise.com/source/27/channel_logo/chan_0.png"/>
  <preset id="2" name="Rolig musik" volume="6"
          url="/Load?service=Tidal&amp;id=9977e64f-8df5-4967-9219-9cd777f8eb64"
          image="/Artwork?service=Tidal&amp;playlistimage=6793e3e6-0a62-4921-8158-0e0fe2e52d3c"/>
</presets>
```

A preset `url` is either a **service URI** (`RadioParadise:/0:4`, pass to
`/Play?url=`) or a **local path** (`/Load?...`, request directly). Decide by
whether it starts with `/`. `image` follows the same split: absolute for
service-hosted art, `/Artwork?...` for player-hosted. `volume` is optional and
applies when the preset is recalled.

`<preset>` attributes are **not** whitelisted — the handler copies *every*
attribute into a generic string map. The ones the app reads by name are `id`,
`name`, `url`, `image`, `volume`, `shuffle`, `canShuffle`. `canShuffle` and
`shuffle` are `"1"`/`"0"`. A preset with a blank `id` is treated as new.

---

## 7. Queue / current playlist **[V]**

| Endpoint | Params | Notes |
|---|---|---|
| `/Playlist` | `start`, `end`, `length` | Current play queue. Android pages 20 at a time. `length=1` returns only the top-level attributes and no tracks. |
| `/Add` | see §7.2 | One endpoint, all content types. |
| `/Clear` | — | Clear the queue. |
| `/Clear` | `nextlist=1` | Clear the "play next" list. |
| `/Delete` | `id=<index>` | Remove one queue entry. |
| `/Move` | `old=<index>`, `new=<index>` | Reorder a queue entry. |
| `/Save` | `name=<playlist name>` | Save the queue as a named playlist. |
| `/Load` | `service`, `id`, `name` | Load a playlist or collection, replacing the queue. This is the form preset `url` attributes take for playlist presets. Response is one of the four roots in §7.3, most likely `<loaded service><entries>`. |
| `/AddFavourite` | `service`, plus item identifiers such as `artist`, `albumid`, `songid`, `playlistid` | Add to the service's favourites. |
| `/DeleteFavourite` | same as above | Remove from favourites. Declared in `/Services` as `<request type="favourite" subtype="delete">`. |

### 7.1 `/Playlist` response **[V]**

```xml
<playlist id="7" name="…" length="42" modified="1">
  <song id="0" service="…" fn="…" …>
    <title>…</title><art>…</art><alb>…</alb><quality>…</quality><fn>…</fn>
  </song>
</playlist>
```

| Element / attribute | Notes |
|---|---|
| `playlist@id` | Playlist **version**, not an identifier. |
| `playlist@name` | Defaults to empty string if absent. |
| `playlist@length` | Total queue length (not the page size). |
| `playlist@modified` | `"1"`/`"0"`. |
| `song@id` | Queue index. |

`<song>` copies **every** attribute into a generic string map, then these
child text elements are mapped onto typed fields. Attributes observed on a
streaming-service queue entry: `id`, `service`, `songid`, `albumid`,
`artistid`, `similarstationid`, `trackstationid`, `fn`.

| Child element | Maps to |
|---|---|
| `title` | song name |
| `art` | artist |
| `alb` | album name |
| `quality` | quality string |
| `fn` | filename |

Any other child element also lands in the generic map. Note the collision:
`fn` appears both as an attribute and as a child element.

`<track>` text of the form `n/m` is split on `/` and only `n` is kept
(seen in `SongHandler` and `SongsWithWorksHandler`).

### 7.2 `/Add` parameters by content type **[V]**

| Content | Params |
|---|---|
| Song | `service`, `file`, `cursor`, `playnow`, `where`, `last`, `all`, `listindex`, `nextlist` |
| Album | `service`, `albumid`, `cursor`, `playnow`, `where`, `last` |
| Playlist | `service`, `playlist`, `playlistid`, `cursor`, `playnow`, `where`, `last` |
| Work (classical) | `service`, `albumid`, `recordingid`, `cursor`, `playnow`, `where`, `last` |
| Generic item | `service`, `file`, `playnow` |

Android sends `playnow=1&where=last&cursor=last` as its defaults.

Observed values: `playnow=1` plays immediately, `playnow=-1` enqueues without
playing. `where` takes `last` and `nextAlbum` (append after the current album
rather than the current track), plus `next` and `nextAlbum` in context-menu
`actionURL`s from `/Services`.

### 7.3 The play response is polymorphic **[T]**

Issuing a `playURL` from a browse item, or an `/Add`-family request, can return
**four different root elements** depending on what was played. Blu4Net
dispatches on the root name and throws on anything else. No other source
documents this and it is untested here, but it matches the shapes the vendor
document shows for `/Preset` and `/Shuffle`, so it is likely right.

| Root | Shape | Emitted when | Evidence |
|---|---|---|---|
| `<loaded service>` | `<entries>` child = track count | A playlist or collection was loaded | **Sample** (`/Preset` on a playlist preset) |
| `<state>` | Text, e.g. `stream` | A stream or radio station started | **Sample** (`/Preset` on a radio preset), and hardware |
| `<addsong id count length>` | Attributes only | Tracks were appended to the queue | Blu4Net only |
| `<playlist id length count shuffle repeat>` | Attributes only | The queue itself was replaced or reordered | **Samples** (`/Clear`, `/Shuffle`, `/Repeat`) |

Two of the four roots are now backed by real samples of the **same endpoint**
(`/Preset`) returning different shapes for a playlist versus a radio station,
which is the clearest possible demonstration of the point.

So a client must switch on the root element rather than assume one shape per
endpoint. Together with the `<error>` envelope and the HTML failure body of
§0.1, that is **six** possible replies to a single play request.

`<addsong>` is the only place a queue insert reports what it did: `id` is the
queue position of the first inserted track, `count` how many were added, and
`length` the resulting queue length. Worth confirming — see T-28.

---

## 8. Library browsing — device-driven **[V]**

The most important structural fact about browsing.
On Android, `BrowseOptions.getAction()` returns `url.encodedPath()`. The path and
query come from a URL string the **player supplied** in a previous XML
response. The app follows links; it does not construct browse paths.

The pattern:
1. `GET /Services` — enumerate available sources/services.
2. Each response element carries a `url` attribute plus `resultType`, `style`
   and `refresh` hints.
3. Follow that URL; repeat.

### 8.1 Typed browse entry points **[V]**

These paths are constructed directly by at least one client, so they are real
endpoints rather than purely device-supplied links:

| Path | Seen in | Typical parameters |
|---|---|---|
| `/Songs` | Android, Windows | `service`, `playlistid`, `section` |
| `/Albums` | Windows | `service`, `artistid`, `genre`, `category` |
| `/Artists` | Windows | `service`, `section` |
| `/Composers` | Windows | `service`, `section` |
| `/Folders` | Windows | `service`, `path` |
| `/Genres` | Android | `service` |
| `Playlists` | Android, blucli | `service`, `category`, `expr` |
| `/RadioBrowse` | Android, Windows | `service`, `key`, `url` |
| `/RadioPresets` | Android | — |
| `/Sources` | Windows | — |
| `Search` | Android | `expr` |
| `/AddToPlaylist` | Windows | `create=1`, `name`, plus item params |
| `/AddToPlaylistOptions` | Windows | `service` |

Even so, prefer the urls declared in `/Services` (§8.3). The parameter sets
vary per service, and LocalMusic uses a versioned `/library/v1/` namespace for
the same concepts (§8.5) — so a hard-coded path with hand-built parameters will
work for one service and silently miss another.

### 8.2 Sorting and filtering are declared in `/Services` **[V hardware]**

Sort and filter options are **not** advertised in the browse response. They are
declared once per list inside the `<service>` subtree returned by `/Services`,
and the client turns the chosen option into an ordinary query parameter on the
browse request. A list that returns no `<sortMenu>` may still be fully sortable
— Tidal favourites is exactly that case.

This is the single most important reason to fetch and keep `/Services`. A client
that treats it as a one-off source list loses all sorting and filtering even
though the endpoints support it.

#### The declaration

```xml
<menuGroup id="Tidal-Favourites" context="Favourites" displayName="My Music">
  <menuEntry displayName="Songs" inlineRows="5">
    <sort name="sort" default="name" minimumSchemaVersion="19">
      <value name="name"   displayName="A → Z" />
      <value name="recent" displayName="Date added" />
      <value name="album"  displayName="Album" />
      <value name="artist" displayName="Artist" />
    </sort>
    <browseRequest url="/Songs" resultType="Song">
      <requestParameter>category=FAVOURITES</requestParameter>
    </browseRequest>
  </menuEntry>
</menuGroup>
```

| Element / attribute | Meaning |
|---|---|
| `<sort name>` | **The query parameter to send.** Defaults to `sort` when absent. |
| `<sort default>` | Value used when the user has not chosen one. |
| `<sort minimumSchemaVersion>` | Hide the whole sort control below this client schema. |
| `<value name>` | The value to send. |
| `<value displayName>` | Label for the UI. |
| `<value reverseName>` | Descending variant. **Read by the Android client but not present in any observed response** — treat descending as unavailable unless a device sends it. |
| `<browseRequest url>` | Base path for the request. |
| `<browseRequest resultType>` | `Song`, `Album`, `Artist`, `Playlist`, `Info` — tells the client how to render the result. |
| `<browseRequest grouped>` | Result is section-grouped (A–Z headers). |
| `<browseRequest defaultView>` | This entry is the group's landing tab. |
| `<requestParameter>` | **Text content** is a literal `key=value` pair to append. Repeatable. |
| `<requestItemParameter name>` | Take this parameter's value from the item being browsed into. |
| `<genreItemParameter name>` | Same, sourced from the current genre. |
| `<menuEntry inlineRows>` | How many rows to preview inline on the parent screen. |
| `<menuGroup context>` | Which object type this group hangs off, e.g. `Artist`, `Favourites`. |

#### Building the request

Concatenate the `browseRequest` url, its `requestParameter` children, the
service name, and the chosen sort value:

```
/Songs ?service=Tidal &category=FAVOURITES &sort=recent
  │       │             │                    └─ <value name> chosen by the user
  │       │             └─ from <requestParameter>
  │       └─ the <service name> being browsed
  └─ <browseRequest url>
```

Confirmed working. `GET /Songs?service=Tidal&category=FAVOURITES&sort=recent`
returns the favourites ordered by date added, and **the response echoes the
parameter back** on its root element:

```xml
<songs service="Tidal" category="FAVOURITES" sort="recent" start="30" end="79">
```

Applying a sort **replaces** any existing value of that parameter rather than
appending. Selections are remembered per list, keyed by the `browseRequest` url
plus its `requestParameter` children.

#### Filters

Filters follow the same shape, one level deeper, and are inherited by
descendant entries:

```xml
<filter name="quality" displayName="Filter by quality" class="alternative"
        default="20" required="true" minimumSchemaVersion="35">
  <value name="20" displayName="MQA"        type="mqa" />
  <value name="4"  displayName="CD Quality" type="cd" />
</filter>
```

`<filter name>` is the query parameter; selected `<value name>`s are joined
with commas into one parameter. `class="alternative"` means single-choice,
otherwise multi-select. `required="true"` means a value must always be sent,
and `default` gives the initial one. A `<nofilter/>` child on a `menuEntry`
suppresses an inherited filter for that entry.

`<value type>` is a semantic hint (`mqa`, `hr`, `cd`) so a client can show a
quality badge rather than raw text.

### 8.3 The rest of the `/Services` menu tree **[V hardware]**

`<sort>` and `<filter>` are two elements of a larger declaration language. The
whole browse UI — screens, actions, context menus, search — is defined here,
which is why a client that skips `/Services` ends up hard-coding behaviour that
the device was willing to describe.

#### Request elements

Five element names, all sharing the same `url` + parameter-children pattern.
The difference is what the client does with the result.

| Element | Purpose | `type` values observed |
|---|---|---|
| `<browseRequest>` | Navigate to a list screen | *(none)*, `info`, `addtoplaylist`, `favourite`, `relatedStations`, `selectStream` |
| `<request>` | Perform an action, stay put | `favourite`, `add`, `addAll`, `preset`, `playRadio`, `delete`, `play` |
| `<contextRequest>` | Jump to a related object | `gotoartist`, `gotoalbum` |
| `<searchRequest>` | Search within a scope | `searchOn`, with `view` = `artists`, `songs`, `albums` |
| `<artworkRequest>` | Build an artwork URL | — |

`<request subtype>` refines the action: `add`/`delete` for favourites,
`now`/`next`/`last`/`shuffle` for queue operations.

`<browseRequest resultType>` tells the client how to render the response:
`Song`, `Album`, `Artist`, `Composer`, `Genre`, `Playlist`, `Info`,
`BriefInfo`, `BrowseMenu`, `Search`, `Alarms`, `AddToPlaylistOptions`,
`SongsFoldersPlaylists`. Also `grouped="true"` for A–Z section grouping,
`defaultView="true"` for the landing tab, and `xmlRequestParameter="format=xml"`
where a request would otherwise return a non-XML representation.

#### Parameter children

| Element | Meaning |
|---|---|
| `<requestParameter>` | **Text content** is a literal `key=value` pair. Repeatable. |
| `<requestItemParameter name source optional>` | Take the value from the item being acted on. `name` is the parameter to send; `source` names the item attribute to read when it differs from `name`; `optional="true"` means omit it if the item lacks it, otherwise the entry is unavailable. |
| `<genreItemParameter name source>` | Same, sourced from the current genre. |

So a context-menu entry is fully self-describing:

```xml
<menuEntry displayName="Remove favourite">
  <enableOnAttribute name="isFavourite"/>
  <request url="/DeleteFavourite" type="favourite" subtype="delete">
    <requestItemParameter name="artist" />
  </request>
</menuEntry>
```

That means: show this entry only when the item has an `isFavourite` attribute,
and on tap issue `GET /DeleteFavourite?artist=<item's artist>`.

#### Conditional visibility

| Element | Meaning |
|---|---|
| `<enableOnAttribute name>` | Show the entry only when the item **has** this attribute. |
| `<disableOnAttribute name>` | Hide the entry when the item has it. |

These are what make a single declaration serve both "Favourite" and "Remove
favourite" without the client knowing anything about favourites.

#### Confirmation prompts

```xml
<confirmAction text="Delete playlist: %s?">
  <textItemSubstitution attribute="text" source="playlist" />
</confirmAction>
```

`text` is a printf-style template; each `<textItemSubstitution>` fills one `%s`
from the item, reading the attribute named by `source`. Destructive entries
carry one, and a client should honour it rather than firing the request
directly.

#### Preset creation

`<request type="preset">` carries three extra attributes naming which item
fields become the preset:

```xml
<request url="/SetPreset" type="preset"
         preset_name="playlist" preset_url="preset_url" preset_image="image">
  <requestItemParameter name="url"   source="preset_url"/>
  <requestItemParameter name="name"  source="playlist"/>
  <requestItemParameter name="image" optional="true" />
</request>
```

#### Search

```xml
<search prompt="Search..." parameterName="expr" hasSuggestions="true">
  <menuGroup context="Search" minimumSchemaVersion="2"> … </menuGroup>
</search>
```

`parameterName` is the query parameter carrying the search text (`expr` for
LocalMusic and Tidal), `prompt` is the placeholder, and `hasSuggestions`
indicates typeahead support. The `<menuGroup>` inside defines the result tabs.

#### Gating

`minimumSchemaVersion` appears on `menuEntry`, `menuGroup`, `genreGroup`,
`inlineEntry`, `sort` and `filter`. Skip any element whose value exceeds the
schema version you advertise in `X-Sovi-Schema-Version` (§1.4), or you will
render controls the device does not expect you to support.

`<menuGroup mainMenu="true">` marks the service's top-level menu;
`<menuGroup context="…">` groups are context menus for that object type
(`Artist`, `Album`, `Playlist`, `Favourites`, `Search`).

#### `/Services` is per-player, and unordered

Three players on the same firmware returned **semantically identical** trees —
same eight services, same menus — but with services and attributes emitted in
different orders and a different `sid` each. So:

- Do not treat `sid` as a shared identity; it is per player.
- Do not rely on document order.
- Do not cache one player's tree for another, even on identical firmware.

Whether the order is stable for a given player across requests is untested.

### 8.4 Observed sort vocabularies **[V hardware]**

Values are per service and per list — read them from your own `/Services`
rather than hard-coding these. Recorded here to show the shape:

| List | `default` | Values |
|---|---|---|
| Tidal → My Music → Songs / Playlists / My Playlists / Artists | `name` | `name` (A → Z), `recent` (Date added), and for Songs also `album`, `artist` |
| Tidal → My Music → Albums | `name` | `name`, `recent`, `artist`, `date` (Release date) |
| BluOS Playlists | `alpha` | `recent` (Date added), `alpha` (A → Z) |
| LocalMusic → Albums | `alpha` | `alpha`, `recent`, `year`, `decade`, `artist`, `artistDate` |
| LocalMusic → Artist → Albums | `alpha` | `alpha`, `date` (Release date), `recent` |

Note the vocabularies are **not** shared: Tidal calls alphabetical `name`,
LocalMusic and BluOS Playlists call it `alpha`. Never assume a value carries
across services — this is precisely what the declaration exists to tell you.

### 8.5 Versioned library paths

LocalMusic declares a whole parallel `/library/v1/` namespace:
`/library/v1/Songs`, `/library/v1/Albums`, `/library/v1/Artists`,
`/library/v1/Composers`, `/library/v1/Genres`, `/library/v1/Folders`,
`/library/v1/Playlists`, `/library/v1/Search` and `/library/v1/Artwork` — in
place of the unversioned paths of §8.1, which streaming services still use.

This is the clearest argument against hard-coding browse paths. The unversioned
forms are not deprecated, they simply are not what LocalMusic uses on this
firmware, and a `v2` would presumably appear the same way.

### 8.6 Common browse parameters **[V]**

`service`, `nextlink`, `nextLink`, `offset`, `index`, `section`, `length`,
`all`, `item`, `action`, `addAction`, `playAction`, `menuAction`,
`contextMenu`, `nowPlayingMatch`, `fetch`, `input`, `genre`, `genreid`,
`folder`, `path`, `fn`, `art`, `alb`, `song`, `title`, `cover`, `quality`,
`work`, `works`, `image`, `largeThumbnail`, `customiseScreen`, `category`,
`recent`, `start`, `end`, `browseIsFavouritesContext`.

Paging uses `nextlink` / `offset` values the device returns — do not compute
them yourself.

---

## 9. Artwork **[V]**

`/Artwork?fn=<path>` for local-library files. Folder browse responses do not
carry artwork URLs, so a client synthesises them from the folder path. `/Status` returns absolute artwork URLs for streaming services.

`/Artwork` also takes a **service-scoped parameter family**, used for streaming
content rather than local files:

| Form | Selects |
|---|---|
| `/Artwork?fn=<path>` | Local library file |
| `/Artwork?service=<svc>&songid=<id>` | Track artwork |
| `/Artwork?service=<svc>&albumid=<id>` | Album artwork |
| `/Artwork?service=<svc>&playlistid=<id>` | Playlist artwork |
| `/Artwork?service=<svc>&playlistimage=<id>` | Playlist cover image |
| `/Artwork?service=<svc>&album=<name>&artist=<name>` | **[T]** By name rather than id. Reported in 2015 and 2016 for LocalMusic; not seen on current firmware, where the id forms are used instead. |

**`/Artwork` does not always return an image [T].** When no artwork exists it
answers with XML instead of binary:

```xml
<artwork>none found</artwork>
```

HTTP 200, `Content-Type` unverified. A client must check the content type or
sniff the first bytes rather than handing the body straight to an image
decoder.

**Append `followRedirects=1` to any image URL beginning with `/Artwork`.**
Without it the request may answer with a redirect that the client then has to
follow. This applies to `image` and `stationImage` in `/Status`, `image` in
`/Presets`, and `image` on browse items.

**Artwork response headers [T, 2016].** BluShepherd's packet captures show
`/Artwork` replying with `Access-Control-Allow-Origin: *`, `Cache-Control:
max-age=0`, an `Expires` equal to `Date`, and **no `ETag`**. If the CORS header
still holds, a browser can fetch artwork directly; the absent validators mean
it will refetch every time, which is what makes artwork caching painful in the
official desktop app. Worth re-checking on current firmware before relying on
either.

In a server-side client, proxy artwork through your server so browsers never
need direct player access, and add the caching the player does not provide.

---

## 10. Settings, alarms, misc

| Endpoint | Params | Notes |
|---|---|---|
| `/Settings` | `id`, `schemaVersion` | **Served on port 11001**; a request to 11000 answers 301 with the 11001 URL, so follow redirects. See §10.3. `id` is optional: `/Settings?schemaVersion=25` returns the whole settings tree, `/Settings?id=capture&schemaVersion=32` just the inputs. Response root `<settings schemaVersion>` containing nested `<menuGroup>` and `<setting>` elements. |
| `/ui/Configuration` | — | UI configuration. |
| `/Alarms` | — | See §11.6. |
| `/BTDevices` | `etag`, `timeout=100` | List; long-polls. |
| `/BTDevices` | `connect=<id>` or `disconnect=<id>` | Connect or disconnect a paired device. |
| `/BTDevices` | `unpair=<id>` | Unpair. |
| `/update` | `doit=1` | Firmware update trigger. Lowercase. |
| `/Action?<query>` | — | Generic action dispatch; the query is passed through verbatim. |
| `/GetUnpairedSlaves` | — | See §11.4. |
| `/proxyToSlave` | `slave=<ip>:<port>`, `url=<path>` | **[T]** **POST.** Forwards the request body to `<path>` on the named slave. See below. |
| `/Name` | *(none)* | Read the player name. Returns `<name>Stue</name>`. |
| `/Name` | `set=<new name>` | Rename the player. Returns `<name>` with the new value. The change is immediate and shows in `/SyncStatus` and in running Controller apps within a second. |
| `/Name` | **POST**, form field `nodename=<new name>` | **[T]** An alternative rename form used by `blutui`. The `set=` query form is confirmed on hardware; this one is not. |
| `/Reindex` | `logall=0\|1` | Trigger a local-library reindex. Progress shows as `<indexing>` in `/Status`. |
| `/GetSettings` | — | **Returns JSON**, not XML. See §10.1. |

`/DynamicSettings` is not a literal path — the URL always comes from the
device, via `<soundbar_settings url>` in `/SyncStatus`. The app opens it in a
WebView, and posts changes back as a url-encoded form.

### 10.0 `/proxyToSlave` — writing to a grouped slave **[V hardware][T]**

A slave in a group is still individually addressable, but `blutui` (Rust) uses a
relay on the master instead:

```
POST /proxyToSlave?slave=<ip>:<port>&url=<path>
Content-Type: application/x-www-form-urlencoded

<the form body to deliver>
```

The master forwards the body to `<path>` on that slave. Its use there is to set
LED brightness on a zone slave: `url=/setting` with a body of
`ledbrightness=<value>`.

Why this exists rather than addressing the slave directly is unclear. The most
likely reason is zone slaves in a stereo pair or home-theatre zone, which may
sit on a separate subnet (`zoneSubnet` appears in `/SyncStatus`, §2.1) and so be
unreachable from the controller even though the master can reach them.

Note the `slave` parameter is a **combined `ip:port`**, not the separate
`slave` + `port` pair used by `/AddSlave`.

The path's **existence** is confirmed on hardware (`C-04` in §17.1): called bare
it answers 400, not the 404 an unknown path gets, on 4.16.22. The **relay
behaviour** described above — that the body actually reaches the named slave —
is not; that needs the slave's own setting to change, which no run has checked.
See T-34.

### 10.1 `/GetSettings` — not present on current firmware **[V hardware]**

The Integration Utility (2024) polls a `/GetSettings` endpoint and parses the
reply as **JSON**, diffing it for per-setting add/change/enable/disable events
instead of re-fetching the whole `/Settings` tree.

**On firmware 4.16.22 (schema 34, NODE N132) the path returns a bare
HTTP 404.** So it is either removed, superseded by the `/ui` surface (§10.2),
or restricted to Hub-role players — the Integration Utility only supports
CI-series players and the CB130, not the N-series.

Do not build on it. If you need settings, use `/Settings?schemaVersion=<n>`,
which is XML and does work. Whether any current firmware still serves JSON here
is **[U]**.

### 10.2 The `/ui` server-driven UI surface **[V hardware]**

`GET /ui/Configuration` returns the player's map of server-driven UI screens.
On firmware 4.16.22 it answers on **port 11000** — the `ms`/`ms-go` migration
described in §13 has progressed, so do not assume `/ui` still requires port 80.

```xml
<configuration>
  <item id="home"                  URI="/ui/Home"/>
  <item id="recentlyPlayed"        URI="/ui/RecentlyPlayed"/>
  <item id="news"                  URI="/ui/News"/>
  <item id="favourites"            URI="/ui/Favourites"/>
  <item id="sources"               URI="/ui/Sources"/>
  <item id="search"                URI="/ui/Search"/>
  <item id="nowPlayingContextMenu" URI="/ui/nowPlayingCM"  resultType="contextMenu"/>
  <item id="queueItemContextMenu"  URI="/ui/queueItemCM"   resultType="contextMenu"/>
  <item id="resolveSoviURL"        URI="/ui/resolveSoviURL"/>
  <item id="queue"                 URI="/ui/Queue"         resultType="queue"/>
  <item id="presets"               URI="/ui/presets"/>
</configuration>
```

Each `<item>` has `id`, `URI` and an optional `resultType`. As everywhere else
in the protocol, **follow the `URI` rather than hard-coding it** — this
document lists the values one player returned, not a fixed set.

These screens return the component model of §11.11 (`<list>`, `<item>`,
`<action URI=…>`), which is why `URI` is uppercase here. `resolveSoviURL` is
the resolver behind the `sovi://` scheme (§13).

This surface overlaps `/Browse` and the typed endpoints of §8 without replacing
either: `/ui/Queue` and `/Playlist` describe the same queue, `/ui/presets` and
`/Presets` the same presets. It is the newest of the three and the one the
current Controller apps render, but it is undocumented by the vendor and
carries no stability promise. For integrations, §15.1 still applies: prefer
`/Browse`.

### 10.3 Port 11001 — the settings surface **[V hardware]**

Settings live on their **own port**. `GET :11000/Settings?...` answers `301
Moved Permanently` with the same path on `:11001`. Port 11001 serves *only*
settings — `/Status`, `/Shares` and `/ui/Configuration` all return 404 there.

That makes three ports in total: **11000** control, **11001** settings,
**80** legacy web UI (§13).

**Always state the port when recording a result.** Endpoints are not uniformly
available across the three, and a 404 means only “not on this port”. Confirmed
so far: `/diagnostics` answers on **80** and 404s on 11000; `/Settings` answers
on **11001** and 301-redirects from 11000; `/Status`, `/GitVersion` and
`/ui/Configuration` answer on **11000** and 404 on 11001.

```
GET :11001/Settings?schemaVersion=<n>            # whole tree
GET :11001/Settings?id=<pageId>&schemaVersion=<n>  # one page
```

Root is `<settings schemaVersion>`, plus `pageId` when a page was requested.
It contains `<menuGroup>` and `<setting>` elements, nested arbitrarily.

| Element | Attributes |
|---|---|
| `<menuGroup>` | `id`, `displayName`, `icon`, `url`, `defaults` |
| `<setting>` | `id`, `name`, `displayName`, `icon`, `url`, `class`, `value`, `description`, `explanation`, `refresh`, plus per-class extras (`count`, `enabled`, `sleep`, `helpUrl`) |
| `<value>` | `name`, `displayName`, and optionally `icon` — the options of a `class="list"` setting. The parent `<setting value="…">` names the currently selected option, so "which is active" is `setting.value == value.name`. |
| `<webview url>` | An external page to embed for settings with no native UI |

`class` selects the control type: `list`, `boolean`, `button`, `alarms`,
`sleep`. `description` is the current value rendered for display;
`explanation` is long-form help text. `refresh="true"` means re-fetch the tree
after changing this setting.

**The `url` attribute is the write endpoint**, and it is not uniform:

| `url` | Meaning |
|---|---|
| `/setting` | The generic setting writer — **lowercase and singular**, distinct from `/Settings`. Also serves `/Settings?id=player`, whose settings include `ledbrightness` |
| `/audiomodes` | Audio and source settings — Bluetooth mode, subwoofer, replay gain, channel mode, MQA passthrough, clock trim. **Also readable** — see §10.4 |
| `/alsa_setting` | EQ and DSP settings — tone controls, treble, bass, crossover, balance, centre trim, listening-mode preset, reset |
| `/Reindex` | A `class="button"` setting that fires the endpoint directly |

An empty `<menuGroup>` (e.g. `capture-input0`) is a page to be fetched with
`?id=` rather than a group with no contents. `<webview url>` still points at
**port 80** — network share configuration is served as
`http://<player>:80/sharecfg?noheader=1`, so the legacy surface is not gone.

As always, follow the `url` the device gives you rather than hard-coding it.

### 10.4 `/audiomodes` as a read endpoint **[T]**

A bare `GET /audiomodes` returns the player's current audio configuration as a
single element. This is separate from the settings tree of §10.3, which
describes the same values as UI controls; `/audiomodes` gives them raw.

```xml
<audiomode volMin="-90" volMax="0" volMinLimit="-90" volMaxLimit="0"
           volMinDefault="-90" volMaxDefault="0"
           volume="variable" canFixVolume="false"
           volRamp="log" volRampDefault="log"
           channelMode="default" replayGainMode="none" mqaDisable="0"
           crossover="" bluetoothAutoplay="1"
           captureLatency="0" captureAutoplay="0"/>
```

Reported by BluShell against schema 25; not re-checked on current firmware.
Two things it adds beyond §10.3:

- **The dB range in numbers.** `volMin`/`volMax` give the configured range and
  `volMinLimit`/`volMaxLimit` the hard bounds, with `*Default` variants. This is
  what turns a 0..100 `level` into dB. A floor of **-90** here matches the
  earliest published figure of -91 dB at level 0, and is lower than the -80
  typically quoted.
- **Settings not exposed as writes elsewhere**: `volRamp` (`log`),
  `captureLatency`, `captureAutoplay`, `crossover`.

Worth confirming on current firmware (T-32) — if it still answers, it is a
cheaper way to read audio state than parsing the settings tree.

#### Conditional and ranged settings **[V hardware]**

The audio page (`?id=audio`) uses two constructs the top-level tree does not.
Confirmed unchanged between schema 28 and schema 35 on the same model (N130),
so this vocabulary is stable across firmware generations.

```xml
<setting id="eq-treble" name="eq-treble" displayName="Treble" url="/alsa_setting"
         class="range" value="0" hideIfDisabled="true">
  <value min="-6" max="6" step="0.5" units="dB"/>
  <dependsOn name="eq-switch" value="ON"/>
</setting>

<setting id="volumeLimits" name="volumeLimits" displayName="Volume limits (dB)"
         class="dual-range" value="-44,0" hideIfDisabled="true">
  <value min="-90" max="0" minRange="30" units="dB"/>
  <dependsOn name="fixedVolume" value="OFF"/>
</setting>
```

| Construct | Meaning |
|---|---|
| `<dependsOn name value/>` | **Repeatable.** The setting applies only while the named setting holds that value. A client that ignores these will render mutually contradictory controls — for example offering Replay-gain while Digital Passthrough is on. |
| `class="range"` + `<value min max step units/>` | A single numeric slider. `value` is the current number. |
| `class="dual-range"` + `<value min max minRange units/>` | A two-handle range. `value` is a comma-separated pair, e.g. `-44,0`; `minRange` is the smallest allowed span between handles. |
| `hideIfDisabled="true"` | Hide rather than grey out when a `dependsOn` is unsatisfied. |
| `style` | Presentation hint on a `class="button"` setting, e.g. `style="center"`. |

So the full `class` set is `list`, `boolean`, `button`, `range`, `dual-range`,
`alarms`, `sleep`. `style` also takes `inline` and `balance` besides `center`,
and `required="true"` marks a setting that must hold a value.

**The audio page is model-dependent.** Two players on the same firmware expose
different settings, so a client must render whatever the tree returns rather
than assume a fixed list. Observed:

| Setting | Seen on | Endpoint |
|---|---|---|
| `eq-switch`, `eq-treble`, `eq-bass`, `eq-crossover`, `reset` | all | `/alsa_setting` |
| `eq-dirac` (Dirac Live, `class="list"`, `refresh="true"`) | N130 at schema 35 | `/alsa_setting` |
| `eq-balance`, `eq-centre-trim`, `preset` (Listening Mode) | N331 | `/alsa_setting` |
| `subwoofer`, `replayGainMode`, `channelMode`, `mqaDisable`, `enableClockTrim` | most | `/audiomodes` |
| `ears` (Stereo surround) | N331 | `/audiomodes` |
| `centre` (Centre Channel) | N331 | `/setting` |
| `fixedVolume`, `volumeLimits` | all | no `url` — generic `/setting` |

`eq-dirac` is the settings-side counterpart of the `<dirac>` element in
`/Status` (§2.2): its `<value>` list enumerates the Dirac Live filter slots
stored on the player, with `0` meaning off.

Each setting is written as `<url>?<setting name>=<value>`, taking the value from
a `<value name>` child for list settings or the raw number for ranges.

**Two request styles are in use, and it is not settled which the device
prefers.** pyblu sends GET with query parameters; `blutui` (Rust) sends **POST
with a url-encoded form body** to the same paths — `POST /alsa_setting` with
`preset=<value>`, `POST /setting` with `ledbrightness=<value>`. The port 80
surface (§13) is definitely POST-and-form, and `/setting` may have inherited
that convention. Both styles are reported to work by their authors; neither has
been checked here. See T-35.

Two worked examples, both confirmed by an independent implementation:

```
GET /Settings?id=audio                 # read the tree
GET /alsa_setting?preset=<value name>  # set listening mode
GET /audiomodes?subwoofer=withsub      # set subwoofer mode
```

A setting is **absent** rather than disabled when a model does not support it,
so `is this feature available` is answered by whether the `<setting id=…>`
exists at all — not by an enabled flag.

---

## 11. Response shapes **[V]**

### 11.1 Two different error conventions **[V]**

Most handlers extend `AbstractXmlHandler` and get the structured envelope in
§0.1. But `ResultHandler` — used by **`/RemoveSlave`** and **`/MovePlayback`**
— does not. It extends `DefaultHandler` directly and uses a flat convention:

```xml
<error>Something went wrong</error>
```

Here the **element text** is the message; there is no `type` attribute, no
`<message>` child, no buttons. A client must handle both forms.

`MessageResultHandler` (`/AddSlave`, `/Action`, upload) reads one element:
`<message>` text content, plus the structured error envelope.

`ErrorResultHandler` (`/SetInitialized`, `/update`, `/BTDevices` writes,
`/ReorderPresets`) parses **nothing** except the error envelope. A successful
call yields an empty result — the absence of `<error>` is the success signal.

### 11.2 `/Services` — the only DOM-parsed endpoint **[V]**

`NodeService.parseServices` uses `DocumentBuilderFactory`, not SAX. Root
element attributes:

| Attribute | Notes |
|---|---|
| `schemaVersion` | Integer. Also what `WSCSchemaVersion` probes. |
| `sid` | Services-list id; changes when the set of services changes. |
| `url` | Configure URL for the services screen. Observed as `/redirectToCp?href=%2Fservices%3Fnoheader%3D1%26schemaVersion%3D0` — a redirect into the port 80 control panel (§13). |

Then every `<service>` element **anywhere in the document** (via
`getElementsByTagName`, so nesting does not matter):

| Attribute | Notes |
|---|---|
| `name` | Service key, e.g. `LocalMusic`, `TuneIn`, `Qobuz`. |
| `type` | Must be one of `LocalMusic`, `RadioService`, `CloudService`, `AudioInputs`, `WebView`, `Alarms`. **A service with an unrecognised `type` is silently dropped.** |
| `displayname` | Note the all-lowercase spelling. |
| `icon` | |
| `backgroundImage` | |
| `url` | The browse entry point — this is the link the whole browse tree hangs off. |
| `removable` | `"yes"` (not `"true"`). |
| `hasStableBrowse` | `"true"`. |
| `minimumSchemaVersion` | Service is skipped if the client's schema (35) is lower. |
| `maximumSchemaVersion` | Service is skipped if the client's schema is higher. |

The `<service>` **subtree is copied generically** by
`Element.convertXmlDescription` — every attribute and every child element is
retained without a whitelist, so unknown elements survive.

Child element names the client gives meaning to: `menu`, `menuGroup`,
`menuEntry`, `genreGroup`, `inlineEntry`, `filters`, `filter`, `nofilter`,
`sort`, `value`, `browseRequest`, `contextRequest`, `requestParameter`,
`requestItemParameter`, `genreItemParameter`. A `filter`/`nofilter` child is
hoisted into a synthetic `filters` element and inherited by descendants.

**This subtree is the browse menu structure**, not just service metadata: it
defines the screens, their order, their request URLs, and their sort and filter
vocabularies. See §8.2 — it is the part of `/Services` a client actually has to
implement.

### 11.3 `/GitVersion`, `/Sleep` **[V]**

Both are single-element responses:

| Endpoint | Element | Notes |
|---|---|---|
| `/GitVersion` | `<version>` text | Matched case-insensitively. |
| `/Sleep` | `<sleep>` text | The new sleep-timer value in minutes, or empty when off. Android's handler suppresses errors entirely, so `/Sleep` **never surfaces one**. |

### 11.4 `/GetUnpairedSlaves` **[V]**

```xml
<unpairedSlaves>
  <unpairedSlave>
    <brand>…</brand><model>…</model><modelName>…</modelName>
    <version>…</version><mac>001122334455</mac><pairUrl>/…</pairUrl>
  </unpairedSlave>
</unpairedSlaves>
```

All six children are **text elements, not attributes**, and **all six are
mandatory** — the handler discards any `<unpairedSlave>` missing even one.

A `mac` of exactly 12 characters with no `:` is reformatted client-side into
colon-separated form, so both `001122334455` and `00:11:22:33:44:55` are
accepted.

### 11.5 `/upgrade` **[V]**

Parsed with a bare `DefaultHandler`, no error envelope.

| Element | Attribute | Meaning |
|---|---|---|
| `<stage0>` | — | **Presence sets `stage0Ready = false`.** Absence means ready. Inverted logic — easy to get wrong. |
| `<upgrade>` | `available="true"` | An update exists. |
| `<upgrade>` | `inProgress` | **Presence of the attribute** sets upgrading, regardless of its value. |

### 11.6 `/Alarms` **[V]**

```xml
<alarms supportsEndTime="true">
  <alarm id="1" hour="7" minute="30" days="…" enable="1" … />
</alarms>
```

| Element / attribute | Notes |
|---|---|
| `alarms@supportsEndTime` | `"true"`, case-insensitive. |
| `alarm` | Repeatable. **Every attribute is copied into a generic string map** — no whitelist. |

Attributes the app reads by name: `id`, `hour`, `minute`, `days`, `duration`,
`enable`, `end`, `fadein`, `useBackup`, `source`, `url`, `image`, `service`,
`volume`, `shuffle`, `canShuffle`. Requests also carry a `tz` parameter.

A real alarm, from BluShell at schema 25:

```xml
<alarm id="1" hour="8" minute="0" days="1010000" enable="1" volume="25"
       duration="15" fadein="0" source="Current play queue or station"
       url="undefined" image="img/cover.png"/>
```

**`days` is a seven-character bitmask string**, one character per weekday,
`1` for on. `duration` is in minutes. `url="undefined"` is the literal string,
not an empty value — do not treat it as a URL. Older responses carry neither
`supportsEndTime` on the root nor `end` on the alarm.

### 11.7 `/BTDevices` **[V]**

```xml
<btdevices etag="…" connecting="true">
  <device id="00:11:…" name="…" paired="true" connecting="false" connected="true"/>
</btdevices>
```

Element names are matched case-insensitively. Booleans are `"true"`/`"false"`.
A `<device>` without an `id` is skipped.

### 11.8 Notification (device-supplied `notifyurl`) **[V]**

Fetched from the `notifyurl` value in `/Status`, not a fixed path.

| Element | Notes |
|---|---|
| `<notification>` | Root. |
| `<message>` | Text. |
| `<label>` | Repeatable — a list of button labels. |
| `<url externalBrowse>` | Repeatable, positionally paired with the labels. |
| `<displaytime>` | Integer seconds. **Parsed with a bare `Integer.parseInt`** — a non-numeric value throws. |
| `<action type>` | `type="upgrade"` selects the upgrade notification style; anything else is generic. |

### 11.9 Info (device-supplied browse URL) **[V]**

| Element / attribute | Notes |
|---|---|
| `<info service>` | Root, service name in the attribute. |
| `<image>` | Text. |
| `<description format>` | Text, plus a `format` attribute giving the content type. |

### 11.10 Browse list handlers — the shared idiom **[V]**

Every browse handler follows the same pattern, and it is the single most
useful thing to internalise:

1. The container element carries a `service` attribute.
2. Each item element copies **every one of its attributes** into a generic
   string map — there is no whitelist, so unknown attributes survive.
3. A handful of **child text elements** are then mapped onto typed fields.
4. A top-level `<nextlink>` text element carries the paging cursor.

`<nextlink>` appears in `SongHandler`, `AlbumsResultHandler`, `ArtistsHandler`
and `ComposersResultHandler`, always as a sibling of the item elements (the
handlers guard with `!inElement(item)`). Follow it verbatim; do not construct
offsets.

#### `/Songs`-shaped responses **[V]**

The root element echoes the request context and carries a paging window:
`<songs service category sort start end>`. Any sort parameter you sent (§8.2)
is reflected back, which is a cheap way to confirm the device honoured it. Observed on a Tidal favourites list,
`start` and `end` describe the **next** window rather than the page in hand — a
request with no paging parameters returned about 30 songs and
`start="30" end="79"`. Treat them as a paging hint, not a description of the
current page, and prefer the `nextKey` / `nextlink` the device supplies.

**Page size is capped server-side at 50.** Requesting `start=0&end=999` returns
50 items and a next pointer at `start=50&end=99`. You cannot fetch a whole
large list in one call.

**An album-scoped variant [T, 2016].** `/Songs?service=LocalMusic&album=…&artist=…`
returned an extra wrapper level — `<songs service id>` containing
`<album time quality>` containing the `<song>` elements — rather than the flat
list seen on current firmware. Also `<discno>1/1</discno>`, so `discno` takes
the same `n/m` form as `<track>`. A parser should tolerate `<song>` at either
depth, which `inElement()` matching already does (§0).

`<song>` attributes seen on a streaming service: `albumid`, `artistid`,
`songid`, `isFavourite`, `similarstationid`, `trackstationid`. Child text
elements add `discno` alongside those below. `<date>` is the **album release
date** and appears only sporadically — it is not a date-added timestamp, and no
date-added field is returned at all.

```xml
<songs service="LocalMusic">
  <song …attributes…>
    <title>…</title><art>…</art><alb>…</alb><fn>…</fn>
    <time>245</time><track>3/12</track><date>2019</date>
    <quality>…</quality><composer>…</composer>
  </song>
  <nextlink>/Songs?…</nextlink>
</songs>
```

| Child element | Maps to |
|---|---|
| `title` | name |
| `art` | artist |
| `alb` | album name |
| `fn` | filename |
| `time` | length in seconds (`parseInt`) |
| `track` | track number — see below |
| `date` | release date |
| `quality` | quality string |
| `composer` | stored in the generic map |

`<track>` accepts three forms: `3/12` and `3\12` are split and only the
leading number kept; a bare numeric string is used as-is; anything else is
ignored. Song index is assigned **client-side** by a running counter, and the
client appends its own `songIndexOffset` parameter to `nextlink` so paging
keeps the numbering continuous. That parameter is client-invented — a player
does not need to honour it, and the client strips it before sending.

#### `/Albums`-shaped responses **[V]**

Item element is `<album>`; all attributes copied generically. Child text
elements: `title` and `alb` (both set the name), `art` (artist), `cover`
(image URL). If `<album>` has no name from any of those, the album element's
own text content is used as the name.

An `<artist name="…">` element appearing **outside** any `<album>` sets a
default artist inherited by every following album — that is how
artist-scoped album lists avoid repeating the artist per row.

#### `/Artists`-shaped responses **[V]**

Item element is `<art>` — note it is *not* `<artist>`. Attributes copied
generically; the **element's text content is the artist name**, and an `<art>`
with blank text is dropped entirely.

#### `/Genres` and `/Composers` **[V]**

`<genre>` carries `genreid` and `image` attributes with the name as text.
`<composer>` follows the standard item idiom with generic attribute copying
and a `nextlink` sibling.

#### `/Folders` **[V]**

Folder entries get a synthesised `imageURL` of `/Artwork?fn=<encoded path>` —
this is the only place in the client that builds an `/Artwork` URL. Paths are
accumulated against a running base path with `/` appended.

#### Playlists **[V]**

Breaks the idiom in a way worth flagging: the item element is **`<name>`**,
not `<playlist>`.

```xml
<playlists service="…">
  <name …attributes…>My Playlist</name>
  <nextlink>…</nextlink>
</playlists>
```

Attributes are copied generically; the element's **text content** is the
playlist name.

#### Search **[V]**

A single response carrying three parallel item lists — `<artist>`, `<album>`
and `<song>` — each following the standard idiom.

Root is `<search service id>`, and the three lists sit inside `<artists>`,
`<albums>` and `<songs>` container elements:

```xml
<search service="LocalMusic" id="3">
  <artists>…</artists>
  <albums>…</albums>
  <songs>…</songs>
</search>
```

Empty containers are still emitted when a category has no hits, so their
presence says nothing about whether results exist.

| Item element | Typed children |
|---|---|
| `<artist>` | `name` (text), `id` (only if no artist id was set from attributes) |
| `<album>` | `title`, `alb` (name), `art` (artist), `cover` (image) |
| `<song>` | `title`, `art`, `alb`, `fn`, `quality` |

All three copy their own attributes into generic maps first.

#### Radio browse **[V]**

Radio uses TuneIn's own vocabulary, so it does not match the other browse
shapes:

| Element | Notes |
|---|---|
| `<radiotime service total_count>` | Root. Everything else is guarded by `inElement("radiotime")`. `total_count` **[T]** is reported by Blu4Net and was not present in the captured input list. |
| `<category text icon>` | Groups items. Repeatable. |
| `<item>` / `<remoteitem>` | **Two interchangeable item element names.** Both are handled identically. |
| `<nextlink>` | Paging cursor. |

Item attributes are copied generically; `text` is required (an item without it
is skipped) and `canShuffle` is read by name.

On a `/RadioPresets` response the items carry a further set **[T]**:
`guide_id` (the service's own id), `item` (`url` or `station`), `is_preset`
(`"true"`), `preset_id`, and `subtext` for a second line. Note that
**`is_preset` never appears in `/Status` [V hardware].** Tested on a player
while a preset was actively playing, on four players and two models: the
element is absent. It **is** a radio-item attribute (below), which is almost
certainly where the Blu4Net claim came from. Do not look for it in `/Status`.

**`is_preset` is a radio-item attribute here** — which may be where Blu4Net's
`<is_preset>` `/Status` element came from. The two are not the same claim, and
only this one has a sample behind it. Confirmed attributes on a Capture
input list: `id`, `text`, `URL` (uppercase, percent-encoded), `image`, `type`,
`inputType`, `playerName`, `serviceType`. Blu4Net additionally reads `key` and
`is_active` **[T]**, neither of which appeared in the captured list — `is_active`
would be the obvious way to tell which input is currently selected, so it is
worth looking for. Items may appear inside a
`<category>` or at top level.

#### Section info **[V]**

Requested by rewriting the current browse URL with `section=all&length=1`.

```xml
<sections><section name="A" length="24"/></sections>
```

A `<section>` with `length <= 0` is dropped — that includes the `-2`
`parseInt` sentinel, so a missing `length` attribute silently removes the
section. This is the A–Z jump-bar index.

### 11.11 The component model — `<list>` **[V]**

Newer browse screens return a generic component tree rather than a typed list.
This is what `ComponentListHandler` parses, and it is the shape a modern
client should target.

```xml
<list id="…" style="…" title="…">
  <item title="…" text="…" image="…" …>
    <action URI="…" type="…" resultType="…" title="…"/>
    <playAction URI="…"/>
    <addAction URI="…"/>
    <contextMenu URI="…" type="…" resultType="…" title="…">
      <item text="…" icon="…" selected="…"/>
    </contextMenu>
    <nowPlayingMatch key="…" value="…"/>
  </item>
  <menuAction type="…" text="…"><action URI="…"/></menuAction>
  <sortMenu><item text="…" icon="…" selected="…"/></sortMenu>
  <selectorMenu><item text="…" icon="…" selected="…"/></selectorMenu>
  <nextLink>…</nextLink>
</list>
```

**`<item>` is context-sensitive.** Inside `<sortMenu>`, `<selectorMenu>` or
`<contextMenu>` it is parsed as a menu entry; anywhere else it is a content
row. Same element name, two different attribute sets — a parser that ignores
the enclosing element will get this wrong.

| Element | Attributes |
|---|---|
| `<list>` | `id`, `style`, `title` |
| `<item>` (content row) | `title`, `text`, `subTitle`, `subSubTitle`, `topLine`, `image`, `icon`, `quality`, `duration`, `track`, `counter`, `notification`, `objectType`, `selected`, `solidBackground`, `contextMenuURI` |
| `<item>` (menu entry) | `text`, `icon`, `selected` |
| `<action>`, `<playAction>`, `<addAction>` | `URI`, `type`, `resultType`, `title`, `service`, `event`, `externalBrowse`, `closeScreen`, `refreshScreen`, `haptic`, `notification`, `notificationIcon`, `androidAction`, `itunesUrl` |
| `<menuAction>` | `type`, `text`; wraps an `<action>` |
| `<contextMenu>` | `URI`, `type`, `resultType`, `title` |
| `<nowPlayingMatch>` | `key`, `value` |

Note `URI` is **uppercase** in the action elements, unlike the lowercase `url`
used everywhere else in the protocol.

`<action>` attaches to whichever container is currently open, in this
precedence order: `menuAction` → `item` → context-menu item → `list`.

**`<nextLink>` here is camel-case**, unlike the lowercase `<nextlink>` in the
typed browse handlers. Its presence also sets the list to "infinite" mode.
A `<list>` can carry several `<nextLink>` elements.

### 11.12 `<sortMenu>` / `<selectorMenu>` **[V]**

`<sortMenu>` and `<selectorMenu>` are a **different, newer mechanism** from the
`/Services` declarations in §8.2, and the two are not interchangeable. These
appear inline in a component-model response; the `/Services` form is declared
once per list. A list may use either, both, or neither — Tidal favourites, for
example, returns no `<sortMenu>` at all.

Container attributes: `menuTitle`, `text`, and `replaceScreen` (default `true`,
meaning the result replaces the current screen rather than opening a new one).

Each option is an `<item text icon selected>` **with a nested `<action URI=...>`**
— the action is mandatory and is what the client issues when the option is
chosen. There is no sort parameter to construct: take the `URI` verbatim.

Both are plain
containers of menu-style `<item text icon selected>` elements, parsed by the
same `ContextMenuItemModel.fromAttributes` as context menus. `selected` marks
the active option. There is no protocol-level cap on how many options a device
may advertise, and no cap on result length.

---

### 11.13 Long-poll and timeout values in practice **[V]**

The three sources disagree, which is itself informative: the device tolerates a
wide range.

| | Android 4.16.2 | Windows 4.16.0 | HA core (pyblu) | bluesound_alt | Vendor spec |
|---|---|---|---|---|---|
| `/Status` `timeout` | 100 | 15 | 120 | 100 | 100 recommended, never below 10 |
| `/SyncStatus` `timeout` | 10 | 10 | 120 | — | 180 recommended |
| Read timeout | 105 for `/Status` | 15 default | 125 | 110 | — |
| Long polls held per player | 2 | 1 (uses `syncStat`) | 2 | 1 + a volume poll | 1 is normally enough |
| Min gap between polls of one resource | 1 s enforced | — | — | 1 s | 1 s required |

**The read timeout is always the poll timeout plus a margin**, and every
implementation that sets one uses **+5 to +10 seconds**: Android 100→105, HA
120→125, bluesound_alt 100→110. That margin is the client's own guard, not a
protocol requirement, but sizing it below the poll timeout guarantees a
self-inflicted timeout on every idle poll.

A reasonable client: hold one `/Status` long poll at `timeout=100`, set the
read timeout comfortably above it (105 s is what Android uses), re-fetch
`/SyncStatus` when `<syncStat>` changes, and never issue two requests for the
same resource inside one second.

---

## 12. Discovery **[V]**

Discovery is the one part of this document that is not HTTP. Players are found
two ways, LSDP and mDNS, and both yield only an address and port — everything
else requires `/SyncStatus`. A client with static configuration can skip
discovery entirely, and on a segmented network it may have to (§12.1).

LSDP is the primary mechanism and the one to implement first. mDNS exists for
compatibility and is treated by the vendor's own clients as the less reliable
of the two.

### 12.1 LSDP — Lenbrook Service Discovery Protocol **[V]**

Lenbrook's own protocol, on **UDP port 11430**, using broadcast rather than
multicast. It exists because multicast is unreliable on a significant number of
consumer home networks, which made mDNS-based discovery fail often enough to
generate product returns.

**Query.** Clients send this eleven-byte packet, identical across the Android,
Windows and macOS controllers:

```
06 4C 53 44 50 01 05 51 01 FF FF
│  └─ LSDP ─┘  │  │  │  │  └─ class 0xFFFF (all)
│             │  │  │  └──── count = 1
│             │  │  └─────── 'Q' = 0x51, broadcast query
│             │  └────────── message length = 5
│             └───────────── protocol version = 1
└──────────────────────────── header length = 6
```

Sent to each interface's subnet-directed broadcast address (`ip | ~mask`),
falling back to `255.255.255.255` when no suitable interface exists. The
schedule is seven packets at t = 0, 1, 2, 3, 5, 7, 10 s, each with up to 250 ms
of jitter. The same seven-packet burst is specified for **any** state change,
not just client startup: a node advertising a new service sends seven
Announces, and a node withdrawing one sends seven Deletes. The redundancy is
deliberate — UDP is lossy — and if all seven are missed the 57 s announce cycle
recovers eventually.

**Packet structure.** Header: `length` (1) · `LSDP` (4) · `version` (1,
currently 1). Then message blocks, each starting with its own length byte so
unrecognised types can be skipped:

| Type | Byte | Body |
|---|---|---|
| Query | `Q` 0x51 | `count` (1), then `class` (2) × count. Responders answer by **broadcast**. |
| Query | `R` 0x52 | Identical body. Responders answer by **unicast** to the querier. |
| Announce | `A` 0x41 | `nodeIdLen` (1), `nodeId` (var), `addrLen` (1, always **4** in practice — IPv4), `addr` (var), `count` (1), then records |
| Delete | `D` 0x44 | `nodeIdLen` (1), `nodeId` (var), `count` (1), `class` (2) × count |

Announce record: `class` (2), `txtCount` (1), then per TXT record `keyLen` (1) ·
`key` · `valueLen` (1) · `value`. Multi-byte numbers are big-endian and
unsigned. Every length field exists so an unrecognised message or record can be
skipped rather than aborting the parse — build the parser that way, because the
version byte is only incremented for *incompatible* changes.

**A real Announce**, captured from a Bluesound Node N130 and preserved as a
test fixture in the `nightvision` library. Decoded field by field — **The node id is redacted.** It is a real device's MAC in the original fixture, replaced here and everywhere else in this repository with an RFC 7042 documentation MAC (`00-00-5E-00-53-xx`), the same convention `bluos-probe.py` uses for its own copy of this packet. Every length is unchanged, so the structure is exactly as captured; only those six bytes differ.



```
06 4C 53 44 50 01              header: len 6, "LSDP", version 1
73                             message length = 115
41                             'A' announce
06 00 00 5E 00 53 03           nodeId, 6 bytes (a MAC, redacted)
04 C0 A8 0A 0A                 address, 4 bytes = 192.168.10.10
02                             2 announce records
   00 01                       record 1: class 0x0001, BluOS Player
   05                            5 TXT records
      04 "name"    0E "Bluesound Node"
      04 "port"    05 "11000"
      05 "model"   04 "N130"
      07 "version" 07 "3.20.52"
      02 "zs"      01 "0"
   00 04                       record 2: class 0x0004, sovi-mfg
   02                            2 TXT records
      04 "name"    0E "Bluesound Node"
      04 "port"    05 "11431"
```

Three things this shows that a field table does not:

- **One Announce carries several records**, each its own class with its own TXT
  set and its own **port**. A player advertising both 0x0001 on 11000 and
  0x0004 on 11431 is normal; do not assume one node means one service.
- **TXT keys are richer than `port`.** Observed: `name`, `port`, `model`,
  `version`, and `zs` (meaning unconfirmed — plausibly a zone-slave flag, `"0"`
  here). Read the ones you need and ignore the rest.
- The record set differs per class: the manufacturing-test service advertises
  only `name` and `port`.

The matching Delete and Query packets from the same fixture set:

```
06 4C 53 44 50 01  0E 44  06 00 00 5E 00 53 03  02 00 01 00 04
                   └─ len 14, 'D', nodeId, 2 classes: 0x0001 and 0x0004

06 4C 53 44 50 01  07 51  02 00 01 00 04
                   └─ len 7, 'Q', 2 classes — a query may name several
```

**Everything observed is IPv4, and the clients enforce that.** The address
field is length-prefixed, and the vendor document says only “for IPv4 this shall
be 4” — permissive wording, but it never mentions another family. Every
first-party client filters to IPv4 explicitly: the macOS LSDP code skips any
interface whose `family !== "IPv4"`, its mDNS code filters resolved addresses
through `isIPv4()`, and the Android client does the same. The macOS LSDP parser
joins the address bytes with `.` unconditionally, so a 16-byte address would
come out as garbage rather than an error.

The Rust `lsdp` crate does map length 16 to IPv6, but that is a careful library
author covering a case the protocol leaves open — not evidence any player emits
one. **Treat LSDP as IPv4-only.** A defensive parser can reject any address
length other than 4 rather than trying to interpret it.

**In practice, clients parse only Announce.** The macOS controller's parser
switches on the message type and falls through to
`"Message Type Not Yet Handled"` for everything else, advancing by the length
byte. So Query and Delete are received and discarded. Two consequences:

- A player should not assume a controller acts on a **Delete**. Controllers
  detect departure by failing to reach the player, not by being told.
- Nobody sends **`R` unicast queries**, even though the protocol defines them.
  See the subnet note below — this is the one part of LSDP with obvious
  unrealised value.

**TXT keys.** Observed: `name`, `port` (defaulting to 11000), `model`,
`version` and `zs`. The Lenbrook controllers read only `port` and `version`;
`name` and `model` let a client show something useful before its first
`/SyncStatus` call. Unknown keys should be ignored, not treated as errors.

**Class IDs**, with their mDNS equivalents:

| Class | Meaning | mDNS |
|---|---|---|
| 0x0001 | BluOS Player | `_musc._tcp` |
| 0x0002 | BluOS Server | `_muss._tcp` |
| 0x0003 | BluOS Player, secondary node in a multi-zone chassis (e.g. CI580) | `_musp._tcp` |
| 0x0004 | sovi-mfg, manufacturing test | `_sovi-mfg._tcp` |

| 0x0005 | sovi-keypad | `_sovi-keypad._tcp` |
| 0x0006 | BluOS Player, pair slave | `_musz._tcp` |
| 0x0007 | Remote Web App (AVR OSD page) | `_remote-web-ui._tcp` |
| 0x0008 | BluOS Hub | `_mush._tcp` |
| 0xFFFF | All classes — query only | — |

Controllers accept only the four player classes: the check is
`class[0] == 0 && class[1] ∈ {1, 3, 6, 8}`, so the high byte must be zero.

**Timing.** Steady-state announce every 57 s ± 6 s. Query responses are delayed
0–750 ms at random. A node hearing a query for a class it advertises answers
after that delay and resets its announce timer. **The reply delay is confirmed
on hardware [V hardware]:** 20 broadcast query rounds against four players
(two N132, one N130 and one N110; one on Wi-Fi, three wired) gave 80
first-answer times with a
pooled mean of 390 ms and a median of 393, against the 375/375 a uniform
0–750 ms draw predicts, with all four players drawing from the same
distribution and no difference attributable to a player's own link. Run bundle:
`test-runs/lsdp-measure-20260912T185206Z/`. Node IDs are unique per node,
not per interface, and are the correct cache key. A single announcement may be
split across several messages when it cannot hold all of a node's info — the
CI580 is the cited case.

**`Q` and `R` differ in how the answer comes back, not how the query goes out
[V].** Both are queries and both are normally **broadcast** to port 11430. The
difference is what the responder does: after `Q` it broadcasts its Announce so
every listener on the segment learns about it; after `R` it unicasts the
Announce to the querier alone. `R` is therefore the polite form — one client
refreshing its own view without waking every other controller in the house. On
a busy network with many players and several controllers, `Q` means every
refresh is heard by everyone.

No shipping client sends `R`; all three send `Q` (`0x51`).

**Broadcast does not cross subnets [U].** UDP broadcast is not routed, so LSDP
finds nothing on another VLAN or subnet however well it works locally. Two
things suggest themselves before falling back to a configured address list
(§12.3). The first has since been tested and does not work:

- Send an `R` query **unicast** to a known player address. Nothing in the spec
  says a query must arrive by broadcast, and the responder already knows how to
  answer a single querier. **Tested, and it does not work [V hardware]:** a
  player answers neither a unicast `R` nor a unicast `Q`, while answering every
  broadcast `Q` in the same session. Claim `C-19`, DISCONFIRMED — a query has to
  arrive by broadcast to be acted on. Run bundles:
  `test-runs/lsdp-measure-20260914T180831Z/` (the broadcast control) and
  `…20260914T180935Z/` (unicast `R`, with replies listened for on 11430), plus
  the earlier `…20260913T171249Z/`, `…T171402Z/` and `…T171517Z/`.
- Send `Q` or `R` to the **remote subnet's directed broadcast address**. This
  needs the router to forward directed broadcasts, which is off by default on
  most consumer gear and a deliberate security choice. Whether a player answers
  a query that arrives that way has not been tried here, and it cannot be read
  off the `C-19` result: that one addressed a player directly, where this
  arrives as a broadcast on the player's own segment, which is the form players
  do act on.

With the first gone and the second needing a router that most consumer gear
will not give you, a configured address list plus `/SyncStatus` is the answer,
and it is what the vendor's own desktop clients fall back to.

**Two implementation traps [V]:**
- `SO_REUSEPORT` is Linux-only. Requesting it on macOS or Windows makes `bind()`
  fail with `ENOTSUP`, silently disabling discovery altogether.
- On macOS, a denied Local Network permission drops the broadcast traffic with
  **no error surfaced** to the sender. Discovery simply returns nothing.

### 12.2 mDNS **[V]**

Standard multicast DNS — no BluOS-specific framing, so any mDNS library works.

**Service types.** Four, fully qualified as `_musc._tcp.local.`,
`_musp._tcp.local.`, `_musz._tcp.local.` and `_mush._tcp.local.`, matching LSDP
classes 1, 3, 6 and 8. Browse all four: a stereo-pair slave advertises only
`_musz`, a hub only `_mush`, and a client watching just `_musc` will miss them.

The other LSDP classes have registered mDNS equivalents (`_muss._tcp` for BluOS
Server, `_sovi-mfg._tcp`, `_sovi-keypad._tcp`, `_remote-web-ui._tcp`) but no
controller browses for them.

**What to read from a resolved service:**

| Field | Use |
|---|---|
| SRV port | The control port. **Take it from the record** — this is how a CI580's four nodes are told apart on one address. |
| A record | IPv4 address. Both clients filter to IPv4 and use the first match; IPv6 is ignored. |
| TXT `version` | Firmware version. The only TXT key either client reads. |

The device id is `<address>:<port>`, the same form as the `id` attribute in
`/SyncStatus`, so the two discovery paths and the HTTP layer agree on identity
without extra work.

**Resolution is two-stage.** A service-added event carries only a name and
type; the Android client calls `requestServiceInfo` and waits for the resolved
event before it has an address or port. Budget for that round trip — a player
is not usable at the moment it is first seen.

**Departure handling differs by client**, which says something about how much
either trusts it. The desktop client listens for `down` events and reports the
device lost; the Android client implements `serviceRemoved` as an empty method
and ignores it entirely.

**Both desktop clients tear down and rebuild the entire mDNS browser every ten
seconds** (`setInterval(resetBonjour, 10000)`). That is an aggressive workaround
for the same multicast unreliability that motivated LSDP, and a strong hint
about what to expect. Treat mDNS as a supplement to LSDP, not a replacement —
and if you implement only one, implement LSDP.

### 12.3 Static configuration **[V]**

The desktop controllers read a `staticPlayers.txt` file from their user-data
directory: a comma-separated list of player addresses, each optionally
`ip:port`. Players listed there are used directly, with no discovery. This is
the right approach for a server-side client on a known network.

**It is also documented by the vendor**, which the code-level reading above did
not make clear. Bluesound Professional publishes it as the way to reach players
from a remote subnet, with the Windows path and the file format:

| field | value |
|---|---|
| Path (Windows) | `C:\Users\<user>\AppData\Roaming\BluOS Controller\staticPlayers.txt` |
| Format | one comma-separated line of `ip:port`, no spaces |
| Vendor example | `192.168.0.1:11000,192.168.0.1:11010,192.168.0.1:11020,192.168.0.1:11030` |

The example is **one address with four ports**, which is a four-zone chassis
rather than four players — consistent with class `0x0003` and with the SRV-port
note in §12.2, both of which exist because a CI580's four nodes share an
address. For a single-zone player the vendor says to list only `<ip>:11000`.

Two limits are stated outright, and both matter when judging what this feature
is for:

> This method is not meant for grouping players and is not designed to support
> grouping multiple players across different subnets.
>
> This setup can be performed only using the Windows or macOS version of the
> BluOS Controller app.

So it is unavailable on Android, and it is a reachability feature for
professional installs rather than a general configuration mechanism.

**The listed players are added to discovery's results, not substituted for
them [V official].** The desktop app reads the file in a module that runs
*alongside* its LSDP and Bonjour modules, and hands each entry to the same code
path an announce goes through — a version fetch and a `/SyncStatus`, into the
same device store — after checking that discovery has not already found that
address. So "used directly, with no discovery" describes what the feature is
for, not a code path the app skips: nothing about the file changes what a
player must answer, or when. How the app behaves with it is
`controller-code-notes.md`; what it costs the user is
`controller-discovery-timings.md`.

Source: [How to Discover and Control Players from a Remote
Subnet](https://support.bluesoundprofessional.com/hc/en-us/articles/360060411413-How-to-Discover-and-Control-Players-from-a-Remote-Subnet),
Bluesound Professional.

---

## 13. The port 80 surface **[V]**

Players expose a second HTTP surface on **port 80**, separate from the control
API on 11000. It serves the player-hosted settings web UI and a small number of
endpoints that have no equivalent on 11000.

The split is a migration artefact. A comment in the Windows client explains it:
the legacy `ms` service serves `/ui` endpoints on port 80 while the newer
`ms-go` serves port 11000, and the intention is for all `/ui` endpoints to move
to 11000 once the migration completes.

**The migration has progressed.** On firmware 4.16.22, `/ui/Configuration`
answers on **port 11000** (§10.2), and unknown paths there return Go's default
404 page — so `ms-go` is now fronting the control port. Probe both ports rather
than assuming either split or consolidation.

| Endpoint | Method | Notes |
|---|---|---|
| `/Shares` | GET | Lists configured SMB/network shares. See below. |
| `/AddShare` | POST | `application/x-www-form-urlencoded` with `sharename`, `username`, `password`. |
| `/RemoveShare` | POST | `application/x-www-form-urlencoded` with `sharename`. |
| `/upgrade?noheader=1` | GET | Firmware upgrade page as HTML, intended for embedding in a WebView. `noheader=1` suppresses the page chrome. |
| `/diagnostics` | GET | **[V hardware]** The diagnostics page as HTML — the source of the official apps' “Diagnostics” screen. `blutui` scrapes it by reading `div.ui-block-a` as the key and `div.ui-block-b` as the value of each row. **Port 80 only**; it does not answer on 11000. May expose fields no XML endpoint returns. |
| `/ui/Configuration?playnum=1` | GET | Settings UI, reached by redirect from port 11000. |

`/Shares` response, confirmed on four players:

```xml
<shares count="1">
  <share>
    <sharename>\\192.168.1.5\music</sharename>
    <username>bluesound</username>
  </share>
</shares>
```

`<shares count>` wraps repeated `<share>`, each carrying `<sharename>` and
`<username>` as **text elements**. Share names use Windows UNC form with
backslashes. **The password is never returned.**

**Authentication crosses the port boundary awkwardly.** On a player that
requires credentials, `/ui/Configuration` on port 11000 challenges first, and a
successful authentication then redirects to `/ui/Configuration?playnum=1` on
port 80 — which challenges again, because the credential cache is scoped per
origin and the origin has changed. The redirect is not flagged distinguishably
from a failed login, so the Windows client simply replays the same credentials
for a bounded number of attempts rather than re-prompting. A client that
prompts on every challenge will ask the user twice for the same password.

**The `sovi://` URL scheme** has two uses. `sovi://player/<path>` appears in
server-driven UI and resolves against the **port 80** base, not 11000. Bare
`sovi://player?...` is also used as an OAuth return target: services that
authenticate in an external browser (Amazon Music, for example) redirect back
to it, and the desktop controllers register as the system handler for the
scheme so the redirect reopens the app.

---

## 14. Group merging — nesting, not merging **[V]**

Established by hardware testing, and consistent with the client code.

### 14.1 What the device does

| `/AddSlave` target | Result |
|---|---|
| A player that is already a **slave** of another group | **No effect.** |
| A player that is already a **master** of another group | **A nested group is created.** The call is accepted and returns a normal `<addSlave><slave .../></addSlave>`. |

The nesting case, in detail. Given group A (master A, slaves A1/A2) and group
B (master B, slaves B1/B2), calling `/AddSlave` on **A** with **B** as the
target:

- B becomes a slave of A and plays what A plays.
- B's own slaves B1/B2 remain slaves of **B**, and follow B — which is now
  following A.
- Net effect: every player in both groups plays the same audio.

So the audio result looks like a merge, but the topology is a two-level tree,
not a flat group. B is simultaneously a slave (of A) and a master (of B1/B2),
and its `/SyncStatus` carries `<master>` and `<slave>` elements side by side:

```xml
<SyncStatus ... group="Kontor+Sovevaerelse" ...>
  <master port="11000">192.168.1.10</master>
  <slave id="192.168.1.40" port="11000" name="Sovevaerelse" model="N110"/>
</SyncStatus>
```

Note that the nested master keeps reporting **its own** subgroup name in
`group`, while its slaves report the **top-level** group name in `/Status`
`<groupName>`. The two disagree by design; neither is wrong.

**Commands recurse through the tree [V hardware].** `/Volume?tell_slaves=1`
and `/Pause` addressed to the top master both reach the grandchild. Group
volume and transport are therefore *not* broken by nesting — only the client's
topology model is.

**Two levels were tested and no depth limit was found.** The master/slave
relation appears to be generic rather than special-cased for a single tier, so
deeper trees are plausible but unverified. A client should not assume a maximum
depth; recurse.

**Recovery.** A player hidden by nesting reappears as soon as the group is
dissolved — the ordinary "ungroup" action in the Controller app is enough. No
power cycle or `force=1` is needed.

This is not reachable through the BluOS Controller: the app forbids grouping a
player that is already a master or a slave (`canGroup()`), and there is no
merge-groups affordance anywhere in the UI. The device accepts the call
regardless — the restriction is purely client-side.

### 14.2 Why the nested master's slaves vanish from the app **[V]**

Worth understanding, because it is a client bug rather than a device
behaviour, and a custom client does not have to inherit it.

Once nested, B's `/SyncStatus` reports a `<master>` element **and**
`<slave>` elements at the same time. The app's predicates assume those are
mutually exclusive:

```
isSlave()  = master != null                       → true  for B
isMaster() = master == null && slaves.isNotEmpty() → false for B
isNormal() = master == null && slaves.isEmpty()    → false for B
```

In `PlayerDiscoveryState`, a player is added to `selectablePlayers` only if
`isMaster() || isNormal() || isReconnectingToMaster()`. B satisfies none of
them, so B is **removed from the selectable list** and attached as a slave
under A.

B1 and B2 are then processed as slaves: each scans `selectablePlayers` for the
player whose host equals its master (B). B is no longer in that list, so the
scan finds nothing, they are attached to no parent, and — being slaves — they
are removed from `selectablePlayers` too.

The result is that B1 and B2 exist on the network, are playing, and are
referenced by B's `<slave>` elements, but appear nowhere in the app's player
list. There is also an ordering dependency here: which of B or its slaves is
processed first is not guaranteed.

**Implication for a custom client:** do not treat master and slave as mutually
exclusive. Model the topology as a general tree. `hasMaster` and `hasSlaves`
are independent booleans, and a player can be both.

### 14.3 Practical guidance

Treat group merging as unsupported. To combine two groups, dissolve the second
group first (`/RemoveSlave` for each of its members addressed to B, or a bare
`/SetMaster` to each member — see §5.3), then add the now-free players to A
individually or in one batched call. Nesting will
technically produce synchronised audio, but it produces a topology neither the
official app nor most clients will render correctly, and it is clearly not an
intended configuration.

---

## 15. Relationship to the vendor Custom Integration API

The official *BluOS Custom Integration API* v1.7 and this document describe
**two different surfaces on the same device**. Neither supersedes the other.

| | Official CI API | App protocol (this document) |
|---|---|---|
| Audience | System integrators | The Controller app |
| Stability | Contractual, versioned, revision-tracked | Unversioned; changes with app releases |
| Browsing | `/Browse?key=…` — one endpoint, opaque keys | Follow device-supplied URLs into `/Songs`, `/Albums`, … |
| Coverage | Deliberately a subset | Everything the app can do |
| Legal footing | Published under an API Use Policy | Reverse-engineered |

### 15.1 `/Browse` — a stable facade no first-party client uses **[V]**

`/Browse` is the vendor's stable browsing facade. None of the three BluOS
Controller apps use it — the strings `Browse`, `browseKey`, `playURL`,
`contextMenuKey`, `nextKey` and `parentKey` appear in none of them; the
controllers browse by following `url` attributes into the typed endpoints
of §8.

**The Lenbrook-authored RTI driver does use it**, which is the strongest
available evidence that `/Browse` is the intended path for integrations. Its
service enumeration is a bare `GET /Browse` with no `key`, and its response
parser reads exactly the attributes the vendor document specifies —
`serviceIcon`, `serviceName`, `service`, `searchKey`, `nextKey`, `parentKey`,
`type`, plus `<category text nextKey parentKey>` wrapping `<item>` elements.
That is an independent confirmation of the shape below.

```
GET /Browse                              # top level
GET /Browse?key=<urlencoded-key>         # descend
GET /Browse?key=<searchKey>&q=<text>     # search
GET /Browse?key=<key>&withContextMenuItems=1
```

Root `<browse>` with `type`, and where applicable `service`, `serviceName`,
`serviceIcon`, `searchKey`, `nextKey`, `parentKey`. The `sid` attribute shown
in the vendor document's examples is **absent** on firmware 4.16.22 — treat it
as optional. This is not academic: the Rust `bluos-api-rs` library declares
`sid` as a required field and would fail to deserialise a current response.

Confirmed live on 4.16.22. A bare `GET /Browse` returns the source list:

```xml
<browse type="menu">
  <item browseKey="BluOS:" text="Playlists" image="/images/ci_myplaylists.png" type="link"/>
  <item playURL="/Play?url=Capture%3Ahw%3Aimxspdif%2C0%2F1%2F25%2F2%3Fid%3Dinput2"
        text="HDMI ARC" image="/images/capture/ic_tv.png" type="audio" inputType="arc"/>
  <item browseKey="LocalMusic:" text="Library" type="link"/>
  <item browseKey="Airable:" text="Radio" type="link"/>
  <item browseKey="Tidal:" text="TIDAL" type="link"/>
</browse>
```

Descending with `?key=Tidal:` adds `serviceIcon`, `serviceName` and
`searchKey`.

Filtering the root for `type="audio"` items with a `playURL` is how
`bluesound_alt` builds its input/source list — a simpler route to the physical
inputs than `/RadioBrowse?service=Capture` or `/Play?inputIndex=`, and it needs
no knowledge of input types at all.

**Filter out empty items [T].** Blu4Net drops any `<item>` whose `text` is
absent, citing TuneIn. **Not reproduced**: the TuneIn root returned ten
well-formed items with no empty elements. Either the quirk was fixed, or it
occurs on a deeper page. Cheap to guard against regardless, since browse
responses are generated per service. Note that `<item type="audio">` on the root carries a `playURL`
and an `inputType`, so **physical inputs appear in the browse tree alongside
streaming services** and can be selected without touching `/Play?inputIndex=`.

Browse keys are opaque, but their observed shape corroborates the service
subtree of §11.2: `Tidal:MG/Tidal-New` is a `menuGroup`, `Tidal:GG/Moods` a
`genreGroup`. Do not parse them — the correspondence is a sanity check, not an
interface. `type` is one of `menu`, `contextMenu`,
`artists`, `composers`, `albums`, `playlists`, `tracks`, `genres`, `sections`,
`items`, `folders`. Results are `<item>` elements, sometimes wrapped in
`<category text nextKey parentKey>`.

`<item>` attributes: `type` (`link`, `audio`, `artist`, `composer`, `album`,
`playlist`, `track`, `text`, `section`, `folder`), `text`, `text2`, `image`,
`browseKey`, `playURL`, `autoplayURL`, `contextMenuKey`, `actionURL`.

Capability is signalled by attribute presence: `browseKey` means descendable,
`playURL` means playable, and an item may have both. Inline context menus
(`withContextMenuItems=1`) nest a `<contextMenu>` of `<item text type
actionURL>` inside each item, with `type` values like `favourite-add`,
`add-now`, `add-next`, `add-last`, `addAll-now`, `addAll-next`, `addAll-last`,
`add-shuffle`, `playRadio`, `delete`.

Errors use the same `<error><message><detail>` envelope as §0.1.

**Which to build against.** `/Browse` for anything long-lived: it is
contractual, hides per-service differences, and its keys are opaque so
Lenbrook can restructure behind them. The typed path of §8 only when you need
something `/Browse` does not expose — the `<sortMenu>`/`<selectorMenu>`
affordances (§11.12), section/jump-bar indexes (§11.10), or the full component
model (§11.11). Note that all keys must be URL-encoded when passed back, and
that paging chunk size is not under client control: follow `nextKey` verbatim.

### 15.2 Endpoints only in the vendor spec **[V]**

These appear in none of the three Controller apps. Where a Lenbrook
integration driver does use one, that is noted — such endpoints are safe to
rely on:

| Endpoint | Notes |
|---|---|
| `/Browse` | §15.1. |
| `/Stop` | `<state>stop</state>`. `/Play` will not resume from `stop`. Also used by the Windows controller and the RTI driver, so it is not integration-only. |
| `/Pause?toggle=1` | Toggle rather than force. |
| `/Volume?abs_db=`, `/Volume?db=` | Absolute and relative dB. |
| `/Doorbell?play=1` | Returns `<status enable volume chime/>`. |
| `/reboot` | **POST**, form field `yes=1` (any value). Returns HTML, not XML. Distinct from `/update?doit=1`. |
| `/audiomodes` | Writes audio and source settings. `bluetoothAutoplay=0\|1\|2\|3` is Manual / Automatic / Guest / Disabled. Also accepts `subwoofer`, `replayGainMode`, `channelMode`, `mqaDisable`, `enableClockTrim` and `ears` — see §10.3, which is where a client learns each parameter name and its legal values. Note `centre` writes to `/setting`, not here. No response body. |
| `/Play?inputIndex=<n>` | **Correct and working on 4.16.22** — returns `<state>stream</state>` and switches away from whatever was playing. The vendor document's `InputId` spelling is wrong: `/Play?InputId=2` behaves as a bare `/Play` (resume), because an unknown parameter is simply ignored. |
| `/Play?inputTypeIndex=<type>-<n>` | Firmware ≥ 4.2.0. Types: `spdif`, `analog`, `coax`, `bluetooth`, `arc`, `earc`, `phono`, `computer`, `aesebu`, `balanced`, `microphone`. Index starts at 1 per type. |
| `/Play?inputType=<type>&index=<n>` | **[T]** A separate two-parameter form, documented by the Rust `bluos-api-rs` library as `analog`, `spdif`, `hdmi` or `bluetooth`, with `index` defaulting to 1. Not in the vendor document and not sent by any first-party client, but plausible: `inputType` is a real attribute on `/RadioBrowse?service=Capture` items and on `/Browse` root entries. Untested — see T-27. |
| `/Preset?id=+1` / `id=-1` | Next / previous preset, wrapping at both ends. Distinct from `/ExternalSource?id=+`. **Used by the Integration Utility.** |
| `/Pause?toggle=1` | **Used by the Integration Utility.** |
| `/Volume?db=±2` | **Used by the Integration Utility** for volume up/down. |

`inputTypeIndex` is the recommended way to select an input, because it works
for **inactive** inputs that never appear in `/RadioBrowse?service=Capture`.

> **A second error in the official document, now confirmed.** §11.2 specifies
> `/Play?inputIndex=` in its parameter table and `/Play?InputId=` in its worked
> example. The parameter table is right. On hardware `InputId` is silently
> ignored, so `/Play?InputId=2` merely resumes playback — which looks like
> success if something was paused. Use `inputIndex`.

### 15.3 Cross-confirmed facts

Independently corroborated by two or more of the three sources:

- **`/Repeat` values.** `0` = repeat queue, `1` = repeat track, `2` = off —
  exactly the mapping derived from `TransportControlsFragment` in §3.
- **`<volume>-1</volume>` means fixed volume**, confirming that
  `isFixedVolume` is derived rather than transmitted (§2.2).
- **`<master port reconnecting>`** and **`<slave id port>`**, including the
  `reconnecting` attribute (§2.1).
- **Radio browse.** `<radiotime service>` containing `<category text icon>`
  and interchangeable `<item>` / `<remoteitem>` — precisely the odd shape
  enumerated from `RadioResultHandler` (§11.10). Official attributes for those
  items: `text`, `id`, `URL`, `image`, `type`, `inputType`, `playerName`,
  `serviceType`, matching the `Item` model's constants.
- **`/Save?name=`**, **`/Playlist?start=&end=`**, **`/Play?seek=&id=`**,
  **`/Play?url=`** — all four were flagged as missing from the original
  document and all four are officially specified.
- **The ≥1 s long-poll spacing** found in `PlayerManager` is a stated
  requirement: consecutive requests for the same resource must be at least one
  second apart. Without long-polling, poll at most **once every 30 seconds**.
- **Discovery.** All three clients send the identical eleven-byte LSDP query on
  the same schedule, and accept the same four player classes. See §12.
- **Upgrade roots.** Both clients test for `UpgradeStatusStage1` /
  `UpgradeStatusStage2` before `SyncStatus`, including inside `<zoneSlave>`.
- **Settings URL precedence.** Both prefer `<audioPresetUrl url>` and fall back
  to `<soundbar_settings url>`.
- **`/SetPreset` parameters.** Both send the same set, including `shuffle` and
  `canShuffle`.

---

## 16. Open questions **[U]**

Test procedures are in `HARDWARE-TESTS.md`. Nearly everything has now been
settled on hardware (Bluesound N110 / N130 / N132, firmware 4.16.22, schema 34).

**Still open, by choice or circumstance:**

1. **Nesting beyond two levels.** Two levels confirmed working with correct
   command propagation; no depth limit found. Deeper testing deprioritised —
   the relation looks generic, so recursion is the safe assumption.
2. **Authentication.** No way found to set credentials on a consumer N-series
   player, so the auth path (§1.1) is unexercised. It may be CI-hardware only.
3. **`/Load` and `/AddFavourite` parameters.** `/Load` is confirmed to exist and
   to be the form playlist presets take (§6.1); its full parameter set and
   response are untested.
4. **`/AddShare` and `/RemoveShare`** — destructive, deliberately deferred.
5. **`/Play?inputTypeIndex=`** returned an empty body once. Inconclusive:
   BluOS has a "source must be active to switch" behaviour that may explain it.
6. **The concurrency ceiling.** 24 simultaneous held long-polls succeeded; the
   limit was not found.
7. **Player enumeration outside a group.** A master describes its own slaves
   fully; nothing found lists others.
8. **Whether `/Name` survives a reboot.**
9. **Whether any firmware still serves `/GetSettings` as JSON** (§10.1).
10. **Per-service browse element sets** — samplable, never closable.
11. **Whether `<is_preset>` exists in `/Status`** (§2.2). Reported by Blu4Net.
    The check was inconclusive — the preset recall and the status read hit
    different players. Retry on one player that has presets.
12. **Whether descending sort is reachable.** The client reads a `reverseName`
    attribute on `<sort><value>` (§8.2) but no observed `/Services` sends one.
    Either no service offers it, or it is newer than schema 34.

## 17. Register of third-party claims **[T]**

Everything in this document marked **[T]** comes from an independent
implementation rather than from Lenbrook code, the vendor document, or these
players. It is listed here in one place because the marker is easy to skim past,
and because the risk runs both ways. `/diagnostics` came from a single
third-party source, was reported as failing on hardware, and turned out to be
real — the check had been aimed at the wrong port. A claim is not settled until
it has been tested **the way the source describes it**, which for the port 80
surface means port 80.

Each row carries a **permanent id**. Ids are never reused and rows are never
deleted: a claim tested and found false keeps its row and gains a verdict, so
the next reader who meets it in a third-party project can see it was already
checked, when, against what, and with what result. `INCONCLUSIVE` and
`NOT ANSWERABLE` are real results and neither means false — do not implement
against either.

Verdicts below are from hardware runs on 2026-09-10: four players (N132, N132,
N130, N110), firmware 4.16.22, schema 34, with the `bluos-probe` harness.

| Claim | § | Source | Status |
|---|---|---|---|
| `/diagnostics` on port 80 | 13 | blutui (Rust) | **Confirmed on hardware.** Port 80 only — it 404s on 11000, which is what an initial mis-aimed check reported |
| `/proxyToSlave` POST relay to a slave | 10.0 | blutui (Rust) | Untested — T-34 |
| `/audiomodes` as a read endpoint | 10.4 | BluShell | Untested — T-32 |
| Setting writes as POST form vs GET query | 10.3 | blutui vs pyblu | **Settled [V hardware]:** the GET query form works, the POST form did not. See below. |
| `/Name` POST with `nodename=` | 10 | blutui (Rust) | Untested; `?set=` is confirmed |
| `/SlaveVolume` with combined `slave=<ip>:<port>` | 4 | blutui (Rust) | Untested; separate `slave`+`port` is documented |
| `/Sync?slave=` / `?remove=` legacy grouping | 5.2 | bluos-dashboard | Untested — T-30 |
| Orphaned-group recovery by reparenting | 5.1 | bluos-dashboard | Untested — T-29 |
| `port` optional in singular `/AddSlave` | 5 | 2015 forum | Untested |
| Polymorphic play response | 7.3 | Blu4Net | **Two of four roots** now have samples — T-28 |
| `/Play?inputType=&index=` | 15.2 | bluos-api-rs | Untested — T-27 |
| `/Artwork` returning `<artwork>none found</artwork>` | 9 | BluShell | Untested — T-33 |
| `/Artwork?album=&artist=` by name | 9 | 2015 forum, BluShepherd | Untested |
| `<is_preset>` in `/Status` | 2.2 | Blu4Net | Untested — T-22. Confirmed only as a `/RadioPresets` attribute |
| `total_count` on `<radiotime>` | 11.10 | Blu4Net | Untested |
| `key` / `is_active` on radio items | 11.10 | Blu4Net | Untested — `is_preset` and friends confirmed by a BluShell sample |
| `guide_id`, `item`, `preset_id`, `subtext` on `/RadioPresets` items | 11.10 | BluShell sample | Sample-backed, schema 25 |
| TuneIn empty `<item></item>` | 15.1 | Blu4Net | **Not reproduced** on 4.16.22 |
| Album-scoped `/Songs` wrapper, `<discno>n/m</discno>` | 11.10 | BluShepherd, 2016 | Untested on current firmware |
| `/Alarms` `days` bitmask, `/Search` containers, `/audiomodes` attributes | 11.6, 11.10, 10.4 | BluShell samples | Sample-backed at schema 25, not re-checked at 34 |

### 17.1 Hardware verdicts, 2026-09-10 **[V hardware]**

Four players (N132 ×2, N130, N110), firmware 4.16.22, schema 34.

| id | claim | source | verdict | evidence |
|---|---|---|---|---|
| `C-01` | `/diagnostics` answers on port 80 | blutui (Rust) | **CONFIRMED** | 200 HTML on 80, two players |
| `C-02` | `/diagnostics` does *not* answer on 11000 | this project | **CONFIRMED** | 404 |
| `C-03` | bare `/audiomodes` is a read | BluShell | **CONFIRMED** | 200 on 11000, 404 on 80 and 11001 |
| `C-04` | `/proxyToSlave` exists | blutui (Rust) | **CONFIRMED** | 400 with no parameters — the path exists |
| `C-05` | the legacy `/Sync` path still exists | bluos-dashboard | **DISCONFIRMED** | 404 |
| `C-06` | `/GetSettings` exists, returns JSON | Integration Utility 1.8.1 | **DISCONFIRMED** | 404 on all three ports |
| `C-16` | `/Shares` has migrated to 11000 | conjecture | **DISCONFIRMED** | 404 on 11000, 200 on 80 |
| `C-17` | `<is_preset>` in `/Status` | Blu4Net | **DISCONFIRMED** | absent while a preset played |
| `C-19` | an LSDP `R` query sent by unicast is answered | vendor wire format | **DISCONFIRMED** | 20 rounds, no answer. A unicast `Q` control is equally unanswered, so what is ignored is unicast delivery, not the `R` form |
| `C-20` | `sid` is required on `/Browse` | bluos-api-rs | **DISCONFIRMED** | `/Browse?sid=0` returns 200 |
| `C-21` | omitting `X-Sovi-Schema-Version` changes the response | inference | **CONFIRMED** | `/Services` body differs |
| `C-23` | port 11001 serves settings and nothing else | this project | **CONFIRMED** | 404 for `/Status`, `/SyncStatus`, `/Shares`, `/Services`, `/ui/Configuration` |
| `C-24` | some endpoint enumerates players | open question 7 | **DISCONFIRMED** | `/Players`, `/Devices`, `/Zones`, `/Groups` all 404 |
| `C-30` | a bare `/RemoveSlave` drops every slave | HA integration | **DISCONFIRMED** | two slaves remained |
| `C-34` | `/Name` accepts `POST nodename=` | blutui (Rust) | **CONFIRMED** | name changed |
| `C-35` | setting writes are POST form, not GET query | blutui vs pyblu | **DISCONFIRMED** | the GET query took effect; the POST form did not |
| `C-36` | `mute=1` mutes, `mute=0` unmutes | app vs CI API v1.7 | **INCONCLUSIVE** | `/Volume` carries no `mute` attribute on this firmware |
| `C-37` | `/Play?inputType=&index=` selects an input | bluos-api-rs | **CONFIRMED** | source changed |
| `C-39` | roles can be swapped without ungrouping | this project | **DISCONFIRMED** | produces a mutual master loop — §5.3 |
| `C-40` | bare `/Repeat` and `/Shuffle` read rather than write | untested | **DISCONFIRMED** | bare `/Shuffle` wrote `1 → 0` |
| `C-41` | bare `/SetMaster` on a standalone player is a no-op | hardware | **CONFIRMED** | |
| `C-42` | bare `/SetMaster` on a master is a no-op | hardware | **CONFIRMED** | group survived |
| `C-43` | bare `/SetMaster` on a slave leaves the group | hardware | **CONFIRMED** | |
| `C-44` | `?master=` joins that group | hardware | **CONFIRMED** | but one-sided — §5.3 |
| `C-45` | `?slave=` is ignored by `/SetMaster` | hardware | **CONFIRMED** | |
| `C-46` | `?master=` answers with the pre-call `SyncStatus` | hardware | **CONFIRMED** | six cases, `etag` unchanged |
| `C-47` | `port` is optional on `?master=` | untested | **CONFIRMED** | |
| `C-48` | `?master=<own address>` is handled gracefully | untested | **DISCONFIRMED** | the player becomes its own master |
| `C-49` | `?master=<not a player>` is handled gracefully | untested | **CONFIRMED** | no change |
| `C-50` | a slave can be reparented with `?master=` | bluos-dashboard | **CONFIRMED** | old master's slave list cleared |
| `C-51` | bare `/SetMaster` detaches a nested master cleanly | untested | **CONFIRMED** | its own slaves retained |
| `C-52` | a disabled input still appears in some API surface | this project | **INCONCLUSIVE** | display names differ across surfaces for innocent reasons |
| `C-53` | a disabled input is still selectable through the API | this project | **DISCONFIRMED** | every unadvertised slot was ignored. Weakened: only one input was learnable |
| `C-54` | membership from `?master=` is one-sided | this project | **CONFIRMED** | §5.3 |
| `C-55` | bare `/SetMaster` answers with a *fresh* `etag` | this project | **CONFIRMED** | unlike `?master=` |

### 17.2 Not answerable on this hardware

Distinct from `INCONCLUSIVE`, and **not** to be recorded as disconfirmed: a
negative result here would be a fact about the fleet, not about the protocol.

- **Authentication (T-14).** No way found to set credentials on a consumer
  N-series player. §1.1 stays source-derived and unexercised.
- **CI-series multi-zone port offsets.** No CI hardware.
- **Subwoofer pairing** (`pairSlave`, `slaveChannelMode=subwoofer`). No paired
  subwoofer in the fleet.
- **Three-level nesting (T-16).** Needs a fourth player in the right topology.
- **Orphaned-group recovery (T-29).** Needs a primary powered off mid-group.

### 17.3 How to use this

If you are implementing something still marked untested, test it first — the
cost is one `curl` and a 404 is a clean answer (§0.1). Then **append a row**
above rather than editing one: if a later firmware changes an answer, the old
row stays and the new one is added, so the history is visible. Never reuse an
id for a different claim.

**Absence from a capture never disconfirms a [V] claim.** Most elements here
are conditional: `<preset_name>` only while a preset plays, `<slave>` only on a
master, `muteDb` only while muted. If first-party code reads a field and no
capture contains it, the field is conditional — document *when* it appears
rather than deleting it. Only an explicit contradiction demotes a `[V]`.

**What is not on this list is not third-party.** Everything else in this
document traces to Lenbrook client code, the vendor specification, or a capture
in `captures/`.

---

## Claims examined and rejected

Not everything a third-party client does is real. These were considered and
deliberately left out.

| Claim | Source | Why rejected |
|---|---|---|
| `/Standalone` and `/LeaveGroup` to leave a group | `bluesoundplayer` (Dart) | Both are issued inside `try {} catch (_) {}` with the error swallowed and no verification, and the surrounding comments read as guesses. A verified mechanism already exists: a bare `/SetMaster` on the slave (§5.3). |
| LSDP carries IPv6 addresses | `lsdp` (Rust) | The crate maps address length 16 to IPv6, but no player has been seen emitting one and every first-party client filters to IPv4 explicitly (§12.1). |
| `<is_preset>` as a `/Status` element | Blu4Net | Kept as **[T]** only. `is_preset` is confirmed as an attribute on `/RadioPresets` items (§11.10), which is the likelier origin of the claim. |
| TuneIn returns empty `<item></item>` | Blu4Net | Not reproduced — the TuneIn root returned ten well-formed items. Kept as a cheap defensive note, downgraded (§15.1). |
| `/AddSlave` takes `channelMode=0\|1\|2` for stereo/left/right | `bluos` HA integration | **Conflicts with better evidence.** Everywhere else `channelMode` is a string — `default`, `left`, `right`, `mono` — both in `/SyncStatus` and in the audio settings tree (§10.3). The integration may be describing a different parameter, or guessing. Left out until tested (T-36). |
| `/RemoveSlave` with no parameters ungroups every slave | `bluos` HA integration | Plausible and useful, but asserted without evidence in a project that also gets `channelMode` questionably. Untested (T-36). |

---

**Resolved on hardware:**

| Question | Answer |
|---|---|
| Concurrent long-polls | ≥ 24 held simultaneously, all released on schedule. No low cap. §1.3 |
| Group nesting | Real. `<master>` and `<slave>` coexist; volume and transport recurse. §14 |
| `/SetMaster` | Slave-side grouping: bare call leaves, `?master=` joins. §5.1 |
| Role reversal | Not rejected. Pointing a master at its own slave produces a mutual master loop; role is fixed at group formation. §5.3 |
| `/AddSlave` rejection | Empty `<addSlave></addSlave>`, HTTP 200. §5 |
| Path case-sensitivity | Exact match. `/upgrade` works, `/Upgrade` 404s. §1.6 |
| `inputIndex` vs `InputId` | `inputIndex` is correct; `InputId` is ignored. §15.2 |
| `/PlayTestSound` | Both forms work but play different sounds. §3 |
| `/Sleep?minutes=` | Accepts any integer, not only 0/15/30/45/60. §3 |
| `/Repeat` validation | Rejects out-of-range with `<error><message>invalid state</message></error>`. §3 |
| `/Shuffle` validation | None — silently ignores out-of-range values. §3 |
| `/Name` | Bare call reads, `?set=` writes; both return `<name>`. §10 |
| `/Browse` | Works on current firmware; `sid` is optional. §15.1 |
| `/Shares` | `<shares count>` of `<share>` with text children. §13 |
| Nesting depth | Two levels verified, no limit found, commands recurse. §14 |
| Audio-settings vocabulary | `<dependsOn>`, `range`, `dual-range` unchanged from schema 28 to 35. §10.3 |
| Sorting and filtering | Declared in `/Services` per list, applied as a query parameter. §8.2 |
| Tidal favourites by date added | `/Songs?service=Tidal&category=FAVOURITES&sort=recent`. §8.2 |
| TuneIn empty browse items | Not reproduced on the TuneIn root. §15.1 |
| Failure bodies | Some are HTML, not XML. §0.1 |
| Recovering a hidden player | Ordinary ungroup in the app is enough. §14 |
| `/Settings` | Served on **port 11001**; that port serves settings only. §10.3 |
| Unknown paths | Bare 404 `text/plain`, not an error envelope. §0.1 |
| Stale or invented etag | Returns immediately; does not hold. §1.9 |
| `/GetSettings` | 404 on 4.16.22. §10.1 |
| `/ui` port | Answers on 11000, not only 80. §10.2, §13 |
