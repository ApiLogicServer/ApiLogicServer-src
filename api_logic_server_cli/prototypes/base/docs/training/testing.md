# AI Training: Creating Tests from Rules

> **🤖 For AI Assistants Only**
> 
> This is internal training material for AI assistants (like GitHub Copilot) to generate Behave tests from declarative business rules.
> 
> **👤 For Users:** See the [public documentation](https://apilogicserver.github.io/Docs/Behave-Creation/) which covers how to run tests, generate reports, and understand the testing framework.
> 
> This document focuses on Phase 2 testing (using custom business APIs) and the critical patterns AI must follow to generate correct tests.

## CRITICAL: Test Generation Workflow

**When user says "create tests from rules", follow this EXACT sequence:**

```
Step 1a. Read database/models.py → Understand schema (IDs, aggregates, columns)
Step 1b. Read logic/declare_logic.py → Identify rules to test  
Step 1c. Scan api/api_discovery/*.py → Discover custom APIs (PHASE 2!)
Step 2.  Decide Phase 1 vs Phase 2 → Based on custom API existence
Step 3.  Generate .feature files → Business language scenarios
Step 4.  Implement steps/*.py → Using discovered APIs or CRUD
Step 5.  Run tests → python behave_run.py
```

**DO NOT skip Step 1c!** Custom APIs change the entire testing approach.

## Phase 1 vs Phase 2: The Core Decision

### Phase 1: CRUD-Level Testing
- Direct API calls (POST, PATCH, DELETE)
- Granular rule testing (update qty, change FK, delete)
- Use when: No custom API exists

### Phase 2: Business Transaction Testing  
- Custom business APIs (api/api_discovery/)
- Complete transactions (Order + Items together)
- Business-friendly language ("Account" vs "customer_id")
- Use when: Custom API exists for the business object

**Decision Tree:**
```
Custom API exists in api/api_discovery/?
├─ YES → Phase 2 for CREATE, Phase 1 for UPDATE/DELETE
└─ NO  → Phase 1 for everything
```

## Step 1c: Discover Custom APIs (Phase 2)

**CRITICAL:** Check for custom APIs BEFORE generating CRUD tests!

**Discovery Process:**
```python
# 1. Scan api/api_discovery/*.py
# 2. Find classes with @jsonapi_rpc decorator
# 3. Extract: method name, endpoint, parameters, models created
# 4. Match to business rules (which rules does it test?)
```

**CRITICAL - Custom API Calling Convention:**

Custom APIs require **BOTH** `"method"` and `"args"` in the `meta` object:

```python
# ✅ CORRECT - Has both "method" and "args"
{
    "meta": {
        "method": "OrderB2B",    # ← REQUIRED!
        "args": {
            "data": { ... }
        }
    }
}

# ❌ WRONG - Missing "method" field
{
    "meta": {
        "args": {
            "data": { ... }
        }
    }
}
```

Without the `"method"` field, the API call will fail with a 500 error.

**Example Discovery - OrderB2B:**
```python
# api/api_discovery/order_b2b_service.py
class OrderB2BEndPoint(safrs.JABase):
    @jsonapi_rpc(http_methods=["POST"])
    def OrderB2B(self, *args, **kwargs):
        """
        Creates B2B orders from external partner systems.
        
        Parameters:
            Account: str - Customer name (not ID!)
            Notes: str
            Items: list - [{Name, QuantityOrdered}]
        """
```

**Discovery Result:**
```python
{
    "order_b2b_service": {
        "endpoint": "/api/OrderB2BEndPoint/OrderB2B",
        "parameters": {
            "Account": "Customer name",
            "Items": [{"Name": "Product name", "QuantityOrdered": int}]
        },
        "creates": ["Order", "Item"],
        "tests_rules": [
            "Customer.Balance = sum(Order.AmountTotal)",
            "Order.AmountTotal = sum(Item.Amount)", 
            "Customer.Balance <= CreditLimit"
        ]
    }
}
```

**Using Discovered API:**
```python
# Phase 2: CREATE using custom API
@when('B2B order placed for "{customer_name}" with items')
def step_impl(context):
    add_order_uri = 'http://localhost:5656/api/OrderB2BEndPoint/OrderB2B'
    add_order_args = {
        "meta": {"method": "OrderB2B", "args": {"data": {
            "Account": customer_name,  # Business language!
            "Items": [{"Name": "Widget", "QuantityOrdered": 5}]
        }}}
    }
    r = requests.post(url=add_order_uri, json=add_order_args)

# Phase 1: UPDATE using CRUD (granular testing)
@when('Item quantity changed to {qty:d}')
def step_impl(context, qty):
    patch_uri = f'http://localhost:5656/api/Item/{item_id}/'
    patch_data = {"data": {"attributes": {"quantity": qty}}}
    r = requests.patch(url=patch_uri, json=patch_data)
```

## The 6 Critical Rules (Read FIRST!)

### Rule #0: TEST REPEATABILITY (MOST CRITICAL!) ⚠️

**TESTS MODIFY THE DATABASE. Tests MUST be repeatable and restartable.**

```python
# ❌ WRONG - Reuses contaminated data
@given('Customer "Bob" with balance {balance:d}')
def step_impl(context, name, balance):
    r = requests.get(f'/api/Customer/?filter[name]=Bob')
    if r.json()['data']:
        customer = r.json()['data'][0]  # REUSES Bob - balance accumulated!

# ✅ CORRECT - Always creates fresh data with timestamp
@given('Customer "Bob" with balance {balance:d}')
def step_impl(context, name, balance):
    unique_name = f"Bob {int(time.time() * 1000)}"  # ALWAYS unique!
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
    r = requests.post(f'/api/Customer/', json=post_data)
    context.customer_id = int(r.json()['data']['id'])
    context.customer_name = unique_name  # Save for later use
```

**Critical Patterns:**
- **NEVER reuse existing customers/orders** - always create fresh
- **Use timestamps** in names: `f"Bob {int(time.time() * 1000)}"`
- **Match exact database names** - "Widget" not "Widgets"
- **Don't assume clean state** - tests may run after failures
- **Track name mappings** for multi-customer tests (see Rule #8)
- **Understand DERIVED vs ADDED aggregates** (see Rule #9)

### Rule #0.5: BEHAVE STEP ORDERING (Pattern Matching!) ⚠️

**Behave matches steps by FIRST pattern that fits. More specific patterns MUST come before general ones.**

**Example 1: Carbon Neutral Products**

```python
# ❌ WRONG ORDER - General pattern matches first, specific never runs!
@when('B2B order placed for "{customer_name}" with {quantity:d} {product_name}')
def step_impl_general(context, customer_name, quantity, product_name):
    # This matches "carbon neutral Widget" as product_name="carbon neutral Widget"
    # The specific carbon neutral step below NEVER executes!
    ...

@when('B2B order placed for "{customer_name}" with {quantity:d} carbon neutral {product_name}')
def step_impl_carbon_neutral(context, customer_name, quantity, product_name):
    # NEVER REACHED because general pattern above matched first
    ...

# ✅ CORRECT ORDER - Specific pattern first!
@when('B2B order placed for "{customer_name}" with {quantity:d} carbon neutral {product_name}')
def step_impl_carbon_neutral(context, customer_name, quantity, product_name):
    # This matches first for "carbon neutral Widget"
    # Sets context.item_id correctly
    ...

@when('B2B order placed for "{customer_name}" with {quantity:d} {product_name}')
def step_impl_general(context, customer_name, quantity, product_name):
    # Only matches if "carbon neutral" not present
    ...
```

**Example 2: Multi-Item Orders**

```python
# ❌ WRONG ORDER - Single-item pattern matches "3 Widget and 2 Gadget"
@given('Order exists for "{customer_name}" with {quantity:d} {product_name}')
def step_impl_single(context, customer_name, quantity, product_name):
    # This matches FIRST!
    # product_name = "Widget and 2 Gadget" (treats "and 2 Gadget" as part of name)
    # Creates only 1 item, context.item_ids never set properly
    ...

@given('Order exists for "{customer_name}" with {qty1:d} {product1} and {qty2:d} {product2}')
def step_impl_multi(context, customer_name, qty1, product1, qty2, product2):
    # NEVER REACHED! Single-item pattern above matched first
    ...

# ✅ CORRECT ORDER - Multi-item pattern first!
@given('Order exists for "{customer_name}" with {qty1:d} {product1} and {qty2:d} {product2}')
def step_impl_multi(context, customer_name, qty1, product1, qty2, product2):
    # This matches first for "3 Widget and 2 Gadget"
    # Creates 2 items, sets context.item_ids = [id1, id2]
    ...

@given('Order exists for "{customer_name}" with {quantity:d} {product_name}')
def step_impl_single(context, customer_name, quantity, product_name):
    # Only matches if "and" not present
    ...
```

**Why This Matters:**
- Wrong order → context.item_id not set → "Then Item amount" step fails with "item_id not set in context"
- Behave doesn't warn about unreachable patterns
- **ALWAYS order from most specific to most general**

**Specificity Rules:**
- More literal text = more specific ("and", "carbon neutral")
- More parameters = more specific
- Tighter type constraints = more specific

**Anti-Pattern Alert:**
Using `context.execute_steps()` to reuse step logic can cause context propagation issues. Instead, duplicate the implementation for specific patterns (DRY doesn't apply to Behave steps with context dependencies).

**Debugging Tip:**
If a step seems to execute but context variables aren't set, check if a MORE GENERAL pattern exists ABOVE it in the file.

### Rule #1: Read database/models.py First
```python
# Check: ID types (Integer vs String), column names, aggregates
class Customer(Base):
    id = Column(Integer, primary_key=True)  # Integer not String!
    balance = Column(Numeric)  # Check logic - is this aggregate?
```

### Rule #2: Use Direct FK Format
```python
# ✅ CORRECT
post_data = {
    "data": {
        "attributes": {"customer_id": int(customer_id)}  # Direct FK
    }
}

# ❌ WRONG - causes optimistic locking errors
post_data = {
    "data": {
        "relationships": {"customer": {"data": {"id": customer_id}}}
    }
}
```

### Rule #3: Mandatory Patterns
```python
# Filter format
params = {"filter[name]": "Alice"}  # NOT: {"filter": "name eq 'Alice'"}

# Unique test data
name = f"Test {int(time.time() * 1000)}"  # NOT: "Test Customer"

# Convert IDs
customer_id = int(result['data']['id'])  # NOT: result['data']['id']

# Imports (only these!)
from behave import *
import requests, test_utils, time
from decimal import Decimal
# NO imports from logic/, database/, integration/
```

### Rule #4: Complete CRUD + WHERE Coverage
```gherkin
Scenario: Good Order (CREATE - POST)
Scenario: Item Qty Change (UPDATE - PATCH)
Scenario: Change Customer (UPDATE - FK change, both parents adjust)
Scenario: Delete Item (DELETE)
Scenario: Ship Order (WHERE exclude)
Scenario: Unship Order (WHERE include - test bidirectional!)
Scenario: Exceed Credit (Constraint FAIL - negative test)
```

**CRITICAL:** Check `logic/declare_logic.py` for custom Python logic affecting calculations (e.g., discounts, adjustments) before writing constraint test expectations!

### Rule #5: Security Configuration
```python
# Read config/default.env FIRST
SECURITY_ENABLED = False  # or True

# Match in test code
if SECURITY_ENABLED == False:
    headers = {}  # Empty
else:
    headers = test_utils.login()
```

### Rule #6: Logic Logging
```python
@when('Good Order Placed')
def step_impl(context):
    scenario_name = 'Good Order Placed'
    test_utils.prt(f'\n{scenario_name}\n', scenario_name)  # 2nd arg critical!
```

### Rule #7: Custom API Response Handling ⚠️ NEW
```python
# Phase 2 APIs may return different formats - handle both!
r = requests.post(url=api_uri, json=args, headers=get_headers())
context.order_created = (r.status_code == 200)

if context.order_created:
    response_data = r.json()
    # Custom APIs may return direct dict, not JSON:API format
    context.order_id = response_data.get('order_id')  # Direct field
else:
    context.order_id = None  # Always set to prevent KeyError

# When reading back via CRUD API:
r = requests.get(url=order_uri, headers=get_headers())
if 'data' in r.json():
    order_data = r.json()['data']['attributes']  # JSON:API format
else:
    order_data = r.json()  # Direct format
```

### Rule #8: Customer Name Mapping for Multi-Customer Tests ⚠️ NEW
```python
# When tests involve MULTIPLE customers, track the mapping!
@given('Customer "{customer_name}" with balance {balance:d}')
def step_impl(context, customer_name, balance, limit):
    unique_name = f"{customer_name} {int(time.time() * 1000)}"
    # ... create customer ...
    
    # Track mapping for later lookups
    if not hasattr(context, 'customer_map'):
        context.customer_map = {}
    context.customer_map[customer_name] = {'id': customer_id, 'unique_name': unique_name}

# Then later, when checking specific customer:
@then('Customer "{customer_name}" balance should be {expected:d}')
def step_impl(context, customer_name, expected):
    # ✅ CORRECT - Use ID from mapping
    customer_info = context.customer_map[customer_name]
    r = requests.get(f'/api/Customer/{customer_info["id"]}/')
    
    # ❌ WRONG - Query by original name (won't find "Bob 1729...")
    r = requests.get(f'/api/Customer/?filter[name]={customer_name}')
```

### Rule #9: Understand DERIVED Aggregates ⚠️ NEW
```python
# Customer.balance is DERIVED from orders, not ADDED to!
Rule.sum(derive=Customer.balance, as_sum_of=Order.amount_total, 
         where=lambda row: row.date_shipped is None)

# ❌ WRONG expectations:
# Given Customer "Charlie" with existing balance 220
# And Order for 180
# Then balance should be 310  # WRONG! Thinks 220 + 90 (after delete)

# ✅ CORRECT expectations:
# Given Customer "Charlie" with balance 0
# And Order for 180
# Then balance should be 90  # After deleting one item
# The "existing balance 220" is REPLACED by sum of orders (180)!
```

### Rule #10: Verify Actual Database Values FIRST ⚠️ NEW
```python
# ALWAYS check actual product prices/flags before writing test expectations!

# Check prices:
# sqlite3 db.sqlite "SELECT name, unit_price, carbon_neutral FROM Product;"

# Widget=90, Gadget=150, Green=109

# ❌ WRONG - Assumed Widget=$100
# Expected: 10 * 100 = 1000

# ✅ CORRECT - Verified Widget=$90  
# Expected: 10 * 90 = 900

# For carbon neutral discount (10% off when qty >= 10):
# Expected: 10 * 90 * 0.9 = 810
```

### Rule #11: Step Definitions Must Match Feature Files ⚠️ NEW
```python
# Feature file:
Given Customer "Alice" with balance 0 and credit limit 1000

# Step implementation - ALL parameters must be captured:
@given('Customer "{customer_name}" with balance {balance:d} and credit limit {limit:d}')
def step_impl(context, customer_name, balance, limit):  # ✅ CORRECT
    pass

# ❌ WRONG - hard-coded values instead of parameters:
@given('Customer "{customer_name}" exists with balance 0 and credit limit 1000')
def step_impl(context, customer_name):  # Missing balance and limit parameters!
    balance = 0  # Hard-coded - won't work for different scenarios
    limit = 1000
```

### Rule #10: Always Initialize Context Variables ⚠️ NEW
```python
# ✅ CORRECT - prevents KeyError in subsequent steps
@when('B2B order placed')
def step_impl(context):
    r = requests.post(url=api_uri, json=args)
    context.order_created = (r.status_code == 200)
    
    if context.order_created:
        context.order_id = r.json().get('order_id')
    else:
        context.order_id = None  # CRITICAL - prevents "not hasattr" errors
        
# Then steps can safely check:
@then('Each item calculated correctly')
def step_impl(context):
    if not hasattr(context, 'order_id') or context.order_id is None:
        assert not context.order_created, "Order should have failed"
        return  # Skip gracefully
```

## Complete Phase 2 Example

### .feature File
```gherkin
Feature: Order Processing via B2B API

  # Phase 2: CREATE
  Scenario: Good Order Placed
     When B2B order placed for "Alice" with items:
       | Name   | Quantity |
       | Widget | 5        |
     Then Customer balance is 50
     Then Order created successfully

  # Phase 1: UPDATE (granular)
  Scenario: Alter Item Quantity
     Given Order exists with 1 item (qty 5)
     When Item quantity changed to 10
     Then Item amount is 100
     Then Order amount_total is 100
```

### Step Implementation
```python
from behave import *
import requests, test_utils, time
from decimal import Decimal

BASE_URL = 'http://localhost:5656'

@when('B2B order placed for "{customer_name}" with items')
def step_impl(context):
    """Phase 2: Uses OrderB2B custom API"""
    scenario_name = 'B2B Order Placement'
    test_utils.prt(f'\n{scenario_name}\n', scenario_name)
    
    items = [{"Name": row['Name'], "QuantityOrdered": int(row['Quantity'])} 
             for row in context.table]
    
    add_order_uri = f'{BASE_URL}/api/OrderB2BEndPoint/OrderB2B'
    add_order_args = {
        "meta": {"method": "OrderB2B", "args": {"data": {
            "Account": customer_name,
            "Notes": "Test order",
            "Items": items
        }}}
    }
    
    r = requests.post(url=add_order_uri, json=add_order_args, 
                     headers=test_utils.login())
    context.order_created = (r.status_code == 200)
    if context.order_created:
        response_data = r.json()
        context.order_id = response_data.get('order_id')  # Custom API direct response
    else:
        context.order_id = None  # Always initialize to prevent KeyError

@when('Item quantity changed to {qty:d}')
def step_impl(context, qty):
    """Phase 1: Uses CRUD for granular testing"""
    scenario_name = 'Item Quantity Update'
    test_utils.prt(f'\n{scenario_name}\n', scenario_name)
    
    patch_uri = f'{BASE_URL}/api/Item/{context.item_id}/'
    patch_data = {
        "data": {
            "attributes": {"quantity": qty},
            "type": "Item",
            "id": context.item_id
        }
    }
    r = requests.patch(url=patch_uri, json=patch_data, 
                      headers=test_utils.login())

@then('Customer balance is {expected:d}')
def step_impl(context, expected):
    customer_uri = f'{BASE_URL}/api/Customer/{context.customer_id}/'
    r = requests.get(url=customer_uri, headers=test_utils.login())
    actual = float(r.json()['data']['attributes']['balance'])
    assert abs(actual - expected) < 0.01
```

## Quick Error Reference

| Error | Fix |
|-------|-----|
| "405 Method Not Allowed" | `SECURITY_ENABLED=False`, remove auth |
| "invalid literal for int('ALFKI')" | Check models.py - use Integer IDs |
| "balance: field not writable" | Aggregate - create child Orders, don't set |
| "Invalid filter format" | Use `filter[name]=value` |
| "row altered by another user" | Use direct FK: `"customer_id": int(id)` |
| "circular import" | Remove imports from logic/, database/ |
| "empty logic log" | Add `test_utils.prt(msg, scenario_name)` |

## Test Generation Workflow

```
1. Read database/models.py → Understand schema (IDs, aggregates)
2. Read logic/declare_logic.py → Identify rules to test
3. Scan api/api_discovery/*.py → Discover custom APIs
4. Decide Phase 1 vs Phase 2 → Based on custom API existence
5. Generate .feature files → Business language scenarios
6. Implement steps/*.py → Using discovered APIs or CRUD
7. Run tests → python behave_run.py
8. Generate report → python behave_logic_report.py run
```

## Key Testing Patterns

**Test ALL scenarios for each rule:**
- ✅ CREATE (POST) - new entity triggers rules
- ✅ UPDATE (PATCH) - modify triggers recalc
- ✅ UPDATE FK - change parent (both old/new adjust)
- ✅ DELETE - remove entity (aggregates down)
- ✅ WHERE include - condition becomes true
- ✅ WHERE exclude - condition becomes false
- ✅ Constraint pass - valid data accepted
- ✅ Constraint fail - invalid data rejected

**Common missed scenarios:**
- ❌ Only testing CREATE/UPDATE, not DELETE
- ❌ Only testing WHERE one direction (ship, not unship)
- ❌ Only testing constraint pass, not fail
- ❌ Only testing FK create, not FK change

## Benefits of Phase 2

| Phase 2 (Custom API) | Phase 1 (CRUD) |
|---------------------|----------------|
| One API call | Multiple CRUD calls |
| Business language | Technical IDs |
| Tests API + Rules | Tests Rules only |
| Realistic scenarios | Implementation details |
| "Place Order" | "POST Order, POST Items" |

**The Magic:** Users built OrderB2B for partners → Same API provides natural test scenarios!

