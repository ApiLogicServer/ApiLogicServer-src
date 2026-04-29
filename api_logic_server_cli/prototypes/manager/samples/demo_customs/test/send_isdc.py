"""
Send a test CIMCorpShipment XML message to the `isdc` Kafka topic.

Requires a running Kafka broker and server started with KAFKA_SERVER configured.
Run from project root: python test/send_isdc.py

To repeat without collision, the replace policy (ISDC_DUPLICATE_POLICY=replace) handles
duplicate LOCAL_SHIPMENT_OID_NBR automatically.  For insert-only testing set ISDC_DUPLICATE_POLICY=fail.

Reset between runs:
  bash integration/kafka/isdc_reset.sh   # reset Kafka topics + truncate log
  bash integration/kafka/isdc_reset_db.sh  # clear domain + blob tables
"""

from pathlib import Path

try:
    from confluent_kafka import Producer
except ImportError:
    raise SystemExit("confluent-kafka not installed. Run: pip install confluent-kafka")

SAMPLE_FILE = "docs/requirements/customs_demo/message_formats/MDE-CDV-HVS-WR-Rev260328.xml"
KAFKA_SERVER = "localhost:9092"
TOPIC = "isdc"

payload = Path(SAMPLE_FILE).read_text()
producer = Producer({"bootstrap.servers": KAFKA_SERVER})
producer.produce(TOPIC, value=payload.encode("utf-8"))
producer.flush(timeout=10)
print(f"Sent {len(payload)} bytes to topic '{TOPIC}' from {SAMPLE_FILE}")
