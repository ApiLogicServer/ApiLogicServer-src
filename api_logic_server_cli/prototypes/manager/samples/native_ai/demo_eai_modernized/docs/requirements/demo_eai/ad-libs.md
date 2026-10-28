## Ad-Libs Report
**4 items need your review. 5 FYIs — standard patterns, no action needed.**

---

## Walkthrough

1. **Basic data model** — Existing `basic_demo.sqlite` schema (`Customer`, `Order`, `Item`, `Product`, `Supplier`, `ProductSupplier`).
2. **Derived/predicted schema additions** — Added `order_b2b_message` (`OrderB2bMessage`) blob table (`id`, `received_at`, `payload`, `is_processed`, `error_text`) for the 2-message Kafka subscribe pipeline; all Check Credit derived columns (`Item.unit_price`, `Item.amount`, `Order.amount_total`, `Customer.balance`) already exist on `models.py`.
3. **Create db** — Added `order_b2b_message` via SQLite DDL and ran `genai-logic rebuild-from-database` (7 tables total).
4. **Run impl-req** — Implemented 5 Check Credit rules (`copy`, `formula`, 2 `sum`, `constraint`), `OrderB2B` custom API + `RowDictMapper`, 2-message `order_b2b` Kafka subscribe pipeline (all 9 artifacts), by-example `order_shipping` Kafka publish event + mapper, and `sales` role row-level security grants.
5. **Test data / testing** — Shipped `basic_demo.sqlite` seed data retained; Behave feature suites generated and executed against live server + Kafka broker.

<details markdown>
<summary>Full diagnostic detail (DDL change list, rule plan, rejected alternatives, replay log)</summary>

### 🟢 Diagnostic Appendix

#### Pre-Coding Analysis
*(written before any code — both phases completed in order)*

**Phase 1 — Schema Impact Assessment**
Files read: `requirements.md` (all steps), `message_formats/*` (all files), `database/models.py`

| Step | Signal |
|---|---|
| Step 1 — Business Logic — Check Credit | `Rule.copy`, `Rule.formula`, `Rule.sum` (x2), `Rule.constraint` — no schema change (all target columns already exist in `models.py`) |
| Step 2 — B2B API — Accept orders from external partners | Custom API (`OrderB2B`) + `RowDictMapper` — no schema change |
| Step 3 — Kafka Subscribe — Inbound orders from sales channel | EAI Consume detected (`order_b2b` topic) — requires `order_b2b_message` (`OrderB2bMessage`) blob table |
| Step 4 — Kafka Publish — Notify shipping on dispatch | `Rule.after_flush_row_event` + `EaiPublishMapper` — no schema change |
| Step 5 — Security | Row-level `Grant` declarations in `security/declare_security.py` — no schema change |

DDL change list *(one row per change — covers ALL steps, run once before any coding)*:

| Table | Change | Reason |
|---|---|---|
| `order_b2b_message` | CREATE TABLE `order_b2b_message` (`id`, `received_at`, `payload`, `is_processed`, `error_text`) | Step 3 — EAI blob table for 2-message Kafka consume pipeline |

**Phase 2 — CE / Pattern Assessment**
Files read: `eai_subscribe.md`, `logic_bank_api.md`, `logic_bank_patterns.md`, `security.md`

| Step | Rule Plan |
|---|---|
| Step 1 — Business Logic — Check Credit | `Rule.copy(derive=Item.unit_price, from_parent=Product.unit_price)`, `Rule.formula(derive=Item.amount, as_expression=lambda row: row.quantity * row.unit_price)`, `Rule.sum(derive=Order.amount_total, as_sum_of=Item.amount)`, `Rule.sum(derive=Customer.balance, as_sum_of=Order.amount_total, where=lambda row: row.date_shipped is None)`, `Rule.constraint(validate=Customer, as_condition=lambda row: row.balance <= row.credit_limit, ...)` |
| Step 2 — B2B API — Accept orders from external partners | `OrderB2B` service in `api/api_discovery/order_b2b_service.py` + `OrderB2BMapper` in `integration/row_dict_maps/OrderB2BMapper.py`, raising `safrs.ValidationError` on failure |
| Step 3 — Kafka Subscribe — Inbound orders from sales channel | 2-message EAI consume — 9 artifacts confirmed (`OrderB2bMessage` table, `kafka_subscribe_discovery/order_b2b.py`, `logic/logic_discovery/order_b2b_consume.py`, `integration/OrderB2bMapper.py`, sample JSON, `api/api_discovery/order_b2b_kafka_consume_debug.py`, `ui/admin/admin.yaml`, `integration/kafka/order_b2b_reset.sh`, `test/send_order_b2b.py`) |
| Step 4 — Kafka Publish — Notify shipping on dispatch | `Rule.after_flush_row_event(on_class=Order, calling=send_order_to_shipping)` calling `kafka_producer.publish_kafka_message(topic="order_shipping", logic_row=logic_row, mapper=order_shipping)` with `integration/kafka/kafka_publish_discovery/order_shipping.py` |
| Step 5 — Security | `Grant` on `models.Customer` for `Roles.sales` (`credit_limit >= 3000` OR `balance > 0`) in `security/declare_security.py` |

