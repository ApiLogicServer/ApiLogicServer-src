"""
Send one CIMCorp shipment XML to the isdc Kafka topic (live Kafka test).

Requires Kafka running and KAFKA_SERVER set in config/default.env.
Run from project root: python test/send_isdc.py

Uses confluent_kafka.Producer directly (NOT docker exec kafka-console-producer
which breaks multi-line XML by treating each line as a separate message).
"""
import os
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


def load_env():
    env_path = PROJECT_ROOT / 'config' / 'default.env'
    env = {}
    for line in env_path.read_text().splitlines():
        line = line.strip()
        if line.startswith('#') or '=' not in line:
            continue
        key, _, val = line.partition('=')
        env[key.strip()] = val.strip().strip('"')
    return env


def main():
    env = load_env()
    kafka_server = env.get('KAFKA_SERVER', 'localhost:9092')

    try:
        from confluent_kafka import Producer
    except ImportError:
        print("ERROR: confluent_kafka not installed. Run: pip install confluent-kafka")
        sys.exit(1)

    sample_file = PROJECT_ROOT / 'docs' / 'requirements' / 'customs_demo' / 'message_formats' / 'MDE-CDV-HVS-WR-Rev260328.xml'
    payload = sample_file.read_text(encoding='utf-8')

    producer = Producer({'bootstrap.servers': kafka_server})

    def delivery_report(err, msg):
        if err:
            print(f"Delivery failed: {err}")
        else:
            print(f"Delivered to {msg.topic()} [{msg.partition()}] offset={msg.offset()}")

    producer.produce('isdc', value=payload.encode('utf-8'), callback=delivery_report)
    producer.flush(timeout=15)
    print(f"Sent {len(payload)} bytes to topic 'isdc' via {kafka_server}")


if __name__ == '__main__':
    main()
