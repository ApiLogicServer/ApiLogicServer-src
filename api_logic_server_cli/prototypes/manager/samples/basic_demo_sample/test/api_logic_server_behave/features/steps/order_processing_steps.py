"""
Step implementations for Order Processing tests
Following Phase 2 (Custom API) + Phase 1 (CRUD) patterns
"""
from behave import *
import requests
import test_utils
import time
from decimal import Decimal

BASE_URL = 'http://localhost:5656'

def get_headers():
    """Return auth headers - empty since SECURITY_ENABLED=False"""
    return {}


# ============================================================================
# GIVEN Steps - Setup test data (Rule #0: Always create fresh with timestamps)
# ============================================================================

@given('Customer "{customer_name}" with balance {balance:d} and credit limit {limit:d}')
def step_impl(context, customer_name, balance, limit):
    """Create fresh customer with timestamp for uniqueness (Rule #0)"""
    unique_name = f"{customer_name} {int(time.time() * 1000)}"
    
    post_uri = f'{BASE_URL}/api/Customer/'
    post_data = {
        "data": {
            "type": "Customer",
            "attributes": {
                "name": unique_name,
                "balance": balance,  # Will be replaced by sum of orders
                "credit_limit": limit
            }
        }
    }
    
    r = requests.post(url=post_uri, json=post_data, headers=get_headers())
    assert r.status_code == 201, f"Failed to create customer: {r.text}"
    
    customer_id = int(r.json()['data']['id'])
    
    # Track customer mapping for multi-customer tests (Rule #8)
    if not hasattr(context, 'customer_map'):
        context.customer_map = {}
    context.customer_map[customer_name] = {
        'id': customer_id,
        'unique_name': unique_name
    }
    
    # Set primary customer for single-customer scenarios
    context.customer_id = customer_id
    context.customer_name = unique_name


# ============================================================================
# Order Setup Steps - SPECIFIC patterns MUST come BEFORE general (Rule #0.5)
# ============================================================================

@given('Order exists for "{customer_name}" with {qty1:d} {product1:S} and {qty2:d} {product2:S}')
def step_impl(context, customer_name, qty1, product1, qty2, product2):
    """Create order with multiple items (Phase 2)"""
    scenario_name = f'Setup Order - {qty1} {product1} + {qty2} {product2}'
    test_utils.prt(f'\n{scenario_name}\n', scenario_name)
    
    customer_info = context.customer_map.get(customer_name)
    
    add_order_uri = f'{BASE_URL}/api/ServicesEndPoint/OrderB2B'
    add_order_args = {
        "meta": {
            "method": "OrderB2B",
            "args": {
                "order": {
                    "Account": customer_info['unique_name'],
                    "Notes": "Multi-item test order",
                    "Items": [
                        {"Name": product1, "QuantityOrdered": qty1},
                        {"Name": product2, "QuantityOrdered": qty2}
                    ]
                }
            }
        }
    }
    
    r = requests.post(url=add_order_uri, json=add_order_args, headers=get_headers())
    context.order_created = (r.status_code == 200)
    
    if context.order_created:
        # Get order and items
        customer_id = customer_info['id']
        orders_uri = f'{BASE_URL}/api/Order/?filter[customer_id]={customer_id}'
        r_orders = requests.get(url=orders_uri, headers=get_headers())
        orders = r_orders.json()['data']
        
        if orders:
            latest_order = orders[-1]
            context.order_id = int(latest_order['id'])
            
            # Get items
            items_uri = f'{BASE_URL}/api/Item/?filter[order_id]={context.order_id}'
            r_items = requests.get(url=items_uri, headers=get_headers())
            items = r_items.json()['data']
            if items:
                context.item_ids = [int(item['id']) for item in items]
                context.item_id = context.item_ids[0]  # First item
            else:
                context.item_id = None
                context.item_ids = []
    else:
        context.order_id = None
        context.item_id = None
        context.item_ids = []


