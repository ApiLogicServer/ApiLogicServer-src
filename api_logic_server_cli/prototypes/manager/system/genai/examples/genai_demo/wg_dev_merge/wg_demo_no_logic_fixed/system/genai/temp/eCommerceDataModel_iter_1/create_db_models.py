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
from datetime import date   
from datetime import datetime


logging.getLogger('sqlalchemy.engine.Engine').disabled = True  # remove for additional logging

Base = declarative_base()  # from system/genai/create_db_models_inserts/create_db_models_prefix.py


from sqlalchemy.dialects.sqlite import *

class Customer(Base):
    """description: Represents a customer in the system with unique names and a balance constraint."""
    __tablename__ = 'customers'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), unique=True)
    email = Column(String(50))
    balance = Column(Integer)
    credit_limit = Column(Integer)

class Order(Base):
    """description: Represents an order made by a customer, needing a valid customer reference."""
    __tablename__ = 'orders'
    id = Column(Integer, primary_key=True, autoincrement=True)
    customer_id = Column(Integer, ForeignKey('customers.id'), nullable=False)
    order_date = Column(DateTime)
    notes = Column(String(255))
    total_amount = Column(Integer)
    amount_total = Column(Integer)

class Item(Base):
    """description: Represents an item included in an order with non-null quantity and derived attributes."""
    __tablename__ = 'items'
    id = Column(Integer, primary_key=True, autoincrement=True)
    order_id = Column(Integer, ForeignKey('orders.id'))
    product_id = Column(Integer, ForeignKey('products.id'))
    quantity = Column(Integer, nullable=False)
    price = Column(Integer)
    amount = Column(Integer)
    unit_price = Column(Integer)

class Product(Base):
    """description: Represents a product available for purchase."""
    __tablename__ = 'products'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50))
    price = Column(Integer)


# end of model classes


try:
    
    
    # ALS/GenAI: Create an SQLite database
    engine = create_engine('sqlite:///system/genai/temp/create_db_models.sqlite')
    Base.metadata.create_all(engine)
    
    Session = sessionmaker(bind=engine)
    session = Session()
    
    # ALS/GenAI: Prepare for sample data
    
    
    session.commit()
    Customer(name="Alice Smith", email="alice@example.com", balance=0, credit_limit=500)
    Order(customer_id=1, order_date=date(2023, 3, 1), notes="Urgent delivery", total_amount=200, amount_total=200)
    Item(order_id=1, product_id=1, quantity=2, price=50, amount=100, unit_price=50)
    Product(name="Laptop", price=1000)
    
    
    
    session.add_all([customer1, order1, item1, product1])
    session.commit()
    # end of test data
    
    
except Exception as exc:
    print(f'Test Data Error: {exc}')
