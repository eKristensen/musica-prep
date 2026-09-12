# Musica — a hosted web-based BluOS controller

This is a personal project that aims to solve problems I have run into while
using Bluesound music players. It is not meant to replace the official app, or
any of the alternatives to it.

---

## Why

**1. Unreliable player visibility on Android.** The official Android app loses
players, shows them inconsistently, and generally makes it hard to control the
ones I own. I assumed this was normal until I ran the same app under Waydroid
and saw it behave. Later I tried the official iOS app, which worked fine. I
believe it is a solvable problem that has, for whatever reason, not been solved
on Android.

**2. No Linux desktop client.** The official desktop app is Electron, which
makes the absence of a Linux build hard to explain. A community project
repackages the Windows build as an AppImage and it does work, but it carries
over some of the same discovery problems, and running the Windows app under
Wine is not an acceptable solution for me.

**3. Slow Tidal browsing.** Opening My Music → Songs means waiting several
seconds, every time, for a list that has not changed.

I tried the alternatives first. None of them worked for me — see
[MOTIVATION.md](MOTIVATION.md).

---

## Design philosophy

**Platform independence.** I do not like when someone else decides which
platform you should use by not offering an equal experience and featureset
for all platforms. The applications I have that get closest to platform
independence in my experiences is web apps, so this is a web app. It runs on
anything with a browser, and installs like a native app where Progressive Web
Apps are supported.

**One user interface.** One interface for desktop and phone, rather than one
per platform. A web app collapses that into a single codebase that behaves the
same everywhere.

**Built to last.** Rust on the backend and TypeScript in the frontend, to get
as much feedback from the compiler as possible. Dependencies are chosen
carefully and added only when implementing the thing directly would make little
sense. The hope is to avoid death by dependency.

The design principles are described in depth in
[DESIGN_PRINCIPLES.md](DESIGN_PRINCIPLES.md).

---

## How it works

A small server runs on a machine that is always on. It holds permanent
connections to each player and keeps a complete, current picture of them. The
browser connects to that server and nothing else.

```
   players  ──HTTP/XML long-poll──▶  server  ──SSE──▶  browser
   (fixed IPs from config)         (holds state)     (phone / laptop)
```

That single design choice is what fixes problem 1. Loading a page from a server
that already holds the state is faster and more reliable than rediscovering
players and resynchronising on every launch. Delivering it as a web app is what
answers problem 2.

It hides problem 3 as well: because the server is always running, it can
pre-cache Tidal lists and hand them over instantly, though Search speed will
remain unchanged.

---

## Features

**Nothing here is built yet.** This is the intended scope, not a change log.
The repository currently holds the plan to start the work.

Feature completeness is not the goal. The list is based on selected features of
the Bluesound NODE N110, N130 and N132.

- List configured players, always visible, online or offline
- Play, pause, stop, skip, seek
- Volume per player and per group, with mute
- Now playing, with artwork
- Grouping — create named groups, group all, per-slave volume
- Sleep timer
- Presets
- Play queue
- Browsing and search for Tidal, Radio Paradise and local media
- Tidal lists pre-cached, sortable, and searchable within a single list
- Dirac Live preset, subwoofer, crossover and the rest of the audio settings

The BluOS API is the same across Bluesound players, so most other BluOS-based
players will most likely work even though they are not listed above. Which
features are available will vary with the hardware.

The targets during development is Firefox on Linux and Android as a PWA. Other
browsers are not a goal, and nothing is deliberately done to break them either.

### Deliberately absent

Soundbars. Home theatre and zone configuration. Rechargeable and battery
players. Anything specific to custom-install or professional hardware. Player
setup and Wi-Fi provisioning. Automatic discovery. Move playback. Firmware
upgrade triggering. Authentication — the server belongs on a network you trust.

Keep the official app installed for those.

---

## Configuration

```yaml
players:
  - { ip: 10.20.30.11, port: 11000 }
  - { ip: 10.20.30.12 }

listen: "0.0.0.0:8080"
```

IP addresses only. Names, models and capabilities come from the players
themselves. Port is optional and defaults to 11000. See
[config.example.yaml](config.example.yaml) for the remaining settings.

---

## Building

You will need a Rust toolchain and Node.

```sh
make          # build everything
make run      # run against the players in config.yaml
make mock     # run against the mock player, no hardware needed
make test
```

The result is one binary with the frontend embedded.

---

## Design notes

The reasoning behind the significant choices lives in
[DESIGN_PRINCIPLES.md](DESIGN_PRINCIPLES.md). It is worth reading before
changing anything structural — each decision records what was chosen, why, and
the specific signal that would justify revisiting it.

Two that shape everything else:

- **The app never acts on its own.** It does what you ask, and it keeps its
  picture of the players current. It does not tidy up, correct configurations
  it disapproves of, or act because it noticed it could. The one exception is
  pre-caching Tidal lists, which is read-only.
- **It is meant to be boring.** Written once, built, and left with minimal
  maintenance.

---

## Status and expectations

Planning stage. No code yet.

MIT licensed — see [LICENSE](LICENSE). There is no intention to replace any
commercial product or to make money from this.

It is built for my hardware and my habits. It may well not suit yours.

---

## Regarding the BluOS API

This project is built against the
[BluOS Custom Integration API v1.7](https://content-bluesound-com.s3.amazonaws.com/uploads/BluOS-Custom-Integration-API_v1.7.pdf).

The players I own support calls that document does not cover, and this project
uses some of them.

---

## Acknowledgements

This project is not affiliated with, endorsed by or supported by any hardware
or service vendor. All product names, logos and trademarks mentioned here
belong to their respective owners and are used descriptively. Support for any
given device or feature is partial at best.
