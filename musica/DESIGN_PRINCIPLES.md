# Design Principles

There is quite a distance between finding motivation based on an less than ideal Andorid App and having a working solution. On the way many choices needs to be made. The purpose of this document is to clearly outline the principles that form the basis for any coding decisions made while building this program.

This document is meant to be updated if needed, but for the most part it is expected that no updates should be needed. Making a change in this document could start a chain reaction that requires changes to many parts of Musica.

These principles get close to the implementation in places, but this is not the
implementation plan. What gets built, and in what order, is `PLAN.md`. What has
to hold however it is built is here.

## How to read this

For each element there is a clear structure:

- **Decision** — what was chosen.
- **Because** — the reasoning.
- **Consequences** — what follows mechanically.
- **Revisit if** — the concrete signal that reopens it.

**A number is an identity, not a position.** `PLAN.md`, `CLAUDE.md` and
`MOTIVATION.md` all cite elements by number, so an element keeps its number for
good. The sections below group them by subject, which is why the numbering does
not run in order.

**An open question is not settled.** It is either an element of its own with
"open question" in the heading, or a paragraph marked **Open question.** inside
an element that is otherwise decided. Nothing is built against one.

---

## What the app is allowed to do

The principle everything else is downstream of.

### D0. The app acts only on user action or to stay in sync

**Decision.** The app does exactly two kinds of thing: what the user asked for,
and whatever polling is needed to keep its picture of the players current. It
never changes device state on its own initiative, never "corrects" a "wrong"
configuration.

**Because.** A remote control that quietly reorganises your system is worse than
one that lacks a feature. Every autonomous action is a behaviour you have to
learn, predict and eventually work around. Home Automation belongs in Home Assistant, not here.
It is tempting to "correct" the state given the details the API give access to and the less than ideal configurations raw API calls can yield. However to keep the application predicable it must not do anything unless the user directly requests that action, with the Tidal cache and player status being the exception.

**Consequences.** Reaches into several other decisions: the app renders a nested
group correctly but does not undo one (D8); it prevents bad states rather than
repairing them; error recovery re-polls rather than re-issuing commands.

**The one exception** is the Tidal pre-cache (D14), which issues reads on a
timer. It is read-only, changes no device state, and is the feature that
justifies the server-side architecture in the first place.

**Revisit if.** Never.

---

## The stack

What Musica is built out of, what ships, and what may be added.

### D1. Backend in Rust, safe only

**Decision.** `axum` + `tokio` + `reqwest` + `quick-xml`. One binary.
`#![forbid(unsafe_code)]` at the crate root. No `unsafe` blocks, no exceptions.

**Because.** The server holds many permanent long-poll connections and a parse
layer full of sharp edges. Nothing here is performance-critical enough to
justify `unsafe`, and forbidding it at compile time means the question never
comes up in review.

**Consequences.** If a dependency requires writing `unsafe` in our code to use
it, that is a reason to reject the dependency.


**Revisit if.** Never.

### D2. Frontend is Preact + TypeScript with a three-package toolchain

**Decision.** Preact, TypeScript, esbuild. Plain CSS with custom properties. No
bundler framework, no Tailwind, no component library, no CSS-in-JS.

Total npm dependencies: **three** — `preact`, `typescript`, `esbuild`. One is a
4 KB runtime dependency; the other two are build-time only.

**Because.** Large npm trees rot, builds easily break after a few years with conflicting dependencies. The answer is not to avoid the ecosystem, it is to take almost none of it.

- **esbuild, not Vite.** Vite is excellent and pulls in a substantial tree.
  esbuild ships as a single prebuilt binary with **no transitive npm
  dependencies**, and does TypeScript, JSX and bundling in one step. This is the
  single largest reduction available.
- **Preact, not React.** 4 KB, one package, API stable since 2018, and
  `preact/compat` aliases to React if Preact ever goes quiet. Generated code
  quality is high because the API mirrors React's, which matters when an agent
  writes most of it.
- **TypeScript earns its package.** Types generated from the Rust side (D15) are
  how the API contract stays honest across a language boundary.

**Node is build-time only.** Nothing in the shipped artifact runs on Node. The
built output is static files embedded in the Rust binary (D15), so a Node
toolchain that stops installing in 2031 blocks *rebuilding*, not *running*. To
make that concrete, the built bundle is committed alongside its source. Worst
case you edit the committed JavaScript directly — unpleasant, but not a rewrite.

