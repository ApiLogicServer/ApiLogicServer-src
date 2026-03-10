---
title: Allocate Extension — Pattern Reference
description: Rule.Allocate for distributing an amount from a Provider to Recipients, creating Allocation junction rows. Covers single-level and cascade allocation.
source: Generic training for ApiLogicServer projects with GenAI integration
usage: AI assistants read this when detecting allocation / distribution patterns in a user prompt
version: 1.2
date: March 9, 2026
related:
  - logic_bank_api.md (full rule API)
  - logic_bank_patterns.md (general patterns)
  - https://github.com/valhuber/LogicBank/wiki/Sample-Project---Allocation
changelog:
  - 1.0 (March 9, 2026): Extracted from logic_bank_api.md; added cascade variant and expanded signal phrases
  - 1.1 (March 9, 2026): Added real-world examples from LogicBank wiki; added wiki reference
  - 1.2 (March 9, 2026): 🚨 Fixed cascade timing pitfall in Variant C — Level-2 EarlyRowEvent fires BEFORE Level-1 copy/formula rules; allocators must pre-compute percent+amount; updated execution trace, allocator examples, and complete logic file to match verified production behaviour
---

# Allocate Extension — Pattern Reference

**Reference:** https://github.com/valhuber/LogicBank/wiki/Sample-Project---Allocation

=============================================================================
🌍 REAL-WORLD EXAMPLES — Why This Matters
=============================================================================

From the LogicBank wiki, Allocate has repeatedly replaced months of development:

| Domain | Pattern | Result |
|--------|---------|--------|
| **Budget → Departments → G/L** | State govt: projects allocated budget to depts, each dept cascades to GL | *Completed in a weekend; had been running for months* |
| **Bank Payment → Accounts** | Logistics company allocates bank payments to customer accounts | *Completed in a weekend; previously required 9 months* |
| **Benefits → Time Periods** | Unemployment system allocates benefits to time periods | *Eliminated hundreds of lines; minutes instead of seconds; was getting wrong answers* |
| **Bonus → Employees** | Dept receives bonus; allocated to employees | Classic proportional split |
| **Resources → Emergency Events** | Wildfire resources (personnel, bulldozers, aircraft) to incidents | Priority/availability-based |
| **Payment → Orders** | Customer pays multiple outstanding orders, oldest first | Classic draining allocation |

**The Budget → Depts → G/L example is a cascade** — exactly the same pattern as
Charge → ChargeDeptAllocation → ChargeGlAllocation in this project.

=============================================================================
🔍 PATTERN DETECTION — READ THIS FIRST
=============================================================================

**STOP before writing `Rule.copy` + `Rule.formula` for any distribution problem.**

Ask: *"Is a row being created (inserted), and does that insert need to automatically
create child rows that each receive a portion of the parent's amount?"*

If yes → **this is an Allocate pattern**.  Use `Allocate`, not `copy`/`formula`.

`copy` + `formula` derive values on rows that *already exist*.
`Allocate` *creates* the allocation rows, then rule chaining derives their values.

---

## Signal phrases — any of these in the domain prompt = use Allocate

### Classic (payment/budget style — draining)
- "allocate [payment/budget/bonus] to [orders/departments/employees]"
- "distribute [payment] across [recipients] [oldest/priority] first"
- "apply [payment] to outstanding [orders] until exhausted"
- "apply payment to invoices, oldest first"

### Proportional / percent-based (non-draining — all recipients get their full share)
- "distribute [charge/cost/expense/revenue] to [departments/GL accounts/buckets] by percent"
- "when [a charge/cost] is received, distribute to [departments/accounts]"
- "split [amount] across [recipients] according to their designated percentage"
- "[entity] covers [N]% of the cost"
- "allocate cost to departments, then each department allocates to its GL accounts"
- "charges flow to departments, then to general ledger accounts"
- "cascade allocation" / "two-level distribution" / "multi-level cost distribution"

**Key insight:** The difference between classic and proportional is only in the
`while_calling_allocator` function — the framework, schema, and `Allocate` declaration
are identical. Never use `copy`/`formula` as a substitute.

---

## Required import

```python
from logic_bank.extensions.allocate import Allocate
```

---

## Data model — 3 roles (same for all variants)

| Role | Example table | Key columns |
|------|--------------|-------------|
| Provider | Payment / Charge | Amount (the total to distribute) |
| Recipient | Order / ProjectFundingLine / DeptChargeDefinitionLine | AmountOwed or percent |
| Allocation (junction) | PaymentAllocation / ChargeDeptAllocation | AmountAllocated / amount, FK→Provider, FK→Recipient |

