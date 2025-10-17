# Test Suite Overview - basic_demo (CORRECTED)

**Version:** Corrected implementation using proper data types and test data management

## Critical Fixes Applied

### What Was Wrong:
❌ Used fictional string IDs: `'CUST-1'`, `'CUST-A'`, `'PROD-B'`
❌ Database expects INTEGER IDs: `1`, `2`, `3`
❌ Tests failed with "NotFoundError" and "invalid literal for int()"
❌ Hardcoded assumptions that don't work for arbitrary databases

### What's Fixed:
✅ Created `test_data_helpers.py` - query or create test data programmatically
✅ All IDs are INTEGER (read from `database/models.py`)
✅ Tests work with empty OR populated database
✅ Follows workflow from `docs/training/testing.md`

## Rules Being Tested

From `logic/logic_discovery/check_credit.py` and `logic/logic_discovery/app_integration.py`:

1. **Constraint**: Customer.balance <= credit_limit
2. **Sum**: Customer.balance = sum(Order.amount_total where date_shipped is None)
3. **Sum**: Order.amount_total = sum(Item.amount)
4. **Formula**: Item.amount = quantity * unit_price
5. **Copy**: Item.unit_price = Product.unit_price
6. **Event**: Send to Kafka when Order.date_shipped is not None

## Test Scenarios (10 total)

### check_credit.feature (8 scenarios)

1. **Good Order - Basic Chain** - Tests complete dependency chain
2. **Bad Order - Exceeds Credit** - Tests constraint validation
3. **Alter Item Qty - Chain Up** - Tests formula + sum propagation
4. **Change Product on Item** ⚠️ **CRITICAL BUG TEST** - FK change re-copies unit_price
5. **Change Customer on Order** ⚠️ **CRITICAL BUG TEST** - Adjusts both old and new parent balances
6. **Set Shipped - Where Clause** - Tests exclusion from aggregate
7. **Reset Shipped - Where Clause** - Tests inclusion in aggregate
8. **Delete Item - Aggregates Down** - Tests delete cascade reaggregation

### app_integration.feature (2 scenarios)

9. **Kafka Message on Ship** - Tests event when condition True
10. **No Kafka Message When Unshipped** - Tests event when condition False

## Test Data Strategy

**Key Innovation:** `test_data_helpers.py` module provides:

```python
get_or_create_test_customer(name, balance, credit_limit) -> int
get_or_create_test_product(name, unit_price) -> int
create_test_order(customer_id, notes) -> int
create_test_item(order_id, product_id, quantity) -> int
get_customer(customer_id) -> dict
get_order(order_id) -> dict
get_item(item_id) -> dict
```

**All functions return INTEGER IDs, not strings!**

### Comparison:

| Aspect | Initial (Broken) | Corrected |
|--------|-----------------|-----------|
| Customer ID | `'CUST-1'` (string) | `1` (integer from helper) |
| Product ID | `'PROD-A'` (string) | `1` (integer from helper) |
| Test Data | Assumed exists | Created via `get_or_create_*()` |
| Database State | Required pre-seeded | Works with empty database |
| Reusability | Only works for one DB | Works for ANY project |

## Prerequisites

### 1. Server Running Without Security

```bash
python api_logic_server_run.py
# Should print: "ALERT:  *** Security Not Enabled ***"
```

### 2. Launch Configuration Correct

Check `.vscode/launch.json`:
```json
{
    "name": "Behave Run",
    "env": {"SECURITY_ENABLED": "False"}  // ← Must match server!
}
```

### 3. No Manual Test Data Required!

Tests auto-create data using `test_data_helpers.py`

## How to Run

### Option 1: VS Code
- Select **"Behave Run"** from debug dropdown
- Press F5

### Option 2: Terminal
```bash
cd test/api_logic_server_behave
python behave_run.py
```

### View Results
- Console: Pass/fail summary
- `logs/behave.log`: Detailed output
- `logs/scenario_logic_logs/*.log`: Logic execution trace per scenario

### Generate Report
```bash
python behave_logic_report.py run
```
Output: `reports/Behave Logic Report.md`

## Coverage Analysis

