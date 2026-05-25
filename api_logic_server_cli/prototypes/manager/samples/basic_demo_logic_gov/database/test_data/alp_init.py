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

    # Products
    product_1 = Product(name="Chai", unit_price=18.00)
    product_2 = Product(name="Chang", unit_price=19.00)
    product_3 = Product(name="Aniseed Syrup", unit_price=10.00)
    safrs.DB.session.add_all([product_1, product_2, product_3])
    safrs.DB.session.commit()

    # Customers
    customer_1 = Customer(name="Alice", email="alice@example.com", credit_limit=2000.0)
    customer_2 = Customer(name="Bob", email="bob@example.com", credit_limit=500.0)
    safrs.DB.session.add_all([customer_1, customer_2])
    safrs.DB.session.commit()

    # Orders for Alice (unpaid - date_shipped is None)
    order_1 = Order(customer_id=customer_1.id, date_ordered="2026-05-01", notes="Rush order")
    safrs.DB.session.add(order_1)
    safrs.DB.session.commit()

    item_1 = Item(order_id=order_1.id, product_id=product_1.id, quantity=5)
    item_2 = Item(order_id=order_1.id, product_id=product_2.id, quantity=3)
    safrs.DB.session.add_all([item_1, item_2])
    safrs.DB.session.commit()

    # Orders for Bob (one shipped, one unpaid)
    order_2 = Order(customer_id=customer_2.id, date_ordered="2026-05-10", date_shipped="2026-05-15")
    order_3 = Order(customer_id=customer_2.id, date_ordered="2026-05-20", notes="Pending")
    safrs.DB.session.add_all([order_2, order_3])
    safrs.DB.session.commit()

    item_3 = Item(order_id=order_2.id, product_id=product_3.id, quantity=10)
    item_4 = Item(order_id=order_3.id, product_id=product_1.id, quantity=2)
    safrs.DB.session.add_all([item_3, item_4])
    safrs.DB.session.commit()

