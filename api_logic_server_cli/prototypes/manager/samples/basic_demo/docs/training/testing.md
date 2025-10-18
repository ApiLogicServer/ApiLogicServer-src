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

**F. DELETE Operations (Often Forgotten!):**
- Deleting `OrderDetail` → decreases `Order.AmountTotal` → decreases `Customer.Balance`
- Deleting `Order` → removes from `Customer.Balance` aggregate
- Verify aggregates adjust **downward** correctly (not just upward)

**G. WHERE Clause Bidirectional Testing (Critical!):**
- Test both **adding** and **removing** rows from aggregate:
  - Setting `Order.ShippedDate = today` → excludes from balance (WHERE fails)
  - Setting `Order.ShippedDate = None` → includes in balance (WHERE passes)
- WHERE clauses should work **both directions** (not just one-way)

**H. All CRUD Operations:**
- **POST (Create)** - New entities trigger rules
- **PATCH (Update)** - Modified entities trigger recalculation
- **DELETE (Delete)** - Removed entities adjust aggregates downward
- **GET (Read)** - Verify all changes applied correctly

**CRITICAL: Don't just test happy path!** Test:
- ✅ Good order (passes constraint)
- ✅ Bad order (exceeds credit - rejected)
- ✅ Quantity increase (balance increases)
- ✅ Quantity decrease (balance decreases)
- ✅ Product change (re-copy unit_price)
- ✅ Customer change (both balances adjust)
- ✅ Ship order (exclude from balance)
- ✅ **Unship order** (include back in balance) ← Often missed!
- ✅ **Delete item** (balance decreases) ← Often missed!

**Common Mistake:** Only testing POST and PATCH, forgetting DELETE and WHERE bidirectionality.

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

## CRITICAL: AI Test Creation Rules (Read This FIRST!)

**Purpose:** These 6 mandatory rules prevent 90% of test failures. Follow them BEFORE writing any test code.

---

### Rule #1: ALWAYS Read Database Schema First

**Before writing ANY test code, read `database/models.py` to understand:**

1. **Primary key types** - Integer vs String determines how you pass IDs
2. **Column names** - Use exact names from schema
3. **Relationships** - Understand FK column names (customer_id, product_id, etc.)
4. **Aggregates** - Identify computed columns (balance, items_count, etc.)

**Example:**
```python
# Read database/models.py first:
class Customer(Base):
    __tablename__ = 'customer'
    id = Column(Integer, primary_key=True)  # ← Integer, not String!
    name = Column(String)
    balance = Column(Numeric)  # ← Check logic files - is this an aggregate?
    credit_limit = Column(Numeric)

class Order(Base):
    __tablename__ = 'order'
    id = Column(Integer, primary_key=True)
    customer_id = Column(Integer, ForeignKey('customer.id'))  # ← FK column name
    amount_total = Column(Numeric)  # ← Likely an aggregate (sum of items)
```

**Then check `logic/declare_logic.py` for aggregates:**
```python
Rule.sum(derive=Customer.balance, as_sum_of=Order.amount_total,
         where=lambda row: row.date_shipped is None)  # ← balance IS an aggregate!
Rule.sum(derive=Order.amount_total, as_sum_of=Item.amount)  # ← amount_total IS an aggregate!
```

**This prevents these bugs:**
- ❌ **Wrong IDs** - Using "ALFKI" when DB expects Integer 1
- ❌ **Setting aggregates directly** - Trying to PATCH `balance` when it's computed from Orders
- ❌ **String vs Int confusion** - JSON returns "123" but DB expects int(123)
- ❌ **Wrong column names** - Using `customer` instead of `customer_id`

**Golden Rule:** Never set aggregate columns directly. Create/modify child entities instead.

---

### Rule #2: ALWAYS Use Direct FK Format (Not Relationships)

**For ALL POST and PATCH operations, use direct foreign key format in attributes:**

```python
# ✅ CORRECT - Direct FK in attributes
post_data = {
    "data": {
        "type": "Order",
        "attributes": {
            "customer_id": int(customer_id),  # Direct FK, converted to int
            "date_shipped": None,             # Explicit null values
            "notes": "Test order"
        }
    }
}

# ❌ WRONG - Relationships format causes optimistic locking errors
post_data = {
    "data": {
        "type": "Order",
        "relationships": {
            "customer": {
                "data": {"type": "Customer", "id": customer_id}
            }
        },
        "attributes": {
            "notes": "Test order"
        }
    }
}
```

