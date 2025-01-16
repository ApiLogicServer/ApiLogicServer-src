# coding: utf-8
from sqlalchemy import Boolean, Column, DECIMAL, DateTime, ForeignKey, Integer, Text, text
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

########################################################################################################################
# Classes describing database for SqlAlchemy ORM, initially created by schema introspection.
#
# Alter this file per your database maintenance policy
#    See https://apilogicserver.github.io/Docs/Project-Rebuild/#rebuilding
#
# Created:  May 03, 2024 22:23:08
# Database: sqlite:////Users/val/dev/ApiLogicServer/ApiLogicServer-dev/clean/ApiLogicServer/genai_demo/database/db.sqlite
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


class Customer(Base):
    __tablename__ = 'Customers'
    _s_collection_name = 'Customer'  # type: ignore

    CustomerID = Column(Integer, primary_key=True)
    CustomerName = Column(Text, nullable=False)
    Address = Column(Text)
    Phone = Column(Text)
    Balance : DECIMAL = Column(DECIMAL(10, 2))
    CreditLimit : DECIMAL = Column(DECIMAL(10, 2), nullable=False)

    # parent relationships (access parent)

    # child relationships (access children)
    OrderList : Mapped[List["Order"]] = relationship(back_populates="Customer")


class Product(Base):
    __tablename__ = 'Products'
    _s_collection_name = 'Product'  # type: ignore

    ProductID = Column(Integer, primary_key=True)
    ProductName = Column(Text, nullable=False)
    UnitPrice : DECIMAL = Column(DECIMAL(10, 2), nullable=False)
    CarbonNeutral = Column(Boolean)

    # parent relationships (access parent)

    # child relationships (access children)
    ItemList : Mapped[List["Item"]] = relationship(back_populates="Product")



class Order(Base):
    __tablename__ = 'Orders'
    _s_collection_name = 'Order'  # type: ignore

    OrderID = Column(Integer, primary_key=True)
    CustomerID = Column(ForeignKey('Customers.CustomerID'))
    OrderDate = Column(DateTime, server_default=text("CURRENT_TIMESTAMP"))
    Notes = Column(Text)
    ShipDate = Column(DateTime)
    AmountTotal : DECIMAL = Column(DECIMAL(10, 2))

    # parent relationships (access parent)
    Customer : Mapped["Customer"] = relationship(back_populates=("OrderList"))

    # child relationships (access children)
    ItemList : Mapped[List["Item"]] = relationship(back_populates="Order")



class Item(Base):
    __tablename__ = 'Items'
    _s_collection_name = 'Item'  # type: ignore

    ItemID = Column(Integer, primary_key=True)
    OrderID = Column(ForeignKey('Orders.OrderID'))
    ProductID = Column(ForeignKey('Products.ProductID'))
    Quantity = Column(Integer, nullable=False)
    UnitPrice : DECIMAL = Column(DECIMAL(10, 2))
    Amount : DECIMAL = Column(DECIMAL(10, 2))

    # parent relationships (access parent)
    Order : Mapped["Order"] = relationship(back_populates=("ItemList"))
    Product : Mapped["Product"] = relationship(back_populates=("ItemList"))

    # child relationships (access children)

