# erpnext_modernize: a modernization test, built on the demo_eai_modernize pattern

Drafted 2026-10-29. This folder is the master copy; a working copy is in the Manager at `samples/requirements/erpnext_modernize/` (build_and_test/genai-logic, not gold source). Keep the two in sync by hand.

## What it tests

Whether requirements recovered from a real, unfamiliar, framework-heavy codebase (ERPNext's credit control) can be turned into a governed rules system, and what the AI decides on its own along the way. The AI designs the schema from nothing (only `starter.sqlite`), so the ad-libs report is the main output to read.

## Provenance of `erpnext_credit/requirements.md`

- Stage 1 (blind to tests and docs): `../stage1-extraction/requirements.md`.
- Stage 2 (tests diff): `../stage2-ground-truth/tests-diff.md`. Two behaviors the tests exposed are **added** here: reopening a Closed Sales Order re-checks credit, and copying a group's limit rows to a customer.
- Rewritten in the demo_eai style: behavior statements only. The commentary on quirks was removed; each quirk is stated as plain behavior. `Feature:` lines appear on five sections; the demo_eai run had none and the AI added them, so remove these to repeat that exactly.
- So this is not a pure extraction: it has stage 2 information in it.

## Differences from demo_eai_modernize

- No source database: schema is invented by the AI (expect many ad-libs).
- No Kafka or messages; security is included for the credit-controller role.
- Equivalence cannot be tested by running ERPNext's tests. See the mapping below.

## Equivalence mapping (expected scenarios, to compare with the run)

| ERPNext test | Scenario the rebuild should have |
|---|---|
| `test_customer_credit_limit` | Over-limit Sales Order, Delivery Note and Sales Invoice are rejected on submit |
| `test_credit_limit_for_customer` (journal) | Journal Entry debit to a customer over the limit is rejected |
| `test_customer_credit_limit_after_submit` | Raising the amount of a submitted Sales Order over the limit is rejected |
| `test_credit_limit_on_so_reopning` | Reopening a Closed Sales Order over the limit is rejected |
| `test_customer_credit_limit_on_change` / `test_duplicate_credit_limit_company` | Duplicate company rows rejected, customer and group |
| `test_credit_limit_with_sales_order_bypass` (delivery) | Flag on: standalone submitted delivery 600 + order 500 + delivery against order is rejected at limit 1000 |
| `test_customer_group_details` | Copy-from-group fills the customer's rows |
| pre-submit tests (invoice lines linked to order/delivery; returns; no limit; proportional delivery) | Invoice with all lines linked: no check; return: no check; no limit: no check; delivery with a linked line counts only the unlinked part |
| Sales Order flag-on skip | Flag on: Sales Order is not checked |

Written by us, no ERPNext test behind them (expected to show up as ad-libs or 🔴): boundary equal to the limit passes; credit controller is not rejected; no credit controller role means nobody is excused; group `bypass` flag removes the group limit; zero customer limit inherits the group's.

## Predictions, to check against the run

- The AI will invent table and column names, a ledger design, and a way to express "user has role X" in a constraint.
- Expect 🔴 items for: the credit controller override (a role check inside a rule), the four-way "bypass" meaning, status handling (what counts as open), and the ledger simplification.
- The delivered-not-billed formula is the hardest to express as rules and the most likely to be simplified.
- The credit controller override needs a role check inside a rule. The engine has `Security.current_user_has_role(name)` (generated `security/system/authorization.py`) but the CE does not mention it for business rules. Prediction: the AI may not find it; if so, it should say so as a 🔴 ad-lib. Either outcome is evidence for the CE backlog note `internal_dev/ce_roles_in_business_rules.md`.
