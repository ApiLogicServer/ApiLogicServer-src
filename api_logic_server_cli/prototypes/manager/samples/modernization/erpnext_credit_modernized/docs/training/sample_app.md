---
title: Sample App — Canonical Pattern Reference
description: Worked example of basic_demo patterns (Customer/Order/Item/Product) as explicit CE few-shot examples
usage: AI assistants read this to understand canonical LogicBank patterns before generating a new domain subsystem
version: 1.0 (March 2026)
AI-Assistants: Read this file to internalize the canonical patterns. Then apply the PATTERNS to your domain — do NOT copy the entity names (Customer, Order, Item, Product). Your domain's header/detail/reference tables will have different names.
---

# Sample App — Canonical Pattern Reference

> **🤖 HOW TO USE THIS FILE**
> This file provides **canonical code examples** for the five core LogicBank patterns, using the
> `Customer → Order → Item / Product` domain as a concrete worked example.
> **Use the patterns. Do not copy the entity names.**
> Your domain will have different entities (e.g., `CustomsEntry → SurtaxLineItem / HSCodeRate`),
> but the same structural patterns apply directly.

---

## Why This File Exists

The `basic_demo` schema (`Customer → Order → Item / Product`) has historically been the most
reliable source of correct LogicBank pattern generation. When this schema was present as database
artifacts, AI assistants used it as implicit few-shot examples and produced correct results.
When it was absent (clean `starter.sqlite`), quality degraded significantly.

This file makes those patterns **explicit and deliberate** — a permanent few-shot reference
independent of what database is used.

---

## The Canonical Schema

Four tables demonstrating the three structural roles every subsystem needs:

| Role | Example table | Your domain equivalent |
|---|---|---|
| **Header** (aggregate root) | `Customer` | `CustomsEntry`, `Invoice`, `Project` |
| **Transaction** (line-level detail, child of header) | `Order` | `SurtaxLineItem`, `InvoiceLine`, `Task` |
| **Line item** (detail of transaction) | `Item` | (nested detail if needed) |
| **Reference/lookup** (flat parent, rates/prices) | `Product` | `HSCodeRate`, `PriceList`, `TaxRate` |

### SQLAlchemy Models (exact basic_demo code)

```python
from sqlalchemy import Column, Integer, String, Date, ForeignKey
from sqlalchemy.orm import relationship, Mapped
from sqlalchemy.types import DECIMAL
from typing import List

class Customer(Base):
    __tablename__ = 'customer'
    id           = Column(Integer, primary_key=True, autoincrement=True)
    name         = Column(String)
    balance      = Column(DECIMAL)          # ← derived by Rule.sum (do NOT set manually)
    credit_limit = Column(DECIMAL)          # ← input: set by user
    email        = Column(String)

    OrderList : Mapped[List["Order"]] = relationship(back_populates="customer")


class Product(Base):
    __tablename__ = 'product'
    id         = Column(Integer, primary_key=True, autoincrement=True)
    name       = Column(String)
    unit_price = Column(DECIMAL)            # ← flat reference value — copied to Item by Rule.copy

    ItemList : Mapped[List["Item"]] = relationship(back_populates="product")


class Order(Base):
    __tablename__ = 'order'
    id           = Column(Integer, primary_key=True, autoincrement=True)
    customer_id  = Column(ForeignKey('customer.id'), nullable=False)
    date_shipped = Column(Date)             # ← None = unpaid; used in sum where-clause
    amount_total = Column(DECIMAL)          # ← derived by Rule.sum (do NOT set manually)

    customer : Mapped["Customer"] = relationship(back_populates="OrderList")
    ItemList : Mapped[List["Item"]] = relationship(back_populates="order")


class Item(Base):
    __tablename__ = 'item'
    id         = Column(Integer, primary_key=True, autoincrement=True)
    order_id   = Column(ForeignKey('order.id'), nullable=False)
    product_id = Column(ForeignKey('product.id'), nullable=False)
    quantity   = Column(Integer, nullable=False)
    unit_price = Column(DECIMAL)            # ← snapshot copy from Product.unit_price via Rule.copy
    amount     = Column(DECIMAL)            # ← derived: quantity × unit_price via Rule.formula

    order   : Mapped["Order"]   = relationship(back_populates="ItemList")
    product : Mapped["Product"] = relationship(back_populates="ItemList")
```

**Key schema points:**
- Every derived column (`balance`, `amount_total`, `amount`, `unit_price` on Item) has a **column in the model** — LogicBank stores results there
- `unit_price` appears on **both** `Product` (the reference value) and `Item` (the snapshot copy) — this is the `Rule.copy` pattern
- FK relationships (`customer_id`, `product_id`, `order_id`) are **integer FKs**, not string codes — this is what `Rule.copy` traverses

---

## The Five Canonical Rules

All five LogicBank rule types in one `declare_logic()` function.
(For full API reference see `docs/training/logic_bank_api.md` — this file provides the schema context and dependency chain that `logic_bank_api.md` omits.)

