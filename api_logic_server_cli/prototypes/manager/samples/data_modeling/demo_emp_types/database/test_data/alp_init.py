#!/usr/bin/env python
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
import os
os.environ['AGGREGATE_DEFAULTS'] = 'True'

with flask_app.app_context():
    safrs.DB.create_all()
    # try:
    #     alice = Customer(id=1, name="Alice", credit_limit=1000, balance=0, total_orders=0)
    #     safrs.DB.session.add(alice)
    #     safrs.DB.session.commit()
    # except Exception as e:
    #     print(f"Error adding variable to session: {e}")

    

    if safrs.DB.session.query(Employee).count() == 0 and safrs.DB.session.query(Department).count() == 0:
        session = safrs.DB.session
        # lookup/parent rows first: committed before children whose formulas read them
        local_42 = LaborUnion(name="Local 42", dues_rate=2.5)
        engineering = Department(name="Engineering", budget=200000)
        sales = Department(name="Sales", budget=150000)
        session.add_all([local_42, engineering, sales])
        session.commit()

        session.add_all([
            Employee(type="salaried", name="Sally Salaried", dept_id=engineering.id, salary=90000),
            Employee(type="hourly", name="Harry Hourly", dept_id=engineering.id, hours_worked=40, hourly_rate=50, union_id=local_42.id),
            Employee(type="hourly", name="Nina Nonunion", dept_id=engineering.id, hours_worked=30, hourly_rate=40),
            Employee(type="commissioned", name="Carl Commissioned", dept_id=sales.id, base_salary=50000),
            Employee(type="salaried", name="Mia Military", dept_id=sales.id, salary=60000,
                     military="yes", branch="Navy", rank="Lieutenant", service_years=8),
        ])
        session.commit()
        carl = session.query(Employee).filter(Employee.name == "Carl Commissioned").one()
        session.add_all([Order(employee_id=carl.id, amount=1000, customer_name="Acme"),
                         Order(employee_id=carl.id, amount=2500, customer_name="Globex")])
        session.commit()
        print("demo_emp_types seed data loaded")
