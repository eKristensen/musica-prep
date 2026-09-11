# BluOS protocol — test plan

Companion to `bluos-probe.py`. What the harness tests, why those tests, what it
deliberately does not touch, and what the later destructive rounds need.

The specification is now broad. What it is thin on is **independent
confirmation**: a large share of it rests on reading client code, and a
meaningful share on single third-party projects. Section 17 lists nineteen such
claims. `TEST-LOG.md` records ten more results as inconclusive, not performed,
or performed against the wrong target. Those are the two lists this round exists
to shorten.

---

## Principles

**Repeat anything a third party asserted.** `/diagnostics` is the case that
justifies the whole exercise: one source, dismissed as failing on hardware,
actually real — the check had been aimed at port 11000 instead of port 80. So
every check states its port, and the harness tries both.

**Repeat anything that came back uncertain.** T-6 `inputTypeIndex` returned an
empty body once. T-22 recalled a preset on one player and read status from
another. T-1a measured nothing because it used an invented etag. A test whose
result you cannot explain is a test that has not been run.

**A 404 is a result.** Unknown paths return a bare `text/plain` 404 from Go's
`net/http`, distinct from an endpoint that exists and refuses. That makes
existence probing cheap and unambiguous, and makes negative results worth
recording rather than discarding.

**Capture the body, not the conclusion.** Response bodies become fixtures for a
mock player and inputs to a parser. `TEST-LOG.md` already says that where the
narrative and the captures disagree, the captures win.

**Harvest shape automatically.** The specification's response tables came from
reading SAX handlers — that gives what the official app *reads*, not what the
device *sends*. Most item elements copy every attribute into an open string map,
so the documented lists are a lower bound. `SHAPES.md` inventories every element
path and attribute actually observed, which is the only way to find the
difference.

---

## Round 1 — what the harness runs

Every request is a read, or a bare-path existence check that has no target to
act on. Runtime is roughly 8–15 minutes for four players.

| suite | what it settles |
|---|---|
| `env` | Inventory and the core reads, per player. Establishes firmware, schema and topology, and seeds the redactor. Captures `/Services` from every player, which is the single most valuable file. |
| `transport` | Path case sensitivity on every player, not one. Unknown-path 404 shape on all three ports. Trailing and doubled slashes, dot segments, blank and duplicated parameters. HEAD, OPTIONS, POST, PUT, DELETE against a GET endpoint. **CORS preflight** — decides whether a browser client can talk to a player directly. **Whether the `X-Sovi-*` schema headers change the response**, which the specification suspects but no source confirms. |
| `ports` | The endpoint × port matrix across 80 / 11000 / 11001, in one table. Speculative player-enumeration paths (`/Players`, `/Zones`, `/Topology`, …) against open question 7. Every URI advertised by `/ui/Configuration`, which is a surface nothing has ever walked. |
| `longpoll` | Which endpoints actually honour `etag`+`timeout` — asked of eight, where the specification only documents three. Stale, empty, zero-length and 200-character etags. Malformed and negative timeouts. A concurrency ladder from 8 upward, stopping at the first level where connections are not held, which finds the ceiling T-1 left open. |
| `errors` | A survey of failure bodies: unknown service, missing parameter, unknown browse key, malformed schema version, 300-character path. Distinguishes the four conventions — plain 404, structured `<error type>`, flat `<error>text</error>`, raw HTML. |
| `claims` | The read-only half of the section 17 register, each called the way its source describes it: `/diagnostics` on 80 **and** 11000, `/audiomodes` as a bare read, `/proxyToSlave` and `/Sync` existence, radio item attributes, `/Search` containers, album-scoped `/Songs`, `/Shares` on both ports. |
| `artwork` | The now-playing artwork URL taken from `/Status`, then its headers: CORS, `ETag`, `Cache-Control`. The no-artwork case and its content type. The by-name form. `HEAD` on artwork. |
| `browse` | A bounded crawl following only `browseKey` and browse-typed `url` attributes — never a `playURL`. Paging edges including the 50-item cap, `start > end`, negatives and non-numeric. Nine sort values including four descending spellings, which closes T-25 either way. The `%26` versus `&amp;` key encoding failure, kept because it fails silently with HTTP 200. |
| `settings` | The 11001 tree, then a `schemaVersion` sweep from 0 to 99 to see what appears and disappears. Eleven settings pages by id. Confirmation that 11001 still serves settings only. |
| `discovery` | LSDP broadcast `Q`, both with class `0xFFFF` and with the four player classes. **`R` unicast at a known player — T-26**, the untested route to cross-subnet discovery. Raw packets are stored hex-encoded and decoded field by field. |
| `inputs` | Every surface that enumerates physical inputs — the browse root, `/RadioBrowse?service=Capture`, the `/Settings?id=capture` page and `/Sources` — cross-tabulated per player. This is what shows whether an input disabled in the Controller app is genuinely disabled or only hidden from that one view. Read-only; the write half is in `state_source`. |
| `stability` | Is `/Services` byte-stable across calls on one player? Across players? Does the `/Status` etag churn while nothing is playing? Is `/SyncStatus` `etag` always equal to `syncStat`? These decide what a client may cache. |

