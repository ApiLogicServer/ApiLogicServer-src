"""
Feature: Check Credit

  Scenario: Place an order
    Given a customer with a credit limit
    When an order is placed
    Then copy the price from the product
    And multiply by quantity to get the item amount
    And sum item amounts to get the order total
    And sum unpaid order totals to get the customer balance
    And reject if balance exceeds the credit limit
"""

from logic_bank.logic_bank import Rule
import database.models as models


def declare_logic():
    Rule.copy(derive=models.Item.unit_price, from_parent=models.Product.unit_price)

    Rule.formula(derive=models.Item.amount,
                 as_expression=lambda row: row.quantity * row.unit_price)

    Rule.sum(derive=models.Order.amount_total, as_sum_of=models.Item.amount)

    Rule.sum(derive=models.Customer.balance,
             as_sum_of=models.Order.amount_total,
             where=lambda row: row.date_shipped is None)

    Rule.constraint(
        validate=models.Customer,
        as_condition=lambda row: row.balance is None or row.credit_limit is None or row.balance <= row.credit_limit,
        error_msg="balance ({row.balance}) exceeds credit limit ({row.credit_limit})")
