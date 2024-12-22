# using resolved_model gpt-4o-2024-08-06# created from response, to create create_db_models.sqlite, with test data
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
from datetime import date   
from datetime import datetime


logging.getLogger('sqlalchemy.engine.Engine').disabled = True  # remove for additional logging

Base = declarative_base()  # from system/genai/create_db_models_inserts/create_db_models_prefix.py

from sqlalchemy.dialects.sqlite import *


class Customer(Base):
    """description: Table for storing customer information."""
    __tablename__ = 'customer'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, unique=True)
    balance = Column(Integer)
    credit_limit = Column(Integer)


class Order(Base):
    """description: Table for storing orders made by customers."""
    __tablename__ = 'order'

    id = Column(Integer, primary_key=True, autoincrement=True)
    customer_id = Column(Integer, ForeignKey('customer.id'))
    date_created = Column(DateTime)
    date_shipped = Column(DateTime, nullable=True)
    amount_total = Column(Integer)
    notes = Column(String)


class Item(Base):
    """description: Table for storing items in each order."""
    __tablename__ = 'item'

    id = Column(Integer, primary_key=True, autoincrement=True)
    order_id = Column(Integer, ForeignKey('order.id'))
    product_id = Column(Integer, ForeignKey('product.id'))
    quantity = Column(Integer)
    unit_price = Column(Integer)
    amount = Column(Integer)


class Product(Base):
    """description: Table for storing product information."""
    __tablename__ = 'product'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String)
    unit_price = Column(Integer)


# end of model classes


try:
    
    
    
    
    # ALS/GenAI: Create an SQLite database
    
    engine = create_engine('sqlite:///system/genai/temp/create_db_models.sqlite')
    
    Base.metadata.create_all(engine)
    
    
    
    Session = sessionmaker(bind=engine)
    
    session = Session()
    
    
    
    # ALS/GenAI: Prepare for sample data
    
    
    
    session.commit()
    customer_1 = Customer(name="Customer A", balance=1000, credit_limit=5000)
    customer_2 = Customer(name="Customer B", balance=2000, credit_limit=7000)
    customer_3 = Customer(name="Customer C", balance=3000, credit_limit=9000)
    customer_4 = Customer(name="Customer D", balance=4000, credit_limit=10000)
    order_1 = Order(customer_id=1, date_created=date(2023, 3, 15), date_shipped=None, amount_total=300, notes="Urgent")
    order_2 = Order(customer_id=2, date_created=date(2023, 4, 20), date_shipped=None, amount_total=150, notes="")
    order_3 = Order(customer_id=3, date_created=date(2023, 5, 25), date_shipped=None, amount_total=250, notes="")
    order_4 = Order(customer_id=4, date_created=date(2023, 6, 30), date_shipped=None, amount_total=350, notes="Regular shipment")
    item_1 = Item(order_id=1, product_id=1, quantity=10, unit_price=25, amount=250)
    item_2 = Item(order_id=1, product_id=2, quantity=5, unit_price=10, amount=50)
    item_3 = Item(order_id=2, product_id=1, quantity=15, unit_price=25, amount=375)
    item_4 = Item(order_id=3, product_id=2, quantity=20, unit_price=10, amount=200)
    product_1 = Product(name="Widget A", unit_price=25)
    product_2 = Product(name="Widget B", unit_price=10)
    product_3 = Product(name="Widget C", unit_price=15)
    product_4 = Product(name="Widget D", unit_price=20)
    
    
    
    session.add_all([customer_1, customer_2, customer_3, customer_4, order_1, order_2, order_3, order_4, item_1, item_2, item_3, item_4, product_1, product_2, product_3, product_4])
    session.commit()
    # end of test data
    
    
except Exception as exc:
    print(f'Test Data Error: {exc}')
