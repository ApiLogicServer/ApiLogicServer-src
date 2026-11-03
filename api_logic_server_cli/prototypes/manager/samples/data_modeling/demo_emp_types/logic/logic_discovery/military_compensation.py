"""
Employees may also have a military classification, independent of employment type.
Military employees have a branch (TEXT: 'Army', 'Navy', 'Air Force', 'Marines', 'Coast Guard'),
a rank (TEXT), and service_years (INTEGER).
Military employees receive a military_stipend (REAL) = service_years * 100.
Total compensation for military employees = salary + military_stipend.
Total compensation for non-military employees = salary.

version: 1.0
created: 2026-10-29T17:48:00
created_by: claude-opus-5-5 (valjhuber@gmail.com)
"""

from decimal import Decimal
from logic_bank.logic_bank import Rule
from logic_bank.exec_row_logic.logic_row import LogicRow
from database import models

MILITARY_BRANCHES = ('Army', 'Navy', 'Air Force', 'Marines', 'Coast Guard')
MILITARY_VALUES = ('yes', 'no')


def declare_logic():
    """Business logic rules for Military Compensation use case (military axis, independent of type)."""

    def _military_stipend(row: models.Employee, old_row: models.Employee, logic_row: LogicRow):
        """Derive military_stipend: service_years * SysConfig.military_stipend_per_service_year for military employees, 0 otherwise."""
        military = row.military
        years = row.service_years or 0
        if military != "yes":
            return Decimal(0)
        rate = models.SysConfig.current(logic_row.session).military_stipend_per_service_year
        return Decimal(str(years)) * Decimal(str(rate or 0))

    def _total_compensation(row: models.Employee, old_row: models.Employee, logic_row: LogicRow):
        """Derive total_compensation: salary + military_stipend for military employees; salary for non-military."""
        military = row.military
        salary = row.salary or Decimal(0)
        stipend = row.military_stipend or Decimal(0)
        if military == "yes":
            return salary + stipend
        return salary

    Rule.formula(derive=models.Employee.military_stipend, calling=_military_stipend)
    Rule.formula(derive=models.Employee.total_compensation, calling=_total_compensation)

    Rule.constraint(validate=models.Employee, as_condition=lambda row: row.military in MILITARY_VALUES, error_msg="military ({row.military}) must be 'yes' or 'no'")
    Rule.constraint(validate=models.Employee, as_condition=lambda row: row.branch is None or row.branch in MILITARY_BRANCHES, error_msg="branch ({row.branch}) must be one of: Army, Navy, Air Force, Marines, Coast Guard")
    Rule.constraint(validate=models.Employee, as_condition=lambda row: row.military == 'yes' or row.branch is None, error_msg="branch must be null for non-military employees")
    Rule.constraint(validate=models.Employee, as_condition=lambda row: row.military == 'yes' or row.rank is None, error_msg="rank must be null for non-military employees")
    Rule.constraint(validate=models.Employee, as_condition=lambda row: row.military == 'yes' or row.service_years is None, error_msg="service_years must be null for non-military employees")
