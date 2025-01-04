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
import logging, os
from flask import jsonify
from integration.row_dict_maps.OrderShipping import OrderShipping
from confluent_kafka import Producer, KafkaException
import integration.kafka.kafka_producer as kafka_producer

app_logger = logging.getLogger(__name__)

declare_logic_message = "Sample Rules  Iteration Loaded"

def declare_logic():

    """ Declarative multi-table derivations and constraints, extensible with Python. 

    Brief background: see readme_declare_logic.md

    Use code completion (Rule.) to declare rules here

    Check Credit - Logic Design (note: translates directly into rules)

    1. Customer.Balance <= CreditLimit
    2. Customer.Balance = Sum(Order.AmountTotal where unshipped)
    3. Order.AmountTotal = Sum(Items.Amount)
    4. Items.Amount = Quantity * UnitPrice
    5. Items.UnitPrice = copy from Product
    """

    Rule.constraint(validate=models.Customer,       # 5 rules vs. 200 lines of Python - https://apilogicserver.github.io/Docs/Logic-Why/
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
    
    #als: Demonstrate that logic == Rules + Python (for extensibility)

    def send_order_to_shipping(row: models.Order, old_row: models.Order, logic_row: LogicRow):
        """ #als: Send Kafka message formatted by OrderShipping RowDictMapper

        Format row per shipping requirements, and send (e.g., a message)

        NB: the after_flush event makes Order.Id avaible.  Contrast to congratulate_sales_rep().

        Args:
            row (models.Order): inserted Order
            old_row (models.Order): n/a
            logic_row (LogicRow): bundles curr/old row, with ins/upd/dlt logic
        """
        if logic_row.is_inserted():
            kafka_producer.send_kafka_message(logic_row=logic_row,
                                              row_dict_mapper=OrderShipping,
                                              kafka_topic="order_shipping",
                                              kafka_key=str(row.OrderID),
                                              msg="Sending Order to Shipping")
            
    Rule.after_flush_row_event(on_class=models.Order, calling=send_order_to_shipping)  # see above


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
        enable_creation_stamping = False  # CreatedOn time stamping
        if enable_creation_stamping:
            row = logic_row.row
            if logic_row.ins_upd_dlt == "ins" and hasattr(row, "CreatedOn"):
                row.CreatedOn = datetime.datetime.now()
                logic_row.log("early_row_event_all_classes - handle_all sets 'Created_on"'')
            Grant.process_updates(logic_row=logic_row)

    Rule.early_row_event_all_classes(early_row_event_all_classes=handle_all)


    app_logger.debug("..logic/declare_logic.py (logic == rules + code)")

