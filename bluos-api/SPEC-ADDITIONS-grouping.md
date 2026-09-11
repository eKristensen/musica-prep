# Grouping: hardware results against the official apps

Three sources, agreeing. Hardware results from the `state_setmaster` runs, plus the grouping code read
out of **BluOS Controller 4.16.0 for macOS** (Electron/Vue, inside the DMG) and
**BluOS Controller 4.16.2 for Android** (`com.lenbrook.sovi`, three dex files).
Both are first-party, so what follows is `[V first-party]`, not `[T]`.

---

## The role reversal produces a mutual master loop

This is the most important single finding in the section, and it corrects an
earlier reading of the same run.

Starting from a proper group (A master, B slave), issuing
`A/SetMaster?master=B` — the "swap" — gives:

| player | master before | slaves before | master after | slaves after | group after |
|---|---|---|---|---|---|
| A | – | B | **B** | **B** | `Stue+Kontor` |
| B | A | – | A | – | – |

**A now names B as both its master and its slave, while B still names A as its
master.** Each player considers the other its master. That is a circular state
nothing else in the protocol produces, and it is not a swap: a swap would leave
A with no master and B holding A as a slave.

The harness first scored this CONFIRMED because the topology *changed*, which is
not the same as the roles *swapping*. Corrected in v1.5, which now judges the
end state and reports DISCONFIRMED with the loop named explicitly. The evidence
was captured correctly either way — the table above is from the run itself.

So: **role is fixed at group formation.** To reverse it, dissolve the group and
re-form it from the intended master. There is no swap operation, which is
exactly why doing it by hand appeared to fail while the app "just worked" — the
app dissolves first.

A client must never issue `/SetMaster?master=` to a player that is already a
master.

## Note on the APK — and a correction to my own earlier claim

`com_bluesound_bluesoundplayer_53.apk` is a third-party Flutter app
(`bluos_client.dart` shipped alongside `sonos_client.dart`, Sonos UPnP payloads
inside). I initially said the specification had it mislabelled as first-party
and that claims sourced from it needed re-grading.

**That was wrong.** The specification's source table already classes
`bluesoundplayer` as a consumer app that "added nothing", and had already
rejected two endpoints taken from it (`/Standalone`, `/LeaveGroup`). No
re-grading is needed. The correct official Android build,
`BluOS_Controller_4_16_2` (`com.lenbrook.sovi`), was also already mined in an
earlier pass.

---

## What the official app actually does

### It never forms a group with `/SetMaster`

The only `/SetMaster` call in the entire bundle is bare:

```js
function kf(e) {
  return $.get(`SetMaster`, {
    baseURL: e.toString(),
    headers: { Accept: `text/javascript; charset=utf-8`, "Accept-Language": `en-US` },
    timeout: 1e4
  })
}
```

No parameters. That is the self-unjoin — the form hardware confirmed as
`C-43`. **`/SetMaster?master=` is never used by the official app.**

### Groups are formed with `/AddSlave`, in five distinct shapes

| shape | parameters | purpose |
|---|---|---|
| singular | `slave`, `port` | add one player, addressed to the master |
| plural | `slaves`, `ports` (comma-joined) | add several at once |
| subwoofer | `slave`, **`ports`**, `slaveChannelMode=subwoofer`, `pairSlave=1` | pair a subwoofer |
| full | `channelMode`, **`group`**, `ports`, `slaveChannelMode`, `slaves` | named group with channel roles |
| full + delay | the above plus **`distance`**, **`slaveDistance`** | with per-player delay compensation |

The Android app adds the **plural** spellings and, usefully, their validation
messages:

- `slaveChannelMode` **and** `slaveChannelModes`
- `slaveDistance` **and** `slaveDistances`
- `slave channel mode size must equal the number of slaves`
- `slave distances size must equal the number of slaves`

So the plural forms are comma-separated lists whose length must match `slaves`.
The constraint is already in §5; the **plural spellings** and the exact
validation strings are the new part, and the strings are worth having because a
client can match on them.

**Correction to my earlier claim:** I described `group`, `distance`,
`slaveDistance` and `pairSlave=1` as undocumented. They are already in §5 of the
specification, derived from the official Android app in an earlier pass,
including the length-equality constraint. The genuinely new material from this
pass is narrower — the plural spellings and their validation strings below, and
the `group` parameter, which does not appear in §5's table.

Note the inconsistency in the subwoofer form: a **singular** `slave` with a
**plural** `ports` key. That is in the official app's own code, so a device that
accepts it is accepting a mismatched pair — worth a test before relying on
either spelling.

### Ungrouping has a two-stage protocol nobody has documented

