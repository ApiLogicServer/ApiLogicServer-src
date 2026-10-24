# Requirements Traceability Report

This report shows requirements, the rules created from them, and the tests created from those rules.

This project began as natural-language requirements, fleshed out by AI into a running system of business rules that are *executable documentation*. This report is how you govern the result.

A governable system is one you can **read**, **trust**, and **maintain**: each requirement is listed beside the rules that implement it (*read*); the tests and logic logs show those rules running (*trust*); re-run it after any change and it flags the gaps — an untested requirement, an untraced rule, a channel no test checks (*maintain*).

It is generated from the project's own files, nothing written by hand, so it is as current as the last run and covers the whole project, not a sample. Open **Background** (below the summary) for what the terms mean, how to read the report, and what it can and can't tell you.


**Project:** demo_eai &nbsp;|&nbsp; **Generated:** October 23, 2026 17:22 &nbsp;|&nbsp; **Rules:** 8 &nbsp;|&nbsp; **Test scenarios:** 11 &nbsp;|&nbsp; **Generator:** requirements_traceability_report.py 2.9

**Last test run:** October 23, 2026 17:22 (0m before this report; test results and logic logs below are from that run)


&nbsp;
&nbsp;

## At a Glance

**✅ 5 requirement(s), all implemented; 5 tested; 11 of 11 scenarios passed; last run 0m ago.**

| | |
|---|---|
| Requirements | 5 (5 implemented) |
| Tested | 5 of 5 |
| Last test run | ✅ 11 passed, 0 failed (October 23, 2026 17:22, 0m ago) |
| Rules | 8 (5 declarative, 0 Python functions, 3 Python events) |
| Rules shown running in a test log | 7 of 8 |
| Security | not enabled; 11 role(s), 2 row-level grant(s) |
| Messages and APIs | 2 Kafka topic(s) in, 2 out; 1 HTTP endpoint(s) |

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
| Implementation not traced to a requirement | `api/api_discovery/order_b2b_kafka_consume_debug.py`, `logic/logic_discovery/system/all_classes_stamping.py` |
| Tests not traced to a requirement | none |
| Test results (last run) | ✅ 11 passed, 0 failed |
| Scenarios with a logic log | 11 of 11 |
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
| §3 Kafka Subscribe — Inbound orders from sales channel | [logic/logic_discovery/kafka_subscribe_order.py](../../../logic/logic_discovery/kafka_subscribe_order.py)<br>[integration/kafka/kafka_subscribe_discovery/order_b2b.py](../../../integration/kafka/kafka_subscribe_discovery/order_b2b.py)<br>[integration/OrderB2BSubscribeMapper.py](../../../integration/OrderB2BSubscribeMapper.py) | 1 | ✅ 3 scenario(s): 3 passed |
| §4 Kafka Publish — Notify shipping on dispatch | [logic/logic_discovery/kafka_publish_shipping.py](../../../logic/logic_discovery/kafka_publish_shipping.py)<br>[integration/kafka/kafka_publish_discovery/order_shipping.py](../../../integration/kafka/kafka_publish_discovery/order_shipping.py) | 1 | ✅ 2 scenario(s): 2 passed |
| §5 Security | [security/declare_security.py](../../../security/declare_security.py) | 0 | ✅ 1 scenario(s): 1 passed |


&nbsp;

### Rule coverage by tests

| Rule | Requirement | Seen in |
|---|---|---|
| `Customer: balance <= credit_limit` | §1 Business Logic — Check Credit | 2: Exceed Credit Rejected; Inbound Message Over Credit Limit Rejected |
| `Customer.balance = sum(Order.amount_total) where date_shipped is None` | §1 Business Logic — Check Credit | 8: Partner Order Accepted; Good Order Placed; Ship Order Excludes From Balance; +5 more |
| `Order.amount_total = sum(Item.amount)` | §1 Business Logic — Check Credit | 8: Partner Order Accepted; Good Order Placed; Ship Order Excludes From Balance; +5 more |
| `Item.amount = quantity * unit_price` | §1 Business Logic — Check Credit | 8: Partner Order Accepted; Good Order Placed; Ship Order Excludes From Balance; +5 more |
| `Item.unit_price = copy of Product.unit_price` | §1 Business Logic — Check Credit | 8: Partner Order Accepted; Good Order Placed; Ship Order Excludes From Balance; +5 more |
| `Order.after_flush_row_event → _send_order_to_kafka()` | §4 Kafka Publish — Notify shipping on dispatch | 6: Partner Order Accepted; Good Order Placed; Ship Order Excludes From Balance; +3 more |
| `OrderB2bMessage.after_flush_row_event → _publish_order_b2b_blob()` | §3 Kafka Subscribe — Inbound orders from sales channel | 1: Inbound Order Message Processed |
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

or run this from the Manager root (`codespaces_mgr`):

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
| `Customer: balance <= credit_limit` | constraint | declarative | Error: Customer balance ({row.balance}) exceeds credit limit ({row.credit_limit}) | [check_credit.py](../../../logic/logic_discovery/check_credit.py) |
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

Tests: ✅ 3 scenario(s): 3 passed

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
| `Kafka in: order_b2b` | kafka | handler (Python) | Kafka subscribe order_b2b: Consumer 1 saves the raw message as an OrderB2bMessage blob (Tx 1); the blob insert event publishes it to order_b2b_processed. | [order_b2b.py](../../../integration/kafka/kafka_subscribe_discovery/order_b2b.py) |
| `Kafka in: order_b2b_processed` | kafka | handler (Python) | Kafka subscribe order_b2b_processed: Consumer 2 parses the blob into an Order with Items (Tx 2), recording any failure on the blob's error_text. | [order_b2b.py](../../../integration/kafka/kafka_subscribe_discovery/order_b2b.py) |
| `OrderB2BSubscribeMapper.py` | module |  | Feature: Kafka Subscribe Order Integration | [OrderB2BSubscribeMapper.py](../../../integration/OrderB2BSubscribeMapper.py) |

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
| `Order.after_flush_row_event → _send_order_to_kafka()` | after_flush_row_event | event (Python) | Order publish: sends the Order to Kafka topic order_shipping, shaped by message_formats/order_shipping.json, when date_shipped is first set. | [kafka_publish_shipping.py](../../../logic/logic_discovery/kafka_publish_shipping.py) |
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

_Diagram not rendered: Graphviz `dot` is not installed (`brew install graphviz`). The graph source is in `test/api_logic_server_behave/reports/db_diagram.generated.dot`._


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
| sales | ✅ | — | — | — |
| public | ✅ | — | — | — |
| default-roles-kcals | ✅ | ✅ | ✅ | — |
| uma_authorization | ✅ | ✅ | ✅ | — |


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

