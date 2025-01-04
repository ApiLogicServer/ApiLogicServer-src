import datetime
from decimal import Decimal
from logic_bank.exec_row_logic.logic_row import LogicRow
from logic_bank.extensions.rule_extensions import RuleExtension
from logic_bank.logic_bank import Rule
from database import models
import api.system.opt_locking.opt_locking as opt_locking
from security.system.authorization import Grant, Security
import logging, os
from base64 import b64decode
from requests import get, post
import yaml

app_logger = logging.getLogger(__name__)
encoding = 'utf-8'
declare_logic_message = "ALERT:  *** No Rules Yet ***"  # printed in api_logic_server.py

def declare_logic():
    ''' Declarative multi-table derivations and constraints, extensible with Python.
 
    Brief background: see readme_declare_logic.md
    
    Your Code Goes Here - Use code completion (Rule.) to declare rules
    '''

    from logic.logic_discovery.auto_discovery import discover_logic
    discover_logic()
    def handle_all(logic_row: LogicRow):  # OPTIMISTIC LOCKING, [TIME / DATE STAMPING]
        """
        This is generic - executed for all classes.

        Invokes optimistic locking.

        You can optionally do time and date stamping here, as shown below.

        Args:
            logic_row (LogicRow): from LogicBank - old/new row, state
        """

        if not os.getenv("APILOGICPROJECT_NO_FLASK") is not None:
            return  # enables rules to be used outside of Flask, e.g., test data loading

        if logic_row.is_updated() and logic_row.old_row is not None and logic_row.nest_level == 0:
            opt_locking.opt_lock_patch(logic_row=logic_row)
        enable_creation_stamping = True  # CreatedOn time stamping
        if enable_creation_stamping:
            row = logic_row.row
            if logic_row.ins_upd_dlt == "ins" and hasattr(row, "createdate"):
                #row.createdate = datetime.datetime.now()
                logic_row.log("early_row_event_all_classes - handle_all sets 'createdate"'')
        
        Grant.process_updates(logic_row=logic_row)

    Rule.early_row_event_all_classes(early_row_event_all_classes=handle_all)

    def validate_yaml(row:models.YamlFiles, old_row:models.YamlFiles, logic_row:LogicRow):
        if logic_row.ins_upd_dlt in ["ins"] and (row.download_flag is None or row.download_flag == False):
            if row.content:
                yaml_content = str(b64decode(row.content), encoding=encoding) if row.content else None 
                try:
                    ont_yaml = yaml.safe_load(yaml_content)
                    if ont_yaml.get('entities') is None:
                        app_logger.debug("The yaml file must be a valid app_model.yaml file")
                        return False
                    row.size = len(yaml_content)
                    row.upload_flag = False
                    row.download_flag = False
                    row.content = yaml_content
                    return True
                except yaml.YAMLError as exc:
                    row.content = None
                    return False    
            return False
        return True

            
    def export_yaml(row:models.YamlFiles, old_row:models.YamlFiles, logic_row:LogicRow):
        if logic_row.is_updated and row.download_flag and old_row.download_flag == False and row.content != None:
            from api.api_discovery.ontimize_api import export_yaml_to_file
            from pathlib import Path
            running_at = Path(__file__)
            project_dir = running_at.parent.parent
            row.downloaded = export_yaml_to_file(project_dir=project_dir)
                
    Rule.row_event(models.YamlFiles, calling=export_yaml)
    Rule.constraint(models.YamlFiles, calling=validate_yaml, error_msg="Invalid app_model.yaml file")
    

    app_logger.debug("..logic/declare_logic.py (logic == rules + code)")

