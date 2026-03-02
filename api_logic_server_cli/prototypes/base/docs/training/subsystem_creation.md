# Subsystem Creation - Architectural Principles

> **Before starting:** Read `docs/training/sample_app.md` for canonical LogicBank rule patterns
> (`Rule.sum`, `Rule.formula`, `Rule.copy`, `Rule.constraint`) with concrete worked examples,
> a dependency-chain walkthrough, and ordering notes for rules vs events/AI-Rules.

## When to Use This Guide

Read this when creating **multiple related tables with business logic** - for example:
- Complete subsystems (customs, billing, inventory, HR)
- Complex domains (tariff calculations, order processing, financial transactions)
- Systems involving multiple entities and calculations

**Not for**: Adding single columns or simple CRUD tables without logic.

---

## Governing Principle: Prompt Spec = Floor, Not Ceiling

**This is the most important principle in this guide.**

When a prompt provides an explicit column list, table spec, or FK wiring — interpret it as the **minimum anchor**: the fields the author needed to specify to ensure correct structure. It is **not a complete design**.

The prompt author is a domain expert. They wrote only what they needed to control. They omitted fields they consider "obvious" — standard rate/amount/date columns for the domain, validation constraints, audit fields. Treat omissions as **"expected by a domain expert"**, not as **"not required"**.

**Always apply domain knowledge to flesh out beyond the spec:**
- Add domain-standard fields the spec didn't mention (e.g., `base_duty_rate` on a tariff HS code table, `effective_date` on a rate table)
- Add `Rule.constraint` for `quantity > 0` and `unit_price`/`unit_value > 0` on any line item — always, without being asked
- Add `Rule.sum` for every numeric child column that rolls up to a header — always
- Add audit/traceability columns where domain convention expects them

**The failure mode to avoid:** receiving `HSCodeRate (hs_code PK, surtax_rate)` and implementing exactly two columns, stopping there. A CBSA tariff code table without `base_duty_rate` is incomplete by domain standards — the spec listed what it needed to anchor, not everything the table needs.

> *Explicit specs buy structural correctness (FK wiring, table names). Domain knowledge buys completeness (fields, constraints, rules). Both must be active simultaneously.*

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

### Lookup References: Use FK Integers, Not String Codes

When the prompt supplies lookup values as codes or names ("province code", "country of origin", "hs code", "customer name"), the transactional table stores these as **FK integer columns pointing to the lookup table's autonum `id`**. The string code/name stays only on the lookup table parent row.

**Gate — apply this when:** the value identifies a known lookup entity (country, province, HS code, product, customer).  
**Don't apply when:** the value is free text (description, notes, broker name, address line).

**✅ CORRECT — FK integers on the transactional table:**
```python
class SurtaxOrder(Base):
    __tablename__ = 'surtax_order'
    id = Column(Integer, primary_key=True, autoincrement=True)

    # Lookup references — FK integers, NOT string codes
    country_origin_id = Column(ForeignKey('country_origin.id'), nullable=False)
    province_id       = Column(ForeignKey('province.id'), nullable=False)

    # Free text — String is correct here
    importer_name = Column(String(200))
    notes         = Column(String)

    # Relationships — enable Rule.copy to traverse to parent columns
    country_origin : Mapped["CountryOrigin"] = relationship(back_populates="SurtaxOrderList")
    province       : Mapped["Province"]      = relationship(back_populates="SurtaxOrderList")

class SurtaxLineItem(Base):
    __tablename__ = 'surtax_line_item'
    id             = Column(Integer, primary_key=True, autoincrement=True)
    surtax_order_id = Column(ForeignKey('surtax_order.id'), nullable=False)
    hs_code_id      = Column(ForeignKey('hs_code_rate.id'), nullable=False)  # FK, not String

    hs_code_rate : Mapped["HSCodeRate"] = relationship(back_populates="SurtaxLineItemList")
```

**❌ WRONG — string codes stored directly on the transactional row:**
```python
class SurtaxOrder(Base):
    country_of_origin = Column(String)  # ← "DE", "US" stored as text
    province_code     = Column(String)  # ← "ON", "BC" stored as text
    # No relationships → Rule.copy impossible → forces early_row_event + session.query()
```

**Why this matters:**
- FK relationships are what `Rule.copy` traverses: `Rule.copy(derive=SurtaxLineItem.surtax_rate, from_parent=HSCodeRate.surtax_rate)` requires `hs_code_id FK → HSCodeRate.id`
- Text code storage = no parent relationship = no `Rule.copy` = forced `early_row_event + session.query()` = nested-flush risk
- Admin App auto-generates FK dropdowns for free — users pick from a list rather than typing codes
- Referential integrity enforced at the DB level

