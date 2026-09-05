# coding: utf-8
from sqlalchemy import DECIMAL, DateTime  # API Logic Server GenAI assist
from sqlalchemy import Column, Float, ForeignKey, Integer, Text, text
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

########################################################################################################################
# Classes describing database for SqlAlchemy ORM, initially created by schema introspection.
#
# Alter this file per your database maintenance policy
#    See https://apilogicserver.github.io/Docs/Project-Rebuild/#rebuilding
#
# Created:  September 03, 2026 18:55:00
# Database: sqlite:////Users/val/dev/genai-logic/ApiLogicServer-dev/build_and_test/genai-logic/library_rfi/database/db.sqlite
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



class Book(Base):  # type: ignore
    __tablename__ = 'book'
    _s_collection_name = 'Book'  # type: ignore

    id = Column(Integer, primary_key=True)
    title = Column(Text, nullable=False)
    author = Column(Text)
    active_loan_count = Column(Integer, server_default=text("0"))
    hold_count = Column(Integer, server_default=text("0"))
    available = Column(Integer, server_default=text("1"))

    # parent relationships (access parent)

    # child relationships (access children)
    HoldList : Mapped[List["Hold"]] = relationship(back_populates="book")
    LoanList : Mapped[List["Loan"]] = relationship(back_populates="book")



class SysConfig(Base):  # type: ignore
    __tablename__ = 'sys_config'
    _s_collection_name = 'SysConfig'  # type: ignore

    id = Column(Integer, primary_key=True)
    name = Column(Text, server_default=text("'system'"), nullable=False)
    discount_rate = Column(Float, server_default=text("0.05"))
    tax_rate = Column(Float, server_default=text("0.10"))
    notes = Column(Text)
    fine_rate_per_day = Column(Float, server_default=text("0.25"))
    fine_cap_per_book = Column(Float, server_default=text("10.0"))
    fine_block_threshold = Column(Float, server_default=text("5.0"))
    loan_period_days = Column(Integer, server_default=text("21"))

    # parent relationships (access parent)

    # child relationships (access children)
    MemberList : Mapped[List["Member"]] = relationship(back_populates="sys_config")
    LoanList : Mapped[List["Loan"]] = relationship(back_populates="sys_config")



class Member(Base):  # type: ignore
    __tablename__ = 'member'
    _s_collection_name = 'Member'  # type: ignore

    id = Column(Integer, primary_key=True)
    name = Column(Text, nullable=False)
    email = Column(Text)
    sys_config_id = Column(ForeignKey('sys_config.id'), server_default=text("1"))
    fine_block_threshold = Column(Float, server_default=text("0"))
    fine_balance = Column(Float, server_default=text("0"))
    blocked = Column(Integer, server_default=text("0"))

    # parent relationships (access parent)
    sys_config : Mapped["SysConfig"] = relationship(back_populates=("MemberList"))

    # child relationships (access children)
    HoldList : Mapped[List["Hold"]] = relationship(back_populates="member")
    LoanList : Mapped[List["Loan"]] = relationship(back_populates="member")



class Hold(Base):  # type: ignore
    __tablename__ = 'hold'
    _s_collection_name = 'Hold'  # type: ignore

    id = Column(Integer, primary_key=True)
    member_id = Column(ForeignKey('member.id'), nullable=False)
    book_id = Column(ForeignKey('book.id'), nullable=False)
    requested_date = Column(Text, nullable=False)
    status = Column(Text, server_default=text("'waiting'"))

    # parent relationships (access parent)
    book : Mapped["Book"] = relationship(back_populates=("HoldList"))
    member : Mapped["Member"] = relationship(back_populates=("HoldList"))

    # child relationships (access children)



class Loan(Base):  # type: ignore
    __tablename__ = 'loan'
    _s_collection_name = 'Loan'  # type: ignore

    id = Column(Integer, primary_key=True)
    member_id = Column(ForeignKey('member.id'), nullable=False)
    book_id = Column(ForeignKey('book.id'), nullable=False)
    checkout_date = Column(Text, nullable=False)
    due_date = Column(Text)
    return_date = Column(Text)
    renewed = Column(Integer, server_default=text("0"))
    sys_config_id = Column(ForeignKey('sys_config.id'), server_default=text("1"))
    fine_rate_per_day = Column(Float, server_default=text("0"))
    fine_cap_per_book = Column(Float, server_default=text("0"))
    loan_period_days = Column(Integer, server_default=text("0"))
    fine_amount = Column(Float, server_default=text("0"))
    fine_paid = Column(Float, server_default=text("0"))
    fine_balance = Column(Float, server_default=text("0"))

    # parent relationships (access parent)
    book : Mapped["Book"] = relationship(back_populates=("LoanList"))
    member : Mapped["Member"] = relationship(back_populates=("LoanList"))
    sys_config : Mapped["SysConfig"] = relationship(back_populates=("LoanList"))

    # child relationships (access children)
