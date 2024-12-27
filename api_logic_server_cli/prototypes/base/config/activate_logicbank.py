import logging
import os
from logic_bank.logic_bank import LogicBank
from logic_bank.exceptions import LBActivateException

app_logger = logging.getLogger("api_logic_server_app")

def activate_logicbank(session, constraint_handler):
    
    from logic import declare_logic
            
    logic_logger = logging.getLogger('logic_logger')
    logic_logger_level = logic_logger.getEffectiveLevel()
    
    disable_rules = os.getenv('APILOGICPROJECT_DISABLE_RULES', '').lower() in ['1', 't', 'true', 'y', 'yes']
    if disable_rules:
        app_logger.info("LogicBank rules disabled")
        return

    app_logger.info("LogicBank Activation - declare_logic.py")
    try:          # hover activate for info
        LogicBank.activate(session=session, activator=declare_logic.declare_logic, constraint_event=constraint_handler)
    except LBActivateException as e:
        app_logger.error("Logic Bank Activation Error")
        if e.invalid_rules: logic_logger.error(f"Invalid Rules:  {e.invalid_rules}")
        if e.missing_attributes: logic_logger.error(f"Missing Attrs: {e.missing_attributes}")
        
    except Exception as e:
        app_logger.error(f"Logic Bank Activation Error: {e}")
        app_logger.exception(e)
        raise e
    logic_logger.setLevel(logic_logger_level)
    