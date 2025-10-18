from behave import *
import requests
import test_utils
from decimal import Decimal
import time

base_url = "http://localhost:5656/api"

# ============================================================================
# GIVEN Steps - Setup test data
# ============================================================================

@given('Customer with balance {balance:d} and credit {credit:d}')
def step_impl(context, balance, credit):
    """
    Create customer with specified balance and credit limit.
    Balance is an aggregate - must create orders to reach it.
    """
    # Step 1: Create customer (balance defaults to 0)
    customer_name = f"Test Customer {int(time.time() * 1000)}"
    customer_id = create_test_customer(customer_name, credit)
    
    # Step 2: If balance > 0, create filler order to reach it
    if balance > 0:
        product_id = create_test_product("Filler Product", unit_price=1.00)
        order_id = create_test_order(customer_id, "Filler order")
        create_test_item(order_id, product_id, quantity=balance)
        # Now customer.balance = balance (computed by rules)
    
    context.customer_id = customer_id
    context.initial_balance = balance
    context.credit_limit = credit


@given('Order with 1 item quantity {quantity:d}')
def step_impl(context, quantity):
    """
    Create order with single item at specified quantity.
    """
    product_id = create_test_product("Test Product", unit_price=5.00)
    order_id = create_test_order(context.customer_id, "Test order")
    item_id = create_test_item(order_id, product_id, quantity)
    
    context.product_id = product_id
    context.order_id = order_id
    context.item_id = item_id
    context.original_quantity = quantity


@given('Two customers with balance 0')
def step_impl(context):
    """
    Create two customers for testing order transfers.
    """
    customer1_name = f"Test Customer 1 {int(time.time() * 1000)}"
    customer2_name = f"Test Customer 2 {int(time.time() * 1000)}"
    
    context.customer1_id = create_test_customer(customer1_name, 1000)
    context.customer2_id = create_test_customer(customer2_name, 1000)


@given('Order for first customer with balance {balance:d}')
def step_impl(context, balance):
    """
    Create order for first customer reaching specified balance.
    """
    product_id = create_test_product("Transfer Product", unit_price=1.00)
    order_id = create_test_order(context.customer1_id, "Order to transfer")
    create_test_item(order_id, product_id, quantity=balance)
    
    context.order_id = order_id
    context.transfer_balance = balance


@given('Order with 2 items')
def step_impl(context):
    """
    Create order with two items for delete testing.
    """
    product1_id = create_test_product("Product 1", unit_price=10.00)
    product2_id = create_test_product("Product 2", unit_price=20.00)
    order_id = create_test_order(context.customer_id, "Order with 2 items")
    
    item1_id = create_test_item(order_id, product1_id, quantity=5)  # 50
    item2_id = create_test_item(order_id, product2_id, quantity=3)  # 60
    
    context.order_id = order_id
    context.item1_id = item1_id
    context.item2_id = item2_id
    context.expected_balance_after_delete = Decimal('60')  # After deleting item1


# ============================================================================
# WHEN Steps - Actions
# ============================================================================

@when('Good Order Placed')
def step_impl(context):
    """
    Place an order with quantity that fits within credit limit.
    
    This tests the complete dependency chain:
    - Item.unit_price copied from Product.unit_price (Rule.copy)
    - Item.amount = quantity * unit_price (Rule.formula)
    - Order.amount_total = Sum(Item.amount) (Rule.sum)
    - Customer.balance = Sum(Order.amount_total where not shipped) (Rule.sum with WHERE)
    - Customer.balance <= credit_limit (Rule.constraint)
    
    > **Key Takeaway:** One transaction triggers multiple chained rules automatically
    """
    scenario_name = 'Good Order Placed'
    test_utils.prt(f'\n{scenario_name}\n', scenario_name)
    
    # Create product and order
    product_id = create_test_product("Widget", unit_price=5.00)
    order_id = create_test_order(context.customer_id, "Good order")
    item_id = create_test_item(order_id, product_id, quantity=10)
    
    context.order_id = order_id
    context.item_id = item_id
    context.expected_balance = Decimal('50')  # 10 * 5.00


