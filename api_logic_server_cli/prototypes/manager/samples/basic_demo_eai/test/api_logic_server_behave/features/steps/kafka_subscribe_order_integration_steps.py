from behave import *
import requests
import test_utils
import demo_eai_helpers as h

# Reuses from check_credit_steps.py: Given Customer "{}" with credit limit {}
# Wording is neutral ("delivered to topic"): the message goes live or simulated, and the report says which.


@when('an inbound order message for that customer is delivered to topic order_b2b with {q1:d} {p1} and {q2:d} {p2}')
def step_impl(context, q1, p1, q2, p2):
    """Delivers a two-item order_b2b message for the Customer (unique name) through the debug endpoint."""
    scenario_name = context.scenario.name
    test_utils.prt(f'\n{scenario_name}\n', scenario_name)
    h.deliver_message(context, context.customer['name'], [(p1, q1), (p2, q2)])


@when('an inbound order message for an unknown account is delivered to topic order_b2b')
def step_impl(context):
    """Delivers a message whose Account is not a Customer; it should be rejected."""
    scenario_name = context.scenario.name
    test_utils.prt(f'\n{scenario_name}\n', scenario_name)
    context.account = h.unique('No Such Account')
    h.deliver_message(context, context.account, [('Widget', 1)])


@when('an inbound message for an unknown account is delivered live to topic order_b2b')
def step_impl(context):
    """Live only: skips the scenario when no broker answers (not verified, not failed)."""
    scenario_name = context.scenario.name
    test_utils.prt(f'\n{scenario_name}\n', scenario_name)
    context.account = h.unique('No Such Account')
    h.deliver_message(context, context.account, [('Widget', 1)], mode='live')


@then('the message is processed')
def step_impl(context):
    """Consumer 2 (or the simulated function) parsed the message and saved the Order."""
    assert context.consumed, f'message not processed: error_text={context.error_text}'
    assert not context.error_text, context.error_text


@then('an Order for the customer has {count:d} items totalling {total:d}')
def step_impl(context, count, total):
    """The Customer's newest Order has the mapped Items; amounts come from the rules."""
    r = requests.get(f'{h.BASE}/api/Order/', params={"filter[customer_id]": context.customer['id'], "sort": "-id", "page[limit]": 1},
                     headers=h.headers())
    orders = r.json()['data']
    assert orders, 'no Order for the customer'
    order_id = int(orders[0]['id'])
    items = h.order_items(order_id)
    assert len(items) == count, f'expected {count} items, got {len(items)}'
    actual = float(h.order_attrs(order_id)['amount_total'])
    assert abs(actual - total) < 0.01, f'amount_total expected {total}, got {actual}'


@then('the message is rejected with a reason')
def step_impl(context):
    """Rejected: not consumed, and the reason is available (error_text live, the response's error simulated)."""
    assert not context.consumed, 'the message for an unknown account was accepted'
    assert context.error_text, 'no reason recorded for the rejection'


@then('the blob stays unprocessed with error_text')
def step_impl(context):
    """Live Tx 2 rolled back: the blob is still is_processed = 0 and carries the reason."""
    assert context.blob_id, 'no blob'
    r = requests.get(f'{h.BASE}/api/OrderB2bMessage/{context.blob_id}/', headers=h.headers())
    a = r.json()['data']['attributes']
    assert not a['is_processed'], 'blob was marked processed'
    assert a['error_text'], 'error_text is empty'
