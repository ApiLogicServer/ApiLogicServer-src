---
created: 2026-11-07T17:00:00
created_by: claude-sonnet-5-5 (valjhuber@gmail.com)
use_case: hourly_employees
---

Feature: Hourly Employees

Hourly employees are employees with hours_worked (REAL) and hourly_rate (REAL). Hourly employees: salary must not exceed 5000 per week. Hourly employees may be assigned to a Union (optional); only Hourly employees may have a union_id. Unions have a name and a dues_rate (REAL). Hourly employees: union_dues = hours_worked * union.dues_rate (0 if no union assigned).
