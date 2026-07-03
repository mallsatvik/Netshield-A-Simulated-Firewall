#!/usr/bin/env bash
set -euo pipefail

SET_NAME="cnn_blocklist"

if [ $# -lt 1 ]; then
  echo "Usage: $0 <IPv4> [ttl_seconds]" >&2
  exit 2
fi

IP="$1"
TTL="${2:-3600}"

sudo ipset list "$SET_NAME" >/dev/null 2>&1 || sudo ipset create "$SET_NAME" hash:ip timeout 3600
sudo ipset add "$SET_NAME" "$IP" timeout "$TTL" -exist
echo "OK: added $IP to $SET_NAME for ${TTL}s"
