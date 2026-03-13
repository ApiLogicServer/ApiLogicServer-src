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
- Email / Kafka / external API calls (fire-and-forget side effects with optional inputs)

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
- **Domain data entry where LogicBank rules handle derivation.** If inserting a `CustomsEntry` and rules automatically compute `duty_amount`, `tax_amount`, etc. — the insert IS the operation. No `Sys*` wrapper table is needed or correct. Adding one forces `early_row_event + session.flush()` inside a flush cycle → nested flush errors.

---

## Model Structure

Example: `SysEmail` — caller provides recipient context; event sends email (or skips if opted out).

```python
class SysEmail(Base):
    __tablename__ = 'sys_email'
    _s_collection_name = 'SysEmail'

    id          = Column(Integer, primary_key=True, autoincrement=True)

    # Request fields (caller provides on insert)
    customer_id = Column(Integer, ForeignKey('customer.id'), nullable=False)
    subject     = Column(String(200), nullable=False)
    message     = Column(String(2000), nullable=False)
    CreatedOn   = Column(DateTime, default=datetime.now)

    # No response fields — fire-and-forget; email is sent as a side effect
    customer    = relationship("Customer")
```

Example with response field: `SysSupplierReq` — AI selects supplier, writes `chosen_supplier_id` back so the calling formula can read it:

```python
class SysSupplierReq(Base):
    __tablename__ = 'sys_supplier_req'
    _s_collection_name = 'SysSupplierReq'

    id                  = Column(Integer, primary_key=True, autoincrement=True)

    # Request fields
    product_id          = Column(Integer, ForeignKey('product.id'), nullable=False)

    # Response fields (populated by early_row_event)
    chosen_supplier_id  = Column(Integer, ForeignKey('supplier.id'))
    chosen_unit_price   = Column(DECIMAL)
    reason              = Column(String)
```

---

## Row Event Implementation

**Fire-and-forget** (`SysEmail` — no response fields, side-effect only):

```python
Rule.after_flush_row_event(
    on_class=models.SysEmail,
    calling=send_email_if_not_opted_out
)

def send_email_if_not_opted_out(row: models.SysEmail, old_row, logic_row):
    if not logic_row.is_inserted():
        return
    if row.customer.email_opt_out:
        logic_row.log(f"Email skipped — {row.customer.name} opted out")
        return
    logic_row.log(f"email sent to {row.customer.email}: {row.subject}")
    # email_service.send(to=row.customer.email, subject=row.subject, body=row.message)
```

**With response fields** (`SysSupplierReq` — AI result read back by caller):

```python
Rule.early_row_event(
    on_class=models.SysSupplierReq,
    calling=select_supplier_via_ai
)

def select_supplier_via_ai(row: models.SysSupplierReq, old_row, logic_row):
    if not logic_row.is_inserted():
        return
    # call AI, populate response fields
    result = ai_service.choose_supplier(product_id=row.product_id)
    row.chosen_supplier_id = result.supplier_id
    row.chosen_unit_price  = result.unit_price
    row.reason             = result.rationale
```

---

## Thin API Wrapper (optional)

For fire-and-forget (email), the Admin App insert IS sufficient — no API wrapper needed.

For cases where a REST caller needs a named endpoint that reads response fields back:

```python
@app.route('/api/SysSupplierReqEndpoint/SelectSupplier', methods=['POST'])
def select_supplier():
    data = request.json['meta']['args']['data']
    row = models.SysSupplierReq(product_id=data['product_id'])
    session.add(row)
    session.commit()  # early_row_event fires, populates chosen_supplier_id etc.
    return jsonify({'supplier_id': row.chosen_supplier_id,
                    'unit_price': float(row.chosen_unit_price),
                    'reason': row.reason})
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
