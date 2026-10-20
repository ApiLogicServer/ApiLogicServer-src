from behave import *
import requests, time
import test_utils

BASE_URL = 'http://localhost:5656'


def _headers():
    headers = test_utils.login()
    headers['Content-Type'] = 'application/vnd.api+json'
    return headers


def _customer_map(context):
    if not hasattr(context, 'customer_map'):
        context.customer_map = {}
    return context.customer_map


@given('Customer "{customer_name}" with balance {balance:d} and credit limit {limit:d}')
def step_impl(context, customer_name, balance, limit):
    scenario_name = context.scenario.name[:25]
    if not hasattr(context, 'scenario_name'):
        context.scenario_name = scenario_name
        # ONE prt call per scenario, before the first API call - opens the logic log
        test_utils.prt(f'\n{scenario_name}\n', scenario_name)

    unique_name = f"{customer_name} {int(time.time() * 1000)}"
    post_data = {
        "data": {
            "type": "Customer",
            "attributes": {
                "name": unique_name,
                "balance": balance,
                "credit_limit": limit
            }
        }
    }
    r = requests.post(url=f'{BASE_URL}/api/Customer/', json=post_data, headers=_headers())
    assert r.status_code in (200, 201), f'Customer create failed: {r.status_code} {r.text}'
    customer_id = int(r.json()['data']['id'])

    _customer_map(context)[customer_name] = {'id': customer_id, 'unique_name': unique_name}
    # Default "current" customer is the most recently created one
    context.customer_id = customer_id
    context.customer_name = customer_name


@given('Order is created for "{customer_name}"')
def step_impl(context, customer_name):
    customer_id = _customer_map(context)[customer_name]['id']
    post_data = {
        "data": {
            "type": "Order",
            "attributes": {
                "customer_id": customer_id
            }
        }
    }
    r = requests.post(url=f'{BASE_URL}/api/Order/', json=post_data, headers=_headers())
    assert r.status_code in (200, 201), f'Order create failed: {r.status_code} {r.text}'
    context.order_id = int(r.json()['data']['id'])
    context.order_customer_name = customer_name


def _lookup_product_id(product_name):
    r = requests.get(url=f'{BASE_URL}/api/Product/', params={'filter[name]': product_name}, headers=_headers())
    assert r.status_code == 200, f'Product lookup failed: {r.status_code} {r.text}'
    data = r.json()['data']
    assert len(data) > 0, f'Product "{product_name}" not found'
    return int(data[0]['id']), float(data[0]['attributes']['unit_price'])


@given('Item is created with {quantity:d} {product_name}')
@when('Item is created with {quantity:d} {product_name}')
def step_impl(context, quantity, product_name):
    product_id, _ = _lookup_product_id(product_name)
    post_data = {
        "data": {
            "type": "Item",
            "attributes": {
                "order_id": context.order_id,
                "product_id": product_id,
                "quantity": quantity
            }
        }
    }
    r = requests.post(url=f'{BASE_URL}/api/Item/', json=post_data, headers=_headers())
    context.item_created = (r.status_code in (200, 201))
    context.item_create_response = r
    if context.item_created:
        context.item_id = int(r.json()['data']['id'])
    else:
        context.item_id = None


@when('Item quantity is changed to {qty:d}')
def step_impl(context, qty):
    patch_data = {
        "data": {
            "type": "Item",
            "id": str(context.item_id),
            "attributes": {"quantity": qty}
        }
    }
    r = requests.patch(url=f'{BASE_URL}/api/Item/{context.item_id}/', json=patch_data, headers=_headers())
    assert r.status_code in (200, 201), f'Item quantity update failed: {r.status_code} {r.text}'


@when('Item product is changed to {product_name}')
def step_impl(context, product_name):
    product_id, _ = _lookup_product_id(product_name)
    patch_data = {
        "data": {
            "type": "Item",
            "id": str(context.item_id),
            "attributes": {"product_id": product_id}
        }
    }
    r = requests.patch(url=f'{BASE_URL}/api/Item/{context.item_id}/', json=patch_data, headers=_headers())
    assert r.status_code in (200, 201), f'Item product update failed: {r.status_code} {r.text}'


