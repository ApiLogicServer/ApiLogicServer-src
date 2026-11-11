# Test plan: demo_ai_rules_supplier

AI choice is not deterministic: tests assert the chosen supplier is one of the product's suppliers and that an audit row exists, never a specific supplier. Each scenario creates fresh data (timestamped names).

| Rule | Requirement | Scenarios | Covered by |
|---|---|---|---|
| Customer.balance <= credit_limit (constraint) | Check Credit | accepted; accepted at boundary (balance == limit); rejected | TBD |
| Customer.balance = sum(Order.amount_total where date_shipped is null) | Check Credit | create child; change; delete; move item to another order/customer; ship (leaves where); unship (enters where) | TBD |
| Order.amount_total = sum(Item.amount) | Check Credit | create item; change quantity; delete item; move item to another order | TBD |
| Item.amount = quantity * unit_price | Check Credit | change quantity | TBD |
| Product.count_suppliers = count(ProductSupplier) | Check Credit | add supplier; delete supplier | TBD |
| AI event: Item.unit_price from SysSupplierReq | Check Credit | product with suppliers: audit row exists, linked to Item, chosen supplier is one of the product's suppliers, unit_price equals chosen price; product with no suppliers: Product.unit_price copied, no audit row | TBD |
| Order published to Kafka 'order_shipping' when date_shipped set | App Integration | fires when date_shipped becomes set; does NOT fire when not shipped | TBD |

- NOT covered: 0 rows (Kafka broker delivery not exercised: simulated mode)
