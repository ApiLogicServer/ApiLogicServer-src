# coding: utf-8
from sqlalchemy import DECIMAL, DateTime  # API Logic Server GenAI assist
from sqlalchemy import Boolean, Column, DECIMAL, Date, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
import datetime

########################################################################################################################
# Classes describing database for SqlAlchemy ORM, initially created by schema introspection.
#
# Alter this file per your database maintenance policy
#    See https://apilogicserver.github.io/Docs/Project-Rebuild/#rebuilding
#
# Created:  February 05, 2026 17:04:34
# Database: sqlite:////Users/val/dev/ApiLogicServer/ApiLogicServer-dev/build_and_test/ApiLogicServer/basic_demo_agentic/database/db.sqlite
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
    SysSupplierReqList : Mapped[List["SysSupplierReq"]] = relationship(back_populates="product")



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

    # parent relationships (access parent)
    customer : Mapped["Customer"] = relationship(back_populates=("OrderList"))

    # child relationships (access children)
    ItemList : Mapped[List["Item"]] = relationship(back_populates="order")



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
    SysSupplierReqList : Mapped[List["SysSupplierReq"]] = relationship(back_populates="item")



class SysSupplierReq(Base):  # type: ignore
    """AI-driven supplier selection audit table"""
    __tablename__ = 'sys_supplier_req'
    _s_collection_name = 'SysSupplierReq'  # type: ignore
    
    # Standard AI Audit
    id = Column(Integer, primary_key=True)
    request = Column(String(2000))           # Full AI prompt
    reason = Column(String(500))             # AI explanation
    created_on = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
    fallback_used = Column(Boolean, default=False)
    
    # Parent Context Links (FKs to triggering entities)
    item_id = Column(Integer, ForeignKey("item.id"), index=True, nullable=True)
    product_id = Column(Integer, ForeignKey("product.id"), index=True, nullable=False)
    
    # AI Results (values selected by AI)
    chosen_supplier_id = Column(Integer, ForeignKey("supplier.id"))
    chosen_unit_price : DECIMAL = Column(DECIMAL)
    
    # Relationships (bidirectional for parent context, unidirectional for chosen_supplier)
    item : Mapped["Item"] = relationship(back_populates="SysSupplierReqList")
    product : Mapped["Product"] = relationship(back_populates="SysSupplierReqList")
    chosen_supplier : Mapped["Supplier"] = relationship()

    # parent relationships (access parent)

    # child relationships (access children)
