from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, DECIMAL, Date
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()

class Customer(Base):
    __tablename__ = 'customers'

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=True)
    balance = Column(DECIMAL, nullable=True)
    credit_limit = Column(DECIMAL, nullable=True)

class Order(Base):
    __tablename__ = 'orders'

    id = Column(Integer, primary_key=True)
    customer_id = Column(Integer, ForeignKey('customers.id'), nullable=True)
    notes = Column(String, nullable=True)

class Item(Base):
    __tablename__ = 'items'

    id = Column(Integer, primary_key=True)
    order_id = Column(Integer, ForeignKey('orders.id'), nullable=True)   
    product_id = Column(Integer, ForeignKey('products.id'), nullable=True)
    quantity = Column(Integer, nullable=True)
    amount = Column(DECIMAL, nullable=True)

class Product(Base):
    __tablename__ = 'products'

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=True)
    unit_price = Column(DECIMAL, nullable=True)

# Create the SQLite database
engine = create_engine('sqlite:///system/genai/temp/create_db_models.sqlite')
Base.metadata.create_all(engine)

# Insert sample data into the customers table
from sqlalchemy.orm import sessionmaker

Session = sessionmaker(bind=engine)
session = Session()

customer1 = Customer(name="John Doe", balance=1000.0, credit_limit=2000.0)
customer2 = Customer(name="Jane Smith", balance=1500.0, credit_limit=3000.0)

session.add_all([customer1, customer2])
session.commit()

# Insert sample data into the products table
product1 = Product(name="Product A", unit_price=10.0)
product2 = Product(name="Product B", unit_price=15.0)

session.add_all([product1, product2])
session.commit()

session.close()
