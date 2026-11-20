from behave import *
import demo_eai_helpers as h


@when('an inbound order message for "{customer_name}" with {qty1:d} {product1} and {qty2:d} {product2} is delivered to topic order_b2b')
def step_impl(context, customer_name, qty1, product1, qty2, product2):
    """Delivers an order_b2b message for the Customer: live through the broker when one answers, else simulated."""
    h.open_log(context)
    customer = context.customers.get(customer_name, context.customer)
    h.deliver_message(context, customer['name'], [(product1, qty1), (product2, qty2)])


@when('an inbound order message for an unknown account is delivered to topic order_b2b')
def step_impl(context):
    """Delivers an order_b2b message whose Account matches no Customer (live or simulated)."""
    h.open_log(context)
    h.deliver_message(context, h.unique('Nobody'), [("Widget", 1)])


@when('an inbound order message for an unknown account is delivered live to topic order_b2b')
def step_impl(context):
    """Delivers the unknown-account message LIVE only; skips (not verified) when Kafka is not available."""
    h.open_log(context)
    h.deliver_message(context, h.unique('Nobody'), [("Widget", 1)], mode='live')


@then('the message is processed')
def step_impl(context):
    """The message was saved and parsed: the order exists, no error recorded."""
    assert context.consumed, f'message not processed: error_text={context.error_text}'


@then("the Customer's newest order has {n:d} items totaling {total:d}")
def step_impl(context, n, total):
    """The message created an Order for the Customer, with its Items; the rules derived the total."""
    r = h.requests.get(f'{h.BASE}/api/Order/', params={"filter[customer_id]": context.customer['id'], "sort": "-id",
                       "page[limit]": 1}, headers=h.headers())
    orders = r.json()['data']
    assert orders, 'no order created for the customer'
    context.order_id = int(orders[0]['id'])
    items = h.order_items(context.order_id)
    assert len(items) == n, f'expected {n} items, got {len(items)}'
    actual = float(orders[0]['attributes']['amount_total'] or 0)
    assert abs(actual - total) < 0.01, f'amount_total expected {total}, got {actual}'


@then('the message is rejected with "{text}"')
def step_impl(context, text):
    """The Customer lookup failed: error_text (live) or the endpoint's error (simulated) names it."""
    assert not context.consumed, 'expected the message to be rejected'
    assert context.error_text and text in context.error_text, f'expected "{text}" in the error, got {context.error_text}'


@then('the message row keeps is_processed false and its error_text')
def step_impl(context):
    """Live only: the failed message stays in the blob table, unprocessed, with the reason recorded."""
    assert context.blob_id, 'no message row found'
    r = h.requests.get(f'{h.BASE}/api/OrderB2bMessage/{context.blob_id}/', headers=h.headers())
    a = r.json()['data']['attributes']
    assert not a['is_processed'], f'expected is_processed false: {a}'
    assert a['error_text'], f'expected error_text: {a}'
