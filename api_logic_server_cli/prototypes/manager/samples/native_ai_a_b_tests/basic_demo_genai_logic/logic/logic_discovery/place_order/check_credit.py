"""
For each line item on the order, look up the product's price and multiply by the
quantity to get the item's amount.
Add up the item amounts to get the order's total.
Add the order total to the customer's balance.
Before we let the order go through, check that the customer's balance doesn't go
over their credit limit -- if it would, reject the order.

version: 1.0
created: 2026-09-21T00:00:00
created_by: claude-sonnet-5 (valjhuber@gmail.com)
"""

from logic_bank.logic_bank import Rule
from database import models


def declare_logic():
    """Business logic rules for Check Credit use case."""

    Rule.copy(derive=models.Item.unit_price, from_parent=models.Product.unit_price)
    Rule.formula(derive=models.Item.amount, 
                 as_expression=lambda row: row.quantity * row.unit_price)
    Rule.sum(derive=models.Order.amount_total, as_sum_of=models.Item.amount)
    Rule.sum(derive=models.Customer.balance, as_sum_of=models.Order.amount_total)
    Rule.constraint(validate=models.Customer,
                    as_condition=lambda row: row.balance <= row.credit_limit,
                    error_msg="Customer balance ({row.balance}) exceeds credit limit ({row.credit_limit})")
