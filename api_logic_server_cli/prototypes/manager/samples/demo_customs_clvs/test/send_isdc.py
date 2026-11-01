"""
Kafka test publisher for topic isdc: publishes one sample shipment XML and reports delivery.
Run from project root (broker up, KAFKA_SERVER set):  python test/send_isdc.py [path/to/message.xml]
"""
import os
import sys
from pathlib import Path
from confluent_kafka import Producer

SAMPLE = "docs/requirements/customs_demo/message_formats/MDE-CDV-HVS-WR-Rev260328.xml"


def main():
    """Publish one message to isdc and wait for the broker acknowledgement."""
    path = sys.argv[1] if len(sys.argv) > 1 else SAMPLE
    server = os.getenv("KAFKA_SERVER", "localhost:9092")
    producer = Producer({"bootstrap.servers": server})
    result = {}

    def delivered(err, msg):
        result["err"], result["msg"] = err, msg

    producer.produce("isdc", value=Path(path).read_text().encode("utf-8"), callback=delivered)
    producer.flush(10)
    if result.get("err") or not result.get("msg"):
        print(f"FAILED to deliver {path} to isdc at {server}: {result.get('err')}")
        sys.exit(1)
    msg = result["msg"]
    print(f"delivered {path} to isdc [partition {msg.partition()} offset {msg.offset()}]")


if __name__ == "__main__":
    main()
