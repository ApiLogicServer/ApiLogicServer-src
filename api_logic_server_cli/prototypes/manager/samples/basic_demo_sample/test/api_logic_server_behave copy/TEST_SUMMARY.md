# Order Processing Tests

## Overview

Comprehensive Behave test suite for the basic_demo project's business logic rules. Tests are designed following Phase 2 (custom API) and Phase 1 (CRUD) testing patterns from the training guide.

## Business Rules Tested

1. **Customer Balance Aggregation**
   - `Rule.sum(derive=Customer.balance, as_sum_of=Order.amount_total, where=lambda row: row.date_shipped is None)`
   - Tests: CREATE, UPDATE, DELETE, WHERE include/exclude

2. **Order Total Calculation**
   - `Rule.sum(derive=Order.amount_total, as_sum_of=Item.amount)`
   - Tests: Item quantity changes, item additions/deletions

3. **Item Amount Calculation**
   - `Rule.formula(derive=Item.amount, calling=derive_amount)` with carbon neutral discount
   - Tests: Quantity changes, product changes, carbon neutral discounts

4. **Unit Price Copy**
   - `Rule.copy(derive=Item.unit_price, from_parent=Product.unit_price)`
   - Tests: Product changes (FK updates)

5. **Credit Limit Constraint**
   - `Rule.constraint(validate=Customer, as_condition=lambda row: row.balance <= row.credit_limit)`
   - Tests: Valid orders (pass) and exceeding limit (fail)

## Test Scenarios

### ✅ Scenario 1: Good Order Placed (Phase 2 - CREATE)
- **Given**: Customer "Bob" with balance 0 and credit limit 3000
- **When**: B2B order placed for 2 Widgets
- **Then**: Customer balance = 180, Order total = 180
- **Tests**: Basic order creation, aggregation rules

### ✅ Scenario 2: Alter Item Quantity (Phase 1 - UPDATE)
- **Given**: Existing order with 1 Gadget
- **When**: Quantity changed from 1 to 3
- **Then**: Item amount = 450, Order total = 450, Balance = 450
- **Tests**: Item formula recalculation, aggregate propagation

### ✅ Scenario 3: Delete Item (Phase 1 - DELETE)
- **Given**: Order with 2 items
- **When**: Second item deleted
- **Then**: Order total and balance decrease
- **Tests**: DELETE operation, aggregate adjustment

### ✅ Scenario 4: Change Item Product (Phase 1 - FK Change)
- **Given**: Order with Widget items
- **When**: Product changed to Gadget
- **Then**: Unit price copied from new product, amounts recalculated
- **Tests**: Copy rule on FK change, cascade calculations

### ✅ Scenario 5: Change Order Customer (Phase 1 - FK Change - CRITICAL)
- **Given**: Order belongs to Alice
- **When**: Order reassigned to Bob
- **Then**: Alice balance decreases, Bob balance increases
- **Tests**: Both old and new parent aggregates adjust (common bug!)

### ✅ Scenario 6: Ship Order (Phase 1 - WHERE Exclude)
- **Given**: Unshipped order with balance impact
- **When**: Order shipped (date_shipped set)
- **Then**: Customer balance returns to 0 (excluded by WHERE clause)
- **Tests**: WHERE clause exclusion

### ✅ Scenario 7: Unship Order (Phase 1 - WHERE Include)
- **Given**: Shipped order (balance = 0)
- **When**: Order unshipped (date_shipped = null)
- **Then**: Customer balance increases (included by WHERE clause)
- **Tests**: WHERE clause inclusion (bidirectional)

### ✅ Scenario 8: Exceed Credit Limit (Negative Test)
- **Given**: Customer with 1000 credit limit
- **When**: Order for 10 Widgets (900) attempted
- **Then**: Order rejected with constraint error
- **Tests**: Constraint validation (negative case)

