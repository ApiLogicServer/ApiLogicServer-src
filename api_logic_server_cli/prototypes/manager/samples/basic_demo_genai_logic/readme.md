---
title: basic_demo_genai_logic
Description: Logic only — prompt phrased procedurally, not as declarative rules
URL: https://github.com/ApiLogicServer/basic_demo_genai_logic
copy to gold source: cp -r ApiLogicServer-dev/build_and_test/genai-logic/basic_demo_genai_logic/. api_logic_server_cli/prototypes/manager/samples/basic_demo_genai_logic/ (no .git)
version info: 17.04.01 (09/21/2026)
---

!!! pied-piper ":bulb: TL;DR - Governed rules from a procedural spec"

    Created by: › genai-logic create --project_name=basic_demo_genai_logic --db_url=sqlite:///samples/dbs/basic_demo.sqlite, then the prompt below ("The Prompt")

    * The prompt was phrased as a procedure ("here's what needs to happen when someone places an order..."), not as declarative rules
    * GenAI-Logic's context engineering still produced 5 declarative rules — not an event handler wired to one path
    * Compare: [bd_claude_native_ai](../bd_claude_native_ai) — the identical procedural prompt, without ApiLogicServer, produced insert-only code with 4 confirmed silent-stale bugs

    Status: Reference implementation

# GenAI-Logic Basic Demo — Procedural Prompt

A working system — API, admin UI, and business rules — generated from a prompt that describes
a *procedure*, not a set of declarative rules. The point: it doesn't matter how the requirement
is phrased. Context engineering steers the AI to declarative rules either way.

## The Prompt

```
Using basic_demo.sqlite, build basic_demo_genai_logic (api + web app) that lets us enter orders.

Here's what needs to happen when someone places an order:

For each line item on the order, look up the product's price and multiply by the quantity to
get the item's amount.
Add up the item amounts to get the order's total.
Add the order total to the customer's balance.
Before we let the order go through, check that the customer's balance doesn't go over their
credit limit — if it would, reject the order.
```

Compare this to [basic_demo_logic_gov](../basic_demo_logic_gov)'s prompt — that one already reads
like rule declarations ("Customer balance = sum of unshipped order totals"). This prompt reads
like a developer explaining a workflow, event by event. Same requirement, different framing.

## Run It

```bash
git clone <repo>
cd basic_demo_genai_logic
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
python api_logic_server_run.py
```

Then open: http://localhost:5656 (no login required — security is not enabled in this demo).

&nbsp;

## What Runs

| Artifact | Description | Notes |
|---|---|---|
| JSON:API | Auto-generated REST for all tables at `/api` | Pagination, optimistic locking, filtering/sorting, swagger |
| Admin UI | Full CRUD at `/admin-app` | Multi-table - navigations, lookups etc |
| Business Rules | 5 declarative rules in `logic/logic_discovery/place_order/` | Governs all ORM CRUD operations |

&nbsp;

## The Rules — [check_credit.py](logic/logic_discovery/place_order/check_credit.py)

```python
Rule.copy(derive=models.Item.unit_price, from_parent=models.Product.unit_price)
Rule.formula(derive=models.Item.amount, as_expression=lambda row: row.quantity * row.unit_price)
Rule.sum(derive=models.Order.amount_total, as_sum_of=models.Item.amount)
Rule.sum(derive=models.Customer.balance, as_sum_of=models.Order.amount_total)
Rule.constraint(validate=models.Customer,
                as_condition=lambda row: row.balance <= row.credit_limit,
                error_msg="Customer balance ({row.balance}) exceeds credit limit ({row.credit_limit})")
```

Nothing in the prompt used the words "rule," "declare," or "sum of." It described a sequence of
steps. The AI still recognized the underlying data invariants and wrote data-bound rules — reactive
to every write path (insert, update, delete, FK reassignment), not just the "place an order" path
the prompt happened to describe.

&nbsp;

## Why This Matters More Than It Looks

Most developers describe requirements procedurally — that's how people naturally think and talk
about a business process. If context engineering only worked when the prompt was pre-formatted as
rules, it would be a party trick, not infrastructure. This sample is the check: hand the AI the
same kind of prompt a developer would actually write, with no rule-shaped hints, and confirm the
output is still governed.

**The control group:** [bd_claude_native_ai](../bd_claude_native_ai) took the *identical* procedural
prompt and told Claude explicitly not to use ApiLogicServer — plain hand-written Python instead.
The result: `place_order()` correctly handled inserts, but no update or delete path exists anywhere
in the app. `Customer.balance` is a running accumulator, not a recomputed value — correct only if
every future write goes through that one function. A live probe confirmed 4 silent-stale cases
(quantity change, item deletion, order reassignment, product reassignment) that ordinary testing
wouldn't catch.

Same prompt. Same underlying requirement. The difference is entirely in whether context engineering
was present to steer the AI toward data-bound rules instead of one-path procedural code.

| | Procedural prompt, no ApiLogicServer | Procedural prompt, GenAI-Logic |
|---|---|---|
| Rule count | 1 function, insert-only | 5 declarative rules |
| Paths covered | 1 of 9 (insert only) | All 9 — insert/update/delete/FK reassignment |
| Update quantity, delete item, reassign order/product | Silently stale | Correctly recomputed |

&nbsp;

## Governance Reports

| NL Command | Artifact | What you get |
|---|---|---|
| `create logic diagram` | `docs/requirements/logic_flow_basic_demo_genai_logic.md` | Dependency chain for `check_credit`, generated from the rules |
| `health check` | Governance report | Coverage and integrity score for this project |

&nbsp;

---

See also: [basic_demo_logic_gov](../basic_demo_logic_gov) (rule-formatted prompt, same requirement) and
[bd_claude_native_ai](../bd_claude_native_ai) (no ApiLogicServer — the control group referenced above).