| Direction | Channel | Name | Handler | Tables created | Message shape | Requirement | Tests mention it |
|---|---|---|---|---|---|---|---|
| ➡ in | Kafka | `order_b2b` | `order_b2b()` - Kafka subscribe order_b2b: Consumer 1 saves the raw message as an OrderB2bMessage blob (Tx 1); the blob insert event publishes it to order_b2b_processed. | OrderB2bMessage | [order_b2b.json](../../../integration/kafka/message_formats/order_b2b.json) | §3 Kafka Subscribe — Inbound orders from sales channel | ✅ |
| ➡ in | Kafka | `order_b2b_processed` | `order_b2b_processed()` - Kafka subscribe order_b2b_processed: Consumer 2 parses the blob into an Order with Items (Tx 2), recording any failure on the blob's error_text. | Item, Order, OrderB2bMessage |  | §3 Kafka Subscribe — Inbound orders from sales channel | ⚠ no test mentions it |
| ⬅ out | Kafka | `order_shipping` | Order.after_flush_row_event → _send_order_to_kafka() - Order publish: sends the Order to Kafka topic order_shipping, shaped by message_formats/order_shipping.json, when date_shipped is first set. |  | [order_shipping.json](../../../integration/kafka/message_formats/order_shipping.json) | §4 Kafka Publish — Notify shipping on dispatch | ✅ |
| ⬅ out | Kafka | `order_b2b_processed` | OrderB2bMessage.after_flush_row_event → _publish_order_b2b_blob() - OrderB2bMessage event: after Tx 1 commits the blob, publishes its payload to order_b2b_processed so Consumer 2 parses it in a clean Tx 2 (skipped when already processed, i.e. the debug path). |  |  | §3 Kafka Subscribe — Inbound orders from sales channel | ⚠ no test mentions it |
| ➡ in | HTTP | `GET /consume_debug/order_b2b` | `consume_debug_order_b2b()` - Debug the order_b2b consume pipeline without Kafka. |  |  |  | ✅ |

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

**✅ 11 scenario(s): 11 passed, 0 failed** (from the last run, `logs/behave.log`).

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

#### Scenario: Partner Order Accepted ✅
&emsp;  Scenario: Partner Order Accepted  
&emsp;&emsp;    Given a customer with credit limit 1000  
&emsp;&emsp;    When a B2B order is placed for 3 Widget and 2 Gadget  
&emsp;&emsp;    Then the B2B order is created  
&emsp;&emsp;    And the order belongs to the customer  
&emsp;&emsp;    And the order has 2 items  
&emsp;&emsp;    And the order has 3 of Widget  
&emsp;&emsp;    And the order has 2 of Gadget  

<details markdown>
<summary>Rules exercised and logic log (1 transaction)</summary>


&nbsp;
&nbsp;


**Rules Used** in Scenario: Partner Order Accepted
```
  Customer  
    1. Derive Customer.balance as Sum(Order.amount_total Where lambda row: row.date_shipped is None))  
  Item  
    2. Derive Item.amount as Formula (1): Rule.formula(derive=models.Item.amount, as_expres [...]  
    3. Derive Item.unit_price as Copy(product.unit_price)  
  Order  
    4. Derive Order.amount_total as Sum(Item.amount Where  - None)  
    5. RowEvent Order._send_order_to_kafka()  
```
**Logic Log** in Scenario: Partner Order Accepted (1 transaction)
```
Logic Phase:		ROW LOGIC		(session=0x71d6952618b0) (sqlalchemy before_flush)			 - 2026-10-23 17:22:45,932 - logic_logger - INFO
..Product[1] {Update - client} id: 1, name: Gadget, count_suppliers: 0, unit_price: 150.0000000000  row: 0x71d696bcede0  session: 0x71d6952618b0  ins_upd_dlt: upd, initial: upd - 2026-10-23 17:22:45,933 - logic_logger - INFO
..Order[None] {Insert - client} id: None, notes: Test order, customer_id: 16, CreatedOn: None, date_shipped: None, amount_total: None  row: 0x71d6952610a0  session: 0x71d6952618b0  ins_upd_dlt: ins, initial: ins - 2026-10-23 17:22:45,934 - logic_logger - INFO
..Order[None] {server aggregate_defaults: amount_total } id: None, notes: Test order, customer_id: 16, CreatedOn: None, date_shipped: None, amount_total: 0  row: 0x71d6952610a0  session: 0x71d6952618b0  ins_upd_dlt: ins, initial: ins - 2026-10-23 17:22:45,934 - logic_logger - INFO
..Item[None] {Insert - client} id: None, order_id: None, product_id: 2, quantity: 3, amount: None, unit_price: None  row: 0x71d695261c10  session: 0x71d6952618b0  ins_upd_dlt: ins, initial: ins - 2026-10-23 17:22:45,935 - logic_logger - INFO
..Item[None] {copy_rules for role: product - unit_price} id: None, order_id: None, product_id: 2, quantity: 3, amount: None, unit_price: 90.0000000000  row: 0x71d695261c10  session: 0x71d6952618b0  ins_upd_dlt: ins, initial: ins - 2026-10-23 17:22:45,936 - logic_logger - INFO
..Item[None] {Formula amount} id: None, order_id: None, product_id: 2, quantity: 3, amount: 270.0000000000, unit_price: 90.0000000000  row: 0x71d695261c10  session: 0x71d6952618b0  ins_upd_dlt: ins, initial: ins - 2026-10-23 17:22:45,936 - logic_logger - INFO
....Order[None] {Update - Adjusting order: amount_total} id: None, notes: Test order, customer_id: 16, CreatedOn: None, date_shipped: None, amount_total:  [0-->] 270.0000000000  row: 0x71d6952610a0  session: 0x71d6952618b0  ins_upd_dlt: upd, initial: upd - 2026-10-23 17:22:45,937 - logic_logger - INFO
......Customer[16] {Update - Adjusting customer: balance} id: 16, name: Test Customer 1792776165896, balance:  [0E-10-->] 270.0000000000, credit_limit: 1000.0000000000, email: None, email_opt_out: None  row: 0x71d69524fa10  session: 0x71d6952618b0  ins_upd_dlt: upd, initial: upd - 2026-10-23 17:22:45,938 - logic_logger - INFO
..Item[None] {Insert - client} id: None, order_id: None, product_id: None, quantity: 2, amount: None, unit_price: None  row: 0x71d695262780  session: 0x71d6952618b0  ins_upd_dlt: ins, initial: ins - 2026-10-23 17:22:45,940 - logic_logger - INFO
..Item[None] {copy_rules for role: product - unit_price} id: None, order_id: None, product_id: None, quantity: 2, amount: None, unit_price: 150.0000000000  row: 0x71d695262780  session: 0x71d6952618b0  ins_upd_dlt: ins, initial: ins - 2026-10-23 17:22:45,940 - logic_logger - INFO
..Item[None] {Formula amount} id: None, order_id: None, product_id: None, quantity: 2, amount: 300.0000000000, unit_price: 150.0000000000  row: 0x71d695262780  session: 0x71d6952618b0  ins_upd_dlt: ins, initial: ins - 2026-10-23 17:22:45,940 - logic_logger - INFO
....Order[None] {Update - Adjusting order: amount_total} id: None, notes: Test order, customer_id: 16, CreatedOn: None, date_shipped: None, amount_total:  [270.0000000000-->] 570.0000000000  row: 0x71d6952610a0  session: 0x71d6952618b0  ins_upd_dlt: upd, initial: upd - 2026-10-23 17:22:45,941 - logic_logger - INFO
......Customer[16] {Update - Adjusting customer: balance} id: 16, name: Test Customer 1792776165896, balance:  [270.0000000000-->] 570.0000000000, credit_limit: 1000.0000000000, email: None, email_opt_out: None  row: 0x71d69524fa10  session: 0x71d6952618b0  ins_upd_dlt: upd, initial: upd - 2026-10-23 17:22:45,942 - logic_logger - INFO
Logic Phase:		COMMIT LOGIC		(session=0x71d6952618b0)   										 - 2026-10-23 17:22:45,943 - logic_logger - INFO
Logic Phase:		AFTER_FLUSH LOGIC	(session=0x71d6952618b0)   										 - 2026-10-23 17:22:45,945 - logic_logger - INFO
..Order[17] {AfterFlush Event} id: 17, notes: Test order, customer_id: 16, CreatedOn: None, date_shipped: None, amount_total: 570.0000000000  row: 0x71d6952610a0  session: 0x71d6952618b0  ins_upd_dlt: ins, initial: ins - 2026-10-23 17:22:45,945 - logic_logger - INFO

```
</details>

