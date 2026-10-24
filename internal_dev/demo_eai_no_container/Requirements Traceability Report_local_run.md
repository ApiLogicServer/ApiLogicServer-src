# Requirements Traceability Report

This report shows requirements, the rules created from them, and the tests created from those rules.

This project began as natural-language requirements, fleshed out by AI into a running system of business rules that are *executable documentation*. This report is how you govern the result.

A governable system is one you can **read**, **trust**, and **maintain**: each requirement is listed beside the rules that implement it (*read*); the tests and logic logs show those rules running (*trust*); re-run it after any change and it flags the gaps — an untested requirement, an untraced rule, a channel no test checks (*maintain*).

It is generated from the project's own files, nothing written by hand, so it is as current as the last run and covers the whole project, not a sample. Open **Background** (below the summary) for what the terms mean, how to read the report, and what it can and can't tell you.


**Project:** demo_eai &nbsp;|&nbsp; **Generated:** October 24, 2026 09:59 &nbsp;|&nbsp; **Rules:** 8 &nbsp;|&nbsp; **Test scenarios:** 12 &nbsp;|&nbsp; **Generator:** requirements_traceability_report.py 2.11

**Last test run:** October 24, 2026 09:59, took 3.0 s (0m before this report; test results and logic logs below are from that run)


&nbsp;
&nbsp;

## At a Glance

**✅ 5 requirement(s), all implemented; 5 tested; 12 of 12 scenarios passed; last run 0m ago.**

| | |
|---|---|
| Requirements | 5 (5 implemented) |
| Tested | 5 of 5 |
| Last test run | ✅ 12 passed, 0 failed (October 24, 2026 09:59, 0m ago); took 3.0 s |
| Rules | 8 (5 declarative, 0 Python functions, 3 Python events) |
| Rules shown running in a test log | 7 of 8 |
| Security | enabled; 11 role(s), 2 row-level grant(s) |
| Messages and APIs | 2 Kafka topic(s) in, 2 out; 0 HTTP endpoint(s) |
| Kafka | live (localhost:9192): subscribe tested through the broker; outbound messages checked in the log |

_Status: ✅ every requirement is implemented and tested, all scenarios pass, and the results are current. ⚠ a requirement is untested or unimplemented, there is no test run, or files changed since the last run. ❌ a scenario failed. This reports what was traced and tested, not that the system is correct._

**About this project** _(from [readme.md](../../../readme.md))_

This app illustrates using IntegrationServices for B2B push-style integrations with APIs, and internal integration with messages.

**basic_demo_eai** is a single API Logic Server providing APIs *and logic* — it both
subscribes and publishes, so there's no second project to stand up:

1. **Order Logic:** enforcing database integrity (Check Credit) and application
   integration (notify shipping)

2. A **Custom API** (`OrderB2B`), matching an agreed-upon format for B2B partners

3. **Kafka Subscribe:** listens on topic `order_b2b` for inbound orders from a
   message broker

4. **Kafka Publish:** publishes to topic `order_shipping` when an order ships —
   consumed by whatever downstream shipping system you plug in (not part of this
   demo)

5. **Standard APIs** for ad-hoc integration, user interfaces, etc

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

Every requirement should have rules that implement it, and tests that prove it. This section checks that chain in both directions: a requirement missing rules or tests is a gap, and rules or tests that belong to no requirement are flagged too. The matching uses the `Feature:` names and `§N` tags that requirements, code and tests share.


&nbsp;

### Coverage summary

| Measure | Result |
|---|---|
| Requirements | 5 |
| Implemented (at least one file) | 5 of 5 |
| Tested (at least one scenario) | 5 of 5 |
| Implementation not traced to a requirement | `api/api_discovery/authentication_expose_api_models.py`, `logic/logic_discovery/system/all_classes_stamping.py` |
| Tests not traced to a requirement | none |
| Test results (last run) | ✅ 12 passed, 0 failed; took 3.0 s |
| Scenarios with a logic log | 12 of 12 |
| Rules seen in at least one scenario's log | 7 of 8 (1 not counted: the engine's log does not name `all classes.early_row_event → handle_all()`, so it cannot be matched) |

_Test results are as current as the last run (see the header). A gap is any requirement with no implementation or no test._

<details markdown>
<summary>How to read this table</summary>

Test results are read from `logs/behave.log`, so they are only as current as that run. Not recorded here: which version of a requirement the code was built against, and which clause of a requirement a given rule serves.

</details>



&nbsp;

### Traceability matrix

| Requirement | Implemented by | Rules | Tests |
|---|---|---|---|
| §1 Business Logic — Check Credit | [logic/logic_discovery/check_credit.py](../../../logic/logic_discovery/check_credit.py) | 5 | ✅ 3 scenario(s): 3 passed |
| §2 B2B API — Accept orders from external partners | [api/api_discovery/order_b2b_service.py](../../../api/api_discovery/order_b2b_service.py) | 0 | ✅ 2 scenario(s): 2 passed |
| §3 Kafka Subscribe — Inbound orders from sales channel | [logic/logic_discovery/kafka_subscribe_order.py](../../../logic/logic_discovery/kafka_subscribe_order.py)<br>[integration/kafka/kafka_subscribe_discovery/order_b2b.py](../../../integration/kafka/kafka_subscribe_discovery/order_b2b.py)<br>[integration/OrderB2bMapper.py](../../../integration/OrderB2bMapper.py)<br>[api/api_discovery/order_b2b_kafka_consume_debug.py](../../../api/api_discovery/order_b2b_kafka_consume_debug.py) | 1 | ✅ 4 scenario(s): 4 passed |
| §4 Kafka Publish — Notify shipping on dispatch | [logic/logic_discovery/kafka_publish_shipping.py](../../../logic/logic_discovery/kafka_publish_shipping.py)<br>[integration/kafka/kafka_publish_discovery/order_shipping.py](../../../integration/kafka/kafka_publish_discovery/order_shipping.py) | 1 | ✅ 2 scenario(s): 2 passed |
| §5 Security | [security/declare_security.py](../../../security/declare_security.py) | 0 | ✅ 1 scenario(s): 1 passed |


&nbsp;

### Rule coverage by tests

| Rule | Requirement | Seen in |
|---|---|---|
| `Customer: balance <= credit_limit` | §1 Business Logic — Check Credit | 2: Order beyond the credit limit is rejected; Check Credit is enforced on the Kafka path |
| `Customer.balance = sum(Order.amount_total) where date_shipped is None` | §1 Business Logic — Check Credit | 9: Accept order from external partner; Order within the credit limit is accepted; Order beyond the credit limit is rejected; +6 more |
| `Order.amount_total = sum(Item.amount)` | §1 Business Logic — Check Credit | 9: Accept order from external partner; Order within the credit limit is accepted; Order beyond the credit limit is rejected; +6 more |
| `Item.amount = quantity * unit_price` | §1 Business Logic — Check Credit | 9: Accept order from external partner; Order within the credit limit is accepted; Order beyond the credit limit is rejected; +6 more |
| `Item.unit_price = copy of Product.unit_price` | §1 Business Logic — Check Credit | 9: Accept order from external partner; Order within the credit limit is accepted; Order beyond the credit limit is rejected; +6 more |
| `Order.after_flush_row_event → _send_order_to_kafka()` | §4 Kafka Publish — Notify shipping on dispatch | 7: Accept order from external partner; Order within the credit limit is accepted; Shipping an order removes it from the customer balance; +4 more |
| `OrderB2bMessage.after_flush_row_event → _publish_order_b2b_blob()` | §3 Kafka Subscribe — Inbound orders from sales channel | 4: Accept inbound orders from sales channel; Check Credit is enforced on the Kafka path; Message for an unknown account is rejected; +1 more |
| `all classes.early_row_event → handle_all()` | (none) | n/a - cannot be matched to the engine's log |

_"Seen" means the engine's log shows the rule ran, not proof that it took effect._

<details markdown>
<summary>How to read this table</summary>

"Seen" means the engine reported running the rule in that scenario's logic log. A scenario can only contribute if it has a log (see the coverage summary): a test that does not open one writes into whichever log was open last, and its rules are then credited to that scenario, or to the shared log. An event's function runs on every commit of its class, and its own condition decides whether it acts, so seen does not mean it took effect. A constraint appears in the log only when it rejects a transaction, so it is seen only in scenarios that make it reject. "Not seen" therefore means no log shows it, not that no test ran it.

</details>



&nbsp;

### Requirements in detail

**8 rules** in 4 files: 5 declarative (sum, count, copy, formula and constraint expressions), 0 backed by a Python function, 3 events (Python).

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
python system/ApiLogicServer-Internal-Dev/logic_diagram_gv.py demo_eai --each
```

Each diagram is saved under `docs/requirements/<name>/logic_diagrams/`. Then regenerate this report (`python requirements_traceability_report.py run`, from `test/api_logic_server_behave`).

</details>

&nbsp;


#### §1 Business Logic — Check Credit

Tests: ✅ 3 scenario(s): 3 passed

```
Feature: Check Credit

  Scenario: Place an order
    Given a customer with a credit limit
    When an order is placed
    Then copy the price from the product
    And multiply by quantity to get the item amount
    And sum item amounts to get the order total
    And sum unpaid order totals to get the customer balance
    And reject if balance exceeds the credit limit
```

| Rule / item | Type | Logic | Description | Where |
|---|---|---|---|---|
| `Customer: balance <= credit_limit` | constraint | declarative | Error: balance ({row.balance}) exceeds credit limit ({row.credit_limit}) | [check_credit.py](../../../logic/logic_discovery/check_credit.py) |
| `Customer.balance = sum(Order.amount_total) where date_shipped is None` | sum | declarative |  | [check_credit.py](../../../logic/logic_discovery/check_credit.py) |
| `Order.amount_total = sum(Item.amount)` | sum | declarative |  | [check_credit.py](../../../logic/logic_discovery/check_credit.py) |
| `Item.amount = quantity * unit_price` | formula | declarative |  | [check_credit.py](../../../logic/logic_discovery/check_credit.py) |
| `Item.unit_price = copy of Product.unit_price` | copy | declarative |  | [check_credit.py](../../../logic/logic_discovery/check_credit.py) |

<details markdown>
<summary>Logic diagram: check_credit</summary>

![logic diagram: check_credit](../../../docs/requirements/check_credit/logic_diagrams/logic_diagram_check_credit.svg)

</details>

#### §2 B2B API — Accept orders from external partners

Tests: ✅ 2 scenario(s): 2 passed

```
Feature: B2B Order Integration

  Scenario: Accept order from external partner
    Given an inbound B2B order in partner format (message_formats/order_b2b.json)
    When the order is received via a Custom API endpoint named OrderB2B
    Then map Account to Customer by name
    And map Items.Name to Product by name
    And map Items.QuantityOrdered to Item.quantity
