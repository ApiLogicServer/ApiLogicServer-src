import datetime
from decimal import Decimal
from logic_bank.exec_row_logic.logic_row import LogicRow
from logic_bank.extensions.rule_extensions import RuleExtension
from logic_bank.logic_bank import Rule
from logic_bank.util import ConstraintException
from database import models
import api.system.opt_locking.opt_locking as opt_locking
from security.system.authorization import Grant, Security
import logging
from flask import jsonify
from integration.row_dict_maps.OrderShipping import OrderShipping
from confluent_kafka import Producer, KafkaException
import integration.kafka.kafka_producer as kafka_producer
from config.config import Config

preferred_approach = True
""" Some examples below contrast a preferred approach with a more manual one """

app_logger = logging.getLogger(__name__)

declare_logic_message = "Sample Rules  Loaded"

def declare_logic():
    """ Declarative multi-table derivations and constraints, extensible with Python.
 
    Brief background: see readme_declare_logic.md
    
    Your Code Goes Here - Use code completion (Rule.) to declare rules
    """

    """         HOW TO USE RULES
                ================
    Declare, Activate and Run...

        *Declare* Logic here, using Python with code completion.

            This logic pre-created for default database, nw.sqlite.
                You would normally declare your *own* rules.
                For details on these rules, see
                    https://apilogicserver.github.io/Docs/Logic/
                    https://apilogicserver.github.io/Docs/Logic-Tutorial/

        *Activation* occurs automatically in api_logic_server_run.py:
            LogicBank.activate(session=session, activator=declare_logic, constraint_event=constraint_handler)

        Logic *runs* automatically, by listening to SQLAlchemy events (e.g. from API calls),
            for multi-table derivations and constraints,
            and events such as sending messages or mail.
        Logic consists of spreadsheet-like Rules and Python code
    """

    """         HOW RULES OPERATE
                =================
    Rules operate much like a spreadsheet:
        Watch, for changes in referenced values
        React, by recomputing value
        Chain, to any referencing rules, including other tables (multi-table logic)
            SQL is automated, and optimized (e.g., adjust vs. select sum)

    Unlike procedural code, rules are declarative:
        automatically re-used                        (improves quality)
        automatically ordered per their dependencies (simplifies maintenance)
        automatically optimized (pruned, with sql optimizations such as adjust logic)

    These 5 rules apply to all transactions (automatic re-use), eg.
        * place order
        * change Order Detail product, quantity
        * add/delete Order Detail
        * ship / unship order
        * delete order
        * move order to new customer, etc
    This reuse is how 5 rules replace 200 lines of legacy code: https://github.com/valhuber/LogicBank/wiki/by-code
    """

    """         FEATURE: Place Order
                ====================

    You can optionally use a BDD approach to document and run test suites
         See test/api_logic_server/behave/features/place_order.feature
         See https://apilogicserver.github.io/Docs/Behave/

    SCENARIO: Bad Order Custom Service
        When Order Placed with excessive quantity
        Then Rejected per CHECK CREDIT LIMIT

    LOGIC DESIGN: ("Cocktail Napkin Design")
    ========================================
        Customer.Balance <= CreditLimit
        Customer.Balance = Sum(Order.AmountTotal where unshipped)
        Order.AmountTotal = Sum(OrderDetail.Amount)
        OrderDetail.Amount = Quantity * UnitPrice
        OrderDetail.UnitPrice = copy from Product
    """

    from logic.logic_discovery.auto_discovery import discover_logic
    discover_logic()

    #als: basic rules - 5 rules vs 200 lines of code: https://github.com/valhuber/LogicBank/wiki/by-code
    Rule.constraint(validate=models.Customer,       # logic design translates directly into rules
        as_condition=lambda row: row.Balance <= row.CreditLimit,
        error_msg="balance ({round(row.Balance, 2)}) exceeds credit ({round(row.CreditLimit, 2)})")

    Rule.sum(derive=models.Customer.Balance,        # adjust iff AmountTotal or ShippedDate or CustomerID changes
        as_sum_of=models.Order.AmountTotal,
        where=lambda row: row.ShippedDate is None and row.Ready == True)  # adjusts - *not* a sql select sum...

    Rule.sum(derive=models.Order.AmountTotal,       # adjust iff Amount or OrderID changes
        as_sum_of=models.OrderDetail.Amount)

    Rule.formula(derive=models.OrderDetail.Amount,  # compute price * qty
        as_expression=lambda row: row.UnitPrice * row.Quantity)

    Rule.copy(derive=models.OrderDetail.UnitPrice,  # get Product Price (e,g., on insert, or ProductId change)
        from_parent=models.Product.UnitPrice)

    #als: Demonstrate that logic == Rules + Python (for extensibility)

    def send_order_to_shipping(row: models.Order, old_row: models.Order, logic_row: LogicRow):
        """ #als: Send Kafka message formatted by OrderShipping RowDictMapper

        Format row per shipping requirements, and send (e.g., a message)

        NB: the after_flush event makes Order.Id available.  Contrast to congratulate_sales_rep().

        Args:
            row (models.Order): inserted Order
            old_row (models.Order): n/a
            logic_row (LogicRow): bundles curr/old row, with ins/upd/dlt logic
        """
        if (logic_row.is_inserted() and row.Ready == True) or \
            (logic_row.is_updated() and row.Ready == True and old_row.Ready == False):
            kafka_producer.send_kafka_message(logic_row=logic_row,
                                              row_dict_mapper=OrderShipping,
                                              kafka_topic="order_shipping",
                                              kafka_key=str(row.Id),
                                              msg="Sending Order to Shipping")
            
    Rule.after_flush_row_event(on_class=models.Order, calling=send_order_to_shipping)  # see above


    def congratulate_sales_rep(row: models.Order, old_row: models.Order, logic_row: LogicRow):
        """ use events for sending email, messages, etc. """
        if logic_row.ins_upd_dlt == "ins":  # logic engine fills parents for insert
            sales_rep = row.Employee        # parent accessor
            if sales_rep is None:           # breakpoint here
                logic_row.log("no salesrep for this order")
            elif sales_rep.Manager is None:
                logic_row.log("no manager for this order's salesrep")
            else:
                logic_row.log(f'Hi, {sales_rep.Manager.FirstName} - '
                              f'Congratulate {sales_rep.FirstName} on their new order')
            category_1 = logic_row.session.query(models.Category).filter(models.Category.Id == 1).one()
            logic_row.log("Illustrate database access")  # not granted for user: u2
            # Note: *Client* access is subject to authorization
            #       *Logic* is system code, not subject to authorization

    Rule.commit_row_event(on_class=models.Order, calling=congratulate_sales_rep)


    """
        #als: Commit Events (which reflect sum/count values)
    """
    def do_not_ship_empty_orders(row: models.Order, old_row: models.Order, logic_row: LogicRow) -> bool:
        if row.OrderDetailCount == 0:  # an empty order... error if trying to ship...
            if logic_row.is_deleted():
                pass
            else:  # enforce child cardinality
                if row.ShippedDate is not None or row.Ready == True:
                    raise ConstraintException("Empty Order - Cannot Ship or Make Ready")
    
    Rule.commit_row_event(on_class=models.Order, calling=do_not_ship_empty_orders)


    def ship_ready_orders_only(row: models.Order, old_row: models.Order, logic_row: LogicRow) -> bool:
        invalid_row = row.Ready == False and row.ShippedDate is not None and old_row.ShippedDate is None
        return not invalid_row
    
    Rule.constraint(validate=models.Order,       # Do not ship orders that are not ready
        calling=ship_ready_orders_only,
        error_msg="Cannot Ship Order that is not Ready")

    """
        Simplify data entry with defaults 
    """

    def customer_defaults(row: models.Customer, old_row: models.Order, logic_row: LogicRow):
        if row.Balance is None:
            row.Balance = 0
        if row.CreditLimit is None:
            row.CreditLimit = 1000

    def order_defaults(row: models.Order, old_row: models.Order, logic_row: LogicRow):
        if row.Freight is None:
            row.Freight = 10
        if row.AmountTotal is None:
            row.AmountTotal = 0
        if row.Ready is None:  # if not set in UI, set to False for do_not_ship_empty_orders() 
            row.Ready = False

    def order_detail_defaults(row: models.OrderDetail, old_row: models.OrderDetail, logic_row: LogicRow):
        if row.Quantity is None:
            row.Quantity = 1
        if row.Discount is None:
            row.Discount = 0

    Rule.early_row_event(on_class=models.Customer, calling=customer_defaults)
    Rule.early_row_event(on_class=models.Order, calling=order_defaults)
    Rule.early_row_event(on_class=models.OrderDetail, calling=order_detail_defaults)


    """
        More complex rules follow - see: 
            https://github.com/valhuber/LogicBank/wiki/Examples
            https://github.com/valhuber/LogicBank/wiki/Rule-Extensibility
    """

    def units_in_stock(row: models.Product, old_row: models.Product, logic_row: LogicRow):
        result = row.UnitsInStock - (row.UnitsShipped - old_row.UnitsShipped)
        return result  # use lambdas for simple expressions, functions for complex logic (if/else etc)

    Rule.formula(derive=models.Product.UnitsInStock, calling=units_in_stock)  # compute reorder required

    Rule.sum(derive=models.Product.UnitsShipped,
        as_sum_of=models.OrderDetail.Quantity,
        where=lambda row: row.ShippedDate is None)

    Rule.formula(derive=models.OrderDetail.ShippedDate,  # unlike copy, referenced parent values cascade to children
        as_exp="row.Order.ShippedDate")


    Rule.count(derive=models.Customer.UnpaidOrderCount,
        as_count_of=models.Order,
        where=lambda row: row.ShippedDate is None)  # *not* a sql select sum...

    Rule.count(derive=models.Customer.OrderCount, as_count_of=models.Order)

    Rule.count(derive=models.Order.OrderDetailCount, as_count_of=models.OrderDetail)


    """
        #als: STATE TRANSITION LOGIC, using old_row
    """
    def raise_over_20_percent(row: models.Employee, old_row: models.Employee, logic_row: LogicRow):
        if logic_row.ins_upd_dlt == "upd" and row.Salary > old_row.Salary:
            return row.Salary >= Decimal('1.20') * old_row.Salary
        else:
            return True
    Rule.constraint(validate=models.Employee,
                    calling=raise_over_20_percent,
                    error_msg="{row.LastName} needs a more meaningful raise")


    """
        EXTEND RULE TYPES 
            Events, plus *generic* event handlers
    """
    
    RuleExtension.copy_row(copy_from=models.Employee,  # #als: AUDITING can be as simple as 1 rule
                    copy_to=models.EmployeeAudit,
                    copy_when=lambda logic_row: logic_row.ins_upd_dlt == "upd" and 
                            logic_row.are_attributes_changed([models.Employee.Salary, models.Employee.Title]))
    pass  # audited (never gets here)
    
    ''' the logic above is simpler than
        def audit_by_event(row: models.Employee, old_row: models.Employee, logic_row: LogicRow):
            if logic_row.ins_upd_dlt == "upd" and logic_row.are_attributes_changed([models.Employee.Salary, models.Employee.Title]):
                # #als: triggered inserts  
                copy_to_logic_row = logic_row.new_logic_row(models.EmployeeAudit)
                copy_to_logic_row.link(to_parent=logic_row)
                copy_to_logic_row.set_same_named_attributes(logic_row)
                # copy_to_logic_row.row.attribute_name = value
                copy_to_logic_row.insert(reason="Manual Copy " + copy_to_logic_row.name)  # triggers rules...

        Rule.commit_row_event(on_class=models.Employee, calling=audit_by_event)
    '''    

    def clone_order(row: models.Order, old_row: models.Order, logic_row: LogicRow):
        """ #als: clone multi-row business object

        Args:
            row (models.Order): _description_
            old_row (models.Order): _description_
            logic_row (LogicRow): _description_
        """
        if row.CloneFromOrder is not None and logic_row.nest_level == 0:
            which = ["OrderDetailList"]
            logic_row.copy_children(copy_from=row.Order,
                                    which_children=which)
    Rule.row_event(on_class=models.Order, calling=clone_order)


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


        did_stamping = False  # #als: TIME / DATE STAMPING
        if enable_stamping := True:
            row = logic_row.row
            if logic_row.ins_upd_dlt == "ins" and hasattr(row, "CreatedOn"):
                row.CreatedOn = datetime.datetime.now()
                did_stamping = True
            if logic_row.ins_upd_dlt == "ins" and hasattr(row, "CreatedBy"):
                row.CreatedBy = Security.current_user().id  \
                    if Config.SECURITY_ENABLED == True else 'public'
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
        
    Rule.formula(derive=models.Order.OrderDate, 
                 as_expression=lambda row: datetime.datetime.now())
    
    from api.system import api_utils
    # api_utils.rules_report()
    
    app_logger.debug("..logic/declare_logic.py (logic == rules + code)")
