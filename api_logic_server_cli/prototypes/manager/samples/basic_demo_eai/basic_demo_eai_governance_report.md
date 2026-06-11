# 🩺 basic_demo_eai — Project Governance Report
**Date:** 2026-06-11
**Scoring:** Coverage Score (weighted rules / domain tables) + Integrity Score (100 - demerits) + Effective LOC
**Reference:** `docs/training/health_check.md`

---

## Summary

| Project | Tables | Wtd Rules | Coverage | Integrity | Red Flag | Effective LOC | Profile |
|---|---|---|---|---|---|---|---|
| basic_demo_eai | 7 | 11 | **1.6** | **94** | — | **454** | 🟢 Clean — rules in logic_discovery, EAI consume/publish wired correctly; FK indexes missing (schema-wide) |

> **Coverage** = weighted rules / domain tables (sum/count=3, formula/copy=2, constraint=1). Target ≥ 3.0 for mature projects.
> **Integrity** = 100 minus demerits for anti-patterns: broken dependency tracking, procedural aggregates replacing rules, events that should be rules. Target ≥ 95.
> **Red Flag** = 🚨 if ≥ 10 FK tables and zero sum/count rules — team has evidently not adopted aggregation rules.
> **Effective LOC** = code added beyond the generated scaffold, vs hardcoded baseline LOC per file (see `docs/training/health_check.md` v1.7).
> See `docs/training/governance.md` for full scoring guide.

---

## Scores

| Metric | Value | Grade |
|---|---|---|
| **Coverage Score** | **1.6** (11 pts / 7 domain tables) | 🟡 Moderate |
| **Integrity Score** | **94** (6 points deducted) | 🟡 Fair |
| **Effective LOC** | **454** | — |

---

## Coverage Detail

**Domain tables (7):** Customer, Item, Order, OrderB2bMessage, Product, ProductSupplier, Supplier

**Rule inventory:**

| Rule | File | Type | Weight |
|---|---|---|---|
| Item.unit_price copied from Product.unit_price | check_credit.py | copy | 2 |
| Item.amount = quantity × unit_price | check_credit.py | formula | 2 |
| Order.amount_total = sum(Item.amount) | check_credit.py | sum | 3 |
| Customer.balance = sum(Order.amount_total where unshipped) | check_credit.py | sum | 3 |
| Customer.balance ≤ credit_limit | check_credit.py | constraint | 1 |
| Order → Kafka 'order_shipping' on date_shipped set (by-example, mapper) | app_integration.py | event | 0 |
| OrderB2bMessage → Kafka 'order_b2b_processed' (2-message EAI bridge) | order_b2b_consume.py | event | 0 |

**Weighted total:** 1×sum(3) + 1×sum(3) + 1×formula(2) + 1×copy(2) + 1×constraint(1) = 3+3+2+2+1 = **11**
**Coverage:** 11 / 7 = **1.6**

> Coverage is moderate by design — basic_demo_eai's primary focus is the EAI (Kafka publish/consume) integration pattern, not a deep aggregation hierarchy. ProductSupplier and Supplier carry no rules (appropriate for a reference/demo project).

---

## Integrity Findings

| | File | Finding | Points |
|---|---|---|---|
| 🟡 | logic/logic_discovery/ | Missing `__init__.py` | **-1** |
| 🟡 | database/db.sqlite | `order.customer_id` → customer — no covering index | **-1** |
| 🟡 | database/db.sqlite | `item.product_id` → product — no covering index | **-1** |
| 🟡 | database/db.sqlite | `item.order_id` → order — no covering index | **-1** |
| 🟡 | database/db.sqlite | `product_supplier.supplier_id` → supplier — no covering index | **-1** |
| 🟡 | database/db.sqlite | `product_supplier.product_id` → product — no covering index | **-1** |

**Integrity:** 100 - 6 = **94**

### What's Clean

- ✅ Rules already organized in `logic/logic_discovery/` by use case (check_credit.py, app_integration.py, order_b2b_consume.py) — no migration needed
- ✅ No wildcard imports (`from database.models import *`) in declare_logic.py or logic_discovery files
- ✅ No `session.query()` inside formula functions
- ✅ No `as_expression=lambda row: my_func(row)` wrapping — all formulas are direct expressions
- ✅ EAI consume follows the 2-message design (blob insert → after_flush publish → Consumer 2 parse), with `is_processed` guard to prevent duplicate publish on the debug path
- ✅ Kafka publish uses `kafka_producer.publish_kafka_message(...)` with by-example mapper, not ad-hoc send functions
- ✅ Producer accessed via `kafka_producer.producer` at call time (not import-by-value)

---

## Action Items

| Priority | Item | Fix |
|---|---|---|
| 🟡 -1 | Missing `__init__.py` | `touch logic/logic_discovery/__init__.py` |
| 🟡 -5 | 5 unindexed FK columns | `CREATE INDEX` on order.customer_id, item.product_id, item.order_id, product_supplier.supplier_id, product_supplier.product_id |

---

## Effective LOC Detail

Total Effective LOC: **454** (vs hardcoded scaffold baselines; `database/models.py` excluded)

| Bucket | LOC | Detail |
|---|---|---|
| logic_discovery | 118 | check_credit.py, app_integration.py, order_b2b_consume.py |
| cross-cutting | 336 | api_discovery: order_b2b_api.py + order_b2b_consume_debug.py = 143; integration: OrderB2bMapper.py + kafka_publish_discovery/order_shipping.py + kafka_subscribe_discovery/order_b2b.py = 182; security: declare_security.py growth = 11 |

**Per-table (logic_discovery LOC referencing each table — overlapping by design):**

| Table | LOC |
|---|---|
| Order | 66 |
| Customer | 46 |
| OrderB2bMessage | 42 |
| Item | 36 |
| Product | 36 |

---

## Summary

basic_demo_eai is a **clean, focused EAI integration sample** — 5 weighted rules (11 pts) covering the core order/credit-check flow, plus 2 correctly-implemented event rules: Kafka publish (order_shipping, by-example mapper) and Kafka consume (2-message order_b2b pipeline with debug endpoint). The single logic-organization finding (missing `logic_discovery/__init__.py`) is cosmetic and does not affect runtime (Python 3 namespace packages still discover the files). Schema-check found 5 FK columns with no covering index — typical of `rebuild-from-database` scaffolding, which does not auto-create FK indexes.

**Coverage 1.6** — moderate; appropriate for a project whose purpose is demonstrating EAI patterns rather than a deep rule hierarchy.
**Integrity 94** — fair; one housekeeping item plus 5 unindexed FK columns (schema-wide pattern, not project-specific).
**Effective LOC 454** — measurable "beyond-scaffold" effort, concentrated in the EAI consume/publish pipeline (336 lines) and core credit-check rules (118 lines).
