import decimal

from sqlalchemy.sql import func  # end imports from system/genai/create_db_models_inserts/create_db_models_prefix.py
from sqlalchemy import create_engine, Column, Integer, String, DateTime, DECIMAL, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import datetime

# Define the database location
DATABASE_LOCATION = 'sqlite:///system/genai/temp/create_db_models.sqlite'

# Create the engine and Base
engine = create_engine(DATABASE_LOCATION, echo=True)
Base = declarative_base()

# Define the tables
class Manufacturer(Base):
    __tablename__ = 'manufacturers'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)

class CarModel(Base):
    __tablename__ = 'car_models'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    manufacturer_id = Column(Integer, ForeignKey('manufacturers.id'))
    year = Column(Integer)

class Dealership(Base):
    __tablename__ = 'dealerships'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    location = Column(String, nullable=True)

class Employee(Base):
    __tablename__ = 'employees'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    dealership_id = Column(Integer, ForeignKey('dealerships.id'))
    hire_date = Column(DateTime, nullable=True)

class Customer(Base):
    __tablename__ = 'customers'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    email = Column(String, nullable=True)

class Vehicle(Base):
    __tablename__ = 'vehicles'
    id = Column(Integer, primary_key=True, autoincrement=True)
    vin = Column(String, unique=True, nullable=False)
    car_model_id = Column(Integer, ForeignKey('car_models.id'))
    dealership_id = Column(Integer, ForeignKey('dealerships.id'))
    price = Column(DECIMAL, nullable=True)
    date_added = Column(DateTime, default=datetime.datetime.utcnow)

class Sale(Base):
    __tablename__ = 'sales'
    id = Column(Integer, primary_key=True, autoincrement=True)
    vehicle_id = Column(Integer, ForeignKey('vehicles.id'))
    customer_id = Column(Integer, ForeignKey('customers.id'))
    sale_date = Column(DateTime, default=datetime.datetime.utcnow)
    sale_price = Column(DECIMAL, nullable=True)

class Service(Base):
    __tablename__ = 'services'
    id = Column(Integer, primary_key=True, autoincrement=True)
    vehicle_id = Column(Integer, ForeignKey('vehicles.id'))
    service_date = Column(DateTime, default=datetime.datetime.utcnow)
    description = Column(String, nullable=True)

class TestDrive(Base):
    __tablename__ = 'test_drives'
    id = Column(Integer, primary_key=True, autoincrement=True)
    vehicle_id = Column(Integer, ForeignKey('vehicles.id'))
    customer_id = Column(Integer, ForeignKey('customers.id'))
    test_drive_date = Column(DateTime, default=datetime.datetime.utcnow)

class Inventory(Base):
    __tablename__ = 'inventory'
    id = Column(Integer, primary_key=True, autoincrement=True)
    dealership_id = Column(Integer, ForeignKey('dealerships.id'))
    vehicle_id = Column(Integer, ForeignKey('vehicles.id'))
    quantity = Column(Integer, default=1)

# Create all tables
Base.metadata.create_all(engine)

# Create a session
Session = sessionmaker(bind=engine)
session = Session()

# Add some test data
manufacturer = Manufacturer(name="Toyota")
session.add(manufacturer)

carmodel = CarModel(name="Camry", manufacturer_id=1, year=2022)
session.add(carmodel)

dealership = Dealership(name="Super Auto", location="New York")
session.add(dealership)

employee = Employee(name="John Doe", dealership_id=1, hire_date=datetime.datetime(2021, 5, 21))
session.add(employee)

customer = Customer(name="Jane Smith", email="jane.smith@test.com")
session.add(customer)

vehicle = Vehicle(vin="1HGBH41JXMN109186", car_model_id=1, dealership_id=1, price=30000)
session.add(vehicle)

sale = Sale(vehicle_id=1, customer_id=1, sale_date=datetime.datetime(2023, 2, 20), sale_price=29000)
session.add(sale)

service = Service(vehicle_id=1, service_date=datetime.datetime(2023, 3, 15), description="Oil Change")
session.add(service)

test_drive = TestDrive(vehicle_id=1, customer_id=1, test_drive_date=datetime.datetime(2023, 1, 15))
session.add(test_drive)

inventory = Inventory(dealership_id=1, vehicle_id=1, quantity=10)
session.add(inventory)

# Commit the session to the database
session.commit()