**Explicitly rejected options:**

| Option | Why not |
|---|---|
| Leptos | Pre-1.0, effectively single-vendor; Rust UI code bound to a dead framework has no migration path. It also does not avoid a toolchain — it substitutes `wasm-bindgen`, `trunk` and a WASM pipeline for the npm one. |
| Svelte 5 | Runes broke Svelte 4. Weaker generated code than React-shaped output. |
| Solid | Good model, thin training data, small ecosystem. |
| HTMX + Rust templates | Good for the browse tree, fights optimistic volume sliders and continuous now-playing updates. |
| Dioxus | Same pre-1.0 risk as Leptos with more churn. |
| Vite | Not wrong, just a far larger tree than esbuild for no benefit at this size. |

**Revisit if.** esbuild is abandoned — it is then replaceable in an afternoon,
which is the point of a bundler with no config surface. Or if three packages
prove impossible for something genuinely necessary; see D3.

### D3. Dependencies must earn their place, in every language

**Decision.** A dependency is added only when it is clearly better than writing
the thing ourselves *and* it looks maintainable for a decade. Every addition
gets a one-line justification in the commit message. This applies identically to
Cargo and npm.

Before adding anything:

- **Check the transitive tree, not the package.** `cargo tree -p <crate>`,
  `npm ls`. A small crate that drags in forty others is a large crate.
- **Prefer no build step.** Compiler plugins, codegen passes and heavy
  proc-macros are future breakage.
- **Prefer boring and old.** Stable for five years beats better-designed and
  released last year.
- **Reject fragile.** Pre-1.0, single maintainer, no release in a year — a
  liability regardless of fit.
- **Do not reinvent.** This is not an argument for hand-rolling an HTTP client
  or an XML parser. Solid, widely-used, well-maintained projects are what
  dependencies are for. The test is whether it is *worth it*, not whether it is
  avoidable.

**Because.** Projects become unmaintainable through accumulated transitive
dependencies, not direct ones. A dependency's real cost is its tree and its
lifespan, neither visible at the moment you add it.

**Consequences.** Lockfiles committed. Dependency trees reviewed periodically,
not only at add time. A dependency that grows a large tree in a minor version is
grounds for reconsidering it.

**Revisit if.** Never.

### D15. One artifact, generated types

**Decision.** The built frontend is embedded into the Rust binary
(`rust-embed`). TypeScript types are generated from Rust types and the generated
files are committed. The built JavaScript bundle is committed too (D2).

**Because.** One deployment artifact means no version skew between API and UI.
Committing generated output means a rotted toolchain blocks rebuilds, not runs.

---

## Server and client: where the work happens

Which side does which work, and what is allowed to cross between them.

### D5. Thick server, thin client

**Decision.** The browser talks to Musica. The Musica server talks to BluOS devices. Musica is not a proxy server. Complicated BluOS interaction such as master resolution, groupping, batch jobs and cache invalidation must be performed where it can be unit-tested

**Because.** The whole idea of Musica is to offload the client, make the client more thin and thereby make it more responsive. The complex BluOS HTTP API must not be exposed to the clients, but simple calls that clearly mark the intent should be preferred. A think client allows for more testing against the BluOS HTTP Api with a mock player. The client tests should not depend on the BluOS HTTP API.

**Exception** Browser api, settings and similar direct UI elements of the BluOS api should be relayed rather than replicated in code. Do not reimplement what already works.

**Trap** A generic `POST /api/proxy?path=…` is tempting during Tier 0 and then quietly
becomes how every later feature is built, at which point all protocol knowledge
is in the browser after all. A debug-only equivalent may exist behind a flag
that is off by default and never called from application code.

**Revisit if** The stack design does not work out.

### D4. The core client module is framework-free

**Decision.** The SSE client, the state store and the shared type definitions
live in a module with zero framework imports. View components import from it; it
imports nothing from them.

**Because.** This is the insurance behind D2. If the framework ever has to
change, the migration is a rewrite of a few view components, not of the app.

**Consequences.** No Preact hooks or signals inside the core module. It exposes a
plain subscribe/snapshot interface.

**Open question.** I am not sure whether this is a good decision. If we change front, wont we need to rewrite everything? Would it be more clear/better to make a more stable API between back and frontend? I might be wrong I just want to know what you think.

### D10. Optimistic state is client-side only and TTL-bounded

