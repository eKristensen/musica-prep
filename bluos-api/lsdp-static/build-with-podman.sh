#!/bin/sh
# Build lsdp-static without installing cargo: compile it in a container and copy
# the binary out.  Rootless podman is fine -- nothing here needs root, and the
# extracted binary ends up owned by you.
#
#   ./build-with-podman.sh              # podman
#   ENGINE=docker ./build-with-podman.sh
set -eu
cd "$(dirname "$0")"
ENGINE=${ENGINE:-podman}
IMAGE=${IMAGE:-localhost/lsdp-static:built}

command -v "$ENGINE" >/dev/null 2>&1 || {
    echo "$ENGINE not found -- set ENGINE=docker, or install podman" >&2; exit 1; }

"$ENGINE" build -t "$IMAGE" -f Containerfile .

# `create` does not run anything; it just gives the image a filesystem to copy from.
cid=$("$ENGINE" create "$IMAGE")
trap '"$ENGINE" rm -f "$cid" >/dev/null 2>&1 || true' EXIT
"$ENGINE" cp "$cid:/lsdp-static" ./lsdp-static
chmod +x ./lsdp-static

echo
./lsdp-static selftest
echo
echo "built: $(pwd)/lsdp-static"
echo "install it with: sudo install -m755 $(pwd)/lsdp-static /usr/local/sbin/"
