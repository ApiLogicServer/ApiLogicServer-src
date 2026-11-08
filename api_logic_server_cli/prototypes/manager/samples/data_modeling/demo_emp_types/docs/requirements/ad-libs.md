## Ad-Libs Report
**7 items need your review. 9 FYIs — standard patterns, no action needed.**

---

## Walkthrough

1. **Basic data model** — department, employee (single table, `type` discriminator), labor_union, order.
2. **Derived/predicted schema additions** — constants to `sys_config` (hourly weekly cap 5000, stipend 100 per year); derived columns salary, union_dues, commission_total, order_count, military_stipend, total_compensation, department.total_salary; no Allocate, Request Pattern or EAI.
3. **Create db** — DDL + rebuild-from-database (4 domain tables; employee recreated once after `military` lost its default).
4. **Run impl-req** — 5 use cases, 18 rules: 2 sum, 1 count, 4 formula, 11 constraint.
5. **Test data / testing** — seed loaded with alp_init.py; 38 Behave scenarios, all pass; logic diagrams per use case; ontology generated (SHACL validation skipped: rdflib not installed).

<details markdown>
<summary>Full diagnostic detail (DDL change list, rule plan, rejected alternatives, replay log)</summary>

### 🟢 Diagnostic Appendix

#### Pre-Coding Analysis

**Phase 1 — Schema Impact Assessment** (read: the prompt, `database/models.py`; no message_formats)

| Requirement | Signal |
|

---

#### Execution Metrics

| Metric | Value |
|---|---|
| Strategy Used | Data-level STI on one Employee table; sums/count for rollups; type-branched formulas; constraints for every "only X may have Y" |
| CE Files Loaded | project CE, logic_bank_api.md, implement_requirements.md (parts), security.md (section), testing.md (parts) |
| Schema Read First | Yes |
| Sample Data Read | n/a (no message formats) |
| Subagent Used | No — single pass |
| Self-Verification | Yes — seed run, server started, Behave run, logs checked |
| Gate Test Run Count | 2 (the first run found 2 failures) |
| Gate Test Purpose | Final verification (the first run was also diagnostic) |
| Error Correction Loops | 4 |

```
Loop 1: Symptom: alp_init.py ModuleNotFoundError: config. Fix: added the sys.path line the CE says is already there (it was not). Root cause type: CE gap
Loop 2: Symptom: "military must be yes or no" on a row whose military was 'no'. Diagnosis: debug print showed the value is the literal string "'no'" (LogicBank applies a string server_default with its quotes). Fix: military is nullable with no default; NULL means non-military; constraint tolerates NULL. Root cause type: CE gap (string server defaults)
Loop 3: Symptom: union_dues did not follow a union dues_rate change. Diagnosis: the dependency scanner reads tokens that start with "row."; "str(row.union.dues_rate" starts with "str(". Fix: bind to a local first. Root cause type: CE gap (tokenizer note covers punctuation after a token, not a call wrapped around it)
Loop 4: Symptom: test "Leaving the military" got 400. Diagnosis: test patched only military; the constraint correctly rejected leftover branch/rank. Fix: test step clears them too. Root cause type: test error
```

---

### 🔴 Review Required
| Location | Issue | Action |
|---|---|---|
| `logic/logic_discovery/department_budget.py:11-30` | The manager exemption reads the signed-in user's role; security is not enabled in this project, so with no user the budget is always enforced and the exemption is not tested | Run `genai-logic add-auth` and test with a manager user if you need it |
| `database/models.py` (Employee.military) | `military` is nullable text, NULL meaning non-military (a default of 'no' breaks, see Loop 2); the prompt did not give a representation | Confirm yes/no/NULL is acceptable |
| `logic/logic_discovery/military_employees.py:36-40` | branch must be in the five listed values (spec) but a military employee is not required to have branch, rank or service_years (spec silent) | Say so if all three are required |
| `logic/logic_discovery/hourly_employees.py:22-30` | The weekly cap compares salary to `sys_config.max_hourly_weekly_salary`; changing the cap does not re-check existing rows | Confirm |
| `database/models.py` (LaborUnion) | Table named `labor_union` (class LaborUnion) because UNION is an SQL reserved word; the column stays `union_id` | Confirm the name |
| `logic/logic_discovery/employee_types.py:16-28` | A salaried employee's salary is the entered value (spec says nothing); the salary rule for hourly and commissioned lives here, so it appears under Employee Types rather than the hourly and commissioned use cases | Confirm |
| `logic/logic_discovery/hourly_employees.py:36-40`, `commissioned_employees.py:16`, `military_employees.py:38` | Null-exclusion constraints (hours_worked/hourly_rate only hourly, base_salary only commissioned, branch/rank/service_years only military) are inferred from the type structure, not stated | Remove any you do not want |

---

### 🟡 FYI
- `logic/logic_discovery/employee_types.py:33` — type must be salaried, hourly or commissioned (stated in the prompt)
- `logic/logic_discovery/military_employees.py:34` — military must be yes or no (inferred, needed for the classification axis)
- `logic/logic_discovery/military_employees.py:24-28` — `_military_valid` is a function (`calling=`) only to tolerate NULL
- `database/models.py` — money columns are NUMERIC(15,2); rates and hours are REAL
- `logic/logic_discovery/hourly_employees.py:12-20` — union dues rounded to 2 decimals; 0 when no union or not hourly
- `logic/logic_discovery/military_employees.py:14-21` — stipend is 0, not NULL, for non-military
- `logic/logic_discovery/department_budget.py:20-30` — constraint at equality is accepted (<=)
- `database/test_data/alp_init.py` — seed adds 2 departments, 1 union, 5 employees (all types, one military), 2 orders
- `ui/admin/admin-merge.yaml` — show_when for subtype columns; toone union tab group removed; `required` dropped on derived columns. admin.yaml itself not replaced (awaiting your OK)

</details>
