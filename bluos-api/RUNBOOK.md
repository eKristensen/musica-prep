# Runbook

Python 3.8+ and nothing else. Standard library only, no virtualenv, no pip.
Run it from a machine on the same subnet as the players.

```bash
mkdir -p ~/bluos-probe && cd ~/bluos-probe
cp /path/to/bluos-probe.py .
chmod +x bluos-probe.py
```

---

## 0. Check the harness before it touches anything

```bash
python3 bluos-probe.py --verify-harness
```

Expect `126 passed, 0 failed`. Two lines reading `ERR boom` and
`ERR e2e: a restore that returns 500` are **supposed** to appear: they are the
tests that prove a failing restore is reported as failed.

No bundle is written and no player is contacted. If this does not pass, stop.

---

## 1. Find the players

```bash
python3 bluos-probe.py --discover --suite discovery --out runs
```

About fifteen seconds. It sends LSDP queries and prints what answers:

```
  found Stue at 192.168.x.x:11000
```

If nothing answers, the machine is probably on a different subnet or VLAN from
the players, or a host firewall is dropping UDP 11430. Fall back to naming them
by address; everything below works the same way.

To find out *why* discovery is slow or flaky rather than working around it,
`lsdp-static/` measures it — how long a round takes, and how often a round
comes back short — and can answer LSDP queries itself from a static player
list, which is how to tell an unreliable network apart from an unreliable
protocol. Measured controller timings are logged in
`controller-discovery-timings.md`.

Note the labels it assigned (A, B, C, D) — they are how every later report
refers to each player, and `A` is the one that gets the single-player tests.
To control that, name them yourself:

```bash
python3 bluos-probe.py --player A=192.168.1.10 --player B=192.168.1.11 \
                       --player C=192.168.1.12 --player D=192.168.1.13 ...
```

Put the player you care most about first. Round 1 does per-player inventory on
all of them, but the deep suites (browse, settings, long-poll) run against `A`.

---

## 2. Round 1 — read-only

```bash
python3 bluos-probe.py --discover \
    --secret 'YOUR-NAS-HOSTNAME' \
    --secret 'YOUR-WIFI-SSID' \
    --out runs
```

Roughly 10–15 minutes for four players. Nothing changes player state.

**`--secret` matters.** It scrubs an exact string, and its encoded forms,
everywhere. Use it for anything the redactor cannot infer: the NAS hostname, the
Wi-Fi SSID, a person's name in a room or Bluetooth device name. Repeatable. It
is the one thing you must supply by hand — everything else (addresses, MACs,
share credentials, tokens) is automatic.

Two things to know before you press enter:

- The long-poll ladder briefly holds up to 32 simultaneous connections to
  player A. If the BluOS app or a Home Assistant integration is mid-something,
  it may stutter for a few seconds. `--concurrency-max 0` skips it, at the cost
  of leaving the connection ceiling unmeasured.
- Room and player names are **kept** by default, because they carry no personal
  information and make the captures readable. Add `--redact-names` to replace
  them with `Room-A`, `Room-B`.

### Before sharing

The last lines tell you whether it is safe:

```
redaction check: clean -- no address, MAC or supplied secret survived
zip:     bluos-probe-20260910T....zip  (nnn KB) -- this is the file to share
```

If instead it says the check **failed**, no zip is created. It will name the
files and the values it found. Add them with `--secret` and re-run.

Two files appear next to each other. Send me the **zip**. Keep
`DO-NOT-SHARE-key-*.json` — it maps `192.0.2.11` back to your real addresses so
you can read your own results, and it is created mode 0600 for that reason.

Exit codes: `0` clean · `3` a restore did not complete · `4` redaction findings
· `7` both · `130` interrupted.

---

## 3. Round 2 — reversible state changes

Only after round 1 has been read. Run the grouping matrix **on its own first**,
so its results are not tangled with playback and volume changes:

```bash
python3 bluos-probe.py --discover --allow-state \
    --suite state_setmaster \
    --secret 'YOUR-NAS-HOSTNAME' --out runs
```

Ten to fifteen minutes. It will group and ungroup repeatedly. Expect the
players to disappear and reappear in the BluOS app while it runs — that is the
test working. It records your starting topology first and rebuilds it at the
end, and the ledger rebuilds it even if the suite crashes or you press Ctrl-C.

Then the rest:

```bash
python3 bluos-probe.py --discover --allow-state --suite round2 \
    --secret 'YOUR-NAS-HOSTNAME' --out runs
```

What this does to your system, explicitly:

- **Volume** goes no higher than level 10, and is lowered to 10 before any suite
  that can start audio. Original level and mute state are restored.
- **Playback** starts, pauses and toggles. Track position cannot be restored
  through the API — a paused track resumes from where the suite left it.
- **Input** switches on the player with the most inputs. Best-effort restore
  only: re-selecting your previous source may need a tap in the app.
- **Presets** are recalled, never created or deleted. Your two presets are safe.
- **TIDAL** favourites and playlists are never touched. No `/AddFavourite`, no
  playlist create or delete.
- **Player name** is temporarily changed and set back.
- **LED brightness** is changed and set back.
- **Sleep timer** is cycled and cleared.

If anything fails to restore, the run prints it, writes it into the `restore`
section of `REPORT.md`, and exits 3. Nothing waits until the end: a suite that
crashes triggers its restores immediately, so the next suite starts from a clean
state.

### Worth doing first, if you can

Re-enable optical on the Stue player for the round-2 run. With two working
inputs the input tests become conclusive; with one, "it switched" cannot be
separated from "it was already there" and the suite says so rather than
guessing. Disable it again afterwards and re-run just `--suite inputs,state_source`
to compare — that pair of runs is what settles whether "disabled" means
disabled or only hidden.

### If you would rather a player were left completely alone

```bash
--preserve D
```

Never written to, in any suite, including grouping. You do not need it for the
preset player: nothing in round 2 creates or deletes a preset.

---

## Sending results

Send the zip from each run. If a run produced anything interesting, the useful
files to look at yourself are:

| file | what to read it for |
|---|---|
| `REPORT.md` | opens with results that did not match the specification — read those first |
| `FINDINGS.md` | claim-by-claim verdicts, plus rows ready to paste into §17 |
| `SHAPES.md` | every element and attribute observed, per endpoint — the gap list against §11 |
| `SAMPLES.md` | one canonical response per endpoint, for the spec to quote |

---

## If something goes wrong mid-run

Ctrl-C once. The restore ledger runs, prints what it put back, then writes the
partial bundle. Do not Ctrl-C twice unless it hangs — the second one can
interrupt a restore, and it will tell you which one.

If a player ends up renamed, grouped oddly or at the wrong volume, re-running
the same suite will re-snapshot and restore from wherever things are now. The
ledger prints exactly what it could not fix, so there is never a guess about
what needs a manual tap.
