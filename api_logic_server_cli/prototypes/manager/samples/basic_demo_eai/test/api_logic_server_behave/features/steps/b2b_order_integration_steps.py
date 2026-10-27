from behave import *
import requests
import test_utils
import demo_eai_helpers as h

# Patterns: the multi-item pattern comes BEFORE the single-item one (behave uses the first pattern that fits).


@when('Partner order posted via OrderB2B for account "{account}" with {q1:d} {p1} and {q2:d} {p2}')
def step_impl(context, account, q1, p1, q2, p2):
    """Posts a two-item partner order to the OrderB2B API, using the Customer's unique test name as Account."""
    scenario_name = context.scenario.name
    test_utils.prt(f'\n{scenario_name}\n', scenario_name)
    context.response = h.place_b2b_order(context.customer['name'], [(p1, q1), (p2, q2)])
    context.order_id = None
    if context.response.status_code == 200:
        context.order_id = context.response.json()['meta']['result']['order_id']


@when('Partner order posted via OrderB2B for unknown account "{account}" with {qty:d} {product}')
def step_impl(context, account, qty, product):
    """Posts a partner order for an Account that is not a Customer (unique name: it must not exist)."""
    scenario_name = context.scenario.name
    test_utils.prt(f'\n{scenario_name}\n', scenario_name)
    context.account = h.unique(account)
    newest = requests.get(f'{h.BASE}/api/Order/', params={"sort": "-id", "page[limit]": 1}, headers=h.headers()).json()['data']
    context.newest_order_before = int(newest[0]['id']) if newest else 0
    context.response = h.place_b2b_order(context.account, [(product, qty)])
    context.order_id = None


@then('OrderB2B reports an Order with 2 items for the customer')
def step_impl(context):
    """The API response names the Customer and the item count."""
    assert context.response.status_code == 200, f'{context.response.status_code}: {context.response.text}'
    result = context.response.json()['meta']['result']
    assert result['customer'] == context.customer['name'], f'customer: {result}'
    assert result['items_count'] == 2, f'items_count: {result}'


@then('Items are mapped to Products Widget and Gadget with quantities 2 and 1')
def step_impl(context):
    """Items.Name -> Product by name, Items.QuantityOrdered -> Item.quantity, unit_price copied from the Product."""
    items = h.order_items(context.order_id)
    by_qty = {int(i['quantity']): i for i in items}
    assert set(by_qty) == {1, 2}, f'quantities: {sorted(by_qty)}'
    assert float(by_qty[2]['unit_price']) == 90.0 and float(by_qty[2]['amount']) == 180.0, f'Widget item: {by_qty[2]}'
    assert float(by_qty[1]['unit_price']) == 150.0 and float(by_qty[1]['amount']) == 150.0, f'Gadget item: {by_qty[1]}'


@then('OrderB2B answers HTTP 400 and no Order is created')
def step_impl(context):
    """A rejected partner order must look rejected (HTTP 400) and leave nothing behind."""
    r = context.response
    assert r.status_code == 400, f'expected HTTP 400, got {r.status_code}: {r.text}'
    assert 'Failed to create B2B order' in r.text, r.text
    newest = requests.get(f'{h.BASE}/api/Order/', params={"sort": "-id", "page[limit]": 1}, headers=h.headers()).json()['data']
    newest_id = int(newest[0]['id']) if newest else 0
    assert newest_id <= context.newest_order_before, 'an Order was created for an unknown account'
