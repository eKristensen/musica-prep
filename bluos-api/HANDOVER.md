# Handover — state of play

## Current status (updated 2026-09-11)

Everything below this box is the original handover, written after the
2026-09-10 runs and before the two 2026-09-11 runs existed. It is kept
because the reasoning in it is still the reasoning — but read this box
first for what has actually happened since.

**Runs on disk, current:**

| bundle | harness | what it is |
|---|---|---|
| `bluos-probe-20260910T225205` | 1.4 | `state_setmaster` — the full grouping-matrix pass behind §5.3 and `C-41`–`C-51` |
| `bluos-probe-20260910T225427` | 1.4 | `round2` — volume, playback, sleep, name, setting, preset, source and grouping state changes |
| `bluos-probe-20260911T220357` | 1.6 | `all` — the full read-only round 1 (env, transport, ports, longpoll, errors, claims, inputs, artwork, browse, settings, discovery, stability; 450 probes). This is the primary read-only evidence bundle now: it supersedes the three unredacted 9/10 round-1 runs this document told you to delete, and also the narrow 22:51 discovery-only run |
| `bluos-probe-20260911T220626` | 1.6 | `state_capture` — the staged-topology capture tree described below, now actually produced |

**Removed in this cleanup pass:** `bluos-probe-20260910T225109` (the 22:51
discovery-only bundle). Its 8 probes, including the `C-19` unicast-LSDP
result, are byte-for-byte reproduced inside `bluos-probe-20260911T220357`'s
own `discovery` suite — same fleet, same node ids, same INCONCLUSIVE verdict,
newer harness. Nothing was lost.

**`PROJECT-INVENTORY.md`** belongs in the "files to keep" table below; it was
missing from it. Its corrections are already folded into the Sources table at
the top of `bluos-http-api.md`.

**Open work — the spec has not caught up with `20260911T220357`:**

1. Only two spots were fixed in this pass, both unambiguous: §5.2 (`/Sync`)
   and §10.0 (`/proxyToSlave`) now say what §17.1 already recorded for `C-05`
   and `C-04` instead of still saying "untested". A dozen more claims that
   run resolved — `C-07`, `C-08`, `C-09`, `C-10`, `C-11`, `C-12`, `C-13`,
   `C-15`, `C-18`, `C-22`, `C-52` — are tested in `FINDINGS.md` but not yet in
   §17.1 or the body text. Mechanical, but real work; do it as its own task
   per `TEST-PLAN.md`'s "Feeding results back" section, fed `FINDINGS.md`
   rather than the raw bundle.
2. **`C-03` (`/audiomodes` as a read) now disagrees with itself.** §17.1
   still says CONFIRMED, from the original 2026-09-10 hardware pass — the one
   deleted from this repo for leaking a real MAC address. The clean
   2026-09-11 re-run of the same claim, same firmware, same schema, came back
   INCONCLUSIVE: 200 OK, but a 9-10 byte body on both players, not the
   populated `<audiomode>` element the vendor sample shows. That is not a
   mechanical merge — it needs a look at why the body differs before §17.1 is
   touched.
3. §17 carries two claim tables — the topic-ordered list that opens the
   section, and the id-ordered §17.1 — and they can now drift apart exactly
   the way `C-03` and `C-04` show. `SPEC-SECTION-claim-register.md` specified
   one append-only table. Worth collapsing to that next time someone is
   editing §17, rather than maintaining two by hand.

---

## Where the project is

The specification is verified far enough to build against. Grouping — the part
third-party clients most often get wrong — is now settled from two independent
sources that agree: hardware results and the official desktop Controller's own
code.

**Verified on hardware:** the whole `/SetMaster` behaviour table (C-41 through
C-45, C-50, C-51), `/diagnostics` on port 80 only, `/Name` POST form (C-34),
`/Play?inputType=&index=` (C-37).

**Disconfirmed on hardware — keep these rows, they are the ones that stop work
being repeated:** `<is_preset>` does not exist (C-17), bare `/RemoveSlave` does
not drop every slave (C-30), disabled inputs are genuinely not selectable
(C-53), `/GetSettings` is absent, the legacy `/Sync` path is absent,
`/SetMaster?master=<self>` is accepted rather than rejected (C-48).

**Still open, and probably not worth chasing:** authentication (no way to enable
it on N-series), CI-series multi-zone, LSDP unicast (silent in both forms with
the firewall open, so likely broadcast-only), `/Search` on LocalMusic and Tidal
returning 404 with the parameters tried.

