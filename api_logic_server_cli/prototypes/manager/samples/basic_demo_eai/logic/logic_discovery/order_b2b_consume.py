"""
Feature: Kafka Subscribe Order Integration

  Scenario: Accept inbound orders from sales channel
    Given an inbound order message in JSON format (message_formats/order_b2b.json)
    When the message is received from Kafka topic order_b2b
    Then map Account to Customer by name
    And map Items.Name to Product by name
    And map Items.QuantityOrdered to Item.quantity

version: 1.0
created: 2026-10-24
created_by: claude-sonnet-5-5 (valjhuber@gmail.com)
"""

from logic_bank.logic_bank import Rule
from logic_bank.exec_row_logic.logic_row import LogicRow
from database import models


def _publish_order_b2b(row: models.OrderB2bMessage, old_row: models.OrderB2bMessage, logic_row: LogicRow):
    """OrderB2bMessage event: publishes the raw blob to topic order_b2b_processed after Tx 1 commits, so
    Consumer 2 can parse it in a clean Tx 2 (2-message pattern)."""
    if not logic_row.is_inserted() or not row.payload:
        return
    if row.is_processed:
        # debug path: the blob was created with is_processed=True after Tx 2 already ran inline - do not re-publish
        logic_row.log(f"_publish_order_b2b: skipping re-publish - blob.id={row.id} already is_processed=True (debug path)")
        return
    import integration.kafka.kafka_producer as kafka_producer
    if not kafka_producer.kafka_available():
        logic_row.log("_publish_order_b2b: Kafka not configured or broker not reachable - skipping publish")
        return
    kafka_producer.producer.produce(topic='order_b2b_processed', key=str(row.id), value=row.payload.encode('utf-8'))
    kafka_producer.producer.flush(timeout=10)


def declare_logic():
    """Row-event bridge for the Kafka Subscribe Order Integration use case."""
    Rule.after_flush_row_event(on_class=models.OrderB2bMessage, calling=_publish_order_b2b)
