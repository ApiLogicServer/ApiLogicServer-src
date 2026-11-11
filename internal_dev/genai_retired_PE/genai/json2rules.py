#!/usr/bin/env python
#
# Convert a WG exported JSON file to Python rules:
# This script reads an exported JSON file and generates Python rules that can be used to add the rules to the logicbank.
# We only consider active rules.
#
import sys
import json
import logging
from pathlib import Path

log = logging.getLogger(__name__)
DEFAULT_EXPORT_JSON_PATH = Path('docs/export/export.json')

declare_logic_template = """
from logic.declare_logic import *

def declare_logic():
    '''
        Imported rules
    '''
    {code}
"""

rule_template = """
# {name}
# {description}
{code}
"""

def get_exported_rules(export_json = None):
    """
    Read the exported rules from export.json and 
    write the code to the rule_code_dir
    """
    if not export_json:
        export_json = Path(DEFAULT_EXPORT_JSON_PATH)
    if not export_json.exists():
        log.warning(f"{export_json.resolve()} does not exist")
        return

    try:
        with open(export_json) as f:
            export = json.load(f)
        rules = export.get("rules", [])
    except Exception as exc:
        log.warning(f"Failed to load rules from {export_json}: {exc}")
        return []

    rules = [rule for rule in rules if rule["status"] == "active"]
    
    return rules


def write_rules(rules, rule_code_dir = None):
    """
    Write the rules to the rule_code_dir
    """
    if not rule_code_dir:
        rule_code_dir = Path('logic')
    if not rule_code_dir.exists():
        rule_code_dir.mkdir(parents=True)

    rules_code = ""
    for rule in rules:
        rule_code = rule["code"]
        rule_name = rule["name"]
        rule_desc = rule.get("description","").replace("\n", " ")
        
        export_code = rule_template.format(code=rule_code, name=rule_name, description=rule_desc)
        export_code = "    ".join(export_code.splitlines(True))
        rules_code += export_code
    
    rules_code_file = rule_code_dir / f"exported.py"
    with open(rules_code_file, 'w') as f:
        f.write(declare_logic_template.format(code=rules_code))
        
    log.info(f"Successfully wrote rule code to {rules_code_file}")

def json2rules(export_json = None, rule_code_dir = None):
    rules = get_exported_rules(export_json)
    if not rules:
        log.warning("No active rules found")
        return
    write_rules(rules, rule_code_dir)

if __name__ == "__main__":
    export_json = Path(sys.argv[1]) if len(sys.argv) > 1 else None
    rule_code_dir= sys.argv[2] if len(sys.argv) > 2 else None
    json2rules(export_json, rule_code_dir)
    
    
    