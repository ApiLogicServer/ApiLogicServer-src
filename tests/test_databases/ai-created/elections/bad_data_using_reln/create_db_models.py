from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String, ForeignKey, DateTime
from datetime import datetime

# Create the SQLite database
engine = create_engine('sqlite:///system/genai/temp/model.sqlite')
metadata = MetaData()

# Define the tables
bartenders = Table('bartenders', metadata,
    Column('id', Integer, primary_key=True),
    Column('name', String, nullable=False),
)

drinks = Table('drinks', metadata,
    Column('id', Integer, primary_key=True),
    Column('name', String, nullable=False),
)

bars = Table('bars', metadata,
    Column('id', Integer, primary_key=True),
    Column('name', String, nullable=False),
)

orders = Table('orders', metadata,
    Column('id', Integer, primary_key=True),
    Column('bartender_id', Integer, ForeignKey('bartenders.id'), nullable=False),
    Column('drink_id', Integer, ForeignKey('drinks.id'), nullable=False),
    Column('bar_id', Integer, ForeignKey('bars.id'), nullable=False),
    Column('order_time', DateTime, default=datetime.now),
)

# Create the tables
metadata.create_all(engine)

# Insert sample data
conn = engine.connect()

conn.execute(bartenders.insert(), [
    {'name': 'Alice'},
    {'name': 'Bob'},
])

conn.execute(drinks.insert(), [
    {'name': 'Martini'},
    {'name': 'Beer'},
])

conn.execute(bars.insert(), [
    {'name': 'Bar A'},
    {'name': 'Bar B'},
])

conn.execute(orders.insert(), [
    {'bartender_id': 1, 'drink_id': 1, 'bar_id': 1},
    {'bartender_id': 2, 'drink_id': 2, 'bar_id': 2},
])

conn.close()
print("Database created with sample data.")
