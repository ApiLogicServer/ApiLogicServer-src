## Ad-Libs Report
**9 items need your review. 13 FYIs — standard patterns, no action needed.**

Every assumption or guess made beyond `project_creation_prompt.md` (the prompt, `samples/prompts/emp_types.prompt.md`).

---

## Walkthrough

1. **Basic data model** — Department, Employee (single table for all types: STI), LaborUnion, Order, plus the starter `sys_config`.
2. **Derived/predicted schema additions** — 2 constants to SysConfig (`max_hourly_weekly_salary` 5000, `military_stipend_per_service_year` 100); FKs `employee.dept_id`, `employee.union_id`, `order.employee_id`; derived columns `department.total_salary`, `employee.salary/union_dues/commission_total/order_count/military_stipend/total_compensation`; no Allocate; no Request Pattern.
3. **Create db** — DDL in `database/ddl_emp_types.sql` + `rebuild-from-database` (5 tables).
4. **Run impl-req** — 3 logic files: 2 sum, 1 count, 4 formula, 13 constraint (one of them role-aware via `Security.current_user_has_role('manager')`). Security: Keycloak (`add-auth --provider-type=keycloak --db-url=localhost`).
5. **Test data / testing** — `database/test_data/alp_init.py` seeded 2 departments, 2 unions, 5 employees, 2 orders (all derived values computed by the rules). No Behave tests (not requested). API checked with curl as Keycloak users.

## Creation Steps (commands actually run, from the Manager root unless noted)

```bash
source venv/bin/activate
genai-logic create --project-name=demo_emp_types --db_url=sqlite:///samples/dbs/starter.sqlite
cd demo_emp_types && genai-logic add-auth --provider-type=keycloak --db-url=localhost && cd ..
sqlite3 demo_emp_types/database/db.sqlite < demo_emp_types/database/ddl_emp_types.sql
cd demo_emp_types && genai-logic rebuild-from-database --db_url=sqlite:///database/db.sqlite && cd ..
# wrote logic/logic_discovery/{department_budget,employee_pay,military_compensation}.py + docs/requirements/<use_case>/requirements.md
cd demo_emp_types && PROJECT_DIR=$(pwd) python database/test_data/alp_init.py && cd ..   # failed: see Loop 1
# Loop 1 fix: dropped/recreated employee + order without the military TEXT default, cleared the partial seed rows
cd demo_emp_types && genai-logic rebuild-from-database --db_url=sqlite:///database/db.sqlite && cd ..
cd demo_emp_types && PROJECT_DIR=$(pwd) python database/test_data/alp_init.py && cd ..   # OK
python system/ApiLogicServer-Internal-Dev/logic_diagram_gv.py demo_emp_types --each
cd demo_emp_types && python api_logic_server_run.py > logs/server_verify.log 2>&1 &     # then curl checks, then kill <PID>
```

<details markdown>
<summary>Full diagnostic detail (DDL change list, rule plan, rejected alternatives, replay log)</summary>

### 🟢 Diagnostic Appendix

#### Pre-Coding Analysis

**Phase 1 — Schema Impact Assessment**
Files read: `project_creation_prompt.md` (whole prompt), `database/models.py` (starter: SysConfig only)

| Step | Signal |
|---|---|
| Department budget | Rule.sum (total_salary) + role-aware Rule.constraint |
| Employee types / hourly / commissioned | STI (type discriminator); Rule.formula salary, union_dues; Rule.sum commission_total; Rule.count order_count; constraints |
| Military axis | second discriminator `military` TEXT yes/no; Rule.formula military_stipend, total_compensation |

DDL change list:

| Table | Change | Reason |
|---|---|---|
| sys_config | ADD max_hourly_weekly_salary REAL 5000 | constant (hourly cap) |
| sys_config | ADD military_stipend_per_service_year REAL 100 | constant (stipend rate) |
| department | CREATE (name, budget, total_salary) | total_salary: Rule.sum |
| labor_union | CREATE (name, dues_rate) | lookup for union_id |
| employee | CREATE (STI: type, salary, hours_worked, hourly_rate, union_id, union_dues, base_salary, commission_total, order_count, military, branch, rank, service_years, military_stipend, total_compensation) | salary/union_dues/military_stipend/total_compensation: Rule.formula; commission_total: Rule.sum; order_count: Rule.count |
| order | CREATE (employee_id, customer_name, amount) | child of commissioned employees |

