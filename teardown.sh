#!/bin/bash
# Network Device Monitoring Lab - Teardown
# Stops and removes all containers and networks

set -e
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "Stopping and removing lab..."
docker compose down -v

echo "Lab torn down."
