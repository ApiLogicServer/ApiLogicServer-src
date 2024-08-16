import os
import datetime
import decimal
from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, DateTime, Numeric
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship

# Define database path and Engine
db_path = 'system/genai/temp/model.sqlite'
os.makedirs(os.path.dirname(db_path), exist_ok=True)
engine = create_engine(f'sqlite:///{db_path}', echo=False)

# Create a base class for declarative class definitions
Base = declarative_base()

# Define Customer class
class Customer(Base):
    __tablename__ = 'customers'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    balance = Column(Numeric, nullable=False, default=decimal.Decimal('0.00'))  # Decimal type for balance
    credit_limit = Column(Numeric, nullable=False, default=decimal.Decimal('0.00'))  # Decimal type for credit limit

# Define Product class
class Product(Base):
    __tablename__ = 'products'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    unit_price = Column(Numeric, nullable=False, default=decimal.Decimal('0.00'))  # Decimal type for unit price

# Define Order class
class Order(Base):
    __tablename__ = 'orders'

    id = Column(Integer, primary_key=True, autoincrement=True)
    customer_id = Column(Integer, ForeignKey('customers.id'), nullable=False)
    date_created = Column(DateTime, nullable=False, default=datetime.datetime.utcnow)
    date_shipped = Column(DateTime, nullable=True)
    amount_total = Column(Numeric, nullable=False, default=decimal.Decimal('0.00'))  # Decimal type for total amount
    notes = Column(String)
    # customer = relationship('Customer', backref='orders')

# Define Item class
class Item(Base):
    __tablename__ = 'items'

    id = Column(Integer, primary_key=True, autoincrement=True)
    order_id = Column(Integer, ForeignKey('orders.id'), nullable=False)
    product_id = Column(Integer, ForeignKey('products.id'), nullable=False)
    quantity = Column(Integer, nullable=False, default=1)
    unit_price = Column(Numeric, nullable=False)
    amount = Column(Numeric, nullable=False, default=decimal.Decimal('0.00'))  # Decimal type for item amount
    # order = relationship('Order', backref='items')
    # product = relationship('Product')

def calculate_order_amount_total(order):
    return sum(item.amount for item in order.items)

def calculate_customer_balance(customer):
    return sum(order.amount_total for order in customer.orders if order.date_shipped is None)

# Create all tables
Base.metadata.create_all(engine)

# Create a session
Session = sessionmaker(bind=engine)
session = Session()

# Create some test data
customer1 = Customer(name='John Doe', balance=decimal.Decimal('0.00'), credit_limit=decimal.Decimal('500.00'))
session.add(customer1)

product1 = Product(name='Widget', unit_price=decimal.Decimal('10.00'))
product2 = Product(name='Gizmo', unit_price=decimal.Decimal('20.00'))
session.add(product1)
session.add(product2)

# Add an order for the customer
order1 = Order(customer=customer1, notes='First order')
session.add(order1)

# Add items to the order
item1 = Item(order=order1, product=product1, quantity=5, unit_price=product1.unit_price, amount=product1.unit_price * 5)
item2 = Item(order=order1, product=product2, quantity=2, unit_price=product2.unit_price, amount=product2.unit_price * 2)
session.add(item1)
session.add(item2)

# Calculate the order total and update the order
order1.amount_total = calculate_order_amount_total(order1)

# Update customer balance
customer1.balance = calculate_customer_balance(customer1)

# Commit the changes to the database
session.commit()

# Close the session
session.close()
