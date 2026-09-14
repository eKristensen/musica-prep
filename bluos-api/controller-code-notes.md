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

**Run ids** are used throughout without re-describing the run: `R1`–`R9` are the
phone, Waydroid and iPhone runs and `D1`–`D3` the desktop ones, all in the Runs
table of
[`controller-discovery-timings.md`](controller-discovery-timings.md). (`R8`
inside a sentence about bytecode is the Android shrinker, not run 8.)

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

So on Android there is no build gap between this file and the measurements.

There is none on the desktop either. The source read here is Windows
**4.16.1**, and the Windows runs D1 and D3 were measured on **4.16.1 build
6281** — the same build. D2 ran the Linux AppImage, **4.16.0 build 5930**, whose
source was recovered the same way and compared:

- **`app-main/src` is byte-identical between the two.** That includes all three
  discovery modules — `lsdpDiscovery.ts`, `bonjourDiscovery.ts` and
  `staticPlayersDiscovery.ts` — which are the whole basis of the Windows half of
  this file.
- One file differs in the entire recovered tree: `SettingItem.vue` in the shared
  `@lenbrook/vue-settings` package, where 4.16.1 lets a readonly text setting
  render without a POST url. A settings-UI fix, nothing to do with discovery.

So the repackaging really did leave the app code alone, and everything below
about the desktop describes both builds. It remains a code-level comparison
only: it says nothing about what the unofficial packaging may add around the app
— launch scripts, bundled native binaries — which has not been examined **[U]**.

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

The lock itself is real and correctly taken: the app declares
`CHANGE_WIFI_MULTICAST_STATE` in its manifest, creates a lock named
`"PlayerDiscoveryManager"`, acquires it on subscribe and releases it on dispose.
Android filters non-directed packets without one, so this is the right thing to
do — **the cost is not a missing lock, it is the two seconds wrapped around
taking one.**

Presumably the delay exists to let the Wi-Fi driver actually start delivering
multicast after the lock is taken. Whatever the reason, it is a flat two seconds
on every discovery **that takes the lock** — and **none at all** on one that does
not. There is no middle setting and no shortening of it: the branch either runs
or it does not, which is why the measured times fall into two groups rather than
onto a spread.

### mDNS waits too — the delay is upstream of both protocols

The two seconds are not an LSDP problem. `multicastLock` is applied to the
**merged** discovery observable, with both protocols already inside it:

```java
Observable createPlayerDiscoveryObservable(Context ctx) {
    return multicastLock(ctx,                                   // <-- the 2 s sits here
        Observable.defer(() -> Observable.fromIterable(getNetworkAddressesForDiscovery()))
            .flatMap(addr -> Observable.merge(
                logAndResumeOnError("Error during LSDP discovery",
                    createLSDPPlayerDiscoveryObservable(addr)).unsubscribeOn(IO),
                logAndResumeOnError("Error during mDNS discovery",
                    JmDNSPlayerDiscoveryOnSubscribe.createObservable(addr)).unsubscribeOn(IO))));
}
```

`delaySubscription` delays the subscription to that merge, so neither branch
starts. The app's mDNS path is JmDNS rather than Android's own `NsdManager`, and
it pays the same two seconds LSDP does — as does the interface enumeration,
which is deferred inside. **Nothing about the discovery protocol changes the
wait**, which is why a faster responder could not have helped and why switching
to mDNS would not either.

### The floor underneath it is not a timer at all **[V official]**

With the two seconds gone, about a second remains. **There is no fixed
contribution to it from LSDP.** The second is made of two things that each take
as long as they take:

| | what it is | roughly |
|---|---|---|
| waiting for the **last** player's announce | the protocol's own random 0–750 ms reply delay (§12.1), and the list is not complete until the slowest of four has answered | measured on the wire at **448–749 ms** to hear all four |
| then, per player, an **HTTP chain** before its row is drawn | two to three requests, serialized | the remainder, a few hundred ms |

Measured end to end that is 1.0–1.5 s, and the two parts above are the whole of
it. Neither is a wait the app chose; both are work finishing.

**The 1000 ms in the receive loop is not part of it**, which is the easy mistake
to make. It is the only second-scale constant in
`com.lenbrook.sovi.discovery` besides 16 s (staleness) and 60 s (in
`PlayerDiscoveryState.update`), and it is a ceiling on how long `receive()`
blocks, so the loop can re-check `isDisposed()` about once a second:

```java
socket.setSoTimeout(1000);
while (!emitter.isDisposed()) {
    socket.receive(packet);            // returns the instant a datagram arrives
    parseResponse(packet, emitter);    // emitted immediately, not on a tick
}
```

An announce that arrives 30 ms in is parsed 30 ms in. The timeout only matters
when *nothing* arrives. **Nothing gates a player on a one-second boundary.**

The second part, between an announce and its row appearing, is a chain of HTTP
requests per player, serialized by `flatMap`:

