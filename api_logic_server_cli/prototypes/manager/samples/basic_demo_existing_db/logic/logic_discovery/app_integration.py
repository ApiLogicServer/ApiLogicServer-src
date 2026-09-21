from logic_bank.logic_bank import Rule
from logic_bank.exec_row_logic.logic_row import LogicRow
from integration.kafka import kafka_producer
from database import models


def send_order_to_kafka(row: models.Order, old_row: models.Order, logic_row: LogicRow):
    """Order event: publish to Kafka topic 'order_shipping' when date_shipped is set
    and differs from its prior value (old_row is None on insert)."""
    if row.date_shipped is not None and (old_row is None or row.date_shipped != old_row.date_shipped):
        kafka_producer.publish_kafka_message(
            topic="order_shipping",
            logic_row=logic_row)


def declare_logic():
    """
    Use case: App Integration
        1. Publish the Order to Kafka topic 'order_shipping' when the date_shipped becomes not None.
    """

    Rule.after_flush_row_event(on_class=models.Order, calling=send_order_to_kafka)
