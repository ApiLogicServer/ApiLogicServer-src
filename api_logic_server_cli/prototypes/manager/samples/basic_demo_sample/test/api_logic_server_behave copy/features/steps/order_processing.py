"""
Order Processing Test Steps

Tests business logic rules:
- Customer.balance = sum(Order.amount_total where date_shipped is null)
- Order.amount_total = sum(Item.amount)
- Item.amount = quantity * unit_price (with carbon neutral discount)
- Item.unit_price copied from Product.unit_price
- Customer.balance <= credit_limit constraint

Uses Phase 2 (OrderB2B custom API) for CREATE operations
Uses Phase 1 (CRUD API) for UPDATE/DELETE operations
"""

from behave import *
import requests
import test_utils
import time
from decimal import Decimal

BASE_URL = 'http://localhost:5656'

# Security is disabled (SECURITY_ENABLED=False in config/default.env)
def get_headers():
    return {}


# ========== GIVEN STEPS ==========

@given('Customer "{customer_name}" with balance {balance:d} and credit limit {limit:d}')
def step_impl(context, customer_name, balance, limit):
    """Create fresh customer with unique name (repeatability!)"""
    # ALWAYS create fresh customer with timestamp - never reuse!
    unique_name = f"{customer_name} {int(time.time() * 1000)}"
    post_uri = f'{BASE_URL}/api/Customer/'
    post_data = {
        "data": {
            "type": "Customer",
            "attributes": {
                "name": unique_name,
                "balance": balance,
                "credit_limit": limit
            }
        }
    }
    r = requests.post(url=post_uri, json=post_data, headers=get_headers())
    assert r.status_code == 201, f"Failed to create customer: {r.text}"
    
    context.customer_id = int(r.json()['data']['id'])
    context.customer_name = unique_name
    # Track name mapping for later lookups
    if not hasattr(context, 'customer_map'):
        context.customer_map = {}
    context.customer_map[customer_name] = {'id': context.customer_id, 'unique_name': unique_name}
    test_utils.prt(f"Created fresh customer: {unique_name} (ID: {context.customer_id})")


@given('Customer "{customer_name}" with existing balance {balance:d}')
def step_impl(context, customer_name, balance):
    """Create fresh customer with specified starting balance"""
    # ALWAYS create fresh - even for "existing balance" scenarios
    unique_name = f"{customer_name} {int(time.time() * 1000)}"
    post_uri = f'{BASE_URL}/api/Customer/'
    post_data = {
        "data": {
            "type": "Customer",
            "attributes": {
                "name": unique_name,
                "balance": balance,
                "credit_limit": 10000  # High limit for "existing balance" tests
            }
        }
    }
    r = requests.post(url=post_uri, json=post_data, headers=get_headers())
    assert r.status_code == 201, f"Failed to create customer: {r.text}"
    
    context.customer_id = int(r.json()['data']['id'])
    context.customer_name = unique_name
    # Track name mapping for later lookups
    if not hasattr(context, 'customer_map'):
        context.customer_map = {}
    context.customer_map[customer_name] = {'id': context.customer_id, 'unique_name': unique_name}
    test_utils.prt(f"Created fresh customer with balance: {unique_name} (ID: {context.customer_id}, Balance: {balance})")


@given('Order exists for "{customer_name}" with {quantity:d} {product_name} quantity {qty:d}')
def step_impl(context, customer_name, quantity, product_name, qty):
    """Create order using OrderB2B API for given customer and product"""
    scenario_name = f'Setup Order for {customer_name}'
    test_utils.prt(f'\n{scenario_name}\n', scenario_name)
    
    # Use OrderB2B API to create order
    add_order_uri = f'{BASE_URL}/api/ServicesEndPoint/OrderB2B'
    items = [{"Name": product_name, "QuantityOrdered": qty} for _ in range(quantity)]
    
    add_order_args = {
        "meta": {
            "method": "OrderB2B",
            "args": {
                "order": {
                    "Account": context.customer_name,  # Use unique name from context!
                    "Notes": "Test order setup",
                    "Items": items
                }
            }
        }
    }
    
    r = requests.post(url=add_order_uri, json=add_order_args, headers=get_headers())
    assert r.status_code == 200, f"Failed to create order: {r.text}"
    
    # Get the created order to extract IDs
    orders_uri = f'{BASE_URL}/api/Order/?filter[customer_id]={context.customer_id}&sort=-id'
    r = requests.get(url=orders_uri, headers=get_headers())
    order_data = r.json()['data'][0]
    
    context.order_id = int(order_data['id'])
    
    # Get the items
    items_uri = f'{BASE_URL}/api/Item/?filter[order_id]={context.order_id}'
    r = requests.get(url=items_uri, headers=get_headers())
    items_data = r.json()['data']
    
    context.item_id = int(items_data[0]['id'])
    if len(items_data) > 1:
        context.item_id_2 = int(items_data[1]['id'])
    
    test_utils.prt(f"Created order {context.order_id} with {len(items_data)} item(s)")


