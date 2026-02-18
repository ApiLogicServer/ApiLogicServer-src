# Subsystem Creation - Architectural Principles

## When to Use This Guide

Read this when creating **multiple related tables with business logic** - for example:
- Complete subsystems (customs, billing, inventory, HR)
- Complex domains (tariff calculations, order processing, financial transactions)
- Systems involving multiple entities and calculations

**Not for**: Adding single columns or simple CRUD tables without logic.

---

## Part 1: Data Model Principles

### Always Use Autoincrement Primary Keys

**✅ CORRECT:**
```python
class CustomsEntry(Base):
    __tablename__ = 'customs_entry'
    
    id = Column(Integer, primary_key=True, autoincrement=True)  # ← CRITICAL
    entry_number = Column(String, nullable=False)
    # ... other fields
```

**❌ WRONG:**
```python
class CustomsEntry(Base):
    __tablename__ = 'customs_entry'
    
    id = Column(Integer, primary_key=True)  # Missing autoincrement!
```

**Why this matters:**
- SQLite requires explicit `autoincrement=True` for proper auto-increment behavior
- Prevents ID conflicts and insertion errors
- Standard across all database engines

### Create Columns for Derived Values

If business logic calculates a value, **create a column for it in the model**.

**✅ CORRECT:**
```python
class CustomsEntry(Base):
    # Input fields
    customs_value = Column(DECIMAL, nullable=False)
    
    # Calculated fields - CREATE COLUMNS
    base_duty_amount = Column(DECIMAL)      # Will be calculated by rules
    surtax_amount = Column(DECIMAL)          # Will be calculated by rules
    duty_paid_value = Column(DECIMAL)        # Will be calculated by rules
    gst_amount = Column(DECIMAL)             # Will be calculated by rules
    total_duty_tax = Column(DECIMAL)         # Will be calculated by rules
```

**❌ WRONG:**
```python
class CustomsEntry(Base):
    customs_value = Column(DECIMAL, nullable=False)
    # Missing columns for calculated values - formulas will fail!
```

**Why this matters:**
- Rules need columns to populate
- Enables querying/filtering on calculated values
- Provides audit trail of calculations

### Table Naming Conventions

**✅ CORRECT:**
```python
class Customer(Base):           # Singular, capitalized
    __tablename__ = 'customer'  # Lowercase table name
    
class CustomsEntry(Base):       # Singular, capitalized, CamelCase
    __tablename__ = 'customs_entry'  # Lowercase, snake_case
```

**❌ WRONG:**
```python
class Customers(Base):          # Plural - wrong!
class customs_entry(Base):      # Lowercase class - wrong!
```

---

## Part 2: Business Logic Architecture

### The Golden Rule: Try HARD to Use Rules First

**Priority hierarchy:**
1. **Declarative rules** (formulas, sums, counts, constraints) - ALWAYS TRY FIRST
2. **Events** (before/after/commit events) - fallback when rules can't handle it

### Calculations Belong in Formulas, Not Events

**✅ CORRECT - Use Formulas:**
```python
# Simple calculations
Rule.formula(derive=models.CustomsEntry.base_duty_amount,
             as_expression=lambda row: 
                (row.customs_value or Decimal(0)) * 
                (row.base_duty_rate or Decimal(0)) / Decimal(100))

# Complex conditional logic (HST vs GST+PST)
Rule.formula(derive=models.CustomsEntry.gst_amount,
             as_expression=lambda row: 
                (row.duty_paid_value or Decimal(0)) * 
                ((row.province.hst_rate if row.province and row.province.hst_rate else 
                  row.province.gst_rate if row.province else Decimal(0)) / Decimal(100)))

Rule.formula(derive=models.CustomsEntry.pst_amount,
             as_expression=lambda row: 
                Decimal(0) if (row.province and row.province.hst_rate) else
                (row.duty_paid_value or Decimal(0)) * 
                ((row.province.pst_rate if row.province else Decimal(0)) / Decimal(100)))

# Dependent calculations (engine handles ordering automatically)
Rule.formula(derive=models.CustomsEntry.total_duty_tax,
             as_expression=lambda row: 
                (row.base_duty_amount or Decimal(0)) + 
                (row.surtax_amount or Decimal(0)) + 
                (row.gst_amount or Decimal(0)) + 
                (row.pst_amount or Decimal(0)))
```

