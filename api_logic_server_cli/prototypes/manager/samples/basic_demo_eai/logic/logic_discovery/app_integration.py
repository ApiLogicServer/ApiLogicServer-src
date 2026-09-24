"""
Feature: Kafka Publish Shipping Notification

  Scenario: Notify shipping when an order is dispatched
    Given an Order exists
    When date_shipped is set
    Then publish to Kafka topic order_shipping
    And use message_formats/order_shipping.json as the message shape
    And use by-example publish rather than key-only publish
"""

from logic_bank.logic_bank import Rule
from logic_bank.exec_row_logic.logic_row import LogicRow
import database.models as models
import integration.kafka.kafka_producer as kafka_producer


def _send_order_to_kafka(row: models.Order, old_row: models.Order, logic_row: LogicRow):
    if row.date_shipped is not None and (old_row is None or row.date_shipped != old_row.date_shipped):
        from integration.kafka.kafka_publish_discovery import order_shipping
        kafka_producer.publish_kafka_message(
            topic='order_shipping',
            logic_row=logic_row,
            mapper=order_shipping,
        )


def declare_logic():
    Rule.after_flush_row_event(on_class=models.Order, calling=_send_order_to_kafka)