@given('Shipped order exists for "{customer_name}" with {quantity:d} {product_name} quantity {qty:d}')
def step_impl(context, customer_name, quantity, product_name, qty):
    """Create shipped order"""
    # First create the order
    context.execute_steps(f'Given Order exists for "{customer_name}" with {quantity} {product_name} quantity {qty}')
    
    # Then ship it
    patch_uri = f'{BASE_URL}/api/Order/{context.order_id}/'
    patch_data = {
        "data": {
            "type": "Order",
            "id": context.order_id,
            "attributes": {
                "date_shipped": "2025-10-19"
            }
        }
    }
    r = requests.patch(url=patch_uri, json=patch_data, headers=get_headers())
    assert r.status_code == 200, f"Failed to ship order: {r.text}"
    test_utils.prt(f"Order {context.order_id} shipped")


@given('Product "{product_name}" is carbon neutral')
def step_impl(context, product_name):
    """Set product as carbon neutral"""
    # Get product
    get_uri = f'{BASE_URL}/api/Product/?filter[name]={product_name}'
    r = requests.get(url=get_uri, headers=get_headers())
    product_data = r.json()['data'][0]
    product_id = int(product_data['id'])
    
    # Update carbon_neutral flag
    patch_uri = f'{BASE_URL}/api/Product/{product_id}/'
    patch_data = {
        "data": {
            "type": "Product",
            "id": product_id,
            "attributes": {
                "carbon_neutral": True
            }
        }
    }
    r = requests.patch(url=patch_uri, json=patch_data, headers=get_headers())
    assert r.status_code == 200
    test_utils.prt(f"Product {product_name} set as carbon neutral")


# ========== WHEN STEPS ==========

@when('B2B order placed for "{customer_name}" with {quantity:d} carbon neutral {product_name}')
def step_impl(context, customer_name, quantity, product_name):
    """Phase 2: Create order using OrderB2B custom API with carbon neutral product"""
    scenario_name = f'B2B Carbon Neutral Order for {customer_name}'
    test_utils.prt(f'\n{scenario_name}\n', scenario_name)
    
    add_order_uri = f'{BASE_URL}/api/ServicesEndPoint/OrderB2B'
    add_order_args = {
        "meta": {
            "method": "OrderB2B",
            "args": {
                "order": {
                    "Account": context.customer_name,  # Use unique name from context!
                    "Notes": "Test B2B carbon neutral order",
                    "Items": [
                        {"Name": product_name, "QuantityOrdered": quantity}
                    ]
                }
            }
        }
    }
    
    r = requests.post(url=add_order_uri, json=add_order_args, headers=get_headers())
    context.response_status = r.status_code
    context.order_created = (r.status_code == 200)
    
    if context.order_created:
        # Get the created order
        orders_uri = f'{BASE_URL}/api/Order/?filter[customer_id]={context.customer_id}&sort=-id'
        r = requests.get(url=orders_uri, headers=get_headers())
        if r.json()['data']:
            order_data = r.json()['data'][0]
            context.order_id = int(order_data['id'])
            
            # Get items
            items_uri = f'{BASE_URL}/api/Item/?filter[order_id]={context.order_id}'
            r = requests.get(url=items_uri, headers=get_headers())
            if r.json()['data']:
                context.item_id = int(r.json()['data'][0]['id'])
        test_utils.prt(f"Order created: {context.order_id}, Item: {context.item_id}")
    else:
        context.order_id = None
        context.item_id = None
        context.error_response = r.json() if r.text else {}
        test_utils.prt(f"Order creation failed: {r.status_code}")


