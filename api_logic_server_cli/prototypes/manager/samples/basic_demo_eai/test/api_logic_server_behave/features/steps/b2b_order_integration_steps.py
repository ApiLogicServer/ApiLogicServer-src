from behave import *
import demo_eai_helpers as h


@when('B2B order placed for "{customer_name}" with {qty1:d} {product1} and {qty2:d} {product2}')
def step_impl(context, customer_name, qty1, product1, qty2, product2):
    """Places a two-Item partner order through the OrderB2B API (multi-item: registered before the single-item step)."""
    h.open_log(context)
    customer = context.customers.get(customer_name, context.customer)
    context.response = h.place_b2b_order(customer['name'], [(product1, qty1), (product2, qty2)])
    context.order_id = None
    if context.response.status_code == 200:
        context.order_id = context.response.json()['meta']['result']['order_id']


@when('B2B order placed for unknown account "{name}"')
def step_impl(context, name):
    """Places a partner order for an account no Customer has (unique name, so no earlier run can match it)."""
    h.open_log(context)
    context.response = h.place_b2b_order(h.unique(name), [("Widget", 1)])


@then('the partner order is accepted with {n:d} items')
def step_impl(context, n):
    """The OrderB2B API answers 200 with the new order id and its item count."""
    r = context.response
    assert r.status_code == 200, f'expected the partner order to be accepted, got {r.status_code}: {r.text}'
    result = r.json()['meta']['result']
    assert result['items_count'] == n, f'expected {n} items, got {result}'


@then('the order is rejected for an unknown customer')
def step_impl(context):
    """The Customer lookup fails: HTTP 400 naming the missing parent."""
    r = context.response
    assert r.status_code == 400, f'expected HTTP 400, got {r.status_code}: {r.text}'
    assert 'missing parent' in r.text and 'Customer' in r.text, f'unknown-customer message missing: {r.text}'


def _newest_request_for(name: str) -> dict:
    """The newest OrderB2bRequest whose payload names the (unique) customer."""
    r = h.requests.get(f'{h.BASE}/api/OrderB2bRequest/', params={"sort": "-id", "page[limit]": 20}, headers=h.headers())
    for each in r.json()['data']:
        if name in (each['attributes'].get('payload') or ''):
            return each['attributes']
    raise AssertionError(f'no request recorded for {name}')


@then('the B2B request is recorded as processed')
def step_impl(context):
    """The request row exists, processed, with no error."""
    a = _newest_request_for(context.customer['name'])
    assert a['is_processed'] and not a['error_text'], f'expected a processed request: {a}'


@then('the B2B request is recorded with the error "{text}"')
def step_impl(context, text):
    """The rejected request is kept, unprocessed, with the reason."""
    assert context.response.status_code == 400, f'expected HTTP 400, got {context.response.status_code}'
    a = _newest_request_for(context.customer['name'])
    assert not a['is_processed'] and a['error_text'] and text in a['error_text'], f'expected error "{text}": {a}'
