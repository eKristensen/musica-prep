# Musica — work plan

TODO: Include motivation wishlist in plan.

A self-hosted web app on the home server, reachable from the phone over LAN or
WireGuard. Players are configured by IP; everything else comes from the players
over the HTTP/XML API.

Companion documents:

- `README.md` — what this is and why.
- `MOTIVATION.md` — the survey of alternatives and where each falls short.
- `DECISIONS.md` — standing architectural decisions. **Read first.**
- `docs/bluos-http-api.md` — the protocol reference. **Source of truth** for
  anything wire-level; this plan does not restate endpoint details. Maintained
  separately and dropped in whole; do not fork or patch it here. It is
  gitignored and never committed (D16).
- `docs/protocol-notes.md` — the committed protocol record, written as endpoints
  are implemented and limited to what the code depends on.

---

## Acceptance criteria

Six requirements, from `MOTIVATION.md`. Nothing that exists satisfies all six.

| # | Requirement | Where |
|---|---|---|
| R1 | A real GUI, not a CLI or a Home Assistant card | Tier 0–1 |
| R2 | Manual player entry as the primary mechanism | Config, D11 |
| R3 | Browsing with sorting, specifically Tidal | Tier 3.4; Tier 3b makes it fast |
| R4 | Search that works | Tier 3 |
| R5 | Grouping that works | Tier 2 |
| R6 | Built in a language worth maintaining | D1, D2, D3 |

---

## Architecture

```
   players  ──HTTP/XML long-poll──▶  server daemon  ──SSE──▶  browser
   (fixed IPs from config)           (holds all state)        (phone / laptop)
```

### Invariants

Properties to preserve, not features to build. A change that violates one is
wrong.

1. **The server holds state permanently.** Long-polls run continuously
   regardless of whether a browser is connected. The browser never discovers
   anything; it subscribes to a snapshot that is always current.
2. **The browser talks only to the server.** One connection, no broadcast, no
   per-player reachability from the phone. Identical on LAN, cellular and VPN,
   and across VLANs.
3. **Players never disappear.** A configured player is always listed, offline if
   unreachable, never removed. This is the biggest behavioural difference from
   the official app.
4. **Topology is a recursive tree.** `has_master` and `has_slaves` are
   independent; commands recurse (D8).
5. **The snapshot is what the players report.** No optimistic or inferred state
   on the server (D10).
6. **Nothing happens unprompted.** Only user actions and sync polling, with the
   pre-cache as the single read-only exception (D0).

### Stack

Rust backend: `axum`, `tokio`, `reqwest`, `quick-xml`, safe code only (D1).
Frontend: Preact + TypeScript, built with esbuild — three npm packages total
(D2). Frontend embedded in the binary; TS types generated from Rust (D15).
Dependencies are added deliberately and justified (D3).

### Ports

Three, and they matter:

| Port | Serves |
|---|---|
| 11000 | Control, browse, `/ui` |
| 11001 | Settings only. `/Settings` on 11000 issues a 301 here. |
| 80 | Legacy web UI, network share config |

Paths are **case-sensitive**. `/upgrade` works, `/Upgrade` 404s. Most endpoints
are PascalCase; `/upgrade`, `/update`, `/audiomodes` and the `/ui/…` prefix are
lowercase. An unknown path returns a bare `text/plain` 404, not an error
envelope.

### Server ↔ browser API

Semantic for control, structural for browse (D5, D6).

```
GET    /api/state                          full snapshot
GET    /api/events                         SSE deltas
POST   /api/players/{id}/volume            {level} | {mute} | {group: true}
POST   /api/players/{id}/slave-volume      {slave, db}
POST   /api/players/{id}/transport         {action, …}
POST   /api/players/{id}/sleep             {minutes}
POST   /api/players/{id}/mode              {repeat} | {shuffle}
POST   /api/groups                         {master, members[]}
DELETE /api/groups/{master}/members/{id}
POST   /api/groups/all                     minimal-change (D9)
GET    /api/browse/{token}                 structural pass-through
GET    /api/browse/{token}/sorted          server-side sort over cache
POST   /api/browse/{token}/add             {playnow, where, …}
GET    /api/settings/{id}                  settings tree (port 11001)
POST   /api/settings/{id}/{setting}        {value}
GET    /api/art/{token}                    proxied artwork
GET    /api/debug/{id}/raw                 last raw XML per endpoint
```

`{id}` is `ip:port` (D7). `{token}` is an opaque handle for a device-supplied
URL or browse key — device URLs never reach the browser.

