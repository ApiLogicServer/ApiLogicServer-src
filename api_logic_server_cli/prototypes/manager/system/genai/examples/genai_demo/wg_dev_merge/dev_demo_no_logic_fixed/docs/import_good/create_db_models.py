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
    """description: Model for Customer data, representing customers in the system."""
    """
    Represents a customer in the system.
    """
    __tablename__ = 'customers'
    id = Column(Integer, primary_key=True)
    name = Column(String(50), unique=True)
    email = Column(String(50))
    balance = Column(Integer)
    credit_limit = Column(Integer)

class Product(Base):
    """description: Model for Product data, representing products."""
    """
    Represents a product available for purchase.
    """
    __tablename__ = 'products'
    id = Column(Integer, primary_key=True)
    name = Column(String(50))
    price = Column(Integer)
    carbon_neutral = Column(Boolean)

class Order(Base):
    """description: Model for Order data, representing orders placed by customers."""
    """
    Represents an order made by a customer.
    """
    __tablename__ = 'orders'
    id = Column(Integer, primary_key=True)
    customer_id = Column(ForeignKey('customers.id'), nullable=False)
    order_date = Column(DateTime)
    notes = Column(String(255))
    total_amount = Column(Integer)

class Item(Base):
    """description: Model for Item data, representing items in an order."""
    """
    Represents an item included in an order.
    """
    __tablename__ = 'items'
    id = Column(Integer, primary_key=True)
    order_id = Column(ForeignKey('orders.id'))
    product_id = Column(ForeignKey('products.id'))
    quantity = Column(Integer, nullable=False)
    price = Column(Integer)
    amount = Column(Integer)
    unit_price = Column(Integer)



engine = create_engine('sqlite:///docs/import/create_db_models.sqlite')

Base.metadata.create_all(engine)

