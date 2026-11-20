"""
Kafka test publisher for topic order_b2b: publishes one message (a JSON file) and reports delivery.

    python test/send_order_b2b.py                                   # the sample message
    python test/send_order_b2b.py path/to/message.json [topic] [bootstrap]

Usually you send through the debug endpoint instead (curl /consume_debug/order_b2b, live mode); this is the
standalone tool.  Uses confluent_kafka.Producer directly (never kafka-console-producer: one message per line).
"""
import sys
from pathlib import Path
from confluent_kafka import Producer

file_path = sys.argv[1] if len(sys.argv) > 1 else "docs/requirements/demo_eai/message_formats/order_b2b.json"
topic = sys.argv[2] if len(sys.argv) > 2 else "order_b2b"
bootstrap = sys.argv[3] if len(sys.argv) > 3 else "localhost:9092"


def delivered(err, msg):
    """Kafka test publisher: reports the broker's acknowledgement (or the error) for the message."""
    if err:
        print(f"delivery failed: {err}")
    else:
        print(f"delivered to {msg.topic()} partition {msg.partition()} offset {msg.offset()}")


producer = Producer({"bootstrap.servers": bootstrap})
producer.produce(topic, value=Path(file_path).read_text().encode("utf-8"), callback=delivered)
producer.flush(10)
