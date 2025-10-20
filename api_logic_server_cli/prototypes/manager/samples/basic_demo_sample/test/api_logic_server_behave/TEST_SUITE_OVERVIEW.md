# Test Suite Overview

## Test Files Created

### 1. check_credit.feature (6 scenarios)
Tests core credit checking logic and rule chains:

- ✅ **Good Order Placed** - Complete dependency chain (copy → formula → sum → sum → constraint)
- ✅ **Bad Order Exceeds Credit** - Constraint rejection on insert
- ✅ **Alter Item Quantity to Exceed Credit** - Constraint rejection on update
- ✅ **Change Product on Item** - Copy rule re-execution + chain propagation
- ✅ **Change Customer on Order** - Both parent balances adjust (THE CRITICAL BUG test)
- ✅ **Delete Item Adjusts Balance** - Aggregate adjustment downward

### 2. order_lifecycle.feature (3 scenarios)
Tests WHERE clause bidirectional behavior and DELETE operations:

- ✅ **Set Order Shipped Excludes from Balance** - WHERE clause exclusion
- ✅ **Reset Shipped Includes in Balance** - WHERE clause inclusion (reverse direction)
- ✅ **Delete Order Adjusts Balance** - Complete order deletion

## Implementation Quality

All tests follow the **6 CRITICAL RULES** from `docs/training/testing.md`:

### ✅ Rule #1: Read Database Schema First
- Used Integer IDs (not strings)
- Identified aggregates: `Customer.balance`, `Order.amount_total`, `Item.amount`
- Used exact column names from models.py

### ✅ Rule #2: Direct FK Format
- All POST/PATCH use `"customer_id": int(id)` in attributes
- No relationships format (prevents optimistic locking errors)

### ✅ Rule #3: Mandatory Test Code Patterns
- **Filter format**: JSON:API standard (not used in these tests, but ready)
- **Fresh test data**: `f"Test Customer {int(time.time() * 1000)}"`
- **Convert IDs to int**: All helpers return `int(result['data']['id'])`
- **No circular imports**: Only `behave`, `requests`, `test_utils`
- **Execute steps**: Using `context.execute_steps()` pattern (when needed)
- **Null-safe constraints**: Constraint in logic includes None checks

### ✅ Rule #4: Complete CRUD + WHERE Coverage
- **CREATE (POST)**: Good Order Placed
- **UPDATE (PATCH)**: Item quantity, product change, customer change, shipped flag
- **DELETE**: Delete item, delete order
- **WHERE bidirectional**: Ship order (exclude), unship order (include)
- **Constraint pass/fail**: Good order (pass), bad order (fail)

### ✅ Rule #5: Security & Environment Awareness
- Checked `config/default.env`: `SECURITY_ENABLED = false`
- Using `test_utils.login()` which returns `{}` when security disabled

### ✅ Rule #6: Logic Logging for Documentation
- Every WHEN step includes `test_utils.prt(f'\n{scenario_name}\n', scenario_name)`
- Second argument critical for scenario grouping in reports

## Helper Functions

Created clean, single-responsibility helpers:

```python
create_test_customer(name, credit_limit) -> int
create_test_product(name, unit_price) -> int
create_test_order(customer_id, notes) -> int
create_test_item(order_id, product_id, quantity) -> int
get_customer(customer_id) -> dict
```

All helpers:
- ✅ Return **int** IDs (not strings)
- ✅ Use **direct FK format** in attributes
- ✅ Keep it simple (no circular dependencies)
- ✅ Create entities only (test steps create relationships)

## Test Coverage

### Rules Tested:
1. ✅ `Rule.constraint` - Credit limit validation
2. ✅ `Rule.sum` (with WHERE) - Customer.balance
3. ✅ `Rule.sum` - Order.amount_total
4. ✅ `Rule.formula` - Item.amount
5. ✅ `Rule.copy` - Item.unit_price from Product
6. ⚠️ `Rule.after_flush_row_event` - Kafka (not tested yet - see note below)

### Critical Patterns Tested:
- ✅ Dependency chains (grandchild → child → parent)
- ✅ Foreign key changes (both parents adjust)
- ✅ WHERE clause bidirectional (include/exclude)
- ✅ DELETE operations (aggregate down)
- ✅ Constraint on insert and update
- ✅ Copy rule re-execution

## Next Steps

### 1. Start the Server
```bash
# Option A: Use VS Code Launch Configuration "ApiLogicServer" (F5)
# Option B: Run from terminal
python api_logic_server_run.py
```

### 2. Run the Test Suite
```bash
# Use VS Code Launch Configuration "Behave Run"
# Or from terminal:
cd test/api_logic_server_behave
behave
```

### 3. Check Test Results
```bash
# View test summary
cat test/api_logic_server_behave/logs/behave.log

# View individual scenario logic logs
ls -la test/api_logic_server_behave/logs/scenario_logic_logs/
```

### 4. Generate Documentation
```bash
# Use VS Code Launch Configuration "Behave Report"
# Or from terminal:
cd test/api_logic_server_behave
python behave_logic_report.py run

# View report
cat test/api_logic_server_behave/reports/Behave\ Logic\ Report.md
```

## Note on Kafka Testing

The Kafka integration rule is not tested yet:
```python
Rule.after_flush_row_event(on_class=Order, 
                          calling=kafka_producer.send_row_to_kafka,
                          if_condition=lambda row: row.date_shipped is not None)
```

**Reason**: Kafka testing requires:
- Kafka broker running
- Mocking/verification of Kafka messages
- More complex test infrastructure

**Recommendation**: Add Kafka tests later if integration testing is needed. Current tests focus on core business logic correctness.

## Test Data Strategy

Tests use **fresh test data creation** (not pre-seeded data):
- ✅ Unique names with timestamps prevent contamination
- ✅ Tests are idempotent (can run multiple times)
- ✅ No dependencies on specific database state
- ✅ Works with empty database

## Expected Test Results

All 9 scenarios should **PASS** ✅ if:
- Server is running on `http://localhost:5656`
- Security is disabled (`SECURITY_ENABLED = false`)
- Database is accessible
- Logic rules are loaded from `logic/declare_logic.py`

## Documentation Features

When you run the Behave Report, you'll see:
- 📋 **Test scenarios** with Given/When/Then
- 📝 **Logic documentation** from docstrings
- 🔍 **Rules used** in each scenario
- 📊 **Logic log** showing rule execution trace
- ✅ **Complete traceability** from requirement to execution

This demonstrates the **44X advantage** - transparent logic with complete audit trail!
