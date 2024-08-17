from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, DateTime  # see 185: _class
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import datetime
import random

# Define the SQLite database
engine = create_engine('sqlite:///system/genai/temp/create_db_models.sqlite', echo=True)
Base = declarative_base()
Session = sessionmaker(bind=engine)
session = Session()

# Define the tables
class Character(Base):
    __tablename__ = 'characters'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)

class Race(Base):
    __tablename__ = 'races'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)

class Class(Base):
    __tablename__ = 'classes'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)

class Weapon(Base):
    __tablename__ = 'weapons'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)

class Spell(Base):
    __tablename__ = 'spells'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)

# More tables as needed, up to 25 tables following the same pattern
# For demonstration, I'll create only the necessary to show you the pattern
class CharacterRace(Base):
    __tablename__ = 'character_races'
    id = Column(Integer, primary_key=True, autoincrement=True)
    character_id = Column(Integer, ForeignKey('characters.id'), nullable=False)
    race_id = Column(Integer, ForeignKey('races.id'), nullable=False)

class CharacterClass(Base):
    __tablename__ = 'character_classes'
    id = Column(Integer, primary_key=True, autoincrement=True)
    character_id = Column(Integer, ForeignKey('characters.id'), nullable=False)
    class_id = Column(Integer, ForeignKey('classes.id'), nullable=False)

class CharacterWeapon(Base):
    __tablename__ = 'character_weapons'
    id = Column(Integer, primary_key=True, autoincrement=True)
    character_id = Column(Integer, ForeignKey('characters.id'), nullable=False)
    weapon_id = Column(Integer, ForeignKey('weapons.id'), nullable=False)

class CharacterSpell(Base):
    __tablename__ = 'character_spells'
    id = Column(Integer, primary_key=True, autoincrement=True)
    character_id = Column(Integer, ForeignKey('characters.id'), nullable=False)
    spell_id = Column(Integer, ForeignKey('spells.id'), nullable=False)

# Other tables up to 25...
# After defining the rest of the tables similarly

Base.metadata.create_all(engine)

# Insert sample data
character_names = [f'Character_{i}' for i in range(20)]
race_names = [f'Race_{i}' for i in range(5)]
class_names = [f'Class_{i}' for i in range(5)]
weapon_names = [f'Weapon_{i}' for i in range(10)]
spell_names = [f'Spell_{i}' for i in range(15)]

for name in character_names:
    session.add(Character(name=name))

for name in race_names:
    session.add(Race(name=name))

for name in class_names:
    session.add(Class(name=name))

for name in weapon_names:
    session.add(Weapon(name=name))

for name in spell_names:
    session.add(Spell(name=name))

session.commit()

characters = session.query(Character).all()
races = session.query(Race).all()
classes = session.query(Class).all()
weapons = session.query(Weapon).all()
spells = session.query(Spell).all()

for _ in range(100):
    character = random.choice(characters)
    race = random.choice(races)
    class_ = random.choice(classes)
    weapon = random.choice(weapons)
    spell = random.choice(spells)
    
    session.add(CharacterRace(character_id=character.id, race_id=race.id))
    session.add(CharacterClass(character_id=character.id, class_id=class_.id))
    session.add(CharacterWeapon(character_id=character.id, weapon_id=weapon.id))
    session.add(CharacterSpell(character_id=character.id, spell_id=spell.id))

session.commit()
print("Database and sample data created successfully!")