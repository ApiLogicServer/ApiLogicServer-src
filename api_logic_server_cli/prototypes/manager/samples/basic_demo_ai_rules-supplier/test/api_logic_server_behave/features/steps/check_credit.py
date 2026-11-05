"""
Feature: Check Credit
Feature: App Integration

Steps shared by check_credit.feature and app_integration.feature. Every scenario builds fresh, uniquely named data
(Rule #0), uses the JSON:API directly, and never asserts a specific AI choice: only that the choice is one of the
product's suppliers and that an audit row exists.
"""
from behave import *
import requests, time, datetime
from pathlib import Path
import test_utils

BASE = 'http://localhost:5656/api'
HEADERS = {'Content-Type': 'application/vnd.api+json'}
LOGS_DIR = Path(__file__).resolve().parent.parent.parent / 'logs' / 'scenario_logic_logs'


def _uid() -> str:
    return str(int(time.time() * 1000))


def _post(type_: str, attrs: dict) -> requests.Response:
    return requests.post(f'{BASE}/{type_}/', json={'data': {'type': type_, 'attributes': attrs}}, headers=HEADERS)


def _patch(type_: str, id_: int, attrs: dict) -> requests.Response:
    return requests.patch(f'{BASE}/{type_}/{id_}/', json={'data': {'type': type_, 'id': str(id_), 'attributes': attrs}}, headers=HEADERS)


def _get(type_: str, id_: int) -> dict:
    r = requests.get(f'{BASE}/{type_}/{id_}/', headers=HEADERS)
    assert r.status_code == 200, f'GET {type_}/{id_} -> {r.status_code} {r.text[:200]}'
    return r.json()['data']['attributes']


def _created_id(r: requests.Response, what: str) -> int:
    assert r.status_code in (200, 201), f'{what} failed: {r.status_code} {r.text[:300]}'
    return int(r.json()['data']['id'])


def _new_customer(context, limit: int) -> int:
    r = _post('Customer', {'name': f'Test Customer {_uid()}', 'balance': 0, 'credit_limit': limit})
    return _created_id(r, 'create customer')


def _new_product(price: int) -> int:
    r = _post('Product', {'name': f'Test Product {_uid()}', 'unit_price': price})
    return _created_id(r, 'create product')


def _add_supplier(product_id: int, supplier_id: int, cost: int) -> int:
    r = _post('ProductSupplier', {'product_id': product_id, 'supplier_id': supplier_id, 'unit_cost': cost, 'lead_time_days': 3})
    return _created_id(r, 'create product supplier')


def _add_item(context, order_id: int, product_id: int, qty: int) -> requests.Response:
    r = _post('Item', {'order_id': order_id, 'product_id': product_id, 'quantity': qty})
    context.item_response = r
    return r


def _new_order(context, product_id: int, qty: int) -> tuple:
    order_id = _created_id(_post('Order', {'customer_id': context.customer_id, 'notes': f'test {_uid()}'}), 'create order')
    r = _add_item(context, order_id, product_id, qty)
    item_id = int(r.json()['data']['id']) if r.status_code in (200, 201) else None
    return order_id, item_id


@step('a customer with credit limit {limit:d}')
def _(context, limit):
    scenario = context.scenario.name
    test_utils.prt(f'\n{scenario}\n', scenario)  # once per scenario, before the first API call
    context.customer_id = _new_customer(context, limit)
    context.limit = limit


@step('a second customer with credit limit {limit:d}')
def _(context, limit):
    context.customer2_id = _new_customer(context, limit)


@step('a product priced {price:d} with no suppliers')
def _(context, price):
    context.product_id = _new_product(price)


@step('a second product priced {price:d} with no suppliers')
def _(context, price):
    context.product2_id = _new_product(price)


@step('a second product priced {price:d} with suppliers costing {c1:d} and {c2:d}')
def _(context, price, c1, c2):
    context.product2_id = _new_product(price)
    context.product2_costs = {1: c1, 2: c2}
    for supplier_id, cost in context.product2_costs.items():
        _add_supplier(context.product2_id, supplier_id, cost)
    context.expected_costs = context.product2_costs


@step('a product priced {price:d} with suppliers costing {c1:d} and {c2:d}')
def _(context, price, c1, c2):
    context.product_id = _new_product(price)
    context.product_costs = {1: c1, 2: c2}
    for supplier_id, cost in context.product_costs.items():
        _add_supplier(context.product_id, supplier_id, cost)
    context.expected_costs = context.product_costs


@step('an order is created with {qty:d} of the product')
def _(context, qty):
    context.order_id, context.item_id = _new_order(context, context.product_id, qty)


@step('a second order is created with {qty:d} of the product')
def _(context, qty):
    context.order2_id, context.item2_id = _new_order(context, context.product_id, qty)


@step('a second item is added with {qty:d} of the product')
def _(context, qty):
    r = _add_item(context, context.order_id, context.product_id, qty)
    context.item2_id = _created_id(r, 'add second item')


@step('the order is shipped')
def _(context):
    r = _patch('Order', context.order_id, {'date_shipped': str(datetime.date.today())})
    assert r.status_code == 200, r.text[:300]


@step('the order is un-shipped')
def _(context):
    r = _patch('Order', context.order_id, {'date_shipped': None})
    assert r.status_code == 200, r.text[:300]


@step('the order is moved to the second customer')
def _(context):
    r = _patch('Order', context.order_id, {'customer_id': context.customer2_id})
    assert r.status_code == 200, r.text[:300]


@step('the order and its item are deleted')
def _(context):
    r = requests.delete(f'{BASE}/Item/{context.item_id}/', headers=HEADERS)
    assert r.status_code in (200, 204), r.text[:300]
    r = requests.delete(f'{BASE}/Order/{context.order_id}/', headers=HEADERS)
    assert r.status_code in (200, 204), r.text[:300]


