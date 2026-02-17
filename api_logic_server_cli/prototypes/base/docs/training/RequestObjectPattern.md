# Request Pattern

## Pattern Definition

The **Request Pattern** is a database table design where:
- **Request fields** contain user-provided input parameters (e.g., product_id, item_id, hs_code_id)
- **Response fields** contain system-computed outputs (e.g., chosen_supplier_id, duty_amount, reason)
- An **early_row_event** handler performs all business logic during insert/update

This pattern creates a persistent audit trail while keeping business logic encapsulated in declarative rules rather than API services.

### Common Use Cases
The Request Pattern is commonly used for **integration services** that require:
- 🤖 **AI/LLM calls** (supplier selection, pricing recommendations)
- 📧 **Email services** (template rendering, sending)
- 📨 **Messaging** (Kafka, RabbitMQ publishing)
- 🌐 **External API calls** (payment gateways, shipping carriers)
- 🧮 **Complex calculations** (customs duties, tax computations)

### Core Principle
> **Logic lives in `early_row_event`, not in API service code**

The API's role is simply to insert a row with request fields populated. The `early_row_event` fires during the insert and:
1. Looks up reference data
2. Performs calculations/derivations
3. Calls external services (AI, pricing, email, etc.)
4. Populates response fields

### Unified Deterministic/Probabilistic Architecture

The Request Pattern enables a powerful architectural principle:

> **Not AI *vs* Rules — AI and Rules together.**

Different kinds of logic call for different tools in a unified model:

- **Deterministic Logic** — logic that must always be correct, consistent, and governed  
  - *Example:* "Customer balance must not exceed credit limit"
  - *Implementation:* Constraint rules, formula rules - no AI/LLM involvement

- **Probabilistic Logic (AI)** — logic that benefits from reasoning, adaptation, and creativity  
  - *Example:* "Which supplier can deliver if Suez Canal is blocked?"
  - *Implementation:* Request Pattern with AI call in early_row_event

**The Request Pattern enables governance of AI decisions:**
1. Formula calls wrapper function (deterministic: check if suppliers exist)
2. Wrapper creates Request Pattern row (AI: select optimal supplier)
3. early_row_event calls AI and populates response fields
4. AI result returned to calling formula
5. Standard rules continue: Item.amount → Order.amount_total → Customer.balance
6. Constraint rules enforce limits (deterministic governance of AI decision)

**Creative reasoning needs boundaries. Deterministic rules supply the guardrails that keep AI outcomes correct, consistent, and governed.**

## Pattern Recognition

Apply this pattern when you see:

✅ **Use Request Pattern when:**
- User provides input parameters to trigger a process
- System needs to compute/derive outputs from inputs
- Business logic involves **integration services**: lookups, calculations, AI, external APIs, messaging, email
- Result needs to be persisted (audit trail, history, debugging, compliance)
- Multiple entry paths exist (API, Admin UI, batch jobs, other services)
- Logic should be testable independently of API

🎯 **Key Recognition Signal**: *"Insert a row, where logic provides integration services with automatic request auditing"*

### AI Intelligent Selection Pattern

A common specialization of the Request Pattern for AI integration:

**Pattern**: Invoke AI providing a prompt (*find optimal based on \<criteria\>*) and a *list of candidates*. AI computes the selected object.

**Examples**:
1. **Supplier Selection** - AI selects from available suppliers based on cost, lead time, and world conditions (e.g., "Suez Canal blocked")
2. **Shipping Carrier/Route Selection** - AI picks optimal carrier considering delays, weather, costs
3. **Dynamic Pricing/Discount Strategy** - AI determines pricing based on inventory, competition, customer value
4. **Task/Resource Assignment** - AI assigns tasks to team members based on skills, workload, deadlines
5. **Inventory Sourcing/Replenishment** - AI decides which warehouse or supplier to use

**Implementation**: Request Pattern where early_row_event queries candidates, calls AI with options + context, populates chosen_* response fields.

❌ **Don't use when:**
- Simple CRUD without computation or external calls
- Transient operations with no audit requirement
- Pure read-only queries
- Stateless transformations

## Recognition Examples

### Duty Calculation (Current Project)

**User Request:** "Calculate duties and taxes for steel import from China valued at $100,000"