@when('B2B order placed for "{customer_name}" with {quantity:d} {product_name}')
def step_impl(context, customer_name, quantity, product_name):
    """Phase 2: Create order using OrderB2B custom API"""
    scenario_name = f'B2B Order for {customer_name}'
    test_utils.prt(f'\n{scenario_name}\n', scenario_name)
    
    add_order_uri = f'{BASE_URL}/api/ServicesEndPoint/OrderB2B'
    add_order_args = {
        "meta": {
            "method": "OrderB2B",
            "args": {
                "order": {
                    "Account": context.customer_name,  # Use unique name from context!
                    "Notes": "Test B2B order",
                    "Items": [
                        {"Name": product_name, "QuantityOrdered": quantity}
                    ]
                }
            }
        }
    }
    
    r = requests.post(url=add_order_uri, json=add_order_args, headers=get_headers())
    context.response_status = r.status_code
    context.order_created = (r.status_code == 200)
    
    if context.order_created:
        # Get the created order
        orders_uri = f'{BASE_URL}/api/Order/?filter[customer_id]={context.customer_id}&sort=-id'
        r = requests.get(url=orders_uri, headers=get_headers())
        if r.json()['data']:
            order_data = r.json()['data'][0]
            context.order_id = int(order_data['id'])
            
            # Get items
            items_uri = f'{BASE_URL}/api/Item/?filter[order_id]={context.order_id}'
            r = requests.get(url=items_uri, headers=get_headers())
            if r.json()['data']:
                context.item_id = int(r.json()['data'][0]['id'])
        test_utils.prt(f"Order created: {context.order_id}")
    else:
        context.order_id = None
        context.item_id = None
        context.error_response = r.json() if r.text else {}
        test_utils.prt(f"Order creation failed: {r.status_code}")


@when('B2B order placed for "{customer_name}" with multiple items')
def step_impl(context, customer_name):
    """Phase 2: Create order with multiple items using table"""
    scenario_name = f'Multi-Item B2B Order for {customer_name}'
    test_utils.prt(f'\n{scenario_name}\n', scenario_name)
    
    items = [{"Name": row['Product'], "QuantityOrdered": int(row['Quantity'])} 
             for row in context.table]
    
    add_order_uri = f'{BASE_URL}/api/ServicesEndPoint/OrderB2B'
    add_order_args = {
        "meta": {
            "method": "OrderB2B",
            "args": {
                "order": {
                    "Account": context.customer_name,  # Use unique name from context!
                    "Notes": "Multi-item test order",
                    "Items": items
                }
            }
        }
    }
    
    r = requests.post(url=add_order_uri, json=add_order_args, headers=get_headers())
    context.response_status = r.status_code
    context.order_created = (r.status_code == 200)
    
    if context.order_created:
        # Get the created order
        orders_uri = f'{BASE_URL}/api/Order/?filter[customer_id]={context.customer_id}&sort=-id'
        r = requests.get(url=orders_uri, headers=get_headers())
        order_data = r.json()['data'][0]
        context.order_id = int(order_data['id'])
        test_utils.prt(f"Multi-item order created: {context.order_id}")
    else:
        context.order_id = None


@when('Item quantity changed to {qty:d}')
def step_impl(context, qty):
    """Phase 1: Update item quantity using CRUD API"""
    scenario_name = 'Item Quantity Update'
    test_utils.prt(f'\n{scenario_name}\n', scenario_name)
    
    patch_uri = f'{BASE_URL}/api/Item/{context.item_id}/'
    patch_data = {
        "data": {
            "type": "Item",
            "id": context.item_id,
            "attributes": {
                "quantity": qty
            }
        }
    }
    
    r = requests.patch(url=patch_uri, json=patch_data, headers=get_headers())
    assert r.status_code == 200, f"Failed to update item quantity: {r.text}"
    test_utils.prt(f"Item {context.item_id} quantity changed to {qty}")


