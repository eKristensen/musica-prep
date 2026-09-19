# Third-party project inventory — reconciliation

Which of the projects listed in
[`../musica/ECOSYSTEM.md`](../musica/ECOSYSTEM.md) were examined for the
protocol work, and what each one contributed. Three were recorded wrongly;
they come first.

---

## Discrepancies

### Marked "analyzed", initially not examined — now done

Both were flagged as unread in the first pass of this reconciliation, then
provided and analyzed. The markers are now correct.

| Project | Contribution |
|---|---|
| **Home Assistant Core `bluesound`** | Built on **pyblu 2.0.8**, so no new endpoints. Corroborates the independent leader/follower model, and supplies a fourth long-poll data point (`timeout=120`, read timeout 125, on both `/Status` and `/SyncStatus`). Discovers via `_musc._tcp.local.` only. |
| **`aunefyren/bluesound_alt`** | Independent implementation, not pyblu. Uses `/Browse` root filtered to `type="audio"` items to build its source list, and a bare `/Volume` read to get a follower's own level as distinct from group volume. `timeout=100`, read timeout 110. |

Neither changed a protocol fact; both firmed up existing ones.

### Marked "to analyze" but actually done

| Project | Note |
|---|---|
| **`Pimmeke1989/bluos`** | Analyzed. It was the `bluos-main.zip` upload — confirmed by `manifest.json` listing `@Pimmeke1989` as codeowner. Findings: its `TROUBLESHOOTING_JOIN_UNJOIN.md` produced two grouping claims, both **left out** of the specification as unverified (numeric `channelMode=0\|1\|2`, and a bare `/RemoveSlave` ungrouping everything). Both are in the register at §17 and testable as T-36. |

---

## Confirmed correct

Everything else matches. For the record, with what each contributed:

### Full controller apps

| Project | Status | Contribution |
|---|---|---|
| BluOsNadRemote | analyzed ✓ | Nothing — wraps Blu4Net, which was analyzed directly |
| bluesoundplayer (rdOxalis) | analyzed ✓ | Two endpoints **rejected**: `/Standalone`, `/LeaveGroup` |
| BluRemote | closed source ✓ | — |
| bluos-controller-linux | correctly skipped ✓ | Repack of the official Windows app, which was analyzed |

### CLIs and TUIs

| Project | Status | Contribution |
|---|---|---|
| blucli | analyzed ✓ | Nothing new; corroborated the core endpoint set |
| tbaur/bluos-controller | analyzed ✓ | Nothing new (9 endpoints, all known) |
| blutui (LimpSquid, Rust) | analyzed ✓ | `/proxyToSlave`, `/diagnostics` (**since disconfirmed**), `ledbrightness`, POST-form setting writes |
| blutui (mkozjak, Go) | analyzed ✓ | `bySection` browse keys, `browseIsFavouritesContext` |
| bluos-dashboard | analyzed ✓ | Orphaned-group recovery, legacy `/Sync`, browser connection budget |
| ibeex/blue_cli | not analyzed | Not marked as analyzed — correct |

### Libraries

| Project | Status | Contribution |
|---|---|---|
| pyblu | analyzed ✓ | `/alsa_setting`, `/audiomodes` parameters, **captured settings XML** |
| Blu4Net | analyzed ✓ | Polymorphic play response, `<addsong>`, radio item attributes |
| bluos-api-rs | analyzed ✓ | `/Play?inputType=&index=`; also showed `sid` treated as required |
| Nightvision | analyzed ✓ | **Real LSDP packets** — the worked Announce in §12.1 |
| coral/lsdp | analyzed ✓ | Independent LSDP wire-format confirmation |
| proxus-consulting/bluos | analyzed ✓ | Nothing — Swagger shim over `/Preset`, `/Presets` |
| BluShell | analyzed ✓ | **45 sample responses**; `/audiomodes` as a read, `/Alarms` bitmask, `/Search` containers, `/Artwork` XML fallback |
| venjum/bluesound | analyzed ✓ | Nothing new |
| BluShepherd | analyzed ✓ | `/Artwork` CORS headers, album-scoped `/Songs`, `playnow=-1` |
| ClausRN/BluesoundAPI | analyzed ✓ | Nothing new |
| StoneBite | correctly skipped ✓ | — |

### Not analyzed, and correctly unmarked

Web interfaces (kindofblu, great-horn/amp) and the whole
displays/scrobblers/single-purpose section. The reasoning in
[`../musica/ECOSYSTEM.md`](../musica/ECOSYSTEM.md) holds:
these touch a narrow slice of the API, and every endpoint a scrobbler needs
(`/Status` polling) is already covered several times over.

The one exception worth reconsidering is **`jliuhtonen/blu-hawaii`**, by the
same author as Nightvision — that author's LSDP work turned out to be the best
material found on discovery, so their scrobbler may be written with the same
care. Low expected value, but the highest of that section.

---

## Sources used that are not on the list

[`../musica/ECOSYSTEM.md`](../musica/ECOSYSTEM.md) covers third-party
projects. The specification also rests on
material that is not a project at all, and which produced most of its content:

| Source | Contribution |
|---|---|
| BluOS Controller for Android 4.16.2 (decompiled) | The single largest source — exact element and attribute names from the SAX handlers |
| BluOS Controller for Windows 4.16.0 | `syncStat`, port 80 surface, many `/Status` fields |
| BluOS Controller for macOS 4.16.0 | **Original TypeScript** in the sourcemap — discovery and authentication |
| Vendor *Custom Integration API* v1.7 | `/Browse`, LSDP wire format, the documented subset |
| BluOS RTI driver 2.60 | Readable vendor JavaScript; `/Load`, `/Browse` usage |
| BluOS Integration Utility 1.8.1 | `/Sleep?minutes=`, `/Reindex`, `/GetSettings` |
| Crestron / NICE / GIRA / Control4 drivers | CI580 port offsets; otherwise compiled or encrypted |
| "Bluesound API decoded" forum thread, Nov 2015 | Historical corroboration; `playnow` values |
| **Hardware testing** | The only source that can disconfirm anything |
