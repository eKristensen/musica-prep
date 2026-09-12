# What the controllers' own code says about the measurements

Explanations for the numbers in
[`controller-discovery-timings.md`](controller-discovery-timings.md), read out
of the shipping apps. Two sources:

| build | how it was read |
|---|---|
| **Android 4.16.2** | `com.lenbrook.sovi.bluesound`, APK from APKPure. Reconstructed from Dalvik bytecode — names survive R8 shrinking and the control flow below is simple enough to read directly |
| **Windows 4.16.1** | Electron app. Its main process ships **original TypeScript** in adjacent source maps, so this is real source, not decompilation |

This file explains measurements; it does not add any. **[V official]** is
`bluos-http-api.md`'s marker for something read out of a first-party Controller
build, and its legend already names this exact APK.

## Does the read build match the measured ones? **[V official]**

The Android source read here is **4.16.2 build 3217**, which is exactly what the
Mi 9 ran. The Fairphone and Waydroid ran **4.16.3 build 3224**, so that build
was compared against it directly, class by class:

- **`com.lenbrook.sovi.discovery` is byte-identical between the two.** All 174
  methods hash the same, instruction for instruction. Every constant quoted
  below — the two-second `delaySubscription`, the retry schedule, the staleness
  and refresh timeouts — is the same code on every Android device measured.
- The three changed methods in `PlayerDiscoveryFragment` change only a string
  resource id, each by exactly +1, because a string was added elsewhere in the
  table. The text on the discovery screen moved; nothing it does moved.

What 4.16.3 actually changes is one feature, tagged `GL #1071` in its own log
strings: the **deprecation notice** for players losing support. It gains a
`DeprecationNoticeThrottle` that suppresses the notice for 24 hours per player
in `SharedPreferences`, a "select another player" button that opens the player
list with a new `close_on_select` extra so the list closes once a player is
picked, and a retry path for when the post-upgrade check times out. The rest of
the diff is the version string in the `User-Agent`, regenerated data-binding
classes, and resource-id renumbering behind them.

So the build gap between this file and the measurements does not exist for
anything this file claims.

---

# Android

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
multicast after the lock is taken. Whatever the reason, it is a flat two seconds
on every discovery **that takes the lock** — and **none at all** on one that does
not. There is no middle setting and no shortening of it: the branch either runs
or it does not, which is why the measured times fall into two groups rather than
onto a spread.

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

## What makes the list appear instantly, and then not **[V official]**

`PlayerDiscoveryState` is a **process-wide singleton** (`INSTANCE`, `LOCK`,
`getInstance()`) whose `allPlayers` is a plain in-memory `Map`. It outlives any
fragment, any screen and any discovery subscription, and it dies with the
process — or when something calls `reset()`, which `MainActivity.onNoPlayersFound`,
`PlayerDiscoveryManager.lambda$init$0` and, less obviously,
`analytics.DeviceLogger.start` all do: the telemetry component runs its own
discovery to inventory the user's players and resets the shared state to do it.

**Nothing persists the list.** The only player written to storage is the
selected one: `PlayerManager.persistAndBroadcastSelectedMaster` puts a single
string into `SharedPreferences`, and `PlayerManager.init` reads it back through
`createMasterHostFromPreferences`. That one player therefore survives a real
process death; the other three cannot.

Two of its methods explain the whole cycle:

```java
boolean isStale(PlayerInfo p) {
    return currentTimestamp() - p.getLastSeen() > 16000;
}

void markAllPlayersAsSeen() {                    // logs "Marking all players as seen"
    for (PlayerInfo p : allPlayers.values())
        p.setLastSeen(currentTimestamp());
}
```

And `PlayersFragment.startDiscovery()` — which runs when the player screen is
opened — calls `setKeepStalePlayers(false)` and then `markAllPlayersAsSeen()`
before it subscribes to anything.

**So while the list still exists, it is not a cache being consulted — it is the
live list being told it was just seen.** Every player's `lastSeen` is stamped to
*now*, nothing qualifies as stale, and the list renders from memory with no
network involved, so the players shown need not still exist. The stamp is
applied without checking anything.

The decay follows from the same two numbers. After that stamp nothing refreshes
`lastSeen` unless an announce actually arrives; at 16 s every player qualifies
as stale; the 30 s check runs `removeStalePlayers()`, which really does delete
them — `iterator.remove()` on `allPlayers`, plus `selectablePlayers.remove(p)`
— and 20 s after that the "no players found" runnable fires, whereupon
`MainActivity.onNoPlayersFound()` calls `reset()` and clears what is left.

## So how does a tap bring them back? **[V official]**

