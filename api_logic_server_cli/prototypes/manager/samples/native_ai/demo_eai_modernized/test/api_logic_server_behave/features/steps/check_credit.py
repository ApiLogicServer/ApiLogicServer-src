from behave import *
import requests

import demo_eai_helpers as h


@given('a new customer with credit limit {limit:d}')
def step_impl(context, limit):
    h.open_logic_log(context)          # once per scenario, before the first API call
    context.customer_name = h.unique('Credit Test')
    context.customer_id = h.create_customer(context.customer_name, limit)
    context.last_response = None


@given('a second customer with credit limit {limit:d}')
def step_impl(context, limit):
    context.customer2_id = h.create_customer(h.unique('Credit Test 2'), limit)


@given('a new product priced {price:d}')
def step_impl(context, price):
    r = h.post('Product', {'name': h.unique('Test Product'), 'unit_price': price})
    assert r.status_code == 201, r.text
    context.new_product_id = int(r.json()['data']['id'])


@given('an empty order')
def step_impl(context):
    r = h.create_order(context.customer_id)
    assert r.status_code == 201, r.text
    context.order_id = int(r.json()['data']['id'])


def place_order(context, product, qty):
    r = h.create_order(context.customer_id)
    assert r.status_code == 201, r.text
    context.order_id = int(r.json()['data']['id'])
    context.item_id = None
    context.last_response = h.add_item(context.order_id, product, qty)
    if context.last_response.status_code == 201:
        context.item_id = int(context.last_response.json()['data']['id'])


@step('an order is placed with {qty:d} Widget')
def step_impl(context, qty):
    place_order(context, h.product_id('Widget'), qty)


@step('an order is placed with {qty:d} of the new product')
def step_impl(context, qty):
    place_order(context, context.new_product_id, qty)


@when('the item quantity is changed to {qty:d}')
def step_impl(context, qty):
    context.last_response = h.patch('Item', context.item_id, {'quantity': qty})
    assert context.last_response.status_code == 200, context.last_response.text


@step('the order is shipped')
def step_impl(context):
    context.last_response = h.patch('Order', context.order_id, {'date_shipped': '2026-10-27'})
    assert context.last_response.status_code == 200, context.last_response.text


@when('the order is moved to the second customer')
def step_impl(context):
    context.last_response = h.patch('Order', context.order_id, {'customer_id': context.customer2_id})
    assert context.last_response.status_code == 200, context.last_response.text


@when('the credit limit is changed to {limit:d}')
def step_impl(context, limit):
    context.last_response = h.patch('Customer', context.customer_id, {'credit_limit': limit})


@when('the product price is changed to {price:d}')
def step_impl(context, price):
    context.last_response = h.patch('Product', context.new_product_id, {'unit_price': price})
    assert context.last_response.status_code == 200, context.last_response.text


@when('the order is deleted')
def step_impl(context):
    context.last_response = requests.delete(f'{h.API}/Order/{context.order_id}/', headers=h.headers())
    assert context.last_response.status_code == 204, context.last_response.text


@when('an item is added for product id {product:d}')
def step_impl(context, product):
    context.last_response = h.add_item(context.order_id, product, 1)


@then('the item amount is {expected:d}')
def step_impl(context, expected):
    actual = float(h.attrs('Item', context.item_id)['amount'])
    assert abs(actual - expected) < 0.01, f'item amount {actual}, expected {expected}'


@then('the item unit price is {expected:d}')
def step_impl(context, expected):
    actual = float(h.attrs('Item', context.item_id)['unit_price'])
    assert abs(actual - expected) < 0.01, f'item unit_price {actual}, expected {expected}'


@then('the order total is {expected:d}')
def step_impl(context, expected):
    actual = float(h.attrs('Order', context.order_id)['amount_total'])
    assert abs(actual - expected) < 0.01, f'order amount_total {actual}, expected {expected}'


@then('the customer balance is {expected:d}')
def step_impl(context, expected):
    actual = float(h.attrs('Customer', context.customer_id)['balance'])
    assert abs(actual - expected) < 0.01, f'customer balance {actual}, expected {expected}'


@then('the second customer balance is {expected:d}')
def step_impl(context, expected):
    actual = float(h.attrs('Customer', context.customer2_id)['balance'])
    assert abs(actual - expected) < 0.01, f'second customer balance {actual}, expected {expected}'


@then('the request is rejected with "{message}"')
def step_impl(context, message):
    r = context.last_response
    assert r is not None and r.status_code == 400, f'expected 400, got {r.status_code if r is not None else None}'
    assert message in r.text, f'"{message}" not in {r.text}'


@then('the request is accepted')
def step_impl(context):
    assert context.last_response.status_code in (200, 201), context.last_response.text


@then('the order has no items')
def step_impl(context):
    r = requests.get(f'{h.API}/Item/', params={'filter[order_id]': context.order_id}, headers=h.headers())
    assert r.status_code == 200 and r.json()['data'] == [], f'items remain: {r.text}'


@then('Logic adjusts the customer balance from the order total')
def step_impl(context):
    log = h.logic_log_file(context)
    assert "Adjusting customer: balance" in h.logic_log_text(context), f'no balance adjustment in {log}'
