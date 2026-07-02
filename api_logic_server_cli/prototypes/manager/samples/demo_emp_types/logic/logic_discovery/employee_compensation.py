"""
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
"""

from decimal import Decimal
from logic_bank.logic_bank import Rule
from database import models


def _employee_salary(row, old_row, logic_row):
    """Derive salary: type-branched — hourly=hours*rate, commissioned=base+commission, salaried=entered."""
    if row.type == 'hourly':
        return Decimal(str(row.hours_worked or 0)) * Decimal(str(row.hourly_rate or 0))
    elif row.type == 'commissioned':
        return (row.base_salary or Decimal(0)) + (row.commission_total or Decimal(0))
    return row.salary  # salaried: entered directly


def _union_dues(row, old_row, logic_row):
    """Derive union_dues: hours_worked * union.dues_rate for hourly employees in a union, else 0."""
    if row.type != 'hourly' or row.union_id is None:
        return Decimal(0)
    return Decimal(str(row.hours_worked or 0)) * Decimal(str(row.union.dues_rate or 0))


def declare_logic():

    # SysConfig threshold copied down to Employee (see docs/training/logic_bank_api.md SysConfig pattern)
    Rule.copy(derive=models.Employee.max_hourly_weekly_salary, from_parent=models.SysConfig.max_hourly_weekly_salary)

    Rule.formula(derive=models.Employee.salary, calling=_employee_salary)

    Rule.constraint(validate=models.Employee,
                    as_condition=lambda row: row.type != 'hourly' or row.salary is None or row.salary <= row.max_hourly_weekly_salary,
                    error_msg="Hourly salary ({row.salary}) exceeds weekly cap ({row.max_hourly_weekly_salary})")

    # Union assignment is hourly-only
    Rule.constraint(validate=models.Employee,
                    as_condition=lambda row: row.type == 'hourly' or row.union_id is None,
                    error_msg="union_id must be null for non-hourly employees")

    Rule.formula(derive=models.Employee.union_dues, calling=_union_dues)

    # Orders belong only to commissioned employees
    Rule.sum(derive=models.Employee.commission_total, as_sum_of=models.CommissionOrder.amount)

    Rule.constraint(validate=models.CommissionOrder,
                    as_condition=lambda row: row.employee.type == 'commissioned',
                    error_msg="Orders can only be assigned to commissioned employees")

    Rule.constraint(validate=models.CommissionOrder,
                    as_condition=lambda row: row.amount > 0,
                    error_msg="Order amount ({row.amount}) must be greater than 0")

    # Inferred STI null-exclusion constraints (subtype-specific columns must be null for other types)
    Rule.constraint(validate=models.Employee,
                    as_condition=lambda row: row.type == 'hourly' or row.hours_worked is None,
                    error_msg="hours_worked must be null for non-hourly employees")

    Rule.constraint(validate=models.Employee,
                    as_condition=lambda row: row.type == 'hourly' or row.hourly_rate is None,
                    error_msg="hourly_rate must be null for non-hourly employees")

    Rule.constraint(validate=models.Employee,
                    as_condition=lambda row: row.type == 'commissioned' or row.base_salary is None,
                    error_msg="base_salary must be null for non-commissioned employees")
