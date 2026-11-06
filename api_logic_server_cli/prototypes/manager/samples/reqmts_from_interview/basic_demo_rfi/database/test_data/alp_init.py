#!/usr/bin/env python
"""Seed data for basic_demo_rfi - runs with Flask context and LogicBank active, so every derived column
(unit_price, green, discount_amount, amount, amount_total, balance) is computed by the rules.

Run from the project root:   PROJECT_DIR=$(pwd) python database/test_data/alp_init.py
"""
import os, logging, logging.config, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))  # ensure project root on path

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
from decimal import Decimal
import os
os.environ['AGGREGATE_DEFAULTS'] = 'True'

with flask_app.app_context():
    safrs.DB.create_all()
    session = safrs.DB.session

    if session.query(Customer).count() > 0:
        print("Seed data already present - nothing to do")
        sys.exit(0)

    # commit lookup/parent rows first: formulas read the FK columns of children
    alice = Customer(name="Alice", credit_limit=Decimal("1000"))
    bob = Customer(name="Bob", credit_limit=Decimal("500"))
    widget = Product(name="Widget", unit_price=Decimal("25.00"), green="no")
    gadget = Product(name="Gadget", unit_price=Decimal("40.00"), green="no")
    bamboo_cup = Product(name="Bamboo Cup", unit_price=Decimal("10.00"), green="yes")
    recycled_notebook = Product(name="Recycled Notebook", unit_price=Decimal("8.00"), green="yes")
    session.add_all([alice, bob, widget, gadget, bamboo_cup, recycled_notebook])
    session.commit()

    order_1 = Order(customer_id=alice.id, notes="Rush order", CreatedOn=date(2026, 11, 1))
    order_2 = Order(customer_id=alice.id, notes="Standing order", CreatedOn=date(2026, 11, 2))
    order_3 = Order(customer_id=bob.id, notes="First order", CreatedOn=date(2026, 11, 3))
    session.add_all([order_1, order_2, order_3])
    session.commit()

    session.add_all([
        Item(order_id=order_1.id, product_id=widget.id, quantity=2),             # 50.00, not green
        Item(order_id=order_1.id, product_id=bamboo_cup.id, quantity=5),         # 50.00 less 10% green discount = 45.00
        Item(order_id=order_2.id, product_id=gadget.id, quantity=3),             # 120.00
        Item(order_id=order_3.id, product_id=recycled_notebook.id, quantity=10), # 80.00 less 8.00 = 72.00
    ])
    session.commit()

    session.expunge_all()  # reload fresh so the optimistic-locking checksum matches the committed row
    order_2 = session.query(Order).filter(Order.notes == "Standing order").one()
    order_2.date_shipped = date(2026, 11, 4)  # ships: leaves Alice's balance, publishes to order_shipping
    session.commit()

    for customer in session.query(Customer).all():
        print(f"{customer.name}: balance={customer.balance} credit_limit={customer.credit_limit}")
    for order in session.query(Order).all():
        print(f"Order {order.id}: amount_total={order.amount_total} date_shipped={order.date_shipped}")
