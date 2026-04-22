# Ad-Libs Report — demo_eai

**1 item caught during Kafka test and fixed. 6 FYIs — standard patterns, no action needed.**

### 🔴 Review Required (caught and fixed during Kafka test)

| Location | Issue | Fix Applied |
|---|---|---|
| `integration/OrderB2bMapper.py` and `integration/kafka/kafka_subscribe_discovery/order_b2b.py` | Initial `parse()` returned `list[(item_row, item_src_dict)]` tuples; calling code unpacked them directly. Ref impl returns plain `list[models.Item]` and caller uses `zip(item_rows, raw.get(ORDER_B2B_CHILD_KEY, []))`. Consumer 1 also omitted explicit `is_processed=False`, leaving a `None` Python value before flush; the `is_processed` guard in the row-event then suppressed the publish to `order_b2b_processed`, so Consumer 2 never fired. | `parse()` updated to return `(order_row, item_rows)` plain list; caller updated to `zip` pattern; Consumer 1 now passes `is_processed=False` explicitly. Verified end-to-end: blob `is_processed=1`, Order and Items persisted with correct amounts. |

### 🟡 FYI

- `logic/logic_discovery/check_credit.py` — standard 5-rule check-credit suite: copy price, formula amount, sum order total, sum customer balance (unshipped only), constraint balance ≤ credit_limit
- `integration/kafka/kafka_subscribe_discovery/order_b2b.py` — 2-message design applied: Consumer 1 saves blob only (Tx 1, `is_processed=False` explicit); Consumer 2 parses + persists domain rows (Tx 2); `is_processed` guard in row-event prevents spurious re-publish on debug path
- `logic/logic_discovery/order_b2b_consume.py` — `after_flush_row_event` used (not `row_event`) so `blob.id` is DB-assigned before key is published to `order_b2b_processed`; `is_processed` guard `if row.is_processed: return` included per training
- `integration/kafka/kafka_publish_discovery/order_shipping.py` — by-example publish using `EaiPublishMapper.serialize_row`; dot-notation for `customer.name` and `product.name` (related rows); `ItemList` mapped as child collection
- `logic/logic_discovery/app_integration.py` — `after_flush_row_event` guard: `date_shipped is not None and date_shipped != old_row.date_shipped` (fires on insert-with-value OR update-where-changed, not every save)
- `security/declare_security.py` — `sales` role Grant declared with `or_(credit_limit >= 3000, balance > 0)` filter; `SECURITY_ENABLED = false` in `config/default.env` — change to `true` and add `sales` users to auth DB to activate
