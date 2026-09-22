---
title: bd_claude_native_ai
Description: Control group — native AI, no rules engine, same prompt as basic_demo_genai_logic
version: 17.04.01 (09/22/2026)
---

!!! pied-piper ":bulb: TL;DR - Native AI alone, no rules engine — the control group"

    Created by: Claude, given the same procedural prompt as [basic_demo_genai_logic](../basic_demo_genai_logic), told explicitly not to use ApiLogicServer/GenAI-Logic/LogicBank

    * Hand-written Python (FastAPI + SQLAlchemy) — no declarative rules
    * Insert path works; update/delete paths were never written — `Customer.balance` silently goes stale
    * The exact evidence cited in [the insert-only experiment](https://apilogicserver.github.io/Docs/Tech-Standard-Reqs/)

    Status: Control group (evidence)

# Native AI, No ApiLogicServer — Order Entry

This is the control group for [the insert-only experiment](https://apilogicserver.github.io/Docs/Tech-Standard-Reqs/). Claude was given a typical, natural-language spec — the way a developer actually describes requirements — and told explicitly **not** to use ApiLogicServer, GenAI-Logic, LogicBank, or any rules engine. Just plain hand-written Python (FastAPI + SQLAlchemy, Jinja2 templates) over `basic_demo.sqlite`.

- **The prompt:** [basic_demo_procedural.prompt.md](basic_demo_procedural.prompt.md)
- **The full transcript:** [transcript.md](transcript.md) — unedited, exactly what Claude produced
- **The finding:** [bug-assessment.md](bug-assessment.md) — live-probed against the running app

**What happened:** the AI built `place_order()` — the insert path — correctly. No update path, no delete path, anywhere in the app. `Customer.balance` is a running accumulator, not a recomputed value, so it's only ever correct if every future write goes through that one function. Quantity changes, item deletions, and customer/product reassignments all leave stale data behind, silently, with nothing to catch it.

This isn't a bug in the code that got written — the code that got written works. The problem is what never got written: the logic was never generalized past the one path the prompt described.

## Run

```bash
./run.sh
```

Then open http://127.0.0.1:8000

## Order placement logic

All in [app/orders.py](app/orders.py), `place_order()`:

1. For each line item, look up the product's price and multiply by quantity to get the item's amount.
2. Sum item amounts to get the order's total.
3. Add the order total to the customer's balance.
4. If the new balance would exceed the customer's credit limit, reject the whole order (nothing is committed).

## Endpoints

- `GET /` — list orders
- `GET /orders/new`, `POST /orders/new` — order entry form
- `GET /orders/{id}` — order detail
- `GET /api/customers`, `GET /api/products`, `GET /api/orders`
- `POST /api/orders` — JSON: `{"customer_id": 1, "notes": "...", "items": [{"product_id": 1, "quantity": 2}]}`

## Compare

The identical prompt, run through GenAI-Logic instead: [samples/basic_demo_logic_gov](../basic_demo_logic_gov) — 5 declarative rules, every path covered, no bypass.
