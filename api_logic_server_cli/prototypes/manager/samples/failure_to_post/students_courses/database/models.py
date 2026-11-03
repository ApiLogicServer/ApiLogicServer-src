# coding: utf-8
from sqlalchemy import DECIMAL, DateTime  # API Logic Server GenAI assist
from sqlalchemy import Column, ForeignKey, Integer, TIMESTAMP, Text, text
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

########################################################################################################################
# Classes describing database for SqlAlchemy ORM, initially created by schema introspection.
#
# Alter this file per your database maintenance policy
#    See https://apilogicserver.github.io/Docs/Project-Rebuild/#rebuilding
#
# Created:  September 27, 2026 20:41:54
# Database: sqlite:////Users/val/dev/ApiLogicServer/ApiLogicServer-dev/build_and_test/genai-logic/students_courses/database/db.sqlite
# Dialect:  sqlite
#
# mypy: ignore-errors
########################################################################################################################
 
from database.system.SAFRSBaseX import SAFRSBaseX, TestBase
from flask_login import UserMixin
import safrs, flask_sqlalchemy, os
from safrs import jsonapi_attr
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship
from sqlalchemy.orm import Mapped
from sqlalchemy.sql.sqltypes import NullType
from typing import List

db = SQLAlchemy() 
Base = declarative_base()  # type: flask_sqlalchemy.model.DefaultMeta
metadata = Base.metadata

#NullType = db.String  # datatype fixup
#TIMESTAMP= db.TIMESTAMP

from sqlalchemy.dialects.sqlite import *

if os.getenv('APILOGICPROJECT_NO_FLASK') is None or os.getenv('APILOGICPROJECT_NO_FLASK') == 'None':
    Base = SAFRSBaseX   # enables rules to be used outside of Flask, e.g., test data loading
else:
    Base = TestBase     # ensure proper types, so rules work for data loading
    print('*** Models.py Using TestBase ***')



class Course(Base):  # type: ignore
    __tablename__ = 'courses'
    _s_collection_name = 'Course'  # type: ignore

    id = Column(Integer, primary_key=True)
    course_name = Column(Text, nullable=False)
    instructor_name = Column(Text)
    max_capacity = Column(Integer, server_default=text("30"))
    enrolled_count = Column(Integer, server_default=text("0"))

    # parent relationships (access parent)

    # child relationships (access children)
    ClassScheduleList : Mapped[List["ClassSchedule"]] = relationship(back_populates="course")



class Student(Base):  # type: ignore
    __tablename__ = 'students'
    _s_collection_name = 'Student'  # type: ignore

    id = Column(Integer, primary_key=True)
    first_name = Column(Text, nullable=False)
    last_name = Column(Text, nullable=False)
    email = Column(Text)
    active_alert_count = Column(Integer, server_default=text("0"))
    consecutive_absences = Column(Integer, server_default=text("0"))
    total_sessions_completed = Column(Integer, server_default=text("0"))
    created_at = Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP"))

    # parent relationships (access parent)

    # child relationships (access children)
    AlertList : Mapped[List["Alert"]] = relationship(back_populates="student")
    AttendanceList : Mapped[List["Attendance"]] = relationship(back_populates="student")



class SysConfig(Base):  # type: ignore
    __tablename__ = 'sys_config'
    _s_collection_name = 'SysConfig'  # type: ignore

    id = Column(Integer, primary_key=True)
    name = Column(Text, nullable=False, unique=True)
    consecutive_absence_threshold = Column(Integer, server_default=text("2"))

    # parent relationships (access parent)

    # child relationships (access children)



class Alert(Base):  # type: ignore
    __tablename__ = 'alerts'
    _s_collection_name = 'Alert'  # type: ignore

    id = Column(Integer, primary_key=True)
    student_id = Column(ForeignKey('students.id'), nullable=False)
    alert_type = Column(Text, nullable=False)
    status = Column(Text, server_default=text("'active'"), nullable=False)
    message = Column(Text, nullable=False)
    created_at = Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP"))

    # parent relationships (access parent)
    student : Mapped["Student"] = relationship(back_populates=("AlertList"))

    # child relationships (access children)



class ClassSchedule(Base):  # type: ignore
    __tablename__ = 'class_schedules'
    _s_collection_name = 'ClassSchedule'  # type: ignore

    id = Column(Integer, primary_key=True)
    course_id = Column(ForeignKey('courses.id'), nullable=False)
    session_date = Column(Text, nullable=False)
    start_time = Column(Text)
    end_time = Column(Text)
    attended_count = Column(Integer, server_default=text("0"))

    # parent relationships (access parent)
    course : Mapped["Course"] = relationship(back_populates=("ClassScheduleList"))

    # child relationships (access children)
    AttendanceList : Mapped[List["Attendance"]] = relationship(back_populates="class_schedule")



class Attendance(Base):  # type: ignore
    __tablename__ = 'attendances'
    _s_collection_name = 'Attendance'  # type: ignore

    id = Column(Integer, primary_key=True)
    student_id = Column(ForeignKey('students.id'), nullable=False)
    class_schedule_id = Column(ForeignKey('class_schedules.id'), nullable=False)
    status = Column(Text, nullable=False)
    recorded_at = Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP"))

    # parent relationships (access parent)
    class_schedule : Mapped["ClassSchedule"] = relationship(back_populates=("AttendanceList"))
    student : Mapped["Student"] = relationship(back_populates=("AttendanceList"))

    # child relationships (access children)
