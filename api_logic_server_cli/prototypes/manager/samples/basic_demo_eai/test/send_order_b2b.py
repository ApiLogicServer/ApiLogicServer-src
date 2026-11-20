"""
Kafka test publisher: sends one order_b2b message (a JSON file) to the broker, and reports delivery.
The debug endpoint's live mode is the usual way to send; this is the standalone tool.

    python test/send_order_b2b.py [file] [topic] [broker]
    python test/send_order_b2b.py docs/requirements/demo_eai/message_formats/order_b2b.json order_b2b localhost:9092
"""
import sys
from pathlib import Path

from confluent_kafka import Producer


def main():
    """Kafka test publisher: publishes the file's contents as one message and waits for the broker's acknowledgement."""
    file = sys.argv[1] if len(sys.argv) > 1 else "docs/requirements/demo_eai/message_formats/order_b2b.json"
    topic = sys.argv[2] if len(sys.argv) > 2 else "order_b2b"
    broker = sys.argv[3] if len(sys.argv) > 3 else "localhost:9092"
    payload = Path(file).read_text(encoding="utf-8")
    result = {}

    def delivered(err, msg):
        result["err"] = err
        result["msg"] = msg

    producer = Producer({"bootstrap.servers": broker})
    producer.produce(topic=topic, value=payload.encode("utf-8"), callback=delivered)
    producer.flush(timeout=10)
    if result.get("err") or "msg" not in result:
        print(f"NOT delivered to {topic} @ {broker}: {result.get('err', 'no acknowledgement')}")
        sys.exit(1)
    print(f"delivered to {topic} partition {result['msg'].partition()} offset {result['msg'].offset()}")


if __name__ == "__main__":
    main()
