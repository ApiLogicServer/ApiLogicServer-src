import decimal

from sqlalchemy.sql import func  # end imports from system/genai/create_db_models_inserts/create_db_models_prefix.py
from sqlalchemy import create_engine, Column, Integer, String, DECIMAL, Date, ForeignKey, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker, column_property
import datetime

# Creating SQLite database
engine = create_engine("sqlite:///system/genai/temp/create_db_models.sqlite", echo=True)
Base = declarative_base()

# Employee Table
class Employee(Base):
    __tablename__ = 'employees'
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    organization_name = Column(String)

# Departments Table
class Department(Base):
    __tablename__ = 'departments'
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    location = Column(String)
    managed_by_id = Column(Integer, ForeignKey('employees.id'))

    managed_by = relationship('Employee', foreign_keys=[managed_by_id])
    accounts = relationship('Account', back_populates='department')

# Projects Table
class Project(Base):
    __tablename__ = 'projects'
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    managed_by_id = Column(Integer, ForeignKey('employees.id'))
    project_allocator_plan_id = Column(Integer, ForeignKey('project_allocator_plans.id'))
    
    managed_by = relationship('Employee', foreign_keys=[managed_by_id])
    project_allocator_plan = relationship('ProjectAllocatorPlan')


# ProjectAllocatorPlan Table
class ProjectAllocatorPlan(Base):
    __tablename__ = 'project_allocator_plans'
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    date = Column(Date, default=datetime.datetime.now)
    
    dept_allocators = relationship('DeptAllocator', back_populates='project_allocator_plan')
    
    total_percent_allocation = column_property(
        select([func.sum(DeptAllocator.percent_allocation)]).where(DeptAllocator.project_allocator_plan_id == id)
    )

# DeptAllocator Table
class DeptAllocator(Base):
    __tablename__ = 'dept_allocators'
    id = Column(Integer, primary_key=True)
    project_allocator_plan_id = Column(Integer, ForeignKey('project_allocator_plans.id'))
    percent_allocation = Column(DECIMAL, nullable=False)
    account_allocator_plan_id = Column(Integer, ForeignKey('account_allocator_plans.id'))

    project_allocator_plan = relationship('ProjectAllocatorPlan', foreign_keys=[project_allocator_plan_id])
    account_allocator_plan = relationship('AccountAllocatorPlan', foreign_keys=[account_allocator_plan_id])

# Account Table
class Account(Base):
    __tablename__ = 'accounts'
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    department_id = Column(Integer, ForeignKey('departments.id'))
    charge_budget = Column(DECIMAL, nullable=False)
    
    department = relationship('Department', back_populates='accounts')
    project_charges = relationship('ProjectCharge', back_populates='account')
    
    total_charge_amount = column_property(
        select([func.sum(ProjectCharge.charge_amount)]).where(ProjectCharge.account_id == id)
    )

# AccountAllocatorPlan Table
class AccountAllocatorPlan(Base):
    __tablename__ = 'account_allocator_plans'
    id = Column(Integer, primary_key=True)
    department_id = Column(Integer, ForeignKey('departments.id'))
    
    total = column_property(
        select([func.sum(AccountAllocator.percent_allocation)]).where(AccountAllocator.account_allocator_plan_id == id)
    )

# AccountAllocator Table
class AccountAllocator(Base):
    __tablename__ = 'account_allocators'
    id = Column(Integer, primary_key=True)
    account_id = Column(Integer, ForeignKey('accounts.id'))
    percent_allocation = Column(DECIMAL, nullable=False)
    
    account_allocator_plan_id = Column(Integer, ForeignKey('account_allocator_plans.id'))
    account = relationship('Account', foreign_keys=[account_id])

# ProjectCharge Table
class ProjectCharge(Base):
    __tablename__ = 'project_charges'
    id = Column(Integer, primary_key=True)
    charge_amount = Column(DECIMAL, nullable=False)
    charge_date = Column(Date, default=datetime.datetime.now)
    
    project_id = Column(Integer, ForeignKey('projects.id'))
    project = relationship('Project', back_populates='project_charges')
    
    account_id = Column(Integer, ForeignKey('accounts.id'))
    account = relationship('Account', foreign_keys=[account_id])

# DeptAllocation Table
class DeptAllocation(Base):
    __tablename__ = 'dept_allocations'
    id = Column(Integer, primary_key=True)
    account_id = Column(Integer, ForeignKey('accounts.id'))
    charge_amount = Column(DECIMAL, nullable=False)
    
# AccountCharge Table
class AccountCharge(Base):
    __tablename__ = 'account_charges'
    id = Column(Integer, primary_key=True)
    charge_amount = Column(DECIMAL, nullable=False)
    account_id = Column(Integer, ForeignKey('accounts.id'))

# Create all tables
Base.metadata.create_all(engine)

# Create a session
Session = sessionmaker(bind=engine)
session = Session()

# Adding test data
emp1 = Employee(name='John Doe', organization_name='Org1')
emp2 = Employee(name='Jane Smith', organization_name='Org2')
session.add_all([emp1, emp2])
session.commit()

dept1 = Department(name='HR', location='New York', managed_by_id=emp1.id)
dept2 = Department(name='Finance', location='Chicago', managed_by_id=emp2.id)
session.add_all([dept1, dept2])
session.commit()

acc1 = Account(name='Acc1', department_id=dept1.id, charge_budget=10000)
acc2 = Account(name='Acc2', department_id=dept2.id, charge_budget=20000)
session.add_all([acc1, acc2])
session.commit()

proj1 = Project(name='Proj1', managed_by_id=emp1.id)
proj2 = Project(name='Proj2', managed_by_id=emp2.id)
session.add_all([proj1, proj2])
session.commit()

proj_plan = ProjectAllocatorPlan(name='Plan1', date=datetime.datetime.now())
session.add(proj_plan)
session.commit()

dept_alloc1 = DeptAllocator(project_allocator_plan_id=proj_plan.id, percent_allocation=50, account_allocator_plan_id=None)
dept_alloc2 = DeptAllocator(project_allocator_plan_id=proj_plan.id, percent_allocation=50, account_allocator_plan_id=None)
session.add_all([dept_alloc1, dept_alloc2])
session.commit()

proj_charge1 = ProjectCharge(charge_amount=1000, charge_date=datetime.datetime.now(), project_id=proj1.id, account_id=acc1.id)
proj_charge2 = ProjectCharge(charge_amount=2000, charge_date=datetime.datetime.now(), project_id=proj2.id, account_id=acc2.id)
session.add_all([proj_charge1, proj_charge2])
session.commit()

print("Tables created and test data added successfully.")