Closing check (after coding): every derived column has a writer: total_salary (sum), salary (formula), union_dues (formula), commission_total (sum), order_count (count), military_stipend (formula), total_compensation (formula). Confirmed against `database/models.py`.

**Phase 2 — CE / Pattern Assessment**
Files read: `logic_bank_api.md`, `logic_bank_patterns.md`, `security.md` ("Roles inside business rules")

| Use case | Rule Plan |
|---|---|
| department_budget | Rule.sum(Department.total_salary) + Rule.constraint(calling=, manager role exempt) |
| employee_pay | Rule.formula(salary, type-branched) + Rule.formula(union_dues) + Rule.sum(commission_total) + Rule.count(order_count) + 7 constraints |
| military_compensation | Rule.formula(military_stipend) + Rule.formula(total_compensation) + 5 constraints |

Anti-patterns confirmed clear:
- [x] No parent flag where Rule.count on child table is correct (order_count is a Rule.count)
- [x] No `as_expression=lambda row: my_func(row)` — multi-line logic uses `calling=`
- [x] No `session.query()` inside formula or row_event (SysConfig read via `SysConfig.current(session)`)
- [x] No punctuation glued to row attribute tokens (row reads bound to locals first)
- [x] No SQLAlchemy polymorphic subclasses; all rules on `models.Employee`

#### Execution Metrics

| Metric | Value |
|---|---|
| Strategy Used | Data-level STI on `employee` (two independent axes), SysConfig for constants, role check inside one constraint |
| CE Files Loaded | `.github/copilot-instructions.md`, `docs/training/logic_bank_api.md`, `implement_requirements.md`, `logic_bank_patterns.md`, `RequestObjectPattern.md`, `security.md`, `health_check.md` |
| Schema Read First | Yes |
| Sample Data Read | n/a (no message formats) |
| Subagent Used | No — single pass |
| Self-Verification | Yes — seed values checked in sqlite, server started, 10 curl checks, als.log checked |
| Error Correction Loops | 1 |

```
Loop 1:
  Symptom:   seed failed: "military ('no') must be 'yes' or 'no'" for employees that did not set military
  Diagnosis: read logic_bank/exec_row_logic/logic_row.py _eager_defaults: LogicBank applies the column's
             server_default text as-is, so TEXT DEFAULT 'no' becomes the 4-character string 'no' WITH its quotes
  Fix:       removed the DEFAULT (military TEXT NOT NULL, callers must send 'yes' or 'no'); recreated employee/order
             (empty), rebuild-from-database, seed sets military explicitly
  Time:      ~3 min
  Root cause type: platform behavior (LogicBank eager defaults for quoted TEXT server defaults), not covered by the CE
```

---

