# Probabilistic Logic Guide - Pattern Implementation

**Scope:** Implementing probabilistic (AI-powered) logic rules in ApiLogicServer projects.  
**Prerequisites:** Understanding of LogicBank deterministic rules (constraints, sums, formulas).  
**Related:** See `genai_logic_patterns.md` for framework-level patterns.

---

## Overview

Probabilistic logic extends deterministic rules with AI-powered decision making. The key pattern:
- **Deterministic rules:** Constraints, sums, copy - always produce same result
- **Probabilistic rules:** AI-powered formulas - results depend on data, context, external factors

**Architecture:**
```
logic/
  declare_logic.py          # Main rule declarations (loads auto-discovery)
  logic_discovery/          # Use case logic
    check_credit.py         # Deterministic + conditional AI
  ai_requests/              # Reusable AI handlers
    supplier_selection.py   # AI handler with Request Pattern
```

---

## Pattern: Conditional Formula with AI

### Basic Structure

```python
def ConditionalFormula(row, old_row, logic_row):
    """
    Conditional logic:
    - IF condition met → use deterministic calculation
    - ELSE → call AI for probabilistic computation
    """
    if simple_case(row):
        return deterministic_value(row)
    else:
        return probabilistic_value(row, logic_row)

Rule.formula(derive=models.MyTable.field, calling=ConditionalFormula)
```

### Real Example (Supplier Selection)

```python
from logic.ai_requests.supplier_selection import get_supplier_price_from_ai

def ItemUnitPriceFromSupplier(row: models.Item, old_row, logic_row):
    """
    Determine Item.unit_price:
    - IF Product has NO suppliers → copy from Product.unit_price (deterministic)
    - IF Product has suppliers → call AI to select optimal supplier (probabilistic)
    """
    if row.product.count_suppliers == 0:
        logic_row.log("Product has no suppliers, using product.unit_price")
        return row.product.unit_price  # Deterministic
    
    # Probabilistic - AI selects best supplier
    return get_supplier_price_from_ai(
        row=row,
        logic_row=logic_row,
        candidates='product.ProductSupplierList',
        optimize_for='fastest reliable delivery while keeping costs reasonable',
        fallback='min:unit_cost'
    )

Rule.formula(derive=models.Item.unit_price, calling=ItemUnitPriceFromSupplier)
```

**Key Points:**
- Formula handles BOTH deterministic and probabilistic cases
- Clear condition determines which path to take
- AI handler encapsulates complexity
- Fallback strategy always provided

---

## Request Pattern for Audit Trail

Every AI computation creates an audit record capturing:
- Request details (what was asked)
- Response details (what AI decided)
- Reasoning (why AI made that choice)
- Timestamp (when decision was made)

### Audit Table Structure

```python
class SysSupplierReq(Base):
    """Audit table for AI supplier selection"""
    __tablename__ = 'sys_supplier_req'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    item_id = Column(ForeignKey('item.id'))
    product_id = Column(ForeignKey('product.id'), nullable=False)
    
    # AI Response
    chosen_supplier_id = Column(ForeignKey('supplier.id'))
    chosen_unit_price = Column(DECIMAL)
    reason = Column(String)
    
    # Metadata
    request = Column(String)  # Optional: stores AI prompt
    created_on = Column(DateTime, server_default=func.now())
    
    # Relationships for navigation
    item = relationship("Item", back_populates="SysSupplierReqList")
    product = relationship("Product", back_populates="SysSupplierReqList")
    supplier = relationship("Supplier", back_populates="SysSupplierReqList")
```

### Implementation Pattern

**AI Handler (returns value):**
```python
def get_supplier_price_from_ai(row, logic_row, candidates, optimize_for, fallback):
    """
    Creates audit record and returns computed value.
    Event handler populates audit fields DURING this call.
    """
    # Create audit record using LogicBank triggered insert
    audit_logic_row = logic_row.new_logic_row(models.SysSupplierReq)
    audit_record = audit_logic_row.row
    audit_logic_row.link(to_parent=logic_row)
    
    # Set request context
    audit_record.product_id = row.product_id
    audit_record.item_id = row.id
    
    # Insert triggers event handler which populates chosen_* fields
    audit_logic_row.insert(reason="Supplier AI Request")
    
    # Return value populated by event handler
    return audit_record.chosen_unit_price
```

