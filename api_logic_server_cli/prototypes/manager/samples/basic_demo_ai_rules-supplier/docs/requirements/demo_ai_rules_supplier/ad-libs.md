## Ad-Libs Report
**7 items need your review. 6 FYIs — standard patterns, no action needed.**

---

## Walkthrough

1. **Basic data model** — basic_demo.sqlite: Customer, Order, Item, Product, Supplier, ProductSupplier (created with `genai-logic create`).
2. **Derived/predicted schema additions** — Request Pattern detected (clause 6, AI chooses a value): new audit table `sys_supplier_req`. No constants for SysConfig; `Product.count_suppliers`, `Customer.balance`, `Order.amount_total`, `Item.amount`, `Item.unit_price` already existed.
3. **Create db** — one DDL (`CREATE TABLE sys_supplier_req`) + `rebuild-from-database`; Admin UI Replace applied as the script directs (backup in `ui/admin/admin.yaml.bak`).
4. **Run impl-req** — 5 rules (constraint, 2 sum, formula, count), 1 Item early event + 1 SysSupplierReq early event (AI Request Pattern), 1 after_flush event (Kafka).
5. **Test data / testing** — 18 Behave scenarios pass; AI scenarios assert a valid supplier and an audit row, never a specific supplier.

<details markdown>
<summary>Full diagnostic detail (DDL change list, rule plan, rejected alternatives, replay log)</summary>

### 🟢 Diagnostic Appendix

#### Pre-Coding Analysis
**Phase 1 — Schema Impact Assessment**
Files read: `requirements.md`, `database/models.py` (no `message_formats/`)

| Step | Signal |
|---|---|
| Check Credit 1-4 | Rule.constraint, Rule.sum x2, Rule.formula — columns already present |
| Check Credit 5 | Rule.count — `Product.count_suppliers` present |
| Check Credit 6 | Request Pattern (value chosen by AI) -> `Sys*Req` table needed |
| App Integration 1 | after_flush_row_event to Kafka — no schema change |

DDL change list:

| Table | Change | Reason |
|---|---|---|
| sys_supplier_req | CREATE TABLE (item_id, product_id, chosen_supplier_id, chosen_unit_price, request TEXT, reason TEXT, fallback_used, created_on TEXT; all FKs nullable) | Check Credit 6 — Request Pattern audit table |

**Phase 2 — CE / Pattern Assessment**
Files read: `logic_bank_api.md`, `probabilistic_logic_guide.md`, `probabilistic_logic.md`, `implement_requirements.md`

| Step | Rule Plan |
|---|---|
| Check Credit | Rule.constraint + Rule.sum (balance, where date_shipped is None) + Rule.sum (amount_total) + Rule.formula (amount) + Rule.count (count_suppliers) + early_row_event on Item (unit_price) |
| Check Credit 6 | early_row_event on Item -> wrapper inserts SysSupplierReq -> early_row_event on SysSupplierReq calls OpenAI or falls back |
| App Integration | Rule.after_flush_row_event + kafka_producer.send_row_to_kafka, if_condition date_shipped is not None |

Anti-patterns confirmed clear:
- [x] No parent flag where Rule.count on child table is correct
- [x] No `as_expression=lambda row: my_func(row)`
- [x] No `session.query()` inside formula or row_event (relationships and `session.get` only)

#### Execution Metrics

| Metric | Value |
|---|---|
| Strategy Used | Request Pattern: Item early event -> SysSupplierReq insert -> AI event with min-cost fallback |
| CE Files Loaded | .github/copilot-instructions.md (partial), docs/training/logic_bank_api.md, probabilistic_logic_guide.md, probabilistic_logic.md, implement_requirements.md (Request Pattern + ad-libs template), testing.md (workflow + running) |
| Schema Read First | Yes |
| Self-Verification | Yes — server started, order placed through the API, audit row read back, server stopped |
| Gate Test Run Count | 1 — final verification |
| Error Correction Loops | 1 (see below) |

```
Loop 1:
  Symptom:   scripted order (Alice, 100 sheets) rejected: "Customer balance (20590) exceeds credit limit (5000)"; the AI audit row rolled back with it
  Diagnosis: logs/als.log: the AI chose a 205 supplier (100 x 205 = 20500 > 5000)
  Fix:       Alice's credit_limit raised to 50000 through the API (data only, no code change)
  Time:      ~1 min
  Root cause type: spec/seed-data conflict
```

---

### 🔴 Review Required
| Location | Issue | Action |
|---|---|---|
| `database/db.sqlite` (customer id 1) | The scripted verification (100 Egyptian Cotton Sheets for Alice) cannot pass the credit rule with the seed data: Alice's limit is 5000, 100 x 105 (cheapest) = 10,500. I raised her credit_limit to 50000 and the order was accepted (order 6). | Decide whether the demo should use a smaller quantity or a higher seeded limit; the rule itself is correct. |
| `logic/logic_discovery/ai_requests/supplier_selection.py:84` | "Optimal ... based on cost, lead time, and world conditions" does not say how to weigh them. The prompt asks for "fastest reliable delivery while keeping costs reasonable"; model gpt-4o-2024-08-06, temperature 0.7 (so the choice varies run to run). | Confirm the optimisation goal, model and temperature. |
| `logic/logic_discovery/place_order/check_credit.py:51` | Item.unit_price is set to the chosen supplier's `unit_cost` (no markup or margin), not to the Product price. The spec does not say what the price is. | Confirm the unit_cost is the intended selling price. |
| `logic/logic_discovery/place_order/check_credit.py:46` | A product with no suppliers copies `Product.unit_price` (the spec is silent). No audit row is written in that case. | Confirm. |
| `logic/logic_discovery/ai_requests/supplier_selection.py:65` | Fallback when there is no API key, the API errors, or the AI returns an unknown supplier: the minimum-cost supplier, recorded with `fallback_used = true` and the reason. The spec does not define a fallback. | Confirm the fallback policy. |
| `logic/logic_discovery/place_order/check_credit.py:23` | "balance is less than the credit limit" implemented as `<=` (CE boundary convention): an order that lands exactly on the limit is accepted. | Say so if equality should be rejected. |
| `logic/logic_discovery/place_order/app_integration.py:19` | "Publish ... if the date_shipped is not None" is implemented with `when_condition`: one message when date_shipped becomes set (or an Order is inserted already shipped), not on later edits. Payload is the default Order row dict, key = order id. | Confirm the transition reading and the payload shape. |

Not added (the spec does not state them): `quantity > 0` and `unit_price > 0` floors on Item. Say so if you want them.

---

### 🟡 FYI
- `database/models.py` (SysSupplierReq) — audit table created by DDL + rebuild-from-database; FKs nullable, `request` and `created_on` TEXT columns present.
- `ui/admin/admin.yaml` — replaced with the rebuilt config as the script directs; the prior file is `ui/admin/admin.yaml.bak`.
- `config/ai_test_context.yaml` — world_conditions 'Suez Canal blocked - use alternate shipping routes'; other scenarios commented out. It is an input condition, not a predetermined output.
- `logic/logic_discovery/place_order/check_credit.py:30` — early event (not a formula) sets unit_price, because the AI call returns several fields; it also fires when an Item's product changes.
- `logic/logic_discovery/ai_requests/supplier_selection.py` — a helper (no requirement of its own); the audit row is linked to the Item by object, not id.
- Kafka — KAFKA_SERVER is not configured, so publishing is simulated (the send is logged as "Kafka not enabled"); no broker was started.

</details>
