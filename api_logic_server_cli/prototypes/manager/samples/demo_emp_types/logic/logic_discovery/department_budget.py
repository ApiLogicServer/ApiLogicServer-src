"""
Departments have a name and a budget.
Department.total_salary = sum of Employee.salary (all types).
Department.total_salary must not exceed Department.budget.
"""

from logic_bank.logic_bank import Rule
from database import models


def declare_logic():

    Rule.sum(derive=models.Department.total_salary, as_sum_of=models.Employee.salary)

    Rule.constraint(validate=models.Department,
                    as_condition=lambda row: row.total_salary <= row.budget,
                    error_msg="Department total_salary ({row.total_salary}) exceeds budget ({row.budget})")