```

| Rule / item | Type | Logic | Description | Where |
|---|---|---|---|---|
| `order_b2b_service.py` | module |  | Feature: B2B Order Integration | [order_b2b_service.py](../../../api/api_discovery/order_b2b_service.py) |

#### §3 Kafka Subscribe — Inbound orders from sales channel

Tests: ✅ 4 scenario(s): 4 passed

```
Feature: Kafka Subscribe Order Integration

  Scenario: Accept inbound orders from sales channel
    Given an inbound order message in JSON format (message_formats/order_b2b.json)
    When the message is received from Kafka topic order_b2b
    Then map Account to Customer by name
    And map Items.Name to Product by name
    And map Items.QuantityOrdered to Item.quantity
```

| Rule / item | Type | Logic | Description | Where |
|---|---|---|---|---|
| `OrderB2bMessage.after_flush_row_event → _publish_order_b2b_blob()` | after_flush_row_event | event (Python) | OrderB2bMessage event: after Tx 1 commits the blob, publishes its payload to order_b2b_processed so Consumer 2 parses it in a clean Tx 2 (skipped when already processed, i.e. the debug path). | [kafka_subscribe_order.py](../../../logic/logic_discovery/kafka_subscribe_order.py) |
| `Kafka in: order_b2b` | kafka | handler (Python) | Kafka subscribe order_b2b (Consumer 1): saves the raw payload as a blob row and commits (Tx 1). | [order_b2b.py](../../../integration/kafka/kafka_subscribe_discovery/order_b2b.py) |
| `Kafka in: order_b2b_processed` | kafka | handler (Python) | Kafka subscribe order_b2b_processed (Consumer 2): parses and persists the order in a clean Tx 2. | [order_b2b.py](../../../integration/kafka/kafka_subscribe_discovery/order_b2b.py) |
| `OrderB2bMapper.py` | module |  | Feature: Kafka Subscribe Order Integration | [OrderB2bMapper.py](../../../integration/OrderB2bMapper.py) |
| `order_b2b_kafka_consume_debug.py` | module |  | Feature: Kafka Subscribe Order Integration | [order_b2b_kafka_consume_debug.py](../../../api/api_discovery/order_b2b_kafka_consume_debug.py) |

<details markdown>
<summary>Logic diagram: kafka_subscribe_order</summary>

![logic diagram: kafka_subscribe_order](../../../docs/requirements/kafka_subscribe_order/logic_diagrams/logic_diagram_kafka_subscribe_order.svg)

</details>

#### §4 Kafka Publish — Notify shipping on dispatch

Tests: ✅ 2 scenario(s): 2 passed

```
Feature: Kafka Publish Shipping Notification

  Scenario: Notify shipping when an order is dispatched
    Given an Order exists
    When date_shipped is set
    Then publish to Kafka topic order_shipping
    And use message_formats/order_shipping.json as the message shape
    And use by-example publish rather than key-only publish
```

| Rule / item | Type | Logic | Description | Where |
|---|---|---|---|---|
| `Order.after_flush_row_event → _send_order_to_kafka()` | after_flush_row_event | event (Python) | Order publish: sends the Order to Kafka topic order_shipping when date_shipped is first set or changes, using the by-example message shape in message_formats/order_shipping.json. | [kafka_publish_shipping.py](../../../logic/logic_discovery/kafka_publish_shipping.py) |
| `order_shipping.py` | module |  | Feature: Kafka Publish Shipping Notification | [order_shipping.py](../../../integration/kafka/kafka_publish_discovery/order_shipping.py) |

<details markdown>
<summary>Logic diagram: kafka_publish_shipping</summary>

![logic diagram: kafka_publish_shipping](../../../docs/requirements/kafka_publish_shipping/logic_diagrams/logic_diagram_kafka_publish_shipping.svg)

</details>

#### §5 Security

Tests: ✅ 1 scenario(s): 1 passed

```
Feature: Row-Level Security
  Scenario: Sales role sees limited customers
    Given a user with the sales role
    When querying the Customer list
    Then only return customers where credit_limit >= 3000 or balance > 0
