#!/usr/bin/env python3
"""
NetFlow v5 exporter - generates synthetic flow records for lab testing.
Simulates Cisco router exporting flows to Datadog Agent.
"""
import os
import socket
import struct
import time
import random

DATADOG_HOST = os.environ.get("DATADOG_AGENT_HOST", "datadog-agent")
NETFLOW_PORT = int(os.environ.get("NETFLOW_PORT", "2056"))  # NetFlow v5
EXPORTER_IP = os.environ.get("EXPORTER_IP", "10.0.0.2")
INTERVAL = int(os.environ.get("INTERVAL", "30"))


def ip_to_int(ip: str) -> int:
    """Convert dotted IP to integer."""
    return struct.unpack("!I", socket.inet_aton(ip))[0]


def build_netflow_v5_packet(flows: list, uptime: int, seq: int) -> bytes:
    """Build a NetFlow v5 packet. Each flow is a dict with src/dst/bytes/packets/etc."""
    now = int(time.time())
    header = struct.pack(
        "!HHIIIIBBH",
        5,  # version
        len(flows),  # count
        uptime,  # sys uptime ms
        now,  # unix_secs
        0,  # unix_nsecs
        seq,  # flow_sequence
        0,  # engine_type
        0,  # engine_id
        0,  # sampling_interval
    )
    records = b""
    for f in flows:
        rec = struct.pack(
            "!IIIIHHIIIIHHBBBBHHBBH",
            ip_to_int(f["srcaddr"]),
            ip_to_int(f["dstaddr"]),
            ip_to_int(f.get("nexthop", "0.0.0.0")),
            f.get("input", 1),
            f.get("output", 2),
            f.get("dPkts", 100),
            f.get("dOctets", 1500),
            f.get("First", now - 60),
            f.get("Last", now),
            f.get("srcport", 54321),
            f.get("dstport", f.get("dstport", 80)),
            0,  # pad1
            f.get("tcp_flags", 0x18),  # ACK+PUSH
            f.get("prot", 6),  # TCP
            f.get("tos", 0),
            f.get("src_as", 0),
            f.get("dst_as", 0),
            f.get("src_mask", 0),
            f.get("dst_mask", 0),
            0, 0,  # pad2
        )
        records += rec
    return header + records


def generate_flows(exporter_ip: str) -> list:
    """Generate synthetic flow records simulating lab traffic between devices."""
    base_time = int(time.time())
    flows = [
        # Jump host -> Backend (HTTP)
        {"srcaddr": "10.0.0.10", "dstaddr": "10.0.0.5", "dstport": 8080, "prot": 6},
        # Backend -> Jump host (response)
        {"srcaddr": "10.0.0.5", "dstaddr": "10.0.0.10", "srcport": 8080, "prot": 6},
        # Jump host -> Router (SNMP)
        {"srcaddr": "10.0.0.10", "dstaddr": "10.0.0.2", "dstport": 161, "prot": 17},
        # Jump host -> Firewall (ICMP/HTTP)
        {"srcaddr": "10.0.0.10", "dstaddr": "10.0.0.3", "prot": 1},
        # Jump host -> Load balancer
        {"srcaddr": "10.0.0.10", "dstaddr": "10.0.0.4", "prot": 6},
        # Router -> Firewall (device-to-device)
        {"srcaddr": "10.0.0.2", "dstaddr": "10.0.0.3", "prot": 1},
        # Firewall -> Load balancer
        {"srcaddr": "10.0.0.3", "dstaddr": "10.0.0.4", "prot": 6},
        # Load balancer -> Backend
        {"srcaddr": "10.0.0.4", "dstaddr": "10.0.0.5", "dstport": 8080, "prot": 6},
    ]
    result = []
    for f in flows:
        result.append({
            "srcaddr": f["srcaddr"],
            "dstaddr": f["dstaddr"],
            "srcport": f.get("srcport", random.randint(40000, 60000)),
            "dstport": f.get("dstport", 80 if f.get("prot") == 6 else 0),
            "dPkts": random.randint(10, 200),
            "dOctets": random.randint(500, 15000),
            "First": base_time - 120,
            "Last": base_time,
            "prot": f.get("prot", 6),
        })
    return result


def main():
    print(f"Sending NetFlow v5 to {DATADOG_HOST}:{NETFLOW_PORT} (exporter IP: {EXPORTER_IP})")
    print("Waiting 45s for Datadog agent to be ready...")
    time.sleep(45)
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    uptime = 0
    seq = 0
    while True:
        try:
            flows = generate_flows(EXPORTER_IP)
            packet = build_netflow_v5_packet(flows, uptime, seq)
            sock.sendto(packet, (DATADOG_HOST, NETFLOW_PORT))
            uptime += INTERVAL * 1000
            seq += len(flows)
            print(f"Sent {len(flows)} flow records (seq={seq})")
        except Exception as e:
            print(f"Error: {e}")
        time.sleep(INTERVAL)


if __name__ == "__main__":
    main()
