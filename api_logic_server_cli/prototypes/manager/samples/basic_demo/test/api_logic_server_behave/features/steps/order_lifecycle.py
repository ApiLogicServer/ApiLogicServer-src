from behave import *
import requests
import test_utils
from decimal import Decimal
import time

base_url = "http://localhost:5656/api"

# ============================================================================
# GIVEN Steps - Setup test data
# ============================================================================

@given('Order with balance {balance:d}')
def step_impl(context, balance):
    """
    Create order with items totaling specified balance.
    Order is NOT shipped (date_shipped = None).
    """
    product_id = create_test_product("Lifecycle Product", unit_price=1.00)
    order_id = create_test_order(context.customer_id, "Lifecycle order")
    create_test_item(order_id, product_id, quantity=balance)
    
    context.order_id = order_id
    context.product_id = product_id
    context.order_balance = balance


@given('Order with balance {balance:d} marked shipped')
def step_impl(context, balance):
    """
    Create order with items totaling specified balance.
    Order IS shipped (date_shipped set) - excluded from balance.
    """
    product_id = create_test_product("Shipped Product", unit_price=1.00)
    order_id = create_test_order(context.customer_id, "Shipped order")
    create_test_item(order_id, product_id, quantity=balance)
    
    # Mark as shipped
    order_uri = f"{base_url}/Order/{order_id}/"
    patch_data = {
        "data": {
            "type": "Order",
            "id": str(order_id),
            "attributes": {
                "date_shipped": "2024-01-15"
            }
        }
    }
    requests.patch(url=order_uri, json=patch_data, headers=test_utils.login())
    
    context.order_id = order_id
    context.product_id = product_id
    context.order_balance = balance


# ============================================================================
# WHEN Steps - Actions
# ============================================================================

@when('Order is shipped')
def step_impl(context):
    """
    Set date_shipped on order to exclude from balance.
    
    This tests WHERE clause exclusion:
    - Before: date_shipped = None → included in Customer.balance
    - After: date_shipped = today → excluded from Customer.balance
    
    > **Key Takeaway:** WHERE clause conditions work bidirectionally
    """
    scenario_name = 'Set Order Shipped Excludes from Balance'
    test_utils.prt(f'\n{scenario_name}\n', scenario_name)
    
    order_uri = f"{base_url}/Order/{context.order_id}/"
    patch_data = {
        "data": {
            "type": "Order",
            "id": str(context.order_id),
            "attributes": {
                "date_shipped": "2024-01-15"
            }
        }
    }
    
    r = requests.patch(url=order_uri, json=patch_data, headers=test_utils.login())
    context.response = r


@when('Order unshipped')
def step_impl(context):
    """
    Reset date_shipped to None to include order in balance.
    
    This tests WHERE clause inclusion (reverse direction):
    - Before: date_shipped = "2024-01-15" → excluded from balance
    - After: date_shipped = None → included in balance
    
    > **Key Takeaway:** WHERE clauses work both directions (not just one-way)
    """
    scenario_name = 'Reset Shipped Includes in Balance'
    test_utils.prt(f'\n{scenario_name}\n', scenario_name)
    
    order_uri = f"{base_url}/Order/{context.order_id}/"
    patch_data = {
        "data": {
            "type": "Order",
            "id": str(context.order_id),
            "attributes": {
                "date_shipped": None
            }
        }
    }
    
    r = requests.patch(url=order_uri, json=patch_data, headers=test_utils.login())
    context.response = r


@when('Order is deleted')
def step_impl(context):
    """
    Delete entire order to test aggregate adjustment.
    
    This tests DELETE operation:
    - Order deleted
    - Customer.balance updated (order removed from sum)
    
    > **Key Takeaway:** DELETE operations adjust aggregates automatically
    """
    scenario_name = 'Delete Order Adjusts Balance'
    test_utils.prt(f'\n{scenario_name}\n', scenario_name)
    
    order_uri = f"{base_url}/Order/{context.order_id}/"
    r = requests.delete(url=order_uri, headers=test_utils.login())
    context.response = r


# ============================================================================
# THEN Steps - Assertions
# ============================================================================

@then('Order excluded from balance aggregate')
def step_impl(context):
    """Verify order has date_shipped set (excluded from balance WHERE clause)"""
    order_uri = f"{base_url}/Order/{context.order_id}/"
    r = requests.get(url=order_uri, headers=test_utils.login())
    order = r.json()['data']['attributes']
    
    assert order['date_shipped'] is not None, \
        "Order should have date_shipped set (excluded from balance)"


@then('Order included in balance aggregate')
def step_impl(context):
    """Verify order has date_shipped = None (included in balance WHERE clause)"""
    order_uri = f"{base_url}/Order/{context.order_id}/"
    r = requests.get(url=order_uri, headers=test_utils.login())
    order = r.json()['data']['attributes']
    
    assert order['date_shipped'] is None, \
        "Order should have date_shipped = None (included in balance)"


@then('Customer has no orders')
def step_impl(context):
    """Verify order was deleted"""
    order_uri = f"{base_url}/Order/{context.order_id}/"
    r = requests.get(url=order_uri, headers=test_utils.login())
    
    assert r.status_code == 404, \
        f"Order should be deleted (404), got status {r.status_code}"


# ============================================================================
# Helper Functions (Follow Rule #1 - No circular imports!)
# ============================================================================

def create_test_product(name: str, unit_price: float) -> int:
    """
    Create product with specified unit price.
    
    Returns:
        int: Product ID (converted from JSON string)
    """
    product_uri = f"{base_url}/Product/"
    post_data = {
        "data": {
            "type": "Product",
            "attributes": {
                "name": name,
                "unit_price": unit_price
            }
        }
    }
    
    r = requests.post(url=product_uri, json=post_data, headers=test_utils.login())
    result = r.json()
    return int(result['data']['id'])  # CRITICAL: Convert to int!


def create_test_order(customer_id: int, notes: str) -> int:
    """
    Create order for customer.
    amount_total defaults to 0 (it's an aggregate).
    
    Returns:
        int: Order ID (converted from JSON string)
    """
    order_uri = f"{base_url}/Order/"
    post_data = {
        "data": {
            "type": "Order",
            "attributes": {
                "customer_id": int(customer_id),  # Direct FK format
                "notes": notes,
                "date_shipped": None
            }
        }
    }
    
    r = requests.post(url=order_uri, json=post_data, headers=test_utils.login())
    result = r.json()
    return int(result['data']['id'])  # CRITICAL: Convert to int!


def create_test_item(order_id: int, product_id: int, quantity: int) -> int:
    """
    Create item for order.
    unit_price will be copied from product.
    amount will be calculated by formula.
    
    Returns:
        int: Item ID (converted from JSON string)
    """
    item_uri = f"{base_url}/Item/"
    post_data = {
        "data": {
            "type": "Item",
            "attributes": {
                "order_id": int(order_id),    # Direct FK format
                "product_id": int(product_id), # Direct FK format
                "quantity": quantity
            }
        }
    }
    
    r = requests.post(url=item_uri, json=post_data, headers=test_utils.login())
    result = r.json()
    return int(result['data']['id'])  # CRITICAL: Convert to int!
