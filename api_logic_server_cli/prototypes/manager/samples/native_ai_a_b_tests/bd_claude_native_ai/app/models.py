from pathlib import Path

from sqlalchemy import create_engine, Column, Integer, String, Numeric, Boolean, Date, ForeignKey
from sqlalchemy.orm import declarative_base, relationship, sessionmaker

DB_PATH = Path(__file__).resolve().parent.parent / "basic_demo.sqlite"
DATABASE_URL = f"sqlite:///{DB_PATH}"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class Customer(Base):
    __tablename__ = "customer"

    id = Column(Integer, primary_key=True)
    name = Column(String)
    balance = Column(Numeric)
    credit_limit = Column(Numeric)
    email = Column(String)
    email_opt_out = Column(Boolean)

    orders = relationship("Order", back_populates="customer")


class Product(Base):
    __tablename__ = "product"

    id = Column(Integer, primary_key=True)
    name = Column(String)
    count_suppliers = Column(Integer)
    unit_price = Column(Numeric)


class Order(Base):
    __tablename__ = "order"

    id = Column(Integer, primary_key=True)
    notes = Column(String)
    customer_id = Column(Integer, ForeignKey("customer.id"), nullable=False)
    CreatedOn = Column(Date)
    date_shipped = Column(Date)
    amount_total = Column(Numeric)

    customer = relationship("Customer", back_populates="orders")
    items = relationship("Item", back_populates="order", cascade="all, delete-orphan")


class Item(Base):
    __tablename__ = "item"

    id = Column(Integer, primary_key=True)
    order_id = Column(Integer, ForeignKey("order.id"))
    product_id = Column(Integer, ForeignKey("product.id"), nullable=False)
    quantity = Column(Integer, nullable=False)
    amount = Column(Numeric)
    unit_price = Column(Numeric)

    order = relationship("Order", back_populates="items")
    product = relationship("Product")


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
