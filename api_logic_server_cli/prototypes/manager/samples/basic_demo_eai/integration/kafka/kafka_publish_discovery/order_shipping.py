"""
Kafka Publish Mapper — order_shipping topic
============================================
Req §4: By-example publish mapper for the order_shipping topic.

Message shape (message_formats/order_shipping.json):
    {
      "order_id": 1,
      "order_date": "2026-04-06",
      "customer_name": "Alfreds Futterkiste",
      "total": 100.00,
      "items": [
        { "quantity": 2, "product_name": "Chai", "unit_price": 25.00 }
      ]
    }

FIELD_EXCEPTIONS resolution (see EaiPublishMapper.serialize_row docstring):
  order_id      → simple rename → Order.id
  order_date    → simple rename → Order.CreatedOn
  customer_name → dot-notation  → Order.customer.name  (via SQLAlchemy relationship)
  total         → simple rename → Order.amount_total
  items         → child list    → Order.ItemList        (relationship name on Order)
  product_name  → dot-notation  → Item.product.name    (same exceptions dict reused for children)
  quantity      → auto-match    → Item.quantity
  unit_price    → auto-match    → Item.unit_price
"""
from integration.system.EaiPublishMapper import serialize_row

SAMPLE = {
    "order_id":      1,
    "order_date":    "2026-04-06",
    "customer_name": "Alfreds Futterkiste",
    "total":         100.00,
    "items": [
        {"quantity": 2, "product_name": "Chai", "unit_price": 25.00}
    ],
}

FIELD_EXCEPTIONS = {
    "order_id":      "id",
    "order_date":    "CreatedOn",
    "customer_name": "customer.name",
    "total":         "amount_total",
    "items":         "ItemList",      # child collection → SQLAlchemy relationship name
    "product_name":  "product.name",  # also used when serializing child Item rows
}


def row_to_dict(row) -> dict:
    """Serialize an Order row to the order_shipping message shape."""
    return serialize_row(row, sample=SAMPLE, exceptions=FIELD_EXCEPTIONS)
