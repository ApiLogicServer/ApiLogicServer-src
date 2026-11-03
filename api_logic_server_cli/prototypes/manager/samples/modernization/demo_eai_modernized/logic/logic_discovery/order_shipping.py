"""
Feature: Order Shipping Notification

* **Shipping Trigger**: When an `Order` is created with a non-null `date_shipped` or updated so `date_shipped` transitions to a non-null date, an outbound message is queued in a session outbox.
* **Transactional Outbox Delivery**: Messages are only published in `after_commit` and discarded in `after_rollback`, preventing phantom notifications on failed transactions.
* **Payload Format**: `_shipping_message` publishes to the `order_shipping` topic with:
  ```json
  {
    "order_id": 1,
    "order_date": "YYYY-MM-DD",
    "customer_name": "...",
    "total": 123.45,
    "items": [{"quantity": 2, "product_name": "...", "unit_price": 61.725}]
  }
  ```
* **Simulated vs. Live Broker Mode**: `publish` always records messages in the in-memory `published` list (inspectable via `GET /kafka_log`) and additionally produces to a live Kafka broker when `KAFKA_SERVER` is configured.
"""

from logic_bank.logic_bank import Rule
from logic_bank.exec_row_logic.logic_row import LogicRow
from database import models
from integration.kafka import kafka_producer
from integration.kafka.kafka_publish_discovery import order_shipping as order_shipping_mapper


def send_order_shipping(row: models.Order, old_row: models.Order, logic_row: LogicRow):
    """ Order event: publish to topic order_shipping when date_shipped is set on insert or changes to a non-null date
    (old_row is None on insert).  Runs after the flush, so the Order id and its items are final. """
    if row.date_shipped is not None and (old_row is None or row.date_shipped != old_row.date_shipped):
        kafka_producer.publish_kafka_message(topic="order_shipping", logic_row=logic_row,
                                             mapper=order_shipping_mapper)


def declare_logic():
    Rule.after_flush_row_event(on_class=models.Order, calling=send_order_shipping)