**Decision.** Volume and transport get a local optimistic overlay with a short
TTL — dropped as soon as a snapshot reflects it, or after ~1 s, whichever comes
first. The server never holds optimistic state.

**Because.** A slider that waits for a round trip feels broken. Server-side
optimism would corrupt the invariant that the snapshot is what the players
actually report, and would make the debug panel lie.

### Open question — one crate or two, BluOS API and server

**Not decided.** Would it make sense to split the BluOS HTTP api code and the server backend. The idea is to be able to split out the BluOS HTTP api into a seperate repo later if I want to make it easier to reuse just the api integration I build. Or is it better to just build it flat and focus on my own results. Do I gain something by preparing the code to be reusable? If  yes would it maybe even make sense to build the bluos http api lib seperately from the start? I do not know what makes the most sense please advice.

---

## Players: identity, topology and grouping

How a player is named, how group topology is modelled, and what grouping does.

### D7. Player identity is `ip:port`

**Decision.** Players are keyed by `ip:port`, which is what `SyncStatus@id`
contains and what the config supplies. MAC is stored and used only as the key
for *persisted* data — browse caches, per-player preferences, last-known state.

**Because.** The protocol identifies players by address: grouping takes IPs and
ports, `<master>` and `<slave>` carry addresses. There is no alternative at the
wire level. MAC is used for persistence only so that changing a player's address
does not silently orphan its cache.

**Consequences.** No identity resolution table in the hot path.

**Revisit if.** Never.

**Open question.** I am considering to actually change back to MAC again. IP while static could change. I have a LAN and WIFI ip for all my players in static dhcp lease... though it got a different mac for lan and wifi so that does not solve the problem. Do you have any suggestions for a stable index? ip + port is an esy choice and it contains the data needed when working with groups and interacting with the players.

### D8. Model nesting; prevent it; do not act on it

**Decision.** Three separate rules.

*Model:* `has_master` and `has_slaves` are independent booleans. A player can be
both. Topology is a general tree and commands recurse through it.

*Prevent:* the UI replicates the official `canGroup()` restriction — grouping is
offered only for a player that is not a slave, not a master, and initialized. No
merge affordance. Nested groups cannot be created through this app.

*Observe, do not act:* if a nested group exists — created by another client, by
the official app's `groupAll`, or by hand — render it correctly and leave it
alone. No flatten button, no repair prompt, no detection logic that triggers
anything.

**Because.** The first rule exists because the official app's
mutual-exclusivity predicates are exactly why nested groups' slaves vanish from
its list; inheriting the assumption inherits the bug. The second prevents the
bad state at the source, which is the cheap place. The third follows from D0: an
app that notices something and fixes it unasked is a machine rummaging in your
system. Showing the true state is enough — the user can ungroup normally, here
or anywhere else.

**Consequences.** The tree model is load-bearing and must be recursive. The
flatten action from earlier drafts is removed.

**Revisit if.** Nested groups turn out to happen accidentally and often enough
that seeing them is not sufficient. Even then the answer is a clearer display,
not an automatic action.

### D9. "Group all" makes the minimum number of changes

**Decision.** Take the currently selected player as the master. Then:

1. Players already slaves *of that master* — leave them alone.
2. Free players — add them.
3. Players belonging to *other* groups — dissolve those groups, then add the
   freed players.
4. Issue the additions as one batched `/AddSlave`.

**Because.** Dissolving an existing correct group to rebuild it is needless
churn: it interrupts playback and changes state that was already right. The
device only forces dissolution for members of *other* groups, since adding an
existing slave is a silent no-op and adding an existing master nests.

Worked example: players 1–4, group is 1–3 with 1 as master, Group All pressed
with 1 selected. Correct behaviour is one call,
`/AddSlave?slaves=4&ports=11000` to player 1. Nothing else moves.

Two groups A(1,2) and B(3,4), A selected: dissolve B, then one batched
`/AddSlave` to player 1 with slaves 3 and 4.

**Consequences.** Dissolution uses `/SetMaster` addressed to each member, which
makes it leave without needing to know or reach its master. Confirm topology has
settled by re-polling `/SyncStatus` before the add — a rejected `/AddSlave`
returns an empty body with HTTP 200, so success must be verified, not assumed.

---

## Browsing, sorting and caching

Where the browse tree comes from, who sorts it, and what is kept.

### D6. Browse is the deliberate exception: structural pass-through

