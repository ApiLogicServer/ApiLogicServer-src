import datetime
from logic_bank.exec_row_logic.logic_row import LogicRow
from logic_bank.logic_bank import Rule
from database.models import *
import api.system.opt_locking.opt_locking as opt_locking
from security.system.authorization import Grant, Security
import logging
from config.config import Config

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

    # Use case files, one per business use case (see logic/logic_discovery/):
    #   order_place/check_credit.py                       - the 5-rule check-credit chain, order/customer defaults, ship-ready state
    #   order_place/app_integration.py                    - Kafka/N8N notifications on Order events
    #   employee_state_transition_logic/raise_over_20_percent.py - state-transition constraint
    #   employee_auditing/employee_audit.py               - RuleExtension.copy_row audit
    #   order_ship_inventory_reorder/units_in_stock.py     - reorder-point formula/sum
    #   order_clone/clone_order.py                        - clone multi-row business object
    #   simple_constraints.py                             - error-testing constraints (pre-existing)
    #   integration.py                                    - Kafka/N8N examples (pre-existing)
    from logic.logic_discovery.auto_discovery import discover_logic
    discover_logic()

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

    from api.system import api_utils
    # api_utils.rules_report()

    app_logger.debug("..logic/declare_logic.py (logic == rules + code)")
