import os
from datetime import datetime
import decimal
from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, DateTime, Numeric, null
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship

# Define the database path and create the engine
db_path = 'system/genai/temp/model.sqlite'
if not os.path.exists(os.path.dirname(db_path)):
    os.makedirs(os.path.dirname(db_path))
engine = create_engine(f'sqlite:///{db_path}')

# Define the base class for all models
Base = declarative_base()

class Product(Base):
    __tablename__ = 'products'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    unit_price = Column(Numeric, nullable=False)


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
    notes = Column(String, nullable=True)
    amount_total = Column(Numeric, default=0)

    # customer = relationship("Customer", back_populates="orders")


class Item(Base):
    __tablename__ = 'items'
    id = Column(Integer, primary_key=True, autoincrement=True)
    order_id = Column(Integer, ForeignKey('orders.id'), nullable=False)
    product_id = Column(Integer, ForeignKey('products.id'), nullable=False)
    quantity = Column(Integer, nullable=False)
    unit_price = Column(Numeric, nullable=False)
    amount = Column(Numeric, nullable=False, default=0)

    # order = relationship("Order", back_populates="items")
    # product = relationship("Product")

# Customer.orders = relationship("Order", order_by=Order.id, back_populates="customer")
# Order.items = relationship("Item", order_by=Item.id, back_populates="order")

# Create all tables
Base.metadata.create_all(engine)
def check_credit(session, customer):
    # Customer.balance <= credit_limit
    if customer.balance > customer.credit_limit:
        raise ValueError(f"Customer {customer.name}'s balance exceeds credit limit.")

    # Customer.balance = Sum(Order.amount_total where date_shipped is null)
    pending_orders_total = session.query(Order).filter(Order.customer_id == customer.id, Order.date_shipped == null()).with_entities(func.sum(Order.amount_total)).scalar() or 0
    if customer.balance != pending_orders_total:
        raise ValueError(f"Customer {customer.name}'s balance does not match the sum of pending orders.")

def calculate_order_total(session, order):
    # Order.amount_total = Sum(Item.amount)
    total = session.query(Item).filter(Item.order_id == order.id).with_entities(func.sum(Item.amount)).scalar() or 0
    order.amount_total = total

def calculate_item_amount(item):
    # Item.amount = quantity * unit_price
    item.amount = item.quantity * item.unit_price

# Create a new session
Session = sessionmaker(bind=engine)
session = Session()
# Create Products
product1 = Product(name="Product 1", unit_price=decimal.Decimal('100.00'))
product2 = Product(name="Product 2", unit_price=decimal.Decimal('50.00'))

# Create a Customer
customer = Customer(name="Customer 1", balance=decimal.Decimal('0.00'), credit_limit=decimal.Decimal('1000.00'))

# Add to session
session.add_all([product1, product2, customer])
session.commit()

# Create Orders and Items
order = Order(customer_id=customer.id, date_shipped=None, notes="Order 1")
item1 = Item(order_id=order.id, product_id=product1.id, quantity=2, unit_price=product1.unit_price)
item2 = Item(order_id=order.id, product_id=product2.id, quantity=1, unit_price=product2.unit_price)

# Calculate amounts for items and order
calculate_item_amount(item1)
calculate_item_amount(item2)
order.items.append(item1)
order.items.append(item2)
calculate_order_total(session, order)

# Add order to session and adjust customer balance
customer.orders.append(order)
check_credit(session, customer)
customer.balance += order.amount_total

# Commit all changes
session.commit()
