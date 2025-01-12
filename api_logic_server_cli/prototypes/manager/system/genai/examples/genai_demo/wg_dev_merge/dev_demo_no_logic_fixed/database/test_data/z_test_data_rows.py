# experiment - under construction.  Not working, not used.
# created from response, to create create_db_models.sqlite, with test data
#    that is used to create project
# should run without error in manager 
#    if not, check for decimal, indent, or import issues

import decimal
import logging
import sqlalchemy
from sqlalchemy.sql import func 
from logic_bank.logic_bank import Rule
from sqlalchemy import create_engine, Column, Integer, String, Float, ForeignKey, Date, DateTime, Numeric, Boolean, Text, DECIMAL
from sqlalchemy.types import *
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import relationship
from sqlalchemy.orm import Mapped
from datetime import date   
from datetime import datetime
from typing import List
import os, logging, logging.config, sys, yaml
from pathlib import Path
from logic_bank.logic_bank import LogicBank
from database.models import *



def load_data(session):
        # Create test data
    session.commit()
    customer1 = Customer(id=1, name="John Doe", balance=130.00, credit_limit=500.00)
    session.add(customer1)
    session.commit()

    customer2 = Customer(id=2, name="Jane Smith", balance=200.00, credit_limit=600.00)
    session.add(customer2)
    session.commit()

    customer3 = Customer(id=3, name="George White", balance=300.00, credit_limit=700.00)
    session.add(customer3)
    session.commit()

    customer4 = Customer(id=4, name="Lisa Brown", balance=400.00, credit_limit=800.00)
    session.add(customer4)
    session.commit()

    product1 = Product(id=1, unit_price=10.00)
    session.add(product1)
    session.commit()

    product2 = Product(id=2, unit_price=15.00)
    session.add(product2)
    session.commit()

    product3 = Product(id=3, unit_price=20.00)
    session.add(product3)
    session.commit()

    product4 = Product(id=4, unit_price=30.00)
    session.add(product4)
    session.commit()

    order1 = Order(id=1, customer_id=1, date_shipped=None, amount_total=30.00, notes="First order")
    session.add(order1)
    session.commit()

    order2 = Order(id=2, customer_id=2, date_shipped=None, amount_total=45.00, notes="Second order")
    session.add(order2)
    session.commit()

    order3 = Order(id=3, customer_id=3, date_shipped=None, amount_total=60.00, notes="Third order")
    session.add(order3)
    session.commit()

    order4 = Order(id=4, customer_id=4, date_shipped=None, amount_total=50.00, notes="Fourth order")
    session.add(order4)
    session.commit()

    item1 = Item(id=1, order_id=1, product_id=1, quantity=3, amount=30.00, unit_price=10.00)
    session.add(item1)
    session.commit()

    item2 = Item(id=2, order_id=2, product_id=2, quantity=3, amount=45.00, unit_price=15.00)
    session.add(item2)
    session.commit()

    item3 = Item(id=3, order_id=3, product_id=3, quantity=3, amount=60.00, unit_price=20.00)
    session.add(item3)
    session.commit()

    item4 = Item(id=4, order_id=4, product_id=4, quantity=2, amount=50.00, unit_price=25.00)
    session.add(item4)
    session.commit()

    # session.add_all([customer1, customer2, customer3, customer4, product1, product2, product3, product4, order1, order2, order3, order4, item1, item2, item3, item4])
    session.commit()
    # end of test data
    
