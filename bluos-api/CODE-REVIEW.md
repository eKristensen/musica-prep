# Static analysis and refactor record

Tools run against `bluos-probe.py`. Reproduce with:

```
pip install ruff pyflakes vulture bandit radon
ruff check --select F,E,W,B,C4,SIM,RET,PIE,PERF,RUF --ignore E501,E702 bluos-probe.py
vulture --min-confidence 80 bluos-probe.py
bandit -ll bluos-probe.py
radon cc -a -s bluos-probe.py
python3 bluos-probe.py --verify-harness
```

## Was it WET?

Partly, and the part that mattered was the response parsing. There had been
three separate `/SyncStatus` parsers — in `preflight`, `take_snapshot` and
`_sync_of` — each with its own regex for `<slave id=…>` and `<master>`. That is
the worst possible place for duplication: the code that **restores** your
hardware depends on reading the slave list correctly, and it must not be able to
drift from the code that read it in the first place. Four `etag` extractions and
two element-text helpers were also independent.

Those are now a single layer: `root_attrs`, `element_text`, `element_int`,
`parse_sync`, `parse_status`, plus `add_slaves_url` / `remove_slaves_url` for the
grouping URLs. Sixteen call sites use it; nothing parses `/SyncStatus` by hand
any more.

What is **not** deduplicated, deliberately: the suites themselves. Each
`run.call(...)` names an endpoint, a claim id, a spec section and an
expectation, and reads as a statement about the protocol. Collapsing them into
a table-driven loop would save lines and make the file harder to audit — and
auditability is the point, since the output is evidence. That WETness is the
feature.

## Findings and what was done

| finding | tool | action |
|---|---|---|
| Three duplicate `/SyncStatus` parsers, four `etag` extractions | manual | merged into one accessor layer |
| `main` at cyclomatic complexity **F (57)** | radon | split into `build_parser`, `resolve_targets`, `resolve_suites`; now E (33) |
| `build_report` **F (45)**, `build_findings` **F (42)** | radon | section builders extracted; now E (32) and C (17) |
| `ET.fromstring` / `minidom.parseString` on network data | bandit B314/B318 | all XML now goes through `safe_parse_xml`: refuses `<!DOCTYPE` so entity expansion cannot happen, caps body size, never raises |
| Unit tests writing to `/tmp` | bandit B108 | `tempfile.mkdtemp` |
| `ALLOWED_SAFETY`, `Player.display` dead | vulture | removed |
| Ambiguous `l`, unused unpack `st` | ruff E741/RUF059 | renamed |
| No F-class (undefined name, unused import) errors at any point | ruff/pyflakes | — |

Average complexity is now **B (8.3)** across 106 blocks, with no F-grade
functions. Remaining accepted findings: two `B104` (binding `0.0.0.0`, required
to receive LSDP broadcast replies), one `B314` inside `safe_parse_xml` itself
(guarded, annotated `# nosec`), fourteen `E702` semicolons in the LSDP byte
parser where `x = msg[p]; p += 1` reads better than two lines, and three
`PERF203`/`PERF401` micro-optimisations in code that runs once per bundle.

## The tests are now real, and they fail when they should

`--verify-harness` grew from "does the redactor scrub an address" to **78
assertions** covering the response parsers, the redactor, the expectation
matcher, claim verdicts, safety gating, the restore ledger, the LSDP codec,
argument parsing and report assembly. It writes no bundle and produces no
protocol evidence.

Each assertion pins a bug that actually happened. To prove they are not
decorative, each was mutation-tested by reintroducing the original bug:

| bug reintroduced | caught |
|---|---|
| `root_attrs` scanning a 1200-char slice, so `<slave name=…>` wins | 3 assertions fail |
| keep-list short-circuiting before a reserved player address | 1 fails |
| `state` added back into the source fingerprint | 1 fails |
| restore ledger unwinding forwards instead of in reverse | 1 fails |

The keep-list assertion **passed** under mutation on the first attempt — it was
asserting the wrong direction. That is corrected and now fails as it should.

## Two bugs the review itself found

1. **Splitting `build_findings` silently dropped the "Promote out of the
   register" section.** Every logic assertion still passed, because none of them
   looked at the assembled document. Restored, and there are now assertions that
   each report contains every section it promises.
2. **The *Claim checks* table filtered on `"[T"` appearing in the note text.**
   Probes carry a structured `claim` field now, so every claim probe whose note
   lacked that prose marker was missing from the table — which was all of
   `state_setmaster` and both disabled-input checks. It keys on `pr.claim` and
   shows the verdict.

Both are the same class of mistake as the earlier README problem: a promise made
in one place and derived in another. The report-assembly assertions exist to
catch the next one.


---

# Second review round (external agent)

An external review found 30-odd issues across redaction, the restore ledger and
verdict integrity. Its framing was the useful part: the script makes three
strong promises, and each had gaps that undermined it. All High and Medium items
are fixed; the structural Quality items are not.

