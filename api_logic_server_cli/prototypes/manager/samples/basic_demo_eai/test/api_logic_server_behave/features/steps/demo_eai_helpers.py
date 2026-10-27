"""
Shared helpers for the demo_eai behave steps (no behave decorators here).

Imports are limited to requests / test_utils / stdlib: no imports from logic/, database/ or integration/.
"""
import json
import time
from pathlib import Path

import requests
import test_utils

BASE = 'http://localhost:5656'
PROJECT_DIR = Path(__file__).resolve().parents[4]
BEHAVE_DIR = PROJECT_DIR / 'test' / 'api_logic_server_behave'
MODE_FILE = BEHAVE_DIR / 'logs' / 'delivery_modes.json'
MESSAGES_DIR = BEHAVE_DIR / 'logs' / 'messages'
SCENARIO_LOGS = BEHAVE_DIR / 'logs' / 'scenario_logic_logs'

_headers = {}


def headers(user: str = 'admin') -> dict:
    """Authorization header for <user> (cached: one login per user per run), plus the JSON content type."""
    if user not in _headers:
        _headers[user] = {**test_utils.login(user), 'Content-Type': 'application/json'}
    return _headers[user]


def unique(name: str) -> str:
    """A name no earlier run (or scenario) used: tests modify the database and must be repeatable."""
    return f'{name} {int(time.time() * 1000)}'


def create_customer(name: str, credit_limit: int) -> dict:
    """POST a fresh Customer; returns {'id', 'name'} (the name is the unique one)."""
    unique_name = unique(name)
    body = {"data": {"type": "Customer", "attributes": {"name": unique_name, "credit_limit": credit_limit}}}
    r = requests.post(f'{BASE}/api/Customer/', json=body, headers=headers())
    assert r.status_code < 300, f'create customer failed: {r.status_code} {r.text}'
    return {'id': int(r.json()['data']['id']), 'name': unique_name}


def customer_attrs(customer_id: int) -> dict:
    """Current attributes of the Customer (balance etc.)."""
    r = requests.get(f'{BASE}/api/Customer/{customer_id}/', headers=headers())
    assert r.status_code == 200, f'get customer failed: {r.status_code} {r.text}'
    return r.json()['data']['attributes']


def place_b2b_order(account: str, items: list, notes: str = 'behave test') -> requests.Response:
    """POST the partner format to the OrderB2B custom API; items = [(product name, quantity), ...]."""
    body = {"meta": {"method": "OrderB2B", "args": {"data": {
        "Account": account, "Notes": notes,
        "Items": [{"Name": name, "QuantityOrdered": qty} for name, qty in items]}}}}
    return requests.post(f'{BASE}/api/OrderB2B/OrderB2B', json=body, headers=headers())


def order_attrs(order_id: int) -> dict:
    """Current attributes of the Order."""
    r = requests.get(f'{BASE}/api/Order/{order_id}/', headers=headers())
    assert r.status_code == 200, f'get order failed: {r.status_code} {r.text}'
    return r.json()['data']['attributes']


def order_items(order_id: int) -> list:
    """The Item rows of the Order, as [{'id', 'product_id', 'quantity', 'unit_price', 'amount'}, ...]."""
    r = requests.get(f'{BASE}/api/Item/', params={"filter[order_id]": order_id, "page[limit]": 50}, headers=headers())
    assert r.status_code == 200, f'get items failed: {r.status_code} {r.text}'
    return [{'id': int(each['id']), **each['attributes']} for each in r.json()['data']]


def scenario_log(scenario_name: str) -> Path:
    """Path of the logic log for the scenario (test_utils.prt truncates the name to 25 characters)."""
    name = scenario_name[0:25] if len(scenario_name) >= 26 else scenario_name
    return SCENARIO_LOGS / f'{name.replace(" ", "_")}.log'


def record_mode(context, mode: str, broker: str = None) -> None:
    """Remember how this scenario's Kafka message was delivered ('live' or 'simulated'), for the traceability report."""
    modes = json.loads(MODE_FILE.read_text()) if MODE_FILE.is_file() else {}
    modes[f'{context.feature.name} / {context.scenario.name}'] = {"mode": mode, **({"broker": broker} if broker else {})}
    MODE_FILE.parent.mkdir(parents=True, exist_ok=True)
    MODE_FILE.write_text(json.dumps(modes, indent=2))


def write_message(account: str, items: list) -> str:
    """Write an order_b2b message file the SERVER can read; returns its path relative to the project root."""
    MESSAGES_DIR.mkdir(parents=True, exist_ok=True)
    path = MESSAGES_DIR / f'order_b2b_{int(time.time() * 1000)}.json'
    path.write_text(json.dumps({"Account": account, "Notes": "behave kafka test",
                                "Items": [{"Name": name, "QuantityOrdered": qty} for name, qty in items]}))
    return str(path.relative_to(PROJECT_DIR))


def wait_for_blob(account: str, timeout: float = 20):
    """Live Kafka is asynchronous: poll until the blob for this (unique) account is processed or has error_text."""
    deadline = time.time() + timeout
    while time.time() < deadline:
        r = requests.get(f'{BASE}/api/OrderB2bMessage/', params={"sort": "-id", "page[limit]": 30}, headers=headers())
        for each in r.json()['data']:
            a = each['attributes']
            if account in (a.get('payload') or '') and (a.get('is_processed') or a.get('error_text')):
                return int(each['id']), a
        time.sleep(0.5)
    return None, None


def deliver_message(context, account: str, items: list, mode: str = 'auto') -> None:
    """Send the message through the debug endpoint; sets context.consumed / context.error_text / context.blob_id the same way
    for both modes.  mode='live' with no Kafka available skips the scenario (not verified), it does not fail it."""
    path = write_message(account, items)
    r = requests.get(f'{BASE}/consume_debug/order_b2b', params={"file": path, "mode": mode})
    body = r.json()
    context.consumed, context.blob_id, context.error_text = False, None, None
    if r.status_code == 409:
        context.scenario.skip(body.get('error', 'live Kafka is not available'))
        return
    record_mode(context, body['mode'], body.get('broker'))
    context.delivery_mode = body['mode']
    if body['mode'] == 'simulated':
        context.consumed = bool(body.get('success'))
        context.blob_id = body.get('blob_id')
        context.error_text = body.get('error')
        return
    assert body.get('published'), f'live publish failed: {r.text}'
    context.blob_id, a = wait_for_blob(account)
    assert context.blob_id, (f'no processed blob for {account} within 20 s - was the server started AFTER Kafka, '
                             f'with KAFKA_SERVER and a unique KAFKA_CONSUMER_GROUP?')
    context.error_text = a.get('error_text')
    context.consumed = bool(a.get('is_processed')) and not context.error_text
