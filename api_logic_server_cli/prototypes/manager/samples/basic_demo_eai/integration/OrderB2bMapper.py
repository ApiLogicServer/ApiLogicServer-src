"""
JSON → Order + Items mapper for Kafka topic order_b2b / Custom API OrderB2B.

parse() returns (order_row, item_rows) — plain model rows, never (row, src_dict)
tuples. The caller zips item_rows with the raw payload's Items array to call
resolve_lookups() per item (Account/Items.Name are FK lookups, not columns).
"""
from database import models
from integration.system.EaiSubscribeMapper import populate_row_from_dict

# Account (FK lookup) and Items (child array) are resolved outside Tier 1/2 mapping
_PARENT_EXCEPTIONS = {
    "Account": None,
    "Items": None,
}

_CHILD_EXCEPTIONS = {
    "Name": None,                    # name→FK resolved by resolve_lookups
    "QuantityOrdered": "quantity",   # remap to model column
}


def parse(payload: str) -> tuple:
    """Returns (order_row, list[Item]) — plain model rows, NOT (row, src_dict) tuples."""
    import json
    data = json.loads(payload)

    order_row = models.Order()
    populate_row_from_dict(order_row, data, exceptions=_PARENT_EXCEPTIONS)

    item_rows = []
    for item_dict in data.get('Items', []):
        item_row = models.Item()
        populate_row_from_dict(item_row, item_dict, exceptions=_CHILD_EXCEPTIONS)
        item_rows.append(item_row)

    return order_row, item_rows
