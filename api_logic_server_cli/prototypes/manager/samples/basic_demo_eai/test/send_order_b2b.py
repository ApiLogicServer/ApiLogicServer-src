"""
Kafka test publisher: sends one message to topic order_b2b.

Run from project root (broker up, topics created by integration/kafka/order_b2b_reset.sh):
    python test/send_order_b2b.py [path/to/payload.json] [topic]

Defaults to docs/requirements/demo_eai/message_formats/order_b2b.json and topic order_b2b.
Uses confluent_kafka.Producer directly (not kafka-console-producer), so multi-line payloads arrive as ONE message.
"""
import os
import sys
from pathlib import Path

from confluent_kafka import Producer

payload_file = Path(sys.argv[1] if len(sys.argv) > 1 else "docs/requirements/demo_eai/message_formats/order_b2b.json")
topic = sys.argv[2] if len(sys.argv) > 2 else "order_b2b"
bootstrap = os.getenv("KAFKA_SERVER", "localhost:9092")

payload = payload_file.read_text()
delivery = {}


def on_delivery(err, msg):
    """Delivery report: records the outcome of produce()."""
    delivery["err"] = err
    delivery["msg"] = msg


producer = Producer({"bootstrap.servers": bootstrap})
producer.produce(topic, value=payload.encode("utf-8"), callback=on_delivery)
producer.flush(timeout=10)

if delivery.get("err") or "msg" not in delivery:
    print(f"NOT delivered to {topic} on {bootstrap}: {delivery.get('err') or 'no delivery report within 10 s'}")
    sys.exit(1)
m = delivery["msg"]
print(f"Delivered {payload_file} to {topic} on {bootstrap} (partition {m.partition()}, offset {m.offset()})")
