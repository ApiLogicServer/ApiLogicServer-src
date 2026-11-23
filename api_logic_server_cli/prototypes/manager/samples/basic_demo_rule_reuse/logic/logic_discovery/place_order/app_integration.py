"""
Use case: App Integration
    1. Publish the Order to Kafka topic 'order_shipping' when the date_shipped becomes not None.

version: 1.0
created: 2026-11-22T08:55:00
created_by: claude-opus-5-5 (valjhuber@gmail.com)
"""

from logic_bank.logic_bank import Rule
from database import models
from integration.kafka import kafka_producer


def declare_logic():
    """Business logic rules for App Integration use case."""

    Rule.after_flush_row_event(on_class=models.Order, calling=kafka_producer.send_row_to_kafka, when_condition=lambda row: row.date_shipped is not None, with_args={"topic": "order_shipping"}, name="shipping_publish")
