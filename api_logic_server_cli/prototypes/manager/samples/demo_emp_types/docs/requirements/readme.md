# demo_emp_types — Provenance

**Prompt:** `samples/prompts/emp_types.prompt.md`
**Created:** 2026-07-01
**AI model:** claude-sonnet-5
**User:** valjhuber@gmail.com

## Creation command

```bash
source venv/bin/activate
genai-logic create --project-name=demo_emp_types --db_url=sqlite:///samples/dbs/starter.sqlite
```

## Schema decisions made during 4a–4d analysis

- **4a (constants):** `SysConfig.max_hourly_weekly_salary` (5000.0) and `SysConfig.military_stipend_rate_per_year` (100.0) extracted from the "5000 per week" and "service_years * 100" literals in the prompt.
- **4b (FK inventory):** `Employee.dept_id → department.id`, `Employee.union_id → labor_union.id` (nullable), `CommissionOrder.employee_id → employee.id`.
- **4c (Request Pattern):** Not applicable — plain domain data entry with LogicBank-derived columns; no AI/email/Kafka side effects in this prompt.
- **4d (Type hierarchy / STI):** "Employees have a type that is one of: 'salaried', 'hourly', or 'commissioned'" triggered Single Table Inheritance — one `employee` table, `type TEXT NOT NULL` discriminator, nullable subtype-specific columns. Military classification is a second, independent axis on the same table (`is_military` flag + nullable military columns), not a second STI hierarchy, since a row can be both a type AND (optionally) military.

See `docs/requirements/ad-libs.md` for the full analysis, rule plan, and every assumption made beyond the prompt spec.

---

## Original XRD workflow notes (this folder's default purpose)

Place **Executable Requirements (XRD)** sets here for later work on this project, then say **"implement reqs `<name>`"** to AI. See `docs/training/implement_requirements.md`.
