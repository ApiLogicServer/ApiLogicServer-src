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


""" Best practice: create logic files for each use case """

app_logger = logging.getLogger(__name__)


def declare_logic():
    """
    Use GenAI to convert Natural Language into logic, paste here.  See readme_logic_discovery_readme.md for an example.
    
    Sample logic:
    Rule.constraint(validate=models.Customer,
        as_condition=lambda row: row.CompanyName != 'x',
        error_msg="CompanyName cannot be 'x'")
    """
    pass