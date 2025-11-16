---
title: LogicBank Patterns - The Hitchhiker's Guide
description: General patterns for working with LogicBank rules (deterministic and probabilistic)
source: Generic training for ApiLogicServer projects with GenAI integration
usage: AI assistants read this for general LogicBank patterns across ALL rule types
version: 1.0
date: Nov 14, 2025
related: 
  - logic_bank_api.prompt (deterministic rule API)
  - logic_bank_api_probabilistic.prompt (AI/probabilistic rule API)
changelog:
  - 1.0 (Nov 14, 2025): Extracted general patterns from probabilistic prompt for reuse
---

# LogicBank Patterns - The Hitchhiker's Guide

This document contains general patterns for working with LogicBank rules.
These patterns apply to ALL rule types (deterministic and probabilistic).

For specific rule APIs, see:
- `docs/training/logic_bank_api.prompt` - Deterministic rules (sum, count, formula, constraint, etc.)
- `docs/training/logic_bank_api_probabilistic.prompt` - Probabilistic rules (AI value computation)

---

=============================================================================
PATTERN 1: Event Handler Signature
=============================================================================

ALL event handlers (early_row_event, commit_row_event, row_event) receive THREE parameters.

✅ REQUIRED SIGNATURE:
```python
def my_handler(row: models.MyTable, old_row: models.MyTable, logic_row: LogicRow):
    """
    Event handler signature - ALL THREE PARAMETERS REQUIRED
    
    Args:
        row: Current state of the row (with changes)
        old_row: Previous state before changes (for detecting what changed)
        logic_row: LogicBank's wrapper with rule execution methods
    """
    logic_row.log(f"Processing {row.__class__.__name__}")
    # Your logic here
```

❌ WRONG: Trying to "get" logic_row
```python
def my_handler(row: models.MyTable):
    logic_row = LogicRow.get_logic_row(row)  # ❌ This method does NOT exist!
```

❌ WRONG: Missing parameters
```python
def my_handler(row: models.MyTable, logic_row: LogicRow):  # ❌ Missing old_row
    pass
```

REGISTRATION:
```python
# Option 1: Direct registration (LogicBank passes all three params)
Rule.early_row_event(on_class=models.MyTable, calling=my_handler)

# Option 2: Lambda wrapper (if you need to pass additional args)
Rule.early_row_event(
    on_class=models.MyTable,
    calling=lambda row, old_row, logic_row: my_handler(row, old_row, logic_row, extra_arg)
)
```

WHY THREE PARAMETERS:
- `row` - Access current values, make changes
- `old_row` - Detect what changed (if row.price != old_row.price)
- `logic_row` - Access LogicBank methods (.log(), .new_logic_row(), .insert(), etc.)

---

=============================================================================
PATTERN 2: Logging with logic_row.log()
=============================================================================

ALWAYS use logic_row.log() for rule execution logging (not app_logger).

✅ CORRECT: Use logic_row.log()
```python
def my_handler(row: models.Item, old_row, logic_row: LogicRow):
    logic_row.log(f"Processing Item - quantity={row.quantity}")
    
    if row.product.count_suppliers > 0:
        logic_row.log(f"Product has {row.product.count_suppliers} suppliers")
    else:
        logic_row.log("No suppliers available, using default price")
```

❌ WRONG: Using app_logger for rule logic
```python
def my_handler(row: models.Item, old_row, logic_row: LogicRow):
    app_logger.info(f"Item {row.id} - Product has suppliers")  # ❌ Wrong!
```

BENEFITS of logic_row.log():
- ✅ Automatic indentation showing rule cascade depth
- ✅ Grouped with related logic execution in trace output
- ✅ Visible in logic trace (helps debugging)
- ✅ No need to import logging module
- ✅ Shows execution context (which rule fired)

WHEN TO USE app_logger:
- System startup messages
- Configuration loading
- Errors outside rule execution
- Non-rule application logic

EXAMPLE OUTPUT:
```
Logic Phase:		ROW LOGIC		(sqlalchemy before_flush)			 - 2025-11-14 06:19:03,372 - logic_logger - INF
..Item[None] {Insert - client} Id: None, order_id: 1, product_id: 6, quantity: 10, unit_price: None, amount: None  row: 0x107e4a950  session: 0x107e4a8d0  ins_upd_dlt: ins - 2025-11-14 06:19:03,373 - logic_logger - INF
....Processing Item - quantity=10 - 2025-11-14 06:19:03,373 - logic_logger - INF
....Product has 2 suppliers - 2025-11-14 06:19:03,374 - logic_logger - INF
......Creating SysSupplierReq for AI selection - 2025-11-14 06:19:03,375 - logic_logger - INF
```

Note the indentation (dots) showing call depth!

---

=============================================================================
PATTERN 3: Request Pattern with new_logic_row()
=============================================================================

Use the Request Pattern for audit trails, workflows, and AI integration.

