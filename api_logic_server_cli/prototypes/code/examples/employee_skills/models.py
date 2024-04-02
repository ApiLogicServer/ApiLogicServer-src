from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Employee(Base):
    __tablename__ = 'employees'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    spin = Column(Integer)
    skills = relationship('Skill', backref='employee')

class Skill(Base):
    __tablename__ = 'skills'

    id = Column(Integer, primary_key=True)
    skill_name = Column(String)
    employee_id = Column(Integer, ForeignKey('employees.id'))