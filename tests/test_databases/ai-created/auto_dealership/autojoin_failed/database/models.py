# coding: utf-8
from sqlalchemy import DECIMAL, DateTime  # API Logic Server GenAI assist
from sqlalchemy import Column, DECIMAL, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

########################################################################################################################
# Classes describing database for SqlAlchemy ORM, initially created by schema introspection.
#
# Alter this file per your database maintenance policy
#    See https://apilogicserver.github.io/Docs/Project-Rebuild/#rebuilding
#
# Created:  August 24, 2024 11:32:05
# Database: sqlite:////Users/val/dev/ApiLogicServer/auto_dealership_with_at_least_10_tables/database/db.sqlite
# Dialect:  sqlite
#
# mypy: ignore-errors
########################################################################################################################
 
from database.system.SAFRSBaseX import SAFRSBaseX
from flask_login import UserMixin
import safrs, flask_sqlalchemy
from safrs import jsonapi_attr
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship
from sqlalchemy.orm import Mapped
from sqlalchemy.sql.sqltypes import NullType
from typing import List

db = SQLAlchemy() 
Base = declarative_base()  # type: flask_sqlalchemy.model.DefaultMeta
metadata = Base.metadata

#NullType = db.String  # datatype fixup
#TIMESTAMP= db.TIMESTAMP

from sqlalchemy.dialects.sqlite import *



class Customer(SAFRSBaseX, Base):
    __tablename__ = 'customers'
    _s_collection_name = 'Customer'  # type: ignore
    __bind_key__ = 'None'

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    email = Column(String)

    # parent relationships (access parent)

    # child relationships (access children)
    SaleList : Mapped[List["Sale"]] = relationship(back_populates="customer")
    TestDriveList : Mapped[List["TestDrive"]] = relationship(back_populates="customer")

    @jsonapi_attr
    def _check_sum_(self):  # type: ignore [no-redef]
        return None if isinstance(self, flask_sqlalchemy.model.DefaultMeta) \
            else self._check_sum_property if hasattr(self,"_check_sum_property") \
                else None  # property does not exist during initialization

    @_check_sum_.setter
    def _check_sum_(self, value):  # type: ignore [no-redef]
        self._check_sum_property = value

    S_CheckSum = _check_sum_


class Dealership(SAFRSBaseX, Base):
    __tablename__ = 'dealerships'
    _s_collection_name = 'Dealership'  # type: ignore
    __bind_key__ = 'None'

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    location = Column(String)

    # parent relationships (access parent)

    # child relationships (access children)
    EmployeeList : Mapped[List["Employee"]] = relationship(back_populates="dealership")
    VehicleList : Mapped[List["Vehicle"]] = relationship(back_populates="dealership")
    InventoryList : Mapped[List["Inventory"]] = relationship(back_populates="dealership")

    @jsonapi_attr
    def _check_sum_(self):  # type: ignore [no-redef]
        return None if isinstance(self, flask_sqlalchemy.model.DefaultMeta) \
            else self._check_sum_property if hasattr(self,"_check_sum_property") \
                else None  # property does not exist during initialization

    @_check_sum_.setter
    def _check_sum_(self, value):  # type: ignore [no-redef]
        self._check_sum_property = value

    S_CheckSum = _check_sum_


class Manufacturer(SAFRSBaseX, Base):
    __tablename__ = 'manufacturers'
    _s_collection_name = 'Manufacturer'  # type: ignore
    __bind_key__ = 'None'

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)

    # parent relationships (access parent)

    # child relationships (access children)
    CarModelList : Mapped[List["CarModel"]] = relationship(back_populates="manufacturer")

    @jsonapi_attr
    def _check_sum_(self):  # type: ignore [no-redef]
        return None if isinstance(self, flask_sqlalchemy.model.DefaultMeta) \
            else self._check_sum_property if hasattr(self,"_check_sum_property") \
                else None  # property does not exist during initialization

    @_check_sum_.setter
    def _check_sum_(self, value):  # type: ignore [no-redef]
        self._check_sum_property = value

    S_CheckSum = _check_sum_


