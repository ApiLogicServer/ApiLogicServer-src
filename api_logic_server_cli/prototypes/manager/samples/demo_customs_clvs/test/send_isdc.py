#!/usr/bin/env python
"""
Send a sample ISDC shipment XML to the Kafka topic.
Requires KAFKA_SERVER to be set in config/default.env or environment.

Usage (from project root):
  python test/send_isdc.py
"""
import os
import sys
import time
from pathlib import Path

# ---------------------------------------------------------------------------
# Locate and load config/default.env to get KAFKA_SERVER
# ---------------------------------------------------------------------------
project_root = Path(__file__).parent.parent
env_file = project_root / "config" / "default.env"
kafka_server = os.getenv("KAFKA_SERVER", "localhost:9092")
if env_file.exists():
    for line in env_file.read_text().splitlines():
        line = line.strip()
        if line.startswith("#") or "=" not in line:
            continue
        key, _, val = line.partition("=")
        key = key.strip()
        val = val.strip().strip('"')
        if key == "KAFKA_SERVER" and not os.getenv("KAFKA_SERVER"):
            kafka_server = val

sample_file = project_root / "docs" / "requirements" / "customs_demo" / "message_formats" / "MDE-CDV-HVS-WR-Rev260328.xml"
if not sample_file.exists():
    print(f"ERROR: sample file not found: {sample_file}", file=sys.stderr)
    sys.exit(1)

payload = sample_file.read_bytes()

try:
    from confluent_kafka import Producer
except ImportError:
    print("ERROR: confluent_kafka not installed. Run: pip install confluent-kafka", file=sys.stderr)
    sys.exit(1)

producer = Producer({"bootstrap.servers": kafka_server})
producer.produce(topic="isdc", value=payload)
producer.flush(timeout=15)
print(f"Sent {len(payload)} bytes to topic 'isdc' on {kafka_server}")
