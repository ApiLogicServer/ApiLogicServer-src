# demo_emp_types — Ad-Libs Report

**1 item needs your review. 11 FYIs — standard patterns, no action needed.**

---

## Pre-Coding Analysis

**Phase 1 — Schema Impact Assessment**

| Signal | Finding |
|---|---|
| Type hierarchy (STI) | Prompt says "type that is one of: 'salaried', 'hourly', or 'commissioned'" → STI on `employee`, `type TEXT NOT NULL` discriminator |
| Second classification axis | "military classification, independent of employment type" → `is_military` flag + nullable military-only columns, same table |
| Rule.sum needed | `Department.total_salary` = sum of `Employee.salary`; `Employee.commission_total` = sum of `CommissionOrder.amount` |
| Constants (Step 4a) | "5000 per week" and "service_years * 100" are rate/threshold literals → `SysConfig` columns |
| FK inventory (Step 4b) | `dept_id`, `union_id` (nullable), `employee_id` on the order table |
| Request Pattern (Step 4c) | Not applicable — plain domain data entry with derived columns |

**DDL change list:**

| Table | Change | Reason |
|---|---|---|
| `sys_config` | ADD COLUMN `max_hourly_weekly_salary NUMERIC(15,2) DEFAULT 5000.0` | Hourly weekly cap constant |
| `sys_config` | ADD COLUMN `military_stipend_rate_per_year REAL DEFAULT 100.0` | Military stipend rate constant |
| — | CREATE TABLE `department` | Header table with derived `total_salary` |
| — | CREATE TABLE `labor_union` | Lookup table for union dues rate |
| — | CREATE TABLE `employee` (STI) | Base + all 3 subtypes + military axis, one physical table |
| — | CREATE TABLE `commission_order` | Line-item table for commissioned employees |

**Phase 2 — CE / Pattern Assessment**

| Use case | Rule plan |
|---|---|
| `department_budget` | `Rule.sum` + `Rule.constraint` |
| `employee_compensation` | `Rule.copy` (SysConfig), `Rule.formula` (type-branched salary, union_dues), `Rule.sum` (commission_total), `Rule.constraint` × 6 (hourly cap, union-hourly-only, order-commissioned-only, amount>0, 2 null-exclusions) |
| `military_classification` | `Rule.copy` (SysConfig), `Rule.formula` (military_stipend, total_compensation), `Rule.constraint` × 4 (3 null-exclusions + branch enum check) |

Anti-patterns confirmed clear:
- [x] No parent flag where Rule.count/sum on child table is correct
- [x] No `as_expression=lambda row: my_func(row)` — used `calling=my_func` for multi-line logic
- [x] No `session.query()` inside formula or constraint
- [x] All derived/working values are physical columns with their own `Rule.formula`/`Rule.copy`/`Rule.sum`
- [x] No `__mapper_args__` / SQLAlchemy polymorphic subclasses added — data-level STI only, all rules on `models.Employee`

**Implementation Plan:**

| Step | What was planned |
|---|---|
| 1 | Run DDL (SysConfig constants + 4 domain tables) + `rebuild-from-database` |
| 2 | Write `department_budget.py` — Rule.sum + Rule.constraint |
| 3 | Write `employee_compensation.py` — type-branched salary formula, hourly cap, union rules, commission sum, order constraint |
| 4 | Write `military_classification.py` — stipend formula, total_compensation, null-exclusions, branch enum check |
| 5 | Add `show_when` to `admin.yaml` for all subtype-specific fields (Method 4: auto-generated) |
| 6 | Seed `alp_init.py` with all 3 types + 2 military examples across 2 departments |
| 7 | Verify via live API: hourly cap, union-hourly-only, department budget, commissioned-only orders, branch enum, valid insert |

---

## Execution Metrics

| Metric | Value |
|---|---|
| Strategy Used | Method 4 System Creation Services — STI for employee type, independent boolean axis for military status |
| CE Files Loaded | `implement_requirements.md`, `logic_bank_api.md`, `logic_bank_patterns.md` (project CE v3.24, already encoding STI lessons from a prior test run of this same prompt as `demo_emp_types_1`) |
| Schema Read First | Yes — full 4a-4d analysis completed before any DDL |
| Sample Data Read | N/A — no message formats, plain domain prompt |
| Self-Verification | Yes — server started, live API POSTs tested against all constraints, results confirmed |
| Error Correction Loops | 2 |

**Error Correction Loops:**

```
Loop 1:
  Symptom:   LBActivateException: Missing Attrs ['Employee.X:`: - formula'] during seed insert
  Diagnosis: LogicBank's dependency scanner whitespace-splits the calling= function's source text
             (including comments/docstrings) and collects tokens starting with "row.". A code
             comment I wrote to document the known tokenizer gotcha itself contained the literal
             text "row.X:`" as an illustrative example — the scanner picked that up as a fake
             dependency token on models.Employee.
  Fix:       Reworded the comment in military_classification.py to describe the gotcha without
             including a literal "row.<name>:" substring.
  Time:      ~2 min
  Root cause type: Self-inflicted (documentation text mimicking the exact pattern it warned against)