### Config

```yaml
players:
  - { ip: 10.20.30.11, port: 11000 }
  - { ip: 10.20.30.12 }

browse_player: 10.20.30.11        # optional; defaults to first reachable
listen: "0.0.0.0:8080"
```

Names and models are not configured — the player reports its own via
`/SyncStatus`. Port is optional, defaults to 11000. No credentials (D13).
Unknown keys must not be fatal. The registry reads from a *source*; config is
one implementation of that source (D11).

---

## Browsing, sorting and search — settled

### `/Services` is the browse schema

Not a startup source list. It declares every list's path, its fixed parameters,
its sort and filter options, its context-menu actions and its artwork URLs.
Fetch it, keep it, build every request from it (D17).

A real capture is in `docs/captures/services-n132.xml`. Read it before writing
the request builder; it is the fixture that builder is tested against.
`docs/captures/` also holds N110 and N130 captures of the same document, kept as
evidence for the paragraph below.

Three players on the same firmware return **semantically identical** trees with
services and attributes in different orders and a different `sid` each. Do not
rely on document order, and do not treat `sid` as shared identity — it is
per player.

**Structure.** `<services schemaVersion sid>` → `<service>` → `<menu>` →
`<menuGroup>` → `<menuEntry>` → `<browseRequest>`.

**There is no `url` attribute on `<service>`.** The browse tree hangs off
`<browseRequest url>` inside menu entries. The `url` on the root `<services>`
element is a settings redirect, not browse.

**`sid` is a version token**, like `prid` on presets. Re-fetch when it changes.

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

```
GET /Songs?service=Tidal&category=FAVOURITES&sort=recent
```

The response echoes it back: `<songs service="Tidal" category="FAVOURITES"
sort="recent" start="30" end="79">`.

**Date added is `sort=recent` on Tidal.** Confirmed present on your own player.

### Parameters come from five places

The request builder must handle all of them:

| Source | Notes |
|---|---|
| `<requestParameter>` | **Text content** is a literal `key=value` |
| `<requestItemParameter name source optional>` | Value taken from the item being browsed into |
| `<genreItemParameter name>` | Same, from the current genre |
| Attributes carrying literals | `myPlaylistsFilter="myPlaylists=1"`, `xmlRequestParameter` |
| `service=<n>` and the chosen sort / filter values | Added by the builder |

### Context menus are declared, not discovered

The same document defines what each item's menu offers and when:

| Element | Purpose |
|---|---|
| `<request url type subtype>` | Actions — `/Add` with `type="add"`, `subtype="now"` / `"next"` / `"shuffle"` |
| `<contextRequest type resultType url>` | Navigation — `gotoartist`, `gotoalbum` |
| `<searchRequest view subtitleParameter>` | Scoped search — `view="artists"`, `view="albums"` |
| `<enableOnAttribute name>` | Show the action only when the item has this attribute (`isFavourite`) |
| `<disableOnAttribute name>` | Hide it when the item has this attribute (`playlistid`) |
| `<textItemSubstitution attribute source>` | Fill `%s` in a label from an item field |
| `<confirmAction text>` | Confirmation prompt, e.g. *"Delete playlist: %s?"* |

`<artworkRequest url="/Artwork">` with optional `<requestItemParameter>` children
declares artwork URL construction the same way.

### Search

`<search parameterName="expr" hasSuggestions="true" prompt="…">`. The parameter
name is **declared, not assumed** — it is `expr` on Tidal, not `q`.

### Rules that will bite

- **Applying a sort replaces that parameter**, never appends.
- **Vocabularies are per service.** Tidal calls alphabetical `name`; LocalMusic
  and BluOS Playlists call it `alpha`. Never carry a value across services.
- **Descending is unavailable.** `<value reverseName>` is read by the Android
  client but has not been observed in any response. Do not build UI for it.
- **Follow the declared url.** LocalMusic points at `/library/v1/Artists`, not
  `/Artists`. Constructing paths is wrong.
- **`resultType`** (`Song`, `Album`, `Artist`, `Playlist`, `Info`) drives
  rendering; `grouped` means A–Z section headers.
- **Filters** use the same shape one level deeper, are inherited by descendants,
  join selected values with commas, and `class="alternative"` is single-choice.
  `<nofilter/>` suppresses an inherited filter.
- **Never whitelist service `type`.** The official client accepts only six
  values and silently drops the rest — which on a real player discards
  `type="BluOSPlaylists"` entirely. Accept whatever arrives.
