"""
Standalone Kafka test publisher for topic order_b2b using confluent_kafka.Producer.
Run from project root: python test/send_order_b2b.py [sample_file]
"""
from pathlib import Path
import sys
from confluent_kafka import Producer

TOPIC = "order_b2b"
BOOTSTRAP_SERVERS = "localhost:9092"
DEFAULT_SAMPLE = Path(__file__).parent.parent / "docs" / "requirements" / "demo_eai" / "message_formats" / "order_b2b.json"


def _delivery_report(err, msg):
    if err is not None:
        print(f"Delivery failed: {err}")
    else:
        print(f"Delivered to {msg.topic()} [partition {msg.partition()}] @ offset {msg.offset()}")


def main():
    sample_path = Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_SAMPLE
    payload = sample_path.read_text(encoding="utf-8")
    producer = Producer({"bootstrap.servers": BOOTSTRAP_SERVERS})
    producer.produce(TOPIC, value=payload.encode("utf-8"), callback=_delivery_report)
    producer.flush(timeout=10)


if __name__ == "__main__":
    main()

