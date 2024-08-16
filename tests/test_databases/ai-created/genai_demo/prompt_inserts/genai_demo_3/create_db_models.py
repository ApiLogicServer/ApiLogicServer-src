from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, DateTime, Numeric, CheckConstraint, func
from sqlalchemy.orm import declarative_base, sessionmaker, relationship
from sqlalchemy.ext.declarative import declared_attr
from datetime import datetime

Base = declarative_base()

class Customer(Base):
    __tablename__ = 'customers'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    balance = Column(Numeric, nullable=False, default=0)
    credit_limit = Column(Numeric, nullable=False, default=1000)

class Product(Base):
    __tablename__ = 'products'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    unit_price = Column(Numeric, nullable=False)

class Order(Base):
    __tablename__ = 'orders'

    id = Column(Integer, primary_key=True, autoincrement=True)
    customer_id = Column(Integer, ForeignKey('customers.id'), nullable=False)
    date_created = Column(DateTime, default=datetime.utcnow, nullable=False)
    date_shipped = Column(DateTime, nullable=True)
    notes = Column(String, nullable=True)
    amount_total = Column(Numeric, nullable=False, default=0)
    
    # customer = relationship("Customer", back_populates="orders")

# Customer.orders = relationship("Order", order_by=Order.id, back_populates="customer")

class Item(Base):
    __tablename__ = 'items'

    id = Column(Integer, primary_key=True, autoincrement=True)
    order_id = Column(Integer, ForeignKey('orders.id'), nullable=False)
    product_id = Column(Integer, ForeignKey('products.id'), nullable=False)
    quantity = Column(Integer, nullable=False, default=1)
    unit_price = Column(Numeric, nullable=False)
    amount = Column(Numeric, nullable=False, default=0)
    
    # order = relationship("Order", back_populates="items")
    # product = relationship("Product", back_populates="items")

# Order.items = relationship("Item", order_by=Item.id, back_populates="order")
# Product.items = relationship("Item", order_by=Item.id, back_populates="product")

def main():
    # Create an SQLite database
    engine = create_engine('sqlite:///system/genai/temp/model.sqlite')

    # Create all tables
    Base.metadata.create_all(engine)

    # Create a new session
    Session = sessionmaker(bind=engine)
    session = Session()

    # Add some test data
    customer1 = Customer(name="John Doe", balance=0, credit_limit=5000)
    customer2 = Customer(name="Jane Smith", balance=0, credit_limit=3000)
    
    product1 = Product(name="Laptop", unit_price=1000)
    product2 = Product(name="Mouse", unit_price=25)
    
    order1 = Order(customer_id=1, notes="Urgent delivery")
    order2 = Order(customer_id=2, notes="Regular delivery")

    item1 = Item(order_id=1, product_id=1, quantity=2, unit_price=1000, amount=2000)
    item2 = Item(order_id=1, product_id=2, quantity=4, unit_price=25, amount=100)
    item3 = Item(order_id=2, product_id=1, quantity=1, unit_price=1000, amount=1000)

    # Add records to the session
    session.add(customer1)
    session.add(customer2)
    session.add(product1)
    session.add(product2)
    session.add(order1)
    session.add(order2)
    session.add(item1)
    session.add(item2)
    session.add(item3)

    # Commit the session
    session.commit()

    print("Database created and test data added successfully.")

if __name__ == "__main__":
    main()
