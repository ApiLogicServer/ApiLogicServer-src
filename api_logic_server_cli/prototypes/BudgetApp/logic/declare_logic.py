import datetime
from decimal import Decimal
from logic_bank.exec_row_logic.logic_row import LogicRow
from logic_bank.extensions.rule_extensions import RuleExtension
from logic_bank.logic_bank import Rule
from database import models
import api.system.opt_locking.opt_locking as opt_locking
import logging, os
from security.system.authorization import Grant

app_logger = logging.getLogger(__name__)

declare_logic_message = "Sample Rules  Loaded"

def declare_logic():
    ''' Declarative multi-table derivations and constraints, extensible with Python. 

    Brief background: see readme_declare_logic.md
    
    Use code completion (Rule.) to declare rules here:
    '''

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

    use_parent_insert = True

    # Roll up budget amounts
    
    Rule.sum(derive=models.YrTotal.budget_total, as_sum_of=models.CategoryTotal.budget_total,insert_parent=use_parent_insert)
    Rule.sum(derive=models.CategoryTotal.budget_total, as_sum_of=models.Budget.amount,insert_parent=use_parent_insert)
    Rule.sum(derive=models.CategoryTotal.actual_amount, as_sum_of=models.Budget.actual_amount,insert_parent=use_parent_insert)
    Rule.sum(derive=models.MonthTotal.budget_total, as_sum_of=models.Budget.amount,insert_parent=use_parent_insert)
    Rule.sum(derive=models.Budget.actual_amount, as_sum_of=models.Transaction.amount,insert_parent=use_parent_insert)
    
    Rule.copy(derive=models.Budget.is_expense,from_parent=models.Category.is_expense)
    Rule.copy(derive=models.CategoryTotal.is_expense,from_parent=models.Category.is_expense)
    Rule.count(derive=models.Budget.count_transactions,as_count_of=models.Transaction)
    
    # Calculate variance from budget to actual
    Rule.formula(derive=models.Budget.variance_amount, as_expression=lambda row: row.actual_amount - row.amount)
    Rule.formula(derive=models.CategoryTotal.variance_amount, as_expression=lambda row: row.actual_amount - row.budget_total)
    Rule.formula(derive=models.MonthTotal.variance_amount, as_expression=lambda row: row.actual_amount - row.budget_total)
    Rule.formula(derive=models.YrTotal.variance_amount, as_expression=lambda row: row.actual_amount - row.budget_total)
    
    # Roll up actual transaction amounts into Budget
    
    Rule.sum(derive=models.YrTotal.actual_amount, as_sum_of=models.CategoryTotal.actual_amount,insert_parent=use_parent_insert)
    Rule.sum(derive=models.MonthTotal.actual_amount, as_sum_of=models.Budget.actual_amount,insert_parent=use_parent_insert)
    
    # Copy Budget (parent) values 
    
    Rule.copy(derive=models.Transaction.category_id,from_parent=models.Budget.category_id)
    Rule.copy(derive=models.Transaction.user_id,from_parent=models.Budget.user_id)
    Rule.copy(derive=models.Transaction.year_id,from_parent=models.Budget.year_id)
    Rule.copy(derive=models.Transaction.month_id,from_parent=models.Budget.month_id)
    Rule.copy(derive=models.Transaction.is_expense,from_parent=models.Category.is_expense)
    
    app_logger.debug("..logic/declare_logic.py (logic == rules + code)")