- **Not every 200 is XML.** `/Preset?id=<n>` for a missing preset returns
  `<h1>Preset Not Found</h1>` with no XML declaration. Check the body starts with
  `<?xml` and the root is expected; treat anything else as an error.

### Browse keys, when using `/Browse`

Two layers of escaping. XML-unescape first (`&amp;` → `&`), then URL-encode for
the `key=` parameter. A key truncated at an unencoded `&` **still resolves** and
returns the correct `type` with an empty body, so a partially-lost key looks
like an empty list rather than an error. One encoding helper, used everywhere.

### In-list search

Substring filter over the cached list on title, artist and album. Local only, no
network. The typed path returns artist and album as separate fields; `/Browse`
concatenates them into `text2`, which is one more reason it is not the path in
use.

---

## Tier 0 — Foundation

| # | Item | Notes |
|---|---|---|
| 0.1 | Config loading, player registry | Source-based, not file-bound (D11) |
| 0.2 | Parser primitives | Sentinels (`parseInt` → `-2`, `parseFloat` → `-1`), the four boolean conventions, both error conventions, `<nextlink>` vs `<nextLink>`. Written once, property-tested, before any endpoint parsing. |
| 0.3 | Mock player | Serves recorded fixtures including etag long-poll behaviour. Lets development and CI run without hardware. |
| 0.4 | XML parsing layer | Shared error-envelope check on the root element first |
| 0.5 | `/SyncStatus` long-poll per player | `timeout=10`, ≥1 s enforced gap, 10 s backoff when no etag returns, 1 s while upgrading. Handle the `<UpgradeStatusStage1\|2>` alternate roots — a player mid-upgrade returns those *instead of* `<SyncStatus>`. |
| 0.6 | `/Status` long-poll per player | `timeout=100`, 105 s read timeout, no pacing. Not symmetric with 0.5. A stale or invented etag returns immediately rather than holding. |
| 0.7 | Secondaries proxy to the primary | A slave's `/Status`, playback control, queue and browse are forwarded internally, so its `/Status` is a copy of the master's. **Volume is the exception** — per-player, so `/SyncStatus` must be polled per slave to track individual volumes. |
| 0.8 | Header contract | `X-Sovi-Schema-Version: 35`, `X-Sovi-Ui-Schema-Version: 7`, `X-Sovi-Tz`, `Accept-Language`, `User-Agent`; store and echo `x-sovi-ui-context`. Response shape can vary by declared schema version. |
| 0.9 | Reconnect and backoff | Never delete a player, mark offline |
| 0.10 | Recursive tree topology | `has_master` and `has_slaves` independent (D8) |
| 0.11 | State push to browser (SSE) | Full snapshot on connect, deltas after |
| 0.12 | Persisted last-known state | A restart shows the full player list immediately, marked stale, rather than an empty page for the first poll cycle |
| 0.13 | Player list UI | Online / offline |
| 0.14 | Raw-response debug panel | Last raw XML per player per endpoint, visible in the UI. Saves more time than any single feature. |

**Effort: 3–5 evenings.**

---

## Tier 1 — Core control

| # | Item | Notes |
|---|---|---|
| 1.1 | Play / Pause / Stop | `/Play`, `/Pause?toggle=1` (single toggle, better for a remote), `/Stop`. `/Play` resumes from pause but **not** from stop. |
| 1.2 | Next / Previous / Seek | `/Skip`, `/Back`, `/Play?seek=` |
| 1.3 | Volume, with coalescing | `/Volume?level=` for the slider; `/Volume?db=±2` for buttons, which avoids read-modify-write races. Server-side debouncing and coalescing, client-side optimistic overlay with TTL (D10). This is most of what makes a remote feel good or bad. |
| 1.4 | Mute | `/Volume?mute=1` / `mute=0`. `can_mute` derived from `<mute>` presence, not transmitted. |
| 1.5 | Group volume | `/Volume?level=&tell_slaves=1`. `has_group_volume` derived from `<groupVolume>` presence. Recurses through nested groups. |
| 1.6 | Fixed-volume handling | `<volume>-1</volume>` means fixed; hide the slider |
| 1.7 | Now Playing | From `/Status`. Render from the generic string map, not a closed field list. |
| 1.8 | Artwork proxying | `/Artwork` for local files, absolute URLs for services. Proxy everything. |
| 1.9 | Presets | `/Presets`, `/Preset?id=`. `id=+1` / `-1` steps with wrap. |
| 1.10 | Queue view | `/Playlist?start=&end=`, 20 at a time |
| 1.11 | Repeat / shuffle | `/Repeat?state=` (0 = all, 1 = track, 2 = off) rejects out-of-range. `/Shuffle?state=` has **no validation** and silently ignores bad values — clamp client-side. |
| 1.12 | Sleep timer | `/Sleep?minutes=<n>` sets directly and accepts **any integer**, so the picker can be whatever you want. 0 cancels. Errors are never surfaced by this endpoint. |
| 1.13 | PWA manifest, add-to-home-screen | Twenty minutes, changes daily use. Chrome on Android installs properly; Firefox Android does not. |
| 1.14 | Start radio from what is playing | `/Status` carries `similarstationid` and `trackstationid` (e.g. `Tidal:radio:artist/…`), ready-made seeds playable via `/Play?url=`. No client reads these. Two buttons, near-zero cost. |