@when('Second item is deleted')
def step_impl(context):
    """Phase 1: Delete item using CRUD API"""
    scenario_name = 'Delete Item'
    test_utils.prt(f'\n{scenario_name}\n', scenario_name)
    
    delete_uri = f'{BASE_URL}/api/Item/{context.item_id_2}/'
    r = requests.delete(url=delete_uri, headers=get_headers())
    assert r.status_code == 204, f"Failed to delete item: {r.text}"
    test_utils.prt(f"Item {context.item_id_2} deleted")


@when('Item product changed from {old_product} to {new_product}')
def step_impl(context, old_product, new_product):
    """Phase 1: Change item's product (FK change)"""
    scenario_name = 'Item Product Change'
    test_utils.prt(f'\n{scenario_name}\n', scenario_name)
    
    # Get new product ID
    get_uri = f'{BASE_URL}/api/Product/?filter[name]={new_product}'
    r = requests.get(url=get_uri, headers=get_headers())
    new_product_id = int(r.json()['data'][0]['id'])
    
    # Update item's product_id
    patch_uri = f'{BASE_URL}/api/Item/{context.item_id}/'
    patch_data = {
        "data": {
            "type": "Item",
            "id": context.item_id,
            "attributes": {
                "product_id": new_product_id
            }
        }
    }
    
    r = requests.patch(url=patch_uri, json=patch_data, headers=get_headers())
    assert r.status_code == 200, f"Failed to change product: {r.text}"
    test_utils.prt(f"Item {context.item_id} product changed to {new_product} (ID: {new_product_id})")


@when('Order customer changed from "{old_customer}" to "{new_customer}"')
def step_impl(context, old_customer, new_customer):
    """Phase 1: Change order's customer (FK change - tests both parents adjust)"""
    scenario_name = 'Order Customer Change'
    test_utils.prt(f'\n{scenario_name}\n', scenario_name)
    
    # Get new customer ID from mapping
    new_customer_info = context.customer_map.get(new_customer)
    assert new_customer_info is not None, f"Customer {new_customer} not found in context"
    new_customer_id = new_customer_info['id']
    context.new_customer_id = new_customer_id
    
    # Update order's customer_id
    patch_uri = f'{BASE_URL}/api/Order/{context.order_id}/'
    patch_data = {
        "data": {
            "type": "Order",
            "id": context.order_id,
            "attributes": {
                "customer_id": new_customer_id
            }
        }
    }
    
    r = requests.patch(url=patch_uri, json=patch_data, headers=get_headers())
    assert r.status_code == 200, f"Failed to change customer: {r.text}"
    test_utils.prt(f"Order {context.order_id} customer changed to {new_customer} (ID: {new_customer_id})")


@when('Order is shipped')
def step_impl(context):
    """Phase 1: Ship order (WHERE clause - exclude from balance)"""
    scenario_name = 'Ship Order'
    test_utils.prt(f'\n{scenario_name}\n', scenario_name)
    
    patch_uri = f'{BASE_URL}/api/Order/{context.order_id}/'
    patch_data = {
        "data": {
            "type": "Order",
            "id": context.order_id,
            "attributes": {
                "date_shipped": "2025-10-19"
            }
        }
    }
    
    r = requests.patch(url=patch_uri, json=patch_data, headers=get_headers())
    assert r.status_code == 200, f"Failed to ship order: {r.text}"
    test_utils.prt(f"Order {context.order_id} shipped")


@when('Order is unshipped')
def step_impl(context):
    """Phase 1: Unship order (WHERE clause - include in balance)"""
    scenario_name = 'Unship Order'
    test_utils.prt(f'\n{scenario_name}\n', scenario_name)
    
    patch_uri = f'{BASE_URL}/api/Order/{context.order_id}/'
    patch_data = {
        "data": {
            "type": "Order",
            "id": context.order_id,
            "attributes": {
                "date_shipped": None
            }
        }
    }
    
    r = requests.patch(url=patch_uri, json=patch_data, headers=get_headers())
    assert r.status_code == 200, f"Failed to unship order: {r.text}"
    test_utils.prt(f"Order {context.order_id} unshipped")


