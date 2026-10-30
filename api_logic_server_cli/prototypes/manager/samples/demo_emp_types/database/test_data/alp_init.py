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
    from decimal import Decimal

    # 1. lookup / parent rows first, committed, so children reference real ids
    engineering = Department(name="Engineering", budget=Decimal("20000"))
    sales = Department(name="Sales", budget=Decimal("15000"))
    local_42 = LaborUnion(name="Local 42", dues_rate=1.5)
    teamsters = LaborUnion(name="Teamsters", dues_rate=2.0)
    session.add_all([engineering, sales, local_42, teamsters])
    session.commit()

    # 2. employees (salaries are weekly amounts - see ad-libs)
    alice = Employee(name="Alice Salaried", dept_id=engineering.id, type="salaried", salary=Decimal("4000"),
                     military="yes", branch="Army", rank="Captain", service_years=6)
    bob = Employee(name="Bob Hourly", dept_id=engineering.id, type="hourly", hours_worked=40, hourly_rate=50,
                   union_id=local_42.id, military="no")
    carol = Employee(name="Carol Hourly", dept_id=sales.id, type="hourly", hours_worked=35, hourly_rate=30,
                     military="yes", branch="Navy", rank="Petty Officer", service_years=3)
    dan = Employee(name="Dan Commissioned", dept_id=sales.id, type="commissioned", base_salary=Decimal("1500"), military="no")
    eve = Employee(name="Eve Salaried", dept_id=sales.id, type="salaried", salary=Decimal("3000"), military="no")
    session.add_all([alice, bob, carol, dan, eve])
    session.commit()

    # 3. orders for the commissioned employee
    session.add_all([Order(employee_id=dan.id, customer_name="Acme Corp", amount=Decimal("1200")),
                     Order(employee_id=dan.id, customer_name="Globex", amount=Decimal("800"))])
    session.commit()
    print("Seed data loaded")
