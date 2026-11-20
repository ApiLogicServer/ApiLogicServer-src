# Test Plan — demo_eai

Coverage plan written before any test file (testing.md Step 2b). One row per rule (or requirement clause without a
rule), with the scenarios the coverage matrix requires. The **Scenario** column is filled in at close-out (Step 4d).

Features are named exactly as the `Feature:` lines in `requirements.md` (default names).
Test data is fresh per scenario (timestamped customer names); dashboard checks assert **deltas** on today's
`DailyFlow` bucket, so the suite is repeatable.

## Check Credit (`logic/logic_discovery/check_credit.py`)

| # | Rule | Planned scenarios | Scenario (close-out) |
|---|---|---|---|
| 1 | `Rule.copy` Item.unit_price ← Product.unit_price | create (copied); change the item's product (re-copied) || Good order is priced and added to the balance; Changing an item's product re-copies the price |
| 2 | `Rule.formula` Item.amount = quantity * unit_price | change quantity; change unit_price (via product change) || Changing an item quantity re-derives amount, total and balance; Changing an item's product re-copies the price |
| 3 | `Rule.sum` Order.amount_total = sum(Item.amount) | create item; change item value; delete item; move item to another order (both adjust) || Good order...; Changing an item quantity...; Deleting an item reduces the order total and balance; Moving an item to another order adjusts both orders |
| 4 | `Rule.sum` Customer.balance = sum(Order.amount_total where date_shipped is None) | create order; change (qty); delete order; move order to another customer (both adjust); where leaves (ship); where enters (unship) || Good order...; Changing an item quantity...; Deleting an order reduces the balance; Moving an order to another customer adjusts both balances; Shipping an order removes it from the balance; Unshipping an order adds it back to the balance |
| 5 | `Rule.constraint` balance <= credit_limit | accepted; accepted at the boundary (equal); rejected on create; rejected on update || Good order...; Order exactly at the credit limit is accepted; Order over the credit limit is rejected; Raising a quantity over the credit limit is rejected |

## B2B Order Integration (`api/api_discovery/order_b2b_service.py`, `integration/row_dict_maps/OrderB2BMapper.py`)

| # | Clause | Planned scenarios | Scenario (close-out) |
|---|---|---|---|
| 6 | OrderB2B endpoint; Account → Customer, Items.Name → Product, QuantityOrdered → quantity | accepted order is mapped (customer, products, quantities) || Partner order is mapped and the request recorded as processed |
| 7 | Record each request, with its outcome | accepted request recorded as processed; rejected request (unknown product) recorded with error_text, HTTP 400; unknown account rejected || Partner order is mapped and the request recorded as processed; Partner order with an unknown product is rejected and the request recorded with its error; Partner order for an unknown account is rejected |

## Kafka Subscribe Order Integration (`integration/kafka/kafka_subscribe_discovery/order_b2b.py`, `logic/logic_discovery/order_b2b_consume.py`)

| # | Clause / rule | Planned scenarios | Scenario (close-out) |
|---|---|---|---|
| 8 | order_b2b message → Order (mode-aware: live or simulated) | message for a known customer creates the order, mapped by name || Order message for a known customer creates the order |
| 9 | Lookup failure | message with an unknown product is rejected with the reason || Order message with an unknown product is rejected |
| 10 | `Rule.after_flush_row_event` bridge (Tx 1 → Tx 2) | rejected message leaves a blob with is_processed = 0 and error_text (live Kafka only) || Rejected message stays on the blob with its error (live Kafka only) |

## Kafka Publish Shipping Notification (`logic/logic_discovery/shipping_notification.py`)

| # | Rule | Planned scenarios | Scenario (close-out) |
|---|---|---|---|
| 11 | `Rule.after_flush_row_event` Order, on the date_shipped transition, by-example mapper | fires when date_shipped is set (message has the order_shipping.json shape); does NOT fire on a change that does not set date_shipped || Shipping an order publishes the shipping message; Changing an order without shipping it publishes nothing; Changing an already shipped order does not publish again |

## Row-Level Security (`security/declare_security.py`)

| # | Grant | Planned scenarios | Scenario (close-out) |
|---|---|---|---|
| 12 | sales: credit_limit >= 3000 | visible to sales || Sales sees a customer with a credit limit of 3000 or more |
| 13 | sales: balance > 0 (OR'd) | low limit, balance > 0 → visible; low limit, balance 0 → hidden (but visible to admin) || Sales sees a low-limit customer who has a balance; Sales does not see a low-limit customer with no balance |

## Order Flow Dashboard (`logic/logic_discovery/order_flow_dashboard.py`, `api/api_discovery/dashboard_services.py`)

| # | Rule / clause | Planned scenarios | Scenario (close-out) |
|---|---|---|---|
| 14 | `Rule.count` DailyFlow.order_count (insert_parent) | create order (count +1, dated today); delete order (−1); move order to another day (both buckets adjust, new bucket created) || A new order is dated today and counted in today's totals; Deleting an order removes it from today's totals; Moving an order to another day adjusts both days |
| 15 | `Rule.sum` DailyFlow.order_amount (insert_parent) | create; change value (item qty); delete; move to another day || A new order is dated today...; Changing an order's value adjusts today's order amount; Deleting an order...; Moving an order to another day... |
| 16 | `Rule.count` message_received / message_processed (where is_processed) | accepted message: received +1, processed +1 (message dated today) || An accepted message is counted |
| 17 | `Rule.count` message_rejected (where error_text) | rejected message: rejected +1 (live Kafka only: simulated leaves no blob) || A rejected message is counted (live Kafka only) |
| 18 | `Rule.formula` message_pending | message set back to not processed: processed −1 (leaves where), pending +1 || A message set back to not processed counts as not yet done |
| 19 | `Rule.count` request_received / request_processed / request_rejected | accepted request: received +1, processed +1; rejected request: received +1, rejected +1 (request dated today) || Accepted and rejected B2B requests are counted |
| 20 | `Rule.formula` request_pending | request set back to not processed: processed −1 (leaves where), pending +1 || A request set back to not processed counts as not yet done |
| 21 | Chart the last 30 days, zero-filled | chart has 31 days ending today; a day with no DailyFlow row shows 0 || The chart shows the last 30 days with quiet days as zero |
| 22 | Show current data each time | after a new order, the chart's today value equals DailyFlow (no cache) || The chart shows current data each time it is opened |

## Close-out

All 22 rows have a scenario: **0 rows NOT covered.** 36 scenarios in 6 features (plus the generated `about.feature`).

Notes:
- Rows 10 and 17 are live-only: they are skipped (not verified, not passed) when no broker is reachable.
- Kafka subscribe scenarios are mode-aware (`logs/delivery_modes.json` records live or simulated per scenario).
- The publish rows check `logs/als.log` (the message JSON is logged whether or not a broker answers): that proves the
  content, not delivery.
