from behave import *
import requests

import demo_eai_helpers as h


def list_customers(user):
    r = requests.get(f'{h.API}/Customer/', params={'page[limit]': 200}, headers=h.headers(user))
    assert r.status_code == 200, f'{user}: {r.status_code} {r.text}'
    return {int(each['id']) for each in r.json()['data']}


@given('customers with credit limit 1000, credit limit 3000, and credit limit 1000 with a balance')
def step_impl(context):
    h.open_logic_log(context)
    context.low_id = h.create_customer(h.unique('RLS low'), 1000)
    context.high_id = h.create_customer(h.unique('RLS high'), 3000)
    context.indebted_id = h.create_customer(h.unique('RLS indebted'), 1000)
    order = h.create_order(context.indebted_id)
    assert order.status_code == 201, order.text
    item = h.add_item(int(order.json()['data']['id']), h.product_id('Widget'), 2)    # balance 180
    assert item.status_code == 201, item.text


@when('customers are listed without a token')
def step_impl(context):
    context.security_response = requests.get(f'{h.API}/Customer/')


@when('customers are listed by the sales user')
def step_impl(context):
    context.listed = list_customers('s1')


@when('customers are listed by the admin user')
def step_impl(context):
    context.listed = list_customers('admin')


@when('the credit limit 1000 customer is requested by the sales user')
def step_impl(context):
    context.security_response = h.get('Customer', context.low_id, user='s1')


@when('the credit limit 1000 customer is updated by the sales user')
def step_impl(context):
    context.security_response = h.patch('Customer', context.low_id, {'email': 'x@example.org'}, user='s1')


@then('the security request answers {status:d}')
def step_impl(context, status):
    r = context.security_response
    assert r.status_code == status, f'expected {status}, got {r.status_code}: {r.text}'


@then('the sales list includes the credit limit 3000 customer')
def step_impl(context):
    assert context.high_id in context.listed


@then('the sales list includes the customer with a balance')
def step_impl(context):
    assert context.indebted_id in context.listed


@then('the sales list excludes the credit limit 1000 customer')
def step_impl(context):
    assert context.low_id not in context.listed


@then('the admin list includes the credit limit 1000 customer')
def step_impl(context):
    assert context.low_id in context.listed
