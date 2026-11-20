from behave import *
import demo_eai_helpers as h


@when('the sales user lists Customers')
def step_impl(context):
    """Reads the Customer list as s1 (role sales), all pages."""
    r = h.requests.get(f'{h.BASE}/api/Customer/', params={"page[limit]": 1000}, headers=h.headers('s1'))
    assert r.status_code == 200, f'customer list failed: {r.status_code} {r.text}'
    context.listed = r.json()['data']


@then('"{shown1}" and "{shown2}" are listed, and "{hidden}" is not')
def step_impl(context, shown1, shown2, hidden):
    """The grants admit the high-limit and the owing customer, and hide the low-limit one."""
    ids = {int(each['id']) for each in context.listed}
    for name in (shown1, shown2):
        assert context.customers[name]['id'] in ids, f'{name} should be listed'
    assert context.customers[hidden]['id'] not in ids, f'{hidden} should not be listed'


@then('every listed Customer has credit_limit >= 3000 or balance > 0')
def step_impl(context):
    """No listed customer falls outside the grants."""
    for each in context.listed:
        a = each['attributes']
        assert float(a['credit_limit'] or 0) >= 3000 or float(a['balance'] or 0) > 0, f'not granted: {a}'