```java
PlayerDiscoveryManager.getInstance().discoverPlayers()   // announce -> /SyncStatus
    .flatMap(fetchSchemaVersion())                       // -> /schemaVersion, sometimes
    .flatMap(fetchPresetSetting())                       // -> the preset/dynamic-settings url
    .retryWhen(...)
    .subscribe(pair -> updatePlayerInfo(pair.first, pair.second));   // <- the row is drawn here
```

`fetchSchemaVersion` short-circuits with `Observable.just` when the `SyncStatus`
already carries a version or a cached `PlayerInfo` has one, and otherwise asks
the player. `fetchPresetSetting` asks whenever the `SyncStatus` names an
`audioPresetUrl` or a `dynamicSettingsUrl`. Only when both have resolved does
`updatePlayerInfo` draw the row.

**This is why answering discovery instantly did not move the number.** A static
responder removes the 0–750 ms reply delay — the first row of the budget — and
leaves the HTTP chain untouched. It shortens the part that was already the
smaller of the two, in a test where the phone still had to do everything below.

The split between the two rows is approximate: the 448–749 ms comes from
`lsdp-static measure` on a wired host, not from the phone, so it bounds the
protocol part rather than measuring it inside the app. What the HTTP chain
actually costs has not been measured directly **[U]**.

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
| Android, cable, **Wi-Fi explicitly disabled** (R6) | off | no | **1.0–1.5 s** |
| Waydroid, bridged, no Wi-Fi (R7) | none | no | **1.0–1.5 s** |
| Waydroid + instant static responder (R8) | none | no | 1.0–1.5 s, unchanged |
| iPhone (R9) | on | not applicable, not Android | instant |

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

## The list that empties itself, and comes back **[V official]**

The behaviour explained in this section and its parts is the cycle timed in
[`controller-discovery-timings.md`](controller-discovery-timings.md): with the
app open and untouched, the player list goes empty after ~30 s, settles on **"No
Player Found"** at ~50 s, and comes back in full within a second of a tap. It
was provoked with the phone on a different VLAN from the players and both relays
that would carry discovery across the boundary switched off, so **no announce
could reach the app for the whole cycle** — and the selected player stayed
controllable throughout it.

It takes three separate pieces of the app to account for that: what deletes the
players, what can put them back on screen without a network at all, and what
puts them back once they have actually been deleted. They are different
mechanisms and the third is not the second.

### Why it empties

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

### Why it can appear instantly, and then decay

This is the 0 s row of that table — tap Players, all four are there at once —
and the decay that follows it.

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

### Why a tap refills it once it really is empty

This is the last row — tap Players after "No Player Found", all four back within
a second. It is not the mechanism above.

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

### Why the two registries behave differently

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

## What the Android code does not explain

- **The remaining 1.0–1.5 s** when the delay is skipped, as a *duration*. The
  shape of it is now readable (below); what it costs in milliseconds is not,
  because that depends on how fast the players answer HTTP.
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

### The renderer treats it as one more discovery source

`foundStaticPlayers` is one of the channels the preload script exposes, beside
`lsdpAnnounce`, `deviceDiscovered` (Bonjour) and `deviceLost`. All of them land
in the same Vuex `devices` store, by the same route — fetch the device's
version, fetch its `/SyncStatus`, and let the UI render whatever the store now
holds. Reconstructed from the renderer bundle, which is minified, so the names
are mine but the structure and the string constants are not:

```js
// the discovery sources
ipc.on("deviceDiscovered",  d  => addDevice(d.id, d.version));   // Bonjour
ipc.on("lsdpAnnounce",      d  => addDevice(d.id, d.version));   // LSDP
ipc.on("pastDiscoveredDevicesFound", ids => ids.forEach(addDevice));

// the static list — same destination, two differences
ipc.on("foundStaticPlayers", list => {
  list.filter(s => isValidIp(s.split(":")[0]))
      .map(s => DeviceId.fromString(s))
      .forEach(id => {
        if (store.getters["devices/hasDeviceByDeviceId"](id)) return;   // (1)
        getVersion(id)                                                  // (2)
          .then(v  => store.dispatch("devices/setVersion", { deviceId: id, version: v }))
          .then(() => store.dispatch("devices/retrieveDeviceSyncStatus", { deviceId: id }));
      });
});
```

**(1)** is the guard that settles the measurement outright: a listed player that
discovery has already found is **skipped**. The list cannot replace discovery's
results because it explicitly defers to them.

**(2)** is why a listed player is the *slowest* kind to appear. A device is only
displayable once its `/SyncStatus` comes back, and an LSDP announce carries the
version with it, so a discovered player costs one HTTP round trip. A file entry
carries nothing but an address, so it costs a `/GitVersion` **and then** a
`/SyncStatus`, chained rather than parallel — after the three-second timer has
elapsed.

### So the file cannot speed anything up

- **It adds players; it never stops discovery.** LSDP and Bonjour run exactly as
  they would without the file. "Used directly, with no discovery" describes the
  vendor's intent for the feature, not the code.