**Effort: 3–4 evenings.** Tier 0 + 1 is a usable daily driver.

---

## Tier 2 — Grouping

| # | Item | Notes |
|---|---|---|
| 2.1 | Group / ungroup | `/AddSlave`, `/RemoveSlave`, addressed to the **master** |
| 2.2 | `/SetMaster` — slave-side grouping | Addressed to the player *itself*. Bare call on a slave **leaves the group**; `?master=<ip>&port=` **joins**; on a master or standalone it is a no-op. Gives a self-service leave and a slave-initiated join, neither of which the other two provide, since both need the master you may not know or reach. **The response is stale** — a successful `?master=` call returns pre-call state with the previous etag. Never parse it; re-poll. |
| 2.3 | Detect silent rejection | A rejected `/AddSlave` returns an empty `<addSlave></addSlave>` with **HTTP 200**. Without an explicit check, failures look like successes. |
| 2.4 | Batch group creation | One call with positional `slaves=ip1,ip2&ports=…`, not N calls |
| 2.5 | Master resolution before grouping | Check `<master>` first. **Mandatory** — `/AddSlave` targeting an existing slave has no effect, so skipping this silently does nothing. |
| 2.6 | `canGroup()` enforcement | Not a slave, not a master, initialized (D8) |
| 2.7 | Create a named group | Pick a master, select members, name it: one batched `/AddSlave?slaves=…&ports=…&group=<n>`. Renaming is the same call. Blank names are dropped by the device. |
| 2.8 | Per-slave volume | `/SlaveVolume?slave=&port=&db=` — a **trim in dB**, with `min`/`max`/`step` from the response (defaults −10 / 10 / 0.5). Different UI from the 0–100 volume. |
| 2.9 | Group all | Minimal-change (D9): keep the existing group if it is the target, dissolve only other groups, one batched add |
| 2.10 | Render nested groups correctly | Show them; do not act on them (D8) |
| 2.11 | Prevent role reversal | Pointing a master at its own slave creates a cycle; the device breaks the group and reasserts the original master. Do the ungroup-then-reform internally rather than letting the user hit it. |

**Effort: 2–3 evenings.**

---

## Tier 3 — Browsing

Sources in scope: **Tidal**, **Radio Paradise**, **Local Media**.

| # | Item | Notes |
|---|---|---|
| 3.1 | `/Services` parse and retain | The browse schema. Re-fetch when the root `sid` changes. No service `type` whitelist. |
| 3.2 | Request builder | All five parameter sources plus service and sort. One function; everything goes through it. Tested against `docs/captures/services-n132.xml`. |
| 3.3 | Typed result parsing | `<songs>`, `<albums>`, `<art>` (artists — not `<artist>`), playlists (item element is `<n>`). Separate title / artist / album fields. |
| 3.4 | **Sort UI from the declaration** | Render `<value displayName>`; send `<value name>`. Per-list memory keyed by url + requestParameters. Ascending only. **R3 lands here.** |
| 3.5 | Filter UI from the declaration | Same shape, inherited, comma-joined |
| 3.6 | Paging | `start` / `end` are settable, so prefer one request over paging where the list allows |
| 3.7 | Search | `<search parameterName>` — `expr` on Tidal. Declared, not assumed. `hasSuggestions` gates typeahead. |
| 3.8 | Context menus from the declaration | `<request>`, `<contextRequest>`, `<searchRequest>`, gated by `<enableOnAttribute>` / `<disableOnAttribute>`, with `<textItemSubstitution>` and `<confirmAction>`. Honour `confirmAction` before firing anything destructive. |
| 3.9 | **Favourites** | `/AddFavourite`, `/DeleteFavourite`. Declared as `<request type="favourite" subtype="add\|delete">` gated on `isFavourite` (which is `"1"` or absent, not a boolean string). If the builder is faithful, this needs **no favourite-specific code** — the same declaration renders both directions. |
| 3.10 | Respect `minimumSchemaVersion` | On `menuEntry`, `menuGroup`, `genreGroup`, `inlineEntry`, `sort`, `filter`. Skip anything above the schema version advertised in `X-Sovi-Schema-Version`. |
| 3.11 | Play / add | `playURL`, `autoplayURL`, `/Add`. `<request subtype>` gives `now` / `next` / `last` / `shuffle`. |
| 3.12 | Queue management | `/Delete?id=`, `/Move?old=&new=`, `/Clear`, `/Save?name=` |
| 3.13 | `/Browse` fallback | Only for a list with no `/Services` declaration. Not otherwise used — it cannot sort (D17), and the builder is generic, so it buys nothing. |

