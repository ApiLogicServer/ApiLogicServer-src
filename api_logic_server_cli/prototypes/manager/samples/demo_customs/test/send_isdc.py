"""
Send a sample ISDC XML message to the Kafka topic 'isdc'.

Requires Kafka running (docker compose -f integration/kafka/dockercompose_start_kafka.yml up -d)
and KAFKA_SERVER set in config/default.env or environment.

Usage (from project root):
    python test/send_isdc.py
    python test/send_isdc.py --file docs/requirements/customs_demo/message_formats/MDE-CDV-HVS-WR-Rev260328-another.xml
"""

import argparse
import os
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

DEFAULT_XML = "docs/requirements/customs_demo/message_formats/MDE-CDV-HVS-WR-Rev260328.xml"


def main():
    parser = argparse.ArgumentParser(description="Send ISDC XML to Kafka topic isdc")
    parser.add_argument("--file", default=DEFAULT_XML, help="XML file to send")
    parser.add_argument("--topic", default="isdc", help="Kafka topic (default: isdc)")
    args = parser.parse_args()

    kafka_server = os.getenv("KAFKA_SERVER", "localhost:9092")

    try:
        from confluent_kafka import Producer
    except ImportError:
        print("confluent_kafka not installed. Run: pip install confluent-kafka")
        sys.exit(1)

    payload = Path(args.file).read_text()
    producer = Producer({"bootstrap.servers": kafka_server})
    producer.produce(topic=args.topic, value=payload.encode("utf-8"))
    producer.flush(timeout=10)
    print(f"Sent {len(payload)} bytes to topic '{args.topic}' from {args.file}")


if __name__ == "__main__":
    main()