### Deliberately not tested

Cut after an audit, because the result would not change how anything gets built:

- **Invented endpoint names.** `/Fleet`, `/Hub`, `/Topology`, `/Rooms`,
  `/Discovery`, `/Members`, `/Nodes` and friends had no source behind them.
  Guessing endpoint names is a lottery, not a test. Only `/Players`,
  `/Devices`, `/Zones` and `/Groups` survive, on the grounds that the first two
  appear in adjacent vendor APIs and the last two in CI-series vocabulary.
- **URL trivia** — `/./Status`, `/Status%20`, a 300-character path, a
  200-parameter query. No client emits these. Trailing and doubled slashes are
  kept, because a URL builder really does produce those.
- **PUT and DELETE** on a GET endpoint. No client sends them; the answer changes
  nothing.
- **Invariants repeated per player.** Path case sensitivity is a property of one
  HTTP router in one firmware build and cannot vary across players running it.
  Full set on the first player, a two-path spot check on the next, controlled by
  `--breadth` so a mixed-firmware fleet is still caught.
- **The 11000 column of the port matrix** for paths the `env` suite already
  captured there.

### Not answerable on this hardware

Separate from the above, and reported separately. `detect_capabilities` reads
each player's inputs, presets, Bluetooth and subwoofer state at the start of the
run, and any suite whose result would be decided by a missing capability is
skipped as **NOT APPLICABLE** rather than run to produce a row of failures.

This matters because the two look identical in a result table and mean opposite
things. "No player advertises a capture input, so every selector came back
IGNORED" is a fact about the fleet. Written into the register as `DISCONFIRMED`
it becomes a false claim about the protocol — and, being append-only, one that
persists. `FINDINGS.md` lists these under *Not answerable on this hardware* with
an explicit instruction not to promote them.

### Not called at all

Bare forms that are known or suspected to act, excluded so the round-1 promise
holds without qualification:

`/SetMaster` (a bare call makes a slave leave its group) · `/AddSlave` ·
`/RemoveSlave` (a bare call may ungroup everything — that is precisely claim
T-36a) · `/Standalone` · `/LeaveGroup` · `/Sync?slave=` and `?remove=` ·
`/Sleep` (bare cycles the timer) · `/Play` · `/Pause` · `/Stop` · `/Skip` ·
`/Back` · `/Volume?level=` · `/Preset` · `/SlaveVolume` · `/PlayTestSound` ·
`/Add` · `/Clear` · `/Save` · `/Delete` · `/Move` · `/MovePlayback` ·
`/setting` · `/alsa_setting` · `/Name?set=` · `/Reindex` · `/upgrade` ·
`/AddShare` · `/RemoveShare` · `/AddToPlaylist` · `/Load` · `/AddFavourite`.

Three paths **are** called with no parameters, because existence is the whole
question and none of them has a target to act on: `/audiomodes`,
`/proxyToSlave`, `/Sync`. `--no-probe` omits them if you would rather they
waited for round 2.

---

## Round 2 — reversible state changes  *(implemented)*

