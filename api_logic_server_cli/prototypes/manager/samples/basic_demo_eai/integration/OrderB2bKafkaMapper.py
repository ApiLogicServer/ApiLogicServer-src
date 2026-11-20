"""
Feature: Kafka Subscribe Order Integration

  Scenario: Accept inbound orders from sales channel
    Given an inbound order message in JSON format (message_formats/order_b2b.json)
    When the message is received from Kafka topic order_b2b
    Then map Account to Customer by name
    And map Items.Name to Product by name
    And map Items.QuantityOrdered to Item.quantity

Order mapper (Kafka topic order_b2b): parses the JSON message into an Order and its Items.
Lookups (Account -> Customer, Items.Name -> Product) are resolved by the topic handler, not here.
"""
import json

from database import models
from integration.system.EaiSubscribeMapper import populate_row_from_dict

# Parent-level fields: None = skip (name -> FK resolved by resolve_lookups, or the child array)
_PARENT_EXCEPTIONS = {
    "Account": None,
    "Items": None,
}

# Child-level fields: None = skip, str = remap to model column
_CHILD_EXCEPTIONS = {
    "Name": None,
    "QuantityOrdered": "quantity",
}


def parse(payload: str, exceptions: dict = None) -> tuple:
    """Order mapper: returns (Order, list[Item]) from the order_b2b JSON message - plain model rows, no lookups."""
    data = json.loads(payload)

    order = models.Order()
    populate_row_from_dict(order, data, exceptions=_PARENT_EXCEPTIONS)   # Notes -> notes (Tier 1)

    items = []
    for item_dict in data.get('Items', []):
        item = models.Item()
        populate_row_from_dict(item, item_dict, exceptions=_CHILD_EXCEPTIONS)
        items.append(item)
    return order, items
