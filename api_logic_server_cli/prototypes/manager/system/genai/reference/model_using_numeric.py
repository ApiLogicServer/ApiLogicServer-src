from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, Numeric, Date
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()

class Customer(Base):
    __tablename__ = 'customers'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=True)
    balance = Column(Numeric(precision=10, scale=2), nullable=True)
    credit_limit = Column(Numeric(precision=10, scale=2), nullable=True)

class Product(Base):
    __tablename__ = 'products'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=True)
    unit_price = Column(Numeric(precision=10, scale=2), nullable=True)

class Order(Base):
    __tablename__ = 'orders'

    id = Column(Integer, primary_key=True, autoincrement=True)
    customer_id = Column(Integer, ForeignKey('customers.id'), nullable=True)
    date_shipped = Column(Date, nullable=True)
    notes = Column(String, nullable=True)
    amount_total = Column(Numeric(precision=10, scale=2), nullable=True)
    customer = relationship('Customer', backref='orders')

class Item(Base):
    __tablename__ = 'items'

    id = Column(Integer, primary_key=True, autoincrement=True)
    order_id = Column(Integer, ForeignKey('orders.id'), nullable=True)
    product_id = Column(Integer, ForeignKey('products.id'), nullable=True)
    quantity = Column(Integer, nullable=True)
    amount = Column(Numeric(precision=10, scale=2), nullable=True)

    order = relationship('Order', backref='items')
    product = relationship('Product', backref='items')

# Create the SQLite database engine
engine = create_engine('sqlite:///system/genai/temp/create_db_models.sqlite', echo=True)

# Create the tables
Base.metadata.create_all(engine)