`--suite round2 --allow-state`. Every suite snapshots what it will disturb,
changes it, reads the result back, restores explicitly, and then **verifies the
restore**, reporting a failed restore as an ERROR rather than passing over it.

Guards: `--max-volume` (default 10 on the 0–100 scale) is a hard ceiling on any
level this run sets; `--preserve LABEL` marks a player read-only even in round 2
and is honoured by every suite including grouping. Nothing in round 2 creates or
deletes a preset, a playlist or a favourite — presets are only ever recalled.

**Crash safety.** Each undo is registered at the moment of the change, not at
the end of the suite, and the whole suite loop runs inside a `finally` that
replays the ledger. An exception, a failed assertion or Ctrl-C therefore still
puts the player name, volume, sleep timer, LED brightness and group topology
back. Undos are idempotent, so the normal path — where a suite restores things
itself — costs nothing. Anything that could not be restored is printed at the
end, written into the `restore` section of `REPORT.md`, and makes the process
exit non-zero.

**Bundle honesty.** `README.md` inside the bundle describes what the run
actually did, listing the state-changing endpoints it touched and the players it
wrote to. A read-only bundle and a state-changing bundle say different things,
so a bundle can never claim it left the hardware alone when it did not.

| test | claim or gap | recovery |
|---|---|---|
| T-22 `<is_preset>` / `<preset_name>` | Blu4Net; last attempt read status from the wrong player | recall the original source |
| T-27 `/Play?inputType=&index=` | `bluos-api-rs`; both `hdmi` and `arc` spellings; must run **while playing**, or an ignored parameter looks like success | switch the source back |
| T-18 `/Play?inputTypeIndex=` | inconclusive in T-6; needs the input actively receiving signal | as above |
| T-28 play-response roots | Blu4Net says four; two have samples. `<addsong>` with `id`/`count`/`length` is the only report of where a queue insert landed | `/Delete` the added entry |
| T-35 setting writes: GET query or POST form | blutui and pyblu disagree; LED brightness is visible and reversible | write the original value back |
| `/Name` POST with `nodename=` | blutui; `?set=` is confirmed | `?set=` the original name |
| T-11 `/Sleep` bare cycling | which values, in what order, and does it wrap | `minutes=0` |
| C-53 disabled inputs still selectable | tries every `inputTypeIndex` slot, advertised or not, while playing | switch the source back |

#### How an input change is judged to have worked

Three false positives are possible here, and each has already caught someone:

1. **HTTP 200 means nothing.** BluOS answers 200 to parameters it ignores.
2. **A `/Play` carrying unrecognised parameters degenerates into a bare
   `/Play`, which resumes playback.** Against a paused player that is
   indistinguishable from success. This is what nearly settled T-6 the wrong
   way.
3. **Two different inputs are both `service=Capture`**, so checking the service
   name cannot tell you whether the *right* input was chosen — or whether
   anything moved at all, if the previous trial already left the player there.

So the suite works like this. It builds a **fingerprint** from `service`,
`inputId`, `streamUrl`, `title1..3`, `image`, `streamFormat` and `song` —
deliberately *excluding* `state`, because a state change from pause to play is
what a rejected parameter looks like, not what success looks like.

It learns each input's fingerprint by selecting it with the `playURL` the device
itself advertises. That is the **positive control**: if the device cannot select
its own advertised input, detection is broken and every negative result below is
worthless, and the suite says so rather than reporting a clean sweep of
failures.

Each trial then runs from a known starting input, and is only declared IGNORED
once it has failed to move the player from *every* known starting input — which
removes the "already there" ambiguity. **Negative controls** — selectors that
cannot exist, such as `inputType=zzznotreal` — are interleaved at the start and
the end. If one of them appears to work, the whole suite is marked unsound.

Verdicts are therefore IGNORED, RESUMED ONLY (the degenerate `/Play`), SELECTED
A KNOWN INPUT, or SELECTED SOMETHING NOT ADVERTISED — that last one being the
signature of an input disabled in the app but still live in firmware.

