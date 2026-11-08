"""
Feature: Department Budget

Departments have a name and a budget. Department.total_salary = sum of Employee.salary (all types). Department.total_salary must not exceed Department.budget. A user with the manager role may exceed the budget; other users may not.
"""

from logic_bank.logic_bank import Rule
from database import models


def _current_user_is_manager() -> bool:
    """Security helper: True only if a signed-in user holds the manager role; no user means False."""
    try:
        from security.system.authorization import Security   # import here: logic loads before security
        return Security.current_user_has_role('manager')
    except Exception:
        return False


def _total_salary_within_budget(row, old_row, logic_row):
    """Department constraint: total_salary must not exceed budget, unless the user has the manager role."""
    total = row.total_salary
    budget = row.budget
    if total <= budget:
        return True
    if _current_user_is_manager():
        logic_row.log(f"over budget ({total} > {budget}) - allowed for manager role")
        return True
    return False


def declare_logic():
    Rule.sum(derive=models.Department.total_salary, as_sum_of=models.Employee.salary)
    Rule.constraint(validate=models.Department, calling=_total_salary_within_budget,
                    error_msg="Department total_salary ({row.total_salary}) exceeds budget ({row.budget})")
