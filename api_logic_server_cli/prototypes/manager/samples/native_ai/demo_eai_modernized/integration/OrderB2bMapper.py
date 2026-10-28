"""
Feature: Order B2B Intake

Mapper for inbound partner orders (topic order_b2b and REST POST /OrderB2B): partner payload -> Order + Items.

Both channels build the order here, so they validate and resolve lookups identically:
  ValueError  (bad payload)   -> HTTP 400
  LookupError (unknown Account / product Name) -> HTTP 422
"""
import json
from datetime import date

from database import models
from integration.system.EaiSubscribeMapper import populate_row_from_dict, resolve_lookups

PARENT_LOOKUPS = [(models.Customer, models.Customer.name, 'Account', 'customer_id')]
CHILD_LOOKUPS = [(models.Product, models.Product.name, 'Name', 'product_id')]
CHILD_KEY = 'Items'

_PARENT_EXCEPTIONS = {
    "Account": None,   # name -> FK, resolved by resolve_lookups
    "Items": None,     # child array, processed separately
}
_CHILD_EXCEPTIONS = {
    "Name": None,                    # name -> FK, resolved by resolve_lookups
    "QuantityOrdered": "quantity",   # remap to model column
}


def validate(data) -> None:
    """ Raises ValueError unless the payload has an Account and a non-empty Items list of positive integer quantities """
    if not isinstance(data, dict):
        raise ValueError("payload must be a JSON object")
    if not isinstance(data.get("Account"), str) or not data["Account"].strip():
        raise ValueError("Account is required")
    items = data.get(CHILD_KEY)
    if not isinstance(items, list) or len(items) == 0:
        raise ValueError("Items must be a non-empty list")
    for each in items:
        if not isinstance(each, dict) or not isinstance(each.get("Name"), str) or not each["Name"].strip():
            raise ValueError("each item needs a Name")
        qty = each.get("QuantityOrdered")
        if isinstance(qty, bool) or not isinstance(qty, int) or qty <= 0:
            raise ValueError(f"QuantityOrdered must be a positive integer (item {each.get('Name')})")


def parse(payload: str) -> tuple:
    """ Returns (order_row, list[item_row]) - plain model rows, no database access, lookups not yet resolved """
    data = json.loads(payload)
    validate(data)
    order_row = models.Order()
    populate_row_from_dict(order_row, data, exceptions=_PARENT_EXCEPTIONS)
    item_rows = []
    for item_dict in data[CHILD_KEY]:
        item_row = models.Item()
        populate_row_from_dict(item_row, item_dict, exceptions=_CHILD_EXCEPTIONS)
        item_rows.append(item_row)
    return order_row, item_rows


def build_order(payload: str, session) -> models.Order:
    """ Parse, resolve the Account and product Names, attach the items to the order; the caller adds and commits """
    order_row, item_rows = parse(payload)
    raw = json.loads(payload)
    try:
        resolve_lookups(order_row, raw, PARENT_LOOKUPS, session)
        for item_row, item_src in zip(item_rows, raw[CHILD_KEY]):
            resolve_lookups(item_row, item_src, CHILD_LOOKUPS, session)
            order_row.ItemList.append(item_row)   # attach via the relationship, not session.add(item)
    except ValueError as e:
        raise LookupError(str(e)) from e
    order_row.CreatedOn = date.today()
    return order_row