class CarModel(SAFRSBaseX, Base):
    __tablename__ = 'car_models'
    _s_collection_name = 'CarModel'  # type: ignore
    __bind_key__ = 'None'

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    manufacturer_id = Column(ForeignKey('manufacturers.id'))
    year = Column(Integer)

    # parent relationships (access parent)
    manufacturer : Mapped["Manufacturer"] = relationship(back_populates=("CarModelList"))

    # child relationships (access children)
    VehicleList : Mapped[List["Vehicle"]] = relationship(back_populates="car_model")

    @jsonapi_attr
    def _check_sum_(self):  # type: ignore [no-redef]
        return None if isinstance(self, flask_sqlalchemy.model.DefaultMeta) \
            else self._check_sum_property if hasattr(self,"_check_sum_property") \
                else None  # property does not exist during initialization

    @_check_sum_.setter
    def _check_sum_(self, value):  # type: ignore [no-redef]
        self._check_sum_property = value

    S_CheckSum = _check_sum_


class Employee(SAFRSBaseX, Base):
    __tablename__ = 'employees'
    _s_collection_name = 'Employee'  # type: ignore
    __bind_key__ = 'None'

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    dealership_id = Column(ForeignKey('dealerships.id'))
    hire_date = Column(DateTime)

    # parent relationships (access parent)
    dealership : Mapped["Dealership"] = relationship(back_populates=("EmployeeList"))

    # child relationships (access children)

    @jsonapi_attr
    def _check_sum_(self):  # type: ignore [no-redef]
        return None if isinstance(self, flask_sqlalchemy.model.DefaultMeta) \
            else self._check_sum_property if hasattr(self,"_check_sum_property") \
                else None  # property does not exist during initialization

    @_check_sum_.setter
    def _check_sum_(self, value):  # type: ignore [no-redef]
        self._check_sum_property = value

    S_CheckSum = _check_sum_


class Vehicle(SAFRSBaseX, Base):
    __tablename__ = 'vehicles'
    _s_collection_name = 'Vehicle'  # type: ignore
    __bind_key__ = 'None'

    id = Column(Integer, primary_key=True)
    vin = Column(String, nullable=False, unique=True)
    car_model_id = Column(ForeignKey('car_models.id'))
    dealership_id = Column(ForeignKey('dealerships.id'))
    price : DECIMAL = Column(DECIMAL)
    date_added = Column(DateTime)

    # parent relationships (access parent)
    car_model : Mapped["CarModel"] = relationship(back_populates=("VehicleList"))
    dealership : Mapped["Dealership"] = relationship(back_populates=("VehicleList"))

    # child relationships (access children)
    InventoryList : Mapped[List["Inventory"]] = relationship(back_populates="vehicle")
    SaleList : Mapped[List["Sale"]] = relationship(back_populates="vehicle")
    ServiceList : Mapped[List["Service"]] = relationship(back_populates="vehicle")
    TestDriveList : Mapped[List["TestDrive"]] = relationship(back_populates="vehicle")

    @jsonapi_attr
    def _check_sum_(self):  # type: ignore [no-redef]
        return None if isinstance(self, flask_sqlalchemy.model.DefaultMeta) \
            else self._check_sum_property if hasattr(self,"_check_sum_property") \
                else None  # property does not exist during initialization

    @_check_sum_.setter
    def _check_sum_(self, value):  # type: ignore [no-redef]
        self._check_sum_property = value

    S_CheckSum = _check_sum_


