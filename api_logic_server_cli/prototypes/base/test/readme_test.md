# API Logic Server Testing Guide

## Overview

This directory contains comprehensive tests for API Logic Server projects, designed to validate business logic rules, API endpoints, security, and data integrity. The testing framework emphasizes **business logic validation** through declarative rules rather than just basic CRUD operations.

## 🎯 What Gets Tested

- **Business Logic Rules**: Declarative rules for sums, formulas, constraints, and events
- **API Endpoints**: REST API functionality and JSON:API compliance
- **Security**: Authentication, authorization, and role-based access control
- **Data Integrity**: Database constraints, cascading updates, and transactions
- **Integration**: Logic engine, database, and API layer integration

## 📁 Test Structure

```
test/
├── readme_test.md                 # This guide
├── api_logic_server_behave/       # Primary BDD testing framework
│   ├── behave_run.py             # Main test runner
│   ├── behave_logic_report.py    # Report generator
│   ├── features/                 # Gherkin feature files
│   │   ├── *.feature            # Business logic test scenarios
│   │   └── steps/               # Python step implementations
│   ├── logs/                    # Test execution logs
│   └── reports/                 # Generated test reports
└── basic/                       # Simple server tests
    ├── server_test.py           # Basic API functionality tests
    └── results/                 # Basic test results
```

## 🚀 Running Tests

### Prerequisites
1. **Start API Logic Server**: `python api_logic_server_run.py` or press F5
2. **Install behave**: `pip install behave` (if not already installed)
3. **Database State**: Tests restore data automatically, but if tests fail mid-execution, restore your database from backup

### Primary Testing Method: Behave (BDD)

```bash
# From project root
cd test/api_logic_server_behave
python behave_run.py

# Or in VS Code
# Use "Behave Run" configuration (F5)
# In Debug Console, select "Behave Run" from dropdown (not server log)
```

### Alternative: Basic Server Tests

```bash
# From project root
cd test/basic
python server_test.py go
```

**Note**: Basic tests require `SECURITY_ENABLED = False` in `config/config.py`

## 📝 Common Test Scenarios

API Logic Server projects typically test these business patterns:

### Core Business Logic
- **State Management**: Entity status changes and their cascading effects
- **Credit/Limit Checking**: Validation against business constraints
- **Balance/Total Calculations**: Automatic sum and formula derivations
- **Inventory/Resource Management**: Allocation and availability tracking
- **Notifications**: Email alerts and external system integration
- **Constraint Validation**: Business rule enforcement

*Example: In Northwind, order ready/not-ready states affect customer balances through automatic sum rules.*

### Entity Management
- **Audit Trails**: Automatic logging of critical changes
- **Derived Attributes**: Calculated fields and transformations
- **Business Rules**: Validation and constraint enforcement

*Example: Employee salary changes create audit records and validate minimum raise amounts.*

### Security Testing
- **Authentication**: Login/logout functionality
- **Role-Based Access**: Permission validation
- **Data Filtering**: Row-level security based on user roles

## 🧪 Test Data Strategy

### Testing Business Logic Derivations

**Best Practice for Derivation Testing:**

When testing business logic derivations (sums, formulas, constraints), follow this pattern:

1. **Read Initial State**: Capture the starting values before the transaction
2. **Execute Transaction**: Perform the business operation (create order, update quantity, etc.)
3. **Read Final State**: Capture the resulting values after business logic execution
4. **Compare Changes**: Verify the differences match expected derivation behavior

```python
@when('Customer places order for ${amount:d}')
def step_impl(context, amount):
    # 1. Read initial state
    customer_response = requests.get(f"{BASE_URL}/api/Customer/1")
    context.initial_balance = customer_response.json()['data']['attributes']['balance']
    
    # 2. Execute transaction
    order_data = {"customer_id": 1, "amount_total": amount}
    context.response = requests.post(f"{BASE_URL}/api/Order", json=order_data)
    
@then('Customer balance increases by ${expected_increase:d}')
def step_impl(context, expected_increase):
    # 3. Read final state
    customer_response = requests.get(f"{BASE_URL}/api/Customer/1")
    final_balance = customer_response.json()['data']['attributes']['balance']
    
    # 4. Compare changes
    actual_increase = final_balance - context.initial_balance
    assert actual_increase == expected_increase, f"Balance changed by {actual_increase}, expected {expected_increase}"
```

