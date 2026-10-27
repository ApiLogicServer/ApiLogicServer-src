from behave import *
import requests
import demo_eai_helpers as h

# Reuses from check_credit_steps.py: Given Customer "{}" with credit limit {}, Given Order is created for ...
# (context.customers maps each short name to the Customer created for this scenario)


@when('Sales user queries each Customer by name')
def step_impl(context):
    """Logs in as s1 (role sales) and looks up each test Customer by its unique name; keeps the short names it can see."""
    context.visible = set()
    for short_name, customer in context.customers.items():
        r = requests.get(f'{h.BASE}/api/Customer/', params={"filter[name]": customer['name']}, headers=h.headers('s1'))
        assert r.status_code == 200, f'query as sales failed: {r.status_code} {r.text}'
        if r.json()['data']:
            context.visible.add(short_name)


@then('Sales sees HighCredit and Owing but not LowCredit')
def step_impl(context):
    """Grants are OR'd: credit_limit >= 3000 (HighCredit) or balance > 0 (Owing); LowCredit matches neither."""
    assert context.visible == {'HighCredit', 'Owing'}, f'sales sees {sorted(context.visible)}'
