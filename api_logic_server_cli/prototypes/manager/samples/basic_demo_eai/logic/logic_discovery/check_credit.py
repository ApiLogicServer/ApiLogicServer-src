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

version: 1.0
created: 2026-10-24
created_by: claude-sonnet-5-5 (valjhuber@gmail.com)
"""

from logic_bank.logic_bank import Rule
from database import models


def declare_logic():
    """Business logic rules for Check Credit use case."""

    Rule.constraint(validate=models.Customer, as_condition=lambda row: row.balance is None or row.credit_limit is None or row.balance <= row.credit_limit, error_msg="balance ({row.balance}) exceeds credit limit ({row.credit_limit})")
    Rule.sum(derive=models.Customer.balance, as_sum_of=models.Order.amount_total, where=lambda row: row.date_shipped is None)
    Rule.sum(derive=models.Order.amount_total, as_sum_of=models.Item.amount)
    Rule.formula(derive=models.Item.amount, as_expression=lambda row: row.quantity * row.unit_price)
    Rule.copy(derive=models.Item.unit_price, from_parent=models.Product.unit_price)
