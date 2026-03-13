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
# Created:  March 12, 2026 19:52:22
# Database: sqlite:////Users/val/dev/ApiLogicServer/ApiLogicServer-dev/build_and_test/ApiLogicServer/allo_dept_gl2/database/db.sqlite
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



class Contractor(Base):  # type: ignore
    __tablename__ = 'contractor'
    _s_collection_name = 'Contractor'  # type: ignore

    id = Column(Integer, primary_key=True)
    name = Column(Text, nullable=False)
    notes = Column(Text)

    # parent relationships (access parent)

    # child relationships (access children)
    ChargeList : Mapped[List["Charge"]] = relationship(back_populates="contractor")
    SysProjectReqList : Mapped[List["SysProjectReq"]] = relationship(back_populates="contractor")



class Department(Base):  # type: ignore
    __tablename__ = 'department'
    _s_collection_name = 'Department'  # type: ignore

    id = Column(Integer, primary_key=True)
    name = Column(Text, nullable=False)
    notes = Column(Text)

    # parent relationships (access parent)

    # child relationships (access children)
    DeptChargeDefinitionList : Mapped[List["DeptChargeDefinition"]] = relationship(back_populates="department")
    GlAccountList : Mapped[List["GlAccount"]] = relationship(back_populates="department")
    ProjectFundingLineList : Mapped[List["ProjectFundingLine"]] = relationship(back_populates="department")
    ChargeDeptAllocationList : Mapped[List["ChargeDeptAllocation"]] = relationship(back_populates="department")



class ProjectFundingDefinition(Base):  # type: ignore
    __tablename__ = 'project_funding_definition'
    _s_collection_name = 'ProjectFundingDefinition'  # type: ignore

    id = Column(Integer, primary_key=True)
    name = Column(Text, nullable=False)
    total_percent = Column(Numeric(7, 4), server_default=text("0"))
    is_active = Column(Integer, server_default=text("0"))
    notes = Column(Text)

    # parent relationships (access parent)

    # child relationships (access children)
    ProjectList : Mapped[List["Project"]] = relationship(back_populates="project_funding_definition")
    ProjectFundingLineList : Mapped[List["ProjectFundingLine"]] = relationship(back_populates="project_funding_definition")



class SysConfig(Base):  # type: ignore
    __tablename__ = 'sys_config'
    _s_collection_name = 'SysConfig'  # type: ignore

    id = Column(Integer, primary_key=True)
    name = Column(Text, server_default=text("'system'"), nullable=False)
    discount_rate = Column(Float, server_default=text("0.05"))
    tax_rate = Column(Float, server_default=text("0.10"))
    notes = Column(Text)

    # parent relationships (access parent)

    # child relationships (access children)



class DeptChargeDefinition(Base):  # type: ignore
    __tablename__ = 'dept_charge_definition'
    _s_collection_name = 'DeptChargeDefinition'  # type: ignore

    id = Column(Integer, primary_key=True)
    department_id = Column(ForeignKey('department.id'), nullable=False)
    name = Column(Text, nullable=False)
    total_percent = Column(Numeric(7, 4), server_default=text("0"))
    is_active = Column(Integer, server_default=text("0"))
    notes = Column(Text)

    # parent relationships (access parent)
    department : Mapped["Department"] = relationship(back_populates=("DeptChargeDefinitionList"))

    # child relationships (access children)
    DeptChargeDefinitionLineList : Mapped[List["DeptChargeDefinitionLine"]] = relationship(back_populates="dept_charge_definition")
    ProjectFundingLineList : Mapped[List["ProjectFundingLine"]] = relationship(back_populates="dept_charge_definition")
    ChargeDeptAllocationList : Mapped[List["ChargeDeptAllocation"]] = relationship(back_populates="dept_charge_definition")



class GlAccount(Base):  # type: ignore
    __tablename__ = 'gl_account'
    _s_collection_name = 'GlAccount'  # type: ignore

    id = Column(Integer, primary_key=True)
    department_id = Column(ForeignKey('department.id'), nullable=False)
    account_number = Column(Text, nullable=False)
    name = Column(Text, nullable=False)
    total_allocated = Column(Numeric(15, 2), server_default=text("0"))
    notes = Column(Text)

    # parent relationships (access parent)
    department : Mapped["Department"] = relationship(back_populates=("GlAccountList"))

    # child relationships (access children)
    DeptChargeDefinitionLineList : Mapped[List["DeptChargeDefinitionLine"]] = relationship(back_populates="gl_account")
    ChargeGlAllocationList : Mapped[List["ChargeGlAllocation"]] = relationship(back_populates="gl_account")



class Project(Base):  # type: ignore
    __tablename__ = 'project'
    _s_collection_name = 'Project'  # type: ignore

    id = Column(Integer, primary_key=True)
    name = Column(Text, nullable=False)
    project_funding_definition_id = Column(ForeignKey('project_funding_definition.id'))
    total_charges = Column(Numeric(15, 2), server_default=text("0"))
    notes = Column(Text)

    # parent relationships (access parent)
    project_funding_definition : Mapped["ProjectFundingDefinition"] = relationship(back_populates=("ProjectList"))

    # child relationships (access children)
    ChargeList : Mapped[List["Charge"]] = relationship(back_populates="project")
    SysProjectReqList : Mapped[List["SysProjectReq"]] = relationship(back_populates="matched_project")



