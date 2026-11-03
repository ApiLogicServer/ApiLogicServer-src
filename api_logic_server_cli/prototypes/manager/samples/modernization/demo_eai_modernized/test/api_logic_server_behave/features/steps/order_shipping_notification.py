import re
from behave import *

import demo_eai_helpers as h

PUBLISH = re.compile(r"\{publish_kafka_message: topic='order_shipping', key=\{'id': (\d+)\}")
# The publish is logged by kafka_producer.publish_kafka_message whether or not a broker answers (the log proves the
# publish call, not delivery; delivery is checked live by "verify message subscriptions").


@when('an order is created already shipped')
def step_impl(context):
    context.last_response = h.create_order(context.customer_id, date_shipped='2026-10-27')
    assert context.last_response.status_code == 201, context.last_response.text
    context.order_id = int(context.last_response.json()['data']['id'])


@when('the order notes are changed')
def step_impl(context):
    context.last_response = h.patch('Order', context.order_id, {'notes': 'changed after shipping'})
    assert context.last_response.status_code == 200, context.last_response.text


@then('a shipping message is published for the order')
def step_impl(context):
    ids = [int(each) for each in PUBLISH.findall(h.logic_log_text(context))]
    assert context.order_id in ids, f'no order_shipping publish for order {context.order_id} in {h.logic_log_file(context)}'


@then('no shipping message is published')
def step_impl(context):
    assert not PUBLISH.findall(h.logic_log_text(context)), 'an order_shipping message was published'


@then('one shipping message was published')
def step_impl(context):
    count = len(PUBLISH.findall(h.logic_log_text(context)))
    assert count == 1, f'expected exactly one order_shipping publish, found {count}'