**Why This Approach Works:**
- ✅ **Independent of Initial Data**: Tests work regardless of starting database state
- ✅ **Focuses on Business Logic**: Verifies the rule behavior, not absolute values
- ✅ **Robust Against Multiple Runs**: Tests remain valid after repeated execution
- ✅ **Clear Intent**: Shows exactly what the business rule should accomplish

### Identifying Test Data
When creating tests, identify stable test entities in your database:

1. **Key Business Entities**: Main domain objects (customers, orders, products, etc.)
2. **Known State**: Entities with predictable initial values
3. **Relationships**: Connected entities that demonstrate rule cascading
4. **Edge Cases**: Boundary conditions for constraints and validations

### Test Data Documentation
Document your test data in comments or separate files:

```python
"""
Test Data Used:
- Primary Customer: [CustomerID] with [known balance/status]
- Test Order: [OrderID] with [known amount]
- Test Employee: [EmployeeID] with [known salary]
- Constraint Limits: [specific values that trigger validations]
"""
```

## 🔧 For Developers

### Adding New Tests

1. **Identify Business Scenario**: What business rule or process needs testing?
2. **Create Feature File**: Add `.feature` file in `features/` using Gherkin syntax
3. **Implement Steps**: Create corresponding `.py` file in `features/steps/`
4. **Use Test Utilities**: Import `test_utils.py` for common functions
5. **Follow Patterns**: Reference existing tests for authentication, logging, and assertions

### Generic Feature Structure

```gherkin
Feature: [Business Process Name]

  Scenario: [Specific Business Rule Test]
     Given [Initial business state]
      When [Business action is performed]
      Then [Expected business outcome occurs]
      And [Additional validations]
```

### Generic Step Implementation Pattern

```python
# features/steps/[feature_name].py
from behave import *
import test_utils
import requests
import json
from dotmap import DotMap

@given('[Initial business state]')
def step_impl(context):
    # Get initial state of your key business entities
    # Store in context for later comparison
    context.initial_state = get_entity_state(entity_id)

@when('[Business action is performed]')
def step_impl(context):
    # Perform the business operation via API
    header = test_utils.login()  # Get auth header if needed
    
    # Make API call (POST, PATCH, DELETE, etc.)
    api_url = f'http://localhost:5656/api/[YourEntity]/[id]/'
    response = requests.patch(url=api_url, json=your_data, headers=header)
    
    # Store response for validation
    context.response = response

@then('[Expected business outcome occurs]')
def step_impl(context):
    # Verify the business rule executed correctly
    # Check entity state changes, calculated fields, etc.
    final_state = get_entity_state(entity_id)
    assert final_state.calculated_field == expected_value
```

## 🤖 For GitHub Copilot

When generating tests for API Logic Server projects:

### Key Patterns to Follow

1. **Focus on Business Logic**: Test declarative rules, not just CRUD operations
2. **Use Behave Framework**: Create `.feature` files with Gherkin syntax
3. **Test Rule Execution**: Verify LogicBank rules fire and produce correct results
4. **Test Constraints**: Verify business rule violations are properly caught
5. **Check Cascading Updates**: Ensure changes propagate through rule chains
6. **Include Authentication**: Use proper auth headers for API calls

### Common Test Utilities

```python
import test_utils

# Authentication (handles both SQL and Keycloak)
header = test_utils.login(user='username')  # Returns auth header dict

# Logging (appears in console and scenario log files)
test_utils.prt("Test message", "scenario_name")

# Typical API call patterns
r = requests.get(url=api_url, headers=header)
r = requests.post(url=api_url, json=data, headers=header)
r = requests.patch(url=api_url, json=data, headers=header)
r = requests.delete(url=api_url, headers=header)
```

### Business Logic Testing Patterns

#### Testing Sum Rules
```python
# Pattern: Test that derived sums update automatically
# Example: Customer.Balance = sum(Order.AmountTotal where not shipped)

@given('Entity with calculated sum field')
def step_impl(context):
    context.parent_before = get_parent_entity(parent_id)

@when('Child entity is modified')
def step_impl(context):
    # Create/update child entity
    header = test_utils.login()
    child_data = {"amount": 100, "parent_id": parent_id}
    r = requests.post(url=child_api_url, json=child_data, headers=header)

@then('Parent sum field updates automatically')
def step_impl(context):
    parent_after = get_parent_entity(parent_id)
    expected_sum = context.parent_before.sum_field + 100
    assert parent_after.sum_field == expected_sum
```

