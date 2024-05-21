import datetime
from decimal import Decimal
from logic_bank.exec_row_logic.logic_row import LogicRow
from logic_bank.extensions.rule_extensions import RuleExtension
from logic_bank.logic_bank import Rule
from database import models
import api.system.opt_locking.opt_locking as opt_locking
from security.system.authorization import Grant
import logging
from flask import jsonify


""" Some examples below contrast a preferred approach with a more manual one """

app_logger = logging.getLogger(__name__)


def declare_logic():
    """
        Simple constraints for error testing 
    """
    Rule.constraint(validate=models.Customer,
        as_condition=lambda row: row.CompanyName != 'x',
        error_msg="CustomerName cannot be 'x'")

    Rule.constraint(validate=models.Employee,
        as_condition=lambda row: row.LastName != 'x',
        error_msg="LastName cannot be 'x'")
    
    def valid_category_description(row: models.Category, old_row: models.Category, logic_row: LogicRow):
        if logic_row.ins_upd_dlt == "upd":
            return row.Description != 'x'
        else:
            return True
    Rule.constraint(validate=models.Category,
                    calling=valid_category_description,
                    error_msg="Description cannot be 'x'")