@when('Item is deleted')
def step_impl(context):
    r = requests.delete(url=f'{BASE_URL}/api/Item/{context.item_id}/', headers=_headers())
    assert r.status_code in (200, 204), f'Item delete failed: {r.status_code} {r.text}'


@when('Order customer is changed to "{customer_name}"')
def step_impl(context, customer_name):
    new_customer_id = _customer_map(context)[customer_name]['id']
    patch_data = {
        "data": {
            "type": "Order",
            "id": str(context.order_id),
            "attributes": {"customer_id": new_customer_id}
        }
    }
    r = requests.patch(url=f'{BASE_URL}/api/Order/{context.order_id}/', json=patch_data, headers=_headers())
    assert r.status_code in (200, 201), f'Order customer change failed: {r.status_code} {r.text}'


@when('Order is shipped')
def step_impl(context):
    patch_data = {
        "data": {
            "type": "Order",
            "id": str(context.order_id),
            "attributes": {"date_shipped": "2026-01-01"}
        }
    }
    r = requests.patch(url=f'{BASE_URL}/api/Order/{context.order_id}/', json=patch_data, headers=_headers())
    assert r.status_code in (200, 201), f'Order ship failed: {r.status_code} {r.text}'


@given('Order is shipped')
def step_impl(context):
    patch_data = {
        "data": {
            "type": "Order",
            "id": str(context.order_id),
            "attributes": {"date_shipped": "2026-01-01"}
        }
    }
    r = requests.patch(url=f'{BASE_URL}/api/Order/{context.order_id}/', json=patch_data, headers=_headers())
    assert r.status_code in (200, 201), f'Order ship failed: {r.status_code} {r.text}'


@when('Order is unshipped')
def step_impl(context):
    patch_data = {
        "data": {
            "type": "Order",
            "id": str(context.order_id),
            "attributes": {"date_shipped": None}
        }
    }
    r = requests.patch(url=f'{BASE_URL}/api/Order/{context.order_id}/', json=patch_data, headers=_headers())
    assert r.status_code in (200, 201), f'Order unship failed: {r.status_code} {r.text}'


@then('Item unit_price is {expected:g}')
def step_impl(context, expected):
    r = requests.get(url=f'{BASE_URL}/api/Item/{context.item_id}/', headers=_headers())
    actual = float(r.json()['data']['attributes']['unit_price'])
    assert abs(actual - expected) < 0.01, f'expected unit_price {expected}, got {actual}'


@then('Item amount is {expected:g}')
def step_impl(context, expected):
    r = requests.get(url=f'{BASE_URL}/api/Item/{context.item_id}/', headers=_headers())
    actual = float(r.json()['data']['attributes']['amount'])
    assert abs(actual - expected) < 0.01, f'expected amount {expected}, got {actual}'


@then('Order amount_total is {expected:g}')
def step_impl(context, expected):
    r = requests.get(url=f'{BASE_URL}/api/Order/{context.order_id}/', headers=_headers())
    actual = float(r.json()['data']['attributes']['amount_total'])
    assert abs(actual - expected) < 0.01, f'expected amount_total {expected}, got {actual}'


@then('Customer balance is {expected:g}')
def step_impl(context, expected):
    customer_id = context.customer_id
    r = requests.get(url=f'{BASE_URL}/api/Customer/{customer_id}/', headers=_headers())
    actual = float(r.json()['data']['attributes']['balance'])
    assert abs(actual - expected) < 0.01, f'expected balance {expected}, got {actual}'


@then('Customer "{customer_name}" balance is {expected:g}')
def step_impl(context, customer_name, expected):
    customer_id = _customer_map(context)[customer_name]['id']
    r = requests.get(url=f'{BASE_URL}/api/Customer/{customer_id}/', headers=_headers())
    actual = float(r.json()['data']['attributes']['balance'])
    assert abs(actual - expected) < 0.01, f'expected {customer_name} balance {expected}, got {actual}'


@then('Order creation succeeded')
def step_impl(context):
    assert context.item_created, f'Expected item/order creation to succeed: {context.item_create_response.text}'


@then('Item creation is rejected')
def step_impl(context):
    assert not context.item_created, \
        f'Expected item creation to be rejected by credit-limit constraint, but it succeeded'
    assert context.item_create_response.status_code >= 400, \
        f'Expected 4xx/error status, got {context.item_create_response.status_code}'
