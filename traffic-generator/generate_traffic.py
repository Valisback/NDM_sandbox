#!/usr/bin/env python3
"""
Traffic generator - simulates jump host generating traffic across the lab.
Traffic flows: Jump Host -> Router -> Firewall -> Load Balancer -> Backend
"""
import os
import subprocess
import time
import random

BACKEND_HOST = os.environ.get("BACKEND_HOST", "backend")
ROUTER_HOST = os.environ.get("ROUTER_HOST", "cisco-router")
FIREWALL_HOST = os.environ.get("FIREWALL_HOST", "paloalto-firewall")
LB_HOST = os.environ.get("LB_HOST", "f5-loadbalancer")
INTERVAL = int(os.environ.get("TRAFFIC_INTERVAL", "8"))


def http_traffic(host: str, port: int = 8080):
    """Generate HTTP traffic."""
    try:
        subprocess.run(
            ["curl", "-s", "-o", "/dev/null", "-m", "3", f"http://{host}:{port}/"],
            timeout=5,
        )
    except Exception:
        pass


def icmp_traffic(host: str):
    """Generate ICMP traffic."""
    try:
        subprocess.run(["ping", "-c", "1", host], timeout=3, capture_output=True)
    except Exception:
        pass


def main():
    targets = [
        (BACKEND_HOST, "backend"),
        (ROUTER_HOST, "router"),
        (FIREWALL_HOST, "firewall"),
        (LB_HOST, "loadbalancer"),
    ]
    print(f"Generating traffic to: {[t[1] for t in targets]}", flush=True)
    print("Waiting for backend to be reachable...", flush=True)
    for _ in range(30):
        try:
            subprocess.run(
                ["curl", "-s", "-o", "/dev/null", "-m", "2", f"http://{BACKEND_HOST}:8080/"],
                timeout=3,
                capture_output=True,
            )
            print("Backend ready.", flush=True)
            break
        except Exception:
            pass
        time.sleep(2)
    else:
        print("Warning: backend not reachable after 60s, continuing anyway.", flush=True)
    count = 0
    while True:
        try:
            # HTTP to backend (main app traffic)
            http_traffic(BACKEND_HOST)
            # ICMP to all devices (simulates monitoring/connectivity checks)
            for host, name in targets:
                if random.random() > 0.3:
                    icmp_traffic(host)
            count += 1
            if count % 5 == 0:
                print(f"Traffic cycle {count} complete", flush=True)
        except Exception as e:
            print(f"Error: {e}")
        time.sleep(INTERVAL)


if __name__ == "__main__":
    main()
