---
created: 2026-07-01T00:00:00
created_by: claude-sonnet-5 (valjhuber@gmail.com)
use_case: employee_compensation
---

Employees have a name, dept, and salary.
Employees have a type that is one of: 'salaried', 'hourly', or 'commissioned'.

Hourly employees are employees with hours_worked (REAL) and hourly_rate (REAL).
Hourly employees: salary = hours_worked * hourly_rate.
Hourly employees: salary must not exceed 5000 per week.
Hourly employees may be assigned to a Union (optional); only Hourly employees may have a union_id.
Unions have a name and a dues_rate (REAL).
Hourly employees: union_dues = hours_worked * union.dues_rate (0 if no union assigned).

Commissioned employees are employees who can have Orders; only Commissioned employees may have Orders.
Each Order has an amount and a customer name.
Commissioned employees: commission_total = sum of Order.amount.
Commissioned employees: salary = base_salary + commission_total.
