# coding: utf-8
from sqlalchemy import DECIMAL, DateTime  # API Logic Server GenAI assist
from sqlalchemy import Boolean, Column, DECIMAL, Date, DateTime, ForeignKey, Integer, Numeric, String, Text, text
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

########################################################################################################################
# Classes describing database for SqlAlchemy ORM, initially created by schema introspection.
#
# Alter this file per your database maintenance policy
#    See https://apilogicserver.github.io/Docs/Project-Rebuild/#rebuilding
#
# Created:  November 19, 2026 18:51:34
# Database: sqlite:////Users/val/dev/genai-logic/ApiLogicServer-dev/build_and_test/genai-logic/demo_eai/database/db.sqlite
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
    name = Column(String)
    balance : DECIMAL = Column(DECIMAL)
    credit_limit : DECIMAL = Column(DECIMAL)
    email = Column(String)
    email_opt_out = Column(Boolean)

    # parent relationships (access parent)

    # child relationships (access children)
    OrderList : Mapped[List["Order"]] = relationship(back_populates="customer")



class DailyFlow(Base):  # type: ignore
    __tablename__ = 'daily_flow'
    _s_collection_name = 'DailyFlow'  # type: ignore

    day = Column(Text, primary_key=True)
    order_count = Column(Integer, server_default=text("0"))
    order_amount = Column(Numeric(15, 2), server_default=text("0"))
    message_received = Column(Integer, server_default=text("0"))
    message_processed = Column(Integer, server_default=text("0"))
    message_rejected = Column(Integer, server_default=text("0"))
    message_pending = Column(Integer, server_default=text("0"))
    request_received = Column(Integer, server_default=text("0"))
    request_processed = Column(Integer, server_default=text("0"))
    request_rejected = Column(Integer, server_default=text("0"))
    request_pending = Column(Integer, server_default=text("0"))
    allow_client_generated_ids = True

    # parent relationships (access parent)

    # child relationships (access children)
    OrderList : Mapped[List["Order"]] = relationship(back_populates="daily_flow")
    OrderB2bMessageList : Mapped[List["OrderB2bMessage"]] = relationship(back_populates="daily_flow")
    OrderB2bRequestList : Mapped[List["OrderB2bRequest"]] = relationship(back_populates="daily_flow")



class Product(Base):  # type: ignore
    __tablename__ = 'product'
    _s_collection_name = 'Product'  # type: ignore

    id = Column(Integer, primary_key=True)
    name = Column(String)
    count_suppliers = Column(Integer)
    unit_price : DECIMAL = Column(DECIMAL)

    # parent relationships (access parent)

    # child relationships (access children)
    ProductSupplierList : Mapped[List["ProductSupplier"]] = relationship(back_populates="product")
    ItemList : Mapped[List["Item"]] = relationship(back_populates="product")



class Supplier(Base):  # type: ignore
    __tablename__ = 'supplier'
    _s_collection_name = 'Supplier'  # type: ignore

    id = Column(Integer, primary_key=True)
    name = Column(String)
    contact_name = Column(String)
    phone = Column(String)
    email = Column(String)
    region = Column(String)

    # parent relationships (access parent)

    # child relationships (access children)
    ProductSupplierList : Mapped[List["ProductSupplier"]] = relationship(back_populates="supplier")



class Order(Base):  # type: ignore
    __tablename__ = 'order'
    _s_collection_name = 'Order'  # type: ignore

    id = Column(Integer, primary_key=True)
    notes = Column(String)
    customer_id = Column(ForeignKey('customer.id'), nullable=False)
    CreatedOn = Column(Date)
    date_shipped = Column(Date)
    amount_total : DECIMAL = Column(DECIMAL)
    CreatedOnDay = Column(ForeignKey('daily_flow.day'))

    # parent relationships (access parent)
    daily_flow : Mapped["DailyFlow"] = relationship(back_populates=("OrderList"))
    customer : Mapped["Customer"] = relationship(back_populates=("OrderList"))

    # child relationships (access children)
    ItemList : Mapped[List["Item"]] = relationship(back_populates="order")



class OrderB2bMessage(Base):  # type: ignore
    __tablename__ = 'order_b2b_message'
    _s_collection_name = 'OrderB2bMessage'  # type: ignore

    id = Column(Integer, primary_key=True)
    CreatedOn = Column(DateTime)
    CreatedOnDay = Column(ForeignKey('daily_flow.day'))
    payload = Column(Text, nullable=False)
    is_processed = Column(Boolean, default=False)
    error_text = Column(Text)

    # parent relationships (access parent)
    daily_flow : Mapped["DailyFlow"] = relationship(back_populates=("OrderB2bMessageList"))

    # child relationships (access children)



class OrderB2bRequest(Base):  # type: ignore
    __tablename__ = 'order_b2b_request'
    _s_collection_name = 'OrderB2bRequest'  # type: ignore

    id = Column(Integer, primary_key=True)
    CreatedOn = Column(DateTime)
    CreatedOnDay = Column(ForeignKey('daily_flow.day'))
    payload = Column(Text)
    is_processed = Column(Boolean, default=False)
    error_text = Column(Text)

    # parent relationships (access parent)
    daily_flow : Mapped["DailyFlow"] = relationship(back_populates=("OrderB2bRequestList"))

    # child relationships (access children)



class ProductSupplier(Base):  # type: ignore
    __tablename__ = 'product_supplier'
    _s_collection_name = 'ProductSupplier'  # type: ignore

    id = Column(Integer, primary_key=True)
    product_id = Column(ForeignKey('product.id'))
    supplier_id = Column(ForeignKey('supplier.id'))
    supplier_part_number = Column(String)
    unit_cost : DECIMAL = Column(DECIMAL)
    lead_time_days = Column(Integer)

    # parent relationships (access parent)
    product : Mapped["Product"] = relationship(back_populates=("ProductSupplierList"))
    supplier : Mapped["Supplier"] = relationship(back_populates=("ProductSupplierList"))

    # child relationships (access children)



class Item(Base):  # type: ignore
    __tablename__ = 'item'
    _s_collection_name = 'Item'  # type: ignore

    id = Column(Integer, primary_key=True)
    order_id = Column(ForeignKey('order.id'))
    product_id = Column(ForeignKey('product.id'), nullable=False)
    quantity = Column(Integer, nullable=False)
    amount : DECIMAL = Column(DECIMAL)
    unit_price : DECIMAL = Column(DECIMAL)

    # parent relationships (access parent)
    order : Mapped["Order"] = relationship(back_populates=("ItemList"))
    product : Mapped["Product"] = relationship(back_populates=("ItemList"))

    # child relationships (access children)
