#!/bin/sh
# Generates device-to-device traffic - run on each device to ping next in chain
# Usage: NEXT_HOP=10.0.0.3 ./device_traffic.sh
NEXT_HOP="${NEXT_HOP:-}"
INTERVAL="${DEVICE_TRAFFIC_INTERVAL:-20}"
[ -z "$NEXT_HOP" ] && exit 0
while true; do
  ping -c 1 "$NEXT_HOP" 2>/dev/null || true
  sleep "$INTERVAL"
done
