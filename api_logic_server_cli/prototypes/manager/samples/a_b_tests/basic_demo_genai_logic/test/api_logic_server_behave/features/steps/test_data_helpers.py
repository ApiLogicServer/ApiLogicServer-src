"""
Test Data Helpers - Query or Create Test Data

These helpers ensure tests work with any database state by:
1. Querying existing data when available
2. Creating test data programmatically when needed
3. Using correct data types (Integer IDs, not strings)

Usage:
    customer_id = get_or_create_test_customer(balance=0, credit_limit=1000)
    product_id = get_or_create_test_product(unit_price=5.00)
"""

import requests
import json
import test_utils
from decimal import Decimal
import time


def get_or_create_test_customer(name: str = "Test Customer", 
                                balance: float = 0, 
                                credit_limit: float = 1000) -> int:
    """
    Create a NEW test customer (always creates, never reuses).
    
    IMPORTANT: balance is a derived aggregate (sum of unshipped orders).
    - If balance=0: Just create customer (aggregates default to 0)
    - If balance>0: Must be created by caller via orders/items (see note below)
    
    NOTE: This function does NOT create filler orders to reach target balance.
    If you need balance > 0, the caller must create orders/items after getting customer_id.
    
    Returns INTEGER customer ID (not string!)
    
    Args:
        name: Customer name (timestamp added to ensure uniqueness)
        balance: Target balance (for documentation - NOT enforced by this function)
        credit_limit: Credit limit
        
    Returns:
        int: Customer ID (e.g., 1, not 'CUST-1')
    """
    # Always create NEW customer (add timestamp to name for uniqueness)
    unique_name = f"{name} {int(time.time() * 1000)}"  # Add millisecond timestamp
    
    post_uri = 'http://localhost:5656/api/Customer/'
    post_data = {
        "data": {
            "attributes": {
                "name": unique_name,
                # NOTE: Do NOT set balance here - it's a derived aggregate!
                "credit_limit": credit_limit
            },
            "type": "Customer"
        }
    }
    r = requests.post(url=post_uri, json=post_data, headers=test_utils.login())
    result = json.loads(r.text)
    return int(result['data']['id'])  # Convert to int!


def get_or_create_test_product(name: str = "Test Product", 
                               unit_price: float = 5.00) -> int:
    """
    Get or create a test product with specified attributes.
    
    Returns INTEGER product ID (not string!)
    
    Args:
        name: Product name
        unit_price: Unit price
        
    Returns:
        int: Product ID (e.g., 1, not 'PROD-A')
    """
    # Try to find existing product
    get_uri = f'http://localhost:5656/api/Product/?filter[name]={name}'
    r = requests.get(url=get_uri, headers=test_utils.login())
    data = json.loads(r.text)
    
    if data.get('data') and len(data['data']) > 0:
        product_id = int(data['data'][0]['id'])  # Convert to int!
        # Update to ensure correct price
        patch_uri = f'http://localhost:5656/api/Product/{product_id}/'
        patch_data = {
            "data": {
                "attributes": {"unit_price": unit_price},
                "type": "Product",
                "id": product_id
            }
        }
        requests.patch(url=patch_uri, json=patch_data, headers=test_utils.login())
        return product_id
    else:
        # Create new product
        post_uri = 'http://localhost:5656/api/Product/'
        post_data = {
            "data": {
                "attributes": {
                    "name": name,
                    "unit_price": unit_price
                },
                "type": "Product"
            }
        }
        r = requests.post(url=post_uri, json=post_data, headers=test_utils.login())
        result = json.loads(r.text)
        return int(result['data']['id'])  # Convert to int!


def create_test_order(customer_id: int, notes: str = "Test Order") -> int:
    """
    Create a test order (always creates new, doesn't reuse).
    
    Args:
        customer_id: INTEGER customer ID
        notes: Order notes
        
    Returns:
        int: Order ID
    """
    post_uri = 'http://localhost:5656/api/Order/'
    post_data = {
        "data": {
            "attributes": {
                "customer_id": customer_id,  # Integer, not string!
                "notes": notes,
                "date_shipped": None  # Unshipped
            },
            "type": "Order"
        }
    }
    r = requests.post(url=post_uri, json=post_data, headers=test_utils.login())
    result = json.loads(r.text)
    return int(result['data']['id'])  # Convert to int!


def create_test_item(order_id: int, product_id: int, quantity: int = 10) -> int:
    """
    Create a test order item.
    
    Args:
        order_id: INTEGER order ID
        product_id: INTEGER product ID
        quantity: Quantity
        
    Returns:
        int: Item ID
    """
    post_uri = 'http://localhost:5656/api/Item/'
    post_data = {
        "data": {
            "attributes": {
                "order_id": order_id,      # Integer!
                "product_id": product_id,  # Integer!
                "quantity": quantity
            },
            "type": "Item"
        }
    }
    r = requests.post(url=post_uri, json=post_data, headers=test_utils.login())
    result = json.loads(r.text)
    if r.status_code > 300 or 'data' not in result:
        raise Exception(f"Failed to create item: {r.status_code} - {r.text}")
    return int(result['data']['id'])  # Convert to int!


def delete_test_data(customer_id: int = None, order_id: int = None, item_id: int = None):
    """
    Clean up test data (use in teardown or when resetting state).
    
    Args:
        customer_id: Customer to delete
        order_id: Order to delete  
        item_id: Item to delete
    """
    if item_id:
        delete_uri = f'http://localhost:5656/api/Item/{item_id}/'
        requests.delete(url=delete_uri, headers=test_utils.login())
    
    if order_id:
        delete_uri = f'http://localhost:5656/api/Order/{order_id}/'
        requests.delete(url=delete_uri, headers=test_utils.login())
    
    if customer_id:
        delete_uri = f'http://localhost:5656/api/Customer/{customer_id}/'
        requests.delete(url=delete_uri, headers=test_utils.login())


def get_customer(customer_id: int) -> dict:
    """
    Fetch customer data by INTEGER ID.
    
    Args:
        customer_id: INTEGER customer ID (e.g., 1, not 'CUST-1')
        
    Returns:
        dict: Customer attributes (id, name, balance, credit_limit, etc.)
    """
    get_uri = f'http://localhost:5656/api/Customer/{customer_id}/'
    r = requests.get(url=get_uri, headers=test_utils.login())
    if r.status_code > 300:
        raise Exception(f'get_customer failed with {r.text}')
    result_data = json.loads(r.text)
    return result_data['data']['attributes']


def get_order(order_id: int) -> dict:
    """
    Fetch order data by INTEGER ID.
    
    Args:
        order_id: INTEGER order ID
        
    Returns:
        dict: Order attributes
    """
    get_uri = f'http://localhost:5656/api/Order/{order_id}/'
    r = requests.get(url=get_uri, headers=test_utils.login())
    if r.status_code > 300:
        raise Exception(f'get_order failed with {r.text}')
    result_data = json.loads(r.text)
    return result_data['data']['attributes']


def get_item(item_id: int) -> dict:
    """
    Fetch item data by INTEGER ID.
    
    Args:
        item_id: INTEGER item ID
        
    Returns:
        dict: Item attributes
    """
    get_uri = f'http://localhost:5656/api/Item/{item_id}/'
    r = requests.get(url=get_uri, headers=test_utils.login())
    if r.status_code > 300:
        raise Exception(f'get_item failed with {r.text}')
    result_data = json.loads(r.text)
    return result_data['data']['attributes']
