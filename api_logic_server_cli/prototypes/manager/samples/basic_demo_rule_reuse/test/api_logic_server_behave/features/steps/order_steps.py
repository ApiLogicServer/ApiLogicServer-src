"""
Steps for Check Credit, App Integration and Move Order Check Credit.

Each scenario creates its own Customers (timestamped names), so runs are repeatable.
Names in the feature ("Ann", "O1") are aliases for the rows a scenario creates.
"""
from behave import *
import requests, test_utils, time, re
from pathlib import Path

API = 'http://localhost:5656/api'
JSONAPI = {'Content-Type': 'application/vnd.api+json'}
SCENARIO_LOGS = Path(__file__).resolve().parent.parent.parent / 'logs' / 'scenario_logic_logs'


def _headers():
    return {**JSONAPI, **test_utils.login()}


def _start_logic_log(context):
    """ once per scenario, before its first API call: route the logic log to this scenario's file """
    if getattr(context, 'logged_scenario', None) != context.scenario.name:
        context.logged_scenario = context.scenario.name
        context.customers, context.orders, context.items = {}, {}, {}
        context.last_response = None
        test_utils.prt(f'\n\n{context.scenario.name}\n', context.scenario.name)


def _post(resource: str, attributes: dict) -> requests.Response:
    body = {'data': {'type': resource, 'attributes': attributes}}
    return requests.post(f'{API}/{resource}/', json=body, headers=_headers())


def _patch(resource: str, id: int, attributes: dict) -> requests.Response:
    body = {'data': {'type': resource, 'id': str(id), 'attributes': attributes}}
    r = requests.patch(f'{API}/{resource}/{id}/', json=body, headers=_headers())
    return r


def _get(resource: str, id: int) -> dict:
    r = requests.get(f'{API}/{resource}/{id}/', headers=_headers())
    assert r.status_code == 200, f'GET {resource}/{id}: {r.status_code} {r.text}'
    return r.json()['data']['attributes']


def _product_id(name: str) -> int:
    r = requests.get(f'{API}/Product/', params={'filter[name]': name}, headers=_headers())
    data = r.json()['data']
    assert data, f'Product {name} not found'
    return int(data[0]['id'])


def _record(context, r: requests.Response):
    context.last_response = r
    return r


# ---------- Given / When: data ----------

@step('Customer "{alias}" with credit limit {limit:d}')
def step_impl(context, alias, limit):
    _start_logic_log(context)
    r = _post('Customer', {'name': f'{alias} {int(time.time() * 1000)}', 'credit_limit': limit})
    assert r.status_code in (200, 201), f'create Customer: {r.status_code} {r.text}'
    context.customers[alias] = int(r.json()['data']['id'])


@step('Order "{order}" is created for "{alias}" with {quantity:d} {product}')
def step_impl(context, order, alias, quantity, product):
    _start_logic_log(context)
    r = _post('Order', {'customer_id': context.customers[alias], 'notes': f'test {order}'})
    assert r.status_code in (200, 201), f'create Order: {r.status_code} {r.text}'
    context.orders[order] = int(r.json()['data']['id'])
    r = _record(context, _post('Item', {'order_id': context.orders[order], 'product_id': _product_id(product),
                                        'quantity': quantity}))
    if r.status_code in (200, 201):
        context.items[order] = int(r.json()['data']['id'])


@step('Item of Order "{order}" quantity is changed to {quantity:d}')
def step_impl(context, order, quantity):
    _record(context, _patch('Item', context.items[order], {'quantity': quantity}))


@step('Item of Order "{order}" product is changed to {product}')
def step_impl(context, order, product):
    _record(context, _patch('Item', context.items[order], {'product_id': _product_id(product)}))


@step('Item of Order "{order}" is moved to Order "{other}"')
def step_impl(context, order, other):
    _record(context, _patch('Item', context.items[order], {'order_id': context.orders[other]}))


@step('Item of Order "{order}" is deleted')
def step_impl(context, order):
    _record(context, requests.delete(f'{API}/Item/{context.items[order]}/', headers=_headers()))


@step('Order "{order}" is moved to Customer "{alias}"')
def step_impl(context, order, alias):
    _record(context, _patch('Order', context.orders[order], {'customer_id': context.customers[alias]}))


@step('Order "{order}" is shipped')
def step_impl(context, order):
    r = _record(context, _patch('Order', context.orders[order], {'date_shipped': '2026-11-22'}))
    assert r.status_code < 400, f'ship: {r.status_code} {r.text}'


@step('Order "{order}" is unshipped')
def step_impl(context, order):
    r = _record(context, _patch('Order', context.orders[order], {'date_shipped': None}))
    assert r.status_code < 400, f'unship: {r.status_code} {r.text}'


@step('Order "{order}" notes are changed')
def step_impl(context, order):
    r = _record(context, _patch('Order', context.orders[order], {'notes': f'edited {int(time.time() * 1000)}'}))
    assert r.status_code < 400, f'edit notes: {r.status_code} {r.text}'


@step('Order "{order}" is deleted')
def step_impl(context, order):
    r = _record(context, requests.delete(f'{API}/Order/{context.orders[order]}/', headers=_headers()))
    assert r.status_code < 400, f'delete Order: {r.status_code} {r.text}'


# ---------- Then ----------

@then('the transaction is accepted')
def step_impl(context):
    r = context.last_response
    assert r.status_code < 400, f'expected accepted, got {r.status_code} {r.text}'


@then('the transaction is rejected with "{message}"')
def step_impl(context, message):
    r = context.last_response
    assert r.status_code >= 400, f'expected rejection, got {r.status_code} {r.text}'
    assert message in r.text, f'expected "{message}" in {r.text}'


@then('Customer "{alias}" balance is {balance:d}')
def step_impl(context, alias, balance):
    actual = _get('Customer', context.customers[alias])['balance']
    assert float(actual or 0) == balance, f'Customer {alias} balance: expected {balance}, got {actual}'


@then('Order "{order}" amount_total is {total:d}')
def step_impl(context, order, total):
    actual = _get('Order', context.orders[order])['amount_total']
    assert float(actual or 0) == total, f'Order {order} amount_total: expected {total}, got {actual}'


@then('Item of Order "{order}" has unit_price {price:d} and amount {amount:d}')
def step_impl(context, order, price, amount):
    item = _get('Item', context.items[order])
    assert float(item['unit_price']) == price, f'unit_price: expected {price}, got {item["unit_price"]}'
    assert float(item['amount']) == amount, f'amount: expected {amount}, got {item["amount"]}'


@then('Order "{order}" is published to topic "{topic}" {count:d} time')
@then('Order "{order}" is published to topic "{topic}" {count:d} times')
def step_impl(context, order, topic, count):
    """ the logic log records each publish ('Order[<id>] {Sending Order to Kafka topic ...'), live or not """
    name = re.sub(r'[^\w.-]', '_', context.scenario.name)[:25]
    log = (SCENARIO_LOGS / f'{name}.log').read_text(encoding='utf-8')
    sent = log.count(f"Order[{context.orders[order]}] {{Sending Order to Kafka topic '{topic}'")
    assert sent == count, f'Order {order} published to {topic}: expected {count}, got {sent}'