&nbsp;
&nbsp;

#### Scenario: Unknown Account Rejected ✅
&emsp;  Scenario: Unknown Account Rejected  
&emsp;&emsp;    Given a customer with credit limit 1000  
&emsp;&emsp;    When a B2B order is placed for an unknown account  
&emsp;&emsp;    Then the B2B order is rejected with message containing "Lookup failed"  

_No rules fired in this scenario's logic log._

&nbsp;
&nbsp;

### Feature: Check Credit  

&nbsp;
&nbsp;

#### Scenario: Good Order Placed ✅
&emsp;  Scenario: Good Order Placed  
&emsp;&emsp;    Given a customer with credit limit 1000  
&emsp;&emsp;    When a B2B order is placed for 2 Widget  
&emsp;&emsp;    Then the B2B order is created  
&emsp;&emsp;    And the item unit price is 90  
&emsp;&emsp;    And the item amount is 180  
&emsp;&emsp;    And the order total is 180  
&emsp;&emsp;    And the customer balance is 180  

<details markdown>
<summary>Rules exercised and logic log (1 transaction)</summary>


&nbsp;
&nbsp;


**Rules Used** in Scenario: Good Order Placed
```
  Customer  
    1. Derive Customer.balance as Sum(Order.amount_total Where lambda row: row.date_shipped is None))  
  Item  
    2. Derive Item.amount as Formula (1): Rule.formula(derive=models.Item.amount, as_expres [...]  
    3. Derive Item.unit_price as Copy(product.unit_price)  
  Order  
    4. Derive Order.amount_total as Sum(Item.amount Where  - None)  
    5. RowEvent Order._send_order_to_kafka()  
```
**Logic Log** in Scenario: Good Order Placed (1 transaction)
```
Logic Phase:		ROW LOGIC		(session=0x71d6952dc140) (sqlalchemy before_flush)			 - 2026-10-23 17:22:46,047 - logic_logger - INFO
..Product[2] {Update - client} id: 2, name: Widget, count_suppliers: 0, unit_price: 90.0000000000  row: 0x71d69529b8c0  session: 0x71d6952dc140  ins_upd_dlt: upd, initial: upd - 2026-10-23 17:22:46,047 - logic_logger - INFO
..Order[None] {Insert - client} id: None, notes: Test order, customer_id: 18, CreatedOn: None, date_shipped: None, amount_total: None  row: 0x71d6952dc5c0  session: 0x71d6952dc140  ins_upd_dlt: ins, initial: ins - 2026-10-23 17:22:46,048 - logic_logger - INFO
..Order[None] {server aggregate_defaults: amount_total } id: None, notes: Test order, customer_id: 18, CreatedOn: None, date_shipped: None, amount_total: 0  row: 0x71d6952dc5c0  session: 0x71d6952dc140  ins_upd_dlt: ins, initial: ins - 2026-10-23 17:22:46,048 - logic_logger - INFO
..Item[None] {Insert - client} id: None, order_id: None, product_id: None, quantity: 2, amount: None, unit_price: None  row: 0x71d6952dc980  session: 0x71d6952dc140  ins_upd_dlt: ins, initial: ins - 2026-10-23 17:22:46,049 - logic_logger - INFO
..Item[None] {copy_rules for role: product - unit_price} id: None, order_id: None, product_id: None, quantity: 2, amount: None, unit_price: 90.0000000000  row: 0x71d6952dc980  session: 0x71d6952dc140  ins_upd_dlt: ins, initial: ins - 2026-10-23 17:22:46,049 - logic_logger - INFO
..Item[None] {Formula amount} id: None, order_id: None, product_id: None, quantity: 2, amount: 180.0000000000, unit_price: 90.0000000000  row: 0x71d6952dc980  session: 0x71d6952dc140  ins_upd_dlt: ins, initial: ins - 2026-10-23 17:22:46,049 - logic_logger - INFO
....Order[None] {Update - Adjusting order: amount_total} id: None, notes: Test order, customer_id: 18, CreatedOn: None, date_shipped: None, amount_total:  [0-->] 180.0000000000  row: 0x71d6952dc5c0  session: 0x71d6952dc140  ins_upd_dlt: upd, initial: upd - 2026-10-23 17:22:46,050 - logic_logger - INFO
......Customer[18] {Update - Adjusting customer: balance} id: 18, name: Test Customer 1792776166027, balance:  [0E-10-->] 180.0000000000, credit_limit: 1000.0000000000, email: None, email_opt_out: None  row: 0x71d6952dcdd0  session: 0x71d6952dc140  ins_upd_dlt: upd, initial: upd - 2026-10-23 17:22:46,050 - logic_logger - INFO
Logic Phase:		COMMIT LOGIC		(session=0x71d6952dc140)   										 - 2026-10-23 17:22:46,051 - logic_logger - INFO
Logic Phase:		AFTER_FLUSH LOGIC	(session=0x71d6952dc140)   										 - 2026-10-23 17:22:46,052 - logic_logger - INFO
..Order[18] {AfterFlush Event} id: 18, notes: Test order, customer_id: 18, CreatedOn: None, date_shipped: None, amount_total: 180.0000000000  row: 0x71d6952dc5c0  session: 0x71d6952dc140  ins_upd_dlt: ins, initial: ins - 2026-10-23 17:22:46,053 - logic_logger - INFO

```
</details>

&nbsp;
&nbsp;

#### Scenario: Ship Order Excludes From Balance ✅
&emsp;  Scenario: Ship Order Excludes From Balance  
&emsp;&emsp;    Given a customer with credit limit 1000  
&emsp;&emsp;    And a B2B order is placed for 2 Widget  
&emsp;&emsp;    When the order is shipped  
&emsp;&emsp;    Then the customer balance is 0  

<details markdown>
<summary>Rules exercised and logic log (2 transactions)</summary>


&nbsp;
&nbsp;


