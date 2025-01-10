# coding: utf-8
from sqlalchemy import DECIMAL, DateTime  # API Logic Server GenAI assist
from sqlalchemy import Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

########################################################################################################################
# Classes describing database for SqlAlchemy ORM, initially created by schema introspection.
#
# Alter this file per your database maintenance policy
#    See https://apilogicserver.github.io/Docs/Project-Rebuild/#rebuilding
#
# Created:  January 09, 2025 14:55:41
# Database: sqlite:////tmp/tmp.QCoeKqjGri/Comprehensive_Holiday_Planner_iter_1/database/db.sqlite
# Dialect:  sqlite
#
# mypy: ignore-errors
########################################################################################################################
 
from database.system.SAFRSBaseX import SAFRSBaseX, TestBase
from flask_login import UserMixin
import safrs, flask_sqlalchemy, os
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

if os.getenv('APILOGICPROJECT_NO_FLASK') is None:
    Base = SAFRSBaseX   # enables rules to be used outside of Flask, e.g., test data loading
else:
    Base = TestBase     # ensure proper types, so rules work for data loading
    print('*** Models.py Using TestBase ***')



class Destination(Base):  # type: ignore
    """
    description: Represents a holiday destination.
    """
    __tablename__ = 'destination'
    _s_collection_name = 'Destination'  # type: ignore

    id = Column(Integer, primary_key=True)
    name = Column(String)
    description = Column(String)
    activity_count = Column(Integer)

    # parent relationships (access parent)

    # child relationships (access children)
    AccommodationList : Mapped[List["Accommodation"]] = relationship(back_populates="destination")
    ActivityList : Mapped[List["Activity"]] = relationship(back_populates="destination")
    GuideList : Mapped[List["Guide"]] = relationship(back_populates="destination")
    ReviewList : Mapped[List["Review"]] = relationship(back_populates="destination")
    BookingList : Mapped[List["Booking"]] = relationship(back_populates="destination")



class Transport(Base):  # type: ignore
    """
    description: Represents transport arrangements for a booking.
    """
    __tablename__ = 'transport'
    _s_collection_name = 'Transport'  # type: ignore

    id = Column(Integer, primary_key=True)
    name = Column(String)
    departure_date = Column(DateTime)
    arrival_date = Column(DateTime)
    departure_location = Column(String)
    arrival_location = Column(String)

    # parent relationships (access parent)

    # child relationships (access children)



class User(Base):  # type: ignore
    """
    description: Represents a user in the holiday planner system.
    """
    __tablename__ = 'user'
    _s_collection_name = 'User'  # type: ignore

    id = Column(Integer, primary_key=True)
    name = Column(String)
    email = Column(String)
    booking_count = Column(Integer)

    # parent relationships (access parent)

    # child relationships (access children)
    NotificationList : Mapped[List["Notification"]] = relationship(back_populates="user")
    ReviewList : Mapped[List["Review"]] = relationship(back_populates="user")
    BookingList : Mapped[List["Booking"]] = relationship(back_populates="user")
    InsuranceList : Mapped[List["Insurance"]] = relationship(back_populates="user")
    PaymentList : Mapped[List["Payment"]] = relationship(back_populates="user")



class Accommodation(Base):  # type: ignore
    """
    description: Represents available accommodation at a destination.
    """
    __tablename__ = 'accommodation'
    _s_collection_name = 'Accommodation'  # type: ignore

    id = Column(Integer, primary_key=True)
    name = Column(String)
    destination_id = Column(ForeignKey('destination.id'))
    price_per_night = Column(Integer)
    accommodation_type = Column(String)

    # parent relationships (access parent)
    destination : Mapped["Destination"] = relationship(back_populates=("AccommodationList"))

    # child relationships (access children)



class Activity(Base):  # type: ignore
    """
    description: Represents an activity that can be added to a booking by a user.
    """
    __tablename__ = 'activity'
    _s_collection_name = 'Activity'  # type: ignore

    id = Column(Integer, primary_key=True)
    destination_id = Column(ForeignKey('destination.id'))
    name = Column(String)
    description = Column(String)
    duration = Column(Integer)

    # parent relationships (access parent)
    destination : Mapped["Destination"] = relationship(back_populates=("ActivityList"))

    # child relationships (access children)
    BookingList : Mapped[List["Booking"]] = relationship(back_populates="activity")