**Request Fields (User Provides):**
- `hs_code_id` - Harmonized System code identifier
- `origin_country_id` - Country of origin  
- `value_amount` - Customs value

**Response Fields (System Computes):**
- `duty_rate` - Applicable duty percentage (looked up)
- `additional_tax` - Additional tax percentage (looked up)
- `program_applied` - Tariff program name (looked up)
- `duty_amount` - Calculated duty (derived)
- `tax_amount` - Calculated tax (derived)
- `total_amount` - Total cost (derived)

**Business Logic Pipeline (in early_row_event):**
1. Lookup tariff rate based on HS code and origin country
2. Populate duty_rate, additional_tax, program_applied from tariff
3. Calculate duty_amount = value_amount × duty_rate
4. Calculate tax_amount = value_amount × additional_tax
5. Calculate total_amount = duty_amount + tax_amount

### AI Supplier Selection (from probabilistic_logic_guide.md)

**User Request:** "Add order item for Product X with quantity 5"

**Request Fields (User Provides):**
- `product_id` - Product being ordered
- `item_id` - Order item reference

**Response Fields (System Computes):**
- `chosen_supplier_id` - AI-selected supplier
- `chosen_unit_price` - Supplier's unit cost
- `reason` - AI explanation for choice

**Business Logic Pipeline (in early_row_event):**
1. Query available suppliers for the product
2. Call AI service with supplier options and context
3. AI selects optimal supplier (cost, delivery, reliability)
4. Populate chosen_supplier_id, chosen_unit_price, reason
5. Return chosen_unit_price to calling formula

## Implementation Pattern

### Model Structure
```python
class DutyCalculation(SAFRSBase, Base):
    """Request Object: User provides request fields, logic populates response fields"""
    
    # Request Fields (user provides)
    hs_code_id = Column(Integer, ForeignKey('hs_code.id'), nullable=False)
    origin_country_id = Column(Integer, ForeignKey('country.id'), nullable=False)
    value_amount = Column(DECIMAL(15,2), nullable=False)
    
    # Response Fields (computed by early_row_event)
    duty_rate = Column(DECIMAL(5,2))
    additional_tax = Column(DECIMAL(5,2))
    duty_amount = Column(DECIMAL(15,2))
    tax_amount = Column(DECIMAL(15,2))
    total_amount = Column(DECIMAL(15,2))
    program_applied = Column(String(100))
    
    created_date = Column(DateTime, default=datetime.now)
```

### Business Logic (early_row_event)
```python
Rule.early_row_event(
    on_class=models.DutyCalculation, 
    calling=populate_duty_calculation
)

def populate_duty_calculation(row: models.DutyCalculation, old_row, logic_row):
    """
    Request Object Pattern: Perform complete business logic pipeline.
    Fires DURING insert before any other rules.
    """
    if logic_row.is_inserted() or logic_row.is_updated():
        # 1. Lookup reference data
        tariff = logic_row.session.query(models.TariffRate).filter(
            models.TariffRate.hs_code_id == row.hs_code_id,
            models.TariffRate.origin_country_id == row.origin_country_id,
            models.TariffRate.effective_date <= datetime.now()
        ).order_by(models.TariffRate.effective_date.desc()).first()
        
        if not tariff:
            raise ValueError(f"No tariff found for HS Code {row.hs_code_id} from Country {row.origin_country_id}")
        
        # 2. Populate response fields from lookup
        row.duty_rate = tariff.duty_rate
        row.additional_tax = tariff.additional_tax
        row.program_applied = tariff.program_name
        
        # 3. Calculate derived values
        row.duty_amount = Decimal(str(row.value_amount)) * (Decimal(str(row.duty_rate)) / 100)
        row.tax_amount = Decimal(str(row.value_amount)) * (Decimal(str(row.additional_tax)) / 100)
        row.total_amount = row.duty_amount + row.tax_amount
```