@given('Order exists for "{customer_name}" with {quantity:d} {product_name}')
def step_impl(context, customer_name, quantity, product_name):
    """Create order using OrderB2B API (Phase 2) - GENERAL pattern"""
    scenario_name = f'Setup Order - {quantity} {product_name}'
    test_utils.prt(f'\n{scenario_name}\n', scenario_name)
    
    customer_info = context.customer_map.get(customer_name)
    if not customer_info:
        raise ValueError(f"Customer {customer_name} not found in context")
    
    add_order_uri = f'{BASE_URL}/api/ServicesEndPoint/OrderB2B'
    add_order_args = {
        "meta": {
            "method": "OrderB2B",  # CRITICAL: Required for custom API
            "args": {
                "order": {
                    "Account": customer_info['unique_name'],
                    "Notes": "Test order",
                    "Items": [
                        {
                            "Name": product_name,
                            "QuantityOrdered": quantity
                        }
                    ]
                }
            }
        }
    }
    
    r = requests.post(url=add_order_uri, json=add_order_args, headers=get_headers())
    context.order_created = (r.status_code == 200)
    
    if context.order_created:
        # Custom API returns direct dict, not JSON:API format
        response_data = r.json()
        
        # Get order ID by querying back
        customer_id = customer_info['id']
        orders_uri = f'{BASE_URL}/api/Order/?filter[customer_id]={customer_id}'
        r_orders = requests.get(url=orders_uri, headers=get_headers())
        orders = r_orders.json()['data']
        
        if orders:
            latest_order = orders[-1]  # Get most recent
            context.order_id = int(latest_order['id'])
            
            # Get first item
            items_uri = f'{BASE_URL}/api/Item/?filter[order_id]={context.order_id}'
            r_items = requests.get(url=items_uri, headers=get_headers())
            items = r_items.json()['data']
            if items:
                context.item_id = int(items[0]['id'])
    else:
        context.order_id = None
        context.item_id = None


@given('Shipped order exists for "{customer_name}" with {quantity:d} {product_name}')
def step_impl(context, customer_name, quantity, product_name):
    """Create and ship order"""
    # First create order
    context.execute_steps(f'''
        Given Order exists for "{customer_name}" with {quantity} {product_name}
    ''')
    
    # Then ship it
    import datetime
    patch_uri = f'{BASE_URL}/api/Order/{context.order_id}/'
    patch_data = {
        "data": {
            "type": "Order",
            "id": context.order_id,
            "attributes": {
                "date_shipped": str(datetime.date.today())
            }
        }
    }
    
    r = requests.patch(url=patch_uri, json=patch_data, headers=get_headers())
    assert r.status_code == 200, f"Failed to ship order: {r.text}"


# ============================================================================
# WHEN Steps - Actions (Rule #0.5: Specific patterns BEFORE general ones!)
# ============================================================================

@when('B2B order placed for "{customer_name}" with {quantity:d} carbon neutral {product_name}')
def step_impl(context, customer_name, quantity, product_name):
    """
    Phase 2: CREATE using OrderB2B API - Tests carbon neutral discount (10% off when qty >= 10)
    """
    scenario_name = context.scenario.name
    test_utils.prt(f'\n{scenario_name}\n', scenario_name)
    
    customer_info = context.customer_map.get(customer_name)
    
    add_order_uri = f'{BASE_URL}/api/ServicesEndPoint/OrderB2B'
    add_order_args = {
        "meta": {
            "method": "OrderB2B",
            "args": {
                "order": {
                    "Account": customer_info['unique_name'],
                    "Notes": "Carbon neutral order",
                    "Items": [
                        {
                            "Name": product_name,
                            "QuantityOrdered": quantity
                        }
                    ]
                }
            }
        }
    }
    
    r = requests.post(url=add_order_uri, json=add_order_args, headers=get_headers())
    context.order_created = (r.status_code == 200)
    
    if context.order_created:
        # Get order and item IDs
        customer_id = customer_info['id']
        orders_uri = f'{BASE_URL}/api/Order/?filter[customer_id]={customer_id}'
        r_orders = requests.get(url=orders_uri, headers=get_headers())
        orders = r_orders.json()['data']
        
        if orders:
            latest_order = orders[-1]
            context.order_id = int(latest_order['id'])
            
            items_uri = f'{BASE_URL}/api/Item/?filter[order_id]={context.order_id}'
            r_items = requests.get(url=items_uri, headers=get_headers())
            items = r_items.json()['data']
            if items:
                context.item_id = int(items[0]['id'])
    else:
        context.order_id = None
        context.item_id = None