```

| Rule / item | Type | Logic | Description | Where |
|---|---|---|---|---|
| `Grant on Customer to role sales: credit_limit >= 3000` | grant | declarative |  | [declare_security.py](../../../security/declare_security.py) |
| `Grant on Customer to role sales: balance > 0` | grant | declarative |  | [declare_security.py](../../../security/declare_security.py) |

#### Rules not traced to a requirement

| Rule / item | Type | Logic | Description | Where |
|---|---|---|---|---|
| `all classes.early_row_event → handle_all()` | early_row_event_all_classes | event (Python) | Generic handler - executed for every row update across all classes. | [all_classes_stamping.py](../../../logic/logic_discovery/system/all_classes_stamping.py) |


&nbsp;
&nbsp;

## Data Model

The tables the rules run over. Shaded columns are derived by rules — no code writes them.

![db diagram](db_diagram.generated.svg)

_Generated from `docs/db.dbml` (parents above children; shaded rows are derived by rules). To use your own layout, save it as `docs/db_diagram.png`._



&nbsp;

### Derived columns

| Table | Column | Rule | Definition |
|---|---|---|---|
| Customer | balance | sum | `Customer.balance = sum(Order.amount_total) where date_shipped is None` |
| Order | amount_total | sum | `Order.amount_total = sum(Item.amount)` |
| Item | amount | formula | `Item.amount = quantity * unit_price` |
| Item | unit_price | copy | `Item.unit_price = copy of Product.unit_price` |


&nbsp;
&nbsp;

## Security (RBAC)

Who can do what: each role's permissions, and which rows each role can see.

**Security enabled: yes** (`SECURITY_ENABLED` in `config/default.env`).


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
| sales | ✅ | — | — | — |


&nbsp;

### Row-level grants (Grant)

| Table | Role | Filter | Requirement |
|---|---|---|---|
| Customer | sales | `credit_limit >= 3000` |  |
| Customer | sales | `balance > 0` |  |


&nbsp;
&nbsp;

## Messages and APIs

How data enters and leaves beyond the standard API: Kafka topics in and out, custom HTTP endpoints — and whether any test touches each one.

**Kafka mode: live (localhost:9192).** The tests sent inbound messages through a real broker: `/consume_debug` published them to topic `order_b2b`, the server's consumers processed them, and the tests then checked the results. Outbound `order_shipping` messages are checked in the server log, not read back from the topic.

| Direction | Channel | Name | Tests mention it | Handler | Tables created | Message shape | Requirement |
|---|---|---|---|---|---|---|---|
| ➡ in | Kafka | `order_b2b` | ✅ live | `order_b2b()` - Kafka subscribe order_b2b (Consumer 1): saves the raw payload as a blob row and commits (Tx 1). | OrderB2bMessage | [order_b2b.json](../../../integration/kafka/message_formats/order_b2b.json) | §3 Kafka Subscribe — Inbound orders from sales channel |
| ➡ in | Kafka | `order_b2b_processed` | ✅ live | `order_b2b_processed()` - Kafka subscribe order_b2b_processed (Consumer 2): parses and persists the order in a clean Tx 2. | Item, Order, OrderB2bMessage |  | §3 Kafka Subscribe — Inbound orders from sales channel |
| ⬅ out | Kafka | `order_shipping` | ⚠ message checked in the log, not on the topic | Order.after_flush_row_event → _send_order_to_kafka() - Order publish: sends the Order to Kafka topic order_shipping when date_shipped is first set or changes, using the by-example message shape in message_formats/order_shipping.json. |  | [order_shipping.json](../../../integration/kafka/message_formats/order_shipping.json) | §4 Kafka Publish — Notify shipping on dispatch |
| ⬅ out | Kafka | `order_b2b_processed` | ✅ live | OrderB2bMessage.after_flush_row_event → _publish_order_b2b_blob() - OrderB2bMessage event: after Tx 1 commits the blob, publishes its payload to order_b2b_processed so Consumer 2 parses it in a clean Tx 2 (skipped when already processed, i.e. the debug path). |  |  | §3 Kafka Subscribe — Inbound orders from sales channel |

_"Tests mention it" checks the test sources, not delivery._

<details markdown>
<summary>How to read this column</summary>

A passing scenario proves a message reached a topic or an endpoint only if its steps look for it there. A handler that ran (see the logic log) is weaker evidence than a step that consumes the message. Channels no test mentions are flagged.

</details>

<details markdown>
<summary>How to read this table</summary>

Topics and endpoints are read from the discovery folders. The condition that triggers an outbound message lives in Python (see the rules under each requirement); here it is described by the handler's docstring. "Tables created" lists rows the handler's code constructs, following its calls within the project; blank means none were found, not that none exist.

</details>


<details markdown>
<summary>Message shape: order_b2b</summary>

```json
{
  "Account": "Alice",
  "Notes": "Kafka order from sales",
  "Items": [
    { "Name": "Widget",  "QuantityOrdered": 1 },
    { "Name": "Gadget",  "QuantityOrdered": 2 }
  ]
}
```
</details>

<details markdown>
<summary>Message shape: order_shipping</summary>

```json
{
  "order_id": 1,
  "order_date": "2026-04-06",
  "customer_name": "Alfreds Futterkiste",
  "total": 100.00,
  "items": [
    { "quantity": 2, "product_name": "Chai", "unit_price": 25.00 }
  ]
}
```
</details>


&nbsp;
&nbsp;

## Tests and Results

**✅ 12 scenario(s): 12 passed, 0 failed; took 3.0 s** (from the last run, `logs/behave.log`).

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
- B2B Order Integration
- Kafka Subscribe Order Integration
- Kafka Publish Shipping Notification
- Row-Level Security

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

### Feature: B2B Order Integration  

&nbsp;
&nbsp;

#### Scenario: Accept order from external partner ✅ (0.04 s)
&emsp;  Scenario: Accept order from external partner  
&emsp;&emsp;    Given a customer with a credit limit of 1000  
&emsp;&emsp;    When a partner sends an order for 1 Widget and 1 Gadget by customer name  
&emsp;&emsp;    Then the order is accepted  
&emsp;&emsp;    And the order has 2 items looked up by product name  
&emsp;&emsp;    And the customer balance is 240  

<details markdown>
<summary>Rules exercised and logic log (1 transaction)</summary>


&nbsp;
&nbsp;


**Rules Used** in Scenario: Accept order from external partner
```
  Customer  
    1. Derive Customer.balance as Sum(Order.amount_total Where Rule.sum(derive=models.Customer.balance, as_sum_of=models.Order.amount_total, where=lambda row: row.date_shipped is None))  
  Item  
    2. Derive Item.unit_price as Copy(product.unit_price)  
    3. Derive Item.amount as Formula (1): Rule.formula(derive=models.Item.amount, as_expres [...]  
  Order  
    4. Derive Order.amount_total as Sum(Item.amount Where  - None)  
    5. RowEvent Order._send_order_to_kafka()  
```
**Logic Log** in Scenario: Accept order from external partner (1 transaction)
```
Logic Phase:		ROW LOGIC		(session=0x10e4969e0) (sqlalchemy before_flush)			 - 2026-10-24 09:59:26,845 - logic_logger - INFO
..Product[1] {Update - client} id: 1, name: Gadget, count_suppliers: 0, unit_price: 150.0000000000  row: 0x10e65d080  session: 0x10e4969e0  ins_upd_dlt: upd, initial: upd - 2026-10-24 09:59:26,845 - logic_logger - INFO
..Order[None] {Insert - client} id: None, notes: behave, customer_id: 138, CreatedOn: 2026-10-24, date_shipped: None, amount_total: None  row: 0x10e41fcd0  session: 0x10e4969e0  ins_upd_dlt: ins, initial: ins - 2026-10-24 09:59:26,845 - logic_logger - INFO
..Order[None] {server aggregate_defaults: amount_total } id: None, notes: behave, customer_id: 138, CreatedOn: 2026-10-24, date_shipped: None, amount_total: 0  row: 0x10e41fcd0  session: 0x10e4969e0  ins_upd_dlt: ins, initial: ins - 2026-10-24 09:59:26,845 - logic_logger - INFO
..Item[None] {Insert - client} id: None, order_id: None, product_id: 2, quantity: 1, amount: None, unit_price: None  row: 0x10e4130d0  session: 0x10e4969e0  ins_upd_dlt: ins, initial: ins - 2026-10-24 09:59:26,846 - logic_logger - INFO
..Item[None] {copy_rules for role: product - unit_price} id: None, order_id: None, product_id: 2, quantity: 1, amount: None, unit_price: 90.0000000000  row: 0x10e4130d0  session: 0x10e4969e0  ins_upd_dlt: ins, initial: ins - 2026-10-24 09:59:26,846 - logic_logger - INFO
..Item[None] {Formula amount} id: None, order_id: None, product_id: 2, quantity: 1, amount: 90.0000000000, unit_price: 90.0000000000  row: 0x10e4130d0  session: 0x10e4969e0  ins_upd_dlt: ins, initial: ins - 2026-10-24 09:59:26,846 - logic_logger - INFO
....Order[None] {Update - Adjusting order: amount_total} id: None, notes: behave, customer_id: 138, CreatedOn: 2026-10-24, date_shipped: None, amount_total:  [0-->] 90.0000000000  row: 0x10e41fcd0  session: 0x10e4969e0  ins_upd_dlt: upd, initial: upd - 2026-10-24 09:59:26,846 - logic_logger - INFO
......Customer[138] {Update - Adjusting customer: balance} id: 138, name: Credit 1792861166826, balance:  [0E-10-->] 90.0000000000, credit_limit: 1000.0000000000, email: None, email_opt_out: None  row: 0x10e43c750  session: 0x10e4969e0  ins_upd_dlt: upd, initial: upd - 2026-10-24 09:59:26,846 - logic_logger - INFO
..Item[None] {Insert - client} id: None, order_id: None, product_id: None, quantity: 1, amount: None, unit_price: None  row: 0x10e399bd0  session: 0x10e4969e0  ins_upd_dlt: ins, initial: ins - 2026-10-24 09:59:26,846 - logic_logger - INFO
..Item[None] {copy_rules for role: product - unit_price} id: None, order_id: None, product_id: None, quantity: 1, amount: None, unit_price: 150.0000000000  row: 0x10e399bd0  session: 0x10e4969e0  ins_upd_dlt: ins, initial: ins - 2026-10-24 09:59:26,847 - logic_logger - INFO
..Item[None] {Formula amount} id: None, order_id: None, product_id: None, quantity: 1, amount: 150.0000000000, unit_price: 150.0000000000  row: 0x10e399bd0  session: 0x10e4969e0  ins_upd_dlt: ins, initial: ins - 2026-10-24 09:59:26,847 - logic_logger - INFO
....Order[None] {Update - Adjusting order: amount_total} id: None, notes: behave, customer_id: 138, CreatedOn: 2026-10-24, date_shipped: None, amount_total:  [90.0000000000-->] 240.0000000000  row: 0x10e41fcd0  session: 0x10e4969e0  ins_upd_dlt: upd, initial: upd - 2026-10-24 09:59:26,847 - logic_logger - INFO
......Customer[138] {Update - Adjusting customer: balance} id: 138, name: Credit 1792861166826, balance:  [90.0000000000-->] 240.0000000000, credit_limit: 1000.0000000000, email: None, email_opt_out: None  row: 0x10e43c750  session: 0x10e4969e0  ins_upd_dlt: upd, initial: upd - 2026-10-24 09:59:26,847 - logic_logger - INFO
Logic Phase:		COMMIT LOGIC		(session=0x10e4969e0)   										 - 2026-10-24 09:59:26,847 - logic_logger - INFO
Logic Phase:		AFTER_FLUSH LOGIC	(session=0x10e4969e0)   										 - 2026-10-24 09:59:26,849 - logic_logger - INFO
..Order[96] {AfterFlush Event} id: 96, notes: behave, customer_id: 138, CreatedOn: 2026-10-24, date_shipped: None, amount_total: 240.0000000000  row: 0x10e41fcd0  session: 0x10e4969e0  ins_upd_dlt: ins, initial: ins - 2026-10-24 09:59:26,849 - logic_logger - INFO

```
</details>

&nbsp;
&nbsp;

#### Scenario: Partner order for an unknown customer is rejected ✅ (0.01 s)
&emsp;  Scenario: Partner order for an unknown customer is rejected  
&emsp;&emsp;    Given a partner order addressed to an unknown account  
&emsp;&emsp;    When the partner order is sent  
&emsp;&emsp;    Then the order is rejected  

_No rules fired in this scenario's logic log._

&nbsp;
&nbsp;

### Feature: Check Credit  

&nbsp;
&nbsp;

#### Scenario: Order within the credit limit is accepted ✅ (0.03 s)
&emsp;  Scenario: Order within the credit limit is accepted  
&emsp;&emsp;    Given a customer with a credit limit of 1000  
&emsp;&emsp;    When an order for 2 Widget is placed through the B2B API  
&emsp;&emsp;    Then the order is accepted  
&emsp;&emsp;    And the item unit price was copied from the product as 90  
&emsp;&emsp;    And the item amount is 180 and the order total is 180  
&emsp;&emsp;    And the customer balance is 180  

<details markdown>
<summary>Rules exercised and logic log (1 transaction)</summary>


&nbsp;
&nbsp;


**Rules Used** in Scenario: Order within the credit limit is accepted
```
  Customer  
    1. Derive Customer.balance as Sum(Order.amount_total Where Rule.sum(derive=models.Customer.balance, as_sum_of=models.Order.amount_total, where=lambda row: row.date_shipped is None))  
  Item  
    2. Derive Item.unit_price as Copy(product.unit_price)  
    3. Derive Item.amount as Formula (1): Rule.formula(derive=models.Item.amount, as_expres [...]  
  Order  
    4. Derive Order.amount_total as Sum(Item.amount Where  - None)  
    5. RowEvent Order._send_order_to_kafka()  
```
**Logic Log** in Scenario: Order within the credit limit is accepted (1 transaction)
```
Logic Phase:		ROW LOGIC		(session=0x10e466360) (sqlalchemy before_flush)			 - 2026-10-24 09:59:26,878 - logic_logger - INFO
..Product[2] {Update - client} id: 2, name: Widget, count_suppliers: 0, unit_price: 90.0000000000  row: 0x10e6bec80  session: 0x10e466360  ins_upd_dlt: upd, initial: upd - 2026-10-24 09:59:26,878 - logic_logger - INFO
..Order[None] {Insert - client} id: None, notes: behave, customer_id: 139, CreatedOn: 2026-10-24, date_shipped: None, amount_total: None  row: 0x10e3ddf50  session: 0x10e466360  ins_upd_dlt: ins, initial: ins - 2026-10-24 09:59:26,878 - logic_logger - INFO
..Order[None] {server aggregate_defaults: amount_total } id: None, notes: behave, customer_id: 139, CreatedOn: 2026-10-24, date_shipped: None, amount_total: 0  row: 0x10e3ddf50  session: 0x10e466360  ins_upd_dlt: ins, initial: ins - 2026-10-24 09:59:26,878 - logic_logger - INFO
..Item[None] {Insert - client} id: None, order_id: None, product_id: None, quantity: 2, amount: None, unit_price: None  row: 0x10e44d750  session: 0x10e466360  ins_upd_dlt: ins, initial: ins - 2026-10-24 09:59:26,879 - logic_logger - INFO
..Item[None] {copy_rules for role: product - unit_price} id: None, order_id: None, product_id: None, quantity: 2, amount: None, unit_price: 90.0000000000  row: 0x10e44d750  session: 0x10e466360  ins_upd_dlt: ins, initial: ins - 2026-10-24 09:59:26,879 - logic_logger - INFO
..Item[None] {Formula amount} id: None, order_id: None, product_id: None, quantity: 2, amount: 180.0000000000, unit_price: 90.0000000000  row: 0x10e44d750  session: 0x10e466360  ins_upd_dlt: ins, initial: ins - 2026-10-24 09:59:26,879 - logic_logger - INFO
....Order[None] {Update - Adjusting order: amount_total} id: None, notes: behave, customer_id: 139, CreatedOn: 2026-10-24, date_shipped: None, amount_total:  [0-->] 180.0000000000  row: 0x10e3ddf50  session: 0x10e466360  ins_upd_dlt: upd, initial: upd - 2026-10-24 09:59:26,879 - logic_logger - INFO
......Customer[139] {Update - Adjusting customer: balance} id: 139, name: Credit 1792861166869, balance:  [0E-10-->] 180.0000000000, credit_limit: 1000.0000000000, email: None, email_opt_out: None  row: 0x10e652750  session: 0x10e466360  ins_upd_dlt: upd, initial: upd - 2026-10-24 09:59:26,880 - logic_logger - INFO
Logic Phase:		COMMIT LOGIC		(session=0x10e466360)   										 - 2026-10-24 09:59:26,880 - logic_logger - INFO
Logic Phase:		AFTER_FLUSH LOGIC	(session=0x10e466360)   										 - 2026-10-24 09:59:26,881 - logic_logger - INFO
..Order[97] {AfterFlush Event} id: 97, notes: behave, customer_id: 139, CreatedOn: 2026-10-24, date_shipped: None, amount_total: 180.0000000000  row: 0x10e3ddf50  session: 0x10e466360  ins_upd_dlt: ins, initial: ins - 2026-10-24 09:59:26,881 - logic_logger - INFO

```
</details>

&nbsp;
&nbsp;

#### Scenario: Order beyond the credit limit is rejected ✅ (0.02 s)
&emsp;  Scenario: Order beyond the credit limit is rejected  
&emsp;&emsp;    Given a customer with a credit limit of 100  
&emsp;&emsp;    When an order for 2 Widget is placed through the B2B API  
&emsp;&emsp;    Then the order is rejected with a credit limit message  
&emsp;&emsp;    And the customer balance is 0  

<details markdown>
<summary>Rules exercised and logic log (1 transaction)</summary>


&nbsp;
&nbsp;


**Rules Used** in Scenario: Order beyond the credit limit is rejected
```
  Customer  
    1. Derive Customer.balance as Sum(Order.amount_total Where Rule.sum(derive=models.Customer.balance, as_sum_of=models.Order.amount_total, where=lambda row: row.date_shipped is None))  
    2. Constraint Function: None  
  Item  
    3. Derive Item.unit_price as Copy(product.unit_price)  
    4. Derive Item.amount as Formula (1): Rule.formula(derive=models.Item.amount, as_expres [...]  
  Order  
    5. Derive Order.amount_total as Sum(Item.amount Where  - None)  
```
**Logic Log** in Scenario: Order beyond the credit limit is rejected (1 transaction)
```
Logic Phase:		ROW LOGIC		(session=0x10e467790) (sqlalchemy before_flush)			 - 2026-10-24 09:59:26,908 - logic_logger - INFO
..Product[2] {Update - client} id: 2, name: Widget, count_suppliers: 0, unit_price: 90.0000000000  row: 0x10e7082f0  session: 0x10e467790  ins_upd_dlt: upd, initial: upd - 2026-10-24 09:59:26,908 - logic_logger - INFO
..Order[None] {Insert - client} id: None, notes: behave, customer_id: 140, CreatedOn: 2026-10-24, date_shipped: None, amount_total: None  row: 0x10e3d0b50  session: 0x10e467790  ins_upd_dlt: ins, initial: ins - 2026-10-24 09:59:26,908 - logic_logger - INFO
..Order[None] {server aggregate_defaults: amount_total } id: None, notes: behave, customer_id: 140, CreatedOn: 2026-10-24, date_shipped: None, amount_total: 0  row: 0x10e3d0b50  session: 0x10e467790  ins_upd_dlt: ins, initial: ins - 2026-10-24 09:59:26,908 - logic_logger - INFO
..Item[None] {Insert - client} id: None, order_id: None, product_id: None, quantity: 2, amount: None, unit_price: None  row: 0x10e4824d0  session: 0x10e467790  ins_upd_dlt: ins, initial: ins - 2026-10-24 09:59:26,908 - logic_logger - INFO
..Item[None] {copy_rules for role: product - unit_price} id: None, order_id: None, product_id: None, quantity: 2, amount: None, unit_price: 90.0000000000  row: 0x10e4824d0  session: 0x10e467790  ins_upd_dlt: ins, initial: ins - 2026-10-24 09:59:26,908 - logic_logger - INFO
..Item[None] {Formula amount} id: None, order_id: None, product_id: None, quantity: 2, amount: 180.0000000000, unit_price: 90.0000000000  row: 0x10e4824d0  session: 0x10e467790  ins_upd_dlt: ins, initial: ins - 2026-10-24 09:59:26,908 - logic_logger - INFO
....Order[None] {Update - Adjusting order: amount_total} id: None, notes: behave, customer_id: 140, CreatedOn: 2026-10-24, date_shipped: None, amount_total:  [0-->] 180.0000000000  row: 0x10e3d0b50  session: 0x10e467790  ins_upd_dlt: upd, initial: upd - 2026-10-24 09:59:26,909 - logic_logger - INFO
......Customer[140] {Update - Adjusting customer: balance} id: 140, name: Credit 1792861166899, balance:  [0E-10-->] 180.0000000000, credit_limit: 100.0000000000, email: None, email_opt_out: None  row: 0x10e69c150  session: 0x10e467790  ins_upd_dlt: upd, initial: upd - 2026-10-24 09:59:26,909 - logic_logger - INFO
......Customer[140] {Constraint Failure: balance (180.0000000000) exceeds credit limit (100.0000000000)} id: 140, name: Credit 1792861166899, balance:  [0E-10-->] 180.0000000000, credit_limit: 100.0000000000, email: None, email_opt_out: None  row: 0x10e69c150  session: 0x10e467790  ins_upd_dlt: upd, initial: upd - 2026-10-24 09:59:26,909 - logic_logger - INFO

```
</details>

&nbsp;
&nbsp;

#### Scenario: Shipping an order removes it from the customer balance ✅ (0.17 s)
&emsp;  Scenario: Shipping an order removes it from the customer balance  
&emsp;&emsp;    Given a customer with a credit limit of 1000  
&emsp;&emsp;    When an order for 2 Widget is placed through the B2B API  
&emsp;&emsp;    And the order is shipped  
&emsp;&emsp;    Then the customer balance is 0  

<details markdown>
<summary>Rules exercised and logic log (2 transactions)</summary>


&nbsp;
&nbsp;


**Rules Used** in Scenario: Shipping an order removes it from the customer balance
```
  Customer  
    1. Derive Customer.balance as Sum(Order.amount_total Where Rule.sum(derive=models.Customer.balance, as_sum_of=models.Order.amount_total, where=lambda row: row.date_shipped is None))  
  Item  
    2. Derive Item.unit_price as Copy(product.unit_price)  
    3. Derive Item.amount as Formula (1): Rule.formula(derive=models.Item.amount, as_expres [...]  
  Order  
    4. Derive Order.amount_total as Sum(Item.amount Where  - None)  
    5. RowEvent Order._send_order_to_kafka()  
```
**Logic Log** in Scenario: Shipping an order removes it from the customer balance (2 transactions)
```
Logic Phase:		ROW LOGIC		(session=0x10e467570) (sqlalchemy before_flush)			 - 2026-10-24 09:59:26,928 - logic_logger - INFO
..Product[2] {Update - client} id: 2, name: Widget, count_suppliers: 0, unit_price: 90.0000000000  row: 0x10e799860  session: 0x10e467570  ins_upd_dlt: upd, initial: upd - 2026-10-24 09:59:26,928 - logic_logger - INFO
..Order[None] {Insert - client} id: None, notes: behave, customer_id: 141, CreatedOn: 2026-10-24, date_shipped: None, amount_total: None  row: 0x10e7044d0  session: 0x10e467570  ins_upd_dlt: ins, initial: ins - 2026-10-24 09:59:26,928 - logic_logger - INFO
..Order[None] {server aggregate_defaults: amount_total } id: None, notes: behave, customer_id: 141, CreatedOn: 2026-10-24, date_shipped: None, amount_total: 0  row: 0x10e7044d0  session: 0x10e467570  ins_upd_dlt: ins, initial: ins - 2026-10-24 09:59:26,928 - logic_logger - INFO
..Item[None] {Insert - client} id: None, order_id: None, product_id: None, quantity: 2, amount: None, unit_price: None  row: 0x10e7049d0  session: 0x10e467570  ins_upd_dlt: ins, initial: ins - 2026-10-24 09:59:26,928 - logic_logger - INFO
..Item[None] {copy_rules for role: product - unit_price} id: None, order_id: None, product_id: None, quantity: 2, amount: None, unit_price: 90.0000000000  row: 0x10e7049d0  session: 0x10e467570  ins_upd_dlt: ins, initial: ins - 2026-10-24 09:59:26,929 - logic_logger - INFO
..Item[None] {Formula amount} id: None, order_id: None, product_id: None, quantity: 2, amount: 180.0000000000, unit_price: 90.0000000000  row: 0x10e7049d0  session: 0x10e467570  ins_upd_dlt: ins, initial: ins - 2026-10-24 09:59:26,929 - logic_logger - INFO
....Order[None] {Update - Adjusting order: amount_total} id: None, notes: behave, customer_id: 141, CreatedOn: 2026-10-24, date_shipped: None, amount_total:  [0-->] 180.0000000000  row: 0x10e7044d0  session: 0x10e467570  ins_upd_dlt: upd, initial: upd - 2026-10-24 09:59:26,929 - logic_logger - INFO
......Customer[141] {Update - Adjusting customer: balance} id: 141, name: Credit 1792861166920, balance:  [0E-10-->] 180.0000000000, credit_limit: 1000.0000000000, email: None, email_opt_out: None  row: 0x10e6c2cd0  session: 0x10e467570  ins_upd_dlt: upd, initial: upd - 2026-10-24 09:59:26,929 - logic_logger - INFO
Logic Phase:		COMMIT LOGIC		(session=0x10e467570)   										 - 2026-10-24 09:59:26,929 - logic_logger - INFO
Logic Phase:		AFTER_FLUSH LOGIC	(session=0x10e467570)   										 - 2026-10-24 09:59:26,930 - logic_logger - INFO
..Order[98] {AfterFlush Event} id: 98, notes: behave, customer_id: 141, CreatedOn: 2026-10-24, date_shipped: None, amount_total: 180.0000000000  row: 0x10e7044d0  session: 0x10e467570  ins_upd_dlt: ins, initial: ins - 2026-10-24 09:59:26,930 - logic_logger - INFO


Logic Phase:		ROW LOGIC		(session=0x10e467f00) (sqlalchemy before_flush)			 - 2026-10-24 09:59:26,935 - logic_logger - INFO
..Order[98] {Update - client} id: 98, notes: behave, customer_id: 141, CreatedOn: 2026-10-24, date_shipped:  [None-->] 2026-10-23 00:00:00, amount_total: 180.0000000000  row: 0x10e7a4850  session: 0x10e467f00  ins_upd_dlt: upd, initial: upd - 2026-10-24 09:59:26,935 - logic_logger - INFO
....Customer[141] {Update - Adjusting customer: balance} id: 141, name: Credit 1792861166920, balance:  [180.0000000000-->] 0E-10, credit_limit: 1000.0000000000, email: None, email_opt_out: None  row: 0x10e7a4dd0  session: 0x10e467f00  ins_upd_dlt: upd, initial: upd - 2026-10-24 09:59:26,936 - logic_logger - INFO
Logic Phase:		COMMIT LOGIC		(session=0x10e467f00)   										 - 2026-10-24 09:59:26,936 - logic_logger - INFO
Logic Phase:		AFTER_FLUSH LOGIC	(session=0x10e467f00)   										 - 2026-10-24 09:59:26,937 - logic_logger - INFO
..Order[98] {AfterFlush Event} id: 98, notes: behave, customer_id: 141, CreatedOn: 2026-10-24, date_shipped:  [None-->] 2026-10-23 00:00:00, amount_total: 180.0000000000  row: 0x10e7a4850  session: 0x10e467f00  ins_upd_dlt: upd, initial: upd - 2026-10-24 09:59:26,937 - logic_logger - INFO
..Order[98] {publish_kafka_message: topic='order_shipping', key={'id': 98}} id: 98, notes: behave, customer_id: 141, CreatedOn: 2026-10-24, date_shipped:  [None-->] 2026-10-23 00:00:00, amount_total: 180.0000000000  row: 0x10e7a4850  session: 0x10e467f00  ins_upd_dlt: upd, initial: upd - 2026-10-24 09:59:27,072 - logic_logger - INFO

```
</details>

&nbsp;
&nbsp;

### Feature: Kafka Publish Shipping Notification  

&nbsp;
&nbsp;

#### Scenario: Notify shipping when an order is dispatched ✅ (0.03 s)
&emsp;  Scenario: Notify shipping when an order is dispatched  
&emsp;&emsp;    Given a customer with a credit limit of 1000  
&emsp;&emsp;    When an order for 2 Widget is placed through the B2B API  
&emsp;&emsp;    And the order is shipped  
&emsp;&emsp;    Then an order_shipping message with the order, customer and items is published  

<details markdown>
<summary>Rules exercised and logic log (2 transactions)</summary>


&nbsp;
&nbsp;


**Rules Used** in Scenario: Notify shipping when an order is dispatched
```
  Customer  
    1. Derive Customer.balance as Sum(Order.amount_total Where Rule.sum(derive=models.Customer.balance, as_sum_of=models.Order.amount_total, where=lambda row: row.date_shipped is None))  
  Item  
    2. Derive Item.unit_price as Copy(product.unit_price)  
    3. Derive Item.amount as Formula (1): Rule.formula(derive=models.Item.amount, as_expres [...]  
  Order  
    4. Derive Order.amount_total as Sum(Item.amount Where  - None)  
    5. RowEvent Order._send_order_to_kafka()  
```
**Logic Log** in Scenario: Notify shipping when an order is dispatched (2 transactions)
```
Logic Phase:		ROW LOGIC		(session=0x10e7b5370) (sqlalchemy before_flush)			 - 2026-10-24 09:59:27,102 - logic_logger - INFO
..Product[2] {Update - client} id: 2, name: Widget, count_suppliers: 0, unit_price: 90.0000000000  row: 0x10e7c8830  session: 0x10e7b5370  ins_upd_dlt: upd, initial: upd - 2026-10-24 09:59:27,102 - logic_logger - INFO
..Order[None] {Insert - client} id: None, notes: behave, customer_id: 142, CreatedOn: 2026-10-24, date_shipped: None, amount_total: None  row: 0x10e69c7d0  session: 0x10e7b5370  ins_upd_dlt: ins, initial: ins - 2026-10-24 09:59:27,102 - logic_logger - INFO
..Order[None] {server aggregate_defaults: amount_total } id: None, notes: behave, customer_id: 142, CreatedOn: 2026-10-24, date_shipped: None, amount_total: 0  row: 0x10e69c7d0  session: 0x10e7b5370  ins_upd_dlt: ins, initial: ins - 2026-10-24 09:59:27,102 - logic_logger - INFO
..Item[None] {Insert - client} id: None, order_id: None, product_id: None, quantity: 2, amount: None, unit_price: None  row: 0x10e7a45d0  session: 0x10e7b5370  ins_upd_dlt: ins, initial: ins - 2026-10-24 09:59:27,103 - logic_logger - INFO
..Item[None] {copy_rules for role: product - unit_price} id: None, order_id: None, product_id: None, quantity: 2, amount: None, unit_price: 90.0000000000  row: 0x10e7a45d0  session: 0x10e7b5370  ins_upd_dlt: ins, initial: ins - 2026-10-24 09:59:27,103 - logic_logger - INFO
..Item[None] {Formula amount} id: None, order_id: None, product_id: None, quantity: 2, amount: 180.0000000000, unit_price: 90.0000000000  row: 0x10e7a45d0  session: 0x10e7b5370  ins_upd_dlt: ins, initial: ins - 2026-10-24 09:59:27,103 - logic_logger - INFO
....Order[None] {Update - Adjusting order: amount_total} id: None, notes: behave, customer_id: 142, CreatedOn: 2026-10-24, date_shipped: None, amount_total:  [0-->] 180.0000000000  row: 0x10e69c7d0  session: 0x10e7b5370  ins_upd_dlt: upd, initial: upd - 2026-10-24 09:59:27,103 - logic_logger - INFO
......Customer[142] {Update - Adjusting customer: balance} id: 142, name: Credit 1792861167090, balance:  [0E-10-->] 180.0000000000, credit_limit: 1000.0000000000, email: None, email_opt_out: None  row: 0x10e7a5b50  session: 0x10e7b5370  ins_upd_dlt: upd, initial: upd - 2026-10-24 09:59:27,103 - logic_logger - INFO
Logic Phase:		COMMIT LOGIC		(session=0x10e7b5370)   										 - 2026-10-24 09:59:27,103 - logic_logger - INFO
Logic Phase:		AFTER_FLUSH LOGIC	(session=0x10e7b5370)   										 - 2026-10-24 09:59:27,104 - logic_logger - INFO
..Order[99] {AfterFlush Event} id: 99, notes: behave, customer_id: 142, CreatedOn: 2026-10-24, date_shipped: None, amount_total: 180.0000000000  row: 0x10e69c7d0  session: 0x10e7b5370  ins_upd_dlt: ins, initial: ins - 2026-10-24 09:59:27,104 - logic_logger - INFO


Logic Phase:		ROW LOGIC		(session=0x10e7b56a0) (sqlalchemy before_flush)			 - 2026-10-24 09:59:27,110 - logic_logger - INFO
..Order[99] {Update - client} id: 99, notes: behave, customer_id: 142, CreatedOn: 2026-10-24, date_shipped:  [None-->] 2026-10-23 00:00:00, amount_total: 180.0000000000  row: 0x10e6c16d0  session: 0x10e7b56a0  ins_upd_dlt: upd, initial: upd - 2026-10-24 09:59:27,110 - logic_logger - INFO
....Customer[142] {Update - Adjusting customer: balance} id: 142, name: Credit 1792861167090, balance:  [180.0000000000-->] 0E-10, credit_limit: 1000.0000000000, email: None, email_opt_out: None  row: 0x10e7d9c50  session: 0x10e7b56a0  ins_upd_dlt: upd, initial: upd - 2026-10-24 09:59:27,111 - logic_logger - INFO
Logic Phase:		COMMIT LOGIC		(session=0x10e7b56a0)   										 - 2026-10-24 09:59:27,111 - logic_logger - INFO
Logic Phase:		AFTER_FLUSH LOGIC	(session=0x10e7b56a0)   										 - 2026-10-24 09:59:27,112 - logic_logger - INFO
..Order[99] {AfterFlush Event} id: 99, notes: behave, customer_id: 142, CreatedOn: 2026-10-24, date_shipped:  [None-->] 2026-10-23 00:00:00, amount_total: 180.0000000000  row: 0x10e6c16d0  session: 0x10e7b56a0  ins_upd_dlt: upd, initial: upd - 2026-10-24 09:59:27,112 - logic_logger - INFO
..Order[99] {publish_kafka_message: topic='order_shipping', key={'id': 99}} id: 99, notes: behave, customer_id: 142, CreatedOn: 2026-10-24, date_shipped:  [None-->] 2026-10-23 00:00:00, amount_total: 180.0000000000  row: 0x10e6c16d0  session: 0x10e7b56a0  ins_upd_dlt: upd, initial: upd - 2026-10-24 09:59:27,114 - logic_logger - INFO

```
</details>

&nbsp;
&nbsp;

#### Scenario: Changing a shipped order does not publish again ✅ (0.03 s)
&emsp;  Scenario: Changing a shipped order does not publish again  
&emsp;&emsp;    Given a customer with a credit limit of 1000  
&emsp;&emsp;    When an order for 1 Widget is placed through the B2B API  
&emsp;&emsp;    And the order is shipped  
&emsp;&emsp;    And the order notes are changed  
&emsp;&emsp;    Then only one order_shipping message was published for the order  

<details markdown>
<summary>Rules exercised and logic log (3 transactions)</summary>


&nbsp;
&nbsp;


**Rules Used** in Scenario: Changing a shipped order does not publish again
```
  Customer  
    1. Derive Customer.balance as Sum(Order.amount_total Where Rule.sum(derive=models.Customer.balance, as_sum_of=models.Order.amount_total, where=lambda row: row.date_shipped is None))  
  Item  
    2. Derive Item.unit_price as Copy(product.unit_price)  
    3. Derive Item.amount as Formula (1): Rule.formula(derive=models.Item.amount, as_expres [...]  
  Order  
    4. Derive Order.amount_total as Sum(Item.amount Where  - None)  
    5. RowEvent Order._send_order_to_kafka()  
```
**Logic Log** in Scenario: Changing a shipped order does not publish again (3 transactions)
```
Logic Phase:		ROW LOGIC		(session=0x10e7b5590) (sqlalchemy before_flush)			 - 2026-10-24 09:59:27,130 - logic_logger - INFO
..Product[2] {Update - client} id: 2, name: Widget, count_suppliers: 0, unit_price: 90.0000000000  row: 0x10e7c9010  session: 0x10e7b5590  ins_upd_dlt: upd, initial: upd - 2026-10-24 09:59:27,130 - logic_logger - INFO
..Order[None] {Insert - client} id: None, notes: behave, customer_id: 143, CreatedOn: 2026-10-24, date_shipped: None, amount_total: None  row: 0x10e7a43d0  session: 0x10e7b5590  ins_upd_dlt: ins, initial: ins - 2026-10-24 09:59:27,131 - logic_logger - INFO
..Order[None] {server aggregate_defaults: amount_total } id: None, notes: behave, customer_id: 143, CreatedOn: 2026-10-24, date_shipped: None, amount_total: 0  row: 0x10e7a43d0  session: 0x10e7b5590  ins_upd_dlt: ins, initial: ins - 2026-10-24 09:59:27,131 - logic_logger - INFO
..Item[None] {Insert - client} id: None, order_id: None, product_id: None, quantity: 1, amount: None, unit_price: None  row: 0x10e4839d0  session: 0x10e7b5590  ins_upd_dlt: ins, initial: ins - 2026-10-24 09:59:27,131 - logic_logger - INFO
..Item[None] {copy_rules for role: product - unit_price} id: None, order_id: None, product_id: None, quantity: 1, amount: None, unit_price: 90.0000000000  row: 0x10e4839d0  session: 0x10e7b5590  ins_upd_dlt: ins, initial: ins - 2026-10-24 09:59:27,131 - logic_logger - INFO
..Item[None] {Formula amount} id: None, order_id: None, product_id: None, quantity: 1, amount: 90.0000000000, unit_price: 90.0000000000  row: 0x10e4839d0  session: 0x10e7b5590  ins_upd_dlt: ins, initial: ins - 2026-10-24 09:59:27,131 - logic_logger - INFO
....Order[None] {Update - Adjusting order: amount_total} id: None, notes: behave, customer_id: 143, CreatedOn: 2026-10-24, date_shipped: None, amount_total:  [0-->] 90.0000000000  row: 0x10e7a43d0  session: 0x10e7b5590  ins_upd_dlt: upd, initial: upd - 2026-10-24 09:59:27,131 - logic_logger - INFO
......Customer[143] {Update - Adjusting customer: balance} id: 143, name: Credit 1792861167121, balance:  [0E-10-->] 90.0000000000, credit_limit: 1000.0000000000, email: None, email_opt_out: None  row: 0x10e7a4750  session: 0x10e7b5590  ins_upd_dlt: upd, initial: upd - 2026-10-24 09:59:27,132 - logic_logger - INFO
Logic Phase:		COMMIT LOGIC		(session=0x10e7b5590)   										 - 2026-10-24 09:59:27,132 - logic_logger - INFO
Logic Phase:		AFTER_FLUSH LOGIC	(session=0x10e7b5590)   										 - 2026-10-24 09:59:27,133 - logic_logger - INFO
..Order[100] {AfterFlush Event} id: 100, notes: behave, customer_id: 143, CreatedOn: 2026-10-24, date_shipped: None, amount_total: 90.0000000000  row: 0x10e7a43d0  session: 0x10e7b5590  ins_upd_dlt: ins, initial: ins - 2026-10-24 09:59:27,133 - logic_logger - INFO


Logic Phase:		ROW LOGIC		(session=0x10e7b5480) (sqlalchemy before_flush)			 - 2026-10-24 09:59:27,137 - logic_logger - INFO
..Order[100] {Update - client} id: 100, notes: behave, customer_id: 143, CreatedOn: 2026-10-24, date_shipped:  [None-->] 2026-10-23 00:00:00, amount_total: 90.0000000000  row: 0x10f1b1150  session: 0x10e7b5480  ins_upd_dlt: upd, initial: upd - 2026-10-24 09:59:27,137 - logic_logger - INFO
....Customer[143] {Update - Adjusting customer: balance} id: 143, name: Credit 1792861167121, balance:  [90.0000000000-->] 0E-10, credit_limit: 1000.0000000000, email: None, email_opt_out: None  row: 0x10f1b1e50  session: 0x10e7b5480  ins_upd_dlt: upd, initial: upd - 2026-10-24 09:59:27,137 - logic_logger - INFO
Logic Phase:		COMMIT LOGIC		(session=0x10e7b5480)   										 - 2026-10-24 09:59:27,138 - logic_logger - INFO
Logic Phase:		AFTER_FLUSH LOGIC	(session=0x10e7b5480)   										 - 2026-10-24 09:59:27,138 - logic_logger - INFO
..Order[100] {AfterFlush Event} id: 100, notes: behave, customer_id: 143, CreatedOn: 2026-10-24, date_shipped:  [None-->] 2026-10-23 00:00:00, amount_total: 90.0000000000  row: 0x10f1b1150  session: 0x10e7b5480  ins_upd_dlt: upd, initial: upd - 2026-10-24 09:59:27,138 - logic_logger - INFO
..Order[100] {publish_kafka_message: topic='order_shipping', key={'id': 100}} id: 100, notes: behave, customer_id: 143, CreatedOn: 2026-10-24, date_shipped:  [None-->] 2026-10-23 00:00:00, amount_total: 90.0000000000  row: 0x10f1b1150  session: 0x10e7b5480  ins_upd_dlt: upd, initial: upd - 2026-10-24 09:59:27,143 - logic_logger - INFO


Logic Phase:		ROW LOGIC		(session=0x10e7b5e10) (sqlalchemy before_flush)			 - 2026-10-24 09:59:27,148 - logic_logger - INFO
..Order[100] {Update - client} id: 100, notes:  [behave-->] changed by behave, customer_id: 143, CreatedOn: 2026-10-24, date_shipped: 2026-10-23, amount_total: 90.0000000000  row: 0x10f1b1ed0  session: 0x10e7b5e10  ins_upd_dlt: upd, initial: upd - 2026-10-24 09:59:27,149 - logic_logger - INFO
Logic Phase:		COMMIT LOGIC		(session=0x10e7b5e10)   										 - 2026-10-24 09:59:27,149 - logic_logger - INFO
Logic Phase:		AFTER_FLUSH LOGIC	(session=0x10e7b5e10)   										 - 2026-10-24 09:59:27,149 - logic_logger - INFO
..Order[100] {AfterFlush Event} id: 100, notes:  [behave-->] changed by behave, customer_id: 143, CreatedOn: 2026-10-24, date_shipped: 2026-10-23, amount_total: 90.0000000000  row: 0x10f1b1ed0  session: 0x10e7b5e10  ins_upd_dlt: upd, initial: upd - 2026-10-24 09:59:27,149 - logic_logger - INFO

```
</details>

&nbsp;
&nbsp;

### Feature: Kafka Subscribe Order Integration  

&nbsp;
&nbsp;

#### Scenario: Accept inbound orders from sales channel ✅ (0.58 s)
&emsp;  Scenario: Accept inbound orders from sales channel  
&emsp;&emsp;    Given a customer with a credit limit of 1000  
&emsp;&emsp;    When an inbound order message for that customer is delivered to topic order_b2b  
&emsp;&emsp;    Then the message blob is stored and marked processed  
&emsp;&emsp;    And a new order exists with 2 items mapped by product name  
&emsp;&emsp;    And the customer balance is 390  

<details markdown>
<summary>Rules exercised and logic log (3 transactions)</summary>


&nbsp;
&nbsp;


**Rules Used** in Scenario: Accept inbound orders from sales channel
```
  OrderB2bMessage  
    1. RowEvent OrderB2bMessage._publish_order_b2b_blob()  
  Customer  
    2. Derive Customer.balance as Sum(Order.amount_total Where Rule.sum(derive=models.Customer.balance, as_sum_of=models.Order.amount_total, where=lambda row: row.date_shipped is None))  
  Item  
    3. Derive Item.unit_price as Copy(product.unit_price)  
    4. Derive Item.amount as Formula (1): Rule.formula(derive=models.Item.amount, as_expres [...]  
  Order  
    5. Derive Order.amount_total as Sum(Item.amount Where  - None)  
    6. RowEvent Order._send_order_to_kafka()  
```
**Logic Log** in Scenario: Accept inbound orders from sales channel (3 transactions)
```
Logic Phase:		ROW LOGIC		(session=0x10e7b6360) (sqlalchemy before_flush)			 - 2026-10-24 09:59:27,173 - logic_logger - INFO
..OrderB2bMessage[None] {Insert - client} id: None, received_at: 2026-10-24 09:59:27.171786, payload: {"Account": "Credit 1792861167154", "Notes": "Kafka order from behave", "Items": [{"Name": "Widget", "QuantityOrdered": 1}, {"Name": "Gadget", "QuantityOrdered": 2}]}, is_processed: False, error_text: None  row: 0x10e7e5f10  session: 0x10e7b6360  ins_upd_dlt: ins, initial: ins - 2026-10-24 09:59:27,173 - logic_logger - INFO
Logic Phase:		COMMIT LOGIC		(session=0x10e7b6360)   										 - 2026-10-24 09:59:27,175 - logic_logger - INFO
Logic Phase:		AFTER_FLUSH LOGIC	(session=0x10e7b6360)   										 - 2026-10-24 09:59:27,176 - logic_logger - INFO
..OrderB2bMessage[31] {AfterFlush Event} id: 31, received_at: 2026-10-24 09:59:27.171786, payload: {"Account": "Credit 1792861167154", "Notes": "Kafka order from behave", "Items": [{"Name": "Widget", "QuantityOrdered": 1}, {"Name": "Gadget", "QuantityOrdered": 2}]}, is_processed: False, error_text: None  row: 0x10e7e5f10  session: 0x10e7b6360  ins_upd_dlt: ins, initial: ins - 2026-10-24 09:59:27,176 - logic_logger - INFO


Logic Phase:		ROW LOGIC		(session=0x10e7b58c0) (sqlalchemy before_flush)			 - 2026-10-24 09:59:27,181 - logic_logger - INFO
..Order[None] {Insert - client} id: None, notes: Kafka order from behave, customer_id: 144, CreatedOn: 2026-10-24, date_shipped: None, amount_total: None  row: 0x10e78af50  session: 0x10e7b58c0  ins_upd_dlt: ins, initial: ins - 2026-10-24 09:59:27,181 - logic_logger - INFO
..Order[None] {server aggregate_defaults: amount_total } id: None, notes: Kafka order from behave, customer_id: 144, CreatedOn: 2026-10-24, date_shipped: None, amount_total: 0  row: 0x10e78af50  session: 0x10e7b58c0  ins_upd_dlt: ins, initial: ins - 2026-10-24 09:59:27,181 - logic_logger - INFO
..Item[None] {Insert - client} id: None, order_id: None, product_id: 2, quantity: 1, amount: None, unit_price: None  row: 0x10e78a7d0  session: 0x10e7b58c0  ins_upd_dlt: ins, initial: ins - 2026-10-24 09:59:27,182 - logic_logger - INFO
..Item[None] {copy_rules for role: product - unit_price} id: None, order_id: None, product_id: 2, quantity: 1, amount: None, unit_price: 90.0000000000  row: 0x10e78a7d0  session: 0x10e7b58c0  ins_upd_dlt: ins, initial: ins - 2026-10-24 09:59:27,183 - logic_logger - INFO
..Item[None] {Formula amount} id: None, order_id: None, product_id: 2, quantity: 1, amount: 90.0000000000, unit_price: 90.0000000000  row: 0x10e78a7d0  session: 0x10e7b58c0  ins_upd_dlt: ins, initial: ins - 2026-10-24 09:59:27,183 - logic_logger - INFO
....Order[None] {Update - Adjusting order: amount_total} id: None, notes: Kafka order from behave, customer_id: 144, CreatedOn: 2026-10-24, date_shipped: None, amount_total:  [0-->] 90.0000000000  row: 0x10e78af50  session: 0x10e7b58c0  ins_upd_dlt: upd, initial: upd - 2026-10-24 09:59:27,183 - logic_logger - INFO
......Customer[144] {Update - Adjusting customer: balance} id: 144, name: Credit 1792861167154, balance:  [0E-10-->] 90.0000000000, credit_limit: 1000.0000000000, email: None, email_opt_out: None  row: 0x10f1b1d50  session: 0x10e7b58c0  ins_upd_dlt: upd, initial: upd - 2026-10-24 09:59:27,183 - logic_logger - INFO
..Item[None] {Insert - client} id: None, order_id: None, product_id: 1, quantity: 2, amount: None, unit_price: None  row: 0x10e78a2d0  session: 0x10e7b58c0  ins_upd_dlt: ins, initial: ins - 2026-10-24 09:59:27,183 - logic_logger - INFO
..Item[None] {copy_rules for role: product - unit_price} id: None, order_id: None, product_id: 1, quantity: 2, amount: None, unit_price: 150.0000000000  row: 0x10e78a2d0  session: 0x10e7b58c0  ins_upd_dlt: ins, initial: ins - 2026-10-24 09:59:27,184 - logic_logger - INFO
..Item[None] {Formula amount} id: None, order_id: None, product_id: 1, quantity: 2, amount: 300.0000000000, unit_price: 150.0000000000  row: 0x10e78a2d0  session: 0x10e7b58c0  ins_upd_dlt: ins, initial: ins - 2026-10-24 09:59:27,184 - logic_logger - INFO
....Order[None] {Update - Adjusting order: amount_total} id: None, notes: Kafka order from behave, customer_id: 144, CreatedOn: 2026-10-24, date_shipped: None, amount_total:  [90.0000000000-->] 390.0000000000  row: 0x10e78af50  session: 0x10e7b58c0  ins_upd_dlt: upd, initial: upd - 2026-10-24 09:59:27,184 - logic_logger - INFO
......Customer[144] {Update - Adjusting customer: balance} id: 144, name: Credit 1792861167154, balance:  [90.0000000000-->] 390.0000000000, credit_limit: 1000.0000000000, email: None, email_opt_out: None  row: 0x10f1b1d50  session: 0x10e7b58c0  ins_upd_dlt: upd, initial: upd - 2026-10-24 09:59:27,184 - logic_logger - INFO
Logic Phase:		COMMIT LOGIC		(session=0x10e7b58c0)   										 - 2026-10-24 09:59:27,184 - logic_logger - INFO
Logic Phase:		AFTER_FLUSH LOGIC	(session=0x10e7b58c0)   										 - 2026-10-24 09:59:27,185 - logic_logger - INFO
..Order[101] {AfterFlush Event} id: 101, notes: Kafka order from behave, customer_id: 144, CreatedOn: 2026-10-24, date_shipped: None, amount_total: 390.0000000000  row: 0x10e78af50  session: 0x10e7b58c0  ins_upd_dlt: ins, initial: ins - 2026-10-24 09:59:27,185 - logic_logger - INFO


Logic Phase:		ROW LOGIC		(session=0x10e7b58c0) (sqlalchemy before_flush)			 - 2026-10-24 09:59:27,186 - logic_logger - INFO
..OrderB2bMessage[31] {Update - client} id: 31, received_at: 2026-10-24 09:59:27.171786, payload: {"Account": "Credit 1792861167154", "Notes": "Kafka order from behave", "Items": [{"Name": "Widget", "QuantityOrdered": 1}, {"Name": "Gadget", "QuantityOrdered": 2}]}, is_processed:  [False-->] True, error_text: None  row: 0x10f1b3350  session: 0x10e7b58c0  ins_upd_dlt: upd, initial: upd - 2026-10-24 09:59:27,186 - logic_logger - INFO
Logic Phase:		COMMIT LOGIC		(session=0x10e7b58c0)   										 - 2026-10-24 09:59:27,186 - logic_logger - INFO
Logic Phase:		AFTER_FLUSH LOGIC	(session=0x10e7b58c0)   										 - 2026-10-24 09:59:27,187 - logic_logger - INFO
..OrderB2bMessage[31] {AfterFlush Event} id: 31, received_at: 2026-10-24 09:59:27.171786, payload: {"Account": "Credit 1792861167154", "Notes": "Kafka order from behave", "Items": [{"Name": "Widget", "QuantityOrdered": 1}, {"Name": "Gadget", "QuantityOrdered": 2}]}, is_processed:  [False-->] True, error_text: None  row: 0x10f1b3350  session: 0x10e7b58c0  ins_upd_dlt: upd, initial: upd - 2026-10-24 09:59:27,187 - logic_logger - INFO

```
</details>

&nbsp;
&nbsp;

#### Scenario: Check Credit is enforced on the Kafka path ✅ (0.56 s)
&emsp;  Scenario: Check Credit is enforced on the Kafka path  
&emsp;&emsp;    Given a customer with a credit limit of 100  
&emsp;&emsp;    When an inbound order message for that customer is delivered to topic order_b2b  
&emsp;&emsp;    Then the message is rejected with a credit limit message  
&emsp;&emsp;    And the customer balance is 0  

<details markdown>
<summary>Rules exercised and logic log (2 transactions)</summary>


&nbsp;
&nbsp;


**Rules Used** in Scenario: Check Credit is enforced on the Kafka path
```
  OrderB2bMessage  
    1. RowEvent OrderB2bMessage._publish_order_b2b_blob()  
  Customer  
    2. Derive Customer.balance as Sum(Order.amount_total Where Rule.sum(derive=models.Customer.balance, as_sum_of=models.Order.amount_total, where=lambda row: row.date_shipped is None))  
    3. Constraint Function: None  
  Item  
    4. Derive Item.unit_price as Copy(product.unit_price)  
    5. Derive Item.amount as Formula (1): Rule.formula(derive=models.Item.amount, as_expres [...]  
  Order  
    6. Derive Order.amount_total as Sum(Item.amount Where  - None)  
```
**Logic Log** in Scenario: Check Credit is enforced on the Kafka path (2 transactions)
```
Logic Phase:		ROW LOGIC		(session=0x10e7b5d00) (sqlalchemy before_flush)			 - 2026-10-24 09:59:27,743 - logic_logger - INFO
..OrderB2bMessage[None] {Insert - client} id: None, received_at: 2026-10-24 09:59:27.742965, payload: {"Account": "Credit 1792861167731", "Notes": "Kafka order from behave", "Items": [{"Name": "Widget", "QuantityOrdered": 1}, {"Name": "Gadget", "QuantityOrdered": 2}]}, is_processed: False, error_text: None  row: 0x10e78a750  session: 0x10e7b5d00  ins_upd_dlt: ins, initial: ins - 2026-10-24 09:59:27,743 - logic_logger - INFO
Logic Phase:		COMMIT LOGIC		(session=0x10e7b5d00)   										 - 2026-10-24 09:59:27,743 - logic_logger - INFO
Logic Phase:		AFTER_FLUSH LOGIC	(session=0x10e7b5d00)   										 - 2026-10-24 09:59:27,744 - logic_logger - INFO
..OrderB2bMessage[32] {AfterFlush Event} id: 32, received_at: 2026-10-24 09:59:27.742965, payload: {"Account": "Credit 1792861167731", "Notes": "Kafka order from behave", "Items": [{"Name": "Widget", "QuantityOrdered": 1}, {"Name": "Gadget", "QuantityOrdered": 2}]}, is_processed: False, error_text: None  row: 0x10e78a750  session: 0x10e7b5d00  ins_upd_dlt: ins, initial: ins - 2026-10-24 09:59:27,744 - logic_logger - INFO


Logic Phase:		ROW LOGIC		(session=0x10e7b5590) (sqlalchemy before_flush)			 - 2026-10-24 09:59:27,751 - logic_logger - INFO
..Order[None] {Insert - client} id: None, notes: Kafka order from behave, customer_id: 145, CreatedOn: 2026-10-24, date_shipped: None, amount_total: None  row: 0x10e7d9e50  session: 0x10e7b5590  ins_upd_dlt: ins, initial: ins - 2026-10-24 09:59:27,754 - logic_logger - INFO
..Order[None] {server aggregate_defaults: amount_total } id: None, notes: Kafka order from behave, customer_id: 145, CreatedOn: 2026-10-24, date_shipped: None, amount_total: 0  row: 0x10e7d9e50  session: 0x10e7b5590  ins_upd_dlt: ins, initial: ins - 2026-10-24 09:59:27,754 - logic_logger - INFO
..Item[None] {Insert - client} id: None, order_id: None, product_id: 2, quantity: 1, amount: None, unit_price: None  row: 0x10e7d83d0  session: 0x10e7b5590  ins_upd_dlt: ins, initial: ins - 2026-10-24 09:59:27,754 - logic_logger - INFO
..Item[None] {copy_rules for role: product - unit_price} id: None, order_id: None, product_id: 2, quantity: 1, amount: None, unit_price: 90.0000000000  row: 0x10e7d83d0  session: 0x10e7b5590  ins_upd_dlt: ins, initial: ins - 2026-10-24 09:59:27,755 - logic_logger - INFO
..Item[None] {Formula amount} id: None, order_id: None, product_id: 2, quantity: 1, amount: 90.0000000000, unit_price: 90.0000000000  row: 0x10e7d83d0  session: 0x10e7b5590  ins_upd_dlt: ins, initial: ins - 2026-10-24 09:59:27,755 - logic_logger - INFO
....Order[None] {Update - Adjusting order: amount_total} id: None, notes: Kafka order from behave, customer_id: 145, CreatedOn: 2026-10-24, date_shipped: None, amount_total:  [0-->] 90.0000000000  row: 0x10e7d9e50  session: 0x10e7b5590  ins_upd_dlt: upd, initial: upd - 2026-10-24 09:59:27,755 - logic_logger - INFO
......Customer[145] {Update - Adjusting customer: balance} id: 145, name: Credit 1792861167731, balance:  [0E-10-->] 90.0000000000, credit_limit: 100.0000000000, email: None, email_opt_out: None  row: 0x10e7da250  session: 0x10e7b5590  ins_upd_dlt: upd, initial: upd - 2026-10-24 09:59:27,755 - logic_logger - INFO
..Item[None] {Insert - client} id: None, order_id: None, product_id: 1, quantity: 2, amount: None, unit_price: None  row: 0x10e7da650  session: 0x10e7b5590  ins_upd_dlt: ins, initial: ins - 2026-10-24 09:59:27,756 - logic_logger - INFO
..Item[None] {copy_rules for role: product - unit_price} id: None, order_id: None, product_id: 1, quantity: 2, amount: None, unit_price: 150.0000000000  row: 0x10e7da650  session: 0x10e7b5590  ins_upd_dlt: ins, initial: ins - 2026-10-24 09:59:27,756 - logic_logger - INFO
..Item[None] {Formula amount} id: None, order_id: None, product_id: 1, quantity: 2, amount: 300.0000000000, unit_price: 150.0000000000  row: 0x10e7da650  session: 0x10e7b5590  ins_upd_dlt: ins, initial: ins - 2026-10-24 09:59:27,756 - logic_logger - INFO
....Order[None] {Update - Adjusting order: amount_total} id: None, notes: Kafka order from behave, customer_id: 145, CreatedOn: 2026-10-24, date_shipped: None, amount_total:  [90.0000000000-->] 390.0000000000  row: 0x10e7d9e50  session: 0x10e7b5590  ins_upd_dlt: upd, initial: upd - 2026-10-24 09:59:27,757 - logic_logger - INFO
......Customer[145] {Update - Adjusting customer: balance} id: 145, name: Credit 1792861167731, balance:  [90.0000000000-->] 390.0000000000, credit_limit: 100.0000000000, email: None, email_opt_out: None  row: 0x10e7da250  session: 0x10e7b5590  ins_upd_dlt: upd, initial: upd - 2026-10-24 09:59:27,757 - logic_logger - INFO
......Customer[145] {Constraint Failure: balance (390.0000000000) exceeds credit limit (100.0000000000)} id: 145, name: Credit 1792861167731, balance:  [90.0000000000-->] 390.0000000000, credit_limit: 100.0000000000, email: None, email_opt_out: None  row: 0x10e7da250  session: 0x10e7b5590  ins_upd_dlt: upd, initial: upd - 2026-10-24 09:59:27,757 - logic_logger - INFO

```
</details>

&nbsp;
&nbsp;

#### Scenario: Message for an unknown account is rejected ✅ (0.54 s)
&emsp;  Scenario: Message for an unknown account is rejected  
&emsp;&emsp;    Given an inbound order message for an unknown account  
&emsp;&emsp;    When the unknown-account message is delivered to topic order_b2b  
&emsp;&emsp;    Then the message is rejected with a lookup message  

<details markdown>
<summary>Rules exercised and logic log (1 transaction)</summary>


&nbsp;
&nbsp;


**Rules Used** in Scenario: Message for an unknown account is rejected
```
  OrderB2bMessage  
    1. RowEvent OrderB2bMessage._publish_order_b2b_blob()  
```
**Logic Log** in Scenario: Message for an unknown account is rejected (1 transaction)
```
Logic Phase:		ROW LOGIC		(session=0x10e7b5e10) (sqlalchemy before_flush)			 - 2026-10-24 09:59:28,305 - logic_logger - INFO
..OrderB2bMessage[None] {Insert - client} id: None, received_at: 2026-10-24 09:59:28.304539, payload: {"Account": "No Such Account 1792861168294", "Notes": "Kafka order from behave", "Items": [{"Name": "Widget", "QuantityOrdered": 1}, {"Name": "Gadget", "QuantityOrdered": 2}]}, is_processed: False, error_text: None  row: 0x10e7a6550  session: 0x10e7b5e10  ins_upd_dlt: ins, initial: ins - 2026-10-24 09:59:28,305 - logic_logger - INFO
Logic Phase:		COMMIT LOGIC		(session=0x10e7b5e10)   										 - 2026-10-24 09:59:28,305 - logic_logger - INFO
Logic Phase:		AFTER_FLUSH LOGIC	(session=0x10e7b5e10)   										 - 2026-10-24 09:59:28,306 - logic_logger - INFO
..OrderB2bMessage[33] {AfterFlush Event} id: 33, received_at: 2026-10-24 09:59:28.304539, payload: {"Account": "No Such Account 1792861168294", "Notes": "Kafka order from behave", "Items": [{"Name": "Widget", "QuantityOrdered": 1}, {"Name": "Gadget", "QuantityOrdered": 2}]}, is_processed: False, error_text: None  row: 0x10e7a6550  session: 0x10e7b5e10  ins_upd_dlt: ins, initial: ins - 2026-10-24 09:59:28,306 - logic_logger - INFO

```
</details>

&nbsp;
&nbsp;

#### Scenario: A rejected message is kept with its error text (live Kafka only) ✅ (0.57 s)
&emsp;  Scenario: A rejected message is kept with its error text (live Kafka only)  
&emsp;&emsp;    Given an inbound order message for an unknown account  
&emsp;&emsp;    When the unknown-account message is delivered through live Kafka  
&emsp;&emsp;    Then the message blob is kept unprocessed with its error text  

<details markdown>
<summary>Rules exercised and logic log (1 transaction)</summary>


&nbsp;
&nbsp;


**Rules Used** in Scenario: A rejected message is kept with its error text (live Kafka only)
```
  OrderB2bMessage  
    1. RowEvent OrderB2bMessage._publish_order_b2b_blob()  
```
**Logic Log** in Scenario: A rejected message is kept with its error text (live Kafka only) (1 transaction)
```
Logic Phase:		ROW LOGIC		(session=0x10e7b6140) (sqlalchemy before_flush)			 - 2026-10-24 09:59:28,855 - logic_logger - INFO
..OrderB2bMessage[None] {Insert - client} id: None, received_at: 2026-10-24 09:59:28.854626, payload: {"Account": "No Such Account 1792861168839", "Notes": "Kafka order from behave", "Items": [{"Name": "Widget", "QuantityOrdered": 1}, {"Name": "Gadget", "QuantityOrdered": 2}]}, is_processed: False, error_text: None  row: 0x10e7dbdd0  session: 0x10e7b6140  ins_upd_dlt: ins, initial: ins - 2026-10-24 09:59:28,855 - logic_logger - INFO
Logic Phase:		COMMIT LOGIC		(session=0x10e7b6140)   										 - 2026-10-24 09:59:28,856 - logic_logger - INFO
Logic Phase:		AFTER_FLUSH LOGIC	(session=0x10e7b6140)   										 - 2026-10-24 09:59:28,857 - logic_logger - INFO
..OrderB2bMessage[34] {AfterFlush Event} id: 34, received_at: 2026-10-24 09:59:28.854626, payload: {"Account": "No Such Account 1792861168839", "Notes": "Kafka order from behave", "Items": [{"Name": "Widget", "QuantityOrdered": 1}, {"Name": "Gadget", "QuantityOrdered": 2}]}, is_processed: False, error_text: None  row: 0x10e7dbdd0  session: 0x10e7b6140  ins_upd_dlt: ins, initial: ins - 2026-10-24 09:59:28,857 - logic_logger - INFO

```
</details>

&nbsp;
&nbsp;

### Feature: Row-Level Security  

&nbsp;
&nbsp;

#### Scenario: Sales role sees limited customers ✅ (0.07 s)
&emsp;  Scenario: Sales role sees limited customers  
&emsp;&emsp;    Given a high-credit customer, a low-credit customer and a low-credit customer with a balance  
&emsp;&emsp;    When a user with the sales role queries the Customer list  
&emsp;&emsp;    Then the list includes the high-credit customer and the customer with a balance  
&emsp;&emsp;    And the list excludes the low-credit customer  

<details markdown>
<summary>Rules exercised and logic log (1 transaction)</summary>


&nbsp;
&nbsp;


**Rules Used** in Scenario: Sales role sees limited customers
```
  Customer  
    1. Derive Customer.balance as Sum(Order.amount_total Where Rule.sum(derive=models.Customer.balance, as_sum_of=models.Order.amount_total, where=lambda row: row.date_shipped is None))  
  Item  
    2. Derive Item.unit_price as Copy(product.unit_price)  
    3. Derive Item.amount as Formula (1): Rule.formula(derive=models.Item.amount, as_expres [...]  
  Order  
    4. Derive Order.amount_total as Sum(Item.amount Where  - None)  
    5. RowEvent Order._send_order_to_kafka()  
```
**Logic Log** in Scenario: Sales role sees limited customers (1 transaction)
```
Logic Phase:		ROW LOGIC		(session=0x10e7b6cf0) (sqlalchemy before_flush)			 - 2026-10-24 09:59:29,436 - logic_logger - INFO
..Product[2] {Update - client} id: 2, name: Widget, count_suppliers: 0, unit_price: 90.0000000000  row: 0x10f2a0830  session: 0x10e7b6cf0  ins_upd_dlt: upd, initial: upd - 2026-10-24 09:59:29,436 - logic_logger - INFO
..Order[None] {Insert - client} id: None, notes: behave, customer_id: 148, CreatedOn: 2026-10-24, date_shipped: None, amount_total: None  row: 0x10e78a2d0  session: 0x10e7b6cf0  ins_upd_dlt: ins, initial: ins - 2026-10-24 09:59:29,436 - logic_logger - INFO
..Order[None] {server aggregate_defaults: amount_total } id: None, notes: behave, customer_id: 148, CreatedOn: 2026-10-24, date_shipped: None, amount_total: 0  row: 0x10e78a2d0  session: 0x10e7b6cf0  ins_upd_dlt: ins, initial: ins - 2026-10-24 09:59:29,436 - logic_logger - INFO
..Item[None] {Insert - client} id: None, order_id: None, product_id: None, quantity: 1, amount: None, unit_price: None  row: 0x10e78b250  session: 0x10e7b6cf0  ins_upd_dlt: ins, initial: ins - 2026-10-24 09:59:29,436 - logic_logger - INFO
..Item[None] {copy_rules for role: product - unit_price} id: None, order_id: None, product_id: None, quantity: 1, amount: None, unit_price: 90.0000000000  row: 0x10e78b250  session: 0x10e7b6cf0  ins_upd_dlt: ins, initial: ins - 2026-10-24 09:59:29,437 - logic_logger - INFO
..Item[None] {Formula amount} id: None, order_id: None, product_id: None, quantity: 1, amount: 90.0000000000, unit_price: 90.0000000000  row: 0x10e78b250  session: 0x10e7b6cf0  ins_upd_dlt: ins, initial: ins - 2026-10-24 09:59:29,437 - logic_logger - INFO
....Order[None] {Update - Adjusting order: amount_total} id: None, notes: behave, customer_id: 148, CreatedOn: 2026-10-24, date_shipped: None, amount_total:  [0-->] 90.0000000000  row: 0x10e78a2d0  session: 0x10e7b6cf0  ins_upd_dlt: upd, initial: upd - 2026-10-24 09:59:29,437 - logic_logger - INFO
......Customer[148] {Update - Adjusting customer: balance} id: 148, name: Owing 1792861169425, balance:  [0E-10-->] 90.0000000000, credit_limit: 500.0000000000, email: None, email_opt_out: None  row: 0x10e7a47d0  session: 0x10e7b6cf0  ins_upd_dlt: upd, initial: upd - 2026-10-24 09:59:29,437 - logic_logger - INFO
Logic Phase:		COMMIT LOGIC		(session=0x10e7b6cf0)   										 - 2026-10-24 09:59:29,437 - logic_logger - INFO
Logic Phase:		AFTER_FLUSH LOGIC	(session=0x10e7b6cf0)   										 - 2026-10-24 09:59:29,439 - logic_logger - INFO
..Order[102] {AfterFlush Event} id: 102, notes: behave, customer_id: 148, CreatedOn: 2026-10-24, date_shipped: None, amount_total: 90.0000000000  row: 0x10e78a2d0  session: 0x10e7b6cf0  ins_upd_dlt: ins, initial: ins - 2026-10-24 09:59:29,439 - logic_logger - INFO

```
</details>

&nbsp;&nbsp;  
/Users/val/dev/genai-logic/ApiLogicServer-dev/build_and_test/genai-logic/demo_eai/test/api_logic_server_behave/behave_run.py completed at October 24, 2026 09:59:29  
Behave run time: 2.995 s  


&nbsp;
&nbsp;

## Provenance

| | |
|---|---|
| Generated | October 24, 2026 09:59 |
| Generator | `requirements_traceability_report.py` 2.11 |
| Report text from | reports/Requirements Traceability Report Template.md (sha256 ccda5d97612c) |
| Tests last ran | October 24, 2026 09:59 |
| Project | demo_eai |
| Project created | October 23, 2026 16:50:48 |
| Requirement files read | `docs/requirements/check_credit/requirements.md` (sha256 c40669f6)<br>`docs/requirements/demo_eai/requirements.md` (sha256 672062e9)<br>`docs/requirements/kafka_publish_shipping/requirements.md` (sha256 021c2d4b)<br>`docs/requirements/kafka_subscribe_order/requirements.md` (sha256 89e6e5e0) |
| Regenerate | `python requirements_traceability_report.py run`, from `test/api_logic_server_behave` |

_The report is derived from the project's files and the last test run; nothing in it is stored anywhere else, so regenerating it always reflects the project as it is now._

