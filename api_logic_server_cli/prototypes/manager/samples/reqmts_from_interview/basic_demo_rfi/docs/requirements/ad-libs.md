## Ad-Libs Report
**6 items need your review. 8 FYIs — standard patterns, no action needed.**

---

## Walkthrough

1. **Basic data model** — customer, product, order (with the requested `notes`), item; created on top of the `starter.sqlite` `sys_config` table.
2. **Derived/predicted schema additions** — constant found: the green discount percentage → `sys_config.green_discount_pct`; flag `product.green`; snapshot `item.green`; derived `item.discount_amount`; rollups `customer.balance`, `order.amount_total`, `item.amount`; FK columns for every parent link; no allocate tables; no Request Pattern table.
3. **Create db** — one DDL run (1 ALTER + 4 CREATE TABLE) and one `rebuild-from-database`; 5 tables in `models.py`.
4. **Run impl-req** — 3 logic files in `logic/logic_discovery/place_order/`: 2 sum, 2 copy, 2 formula, 1 constraint, 1 after-flush event (Kafka publish).
5. **Test data / testing** — `alp_init.py` ran clean (2 customers, 4 products, 3 orders, 4 items; one order shipped, which published). Server started clean and a green item, a credit rejection and the publish were checked live. No Behave tests were created (not requested).

<details markdown>
<summary>Full diagnostic detail (DDL change list, rule plan, rejected alternatives, replay log)</summary>

### 🟢 Diagnostic Appendix

#### Pre-Coding Analysis

**Phase 1 — Schema Impact Assessment**
Files read: the prompt and interview, `database/models.py` (only `SysConfig` before DDL)

| Step | Signal |
|---|---|
| Check Credit | Rule.sum x2 (balance, amount_total), Rule.formula (amount), Rule.copy (unit_price), Rule.constraint |
| App Integration | EAI publish (after-flush event); outbound only, no consume, so no blob table |
| Green discount (interview) | constant → SysConfig; flag on Product; snapshot copy to Item; Rule.formula |

| Table | Change | Reason |
|---|---|---|
| sys_config | ADD COLUMN green_discount_pct NUMERIC(8,6) DEFAULT 0.10 | green discount — SysConfig constant |
| customer | CREATE TABLE (balance, credit_limit) | Check Credit — Rule.sum target, constraint |
| product | CREATE TABLE (unit_price, green) | Check Credit rule 5; green flag |
| order | CREATE TABLE (notes, customer_id FK, CreatedOn, date_shipped, amount_total) | notes requested; Rule.sum target |
| item | CREATE TABLE (order_id FK, product_id FK, quantity, unit_price, green, discount_amount, amount) | Rule.copy x2, Rule.formula x2 |

**Phase 2 — CE / Pattern Assessment**
Files read: `logic_bank_api.md`, `logic_bank_patterns.md` (first half), `implement_requirements.md`

| Step | Rule Plan |
|---|---|
| Check Credit | Rule.constraint(Customer), Rule.sum(Customer.balance), Rule.sum(Order.amount_total), Rule.formula(Item.amount), Rule.copy(Item.unit_price) |
| Green discount | Rule.copy(Item.green), Rule.formula(Item.discount_amount, calling=) |
| App Integration | Rule.after_flush_row_event(Order) → publish_kafka_message with a by-example mapper |

Anti-patterns confirmed clear:
- [x] No parent flag where Rule.count on a child table is correct (no counts needed)
- [x] No `as_expression=lambda row: my_func(row)` — the multi-line formula uses `calling=`
- [x] No `session.query()` inside a formula; the single `sys_config` read goes through `SysConfig.current()`
- [x] Row attributes are bound to local variables before any condition (tokenizer gotcha)

**Implementation Plan:**

| Step | What was planned |
|---|---|
| 1 | DDL + rebuild-from-database once |
| 2 | check_credit.py, green_discount.py, app_integration.py in `place_order/` |
| 3 | Kafka publish mapper `order_shipping.py` + `message_formats/order_shipping.json` |
| 4 | seed via `alp_init.py`, start server, check live |

---

#### Execution Metrics

