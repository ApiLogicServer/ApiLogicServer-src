#
# This code loads and verifies rules from export.json and activates them if they pass verification
# It is WebGenAI specific, used only when env var WG_PROJECT is set
#
import ast
import json
import logging
import os
import sys
import safrs
import subprocess
from importlib import import_module
from pathlib import Path
from werkzeug.utils import secure_filename
from database.models import *
from logic_bank.logic_bank import DeclareRule, Rule, LogicBank
from colorama import Fore, Style, init
from logic_bank.logic_bank import RuleBank
from logic_bank.rule_bank.rule_bank_setup import find_referenced_attributes
import tempfile


app_logger = logging.getLogger(__name__)
declare_logic_message = "ALERT:  *** No Rules Yet ***"  # printed in api_logic_server.py

rule_import_template = """
from logic_bank.logic_bank import Rule
from database.models import *

def init_rule():
{rule_code}
"""

MANAGER_PATH = "/opt/webgenai/database/manager.py"
EXPORT_JSON_PATH = os.environ.get("EXPORT_JSON_PATH", "./docs/export/export.json")


def set_rule_status(rule_id, status):
    """
    Call the manager.py script to set the status of a rule 
    
    (if the status is "active", the manager will remove the rule error)
    """
    if not Path(MANAGER_PATH).exists():
        app_logger.info(f"No manager, can't set rule {rule_id} status {status}")
        return
    subprocess.run([
            "python", MANAGER_PATH, 
            "-R", rule_id,
            "--rule-status", status],
            cwd="/opt/webgenai")


def set_rule_error(rule_id, error):
    """
    Call the manager.py script to set the error of a rule
    """
    if not Path(MANAGER_PATH).exists():
        app_logger.warning(f"No manager, can't set rule {rule_id} error {error}")
        return
    subprocess.check_output([
                "python", MANAGER_PATH, 
                "-R", rule_id,
                "--rule-error", error],
                cwd="/opt/webgenai")


def check_rule_code_syntax(rule_code):
    """
    Check the syntax of the rule code
    """
    try:
        ast.parse(rule_code)
        return rule_code
    except Exception as exc:
        log.warning(f"Syntax error in rule code '{rule_code}': {exc}")
    
    rule_code = rule_code.replace("\\\\", "\\")
    try:
        ast.parse(rule_code)
        return rule_code
    except Exception as exc:
        log.warning(f"Syntax error in rule code '{rule_code}': {exc}")
        return None


def get_exported_rules(rule_code_dir):
    """
    Read the exported rules from export.json and write the code to the 
    rule_code_dir
    """
    export_file = Path(EXPORT_JSON_PATH)
    if not export_file.exists():
        app_logger.info(f"{export_file.resolve()} does not exist")
        return []

    try:
        with open(export_file) as f:
            export = json.load(f)
        rules = export.get("rules", [])
    except Exception as exc:
        app_logger.warning(f"Failed to load rules from {export_file}: {exc}")
        return []

    for rule in rules:
        if rule["status"] == "rejected":
            continue
        rule_file = rule_code_dir / f"{secure_filename(rule['name']).replace('.','_')}.py"
        try:
            # write current rule to rule_file
            # (we can't use eval, because logicbank uses inspect)
            rule_code_str = check_rule_code_syntax(rule["code"])
            if not rule_code_str:
                continue
            with open(rule_file, "w") as temp_file:
                rule_code = "\n".join([f"  {code}" for code in rule_code_str.split("\n")])
                temp_file.write(rule_import_template.format(rule_code=rule_code))
                temp_file_path = temp_file.name
            # module_name used to import current rule
            module_name = Path(temp_file_path).stem
            rule["module_name"] = module_name
            app_logger.info(f"{rule['id']} rule file: {rule_file}")
        except Exception as exc:
            app_logger.exception(exc)
            app_logger.warning(f"Failed to write rule code to {rule_file}: {exc}")
            
    return rules


def verify_rules(rule_code_dir, rule_type="accepted"):
    """
    Verify the rules from export.json and activate them if they pass verification
    
    Write the rule code to a temporary file and import it as a module
    """
    rules = get_exported_rules(rule_code_dir)
    
    for rule in rules:
        if not rule["status"] == rule_type:
            continue
        module_name = rule["module_name"]
        app_logger.info(f"\n{Fore.BLUE}Verifying rule: {module_name} - {rule['id']}{Style.RESET_ALL}")
        try:
            rule_module = import_module(module_name)
            rule_module.init_rule()
            LogicBank.activate(session=safrs.DB.session, activator=rule_module.init_rule)
            if rule["status"] != "active":
                set_rule_status(rule["id"], "active")
            app_logger.info(f"\n{Fore.GREEN}Activated rule {rule['id']}{Style.RESET_ALL}")
            
        except Exception as exc:
            app_logger.exception(exc)
            set_rule_error(rule["id"], f"{type(exc).__name__}: {exc}")
            app_logger.warning(f"{Fore.RED}Failed to verify {rule_type} rule code\n{rule['code']}\n{Fore.YELLOW}{type(exc).__name__}: {exc}{Style.RESET_ALL}")
            app_logger.debug(f"{rule}")
            rule["status"] = "accepted"
            rule["error"] = f"{type(exc).__name__}: {exc}"
        
    return rules
   
      
def load_active_rules(rule_code_dir, rules=None):
    """
    Load the active rules from export.json
    """
    if not rules:
        rules = get_exported_rules(rule_code_dir)
    for rule in rules:
        module_name = rule.get("module_name", None)
        if not rule["status"] == "active" or module_name is None:
            continue
        app_logger.info(f"{Fore.GREEN}Loading Rule Module {module_name} {rule['id']} {Style.RESET_ALL}")
        rule_module = import_module(module_name)
        try:
            rule_module.init_rule()
        except Exception as exc:
            app_logger.exception(exc)
            app_logger.warning(f"{Fore.RED}Failed to load active rule {rule['id']} {rule['code']} {Style.RESET_ALL}")
            set_rule_error(rule["id"], f"{type(exc).__name__}: {exc}")
            

def get_project_id():
    if os.environ.get("PROJECT_ID"):
        return os.environ.get("PROJECT_ID")
    
    return Path(os.getcwd()).name


def load_verify_rules():
    
    # Add FileHandler to root_logger
    log_file = Path(os.getenv("LOG_DIR",tempfile.mkdtemp())) / "load_verify_rules.log"
    file_handler = logging.FileHandler(log_file)
    root_logger = logging.getLogger()
    root_logger.addHandler(file_handler)
    
    rule_code_dir = Path("./logic/wg_rules") # in the project root
    rule_code_dir.mkdir(parents=True, exist_ok=True)
    sys.path.append(f"{rule_code_dir}")
    
    app_logger.info(f"Loading rules from {rule_code_dir.resolve()}")
    
    rules = []
    
    if os.environ.get("VERIFY_RULES") == "True":
        rules = verify_rules(rule_code_dir, rule_type="active")
        verify_rules(rule_code_dir, rule_type="accepted")
    else:
        try:
            load_active_rules(rule_code_dir, rules)
        except Exception as exc:
            app_logger.exception(exc)
            app_logger.warning(f"{Fore.RED}Failed to load active exported rules: {exc}{Style.RESET_ALL}")
            
    root_logger.removeHandler(file_handler)
    