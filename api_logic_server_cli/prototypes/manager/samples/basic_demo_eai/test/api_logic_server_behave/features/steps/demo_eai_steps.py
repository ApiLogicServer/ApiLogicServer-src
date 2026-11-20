"""
Steps for the demo_eai features: Check Credit, B2B Order Integration, Kafka Subscribe Order Integration,
Kafka Publish Shipping Notification, Row-Level Security, Order Flow Dashboard.

Step ordering (Rule #0.5): within each pattern family, the more specific pattern (two items, "second", "live",
"unknown account") is declared BEFORE the general one.
"""
import json
import re
import time
import datetime

import requests
from behave import *

import test_utils
from demo_eai_support import (BASE, PRICES, headers, unique, today, get, find, post, patch, delete, new_customer,
                              b2b_order, items_of, balance, amount_total, daily, delta, deliver_message, orders_for,
                              server_log_text)

_product_ids = {}


def product_id(name: str) -> int:
    if not _product_ids:
        for each in find('Product'):
            _product_ids[each['attributes']['name']] = int(each['id'])
    return _product_ids[name]


def product_name(pid: int) -> str:
    product_id('Widget')   # loads the map
    return {v: k for k, v in _product_ids.items()}[int(pid)]


def log_scenario(context):
    """Logic log for this scenario: once, before its first API call (Rule #6)."""
    if not getattr(context, 'logged', False):
        context.logged = True
        test_utils.prt(f'\n{context.scenario.name}\n', context.scenario.name)


def place_order(context, label: str, items: list, as_second: bool = False):
    """B2B order for a customer created in this scenario (label) - or any account name not created here."""
    log_scenario(context)
    customers = getattr(context, 'customers', {})
    account = customers[label]["name"] if label in customers else label
    r = b2b_order(account, items)
    context.last_response = r
    context.order_created = r.status_code == 200
    result = r.json().get('meta', {}).get('result', {}) if context.order_created else {}
    order_id = result.get('order_id')
    context.request_id = result.get('request_id')
    context.request_account = account
    if not hasattr(context, 'order_ids'):
        context.order_ids = []
    if order_id:
        context.order_ids.append(int(order_id))
        if not as_second:
            context.order_id = int(order_id)
    else:
        context.order_id = getattr(context, 'order_id', None)


def request_row(context) -> tuple:
    """The OrderB2bRequest of the last B2B call: by id (accepted), else the newest whose payload names the account."""
    if context.request_id:
        return int(context.request_id), get('OrderB2bRequest', context.request_id)
    r = requests.get(f'{BASE}/api/OrderB2bRequest/', params={"sort": "-id", "page[limit]": 30}, headers=headers())
    for each in r.json()['data']:
        if context.request_account in (each['attributes'].get('payload') or ''):
            return int(each['id']), each['attributes']
    return None, None


# ---------------------------------------------------------------- Given / setup

@step('a new customer "{label}" with credit limit {limit:d}')
def step_impl(context, label, limit):
    log_scenario(context)
    new_customer(context, label, limit)


@step('a second B2B order is placed for "{label}" with {q:d} {p}')
def step_impl(context, label, q, p):
    place_order(context, label, [(q, p)], as_second=True)


@step('a B2B order is placed for an unknown account')
def step_impl(context):
    place_order(context, unique("Nobody"), [(1, "Widget")])


@step('a B2B order is placed for "{label}" with {q1:d} {p1} and {q2:d} {p2}')
def step_impl(context, label, q1, p1, q2, p2):
    place_order(context, label, [(q1, p1), (q2, p2)])


@step('a B2B order is placed for "{label}" with {q:d} {p}')
def step_impl(context, label, q, p):
    place_order(context, label, [(q, p)])


@step("today's totals are noted")
def step_impl(context):
    log_scenario(context)
    context.today_before = daily()


@step('the totals of day "{day}" are noted')
def step_impl(context, day):
    context.day_before = daily(day)


# ---------------------------------------------------------------- When / changes (CRUD, Phase 1)

@step('the quantity of the first item is changed to {qty:d}')
def step_impl(context, qty):
    item_id, _ = items_of(context.order_id)[0]
    context.last_change = patch('Item', item_id, {"quantity": qty})


