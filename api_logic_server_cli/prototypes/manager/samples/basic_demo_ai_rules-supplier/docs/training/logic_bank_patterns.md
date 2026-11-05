---
title: LogicBank Patterns - The Hitchhiker's Guide
description: General patterns for working with LogicBank rules (deterministic and probabilistic)
source: Generic training for ApiLogicServer projects with GenAI integration
usage: AI assistants read this for general LogicBank patterns across ALL rule types
version: 1.3
date: Oct 29, 2026
related: 
  - logic_bank_api.md (deterministic rule API)
  - probabilistic_logic.md (AI/probabilistic rule API)
changelog:
  - 1.3 (Oct 29, 2026): New PATTERN 3c, "Recording Changes (Auditing)": routes a requirement that says audit / auditing / history / track changes / who changed to the right mechanism (RuleExtension.copy_row for attribute changes; a hand-written event when old and new values, who or why are needed; the Request Pattern only when a caller reads a result back). The CE had audit only under the Request Pattern (SysAuditReq), while the simpler one-rule form (nw_sample employee_audit.py) was filed as a copy technique. Also states what the engine does not do: copy_row copies the new values only, its `initialize_target` argument is accepted but never called, and the stamping handler is off by default. Verified by a blind run (Oct 29, 2026, demo_emp_types copy, Keycloak): the routing worked and Recipe B recorded old/new value, who and when. The run also showed the first draft was wrong in three places, fixed here: `.id` under Keycloak, "append-only via Grants" (impossible), and recording a decision inside a constraint.
  - 1.0 (Nov 14, 2025): Extracted general patterns from probabilistic prompt for reuse
  - 1.1 (Feb 16, 2026): Request Object Pattern
  - 1.2 (Oct 13, 2026): PATTERN 1 - added a warning that copying a signature from
    existing/commented-out code in the same file does not exempt it from this pattern's
    own typed-signature requirement. Real case (students_courses_attendance_sweep, Oct
    2026): a re-enabled early_row_event's signature was copied verbatim from a
    commented-out reference implementation already sitting in the file
    (def _update_absence_streak_and_alert(row, old_row, logic_row) - no type hints) -
    this PATTERN already showed the typed form as the required signature, but the
    AI followed the file's own existing precedent instead of this file. Caught live by
    the developer reviewing the diff, not by the authoring pass itself.
---

# LogicBank Patterns - The Hitchhiker's Guide

This document contains general patterns for working with LogicBank rules.
These patterns apply to ALL rule types (deterministic and probabilistic).

For specific rule APIs, see:
- `docs/training/logic_bank_api.md` - Deterministic rules (sum, count, formula, constraint, etc.)
- `docs/training/probabilistic_logic.md` - Probabilistic rules (AI value computation)

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

⚠️ The typed signature above is REQUIRED even when writing a function whose shape you're
copying from elsewhere in the same file — e.g. a commented-out reference implementation,
or an earlier draft. "This file already has a similar function, written untyped" is not an
exemption from this pattern; it means that existing code is itself non-conforming. Re-type
the signature per this pattern regardless of what the copied-from code looks like.
REAL CASE (students_courses_attendance_sweep, Oct 2026): a re-enabled `early_row_event` was
copied verbatim from a commented-out reference implementation already sitting in the same
file, carrying that reference's untyped `(row, old_row, logic_row)` signature forward
unchanged — caught only by the developer reviewing the diff afterward, not by the
authoring pass itself, even though this PATTERN already stated the typed form as required.

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
PATTERN 3: Request Pattern (ROP) - Integration Services
=============================================================================

**📚 Full Documentation**: See `docs/training/RequestObjectPattern.md` for comprehensive guide

**Quick Definition:**
The Request Pattern is a table design for integration services with automatic audit:
- **Request fields** = user input (e.g., product_id, hs_code_id, value_amount)
- **Response fields** = computed output (e.g., chosen_supplier_id, duty_amount, reason)
- **early_row_event** = performs integration service (AI, external API, calculations)

**When to Use:**
✅ AI decisions (supplier selection, pricing, routing)
✅ External API calls (payment gateways, shipping carriers)
✅ Messaging/Email services (Kafka, SMTP with templating)
✅ Complex calculations requiring audit (customs, tax, compliance)

