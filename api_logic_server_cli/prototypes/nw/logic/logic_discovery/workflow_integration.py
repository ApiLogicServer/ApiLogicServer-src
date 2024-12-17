import datetime
from decimal import Decimal
from logic_bank.exec_row_logic.logic_row import LogicRow
from logic_bank.extensions.rule_extensions import RuleExtension
from logic_bank.logic_bank import Rule
from database import models
import api.system.opt_locking.opt_locking as opt_locking
from security.system.authorization import Grant
import logging
import requests
from flask import jsonify
import json
from integration.n8n.n8n_producer import send_n8n_message

""" Some examples below contrast a preferred approach with a more manual one """

app_logger = logging.getLogger(__name__)


def declare_logic():


    def call_n8n_workflow(row: models.Customer, old_row: models.Customer, logic_row: LogicRow):
        """
        Webhook Workflow:  When Customer is inserted/updated = post to external system
        """

        status = send_n8n_message(logic_row=logic_row)
        logic_row.debug(status)
        return
    
    Rule.after_flush_row_event(on_class=models.Customer, calling=call_n8n_workflow)