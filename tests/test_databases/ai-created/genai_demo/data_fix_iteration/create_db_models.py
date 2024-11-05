# created from response, to create create_db_models.sqlite, with test data
#    that is used to create project
# should run without error in manager 
#    if not, check for decimal, indent, or import issues

import decimal
import logging
import sqlalchemy
from sqlalchemy.sql import func 
from logic_bank.logic_bank import Rule
from sqlalchemy import create_engine, Column, Integer, String, Float, ForeignKey, Date, DateTime, Numeric, Boolean, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import relationship
from datetime import date   
from datetime import datetime

logging.getLogger('sqlalchemy.engine.Engine').disabled = True  # remove for additional logging

Base = declarative_base()  # from system/genai/create_db_models_inserts/create_db_models_prefix.py


class Customer(Base):
    """description: Represents a customer with their balance and credit limit."""
    __tablename__ = 'customer'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String)
    balance = Column(Float, nullable=False, default=0.0)
    credit_limit = Column(Float, nullable=False)


class Order(Base):
    """description: Represents a customer's order with notes and total amount."""
    __tablename__ = 'order'

    id = Column(Integer, primary_key=True, autoincrement=True)
    customer_id = Column(Integer, ForeignKey('customer.id'))
    date_shipped = Column(DateTime)
    amount_total = Column(Float, nullable=False, default=0.0)
    notes = Column(String)


class Item(Base):
    """description: Represents an item in an order, with calculated amount and copied unit price."""
    __tablename__ = 'item'

    id = Column(Integer, primary_key=True, autoincrement=True)
    order_id = Column(Integer, ForeignKey('order.id'))
    product_id = Column(Integer, ForeignKey('product.id'))
    quantity = Column(Integer, nullable=False)
    unit_price = Column(Float, nullable=False)
    amount = Column(Float, nullable=False, default=0.0)


class Product(Base):
    """description: Represents a product with a defined unit price."""
    __tablename__ = 'product'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String)
    unit_price = Column(Float, nullable=False)


# ALS/GenAI: Create an SQLite database
engine = create_engine('sqlite:///system/genai/temp/create_db_models.sqlite')
Base.metadata.create_all(engine)

Session = sessionmaker(bind=engine)
session = Session()

# ALS/GenAI: Prepare for sample data

# Sample Test Data

# Customer
customer1 = Customer(id=1, name='John Doe', balance=0.0, credit_limit=5000.0)
customer2 = Customer(id=2, name='Jane Smith', balance=0.0, credit_limit=2000.0)

# Product
product1 = Product(id=1, name='Widget', unit_price=20.0)
product2 = Product(id=2, name='Gadget', unit_price=10.0)

# Order
order1 = Order(id=1, customer_id=1, date_shipped=None, amount_total=0.0, notes='Urgent')
order2 = Order(id=2, customer_id=1, date_shipped=date(2023,10,1), amount_total=0.0, notes='Standard')
order3 = Order(id=3, customer_id=2, date_shipped=None, amount_total=0.0, notes='Express')

# Item
item1 = Item(id=1, order_id=1, product_id=1, quantity=5, unit_price=20.0, amount=100.0)
item2 = Item(id=2, order_id=1, product_id=2, quantity=10, unit_price=10.0, amount=100.0)
item3 = Item(id=3, order_id=2, product_id=1, quantity=3, unit_price=20.0, amount=60.0)
item4 = Item(id=4, order_id=3, product_id=2, quantity=8, unit_price=10.0, amount=80.0)


session.add_all([customer1, customer2, product1, product2, order1, order2, order3, item1, item2, item3, item4])
session.commit()
