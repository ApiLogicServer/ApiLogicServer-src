from sqlalchemy import create_engine, ForeignKey, Column, Integer, String, Float, DateTime, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()

class Customer(Base):
    __tablename__ = 'customers'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    credit_limit = Column(Float, nullable=True)
    balance = Column(Float, nullable=True)

    orders = relationship("Order", back_populates="customer")

class Product(Base):
    __tablename__ = 'products'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    unit_price = Column(Float, nullable=True)

    items = relationship("Item", back_populates="product")

class Order(Base):
    __tablename__ = 'orders'

    id = Column(Integer, primary_key=True)
    customer_id = Column(Integer, ForeignKey('customers.id'))
    notes = Column(Text)

    customer = relationship("Customer", back_populates="orders")

    items = relationship("Item", back_populates="order")

class Item(Base):
    __tablename__ = 'items'

    id = Column(Integer, primary_key=True)
    quantity = Column(Integer)
    product_id = Column(Integer, ForeignKey('products.id'))
    unit_price = Column(Float, nullable=True)
    order_id = Column(Integer, ForeignKey('orders.id'))

    product = relationship("Product", back_populates="items")
    order = relationship("Order", back_populates="items")

# Create the SQLite database
engine = create_engine('sqlite:///genai_demo.sqlite')
Base.metadata.create_all(engine)
from sqlalchemy.orm import sessionmaker

Session = sessionmaker(bind=engine)
session = Session()

# Add sample customers
customer1 = Customer(name='John Doe', credit_limit=1000.0, balance=500.0)
customer2 = Customer(name='Jane Smith', credit_limit=2000.0, balance=1500.0)

# Add sample products
product1 = Product(name='Product A', unit_price=10.0)
product2 = Product(name='Product B', unit_price=20.0)

session.add_all([customer1, customer2, product1, product2])
session.commit()

session.close()
