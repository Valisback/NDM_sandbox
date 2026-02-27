#!/bin/sh
# Sends SNMP traps to Datadog Agent - run on each network device
# Usage: DEVICE_NAME=cisco-router TRAP_AGENT=datadog-agent TRAP_PORT=9162 ./send_traps.sh

DEVICE_NAME="${DEVICE_NAME:-cisco-router}"
TRAP_AGENT="${DATADOG_AGENT_HOST:-datadog-agent}"
TRAP_PORT="${TRAP_PORT:-9162}"
INTERVAL="${TRAP_INTERVAL:-45}"

# Cisco linkUp/linkDown OIDs, generic enterprise traps
TRAPS="
1.3.6.1.6.3.1.1.5.3
1.3.6.1.6.3.1.1.5.4
1.3.6.1.4.1.9.9.43.2.0.1
1.3.6.1.4.1.9.9.43.2.0.2
1.3.6.1.4.1.9.2.9.1.0.1
"

echo "Sending SNMP traps from $DEVICE_NAME to $TRAP_AGENT:$TRAP_PORT every ${INTERVAL}s"
echo "Waiting 60s for Datadog agent to be ready..."
sleep 60
while true; do
  for oid in $TRAPS; do
    snmptrap -v 2c -c public "$TRAP_AGENT:$TRAP_PORT" "" "$oid" \
      SNMPv2-MIB::sysLocation.0 s "$DEVICE_NAME" 2>/dev/null || true
  done
  sleep "$INTERVAL"
done