✅ CORRECT: Pass MODEL CLASS to new_logic_row
```python
def create_audit_trail(row: models.Order, old_row, logic_row: LogicRow):
    """Create audit request object using Request Pattern"""
    
    # Step 1: Create request object (pass CLASS not instance)
    request_logic_row = logic_row.new_logic_row(models.OrderAuditReq)
    
    # Step 2: Get the instance from .row property
    request = request_logic_row.row
    
    # Step 3: Set attributes on the instance
    request.order_id = row.id
    request.customer_id = row.customer_id
    request.action = "order_created"
    request.request_data = {"amount": float(row.amount_total)}
    
    # Step 4: Insert using logic_row (triggers any events on request table)
    request_logic_row.insert(reason="Order audit trail")
    
    # Step 5: Access results if needed
    logic_row.log(f"Audit created with ID {request.id}")
```

❌ WRONG: Creating instance first
```python
def create_audit_trail(row: models.Order, old_row, logic_row: LogicRow):
    # ❌ Don't create instance yourself
    request = models.OrderAuditReq()
    
    # ❌ This will fail with TypeError: object is not callable
    request_logic_row = logic_row.new_logic_row(request)
```

THE METHOD SIGNATURE:
```python
logic_row.new_logic_row(a_class: type) -> LogicRow
```

WHAT IT RETURNS:
- Returns a LogicRow wrapper (not the instance directly)
- Access instance via `.row` property
- Use returned logic_row for .insert(), .link(), etc.

WHY THIS PATTERN:
- LogicBank needs to track the new row in the session
- Enables rule execution on the new row
- Maintains parent-child relationships
- Supports cascading logic across related objects

COMMON USE CASES:
1. **Audit trails** - Track who did what when
2. **Workflows** - Create approval requests, notifications
3. **AI integration** - Create request objects for AI to populate
4. **Derived objects** - Generate summary records, reports

---

=============================================================================
PATTERN 4: Rule API Syntax Reference
=============================================================================

Always consult docs/training/logic_bank_api.prompt for complete API details.

COMMON PARAMETERS BY RULE TYPE:

Rule.sum() - NO 'calling' parameter
  Rule.sum(derive: Column, as_sum_of: any, where: Callable = None, insert_parent: bool = False)
  ✅ Use 'where' for filtering
  ❌ NO 'calling' parameter

Rule.count() - NO 'calling' parameter
  Rule.count(derive: Column, as_count_of: type, where: Callable = None, insert_parent: bool = False)
  ✅ Use 'where' for filtering
  ❌ NO 'calling' parameter

Rule.formula() - HAS 'calling' parameter (for functions only)
  Rule.formula(derive: Column, as_expression: Callable = None, calling: Callable = None, no_prune: bool = False)
  ✅ Use 'as_expression' for simple expressions
  ✅ Use 'calling' for complex functions (must be callable, not bool)
  ❌ Never use calling=False or calling=True

Rule.constraint() - HAS 'calling' parameter (for functions only)
  Rule.constraint(validate: type, as_condition: Callable = None, calling: Callable = None, error_msg: str = "")
  ✅ Use 'as_condition' for simple lambda conditions
  ✅ Use 'calling' for complex validation functions
  ❌ Never use calling=False or calling=True

Rule.copy() - NO 'calling' parameter
  Rule.copy(derive: Column, from_parent: any)

Rule.parent_check() - NO 'calling' parameter
  Rule.parent_check(validate: type, error_msg: str = "")

EXAMPLES:

✅ CORRECT: Rule.count with where
```python
Rule.count(
    derive=models.Customer.unshipped_order_count,
    as_count_of=models.Order,
    where=lambda row: row.date_shipped is None
)
```

❌ WRONG: Rule.count with calling
```python
Rule.count(
    derive=models.Customer.unshipped_order_count,
    as_count_of=models.Order,
    calling=lambda row: row.date_shipped is None  # ❌ 'calling' not valid!
)
```

✅ CORRECT: Rule.formula with conditional
```python
Rule.formula(
    derive=models.Item.unit_price,
    as_expression=lambda row: (
        row.product.unit_price if row.product.count_suppliers == 0
        else row.unit_price  # Preserve value from event
    )
)
```

❌ WRONG: Rule.formula with calling=False
```python
Rule.formula(
    derive=models.Item.unit_price,
    calling=False  # ❌ calling must be callable or omitted!
)
```

---

=============================================================================
PATTERN 5: Common Anti-Patterns (What NOT to Do)
=============================================================================

❌ DON'T: Try to "get" logic_row
```python
# This method does NOT exist
logic_row = LogicRow.get_logic_row(row)
```

❌ DON'T: Use app_logger in rule code
```python
# Use logic_row.log() instead
app_logger.info("Processing item")
```

❌ DON'T: Create instances before new_logic_row
```python
# Pass CLASS to new_logic_row, not instance
request = models.AuditReq()
logic_row.new_logic_row(request)  # ❌ TypeError!
```

