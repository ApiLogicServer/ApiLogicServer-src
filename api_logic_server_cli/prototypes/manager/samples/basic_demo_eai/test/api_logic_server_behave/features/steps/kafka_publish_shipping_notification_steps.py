from behave import *
import demo_eai_helpers as h
import test_utils

SERVER_LOG = h.PROJECT_DIR / 'logs' / 'als.log'


@then('the order_shipping message is published with the order id and total')
def step_impl(context):
    """The publish event fired (scenario logic log), and the server log has the by-example message for this order."""
    log = str(h.scenario_log(context.scenario.name))
    assert test_utils.does_file_contain("publish_kafka_message: topic='order_shipping'", log), 'publish event not in the logic log'
    total = float(h.order_attrs(context.order_id)['amount_total'])
    text = SERVER_LOG.read_text(encoding='utf-8')
    assert f'"order_id": {context.order_id},' in text, f'order_shipping message for order {context.order_id} not in logs/als.log'
    assert f'"total": {total}' in text, f'order_shipping message total {total} not in logs/als.log'


@then('no order_shipping message is published')
def step_impl(context):
    """An unshipped order publishes nothing."""
    log = str(h.scenario_log(context.scenario.name))
    assert not test_utils.does_file_contain("publish_kafka_message: topic='order_shipping'", log), 'unexpected publish'