@step('the item quantity is changed to {qty:d}')
def _(context, qty):
    r = _patch('Item', context.item_id, {'quantity': qty})
    assert r.status_code == 200, r.text[:300]


@step('the item is deleted')
def _(context):
    r = requests.delete(f'{BASE}/Item/{context.item_id}/', headers=HEADERS)
    assert r.status_code in (200, 204), r.text[:300]


@step('the item is moved to the second order')
def _(context):
    r = _patch('Item', context.item_id, {'order_id': context.order2_id})
    assert r.status_code == 200, r.text[:300]


@step('the item product is changed to the second product')
def _(context):
    r = _patch('Item', context.item_id, {'product_id': context.product2_id})
    assert r.status_code == 200, r.text[:300]
    context.expected_costs = getattr(context, 'product2_costs', {})


@step('a supplier is added to the product costing {cost:d}')
def _(context, cost):
    context.ps_id = _add_supplier(context.product_id, 1, cost)


@step('a second supplier is added to the product costing {cost:d}')
def _(context, cost):
    context.ps2_id = _add_supplier(context.product_id, 2, cost)


@step('the first supplier is removed from the product')
def _(context):
    r = requests.delete(f'{BASE}/ProductSupplier/{context.ps_id}/', headers=HEADERS)
    assert r.status_code in (200, 204), r.text[:300]


@step('the product supplier is moved to the second product')
def _(context):
    r = _patch('ProductSupplier', context.ps_id, {'product_id': context.product2_id})
    assert r.status_code == 200, r.text[:300]


@step('the customer balance is {value:d}')
def _(context, value):
    assert float(_get('Customer', context.customer_id)['balance']) == value, _get('Customer', context.customer_id)


@step('the second customer balance is {value:d}')
def _(context, value):
    assert float(_get('Customer', context.customer2_id)['balance']) == value


@step('the order amount total is {value:d}')
def _(context, value):
    assert float(_get('Order', context.order_id)['amount_total']) == value


@step('the second order amount total is {value:d}')
def _(context, value):
    assert float(_get('Order', context.order2_id)['amount_total']) == value


@step('the item amount is {value:d}')
def _(context, value):
    assert float(_get('Item', context.item_id)['amount']) == value


@step('the item unit price is {value:d}')
def _(context, value):
    assert float(_get('Item', context.item_id)['unit_price']) == value


@step('the product supplier count is {value:d}')
def _(context, value):
    assert int(_get('Product', context.product_id)['count_suppliers']) == value


@step('the second product supplier count is {value:d}')
def _(context, value):
    assert int(_get('Product', context.product2_id)['count_suppliers']) == value


@step('the item is rejected with a message containing "{text}"')
def _(context, text):
    r = context.item_response
    assert r.status_code >= 400, f'expected rejection, got {r.status_code}'
    assert text in r.text, r.text[:300]


def _audit_rows(item_id: int) -> list:
    r = requests.get(f'{BASE}/SysSupplierReq/', params={'filter[item_id]': item_id}, headers=HEADERS)
    assert r.status_code == 200, r.text[:300]
    return [each['attributes'] for each in r.json()['data']]


@step('no AI audit row exists for the item')
def _(context):
    assert _audit_rows(context.item_id) == []


@step('the AI chose one of the product suppliers and an audit row exists')
def _(context):
    rows = _audit_rows(context.item_id)
    assert len(rows) >= 1, 'no SysSupplierReq audit row for the item'
    audit = rows[-1]
    assert audit['chosen_supplier_id'] in context.expected_costs, f"chosen supplier not one of the product's suppliers: {audit}"
    assert float(audit['chosen_unit_price']) == context.expected_costs[audit['chosen_supplier_id']], audit
    assert audit['request'] and audit['reason'] and audit['created_on'], audit
    assert audit['fallback_used'] in (True, False, 0, 1), audit
    context.chosen_price = float(audit['chosen_unit_price'])
    assert float(_get('Item', context.item_id)['unit_price']) == context.chosen_price


@step('the item amount is the quantity times the chosen price')
def _(context):
    item = _get('Item', context.item_id)
    assert float(item['amount']) == item['quantity'] * context.chosen_price


@step('the customer balance is the item amount')
def _(context):
    assert float(_get('Customer', context.customer_id)['balance']) == float(_get('Item', context.item_id)['amount'])


def _scenario_log(context) -> Path:
    name = context.scenario.name.replace(' ', '_')
    return LOGS_DIR / f'{name[:25]}.log'


@step('the logic log shows the order sent to Kafka topic "{topic}"')
def _(context, topic):
    assert test_utils.does_file_contain(f"Sending Order to Kafka topic '{topic}'", str(_scenario_log(context))), \
        f'no Kafka send in {_scenario_log(context)}'


@step('the logic log shows no message sent to Kafka topic "{topic}"')
def _(context, topic):
    log = _scenario_log(context)
    assert log.exists(), f'scenario log missing: {log}'
    assert not test_utils.does_file_contain(f"Sending Order to Kafka topic '{topic}'", str(log))


@step('the order notes are edited')
def _(context):
    r = _patch('Order', context.order_id, {'notes': f'edited {_uid()}'})
    assert r.status_code == 200, r.text[:300]


@step('the logic log shows the order sent to Kafka topic "{topic}" {times:d} time')
def _(context, topic, times):
    text = _scenario_log(context).read_text()
    assert text.count(f"Sending Order to Kafka topic '{topic}'") == times, text.count(f"Sending Order to Kafka topic '{topic}'")
