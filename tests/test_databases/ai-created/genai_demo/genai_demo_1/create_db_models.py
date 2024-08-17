import sqlalchemy as sa
from sqlalchemy import create_engine, Column, Integer, String, DECIMAL, ForeignKey, Date, Text
from sqlalchemy.orm import relationship, sessionmaker, declarative_base
from sqlalchemy.ext.declarative import DeclarativeMeta

# Create engine and base class
engine = create_engine('sqlite:///system/genai/temp/create_db_models.sqlite', echo=True)
Base: DeclarativeMeta = declarative_base()

class Customer(Base):
    __tablename__ = 'customers'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=True)  # Allowing nulls as per instructions
    balance = Column(DECIMAL, nullable=True)
    credit_limit = Column(DECIMAL, nullable=True)
    
    # orders = relationship("Order", back_populates="customer")

class Product(Base):
    __tablename__ = 'products'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=True)  # Allowing nulls as per instructions
    unit_price = Column(DECIMAL, nullable=True)

class Order(Base):
    __tablename__ = 'orders'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    customer_id = Column(Integer, ForeignKey('customers.id'))
    date_shipped = Column(Date, nullable=True)
    notes = Column(Text, nullable=True)  # Adding the notes field
    amount_total = Column(DECIMAL, nullable=True)
    
    # items = relationship("Item", back_populates="order")
    # customer = relationship("Customer", back_populates="orders")

class Item(Base):
    __tablename__ = 'items'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    order_id = Column(Integer, ForeignKey('orders.id'))
    product_id = Column(Integer, ForeignKey('products.id'))
    quantity = Column(Integer, nullable=True)
    unit_price = Column(DECIMAL, nullable=True)
    amount = Column(DECIMAL, nullable=True)
    
    # product = relationship("Product")
    # order = relationship("Order", back_populates="items")

# Create all tables
Base.metadata.create_all(engine)

# Create a session
Session = sessionmaker(bind=engine)
session = Session()

# Adding initial customer data
customers = [
    Customer(name="John Doe", balance=0, credit_limit=1000),
    Customer(name="Jane Doe", balance=0, credit_limit=1500),
]

# Adding initial product data
products = [
    Product(name="Widget", unit_price=10.99),
    Product(name="Gadget", unit_price=15.99),
]

session.add_all(customers)
session.add_all(products)
session.commit()

# Business logic checks

# Here we need to ensure the correctness of certain requirements, we can use ORM events.

def check_balance(customer):
    # Assuming Customer.balance should equal sum of the amount totals of unshipped orders
    unshipped_orders = session.query(Order).filter(Order.customer_id == customer.id, Order.date_shipped == None)
    balance_calculated = sum(order.amount_total or 0 for order in unshipped_orders)
    if customer.balance != balance_calculated:
        raise ValueError("Customer balance does not match the sum of amounts of unshipped orders.")

def check_credit_limit(customer):
    if customer.balance > customer.credit_limit:
        raise ValueError("Customer balance exceeds their credit limit.")

def check_order_amount_total(order):
    items = session.query(Item).filter(Item.order_id == order.id)
    amount_total_calculated = sum(item.amount for item in items)
    if order.amount_total != amount_total_calculated:
        raise ValueError("Order's total amount does not match the sum of its items' amounts.")

def check_item_amount(item):
    product = session.query(Product).filter(Product.id == item.product_id).first()
    item.unit_price = product.unit_price
    amount_calculated = item.quantity * item.unit_price
    if item.amount != amount_calculated:
        raise ValueError("Item's amount does not match its calculated value (quantity times unit price).")

sa.event.listen(Customer, 'before_update', check_balance)
sa.event.listen(Customer, 'before_update', check_credit_limit)
sa.event.listen(Order, 'before_update', check_order_amount_total)
sa.event.listen(Item, 'before_update', check_item_amount)

print("Database and schema created successfully!")