**► DB design conventions for junction tables — apply ALL rules from `docs/training/subsystem_creation.md`:**
- `id INTEGER PRIMARY KEY AUTOINCREMENT` on every table
- `Numeric(15,2)` for monetary `amount` columns — never `Float` or `REAL`
- `Numeric(7,4)` for `percent` columns stored as whole numbers (e.g. 50.0 = 50%)
- Columns for every derived value (`percent`, `amount`) — LogicBank needs them to exist
- Integer FK columns to parents (not string codes) — required for `Rule.copy` traversal
- Use `Decimal` (not `float`) in formula lambdas to avoid IEEE 754 drift

---

=============================================================================
VARIANT A — Classic (draining) Allocation
e.g. Payments → Orders
=============================================================================

**Pattern:** Apply a payment to orders until the payment is exhausted.
Each order receives up to its `AmountOwed`; loop stops when `AmountUnAllocated` reaches 0.

**🚨 PITFALL — `server_default` on `AmountUnAllocated` breaks allocation:**
The allocator initializes `AmountUnAllocated` from `Amount` only when it is `None`.
If the DDL column has `DEFAULT 0`, SQLAlchemy sets it to `0` before `Allocate` fires —
so `min(0, AmountOwed) = 0` and nothing is allocated.

**Fix:** Add an `early_row_event` to explicitly initialize on insert:
```python
def init_amount_unallocated(row: models.Payment, old_row: models.Payment, logic_row: LogicRow):
    if logic_row.ins_upd_dlt == "ins":
        row.AmountUnAllocated = row.Amount

# MUST be declared before Allocate:
Rule.early_row_event(on_class=models.Payment, calling=init_amount_unallocated)
```

**Required companion rules:**
```python
# AmountAllocated = min(what payment has left, what order still owes)
Rule.formula(derive=models.PaymentAllocation.AmountAllocated,
    as_expression=lambda row: min(row.Payment.AmountUnAllocated, row.Order.AmountOwed))

Rule.sum(derive=models.Order.AmountPaid, as_sum_of=models.PaymentAllocation.AmountAllocated)
Rule.formula(derive=models.Order.AmountOwed,
    as_expression=lambda row: row.AmountTotal - row.AmountPaid)
Rule.sum(derive=models.Customer.Balance, as_sum_of=models.Order.AmountOwed)
```

**Recipients function:**
```python
def unpaid_orders(provider: LogicRow):
    """Returns provider's Customer's Orders where AmountOwed > 0, oldest first."""
    customer = provider.row.Customer
    return provider.session.query(models.Order)\
        .filter(models.Order.AmountOwed > 0, models.Order.CustomerId == customer.Id)\
        .order_by(models.Order.OrderDate).all()
```

**Allocate declaration:**
```python
Allocate(provider=models.Payment,
         recipients=unpaid_orders,
         creating_allocation=models.PaymentAllocation)
```

**How it executes:**
1. Insert `Payment` → triggers `Allocate`
2. `Allocate` calls `unpaid_orders()` → sorted recipient list
3. For each Order: creates `PaymentAllocation` → rule chaining fires:
   - Formula → `AmountAllocated`; Sum → `AmountPaid`; Formula → `AmountOwed`; Sum → `Customer.Balance`
4. `AmountUnAllocated` decremented after each; loop stops when 0

---

=============================================================================
VARIANT B — Proportional (percent-based, non-draining) Allocation
e.g. Charges → Departments
=============================================================================

**Pattern:** When a charge is inserted, create one allocation row per recipient (e.g.
each `ProjectFundingLine`). Every recipient gets its full designated percentage — there
is no draining; all recipients are always processed.

**How it differs from Variant A:**
- No `AmountUnAllocated` needed on the Provider
- `while_calling_allocator` always returns `True` (never stops early)
- The formula uses `percent / 100` instead of `min(remaining, owed)`

**Required companion rules:**
```python
# percent is frozen from the funding line at charge time
Rule.copy(derive=models.ChargeDeptAllocation.percent,
          from_parent=models.ProjectFundingLine.percent)

# amount = charge.amount × percent / 100
Rule.formula(derive=models.ChargeDeptAllocation.amount,
    as_expression=lambda row:
        row.charge.amount * row.percent / Decimal(100)
        if row.charge and row.percent is not None else Decimal(0))

# roll up to audit total on the provider
Rule.sum(derive=models.Charge.total_distributed_amount,
         as_sum_of=models.ChargeDeptAllocation.amount)
```

