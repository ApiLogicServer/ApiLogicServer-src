import DECIMAL

from sqlalchemy.sql import func  # end imports from system/genai/create_db_models_inserts/create_db_models_prefix.py
from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, Date, ForeignKeyConstraint, DECIMAL, CheckConstraint, DateTime, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy.sql import select
import datetime

Base = declarative_base()

class Employee(Base):
    __tablename__ = 'employees'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String)
    organization_name = Column(String)

class Department(Base):
    __tablename__ = 'departments'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String)
    location = Column(String)
    manager_id = Column(Integer, ForeignKey('employees.id'))

class ProjectAllocatorPlan(Base):
    __tablename__ = 'project_allocator_plans'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String)
    date = Column(Date)

class DeptAllocator(Base):
    __tablename__ = 'dept_allocators'
    id = Column(Integer, primary_key=True, autoincrement=True)
    percent_allocation = Column(DECIMAL)  # FIXME Column(Decimal) -> Column(DECIMAL)
    project_allocator_plan_id = Column(Integer, ForeignKey('project_allocator_plans.id'))

class AccountAllocatorPlan(Base):
    __tablename__ = 'account_allocator_plans'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String)
    department_id = Column(Integer, ForeignKey('departments.id'))

class AccountAllocator(Base):
    __tablename__ = 'account_allocators'
    id = Column(Integer, primary_key=True, autoincrement=True)
    account_id = Column(Integer, ForeignKey('accounts.id'))
    percent_allocation = Column(DECIMAL)
    account_allocator_plan_id = Column(Integer, ForeignKey('account_allocator_plans.id'))

class Project(Base):
    __tablename__ = 'projects'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String)
    manager_id = Column(Integer, ForeignKey('employees.id'))
    project_allocator_plan_id = Column(Integer, ForeignKey('project_allocator_plans.id'))

class ProjectCharge(Base):
    __tablename__ = 'project_charges'
    id = Column(Integer, primary_key=True, autoincrement=True)
    charge_date = Column(Date)
    charge_amount = Column(DECIMAL)
    project_id = Column(Integer, ForeignKey('projects.id'))
    account_allocator_plan_id = Column(Integer, ForeignKey('account_allocator_plans.id'))

class Account(Base):
    __tablename__ = 'accounts'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String)
    charge_budget = Column(DECIMAL)

class DeptCharge(Base):
    __tablename__ = 'dept_charges'
    id = Column(Integer, primary_key=True, autoincrement=True)
    account_id = Column(Integer, ForeignKey('accounts.id'))
    charge_amount = Column(DECIMAL)
    project_charge_id = Column(Integer, ForeignKey('project_charges.id'))

class AccountCharge(Base):
    __tablename__ = 'account_charges'
    id = Column(Integer, primary_key=True, autoincrement=True)
    charge_amount = Column(DECIMAL)
    account_id = Column(Integer, ForeignKey('accounts.id'))

engine = create_engine('sqlite:///system/genai/temp/create_db_models.sqlite')
Base.metadata.create_all(engine)

# Create a session
Session = sessionmaker(bind=engine)
session = Session()

# Add test data
employee1 = Employee(name="John Doe", organization_name="Organization 1")
session.add(employee1)

department1 = Department(name="IT", location="Building A", manager_id=1)
session.add(department1)

project_allocator_plan1 = ProjectAllocatorPlan(name="Plan 1", date=datetime.date(2023, 1, 1))
session.add(project_allocator_plan1)

dept_allocator1 = DeptAllocator(percent_allocation=50.0, project_allocator_plan_id=1)
session.add(dept_allocator1)

account_allocator_plan1 = AccountAllocatorPlan(name="Account Plan 1", department_id=1)
session.add(account_allocator_plan1)

account_allocator1 = AccountAllocator(account_id=1, percent_allocation=30.0, account_allocator_plan_id=1)
session.add(account_allocator1)

project1 = Project(name="Project 1", manager_id=1, project_allocator_plan_id=1)
session.add(project1)

project_charge1 = ProjectCharge(charge_date=datetime.date(2023, 1, 5), charge_amount=100.0, project_id=1, account_allocator_plan_id=1)
session.add(project_charge1)

account1 = Account(name="Account 1", charge_budget=1000.0)
session.add(account1)

dept_charge1 = DeptCharge(account_id=1, charge_amount=100.0, project_charge_id=1)
session.add(dept_charge1)

account_charge1 = AccountCharge(charge_amount=100.0, account_id=1)
session.add(account_charge1)

session.commit()

# Query data (Example)
accounts = session.query(Account).all()
for account in accounts:
    print(f'Account ID: {account.id}, Name: {account.name}, Budget: {account.charge_budget}')
