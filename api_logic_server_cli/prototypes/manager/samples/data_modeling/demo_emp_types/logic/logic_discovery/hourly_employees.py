"""
Feature: Hourly Employees

Hourly employees are employees with hours_worked (REAL) and hourly_rate (REAL). Hourly employees: salary must not exceed 5000 per week. Hourly employees may be assigned to a Union (optional); only Hourly employees may have a union_id. Unions have a name and a dues_rate (REAL). Hourly employees: union_dues = hours_worked * union.dues_rate (0 if no union assigned).
"""

from decimal import Decimal
from logic_bank.logic_bank import Rule
from database import models


def _union_dues(row, old_row, logic_row):
    """Derive union_dues: hours_worked * union dues_rate for hourly employees (0 if no union, or not hourly)."""
    emp_type = row.type
    hours = row.hours_worked
    if emp_type != 'hourly' or row.union is None:
        return Decimal(0)
    dues_rate = row.union.dues_rate
    return round(Decimal(str(hours or 0)) * Decimal(str(dues_rate or 0)), 2)


def _hourly_salary_within_cap(row, old_row, logic_row):
    """Employee constraint: an hourly employee's weekly salary must not exceed SysConfig max_hourly_weekly_salary."""
    emp_type = row.type
    salary = row.salary
    if emp_type != 'hourly':
        return True
    cap = models.SysConfig.current(logic_row.session).max_hourly_weekly_salary
    return salary <= cap


def declare_logic():
    Rule.formula(derive=models.Employee.union_dues, calling=_union_dues)
    Rule.constraint(validate=models.Employee, calling=_hourly_salary_within_cap,
                    error_msg="Hourly salary ({row.salary}) exceeds the weekly maximum")
    Rule.constraint(validate=models.Employee, as_condition=lambda row: row.type == 'hourly' or row.union_id is None,
                    error_msg="Only hourly employees may have a union_id")
    Rule.constraint(validate=models.Employee,
                    as_condition=lambda row: row.type == 'hourly' or (row.hours_worked is None and row.hourly_rate is None),
                    error_msg="hours_worked and hourly_rate apply only to hourly employees")