| `/Repeat` and `/Shuffle` bare | do they read or reset? | restore from the pre-snapshot |
| Does a state change release held long-polls? | asserted, never observed | none needed |
| etag semantics under change | does `/Status` etag change for volume, and `/SyncStatus` for grouping only? | restore volume |

### `/SetMaster` — round 2b, its own suite

Grouping is where third-party clients most often go wrong, and the existing
`/SetMaster` findings come from a single pass in which the topology was not
always reset between cases. `state_setmaster` runs a full matrix: every role
(standalone, master, slave, nested master) crossed with every parameter form
(bare, `?master=` with and without `port`, `?master=` at itself, at a
non-player, at a second master, and the ignored `?slave=`).

Three things make it trustworthy where the earlier pass was not. Each case
**forces a known topology first** and skips itself, loudly, if it cannot reach
one. Cleanup uses `/RemoveSlave` from the master rather than `/SetMaster`, so
the endpoint under test is never used to reset the test — and any case that
needed the fallback is flagged as suspect. And every case reads `/SyncStatus`
from **both ends** before and after, then compares the response's own `etag`
against the pre-call one, which is how the earlier pass was misled: `/SetMaster`
appears to answer with the state as it was *before* the call.

### Grouping — round 2c, separate

Worth isolating because a nested group makes players vanish from the Controller
app until it is dissolved. Ungroup everything first, record the starting
topology, and restore it at the end.

| test | claim |
|---|---|
| T-36a bare `/RemoveSlave` ungroups everything | HA integration, asserted without evidence |
| T-36b numeric `channelMode=0\|1\|2` | HA integration; conflicts with the string form used everywhere else |
| `port` optional in singular `/AddSlave` | 2015 forum |
| `/SlaveVolume?slave=<ip>:<port>` combined form | blutui |
| T-34 `/proxyToSlave` POST relay | blutui; only proof is the slave's setting actually changing |
| T-30 legacy `/Sync?slave=` and `?remove=` | bluos-dashboard |
| T-16 three-level nesting | two levels verified; reachable with four players by building from the far end inward |
| T-29 orphaned-group recovery | needs the primary powered off mid-group; a power cut will produce this eventually anyway |

---

## Round 3 — destructive

Left until the configuration is being changed for real reasons.

- **T-15b `/AddShare`, `/RemoveShare`** — wipes network share config. Capture
  `/Shares` first; the password is never returned, so you must know it.
- **`/Reindex`** — long-running, and `logall=` is undocumented.
- **`/upgrade`** — triggers a firmware update. Only on a player you are willing
  to lose for a while.
- **`/Delete`, `/Save`, `/Clear`, `/AddToPlaylist`** — playlist mutation. Do it
  against a scratch playlist created for the purpose.
- **`/AddFavourite` and `removeFavourite=1`** — mutates the streaming account,
  not the player. Least reversible thing here, since it touches TIDAL state.
- **T-19 `/Name` across a reboot** — free next time a player restarts anyway.

---

## Blocked

**T-14 authentication.** No way found to set credentials on a consumer N-series
player. The auth path in §1.1 is source-derived and unexercised. Worth one more
look at `/ui`, the port 80 web UI and the Integration Utility before recording it
as CI-hardware-only.

**mDNS.** Deliberately not implemented in the harness — any mDNS tool does it
better. Run alongside:

```
avahi-browse -rt _musc._tcp        # Linux
dns-sd -B _musc._tcp               # macOS
```

Also worth `tcpdump -i any -n udp port 11430` while the official app starts, to
confirm nothing sends `R` in practice.

---

## Feeding results back

1. Run the harness, read the `Results that did not match the specification`
   table first — every row there is a specification error, a firmware
   difference, or a mis-aimed test.
2. Work the `Claim checks` table against section 17. Move what is confirmed out
   of the register into the body with a `[V hardware]` marker; record what fails
   **in place** rather than deleting it, so the next reader does not rediscover
   the same dead end.
3. Diff `SHAPES.md` against the response-shape tables in §11. Anything in
   `SHAPES.md` that is not documented is a gap; anything documented that never
   appears is conditional or historical.
4. Keep the bundle. `MANIFEST.json` is structured so two runs — across a
   firmware upgrade, or across models — diff directly.
