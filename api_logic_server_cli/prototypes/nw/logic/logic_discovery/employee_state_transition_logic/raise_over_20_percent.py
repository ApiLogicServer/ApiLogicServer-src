"""
Use case: Employee State Transition Logic

STATE TRANSITION LOGIC, using old_row: a raise must be a meaningful raise (>= 20%).
"""

from decimal import Decimal
from logic_bank.exec_row_logic.logic_row import LogicRow
from logic_bank.logic_bank import Rule
from database.models import *


def declare_logic():

    def raise_over_20_percent(row: Employee, old_row: Employee, logic_row: LogicRow):
        if logic_row.ins_upd_dlt == "upd" and row.Salary > old_row.Salary:
            return row.Salary >= Decimal('1.20') * old_row.Salary
        else:
            return True
    Rule.constraint(validate=Employee,
                    calling=raise_over_20_percent,
                    error_msg="{row.LastName} needs a more meaningful raise")
