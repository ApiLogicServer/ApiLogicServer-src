#!/usr/bin/env python
#
# Convert a GPT response (WGResult) to code
#
# python tools/response2code.py docs/response.json
import ast
import json
import sys
import os, logging, logging.config, sys, yaml
import click
import safrs
import os
from colorama import Fore, Style
from pathlib import Path

sys.path.append('.')

from datetime import date

from database.models import *
from database.models import Base                                # FIXME had to disable safrsBaseX 
# Base = declarative_base()  # from system/genai/create_db_models_inserts/create_db_models_prefix.py

from sqlalchemy.dialects.sqlite import *
from sqlalchemy.sql import func 
from logic_bank.logic_bank import Rule
from sqlalchemy import create_engine, Column, Integer, String, Float, ForeignKey, Date, DateTime, Numeric, Boolean, Text, DECIMAL
from sqlalchemy.types import *
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

import os


log = logging.getLogger(__name__)

def get_top_level_assignments(source_code):
    """
    Parses the source_code and returns top-level assignments.
    """
    assignments = {}
    try:
        tree = ast.parse(source_code)
        for node in tree.body:
            if isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name):
                        var_name = target.id
                        var_value = ast.literal_eval(node.value) if isinstance(node.value, (ast.Constant, ast.Num, ast.Str, ast.List, ast.Dict, ast.Tuple)) else None
                        assignments[var_name] = var_value
    except Exception as e:
        log.warning(f"Error parsing source code: {e}")
    return assignments


source_code_template = """
try:
    {code}
    safrs.DB.session.add({variables})
    safrs.DB.session.commit()
except Exception as e:
    print(f"Error adding variable to session: {{e}}")
"""

def exec_test_data(test_data):
    variables = []
    test_data_code = ""
    for row in test_data:
        source_code = row.get("code")
        test_data_row_variable = row.get("test_data_row_variable")
        source_code2 = source_code_template.format(code=source_code, variables=test_data_row_variable)
        exec(source_code2)
        test_data_code += source_code2
    
    with open('/tmp/test_data_code.py', 'w') as f:
        f.write(test_data_code)
        
    for variable in variables:
        try:
            safrs.DB.session.add(locals()[variable])
            safrs.DB.session.commit()
        except Exception as e:
            log.warning(f"{Fore.RED}Error adding variable to session: {e}{Style.RESET_ALL}")
    
    log.info(f"added {variables} variables to session")
    

source_code_template_no_flask = """
try:
    {code}
    session.add({variables})
    session.commit()
except Exception as e:
    print(f"Error adding variable to session: {{e}}")
"""

def exec_test_data_no_flask(test_data, session):
    variables = []
    test_data_code = ""
    for row in test_data:
        source_code = row.get("code")
        test_data_row_variable = row.get("test_data_row_variable")
        source_code2 = source_code_template_no_flask.format(code=source_code, variables=test_data_row_variable)
        exec(source_code2)  # eg, 'customer1 = Customer(id=1, name="John Doe", balance=130.00, credit_limit=500.00)'
        test_data_code += source_code2
    
    with open('/tmp/test_data_code.py', 'w') as f:
        f.write(test_data_code)
        
    for variable in variables:
        try:
            session.add(locals()[variable])
            session.commit()
        except Exception as e:
            log.warning(f"{Fore.RED}Error adding variable to session: {e}{Style.RESET_ALL}")
    
    log.info(f"added {variables} variables to session")
    

def models2code():
    # ...existing code...
    pass

def rules2code():
    # ...existing code...
    pass


@click.command()
@click.option('--models', is_flag=True, help='Call models2code function')
@click.option('--rules', is_flag=True, help='Call rules2code function')
@click.option('--test-data', is_flag=True, help='Call test_data2code function')
@click.option('--response', type=click.Path(exists=True), help='Path to GPT response JSON file')

def main(models, rules, test_data, response):
    if response:
        gpt_response = response
        with open(gpt_response) as f:
            test_data = json.load(f).get("test_data_rows", [])
    
    if models:
        models2code()
    if rules:
        rules2code()
    if test_data and response:
        current_path = Path(__file__)
        project_path = (current_path.parent.parent.parent).resolve()
        sys.path.append(str(project_path))
        print(f'\n\nTest Data Loader here\nproject_path: {project_path}\ncwd: {os.getcwd()}')
        assert str(project_path) == os.getcwd(), "must cd to project_path"
        print("\nPYTHONPATH..")
        for p in sys.path:
            print(".." + p)                 

        import logging
        logging_config = f'{project_path}/config/logging.yml'
        with open(logging_config,'rt') as f:  # see also logic/declare_logic.py
                config=yaml.safe_load(f.read())
                f.close()
        logging.config.dictConfig(config)  # log levels: notset 0, debug 10, info 20, warn 30, error 40, critical 50
        logic_logger = logging.getLogger('logic_logger')
        logic_logger.setLevel(logging.INFO)

        logging.getLogger('sqlalchemy.engine.Engine').disabled = True  # remove for additional logging

        current_file_path = Path(os.path.dirname(__file__))
        db_url_path = project_path.joinpath('database/test_data/db.sqlite')
        db_url = f'sqlite:///{project_path}/database/test_data/db.sqlite'
        print(f'\ncreating {str(db_url_path)} at current_file_path: {current_file_path}')
        print(f'..  db_url: {db_url}')

        if db_url_path.is_file():
            db_url_path.unlink()
        engine = create_engine(db_url)
        # engine = create_engine(f'sqlite:///{current_file_path}/db.sqlite')
        Base.metadata.create_all(engine)

        Session = sessionmaker(bind=engine)
        session = Session()

        # from config.activate_logicbank import activate_logicbank  # ERROR: Working outside of application context.

        from logic import declare_logic_create_test_data as declare_logic  # FIXME disable handle_all (approach??)

        from logic_bank.logic_bank import LogicBank
        LogicBank.activate(session=session, 
                            activator=declare_logic.declare_logic)
        print("\nLogicBank Activated\n\n")

        """
        Execute with:
        python tools/response2code.py --test-data --response docs/response.json
        """

        if no_flask := True:  # this works, but flask approach fails
            # exec_test_data(test_data)  #  no, requires flask
            exec_test_data_no_flask(test_data, session)
            # import test_data_rows as test_data_rows
            # test_data_rows.load_data(session)  # or, this also works
        else:  # this fails because the db_uri is wrong - contains 'instance'
            if old_setup := True:
                project_dir = Path(response).parent.parent
                os.chdir(project_dir)
                db_uri = project_dir.resolve() / 'database/test_data/db.sqlite'
                
                if not db_uri.exists():
                    log.warning(f"Database file not found: {db_uri}")
                           
            os.environ['SQLALCHEMY_DATABASE_URI'] = db_url  # f'sqlite:///{db_uri}'
            print('setting up flask: SQLALCHEMY_DATABASE_URI:', os.environ['SQLALCHEMY_DATABASE_URI'])
            os.environ['AGGREGATE_DEFAULTS'] = 'True'
            from tools.alp_init import flask_app
         
            with flask_app.app_context():
                db_loc_debug = safrs.DB  # FIXME FIXME, what is instance, and where did it come from?
                # engine: Engine(sqlite:////Users/val/dev/ApiLogicServer/ApiLogicServer-dev/build_and_test/ApiLogicServer/Customer_Order_System/instance/../database/db.sqlite)
                safrs.DB.create_all()    
                exec_test_data(test_data)
                
                #print(safrs.DB.session.get_bind())
            
    elif test_data:
        log.warning("Response file not provided. Skipping test_data2code.")


if __name__ == "__main__":
    main()
