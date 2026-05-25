---
title: basic_demo (github) and basic_demo_logic_gov (manager/samples)
Description: Logic only (no EAI, Security, B2B)
URL: https://github.com/ApiLogicServer/basic_demo
Dev Clone at: ApiLogicServer-dev/org_git/basic_demo
copy to gold source: cp -r ApiLogicServer-dev/org_git/basic_demo/. api_logic_server_cli/prototypes/manager/samples/basic_demo_logic_gov/ (no .git)
version info: 17.00.27 (05/24/2026)
---

# GenAI-Logic Basic Demo

A working system — API, admin UI, and business rules — generated from a short prompt. The goal is to show how **declarative rules** address the governance problem at the core of enterprise logic.

## The Prompt

```
Create a system with customers, orders, items and products.
Include a notes field for orders.

On Placing Orders, Check Credit:
  1. Customer balance must not exceed credit limit
  2. Customer balance = sum of unshipped order totals
  3. Order amount_total = sum of item amounts
  4. Item amount = quantity × unit_price
  5. Item unit_price copied from Product

Use case: App Integration
  1. Publish Order to Kafka topic 'order_shipping' when shipped
```

## Run It

```bash
git clone <repo>
cd basic_demo
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

## Why Rules Matter

Business logic — multi-table derivations, constraints, and side-effects like messaging — is typically **40–50% of coding and debugging effort**. Versata measured this across production deployments: declarative rules required writing only 3% of equivalent procedural code.

Standard AI can generate *procedural* code: here is [what Copilot produced](logic/procedural/credit_service.py) from the same requirements above — **~200 lines, with 2 subtle bugs** (documented in the [A/B comparison](logic/procedural/declarative-vs-procedural-comparison.md)).

GenAI-Logic uses [context engineering](docs/training/logic_bank_api.md) to make AI generate **declarative rules instead**: [5 executable lines](logic/logic_discovery/place_order/check_credit.py).

The reduction matters because of these structural properties:

| Property | Procedural Code | Declarative Rules |
|---|---|---|
| **Readability** | Intent buried in implementation — maintainers see *how*, not *what* | **The rule is the requirement** — business and tech read the same artifact, no translation gap |
| **Correctness** | [A/B test](logic/procedural/declarative-vs-procedural-comparison.md) uncovered 2 bugs in Copilot-generated code | **Automatic reuse over all change paths** (insert, update, delete, FK reassignment) |
| **Maintainability** | Adding logic requires finding every call site and insertion point | **Auto-ordered** at startup via dependency graph — add a rule anywhere, engine places it correctly |
| **Enforcement** | Must be explicitly called — can be bypassed or forgotten | **No bypass** — listens to `before_flush`, every ORM write runs rules automatically |
| **Iteration** | Evolving requirements mean patching a growing codebase — regenerating risks regressions as codebase grows | **Each rule is independent** — add or change one rule, engine handles all downstream consequences |

These properties are what make rules a governance mechanism, not just a style preference. Every transaction traces to the rule that governed it — compliance teams can verify governance, not merely assert it.

&nbsp;

## Governance Reports

Rules are the foundation, but governance also requires visibility — that the logic is correct, complete, and tested. These reports provide that. And because rules are structured and machine-readable, the system can generate tests directly from them — a downstream consequence of the rules themselves being unambiguous.

Every developer insists on a database diagram — you cannot engage with a system you cannot visualize. The same is true for logic. Without a logic diagram, onboarding means reading code to reconstruct dependency chains mentally; supporting or maintaining an unfamiliar system means drawing it by hand before you can reason about consequences. The logic diagram here is auto-generated from the rules, so it cannot drift from the code. It is the logic equivalent of a db diagram — and just as essential.

| NL Command | Artifact | Description |
|---|---|---|
| `create logic diagram` | [Logic Diagram](docs/requirements/logic_flow_basic_demo.md) | Requirements, logic diagram, and rules summary — db diagram for logic |
| `health check` | [Governance Report](docs/requirements/health_check.md) | Coverage + integrity scores — manage 1 project, or a portfolio |
| `create tests` | [Behave Tests](test/api_logic_server_behave/reports/Behave%20Logic%20Report.md) | 7 scenarios, 100% pass — generated from the rules; report shows log of each rule execution |

&nbsp;

## How It Works: Logic Governance Architecture


1. **Context Engineering** directs AI to generate Data Rules — not procedural code. Without it, AI pattern-matches to FrankenCode. With it, intent becomes declarations.  This is genned into your project at `docs/training`.

2. **Data Rules** distill path-dependent logic into *path-independent rules on data*. They are Python source — `Rule.constraint`, `Rule.sum`. No missed paths. Every path inherits them automatically.

3. The **Commit Listener** hooks into the ORM commit. Every transaction — API, agent, workflow — passes through one control point. Nothing bypasses it.

4. The **Rule Engine** computes dependency order from the Data Rules at startup — deterministically. No pattern-matching, no subtle ordering bugs.

![Logic Governance Architecture](https://github.com/ApiLogicServer/Docs/blob/main/docs/images/architecture/logic-architecture.png?raw=true)


For more on Governance, [click here](https://apilogicserver.github.io/Docs/IDE-Health-Check/).

&nbsp;

---

Ready to try it? Return to the Manager and open **🚀 First Time Here? → 🔨 Do it** to create `basic_demo` and take the 30-minute hands-on tour.
