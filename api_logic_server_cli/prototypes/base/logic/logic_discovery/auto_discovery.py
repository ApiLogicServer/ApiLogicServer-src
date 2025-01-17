import importlib
from pathlib import Path
import logging

app_logger = logging.getLogger(__name__)

def discover_logic():
    """
    Discover additional logic in this directory
    """
    import os
    logic = []
    logic_path = Path(__file__).parent
    for root, dirs, files in os.walk(logic_path):
        for file in files:
            if file.endswith(".py"):
                spec = importlib.util.spec_from_file_location("module.name", logic_path.joinpath(file))
                if file.endswith("auto_discovery.py"):
                    pass
                else:
                    logic.append(file)
                    each_logic_file = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(each_logic_file)  # runs "bare" module code (e.g., initialization)
                    each_logic_file.declare_logic()  # invoke create function

    if False and Path(__file__).parent.parent.parent.joinpath("docs/project_is_genai_demo.txt").exists():
        return  # for genai_demo, logic is in logic/declare_logic.py (so ignore logic_discovery)
    
    wg_logic_path = Path(__file__).parent.parent.joinpath("wg_rules")
    for root, dirs, files in os.walk(wg_logic_path):
        for file in files:
            if file.endswith(".py"):
                spec = importlib.util.spec_from_file_location("module.name", wg_logic_path.joinpath(file))
                if file.endswith("auto_discovery.py"):
                    pass
                else:
                    logic.append(file)
                    each_logic_file = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(each_logic_file)  # runs "bare" module code (e.g., initialization)
                    each_logic_file.init_rule()  # invoke create function

    app_logger.info(f"..discovered logic: {logic}")
    return