**Rules Used** in Scenario: Ship Order Excludes From Balance
```
  Customer  
    1. Derive Customer.balance as Sum(Order.amount_total Where lambda row: row.date_shipped is None))  
  Item  
    2. Derive Item.amount as Formula (1): Rule.formula(derive=models.Item.amount, as_expres [...]  
    3. Derive Item.unit_price as Copy(product.unit_price)  
  Order  
    4. Derive Order.amount_total as Sum(Item.amount Where  - None)  
    5. RowEvent Order._send_order_to_kafka()  
```
**Logic Log** in Scenario: Ship Order Excludes From Balance (2 transactions)
```
Logic Phase:		ROW LOGIC		(session=0x71d6952dca70) (sqlalchemy before_flush)			 - 2026-10-23 17:22:46,096 - logic_logger - INFO
..Product[2] {Update - client} id: 2, name: Widget, count_suppliers: 0, unit_price: 90.0000000000  row: 0x71d6952dd7c0  session: 0x71d6952dca70  ins_upd_dlt: upd, initial: upd - 2026-10-23 17:22:46,096 - logic_logger - INFO
..Order[None] {Insert - client} id: None, notes: Test order, customer_id: 19, CreatedOn: None, date_shipped: None, amount_total: None  row: 0x71d6952dc2c0  session: 0x71d6952dca70  ins_upd_dlt: ins, initial: ins - 2026-10-23 17:22:46,097 - logic_logger - INFO
..Order[None] {server aggregate_defaults: amount_total } id: None, notes: Test order, customer_id: 19, CreatedOn: None, date_shipped: None, amount_total: 0  row: 0x71d6952dc2c0  session: 0x71d6952dca70  ins_upd_dlt: ins, initial: ins - 2026-10-23 17:22:46,097 - logic_logger - INFO
..Item[None] {Insert - client} id: None, order_id: None, product_id: None, quantity: 2, amount: None, unit_price: None  row: 0x71d6952dc5f0  session: 0x71d6952dca70  ins_upd_dlt: ins, initial: ins - 2026-10-23 17:22:46,098 - logic_logger - INFO
..Item[None] {copy_rules for role: product - unit_price} id: None, order_id: None, product_id: None, quantity: 2, amount: None, unit_price: 90.0000000000  row: 0x71d6952dc5f0  session: 0x71d6952dca70  ins_upd_dlt: ins, initial: ins - 2026-10-23 17:22:46,098 - logic_logger - INFO
..Item[None] {Formula amount} id: None, order_id: None, product_id: None, quantity: 2, amount: 180.0000000000, unit_price: 90.0000000000  row: 0x71d6952dc5f0  session: 0x71d6952dca70  ins_upd_dlt: ins, initial: ins - 2026-10-23 17:22:46,098 - logic_logger - INFO
....Order[None] {Update - Adjusting order: amount_total} id: None, notes: Test order, customer_id: 19, CreatedOn: None, date_shipped: None, amount_total:  [0-->] 180.0000000000  row: 0x71d6952dc2c0  session: 0x71d6952dca70  ins_upd_dlt: upd, initial: upd - 2026-10-23 17:22:46,099 - logic_logger - INFO
......Customer[19] {Update - Adjusting customer: balance} id: 19, name: Test Customer 1792776166077, balance:  [0E-10-->] 180.0000000000, credit_limit: 1000.0000000000, email: None, email_opt_out: None  row: 0x71d6952dd5e0  session: 0x71d6952dca70  ins_upd_dlt: upd, initial: upd - 2026-10-23 17:22:46,099 - logic_logger - INFO
Logic Phase:		COMMIT LOGIC		(session=0x71d6952dca70)   										 - 2026-10-23 17:22:46,100 - logic_logger - INFO
Logic Phase:		AFTER_FLUSH LOGIC	(session=0x71d6952dca70)   										 - 2026-10-23 17:22:46,101 - logic_logger - INFO
..Order[19] {AfterFlush Event} id: 19, notes: Test order, customer_id: 19, CreatedOn: None, date_shipped: None, amount_total: 180.0000000000  row: 0x71d6952dc2c0  session: 0x71d6952dca70  ins_upd_dlt: ins, initial: ins - 2026-10-23 17:22:46,101 - logic_logger - INFO


Logic Phase:		ROW LOGIC		(session=0x71d69529a240) (sqlalchemy before_flush)			 - 2026-10-23 17:22:46,110 - logic_logger - INFO
..Order[19] {Update - client} id: 19, notes: Test order, customer_id: 19, CreatedOn: None, date_shipped:  [None-->] 2026-10-23 00:00:00, amount_total: 180.0000000000  row: 0x71d69529bc20  session: 0x71d69529a240  ins_upd_dlt: upd, initial: upd - 2026-10-23 17:22:46,111 - logic_logger - INFO
....Customer[19] {Update - Adjusting customer: balance} id: 19, name: Test Customer 1792776166077, balance:  [180.0000000000-->] 0E-10, credit_limit: 1000.0000000000, email: None, email_opt_out: None  row: 0x71d6952dcc50  session: 0x71d69529a240  ins_upd_dlt: upd, initial: upd - 2026-10-23 17:22:46,112 - logic_logger - INFO
Logic Phase:		COMMIT LOGIC		(session=0x71d69529a240)   										 - 2026-10-23 17:22:46,112 - logic_logger - INFO
Logic Phase:		AFTER_FLUSH LOGIC	(session=0x71d69529a240)   										 - 2026-10-23 17:22:46,113 - logic_logger - INFO
..Order[19] {AfterFlush Event} id: 19, notes: Test order, customer_id: 19, CreatedOn: None, date_shipped:  [None-->] 2026-10-23 00:00:00, amount_total: 180.0000000000  row: 0x71d69529bc20  session: 0x71d69529a240  ins_upd_dlt: upd, initial: upd - 2026-10-23 17:22:46,113 - logic_logger - INFO
..Order[19] {publish_kafka_message: topic='order_shipping', key={'id': 19}} id: 19, notes: Test order, customer_id: 19, CreatedOn: None, date_shipped:  [None-->] 2026-10-23 00:00:00, amount_total: 180.0000000000  row: 0x71d69529bc20  session: 0x71d69529a240  ins_upd_dlt: upd, initial: upd - 2026-10-23 17:22:46,117 - logic_logger - INFO

```
</details>

&nbsp;
&nbsp;

#### Scenario: Exceed Credit Rejected ✅
&emsp;  Scenario: Exceed Credit Rejected  
&emsp;&emsp;    Given a customer with credit limit 100  
&emsp;&emsp;    When a B2B order is placed for 2 Widget  
&emsp;&emsp;    Then the B2B order is rejected with message containing "exceeds credit limit"  
&emsp;&emsp;    And the customer balance is 0  

<details markdown>
<summary>Rules exercised and logic log (1 transaction)</summary>


&nbsp;
&nbsp;


