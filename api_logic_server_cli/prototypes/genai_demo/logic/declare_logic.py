import datetime
from decimal import Decimal
from logic_bank.exec_row_logic.logic_row import LogicRow
from logic_bank.extensions.rule_extensions import RuleExtension
from logic_bank.logic_bank import Rule
from database import models
from database.models import Customer, Order, Item, Product
import api.system.opt_locking.opt_locking as opt_locking
from security.system.authorization import Grant
import logging

app_logger = logging.getLogger(__name__)

declare_logic_message = "ALERT:  *** No Rules Yet ***"  # printed in api_logic_server.py

def declare_logic():
    ''' Declarative multi-table derivations and constraints, extensible with Python.
 
    Brief background: see readme_declare_logic.md
    
    Your Code Goes Here - Use code completion (Rule.) to declare rules

    GenAI: Paste the following into Copilot Chat, and paste the result below.
        
    Use Logic Bank to enforce these requirements:
    
    Enforce the Check Credit requirement (do not generate check constraints):
    1. Customer.Balance <= CreditLimit
    2. Customer.Balance = Sum(Order.AmountTotal where date shipped is null)
    3. Order.AmountTotal = Sum(Items.Amount)
    4. Items.Amount = Quantity * UnitPrice
    5. Store the Items.UnitPrice as a copy from Product.UnitPrice
    '''

    from logic_bank.logic_bank import Rule

    # 1. Customer.Balance <= CreditLimit
    Rule.constraint(validate=Customer,
                    error_msg="balance exceeds credit limit",
                    as_condition=lambda row: row.Balance <= row.CreditLimit)

    # 2. Customer.Balance = Sum(Order.AmountTotal where date shipped is null)
    Rule.sum(derive=Customer.Balance, as_sum_of=Order.AmountTotal,
            where=lambda row: row.ShipDate is None)

    # 3. Order.AmountTotal = Sum(Items.Amount)
    Rule.sum(derive=Order.AmountTotal, as_sum_of=Item.Amount)

    # 4. Items.Amount = Quantity * UnitPrice
    Rule.formula(derive=Item.Amount, as_expression=lambda row: row.Quantity * row.UnitPrice)

    # 5. Store the Items.UnitPrice as a copy from Product.UnitPrice
    Rule.copy(Item.UnitPrice, from_parent=Product.UnitPrice)


    def handle_all(logic_row: LogicRow):  # OPTIMISTIC LOCKING, [TIME / DATE STAMPING]
        """
        This is generic - executed for all classes.

        Invokes optimistic locking.

        You can optionally do time and date stamping here, as shown below.

        Args:
            logic_row (LogicRow): from LogicBank - old/new row, state
        """
        if logic_row.is_updated() and logic_row.old_row is not None and logic_row.nest_level == 0:
            opt_locking.opt_lock_patch(logic_row=logic_row)
        enable_creation_stamping = False  # CreatedOn time stamping
        if enable_creation_stamping:
            row = logic_row.row
            if logic_row.ins_upd_dlt == "ins" and hasattr(row, "CreatedOn"):
                row.CreatedOn = datetime.datetime.now()
                logic_row.log("early_row_event_all_classes - handle_all sets 'Created_on"'')
            Grant.process_updates(logic_row=logic_row)

    Rule.early_row_event_all_classes(early_row_event_all_classes=handle_all)

    #als rules report
    from api.system import api_utils
    # api_utils.rules_report()

    app_logger.debug("..logic/declare_logic.py (logic == rules + code)")