**Recognition Signal in Prompts:**
- "calculate/determine/select [X] when [Y] is given"
- Integration service needed
- Compliance/audit domain

**Architecture:**
```
User/API → Insert with request fields only
         ↓
   early_row_event fires (integration service logic)
         ↓
   Populates response fields
         ↓
   Automatic audit trail persisted
```

**Benefits:**
- Single source of truth (works from API, Admin UI, batch, tests)
- Automatic audit trail for compliance
- Governed by deterministic rules
- Testable without API/HTTP
- No duplication

**Anti-Pattern:**
❌ Fat API services with business logic (bypasses rules engine, no audit, duplication)

---

**Technical Implementation with new_logic_row():**

Use `new_logic_row()` to create Request Pattern instances in event handlers.

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
PATTERN 3b: set_same_named_attributes() - Copying Between Same-Shaped Rows
=============================================================================

**Quick Definition:**
A copy mechanism, not a trigger mechanism. Inside an event handler (any kind - row_event,
commit_row_event, early_row_event, or a Request Pattern's own event), when the source row
and the new target row share column names, `set_same_named_attributes()` copies by
iterating the source row's actual attributes at runtime and matching names - not by a
hand-written list of `new_row.x = source.x` assignments.

**Why this matters more than it looks:** a hand-written list of assignments silently goes
stale the moment a new shared column is added to both tables later - nobody remembers to add
the new line. `set_same_named_attributes()` has no such list to forget; it reflects whatever
attributes exist on both rows at the moment it runs. This is the same "declarative beats
enumerated-procedural" argument the rest of this stack is built on, applied at the row-copy
level instead of the rule level.

**NOT the Request Pattern:** Request Pattern (PATTERN 3 above) exists for *data-driven*
triggers - a caller inserts a row with response fields to be read back. This is a *copy*
technique used once an event has already fired, for whatever reason (including inside a
Request Pattern's own event, when populating a response row from a source row that happens to
share its column names). Do not reach for a `Sys*`/Request Pattern table just because a copy
is needed - the copy and the trigger are separate concerns.

**Reference implementation:** `samples/nw_sample/logic/logic_discovery/employee_auditing/
employee_audit.py` - copies `Employee` into `EmployeeAudit` (same-shaped audit table) whenever
`Salary` or `Title` changes:

```python
RuleExtension.copy_row(copy_from=Employee,
                copy_to=EmployeeAudit,
                copy_when=lambda logic_row: logic_row.ins_upd_dlt == "upd" and
                        logic_row.are_attributes_changed([Employee.Salary, Employee.Title]))
```

The same file's commented-out manual equivalent shows the underlying mechanism explicitly -
useful when the copy needs to happen mid-handler rather than declared up front via
`RuleExtension.copy_row`:

```python
def audit_by_event(row: Employee, old_row: Employee, logic_row: LogicRow):
    if logic_row.ins_upd_dlt == "upd" and logic_row.are_attributes_changed([Employee.Salary, Employee.Title]):
        copy_to_logic_row = logic_row.new_logic_row(EmployeeAudit)
        copy_to_logic_row.link(to_parent=logic_row)
        copy_to_logic_row.set_same_named_attributes(logic_row)
        # copy_to_logic_row.row.attribute_name = value   # set any non-matching fields manually
        copy_to_logic_row.insert(reason="Manual Copy " + copy_to_logic_row.name)  # triggers rules...

Rule.commit_row_event(on_class=Employee, calling=audit_by_event)
```

**Also applies outside events** - e.g. a scheduled sweep (ordinary application code, not a
LogicBank rule) that queries for rows needing a companion insert: if the query result is
already shaped like the target row (same attribute names), `set_same_named_attributes()` is
the right tool for moving the query result's values onto the new row before inserting it,
same mechanical move as the audit case above.

**Where it stops helping - degrades at mismatched shapes:** this only helps for columns both
sides already agree on by name. The moment a source is a join or a differently-named result
(e.g. `student.id`, `session.id` from a query, not already named to match the target table's
`student_id`/`class_schedule_id`), there is nothing for `set_same_named_attributes()` to match
on for those fields - fall back to manual assignment for the mismatched ones. It is a
convenience for same-named columns, not a general-purpose field-mapping tool (for that, see
Row Dict Mapper in the project CE's B2B Integration section).

---

=============================================================================
PATTERN 3c: Recording Changes (Auditing)
=============================================================================

**Signals** - any of these in a requirement means "record changes": *audit, auditing, audit trail, audit log,
history, change history, version history, track changes, keep a record of, log who changed, who and when,
before and after, old value, record every override / approval / exception.*

**Route it - do not default to a Sys*Req table:**

| The requirement wants | Use |
|---|---|
| A copy of a row when some attributes change (who changed a salary or a limit, a snapshot of the new values) | `RuleExtension.copy_row` into an audit table - ONE rule (Recipe A) |
| The OLD value as well as the new, a reason, or who/when set explicitly | A hand-written event that inserts the audit row (Recipe B) |
| A decision or an event recorded (a credit controller let a document through, an approval was used) | The same event form, inserted when the decision is taken (Recipe B) |
| A caller asks for something and reads a result back | The Request Pattern (PATTERN 3) - **not** an audit |

The Request Pattern's "audit trail" benefit is a side effect of persisting a request. It is not the way to record
changes to existing data: nobody inserts a request when a limit is edited.

**The audit table** (create it with the DDL, before the rule): its own `id`, a foreign key to the audited table
(for example `employee_id`), the columns to record, and optionally `CreatedOn` / `CreatedBy`.

**Append-only cannot be enforced with Grants.** Permissions accumulate: `DefaultRolePermission` turns an access on for a
role and a `Grant` can only add to it, never take it away. Denying insert would also block the engine's own audit
inserts, which run as the request user. So any role with insert or update can add or edit history rows through the
API. Do not claim the history is immutable; list it in ad-libs (🔴) so a person decides.

**Recipe A - a snapshot of the new values when attributes change** (reference: `samples/nw_sample/logic/logic_discovery/
employee_auditing/employee_audit.py`):

```python
from logic_bank.extensions.rule_extensions import RuleExtension
from database.models import *

def declare_logic():
    RuleExtension.copy_row(copy_from=Employee,
                           copy_to=EmployeeAudit,
                           copy_when=lambda logic_row: logic_row.ins_upd_dlt == "upd" and
                                   logic_row.are_attributes_changed([Employee.Salary, Employee.Title]))
```

Like-named columns are copied and the new row is linked to its parent. Details:
- It copies the row **after** the change. It does not record the old value.
- `copy_row` has an `initialize_target` argument. As of LogicBank 1.34 it is accepted and **never called**: do not use
  it to set extra columns. Use Recipe B.

**Recipe B - old and new values, who, when, why** (the manual form, written as an event):

```python
import datetime
from logic_bank.exec_row_logic.logic_row import LogicRow
from logic_bank.logic_bank import Rule
from database import models

def _current_user_id() -> str:
    """The signed-in user's login, or 'system' when there is none (seed script, message consumer, security off).
    SQL-provider users carry the login in `id`; Keycloak users (a DotMap built from the token) carry it in `name`
    and have NO `id` - reading `.id` there returns an empty DotMap, not an error, and would be stored as 'DotMapX()'."""
    try:
        from security.system.authorization import Security
        user = Security.current_user()
        for attr in ('id', 'name'):
            value = user.get(attr) if hasattr(user, 'get') else getattr(user, attr, None)
            if value not in (None, '') and not hasattr(value, 'keys'):
                return str(value)
        return 'system'
    except Exception:
        return 'system'

def audit_credit_limit(row: models.CustomerCompany, old_row: models.CustomerCompany, logic_row: LogicRow):
    """CustomerCompany event: when credit_limit changes, records the old and new value, who and when."""
    if logic_row.is_updated() and logic_row.are_attributes_changed([models.CustomerCompany.credit_limit]):
        audit = logic_row.new_logic_row(models.CreditLimitChange)       # pass the CLASS
        audit.link(to_parent=logic_row)                                  # sets the foreign key
        audit.row.old_limit = old_row.credit_limit
        audit.row.new_limit = row.credit_limit
        audit.row.changed_by = _current_user_id()
        audit.row.changed_on = datetime.datetime.now()
        audit.insert(reason="credit limit change")                      # triggers rules on the audit row

Rule.commit_row_event(on_class=models.CustomerCompany, calling=audit_credit_limit)
```

The same shape records a **decision**: an event that does `new_logic_row(...)`, sets the columns and `insert()`s.
Put it in its own event on the row, with a guard that detects the decision itself (for example, "now over the limit,
and further over than before"), not in the branch of a constraint: a constraint is re-checked on every update of that
row, so a rename of a row that is already over the limit would record a decision that was not taken.

**Who and when.** The all-classes stamping handler (`logic/logic_discovery/system/all_classes_stamping.py`) can fill
`CreatedOn` / `CreatedBy` on any row that has those columns, but it is **off by default** (`enable_stamping := False`).
Do not assume it ran. Set `changed_by` / `changed_on` explicitly in the event, as above, or switch stamping on.
(Known problem: the handler reads `Security.current_user().id`, which under Keycloak is an empty DotMap, so stamped
`CreatedBy` / `UpdatedBy` come out as `DotMapX()`. Use `_current_user_id()` above.)
No signed-in user is a real case (seed script, message consumer): decide what to record and list it in ad-libs.

**Record the choice in ad-libs.** Which mechanism, which attributes trigger it, and (🔴) anything the requirement did
not say: whether deletes are audited, how long history is kept, who may read it.

**NOT the Request Pattern**, and not PATTERN 3b alone: 3b is how to copy between same-shaped rows once an event has
fired; this section is how to decide that a change must be recorded and which form to use.

=============================================================================
PATTERN 4: Rule API Syntax Reference
=============================================================================

Always consult docs/training/logic_bank_api.md for complete API details.

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

  🚨 PITFALL — LogicBank dependency scanner confusion in `calling=` function bodies:
  LogicBank tokenizes the function body to discover attribute dependencies. If the function
  body contains a pattern like `session.query(...).filter(... == row.project_id).first()`,
  the scanner reads `project_id).first` as the attribute name and raises:
    LBActivateException: ['Charge.project_id).first: constraint']

  Fix: extract `row.*` reads to local variables BEFORE any method-chained expressions:
  ```python
  # ❌ WRONG — scanner sees 'project_id).first' as an attribute name
  def check_funding(row, old_row, logic_row):
      project = session.query(models.Project).filter(
          models.Project.id == row.project_id).first()   # row.project_id inside chained call

  # ✅ CORRECT — extract to local variable first
  def check_funding(row, old_row, logic_row):
      project_id = row.project_id                        # scanner sees clean 'project_id'
      project = session.query(models.Project).filter(
          models.Project.id == project_id).first()       # local var, not row.attr
  ```

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
PATTERN 8: Rules vs Events — Rules Are ALWAYS Preferred
=============================================================================

**ALWAYS use declarative rules (Rule.formula, Rule.sum, Rule.count, Rule.constraint)
in preference to events. Events are for side effects only.**

LogicBank formulas order themselves automatically — you do not need an event to
control ordering. If a value is derived from other attributes or child rows, use a rule.

| Value source | Use |
|---|---|
| Derived from row attributes or child rows | `Rule.formula`, `Rule.sum`, `Rule.count` |
| Looked up from a FK parent (external to this row) | `Rule.early_row_event` — only when no rule can express it |
| External module returns multiple output fields (AI response, external API, Request Pattern) | `Rule.early_row_event` — handler sets all response fields; downstream `Rule.formula` rules consume them |
| Pure side effect (Kafka, email, audit, insert child rows) | `Rule.row_event`, `Rule.after_flush_row_event`, `Rule.commit_row_event` |

**External module exception — when `early_row_event` legitimately sets multiple row attributes:**
When an event calls an opaque external computation (AI model, third-party API, Kafka-reply handler
via the Request Pattern), the handler writes back several response fields (e.g. `matched_project_id`,
`confidence`, `reason`, `chosen_unit_price`). This is correct and by design: the external call is a
single atomic operation whose outputs are all response columns on a `Sys*` request table. Downstream
`Rule.formula` rules then consume those output columns as inputs. This is NOT the same as a `Rule.formula`
function setting multiple `row.` attributes as side-effects — that remains wrong (see logic_bank_api.md
"ONE VALUE PER FORMULA"). The distinction:
- `early_row_event` handler setting multiple fields = ✅ external module pattern (opaque computation, all fields are outputs)
- `Rule.formula` calling function setting multiple fields = ❌ side-effect anti-pattern (only the `derive=` column is tracked)

❌ WRONG — using an event to derive a value that Rule.formula/count could express:
```python
def _evaluate(row, old_row, logic_row):
    row.clvs_eligible = 1 if not any(c.is_prohibited for c in row.ShipmentCommodityList) else 0
Rule.commit_row_event(on_class=models.Shipment, calling=_evaluate)
```
This fires once on commit, never re-fires when child rows change, and bypasses all
LogicBank dependency tracking. It is always wrong for derived attributes.

✅ CORRECT — Rule.count + Rule.formula: reactive, dependency-tracked, re-fires automatically:
```python
Rule.count(derive=models.Shipment.prohibited_count, as_count_of=models.ShipmentCommodity,
           where=lambda row: row.is_prohibited == 1)
Rule.formula(derive=models.Shipment.clvs_eligible,
             as_expression=lambda row: 1 if row.prohibited_count == 0 else 0)
```

**Valid Rule event methods (side effects only):**

| Use case | Method |
|----------|--------|
| FK lookup before formulas run (no rule equivalent) | `Rule.early_row_event` |
| Append child rows during parent insert | `Rule.row_event` |
| Kafka publish / side-effect after flush | `Rule.after_flush_row_event` |
| Post-commit finalization | `Rule.commit_row_event` |

**Event firing order — two rules:**

| Scope | Order |
|-------|-------|
| Within a single `declare_logic()` | **Declaration order is guaranteed** — LogicBank appends to a plain list |
| Across files loaded by `auto_discovery` | **Non-deterministic** — `os.walk()` file order is not specified |

Consequence: if two `early_row_event` registrations on the same class live in different files,
you cannot rely on which fires first. Fix: declare both in the same `declare_logic()`, in the
required order. See `docs/training/allocate.md` Variant C for the concrete Allocate + AI case.

⚠️ Note: `Allocate` is internally a subclass of `EarlyRowEvent` — it competes in the same
ordering list as regular `early_row_events` on the same provider class.

**Why it matters:** Formulas and sums run *after* events. If your event sets a value that
a formula consumes, using the wrong event type means the formula runs on the old value —
silently, no error, wrong results.

```python
# ✅ Sets unit_price BEFORE Item.amount formula runs
Rule.early_row_event(on_class=models.Item, calling=set_unit_price)

# ✅ Sends to Kafka AFTER all rules and constraints complete
Rule.after_flush_row_event(on_class=models.Order, calling=kafka_producer.send_row_to_kafka, ...)

# ❌ Wrong for setting unit_price — formula already ran with old value
Rule.row_event(on_class=models.Item, calling=set_unit_price)
```

---

=============================================================================
SUMMARY: Quick Reference
=============================================================================

1. **Event handlers**: def handler(row, old_row, logic_row) - ALL THREE
2. **Logging**: Use logic_row.log() not app_logger
3. **Request Pattern**: new_logic_row(ModelClass) returns LogicRow with .row
4. **Rule APIs**: Check logic_bank_api.md for correct parameters
5. **Anti-patterns**: No get_logic_row(), no calling=False, no app_logger in rules
6. **Type handling**: int for FKs, Decimal for money
7. **Rules over events**: derived values → Rule.formula/sum/count; events → side effects only
8. **Testing**: logic_row.log(), check old_row, use is_inserted/updated/deleted
9. **Valid event methods**: early_row_event, row_event, after_flush_row_event, commit_row_event

For rule-specific APIs and examples:
- Deterministic rules → docs/training/logic_bank_api.md
- Probabilistic rules → docs/training/probabilistic_logic.md

---

END OF GENERAL PATTERNS
