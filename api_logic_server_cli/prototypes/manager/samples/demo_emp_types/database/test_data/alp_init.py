#!/usr/bin/env python
import os, logging, logging.config, sys
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

    try:
        # Parents committed first so their real integer ids are available below —
        # a formula like union_dues reads row.union_id directly (not via Rule.sum's
        # aggregate-adjustment machinery), so the FK must already be resolved when
        # the employee row is inserted, not merely linked via an unflushed relationship.
        engineering = Department(name="Engineering", budget=200000)
        sales = Department(name="Sales", budget=150000)
        session.add_all([engineering, sales])
        local_42 = LaborUnion(name="Local 42", dues_rate=5.0)
        session.add(local_42)
        session.commit()

        # salaried — one plain, one military
        alice = Employee(type="salaried", name="Alice Johnson", dept_id=engineering.id, salary=8000)
        bob = Employee(type="salaried", name="Bob Martinez", dept_id=sales.id, salary=7500,
                       military="yes", branch="Army", rank="Sergeant", service_years=6)

        # hourly — one union member, one non-union + military
        carol = Employee(type="hourly", name="Carol Nguyen", dept_id=engineering.id,
                         hours_worked=40, hourly_rate=50, union_id=local_42.id)
        david = Employee(type="hourly", name="David Kim", dept_id=sales.id,
                         hours_worked=35, hourly_rate=45,
                         military="yes", branch="Navy", rank="Petty Officer", service_years=4)

        # commissioned — one plain, one military
        erin = Employee(type="commissioned", name="Erin Walsh", dept_id=engineering.id, base_salary=3000)
        frank = Employee(type="commissioned", name="Frank Osei", dept_id=sales.id, base_salary=2500,
                         military="yes", branch="Marines", rank="Captain", service_years=10)

        session.add_all([alice, bob, carol, david, erin, frank])
        session.commit()

        # Orders reference the now-committed commissioned employees by id
        session.add_all([
            CommissionOrder(employee_id=erin.id, amount=1200, customer_name="Acme Corp"),
            CommissionOrder(employee_id=erin.id, amount=800, customer_name="Globex Inc"),
            CommissionOrder(employee_id=frank.id, amount=1500, customer_name="Initech"),
        ])
        session.commit()
        app_logger.info("demo_emp_types: seeded 2 departments, 1 union, 6 employees, 3 commission orders")
    except Exception as e:
        session.rollback()
        app_logger.error(f"demo_emp_types seed error: {e}")
        raise