@step('the product of the first item is changed to {p}')
def step_impl(context, p):
    item_id, _ = items_of(context.order_id)[0]
    context.last_change = patch('Item', item_id, {"product_id": product_id(p)})
    assert context.last_change.status_code == 200, context.last_change.text


@step('the first item of the first order is moved to the second order')
def step_impl(context):
    item_id, _ = items_of(context.order_ids[0])[0]
    r = patch('Item', item_id, {"order_id": context.order_ids[1]})
    assert r.status_code == 200, r.text


@step('the first item is deleted')
def step_impl(context):
    item_id, _ = items_of(context.order_id)[0]
    r = delete('Item', item_id)
    assert r.status_code in (200, 204), r.text


@step('the order is moved to customer "{label}"')
def step_impl(context, label):
    r = patch('Order', context.order_id, {"customer_id": context.customers[label]["id"]})
    assert r.status_code == 200, r.text


@step('the order is moved to day "{day}"')
def step_impl(context, day):
    r = patch('Order', context.order_id, {"CreatedOnDay": day})
    assert r.status_code == 200, r.text


@step('the order is deleted')
def step_impl(context):
    r = delete('Order', context.order_id)
    assert r.status_code in (200, 204), r.text


@step('the order is unshipped')
def step_impl(context):
    r = patch('Order', context.order_id, {"date_shipped": None})
    assert r.status_code == 200, r.text


@step('the order is shipped')
def step_impl(context):
    r = patch('Order', context.order_id, {"date_shipped": today()})
    assert r.status_code == 200, r.text
    time.sleep(0.5)    # the publish is logged after the flush


@step('the order notes are changed')
def step_impl(context):
    r = patch('Order', context.order_id, {"notes": unique("edited")})
    assert r.status_code == 200, r.text
    time.sleep(0.5)


@step('the B2B request is set back to not processed')
def step_impl(context):
    r = patch('OrderB2bRequest', context.request_id, {"is_processed": False})
    assert r.status_code == 200, r.text


@step('the message is set back to not processed')
def step_impl(context):
    r = patch('OrderB2bMessage', context.blob_id, {"is_processed": False})
    assert r.status_code == 200, r.text


# ---------------------------------------------------------------- Kafka subscribe (mode-aware)

@step('an order message for "{label}" with {q1:d} {p1} and {q2:d} {p2} is delivered to topic order_b2b')
def step_impl(context, label, q1, p1, q2, p2):
    log_scenario(context)
    deliver_message(context, context.customers[label]["name"], [(q1, p1), (q2, p2)])


@step('an order message for "{label}" with {q:d} {p} is delivered live to topic order_b2b')
def step_impl(context, label, q, p):
    log_scenario(context)
    deliver_message(context, context.customers[label]["name"], [(q, p)], mode='live')


@step('an order message for "{label}" with {q:d} {p} is delivered to topic order_b2b')
def step_impl(context, label, q, p):
    log_scenario(context)
    deliver_message(context, context.customers[label]["name"], [(q, p)])


@then('the message is processed')
def step_impl(context):
    assert context.consumed, f'message not processed ({context.delivery_mode}): {context.error_text}'


@then('the message is rejected with "{text}"')
def step_impl(context, text):
    assert not context.consumed, 'message was expected to be rejected'
    assert context.error_text and text in context.error_text, f'error was: {context.error_text}'


@then('the message blob is not processed and has error text')
def step_impl(context):
    blob = get('OrderB2bMessage', context.blob_id)
    assert not blob['is_processed'], f'blob {context.blob_id} is processed'
    assert blob['error_text'], f'blob {context.blob_id} has no error_text'


@then('the message is dated today')
def step_impl(context):
    blob = get('OrderB2bMessage', context.blob_id)
    assert blob['CreatedOnDay'] == today() and str(blob['CreatedOn']).startswith(today()), blob


@then('"{label}" has one order with total {total:d}')
def step_impl(context, label, total):
    ids = orders_for(context.customers[label]["id"])
    assert len(ids) == 1, f'expected one order, found {ids}'
    context.order_id = ids[0]
    assert abs(amount_total(ids[0]) - total) < 0.01, f'total {amount_total(ids[0])}'


@then('"{label}" has no orders')
def step_impl(context, label):
    ids = orders_for(context.customers[label]["id"])
    assert ids == [], f'expected no orders, found {ids}'


