# 🩺 basic_demo_logic_gov — Project Governance Report
**Date:** 2026-06-11
**Scoring:** Coverage Score (weighted rules / domain tables) + Integrity Score (100 - demerits) + Effective LOC
**Reference:** `docs/training/health_check.md`

---

## Summary

| Project | Tables | Wtd Rules | Coverage | Integrity | Red Flag | Effective LOC | Profile |
|---|---|---|---|---|---|---|---|
| basic_demo_logic_gov | 3 | 11 | **3.7** | **96** | — | **0** | 🟢 Canonical check-credit reference (5 rules), minimal/clean; FK indexes missing schema-wide |

> **Coverage** = weighted rules / domain tables (sum/count=3, formula/copy=2, constraint=1). Target ≥ 3.0 for mature projects.
> **Integrity** = 100 minus demerits for anti-patterns: broken dependency tracking, procedural aggregates replacing rules, events that should be rules. Target ≥ 95.
> **Red Flag** = 🚨 if ≥ 10 FK tables and zero sum/count rules — team has evidently not adopted aggregation rules.
> **Effective LOC** = code added beyond the generated scaffold, vs hardcoded baseline LOC per file (see `docs/training/health_check.md` v1.7).
> See `docs/training/governance.md` for full scoring guide.

---

## Scores

| Metric | Value | Grade |
|---|---|---|
| **Coverage Score** | **3.7** (11 pts / 3 domain tables) | 🟡 Moderate-to-Strong |
| **Integrity Score** | **96** (4 points deducted) | 🟢 Good |
| **Effective LOC** | **0** | — |

---

## Coverage Detail

**Domain tables (3):** Customer, Order, Item

**Excluded — system (1):** SysConfig (settings table — `discount_rate`, `tax_rate`, `notes`)
**Excluded — lookup (1):** Product (2 non-PK cols: name, unit_price — referenced as `Rule.copy` source only)
*(lookup threshold: ≤ 2 non-PK columns)*

**Rule inventory:**

| Rule | File | Type | Weight |
|---|---|---|---|
| Customer.balance ≤ credit_limit | check_credit.py | constraint | 1 |
| Customer.balance = sum(Order.amount_total where date_shipped is null) | check_credit.py | sum | 3 |
| Order.amount_total = sum(Item.amount) | check_credit.py | sum | 3 |
| Item.amount = quantity × unit_price | check_credit.py | formula | 2 |
| Item.unit_price copied from Product.unit_price | check_credit.py | copy | 2 |
| Order → Kafka topic `order_shipping` if date_shipped is not None | app_integration.py | event | 0 |

**Weighted total:** 2×sum(3) + 1×formula(2) + 1×copy(2) + 1×constraint(1) = 6 + 2 + 2 + 1 = **11**
**Coverage:** 11 / 3 = **3.7**

---

## Integrity Findings

| | File | Finding | Points |
|---|---|---|---|
| 🟡 | logic/logic_discovery/ | Missing `__init__.py` (root level) | **-1** |
| 🟡 | database/db.sqlite | item.product_id → product — no covering index | **-1** |
| 🟡 | database/db.sqlite | item.order_id → order — no covering index | **-1** |
| 🟡 | database/db.sqlite | order.customer_id → customer — no covering index | **-1** |

**Integrity:** 100 - 1 - (3 × 1) = **96**

### Schema Check — Primary Keys

All 4 mapped tables have a primary key. **No findings.**

### Hall Passes Applied

| | File | Function | Pattern |
|---|---|---|---|
| ✅ | place_order/app_integration.py | `kafka_producer.send_row_to_kafka` (after_flush_row_event) | `kafka-publish` — built-in framework function, conditional on `date_shipped` |

### What's Clean

- ✅ No `session.query()` anywhere in `logic/logic_discovery/`
- ✅ No wildcard imports in any logic_discovery file
- ✅ All formula/copy lambdas reference `row.attr` directly — dependency tracking intact
- ✅ Rules organized by use case: `check_credit.py` (5 rules), `app_integration.py` (1 event)
- ✅ `declare_logic.py` contains only framework boilerplate — no project rules misplaced there
- ✅ Minimal, clean implementation — this is the canonical 5-rule check-credit reference (same logic as `basic_demo_sample`, more compact presentation)

---

## Action Items

| Priority | Item | Fix |
|---|---|---|
| 🟡 -1 | Missing `__init__.py` at `logic/logic_discovery/` root | `touch logic/logic_discovery/__init__.py` |
| 🟡 -3 | 3 unindexed FK columns | `CREATE INDEX` on each FK column listed above (item.product_id, item.order_id, order.customer_id) |

---

## Effective LOC Detail

Total Effective LOC: **0** (vs hardcoded scaffold baselines; `database/models.py` excluded)

> This project implements the **same 5 check-credit rules + 1 Kafka integration event** as
> `basic_demo_sample` — the canonical "On Placing Orders, Check Credit" requirement — but in a
> more compact style (23-line `check_credit.py` + 14-line `app_integration.py`, vs 31 + 23 in
> `basic_demo_sample`). `logic/declare_logic.py` (91 lines) differs from the
> `allocate_dept_account_demo` baseline (83 lines) only in scaffold-template comment wording and
> one extra import (`from config.config import Config`) — pure scaffold-version variance, not
> project logic. `security/declare_security.py` (48), `use_case.py` (32), `auto_discovery.py` (51)
> all match the basic_demo-family baseline. No new files in `api/api_discovery/` or `integration/`
> beyond unmodified EAI/Kafka framework infrastructure.
>
> Net result: this project's hand-written logic is a **restatement of baseline rules already
> present in its sibling**, not additional code beyond the scaffold → Effective LOC = 0.

---

## Summary

basic_demo_logic_gov is the **canonical, minimal reference implementation** of the classic check-credit chain — 5 weighted rules (11 pts) covering the full Customer→Order→Item dependency graph (balance constraint, two sum rules, one formula, one copy) plus a Kafka `order_shipping` integration event. The implementation is clean and compact: no dependency-tracking bugs, no wildcard imports, no `session.query()`, and no rules misplaced in `declare_logic.py`.

**Coverage 3.7** — moderate-to-strong for a deliberately small 3-table domain (Customer, Order, Item); Product is correctly excluded as a 2-column lookup table referenced only via `Rule.copy`.
**Integrity 96** — good; the only findings are 3 unindexed FK columns (a schema-wide `rebuild-from-database` pattern shared with `basic_demo_sample` and `basic_demo_ai_rules-supplier`, all built on the same basic_demo schema) and one missing `__init__.py`.
**Effective LOC 0** — this project's logic is the same 5+1 rule set found in `basic_demo_sample`, expressed more concisely; it does not add code beyond what the basic_demo-family baseline already represents.
