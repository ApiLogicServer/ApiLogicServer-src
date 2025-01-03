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
from colorama import Fore, Style
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
        db_uri = project_dir.resolve() / 'database/db.sqlite'
        
        if not db_uri.exists():
            log.warning(f"Database file not found: {db_uri}")
            
        
        os.environ['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_uri}'
        os.environ['AGGREGATE_DEFAULTS'] = 'True'
        from tools.alp_init import flask_app
        
        
        with flask_app.app_context():
            safrs.DB.create_all()    
            exec_test_data(test_data)
            
            #print(safrs.DB.session.get_bind())
            
    elif test_data:
        log.warning("Response file not provided. Skipping test_data2code.")


if __name__ == "__main__":
    main()
