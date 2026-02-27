#!/bin/bash
# Network Device Monitoring Lab - Setup
# Builds and starts all containers

set -e
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Load .env first so DD_API_KEY can be set there
[ -f .env ] && set -a && source .env && set +a

# Check for required env vars
if [ -z "${DD_API_KEY}" ]; then
  echo "ERROR: DD_API_KEY is required. Set it in .env or export it."
  echo "  export DD_API_KEY=your_api_key"
  echo "  Or create .env from .env.example"
  exit 1
fi

# Generate datadog.yaml with API key and site (ensures agent can report)
DD_SITE="${DD_SITE:-datadoghq.com}"
sed -e "s|API_KEY_PLACEHOLDER|${DD_API_KEY}|g" \
    -e "s|SITE_PLACEHOLDER|${DD_SITE}|g" \
    datadog/datadog.yaml.template > datadog/datadog.yaml

# Ensure Docker is running
if ! docker info &>/dev/null; then
  echo "Docker is not running. Starting Docker..."
  if [[ "$(uname)" == "Darwin" ]]; then
    open -a Docker
  elif [[ -x /usr/bin/systemctl ]]; then
    sudo systemctl start docker
  else
    echo "ERROR: Could not start Docker. Please start Docker manually and retry."
    exit 1
  fi
  echo "Waiting for Docker to be ready..."
  for i in {1..60}; do
    if docker info &>/dev/null; then
      echo "Docker is ready."
      break
    fi
    sleep 2
  done
  if ! docker info &>/dev/null; then
    echo "ERROR: Docker failed to start within 2 minutes."
    exit 1
  fi
fi

echo "Building and starting lab..."
docker compose build
docker compose up -d

# Restart agent to pick up regenerated datadog.yaml (if already running)
docker compose restart datadog-agent 2>/dev/null || true

echo ""
echo "Waiting for services to be healthy..."
sleep 15

echo ""
echo "Lab is running. Services:"
docker compose ps

echo ""
echo "Validate SNMP (from host):"
echo "  snmpget -v2c -c public -r 2 localhost:1611 sysDescr.0"
echo "  snmpget -v2c -c public -r 2 localhost:1612 sysDescr.0"
echo "  snmpget -v2c -c public -r 2 localhost:1613 sysDescr.0"
echo ""
echo "Datadog:"
echo "  - Infrastructure > Network Devices"
echo "  - Network > NetFlow"
echo "  - Logs"
echo ""
echo "If nothing appears in Datadog, run: ./diagnose.sh"
