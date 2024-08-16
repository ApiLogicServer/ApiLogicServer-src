from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, DateTime, Numeric
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime, date

Base = declarative_base()

class Customer(Base):
    __tablename__ = 'customers'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    balance = Column(Numeric, nullable=True)
    credit_limit = Column(Numeric, nullable=True)

class Product(Base):
    __tablename__ = 'products'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    unit_price = Column(Numeric, nullable=False)

class Order(Base):
    __tablename__ = 'orders'
    id = Column(Integer, primary_key=True, autoincrement=True)
    customer_id = Column(Integer, ForeignKey('customers.id'), nullable=False)
    date_shipped = Column(DateTime, nullable=True)
    amount_total = Column(Numeric, nullable=True)
    notes = Column(String, nullable=True)

class Item(Base):
    __tablename__ = 'items'
    id = Column(Integer, primary_key=True, autoincrement=True)
    order_id = Column(Integer, ForeignKey('orders.id'), nullable=False)
    product_id = Column(Integer, ForeignKey('products.id'), nullable=False)
    quantity = Column(Integer, nullable=False)
    unit_price = Column(Numeric, nullable=False)
    amount = Column(Numeric, nullable=True)

engine = create_engine('sqlite:///system/genai/temp/model.sqlite')
Base.metadata.create_all(engine)

Session = sessionmaker(bind=engine)
session = Session()

# Add test customers
customer1 = Customer(name="John Doe", balance=0, credit_limit=1000)
customer2 = Customer(name="Jane Smith", balance=0, credit_limit=2000)
session.add(customer1)
session.add(customer2)
session.commit()

# Add products
product1 = Product(name="Widget", unit_price=10.00)
product2 = Product(name="Gadget", unit_price=25.00)
session.add(product1)
session.add(product2)
session.commit()

# Add an order with items for customer1
order1 = Order(customer_id=customer1.id, date_shipped=None, amount_total=0, notes="First order")
session.add(order1)
session.commit()

# Add items to this order
item1 = Item(order_id=order1.id, product_id=product1.id, quantity=3, unit_price=product1.unit_price, amount=0)
item2 = Item(order_id=order1.id, product_id=product2.id, quantity=2, unit_price=product2.unit_price, amount=0)

item1.amount = item1.quantity * item1.unit_price
item2.amount = item2.quantity * item2.unit_price

order1.amount_total = item1.amount + item2.amount
customer1.balance = order1.amount_total

session.add(item1)
session.add(item2)
session.commit()

# Repeat for another order and customer if needed...