## Recommendation

Stop spec-first work and start building the client. The remaining unknowns are
mostly things an app will not touch. Every time you have to guess or open a
decompiler while building, that is a gap worth one test — and it is a gap you
know matters, rather than one you are testing because it is testable.

The claim register protects you here: "unverified" is now recorded with a
permanent id rather than forgotten, so stopping costs nothing.

---

## The specification has been updated

`bluos-http-api.md` now carries the hardware findings directly. Changed:

- **§0.4 (new)** — how `[V hardware]` claims were tested, and the two traps:
  HTTP 200 means nothing on a write, and a claim is not settled until tested the
  way its source describes it.
- **§0 markers** — `[V hardware]`, `[V official]` and `[S]` added, plus the rule
  that absence from a capture never disconfirms a `[V]` claim.
- **§2.2** — `<is_preset>` never appears in `/Status`; it is a radio-item
  attribute, which is where the claim came from.
- **§5** — a bare `/RemoveSlave` does not drop every slave; the `force=0` →
  confirm → retry path and its two error strings.
- **§5.3** — substantially rewritten. Role reversal is **not** rejected; it
  produces a mutual master loop. `?master=` membership is one-sided. Six new
  behaviours in the call table. Staleness split by form.
- **§6** — `/ExternalSource` absolute selection by `chassisInputId`.
- **§17** — rewritten as an append-only register with permanent ids and 35
  hardware verdicts, plus §17.2 listing what this hardware cannot answer.

## The capture set is now a build artefact

**Done** — see `test-runs/bluos-probe-20260911T220626/captures/`.

`state_capture` (v1.6) stages each documented state deliberately and captures
every player at each one, instead of relying on states someone set up by hand
once and saved. It produces a browsable tree inside the bundle:

```
captures/standalone/A-SyncStatus.xml
captures/group-a-master-b-slave/B-Status.xml
captures/nested-a-b-c/B-SyncStatus.xml
captures/one-sided-b-joined-a-via-master/A-SyncStatus.xml
captures/playing-preset-recall/A-Status.xml
```

plus `CAPTURES.md` indexing state to probe id to file. Everything is redacted,
dated by its bundle, and carries the firmware and schema it came from — none of
which the hand-made folder did.

```bash
python3 bluos-probe.py --discover --allow-state --suite state_capture \
    --secret 'ek-nas' --secret 'machina' --out runs
```

It stages: **whatever is already playing** (captured first, before anything is
touched); all standalone; playing from a recalled preset; a two-player group; a
three-player group; a nested master; and the one-sided `?master=` join, which
the old set never contained at all. Topology is restored and the restore
verified.

**To capture a content-dependent state** — an MQA stream, a radio stream with
`<actions>` — start it playing on any player first, then run this suite. It
lands in `captures/playing-as-found-<service>-<quality>/`. That is the only way
such a capture can exist: no harness can conjure a particular stream.

## Replacing the old `captures/` set

**Done** — the hand-made `captures/` folder this section describes is gone
from the repo, replaced by `bluos-probe-20260911T220357` (round 1) and
`bluos-probe-20260911T220626` (`state_capture`). Kept below for the record of
what replaced what.

The old captures were unredacted. Replacing them took **one round-1 run**, not
a discovery run — discovery only produces LSDP packets.

| old folder | files | replaced by |
|---|---|---|
| `lsdp/` | 2 | **already replaced** by the 22:51 discovery run |
| `services/` | 3 | round 1, `env` suite |
| `syncstatus/` | 4 | round 1, `env` — except the staged nested/grouped states |
| `status/` | 3 | round 1, `env` — except the staged Tidal/MQA states |
| `browse/` | 11 | round 1, `browse` suite |
| `settings/` | 6 | round 1, `settings` suite |
| `transport/` | 5 | round 1, `transport` suite |
| `misc/` | 1 | round 1, `env` |
| `third-party-samples/` | 8 | **never** — not hardware captures |
| staged states in `status/`, `syncstatus/` | 4 | `state_capture`, and it stages more of them |

```bash
python3 bluos-probe.py --discover --secret 'ek-nas' --secret 'machina' --out runs
```

Eighty seconds. After it passes the redaction check, the old `captures/` folder
can go **except** for two things that no run reproduces:

