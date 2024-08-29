from behave import *
import requests, pdb
import json
import test_utils

host = "localhost"
port = "5656"

@given('Database and Set of Tests')
def step_impl(context):
    pass

@when('Run Configuration: Behave Tests')
def step_impl(context):
    """
    TBD Observe the logic log to see that it creates audit rows:

    1. **Discouraged:** you can implement auditing with events.  But auditing is a common pattern, and this can lead to repetitive, tedious code
    2. **Preferred:** approaches use [extensible rules](https://github.com/valhuber/LogicBank/wiki/Rule-Extensibility#generic-event-handlers).

    Generic event handlers can also reduce redundant code, illustrated in the time/date stamping `handle_all` logic.

    This is due to the `copy_row` rule.  Contrast this to the *tedious* `audit_by_event` alternative:

    <figure><img src="https://github.com/ApiLogicServer/Docs/blob/main/docs/images/behave/salary_change.png?raw=true"></figure>

    > **Key Takeaway:** use **extensible own rule types** to automate pattern you identify; events can result in tedious amounts of code.

    """
    scenario_name = 'Run Configuration: Behave Tests'
    context.scenario_name = 'Run Configuration: Behave Tests' 


@then("No Errors")
def step_impl(context):
    print("\n\n Behave Run Successfully Completed")
    print("..(console log stacktraces are successful negative tests)")
    test_utils.prt("\n\n Server Log: Behave Run Successfully Completed - now run Behave Logic Report", context.scenario_name)