**Event Handler (populates audit):**
```python
def supplier_id_from_ai(row: models.SysSupplierReq, old_row, logic_row):
    """
    Fires DURING audit record insert.
    Computes AI decision and populates audit fields.
    """
    if not logic_row.is_inserted():
        return
    
    # Get candidates (suppliers for this product)
    suppliers = row.product.ProductSupplierList
    
    # AI computation (or fallback)
    if not has_api_key():
        min_supplier = min(suppliers, key=lambda s: s.unit_cost)
    else:
        # Load test context for INPUT conditions (world_conditions)
        test_context = load_test_context()
        world_conditions = test_context.get('world_conditions', 'normal conditions')
        
        # Call AI service with world conditions
        result = call_ai_service(
            candidates=suppliers,
            optimize_for='fastest reliable delivery',
            world_conditions=world_conditions  # Test context provides conditions, not outputs
        )
        min_supplier = result.chosen_supplier
    
    # Populate audit fields
    row.chosen_supplier_id = min_supplier.supplier_id
    row.chosen_unit_price = min_supplier.unit_cost
    row.reason = f"Selected supplier {min_supplier.supplier_id}: lowest cost at {min_supplier.unit_cost}"

def declare_logic():
    """Auto-discovery calls this to register event handler"""
    Rule.early_row_event(on_class=models.SysSupplierReq, calling=supplier_id_from_ai)
```

**Why This Works:**
1. Formula calls `get_supplier_price_from_ai()`
2. Handler creates audit record using `logic_row.insert()`
3. Insert triggers event handler `supplier_id_from_ai()`
4. Event handler computes AI decision and populates fields
5. Formula returns `audit_record.chosen_unit_price` (now populated)
6. All audit details captured in database

---

## Integration with Deterministic Rules

Probabilistic rules work seamlessly with deterministic rules:

```python
# Deterministic rules execute first
Rule.sum(derive=models.Order.amount_total, as_sum_of=models.Item.amount)
Rule.formula(derive=models.Item.amount, as_expression=lambda row: row.quantity * row.unit_price)
Rule.count(derive=models.Product.count_suppliers, as_count_of=models.ProductSupplier)

# Probabilistic rule depends on count_suppliers (deterministic)
def ItemUnitPriceFromSupplier(row, old_row, logic_row):
    if row.product.count_suppliers == 0:  # Uses deterministic count
        return row.product.unit_price
    return get_supplier_price_from_ai(...)  # Probabilistic

Rule.formula(derive=models.Item.unit_price, calling=ItemUnitPriceFromSupplier)

# Constraint applies to final result (regardless of how computed)
Rule.constraint(validate=models.Customer,
    as_condition=lambda row: row.balance <= row.credit_limit,
    error_msg="Balance exceeds credit limit")
```

**Execution Flow:**
1. Item inserted with product_id and quantity
2. count_suppliers computed (deterministic sum)
3. unit_price computed (conditional: deterministic OR probabilistic)
4. amount computed (deterministic: quantity * unit_price)
5. amount_total computed (deterministic sum)
6. balance updated (deterministic sum)
7. credit_limit constraint checked (deterministic validation)

**Key Insight:** AI decision (step 3) is just one step in the chain. All other rules remain deterministic.

---

## Testing Probabilistic Rules

### Test Without AI (Deterministic Path)
```python
def test_no_suppliers_uses_product_price():
    """When product has no suppliers, should use product.unit_price"""
    session = create_session()
    
    # Setup: Product with NO suppliers
    product = Product(id=1, name="Test", unit_price=100.00)
    product.count_suppliers = 0  # Deterministic
    
    # Test: Insert item
    item = Item(product_id=1, quantity=5)
    session.add(item)
    session.flush()
    
    # Verify: Used product.unit_price (deterministic path)
    assert item.unit_price == 100.00
    assert item.amount == 500.00
```

