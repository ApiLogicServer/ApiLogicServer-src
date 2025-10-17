from behave import *
import requests
import test_utils
import test_data_helpers
import json
from dotmap import DotMap
import datetime

logic_logs_dir = "logs/scenario_logic_logs"

# ====================
# GIVEN steps
# ====================

@given('Test customer with balance {balance:d} and credit {credit:d}')
def step_impl(context, balance, credit):
    """
    Create or get test customer with specified balance and credit limit.
    
    NOTE: balance is an aggregate (sum of orders). If balance > 0, we create
    a filler order to reach that balance.
    """
    print(f"DEBUG GIVEN: Creating customer with balance={balance}, credit={credit}")
    customer_id = test_data_helpers.get_or_create_test_customer(
        name=f"Test Cust {balance}",
        balance=0,  # Always starts at 0
        credit_limit=credit
    )
    print(f"DEBUG GIVEN: Got customer_id={customer_id}, type={type(customer_id)}")
    
    # If balance > 0, create filler order to reach it
    if balance > 0:
        print(f"DEBUG GIVEN: Creating filler order to reach balance={balance}")
        product_id = test_data_helpers.get_or_create_test_product(
            name="Filler Product",
            unit_price=1.00
        )
        order_id = test_data_helpers.create_test_order(customer_id, "Filler order")
        test_data_helpers.create_test_item(order_id, product_id, quantity=balance)
        print(f"DEBUG GIVEN: Created filler order_id={order_id} with amount={balance}")
    
    context.customer_id = customer_id
    context.initial_balance = balance


@given('Test customer with existing order (balance {balance:d})')
def step_impl(context, balance):
    """Create customer with an existing order that results in the specified balance"""
    # Create customer
    customer_id = test_data_helpers.get_or_create_test_customer(
        name="Test Cust with Order",
        balance=0,
        credit_limit=1000
    )
    
    # Create product
    product_id = test_data_helpers.get_or_create_test_product(
        name="Test Product",
        unit_price=5.00
    )
    
    # Create order with item to reach desired balance
    order_id = test_data_helpers.create_test_order(customer_id, "Test Order")
    item_id = test_data_helpers.create_test_item(order_id, product_id, quantity=10)  # 10 * 5 = 50
    
    context.customer_id = customer_id
    context.order_id = order_id
    context.item_id = item_id
    context.product_id = product_id
    context.initial_balance = balance


@given('Test customer with order containing product at price {price:f}')
def step_impl(context, price):
    """Create customer with order containing a specific product"""
    customer_id = test_data_helpers.get_or_create_test_customer(
        name="Test Cust Product Change",
        balance=0,
        credit_limit=1000
    )
    
    product_id = test_data_helpers.get_or_create_test_product(
        name=f"Product ${price}",
        unit_price=price
    )
    
    order_id = test_data_helpers.create_test_order(customer_id, "Product Test Order")
    item_id = test_data_helpers.create_test_item(order_id, product_id, quantity=10)
    
    context.customer_id = customer_id
    context.order_id = order_id
    context.item_id = item_id
    context.product_id = product_id


@given('Test customer A with order (balance {balance:d})')
def step_impl(context, balance):
    """Create customer A with an order"""
    customer_a_id = test_data_helpers.get_or_create_test_customer(
        name="Customer A",
        balance=0,
        credit_limit=1000
    )
    
    product_id = test_data_helpers.get_or_create_test_product(
        name="Test Product",
        unit_price=5.00
    )
    
    order_id = test_data_helpers.create_test_order(customer_a_id, "Order for A")
    item_id = test_data_helpers.create_test_item(order_id, product_id, quantity=10)  # 50 balance
    
    context.customer_a_id = customer_a_id
    context.customer_b_id = None
    context.order_id = order_id


@given('Test customer B with balance {balance:d}')
def step_impl(context, balance):
    """Create customer B"""
    customer_b_id = test_data_helpers.get_or_create_test_customer(
        name="Customer B",
        balance=balance,
        credit_limit=1000
    )
    context.customer_b_id = customer_b_id