**Rules Used** in Scenario: Exceed Credit Rejected
```
  Customer  
    1. Constraint Function: None  
    2. Derive Customer.balance as Sum(Order.amount_total Where lambda row: row.date_shipped is None))  
  Item  
    3. Derive Item.amount as Formula (1): Rule.formula(derive=models.Item.amount, as_expres [...]  
    4. Derive Item.unit_price as Copy(product.unit_price)  
  Order  
    5. Derive Order.amount_total as Sum(Item.amount Where  - None)  
```
**Logic Log** in Scenario: Exceed Credit Rejected (1 transaction)
```
Logic Phase:		ROW LOGIC		(session=0x71d6952dd040) (sqlalchemy before_flush)			 - 2026-10-23 17:22:46,150 - logic_logger - INFO
..Product[2] {Update - client} id: 2, name: Widget, count_suppliers: 0, unit_price: 90.0000000000  row: 0x71d6952de300  session: 0x71d6952dd040  ins_upd_dlt: upd, initial: upd - 2026-10-23 17:22:46,150 - logic_logger - INFO
..Order[None] {Insert - client} id: None, notes: Test order, customer_id: 20, CreatedOn: None, date_shipped: None, amount_total: None  row: 0x71d6952dd1f0  session: 0x71d6952dd040  ins_upd_dlt: ins, initial: ins - 2026-10-23 17:22:46,150 - logic_logger - INFO
..Order[None] {server aggregate_defaults: amount_total } id: None, notes: Test order, customer_id: 20, CreatedOn: None, date_shipped: None, amount_total: 0  row: 0x71d6952dd1f0  session: 0x71d6952dd040  ins_upd_dlt: ins, initial: ins - 2026-10-23 17:22:46,151 - logic_logger - INFO
..Item[None] {Insert - client} id: None, order_id: None, product_id: None, quantity: 2, amount: None, unit_price: None  row: 0x71d6952dcc20  session: 0x71d6952dd040  ins_upd_dlt: ins, initial: ins - 2026-10-23 17:22:46,151 - logic_logger - INFO
..Item[None] {copy_rules for role: product - unit_price} id: None, order_id: None, product_id: None, quantity: 2, amount: None, unit_price: 90.0000000000  row: 0x71d6952dcc20  session: 0x71d6952dd040  ins_upd_dlt: ins, initial: ins - 2026-10-23 17:22:46,152 - logic_logger - INFO
..Item[None] {Formula amount} id: None, order_id: None, product_id: None, quantity: 2, amount: 180.0000000000, unit_price: 90.0000000000  row: 0x71d6952dcc20  session: 0x71d6952dd040  ins_upd_dlt: ins, initial: ins - 2026-10-23 17:22:46,152 - logic_logger - INFO
....Order[None] {Update - Adjusting order: amount_total} id: None, notes: Test order, customer_id: 20, CreatedOn: None, date_shipped: None, amount_total:  [0-->] 180.0000000000  row: 0x71d6952dd1f0  session: 0x71d6952dd040  ins_upd_dlt: upd, initial: upd - 2026-10-23 17:22:46,153 - logic_logger - INFO
......Customer[20] {Update - Adjusting customer: balance} id: 20, name: Test Customer 1792776166130, balance:  [0E-10-->] 180.0000000000, credit_limit: 100.0000000000, email: None, email_opt_out: None  row: 0x71d6952de180  session: 0x71d6952dd040  ins_upd_dlt: upd, initial: upd - 2026-10-23 17:22:46,153 - logic_logger - INFO
......Customer[20] {Constraint Failure: Customer balance (180.0000000000) exceeds credit limit (100.0000000000)} id: 20, name: Test Customer 1792776166130, balance:  [0E-10-->] 180.0000000000, credit_limit: 100.0000000000, email: None, email_opt_out: None  row: 0x71d6952de180  session: 0x71d6952dd040  ins_upd_dlt: upd, initial: upd - 2026-10-23 17:22:46,153 - logic_logger - INFO

```
</details>

&nbsp;
&nbsp;

### Feature: Kafka Publish Shipping Notification  

&nbsp;
&nbsp;

#### Scenario: Shipping Notification Published ✅
&emsp;  Scenario: Shipping Notification Published  
&emsp;&emsp;    Given a customer with credit limit 1000  
&emsp;&emsp;    And a B2B order is placed for 1 Widget  
&emsp;&emsp;    When the order is shipped  
&emsp;&emsp;    Then a shipping notification is published to topic order_shipping  

<details markdown>
<summary>Rules exercised and logic log (2 transactions)</summary>


&nbsp;
&nbsp;


**Rules Used** in Scenario: Shipping Notification Published
```
  Customer  
    1. Derive Customer.balance as Sum(Order.amount_total Where lambda row: row.date_shipped is None))  
  Item  
    2. Derive Item.amount as Formula (1): Rule.formula(derive=models.Item.amount, as_expres [...]  
    3. Derive Item.unit_price as Copy(product.unit_price)  
  Order  
    4. Derive Order.amount_total as Sum(Item.amount Where  - None)  
    5. RowEvent Order._send_order_to_kafka()  
```
**Logic Log** in Scenario: Shipping Notification Published (2 transactions)
```
Logic Phase:		ROW LOGIC		(session=0x71d6952dcd40) (sqlalchemy before_flush)			 - 2026-10-23 17:22:46,181 - logic_logger - INFO
..Product[2] {Update - client} id: 2, name: Widget, count_suppliers: 0, unit_price: 90.0000000000  row: 0x71d6952de4e0  session: 0x71d6952dcd40  ins_upd_dlt: upd, initial: upd - 2026-10-23 17:22:46,181 - logic_logger - INFO
..Order[None] {Insert - client} id: None, notes: Test order, customer_id: 21, CreatedOn: None, date_shipped: None, amount_total: None  row: 0x71d6952dc3e0  session: 0x71d6952dcd40  ins_upd_dlt: ins, initial: ins - 2026-10-23 17:22:46,182 - logic_logger - INFO
..Order[None] {server aggregate_defaults: amount_total } id: None, notes: Test order, customer_id: 21, CreatedOn: None, date_shipped: None, amount_total: 0  row: 0x71d6952dc3e0  session: 0x71d6952dcd40  ins_upd_dlt: ins, initial: ins - 2026-10-23 17:22:46,182 - logic_logger - INFO
..Item[None] {Insert - client} id: None, order_id: None, product_id: None, quantity: 1, amount: None, unit_price: None  row: 0x71d6952de000  session: 0x71d6952dcd40  ins_upd_dlt: ins, initial: ins - 2026-10-23 17:22:46,183 - logic_logger - INFO
..Item[None] {copy_rules for role: product - unit_price} id: None, order_id: None, product_id: None, quantity: 1, amount: None, unit_price: 90.0000000000  row: 0x71d6952de000  session: 0x71d6952dcd40  ins_upd_dlt: ins, initial: ins - 2026-10-23 17:22:46,183 - logic_logger - INFO
..Item[None] {Formula amount} id: None, order_id: None, product_id: None, quantity: 1, amount: 90.0000000000, unit_price: 90.0000000000  row: 0x71d6952de000  session: 0x71d6952dcd40  ins_upd_dlt: ins, initial: ins - 2026-10-23 17:22:46,183 - logic_logger - INFO
....Order[None] {Update - Adjusting order: amount_total} id: None, notes: Test order, customer_id: 21, CreatedOn: None, date_shipped: None, amount_total:  [0-->] 90.0000000000  row: 0x71d6952dc3e0  session: 0x71d6952dcd40  ins_upd_dlt: upd, initial: upd - 2026-10-23 17:22:46,184 - logic_logger - INFO
......Customer[21] {Update - Adjusting customer: balance} id: 21, name: Test Customer 1792776166163, balance:  [0E-10-->] 90.0000000000, credit_limit: 1000.0000000000, email: None, email_opt_out: None  row: 0x71d6952de2d0  session: 0x71d6952dcd40  ins_upd_dlt: upd, initial: upd - 2026-10-23 17:22:46,184 - logic_logger - INFO
Logic Phase:		COMMIT LOGIC		(session=0x71d6952dcd40)   										 - 2026-10-23 17:22:46,185 - logic_logger - INFO
Logic Phase:		AFTER_FLUSH LOGIC	(session=0x71d6952dcd40)   										 - 2026-10-23 17:22:46,186 - logic_logger - INFO
..Order[20] {AfterFlush Event} id: 20, notes: Test order, customer_id: 21, CreatedOn: None, date_shipped: None, amount_total: 90.0000000000  row: 0x71d6952dc3e0  session: 0x71d6952dcd40  ins_upd_dlt: ins, initial: ins - 2026-10-23 17:22:46,187 - logic_logger - INFO


Logic Phase:		ROW LOGIC		(session=0x71d69529b410) (sqlalchemy before_flush)			 - 2026-10-23 17:22:46,198 - logic_logger - INFO
..Order[20] {Update - client} id: 20, notes: Test order, customer_id: 21, CreatedOn: None, date_shipped:  [None-->] 2026-10-23 00:00:00, amount_total: 90.0000000000  row: 0x71d695263350  session: 0x71d69529b410  ins_upd_dlt: upd, initial: upd - 2026-10-23 17:22:46,198 - logic_logger - INFO
....Customer[21] {Update - Adjusting customer: balance} id: 21, name: Test Customer 1792776166163, balance:  [90.0000000000-->] 0E-10, credit_limit: 1000.0000000000, email: None, email_opt_out: None  row: 0x71d6952dc8c0  session: 0x71d69529b410  ins_upd_dlt: upd, initial: upd - 2026-10-23 17:22:46,199 - logic_logger - INFO
Logic Phase:		COMMIT LOGIC		(session=0x71d69529b410)   										 - 2026-10-23 17:22:46,200 - logic_logger - INFO
Logic Phase:		AFTER_FLUSH LOGIC	(session=0x71d69529b410)   										 - 2026-10-23 17:22:46,201 - logic_logger - INFO
..Order[20] {AfterFlush Event} id: 20, notes: Test order, customer_id: 21, CreatedOn: None, date_shipped:  [None-->] 2026-10-23 00:00:00, amount_total: 90.0000000000  row: 0x71d695263350  session: 0x71d69529b410  ins_upd_dlt: upd, initial: upd - 2026-10-23 17:22:46,202 - logic_logger - INFO
..Order[20] {publish_kafka_message: topic='order_shipping', key={'id': 20}} id: 20, notes: Test order, customer_id: 21, CreatedOn: None, date_shipped:  [None-->] 2026-10-23 00:00:00, amount_total: 90.0000000000  row: 0x71d695263350  session: 0x71d69529b410  ins_upd_dlt: upd, initial: upd - 2026-10-23 17:22:46,204 - logic_logger - INFO

```
</details>

