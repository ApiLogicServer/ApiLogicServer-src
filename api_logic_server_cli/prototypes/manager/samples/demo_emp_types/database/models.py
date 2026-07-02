# coding: utf-8
from sqlalchemy import DECIMAL, DateTime  # API Logic Server GenAI assist
from sqlalchemy import Column, Float, ForeignKey, Integer, Numeric, Text, text
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

########################################################################################################################
# Classes describing database for SqlAlchemy ORM, initially created by schema introspection.
#
# Alter this file per your database maintenance policy
#    See https://apilogicserver.github.io/Docs/Project-Rebuild/#rebuilding
#
# Created:  July 01, 2026 18:16:53
# Database: sqlite:////Users/val/dev/ApiLogicServer/ApiLogicServer-dev/build_and_test/genai-logic/demo_emp_types/database/db.sqlite
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



class Department(Base):  # type: ignore
    __tablename__ = 'department'
    _s_collection_name = 'Department'  # type: ignore

    id = Column(Integer, primary_key=True)
    name = Column(Text, nullable=False)
    budget = Column(Numeric(15, 2), nullable=False)
    total_salary = Column(Numeric(15, 2), server_default=text("0"))

    # parent relationships (access parent)

    # child relationships (access children)
    EmployeeList : Mapped[List["Employee"]] = relationship(back_populates="dept")



class LaborUnion(Base):  # type: ignore
    __tablename__ = 'labor_union'
    _s_collection_name = 'LaborUnion'  # type: ignore

    id = Column(Integer, primary_key=True)
    name = Column(Text, nullable=False)
    dues_rate = Column(Float, nullable=False)

    # parent relationships (access parent)

    # child relationships (access children)
    EmployeeList : Mapped[List["Employee"]] = relationship(back_populates="union")



class SysConfig(Base):  # type: ignore
    __tablename__ = 'sys_config'
    _s_collection_name = 'SysConfig'  # type: ignore

    id = Column(Integer, primary_key=True)
    name = Column(Text, server_default=text("'system'"), nullable=False)
    discount_rate = Column(Float, server_default=text("0.05"))
    tax_rate = Column(Float, server_default=text("0.10"))
    notes = Column(Text)
    max_hourly_weekly_salary = Column(Numeric(15, 2), server_default=text("5000.0"))
    military_stipend_rate_per_year = Column(Float, server_default=text("100.0"))

    # parent relationships (access parent)

    # child relationships (access children)
    EmployeeList : Mapped[List["Employee"]] = relationship(back_populates="sys_config")



class Employee(Base):  # type: ignore
    __tablename__ = 'employee'
    _s_collection_name = 'Employee'  # type: ignore

    id = Column(Integer, primary_key=True)
    type = Column(Text, nullable=False)
    name = Column(Text, nullable=False)
    dept_id = Column(ForeignKey('department.id'), nullable=False)
    sys_config_id = Column(ForeignKey('sys_config.id'), server_default=text("1"))
    max_hourly_weekly_salary = Column(Numeric(15, 2))
    military_stipend_rate_per_year = Column(Float)
    salary = Column(Numeric(15, 2), server_default=text("0"))
    hours_worked = Column(Float)
    hourly_rate = Column(Float)
    union_id = Column(ForeignKey('labor_union.id'))
    union_dues = Column(Numeric(15, 2), server_default=text("0"))
    base_salary = Column(Numeric(15, 2))
    commission_total = Column(Numeric(15, 2), server_default=text("0"))
    military = Column(Text, server_default=text("'no'"), nullable=False)
    branch = Column(Text)
    rank = Column(Text)
    service_years = Column(Integer)
    military_stipend = Column(Float, server_default=text("0"))
    total_compensation = Column(Numeric(15, 2), server_default=text("0"))

    # parent relationships (access parent)
    dept : Mapped["Department"] = relationship(back_populates=("EmployeeList"))
    sys_config : Mapped["SysConfig"] = relationship(back_populates=("EmployeeList"))
    union : Mapped["LaborUnion"] = relationship(back_populates=("EmployeeList"))

    # child relationships (access children)
    CommissionOrderList : Mapped[List["CommissionOrder"]] = relationship(back_populates="employee")



class CommissionOrder(Base):  # type: ignore
    __tablename__ = 'commission_order'
    _s_collection_name = 'CommissionOrder'  # type: ignore

    id = Column(Integer, primary_key=True)
    employee_id = Column(ForeignKey('employee.id'), nullable=False)
    amount = Column(Numeric(15, 2), nullable=False)
    customer_name = Column(Text, nullable=False)

    # parent relationships (access parent)
    employee : Mapped["Employee"] = relationship(back_populates=("CommissionOrderList"))

    # child relationships (access children)