**Why?** The relationships format triggers validation on newly-created rows that aren't yet "loaded_as_persistent", causing optimistic locking errors: "Sorry, row altered by another user".

**This prevents these bugs:**
- ❌ **Optimistic locking errors** - "Sorry, row altered by another user"
- ❌ **String vs Int confusion** - Relationships hide the type conversion
- ❌ **Nested relationship errors** - Creating customer while creating order

**Golden Rule:** Always use `"customer_id": int(id)` in attributes, never use relationships.

---

### Rule #3: Mandatory Test Code Patterns

**Follow these 6 patterns in EVERY test file:**

#### Pattern 1: Filter Format (JSON:API Standard)
```python
# ✅ CORRECT - JSON:API filter format
params = {"filter[name]": "Alice"}
params = {"filter[id]": customer_id}

# ❌ WRONG - OData format
params = {"filter": "name eq 'Alice'"}
params = {"$filter": "id eq 1"}
```

#### Pattern 2: Create Fresh Test Data
```python
# ✅ CORRECT - Unique timestamp for every test run
customer_name = f"Test Customer {int(time.time() * 1000)}"

# ❌ WRONG - Reusing same name causes contamination
customer_name = "Test Customer"
```

#### Pattern 3: Convert All IDs to Integer
```python
# ✅ CORRECT - JSON returns strings, DB expects ints
customer_id = int(result['data']['id'])
order_id = int(order_result['data']['id'])

# ❌ WRONG - Passing string IDs
customer_id = result['data']['id']  # This is "123", not 123
```

#### Pattern 4: No Circular Imports
```python
# ✅ CORRECT - Only these imports in test files
from behave import *
import requests
import test_utils
from decimal import Decimal
import time

# ❌ WRONG - These cause circular import errors
from logic import declare_logic  # NO!
from database import models      # NO!
from integration import kafka    # NO!
```

#### Pattern 5: Execute Steps Correctly
```python
# ✅ CORRECT - Use context.execute_steps()
context.execute_steps('''
    when Good Order Placed
    then Balance is 1000
''')

# ❌ WRONG - Direct function calls break Behave
step_impl.execute_step(context)
```

#### Pattern 6: Null-Safe Constraint Rules
```python
# ✅ CORRECT - Always check None first
Rule.constraint(validate=Customer,
    as_condition=lambda row: row.balance is None or 
                             row.credit_limit is None or 
                             row.balance <= row.credit_limit,
    error_msg="Balance ({row.balance}) exceeds credit limit ({row.credit_limit})")

# ❌ WRONG - Fails when balance or credit_limit is None
Rule.constraint(validate=Customer,
    as_condition=lambda row: row.balance <= row.credit_limit,
    error_msg="Balance exceeds credit limit")
```

**This prevents these bugs:**
- ❌ **Filter validation errors** - Invalid filter format
- ❌ **Test data contamination** - Tests fail on second run
- ❌ **String ID errors** - "invalid literal for int()"
- ❌ **Circular import errors** - ImportError at runtime
- ❌ **Step execution failures** - Steps don't run
- ❌ **Null pointer errors** - Constraint fails on None values

---

### Rule #4: Complete CRUD + WHERE Coverage

**Every test suite MUST include these scenario types:**

```gherkin
# ✅ CREATE (POST)
Scenario: Good Order Placed
  When Good Order Placed
  Then Balance is 1000

# ✅ UPDATE (PATCH) - Multiple variations
Scenario: Item Quantity Change
  When Item Quantity Changed to 10
  Then Balance is 2000

Scenario: Item Product Change
  When Item Product Changed
  Then Balance is 500

Scenario: Change Customer
  When Order Customer Changed
  Then Original Customer Balance is 0
  And New Customer Balance is 1000

# ✅ DELETE
Scenario: Delete Item
  When Item is Deleted
  Then Balance is 0

# ✅ WHERE clause - Bidirectional testing
Scenario: Order Shipped (exclude from balance)
  When Order Shipped
  Then Balance is 0

Scenario: Reset Shipped (include in balance)
  When Order Unshipped
  Then Balance is 1000

# ✅ Constraint - Pass AND Fail
Scenario: Order Exceeds Credit Limit
  When Order Placed Exceeding Credit
  Then Error Raised "Balance (1100.00) exceeds credit limit (1000)"
```

**This prevents these bugs:**
- ❌ **Incomplete testing** - Missing DELETE or WHERE scenarios
- ❌ **One-directional WHERE testing** - Only testing ship, not unship
- ❌ **No constraint failure testing** - Only testing happy path

**Golden Rule:** Test ALL CRUD operations + WHERE bidirectional + constraint pass/fail.

