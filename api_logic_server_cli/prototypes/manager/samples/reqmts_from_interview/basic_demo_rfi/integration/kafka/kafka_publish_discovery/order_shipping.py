"""
Feature: App Integration
    1. Publish the Order to Kafka topic 'order_shipping' when the date_shipped becomes not None.

Order shipping mapper: shapes the Order (with its customer name and Items) as the message in
integration/kafka/message_formats/order_shipping.json.
"""

from integration.system.EaiPublishMapper import serialize_row

SAMPLE = {
    "order_id": 1,
    "order_date": "2026-11-05",
    "customer_name": "Alice",
    "total": 100.00,
    "items": [
        {"quantity": 2, "product_name": "Widget", "unit_price": 25.00, "discount_amount": 0.00, "amount": 50.00}
    ],
}

FIELD_EXCEPTIONS = {
    "order_id": "id",
    "order_date": "CreatedOn",
    "customer_name": "customer.name",
    "total": "amount_total",
    "items": "ItemList",
    "product_name": "product.name",
}


def row_to_dict(row):
    """Order mapper: maps an Order row to the order_shipping message dict."""
    return serialize_row(row, sample=SAMPLE, exceptions=FIELD_EXCEPTIONS)
