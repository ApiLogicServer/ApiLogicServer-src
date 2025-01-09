# using resolved_model self.resolved_model FIXME
# created from response, to create create_db_models.sqlite, with test data
#    that is used to create project
# should run without error in manager 
#    if not, check for decimal, indent, or import issues

import decimal
import logging
import sqlalchemy
from sqlalchemy.sql import func 
from logic_bank.logic_bank import Rule
from sqlalchemy import create_engine, Column, Integer, String, Float, ForeignKey, Date, DateTime, Numeric, Boolean, Text, DECIMAL
from sqlalchemy.types import *
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import relationship
from sqlalchemy.orm import Mapped
from datetime import date   
from datetime import datetime
from typing import List


logging.getLogger('sqlalchemy.engine.Engine').disabled = True  # remove for additional logging

Base = declarative_base()  # from system/genai/create_db_models_inserts/create_db_models_prefix.py


from sqlalchemy.dialects.sqlite import *

class Customer(Base):
    """description: Model for holding customer information with a balance and credit limit."""
    """
    description: Represents a customer in the system with unique names and a balance constraint.
    """
    __tablename__ = 'customer'
    _s_collection_name = 'Customer'
    __bind_key__ = 'None'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), unique=True)
    email = Column(String(50))
    balance = Column(Integer)
    credit_limit = Column(Integer)

class Product(Base):
    """description: Model representing products with a price and carbon-neutral status."""
    """
    description: Represents a product available for purchase.
    """
    __tablename__ = 'product'
    _s_collection_name = 'Product'
    __bind_key__ = 'None'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50))
    price = Column(Integer)
    carbon_neutral = Column(Boolean)

class Order(Base):
    """description: Model for customer orders, including references to customer and items."""
    """
    description: Represents an order made by a customer, needing a valid customer reference.
    """
    __tablename__ = 'order'
    _s_collection_name = 'Order'
    __bind_key__ = 'None'
    id = Column(Integer, primary_key=True, autoincrement=True)
    customer_id = Column(Integer, ForeignKey('customer.id'))
    order_date = Column(DateTime)
    notes = Column(String(255))
    total_amount = Column(Integer)

class Item(Base):
    """description: Model for items in orders, with calculated amount from quantity and unit price."""
    """
    description: Represents an item included in an order with non-null quantity and derived attributes.
    """
    __tablename__ = 'item'
    _s_collection_name = 'Item'
    __bind_key__ = 'None'
    id = Column(Integer, primary_key=True, autoincrement=True)
    order_id = Column(Integer, ForeignKey('order.id'))
    product_id = Column(Integer, ForeignKey('product.id'))
    quantity = Column(Integer, nullable=False)
    price = Column(Integer)
    unit_price = Column(Integer)
    amount = Column(Integer, doc='derived: quantity * unit_price')



engine = create_engine('sqlite:///docs/import/create_db_models.sqlite')

Base.metadata.create_all(engine)