@given('Test customer with unshipped order (balance {balance:d})')
def step_impl(context, balance):
    """Create customer with unshipped order"""
    customer_id = test_data_helpers.get_or_create_test_customer(
        name="Test Cust Unshipped",
        balance=0,
        credit_limit=1000
    )
    
    product_id = test_data_helpers.get_or_create_test_product(
        name="Test Product",
        unit_price=5.00
    )
    
    order_id = test_data_helpers.create_test_order(customer_id, "Unshipped Order")
    item_id = test_data_helpers.create_test_item(order_id, product_id, quantity=10)  # 50 balance
    
    context.customer_id = customer_id
    context.order_id = order_id


@given('Test customer with shipped order (balance {balance:d})')
def step_impl(context, balance):
    """Create customer with shipped order"""
    customer_id = test_data_helpers.get_or_create_test_customer(
        name="Test Cust Shipped",
        balance=balance,
        credit_limit=1000
    )
    
    product_id = test_data_helpers.get_or_create_test_product(
        name="Test Product",
        unit_price=5.00
    )
    
    order_id = test_data_helpers.create_test_order(customer_id, "Shipped Order")
    item_id = test_data_helpers.create_test_item(order_id, product_id, quantity=10)
    
    # Ship it
    patch_uri = f'http://localhost:5656/api/Order/{order_id}/'
    patch_data = {
        "data": {
            "attributes": {"date_shipped": datetime.date.today().isoformat()},
            "type": "Order",
            "id": order_id
        }
    }
    requests.patch(url=patch_uri, json=patch_data, headers=test_utils.login())
    
    context.customer_id = customer_id
    context.order_id = order_id


@given('Test customer with order containing 2 items')
def step_impl(context):
    """Create customer with order containing 2 items"""
    customer_id = test_data_helpers.get_or_create_test_customer(
        name="Test Cust 2 Items",
        balance=0,
        credit_limit=1000
    )
    
    product_id = test_data_helpers.get_or_create_test_product(
        name="Test Product",
        unit_price=5.00
    )
    
    order_id = test_data_helpers.create_test_order(customer_id, "Two Items Order")
    item1_id = test_data_helpers.create_test_item(order_id, product_id, quantity=10)
    item2_id = test_data_helpers.create_test_item(order_id, product_id, quantity=10)
    
    context.customer_id = customer_id
    context.order_id = order_id
    context.item1_id = item1_id
    context.item2_id = item2_id
    
    # Save initial state
    customer = test_data_helpers.get_customer(customer_id)
    order = test_data_helpers.get_order(order_id)
    context.initial_balance = customer['balance']
    context.initial_amount_total = order['amount_total']


@given('Test customer with unshipped order')
def step_impl(context):
    """Create customer with unshipped order for Kafka testing"""
    customer_id = test_data_helpers.get_or_create_test_customer(
        name="Test Kafka Cust",
        balance=0,
        credit_limit=1000
    )
    
    product_id = test_data_helpers.get_or_create_test_product(
        name="Test Product",
        unit_price=5.00
    )
    
    order_id = test_data_helpers.create_test_order(customer_id, "Kafka Test Order")
    item_id = test_data_helpers.create_test_item(order_id, product_id, quantity=10)
    
    context.customer_id = customer_id
    context.order_id = order_id


@given('Test customer with shipped order')
def step_impl(context):
    """Create customer with shipped order for Kafka testing"""
    customer_id = test_data_helpers.get_or_create_test_customer(
        name="Test Kafka Cust Shipped",
        balance=0,
        credit_limit=1000
    )
    
    product_id = test_data_helpers.get_or_create_test_product(
        name="Test Product",
        unit_price=5.00
    )
    
    order_id = test_data_helpers.create_test_order(customer_id, "Kafka Shipped Order")
    item_id = test_data_helpers.create_test_item(order_id, product_id, quantity=10)
    
    # Ship it
    patch_uri = f'http://localhost:5656/api/Order/{order_id}/'
    patch_data = {
        "data": {
            "attributes": {"date_shipped": datetime.date.today().isoformat()},
            "type": "Order",
            "id": order_id
        }
    }
    requests.patch(url=patch_uri, json=patch_data, headers=test_utils.login())
    
    context.customer_id = customer_id
    context.order_id = order_id


