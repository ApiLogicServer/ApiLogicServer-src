from behave import *
import demo_eai_helpers as h

# Reuses from check_credit_steps.py: Given Customer "{}" with credit limit {}, Given Order is created for ...,
# When Order is shipped, When B2B order placed for ...


@then('Order is published to Kafka topic order_shipping')
def step_impl(context):
    """The logic log of this scenario shows publish_kafka_message for topic order_shipping and this Order's key."""
    log = h.scenario_log(context.scenario.name)
    assert log.is_file(), f'no logic log: {log}'
    text = log.read_text()
    assert "publish_kafka_message: topic='order_shipping'" in text, 'no publish to order_shipping in the logic log'
    assert f"'id': {context.order_id}" in text, f'the publish is not for order {context.order_id}'


@then('no shipping notification is published')
def step_impl(context):
    """An order that is not shipped must not publish."""
    log = h.scenario_log(context.scenario.name)
    text = log.read_text() if log.is_file() else ''
    assert "publish_kafka_message: topic='order_shipping'" not in text, 'published although not shipped'