**Recipients function:**
```python
def funding_lines_for_charge(provider: LogicRow):
    """Returns all ProjectFundingLines for this charge's project."""
    project = provider.row.project
    pfd = project.project_funding_definition if project else None
    if pfd is None:
        return []
    return provider.session.query(models.ProjectFundingLine)\
        .filter(models.ProjectFundingLine.project_funding_definition_id == pfd.id)\
        .all()
```

**Custom allocator — sets dept/FK fields and always continues:**
```python
def allocate_charge_to_dept(allocation_logic_row, provider_logic_row) -> bool:
    """
    Percent-based allocator: set allocation fields, insert, always return True.
    No draining — all recipients always receive their designated share.
    """
    allocation = allocation_logic_row.row
    funding_line = allocation_logic_row.row.project_funding_line  # linked by link()

    allocation.department_id = funding_line.department_id
    allocation.dept_charge_definition_id = funding_line.dept_charge_definition_id

    allocation_logic_row.insert(reason="Allocate charge to dept")
    return True  # always process all recipients
```

**Allocate declaration:**
```python
Allocate(provider=models.Charge,
         recipients=funding_lines_for_charge,
         creating_allocation=models.ChargeDeptAllocation,
         while_calling_allocator=allocate_charge_to_dept)
```

---

=============================================================================
VARIANT C — Cascade (two-level) Allocation
e.g. Charges → Departments → GL Accounts
=============================================================================