- **`third-party-samples/`** — BluShell's schema-25 samples. Not from your
  players at all, and the only evidence of what an older schema returned.
- **Nothing**, if you start RadioParadise playing before the `state_capture`
  run. The two content-dependent status captures
  (`A-N132-radioparadise-mqa`, `A-N132-radioparadise-with-actions`) are then
  reproduced as `playing-as-found`.

Everything else in `captures/` was reproducible, and the folder is gone.
`third-party-samples/` — BluShell's schema-25 samples, not hardware evidence —
is also not present as a folder in this repo; its content lives inline in
`bluos-http-api.md` wherever a claim cites "BluShell sample". If a future
sample turns up that isn't already quoted in the spec, give it a reference
folder of its own cited as `[T]` rather than dropping it into `captures/`.

## Files to keep

| file | why |
|---|---|
| `bluos-http-api.md` | the specification itself — the actual deliverable |
| `bluos-probe.py` (v1.6) | the harness; 126 self-test assertions, `--verify-harness` before any run |
| `SPEC-ADDITIONS-grouping.md` | the working notes behind the §5 rewrite, including the first-party app evidence. Now folded in — keep it as provenance, not as a to-do |
| `SPEC-SECTION-claim-register.md` | the append-only §17 design and marker scheme |
| `TEST-PLAN.md` | what is tested, what is deliberately not, and why |
| `RUNBOOK.md` | how to run it |
| `CODE-REVIEW.md` | static-analysis record and the two review rounds |
| `PROJECT-INVENTORY.md` | third-party source-list reconciliation; corrections already folded into `bluos-http-api.md`'s Sources table |
| `FINDINGS.md` + `SHAPES.md` + `REPORT.md` from each hardware run | the evidence |

## Files to discard

**Done** — none of the four items below are in this repo. Kept as a record of
what was deliberately left out and why, so nobody re-uploads them.

- **`BluOS-Controller-4_16_0-MacOS.zip` (297 MB)** — mined. The grouping code is
  extracted into `SPEC-ADDITIONS-grouping.md`. Keep the DMG locally in case a
  future question needs it, but do not upload it again; it is expensive and
  slow to re-open.
- **`com_bluesound_bluesoundplayer_53.apk`** — third-party, thin, and misleading
  if treated as first-party. See the correction in
  `SPEC-ADDITIONS-grouping.md`.
- **`raw/` directories from hardware runs** — hundreds of files. They stay
  inside each `test-runs/` bundle as parser fixtures; do not paste them into a
  chat. `SAMPLES.md` has one canonical response per endpoint, which is what a
  spec needs to quote.
- **`BluOS_RTI_Driver_Package_2_60.zip`** — already mined in an earlier pass.

---

## Starting a fresh chat

Upload: the spec, `bluos-probe.py`, `SPEC-ADDITIONS-grouping.md`,
`SPEC-SECTION-claim-register.md`, and the `FINDINGS.md` from the most recent
runs. Then open with something like:

> I am building a BluOS HTTP API specification. Attached: the spec, the test
> harness, hardware findings, and the claim-register design. I have four
> players (N132, N132, N130, N110) all on firmware 4.16.22, schema 34.
>
> Task for this chat: **[one specific thing].** Do not modify the harness.

One task per chat. The expensive pattern is asking a single chat to build the
tool, run it, interpret the output and rewrite the spec — each round re-reads
everything that came before.

Split by job:

- **Harness changes** → cheapest model that holds the file. Mechanical, and
  `--verify-harness` proves it still works.
- **Spec writing and result interpretation** → a stronger model, fed
  `FINDINGS.md` and `SHAPES.md` rather than raw bundles.

---

## Test status: complete (as of 2026-09-10, superseded — see the box at top)

Three v1.4 runs on 2026-09-10 (22:51 discovery, 22:52 `state_setmaster`, 22:54
`round2`) came back with the `state_setmaster` suite fully clean — 70 probes,
zero ERROR, zero UNEXPECTED, every case reaching a verdict instead of being
skipped. The MAC leak is closed: every `node_id` in the shared discovery
captures is now a placeholder.

**No further hardware runs are needed.** v1.5 changes two verdict *labels*, not
what is measured, and the underlying readbacks were already captured — the
corrected C-39 reading comes from the topology table in the 22:52 bundle itself.

Remaining unresolved, and not worth more effort:

