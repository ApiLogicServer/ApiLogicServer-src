from behave import *
import demo_eai_helpers as h
import requests
import test_utils

# Product prices (verified with sqlite3): Widget 90, Gadget 150


@given('Customer "{customer_name}" with credit limit {limit:d}')
def step_impl(context, customer_name, limit):
    """Creates a fresh Customer (unique name) with the given credit limit; kept by short name for multi-customer scenarios."""
    h.open_log(context)
    context.customer = h.create_customer(customer_name, limit)
    context.customers = getattr(context, 'customers', {})
    context.customers[customer_name] = context.customer
    context.order_id = None
    context.response = None


@given('Order is created for "{customer_name}" with {qty1:d} {product1} and {qty2:d} {product2}')
def step_impl(context, customer_name, qty1, product1, qty2, product2):
    """Creates a two-Item Order through the OrderB2B API (multi-item: must precede the single-item step, Rule #0.5)."""
    h.open_log(context)
    customer = context.customers.get(customer_name, context.customer)
    r = h.place_b2b_order(customer['name'], [(product1, qty1), (product2, qty2)])
    assert r.status_code == 200, f'order not created: {r.status_code} {r.text}'
    context.order_id = r.json()['meta']['result']['order_id']


@given('Order is created for "{customer_name}" with {qty:d} {product}')
def step_impl(context, customer_name, qty, product):
    """Creates the Order through the OrderB2B API (the rules fire on creation)."""
    h.open_log(context)
    customer = context.customers.get(customer_name, context.customer)
    r = h.place_b2b_order(customer['name'], [(product, qty)])
    assert r.status_code == 200, f'order not created: {r.status_code} {r.text}'
    context.order_id = r.json()['meta']['result']['order_id']


@when('B2B order placed for "{customer_name}" with {qty:d} {product}')
def step_impl(context, customer_name, qty, product):
    """Places the Order through the OrderB2B API; keeps the response (a rejection is a valid outcome)."""
    h.open_log(context)
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


# --- Coverage-matrix steps: boundary, unship, delete, move to another parent, change product ---

def _product_id(name: str) -> int:
    """Product id by name (prices verified with sqlite3: Widget 90, Gadget 150)."""
    r = requests.get(f'{h.BASE}/api/Product/', params={"filter[name]": name}, headers=h.headers())
    assert r.status_code == 200 and r.json()['data'], f'product {name} not found: {r.status_code} {r.text}'
    return int(r.json()['data'][0]['id'])


def _item_for(order_id: int, product: str) -> dict:
    """The Order's Item for the named product."""
    pid = _product_id(product)
    items = [each for each in h.order_items(order_id) if int(each['product_id']) == pid]
    assert items, f'no {product} item on order {order_id}'
    return items[0]


def _patch(resource: str, row_id: int, attributes: dict) -> None:
    """PATCH attributes on a row through the JSON:API (the rules fire on the update)."""
    body = {"data": {"type": resource, "id": str(row_id), "attributes": attributes}}
    r = requests.patch(f'{h.BASE}/api/{resource}/{row_id}/', json=body, headers=h.headers())
    assert r.status_code == 200, f'{resource} update failed: {r.status_code} {r.text}'


@given('a second Order is created for "{customer_name}" with {qty:d} {product}')
def step_impl(context, customer_name, qty, product):
    """Creates a second Order for the Customer (no prt: the scenario's log was opened by the first Order)."""
    customer = context.customers.get(customer_name, context.customer)
    r = h.place_b2b_order(customer['name'], [(product, qty)])
    assert r.status_code == 200, f'second order not created: {r.status_code} {r.text}'
    context.second_order_id = r.json()['meta']['result']['order_id']


@given('Order has been shipped')
def step_impl(context):
    """Ships the Order (setup for unship): the Order leaves the balance."""
    _patch('Order', context.order_id, {"date_shipped": "2026-10-24"})


@when('Order is unshipped')
def step_impl(context):
    """Clears date_shipped: the Order enters the balance's where= set again."""
    _patch('Order', context.order_id, {"date_shipped": None})


@when('the {product} Item is deleted')
def step_impl(context, product):
    """DELETEs the Order's Item for the product: Order.amount_total and Customer.balance adjust down."""
    item = _item_for(context.order_id, product)
    r = requests.delete(f'{h.BASE}/api/Item/{item["id"]}/', headers=h.headers())
    assert r.status_code < 300, f'item delete failed: {r.status_code} {r.text}'


@when('Order is deleted')
def step_impl(context):
    """DELETEs the Order: the Customer balance adjusts down by the Order's amount_total."""
    r = requests.delete(f'{h.BASE}/api/Order/{context.order_id}/', headers=h.headers())
    assert r.status_code < 300, f'order delete failed: {r.status_code} {r.text}'


@when('Order is moved to Customer "{customer_name}"')
def step_impl(context, customer_name):
    """PATCHes the Order's customer_id FK: the OLD and the NEW Customer balances both adjust."""
    _patch('Order', context.order_id, {"customer_id": context.customers[customer_name]['id']})


@when('the {product} Item is moved to the second Order')
def step_impl(context, product):
    """PATCHes the Item's order_id FK: the OLD and the NEW Order totals both adjust."""
    item = _item_for(context.order_id, product)
    _patch('Item', item['id'], {"order_id": context.second_order_id})


@when('the Item product is changed to {product}')
def step_impl(context, product):
    """PATCHes the Item's product_id FK: the NEW Product's unit_price is re-copied, and the amounts follow."""
    item = h.order_items(context.order_id)[0]
    context.item_id = item['id']
    _patch('Item', item['id'], {"product_id": _product_id(product)})


@then('Order is accepted')
def step_impl(context):
    """The Order was created (HTTP 200): a balance equal to the credit limit is allowed (<=)."""
    r = context.response
    assert r.status_code == 200, f'expected the order to be accepted, got {r.status_code}: {r.text}'


@then('Customer "{customer_name}" balance should be {expected:d}')
def step_impl(context, customer_name, expected):
    """The named Customer's derived balance."""
    actual = float(h.customer_attrs(context.customers[customer_name]['id'])['balance'] or 0)
    assert abs(actual - expected) < 0.01, f'{customer_name} balance expected {expected}, got {actual}'


@then('second Order amount_total should be {expected:d}')
def step_impl(context, expected):
    """The second Order's total is the sum of its Item amounts."""
    actual = float(h.order_attrs(context.second_order_id)['amount_total'] or 0)
    assert abs(actual - expected) < 0.01, f'second order amount_total expected {expected}, got {actual}'


@then('Item unit_price should be {expected:d}')
def step_impl(context, expected):
    """The Item's unit_price is copied from its (new) Product."""
    items = [each for each in h.order_items(context.order_id) if each['id'] == context.item_id]
    actual = float(items[0]['unit_price'] or 0)
    assert abs(actual - expected) < 0.01, f'unit_price expected {expected}, got {actual}'
