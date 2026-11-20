"""
Feature: Kafka Subscribe Order Integration

  Scenario: Accept inbound orders from sales channel
    Given an inbound order message in JSON format (message_formats/order_b2b.json)
    When the message is received from Kafka topic order_b2b
    Then map Account to Customer by name
    And map Items.Name to Product by name
    And map Items.QuantityOrdered to Item.quantity

Order mapper for the Kafka topic order_b2b (JSON): turns one message into an Order with its Items.

3-tier contract (integration/system/EaiSubscribeMapper.py): Tier 1 by name, Tier 2 the exceptions below.
Name -> FK lookups (Account -> Customer, Name -> Product) are resolved after parse() by the topic handler.
"""
import json
from database import models
from integration.system.EaiSubscribeMapper import populate_row_from_dict

_PARENT_EXCEPTIONS = {
    "Account": None,   # name -> FK resolved by resolve_lookups
    "Items":   None,   # child array, processed below
}

_CHILD_EXCEPTIONS = {
    "Name":            None,         # name -> FK resolved by resolve_lookups
    "QuantityOrdered": "quantity",   # remap to the model column
}


def parse(payload: str, exceptions: dict = None) -> tuple:
    """Order mapper: returns (order_row, list[item_row]) - plain model rows, NOT (row, src_dict) tuples."""
    data = json.loads(payload)
    order_row = models.Order()
    populate_row_from_dict(order_row, data, exceptions=_PARENT_EXCEPTIONS)
    item_rows = []
    for item_dict in data.get('Items', []):
        item_row = models.Item()
        populate_row_from_dict(item_row, item_dict, exceptions=_CHILD_EXCEPTIONS)
        item_rows.append(item_row)
    return order_row, item_rows
