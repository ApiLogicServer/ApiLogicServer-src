# created from response - used to create database and project
#  should run without error
#  if not, check for decimal, indent, or import issues

import decimal

import logging



logging.getLogger('sqlalchemy.engine.Engine').disabled = True  # remove for additional logging

import sqlalchemy



from sqlalchemy.sql import func  # end imports from system/genai/create_db_models_inserts/create_db_models_prefix.py

from logic_bank.logic_bank import Rule

from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.orm.session import Session
from datetime import datetime
import os

# Define the base class
Base = declarative_base()

# Data Model Definitions
class Customer(Base):
    """
    description: Table for storing customer information with credit and balance tracking.
    """
    __tablename__ = 'customer'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    balance = Column(Float, default=0.0)  # Starting balance is 0
    credit_limit = Column(Float, nullable=False)

class Order(Base):
    """
    description: Table for storing orders, linking customers with the items they purchase.
    Includes order-level total amount calculation and optional shipment date.
    """
    __tablename__ = 'order'
    id = Column(Integer, primary_key=True, autoincrement=True)
    customer_id = Column(Integer, ForeignKey('customer.id'), nullable=False)
    amount_total = Column(Float, default=0.0)  # Calculated total amount of order
    date_shipped = Column(DateTime, nullable=True)
    notes = Column(String, nullable=True)  # Optional field for notes

class Item(Base):
    """
    description: Table for storing individual items within an order, defining quantity and unit price.
    Also calculates the total amount for each item line.
    """
    __tablename__ = 'item'
    id = Column(Integer, primary_key=True, autoincrement=True)
    order_id = Column(Integer, ForeignKey('order.id'), nullable=False)
    product_id = Column(Integer, ForeignKey('product.id'), nullable=False)
    quantity = Column(Integer, nullable=False)
    unit_price = Column(Float, nullable=False)
    amount = Column(Float, default=0.0)  # Calculated as quantity * unit_price

class Product(Base):
    """
    description: Table for storing product information including price.
    """
    __tablename__ = 'product'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    unit_price = Column(Float, nullable=False)

# Database Initialization
db_path = "system/genai/temp/create_db_models.sqlite"
os.makedirs(os.path.dirname(db_path), exist_ok=True)
engine = create_engine(f'sqlite:///system/genai/temp/create_db_models.sqlite')
Base.metadata.create_all(engine)

# Session Initialization
Session = sessionmaker(bind=engine)
session = Session()

# LogicBank Rules Setup
# from logic_bank.rule_bank import rule_bank_setup, rule_bank_withdraw

def declare_logic():
    Rule.sum(derive=Customer.balance, as_sum_of=Order.amount_total, where=lambda row: row.date_shipped is None)
    Rule.sum(derive=Order.amount_total, as_sum_of=Item.amount)
    Rule.formula(derive=Item.amount, as_expression=lambda row: row.quantity * row.unit_price)
    Rule.copy(derive=Item.unit_price, from_parent=lambda row: row.product_id.unit_price)
    Rule.constraint(validate=Customer,
                    as_condition=lambda row: row.balance <= row.credit_limit,
                    error_msg="Customer balance ({row.balance}) exceeds credit limit ({row.credit_limit})")

# LogicBank.activate(session=session, activator=declare_logic)

# Test Data Insertion
# Products
product1 = Product(name="Widget", unit_price=10.0)
product2 = Product(name="Gadget", unit_price=20.0)

# Customers
customer1 = Customer(name="Alice", credit_limit=100.0)
customer2 = Customer(name="Bob", credit_limit=50.0)

# Orders
order1 = Order(customer_id=1, date_shipped=None, notes="Urgent order")
order2 = Order(customer_id=2, date_shipped=datetime.now(), notes="Delayed order")

# Items
item1 = Item(order_id=1, product_id=1, quantity=2, unit_price=10.0, amount=20.0)
item2 = Item(order_id=1, product_id=2, quantity=1, unit_price=20.0, amount=20.0)
item3 = Item(order_id=2, product_id=1, quantity=3, unit_price=10.0, amount=30.0)

# Add to session
session.add_all([product1, product2, customer1, customer2, order1, order2, item1, item2, item3])

# Calculate initial derived attributes without relying on LogicBank
for order in [order1, order2]:
    order.amount_total = sum(item.amount for item in (item1, item2, item3) if item.order_id == order.id)

for customer in [customer1, customer2]:
    customer.balance = sum(order.amount_total for order in [order1, order2] if order.customer_id == customer.id and order.date_shipped is None)

# Commit data
session.commit()