---

### Rule #5: Security & Environment Awareness

**Always check `config/default.env` FIRST to understand security settings:**

```python
# Read config/default.env:
SECURITY_ENABLED = False  # ← Key setting!

# If SECURITY_ENABLED = False:
@given('Login')
def step_impl(context):
    context.headers = {}  # Empty headers, no auth needed

# If SECURITY_ENABLED = True:
@given('Login')
def step_impl(context):
    context.headers = test_utils.login()  # Returns actual auth token
```

**Common security configuration:**
```bash
# config/default.env
SECURITY_ENABLED = False     # ← Basic demo has security disabled
SECURITY_PROVIDER = None
```

**This prevents these bugs:**
- ❌ **405 Method Not Allowed** - Trying to call /auth/login when security is disabled
- ❌ **401 Unauthorized** - Missing auth headers when security is enabled

**Golden Rule:** Match your test code to the SECURITY_ENABLED setting.

---

### Rule #6: Logic Logging for Documentation

**Every WHEN step must include logging to generate documentation:**

```python
@when('Good Order Placed')
def step_impl(context):
    scenario_name = 'Good Order Placed'
    
    # ✅ CORRECT - Second argument is critical for scenario grouping
    test_utils.prt(f'\n{scenario_name}\n', scenario_name)
    
    # Create order...
    post_data = {...}
    result = requests.post(...)
    
    # ❌ WRONG - Missing second argument, logic log is empty
    test_utils.prt(f'\n{scenario_name}\n')
```

**Why?** The second argument to `test_utils.prt()` groups logic log entries by scenario, enabling the "Behave Logic Report" to show which rules were tested.

**This prevents these bugs:**
- ❌ **Empty logic logs** - Report shows "No logic log found"
- ❌ **Ungrouped logs** - Can't trace which rule fired for which scenario

**Golden Rule:** Always pass scenario name as both first AND second argument to prt().

---

## Quick Error Lookup

**If you still hit errors after following the 6 rules, check this table:**

| Error Message | Instant Fix |
|--------------|-------------|
| "405 Method Not Allowed on /auth/login" | Server has `SECURITY_ENABLED = False`, remove auth calls |
| "invalid literal for int() with base 10: 'ALFKI'" | Check `database/models.py` for actual ID type, likely Integer not String |
| "balance: field not writable" | `balance` is an aggregate - create/modify child Orders, don't PATCH balance directly |
| "Validation Error: Invalid filter format" | Use `filter[name]=value` not OData `filter="name eq 'value'"` |
| "Sorry, row altered by another user" | Use direct FK in attributes: `"customer_id": int(id)` not relationships format |
| "ImportError: circular import" | Remove imports from `logic/`, `database/`, `integration/` - only import `behave`, `requests`, `test_utils` |
| "Test passes but logic log empty" | Add `test_utils.prt(msg, scenario_name)` with 2nd argument |
| "TypeError: '<' not supported between 'NoneType' and 'Decimal'" | Add None checks in constraints: `row.x is None or row.y is None or row.x < row.y` |

---

## Common Bugs and Solutions (OPTIONAL REFERENCE)

**Note:** If you followed the 6 rules above, you should rarely need this section. It's kept for complex edge cases.
- [ ] Used `context.execute_steps()` for step reuse
- [ ] Created fresh test data with `f"{name} {int(time.time()*1000)}"`
- [ ] Restarted server after changing `logic/declare_logic.py`

**See detailed fixes below ↓**

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

---

### Complex Edge Cases (Only if Rules Aren't Enough)

**Most bugs are prevented by following the 6 CRITICAL RULES above.** This section covers rare edge cases.

#### Environment Variable Conflicts

**Symptom:** "405 Method Not Allowed" on `/auth/login` even though `default.env` has `SECURITY_ENABLED = False`

**Cause:** VS Code launch configurations override `.env` files!

**Fix:**
```json
// Check .vscode/launch.json
{
    "name": "Behave Run",
    "env": {"SECURITY_ENABLED": "False"}  // ← Must match default.env!
}
```

**Debug:**
```bash
grep SECURITY_ENABLED config/default.env  # Check project setting
curl http://localhost:5656/api/auth/login # 404 if security disabled
```

#### VS Code Launch Configuration Overrides

**If tests behave differently in VS Code vs terminal:**
1. Check `.vscode/launch.json` for `"env"` overrides
2. Verify launch config name matches test type ("Behave Run", "Behave No Security")
3. Environment variables from launch configs take precedence over `.env` files

---

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
