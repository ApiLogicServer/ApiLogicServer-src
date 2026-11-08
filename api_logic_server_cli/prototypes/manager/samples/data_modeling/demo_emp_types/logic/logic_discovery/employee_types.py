"""
Feature: Employee Types

Employees have a name, dept, and salary. Employees have a type that is one of: 'salaried', 'hourly', or 'commissioned'.

Hourly employees: salary = hours_worked * hourly_rate.

Commissioned employees: salary = base_salary + commission_total.
"""

from decimal import Decimal
from logic_bank.logic_bank import Rule
from database import models


def _salary(row, old_row, logic_row):
    """Derive salary: hourly = hours_worked * hourly_rate; commissioned = base_salary + commission_total; salaried = as entered."""
    emp_type = row.type
    hours = row.hours_worked
    rate = row.hourly_rate
    base = row.base_salary
    commission = row.commission_total
    entered = row.salary
    if emp_type == 'hourly':
        return round(Decimal(str(hours or 0)) * Decimal(str(rate or 0)), 2)
    if emp_type == 'commissioned':
        return (base or Decimal(0)) + (commission or Decimal(0))
    return entered or Decimal(0)


def declare_logic():
    Rule.formula(derive=models.Employee.salary, calling=_salary)
    Rule.constraint(validate=models.Employee, as_condition=lambda row: row.type in ('salaried', 'hourly', 'commissioned'),
                    error_msg="Employee type ({row.type}) must be salaried, hourly or commissioned")
