import decimal

from sqlalchemy.sql import func  # end imports from system/genai/create_db_models_inserts/create_db_models_prefix.py
from sqlalchemy import create_engine, Column, Integer, String, DECIMAL, DateTime, ForeignKey, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import datetime
import decimal

Base = declarative_base()
engine = create_engine('sqlite:///system/genai/temp/create_db_models.sqlite', echo=True)  

class CustomerAccount(Base):
    """description: Table to store customer account information"""
    __tablename__ = 'customer_accounts'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    balance = Column(DECIMAL(10, 2), nullable=True, default=decimal.Decimal('0.00'))
    credit_limit = Column(DECIMAL(10, 2), nullable=False)

class Product(Base):
    """description: Table to store product information"""
    __tablename__ = 'products'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    unit_price = Column(DECIMAL(10, 2), nullable=False)

class SalesRep(Base):
    """description: Table to store sales representative information"""
    __tablename__ = 'sales_reps'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)

class Order(Base):
    """description: Table to store order information"""
    __tablename__ = 'orders'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    customer_id = Column(Integer, ForeignKey('customer_accounts.id'), nullable=False)
    salesrep_id = Column(Integer, ForeignKey('sales_reps.id'), nullable=False)
    date_shipped = Column(DateTime, nullable=True)
    notes = Column(String, nullable=True)
    
    @property
    def amount_total(self):
        # Calculated as the sum of related items' amounts
        return sum(item.amount for item in self.items)

class Item(Base):
    """description: Table to store order item information"""
    __tablename__ = 'items'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    order_id = Column(Integer, ForeignKey('orders.id'), nullable=False)
    product_id = Column(Integer, ForeignKey('products.id'), nullable=False)
    quantity = Column(Integer, nullable=False)
    unit_price = Column(DECIMAL(10, 2), nullable=False)
    
    @property
    def amount(self):
        # Calculated as quantity times unit_price
        return self.quantity * self.unit_price

# Create the database tables
Base.metadata.create_all(engine)

Session = sessionmaker(bind=engine)
session = Session()

# Insert test data
product1 = Product(name='Product A', unit_price=decimal.Decimal('10.00'))
product2 = Product(name='Product B', unit_price=decimal.Decimal('20.00'))
session.add(product1)
session.add(product2)

customer1 = CustomerAccount(name='Customer A', balance=decimal.Decimal('0.00'), credit_limit=decimal.Decimal('100.00'))
customer2 = CustomerAccount(name='Customer B', balance=decimal.Decimal('0.00'), credit_limit=decimal.Decimal('200.00'))
session.add(customer1)
session.add(customer2)
session.commit()

salesrep1 = SalesRep(name='SalesRep A')
salesrep2 = SalesRep(name='SalesRep B')
session.add(salesrep1)
session.add(salesrep2)
session.commit()

order1 = Order(customer_id=customer1.id, salesrep_id=salesrep1.id, date_shipped=None, notes='First order')
order2 = Order(customer_id=customer2.id, salesrep_id=salesrep2.id, date_shipped=datetime.datetime.now(), notes='Second order')
session.add(order1)
session.add(order2)
session.commit()

item1 = Item(order_id=order1.id, product_id=product1.id, quantity=2, unit_price=product1.unit_price)
item2 = Item(order_id=order1.id, product_id=product2.id, quantity=1, unit_price=product2.unit_price)
item3 = Item(order_id=order2.id, product_id=product1.id, quantity=3, unit_price=product1.unit_price)
session.add(item1)
session.add(item2)
session.add(item3)
session.commit()

# Update the balance for each customer
for customer in session.query(CustomerAccount).all():
    customer.balance = session.query(func.sum(Item.unit_price * Item.quantity)).\
            join(Order, Item.order_id == Order.id).\
            filter(Order.customer_id == customer.id, Order.date_shipped == None).scalar() or Decimal('0.00')
    session.commit()

session.close()
