from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

# pushd  ~/dev/ApiLogicServer/ApiLogicServer-dev/build_and_test/ApiLogicServer  
# . venv/bin/activate
# popd
# als create --project-name=copilot --from-model=models.py --db_url=sqlite:///copilot/database/db.sqlite
# db_url is wrong

# db = SQLAlchemy() 
Base = declarative_base()  # type: flask_sqlalchemy.model.DefaultMeta
metadata = Base.metadata

class Employee(Base):
    __tablename__ = 'employees'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    skills = relationship('Skill', backref='employee')

class Skill(Base):
    __tablename__ = 'skills'

    id = Column(Integer, primary_key=True)
    skill_name = Column(String)
    employee_id = Column(Integer, ForeignKey('employees.id'))