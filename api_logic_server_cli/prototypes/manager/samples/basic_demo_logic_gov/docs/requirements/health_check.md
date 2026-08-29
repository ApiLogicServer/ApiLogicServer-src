# 🩺 Project Governance Report — basic_demo

**Date:** 2026-08-28

## Summary

| Project | Tables | Wtd Rules | Coverage | Integrity | Red Flag | Profile |
|---|---|---|---|---|---|---|
| basic_demo | 4 | 11 | **2.75** | **100** | — | 🟡 Moderate coverage, clean integrity |

> **Coverage** = weighted rules / domain tables (sum/count=3, formula/copy=2, constraint=1). Target ≥ 3.0 for mature projects.  
> **Integrity** = 100 minus demerits for anti-patterns. Target ≥ 95.  
> **Red Flag** = 🚨 if ≥ 10 FK tables and zero sum/count rules.

**Coverage Score: 2.75** (11 weighted rules / 4 tables) 🟡 Moderate  
**Integrity Score: 100** — no findings  
**Red Flag: none** (2 aggregation rules, 3 tables with incoming FKs)

---

## Coverage Detail

**Domain tables (4):** Customer, Product, Order, Item  
*(SysConfig excluded — Sys\* prefix)*

| Rule | Count | Weight | Points |
|---|---|---|---|
| `Rule.sum` | 2 | ×3 | 6 |
| `Rule.formula` | 1 | ×2 | 2 |
| `Rule.copy` | 1 | ×2 | 2 |
| `Rule.constraint` | 1 | ×1 | 1 |
| `Rule.after_flush_row_event` | 1 | ×0 | 0 (hook) |
| **Total** | | | **11** |

**Rules by file:**

| File | Rules |
|---|---|
| `logic/logic_discovery/place_order/check_credit.py` | sum×2, formula×1, copy×1, constraint×1 |
| `logic/logic_discovery/app_integration.py` | after_flush_row_event×1 (kafka-publish, hall pass) |
| `logic/logic_discovery/use_case.py` | stub only — no rules |

**Tables with no rules:** Product (acts only as a copy source; no rules declared on it)

---

## Integrity Findings

✅ No demerits found.

- `declare_logic.py` — no `Rule.*` declarations; correctly delegates to discovery
- `check_credit.py` — inline lambdas with dependencies directly visible to LogicBank; docstring is verbatim requirement text
- `app_integration.py` — Kafka publish via `after_flush_row_event` with `if_condition` ✅ hall pass: `kafka-publish`
- `use_case.py` — template stub only (`pass`), no rules

---

## Recommendation

**Product** has no rules of its own. The basic_demo prompt references `count_suppliers` — that rule is not yet present. Adding it would raise coverage to ≥ 3.5 (Strong):

```python
Rule.count(derive=models.Product.count_suppliers, as_count_of=models.ProductSupplier)
```

Requires a `ProductSupplier` table in the schema.
