# Test plan - demo_ai_rules_supplier

One Feature per requirement ("Check Credit", "App Integration"). The AI choice is not deterministic, so AI scenarios
assert that the chosen supplier is one of the product's suppliers and that an audit row exists, never a specific supplier.
Every scenario builds fresh data (unique names), so the suite is repeatable.

| # | Rule | Scenarios planned | Scenario written |
|---|---|---|---|
| 1 | `Customer.balance <= credit_limit` (constraint) | accepted; accepted at the boundary (equality); rejected | |
| 2 | `Customer.balance` = sum(Order.amount_total where date_shipped is None) | create order; ship it (leaves the where); un-ship it (re-enters); delete; move order to another customer | |
| 3 | `Order.amount_total` = sum(Item.amount) | create item; change quantity; delete item; move item to another order | |
| 4 | `Item.amount` = quantity * unit_price | change quantity; change product (unit_price re-derived) | |
| 5 | `Product.count_suppliers` = count(ProductSupplier) | add a supplier; delete a supplier; move a ProductSupplier to another product | |
| 6 | Item.unit_price by AI (early event, Request Pattern) | product with suppliers: chosen supplier is one of them, audit row exists, unit_price = chosen price; product without suppliers: copied from Product.unit_price, no audit row; change product on an item re-selects | |
| 7 | Publish Order to Kafka 'order_shipping' if date_shipped is not None | fires when date_shipped is set; does NOT fire for an unshipped order | |

## Close-out

| # | Scenario(s) written | Feature |
|---|---|---|
| 1 | Credit - within limit; Credit - at the limit; Credit - over the limit | Check Credit |
| 2 | Balance - ship and unship (leaves and re-enters the where); Balance - move order; Balance - delete order; create: Credit - within limit | Check Credit |
| 3 | Credit - within limit (create); Item - change quantity; Item - delete; Item - move to order | Check Credit |
| 4 | Item - change quantity; Item - change product | Check Credit |
| 5 | Suppliers - add and remove; Suppliers - move | Check Credit |
| 6 | AI - no suppliers; AI - chooses a supplier; AI - product change | Check Credit |
| 7 | Kafka - shipped order; Kafka - unshipped order | App Integration |

NOT covered: 0 rows. Notes: Kafka is checked from the logic log (simulated mode: the broker is not enabled), which proves the
message is produced, not delivery. "Order delete" removes the item first, then the order.
