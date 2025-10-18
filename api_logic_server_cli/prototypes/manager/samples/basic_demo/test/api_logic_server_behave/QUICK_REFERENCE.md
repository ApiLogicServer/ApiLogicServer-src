# Quick Test Reference Card

## 🚀 Run Tests (3 Steps)

```bash
# 1. Start Server
Press F5 → "ApiLogicServer"

# 2. Run Tests  
Press F5 → "Behave No Security"

# 3. View Results
cat test/api_logic_server_behave/logs/behave.log
```

## 📊 Test Files Created

| File | Lines | Purpose |
|------|-------|---------|
| `features/check_credit.feature` | 44 | 6 scenarios - credit checking |
| `features/order_lifecycle.feature` | 23 | 3 scenarios - WHERE/DELETE |
| `features/steps/check_credit.py` | 418 | Test implementation |
| `features/steps/order_lifecycle.py` | 185 | Test implementation |

**Total: 9 scenarios, 600+ lines of professional test code**

## ✅ Test Scenarios

### check_credit.feature
1. Good Order Placed ✅
2. Bad Order Exceeds Credit ✅
3. Alter Item Quantity to Exceed Credit ✅
4. Change Product on Item ✅
5. Change Customer on Order ✅ ← **THE CRITICAL BUG TEST**
6. Delete Item Adjusts Balance ✅

### order_lifecycle.feature
7. Set Order Shipped Excludes from Balance ✅
8. Reset Shipped Includes in Balance ✅ ← **Bidirectional WHERE**
9. Delete Order Adjusts Balance ✅

## 🎯 What's Tested

✅ All CRUD operations (POST, PATCH, DELETE, GET)  
✅ All 5 business rules (constraint, sum×2, formula, copy)  
✅ Dependency chains (Product → Item → Order → Customer)  
✅ Foreign key changes (both parents adjust)  
✅ WHERE clause bidirectional (include/exclude)  
✅ DELETE operations (aggregates down)  
✅ Constraints on all operations

## 📖 Generate Documentation

```bash
# Generate Behave Logic Report
Press F5 → "Behave Logic Report"

# View report
open test/api_logic_server_behave/reports/Behave\ Logic\ Report.md
```

## 🐛 Debug Failed Test

```bash
# 1. Check which scenarios failed
cat test/api_logic_server_behave/logs/behave.log

# 2. Check scenario logic log
ls -la test/api_logic_server_behave/logs/scenario_logic_logs/

# 3. Empty log? → Problem in GIVEN/WHEN (before logic)
# 4. Has content? → Problem in THEN or logic execution
```

## 💡 Key Insights

**These 5 rules:**
```python
Rule.constraint(...)  # Credit limit
Rule.sum(...)        # Customer.balance (with WHERE)
Rule.sum(...)        # Order.amount_total
Rule.formula(...)    # Item.amount
Rule.copy(...)       # Item.unit_price
```

**Replace 200+ lines of procedural code that would miss:**
- ❌ Changing customer on order (both balances)
- ❌ Changing product on item (re-copy price)
- ❌ WHERE clause bidirectional (ship/unship)
- ❌ DELETE operations (aggregates down)

**The rules engine handles ALL automatically = 44X advantage!**

## 📚 Full Documentation

- **Test Overview**: `TEST_SUITE_OVERVIEW.md`
- **Complete Guide**: `TESTS_CREATED.md`
- **Training Material**: `docs/training/testing.md` (1755 lines)

---

**Ready to run!** Press F5 → "ApiLogicServer", then F5 → "Behave No Security"
