#!/usr/bin/env python
#
# Convert a GPT response (WGResult) to code
# This script reads a GPT response JSON file and generates Python code that can be used to add the test data to the database.
# 
# # Generate test data code from a GPT response JSON file:
# python database/test_data/response2code.py --test-data --response=docs/Customer_Order_System_003.response
# # Run the generated test data code:
# python database/test_data_code.py
#
<<<<<<< HEAD
=======
# python tools/response2code.py docs/response.json
# python database/test_data/response2code.py --test-data --response=docs/Customer_Order_System_003.response
import ast
>>>>>>> af26307 (comments)
import json
import sys
import os
import logging
import logging.config
import click

logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger("response2code")

source_code_preamble = """
import logging
import logging.config
import os
import yaml
from datetime import date
from pathlib import Path
from sqlalchemy import (Boolean, Column, Date, DateTime, DECIMAL, Float, ForeignKey, Integer, Numeric, String, Text, create_engine)
from sqlalchemy.dialects.sqlite import *
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import func
from database.models import *
from database.models import Base
from logic import declare_logic
from logic_bank.logic_bank import LogicBank, Rule

project_dir = Path(os.getenv("PROJECT_DIR",'./')).resolve()

logging_config = project_dir / 'config/logging.yml'
if logging_config.is_file():
    with open(logging_config,'rt') as f:  
        config=yaml.safe_load(f.read())
    logging.config.dictConfig(config)

db_url_path = project_dir.joinpath('database/db.sqlite')
db_url = f'sqlite:///{db_url_path.resolve()}'
logging.info(f'..  db_url: {db_url}')

if db_url_path.is_file():
    db_url_path.unlink()

engine = create_engine(db_url)
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
session = Session()

LogicBank.activate(session=session, activator=declare_logic.declare_logic)
"""

source_code_template = """
try:
    instance = {code}
    session.add(instance)
    session.commit()
except Exception as e:
    print(f"Error adding variable to session: {{e}}")
"""

def write_test_data(test_data):
    test_data_code = source_code_preamble
    
    for row in test_data:
        test_data_code += source_code_template.format(code=row.get("code"))
    
    test_data_file = 'database/test_data_code.py'
    
    with open(test_data_file, 'w') as f:
        f.write(test_data_code)
    
    log.info(f"Successfully wrote test data code to {test_data_file}")

def models2code():
    log.info("models2code function called")
    # ...existing code...
    pass

def rules2code():
    log.info("rules2code function called")
    # ...existing code...
    pass


def get_test_data(response):
    if not response:
        response = './docs/response.json'
    
    log.info(f"Loading GPT response from {response}")
    
    with open(response) as f:
        test_data = json.load(f).get("test_data_rows", [])

    return test_data

@click.command()
@click.option('--models', is_flag=True, help='Call models2code function')
@click.option('--rules', is_flag=True, help='Call rules2code function')
@click.option('--test-data', is_flag=True, help='Call test_data2code function')
@click.option('--response', type=click.Path(exists=True), help='Path to GPT response JSON file')
def main(models, rules, test_data, response):
    
    if models:
        models2code()
    if rules:
        rules2code()
    if test_data:
        test_data = get_test_data(response)
        write_test_data(test_data)

if __name__ == "__main__":
    main()