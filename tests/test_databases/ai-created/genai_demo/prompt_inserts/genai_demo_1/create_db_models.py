from sqlalchemy import create_engine, Column, Integer, String, DateTime, ForeignKey, DECIMAL, Table, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
import datetime

Base = declarative_base()

# Define the Customer model
class Customer(Base):
    __tablename__ = 'customers'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    balance = Column(DECIMAL(10, 2), nullable=True)
    credit_limit = Column(DECIMAL(10, 2), nullable=False)

# Define the Product model
class Product(Base):
    __tablename__ = 'products'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    unit_price = Column(DECIMAL(10, 2), nullable=False)

# Define the Order model
class Order(Base):
    __tablename__ = 'orders'
    id = Column(Integer, primary_key=True, autoincrement=True)
    customer_id = Column(Integer, ForeignKey('customers.id'), nullable=False)
    date_shipped = Column(DateTime, nullable=True)
    amount_total = Column(DECIMAL(10, 2), nullable=True)
    notes = Column(String, nullable=True)

# Define the Item model
class Item(Base):
    __tablename__ = 'items'
    id = Column(Integer, primary_key=True, autoincrement=True)
    order_id = Column(Integer, ForeignKey('orders.id'), nullable=False)
    product_id = Column(Integer, ForeignKey('products.id'), nullable=False)
    quantity = Column(Integer, nullable=False)
    unit_price = Column(DECIMAL(10, 2), nullable=False)
    amount = Column(DECIMAL(10, 2), nullable=True)

# Create engine and a session
engine = create_engine('sqlite:///system/genai/temp/create_db_models.sqlite')
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
session = Session()

# Insert test data
def populate_test_data(session):
    # Create customers
    customer1 = Customer(name="John Doe", balance=0.00, credit_limit=500.00)
    customer2 = Customer(name="Jane Smith", balance=0.00, credit_limit=1000.00)
    session.add_all([customer1, customer2])
    session.commit()
    
    # Create products
    product1 = Product(name="Widget A", unit_price=10.00)
    product2 = Product(name="Widget B", unit_price=25.00)
    session.add_all([product1, product2])
    session.commit()
    
    # Create an order
    order1 = Order(customer_id=customer1.id, date_shipped=None, amount_total=0.00, notes="First order")
    session.add(order1)
    session.commit()
    
    # Create items for the order
    item1 = Item(order_id=order1.id, product_id=product1.id, quantity=2, unit_price=product1.unit_price)
    item2 = Item(order_id=order1.id, product_id=product2.id, quantity=1, unit_price=product2.unit_price)
    session.add_all([item1, item2])
    session.commit()

    # Update item amounts and order total
    item1.amount = item1.quantity * item1.unit_price
    item2.amount = item2.quantity * item2.unit_price
    session.commit()
    
    order1.amount_total = item1.amount + item2.amount
    session.commit()

    # Update customer balance based on unshipped orders
    customer1.balance = session.query(Order).filter_by(customer_id=customer1.id, date_shipped=None).with_entities(func.sum(Order.amount_total)).scalar()
    session.commit()

# Populating test data
populate_test_data(session)

# Querying the data to verify
for customer in session.query(Customer).all():
    print(f"Customer: {customer.name}, Balance: {customer.balance}, Credit Limit: {customer.credit_limit}")

for order in session.query(Order).all():
    print(f"Order ID: {order.id}, Customer ID: {order.customer_id}, Amount Total: {order.amount_total}, Notes: {order.notes}")

for item in session.query(Item).all():
    print(f"Item ID: {item.id}, Order ID: {item.order_id}, Product ID: {item.product_id}, Quantity: {item.quantity}, Unit Price: {item.unit_price}, Amount: {item.amount}")

# Closing the session
session.close()
