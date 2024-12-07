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
    """
    description: Table to store customer details.
    """
    __tablename__ = 'customers'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String)
    email = Column(String, unique=True)
    phone_number = Column(String)
    address = Column(String)
    balance = Column(DECIMAL)
    credit_limit = Column(DECIMAL)
    unpaid_order_total = Column(DECIMAL)


class Order(Base):
    """
    description: Table to store order details, with a notes field included.
    """
    __tablename__ = 'orders'
    id = Column(Integer, primary_key=True, autoincrement=True)
    customer_id = Column(Integer, ForeignKey('customers.id'))
    order_date = Column(DateTime)
    notes = Column(Text)  # Field for additional notes
    amount_total = Column(DECIMAL)
    item_count = Column(Integer)



class Item(Base):
    """
    description: Table to store individual items that are linked to orders.
    """
    __tablename__ = 'items'
    id = Column(Integer, primary_key=True, autoincrement=True)
    order_id = Column(Integer, ForeignKey('orders.id'))
    product_id = Column(Integer, ForeignKey('products.id'))
    quantity = Column(Integer)
    unit_price = Column(DECIMAL)
    amount = Column(DECIMAL)  # Calculated as quantity * unit_price



class Product(Base):
    """
    description: Table to store product details.
    """
    __tablename__ = 'products'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String)
    description = Column(String)
    price = Column(DECIMAL)



# end of model classes


try:
    
    
    
    
    # ALS/GenAI: Create an SQLite database
    
    engine = create_engine('sqlite:///system/genai/temp/create_db_models.sqlite')
    
    Base.metadata.create_all(engine)
    
    
    
    Session = sessionmaker(bind=engine)
    
    session = Session()
    
    
    
    # ALS/GenAI: Prepare for sample data
    
    
    
    session.commit()
    customer_1 = Customer(name="Alice Smith", email="alice.smith@example.com", phone_number="123-456-7890", address="123 Elm Street", balance=500, credit_limit=1000, unpaid_order_total=0)
    customer_2 = Customer(name="Bob Brown", email="bob.brown@example.com", phone_number="234-567-8901", address="456 Oak Avenue", balance=300, credit_limit=500, unpaid_order_total=0)
    customer_3 = Customer(name="Charlie Johnson", email="charlie.johnson@example.com", phone_number="345-678-9012", address="789 Pine Road", balance=150, credit_limit=400, unpaid_order_total=0)
    customer_4 = Customer(name="Diana Gonzalez", email="diana.gonzalez@example.com", phone_number="456-789-0123", address="321 Maple Court", balance=50, credit_limit=300, unpaid_order_total=0)
    order_1 = Order(customer_id=1, order_date=date(2023, 9, 20), notes="Leave package at back door.", amount_total=1999.98, item_count=2)
    order_2 = Order(customer_id=2, order_date=date(2023, 9, 21), notes="Urgent delivery.", amount_total=199.99, item_count=1)
    order_3 = Order(customer_id=3, order_date=date(2023, 9, 22), notes="Gift wrap this order.", amount_total=2249.97, item_count=3)
    order_4 = Order(customer_id=4, order_date=date(2023, 9, 23), notes="Deliver between 9-11 AM.", amount_total=99.99, item_count=1)
    product_1 = Product(name="Laptop", description="15-inch display, 256GB SSD", price=999.99)
    product_2 = Product(name="Headphones", description="Noise-canceling, over-ear", price=199.99)
    product_3 = Product(name="Smartphone", description="Unlocked, 128GB storage", price=749.99)
    product_4 = Product(name="Coffee Maker", description="Automatic, with built-in grinder", price=99.99)
    item_1 = Item(order_id=1, product_id=1, quantity=2, unit_price=999.99, amount=1999.98)
    item_2 = Item(order_id=2, product_id=2, quantity=1, unit_price=199.99, amount=199.99)
    item_3 = Item(order_id=3, product_id=3, quantity=3, unit_price=749.99, amount=2249.97)
    item_4 = Item(order_id=4, product_id=4, quantity=1, unit_price=99.99, amount=99.99)
    
    
    
    session.add_all([customer_1, customer_2, customer_3, customer_4, order_1, order_2, order_3, order_4, product_1, product_2, product_3, product_4, item_1, item_2, item_3, item_4])
    session.commit()
    # end of test data
    
    
except Exception as exc:
    print(f'Test Data Error: {exc}')
