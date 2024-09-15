import decimal
import logging

"""
logging.basicConfig()
sa_e = logging.getLogger('sqlalchemy.engine.base.Engine')
sa_e.setLevel(logging.ERROR)

sa = logging.getLogger('sqlalchemy')
sa.setLevel(logging.ERROR)
"""

logging.getLogger('sqlalchemy.engine.Engine').disabled = True  # drive a stake throug its heart
import sqlalchemy

from sqlalchemy.sql import func  # end imports from system/genai/create_db_models_inserts/create_db_models_prefix.py
import os
from datetime import datetime
import decimal
from sqlalchemy import create_engine, Column, Integer, String, DateTime, ForeignKey, DECIMAL
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship

# Create SQLite database
db_path = 'system/genai/temp/new_create_db_models.sqlite'
os.makedirs(os.path.dirname(db_path), exist_ok=True)
engine = create_engine(f'sqlite:///{db_path}', echo=True)

# Base = declarative_base()
Base = sqlalchemy.orm.declarative_base()

class Customer(Base):
    """
    description: Table for storing customer information
    """
    __tablename__ = 'customers'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=True)
    email = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class Order(Base):
    """
    description: Table for storing order information
    """
    __tablename__ = 'orders'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    customer_id = Column(Integer, ForeignKey('customers.id'), nullable=True)
    amount = Column(DECIMAL(10, 2), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    customer = relationship('Customer')

class Product(Base):
    """
    description: Table for storing product information
    """
    __tablename__ = 'products'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=True)
    price = Column(DECIMAL(10, 2), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class OrderDetail(Base):
    """
    description: Table for storing order details information
    """
    __tablename__ = 'order_details'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    order_id = Column(Integer, ForeignKey('orders.id'), nullable=True)
    product_id = Column(Integer, ForeignKey('products.id'), nullable=True)
    quantity = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    order = relationship('Order')
    product = relationship('Product')

# Create tables
Base.metadata.create_all(engine)

# Create a new session
Session = sessionmaker(bind=engine)
session = Session()

# Adding test data
new_customer = Customer(name="John Doe", email="john.doe@example.com")
new_order = Order(customer_id=1, amount=decimal.Decimal('199.99'))
new_product1 = Product(name="Widget", price=decimal.Decimal('49.99'))
new_product2 = Product(name="Gadget", price=decimal.Decimal('99.99'))
new_order_detail1 = OrderDetail(order_id=1, product_id=1, quantity=2)  # 2 Widgets
new_order_detail2 = OrderDetail(order_id=1, product_id=2, quantity=1)  # 1 Gadget

session.add(new_customer)
session.add(new_order)
session.add(new_product1)
session.add(new_product2)
session.add(new_order_detail1)
session.add(new_order_detail2)
session.commit()

# Query data for verification
customers = session.query(Customer).all()
orders = session.query(Order).all()
products = session.query(Product).all()
order_details = session.query(OrderDetail).all()

"""
print("Customers:", customers)
print("Orders:", orders)
print("Products:", products)
print("OrderDetails:", order_details)
"""

# Close the session
session.close()
