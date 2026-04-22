"""
Check Credit - Business Logic Rules
====================================
Req §1: Copy price from product, compute item amount, sum order total,
        sum customer balance, enforce credit limit.
"""
from logic_bank.logic_bank import Rule
import database.models as models


def declare_logic():
    # Item unit_price copied from Product (stays current if product price changes)
    Rule.copy(derive=models.Item.unit_price, from_parent=models.Product.unit_price)

    # Item amount = quantity × unit_price
    Rule.formula(derive=models.Item.amount,
                 as_expression=lambda row: row.quantity * row.unit_price)

    # Order amount_total = sum of item amounts
    Rule.sum(derive=models.Order.amount_total, as_sum_of=models.Item.amount)

    # Customer balance = sum of unpaid order totals (date_shipped is null)
    Rule.sum(derive=models.Customer.balance,
             as_sum_of=models.Order.amount_total,
             where=lambda row: row.date_shipped is None)

    # Constraint: balance must not exceed credit limit
    Rule.constraint(
        validate=models.Customer,
        as_condition=lambda row: (
            row.balance is None
            or row.credit_limit is None
            or row.balance <= row.credit_limit
        ),
        error_msg="balance ({row.balance}) exceeds credit limit ({row.credit_limit})",
    )