Not from the player list, which by then is genuinely empty —
`markAllPlayersAsSeen()` would have nothing to iterate over. **The app keeps a
second registry, and the staleness sweep never touches it.**

`PlayerDiscoveryManager.mKnownHosts` is a `Set<Host>` — addresses only, no
player data. Every `SyncStatus` the app ever receives adds its host to it. And
`createObservable()`, which is what a fragment subscribes to when it starts
discovery, is built like this:

```java
Observable.defer(this::replayCachedSyncStatuses)   // empty: cleared on the last dispose
    .doOnNext(s -> { mKnownHosts.add(s.getHost());
                     cachedSyncStatuses.put(s.getHost(), s); })
    .doOnDispose(() -> cachedSyncStatuses.clear())
    .share()
    .startWith(Observable.defer(() -> {            // ← runs FIRST, on every subscribe
        List<Observable<SyncStatus>> probes = new ArrayList<>(mKnownHosts.size());
        synchronized (mKnownHosts) {
            for (Host h : mKnownHosts)
                probes.add(getSingleSyncStatus(h)   // PlayerManager.createForHost(h)
                              .onErrorResumeNext(   //   .syncStatus().take(1)
                                  t -> { mKnownHosts.remove(h); return Observable.empty(); }));
        }
        return Observable.merge(probes);
    }));
```

**The refill is a unicast HTTP request to each remembered address, in parallel,
before any discovery runs at all.** Four `/SyncStatus` requests to four live
players on a LAN come back in well under a second, each one going through
`PlayerDiscoveryState.update(SyncStatus)`, which is what rebuilds the list. No
broadcast is involved, which is exactly why switching every discovery mechanism
off changes nothing about it.

