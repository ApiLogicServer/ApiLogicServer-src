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
from datetime import datetime
import os

# Define the base class
Base = declarative_base()

# Data Model Definitions
class CustomerAccount(Base):
    """
    description: Table for storing customer accounts with credit and balance tracking.
    Can have multiple addresses.
    """
    __tablename__ = 'customer_account'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    balance = Column(Float, default=0.0)  # Starting balance is 0
    credit_limit = Column(Float, nullable=False)
    addresses = relationship('Address', back_populates='customer_account')

class Address(Base):
    """
    description: Table of addresses associated with a customer account.
    """
    __tablename__ = 'address'
    id = Column(Integer, primary_key=True, autoincrement=True)
    customer_account_id = Column(Integer, ForeignKey('customer_account.id'), nullable=False)
    street = Column(String, nullable=False)
    city = Column(String, nullable=False)
    state = Column(String, nullable=False)
    zipcode = Column(String, nullable=False)
    customer_account = relationship('CustomerAccount', back_populates='addresses')

class SalesRep(Base):
    """
    description: Table for storing sales representative details.
    """
    __tablename__ = 'sales_rep'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    email = Column(String, nullable=False)

class Order(Base):
    """
    description: Table for storing orders, linking customers with the items they purchase.
    Includes order-level total amount calculation and optional shipment date.
    Each order is assigned to a sales representative.
    """
    __tablename__ = 'order'
    id = Column(Integer, primary_key=True, autoincrement=True)
    customer_account_id = Column(Integer, ForeignKey('customer_account.id'), nullable=False)
    sales_rep_id = Column(Integer, ForeignKey('sales_rep.id'), nullable=False)
    amount_total = Column(Float, default=0.0)  # Calculated total amount of order
    date_shipped = Column(DateTime, nullable=True)
    notes = Column(String, nullable=True)  # Optional field for notes
    sales_rep = relationship('SalesRep')

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
    Rule.sum(derive=CustomerAccount.balance, as_sum_of=Order.amount_total, where=lambda row: row.date_shipped is None)
    Rule.sum(derive=Order.amount_total, as_sum_of=Item.amount)
    Rule.formula(derive=Item.amount, as_expression=lambda row: row.quantity * row.unit_price)
    Rule.copy(derive=Item.unit_price, from_parent=lambda row: row.product_id.unit_price)
    Rule.constraint(validate=CustomerAccount,
                    as_condition=lambda row: row.balance <= row.credit_limit,
                    error_msg="Customer balance ({row.balance}) exceeds credit limit ({row.credit_limit})")

# LogicBank.activate(session=session, activator=declare_logic)

# Test Data Insertion
# Sales Rep
sales_rep1 = SalesRep(name="Charlie", email="charlie@company.com")
sales_rep2 = SalesRep(name="Dana", email="dana@company.com")

# Products
product1 = Product(name="Widget", unit_price=10.0)
product2 = Product(name="Gadget", unit_price=20.0)

# Customers
customer1 = CustomerAccount(name="Alice", credit_limit=100.0)
customer2 = CustomerAccount(name="Bob", credit_limit=50.0)

# Addresses
address1 = Address(customer_account_id=1, street="123 Apple St", city="Wonderland", state="NY", zipcode="10001")
address2 = Address(customer_account_id=2, street="456 Orange Rd", city="Paradise", state="CA", zipcode="90001")

# Orders
order1 = Order(customer_account_id=1, sales_rep_id=1, date_shipped=None, notes="Urgent order")
order2 = Order(customer_account_id=2, sales_rep_id=2, date_shipped=datetime.now(), notes="Delayed order")

# Items
item1 = Item(order_id=1, product_id=1, quantity=2, unit_price=10.0, amount=20.0)
item2 = Item(order_id=1, product_id=2, quantity=1, unit_price=20.0, amount=20.0)
item3 = Item(order_id=2, product_id=1, quantity=3, unit_price=10.0, amount=30.0)

# Add to session
session.add_all([sales_rep1, sales_rep2, product1, product2, customer1, customer2, address1, address2, order1, order2, item1, item2, item3])

# Calculate initial derived attributes without relying on LogicBank
for order in session.query(Order):
    order.amount_total = sum(item.amount for item in session.query(Item).filter(Item.order_id == order.id))

for customer in session.query(CustomerAccount):
    customer.balance = sum(order.amount_total for order in session.query(Order).filter(Order.customer_account_id == customer.id, Order.date_shipped == None))

# Commit data
session.commit()
