#!/usr/bin/env python3
"""Cisco-style Syslog generator."""
import os
import socket
import time
import random

DATADOG_AGENT = os.environ.get("DATADOG_AGENT_HOST", "datadog-agent")
SYSLOG_PORT = int(os.environ.get("SYSLOG_PORT", "514"))
DEVICE_NAME = os.environ.get("DEVICE_NAME", "cisco-router")
INTERVAL = int(os.environ.get("SYSLOG_INTERVAL", "20"))

LOGS = [
    "%LINEPROTO-5-UPDOWN: Line protocol on Interface GigabitEthernet0/1, changed state to up",
    "%LINK-3-UPDOWN: Interface GigabitEthernet0/1, changed state to up",
    "%SYS-5-CONFIG_I: Configured from console by admin",
    "%SEC-6-IPACCESSLOGP: list ACL-IN permitted tcp 10.0.0.10 -> 10.0.0.5",
    "%BGP-5-ADJCHANGE: neighbor 10.0.0.1 Down",
]


def send(msg: str):
    pri = 134  # facility 16, severity 6
    ts = time.strftime("%b %d %H:%M:%S", time.localtime())
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.sendto(f"<{pri}>{ts} {DEVICE_NAME} : {msg}".encode(), (DATADOG_AGENT, SYSLOG_PORT))
    sock.close()


def main():
    print(f"Sending Cisco syslog from {DEVICE_NAME} to {DATADOG_AGENT}:{SYSLOG_PORT}")
    print("Waiting 60s for Datadog agent to be ready...")
    time.sleep(60)
    while True:
        try:
            send(random.choice(LOGS))
        except Exception as e:
            print(f"Error: {e}")
        time.sleep(INTERVAL)


if __name__ == "__main__":
    main()
