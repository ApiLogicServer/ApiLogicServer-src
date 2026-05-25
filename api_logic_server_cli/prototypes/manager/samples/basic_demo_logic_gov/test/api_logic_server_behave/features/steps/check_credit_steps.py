from behave import *
import requests, test_utils, time
from decimal import Decimal

BASE_URL = 'http://localhost:5656'


def _post(url, data, headers=None):
    return requests.post(url, json=data, headers=headers or {})

def _patch(url, data, headers=None):
    return requests.patch(url, json=data, headers=headers or {})

def _get(url, headers=None):
    return requests.get(url, headers=headers or {})

def _delete(url, headers=None):
    return requests.delete(url, headers=headers or {})


# ─── GIVEN ────────────────────────────────────────────────────────────────────

@given('Customer with credit limit {limit:g}')
def step_customer(context, limit):
    scenario_name = context.scenario.name[:25]
    context.scenario_name = scenario_name
    test_utils.prt(f'\n{scenario_name}\n', scenario_name)

    unique_name = f"Test {int(time.time() * 1000)}"
    r = _post(f'{BASE_URL}/api/Customer/', {"data": {
        "type": "Customer",
        "attributes": {"name": unique_name, "credit_limit": limit, "balance": 0}
    }})
    assert r.status_code == 201, f"Customer create failed: {r.text}"
    context.customer_id = int(r.json()['data']['id'])
    context.customer_name = unique_name


@given('Order is placed with {qty1:d} {product1} and {qty2:d} {product2}')
def step_order_two_items(context, qty1, product1, qty2, product2):
    _create_order_with_items(context, [(qty1, product1), (qty2, product2)])


@given('Order is placed with {qty:d} {product_name}')
def step_order_one_item(context, qty, product_name):
    _create_order_with_items(context, [(qty, product_name)])


@given('Shipped order is created with {qty:d} {product_name}')
def step_shipped_order(context, qty, product_name):
    _create_order_with_items(context, [(qty, product_name)])
    # ship it
    r = _patch(f'{BASE_URL}/api/Order/{context.order_id}/', {"data": {
        "type": "Order", "id": context.order_id,
        "attributes": {"date_shipped": "2026-01-01", "_check_sum_": context.order_checksum}
    }})
    assert r.status_code == 200, f"Ship order failed: {r.text}"
    context.order_checksum = r.json()['data']['attributes'].get('_check_sum_', '')


# ─── WHEN ─────────────────────────────────────────────────────────────────────

@when('Order is placed with {qty1:d} {product1} and {qty2:d} {product2}')
def step_when_order_two_items(context, qty1, product1, qty2, product2):
    _create_order_with_items(context, [(qty1, product1), (qty2, product2)])


@when('Order is placed with {qty:d} {product_name}')
def step_when_order_one_item(context, qty, product_name):
    _create_order_with_items(context, [(qty, product_name)])


@when('Item quantity changed to {qty:d}')
def step_change_qty(context, qty):
    r = _patch(f'{BASE_URL}/api/Item/{context.item_id}/', {"data": {
        "type": "Item", "id": context.item_id,
        "attributes": {"quantity": qty, "_check_sum_": context.item_checksum}
    }})
    assert r.status_code == 200, f"Item patch failed: {r.text}"


@when('Item is deleted')
def step_delete_item(context):
    # delete the first item (Chai); server returns 204 on success
    r = _delete(f'{BASE_URL}/api/Item/{context.item_id}/')
    assert r.status_code in (200, 204), f"Item delete failed ({r.status_code}): {r.text}"


@when('Order is shipped')
def step_ship_order(context):
    r = _patch(f'{BASE_URL}/api/Order/{context.order_id}/', {"data": {
        "type": "Order", "id": context.order_id,
        "attributes": {"date_shipped": "2026-01-01", "_check_sum_": context.order_checksum}
    }})
    assert r.status_code == 200, f"Ship order failed: {r.text}"


@when('Order is unshipped')
def step_unship_order(context):
    r = _patch(f'{BASE_URL}/api/Order/{context.order_id}/', {"data": {
        "type": "Order", "id": context.order_id,
        "attributes": {"date_shipped": None, "_check_sum_": context.order_checksum}
    }})
    assert r.status_code == 200, f"Unship order failed: {r.text}"


# ─── THEN ─────────────────────────────────────────────────────────────────────

@then('Customer balance is {expected:g}')
def step_check_balance(context, expected):
    r = _get(f'{BASE_URL}/api/Customer/{context.customer_id}/')
    assert r.status_code == 200, f"Customer GET failed: {r.text}"
    actual = float(r.json()['data']['attributes']['balance'])
    assert abs(actual - expected) < 0.01, f"Balance: expected {expected}, got {actual}"


@then('Order is rejected with credit limit error')
def step_check_rejected(context):
    assert context.order_rejected, "Expected order to be rejected but it was accepted"


@then('Item amount is {expected:g}')
def step_check_item_amount(context, expected):
    r = _get(f'{BASE_URL}/api/Item/{context.item_id}/')
    assert r.status_code == 200, f"Item GET failed: {r.text}"
    actual = float(r.json()['data']['attributes']['amount'])
    assert abs(actual - expected) < 0.01, f"Item amount: expected {expected}, got {actual}"


@then('Order amount_total is {expected:g}')
def step_check_order_total(context, expected):
    r = _get(f'{BASE_URL}/api/Order/{context.order_id}/')
    assert r.status_code == 200, f"Order GET failed: {r.text}"
    actual = float(r.json()['data']['attributes']['amount_total'])
    assert abs(actual - expected) < 0.01, f"Order amount_total: expected {expected}, got {actual}"


# ─── HELPERS ──────────────────────────────────────────────────────────────────

def _lookup_product(name):
    """Return (id, unit_price) for a product by name."""
    r = requests.get(f'{BASE_URL}/api/Product/', params={"filter[name]": name})
    assert r.status_code == 200, f"Product lookup failed: {r.text}"
    data = r.json()['data']
    assert len(data) > 0, f"Product '{name}' not found"
    attrs = data[0]['attributes']
    return int(data[0]['id']), float(attrs['unit_price'])


def _create_order_with_items(context, items):
    """Create an Order with one or more (qty, product_name) items.
    Sets context: order_id, order_checksum, item_id, item_checksum (first item).
    Also sets context.order_rejected = True/False.
    """
    # Create order
    r = _post(f'{BASE_URL}/api/Order/', {"data": {
        "type": "Order",
        "attributes": {"customer_id": context.customer_id}
    }})
    if r.status_code != 201:
        context.order_rejected = True
        context.order_id = None
        return
    context.order_rejected = False
    order = r.json()['data']
    context.order_id = int(order['id'])
    context.order_checksum = order['attributes'].get('_check_sum_', '')

    first_item_id = None
    first_item_checksum = ''
    for qty, product_name in items:
        product_id, unit_price = _lookup_product(product_name)
        ri = _post(f'{BASE_URL}/api/Item/', {"data": {
            "type": "Item",
            "attributes": {
                "order_id": context.order_id,
                "product_id": product_id,
                "quantity": qty,
                "unit_price": unit_price
            }
        }})
        if ri.status_code != 201:
            context.order_rejected = True
            return
        if first_item_id is None:
            first_item_id = int(ri.json()['data']['id'])
            first_item_checksum = ri.json()['data']['attributes'].get('_check_sum_', '')

    context.item_id = first_item_id
    context.item_checksum = first_item_checksum
