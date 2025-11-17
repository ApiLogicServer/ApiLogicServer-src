---
version: 1.0
---

# GenAI Logic Patterns - Universal Guide

**Scope:** Framework-level patterns for integrating AI into business logic using LogicBank.  
**Applies to:** Any ApiLogicServer project using AI-powered rules.

---

## 1. Critical Imports - AVOID CIRCULAR IMPORTS

### ⚠️ CRITICAL: Import LogicBank ONLY Inside Functions

**Problem:** Importing `LogicRow`, `Rule` at module level causes circular import errors during auto-discovery.

### ❌ WRONG (causes circular import):
```python
# At module level - DO NOT DO THIS
from logic_bank.exec_row_logic.logic_row import LogicRow
from logic_bank.logic_bank import Rule
from database import models

def declare_logic():
    Rule.formula(...)  # ❌ Circular import error
```

### ✅ CORRECT (import inside functions):
```python
# At module level - only non-LogicBank imports
import database.models as models

def declare_logic():
    from logic_bank.logic_bank import Rule  # ✅ Import inside function
    
    Rule.formula(derive=models.Item.unit_price, calling=my_formula)

def my_formula(row, old_row, logic_row):  # ✅ No type hints on logic_row
    from logic.ai_requests.handler import get_ai_value  # ✅ Import when needed
    return get_ai_value(row, logic_row)
```

**Why:** LogicBank's auto-discovery imports modules during initialization. Module-level LogicBank imports create circular dependencies that fail with "cannot import name 'LogicRow' from partially initialized module".

**Pattern for All Logic Files:**
1. ✅ Import `database.models as models` at module level
2. ✅ Import `Rule` inside `declare_logic()` function
3. ✅ Import other logic modules inside functions where used
4. ✅ No type hints on `logic_row` parameters (avoid `LogicRow` import)
5. ✅ Import external libraries (OpenAI, yaml, etc.) inside functions that use them

---

## 2. LogicBank Triggered Insert Pattern

**Problem:** Cannot use `session.add()` + `session.flush()` inside formulas because formulas execute DURING SQLAlchemy's flush cycle (nested flush not allowed).

### ❌ WRONG (causes "Session is already flushing" error):
```python
def my_formula(row, old_row, logic_row):
    audit_record = models.AuditTable(data=...)
    logic_row.session.add(audit_record)
    logic_row.session.flush()  # ❌ ERROR: Session is already flushing
    return audit_record.computed_value
```

### ✅ CORRECT (LogicBank triggered insert):
```python
def my_formula(row, old_row, logic_row):
    # Use LogicBank API instead of session
    audit_logic_row = logic_row.new_logic_row(models.AuditTable)
    audit_record = audit_logic_row.row
    audit_logic_row.link(to_parent=logic_row)
    audit_record.data = ...
    audit_logic_row.insert(reason="AI computation")
    return audit_record.computed_value  # Populated by event handler

def populate_audit_fields(row, old_row, logic_row):
    if logic_row.is_inserted():
        # Event handler fires DURING formula execution
        row.computed_value = ...
        row.audit_details = ...

Rule.early_row_event(on_class=models.AuditTable, calling=populate_audit_fields)
```

**Key Points:**
- `logic_row.new_logic_row()` creates row without session
- `logic_row.insert()` uses LogicBank's insert mechanism
- Event handler fires DURING formula execution
- Formula returns value populated by event handler

**Reference:** https://apilogicserver.github.io/Docs/Logic-Use/#in-logic

---

## 3. AI Value Computation Architecture

### Pattern: Reusable AI Handlers

**Structure:**
```
logic/
  logic_discovery/          # Use case logic
    check_credit.py         # Business rule that calls AI
  ai_requests/              # Reusable AI handlers
    supplier_selection.py   # AI handler module
  system/                   # Framework utilities
    ai_value_computation.py # Shared utilities
```

**Use Case Logic (check_credit.py):**
```python
from logic.logic_discovery.ai_requests.supplier_selection import get_supplier_price_from_ai

def ItemUnitPriceFromSupplier(row, old_row, logic_row):
    """Conditional formula - use AI when suppliers exist"""
    if row.product.count_suppliers == 0:
        return row.product.unit_price  # Fallback
    
    # Call reusable AI handler (encapsulates Request Pattern)
    logic_row.log(f"Item - Product has {row.product.count_suppliers} suppliers, invoking AI")
    return get_supplier_price_from_ai(row=row, logic_row=logic_row)

Rule.formula(derive=models.Item.unit_price, calling=ItemUnitPriceFromSupplier)
```