`mKnownHosts` is cleared in only two circumstances: the whole set goes when the
network changes (`lambda$init$0`, logged as *"Network changed to [%s]. Clearing
cache of previously discovered players"*, which also calls `reset()`), and a
single host is dropped when its own request fails. Nothing ages it out.

### Why the two behave differently

This is the inconsistency, and it is not an accident of timing — the two
registries answer different questions and expire on different evidence:

| | `PlayerDiscoveryState.allPlayers` | `PlayerDiscoveryManager.mKnownHosts` |
|---|---|---|
| holds | the full player records the UI renders | addresses, nothing else |
| refreshed by | an LSDP or mDNS sighting stamping `lastSeen` | any `SyncStatus` reply |
| expires after | 16 s without a sighting, swept at 30 s | never on a timer |
| cleared by | the sweep, or `reset()` | a network change, or that host failing |

So **"No Player Found" means "nothing has announced itself lately", not "nothing
is reachable"** — and the app can disprove its own message in under a second,
using addresses it never forgot, the moment someone asks it to look.

Both refill paths exist and cover different starting states: if the sweep has
not run yet and the process still holds the list, `markAllPlayersAsSeen()` makes
it appear instantly with no network at all; if the sweep has emptied it, the
known-host probes rebuild it from live replies.

### Why it is intermittent, and why a swipe is not a guarantee

Since the list is only in memory and only the selected master is persisted, an
instant *full* list after swiping the app away means one thing: **the process
did not actually die.** Removing a task from Recents usually kills the process,
but Android does not promise it, and this app ships several services that give
the system a reason to keep it: `BluOSControllerService` (media control),
three widget services, and Firebase's `SessionLifecycleService`. A media session
or a placed widget is exactly the kind of thing that keeps a process resident
after its task is gone.

So the two behaviours are one code path with different starting state:

| after a swipe | `allPlayers` | what the screen does |
|---|---|---|
| process really died | empty — `markAllPlayersAsSeen()` marks nothing | "Discovering…", then whatever discovery finds |
| process survived | still populated | the whole list, instantly, then the 16/30/20 s decay |

Which of those happens is the system's call, not the app's, and that is why the
behaviour was hard to provoke on demand. **Confirming it takes one look**:
`adb shell ps | grep sovi` after the swipe, or the running-services list in
Developer Options — if the process is still there, the instant list is expected
**[U]**; this has not been checked against an actual sighting.

The one thing it is *not* is a network problem. The app spends the entire cycle
able to reach the players it is about to declare missing.

## Corrections to earlier guesses

**The multicast lock is acquired.** An earlier hypothesis in this work, since
removed, was that the Wi-Fi penalty might come from the app *not* holding a
`WifiManager.MulticastLock`, since Android filters non-directed packets without
one. That is wrong: the app declares `CHANGE_WIFI_MULTICAST_STATE` in its
manifest, creates a lock named `"PlayerDiscoveryManager"`, acquires it on
subscribe and releases it on dispose.

The hypothesis pointed at the right code and drew the wrong conclusion from it.
The cost is not a missing lock; it is the two-second delay wrapped around
taking one.

**The instant list is not unicast HTTP to cached addresses.** An earlier guess
in the measurement log was that a tap might be re-probing known addresses over
HTTP. It is simpler and stranger than that: the list is already in memory and
gets its timestamps reset.

**"App or platform?" is answered, for the Wi-Fi penalty.** It is the app: a
hard-coded delay in the app's own discovery composition, conditional on the
app's own reading of the Wi-Fi radio state. No Bonjour-browser differential test
is needed for that part.

---

## What the Android code does not explain

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

# Windows

Source, not decompilation: the Electron main process ships its original
TypeScript in source maps. Three discovery modules live in
`app-main/src/modules/`.

## `staticPlayers.txt` never replaced discovery **[V official]**

`staticPlayersDiscovery.ts` is a **peer of the other two discovery modules**,
not a substitute for either. `index.ts` builds all three and starts them
together:

```ts
const bonjourDiscovery = new BonjourDiscovery();
const lsdpDiscovery = new LsdpDiscovery();
const staticPlayersDiscovery = new StaticPlayersDiscovery();

const restartDiscovery = () => {
  lsdpDiscovery.disable(); lsdpDiscovery.enable();
  bonjourDiscovery.enable({ ... });
  staticPlayersDiscovery.enable();
};
```

And the module itself does nothing but read a file and push its contents at the
renderer — **after its own three-second timer**:

```ts
enable(): void {
  this.#discoveryTimeout = setTimeout(() => {
    if (fs.existsSync(staticPlayersFile)) {
      ... readStaticPlayers(window)       // window.webContents.send("foundStaticPlayers", players)
    } else {
      fs.writeFile(staticPlayersFile, "", () => {});
    }
  }, 3000);
}
```

Three things follow, and together they settle the measurement:

- **It adds players; it never stops discovery.** LSDP and Bonjour run exactly as
  they would without the file. The reading that the static list is "used
  directly, with no discovery" describes the vendor's intent for the feature,
  not the code.
- **It cannot make startup faster, by construction.** Its players are delivered
  on a 3-second timer, which is *slower* than a working discovery round. Nothing
  it does is on the critical path to a player appearing sooner.
- **It creates an empty `staticPlayers.txt` when none exists**, which is why the
  file turns up on machines that never used the feature.

## The same LSDP schedule, written out **[V official]**

`lsdpDiscovery.ts`:

```ts
const msg = Buffer.from([6, 76, 83, 68, 80, 1, 5, 81, 1, 255, 255]);
const delays = [0, 1, 2, 3, 5, 7, 10];
for (let d = 0; d < delays.length; d++) {
  this.#queryTimeouts[d] = setTimeout(..., delays[d] * 1000 + Math.random() * 250);
}
```

The buffer is `06 4C 53 44 50 01 05 51 01 FF FF` — §12.1's eleven-byte query,
byte for byte — and the schedule is the same 0,1,2,3,5,7,10 s with up to 250 ms
of jitter that the Android app builds out of its `DELAYS` array. Two independent
clients, one schedule.

`RESTART_DEBOUNCE_MS = 3000` debounces the "Search Again" button, with a comment
saying each restart tears down and rebinds the socket.

`bonjourDiscovery.ts` has `setInterval(resetBonjour, 10000)` — the ten-second
rebuild of the whole mDNS browser that §12.2 describes, confirmed here.

## What the Windows code does not explain

**The 5–6 s from launch.** There is no equivalent of Android's two-second
delay: LSDP queries start at `delays[0] = 0`. So the desktop's wait is not
inside discovery, which is what the measurement already said. What is left is
Electron and Vue starting up before the modules run and the UI paints, and that
is not something this source can be read off — it would have to be timed.

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

For Windows no tooling is needed: the source maps carry the original
TypeScript, and `app-main/src/modules/` holds the three discovery modules
directly.

The Android classes worth reading are `com.lenbrook.sovi.discovery.PlayerDiscoveryManager`
(and its `$LSDPProbeRetry`), `LSDPPlayerDiscoveryOnSubscribe`,
`JmDNSPlayerDiscoveryOnSubscribe`, `PlayerDiscoveryState`, and
`com.lenbrook.sovi.bluos4.ui.players.PlayersFragment`. The app logs its own
discovery steps through Timber with a `"Discovery P1: …"` prefix, so `adb
logcat` on a debug-visible build would show the same sequence live.
