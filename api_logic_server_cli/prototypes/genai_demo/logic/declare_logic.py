import datetime
from decimal import Decimal
from logic_bank.exec_row_logic.logic_row import LogicRow
from logic_bank.extensions.rule_extensions import RuleExtension
from logic_bank.logic_bank import Rule
from database.models import *
from database.models import Customer, Order, Item, Product
import api.system.opt_locking.opt_locking as opt_locking
from security.system.authorization import Grant
import logging, os
from integration.row_dict_maps.OrderShipping import OrderShipping
from confluent_kafka import Producer, KafkaException
import integration.kafka.kafka_producer as kafka_producer

app_logger = logging.getLogger(__name__)

declare_logic_message = "ALERT:  *** No Rules Yet ***"  # printed in api_logic_server.py

def declare_logic():
    ''' Declarative multi-table derivations and constraints, extensible with Python.
 
    Brief background: see readme_declare_logic.md

    GenAI: the following prompt was sent to GenAI-Logic, which translated it into the code below:
        
    Use case: Check Credit 
    
    1. The Customer's balance is less than the credit limit
    2. The Customer's balance is the sum of the Order amount_total where date_shipped is null
    3. The Order's amount_total is the sum of the Item amount
    4. The Item amount is the quantity * unit_price
    5. The Item unit_price is copied from the Product unit_price
    '''

    from logic_bank.logic_bank import Rule

    from logic.logic_discovery.auto_discovery import discover_logic
    discover_logic()

    # Logic from GenAI: (or, use your IDE w/ code completion)

    # Ensures the customer's balance is less than the credit limit.
    Rule.constraint(validate=Customer,
                    as_condition=lambda row: row.Balance <= row.CreditLimit,
                    error_msg="Customer balance ({row.Balance}) exceeds credit limit ({row.CreditLimit})")

    # Computes the customer's balance as the sum of unshipped orders.
    Rule.sum(derive=Customer.Balance, as_sum_of=Order.AmountTotal, where=lambda row: row.ShipDate is None)

    # Computes the total amount of an order as the sum of item amounts.
    Rule.sum(derive=Order.AmountTotal, as_sum_of=Item.Amount)

    # Calculates the item amount as the quantity times unit price.  (original rule, prior to iteration)
    # Rule.formula(derive=Item.amount, as_expression=lambda row: row.quantity * row.unit_price)

    # Copies the unit price from the parent product to the item.
    Rule.copy(derive=Item.UnitPrice, from_parent=Product.UnitPrice)

    # End Logic from GenAI


    #als: Demonstrate that logic == Rules + Python (for extensibility)

    # 4. Items.Amount = Quantity * UnitPrice, altered with IDE for CarbonNeutral discount
    def derive_amount(row: Item, old_row: Item, logic_row: LogicRow):
        amount = row.Quantity * row.UnitPrice
        if row.Product.CarbonNeutral == True and row.Quantity >= 10:
           amount = amount * Decimal(0.9)  # breakpoint here
        return amount
    # now register function; note logic ordering is automatic
    Rule.formula(derive=Item.Amount, calling=derive_amount)  

    def send_order_to_shipping(row: Order, old_row: Order, logic_row: LogicRow):
        """ #als: Send Kafka message formatted by OrderShipping RowDictMapper

        Format row per shipping requirements, and send (e.g., a message)

        NB: the after_flush event makes Order.Id avaible.

        Args:
            row (Order): inserted Order
            old_row (Order): n/a
            logic_row (LogicRow): bundles curr/old row, with ins/upd/dlt (etc) state
        """
        if logic_row.is_inserted():
            kafka_producer.send_kafka_message(logic_row=logic_row,
                                              row_dict_mapper=OrderShipping,
                                              kafka_topic="order_shipping",
                                              kafka_key=str(row.OrderID),
                                              msg="Sending Order to Shipping")
            
    Rule.after_flush_row_event(on_class=Order, calling=send_order_to_shipping)  # see above



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

    #als rules report
    from api.system import api_utils
    # api_utils.rules_report()

    app_logger.debug("..logic/declare_logic.py (logic == rules + code)")

