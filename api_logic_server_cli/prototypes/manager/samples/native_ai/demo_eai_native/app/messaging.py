"""Kafka publish. Every message is recorded in `published`; it is sent to the broker only when one is configured."""
import json
import logging

log = logging.getLogger("messaging")

published = []  # (topic, message) in send order; inspected by tests and /kafka_log
_producer = None


def configure(server):
    global _producer
    if server:
        from confluent_kafka import Producer
        _producer = Producer({"bootstrap.servers": server})
    else:
        _producer = None


def mode():
    return "live" if _producer else "simulated"


def publish(topic, message):
    published.append((topic, message))
    if _producer:
        _producer.produce(topic, json.dumps(message).encode())
        if _producer.flush(10):
            log.error("kafka: message to %s not delivered", topic)
