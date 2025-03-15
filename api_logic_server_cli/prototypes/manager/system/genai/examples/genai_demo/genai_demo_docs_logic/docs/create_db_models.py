# using resolved_model self.resolved_model FIXME
# created from response, to create create_db_models.sqlite, with test data
#    that is used to create project
# should run without error in manager 
#    if not, check for decimal, indent, or import issues

import decimal
import logging
import sqlalchemy
from sqlalchemy.sql import func 
from decimal import Decimal
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
    """description: Represents a customer entity with unique name, credit limit, and balance."""
    __tablename__ = 'customer'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), unique=True)
    credit_limit = Column(DECIMAL)
    balance = Column(DECIMAL)

class Order(Base):
    """description: Represents an order entity linked to a customer with a note field."""
    __tablename__ = 'order'
    id = Column(Integer, primary_key=True, autoincrement=True)
    customer_id = Column(Integer, ForeignKey('customer.id'))
    date_shipped = Column(DateTime)
    amount_total = Column(DECIMAL)
    notes = Column(String(255))

class Item(Base):
    """description: Represents an item within an order, linked to a product with mandatory quantity."""
    __tablename__ = 'item'
    id = Column(Integer, primary_key=True, autoincrement=True)
    order_id = Column(Integer, ForeignKey('order.id'))
    product_id = Column(Integer, ForeignKey('product.id'))
    quantity = Column(Integer, nullable=False)
    unit_price = Column(DECIMAL)
    amount = Column(DECIMAL)

class Product(Base):
    """description: Represents a product entity with unique name and unit price."""
    __tablename__ = 'product'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), unique=True)
    unit_price = Column(DECIMAL)


# end of model classes


try:
    
    
    # ALS/GenAI: Create an SQLite database
    import os
    mgr_db_loc = True
    if mgr_db_loc:
        print(f'creating in manager: sqlite:///system/genai/temp/create_db_models.sqlite')
        engine = create_engine('sqlite:///system/genai/temp/create_db_models.sqlite')
    else:
        current_file_path = os.path.dirname(__file__)
        print(f'creating at current_file_path: {current_file_path}')
        engine = create_engine(f'sqlite:///{current_file_path}/create_db_models.sqlite')
    Base.metadata.create_all(engine)
    
    
    Session = sessionmaker(bind=engine)
    session = Session()
    
    # ALS/GenAI: Prepare for sample data
    
    
    session.commit()
    customer1 = Customer(id=1, name="John Doe", credit_limit=1000, balance=0)
    customer2 = Customer(id=2, name="Jane Roe", credit_limit=2000, balance=0)
    customer3 = Customer(id=3, name="Acme Corp", credit_limit=5000, balance=0)
    customer4 = Customer(id=4, name="Globex Inc", credit_limit=3000, balance=0)
    product1 = Product(id=1, name="Widget", unit_price=10)
    product2 = Product(id=2, name="Gadget", unit_price=20)
    product3 = Product(id=3, name="Doodad", unit_price=15)
    product4 = Product(id=4, name="Thingamajig", unit_price=25)
    order1 = Order(id=1, customer_id=1, amount_total=0, notes="First order")
    order2 = Order(id=2, customer_id=2, amount_total=0, notes="Second order")
    order3 = Order(id=3, customer_id=3, amount_total=0, notes="Third order")
    order4 = Order(id=4, customer_id=4, amount_total=0, notes="Fourth order")
    item1 = Item(id=1, order_id=1, product_id=1, quantity=2, unit_price=10, amount=20)
    item2 = Item(id=2, order_id=2, product_id=2, quantity=1, unit_price=20, amount=20)
    item3 = Item(id=3, order_id=3, product_id=3, quantity=3, unit_price=15, amount=45)
    item4 = Item(id=4, order_id=4, product_id=4, quantity=4, unit_price=25, amount=100)
    
    
    
    session.add_all([customer1, customer2, customer3, customer4, product1, product2, product3, product4, order1, order2, order3, order4, item1, item2, item3, item4])
    session.commit()
    # end of test data
    
    
except Exception as exc:
    print(f'Test Data Error: {exc}')
