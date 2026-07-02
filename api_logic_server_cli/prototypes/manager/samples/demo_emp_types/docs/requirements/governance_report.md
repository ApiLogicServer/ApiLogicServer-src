# 🩺 Project Governance Report

## Summary

| Project | Tables | Wtd Rules | Coverage | Integrity | Red Flag | Effective LOC | Profile |
|---|---|---|---|---|---|---|---|
| demo_emp_types | 3 | 30 | **10.0** | **96** | — | 147 | ✅ Production-ready, well-governed |

> **Coverage** = weighted rules / domain tables (sum/count=3, formula/copy=2, constraint=1). Target ≥ 3.0 for mature projects.
> **Integrity** = 100 minus demerits for anti-patterns: broken dependency tracking, procedural aggregates replacing rules, events that should be rules. Target ≥ 95.
> **Red Flag** = 🚨 if ≥ 10 FK tables and zero sum/count rules — team has evidently not adopted aggregation rules.
> **Effective LOC** = project `.py` lines added/changed vs the generated scaffold (`database/models.py` excluded). See per-table breakdown below.
> See `docs/training/governance.md` for full scoring guide.

**Coverage Score: 10.0**  (30 weighted rules / 3 tables)   ✅ Strong
**Integrity Score: 96**  (4 demerits, 0 reviewed)
**Red Flag: none**  (2 aggregation rules, 4 FK tables — well below the ≥10-table threshold)
**Effective LOC: 147**  (vs scaffold baseline; database/models.py excluded)

────────────────────────────────────────
## COVERAGE DETAIL

**Domain tables (3):**
- `Department` — governed by `department_budget.py`
- `Employee` — governed by `department_budget.py`, `employee_compensation.py`, `military_classification.py`
- `CommissionOrder` — governed by `employee_compensation.py`

**Excluded (lookup, ≤2 non-PK columns):**
- `LaborUnion` (name, dues_rate)

**Excluded (SysConfig pattern, not a domain table):**
- `SysConfig`

**Rules: 2× sum, 0× count, 4× formula, 2× copy, 12× constraint** (weighted: 6 + 0 + 8 + 4 + 12 = 30)

| File | sum | count | formula | copy | constraint |
|---|---|---|---|---|---|
| `department_budget.py` | 1 | 0 | 0 | 0 | 1 |
| `employee_compensation.py` | 1 | 0 | 2 | 1 | 7 |
| `military_classification.py` | 0 | 0 | 2 | 1 | 4 |

────────────────────────────────────────
## EFFECTIVE LOC DETAIL

**Total Effective LOC: 147**
- logic_discovery: 147
- cross-cutting: 0  (no changes to api_discovery, security, integration, ui, or config beyond generated scaffold)

All scaffold-customizable files (`api/customize_api.py`, `api/expose_api_models.py`, `logic/declare_logic.py`, `security/declare_security.py`, etc.) remain at their generated baseline line counts — no cross-cutting customization.

**Per-table (logic_discovery LOC referencing each table — overlapping by design):**

| Table | Effective LOC |
|---|---|
| Employee | 147 |
| CommissionOrder | 79 |
| Department | 17 |

*(Employee's total reflects all three logic files, since each governs at least one Employee-typed subtype or aggregate; totals across tables exceed the 147 logic_discovery subtotal because files are shared across tables — this is expected.)*

────────────────────────────────────────
## INTEGRITY FINDINGS

🟡 -1  `database/models.py: employee.dept_id`
       FK column `dept_id` on `employee` has no covering index
       → Fix: `CREATE INDEX ix_employee_dept_id ON employee(dept_id);` then rebuild-from-database

🟡 -1  `database/models.py: employee.sys_config_id`
       FK column `sys_config_id` on `employee` has no covering index
       → Fix: `CREATE INDEX ix_employee_sys_config_id ON employee(sys_config_id);` then rebuild-from-database

🟡 -1  `database/models.py: employee.union_id`
       FK column `union_id` on `employee` has no covering index
       → Fix: `CREATE INDEX ix_employee_union_id ON employee(union_id);` then rebuild-from-database

🟡 -1  `database/models.py: commission_order.employee_id`
       FK column `employee_id` on `commission_order` has no covering index
       → Fix: `CREATE INDEX ix_commission_order_employee_id ON commission_order(employee_id);` then rebuild-from-database

**Checks that passed clean (no findings):**
- No raw `session.query()` or list-comprehension aggregates replacing sum/count rules
- No events assigning derived values that should be rules
- No broken dependency tracking — every `calling=` function references `row.attr` directly (no helper-hidden refs), no `as_expression=lambda row: my_func(row)` wrapping
- No side-effect assignments inside formula functions (one value per formula, throughout)
- Every `calling=` function has a one-line docstring
- All docstrings contain only verbatim requirement text — no implementation notes or field-mapping leakage
- No rules declared in `logic/declare_logic.py` outside the discovery pattern
- All 5 mapped tables have a single-column primary key
- Flat `logic/logic_discovery/` structure (no subdirectories) — no missing `__init__.py`
- STI null-exclusion constraints present and correctly guard every subtype-specific column (`hours_worked`, `hourly_rate`, `base_salary`, `branch`, `rank`, `service_years`)
- Type-guarded formulas (`_military_stipend`, `_union_dues`) correctly return `Decimal(0)`, never `None`, on the non-applicable branch
- `military != "yes"` guard form used correctly — avoids the LB tokenizer colon gotcha (`if not row.military:`)

────────────────────────────────────────
4 findings need attention (all low-severity, same root cause). Want me to fix them?
