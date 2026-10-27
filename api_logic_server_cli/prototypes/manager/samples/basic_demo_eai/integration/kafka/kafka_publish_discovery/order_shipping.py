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

# Message shape, copied from docs/requirements/demo_eai/message_formats/order_shipping.json
SAMPLE = {
    "order_id": 1,
    "order_date": "2026-04-06",
    "customer_name": "Alfreds Futterkiste",
    "total": 100.00,
    "items": [
        {"quantity": 2, "product_name": "Chai", "unit_price": 25.00}
    ]
}

# sample key -> model attribute (plain), "Relationship.column" (join), or relationship name (child list)
FIELD_EXCEPTIONS = {
    "order_id": "id",
    "order_date": "CreatedOn",
    "customer_name": "customer.name",
    "total": "amount_total",
    "items": "ItemList",
    "product_name": "product.name",
}


def row_to_dict(row) -> dict:
    """Order mapper: shapes an Order like order_shipping.json (by-example publish)."""
    return serialize_row(row, sample=SAMPLE, exceptions=FIELD_EXCEPTIONS)
