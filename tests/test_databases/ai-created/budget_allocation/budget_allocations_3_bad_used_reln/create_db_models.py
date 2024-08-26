import decimal

from sqlalchemy.sql import func  # end imports from system/genai/create_db_models_inserts/create_db_models_prefix.py
from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, DateTime, Numeric, CheckConstraint, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker

Base = declarative_base()
DB_PATH = 'sqlite:///system/genai/temp/create_db_models.sqlite'

# Define our classes

class Employee(Base):
    __tablename__ = 'employees'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String)
    organization_name = Column(String)
    # managed_projects = relationship("Project", back_populates="managed_by")
    # managed_departments = relationship("Department", back_populates="managed_by")

class Department(Base):
    __tablename__ = 'departments'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String)
    location = Column(String)
    managed_by_id = Column(Integer, ForeignKey('employees.id'))
    # accounts = relationship("Account", back_populates="department")
    # managed_by = relationship("Employee", back_populates="managed_departments")

class ProjectAllocatorPlan(Base):
    __tablename__ = 'project_allocator_plans'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String)
    date = Column(DateTime)
    # dept_allocations = relationship("DeptAllocator", back_populates="project_allocator_plan")

class DeptAllocator(Base):
    __tablename__ = 'dept_allocators'
    id = Column(Integer, primary_key=True, autoincrement=True)
    percent_allocation = Column(Numeric)
    project_allocator_plan_id = Column(Integer, ForeignKey('project_allocator_plans.id'))
    account_allocator_plan_id = Column(Integer, ForeignKey('account_allocator_plans.id'))
    # project_allocator_plan = relationship("ProjectAllocatorPlan", back_populates="dept_allocations")

class Project(Base):
    __tablename__ = 'projects'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String)
    managed_by_id = Column(Integer, ForeignKey('employees.id'))
    project_allocator_plan_id = Column(Integer, ForeignKey('project_allocator_plans.id'))
    # project_allocator_plan = relationship("ProjectAllocatorPlan")
    # managed_by = relationship("Employee", back_populates="managed_projects")
    # project_charges = relationship("ProjectCharge", back_populates="project")

class ProjectCharge(Base):
    __tablename__ = 'project_charges'
    id = Column(Integer, primary_key=True, autoincrement=True)
    charge_date = Column(DateTime)
    charge_amount = Column(Numeric)
    project_id = Column(Integer, ForeignKey('projects.id'))
    # project = relationship("Project", back_populates="project_charges")

class Account(Base):
    __tablename__ = 'accounts'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String)
    department_id = Column(Integer, ForeignKey('departments.id'))
    charge_budget = Column(Numeric)
    # department = relationship("Department", back_populates="accounts")
    # project_charges = relationship("ProjectCharge")
    # account_allocators_plans = relationship("AccountAllocatorPlan", back_populates="account")

class DeptAllocation(Base):
    __tablename__ = 'dept_allocations'
    id = Column(Integer, primary_key=True, autoincrement=True)
    charge_amount = Column(Numeric)
    account_id = Column(Integer, ForeignKey('accounts.id'))
    # account = relationship("Account")

class AccountAllocatorPlan(Base):
    __tablename__ = 'account_allocator_plans'
    id = Column(Integer, primary_key=True, autoincrement=True)
    department_id = Column(Integer, ForeignKey('departments.id'))
    # department = relationship("Department")
    # account_allocators = relationship("AccountAllocator", back_populates="account_allocator_plan")

class AccountAllocator(Base):
    __tablename__ = 'account_allocators'
    id = Column(Integer, primary_key=True, autoincrement=True)
    percent_allocation = Column(Numeric)
    account_id = Column(Integer, ForeignKey('accounts.id'))
    account_allocator_plan_id = Column(Integer, ForeignKey('account_allocator_plans.id'))
    # account_allocator_plan = relationship("AccountAllocatorPlan", back_populates="account_allocators")

class AccountCharge(Base):
    __tablename__ = 'account_charges'
    id = Column(Integer, primary_key=True, autoincrement=True)
    charge_amount = Column(Numeric)
    account_id = Column(Integer, ForeignKey('accounts.id'))


# Initialize the database
engine = create_engine(DB_PATH)
Base.metadata.create_all(engine)

# Create a session to add some test data
Session = sessionmaker(bind=engine)
session = Session()

# Add some example data
employee1 = Employee(name="John Doe", organization_name="Tech Co.")
department1 = Department(name="IT", location="New York", managed_by=employee1)
project_allocator_plan1 = ProjectAllocatorPlan(name="Q1 Allocation", date=datetime.now())
dept_allocator1 = DeptAllocator(percent_allocation=50, project_allocator_plan=project_allocator_plan1)
project1 = Project(name="Project A", managed_by=employee1, project_allocator_plan=project_allocator_plan1)
project_charge1 = ProjectCharge(charge_date=datetime.now(), charge_amount=1000, project=project1)
account1 = Account(name="Account 1", department=department1, charge_budget=5000)
dept_allocation1 = DeptAllocation(charge_amount=200, account=account1)
account_allocator_plan1 = AccountAllocatorPlan(department=department1)
account_allocator1 = AccountAllocator(percent_allocation=75, account=account1, account_allocator_plan=account_allocator_plan1)

# Add instances to the session
session.add(employee1)
session.add(department1)
session.add(project_allocator_plan1)
session.add(dept_allocator1)
session.add(project1)
session.add(project_charge1)
session.add(account1)
session.add(dept_allocation1)
session.add(account_allocator_plan1)
session.add(account_allocator1)

# Commit all instances to the database
session.commit()

# Close the session
session.close()
