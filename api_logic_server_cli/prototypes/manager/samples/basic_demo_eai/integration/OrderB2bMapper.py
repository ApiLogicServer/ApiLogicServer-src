import json
from database import models
from integration.system.EaiSubscribeMapper import populate_row_from_dict

# Exceptions for Order-level fields
_ORDER_EXCEPTIONS = {
    "Account": None,   # handled by resolve_lookups — no column to map to
    "Items":   None,   # child array — processed separately
}

# Exceptions for Item-level fields
_ITEM_EXCEPTIONS = {
    "Name":           None,         # handled by resolve_lookups
    "QuantityOrdered": "quantity",  # remap to model column
}


def parse(payload: str, exceptions: dict = None) -> tuple:
    """Parse order_b2b JSON payload → (order_row, item_rows).

    Returns:
        (models.Order, list[models.Item]) — unpopulated FKs are resolved
        by the caller via resolve_lookups() after this call returns.
    """
    data = json.loads(payload)

    order_row = models.Order()
    populate_row_from_dict(order_row, data, exceptions=_ORDER_EXCEPTIONS)

    item_rows = []
    for item_dict in data.get('Items', []):
        item_row = models.Item()
        populate_row_from_dict(item_row, item_dict, exceptions=_ITEM_EXCEPTIONS)
        item_rows.append(item_row)

    return order_row, item_rows


    return order, item_pairs
