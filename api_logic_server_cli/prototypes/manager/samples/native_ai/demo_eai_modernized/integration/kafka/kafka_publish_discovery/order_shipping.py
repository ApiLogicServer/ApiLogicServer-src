"""
Feature: Order Shipping Notification

Publish mapper for topic order_shipping (message shape: docs/requirements/demo_eai/message_formats/order_shipping.json).

Used by logic/logic_discovery/order_shipping.py via kafka_producer.publish_kafka_message(..., mapper=this module).
"""
from integration.system.EaiPublishMapper import serialize_row

SAMPLE = {
    "order_id": 1,
    "order_date": "2023-02-22",
    "customer_name": "Bob",
    "total": 300,
    "items": [{"quantity": 2, "product_name": "Gadget", "unit_price": 150}]
}

FIELD_EXCEPTIONS = {
    "order_id": "id",
    "order_date": "CreatedOn",
    "customer_name": "customer.name",
    "total": "amount_total",
    "items": "ItemList",
    "product_name": "product.name",
}


def row_to_dict(row) -> dict:
    """ Order row -> the order_shipping message """
    return serialize_row(row, sample=SAMPLE, exceptions=FIELD_EXCEPTIONS)
