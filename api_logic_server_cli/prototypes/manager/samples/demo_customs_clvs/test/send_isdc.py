"""
Kafka test publisher for topic `isdc`: publishes one CIMCorp shipment XML (confluent_kafka.Producer, not a subprocess).

    python test/send_isdc.py [path/to/message.xml]      # default: the reference message

Broker: KAFKA_SERVER (default localhost:9092).  The server must be running with Kafka enabled
(config/default.env: KAFKA_SERVER, KAFKA_CONSUMER_GROUP) to process the message.
"""
import os
import sys
from pathlib import Path
from confluent_kafka import Producer

DEFAULT_FILE = "docs/requirements/customs_demo/message_formats/MDE-CDV-HVS-WR-Rev260328.xml"


def main():
    path = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_FILE
    payload = Path(path).read_text()
    producer = Producer({"bootstrap.servers": os.getenv("KAFKA_SERVER", "localhost:9092")})
    result = {}

    def delivered(err, msg):
        result["err"] = err
        result["msg"] = msg

    producer.produce("isdc", value=payload.encode("utf-8"), callback=delivered)
    producer.flush(timeout=15)
    if result.get("err") or "msg" not in result:
        print(f"FAILED to deliver {path}: {result.get('err', 'no delivery report (broker down?)')}")
        sys.exit(1)
    m = result["msg"]
    print(f"Delivered {path} to topic {m.topic()} partition {m.partition()} offset {m.offset()}")


if __name__ == "__main__":
    main()