&nbsp;
&nbsp;

#### Scenario: Unshipped Order Not Published ✅
&emsp;  Scenario: Unshipped Order Not Published  
&emsp;&emsp;    Given a customer with credit limit 1000  
&emsp;&emsp;    When a B2B order is placed for 1 Widget  
&emsp;&emsp;    Then no shipping notification is published to topic order_shipping  

<details markdown>
<summary>Rules exercised and logic log (1 transaction)</summary>


&nbsp;
&nbsp;


**Rules Used** in Scenario: Unshipped Order Not Published
```
  Customer  
    1. Derive Customer.balance as Sum(Order.amount_total Where lambda row: row.date_shipped is None))  
  Item  
    2. Derive Item.amount as Formula (1): Rule.formula(derive=models.Item.amount, as_expres [...]  
    3. Derive Item.unit_price as Copy(product.unit_price)  
  Order  
    4. Derive Order.amount_total as Sum(Item.amount Where  - None)  
    5. RowEvent Order._send_order_to_kafka()  
```
**Logic Log** in Scenario: Unshipped Order Not Published (1 transaction)
```
Logic Phase:		ROW LOGIC		(session=0x71d6952de960) (sqlalchemy before_flush)			 - 2026-10-23 17:22:46,236 - logic_logger - INFO
..Product[2] {Update - client} id: 2, name: Widget, count_suppliers: 0, unit_price: 90.0000000000  row: 0x71d6952df350  session: 0x71d6952de960  ins_upd_dlt: upd, initial: upd - 2026-10-23 17:22:46,237 - logic_logger - INFO
..Order[None] {Insert - client} id: None, notes: Test order, customer_id: 22, CreatedOn: None, date_shipped: None, amount_total: None  row: 0x71d6952dd1c0  session: 0x71d6952de960  ins_upd_dlt: ins, initial: ins - 2026-10-23 17:22:46,237 - logic_logger - INFO
..Order[None] {server aggregate_defaults: amount_total } id: None, notes: Test order, customer_id: 22, CreatedOn: None, date_shipped: None, amount_total: 0  row: 0x71d6952dd1c0  session: 0x71d6952de960  ins_upd_dlt: ins, initial: ins - 2026-10-23 17:22:46,238 - logic_logger - INFO
..Item[None] {Insert - client} id: None, order_id: None, product_id: None, quantity: 1, amount: None, unit_price: None  row: 0x71d6952dcbf0  session: 0x71d6952de960  ins_upd_dlt: ins, initial: ins - 2026-10-23 17:22:46,238 - logic_logger - INFO
..Item[None] {copy_rules for role: product - unit_price} id: None, order_id: None, product_id: None, quantity: 1, amount: None, unit_price: 90.0000000000  row: 0x71d6952dcbf0  session: 0x71d6952de960  ins_upd_dlt: ins, initial: ins - 2026-10-23 17:22:46,239 - logic_logger - INFO
..Item[None] {Formula amount} id: None, order_id: None, product_id: None, quantity: 1, amount: 90.0000000000, unit_price: 90.0000000000  row: 0x71d6952dcbf0  session: 0x71d6952de960  ins_upd_dlt: ins, initial: ins - 2026-10-23 17:22:46,239 - logic_logger - INFO
....Order[None] {Update - Adjusting order: amount_total} id: None, notes: Test order, customer_id: 22, CreatedOn: None, date_shipped: None, amount_total:  [0-->] 90.0000000000  row: 0x71d6952dd1c0  session: 0x71d6952de960  ins_upd_dlt: upd, initial: upd - 2026-10-23 17:22:46,239 - logic_logger - INFO
......Customer[22] {Update - Adjusting customer: balance} id: 22, name: Test Customer 1792776166217, balance:  [0E-10-->] 90.0000000000, credit_limit: 1000.0000000000, email: None, email_opt_out: None  row: 0x71d6952df200  session: 0x71d6952de960  ins_upd_dlt: upd, initial: upd - 2026-10-23 17:22:46,240 - logic_logger - INFO
Logic Phase:		COMMIT LOGIC		(session=0x71d6952de960)   										 - 2026-10-23 17:22:46,240 - logic_logger - INFO
Logic Phase:		AFTER_FLUSH LOGIC	(session=0x71d6952de960)   										 - 2026-10-23 17:22:46,243 - logic_logger - INFO
..Order[21] {AfterFlush Event} id: 21, notes: Test order, customer_id: 22, CreatedOn: None, date_shipped: None, amount_total: 90.0000000000  row: 0x71d6952dd1c0  session: 0x71d6952de960  ins_upd_dlt: ins, initial: ins - 2026-10-23 17:22:46,243 - logic_logger - INFO

```
</details>

&nbsp;
&nbsp;

### Feature: Kafka Subscribe Order Integration  

&nbsp;
&nbsp;

#### Scenario: Inbound Order Message Processed ✅
&emsp;  Scenario: Inbound Order Message Processed  
&emsp;&emsp;    Given a customer with credit limit 1000  
&emsp;&emsp;    When an order_b2b message arrives for 2 Widget and 1 Gadget  
&emsp;&emsp;    Then the message is processed  
&emsp;&emsp;    And the order belongs to the customer  
&emsp;&emsp;    And the order has 2 items  
&emsp;&emsp;    And the order has 2 of Widget  
&emsp;&emsp;    And the order has 1 of Gadget  
&emsp;&emsp;    And the customer balance is 330  

