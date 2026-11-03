from behave import *
import requests

import demo_eai_helpers as h


@when('a customer is created with a balance of {balance:d}')
def step_impl(context, balance):
    h.open_logic_log(context)
    context.last_response = h.post('Customer', {'name': h.unique('Derived Test'), 'credit_limit': 1000, 'balance': balance})
    assert context.last_response.status_code == 201, context.last_response.text
    context.new_customer_id = int(context.last_response.json()['data']['id'])


@when('a customer is created with an unknown column')
def step_impl(context):
    h.open_logic_log(context)
    context.last_response = h.post('Customer', {'name': h.unique('Unknown Test'), 'credit_limit': 1000, 'no_such_column': 1})


@when('the customer balance is patched to {balance:d}')
def step_impl(context, balance):
    context.last_response = h.patch('Customer', context.customer_id, {'balance': balance})


@when('the item amount is patched to {amount:d}')
def step_impl(context, amount):
    context.last_response = h.patch('Item', context.item_id, {'amount': amount})


@when('an order is created for customer id {customer_id:d}')
def step_impl(context, customer_id):
    h.open_logic_log(context)
    context.last_response = h.create_order(customer_id)


@when('the unknown table is requested')
def step_impl(context):
    context.last_response = requests.get(f'{h.API}/NoSuchTable/', headers=h.headers())


@then('the new customer balance is {expected:d}')
def step_impl(context, expected):
    actual = float(h.attrs('Customer', context.new_customer_id)['balance'])
    assert abs(actual - expected) < 0.01, f'balance {actual}, expected {expected}'


@then('the request answers {status:d}')
def step_impl(context, status):
    assert context.last_response.status_code == status, f'{context.last_response.status_code}: {context.last_response.text}'