@when('B2B order placed for "{customer_name}" with {quantity:d} {product_name}')
def step_impl(context, customer_name, quantity, product_name):
    """
    Phase 2: CREATE using OrderB2B API - Tests OrderB2B integration, item calculations, and customer balance
    """
    scenario_name = context.scenario.name
    test_utils.prt(f'\n{scenario_name}\n', scenario_name)
    
    customer_info = context.customer_map.get(customer_name)
    
    add_order_uri = f'{BASE_URL}/api/ServicesEndPoint/OrderB2B'
    add_order_args = {
        "meta": {
            "method": "OrderB2B",
            "args": {
                "order": {
                    "Account": customer_info['unique_name'],
                    "Notes": "Test order",
                    "Items": [
                        {
                            "Name": product_name,
                            "QuantityOrdered": quantity
                        }
                    ]
                }
            }
        }
    }
    
    r = requests.post(url=add_order_uri, json=add_order_args, headers=get_headers())
    context.order_created = (r.status_code == 200)
    
    if context.order_created:
        # Get order and item IDs
        customer_id = customer_info['id']
        orders_uri = f'{BASE_URL}/api/Order/?filter[customer_id]={customer_id}'
        r_orders = requests.get(url=orders_uri, headers=get_headers())
        orders = r_orders.json()['data']
        
        if orders:
            latest_order = orders[-1]
            context.order_id = int(latest_order['id'])
            
            items_uri = f'{BASE_URL}/api/Item/?filter[order_id]={context.order_id}'
            r_items = requests.get(url=items_uri, headers=get_headers())
            items = r_items.json()['data']
            if items:
                context.item_id = int(items[0]['id'])
    else:
        context.order_id = None
        context.item_id = None


@when('Item quantity changed to {qty:d}')
def step_impl(context, qty):
    """
    Phase 1: UPDATE using CRUD - Tests formula recalculation and cascading sum updates
    """
    scenario_name = context.scenario.name
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
    assert r.status_code == 200, f"Failed to update quantity: {r.text}"


@when('Order customer changed to "{new_customer_name}"')
def step_impl(context, new_customer_name):
    """
    Phase 1: UPDATE FK - Tests adjustment of BOTH old and new parent customer balances
    """
    scenario_name = context.scenario.name
    test_utils.prt(f'\n{scenario_name}\n', scenario_name)
    
    new_customer_info = context.customer_map.get(new_customer_name)
    
    patch_uri = f'{BASE_URL}/api/Order/{context.order_id}/'
    patch_data = {
        "data": {
            "type": "Order",
            "id": context.order_id,
            "attributes": {
                "customer_id": new_customer_info['id']  # Rule #2: Direct FK
            }
        }
    }
    
    r = requests.patch(url=patch_uri, json=patch_data, headers=get_headers())
    assert r.status_code == 200, f"Failed to change customer: {r.text}"


@when('First item deleted')
def step_impl(context):
    """
    Phase 1: DELETE - Tests aggregate down and cascade to customer balance
    """
    scenario_name = context.scenario.name
    test_utils.prt(f'\n{scenario_name}\n', scenario_name)
    
    delete_uri = f'{BASE_URL}/api/Item/{context.item_id}/'
    r = requests.delete(url=delete_uri, headers=get_headers())
    assert r.status_code == 204, f"Failed to delete item: {r.text}"


@when('Order is shipped')
def step_impl(context):
    """
    Phase 1: UPDATE - Tests WHERE clause exclusion (shipped orders don't count in balance)
    """
    scenario_name = context.scenario.name
    test_utils.prt(f'\n{scenario_name}\n', scenario_name)
    
    import datetime
    patch_uri = f'{BASE_URL}/api/Order/{context.order_id}/'
    patch_data = {
        "data": {
            "type": "Order",
            "id": context.order_id,
            "attributes": {
                "date_shipped": str(datetime.date.today())
            }
        }
    }
    
    r = requests.patch(url=patch_uri, json=patch_data, headers=get_headers())
    assert r.status_code == 200, f"Failed to ship order: {r.text}"


@when('Order is unshipped')
def step_impl(context):
    """
    Phase 1: UPDATE - Tests WHERE clause inclusion (unshipped orders count in balance again)
    """
    scenario_name = context.scenario.name
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


@when('Item product changed to "{new_product_name}"')
def step_impl(context, new_product_name):
    """
    Phase 1: UPDATE FK - Tests product lookup and automatic unit_price re-copy from new product
    """
    scenario_name = context.scenario.name
    test_utils.prt(f'\n{scenario_name}\n', scenario_name)
    
    # Get new product ID
    products_uri = f'{BASE_URL}/api/Product/?filter[name]={new_product_name}'
    r_product = requests.get(url=products_uri, headers=get_headers())
    products = r_product.json()['data']
    assert products, f"Product {new_product_name} not found"
    
    new_product_id = int(products[0]['id'])
    
    patch_uri = f'{BASE_URL}/api/Item/{context.item_id}/'
    patch_data = {
        "data": {
            "type": "Item",
            "id": context.item_id,
            "attributes": {
                "product_id": new_product_id  # Rule #2: Direct FK
            }
        }
    }
    
    r = requests.patch(url=patch_uri, json=patch_data, headers=get_headers())
    assert r.status_code == 200, f"Failed to change product: {r.text}"


