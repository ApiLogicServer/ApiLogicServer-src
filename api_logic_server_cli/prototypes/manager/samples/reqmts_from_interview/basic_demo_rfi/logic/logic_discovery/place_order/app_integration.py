"""
Feature: App Integration
    1. Publish the Order to Kafka topic 'order_shipping' when the date_shipped becomes not None.
"""

from logic_bank.logic_bank import Rule
from logic_bank.exec_row_logic.logic_row import LogicRow
import integration.kafka.kafka_producer as kafka_producer
from integration.kafka.kafka_publish_discovery import order_shipping
from database import models


def declare_logic():
    """Business logic rules for the App Integration use case."""

    def _send_order_to_kafka(row: models.Order, old_row: models.Order, logic_row: LogicRow):
        """Order publish: sends the Order to Kafka topic order_shipping when date_shipped changes from None
        to a value (insert with a value counts); later edits to a shipped Order do not republish."""
        date_shipped = row.date_shipped
        was_shipped = old_row is not None and old_row.date_shipped is not None
        if date_shipped is not None and not was_shipped:
            kafka_producer.publish_kafka_message(topic="order_shipping", logic_row=logic_row, mapper=order_shipping)

    Rule.after_flush_row_event(on_class=models.Order, calling=_send_order_to_kafka)
