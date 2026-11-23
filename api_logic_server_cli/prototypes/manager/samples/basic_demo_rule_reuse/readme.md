---
title: Rule Reuse
do_process_code_block_titles: True
version: 1.0 11/22/2026 - rule names (LogicBank 1.34.06), Uses:, "covered by existing rules" in the traceability report
source: docs/Sample-Demo-Reuse
Propagation: see api_logic_server_cli/sample_mgr/create_readme.py
---
<style>
  -typeset h1,
  -content__button {
    display: none;
  }
</style>


&nbsp;
**Key Takeways - TL;DR - Rules are not per path**
&nbsp;

    Requirements often name one path: *"on moving an order to a different customer, check credit."* With procedural
    code, each path needs its own code. With rules, it is usually **already done**: the rules are declared on the data,
    so they run on every write path, automatically.

    This sample shows the AI recognizing that. Given a requirement that restates existing rules for one path, it adds
    **no new rule**: it links the requirement to the rules it uses, tests the path, and the traceability report shows
    the requirement as **covered by existing rules**.

&nbsp;

## Build It

Paste this into your AI assistant, from the Manager:

```text
Create basic_demo_rule_reuse from samples/prompts/basic_demo_rule_reuse.prompt
```

Then, in the created project: `create tests`, `run the tests`, and `run the requirements traceability report`.

The prompt is Check Credit and a Kafka publish (as in the basic demo), plus one requirement for a single path:

**The requirement for one path:**
```text title="The requirement for one path"
On Moving Orders to a different Customer, Check Credit
    1. Recompute the customers balances as the sum of the unshipped order totals
    2. The Customer's balance must not exceed the credit limit
```

&nbsp;

## What You Get

![rule reuse in the traceability report](https://raw.githubusercontent.com/ApiLogicServer/Docs/main/docs/images/basic_demo/rule-reuse/rule-reuse.png)

Check Credit's rules already cover moving an order: the balance sum adjusts both the old and the new customer, and the
credit check runs on both. So for this requirement the AI:

* **Adds no rule.** A second constraint would run twice; a second derivation would stop the server.
* **Links the requirement to the rules it uses,** by name:
  `Uses: Customer.balance (Check Credit), Customer.credit_limit_check (Check Credit)`.
* **Writes a placeholder logic file,** `logic/logic_discovery/move_order/check_credit.py`: the requirement as its
  docstring, no rules, and the `Uses:` line. A later `implement reqs` finds it and adds nothing.
* **Notes it in `ad-libs.md`** as redundant, with the test to write.

When you create tests, that path gets its own scenarios (a move within the limit adjusts both balances; a move over
the limit is rejected). The report shows the requirement **covered by existing rules**, tested, and still listed, so a
change to the rules it uses shows there too.

&nbsp;

## Rule Names

Requirements refer to rules by name (LogicBank 1.34.06):

* **Derivations** are named by the column they derive: `Customer.balance`.
* **Constraints and events** get a name when declared (`name="credit_limit_check"`), so they read
  `Customer.credit_limit_check` and `Order.shipping_publish`. The name appears in the logic log:
  `Constraint Failure (Customer.credit_limit_check): ...`.

A `Uses:` name that matches no rule is flagged in the report, with the closest names (for example,
*did you mean `Customer.credit_limit_check`?*).
