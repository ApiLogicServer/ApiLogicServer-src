---
created: 2026-10-29T17:50:00
created_by: claude-opus-5-5 (valjhuber@gmail.com)
use_case: department_budget
source: samples/prompts/emp_types.prompt.md (lines 6-9)
---

Departments have a name and a budget.
Department.total_salary = sum of Employee.salary (all types).
Department.total_salary must not exceed Department.budget.
A user with the manager role may exceed the budget; other users may not.