### Test With AI (Probabilistic Path)
```python
def test_with_suppliers_uses_ai():
    """When product has suppliers, should call AI"""
    session = create_session()
    
    # Setup: Product WITH suppliers
    product = Product(id=2, name="Test", unit_price=100.00)
    supplier1 = Supplier(id=1, name="Fast Inc")
    supplier2 = Supplier(id=2, name="Cheap Co")
    ProductSupplier(product_id=2, supplier_id=1, unit_cost=110.00)
    ProductSupplier(product_id=2, supplier_id=2, unit_cost=95.00)
    product.count_suppliers = 2  # Deterministic
    
    # Test: Insert item
    item = Item(product_id=2, quantity=5)
    session.add(item)
    session.flush()
    
    # Verify: Used AI (probabilistic path)
    assert item.unit_price in [110.00, 95.00]  # One of the suppliers
    
    # Verify: Audit record created
    audit = session.query(SysSupplierReq).filter_by(item_id=item.id).one()
    assert audit.chosen_supplier_id in [1, 2]
    assert audit.chosen_unit_price in [110.00, 95.00]
    assert audit.reason is not None
```

### Test AI Logic Independently
```python
@patch('logic.ai_requests.supplier_selection.call_ai_service')
def test_ai_handler_with_mock(mock_ai):
    """Test AI handler in isolation"""
    mock_ai.return_value = {
        'supplier_id': 2,
        'unit_cost': 95.00,
        'reason': 'Lowest cost'
    }
    
    # Create test context with INPUT conditions (not predetermined outputs)
    # Example: test_context = {'world_conditions': 'Suez Canal blocked'}
    row = create_test_item()
    logic_row = create_test_logic_row(row)
    
    # Call handler (AI will make decision based on world conditions)
    result = get_supplier_price_from_ai(row, logic_row, ...)
    
    # Verify AI was called with proper conditions
    assert result == 95.00
    assert mock_ai.called
```

---

## Common Patterns

### Pattern 1: Simple Conditional AI
```python
def my_formula(row, old_row, logic_row):
    if has_simple_answer(row):
        return simple_calculation(row)
    return get_ai_value(row, logic_row, ...)

Rule.formula(derive=models.MyTable.field, calling=my_formula)
```

### Pattern 2: AI with Fallback Strategy
```python
def robust_formula(row, old_row, logic_row):
    try:
        return get_ai_value(row, logic_row, fallback='min:cost')
    except AIError:
        return row.default_value
```

### Pattern 3: Multiple AI Decisions
```python
def complex_formula(row, old_row, logic_row):
    # First decision: supplier
    supplier_price = get_supplier_price_from_ai(...)
    
    # Second decision: route
    shipping_cost = get_route_cost_from_ai(...)
    
    return supplier_price + shipping_cost
```

### Pattern 4: AI Influences Multiple Fields
```python
def ai_event_populates_multiple_fields(row, old_row, logic_row):
    if logic_row.is_inserted():
        result = call_ai_service(...)
        row.field1 = result.value1
        row.field2 = result.value2
        row.field3 = result.value3
        row.audit_reason = result.reasoning
```

---

## Best Practices

1. **Always provide fallback:** Never let AI failure break business logic
2. **Use conditional formulas:** Check simple cases before calling AI
3. **Create audit records:** Capture every AI decision for observability
4. **Test both paths:** Test deterministic path AND AI path independently
5. **Document AI goals:** What is AI optimizing for? Make it explicit
6. **Handle errors gracefully:** Catch exceptions, log details, use fallback
7. **Use early_row_event:** Populate audit fields before other rules need them
8. **Leverage relationships:** Navigate to candidates via SQLAlchemy relationships
9. **Keep handlers reusable:** One AI handler can serve multiple use cases
10. **Monitor audit tables:** Review AI decisions periodically for quality

---

## Troubleshooting

### Issue: AI not called when expected
**Check:**
- Is conditional logic correct? (`if count > 0` vs `if count == 0`)
- Are relationships loaded? (Use `row.product.ProductSupplierList`)
- Is count_suppliers computed before formula runs?