Anti-patterns confirmed clear:
- [x] No parent flag where Rule.count on child table is correct
- [x] No `as_expression=lambda row: my_func(row)` — using `calling=my_func` or direct inline lambda
- [x] No `session.query()` inside formula or row_event
- [x] EAI: plain model rows return from mapper confirmed, 2-message design confirmed

**Implementation Plan** *(ordered steps written before any file was changed)*:

| Step | What was planned |
|---|---|
| 1 | Run DDL to create `order_b2b_message` table + `genai-logic rebuild-from-database` |
| 2 | Write `logic/logic_discovery/check_credit.py` + `docs/requirements/check_credit/requirements.md` |
| 3 | Write `integration/row_dict_maps/OrderB2BMapper.py` and `api/api_discovery/order_b2b_service.py` (with `Feature: B2B Order Integration` docstring) |
| 4 | Write EAI subscribe artifacts: `integration/OrderB2bMapper.py`, `integration/kafka/kafka_subscribe_discovery/order_b2b.py`, `logic/logic_discovery/order_b2b_consume.py` (+ `docs/requirements/order_b2b_consume/requirements.md`), `api/api_discovery/order_b2b_kafka_consume_debug.py`, `docs/sample_data/sample_order_b2b.json`, `ui/admin/admin.yaml`, `integration/kafka/order_b2b_reset.sh`, `test/send_order_b2b.py` |
| 5 | Write EAI publish artifacts: `integration/kafka/kafka_publish_discovery/order_shipping.py` and `logic/logic_discovery/order_shipping_publish.py` (+ `docs/requirements/order_shipping_publish/requirements.md`) |
| 6 | Update `security/declare_security.py` with `Feature: Row-Level Security` docstring, `Roles.sales`, `DefaultRolePermission`, and the two `Grant` filters on `Customer` |
| 7 | Run behavioral verification pass (STEP 8) and complete `ad-libs.md` + `project_creation_report.md` |

---

#### Execution Metrics

| Metric | Value |
|---|---|
| Strategy Used | Pre-coding schema & pattern assessment followed by single-pass DDL rebuild and modular discovery files |
| CE Files Loaded | `.github/copilot-instructions.md`, `docs/training/implement_requirements.md`, `docs/training/eai_subscribe.md`, `docs/training/logic_bank_api.md`, `docs/training/logic_bank_patterns.md`, `docs/training/security.md`, `docs/training/testing.md` |
| Schema Read First | Yes — `models.py` read before any logic or mapper |
| Sample Data Read | Yes — `message_formats/*` read before mapper |
| Subagent Used | No — single pass |
| Self-Verification | Yes — 8/8 checks passed |
| Lightweight Checks Used | Yes (`py_compile` + AST / import checks) |
| Gate Test Run Count | 2 |
| Gate Test Purpose | Final verification |
| Error Correction Loops | None |
| Long-Run Diagnostics | None |

None — implementation passed on first run.

---

### 🔴 Review Required
| Location | Issue | Action |
|---|---|---|
| `logic/logic_discovery/check_credit.py:26` | Spec states "sum unpaid order totals to get the customer balance" without defining "unpaid"; interpreted "unpaid" as `row.date_shipped is None` since `Order` has `date_shipped` and no payment status column. | Confirm that unshipped (`date_shipped is None`) is the intended definition of an unpaid order. |
| `logic/logic_discovery/check_credit.py:30` | Spec states "reject if balance exceeds the credit limit"; implemented with null-guards (`row.balance is None or row.credit_limit is None or row.balance <= row.credit_limit`). | Confirm whether customers with `credit_limit is None` should be allowed unlimited credit or rejected. |
| `logic/logic_discovery/check_credit.py:18` | Domain-floor constraints (`Item.quantity > 0`, `Product.unit_price > 0`) are not stated in `requirements.md` and were not added silently per CE Rule 8. | Confirm if you want `Rule.constraint` validations added for `Item.quantity > 0` and `Product.unit_price > 0`. |
| `integration/kafka/kafka_publish_discovery/order_shipping.py:39` | `message_formats/order_shipping.json` specifies `"order_date"`, while `models.Order` has `CreatedOn` and `date_shipped` (no `order_date` column); mapped `"order_date"` to `Order.CreatedOn`. | Confirm whether `"order_date"` in the shipping message should map to `Order.CreatedOn` or `Order.date_shipped`. |

---

### 🟡 FYI
- `database/models.py` — Added `order_b2b_message` (`OrderB2bMessage`) table with `id`, `received_at`, `payload`, `is_processed`, and `error_text` for the mandatory 2-message EAI consume pattern.
- `logic/logic_discovery/check_credit.py:30` — Used `<=` boundary operator for "reject if balance exceeds the credit limit" (`row.balance <= row.credit_limit`).
- `api/api_discovery/order_b2b_service.py:67` — Raised `safrs.ValidationError` on rejected B2B orders so SAFRS returns HTTP 400 instead of wrapping a tuple in HTTP 200.
- `logic/logic_discovery/order_shipping_publish.py:21` — Guarded `order_shipping` Kafka publish with `row.date_shipped is not None and (old_row is None or row.date_shipped != old_row.date_shipped)` on `Rule.after_flush_row_event`.
- `security/declare_security.py:37` — Implemented `credit_limit >= 3000 or balance > 0` for the `sales` role as two separate `Grant` declarations on `models.Customer` (multiple grants for the same role/entity are OR'd by the security engine).

</details>
