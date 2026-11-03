import json

from behave import given, then, when

MESSAGES = "docs/requirements/demo_eai/message_formats/"


def call(context, method, url, body=None):
    r = getattr(context.client, method)(url, json=body, headers=context.headers)
    return r, (r.get_json(silent=True) or {})


def customer(context, name):
    return call(context, "get", f"/api/customer?name={name}")[1]["data"][0]


# ---- Check Credit -------------------------------------------------------------------------------------------

@given("a customer with a credit limit")
def _(context):
    context.cust = customer(context, "Bob")  # credit_limit 3000, balance 0
    assert context.cust["credit_limit"] == 3000 and context.cust["balance"] == 0


@when("an order is placed")
def _(context):
    r, order = call(context, "post", "/api/order", {"customer_id": context.cust["id"], "notes": "test"})
    assert r.status_code == 201, order
    context.order_id = order["id"]
    context.products = {p["name"]: p for p in call(context, "get", "/api/product")[1]["data"]}
    for name, qty in (("Widget", 2), ("Gadget", 3)):  # 2*90 + 3*150 = 630
        r, item = call(context, "post", "/api/item", {"order_id": context.order_id,
                                                      "product_id": context.products[name]["id"], "quantity": qty})
        assert r.status_code == 201, item
    context.items = call(context, "get", f"/api/item?order_id={context.order_id}")[1]["data"]


@then("copy the price from the product")
def _(context):
    for item in context.items:
        product = next(p for p in context.products.values() if p["id"] == item["product_id"])
        assert item["unit_price"] == product["unit_price"], item


@then("multiply by quantity to get the item amount")
def _(context):
    assert sorted(i["amount"] for i in context.items) == [180, 450], context.items


@then("sum item amounts to get the order total")
def _(context):
    assert call(context, "get", f"/api/order/{context.order_id}")[1]["amount_total"] == 630


@then("sum unpaid order totals to get the customer balance")
def _(context):
    assert customer(context, "Bob")["balance"] == 630
    # shipping the order makes it paid: it drops out of the balance
    call(context, "patch", f"/api/order/{context.order_id}", {"date_shipped": "2026-10-25"})
    assert customer(context, "Bob")["balance"] == 0
    call(context, "patch", f"/api/order/{context.order_id}", {"date_shipped": None})
    assert customer(context, "Bob")["balance"] == 630


@then("reject if balance exceeds the credit limit")
def _(context):
    r, order = call(context, "post", "/api/order", {"customer_id": context.cust["id"]})
    r, body = call(context, "post", "/api/item", {"order_id": order["id"],
                                                  "product_id": context.products["Thingamajig"]["id"], "quantity": 1})
    assert r.status_code == 400 and "exceeds credit limit" in body["error"], (r.status_code, body)
    assert customer(context, "Bob")["balance"] == 630  # rejected item left no trace
    assert call(context, "get", f"/api/item?order_id={order['id']}")[1]["data"] == []
    # raising a quantity so the total passes the limit is rejected too
    item = context.items[0]
    r, body = call(context, "patch", f"/api/item/{item['id']}", {"quantity": 100})
    assert r.status_code == 400, body


# ---- B2B Order Integration (OrderB2B endpoint) and Kafka Subscribe (consumer parse-and-save) -------------------

def check_alice_order(context, order_id):
    order = call(context, "get", f"/api/order/{order_id}")[1]
    items = call(context, "get", f"/api/item?order_id={order_id}")[1]["data"]
    context.order, context.items = order, items


@given("an inbound B2B order in partner format (message_formats/order_b2b.json)")
def _(context):
    context.partner_msg = json.load(open(MESSAGES + "order_b2b.json"))


@when("the order is received via a Custom API endpoint named OrderB2B")
def _(context):
    r, body = call(context, "post", "/OrderB2B", context.partner_msg)
    assert r.status_code == 201, body
    check_alice_order(context, body["id"])


@given("an inbound order message in JSON format (message_formats/order_b2b.json)")
def _(context):
    context.partner_msg = json.load(open(MESSAGES + "order_b2b.json"))


