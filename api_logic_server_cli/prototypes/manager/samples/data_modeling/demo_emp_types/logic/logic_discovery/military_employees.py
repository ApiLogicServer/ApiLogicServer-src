"""
Feature: Military Employees

Employees may also have a military classification, independent of employment type. Military employees have a branch (TEXT: 'Army', 'Navy', 'Air Force', 'Marines', 'Coast Guard'), a rank (TEXT), and service_years (INTEGER). Military employees receive a military_stipend (REAL) = service_years * 100. Total compensation for military employees = salary + military_stipend. Total compensation for non-military employees = salary.
"""

from decimal import Decimal
from logic_bank.logic_bank import Rule
from database import models

BRANCHES = ('Army', 'Navy', 'Air Force', 'Marines', 'Coast Guard')


def _military_stipend(row, old_row, logic_row):
    """Derive military_stipend: service_years * SysConfig military_stipend_per_year for military employees, 0 otherwise."""
    military = row.military
    years = row.service_years
    if military != "yes":
        return Decimal(0)
    rate = models.SysConfig.current(logic_row.session).military_stipend_per_year
    return round(Decimal(str(years or 0)) * Decimal(str(rate)), 2)


def _military_valid(row, old_row, logic_row):
    """Employee constraint: the military classification must be yes or no."""
    military = row.military
    return military is None or military in ("yes", "no")


def declare_logic():
    Rule.formula(derive=models.Employee.military_stipend, calling=_military_stipend)
    Rule.formula(derive=models.Employee.total_compensation,
                 as_expression=lambda row: row.salary + row.military_stipend if row.military == "yes" else row.salary)
    Rule.constraint(validate=models.Employee, calling=_military_valid,
                    error_msg="military must be yes or no")
    Rule.constraint(validate=models.Employee, as_condition=lambda row: row.branch is None or row.branch in BRANCHES,
                    error_msg="branch ({row.branch}) must be Army, Navy, Air Force, Marines or Coast Guard")
    Rule.constraint(validate=models.Employee,
                    as_condition=lambda row: row.military == "yes" or (row.branch is None and row.rank is None and row.service_years is None),
                    error_msg="branch, rank and service_years apply only to military employees")