**❌ WRONG - Procedural Code in Events:**
```python
# DON'T DO THIS - Calculations in row_event
def calculate_taxes(row: models.CustomsEntry, old_row, logic_row):
    province = logic_row.session.query(models.Province)...
    
    if province.hst_rate and province.hst_rate > 0:
        row.gst_amount = row.duty_paid_value * province.hst_rate / Decimal(100)
        row.pst_amount = Decimal(0)
    else:
        row.gst_amount = row.duty_paid_value * province.gst_rate / Decimal(100)
        row.pst_amount = row.duty_paid_value * province.pst_rate / Decimal(100)

Rule.row_event(on_class=models.CustomsEntry, calling=calculate_taxes)
```

**Why formulas are better:**
- ✅ **Automatic ordering** - Engine determines execution sequence based on dependencies
- ✅ **All change paths work** - If `duty_paid_value` changes, `gst_amount` recalculates automatically
- ✅ **No ordering bugs** - Can't get the sequence wrong
- ✅ **Declarative** - Shows WHAT not HOW
- ❌ **Events require manual ordering** - early_row_event → row_event → commit_row_event
- ❌ **Easy to miss change paths** - Formula dependencies not obvious in procedural code

### When to Use Events (Fallback Cases)

Events are appropriate for:

**✅ Valid Event Uses:**

1. **Audit Trail Creation** (side effect, not calculation):
```python
def create_audit_record(row: models.CustomsEntry, old_row, logic_row):
    audit = models.SysSurtaxReq(
        customs_entry_id=row.id,
        hs_code=row.hs_code.code,
        surtax_rate_found=row.surtax_rate,
        lookup_timestamp=datetime.utcnow()
    )
    logic_row.session.add(audit)

Rule.early_row_event(on_class=models.CustomsEntry, calling=create_audit_record)
```

2. **External Integrations** (Kafka, webhooks, email):
```python
def send_kafka_message(row: models.Order, old_row, logic_row):
    if row.date_shipped and not old_row.date_shipped:
        kafka_producer.send('order_shipping', row)

Rule.commit_row_event(on_class=models.Order, calling=send_kafka_message)
```

3. **Lookups That Set Values** (early_row_event pattern):
```python
def lookup_surtax_rate(row: models.CustomsEntry, old_row, logic_row):
    """Lookup and SET surtax_rate - formulas will use it"""
    if row.ship_date >= surtax_effective_date:
        rate_obj = logic_row.session.query(models.SurtaxRate)...
        row.surtax_rate = rate_obj.surtax_rate if rate_obj else Decimal(0)

Rule.early_row_event(on_class=models.CustomsEntry, calling=lookup_surtax_rate)
```

**Key distinction:** Event *sets* the rate, formula *uses* the rate to calculate amounts.

---

## Part 3: Complex Inserts - Request Pattern vs Custom API

### The Anti-Pattern: Custom API Service

**❌ WRONG - duty_calculator_service.py:**
```python
# api/api_discovery/duty_calculator_service.py
@jsonapi_rpc(http_methods=["POST"])
def calculate_duty(self, *args, **kwargs):
    """Custom API that does lookups, validation, calculation, then insert"""
    request_data = request.json["meta"]["args"]["data"]
    
    # Lookup HS code
    hs_code = session.query(HsCode).filter(...)...
    
    # Lookup surtax rate
    surtax_rate = session.query(SurtaxRate).filter(...)...
    
    # Validate
    if not hs_code:
        return {"error": "Invalid HS code"}
    
    # Calculate
    base_duty = value * base_rate / 100
    surtax = value * surtax_rate / 100
    
    # Create entry
    entry = CustomsEntry(
        hs_code_id=hs_code.id,
        base_duty_amount=base_duty,
        surtax_amount=surtax,
        ...
    )
    session.add(entry)
    return {"entry_id": entry.id}
```

**Problems:**
- 🔴 Business logic in API service (bypasses rules engine)
- 🔴 No audit trail of request vs result
- 🔴 Custom boilerplate (error handling, docs, testing)
- 🔴 Can't test logic independently
- 🔴 Multiple entry points need duplication

### The Correct Pattern: Request Object

**✅ CORRECT - Request Pattern:**

