# Syslog Forwarding Rules

## Lab Configuration

- **Listener**: UDP port 514
- **Source**: syslog (for NDM correlation)
- **Service**: paloalto-firewall

## Device Correlation

For NDM to associate logs with devices, ensure `syslog_ip` tag matches device IP:

- Palo Alto firewall: 10.0.0.3
- The Agent's `use_sourcehost_tag: true` adds `source_host` with sender IP
- Create a Log Pipeline: remap `source_host` → `syslog_ip`

## Log Pipeline (Datadog UI)

1. Go to **Logs > Log Configuration > Pipelines**
2. Add processor: **Log Remapper**
   - Source: `source_host`
   - Target tag: `syslog_ip`

This enables the Syslog tab in the device side panel.