**Preserve open attribute maps end to end.** Item elements copy all their
attributes into an open string map. Rust types carry a
`HashMap<String, String>` alongside typed fields, the debug panel renders it,
and browse JSON passes it through. Parsing only known attributes makes it
impossible to expose more than the official app does, which is the point.

**Effort: 4–6 evenings.** Each additional service is nearly free.

---

## Tier 3b — Cache

Removing the three-second wait. Sorting is a device operation (D17); caching is
for speed.

| # | Item | Notes |
|---|---|---|
| 3b.1 | SQLite browse cache | Key = `browseRequest` url + its requestParameters + chosen sort value, so each sort order is its own node. Stores the generic parsed form with full attribute maps (D14). Survives restarts. |
| 3b.2 | Full enumeration | `start` / `end` are settable — prefer one request per list |
| 3b.3 | **In-list search** | Substring filter on title, artist, album over the cached list. Local, no network. |
| 3b.4 | Stale-while-revalidate | Serve cached instantly, refresh behind it, push the delta over the existing SSE channel |
| 3b.5 | Startup warm | Personal lists in their default order and in `sort=recent`. Other orders on demand. |
| 3b.6 | Crawl bounds | Hard cap on node count and depth. A cap, not a blocklist — never wander into unbounded catalogue nodes. |
| 3b.7 | Scheduled refresh | ~15 minutes for personal lists. Read-only; the one exception to D0. |
| 3b.8 | Manual refresh | Per-node and global |
| 3b.9 | Designated browse player | From config, with fallback when offline. Browse goes *to a player*; without this you cache the same tree N times. |

There are no callbacks. The player proxies Tidal and exposes no subscription
mechanism, so polling is the only option.

**Effort: 2 evenings.**

---

## Tier 4 — Settings and extras

| # | Item | Notes |
|---|---|---|
| 4.1 | **Settings tree** | Dirac, subwoofer, crossover. See below. |
| 4.2 | Alarms | `/Alarms`, with a `tz` parameter |
| 4.3 | Preset editing | `/SetPreset` — `id`, `name`, `image`, `volume`, `encoded_url`, `shuffle`, `canShuffle`, `delete` |
| 4.4 | Reorder presets | **POST JSON** to a device-supplied URL, not a GET |
| 4.5 | Input selection | `/Play?inputTypeIndex=<type>-<n>` (firmware ≥ 4.2.0) — types `spdif`, `analog`, `coax`, `bluetooth`, `arc`, `earc`, `phono`, `computer`, index from 1 per type. Reaches **inactive** inputs that never appear in browse. |
| 4.6 | Bluetooth output | `/BTDevices` (long-polls, `timeout=100`), `connect=`, `disconnect=`, `unpair=` |
| 4.7 | Firmware version display | `/GitVersion`, `/Upgrade?upgrade=check`. Read only (D12). |
| 4.8 | Rename player | `/Name?set=` — returns `<n>` |
| 4.9 | **Find the playing track on Tidal** | When Radio Paradise (or any radio) is playing, take artist and title from `/Status` and run a Tidal search via the declared `<search parameterName="expr">` and `<searchRequest view="songs">`. Show candidates; favourite from the result's own declared context menu. It is a text search with no exact-match guarantee, so this is a "find candidates" action, not a one-tap favourite. Needs nothing beyond Tier 3. |
| 4.10 | Reindex local library | `/Reindex?logall=0`; progress via `<indexing>` in `/Status` |

