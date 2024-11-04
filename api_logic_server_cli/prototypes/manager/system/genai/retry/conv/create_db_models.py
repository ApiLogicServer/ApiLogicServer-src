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
    """description: Table representing customers in the system."""

    __tablename__ = 'customers'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    balance = Column(Float, default=0.0)  # Derived as sum of Order.amount_total where shipped_date is null
    credit_limit = Column(Float, nullable=False)


class Order(Base):
    """description: Table representing customer orders with associated notes."""

    __tablename__ = 'orders'

    id = Column(Integer, primary_key=True, autoincrement=True)
    customer_id = Column(Integer, ForeignKey('customers.id'))
    notes = Column(Text)
    amount_total = Column(Float, default=0.0)  # Derived as sum of Item.amount
    date_shipped = Column(DateTime)


class Item(Base):
    """description: Table representing items associated with orders."""

    __tablename__ = 'items'

    id = Column(Integer, primary_key=True, autoincrement=True)
    order_id = Column(Integer, ForeignKey('orders.id'))
    product_id = Column(Integer, ForeignKey('products.id'))
    quantity = Column(Integer, nullable=False)
    amount = Column(Float, default=0.0)  # Derived as quantity * unit_price
    unit_price = Column(Float)  # Copied from Product.unit_price


class Product(Base):
    """description: Table representing products available for sale."""

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

# Test Data Loading
from datetime import date, datetime

test_product1 = Product(id=1, name="Laptop", unit_price=1000.00)
test_product2 = Product(id=2, name="Phone", unit_price=600.00)

test_customer1 = Customer(id=1, name="Alice Smith", credit_limit=5000.00, balance=3800.00)
test_customer2 = Customer(id=2, name="Bob Johnson", credit_limit=3000.00, balance=0.0)

test_order1 = Order(id=1, customer_id=1, notes="Urgent delivery", amount_total=3800.00, date_shipped=None)
test_order2 = Order(id=2, customer_id=2, notes="Gift wrap", amount_total=1000.00, date_shipped=datetime(2023, 5, 10))

test_item1 = Item(id=1, order_id=1, product_id=1, quantity=2, amount=2000.00, unit_price=1000.00)
test_item2 = Item(id=2, order_id=1, product_id=2, quantity=3, amount=1800.00, unit_price=600.00)
test_item3 = Item(id=3, order_id=2, product_id=1, quantity=1, amount=1000.00, unit_price=1000.00)


session.add_all([test_product1, test_product2, test_customer1, test_customer2, test_order1, test_order2, test_item1, test_item2, test_item3])
session.commit()