---

### Use DECIMAL/Numeric for Monetary and Rate Columns

Never use `Float` for money amounts or rates. `Float` uses IEEE 754 binary representation — it **cannot represent most decimal fractions exactly**, causing silent rounding drift that compounds across multi-row calculations. For financial and regulatory systems this is incorrect by definition.

Use SQLAlchemy `Numeric(precision, scale)` instead:

| Column type | Recommended type | Example |
|---|---|---|
| Monetary amounts | `Numeric(15, 2)` | `customs_value`, `duty_amount`, `total_tax` |
| Rates stored as fractions (0.25 = 25%) | `Numeric(8, 6)` | `surtax_rate = 0.250000`, `tax_rate = 0.130000` |
| Rates stored as percentages (25.0 = 25%) | `Numeric(7, 4)` | `surtax_rate = 25.0000`, `tax_rate = 13.0000` |

**✅ CORRECT:**
```python
from sqlalchemy import Numeric

class SurtaxLineItem(Base):
    customs_value   = Column(Numeric(15, 2), nullable=False)  # monetary amount
    duty_amount     = Column(Numeric(15, 2))                  # derived by rule
    surtax_amount   = Column(Numeric(15, 2))                  # derived by rule
    pst_hst_amount  = Column(Numeric(15, 2))                  # derived by rule

class HSCodeRate(Base):
    base_duty_rate  = Column(Numeric(8, 6))   # e.g. 0.050000 = 5%
    surtax_rate     = Column(Numeric(8, 6))   # e.g. 0.250000 = 25%
```

**❌ WRONG:**
```python
class SurtaxLineItem(Base):
    customs_value  = Column(Float)   # ← binary floating-point, not exact decimal
    duty_amount    = Column(Float)   # ← drift accumulates across line items
```

