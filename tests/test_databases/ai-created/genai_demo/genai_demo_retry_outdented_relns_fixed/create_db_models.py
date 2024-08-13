from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, DateTime, DECIMAL, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy.sql import func

import os

# Define base class
Base = declarative_base()

# Define Customer class
class Customer(Base):
    __tablename__ = 'customers'
    
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    balance = Column(DECIMAL, nullable=True)  # Assume null balance is allowed
    credit_limit = Column(DECIMAL, nullable=True)

# Define Product class
class Product(Base):
    __tablename__ = 'products'
    
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    unit_price = Column(DECIMAL, nullable=False)

# Define Order class
class Order(Base):
    __tablename__ = 'orders'
    
    id = Column(Integer, primary_key=True)
    customer_id = Column(Integer, ForeignKey('customers.id'))
    amount_total = Column(DECIMAL, nullable=True)
    date_shipped = Column(DateTime, nullable=True)
    notes = Column(Text, nullable=True)
    
    # customer = relationship('Customer', back_populates='orders')

# Define Item class
class Item(Base):
    __tablename__ = 'items'
    
    id = Column(Integer, primary_key=True)
    order_id = Column(Integer, ForeignKey('orders.id'))
    product_id = Column(Integer, ForeignKey('products.id'))
    quantity = Column(Integer, nullable=False)
    unit_price = Column(DECIMAL, nullable=False)
    amount = Column(DECIMAL, nullable=True)
    
    # order = relationship('Order', back_populates='items')
    # product = relationship('Product')

# Customer.orders = relationship('Order', order_by=Order.id, back_populates='customer')
# Order.items = relationship('Item', order_by=Item.id, back_populates='order')

# Create database file and engine
os.makedirs('system/genai/temp', exist_ok=True)
engine = create_engine('sqlite:///system/genai/temp/model.sqlite')
Base.metadata.create_all(engine)

# Create a session
Session = sessionmaker(bind=engine)
session = Session()

# Add some customer data
customer1 = Customer(name='Customer 1', balance=0, credit_limit=1000)
customer2 = Customer(name='Customer 2', balance=0, credit_limit=2000)

# Add some product data
product1 = Product(name='Product 1', unit_price=10.99)
product2 = Product(name='Product 2', unit_price=15.50)

# Add data to session and commit
session.add_all([customer1, customer2, product1, product2])
session.commit()

# Close the session
session.close()