# ---------------------------------------------------------------- Then: B2B / Check Credit

@then('the order is accepted')
def step_impl(context):
    assert context.order_created, f'order rejected: {context.last_response.status_code} {context.last_response.text}'


@then('the order is rejected with "{text}"')
def step_impl(context, text):
    r = context.last_response
    assert r.status_code == 400, f'expected HTTP 400, got {r.status_code}: {r.text}'
    assert text in r.text, r.text


@then('the change is rejected with "{text}"')
def step_impl(context, text):
    r = context.last_change
    assert r.status_code >= 400, f'expected a rejection, got {r.status_code}: {r.text}'
    assert text in r.text, r.text


@then('the order belongs to "{label}"')
def step_impl(context, label):
    assert int(get('Order', context.order_id)['customer_id']) == context.customers[label]["id"]


@then('the order items are {q1:d} {p1} and {q2:d} {p2}')
def step_impl(context, q1, p1, q2, p2):
    actual = sorted((a['quantity'], product_name(a['product_id'])) for _, a in items_of(context.order_id))
    assert actual == sorted([(q1, p1), (q2, p2)]), actual


@then('the B2B request is recorded as processed')
def step_impl(context):
    _, req = request_row(context)
    assert req and req['is_processed'] and not req['error_text'], req


@then('the B2B request is recorded with an error')
def step_impl(context):
    _, req = request_row(context)
    assert req and not req['is_processed'] and req['error_text'], req


@then('the B2B request is dated today')
def step_impl(context):
    _, req = request_row(context)
    assert req['CreatedOnDay'] == today() and str(req['CreatedOn']).startswith(today()), req


@then('the item prices are copied from the products')
def step_impl(context):
    for _, a in items_of(context.order_id):
        assert abs(float(a['unit_price']) - PRICES[product_name(a['product_id'])]) < 0.01, a


@then('each item amount is quantity times unit price')
def step_impl(context):
    for _, a in items_of(context.order_id):
        assert abs(float(a['amount']) - a['quantity'] * float(a['unit_price'])) < 0.01, a


@then('the first item unit price is {price:d}')
def step_impl(context, price):
    _, a = items_of(context.order_id)[0]
    assert abs(float(a['unit_price']) - price) < 0.01, a


@then('the first item amount is {amount:d}')
def step_impl(context, amount):
    _, a = items_of(context.order_id)[0]
    assert abs(float(a['amount']) - amount) < 0.01, a


@then('the first order total is {total:d}')
def step_impl(context, total):
    assert abs(amount_total(context.order_ids[0]) - total) < 0.01, amount_total(context.order_ids[0])


@then('the second order total is {total:d}')
def step_impl(context, total):
    assert abs(amount_total(context.order_ids[1]) - total) < 0.01, amount_total(context.order_ids[1])


@then('the order total is {total:d}')
def step_impl(context, total):
    assert abs(amount_total(context.order_id) - total) < 0.01, amount_total(context.order_id)


@then('the balance of "{label}" is {expected:d}')
def step_impl(context, label, expected):
    actual = balance(context.customers[label]["id"])
    assert abs(actual - expected) < 0.01, f'balance {actual}, expected {expected}'


@then('the order is dated today')
def step_impl(context):
    order = get('Order', context.order_id)
    assert order['CreatedOnDay'] == today() and str(order['CreatedOn']).startswith(today()), order


# ---------------------------------------------------------------- Then: Kafka publish

def _publish_count(order_id: int) -> int:
    return server_log_text().count(f"publish_kafka_message: topic='order_shipping', key={{'id': {order_id}}}")


@then('an order_shipping message is published for the order')
def step_impl(context):
    assert _publish_count(context.order_id) == 1, f'publish count {_publish_count(context.order_id)}'


@then('the message has the order_shipping shape with total {total:d} and {n:d} items')
def step_impl(context, total, n):
    line = next((each for each in server_log_text().splitlines()
                 if each.startswith('{') and f'"order_id": {context.order_id},' in each), None)
    assert line, f'no order_shipping message for order {context.order_id} in logs/als.log'
    message = json.loads(line)
    assert set(message) == {"order_id", "order_date", "customer_name", "total", "items"}, message
    assert message["customer_name"] == context.customers[list(context.customers)[0]]["name"], message
    assert abs(message["total"] - total) < 0.01 and len(message["items"]) == n, message
    assert set(message["items"][0]) == {"quantity", "product_name", "unit_price"}, message


