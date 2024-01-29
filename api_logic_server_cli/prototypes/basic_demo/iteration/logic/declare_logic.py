#############################################
# copy this file over logic/declare_logic.py
#############################################

import datetime
from decimal import Decimal
from logic_bank.exec_row_logic.logic_row import LogicRow
from logic_bank.extensions.rule_extensions import RuleExtension
from logic_bank.logic_bank import Rule
from database import models
import api.system.opt_locking.opt_locking as opt_locking
from security.system.authorization import Grant
import logging

app_logger = logging.getLogger(__name__)

def declare_logic():

    """ Declarative multi-table derivations and constraints, extensible with Python. 

    Brief background: see readme_declare_logic.md

    Use code completion (Rule.) to declare rules here

    Check Credit - Logic Design:

    1. Customer.Balance <= CreditLimit

    2. Customer.Balance = Sum(Order.AmountTotal where unshipped)

    3. Order.AmountTotal = Sum(Items.Amount)

    4. Items.Amount = Quantity * UnitPrice

    5. Items.UnitPrice = copy from Product
    """

    Rule.constraint(validate=models.Customer,       # logic design translates directly into rules
        as_condition=lambda row: row.Balance <= row.CreditLimit,
        error_msg="balance ({round(row.Balance, 2)}) exceeds credit ({round(row.CreditLimit, 2)})")

    Rule.sum(derive=models.Customer.Balance,        # adjust iff AmountTotal or ShippedDate or CustomerID changes
        as_sum_of=models.Order.AmountTotal,
        where=lambda row: row.ShipDate is None)     # adjusts - *not* a sql select sum...

    Rule.sum(derive=models.Order.AmountTotal,       # adjust iff Amount or OrderID changes
        as_sum_of=models.Item.Amount)

    def derive_amount(row: models.Item, old_row: models.Item, logic_row: LogicRow):
        amount = row.Quantity * row.UnitPrice
        if row.Product.CarbonNeutral == True and row.Quantity >= 10:
           amount = amount * Decimal(0.9)  # breakpoint here
        return amount

    Rule.formula(derive=models.Item.Amount, calling=derive_amount)
    
    Rule.copy(derive=models.Item.UnitPrice,    # get Product Price (e,g., on insert, or ProductId change)
        from_parent=models.Product.UnitPrice)


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


    app_logger.debug("..logic/declare_logic.py (logic == rules + code)")

