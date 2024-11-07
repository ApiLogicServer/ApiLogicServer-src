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
    """description: Represents a student participating in courses."""
    __tablename__ = 'students'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    enrollment_date = Column(Date, nullable=True)
    budget = Column(Float, nullable=False)
    total_charges = Column(Float, nullable=False, default=0.0)


class Course(Base):
    """description: Represents a course available for enrollment."""
    __tablename__ = 'courses'

    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String, nullable=False)
    description = Column(String, nullable=True)
    start_date = Column(Date, nullable=True)
    end_date = Column(Date, nullable=True)
    charge = Column(Float, nullable=False)


class Teacher(Base):
    """description: Represents a teacher responsible for conducting courses."""
    __tablename__ = 'teachers'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    hire_date = Column(Date, nullable=True)
    num_courses_assigned = Column(Integer, nullable=False, default=0)


class Enrollment(Base):
    """description: Represents the association between a student and a course."""
    __tablename__ = 'enrollments'

    id = Column(Integer, primary_key=True, autoincrement=True)
    student_id = Column(Integer, ForeignKey('students.id'), nullable=False)
    course_id = Column(Integer, ForeignKey('courses.id'), nullable=False)
    status = Column(String, nullable=True)


class TeachingAssignment(Base):
    """description: Represents the assignment of a teacher to a course."""
    __tablename__ = 'teaching_assignments'

    id = Column(Integer, primary_key=True, autoincrement=True)
    teacher_id = Column(Integer, ForeignKey('teachers.id'), nullable=False)
    course_id = Column(Integer, ForeignKey('courses.id'), nullable=False)


class Grade(Base):
    """description: Represents grades received by students for courses."""
    __tablename__ = 'grades'

    id = Column(Integer, primary_key=True, autoincrement=True)
    enrollment_id = Column(Integer, ForeignKey('enrollments.id'), nullable=False)
    score = Column(Float, nullable=True)
    date_recorded = Column(Date, nullable=True)


class StudentAttendance(Base):
    """description: Tracks the attendance record for students in courses."""
    __tablename__ = 'student_attendances'

    id = Column(Integer, primary_key=True, autoincrement=True)
    enrollment_id = Column(Integer, ForeignKey('enrollments.id'), nullable=False)
    date = Column(Date, nullable=False)
    status = Column(String, nullable=False)


class CourseMaterial(Base):
    """description: Represents materials related to specific courses."""
    __tablename__ = 'course_materials'

    id = Column(Integer, primary_key=True, autoincrement=True)
    course_id = Column(Integer, ForeignKey('courses.id'), nullable=False)
    material_name = Column(String, nullable=False)
    material_type = Column(String, nullable=True)


class CourseSchedule(Base):
    """description: Represents the schedule dates for courses."""
    __tablename__ = 'course_schedules'

    id = Column(Integer, primary_key=True, autoincrement=True)
    course_id = Column(Integer, ForeignKey('courses.id'), nullable=False)
    scheduled_date = Column(Date, nullable=False)


class StudentContact(Base):
    """description: Represents contact details for students."""
    __tablename__ = 'student_contacts'

    id = Column(Integer, primary_key=True, autoincrement=True)
    student_id = Column(Integer, ForeignKey('students.id'), nullable=False)
    contact_type = Column(String, nullable=False)
    contact_value = Column(String, nullable=False)


class TeacherContact(Base):
    """description: Represents contact details for teachers."""
    __tablename__ = 'teacher_contacts'

    id = Column(Integer, primary_key=True, autoincrement=True)
    teacher_id = Column(Integer, ForeignKey('teachers.id'), nullable=False)
    contact_type = Column(String, nullable=False)
    contact_value = Column(String, nullable=False)


class Department(Base):
    """description: Represents a department within the educational institution."""
    __tablename__ = 'departments'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    head_id = Column(Integer, ForeignKey('teachers.id'), nullable=True)


# ALS/GenAI: Create an SQLite database
engine = create_engine('sqlite:///system/genai/temp/create_db_models.sqlite')
Base.metadata.create_all(engine)

Session = sessionmaker(bind=engine)
session = Session()

# ALS/GenAI: Prepare for sample data

from datetime import date

# Student data
student_1 = Student(id=1, name="Alice Doe", enrollment_date=date(2021, 9, 1), budget=2000.0, total_charges=0.0)
student_2 = Student(id=2, name="Bob Smith", enrollment_date=date(2021, 9, 1), budget=1500.0, total_charges=0.0)

# Course data
course_1 = Course(id=1, title="Introduction to Programming", description="Learn basics of programming.", start_date=date(2021, 9, 1), end_date=date(2021, 12, 15), charge=300.0)
course_2 = Course(id=2, title="Advanced Mathematics", description="Advanced study of mathematics.", start_date=date(2021, 9, 1), end_date=date(2021, 12, 15), charge=400.0)

# Teacher data
teacher_1 = Teacher(id=1, name="Dr. Emily Johnson", hire_date=date(2018, 8, 15), num_courses_assigned=0)
teacher_2 = Teacher(id=2, name="Professor Michael Brown", hire_date=date(2017, 5, 10), num_courses_assigned=0)

# Enrollment data
enrollment_1 = Enrollment(id=1, student_id=1, course_id=1)
enrollment_2 = Enrollment(id=2, student_id=2, course_id=2)

# Teaching Assignment data
teaching_assignment_1 = TeachingAssignment(id=1, teacher_id=1, course_id=1)
teaching_assignment_2 = TeachingAssignment(id=2, teacher_id=2, course_id=2)

# Grade data
grade_1 = Grade(id=1, enrollment_id=1, score=95.0, date_recorded=date(2021, 10, 15))
grade_2 = Grade(id=2, enrollment_id=2, score=89.0, date_recorded=date(2021, 10, 20))

# Student Attendance data
attendance_1 = StudentAttendance(id=1, enrollment_id=1, date=date(2021, 9, 1), status="Present")
attendance_2 = StudentAttendance(id=2, enrollment_id=2, date=date(2021, 9, 1), status="Absent")

# Course Material data
material_1 = CourseMaterial(id=1, course_id=1, material_name="Intro to Programming Textbook", material_type="Book")
material_2 = CourseMaterial(id=2, course_id=2, material_name="Advanced Math Workbook", material_type="Workbook")

# Course Schedule data
schedule_1 = CourseSchedule(id=1, course_id=1, scheduled_date=date(2021, 9, 1))
schedule_2 = CourseSchedule(id=2, course_id=2, scheduled_date=date(2021, 9, 1))

# Student Contact data
contact_1 = StudentContact(id=1, student_id=1, contact_type="Email", contact_value="alice.doe@example.com")
contact_2 = StudentContact(id=2, student_id=2, contact_type="Phone", contact_value="555-0012")

# Teacher Contact data
teacher_contact_1 = TeacherContact(id=1, teacher_id=1, contact_type="Email", contact_value="emily.johnson@example.com")
teacher_contact_2 = TeacherContact(id=2, teacher_id=2, contact_type="Phone", contact_value="555-0098")

# Department data
department_1 = Department(id=1, name="Computer Science", head_id=1)
department_2 = Department(id=2, name="Mathematics", head_id=2)


session.add_all([student_1, student_2, course_1, course_2, teacher_1, teacher_2, enrollment_1, enrollment_2, teaching_assignment_1, teaching_assignment_2, grade_1, grade_2, attendance_1, attendance_2, material_1, material_2, schedule_1, schedule_2, contact_1, contact_2, teacher_contact_1, teacher_contact_2, department_1, department_2])
session.commit()
