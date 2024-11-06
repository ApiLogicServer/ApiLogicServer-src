# created from response, to create create_db_models.sqlite, with test data
#    that is used to create project
# should run without error in manager 
#    if not, check for decimal, indent, or import issues

import decimal
import logging
import sqlalchemy
from sqlalchemy.sql import func 
from logic_bank.logic_bank import Rule
from sqlalchemy import create_engine, Column, Integer, String, Float, ForeignKey, Date, DateTime, Numeric, Boolean, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import relationship
from datetime import date   
from datetime import datetime

logging.getLogger('sqlalchemy.engine.Engine').disabled = True  # remove for additional logging

Base = declarative_base()  # from system/genai/create_db_models_inserts/create_db_models_prefix.py


class Student(Base):
    """description: Represents a student in the system."""
    __tablename__ = 'students'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    email = Column(String, nullable=True)
    enrollment_date = Column(Date, nullable=True)


class Course(Base):
    """description: Represents a course offered in the system."""
    __tablename__ = 'courses'

    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String, nullable=False)
    description = Column(String, nullable=True)


class Teacher(Base):
    """description: Represents a teacher responsible for courses."""
    __tablename__ = 'teachers'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    department = Column(String, nullable=True)


class Offering(Base):
    """description: Represents the association between courses and teachers."""
    __tablename__ = 'offerings'

    id = Column(Integer, primary_key=True, autoincrement=True)
    course_id = Column(Integer, ForeignKey('courses.id'))
    teacher_id = Column(Integer, ForeignKey('teachers.id'))
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=True)
    total_students = Column(Integer, default=0)  # Required for logic rule to count enrolled students


class Enrollment(Base):
    """description: Represents the enrollment of students in offerings."""
    __tablename__ = 'enrollments'

    id = Column(Integer, primary_key=True, autoincrement=True)
    student_id = Column(Integer, ForeignKey('students.id'))
    offering_id = Column(Integer, ForeignKey('offerings.id'))
    enrollment_date = Column(Date, nullable=False)


# ALS/GenAI: Create an SQLite database
engine = create_engine('sqlite:///system/genai/temp/create_db_models.sqlite')
Base.metadata.create_all(engine)

Session = sessionmaker(bind=engine)
session = Session()

# ALS/GenAI: Prepare for sample data

from datetime import date

# Creating Student Test Data
student1 = Student(name="John Doe", email="john.doe@example.com", enrollment_date=date(2022, 9, 1))
student2 = Student(name="Jane Smith", email="jane.smith@example.com", enrollment_date=date(2022, 9, 1))
student3 = Student(name="Alan Turing", email="alan.turing@example.com", enrollment_date=date(2022, 9, 1))

# Creating Course Test Data
course1 = Course(title="Mathematics 101", description="An introductory course on Mathematics.")
course2 = Course(title="Physics 101", description="An introductory course on Physics.")

# Creating Teacher Test Data
teacher1 = Teacher(name="Dr. Brown", department="Mathematics")
teacher2 = Teacher(name="Dr. Green", department="Physics")

# Creating Offering Test Data
offering1 = Offering(course_id=1, teacher_id=1, start_date=date(2022, 9, 1), end_date=date(2022, 12, 15), total_students=2)
offering2 = Offering(course_id=2, teacher_id=2, start_date=date(2022, 9, 1), total_students=1)

# Creating Enrollment Test Data
enrollment1 = Enrollment(student_id=1, offering_id=1, enrollment_date=date(2022, 9, 1))
enrollment2 = Enrollment(student_id=2, offering_id=1, enrollment_date=date(2022, 9, 2))
enrollment3 = Enrollment(student_id=3, offering_id=2, enrollment_date=date(2022, 9, 2))


session.add_all([student1, student2, student3, course1, course2, teacher1, teacher2, offering1, offering2, enrollment1, enrollment2, enrollment3])
session.commit()
