"""
Shared helpers for the demo_eai step files (no step definitions here).
All writes go through the API (rules fire); test data is unique per scenario (timestamped names).
"""
import datetime
import json
import time
from pathlib import Path

import requests
import test_utils

BASE = 'http://localhost:5656'
PROJECT_DIR = Path(__file__).resolve().parents[4]
PRICES = {"Gadget": 150, "Widget": 90, "Thingamajig": 5075, "Doodad": 110, "Green": 109}   # verified in db.sqlite
_tokens = {}


def headers(user: str = 'admin') -> dict:
    """Auth header for user (cached per test run)."""
    if user not in _tokens:
        _tokens[user] = test_utils.login(user)
    return {**_tokens[user], 'Content-Type': 'application/vnd.api+json'}


def unique(name: str) -> str:
    time.sleep(0.002)
    return f"{name} {int(time.time() * 1000)}"


def today() -> str:
    return datetime.date.today().isoformat()


def get(resource: str, key, user: str = 'admin') -> dict:
    """Attributes of one row (None if not found)."""
    r = requests.get(f'{BASE}/api/{resource}/{key}/', headers=headers(user))
    if r.status_code == 404:
        return None
    assert r.status_code == 200, f'GET {resource}/{key}: {r.status_code} {r.text}'
    return r.json()['data']['attributes']


def find(resource: str, user: str = 'admin', **filters) -> list:
    params = {f'filter[{k}]': v for k, v in filters.items()}
    params["page[limit]"] = 500
    r = requests.get(f'{BASE}/api/{resource}/', params=params, headers=headers(user))
    assert r.status_code == 200, f'GET {resource}: {r.status_code} {r.text}'
    return r.json()['data']


def post(resource: str, attributes: dict) -> requests.Response:
    return requests.post(f'{BASE}/api/{resource}/', headers=headers(),
                         json={"data": {"type": resource, "attributes": attributes}})


def patch(resource: str, key, attributes: dict) -> requests.Response:
    return requests.patch(f'{BASE}/api/{resource}/{key}/', headers=headers(),
                          json={"data": {"type": resource, "id": str(key), "attributes": attributes}})


def delete(resource: str, key) -> requests.Response:
    return requests.delete(f'{BASE}/api/{resource}/{key}/', headers=headers())


def new_customer(context, label: str, credit_limit: float) -> int:
    """Create a fresh customer; remember it in context.customers[label]."""
    name = unique(label)
    r = post('Customer', {"name": name, "credit_limit": credit_limit, "balance": 0})
    assert r.status_code == 201, f'create customer: {r.status_code} {r.text}'
    if not hasattr(context, 'customers'):
        context.customers = {}
    context.customers[label] = {"id": int(r.json()['data']['id']), "name": name}
    return context.customers[label]["id"]


def b2b_order(account: str, items: list, notes: str = "behave test") -> requests.Response:
    """POST the partner order to the OrderB2B custom API. items: [(qty, product_name), ...]"""
    data = {"Account": account, "Notes": notes,
            "Items": [{"Name": name, "QuantityOrdered": qty} for qty, name in items]}
    return requests.post(f'{BASE}/api/OrderB2B/OrderB2B', headers=headers(),
                         json={"meta": {"method": "OrderB2B", "args": {"data": data}}})


def items_of(order_id: int) -> list:
    """[(item_id, attributes), ...] of an order, in id order."""
    rows = find('Item', order_id=order_id)
    return sorted([(int(each['id']), each['attributes']) for each in rows])


def balance(customer_id: int) -> float:
    return float(get('Customer', customer_id)['balance'] or 0)


def amount_total(order_id: int) -> float:
    return float(get('Order', order_id)['amount_total'] or 0)


DAILY_COLUMNS = ["order_count", "order_amount", "message_received", "message_processed", "message_rejected",
                 "message_pending", "request_received", "request_processed", "request_rejected", "request_pending"]


def daily(day: str = None) -> dict:
    """Today's (or day's) DailyFlow totals as floats; zeros when the day has no bucket yet."""
    row = get('DailyFlow', day or today())
    return {col: float((row or {}).get(col) or 0) for col in DAILY_COLUMNS}


def delta(before: dict, after: dict) -> dict:
    return {col: round(after[col] - before[col], 2) for col in DAILY_COLUMNS}


# ---------------- Kafka subscribe (mode-aware: live through the broker, or simulated) ----------------

MODE_FILE = PROJECT_DIR / 'test' / 'api_logic_server_behave' / 'logs' / 'delivery_modes.json'
MESSAGE_DIR = 'test/api_logic_server_behave/logs/messages'      # relative to the project root (the server reads it)


def record_mode(context, mode, broker=None):
    """Remember how this scenario's message was delivered, for the traceability report."""
    modes = json.loads(MODE_FILE.read_text()) if MODE_FILE.is_file() else {}
    modes[f'{context.feature.name} / {context.scenario.name}'] = {"mode": mode, **({"broker": broker} if broker else {})}
    MODE_FILE.parent.mkdir(parents=True, exist_ok=True)
    MODE_FILE.write_text(json.dumps(modes, indent=2))


def write_message(account: str, items: list) -> str:
    """Write an order_b2b message (same shape as message_formats/order_b2b.json) to a file the server can read."""
    folder = PROJECT_DIR / MESSAGE_DIR
    folder.mkdir(parents=True, exist_ok=True)
    file_name = f"order_b2b_{int(time.time() * 1000)}.json"
    message = {"Account": account, "Notes": "behave kafka message",
               "Items": [{"Name": name, "QuantityOrdered": qty} for qty, name in items]}
    (folder / file_name).write_text(json.dumps(message, indent=2))
    return f"{MESSAGE_DIR}/{file_name}"


def wait_for_blob(account: str, timeout: int = 30):
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


def deliver_message(context, account: str, items: list, mode: str = 'auto'):
    """Send the message through the debug endpoint; sets context.consumed / blob_id / error_text for both modes."""
    path = write_message(account, items)
    r = requests.get(f'{BASE}/consume_debug/order_b2b', params={"file": path, "mode": mode})
    body = r.json()
    context.consumed, context.blob_id, context.error_text, context.delivery_mode = False, None, None, None
    if r.status_code == 409:                            # live required, not available: NOT VERIFIED, not failed
        context.scenario.skip(body.get('error', 'live Kafka is not available'))
        return
    context.delivery_mode = body['mode']
    record_mode(context, body['mode'], body.get('broker'))
    if body['mode'] == 'simulated':
        context.consumed, context.blob_id, context.error_text = bool(body.get('success')), body.get('blob_id'), body.get('error')
        return
    assert body.get('published'), f'live publish failed: {r.text}'
    context.blob_id, a = wait_for_blob(account)
    assert context.blob_id, ('no processed blob for ' + account + ' within 30 s - was the server started AFTER Kafka, '
                             'with KAFKA_SERVER and a unique KAFKA_CONSUMER_GROUP?')
    context.error_text = a.get('error_text')
    context.consumed = bool(a.get('is_processed')) and not context.error_text


def orders_for(customer_id: int) -> list:
    return sorted(int(each['id']) for each in find('Order', customer_id=customer_id))


def server_log_text() -> str:
    return (PROJECT_DIR / 'logs' / 'als.log').read_text(encoding='utf-8', errors='replace')
