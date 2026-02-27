# NetFlow Configuration

## Lab Setup

- **NetFlow v5** listener: UDP port 2056
- **NetFlow v9** listener: UDP port 2055
- Exporter IP: 10.0.0.2 (cisco-router) - flows are attributed to this device

## Flow Types Supported

| Flow Type | Port | Used By |
|-----------|------|---------|
| netflow5 | 2056 | netflow-exporter (Cisco simulation) |
| netflow9 | 2055 | Available for additional exporters |
| ipfix | 4739 | Not configured |
| sflow5 | 6343 | Not configured |

## Enrichment

NetFlow records are enriched with device metadata when the exporter IP (10.0.0.2) matches an SNMP-monitored device (cisco-router).