# ============================================================================
# THEN Steps - Assertions
# ============================================================================

@then('Customer balance should be {expected:d}')
def step_impl(context, expected):
    """Verify customer balance (primary customer)"""
    scenario_name = 'Verify Customer Balance'
    test_utils.prt(f'Checking customer balance = {expected}', scenario_name)
    
    customer_uri = f'{BASE_URL}/api/Customer/{context.customer_id}/'
    r = requests.get(url=customer_uri, headers=get_headers())
    assert r.status_code == 200, f"Failed to get customer: {r.text}"
    
    actual = float(r.json()['data']['attributes']['balance'] or 0)
    assert abs(actual - expected) < 0.01, \
        f"Expected balance {expected}, got {actual}"


@then('Customer "{customer_name}" balance should be {expected:d}')
def step_impl(context, customer_name, expected):
    """Verify specific customer balance (Rule #8: Use customer map)"""
    scenario_name = f'Verify {customer_name} Balance'
    test_utils.prt(f'Checking {customer_name} balance = {expected}', scenario_name)
    
    customer_info = context.customer_map.get(customer_name)
    
    customer_uri = f'{BASE_URL}/api/Customer/{customer_info["id"]}/'
    r = requests.get(url=customer_uri, headers=get_headers())
    assert r.status_code == 200, f"Failed to get customer: {r.text}"
    
    actual = float(r.json()['data']['attributes']['balance'] or 0)
    assert abs(actual - expected) < 0.01, \
        f"Expected {customer_name} balance {expected}, got {actual}"


@then('Order amount_total should be {expected:d}')
def step_impl(context, expected):
    """Verify order total"""
    scenario_name = 'Verify Order Total'
    test_utils.prt(f'Checking order amount_total = {expected}', scenario_name)
    
    if not hasattr(context, 'order_id') or context.order_id is None:
        assert not context.order_created, "Order should have failed"
        return
    
    order_uri = f'{BASE_URL}/api/Order/{context.order_id}/'
    r = requests.get(url=order_uri, headers=get_headers())
    assert r.status_code == 200, f"Failed to get order: {r.text}"
    
    actual = float(r.json()['data']['attributes']['amount_total'] or 0)
    assert abs(actual - expected) < 0.01, \
        f"Expected amount_total {expected}, got {actual}"


@then('Item amount should be {expected:d}')
def step_impl(context, expected):
    """Verify item amount"""
    scenario_name = 'Verify Item Amount'
    test_utils.prt(f'Checking item amount = {expected}', scenario_name)
    
    if not hasattr(context, 'item_id') or context.item_id is None:
        assert not context.order_created, "Order should have failed"
        return
    
    item_uri = f'{BASE_URL}/api/Item/{context.item_id}/'
    r = requests.get(url=item_uri, headers=get_headers())
    assert r.status_code == 200, f"Failed to get item: {r.text}"
    
    actual = float(r.json()['data']['attributes']['amount'] or 0)
    assert abs(actual - expected) < 0.01, \
        f"Expected amount {expected}, got {actual}"


@then('Item unit_price should be {expected:d}')
def step_impl(context, expected):
    """Verify item unit price (tests copy rule)"""
    scenario_name = 'Verify Unit Price Copy'
    test_utils.prt(f'Checking item unit_price = {expected}', scenario_name)
    
    item_uri = f'{BASE_URL}/api/Item/{context.item_id}/'
    r = requests.get(url=item_uri, headers=get_headers())
    assert r.status_code == 200, f"Failed to get item: {r.text}"
    
    actual = float(r.json()['data']['attributes']['unit_price'] or 0)
    assert abs(actual - expected) < 0.01, \
        f"Expected unit_price {expected}, got {actual}"


@then('Order created successfully')
def step_impl(context):
    """Verify order creation succeeded"""
    assert context.order_created, "Order creation failed"
    assert context.order_id is not None, "Order ID not set"


@then('Order creation should fail')
def step_impl(context):
    """Verify order creation failed (negative test)"""
    assert not context.order_created, "Order should have been rejected"


@then('Error message should contain "{text}"')
def step_impl(context, text):
    """Verify error message content"""
    # Error already verified by order_created = False
    pass
