import json
import time
from pathlib import Path
import requests
from behave import given, when, then
import test_utils
from test_data_helpers import (
    get_or_create_test_customer,
    get_or_create_test_product,
    create_test_order,
    create_test_item,
    get_customer,
    get_order,
    get_item,
)

BASE_URL = "http://localhost:5656"


def _record_delivery_mode(context, body: dict):
    modes_file = Path(__file__).resolve().parents[2] / "logs" / "delivery_modes.json"
    modes = json.loads(modes_file.read_text()) if modes_file.is_file() else {}
    modes[f"{context.feature.name} / {context.scenario.name}"] = {
        "mode": body.get("mode"),
        "broker": body.get("broker"),
    }
    modes_file.parent.mkdir(parents=True, exist_ok=True)
    modes_file.write_text(json.dumps(modes, indent=2))


# ============================================================================
# Feature: Check Credit
# ============================================================================

@given('a customer with credit_limit {credit_limit:d} and balance 0')
def step_given_customer_credit_limit(context, credit_limit):
    test_utils.prt(f"\n{context.scenario.name}\n", context.scenario.name)
    context.customer_id = get_or_create_test_customer(
        name="CheckCredit Cust", credit_limit=float(credit_limit)
    )


@given('a customer with credit_limit {credit_limit:d} and an unshipped order of {qty:d} items at unit_price {price:d}')
def step_given_customer_with_unshipped_order(context, credit_limit, qty, price):
    test_utils.prt(f"\n{context.scenario.name}\n", context.scenario.name)
    context.customer_id = get_or_create_test_customer(
        name="CheckCredit OrderCust", credit_limit=float(credit_limit)
    )
    context.product_id = get_or_create_test_product(
        name=f"Prod_{price}", unit_price=float(price)
    )
    context.order_id = create_test_order(customer_id=context.customer_id)
    context.item_id = create_test_item(
        order_id=context.order_id, product_id=context.product_id, quantity=qty
    )


@given('a customer with credit_limit {credit_limit:d} and a shipped order of {qty:d} items at unit_price {price:d}')
def step_given_customer_with_shipped_order(context, credit_limit, qty, price):
    test_utils.prt(f"\n{context.scenario.name}\n", context.scenario.name)
    context.customer_id = get_or_create_test_customer(
        name="CheckCredit ShippedCust", credit_limit=float(credit_limit)
    )
    context.product_id = get_or_create_test_product(
        name=f"Prod_{price}", unit_price=float(price)
    )
    context.order_id = create_test_order(customer_id=context.customer_id)
    context.item_id = create_test_item(
        order_id=context.order_id, product_id=context.product_id, quantity=qty
    )
    patch_uri = f"{BASE_URL}/api/Order/{context.order_id}/"
    patch_data = {
        "data": {
            "attributes": {"date_shipped": "2026-10-26"},
            "type": "Order",
            "id": context.order_id,
        }
    }
    r = requests.patch(url=patch_uri, json=patch_data, headers=test_utils.login())
    assert r.status_code < 300, f"Failed to ship order in setup: {r.text}"


@given('two customers with credit_limit {credit_limit:d} and an order of 300 on the first customer')
def step_given_two_customers(context, credit_limit):
    test_utils.prt(f"\n{context.scenario.name}\n", context.scenario.name)
    context.first_customer_id = get_or_create_test_customer(
        name="First Cust", credit_limit=float(credit_limit)
    )
    context.second_customer_id = get_or_create_test_customer(
        name="Second Cust", credit_limit=float(credit_limit)
    )
    context.product_id = get_or_create_test_product(name="Prod_150", unit_price=150.0)
    context.order_id = create_test_order(customer_id=context.first_customer_id)
    context.item_id = create_test_item(
        order_id=context.order_id, product_id=context.product_id, quantity=2
    )


@when('an unshipped order is placed with {qty:d} items of unit_price {price:d}')
def step_when_place_unshipped_order(context, qty, price):
    context.product_id = get_or_create_test_product(
        name=f"Prod_{price}", unit_price=float(price)
    )
    context.order_id = create_test_order(customer_id=context.customer_id)
    post_uri = f"{BASE_URL}/api/Item/"
    post_data = {
        "data": {
            "attributes": {
                "order_id": context.order_id,
                "product_id": context.product_id,
                "quantity": qty,
            },
            "type": "Item",
        }
    }
    context.last_response = requests.post(
        url=post_uri, json=post_data, headers=test_utils.login()
    )
    if context.last_response.status_code < 300:
        result = context.last_response.json()
        context.item_id = int(result["data"]["id"])