#### Testing Constraint Rules
```python
# Pattern: Test that business constraints are enforced
# Example: Customer.Balance <= Customer.CreditLimit

@when('Action violates business constraint')
def step_impl(context):
    header = test_utils.login()
    # Data that should violate constraint
    violating_data = {"amount": 99999}  # Exceeds credit limit
    r = requests.patch(url=api_url, json=violating_data, headers=header)
    context.response = r

@then('Constraint violation is detected')
def step_impl(context):
    assert context.response.status_code >= 400  # Should fail
    error_message = context.response.json()
    assert "constraint" in error_message.get("message", "").lower()
```

#### Testing Formula Rules
```python
# Pattern: Test that formulas calculate correctly
# Example: OrderDetail.Amount = Quantity * UnitPrice

@when('Formula inputs are changed')
def step_impl(context):
    header = test_utils.login()
    update_data = {"quantity": 5, "unit_price": 10.50}
    r = requests.patch(url=api_url, json=update_data, headers=header)

@then('Formula result updates automatically')
def step_impl(context):
    updated_entity = get_entity(entity_id)
    expected_amount = 5 * 10.50
    assert updated_entity.amount == expected_amount
```

### Security Testing Patterns

```python
# Test role-based access
@given('User with specific role')
def step_impl(context):
    context.auth_header = test_utils.login(user='role_specific_user')

@when('User accesses restricted resource')
def step_impl(context):
    r = requests.get(url=restricted_api_url, headers=context.auth_header)
    context.response = r

@then('Access is properly controlled')
def step_impl(context):
    # Should succeed for authorized users, fail for others
    if user_has_permission:
        assert context.response.status_code == 200
    else:
        assert context.response.status_code in [401, 403]
```

### Project-Specific Considerations

When creating tests for a specific project:

1. **Identify Key Business Rules**: What are the main business logic rules in `logic/declare_logic.py`?
2. **Map Test Scenarios**: Create scenarios that exercise each major rule type
3. **Use Domain Language**: Write scenarios in business terms, not technical terms
4. **Test Rule Interactions**: Verify that rules work together correctly
5. **Include Edge Cases**: Test boundary conditions and error cases

### API Endpoint Patterns

```python
# Standard API endpoint patterns for any project
base_url = "http://localhost:5656/api"

# Get entity with relationships
get_url = f"{base_url}/{EntityName}/{entity_id}/?include={RelatedEntity}List"

# Create new entity
post_url = f"{base_url}/{EntityName}/"
post_data = {"data": {"attributes": {...}, "type": "EntityName"}}

# Update existing entity  
patch_url = f"{base_url}/{EntityName}/{entity_id}/"
patch_data = {"data": {"attributes": {...}, "type": "EntityName", "id": entity_id}}

# Delete entity
delete_url = f"{base_url}/{EntityName}/{entity_id}/"
```

## 📊 Test Reports and Logging

- **Logic Reports**: Generated in `reports/` showing which rules executed
- **Behave Output**: Standard BDD test results with pass/fail status
- **Logic Logs**: Detailed rule execution in `logs/scenario_logic_logs/`
- **Server Logs**: API request/response details and errors

## 🔍 Debugging Tests

### Common Issues and Solutions

1. **Authentication Failures**: Check `Config.SECURITY_ENABLED` and login credentials
2. **Database State**: If tests fail, restore database to clean state
3. **Rule Not Firing**: Verify rule syntax in `logic/declare_logic.py`
4. **API Errors**: Check server console and `logs/scenario_logic_logs/`

### Debug Steps

```python
# Add debug logging to your test steps
test_utils.prt(f"Before: {entity_before}", scenario_name)
test_utils.prt(f"API Response: {response.text}", scenario_name)
test_utils.prt(f"After: {entity_after}", scenario_name)
```

## ⚠️ Important Notes

- **Data Restoration**: Tests automatically restore data, but partial failures may require manual database restore
- **Security Mode**: Behave tests work with security enabled; basic tests require security disabled  
- **Rule Engine Focus**: Tests specifically validate LogicBank rule execution, not just API responses
- **Performance Testing**: Tests can include logic optimization verification (rule pruning, etc.)
- **Concurrent Testing**: Be aware of database locking if running multiple test suites simultaneously

## 🎯 Best Practices

1. **Test Business Logic First**: Focus on rules and constraints before API mechanics
2. **Use Meaningful Test Data**: Choose entities and values that clearly demonstrate rule behavior
3. **Document Test Scenarios**: Explain the business purpose of each test
4. **Keep Tests Independent**: Each scenario should work regardless of other test execution
5. **Verify Rule Execution**: Don't just test API responses, verify that business logic actually ran
6. **Test Error Cases**: Include scenarios that should fail due to business constraints