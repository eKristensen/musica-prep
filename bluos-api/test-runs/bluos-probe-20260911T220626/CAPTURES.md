# Capture index

Every response below was captured with the topology or playback state
named in the first column, staged deliberately by the `state_capture`
suite rather than set up by hand. Each is redacted and dated by the
bundle it lives in.

Files are also copied into `captures/<state>/<player>-<endpoint>.xml`,
which is the browsable form. `raw/` keeps the originals under their
probe ids.

| state | player | probe | file |
|---|---|---|---|
| playing as-found: Tidal mqa | A | `001-state_capture` | `captures/playing-as-found-tidal-mqa/A-SyncStatus.xml` |
| playing as-found: Tidal mqa | A | `002-state_capture` | `captures/playing-as-found-tidal-mqa/A-Status.xml` |
| standalone | A | `005-state_capture` | `captures/standalone/A-SyncStatus.xml` |
| standalone | A | `006-state_capture` | `captures/standalone/A-Status.xml` |
| standalone | A | `007-state_capture` | `captures/standalone/A-Presets.xml` |
| standalone | A | `008-state_capture` | `captures/standalone/A-Playlist.xml` |
| standalone | A | `009-state_capture` | `captures/standalone/A-Volume.xml` |
| standalone | B | `010-state_capture` | `captures/standalone/B-SyncStatus.xml` |
| standalone | B | `011-state_capture` | `captures/standalone/B-Status.xml` |
| standalone | B | `012-state_capture` | `captures/standalone/B-Presets.xml` |
| standalone | B | `013-state_capture` | `captures/standalone/B-Playlist.xml` |
| standalone | B | `014-state_capture` | `captures/standalone/B-Volume.xml` |
| standalone | C | `015-state_capture` | `captures/standalone/C-SyncStatus.xml` |
| standalone | C | `016-state_capture` | `captures/standalone/C-Status.xml` |
| standalone | C | `017-state_capture` | `captures/standalone/C-Presets.xml` |
| standalone | C | `018-state_capture` | `captures/standalone/C-Playlist.xml` |
| standalone | C | `019-state_capture` | `captures/standalone/C-Volume.xml` |
| standalone | D | `020-state_capture` | `captures/standalone/D-SyncStatus.xml` |
| standalone | D | `021-state_capture` | `captures/standalone/D-Status.xml` |
| standalone | D | `022-state_capture` | `captures/standalone/D-Presets.xml` |
| standalone | D | `023-state_capture` | `captures/standalone/D-Playlist.xml` |
| standalone | D | `024-state_capture` | `captures/standalone/D-Volume.xml` |
| playing (preset recall) | A | `029-state_capture` | `captures/playing-preset-recall/A-SyncStatus.xml` |
| playing (preset recall) | A | `030-state_capture` | `captures/playing-preset-recall/A-Status.xml` |
| group: A master, B slave | A | `033-state_capture` | `captures/group-a-master-b-slave/A-SyncStatus.xml` |
| group: A master, B slave | A | `034-state_capture` | `captures/group-a-master-b-slave/A-Status.xml` |
| group: A master, B slave | B | `035-state_capture` | `captures/group-a-master-b-slave/B-SyncStatus.xml` |
| group: A master, B slave | B | `036-state_capture` | `captures/group-a-master-b-slave/B-Status.xml` |
| nested: A -> B -> C | A | `043-state_capture` | `captures/nested-a-b-c/A-SyncStatus.xml` |
| nested: A -> B -> C | A | `044-state_capture` | `captures/nested-a-b-c/A-Status.xml` |
| nested: A -> B -> C | B | `045-state_capture` | `captures/nested-a-b-c/B-SyncStatus.xml` |
| nested: A -> B -> C | B | `046-state_capture` | `captures/nested-a-b-c/B-Status.xml` |
| nested: A -> B -> C | C | `047-state_capture` | `captures/nested-a-b-c/C-SyncStatus.xml` |
| nested: A -> B -> C | C | `048-state_capture` | `captures/nested-a-b-c/C-Status.xml` |
| one-sided: D joined A via ?master= | A | `054-state_capture` | `captures/one-sided-d-joined-a-via-master/A-SyncStatus.xml` |
| one-sided: D joined A via ?master= | A | `055-state_capture` | `captures/one-sided-d-joined-a-via-master/A-Status.xml` |
| one-sided: D joined A via ?master= | D | `056-state_capture` | `captures/one-sided-d-joined-a-via-master/D-SyncStatus.xml` |
| one-sided: D joined A via ?master= | D | `057-state_capture` | `captures/one-sided-d-joined-a-via-master/D-Status.xml` |

## What this does not cover

Third-party sample responses -- BluShell's schema-25 captures and
similar -- are not hardware captures and cannot be regenerated here.
They belong in a separate reference folder, cited as `[T]`, not in a
folder of machine-produced captures.
