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

app_logger = logging.getLogger(__name__)

def declare_logic():
    """
        This illustrates the request pattern.

        The request pattern is a common pattern in API Logic Server, 
        where an insert into SysEmail triggers service invocation, such as sending email.

        See https://apilogicserver.github.io/Docs/Integration-MCP/.
        
        The SysEmail table includes the columns for the email (e,g, recipient, subject, message).
        
        Using a request object enables you to wrap the service call with logic, eg:
        
        * *email requirement: do not send mail if customer has opted out*  

        See: https://apilogicserver.github.io/Docs/Integration-MCP/#3a-logic-request-pattern     
    """

    def send_mail(row: models.SysEmail, old_row: models.SysEmail, logic_row: LogicRow):
        """ 

        #als: Send N8N email message

        Args:
            row (Email): inserted Email
            old_row (Email): n/a
            logic_row (LogicRow): bundles curr/old row, with ins/upd/dlt logic
        """
        if logic_row.is_inserted(): 
            customer = row.customer  # parent accessor
            if customer.email_opt_out:
                logic_row.log("customer opted out of email")
                return
            logic_row.log(f"send email {row.message} to {customer.email} (stub, eg use N8N")  # see in log  

    Rule.after_flush_row_event(on_class=models.SysEmail, calling=send_mail)  # see above
