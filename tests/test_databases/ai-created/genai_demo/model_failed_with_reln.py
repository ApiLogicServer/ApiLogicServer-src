from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, Date, Numeric, Text, DateTime
from sqlalchemy.orm import relationship, sessionmaker, declarative_base
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.sql import func

Base = declarative_base()

class Customer(Base):
    __tablename__ = 'customers'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    balance = Column(Numeric, default=0)
    credit_limit = Column(Numeric, nullable=False)
    
    # orders = relationship('Order', back_populates='customer')

class Order(Base):
    __tablename__ = 'orders'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    customer_id = Column(Integer, ForeignKey('customers.id'), nullable=False)
    amount_total = Column(Numeric, default=0)
    date_shipped = Column(DateTime, nullable=True)
    notes = Column(Text, nullable=True)
    
    # customer = relationship('Customer', back_populates='orders')
    # items = relationship('Item', back_populates='order')

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
    
    # order = relationship('Order', back_populates='items')
    # product = relationship('Product')

# Create SQLite database
engine = create_engine('sqlite:///system/genai/temp/model.sqlite')
Base.metadata.create_all(engine)

# Create a new session
Session = sessionmaker(bind=engine)
session = Session()

# Add initial data for customers and products
customer1 = Customer(name='Customer One', balance=0, credit_limit=1000)
customer2 = Customer(name='Customer Two', balance=0, credit_limit=2000)
product1 = Product(name='Product A', unit_price=10)
product2 = Product(name='Product B', unit_price=20)

session.add_all([customer1, customer2, product1, product2])
session.commit()

# Enforcing business rules via Python logic
def calculate_item_amount(item):
    item.unit_price = item.product.unit_price  # Copy unit_price from Product
    item.amount = item.quantity * item.unit_price

def calculate_order_total(order):
    order.amount_total = sum(item.amount for item in order.items)

def check_customer_credit(customer):
    balance = sum(order.amount_total for order in customer.orders if order.date_shipped is None)
    if balance > customer.credit_limit:
        raise ValueError("Customer balance exceeds credit limit.")
    customer.balance = balance

# Example of adding an order and items
def add_order_with_items(customer, product_quantities, notes=''):
    order = Order(customer=customer, notes=notes)
    
    for product, quantity in product_quantities.items():
        item = Item(order=order, product=product, quantity=quantity)
        calculate_item_amount(item)
        session.add(item)
    
    calculate_order_total(order)
    session.add(order)

    check_customer_credit(customer)

    session.commit()

# Example usage
try:
    add_order_with_items(customer1, {product1: 5, product2: 2}, notes='First order')
except ValueError as e:
    print(e)

# Make sure to close session
session.close()
