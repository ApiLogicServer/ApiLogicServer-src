# 🩺 basic_demo_ai_rules-supplier — Project Governance Report
**Date:** 2026-06-11
**Scoring:** Coverage Score (weighted rules / domain tables) + Integrity Score (100 - demerits) + Effective LOC
**Reference:** `docs/training/health_check.md`

---

## Summary

| Project | Tables | Wtd Rules | Coverage | Integrity | Red Flag | Effective LOC | Profile |
|---|---|---|---|---|---|---|---|
| basic_demo_ai_rules-supplier | 6 | 12 | **2.0** | **93** | — | **337** | 🟢 AI-driven supplier selection (Request Pattern) + check-credit chain, well-organized; FK indexes missing schema-wide |

> **Coverage** = weighted rules / domain tables (sum/count=3, formula/copy=2, constraint=1). Target ≥ 3.0 for mature projects.
> **Integrity** = 100 minus demerits for anti-patterns: broken dependency tracking, procedural aggregates replacing rules, events that should be rules. Target ≥ 95.
> **Red Flag** = 🚨 if ≥ 10 FK tables and zero sum/count rules — team has evidently not adopted aggregation rules.
> **Effective LOC** = code added beyond the generated scaffold, vs hardcoded baseline LOC per file (see `docs/training/health_check.md` v1.7).
> See `docs/training/governance.md` for full scoring guide.

---

## Scores

| Metric | Value | Grade |
|---|---|---|
| **Coverage Score** | **2.0** (12 pts / 6 domain tables) | 🟡 Moderate |
| **Integrity Score** | **93** (7 points deducted) | 🟢 Fair-to-Good |
| **Effective LOC** | **337** | — |

---

## Coverage Detail

**Domain tables (6):** Customer, Product, Supplier, Order, ProductSupplier, Item

**Excluded — system (1):** SysSupplierReq (begins with "Sys" — request/audit table for AI supplier selection)
*(no lookup-table exclusions — all 6 domain tables have > 2 non-PK columns)*

**Rule inventory:**

| Rule | File | Type | Weight |
|---|---|---|---|
| Customer.balance ≤ credit_limit | check_credit.py | constraint | 1 |
| Customer.balance = sum(Order.amount_total where date_shipped is null) | check_credit.py | sum | 3 |
| Order.amount_total = sum(Item.amount) | check_credit.py | sum | 3 |
| Item.amount = quantity × unit_price | check_credit.py | formula | 2 |
| Product.count_suppliers = count(ProductSupplier) | check_credit.py | count | 3 |
| Item.unit_price — set via AI supplier selection (early_row_event, fallback-or-AI) | check_credit.py | event | 0 |
| SysSupplierReq — AI supplier selection (early_row_event, Request Pattern) | ai_requests/supplier_selection.py | event | 0 |
| Order → Kafka topic `order_shipping` if date_shipped is not None | app_integration.py | event | 0 |

**Weighted total:** 2×sum(3) + 1×count(3) + 1×formula(2) + 1×constraint(1) = 6 + 3 + 2 + 1 = **12**
*(2 sum: Customer.balance, Order.amount_total — 1 count: Product.count_suppliers — 1 formula: Item.amount — 1 constraint: Customer.balance ≤ credit_limit)*
**Coverage:** 12 / 6 = **2.0**

---

## Integrity Findings

| | File | Finding | Points |
|---|---|---|---|
| 🟡 | logic/logic_discovery/ | Missing `__init__.py` (root level) | **-1** |
| 🟡 | database/db.sqlite | item.product_id → product — no covering index | **-1** |
| 🟡 | database/db.sqlite | item.order_id → order — no covering index | **-1** |
| 🟡 | database/db.sqlite | order.customer_id → customer — no covering index | **-1** |
| 🟡 | database/db.sqlite | product_supplier.supplier_id → supplier — no covering index | **-1** |
| 🟡 | database/db.sqlite | product_supplier.product_id → product — no covering index | **-1** |
| 🟡 | database/db.sqlite | sys_supplier_req.chosen_supplier_id → supplier — no covering index | **-1** |

**Integrity:** 100 - 1 - (6 × 1) = **93**

### Schema Check — Primary Keys

All 7 mapped tables have a primary key. **No findings.**

### Hall Passes Applied

| | File | Function | Pattern |
|---|---|---|---|
| ✅ | place_order/app_integration.py | `send_order_to_kafka` (after_flush_row_event) | `kafka-publish` — Kafka producer call, conditional on `date_shipped` |
| ✅ | place_order/check_credit.py | `set_item_unit_price_from_supplier` (early_row_event) | `ai-handler` — fallback-or-AI pattern, calls `get_supplier_selection_from_ai` |
| ✅ | place_order/ai_requests/supplier_selection.py | `select_supplier_via_ai` (early_row_event on SysSupplierReq) | `ai-handler` — Request Pattern, populates `chosen_*` fields via AI |

