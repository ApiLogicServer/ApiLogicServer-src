#!/usr/bin/env python
"""
One-time initialization of the daily totals for rows that existed before the totals were added (the sample orders):
sets each Order's CreatedOnDay from its CreatedOn, through the ORM inside the app, so the rules create and adjust the
DailyFlow rows (see logic_bank_api.md, "initialize derived columns for pre-existing rows").
Run from the project root with the server stopped:   KAFKA_SERVER= python database/test_data/init_daily_flow.py
"""
import os, sys, logging
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
os.environ["PROJECT_DIR"] = os.environ.get("PROJECT_DIR", str(Path(__file__).parent.parent.parent))
from flask import Flask
from config import server_setup
import config.config as config
server_setup.logging_setup().setLevel(logging.WARNING)
flask_app = Flask("API Logic Server", template_folder='ui/templates')
flask_app.config.from_object(config.Config)
flask_app.config.from_prefixed_env(prefix="APILOGICPROJECT")
server_setup.api_logic_server_setup(flask_app, server_setup.get_args(flask_app))
import safrs
from database import models

with flask_app.app_context():
    session = safrs.DB.session
    todo = session.query(models.Order).filter(models.Order.CreatedOnDay.is_(None), models.Order.CreatedOn.is_not(None)).all()
    # insert_parent creates a day row only on INSERT; on an UPDATE that moves a row to a new day, LogicBank 1.34.04
    # raises "Unable to Adjust Missing Adopting Parent" - so create the missing day rows first (the rules fill them)
    days = {order.CreatedOn.strftime('%Y-%m-%d') for order in todo}
    existing = {d.day for d in session.query(models.DailyFlow).filter(models.DailyFlow.day.in_(days))}
    session.add_all([models.DailyFlow(day=day) for day in days - existing])
    session.commit()
    for order in todo:
        order.CreatedOnDay = order.CreatedOn.strftime('%Y-%m-%d')
    session.commit()
    print(f"initialized CreatedOnDay on {len(todo)} orders")
