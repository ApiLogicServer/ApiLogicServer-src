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
│   │   ├── place_order.feature   # Core business logic scenarios
│   │   ├── salary_change.feature # Employee management tests
│   │   ├── authorization.feature # Security tests
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
3. **Database State**: Tests restore data automatically, but if tests fail mid-execution, restore `database/db.sqlite` from backup

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

## 📝 Test Scenarios

### Core Business Logic (`place_order.feature`)

Tests the fundamental business rules of the sample Northwind application:

- **Order State Management**: Ready/Not Ready flag changes
- **Credit Checking**: Validates customer credit limits
- **Balance Calculations**: Automatic customer balance adjustments
- **Inventory Management**: Product reordering and stock updates
- **Notifications**: Email alerts to sales representatives
- **Integration**: Kafka message publishing
- **Constraint Validation**: Prevents shipping empty orders

### Employee Management (`salary_change.feature`)

- **Audit Trail**: Automatic logging of salary changes
- **Derived Attributes**: ProperSalary calculations
- **Business Rules**: Minimum raise requirements

### Security (`authorization.feature`)

- **Authentication**: Login/logout functionality
- **Role-Based Access**: Permission validation
- **Data Filtering**: Row-level security

## 🧪 Test Data

Tests use consistent, known data for predictable results:

| Entity | ID/Key | Key Attributes | Purpose |
|--------|--------|----------------|---------|
| Customer | ALFKI | Balance: 2102, CreditLimit varies | Credit checking, balance calculations |
| Order | 10643 | Amount: 1086 | Order processing, shipping logic |
| Employee | 5 (Buchanan) | Salary: 95k | Salary management, audit testing |

## 🔧 For Developers

### Adding New Tests

1. **Create Feature File**: Add `.feature` file in `features/` using Gherkin syntax
2. **Implement Steps**: Create corresponding `.py` file in `features/steps/`
3. **Use Test Utilities**: Import `test_utils.py` for common functions
4. **Follow Patterns**: Reference existing tests for authentication, logging, and assertions

### Example Feature Structure

```gherkin
Feature: My New Feature

  Scenario: Test Scenario Name
     Given Initial condition
      When Action is performed
      Then Expected result occurs
```

### Example Step Implementation

```python
# features/steps/my_feature.py
from behave import *
import test_utils
import requests
import json

@given('Initial condition')
def step_impl(context):
    # Setup code
    pass

@when('Action is performed')
def step_impl(context):
    # Action code
    header = test_utils.login()  # Get auth header
    # Make API calls
    pass

@then('Expected result occurs')
def step_impl(context):
    # Assertion code
    pass
```

## 🤖 For GitHub Copilot

When generating tests for API Logic Server projects:

### Key Patterns to Follow

1. **Focus on Business Logic**: Test declarative rules, not just CRUD operations
2. **Use Behave Framework**: Create `.feature` files with Gherkin syntax
3. **Test Authentication**: Include login/security in API calls
4. **Verify Rule Execution**: Check that LogicBank rules fire correctly
5. **Test Constraints**: Verify business rule violations are caught
6. **Check Cascading Updates**: Ensure changes propagate correctly

### Common Test Utilities

```python
import test_utils

# Authentication
header = test_utils.login(user='aneu')  # Returns auth header

# Logging (appears in both console and log files)
test_utils.prt("Test message", "scenario_name")

# API calls with auth
r = requests.get(url=api_url, headers=header)
r = requests.patch(url=api_url, json=data, headers=header)
```

### Security Considerations

- Tests can run with or without security enabled
- Use `test_utils.login()` for authenticated requests
- Handle both SQL and Keycloak authentication providers
- Check `Config.SECURITY_ENABLED` flag

### Business Logic Testing Patterns

1. **Setup**: Get initial state (e.g., customer balance)
2. **Action**: Perform business operation (e.g., place order)
3. **Verify**: Check rule execution results (e.g., balance updated, constraints enforced)
4. **Cleanup**: Data is automatically restored

### Sample Rule Testing

```python
# Test a sum rule: Customer.Balance = sum(Order.AmountTotal where not shipped)
def test_balance_calculation():
    # 1. Get initial customer state
    customer_before = get_customer('ALFKI')
    
    # 2. Create/modify order
    create_order_for_customer('ALFKI', amount=100)
    
    # 3. Verify balance updated automatically
    customer_after = get_customer('ALFKI')
    assert customer_after.Balance == customer_before.Balance + 100
```

## 📊 Test Reports

- **Logic Reports**: Generated in `reports/` showing which rules executed
- **Behave Output**: Standard BDD test results
- **Logic Logs**: Detailed rule execution in `logs/scenario_logic_logs/`

## 🔍 Debugging Tests

- **Check Logs**: Review `logs/scenario_logic_logs/<scenario>.log`
- **Use Debug Console**: In VS Code, select "Behave Run" from dropdown
- **Server Logs**: Check server console for API errors
- **Database State**: Restore `database/db.sqlite` if tests fail mid-execution

## ⚠️ Important Notes

- **Data Restoration**: Tests automatically restore data, but partial failures may require manual database restore
- **Security Mode**: Behave tests work with security enabled; basic tests require security disabled
- **Rule Engine**: Tests specifically validate LogicBank rule execution, not just API responses
- **Performance**: Tests include logic optimization verification (rule pruning, etc.)