# Request Pattern

## Pattern Definition

The **Request Pattern** is a database table design where:
- **Request fields** contain user-provided input parameters (e.g., `product_id`, `hs_code_id`, `value_amount`)
- **Response fields** contain system-computed outputs (e.g., `chosen_supplier_id`, `duty_amount`, `reason`)
- A **row event** fires during commit, performs all the work, and populates response fields

**Far preferable to creating a service** — better encapsulation. Logic stays in the rules layer, not scattered across API endpoints. The API is a thin wrapper that just inserts the row.

### Is this the Request Pattern?

| Situation | Pattern? |
|---|---|
| `SysSupplierReq` insert → `early_row_event` → populates `chosen_supplier_id` → caller reads it back | ✅ Yes — classic Request Pattern |
| `SysEmail` insert → `commit_row_event` → sends email, no response fields | ❌ No — this is a **fire-and-forget event handler**. The `Sys`-prefix table is just a trigger; there's no result returned to the caller |

**The defining characteristic is response fields read back by the caller.** If the caller inserts and never reads back a result, it's a fire-and-forget event — not the Request Pattern.

### Common Use Cases
- AI/LLM calls (supplier selection, pricing)
- Email / Kafka / external API calls
- Complex calculations (duties, taxes)

---

## Choosing the Event

| Event | When to Use |
|-------|-------------|
| `early_row_event` | Response fields must feed back into other rules (e.g., AI selects supplier → `Item.unit_price` uses result) |
| `after_flush_row_event` | Side-effect only — no return value needed (e.g., send email, publish to Kafka) |

---

## Recognition Signal

Apply this pattern when: *"user provides input → system performs integration service → result should be persisted"*

✅ Use when:
- Output needs an audit trail (compliance, debugging)
- Same logic must work from API, Admin UI, batch jobs, tests
- Logic involves external calls or complex multi-step calculations

❌ Don't use when:
- Simple CRUD with no computation
- Pure read-only queries

---

## Model Structure

```python
class DutyCalculation(Base):
    __tablename__ = 'duty_calculation'
    _s_collection_name = 'DutyCalculation'

    id = Column(Integer, primary_key=True, autoincrement=True)

    # Request fields (user provides on insert)
    hs_code_id       = Column(Integer, ForeignKey('hs_code.id'), nullable=False)
    origin_country_id = Column(Integer, ForeignKey('country.id'), nullable=False)
    value_amount     = Column(DECIMAL(15, 2), nullable=False)

    # Response fields (populated by row event)
    duty_rate        = Column(DECIMAL(5, 2))
    duty_amount      = Column(DECIMAL(15, 2))
    tax_amount       = Column(DECIMAL(15, 2))
    total_amount     = Column(DECIMAL(15, 2))
    program_applied  = Column(String(100))
    created_date     = Column(DateTime, default=datetime.now)
```

---

## Row Event Implementation

```python
Rule.early_row_event(
    on_class=models.DutyCalculation,
    calling=populate_duty_calculation
)

def populate_duty_calculation(row: models.DutyCalculation, old_row, logic_row):
    if not logic_row.is_inserted():
        return

    # 1. Look up reference data
    tariff = logic_row.session.query(models.TariffRate).filter(
        models.TariffRate.hs_code_id == row.hs_code_id,
        models.TariffRate.origin_country_id == row.origin_country_id
    ).first()
    if not tariff:
        raise ValueError(f"No tariff found for hs_code {row.hs_code_id}")

    # 2. Populate response fields
    row.duty_rate       = tariff.duty_rate
    row.program_applied = tariff.program_name
    row.duty_amount     = Decimal(str(row.value_amount)) * tariff.duty_rate / 100
    row.tax_amount      = Decimal(str(row.value_amount)) * tariff.additional_tax / 100
    row.total_amount    = row.duty_amount + row.tax_amount
```

For **side-effect only** (email, Kafka) — where the caller never reads a result back — use `after_flush_row_event` instead. This is a related but simpler pattern (**fire-and-forget**), not the full Request Pattern.

---

## Thin API Wrapper

```python
@app.route('/api/DutyCalculatorEndpoint/CalculateDuty', methods=['POST'])
def calculate_duty():
    data = request.json
    row = models.DutyCalculation(
        hs_code_id=data['hs_code_id'],
        origin_country_id=data['origin_country_id'],
        value_amount=data['value_amount']
    )
    session.add(row)
    session.commit()  # early_row_event fires here, populates response fields
    return jsonify({'total_amount': float(row.total_amount), 'program': row.program_applied})
```

❌ **Anti-pattern:** Logic in the API service. This bypasses the rules engine, breaks Admin UI support, duplicates logic across entry points, and loses the audit trail.

---

## Wrapper Function (Optional — for Rule.formula integration)

When a `Rule.formula` needs to call the pattern (e.g., AI supplier selection setting `Item.unit_price`):

```python
def get_unit_price_from_ai(row, old_row, logic_row, fallback='first:id,asc') -> Decimal:
    """Wrapper: hides Request Pattern complexity, returns computed value."""
    if row.product.count_suppliers == 0:
        return row.product.unit_price  # deterministic fallback
    req = models.SysSupplierReq(product_id=row.product_id, item_id=row.id)
    logic_row.new_logic_row(req)    # triggers early_row_event synchronously
    return req.chosen_unit_price    # response field now populated

Rule.formula(derive=models.Item.unit_price, calling=get_unit_price_from_ai)
```

`logic_row.new_logic_row()` runs the nested insert synchronously — early_row_event fires, populates `chosen_unit_price`, then control returns to the wrapper.

---

## Benefits

| | Without Pattern | With Pattern |
|--|--|--|
| Audit trail | ❌ Transient | ✅ Every request persisted |
| Entry points | ❌ API only | ✅ API, Admin UI, batch, tests |
| Logic location | ❌ Scattered | ✅ Single early_row_event |
| Governance | ❌ None | ✅ Rules chain after event |
| Testability | ❌ Requires HTTP | ✅ Insert model directly |
