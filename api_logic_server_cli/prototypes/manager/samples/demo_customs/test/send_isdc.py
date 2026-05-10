"""
Send one ISDC sample XML message to the `isdc` Kafka topic.
Run from project root: python test/send_isdc.py

Requires KAFKA_SERVER set in config/default.env (or env).
"""

import os
import sys
from pathlib import Path

SAMPLE = "docs/requirements/customs_demo/message_formats/MDE-CDV-HVS-WR-Rev260328.xml"
TOPIC = "isdc"

def main():
    try:
        from confluent_kafka import Producer
    except ImportError:
        print("confluent_kafka not installed — skipping Kafka test send")
        sys.exit(0)

    kafka_server = os.environ.get('KAFKA_SERVER', 'localhost:9092')
    producer = Producer({'bootstrap.servers': kafka_server})

    payload = Path(SAMPLE).read_text()
    producer.produce(TOPIC, value=payload.encode('utf-8'))
    producer.flush(timeout=10)
    print(f"Sent 1 message to topic '{TOPIC}' ({len(payload)} bytes)")


if __name__ == '__main__':
    main()
