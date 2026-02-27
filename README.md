# Network Device Monitoring Lab

A fully local sandbox that simulates interconnected network devices and integrates them with **Datadog** for monitoring. Uses Docker Compose to run Cisco router, Palo Alto firewall, F5 load balancer, and supporting services.

## Architecture

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│  Jump Host  │────▶│   Cisco     │────▶│   Palo Alto │────▶│     F5      │
│ (traffic)   │     │   Router    │     │   Firewall  │     │ Load Balancer│
└─────────────┘     └──────┬──────┘     └──────┬──────┘     └──────┬──────┘
                          │                  │                   │
                          │ SNMP+NetFlow     │ SNMP+Syslog       │ SNMP
                          ▼                  ▼                   ▼
                    ┌─────────────────────────────────────────────────┐
                    │              Datadog Agent                       │
                    │  SNMP | NetFlow | Syslog                         │
                    └─────────────────────────────────────────────────┘
                                        │
                                        ▼
                              ┌─────────────────┐
                              │    Backend      │
                              │  (HTTP server)  │
                              └─────────────────┘
```

## Prerequisites

- **Docker** and **Docker Compose** v2+
- **Datadog API key** ([create one](https://app.datadoghq.com/organization-settings/api-keys))

## Quick Start

### 1. Configure environment

```bash
cp .env.example .env
# Edit .env and set your DD_API_KEY
```

Or export directly:

```bash
export DD_API_KEY=your_api_key_here
export DD_SITE=datadoghq.com   # optional, default is datadoghq.com
```

### 2. Start the lab

```bash
chmod +x setup.sh teardown.sh
./setup.sh
```

### 3. Stop and clean up

```bash
./teardown.sh
```

## What Gets Simulated

| Service | IP | SNMP | Traps | NetFlow | Syslog | Traffic |
|---------|-----|------|-------|---------|--------|---------|
| cisco-router | 10.0.0.2 | ✓ | ✓ | ✓ (exporter) | ✓ | → firewall |
| paloalto-firewall | 10.0.0.3 | ✓ | ✓ | - | ✓ | → load balancer |
| f5-loadbalancer | 10.0.0.4 | ✓ | ✓ | - | ✓ | → backend |
| netflow-exporter | 10.0.0.6 | - | - | ✓ v5 | - | Synthetic flows |
| jump-host | 10.0.0.10 | - | - | - | - | HTTP + ICMP to all |
| backend | 10.0.0.5 | - | - | - | - | HTTP server |
| datadog-agent | 10.0.0.100 | polls | 9162 | 2055/56 | 514 | Collector |

## Validate in Datadog

### SNMP / Network Devices

1. Go to **Infrastructure > Network Devices**
2. Wait 1–2 minutes for discovery
3. You should see: cisco-router, paloalto-firewall, f5-loadbalancer

### NetFlow

1. Go to **Network > NetFlow**
2. Check **Traffic Volume**, **Flows**, **Conversations**
3. Flows should show traffic between 10.0.0.10 (jump-host) and 10.0.0.5 (backend)

### Syslog

1. Go to **Logs > Log Explorer**
2. Filter: `source:syslog`
3. You should see Cisco, Palo Alto, and F5–style logs

### SNMP Traps

1. Go to **Logs > Log Explorer**
2. Filter: `source:snmp-traps`
3. Traps are sent from all three devices every ~45s

### Syslog ↔ Device correlation

1. In **Logs > Log Configuration > Pipelines**, add a **Log Remapper**:
   - Source: `source_host`
   - Target tag: `syslog_ip`
2. Then in **Network Devices**, open a device and check the **Syslog** tab

## Troubleshooting

### No devices in Datadog

- Run `./diagnose.sh` to check agent status, SNMP connectivity, and logs
- Ensure `DD_API_KEY` in `.env` is valid for your Datadog org
- If using EU/US3/etc., set `DD_SITE` in `.env` (e.g. `datadoghq.eu`)
- Re-run `./setup.sh` after changing `.env` (regenerates agent config)
- Test SNMP from host: `snmpget -v2c -c public -r 2 localhost:1611 sysDescr.0`

### No NetFlow data

- NetFlow is sent every 30 seconds; wait 1–2 minutes
- Check `docker compose logs netflow-exporter` for send errors
- Ensure firewall allows UDP 2055/2056 to the agent

### No Syslog or SNMP Traps in Datadog

- **Startup delay**: Traps and syslog wait 60s for the agent to be ready. Wait ~2 minutes after `./setup.sh`
- Run `./diagnose.sh` and check device logs (section 8)
- Verify agent listens: `docker compose exec datadog-agent netstat -ulnp | grep -E '514|9162'`
- Check device logs: `docker compose logs cisco-router --tail 30` (look for "Sending" messages)

### No traffic flowing

- Jump host waits 30s before first traffic. Check `docker compose logs jump-host` for "Traffic cycle" messages
- Jump host only depends on backend; other devices may still be starting. Wait 1–2 minutes

### SNMP port conflicts

If port 161 is in use, the lab maps SNMP to 1611 (Cisco), 1612 (Palo Alto), 1613 (F5). The Datadog agent connects to the internal Docker IPs (10.0.0.x) on port 161, so host port conflicts do not affect it.

### Agent fails to start

- Confirm `datadog/datadog.yaml` and `datadog/conf.d/` are present
- Check `DD_SITE` for your region (e.g. `datadoghq.eu`, `us3.datadoghq.com`)

## File Structure

```
.
├── docker-compose.yml      # Service definitions
├── setup.sh                # Build and start
├── teardown.sh             # Stop and remove
├── .env.example            # Env template
├── snmp_data/              # SNMP configs per device
│   ├── cisco/
│   ├── paloalto/
│   ├── f5/
│   └── SAMPLE_OIDS.md
├── datadog/                # Agent config
│   ├── datadog.yaml
│   ├── conf.d/snmp.d/
│   ├── conf.d/syslog.d/
│   ├── NETFLOW_CONFIG.md
│   └── SYSLOG_RULES.md
├── netflow-exporter/       # NetFlow v5 generator
├── syslog-generator/       # Palo Alto syslog simulator
├── traffic-generator/      # Jump host traffic
└── backend/                # HTTP backend
```

## Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| DD_API_KEY | Yes | - | Datadog API key |
| DD_SITE | No | datadoghq.com | Datadog site (e.g. datadoghq.eu) |

## License

MIT