@when('the item quantity is updated to {new_qty:d}')
def step_when_update_item_qty(context, new_qty):
    patch_uri = f"{BASE_URL}/api/Item/{context.item_id}/"
    patch_data = {
        "data": {
            "attributes": {"quantity": new_qty},
            "type": "Item",
            "id": context.item_id,
        }
    }
    r = requests.patch(url=patch_uri, json=patch_data, headers=test_utils.login())
    assert r.status_code < 300, f"Update item failed: {r.text}"


@when('the order is reassigned to the second customer')
def step_when_reassign_order(context):
    patch_uri = f"{BASE_URL}/api/Order/{context.order_id}/"
    patch_data = {
        "data": {
            "attributes": {"customer_id": context.second_customer_id},
            "type": "Order",
            "id": context.order_id,
        }
    }
    r = requests.patch(url=patch_uri, json=patch_data, headers=test_utils.login())
    assert r.status_code < 300, f"Reassign order failed: {r.text}"


@when('the item is deleted')
def step_when_delete_item(context):
    delete_uri = f"{BASE_URL}/api/Item/{context.item_id}/"
    r = requests.delete(url=delete_uri, headers=test_utils.login())
    assert r.status_code < 300, f"Delete item failed: {r.text}"


@when('the order date_shipped is set to "{date_str}"')
def step_when_set_date_shipped(context, date_str):
    patch_uri = f"{BASE_URL}/api/Order/{context.order_id}/"
    patch_data = {
        "data": {
            "attributes": {"date_shipped": date_str},
            "type": "Order",
            "id": context.order_id,
        }
    }
    r = requests.patch(url=patch_uri, json=patch_data, headers=test_utils.login())
    assert r.status_code < 300, f"Set date_shipped failed: {r.text}"


@when('the order date_shipped is cleared')
def step_when_clear_date_shipped(context):
    patch_uri = f"{BASE_URL}/api/Order/{context.order_id}/"
    patch_data = {
        "data": {
            "attributes": {"date_shipped": None},
            "type": "Order",
            "id": context.order_id,
        }
    }
    r = requests.patch(url=patch_uri, json=patch_data, headers=test_utils.login())
    assert r.status_code < 300, f"Clear date_shipped failed: {r.text}"


@then('the item amount is {expected_amount:d}')
def step_then_item_amount(context, expected_amount):
    item_attrs = get_item(context.item_id)
    actual = float(item_attrs["amount"])
    assert actual == float(expected_amount), f"Expected item amount {expected_amount}, got {actual}"


@then('the order amount_total is {expected_total:d}')
def step_then_order_amount_total(context, expected_total):
    order_attrs = get_order(context.order_id)
    actual = float(order_attrs["amount_total"] or 0)
    assert actual == float(expected_total), f"Expected order amount_total {expected_total}, got {actual}"


@then('the customer balance is {expected_balance:d}')
def step_then_customer_balance(context, expected_balance):
    cust_attrs = get_customer(context.customer_id)
    actual = float(cust_attrs["balance"] or 0)
    assert actual == float(expected_balance), f"Expected customer balance {expected_balance}, got {actual}"


@then('the first customer balance is {expected_balance:d}')
def step_then_first_customer_balance(context, expected_balance):
    cust_attrs = get_customer(context.first_customer_id)
    actual = float(cust_attrs["balance"] or 0)
    assert actual == float(expected_balance), f"Expected first customer balance {expected_balance}, got {actual}"


@then('the second customer balance is {expected_balance:d}')
def step_then_second_customer_balance(context, expected_balance):
    cust_attrs = get_customer(context.second_customer_id)
    actual = float(cust_attrs["balance"] or 0)
    assert actual == float(expected_balance), f"Expected second customer balance {expected_balance}, got {actual}"


@then('the transaction is rejected with credit limit constraint')
def step_then_rejected_credit_limit(context):
    assert context.last_response.status_code >= 400, (
        f"Expected constraint rejection (>=400), got {context.last_response.status_code}: {context.last_response.text}"
    )
    assert "credit limit" in context.last_response.text.lower(), (
        f"Expected 'credit limit' in error response, got: {context.last_response.text}"
    )


# ============================================================================
# Feature: B2B Order Integration (OrderB2B custom endpoint)
# ============================================================================

@given('a B2B customer with credit_limit {credit_limit:d}')
def step_given_b2b_customer(context, credit_limit):
    test_utils.prt(f"\n{context.scenario.name}\n", context.scenario.name)
    get_or_create_test_product(name="Gadget", unit_price=150.0)
    get_or_create_test_product(name="Widget", unit_price=90.0)
    context.b2b_customer_id = get_or_create_test_customer(
        name="B2B Cust", credit_limit=float(credit_limit)
    )
    cust_attrs = get_customer(context.b2b_customer_id)
    context.b2b_customer_name = cust_attrs["name"]
    context.initial_balance = float(cust_attrs["balance"] or 0)


