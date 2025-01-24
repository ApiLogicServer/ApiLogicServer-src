import datetime
from decimal import Decimal
from logic_bank.exec_row_logic.logic_row import LogicRow
from logic_bank.extensions.rule_extensions import RuleExtension
from logic_bank.logic_bank import Rule
import database.models as models
import api.system.opt_locking.opt_locking as opt_locking
from security.system.authorization import Grant, Security
import logging

logger = logging.getLogger(__name__)

def declare_logic():
    ''' Declarative multi-table derivations and constraints, extensible with Python.
 
    Brief background: see readme_declare_logic.md
    
    Your Code Goes Here - Use code completion (Rule.) to declare rules
    '''

    # this logic is automatically discovered by declare_logic.py#discover_logic()
    