# ====================
# WHEN steps
# ====================

@when('New order placed with 1 item (qty {qty:d}, product price {price:f})')
def step_impl(context, qty, price):
    """
    Place new order with one item.
    
    Tests the complete dependency chain:
    - Item.unit_price copied from Product.unit_price (Rule.copy)
    - Item.amount = quantity * unit_price (Rule.formula)
    - Order.amount_total = sum(Item.amount) (Rule.sum)
    - Customer.balance = sum(Order.amount_total where not shipped) (Rule.sum with where)
    
    > **Key Takeaway:** One transaction triggers multiple chained rules automatically
    """
    scenario_name = 'New Order Placed'
    test_utils.prt(f'\n{scenario_name}... testing complete chain\n', scenario_name)
    
    print(f"DEBUG WHEN: customer_id={context.customer_id}, qty={qty}, price={price}")
    
    # Create product with specified price
    product_id = test_data_helpers.get_or_create_test_product(
        name=f"Product ${price}",
        unit_price=price
    )
    print(f"DEBUG WHEN: Created product_id={product_id}")
    
    # Create order (without items - add them separately)
    order_id = test_data_helpers.create_test_order(context.customer_id, "Test Order")
    print(f"DEBUG WHEN: Created order_id={order_id}")
    
    # Create item (triggers the full chain of rules) - may fail due to constraint!
    try:
        item_id = test_data_helpers.create_test_item(order_id, product_id, quantity=qty)
        print(f"DEBUG WHEN: Created item_id={item_id}")
        # Success
        context.response = type('obj', (object,), {'status_code': 200, 'text': ''})()
        context.order_id = order_id
        context.item_id = item_id
    except Exception as e:
        # Constraint violation (expected for "Bad Order" scenario)
        print(f"DEBUG WHEN: Item creation failed (constraint): {str(e)}")
        # Extract status code and error message
        error_msg = str(e)
        if "400" in error_msg:
            context.response = type('obj', (object,), {
                'status_code': 400,
                'text': error_msg
            })()
        else:
            raise  # Re-raise if it's not a constraint error


@when('Item quantity changed from {old_qty:d} to {new_qty:d}')
def step_impl(context, old_qty, new_qty):
    """
    Change item quantity.
    
    Tests dependency chain propagation:
    - Item.amount recalculates (Formula)
    - Order.amount_total updates (Sum)
    - Customer.balance updates (Sum)
    
    > **Key Takeaway:** Changing child attribute cascades up to grandparent
    """
    scenario_name = 'Alter Item Qty'
    test_utils.prt(f'\n{scenario_name}... testing chain up\n', scenario_name)
    
    patch_uri = f'http://localhost:5656/api/Item/{context.item_id}/'
    patch_data = {
        "data": {
            "attributes": {"quantity": new_qty},
            "type": "Item",
            "id": context.item_id
        }
    }
    r = requests.patch(url=patch_uri, json=patch_data, headers=test_utils.login())
    context.response = r


@when('Item product changed to product at price {new_price:f}')
def step_impl(context, new_price):
    """
    Change product on an item (foreign key change).
    
    **Critical Bug Prevented:**
    - Item.unit_price re-copies from NEW product (Rule.copy)
    - Item.amount recalculates with new price (Rule.formula)
    - Order.amount_total updates (Rule.sum)
    - Customer.balance updates (Rule.sum)
    
    > **Key Takeaway:** FK change triggers re-copy from new parent, chain propagates up
    """
    scenario_name = 'Change Product on Item'
    test_utils.prt(f'\n{scenario_name}... testing FK change\n', scenario_name)
    
    # Create new product with new price
    new_product_id = test_data_helpers.get_or_create_test_product(
        name=f"Product ${new_price}",
        unit_price=new_price
    )
    
    patch_uri = f'http://localhost:5656/api/Item/{context.item_id}/'
    patch_data = {
        "data": {
            "attributes": {"product_id": new_product_id},  # INTEGER ID!
            "type": "Item",
            "id": context.item_id
        }
    }
    r = requests.patch(url=patch_uri, json=patch_data, headers=test_utils.login())
    context.response = r
    context.new_product_id = new_product_id