```js
function YC(e, t, n) {                      // slave, force, schemaVersion
  return $.get(`RemoveSlave`, { params: { slave: e.host, port: e.port,
                                          force: t, schemaVersion: n },
                                skipGlobalErrorNotification: true })
}
```

and the caller:

```js
$C = async e => {
  YC(e, 0, schemaVersion).catch(t => {
    t.message === `Cannot move input source` &&
      openEventDrivenConfirmDialog({ title: `Remove from group`,
                                     message: `Cannot move input source`, ... })
  })
}
```

So the app removes with **`force=0`** first. If the device refuses with
`Cannot move input source`, it asks the user to confirm and retries — almost
certainly with `force=1`. Two undocumented parameters (`force`,
`schemaVersion`) and a named error string that a client must match on.

`/RemoveSlave` also has singular (`slave`, `port`) and plural (`slaves`,
`ports`) forms, matching `/AddSlave`.

### An endpoint with an undocumented second form

```js
function Of(e) {
  if (!e.chassisInputId && !e.changeDirection) Promise.reject(`invalid payload`)
  return $.get(`ExternalSource`, { baseURL: e.deviceId.toString(),
                                   params: { id: e.chassisInputId || e.changeDirection } })
}
```

**`/ExternalSource?id=`** — §6 of the specification already documents the
relative form, `id=+` and `id=-`. What is new is the **absolute** form: both
apps build the call as `id = chassisInputId ?? changeDirection`, so an input can
be selected directly by id rather than stepped to.

The Android app corroborates it heavily (22 references, a model class
`com.lenbrook.sovi.model.content.ExternalSource` with an inner `Item` type) and
names the directional variants: `nextExternalSource`, `previousExternalSource`,
`onNextExternalSource`, `onPreviousExternalSource`. So `changeDirection` steps
through inputs relatively while `chassisInputId` selects one absolutely. This
looks like the input-selection path for chassis products, and it is a genuine
gap in the specification. The harness probes it read-only in the `ports` suite.

Two more first-party error strings worth matching on, from the Android app:
`Cannot move a group while inserting`, and a
`newRetryRemoveMasterDialogFragment` that matches the macOS `force=0` → confirm
→ retry flow.

---

## How this matches the hardware results

| hardware finding | official app |
|---|---|
| `/AddSlave` produces a real group: master lists the slave, both show `group="A+B"` | agrees — this is the only way it forms groups |
| `/SetMaster?master=` produces a **one-sided** association: the joiner reports a master, the master lists no slave, no group name (probe `016`) | explains it — the app never uses this form |
| bare `/SetMaster` on a slave leaves the group (`C-43`) | agrees — the only `/SetMaster` the app issues |
| bare `/SetMaster` on a master is a no-op (`C-42`) | consistent: the master leaves nothing to leave |
| the swap attempt produces a **mutual master loop**, not a swap (`C-39` disconfirmed) | agrees — **no swap operation exists**. The app ungroups, then calls `/AddSlave` on the new master, so it never reaches this state |
| bare `/RemoveSlave` did **not** drop all slaves (`C-30` disconfirmed) | agrees — the app always names `slave`/`slaves` |

**Your original observation was correct and the cause is now known.** There is
no role-swap in the protocol. The app ungroups and re-forms in the other
direction, which is why doing it by hand appeared to fail while the app
"just worked". The specification should state this plainly: **role is fixed at
group formation; to reverse it, dissolve the group and re-form it from the
intended master.**

---

## Consequences for a client

1. **Build topology from both ends.** A player that joined via
   `/SetMaster?master=` is invisible in its master's `<slave>` list. Reading
   only the master's `/SyncStatus` will miss it.
2. **Form groups with `/AddSlave` addressed to the intended master.** Never use
   `?master=` for group formation.
3. **Handle `force`.** Expect `/RemoveSlave` to fail with
   `Cannot move input source` when the slave is the group's active source;
   confirm with the user, then retry with `force=1`.
4. **Never send `/SetMaster?master=<own address>`.** Hardware showed a player
   accepting itself as its own master (`C-48` disconfirmed), which is a state
   nothing else in the protocol produces.
5. **Grouping is asynchronous, and staleness depends on the form.** Every
   `/SetMaster?master=` call answered with the pre-call `/SyncStatus`, same etag
   (`C-46` confirmed, six cases). The **bare** `/SetMaster` self-unjoin answered
   with a fresh etag reflecting the change (`C-55`). So a client can trust the
   bare form's response and must re-read after `?master=`. These were one claim
   and resolved as MIXED, which hid a clean split; they are now two.
6. **Respect the length constraint** on `slaveChannelModes` and
   `slaveDistances`: both must have exactly as many comma-separated entries as
   `slaves`.
