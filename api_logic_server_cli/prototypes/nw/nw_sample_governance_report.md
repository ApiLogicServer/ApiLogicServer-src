# 🩺 nw_sample — Project Governance Report
**Date:** 2026-05-10  
**Scoring:** Coverage Score (weighted rules / domain tables) + Integrity Score (100 - demerits)  
**Reference:** `docs/training/health_check.md`

---

## Summary

| Project | Tables | Wtd Rules | Coverage | Integrity | Red Flag | Profile |
|---|---|---|---|---|---|---|
| nw_sample | 9 | 34 | **3.8** | **96** | — | 🟠 Rules in declare_logic.py — needs migration |

> **Coverage** = weighted rules / domain tables (sum/count=3, formula/copy=2, constraint=1). Target ≥ 3.0 for mature projects.  
> **Integrity** = 100 minus demerits for anti-patterns: broken dependency tracking, procedural aggregates replacing rules, events that should be rules. Target ≥ 95.  
> **Red Flag** = 🚨 if ≥ 10 FK tables and zero sum/count rules — team has evidently not adopted aggregation rules.  
> See `docs/training/governance.md` for full scoring guide.

---

## Scores

| Metric | Value | Grade |
|---|---|---|
| **Coverage Score** | **3.8** (34 pts / 9 domain tables) | 🟡 Moderate |
| **Integrity Score** | **96** (4 points deducted) | ✅ Good |

---

## Coverage Detail

**Domain tables (9):** CategoryTableNameTest, Customer, Department, Employee, EmployeeAudit, Order, OrderDetail, Product, Supplier

**Excluded — system (2):** SampleDBVersion (version table), sqlite_sequence (internal)  
**Excluded — lookup/junction (7):** CustomerDemographic (1 col), Location (1 col), Region (1 col), Union (1 col), EmployeeTerritory (2 cols), Shipper (2 cols), Territory (2 cols)  
*(lookup threshold: ≤ 2 non-PK columns)*

**Rule inventory:**

| Rule | File | Line | Type | Weight |
|---|---|---|---|---|
| Customer.Balance ≤ CreditLimit | declare_logic.py | 106 | constraint | 1 |
| Customer.Balance = sum(Order.AmountTotal where unshipped+ready) | declare_logic.py | 110 | sum | 3 |
| Order.AmountTotal = sum(OrderDetail.Amount) | declare_logic.py | 114 | sum | 3 |
| OrderDetail.Amount = Quantity × UnitPrice | declare_logic.py | 117 | formula | 2 |
| OrderDetail.UnitPrice copy from Product.UnitPrice | declare_logic.py | 120 | copy | 2 |
| Order: cannot ship unready orders | declare_logic.py | 202 | constraint | 1 |
| Product.UnitsInStock (formula via units_in_stock) | declare_logic.py | 245 | formula | 2 |
| Product.UnitsShipped = sum(OrderDetail.Quantity where unshipped) | declare_logic.py | 247 | sum | 3 |
| OrderDetail.ShippedDate = Order.ShippedDate (cascading formula) | declare_logic.py | 251 | formula | 2 |
| Customer.UnpaidOrderCount = count(Orders where unshipped) | declare_logic.py | 255 | count | 3 |
| Customer.OrderCount = count(Orders) | declare_logic.py | 259 | count | 3 |
| Order.OrderDetailCount = count(OrderDetails) | declare_logic.py | 261 | count | 3 |
| Employee: salary raise ≤ 20% | declare_logic.py | 272 | constraint | 1 |
| Order.OrderDate = now() | declare_logic.py | 355 | formula | 2 |
| Customer.CompanyName ≠ 'x' | simple_constraints.py | 22 | constraint | 1 |
| Employee.LastName ≠ 'x' | simple_constraints.py | 26 | constraint | 1 |
| Category.Description ≠ 'x' | simple_constraints.py | 35 | constraint | 1 |
| Events (8 — after_flush, commit, early, row) | declare_logic.py | various | event | 0 |
| Integration events (2 — Kafka, n8n) | integration.py | 97–98 | event | 0 |

**Weighted total:** 3×sum(3) + 3×count(3) + 4×formula(2) + 1×copy(2) + 6×constraint(1) = 9+9+8+2+6 = **34**  
**Coverage:** 34 / 9 = **3.8**

---

## Integrity Findings

| | File | Line | Finding | Points |
|---|---|---|---|---|
| 🔴 | logic/declare_logic.py | 106–355 | Rules in declare_logic.py instead of logic_discovery/ files | **-2** |
| 🟡 | declare_logic.py, integration.py | 7, 5 | Wildcard import `from database.models import *` (×2 files) | **-1** |
| 🟡 | logic/logic_discovery/ | — | Missing `__init__.py` | **-1** |

**Integrity:** 100 - 2 - 1 - 1 = **96**

### Hall Passes Applied

| | File | Line | Pattern |
|---|---|---|---|
| ✅ | integration.py | 97 | `kafka-publish` — send_kafka_message call |
| ✅ | integration.py | 98 | `kafka-publish` — n8n webhook (external I/O) |
| ✅ | declare_logic.py | 176 | `row-lookup` — single `.filter().one()` in commit_row_event |

### What's Clean

- ✅ No `session.query()` inside formula functions — all queries are in events (correct)
- ✅ No `as_expression=lambda row: my_func(row)` wrapping — both lambdas are direct computations
- ✅ `units_in_stock()` calling function references `row.UnitsInStock`, `row.UnitsShipped` directly — LB tracks dependencies correctly
- ✅ No side-effect assignments inside formula functions
- ✅ No hardcoded values in rule lambdas

---

## Action Items

| Priority | Item | Fix |
|---|---|---|
| 🔴 -2 | Rules in declare_logic.py | Migrate into logic_discovery/ files by use case — see suggested structure below |
| 🟡 -1 | Wildcard imports (×2) | Replace with explicit: `from database.models import Customer, Order, OrderDetail, Product, Employee` |
| 🟡 -1 | Missing `__init__.py` | `touch logic/logic_discovery/__init__.py` |

### Suggested Migration Structure

```
logic/logic_discovery/
  __init__.py
  check_credit.py         ← Customer.Balance, constraint
  order_amounts.py        ← Order.AmountTotal, OrderDetail.Amount, OrderDetail.UnitPrice
  inventory.py            ← Product.UnitsInStock, Product.UnitsShipped, OrderDetail.ShippedDate
  customer_metrics.py     ← Customer.UnpaidOrderCount, Customer.OrderCount
  order_metrics.py        ← Order.OrderDetailCount, Order constraint (unready), Order.OrderDate
  employee_audit.py       ← Employee constraint (salary), audit event
  app_integration.py      ← after_flush Kafka/n8n events (already in integration.py ✅)
  simple_constraints.py   ← already correct ✅
```

This migration would raise the Integrity Score from 96 → 98 and make the rules self-documenting by use case.

---

## Summary

nw_sample has **solid business logic** — 14 weighted rules across the core order/customer/inventory domain, well-structured and correctly implemented. The main issue is organizational: the rules predate the discovery pattern and live in `declare_logic.py`. The logic itself is clean (no dependency-tracking bugs, no procedural aggregates replacing rules). A migration to discovery files would complete the picture without changing any rule logic.

**Coverage 2.1** — moderate; the 16-table Northwind schema has several tables with no rules (Region, Territory, Shipper, Supplier, etc.) which is appropriate for a reference/demo project.  
**Integrity 96** — good; three minor organizational findings, no bugs.