@when("the message is received from Kafka topic order_b2b")
def _(context):
    # the debug endpoint runs the same parse-and-save function the consumer thread uses
    r, body = call(context, "get", f"/consume_debug/order_b2b?file={MESSAGES}order_b2b.json&mode=simulated")
    assert r.status_code == 200, body
    check_alice_order(context, body["order_id"])


@then("map Account to Customer by name")
def _(context):
    assert context.order["customer_id"] == customer(context, context.partner_msg["Account"])["id"]


@then("map Items.Name to Product by name")
def _(context):
    products = {p["id"]: p["name"] for p in call(context, "get", "/api/product")[1]["data"]}
    assert sorted(products[i["product_id"]] for i in context.items) == sorted(i["Name"] for i in context.partner_msg["Items"])


@then("map Items.QuantityOrdered to Item.quantity")
def _(context):
    products = {p["id"]: p["name"] for p in call(context, "get", "/api/product")[1]["data"]}
    want = {i["Name"]: i["QuantityOrdered"] for i in context.partner_msg["Items"]}
    assert {products[i["product_id"]]: i["quantity"] for i in context.items} == want
    # and the credit logic ran on the mapped order: 1 Widget + 2 Gadgets
    assert context.order["amount_total"] == 390
    # unknown account / product are rejected, not guessed
    bad = dict(context.partner_msg, Account="Nobody")
    assert call(context, "post", "/OrderB2B", bad)[0].status_code == 422
    bad = dict(context.partner_msg, Items=[{"Name": "Nothing", "QuantityOrdered": 1}])
    assert call(context, "post", "/OrderB2B", bad)[0].status_code == 422


# ---- Kafka Publish --------------------------------------------------------------------------------------------

@given("an Order exists")
def _(context):
    context.order_id = 2  # Alice's unshipped order
    order = call(context, "get", f"/api/order/{context.order_id}")[1]
    assert order["date_shipped"] is None


@when("date_shipped is set")
def _(context):
    r, body = call(context, "patch", f"/api/order/{context.order_id}", {"date_shipped": "2026-10-25"})
    assert r.status_code == 200, body
    context.log = call(context, "get", "/kafka_log")[1]


@then("publish to Kafka topic order_shipping")
def _(context):
    assert [m["topic"] for m in context.log] == ["order_shipping"], context.log
    # setting some other attribute afterwards must not publish again
    call(context, "patch", f"/api/order/{context.order_id}", {"notes": "changed"})
    assert len(call(context, "get", "/kafka_log")[1]) == 1


@then("use message_formats/order_shipping.json as the message shape")
def _(context):
    shape = json.load(open(MESSAGES + "order_shipping.json"))
    message = context.log[0]["message"]
    assert message.keys() == shape.keys() and message["items"][0].keys() == shape["items"][0].keys()
    assert message["customer_name"] == "Alice" and message["order_id"] == context.order_id


@then("use by-example publish rather than key-only publish")
def _(context):
    message = context.log[0]["message"]  # a full document, not just {"order_id": n}
    assert message["total"] == 90 and message["items"] == [{"quantity": 1, "product_name": "Widget", "unit_price": 90}]


# ---- Row-Level Security --------------------------------------------------------------------------------------

@given("a user with the sales role")
def _(context):
    context.headers = context.tokens["u1"]  # mapped to the sales role (see security.SALES_USERS)


@when("querying the Customer list")
def _(context):
    r, body = call(context, "get", "/api/customer")
    assert r.status_code == 200
    context.names = {c["name"] for c in body["data"]}
    context.sales_view = body["data"]


@then("only return customers where credit_limit >= 3000 or balance > 0")
def _(context):
    # Alice 5000/90, Bob 3000/0, Charlie 2000/220 qualify; Diana 1000/0 does not; Silent 1000/220 has a balance
    assert context.names == {"Alice", "Bob", "Charlie", "Silent"} and "Diana" not in context.names
    assert all(c["credit_limit"] >= 3000 or c["balance"] > 0 for c in context.sales_view)
    assert call(context, "get", "/api/customer/4")[0].status_code == 404  # not reachable by id either
    context.headers = context.tokens["admin"]  # other roles are unrestricted
    assert len(call(context, "get", "/api/customer")[1]["data"]) == 5
    r = context.client.get("/api/customer")
    assert r.status_code == 401  # and no token, no data
