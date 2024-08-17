m sqlalchemy import create_engine, Column, Integer, String, Numeric, ForeignKey, DateTime
m sqlalchemy.ext.declarative import declarative_base
m sqlalchemy.orm import relationship, sessionmaker
m decimal import DECIMAL

efine the SQLite database path
ABASE_URI = 'sqlite:///system/genai/temp/create_db_models.sqlite'
e = declarative_base()

efine Customer table
ss Customer(Base):
 __tablename__ = 'customers'
 id = Column(Integer, primary_key=True, autoincrement=True)
 name = Column(String, nullable=True)
 balance = Column(Numeric, nullable=True)
 credit_limit = Column(Numeric, nullable=True)
 orders = relationship("Order", back_populates="customer")

efine Product table
ss Product(Base):
 __tablename__ = 'products'
 id = Column(Integer, primary_key=True, autoincrement=True)
 name = Column(String, nullable=True)
 unit_price = Column(Numeric, nullable=True)
 items = relationship("Item", back_populates="product")

efine Order table
ss Order(Base):
 __tablename__ = 'orders'
 id = Column(Integer, primary_key=True, autoincrement=True)
 customer_id = Column(Integer, ForeignKey('customers.id'))
 amount_total = Column(Numeric, nullable=True)
 date_shipped = Column(DateTime, nullable=True)
 notes = Column(String, nullable=True)
 customer = relationship("Customer", back_populates="orders")
 items = relationship("Item", back_populates="order")

efine Item table
ss Item(Base):
 __tablename__ = 'items'
 id = Column(Integer, primary_key=True, autoincrement=True)
 order_id = Column(Integer, ForeignKey('orders.id'))
 product_id = Column(Integer, ForeignKey('products.id'))
 quantity = Column(Integer, nullable=True)
 unit_price = Column(Numeric, nullable=True)
 amount = Column(Numeric, nullable=True)
 order = relationship("Order", back_populates="items")
 product = relationship("Product", back_populates="items")

reate the SQLite database
ine = create_engine(DATABASE_URI)
e.metadata.create_all(engine)

reate a new session
sion = sessionmaker(bind=engine)
sion = Session()

dd some initial rows for Customer and Product data
tomers = [
 Customer(name="Alice", balance=DECIMAL('200.00'), credit_limit=DECIMAL('500.00')),
 Customer(name="Bob", balance=DECIMAL('300.00'), credit_limit=DECIMAL('600.00')),


ducts = [
 Product(name="Laptop", unit_price=DECIMAL('800.00')),
 Product(name="Smartphone", unit_price=DECIMAL('400.00')),


sion.add_all(customers)
sion.add_all(products)
sion.commit()

nt("Database created and initial data inserted successfully.")