class Guide(Base):  # type: ignore
    """
    description: Represents a tour guide available at a destination.
    """
    __tablename__ = 'guide'
    _s_collection_name = 'Guide'  # type: ignore

    id = Column(Integer, primary_key=True)
    name = Column(String)
    languages = Column(String)
    destination_id = Column(ForeignKey('destination.id'))

    # parent relationships (access parent)
    destination : Mapped["Destination"] = relationship(back_populates=("GuideList"))

    # child relationships (access children)



class Notification(Base):  # type: ignore
    """
    description: Represents messages sent to users.
    """
    __tablename__ = 'notification'
    _s_collection_name = 'Notification'  # type: ignore

    id = Column(Integer, primary_key=True)
    user_id = Column(ForeignKey('user.id'))
    message = Column(String)
    date_sent = Column(DateTime)
    is_read = Column(Integer)

    # parent relationships (access parent)
    user : Mapped["User"] = relationship(back_populates=("NotificationList"))

    # child relationships (access children)



class Review(Base):  # type: ignore
    """
    description: Represents a user's review of a destination.
    """
    __tablename__ = 'review'
    _s_collection_name = 'Review'  # type: ignore

    id = Column(Integer, primary_key=True)
    user_id = Column(ForeignKey('user.id'))
    destination_id = Column(ForeignKey('destination.id'))
    rating = Column(Integer)
    comment = Column(String)

    # parent relationships (access parent)
    destination : Mapped["Destination"] = relationship(back_populates=("ReviewList"))
    user : Mapped["User"] = relationship(back_populates=("ReviewList"))

    # child relationships (access children)



class Booking(Base):  # type: ignore
    """
    description: Represents a booking instance associating a user, a destination, and activities.
    """
    __tablename__ = 'booking'
    _s_collection_name = 'Booking'  # type: ignore

    id = Column(Integer, primary_key=True)
    user_id = Column(ForeignKey('user.id'))
    destination_id = Column(ForeignKey('destination.id'))
    activity_id = Column(ForeignKey('activity.id'))
    booking_date = Column(DateTime)
    total_cost = Column(Integer)

    # parent relationships (access parent)
    activity : Mapped["Activity"] = relationship(back_populates=("BookingList"))
    destination : Mapped["Destination"] = relationship(back_populates=("BookingList"))
    user : Mapped["User"] = relationship(back_populates=("BookingList"))

    # child relationships (access children)
    InsuranceList : Mapped[List["Insurance"]] = relationship(back_populates="booking")
    MealList : Mapped[List["Meal"]] = relationship(back_populates="booking")
    PaymentList : Mapped[List["Payment"]] = relationship(back_populates="booking")



class Insurance(Base):  # type: ignore
    """
    description: Represents an insurance policy booked along with the trip.
    """
    __tablename__ = 'insurance'
    _s_collection_name = 'Insurance'  # type: ignore

    id = Column(Integer, primary_key=True)
    user_id = Column(ForeignKey('user.id'))
    booking_id = Column(ForeignKey('booking.id'))
    policy_number = Column(String)
    coverage_amount = Column(Integer)

    # parent relationships (access parent)
    booking : Mapped["Booking"] = relationship(back_populates=("InsuranceList"))
    user : Mapped["User"] = relationship(back_populates=("InsuranceList"))

    # child relationships (access children)



class Meal(Base):  # type: ignore
    """
    description: Represents meals that can be pre-booked for the trip.
    """
    __tablename__ = 'meal'
    _s_collection_name = 'Meal'  # type: ignore

    id = Column(Integer, primary_key=True)
    booking_id = Column(ForeignKey('booking.id'))
    meal_type = Column(String)
    price = Column(Integer)

    # parent relationships (access parent)
    booking : Mapped["Booking"] = relationship(back_populates=("MealList"))

    # child relationships (access children)



class Payment(Base):  # type: ignore
    """
    description: Represents a payment processed for a particular booking.
    """
    __tablename__ = 'payment'
    _s_collection_name = 'Payment'  # type: ignore

    id = Column(Integer, primary_key=True)
    user_id = Column(ForeignKey('user.id'))
    booking_id = Column(ForeignKey('booking.id'))
    payment_date = Column(DateTime)
    amount = Column(Integer)

    # parent relationships (access parent)
    booking : Mapped["Booking"] = relationship(back_populates=("PaymentList"))
    user : Mapped["User"] = relationship(back_populates=("PaymentList"))

    # child relationships (access children)