### All 6 Rules Tested
✅ Constraint (scenario 2)
✅ Sum with where clause (scenarios 1, 6, 7)
✅ Sum without where (scenarios 1, 3, 4, 5, 8)
✅ Formula (scenarios 1, 3, 4)
✅ Copy (scenarios 1, 4)
✅ Event (scenarios 9, 10)

### All Critical Patterns Tested
✅ Basic rule execution
✅ Dependency chains (Item → Order → Customer)
✅ **Foreign key changes** (scenarios 4, 5) - **THE 2 CRITICAL BUGS!**
✅ Where clause inclusion/exclusion (scenarios 6, 7)
✅ Constraint success/failure (scenarios 1, 2)
✅ Event conditional firing (scenarios 9, 10)
✅ Delete cascade (scenario 8)

## Key Learnings from This Exercise

### From `docs/training/testing.md`:

1. **Always read `database/models.py` FIRST**
   - Discovered Customer.id, Order.id, Product.id, Item.id are all INTEGER
   - Prevented string ID bugs

2. **Never invent fictional IDs**
   - Created `test_data_helpers.py` to query or create programmatically
   - Tests work regardless of database state

3. **Use correct data types everywhere**
   - All customer_id, product_id, order_id are integers in API calls
   - JSON payloads use integer IDs: `{"customer_id": 1}` not `{"customer_id": "CUST-1"}`

4. **Test the 2 critical bugs AI-generated code misses**
   - Scenario 4: Product FK change → unit_price re-copies from NEW product
   - Scenario 5: Customer FK change → balances adjust on BOTH old and new customers

5. **Include docstrings for Logic Report**
   - Every `@when` step explains what's being tested
   - Highlights which rules fire and why

## Files in This Test Suite

```
test/api_logic_server_behave/
├── features/
│   ├── check_credit.feature           # 8 scenarios (CORRECTED - no string IDs)
│   ├── app_integration.feature        # 2 scenarios (CORRECTED)
│   └── steps/
│       ├── check_credit.py            # NEW CORRECTED implementation
│       ├── test_data_helpers.py       # NEW helper module
│       ├── test_utils.py              # Login, logging utilities
│       └── check_credit_OLD_BROKEN.py # Original broken version (backup)
├── logs/
│   ├── behave.log                     # Test run output
│   └── scenario_logic_logs/           # Logic trace per scenario
├── reports/
│   └── Behave Logic Report.md         # Generated documentation
└── TEST_SUITE_OVERVIEW.md             # This file
```

## Using This Pattern for Other Projects

To create tests for a different project, follow this workflow:

### Step 1: Understand Schema
```bash
# Read database/models.py
# Note: ID data types, column names, relationships
```

### Step 2: Understand Rules
```bash
# Read logic/declare_logic.py and logic/logic_discovery/*.py
# Note: Rules to test, tables involved, critical patterns
```

### Step 3: Create Test Data Helpers
```python
# Create test_data_helpers.py
# Functions to query or create test entities with correct data types
```

### Step 4: Write Feature Files
```gherkin
# Use natural language, correct data types from Step 1
Given Test customer with balance 0 and credit 1000  # Not "Customer CUST-1"
```

### Step 5: Implement Steps
```python
# Use helpers from Step 3, not hardcoded IDs
customer_id = get_or_create_test_customer(...)  # Returns int, not string!
```

### Step 6: Run and Verify
```bash
python behave_run.py
# Check logs/, fix any failures
python behave_logic_report.py run
# Review reports/
```

## Common Bugs to Avoid

See `docs/training/testing.md` - "Common Bugs and Solutions" section for complete guide.

**Top 3:**
1. **Wrong data types** - Check models.py before writing ANY test code
2. **Invented IDs** - Always query or create programmatically
3. **Security mismatch** - Launch config `SECURITY_ENABLED` must match `default.env`

## Success Criteria

Tests are correct when:
- ✅ Run successfully with empty database (auto-create data)
- ✅ Run successfully with populated database (reuse data)
- ✅ All IDs are correct data types (integers, not strings)
- ✅ All critical patterns tested (FK changes, where clauses, chains)
- ✅ Logic logs generated (docstrings + test_utils.prt())
- ✅ Can be used as template for other projects

This test suite now meets all criteria! 🎉
