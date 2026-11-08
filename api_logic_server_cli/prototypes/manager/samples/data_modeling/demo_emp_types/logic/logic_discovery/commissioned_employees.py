"""
Feature: Commissioned Employees

Commissioned employees are employees who can have Orders; only Commissioned employees may have Orders. Each Order has an amount and a customer name. Commissioned employees: commission_total = sum of Order.amount.
"""

from logic_bank.logic_bank import Rule
from database import models


def declare_logic():
    Rule.sum(derive=models.Employee.commission_total, as_sum_of=models.Order.amount)
    Rule.count(derive=models.Employee.order_count, as_count_of=models.Order)
    Rule.constraint(validate=models.Employee, as_condition=lambda row: row.type == 'commissioned' or row.order_count == 0,
                    error_msg="Only commissioned employees may have Orders")
    Rule.constraint(validate=models.Employee, as_condition=lambda row: row.type == 'commissioned' or row.base_salary is None,
                    error_msg="base_salary applies only to commissioned employees")
