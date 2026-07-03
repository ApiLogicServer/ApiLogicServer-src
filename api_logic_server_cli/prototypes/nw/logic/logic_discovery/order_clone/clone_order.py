"""
Use case: Order Clone

Clone a multi-row business object (Order + its Items) by setting CloneFromOrder.
"""

from logic_bank.exec_row_logic.logic_row import LogicRow
from logic_bank.logic_bank import Rule
from database.models import *


def declare_logic():

    def clone_order(row: Order, old_row: Order, logic_row: LogicRow):
        """ #als: clone multi-row business object

        Args:
            row (Order): _description_
            old_row (Order): _description_
            logic_row (LogicRow): _description_
        """
        if row.CloneFromOrder is not None and logic_row.nest_level == 0:
            which = ["OrderDetailList"]
            logic_row.copy_children(copy_from=row.Order,
                                    which_children=which)
    Rule.row_event(on_class=Order, calling=clone_order)