@when('a B2B order payload is posted to OrderB2B for 2 Gadget and 1 Widget')
def step_when_post_order_b2b(context):
    url = f"{BASE_URL}/api/OrderB2B/OrderB2B"
    payload = {
        "meta": {
            "args": {
                "data": {
                    "Account": context.b2b_customer_name,
                    "Notes": "B2B Endpoint Test Order",
                    "Items": [
                        {"Name": "Gadget", "QuantityOrdered": 2},
                        {"Name": "Widget", "QuantityOrdered": 1},
                    ],
                }
            }
        }
    }
    context.b2b_response = requests.post(
        url=url, json=payload, headers=test_utils.login()
    )


@then('the OrderB2B response status is {expected_status:d}')
def step_then_b2b_status(context, expected_status):
    assert context.b2b_response.status_code == expected_status, (
        f"Expected HTTP {expected_status}, got {context.b2b_response.status_code}: {context.b2b_response.text}"
    )


@then('the B2B customer balance increases by {delta:d}')
def step_then_b2b_balance_increases(context, delta):
    cust_attrs = get_customer(context.b2b_customer_id)
    new_balance = float(cust_attrs["balance"] or 0)
    expected = context.initial_balance + float(delta)
    assert new_balance == expected, f"Expected balance {expected}, got {new_balance}"


# ============================================================================
# Feature: Kafka Subscribe Order Integration (order_b2b topic -> OrderB2bMessage)
# ============================================================================

def _get_message_rows():
    r = requests.get(f"{BASE_URL}/api/OrderB2bMessage/", headers=test_utils.login())
    assert r.status_code < 300, f"GET OrderB2bMessage failed: {r.text}"
    return r.json().get("data", [])


def _wait_for_new_message(before_ids: set, timeout_sec: float = 10.0) -> dict:
    deadline = time.time() + timeout_sec
    while time.time() < deadline:
        rows = _get_message_rows()
        for row in rows:
            row_id = int(row["id"])
            attrs = row.get("attributes", {})
            if row_id not in before_ids and attrs.get("is_processed") is not None:
                return row
        time.sleep(0.25)
    raise AssertionError(
        f"Timed out waiting for new OrderB2bMessage (before_ids={before_ids})"
    )


@given('a fresh customer for order_b2b with credit_limit {credit_limit:d}')
def step_given_kafka_customer(context, credit_limit):
    test_utils.prt(f"\n{context.scenario.name}\n", context.scenario.name)
    get_or_create_test_product(name="Gadget", unit_price=150.0)
    get_or_create_test_product(name="Widget", unit_price=90.0)
    context.kafka_customer_id = get_or_create_test_customer(
        name="KafkaB2BCust", credit_limit=float(credit_limit)
    )
    cust_attrs = get_customer(context.kafka_customer_id)
    context.kafka_customer_name = cust_attrs["name"]


@when('a valid order_b2b message is delivered for that customer')
def step_when_deliver_valid_order_b2b(context):
    # Reset topics order_b2b and order_b2b_processed before delivering
    requests.post(f"{BASE_URL}/consume_debug/order_b2b/reset")
    before_ids = {int(r["id"]) for r in _get_message_rows()}
    payload = {
        "Account": context.kafka_customer_name,
        "Notes": "Valid order_b2b via consume_debug -> order_b2b_processed",
        "Items": [
            {"Name": "Gadget", "QuantityOrdered": 2},
            {"Name": "Widget", "QuantityOrdered": 1},
        ],
    }
    project_root = Path(__file__).resolve().parents[4]
    msg_file = project_root / "docs" / "sample_data" / "sample_order_b2b.json"
    msg_file.write_text(json.dumps(payload, indent=2))
    r = requests.get(
        f"{BASE_URL}/consume_debug/order_b2b?file=docs/sample_data/sample_order_b2b.json"
    )
    assert r.status_code == 200, f"consume_debug failed: {r.status_code} {r.text}"
    body = r.json()
    _record_delivery_mode(context, body)
    context.message_row = _wait_for_new_message(before_ids)


@when('an over-limit order_b2b message is delivered via live Kafka for that customer')
def step_when_deliver_over_limit_order_b2b_live(context):
    before_ids = {int(r["id"]) for r in _get_message_rows()}
    payload = {
        "Account": context.kafka_customer_name,
        "Notes": "Over-limit order_b2b via live Kafka -> order_b2b_processed",
        "Items": [
            {"Name": "Gadget", "QuantityOrdered": 2},
            {"Name": "Widget", "QuantityOrdered": 1},
        ],
    }
    project_root = Path(__file__).resolve().parents[4]
    msg_file = project_root / "docs" / "sample_data" / "sample_order_b2b.json"
    msg_file.write_text(json.dumps(payload, indent=2))
    r = requests.get(
        f"{BASE_URL}/consume_debug/order_b2b?file=docs/sample_data/sample_order_b2b.json&mode=live"
    )
    if r.status_code in (409, 503):
        context.scenario.skip(r.json().get("error", "no live Kafka broker"))
        return
    assert r.status_code == 200, f"consume_debug?mode=live failed: {r.status_code} {r.text}"
    body = r.json()
    _record_delivery_mode(context, body)
    context.message_row = _wait_for_new_message(before_ids)


