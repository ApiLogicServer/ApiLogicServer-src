# https://stackoverflow.com/questions/51142320/how-to-instantiate-class-by-its-string-name-in-python-from-current-file
from integration.actions import * 
import importlib
from pathlib import Path


'''
put this in declare_logic.py:


    def call_action(row: Customer, old_row: Customer, logic_row: LogicRow):
        import integration.actions.action_exec as action_exec
        if (True):
            action_exec.factory('Action1', logic_row)
            
    Rule.after_flush_row_event(on_class=Customer, calling=call_action)  # see above    

'''
logic = []

def discover_actions():
    global logic
    import os
    logic_path = Path(__file__).parent
    for root, dirs, files in os.walk(logic_path):
        for file in files:
            if file.endswith(".py"):
                spec = importlib.util.spec_from_file_location("module.name", logic_path.joinpath(file))
                if file.endswith("action_exec.py"):
                    pass
                else:
                    logic.append(file)
                    each_logic_file = importlib.util.module_from_spec(spec)
                    # spec.loader.exec_module(each_logic_file)  # runs "bare" module code (e.g., initialization)
                    # each_logic_file.declare_logic()  # invoke create function
    print(f"..discovered logic: {logic}")
    return

discover_actions()
# <module 'integration.actions' from '/Users/val/dev/ApiLogicServer/ApiLogicServer-dev/webg-local/webg-projects/by-ulid/01JCHQS2MC4MPJJ0PQ4MKM81HV/integration/actions/__init__.py'>

def factory(classname, logic_row):
    global logic
    # Check if the class is in the current module's globals
    if classname in globals():
        cls = globals()[classname]
    else:
        # Import the actions module and get the class from it
        from integration import actions
        cls = getattr(actions, classname)


    new_variable = "a value"
    globals_db = globals()  # should be objects in this module
    for each_global in globals_db:
        print(f"globals_db: {each_global}")
    cls = globals()[classname]

    from integration import actions
    actions_db  = actions
    cls = getattr(actions, classname)
    return cls().run('classname', logic_row)