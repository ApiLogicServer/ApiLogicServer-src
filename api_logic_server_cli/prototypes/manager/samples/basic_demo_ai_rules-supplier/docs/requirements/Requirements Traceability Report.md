# Requirements Traceability Report

This report shows requirements, the rules created from them, and the tests created from those rules.

This project began as natural-language requirements, fleshed out by AI into a running system of business rules that are *executable documentation*. This report is how you govern the result.

A governable system is one you can **read**, **trust**, and **maintain**: each requirement is listed beside the rules that implement it (*read*); the tests and logic logs show those rules running (*trust*); re-run it after any change and it flags the gaps — an untested requirement, an untraced rule, a channel no test checks (*maintain*).

It is generated from the project's own files, nothing written by hand, so it is as current as the last run and covers the whole project, not a sample. Open **Background** (below the summary) for what the terms mean, how to read the report, and what it can and can't tell you.


**Project:** basic_demo_ai_rules-supplier &nbsp;|&nbsp; **Generated:** November 04, 2026 18:12 &nbsp;|&nbsp; **Rules:** 9 &nbsp;|&nbsp; **Test scenarios:** 18 &nbsp;|&nbsp; **Generator:** requirements_traceability_report.py 2.15

**Last test run:** November 04, 2026 18:03, took 4.7 s (9m before this report; test results and logic logs below are from that run)


&nbsp;
&nbsp;

## At a Glance

**✅ 2 requirement(s), all implemented; 2 tested; 18 of 18 scenarios passed; last run 9m ago.**

| | |
|---|---|
| Requirements | 2 (2 implemented) |
| Tested | 2 of 2 |
| Last test run | ✅ 18 passed, 0 failed (November 04, 2026 18:03, 9m ago); took 4.7 s |
| Rules | 9 (5 declarative, 0 Python functions, 4 Python events) |
| Rules shown running in a test log | 7 of 9 |
| Security | not enabled; 10 role(s), 0 row-level grant(s) |
| Messages and APIs | 0 Kafka topic(s) in, 1 out; 0 HTTP endpoint(s) |
| Kafka | simulated, no broker: messages are tested through /consume_debug; live delivery not verified |

_Status: ✅ every requirement is implemented and tested, all scenarios pass, and the results are current. ⚠ a requirement is untested or unimplemented, there is no test run, or files changed since the last run. ❌ a scenario failed. This reports what was traced and tested, not that the system is correct._

<details markdown>
<summary>Background: what this report is, and how to read it</summary>

&nbsp;

<details markdown>
<summary>Requirements are business policies, expressed in natural language</summary>

<br>

A **requirement** is a statement of business behavior - how data is computed, validated, and transmitted - written in plain language. It lives in the project at `docs/requirements/<name>/requirements.md`.  For example:

&nbsp;

```
On Placing Orders, Check Credit
    1. The Customer's balance does not exceed the credit limit
    2. The Customer's balance is the sum of the unshipped Order amount_total
    3. The Order's amount_total is the sum of the Item amount
    4. The Item amount is the quantity * unit_price
    5. The Item unit_price is copied from the Product unit_price
```

</details>

&nbsp;

<details markdown>
<summary>Rules implement requirements</summary>

<br>

A requirement is written at a high level, and AI fills in details as it builds — as it should — so the requirement no longer says exactly what the system does. The rules do. That's a Goldilocks answer to the question of what you review:

* **Requirements say too little** — incomplete by design; AI fills in the details.
* **Code says too much** — business language in, hundreds of lines of procedural code out. The work moves from writing to reading, and if you can't read it, you can't govern it.
* **Rules are just right** — close to the requirement's own level, but complete and deterministic.

Code could be treated like machine language — never read, only trusted — if it were produced deterministically. Generation from natural language isn't. Rules restore that contract: a readable source, deterministically executed.

The requirements above become rules like this:

```
Rule.copy(derive=models.Item.unit_price, from_parent=models.Product.unit_price)
Rule.formula(derive=models.Item.amount,
             as_expression=lambda row: row.quantity * row.unit_price)
Rule.sum(derive=models.Order.amount_total, as_sum_of=models.Item.amount)
Rule.sum(derive=models.Customer.balance, as_sum_of=models.Order.amount_total,
         where=lambda row: row.date_shipped is None)
Rule.constraint(
    validate=models.Customer,
    as_condition=lambda row: row.balance <= row.credit_limit,
    error_msg="balance ({row.balance}) exceeds credit limit ({row.credit_limit})")
```

Rules are ***executable documentation*** that you can read and trust:

* **Read:** rules stay near the requirement's level, so this report can list them side by side and you can check one against the other. 5 rules vs. ~200 lines in our [A/B test](https://github.com/ApiLogicServer/ApiLogicServer-src/blob/main/api_logic_server_cli/prototypes/manager/samples/basic_demo_logic_gov/logic/procedural/declarative-vs-procedural-comparison.md) — **~40x less to review**, whether generated or hand-coded.
* **Trust:** the document is enforced, not just descriptive.
    * **What you read is what runs** — no drift between description and behavior.
    * **Dependencies:** with code, you analyze every execution path to know it runs at the right times. With rules: if the rule is there, it runs, in the right order.
    * **All sources and paths:** the engine hooks into every commit — API, UI or agent — insert, update and delete, including related rows. No bypass.
    * **Seeing is believing:** each scenario in *Tests and Results* below embeds its logic log — every rule that ran, in order, with old and new values.

Better AI makes generating code easier. It doesn't change what you have to read. The problem is the representation, not the capability. And governance is active, not just process: the engine enforces the rules on every transaction, and this report — regenerated from the project itself — shows it happening.

&nbsp;

</details>

&nbsp;

<details markdown>
<summary>Process overview: creation and iteration</summary>

<br>