@when('Order Placed with quantity {quantity:d}')
def step_impl(context, quantity):
    """
    Attempt to place order that exceeds credit limit.
    
    This tests the constraint rule:
    - Customer.balance would exceed credit_limit
    - Transaction should be rejected
    
    > **Key Takeaway:** Constraints prevent invalid data automatically
    """
    scenario_name = 'Bad Order Exceeds Credit'
    test_utils.prt(f'\n{scenario_name}\n', scenario_name)
    
    product_id = create_test_product("Expensive Widget", unit_price=1.00)
    order_uri = f"{base_url}/Order/"
    
    post_data = {
        "data": {
            "type": "Order",
            "attributes": {
                "customer_id": int(context.customer_id),
                "notes": "Order exceeding credit",
                "date_shipped": None
            }
        }
    }
    
    # Create order first
    r = requests.post(url=order_uri, json=post_data, headers=test_utils.login())
    
    if r.status_code >= 200 and r.status_code < 300:
        order_id = int(r.json()['data']['id'])
        
        # Now try to add item that exceeds credit
        item_uri = f"{base_url}/Item/"
        item_data = {
            "data": {
                "type": "Item",
                "attributes": {
                    "order_id": int(order_id),
                    "product_id": int(product_id),
                    "quantity": quantity
                }
            }
        }
        
        r = requests.post(url=item_uri, json=item_data, headers=test_utils.login())
    
    context.response = r


@when('Item quantity changed to {new_quantity:d}')
def step_impl(context, new_quantity):
    """
    Alter existing item quantity to exceed credit limit.
    
    This tests:
    - PATCH operation triggers recalculation
    - Constraint checked on update (not just insert)
    
    > **Key Takeaway:** Rules enforce constraints on all operations
    """
    scenario_name = 'Alter Item Quantity to Exceed Credit'
    test_utils.prt(f'\n{scenario_name}\n', scenario_name)
    
    item_uri = f"{base_url}/Item/{context.item_id}/"
    patch_data = {
        "data": {
            "type": "Item",
            "id": str(context.item_id),
            "attributes": {
                "quantity": new_quantity
            }
        }
    }
    
    r = requests.patch(url=item_uri, json=patch_data, headers=test_utils.login())
    context.response = r


@when('Item product changed to expensive product')
def step_impl(context):
    """
    Change product_id on item to test copy rule re-execution.
    
    This tests:
    - Item.unit_price re-copies from new Product
    - Item.amount recalculates with new unit_price
    - Order.amount_total updates
    - Customer.balance updates
    
    > **Key Takeaway:** Foreign key changes trigger complete rule chain
    """
    scenario_name = 'Change Product on Item'
    test_utils.prt(f'\n{scenario_name}\n', scenario_name)
    
    # Create expensive product
    expensive_product_id = create_test_product("Expensive Product", unit_price=15.00)
    
    item_uri = f"{base_url}/Item/{context.item_id}/"
    patch_data = {
        "data": {
            "type": "Item",
            "id": str(context.item_id),
            "attributes": {
                "product_id": int(expensive_product_id)
            }
        }
    }
    
    r = requests.patch(url=item_uri, json=patch_data, headers=test_utils.login())
    context.response = r
    context.expensive_product_id = expensive_product_id
    context.new_expected_balance = Decimal('150')  # 10 items * 15.00


@when('Order moved to second customer')
def step_impl(context):
    """
    Change customer_id on order to test both parent adjustments.
    
    This tests THE CRITICAL BUG that procedural code misses:
    - Original customer balance decreases
    - New customer balance increases
    - Rules engine handles BOTH automatically
    
    > **Key Takeaway:** Declarative rules adjust both old and new parents
    """
    scenario_name = 'Change Customer on Order'
    test_utils.prt(f'\n{scenario_name}\n', scenario_name)
    
    order_uri = f"{base_url}/Order/{context.order_id}/"
    patch_data = {
        "data": {
            "type": "Order",
            "id": str(context.order_id),
            "attributes": {
                "customer_id": int(context.customer2_id)
            }
        }
    }
    
    r = requests.patch(url=order_uri, json=patch_data, headers=test_utils.login())
    context.response = r


@when('One item is deleted')
def step_impl(context):
    """
    Delete item to test aggregate adjustment downward.
    
    This tests DELETE operation (often forgotten):
    - Item deleted
    - Order.amount_total decreases
    - Customer.balance decreases
    
    > **Key Takeaway:** DELETE operations adjust aggregates downward automatically
    """
    scenario_name = 'Delete Item Adjusts Balance'
    test_utils.prt(f'\n{scenario_name}\n', scenario_name)
    
    item_uri = f"{base_url}/Item/{context.item1_id}/"
    r = requests.delete(url=item_uri, headers=test_utils.login())
    context.response = r


