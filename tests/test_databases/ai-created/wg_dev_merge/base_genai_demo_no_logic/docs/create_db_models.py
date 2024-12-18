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
    """description: Storage of customer information."""
    __tablename__ = 'customer'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String)
    email = Column(String)
    join_date = Column(Date)



class Product(Base):
    """description: Catalog of products available for purchase."""
    __tablename__ = 'product'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String)
    price = Column(Integer)
    stock_quantity = Column(Integer)



class Order(Base):
    """description: Records of customer orders."""
    __tablename__ = 'order'

    id = Column(Integer, primary_key=True, autoincrement=True)
    customer_id = Column(Integer, ForeignKey('customer.id'))
    order_date = Column(Date)
    notes = Column(String)



class Item(Base):
    """description: Items purchased within an order."""
    __tablename__ = 'item'

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
    customer_1 = Customer(id=1, name="Alice", email="alice@example.com", join_date=date(2023, 1, 15))
    customer_2 = Customer(id=2, name="Bob", email="bob@example.com", join_date=date(2023, 2, 10))
    customer_3 = Customer(id=3, name="Charlie", email="charlie@example.com", join_date=date(2023, 3, 5))
    customer_4 = Customer(id=4, name="Diana", email="diana@example.com", join_date=date(2023, 4, 25))
    product_1 = Product(id=1, name="Laptop", price=1500, stock_quantity=20)
    product_2 = Product(id=2, name="Smartphone", price=800, stock_quantity=50)
    product_3 = Product(id=3, name="Headphones", price=200, stock_quantity=30)
    product_4 = Product(id=4, name="Monitor", price=300, stock_quantity=15)
    order_1 = Order(id=1, customer_id=1, order_date=date(2023, 5, 15), notes="Urgent delivery")
    order_2 = Order(id=2, customer_id=2, order_date=date(2023, 6, 10), notes="Gift wrap")
    order_3 = Order(id=3, customer_id=3, order_date=date(2023, 7, 20), notes="Include a thank you card")
    order_4 = Order(id=4, customer_id=4, order_date=date(2023, 8, 2), notes="Address needs verification")
    item_1 = Item(id=1, order_id=1, product_id=1, quantity=1)
    item_2 = Item(id=2, order_id=2, product_id=3, quantity=2)
    item_3 = Item(id=3, order_id=3, product_id=2, quantity=1)
    item_4 = Item(id=4, order_id=4, product_id=4, quantity=1)
    
    
    
    session.add_all([customer_1, customer_2, customer_3, customer_4, product_1, product_2, product_3, product_4, order_1, order_2, order_3, order_4, item_1, item_2, item_3, item_4])
    session.commit()
    # end of test data
    
    
except Exception as exc:
    print(f'Test Data Error: {exc}')
