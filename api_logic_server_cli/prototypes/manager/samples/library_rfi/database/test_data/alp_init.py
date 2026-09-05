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
    try:
        session = safrs.DB.session

        alice = Member(name="Alice Nguyen", email="alice@example.com")
        bob = Member(name="Bob Carter", email="bob@example.com")
        carla = Member(name="Carla Diaz", email="carla@example.com")
        session.add_all([alice, bob, carla])
        session.commit()

        hobbit = Book(title="The Hobbit", author="J.R.R. Tolkien")
        dune = Book(title="Dune", author="Frank Herbert")
        foundation = Book(title="Foundation", author="Isaac Asimov")
        clean_code = Book(title="Clean Code", author="Robert C. Martin")
        session.add_all([hobbit, dune, foundation, clean_code])
        session.commit()

        # Alice: current loan, not overdue
        loan_current = Loan(member_id=alice.id, book_id=hobbit.id,
                             checkout_date="2026-08-25")
        # Bob: overdue loan on Dune (due_date will compute to 2026-07-22, well past today)
        loan_overdue = Loan(member_id=bob.id, book_id=dune.id,
                             checkout_date="2026-07-01", return_date="2026-08-10")
        session.add_all([loan_current, loan_overdue])
        session.commit()

        # Carla wants Dune, which Bob's loan (above) has already made unavailable
        # while it was outstanding -- demonstrate the hold queue on Foundation instead,
        # where Bob is mid-loan and Carla is on hold behind him.
        loan_foundation = Loan(member_id=bob.id, book_id=foundation.id,
                                checkout_date="2026-08-20")
        session.add(loan_foundation)
        session.commit()

        hold_carla = Hold(member_id=carla.id, book_id=foundation.id,
                           requested_date="2026-08-28")
        session.add(hold_carla)
        session.commit()

        print("library_rfi seed data loaded: 3 members, 4 books, 3 loans, 1 hold")
    except Exception as e:
        print(f"Error adding variable to session: {e}")

    