**AI Handler (ai_requests/supplier_selection.py):**
```python
def get_supplier_price_from_ai(row, logic_row):
    """
    Returns optimal supplier price using AI selection.
    Encapsulates Request Pattern - creates audit record, triggers AI, returns computed value.
    """
    # Create audit record using LogicBank triggered insert (Request Pattern)
    supplier_req_logic_row = logic_row.new_logic_row(models.SysSupplierReq)
    supplier_req = supplier_req_logic_row.row
    supplier_req_logic_row.link(to_parent=logic_row)
    supplier_req.product_id = row.product_id
    supplier_req.item_id = row.id
    
    # Insert triggers supplier_id_from_ai event handler which populates chosen_* fields
    supplier_req_logic_row.insert(reason="AI supplier selection request")
    
    # Return value populated by event handler
    return supplier_req.chosen_unit_price

def supplier_id_from_ai(row, old_row, logic_row):
    """Event handler - fires on SysSupplierReq insert, populates audit fields"""
    if not logic_row.is_inserted():
        return
    
    # Get candidates, call AI, populate row fields
    # (Full implementation in actual file)
    row.chosen_supplier_id = ai_result['chosen_supplier_id']
    row.chosen_unit_price = Decimal(str(ai_result['chosen_unit_price']))
    row.reason = ai_result['reason']

def declare_logic():
    """Self-register event handler for auto-discovery"""
    from logic_bank.logic_bank import Rule
    Rule.early_row_event(on_class=models.SysSupplierReq, calling=supplier_id_from_ai)
```

**Benefits:**
- Separation of concerns (use case vs AI handler vs utilities)
- Reusability (multiple use cases can call same AI handler)
- Testability (each layer independently testable)
- Encapsulation (Request Pattern details hidden from use case)

---

## 4. Auto-Discovery System - RECURSIVE SCANNING REQUIRED

### ⚠️ CRITICAL: Auto-Discovery Must Scan Subdirectories

**Problem:** Default auto_discovery.py only scans immediate directory, not subdirectories like `ai_requests/`.

### ❌ WRONG (misses subdirectories):
```python
def discover_logic():
    for root, dirs, files in os.walk(logic_path):
        for file in files:
            spec = importlib.util.spec_from_file_location("module.name", logic_path.joinpath(file))
            # ❌ Uses logic_path instead of actual file location
```

### ✅ CORRECT (recursive with proper paths):
```python
def discover_logic():
    """Discover additional logic in this directory and subdirectories"""
    import os
    logic = []
    logic_path = Path(__file__).parent
    for root, dirs, files in os.walk(logic_path):
        root_path = Path(root)  # ✅ Use actual subdirectory path
        for file in files:
            if file.endswith(".py") and not file.endswith("auto_discovery.py") and not file.startswith("__"):
                file_path = root_path / file  # ✅ Build complete path
                spec = importlib.util.spec_from_file_location("module.name", file_path)
                logic.append(str(file_path))
                try:
                    each_logic_file = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(each_logic_file)
                    if hasattr(each_logic_file, 'declare_logic'):
                        each_logic_file.declare_logic()
                except Exception as e:
                    app_logger.error(f"Error loading logic from {file_path}: {e}")
                    raise
```

**Key Fixes:**
1. ✅ Use `root_path = Path(root)` to get actual subdirectory path
2. ✅ Build complete path: `file_path = root_path / file`
3. ✅ Check for `declare_logic` existence with `hasattr()`
4. ✅ Skip `__init__.py` and `auto_discovery.py` files
5. ✅ Wrap in try/except to catch import errors with context

**Requirements:**
1. Module must be in `logic/logic_discovery/` or subfolder
2. Module must have `declare_logic()` function
3. Function registers rules when called

**Example Structure:**
```
logic/logic_discovery/
  check_credit.py          # ✅ Discovered
  app_integration.py       # ✅ Discovered
  ai_requests/             # ✅ Subdirectory scanned
    __init__.py            # ✅ Skipped
    supplier_selection.py  # ✅ Discovered
```

---

## 5. Formula Pattern with AI

**Basic Pattern:**
```python
def MyFormula(row, old_row, logic_row):
    """Formula computes value, optionally calling AI"""
    if some_condition:
        return simple_calculation()
    else:
        return ai_computation(...)

Rule.formula(derive=models.MyTable.my_field, calling=MyFormula)
```

**Conditional Pattern:**
```python
def ConditionalFormula(row, old_row, logic_row):
    """Use default value OR call AI based on data availability"""
    if not has_enough_data(row):
        return row.default_value
    return get_ai_value(row, logic_row, ...)

Rule.formula(derive=models.MyTable.computed_field, calling=ConditionalFormula)
```

**Key Points:**
- Formula function returns computed value
- Can call reusable AI handlers
- AI handler encapsulates audit/request pattern
- Formula remains clean and readable

---

## 6. Event Handler Patterns

### Early Row Event (for audit population):
```python
def populate_audit_fields(row, old_row, logic_row):
    """Fires DURING insert, before other rules"""
    if logic_row.is_inserted():
        row.field1 = compute_value1()
        row.field2 = compute_value2()
        # NO return value needed

Rule.early_row_event(on_class=models.AuditTable, calling=populate_audit_fields)
```

