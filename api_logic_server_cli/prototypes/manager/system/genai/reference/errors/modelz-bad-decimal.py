from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, DateTime, Boolean, Numeric, DateTime
from sqlalchemy.orm import sessionmaker, relationship, backref
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
import decimal

Base = declarative_base()


# Define the models
class Customer(Base):
    __tablename__ = 'customers'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    balance = Column(Numeric)
    creditLimit = Column(Numeric)

class Product(Base):
    __tablename__ = 'products'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    unitPrice = Column(Numeric)

class Order(Base):
    __tablename__ = 'orders'
    id = Column(Integer, primary_key=True)
    customerId = Column(Integer, ForeignKey('customers.id'))
    amountTotal = Column(Numeric)
    dateShipped = Column(DateTime)
    notes = Column(String)
    customer = relationship("Customer", backref=backref('orders', order_by=id))


class Item(Base):
    __tablename__ = 'items'
    id = Column(Integer, primary_key=True)
    orderId = Column(Integer, ForeignKey('orders.id'))
    productId = Column(Integer, ForeignKey('products.id'))
    quantity = Column(Integer)
    amount = Column(Numeric)
    order = relationship("Order", backref=backref('items', order_by=id))
    product = relationship("Product", backref=backref('products', order_by=id))

# Create SQLite database and session
engine = create_engine('sqlite:///system/genai/temp/create_db_models.sqlite')
session = sessionmaker()
session.configure(bind=engine)
Base.metadata.create_all(engine)
s = session()

# Insert customer and product data
cust1 = Customer(name='Customer 1', balance=decimal.DECIMAL(0.00), creditLimit=decimal.DECIMAL(1000.00))
cust2 = Customer(name='Customer 2', balance=decimal.DECIMAL(0.00), creditLimit=decimal.DECIMAL(2000.00))

prod1 = Product(name='Product 1', unitPrice=decimal.DECIMAL(10.00))
prod2 = Product(name='Product 2', unitPrice=decimal.DECIMAL(20.00))

s.add(cust1)
s.add(cust2)
s.add(prod1)
s.add(prod2)
s.commit()
