from behave import *
import demo_eai_helpers as h
import requests
import test_utils

# Product prices (verified with sqlite3): Widget 90, Gadget 150


@given('Customer "{customer_name}" with credit limit {limit:d}')
def step_impl(context, customer_name, limit):
    """Creates a fresh Customer (unique name) with the given credit limit; kept by short name for multi-customer scenarios."""
    context.customer = h.create_customer(customer_name, limit)
    context.customers = getattr(context, 'customers', {})
    context.customers[customer_name] = context.customer
    context.order_id = None
    context.response = None


@given('Order is created for "{customer_name}" with {qty:d} {product}')
def step_impl(context, customer_name, qty, product):
    """Creates the Order through the OrderB2B API (the rules fire on creation)."""
    scenario_name = context.scenario.name
    test_utils.prt(f'\n{scenario_name}\n', scenario_name)
    customer = context.customers.get(customer_name, context.customer)
    r = h.place_b2b_order(customer['name'], [(product, qty)])
    assert r.status_code == 200, f'order not created: {r.status_code} {r.text}'
    context.order_id = r.json()['meta']['result']['order_id']


@when('B2B order placed for "{customer_name}" with {qty:d} {product}')
def step_impl(context, customer_name, qty, product):
    """Places the Order through the OrderB2B API; keeps the response (a rejection is a valid outcome)."""
    scenario_name = context.scenario.name
    test_utils.prt(f'\n{scenario_name}\n', scenario_name)
    context.response = h.place_b2b_order(context.customer['name'], [(product, qty)])
    context.order_id = None
    if context.response.status_code == 200:
        context.order_id = context.response.json()['meta']['result']['order_id']


@when('Item quantity changed to {qty:d}')
def step_impl(context, qty):
    """PATCHes the quantity of the Order's (only) Item."""
    item = h.order_items(context.order_id)[0]
    body = {"data": {"type": "Item", "id": str(item['id']), "attributes": {"quantity": qty}}}
    r = requests.patch(f'{h.BASE}/api/Item/{item["id"]}/', json=body, headers=h.headers())
    assert r.status_code == 200, f'item update failed: {r.status_code} {r.text}'


@when('Order is shipped')
def step_impl(context):
    """PATCHes date_shipped on the Order."""
    body = {"data": {"type": "Order", "id": str(context.order_id), "attributes": {"date_shipped": "2026-10-24"}}}
    r = requests.patch(f'{h.BASE}/api/Order/{context.order_id}/', json=body, headers=h.headers())
    assert r.status_code == 200, f'ship failed: {r.status_code} {r.text}'


@then('Customer balance should be {expected:d}')
def step_impl(context, expected):
    """The Customer's balance is derived by rules."""
    actual = float(h.customer_attrs(context.customer['id'])['balance'] or 0)
    assert abs(actual - expected) < 0.01, f'balance expected {expected}, got {actual}'


@then('Order amount_total should be {expected:d}')
def step_impl(context, expected):
    """The Order total is the sum of its Item amounts."""
    assert context.order_id, 'order was not created'
    actual = float(h.order_attrs(context.order_id)['amount_total'] or 0)
    assert abs(actual - expected) < 0.01, f'amount_total expected {expected}, got {actual}'


@then('Order is rejected with a credit limit message')
def step_impl(context):
    """The constraint rejects the order: HTTP 400 and the credit limit message."""
    r = context.response
    assert r.status_code == 400, f'expected HTTP 400, got {r.status_code}: {r.text}'
    assert 'exceeds credit limit' in r.text, f'credit limit message missing: {r.text}'
