from sqlalchemy.sql import func  # end imports from system/genai/create_db_models_inserts/create_db_models_prefix.py
import os
from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, String, DateTime, ForeignKey, Numeric, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Path to the SQLite database
database_path = os.path.join('system', 'genai', 'temp', 'create_db_models.sqlite')

# Create the engine
engine = create_engine(f'sqlite:///{database_path}', echo=True)

# Create session
Session = sessionmaker(bind=engine)
session = Session()

# Base class for our classes
Base = declarative_base()

# Define the tables

class Employee(Base):
    __tablename__ = 'employees'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), nullable=False)
    department = Column(String(50), nullable=True)

class Project(Base):
    __tablename__ = 'projects'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)

class Task(Base):
    __tablename__ = 'tasks'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    project_id = Column(Integer, ForeignKey('projects.id'), nullable=False)
    estimated_hours = Column(Numeric, nullable=True)

class TimeCard(Base):
    __tablename__ = 'timecards'
    id = Column(Integer, primary_key=True, autoincrement=True)
    employee_id = Column(Integer, ForeignKey('employees.id'), nullable=False)
    task_id = Column(Integer, ForeignKey('tasks.id'), nullable=False)
    date = Column(DateTime, default=datetime.utcnow, nullable=False)
    hours_worked = Column(Numeric, nullable=False)
    notes = Column(Text, nullable=True)

class Department(Base):
    __tablename__ = 'departments'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), nullable=False)
    description = Column(Text, nullable=True)

class Role(Base):
    __tablename__ = 'roles'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), nullable=False)
    description = Column(Text, nullable=True)

class EmployeeRole(Base):
    __tablename__ = 'employee_roles'
    id = Column(Integer, primary_key=True, autoincrement=True)
    employee_id = Column(Integer, ForeignKey('employees.id'), nullable=False)
    role_id = Column(Integer, ForeignKey('roles.id'), nullable=False)

class ProjectAssignment(Base):
    __tablename__ = 'project_assignments'
    id = Column(Integer, primary_key=True, autoincrement=True)
    project_id = Column(Integer, ForeignKey('projects.id'), nullable=False)
    employee_id = Column(Integer, ForeignKey('employees.id'), nullable=False)
    hours_allocated = Column(Numeric, nullable=True)
    start_date = Column(DateTime, default=datetime.utcnow, nullable=False)
    end_date = Column(DateTime, nullable=True)

class PayRate(Base):
    __tablename__ = 'pay_rates'
    id = Column(Integer, primary_key=True, autoincrement=True)
    employee_id = Column(Integer, ForeignKey('employees.id'), nullable=False)
    rate = Column(Numeric, nullable=False)
    effective_date = Column(DateTime, default=datetime.utcnow, nullable=False)

class Expense(Base):
    __tablename__ = 'expenses'
    id = Column(Integer, primary_key=True, autoincrement=True)
    project_id = Column(Integer, ForeignKey('projects.id'), nullable=False)
    employee_id = Column(Integer, ForeignKey('employees.id'), nullable=False)
    amount = Column(Numeric, nullable=False)
    date = Column(DateTime, default=datetime.utcnow, nullable=False)
    description = Column(Text, nullable=True)

# Create all tables
Base.metadata.create_all(engine)

# Insert some sample data
def insert_sample_data():
    emp1 = Employee(name='John Smith', department='Engineering')
    emp2 = Employee(name='Jane Doe', department='Marketing')
    proj1 = Project(name='Project A', description='Project A Description')
    proj2 = Project(name='Project B', description='Project B Description')
    task1 = Task(name='Design', project_id=1, estimated_hours=10)
    task2 = Task(name='Development', project_id=1, estimated_hours=20)
    timecard1 = TimeCard(employee_id=1, task_id=1, date=datetime(2023, 10, 1, 9, 0, 0), hours_worked=8, notes='Completed design')
    timecard2 = TimeCard(employee_id=1, task_id=2, date=datetime(2023, 10, 2, 9, 0, 0), hours_worked=6, notes='Started development')
    dept1 = Department(name='Engineering', description='Engineering Department')
    role1 = Role(name='Developer', description='Writes code')
    emp_role1 = EmployeeRole(employee_id=1, role_id=1)
    proj_assign1 = ProjectAssignment(project_id=1, employee_id=1, hours_allocated=20, start_date=datetime(2023, 9, 1), end_date=datetime(2023, 12, 31))
    pay_rate1 = PayRate(employee_id=1, rate=50.00, effective_date=datetime(2023, 1, 1))
    expense1 = Expense(project_id=1, employee_id=1, amount=200.00, date=datetime(2023, 10, 3), description='Software purchase')

    session.add(emp1)
    session.add(emp2)
    session.add(proj1)
    session.add(proj2)
    session.add(task1)
    session.add(task2)
    session.add(timecard1)
    session.add(timecard2)
    session.add(dept1)
    session.add(role1)
    session.add(emp_role1)
    session.add(proj_assign1)
    session.add(pay_rate1)
    session.add(expense1)

    session.commit()

insert_sample_data()