<details markdown>
<summary>Rules exercised and logic log (1 transaction)</summary>


&nbsp;
&nbsp;


**Rules Used** in Scenario: Inbound Order Message Processed
```
  Customer  
    1. Derive Customer.balance as Sum(Order.amount_total Where lambda row: row.date_shipped is None))  
  Item  
    2. Derive Item.amount as Formula (1): Rule.formula(derive=models.Item.amount, as_expres [...]  
    3. Derive Item.unit_price as Copy(product.unit_price)  
  Order  
    4. Derive Order.amount_total as Sum(Item.amount Where  - None)  
    5. RowEvent Order._send_order_to_kafka()  
  OrderB2bMessage  
    6. RowEvent OrderB2bMessage._publish_order_b2b_blob()  
```
**Logic Log** in Scenario: Inbound Order Message Processed (1 transaction)
```
Logic Phase:		ROW LOGIC		(session=0x71d6952deb40) (sqlalchemy before_flush)			 - 2026-10-23 17:22:46,278 - logic_logger - INFO
..Order[None] {Insert - client} id: None, notes: Kafka order from sales, customer_id: 23, CreatedOn: None, date_shipped: None, amount_total: None  row: 0x71d6952dd790  session: 0x71d6952deb40  ins_upd_dlt: ins, initial: ins - 2026-10-23 17:22:46,279 - logic_logger - INFO
..Order[None] {server aggregate_defaults: amount_total } id: None, notes: Kafka order from sales, customer_id: 23, CreatedOn: None, date_shipped: None, amount_total: 0  row: 0x71d6952dd790  session: 0x71d6952deb40  ins_upd_dlt: ins, initial: ins - 2026-10-23 17:22:46,279 - logic_logger - INFO
..Item[None] {Insert - client} id: None, order_id: None, product_id: 2, quantity: 2, amount: None, unit_price: None  row: 0x71d6952dc800  session: 0x71d6952deb40  ins_upd_dlt: ins, initial: ins - 2026-10-23 17:22:46,280 - logic_logger - INFO
..Item[None] {copy_rules for role: product - unit_price} id: None, order_id: None, product_id: 2, quantity: 2, amount: None, unit_price: 90.0000000000  row: 0x71d6952dc800  session: 0x71d6952deb40  ins_upd_dlt: ins, initial: ins - 2026-10-23 17:22:46,281 - logic_logger - INFO
..Item[None] {Formula amount} id: None, order_id: None, product_id: 2, quantity: 2, amount: 180.0000000000, unit_price: 90.0000000000  row: 0x71d6952dc800  session: 0x71d6952deb40  ins_upd_dlt: ins, initial: ins - 2026-10-23 17:22:46,281 - logic_logger - INFO
....Order[None] {Update - Adjusting order: amount_total} id: None, notes: Kafka order from sales, customer_id: 23, CreatedOn: None, date_shipped: None, amount_total:  [0-->] 180.0000000000  row: 0x71d6952dd790  session: 0x71d6952deb40  ins_upd_dlt: upd, initial: upd - 2026-10-23 17:22:46,282 - logic_logger - INFO
......Customer[23] {Update - Adjusting customer: balance} id: 23, name: Test Customer 1792776166256, balance:  [0E-10-->] 180.0000000000, credit_limit: 1000.0000000000, email: None, email_opt_out: None  row: 0x71d6952dfa10  session: 0x71d6952deb40  ins_upd_dlt: upd, initial: upd - 2026-10-23 17:22:46,282 - logic_logger - INFO
..Item[None] {Insert - client} id: None, order_id: None, product_id: 1, quantity: 1, amount: None, unit_price: None  row: 0x71d6952decf0  session: 0x71d6952deb40  ins_upd_dlt: ins, initial: ins - 2026-10-23 17:22:46,283 - logic_logger - INFO
..Item[None] {copy_rules for role: product - unit_price} id: None, order_id: None, product_id: 1, quantity: 1, amount: None, unit_price: 150.0000000000  row: 0x71d6952decf0  session: 0x71d6952deb40  ins_upd_dlt: ins, initial: ins - 2026-10-23 17:22:46,284 - logic_logger - INFO
..Item[None] {Formula amount} id: None, order_id: None, product_id: 1, quantity: 1, amount: 150.0000000000, unit_price: 150.0000000000  row: 0x71d6952decf0  session: 0x71d6952deb40  ins_upd_dlt: ins, initial: ins - 2026-10-23 17:22:46,284 - logic_logger - INFO
....Order[None] {Update - Adjusting order: amount_total} id: None, notes: Kafka order from sales, customer_id: 23, CreatedOn: None, date_shipped: None, amount_total:  [180.0000000000-->] 330.0000000000  row: 0x71d6952dd790  session: 0x71d6952deb40  ins_upd_dlt: upd, initial: upd - 2026-10-23 17:22:46,285 - logic_logger - INFO
......Customer[23] {Update - Adjusting customer: balance} id: 23, name: Test Customer 1792776166256, balance:  [180.0000000000-->] 330.0000000000, credit_limit: 1000.0000000000, email: None, email_opt_out: None  row: 0x71d6952dfa10  session: 0x71d6952deb40  ins_upd_dlt: upd, initial: upd - 2026-10-23 17:22:46,285 - logic_logger - INFO
..OrderB2bMessage[None] {Insert - client} id: None, received_at: 2026-10-23 17:22:46.277729, payload: {"Account": "Test Customer 1792776166256", "Notes": "Kafka order from sales", "Items": [{"Name": "Widget", "QuantityOrdered": 2}, {"Name": "Gadget", "QuantityOrdered": 1}]}, is_processed: True, error_text: None  row: 0x71d6952dd5b0  session: 0x71d6952deb40  ins_upd_dlt: ins, initial: ins - 2026-10-23 17:22:46,286 - logic_logger - INFO
Logic Phase:		COMMIT LOGIC		(session=0x71d6952deb40)   										 - 2026-10-23 17:22:46,286 - logic_logger - INFO
Logic Phase:		AFTER_FLUSH LOGIC	(session=0x71d6952deb40)   										 - 2026-10-23 17:22:46,289 - logic_logger - INFO
..Order[22] {AfterFlush Event} id: 22, notes: Kafka order from sales, customer_id: 23, CreatedOn: None, date_shipped: None, amount_total: 330.0000000000  row: 0x71d6952dd790  session: 0x71d6952deb40  ins_upd_dlt: ins, initial: ins - 2026-10-23 17:22:46,289 - logic_logger - INFO
..OrderB2bMessage[7] {AfterFlush Event} id: 7, received_at: 2026-10-23 17:22:46.277729, payload: {"Account": "Test Customer 1792776166256", "Notes": "Kafka order from sales", "Items": [{"Name": "Widget", "QuantityOrdered": 2}, {"Name": "Gadget", "QuantityOrdered": 1}]}, is_processed: True, error_text: None  row: 0x71d6952dd5b0  session: 0x71d6952deb40  ins_upd_dlt: ins, initial: ins - 2026-10-23 17:22:46,289 - logic_logger - INFO
..OrderB2bMessage[7] {_publish_order_b2b_blob: skipping - blob.id=7 already is_processed} id: 7, received_at: 2026-10-23 17:22:46.277729, payload: {"Account": "Test Customer 1792776166256", "Notes": "Kafka order from sales", "Items": [{"Name": "Widget", "QuantityOrdered": 2}, {"Name": "Gadget", "QuantityOrdered": 1}]}, is_processed: True, error_text: None  row: 0x71d6952dd5b0  session: 0x71d6952deb40  ins_upd_dlt: ins, initial: ins - 2026-10-23 17:22:46,289 - logic_logger - INFO

```
</details>

