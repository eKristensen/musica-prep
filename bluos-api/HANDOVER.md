# Handover — state of play

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

The old captures are unredacted. Replacing them takes **one round-1 run**, not
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

Everything else in `captures/` is reproducible. Keep
`third-party-samples/` as a separate reference folder cited as `[T]` — it is
not hardware evidence and does not belong in a folder of machine-produced
captures.

## Files to keep

| file | why |
|---|---|
| `bluos-http-api.md` | the specification itself — the actual deliverable |
| `bluos-probe.py` (v1.4) | the harness; 126 self-test assertions, `--verify-harness` before any run |
| `SPEC-ADDITIONS-grouping.md` | the working notes behind the §5 rewrite, including the first-party app evidence. Now folded in — keep it as provenance, not as a to-do |
| `SPEC-SECTION-claim-register.md` | the append-only §17 design and marker scheme |
| `TEST-PLAN.md` | what is tested, what is deliberately not, and why |
| `RUNBOOK.md` | how to run it |
| `CODE-REVIEW.md` | static-analysis record and the two review rounds |
| `FINDINGS.md` + `SHAPES.md` + `REPORT.md` from each hardware run | the evidence |

## Files to discard

- **`BluOS-Controller-4_16_0-MacOS.zip` (297 MB)** — mined. The grouping code is
  extracted into `SPEC-ADDITIONS-grouping.md`. Keep the DMG locally in case a
  future question needs it, but do not upload it again; it is expensive and
  slow to re-open.
- **`com_bluesound_bluesoundplayer_53.apk`** — third-party, thin, and misleading
  if treated as first-party. See the correction in
  `SPEC-ADDITIONS-grouping.md`.
- **`raw/` directories from hardware runs** — hundreds of files. Keep them
  locally as parser fixtures; do not paste them into a chat. `SAMPLES.md` has
  one canonical response per endpoint, which is what a spec needs to quote.
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

## Test status: complete

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

## Fixed in v1.6

**The harness itself was not shareable.** It embedded a real device MAC —
`90:56:82:98:06:6E`, lifted from `captures/syncstatus/` and propagated into
seven test fixtures plus the raw bytes of the LSDP announce fixture. All
identifying values are now synthetic and the convention is stated at the top of
the file: RFC 7042 documentation MACs (`00:00:5E:00:53:xx`) and `10.255.255.x`
fixture addresses. 126 assertions still pass.

## Fixed in v1.4 and v1.5

1. **A MAC address was reaching shared bundles.** LSDP `node_id` is a MAC with
   the separators stripped (`905682982996`), which `MAC_RE` could not see.
   Every discovery capture you have shared so far contains real device MACs.
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
