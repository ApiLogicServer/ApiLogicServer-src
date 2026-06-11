# coding: utf-8
from sqlalchemy import DECIMAL, DateTime  # API Logic Server GenAI assist
from sqlalchemy import Column, Date, Float, ForeignKey, Integer, Numeric, String, Text, text
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

########################################################################################################################
# Classes describing database for SqlAlchemy ORM, initially created by schema introspection.
#
# Alter this file per your database maintenance policy
#    See https://apilogicserver.github.io/Docs/Project-Rebuild/#rebuilding
#
# Created:  June 10, 2026 14:57:34
# Database: sqlite:////Users/val/dev/ApiLogicServer/ApiLogicServer-dev/build_and_test/genai-logic/demo_customs_surtax/database/db.sqlite
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



class CountryOrigin(Base):  # type: ignore
    __tablename__ = 'country_origin'
    _s_collection_name = 'CountryOrigin'  # type: ignore

    id = Column(Integer, primary_key=True)
    country_code = Column(String(2), nullable=False)
    country_name = Column(String(100), nullable=False)
    trade_agreement = Column(String(20))
    surtax_rate = Column(Numeric(8, 6), server_default=text("0"), nullable=False)

    # parent relationships (access parent)

    # child relationships (access children)
    CustomsEntryList : Mapped[List["CustomsEntry"]] = relationship(back_populates="country_origin")



class HsCodeRate(Base):  # type: ignore
    __tablename__ = 'hs_code_rate'
    _s_collection_name = 'HsCodeRate'  # type: ignore

    id = Column(Integer, primary_key=True)
    hs_code = Column(String(10), nullable=False)
    description = Column(String(200))
    base_duty_rate = Column(Numeric(8, 6), server_default=text("0"), nullable=False)
    is_steel_derivative = Column(Integer, server_default=text("1"), nullable=False)

    # parent relationships (access parent)

    # child relationships (access children)
    SurtaxLineItemList : Mapped[List["SurtaxLineItem"]] = relationship(back_populates="hs_code")



class Province(Base):  # type: ignore
    __tablename__ = 'province'
    _s_collection_name = 'Province'  # type: ignore

    id = Column(Integer, primary_key=True)
    province_code = Column(String(2), nullable=False)
    province_name = Column(String(100), nullable=False)
    tax_rate = Column(Numeric(8, 4), server_default=text("0"), nullable=False)

    # parent relationships (access parent)

    # child relationships (access children)
    CustomsEntryList : Mapped[List["CustomsEntry"]] = relationship(back_populates="province")



class SysConfig(Base):  # type: ignore
    __tablename__ = 'sys_config'
    _s_collection_name = 'SysConfig'  # type: ignore

    id = Column(Integer, primary_key=True)
    name = Column(Text, server_default=text("'system'"), nullable=False)
    discount_rate = Column(Float, server_default=text("0.05"))
    tax_rate = Column(Float, server_default=text("0.10"))
    notes = Column(Text)
    pc_number = Column(Text, server_default=text("'2025-0917'"))
    program_code = Column(Text, server_default=text("'25267A'"))
    order_title = Column(Text, server_default=text("'Steel Derivative Goods Surtax Order'"))
    order_date = Column(Date, server_default=text("'2025-12-11'"))
    legal_authority = Column(Text, server_default=text("'Subsection 53(2) and paragraph 79(a) of the Customs Tariff'"))
    effective_date = Column(Date, server_default=text("'2025-12-26'"))

    # parent relationships (access parent)

    # child relationships (access children)
    CustomsEntryList : Mapped[List["CustomsEntry"]] = relationship(back_populates="sys_config")



class CustomsEntry(Base):  # type: ignore
    __tablename__ = 'customs_entry'
    _s_collection_name = 'CustomsEntry'  # type: ignore

    id = Column(Integer, primary_key=True)
    entry_number = Column(String(30), nullable=False)
    importer_name = Column(String(100), nullable=False)
    ship_date = Column(Date, nullable=False)
    country_origin_id = Column(ForeignKey('country_origin.id'), nullable=False)
    province_id = Column(ForeignKey('province.id'), nullable=False)
    sys_config_id = Column(ForeignKey('sys_config.id'), server_default=text("1"), nullable=False)
    effective_date = Column(Date)
    program_code = Column(String(20))
    pc_number = Column(String(20))
    country_surtax_rate = Column(Numeric(8, 6), server_default=text("0"))
    province_tax_rate = Column(Numeric(8, 4), server_default=text("0"))
    surtax_applicable = Column(Integer, server_default=text("0"))
    total_customs_value = Column(Numeric(15, 2), server_default=text("0"))
    total_duty_amount = Column(Numeric(15, 2), server_default=text("0"))
    total_surtax_amount = Column(Numeric(15, 2), server_default=text("0"))
    duty_paid_value = Column(Numeric(15, 2), server_default=text("0"))
    sales_tax_amount = Column(Numeric(15, 2), server_default=text("0"))
    total_tax_due = Column(Numeric(15, 2), server_default=text("0"))
    notes = Column(String(200))

    # parent relationships (access parent)
    country_origin : Mapped["CountryOrigin"] = relationship(back_populates=("CustomsEntryList"))
    province : Mapped["Province"] = relationship(back_populates=("CustomsEntryList"))
    sys_config : Mapped["SysConfig"] = relationship(back_populates=("CustomsEntryList"))

    # child relationships (access children)
    SurtaxLineItemList : Mapped[List["SurtaxLineItem"]] = relationship(back_populates="customs_entry")



class SurtaxLineItem(Base):  # type: ignore
    __tablename__ = 'surtax_line_item'
    _s_collection_name = 'SurtaxLineItem'  # type: ignore

    id = Column(Integer, primary_key=True)
    customs_entry_id = Column(ForeignKey('customs_entry.id'), nullable=False)
    hs_code_id = Column(ForeignKey('hs_code_rate.id'), nullable=False)
    line_number = Column(Integer, server_default=text("1"), nullable=False)
    description = Column(String(200))
    customs_value = Column(Numeric(15, 2), server_default=text("0"), nullable=False)
    base_duty_rate = Column(Numeric(8, 6), server_default=text("0"))
    is_steel_derivative = Column(Integer, server_default=text("1"))
    surtax_applicable = Column(Integer, server_default=text("0"))
    base_duty_amount = Column(Numeric(15, 2), server_default=text("0"))
    surtax_amount = Column(Numeric(15, 2), server_default=text("0"))

    # parent relationships (access parent)
    customs_entry : Mapped["CustomsEntry"] = relationship(back_populates=("SurtaxLineItemList"))
    hs_code : Mapped["HsCodeRate"] = relationship(back_populates=("SurtaxLineItemList"))

    # child relationships (access children)
