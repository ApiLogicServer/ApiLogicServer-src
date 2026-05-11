# 🩺 nw_sample_nocust — Project Governance Report
**Date:** 2026-05-10  
**Scoring:** Coverage Score (weighted rules / domain tables) + Integrity Score (100 - demerits)  
**Reference:** `docs/training/health_check.md`, `docs/training/governance.md`

---

## Summary

| Project | Tables | Wtd Rules | Coverage | Integrity | Red Flag | Profile |
|---|---|---|---|---|---|---|
| nw_sample_nocust | 16 | 0 | **0.0** | n/a | 🚨 | ℹ️ Intentionally empty — "new from db" reference |

---

> **ℹ️ About this project**  
> `nw_sample_nocust` is the reference "new from database" project — what you get immediately
> after `genai-logic create --db_url=nw`. No customization, no rules added. It exists to show
> the baseline and to contrast with `nw_sample` (same schema, rules added).  
> See `../nw_sample/nw_sample_governance_report.md` for the comparison.

---

## Scores

| Metric | Value | Grade |
|---|---|---|
| **Coverage Score** | **0.0** (0 weighted rules / 16 tables) | 🔴 Weak |
| **Integrity Score** | **100** (nothing to demerit) | ✅ — |
| **Red Flag** | **🚨 RAISED** | 16 FK tables, zero aggregation rules |

---

## 🚨 Red Flag

**Condition met:** 10 tables with incoming foreign keys AND zero `Rule.sum` + zero `Rule.count`

```
🚨 RED FLAG: 16 tables with child relationships, zero aggregation rules.
   Suggestion: schedule rules training or consulting engagement.
   To acknowledge: add @health-check: red-flag-suppress to use_case.py docstring.
```

**In this case the flag is expected** — this project is intentionally the pre-rules baseline.  
See the contrast in `../nw_sample/nw_sample_governance_report.md`:  
- nw_sample: Coverage 2.1, Integrity 96, no red flag  
- nw_sample_nocust: Coverage 0.0, Red Flag raised ← you are here

---

## Coverage Detail

**Domain tables (16):** Category, Customer, CustomerDemographic, Department, Employee,
EmployeeAudit, EmployeeTerritory, Location, Order, OrderDetail, Product, Region, Shipper,
Supplier, Territory, Union  
*(SampleDBVersion excluded — system/version table)*

**Tables with incoming FKs (10):** Order, OrderDetail, Employee, EmployeeTerritory,
EmployeeAudit, Product, CustomerDemographic, Department, Territory, Location

**Rule inventory:** None. The only declaration is `Rule.early_row_event_all_classes`
for stamping/opt-locking — infrastructure, weight 0.

**Weighted total:** 0  
**Coverage:** 0 / 16 = **0.0**

---

## Integrity Detail

**No demerits applicable** — there is no logic to evaluate. The project is a clean
generated stub. Integrity score of 100 is vacuously true, not an achievement.

**Infrastructure present (correct):**
- ✅ `early_row_event_all_classes` — date/user stamping + opt-locking (disabled by default, correctly stubbed)
- ✅ `logic/logic_discovery/use_case.py` — discovery stub, ready for rules
- ✅ `logic/logic_discovery/auto_discovery.py` — discovery wiring in place

---

## What This Looks Like After Adding Rules

Run the health check on `../nw_sample/` to see the same schema with rules added:

| | nw_sample_nocust | nw_sample |
|---|---|---|
| Coverage Score | 0.0 | 2.1 |
| Integrity Score | 100 (vacuous) | 96 |
| Red Flag | 🚨 Raised | — None |
| Weighted rules | 0 | 34 |
| Rule.sum/count | 0 | 6 |
| Rule.formula/copy | 0 | 5 |
| Rule.constraint | 0 | 6 |

The jump from 0.0 → 2.1 coverage and red flag → no flag represents the value of
adopting rules on an existing project. The rules in `nw_sample` were added to
`declare_logic.py` (pre-discovery pattern) — migrating them to `logic/logic_discovery/`
files would raise the Integrity score from 96 → 98.

---

## Summary

This project is **intentionally empty** — it is the correct output of `genai-logic create`
before any developer customization. The red flag is expected and informative, not a problem
to fix in this project.

Its governance value is as a **reference baseline**: a team whose production project looks
like this report has not adopted rules. A team whose production project looks like
`nw_sample` has made a solid start.
