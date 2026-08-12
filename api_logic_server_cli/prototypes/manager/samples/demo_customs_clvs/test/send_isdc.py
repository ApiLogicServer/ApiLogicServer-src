"""
Kafka test publisher for the isdc EAI consume pipeline.

Reads a sample CIMCorp shipment XML file and publishes it to Kafka topic `isdc`.
Uses confluent_kafka.Producer directly — never subprocess + kafka-console-producer,
which sends one message per input line and mangles multi-line XML payloads.

Usage:
    python test/send_isdc.py [path/to/message.xml]

Default file: docs/requirements/customs_demo/message_formats/MDE-CDV-HVS-WR-Rev260328.xml
"""
import sys
from pathlib import Path
from confluent_kafka import Producer

BOOTSTRAP_SERVERS = "localhost:9092"
TOPIC = "isdc"
DEFAULT_FILE = "docs/requirements/customs_demo/message_formats/MDE-CDV-HVS-WR-Rev260328.xml"


def delivery_report(err, msg):
    if err is not None:
        print(f"Delivery failed: {err}")
    else:
        print(f"Delivered to {msg.topic()} [{msg.partition()}] offset {msg.offset()}")


def main():
    file_path = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_FILE
    payload = Path(file_path).read_text()

    producer = Producer({"bootstrap.servers": BOOTSTRAP_SERVERS})
    producer.produce(TOPIC, value=payload.encode("utf-8"), callback=delivery_report)
    producer.flush(timeout=10)
    print(f"Sent {file_path} to topic '{TOPIC}'")


if __name__ == "__main__":
    main()