### What's Clean

- ✅ No `session.query()` anywhere in `logic/logic_discovery/` — all dependencies are rule-based or event-based
- ✅ No wildcard imports in any logic_discovery file (the `from database.models import *` in `logic/load_verify_rules.py` is unmodified framework infrastructure, not project logic)
- ✅ Both `calling=` event functions (`set_item_unit_price_from_supplier`, `select_supplier_via_ai`) have docstrings
- ✅ AI supplier selection follows the Request Pattern (`SysSupplierReq` with audit fields: `request`, `reason`, `fallback_used`)
- ✅ Rules organized by use case in `logic/logic_discovery/place_order/` (check_credit.py, app_integration.py, ai_requests/supplier_selection.py)
- ✅ `declare_logic.py` contains only framework boilerplate — no project rules misplaced there
- ✅ `Item.amount = quantity * unit_price` formula references `row.quantity`, `row.unit_price` directly — dependency tracking intact

---

## Action Items

| Priority | Item | Fix |
|---|---|---|
| 🟡 -1 | Missing `__init__.py` at `logic/logic_discovery/` root | `touch logic/logic_discovery/__init__.py` |
| 🟡 -6 | 6 unindexed FK columns | `CREATE INDEX` on each FK column listed above (item, order, product_supplier, sys_supplier_req) |

---

## Effective LOC Detail

Total Effective LOC: **337** (vs hardcoded scaffold baselines; `database/models.py` excluded)

| Bucket | LOC | Detail |
|---|---|---|
| logic_discovery (new directory: place_order/) | 337 | check_credit.py=95, ai_requests/supplier_selection.py=214, app_integration.py=26, place_order/__init__.py=1, ai_requests/__init__.py=1 |

> Baseline reference: `allocate_dept_account_demo` (same basic_demo schema family — both share
> `logic/declare_logic.py`=83 lines, `security/declare_security.py`=48 lines,
> `logic/logic_discovery/use_case.py`=32 lines, `logic/logic_discovery/auto_discovery.py`=51 lines,
> identical `api/api_discovery/` and `integration/` file sets — all match exactly, 0 growth).
> All Effective LOC is concentrated in the new `logic/logic_discovery/place_order/` directory.

**Per-table (logic_discovery LOC referencing each table — overlapping by design):**

| Table | LOC |
|---|---|
| Item | ~190 (check_credit.py — amount formula + AI unit_price event) |
| Customer | ~95 (check_credit.py — balance sum/constraint) |
| Order | ~120 (check_credit.py amount_total sum + app_integration.py Kafka event) |
| Product / ProductSupplier | ~95 (check_credit.py — count_suppliers) |
| Supplier / SysSupplierReq | ~214 (ai_requests/supplier_selection.py — AI selection handler) |

> Counts overlap because `check_credit.py` declares 5 rules across multiple tables in one file.

---

## Summary

basic_demo_ai_rules-supplier is a **well-organized AI-augmented sample** — 5 weighted rules (12 pts) implementing the classic check-credit chain (Customer.balance ≤ credit_limit, sum/sum/formula/count cascade), plus an AI-driven supplier-selection handler using the Request Pattern (`SysSupplierReq` with full audit trail: `request`, `reason`, `fallback_used`). Logic is correctly split by use case (`check_credit.py`, `app_integration.py`, `ai_requests/supplier_selection.py`), with no dependency-tracking bugs, no wildcard imports, and complete docstring hygiene on both event handlers.

**Coverage 2.0** — moderate; reflects a focused 6-table domain where the credit-check chain (balance, amount_total, amount, count_suppliers) covers the core transactional path, while `Supplier`/`ProductSupplier` carry weight indirectly via the count rule and AI handler.
**Integrity 93** — fair-to-good, driven almost entirely by 6 unindexed FK columns (a schema-wide `rebuild-from-database` pattern, not specific to this project's logic) plus one missing `__init__.py`. No organizational anti-patterns found — clean dependency tracking, no `session.query()`, no events that should be rules.
**Effective LOC 337** — entirely concentrated in the new `logic/logic_discovery/place_order/` directory: 95 lines for the check-credit rule chain + AI fallback wiring, 214 lines for the AI supplier-selection Request Pattern handler, and 26 lines for the Kafka app-integration event. All other scaffold files (declare_logic.py, security, use_case.py, auto_discovery.py, api_discovery, integration) match the basic_demo-family baseline exactly — zero growth.
