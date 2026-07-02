"""
Employees may also have a military classification, independent of employment type.
Military employees have a branch (TEXT: 'Army', 'Navy', 'Air Force', 'Marines', 'Coast Guard'),
a rank (TEXT), and service_years (INTEGER).
Military employees receive a military_stipend (REAL) = service_years * 100.
Total compensation for military employees = salary + military_stipend.
Total compensation for non-military employees = salary.
"""

from decimal import Decimal
from logic_bank.logic_bank import Rule
from database import models

_VALID_BRANCHES = ('Army', 'Navy', 'Air Force', 'Marines', 'Coast Guard')


def _military_stipend(row, old_row, logic_row):
    """Derive military_stipend: service_years * rate for military employees, 0 otherwise."""
    if row.military != "yes":   # explicit comparison avoids the LB dependency-scanner colon gotcha
        return Decimal(0)
    return Decimal(str(row.service_years or 0)) * Decimal(str(row.military_stipend_rate_per_year or 0))


def declare_logic():

    # SysConfig rate copied down to Employee (see docs/training/logic_bank_api.md SysConfig pattern)
    Rule.copy(derive=models.Employee.military_stipend_rate_per_year, from_parent=models.SysConfig.military_stipend_rate_per_year)

    Rule.formula(derive=models.Employee.military_stipend, calling=_military_stipend)

    # military_stipend is always 0 for non-military rows, so this single formula covers both spec cases
    Rule.formula(derive=models.Employee.total_compensation,
                as_expression=lambda row: (row.salary or Decimal(0)) + Decimal(str(row.military_stipend or 0)))

    # Inferred null-exclusion constraints (military-specific columns must be null for non-military employees)
    Rule.constraint(validate=models.Employee,
                    as_condition=lambda row: row.military == "yes" or row.branch is None,
                    error_msg="branch must be null for non-military employees")

    Rule.constraint(validate=models.Employee,
                    as_condition=lambda row: row.military == "yes" or row.rank is None,
                    error_msg="rank must be null for non-military employees")

    Rule.constraint(validate=models.Employee,
                    as_condition=lambda row: row.military == "yes" or row.service_years is None,
                    error_msg="service_years must be null for non-military employees")

    # Domain-standard validation (spec = floor, not ceiling): branch must be a recognized service branch
    Rule.constraint(validate=models.Employee,
                    as_condition=lambda row: row.branch is None or row.branch in _VALID_BRANCHES,
                    error_msg="branch ({row.branch}) is not a recognized military branch")
