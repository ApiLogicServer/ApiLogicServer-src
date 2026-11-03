"""
Best practice: create logic files for each use case,
named for the use case (e.g., check_credit.py).
"""
from logic_bank.logic_bank import Rule
from database import models
import logging

app_logger = logging.getLogger(__name__)


def declare_logic():
    """
    Use code completion (Rule.) to declare rules, or
    use GenAI to convert natural language into logic.

    Sample logic:
    Rule.constraint(validate=models.Customer,
        as_condition=lambda row: row.CompanyName != 'x',
        error_msg="CompanyName cannot be 'x'")
    """
    pass
