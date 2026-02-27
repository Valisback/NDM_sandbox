#!/usr/bin/env python3
"""F5 BIG-IP style Syslog generator."""
import os
import socket
import time
import random

DATADOG_AGENT = os.environ.get("DATADOG_AGENT_HOST", "datadog-agent")
SYSLOG_PORT = int(os.environ.get("SYSLOG_PORT", "514"))
DEVICE_NAME = os.environ.get("DEVICE_NAME", "f5-loadbalancer")
INTERVAL = int(os.environ.get("SYSLOG_INTERVAL", "25"))

LOGS = [
    "01070163:5: Pool /Common/http_pool member 10.0.0.5:8080 monitor status down",
    "01070163:5: Pool /Common/http_pool member 10.0.0.5:8080 monitor status up",
    "01020011:5: Virtual server 10.0.0.4:80 connection limit reached",
    "01070352:3: Connection to 10.0.0.5:8080 timed out",
    "01010016:5: New connection to virtual 10.0.0.4:80 from 10.0.0.10",
]


def send(msg: str):
    pri = 134
    ts = time.strftime("%Y-%m-%dT%H:%M:%S.000Z", time.gmtime())
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.sendto(f"<{pri}>{ts} {DEVICE_NAME} - - - {msg}".encode(), (DATADOG_AGENT, SYSLOG_PORT))
    sock.close()


def main():
    print(f"Sending F5 syslog from {DEVICE_NAME} to {DATADOG_AGENT}:{SYSLOG_PORT}")
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