![governance loop](https://apilogicserver.github.io/Docs/images/agile/governance_loop.svg)

In two phases. First, `genai-logic create` builds a working system from the database: API, Admin App, data model. Then behavior is added from requirements — the typical sequence, each step a request to an AI assistant:

1. Write each requirement in natural language, in `docs/requirements/<name>/requirements.md`.
2. `implement reqs <name>` — creates the rules, API endpoints and Kafka integrations.
3. `create tests from rules` — writes the test scenarios and steps.
4. `run the tests` — starts the server if needed, runs the suite, reports pass/fail.
5. `run the requirements traceability report` — regenerates this report.

Optional: `create logic diagram for each requirement` (needs Graphviz).

What makes steps 3–5 possible: rules are high-level enough that AI can read them too. The tests, the logic diagrams and this report are all generated by reading the same rules you review — where logic is Python code, the report can only quote its docstring.

The report connects the chain: requirement → rules and handlers → tests → logic log. How *this* project was actually built is recorded under Provenance.

</details>

&nbsp;

<details markdown>
<summary>How to read this report</summary>

<br>

| If you are...  | Start with                                                        | Look for                                                                                     |
| -------------- | ----------------------------------------------------------------- | -------------------------------------------------------------------------------------------- |
| Business owner | *Requirements in detail*                                          | The requirement text, then the **Tests** line under it: does a test exist, and did it pass?  |
| Auditor        | *Coverage summary*, *Rule coverage by tests*, *Messages and APIs* | Gaps (untested, untraced), the date of the last test run, and how each rule was shown to run |
| Developer      | *Tests and Results*                                               | Each scenario's logic log: every rule that ran, in order, with old and new values            |

</details>

&nbsp;

<details markdown>
<summary>What this report can and can't tell you</summary>

<br>

**It shows**

- Which files and rules implement each requirement, read from the project's source.
- Which scenarios ran in the last test run, and whether each passed.
- Which rules the engine logged as running in each scenario.

**It doesn't show**

- Whether the requirements are right or complete. It traces what was written down.
- Whether an event did anything. Events run on every commit of their class and decide for themselves whether to act, so appearing in the log doesn't mean the event had an effect.
- Whether a constraint works. A constraint appears in the log only when it rejects a transaction, so look for a scenario that makes it reject.
- Whether a message arrived. Unless a test step looks for it on the broker or endpoint, a passing scenario doesn't prove delivery. The *Messages and APIs* table flags channels no test mentions.
- Whether the results are current. They are as old as the last test run, shown in the header, which also warns if files changed since.
- Which version of a requirement the code was built from, or which clause of a requirement a given rule serves.

</details>

&nbsp;

<details markdown>
<summary>Terms</summary>

<br>

| Term        | Meaning                                                                                              |
| ----------- | ---------------------------------------------------------------------------------------------------- |
| Requirement | A statement of business behavior, in plain language; the unit this report traces.                    |
| Rule        | A declaration about data (sum, count, formula, copy, constraint) that the engine enforces at every commit. |
| Event       | Python code the engine calls when a row of a given class changes (for example, to publish a message). |
| Handler     | Code that serves an API endpoint or consumes a Kafka topic.                                          |
| Scenario    | One Behave test: a short Given / When / Then script run against the live API.                        |
| Logic log   | The engine's record of every rule it ran in a transaction, nested to show cascades (an Item change adjusts its Order, which adjusts its Customer). |
| Phase       | The step of a commit: ROW LOGIC (derivations, constraints), COMMIT LOGIC (checks that need finished totals), AFTER_FLUSH LOGIC (events that need database-assigned keys, such as publishing). |
| Seen        | The engine reported running the rule in that scenario's log.                                         |

</details>

</details>


&nbsp;
&nbsp;

## Contents

- [Requirements Coverage](#requirements-coverage)
- [Data Model](#data-model)
- [Security (RBAC)](#security-rbac)
- [Messages and APIs](#messages-and-apis)
- [Tests and Results](#tests-and-results)
- [Provenance](#provenance)


&nbsp;
&nbsp;

## Requirements Coverage

Every requirement should have rules that implement it, and tests that prove it. This section checks that chain in both directions: a requirement missing rules or tests is a gap, and rules or tests that belong to no requirement are flagged too. The matching uses the requirement names, `Feature:` names and `§N` tags that requirements, code and tests share. Requirements may be grouped into a use case (for example Place Order), read from the logic folder or the prompt; the level is optional.


&nbsp;

### Coverage summary

| Measure | Result |
|---|---|
| Requirements | 2 |
| Implemented (at least one file) | 2 of 2 |
| Tested (at least one scenario) | 2 of 2 |
| Use cases | 1: Place Order |
| Implementation not traced to a requirement | `security/declare_security.py`, `logic/logic_discovery/system/all_classes_stamping.py` |
| Tests not traced to a requirement | none |
| Test results (last run) | ✅ 18 passed, 0 failed; took 4.7 s |
| Scenarios with a logic log | 18 of 18 |
| Rules seen in at least one scenario's log | 7 of 9 (2 not counted: the engine's log does not name `Order.after_flush_row_event → kafka_producer.send_row_to_kafka()`, `all classes.early_row_event → handle_all()`, so it cannot be matched) |

_Test results are as current as the last run (see the header). A gap is any requirement with no implementation or no test._

<details markdown>
<summary>How to read this table</summary>

Test results are read from `logs/behave.log`, so they are only as current as that run. Not recorded here: which version of a requirement the code was built against, and which clause of a requirement a given rule serves.

</details>



&nbsp;

### Traceability matrix

| Use case | Requirement | Implemented by | Rules | Tests |
|---|---|---|---|---|
| Place Order | Check Credit | [logic/logic_discovery/place_order/check_credit.py](../../logic/logic_discovery/place_order/check_credit.py)<br>[logic/logic_discovery/ai_requests/supplier_selection.py](../../logic/logic_discovery/ai_requests/supplier_selection.py) | 7 | ✅ 15 scenario(s): 15 passed |
| Place Order | App Integration | [logic/logic_discovery/place_order/app_integration.py](../../logic/logic_discovery/place_order/app_integration.py) | 1 | ✅ 3 scenario(s): 3 passed |


&nbsp;

### Rule coverage by tests

| Rule | Requirement | Seen in |
|---|---|---|
| `SysSupplierReq.early_row_event → select_supplier_via_ai()` | Check Credit | 2: AI - chooses a supplier; AI - product change |
| `Order.after_flush_row_event → kafka_producer.send_row_to_kafka()` | App Integration | n/a - cannot be matched to the engine's log |
| `Customer: balance <= credit_limit` | Check Credit | 1: Credit - over the limit |
| `Customer.balance = sum(Order.amount_total) where date_shipped is None` | Check Credit | 16: Kafka - shipped order; Kafka - unshipped order; Kafka - edit shipped order; +13 more |
| `Order.amount_total = sum(Item.amount)` | Check Credit | 16: Kafka - shipped order; Kafka - unshipped order; Kafka - edit shipped order; +13 more |
| `Item.amount = quantity * unit_price` | Check Credit | 16: Kafka - shipped order; Kafka - unshipped order; Kafka - edit shipped order; +13 more |
| `Product.count_suppliers = count(ProductSupplier)` | Check Credit | 4: Suppliers - add and remove; Suppliers - move; AI - chooses a supplier; +1 more |
| `Item.early_row_event → set_item_unit_price_from_supplier()` | Check Credit | 16: Kafka - shipped order; Kafka - unshipped order; Kafka - edit shipped order; +13 more |
| `all classes.early_row_event → handle_all()` | (none) | n/a - cannot be matched to the engine's log |

_"Seen" means the engine's log shows the rule ran, not proof that it took effect._

<details markdown>
<summary>How to read this table</summary>

"Seen" means the engine reported running the rule in that scenario's logic log. A scenario can only contribute if it has a log (see the coverage summary): a test that does not open one writes into whichever log was open last, and its rules are then credited to that scenario, or to the shared log. An event's function runs on every commit of its class, and its own condition decides whether it acts, so seen does not mean it took effect. A constraint appears in the log only when it rejects a transaction, so it is seen only in scenarios that make it reject. "Not seen" therefore means no log shows it, not that no test ran it.

</details>



&nbsp;

### Requirements in detail

**9 rules** in 4 files: 5 declarative (sum, count, copy, formula and constraint expressions), 0 backed by a Python function, 4 events (Python).

_Declarative rules are read straight from their declarations. Functions and events are Python code, so for those the report shows the docstring — it does not analyze the code._

Each requirement is followed by the rules and handlers in the files that implement it. Logic diagrams are shown (click to expand) where they exist.

<details markdown>
<summary>How to create or refresh the logic diagrams</summary>

Needs Graphviz (`brew install graphviz`). Tell your AI assistant:

```
create logic diagram for each requirement
```

or run this from the Manager root (`genai-logic`):

```
python system/ApiLogicServer-Internal-Dev/logic_diagram_gv.py samples/basic_demo_ai_rules-supplier --each
```

Each diagram is saved under `docs/requirements/<name>/logic_diagrams/`. Then regenerate this report (`python requirements_traceability_report.py run`, from `test/api_logic_server_behave`).

</details>

&nbsp;


#### Check Credit

Use case: Place Order

Tests: ✅ 15 scenario(s): 15 passed

```
1. The Customer's balance is less than the credit limit
2. The Customer's balance is the sum of the Order amount_total where date_shipped is null
3. The Order's amount_total is the sum of the Item amount
4. The Item amount is the quantity * unit_price
5. The Product count suppliers is the sum of the Product Suppliers
6. Use AI to Set Item field unit_price by finding the optimal Product Supplier based on cost, lead time, and world conditions
```

| Rule / item | Type | Logic | Description | Where |
|---|---|---|---|---|
| `Customer: balance <= credit_limit` | constraint | declarative | Error: Customer balance ({row.balance}) exceeds credit limit ({row.credit_limit}) | [check_credit.py](../../logic/logic_discovery/place_order/check_credit.py) |
| `Customer.balance = sum(Order.amount_total) where date_shipped is None` | sum | declarative |  | [check_credit.py](../../logic/logic_discovery/place_order/check_credit.py) |
| `Order.amount_total = sum(Item.amount)` | sum | declarative |  | [check_credit.py](../../logic/logic_discovery/place_order/check_credit.py) |
| `Item.amount = quantity * unit_price` | formula | declarative |  | [check_credit.py](../../logic/logic_discovery/place_order/check_credit.py) |
| `Product.count_suppliers = count(ProductSupplier)` | count | declarative |  | [check_credit.py](../../logic/logic_discovery/place_order/check_credit.py) |
| `Item.early_row_event → set_item_unit_price_from_supplier()` | early_row_event | event (Python) | Item event: sets unit_price before Item.amount is derived - by AI supplier selection when the Product has suppliers, else copied from Product.unit_price. | [check_credit.py](../../logic/logic_discovery/place_order/check_credit.py) |
| `SysSupplierReq.early_row_event → select_supplier_via_ai()` | early_row_event | event (Python) | SysSupplierReq event: chooses the optimal ProductSupplier by calling OpenAI with the candidates and the world conditions from config/ai_test_context.yaml; falls back to minimum cost when there is no API key or the call fails, and records request, reason, fallback_used and the choice as the audit trail. | [supplier_selection.py](../../logic/logic_discovery/ai_requests/supplier_selection.py) |

<details markdown>
<summary>Logic diagram: check_credit</summary>

![logic diagram: check_credit](check_credit/logic_diagrams/logic_diagram_check_credit.svg)

</details>

<details markdown>
<summary>Logic diagram: supplier_selection</summary>

![logic diagram: supplier_selection](supplier_selection/logic_diagrams/logic_diagram_supplier_selection.svg)

</details>

#### App Integration

Use case: Place Order

Tests: ✅ 3 scenario(s): 3 passed

```
1. Publish the Order to Kafka topic 'order_shipping' if the date_shipped is not None
```

| Rule / item | Type | Logic | Description | Where |
|---|---|---|---|---|
| `Order.after_flush_row_event → kafka_producer.send_row_to_kafka()` | after_flush_row_event | event (Python) | (no docstring) | [app_integration.py](../../logic/logic_discovery/place_order/app_integration.py) |

<details markdown>
<summary>Logic diagram: app_integration</summary>

![logic diagram: app_integration](app_integration/logic_diagrams/logic_diagram_app_integration.svg)

</details>

#### Rules not traced to a requirement

| Rule / item | Type | Logic | Description | Where |
|---|---|---|---|---|
| `all classes.early_row_event → handle_all()` | early_row_event_all_classes | event (Python) | Generic handler - executed for every row update across all classes. | [all_classes_stamping.py](../../logic/logic_discovery/system/all_classes_stamping.py) |


&nbsp;
&nbsp;

## Data Model

The tables the rules run over. Derived columns (in italics) are computed by rules — no code writes them. Tinted groups are the subtypes.

![db diagram](db_diagram.generated.svg)

_Generated from `docs/db.dbml` (parents above children; shaded rows are derived by rules). To use your own layout, save it as `docs/db_diagram.png`._



&nbsp;

### Derived columns

| Table | Column | Rule | Definition |
|---|---|---|---|
| Customer | balance | sum | `Customer.balance = sum(Order.amount_total) where date_shipped is None` |
| Order | amount_total | sum | `Order.amount_total = sum(Item.amount)` |
| Item | amount | formula | `Item.amount = quantity * unit_price` |
| Product | count_suppliers | count | `Product.count_suppliers = count(ProductSupplier)` |


&nbsp;
&nbsp;

## Security (RBAC)

Who can do what: each role's permissions, and which rows each role can see.

**Security enabled: no** (`SECURITY_ENABLED` in `config/default.env`). The declarations below are not enforced until `genai-logic add-auth` is run.


&nbsp;

### Roles and CRUD (DefaultRolePermission)

| Role | Read | Insert | Update | Delete |
|---|---|---|---|---|
| sa | ✅ | ✅ | ✅ | ✅ |
| tenant | ✅ | — | — | ✅ |
| CS_ADMIN | ✅ | ✅ | ✅ | ✅ |
| manager | ✅ | ✅ | ✅ | — |
| teller | ✅ | ✅ | ✅ | — |
| customer | ✅ | ✅ | ✅ | — |
| readonly | ✅ | — | — | — |
| public | ✅ | — | — | — |
| default-roles-kcals | ✅ | ✅ | ✅ | — |
| uma_authorization | ✅ | ✅ | ✅ | — |


&nbsp;

### Row-level grants (Grant)

None declared (`Grant`).


&nbsp;
&nbsp;

## Messages and APIs

How data enters and leaves beyond the standard API: Kafka topics in and out, custom HTTP endpoints — and whether any test touches each one.

**Kafka mode: simulated (no broker).** `KAFKA_SERVER` is not set, so no Kafka consumer or producer runs. The tests deliver inbound messages by calling `/consume_debug`, which runs the same parse-and-save function the live consumer uses, so lookups, rules and the saved message are exercised, but Kafka delivery itself is not. Outbound messages are built and logged, not sent. To test with a real broker, set `KAFKA_SERVER` and `KAFKA_CONSUMER_GROUP` (see `integration/kafka/kafka_readme.md`).

| Direction | Channel | Name | Tests mention it | Handler | Tables created | Message shape | Requirement |
|---|---|---|---|---|---|---|---|
| ⬅ out | Kafka | `order_shipping` | ⚠ message checked in the log, not on the topic | Order.after_flush_row_event → kafka_producer.send_row_to_kafka() - (no docstring) |  |  | App Integration |

_"Tests mention it" checks the test sources, not delivery._

<details markdown>
<summary>How to read this column</summary>

A passing scenario proves a message reached a topic or an endpoint only if its steps look for it there. A handler that ran (see the logic log) is weaker evidence than a step that consumes the message. Channels no test mentions are flagged.

</details>

<details markdown>
<summary>How to read this table</summary>

Topics and endpoints are read from the discovery folders. The condition that triggers an outbound message lives in Python (see the rules under each requirement); here it is described by the handler's docstring. "Tables created" lists rows the handler's code constructs, following its calls within the project; blank means none were found, not that none exist.

</details>



&nbsp;
&nbsp;

## Tests and Results

**✅ 18 scenario(s): 18 passed, 0 failed; took 4.7 s** (from the last run, `logs/behave.log`).

Each test drives the running system the way any client would — create an order, change a quantity, ship it — and checks the result.

**The logic log** is what makes them more than pass/fail. Business rules run inside the server on every commit, so the server records exactly what they did, and this report embeds that record for each scenario. Two things to look for:

1. **It shows every rule that runs.** Each line is one rule execution, with the row's state, old and new values. You see not just that a test passed, but which rules ran and what each one changed.
2. **The nesting shows multi-table chaining.** Indentation follows the cascade: a change to an Item adjusts its Order, which adjusts its Customer.

<details markdown>
<summary>How to read the logic log</summary>

Open a scenario's "Rules exercised and logic log" block to see it. The log is shown in full, attribute values included, because those values are what you diagnose from when a rule produces an unexpected result.

To read a log line:

```
....Order[16] {Update - Adjusting order: amount_total} id: 16, customer_id: 19, amount_total:  [0.0-->] 90.0

```

- The leading dots are the depth in the cascade: Item (2 dots), its Order (4), its Customer (6).
- `Order[16]` is the row; `{...}` is the rule or action that ran; the rest is the row's attribute values at that step.
- `[0.0-->] 90.0` marks a value the rules changed, with its old and new value.
- The log is in phases: **ROW LOGIC** (derivations and constraints, as rows change), **COMMIT LOGIC** (checks that need the finished aggregates), and **AFTER_FLUSH LOGIC** (events that need database-assigned keys, such as the Kafka publish).

More: [Logic Log](https://apilogicserver.github.io/Docs/Logic-Debug/#logic-log).

</details>

&nbsp;

<details markdown>
<summary>How to add more tests, and run them</summary>

**1. Have AI create them.** This project's context tells your AI assistant how (`.github/copilot-instructions.md`, `docs/training/testing.md`). Just say:

```

create tests from rules

```

The assistant reads `database/models.py`, the logic files and the custom APIs, then writes `.feature` files and step implementations under `test/api_logic_server_behave/features/`. Then say `run the tests` and `run the requirements traceability report` and the assistant does both.

Or, to have each requirement's tests linked in the Tests column above (it matches on `Feature:` name), say which names to use:

```

create tests from rules, one Feature per requirement, named exactly:
- Check Credit
- App Integration

```

_Tests with other names still run and appear below; they just aren't linked to a requirement._

**2. You can also define tests manually.** Add a `<name>.feature` file (Gherkin) under `test/api_logic_server_behave/features/` and its steps under `features/steps/`. The steps call the running API, so tests exercise the same rules as any client. See `docs/training/testing.md` for the patterns that keep tests repeatable.

**Or run them yourself** (server running, from `test/api_logic_server_behave`):

```

python behave_run.py --outfile=logs/behave.log
python requirements_traceability_report.py run

```

</details>

&nbsp;
&nbsp;

### Feature: App Integration  

&nbsp;
&nbsp;

#### Scenario: Kafka - shipped order ✅ (0.05 s)
&emsp;  Scenario: Kafka - shipped order  
&emsp;&emsp;    Given a customer with credit limit 1000  
&emsp;&emsp;    And a product priced 10 with no suppliers  
&emsp;&emsp;    And an order is created with 5 of the product  
&emsp;&emsp;    When the order is shipped  
&emsp;&emsp;    Then the logic log shows the order sent to Kafka topic "order_shipping"  

<details markdown>
<summary>Rules exercised and logic log (3 transactions)</summary>


&nbsp;
&nbsp;


**Rules Used** in Scenario: Kafka - shipped order
```
  Customer  
    1. Derive Customer.balance as Sum(Order.amount_total Where Rule.sum(derive=models.Customer.balance, as_sum_of=models.Order.amount_total, where=lambda row: row.date_shipped is None))  
  Order  
    2. RowEvent Order.send_row_to_kafka()  
    3. Derive Order.amount_total as Sum(Item.amount Where  - None)  
  Item  
    4. Derive Item.amount as Formula (1): Rule.formula(derive=models.Item.amount, as_expres [...]  
    5. RowEvent Item.set_item_unit_price_from_supplier()  
```
**Logic Log** in Scenario: Kafka - shipped order (3 transactions)
```
Logic Phase:		ROW LOGIC		(session=0x10c3162c0) (sqlalchemy before_flush)			 - 2026-11-04 18:03:00,359 - logic_logger - INFO
..Order[None] {Insert - client} id: None, notes: test 1793844180355, customer_id: 24, CreatedOn: None, date_shipped: None, amount_total: None  row: 0x10c47b1d0  session: 0x10c3162c0  ins_upd_dlt: ins, initial: ins - 2026-11-04 18:03:00,359 - logic_logger - INFO
..Order[None] {server aggregate_defaults: amount_total } id: None, notes: test 1793844180355, customer_id: 24, CreatedOn: None, date_shipped: None, amount_total: 0  row: 0x10c47b1d0  session: 0x10c3162c0  ins_upd_dlt: ins, initial: ins - 2026-11-04 18:03:00,359 - logic_logger - INFO
Logic Phase:		COMMIT LOGIC		(session=0x10c3162c0)   										 - 2026-11-04 18:03:00,360 - logic_logger - INFO
Logic Phase:		AFTER_FLUSH LOGIC	(session=0x10c3162c0)   										 - 2026-11-04 18:03:00,361 - logic_logger - INFO
..Order[23] {AfterFlush Event} id: 23, notes: test 1793844180355, customer_id: 24, CreatedOn: None, date_shipped: None, amount_total: 0  row: 0x10c47b1d0  session: 0x10c3162c0  ins_upd_dlt: ins, initial: ins - 2026-11-04 18:03:00,361 - logic_logger - INFO


Logic Phase:		ROW LOGIC		(session=0x10c316780) (sqlalchemy before_flush)			 - 2026-11-04 18:03:00,367 - logic_logger - INFO
..Item[None] {Insert - client} id: None, order_id: 23, product_id: 27, quantity: 5, amount: None, unit_price: None  row: 0x10c47a9d0  session: 0x10c316780  ins_upd_dlt: ins, initial: ins - 2026-11-04 18:03:00,367 - logic_logger - INFO
..Item[None] {No suppliers for Test Product 1793844180348, using product unit_price} id: None, order_id: 23, product_id: 27, quantity: 5, amount: None, unit_price: None  row: 0x10c47a9d0  session: 0x10c316780  ins_upd_dlt: ins, initial: ins - 2026-11-04 18:03:00,369 - logic_logger - INFO
..Item[None] {Formula amount} id: None, order_id: 23, product_id: 27, quantity: 5, amount: 50.0000000000, unit_price: 10.0000000000  row: 0x10c47a9d0  session: 0x10c316780  ins_upd_dlt: ins, initial: ins - 2026-11-04 18:03:00,370 - logic_logger - INFO
....Order[23] {Update - Adjusting order: amount_total} id: 23, notes: test 1793844180355, customer_id: 24, CreatedOn: None, date_shipped: None, amount_total:  [0E-10-->] 50.0000000000  row: 0x10c4b57d0  session: 0x10c316780  ins_upd_dlt: upd, initial: upd - 2026-11-04 18:03:00,370 - logic_logger - INFO
......Customer[24] {Update - Adjusting customer: balance} id: 24, name: Test Customer 1793844180339, balance:  [0E-10-->] 50.0000000000, credit_limit: 1000.0000000000, email: None, email_opt_out: None  row: 0x10c4b5ad0  session: 0x10c316780  ins_upd_dlt: upd, initial: upd - 2026-11-04 18:03:00,371 - logic_logger - INFO
Logic Phase:		COMMIT LOGIC		(session=0x10c316780)   										 - 2026-11-04 18:03:00,371 - logic_logger - INFO
Logic Phase:		AFTER_FLUSH LOGIC	(session=0x10c316780)   										 - 2026-11-04 18:03:00,373 - logic_logger - INFO
....Order[23] {AfterFlush Event} id: 23, notes: test 1793844180355, customer_id: 24, CreatedOn: None, date_shipped: None, amount_total:  [0E-10-->] 50.0000000000  row: 0x10c4b57d0  session: 0x10c316780  ins_upd_dlt: upd, initial: upd - 2026-11-04 18:03:00,373 - logic_logger - INFO


Logic Phase:		ROW LOGIC		(session=0x10bbb1c70) (sqlalchemy before_flush)			 - 2026-11-04 18:03:00,380 - logic_logger - INFO
..Order[23] {Update - client} id: 23, notes: test 1793844180355, customer_id: 24, CreatedOn: None, date_shipped:  [None-->] 2026-11-04 00:00:00, amount_total: 50.0000000000  row: 0x10c4b7050  session: 0x10bbb1c70  ins_upd_dlt: upd, initial: upd - 2026-11-04 18:03:00,380 - logic_logger - INFO
....Customer[24] {Update - Adjusting customer: balance} id: 24, name: Test Customer 1793844180339, balance:  [50.0000000000-->] 0E-10, credit_limit: 1000.0000000000, email: None, email_opt_out: None  row: 0x10c5204d0  session: 0x10bbb1c70  ins_upd_dlt: upd, initial: upd - 2026-11-04 18:03:00,381 - logic_logger - INFO
Logic Phase:		COMMIT LOGIC		(session=0x10bbb1c70)   										 - 2026-11-04 18:03:00,381 - logic_logger - INFO
Logic Phase:		AFTER_FLUSH LOGIC	(session=0x10bbb1c70)   										 - 2026-11-04 18:03:00,382 - logic_logger - INFO
..Order[23] {AfterFlush Event} id: 23, notes: test 1793844180355, customer_id: 24, CreatedOn: None, date_shipped:  [None-->] 2026-11-04 00:00:00, amount_total: 50.0000000000  row: 0x10c4b7050  session: 0x10bbb1c70  ins_upd_dlt: upd, initial: upd - 2026-11-04 18:03:00,382 - logic_logger - INFO
..Order[23] {Sending Order to Kafka topic 'order_shipping' [Note: **Kafka not enabled** ]} id: 23, notes: test 1793844180355, customer_id: 24, CreatedOn: None, date_shipped:  [None-->] 2026-11-04 00:00:00, amount_total: 50.0000000000  row: 0x10c4b7050  session: 0x10bbb1c70  ins_upd_dlt: upd, initial: upd - 2026-11-04 18:03:00,382 - logic_logger - INFO

```
</details>

&nbsp;
&nbsp;

#### Scenario: Kafka - unshipped order ✅ (0.03 s)
&emsp;  Scenario: Kafka - unshipped order  
&emsp;&emsp;    Given a customer with credit limit 1000  
&emsp;&emsp;    And a product priced 10 with no suppliers  
&emsp;&emsp;    When an order is created with 5 of the product  
&emsp;&emsp;    Then the logic log shows no message sent to Kafka topic "order_shipping"  

<details markdown>
<summary>Rules exercised and logic log (2 transactions)</summary>


&nbsp;
&nbsp;


**Rules Used** in Scenario: Kafka - unshipped order
```
  Customer  
    1. Derive Customer.balance as Sum(Order.amount_total Where Rule.sum(derive=models.Customer.balance, as_sum_of=models.Order.amount_total, where=lambda row: row.date_shipped is None))  
  Order  
    2. RowEvent Order.send_row_to_kafka()  
    3. Derive Order.amount_total as Sum(Item.amount Where  - None)  
  Item  
    4. Derive Item.amount as Formula (1): Rule.formula(derive=models.Item.amount, as_expres [...]  
    5. RowEvent Item.set_item_unit_price_from_supplier()  
```
**Logic Log** in Scenario: Kafka - unshipped order (2 transactions)
```
Logic Phase:		ROW LOGIC		(session=0x10c4c09e0) (sqlalchemy before_flush)			 - 2026-11-04 18:03:00,401 - logic_logger - INFO
..Order[None] {Insert - client} id: None, notes: test 1793844180399, customer_id: 25, CreatedOn: None, date_shipped: None, amount_total: None  row: 0x10c47bbd0  session: 0x10c4c09e0  ins_upd_dlt: ins, initial: ins - 2026-11-04 18:03:00,401 - logic_logger - INFO
..Order[None] {server aggregate_defaults: amount_total } id: None, notes: test 1793844180399, customer_id: 25, CreatedOn: None, date_shipped: None, amount_total: 0  row: 0x10c47bbd0  session: 0x10c4c09e0  ins_upd_dlt: ins, initial: ins - 2026-11-04 18:03:00,402 - logic_logger - INFO
Logic Phase:		COMMIT LOGIC		(session=0x10c4c09e0)   										 - 2026-11-04 18:03:00,402 - logic_logger - INFO
Logic Phase:		AFTER_FLUSH LOGIC	(session=0x10c4c09e0)   										 - 2026-11-04 18:03:00,402 - logic_logger - INFO
..Order[24] {AfterFlush Event} id: 24, notes: test 1793844180399, customer_id: 25, CreatedOn: None, date_shipped: None, amount_total: 0  row: 0x10c47bbd0  session: 0x10c4c09e0  ins_upd_dlt: ins, initial: ins - 2026-11-04 18:03:00,403 - logic_logger - INFO


Logic Phase:		ROW LOGIC		(session=0x10c4c1150) (sqlalchemy before_flush)			 - 2026-11-04 18:03:00,407 - logic_logger - INFO
..Item[None] {Insert - client} id: None, order_id: 24, product_id: 28, quantity: 5, amount: None, unit_price: None  row: 0x10c4793d0  session: 0x10c4c1150  ins_upd_dlt: ins, initial: ins - 2026-11-04 18:03:00,407 - logic_logger - INFO
..Item[None] {No suppliers for Test Product 1793844180394, using product unit_price} id: None, order_id: 24, product_id: 28, quantity: 5, amount: None, unit_price: None  row: 0x10c4793d0  session: 0x10c4c1150  ins_upd_dlt: ins, initial: ins - 2026-11-04 18:03:00,408 - logic_logger - INFO
..Item[None] {Formula amount} id: None, order_id: 24, product_id: 28, quantity: 5, amount: 50.0000000000, unit_price: 10.0000000000  row: 0x10c4793d0  session: 0x10c4c1150  ins_upd_dlt: ins, initial: ins - 2026-11-04 18:03:00,408 - logic_logger - INFO
....Order[24] {Update - Adjusting order: amount_total} id: 24, notes: test 1793844180399, customer_id: 25, CreatedOn: None, date_shipped: None, amount_total:  [0E-10-->] 50.0000000000  row: 0x10c47b1d0  session: 0x10c4c1150  ins_upd_dlt: upd, initial: upd - 2026-11-04 18:03:00,408 - logic_logger - INFO
......Customer[25] {Update - Adjusting customer: balance} id: 25, name: Test Customer 1793844180388, balance:  [0E-10-->] 50.0000000000, credit_limit: 1000.0000000000, email: None, email_opt_out: None  row: 0x10c520bd0  session: 0x10c4c1150  ins_upd_dlt: upd, initial: upd - 2026-11-04 18:03:00,409 - logic_logger - INFO
Logic Phase:		COMMIT LOGIC		(session=0x10c4c1150)   										 - 2026-11-04 18:03:00,409 - logic_logger - INFO
Logic Phase:		AFTER_FLUSH LOGIC	(session=0x10c4c1150)   										 - 2026-11-04 18:03:00,410 - logic_logger - INFO
....Order[24] {AfterFlush Event} id: 24, notes: test 1793844180399, customer_id: 25, CreatedOn: None, date_shipped: None, amount_total:  [0E-10-->] 50.0000000000  row: 0x10c47b1d0  session: 0x10c4c1150  ins_upd_dlt: upd, initial: upd - 2026-11-04 18:03:00,410 - logic_logger - INFO

```
</details>

&nbsp;
&nbsp;

#### Scenario: Kafka - edit shipped order ✅ (0.04 s)
&emsp;  Scenario: Kafka - edit shipped order  
&emsp;&emsp;    Given a customer with credit limit 1000  
&emsp;&emsp;    And a product priced 10 with no suppliers  
&emsp;&emsp;    And an order is created with 5 of the product  
&emsp;&emsp;    And the order is shipped  
&emsp;&emsp;    When the order notes are edited  
&emsp;&emsp;    Then the logic log shows the order sent to Kafka topic "order_shipping" 1 time  

<details markdown>
<summary>Rules exercised and logic log (4 transactions)</summary>


&nbsp;
&nbsp;


**Rules Used** in Scenario: Kafka - edit shipped order
```
  Customer  
    1. Derive Customer.balance as Sum(Order.amount_total Where Rule.sum(derive=models.Customer.balance, as_sum_of=models.Order.amount_total, where=lambda row: row.date_shipped is None))  
  Order  
    2. RowEvent Order.send_row_to_kafka()  
    3. Derive Order.amount_total as Sum(Item.amount Where  - None)  
  Item  
    4. Derive Item.amount as Formula (1): Rule.formula(derive=models.Item.amount, as_expres [...]  
    5. RowEvent Item.set_item_unit_price_from_supplier()  
```
**Logic Log** in Scenario: Kafka - edit shipped order (4 transactions)
```
Logic Phase:		ROW LOGIC		(session=0x10c4c19d0) (sqlalchemy before_flush)			 - 2026-11-04 18:03:00,427 - logic_logger - INFO
..Order[None] {Insert - client} id: None, notes: test 1793844180425, customer_id: 26, CreatedOn: None, date_shipped: None, amount_total: None  row: 0x10c4b6a50  session: 0x10c4c19d0  ins_upd_dlt: ins, initial: ins - 2026-11-04 18:03:00,427 - logic_logger - INFO
..Order[None] {server aggregate_defaults: amount_total } id: None, notes: test 1793844180425, customer_id: 26, CreatedOn: None, date_shipped: None, amount_total: 0  row: 0x10c4b6a50  session: 0x10c4c19d0  ins_upd_dlt: ins, initial: ins - 2026-11-04 18:03:00,427 - logic_logger - INFO
Logic Phase:		COMMIT LOGIC		(session=0x10c4c19d0)   										 - 2026-11-04 18:03:00,428 - logic_logger - INFO
Logic Phase:		AFTER_FLUSH LOGIC	(session=0x10c4c19d0)   										 - 2026-11-04 18:03:00,428 - logic_logger - INFO
..Order[25] {AfterFlush Event} id: 25, notes: test 1793844180425, customer_id: 26, CreatedOn: None, date_shipped: None, amount_total: 0  row: 0x10c4b6a50  session: 0x10c4c19d0  ins_upd_dlt: ins, initial: ins - 2026-11-04 18:03:00,428 - logic_logger - INFO


Logic Phase:		ROW LOGIC		(session=0x10c4c1bf0) (sqlalchemy before_flush)			 - 2026-11-04 18:03:00,434 - logic_logger - INFO
..Item[None] {Insert - client} id: None, order_id: 25, product_id: 29, quantity: 5, amount: None, unit_price: None  row: 0x10c4b48d0  session: 0x10c4c1bf0  ins_upd_dlt: ins, initial: ins - 2026-11-04 18:03:00,434 - logic_logger - INFO
..Item[None] {No suppliers for Test Product 1793844180421, using product unit_price} id: None, order_id: 25, product_id: 29, quantity: 5, amount: None, unit_price: None  row: 0x10c4b48d0  session: 0x10c4c1bf0  ins_upd_dlt: ins, initial: ins - 2026-11-04 18:03:00,435 - logic_logger - INFO
..Item[None] {Formula amount} id: None, order_id: 25, product_id: 29, quantity: 5, amount: 50.0000000000, unit_price: 10.0000000000  row: 0x10c4b48d0  session: 0x10c4c1bf0  ins_upd_dlt: ins, initial: ins - 2026-11-04 18:03:00,435 - logic_logger - INFO
....Order[25] {Update - Adjusting order: amount_total} id: 25, notes: test 1793844180425, customer_id: 26, CreatedOn: None, date_shipped: None, amount_total:  [0E-10-->] 50.0000000000  row: 0x10c5209d0  session: 0x10c4c1bf0  ins_upd_dlt: upd, initial: upd - 2026-11-04 18:03:00,435 - logic_logger - INFO
......Customer[26] {Update - Adjusting customer: balance} id: 26, name: Test Customer 1793844180416, balance:  [0E-10-->] 50.0000000000, credit_limit: 1000.0000000000, email: None, email_opt_out: None  row: 0x10c47bbd0  session: 0x10c4c1bf0  ins_upd_dlt: upd, initial: upd - 2026-11-04 18:03:00,436 - logic_logger - INFO
Logic Phase:		COMMIT LOGIC		(session=0x10c4c1bf0)   										 - 2026-11-04 18:03:00,436 - logic_logger - INFO
Logic Phase:		AFTER_FLUSH LOGIC	(session=0x10c4c1bf0)   										 - 2026-11-04 18:03:00,437 - logic_logger - INFO
....Order[25] {AfterFlush Event} id: 25, notes: test 1793844180425, customer_id: 26, CreatedOn: None, date_shipped: None, amount_total:  [0E-10-->] 50.0000000000  row: 0x10c5209d0  session: 0x10c4c1bf0  ins_upd_dlt: upd, initial: upd - 2026-11-04 18:03:00,437 - logic_logger - INFO


Logic Phase:		ROW LOGIC		(session=0x10c3d3bd0) (sqlalchemy before_flush)			 - 2026-11-04 18:03:00,443 - logic_logger - INFO
..Order[25] {Update - client} id: 25, notes: test 1793844180425, customer_id: 26, CreatedOn: None, date_shipped:  [None-->] 2026-11-04 00:00:00, amount_total: 50.0000000000  row: 0x10c4b7050  session: 0x10c3d3bd0  ins_upd_dlt: upd, initial: upd - 2026-11-04 18:03:00,443 - logic_logger - INFO
....Customer[26] {Update - Adjusting customer: balance} id: 26, name: Test Customer 1793844180416, balance:  [50.0000000000-->] 0E-10, credit_limit: 1000.0000000000, email: None, email_opt_out: None  row: 0x10c520250  session: 0x10c3d3bd0  ins_upd_dlt: upd, initial: upd - 2026-11-04 18:03:00,444 - logic_logger - INFO
Logic Phase:		COMMIT LOGIC		(session=0x10c3d3bd0)   										 - 2026-11-04 18:03:00,444 - logic_logger - INFO
Logic Phase:		AFTER_FLUSH LOGIC	(session=0x10c3d3bd0)   										 - 2026-11-04 18:03:00,445 - logic_logger - INFO
..Order[25] {AfterFlush Event} id: 25, notes: test 1793844180425, customer_id: 26, CreatedOn: None, date_shipped:  [None-->] 2026-11-04 00:00:00, amount_total: 50.0000000000  row: 0x10c4b7050  session: 0x10c3d3bd0  ins_upd_dlt: upd, initial: upd - 2026-11-04 18:03:00,445 - logic_logger - INFO
..Order[25] {Sending Order to Kafka topic 'order_shipping' [Note: **Kafka not enabled** ]} id: 25, notes: test 1793844180425, customer_id: 26, CreatedOn: None, date_shipped:  [None-->] 2026-11-04 00:00:00, amount_total: 50.0000000000  row: 0x10c4b7050  session: 0x10c3d3bd0  ins_upd_dlt: upd, initial: upd - 2026-11-04 18:03:00,445 - logic_logger - INFO


Logic Phase:		ROW LOGIC		(session=0x10c3d3f00) (sqlalchemy before_flush)			 - 2026-11-04 18:03:00,451 - logic_logger - INFO
..Order[25] {Update - client} id: 25, notes:  [test 1793844180425-->] edited 1793844180448, customer_id: 26, CreatedOn: None, date_shipped: 2026-11-04, amount_total: 50.0000000000  row: 0x10c4b77d0  session: 0x10c3d3f00  ins_upd_dlt: upd, initial: upd - 2026-11-04 18:03:00,451 - logic_logger - INFO
Logic Phase:		COMMIT LOGIC		(session=0x10c3d3f00)   										 - 2026-11-04 18:03:00,451 - logic_logger - INFO
Logic Phase:		AFTER_FLUSH LOGIC	(session=0x10c3d3f00)   										 - 2026-11-04 18:03:00,452 - logic_logger - INFO
..Order[25] {AfterFlush Event} id: 25, notes:  [test 1793844180425-->] edited 1793844180448, customer_id: 26, CreatedOn: None, date_shipped: 2026-11-04, amount_total: 50.0000000000  row: 0x10c4b77d0  session: 0x10c3d3f00  ins_upd_dlt: upd, initial: upd - 2026-11-04 18:03:00,452 - logic_logger - INFO

```
</details>

&nbsp;
&nbsp;

### Feature: Check Credit  

&nbsp;
&nbsp;

#### Scenario: Credit - within limit ✅ (0.04 s)
&emsp;  Scenario: Credit - within limit  
&emsp;&emsp;    Given a customer with credit limit 1000  
&emsp;&emsp;    And a product priced 10 with no suppliers  
&emsp;&emsp;    When an order is created with 5 of the product  
&emsp;&emsp;    Then the customer balance is 50  
&emsp;&emsp;    And the order amount total is 50  
&emsp;&emsp;    And the item amount is 50  

<details markdown>
<summary>Rules exercised and logic log (2 transactions)</summary>


&nbsp;
&nbsp;


**Rules Used** in Scenario: Credit - within limit
```
  Customer  
    1. Derive Customer.balance as Sum(Order.amount_total Where Rule.sum(derive=models.Customer.balance, as_sum_of=models.Order.amount_total, where=lambda row: row.date_shipped is None))  
  Order  
    2. RowEvent Order.send_row_to_kafka()  
    3. Derive Order.amount_total as Sum(Item.amount Where  - None)  
  Item  
    4. Derive Item.amount as Formula (1): Rule.formula(derive=models.Item.amount, as_expres [...]  
    5. RowEvent Item.set_item_unit_price_from_supplier()  
```
**Logic Log** in Scenario: Credit - within limit (2 transactions)
```
Logic Phase:		ROW LOGIC		(session=0x10c4c1150) (sqlalchemy before_flush)			 - 2026-11-04 18:03:00,472 - logic_logger - INFO
..Order[None] {Insert - client} id: None, notes: test 1793844180471, customer_id: 27, CreatedOn: None, date_shipped: None, amount_total: None  row: 0x10c4b4450  session: 0x10c4c1150  ins_upd_dlt: ins, initial: ins - 2026-11-04 18:03:00,473 - logic_logger - INFO
..Order[None] {server aggregate_defaults: amount_total } id: None, notes: test 1793844180471, customer_id: 27, CreatedOn: None, date_shipped: None, amount_total: 0  row: 0x10c4b4450  session: 0x10c4c1150  ins_upd_dlt: ins, initial: ins - 2026-11-04 18:03:00,473 - logic_logger - INFO
Logic Phase:		COMMIT LOGIC		(session=0x10c4c1150)   										 - 2026-11-04 18:03:00,473 - logic_logger - INFO
Logic Phase:		AFTER_FLUSH LOGIC	(session=0x10c4c1150)   										 - 2026-11-04 18:03:00,474 - logic_logger - INFO
..Order[26] {AfterFlush Event} id: 26, notes: test 1793844180471, customer_id: 27, CreatedOn: None, date_shipped: None, amount_total: 0  row: 0x10c4b4450  session: 0x10c4c1150  ins_upd_dlt: ins, initial: ins - 2026-11-04 18:03:00,474 - logic_logger - INFO


Logic Phase:		ROW LOGIC		(session=0x10c4c09e0) (sqlalchemy before_flush)			 - 2026-11-04 18:03:00,478 - logic_logger - INFO
..Item[None] {Insert - client} id: None, order_id: 26, product_id: 30, quantity: 5, amount: None, unit_price: None  row: 0x10c4793d0  session: 0x10c4c09e0  ins_upd_dlt: ins, initial: ins - 2026-11-04 18:03:00,479 - logic_logger - INFO
..Item[None] {No suppliers for Test Product 1793844180465, using product unit_price} id: None, order_id: 26, product_id: 30, quantity: 5, amount: None, unit_price: None  row: 0x10c4793d0  session: 0x10c4c09e0  ins_upd_dlt: ins, initial: ins - 2026-11-04 18:03:00,479 - logic_logger - INFO
..Item[None] {Formula amount} id: None, order_id: 26, product_id: 30, quantity: 5, amount: 50.0000000000, unit_price: 10.0000000000  row: 0x10c4793d0  session: 0x10c4c09e0  ins_upd_dlt: ins, initial: ins - 2026-11-04 18:03:00,479 - logic_logger - INFO
....Order[26] {Update - Adjusting order: amount_total} id: 26, notes: test 1793844180471, customer_id: 27, CreatedOn: None, date_shipped: None, amount_total:  [0E-10-->] 50.0000000000  row: 0x10c520ed0  session: 0x10c4c09e0  ins_upd_dlt: upd, initial: upd - 2026-11-04 18:03:00,480 - logic_logger - INFO
......Customer[27] {Update - Adjusting customer: balance} id: 27, name: Test Customer 1793844180459, balance:  [0E-10-->] 50.0000000000, credit_limit: 1000.0000000000, email: None, email_opt_out: None  row: 0x10c5214d0  session: 0x10c4c09e0  ins_upd_dlt: upd, initial: upd - 2026-11-04 18:03:00,480 - logic_logger - INFO
Logic Phase:		COMMIT LOGIC		(session=0x10c4c09e0)   										 - 2026-11-04 18:03:00,480 - logic_logger - INFO
Logic Phase:		AFTER_FLUSH LOGIC	(session=0x10c4c09e0)   										 - 2026-11-04 18:03:00,481 - logic_logger - INFO
....Order[26] {AfterFlush Event} id: 26, notes: test 1793844180471, customer_id: 27, CreatedOn: None, date_shipped: None, amount_total:  [0E-10-->] 50.0000000000  row: 0x10c520ed0  session: 0x10c4c09e0  ins_upd_dlt: upd, initial: upd - 2026-11-04 18:03:00,481 - logic_logger - INFO

```
</details>

&nbsp;
&nbsp;

#### Scenario: Credit - at the limit ✅ (0.03 s)
&emsp;  Scenario: Credit - at the limit  
&emsp;&emsp;    Given a customer with credit limit 100  
&emsp;&emsp;    And a product priced 10 with no suppliers  
&emsp;&emsp;    When an order is created with 10 of the product  
&emsp;&emsp;    Then the customer balance is 100  

<details markdown>
<summary>Rules exercised and logic log (2 transactions)</summary>


&nbsp;
&nbsp;


**Rules Used** in Scenario: Credit - at the limit
```
  Customer  
    1. Derive Customer.balance as Sum(Order.amount_total Where Rule.sum(derive=models.Customer.balance, as_sum_of=models.Order.amount_total, where=lambda row: row.date_shipped is None))  
  Order  
    2. RowEvent Order.send_row_to_kafka()  
    3. Derive Order.amount_total as Sum(Item.amount Where  - None)  
  Item  
    4. Derive Item.amount as Formula (1): Rule.formula(derive=models.Item.amount, as_expres [...]  
    5. RowEvent Item.set_item_unit_price_from_supplier()  
```
**Logic Log** in Scenario: Credit - at the limit (2 transactions)
```
Logic Phase:		ROW LOGIC		(session=0x10c4c1e10) (sqlalchemy before_flush)			 - 2026-11-04 18:03:00,507 - logic_logger - INFO
..Order[None] {Insert - client} id: None, notes: test 1793844180505, customer_id: 28, CreatedOn: None, date_shipped: None, amount_total: None  row: 0x10c4b7350  session: 0x10c4c1e10  ins_upd_dlt: ins, initial: ins - 2026-11-04 18:03:00,507 - logic_logger - INFO
..Order[None] {server aggregate_defaults: amount_total } id: None, notes: test 1793844180505, customer_id: 28, CreatedOn: None, date_shipped: None, amount_total: 0  row: 0x10c4b7350  session: 0x10c4c1e10  ins_upd_dlt: ins, initial: ins - 2026-11-04 18:03:00,507 - logic_logger - INFO
Logic Phase:		COMMIT LOGIC		(session=0x10c4c1e10)   										 - 2026-11-04 18:03:00,508 - logic_logger - INFO
Logic Phase:		AFTER_FLUSH LOGIC	(session=0x10c4c1e10)   										 - 2026-11-04 18:03:00,508 - logic_logger - INFO
..Order[27] {AfterFlush Event} id: 27, notes: test 1793844180505, customer_id: 28, CreatedOn: None, date_shipped: None, amount_total: 0  row: 0x10c4b7350  session: 0x10c4c1e10  ins_upd_dlt: ins, initial: ins - 2026-11-04 18:03:00,508 - logic_logger - INFO


Logic Phase:		ROW LOGIC		(session=0x10c4c2030) (sqlalchemy before_flush)			 - 2026-11-04 18:03:00,512 - logic_logger - INFO
..Item[None] {Insert - client} id: None, order_id: 27, product_id: 31, quantity: 10, amount: None, unit_price: None  row: 0x10c4b7c50  session: 0x10c4c2030  ins_upd_dlt: ins, initial: ins - 2026-11-04 18:03:00,512 - logic_logger - INFO
..Item[None] {No suppliers for Test Product 1793844180501, using product unit_price} id: None, order_id: 27, product_id: 31, quantity: 10, amount: None, unit_price: None  row: 0x10c4b7c50  session: 0x10c4c2030  ins_upd_dlt: ins, initial: ins - 2026-11-04 18:03:00,513 - logic_logger - INFO
..Item[None] {Formula amount} id: None, order_id: 27, product_id: 31, quantity: 10, amount: 100.0000000000, unit_price: 10.0000000000  row: 0x10c4b7c50  session: 0x10c4c2030  ins_upd_dlt: ins, initial: ins - 2026-11-04 18:03:00,513 - logic_logger - INFO
....Order[27] {Update - Adjusting order: amount_total} id: 27, notes: test 1793844180505, customer_id: 28, CreatedOn: None, date_shipped: None, amount_total:  [0E-10-->] 100.0000000000  row: 0x10c520b50  session: 0x10c4c2030  ins_upd_dlt: upd, initial: upd - 2026-11-04 18:03:00,513 - logic_logger - INFO
......Customer[28] {Update - Adjusting customer: balance} id: 28, name: Test Customer 1793844180496, balance:  [0E-10-->] 100.0000000000, credit_limit: 100.0000000000, email: None, email_opt_out: None  row: 0x10c521d50  session: 0x10c4c2030  ins_upd_dlt: upd, initial: upd - 2026-11-04 18:03:00,514 - logic_logger - INFO
Logic Phase:		COMMIT LOGIC		(session=0x10c4c2030)   										 - 2026-11-04 18:03:00,514 - logic_logger - INFO
Logic Phase:		AFTER_FLUSH LOGIC	(session=0x10c4c2030)   										 - 2026-11-04 18:03:00,515 - logic_logger - INFO
....Order[27] {AfterFlush Event} id: 27, notes: test 1793844180505, customer_id: 28, CreatedOn: None, date_shipped: None, amount_total:  [0E-10-->] 100.0000000000  row: 0x10c520b50  session: 0x10c4c2030  ins_upd_dlt: upd, initial: upd - 2026-11-04 18:03:00,515 - logic_logger - INFO

```
</details>

&nbsp;
&nbsp;

#### Scenario: Credit - over the limit ✅ (0.03 s)
&emsp;  Scenario: Credit - over the limit  
&emsp;&emsp;    Given a customer with credit limit 100  
&emsp;&emsp;    And a product priced 10 with no suppliers  
&emsp;&emsp;    When an order is created with 11 of the product  
&emsp;&emsp;    Then the item is rejected with a message containing "exceeds credit limit"  
&emsp;&emsp;    And the customer balance is 0  

<details markdown>
<summary>Rules exercised and logic log (2 transactions)</summary>


&nbsp;
&nbsp;


**Rules Used** in Scenario: Credit - over the limit
```
  Customer  
    1. Derive Customer.balance as Sum(Order.amount_total Where Rule.sum(derive=models.Customer.balance, as_sum_of=models.Order.amount_total, where=lambda row: row.date_shipped is None))  
    2. Constraint Function: None  
  Order  
    3. RowEvent Order.send_row_to_kafka()  
    4. Derive Order.amount_total as Sum(Item.amount Where  - None)  
  Item  
    5. Derive Item.amount as Formula (1): Rule.formula(derive=models.Item.amount, as_expres [...]  
    6. RowEvent Item.set_item_unit_price_from_supplier()  
```
**Logic Log** in Scenario: Credit - over the limit (2 transactions)
```
Logic Phase:		ROW LOGIC		(session=0x10c4c27a0) (sqlalchemy before_flush)			 - 2026-11-04 18:03:00,535 - logic_logger - INFO
..Order[None] {Insert - client} id: None, notes: test 1793844180533, customer_id: 29, CreatedOn: None, date_shipped: None, amount_total: None  row: 0x10c47add0  session: 0x10c4c27a0  ins_upd_dlt: ins, initial: ins - 2026-11-04 18:03:00,535 - logic_logger - INFO
..Order[None] {server aggregate_defaults: amount_total } id: None, notes: test 1793844180533, customer_id: 29, CreatedOn: None, date_shipped: None, amount_total: 0  row: 0x10c47add0  session: 0x10c4c27a0  ins_upd_dlt: ins, initial: ins - 2026-11-04 18:03:00,535 - logic_logger - INFO
Logic Phase:		COMMIT LOGIC		(session=0x10c4c27a0)   										 - 2026-11-04 18:03:00,536 - logic_logger - INFO
Logic Phase:		AFTER_FLUSH LOGIC	(session=0x10c4c27a0)   										 - 2026-11-04 18:03:00,536 - logic_logger - INFO
..Order[28] {AfterFlush Event} id: 28, notes: test 1793844180533, customer_id: 29, CreatedOn: None, date_shipped: None, amount_total: 0  row: 0x10c47add0  session: 0x10c4c27a0  ins_upd_dlt: ins, initial: ins - 2026-11-04 18:03:00,536 - logic_logger - INFO


Logic Phase:		ROW LOGIC		(session=0x10c4c29c0) (sqlalchemy before_flush)			 - 2026-11-04 18:03:00,541 - logic_logger - INFO
..Item[None] {Insert - client} id: None, order_id: 28, product_id: 32, quantity: 11, amount: None, unit_price: None  row: 0x10c479150  session: 0x10c4c29c0  ins_upd_dlt: ins, initial: ins - 2026-11-04 18:03:00,541 - logic_logger - INFO
..Item[None] {No suppliers for Test Product 1793844180528, using product unit_price} id: None, order_id: 28, product_id: 32, quantity: 11, amount: None, unit_price: None  row: 0x10c479150  session: 0x10c4c29c0  ins_upd_dlt: ins, initial: ins - 2026-11-04 18:03:00,541 - logic_logger - INFO
..Item[None] {Formula amount} id: None, order_id: 28, product_id: 32, quantity: 11, amount: 110.0000000000, unit_price: 10.0000000000  row: 0x10c479150  session: 0x10c4c29c0  ins_upd_dlt: ins, initial: ins - 2026-11-04 18:03:00,542 - logic_logger - INFO
....Order[28] {Update - Adjusting order: amount_total} id: 28, notes: test 1793844180533, customer_id: 29, CreatedOn: None, date_shipped: None, amount_total:  [0E-10-->] 110.0000000000  row: 0x10c5215d0  session: 0x10c4c29c0  ins_upd_dlt: upd, initial: upd - 2026-11-04 18:03:00,542 - logic_logger - INFO
......Customer[29] {Update - Adjusting customer: balance} id: 29, name: Test Customer 1793844180523, balance:  [0E-10-->] 110.0000000000, credit_limit: 100.0000000000, email: None, email_opt_out: None  row: 0x10c5224d0  session: 0x10c4c29c0  ins_upd_dlt: upd, initial: upd - 2026-11-04 18:03:00,542 - logic_logger - INFO
......Customer[29] {Constraint Failure: Customer balance (110.0000000000) exceeds credit limit (100.0000000000)} id: 29, name: Test Customer 1793844180523, balance:  [0E-10-->] 110.0000000000, credit_limit: 100.0000000000, email: None, email_opt_out: None  row: 0x10c5224d0  session: 0x10c4c29c0  ins_upd_dlt: upd, initial: upd - 2026-11-04 18:03:00,542 - logic_logger - INFO

```
</details>

&nbsp;
&nbsp;

#### Scenario: Balance - ship and unship ✅ (0.04 s)
&emsp;  Scenario: Balance - ship and unship  
&emsp;&emsp;    Given a customer with credit limit 1000  
&emsp;&emsp;    And a product priced 10 with no suppliers  
&emsp;&emsp;    And an order is created with 5 of the product  
&emsp;&emsp;    When the order is shipped  
&emsp;&emsp;    Then the customer balance is 0  
&emsp;&emsp;    When the order is un-shipped  
&emsp;&emsp;    Then the customer balance is 50  

<details markdown>
<summary>Rules exercised and logic log (4 transactions)</summary>


&nbsp;
&nbsp;


**Rules Used** in Scenario: Balance - ship and unship
```
  Customer  
    1. Derive Customer.balance as Sum(Order.amount_total Where Rule.sum(derive=models.Customer.balance, as_sum_of=models.Order.amount_total, where=lambda row: row.date_shipped is None))  
  Order  
    2. RowEvent Order.send_row_to_kafka()  
    3. Derive Order.amount_total as Sum(Item.amount Where  - None)  
  Item  
    4. Derive Item.amount as Formula (1): Rule.formula(derive=models.Item.amount, as_expres [...]  
    5. RowEvent Item.set_item_unit_price_from_supplier()  
```
**Logic Log** in Scenario: Balance - ship and unship (4 transactions)
```
Logic Phase:		ROW LOGIC		(session=0x10c4c3460) (sqlalchemy before_flush)			 - 2026-11-04 18:03:00,566 - logic_logger - INFO
..Order[None] {Insert - client} id: None, notes: test 1793844180564, customer_id: 30, CreatedOn: None, date_shipped: None, amount_total: None  row: 0x10c521f50  session: 0x10c4c3460  ins_upd_dlt: ins, initial: ins - 2026-11-04 18:03:00,566 - logic_logger - INFO
..Order[None] {server aggregate_defaults: amount_total } id: None, notes: test 1793844180564, customer_id: 30, CreatedOn: None, date_shipped: None, amount_total: 0  row: 0x10c521f50  session: 0x10c4c3460  ins_upd_dlt: ins, initial: ins - 2026-11-04 18:03:00,566 - logic_logger - INFO
Logic Phase:		COMMIT LOGIC		(session=0x10c4c3460)   										 - 2026-11-04 18:03:00,567 - logic_logger - INFO
Logic Phase:		AFTER_FLUSH LOGIC	(session=0x10c4c3460)   										 - 2026-11-04 18:03:00,567 - logic_logger - INFO
..Order[29] {AfterFlush Event} id: 29, notes: test 1793844180564, customer_id: 30, CreatedOn: None, date_shipped: None, amount_total: 0  row: 0x10c521f50  session: 0x10c4c3460  ins_upd_dlt: ins, initial: ins - 2026-11-04 18:03:00,567 - logic_logger - INFO


Logic Phase:		ROW LOGIC		(session=0x10c4c3790) (sqlalchemy before_flush)			 - 2026-11-04 18:03:00,571 - logic_logger - INFO
..Item[None] {Insert - client} id: None, order_id: 29, product_id: 33, quantity: 5, amount: None, unit_price: None  row: 0x10c521ad0  session: 0x10c4c3790  ins_upd_dlt: ins, initial: ins - 2026-11-04 18:03:00,571 - logic_logger - INFO
..Item[None] {No suppliers for Test Product 1793844180560, using product unit_price} id: None, order_id: 29, product_id: 33, quantity: 5, amount: None, unit_price: None  row: 0x10c521ad0  session: 0x10c4c3790  ins_upd_dlt: ins, initial: ins - 2026-11-04 18:03:00,572 - logic_logger - INFO
..Item[None] {Formula amount} id: None, order_id: 29, product_id: 33, quantity: 5, amount: 50.0000000000, unit_price: 10.0000000000  row: 0x10c521ad0  session: 0x10c4c3790  ins_upd_dlt: ins, initial: ins - 2026-11-04 18:03:00,572 - logic_logger - INFO
....Order[29] {Update - Adjusting order: amount_total} id: 29, notes: test 1793844180564, customer_id: 30, CreatedOn: None, date_shipped: None, amount_total:  [0E-10-->] 50.0000000000  row: 0x10c64c7d0  session: 0x10c4c3790  ins_upd_dlt: upd, initial: upd - 2026-11-04 18:03:00,572 - logic_logger - INFO
......Customer[30] {Update - Adjusting customer: balance} id: 30, name: Test Customer 1793844180555, balance:  [0E-10-->] 50.0000000000, credit_limit: 1000.0000000000, email: None, email_opt_out: None  row: 0x10c64d5d0  session: 0x10c4c3790  ins_upd_dlt: upd, initial: upd - 2026-11-04 18:03:00,573 - logic_logger - INFO
Logic Phase:		COMMIT LOGIC		(session=0x10c4c3790)   										 - 2026-11-04 18:03:00,573 - logic_logger - INFO
Logic Phase:		AFTER_FLUSH LOGIC	(session=0x10c4c3790)   										 - 2026-11-04 18:03:00,573 - logic_logger - INFO
....Order[29] {AfterFlush Event} id: 29, notes: test 1793844180564, customer_id: 30, CreatedOn: None, date_shipped: None, amount_total:  [0E-10-->] 50.0000000000  row: 0x10c64c7d0  session: 0x10c4c3790  ins_upd_dlt: upd, initial: upd - 2026-11-04 18:03:00,574 - logic_logger - INFO


Logic Phase:		ROW LOGIC		(session=0x10c4c2140) (sqlalchemy before_flush)			 - 2026-11-04 18:03:00,578 - logic_logger - INFO
..Order[29] {Update - client} id: 29, notes: test 1793844180564, customer_id: 30, CreatedOn: None, date_shipped:  [None-->] 2026-11-04 00:00:00, amount_total: 50.0000000000  row: 0x10c64c2d0  session: 0x10c4c2140  ins_upd_dlt: upd, initial: upd - 2026-11-04 18:03:00,578 - logic_logger - INFO
....Customer[30] {Update - Adjusting customer: balance} id: 30, name: Test Customer 1793844180555, balance:  [50.0000000000-->] 0E-10, credit_limit: 1000.0000000000, email: None, email_opt_out: None  row: 0x10c64d950  session: 0x10c4c2140  ins_upd_dlt: upd, initial: upd - 2026-11-04 18:03:00,579 - logic_logger - INFO
Logic Phase:		COMMIT LOGIC		(session=0x10c4c2140)   										 - 2026-11-04 18:03:00,579 - logic_logger - INFO
Logic Phase:		AFTER_FLUSH LOGIC	(session=0x10c4c2140)   										 - 2026-11-04 18:03:00,579 - logic_logger - INFO
..Order[29] {AfterFlush Event} id: 29, notes: test 1793844180564, customer_id: 30, CreatedOn: None, date_shipped:  [None-->] 2026-11-04 00:00:00, amount_total: 50.0000000000  row: 0x10c64c2d0  session: 0x10c4c2140  ins_upd_dlt: upd, initial: upd - 2026-11-04 18:03:00,579 - logic_logger - INFO
..Order[29] {Sending Order to Kafka topic 'order_shipping' [Note: **Kafka not enabled** ]} id: 29, notes: test 1793844180564, customer_id: 30, CreatedOn: None, date_shipped:  [None-->] 2026-11-04 00:00:00, amount_total: 50.0000000000  row: 0x10c64c2d0  session: 0x10c4c2140  ins_upd_dlt: upd, initial: upd - 2026-11-04 18:03:00,580 - logic_logger - INFO


Logic Phase:		ROW LOGIC		(session=0x10c4c3ac0) (sqlalchemy before_flush)			 - 2026-11-04 18:03:00,588 - logic_logger - INFO
..Order[29] {Update - client} id: 29, notes: test 1793844180564, customer_id: 30, CreatedOn: None, date_shipped:  [2026-11-04-->] None, amount_total: 50.0000000000  row: 0x10c64d350  session: 0x10c4c3ac0  ins_upd_dlt: upd, initial: upd - 2026-11-04 18:03:00,588 - logic_logger - INFO
....Customer[30] {Update - Adjusting customer: balance} id: 30, name: Test Customer 1793844180555, balance:  [0E-10-->] 50.0000000000, credit_limit: 1000.0000000000, email: None, email_opt_out: None  row: 0x10c64dbd0  session: 0x10c4c3ac0  ins_upd_dlt: upd, initial: upd - 2026-11-04 18:03:00,589 - logic_logger - INFO
Logic Phase:		COMMIT LOGIC		(session=0x10c4c3ac0)   										 - 2026-11-04 18:03:00,589 - logic_logger - INFO
Logic Phase:		AFTER_FLUSH LOGIC	(session=0x10c4c3ac0)   										 - 2026-11-04 18:03:00,589 - logic_logger - INFO
..Order[29] {AfterFlush Event} id: 29, notes: test 1793844180564, customer_id: 30, CreatedOn: None, date_shipped:  [2026-11-04-->] None, amount_total: 50.0000000000  row: 0x10c64d350  session: 0x10c4c3ac0  ins_upd_dlt: upd, initial: upd - 2026-11-04 18:03:00,589 - logic_logger - INFO

```
</details>

&nbsp;
&nbsp;

#### Scenario: Balance - move order ✅ (0.04 s)
&emsp;  Scenario: Balance - move order  
&emsp;&emsp;    Given a customer with credit limit 1000  
&emsp;&emsp;    And a second customer with credit limit 1000  
&emsp;&emsp;    And a product priced 10 with no suppliers  
&emsp;&emsp;    And an order is created with 5 of the product  
&emsp;&emsp;    When the order is moved to the second customer  
&emsp;&emsp;    Then the customer balance is 0  
&emsp;&emsp;    And the second customer balance is 50  

<details markdown>
<summary>Rules exercised and logic log (3 transactions)</summary>


&nbsp;
&nbsp;


**Rules Used** in Scenario: Balance - move order
```
  Customer  
    1. Derive Customer.balance as Sum(Order.amount_total Where Rule.sum(derive=models.Customer.balance, as_sum_of=models.Order.amount_total, where=lambda row: row.date_shipped is None))  
  Order  
    2. RowEvent Order.send_row_to_kafka()  
    3. Derive Order.amount_total as Sum(Item.amount Where  - None)  
  Item  
    4. Derive Item.amount as Formula (1): Rule.formula(derive=models.Item.amount, as_expres [...]  
    5. RowEvent Item.set_item_unit_price_from_supplier()  
```
**Logic Log** in Scenario: Balance - move order (3 transactions)
```
Logic Phase:		ROW LOGIC		(session=0x10c4c3ce0) (sqlalchemy before_flush)			 - 2026-11-04 18:03:00,613 - logic_logger - INFO
..Order[None] {Insert - client} id: None, notes: test 1793844180611, customer_id: 31, CreatedOn: None, date_shipped: None, amount_total: None  row: 0x10c479b50  session: 0x10c4c3ce0  ins_upd_dlt: ins, initial: ins - 2026-11-04 18:03:00,613 - logic_logger - INFO
..Order[None] {server aggregate_defaults: amount_total } id: None, notes: test 1793844180611, customer_id: 31, CreatedOn: None, date_shipped: None, amount_total: 0  row: 0x10c479b50  session: 0x10c4c3ce0  ins_upd_dlt: ins, initial: ins - 2026-11-04 18:03:00,613 - logic_logger - INFO
Logic Phase:		COMMIT LOGIC		(session=0x10c4c3ce0)   										 - 2026-11-04 18:03:00,614 - logic_logger - INFO
Logic Phase:		AFTER_FLUSH LOGIC	(session=0x10c4c3ce0)   										 - 2026-11-04 18:03:00,615 - logic_logger - INFO
..Order[30] {AfterFlush Event} id: 30, notes: test 1793844180611, customer_id: 31, CreatedOn: None, date_shipped: None, amount_total: 0  row: 0x10c479b50  session: 0x10c4c3ce0  ins_upd_dlt: ins, initial: ins - 2026-11-04 18:03:00,615 - logic_logger - INFO


Logic Phase:		ROW LOGIC		(session=0x10c4c38a0) (sqlalchemy before_flush)			 - 2026-11-04 18:03:00,619 - logic_logger - INFO
..Item[None] {Insert - client} id: None, order_id: 30, product_id: 34, quantity: 5, amount: None, unit_price: None  row: 0x10c479750  session: 0x10c4c38a0  ins_upd_dlt: ins, initial: ins - 2026-11-04 18:03:00,619 - logic_logger - INFO
..Item[None] {No suppliers for Test Product 1793844180606, using product unit_price} id: None, order_id: 30, product_id: 34, quantity: 5, amount: None, unit_price: None  row: 0x10c479750  session: 0x10c4c38a0  ins_upd_dlt: ins, initial: ins - 2026-11-04 18:03:00,619 - logic_logger - INFO
..Item[None] {Formula amount} id: None, order_id: 30, product_id: 34, quantity: 5, amount: 50.0000000000, unit_price: 10.0000000000  row: 0x10c479750  session: 0x10c4c38a0  ins_upd_dlt: ins, initial: ins - 2026-11-04 18:03:00,620 - logic_logger - INFO
....Order[30] {Update - Adjusting order: amount_total} id: 30, notes: test 1793844180611, customer_id: 31, CreatedOn: None, date_shipped: None, amount_total:  [0E-10-->] 50.0000000000  row: 0x10c47add0  session: 0x10c4c38a0  ins_upd_dlt: upd, initial: upd - 2026-11-04 18:03:00,620 - logic_logger - INFO
......Customer[31] {Update - Adjusting customer: balance} id: 31, name: Test Customer 1793844180597, balance:  [0E-10-->] 50.0000000000, credit_limit: 1000.0000000000, email: None, email_opt_out: None  row: 0x10c5204d0  session: 0x10c4c38a0  ins_upd_dlt: upd, initial: upd - 2026-11-04 18:03:00,620 - logic_logger - INFO
Logic Phase:		COMMIT LOGIC		(session=0x10c4c38a0)   										 - 2026-11-04 18:03:00,620 - logic_logger - INFO
Logic Phase:		AFTER_FLUSH LOGIC	(session=0x10c4c38a0)   										 - 2026-11-04 18:03:00,621 - logic_logger - INFO
....Order[30] {AfterFlush Event} id: 30, notes: test 1793844180611, customer_id: 31, CreatedOn: None, date_shipped: None, amount_total:  [0E-10-->] 50.0000000000  row: 0x10c47add0  session: 0x10c4c38a0  ins_upd_dlt: upd, initial: upd - 2026-11-04 18:03:00,621 - logic_logger - INFO


Logic Phase:		ROW LOGIC		(session=0x10c4c39b0) (sqlalchemy before_flush)			 - 2026-11-04 18:03:00,626 - logic_logger - INFO
..Order[30] {Update - client} id: 30, notes: test 1793844180611, customer_id:  [31-->] 32, CreatedOn: None, date_shipped: None, amount_total: 50.0000000000  row: 0x10c4b7350  session: 0x10c4c39b0  ins_upd_dlt: upd, initial: upd - 2026-11-04 18:03:00,626 - logic_logger - INFO
....Customer[32] {Update - Adjusting customer: balance, balance} id: 32, name: Test Customer 1793844180601, balance:  [0E-10-->] 50.0000000000, credit_limit: 1000.0000000000, email: None, email_opt_out: None  row: 0x10c5221d0  session: 0x10c4c39b0  ins_upd_dlt: upd, initial: upd - 2026-11-04 18:03:00,627 - logic_logger - INFO
....Customer[31] {Update - Adjusting Old customer} id: 31, name: Test Customer 1793844180597, balance:  [50.0000000000-->] 0E-10, credit_limit: 1000.0000000000, email: None, email_opt_out: None  row: 0x10c5215d0  session: 0x10c4c39b0  ins_upd_dlt: upd, initial: upd - 2026-11-04 18:03:00,627 - logic_logger - INFO
Logic Phase:		COMMIT LOGIC		(session=0x10c4c39b0)   										 - 2026-11-04 18:03:00,627 - logic_logger - INFO
Logic Phase:		AFTER_FLUSH LOGIC	(session=0x10c4c39b0)   										 - 2026-11-04 18:03:00,628 - logic_logger - INFO
..Order[30] {AfterFlush Event} id: 30, notes: test 1793844180611, customer_id:  [31-->] 32, CreatedOn: None, date_shipped: None, amount_total: 50.0000000000  row: 0x10c4b7350  session: 0x10c4c39b0  ins_upd_dlt: upd, initial: upd - 2026-11-04 18:03:00,628 - logic_logger - INFO

```
</details>

&nbsp;
&nbsp;

#### Scenario: Balance - delete order ✅ (0.04 s)
&emsp;  Scenario: Balance - delete order  
&emsp;&emsp;    Given a customer with credit limit 1000  
&emsp;&emsp;    And a product priced 10 with no suppliers  
&emsp;&emsp;    And an order is created with 5 of the product  
&emsp;&emsp;    When the order and its item are deleted  
&emsp;&emsp;    Then the customer balance is 0  

<details markdown>
<summary>Rules exercised and logic log (4 transactions)</summary>


&nbsp;
&nbsp;


**Rules Used** in Scenario: Balance - delete order
```
  Customer  
    1. Derive Customer.balance as Sum(Order.amount_total Where Rule.sum(derive=models.Customer.balance, as_sum_of=models.Order.amount_total, where=lambda row: row.date_shipped is None))  
  Order  
    2. RowEvent Order.send_row_to_kafka()  
    3. Derive Order.amount_total as Sum(Item.amount Where  - None)  
  Item  
    4. Derive Item.amount as Formula (1): Rule.formula(derive=models.Item.amount, as_expres [...]  
    5. RowEvent Item.set_item_unit_price_from_supplier()  
```
**Logic Log** in Scenario: Balance - delete order (4 transactions)
```
Logic Phase:		ROW LOGIC		(session=0x10c4c3130) (sqlalchemy before_flush)			 - 2026-11-04 18:03:00,650 - logic_logger - INFO
..Order[None] {Insert - client} id: None, notes: test 1793844180649, customer_id: 33, CreatedOn: None, date_shipped: None, amount_total: None  row: 0x10c4b7bd0  session: 0x10c4c3130  ins_upd_dlt: ins, initial: ins - 2026-11-04 18:03:00,650 - logic_logger - INFO
..Order[None] {server aggregate_defaults: amount_total } id: None, notes: test 1793844180649, customer_id: 33, CreatedOn: None, date_shipped: None, amount_total: 0  row: 0x10c4b7bd0  session: 0x10c4c3130  ins_upd_dlt: ins, initial: ins - 2026-11-04 18:03:00,651 - logic_logger - INFO
Logic Phase:		COMMIT LOGIC		(session=0x10c4c3130)   										 - 2026-11-04 18:03:00,651 - logic_logger - INFO
Logic Phase:		AFTER_FLUSH LOGIC	(session=0x10c4c3130)   										 - 2026-11-04 18:03:00,652 - logic_logger - INFO
..Order[31] {AfterFlush Event} id: 31, notes: test 1793844180649, customer_id: 33, CreatedOn: None, date_shipped: None, amount_total: 0  row: 0x10c4b7bd0  session: 0x10c4c3130  ins_upd_dlt: ins, initial: ins - 2026-11-04 18:03:00,652 - logic_logger - INFO


Logic Phase:		ROW LOGIC		(session=0x10c4c3350) (sqlalchemy before_flush)			 - 2026-11-04 18:03:00,655 - logic_logger - INFO
..Item[None] {Insert - client} id: None, order_id: 31, product_id: 35, quantity: 5, amount: None, unit_price: None  row: 0x10c47b850  session: 0x10c4c3350  ins_upd_dlt: ins, initial: ins - 2026-11-04 18:03:00,655 - logic_logger - INFO
..Item[None] {No suppliers for Test Product 1793844180644, using product unit_price} id: None, order_id: 31, product_id: 35, quantity: 5, amount: None, unit_price: None  row: 0x10c47b850  session: 0x10c4c3350  ins_upd_dlt: ins, initial: ins - 2026-11-04 18:03:00,656 - logic_logger - INFO
..Item[None] {Formula amount} id: None, order_id: 31, product_id: 35, quantity: 5, amount: 50.0000000000, unit_price: 10.0000000000  row: 0x10c47b850  session: 0x10c4c3350  ins_upd_dlt: ins, initial: ins - 2026-11-04 18:03:00,656 - logic_logger - INFO
....Order[31] {Update - Adjusting order: amount_total} id: 31, notes: test 1793844180649, customer_id: 33, CreatedOn: None, date_shipped: None, amount_total:  [0E-10-->] 50.0000000000  row: 0x10c520a50  session: 0x10c4c3350  ins_upd_dlt: upd, initial: upd - 2026-11-04 18:03:00,656 - logic_logger - INFO
......Customer[33] {Update - Adjusting customer: balance} id: 33, name: Test Customer 1793844180639, balance:  [0E-10-->] 50.0000000000, credit_limit: 1000.0000000000, email: None, email_opt_out: None  row: 0x10c520850  session: 0x10c4c3350  ins_upd_dlt: upd, initial: upd - 2026-11-04 18:03:00,656 - logic_logger - INFO
Logic Phase:		COMMIT LOGIC		(session=0x10c4c3350)   										 - 2026-11-04 18:03:00,657 - logic_logger - INFO
Logic Phase:		AFTER_FLUSH LOGIC	(session=0x10c4c3350)   										 - 2026-11-04 18:03:00,657 - logic_logger - INFO
....Order[31] {AfterFlush Event} id: 31, notes: test 1793844180649, customer_id: 33, CreatedOn: None, date_shipped: None, amount_total:  [0E-10-->] 50.0000000000  row: 0x10c520a50  session: 0x10c4c3350  ins_upd_dlt: upd, initial: upd - 2026-11-04 18:03:00,657 - logic_logger - INFO


Logic Phase:		ROW LOGIC		(session=0x10c4c2cf0) (sqlalchemy before_flush)			 - 2026-11-04 18:03:00,662 - logic_logger - INFO
..Item[30] {Delete - client} id: 30, order_id: 31, product_id: 35, quantity: 5, amount: 50.0000000000, unit_price: 10.0000000000  row: 0x10c521c50  session: 0x10c4c2cf0  ins_upd_dlt: dlt, initial: dlt - 2026-11-04 18:03:00,662 - logic_logger - INFO
....Order[31] {Update - Adjusting order: amount_total} id: 31, notes: test 1793844180649, customer_id: 33, CreatedOn: None, date_shipped: None, amount_total:  [50.0000000000-->] 0E-10  row: 0x10c521e50  session: 0x10c4c2cf0  ins_upd_dlt: upd, initial: upd - 2026-11-04 18:03:00,662 - logic_logger - INFO
......Customer[33] {Update - Adjusting customer: balance} id: 33, name: Test Customer 1793844180639, balance:  [50.0000000000-->] 0E-10, credit_limit: 1000.0000000000, email: None, email_opt_out: None  row: 0x10c64d7d0  session: 0x10c4c2cf0  ins_upd_dlt: upd, initial: upd - 2026-11-04 18:03:00,663 - logic_logger - INFO
Logic Phase:		COMMIT LOGIC		(session=0x10c4c2cf0)   										 - 2026-11-04 18:03:00,663 - logic_logger - INFO
Logic Phase:		AFTER_FLUSH LOGIC	(session=0x10c4c2cf0)   										 - 2026-11-04 18:03:00,664 - logic_logger - INFO
....Order[31] {AfterFlush Event} id: 31, notes: test 1793844180649, customer_id: 33, CreatedOn: None, date_shipped: None, amount_total:  [50.0000000000-->] 0E-10  row: 0x10c521e50  session: 0x10c4c2cf0  ins_upd_dlt: upd, initial: upd - 2026-11-04 18:03:00,664 - logic_logger - INFO


Logic Phase:		ROW LOGIC		(session=0x10c4c2ad0) (sqlalchemy before_flush)			 - 2026-11-04 18:03:00,668 - logic_logger - INFO
..Order[31] {Delete - client} id: 31, notes: test 1793844180649, customer_id: 33, CreatedOn: None, date_shipped: None, amount_total: 0E-10  row: 0x10c520bd0  session: 0x10c4c2ad0  ins_upd_dlt: dlt, initial: dlt - 2026-11-04 18:03:00,668 - logic_logger - INFO
Logic Phase:		COMMIT LOGIC		(session=0x10c4c2ad0)   										 - 2026-11-04 18:03:00,668 - logic_logger - INFO
Logic Phase:		AFTER_FLUSH LOGIC	(session=0x10c4c2ad0)   										 - 2026-11-04 18:03:00,669 - logic_logger - INFO
..Order[31] {AfterFlush Event} id: 31, notes: test 1793844180649, customer_id: 33, CreatedOn: None, date_shipped: None, amount_total: 0E-10  row: 0x10c520bd0  session: 0x10c4c2ad0  ins_upd_dlt: dlt, initial: dlt - 2026-11-04 18:03:00,669 - logic_logger - INFO

```
</details>

&nbsp;
&nbsp;

#### Scenario: Item - change quantity ✅ (0.04 s)
&emsp;  Scenario: Item - change quantity  
&emsp;&emsp;    Given a customer with credit limit 1000  
&emsp;&emsp;    And a product priced 10 with no suppliers  
&emsp;&emsp;    And an order is created with 5 of the product  
&emsp;&emsp;    When the item quantity is changed to 8  
&emsp;&emsp;    Then the item amount is 80  
&emsp;&emsp;    And the order amount total is 80  
&emsp;&emsp;    And the customer balance is 80  

<details markdown>
<summary>Rules exercised and logic log (3 transactions)</summary>


&nbsp;
&nbsp;


**Rules Used** in Scenario: Item - change quantity
```
  Customer  
    1. Derive Customer.balance as Sum(Order.amount_total Where Rule.sum(derive=models.Customer.balance, as_sum_of=models.Order.amount_total, where=lambda row: row.date_shipped is None))  
  Order  
    2. RowEvent Order.send_row_to_kafka()  
    3. Derive Order.amount_total as Sum(Item.amount Where  - None)  
  Item  
    4. Derive Item.amount as Formula (1): Rule.formula(derive=models.Item.amount, as_expres [...]  
    5. RowEvent Item.set_item_unit_price_from_supplier()  
```
**Logic Log** in Scenario: Item - change quantity (3 transactions)
```
Logic Phase:		ROW LOGIC		(session=0x10c4c2250) (sqlalchemy before_flush)			 - 2026-11-04 18:03:00,686 - logic_logger - INFO
..Order[None] {Insert - client} id: None, notes: test 1793844180684, customer_id: 34, CreatedOn: None, date_shipped: None, amount_total: None  row: 0x10c521650  session: 0x10c4c2250  ins_upd_dlt: ins, initial: ins - 2026-11-04 18:03:00,686 - logic_logger - INFO
..Order[None] {server aggregate_defaults: amount_total } id: None, notes: test 1793844180684, customer_id: 34, CreatedOn: None, date_shipped: None, amount_total: 0  row: 0x10c521650  session: 0x10c4c2250  ins_upd_dlt: ins, initial: ins - 2026-11-04 18:03:00,686 - logic_logger - INFO
Logic Phase:		COMMIT LOGIC		(session=0x10c4c2250)   										 - 2026-11-04 18:03:00,687 - logic_logger - INFO
Logic Phase:		AFTER_FLUSH LOGIC	(session=0x10c4c2250)   										 - 2026-11-04 18:03:00,687 - logic_logger - INFO
..Order[32] {AfterFlush Event} id: 32, notes: test 1793844180684, customer_id: 34, CreatedOn: None, date_shipped: None, amount_total: 0  row: 0x10c521650  session: 0x10c4c2250  ins_upd_dlt: ins, initial: ins - 2026-11-04 18:03:00,687 - logic_logger - INFO


Logic Phase:		ROW LOGIC		(session=0x10c4c2030) (sqlalchemy before_flush)			 - 2026-11-04 18:03:00,691 - logic_logger - INFO
..Item[None] {Insert - client} id: None, order_id: 32, product_id: 36, quantity: 5, amount: None, unit_price: None  row: 0x10c521250  session: 0x10c4c2030  ins_upd_dlt: ins, initial: ins - 2026-11-04 18:03:00,691 - logic_logger - INFO
..Item[None] {No suppliers for Test Product 1793844180680, using product unit_price} id: None, order_id: 32, product_id: 36, quantity: 5, amount: None, unit_price: None  row: 0x10c521250  session: 0x10c4c2030  ins_upd_dlt: ins, initial: ins - 2026-11-04 18:03:00,692 - logic_logger - INFO
..Item[None] {Formula amount} id: None, order_id: 32, product_id: 36, quantity: 5, amount: 50.0000000000, unit_price: 10.0000000000  row: 0x10c521250  session: 0x10c4c2030  ins_upd_dlt: ins, initial: ins - 2026-11-04 18:03:00,692 - logic_logger - INFO
....Order[32] {Update - Adjusting order: amount_total} id: 32, notes: test 1793844180684, customer_id: 34, CreatedOn: None, date_shipped: None, amount_total:  [0E-10-->] 50.0000000000  row: 0x10c64c750  session: 0x10c4c2030  ins_upd_dlt: upd, initial: upd - 2026-11-04 18:03:00,692 - logic_logger - INFO
......Customer[34] {Update - Adjusting customer: balance} id: 34, name: Test Customer 1793844180675, balance:  [0E-10-->] 50.0000000000, credit_limit: 1000.0000000000, email: None, email_opt_out: None  row: 0x10c64e2d0  session: 0x10c4c2030  ins_upd_dlt: upd, initial: upd - 2026-11-04 18:03:00,692 - logic_logger - INFO
Logic Phase:		COMMIT LOGIC		(session=0x10c4c2030)   										 - 2026-11-04 18:03:00,693 - logic_logger - INFO
Logic Phase:		AFTER_FLUSH LOGIC	(session=0x10c4c2030)   										 - 2026-11-04 18:03:00,694 - logic_logger - INFO
....Order[32] {AfterFlush Event} id: 32, notes: test 1793844180684, customer_id: 34, CreatedOn: None, date_shipped: None, amount_total:  [0E-10-->] 50.0000000000  row: 0x10c64c750  session: 0x10c4c2030  ins_upd_dlt: upd, initial: upd - 2026-11-04 18:03:00,694 - logic_logger - INFO


Logic Phase:		ROW LOGIC		(session=0x10c3d3bd0) (sqlalchemy before_flush)			 - 2026-11-04 18:03:00,699 - logic_logger - INFO
..Item[31] {Update - client} id: 31, order_id: 32, product_id: 36, quantity:  [5-->] 8, amount: 50.0000000000, unit_price: 10.0000000000  row: 0x10c520750  session: 0x10c3d3bd0  ins_upd_dlt: upd, initial: upd - 2026-11-04 18:03:00,699 - logic_logger - INFO
..Item[31] {Formula amount} id: 31, order_id: 32, product_id: 36, quantity:  [5-->] 8, amount:  [50.0000000000-->] 80.0000000000, unit_price: 10.0000000000  row: 0x10c520750  session: 0x10c3d3bd0  ins_upd_dlt: upd, initial: upd - 2026-11-04 18:03:00,699 - logic_logger - INFO
....Order[32] {Update - Adjusting order: amount_total} id: 32, notes: test 1793844180684, customer_id: 34, CreatedOn: None, date_shipped: None, amount_total:  [50.0000000000-->] 80.0000000000  row: 0x10c4b7dd0  session: 0x10c3d3bd0  ins_upd_dlt: upd, initial: upd - 2026-11-04 18:03:00,699 - logic_logger - INFO
......Customer[34] {Update - Adjusting customer: balance} id: 34, name: Test Customer 1793844180675, balance:  [50.0000000000-->] 80.0000000000, credit_limit: 1000.0000000000, email: None, email_opt_out: None  row: 0x10c4b7e50  session: 0x10c3d3bd0  ins_upd_dlt: upd, initial: upd - 2026-11-04 18:03:00,700 - logic_logger - INFO
Logic Phase:		COMMIT LOGIC		(session=0x10c3d3bd0)   										 - 2026-11-04 18:03:00,700 - logic_logger - INFO
Logic Phase:		AFTER_FLUSH LOGIC	(session=0x10c3d3bd0)   										 - 2026-11-04 18:03:00,701 - logic_logger - INFO
....Order[32] {AfterFlush Event} id: 32, notes: test 1793844180684, customer_id: 34, CreatedOn: None, date_shipped: None, amount_total:  [50.0000000000-->] 80.0000000000  row: 0x10c4b7dd0  session: 0x10c3d3bd0  ins_upd_dlt: upd, initial: upd - 2026-11-04 18:03:00,701 - logic_logger - INFO

```
</details>

&nbsp;
&nbsp;

#### Scenario: Item - delete ✅ (0.04 s)
&emsp;  Scenario: Item - delete  
&emsp;&emsp;    Given a customer with credit limit 1000  
&emsp;&emsp;    And a product priced 10 with no suppliers  
&emsp;&emsp;    And an order is created with 5 of the product  
&emsp;&emsp;    And a second item is added with 2 of the product  
&emsp;&emsp;    When the item is deleted  
&emsp;&emsp;    Then the order amount total is 20  
&emsp;&emsp;    And the customer balance is 20  

<details markdown>
<summary>Rules exercised and logic log (4 transactions)</summary>


&nbsp;
&nbsp;


**Rules Used** in Scenario: Item - delete
```
  Customer  
    1. Derive Customer.balance as Sum(Order.amount_total Where Rule.sum(derive=models.Customer.balance, as_sum_of=models.Order.amount_total, where=lambda row: row.date_shipped is None))  
  Order  
    2. RowEvent Order.send_row_to_kafka()  
    3. Derive Order.amount_total as Sum(Item.amount Where  - None)  
  Item  
    4. Derive Item.amount as Formula (1): Rule.formula(derive=models.Item.amount, as_expres [...]  
    5. RowEvent Item.set_item_unit_price_from_supplier()  
```
**Logic Log** in Scenario: Item - delete (4 transactions)
```
Logic Phase:		ROW LOGIC		(session=0x10c4c2690) (sqlalchemy before_flush)			 - 2026-11-04 18:03:00,728 - logic_logger - INFO
..Order[None] {Insert - client} id: None, notes: test 1793844180726, customer_id: 35, CreatedOn: None, date_shipped: None, amount_total: None  row: 0x10c5216d0  session: 0x10c4c2690  ins_upd_dlt: ins, initial: ins - 2026-11-04 18:03:00,728 - logic_logger - INFO
..Order[None] {server aggregate_defaults: amount_total } id: None, notes: test 1793844180726, customer_id: 35, CreatedOn: None, date_shipped: None, amount_total: 0  row: 0x10c5216d0  session: 0x10c4c2690  ins_upd_dlt: ins, initial: ins - 2026-11-04 18:03:00,729 - logic_logger - INFO
Logic Phase:		COMMIT LOGIC		(session=0x10c4c2690)   										 - 2026-11-04 18:03:00,729 - logic_logger - INFO
Logic Phase:		AFTER_FLUSH LOGIC	(session=0x10c4c2690)   										 - 2026-11-04 18:03:00,730 - logic_logger - INFO
..Order[33] {AfterFlush Event} id: 33, notes: test 1793844180726, customer_id: 35, CreatedOn: None, date_shipped: None, amount_total: 0  row: 0x10c5216d0  session: 0x10c4c2690  ins_upd_dlt: ins, initial: ins - 2026-11-04 18:03:00,730 - logic_logger - INFO


Logic Phase:		ROW LOGIC		(session=0x10c4c2ad0) (sqlalchemy before_flush)			 - 2026-11-04 18:03:00,734 - logic_logger - INFO
..Item[None] {Insert - client} id: None, order_id: 33, product_id: 37, quantity: 5, amount: None, unit_price: None  row: 0x10c521a50  session: 0x10c4c2ad0  ins_upd_dlt: ins, initial: ins - 2026-11-04 18:03:00,734 - logic_logger - INFO
..Item[None] {No suppliers for Test Product 1793844180722, using product unit_price} id: None, order_id: 33, product_id: 37, quantity: 5, amount: None, unit_price: None  row: 0x10c521a50  session: 0x10c4c2ad0  ins_upd_dlt: ins, initial: ins - 2026-11-04 18:03:00,735 - logic_logger - INFO
..Item[None] {Formula amount} id: None, order_id: 33, product_id: 37, quantity: 5, amount: 50.0000000000, unit_price: 10.0000000000  row: 0x10c521a50  session: 0x10c4c2ad0  ins_upd_dlt: ins, initial: ins - 2026-11-04 18:03:00,735 - logic_logger - INFO
....Order[33] {Update - Adjusting order: amount_total} id: 33, notes: test 1793844180726, customer_id: 35, CreatedOn: None, date_shipped: None, amount_total:  [0E-10-->] 50.0000000000  row: 0x10c5220d0  session: 0x10c4c2ad0  ins_upd_dlt: upd, initial: upd - 2026-11-04 18:03:00,735 - logic_logger - INFO
......Customer[35] {Update - Adjusting customer: balance} id: 35, name: Test Customer 1793844180716, balance:  [0E-10-->] 50.0000000000, credit_limit: 1000.0000000000, email: None, email_opt_out: None  row: 0x10c64cdd0  session: 0x10c4c2ad0  ins_upd_dlt: upd, initial: upd - 2026-11-04 18:03:00,735 - logic_logger - INFO
Logic Phase:		COMMIT LOGIC		(session=0x10c4c2ad0)   										 - 2026-11-04 18:03:00,736 - logic_logger - INFO
Logic Phase:		AFTER_FLUSH LOGIC	(session=0x10c4c2ad0)   										 - 2026-11-04 18:03:00,736 - logic_logger - INFO
....Order[33] {AfterFlush Event} id: 33, notes: test 1793844180726, customer_id: 35, CreatedOn: None, date_shipped: None, amount_total:  [0E-10-->] 50.0000000000  row: 0x10c5220d0  session: 0x10c4c2ad0  ins_upd_dlt: upd, initial: upd - 2026-11-04 18:03:00,736 - logic_logger - INFO


Logic Phase:		ROW LOGIC		(session=0x10c4c2cf0) (sqlalchemy before_flush)			 - 2026-11-04 18:03:00,741 - logic_logger - INFO
..Item[None] {Insert - client} id: None, order_id: 33, product_id: 37, quantity: 2, amount: None, unit_price: None  row: 0x10c47b850  session: 0x10c4c2cf0  ins_upd_dlt: ins, initial: ins - 2026-11-04 18:03:00,741 - logic_logger - INFO
..Item[None] {No suppliers for Test Product 1793844180722, using product unit_price} id: None, order_id: 33, product_id: 37, quantity: 2, amount: None, unit_price: None  row: 0x10c47b850  session: 0x10c4c2cf0  ins_upd_dlt: ins, initial: ins - 2026-11-04 18:03:00,742 - logic_logger - INFO
..Item[None] {Formula amount} id: None, order_id: 33, product_id: 37, quantity: 2, amount: 20.0000000000, unit_price: 10.0000000000  row: 0x10c47b850  session: 0x10c4c2cf0  ins_upd_dlt: ins, initial: ins - 2026-11-04 18:03:00,742 - logic_logger - INFO
....Order[33] {Update - Adjusting order: amount_total} id: 33, notes: test 1793844180726, customer_id: 35, CreatedOn: None, date_shipped: None, amount_total:  [50.0000000000-->] 70.0000000000  row: 0x10c521e50  session: 0x10c4c2cf0  ins_upd_dlt: upd, initial: upd - 2026-11-04 18:03:00,742 - logic_logger - INFO
......Customer[35] {Update - Adjusting customer: balance} id: 35, name: Test Customer 1793844180716, balance:  [50.0000000000-->] 70.0000000000, credit_limit: 1000.0000000000, email: None, email_opt_out: None  row: 0x10c64cbd0  session: 0x10c4c2cf0  ins_upd_dlt: upd, initial: upd - 2026-11-04 18:03:00,743 - logic_logger - INFO
Logic Phase:		COMMIT LOGIC		(session=0x10c4c2cf0)   										 - 2026-11-04 18:03:00,743 - logic_logger - INFO
Logic Phase:		AFTER_FLUSH LOGIC	(session=0x10c4c2cf0)   										 - 2026-11-04 18:03:00,744 - logic_logger - INFO
....Order[33] {AfterFlush Event} id: 33, notes: test 1793844180726, customer_id: 35, CreatedOn: None, date_shipped: None, amount_total:  [50.0000000000-->] 70.0000000000  row: 0x10c521e50  session: 0x10c4c2cf0  ins_upd_dlt: upd, initial: upd - 2026-11-04 18:03:00,744 - logic_logger - INFO


Logic Phase:		ROW LOGIC		(session=0x10c4c2f10) (sqlalchemy before_flush)			 - 2026-11-04 18:03:00,749 - logic_logger - INFO
..Item[32] {Delete - client} id: 32, order_id: 33, product_id: 37, quantity: 5, amount: 50.0000000000, unit_price: 10.0000000000  row: 0x10c4b7c50  session: 0x10c4c2f10  ins_upd_dlt: dlt, initial: dlt - 2026-11-04 18:03:00,749 - logic_logger - INFO
....Order[33] {Update - Adjusting order: amount_total} id: 33, notes: test 1793844180726, customer_id: 35, CreatedOn: None, date_shipped: None, amount_total:  [70.0000000000-->] 20.0000000000  row: 0x10c64c9d0  session: 0x10c4c2f10  ins_upd_dlt: upd, initial: upd - 2026-11-04 18:03:00,749 - logic_logger - INFO
......Customer[35] {Update - Adjusting customer: balance} id: 35, name: Test Customer 1793844180716, balance:  [70.0000000000-->] 20.0000000000, credit_limit: 1000.0000000000, email: None, email_opt_out: None  row: 0x10c64d750  session: 0x10c4c2f10  ins_upd_dlt: upd, initial: upd - 2026-11-04 18:03:00,749 - logic_logger - INFO
Logic Phase:		COMMIT LOGIC		(session=0x10c4c2f10)   										 - 2026-11-04 18:03:00,750 - logic_logger - INFO
Logic Phase:		AFTER_FLUSH LOGIC	(session=0x10c4c2f10)   										 - 2026-11-04 18:03:00,751 - logic_logger - INFO
....Order[33] {AfterFlush Event} id: 33, notes: test 1793844180726, customer_id: 35, CreatedOn: None, date_shipped: None, amount_total:  [70.0000000000-->] 20.0000000000  row: 0x10c64c9d0  session: 0x10c4c2f10  ins_upd_dlt: upd, initial: upd - 2026-11-04 18:03:00,751 - logic_logger - INFO

```
</details>

&nbsp;
&nbsp;

#### Scenario: Item - move to order ✅ (0.05 s)
&emsp;  Scenario: Item - move to order  
&emsp;&emsp;    Given a customer with credit limit 1000  
&emsp;&emsp;    And a product priced 10 with no suppliers  
&emsp;&emsp;    And an order is created with 5 of the product  
&emsp;&emsp;    And a second order is created with 2 of the product  
&emsp;&emsp;    When the item is moved to the second order  
&emsp;&emsp;    Then the order amount total is 0  
&emsp;&emsp;    And the second order amount total is 70  
&emsp;&emsp;    And the customer balance is 70  

<details markdown>
<summary>Rules exercised and logic log (5 transactions)</summary>


&nbsp;
&nbsp;


**Rules Used** in Scenario: Item - move to order
```
  Customer  
    1. Derive Customer.balance as Sum(Order.amount_total Where Rule.sum(derive=models.Customer.balance, as_sum_of=models.Order.amount_total, where=lambda row: row.date_shipped is None))  
  Order  
    2. RowEvent Order.send_row_to_kafka()  
    3. Derive Order.amount_total as Sum(Item.amount Where  - None)  
  Item  
    4. Derive Item.amount as Formula (1): Rule.formula(derive=models.Item.amount, as_expres [...]  
    5. RowEvent Item.set_item_unit_price_from_supplier()  
```
**Logic Log** in Scenario: Item - move to order (5 transactions)
```
Logic Phase:		ROW LOGIC		(session=0x10c4c3680) (sqlalchemy before_flush)			 - 2026-11-04 18:03:00,770 - logic_logger - INFO
..Order[None] {Insert - client} id: None, notes: test 1793844180768, customer_id: 36, CreatedOn: None, date_shipped: None, amount_total: None  row: 0x10c5206d0  session: 0x10c4c3680  ins_upd_dlt: ins, initial: ins - 2026-11-04 18:03:00,770 - logic_logger - INFO
..Order[None] {server aggregate_defaults: amount_total } id: None, notes: test 1793844180768, customer_id: 36, CreatedOn: None, date_shipped: None, amount_total: 0  row: 0x10c5206d0  session: 0x10c4c3680  ins_upd_dlt: ins, initial: ins - 2026-11-04 18:03:00,770 - logic_logger - INFO
Logic Phase:		COMMIT LOGIC		(session=0x10c4c3680)   										 - 2026-11-04 18:03:00,771 - logic_logger - INFO
Logic Phase:		AFTER_FLUSH LOGIC	(session=0x10c4c3680)   										 - 2026-11-04 18:03:00,771 - logic_logger - INFO
..Order[34] {AfterFlush Event} id: 34, notes: test 1793844180768, customer_id: 36, CreatedOn: None, date_shipped: None, amount_total: 0  row: 0x10c5206d0  session: 0x10c4c3680  ins_upd_dlt: ins, initial: ins - 2026-11-04 18:03:00,771 - logic_logger - INFO


Logic Phase:		ROW LOGIC		(session=0x10c4c2140) (sqlalchemy before_flush)			 - 2026-11-04 18:03:00,775 - logic_logger - INFO
..Item[None] {Insert - client} id: None, order_id: 34, product_id: 38, quantity: 5, amount: None, unit_price: None  row: 0x10c4b75d0  session: 0x10c4c2140  ins_upd_dlt: ins, initial: ins - 2026-11-04 18:03:00,775 - logic_logger - INFO
..Item[None] {No suppliers for Test Product 1793844180764, using product unit_price} id: None, order_id: 34, product_id: 38, quantity: 5, amount: None, unit_price: None  row: 0x10c4b75d0  session: 0x10c4c2140  ins_upd_dlt: ins, initial: ins - 2026-11-04 18:03:00,775 - logic_logger - INFO
..Item[None] {Formula amount} id: None, order_id: 34, product_id: 38, quantity: 5, amount: 50.0000000000, unit_price: 10.0000000000  row: 0x10c4b75d0  session: 0x10c4c2140  ins_upd_dlt: ins, initial: ins - 2026-11-04 18:03:00,775 - logic_logger - INFO
....Order[34] {Update - Adjusting order: amount_total} id: 34, notes: test 1793844180768, customer_id: 36, CreatedOn: None, date_shipped: None, amount_total:  [0E-10-->] 50.0000000000  row: 0x10c64ddd0  session: 0x10c4c2140  ins_upd_dlt: upd, initial: upd - 2026-11-04 18:03:00,776 - logic_logger - INFO
......Customer[36] {Update - Adjusting customer: balance} id: 36, name: Test Customer 1793844180759, balance:  [0E-10-->] 50.0000000000, credit_limit: 1000.0000000000, email: None, email_opt_out: None  row: 0x10c64e3d0  session: 0x10c4c2140  ins_upd_dlt: upd, initial: upd - 2026-11-04 18:03:00,776 - logic_logger - INFO
Logic Phase:		COMMIT LOGIC		(session=0x10c4c2140)   										 - 2026-11-04 18:03:00,776 - logic_logger - INFO
Logic Phase:		AFTER_FLUSH LOGIC	(session=0x10c4c2140)   										 - 2026-11-04 18:03:00,777 - logic_logger - INFO
....Order[34] {AfterFlush Event} id: 34, notes: test 1793844180768, customer_id: 36, CreatedOn: None, date_shipped: None, amount_total:  [0E-10-->] 50.0000000000  row: 0x10c64ddd0  session: 0x10c4c2140  ins_upd_dlt: upd, initial: upd - 2026-11-04 18:03:00,777 - logic_logger - INFO


Logic Phase:		ROW LOGIC		(session=0x10c4c3ac0) (sqlalchemy before_flush)			 - 2026-11-04 18:03:00,783 - logic_logger - INFO
..Order[None] {Insert - client} id: None, notes: test 1793844180780, customer_id: 36, CreatedOn: None, date_shipped: None, amount_total: None  row: 0x10c5207d0  session: 0x10c4c3ac0  ins_upd_dlt: ins, initial: ins - 2026-11-04 18:03:00,783 - logic_logger - INFO
..Order[None] {server aggregate_defaults: amount_total } id: None, notes: test 1793844180780, customer_id: 36, CreatedOn: None, date_shipped: None, amount_total: 0  row: 0x10c5207d0  session: 0x10c4c3ac0  ins_upd_dlt: ins, initial: ins - 2026-11-04 18:03:00,783 - logic_logger - INFO
Logic Phase:		COMMIT LOGIC		(session=0x10c4c3ac0)   										 - 2026-11-04 18:03:00,784 - logic_logger - INFO
Logic Phase:		AFTER_FLUSH LOGIC	(session=0x10c4c3ac0)   										 - 2026-11-04 18:03:00,784 - logic_logger - INFO
..Order[35] {AfterFlush Event} id: 35, notes: test 1793844180780, customer_id: 36, CreatedOn: None, date_shipped: None, amount_total: 0  row: 0x10c5207d0  session: 0x10c4c3ac0  ins_upd_dlt: ins, initial: ins - 2026-11-04 18:03:00,784 - logic_logger - INFO


Logic Phase:		ROW LOGIC		(session=0x10c4c3bd0) (sqlalchemy before_flush)			 - 2026-11-04 18:03:00,789 - logic_logger - INFO
..Item[None] {Insert - client} id: None, order_id: 35, product_id: 38, quantity: 2, amount: None, unit_price: None  row: 0x10c4b4fd0  session: 0x10c4c3bd0  ins_upd_dlt: ins, initial: ins - 2026-11-04 18:03:00,789 - logic_logger - INFO
..Item[None] {No suppliers for Test Product 1793844180764, using product unit_price} id: None, order_id: 35, product_id: 38, quantity: 2, amount: None, unit_price: None  row: 0x10c4b4fd0  session: 0x10c4c3bd0  ins_upd_dlt: ins, initial: ins - 2026-11-04 18:03:00,790 - logic_logger - INFO
..Item[None] {Formula amount} id: None, order_id: 35, product_id: 38, quantity: 2, amount: 20.0000000000, unit_price: 10.0000000000  row: 0x10c4b4fd0  session: 0x10c4c3bd0  ins_upd_dlt: ins, initial: ins - 2026-11-04 18:03:00,790 - logic_logger - INFO
....Order[35] {Update - Adjusting order: amount_total} id: 35, notes: test 1793844180780, customer_id: 36, CreatedOn: None, date_shipped: None, amount_total:  [0E-10-->] 20.0000000000  row: 0x10c64cb50  session: 0x10c4c3bd0  ins_upd_dlt: upd, initial: upd - 2026-11-04 18:03:00,790 - logic_logger - INFO
......Customer[36] {Update - Adjusting customer: balance} id: 36, name: Test Customer 1793844180759, balance:  [50.0000000000-->] 70.0000000000, credit_limit: 1000.0000000000, email: None, email_opt_out: None  row: 0x10c64e950  session: 0x10c4c3bd0  ins_upd_dlt: upd, initial: upd - 2026-11-04 18:03:00,790 - logic_logger - INFO
Logic Phase:		COMMIT LOGIC		(session=0x10c4c3bd0)   										 - 2026-11-04 18:03:00,790 - logic_logger - INFO
Logic Phase:		AFTER_FLUSH LOGIC	(session=0x10c4c3bd0)   										 - 2026-11-04 18:03:00,791 - logic_logger - INFO
....Order[35] {AfterFlush Event} id: 35, notes: test 1793844180780, customer_id: 36, CreatedOn: None, date_shipped: None, amount_total:  [0E-10-->] 20.0000000000  row: 0x10c64cb50  session: 0x10c4c3bd0  ins_upd_dlt: upd, initial: upd - 2026-11-04 18:03:00,791 - logic_logger - INFO


Logic Phase:		ROW LOGIC		(session=0x10c4c1e10) (sqlalchemy before_flush)			 - 2026-11-04 18:03:00,797 - logic_logger - INFO
..Item[34] {Update - client} id: 34, order_id:  [34-->] 35, product_id: 38, quantity: 5, amount: 50.0000000000, unit_price: 10.0000000000  row: 0x10c64d450  session: 0x10c4c1e10  ins_upd_dlt: upd, initial: upd - 2026-11-04 18:03:00,797 - logic_logger - INFO
..Item[34] {Prune Formula: amount [['quantity', 'unit_price']]} id: 34, order_id:  [34-->] 35, product_id: 38, quantity: 5, amount: 50.0000000000, unit_price: 10.0000000000  row: 0x10c64d450  session: 0x10c4c1e10  ins_upd_dlt: upd, initial: upd - 2026-11-04 18:03:00,797 - logic_logger - INFO
....Order[35] {Update - Adjusting order: amount_total, amount_total} id: 35, notes: test 1793844180780, customer_id: 36, CreatedOn: None, date_shipped: None, amount_total:  [20.0000000000-->] 70.0000000000  row: 0x10c64d0d0  session: 0x10c4c1e10  ins_upd_dlt: upd, initial: upd - 2026-11-04 18:03:00,798 - logic_logger - INFO
......Customer[36] {Update - Adjusting customer: balance} id: 36, name: Test Customer 1793844180759, balance:  [70.0000000000-->] 120.0000000000, credit_limit: 1000.0000000000, email: None, email_opt_out: None  row: 0x10c64f250  session: 0x10c4c1e10  ins_upd_dlt: upd, initial: upd - 2026-11-04 18:03:00,798 - logic_logger - INFO
....Order[34] {Update - Adjusting Old order} id: 34, notes: test 1793844180768, customer_id: 36, CreatedOn: None, date_shipped: None, amount_total:  [50.0000000000-->] 0E-10  row: 0x10c64dcd0  session: 0x10c4c1e10  ins_upd_dlt: upd, initial: upd - 2026-11-04 18:03:00,798 - logic_logger - INFO
......Customer[36] {Update - Adjusting customer: balance} id: 36, name: Test Customer 1793844180759, balance:  [120.0000000000-->] 70.0000000000, credit_limit: 1000.0000000000, email: None, email_opt_out: None  row: 0x10c64f250  session: 0x10c4c1e10  ins_upd_dlt: upd, initial: upd - 2026-11-04 18:03:00,798 - logic_logger - INFO
Logic Phase:		COMMIT LOGIC		(session=0x10c4c1e10)   										 - 2026-11-04 18:03:00,798 - logic_logger - INFO
Logic Phase:		AFTER_FLUSH LOGIC	(session=0x10c4c1e10)   										 - 2026-11-04 18:03:00,799 - logic_logger - INFO
....Order[35] {AfterFlush Event} id: 35, notes: test 1793844180780, customer_id: 36, CreatedOn: None, date_shipped: None, amount_total:  [20.0000000000-->] 70.0000000000  row: 0x10c64d0d0  session: 0x10c4c1e10  ins_upd_dlt: upd, initial: upd - 2026-11-04 18:03:00,799 - logic_logger - INFO
....Order[34] {AfterFlush Event} id: 34, notes: test 1793844180768, customer_id: 36, CreatedOn: None, date_shipped: None, amount_total:  [50.0000000000-->] 0E-10  row: 0x10c64dcd0  session: 0x10c4c1e10  ins_upd_dlt: upd, initial: upd - 2026-11-04 18:03:00,799 - logic_logger - INFO

```
</details>

&nbsp;
&nbsp;

#### Scenario: Item - change product ✅ (0.04 s)
&emsp;  Scenario: Item - change product  
&emsp;&emsp;    Given a customer with credit limit 1000  
&emsp;&emsp;    And a product priced 10 with no suppliers  
&emsp;&emsp;    And a second product priced 30 with no suppliers  
&emsp;&emsp;    And an order is created with 5 of the product  
&emsp;&emsp;    When the item product is changed to the second product  
&emsp;&emsp;    Then the item unit price is 30  
&emsp;&emsp;    And the item amount is 150  

<details markdown>
<summary>Rules exercised and logic log (3 transactions)</summary>


&nbsp;
&nbsp;


**Rules Used** in Scenario: Item - change product
```
  Customer  
    1. Derive Customer.balance as Sum(Order.amount_total Where Rule.sum(derive=models.Customer.balance, as_sum_of=models.Order.amount_total, where=lambda row: row.date_shipped is None))  
  Order  
    2. RowEvent Order.send_row_to_kafka()  
    3. Derive Order.amount_total as Sum(Item.amount Where  - None)  
  Item  
    4. Derive Item.amount as Formula (1): Rule.formula(derive=models.Item.amount, as_expres [...]  
    5. RowEvent Item.set_item_unit_price_from_supplier()  
```
**Logic Log** in Scenario: Item - change product (3 transactions)
```
Logic Phase:		ROW LOGIC		(session=0x10c4c1150) (sqlalchemy before_flush)			 - 2026-11-04 18:03:00,830 - logic_logger - INFO
..Order[None] {Insert - client} id: None, notes: test 1793844180827, customer_id: 37, CreatedOn: None, date_shipped: None, amount_total: None  row: 0x10c4b61d0  session: 0x10c4c1150  ins_upd_dlt: ins, initial: ins - 2026-11-04 18:03:00,830 - logic_logger - INFO
..Order[None] {server aggregate_defaults: amount_total } id: None, notes: test 1793844180827, customer_id: 37, CreatedOn: None, date_shipped: None, amount_total: 0  row: 0x10c4b61d0  session: 0x10c4c1150  ins_upd_dlt: ins, initial: ins - 2026-11-04 18:03:00,831 - logic_logger - INFO
Logic Phase:		COMMIT LOGIC		(session=0x10c4c1150)   										 - 2026-11-04 18:03:00,831 - logic_logger - INFO
Logic Phase:		AFTER_FLUSH LOGIC	(session=0x10c4c1150)   										 - 2026-11-04 18:03:00,831 - logic_logger - INFO
..Order[36] {AfterFlush Event} id: 36, notes: test 1793844180827, customer_id: 37, CreatedOn: None, date_shipped: None, amount_total: 0  row: 0x10c4b61d0  session: 0x10c4c1150  ins_upd_dlt: ins, initial: ins - 2026-11-04 18:03:00,832 - logic_logger - INFO


Logic Phase:		ROW LOGIC		(session=0x10c4c16a0) (sqlalchemy before_flush)			 - 2026-11-04 18:03:00,835 - logic_logger - INFO
..Item[None] {Insert - client} id: None, order_id: 36, product_id: 39, quantity: 5, amount: None, unit_price: None  row: 0x10c4b6350  session: 0x10c4c16a0  ins_upd_dlt: ins, initial: ins - 2026-11-04 18:03:00,836 - logic_logger - INFO
..Item[None] {No suppliers for Test Product 1793844180818, using product unit_price} id: None, order_id: 36, product_id: 39, quantity: 5, amount: None, unit_price: None  row: 0x10c4b6350  session: 0x10c4c16a0  ins_upd_dlt: ins, initial: ins - 2026-11-04 18:03:00,836 - logic_logger - INFO
..Item[None] {Formula amount} id: None, order_id: 36, product_id: 39, quantity: 5, amount: 50.0000000000, unit_price: 10.0000000000  row: 0x10c4b6350  session: 0x10c4c16a0  ins_upd_dlt: ins, initial: ins - 2026-11-04 18:03:00,836 - logic_logger - INFO
....Order[36] {Update - Adjusting order: amount_total} id: 36, notes: test 1793844180827, customer_id: 37, CreatedOn: None, date_shipped: None, amount_total:  [0E-10-->] 50.0000000000  row: 0x10c64e350  session: 0x10c4c16a0  ins_upd_dlt: upd, initial: upd - 2026-11-04 18:03:00,836 - logic_logger - INFO
......Customer[37] {Update - Adjusting customer: balance} id: 37, name: Test Customer 1793844180813, balance:  [0E-10-->] 50.0000000000, credit_limit: 1000.0000000000, email: None, email_opt_out: None  row: 0x10c64f8d0  session: 0x10c4c16a0  ins_upd_dlt: upd, initial: upd - 2026-11-04 18:03:00,837 - logic_logger - INFO
Logic Phase:		COMMIT LOGIC		(session=0x10c4c16a0)   										 - 2026-11-04 18:03:00,837 - logic_logger - INFO
Logic Phase:		AFTER_FLUSH LOGIC	(session=0x10c4c16a0)   										 - 2026-11-04 18:03:00,838 - logic_logger - INFO
....Order[36] {AfterFlush Event} id: 36, notes: test 1793844180827, customer_id: 37, CreatedOn: None, date_shipped: None, amount_total:  [0E-10-->] 50.0000000000  row: 0x10c64e350  session: 0x10c4c16a0  ins_upd_dlt: upd, initial: upd - 2026-11-04 18:03:00,838 - logic_logger - INFO


Logic Phase:		ROW LOGIC		(session=0x10c4c18c0) (sqlalchemy before_flush)			 - 2026-11-04 18:03:00,843 - logic_logger - INFO
..Item[36] {Update - client} id: 36, order_id: 36, product_id:  [39-->] 40, quantity: 5, amount: 50.0000000000, unit_price: 10.0000000000  row: 0x10c64f750  session: 0x10c4c18c0  ins_upd_dlt: upd, initial: upd - 2026-11-04 18:03:00,843 - logic_logger - INFO
..Item[36] {No suppliers for Test Product 1793844180823, using product unit_price} id: 36, order_id: 36, product_id:  [39-->] 40, quantity: 5, amount: 50.0000000000, unit_price: 10.0000000000  row: 0x10c64f750  session: 0x10c4c18c0  ins_upd_dlt: upd, initial: upd - 2026-11-04 18:03:00,843 - logic_logger - INFO
..Item[36] {Formula amount} id: 36, order_id: 36, product_id:  [39-->] 40, quantity: 5, amount:  [50.0000000000-->] 150.0000000000, unit_price:  [10.0000000000-->] 30.0000000000  row: 0x10c64f750  session: 0x10c4c18c0  ins_upd_dlt: upd, initial: upd - 2026-11-04 18:03:00,843 - logic_logger - INFO
....Order[36] {Update - Adjusting order: amount_total} id: 36, notes: test 1793844180827, customer_id: 37, CreatedOn: None, date_shipped: None, amount_total:  [50.0000000000-->] 150.0000000000  row: 0x10c64ecd0  session: 0x10c4c18c0  ins_upd_dlt: upd, initial: upd - 2026-11-04 18:03:00,844 - logic_logger - INFO
......Customer[37] {Update - Adjusting customer: balance} id: 37, name: Test Customer 1793844180813, balance:  [50.0000000000-->] 150.0000000000, credit_limit: 1000.0000000000, email: None, email_opt_out: None  row: 0x10c688150  session: 0x10c4c18c0  ins_upd_dlt: upd, initial: upd - 2026-11-04 18:03:00,844 - logic_logger - INFO
Logic Phase:		COMMIT LOGIC		(session=0x10c4c18c0)   										 - 2026-11-04 18:03:00,844 - logic_logger - INFO
Logic Phase:		AFTER_FLUSH LOGIC	(session=0x10c4c18c0)   										 - 2026-11-04 18:03:00,845 - logic_logger - INFO
....Order[36] {AfterFlush Event} id: 36, notes: test 1793844180827, customer_id: 37, CreatedOn: None, date_shipped: None, amount_total:  [50.0000000000-->] 150.0000000000  row: 0x10c64ecd0  session: 0x10c4c18c0  ins_upd_dlt: upd, initial: upd - 2026-11-04 18:03:00,845 - logic_logger - INFO

```
</details>

&nbsp;
&nbsp;

#### Scenario: Suppliers - add and remove ✅ (0.04 s)
&emsp;  Scenario: Suppliers - add and remove  
&emsp;&emsp;    Given a customer with credit limit 1000  
&emsp;&emsp;    And a product priced 10 with no suppliers  
&emsp;&emsp;    When a supplier is added to the product costing 7  
&emsp;&emsp;    Then the product supplier count is 1  
&emsp;&emsp;    When a second supplier is added to the product costing 9  
&emsp;&emsp;    Then the product supplier count is 2  
&emsp;&emsp;    When the first supplier is removed from the product  
&emsp;&emsp;    Then the product supplier count is 1  

<details markdown>
<summary>Rules exercised and logic log (3 transactions)</summary>


&nbsp;
&nbsp;


**Rules Used** in Scenario: Suppliers - add and remove
```
  Product  
    1. Derive Product.count_suppliers as Count(ProductSupplier Where  - None)  
```
**Logic Log** in Scenario: Suppliers - add and remove (3 transactions)
```
Logic Phase:		ROW LOGIC		(session=0x10c694270) (sqlalchemy before_flush)			 - 2026-11-04 18:03:00,868 - logic_logger - INFO
..ProductSupplier[None] {Insert - client} id: None, product_id: 41, supplier_id: 1, supplier_part_number: None, unit_cost: 7, lead_time_days: 3  row: 0x10c4b79d0  session: 0x10c694270  ins_upd_dlt: ins, initial: ins - 2026-11-04 18:03:00,868 - logic_logger - INFO
....Product[41] {Update - Adjusting product: count_suppliers} id: 41, name: Test Product 1793844180860, count_suppliers:  [0-->] 1, unit_price: 10.0000000000  row: 0x10c644670  session: 0x10c694270  ins_upd_dlt: upd, initial: upd - 2026-11-04 18:03:00,870 - logic_logger - INFO
Logic Phase:		COMMIT LOGIC		(session=0x10c694270)   										 - 2026-11-04 18:03:00,870 - logic_logger - INFO
Logic Phase:		AFTER_FLUSH LOGIC	(session=0x10c694270)   										 - 2026-11-04 18:03:00,871 - logic_logger - INFO


Logic Phase:		ROW LOGIC		(session=0x10c4c19d0) (sqlalchemy before_flush)			 - 2026-11-04 18:03:00,878 - logic_logger - INFO
..ProductSupplier[None] {Insert - client} id: None, product_id: 41, supplier_id: 2, supplier_part_number: None, unit_cost: 9, lead_time_days: 3  row: 0x10c5206d0  session: 0x10c4c19d0  ins_upd_dlt: ins, initial: ins - 2026-11-04 18:03:00,879 - logic_logger - INFO
....Product[41] {Update - Adjusting product: count_suppliers} id: 41, name: Test Product 1793844180860, count_suppliers:  [1-->] 2, unit_price: 10.0000000000  row: 0x10c525da0  session: 0x10c4c19d0  ins_upd_dlt: upd, initial: upd - 2026-11-04 18:03:00,879 - logic_logger - INFO
Logic Phase:		COMMIT LOGIC		(session=0x10c4c19d0)   										 - 2026-11-04 18:03:00,879 - logic_logger - INFO
Logic Phase:		AFTER_FLUSH LOGIC	(session=0x10c4c19d0)   										 - 2026-11-04 18:03:00,880 - logic_logger - INFO


Logic Phase:		ROW LOGIC		(session=0x10c4c18c0) (sqlalchemy before_flush)			 - 2026-11-04 18:03:00,887 - logic_logger - INFO
..ProductSupplier[10] {Delete - client} id: 10, product_id: 41, supplier_id: 1, supplier_part_number: None, unit_cost: 7.0000000000, lead_time_days: 3  row: 0x10c5215d0  session: 0x10c4c18c0  ins_upd_dlt: dlt, initial: dlt - 2026-11-04 18:03:00,887 - logic_logger - INFO
....Product[41] {Update - Adjusting product: count_suppliers} id: 41, name: Test Product 1793844180860, count_suppliers:  [2-->] 1, unit_price: 10.0000000000  row: 0x10c5259b0  session: 0x10c4c18c0  ins_upd_dlt: upd, initial: upd - 2026-11-04 18:03:00,887 - logic_logger - INFO
Logic Phase:		COMMIT LOGIC		(session=0x10c4c18c0)   										 - 2026-11-04 18:03:00,888 - logic_logger - INFO
Logic Phase:		AFTER_FLUSH LOGIC	(session=0x10c4c18c0)   										 - 2026-11-04 18:03:00,888 - logic_logger - INFO

```
</details>

&nbsp;
&nbsp;

#### Scenario: Suppliers - move ✅ (0.03 s)
&emsp;  Scenario: Suppliers - move  
&emsp;&emsp;    Given a customer with credit limit 1000  
&emsp;&emsp;    And a product priced 10 with no suppliers  
&emsp;&emsp;    And a second product priced 20 with no suppliers  
&emsp;&emsp;    And a supplier is added to the product costing 7  
&emsp;&emsp;    When the product supplier is moved to the second product  
&emsp;&emsp;    Then the product supplier count is 0  
&emsp;&emsp;    And the second product supplier count is 1  

<details markdown>
<summary>Rules exercised and logic log (2 transactions)</summary>


&nbsp;
&nbsp;


**Rules Used** in Scenario: Suppliers - move
```
  Product  
    1. Derive Product.count_suppliers as Count(ProductSupplier Where  - None)  
```
**Logic Log** in Scenario: Suppliers - move (2 transactions)
```
Logic Phase:		ROW LOGIC		(session=0x10c4c0050) (sqlalchemy before_flush)			 - 2026-11-04 18:03:00,910 - logic_logger - INFO
..ProductSupplier[None] {Insert - client} id: None, product_id: 42, supplier_id: 1, supplier_part_number: None, unit_cost: 7, lead_time_days: 3  row: 0x10c47b0d0  session: 0x10c4c0050  ins_upd_dlt: ins, initial: ins - 2026-11-04 18:03:00,910 - logic_logger - INFO
....Product[42] {Update - Adjusting product: count_suppliers} id: 42, name: Test Product 1793844180899, count_suppliers:  [0-->] 1, unit_price: 10.0000000000  row: 0x10c525390  session: 0x10c4c0050  ins_upd_dlt: upd, initial: upd - 2026-11-04 18:03:00,911 - logic_logger - INFO
Logic Phase:		COMMIT LOGIC		(session=0x10c4c0050)   										 - 2026-11-04 18:03:00,911 - logic_logger - INFO
Logic Phase:		AFTER_FLUSH LOGIC	(session=0x10c4c0050)   										 - 2026-11-04 18:03:00,912 - logic_logger - INFO


Logic Phase:		ROW LOGIC		(session=0x10c4c07c0) (sqlalchemy before_flush)			 - 2026-11-04 18:03:00,916 - logic_logger - INFO
..ProductSupplier[12] {Update - client} id: 12, product_id:  [42-->] 43, supplier_id: 1, supplier_part_number: None, unit_cost: 7.0000000000, lead_time_days: 3  row: 0x10c64f5d0  session: 0x10c4c07c0  ins_upd_dlt: upd, initial: upd - 2026-11-04 18:03:00,916 - logic_logger - INFO
....Product[43] {Update - Adjusting product: count_suppliers, count_suppliers} id: 43, name: Test Product 1793844180904, count_suppliers:  [0-->] 1, unit_price: 20.0000000000  row: 0x10c525010  session: 0x10c4c07c0  ins_upd_dlt: upd, initial: upd - 2026-11-04 18:03:00,917 - logic_logger - INFO
....Product[42] {Update - Adjusting Old product} id: 42, name: Test Product 1793844180899, count_suppliers:  [1-->] 0, unit_price: 10.0000000000  row: 0x10c524e50  session: 0x10c4c07c0  ins_upd_dlt: upd, initial: upd - 2026-11-04 18:03:00,917 - logic_logger - INFO
Logic Phase:		COMMIT LOGIC		(session=0x10c4c07c0)   										 - 2026-11-04 18:03:00,917 - logic_logger - INFO
Logic Phase:		AFTER_FLUSH LOGIC	(session=0x10c4c07c0)   										 - 2026-11-04 18:03:00,918 - logic_logger - INFO

```
</details>

&nbsp;
&nbsp;

#### Scenario: AI - no suppliers ✅ (0.03 s)
&emsp;  Scenario: AI - no suppliers  
&emsp;&emsp;    Given a customer with credit limit 1000  
&emsp;&emsp;    And a product priced 10 with no suppliers  
&emsp;&emsp;    When an order is created with 5 of the product  
&emsp;&emsp;    Then the item unit price is 10  
&emsp;&emsp;    And no AI audit row exists for the item  

<details markdown>
<summary>Rules exercised and logic log (2 transactions)</summary>


&nbsp;
&nbsp;


**Rules Used** in Scenario: AI - no suppliers
```
  Customer  
    1. Derive Customer.balance as Sum(Order.amount_total Where Rule.sum(derive=models.Customer.balance, as_sum_of=models.Order.amount_total, where=lambda row: row.date_shipped is None))  
  Order  
    2. RowEvent Order.send_row_to_kafka()  
    3. Derive Order.amount_total as Sum(Item.amount Where  - None)  
  Item  
    4. Derive Item.amount as Formula (1): Rule.formula(derive=models.Item.amount, as_expres [...]  
    5. RowEvent Item.set_item_unit_price_from_supplier()  
```
**Logic Log** in Scenario: AI - no suppliers (2 transactions)
```
Logic Phase:		ROW LOGIC		(session=0x10c4c3ac0) (sqlalchemy before_flush)			 - 2026-11-04 18:03:00,940 - logic_logger - INFO
..Order[None] {Insert - client} id: None, notes: test 1793844180938, customer_id: 40, CreatedOn: None, date_shipped: None, amount_total: None  row: 0x10c4b7dd0  session: 0x10c4c3ac0  ins_upd_dlt: ins, initial: ins - 2026-11-04 18:03:00,940 - logic_logger - INFO
..Order[None] {server aggregate_defaults: amount_total } id: None, notes: test 1793844180938, customer_id: 40, CreatedOn: None, date_shipped: None, amount_total: 0  row: 0x10c4b7dd0  session: 0x10c4c3ac0  ins_upd_dlt: ins, initial: ins - 2026-11-04 18:03:00,940 - logic_logger - INFO
Logic Phase:		COMMIT LOGIC		(session=0x10c4c3ac0)   										 - 2026-11-04 18:03:00,941 - logic_logger - INFO
Logic Phase:		AFTER_FLUSH LOGIC	(session=0x10c4c3ac0)   										 - 2026-11-04 18:03:00,941 - logic_logger - INFO
..Order[37] {AfterFlush Event} id: 37, notes: test 1793844180938, customer_id: 40, CreatedOn: None, date_shipped: None, amount_total: 0  row: 0x10c4b7dd0  session: 0x10c4c3ac0  ins_upd_dlt: ins, initial: ins - 2026-11-04 18:03:00,941 - logic_logger - INFO


Logic Phase:		ROW LOGIC		(session=0x10c4c2140) (sqlalchemy before_flush)			 - 2026-11-04 18:03:00,946 - logic_logger - INFO
..Item[None] {Insert - client} id: None, order_id: 37, product_id: 44, quantity: 5, amount: None, unit_price: None  row: 0x10c5220d0  session: 0x10c4c2140  ins_upd_dlt: ins, initial: ins - 2026-11-04 18:03:00,946 - logic_logger - INFO
..Item[None] {No suppliers for Test Product 1793844180933, using product unit_price} id: None, order_id: 37, product_id: 44, quantity: 5, amount: None, unit_price: None  row: 0x10c5220d0  session: 0x10c4c2140  ins_upd_dlt: ins, initial: ins - 2026-11-04 18:03:00,947 - logic_logger - INFO
..Item[None] {Formula amount} id: None, order_id: 37, product_id: 44, quantity: 5, amount: 50.0000000000, unit_price: 10.0000000000  row: 0x10c5220d0  session: 0x10c4c2140  ins_upd_dlt: ins, initial: ins - 2026-11-04 18:03:00,947 - logic_logger - INFO
....Order[37] {Update - Adjusting order: amount_total} id: 37, notes: test 1793844180938, customer_id: 40, CreatedOn: None, date_shipped: None, amount_total:  [0E-10-->] 50.0000000000  row: 0x10c64f6d0  session: 0x10c4c2140  ins_upd_dlt: upd, initial: upd - 2026-11-04 18:03:00,947 - logic_logger - INFO
......Customer[40] {Update - Adjusting customer: balance} id: 40, name: Test Customer 1793844180928, balance:  [0E-10-->] 50.0000000000, credit_limit: 1000.0000000000, email: None, email_opt_out: None  row: 0x10c64e950  session: 0x10c4c2140  ins_upd_dlt: upd, initial: upd - 2026-11-04 18:03:00,947 - logic_logger - INFO
Logic Phase:		COMMIT LOGIC		(session=0x10c4c2140)   										 - 2026-11-04 18:03:00,947 - logic_logger - INFO
Logic Phase:		AFTER_FLUSH LOGIC	(session=0x10c4c2140)   										 - 2026-11-04 18:03:00,948 - logic_logger - INFO
....Order[37] {AfterFlush Event} id: 37, notes: test 1793844180938, customer_id: 40, CreatedOn: None, date_shipped: None, amount_total:  [0E-10-->] 50.0000000000  row: 0x10c64f6d0  session: 0x10c4c2140  ins_upd_dlt: upd, initial: upd - 2026-11-04 18:03:00,948 - logic_logger - INFO

```
</details>

&nbsp;
&nbsp;

#### Scenario: AI - chooses a supplier ✅ (2.6 s)
&emsp;  Scenario: AI - chooses a supplier  
&emsp;&emsp;    Given a customer with credit limit 1000  
&emsp;&emsp;    And a product priced 50 with suppliers costing 7 and 9  
&emsp;&emsp;    When an order is created with 5 of the product  
&emsp;&emsp;    Then the AI chose one of the product suppliers and an audit row exists  
&emsp;&emsp;    And the item amount is the quantity times the chosen price  
&emsp;&emsp;    And the customer balance is the item amount  

<details markdown>
<summary>Rules exercised and logic log (4 transactions)</summary>


&nbsp;
&nbsp;


**Rules Used** in Scenario: AI - chooses a supplier
```
  Product  
    1. Derive Product.count_suppliers as Count(ProductSupplier Where  - None)  
  Customer  
    2. Derive Customer.balance as Sum(Order.amount_total Where Rule.sum(derive=models.Customer.balance, as_sum_of=models.Order.amount_total, where=lambda row: row.date_shipped is None))  
  Order  
    3. RowEvent Order.send_row_to_kafka()  
    4. Derive Order.amount_total as Sum(Item.amount Where  - None)  
  Item  
    5. Derive Item.amount as Formula (1): Rule.formula(derive=models.Item.amount, as_expres [...]  
    6. RowEvent Item.set_item_unit_price_from_supplier()  
  SysSupplierReq  
    7. RowEvent SysSupplierReq.select_supplier_via_ai()  
```
**Logic Log** in Scenario: AI - chooses a supplier (4 transactions)
```
Logic Phase:		ROW LOGIC		(session=0x10c4c1f20) (sqlalchemy before_flush)			 - 2026-11-04 18:03:00,973 - logic_logger - INFO
..ProductSupplier[None] {Insert - client} id: None, product_id: 45, supplier_id: 1, supplier_part_number: None, unit_cost: 7, lead_time_days: 3  row: 0x10c4b55d0  session: 0x10c4c1f20  ins_upd_dlt: ins, initial: ins - 2026-11-04 18:03:00,974 - logic_logger - INFO
....Product[45] {Update - Adjusting product: count_suppliers} id: 45, name: Test Product 1793844180967, count_suppliers:  [0-->] 1, unit_price: 50.0000000000  row: 0x10c525080  session: 0x10c4c1f20  ins_upd_dlt: upd, initial: upd - 2026-11-04 18:03:00,974 - logic_logger - INFO
Logic Phase:		COMMIT LOGIC		(session=0x10c4c1f20)   										 - 2026-11-04 18:03:00,974 - logic_logger - INFO
Logic Phase:		AFTER_FLUSH LOGIC	(session=0x10c4c1f20)   										 - 2026-11-04 18:03:00,975 - logic_logger - INFO


Logic Phase:		ROW LOGIC		(session=0x10c4c1d00) (sqlalchemy before_flush)			 - 2026-11-04 18:03:00,978 - logic_logger - INFO
..ProductSupplier[None] {Insert - client} id: None, product_id: 45, supplier_id: 2, supplier_part_number: None, unit_cost: 9, lead_time_days: 3  row: 0x10c4b7dd0  session: 0x10c4c1d00  ins_upd_dlt: ins, initial: ins - 2026-11-04 18:03:00,978 - logic_logger - INFO
....Product[45] {Update - Adjusting product: count_suppliers} id: 45, name: Test Product 1793844180967, count_suppliers:  [1-->] 2, unit_price: 50.0000000000  row: 0x10c5252b0  session: 0x10c4c1d00  ins_upd_dlt: upd, initial: upd - 2026-11-04 18:03:00,979 - logic_logger - INFO
Logic Phase:		COMMIT LOGIC		(session=0x10c4c1d00)   										 - 2026-11-04 18:03:00,979 - logic_logger - INFO
Logic Phase:		AFTER_FLUSH LOGIC	(session=0x10c4c1d00)   										 - 2026-11-04 18:03:00,980 - logic_logger - INFO


Logic Phase:		ROW LOGIC		(session=0x10c4c1260) (sqlalchemy before_flush)			 - 2026-11-04 18:03:00,984 - logic_logger - INFO
..Order[None] {Insert - client} id: None, notes: test 1793844180982, customer_id: 41, CreatedOn: None, date_shipped: None, amount_total: None  row: 0x10c5223d0  session: 0x10c4c1260  ins_upd_dlt: ins, initial: ins - 2026-11-04 18:03:00,984 - logic_logger - INFO
..Order[None] {server aggregate_defaults: amount_total } id: None, notes: test 1793844180982, customer_id: 41, CreatedOn: None, date_shipped: None, amount_total: 0  row: 0x10c5223d0  session: 0x10c4c1260  ins_upd_dlt: ins, initial: ins - 2026-11-04 18:03:00,984 - logic_logger - INFO
Logic Phase:		COMMIT LOGIC		(session=0x10c4c1260)   										 - 2026-11-04 18:03:00,984 - logic_logger - INFO
Logic Phase:		AFTER_FLUSH LOGIC	(session=0x10c4c1260)   										 - 2026-11-04 18:03:00,985 - logic_logger - INFO
..Order[38] {AfterFlush Event} id: 38, notes: test 1793844180982, customer_id: 41, CreatedOn: None, date_shipped: None, amount_total: 0  row: 0x10c5223d0  session: 0x10c4c1260  ins_upd_dlt: ins, initial: ins - 2026-11-04 18:03:00,985 - logic_logger - INFO


Logic Phase:		ROW LOGIC		(session=0x10c4c1040) (sqlalchemy before_flush)			 - 2026-11-04 18:03:00,988 - logic_logger - INFO
..Item[None] {Insert - client} id: None, order_id: 38, product_id: 45, quantity: 5, amount: None, unit_price: None  row: 0x10c521e50  session: 0x10c4c1040  ins_upd_dlt: ins, initial: ins - 2026-11-04 18:03:00,988 - logic_logger - INFO
..Item[None] {Product Test Product 1793844180967 has 2 suppliers, requesting AI selection} id: None, order_id: 38, product_id: 45, quantity: 5, amount: None, unit_price: None  row: 0x10c521e50  session: 0x10c4c1040  ins_upd_dlt: ins, initial: ins - 2026-11-04 18:03:00,989 - logic_logger - INFO
....SysSupplierReq[None] {Insert - AI supplier selection request} id: None, item_id: None, product_id: 45, chosen_supplier_id: None, chosen_unit_price: None, request: None, reason: None, fallback_used: None, created_on: None  row: 0x10c6632f0  session: 0x10c4c1040  ins_upd_dlt: ins, initial: ins - 2026-11-04 18:03:00,989 - logic_logger - INFO
....SysSupplierReq[None] {Calling OpenAI with 2 candidates, world conditions: Suez Canal blocked - use alternate shipping routes} id: None, item_id: None, product_id: 45, chosen_supplier_id: None, chosen_unit_price: None, request: Select supplier for Test Product 1793844180967: Candidates=[Genuine Sheets of Cairo($7.0, Near East, 3days), Sheets for Less of NJ($9.0, New Jersey, 3days)], World=Suez Canal blocked - use alternate shipping routes, reason: None, fallback_used: None, created_on: 2026-11-04T18:03:00  row: 0x10c6632f0  session: 0x10c4c1040  ins_upd_dlt: ins, initial: ins - 2026-11-04 18:03:01,206 - logic_logger - INFO
....SysSupplierReq[None] {OpenAI response: {"chosen_supplier_id": 2, "chosen_unit_price": 9.0, "reason": "Despite the higher cost, Sheets for Less of NJ offers a similar lead time without being affected by the Suez Canal blockage, ensuring faster and more reliable delivery."}} id: None, item_id: None, product_id: 45, chosen_supplier_id: None, chosen_unit_price: None, request: Select supplier for Test Product 1793844180967: Candidates=[Genuine Sheets of Cairo($7.0, Near East, 3days), Sheets for Less of NJ($9.0, New Jersey, 3days)], World=Suez Canal blocked - use alternate shipping routes, reason: None, fallback_used: None, created_on: 2026-11-04T18:03:00  row: 0x10c6632f0  session: 0x10c4c1040  ins_upd_dlt: ins, initial: ins - 2026-11-04 18:03:03,508 - logic_logger - INFO
....SysSupplierReq[None] {Selected supplier 2 with price 9.0000000000} id: None, item_id: None, product_id: 45, chosen_supplier_id: 2, chosen_unit_price: 9.0000000000, request: Select supplier for Test Product 1793844180967: Candidates=[Genuine Sheets of Cairo($7.0, Near East, 3days), Sheets for Less of NJ($9.0, New Jersey, 3days)], World=Suez Canal blocked - use alternate shipping routes, reason: AI: Sheets for Less of NJ ($9.0000000000) - Despite the higher cost, Sheets for Less of NJ offers a similar lead time without being affected by the Suez Canal blockage, ensuring faster and more reliable delivery., fallback_used: False, created_on: 2026-11-04T18:03:00  row: 0x10c6632f0  session: 0x10c4c1040  ins_upd_dlt: ins, initial: ins - 2026-11-04 18:03:03,509 - logic_logger - INFO
..Item[None] {AI Request: Select supplier for Test Product 1793844180967: Candidates=[Genuine Sheets of Cairo($7.0, Near East, 3days), Sheets for Less of NJ($9.0, New Jersey, 3days)], World=Suez Canal blocked - use alternate shipping routes} id: None, order_id: 38, product_id: 45, quantity: 5, amount: None, unit_price: None  row: 0x10c521e50  session: 0x10c4c1040  ins_upd_dlt: ins, initial: ins - 2026-11-04 18:03:03,509 - logic_logger - INFO
..Item[None] {AI Results: supplier_id=2, price=9.0000000000, reason=AI: Sheets for Less of NJ ($9.0000000000) - Despite the higher cost, Sheets for Less of NJ offers a similar lead time without being affected by the Suez Canal blockage, ensuring faster and more reliable delivery.} id: None, order_id: 38, product_id: 45, quantity: 5, amount: None, unit_price: None  row: 0x10c521e50  session: 0x10c4c1040  ins_upd_dlt: ins, initial: ins - 2026-11-04 18:03:03,509 - logic_logger - INFO
..Item[None] {Formula amount} id: None, order_id: 38, product_id: 45, quantity: 5, amount: 45.0000000000, unit_price: 9.0000000000  row: 0x10c521e50  session: 0x10c4c1040  ins_upd_dlt: ins, initial: ins - 2026-11-04 18:03:03,510 - logic_logger - INFO
....Order[38] {Update - Adjusting order: amount_total} id: 38, notes: test 1793844180982, customer_id: 41, CreatedOn: None, date_shipped: None, amount_total:  [0E-10-->] 45.0000000000  row: 0x10c64ea50  session: 0x10c4c1040  ins_upd_dlt: upd, initial: upd - 2026-11-04 18:03:03,510 - logic_logger - INFO
......Customer[41] {Update - Adjusting customer: balance} id: 41, name: Test Customer 1793844180962, balance:  [0E-10-->] 45.0000000000, credit_limit: 1000.0000000000, email: None, email_opt_out: None  row: 0x113003dd0  session: 0x10c4c1040  ins_upd_dlt: upd, initial: upd - 2026-11-04 18:03:03,513 - logic_logger - INFO
Logic Phase:		COMMIT LOGIC		(session=0x10c4c1040)   										 - 2026-11-04 18:03:03,513 - logic_logger - INFO
Logic Phase:		AFTER_FLUSH LOGIC	(session=0x10c4c1040)   										 - 2026-11-04 18:03:03,518 - logic_logger - INFO
....Order[38] {AfterFlush Event} id: 38, notes: test 1793844180982, customer_id: 41, CreatedOn: None, date_shipped: None, amount_total:  [0E-10-->] 45.0000000000  row: 0x10c64ea50  session: 0x10c4c1040  ins_upd_dlt: upd, initial: upd - 2026-11-04 18:03:03,518 - logic_logger - INFO

```
</details>

&nbsp;
&nbsp;

#### Scenario: AI - product change ✅ (1.4 s)
&emsp;  Scenario: AI - product change  
&emsp;&emsp;    Given a customer with credit limit 1000  
&emsp;&emsp;    And a product priced 10 with no suppliers  
&emsp;&emsp;    And a second product priced 50 with suppliers costing 7 and 9  
&emsp;&emsp;    And an order is created with 5 of the product  
&emsp;&emsp;    When the item product is changed to the second product  
&emsp;&emsp;    Then the AI chose one of the product suppliers and an audit row exists  

<details markdown>
<summary>Rules exercised and logic log (5 transactions)</summary>


&nbsp;
&nbsp;


**Rules Used** in Scenario: AI - product change
```
  Product  
    1. Derive Product.count_suppliers as Count(ProductSupplier Where  - None)  
  Customer  
    2. Derive Customer.balance as Sum(Order.amount_total Where Rule.sum(derive=models.Customer.balance, as_sum_of=models.Order.amount_total, where=lambda row: row.date_shipped is None))  
  Order  
    3. RowEvent Order.send_row_to_kafka()  
    4. Derive Order.amount_total as Sum(Item.amount Where  - None)  
  Item  
    5. Derive Item.amount as Formula (1): Rule.formula(derive=models.Item.amount, as_expres [...]  
    6. RowEvent Item.set_item_unit_price_from_supplier()  
  SysSupplierReq  
    7. RowEvent SysSupplierReq.select_supplier_via_ai()  
```
**Logic Log** in Scenario: AI - product change (5 transactions)
```
Logic Phase:		ROW LOGIC		(session=0x10df118c0) (sqlalchemy before_flush)			 - 2026-11-04 18:03:03,574 - logic_logger - INFO
..ProductSupplier[None] {Insert - client} id: None, product_id: 47, supplier_id: 1, supplier_part_number: None, unit_cost: 7, lead_time_days: 3  row: 0x10dcb10d0  session: 0x10df118c0  ins_upd_dlt: ins, initial: ins - 2026-11-04 18:03:03,574 - logic_logger - INFO
....Product[47] {Update - Adjusting product: count_suppliers} id: 47, name: Test Product 1793844183568, count_suppliers:  [0-->] 1, unit_price: 50.0000000000  row: 0x10df02cf0  session: 0x10df118c0  ins_upd_dlt: upd, initial: upd - 2026-11-04 18:03:03,575 - logic_logger - INFO
Logic Phase:		COMMIT LOGIC		(session=0x10df118c0)   										 - 2026-11-04 18:03:03,575 - logic_logger - INFO
Logic Phase:		AFTER_FLUSH LOGIC	(session=0x10df118c0)   										 - 2026-11-04 18:03:03,575 - logic_logger - INFO


Logic Phase:		ROW LOGIC		(session=0x10df119d0) (sqlalchemy before_flush)			 - 2026-11-04 18:03:03,579 - logic_logger - INFO
..ProductSupplier[None] {Insert - client} id: None, product_id: 47, supplier_id: 2, supplier_part_number: None, unit_cost: 9, lead_time_days: 3  row: 0x10c403ad0  session: 0x10df119d0  ins_upd_dlt: ins, initial: ins - 2026-11-04 18:03:03,579 - logic_logger - INFO
....Product[47] {Update - Adjusting product: count_suppliers} id: 47, name: Test Product 1793844183568, count_suppliers:  [1-->] 2, unit_price: 50.0000000000  row: 0x10df02e40  session: 0x10df119d0  ins_upd_dlt: upd, initial: upd - 2026-11-04 18:03:03,580 - logic_logger - INFO
Logic Phase:		COMMIT LOGIC		(session=0x10df119d0)   										 - 2026-11-04 18:03:03,580 - logic_logger - INFO
Logic Phase:		AFTER_FLUSH LOGIC	(session=0x10df119d0)   										 - 2026-11-04 18:03:03,581 - logic_logger - INFO


Logic Phase:		ROW LOGIC		(session=0x10df11ae0) (sqlalchemy before_flush)			 - 2026-11-04 18:03:03,584 - logic_logger - INFO
..Order[None] {Insert - client} id: None, notes: test 1793844183583, customer_id: 42, CreatedOn: None, date_shipped: None, amount_total: None  row: 0x10c64fad0  session: 0x10df11ae0  ins_upd_dlt: ins, initial: ins - 2026-11-04 18:03:03,584 - logic_logger - INFO
..Order[None] {server aggregate_defaults: amount_total } id: None, notes: test 1793844183583, customer_id: 42, CreatedOn: None, date_shipped: None, amount_total: 0  row: 0x10c64fad0  session: 0x10df11ae0  ins_upd_dlt: ins, initial: ins - 2026-11-04 18:03:03,584 - logic_logger - INFO
Logic Phase:		COMMIT LOGIC		(session=0x10df11ae0)   										 - 2026-11-04 18:03:03,585 - logic_logger - INFO
Logic Phase:		AFTER_FLUSH LOGIC	(session=0x10df11ae0)   										 - 2026-11-04 18:03:03,585 - logic_logger - INFO
..Order[39] {AfterFlush Event} id: 39, notes: test 1793844183583, customer_id: 42, CreatedOn: None, date_shipped: None, amount_total: 0  row: 0x10c64fad0  session: 0x10df11ae0  ins_upd_dlt: ins, initial: ins - 2026-11-04 18:03:03,585 - logic_logger - INFO


Logic Phase:		ROW LOGIC		(session=0x10df11f20) (sqlalchemy before_flush)			 - 2026-11-04 18:03:03,589 - logic_logger - INFO
..Item[None] {Insert - client} id: None, order_id: 39, product_id: 46, quantity: 5, amount: None, unit_price: None  row: 0x10c4793d0  session: 0x10df11f20  ins_upd_dlt: ins, initial: ins - 2026-11-04 18:03:03,589 - logic_logger - INFO
..Item[None] {No suppliers for Test Product 1793844183563, using product unit_price} id: None, order_id: 39, product_id: 46, quantity: 5, amount: None, unit_price: None  row: 0x10c4793d0  session: 0x10df11f20  ins_upd_dlt: ins, initial: ins - 2026-11-04 18:03:03,589 - logic_logger - INFO
..Item[None] {Formula amount} id: None, order_id: 39, product_id: 46, quantity: 5, amount: 50.0000000000, unit_price: 10.0000000000  row: 0x10c4793d0  session: 0x10df11f20  ins_upd_dlt: ins, initial: ins - 2026-11-04 18:03:03,589 - logic_logger - INFO
....Order[39] {Update - Adjusting order: amount_total} id: 39, notes: test 1793844183583, customer_id: 42, CreatedOn: None, date_shipped: None, amount_total:  [0E-10-->] 50.0000000000  row: 0x113048550  session: 0x10df11f20  ins_upd_dlt: upd, initial: upd - 2026-11-04 18:03:03,590 - logic_logger - INFO
......Customer[42] {Update - Adjusting customer: balance} id: 42, name: Test Customer 1793844183556, balance:  [0E-10-->] 50.0000000000, credit_limit: 1000.0000000000, email: None, email_opt_out: None  row: 0x11304a2d0  session: 0x10df11f20  ins_upd_dlt: upd, initial: upd - 2026-11-04 18:03:03,590 - logic_logger - INFO
Logic Phase:		COMMIT LOGIC		(session=0x10df11f20)   										 - 2026-11-04 18:03:03,590 - logic_logger - INFO
Logic Phase:		AFTER_FLUSH LOGIC	(session=0x10df11f20)   										 - 2026-11-04 18:03:03,591 - logic_logger - INFO
....Order[39] {AfterFlush Event} id: 39, notes: test 1793844183583, customer_id: 42, CreatedOn: None, date_shipped: None, amount_total:  [0E-10-->] 50.0000000000  row: 0x113048550  session: 0x10df11f20  ins_upd_dlt: upd, initial: upd - 2026-11-04 18:03:03,591 - logic_logger - INFO


Logic Phase:		ROW LOGIC		(session=0x10df11e10) (sqlalchemy before_flush)			 - 2026-11-04 18:03:03,595 - logic_logger - INFO
..Item[39] {Update - client} id: 39, order_id: 39, product_id:  [46-->] 47, quantity: 5, amount: 50.0000000000, unit_price: 10.0000000000  row: 0x113000350  session: 0x10df11e10  ins_upd_dlt: upd, initial: upd - 2026-11-04 18:03:03,595 - logic_logger - INFO
..Item[39] {Product Test Product 1793844183568 has 2 suppliers, requesting AI selection} id: 39, order_id: 39, product_id:  [46-->] 47, quantity: 5, amount: 50.0000000000, unit_price: 10.0000000000  row: 0x113000350  session: 0x10df11e10  ins_upd_dlt: upd, initial: upd - 2026-11-04 18:03:03,596 - logic_logger - INFO
....SysSupplierReq[None] {Insert - AI supplier selection request} id: None, item_id: None, product_id: 47, chosen_supplier_id: None, chosen_unit_price: None, request: None, reason: None, fallback_used: None, created_on: None  row: 0x10c662350  session: 0x10df11e10  ins_upd_dlt: ins, initial: ins - 2026-11-04 18:03:03,596 - logic_logger - INFO
....SysSupplierReq[None] {Calling OpenAI with 2 candidates, world conditions: Suez Canal blocked - use alternate shipping routes} id: None, item_id: None, product_id: 47, chosen_supplier_id: None, chosen_unit_price: None, request: Select supplier for Test Product 1793844183568: Candidates=[Genuine Sheets of Cairo($7.0, Near East, 3days), Sheets for Less of NJ($9.0, New Jersey, 3days)], World=Suez Canal blocked - use alternate shipping routes, reason: None, fallback_used: None, created_on: 2026-11-04T18:03:03  row: 0x10c662350  session: 0x10df11e10  ins_upd_dlt: ins, initial: ins - 2026-11-04 18:03:03,597 - logic_logger - INFO
....SysSupplierReq[None] {OpenAI response: {"chosen_supplier_id": 2, "chosen_unit_price": 9.0, "reason": "With the Suez Canal blocked, Genuine Sheets of Cairo may face delays due to alternate shipping routes, making Sheets for Less of NJ a more reliable choice for fastest delivery."}} id: None, item_id: None, product_id: 47, chosen_supplier_id: None, chosen_unit_price: None, request: Select supplier for Test Product 1793844183568: Candidates=[Genuine Sheets of Cairo($7.0, Near East, 3days), Sheets for Less of NJ($9.0, New Jersey, 3days)], World=Suez Canal blocked - use alternate shipping routes, reason: None, fallback_used: None, created_on: 2026-11-04T18:03:03  row: 0x10c662350  session: 0x10df11e10  ins_upd_dlt: ins, initial: ins - 2026-11-04 18:03:04,914 - logic_logger - INFO
....SysSupplierReq[None] {Selected supplier 2 with price 9.0000000000} id: None, item_id: None, product_id: 47, chosen_supplier_id: 2, chosen_unit_price: 9.0000000000, request: Select supplier for Test Product 1793844183568: Candidates=[Genuine Sheets of Cairo($7.0, Near East, 3days), Sheets for Less of NJ($9.0, New Jersey, 3days)], World=Suez Canal blocked - use alternate shipping routes, reason: AI: Sheets for Less of NJ ($9.0000000000) - With the Suez Canal blocked, Genuine Sheets of Cairo may face delays due to alternate shipping routes, making Sheets for Less of NJ a more reliable choice for fastest delivery., fallback_used: False, created_on: 2026-11-04T18:03:03  row: 0x10c662350  session: 0x10df11e10  ins_upd_dlt: ins, initial: ins - 2026-11-04 18:03:04,914 - logic_logger - INFO
..Item[39] {AI Request: Select supplier for Test Product 1793844183568: Candidates=[Genuine Sheets of Cairo($7.0, Near East, 3days), Sheets for Less of NJ($9.0, New Jersey, 3days)], World=Suez Canal blocked - use alternate shipping routes} id: 39, order_id: 39, product_id:  [46-->] 47, quantity: 5, amount: 50.0000000000, unit_price: 10.0000000000  row: 0x113000350  session: 0x10df11e10  ins_upd_dlt: upd, initial: upd - 2026-11-04 18:03:04,915 - logic_logger - INFO
..Item[39] {AI Results: supplier_id=2, price=9.0000000000, reason=AI: Sheets for Less of NJ ($9.0000000000) - With the Suez Canal blocked, Genuine Sheets of Cairo may face delays due to alternate shipping routes, making Sheets for Less of NJ a more reliable choice for fastest delivery.} id: 39, order_id: 39, product_id:  [46-->] 47, quantity: 5, amount: 50.0000000000, unit_price: 10.0000000000  row: 0x113000350  session: 0x10df11e10  ins_upd_dlt: upd, initial: upd - 2026-11-04 18:03:04,915 - logic_logger - INFO
..Item[39] {Formula amount} id: 39, order_id: 39, product_id:  [46-->] 47, quantity: 5, amount:  [50.0000000000-->] 45.0000000000, unit_price:  [10.0000000000-->] 9.0000000000  row: 0x113000350  session: 0x10df11e10  ins_upd_dlt: upd, initial: upd - 2026-11-04 18:03:04,915 - logic_logger - INFO
....Order[39] {Update - Adjusting order: amount_total} id: 39, notes: test 1793844183583, customer_id: 42, CreatedOn: None, date_shipped: None, amount_total:  [50.0000000000-->] 45.0000000000  row: 0x11304b650  session: 0x10df11e10  ins_upd_dlt: upd, initial: upd - 2026-11-04 18:03:04,917 - logic_logger - INFO
......Customer[42] {Update - Adjusting customer: balance} id: 42, name: Test Customer 1793844183556, balance:  [50.0000000000-->] 45.0000000000, credit_limit: 1000.0000000000, email: None, email_opt_out: None  row: 0x11304bd50  session: 0x10df11e10  ins_upd_dlt: upd, initial: upd - 2026-11-04 18:03:04,918 - logic_logger - INFO
Logic Phase:		COMMIT LOGIC		(session=0x10df11e10)   										 - 2026-11-04 18:03:04,918 - logic_logger - INFO
Logic Phase:		AFTER_FLUSH LOGIC	(session=0x10df11e10)   										 - 2026-11-04 18:03:04,922 - logic_logger - INFO
....Order[39] {AfterFlush Event} id: 39, notes: test 1793844183583, customer_id: 42, CreatedOn: None, date_shipped: None, amount_total:  [50.0000000000-->] 45.0000000000  row: 0x11304b650  session: 0x10df11e10  ins_upd_dlt: upd, initial: upd - 2026-11-04 18:03:04,922 - logic_logger - INFO

```
</details>

&nbsp;&nbsp;  
/Users/val/dev/genai-logic/ApiLogicServer-dev/build_and_test/genai-logic/demo_ai_rules_supplier/test/api_logic_server_behave/behave_run.py completed at November 04, 2026 18:03:04  
Behave run time: 4.711 s  


&nbsp;
&nbsp;

## Provenance

| | |
|---|---|
| Generated | November 04, 2026 18:12 |
| Generator | `requirements_traceability_report.py` 2.15 |
| Report text from | reports/Requirements Traceability Report Template.md (sha256 a19673a13fa0) |
| Tests last ran | November 04, 2026 18:03 |
| Project | basic_demo_ai_rules-supplier |
| Project created | November 04, 2026 17:39:57 |
| Requirement files read | `docs/requirements/app_integration/requirements.md` (sha256 f1ca8662)<br>`docs/requirements/check_credit/requirements.md` (sha256 965d672e)<br>`docs/requirements/demo_ai_rules_supplier/requirements.md` (sha256 f3a7037e) |
| Regenerate | `python requirements_traceability_report.py run`, from `test/api_logic_server_behave` |

_The report is derived from the project's files and the last test run; nothing in it is stored anywhere else, so regenerating it always reflects the project as it is now._

