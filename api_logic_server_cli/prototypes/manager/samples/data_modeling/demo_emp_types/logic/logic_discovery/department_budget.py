"""
Departments have a name and a budget.
Department.total_salary = sum of Employee.salary (all types).
Department.total_salary must not exceed Department.budget.
A user with the manager role may exceed the budget; other users may not.

version: 1.0
created: 2026-10-29T17:48:00
created_by: claude-opus-5-5 (valjhuber@gmail.com)
"""

from logic_bank.logic_bank import Rule
from logic_bank.exec_row_logic.logic_row import LogicRow
from database import models


def _current_user_is_manager() -> bool:
    """True only if a request user exists and holds the manager role; no user -> False."""
    try:
        from security.system.authorization import Security   # import here: logic loads before security
        return Security.current_user_has_role('manager')
    except Exception:
        return False   # no request / no signed-in user (seed script, SECURITY_ENABLED=False): rule enforced


def declare_logic():
    """Business logic rules for Department Budget use case."""

    def _total_salary_within_budget(row: models.Department, old_row: models.Department, logic_row: LogicRow):
        """Department constraint: total_salary must not exceed budget, unless the committing user holds the manager role."""
        total_salary = row.total_salary or 0
        budget = row.budget or 0
        if total_salary <= budget:
            return True
        if _current_user_is_manager():
            logic_row.log(f"over budget ({total_salary} > {budget}) - allowed for manager role")
            return True
        return False

    Rule.sum(derive=models.Department.total_salary, as_sum_of=models.Employee.salary)
    Rule.constraint(validate=models.Department, calling=_total_salary_within_budget, error_msg="Department total_salary ({row.total_salary}) exceeds budget ({row.budget}) - only the manager role may exceed the budget")
