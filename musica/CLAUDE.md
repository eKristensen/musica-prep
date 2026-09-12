# CLAUDE.md

## Read first

- `CONTRIBUTING.md` — applies to you exactly as it does to a person. Nothing in
  it is relaxed because the change comes from an agent.
- `DESIGN_PRINCIPLES.md` — settled architectural decisions, and binding here.
  **They are not open for reinterpretation.** If you believe one is wrong, say
  so and stop; do not build against it.
- `PLAN.md` — the work plan, tiers and ordering.
- `README.md` and `MOTIVATION.md` — what this is, and the requirements the
  work is measured against.

## The two protocol documents

They have different jobs. Do not confuse them.

**`docs/bluos-http-api.md` — the reference. Source of truth, read-only, never
committed.** It is the complete description of the protocol, maintained
elsewhere and dropped in whole. It is listed in `.gitignore`; it stays in the
working tree so you can read it, and git never sees it. Do not patch it, do not
quote its provenance, do not copy its confidence markers.

^^^ Notes / adjustments to above: The http api spec document is an ai model ready document
that describes the bluos api going beyond the official documentation including observed behavior
of the bluesound players . Whenever possible the official v1.7 spec should be used in references,
if anything goes beyond the official spec put the parts you use in protocol notes as observed behaviour.
Never put in any reference to how the extra api calls have been discovered. Just describe what is used in the implementation of this project
when used.

**`docs/protocol-notes.md` — the record. Committed, written as we go.** When an
endpoint is implemented, add to this file only what the implementation depends
on: the request, the response shape actually parsed, and the traps the code
guards against. Write it as observed device behaviour — "the device returns X
when sent Y". Never how any of it was found, never a client class or method
name, never a decompiler or a source client by name. It documents what is built,
so it is expected to be incomplete; that is the point, not a gap to fill.

**Precedence.** The reference wins on anything wire-level. `protocol-notes.md`
never contradicts it; it is a subset of it, narrowed to what is implemented.
Cite the reference section (§8.2) beside each note so the two stay tied.

**When the device disagrees with the reference, or does something the reference
does not cover: stop and report it.** Do not edit the reference and do not paper
over it in code. It is updated at its own source, and the finding has to travel
back there or it is lost.

## Non-negotiable constraints (Note this is a duplicate of decisions and play do I really need it again here?)

**Safe Rust only.** `#![forbid(unsafe_code)]` is at the crate root. Do not
remove it. If a dependency requires writing `unsafe` to use, reject the
dependency.

**Three npm packages.** `preact`, `typescript`, `esbuild`. Adding a fourth needs
explicit approval and a written justification. No Tailwind, no component
library, no CSS-in-JS, no bundler framework. Plain CSS with custom properties.

**Every dependency is justified.** Before adding anything, in either ecosystem:
check the transitive tree (`cargo tree -p <crate>`, `npm ls`), prefer no build
step, prefer boring and old, reject pre-1.0 single-maintainer packages. Put the
reason in the commit message. This is not an argument for hand-rolling an HTTP
client — solid widely-used projects are what dependencies are for. The test is
whether it is *worth it*.

**The app never acts on its own.** Only user actions and sync polling. It does
not repair configurations, tidy up state it disapproves of, or take an action
because it noticed it could. The Tidal pre-cache is the single exception, and it
is read-only. If you find yourself writing "if we detect X, automatically do Y",
stop.

**No browser-side protocol knowledge.** The browser never sees XML, device
URLs, sentinel values, or anything about how BluOS works. There is no generic
proxy endpoint. Adding one is how all the protocol knowledge ends up in the
frontend.

**No telemetry, analytics or crash reporting.** Nothing leaves the LAN.

**No decompiler output in the repository.** Ever.

## Working style (mock player tests should that not be described elsewhere instead of here?)

**Test against the mock player, not the hardware.** `make mock`. The real
players are in a house where people sleep. The mock serves recorded fixtures
from `docs/captures/` including etag long-poll behaviour.

**When a fixture is missing**, say so and ask for a capture rather than
inventing XML. Guessed response shapes are worse than no code.

**Parser primitives before endpoints.** The sentinel values, boolean
conventions and error envelopes are shared and sharp. They live in one
property-tested module.

**Preserve open attribute maps.** Item elements copy *all* their attributes into
an open string map. Rust types carry a `HashMap<String, String>` alongside typed
fields, and it passes through to the browser untouched. Parsing only the known
attributes makes it impossible to expose more than the official app does, which
is the point of the project.

