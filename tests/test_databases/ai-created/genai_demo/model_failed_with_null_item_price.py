import decimal

import logging



logging.getLogger('sqlalchemy.engine.Engine').disabled = True  # remove for additional logging

import sqlalchemy



from sqlalchemy.sql import func  # end imports from system/genai/create_db_models_inserts/create_db_models_prefix.py



from logic_bank.logic_bank import Rule
from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, DateTime, Numeric, Sequence
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.sql import func
# from logic_bank.logic_bank import LogicBank
# from logic_bank.rules import DeclareRule as Rule
import datetime

# Step 1: Define SQLAlchemy models

Base = declarative_base()

class Customer(Base):
    """description: A model for storing customer data including balance and credit limit."""
    __tablename__ = 'customers'
    
    id = Column(Integer, Sequence('customer_id_seq'), primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    balance = Column(Numeric, nullable=True, default=0)
    credit_limit = Column(Numeric, nullable=True)

class Order(Base):
    """description: A model for storing orders with amounts and notes."""
    __tablename__ = 'orders'
    
    id = Column(Integer, Sequence('order_id_seq'), primary_key=True, autoincrement=True)
    customer_id = Column(Integer, ForeignKey('customers.id'), nullable=False)
    amount_total = Column(Numeric, nullable=True, default=0)
    date_shipped = Column(DateTime, nullable=True)
    notes = Column(String, nullable=True)

class Item(Base):
    """description: A model for storing line items of orders."""
    __tablename__ = 'items'
    
    id = Column(Integer, Sequence('item_id_seq'), primary_key=True, autoincrement=True)
    order_id = Column(Integer, ForeignKey('orders.id'), nullable=False)
    product_id = Column(Integer, ForeignKey('products.id'), nullable=False)
    quantity = Column(Numeric, nullable=False)
    unit_price = Column(Numeric, nullable=False)  # FIXME this fails
    amount = Column(Numeric, nullable=True)

class Product(Base):
    """description: A model for storing products with unit prices."""
    __tablename__ = 'products'
    
    id = Column(Integer, Sequence('product_id_seq'), primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    unit_price = Column(Numeric, nullable=False)


# Step 2: Enforce LogicBank Rules

def declare_logic():
    Rule.formula(derive=Item.amount, 
                 as_expression=lambda row: row.quantity * row.unit_price)
    Rule.sum(derive=Order.amount_total, 
             as_sum_of=Item.amount)
    Rule.sum(derive=Customer.balance, 
             as_sum_of=Order.amount_total,
             where=lambda row: row.date_shipped is None)
    Rule.constraint(validate=Customer, 
                    as_condition=lambda row: row.balance <= row.credit_limit,
                    error_msg="Customer {row.id} balance exceeds credit limit")
    Rule.copy(derive=Item.unit_price, 
              from_parent=Product.unit_price)

# Step 3: Create the SQLite database and the tables

engine = create_engine('sqlite:///system/genai/temp/create_db_models.sqlite')
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
session = Session()

# Step 4: Insert test data

customer1 = Customer(name='Acme Corp', credit_limit=1000)
customer2 = Customer(name='Globex Inc', credit_limit=2000)

product1 = Product(name='Gadget', unit_price=50)
product2 = Product(name='Widget', unit_price=25)

session.add_all([customer1, customer2, product1, product2])
session.commit()

order1 = Order(customer_id=customer1.id, notes='Urgent order')
order2 = Order(customer_id=customer2.id)

session.add_all([order1, order2])
session.commit()

item1 = Item(order_id=order1.id, product_id=product1.id, quantity=5)
item2 = Item(order_id=order2.id, product_id=product2.id, quantity=10)

session.add_all([item1, item2])
session.commit()

# Step 5: Activate LogicBank and enforce rules

# LogicBank.activate(session=session, activator=declare_logic)

# The rules will automatically apply during the session commit phase
try:
    session.commit()
except Exception as e:
    print(f"Failed to commit: {e}")

session.close()
