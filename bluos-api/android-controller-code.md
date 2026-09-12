# What the Android controller's code says about the measurements

Read out of **BluOS Controller for Android 4.16.2** (`com.lenbrook.sovi.bluesound`,
APK from APKPure), against the timings in `controller-discovery-timings.md`.
Everything here is reconstructed from Dalvik bytecode — method and field names
survive R8 shrinking, and the control flow in the methods below is simple enough
to read directly. Reproduction notes are at the end.

This file explains measurements; it does not add any. **[V official]** is
`bluos-http-api.md`'s marker for something read out of a first-party Controller
build, and its legend already names this exact APK.

---

## The headline: discovery waits two seconds when Wi-Fi is on **[V official]**

`com.lenbrook.sovi.discovery.PlayerDiscoveryManager.multicastLock(Context, Observable)`,
reconstructed:

```java
Observable multicastLock(Context ctx, Observable source) {
    WifiManager wm = (WifiManager) ctx.getApplicationContext().getSystemService("wifi");
    if (wm == null || !wm.isWifiEnabled()) {
        return source;                                   // no lock, no delay
    }
    return Observable.using(
        () -> { MulticastLock l = wm.createMulticastLock("PlayerDiscoveryManager");
                l.acquire(); return l; },                // "Discovery P1: Acquiring multicast lock"
        lock  -> source.delaySubscription(2, SECONDS),   // <-- two seconds
        lock  -> lock.release());                        // "Discovery P1: Releasing multicast lock"
}
```

**When the Wi-Fi radio is enabled, the discovery observable is not subscribed to
for two seconds.** Nothing is listening and nothing is sent in that window: the
socket is opened by the subscribe, and the first LSDP query goes out after it.

Presumably the delay exists to let the Wi-Fi driver actually start delivering
multicast after the lock is taken. Whatever the reason, it is a fixed two
seconds on every discovery.

### The gate is `isWifiEnabled()`, not "is Wi-Fi in use"

This is the part that matters for the measurements. The check asks whether the
**radio is switched on**, not which interface carries traffic. A phone with an
Ethernet adapter plugged in and Wi-Fi still enabled pays the two seconds in
full, because as far as this code is concerned Wi-Fi is on.

### It accounts for every timing result so far

| measurement | Wi-Fi radio | delay applies | measured |
|---|---|---|---|
| Android over Wi-Fi | on | **yes** | 3–5 s |
| Android, USB Ethernet, Wi-Fi never switched off (R3, R4) | on | **yes** | 3–5 s, 2.9–3.4 s |
| Android, cable, **Wi-Fi explicitly disabled** (R6) | off | no | **1–1.5 s** |
| Waydroid, bridged, no Wi-Fi (R7) | none | no | **1.0–1.5 s** |
| Waydroid + instant static responder (R8) | none | no | 1.0–1.5 s, unchanged |
| iPhone (R9) | on | n/a — Android code | instant |

Two seconds of dead time, plus a player's own random 0–750 ms reply and
rendering, lands squarely on the 3–5 s that was measured. The wired figure is
what remains when the delay is skipped.

It also explains two results that were puzzling at the time:

- **Plugging in Ethernet changed nothing** unless Wi-Fi was also switched off.
  That looked like the app ignoring the cable. It is simpler than that: the app
  does not care which interface it uses, only whether the radio is on.
- **A static responder answering in microseconds did not help.** The app is not
  listening yet.

---

## The LSDP query schedule, in the app's own code **[V official]**

`PlayerDiscoveryManager$LSDPProbeRetry` holds `DELAYS`, a `long[6]` initialised
by `fill-array-data` to:

```
1000, 1000, 1000, 2000, 2000, 3000   (ms)
```

`lambda$apply$1` computes `Observable.timer(DELAYS[i] + Math.random() * 250.0,
MILLISECONDS, COMPUTATION)`, and `apply` drives it with
`Observable.range(0, DELAYS.length)` through `repeatWhen`, so the prober repeats
after each delay in turn. Cumulatively, queries go out at:

```
0, 1, 2, 3, 5, 7, 10 s   each with up to 250 ms of jitter
```

That is exactly the schedule in `bluos-http-api.md` §12.1, confirmed from the
Android client rather than from a document — including the 250 ms jitter.

**Probing stops after the t = 10 s query.** The range is finite, so once the six
delays are spent the prober completes and nothing further is sent. This matters
for the section below.

