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

version: 1.0
created: 2026-10-29T17:48:00
created_by: claude-opus-5-5 (valjhuber@gmail.com)
"""

from decimal import Decimal
from logic_bank.logic_bank import Rule
from logic_bank.exec_row_logic.logic_row import LogicRow
from database import models

EMPLOYEE_TYPES = ('salaried', 'hourly', 'commissioned')


def declare_logic():
    """Business logic rules for Employee Pay use case (employment-type axis)."""
    # TODO: Review parent-value rules below.
    #   Rule.copy  = snapshot (value frozen at transaction time, no cascade on parent change) <- default
    #   Rule.formula referencing a parent attribute = live (re-derives if parent changes)
    #   union_dues reads union.dues_rate LIVE (prompt states it as a formula): a dues_rate change re-derives dues.

    def _employee_salary(row: models.Employee, old_row: models.Employee, logic_row: LogicRow):
        """Derive salary: hourly = hours_worked * hourly_rate; commissioned = base_salary + commission_total; salaried = entered value."""
        emp_type = row.type
        if emp_type == 'hourly':
            hours = row.hours_worked or 0
            rate = row.hourly_rate or 0
            return Decimal(str(hours)) * Decimal(str(rate))
        if emp_type == 'commissioned':
            base = row.base_salary or Decimal(0)
            commission = row.commission_total or Decimal(0)
            return base + commission
        return row.salary or Decimal(0)   # salaried: entered directly

    def _union_dues(row: models.Employee, old_row: models.Employee, logic_row: LogicRow):
        """Derive union_dues: hours_worked * union.dues_rate for hourly employees with a union, else 0."""
        emp_type = row.type
        union_id = row.union_id
        if emp_type != 'hourly' or union_id is None:
            return Decimal(0)
        hours = row.hours_worked or 0
        dues_rate = row.union.dues_rate or 0
        return Decimal(str(hours)) * Decimal(str(dues_rate))

    def _hourly_salary_within_weekly_cap(row: models.Employee, old_row: models.Employee, logic_row: LogicRow):
        """Employee constraint: an hourly employee's (weekly) salary must not exceed SysConfig.max_hourly_weekly_salary."""
        emp_type = row.type
        salary = row.salary or Decimal(0)
        if emp_type != 'hourly':
            return True
        cap = models.SysConfig.current(logic_row.session).max_hourly_weekly_salary
        return salary <= Decimal(str(cap))

    Rule.formula(derive=models.Employee.salary, calling=_employee_salary)
    Rule.formula(derive=models.Employee.union_dues, calling=_union_dues)
    Rule.sum(derive=models.Employee.commission_total, as_sum_of=models.Order.amount)
    Rule.count(derive=models.Employee.order_count, as_count_of=models.Order)

    Rule.constraint(validate=models.Employee, as_condition=lambda row: row.type in EMPLOYEE_TYPES, error_msg="Employee type ({row.type}) must be one of: salaried, hourly, commissioned")
    Rule.constraint(validate=models.Employee, calling=_hourly_salary_within_weekly_cap, error_msg="Hourly employee salary ({row.salary}) exceeds the weekly maximum (SysConfig.max_hourly_weekly_salary)")
    Rule.constraint(validate=models.Employee, as_condition=lambda row: row.type == 'hourly' or row.union_id is None, error_msg="Only hourly employees may have a union_id")
    Rule.constraint(validate=models.Employee, as_condition=lambda row: row.type == 'commissioned' or row.order_count == 0, error_msg="Only commissioned employees may have Orders (order_count is {row.order_count})")
    Rule.constraint(validate=models.Employee, as_condition=lambda row: row.type == 'hourly' or row.hours_worked is None, error_msg="hours_worked must be null for non-hourly employees")
    Rule.constraint(validate=models.Employee, as_condition=lambda row: row.type == 'hourly' or row.hourly_rate is None, error_msg="hourly_rate must be null for non-hourly employees")
    Rule.constraint(validate=models.Employee, as_condition=lambda row: row.type == 'commissioned' or row.base_salary is None, error_msg="base_salary must be null for non-commissioned employees")
