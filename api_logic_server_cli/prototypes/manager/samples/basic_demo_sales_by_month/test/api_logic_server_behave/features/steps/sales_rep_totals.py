"""
Steps for features/sales_rep_totals.feature

Regression coverage for the insert_parent + composite-key LogicBank bug - see
internal_dev/composite_key_issue/composite_key_issue.md (ApiLogicServer-src, v1.2)
for the full investigation. SalesRepTotal(sales_rep_id, year_month) is a composite-
natural-key "bucket" row, auto-created on first reference (Rule.sum/Rule.count with
insert_parent=True) - not pre-seeded. year_month is stamped generically
(Order.CreatedOnYearMonth, from Order.CreatedOn) by
logic/logic_discovery/system/all_classes_stamping.py.

Each scenario uses a freshly-created SalesRep (Rule #0: test repeatability - a shared/
reused rep would accumulate order_count/total_amount across runs, making assertions on
absolute values unreliable).
"""

from behave import *
import requests, json, time
import test_utils
from test_data_helpers import get_or_create_test_customer, get_or_create_test_product

BASE_URL = 'http://localhost:5656'


def create_test_sales_rep(name: str = "Test SalesRep") -> int:
    """ Create a NEW sales rep (always creates, never reuses - see module docstring). """
    unique_name = f"{name} {int(time.time() * 1000)}"
    post_uri = f'{BASE_URL}/api/SalesRep/'
    post_data = {"data": {"attributes": {"name": unique_name}, "type": "SalesRep"}}
    r = requests.post(url=post_uri, json=post_data, headers=test_utils.login())
    result = json.loads(r.text)
    if r.status_code > 300 or 'data' not in result:
        raise Exception(f"Failed to create SalesRep: {r.status_code} - {r.text}")
    return int(result['data']['id'])


def create_test_order_for_sales_rep(customer_id: int, sales_rep_id: int) -> dict:
    """ Create an Order assigned to sales_rep_id; returns its attributes (incl. id). """
    post_uri = f'{BASE_URL}/api/Order/'
    post_data = {
        "data": {
            "attributes": {
                "customer_id": customer_id,
                "sales_rep_id": sales_rep_id,
                "notes": "sales_rep_totals.feature test order",
            },
            "type": "Order",
        }
    }
    r = requests.post(url=post_uri, json=post_data, headers=test_utils.login())
    result = json.loads(r.text)
    if r.status_code > 300 or 'data' not in result:
        raise Exception(f"Failed to create Order: {r.status_code} - {r.text}")
    attrs = result['data']['attributes']
    attrs['id'] = int(result['data']['id'])
    return attrs


def get_sales_rep_total(sales_rep_id: int, year_month: str) -> dict:
    """ Fetch the SalesRepTotal bucket for (sales_rep_id, year_month), or None. """
    get_uri = f'{BASE_URL}/api/SalesRepTotal/'
    params = {"filter[sales_rep_id]": sales_rep_id, "filter[year_month]": year_month}
    r = requests.get(url=get_uri, params=params, headers=test_utils.login())
    if r.status_code > 300:
        raise Exception(f'get_sales_rep_total failed with {r.text}')
    rows = json.loads(r.text)['data']
    assert len(rows) <= 1, \
        f'BUG: {len(rows)} SalesRepTotal rows for sales_rep_id={sales_rep_id}, ' \
        f'year_month={year_month!r} - composite key should be unique'
    return rows[0]['attributes'] if rows else None


@given('A new Sales Rep with no prior orders')
def step_impl(context):
    context.sales_rep_id = create_test_sales_rep()
    context.customer_id = get_or_create_test_customer(name="SalesRepTotals Customer")
    context.product_id = get_or_create_test_product(name="SalesRepTotals Product", unit_price=25.00)


@when('An Order is placed for that Sales Rep')
def step_impl(context):
    context.order = create_test_order_for_sales_rep(context.customer_id, context.sales_rep_id)


@when('A second Order is placed for the same Sales Rep')
def step_impl(context):
    context.order_2 = create_test_order_for_sales_rep(context.customer_id, context.sales_rep_id)


@given('An Order is placed for that Sales Rep')
def step_impl(context):
    context.order = create_test_order_for_sales_rep(context.customer_id, context.sales_rep_id)


@then('A SalesRepTotal bucket is auto-created with order_count {expected_count:d}')
def step_impl(context, expected_count):
    scenario = "First Order for a New Sales Rep"
    test_utils.prt(f'Rules Report', scenario)
    year_month = context.order['CreatedOnYearMonth']
    assert year_month, 'BUG: Order.CreatedOnYearMonth was not stamped'

    bucket = get_sales_rep_total(context.sales_rep_id, year_month)
    assert bucket is not None, \
        f'BUG: no SalesRepTotal bucket for sales_rep_id={context.sales_rep_id}, ' \
        f'year_month={year_month!r} (insert_parent did not fire)'
    assert bucket['order_count'] == expected_count, \
        f'Expected order_count {expected_count}, got {bucket["order_count"]}'


@then('The same SalesRepTotal bucket is adjusted, not recreated, with order_count {expected_count:d}')
def step_impl(context, expected_count):
    scenario = "Second Order for the Same Sales Rep"
    test_utils.prt(f'Rules Report', scenario)
    year_month = context.order['CreatedOnYearMonth']

    bucket = get_sales_rep_total(context.sales_rep_id, year_month)
    assert bucket is not None, \
        f'BUG: no SalesRepTotal bucket for sales_rep_id={context.sales_rep_id}, ' \
        f'year_month={year_month!r}'
    assert bucket['order_count'] == expected_count, \
        f'Expected order_count {expected_count} (bucket should be adjusted, not recreated), ' \
        f'got {bucket["order_count"]}'


@then("The Order's sales_rep_id and CreatedOnYearMonth are not null")
def step_impl(context):
    scenario = "Order Retains its Sales Rep Assignment"
    test_utils.prt(f'Rules Report', scenario)
    assert context.order['sales_rep_id'] == context.sales_rep_id, \
        f'BUG: Order.sales_rep_id was not preserved - expected {context.sales_rep_id}, ' \
        f'got {context.order["sales_rep_id"]!r}'
    assert context.order['CreatedOnYearMonth'], \
        'BUG: Order.CreatedOnYearMonth was not stamped'