&nbsp;
&nbsp;

#### Scenario: Inbound Message With Unknown Product Rejected ✅
&emsp;  Scenario: Inbound Message With Unknown Product Rejected  
&emsp;&emsp;    Given a customer with credit limit 1000  
&emsp;&emsp;    When an order_b2b message arrives for an unknown product  
&emsp;&emsp;    Then the message is rejected  
&emsp;&emsp;    And the customer balance is 0  

_No rules fired in this scenario's logic log._

&nbsp;
&nbsp;

#### Scenario: Inbound Message Over Credit Limit Rejected ✅
&emsp;  Scenario: Inbound Message Over Credit Limit Rejected  
&emsp;&emsp;    Given a customer with credit limit 100  
&emsp;&emsp;    When an order_b2b message arrives for 2 Widget and 1 Gadget  
&emsp;&emsp;    Then the message is rejected  
&emsp;&emsp;    And the customer balance is 0  

<details markdown>
<summary>Rules exercised and logic log (1 transaction)</summary>


&nbsp;
&nbsp;


**Rules Used** in Scenario: Inbound Message Over Credit Limit Rejected
```
  Customer  
    1. Constraint Function: None  
    2. Derive Customer.balance as Sum(Order.amount_total Where lambda row: row.date_shipped is None))  
  Item  
    3. Derive Item.amount as Formula (1): Rule.formula(derive=models.Item.amount, as_expres [...]  
    4. Derive Item.unit_price as Copy(product.unit_price)  
  Order  
    5. Derive Order.amount_total as Sum(Item.amount Where  - None)  
```
**Logic Log** in Scenario: Inbound Message Over Credit Limit Rejected (1 transaction)
```
Logic Phase:		ROW LOGIC		(session=0x71d6952e5610) (sqlalchemy before_flush)			 - 2026-10-23 17:22:46,404 - logic_logger - INFO
..Order[None] {Insert - client} id: None, notes: Kafka order from sales, customer_id: 25, CreatedOn: None, date_shipped: None, amount_total: None  row: 0x71d6952e4cb0  session: 0x71d6952e5610  ins_upd_dlt: ins, initial: ins - 2026-10-23 17:22:46,404 - logic_logger - INFO
..Order[None] {server aggregate_defaults: amount_total } id: None, notes: Kafka order from sales, customer_id: 25, CreatedOn: None, date_shipped: None, amount_total: 0  row: 0x71d6952e4cb0  session: 0x71d6952e5610  ins_upd_dlt: ins, initial: ins - 2026-10-23 17:22:46,405 - logic_logger - INFO
..Item[None] {Insert - client} id: None, order_id: None, product_id: 2, quantity: 2, amount: None, unit_price: None  row: 0x71d6952e5010  session: 0x71d6952e5610  ins_upd_dlt: ins, initial: ins - 2026-10-23 17:22:46,406 - logic_logger - INFO
..Item[None] {copy_rules for role: product - unit_price} id: None, order_id: None, product_id: 2, quantity: 2, amount: None, unit_price: 90.0000000000  row: 0x71d6952e5010  session: 0x71d6952e5610  ins_upd_dlt: ins, initial: ins - 2026-10-23 17:22:46,407 - logic_logger - INFO
..Item[None] {Formula amount} id: None, order_id: None, product_id: 2, quantity: 2, amount: 180.0000000000, unit_price: 90.0000000000  row: 0x71d6952e5010  session: 0x71d6952e5610  ins_upd_dlt: ins, initial: ins - 2026-10-23 17:22:46,407 - logic_logger - INFO
....Order[None] {Update - Adjusting order: amount_total} id: None, notes: Kafka order from sales, customer_id: 25, CreatedOn: None, date_shipped: None, amount_total:  [0-->] 180.0000000000  row: 0x71d6952e4cb0  session: 0x71d6952e5610  ins_upd_dlt: upd, initial: upd - 2026-10-23 17:22:46,407 - logic_logger - INFO
......Customer[25] {Update - Adjusting customer: balance} id: 25, name: Test Customer 1792776166386, balance:  [0E-10-->] 180.0000000000, credit_limit: 100.0000000000, email: None, email_opt_out: None  row: 0x71d6952e64b0  session: 0x71d6952e5610  ins_upd_dlt: upd, initial: upd - 2026-10-23 17:22:46,408 - logic_logger - INFO
......Customer[25] {Constraint Failure: Customer balance (180.0000000000) exceeds credit limit (100.0000000000)} id: 25, name: Test Customer 1792776166386, balance:  [0E-10-->] 180.0000000000, credit_limit: 100.0000000000, email: None, email_opt_out: None  row: 0x71d6952e64b0  session: 0x71d6952e5610  ins_upd_dlt: upd, initial: upd - 2026-10-23 17:22:46,408 - logic_logger - INFO

```
</details>

&nbsp;
&nbsp;

### Feature: Row-Level Security  

&nbsp;
&nbsp;

#### Scenario: Sales Role Sees Limited Customers ✅
&emsp;  Scenario: Sales Role Sees Limited Customers  
&emsp;&emsp;    Given a high-credit customer, a low-credit customer and a low-credit customer with a balance  
&emsp;&emsp;    When a user with the sales role queries the Customer list  _(skipped)_  
&emsp;&emsp;    Then the list includes the high-credit customer and the customer with a balance  _(skipped)_  
&emsp;&emsp;    And the list excludes the low-credit customer  _(skipped)_  

_No rules fired in this scenario's logic log._
&nbsp;&nbsp;  
/workspaces/codespaces_mgr/demo_eai/test/api_logic_server_behave/behave_run.py completed at October 23, 2026 17:22:46  


&nbsp;
&nbsp;

## Provenance

| | |
|---|---|
| Generated | October 23, 2026 17:22 |
| Generator | `requirements_traceability_report.py` 2.9 |
| Report text from | reports/Requirements Traceability Report Template.md (sha256 e0c810e2e22e) |
| Tests last ran | October 23, 2026 17:22 |
| Project | demo_eai |
| Source commit | 685044c (uncommitted changes) |
| Project created | October 23, 2026 17:01:00 |
| Requirement files read | `docs/requirements/check_credit/requirements.md` (sha256 98ce1a43)<br>`docs/requirements/demo_eai/requirements.md` (sha256 672062e9)<br>`docs/requirements/kafka_publish_shipping/requirements.md` (sha256 0f6b7cd6)<br>`docs/requirements/kafka_subscribe_order/requirements.md` (sha256 350b98cb) |
| Regenerate | `python requirements_traceability_report.py run`, from `test/api_logic_server_behave` |

_The report is derived from the project's files and the last test run; nothing in it is stored anywhere else, so regenerating it always reflects the project as it is now._