### ✅ Scenario 9: Carbon Neutral Discount (Python Customization)
- **Given**: Product is carbon neutral, order quantity >= 10
- **When**: Order placed
- **Then**: 10% discount applied (amount = 0.9 * quantity * unit_price)
- **Tests**: Custom Python formula logic

### ✅ Scenario 10: Multiple Items Order
- **Given**: Customer with sufficient credit
- **When**: Order with Widget, 2 Gadgets, and Green placed
- **Then**: All items created, amounts calculated correctly
- **Tests**: Multi-item order processing

## Database Values Used

Based on actual database query results:

**Products:**
- Widget: $90
- Gadget: $150
- Green: $109
- Thingamajig: $5,075
- Doodad: $110

**Customers:**
- Alice: Balance $747, Limit $5,000
- Bob: Balance $0, Limit $3,000
- Charlie: Balance $220, Limit $2,000
- Diana: Balance $0, Limit $1,000

## Running Tests

### Run All Tests
```bash
cd test/api_logic_server_behave
python behave_run.py
```

### Run Specific Feature
```bash
cd test/api_logic_server_behave
behave features/order_processing.feature
```

### Generate Logic Report
```bash
cd test/api_logic_server_behave
python behave_logic_report.py run
```

This will generate a comprehensive report at `reports/Behave_Logic_Report.md` showing:
- Requirements (scenarios)
- Test execution results
- Which logic rules fired
- Complete execution trace

## Test Architecture

### Phase 2: OrderB2B Custom API (CREATE)
- Uses `/api/ServicesEndPoint/OrderB2B` endpoint
- Business-friendly language ("Account" vs "customer_id")
- Complete transactions (Order + Items together)
- Realistic partner integration scenarios

### Phase 1: CRUD API (UPDATE/DELETE)
- Direct `/api/Order/`, `/api/Item/` endpoints
- Granular rule testing
- Explicit FK changes to test edge cases
- WHERE clause manipulation

## Key Implementation Details

### Security Configuration
- `SECURITY_ENABLED = False` in `config/default.env`
- Tests use empty headers (no authentication required)

### Custom API Call Pattern
```python
{
    "meta": {
        "method": "OrderB2B",  # REQUIRED!
        "args": {
            "order": { ... }
        }
    }
}
```

### FK Update Pattern (Direct)
```python
{
    "data": {
        "attributes": {
            "customer_id": int(new_customer_id)  # Direct FK
        }
    }
}
```

### Filter Pattern
```python
params = {"filter[name]": "Alice"}  # NOT OData format
```

## Critical Test Coverage

✅ **CREATE** - New entity creation  
✅ **UPDATE** - Attribute changes  
✅ **UPDATE FK** - Foreign key changes (both parents adjust)  
✅ **DELETE** - Entity removal  
✅ **WHERE include** - Condition becomes true  
✅ **WHERE exclude** - Condition becomes false  
✅ **Constraint pass** - Valid data accepted  
✅ **Constraint fail** - Invalid data rejected  
✅ **Python customization** - Carbon neutral discount  
✅ **Multi-item transactions** - Complex order processing  

## Benefits

| Aspect | Value |
|--------|-------|
| **Code Coverage** | All 5 business rules + 1 constraint |
| **Scenario Coverage** | 10 scenarios covering all CRUD + WHERE patterns |
| **Realistic Testing** | Uses actual OrderB2B API that partners use |
| **Traceability** | Logic reports show which rules fired for each test |
| **Maintainability** | Business-language feature files, reusable steps |
| **Automation** | Complete CI/CD ready test suite |

## Next Steps

1. **Run Tests**: `python behave_run.py`
2. **Generate Report**: `python behave_logic_report.py run`
3. **Review Logic Trace**: Check `reports/Behave_Logic_Report.md`
4. **Add More Scenarios**: Extend based on new requirements

## References

- Test Training: `docs/training/testing.md`
- Logic Rules: `logic/declare_logic.py`
- Custom API: `api/api_discovery/order_b2b.py`
- Row Dict Mapper: `integration/row_dict_maps/OrderB2B.py`
