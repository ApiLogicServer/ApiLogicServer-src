import datetime
from decimal import Decimal
from logic_bank.exec_row_logic.logic_row import LogicRow
from logic_bank.extensions.rule_extensions import RuleExtension
from logic_bank.logic_bank import Rule
from logic_bank.logic_bank import DeclareRule
import database.models as models
from database.models import *
import api.system.opt_locking.opt_locking as opt_locking
from security.system.authorization import Grant, Security
import logging

app_logger = logging.getLogger(__name__)

declare_logic_message = "ALERT:  *** No Rules Yet ***"  # printed in api_logic_server.py

def declare_logic():
    ''' Declarative multi-table derivations and constraints, extensible with Python.
 
    Brief background: see readme_declare_logic.md
    
    Your Code Goes Here - Use code completion (Rule.) to declare rules
    '''

    from logic.logic_discovery.auto_discovery import discover_logic
    discover_logic()

    # Logic from GenAI: (or, use your IDE w/ code completion)

    # Customer's balance is the sum of order totals where orders are not shipped.
    Rule.sum(derive=Customer.balance, as_sum_of=Order.amount_total, where=lambda row: row.date_shipped is None)

    # Order's amount total is the sum of its items' amounts.
    Rule.sum(derive=Order.amount_total, as_sum_of=OrderItem.amount)

    # Each item's amount is the product of its quantity and unit price.
    Rule.formula(derive=OrderItem.amount, as_expression=lambda row: row.quantity * row.unit_price)

    # Copy unit price from the product to the order item.
    Rule.copy(derive=OrderItem.unit_price, from_parent=Product.price)

    # Ensure customer's balance does not exceed their credit limit.
    Rule.constraint(validate=Customer, as_condition=lambda row: row.balance <= row.credit_limit, error_msg="balance ({row.balance}) exceeds credit limit ({row.credit_limit})")

    # End Logic from GenAI


    def handle_all(logic_row: LogicRow):  # #als: TIME / DATE STAMPING, OPTIMISTIC LOCKING
        """
        This is generic - executed for all classes.

        Invokes optimistic locking, and checks Grant permissions.

        Also provides user/date stamping.

        Args:
            logic_row (LogicRow): from LogicBank - old/new row, state
        """
        if logic_row.is_updated() and logic_row.old_row is not None and logic_row.nest_level == 0:
            opt_locking.opt_lock_patch(logic_row=logic_row)

        Grant.process_updates(logic_row=logic_row)

        did_stamping = False
        if enable_stamping := False:  # #als:  DATE / USER STAMPING
            row = logic_row.row
            if logic_row.ins_upd_dlt == "ins" and hasattr(row, "CreatedOn"):
                row.CreatedOn = datetime.datetime.now()
                did_stamping = True
            if logic_row.ins_upd_dlt == "ins" and hasattr(row, "CreatedBy"):
                row.CreatedBy = Security.current_user().id
                #    if Config.SECURITY_ENABLED == True else 'public'
                did_stamping = True
            if logic_row.ins_upd_dlt == "upd" and hasattr(row, "UpdatedOn"):
                row.UpdatedOn = datetime.datetime.now()
                did_stamping = True
            if logic_row.ins_upd_dlt == "upd" and hasattr(row, "UpdatedBy"):
                row.UpdatedBy = Security.current_user().id  \
                    if Config.SECURITY_ENABLED == True else 'public'
                did_stamping = True
            if did_stamping:
                logic_row.log("early_row_event_all_classes - handle_all did stamping")     
    Rule.early_row_event_all_classes(early_row_event_all_classes=handle_all)

    #als rules report
    from api.system import api_utils
    # api_utils.rules_report()

    app_logger.debug("..logic/declare_logic.py (logic == rules + code)")

