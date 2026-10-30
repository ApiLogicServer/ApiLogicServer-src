#!/usr/bin/env python
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))  # ensure project root on path
import os, logging, logging.config
from config import server_setup
import api.system.api_utils as api_utils
from flask import Flask
import logging
import config.config as config

os.environ["PROJECT_DIR"] = os.environ.get("PROJECT_DIR", os.path.abspath(os.path.dirname(__file__)))

app_logger = server_setup.logging_setup()
app_logger.setLevel(logging.INFO)

current_path = os.path.abspath(os.path.dirname(__file__))
sys.path.extend([current_path, '.'])

flask_app = Flask("API Logic Server", template_folder='ui/templates')
flask_app.config.from_object(config.Config)
flask_app.config.from_prefixed_env(prefix="APILOGICPROJECT")

args = server_setup.get_args(flask_app)

server_setup.api_logic_server_setup(flask_app, args)

from database.models import *
import safrs
from datetime import date
import os
os.environ['AGGREGATE_DEFAULTS'] = 'True'

with flask_app.app_context():
    safrs.DB.create_all()
    session = safrs.DB.session

    # Accounts Settings: the credit controller role (Keycloak realm role 'manager')
    sys_config = session.query(SysConfig).first()
    sys_config.credit_controller = "manager"

    acme = Company(name="Acme Inc", credit_limit=5000)
    beta = Company(name="Beta Ltd", credit_limit=0)            # no default limit
    commercial = CustomerGroup(name="Commercial")
    retail = CustomerGroup(name="Retail")
    government = CustomerGroup(name="Government")
    session.add_all([acme, beta, commercial, retail, government])
    session.commit()

    session.add_all([
        CustomerGroupCreditLimit(customer_group_id=commercial.id, company_id=acme.id, credit_limit=3000, bypass_credit_limit_check=0),
        CustomerGroupCreditLimit(customer_group_id=government.id, company_id=acme.id, credit_limit=8000, bypass_credit_limit_check=1),
    ])
    alice = Customer(name="Alice Co", customer_group_id=commercial.id)      # own limit 1000 at Acme
    bob = Customer(name="Bob Ltd", customer_group_id=commercial.id)         # group limit 3000 at Acme
    carol = Customer(name="Carol Inc", customer_group_id=retail.id)         # company default 5000 at Acme
    dave = Customer(name="Dave Gov", customer_group_id=government.id)       # group row bypassed -> company default
    erin = Customer(name="Erin Trading", customer_group_id=retail.id)       # own row bypasses the check at Sales Order
    session.add_all([alice, bob, carol, dave, erin])
    session.commit()

    session.add_all([
        CustomerCreditLimit(customer_id=alice.id, company_id=acme.id, credit_limit=1000, bypass_credit_limit_check=0),
        CustomerCreditLimit(customer_id=erin.id, company_id=acme.id, credit_limit=2000, bypass_credit_limit_check=1),
    ])
    session.commit()

    # a few documents (entered with their totals, then submitted)
    so = SalesOrder(customer_id=alice.id, company_id=acme.id, grand_total=400, per_billed=0, status="To Deliver and Bill", docstatus=1)
    session.add(so)
    session.commit()
    inv = SalesInvoice(customer_id=bob.id, company_id=acme.id, grand_total=1200, docstatus=1)   # entered submitted
    inv.SalesInvoiceItemList.append(SalesInvoiceItem(qty=1))
    session.add(inv)
    session.commit()
    print("seed complete")