Loop 2:
  Symptom:   Carol Nguyen (hourly, union assigned) seeded with union_dues=0 instead of 200
             (40 hours * 5.0 dues_rate)
  Diagnosis: Employee and LaborUnion were both new, uncommitted objects in the same session;
             Carol was constructed with union=local_42 (relationship object, not a flushed id).
             Rule.formula's calling function reads row.union_id directly at Row Logic time —
             unlike Rule.sum's aggregate-adjustment machinery, this scalar FK read happens before
             SQLAlchemy's flush-time dependency resolution assigns the real FK value, so
             row.union_id was still None when the formula first evaluated it.
  Fix:       Restructured alp_init.py to commit Department/LaborUnion rows first, then construct
             Employee rows using their real integer ids (dept_id=engineering.id, union_id=local_42.id)
             instead of relationship objects, matching the pattern already used successfully in
             demo_emp_types_1's seed script.
  Time:      ~5 min
  Root cause type: Missing read (seed-ordering pattern not called out explicitly in local CE,
             though demo_emp_types_1's working seed script already used it)
```

---

## 🔴 Review Required

| Location | Issue | Action |
|---|---|---|
| `database/db.sqlite` schema | Named the commissioned-employee line-item table `commission_order` rather than a literal `order` table — prompt just says "Orders" without naming the table. Chosen to avoid `order` being a SQL reserved word requiring quoting everywhere. | Confirm the name `CommissionOrder` (API resource `/api/CommissionOrder/`) is acceptable, or rename if a different convention is preferred. |

---

## 🟡 FYI

- `database/db.sqlite` — used STI (Single Table Inheritance) per CE Step 4d: one `employee` table with `type` discriminator and nullable subtype-specific columns (`hours_worked`, `hourly_rate`, `union_id`, `union_dues`, `base_salary`, `commission_total`); no SQLAlchemy polymorphic subclasses added to `models.py` (LogicBank/SAFRS platform constraint).
- `database/db.sqlite` — `SysConfig.max_hourly_weekly_salary` (default 5000.0) extracted from "5000 per week" per constant-extraction guidance (Step 4a).
- `database/db.sqlite` — `SysConfig.military_stipend_rate_per_year` (default 100.0) extracted from "service_years * 100" per constant-extraction guidance (Step 4a).
- `database/db.sqlite` — `is_military` modeled as an explicit `INTEGER` flag (0/1) rather than inferring military status from `branch`/`rank`/`service_years` being non-null — makes the independent classification axis an explicit, queryable column, consistent with "may also have a military classification" phrasing.
- `logic/logic_discovery/employee_compensation.py:69-79` — added null-exclusion constraints for `hours_worked`, `hourly_rate`, `base_salary` (must be null for the wrong employee type) — mechanical inference from the STI structure, not explicitly requested.
- `logic/logic_discovery/military_classification.py:35-46` — added null-exclusion constraints for `branch`, `rank`, `service_years` (must be null when `is_military=0`) — same mechanical inference applied to the independent military axis.
- `logic/logic_discovery/military_classification.py:48-51` — added a `Rule.constraint` validating `branch` against the 5 values the prompt listed ('Army', 'Navy', 'Air Force', 'Marines', 'Coast Guard') — domain-standard validation per "Spec = Floor, Not Ceiling" (add validation constraints the spec implied but didn't explicitly ask for).
- `logic/logic_discovery/employee_compensation.py:64-66` — added `Rule.constraint(CommissionOrder.amount > 0)` per "Spec = Floor, Not Ceiling" line-item guidance (always add quantity/amount > 0 on line items, even if not explicitly requested).
- `ui/admin/admin.yaml` — performed the admin.yaml swap (backup → `admin.yaml.bak`, then `admin-merge.yaml` → `admin.yaml`) since this is a brand-new project created moments earlier with no prior user customizations to lose.
- `ui/admin/admin.yaml` — added `show_when` entries for all subtype-specific `Employee` fields (hourly fields shown only when `Type == 'hourly'`, commissioned fields only when `Type == 'commissioned'`, military fields only when `is_military == 1`) per Method 4 auto-generation guidance.
- API consumers — the `Employee.type` column is exposed over JSON:API as attribute key **`Type`** (capitalized), not `type` — SAFRS renames it internally because `type` is JSON:API's reserved resource-discriminator key at the `data` object level. Confirmed by live testing; Python/LogicBank code still uses `row.type` (the real SQLAlchemy attribute) throughout.
- `database/models.py` — `hours_worked`, `hourly_rate`, `dues_rate` (LaborUnion), and `military_stipend` kept as `REAL`/`Float` per the prompt's explicit `(REAL)` type annotations; all other monetary/derived columns use `NUMERIC(15,2)` per domain convention (money should not be `Float`).
- `database/test_data/alp_init.py` — seeded 2 departments, 1 union, 6 employees (2 salaried incl. 1 military, 2 hourly incl. 1 unionized + 1 military, 2 commissioned incl. 1 military), 3 commission orders — chosen to exercise every rule path (both STI branches × both military states, union assigned/unassigned).

---

## Creation Steps

1. `genai-logic create --project-name=demo_emp_types --db_url=sqlite:///samples/dbs/starter.sqlite`
2. `sqlite3 demo_emp_types/database/db.sqlite` — wrote DDL: 2 `sys_config` ALTER COLUMNs, 4 CREATE TABLEs (`department`, `labor_union`, `employee`, `commission_order`)
3. `genai-logic rebuild-from-database --db_url=sqlite:///database/db.sqlite` (from `demo_emp_types/`)
4. `logic/logic_discovery/` — wrote 3 logic files (`department_budget.py`, `employee_compensation.py`, `military_classification.py`), 18 rules total (2 sum, 2 copy, 4 formula, 10 constraint)
5. `docs/requirements/<use_case>/requirements.md` — wrote 3 verbatim requirement excerpts
6. `ui/admin/admin.yaml` — swapped in `admin-merge.yaml`, added 8 `show_when` entries
7. `PROJECT_DIR=$(pwd) PYTHONPATH=$(pwd) python database/test_data/alp_init.py` — seeded 2 departments, 1 union, 6 employees, 3 commission orders
8. Started server, ran 7 live API verification calls (hourly cap, union-hourly-only, department budget, commissioned-only orders, valid insert, branch enum, STI null-exclusion), all passed, cleaned up test row