- **C-36 mute polarity** — INCONCLUSIVE across four players. The `/Volume`
  readback appears not to carry a `mute` attribute on this firmware, so the
  test cannot see the effect. Resolvable by reading `<mute>` from `/Status`
  instead, if it ever matters.
- **C-33 `/SlaveVolume` combined form** — INCONCLUSIVE.
- **Volume restore on D failed once** and three players were restored to
  `pause` from `stop`. Both are cosmetic: the ledger reported them rather than
  hiding them, which is the behaviour that matters.
- **Only one input learned**, so C-53 (disabled inputs not selectable) is
  strong but not conclusive. Re-enabling a second input would settle it.

## Fixed in v1.7

**Real MACs and addresses were still leaving in packet dumps.** A discovery
capture writes each datagram twice, parsed into JSON and again as a `raw_hex`
string. The parsed copy was redacted; the hex copy was not, and it carried four
real device MACs and four real player addresses out of
`test-runs/bluos-probe-20260911T220357`.

Neither the scrubber nor the verifier could have caught it, and no amount of
pattern tuning would have. On the wire a node id is a bare MAC with no
separators and no boundary, so `MAC_HEX_RE`'s lookarounds fail inside the longer
hex run of a dump, and an address is four raw bytes that no dotted-quad pattern
can match. The bundle was reported clean because the verifier was blind in the
same place the scrubber was.

Both sides are now structural rather than textual:

- `Redactor.redact_lsdp_packet()` rewrites the identifying fields inside a
  datagram, and discovery captures redact the bytes *before* parsing them, so
  the two copies cannot disagree. Placeholders are the same length as what they
  replace, so the packet stays structurally identical.
- `verify_bundle` decodes every long hex run and inspects it as a packet, via
  `_lsdp_identifiers()`.

Eight assertions cover it, including one that asserts the blind spot still
exists so the note above cannot go stale silently. 134 pass.

The already-published bundle was corrected in place; its `REDACTIONS.md` records
what was wrong rather than being quietly fixed.

## Fixed in v1.6

**The harness itself was not shareable.** It embedded a real device MAC, lifted
from `captures/syncstatus/` and propagated into seven test fixtures plus the raw
bytes of the LSDP announce fixture. All
identifying values are now synthetic and the convention is stated at the top of
the file: RFC 7042 documentation MACs (`00:00:5E:00:53:xx`) and `10.255.255.x`
fixture addresses. 126 assertions still pass.

## Fixed in v1.4 and v1.5

1. **A MAC address was reaching shared bundles.** LSDP `node_id` is a MAC with
   the separators stripped (twelve bare hex digits, e.g. `00005e005303`), which
   `MAC_RE` could not see. Every discovery capture shared before this fix
   contains real device MACs.
2. **C-35 was mis-scored.** The settings tree reports a display string
   (`off`/`dim`/`bright`), not the numeric value written, so "asked 1, got dim"
   read as failure. The GET query form works — pyblu is right, blutui is wrong.
3. **C-40 now resolves to DISCONFIRMED.** Bare `/Shuffle` wrote `1 → 0`. The
   confirming cases only meant the flag already held 0.
4. **C-30's verdict now reaches `FINDINGS.md`.** It had no claim id, so a
   genuine disconfirmation was visible only as an UNEXPECTED row.
5. **C-39 is no longer skipped.** The clean-start guard treated the bare
   `/SetMaster` fallback as contamination, when after a slave-side join it is
   the only way to free a player — because no master lists it. One-sided
   membership is now distinguished from a genuine `/RemoveSlave` failure, and
   measured directly as its own claim, `C-54`.
6. **`/ExternalSource` is probed** read-only — a first-party endpoint absent
   from the published document.

**v1.5** adds two corrections that need no re-run:

7. **C-39 is now judged on the end state, not on "something changed".** The
   attempt leaves each player naming the other as its master — a mutual loop,
   not a swap — so the verdict is DISCONFIRMED. See
   `SPEC-ADDITIONS-grouping.md`.
8. **C-46 split into two claims.** `?master=` returns the pre-call state
   (confirmed, six cases); the bare self-unjoin returns a fresh etag
   (`C-55`). As one claim it resolved to MIXED, which hid a clean split.

The bundles from the 22:5x runs are safe to keep and cite. The earlier ones
(18:35, 21:47, 21:49, 21:54) contain unredacted device MACs in their discovery
captures and should be deleted.
