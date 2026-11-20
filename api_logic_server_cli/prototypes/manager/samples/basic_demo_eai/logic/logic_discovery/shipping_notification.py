"""
Feature: Kafka Publish Shipping Notification

  Scenario: Notify shipping when an order is dispatched
    Given an Order exists
    When date_shipped is set
    Then publish to Kafka topic order_shipping
    And use message_formats/order_shipping.json as the message shape
    And use by-example publish rather than key-only publish

version: 1.0
created: 2026-11-19T19:00:00
created_by: claude-opus-5-5 (valjhuber@gmail.com)
"""

from logic_bank.exec_row_logic.logic_row import LogicRow
from logic_bank.logic_bank import Rule
from database import models
from integration.kafka import kafka_producer
from integration.kafka.kafka_publish_discovery import order_shipping


def _send_order_to_shipping(row: models.Order, old_row: models.Order, logic_row: LogicRow):
    """Order publish: sends the Order to Kafka topic order_shipping when date_shipped is set (insert with a value,
    or an update that changes it), shaped by example from message_formats/order_shipping.json."""
    if row.date_shipped is not None and (old_row is None or row.date_shipped != old_row.date_shipped):
        kafka_producer.publish_kafka_message(topic="order_shipping", logic_row=logic_row, mapper=order_shipping)


def declare_logic():
    """Kafka publish: notify shipping when an order is dispatched."""
    Rule.after_flush_row_event(on_class=models.Order, calling=_send_order_to_shipping)