| Metric | Value |
|---|---|
| Strategy Used | Method 4 (Manager): STEP 1b scoped interview on the green clause, then project CE System Creation Services |
| CE Files Loaded | project CE (via CLAUDE.md), `logic_bank_api.md`, `implement_requirements.md`, `logic_bank_patterns.md` (lines 1-400) |
| Schema Read First | Yes |
| Sample Data Read | n/a (no inbound messages) |
| Subagent Used | No — single pass |
| Self-Verification | Yes — server started, API probed, publish seen in the seed run |
| Lightweight Checks Used | Yes — curl + seed output |
| Gate Test Run Count | 0 (no Behave tests) |
| Error Correction Loops | 1 |

```
Loop 1:
  Symptom:   seed script failed with "Sorry, row altered by another user" on the shipping update
  Diagnosis: read the optimistic-locking patch: the as-read checksum was stale after earlier commits in the same session
  Fix:       session.expunge_all() and re-query the order before setting date_shipped; DB restored from a pre-seed copy and reseeded
  Time:      ~3 min
  Root cause type: CE gap (seed pattern for an update after commits)
```

---

### 🔴 Review Required
| Location | Issue | Action |
|---|---|---|
| `logic/logic_discovery/place_order/check_credit.py:20` | "less than the credit limit" implemented as `<=` (CE boundary convention: a balance exactly at the limit is allowed) | Confirm a balance equal to the limit should be accepted; change to `<` if not |
| `logic/logic_discovery/place_order/check_credit.py:21` | "unshipped" is not defined in the spec; read as `date_shipped is None` | Confirm that is what unshipped means |
| `database/models.py` (`sys_config.green_discount_pct`) | You gave no starting percentage; I defaulted it to 10% (0.10) | Set the value you want in the Admin UI (`sys_config` row) |
| `logic/logic_discovery/place_order/green_discount.py:28` | `Product.green` is free text; only exactly `'yes'` counts as green (`'Yes'`, `'true'` do not) | Say if you want the values constrained (a CHECK or constraint rule) |
| `integration/kafka/kafka_publish_discovery/order_shipping.py:11` | The spec says "publish the Order" with no message shape; I used the sample shape from `message_formats/readme.md` (order_id, order_date, customer_name, total, items) and added `discount_amount` and `amount` per item | Confirm the shape with the subscriber of `order_shipping` |
| `database/models.py` | Domain-floor constraints not added because the spec does not state them: `quantity > 0`, `unit_price > 0`, `green_discount_pct` between 0 and 1 | Say so if you want any of them |

---

### 🟡 FYI
- `logic/logic_discovery/place_order/green_discount.py:19` — `Item.green` is a `Rule.copy` snapshot from `Product.green`, and the percentage is read from `sys_config` when the item is priced (confirmed in the interview readback): flipping a product's flag or changing the percentage does not re-price existing items.
- `logic/logic_discovery/place_order/green_discount.py:29` — the discount is rounded to cents (`Decimal("0.01")`).
- `logic/logic_discovery/place_order/green_discount.py:28` — the rate is read with `SysConfig.current()`, with no `sys_config_id` FK on any table (CE default for a singleton settings table).
- `logic/logic_discovery/place_order/app_integration.py:20` — "becomes not None" is read as a transition from None (an insert with a value counts); changing a date on an already-shipped order does not republish.
- `logic/logic_discovery/place_order/check_credit.py:23` — rule 4 is extended (interview option A): `amount = quantity * unit_price - discount_amount`; for non-green items `discount_amount` is 0, so it equals your original rule 4.
- `database/models.py` — `sys_config.discount_rate` (0.05) and `tax_rate` (0.10) came with `starter.sqlite`; they are unused and separate from `green_discount_pct`.
- `logic/logic_discovery/place_order/` — files are grouped in a directory named for the context phrase "On Placing Orders" (project CE convention); each use case has its own `docs/requirements/<use_case>/requirements.md`.
- `database/test_data/alp_init.py` — seed data is illustrative (Alice, Bob; Widget, Gadget, green Bamboo Cup and Recycled Notebook); Kafka is not enabled, so the publish is the simulated "Kafka not enabled" path.

</details>
