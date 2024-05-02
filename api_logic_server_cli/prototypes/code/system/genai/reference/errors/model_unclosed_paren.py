from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, Numeric, Date
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from decimal import DECIMAL  # decimal; see also l. 42

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
    customer = relationship('Customer', backref='orders')
    notes = Column(String)
    date_shipped = Column(Date)

class Product(Base):
    __tablename__ = 'products'
    
    id = Column(Integer, primary_key=True)
    name = Column(String)
    unit_price = Column(Numeric(precision=10, scale=2))

class Item(Base):
    __tablename__ = 'items'
    
    id = Column(Integer, primary_key=True)
    order_id = Column(Integer, ForeignKey('orders.id'))
    order = relationship('Order', backref='items')
    product_id = Column(Integer, ForeignKey('products.id'))
    product = relationship('Product', backref='items')
    quantity = Column(Integer)
    amount = Column(Numeric(precision=10, scale=2))
    unit_price = Column(Numeric(precision=10, scale=2)

# Create the database engine
engine = create_engine('postgresql://postgres:p@localhost/genai_demo')

# Create tables in the database
Base.metadata.create_all(engine)

# Create a session
Session = sessionmaker(bind=engine)
session = Session()

# Add sample data
customer1 = Customer(name='John Doe', balance=DECIMAL('1000.00'), credit_limit=DECIMAL('5000.00'))
customer2 = Customer(name='Jane Smith', balance=DECIMAL('1500.00'), credit_limit=DECIMAL('2000.00'))

product1 = Product(name='Product A', unit_price=DECIMAL('25.50'))
product2 = Product(name='Product B', unit_price=DECIMAL('15.75'))

session.add_all([customer1, customer2, product1, product2])
session.commit()