### API Service (Thin Wrapper)
```python
@app.route('/api/DutyCalculatorEndpoint/CalculateDuty', methods=['POST'])
def calculate_duty():
    """
    CORRECT Pattern: API just inserts with request fields.
    early_row_event performs all lookups and calculations.
    """
    data = request.json
    
    # Simple validation
    if not all(k in data for k in ['hs_code_id', 'origin_country_id', 'value_amount']):
        return jsonify({'error': 'Missing required fields'}), 400
    
    # Insert with request fields only - logic does the rest
    duty_calc = models.DutyCalculation(
        hs_code_id=data['hs_code_id'],
        origin_country_id=data['origin_country_id'],
        value_amount=data['value_amount']
    )
    session.add(duty_calc)
    session.commit()
    
    # Return populated object (response fields filled by early_row_event)
    return jsonify({
        'id': duty_calc.id,
        'duty_amount': float(duty_calc.duty_amount),
        'tax_amount': float(duty_calc.tax_amount),
        'total_amount': float(duty_calc.total_amount),
        'program_applied': duty_calc.program_applied
    })
```

### ❌ Anti-Pattern: Logic in API Service
```python
# WRONG: Do NOT do this
@app.route('/api/DutyCalculatorEndpoint/CalculateDuty', methods=['POST'])
def calculate_duty_wrong():
    """
    ANTI-PATTERN: API contains business logic.
    
    Problems:
    1. Logic won't work from Admin UI or batch jobs (duplication required)
    2. Bypasses rules engine governance
    3. No automatic audit trail
    4. Hard to test without HTTP calls
    5. Can't chain with other declarative rules
    """
    data = request.json
    
    # API doing lookups (should be in early_row_event)
    hs_code = session.query(models.HSCode).filter_by(code=data['hs_code']).first()
    country = session.query(models.Country).filter_by(iso_code=data['country']).first()
    tariff = session.query(models.TariffRate).filter(
        models.TariffRate.hs_code_id == hs_code.id,
        models.TariffRate.origin_country_id == country.id
    ).first()
    
    # API doing calculations (should be in early_row_event)
    duty_amount = Decimal(data['value']) * (tariff.duty_rate / 100)
    tax_amount = Decimal(data['value']) * (tariff.additional_tax / 100)
    
    # Creates record with everything precomputed (bypasses logic layer)
    duty_calc = models.DutyCalculation(
        hs_code_id=hs_code.id,
        origin_country_id=country.id,
        value_amount=data['value'],
        duty_rate=tariff.duty_rate,  # Pre-populated (bypasses rules)
        duty_amount=duty_amount,      # Pre-calculated (bypasses rules)
        tax_amount=tax_amount         # Pre-calculated (bypasses rules)
    )
    session.add(duty_calc)
    session.commit()
    # This bypasses early_row_event logic entirely!
    # No governance, no audit of the integration decision, no rule chaining
```

## Benefits

### 1. Single Source of Truth
Business logic lives in one place (early_row_event), not scattered across API services, SQL scripts, and UI code.

### 2. Works from Any Entry Point
- ✅ REST API calls
- ✅ Admin UI manual inserts
- ✅ Batch imports
- ✅ Tests
- ✅ Other microservices

All use the SAME logic automatically.

### 3. Automatic Audit Trail
Every computation is persisted with:
- Input parameters (request fields)
- Computed results (response fields)
- Timestamp
- User context (if linked)

Perfect for compliance, debugging, and analysis.

### 4. Testable Business Logic
```python
def test_chinese_steel_duty():
    """Test duty calculation without API"""
    duty = models.DutyCalculation(
        hs_code_id=1,         # Steel
        origin_country_id=2,  # China
        value_amount=100000
    )
    session.add(duty)
    session.flush()  # Triggers early_row_event
    
    # Verify computed values
    assert duty.duty_amount == 25000  # 25% duty
    assert duty.tax_amount == 25000   # 25% Section 301 tax
    assert duty.total_amount == 50000
    assert duty.program_applied == "Section 232 + Section 301"
```

### 5. Eliminates Code Duplication
Without this pattern, you'd need:
- API endpoint logic
- Admin UI custom form logic  
- Batch import scripts
- Test fixtures with precomputed values

With Request Object Pattern: **One early_row_event serves all**

## AI Service Integration Example - Supplier Selection

From **basic_demo_ai_rules_supplier** and **probabilistic_logic_guide.md**:

