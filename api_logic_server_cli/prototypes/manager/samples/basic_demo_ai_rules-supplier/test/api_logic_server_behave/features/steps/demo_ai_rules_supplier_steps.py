from behave import *
import requests, time
from decimal import Decimal
from pathlib import Path
import test_utils

BASE = 'http://localhost:5656/api'
HDR = {'Content-Type': 'application/vnd.api+json'}
LOGDIR = Path(__file__).resolve().parent.parent.parent / 'logs' / 'scenario_logic_logs'


def _post(resource, attrs):
    return requests.post(f'{BASE}/{resource}/', json={"data": {"type": resource, "attributes": attrs}}, headers=HDR)


def _patch(resource, rid, attrs):
    return requests.patch(f'{BASE}/{resource}/{rid}/', json={"data": {"type": resource, "id": str(rid), "attributes": attrs}}, headers=HDR)


def _get(path):
    return requests.get(f'{BASE}/{path}', headers=HDR).json()


def _attrs(resource, rid):
    return _get(f'{resource}/{rid}/')['data']['attributes']


def _product_id(name):
    return int(_get(f'Product/?filter[name]={name.replace(" ", "%20")}')['data'][0]['id'])


def _new_customer(limit):
    r = _post('Customer', {'name': f'Test Cust {int(time.time() * 1000)}', 'balance': 0, 'credit_limit': limit})
    assert r.status_code in (200, 201), r.text
    return int(r.json()['data']['id'])


def _new_order(customer_id):
    r = _post('Order', {'customer_id': customer_id, 'notes': 'behave'})
    assert r.status_code in (200, 201), r.text
    return int(r.json()['data']['id'])


def _num(v):
    return Decimal(str(v))


@given('a customer with credit limit {limit:d}')
def step_impl(context, limit):
    context.customer_id = _new_customer(limit)
    context.limit = limit


@given('a customer whose credit limit equals the cost of 2 Egyptian Cotton Sheets')
def step_impl(context):
    # the AI may choose either supplier; the boundary is the most expensive candidate (2 x max unit_cost)
    pid = _product_id('Egyptian Cotton Sheets')
    ps = _get(f'ProductSupplier/?filter[product_id]={pid}')['data']
    top = max(_num(p['attributes']['unit_cost']) for p in ps)
    context.limit = int(top * 2)
    context.customer_id = _new_customer(context.limit)


@given('the scenario logic log is started for "{name}"')
def step_impl(context, name):
    context.log_name = name
    test_utils.prt(f'\n{name}\n', name)


def _place(context, qty, product_name):
    context.order_id = _new_order(context.customer_id)
    r = _post('Item', {'order_id': context.order_id, 'product_id': _product_id(product_name), 'quantity': qty})
    context.item_resp = r
    if r.status_code in (200, 201):
        context.item_id = int(r.json()['data']['id'])


@given('an order is placed with {qty:d} Egyptian Cotton Sheets')
def step_impl(context, qty):
    _place(context, qty, 'Egyptian Cotton Sheets')
    assert context.item_resp.status_code in (200, 201), context.item_resp.text


@when('an order is placed with {qty:d} Egyptian Cotton Sheets')
def step_impl(context, qty):
    _place(context, qty, 'Egyptian Cotton Sheets')


@when('an order is placed with {qty:d} Widget')
def step_impl(context, qty):
    _place(context, qty, 'Widget')
    assert context.item_resp.status_code in (200, 201), context.item_resp.text


@given('a second order for a second customer exists')
def step_impl(context):
    context.customer2_id = _new_customer(5000)
    context.order2_id = _new_order(context.customer2_id)


@then('the item unit_price is one of the product\'s supplier costs')
def step_impl(context):
    pid = _product_id('Egyptian Cotton Sheets')
    costs = {_num(p['attributes']['unit_cost']) for p in _get(f'ProductSupplier/?filter[product_id]={pid}')['data']}
    context.unit_price = _num(_attrs('Item', context.item_id)['unit_price'])
    assert context.unit_price in costs, f'{context.unit_price} not in {costs}'


@then('an audit row exists linked to the item with a chosen supplier of that product')
def step_impl(context):
    rows = _get(f'SysSupplierReq/?filter[item_id]={context.item_id}')['data']
    assert len(rows) == 1, f'expected 1 audit row, got {len(rows)}'
    a = rows[0]['attributes']
    pid = _product_id('Egyptian Cotton Sheets')
    suppliers = {p['attributes']['supplier_id'] for p in _get(f'ProductSupplier/?filter[product_id]={pid}')['data']}
    assert a['chosen_supplier_id'] in suppliers
    assert a['request'] and a['reason'] and a['fallback_used'] in (True, False)
    assert _num(a['chosen_unit_price']) == context.unit_price