❌ DON'T: Use wrong parameters for rules
```python
# Rule.count/sum/copy don't have 'calling'
Rule.count(derive=..., as_count_of=..., calling=...)  # ❌ Invalid!
```

❌ DON'T: Use calling with boolean values
```python
# calling must be a function, not bool
Rule.formula(derive=..., calling=False)  # ❌ Invalid!
```

❌ DON'T: Forget to copy AI results to target
```python
# AI populates request table, you must copy to target
request_logic_row.insert()
# ❌ Missing: row.unit_price = request.chosen_unit_price
```

❌ DON'T: Skip event handler parameters
```python
# Event handlers need all THREE parameters
def my_handler(row):  # ❌ Missing old_row and logic_row
    pass
```

---

=============================================================================
PATTERN 6: Type Handling for Database Fields
=============================================================================

When setting values in event handlers or custom code, use correct Python types for database columns.

✅ FOREIGN KEY (ID) FIELDS - Use int
```python
def my_handler(row, old_row, logic_row: LogicRow):
    # ✅ CORRECT: Foreign keys must be int for SQLite
    row.customer_id = 123  # int
    row.supplier_id = int(some_value)  # Ensure it's int
```

❌ WRONG: Using Decimal for foreign keys
```python
row.customer_id = Decimal('123')  # ❌ SQLite error: Decimal not supported for INTEGER FK
```

✅ MONETARY FIELDS - Use Decimal for precision
```python
from decimal import Decimal

def my_handler(row, old_row, logic_row: LogicRow):
    # ✅ CORRECT: Monetary values as Decimal
    row.unit_price = Decimal('19.99')
    row.amount = Decimal(str(quantity * price))  # Convert via string for precision
```

✅ PATTERN SUMMARY:
```python
# Foreign keys and IDs
if '_id' in field_name or field_name.endswith('_id'):
    value = int(value)  # Must be int for SQLite INTEGER columns

# Monetary fields  
elif '_price' in field_name or '_cost' in field_name or '_amount' in field_name:
    value = Decimal(str(value))  # Use Decimal for precision

# Other numerics
else:
    value = float(value) or int(value)  # Based on column type
```

WHY THIS MATTERS:
- SQLite INTEGER columns (foreign keys) don't support Decimal type
- Monetary calculations need Decimal to avoid floating-point errors
- Type mismatches cause "type not supported" database errors

COMMON ERRORS:
```python
# ❌ WRONG: Decimal for foreign key
row.order_id = Decimal('42')  # Database error!

# ❌ WRONG: Float for money (precision loss)
row.unit_price = 19.99  # May lose precision in calculations

# ✅ CORRECT: Proper types
row.order_id = 42  # int for FK
row.unit_price = Decimal('19.99')  # Decimal for money
```

=============================================================================
PATTERN 7: Testing and Debugging Patterns
=============================================================================

✅ USE logic_row.log() EXTENSIVELY during development
```python
def my_handler(row, old_row, logic_row: LogicRow):
    logic_row.log("=== Starting my_handler ===")
    logic_row.log(f"Row state: quantity={row.quantity}, price={row.unit_price}")
    
    if row.quantity != old_row.quantity:
        logic_row.log(f"Quantity changed: {old_row.quantity} -> {row.quantity}")
    
    # ... your logic
    
    logic_row.log(f"=== Completed my_handler, result={row.amount} ===")
```

✅ CHECK old_row to detect changes
```python
def update_handler(row, old_row, logic_row: LogicRow):
    if row.status != old_row.status:
        logic_row.log(f"Status changed: {old_row.status} -> {row.status}")
        # Take action on status change
```

✅ USE logic_row.is_inserted(), is_updated(), is_deleted()
```python
def audit_handler(row, old_row, logic_row: LogicRow):
    if logic_row.is_inserted():
        logic_row.log("New row created")
    elif logic_row.is_updated():
        logic_row.log("Row updated")
    elif logic_row.is_deleted():
        logic_row.log("Row deleted")
```

✅ TRACE rule execution with PYTHONPATH
```bash
# Enable verbose logic logging
export APILOGICSERVER_VERBOSE=True
python api_logic_server_run.py
```

---

=============================================================================
SUMMARY: Quick Reference
=============================================================================

1. **Event handlers**: def handler(row, old_row, logic_row) - ALL THREE
2. **Logging**: Use logic_row.log() not app_logger
3. **Request Pattern**: new_logic_row(ModelClass) returns LogicRow with .row
4. **Rule APIs**: Check logic_bank_api.prompt for correct parameters
5. **Anti-patterns**: No get_logic_row(), no calling=False, no app_logger in rules
6. **Type handling**: int for FKs, Decimal for money
7. **Testing**: logic_row.log(), check old_row, use is_inserted/updated/deleted

For rule-specific APIs and examples:
- Deterministic rules → docs/training/logic_bank_api.prompt
- Probabilistic rules → docs/training/logic_bank_api_probabilistic.prompt

---

END OF GENERAL PATTERNS
