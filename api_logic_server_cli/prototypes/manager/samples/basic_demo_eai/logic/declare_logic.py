import os
from logic.load_verify_rules import load_verify_rules
import logging

app_logger = logging.getLogger(__name__)

declare_logic_message = "ALERT:  *** No Rules Yet ***"  # printed in api_logic_server.py

def declare_logic():
    ''' Declarative multi-table derivations and constraints, extensible with Python.

    Brief background: see readme_declare_logic.md

    You can put quick-and-dirty rules directly here, but best practice is to use
    Discovery: add a file per use case in logic/logic_discovery/ (e.g., check_credit.py),
    and it is loaded automatically - see readme_logic_discovery.md
    '''

    if os.environ.get("WG_PROJECT"):
        # Inside WG: Load rules from docs/expprt/export.json
        load_verify_rules()
    else:
        # Outside WG: load declare_logic function
        from logic.logic_discovery.auto_discovery import discover_logic
        discover_logic()

    app_logger.debug("..logic/declare_logic.py (logic == rules + code)")
