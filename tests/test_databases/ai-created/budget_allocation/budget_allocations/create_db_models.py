import decimal

from sqlalchemy.sql import func  # end imports from system/genai/create_db_models_inserts/create_db_models_prefix.py
from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, DateTime, Numeric
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.ext.hybrid import hybrid_property
from datetime import datetime

# Create SQLite engine
engine = create_engine('sqlite:///system/genai/temp/create_db_models.sqlite', echo=True)

# Create a base class
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
    managed_by = Column(Integer, ForeignKey('employees.id'))

class ProjectAllocatorPlan(Base):
    __tablename__ = 'project_allocator_plans'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String)
    date = Column(DateTime, default=datetime.utcnow)
    
    @hybrid_property
    def total_percent_allocation(self):
        return sum(allocator.percent_allocation for allocator in self.dept_allocators)
    
class DeptAllocator(Base):
    __tablename__ = 'dept_allocators'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    project_allocator_plan_id = Column(Integer, ForeignKey('project_allocator_plans.id'))
    percent_allocation = Column(Numeric)
    account_allocator_plan_id = Column(Integer, ForeignKey('account_allocator_plans.id'))

class Project(Base):
    __tablename__ = 'projects'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String)
    managed_by = Column(Integer, ForeignKey('employees.id'))
    project_allocator_plan_id = Column(Integer, ForeignKey('project_allocator_plans.id'))

class ProjectCharge(Base):
    __tablename__ = 'project_charges'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    charge_date = Column(DateTime, default=datetime.utcnow)
    charge_amount = Column(Numeric)
    project_id = Column(Integer, ForeignKey('projects.id'))
    account_id = Column(Integer, ForeignKey('accounts.id'))
    account_allocator_plan_id = Column(Integer, ForeignKey('account_allocator_plans.id'))

class Account(Base):
    __tablename__ = 'accounts'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String)
    department_id = Column(Integer, ForeignKey('departments.id'))
    charge_budget = Column(Numeric)
    
    @hybrid_property
    def total_charge_amount(self):
        return sum(charge.charge_amount for charge in self.project_charges)

class DeptAllocation(Base):
    __tablename__ = 'dept_allocations'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    account_id = Column(Integer, ForeignKey('accounts.id'))
    charge_amount = Column(Numeric)

class AccountAllocatorPlan(Base):
    __tablename__ = 'account_allocator_plans'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    department_id = Column(Integer, ForeignKey('departments.id'))

    @hybrid_property
    def total_percent_allocation(self):
        return sum(allocator.percent_allocation for allocator in self.account_allocators)

class AccountAllocator(Base):
    __tablename__ = 'account_allocators'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    account_id = Column(Integer, ForeignKey('accounts.id'))
    percent_allocation = Column(Numeric)

class AccountCharge(Base):
    __tablename__ = 'account_charges'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    charge_amount = Column(Numeric)
    account_id = Column(Integer, ForeignKey('accounts.id'))

# Creating tables
Base.metadata.create_all(engine)

# Creating a session
Session = sessionmaker(bind=engine)
session = Session()

# Adding some test data
emp = Employee(name="John Doe", organization_name="ABC Corp")
session.add(emp)
session.commit()

dept = Department(name="IT", location="Building 1", managed_by=emp.id)
session.add(dept)
session.commit()

project_allocator_plan = ProjectAllocatorPlan(name="Plan A")
session.add(project_allocator_plan)
session.commit()

dept_allocator = DeptAllocator(project_allocator_plan_id=project_allocator_plan.id, percent_allocation=50, account_allocator_plan_id=None)
session.add(dept_allocator)
session.commit()

project = Project(name="Project X", managed_by=emp.id, project_allocator_plan_id=project_allocator_plan.id)
session.add(project)
session.commit()

account = Account(name="Account 1", department_id=dept.id, charge_budget=10000)
session.add(account)
session.commit()

project_charge = ProjectCharge(charge_date=datetime.utcnow(), charge_amount=1000, project_id=project.id, account_id=account.id, account_allocator_plan_id=None)
session.add(project_charge)
session.commit()

dept_allocation = DeptAllocation(account_id=account.id, charge_amount=500)
session.add(dept_allocation)
session.commit()

account_allocator_plan = AccountAllocatorPlan(department_id=dept.id)
session.add(account_allocator_plan)
session.commit()

account_allocator = AccountAllocator(account_id=account.id, percent_allocation=30)
session.add(account_allocator)
session.commit()

account_charge = AccountCharge(charge_amount=1000, account_id=account.id)
session.add(account_charge)
session.commit()

# Closing session
session.close()
