from sqlalchemy import create_engine, Column, Integer, String, Numeric, ForeignKey, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from decimal import DECIMAL

# Define the SQLite database path
DATABASE_URI = 'sqlite:///system/genai/temp/model.sqlite'
Base = declarative_base()

# Define Customer table
class Customer(Base):
    __tablename__ = 'customers'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=True)
    balance = Column(Numeric, nullable=True)
    credit_limit = Column(Numeric, nullable=True)
    # orders = relationship("Order", back_populates="customer")

# Define Product table
class Product(Base):
    __tablename__ = 'products'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=True)
    unit_price = Column(Numeric, nullable=True)
    # items = relationship("Item", back_populates="product")

# Define Order table
class Order(Base):
    __tablename__ = 'orders'
    id = Column(Integer, primary_key=True, autoincrement=True)
    customer_id = Column(Integer, ForeignKey('customers.id'))
    amount_total = Column(Numeric, nullable=True)
    date_shipped = Column(DateTime, nullable=True)
    notes = Column(String, nullable=True)
    # customer = relationship("Customer", back_populates="orders")
    # items = relationship("Item", back_populates="order")

# Define Item table
class Item(Base):
    __tablename__ = 'items'
    id = Column(Integer, primary_key=True, autoincrement=True)
    order_id = Column(Integer, ForeignKey('orders.id'))
    product_id = Column(Integer, ForeignKey('products.id'))
    quantity = Column(Integer, nullable=True)
    unit_price = Column(Numeric, nullable=True)
    amount = Column(Numeric, nullable=True)
    # order = relationship("Order", back_populates="items")
    # product = relationship("Product", back_populates="items")

# Create the SQLite database
engine = create_engine(DATABASE_URI)
Base.metadata.create_all(engine)

# Create a new session
Session = sessionmaker(bind=engine)
session = Session()

# Add some initial rows for Customer and Product data
customers = [
    Customer(name="Alice", balance=DECIMAL('200.00'), credit_limit=DECIMAL('500.00')),
    Customer(name="Bob", balance=DECIMAL('300.00'), credit_limit=DECIMAL('600.00')),
]

products = [
    Product(name="Laptop", unit_price=DECIMAL('800.00')),
    Product(name="Smartphone", unit_price=DECIMAL('400.00')),
]

session.add_all(customers)
session.add_all(products)
session.commit()

print("Database created and initial data inserted successfully.")
