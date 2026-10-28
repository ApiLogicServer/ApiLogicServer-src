"""
Feature: Kafka Subscribe Order Integration

  Scenario: Accept inbound orders from sales channel
    Given an inbound order message in JSON format (message_formats/order_b2b.json)
    When the message is received from Kafka topic order_b2b
    Then map Account to Customer by name
    And map Items.Name to Product by name
    And map Items.QuantityOrdered to Item.quantity

Order mapper: parses inbound order_b2b JSON payloads into Order and Item model instances.
"""

import json
from database import models
from integration.system.EaiSubscribeMapper import populate_row_from_dict

_PARENT_EXCEPTIONS = {
    "Account": None,
    "Items": None,
}

_CHILD_EXCEPTIONS = {
    "Name": None,
    "QuantityOrdered": "quantity",
}


def parse(payload: str, exceptions: dict = None) -> tuple:
    """Order mapper: parses inbound order_b2b JSON into (Order, list[Item]) model instances."""
    data = json.loads(payload)

    parent_row = models.Order()
    populate_row_from_dict(parent_row, data, exceptions=_PARENT_EXCEPTIONS)

    child_rows = []
    for item_dict in data.get("Items", []):
        child_row = models.Item()
        populate_row_from_dict(child_row, item_dict, exceptions=_CHILD_EXCEPTIONS)
        child_rows.append(child_row)

    return parent_row, child_rows
