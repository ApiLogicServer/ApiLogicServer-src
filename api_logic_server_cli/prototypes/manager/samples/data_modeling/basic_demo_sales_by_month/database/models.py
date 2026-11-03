# coding: utf-8
from sqlalchemy import DECIMAL, DateTime  # API Logic Server GenAI assist
from sqlalchemy import Column, Float, ForeignKey, ForeignKeyConstraint, Integer, Text, text
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

########################################################################################################################
# Classes describing database for SqlAlchemy ORM, initially created by schema introspection.
#
# Alter this file per your database maintenance policy
#    See https://apilogicserver.github.io/Docs/Project-Rebuild/#rebuilding
#
# Created:  September 10, 2026 07:21:02
# Database: sqlite:////Users/val/dev/ApiLogicServer/ApiLogicServer-dev/build_and_test/genai-logic/basic_demo_sales_by_month/database/db.sqlite
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



class Customer(Base):  # type: ignore
    __tablename__ = 'customer'
    _s_collection_name = 'Customer'  # type: ignore

    id = Column(Integer, primary_key=True)
    name = Column(Text)
    balance = Column(Float, server_default=text("0"))
    credit_limit = Column(Float, server_default=text("1000"))

    # parent relationships (access parent)

    # child relationships (access children)
    OrderList : Mapped[List["Order"]] = relationship(back_populates="customer")



class Product(Base):  # type: ignore
    __tablename__ = 'product'
    _s_collection_name = 'Product'  # type: ignore

    id = Column(Integer, primary_key=True)
    name = Column(Text)
    unit_price = Column(Float, server_default=text("0"))

    # parent relationships (access parent)

    # child relationships (access children)
    ItemList : Mapped[List["Item"]] = relationship(back_populates="product")



class SalesRep(Base):  # type: ignore
    __tablename__ = 'sales_rep'
    _s_collection_name = 'SalesRep'  # type: ignore

    id = Column(Integer, primary_key=True)
    name = Column(Text)

    # parent relationships (access parent)

    # child relationships (access children)
    SalesRepTotalList : Mapped[List["SalesRepTotal"]] = relationship(back_populates="sales_rep")



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



class SalesRepTotal(Base):  # type: ignore
    __tablename__ = 'sales_rep_totals'
    _s_collection_name = 'SalesRepTotal'  # type: ignore

    sales_rep_id = Column(ForeignKey('sales_rep.id'), primary_key=True)
    year_month = Column(Text, primary_key=True)
    total_amount = Column(Float, server_default=text("0"))
    order_count = Column(Integer, server_default=text("0"))
    allow_client_generated_ids = True

    # parent relationships (access parent)
    sales_rep : Mapped["SalesRep"] = relationship(back_populates=("SalesRepTotalList"))

    # child relationships (access children)
    OrderList : Mapped[List["Order"]] = relationship(back_populates="sales_rep_total")



class Order(Base):  # type: ignore
    __tablename__ = 'order'
    _s_collection_name = 'Order'  # type: ignore
    __table_args__ = (
        ForeignKeyConstraint(['sales_rep_id', 'CreatedOnYearMonth'], ['sales_rep_totals.sales_rep_id', 'sales_rep_totals.year_month']),
    )

    id = Column(Integer, primary_key=True)
    customer_id = Column(ForeignKey('customer.id'))
    sales_rep_id = Column(Integer)
    CreatedOnYearMonth = Column(Text)
    notes = Column(Text)
    CreatedOn = Column(Text)
    amount_total = Column(Float, server_default=text("0"))
    date_shipped = Column(Text)

    # parent relationships (access parent)
    customer : Mapped["Customer"] = relationship(back_populates=("OrderList"))
    sales_rep_total : Mapped["SalesRepTotal"] = relationship(back_populates=("OrderList"))

    # child relationships (access children)
    ItemList : Mapped[List["Item"]] = relationship(back_populates="order")



class Item(Base):  # type: ignore
    __tablename__ = 'item'
    _s_collection_name = 'Item'  # type: ignore

    id = Column(Integer, primary_key=True)
    order_id = Column(ForeignKey('order.id'))
    product_id = Column(ForeignKey('product.id'))
    quantity = Column(Integer, server_default=text("1"))
    unit_price = Column(Float, server_default=text("0"))
    amount = Column(Float, server_default=text("0"))

    # parent relationships (access parent)
    order : Mapped["Order"] = relationship(back_populates=("ItemList"))
    product : Mapped["Product"] = relationship(back_populates=("ItemList"))

    # child relationships (access children)
