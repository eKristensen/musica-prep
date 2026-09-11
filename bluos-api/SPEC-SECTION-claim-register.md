# Proposed replacement for §17 — the claim register

The current §17 is a to-do list. It records what is *unverified*, and when
something gets verified the row leaves the table. That loses the negative
results, which is the thing you identified: `/GetSettings` was tested, found
absent, and the fact now lives only in a narrative log. The next person to read
the Integration Utility's strings will find `/GetSettings`, believe it, and
rediscover the 404.

The fix is to make the register **append-only** and give every claim a
**permanent id**. A claim never leaves the table. It gains a verdict, a date,
and a pointer to the evidence.

---

## §17. Claim register

Every claim about this protocol that came from somewhere other than Lenbrook
code, the vendor document, or a capture in `captures/`. Rows are never deleted.
A claim that has been disconfirmed keeps its row so that the next reader who
meets it in a third-party project can see it was already checked — when,
against what firmware, with what request, and with what answer.

**Verdicts.**

| verdict | meaning |
|---|---|
| `CONFIRMED` | Observed on hardware, doing what the source said. The detail lives in the body of this document; the row remains as provenance. |
| `DISCONFIRMED` | Tested the way the source describes it, including the port, and it did not do that. **Not** implemented. |
| `INCONCLUSIVE` | Tested, answer unclear. Records what was ambiguous so a retest can be aimed better. Different from untested. |
| `UNTESTED` | No hardware result yet. |
| `SUPERSEDED` | A later firmware changed the answer. The old row stays; a new row is appended below it. |

`INCONCLUSIVE` and `UNTESTED` are not weak forms of `DISCONFIRMED`. Do not
implement against either.

| id | claim | source | § | verdict | tested against | request → answer | evidence |
|---|---|---|---|---|---|---|---|
| `C-01-diagnostics-80` | `/diagnostics` answers on port 80 | blutui (Rust) | 13 | CONFIRMED | 2026-xx-xx, N110/N130/N132, fw 4.16.22, schema 34 | `GET :80/diagnostics` → 200 HTML | *bundle*, `nnn-claims` |
| `C-02-diagnostics-11000` | `/diagnostics` does **not** answer on 11000 | this project | 13 | CONFIRMED | as above | `GET :11000/diagnostics` → 404 | *bundle*, `nnn-claims` |
| `C-06-getsettings` | `/GetSettings` exists and returns JSON | Integration Utility 1.8.1 | 10.1 | DISCONFIRMED | 2025-xx-xx, N132, fw 4.16.22 | `GET :11000/GetSettings` → 404 `text/plain` | `captures/transport/GetSettings-404.txt` |
| … | | | | | | | |

### Why the "tested against" column is not optional

`/diagnostics` came from one third-party source, was reported as failing, and
was very nearly written off. The check had been aimed at port 11000. On port 80
it works exactly as described. A verdict without the exact request that produced
it is not a verdict; it is a rumour with a table row.

So every row states: the firmware and schema it was tested against, the full
request including **port and method**, and the answer. A claim tested on one
model is not settled for all models — append a second row rather than editing
the first.

### Retired claims

Rows whose verdict is `DISCONFIRMED` stay in the table above. They are the most
valuable rows in it, because they are the ones that stop work being repeated.
When you meet an endpoint in a third-party project, search this table by
endpoint name **before** implementing or testing it.

---

## How the harness feeds this

`bluos-probe.py` carries the same ids in `CLAIMS`, tests each one the way its
source describes, and writes `FINDINGS.md` containing rows already formatted for
this table — including the disconfirmed ones. The workflow is:

1. Run the harness.
2. Open `FINDINGS.md`, take the block under *Rows for the specification's
   disconfirmation register*, paste it in.
3. For `CONFIRMED` rows, also move the detail into the body of the document and
   change its marker from `[T]` to `[V hardware]`. The register row stays.

Because the ids are stable, a second run months later against new firmware
produces rows that line up with the old ones, and a changed answer becomes a
`SUPERSEDED` pair rather than a silent edit.

## Ids are permanent

`C-06-getsettings` means `/GetSettings` returning JSON, for ever. If a future
firmware brings it back, that is a new row with the same id and verdict
`SUPERSEDED` on the old one — not a rewrite. Never reuse an id for a different
claim.

---

# Confidence and evidence are two different axes

Your instinct here is right, and the current markers conflate two things that
should be separate.

**Confidence** answers *how far should I trust this?* It comes from provenance:
first-party code and vendor documents are strong, a third-party project is weak.

**Evidence** answers *what does it actually look like?* That is a captured
response, and it is useful regardless of confidence. The whole point of this
document is that nobody should need to decompile an APK to find out that
`<slave>` carries a `port` attribute. Reading a SAX handler tells you the field
is *read*; only a capture tells you what arrives, in what order, with what
formatting, and alongside what undocumented siblings.

So a `[V first-party]` element does not need *testing* — but it does benefit
from a *sample*. Those are different activities, and the harness already does
the second one for free while doing the first.

## Markers

| marker | meaning |
|---|---|
| `[V]` | Verified against first-party material: Lenbrook code, the vendor document, or the official app's own behaviour. |
| `[V hardware]` | Observed directly on a player. Cites a bundle and probe id. |
| `[T]` | Third-party assertion, carrying a `C-nn` id in the register. |
| `[U]` | Inference or conjecture by this document. Never implement against `[U]` without checking. |
| `[S]` | **New.** A captured sample exists in `SAMPLES.md`. Orthogonal to the others: `[V][S]` is normal and desirable. |

`[S]` is not a confidence claim. `[V][S]` means "certain, and here is what it
looks like". `[T][S]` means "one project asserts this, and here is a capture of
whatever the device actually returned" — which is often how a `[T]` gets
resolved.

## The trap to avoid

A single capture shows what one player did once, on one firmware, in one state.
Most BluOS elements are conditional: `<preset_name>` only exists while a preset
is playing, `<slave>` only on a master, `muteDb` only while muted.

**Absence from a sample never disconfirms a `[V]` claim.** If first-party code
reads a field and no capture contains it, the field is conditional and the
correct action is to document *when* it appears — not to delete it. Only an
explicit contradiction (the field present with a different type, name or
meaning) can demote a `[V]`.

This is the one direction in which "test everything" would actively damage the
document, and it is worth stating in the specification itself so a future
contributor does not prune fields they failed to observe.
