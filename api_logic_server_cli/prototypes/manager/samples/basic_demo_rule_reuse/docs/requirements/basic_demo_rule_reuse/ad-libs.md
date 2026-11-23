## Ad-Libs Report
**3 items need your review. 5 FYIs — standard patterns, no action needed.**

---

## Walkthrough

1. **Basic data model** — existing `basic_demo.sqlite`: Customer, Order, Item, Product, Supplier, ProductSupplier.
2. **Derived/predicted schema additions** — none: every derived column (balance, amount_total, amount, unit_price) and `Order.notes` already exist; no constants → no SysConfig; no Allocate; no Request Pattern.
3. **Create db** — `genai-logic create --db_url=sqlite:///samples/dbs/basic_demo.sqlite` (Method 1); no DDL, no rebuild.
4. **Run impl-req** — Check Credit: 2 sums, 1 formula, 1 copy, 1 constraint (`Customer.credit_limit_check`); App Integration: 1 after-flush event (`Order.shipping_publish`); Move Order Check Credit: **no new rule** — linked by `Uses:` to `Customer.balance` and `Customer.credit_limit_check`.
5. **Test data / testing** — existing data kept (stored aggregates checked consistent with the rules). Behave tests created on request: 16 scenarios in 3 Features, all passing (see test_plan.md).

<details markdown>
<summary>Full diagnostic detail (DDL change list, rule plan, rejected alternatives, replay log)</summary>

### 🟢 Diagnostic Appendix

#### Pre-Coding Analysis
*(written before any code — both phases completed in order)*

**Phase 1 — Schema Impact Assessment**
Files read: `requirements.md` (all steps), `message_formats/*` (none for this use case), `database/models.py`

| Step | Signal |
|---|---|
| Notes field for orders | no schema change — `Order.notes` exists |
| Check Credit | Rule.sum ×2, formula, copy, constraint — columns all present |
| App Integration | after_flush_row_event (Kafka publish) — no schema change |
| Move Orders, Check Credit | redundant — same derivation and constraint as Check Credit; no schema change |

DDL change list: None — all required columns already present in models.py

**Phase 2 — CE / Pattern Assessment**
Files read: `logic_bank_api.md`

| Step | Rule Plan |
|---|---|
| Check Credit | Rule.sum(Customer.balance where date_shipped is None) + Rule.sum(Order.amount_total) + Rule.formula(Item.amount) + Rule.copy(Item.unit_price) + Rule.constraint(name=credit_limit_check) |
| App Integration | Rule.after_flush_row_event(Order, send_row_to_kafka, when_condition=date_shipped is not None, name=shipping_publish) |
| Move Orders, Check Credit | none — placeholder logic file with `Uses: Customer.balance (Check Credit), Customer.credit_limit_check (Check Credit)` |

Anti-patterns confirmed clear:
- [x] No parent flag where Rule.count on child table is correct
- [x] No `as_expression=lambda row: my_func(row)` — no calling functions needed
- [x] No `session.query()` inside formula or row_event
- [x] EAI: n/a (publish only, standard `send_row_to_kafka`)

**Implementation Plan**:

| Step | What was planned |
|---|---|
| 1 | Create project from basic_demo.sqlite (no DDL) |
| 2 | Write `place_order/check_credit.py` — 5 rules |
| 3 | Write `place_order/app_integration.py` — 1 event |
| 4 | Write `move_order/check_credit.py` — placeholder, Uses: only |
| 5 | Per-use-case requirements.md excerpts; start server; exercise move-order and shipping paths via API |

---

#### Execution Metrics

| Metric | Value |
|---|---|
| Strategy Used | Rules over existing schema; rule reuse for the path-specific requirement |
| CE Files Loaded | `.github/copilot-instructions.md` (Executable Requirements section), `docs/training/logic_bank_api.md`, `docs/training/implement_requirements.md` (ad-libs template) |
| Schema Read First | Yes — models.py / db schema read before logic |
| Sample Data Read | n/a — no message_formats |
| Subagent Used | No — single pass |
| Self-Verification | Yes — server started, logic discovered, PATCHes via API, logs/als.log checked |
| Lightweight Checks Used | Yes — curl + logs/als.log |
| Gate Test Run Count | 0 — no Behave tests created |
| Gate Test Purpose | n/a |
| Error Correction Loops | None |
| Long-Run Diagnostics | None |

Self-verification (API, data restored afterward):
- Moved Order 3 (220) Charlie → Alice: Alice 90 → 310, Charlie 220 → 0; moved back.
- Lowered Diana's credit_limit to 100, moved Order 3 to Diana: rejected once — "Customer balance (220) exceeds credit limit (100)"; limit restored.
- Shipped Order 2: one `order_shipping` publish (Kafka not enabled → logged); a later notes edit did not publish again; reverted.

**Error Correction Loops**: None — implementation passed on first run.

---

### 🔴 Review Required
| Location | Issue | Action |
|---|---|---|
| `logic/logic_discovery/place_order/check_credit.py:26` | "unshipped" is not defined by the spec; read as `date_shipped is None` | Confirm — or name the column/status that means shipped |
| `logic/logic_discovery/place_order/check_credit.py:25` | "less than the credit limit" implemented as `balance <= credit_limit` (standing convention: a balance exactly at the limit is accepted) | Say so if the boundary must be rejected (strict `<`) |
| `logic/logic_discovery/place_order/check_credit.py` | Not added: domain-floor constraints (`Item.quantity > 0`, `Product.unit_price > 0`) — the spec does not state them | Say if you want them |

---

### 🟡 FYI
- `logic/logic_discovery/move_order/check_credit.py:12` — **redundant:** `Customer.balance` and `Customer.credit_limit_check` already enforce this on every path (a sum adjusts both the old and new Customer when an Order's customer changes); no new rule added. **Test to write:** moving an Order to a Customer whose balance would then exceed the credit limit is rejected. Linked by `Uses:` in `docs/requirements/move_order_check_credit/requirements.md`.
- `database/models.py` — "Include a notes field for orders": `Order.notes` already exists in basic_demo.sqlite; no change.
- `logic/logic_discovery/place_order/app_integration.py:18` — "becomes not None" → `when_condition` (fires once, on the transition), not `if_condition`.
- `logic/logic_discovery/place_order/check_credit.py:29` — Item.unit_price is `Rule.copy` (price frozen at order entry), per "copied from".
- `logic/logic_discovery/place_order/` — "Use case: App Integration" has no context phrase of its own; placed with Check Credit under `place_order/`, following the training example's structure.
- `docs/requirements/app_integration/requirements.md:1` — added the line `On Placing Orders:` above the verbatim excerpt. Without it, the traceability report listed App Integration twice: once with the context it inherits in the full spec ("Placing Orders") and once without, and the second copy showed no tests.

</details>
