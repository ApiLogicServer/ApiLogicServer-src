from sqlalchemy import Boolean, Column, Date, Float, ForeignKey, Integer, String
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class Customer(Base):
    __tablename__ = "customer"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String)
    balance = Column(Float)
    credit_limit = Column(Float)
    email = Column(String)
    email_opt_out = Column(Boolean)


class Product(Base):
    __tablename__ = "product"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String)
    count_suppliers = Column(Integer)
    unit_price = Column(Float)


class Order(Base):
    __tablename__ = "order"
    id = Column(Integer, primary_key=True, autoincrement=True)
    notes = Column(String)
    customer_id = Column(Integer, ForeignKey("customer.id"), nullable=False)
    CreatedOn = Column(Date)
    date_shipped = Column(Date)
    amount_total = Column(Float)


class Item(Base):
    __tablename__ = "item"
    id = Column(Integer, primary_key=True, autoincrement=True)
    order_id = Column(Integer, ForeignKey("order.id"))
    product_id = Column(Integer, ForeignKey("product.id"), nullable=False)
    quantity = Column(Integer, nullable=False)
    amount = Column(Float)
    unit_price = Column(Float)


class Supplier(Base):
    __tablename__ = "supplier"
    id = Column(Integer, primary_key=True)
    name = Column(String)
    contact_name = Column(String)
    phone = Column(String)
    email = Column(String)
    region = Column(String)


class ProductSupplier(Base):
    __tablename__ = "product_supplier"
    id = Column(Integer, primary_key=True)
    product_id = Column(Integer, ForeignKey("product.id"))
    supplier_id = Column(Integer, ForeignKey("supplier.id"))
    supplier_part_number = Column(String)
    unit_cost = Column(Float)
    lead_time_days = Column(Integer)


TABLES = {m.__tablename__: m for m in (Customer, Product, Order, Item, Supplier, ProductSupplier)}
