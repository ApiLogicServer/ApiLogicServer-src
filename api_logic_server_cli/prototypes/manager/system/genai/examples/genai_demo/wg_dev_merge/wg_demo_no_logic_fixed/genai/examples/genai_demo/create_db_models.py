from sqlalchemy.sql import func  # end imports from system/genai/create_db_models_inserts/create_db_models_prefix.py
from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, DateTime, Numeric, CheckConstraint
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime

# Initialize the base
Base = declarative_base()

# Define the models
class Customer(Base):
    __tablename__ = 'customers'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    balance = Column(Numeric, default=0)
    credit_limit = Column(Numeric, nullable=False)

class Order(Base):
    __tablename__ = 'orders'
    id = Column(Integer, primary_key=True, autoincrement=True)
    customer_id = Column(Integer, ForeignKey('customers.id'), nullable=False)
    date_shipped = Column(DateTime, nullable=True)
    amount_total = Column(Numeric, default=0)
    notes = Column(String, nullable=True)

class Product(Base):
    __tablename__ = 'products'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    unit_price = Column(Numeric, nullable=False)

class Item(Base):
    __tablename__ = 'items'
    id = Column(Integer, primary_key=True, autoincrement=True)
    order_id = Column(Integer, ForeignKey('orders.id'), nullable=False)
    product_id = Column(Integer, ForeignKey('products.id'), nullable=False)
    quantity = Column(Integer, nullable=False)
    unit_price = Column(Numeric, nullable=False)
    amount = Column(Numeric, default=0)

# Create an engine to the SQLite database
engine = create_engine('sqlite:///system/genai/temp/create_db_models.sqlite')

# Create all tables
Base.metadata.create_all(engine)

# Create a configured "Session" class
Session = sessionmaker(bind=engine)

# Create a Session
session = Session()

# Add some test data
# Customers
customer1 = Customer(name="John Doe", balance=100, credit_limit=500)
customer2 = Customer(name="Jane Smith", balance=150, credit_limit=300)
session.add(customer1)
session.add(customer2)
session.commit()

# Products
product1 = Product(name="Product A", unit_price=10)
product2 = Product(name="Product B", unit_price=20)
session.add(product1)
session.add(product2)
session.commit()

# Orders
order1 = Order(customer_id=customer1.id, date_shipped=None, amount_total=0, notes="First order")
order2 = Order(customer_id=customer2.id, date_shipped=None, amount_total=0, notes="Second order")
session.add(order1)
session.add(order2)
session.commit()

# Items
item1 = Item(order_id=order1.id, product_id=product1.id, quantity=3, unit_price=product1.unit_price, amount=3 * product1.unit_price)
item2 = Item(order_id=order1.id, product_id=product2.id, quantity=2, unit_price=product2.unit_price, amount=2 * product2.unit_price)
item3 = Item(order_id=order2.id, product_id=product1.id, quantity=5, unit_price=product1.unit_price, amount=5 * product1.unit_price)
session.add(item1)
session.add(item2)
session.add(item3)
session.commit()

# Update order amounts
order1.amount_total = item1.amount + item2.amount
order2.amount_total = item3.amount
session.commit()

# Update customer balances
customer1.balance = session.query(Order).filter(Order.customer_id == customer1.id, Order.date_shipped == None).with_entities(func.sum(Order.amount_total)).scalar()
customer2.balance = session.query(Order).filter(Order.customer_id == customer2.id, Order.date_shipped == None).with_entities(func.sum(Order.amount_total)).scalar()
session.commit()

# Close the session
session.close()
