"""
Feature: Kafka Publish Shipping Notification

  Scenario: Notify shipping when an order is dispatched
    Given an Order exists
    When date_shipped is set
    Then publish to Kafka topic order_shipping
    And use message_formats/order_shipping.json as the message shape
    And use by-example publish rather than key-only publish

version: 1.0
created: 2026-10-24
created_by: claude-sonnet-5-5 (valjhuber@gmail.com)
"""

from logic_bank.logic_bank import Rule
from logic_bank.exec_row_logic.logic_row import LogicRow
from database import models
from integration.kafka import kafka_producer
from integration.kafka.kafka_publish_discovery import order_shipping


def _send_order_to_shipping(row: models.Order, old_row: models.Order, logic_row: LogicRow):
    """Order event: publishes the Order to Kafka topic order_shipping (by-example, shape from
    message_formats/order_shipping.json) when date_shipped is first set (old_row is None on insert)."""
    if row.date_shipped is not None and (old_row is None or row.date_shipped != old_row.date_shipped):
        kafka_producer.publish_kafka_message(topic="order_shipping", logic_row=logic_row, mapper=order_shipping)


def declare_logic():
    """Kafka publish rule for the Kafka Publish Shipping Notification use case."""
    Rule.after_flush_row_event(on_class=models.Order, calling=_send_order_to_shipping)
