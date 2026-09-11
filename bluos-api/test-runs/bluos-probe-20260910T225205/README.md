# BluOS probe bundle

Automated state-changing probe of a live BluOS fleet, produced by
`bluos-probe.py 1.4` on 2026-09-10T22:52:05.

## What is here

| file | what it is |
|---|---|
| `REPORT.md` | every probe, grouped by suite, with a verdict against the specification |
| `MANIFEST.json` | the same data structured, for diffing between runs |
| `SHAPES.md` | element/attribute inventory harvested from every XML body captured |
| `SAMPLES.md` | one canonical, pretty-printed response per endpoint, for the specification to quote |
| `FINDINGS.md` | claim-by-claim verdicts, including the disconfirmed ones, ready to paste into the register |
| `REDACTIONS.md` | what was removed and what replaced it |
| `raw/` | redacted response bodies and headers, one pair per probe id |


## What was run

**This run changed player state.** It was invoked with `--allow-state`,
so the `read`, `probe` and `state` safety classes were all enabled.
29 state-changing request(s) were issued against player(s) A, B, touching
these endpoints:

  `/AddSlave`, `/RemoveSlave`, `/SetMaster`

Every change was snapshotted beforehand and restored afterwards; the
`restore` section of `REPORT.md` records whether each restore
succeeded. Nothing irreversible was attempted: no share was modified,
no firmware path was called, and no preset, playlist or streaming
favourite was created or deleted.

## Reading it

`REPORT.md` opens with the rows whose result did not match the
specification. Those are the ones worth reading first: each is either a
specification error, a firmware difference, or a test that was aimed
wrongly.

## Timezone

Devices were told `Europe/Copenhagen` in the `X-Sovi-Tz` header on every request.
That is a fixed, recorded constant rather than whatever the machine
running the harness was set to, because BluOS uses it for
time-dependent answers -- alarm times in particular. Read every clock
value in these captures against that zone. The harness host's own
clock at the time of the run was CEST (UTC+0200), recorded in
`MANIFEST.json` under `timezone` so the two can be told apart.

## Privacy

Addresses, MAC addresses, share hosts, credentials and other identifying
values were replaced before anything was written to disk, and the whole
bundle was re-scanned afterwards to confirm none survived. See
`REDACTIONS.md`. Placeholders are stable within the run, so
`192.0.2.11` is the same player everywhere.
