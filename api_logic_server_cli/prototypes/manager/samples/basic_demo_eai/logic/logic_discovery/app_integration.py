"""
App Integration — Kafka Publish on Order Dispatch
==================================================
Req §4: Publish to 'order_shipping' topic when Order.date_shipped is set.

Uses by-example publish (mapper=order_shipping) so the full order shape
is sent (customer_name, items, total) rather than just the primary key.

Guard condition fires on:
  INSERT with date_shipped set, OR
  UPDATE where date_shipped changed from None to a value.
"""
from logic_bank.logic_bank import Rule
from logic_bank.exec_row_logic.logic_row import LogicRow
import database.models as models
import integration.kafka.kafka_producer as kafka_producer


def _send_order_to_kafka(row: models.Order, old_row: models.Order, logic_row: LogicRow):
    if row.date_shipped is not None and row.date_shipped != old_row.date_shipped:
        from integration.kafka.kafka_publish_discovery import order_shipping
        kafka_producer.publish_kafka_message(
            topic='order_shipping',
            logic_row=logic_row,
            mapper=order_shipping,
        )


def declare_logic():
    Rule.after_flush_row_event(on_class=models.Order, calling=_send_order_to_kafka)