- **It is last by construction**, on every axis: a 3 s timer before it starts, a
  serialized pair of HTTP requests after, and a guard that yields to anything
  discovery already found.
- **It creates an empty `staticPlayers.txt` when none exists**, which is why the
  file turns up on machines that never used the feature.

### What this does *not* explain

The 5–6 s the desktop takes from launch. The file is not on that path, and
neither is waiting for discovery answers: D3 measured the same 5–6 s with every
discovery mechanism switched off, so there were no answers to wait for. What
is left is the app's own startup: Electron and Vue booting, the modules being
constructed and enabled, and then at least one `/SyncStatus` round trip before
any player can be drawn. None of that can be read off as a duration from this
source; it would have to be timed, and has not been **[U]**.

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

## There is no Wi-Fi gate on the desktop **[V official]**

Nothing in the desktop source branches on link type. `lsdpDiscovery.ts`
enumerates every interface from `networkInterfaces()`, broadcasts the query to
each, and sends the first at `delays[0] = 0` — no `isWifiEnabled()` equivalent,
no multicast lock, no conditional wait. The single mention of Wi-Fi in the whole
recovered tree is a comment in `networkChangeMonitor.ts` explaining why it
watches for interfaces changing under a running app.

So the Android finding does not carry over, and there is no reason to expect the
desktop to start faster with Wi-Fi switched off. Its 5–6 s is the same on any
link.

## What the Windows code does not explain

**The 5–6 s from launch.** There is no equivalent of Android's two-second
delay: LSDP queries start at `delays[0] = 0`. So the desktop's wait is not
inside discovery, which is what the measurement already said. What is left is
Electron and Vue starting up before the modules run and the UI paints, and that
is not something this source can be read off — it would have to be timed.

## Reproducing this

### Android

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

### Windows

The code is four containers deep, each a different format:

```
BluOS Controller 4.16.1 Windows.exe      NSIS installer
 └─ $PLUGINSDIR/app-64.7z                nested 7-Zip archive
     └─ resources/app.asar               Electron's packed source archive
         └─ node_modules/@app/
             ├─ main/dist/index.js         Electron main process, the Node side
             ├─ preload/dist/exposed.mjs   preload / contextBridge script
             └─ renderer/dist/             the Vue 3 UI, production build
         └─ node_modules/@lenbrook/vue-settings/   their shared settings-UI package
```

Needs `7z` (`apt install p7zip-full`) and `@electron/asar`:

```sh
7z x "BluOS Controller 4.16.1 Windows.exe" -oextracted
7z x 'extracted/$PLUGINSDIR/app-64.7z' -oapp
npx @electron/asar extract app/resources/app.asar asar_out
```

`asar_out/node_modules/@app/` is then the application.

**Recovering the original TypeScript.** `@app/main/dist/index.js` ends with a
`//# sourceMappingURL=data:application/json;charset=utf-8;base64,…` line. Decode
it and the map's `sourcesContent` holds the unminified sources, named by
`sources`:

```python
import re, base64, json
content = open("asar_out/node_modules/@app/main/dist/index.js", encoding="utf-8").read()
b64 = re.search(r"base64,([A-Za-z0-9+/=]+)", content).group(1)
map_data = json.loads(base64.b64decode(b64))
for path, src in zip(map_data["sources"], map_data["sourcesContent"]):
    print(path)          # write `src` to this path to reconstruct the tree
```

`@lenbrook/vue-settings/dist/index.js.map` is a separate `.map` file next to its
bundle and yields to the same trick. That reconstruction is what
`app-main/src/modules/` refers to throughout this file; the three discovery
modules sit there together.

The renderer bundle (`@app/renderer/dist/assets/*.js`) ships **no** source map,
so it stays minified — nothing above is read from it.

### Linux

One container fewer: an AppImage is an ELF binary with a SquashFS filesystem
appended, so there is no NSIS or 7-Zip nesting to get through.

```sh
chmod +x bluos-controller-linux-4_16_0.AppImage
./bluos-controller-linux-4_16_0.AppImage --appimage-extract   # -> ./squashfs-root/
npx @electron/asar extract squashfs-root/resources/app.asar asar_out
```

No install, no root, no FUSE. From `asar_out` the layout and the source-map
trick are identical to Windows: `@app/main/dist/index.js` and
`@app/preload/dist/exposed.mjs` carry embedded maps, and
`@lenbrook/vue-settings/dist/index.js.map` sits beside its bundle.

The Android classes worth reading are `com.lenbrook.sovi.discovery.PlayerDiscoveryManager`
(and its `$LSDPProbeRetry`), `LSDPPlayerDiscoveryOnSubscribe`,
`JmDNSPlayerDiscoveryOnSubscribe`, `PlayerDiscoveryState`, and
`com.lenbrook.sovi.bluos4.ui.players.PlayersFragment`. The app logs its own
discovery steps through Timber with a `"Discovery P1: …"` prefix, so `adb
logcat` on a debug-visible build would show the same sequence live.
