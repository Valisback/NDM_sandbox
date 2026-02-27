#!/usr/bin/env python3
"""
Palo Alto-style Syslog generator - sends synthetic firewall logs to Datadog Agent.
"""
import os
import socket
import time
import random

DATADOG_AGENT = os.environ.get("DATADOG_AGENT_HOST", "datadog-agent")
SYSLOG_PORT = int(os.environ.get("SYSLOG_PORT", "514"))
INTERVAL = int(os.environ.get("SYSLOG_INTERVAL", "15"))

# Palo Alto syslog format examples
TRAFFIC_LOGS = [
    '1,2025-02-27T12:00:00.000-00:00,001606001234,TRAFFIC,start,2025/02/27 12:00:00,10.0.0.10,10.0.0.5,0.0.0.0,0.0.0.0,allow,,,http,outbound,trust,untrust,1,2025,0,0,0,0,0,0,0,0,,from-policy,,,0,0,0,0,,lab-firewall,,',
    '1,2025-02-27T12:00:01.000-00:00,001606001234,TRAFFIC,end,2025/02/27 12:00:01,10.0.0.10,10.0.0.5,0.0.0.0,0.0.0.0,allow,,,http,outbound,trust,untrust,1,2025,2048,1500,0,0,0,0,0,0,,from-policy,,,0,0,0,0,,lab-firewall,,',
    '1,2025-02-27T12:00:02.000-00:00,001606001234,THREAT,vulnerability,2025/02/27 12:00:02,10.0.0.10,10.0.0.5,0.0.0.0,0.0.0.0,drop,,,http,outbound,trust,untrust,1,2025,0,0,0,0,0,0,0,0,,from-policy,,,0,0,0,0,,lab-firewall,,',
]

SYSTEM_LOGS = [
    "Configuration committed by admin",
    "Interface eth0 link up",
    "Interface eth0 link down",
    "Session timed out",
    "HA state changed to active",
]


def send_syslog(msg: str, facility=20, severity=6):
    """Send RFC 5424-style syslog over UDP."""
    pri = facility * 8 + severity
    timestamp = time.strftime("%Y-%m-%dT%H:%M:%S.000Z", time.gmtime())
    syslog_msg = f"<{pri}>{timestamp} paloalto-firewall lab - - - {msg}"
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.sendto(syslog_msg.encode(), (DATADOG_AGENT, SYSLOG_PORT))
    sock.close()


def main():
    print(f"Sending Syslog to {DATADOG_AGENT}:{SYSLOG_PORT}")
    print("Waiting 60s for Datadog agent to be ready...")
    time.sleep(60)
    idx = 0
    while True:
        try:
            if idx % 3 == 0:
                msg = random.choice(TRAFFIC_LOGS)
            else:
                msg = random.choice(SYSTEM_LOGS)
            send_syslog(msg)
            print(f"Sent: {msg[:60]}...")
        except Exception as e:
            print(f"Error: {e}")
        idx += 1
        time.sleep(INTERVAL)


if __name__ == "__main__":
    main()
