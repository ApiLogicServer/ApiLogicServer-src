"""
Feature: Kafka Publish Shipping Notification

  Scenario: Notify shipping when an order is dispatched
    Given an Order exists
    When date_shipped is set
    Then publish to Kafka topic order_shipping
    And use message_formats/order_shipping.json as the message shape
    And use by-example publish rather than key-only publish
"""

from integration.system.EaiPublishMapper import serialize_row

SAMPLE = {
    "order_id": 1,
    "order_date": "2026-04-06",
    "customer_name": "Alfreds Futterkiste",
    "total": 100.00,
    "items": [
        {"quantity": 2, "product_name": "Chai", "unit_price": 25.00}
    ]
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
    """Order mapper: serializes an Order and its ItemList into the order_shipping by-example message shape."""
    return serialize_row(row, sample=SAMPLE, exceptions=FIELD_EXCEPTIONS)

