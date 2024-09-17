import decimal

import logging



logging.getLogger('sqlalchemy.engine.Engine').disabled = True  # remove for additional logging

import sqlalchemy



from sqlalchemy.sql import func  # end imports from system/genai/create_db_models_inserts/create_db_models_prefix.py



from sqlalchemy import create_engine, Column, Integer, String, DateTime, ForeignKey, Numeric, Sequence
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime

# Setup the database connection and Base class
engine = create_engine('sqlite:///system/genai/temp/create_db_models.sqlite')
Base = declarative_base()

class Customer(Base):
    """
    description: Table storing customer information.
    """
    __tablename__ = 'customers'
    
    id = Column(Integer, Sequence('customer_id_seq'), primary_key=True, autoincrement=True)
    name = Column(String, nullable=True)
    email = Column(String, nullable=True)

class Order(Base):
    """
    description: Table storing customer orders.
    """
    __tablename__ = 'orders'
    
    id = Column(Integer, Sequence('order_id_seq'), primary_key=True, autoincrement=True)
    customer_id = Column(Integer, ForeignKey('customers.id'))
    order_datetime = Column(DateTime, default=datetime.utcnow, nullable=True)
    amount = Column(Numeric, nullable=True)
    
    customer = relationship("Customer", back_populates="orders")
    details = relationship("OrderDetail", back_populates="order")

class Product(Base):
    """
    description: Table storing product information.
    """
    __tablename__ = 'products'
    
    id = Column(Integer, Sequence('product_id_seq'), primary_key=True, autoincrement=True)
    name = Column(String, nullable=True)
    price = Column(Numeric, nullable=True)

class OrderDetail(Base):
    """
    description: Table storing order detail information.
    """
    __tablename__ = 'order_details'
    
    id = Column(Integer, Sequence('order_detail_id_seq'), primary_key=True, autoincrement=True)
    order_id = Column(Integer, ForeignKey('orders.id'))
    product_id = Column(Integer, ForeignKey('products.id'))
    quantity = Column(Integer, nullable=True)
    price = Column(Numeric, nullable=True)
    
    order = relationship("Order", back_populates="details")
    product = relationship("Product")

Customer.orders = relationship("Order", order_by=Order.id, back_populates="customer")

# Create the tables in the database
Base.metadata.create_all(engine)

# Create a session to interact with the database
Session = sessionmaker(bind=engine)
session = Session()

# Add test data
customers = [
    Customer(name='John Doe', email='john.doe@example.com'),
    Customer(name='Jane Smith', email='jane.smith@example.com')
]
products = [
    Product(name='Product 1', price=10.00),
    Product(name='Product 2', price=20.00),
    Product(name='Product 3', price=15.00)
]
orders = [
    Order(customer_id=1, order_datetime=datetime(2022, 1, 1, 10, 0), amount=100.50),
    Order(customer_id=2, order_datetime=datetime(2022, 1, 2, 12, 30), amount=200.75),
    Order(customer_id=1, order_datetime=datetime(2022, 1, 3, 14, 45), amount=150.00)
]
order_details = [
    OrderDetail(order_id=1, product_id=1, quantity=3, price=30.00),
    OrderDetail(order_id=1, product_id=2, quantity=2, price=40.00),
    OrderDetail(order_id=2, product_id=2, quantity=5, price=100.00),
    OrderDetail(order_id=3, product_id=3, quantity=10, price=150.00)
]

session.add_all(customers)
session.add_all(products)
session.commit()  # commit customers and products first to generate their ids

session.add_all(orders)
session.commit()  # commit orders

session.add_all(order_details)
session.commit()

# Close the session
session.close()
