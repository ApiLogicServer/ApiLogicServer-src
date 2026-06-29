"""
Send a CIMCorp ISDC XML message to the Kafka 'isdc' topic.
Used for Step 4 (Live Kafka end-to-end test).

Usage (from project root, with Kafka running):
    python test/send_isdc.py
    python test/send_isdc.py docs/requirements/customs_demo/message_formats/MDE-CDV-LVS-1.xml
"""

import os
import sys

try:
    from confluent_kafka import Producer
except ImportError:
    print('ERROR: confluent_kafka not installed. Run: pip install confluent_kafka')
    sys.exit(1)

DEFAULT_FILE = 'docs/requirements/customs_demo/message_formats/MDE-CDV-HVS-WR-Rev260328.xml'
TOPIC = 'isdc'

kafka_server = os.getenv('KAFKA_SERVER', 'localhost:9092')
xml_file = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_FILE

print(f'send_isdc: broker={kafka_server}, file={xml_file}, topic={TOPIC}')

with open(xml_file, 'rb') as fh:
    xml_bytes = fh.read()

producer = Producer({'bootstrap.servers': kafka_server})
producer.produce(TOPIC, value=xml_bytes)
outstanding = producer.flush(timeout=15)
if outstanding > 0:
    print(f'ERROR: {outstanding} messages not delivered')
    sys.exit(1)

print(f'send_isdc: delivered {len(xml_bytes)} bytes to topic {TOPIC!r}')
