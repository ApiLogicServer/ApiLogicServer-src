"""
On Placing Orders, Check Credit
    1. The Customer's balance is less than the credit limit
    2. The Customer's balance is the sum of the Order amount_total where date_shipped is null
    3. The Order's amount_total is the sum of the Item amount
    4. The Item amount is the quantity * unit_price
    5. The Item unit_price is copied from the Product unit_price
"""

from logic_bank.logic_bank import Rule
from database import models


def declare_logic():
    Rule.constraint(validate=models.Customer,
                     as_condition=lambda row: row.balance <= row.credit_limit,
                     error_msg="balance ({row.balance}) exceeds credit limit ({row.credit_limit})")

    Rule.sum(derive=models.Customer.balance, as_sum_of=models.Order.amount_total,
             where=lambda row: row.date_shipped is None)

    Rule.sum(derive=models.Order.amount_total, as_sum_of=models.Item.amount)

    Rule.formula(derive=models.Item.amount, as_expression=lambda row: row.quantity * row.unit_price)

    Rule.copy(derive=models.Item.unit_price, from_parent=models.Product.unit_price)

# See logic/procedural/credit_service.py for the equivalent procedural implementation —
# 5 declarative rules here vs ~200 lines there, with 0 bugs vs 2.
