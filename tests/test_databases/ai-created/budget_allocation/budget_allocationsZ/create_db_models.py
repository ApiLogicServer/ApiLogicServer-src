import decimal

from sqlalchemy.sql import func  # end imports from system/genai/create_db_models_inserts/create_db_models_prefix.py
from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, DateTime, DECIMAL
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime

# Setup the SQLite database
engine = create_engine('sqlite:///system/genai/temp/create_db_models.sqlite')
Base = declarative_base()

# Define the models
class DepartmentAccount(Base):
    __tablename__ = 'department_accounts'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=True)
    budget_amount = Column(DECIMAL, nullable=True)

class DepartmentCharge(Base):
    __tablename__ = 'department_charges'

    id = Column(Integer, primary_key=True, autoincrement=True)
    department_account_id = Column(Integer, ForeignKey('department_accounts.id'), nullable=True)
    amount = Column(DECIMAL, nullable=True)
    date = Column(DateTime, default=datetime.utcnow)

class DepartmentAllocationPlan(Base):
    __tablename__ = 'department_allocation_plans'

    id = Column(Integer, primary_key=True, autoincrement=True)
    allocation_percent = Column(DECIMAL, nullable=True)
    department_account_id = Column(Integer, ForeignKey('department_accounts.id'), nullable=True)

class ProjectAllocationPlan(Base):
    __tablename__ = 'project_allocation_plans'

    id = Column(Integer, primary_key=True, autoincrement=True)
    allocation_percent = Column(DECIMAL, nullable=True)
    department_allocation_plan_id = Column(Integer, ForeignKey('department_allocation_plans.id'), nullable=True)

class Project(Base):
    __tablename__ = 'projects'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=True)
    approved = Column(Integer, nullable=True)  # Use 1 for True and 0 for False
    allocation_plan_id = Column(Integer, ForeignKey('project_allocation_plans.id'), nullable=True)


# Create all tables
Base.metadata.create_all(engine)

# Set up the session
Session = sessionmaker(bind=engine)
session = Session()

# Create some test data
dept_account1 = DepartmentAccount(name="HR", budget_amount=100000)
dept_account2 = DepartmentAccount(name="IT", budget_amount=200000)

session.add(dept_account1)
session.add(dept_account2)
session.commit()

dept_charge1 = DepartmentCharge(department_account_id=dept_account1.id, amount=5000)
dept_charge2 = DepartmentCharge(department_account_id=dept_account2.id, amount=10000)

session.add(dept_charge1)
session.add(dept_charge2)
session.commit()

dept_alloc_plan1 = DepartmentAllocationPlan(department_account_id=dept_account1.id, allocation_percent=50)
dept_alloc_plan2 = DepartmentAllocationPlan(department_account_id=dept_account2.id, allocation_percent=50)

session.add(dept_alloc_plan1)
session.add(dept_alloc_plan2)
session.commit()

proj_alloc_plan1 = ProjectAllocationPlan(department_allocation_plan_id=dept_alloc_plan1.id, allocation_percent=60)
proj_alloc_plan2 = ProjectAllocationPlan(department_allocation_plan_id=dept_alloc_plan2.id, allocation_percent=40)

session.add(proj_alloc_plan1)
session.add(proj_alloc_plan2)
session.commit()

project1 = Project(name="Project A", approved=1, allocation_plan_id=proj_alloc_plan1.id)
project2 = Project(name="Project B", approved=0, allocation_plan_id=proj_alloc_plan2.id)

session.add(project1)
session.add(project2)
session.commit()

# Clean up the session
session.close()

print("Database created and populated with test data.")