```python
from logic_bank.logic_bank import Rule
from database import models


def declare_logic():
    """Check Credit — enforce balance and credit limit on order placement."""

    # Rule.sum with where-clause: Customer.balance = sum of unpaid Order.amount_total
    # Any change to Item.amount chains up: Item → Order.amount_total → Customer.balance
    Rule.sum(derive=models.Customer.balance,
             as_sum_of=models.Order.amount_total,
             where=lambda row: row.date_shipped is None)

    # Rule.sum without where-clause: Order.amount_total = sum of all Item.amount
    Rule.sum(derive=models.Order.amount_total,
             as_sum_of=models.Item.amount)

    # Rule.formula: Item.amount = quantity × unit_price (unit_price is a snapshot from Rule.copy)
    Rule.formula(derive=models.Item.amount,
                 as_expression=lambda row: row.quantity * row.unit_price)

    # Rule.copy: snapshot Product.unit_price → Item.unit_price at insert time
    # Requires Item.product_id FK → Product.id — the relationship is what makes traversal possible
    # Use copy (not formula) when the value should be frozen at transaction time (price contracts)
    Rule.copy(derive=models.Item.unit_price,
              from_parent=models.Product.unit_price)

    # Rule.constraint: fires after all derivations; balance is already recalculated before this check
    Rule.constraint(validate=models.Customer,
                    as_condition=lambda row: row.balance <= row.credit_limit,
                    error_msg="Customer balance ({row.balance}) exceeds credit limit ({row.credit_limit})")
```

---

## Ordering: Rules vs Events

### Rules — ordering is automatic, never use events to control it

LogicBank builds the execution order from rule declarations. If you find yourself writing
an `early_row_event` or `row_event` to look up a value before a formula fires, that is a
signal to use `Rule.copy` or `Rule.formula` instead:

```
Item inserted/updated
  → Rule.copy fires first:  Item.unit_price ← Product.unit_price   (copy is upstream of formula)
  → Rule.formula fires:     Item.amount = quantity × unit_price     (sees the copied value)
  → Rule.sum fires:         Order.amount_total = Σ Item.amount
  → Rule.sum fires:         Customer.balance = Σ Order.amount_total (unpaid)
  → Rule.constraint:        Customer.balance <= credit_limit  ✓ or raise error
```

`Rule.copy` fires before `Rule.formula` because the dependency graph puts copy upstream.
The engine handles all change paths (insert, update, delete, cascade, re-parent) automatically.
**Do not add events to control rule ordering.**

### Events and AI-Rules — ordering DOES matter inside procedural code

When you write an `early_row_event`, `row_event`, or an **AI-Rule** (which receives domain
values as request-object attributes), you are writing **procedural code**. Dependencies among
the computed values must be respected in the order you reference them:

```python
# AI-Rule example — args arrive as req object attributes
def customs_duty(row, old_row, logic_row):
    req = logic_row.req
    # CORRECT: use req.customs_value before req.duty_amount depends on it
    customs_value = req.customs_value                   # set upstream
    duty_rate     = req.hs_code_rate.duty_rate          # lookup from related row
    row.duty_amount = customs_value * duty_rate         # computed from both
```

If `req.customs_value` is itself derived from another attribute on `req`, that attribute
must be assigned (or already present) before you reference `req.customs_value`.
In other words: **in event/AI-Rule code, declare/compute values in dependency order, top to bottom.**

---

## Translating Patterns to Your Domain

| basic_demo | Customs domain equivalent | Pattern |
|---|---|---|
| `Customer.balance` = sum of unpaid `Order.amount_total` | `CustomsEntry.total_duty` = sum of `SurtaxLineItem.duty_amount` | `Rule.sum` |
| `Order.amount_total` = sum of `Item.amount` | `SurtaxLineItem.duty_amount` = `customs_value × duty_rate` | `Rule.formula` |
| `Item.unit_price` ← `Product.unit_price` (snapshot) | `SurtaxLineItem.surtax_rate` ← `HSCodeRate.surtax_rate` | `Rule.copy` |
| `Customer.balance <= credit_limit` | `SurtaxLineItem.quantity > 0` | `Rule.constraint` |

**The structural translation:**
- `Customer` → header aggregate (e.g., `CustomsEntry`)
- `Order` → transaction (e.g., a grouping within the entry, or the entry itself)
- `Item` → line item (e.g., `SurtaxLineItem`)
- `Product` → reference/lookup table (e.g., `HSCodeRate`, `ProvinceTaxRate`, `CountryOrigin`)

The `Rule.copy` pattern depends entirely on the FK relationship existing:
`SurtaxLineItem.hs_code_id FK → HSCodeRate.id` is exactly analogous to
`Item.product_id FK → Product.id`. Without the FK, `Rule.copy` cannot traverse to the parent.
This is why FK integers (not string codes) are mandatory for lookup references.
