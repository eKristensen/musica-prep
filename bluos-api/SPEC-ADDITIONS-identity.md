# Player identity across network interfaces

A player has two network interfaces, two MAC addresses and two IP addresses,
but only one interface is live at a time — and which one is live changes by
itself, with no action from any controller. Anything that identifies a player
by an address, or by "the MAC", therefore has to say which one it means.

The switching behaviour below is `[V]`: it is documented by the vendor and was
observed directly on this fleet. The `/SyncStatus` question at the end is `[U]`
and carries register rows rather than an answer.

**Provenance caveat.** The vendor pages cited here were read through search
result summaries, not retrieved directly — `support1.bluesound.com` and
`support.bluos.net` were unreachable from the machine this was written on. The
statements agreed across three separate searches and match what the players do,
but the URLs have not been opened and checked. Confirm them before this section
is folded into the specification body.

---

## The hardware behaviour **[V]**

- A player has a wired and a wireless interface, each with its own MAC address.
  Wired-only models (VAULT) have one.
- The two are never live at once. Ethernet wins: connecting a cable disables
  the wireless interface.
- Pulling the cable brings wireless back automatically and it rejoins the
  last-known network.
- Because the MACs differ, the interfaces take different DHCP leases. A
  reservation covers one interface, not the player, so a player that is used
  both ways needs two reservations.
- The Controller app displays the MAC of the interface currently connected, not
  both.

One edge case, reported by users rather than observed here: if the cable is
already plugged in when the wired network *starts* working, the player may not
notice and stays on wireless until the cable is pulled and reinserted.

| statement | source |
|---|---|
| Wireless disabled on cable insert, restored on removal; not usable simultaneously | [Change connection method from LAN to WIFI](https://support1.bluesound.com/hc/en-us/community/posts/360043279234-Change-connection-method-from-LAN-to-WIFI) (community post) |
| Two MAC addresses, one per interface; VAULT wired-only; separate DHCP reservations | [How do I find the MAC Address for my Player?](https://support1.bluesound.com/hc/en-us/articles/201043853-How-do-I-find-the-MAC-Address-for-my-Player) (support article) |
| The app shows the MAC of the connected network card | [How do I know if the Bluesound player is using Ethernet or wireless?](https://support1.bluesound.com/hc/en-us/articles/201056677-How-do-I-know-if-the-Bluesound-player-is-using-Ethernet-or-wireless-network-connection) (support article) |

---

## What this does to each identifier

| identifier | § | survives an interface switch |
|---|---|---|
| LSDP `nodeId` | 12.1 | **Yes.** Six bytes, a MAC, unique per node rather than per interface, and stated there to be the correct cache key. |
| `/SyncStatus` `id` | 2.1 | **No.** It is `ip:port`, and the address belongs to the interface. |
| `/SyncStatus` `mac` | 2.1 | **Unknown.** See below. |
| `<slave id>`, `<master>` text | 2.1 | **No.** Bare IPs, same as `id`. |

So the only identifier that can currently be trusted to survive a cable being
pulled is the LSDP node id. A client that dedupes on `id` — or on whatever
address it reached the player at — sees one player become two the first time
someone moves a player between wired and wireless, and keeps a stale entry it
can never reach again.

A DHCP lease changing on a single interface produces the same symptom by the
same mechanism, and is the more common cause. The interface switch is the case
that cannot be fixed with a reservation, because a reservation only pins one
interface.

---

## The open question: which MAC does `/SyncStatus` report? **[U]**

§2.1 lists the `mac` attribute with an empty Notes cell. Two readings are
possible and they behave differently:

1. `mac` is fixed — the same value whichever interface is live, presumably the
   wired one, matching the sticker and the LSDP node id.
2. `mac` follows the live interface, matching what the Controller app displays.

Reading 2 is the one the app's documented behaviour points at, and it is the
one that hurts: a client keying on `mac` would be keying on a value that
changes under it, with no event announcing the change.

**Test**, on one player that has run both ways:

1. On Ethernet: `GET :11000/SyncStatus`, record `id` and `mac`. Capture an LSDP
   announce for the same player, record `nodeId`.
2. Pull the cable, let it join wireless, repeat both.
3. Compare. Three answers fall out of the one run: whether `mac` changes,
   whether `nodeId` changes, and whether `mac` on either interface equals
   `nodeId`.

Until that is answered, treat `mac` as `[U]` and key nothing on it.

---

## Proposed changes

**§2.1** — the `mac` row, currently `| `mac` | string | |`:

| Attribute | Type | Notes |
|---|---|---|
| `mac` | string | MAC of a network interface. A player has one per interface and only one interface is live at a time, so **which** MAC this is depends on whether the player is currently wired or wireless — untested, `C-56`. Not interchangeable with the LSDP node id until that is settled. |

**§17** — appended:

| id | claim | source | § | verdict | tested against | request → answer | evidence |
|---|---|---|---|---|---|---|---|
| `C-56-syncstatus-mac-interface` | `/SyncStatus` `mac` reports the live interface's MAC, so it changes when a player moves between Ethernet and wireless | vendor support documentation (the app displays the connected card's MAC) | 2.1 | UNTESTED | — | — | — |
| `C-57-lsdp-nodeid-interface-stable` | the LSDP `nodeId` is unchanged by an interface switch | §12.1 | 12.1 | UNTESTED | — | — | — |

Both are settled by the single run above, so they belong to one test rather
than two.
