"""
Kafka subscribe mapper: topic order_b2b (JSON) -> Order + Items.

Tier 1 maps by lowercase name (Notes -> notes); the exceptions below skip or remap the rest.
Name -> FK lookups (Account -> Customer, Items.Name -> Product) are done by resolve_lookups() in the topic handler.
"""

import json

from database import models
from integration.system.EaiSubscribeMapper import populate_row_from_dict

# parent-level fields: None = skip (handled by resolve_lookups or the child array)
_PARENT_EXCEPTIONS = {
    "Account": None,   # name -> customer_id, resolved by resolve_lookups
    "Items": None,     # child array, processed below
}

# child-level fields: None = skip, str = remap to model column
_CHILD_EXCEPTIONS = {
    "Name": None,                      # name -> product_id, resolved by resolve_lookups
    "QuantityOrdered": "quantity",
}


def parse(payload: str, exceptions: dict = None) -> tuple:
    """Order mapper: returns (order_row, list[Item rows]) - plain model rows, not (row, src_dict) tuples."""
    data = json.loads(payload)

    order_row = models.Order()
    populate_row_from_dict(order_row, data, exceptions=_PARENT_EXCEPTIONS)

    item_rows = []
    for item_dict in data.get("Items", []):
        item_row = models.Item()
        populate_row_from_dict(item_row, item_dict, exceptions=_CHILD_EXCEPTIONS)
        item_rows.append(item_row)

    return order_row, item_rows
