from sqlalchemy.sql import func  # end imports from system/genai/create_db_models_inserts/create_db_models_prefix.py
from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, DateTime, Numeric
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import datetime

# Create an engine and base class
engine = create_engine('sqlite:///system/genai/temp/create_db_models.sqlite', echo=True)
Base = declarative_base()

# Define tables
class Employee(Base):
    __tablename__ = 'employees'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)

class Project(Base):
    __tablename__ = 'projects'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)

class Task(Base):
    __tablename__ = 'tasks'
    id = Column(Integer, primary_key=True, autoincrement=True)
    project_id = Column(Integer, ForeignKey('projects.id'), nullable=False)
    name = Column(String, nullable=False)

class TimeEntry(Base):
    __tablename__ = 'time_entries'
    id = Column(Integer, primary_key=True, autoincrement=True)
    employee_id = Column(Integer, ForeignKey('employees.id'), nullable=False)
    task_id = Column(Integer, ForeignKey('tasks.id'), nullable=False)
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=False)
    hours_worked = Column(Numeric, nullable=False)

class Payroll(Base):
    __tablename__ = 'payrolls'
    id = Column(Integer, primary_key=True, autoincrement=True)
    employee_id = Column(Integer, ForeignKey('employees.id'), nullable=False)
    pay_date = Column(DateTime, nullable=False)
    amount = Column(Numeric, nullable=False)

class Department(Base):
    __tablename__ = 'departments'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)

class EmployeeDepartment(Base):
    __tablename__ = 'employee_departments'
    id = Column(Integer, primary_key=True, autoincrement=True)
    employee_id = Column(Integer, ForeignKey('employees.id'), nullable=False)
    department_id = Column(Integer, ForeignKey('departments.id'), nullable=False)

class Client(Base):
    __tablename__ = 'clients'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)

class ProjectAssignment(Base):
    __tablename__ = 'project_assignments'
    id = Column(Integer, primary_key=True, autoincrement=True)
    employee_id = Column(Integer, ForeignKey('employees.id'), nullable=False)
    project_id = Column(Integer, ForeignKey('projects.id'), nullable=False)

class Invoice(Base):
    __tablename__ = 'invoices'
    id = Column(Integer, primary_key=True, autoincrement=True)
    project_id = Column(Integer, ForeignKey('projects.id'), nullable=False)
    invoice_date = Column(DateTime, nullable=False)
    amount = Column(Numeric, nullable=False)

# Create all tables in the engine
Base.metadata.create_all(engine)

# Create a session to insert test data
Session = sessionmaker(bind=engine)
session = Session()

# Create some test data
employee1 = Employee(name='John Doe')
employee2 = Employee(name='Jane Smith')
project1 = Project(name='Project A')
project2 = Project(name='Project B')
task1 = Task(project_id=1, name='Task 1')
task2 = Task(project_id=1, name='Task 2')
task3 = Task(project_id=2, name='Task 3')
time_entry1 = TimeEntry(employee_id=1, task_id=1, start_time=datetime.datetime.now(), end_time=datetime.datetime.now() + datetime.timedelta(hours=2), hours_worked=2.0)
time_entry2 = TimeEntry(employee_id=2, task_id=2, start_time=datetime.datetime.now(), end_time(datetime.datetime.now() + datetime.timedelta(hours=3), hours_worked=3.0))
payroll1 = Payroll(employee_id=1, pay_date=datetime.datetime.now(), amount=1500.00)
payroll2 = Payroll(employee_id=2, pay_date=datetime.datetime.now(), amount=1600.00)
department1 = Department(name='HR')
department2 = Department(name='Engineering')
emp_dept1 = EmployeeDepartment(employee_id=1, department_id=1)
emp_dept2 = EmployeeDepartment(employee_id=2, department_id=2)
client1 = Client(name='Client X')
client2 = Client(name='Client Y')
proj_assign1 = ProjectAssignment(employee_id=1, project_id=1)
proj_assign2 = ProjectAssignment(employee_id=2, project_id=2)
invoice1 = Invoice(project_id=1, invoice_date=datetime.datetime.now(), amount=2000.00)
invoice2 = Invoice(project_id=2, invoice_date=datetime.datetime.now(), amount=3000.00)

# Add and commit test data to the session
session.add_all([employee1, employee2, project1, project2, task1, task2, task3, time_entry1, time_entry2, payroll1, payroll2, department1, department2, emp_dept1, emp_dept2, client1, client2, proj_assign1, proj_assign2, invoice1, invoice2])
session.commit()

# Close the session
session.close()