**Decision.** For browse only, the server is a sanitising pass-through, not a
domain modeller. It converts XML to structurally equivalent JSON, preserves the
generic attribute maps intact, and rewrites device URLs and browse keys into
opaque server-side tokens. It does not decide what an item *means*; the client
renders generically from `type` and `resultType`.

**Because.** The browse protocol is link-driven on purpose. A server-side domain
model would have to invent a taxonomy the protocol lacks, and would be wrong
differently for each service.

**Sorting is not part of this.** Sorting is a device operation, requested via
the parameter declared in `/Services` (D17). The cache stores each sort order as
its own node rather than reordering locally.

**Revisit if.** A concrete rendering problem cannot be solved client-side. Then
add a hint field and record it here.

### D17. Browse is driven by the `/Services` declaration

**Decision.** `/Services` is a first-class persistent object, not a startup
source list. It declares, per list, the browse path, its fixed parameters, and
the sort and filter options that list supports. Browse requests are built from
that declaration.

`/Browse` is used only for a list that has no declaration at all. It is not a
parallel path kept for convenience: it cannot sort, and the request builder is
generic, so there is nothing it makes easier.

**Because.** Sort options are declared in `/Services`, not advertised in the
browse response. A list that returns no `<sortMenu>` may still be fully
sortable — Tidal favourites is exactly that case, and `sort=recent` returns date
added. A client that treats `/Services` as a one-off source list loses all
sorting and filtering even though the endpoints support it. That is precisely
the official app's failure, and R3 exists because of it.

`/Browse` cannot sort, and its track items concatenate artist and album into
`text2`, which in-list search needs separated. The earlier decision named
exactly this revisit condition — `/Browse` being unable to reach content the
typed path can — and it fired.

**This is not hard-coding.** `<browseRequest url>` and `<requestParameter>` are
followed exactly like any device-supplied URL, just declared once per list
rather than repeated per response. LocalMusic pointing at `/library/v1/Artists`
rather than `/Artists` is the proof: constructing the path yourself would be
wrong, and the declaration is what tells you so.

**Consequences.**

- Fetch `/Services` at startup, keep it, re-fetch on schema change. It is the
  browse schema.
- Build requests by concatenating `browseRequest url` + its `requestParameter`
  children + `service=<name>` + the chosen sort value.
- Applying a sort **replaces** that parameter rather than appending.
- Sort selections are remembered per list, keyed by the `browseRequest` url plus
  its `requestParameter` children. That key is also the cache key.
- **Sort vocabularies are per service.** Tidal calls alphabetical `name`;
  LocalMusic and BluOS Playlists call it `alpha`. Never assume a value carries
  across services. Read them from the declaration.
- Treat descending as unavailable. `<value reverseName>` is read by the Android
  client but has not been observed in any response.
- `resultType` (`Song`, `Album`, `Artist`, `Playlist`, `Info`) tells the client
  how to render; `grouped` means section-grouped with A–Z headers.
- Filters use the same shape one level deeper, are inherited by descendants,
  join selected values with commas, and `<nofilter/>` suppresses an inherited
  one. `class="alternative"` is single-choice.

**A third surface exists and is rejected.** `/ui/Configuration` returns
server-driven UI screens and is what current Controller apps render. It is
undocumented with no stability promise. Not used.

**Revisit if.** A service we care about has no `/Services` declaration for a
list we need. Then `/Browse` is the fallback for that list specifically.

### D14. Cache complete lists; one cached node per sort order

**Decision.** SQLite-backed browse cache, stale-while-revalidate, keyed by
browse node. Cached payloads are the generic parsed form including full open
attribute maps, never typed structs. Personal lists are cached in **full**, not
page by page.

**Because.** Item elements copy all attributes into an open map, so caching
typed structs would silently discard service-specific attributes. Caching is for
**speed** — removing the three-second wait — not for sorting; sorting is a
device operation (D17).

**Consequences.** The cache key is the `browseRequest` url plus its
`requestParameter` children plus the chosen sort value, so each sort order is a
separate cached node. Pre-cache the default order and date-added; fetch others
on demand.

`start` and `end` are settable on the typed path, so a list can often be
enumerated in one request rather than paged. The crawl still needs a hard cap on
node count and depth so it never wanders into unbounded catalogue nodes.

In-list search filters the cached list locally on title, artist and album. The
typed path returns these as separate fields, unlike `/Browse`.

**Sorting locally over the cache was the original plan and it does not work.**
`/Browse` returns lists it cannot sort and concatenates artist and album into a
single field, so there is nothing to reorder faithfully. Sorting moved to the
device (D17) and the cache followed it. Do not propose local reordering again.

