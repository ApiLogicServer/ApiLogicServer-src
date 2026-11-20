import datetime
from behave import *
import demo_eai_helpers as h

TODAY = datetime.date.today().isoformat()
YESTERDAY = (datetime.date.today() - datetime.timedelta(days=1)).isoformat()


def _daily() -> dict:
    """The rule-maintained daily totals (last 30 days, zero-filled)."""
    r = h.requests.get(f'{h.BASE}/order_flow/daily')
    assert r.status_code == 200, f'daily totals failed: {r.status_code} {r.text}'
    return r.json()


def _on(data: dict, day: str, figure: str) -> float:
    return data[figure][data['days'].index(day)] if day in data['days'] else 0


@given('the daily totals are read')
def step_impl(context):
    """Reads the daily totals before the change (and opens the scenario's logic log)."""
    h.open_log(context)
    context.before = _daily()


@then('the Order is dated today')
def step_impl(context):
    """Stamping set CreatedOn and the day key when the Order was placed."""
    a = h.order_attrs(context.order_id)
    assert a['CreatedOn'] == TODAY and a['CreatedOnDay'] == TODAY, f'expected {TODAY}: {a}'


@when('an Order dated {date} is created for "{customer_name}" through the API')
def step_impl(context, date, customer_name):
    """POSTs an Order that already carries a date."""
    customer = context.customers.get(customer_name, context.customer)
    body = {"data": {"type": "Order", "attributes": {"customer_id": customer['id'], "notes": "behave dated", "CreatedOn": date}}}
    r = h.requests.post(f'{h.BASE}/api/Order/', json=body, headers=h.headers())
    assert r.status_code < 300, f'order create failed: {r.status_code} {r.text}'
    context.order_id = int(r.json()['data']['id'])


@then('the Order keeps its date {date}')
def step_impl(context, date):
    """Stamping keeps a supplied CreatedOn, and derives the day key from it."""
    a = h.order_attrs(context.order_id)
    assert a['CreatedOn'] == date and a['CreatedOnDay'] == date, f'expected {date}: {a}'


@when('the Order is moved to yesterday')
def step_impl(context):
    """PATCHes the Order's day key: the OLD and the NEW day totals both adjust."""
    body = {"data": {"type": "Order", "id": str(context.order_id), "attributes": {"CreatedOnDay": YESTERDAY}}}
    r = h.requests.patch(f'{h.BASE}/api/Order/{context.order_id}/', json=body, headers=h.headers())
    assert r.status_code == 200, f'move failed: {r.status_code} {r.text}'


@then("today's order_count rises by {count:d} and order_amount by {amount:d}")
def step_impl(context, count, amount):
    """Today's order totals changed by exactly the order's count and amount."""
    after = _daily()
    for figure, delta in (('order_count', count), ('order_amount', amount)):
        change = _on(after, TODAY, figure) - _on(context.before, TODAY, figure)
        assert abs(change - delta) < 0.01, f'{figure}: expected {delta:+}, got {change:+}'


@then("yesterday's order_count rises by {count:d}")
def step_impl(context, count):
    """The moved order now counts on yesterday."""
    change = _on(_daily(), YESTERDAY, 'order_count') - _on(context.before, YESTERDAY, 'order_count')
    assert change == count, f"yesterday's order_count: expected {count:+}, got {change:+}"


@then("today's {figure1} and {figure2} rise by 1")
def step_impl(context, figure1, figure2):
    """Two of today's message / request figures each rose by one."""
    after = _daily()
    for figure in (figure1, figure2):
        change = _on(after, TODAY, figure) - _on(context.before, TODAY, figure)
        assert change == 1, f'{figure}: expected +1, got {change:+} (before {context.before[figure][-1]}, after {after[figure][-1]})'


@then("today's message_stuck is unchanged")
def step_impl(context):
    """A processed message is not left stuck."""
    assert _on(_daily(), TODAY, 'message_stuck') == _on(context.before, TODAY, 'message_stuck'), 'stuck count changed'


@then('the dashboard shows the three charts with today')
def step_impl(context):
    """The dashboard frames the three charts; each renders current data that includes today."""
    page = h.requests.get(f'{h.BASE}/dashboard').text
    for name in ('orders_per_day', 'messages_per_day', 'requests_per_day'):
        assert f'chart_graphics/{name}' in page, f'{name} not on the dashboard'
        chart = h.requests.get(f'{h.BASE}/chart_graphics/{name}')
        assert chart.status_code == 200 and 'new Chart' in chart.text and TODAY in chart.text, f'{name} did not render today'