# ============================================================================
# THEN Steps - Assertions
# ============================================================================

@then('Balance is {expected_balance:d}')
def step_impl(context, expected_balance):
    """Verify customer balance equals expected value"""
    customer = get_customer(context.customer_id)
    actual_balance = Decimal(str(customer['balance']))
    expected = Decimal(str(expected_balance))
    
    assert actual_balance == expected, \
        f"Expected balance {expected}, got {actual_balance}"


@then('Customer balance does not exceed credit limit')
def step_impl(context):
    """Verify constraint is satisfied"""
    customer = get_customer(context.customer_id)
    balance = Decimal(str(customer['balance']))
    credit_limit = Decimal(str(customer['credit_limit']))
    
    assert balance <= credit_limit, \
        f"Balance {balance} exceeds credit limit {credit_limit}"


@then('Error raised containing "{text}"')
def step_impl(context, text):
    """Verify error response contains expected text"""
    assert context.response.status_code >= 400, \
        f"Expected error status, got {context.response.status_code}"
    
    response_text = context.response.text.lower()
    assert text.lower() in response_text, \
        f"Expected '{text}' in error message, got: {context.response.text}"


@then('Balance recalculates with new price')
def step_impl(context):
    """Verify balance updated with new product price"""
    customer = get_customer(context.customer_id)
    actual_balance = Decimal(str(customer['balance']))
    
    assert actual_balance == context.new_expected_balance, \
        f"Expected balance {context.new_expected_balance}, got {actual_balance}"


@then('Item unit_price updated from new product')
def step_impl(context):
    """Verify unit_price copied from new product"""
    item_uri = f"{base_url}/Item/{context.item_id}/"
    r = requests.get(url=item_uri, headers=test_utils.login())
    item = r.json()['data']['attributes']
    
    item_unit_price = Decimal(str(item['unit_price']))
    expected_price = Decimal('15.00')
    
    assert item_unit_price == expected_price, \
        f"Expected unit_price {expected_price}, got {item_unit_price}"


@then('First customer balance is {expected:d}')
def step_impl(context, expected):
    """Verify first customer balance after order transfer"""
    customer = get_customer(context.customer1_id)
    actual_balance = Decimal(str(customer['balance']))
    expected_balance = Decimal(str(expected))
    
    assert actual_balance == expected_balance, \
        f"First customer: expected balance {expected_balance}, got {actual_balance}"


@then('Second customer balance is {expected:d}')
def step_impl(context, expected):
    """Verify second customer balance after order transfer"""
    customer = get_customer(context.customer2_id)
    actual_balance = Decimal(str(customer['balance']))
    expected_balance = Decimal(str(expected))
    
    assert actual_balance == expected_balance, \
        f"Second customer: expected balance {expected_balance}, got {actual_balance}"


@then('Balance decreases correctly')
def step_impl(context):
    """Verify balance decreased after item deletion"""
    customer = get_customer(context.customer_id)
    actual_balance = Decimal(str(customer['balance']))
    
    assert actual_balance == context.expected_balance_after_delete, \
        f"Expected balance {context.expected_balance_after_delete}, got {actual_balance}"


# ============================================================================
# Helper Functions (Follow Rule #1 - No circular imports!)
# ============================================================================

def create_test_customer(name: str, credit_limit: int) -> int:
    """
    Create customer with specified credit limit.
    Balance defaults to 0 (it's an aggregate).
    
    Returns:
        int: Customer ID (converted from JSON string)
    """
    customer_uri = f"{base_url}/Customer/"
    post_data = {
        "data": {
            "type": "Customer",
            "attributes": {
                "name": name,
                "credit_limit": credit_limit,
                "email_opt_out": False
            }
        }
    }
    
    r = requests.post(url=customer_uri, json=post_data, headers=test_utils.login())
    result = r.json()
    return int(result['data']['id'])  # CRITICAL: Convert to int!


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


def get_customer(customer_id: int) -> dict:
    """
    Retrieve customer by ID.
    
    Returns:
        dict: Customer attributes
    """
    customer_uri = f"{base_url}/Customer/{customer_id}/"
    r = requests.get(url=customer_uri, headers=test_utils.login())
    return r.json()['data']['attributes']
