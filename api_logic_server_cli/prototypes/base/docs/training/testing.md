# Automated Testing: Creating Tests from Rules

This guide explains how to create Behave tests from declarative rules, execute test suites, and generate automated documentation with complete logic traceability.

## Overview: Behave BDD Testing Framework

[Behave](https://behave.readthedocs.io/en/stable/tutorial.html) is a framework for defining and executing tests based on [TDD (Test Driven Development)](http://dannorth.net/introducing-bdd/), an Agile approach for defining system requirements as executable tests.

**The Key Innovation:** Behave tests in API Logic Server create **living documentation** that connects:
1. Business Requirements (Features)
2. Test Scenarios (Given/When/Then)
3. Test Implementation (Python code)
4. **Declarative Rules** (the actual business logic)
5. **Execution Trace** (Logic Log showing which rules fired)

## The Complete Workflow

```
1. Analyze Rules → Identify test scenarios
2. Create .feature files → Define scenarios in natural language
3. Implement steps/*.py → Write test code
4. Run Behave → Execute test suite (generates logs)
5. Generate Report → Create documentation with logic traceability
```

## Prerequisites and Configuration

### Critical: Security Configuration

**Tests must match the project's security settings** defined in `config/default.env`:

```bash
# In config/default.env
SECURITY_ENABLED = false  # or True
```

**The test framework automatically adapts:**
- `test_utils.login()` returns empty headers `{}` when `SECURITY_ENABLED = false`
- `test_utils.login()` authenticates and returns token headers when `SECURITY_ENABLED = True`

**Common Bug:** Tests fail with `405 Method Not Allowed` on `/auth/login`
- **Cause:** Server running without security, but tests expect security enabled (or vice versa)
- **Solution:** Check `config/default.env` - ensure `SECURITY_ENABLED` matches how server was started
- **Test Location:** Behave runs from `test/api_logic_server_behave/` and logs found in `logs/behave.log`

### Test Data Requirements

Tests require specific database state:
1. **Document test data** in `TEST_SUITE_OVERVIEW.md` or feature file comments
2. **Restore data** after test runs (tests should be idempotent)
3. **Seed database** with known customer IDs, product IDs, order IDs before first run

**Example:** If testing Customer balance rules, document:
```
Test Data Used:
- Customer: CUST-1 (balance 0, credit_limit 1000)
- Product: PROD-A (unit_price 5.00)
- Order: ORD-1 (customer CUST-1, not shipped)
```

### Running the Server

Before running tests, start the API Logic Server:

**Option 1: VS Code Launch Configuration**
- Use **"ApiLogicServer"** launch config
- Respects `config/default.env` settings

**Option 2: Command Line**
```bash
python api_logic_server_run.py
```

**Verify server is running:**
```bash
curl http://localhost:5656/api/Customer/
```

## Creating Tests from Declarative Rules

### Step 1: Analyze Your Rules

Given declarative rules in `logic/declare_logic.py`, identify what needs testing:

**Example Rules:**
```python
Rule.sum(derive=Customer.Balance, as_sum_of=Order.AmountTotal, 
         where=lambda row: row.ShippedDate is None)
Rule.sum(derive=Order.AmountTotal, as_sum_of=OrderDetail.Amount)
Rule.formula(derive=OrderDetail.Amount, 
             as_expression=lambda row: row.UnitPrice * row.Quantity)
Rule.copy(derive=OrderDetail.UnitPrice, from_parent=Product.UnitPrice)
Rule.constraint(validate=Customer, 
                as_condition=lambda row: row.Balance <= row.CreditLimit,
                error_msg="Customer balance ({row.Balance}) exceeds credit limit ({row.CreditLimit})")
```

### Step 1a: Inspect Database Schema (CRITICAL!)

**Before writing any test code**, inspect `database/models.py` to understand:

1. **Primary key data types** - Are IDs integers, strings, UUIDs?
   ```python
   class Customer(Base):
       id = Column(Integer, primary_key=True)  # ← Integer IDs (1, 2, 3)
       # vs
       id = Column(String, primary_key=True)   # ← String IDs ('CUST-1', 'ALFKI')
   ```

2. **Column names** - Exact spelling (balance vs Balance, customer_id vs CustomerId)

3. **Foreign key relationships** - Which tables link to which

4. **Nullable fields** - Which fields can be None

**Common Bug:** Tests fail with `invalid literal for int() with base 10: 'CUST-1'`
- **Cause:** Used string ID `'CUST-1'` but table expects integer `1`
- **Solution:** Check models.py before writing test data

### Step 1a-2: Identify Aggregate Columns (CRITICAL!)

**NEVER set aggregate columns directly - they are computed from child data!**

**How to identify aggregates:**

1. **Check logic files** (`logic/*.py`) for `Rule.sum`, `Rule.count`, `Rule.formula`:
   ```python
   # In logic/declare_logic.py
   Rule.sum(derive=Customer.balance, as_sum_of=Order.amount_total,
            where=lambda row: row.date_shipped is None)
   ```
   → **Customer.balance is an AGGREGATE** (sum of child Orders)

2. **Look for aggregate_default in logic logs:**
   ```
   ..Customer[None] {server aggregate_defaults: balance }
   ```
   → **balance is initialized by the rules engine, not by client**

3. **Common aggregates:**
   - **Sum columns:** `balance`, `amount_total`, `order_total`
   - **Count columns:** `order_count`, `item_count`
   - **Computed columns:** Any column derived by `Rule.formula` or `Rule.sum`

**The Bug:**
```python
# ❌ WRONG - Trying to set aggregate directly
post_data = {
    "attributes": {
        "name": "Test Customer",
        "balance": 950,  # ← balance is an aggregate! Can't set directly!
        "credit_limit": 1000
    }
}
# Result: Server rejects or ignores balance value
```

**The Fix:**
```python
# ✅ CORRECT - Create child data to reach desired aggregate
# Step 1: Create customer (balance defaults to 0)
post_data = {
    "attributes": {
        "name": "Test Customer",
        # Don't set balance - it's computed from Orders
        "credit_limit": 1000
    }
}
r = requests.post(url=customer_uri, json=post_data)
customer_id = r.json()['data']['id']

# Step 2: Create orders to reach balance=950
product_id = create_test_product(unit_price=1.00)
order_id = create_test_order(customer_id, "Filler order")
create_test_item(order_id, product_id, quantity=950)  # Creates balance of 950

# Now customer.balance = 950 (computed by Rule.sum)
```

**Helper Function Pattern (Recommended):**
```python
def get_or_create_test_customer(name="Test Customer", balance=0, credit_limit=1000) -> int:
    """
    Create customer. Does NOT create filler orders.
    
    NOTE: balance parameter is for documentation only - helper always creates
    customer with balance=0. Caller must create orders to reach target balance.
    
    Returns:
        int: Customer ID (ALWAYS converted from JSON string to integer!)
    """
    # Create customer (aggregates default to 0)
    post_data = {
        "data": {
            "attributes": {
                "name": name,
                "credit_limit": credit_limit  # OK - regular column
                # NO balance - it's an aggregate!
            },
            "type": "Customer"
        }
    }
    r = requests.post(url=customer_uri, json=post_data, headers=test_utils.login())
    result = r.json()
    return int(result['data']['id'])  # CRITICAL: Convert to int! JSON returns string
```

**CRITICAL: Always Convert JSON IDs to int**

JSON APIs return IDs as **strings**, but database expects **integers**:
```python
# ❌ WRONG - Returns string "8"
return result['data']['id']

# ✅ CORRECT - Returns integer 8
return int(result['data']['id'])
```

**All helper functions MUST convert:**
```python
def get_or_create_test_product(name, unit_price) -> int:
    # ...
    return int(result['data']['id'])  # ← int()

def create_test_order(customer_id, notes) -> int:
    # ...
    return int(result['data']['id'])  # ← int()

def create_test_item(order_id, product_id, quantity) -> int:
    # ...
    return int(result['data']['id'])  # ← int()
```

**Using the Helper in GIVEN Steps:**
```python
@given('Customer with balance {balance:d} and credit {credit:d}')
def step_impl(context, balance, credit):
    """
    Create customer with specified balance.
    Balance is aggregate - must create orders to reach it.
    """
    # Step 1: Create customer (balance defaults to 0)
    customer_id = get_or_create_test_customer(
        name=f"Test Cust {balance}",
        credit_limit=credit
    )
    # customer_id is now integer (not string!)
    
    # Step 2: If balance > 0, create filler order to reach it
    if balance > 0:
        product_id = get_or_create_test_product("Filler", unit_price=1.00)
        order_id = create_test_order(customer_id, "Filler order")
        create_test_item(order_id, product_id, quantity=balance)
        # Now customer.balance = balance (computed by rules)
    
    context.customer_id = customer_id
    context.initial_balance = balance
```

**Why Keep Helpers Simple:**
- ✅ **Single responsibility** - helper creates entity, step creates relationships
- ✅ **Avoid circular dependencies** - helper doesn't call other helpers recursively
- ✅ **Clear test logic** - step shows exactly what data is being created
- ✅ **Easier debugging** - can see full data creation in step implementation
- ✅ **Flexible** - different tests can create different order structures

**Anti-Pattern (Don't Do This):**
```python
# ❌ WRONG - Helper tries to create filler orders automatically
def get_or_create_test_customer(name, balance=0, credit_limit=1000):
    customer_id = create_customer(name, credit_limit)
    
    if balance > 0:
        # Problem: Circular dependency! Calls other helpers
        product_id = get_or_create_test_product(...)  # ← Can cause issues
        order_id = create_test_order(...)  # ← Hard to debug
        create_test_item(...)  # ← Hidden test data creation
    
    return customer_id
    # Issues: Complex, hard to debug, circular dependencies, unclear what data exists
```

**Why this matters:**
- ✅ **Aggregates reflect reality** - balance = sum of actual orders
- ✅ **Tests the rules engine** - verifies aggregates compute correctly
- ✅ **Prevents silent failures** - server won't accept invalid aggregate values
- ✅ **Works with any database** - doesn't rely on pre-seeded data
- ✅ **Clear separation** - helper creates entity, step creates relationships

**Common aggregate patterns:**
- `Customer.balance` ← Sum of `Order.amount_total` (where not shipped)
- `Order.amount_total` ← Sum of `Item.amount`
- `Product.units_in_stock` ← Count or sum of inventory transactions
- `Department.budget_used` ← Sum of `Employee.salary`

**Rule of thumb:** 
1. If a column appears in `Rule.sum()`, `Rule.count()`, or `Rule.formula()` → It's an aggregate
2. Helpers create entities WITHOUT aggregates
3. Test steps create child data to reach desired aggregate values

### Step 1b: Query Existing Data OR Create Test Data

**Option A: Use Existing Data (Query First)**

```python
# In features/steps/my_test.py
def get_test_customer():
    """Find first customer to use for testing"""
    r = requests.get('http://localhost:5656/api/Customer/?page[limit]=1', 
                     headers=test_utils.login())
    data = json.loads(r.text)
    if data['data']:
        return data['data'][0]['id']  # Returns actual ID from database
    else:
        raise Exception('No customers found - seed database first')
```

**Option B: Create Test Data Programmatically**

```python
# In features/environment.py
def before_all(context):
    """Create test data before running scenarios"""
    # Create test customer
    post_uri = 'http://localhost:5656/api/Customer/'
    post_data = {
        "data": {
            "attributes": {
                "name": "Test Customer",
                "balance": 0,
                "credit_limit": 1000
            },
            "type": "Customer"
        }
    }
    r = requests.post(url=post_uri, json=post_data, headers=test_utils.login())
    result = json.loads(r.text)
    context.test_customer_id = result['data']['id']  # Save for scenarios
```

**Option C: Document Required Test Data**

```markdown
# In TEST_SUITE_OVERVIEW.md or feature file comments
Test Data Requirements:
- Customer ID 1: balance=0, credit_limit=1000
- Product ID 1: unit_price=5.00
- Product ID 2: unit_price=10.00

Setup:
Run `python database/test_data/setup_test_data.py` to seed database
```

### Step 2: Identify Test Scenarios

From these rules, generate test scenarios that verify:

**A. Basic Rule Execution:**
- Does `Customer.Balance` update when `Order.AmountTotal` changes?
- Does `Order.AmountTotal` update when `OrderDetail` quantities change?
- Does `OrderDetail.UnitPrice` copy from `Product.UnitPrice`?

**B. Dependency Chains (Critical!):**
- Changing `OrderDetail.Quantity` → affects `Item.Amount` → `Order.AmountTotal` → `Customer.Balance`
- Changing `Product.UnitPrice` → affects copied `OrderDetail.UnitPrice` → `Item.Amount` → chain up
- Changing `Order.ShippedDate` → includes/excludes order from `Customer.Balance` (where clause)

**C. Foreign Key Changes (The Missed Bugs!):**
- Changing `Order.CustomerId` → adjusts **both old and new customer balances**
- Changing `OrderDetail.ProductId` → re-copies `UnitPrice` from new product

**D. Constraints:**
- Exceeding `Customer.CreditLimit` → rejection
- Edge cases that should trigger constraints

**E. Events:**
- Kafka messages sent when conditions met
- Email notifications triggered
- Integration actions

### Step 3: Create .feature Files

Create `test/api_logic_server_behave/features/<feature_name>.feature`:

```gherkin
Feature: Place Order

  Scenario: Good Order Custom Service
     Given Customer Account: ALFKI
      When Good Order Placed
      Then Logic adjusts Balance (demo: chain up)
      Then Logic adjusts Products Reordered
      Then Logic sends email to salesrep
      Then Logic sends kafka message
      Then Logic adjusts aggregates down on delete order

  Scenario: Bad Order Custom Service
     Given Customer Account: ALFKI
      When Order Placed with excessive quantity
      Then Rejected per Check Credit

  Scenario: Alter Item Qty to exceed credit
     Given Customer Account: ALFKI
      When Order Detail Quantity altered very high
      Then Rejected per Check Credit

  Scenario: Set Shipped - adjust logic reuse
     Given Customer Account: ALFKI
      When Order ShippedDate altered (2013-10-13)
      Then Balance reduced 1086
      Then Product[46] UnitsInStock adjusted

  Scenario: Change Customer on Order
     Given Customer Account: ALFKI
      When Order moved to different customer
      Then Both customer balances adjust correctly
```

### Step 4: Implement Test Steps

Create `test/api_logic_server_behave/features/steps/<feature_name>.py`:

```python
from behave import *
import requests
import test_utils
import json
from dotmap import DotMap

@given('Customer Account: ALFKI')
def step_impl(context):
    """Load initial customer data for testing"""
    alfki_before = get_customer('ALFKI')
    context.alfki_before = alfki_before

@when('Good Order Placed')
def step_impl(context):
    """
    Place an order with multiple items.
    
    This tests the complete dependency chain:
    - OrderDetail.UnitPrice copied from Product.UnitPrice (Rule.copy)
    - OrderDetail.Amount = Quantity * UnitPrice (Rule.formula)
    - Order.AmountTotal = Sum(OrderDetail.Amount) (Rule.sum)
    - Customer.Balance = Sum(Order.AmountTotal where not shipped) (Rule.sum with where)
    
    > **Key Takeaway:** One transaction triggers multiple chained rules
    """
    scenario_name = 'Good Order Custom Service'
    test_utils.prt(f'\n{scenario_name}... testing complete chain\n', scenario_name)
    
    post_uri = 'http://localhost:5656/api/Order/'
    post_args = {
        "data": {
            "attributes": {
                "CustomerId": "ALFKI",
                "EmployeeId": 1,
                "OrderDetailList": [
                    {"ProductId": 1, "Quantity": 1},
                    {"ProductId": 2, "Quantity": 2}
                ]
            },
            "type": "Order"
        }
    }
    r = requests.post(url=post_uri, json=post_args, headers=test_utils.login())
    context.response_text = r.text

@then('Logic adjusts Balance (demo: chain up)')
def step_impl(context):
    """Verify Customer.Balance updated correctly via rule chain"""
    before = context.alfki_before
    after = get_customer('ALFKI')
    expected_change = calculate_expected_order_total()  # based on test data
    assert after.Balance == before.Balance + expected_change, \
        f'Balance should be {before.Balance + expected_change}, got {after.Balance}'
```

**Critical Implementation Details:**

1. **Include docstrings** on `@when` steps - these become "Logic Doc" in the report
2. **Use `test_utils.prt()`** with scenario name as 2nd argument - drives Logic Log file naming
3. **Test data restoration** - tests should restore data to original state
4. **Include scenario_name line** - required for report generation:
   ```python
   scenario_name = 'Good Order Custom Service'
   test_utils.prt(f'\n{scenario_name}...\n', scenario_name)
   ```

## Test Patterns for Common Rules

### Pattern 1: Testing Sum Rules with Where Clauses

**Rule:**
```python
Rule.sum(derive=Customer.Balance, as_sum_of=Order.AmountTotal,
         where=lambda row: row.ShippedDate is None)
```

**Test Scenarios:**
```gherkin
Scenario: Order Made Ready
  Given Customer Account: ALFKI
  When Ready Flag is Set
  Then Logic Increases Balance

Scenario: Set Shipped
  Given Customer Account: ALFKI
  When Order ShippedDate altered (2013-10-13)
  Then Balance reduced
```

**Why:** Tests both inclusion (Ready=True) and exclusion (ShippedDate set) from the sum.

### Pattern 2: Testing Foreign Key Changes

**Rule:**
```python
Rule.sum(derive=Customer.Balance, as_sum_of=Order.AmountTotal)
```

**Test Scenario:**
```gherkin
Scenario: Change Customer on Order
  Given Order for Customer ALFKI
  When Order CustomerId changed to BOLID
  Then ALFKI Balance decreased
  Then BOLID Balance increased
```

**Why:** Verifies the rules engine adjusts **both** old and new parent aggregates.

### Pattern 3: Testing Copy Rules with Foreign Key Changes

**Rule:**
```python
Rule.copy(derive=OrderDetail.UnitPrice, from_parent=Product.UnitPrice)
```

**Test Scenario:**
```gherkin
Scenario: Change Product on OrderDetail
  Given OrderDetail for Product 1 (price $10)
  When ProductId changed to Product 2 (price $20)
  Then OrderDetail.UnitPrice updates to $20
  Then Order.AmountTotal recalculates
  Then Customer.Balance updates
```

**Why:** Verifies copy rule re-executes and chain propagates up.

### Pattern 4: Testing Constraints

**Rule:**
```python
Rule.constraint(validate=Customer,
                as_condition=lambda row: row.Balance <= row.CreditLimit,
                error_msg="Balance exceeds credit limit")
```

**Test Scenarios:**
```gherkin
Scenario: Bad Order Custom Service
  Given Customer Account: ALFKI
  When Order Placed with excessive quantity
  Then Rejected per Check Credit

Scenario: Alter Item Qty to exceed credit
  Given Customer Account: ALFKI
  When Order Detail Quantity altered very high
  Then Rejected per Check Credit
```

**Why:** Tests constraint from different entry points (new order vs. altered existing).

### Pattern 5: Testing Events

**Rule:**
```python
Rule.after_flush_row_event(on_class=Order, 
                           calling=kafka_producer.send_row_to_kafka,
                           if_condition=lambda row: row.ShippedDate is not None,
                           with_args={"topic": "order_shipping"})
```

**Test Scenario:**
```gherkin
Scenario: Good Order Custom Service
  Given Customer Account: ALFKI
  When Good Order Placed
  Then Logic sends kafka message
```

**Why:** Verifies event triggered when condition met.

## Executing Tests

### Run Test Suite

Use Launch Configuration **"Behave Run"** (or **"Windows Behave Run"** on Windows):

```bash
# Or from terminal:
cd test/api_logic_server_behave
behave
```

**Output:**
- `logs/behave.log` - Test execution summary
- `logs/scenario_logic_logs/<scenario>.log` - Logic execution trace for each scenario

**Prerequisites:**
- Server must be running (use "ApiLogicServer" launch config or `python api_logic_server_run.py`)

### Run Single Scenario (Debug)

Use Launch Configuration **"Behave Scenario"** - useful for:
- Debugging specific tests
- Setting breakpoints in test code
- Iterating on test development

## Generating Documentation

### Create Behave Logic Report

Run Launch Configuration **"Behave Report"**:

```bash
# Or from terminal:
cd test/api_logic_server_behave
python behave_logic_report.py run
```

**Output:**
- `reports/Behave Logic Report.md` - Complete wiki documentation

**What Gets Generated:**

1. **Test Results** - All scenarios with pass/fail status
2. **Logic Documentation** - Docstrings from `@when` steps
3. **Rules Used** - Which declarative rules fired during each scenario
4. **Logic Log** - Detailed execution trace showing rule chaining

### Example Output

```markdown
### Scenario: Good Order Custom Service
  Given Customer Account: ALFKI
  When Good Order Placed
  Then Logic adjusts Balance (demo: chain up)

<details>
**Logic Doc** for scenario: Good Order Custom Service
  Place an order with multiple items.
  This tests the complete dependency chain:
  - OrderDetail.UnitPrice copied from Product.UnitPrice
  - OrderDetail.Amount = Quantity * UnitPrice
  ...

**Rules Used** in Scenario:
  Rule.copy(OrderDetail.UnitPrice from Product.UnitPrice)
  Rule.formula(OrderDetail.Amount = Quantity * UnitPrice)
  Rule.sum(Order.AmountTotal from OrderDetail.Amount)
  Rule.sum(Customer.Balance from Order.AmountTotal)

**Logic Log** in Scenario:
  Logic Phase: ROW LOGIC
  ..OrderDetail[1040] {Insert - client}
  ....OrderDetail.UnitPrice [None-->18.0000000000] (copy from Product.UnitPrice)
  ....OrderDetail.Amount [None-->18.0000000000] (formula: Quantity * UnitPrice)
  ......Order.AmountTotal [1086-->1104] (sum OrderDetail.Amount)
  ........Customer.Balance [2102-->2120] (sum Order.AmountTotal)
</details>
```

## AI-Assisted Test Generation

When using AI (like Copilot) to generate tests from rules:

### CRITICAL: Multi-Step Process (Don't Skip Steps!)

**AI must complete these steps IN ORDER:**

1. **Read `database/models.py`** - Understand schema (ID types, column names, relationships)
2. **Read `logic/declare_logic.py`** - Understand which rules to test
3. **Query actual data OR plan test data creation** - Don't invent fictional IDs
4. **Create .feature files** - Using correct data types from step 1
5. **Implement steps/*.py** - Using actual IDs/data from step 3

### Prompt Pattern:

```
I need to create Behave tests for the declarative rules in this project.

Step 1: Please read database/models.py and tell me:
- What is the primary key type for Customer? (Integer, String, UUID?)
- What is the primary key type for Product?
- What is the primary key type for Order?
- What are the exact column names (balance vs Balance, customer_id vs CustomerId)?

Step 2: Please read logic/declare_logic.py and identify:
- Which rules need testing
- Which tables are involved in each rule
- What scenarios test the critical patterns (FK changes, where clauses, chains)

Step 3: How should we handle test data?
- Option A: Query existing data (show me the query)
- Option B: Create test data in environment.py (show me the code)
- Option C: Document required seed data (tell me what IDs to create manually)

Step 4: Generate the test files:
- .feature file with Given/When/Then scenarios
- steps/*.py implementation with correct data types and IDs

Follow patterns from docs/training/testing.md
```

### What AI Should Generate:

**For each rule, create tests covering:**

1. **Sum/Count rules:**
   - Basic: Child changes → Parent updates
   - Chain: Grandchild changes → Child → Parent
   - Where clause: Condition changes include/exclude from aggregate
   - Foreign key: Child moves to different parent → both parents adjust

2. **Formula rules:**
   - Basic: Input attributes change → Formula recalculates
   - Chain: Formula result affects parent sums

3. **Copy rules:**
   - Basic: Copies on insert
   - Foreign key change: Re-copies from new parent

4. **Constraint rules:**
   - Success: Valid data accepted
   - Failure: Invalid data rejected
   - Multiple paths: Test constraint from different entry points

5. **Event rules:**
   - Condition met: Event fires
   - Condition not met: Event doesn't fire

## Best Practices

### Naming Conventions

- **Feature files:** `<domain>.feature` (e.g., `place_order.feature`, `salary_change.feature`)
- **Step files:** Match feature name (e.g., `place_order.py`, `salary_change.py`)
- **Scenario names:** Descriptive, max 26 chars (truncated for log file names)

### Test Data Management

```python
# Save before state
@given('Customer Account: ALFKI')
def step_impl(context):
    context.alfki_before = get_customer('ALFKI')

# Verify changes
@then('Logic adjusts Balance')
def step_impl(context):
    before = context.alfki_before
    after = get_customer('ALFKI')
    assert after.Balance == expected_balance
```

### Docstring Guidelines

Include docstrings on `@when` steps explaining:
- What the test does
- Which rules are being tested
- What the expected chain of execution is
- Key takeaways about the logic

**Example:**
```python
@when('Good Order Placed')
def step_impl(context):
    """
    Place an order with multiple items.
    
    This tests the complete dependency chain:
    - OrderDetail.UnitPrice copied from Product.UnitPrice (Rule.copy)
    - OrderDetail.Amount = Quantity * UnitPrice (Rule.formula)
    - Order.AmountTotal = Sum(OrderDetail.Amount) (Rule.sum)
    - Customer.Balance = Sum(Order.AmountTotal where not shipped) (Rule.sum)
    
    > **Key Takeaway:** One transaction triggers multiple chained rules automatically
    """
```

### Test Organization

```
test/api_logic_server_behave/
  features/
    *.feature           # Natural language scenarios
    steps/
      *.py              # Test implementations
      test_utils.py     # Shared utilities
  logs/
    behave.log          # Test run summary
    scenario_logic_logs/
      *.log             # Logic trace for each scenario
  reports/
    Behave Logic Report.md  # Generated documentation
```

## Requirements Traceability

The Behave Logic Report provides complete traceability:

```
Business Requirement (Feature)
  ↓
Test Scenario (Given/When/Then)
  ↓
Test Implementation (Python code)
  ↓
Declarative Rules (5 lines)
  ↓
Execution Trace (Logic Log)
```

**This solves the traditional problem:**
- **Before:** Requirements → Code (opaque, 200+ lines)
- **Now:** Requirements → Tests → Rules → Trace (transparent, 5 lines)

The **44X advantage** extends to testing:
- Tests are simple API calls
- Business logic verified by checking which rules fired
- Complete audit trail from requirement to execution
- Living documentation auto-generated from test runs

## Example: Complete Test Flow

### 1. Identify Rule to Test

```python
# In logic/declare_logic.py
Rule.sum(derive=Customer.Balance, as_sum_of=Order.AmountTotal,
         where=lambda row: row.ShippedDate is None)
```

### 2. Create Scenario

```gherkin
# In features/place_order.feature
Scenario: Set Shipped - adjust logic reuse
  Given Customer Account: ALFKI
  When Order ShippedDate altered (2013-10-13)
  Then Balance reduced 1086
```

### 3. Implement Test

```python
# In features/steps/place_order.py
@when('Order ShippedDate altered (2013-10-13)')
def step_impl(context):
    """
    Set ShippedDate on an order.
    
    This removes the order from Customer.Balance calculation
    (due to where clause: ShippedDate is None).
    
    > **Key Takeaway:** Where clause conditions affect aggregate inclusion
    """
    scenario_name = 'Set Shipped - adjust logic reuse'
    test_utils.prt(f'\n{scenario_name}\n', scenario_name)
    
    patch_uri = 'http://localhost:5656/api/Order/10643/'
    patch_args = {
        "data": {
            "attributes": {"ShippedDate": "2013-10-13"},
            "type": "Order",
            "id": "10643"
        }
    }
    r = requests.patch(url=patch_uri, json=patch_args, headers=test_utils.login())
    context.response = r

@then('Balance reduced 1086')
def step_impl(context):
    before = context.alfki_before
    after = get_customer('ALFKI')
    expected_reduction = 1086
    assert after.Balance == before.Balance - expected_reduction
```

### 4. Run Tests

```bash
# Launch Configuration: "Behave Run"
# Generates logs/behave.log and logs/scenario_logic_logs/Set_Shipped_-_adjust_log.log
```

### 5. Generate Report

```bash
# Launch Configuration: "Behave Report"
# Creates reports/Behave Logic Report.md
```

### 6. Result

Documentation showing:
- ✅ Test passed
- ✅ Which rule was tested (sum with where clause)
- ✅ Detailed logic log showing Balance adjustment
- ✅ Complete traceability from requirement to execution

## Common Bugs and Solutions

### Debugging with Scenario Logic Logs

**When tests fail, check the scenario logic logs FIRST!**

**Location:** `test/api_logic_server_behave/logs/scenario_logic_logs/`

**What to look for:**

1. **Missing log files** - Scenario failed before creating any data:
   ```bash
   cd test/api_logic_server_behave/logs/scenario_logic_logs
   ls -lart | tail -20
   # If expected scenario log is missing or 0 bytes, failure occurred in GIVEN or WHEN step
   ```

2. **Empty (0 byte) log files** - Test data creation failed:
   ```bash
   ls -la | grep " 0 Oct"
   # Example: Good_Order_-_Basic_Chain.log (0 bytes)
   # Means: GIVEN or WHEN step failed before any logic executed
   ```

3. **Check recent logs** - Compare successful vs failed scenarios:
   ```bash
   # View a successful scenario log
   cat New_Order_Placed.log
   # Look for:
   # - Customer[ID] {Insert/Update}
   # - Order[ID] {Insert/Update}
   # - Rules fired (sum, formula, copy, constraint)
   # - Final values (balance, amount_total)
   ```

4. **Trace the logic execution:**
   - Each log shows the complete dependency chain
   - Look for which rules fired and in what order
   - Verify expected values in the logs
   - Check if constraint rules were checked

**Example - Successful scenario log shows:**
```
Logic Phase:		ROW LOGIC		(session=0x...) 
..Customer[10] {Insert - client} id: 10, name: Test Cust, balance: 0, credit_limit: 1000
..Order[10] {Insert - client} id: 10, customer_id: 10, amount_total: 0
..Item[10] {Insert - client} id: 10, order_id: 10, product_id: 6, quantity: 10
..Item[10] {copy_rules for role: product - unit_price} unit_price: 5.0
..Item[10] {Formula amount} amount: 50.0
....Order[10] {Update - Adjusting order: amount_total} amount_total: 50.0
......Customer[10] {Update - Adjusting Customer: balance} balance: 50.0

These Rules Fired:
  1. Derive Customer.balance as Sum(Order.amount_total Where not shipped)
  2. Derive Order.amount_total as Sum(Item.amount)
  3. Derive Item.amount as Formula(quantity * unit_price)
  4. Copy Item.unit_price from Product.unit_price
```

**Example - Failed scenario (empty log):**
- Indicates GIVEN or WHEN step failed
- Check test output for actual error (405, 404, assertion failure)
- Verify test data exists (customer_id, product_id valid)
- Check data types (integer vs string IDs)

**Workflow:**
1. Run tests: `python behave_run.py` (or "Behave Run" in VS Code)
2. Note which scenarios failed
3. Check logs: `ls -la test/api_logic_server_behave/logs/scenario_logic_logs/`
4. If log missing/empty → Problem in GIVEN/WHEN step (before logic)
5. If log has content → Problem in THEN assertion or logic execution
6. Compare with similar successful scenario logs

### Bug #1: "405 Method Not Allowed" on Login

**Symptom:**
```
Exception: POST login failed with <!doctype html>
405 Method Not Allowed
The method is not allowed for the requested URL.
```

**Cause:** Security mismatch
- Project has `SECURITY_ENABLED = false` in `config/default.env`
- But test tries to POST to `/auth/login` (endpoint doesn't exist without security)

**Root Cause:** `test_utils.login()` should detect this automatically, but Config may not be loading `default.env` correctly

**Why This Happens:**
- `config.py` uses `load_dotenv(path.join(basedir, "default.env"))` to load settings
- But **VS Code launch configurations can override environment variables!**
- Check `.vscode/launch.json` - the "Behave Run" config may have: `"env": {"SECURITY_ENABLED": "True"}`
- Environment variables from launch configs take precedence over `default.env`
- When tests import Config, they see the launch config's environment, not `default.env`

**Solutions:**
1. **Check `.vscode/launch.json`** - Verify "Behave Run" launch config matches project security:
   ```json
   {
       "name": "Behave Run",
       "env": {"SECURITY_ENABLED": "False"}  ← Must match default.env!
   }
   ```

2. **Use the correct launch config:**
   - **"Behave Run"** - Should match your project's security setting
   - **"  - Behave No Security"** - Forces security disabled (use for projects without security)

3. **Check `config/default.env`** - Verify `SECURITY_ENABLED` setting:
   ```bash
   grep SECURITY_ENABLED config/default.env
   # Should show: SECURITY_ENABLED = false (or True)
   ```

4. **Check for conflicting .env files:**
   ```bash
   find . -name ".env" -o -name "*.env"
   # Look for multiple .env files that might conflict
   ```

5. **Check environment variables:**
   ```bash
   env | grep SECURITY
   # Should show nothing, or match your intended setting
   ```

6. **Verify server started with correct security** - Check server startup logs:
   ```
   ALERT:  *** Security Not Enabled ***  ← Should match test expectations
   ```

7. **Debug Config loading in tests** - Add temporary debug to `test_utils.py`:
   ```python
   import os
   from config.config import Config
   print(f'DEBUG: os.getenv("SECURITY_ENABLED") = {os.getenv("SECURITY_ENABLED")}')
   print(f'DEBUG: Config.SECURITY_ENABLED = {Config.SECURITY_ENABLED}')
   ```

**How to verify:**
```bash
# From project root
cat config/default.env | grep SECURITY_ENABLED
# Should match whether server has /auth/login endpoint
curl http://localhost:5656/api/auth/login
# Should return 404 if security disabled, or require credentials if enabled
```

### Bug #2: Wrong Customer/Product/Order IDs

**Symptom:**
```
Exception: get_customer failed with {"errors": [{"title": "NotFoundError Invalid \"Customer\" ID \"CUST-1\""
```
Or:
```
{"errors": [{"title": "invalid literal for int() with base 10: 'CUST-1'", "code": "500"}]}
```

**Cause:** Tests use hardcoded fictional IDs that don't exist OR wrong data type

**Root Causes:**
1. **Invented IDs**: AI generated IDs like `'CUST-1'`, `'PROD-A'` without checking if they exist
2. **Wrong data type**: Used string `'CUST-1'` but table has integer ID (should be `1`)
3. **No test data**: Database is empty or doesn't have expected records

**Solutions:**

1. **First, check database schema** in `database/models.py`:
   ```python
   class Customer(Base):
       id = Column(Integer, primary_key=True)  # ← Integer! Use 1, 2, 3
       # NOT: id = Column(String, primary_key=True)  # ← Would use 'CUST-1', 'ALFKI'
   ```

2. **Query existing data** to find valid IDs:
   ```bash
   curl http://localhost:5656/api/Customer/?page[limit]=5 | jq '.data[] | {id, name}'
   ```

3. **Create test data helper**:
   ```python
   # In features/steps/test_helpers.py
   def get_or_create_test_customer():
       """Returns ID of test customer, creating if needed"""
       r = requests.get('http://localhost:5656/api/Customer/?page[limit]=1',
                       headers=test_utils.login())
       data = json.loads(r.text)
       if data['data']:
           return data['data'][0]['id']
       else:
           # Create test customer
           post_data = {
               "data": {
                   "attributes": {"name": "Test", "balance": 0, "credit_limit": 1000},
                   "type": "Customer"
               }
           }
           r = requests.post('http://localhost:5656/api/Customer/', 
                           json=post_data, headers=test_utils.login())
           return json.loads(r.text)['data']['id']
   ```

4. **Use environment hook** to create test data in `features/environment.py`:
   ```python
   def before_all(context):
       # Create test customer if doesn't exist
       context.test_customer_id = get_or_create_test_customer()
       context.test_product_id = get_or_create_test_product()
   ```

5. **Document required seed data** in `TEST_SUITE_OVERVIEW.md`:
   ```markdown
   ## Test Data Requirements
   
   Before running tests, ensure database has:
   - Customer ID 1: balance=0, credit_limit=1000
   - Product ID 1: unit_price=5.00
   - Product ID 2: unit_price=10.00
   
   Setup: Run `python database/test_data/seed.py`
   ```

**CRITICAL for AI:** Never invent fictional IDs! Always:
1. Read `database/models.py` to check ID data types
2. Query actual data OR create programmatically
3. Use real IDs in tests

### Bug #2a: Setting Aggregate Columns Directly

**Symptom:**
```
# Test creates customer with balance=950, but actual balance is 0
DEBUG: customer_id=10, actual_balance=0.0, expected=950
AssertionError: Customer balance should be 950, got 0.0
```
Or:
```
# Empty scenario log file - no logic executed
ls -la logs/scenario_logic_logs/Good_Order_-_Basic_Chain.log
-rw-r--r--  0 bytes
```

**Cause:** Trying to set an **aggregate column** directly instead of creating child data

**What are aggregates?**
- Columns computed by `Rule.sum()`, `Rule.count()`, or `Rule.formula()`
- Cannot be set directly by clients - only computed from child data
- Examples: `Customer.balance` (sum of orders), `Order.amount_total` (sum of items)

**Root Cause:**
```python
# ❌ WRONG - balance is an aggregate, can't set directly!
post_data = {
    "attributes": {
        "name": "Test Customer",
        "balance": 950,  # ← Ignored or rejected by server!
        "credit_limit": 1000
    }
}
r = requests.post(url=customer_uri, json=post_data)
# Result: Customer created with balance=0 (default), not 950
```

**How to identify aggregates:**
1. Check `logic/*.py` files for `Rule.sum`, `Rule.count`, `Rule.formula`:
   ```python
   Rule.sum(derive=Customer.balance, as_sum_of=Order.amount_total,
            where=lambda row: row.date_shipped is None)
   ```
2. Look in logic logs for `{server aggregate_defaults: balance}`
3. Common patterns: `balance`, `amount_total`, `order_count`, `units_in_stock`

**Solutions:**

1. **Create child data to reach desired aggregate:**
   ```python
   # ✅ CORRECT - Create customer, then orders to reach balance=950
   
   # Step 1: Create customer (balance defaults to 0)
   post_data = {
       "attributes": {
           "name": "Test Customer",
           # Don't set balance - it's computed!
           "credit_limit": 1000
       }
   }
   r = requests.post(url=customer_uri, json=post_data)
   customer_id = r.json()['data']['id']
   
   # Step 2: Create order with items to reach balance=950
   product_id = get_or_create_test_product(unit_price=1.00)
   order_id = create_test_order(customer_id, "Filler order")
   create_test_item(order_id, product_id, quantity=950)
   
   # Now customer.balance = 950 (computed by rules engine)
   ```

2. **RECOMMENDED: Keep helpers simple, create child data in step:**
   ```python
   # Helper: Simple - just creates customer
   def get_or_create_test_customer(name="Test", credit_limit=1000):
       """
       Create customer. Does NOT create filler orders.
       
       NOTE: balance parameter omitted - helper always creates with balance=0.
       Caller must create orders to reach target balance.
       """
       post_data = {
           "attributes": {
               "name": name,
               "credit_limit": credit_limit  # OK - regular column
               # NO balance - it's an aggregate!
           }
       }
       r = requests.post(url=customer_uri, json=post_data, headers=test_utils.login())
       return r.json()['data']['id']
   
   # Step: Creates customer AND child data to reach balance
   @given('Customer with balance {balance:d} and credit {credit:d}')
   def step_impl(context, balance, credit):
       # Create customer (balance=0)
       customer_id = get_or_create_test_customer(
           name=f"Test {balance}",
           credit_limit=credit
       )
       
       # If balance > 0, create filler order
       if balance > 0:
           product_id = get_or_create_test_product("Filler", 1.00)
           order_id = create_test_order(customer_id, "Filler")
           create_test_item(order_id, product_id, quantity=balance)
       
       context.customer_id = customer_id
   ```

3. **ALTERNATIVE: Helper creates child data (can cause issues):**
   ```python
   # ⚠️ More complex - helper creates filler orders automatically
   def get_or_create_test_customer(name, balance=0, credit_limit=1000):
       """Create customer with target balance by creating orders"""
       # Create customer
       post_data = {"attributes": {"name": name, "credit_limit": credit_limit}}
       r = requests.post(url=customer_uri, json=post_data)
       customer_id = r.json()['data']['id']
       
       # Create filler orders if needed
       if balance > 0:
           product_id = get_or_create_test_product("Filler", 1.00)  # ← Circular dep
           order_id = create_test_order(customer_id, "Filler")
           create_test_item(order_id, product_id, quantity=int(balance))
       
       return customer_id
   
   # Risks: Circular dependencies, harder to debug, hidden data creation
   ```

**Why keep helpers simple (option 2 recommended):**
- ✅ **Single responsibility** - helper creates entity, step creates relationships
- ✅ **No circular dependencies** - helper doesn't call other helpers
- ✅ **Clear test logic** - step shows exactly what data is created
- ✅ **Easier debugging** - full data creation visible in step
- ✅ **More flexible** - different tests create different structures

**Why this matters:**
- ✅ **Aggregates reflect reality** - balance comes from actual orders
- ✅ **Tests the rules** - verifies aggregates compute correctly  
- ✅ **Server enforces** - API may reject/ignore aggregate values
- ✅ **Prevents silent bugs** - balance=0 instead of expected value

**Debugging:**
```bash
# Check if column is an aggregate
grep -r "balance" logic/*.py
# If you see: Rule.sum(derive=Customer.balance, ...)
# Then: balance is an aggregate - create child data!

# Verify aggregate computed correctly
curl http://localhost:5656/api/Customer/10 | jq '.data.attributes.balance'
# Compare to sum of orders
curl http://localhost:5656/api/Order/?filter[customer_id]=10 | jq '[.data[].attributes.amount_total] | add'
```

**CRITICAL for AI:** Before setting any column in test data:
1. ✅ Check if it appears in `Rule.sum()`, `Rule.count()`, `Rule.formula()`
2. ✅ If yes → Create child data instead of setting directly
3. ✅ If no → Safe to set directly

### Bug #2b: JSON Returns String IDs, Database Expects Integers

**Symptom:**
```
DEBUG GIVEN: Got customer_id=8, type=<class 'str'>
DEBUG WHEN: ERROR Response={"errors": [{"title": "Validation Error: Invalid relationship payload: [{'product_id': '7', 'quantity': 10}]"
```
Or:
```
TypeError: '>=' not supported between instances of 'str' and 'int'
```

**Cause:** JSON API returns IDs as **strings**, but database schema expects **integers**

**Why This Happens:**
- JSON has no integer type - all numbers become strings when serialized
- API returns: `{"data": {"id": "123"}}` ← String "123"
- Database expects: `customer_id = 123` ← Integer 123
- Passing string ID to API causes: `"Invalid relationship payload"`

**Root Cause:**
```python
# ❌ WRONG - Returns string ID from JSON
def get_or_create_test_customer(...):
    r = requests.post(url=customer_uri, json=post_data)
    result = json.loads(r.text)
    return result['data']['id']  # ← Returns string "8", not int 8!

# Result: customer_id = "8" (string)
# When used in POST: {"customer_id": "8"} ← API rejects this!
```

**The Fix - Always Convert JSON IDs to int:**
```python
# ✅ CORRECT - Convert to int before returning
def get_or_create_test_customer(...):
    r = requests.post(url=customer_uri, json=post_data, headers=test_utils.login())
    result = json.loads(r.text)
    return int(result['data']['id'])  # ← Convert to int!

# Also when querying:
def get_customer_id():
    r = requests.get(url=customer_uri, headers=test_utils.login())
    data = json.loads(r.text)
    return int(data['data'][0]['id'])  # ← Convert to int!
```

**Apply to ALL helper functions:**
```python
# Every function that returns an ID must convert to int:

def get_or_create_test_customer(...) -> int:
    # ...
    return int(result['data']['id'])  # ← int()

def get_or_create_test_product(...) -> int:
    # ...
    return int(result['data']['id'])  # ← int()

def create_test_order(...) -> int:
    # ...
    return int(result['data']['id'])  # ← int()

def create_test_item(...) -> int:
    # ...
    return int(result['data']['id'])  # ← int()

def get_customer(customer_id: int) -> dict:
    # Query still works with int - API converts it
    r = requests.get(f'http://localhost:5656/api/Customer/{customer_id}/')
    # customer_id can be int, URL will be .../Customer/8/
```

**Why This Matters:**
- ✅ **Database schema compliance** - IDs match column types
- ✅ **API validation** - Relationships accept correct types
- ✅ **Type safety** - Prevents string/int comparison errors
- ✅ **Consistent behavior** - All IDs are integers throughout

**How to Verify:**
```python
# Add debug to check types
customer_id = get_or_create_test_customer(...)
print(f"customer_id={customer_id}, type={type(customer_id)}")
# Should show: customer_id=8, type=<class 'int'>
# NOT: customer_id=8, type=<class 'str'>
```

**Pattern to Follow:**
```python
# EVERY time you extract an ID from JSON response:
result = json.loads(r.text)

# ❌ WRONG:
id = result['data']['id']

# ✅ CORRECT:
id = int(result['data']['id'])

# Or from query results:
# ❌ WRONG:
id = data['data'][0]['id']

# ✅ CORRECT:
id = int(data['data'][0]['id'])
```

**CRITICAL for AI:** 
- Always wrap `result['data']['id']` with `int()`
- JSON APIs return strings, databases expect integers
- This applies to ALL ID fields: customer_id, product_id, order_id, item_id
- Type annotations (`-> int`) remind you to convert

### Bug #2c: Nested Relationship Creation Not Supported

**Symptom:**
```
DEBUG WHEN: ERROR Response={"errors": [{"title": "Validation Error: Invalid relationship payload: [{'product_id': 7, 'quantity': 10}]"
```

**Cause:** Trying to create child records (Items) nested in parent POST (Order)

**Why This Happens:**
- SAFRS/JSONAPI may not support nested creation of relationships in all cases
- Attempting to POST Order with embedded ItemList fails validation
- API expects separate POST requests for parent and children

**Root Cause:**
```python
# ❌ WRONG - Trying to create Order with nested Items in one POST
post_data = {
    "data": {
        "attributes": {
            "customer_id": customer_id,
            "notes": "Test Order",
            "ItemList": [  # ← Nested child creation - may not work!
                {"product_id": product_id, "quantity": 10}
            ]
        },
        "type": "Order"
    }
}
r = requests.post('http://localhost:5656/api/Order/', json=post_data)
# Result: 400 Validation Error: Invalid relationship payload
```

**The Fix - Create Parent First, Then Children:**
```python
# ✅ CORRECT - Create Order first, then create Items separately

# Step 1: Create Order (parent)
order_id = create_test_order(customer_id, "Test Order")

# Step 2: Create Item (child) - triggers full dependency chain
item_id = create_test_item(order_id, product_id, quantity=10)

# Helper functions:
def create_test_order(customer_id: int, notes: str) -> int:
    """Create order without items"""
    post_data = {
        "data": {
            "attributes": {
                "customer_id": customer_id,
                "notes": notes
                # No ItemList here!
            },
            "type": "Order"
        }
    }
    r = requests.post('http://localhost:5656/api/Order/', json=post_data, 
                     headers=test_utils.login())
    return int(r.json()['data']['id'])

def create_test_item(order_id: int, product_id: int, quantity: int) -> int:
    """Create item - separate POST"""
    post_data = {
        "data": {
            "attributes": {
                "order_id": order_id,
                "product_id": product_id,
                "quantity": quantity
            },
            "type": "Item"
        }
    }
    r = requests.post('http://localhost:5656/api/Item/', json=post_data,
                     headers=test_utils.login())
    return int(r.json()['data']['id'])
```

**In Test Steps:**
```python
@when('New order placed with 1 item (qty {qty:d}, product price {price:f})')
def step_impl(context, qty, price):
    # Create product
    product_id = get_or_create_test_product(f"Product ${price}", price)
    
    # Create order (parent) - separate POST
    order_id = create_test_order(context.customer_id, "Test Order")
    
    # Create item (child) - separate POST, triggers dependency chain
    item_id = create_test_item(order_id, product_id, quantity=qty)
    
    # Now the rules have fired:
    # - Item.unit_price copied from Product
    # - Item.amount = quantity * unit_price
    # - Order.amount_total = sum(Item.amount)
    # - Customer.balance = sum(Order.amount_total)
    
    context.order_id = order_id
    context.item_id = item_id
```

**Why This Matters:**
- ✅ **Works reliably** - Separate POSTs are always supported
- ✅ **Triggers rules correctly** - Each insert fires its own rule cascade
- ✅ **Easier debugging** - Can see each creation step separately
- ✅ **Standard pattern** - Matches typical API usage

**Alternative APIs May Support Nested Creation:**
Some APIs might support nested creation with different syntax:
```python
# May work with some frameworks (not guaranteed):
"relationships": {
    "ItemList": {
        "data": [
            {"type": "Item", "attributes": {"product_id": 7, "quantity": 10}}
        ]
    }
}
```

**But the safest approach is always: Parent first, then children.**

**CRITICAL for AI:**
- ❌ Don't assume nested creation works
- ✅ Always create parent first (Order)
- ✅ Then create children separately (Items)
- ✅ Each POST is independent and triggers its own rules
- ✅ Use helper functions: `create_test_order()` then `create_test_item()`

### Bug #3: Ambiguous Step Definitions

**Symptom:**
```
Exception AmbiguousStep: @when('Order date_shipped set to today') 
has already been defined in existing step @when(...) at features/steps/check_credit.py:237
```

**Cause:** Same `@given/@when/@then` decorator defined in multiple step files

**Solution:** Remove duplicate step definitions
- Behave pools ALL steps from ALL step files globally
- Any scenario can use any step from any file
- Each step must be defined only ONCE

**Example Fix:**
```python
# WRONG: Same step in check_credit.py AND app_integration.py
# File: check_credit.py
@when('Order date_shipped set to today')
def step_impl(context):
    pass

# File: app_integration.py
@when('Order date_shipped set to today')  # <-- DUPLICATE!
def step_impl(context):
    pass

# CORRECT: Define once, use everywhere
# File: check_credit.py
@when('Order date_shipped set to today')
def step_impl(context):
    pass

# File: app_integration.py
# No duplicate - reuses step from check_credit.py!
```

### Bug #3a: Test Data Contamination from Previous Runs

**Symptom:**
```
DEBUG: customer_id=8, actual_balance=100.0, expected=50
AssertionError: Customer balance should be 50, got 100.0
```

**Cause:** Reusing existing customers/data from previous test runs

**Why This Happens:**
- Helper finds existing customer by name and reuses it
- That customer has orders from previous test runs
- Balance includes orders from BOTH current AND previous tests
- Expected: balance=50 (from current test), Actual: balance=100 (current + previous)

**Root Cause:**
```python
# ❌ WRONG - Queries for existing customer by name
def get_or_create_test_customer(name="Test Customer", ...):
    r = requests.get(f'http://localhost:5656/api/Customer/?filter[name]={name}')
    data = r.json()
    if data['data']:
        return int(data['data'][0]['id'])  # ← Reuses customer from previous run!
    # Customer might have orders from last test run
```

**The Fix - Always Create Fresh Test Data:**
```python
# ✅ CORRECT - Always creates NEW customer with unique name
import time

def get_or_create_test_customer(name="Test Customer", balance=0, credit_limit=1000) -> int:
    """Create a NEW test customer (always creates, never reuses)."""
    
    # Add timestamp to ensure uniqueness
    unique_name = f"{name} {int(time.time() * 1000)}"
    
    post_data = {
        "data": {
            "attributes": {
                "name": unique_name,  # Unique name every time!
                "credit_limit": credit_limit
            },
            "type": "Customer"
        }
    }
    r = requests.post(url=customer_uri, json=post_data, headers=test_utils.login())
    return int(r.json()['data']['id'])
    
    # Fresh customer with balance=0, no leftover orders
```

**Why This Matters:**
- ✅ **Test isolation** - Each test runs independently
- ✅ **Repeatable** - Same results every time
- ✅ **Order independent** - Tests can run in any sequence
- ✅ **No cleanup needed** - Fresh data each time
- ✅ **Clear assertions** - Know exactly what data exists

**CRITICAL for AI:**
- ❌ Don't reuse existing test data (leads to contamination)
- ✅ Always create fresh data with unique identifiers
- ✅ Add timestamps to names for uniqueness: `f"{name} {int(time.time() * 1000)}"`
- ✅ Each scenario gets completely new entities
- ✅ Tests must be independent and repeatable

### Bug #4: Assertion Failures with Wrong Expected Values

**Symptom:**
```
AssertionError: Before balance 0 + 50 != new Balance 55
```

**Cause:** Test expects wrong values because:
- Copy rule changed `UnitPrice`
- Where clause excluded/included unexpected orders
- Test data wasn't in expected state

**Solutions:**
1. **Run test once with debug output** to see actual values:
   ```python
   print(f'DEBUG: before={before.Balance}, after={after.Balance}')
   ```
2. **Check Logic Log** in `logs/scenario_logic_logs/` to see which rules fired
3. **Verify test data state** before running scenario
4. **Update expected values** based on actual rule execution

### Bug #4a: WHEN Step Throws Exception on Expected Constraint Violations

**Symptom:**
```
Exception: Failed to create item: 400 - {"errors": [{"title": "Customer balance exceeds credit limit"
Scenario: Bad Order - Exceeds Credit
  When New order placed with 1 item (qty 20, product price 10.00)
  Then Rejected per Check Credit  # ← Never reached! WHEN step crashed!
```

**Cause:** Helper function raises exception when API returns error, but constraint violation is **expected behavior** for negative test scenarios

**The Fix - Catch Expected Errors in WHEN Steps:**
```python
# ✅ CORRECT - WHEN step catches constraint violations
@when('New order placed with 1 item (qty {qty:d}, product price {price:f})')
def step_impl(context, qty, price):
    """Place new order - may succeed or fail due to constraint"""
    
    # Create product and order
    product_id = get_or_create_test_product(f"Product ${price}", price)
    order_id = create_test_order(context.customer_id, "Test Order")
    
    # Create item - may fail due to constraint!
    try:
        item_id = create_test_item(order_id, product_id, quantity=qty)
        # Success
        context.response = type('obj', (object,), {'status_code': 200, 'text': ''})()
        context.item_id = item_id
    except Exception as e:
        # Constraint violation (expected for negative tests)
        if "400" in str(e):
            context.response = type('obj', (object,), {'status_code': 400, 'text': str(e)})()
        else:
            raise  # Re-raise if unexpected error
```

**THEN Step Verifies Rejection:**
```python
@then('Rejected per Check Credit')
def step_impl(context):
    assert context.response.status_code > 300, 'Request should fail'
    assert 'credit' in context.response.text.lower(), 'Error should mention credit'
```

**CRITICAL for AI:**
- ✅ Use try/except in WHEN steps for scenarios that may fail
- ✅ Store both success and error responses in `context.response`
- ✅ THEN steps verify expected outcome (success OR rejection)
- ✅ Negative tests validate constraints work correctly

### Bug #5: Tests Pass But Logic Log Empty

**Symptom:** Tests pass, but `logs/scenario_logic_logs/` is empty or incomplete

**Cause:** Missing `test_utils.prt()` call with scenario name

**Solution:** Ensure EVERY `@when` step includes:
```python
@when('Some action happens')
def step_impl(context):
    scenario_name = 'Some Action Happens'  # <-- Required!
    test_utils.prt(f'\n{scenario_name}\n', scenario_name)  # <-- 2nd arg is key!
    # ... rest of test
```

**Why:** The 2nd argument to `test_utils.prt()` controls Logic Log file naming

## Summary

**Creating tests from rules provides:**

1. **Correctness verification** - Ensures rules work as intended
2. **Dependency chain validation** - Tests transitive effects (Product → Item → Order → Customer)
3. **Foreign key change testing** - Verifies old/new parent adjustments (the "missed bugs")
4. **Automated documentation** - Living documentation with complete traceability
5. **Regression prevention** - Executable test suite protects against future breaks

**The key insight:** Declarative rules make testing **dramatically simpler** because:
- Tests focus on "what" not "how"
- Rule execution is logged automatically
- Dependency chains are traced automatically
- Complete audit trail from requirement to execution

**For more examples:** See `test/api_logic_server_behave/` in this project and the published [Behave Logic Report](https://apilogicserver.github.io/Docs/Behave-Logic-Report/).
