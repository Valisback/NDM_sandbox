# SNMP Traps Configuration

## Lab Setup

- **Listener**: UDP port 9162 (avoids privileged port 162)
- **Community**: public
- **Devices**: Cisco, Palo Alto, F5 all send traps every ~45s

## Trap OIDs Sent

- 1.3.6.1.6.3.1.1.5.3 (linkUp)
- 1.3.6.1.6.3.1.1.5.4 (linkDown)
- 1.3.6.1.4.1.9.9.43.2.0.1 (Cisco config change)
- 1.3.6.1.4.1.9.9.43.2.0.2 (Cisco interface)
- 1.3.6.1.4.1.9.2.9.1.0.1 (Cisco cold start)

## View in Datadog

Logs > Log Explorer > filter: `source:snmp-traps`