@then('no order_shipping message is published for the order')
def step_impl(context):
    assert _publish_count(context.order_id) == 0, f'publish count {_publish_count(context.order_id)}'


@then('exactly one order_shipping message is published for the order')
def step_impl(context):
    assert _publish_count(context.order_id) == 1, f'publish count {_publish_count(context.order_id)}'


# ---------------------------------------------------------------- Security

@step('a sales user queries the Customer list')
def step_impl(context):
    log_scenario(context)
    context.sales_user = 's1'      # Keycloak user with the sales role


@then('the sales user sees "{label}"')
def step_impl(context, label):
    assert find('Customer', user=context.sales_user, name=context.customers[label]["name"]), 'not visible to sales'


@then('the sales user does not see "{label}"')
def step_impl(context, label):
    assert not find('Customer', user=context.sales_user, name=context.customers[label]["name"]), 'visible to sales'


@then('an admin user sees "{label}"')
def step_impl(context, label):
    assert find('Customer', user='admin', name=context.customers[label]["name"]), 'not visible to admin'


# ---------------------------------------------------------------- Dashboard

@then("today's order count rose by {count:d} and order amount by {amount:d}")
def step_impl(context, count, amount):
    d = delta(context.today_before, daily())
    assert d["order_count"] == count and d["order_amount"] == amount, d


@then('day "{day}" order count rose by {count:d} and order amount by {amount:d}')
def step_impl(context, day, count, amount):
    d = delta(context.day_before, daily(day))
    assert d["order_count"] == count and d["order_amount"] == amount, d


@then("today's requests rose by {rec:d} received, {proc:d} processed, {rej:d} rejected and {pend:d} not yet done")
def step_impl(context, rec, proc, rej, pend):
    d = delta(context.today_before, daily())
    actual = (d["request_received"], d["request_processed"], d["request_rejected"], d["request_pending"])
    assert actual == (rec, proc, rej, pend), d


@then("today's messages rose by {rec:d} received, {proc:d} processed, {rej:d} rejected and {pend:d} not yet done")
def step_impl(context, rec, proc, rej, pend):
    d = delta(context.today_before, daily())
    actual = (d["message_received"], d["message_processed"], d["message_rejected"], d["message_pending"])
    assert actual == (rec, proc, rej, pend), d


def _open_chart(name: str) -> dict:
    r = requests.get(f'{BASE}/chart_graphics/{name}')
    assert r.status_code == 200, r.text
    match = re.search(r'const result = (\{.*?\});\n', r.text, re.S)
    assert match, 'no chart data in the rendered page'
    return json.loads(match.group(1))


@step('the order volume chart is opened again')
def step_impl(context):
    context.chart_after = _open_chart('order_volume')


@step('the order volume chart is opened')
def step_impl(context):
    log_scenario(context)
    context.chart = _open_chart('order_volume')


@then('the chart shows {n:d} days ending today')
def step_impl(context, n):
    labels = context.chart["labels"]
    assert len(labels) == n and labels[-1] == today()[5:], labels


@then('every day with no totals shows zero')
def step_impl(context):
    labels = context.chart["labels"]
    start = datetime.date.today() - datetime.timedelta(days=len(labels) - 1)
    days = [(start + datetime.timedelta(days=i)).isoformat() for i in range(len(labels))]
    with_totals = {each['id'] for each in find('DailyFlow') if each['id'] >= days[0]}
    counts = context.chart["datasets"][0]["data"]
    quiet = [i for i, d in enumerate(days) if d not in with_totals]
    assert quiet, 'no quiet day in the window to check'
    assert all(counts[i] == 0 for i in quiet), [(days[i], counts[i]) for i in quiet]


@then("the chart's value for today rose by 1 and matches today's order count")
def step_impl(context):
    before, after = context.chart["datasets"][0]["data"][-1], context.chart_after["datasets"][0]["data"][-1]
    assert after - before == 1, (before, after)
    assert after == daily()["order_count"], (after, daily()["order_count"])