**`/Services` is the browse schema, not a source list.** It declares every
list's path, fixed parameters, sorts, filters, context-menu actions and artwork
URLs. Every browse request goes through one request-builder function, tested
against `docs/captures/services-n132.xml` — read that file before writing the
builder. `docs/captures/` also holds N110 and N130 captures of the same
document: semantically identical, different `sid`, different element and
attribute order. They exist to prove the builder does not depend on order.

**`/Browse` is not the browse path.** It cannot sort, and sorting is the reason
this project exists (R3, D17). The request builder is generic, so there is
nothing `/Browse` makes easier. Use it only for a list that has no `/Services`
declaration at all, and say so when you do.

Specifics that are easy to get wrong:

- **`<service>` has no `url`.** The tree hangs off `<browseRequest url>` inside
  `<menuEntry>`. The root `<services url>` is a settings redirect.
- **Never whitelist service `type`.** The official client accepts six values and
  drops the rest, which discards `type="BluOSPlaylists"` on a real player.
- **Parameters come from five places**: `<requestParameter>` text,
  `<requestItemParameter>`, `<genreItemParameter>`, literal-carrying attributes
  like `myPlaylistsFilter`, and the builder's own `service` and sort values.
- **Search parameter name is declared** — `expr` on Tidal, not `q`.
- **Sort vocabularies differ per service** — `name` on Tidal, `alpha` on
  LocalMusic. Never carry a value across services.
- **Re-fetch when the root `sid` changes.** `sid` is per player, not shared.
  Service and attribute order is not stable between players — never rely on
  document order.
- **Honour `<confirmAction>`** before firing any request that declares one.
- **Skip elements above your advertised schema version** (`minimumSchemaVersion`
  on `menuEntry`, `menuGroup`, `genreGroup`, `inlineEntry`, `sort`, `filter`).
- **`isFavourite` is `"1"` or absent**, not `"true"`/`"false"`.

**Follow device-supplied URLs and keys verbatim.** Never construct browse paths,
compute paging offsets, or hard-code an endpoint the device handed you. Six of
the paths that look like literals are not.

## Protocol traps that will bite you

- **Browse keys need two decodings.** XML-unescape (`&amp;` → `&`), then
  URL-encode for the `key=` parameter. A key truncated at an unencoded `&`
  still resolves and returns an **empty list with the correct type**, so this
  failure looks like no results rather than an error. All browse calls go
  through one encoding helper.
- **Not every HTTP 200 is XML.** `/Preset?id=<n>` for a missing preset returns
  `<h1>Preset Not Found</h1>` with no XML declaration. Check the body starts
  with `<?xml` and the root element is one you expect.
- **Applying a sort replaces that query parameter**, never appends.
- **Paths are case-sensitive.** `/upgrade` works, `/Upgrade` 404s. `/Status`
  works, `/status` 404s.
- **Three ports.** 11000 control and browse, 11001 settings (11000 redirects
  with a 301), 80 legacy web UI.
- **A rejected `/AddSlave` returns HTTP 200** with an empty body. Verify by
  re-polling; never assume success.
- **`/SetMaster` returns stale state** — pre-call `<SyncStatus>` with the
  previous etag. Never parse it to confirm anything.
- **A slave's `/Status` is a copy of its master's.** Volume is the exception and
  stays per-player, which is why `/SyncStatus` is polled per slave.
- **`/Shuffle` does not validate** and silently ignores bad values. `/Repeat`
  does validate.
- **`/SyncStatus` has alternate roots** during upgrade:
  `<UpgradeStatusStage1|2>` instead of `<SyncStatus>`.
- **Master and slave are not mutually exclusive.** A player can be both.
  Topology is a recursive tree; commands recurse through it.
- **Sentinels:** `parseInt` → `-2`, `parseFloat` → `-1`. A `-2` means absent.
- **Booleans use four different conventions** including presence-only and
  inverted-presence.

## Code conventions

- Errors: `thiserror` for library errors, `anyhow` at the binary boundary. No
  `unwrap()` outside tests.
- Logging: `tracing`. Every device request logs at debug with its full URL, and
  the raw response is retained for the debug panel.
- Tests: unit tests for parsers against real captures; integration tests against
  the mock player. A parser change without a fixture test is not done.
- Frontend: the core module (SSE client, store, types) imports no framework.
  View components import from it, never the reverse.
- Types shared with the frontend are generated from the Rust types and
  committed. Regenerate when they change; do not hand-edit.

## When you are unsure

Ask. Particularly about:

- Anything that would add a dependency.
- Anything that would make the app act without a user asking.
- Anything where the device behaviour is not in `docs/bluos-http-api.md`.
- Anything that contradicts `DESIGN_PRINCIPLES.md`.

A question costs a minute. A wrong assumption baked into the architecture costs
an evening.