@then('the OrderB2bMessage row is recorded with is_processed True')
def step_then_message_processed_true(context):
    attrs = context.message_row["attributes"]
    assert attrs.get("is_processed") is True, f"Expected is_processed=True, got {attrs}"
    assert not attrs.get("error_text"), f"Expected no error_text, got {attrs.get('error_text')}"


@then('an Order is created for that customer with amount_total {expected_total:d}')
def step_then_order_created_for_kafka_customer(context, expected_total):
    r = requests.get(
        f"{BASE_URL}/api/Order/?filter[customer_id]={context.kafka_customer_id}",
        headers=test_utils.login(),
    )
    assert r.status_code < 300, f"GET Order failed: {r.text}"
    orders = r.json().get("data", [])
    assert len(orders) >= 1, f"Expected at least 1 Order for customer {context.kafka_customer_id}"
    actual_total = float(orders[-1]["attributes"]["amount_total"])
    assert actual_total == float(expected_total), (
        f"Expected Order amount_total {expected_total}, got {actual_total}"
    )


@then('the OrderB2bMessage row is recorded with is_processed False and error_text')
def step_then_message_processed_false(context):
    attrs = context.message_row["attributes"]
    assert attrs.get("is_processed") is False, f"Expected is_processed=False, got {attrs}"
    assert attrs.get("error_text"), f"Expected non-empty error_text, got {attrs}"


# ============================================================================
# Feature: Kafka Publish Shipping Notification (order_shipping topic)
# ============================================================================

@when('the order date_shipped is updated to "{date_str}" to trigger order_shipping')
def step_when_ship_order_for_kafka_publish(context, date_str):
    patch_uri = f"{BASE_URL}/api/Order/{context.order_id}/"
    patch_data = {
        "data": {
            "attributes": {"date_shipped": date_str},
            "type": "Order",
            "id": context.order_id,
        }
    }
    r = requests.patch(url=patch_uri, json=patch_data, headers=test_utils.login())
    assert r.status_code < 300, f"Set date_shipped failed: {r.text}"


@then('the order_shipping message is published with order_id, customer_name, total, and items')
def step_then_order_shipping_published(context):
    cust_attrs = get_customer(context.customer_id)
    assert float(cust_attrs["balance"] or 0) == 0.0, "Expected balance=0 after shipping"
    als_log = Path(__file__).resolve().parents[4] / "logs" / "als.log"
    log_text = als_log.read_text() if als_log.is_file() else ""
    assert "order_shipping" in log_text, "Expected 'order_shipping' topic in logs/als.log"
    assert '"customer_name"' in log_text and '"items"' in log_text, (
        "Expected order_shipping payload keys in logs/als.log"
    )


# ============================================================================
# Feature: Row-Level Security
# ============================================================================

@given('a user logged in with the sales role')
def step_given_sales_user(context):
    test_utils.prt(f"\n{context.scenario.name}\n", context.scenario.name)
    context.sales_headers = test_utils.login(user="s1")


@when('the sales user requests the Customer list')
def step_when_sales_requests_customers(context):
    r = requests.get(f"{BASE_URL}/api/Customer/", headers=context.sales_headers)
    assert r.status_code == 200, f"GET Customer as s1 failed: {r.status_code} {r.text}"
    context.sales_customers = r.json().get("data", [])


@then('every returned customer has credit_limit >= 3000 or balance > 0')
def step_then_sales_customers_filtered(context):
    assert len(context.sales_customers) > 0, "Expected at least one customer visible to sales role"
    for row in context.sales_customers:
        attrs = row["attributes"]
        credit_limit = float(attrs.get("credit_limit") or 0)
        balance = float(attrs.get("balance") or 0)
        assert credit_limit >= 3000 or balance > 0, (
            f"Customer {attrs.get('name')} violates sales grant: credit_limit={credit_limit}, balance={balance}"
        )


@then('customer "{excluded_name}" with balance 0 and credit_limit 1000 is excluded')
def step_then_diana_excluded(context, excluded_name):
    names = [row["attributes"].get("name") for row in context.sales_customers]
    assert excluded_name not in names, (
        f"Expected customer '{excluded_name}' to be excluded by row-level security, but found in {names}"
    )
