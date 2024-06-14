from sqlalchemy import create_engine, Column, DECIMAL, DateTime, ForeignKey, Integer, Text, text
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()  # ed. Used for: 3. New Database - using Copilot (Signup optional)

class Customer(Base):
    __tablename__ = 'Customers'

    CustomerID = Column(Integer, primary_key=True)
    CustomerName = Column(Text, nullable=False)
    Address = Column(Text)
    Phone = Column(Text)
    Balance : DECIMAL = Column(DECIMAL(10, 2))
    CreditLimit : DECIMAL = Column(DECIMAL(10, 2), nullable=False)

class Product(Base):
    __tablename__ = 'Products'

    ProductID = Column(Integer, primary_key=True)
    ProductName = Column(Text, nullable=False)
    UnitPrice : DECIMAL = Column(DECIMAL(10, 2), nullable=False)

class Order(Base):
    __tablename__ = 'Orders'

    OrderID = Column(Integer, primary_key=True)
    CustomerID = Column(ForeignKey('Customers.CustomerID'))
    OrderDate = Column(DateTime, server_default=text("CURRENT_TIMESTAMP"))
    Notes = Column(Text)
    ShipDate = Column(DateTime)
    AmountTotal : DECIMAL = Column(DECIMAL(10, 2))

class Item(Base):
    __tablename__ = 'Items'

    ItemID = Column(Integer, primary_key=True)
    OrderID = Column(ForeignKey('Orders.OrderID'))
    ProductID = Column(ForeignKey('Products.ProductID'))
    Quantity = Column(Integer, nullable=False)
    UnitPrice : DECIMAL = Column(DECIMAL(10, 2))
    Amount : DECIMAL = Column(DECIMAL(10, 2))

engine = create_engine('sqlite:///sample_ai.sqlite')
Base.metadata.create_all(engine)

Session = sessionmaker(bind=engine)
session = Session()

# Add a few rows of customer and product data
customer1 = Customer(CustomerName='Customer 1', Balance=1000, CreditLimit=2000)
product1 = Product(ProductName='Product 1', UnitPrice=50)

session.add(customer1)
session.add(product1)
session.commit()