class Inventory(SAFRSBaseX, Base):
    __tablename__ = 'inventory'
    _s_collection_name = 'Inventory'  # type: ignore
    __bind_key__ = 'None'

    id = Column(Integer, primary_key=True)
    dealership_id = Column(ForeignKey('dealerships.id'))
    vehicle_id = Column(ForeignKey('vehicles.id'))
    quantity = Column(Integer)

    # parent relationships (access parent)
    dealership : Mapped["Dealership"] = relationship(back_populates=("InventoryList"))
    vehicle : Mapped["Vehicle"] = relationship(back_populates=("InventoryList"))

    # child relationships (access children)

    @jsonapi_attr
    def _check_sum_(self):  # type: ignore [no-redef]
        return None if isinstance(self, flask_sqlalchemy.model.DefaultMeta) \
            else self._check_sum_property if hasattr(self,"_check_sum_property") \
                else None  # property does not exist during initialization

    @_check_sum_.setter
    def _check_sum_(self, value):  # type: ignore [no-redef]
        self._check_sum_property = value

    S_CheckSum = _check_sum_


class Sale(SAFRSBaseX, Base):
    __tablename__ = 'sales'
    _s_collection_name = 'Sale'  # type: ignore
    __bind_key__ = 'None'

    id = Column(Integer, primary_key=True)
    vehicle_id = Column(ForeignKey('vehicles.id'))
    customer_id = Column(ForeignKey('customers.id'))
    sale_date = Column(DateTime)
    sale_price : DECIMAL = Column(DECIMAL)

    # parent relationships (access parent)
    customer : Mapped["Customer"] = relationship(back_populates=("SaleList"))
    vehicle : Mapped["Vehicle"] = relationship(back_populates=("SaleList"))

    # child relationships (access children)

    @jsonapi_attr
    def _check_sum_(self):  # type: ignore [no-redef]
        return None if isinstance(self, flask_sqlalchemy.model.DefaultMeta) \
            else self._check_sum_property if hasattr(self,"_check_sum_property") \
                else None  # property does not exist during initialization

    @_check_sum_.setter
    def _check_sum_(self, value):  # type: ignore [no-redef]
        self._check_sum_property = value

    S_CheckSum = _check_sum_


class Service(SAFRSBaseX, Base):
    __tablename__ = 'services'
    _s_collection_name = 'Service'  # type: ignore
    __bind_key__ = 'None'

    id = Column(Integer, primary_key=True)
    vehicle_id = Column(ForeignKey('vehicles.id'))
    service_date = Column(DateTime)
    description = Column(String)

    # parent relationships (access parent)
    vehicle : Mapped["Vehicle"] = relationship(back_populates=("ServiceList"))

    # child relationships (access children)

    @jsonapi_attr
    def _check_sum_(self):  # type: ignore [no-redef]
        return None if isinstance(self, flask_sqlalchemy.model.DefaultMeta) \
            else self._check_sum_property if hasattr(self,"_check_sum_property") \
                else None  # property does not exist during initialization

    @_check_sum_.setter
    def _check_sum_(self, value):  # type: ignore [no-redef]
        self._check_sum_property = value

    S_CheckSum = _check_sum_


class TestDrive(SAFRSBaseX, Base):
    __tablename__ = 'test_drives'
    _s_collection_name = 'TestDrive'  # type: ignore
    __bind_key__ = 'None'

    id = Column(Integer, primary_key=True)
    vehicle_id = Column(ForeignKey('vehicles.id'))
    customer_id = Column(ForeignKey('customers.id'))
    test_drive_date = Column(DateTime)

    # parent relationships (access parent)
    customer : Mapped["Customer"] = relationship(back_populates=("TestDriveList"))
    vehicle : Mapped["Vehicle"] = relationship(back_populates=("TestDriveList"))

    # child relationships (access children)

    @jsonapi_attr
    def _check_sum_(self):  # type: ignore [no-redef]
        return None if isinstance(self, flask_sqlalchemy.model.DefaultMeta) \
            else self._check_sum_property if hasattr(self,"_check_sum_property") \
                else None  # property does not exist during initialization

    @_check_sum_.setter
    def _check_sum_(self, value):  # type: ignore [no-redef]
        self._check_sum_property = value

    S_CheckSum = _check_sum_
