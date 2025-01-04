import datetime
from decimal import Decimal
from logic_bank.exec_row_logic.logic_row import LogicRow
from logic_bank.extensions.rule_extensions import RuleExtension
from logic_bank.logic_bank import Rule
import api.system.opt_locking.opt_locking as opt_locking
from security.system.authorization import Grant
from database import models
import logging, os

from logic_bank.extensions.allocate import Allocate

declare_logic_message = "Sample Rules  Loaded"

def unpaid_orders(provider: LogicRow):
    """ returns Payments' Customers' Orders, where AmountOwed > 0, by OrderDate """
    customer_of_payment = provider.row.Customer
    unpaid_orders_result = provider.session.query(models.Order)\
        .filter(models.Order.AmountOwed > 0, models.Order.CustomerId == customer_of_payment.Id)\
        .order_by(models.Order.OrderDate).all()
    return unpaid_orders_result


def declare_logic():

    Rule.sum(derive=models.Customer.Balance, as_sum_of=models.Order.AmountOwed)

    Rule.formula(derive=models.Order.AmountOwed, as_expression=lambda row: row.AmountTotal - row.AmountPaid)
    
    Rule.sum(derive=models.Order.AmountPaid, as_sum_of=models.PaymentAllocation.AmountAllocated)

    Rule.formula(derive=models.PaymentAllocation.AmountAllocated, as_expression=lambda row:
        min(Decimal(row.Payment.AmountUnAllocated), Decimal(row.Order.AmountOwed)))

    Allocate(provider=models.Payment,  # uses default (overrideable) while_calling_allocator
            recipients=unpaid_orders,
            creating_allocation=models.PaymentAllocation)
    

    ####
    # Standard Rules Follow
    ###

    def handle_all(logic_row: LogicRow):  # OPTIMISTIC LOCKING, [TIME / DATE STAMPING]
        """
        This is generic - executed for all classes.

        Invokes optimistic locking.

        You can optionally do time and date stamping here, as shown below.

        Args:
            logic_row (LogicRow): from LogicBank - old/new row, state
        """

        if not os.getenv("APILOGICPROJECT_NO_FLASK") is not None:
            return  # enables rules to be used outside of Flask, e.g., test data loading

        if logic_row.is_updated() and logic_row.old_row is not None and logic_row.nest_level == 0:
            opt_locking.opt_lock_patch(logic_row=logic_row)
        enable_creation_stamping = True  # CreatedOn time stamping
        if enable_creation_stamping:
            row = logic_row.row
            if logic_row.ins_upd_dlt == "ins" and hasattr(row, "CreatedOn"):
                row.CreatedOn = datetime.datetime.now()
                logic_row.log("early_row_event_all_classes - handle_all sets 'Created_on"'')
            Grant.process_updates(logic_row=logic_row)

    Rule.early_row_event_all_classes(early_row_event_all_classes=handle_all)