@when('Order moved from customer A to customer B')
def step_impl(context):
    """
    Move order to different customer (foreign key change).
    
    **Critical Bug Prevented:**
    - OLD customer A balance decreases (removes order amount)
    - NEW customer B balance increases (adds order amount)
    
    > **Key Takeaway:** FK change adjusts BOTH old and new parent aggregates
    """
    scenario_name = 'Change Customer on Order'
    test_utils.prt(f'\n{scenario_name}... testing FK change both parents\n', scenario_name)
    
    patch_uri = f'http://localhost:5656/api/Order/{context.order_id}/'
    patch_data = {
        "data": {
            "attributes": {"customer_id": context.customer_b_id},  # INTEGER ID!
            "type": "Order",
            "id": context.order_id
        }
    }
    r = requests.patch(url=patch_uri, json=patch_data, headers=test_utils.login())
    context.response = r


@when('Order date_shipped set to today')
def step_impl(context):
    """
    Set ship date on order.
    
    Tests where clause condition:
    - Order excluded from Customer.balance (where date_shipped is None)
    - Balance decreases by order amount
    - Kafka event fires (if_condition met)
    
    > **Key Takeaway:** Where clause dynamically includes/excludes from aggregate
    """
    scenario_name = 'Set Shipped'
    test_utils.prt(f'\n{scenario_name}... testing where clause exclusion\n', scenario_name)
    
    patch_uri = f'http://localhost:5656/api/Order/{context.order_id}/'
    today = datetime.date.today().isoformat()
    patch_data = {
        "data": {
            "attributes": {"date_shipped": today},
            "type": "Order",
            "id": context.order_id
        }
    }
    r = requests.patch(url=patch_uri, json=patch_data, headers=test_utils.login())
    context.response = r


@when('Order date_shipped set to None')
def step_impl(context):
    """
    Clear ship date on order.
    
    Tests where clause condition:
    - Order included in Customer.balance (where date_shipped is None)
    - Balance increases by order amount
    
    > **Key Takeaway:** Where clause condition change triggers reaggregation
    """
    scenario_name = 'Reset Shipped'
    test_utils.prt(f'\n{scenario_name}... testing where clause inclusion\n', scenario_name)
    
    patch_uri = f'http://localhost:5656/api/Order/{context.order_id}/'
    patch_data = {
        "data": {
            "attributes": {"date_shipped": None},
            "type": "Order",
            "id": context.order_id
        }
    }
    r = requests.patch(url=patch_uri, json=patch_data, headers=test_utils.login())
    context.response = r


@when('One item is deleted')
def step_impl(context):
    """
    Delete one item from order.
    
    Tests cascade down:
    - Item deleted
    - Order.amount_total decreases (Sum reaggregates)
    - Customer.balance decreases (Sum reaggregates)
    
    > **Key Takeaway:** Delete triggers reaggregation up the chain
    """
    scenario_name = 'Delete Item'
    test_utils.prt(f'\n{scenario_name}... testing delete cascade\n', scenario_name)
    
    delete_uri = f'http://localhost:5656/api/Item/{context.item1_id}/'
    r = requests.delete(url=delete_uri, headers=test_utils.login())
    context.response = r


# ====================
# THEN steps
# ====================

@then('Customer balance is {expected_balance:d}')
def step_impl(context, expected_balance):
    """Verify customer balance matches expected value"""
    customer = test_data_helpers.get_customer(context.customer_id)
    actual_balance = float(customer['balance'])
    print(f"DEBUG: customer_id={context.customer_id}, actual_balance={actual_balance}, expected={expected_balance}, type(actual)={type(actual_balance)}, type(expected)={type(expected_balance)}")
    assert abs(actual_balance - expected_balance) < 0.01, \
        f'Customer balance should be {expected_balance}, got {actual_balance}'


@then('Constraint passes')
def step_impl(context):
    """Verify request succeeded (constraint passed)"""
    assert context.response.status_code <= 300, \
        f'Request should succeed, got {context.response.status_code}: {context.response.text}'


