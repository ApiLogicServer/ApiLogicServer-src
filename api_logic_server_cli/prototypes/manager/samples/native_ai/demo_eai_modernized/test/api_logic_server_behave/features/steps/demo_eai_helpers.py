"""
Shared helpers for the demo_eai feature steps: REST calls with a token, fresh test data (Rule #0: repeatable),
and the per-scenario logic log.
"""
import re
import time
from pathlib import Path

import requests
import test_utils

BASE = 'http://localhost:5656'
API = f'{BASE}/api'
_behave_dir = Path(__file__).parent.parent.parent       # steps -> features -> api_logic_server_behave
PROJECT_DIR = _behave_dir.parent.parent

_headers = {}


def headers(user: str = 'admin') -> dict:
    """ bearer token header for user (cached per user); admin has the sa role """
    if user not in _headers:
        _headers[user] = {**test_utils.login(user), 'Content-Type': 'application/json'}
    return _headers[user]


def unique(name: str) -> str:
    return f'{name} {int(time.time() * 1000)}'


def scenario_log_name(scenario_name: str) -> str:
    return re.sub(r'[\s()/\\]', '_', scenario_name)[:25]


def logic_log_file(context) -> str:
    return str(_behave_dir / 'logs' / 'scenario_logic_logs' / f'{context.scenario_log}.log')


def open_logic_log(context) -> None:
    """ ONCE per scenario, in the Given, before the first API call (a second call wipes the log) """
    context.scenario_log = scenario_log_name(context.scenario.name)
    test_utils.prt(f'\n{context.scenario.name} - starting test\n', context.scenario_log)


def logic_log_text(context) -> str:
    path = Path(logic_log_file(context))
    return path.read_text() if path.is_file() else ''


def post(kind: str, attributes: dict, user: str = 'admin'):
    return requests.post(f'{API}/{kind}/', headers=headers(user),
                         json={'data': {'type': kind, 'attributes': attributes}})


def patch(kind: str, row_id, attributes: dict, user: str = 'admin'):
    return requests.patch(f'{API}/{kind}/{row_id}/', headers=headers(user),
                          json={'data': {'type': kind, 'id': str(row_id), 'attributes': attributes}})


def get(kind: str, row_id, user: str = 'admin'):
    return requests.get(f'{API}/{kind}/{row_id}/', headers=headers(user))


def attrs(kind: str, row_id) -> dict:
    r = get(kind, row_id)
    assert r.status_code == 200, f'GET {kind}/{row_id}: {r.status_code} {r.text}'
    return r.json()['data']['attributes']


def product_id(name: str) -> int:
    r = requests.get(f'{API}/Product/', params={'filter[name]': name}, headers=headers())
    return int(r.json()['data'][0]['id'])


def create_customer(name: str, credit_limit: int) -> int:
    r = post('Customer', {'name': name, 'credit_limit': credit_limit})
    assert r.status_code == 201, f'create customer: {r.status_code} {r.text}'
    return int(r.json()['data']['id'])


def create_order(customer_id: int, **more) -> requests.Response:
    return post('Order', {'customer_id': customer_id, **more})


def add_item(order_id: int, product: int, quantity: int) -> requests.Response:
    return post('Item', {'order_id': order_id, 'product_id': product, 'quantity': quantity})