Also visible in `LSDPPlayerDiscoveryOnSubscribe`: `LSDP_PORT = 11430`, message
types `QUERY = 81` (`Q`), `ANNOUNCE = 65` (`A`), `DELETE = 68` (`D`), and the
four accepted classes `LSDP_CLASS_MUSC = 1`, `MUSP = 3`, `MUSZ = 6`,
`MUSH = 8` — §12.1's class table, and its claim that controllers accept exactly
those four. **There is no constant for `R` (82)**, which corroborates for this
client the specification's claim that no shipping controller sends the unicast
query form.

---

## Why the list empties itself **[V official]**

Three independent timers, and they do not fit the protocol they are timing.

| constant | value | where |
|---|---|---|
| `PlayerDiscoveryState.PLAYER_STALE_TIMEOUT_MS` | **16 s** | `isStale(PlayerInfo)` |
| `PlayersFragment.REFRESH_PLAYERS_TIMEOUT` | **30 s** | `startStaleCheck()`, as `handler.postDelayed(…, 30000)` |
| `PlayersFragment$onViewCreated$5.onNoPlayersFound()` | **10 s** and **20 s** | two `handler.postDelayed` runnables: a "need help" prompt at 10 s, a "no players found" state at 20 s |

The observed cycle was: at ~30 s the list changes to "Discovering…", at ~50 s it
settles on "No Player Found". **30 s is the stale check; 30 + 20 = 50 s is the
no-players-found runnable.** The measured cycle and the constants agree to the
second.

And the 16-second staleness rule is the interesting one, because **players
announce unprompted every 57 s ± 6 s** (§12.1). A player that is not actively
probed goes stale roughly forty seconds before it would next announce on its
own. Since LSDP probing stops at t = 10 s, nothing is refreshing them in
between. A list that empties itself while the app sits idle is what those two
numbers produce together.

This is consistent with the app still being able to control the selected player
throughout: reachability over HTTP is a different path from whether a discovery
record has aged out.

---

## Corrections to earlier guesses

**The multicast lock is acquired.** An earlier hypothesis in `FINDINGS.md` was
that the Wi-Fi penalty might come from the app *not* holding a
`WifiManager.MulticastLock`, since Android filters non-directed packets without
one. That is wrong: the app declares `CHANGE_WIFI_MULTICAST_STATE` in its
manifest, creates a lock named `"PlayerDiscoveryManager"`, acquires it on
subscribe and releases it on dispose.

The hypothesis pointed at the right code and drew the wrong conclusion from it.
The cost is not a missing lock; it is the two-second delay wrapped around
taking one.

**"App or platform?" is answered, for the Wi-Fi penalty.** It is the app: a
hard-coded delay in the app's own discovery composition, conditional on the
app's own reading of the Wi-Fi radio state. No Bonjour-browser differential test
is needed for that part.

---

## What this does not explain

- **The remaining 1.0–1.5 s** when the delay is skipped. R8 already showed it is
  not the network; nothing found here accounts for it either. Candidates not yet
  read: the socket receive loop in `LSDPPlayerDiscoveryOnSubscribe.subscribe`
  (which sets `setReuseAddress`, `setBroadcast` and a `setSoTimeout` whose value
  was not extracted), the `/SyncStatus` round trip each discovered player needs
  before it is usable, and list rendering.
- **The desktop's 5–6 s.** Different codebase; the Windows build was not
  available for this pass.
- **Whether the 2 s delay is also on the mDNS path.** `multicastLock` wraps a
  composed observable; which discovery sources are inside it was not traced.
  `JmDNSPlayerDiscoveryOnSubscribe` exists alongside the LSDP one.
- **`PlayerDiscoveryState.update` has a 60 s constant** that was not chased down.

---

## Reproducing this

```sh
python3 -m venv /tmp/agv && /tmp/agv/bin/pip install androguard
```

Then, for any class of interest:

```python
from androguard.core.apk import APK
from androguard.core.dex import DEX
apk = APK("BluOSController_4.16.2.apk")
for dex in [DEX(d) for d in apk.get_all_dex()]:
    for c in dex.get_classes():
        if "discovery/PlayerDiscoveryManager" not in c.get_name():
            continue
        for m in c.get_methods():
            print(m.get_name(), m.get_descriptor())
            for i in m.get_instructions():
                print("   ", i.get_name(), i.get_output())
```

The classes worth reading are `com.lenbrook.sovi.discovery.PlayerDiscoveryManager`
(and its `$LSDPProbeRetry`), `LSDPPlayerDiscoveryOnSubscribe`,
`JmDNSPlayerDiscoveryOnSubscribe`, `PlayerDiscoveryState`, and
`com.lenbrook.sovi.bluos4.ui.players.PlayersFragment`. The app logs its own
discovery steps through Timber with a `"Discovery P1: …"` prefix, so `adb
logcat` on a debug-visible build would show the same sequence live.
