"""
By-example publish mapper for Kafka topic order_shipping (Req §4).

Output shape driven by message_formats/order_shipping.json:
  order_id       ← Order.id                    (auto-match, renamed via FIELD_EXCEPTIONS)
  order_date     ← Order.CreatedOn              (dot-notation not needed, simple rename)
  customer_name  ← Order.customer.name          (dot-notation join)
  total          ← Order.amount_total           (rename)
  items          ← Order.ItemList (child list)
    quantity     ← Item.quantity                (auto-match)
    product_name ← Item.product.name            (dot-notation join)
    unit_price   ← Item.unit_price               (auto-match)
"""

from integration.system.EaiPublishMapper import serialize_row

SAMPLE = {
    "order_id": 1,
    "order_date": "2026-04-06",
    "customer_name": "Alfreds Futterkiste",
    "total": 100.00,
    "items": [
        {"quantity": 2, "product_name": "Chai", "unit_price": 25.00}
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
    return serialize_row(row, sample=SAMPLE, exceptions=FIELD_EXCEPTIONS)
