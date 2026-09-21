---
title: Bug Assessment — bd_claude_native_ai vs. declarative-vs-procedural-comparison.md
version: 1.0
date: 2026-09-17
assessed_by: AI (Claude), by code inspection and live probing against a copy of basic_demo.sqlite
related: ../bd_claude_alp_adjacent/bug-assessment.md
---

# Bug Assessment: bd_claude_native_ai

## Setup

Same basic_demo rules, but the prompt was phrased the way a developer thinking
procedurally would describe it: "here's what needs to happen when someone places an
order..." — an event-triggered sequence, not declared invariants. Goal: test whether
that framing leads the AI to wire logic onto the insert path only.

## Result: yes, it did

`app/orders.py`'s `place_order()` is the entire implementation, called only from order
*creation* (`POST /api/orders`, `POST /orders/new`). No update/delete route exists for
orders or items anywhere in `app/main.py`.

The tell: `customer.balance` is a running **accumulator**
(`customer.balance = (customer.balance or 0) + order_total`), not a value recomputed
from its constituent orders. Correct only if every write forever goes through
`place_order()`.

## Live probe (throwaway db copy, direct ORM writes bypassing the missing endpoints)

| Mutation | Expected if reactive | Actual |
|---|---|---|
| `Item.quantity` 1→5 (was $150) | amount→750, order total→750, balance→840 | all unchanged |
| Delete that `Item` | order total→0, balance drops by 150 | both unchanged |
| `Order.customer_id` reassigned (old Bug 1) | old customer −150, new customer +150 | neither changed |
| `Item.product_id` reassigned (old Bug 2) | price re-copied | stale price kept |

## Takeaway

This is path-dependent logic: the business rules exist only along the one path the prompt
described (place an order). Updates and deletes are not addressed at all — not buggy,
simply absent — so any other path through the same data (a quantity change, an item
deletion, a customer or product reassignment, whether via a future endpoint, a script, or
direct data access) will fail to follow the logic: `Item.amount`, `Order.amount_total`, and
`Customer.balance` silently go stale, with no recomputation of any kind.

Contrast with `bd_claude_alp_adjacent`, where a rule-shaped prompt led the model to
spontaneously choose a `before_flush` session hook — reactive across insert/update/delete
without being asked. Here, procedural-flow phrasing produced procedural-flow code: one
function tied to one event, nothing underneath to keep derived values correct afterward.
Confirms the hypothesis — prompt framing measurably shaped the architecture, not just the
wording.
