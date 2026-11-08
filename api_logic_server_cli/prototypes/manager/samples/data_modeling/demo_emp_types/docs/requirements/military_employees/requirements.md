---
created: 2026-11-07T17:00:00
created_by: claude-sonnet-5-5 (valjhuber@gmail.com)
use_case: military_employees
---

Feature: Military Employees

Employees may also have a military classification, independent of employment type. Military employees have a branch (TEXT: 'Army', 'Navy', 'Air Force', 'Marines', 'Coast Guard'), a rank (TEXT), and service_years (INTEGER). Military employees receive a military_stipend (REAL) = service_years * 100. Total compensation for military employees = salary + military_stipend. Total compensation for non-military employees = salary.
