import datetime
from decimal import Decimal
from logic_bank.exec_row_logic.logic_row import LogicRow
from logic_bank.extensions.rule_extensions import RuleExtension
from logic_bank.logic_bank import Rule
import database.models as models
from database.models import *
import api.system.opt_locking.opt_locking as opt_locking
from security.system.authorization import Grant, Security
import logging

logger = logging.getLogger(__name__)

def declare_logic():
    ''' Declarative multi-table derivations and constraints, extensible with Python.
 
    Brief background: see readme_declare_logic.md
    
    Your Code Goes Here - Use code completion (Rule.) to declare rules
    '''
    
    # Logic from GenAI December 17, 2024 19:36:19:


    # Ensures customer names cannot be 'x'.
    Rule.constraint(validate=Customer,
                as_condition=lambda row: row.name != 'x',
                error_msg="Customer names cannot be 'x'.")

    # Ensures product names cannot be 'xx'.
    Rule.constraint(validate=Product,
                as_condition=lambda row: row.name != 'xx',
                error_msg="Product names cannot be 'xx'.")

    # Ensures products with names containing 'green' are carbon neutral.
    Rule.constraint(validate=Product,
                as_condition=lambda row: 'green' not in row.name.lower() or row.carbon_neutral is True,
                error_msg="Products containing 'green' in their name must be carbon neutral.")

    # End Logic from GenAI

