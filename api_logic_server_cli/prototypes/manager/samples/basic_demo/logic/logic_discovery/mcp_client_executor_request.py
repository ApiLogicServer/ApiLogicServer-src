""" 
Invokes MCP client executor to process MCP requests when a new SysMcp row is inserted.
"""

import json
import os, logging
from typing import Dict, List
import openai
import requests
from logic_bank.logic_bank import Rule
from logic_bank.exec_row_logic.logic_row import LogicRow
from database import models
from database.mcp_models import SysMcp as SysMcp  # type: ignore
from sqlalchemy import Column, Integer, String, DECIMAL, Boolean
from logic_bank.util import ConstraintException
import integration.mcp.mcp_client_executor as mcp_client_executor


def declare_logic():
    """
        This illustrates the request pattern.

        The request pattern is a common pattern in API Logic Server, 
        where an insert triggers service invocation, such as sending email or issue mcp requests.
        
        The SysMCP table captures the prompt (in the row); this logic executes the MCP processing. 

        See: https://apilogicserver.github.io/Docs/Integration-MCP/#3a-logic-request-pattern     
    """


    def mcp_client_executor_event(row: SysMcp, old_row: SysMcp, logic_row: LogicRow):
        """ 

        #als: create an MCP request.  See https://apilogicserver.github.io/Docs/Integration-MCP/

        Test:
        * curl -X 'POST' 'http://localhost:5656/api/SysMcp/' -H 'accept: application/vnd.api+json' -H 'Content-Type: application/json' -d '{ "data": { "attributes": {"request": "List the orders date_shipped is null and CreatedOn before 2023-07-14, and send a discount email (subject: '\''Discount Offer'\'') to the customer for each one."}, "type": "SysMcp"}}'
        * Or, use the Admin App and insert a row into SysMCP, eg:
            * List the orders date_shipped is null and CreatedOn before 2023-07-14, and send a discount email (subject: 'Discount Offer') to the customer for each one."

        Args:
            row (Mcp): inserted SysMcp with prompt
            old_row (Mcp): n/a
            logic_row (LogicRow): bundles curr/old row, with ins/upd/dlt logic
        """
        result = mcp_client_executor.mcp_client_executor(row.request)
        pass

    Rule.row_event(on_class=SysMcp, calling=mcp_client_executor_event)  # see above