@then('the order amount_total is quantity times unit_price')
def step_impl(context):
    item = _attrs('Item', context.item_id)
    expected = _num(item['quantity']) * _num(item['unit_price'])
    assert _num(_attrs('Order', context.order_id)['amount_total']) == expected


@then('the customer balance equals the order amount_total')
def step_impl(context):
    assert _num(_attrs('Customer', context.customer_id)['balance']) == _num(_attrs('Order', context.order_id)['amount_total'])


@when('the item quantity is changed to {qty:d}')
def step_impl(context, qty):
    r = _patch('Item', context.item_id, {'quantity': qty})
    assert r.status_code == 200, r.text


@when('the item is deleted')
def step_impl(context):
    r = requests.delete(f'{BASE}/Item/{context.item_id}/', headers=HDR)
    assert r.status_code in (200, 204), r.text


@then('the order amount_total is 0')
def step_impl(context):
    assert _num(_attrs('Order', context.order_id)['amount_total']) == 0


@then('the customer balance is 0')
def step_impl(context):
    assert _num(_attrs('Customer', context.customer_id)['balance']) == 0


@when('the item is moved to the second order')
def step_impl(context):
    context.item_amount = _num(_attrs('Item', context.item_id)['amount'])
    r = _patch('Item', context.item_id, {'order_id': context.order2_id})
    assert r.status_code == 200, r.text


@then('the first order amount_total is 0 and the first customer balance is 0')
def step_impl(context):
    assert _num(_attrs('Order', context.order_id)['amount_total']) == 0
    assert _num(_attrs('Customer', context.customer_id)['balance']) == 0


@then('the second customer balance equals the item amount')
def step_impl(context):
    assert _num(_attrs('Customer', context.customer2_id)['balance']) == context.item_amount


@given('the order is shipped')
def step_impl(context):
    assert _patch('Order', context.order_id, {'date_shipped': '2026-11-10'}).status_code == 200


@when('the order is shipped')
def step_impl(context):
    r = _patch('Order', context.order_id, {'date_shipped': '2026-11-10'})
    assert r.status_code == 200, r.text


@when('the order is unshipped')
def step_impl(context):
    r = _patch('Order', context.order_id, {'date_shipped': None})
    assert r.status_code == 200, r.text


@then('the order is accepted')
def step_impl(context):
    assert context.item_resp.status_code in (200, 201), context.item_resp.text
    bal = _num(_attrs('Customer', context.customer_id)['balance'])
    assert bal <= context.limit


@then('the item is rejected with "{msg}"')
def step_impl(context, msg):
    assert context.item_resp.status_code == 400, context.item_resp.status_code
    assert msg in context.item_resp.text, context.item_resp.text


@then('the item unit_price equals the Widget product price')
def step_impl(context):
    price = _num(_attrs('Product', _product_id('Widget'))['unit_price'])
    assert _num(_attrs('Item', context.item_id)['unit_price']) == price


@then('no audit row exists for the item')
def step_impl(context):
    assert len(_get(f'SysSupplierReq/?filter[item_id]={context.item_id}')['data']) == 0


@given('a new product with no suppliers')
def step_impl(context):
    r = _post('Product', {'name': f'Test Product {int(time.time() * 1000)}', 'unit_price': 10})
    assert r.status_code in (200, 201), r.text
    context.product_id = int(r.json()['data']['id'])
    context.supplier_id = int(_get('Supplier/')['data'][0]['id'])


@when('a supplier is added to the new product')
def step_impl(context):
    r = _post('ProductSupplier', {'product_id': context.product_id, 'supplier_id': context.supplier_id, 'unit_cost': 5, 'lead_time_days': 3})
    assert r.status_code in (200, 201), r.text
    context.ps_id = int(r.json()['data']['id'])


@then('the product count_suppliers is {n:d}')
def step_impl(context, n):
    assert int(_attrs('Product', context.product_id)['count_suppliers']) == n


@then('when the product supplier is deleted the product count_suppliers is {n:d}')
def step_impl(context, n):
    r = requests.delete(f'{BASE}/ProductSupplier/{context.ps_id}/', headers=HDR)
    assert r.status_code in (200, 204), r.text
    assert int(_attrs('Product', context.product_id)['count_suppliers']) == n


def _log_has_publish(context):
    f = next(LOGDIR.glob(context.log_name[:25].replace(' ', '*') + '*'), None) if LOGDIR.exists() else None
    if f is None:
        f = LOGDIR / f'{context.log_name[:25]}.log'
    return test_utils.does_file_contain("publish_kafka_message: topic='order_shipping'", str(f))


@then('the logic log shows a publish to topic order_shipping')
def step_impl(context):
    assert _log_has_publish(context)


@then('the logic log shows no publish to topic order_shipping')
def step_impl(context):
    assert not _log_has_publish(context)