### Issue: Audit record empty or missing fields
**Check:**
- Is event handler registered? (Check `declare_logic()` called)
- Is event checking `logic_row.is_inserted()`?
- Is event handler using `early_row_event` (not `row_event`)?

### Issue: `request` and `reason` fields contain generic/incomplete data
**Problem:** Audit trail lacks actionable details for debugging/compliance
**Solution:** Populate fields in AI handler (where data exists) with complete information:
```python
# ✅ CORRECT - In AI handler, populate with full context
candidate_summary = ', '.join([f"{s.supplier.name}(${s.unit_cost})" for s in suppliers])
row.request = f"Select supplier for {product.name}: Candidates=[{candidate_summary}], World={world}"
row.reason = f"AI: {supplier_name} (${price}) - {ai_explanation}"

# ❌ WRONG - Generic constants with no business context
row.request = "Select supplier"
row.reason = "AI selection"
```
**Key:** Include supplier names, prices, world conditions - not just IDs

### Issue: "AttributeError: 'NoneType' object has no attribute 'product_id'" on delete
**Problem:** Early events fire on delete but `old_row` is None
**Solution:** Check `is_deleted()` FIRST before accessing `old_row`:
```python
def my_early_event(row, old_row, logic_row):
    # ✅ CORRECT - Check delete first
    if logic_row.is_deleted():
        return
    
    # Now safe to access old_row
    if row.product_id != old_row.product_id:
        # handle change
        pass
```
**Rule:** ALL early events that access `old_row` MUST check `is_deleted()` first

### Issue: "Session is already flushing" error
**Solution:** Use LogicBank triggered insert pattern:
```python
# ❌ WRONG
session.add(audit)
session.flush()

# ✅ CORRECT
audit_logic_row = logic_row.new_logic_row(models.Audit)
audit_logic_row.insert(reason="AI")
```

### Issue: Audit record created but value not returned
**Check:**
- Does event handler populate fields BEFORE formula returns?
- Is event handler using `early_row_event` (runs during insert)?
- Does formula return value from audit record? (`return audit_record.field`)

---

## Test Context: Input Conditions vs Output Mocking

**CRITICAL DISTINCTION:** Test context provides INPUT CONDITIONS for AI, NOT predetermined outputs.

**Purpose:**
- Test how AI responds to different scenarios (e.g., "Suez Canal blocked")
- Verify AI considers world conditions in its decision-making
- Enable repeatable testing with varying conditions

**Example Test Context (config/ai_test_context.yaml):**
```yaml
# ✅ CORRECT - Provides input conditions
world_conditions: "Suez Canal blocked, alternate routes required"

# ❌ WRONG - Predetermines outputs (defeats AI testing)
# selected_supplier_id: 2  # Don't do this!
```

**How It Works:**
1. Load test context for `world_conditions`
2. Pass conditions to AI prompt
3. AI makes decision based on those conditions
4. Verify AI selected appropriate supplier given the conditions

**Testing Strategy:**
- **Normal conditions:** AI should optimize for cost
- **Disrupted conditions:** AI should prioritize reliability/alternate routes
- **No API key:** System uses fallback (min cost)

**Key Insight:** Test context lets you verify AI adapts to different scenarios WITHOUT mocking the AI itself.

---

## Summary

**Probabilistic Logic Pattern:**
1. Conditional formula decides deterministic vs AI
2. AI handler creates audit record using triggered insert
3. Event handler populates audit fields with AI decision
4. Formula returns value from audit record
5. All audit details captured for observability

**Key Benefits:**
- Seamless integration with deterministic rules
- Full audit trail of AI decisions
- Test context for scenario-based testing
- Graceful fallback when AI unavailable
- Testable at multiple levels
- Reusable AI handlers across use cases

**Remember:**
- Probabilistic rules are still rules - they participate in multi-table transactions
- AI decisions are atomic with database updates
- Audit trails enable debugging and quality monitoring
- Fallback strategies ensure business continuity