**Step 1: Create Request Table:**
```python
class SysCustomsReq(Base):
    """Request table for customs duty calculations"""
    __tablename__ = 'sys_customs_req'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # REQUEST FIELDS (user provides)
    hs_code_id = Column(ForeignKey('hs_code.id'), nullable=False)
    country_id = Column(ForeignKey('country.id'), nullable=False)
    province_id = Column(ForeignKey('province.id'), nullable=False)
    customs_value = Column(DECIMAL, nullable=False)
    ship_date = Column(Date, nullable=False)
    
    # RESPONSE FIELDS (system populates)
    customs_entry_id = Column(ForeignKey('customs_entry.id'))
    base_duty_amount = Column(DECIMAL)
    surtax_amount = Column(DECIMAL)
    total_duty_tax = Column(DECIMAL)
    calculation_status = Column(String)  # 'success', 'error'
    error_message = Column(String)
    
    # Relationships
    customs_entry = relationship("CustomsEntry")
```

**Step 2: Logic in early_row_event:**
```python
def process_customs_request(row: models.SysCustomsReq, old_row, logic_row):
    """All business logic here - validates, calculates, creates entry"""
    try:
        # Create actual entry (rules handle calculations automatically)
        entry = models.CustomsEntry(
            hs_code_id=row.hs_code_id,
            country_id=row.country_id,
            province_id=row.province_id,
            customs_value=row.customs_value,
            ship_date=row.ship_date
        )
        logic_row.session.add(entry)
        logic_row.session.flush()  # Get ID
        
        # Populate response fields (audit trail)
        row.customs_entry_id = entry.id
        row.base_duty_amount = entry.base_duty_amount
        row.surtax_amount = entry.surtax_amount
        row.total_duty_tax = entry.total_duty_tax
        row.calculation_status = 'success'
        
    except Exception as e:
        row.calculation_status = 'error'
        row.error_message = str(e)

Rule.early_row_event(on_class=models.SysCustomsReq, calling=process_customs_request)
```

**Step 3: Optional - API Wrapper (thin):**
```python
# Optional: If you want friendly API name
@jsonapi_rpc(http_methods=["POST"])
def CalculateDuty(self, *args, **kwargs):
    """Thin wrapper - just creates request"""
    request_data = request.json["meta"]["args"]["data"]
    
    req = models.SysCustomsReq(**request_data)
    session.add(req)
    session.flush()  # Triggers early_row_event with all logic
    
    return {
        "request_id": req.id,
        "entry_id": req.customs_entry_id,
        "total": float(req.total_duty_tax),
        "status": req.calculation_status
    }
```

**Benefits:**
- ✅ All logic in rules engine (governed, tested, maintained)
- ✅ Automatic audit trail (SysCustomsReq persists)
- ✅ Works from ANY entry point (API, Admin UI, batch, tests)
- ✅ Testable independently
- ✅ Single source of truth

---

## Part 4: Common Mistakes from Customs Example

### Mistake #1: Missing autoincrement

```python
# ❌ WRONG
id = Column(Integer, primary_key=True)

# ✅ CORRECT  
id = Column(Integer, primary_key=True, autoincrement=True)
```

### Mistake #2: Calculations in Events

```python
# ❌ WRONG - Procedural tax calculation in event
def calculate_taxes(row, old_row, logic_row):
    province = session.query(Province)...
    row.gst_amount = row.duty_paid_value * province.gst_rate / 100
    row.pst_amount = row.duty_paid_value * province.pst_rate / 100

# ✅ CORRECT - Declarative formulas
Rule.formula(derive=models.CustomsEntry.gst_amount,
             as_expression=lambda row: (row.duty_paid_value or 0) * 
                ((row.province.gst_rate or 0) / 100))
```

### Mistake #3: Custom API Instead of Request Pattern

```python
# ❌ WRONG - Business logic in custom API
@jsonapi_rpc(http_methods=["POST"])
def CalculateDuty():
    # 50+ lines of lookups, validation, calculation
    # No audit trail, hard to test, bypasses rules

# ✅ CORRECT - Request Pattern
# SysCustomsReq table + early_row_event
# Logic governed by rules engine, automatic audit
```

---

## Quick Reference

**When creating subsystems with multiple tables and business logic:**

1. **Data Models:**
   - `autoincrement=True` on all primary keys
   - Create columns for derived values
   - Singular capitalized class names

2. **Business Logic:**
   - Try HARD to use formulas first
   - Events only for: audit, integration, lookups that set values
   - Calculations in formulas, not events (even complex conditionals)

3. **Complex Inserts:**
   - Request Pattern (SysXxxReq + early_row_event)
   - NOT custom API services with embedded logic

4. **Ask for detailed guidance:**
   - "Should I read subsystem creation guidelines?"
   - When uncertain, consult before implementing
