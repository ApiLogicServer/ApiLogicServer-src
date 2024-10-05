import decimal

import logging



logging.getLogger('sqlalchemy.engine.Engine').disabled = True  # remove for additional logging

import sqlalchemy



from sqlalchemy.sql import func  # end imports from system/genai/create_db_models_inserts/create_db_models_prefix.py



from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy.dialects.sqlite import DECIMAL
import os

# from logic_bank import LogicBank
# from logic_bank.rule_bank import Rule  # FIXME

# from logic_bank.exec_row_logic.logic_row import LogicRow  # TODO circular import?
# from logic_bank.extensions.rule_extensions import RuleExtension
from logic_bank.logic_bank import Rule

# Define the database file location
db_path = 'system/genai/temp/model.sqlite'
os.makedirs(os.path.dirname(db_path), exist_ok=True)
engine = create_engine(f'sqlite:///system/genai/temp/create_db_models.sqlite')

# Define SQLAlchemy Base
Base = declarative_base()

# Define ORM models
class Customer(Base):
    __tablename__ = 'customers'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String)
    balance = Column(DECIMAL, nullable=True)
    credit_limit = Column(DECIMAL, nullable=True)
    orders = relationship("Order", back_populates="customer")

class Order(Base):
    __tablename__ = 'orders'
    id = Column(Integer, primary_key=True, autoincrement=True)
    customer_id = Column(Integer, ForeignKey('customers.id'))
    amount_total = Column(DECIMAL, nullable=True)
    date_shipped = Column(DateTime, nullable=True)
    notes = Column(String)
    customer = relationship("Customer", back_populates="orders")
    items = relationship("Item", back_populates="order")

class Product(Base):
    __tablename__ = 'products'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String)
    unit_price = Column(DECIMAL)

class Item(Base):
    __tablename__ = 'items'
    id = Column(Integer, primary_key=True, autoincrement=True)
    order_id = Column(Integer, ForeignKey('orders.id'))
    product_id = Column(Integer, ForeignKey('products.id'))
    quantity = Column(Integer)
    unit_price = Column(DECIMAL)
    amount = Column(DECIMAL, nullable=True)
    order = relationship("Order", back_populates="items")
    product = relationship("Product")

# Create the tables
Base.metadata.create_all(engine)

# Prepare the session
Session = sessionmaker(bind=engine)
session = Session()

# Add sample data
customer1 = Customer(name='Customer A', credit_limit=1000)
customer2 = Customer(name='Customer B', credit_limit=2000)
session.add_all([
    customer1,
    customer2,
    Product(name='Product X', unit_price=10),
    Product(name='Product Y', unit_price=20)
])
session.commit()

# Define LogicBank rules
def declare_logic():
    Rule.sum(derive=Customer.balance, as_sum_of=Order.amount_total, where=lambda row: row.date_shipped is None)
    Rule.sum(derive=Order.amount_total, as_sum_of=Item.amount)
    Rule.formula(derive=Item.amount, as_expression=lambda row: row.quantity * row.unit_price)
    Rule.copy(derive=Item.unit_price, from_parent=Product.unit_price)
    Rule.constraint(validate=Customer,
                    as_condition=lambda row: row.balance <= row.credit_limit,
                    error_msg="Customer balance ({row.balance}) exceeds credit limit ({row.credit_limit})")

# Activate LogicBank
# LogicBank.activate(session=session, activator=declare_logic)  #FIXME not needed

# Commit the session to trigger LogicBank
try:
    session.commit()
except Exception as e:
    print(f"Error during commit: {e}")
finally:
    session.close()
