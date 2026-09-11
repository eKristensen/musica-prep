# Canonical response samples

One representative response per endpoint from this run, so the
specification can show the actual bytes rather than send a reader to
a decompiler. Every sample is already redacted; the `fidelity` column
says whether redaction touched it at all.

A sample is **not** a confidence marker and never contradicts one. An
element documented from first-party code but absent here is
conditional, not wrong: it appears when there is content to carry it.
Never delete a documented field because one capture lacks it.

| endpoint | probe | status | bytes | fidelity |
|---|---|---|---|---|
| `/SetMaster` | `005-state_setmaster` | 200 | 534 | 3 edit(s) |

## `/SetMaster`

GET `/SetMaster` — probe `005-state_setmaster`, application/xml, 3 redaction edit(s).

```xml
<?xml version="1.0" ?>
<SyncStatus etag="186" syncStat="186" version="4.16.22" id="192.0.2.11:11000" db="-34" volume="46" name="Stue" model="N132" modelName="NODE" class="streamer" icon="/images/players/N125_sub.png" brand="Bluesound" schemaVersion="34" initialized="true" group="Stue+Kontor" mac="02:00:00:00:00:0B" hasSubwoofer="true">
  <slave id="192.0.2.12" port="11000" name="Kontor" model="N130" icon="/images/players/N125_nt.png"/>
  <pairWithSub/>
  <bluetoothOutput/>
</SyncStatus>
```