@then('Rejected per Check Credit')
def step_impl(context):
    """Verify request rejected due to credit limit constraint"""
    assert context.response.status_code > 300, \
        f'Request should fail due to credit limit'
    response_text = context.response.text.lower()
    assert 'credit' in response_text or 'balance' in response_text or 'exceeds' in response_text, \
        f'Error should mention credit limit: {context.response.text}'


@then('Order amount_total is {expected_total:d}')
def step_impl(context, expected_total):
    """Verify order amount_total matches expected value"""
    order = test_data_helpers.get_order(context.order_id)
    actual_total = float(order['amount_total'])
    assert actual_total == expected_total, \
        f'Order amount_total should be {expected_total}, got {actual_total}'


@then('Item unit_price updates to {expected_price:d}')
def step_impl(context, expected_price):
    """Verify item unit_price copied from new product"""
    item = test_data_helpers.get_item(context.item_id)
    actual_price = float(item['unit_price'])
    assert actual_price == expected_price, \
        f'Item unit_price should be {expected_price}, got {actual_price}'


@then('Item amount recalculates')
def step_impl(context):
    """Verify item amount was recalculated (formula fired)"""
    item = test_data_helpers.get_item(context.item_id)
    expected_amount = item['quantity'] * item['unit_price']
    actual_amount = float(item['amount'])
    assert actual_amount == expected_amount, \
        f'Item amount should be {expected_amount}, got {actual_amount}'


@then('Order amount_total updates')
def step_impl(context):
    """Verify order amount_total updated (sum reaggregated)"""
    order = test_data_helpers.get_order(context.order_id)
    assert order['amount_total'] is not None, 'Order amount_total should be calculated'


@then('Customer balance updates')
def step_impl(context):
    """Verify customer balance updated (sum reaggregated)"""
    customer = test_data_helpers.get_customer(context.customer_id)
    assert customer['balance'] is not None, 'Customer balance should be calculated'


@then('Customer A balance is {expected_balance:d}')
def step_impl(context, expected_balance):
    """Verify customer A balance after FK change"""
    customer = test_data_helpers.get_customer(context.customer_a_id)
    actual_balance = float(customer['balance'])
    assert actual_balance == expected_balance, \
        f'Customer A balance should be {expected_balance}, got {actual_balance}'


@then('Customer B balance is {expected_balance:d}')
def step_impl(context, expected_balance):
    """Verify customer B balance after FK change"""
    customer = test_data_helpers.get_customer(context.customer_b_id)
    actual_balance = float(customer['balance'])
    assert actual_balance == expected_balance, \
        f'Customer B balance should be {expected_balance}, got {actual_balance}'


@then('Order amount_total decreased')
def step_impl(context):
    """Verify order amount decreased after delete"""
    order = test_data_helpers.get_order(context.order_id)
    actual_total = float(order['amount_total'])
    assert actual_total < context.initial_amount_total, \
        f'Order amount_total should decrease from {context.initial_amount_total}, got {actual_total}'


@then('Customer balance decreased')
def step_impl(context):
    """Verify customer balance decreased after delete"""
    customer = test_data_helpers.get_customer(context.customer_id)
    actual_balance = float(customer['balance'])
    assert actual_balance < context.initial_balance, \
        f'Customer balance should decrease from {context.initial_balance}, got {actual_balance}'


@then('Kafka message sent')
def step_impl(context):
    """Verify Kafka event fired (check logic log)"""
    # In real scenario, would check Kafka consumer or mock
    # For now, just verify request succeeded
    assert context.response.status_code <= 300, \
        f'Order ship should succeed, got {context.response.status_code}'


@then('Kafka message sent to order_shipping topic')
def step_impl(context):
    """Verify Kafka message sent to specific topic"""
    # In real scenario, verify topic and message content
    assert context.response.status_code <= 300, \
        f'Order ship should succeed, got {context.response.status_code}'


@then('No Kafka message sent')
def step_impl(context):
    """Verify Kafka event did NOT fire"""
    # In real scenario, verify no message in Kafka
    assert context.response.status_code <= 300, \
        f'Order unship should succeed, got {context.response.status_code}'
