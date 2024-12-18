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
    """description: Represents customers in the system."""
    __tablename__ = 'customer'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String)
    email = Column(String)


class Order(Base):
    """description: Represents orders placed by customers."""
    __tablename__ = 'order'

    id = Column(Integer, primary_key=True, autoincrement=True)
    customer_id = Column(Integer, ForeignKey('customer.id'))
    order_date = Column(DateTime)
    notes = Column(String)


class Product(Base):
    """description: Represents products available in the system."""
    __tablename__ = 'product'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String)
    price = Column(Integer)


class OrderItem(Base):
    """description: Represents items in an order."""
    __tablename__ = 'order_item'

    id = Column(Integer, primary_key=True, autoincrement=True)
    order_id = Column(Integer, ForeignKey('order.id'))
    product_id = Column(Integer, ForeignKey('product.id'))
    quantity = Column(Integer)


# end of model classes


try:
    
    
    
    
    # ALS/GenAI: Create an SQLite database
    
    engine = create_engine('sqlite:///system/genai/temp/create_db_models.sqlite')
    
    Base.metadata.create_all(engine)
    
    
    
    Session = sessionmaker(bind=engine)
    
    session = Session()
    
    
    
    # ALS/GenAI: Prepare for sample data
    
    
    
    session.commit()
    customer1 = Customer(name='John Doe', email='johndoe@example.com')
    customer2 = Customer(name='Jane Smith', email='janesmith@example.com')
    customer3 = Customer(name='Michael Brown', email='michaelbrown@example.com')
    customer4 = Customer(name='Emily Davis', email='emilydavis@example.com')
    product1 = Product(name='Widget', price=20)
    product2 = Product(name='Gadget', price=40)
    product3 = Product(name='Doohickey', price=10)
    product4 = Product(name='Thingamajig', price=25)
    order1 = Order(customer_id=1, order_date=date(2023, 1, 15), notes='Delivered to reception')
    order2 = Order(customer_id=2, order_date=date(2023, 2, 20), notes='Urgent delivery')
    order3 = Order(customer_id=3, order_date=date(2023, 3, 10), notes='New address')
    order4 = Order(customer_id=4, order_date=date(2023, 4, 5), notes='Include gift wrapping')
    order_item1 = OrderItem(order_id=1, product_id=1, quantity=2)
    order_item2 = OrderItem(order_id=1, product_id=2, quantity=1)
    order_item3 = OrderItem(order_id=2, product_id=3, quantity=5)
    order_item4 = OrderItem(order_id=2, product_id=1, quantity=1)
    
    
    
    session.add_all([customer1, customer2, customer3, customer4, product1, product2, product3, product4, order1, order2, order3, order4, order_item1, order_item2, order_item3, order_item4])
    session.commit()
    # end of test data
    
    
except Exception as exc:
    print(f'Test Data Error: {exc}')