### 🔴 Review Required
| Location | Issue | Action |
|---|---|---|
| `logic/logic_discovery/department_budget.py:17-23` | No signed-in user (seed script, a direct/batch insert, `SECURITY_ENABLED=False`) is treated as "not a manager": the budget is enforced. | Confirm; the alternative is to exempt system writes. |
| `logic/logic_discovery/department_budget.py:29-38` | The exemption is for whoever commits the transaction. Nothing records that a manager approved an overage, and once a department is over budget, any non-manager change that alters that department's total_salary (a salary change, even a decrease, or a budget change) is rejected while the total is still over budget. | Decide whether an approval record / audit is needed, and whether non-managers may make changes that reduce an overage. |
| `logic/logic_discovery/department_budget.py:20` | Exact role name `manager` only. `sa` (Keycloak `admin`) is NOT exempt; verified: admin is rejected. | Confirm `sa`/admin should not exceed the budget. |
| `logic/logic_discovery/employee_pay.py:60-67` | "salary must not exceed 5000 per week": hourly salary is taken to be a weekly amount (hours_worked = hours per week). Salaried and commissioned salary periods are unstated; `Department.total_salary` sums all types as if same-period (seed uses weekly amounts). | State the pay period for each type, or whether total_salary should normalize. |
| `logic/logic_discovery/employee_pay.py:48` | Salaried salary is entered directly (prompt gives no formula). | Confirm. |
| `logic/logic_discovery/employee_pay.py:41-46` | Missing hours/rate/base salary count as 0 (no "required" constraint); the prompt does not say they are required for their type. | Say if hours_worked/hourly_rate (hourly) and base_salary (commissioned) must be required. |
| `database/ddl_emp_types.sql` (employee.military) | `military` is TEXT 'yes'/'no' and REQUIRED with no default (Loop 1: LogicBank copies a TEXT default with its quotes). API callers must send `"military": "no"` for non-military employees. Branch/rank/service_years are not required for military employees. | Confirm the required flag, or ask for a default via an event/model default. |
| `logic/logic_discovery/military_compensation.py:48` | Branch values enforced by a constraint over the prompt's list (no `branch` lookup table). | Confirm, or ask for a lookup table (FK) if the list will change. |
| `database/models.py` (LaborUnion) | Domain-floor constraints NOT added (spec does not state them): `budget >= 0`, `hours_worked >= 0`, `hourly_rate >= 0`, `Order.amount > 0`, `dues_rate >= 0`, `service_years >= 0`. | Say which you want. |

---

### 🟡 FYI
- `database/ddl_emp_types.sql` — Single Table Inheritance: one `employee` table, `type` discriminator, all subtype columns nullable; no SQLAlchemy subclasses (per CE platform constraint).
- `database/ddl_emp_types.sql` — Union table named `labor_union` (`union` is an SQL keyword); FK column keeps the prompt's name `union_id`, relationship `Employee.union`.
- `database/ddl_emp_types.sql` — Order table named `"order"` (quoted keyword, same as basic_demo); `customer_name` TEXT NOT NULL, `amount` NUMERIC(15,2).
- `database/ddl_emp_types.sql` — `employee.dept_id` NOT NULL (prompt: "Employees have a name, dept").
- `database/ddl_emp_types.sql` — Money columns NUMERIC(15,2); hours_worked, hourly_rate, dues_rate REAL as the prompt states; military_stipend NUMERIC(15,2) (prompt says REAL; Numeric chosen for money).
- `logic/logic_discovery/employee_pay.py:66`, `military_compensation.py:31` — 5000 and 100 moved to `sys_config` (read with `SysConfig.current(session)`, no FK). A change to these settings applies on the next write of each employee; it does not re-derive existing rows.
- `logic/logic_discovery/employee_pay.py:57` — union_dues reads `union.dues_rate` live (verified: changing Local 42's dues_rate re-derived Bob's dues 60 -> 100).
- `logic/logic_discovery/employee_pay.py:72,77` — "only Commissioned employees may have Orders" implemented as Rule.count(order_count) + constraint (so a zero-amount order is also caught, and a commissioned employee with orders cannot be changed to another type).
- `logic/logic_discovery/employee_pay.py:78-80` — inferred STI null-exclusion constraints: hours_worked, hourly_rate (hourly only), base_salary (commissioned only).
- `logic/logic_discovery/military_compensation.py:49-51` — inferred null-exclusion constraints: branch, rank, service_years (military only).
- `logic/logic_discovery/employee_pay.py:74`, `military_compensation.py:47` — type and military values validated against the prompt's lists.
- `logic/logic_discovery/*.py` — type-guarded formulas return 0 (not NULL) for non-applicable rows; "must not exceed" read as `<=`.
- `ui/admin/admin-merge.yaml` — show_when for all subtype fields (`record["Type"] == "hourly"` / `"commissioned"`, `record["military"] == "yes"`), and the nullable `union` toone tab removed. Written to admin-merge.yaml only: `admin.yaml` still holds just SysConfig until you approve the swap (backup admin.yaml -> admin.yaml.bak, copy admin-merge.yaml -> admin.yaml).

</details>
