"""
FEATURE: Place Order
=====================

SCENARIO: Bad Order Custom Service
    When Order Placed with excessive quantity
    Then Rejected per CHECK CREDIT LIMIT

LOGIC DESIGN: ("Cocktail Napkin Design")
========================================
    Customer.Balance <= CreditLimit
    Customer.Balance = Sum(Order.AmountTotal where unshipped and ready)
    Order.AmountTotal = Sum(OrderDetail.Amount)
    OrderDetail.Amount = Quantity * UnitPrice
    OrderDetail.UnitPrice = copy from Product
"""

import datetime
from decimal import Decimal
from logic_bank.exec_row_logic.logic_row import LogicRow
from logic_bank.logic_bank import Rule
from logic_bank.util import ConstraintException
from database.models import *


def declare_logic():

    #als: basic rules - 5 rules vs 200 lines of code: https://github.com/valhuber/LogicBank/wiki/by-code
    Rule.constraint(validate=Customer,       # logic design translates directly into rules
        as_condition=lambda row: row.Balance <= row.CreditLimit,
        error_msg="balance ({round(row.Balance, 2)}) exceeds credit ({round(row.CreditLimit, 2)})")

    Rule.sum(derive=Customer.Balance,        # adjust iff AmountTotal or ShippedDate or CustomerID changes
        as_sum_of=Order.AmountTotal,
        where=lambda row: row.ShippedDate is None and row.Ready == True)  # adjusts - *not* a sql select sum...

    Rule.sum(derive=Order.AmountTotal,       # adjust iff Amount or OrderID changes
        as_sum_of=OrderDetail.Amount)

    Rule.formula(derive=OrderDetail.Amount,  # compute price * qty
        as_expression=lambda row: row.UnitPrice * row.Quantity)

    Rule.copy(derive=OrderDetail.UnitPrice,  # get Product Price (e,g., on insert, or ProductId change)
        from_parent=Product.UnitPrice)

    Rule.count(derive=Customer.UnpaidOrderCount,
        as_count_of=Order,
        where=lambda row: row.ShippedDate is None)  # *not* a sql select sum...

    Rule.count(derive=Customer.OrderCount, as_count_of=Order)

    Rule.count(derive=Order.OrderDetailCount, as_count_of=OrderDetail)

    Rule.formula(derive=Order.OrderDate,
                 as_expression=lambda row: datetime.datetime.now())

    """
        Simplify data entry with defaults
    """

    def customer_defaults(row: Customer, old_row: Order, logic_row: LogicRow):
        if row.Balance is None:
            row.Balance = 0
        if row.CreditLimit is None:
            row.CreditLimit = 1000

    def order_defaults(row: Order, old_row: Order, logic_row: LogicRow):
        if row.Freight is None:
            row.Freight = 10
        if row.AmountTotal is None:
            row.AmountTotal = 0
        if row.Ready is None:  # if not set in UI, set to False for do_not_ship_empty_orders()
            row.Ready = False

    def order_detail_defaults(row: OrderDetail, old_row: OrderDetail, logic_row: LogicRow):
        if row.Quantity is None:
            row.Quantity = 1
        if row.Discount is None:
            row.Discount = 0

    Rule.early_row_event(on_class=Customer, calling=customer_defaults)
    Rule.early_row_event(on_class=Order, calling=order_defaults)
    Rule.early_row_event(on_class=OrderDetail, calling=order_detail_defaults)

    """
        #als: STATE TRANSITION LOGIC, using old_row
    """
    def ship_ready_orders_only(row: Order, old_row: Order, logic_row: LogicRow) -> bool:
        invalid_row = logic_row.is_updated() and row.Ready == False and row.ShippedDate is not None and old_row.ShippedDate is None
        return not invalid_row

    Rule.constraint(validate=Order,       # Do not ship orders that are not ready
        calling=ship_ready_orders_only,
        error_msg="Cannot Ship Order that is not Ready")

    """
        #als: Commit Events (which reflect sum/count values)
    """
    def do_not_ship_empty_orders(row: Order, old_row: Order, logic_row: LogicRow) -> bool:
        if row.OrderDetailCount == 0:  # an empty order... error if trying to ship...
            if logic_row.is_deleted():
                pass
            else:  # enforce child cardinality
                if row.ShippedDate is not None or row.Ready == True:
                    raise ConstraintException("Empty Order - Cannot Ship or Make Ready")

    Rule.commit_row_event(on_class=Order, calling=do_not_ship_empty_orders)