---

## What is deliberately not built

Absent by decision, not by omission.

### D11. Static configuration now; discovery is a late maybe

**Decision.** Players come from a static config file. No LSDP, no mDNS, for all
of development and the first working version.

**Because.** Unreliable discovery is the problem this project exists to solve,
and the devices have fixed addresses. Depending on discovery during development
would reintroduce the exact failure mode being escaped.

**But design for it.** The player registry takes players from a *source*, and
config is one implementation of that source. Do not scatter assumptions that the
player set is fixed at startup or that it came from a file. Adding discovery
later should mean adding a source, not restructuring the registry.

If it is ever built, it layers on top of the static entries rather than
replacing them: seed from config, then look for others. The discovery protocol
is described in the reference, §12; read it there rather than reasoning about it
here. Current evidence is that nothing enumerates players outside a group, so
this may find nothing.

**Revisit if.** Everything else works and this is the most annoying thing left.
Not before.

### D12. Firmware upgrade is not implemented

**Decision.** Display version and update-available status. No upgrade trigger.

**Because.** Low value, not high risk — the earlier framing overstated the
danger. Players manage their own upgrades and the port 80 web UI does the job.
The official app's upgrade-all is presumably the same call to every player and
could be added cheaply if it ever mattered.

**Revisit if.** Upgrading players one at a time through the web UI becomes
irritating. Small feature, not a forbidden one.

### D13. No authentication

**Decision.** Authentication is not implemented. No credentials in config, no
digest or basic handling, no credential cache. A 401 is displayed as an error
like any other.

**Because.** No way was found to set credentials on a consumer N-series player,
so the path is unexercised and untestable on the hardware this targets. The
mechanism is real in other BluOS clients and presumably serves CI hardware, but
implementing behaviour that cannot be verified means shipping untested code
paths for a scenario that may never occur.

**Revisit if.** A player on the network actually returns 401. Then it is worth
doing properly, with real behaviour to test against.

### D19. Playback is not moved between players

**Decision.** `/MovePlayback` is not implemented. To listen somewhere else,
start playback there.

**Because.** Tried on real hardware when the multi-player setup was new, and it
did not work well enough to keep.

Position is not preserved — playback does not resume where it left off. For an
ordinary queue that is an annoyance you can correct by skipping or seeking.

For Tidal track radio it is not correctable. Track radio is a generated
playlist, and moving playback restarts it at the first track rather than
continuing from the current position. Recovery would mean skipping forward to
where you were, except track radio offers no way to select a track, and the
whole point of listening to it is not knowing what is coming — so there is no
position to skip back to. You lose your place and cannot get it back.

That is the case where moving playback would be most useful, and it is the case
where it fails worst.

**Consequences.** No move-playback action anywhere in the UI. `canMovePlayback`
from `/Status` is parsed like any other field but nothing consumes it.

**Revisit if.** Firmware starts preserving position across a move, particularly
for generated playlists. This is a device behaviour, not a client limitation, so
the signal is a change on the device side rather than a better implementation
here.

### D18. Out of scope

Zone and home-theatre pairing, stereo pairs, subwoofer pairing, channel modes,
speaker distances. Soundbars. Rechargeable and battery players. Anything
specific to custom-integration or professional hardware. Service authentication
flows — services are already authenticated on the player. Player setup and Wi-Fi
provisioning. Firmware upgrade triggering (D12). Discovery, for now (D11).
Authentication (D13).

The official app stays installed for these.

---

## The project itself

Name, licence, data, and the vendor's API Use Policy.

### D16. Naming, data, and the API Use Policy

**Decision.**

- **Naming.** The name is **Musica**. No Lenbrook mark in the product
  name, logo or domain. No
  compatibility badge or endorsement-style tagline either. The project says what
  it talks to in a sentence of prose where that is useful, and nowhere else. A
  badge claims a relationship and implies complete support; neither is true.
- **No user data.** No telemetry, no analytics, no crash reporting, nothing
  leaving the LAN. Collecting nothing removes the policy's privacy and deletion
  obligations rather than satisfying them.
- **No Lenbrook code in the repository.** Decompiler output stays out.
- **MIT licensed.** Chosen deliberately rather than left absent. It carries the
  warranty disclaimer, imposes nothing on anyone, and does not change the
  analysis below — a licence grants rights in *this* code and says nothing about
  the Use Policy.