## Fixed

**Redaction.** `AUTH_HDR_RE` had no word boundary and an optional `=`, so any
prose containing "response" was rewritten -- corrupting `/Status` bodies,
breaking XML and JSON parsing, inflating `redaction_edits`, clearing `verbatim`,
and mangling the harness's own analysis notes. Removed; sensitive headers are
now redacted by name, which also covers `Authorization`, `Cookie` and
`Set-Cookie`, none of which the old pattern touched. Keys tolerate a prefix
(`wifiPassword`, `accessToken`); JSON bodies and HTML form values have their own
rules; `verify_bundle` gained a heuristic pass so a secret the redactor never
recognised is flagged instead of the run printing "clean". The key file stores
salted digests instead of `value`-class originals and is created 0600. Encoded
literal variants (`%2B`, `%C3%B8`, `&#248;`, `%3A`-separated MACs) are
registered. MAC redaction is idempotent; the MAC pool uses two octets; short
originals match on word boundaries; all three RFC 5737 ranges are kept.

**Restore ledger.** `defer_get` raises on transport errors and non-2xx, with an
optional readback verify -- previously a timed-out or 500 restore printed `ok`.
`SyncInfo.reachable` means an unanswering player reads as unknown, not
standalone. Topology comparison uses `(master, slaves)`. `SlaveRef` carries per
slave `port` and `channelMode`, so stereo pairs and CI580 zones rebuild
correctly. `group_conflicts` refuses a grouping suite when a writable player
shares a group with a preserved or unlisted one. `teardown_groups` reports which
players *needed* the bare `/SetMaster` fallback. `cap_volume` applies
`--max-volume` before any suite that can start audio, and the flag is validated
0-100. Restores run in the per-suite `except`, so the next suite cannot baseline
a half-restored fleet.

**Verdicts.** CONFIRMED plus DISCONFIRMED now yields MIXED, with
`quantifier: "any"` for genuinely existential claims. The `/SetMaster` matrix
decides from `expect_change` against the readback it already computed, so C-42
can fail. C-35's inversion is fixed and decided by reading the value back; C-17
requires `<is_preset>` to be present; C-34, C-38 and C-40 got readback verdicts.
C-10, C-18, C-19, C-21 and C-46 return INCONCLUSIVE on degenerate inputs, and
the LSDP unicast Q now runs *before* R as its control. A failed control in
`state_source` forces INCONCLUSIVE. Unknown matcher clauses raise. The
concurrency ladder requires `status == 200` before counting a connection held.

**Robustness.** Non-ASCII device paths are percent-encoded, `ValueError` caught.
All control flow reads a bounded raw-body cache on the `Runner` that never
reaches the manifest, so browse keys and playURLs are no longer taken from
redacted or 400-character text and the crawl works under `--no-bodies`.
`parse_players` rejects duplicate labels, handles `[v6]:port`, and errors
cleanly on a bad port. Exit codes: 3 restore, 4 redaction, 7 both, 130
interrupted. `/ui` URIs are allowlisted; the concurrency ladder's real load is
documented and can be switched off with `--concurrency-max 0`.

**Timezone.** `X-Sovi-Tz` is fixed at `Europe/Copenhagen` rather than derived
from the host, recorded in `MANIFEST.json`, `REPORT.md` and `README.md`, and
the report warns when the harness host's clock is in a different zone.

## Test coverage

`run_selftest` used to start a fake player, print its port and shut it down
without sending a request -- so `Runner.call`, `write_bundle`, `verify_bundle`,
the key file and restore-over-HTTP had no coverage, which is exactly where R1,
R3, S1 and S3 lived. `_end_to_end_test` now drives a real bundle against a fake
player using the fixtures this review reproduced: a non-ASCII room name, JSON
with a password, a `<response>` element, a percent-encoded MAC, credential
headers, and a restore returning 500. **117 assertions**, all mutation-tested:

| bug reintroduced | caught by |
|---|---|
| `AUTH_HDR_RE` restored | `<response>` element survived redaction intact |
| `defer_get` swallowing errors | a 500 restore is reported as failed |
| header-name redaction disabled | bundle does not contain the Digest nonce |
| JSON redaction pass removed | bundle does not contain the password; **and the verifier independently flagged `wifiPassword` and `ssid`** |
| key file storing `value` originals | key file does not contain the secret |
| `SlaveRef.port` dropped | e2e parses the slave port |

`ruff --select F` also caught a genuine `F821`: a snapshot block whose anchor
had not matched, leaving `fb` undefined on the C-40 path. Restored.

## Not fixed

Q1 (file ordering), Q3 (`Runner.call`'s wide keyword interface, typed matcher
objects) and the remainder of Q4's duplication helpers. Q2 is only partly
addressed -- `slave_query` takes an explicit port, but `main()` still mutates
module globals, so the root cause stands. These are refactors rather than
correctness fixes, and reshaping the file in the same pass as this much
behavioural change would make the diff unreviewable.
