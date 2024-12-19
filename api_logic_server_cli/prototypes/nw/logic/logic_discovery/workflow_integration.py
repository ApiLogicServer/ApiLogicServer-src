import datetime
from decimal import Decimal
from logic_bank.exec_row_logic.logic_row import LogicRow
from logic_bank.extensions.rule_extensions import RuleExtension
from logic_bank.logic_bank import Rule
from database import models
import api.system.opt_locking.opt_locking as opt_locking
from security.system.authorization import Grant
import logging
from integration.n8n.n8n_producer import send_n8n_message


""" 
    Examples for integrating n8n Webhooks using after_flush_row_event. 
    Note: update config/config.py with n8n webhook URL and authorization token.
"""

app_logger = logging.getLogger(__name__)


def declare_logic():

    def fn_customer_workflow(row: models.Customer, old_row: models.Customer, logic_row: LogicRow):
        """
        Webhook Workflow:  When Customer is inserted/updated - post n8n Webhook and call sendgrid email system
        """
        if logic_row.is_inserted():
            send_n8n_message(logic_row=logic_row)

    def fn_employee_workflow(row: models.Employee, old_row: models.Employee, logic_row: LogicRow):
        """
        Workflow:  When Employee is inserted = post n8n Webhook and call sendgrid email system
        """
        send_n8n_message(logic_row=logic_row,
                msg="1. /Webhook integration.py: n8n, sending Employee logic_row")        

    def fn_order_workflow(row: models.Order, old_row: models.Order, logic_row: LogicRow):
        """
        Workflow:  When Order is inserted = post n8n Webhook and call sendgrid email system
        """
        if logic_row.is_updated() and row.Ready == True and old_row.Ready == False:
            send_n8n_message(payload={
                                    "Order Id": row.Id, 
                                    "Customer Name": row.Customer.CompanyName, 
                                    "Order Total": str(row.AmountTotal),
                                    "Order Date": row.OrderDate,
                                    #"items": [row.OrderDetailList]
                                },
                ins_upd_dlt="upd", wh_entity="Order",
                msg="1. /Webhook integration.py: n8n, sending ready Order payload")        

    Rule.after_flush_row_event(on_class=models.Order, calling=fn_order_workflow)
    Rule.after_flush_row_event(on_class=models.Customer, calling=fn_customer_workflow)
    Rule.after_flush_row_event(on_class=models.Employee, calling=fn_employee_workflow)
