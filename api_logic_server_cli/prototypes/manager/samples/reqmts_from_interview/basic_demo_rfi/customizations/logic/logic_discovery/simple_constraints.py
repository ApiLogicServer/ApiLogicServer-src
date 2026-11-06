import datetime
from decimal import Decimal
from logic_bank.exec_row_logic.logic_row import LogicRow
from logic_bank.extensions.rule_extensions import RuleExtension
from logic_bank.logic_bank import Rule
from database import models
import api.system.opt_locking.opt_locking as opt_locking
from security.system.authorization import Grant
import logging
from flask import jsonify

app_logger = logging.getLogger(__name__)

def declare_logic():
    """
        Simple constraints for error testing, e.g.:
        
        * Set a breakpoint on `as_condition`
        * Observe the row values in the debugger
    """

    Rule.constraint(validate=models.Customer,
        as_condition=lambda row: row.name != 'x',
        error_msg="Customer name cannot be 'x'")

