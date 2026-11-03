#!/usr/bin/env python
import os, logging, logging.config, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
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

    alice = Customer(name="Alice", credit_limit=1000, balance=0)
    session.add(alice)

    widget = Product(name="Widget", unit_price=25.0)
    gadget = Product(name="Gadget", unit_price=50.0)
    session.add_all([widget, gadget])

    jane = SalesRep(name="Jane")
    bob = SalesRep(name="Bob")
    session.add_all([jane, bob])

    session.commit()
    print(f"seeded: customer={alice.id}, products={widget.id},{gadget.id}, sales_reps={jane.id},{bob.id}")