- **Trademark acknowledgement stays generic.** Marks belong to their owners and
  are used descriptively. Naming each rights holder reads like a legal filing
  rather than a personal project, and enumerating them invites the reader to
  weigh a relationship that does not exist.

**On the protocol documentation.** The material splits cleanly by provenance and
should be treated differently:

- Behaviour derived from the **published Custom Integration API** — `/Browse`,
  `/Status`, `/Volume`, grouping, LSDP — is publicly documented by the vendor,
  and can be described freely with a citation.
- Behaviour derived from **decompiling the official client** is what the Use
  Policy's no-reverse-engineering clause bears on, and where the real licensing
  risk sits.

So there are two protocol documents, and only one of them is committed.

- **`docs/bluos-http-api.md`** is the full reference and the source of truth for
  anything wire-level. It is a private working file, maintained outside this
  repository. It stays in the working tree so it can be read while writing code,
  and it is listed in `.gitignore` so git never sees it.
- **`docs/protocol-notes.md`** is committed. It is written as endpoints are
  implemented, and it describes only the behaviour the code depends on, phrased
  as observed device behaviour. No account of how anything was found, no client
  class or method names, no source clients named. It cites the reference by
  section so the two stay tied.

It will therefore be permanently incomplete, which is the intent. Documenting
less than is known is the cheapest available reduction in exposure, and nothing
in the code needs the rest. That is a further argument for D17: the `/Services`
declaration is the device telling us the schema at runtime, so less of it has to
be written down anywhere.

**On the competition clause.** A personal, non-commercial controller is almost
certainly not the target — a decade of hobbyist and even paid third-party
controllers have been tolerated. The question sharpens at publication. Nothing
here is legal advice; read the full policy before anything public.

**Revisit if.** The project moves toward publication. That should be a decision,
not a drift.

---

## Decisions promised to this document but not written

`MOTIVATION.md` expects both of these to be taken here. Neither is.

### Build on an existing project, or start over

`MOTIVATION.md` links here for it: the bluesound_alt integration was forked and
its group playback fixed before the remaining requirements were judged out of
reach, and the conclusion that the survey stops there is a decision in its own
right. Until it is written the link from `MOTIVATION.md` lands on nothing.

### One solution for desktop and phone, or two

`MOTIVATION.md` no longer mentions this at all. `README.md` answers it in
substance — a web app served from the home server, reachable from anything with
a browser — but nothing records it as a decision, so the reasoning and the
revisit condition are missing.

When both are written, the open end in `MOTIVATION.md` that tracks them goes.

---

## Candidates for the plan, not here

First-pass notes for the next edit. Nothing below has been moved.

### Passages that read as plan material

- **D9, the four numbered steps and both worked examples.** The decision is
  that a group which is already correct is left alone. The call sequence, the
  batching and the `/SyncStatus` re-poll are how Tier 2 carries it out.
- **D10's ~1 s TTL.** The decision is that optimistic state never reaches the
  server. The number is a tuning value.
- **D14's Consequences.** Cache key composition, which sort orders are
  pre-cached, the crawl's node and depth caps, and the fields in-list search
  matches on.
- **D17's Consequences.** Request construction, parameter replacement,
  per-service sort vocabularies, `resultType` rendering and filter semantics.
  `PLAN.md` already carries most of this under "Browsing, sorting and search —
  settled".
- **D6's opaque tokens.** That device URLs and browse keys never reach the
  browser is a decision; the token mechanism that achieves it is not.

### Elements that overlap each other or another document

- **D5 and D6.** D6 is written as the exception to D5 and only makes sense
  beside it. One element with an exception clause, or two, but not one of each.
- **D17 and D14.** Sort ownership and the cache key are stated in both.
- **D18 against D11, D12, D13 and D19.** D18 is an index of decisions that each
  already declare their own scope, plus a few lines that are declared nowhere
  else (zone and home-theatre pairing, soundbars, battery players, service
  authentication, Wi-Fi provisioning). Only those lines are load-bearing.
- **D1, D2 and D3 against `CLAUDE.md`.** Its "Non-negotiable constraints"
  section restates all three and asks in its own heading whether it needs to.
- **D16's protocol-documentation split against `CLAUDE.md`.** "The two protocol
  documents" says the same thing at the same length.

### Elements that do not follow the four-field structure

No **Revisit if**: D4, D9, D10, D14, D15. D18 has none of the four fields at
all — it is a list.