**Pattern:** Level-1 `Allocate` creates `ChargeDeptAllocation` rows (one per dept).
Each inserted `ChargeDeptAllocation` triggers a Level-2 `Allocate` that creates
`ChargeGlAllocation` rows (one per GL account line in that dept's charge definition).

**Why cascade works automatically:**
Each `ChargeDeptAllocation` insert is processed by LogicBank rule chaining.
The Level-2 `Allocate` is declared as an `EarlyRowEvent` on `ChargeDeptAllocation`,
so it fires as part of that same insert chain — no explicit orchestration needed.

**Level-1 companion rules** (same as Variant B above):
```python
Rule.copy(derive=models.ChargeDeptAllocation.percent,
          from_parent=models.ProjectFundingLine.percent)
Rule.formula(derive=models.ChargeDeptAllocation.amount,
    as_expression=lambda row:
        row.charge.amount * row.percent / Decimal(100)
        if row.charge and row.percent is not None else Decimal(0))
Rule.sum(derive=models.Charge.total_distributed_amount,
         as_sum_of=models.ChargeDeptAllocation.amount)
```

**Level-2 companion rules:**
```python
Rule.copy(derive=models.ChargeGlAllocation.percent,
          from_parent=models.DeptChargeDefinitionLine.percent)
Rule.formula(derive=models.ChargeGlAllocation.amount,
    as_expression=lambda row:
        row.charge_dept_allocation.amount * row.percent / Decimal(100)
        if row.charge_dept_allocation and row.percent is not None else Decimal(0))
```

**Level-2 recipients function:**
```python
def charge_def_lines_for_dept_allocation(provider: LogicRow):
    """Returns DeptChargeDefinitionLines for this dept allocation's charge definition."""
    funding_line = provider.row.project_funding_line
    if funding_line is None or funding_line.dept_charge_definition_id is None:
        return []
    return provider.session.query(models.DeptChargeDefinitionLine)\
        .filter(models.DeptChargeDefinitionLine.dept_charge_definition_id ==
                funding_line.dept_charge_definition_id)\
        .all()
```

**🚨 PITFALL — Cascade timing: Level-2 allocator fires BEFORE Level-1 copy/formula rules**

In a cascade, the Level-2 `Allocate` fires as an `EarlyRowEvent` on the Level-1 allocation row —
before `Rule.copy` and `Rule.formula` have run on that row. This means when `allocate_dept_to_gl`
reads `provider_logic_row.row.amount` (the `ChargeDeptAllocation.amount`), it sees `0`.
Consequently every `ChargeGlAllocation.amount` formula also computes to `0`.

**Fix — pre-compute percent AND amount in BOTH allocators before calling `insert()`:**

```
Actual execution order for each ChargeDeptAllocation insert:
  1. allocate_charge_to_dept() called  ← Level-1 allocator runs first
     (pre-set: percent=60, amount=60,000)
  2. allocate_dept_to_gl() called       ← Level-2 allocator runs BEFORE copy/formula below
     reads dept_alloc.amount  → must already be set in step 1
  3. Rule.copy  → ChargeDeptAllocation.percent  (overrides, same value)
  4. Rule.formula → ChargeDeptAllocation.amount (overrides, same value)
  5. Rule.copy  → ChargeGlAllocation.percent    (overrides from defn_line)
  6. Rule.formula → ChargeGlAllocation.amount   (reads dept_alloc.amount — now correct)
```

**Level-1 allocator — must pre-compute percent AND amount:**
```python
def allocate_charge_to_dept(allocation_logic_row, provider_logic_row) -> bool:
    allocation = allocation_logic_row.row
    funding_line = allocation_logic_row.row.project_funding_line  # linked by link()
    charge = provider_logic_row.row

    allocation.department_id = funding_line.department_id
    allocation.dept_charge_definition_id = funding_line.dept_charge_definition_id
    # Pre-compute so Level-2 allocator reads correct amount (fires before copy/formula)
    allocation.percent = funding_line.percent
    allocation.amount = (
        Decimal(str(charge.amount or 0)) * Decimal(str(funding_line.percent or 0)) / Decimal(100)
    )
    allocation_logic_row.insert(reason="Allocate charge to dept")
    return True
```

**Level-2 allocator — reads pre-computed amount from provider:**
```python
def allocate_dept_to_gl(allocation_logic_row, provider_logic_row) -> bool:
    allocation = allocation_logic_row.row
    defn_line = allocation_logic_row.row.dept_charge_definition_line  # linked by link()
    dept_alloc = provider_logic_row.row  # amount already set by Level-1 allocator above

    allocation.gl_account_id = defn_line.gl_account_id
    # Pre-compute so ChargeGlAllocation.amount formula sees correct value
    allocation.percent = defn_line.percent
    allocation.amount = (
        Decimal(str(dept_alloc.amount or 0)) * Decimal(str(defn_line.percent or 0)) / Decimal(100)
    )
    allocation_logic_row.insert(reason="Allocate dept amount to GL")
    return True
```

**Level-2 Allocate declaration:**
```python
Allocate(provider=models.ChargeDeptAllocation,
         recipients=charge_def_lines_for_dept_allocation,
         creating_allocation=models.ChargeGlAllocation,
         while_calling_allocator=allocate_dept_to_gl)
```

**Complete execution trace for one Charge insert:**
```
INSERT Charge($100,000)
  → Level-1 Allocate fires (EarlyRowEvent on Charge)
  → funding_lines_for_charge() → [FedLine(60%), StateLine(40%)]
  → For each funding line:

      allocate_charge_to_dept() called:
        allocation.percent = 60   ← pre-set BEFORE insert
        allocation.amount  = 60,000  ← pre-set BEFORE insert
        INSERT ChargeDeptAllocation(dept=Fed, percent=60, amount=60,000)

          ← Level-2 fires immediately (EarlyRowEvent) BEFORE copy/formula below:
          allocate_dept_to_gl() reads dept_alloc.amount = 60,000  ✓ (pre-set above)
          → INSERT ChargeGlAllocation(gl=FedLabor, percent=60×0.6=36, amount=36,000)
          → INSERT ChargeGlAllocation(gl=FedEquip, percent=60×0.4=24, amount=24,000)

          ← THEN copy/formula run on ChargeDeptAllocation (confirm/overwrite same values):
          Rule.copy  → ChargeDeptAllocation.percent = 60
          Rule.formula → ChargeDeptAllocation.amount = 60,000
          Rule.copy  → ChargeGlAllocation.percent = 60, 40 (from defn lines)
          Rule.formula → ChargeGlAllocation.amount (reads 60,000 — correct)

      allocate_charge_to_dept() called:
        allocation.percent = 40, amount = 40,000
        INSERT ChargeDeptAllocation(dept=State, percent=40, amount=40,000)
          → INSERT ChargeGlAllocation(gl=StateOps,   percent=70, amount=28,000)
          → INSERT ChargeGlAllocation(gl=StateAdmin, percent=30, amount=12,000)

  → Rule.sum → Charge.total_distributed_amount = 100,000 ✓
```

**Complete logic file** (`logic/logic_discovery/charge_distribution.py`):
```python
from decimal import Decimal
from logic_bank.logic_bank import Rule
from logic_bank.extensions.allocate import Allocate
from logic_bank.exec_row_logic.logic_row import LogicRow
from database import models


# ── Recipients ───────────────────────────────────────────────────────────────

def funding_lines_for_charge(provider: LogicRow):
    """Level-1: ProjectFundingLines for this charge's project."""
    project = provider.row.project
    pfd = project.project_funding_definition if project else None
    if pfd is None:
        return []
    return provider.session.query(models.ProjectFundingLine)\
        .filter(models.ProjectFundingLine.project_funding_definition_id == pfd.id)\
        .all()


def charge_def_lines_for_dept_allocation(provider: LogicRow):
    """Level-2: DeptChargeDefinitionLines for this dept allocation's charge definition."""
    funding_line = provider.row.project_funding_line
    if funding_line is None or funding_line.dept_charge_definition_id is None:
        return []
    return provider.session.query(models.DeptChargeDefinitionLine)\
        .filter(models.DeptChargeDefinitionLine.dept_charge_definition_id ==
                funding_line.dept_charge_definition_id)\
        .all()


# ── Custom allocators ────────────────────────────────────────────────────────

def allocate_charge_to_dept(allocation_logic_row, provider_logic_row) -> bool:
    """Level-1: pre-compute percent+amount BEFORE insert so Level-2 reads correct values."""
    allocation = allocation_logic_row.row
    funding_line = allocation_logic_row.row.project_funding_line
    charge = provider_logic_row.row
    allocation.department_id = funding_line.department_id
    allocation.dept_charge_definition_id = funding_line.dept_charge_definition_id
    allocation.percent = funding_line.percent
    allocation.amount = (
        Decimal(str(charge.amount or 0)) * Decimal(str(funding_line.percent or 0)) / Decimal(100)
    )
    allocation_logic_row.insert(reason="Allocate charge to dept")
    return True


def allocate_dept_to_gl(allocation_logic_row, provider_logic_row) -> bool:
    """Level-2: provider amount already pre-set by Level-1 allocator above."""
    allocation = allocation_logic_row.row
    defn_line = allocation_logic_row.row.dept_charge_definition_line
    dept_alloc = provider_logic_row.row
    allocation.gl_account_id = defn_line.gl_account_id
    allocation.percent = defn_line.percent
    allocation.amount = (
        Decimal(str(dept_alloc.amount or 0)) * Decimal(str(defn_line.percent or 0)) / Decimal(100)
    )
    allocation_logic_row.insert(reason="Allocate dept amount to GL")
    return True


# ── Logic declarations ───────────────────────────────────────────────────────

def declare_logic():

    # Constraint: charge requires active funding definition
    Rule.constraint(
        validate=models.Charge,
        as_condition=lambda row: (
            row.project is None
            or row.project.project_funding_definition is None
            or row.project.project_funding_definition.is_active == 1
        ),
        error_msg="Charges may only be posted to projects with an active ProjectFundingDefinition"
    )

    # Level-1 companion rules
    Rule.copy(derive=models.ChargeDeptAllocation.percent,
              from_parent=models.ProjectFundingLine.percent)
    Rule.formula(derive=models.ChargeDeptAllocation.amount,
        as_expression=lambda row:
            row.charge.amount * row.percent / Decimal(100)
            if row.charge and row.percent is not None else Decimal(0))
    Rule.sum(derive=models.Charge.total_distributed_amount,
             as_sum_of=models.ChargeDeptAllocation.amount)

    # Level-2 companion rules
    Rule.copy(derive=models.ChargeGlAllocation.percent,
              from_parent=models.DeptChargeDefinitionLine.percent)
    Rule.formula(derive=models.ChargeGlAllocation.amount,
        as_expression=lambda row:
            row.charge_dept_allocation.amount * row.percent / Decimal(100)
            if row.charge_dept_allocation and row.percent is not None else Decimal(0))

    # Level-1 Allocate — Charge → ChargeDeptAllocation
    Allocate(provider=models.Charge,
             recipients=funding_lines_for_charge,
             creating_allocation=models.ChargeDeptAllocation,
             while_calling_allocator=allocate_charge_to_dept)

    # Level-2 Allocate — ChargeDeptAllocation → ChargeGlAllocation (cascade: fires automatically)
    Allocate(provider=models.ChargeDeptAllocation,
             recipients=charge_def_lines_for_dept_allocation,
             creating_allocation=models.ChargeGlAllocation,
             while_calling_allocator=allocate_dept_to_gl)
```
