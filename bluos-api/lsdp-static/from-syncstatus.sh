#!/bin/sh
# Build an lsdp-static config by asking each player over HTTP -- useful exactly
# when discovery is the thing that is broken, since /SyncStatus needs only the
# address.  Usage:  ./from-syncstatus.sh 192.168.10.10 192.168.10.11 > players.conf
set -u
[ $# -gt 0 ] || { echo "usage: $0 <player-ip> [player-ip ...]" >&2; exit 2; }
for ip in "$@"; do
    xml=$(curl -fsS --max-time 5 "http://$ip:11000/SyncStatus" 2>/dev/null) || {
        echo "# $ip: no answer on port 11000" >&2; continue; }
    attr() { printf '%s' "$xml" | grep -o "$1=\"[^\"]*\"" | head -1 | cut -d'"' -f2; }
    mac=$(attr mac); name=$(attr name); model=$(attr model)
    version=$(attr version); class=$(attr class)
    [ -n "$mac" ] || { echo "# $ip: /SyncStatus carried no mac attribute" >&2; continue; }
    # a 12-character mac with no colons is the documented shorthand form
    case "$mac" in *:*) ;; *) mac=$(echo "$mac" | sed 's/../&:/g; s/:$//');; esac
    case "$class" in hub) cls=0x0008;; *) cls=0x0001;; esac
    echo "# $name ($model)"
    echo "node $mac $ip"
    printf '  service %s name="%s" port=11000' "$cls" "$name"
    [ -n "$model" ] && printf ' model=%s' "$model"
    [ -n "$version" ] && printf ' version=%s' "$version"
    echo; echo
done
