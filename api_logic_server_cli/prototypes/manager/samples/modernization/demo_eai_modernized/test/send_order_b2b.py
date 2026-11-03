"""
Kafka test publisher: sends one message to a topic through a real broker (confluent_kafka.Producer).

    python test/send_order_b2b.py [topic] [payload_file]
    defaults: order_b2b  docs/requirements/demo_eai/message_formats/order_b2b.json

The debug endpoint's live mode is the usual way to send (see api/api_discovery/order_b2b_kafka_consume_debug.py);
this is the standalone tool.  Broker: KAFKA_SERVER (default localhost:9092).
"""
import os
import sys
from pathlib import Path
from confluent_kafka import Producer

topic = sys.argv[1] if len(sys.argv) > 1 else "order_b2b"
payload_file = Path(sys.argv[2] if len(sys.argv) > 2 else "docs/requirements/demo_eai/message_formats/order_b2b.json")
payload = payload_file.read_text()

outcome = {}


def delivered(err, msg):
    outcome["error"] = str(err) if err else None
    outcome["where"] = None if err else f"{msg.topic()} [{msg.partition()}] @ {msg.offset()}"


producer = Producer({"bootstrap.servers": os.getenv("KAFKA_SERVER", "localhost:9092")})
producer.produce(topic, value=payload.encode("utf-8"), callback=delivered)
producer.flush(timeout=10)
if outcome.get("error") or "where" not in outcome:
    print(f"NOT delivered: {outcome}")
    sys.exit(1)
print(f"delivered to {outcome['where']}")
