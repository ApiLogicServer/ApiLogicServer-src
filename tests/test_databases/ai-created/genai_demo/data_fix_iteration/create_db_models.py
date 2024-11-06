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
    """
    description: This class represents customers, storing each customer's balance and credit limit.
    """
    __tablename__ = 'customers'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    balance = Column(Float, nullable=True, default=0.0)
    credit_limit = Column(Float, nullable=False, default=1000.0)


class Order(Base):
    """
    description: This class represents orders, which belong to customers and contain the total amount of the order.
    Includes a notes field and a shipped date.
    """
    __tablename__ = 'orders'

    id = Column(Integer, primary_key=True, autoincrement=True)
    customer_id = Column(Integer, ForeignKey('customers.id'), nullable=False)
    amount_total = Column(Float, nullable=True, default=0.0)
    notes = Column(String, nullable=True)
    date_shipped = Column(DateTime, nullable=True)


class Item(Base):
    """
    description: This class represents items, which are part of an order and linked to a product.
    Holds data for quantity, calculated amount and copied unit price.
    """
    __tablename__ = 'items'

    id = Column(Integer, primary_key=True, autoincrement=True)
    order_id = Column(Integer, ForeignKey('orders.id'), nullable=False)
    product_id = Column(Integer, ForeignKey('products.id'), nullable=False)
    quantity = Column(Integer, nullable=False)
    unit_price = Column(Float, nullable=True)
    amount = Column(Float, nullable=True)


class Product(Base):
    """
    description: This class represents products that can be purchased.
    """
    __tablename__ = 'products'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    unit_price = Column(Float, nullable=False)


# ALS/GenAI: Create an SQLite database
engine = create_engine('sqlite:///system/genai/temp/create_db_models.sqlite')
Base.metadata.create_all(engine)

Session = sessionmaker(bind=engine)
session = Session()

# ALS/GenAI: Prepare for sample data

# Create test data
from datetime import date

customer1 = Customer(id=1, name='John Doe', balance=0.0, credit_limit=1500.0)
customer2 = Customer(id=2, name='Jane Smith', balance=0.0, credit_limit=2000.0)

product1 = Product(id=1, name='Laptop', unit_price=1000.0)
product2 = Product(id=2, name='Smartphone', unit_price=500.0)

order1 = Order(id=1, customer_id=1, amount_total=0.0, notes='Urgent', date_shipped=None)
order2 = Order(id=2, customer_id=2, amount_total=0.0, notes='Regular shipping', date_shipped=date(2023, 10, 15))

item1 = Item(id=1, order_id=1, product_id=1, quantity=1, unit_price=1000.0, amount=1000.0)
item2 = Item(id=2, order_id=1, product_id=2, quantity=3, unit_price=500.0, amount=1500.0)
item3 = Item(id=3, order_id=2, product_id=2, quantity=2, unit_price=500.0, amount=1000.0)


session.add_all([customer1, customer2, product1, product2, order1, order2, item1, item2, item3])
session.commit()
