import datetime, os
from decimal import Decimal
from logic_bank.exec_row_logic.logic_row import LogicRow
from logic_bank.extensions.rule_extensions import RuleExtension
from logic_bank.logic_bank import Rule
from logic_bank.logic_bank import DeclareRule
import database.models as models
import api.system.opt_locking.opt_locking as opt_locking
from integration.row_dict_maps.OrderShipping import OrderShipping
from security.system.authorization import Grant, Security
from logic.load_verify_rules import load_verify_rules
import integration.kafka.kafka_producer as kafka_producer
import logging

app_logger = logging.getLogger(__name__)

declare_logic_message = "ALERT:  *** No Rules Yet ***"  # printed in api_logic_server.py

def declare_logic():
    ''' Declarative multi-table derivations and constraints, extensible with Python.
 
    Brief background: see readme_declare_logic.md
    
    Your Code Goes Here - Use code completion (Rule.) to declare rules
    '''

    if os.environ.get("WG_PROJECT"):
        # Inside WG: Load rules from docs/expprt/export.json
        load_verify_rules()
    else:
        # Outside WG: load declare_logic function
        from logic.logic_discovery.auto_discovery import discover_logic
        discover_logic()

    # Logic from GenAI: (or, use your IDE w/ code completion)
    from database.models import Product, Order, Item, Customer

    # Ensure the customer's balance is less than their credit limit
    Rule.constraint(validate=Customer, as_condition=lambda row: row.balance <= row.credit_limit, error_msg="Customer balance ({row.balance}) exceeds credit limit ({row.credit_limit})")

    # Derive the customer's balance as the sum of order totals where not yet shipped.
    Rule.sum(derive=Customer.balance, as_sum_of=Order.amount_total, where=lambda row: row.date_shipped is None)

    # Derive the order's total amount from the sum of item amounts.
    Rule.sum(derive=Order.amount_total, as_sum_of=Item.amount)


    # ************   Python Customization Example ****************

    # Calculate item amount based on quantity and unit price.
    # Formerly, we had this rule:
    #       Rule.formula(derive=Item.amount, as_expression=lambda row: row.quantity * row.unit_price)
    # If the derivation were more complex, we could use a Python function, like this:
    def derive_amount(row: models.Item, old_row: models.Item, logic_row: LogicRow):
        amount = row.quantity * row.unit_price
        product = row.product
        if product.carbon_neutral == True and row.quantity >= 10:
           amount = amount * Decimal(0.9)  # breakpoint here
        return amount

    # 4. Items.Amount = Quantity * UnitPrice
    Rule.formula(derive=models.Item.amount, calling=derive_amount)

    # Copy unit price from product to item.
    Rule.copy(derive=Item.unit_price, from_parent=Product.unit_price)


    # ************   Python Customization Example ****************

    # Send order details to Kafka if order is shipped.
    # Formeraly, we had this rule:
    #       Rule.after_flush_row_event(on_class=Order, calling=kafka_producer.send_row_to_kafka, if_condition=lambda row: row.date_shipped is not None, with_args={'topic': 'order_shipping'})
    # If the integration were more complex, we could use Python, like this:
    #als: Demonstrate that logic == Rules + Python (for extensibility)

    def send_order_to_shipping(row: models.Order, old_row: models.Order, logic_row: LogicRow):
        """ #als: Send Kafka message formatted by OrderShipping RowDictMapper

        Format row per shipping requirements, and send (e.g., a message)

        NB: the after_flush event makes Order.Id avaible.

        Args:
            row (models.Order): inserted Order
            old_row (models.Order): n/a
            logic_row (LogicRow): bundles curr/old row, with ins/upd/dlt logic
        """
        if logic_row.is_inserted():
            kafka_producer.send_kafka_message(logic_row=logic_row,
                                              row_dict_mapper=OrderShipping,
                                              kafka_topic="order_shipping",
                                              kafka_key=str(row.id),
                                              msg="Sending Order to Shipping")
            
    Rule.after_flush_row_event(on_class=models.Order, calling=send_order_to_shipping)  # see above

    # End Logic from GenAI


    def handle_all(logic_row: LogicRow):  # #als: TIME / DATE STAMPING, OPTIMISTIC LOCKING
        """
        This is generic - executed for all classes.

        Invokes optimistic locking, and checks Grant permissions.

        Also provides user/date stamping.

        Args:
            logic_row (LogicRow): from LogicBank - old/new row, state
        """

        if os.getenv("APILOGICPROJECT_NO_FLASK") is not None:
            print("\ndeclare_logic.py Using TestBase\n")
            return  # enables rules to be used outside of Flask, e.g., test data loading

        if logic_row.is_updated() and logic_row.old_row is not None and logic_row.nest_level == 0:
            opt_locking.opt_lock_patch(logic_row=logic_row)

        Grant.process_updates(logic_row=logic_row)

        did_stamping = False
        if enable_stamping := True:  # #als:  DATE / USER STAMPING
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

