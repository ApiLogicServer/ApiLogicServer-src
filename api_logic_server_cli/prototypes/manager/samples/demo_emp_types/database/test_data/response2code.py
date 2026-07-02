#!/usr/bin/env python
#
# Convert a GPT response (WGResult) to code
# This script reads a GPT response JSON file and generates Python code that can be used to add the test data to the database.
# 
# # Generate test data code from a GPT response JSON file:
# python database/test_data/response2code.py --test-data --response=docs/Customer_Order_System_003.response
# # Run the generated test data code:
# python database/test_data/test_data_code.py

# soon: 
# cd project_dir
# export APILOGICPROJECT_NO_FLASK=1
# als genai-utils --rebuild-test-data --response=docs/genai_demo_informal_003.response
#
import ast
import json
import sys
import os
import logging
import logging.config
import click
from pathlib import Path

logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger("response2code")

source_code_preamble = open(Path(__file__).parent / 'test_data_preamble.py').read()

add_instance_code_template = """
    try:
        if not {hash} in succeeded_hashes:  # avoid duplicate inserts
            instance = {code}
            session.add(instance)
            session.commit()
            succeeded_hashes.add({hash})
    except Exception as e:
        has_errors = True
        if 'UNIQUE' in str(e) and restart_count > 1:
            pass
        else:
            error_str = f"Error adding variable to session: {{e}}"
            if not error_str in data_log:
                data_log.append(error_str)
        if not restart_count in [2,3]:
            session.rollback()
"""


def fix_code(code):
    """
    Fix syntax errors in code
    """
    ori_code = code
    try:
        ast.parse(code)
        return code
    except SyntaxError:
        log.warning(f"Syntax error in code (1): {code}")
    
    code = ori_code.replace("'s", "''s")
    try:
        ast.parse(code)
        return code
    except SyntaxError:
        log.warning(f"Syntax error in code (2): {code}")
    
    code = ori_code.replace("'", "")
    try:
        ast.parse(code)
        return code
    except SyntaxError:
        log.warning(f"Syntax error in code (3): {code}")

    code = ori_code.replace('"', '')
    try:
        ast.parse(code)
        return code
    except SyntaxError:
        log.warning(f"Syntax error in code (4): {code}")

    return None

def write_test_data(test_data):
    test_data_code = source_code_preamble
    
    for row in test_data:
        try:
            fixed_code = fix_code(row.get("code",''))
            if not fixed_code:
                continue
        except Exception as e:
            log.warning(f"Error fixing code: {e}")
            continue
        test_data_code += add_instance_code_template.format(code=fixed_code, hash=hash(fixed_code))

    test_data_code += f"print('\\n'.join(data_log))\n"
    test_data_code += "with open(project_dir / 'database/test_data/test_data_code_log.txt', 'w') as log_file:\n"
    test_data_code += "    log_file.write('\\n'.join(data_log))\n"
    test_data_code += "print('\\n'.join(data_log))\n"


    test_data_file = 'database/test_data/test_data_code.py'
    
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
        response = '../docs/response.json'
    
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