### The Request Pattern Table
```python
class SysSupplierReq(SAFRSBase, Base):
    """Request Pattern for AI supplier selection with automatic auditing"""
    
    # Request fields (caller provides)
    product_id = Column(Integer, ForeignKey('product.id'))
    item_id = Column(Integer, ForeignKey('item.id'))
    
    # Response fields (populated by early_row_event that calls AI)
    chosen_supplier_id = Column(Integer, ForeignKey('supplier.id'))
    chosen_unit_price = Column(DECIMAL(10,2))
    reason = Column(String(500))  # AI explanation
    request = Column(String(2000))  # Full AI request for debugging
    created_date = Column(DateTime)
```

### The early_row_event - Integration Service
```python
Rule.early_row_event(
    on_class=models.SysSupplierReq,
    calling=select_supplier_via_ai
)

def select_supplier_via_ai(row: models.SysSupplierReq, old_row, logic_row):
    """
    Request Pattern Implementation:
    Performs integration service (AI call) and populates response fields.
    Fires DURING insert - before commit, enabling governance by other rules.
    """
    if logic_row.is_inserted():
        # 1. Get world conditions from config
        world_conditions = load_world_conditions()  # e.g., "Suez Canal blocked"
        
        # 2. Query available suppliers for the product
        suppliers = logic_row.session.query(models.ProductSupplier).filter_by(
            product_id=row.product_id
        ).all()
        
        # 3. Call AI service with supplier data + context
        ai_result = call_openai_service(
            prompt="Select optimal supplier based on cost, lead time, and world conditions",
            suppliers=[{
                'id': ps.supplier_id,
                'name': ps.supplier.name,
                'cost': float(ps.unit_cost),
                'lead_time': ps.lead_time_days,
                'region': ps.supplier.region
            } for ps in suppliers],
            world_conditions=world_conditions
        )
        
        # 4. Populate response fields with AI decision
        row.chosen_supplier_id = ai_result['supplier_id']
        row.chosen_unit_price = Decimal(str(ai_result['unit_cost']))
        row.reason = ai_result['reasoning']
        row.request = ai_result['full_request']  # Audit the prompt
```

### The Wrapper Function - Hiding Complexity
```python
def get_supplier_selection_from_ai(row, old_row, logic_row, 
                                    fallback: str = 'first:id,asc') -> Decimal:
    """
    Wrapper Function: Hides Request Pattern complexity from caller.
    
    Called by: early_row_event on Item (set_item_unit_price_from_supplier)
    Returns: unit_price (Decimal)
    Side Effect: Creates SysSupplierReq audit record with full AI decision trail
    """
    if row.product.count_suppliers == 0:
        # Deterministic: no suppliers available, use product price
        return row.product.unit_price
    else:
        # Probabilistic: use AI to select optimal supplier
        
        # Create request row with request fields only
        supplier_req = models.SysSupplierReq(
            product_id=row.product_id,
            item_id=row.id
        )
        
        # Insert request - triggers early_row_event that calls AI
        logic_row.new_logic_row(supplier_req)
        
        # Returns with response fields populated by early_row_event
        return supplier_req.chosen_unit_price

Rule.formula(
    derive=models.Item.unit_price,
    calling=get_supplier_selection_from_ai
)
```

### Flow Summary
**Initiating Event**: Item insert or product_id change

1. **Formula fires**: `get_supplier_selection_from_ai()` wrapper function called
2. **Wrapper creates request row**: `SysSupplierReq(product_id=..., item_id=...)`
3. **Wrapper inserts**: `logic_row.new_logic_row(supplier_req)` 
4. **early_row_event fires**: `select_supplier_via_ai()` during insert
5. **Integration service runs**: AI analyzes suppliers with world context
6. **Response fields populated**: `chosen_supplier_id`, `chosen_unit_price`, `reason`, `request`
7. **Wrapper returns**: Extracts `supplier_req.chosen_unit_price`
8. **Audit persisted**: Full AI decision trail saved to `SysSupplierReq` table

Key insight: `logic_row.new_logic_row(supplier_req)` synchronously:
1. Starts a nested logic transaction
2. Fires the early_row_event `select_supplier_via_ai`
3. AI populates response fields DURING the insert (before commit)
4. Returns control with populated `supplier_req` object
5. Leaves audit record for compliance/debugging

## When to Refactor to Request Pattern

### Code Smells Indicating Need for Pattern