class Charge(Base):  # type: ignore
    __tablename__ = 'charge'
    _s_collection_name = 'Charge'  # type: ignore

    id = Column(Integer, primary_key=True)
    project_id = Column(ForeignKey('project.id'))
    contractor_id = Column(ForeignKey('contractor.id'))
    project_description = Column(Text)
    amount = Column(Numeric(15, 2), server_default=text("0"), nullable=False)
    total_distributed_amount = Column(Numeric(15, 2), server_default=text("0"))
    description = Column(Text)
    charge_date = Column(Text)

    # parent relationships (access parent)
    contractor : Mapped["Contractor"] = relationship(back_populates=("ChargeList"))
    project : Mapped["Project"] = relationship(back_populates=("ChargeList"))

    # child relationships (access children)
    ChargeDeptAllocationList : Mapped[List["ChargeDeptAllocation"]] = relationship(back_populates="charge")



class DeptChargeDefinitionLine(Base):  # type: ignore
    __tablename__ = 'dept_charge_definition_line'
    _s_collection_name = 'DeptChargeDefinitionLine'  # type: ignore

    id = Column(Integer, primary_key=True)
    dept_charge_definition_id = Column(ForeignKey('dept_charge_definition.id'), nullable=False)
    gl_account_id = Column(ForeignKey('gl_account.id'), nullable=False)
    percent = Column(Numeric(7, 4), server_default=text("0"), nullable=False)
    notes = Column(Text)

    # parent relationships (access parent)
    dept_charge_definition : Mapped["DeptChargeDefinition"] = relationship(back_populates=("DeptChargeDefinitionLineList"))
    gl_account : Mapped["GlAccount"] = relationship(back_populates=("DeptChargeDefinitionLineList"))

    # child relationships (access children)
    ChargeGlAllocationList : Mapped[List["ChargeGlAllocation"]] = relationship(back_populates="dept_charge_definition_line")



class ProjectFundingLine(Base):  # type: ignore
    __tablename__ = 'project_funding_line'
    _s_collection_name = 'ProjectFundingLine'  # type: ignore

    id = Column(Integer, primary_key=True)
    project_funding_definition_id = Column(ForeignKey('project_funding_definition.id'), nullable=False)
    department_id = Column(ForeignKey('department.id'), nullable=False)
    dept_charge_definition_id = Column(ForeignKey('dept_charge_definition.id'), nullable=False)
    percent = Column(Numeric(7, 4), server_default=text("0"), nullable=False)
    notes = Column(Text)

    # parent relationships (access parent)
    department : Mapped["Department"] = relationship(back_populates=("ProjectFundingLineList"))
    dept_charge_definition : Mapped["DeptChargeDefinition"] = relationship(back_populates=("ProjectFundingLineList"))
    project_funding_definition : Mapped["ProjectFundingDefinition"] = relationship(back_populates=("ProjectFundingLineList"))

    # child relationships (access children)
    ChargeDeptAllocationList : Mapped[List["ChargeDeptAllocation"]] = relationship(back_populates="project_funding_line")



class SysProjectReq(Base):  # type: ignore
    __tablename__ = 'sys_project_req'
    _s_collection_name = 'SysProjectReq'  # type: ignore

    id = Column(Integer, primary_key=True)
    contractor_id = Column(ForeignKey('contractor.id'))
    project_description = Column(Text)
    matched_project_id = Column(ForeignKey('project.id'))
    confidence = Column(Float)
    reason = Column(Text)
    request = Column(Text)
    created_on = Column(Text)

    # parent relationships (access parent)
    contractor : Mapped["Contractor"] = relationship(back_populates=("SysProjectReqList"))
    matched_project : Mapped["Project"] = relationship(back_populates=("SysProjectReqList"))

    # child relationships (access children)



class ChargeDeptAllocation(Base):  # type: ignore
    __tablename__ = 'charge_dept_allocation'
    _s_collection_name = 'ChargeDeptAllocation'  # type: ignore

    id = Column(Integer, primary_key=True)
    charge_id = Column(ForeignKey('charge.id'), nullable=False)
    project_funding_line_id = Column(ForeignKey('project_funding_line.id'), nullable=False)
    department_id = Column(ForeignKey('department.id'))
    dept_charge_definition_id = Column(ForeignKey('dept_charge_definition.id'))
    percent = Column(Numeric(7, 4), server_default=text("0"))
    amount = Column(Numeric(15, 2), server_default=text("0"))

    # parent relationships (access parent)
    charge : Mapped["Charge"] = relationship(back_populates=("ChargeDeptAllocationList"))
    department : Mapped["Department"] = relationship(back_populates=("ChargeDeptAllocationList"))
    dept_charge_definition : Mapped["DeptChargeDefinition"] = relationship(back_populates=("ChargeDeptAllocationList"))
    project_funding_line : Mapped["ProjectFundingLine"] = relationship(back_populates=("ChargeDeptAllocationList"))

    # child relationships (access children)
    ChargeGlAllocationList : Mapped[List["ChargeGlAllocation"]] = relationship(back_populates="charge_dept_allocation")



class ChargeGlAllocation(Base):  # type: ignore
    __tablename__ = 'charge_gl_allocation'
    _s_collection_name = 'ChargeGlAllocation'  # type: ignore

    id = Column(Integer, primary_key=True)
    charge_dept_allocation_id = Column(ForeignKey('charge_dept_allocation.id'), nullable=False)
    dept_charge_definition_line_id = Column(ForeignKey('dept_charge_definition_line.id'), nullable=False)
    gl_account_id = Column(ForeignKey('gl_account.id'))
    percent = Column(Numeric(7, 4), server_default=text("0"))
    amount = Column(Numeric(15, 2), server_default=text("0"))

    # parent relationships (access parent)
    charge_dept_allocation : Mapped["ChargeDeptAllocation"] = relationship(back_populates=("ChargeGlAllocationList"))
    dept_charge_definition_line : Mapped["DeptChargeDefinitionLine"] = relationship(back_populates=("ChargeGlAllocationList"))
    gl_account : Mapped["GlAccount"] = relationship(back_populates=("ChargeGlAllocationList"))

    # child relationships (access children)
