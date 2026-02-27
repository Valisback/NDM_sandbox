#!/bin/bash
# Network Device Monitoring Lab - Diagnostics
# Run this when nothing appears in Datadog

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

[ -f .env ] && set -a && source .env && set +a

echo "=== Lab Diagnostics ==="
echo ""

# Check containers
echo "1. Container status:"
docker compose ps 2>/dev/null || { echo "   Run ./setup.sh first"; exit 1; }
echo ""

# Check Datadog agent
echo "2. Datadog Agent status:"
docker compose exec datadog-agent agent status 2>/dev/null | head -80 || echo "   Agent not running or error"
echo ""

# Check SNMP section specifically
echo "3. SNMP check status:"
docker compose exec datadog-agent agent status 2>/dev/null | grep -A 30 "snmp" || true
echo ""

# Test SNMP from agent to devices
echo "4. SNMP connectivity (agent -> devices):"
for ip in 10.0.0.2 10.0.0.3 10.0.0.4; do
  out=$(docker compose exec -T datadog-agent sh -c "command -v snmpget >/dev/null && snmpget -v2c -c public -r 1 -t 2 $ip sysDescr.0 2>/dev/null" 2>/dev/null) || true
  if echo "$out" | grep -q "SNMPv2-MIB"; then
    echo "   $ip: OK"
  else
    echo "   $ip: FAILED or snmpget not available (check agent status above)"
  fi
done
echo ""

# Check env
echo "5. Agent environment:"
docker compose exec datadog-agent env 2>/dev/null | grep -E "DD_API_KEY|DD_SITE" | sed 's/DD_API_KEY=.*/DD_API_KEY=***/' || true
echo ""

# Check logs
echo "6. Recent agent logs (last 20 lines):"
docker compose logs datadog-agent --tail 20 2>/dev/null || true
echo ""

# Check traffic generator
echo "7. Jump host (traffic generator) logs:"
docker compose logs jump-host --tail 10 2>/dev/null || true
echo ""

# Check device logs (traps/syslog)
echo "8. Cisco router logs (traps/syslog):"
docker compose logs cisco-router --tail 5 2>/dev/null || true
echo ""
echo "=== Run: docker compose logs -f <service>  (for live logs) ==="
