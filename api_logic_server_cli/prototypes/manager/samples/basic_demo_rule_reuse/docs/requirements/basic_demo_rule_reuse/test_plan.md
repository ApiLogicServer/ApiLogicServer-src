# Test Plan — basic_demo_rule_reuse

Coverage plan written before any test file (testing.md, Step 2b). One row per rule; Features are named per requirement.
Test data: each scenario creates its own Customer(s) (timestamped names) and uses Products Gadget (150) and Widget (90).

| Requirement (Feature) | Rule | Planned scenarios | Scenario(s) written |
|---|---|---|---|
| Check Credit | `Item.unit_price` — Rule.copy | create (copied from Product); change Item's product (re-copied) | Order with Item is created; Item product is changed |
| Check Credit | `Item.amount` — Rule.formula (quantity * unit_price) | change quantity; change unit_price (via product change) | Item quantity is changed; Item product is changed |
| Check Credit | `Order.amount_total` — Rule.sum | create item; change item amount; delete item; move item to another Order (both adjust) | Order with Item is created; Item quantity is changed; Item is deleted; Item is moved to another Order |
| Check Credit | `Customer.balance` — Rule.sum where date_shipped is None | create order; change amount; delete order; Order **leaves** the set (shipped); Order **enters** the set (unshipped); move Order to another Customer — in Move Order Check Credit | Order with Item is created; Item quantity is changed; Order is deleted; Shipped Order leaves the balance; Unshipped Order re-enters the balance; (move) Moving an Order adjusts both balances |
| Check Credit | `Customer.credit_limit_check` — Rule.constraint (balance <= credit_limit) | accepted; accepted at boundary (balance == limit); rejected (balance unchanged) | Order within the credit limit is accepted; Order exactly at the credit limit is accepted; Order over the credit limit is rejected |
| App Integration | `Order.shipping_publish` — after_flush_row_event, when_condition | fires when date_shipped becomes set; does NOT fire on edit of an unshipped Order; does NOT fire again on edit of a shipped Order | Shipping an Order publishes it; Editing an unshipped Order does not publish; Editing a shipped Order does not publish again |
| Move Order Check Credit (Uses: Customer.balance, Customer.credit_limit_check) | reused rules | move Order to another Customer: both balances adjust; move to a Customer that would exceed the limit: rejected, both balances unchanged | Moving an Order adjusts both balances; Moving an Order over the new Customer's limit is rejected |

**Close-out:** every row has a scenario; 0 rows NOT covered. 16 scenarios in 3 Features (`check_credit.feature`, `app_integration.feature`, `move_order_check_credit.feature`).
