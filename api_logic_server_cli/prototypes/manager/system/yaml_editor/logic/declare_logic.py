import datetime
from decimal import Decimal
from logic_bank.exec_row_logic.logic_row import LogicRow
from logic_bank.extensions.rule_extensions import RuleExtension
from logic_bank.logic_bank import Rule
from database import models
import api.system.opt_locking.opt_locking as opt_locking
from security.system.authorization import Grant
import logging
from base64 import b64decode
from requests import get

app_logger = logging.getLogger(__name__)
encoding = 'utf-8'
declare_logic_message = "ALERT:  *** No Rules Yet ***"  # printed in api_logic_server.py

def declare_logic():
    ''' Declarative multi-table derivations and constraints, extensible with Python.
 
    Brief background: see readme_declare_logic.md
    
    Your Code Goes Here - Use code completion (Rule.) to declare rules
    '''

    def handle_all(logic_row: LogicRow):  # OPTIMISTIC LOCKING, [TIME / DATE STAMPING]
        """
        This is generic - executed for all classes.

        Invokes optimistic locking.

        You can optionally do time and date stamping here, as shown below.

        Args:
            logic_row (LogicRow): from LogicBank - old/new row, state
        """
        if logic_row.is_updated() and logic_row.old_row is not None and logic_row.nest_level == 0:
            opt_locking.opt_lock_patch(logic_row=logic_row)
        enable_creation_stamping = True  # CreatedOn time stamping
        if enable_creation_stamping:
            row = logic_row.row
            if logic_row.ins_upd_dlt == "ins" and hasattr(row, "createDate"):
                row.createDate = datetime.datetime.now()
                logic_row.log("early_row_event_all_classes - handle_all sets 'createDate"'')
        
        Grant.process_updates(logic_row=logic_row)

    Rule.early_row_event_all_classes(early_row_event_all_classes=handle_all)

    def validate_yaml(row:models.YamlFiles, old_row:models.YamlFiles, logic_row:LogicRow):
        import yaml
        if logic_row.ins_upd_dlt in ["ins","upd"]:
            #yaml_content = str(b64decode(row.content), encoding=encoding) if row.content else None 
            if row.content:
                try:
                    yaml.safe_load(row.content)
                    row.size = len(row.content)
                    row.upload_flag = True
                    return True
                except yaml.YAMLError as exc:
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
    Rule.constraint(models.YamlFiles, calling=validate_yaml, error_msg="Invalid yaml file")
    #als rules report
    from api.system import api_utils
    api_utils.rules_report()

    app_logger.debug("..logic/declare_logic.py (logic == rules + code)")
