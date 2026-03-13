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
    aggregate_defaults = os.environ.get("AGGREGATE_DEFAULTS") == "True"
    all_defaults = os.environ.get("ALL_DEFAULTS") == "True"
    try:          # hover activate for info
        LogicBank.activate(session=session, 
                           activator=declare_logic.declare_logic, 
                           constraint_event=constraint_handler,
                           aggregate_defaults=aggregate_defaults,
                           all_defaults=all_defaults)
    except LBActivateException as e:
        app_logger.error("\nLogic Bank Activation Error -- see https://apilogicserver.github.io/Docs/WebGenAI-CLI/#recovery-options")
        if e.invalid_rules: logic_logger.error(f"Invalid Rules:  {e.invalid_rules}")
        if e.missing_attributes: logic_logger.error(f"Missing Attrs (try als genai-utils --fixup): {e.missing_attributes}")
        app_logger.error("\n")
        if not os.environ.get("VERIFY_RULES") == "True" and not os.environ.get("WG_PROJECT") == "True":
            # WG Rule Verification, continue if VERIFY_RULES is True or inside WebGenAI
            raise e
        
    except Exception as e:
        app_logger.error(f"Logic Bank Activation Error: {e}")
        app_logger.exception(e)
        if not os.environ.get("WG_PROJECT") == "True":
            # Continue if inside WebGenAI
            # see: https://apilogicserver.github.io/Docs/WebGenAI-CLI/#wg_rules-and-ide-rules
            raise e
    logic_logger.setLevel(logic_logger_level)
    
