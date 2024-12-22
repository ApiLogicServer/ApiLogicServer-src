from sqlalchemy import create_engine, Column, Integer, String, Float, ForeignKey, DateTime, Numeric
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()

class Customer(Base):
    __tablename__ = 'customers'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    balance = Column(Numeric(precision=10, scale=2))
    credit_limit = Column(Numeric(precision=10, scale=2))
    
class Order(Base):
    __tablename__ = 'orders'
    id = Column(Integer, primary_key=True)
    customer_id = Column(Integer, ForeignKey('customers.id'))
    notes = Column(String)
    amount_total = Column(Numeric(precision=10, scale=2))
    
class Item(Base):
    __tablename__ = 'items'
    id = Column(Integer, primary_key=True)
    order_id = Column(Integer, ForeignKey('orders.id'))
    product_id = Column(Integer, ForeignKey('products.id'))
    quantity = Column(Integer)
    amount = Column(Numeric(precision=10, scale=2))
    
class Product(Base):
    __tablename__ = 'products'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    description = Column(String)
    unit_price = Column(Numeric(precision=10, scale=2))

engine = create_engine('sqlite:///system/genai/temp/create_db_models.sqlite') # create sqlite db

Base.metadata.create_all(engine) # create tables in the database

# Insert some sample data
# Note: Remember that you need to create a session and add these objects to the session to actually insert them into the database
customer1 = Customer(name='John Doe', balance=1000.00, credit_limit=2000.00)
customer2 = Customer(name='Jane Smith', balance=1500.00, credit_limit=3000.00)

product1 = Product(name='Product A', description='Description A', unit_price=50.00)
product2 = Product(name='Product B', description='Description B', unit_price=75.00)