# ========== THEN STEPS ==========

@then('Order created successfully')
def step_impl(context):
    """Verify order creation succeeded"""
    assert context.order_created, f"Order creation failed with status {context.response_status}"
    assert hasattr(context, 'order_id') and context.order_id is not None, "Order ID not set"


@then('Order should be rejected')
def step_impl(context):
    """Verify order creation failed (constraint violation)"""
    assert not context.order_created, f"Order should have been rejected but was created with status {context.response_status}"


@then('Error message should contain "{text}"')
def step_impl(context, text):
    """Verify error message contains expected text"""
    if hasattr(context, 'error_response'):
        error_str = str(context.error_response).lower()
        assert text.lower() in error_str, f"Expected '{text}' in error message, got: {context.error_response}"


@then('Customer balance should be {expected:d}')
def step_impl(context, expected):
    """Verify customer balance matches expected value"""
    get_uri = f'{BASE_URL}/api/Customer/{context.customer_id}/'
    r = requests.get(url=get_uri, headers=get_headers())
    actual = float(r.json()['data']['attributes']['balance'])
    assert abs(actual - expected) < 0.01, f"Expected balance {expected}, got {actual}"
    test_utils.prt(f"✓ Customer balance verified: {actual}")


@then('Customer "{customer_name}" balance should be {expected:d}')
def step_impl(context, customer_name, expected):
    """Verify specific customer's balance"""
    # Get customer by ID from name mapping
    customer_info = context.customer_map.get(customer_name)
    assert customer_info is not None, f"Customer {customer_name} not found in context"
    
    get_uri = f'{BASE_URL}/api/Customer/{customer_info["id"]}/'
    r = requests.get(url=get_uri, headers=get_headers())
    actual = float(r.json()['data']['attributes']['balance'])
    assert abs(actual - expected) < 0.01, f"Expected {customer_name} balance {expected}, got {actual}"
    test_utils.prt(f"✓ Customer {customer_name} balance verified: {actual}")


@then('Order amount_total should be {expected:d}')
def step_impl(context, expected):
    """Verify order amount_total matches expected value"""
    get_uri = f'{BASE_URL}/api/Order/{context.order_id}/'
    r = requests.get(url=get_uri, headers=get_headers())
    actual = float(r.json()['data']['attributes']['amount_total'])
    assert abs(actual - expected) < 0.01, f"Expected amount_total {expected}, got {actual}"
    test_utils.prt(f"✓ Order amount_total verified: {actual}")


@then('Item amount should be {expected:d}')
def step_impl(context, expected):
    """Verify item amount matches expected value"""
    assert hasattr(context, 'item_id') and context.item_id is not None, "item_id not set in context"
    get_uri = f'{BASE_URL}/api/Item/{context.item_id}/'
    r = requests.get(url=get_uri, headers=get_headers())
    response_data = r.json()
    assert 'data' in response_data, f"No 'data' in response: {response_data}"
    actual = float(response_data['data']['attributes']['amount'])
    assert abs(actual - expected) < 0.01, f"Expected amount {expected}, got {actual}"
    test_utils.prt(f"✓ Item amount verified: {actual}")


@then('Item unit_price should be {expected:d}')
def step_impl(context, expected):
    """Verify item unit_price matches expected value"""
    get_uri = f'{BASE_URL}/api/Item/{context.item_id}/'
    r = requests.get(url=get_uri, headers=get_headers())
    actual = float(r.json()['data']['attributes']['unit_price'])
    assert abs(actual - expected) < 0.01, f"Expected unit_price {expected}, got {actual}"
    test_utils.prt(f"✓ Item unit_price verified: {actual}")


@then('Order should have {count:d} items')
def step_impl(context, count):
    """Verify order has expected number of items"""
    get_uri = f'{BASE_URL}/api/Item/?filter[order_id]={context.order_id}'
    r = requests.get(url=get_uri, headers=get_headers())
    actual_count = len(r.json()['data'])
    assert actual_count == count, f"Expected {count} items, got {actual_count}"
    test_utils.prt(f"✓ Order has {actual_count} items")