Simultaneous browser sessions are not listed because they fall out of the
snapshot-plus-SSE design for free.

### 4.1 — Settings tree (Dirac Live, subwoofer, crossover)

One generic renderer, not three bespoke features.

**Settings live on port 11001.** `/Settings?schemaVersion=<n>` returns the whole
tree; `?id=<pageId>` returns one page. The tree is `<menuGroup>` and `<setting>`
nested arbitrarily. `class` selects the control: `list`, `boolean`, `button`,
`range`, `dual-range`, `alarms`, `sleep`.

**The `url` attribute on each setting is its write endpoint**, and it is not
uniform — `/setting` (lowercase, singular, generic), `/audiomodes`,
`/alsa_setting`, or an endpoint fired directly such as `/Reindex`. Writes are
`<url>?<setting name>=<value>`, taking the value from a `<value name>` child for
lists or the raw number for ranges. Follow the `url` the device gives you.

Two constructs the top-level tree does not use, confirmed unchanged between
schema 28 and 35:

- **`<dependsOn name value/>`**, repeatable. The setting applies only while the
  named setting holds that value. Ignoring these renders contradictory controls.
- **`class="range"`** with `<value min max step units/>`, and
  **`class="dual-range"`** with `<value min max minRange units/>` where `value`
  is a comma-separated pair. `hideIfDisabled="true"` means hide, not grey out.

`refresh="true"` means re-fetch the tree after changing that setting.

| Feature | Setting | Endpoint |
|---|---|---|
| Dirac Live preset | `eq-dirac`, `class="list"`, `refresh="true"` | `/alsa_setting` |
| Subwoofer | `subwoofer` | `/audiomodes?subwoofer=withsub` |
| Crossover | `eq-crossover` | `/alsa_setting` |

`eq-dirac`'s `<value>` list enumerates the Dirac filter slots stored on the
player, `0` meaning off. It is the settings-side counterpart of the `<dirac>`
element in `/Status`, so the active filter can be shown on the now-playing
screen without a settings fetch.

**The audio page is model-dependent.** Two players on the same firmware expose
different settings, and `eq-dirac` was seen on the N130 at schema 35 but not
everywhere. Render whatever the tree returns; never assume a fixed list. That is
the entire argument for the generic renderer.

`<webview url>` settings point at **port 80** — network shares are served as
`:80/sharecfg?noheader=1`.

---

## Order

1. **Tier 0** — foundation, including the mock player and the debug panel.
2. **Tier 1.1–1.8** — transport, volume, now playing, artwork.
3. **Tier 1.13** — PWA manifest. Twenty minutes, and it changes how the thing
   is used every day.
4. **Tier 1.9–1.12** — presets, queue, repeat and shuffle, sleep timer.
5. **Tier 2** — grouping.
6. **Tier 3 for Tidal.** R3 is satisfied at 3.4.
7. **Tier 3b** — the cache. The three-second wait goes away.
8. **Tier 3 for Local Media and Radio Paradise.** Nearly free once the builder
   is generic.
9. **Tier 1.14** — radio seeds from `/Status`. Needs nothing new, and it is a
   natural follow-on once Radio Paradise is browsable.
10. **Tier 4.1** — the settings tree.
11. **The rest of Tier 4**, in three groups:
    - **Free once you are there.** 4.7 firmware version, 4.8 rename player,
      4.10 reindex. A read and a write each, no new surface.
    - **Unblocked by earlier work.** 4.3 preset editing and 4.4 reorder presets
      once 1.9 exists; 4.9 find-the-playing-track once Tier 3 search works.
    - **New surfaces, self-contained.** 4.2 alarms, 4.5 input selection,
      4.6 Bluetooth output. Each is an evening on its own and none blocks the
      others; 4.5 is the one with real daily value if you use physical inputs.

Within those groups the order is preference, not dependency. That is the only
thing left unsequenced, and deliberately so.

First milestone: **open the page on the phone, see every player instantly,
always, and change volume.** Tier 0 plus 1.3, and it already solves what started
this.

Effort estimates are by unknowns, not by lines. Tier 0 will likely go faster
than stated; anything touching browse will go slower.

---

## Open questions

Kept in the protocol reference, §16, so there is one list rather than two. Read
it there.

Nothing on that list blocks any tier. Sorting, paging, the browse schema, group
semantics, settings and concurrency are all settled.
