---
title: Project Assessment — bd_claude_native_ai vs. declarative-vs-procedural-comparison.md
version: 2.0
date: 2026-09-30
assessed_by: AI (Claude), by code inspection and live probing against a copy of basic_demo.sqlite
related: ../bd_claude_alp_adjacent/bug-assessment.md
---

# Project Assessment: bd_claude_native_ai

## Setup

Same basic_demo rules, same prompt given to GenAI-Logic — but phrased the way a developer
thinking procedurally would describe it: *"here's what needs to happen when someone places
an order..."*, an event-triggered sequence, not declared invariants. Goal: test whether that
framing leads the AI to wire logic onto the insert path only, and whether the same gap shows
up in the generated API/app.

---

## Business logic: path-dependent, insert-only

- `app/orders.py`'s `place_order()` is the entire implementation — called only from order
  *creation* (`POST /api/orders`, `POST /orders/new`). No update/delete route exists for
  orders or items anywhere in `app/main.py`.
- **The tell:** `customer.balance` is a running **accumulator**
  (`customer.balance = (customer.balance or 0) + order_total`), not a value recomputed from
  its constituent orders. Correct only if every write forever goes through `place_order()`.

**Live probe** (throwaway db copy, direct ORM writes bypassing the missing endpoints):

| Mutation | Expected if reactive | Actual |
|---|---|---|
| `Item.quantity` 1→5 (was $150) | amount→750, order total→750, balance→840 | all unchanged |
| Delete that `Item` | order total→0, balance drops by 150 | both unchanged |
| `Order.customer_id` reassigned | old customer −150, new customer +150 | neither changed |
| `Item.product_id` reassigned | price re-copied | stale price kept |

**Takeaway:** this is path-dependent logic — the business rules exist only along the one
path the prompt described. Updates and deletes aren't buggy, they're simply absent, so any
other path through the same data (a quantity change, a deletion, a reassignment, via a
future endpoint, a script, or direct data access) silently leaves `Item.amount`,
`Order.amount_total`, and `Customer.balance` stale, with no recomputation of any kind.

Contrast with `bd_claude_alp_adjacent`, where a rule-shaped prompt led the model to
spontaneously choose a `before_flush` session hook — reactive across insert/update/delete
without being asked. Here, procedural-flow phrasing produced procedural-flow code: one
function tied to one event, nothing underneath to keep derived values correct afterward.
**Prompt framing measurably shaped the architecture, not just the wording.**

---

## API/App: the same pattern, one layer up

`main.py`'s hand-written endpoints are **correctly implemented for what the prompt
described** — create an order, list orders/customers/products, view a detail page. No bugs
found here.

But look at what's not there:

- No `PATCH` or `DELETE` on any resource
- No pagination, no filtering
- No optimistic locking
- Each endpoint hand-serializes its own field list (`main.py` lines 36-44, 56-66, 85-93),
  repeating the same shape-selection work per route

None of this was asked for in the prompt — **but it wasn't asked for in the GenAI-Logic
prompt either**, and GenAI-Logic produces all of it anyway, automatically, from schema
introspection.

**This is the same finding as the business-logic result, one layer up the stack:**
prompt-driven generation produces exactly what the prompt's words describe. A platform with
built-in architectural knowledge produces what any professional system needs, independent
of whether the prompt thought to mention it. The business-logic story and the API story are
the same story — this just makes it visible at the infrastructure layer too.
