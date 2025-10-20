import datetime
from decimal import Decimal
from logic_bank.exec_row_logic.logic_row import LogicRow
from logic_bank.extensions.rule_extensions import RuleExtension
from logic_bank.logic_bank import Rule
from database import models
import logging

app_logger = logging.getLogger(__name__)


def declare_logic():
    """
    Check Credit Use Case Logic
    
    Natural Language Requirements:
    1. The Customer's balance is less than the credit limit
    2. The Customer's balance is the sum of the Order amount_total where date_shipped is null
    3. The Order's amount_total is the sum of the Item amount
    4. The Item amount is the quantity * unit_price
    5. The Item unit_price is copied from the Product unit_price
    """
    
    # 1. The Customer's balance is less than the credit limit
    Rule.constraint(validate=models.Customer,
                   as_condition=lambda row: row.balance <= row.credit_limit,
                   error_msg="Customer balance exceeds credit limit")
    
    # 2. The Customer's balance is the sum of the Order amount_total where date_shipped is null
    Rule.sum(derive=models.Customer.balance, 
             as_sum_of=models.Order.amount_total,
             where=lambda row: row.date_shipped is None)
    
    # 3. The Order's amount_total is the sum of the Item amount
    Rule.sum(derive=models.Order.amount_total, 
             as_sum_of=models.Item.amount)
    
    # 4. The Item amount is the quantity * unit_price
    Rule.formula(derive=models.Item.amount, 
                 as_expression=lambda row: row.quantity * row.unit_price)
    
    # 5. The Item unit_price is copied from the Product unit_price
    Rule.copy(derive=models.Item.unit_price, 
              from_parent=models.Product.unit_price)
