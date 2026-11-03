import datetime
from logic_bank.exec_row_logic.logic_row import LogicRow
from logic_bank.logic_bank import Rule
import api.system.opt_locking.opt_locking as opt_locking
from security.system.authorization import Grant, Security
from config.config import Config
import os
import logging

app_logger = logging.getLogger(__name__)


def declare_logic():
    """Cross-cutting rules applied to every class (optimistic locking, RBAC, stamping)."""

    def handle_all(logic_row: LogicRow):  # #als: DATE / USER STAMPING, OPTIMISTIC LOCKING
        """
        Generic handler - executed for every row update across all classes.

        Provides three cross-cutting services:
        1. Optimistic locking (built-in, always active)
        2. Grant/RBAC permission enforcement (built-in, always active)
        3. Date/User stamping (opt-in: set enable_stamping = True below)

        Date/User Stamping - auto-populates audit fields on insert/update:
          CreatedOn, CreatedBy  → set on insert
          UpdatedOn, UpdatedBy  → set on update
          Any subset works — hasattr() checks before setting each field.
          To activate: change `enable_stamping := False` to `enable_stamping := True`

        Args:
            logic_row (LogicRow): from LogicBank - old/new row, state
        """

        if os.getenv("APILOGICPROJECT_NO_FLASK") is not None:
            print("\nall_classes_stamping.py Using TestBase\n")
            return  # enables rules to be used outside of Flask, e.g., test data loading

        if logic_row.is_updated() and logic_row.old_row is not None and logic_row.nest_level == 0:
            opt_locking.opt_lock_patch(logic_row=logic_row)

        Grant.process_updates(logic_row=logic_row)

        did_stamping = False
        if enable_stamping := False:  # #als: change False to True to enable date/user stamping
            row = logic_row.row
            if logic_row.ins_upd_dlt == "ins" and hasattr(row, "CreatedOn"):
                row.CreatedOn = datetime.datetime.now()
                did_stamping = True
            if logic_row.ins_upd_dlt == "ins" and hasattr(row, "CreatedBy"):
                row.CreatedBy = Security.current_user().id \
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
