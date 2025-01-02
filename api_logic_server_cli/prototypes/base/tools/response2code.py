#!/usr/bin/env python
#
# Convert a GPT response (WGResult) to code
#
# python tools/response2code.py docs/response.json
import ast
import json
import sys
import logging
import click
import safrs
import os
from pathlib import Path

sys.path.append('.')

from database.models import *
from datetime import date

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


def exec_test_data(test_data):
    variables = []
    for row in test_data:
        source_code = row.get("code")
        print('>' , source_code)
        try:
            exec(source_code)
            assignments = get_top_level_assignments(source_code)
            variables.extend(assignments.keys())
        except Exception as e:
            log.warning(f"Error executing source code: {e}")
            continue
        
    for variable in variables:
        try:
            safrs.DB.session.add(locals()[variable])
            safrs.DB.session.commit()
        except Exception as e:
            log.warning(f"Error adding variable to session: {e}")
    
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
        """
        Execute with:
        python tools/response2code.py --test-data --response docs/response.json
        """
        project_dir = Path(response).parent.parent
        os.chdir(project_dir)
        db_uri = f'sqlite:///{project_dir.resolve()}/database/db.sqlite'
        #db_uri = f'sqlite:////tmp/db2.sqlite'
        
        os.environ['SQLALCHEMY_DATABASE_URI'] = db_uri
        os.environ['AGGREGATE_DEFAULTS'] = 'True'
        from tools.alp_init import flask_app
        
        print(os.getcwd())
        print(flask_app.config['SQLALCHEMY_DATABASE_URI'])
        
        with flask_app.app_context():
            safrs.DB.create_all()    
            exec_test_data(test_data)
            
            print(safrs.DB.session.get_bind())
            
    elif test_data:
        log.warning("Response file not provided. Skipping test_data2code.")


if __name__ == "__main__":
    main()
