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

class CustomerAccount(Base):
    """description: This table holds customer account details with credit checks."""
    """
    description: This table holds customer account details with credit checks.
    """
    __tablename__ = 'customer_account'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=True)
    email = Column(String, nullable=True)
    balance = Column(Float, nullable=True)
    credit_limit = Column(Float, nullable=True)

class Address(Base):
    """description: This table contains addresses associated with CustomerAccount."""
    """
    description: This table contains addresses associated with CustomerAccount.
    """
    __tablename__ = 'address'
    id = Column(Integer, primary_key=True, autoincrement=True)
    customer_account_id = Column(Integer, ForeignKey('customer_account.id'),
        nullable=False)
    street = Column(String, nullable=True)
    city = Column(String, nullable=True)
    state = Column(String, nullable=True)
    zip_code = Column(String, nullable=True)

class SalesRep(Base):
    """description: This table contains sales representative details."""
    """
    description: This table contains sales representative details.
    """
    __tablename__ = 'sales_rep'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=True)
    region = Column(String, nullable=True)

class Order(Base):
    """description: This table contains order details with an assigned sales representative."""
    """
    description: This table contains order details with an assigned sales representative.
    """
    __tablename__ = 'order'
    id = Column(Integer, primary_key=True, autoincrement=True)
    customer_account_id = Column(Integer, ForeignKey('customer_account.id'),
        nullable=False)
    order_date = Column(Date, nullable=True)
    sales_rep_id = Column(Integer, ForeignKey('sales_rep.id'), nullable=False)
    notes = Column(String, nullable=True)
    amount_total = Column(Float, nullable=True)

class Item(Base):
    """description: This table links orders to products for each item on an order."""
    """
    description: This table links orders to products for each item on an order.
    """
    __tablename__ = 'item'
    id = Column(Integer, primary_key=True, autoincrement=True)
    order_id = Column(Integer, ForeignKey('order.id'), nullable=False)
    product_id = Column(Integer, ForeignKey('product.id'), nullable=False)
    quantity = Column(Integer, nullable=True)
    unit_price = Column(Float, nullable=True)
    amount = Column(Float, nullable=True)

class Product(Base):
    """description: This table contains product information."""
    """
    description: This table contains product information.
    """
    __tablename__ = 'product'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=True)
    price = Column(Float, nullable=True)


# end of model classes