### Row Event (for side effects):
```python
def notify_on_change(row, old_row, logic_row):
    """Fires after all rules complete"""
    if logic_row.nest_level == 0:  # Top-level transaction
        send_notification(row)
        # NO return value

Rule.row_event(on_class=models.MyTable, calling=notify_on_change)
```

**When to use:**
- **early_row_event:** Populate fields that other rules depend on
- **row_event:** Side effects after all rules complete

---

## 7. Common Patterns Summary

### Pattern 1: Simple AI Formula
```python
def ai_formula(row, old_row, logic_row):
    return call_ai_service(row.data)

Rule.formula(derive=models.MyTable.field, calling=ai_formula)
```

### Pattern 2: Conditional AI Formula
```python
def conditional_formula(row, old_row, logic_row):
    if condition:
        return default_value
    return get_ai_value(...)

Rule.formula(derive=models.MyTable.field, calling=conditional_formula)
```

### Pattern 3: AI with Audit Trail
```python
def formula_with_audit(row, old_row, logic_row):
    audit_logic_row = logic_row.new_logic_row(models.AuditTable)
    audit_logic_row.link(to_parent=logic_row)
    audit_logic_row.insert(reason="AI")
    return audit_logic_row.row.computed_value  # From event handler

def audit_event(row, old_row, logic_row):
    if logic_row.is_inserted():
        row.computed_value = call_ai_service(...)
        row.details = ...

Rule.formula(derive=models.MyTable.field, calling=formula_with_audit)
Rule.early_row_event(on_class=models.AuditTable, calling=audit_event)
```

### Pattern 4: Reusable AI Handler
```python
# ai_requests/my_handler.py
def get_ai_value(row, logic_row, ...):
    """Reusable across use cases"""
    audit_logic_row = logic_row.new_logic_row(models.Audit)
    audit_logic_row.insert(reason="AI")
    return audit_logic_row.row.value

def declare_logic():
    Rule.early_row_event(on_class=models.Audit, calling=populate_audit)

# check_credit.py
from logic.ai_requests.my_handler import get_ai_value

def my_formula(row, old_row, logic_row):
    return get_ai_value(row, logic_row, ...)
```

---

## 8. Testing Patterns

### Test AI Handler Independently:
```python
def test_ai_handler():
    session = create_test_session()
    row = create_test_item()
    logic_row = LogicRow(row, old_row=None, ins_upd_dlt="ins", nest_level=0, a_session=session, row_sets=None)
    
    result = get_ai_value(row, logic_row, ...)
    assert result == expected_value
```

### Test with Mock AI:
```python
@patch('logic.ai_requests.handler.call_ai_service')
def test_formula_with_mock_ai(mock_ai):
    mock_ai.return_value = {"value": 100}
    result = my_formula(row, old_row, logic_row)
    assert result == 100
```

---

## 9. Error Handling

### Graceful Fallback:
```python
def safe_ai_formula(row, old_row, logic_row):
    try:
        return get_ai_value(row, logic_row, ...)
    except APIKeyMissing:
        logic_row.log("API key missing, using fallback")
        return row.fallback_value
    except Exception as e:
        logic_row.log(f"AI error: {e}, using fallback")
        return row.fallback_value
```

### Audit Error Details:
```python
def ai_event_with_error_handling(row, old_row, logic_row):
    if logic_row.is_inserted():
        try:
            result = call_ai_service(...)
            row.value = result.value
            row.status = "success"
        except Exception as e:
            row.value = fallback_value
            row.status = "error"
            row.error_message = str(e)
```

---

## 10. Best Practices

1. **Imports:** Always use `from logic_bank.logic_bank import Rule`
2. **Triggered Insert:** Use `logic_row.insert()` not `session.flush()` inside formulas
3. **Reusability:** Put AI handlers in `ai_requests/` subfolder
4. **Separation:** Use case logic separate from AI handlers separate from utilities
5. **Auto-discovery:** Every module with rules needs `declare_logic()`
6. **Testing:** Test AI handlers independently with mocks
7. **Error Handling:** Always provide fallback values
8. **Audit Trail:** Use Request Pattern for observability
9. **Documentation:** Document what AI optimizes for
10. **Logging:** Use `logic_row.log()` for visibility

---

## Summary

**Core Pattern:**
- Formula calls reusable AI handler
- AI handler uses triggered insert to create audit record
- Event handler populates audit fields DURING formula
- Formula returns value from audit record
- Everything auto-discovered from `logic/logic_discovery/`

**Key Insights:**
- AI is just value computation with audit trail
- LogicBank triggered insert avoids nested flush errors
- Reusable handlers improve maintainability
- Separation of concerns enables testing
- Auto-discovery enables modularity