1. **Fat API Service**: API endpoint has 100+ lines of business logic (lookups, calculations, external calls)
2. **No Audit Trail**: Integration service calls are transient, no record of what was requested/computed
3. **Duplication**: Same integration logic in API, UI custom forms, batch scripts
4. **Hard to Test**: Can't test business logic without HTTP calls or mocking external services
5. **No Admin UI Support**: Users can't trigger integration service from Admin UI
6. **Debugging Difficulty**: When AI or external service behaves unexpectedly, no record of request/response

### Refactoring Steps

1. **Identify Request and Response Fields**
   - Request: What does user provide? (e.g., product_id, hs_code_id, value_amount)
   - Response: What does integration service compute? (e.g., chosen_supplier_id, duty_amount, reason)

2. **Create/Update Model**
   - Add response fields to existing table OR
   - Create new audit/request table (recommended for integration services)

3. **Move Integration Logic to early_row_event**
   - Extract lookups from API
   - Extract calculations from API
   - Extract external service calls (AI, messaging, email) from API
   - Add full request/response logging for audit trail

4. **Optional: Create Wrapper Function**
   - Hides Request Pattern complexity from caller
   - Creates request row, inserts via logic_row.new_logic_row()
   - Returns specific computed value from response fields

5. **Simplify API to Thin Wrapper**
   - Validate input
   - Insert with request fields only (or call wrapper function)
   - Return populated object

6. **Update Tests**
   - Test logic by inserting model directly (no API needed)
   - Test wrapper function for conditional logic paths
   - Verify audit records are created
   - No external service mocking needed for integration logic tests

## Summary

The **Request Pattern** is a fundamental architectural principle for API Logic Server applications:

🎯 **Golden Rule**: When user provides input that triggers **integration services** (AI, messaging, email, external APIs, complex calculations) with persistent result → Use Request Pattern

📋 **Implementation**: 
- Table with request fields (input) + response fields (output)
- early_row_event performs integration service and populates response fields
- Optional wrapper function hides complexity, returns specific value
- **Automatic audit trail** of every request/response for compliance and debugging

🔧 **API Role**: Thin validation wrapper that inserts request fields only

⚙️ **Logic Role**: early_row_event performs complete integration pipeline and populates response fields

🎁 **Wrapper Function**: Hides Request Pattern complexity from caller, returns computed value, creates automatic audit

✅ **Benefits**: Single source of truth, works everywhere, automatic audit, testable, no duplication, governance

## Related Patterns

- **Probabilistic Logic Pattern** (docs/training/probabilistic_logic_guide.md): Request Pattern with AI decision-making
- **Audit Table Pattern**: Request Pattern for historical tracking
- **Command Pattern**: Request Pattern represents an action/command to execute
- **Email Request Pattern**: SysEmail uses Request Pattern - queues email with template rendering in early_row_event
- **Messaging Pattern**: Kafka/messaging integration using Request Pattern for reliable async processing

## References

- **basic_demo_ai_rules_supplier**: Full implementation of AI supplier selection with Request Pattern
- **probabilistic_logic_guide.md**: Theory and examples of unified deterministic/probabilistic logic
- **Customs Duty Calculator**: Request Pattern for complex tariff calculations (this project)

## Teaching AI to Recognize This Pattern

**Context Engineering**: AI assistants (like Copilot) are not *born* understanding the Request Pattern. They need extensive context engineering to recognize when and how to apply it.

**This document is training material** to help AI assistants learn:
1. **When to recognize**: User provides input → system performs integration service → result needs audit
2. **What to suggest**: Request Pattern table + early_row_event + optional wrapper, NOT fat API
3. **How to implement**: Specific code patterns shown in examples above
4. **Why it matters**: Governance, audit, reusability, testability

**Key Teaching Points for AI**:
- ❌ Don't suggest putting business logic in API services  
- ✅ Do suggest Request Pattern when integration services are needed
- ❌ Don't suggest bypassing the rules engine by pre-computing values
- ✅ Do suggest wrapper functions to hide Request Pattern complexity
- ❌ Don't suggest transient/stateless integration calls
- ✅ Do suggest persistent audit tables with request/response fields

When AI sees code like the "Anti-Pattern" above in a project, it should proactively suggest refactoring to Request Pattern.

---

*This pattern documentation synthesizes insights from the Customs Duty Calculator architectural review, basic_demo_ai_rules_supplier, and probabilistic logic guide examples.*
