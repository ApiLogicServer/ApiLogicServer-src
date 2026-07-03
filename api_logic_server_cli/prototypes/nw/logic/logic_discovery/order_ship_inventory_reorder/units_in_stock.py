"""
Use case: Order Ship Inventory Reorder

More complex rules - see:
    https://github.com/valhuber/LogicBank/wiki/Examples
    https://github.com/valhuber/LogicBank/wiki/Rule-Extensibility

Product.UnitsInStock is reduced as OrderDetail.UnitsShipped increases (reorder point logic).
"""

from logic_bank.exec_row_logic.logic_row import LogicRow
from logic_bank.logic_bank import Rule
from database.models import *


def declare_logic():

    def units_in_stock(row: Product, old_row: Product, logic_row: LogicRow):
        result = row.UnitsInStock - (row.UnitsShipped - old_row.UnitsShipped)
        return result  # use lambdas for simple expressions, functions for complex logic (if/else etc)

    Rule.formula(derive=Product.UnitsInStock, calling=units_in_stock)  # compute reorder required

    Rule.sum(derive=Product.UnitsShipped,
        as_sum_of=OrderDetail.Quantity,
        where=lambda row: row.ShippedDate is None)

    Rule.formula(derive=OrderDetail.ShippedDate,  # unlike copy, referenced parent values cascade to children
        as_exp="row.Order.ShippedDate")
