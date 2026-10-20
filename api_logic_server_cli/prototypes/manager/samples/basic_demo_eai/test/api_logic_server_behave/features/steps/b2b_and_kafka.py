"""
Steps for the integration requirements: B2B API (§2), Kafka subscribe (§3), Kafka publish (§4).

Check Credit steps (customers, orders, items, balances) are in check_credit.py; these steps
reuse its context (customer_map, customer_id, order_id) and its once-per-scenario logic log.
"""
from behave import *
import json, re, time
from pathlib import Path
import requests
import test_utils

BASE_URL = 'http://localhost:5656'
TEST_DIR = Path(__file__).resolve().parent.parent.parent
""" test/api_logic_server_behave """


def _headers():
    return test_utils.login()   # {} when security is disabled


def _unique_name(context, customer_name):
    return context.customer_map[customer_name]['unique_name']


def _items(*pairs):
    return [{"Name": name, "QuantityOrdered": qty} for qty, name in pairs]


# ---------------------------------------------------------------------------------- §2 B2B API

def _post_b2b(context, account, items):
    payload = {"Account": account, "Notes": "behave test", "Items": items}
    r = requests.post(url=f'{BASE_URL}/api/OrderB2B', json=payload, headers=_headers())
    context.b2b_response = r
    context.b2b_accepted = False
    context.order_id = None   # Rule #12: always initialised
    try:
        body = r.json()
    except ValueError:
        body = {}
    if r.status_code == 200 and body.get('success'):
        context.b2b_accepted = True
        context.order_id = int(body['order_id'])


@when('B2B order is posted for "{customer_name}" with {qty1:d} {product1} and {qty2:d} {product2}')
def step_impl(context, customer_name, qty1, product1, qty2, product2):
    _post_b2b(context, _unique_name(context, customer_name), _items((qty1, product1), (qty2, product2)))


@when('B2B order is posted for unknown customer with {quantity:d} {product_name}')
def step_impl(context, quantity, product_name):
    _post_b2b(context, f'No Such Customer {int(time.time() * 1000)}', _items((quantity, product_name)))


@when('B2B order is posted for "{customer_name}" with {quantity:d} {product_name}')
def step_impl(context, customer_name, quantity, product_name):
    _post_b2b(context, _unique_name(context, customer_name), _items((quantity, product_name)))


@then('B2B order is accepted')
def step_impl(context):
    assert context.b2b_accepted, \
        f'expected the partner order to be accepted: {context.b2b_response.status_code} {context.b2b_response.text}'


@then('B2B order is rejected with status {status:d}')
def step_impl(context, status):
    assert not context.b2b_accepted, 'expected the partner order to be rejected, but it was accepted'
    assert context.b2b_response.status_code == status, \
        f'expected status {status}, got {context.b2b_response.status_code}: {context.b2b_response.text}'


@then('B2B order is not accepted')
def step_impl(context):
    assert not context.b2b_accepted, 'expected the partner order to be rejected, but it was accepted'


@then('Order has {count:d} items')
def step_impl(context, count):
    assert context.order_id is not None, 'no order was created'
    r = requests.get(url=f'{BASE_URL}/api/Item/', params={'filter[order_id]': context.order_id,
                                                           'page[limit]': 100}, headers=_headers())
    assert r.status_code == 200, f'item lookup failed: {r.status_code} {r.text}'
    actual = len(r.json()['data'])
    assert actual == count, f'expected {count} items on order {context.order_id}, found {actual}'


# ------------------------------------------------------------------------------ §3 Kafka subscribe

def _consume(context, account, items):
    """ writes an order_b2b message to a file and consumes it via /consume_debug (no broker needed) """
    payload_dir = TEST_DIR / 'logs' / 'payloads'
    payload_dir.mkdir(parents=True, exist_ok=True)
    payload_file = payload_dir / f'order_b2b_{int(time.time() * 1000)}.json'
    payload_file.write_text(json.dumps({"Account": account, "Notes": "behave kafka test", "Items": items}))
    r = requests.get(url=f'{BASE_URL}/consume_debug/order_b2b', params={'file': str(payload_file)},
                     headers=_headers())
    context.consume_response = r
    context.consume_ok = False
    context.order_id = None
    context.blob_id = None
    try:
        body = r.json()
    except ValueError:
        body = {}
    if r.status_code == 200 and body.get('success'):
        context.consume_ok = True
        context.order_id = int(body['order_id'])
        context.blob_id = int(body['blob_id'])


@when('Inbound order message is consumed for "{customer_name}" with {qty1:d} {product1} and {qty2:d} {product2}')
def step_impl(context, customer_name, qty1, product1, qty2, product2):
    _consume(context, _unique_name(context, customer_name), _items((qty1, product1), (qty2, product2)))


@when('Inbound order message is consumed for "{customer_name}" with {quantity:d} {product_name}')
def step_impl(context, customer_name, quantity, product_name):
    _consume(context, _unique_name(context, customer_name), _items((quantity, product_name)))


@then('Order is persisted from the message')
def step_impl(context):
    assert context.consume_ok, \
        f'expected the message to be consumed: {context.consume_response.status_code} {context.consume_response.text}'


@then('Message blob is marked processed')
def step_impl(context):
    r = requests.get(url=f'{BASE_URL}/api/OrderB2bMessage/{context.blob_id}/', headers=_headers())
    assert r.status_code == 200, f'blob lookup failed: {r.status_code} {r.text}'
    assert r.json()['data']['attributes']['is_processed'], f'blob {context.blob_id} is not marked processed'


# ------------------------------------------------------------------------------- §4 Kafka publish

def _logic_log(scenario_name):
    """ the per-scenario logic log the server writes (same naming as the report generator) """
    name = scenario_name[0:25] if len(scenario_name) >= 26 else scenario_name
    return TEST_DIR / 'logs' / 'scenario_logic_logs' / f"{name.replace(' ', '_')}.log"


@then('The order_shipping publish event fired')
def step_impl(context):
    log = _logic_log(context.scenario.name)
    assert log.is_file(), f'no logic log at {log}'
    assert test_utils.does_file_contain('_send_order_to_kafka', str(log)), \
        f'_send_order_to_kafka did not run for this scenario (see {log})'


def _kafka_server():
    env = (TEST_DIR.parent.parent / 'config' / 'default.env').read_text()
    m = re.search(r'^\s*KAFKA_SERVER\s*=\s*(\S+)', env, re.M)
    return m.group(1) if m else 'localhost:9092'


@then('A message for the order is on topic order_shipping')
def step_impl(context):
    """ reads the topic from the beginning and looks for this order's id in a message """
    from confluent_kafka import Consumer
    consumer = Consumer({'bootstrap.servers': _kafka_server(), 'group.id': f'behave-{int(time.time() * 1000)}',
                         'auto.offset.reset': 'earliest', 'enable.auto.commit': False})
    wanted = context.order_id
    found = False
    try:
        consumer.subscribe(['order_shipping'])
        deadline = time.time() + 20
        while time.time() < deadline and not found:
            msg = consumer.poll(1.0)
            if msg is None or msg.error():
                continue
            try:
                body = json.loads(msg.value().decode('utf-8'))
            except ValueError:
                continue
            found = body.get('order_id') == wanted
    finally:
        consumer.close()
    assert found, f'no message for order {wanted} found on topic order_shipping within 20s ' \
                  f'(broker {_kafka_server()})'
