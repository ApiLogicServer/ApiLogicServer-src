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

    # No 'absent' rows seeded here on purpose - see docs/requirements/course_dropoff/ad-libs.md
    # 🔴 Review Required: seeding an assumed write path would misrepresent an open question.

    bio = Course(course_name="Intro to Biology", instructor_name="Dr. Smith", max_capacity=50)
    session.add(bio)
    session.commit()

    bio_1 = ClassSchedule(course_id=bio.id, session_date="2026-09-01", start_time="09:00", end_time="10:00")
    bio_2 = ClassSchedule(course_id=bio.id, session_date="2026-09-08", start_time="09:00", end_time="10:00")
    session.add_all([bio_1, bio_2])
    session.commit()

    alice = Student(first_name="Alice", last_name="Nguyen", email="alice@example.com")
    carol = Student(first_name="Carol", last_name="Diaz", email="carol@example.com")
    session.add_all([alice, carol])
    session.commit()

    # Alice: attends both Biology sessions
    session.add(Attendance(student_id=alice.id, class_schedule_id=bio_1.id, status="attended"))
    session.commit()
    session.add(Attendance(student_id=alice.id, class_schedule_id=bio_2.id, status="attended"))
    session.commit()

    # Carol: excused then attended - total_sessions_completed only counts 'attended'
    session.add(Attendance(student_id=carol.id, class_schedule_id=bio_1.id, status="excused"))
    session.commit()
    session.add(Attendance(student_id=carol.id, class_schedule_id=bio_2.id, status="attended"))
    session.commit()
