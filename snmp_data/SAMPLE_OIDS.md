# Sample OIDs - Network Device Monitoring Lab

## Standard MIB-II OIDs (collected by Datadog)

| OID | Name | Description |
|-----|------|--------------|
| 1.3.6.1.2.1.1.1.0 | sysDescr | System description |
| 1.3.6.1.2.1.1.3.0 | sysUpTime | System uptime |
| 1.3.6.1.2.1.1.5.0 | sysName | System name |
| 1.3.6.1.2.1.1.6.0 | sysLocation | System location |
| 1.3.6.1.2.1.2.1.0 | ifNumber | Number of interfaces |
| 1.3.6.1.2.1.2.2 | ifTable | Interface table |
| 1.3.6.1.2.1.31.1.1.1 | ifXTable | Extended interface table |

## Device sysObjectIDs (for profile matching)

| Device | sysObjectID | Datadog Profile |
|--------|-------------|-----------------|
| Cisco Router | 1.3.6.1.4.1.9.1.516 | Cisco (generic) |
| Palo Alto Firewall | 1.3.6.1.4.1.25461.2.1.2.1 | Palo Alto PAN-OS |
| F5 Load Balancer | 1.3.6.1.4.1.3375.2.1.1 | F5 BIG-IP |

## Test SNMP locally

```bash
# Cisco (port 1611)
snmpget -v2c -c public -r 2 localhost:1611 sysDescr.0
snmpget -v2c -c public -r 2 localhost:1611 sysObjectID.0

# Palo Alto (port 1612)
snmpget -v2c -c public -r 2 localhost:1612 sysDescr.0

# F5 (port 1613)
snmpget -v2c -c public -r 2 localhost:1613 sysDescr.0
```