**In formulas** — normalize with `Decimal` to prevent mixed-type drift:
```python
from decimal import Decimal

# Safe: Decimal × Decimal
Rule.formula(derive=models.SurtaxLineItem.duty_amount,
    as_expression=lambda row: row.customs_value * row.hs_code_rate.base_duty_rate
        if row.customs_value and row.hs_code_rate else Decimal(0))
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

### Fire-and-Forget Events vs. Request Pattern — Choosing the Right Tool

Both are implemented as event handlers on insert, but they serve different purposes:

| Aspect | Fire-and-Forget Event | Request Pattern |
|---|---|---|
| **Event type** | `commit_row_event` | `early_row_event` |
| **Response fields** | None — no output written back | Row has output fields (`status`, `result_id`, etc.) populated by the handler |
| **Caller gets result** | No — fire and forget | Yes — caller inserts request row, then reads response fields back |
| **Use case** | Side effect: send email, push to Kafka, write to log | Integration service with return value: AI selection, external API call, duty calculation |
| **Example** | `SysEmail` insert → `commit_row_event` sends email | `SysSupplierReq` insert → `early_row_event` calls AI, writes `chosen_supplier_id` back |

**Quick rule:**
- Caller doesn't need a result back? → **fire-and-forget** `commit_row_event`
- Caller needs a result (status, ID, calculated value)? → **Request Pattern** `early_row_event` with response fields

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

### Mistake #4: Unnecessary rebuild-from-database (and venv search)

**Context:** You're adding logic to a newly-created project that includes a Request table (e.g., `SysSupplierReq`).

**❌ WRONG - Assume model is missing, search for venv:**
```
# AI looks for venv, tries to activate it...
# AI runs: genai-logic rebuild-from-database
# ...all unnecessary overhead
```

**✅ CORRECT - Check models.py first:**
```bash
grep -n 'class SysSupplierReq' database/models.py
# → line 160: class SysSupplierReq(Base):
# Model already exists — no rebuild needed
```

**Why this happens:**
- `genai-logic create` already introspects the **full database** and generates all models
- If `sys_supplier_req` was in the database at creation time, `SysSupplierReq` is already in `models.py`
- `rebuild-from-database` is only needed when you add NEW tables/columns **after** the project was created

**Key rule:** Writing logic files (`.py` files in `logic/logic_discovery/`) is **pure file editing** — no venv activation required. Only CLI commands (`genai-logic rebuild-from-database`, running the server) need the venv.

**Decision tree:**
1. Need to write/edit a logic file? → Just edit the file. No venv needed.
2. New table added to DB after project creation? → `rebuild-from-database` (needs venv).
3. Model class already in `models.py`? → Skip rebuild entirely.

---

## Part 5: Seed Data

### Canonical Approach — `alp_init.py` (Flask context + LogicBank active)

The framework ships `database/test_data/alp_init.py`. This is the correct seed pattern for AI-generated projects: runs with Flask app context so LogicBank rules fire on insert — all computed columns populated correctly, no duplicated calculation logic.

It already has the required path fix at line 4:
```python
sys.path.insert(0, str(Path(__file__).parent.parent.parent))  # ensure project root on path
```

**Run from project root:**
```bash
cd /path/to/your_project
PROJECT_DIR=$(pwd) python database/test_data/alp_init.py
# Then open the Admin App at http://localhost:5656/
```

The framework also ships `database/test_data/test_data_preamble.py` which uses `TestBase + LogicBank.activate()` (no Flask) — a valid alternative, but it writes to `database/test_data/db.sqlite` (test copy), not the live `database/db.sqlite`. Change `db_url` if using for live seeding.

> **Note:** `als genai-utils --rebuild-test-data` is for **WebGenAI projects only** — it reads `docs/*.response` JSON files generated by the WebGenAI pipeline. It is not a general seed tool and will not work for AI-generated or hand-crafted projects.

### How It Works — The Two-Step Mechanism

`models.py` already has a conditional base class switch used by `test_data_preamble.py`:
```python
if os.getenv('APILOGICPROJECT_NO_FLASK') is None:
    Base = SAFRSBaseX   # requires Flask + SAFRS
else:
    Base = TestBase     # plain declarative_base() — no Flask needed
```

`test_data_preamble.py` activates LogicBank explicitly after creating the session:
```python
os.environ["APILOGICPROJECT_NO_FLASK"] = "1"  # Step 1: swap to TestBase
# ... create engine, session ...
LogicBank.activate(session=session, activator=declare_logic.declare_logic)  # Step 2: rules active
```

**Both steps are required.** The common failure is setting step 1 without step 2:
```python
os.environ["APILOGICPROJECT_NO_FLASK"] = "1"  # ← TestBase active
# LogicBank.activate() never called  ← rules SILENT
session.add(entry)  # all computed fields remain 0
```

`alp_init.py` uses the Flask context instead — equivalent result, different mechanism.

### Common Failures

| Error | Root cause | Fix |
|---|---|---|
| `ModuleNotFoundError: No module named 'config'` | Project root not on `sys.path` | Ensure `sys.path.insert(0, str(Path(__file__).parent.parent.parent))` is the first lines — `alp_init.py` already has this |
| All computed fields are 0 | `APILOGICPROJECT_NO_FLASK=1` set but `LogicBank.activate()` never called | Add `LogicBank.activate(session=session, activator=declare_logic.declare_logic)` after session creation |
| Seed amounts drift from actual rules | Pre-computed values in raw sqlite3 script not updated when rules change | Use `alp_init.py` pattern instead — rules compute the values |
| Shell heredoc garbled (`cmdand heredoc>`) | Terminal tool mangles multi-line heredocs | Write a `.py` file with `create_file`, then run `python script.py` — never `sqlite3 db << 'SQL'` |

---

## Quick Reference

**When creating subsystems with multiple tables and business logic:**

0. **Spec = Floor, Not Ceiling:**
   - Prompt column lists are the *minimum anchor* — flesh out with domain-standard fields
   - Always add `Rule.constraint` for `quantity > 0` and `unit_price`/`unit_value > 0` on line items
   - Always add `Rule.sum` for every numeric child column that rolls up to a header
   - Domain expert omissions = "obvious to them" — not "excluded"

1. **Data Models:**
   - `autoincrement=True` on all primary keys
   - Create columns for derived values
   - Singular capitalized class names
   - Lookup references: FK integers (`province_id FK → Province.id`), not string codes
   - Monetary amounts: `Numeric(15, 2)` — never `Float` (binary drift in financial calculations)
   - Rates as fractions: `Numeric(8, 6)`; rates as percentages: `Numeric(7, 4)`

2. **Business Logic:**
   - Try HARD to use formulas first
   - Events only for: audit, integration, lookups that set values
   - Calculations in formulas, not events (even complex conditionals)

3. **Complex Inserts:**
   - Direct domain insert — LogicBank rules derive everything
   - NOT `Sys*` wrapper tables (Request Pattern = integration side-effects only)
   - NOT custom API services with embedded logic

4. **Seed Data + Admin App:**
   - Use `alp_init.py` with path fix — Flask + LogicBank active → correct computed values
   - Never shell heredocs — write a `.py` file with `create_file`, then run it
   - `APILOGICPROJECT_NO_FLASK=1` = LogicBank suppressed = zero computed fields
   - After seeding, open Admin App at `http://localhost:5656/` — this IS the runnable UI

5. **Ask for detailed guidance:**
   - "Should I read subsystem creation guidelines?"
   - When uncertain, consult before implementing
