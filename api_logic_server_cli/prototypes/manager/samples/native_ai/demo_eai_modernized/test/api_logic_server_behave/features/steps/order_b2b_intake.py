import json
import time
from behave import *
import requests

import demo_eai_helpers as h

MODE_FILE = h._behave_dir / 'logs' / 'delivery_modes.json'
MESSAGE_DIR = h._behave_dir / 'logs' / 'messages'     # a file the SERVER can read, relative to the project root


def partner_order(account, items, notes='Test order') -> dict:
    return {'Account': account, 'Notes': notes, 'Items': items}


def post_partner(context, payload, user='admin'):
    headers = h.headers(user) if user else {'Content-Type': 'application/json'}
    context.partner_response = requests.post(f'{h.BASE}/OrderB2B', json=payload, headers=headers)
    context.last_response = context.partner_response
    if context.partner_response.status_code == 201:
        context.order_id = context.partner_response.json()['order_id']


@when('a partner order for the customer with 1 Widget and 2 Gadget is posted')
def step_impl(context):
    post_partner(context, partner_order(context.customer_name, [{'Name': 'Widget', 'QuantityOrdered': 1},
                                                                {'Name': 'Gadget', 'QuantityOrdered': 2}]))


@when('a partner order for account "{account}" with 1 Widget is posted')
def step_impl(context, account):
    post_partner(context, partner_order(account, [{'Name': 'Widget', 'QuantityOrdered': 1}]))


@when('a partner order for the customer with 1 "{product}" is posted')
def step_impl(context, product):
    post_partner(context, partner_order(context.customer_name, [{'Name': product, 'QuantityOrdered': 1}]))


@when('a partner order for the customer with no items is posted')
def step_impl(context):
    post_partner(context, partner_order(context.customer_name, []))


@when('a partner order for the customer with 0 Widget is posted')
def step_impl(context):
    post_partner(context, partner_order(context.customer_name, [{'Name': 'Widget', 'QuantityOrdered': 0}]))


@when('a partner order for the customer with 1 Widget is posted without a token')
def step_impl(context):
    post_partner(context, partner_order(context.customer_name, [{'Name': 'Widget', 'QuantityOrdered': 1}]), user=None)


@then('the partner request answers {status:d}')
def step_impl(context, status):
    r = context.partner_response
    assert r.status_code == status, f'expected {status}, got {r.status_code}: {r.text}'


@then('the partner order total is {expected:d}')
def step_impl(context, expected):
    actual = float(h.attrs('Order', context.order_id)['amount_total'])
    assert abs(actual - expected) < 0.01, f'order amount_total {actual}, expected {expected}'


@then('the partner error mentions "{message}"')
def step_impl(context, message):
    assert message in context.partner_response.text, f'"{message}" not in {context.partner_response.text}'


# ---- Kafka subscribe: mode-aware (live through the broker when one answers, else simulated) -------------------

def record_mode(context, mode, broker=None):
    """ remember how this scenario's message was delivered, for the traceability report """
    modes = json.loads(MODE_FILE.read_text()) if MODE_FILE.is_file() else {}
    modes[f'{context.feature.name} / {context.scenario.name}'] = {'mode': mode, **({'broker': broker} if broker else {})}
    MODE_FILE.parent.mkdir(parents=True, exist_ok=True)
    MODE_FILE.write_text(json.dumps(modes, indent=2))


def write_message(account) -> str:
    MESSAGE_DIR.mkdir(parents=True, exist_ok=True)
    path = MESSAGE_DIR / f'{int(time.time() * 1000)}.json'
    path.write_text(json.dumps(partner_order(account, [{'Name': 'Widget', 'QuantityOrdered': 1},
                                                       {'Name': 'Gadget', 'QuantityOrdered': 2}])))
    return str(path.relative_to(h.PROJECT_DIR))


def wait_for_blob(account, timeout=20):
    """ live Kafka is asynchronous: poll until the blob for this (unique) account is processed or has error_text """
    deadline = time.time() + timeout
    while time.time() < deadline:
        r = requests.get(f'{h.API}/OrderB2bMessage/', params={'sort': '-id', 'page[limit]': 30}, headers=h.headers())
        for each in r.json()['data']:
            a = each['attributes']
            if account in (a.get('payload') or '') and (a.get('is_processed') or a.get('error_text')):
                return int(each['id']), a
        time.sleep(0.5)
    return None, None


def deliver_message(context, account, mode='auto'):
    """ send the message through the debug endpoint; set context.consumed / blob_id / error_text for both modes """
    path = write_message(account)
    r = requests.get(f'{h.BASE}/consume_debug/order_b2b', params={'file': path, 'mode': mode})
    body = r.json()
    context.consumed, context.blob_id, context.error_text = False, None, None
    if r.status_code == 409:        # live required, not available: NOT VERIFIED, not failed
        context.scenario.skip(body.get('error', 'live Kafka is not available'))
        return
    record_mode(context, body['mode'], body.get('broker'))
    if body['mode'] == 'simulated':
        context.consumed, context.blob_id, context.error_text = bool(body.get('success')), body.get('blob_id'), body.get('error')
        return
    assert body.get('published'), f'live publish failed: {r.text}'
    context.blob_id, a = wait_for_blob(account)
    assert context.blob_id, (f'no processed blob for {account} within 20 s - was the server started AFTER Kafka, '
                             f'with KAFKA_SERVER and a unique KAFKA_CONSUMER_GROUP?')
    context.error_text = a.get('error_text')
    context.consumed = bool(a.get('is_processed')) and not context.error_text
    context.blob_attrs = a


@when('an inbound order message for the customer is delivered to topic order_b2b')
def step_impl(context):
    deliver_message(context, context.customer_name)


@when('an inbound order message for an unknown account is delivered to topic order_b2b')
def step_impl(context):
    deliver_message(context, h.unique('No Such Account'))


@when('an inbound order message for the customer is delivered live to topic order_b2b')
def step_impl(context):
    deliver_message(context, context.customer_name, mode='live')


@then('the inbound message is processed')
def step_impl(context):
    assert context.consumed, f'message not processed: {context.error_text}'


@then('the inbound message is rejected with "{message}"')
def step_impl(context, message):
    assert not context.consumed, 'message was processed, expected a rejection'
    assert message in (context.error_text or ''), f'"{message}" not in error: {context.error_text}'


@then('the inbound message blob is unprocessed and has error_text "{message}"')
def step_impl(context, message):
    assert not context.blob_attrs.get('is_processed'), 'blob is marked processed'
    assert message in (context.error_text or ''), f'"{message}" not in error_text: {context.error_text}'
