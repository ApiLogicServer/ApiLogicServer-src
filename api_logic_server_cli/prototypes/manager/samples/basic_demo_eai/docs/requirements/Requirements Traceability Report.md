# Requirements Traceability Report

This report shows requirements, the rules created from them, and the tests created from those rules.

This project began as natural-language requirements, fleshed out by AI into a running system of business rules that are *executable documentation*. This report is how you govern the result.

A governable system is one you can **read**, **trust**, and **maintain**: each requirement is listed beside the rules that implement it (*read*); the tests and logic logs show those rules running (*trust*); re-run it after any change and it flags the gaps — an untested requirement, an untraced rule, a channel no test checks (*maintain*).

It is generated from the project's own files, nothing written by hand, so it is as current as the last run and covers the whole project, not a sample. Open **Background** (below the summary) for what the terms mean, how to read the report, and what it can and can't tell you.


**Project:** basic_demo_eai &nbsp;|&nbsp; **Generated:** November 19, 2026 18:04 &nbsp;|&nbsp; **Rules:** 18 &nbsp;|&nbsp; **Test scenarios:** 30 &nbsp;|&nbsp; **Generator:** requirements_traceability_report.py 2.15

**Last test run:** November 19, 2026 17:41, took 3.4 s (23m before this report; test results and logic logs below are from that run)


&nbsp;
&nbsp;

## At a Glance

**✅ 6 requirement(s), all implemented; 6 tested; 30 of 30 scenarios passed; last run 23m ago.**

| | |
|---|---|
| Requirements | 6 (6 implemented) |
| Tested | 6 of 6 |
| Last test run | ✅ 30 passed, 0 failed (November 19, 2026 17:41, 23m ago); took 3.4 s |
| Rules | 18 (15 declarative, 0 Python functions, 3 Python events) |
| Rules shown running in a test log | 17 of 18 |
| Security | enabled (Keycloak provider); 11 role(s), 2 row-level grant(s) |
| Messages and APIs | 2 Kafka topic(s) in, 2 out; 6 HTTP endpoint(s) |
| Kafka | live (localhost:9092): subscribe tested through the broker; outbound messages checked in the log |

_Status: ✅ every requirement is implemented and tested, all scenarios pass, and the results are current. ⚠ a requirement is untested or unimplemented, there is no test run, or files changed since the last run. ❌ a scenario failed. This reports what was traced and tested, not that the system is correct._

**About this project** _(from [readme.md](../../readme.md))_

This app illustrates using IntegrationServices for B2B push-style integrations with APIs, and internal integration with messages.

**This sample** is a single API Logic Server providing APIs *and logic* — it both
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

Every requirement should have rules that implement it, and tests that prove it. This section checks that chain in both directions: a requirement missing rules or tests is a gap, and rules or tests that belong to no requirement are flagged too. The matching uses the requirement names, `Feature:` names and `§N` tags that requirements, code and tests share. Requirements may be grouped into a use case (for example Place Order), read from the logic folder or the prompt; the level is optional.


&nbsp;

### Coverage summary

| Measure | Result |
|---|---|
| Requirements | 6 |
| Implemented (at least one file) | 6 of 6 |
| Tested (at least one scenario) | 6 of 6 |
| Implementation not traced to a requirement | `logic/logic_discovery/system/all_classes_stamping.py` |
| Tests not traced to a requirement | none |
| Test results (last run) | ✅ 30 passed, 0 failed; took 3.4 s |
| Scenarios with a logic log | 30 of 30 |
| Rules seen in at least one scenario's log | 17 of 18 (1 not counted: the engine's log does not name `all classes.early_row_event → handle_all()`, so it cannot be matched) |

_Test results are as current as the last run (see the header). A gap is any requirement with no implementation or no test._

<details markdown>
<summary>How to read this table</summary>

Test results are read from `logs/behave.log`, so they are only as current as that run. Not recorded here: which version of a requirement the code was built against, and which clause of a requirement a given rule serves.

</details>



&nbsp;

### Traceability matrix

| Requirement | Implemented by | Rules | Tests |
|---|---|---|---|
| §1 Business Logic — Check Credit | [logic/logic_discovery/check_credit.py](../../logic/logic_discovery/check_credit.py) | 5 | ✅ 11 scenario(s): 11 passed |
| §2 B2B API — Accept orders from external partners | [api/api_discovery/order_b2b_service.py](../../api/api_discovery/order_b2b_service.py) | 0 | ✅ 4 scenario(s): 4 passed |
| §3 Kafka Subscribe — Inbound orders from sales channel | [logic/logic_discovery/order_b2b_consume.py](../../logic/logic_discovery/order_b2b_consume.py)<br>[integration/kafka/kafka_subscribe_discovery/order_b2b.py](../../integration/kafka/kafka_subscribe_discovery/order_b2b.py)<br>[integration/OrderB2bMapper.py](../../integration/OrderB2bMapper.py)<br>[api/api_discovery/order_b2b_kafka_consume_debug.py](../../api/api_discovery/order_b2b_kafka_consume_debug.py) | 1 | ✅ 3 scenario(s): 3 passed |
| §4 Kafka Publish — Notify shipping on dispatch | [logic/logic_discovery/order_shipping_publish.py](../../logic/logic_discovery/order_shipping_publish.py)<br>[integration/kafka/kafka_publish_discovery/order_shipping.py](../../integration/kafka/kafka_publish_discovery/order_shipping.py) | 1 | ✅ 2 scenario(s): 2 passed |
| §5 Security | [security/declare_security.py](../../security/declare_security.py) | 0 | ✅ 1 scenario(s): 1 passed |
| §6 Operations Dashboard — Order flow | [logic/logic_discovery/order_flow_totals.py](../../logic/logic_discovery/order_flow_totals.py)<br>[api/api_discovery/dashboard_services.py](../../api/api_discovery/dashboard_services.py) | 10 | ✅ 9 scenario(s): 9 passed |


&nbsp;

### Rule coverage by tests

| Rule | Requirement | Seen in |
|---|---|---|
| `Customer: credit_limit is None or balance is None or balance <= credit_limit` | §1 Business Logic — Check Credit | 2: Rejected Request Is Recorded; Order Exceeding Credit Rejected |
| `Customer.balance = sum(Order.amount_total) where date_shipped is None` | §1 Business Logic — Check Credit | 26: Partner Order Accepted; Accepted Request Is Recorded; Rejected Request Is Recorded; +23 more |
| `Order.amount_total = sum(Item.amount)` | §1 Business Logic — Check Credit | 25: Partner Order Accepted; Accepted Request Is Recorded; Rejected Request Is Recorded; +22 more |
| `Item.amount = quantity * unit_price` | §1 Business Logic — Check Credit | 25: Partner Order Accepted; Accepted Request Is Recorded; Rejected Request Is Recorded; +22 more |
| `Item.unit_price = copy of Product.unit_price` | §1 Business Logic — Check Credit | 25: Partner Order Accepted; Accepted Request Is Recorded; Rejected Request Is Recorded; +22 more |
| `OrderB2bMessage.after_flush_row_event → _publish_order_b2b()` | §3 Kafka Subscribe — Inbound orders from sales channel | 5: Order Message Delivered; Unknown Account Message Rejected; Rejected Message Keeps Its Error (live Kafka only); +2 more |
| `DailyFlow.order_count = count(Order)` | §6 Operations Dashboard — Order flow | 26: Partner Order Accepted; Accepted Request Is Recorded; Rejected Request Is Recorded; +23 more |
| `DailyFlow.order_amount = sum(Order.amount_total)` | §6 Operations Dashboard — Order flow | 26: Partner Order Accepted; Accepted Request Is Recorded; Rejected Request Is Recorded; +23 more |
| `DailyFlow.message_received = count(OrderB2bMessage)` | §6 Operations Dashboard — Order flow | 5: Order Message Delivered; Unknown Account Message Rejected; Rejected Message Keeps Its Error (live Kafka only); +2 more |
| `DailyFlow.message_processed = count(OrderB2bMessage) where is_processed == True` | §6 Operations Dashboard — Order flow | 5: Order Message Delivered; Unknown Account Message Rejected; Rejected Message Keeps Its Error (live Kafka only); +2 more |
| `DailyFlow.message_failed = count(OrderB2bMessage) where error_text is not None` | §6 Operations Dashboard — Order flow | 5: Order Message Delivered; Unknown Account Message Rejected; Rejected Message Keeps Its Error (live Kafka only); +2 more |
| `DailyFlow.message_stuck = (message_received or 0) - (message_processed or 0) - (message_failed or 0)` | §6 Operations Dashboard — Order flow | 6: Order Message Delivered; Unknown Account Message Rejected; Rejected Message Keeps Its Error (live Kafka only); +3 more |
| `DailyFlow.request_received = count(OrderB2bRequest)` | §6 Operations Dashboard — Order flow | 24: Partner Order Accepted; Unknown Account Rejected; Accepted Request Is Recorded; +21 more |
| `DailyFlow.request_processed = count(OrderB2bRequest) where is_processed == True` | §6 Operations Dashboard — Order flow | 24: Partner Order Accepted; Unknown Account Rejected; Accepted Request Is Recorded; +21 more |
| `DailyFlow.request_failed = count(OrderB2bRequest) where error_text is not None` | §6 Operations Dashboard — Order flow | 24: Partner Order Accepted; Unknown Account Rejected; Accepted Request Is Recorded; +21 more |
| `DailyFlow.request_stuck = (request_received or 0) - (request_processed or 0) - (request_failed or 0)` | §6 Operations Dashboard — Order flow | 25: Partner Order Accepted; Unknown Account Rejected; Accepted Request Is Recorded; +22 more |
| `Order.after_flush_row_event → _send_order_to_shipping()` | §4 Kafka Publish — Notify shipping on dispatch | 24: Partner Order Accepted; Accepted Request Is Recorded; Good Order Placed; +21 more |
| `all classes.early_row_event → handle_all()` | (none) | n/a - cannot be matched to the engine's log |

_"Seen" means the engine's log shows the rule ran, not proof that it took effect._

<details markdown>
<summary>How to read this table</summary>

"Seen" means the engine reported running the rule in that scenario's logic log. A scenario can only contribute if it has a log (see the coverage summary): a test that does not open one writes into whichever log was open last, and its rules are then credited to that scenario, or to the shared log. An event's function runs on every commit of its class, and its own condition decides whether it acts, so seen does not mean it took effect. A constraint appears in the log only when it rejects a transaction, so it is seen only in scenarios that make it reject. "Not seen" therefore means no log shows it, not that no test ran it.

</details>



&nbsp;

### Requirements in detail

**18 rules** in 5 files: 15 declarative (sum, count, copy, formula and constraint expressions), 0 backed by a Python function, 3 events (Python).

_Declarative rules are read straight from their declarations. Functions and events are Python code, so for those the report shows the docstring — it does not analyze the code._

Each requirement is followed by the rules and handlers in the files that implement it. Logic diagrams are shown (click to expand) where they exist.

<details markdown>
<summary>How to create or refresh the logic diagrams</summary>

Needs Graphviz (`brew install graphviz`). Tell your AI assistant:

```
create logic diagram for each requirement
```

or run this from the Manager root (`manager`):

```
python system/ApiLogicServer-Internal-Dev/logic_diagram_gv.py samples/basic_demo_eai --each
```

Each diagram is saved under `docs/requirements/<name>/logic_diagrams/`. Then regenerate this report (`python requirements_traceability_report.py run`, from `test/api_logic_server_behave`).

</details>

&nbsp;


#### §1 Business Logic — Check Credit

Tests: ✅ 11 scenario(s): 11 passed

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
| `Customer: credit_limit is None or balance is None or balance <= credit_limit` | constraint | declarative | Error: Customer balance ({row.balance}) exceeds credit limit ({row.credit_limit}) | [check_credit.py](../../logic/logic_discovery/check_credit.py) |
| `Customer.balance = sum(Order.amount_total) where date_shipped is None` | sum | declarative |  | [check_credit.py](../../logic/logic_discovery/check_credit.py) |
| `Order.amount_total = sum(Item.amount)` | sum | declarative |  | [check_credit.py](../../logic/logic_discovery/check_credit.py) |
| `Item.amount = quantity * unit_price` | formula | declarative |  | [check_credit.py](../../logic/logic_discovery/check_credit.py) |
| `Item.unit_price = copy of Product.unit_price` | copy | declarative |  | [check_credit.py](../../logic/logic_discovery/check_credit.py) |

<details markdown>
<summary>Logic diagram: check_credit</summary>

<table><tr valign="top">
<td width="65%">

![logic diagram: check_credit](check_credit/logic_diagrams/logic_diagram_check_credit.svg)

</td>
<td width="35%">

**Rules**

1. `unit_price = copy(unit_price)`<br>
2. `amount = quantity * unit_price`<br>
3. `amount_total = sum(amount)`<br>
4. `balance = sum(amount_total where date_shipped)`<br>
5. constraint: `Customer`

</td>
</tr></table>

</details>

#### §2 B2B API — Accept orders from external partners

Tests: ✅ 4 scenario(s): 4 passed

```
Feature: B2B Order Integration

  Scenario: Accept order from external partner
    Given an inbound B2B order in partner format (message_formats/order_b2b.json)
    When the order is received via a Custom API endpoint named OrderB2B
    Then map Account to Customer by name
    And map Items.Name to Product by name
    And map Items.QuantityOrdered to Item.quantity
    And record each request, with its outcome, for the order flow dashboard
```

| Rule / item | Type | Logic | Description | Where |
|---|---|---|---|---|
| `HTTP in: POST /api/OrderB2B/OrderB2B` | http | handler (Python) | API service OrderB2B: records the request, creates the Order and its Items (the rules derive the rest), and records the outcome on the request row. | [order_b2b_service.py](../../api/api_discovery/order_b2b_service.py) |

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
| `OrderB2bMessage.after_flush_row_event → _publish_order_b2b()` | after_flush_row_event | event (Python) | OrderB2bMessage event: publishes the raw blob to order_b2b_processed after Tx 1 commits, so Consumer 2 parses it in a clean Tx 2 (2-message pattern). | [order_b2b_consume.py](../../logic/logic_discovery/order_b2b_consume.py) |
| `Kafka in: order_b2b` | kafka | handler (Python) | Kafka subscribe order_b2b: Consumer 1 - save the raw blob and commit (Tx 1); the row event publishes it on. | [order_b2b.py](../../integration/kafka/kafka_subscribe_discovery/order_b2b.py) |
| `Kafka in: order_b2b_processed` | kafka | handler (Python) | Kafka subscribe order_b2b_processed: Consumer 2 - parse + persist the Order (Tx 2); a failure is recorded on the blob. | [order_b2b.py](../../integration/kafka/kafka_subscribe_discovery/order_b2b.py) |
| `OrderB2bMapper.py` | module |  | Feature: Kafka Subscribe Order Integration | [OrderB2bMapper.py](../../integration/OrderB2bMapper.py) |
| `HTTP in: GET /consume_debug/order_b2b` | http | handler (Python) | EAI debug (development only, no authentication): sends the message in ?file= to the topic, live through Kafka or simulated | [order_b2b_kafka_consume_debug.py](../../api/api_discovery/order_b2b_kafka_consume_debug.py) |
| `HTTP in: POST /consume_debug/order_b2b/reset` | http | handler (Python) | EAI debug (development only, destructive): purges the messages in the pipeline's topics | [order_b2b_kafka_consume_debug.py](../../api/api_discovery/order_b2b_kafka_consume_debug.py) |

<details markdown>
<summary>Logic diagram: order_b2b_consume</summary>

<table><tr valign="top">
<td width="65%">

![logic diagram: order_b2b_consume](order_b2b_consume/logic_diagrams/logic_diagram_order_b2b_consume.svg)

</td>
<td width="35%">

**Rules**

1. `OrderB2bMessage` → `_publish_order_b2b` (after_flush) — OrderB2bMessage event: publishes the raw blob to order_b2b_processed after Tx 1 commits, so Consumer 2

</td>
</tr></table>

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
| `Order.after_flush_row_event → _send_order_to_shipping()` | after_flush_row_event | event (Python) | Order publish: sends the Order to Kafka topic order_shipping when date_shipped is set and differs from its prior value (old_row is None on insert), shaped by example as message_formats/order_shipping.json. | [order_shipping_publish.py](../../logic/logic_discovery/order_shipping_publish.py) |
| `order_shipping.py` | module |  | Feature: Kafka Publish Shipping Notification | [order_shipping.py](../../integration/kafka/kafka_publish_discovery/order_shipping.py) |

<details markdown>
<summary>Logic diagram: order_shipping_publish</summary>

<table><tr valign="top">
<td width="65%">

![logic diagram: order_shipping_publish](order_shipping_publish/logic_diagrams/logic_diagram_order_shipping_publish.svg)

</td>
<td width="35%">

**Rules**

1. `Order` → `_send_order_to_shipping` (after_flush) — Order publish: sends the Order to Kafka topic order_shipping when date_shipped is set and differs from its prior

</td>
</tr></table>

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
| `Grant on Customer to role sales: credit_limit >= 3000` | grant | declarative |  | [declare_security.py](../../security/declare_security.py) |
| `Grant on Customer to role sales: balance > 0` | grant | declarative |  | [declare_security.py](../../security/declare_security.py) |

#### §6 Operations Dashboard — Order flow

Tests: ✅ 9 scenario(s): 9 passed

```
Feature: Order Flow Dashboard

  Scenario: Show that orders are flowing
    Given orders arrive through the B2B API and the Kafka topic order_b2b
    When an operator opens the Admin App home page
    Then maintain daily totals of orders (count and total amount), and of order_b2b messages and B2B requests
         (received, processed, rejected, and not yet done)
    And chart the daily totals for the last 30 days, showing a day with no activity as zero
    And date each Order, message and request when it arrives
    And show current data each time the page is opened
```

| Rule / item | Type | Logic | Description | Where |
|---|---|---|---|---|
| `DailyFlow.order_count = count(Order)` | count | declarative |  | [order_flow_totals.py](../../logic/logic_discovery/order_flow_totals.py) |
| `DailyFlow.order_amount = sum(Order.amount_total)` | sum | declarative |  | [order_flow_totals.py](../../logic/logic_discovery/order_flow_totals.py) |
| `DailyFlow.message_received = count(OrderB2bMessage)` | count | declarative |  | [order_flow_totals.py](../../logic/logic_discovery/order_flow_totals.py) |
| `DailyFlow.message_processed = count(OrderB2bMessage) where is_processed == True` | count | declarative |  | [order_flow_totals.py](../../logic/logic_discovery/order_flow_totals.py) |
| `DailyFlow.message_failed = count(OrderB2bMessage) where error_text is not None` | count | declarative |  | [order_flow_totals.py](../../logic/logic_discovery/order_flow_totals.py) |
| `DailyFlow.message_stuck = (message_received or 0) - (message_processed or 0) - (message_failed or 0)` | formula | declarative |  | [order_flow_totals.py](../../logic/logic_discovery/order_flow_totals.py) |
| `DailyFlow.request_received = count(OrderB2bRequest)` | count | declarative |  | [order_flow_totals.py](../../logic/logic_discovery/order_flow_totals.py) |
| `DailyFlow.request_processed = count(OrderB2bRequest) where is_processed == True` | count | declarative |  | [order_flow_totals.py](../../logic/logic_discovery/order_flow_totals.py) |
| `DailyFlow.request_failed = count(OrderB2bRequest) where error_text is not None` | count | declarative |  | [order_flow_totals.py](../../logic/logic_discovery/order_flow_totals.py) |
| `DailyFlow.request_stuck = (request_received or 0) - (request_processed or 0) - (request_failed or 0)` | formula | declarative |  | [order_flow_totals.py](../../logic/logic_discovery/order_flow_totals.py) |
| `HTTP in: GET /order_flow/daily` | http | handler (Python) | API service order flow: the daily totals for the last 30 days, as JSON (dashboard, tests, custom UIs). | [dashboard_services.py](../../api/api_discovery/dashboard_services.py) |
| `HTTP in: GET /dashboard` | http | handler (Python) | API service order flow: the dashboard iframes, embedded at the top of ui/admin/home.js. | [dashboard_services.py](../../api/api_discovery/dashboard_services.py) |
| `HTTP in: GET /chart_graphics/<path:path>` | http | handler (Python) | API service order flow: one chart, rendered on every request (never cached) so it shows current data. | [dashboard_services.py](../../api/api_discovery/dashboard_services.py) |

<details markdown>
<summary>Logic diagram: order_flow_totals</summary>

<table><tr valign="top">
<td width="65%">

![logic diagram: order_flow_totals](order_flow_totals/logic_diagrams/logic_diagram_order_flow_totals.svg)

</td>
<td width="35%">

**Rules**

1. `message_stuck = (message_received or 0) - (message_processed or 0) - (message_failed or 0)`<br>
2. `request_stuck = (request_received or 0) - (request_processed or 0) - (request_failed or 0)`<br>
3. `order_amount = sum(amount_total)`<br>
4. `order_count = count(Order)`<br>
5. `message_received = count(OrderB2bMessage)`<br>
6. `message_processed = count(OrderB2bMessage where is_processed)`<br>
7. `message_failed = count(OrderB2bMessage where error_text)`<br>
8. `request_received = count(OrderB2bRequest)`<br>
9. `request_processed = count(OrderB2bRequest where is_processed)`<br>
10. `request_failed = count(OrderB2bRequest where error_text)`

</td>
</tr></table>

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
| Item | unit_price | copy | `Item.unit_price = copy of Product.unit_price` |
| DailyFlow | order_count | count | `DailyFlow.order_count = count(Order)` |
| DailyFlow | order_amount | sum | `DailyFlow.order_amount = sum(Order.amount_total)` |
| DailyFlow | message_received | count | `DailyFlow.message_received = count(OrderB2bMessage)` |
| DailyFlow | message_processed | count | `DailyFlow.message_processed = count(OrderB2bMessage) where is_processed == True` |
| DailyFlow | message_failed | count | `DailyFlow.message_failed = count(OrderB2bMessage) where error_text is not None` |
| DailyFlow | message_stuck | formula | `DailyFlow.message_stuck = (message_received or 0) - (message_processed or 0) - (message_failed or 0)` |
| DailyFlow | request_received | count | `DailyFlow.request_received = count(OrderB2bRequest)` |
| DailyFlow | request_processed | count | `DailyFlow.request_processed = count(OrderB2bRequest) where is_processed == True` |
| DailyFlow | request_failed | count | `DailyFlow.request_failed = count(OrderB2bRequest) where error_text is not None` |
| DailyFlow | request_stuck | formula | `DailyFlow.request_stuck = (request_received or 0) - (request_processed or 0) - (request_failed or 0)` |


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

**Kafka mode: live (localhost:9092).** The tests sent inbound messages through a real broker: `/consume_debug` published them to topic `order_b2b`, the server's consumers processed them, and the tests then checked the results. Outbound `order_shipping` messages are checked in the server log, not read back from the topic.

| Direction | Channel | Name | Tests mention it | Handler | Tables created | Message shape | Requirement |
|---|---|---|---|---|---|---|---|
| ➡ in | Kafka | `order_b2b` | ✅ live | `order_b2b()` - Kafka subscribe order_b2b: Consumer 1 - save the raw blob and commit (Tx 1); the row event publishes it on. | OrderB2bMessage | [order_b2b.json](../../integration/kafka/message_formats/order_b2b.json) | §3 Kafka Subscribe — Inbound orders from sales channel |
| ➡ in | Kafka | `order_b2b_processed` | ✅ live | `order_b2b_processed()` - Kafka subscribe order_b2b_processed: Consumer 2 - parse + persist the Order (Tx 2); a failure is recorded on the blob. | Item, Order, OrderB2bMessage |  | §3 Kafka Subscribe — Inbound orders from sales channel |
| ⬅ out | Kafka | `order_b2b_processed` | ✅ live | OrderB2bMessage.after_flush_row_event → _publish_order_b2b() - OrderB2bMessage event: publishes the raw blob to order_b2b_processed after Tx 1 commits, so Consumer 2 parses it in a clean Tx 2 (2-message pattern). |  |  | §3 Kafka Subscribe — Inbound orders from sales channel |
| ⬅ out | Kafka | `order_shipping` | ⚠ message checked in the log, not on the topic | Order.after_flush_row_event → _send_order_to_shipping() - Order publish: sends the Order to Kafka topic order_shipping when date_shipped is set and differs from its prior value (old_row is None on insert), shaped by example as message_formats/order_shipping.json. |  | [order_shipping.json](../../integration/kafka/message_formats/order_shipping.json) | §4 Kafka Publish — Notify shipping on dispatch |
| ➡ in | HTTP | `GET /order_flow/daily` | ✅ | `order_flow_daily()` - API service order flow: the daily totals for the last 30 days, as JSON (dashboard, tests, custom UIs). |  |  | §6 Operations Dashboard — Order flow |
| ➡ in | HTTP | `GET /dashboard` | ✅ | `dashboard()` - API service order flow: the dashboard iframes, embedded at the top of ui/admin/home.js. |  |  | §6 Operations Dashboard — Order flow |
| ➡ in | HTTP | `GET /chart_graphics/<path:path>` | ⚠ no test mentions it | `chart_graphics()` - API service order flow: one chart, rendered on every request (never cached) so it shows current data. |  |  | §6 Operations Dashboard — Order flow |
| ➡ in | HTTP | `GET /consume_debug/order_b2b` | ✅ | `register_consume_debug()` - EAI debug (development only, no authentication): sends the message in ?file= to the topic, live through Kafka or simulated |  |  | §3 Kafka Subscribe — Inbound orders from sales channel |
| ➡ in | HTTP | `POST /consume_debug/order_b2b/reset` | ⚠ no test mentions it | `register_queue_reset()` - EAI debug (development only, destructive): purges the messages in the pipeline's topics |  |  | §3 Kafka Subscribe — Inbound orders from sales channel |
| ➡ in | HTTP | `POST /api/OrderB2B/OrderB2B` | ✅ | `OrderB2B()` - API service OrderB2B: records the request, creates the Order and its Items (the rules derive the rest), and records the outcome on the request row. |  |  | §2 B2B API — Accept orders from external partners |

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

**✅ 30 scenario(s): 30 passed, 0 failed; took 3.4 s** (from the last run, `logs/behave.log`).

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
- Order Flow Dashboard

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

#### Scenario: Partner Order Accepted ✅ (0.06 s)
&emsp;  Scenario: Partner Order Accepted  
&emsp;&emsp;    Given Customer "Pat" with credit limit 5000  
&emsp;&emsp;    When B2B order placed for "Pat" with 1 Widget and 2 Gadget  
&emsp;&emsp;    Then the partner order is accepted with 2 items  
&emsp;&emsp;    And Order amount_total should be 390  
&emsp;&emsp;    And Customer balance should be 390  

<details markdown>
<summary>Rules exercised and logic log (2 transactions)</summary>


&nbsp;
&nbsp;


**Rules Used** in Scenario: Partner Order Accepted
```
  DailyFlow  
    1. Derive DailyFlow.request_processed as Count(OrderB2bRequest Where Rule.count(derive=models.DailyFlow.request_processed, as_count_of=models.OrderB2bRequest, where=lambda row: row.is_processed == True, insert_parent=True), insert_parent)  
    2. Derive DailyFlow.request_failed as Count(OrderB2bRequest Where Rule.count(derive=models.DailyFlow.request_failed, as_count_of=models.OrderB2bRequest, where=lambda row: row.error_text is not None, insert_parent=True), insert_parent)  
    3. Derive DailyFlow.request_stuck as Formula (2): Rule.formula(derive=models.DailyFlow.request_stuc [...]  
    4. Derive DailyFlow.request_received as Count(OrderB2bRequest Where  - None, insert_parent)  
    5. Derive DailyFlow.order_amount as Sum(Order.amount_total Where  - None, insert_parent)  
    6. Derive DailyFlow.order_count as Count(Order Where  - None, insert_parent)  
  Customer  
    7. Derive Customer.balance as Sum(Order.amount_total Where Rule.sum(derive=models.Customer.balance, as_sum_of=models.Order.amount_total, where=lambda row: row.date_shipped is None))  
  Item  
    8. Derive Item.amount as Formula (1): Rule.formula(derive=models.Item.amount, as_expres [...]  
    9. Derive Item.unit_price as Copy(product.unit_price)  
  Order  
    10. RowEvent Order._send_order_to_shipping()  
    11. Derive Order.amount_total as Sum(Item.amount Where  - None)  
```
**Logic Log** in Scenario: Partner Order Accepted (2 transactions)
```
Logic Phase:		ROW LOGIC		(session=0x109ebe710) (sqlalchemy before_flush)			 - 2026-11-19 17:41:41,989 - logic_logger - INFO
..OrderB2bRequest[None] {Insert - client} id: None, CreatedOn: None, CreatedOnDay: None, payload: {"Account": "Pat 1795138901951", "Notes": "behave test", "Items": [{"Name": "Widget", "QuantityOrdered": 1}, {"Name": "Gadget", "QuantityOrdered": 2}]}, is_processed: False, error_text: None  row: 0x10c3f3050  session: 0x109ebe710  ins_upd_dlt: ins, initial: ins - 2026-11-19 17:41:41,989 - logic_logger - INFO
..OrderB2bRequest[None] {early_row_event_all_classes - handle_all did stamping} id: None, CreatedOn: 2026-11-19 17:41:41.989590, CreatedOnDay: 2026-11-19, payload: {"Account": "Pat 1795138901951", "Notes": "behave test", "Items": [{"Name": "Widget", "QuantityOrdered": 1}, {"Name": "Gadget", "QuantityOrdered": 2}]}, is_processed: False, error_text: None  row: 0x10c3f3050  session: 0x109ebe710  ins_upd_dlt: ins, initial: ins - 2026-11-19 17:41:41,989 - logic_logger - INFO
....DailyFlow[2026-11-19] {Update - Adjusting daily_flow: request_received} day: 2026-11-19, order_count: 1, order_amount: 390.00, message_received: 1, message_processed: 1, message_failed: 0, message_stuck: 0, request_received:  [0-->] 1, request_processed: 0, request_failed: 0, request_stuck: 0  row: 0x10c28e4c0  session: 0x109ebe710  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:41,990 - logic_logger - INFO
....DailyFlow[2026-11-19] {Prune Formula: message_stuck [['message_received', 'message_processed', 'message_failed']]} day: 2026-11-19, order_count: 1, order_amount: 390.00, message_received: 1, message_processed: 1, message_failed: 0, message_stuck: 0, request_received:  [0-->] 1, request_processed: 0, request_failed: 0, request_stuck: 0  row: 0x10c28e4c0  session: 0x109ebe710  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:41,990 - logic_logger - INFO
....DailyFlow[2026-11-19] {Formula request_stuck} day: 2026-11-19, order_count: 1, order_amount: 390.00, message_received: 1, message_processed: 1, message_failed: 0, message_stuck: 0, request_received:  [0-->] 1, request_processed: 0, request_failed: 0, request_stuck:  [0-->] 1  row: 0x10c28e4c0  session: 0x109ebe710  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:41,990 - logic_logger - INFO
Logic Phase:		COMMIT LOGIC		(session=0x109ebe710)   										 - 2026-11-19 17:41:41,990 - logic_logger - INFO
Logic Phase:		AFTER_FLUSH LOGIC	(session=0x109ebe710)   										 - 2026-11-19 17:41:41,991 - logic_logger - INFO


Logic Phase:		ROW LOGIC		(session=0x109ebe710) (sqlalchemy before_flush)			 - 2026-11-19 17:41:41,996 - logic_logger - INFO
..Product[1] {Update - client} id: 1, name: Gadget, count_suppliers: 0, unit_price: 150.0000000000  row: 0x10c5888a0  session: 0x109ebe710  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:41,996 - logic_logger - INFO
..OrderB2bRequest[61] {Update - client} id: 61, CreatedOn: 2026-11-19 17:41:41.989590, CreatedOnDay: 2026-11-19, payload: {"Account": "Pat 1795138901951", "Notes": "behave test", "Items": [{"Name": "Widget", "QuantityOrdered": 1}, {"Name": "Gadget", "QuantityOrdered": 2}]}, is_processed:  [False-->] True, error_text: None  row: 0x10c3f3050  session: 0x109ebe710  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:41,996 - logic_logger - INFO
....DailyFlow[2026-11-19] {Update - Adjusting daily_flow: request_processed} day: 2026-11-19, order_count: 1, order_amount: 390.00, message_received: 1, message_processed: 1, message_failed: 0, message_stuck: 0, request_received: 1, request_processed:  [0-->] 1, request_failed: 0, request_stuck: 1  row: 0x10c28e4c0  session: 0x109ebe710  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:41,996 - logic_logger - INFO
....DailyFlow[2026-11-19] {Prune Formula: message_stuck [['message_received', 'message_processed', 'message_failed']]} day: 2026-11-19, order_count: 1, order_amount: 390.00, message_received: 1, message_processed: 1, message_failed: 0, message_stuck: 0, request_received: 1, request_processed:  [0-->] 1, request_failed: 0, request_stuck: 1  row: 0x10c28e4c0  session: 0x109ebe710  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:41,996 - logic_logger - INFO
....DailyFlow[2026-11-19] {Formula request_stuck} day: 2026-11-19, order_count: 1, order_amount: 390.00, message_received: 1, message_processed: 1, message_failed: 0, message_stuck: 0, request_received: 1, request_processed:  [0-->] 1, request_failed: 0, request_stuck:  [1-->] 0  row: 0x10c28e4c0  session: 0x109ebe710  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:41,996 - logic_logger - INFO
..Order[None] {Insert - client} id: None, notes: behave test, customer_id: 10, CreatedOn: None, date_shipped: None, amount_total: None, CreatedOnDay: None  row: 0x10c4cdbe0  session: 0x109ebe710  ins_upd_dlt: ins, initial: ins - 2026-11-19 17:41:41,996 - logic_logger - INFO
..Order[None] {early_row_event_all_classes - handle_all did stamping} id: None, notes: behave test, customer_id: 10, CreatedOn: 2026-11-19, date_shipped: None, amount_total: None, CreatedOnDay: 2026-11-19  row: 0x10c4cdbe0  session: 0x109ebe710  ins_upd_dlt: ins, initial: ins - 2026-11-19 17:41:41,996 - logic_logger - INFO
..Order[None] {server aggregate_defaults: amount_total } id: None, notes: behave test, customer_id: 10, CreatedOn: 2026-11-19, date_shipped: None, amount_total: 0, CreatedOnDay: 2026-11-19  row: 0x10c4cdbe0  session: 0x109ebe710  ins_upd_dlt: ins, initial: ins - 2026-11-19 17:41:41,996 - logic_logger - INFO
....DailyFlow[2026-11-19] {Update - Adjusting daily_flow: order_count} day: 2026-11-19, order_count:  [1-->] 2, order_amount: 390.00, message_received: 1, message_processed: 1, message_failed: 0, message_stuck: 0, request_received: 1, request_processed: 1, request_failed: 0, request_stuck: 0  row: 0x10c28e4c0  session: 0x109ebe710  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:41,997 - logic_logger - INFO
....DailyFlow[2026-11-19] {Prune Formula: message_stuck [['message_received', 'message_processed', 'message_failed']]} day: 2026-11-19, order_count:  [1-->] 2, order_amount: 390.00, message_received: 1, message_processed: 1, message_failed: 0, message_stuck: 0, request_received: 1, request_processed: 1, request_failed: 0, request_stuck: 0  row: 0x10c28e4c0  session: 0x109ebe710  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:41,997 - logic_logger - INFO
....DailyFlow[2026-11-19] {Prune Formula: request_stuck [['request_received', 'request_processed', 'request_failed']]} day: 2026-11-19, order_count:  [1-->] 2, order_amount: 390.00, message_received: 1, message_processed: 1, message_failed: 0, message_stuck: 0, request_received: 1, request_processed: 1, request_failed: 0, request_stuck: 0  row: 0x10c28e4c0  session: 0x109ebe710  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:41,997 - logic_logger - INFO
..Item[None] {Insert - client} id: None, order_id: None, product_id: 2, quantity: 1, amount: None, unit_price: None  row: 0x10c48b8d0  session: 0x109ebe710  ins_upd_dlt: ins, initial: ins - 2026-11-19 17:41:41,997 - logic_logger - INFO
..Item[None] {copy_rules for role: product - unit_price} id: None, order_id: None, product_id: 2, quantity: 1, amount: None, unit_price: 90.0000000000  row: 0x10c48b8d0  session: 0x109ebe710  ins_upd_dlt: ins, initial: ins - 2026-11-19 17:41:41,997 - logic_logger - INFO
..Item[None] {Formula amount} id: None, order_id: None, product_id: 2, quantity: 1, amount: 90.0000000000, unit_price: 90.0000000000  row: 0x10c48b8d0  session: 0x109ebe710  ins_upd_dlt: ins, initial: ins - 2026-11-19 17:41:41,997 - logic_logger - INFO
....Order[None] {Update - Adjusting order: amount_total} id: None, notes: behave test, customer_id: 10, CreatedOn: 2026-11-19, date_shipped: None, amount_total:  [0-->] 90.0000000000, CreatedOnDay: 2026-11-19  row: 0x10c4cdbe0  session: 0x109ebe710  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:41,997 - logic_logger - INFO
......DailyFlow[2026-11-19] {Update - Adjusting daily_flow: order_amount} day: 2026-11-19, order_count: 2, order_amount:  [390.00-->] 480.0000000000, message_received: 1, message_processed: 1, message_failed: 0, message_stuck: 0, request_received: 1, request_processed: 1, request_failed: 0, request_stuck: 0  row: 0x10c28e4c0  session: 0x109ebe710  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:41,997 - logic_logger - INFO
......DailyFlow[2026-11-19] {Prune Formula: message_stuck [['message_received', 'message_processed', 'message_failed']]} day: 2026-11-19, order_count: 2, order_amount:  [390.00-->] 480.0000000000, message_received: 1, message_processed: 1, message_failed: 0, message_stuck: 0, request_received: 1, request_processed: 1, request_failed: 0, request_stuck: 0  row: 0x10c28e4c0  session: 0x109ebe710  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:41,997 - logic_logger - INFO
......DailyFlow[2026-11-19] {Prune Formula: request_stuck [['request_received', 'request_processed', 'request_failed']]} day: 2026-11-19, order_count: 2, order_amount:  [390.00-->] 480.0000000000, message_received: 1, message_processed: 1, message_failed: 0, message_stuck: 0, request_received: 1, request_processed: 1, request_failed: 0, request_stuck: 0  row: 0x10c28e4c0  session: 0x109ebe710  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:41,997 - logic_logger - INFO
......Customer[10] {Update - Adjusting customer: balance} id: 10, name: Pat 1795138901951, balance:  [0E-10-->] 90.0000000000, credit_limit: 5000.0000000000, email: None, email_opt_out: None  row: 0x10c4c76d0  session: 0x109ebe710  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:41,997 - logic_logger - INFO
..Item[None] {Insert - client} id: None, order_id: None, product_id: None, quantity: 2, amount: None, unit_price: None  row: 0x10c45b550  session: 0x109ebe710  ins_upd_dlt: ins, initial: ins - 2026-11-19 17:41:41,997 - logic_logger - INFO
..Item[None] {copy_rules for role: product - unit_price} id: None, order_id: None, product_id: None, quantity: 2, amount: None, unit_price: 150.0000000000  row: 0x10c45b550  session: 0x109ebe710  ins_upd_dlt: ins, initial: ins - 2026-11-19 17:41:41,997 - logic_logger - INFO
..Item[None] {Formula amount} id: None, order_id: None, product_id: None, quantity: 2, amount: 300.0000000000, unit_price: 150.0000000000  row: 0x10c45b550  session: 0x109ebe710  ins_upd_dlt: ins, initial: ins - 2026-11-19 17:41:41,997 - logic_logger - INFO
....Order[None] {Update - Adjusting order: amount_total} id: None, notes: behave test, customer_id: 10, CreatedOn: 2026-11-19, date_shipped: None, amount_total:  [90.0000000000-->] 390.0000000000, CreatedOnDay: 2026-11-19  row: 0x10c4cdbe0  session: 0x109ebe710  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:41,997 - logic_logger - INFO
......DailyFlow[2026-11-19] {Update - Adjusting daily_flow: order_amount} day: 2026-11-19, order_count: 2, order_amount:  [480.0000000000-->] 780.0000000000, message_received: 1, message_processed: 1, message_failed: 0, message_stuck: 0, request_received: 1, request_processed: 1, request_failed: 0, request_stuck: 0  row: 0x10c28e4c0  session: 0x109ebe710  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:41,998 - logic_logger - INFO
......DailyFlow[2026-11-19] {Prune Formula: message_stuck [['message_received', 'message_processed', 'message_failed']]} day: 2026-11-19, order_count: 2, order_amount:  [480.0000000000-->] 780.0000000000, message_received: 1, message_processed: 1, message_failed: 0, message_stuck: 0, request_received: 1, request_processed: 1, request_failed: 0, request_stuck: 0  row: 0x10c28e4c0  session: 0x109ebe710  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:41,998 - logic_logger - INFO
......DailyFlow[2026-11-19] {Prune Formula: request_stuck [['request_received', 'request_processed', 'request_failed']]} day: 2026-11-19, order_count: 2, order_amount:  [480.0000000000-->] 780.0000000000, message_received: 1, message_processed: 1, message_failed: 0, message_stuck: 0, request_received: 1, request_processed: 1, request_failed: 0, request_stuck: 0  row: 0x10c28e4c0  session: 0x109ebe710  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:41,998 - logic_logger - INFO
......Customer[10] {Update - Adjusting customer: balance} id: 10, name: Pat 1795138901951, balance:  [90.0000000000-->] 390.0000000000, credit_limit: 5000.0000000000, email: None, email_opt_out: None  row: 0x10c4c76d0  session: 0x109ebe710  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:41,998 - logic_logger - INFO
Logic Phase:		COMMIT LOGIC		(session=0x109ebe710)   										 - 2026-11-19 17:41:41,998 - logic_logger - INFO
Logic Phase:		AFTER_FLUSH LOGIC	(session=0x109ebe710)   										 - 2026-11-19 17:41:41,999 - logic_logger - INFO
..Order[159] {AfterFlush Event} id: 159, notes: behave test, customer_id: 10, CreatedOn: 2026-11-19, date_shipped: None, amount_total: 390.0000000000, CreatedOnDay: 2026-11-19  row: 0x10c4cdbe0  session: 0x109ebe710  ins_upd_dlt: ins, initial: ins - 2026-11-19 17:41:41,999 - logic_logger - INFO

```
</details>

&nbsp;
&nbsp;

#### Scenario: Unknown Account Rejected ✅ (0.01 s)
&emsp;  Scenario: Unknown Account Rejected  
&emsp;&emsp;    When B2B order placed for unknown account "Nobody"  
&emsp;&emsp;    Then the order is rejected for an unknown customer  

<details markdown>
<summary>Rules exercised and logic log (2 transactions)</summary>


&nbsp;
&nbsp;


**Rules Used** in Scenario: Unknown Account Rejected
```
  DailyFlow  
    1. Derive DailyFlow.request_processed as Count(OrderB2bRequest Where Rule.count(derive=models.DailyFlow.request_processed, as_count_of=models.OrderB2bRequest, where=lambda row: row.is_processed == True, insert_parent=True), insert_parent)  
    2. Derive DailyFlow.request_failed as Count(OrderB2bRequest Where Rule.count(derive=models.DailyFlow.request_failed, as_count_of=models.OrderB2bRequest, where=lambda row: row.error_text is not None, insert_parent=True), insert_parent)  
    3. Derive DailyFlow.request_stuck as Formula (2): Rule.formula(derive=models.DailyFlow.request_stuc [...]  
    4. Derive DailyFlow.request_received as Count(OrderB2bRequest Where  - None, insert_parent)  
```
**Logic Log** in Scenario: Unknown Account Rejected (2 transactions)
```
Logic Phase:		ROW LOGIC		(session=0x10c0fe570) (sqlalchemy before_flush)			 - 2026-11-19 17:41:42,008 - logic_logger - INFO
..OrderB2bRequest[None] {Insert - client} id: None, CreatedOn: None, CreatedOnDay: None, payload: {"Account": "Nobody 1795138902007", "Notes": "behave test", "Items": [{"Name": "Widget", "QuantityOrdered": 1}]}, is_processed: False, error_text: None  row: 0x10c4c6f50  session: 0x10c0fe570  ins_upd_dlt: ins, initial: ins - 2026-11-19 17:41:42,008 - logic_logger - INFO
..OrderB2bRequest[None] {early_row_event_all_classes - handle_all did stamping} id: None, CreatedOn: 2026-11-19 17:41:42.008253, CreatedOnDay: 2026-11-19, payload: {"Account": "Nobody 1795138902007", "Notes": "behave test", "Items": [{"Name": "Widget", "QuantityOrdered": 1}]}, is_processed: False, error_text: None  row: 0x10c4c6f50  session: 0x10c0fe570  ins_upd_dlt: ins, initial: ins - 2026-11-19 17:41:42,008 - logic_logger - INFO
....DailyFlow[2026-11-19] {Update - Adjusting daily_flow: request_received} day: 2026-11-19, order_count: 2, order_amount: 780.00, message_received: 1, message_processed: 1, message_failed: 0, message_stuck: 0, request_received:  [1-->] 2, request_processed: 1, request_failed: 0, request_stuck: 0  row: 0x10c28c100  session: 0x10c0fe570  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:42,008 - logic_logger - INFO
....DailyFlow[2026-11-19] {Prune Formula: message_stuck [['message_received', 'message_processed', 'message_failed']]} day: 2026-11-19, order_count: 2, order_amount: 780.00, message_received: 1, message_processed: 1, message_failed: 0, message_stuck: 0, request_received:  [1-->] 2, request_processed: 1, request_failed: 0, request_stuck: 0  row: 0x10c28c100  session: 0x10c0fe570  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:42,008 - logic_logger - INFO
....DailyFlow[2026-11-19] {Formula request_stuck} day: 2026-11-19, order_count: 2, order_amount: 780.00, message_received: 1, message_processed: 1, message_failed: 0, message_stuck: 0, request_received:  [1-->] 2, request_processed: 1, request_failed: 0, request_stuck:  [0-->] 1  row: 0x10c28c100  session: 0x10c0fe570  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:42,008 - logic_logger - INFO
Logic Phase:		COMMIT LOGIC		(session=0x10c0fe570)   										 - 2026-11-19 17:41:42,008 - logic_logger - INFO
Logic Phase:		AFTER_FLUSH LOGIC	(session=0x10c0fe570)   										 - 2026-11-19 17:41:42,009 - logic_logger - INFO


Logic Phase:		ROW LOGIC		(session=0x10c0fe570) (sqlalchemy before_flush)			 - 2026-11-19 17:41:42,010 - logic_logger - INFO
..OrderB2bRequest[62] {Update - client} id: 62, CreatedOn: 2026-11-19 17:41:42.008253, CreatedOnDay: 2026-11-19, payload: {"Account": "Nobody 1795138902007", "Notes": "behave test", "Items": [{"Name": "Widget", "QuantityOrdered": 1}]}, is_processed: False, error_text:  [None-->] ('Lookup failed: missing parent', <Order (transient 4501336528)>, 'Customer', "{'Account': 'Nobody 1795138902007', 'Notes': 'behave test', 'Items': [{'Name': 'Widget', 'QuantityOrdered': 1}]}")  row: 0x10c4c6f50  session: 0x10c0fe570  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:42,010 - logic_logger - INFO
....DailyFlow[2026-11-19] {Update - Adjusting daily_flow: request_failed} day: 2026-11-19, order_count: 2, order_amount: 780.00, message_received: 1, message_processed: 1, message_failed: 0, message_stuck: 0, request_received: 2, request_processed: 1, request_failed:  [0-->] 1, request_stuck: 1  row: 0x10c28c100  session: 0x10c0fe570  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:42,010 - logic_logger - INFO
....DailyFlow[2026-11-19] {Prune Formula: message_stuck [['message_received', 'message_processed', 'message_failed']]} day: 2026-11-19, order_count: 2, order_amount: 780.00, message_received: 1, message_processed: 1, message_failed: 0, message_stuck: 0, request_received: 2, request_processed: 1, request_failed:  [0-->] 1, request_stuck: 1  row: 0x10c28c100  session: 0x10c0fe570  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:42,010 - logic_logger - INFO
....DailyFlow[2026-11-19] {Formula request_stuck} day: 2026-11-19, order_count: 2, order_amount: 780.00, message_received: 1, message_processed: 1, message_failed: 0, message_stuck: 0, request_received: 2, request_processed: 1, request_failed:  [0-->] 1, request_stuck:  [1-->] 0  row: 0x10c28c100  session: 0x10c0fe570  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:42,011 - logic_logger - INFO
Logic Phase:		COMMIT LOGIC		(session=0x10c0fe570)   										 - 2026-11-19 17:41:42,011 - logic_logger - INFO
Logic Phase:		AFTER_FLUSH LOGIC	(session=0x10c0fe570)   										 - 2026-11-19 17:41:42,011 - logic_logger - INFO

```
</details>

&nbsp;
&nbsp;

#### Scenario: Accepted Request Is Recorded ✅ (0.02 s)
&emsp;  Scenario: Accepted Request Is Recorded  
&emsp;&emsp;    Given Customer "Pia" with credit limit 5000  
&emsp;&emsp;    And the daily totals are read  
&emsp;&emsp;    When B2B order placed for "Pia" with 1 Widget  
&emsp;&emsp;    Then the B2B request is recorded as processed  
&emsp;&emsp;    And today's request_received and request_processed rise by 1  

<details markdown>
<summary>Rules exercised and logic log (2 transactions)</summary>


&nbsp;
&nbsp;


**Rules Used** in Scenario: Accepted Request Is Recorded
```
  DailyFlow  
    1. Derive DailyFlow.request_processed as Count(OrderB2bRequest Where Rule.count(derive=models.DailyFlow.request_processed, as_count_of=models.OrderB2bRequest, where=lambda row: row.is_processed == True, insert_parent=True), insert_parent)  
    2. Derive DailyFlow.request_failed as Count(OrderB2bRequest Where Rule.count(derive=models.DailyFlow.request_failed, as_count_of=models.OrderB2bRequest, where=lambda row: row.error_text is not None, insert_parent=True), insert_parent)  
    3. Derive DailyFlow.request_stuck as Formula (2): Rule.formula(derive=models.DailyFlow.request_stuc [...]  
    4. Derive DailyFlow.request_received as Count(OrderB2bRequest Where  - None, insert_parent)  
    5. Derive DailyFlow.order_amount as Sum(Order.amount_total Where  - None, insert_parent)  
    6. Derive DailyFlow.order_count as Count(Order Where  - None, insert_parent)  
  Customer  
    7. Derive Customer.balance as Sum(Order.amount_total Where Rule.sum(derive=models.Customer.balance, as_sum_of=models.Order.amount_total, where=lambda row: row.date_shipped is None))  
  Item  
    8. Derive Item.amount as Formula (1): Rule.formula(derive=models.Item.amount, as_expres [...]  
    9. Derive Item.unit_price as Copy(product.unit_price)  
  Order  
    10. RowEvent Order._send_order_to_shipping()  
    11. Derive Order.amount_total as Sum(Item.amount Where  - None)  
```
**Logic Log** in Scenario: Accepted Request Is Recorded (2 transactions)
```
Logic Phase:		ROW LOGIC		(session=0x10c51dae0) (sqlalchemy before_flush)			 - 2026-11-19 17:41:42,021 - logic_logger - INFO
..OrderB2bRequest[None] {Insert - client} id: None, CreatedOn: None, CreatedOnDay: None, payload: {"Account": "Pia 1795138902015", "Notes": "behave test", "Items": [{"Name": "Widget", "QuantityOrdered": 1}]}, is_processed: False, error_text: None  row: 0x10c5d3e50  session: 0x10c51dae0  ins_upd_dlt: ins, initial: ins - 2026-11-19 17:41:42,021 - logic_logger - INFO
..OrderB2bRequest[None] {early_row_event_all_classes - handle_all did stamping} id: None, CreatedOn: 2026-11-19 17:41:42.021810, CreatedOnDay: 2026-11-19, payload: {"Account": "Pia 1795138902015", "Notes": "behave test", "Items": [{"Name": "Widget", "QuantityOrdered": 1}]}, is_processed: False, error_text: None  row: 0x10c5d3e50  session: 0x10c51dae0  ins_upd_dlt: ins, initial: ins - 2026-11-19 17:41:42,021 - logic_logger - INFO
....DailyFlow[2026-11-19] {Update - Adjusting daily_flow: request_received} day: 2026-11-19, order_count: 2, order_amount: 780.00, message_received: 1, message_processed: 1, message_failed: 0, message_stuck: 0, request_received:  [2-->] 3, request_processed: 1, request_failed: 1, request_stuck: 0  row: 0x10c5f4100  session: 0x10c51dae0  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:42,022 - logic_logger - INFO
....DailyFlow[2026-11-19] {Prune Formula: message_stuck [['message_received', 'message_processed', 'message_failed']]} day: 2026-11-19, order_count: 2, order_amount: 780.00, message_received: 1, message_processed: 1, message_failed: 0, message_stuck: 0, request_received:  [2-->] 3, request_processed: 1, request_failed: 1, request_stuck: 0  row: 0x10c5f4100  session: 0x10c51dae0  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:42,022 - logic_logger - INFO
....DailyFlow[2026-11-19] {Formula request_stuck} day: 2026-11-19, order_count: 2, order_amount: 780.00, message_received: 1, message_processed: 1, message_failed: 0, message_stuck: 0, request_received:  [2-->] 3, request_processed: 1, request_failed: 1, request_stuck:  [0-->] 1  row: 0x10c5f4100  session: 0x10c51dae0  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:42,022 - logic_logger - INFO
Logic Phase:		COMMIT LOGIC		(session=0x10c51dae0)   										 - 2026-11-19 17:41:42,022 - logic_logger - INFO
Logic Phase:		AFTER_FLUSH LOGIC	(session=0x10c51dae0)   										 - 2026-11-19 17:41:42,022 - logic_logger - INFO


Logic Phase:		ROW LOGIC		(session=0x10c51dae0) (sqlalchemy before_flush)			 - 2026-11-19 17:41:42,024 - logic_logger - INFO
..Product[2] {Update - client} id: 2, name: Widget, count_suppliers: 0, unit_price: 90.0000000000  row: 0x10c5dde80  session: 0x10c51dae0  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:42,024 - logic_logger - INFO
..OrderB2bRequest[63] {Update - client} id: 63, CreatedOn: 2026-11-19 17:41:42.021810, CreatedOnDay: 2026-11-19, payload: {"Account": "Pia 1795138902015", "Notes": "behave test", "Items": [{"Name": "Widget", "QuantityOrdered": 1}]}, is_processed:  [False-->] True, error_text: None  row: 0x10c5d3e50  session: 0x10c51dae0  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:42,024 - logic_logger - INFO
....DailyFlow[2026-11-19] {Update - Adjusting daily_flow: request_processed} day: 2026-11-19, order_count: 2, order_amount: 780.00, message_received: 1, message_processed: 1, message_failed: 0, message_stuck: 0, request_received: 3, request_processed:  [1-->] 2, request_failed: 1, request_stuck: 1  row: 0x10c5f4100  session: 0x10c51dae0  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:42,024 - logic_logger - INFO
....DailyFlow[2026-11-19] {Prune Formula: message_stuck [['message_received', 'message_processed', 'message_failed']]} day: 2026-11-19, order_count: 2, order_amount: 780.00, message_received: 1, message_processed: 1, message_failed: 0, message_stuck: 0, request_received: 3, request_processed:  [1-->] 2, request_failed: 1, request_stuck: 1  row: 0x10c5f4100  session: 0x10c51dae0  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:42,024 - logic_logger - INFO
....DailyFlow[2026-11-19] {Formula request_stuck} day: 2026-11-19, order_count: 2, order_amount: 780.00, message_received: 1, message_processed: 1, message_failed: 0, message_stuck: 0, request_received: 3, request_processed:  [1-->] 2, request_failed: 1, request_stuck:  [1-->] 0  row: 0x10c5f4100  session: 0x10c51dae0  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:42,024 - logic_logger - INFO
..Order[None] {Insert - client} id: None, notes: behave test, customer_id: 11, CreatedOn: None, date_shipped: None, amount_total: None, CreatedOnDay: None  row: 0x10c5c1910  session: 0x10c51dae0  ins_upd_dlt: ins, initial: ins - 2026-11-19 17:41:42,024 - logic_logger - INFO
..Order[None] {early_row_event_all_classes - handle_all did stamping} id: None, notes: behave test, customer_id: 11, CreatedOn: 2026-11-19, date_shipped: None, amount_total: None, CreatedOnDay: 2026-11-19  row: 0x10c5c1910  session: 0x10c51dae0  ins_upd_dlt: ins, initial: ins - 2026-11-19 17:41:42,025 - logic_logger - INFO
..Order[None] {server aggregate_defaults: amount_total } id: None, notes: behave test, customer_id: 11, CreatedOn: 2026-11-19, date_shipped: None, amount_total: 0, CreatedOnDay: 2026-11-19  row: 0x10c5c1910  session: 0x10c51dae0  ins_upd_dlt: ins, initial: ins - 2026-11-19 17:41:42,025 - logic_logger - INFO
....DailyFlow[2026-11-19] {Update - Adjusting daily_flow: order_count} day: 2026-11-19, order_count:  [2-->] 3, order_amount: 780.00, message_received: 1, message_processed: 1, message_failed: 0, message_stuck: 0, request_received: 3, request_processed: 2, request_failed: 1, request_stuck: 0  row: 0x10c5f4100  session: 0x10c51dae0  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:42,025 - logic_logger - INFO
....DailyFlow[2026-11-19] {Prune Formula: message_stuck [['message_received', 'message_processed', 'message_failed']]} day: 2026-11-19, order_count:  [2-->] 3, order_amount: 780.00, message_received: 1, message_processed: 1, message_failed: 0, message_stuck: 0, request_received: 3, request_processed: 2, request_failed: 1, request_stuck: 0  row: 0x10c5f4100  session: 0x10c51dae0  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:42,025 - logic_logger - INFO
....DailyFlow[2026-11-19] {Prune Formula: request_stuck [['request_received', 'request_processed', 'request_failed']]} day: 2026-11-19, order_count:  [2-->] 3, order_amount: 780.00, message_received: 1, message_processed: 1, message_failed: 0, message_stuck: 0, request_received: 3, request_processed: 2, request_failed: 1, request_stuck: 0  row: 0x10c5f4100  session: 0x10c51dae0  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:42,025 - logic_logger - INFO
..Item[None] {Insert - client} id: None, order_id: None, product_id: None, quantity: 1, amount: None, unit_price: None  row: 0x10c558750  session: 0x10c51dae0  ins_upd_dlt: ins, initial: ins - 2026-11-19 17:41:42,025 - logic_logger - INFO
..Item[None] {copy_rules for role: product - unit_price} id: None, order_id: None, product_id: None, quantity: 1, amount: None, unit_price: 90.0000000000  row: 0x10c558750  session: 0x10c51dae0  ins_upd_dlt: ins, initial: ins - 2026-11-19 17:41:42,025 - logic_logger - INFO
..Item[None] {Formula amount} id: None, order_id: None, product_id: None, quantity: 1, amount: 90.0000000000, unit_price: 90.0000000000  row: 0x10c558750  session: 0x10c51dae0  ins_upd_dlt: ins, initial: ins - 2026-11-19 17:41:42,025 - logic_logger - INFO
....Order[None] {Update - Adjusting order: amount_total} id: None, notes: behave test, customer_id: 11, CreatedOn: 2026-11-19, date_shipped: None, amount_total:  [0-->] 90.0000000000, CreatedOnDay: 2026-11-19  row: 0x10c5c1910  session: 0x10c51dae0  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:42,025 - logic_logger - INFO
......DailyFlow[2026-11-19] {Update - Adjusting daily_flow: order_amount} day: 2026-11-19, order_count: 3, order_amount:  [780.00-->] 870.0000000000, message_received: 1, message_processed: 1, message_failed: 0, message_stuck: 0, request_received: 3, request_processed: 2, request_failed: 1, request_stuck: 0  row: 0x10c5f4100  session: 0x10c51dae0  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:42,025 - logic_logger - INFO
......DailyFlow[2026-11-19] {Prune Formula: message_stuck [['message_received', 'message_processed', 'message_failed']]} day: 2026-11-19, order_count: 3, order_amount:  [780.00-->] 870.0000000000, message_received: 1, message_processed: 1, message_failed: 0, message_stuck: 0, request_received: 3, request_processed: 2, request_failed: 1, request_stuck: 0  row: 0x10c5f4100  session: 0x10c51dae0  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:42,025 - logic_logger - INFO
......DailyFlow[2026-11-19] {Prune Formula: request_stuck [['request_received', 'request_processed', 'request_failed']]} day: 2026-11-19, order_count: 3, order_amount:  [780.00-->] 870.0000000000, message_received: 1, message_processed: 1, message_failed: 0, message_stuck: 0, request_received: 3, request_processed: 2, request_failed: 1, request_stuck: 0  row: 0x10c5f4100  session: 0x10c51dae0  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:42,025 - logic_logger - INFO
......Customer[11] {Update - Adjusting customer: balance} id: 11, name: Pia 1795138902015, balance:  [0E-10-->] 90.0000000000, credit_limit: 5000.0000000000, email: None, email_opt_out: None  row: 0x10c5d3a50  session: 0x10c51dae0  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:42,025 - logic_logger - INFO
Logic Phase:		COMMIT LOGIC		(session=0x10c51dae0)   										 - 2026-11-19 17:41:42,025 - logic_logger - INFO
Logic Phase:		AFTER_FLUSH LOGIC	(session=0x10c51dae0)   										 - 2026-11-19 17:41:42,026 - logic_logger - INFO
..Order[160] {AfterFlush Event} id: 160, notes: behave test, customer_id: 11, CreatedOn: 2026-11-19, date_shipped: None, amount_total: 90.0000000000, CreatedOnDay: 2026-11-19  row: 0x10c5c1910  session: 0x10c51dae0  ins_upd_dlt: ins, initial: ins - 2026-11-19 17:41:42,026 - logic_logger - INFO

```
</details>

&nbsp;
&nbsp;

#### Scenario: Rejected Request Is Recorded ✅ (0.02 s)
&emsp;  Scenario: Rejected Request Is Recorded  
&emsp;&emsp;    Given Customer "Rex" with credit limit 100  
&emsp;&emsp;    And the daily totals are read  
&emsp;&emsp;    When B2B order placed for "Rex" with 2 Widget  
&emsp;&emsp;    Then the B2B request is recorded with the error "exceeds credit limit"  
&emsp;&emsp;    And today's request_received and request_failed rise by 1  

<details markdown>
<summary>Rules exercised and logic log (2 transactions)</summary>


&nbsp;
&nbsp;


**Rules Used** in Scenario: Rejected Request Is Recorded
```
  DailyFlow  
    1. Derive DailyFlow.request_processed as Count(OrderB2bRequest Where Rule.count(derive=models.DailyFlow.request_processed, as_count_of=models.OrderB2bRequest, where=lambda row: row.is_processed == True, insert_parent=True), insert_parent)  
    2. Derive DailyFlow.request_failed as Count(OrderB2bRequest Where Rule.count(derive=models.DailyFlow.request_failed, as_count_of=models.OrderB2bRequest, where=lambda row: row.error_text is not None, insert_parent=True), insert_parent)  
    3. Derive DailyFlow.request_stuck as Formula (2): Rule.formula(derive=models.DailyFlow.request_stuc [...]  
    4. Derive DailyFlow.request_received as Count(OrderB2bRequest Where  - None, insert_parent)  
    5. Derive DailyFlow.order_amount as Sum(Order.amount_total Where  - None, insert_parent)  
    6. Derive DailyFlow.order_count as Count(Order Where  - None, insert_parent)  
  Customer  
    7. Constraint Function: None  
    8. Derive Customer.balance as Sum(Order.amount_total Where Rule.sum(derive=models.Customer.balance, as_sum_of=models.Order.amount_total, where=lambda row: row.date_shipped is None))  
  Item  
    9. Derive Item.amount as Formula (1): Rule.formula(derive=models.Item.amount, as_expres [...]  
    10. Derive Item.unit_price as Copy(product.unit_price)  
  Order  
    11. Derive Order.amount_total as Sum(Item.amount Where  - None)  
```
**Logic Log** in Scenario: Rejected Request Is Recorded (2 transactions)
```
Logic Phase:		ROW LOGIC		(session=0x10c51e360) (sqlalchemy before_flush)			 - 2026-11-19 17:41:42,041 - logic_logger - INFO
..OrderB2bRequest[None] {Insert - client} id: None, CreatedOn: None, CreatedOnDay: None, payload: {"Account": "Rex 1795138902035", "Notes": "behave test", "Items": [{"Name": "Widget", "QuantityOrdered": 2}]}, is_processed: False, error_text: None  row: 0x10c45bcd0  session: 0x10c51e360  ins_upd_dlt: ins, initial: ins - 2026-11-19 17:41:42,041 - logic_logger - INFO
..OrderB2bRequest[None] {early_row_event_all_classes - handle_all did stamping} id: None, CreatedOn: 2026-11-19 17:41:42.041613, CreatedOnDay: 2026-11-19, payload: {"Account": "Rex 1795138902035", "Notes": "behave test", "Items": [{"Name": "Widget", "QuantityOrdered": 2}]}, is_processed: False, error_text: None  row: 0x10c45bcd0  session: 0x10c51e360  ins_upd_dlt: ins, initial: ins - 2026-11-19 17:41:42,041 - logic_logger - INFO
....DailyFlow[2026-11-19] {Update - Adjusting daily_flow: request_received} day: 2026-11-19, order_count: 3, order_amount: 870.00, message_received: 1, message_processed: 1, message_failed: 0, message_stuck: 0, request_received:  [3-->] 4, request_processed: 2, request_failed: 1, request_stuck: 0  row: 0x10c615440  session: 0x10c51e360  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:42,041 - logic_logger - INFO
....DailyFlow[2026-11-19] {Prune Formula: message_stuck [['message_received', 'message_processed', 'message_failed']]} day: 2026-11-19, order_count: 3, order_amount: 870.00, message_received: 1, message_processed: 1, message_failed: 0, message_stuck: 0, request_received:  [3-->] 4, request_processed: 2, request_failed: 1, request_stuck: 0  row: 0x10c615440  session: 0x10c51e360  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:42,042 - logic_logger - INFO
....DailyFlow[2026-11-19] {Formula request_stuck} day: 2026-11-19, order_count: 3, order_amount: 870.00, message_received: 1, message_processed: 1, message_failed: 0, message_stuck: 0, request_received:  [3-->] 4, request_processed: 2, request_failed: 1, request_stuck:  [0-->] 1  row: 0x10c615440  session: 0x10c51e360  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:42,042 - logic_logger - INFO
Logic Phase:		COMMIT LOGIC		(session=0x10c51e360)   										 - 2026-11-19 17:41:42,042 - logic_logger - INFO
Logic Phase:		AFTER_FLUSH LOGIC	(session=0x10c51e360)   										 - 2026-11-19 17:41:42,042 - logic_logger - INFO


Logic Phase:		ROW LOGIC		(session=0x10c51e360) (sqlalchemy before_flush)			 - 2026-11-19 17:41:42,044 - logic_logger - INFO
..OrderB2bRequest[64] {Update - client} id: 64, CreatedOn: 2026-11-19 17:41:42.041613, CreatedOnDay: 2026-11-19, payload: {"Account": "Rex 1795138902035", "Notes": "behave test", "Items": [{"Name": "Widget", "QuantityOrdered": 2}]}, is_processed:  [False-->] True, error_text: None  row: 0x10c45bcd0  session: 0x10c51e360  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:42,044 - logic_logger - INFO
....DailyFlow[2026-11-19] {Update - Adjusting daily_flow: request_processed} day: 2026-11-19, order_count: 3, order_amount: 870.00, message_received: 1, message_processed: 1, message_failed: 0, message_stuck: 0, request_received: 4, request_processed:  [2-->] 3, request_failed: 1, request_stuck: 1  row: 0x10c615440  session: 0x10c51e360  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:42,044 - logic_logger - INFO
....DailyFlow[2026-11-19] {Prune Formula: message_stuck [['message_received', 'message_processed', 'message_failed']]} day: 2026-11-19, order_count: 3, order_amount: 870.00, message_received: 1, message_processed: 1, message_failed: 0, message_stuck: 0, request_received: 4, request_processed:  [2-->] 3, request_failed: 1, request_stuck: 1  row: 0x10c615440  session: 0x10c51e360  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:42,044 - logic_logger - INFO
....DailyFlow[2026-11-19] {Formula request_stuck} day: 2026-11-19, order_count: 3, order_amount: 870.00, message_received: 1, message_processed: 1, message_failed: 0, message_stuck: 0, request_received: 4, request_processed:  [2-->] 3, request_failed: 1, request_stuck:  [1-->] 0  row: 0x10c615440  session: 0x10c51e360  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:42,044 - logic_logger - INFO
..Product[2] {Update - client} id: 2, name: Widget, count_suppliers: 0, unit_price: 90.0000000000  row: 0x10c5de6d0  session: 0x10c51e360  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:42,044 - logic_logger - INFO
..Order[None] {Insert - client} id: None, notes: behave test, customer_id: 12, CreatedOn: None, date_shipped: None, amount_total: None, CreatedOnDay: None  row: 0x10c5c1880  session: 0x10c51e360  ins_upd_dlt: ins, initial: ins - 2026-11-19 17:41:42,044 - logic_logger - INFO
..Order[None] {early_row_event_all_classes - handle_all did stamping} id: None, notes: behave test, customer_id: 12, CreatedOn: 2026-11-19, date_shipped: None, amount_total: None, CreatedOnDay: 2026-11-19  row: 0x10c5c1880  session: 0x10c51e360  ins_upd_dlt: ins, initial: ins - 2026-11-19 17:41:42,044 - logic_logger - INFO
..Order[None] {server aggregate_defaults: amount_total } id: None, notes: behave test, customer_id: 12, CreatedOn: 2026-11-19, date_shipped: None, amount_total: 0, CreatedOnDay: 2026-11-19  row: 0x10c5c1880  session: 0x10c51e360  ins_upd_dlt: ins, initial: ins - 2026-11-19 17:41:42,044 - logic_logger - INFO
....DailyFlow[2026-11-19] {Update - Adjusting daily_flow: order_count} day: 2026-11-19, order_count:  [3-->] 4, order_amount: 870.00, message_received: 1, message_processed: 1, message_failed: 0, message_stuck: 0, request_received: 4, request_processed: 3, request_failed: 1, request_stuck: 0  row: 0x10c615440  session: 0x10c51e360  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:42,045 - logic_logger - INFO
....DailyFlow[2026-11-19] {Prune Formula: message_stuck [['message_received', 'message_processed', 'message_failed']]} day: 2026-11-19, order_count:  [3-->] 4, order_amount: 870.00, message_received: 1, message_processed: 1, message_failed: 0, message_stuck: 0, request_received: 4, request_processed: 3, request_failed: 1, request_stuck: 0  row: 0x10c615440  session: 0x10c51e360  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:42,045 - logic_logger - INFO
....DailyFlow[2026-11-19] {Prune Formula: request_stuck [['request_received', 'request_processed', 'request_failed']]} day: 2026-11-19, order_count:  [3-->] 4, order_amount: 870.00, message_received: 1, message_processed: 1, message_failed: 0, message_stuck: 0, request_received: 4, request_processed: 3, request_failed: 1, request_stuck: 0  row: 0x10c615440  session: 0x10c51e360  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:42,045 - logic_logger - INFO
..Item[None] {Insert - client} id: None, order_id: None, product_id: None, quantity: 2, amount: None, unit_price: None  row: 0x10c4887d0  session: 0x10c51e360  ins_upd_dlt: ins, initial: ins - 2026-11-19 17:41:42,045 - logic_logger - INFO
..Item[None] {copy_rules for role: product - unit_price} id: None, order_id: None, product_id: None, quantity: 2, amount: None, unit_price: 90.0000000000  row: 0x10c4887d0  session: 0x10c51e360  ins_upd_dlt: ins, initial: ins - 2026-11-19 17:41:42,045 - logic_logger - INFO
..Item[None] {Formula amount} id: None, order_id: None, product_id: None, quantity: 2, amount: 180.0000000000, unit_price: 90.0000000000  row: 0x10c4887d0  session: 0x10c51e360  ins_upd_dlt: ins, initial: ins - 2026-11-19 17:41:42,045 - logic_logger - INFO
....Order[None] {Update - Adjusting order: amount_total} id: None, notes: behave test, customer_id: 12, CreatedOn: 2026-11-19, date_shipped: None, amount_total:  [0-->] 180.0000000000, CreatedOnDay: 2026-11-19  row: 0x10c5c1880  session: 0x10c51e360  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:42,045 - logic_logger - INFO
......DailyFlow[2026-11-19] {Update - Adjusting daily_flow: order_amount} day: 2026-11-19, order_count: 4, order_amount:  [870.00-->] 1050.0000000000, message_received: 1, message_processed: 1, message_failed: 0, message_stuck: 0, request_received: 4, request_processed: 3, request_failed: 1, request_stuck: 0  row: 0x10c615440  session: 0x10c51e360  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:42,045 - logic_logger - INFO
......DailyFlow[2026-11-19] {Prune Formula: message_stuck [['message_received', 'message_processed', 'message_failed']]} day: 2026-11-19, order_count: 4, order_amount:  [870.00-->] 1050.0000000000, message_received: 1, message_processed: 1, message_failed: 0, message_stuck: 0, request_received: 4, request_processed: 3, request_failed: 1, request_stuck: 0  row: 0x10c615440  session: 0x10c51e360  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:42,045 - logic_logger - INFO
......DailyFlow[2026-11-19] {Prune Formula: request_stuck [['request_received', 'request_processed', 'request_failed']]} day: 2026-11-19, order_count: 4, order_amount:  [870.00-->] 1050.0000000000, message_received: 1, message_processed: 1, message_failed: 0, message_stuck: 0, request_received: 4, request_processed: 3, request_failed: 1, request_stuck: 0  row: 0x10c615440  session: 0x10c51e360  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:42,045 - logic_logger - INFO
......Customer[12] {Update - Adjusting customer: balance} id: 12, name: Rex 1795138902035, balance:  [0E-10-->] 180.0000000000, credit_limit: 100.0000000000, email: None, email_opt_out: None  row: 0x10c55a8d0  session: 0x10c51e360  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:42,045 - logic_logger - INFO
......Customer[12] {Constraint Failure: Customer balance (180.0000000000) exceeds credit limit (100.0000000000)} id: 12, name: Rex 1795138902035, balance:  [0E-10-->] 180.0000000000, credit_limit: 100.0000000000, email: None, email_opt_out: None  row: 0x10c55a8d0  session: 0x10c51e360  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:42,045 - logic_logger - INFO

```
</details>

&nbsp;
&nbsp;

### Feature: Check Credit  

&nbsp;
&nbsp;

#### Scenario: Good Order Placed ✅ (0.01 s)
&emsp;  Scenario: Good Order Placed  
&emsp;&emsp;    Given Customer "Alice" with credit limit 5000  
&emsp;&emsp;    When B2B order placed for "Alice" with 2 Widget  
&emsp;&emsp;    Then Customer balance should be 180  
&emsp;&emsp;    And Order amount_total should be 180  

<details markdown>
<summary>Rules exercised and logic log (2 transactions)</summary>


&nbsp;
&nbsp;


**Rules Used** in Scenario: Good Order Placed
```
  DailyFlow  
    1. Derive DailyFlow.request_processed as Count(OrderB2bRequest Where Rule.count(derive=models.DailyFlow.request_processed, as_count_of=models.OrderB2bRequest, where=lambda row: row.is_processed == True, insert_parent=True), insert_parent)  
    2. Derive DailyFlow.request_failed as Count(OrderB2bRequest Where Rule.count(derive=models.DailyFlow.request_failed, as_count_of=models.OrderB2bRequest, where=lambda row: row.error_text is not None, insert_parent=True), insert_parent)  
    3. Derive DailyFlow.request_stuck as Formula (2): Rule.formula(derive=models.DailyFlow.request_stuc [...]  
    4. Derive DailyFlow.request_received as Count(OrderB2bRequest Where  - None, insert_parent)  
    5. Derive DailyFlow.order_amount as Sum(Order.amount_total Where  - None, insert_parent)  
    6. Derive DailyFlow.order_count as Count(Order Where  - None, insert_parent)  
  Customer  
    7. Derive Customer.balance as Sum(Order.amount_total Where Rule.sum(derive=models.Customer.balance, as_sum_of=models.Order.amount_total, where=lambda row: row.date_shipped is None))  
  Item  
    8. Derive Item.amount as Formula (1): Rule.formula(derive=models.Item.amount, as_expres [...]  
    9. Derive Item.unit_price as Copy(product.unit_price)  
  Order  
    10. RowEvent Order._send_order_to_shipping()  
    11. Derive Order.amount_total as Sum(Item.amount Where  - None)  
```
**Logic Log** in Scenario: Good Order Placed (2 transactions)
```
Logic Phase:		ROW LOGIC		(session=0x10c51e580) (sqlalchemy before_flush)			 - 2026-11-19 17:41:42,062 - logic_logger - INFO
..OrderB2bRequest[None] {Insert - client} id: None, CreatedOn: None, CreatedOnDay: None, payload: {"Account": "Alice 1795138902058", "Notes": "behave test", "Items": [{"Name": "Widget", "QuantityOrdered": 2}]}, is_processed: False, error_text: None  row: 0x10c5e8550  session: 0x10c51e580  ins_upd_dlt: ins, initial: ins - 2026-11-19 17:41:42,062 - logic_logger - INFO
..OrderB2bRequest[None] {early_row_event_all_classes - handle_all did stamping} id: None, CreatedOn: 2026-11-19 17:41:42.062219, CreatedOnDay: 2026-11-19, payload: {"Account": "Alice 1795138902058", "Notes": "behave test", "Items": [{"Name": "Widget", "QuantityOrdered": 2}]}, is_processed: False, error_text: None  row: 0x10c5e8550  session: 0x10c51e580  ins_upd_dlt: ins, initial: ins - 2026-11-19 17:41:42,062 - logic_logger - INFO
....DailyFlow[2026-11-19] {Update - Adjusting daily_flow: request_received} day: 2026-11-19, order_count: 3, order_amount: 870.00, message_received: 1, message_processed: 1, message_failed: 0, message_stuck: 0, request_received:  [4-->] 5, request_processed: 2, request_failed: 2, request_stuck: 0  row: 0x10c616620  session: 0x10c51e580  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:42,062 - logic_logger - INFO
....DailyFlow[2026-11-19] {Prune Formula: message_stuck [['message_received', 'message_processed', 'message_failed']]} day: 2026-11-19, order_count: 3, order_amount: 870.00, message_received: 1, message_processed: 1, message_failed: 0, message_stuck: 0, request_received:  [4-->] 5, request_processed: 2, request_failed: 2, request_stuck: 0  row: 0x10c616620  session: 0x10c51e580  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:42,062 - logic_logger - INFO
....DailyFlow[2026-11-19] {Formula request_stuck} day: 2026-11-19, order_count: 3, order_amount: 870.00, message_received: 1, message_processed: 1, message_failed: 0, message_stuck: 0, request_received:  [4-->] 5, request_processed: 2, request_failed: 2, request_stuck:  [0-->] 1  row: 0x10c616620  session: 0x10c51e580  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:42,062 - logic_logger - INFO
Logic Phase:		COMMIT LOGIC		(session=0x10c51e580)   										 - 2026-11-19 17:41:42,062 - logic_logger - INFO
Logic Phase:		AFTER_FLUSH LOGIC	(session=0x10c51e580)   										 - 2026-11-19 17:41:42,063 - logic_logger - INFO


Logic Phase:		ROW LOGIC		(session=0x10c51e580) (sqlalchemy before_flush)			 - 2026-11-19 17:41:42,064 - logic_logger - INFO
..Product[2] {Update - client} id: 2, name: Widget, count_suppliers: 0, unit_price: 90.0000000000  row: 0x10c6cb8c0  session: 0x10c51e580  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:42,064 - logic_logger - INFO
..OrderB2bRequest[65] {Update - client} id: 65, CreatedOn: 2026-11-19 17:41:42.062219, CreatedOnDay: 2026-11-19, payload: {"Account": "Alice 1795138902058", "Notes": "behave test", "Items": [{"Name": "Widget", "QuantityOrdered": 2}]}, is_processed:  [False-->] True, error_text: None  row: 0x10c5e8550  session: 0x10c51e580  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:42,064 - logic_logger - INFO
....DailyFlow[2026-11-19] {Update - Adjusting daily_flow: request_processed} day: 2026-11-19, order_count: 3, order_amount: 870.00, message_received: 1, message_processed: 1, message_failed: 0, message_stuck: 0, request_received: 5, request_processed:  [2-->] 3, request_failed: 2, request_stuck: 1  row: 0x10c616620  session: 0x10c51e580  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:42,065 - logic_logger - INFO
....DailyFlow[2026-11-19] {Prune Formula: message_stuck [['message_received', 'message_processed', 'message_failed']]} day: 2026-11-19, order_count: 3, order_amount: 870.00, message_received: 1, message_processed: 1, message_failed: 0, message_stuck: 0, request_received: 5, request_processed:  [2-->] 3, request_failed: 2, request_stuck: 1  row: 0x10c616620  session: 0x10c51e580  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:42,065 - logic_logger - INFO
....DailyFlow[2026-11-19] {Formula request_stuck} day: 2026-11-19, order_count: 3, order_amount: 870.00, message_received: 1, message_processed: 1, message_failed: 0, message_stuck: 0, request_received: 5, request_processed:  [2-->] 3, request_failed: 2, request_stuck:  [1-->] 0  row: 0x10c616620  session: 0x10c51e580  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:42,065 - logic_logger - INFO
..Order[None] {Insert - client} id: None, notes: behave test, customer_id: 13, CreatedOn: None, date_shipped: None, amount_total: None, CreatedOnDay: None  row: 0x10c6d91c0  session: 0x10c51e580  ins_upd_dlt: ins, initial: ins - 2026-11-19 17:41:42,065 - logic_logger - INFO
..Order[None] {early_row_event_all_classes - handle_all did stamping} id: None, notes: behave test, customer_id: 13, CreatedOn: 2026-11-19, date_shipped: None, amount_total: None, CreatedOnDay: 2026-11-19  row: 0x10c6d91c0  session: 0x10c51e580  ins_upd_dlt: ins, initial: ins - 2026-11-19 17:41:42,065 - logic_logger - INFO
..Order[None] {server aggregate_defaults: amount_total } id: None, notes: behave test, customer_id: 13, CreatedOn: 2026-11-19, date_shipped: None, amount_total: 0, CreatedOnDay: 2026-11-19  row: 0x10c6d91c0  session: 0x10c51e580  ins_upd_dlt: ins, initial: ins - 2026-11-19 17:41:42,065 - logic_logger - INFO
....DailyFlow[2026-11-19] {Update - Adjusting daily_flow: order_count} day: 2026-11-19, order_count:  [3-->] 4, order_amount: 870.00, message_received: 1, message_processed: 1, message_failed: 0, message_stuck: 0, request_received: 5, request_processed: 3, request_failed: 2, request_stuck: 0  row: 0x10c616620  session: 0x10c51e580  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:42,065 - logic_logger - INFO
....DailyFlow[2026-11-19] {Prune Formula: message_stuck [['message_received', 'message_processed', 'message_failed']]} day: 2026-11-19, order_count:  [3-->] 4, order_amount: 870.00, message_received: 1, message_processed: 1, message_failed: 0, message_stuck: 0, request_received: 5, request_processed: 3, request_failed: 2, request_stuck: 0  row: 0x10c616620  session: 0x10c51e580  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:42,065 - logic_logger - INFO
....DailyFlow[2026-11-19] {Prune Formula: request_stuck [['request_received', 'request_processed', 'request_failed']]} day: 2026-11-19, order_count:  [3-->] 4, order_amount: 870.00, message_received: 1, message_processed: 1, message_failed: 0, message_stuck: 0, request_received: 5, request_processed: 3, request_failed: 2, request_stuck: 0  row: 0x10c616620  session: 0x10c51e580  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:42,065 - logic_logger - INFO
..Item[None] {Insert - client} id: None, order_id: None, product_id: None, quantity: 2, amount: None, unit_price: None  row: 0x10c5eb7d0  session: 0x10c51e580  ins_upd_dlt: ins, initial: ins - 2026-11-19 17:41:42,065 - logic_logger - INFO
..Item[None] {copy_rules for role: product - unit_price} id: None, order_id: None, product_id: None, quantity: 2, amount: None, unit_price: 90.0000000000  row: 0x10c5eb7d0  session: 0x10c51e580  ins_upd_dlt: ins, initial: ins - 2026-11-19 17:41:42,065 - logic_logger - INFO
..Item[None] {Formula amount} id: None, order_id: None, product_id: None, quantity: 2, amount: 180.0000000000, unit_price: 90.0000000000  row: 0x10c5eb7d0  session: 0x10c51e580  ins_upd_dlt: ins, initial: ins - 2026-11-19 17:41:42,065 - logic_logger - INFO
....Order[None] {Update - Adjusting order: amount_total} id: None, notes: behave test, customer_id: 13, CreatedOn: 2026-11-19, date_shipped: None, amount_total:  [0-->] 180.0000000000, CreatedOnDay: 2026-11-19  row: 0x10c6d91c0  session: 0x10c51e580  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:42,065 - logic_logger - INFO
......DailyFlow[2026-11-19] {Update - Adjusting daily_flow: order_amount} day: 2026-11-19, order_count: 4, order_amount:  [870.00-->] 1050.0000000000, message_received: 1, message_processed: 1, message_failed: 0, message_stuck: 0, request_received: 5, request_processed: 3, request_failed: 2, request_stuck: 0  row: 0x10c616620  session: 0x10c51e580  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:42,065 - logic_logger - INFO
......DailyFlow[2026-11-19] {Prune Formula: message_stuck [['message_received', 'message_processed', 'message_failed']]} day: 2026-11-19, order_count: 4, order_amount:  [870.00-->] 1050.0000000000, message_received: 1, message_processed: 1, message_failed: 0, message_stuck: 0, request_received: 5, request_processed: 3, request_failed: 2, request_stuck: 0  row: 0x10c616620  session: 0x10c51e580  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:42,066 - logic_logger - INFO
......DailyFlow[2026-11-19] {Prune Formula: request_stuck [['request_received', 'request_processed', 'request_failed']]} day: 2026-11-19, order_count: 4, order_amount:  [870.00-->] 1050.0000000000, message_received: 1, message_processed: 1, message_failed: 0, message_stuck: 0, request_received: 5, request_processed: 3, request_failed: 2, request_stuck: 0  row: 0x10c616620  session: 0x10c51e580  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:42,066 - logic_logger - INFO
......Customer[13] {Update - Adjusting customer: balance} id: 13, name: Alice 1795138902058, balance:  [0E-10-->] 180.0000000000, credit_limit: 5000.0000000000, email: None, email_opt_out: None  row: 0x10c5d2bd0  session: 0x10c51e580  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:42,066 - logic_logger - INFO
Logic Phase:		COMMIT LOGIC		(session=0x10c51e580)   										 - 2026-11-19 17:41:42,066 - logic_logger - INFO
Logic Phase:		AFTER_FLUSH LOGIC	(session=0x10c51e580)   										 - 2026-11-19 17:41:42,066 - logic_logger - INFO
..Order[161] {AfterFlush Event} id: 161, notes: behave test, customer_id: 13, CreatedOn: 2026-11-19, date_shipped: None, amount_total: 180.0000000000, CreatedOnDay: 2026-11-19  row: 0x10c6d91c0  session: 0x10c51e580  ins_upd_dlt: ins, initial: ins - 2026-11-19 17:41:42,066 - logic_logger - INFO

```
</details>

&nbsp;
&nbsp;

#### Scenario: Item Quantity Changed ✅ (0.02 s)
&emsp;  Scenario: Item Quantity Changed  
&emsp;&emsp;    Given Customer "Bob" with credit limit 5000  
&emsp;&emsp;    And Order is created for "Bob" with 2 Widget  
&emsp;&emsp;    When Item quantity changed to 3  
&emsp;&emsp;    Then Customer balance should be 270  

<details markdown>
<summary>Rules exercised and logic log (3 transactions)</summary>


&nbsp;
&nbsp;


**Rules Used** in Scenario: Item Quantity Changed
```
  DailyFlow  
    1. Derive DailyFlow.request_processed as Count(OrderB2bRequest Where Rule.count(derive=models.DailyFlow.request_processed, as_count_of=models.OrderB2bRequest, where=lambda row: row.is_processed == True, insert_parent=True), insert_parent)  
    2. Derive DailyFlow.request_failed as Count(OrderB2bRequest Where Rule.count(derive=models.DailyFlow.request_failed, as_count_of=models.OrderB2bRequest, where=lambda row: row.error_text is not None, insert_parent=True), insert_parent)  
    3. Derive DailyFlow.request_stuck as Formula (2): Rule.formula(derive=models.DailyFlow.request_stuc [...]  
    4. Derive DailyFlow.request_received as Count(OrderB2bRequest Where  - None, insert_parent)  
    5. Derive DailyFlow.order_amount as Sum(Order.amount_total Where  - None, insert_parent)  
    6. Derive DailyFlow.order_count as Count(Order Where  - None, insert_parent)  
  Customer  
    7. Derive Customer.balance as Sum(Order.amount_total Where Rule.sum(derive=models.Customer.balance, as_sum_of=models.Order.amount_total, where=lambda row: row.date_shipped is None))  
  Item  
    8. Derive Item.amount as Formula (1): Rule.formula(derive=models.Item.amount, as_expres [...]  
    9. Derive Item.unit_price as Copy(product.unit_price)  
  Order  
    10. RowEvent Order._send_order_to_shipping()  
    11. Derive Order.amount_total as Sum(Item.amount Where  - None)  
```
**Logic Log** in Scenario: Item Quantity Changed (3 transactions)
```
Logic Phase:		ROW LOGIC		(session=0x10c51ead0) (sqlalchemy before_flush)			 - 2026-11-19 17:41:42,076 - logic_logger - INFO
..OrderB2bRequest[None] {Insert - client} id: None, CreatedOn: None, CreatedOnDay: None, payload: {"Account": "Bob 1795138902073", "Notes": "behave test", "Items": [{"Name": "Widget", "QuantityOrdered": 2}]}, is_processed: False, error_text: None  row: 0x10c459dd0  session: 0x10c51ead0  ins_upd_dlt: ins, initial: ins - 2026-11-19 17:41:42,076 - logic_logger - INFO
..OrderB2bRequest[None] {early_row_event_all_classes - handle_all did stamping} id: None, CreatedOn: 2026-11-19 17:41:42.076999, CreatedOnDay: 2026-11-19, payload: {"Account": "Bob 1795138902073", "Notes": "behave test", "Items": [{"Name": "Widget", "QuantityOrdered": 2}]}, is_processed: False, error_text: None  row: 0x10c459dd0  session: 0x10c51ead0  ins_upd_dlt: ins, initial: ins - 2026-11-19 17:41:42,077 - logic_logger - INFO
....DailyFlow[2026-11-19] {Update - Adjusting daily_flow: request_received} day: 2026-11-19, order_count: 4, order_amount: 1050.00, message_received: 1, message_processed: 1, message_failed: 0, message_stuck: 0, request_received:  [5-->] 6, request_processed: 3, request_failed: 2, request_stuck: 0  row: 0x10c616410  session: 0x10c51ead0  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:42,077 - logic_logger - INFO
....DailyFlow[2026-11-19] {Prune Formula: message_stuck [['message_received', 'message_processed', 'message_failed']]} day: 2026-11-19, order_count: 4, order_amount: 1050.00, message_received: 1, message_processed: 1, message_failed: 0, message_stuck: 0, request_received:  [5-->] 6, request_processed: 3, request_failed: 2, request_stuck: 0  row: 0x10c616410  session: 0x10c51ead0  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:42,077 - logic_logger - INFO
....DailyFlow[2026-11-19] {Formula request_stuck} day: 2026-11-19, order_count: 4, order_amount: 1050.00, message_received: 1, message_processed: 1, message_failed: 0, message_stuck: 0, request_received:  [5-->] 6, request_processed: 3, request_failed: 2, request_stuck:  [0-->] 1  row: 0x10c616410  session: 0x10c51ead0  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:42,077 - logic_logger - INFO
Logic Phase:		COMMIT LOGIC		(session=0x10c51ead0)   										 - 2026-11-19 17:41:42,077 - logic_logger - INFO
Logic Phase:		AFTER_FLUSH LOGIC	(session=0x10c51ead0)   										 - 2026-11-19 17:41:42,077 - logic_logger - INFO


Logic Phase:		ROW LOGIC		(session=0x10c51ead0) (sqlalchemy before_flush)			 - 2026-11-19 17:41:42,079 - logic_logger - INFO
..OrderB2bRequest[66] {Update - client} id: 66, CreatedOn: 2026-11-19 17:41:42.076999, CreatedOnDay: 2026-11-19, payload: {"Account": "Bob 1795138902073", "Notes": "behave test", "Items": [{"Name": "Widget", "QuantityOrdered": 2}]}, is_processed:  [False-->] True, error_text: None  row: 0x10c459dd0  session: 0x10c51ead0  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:42,079 - logic_logger - INFO
....DailyFlow[2026-11-19] {Update - Adjusting daily_flow: request_processed} day: 2026-11-19, order_count: 4, order_amount: 1050.00, message_received: 1, message_processed: 1, message_failed: 0, message_stuck: 0, request_received: 6, request_processed:  [3-->] 4, request_failed: 2, request_stuck: 1  row: 0x10c616410  session: 0x10c51ead0  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:42,080 - logic_logger - INFO
....DailyFlow[2026-11-19] {Prune Formula: message_stuck [['message_received', 'message_processed', 'message_failed']]} day: 2026-11-19, order_count: 4, order_amount: 1050.00, message_received: 1, message_processed: 1, message_failed: 0, message_stuck: 0, request_received: 6, request_processed:  [3-->] 4, request_failed: 2, request_stuck: 1  row: 0x10c616410  session: 0x10c51ead0  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:42,080 - logic_logger - INFO
....DailyFlow[2026-11-19] {Formula request_stuck} day: 2026-11-19, order_count: 4, order_amount: 1050.00, message_received: 1, message_processed: 1, message_failed: 0, message_stuck: 0, request_received: 6, request_processed:  [3-->] 4, request_failed: 2, request_stuck:  [1-->] 0  row: 0x10c616410  session: 0x10c51ead0  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:42,080 - logic_logger - INFO
..Product[2] {Update - client} id: 2, name: Widget, count_suppliers: 0, unit_price: 90.0000000000  row: 0x10c5de580  session: 0x10c51ead0  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:42,080 - logic_logger - INFO
..Order[None] {Insert - client} id: None, notes: behave test, customer_id: 14, CreatedOn: None, date_shipped: None, amount_total: None, CreatedOnDay: None  row: 0x10c6d9370  session: 0x10c51ead0  ins_upd_dlt: ins, initial: ins - 2026-11-19 17:41:42,080 - logic_logger - INFO
..Order[None] {early_row_event_all_classes - handle_all did stamping} id: None, notes: behave test, customer_id: 14, CreatedOn: 2026-11-19, date_shipped: None, amount_total: None, CreatedOnDay: 2026-11-19  row: 0x10c6d9370  session: 0x10c51ead0  ins_upd_dlt: ins, initial: ins - 2026-11-19 17:41:42,080 - logic_logger - INFO
..Order[None] {server aggregate_defaults: amount_total } id: None, notes: behave test, customer_id: 14, CreatedOn: 2026-11-19, date_shipped: None, amount_total: 0, CreatedOnDay: 2026-11-19  row: 0x10c6d9370  session: 0x10c51ead0  ins_upd_dlt: ins, initial: ins - 2026-11-19 17:41:42,080 - logic_logger - INFO
....DailyFlow[2026-11-19] {Update - Adjusting daily_flow: order_count} day: 2026-11-19, order_count:  [4-->] 5, order_amount: 1050.00, message_received: 1, message_processed: 1, message_failed: 0, message_stuck: 0, request_received: 6, request_processed: 4, request_failed: 2, request_stuck: 0  row: 0x10c616410  session: 0x10c51ead0  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:42,080 - logic_logger - INFO
....DailyFlow[2026-11-19] {Prune Formula: message_stuck [['message_received', 'message_processed', 'message_failed']]} day: 2026-11-19, order_count:  [4-->] 5, order_amount: 1050.00, message_received: 1, message_processed: 1, message_failed: 0, message_stuck: 0, request_received: 6, request_processed: 4, request_failed: 2, request_stuck: 0  row: 0x10c616410  session: 0x10c51ead0  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:42,080 - logic_logger - INFO
....DailyFlow[2026-11-19] {Prune Formula: request_stuck [['request_received', 'request_processed', 'request_failed']]} day: 2026-11-19, order_count:  [4-->] 5, order_amount: 1050.00, message_received: 1, message_processed: 1, message_failed: 0, message_stuck: 0, request_received: 6, request_processed: 4, request_failed: 2, request_stuck: 0  row: 0x10c616410  session: 0x10c51ead0  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:42,080 - logic_logger - INFO
..Item[None] {Insert - client} id: None, order_id: None, product_id: None, quantity: 2, amount: None, unit_price: None  row: 0x10c60c450  session: 0x10c51ead0  ins_upd_dlt: ins, initial: ins - 2026-11-19 17:41:42,080 - logic_logger - INFO
..Item[None] {copy_rules for role: product - unit_price} id: None, order_id: None, product_id: None, quantity: 2, amount: None, unit_price: 90.0000000000  row: 0x10c60c450  session: 0x10c51ead0  ins_upd_dlt: ins, initial: ins - 2026-11-19 17:41:42,080 - logic_logger - INFO
..Item[None] {Formula amount} id: None, order_id: None, product_id: None, quantity: 2, amount: 180.0000000000, unit_price: 90.0000000000  row: 0x10c60c450  session: 0x10c51ead0  ins_upd_dlt: ins, initial: ins - 2026-11-19 17:41:42,080 - logic_logger - INFO
....Order[None] {Update - Adjusting order: amount_total} id: None, notes: behave test, customer_id: 14, CreatedOn: 2026-11-19, date_shipped: None, amount_total:  [0-->] 180.0000000000, CreatedOnDay: 2026-11-19  row: 0x10c6d9370  session: 0x10c51ead0  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:42,080 - logic_logger - INFO
......DailyFlow[2026-11-19] {Update - Adjusting daily_flow: order_amount} day: 2026-11-19, order_count: 5, order_amount:  [1050.00-->] 1230.0000000000, message_received: 1, message_processed: 1, message_failed: 0, message_stuck: 0, request_received: 6, request_processed: 4, request_failed: 2, request_stuck: 0  row: 0x10c616410  session: 0x10c51ead0  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:42,080 - logic_logger - INFO
......DailyFlow[2026-11-19] {Prune Formula: message_stuck [['message_received', 'message_processed', 'message_failed']]} day: 2026-11-19, order_count: 5, order_amount:  [1050.00-->] 1230.0000000000, message_received: 1, message_processed: 1, message_failed: 0, message_stuck: 0, request_received: 6, request_processed: 4, request_failed: 2, request_stuck: 0  row: 0x10c616410  session: 0x10c51ead0  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:42,081 - logic_logger - INFO
......DailyFlow[2026-11-19] {Prune Formula: request_stuck [['request_received', 'request_processed', 'request_failed']]} day: 2026-11-19, order_count: 5, order_amount:  [1050.00-->] 1230.0000000000, message_received: 1, message_processed: 1, message_failed: 0, message_stuck: 0, request_received: 6, request_processed: 4, request_failed: 2, request_stuck: 0  row: 0x10c616410  session: 0x10c51ead0  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:42,081 - logic_logger - INFO
......Customer[14] {Update - Adjusting customer: balance} id: 14, name: Bob 1795138902073, balance:  [0E-10-->] 180.0000000000, credit_limit: 5000.0000000000, email: None, email_opt_out: None  row: 0x10c6d4c50  session: 0x10c51ead0  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:42,081 - logic_logger - INFO
Logic Phase:		COMMIT LOGIC		(session=0x10c51ead0)   										 - 2026-11-19 17:41:42,081 - logic_logger - INFO
Logic Phase:		AFTER_FLUSH LOGIC	(session=0x10c51ead0)   										 - 2026-11-19 17:41:42,081 - logic_logger - INFO
..Order[162] {AfterFlush Event} id: 162, notes: behave test, customer_id: 14, CreatedOn: 2026-11-19, date_shipped: None, amount_total: 180.0000000000, CreatedOnDay: 2026-11-19  row: 0x10c6d9370  session: 0x10c51ead0  ins_upd_dlt: ins, initial: ins - 2026-11-19 17:41:42,081 - logic_logger - INFO


Logic Phase:		ROW LOGIC		(session=0x10c51e8b0) (sqlalchemy before_flush)			 - 2026-11-19 17:41:42,087 - logic_logger - INFO
..Item[309] {Update - client} id: 309, order_id: 162, product_id: 2, quantity:  [2-->] 3, amount: 180.0000000000, unit_price: 90.0000000000  row: 0x10c6d5e50  session: 0x10c51e8b0  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:42,087 - logic_logger - INFO
..Item[309] {Formula amount} id: 309, order_id: 162, product_id: 2, quantity:  [2-->] 3, amount:  [180.0000000000-->] 270.0000000000, unit_price: 90.0000000000  row: 0x10c6d5e50  session: 0x10c51e8b0  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:42,087 - logic_logger - INFO
....Order[162] {Update - Adjusting order: amount_total} id: 162, notes: behave test, customer_id: 14, CreatedOn: 2026-11-19, date_shipped: None, amount_total:  [180.0000000000-->] 270.0000000000, CreatedOnDay: 2026-11-19  row: 0x10c6d8d40  session: 0x10c51e8b0  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:42,088 - logic_logger - INFO
......DailyFlow[2026-11-19] {Update - Adjusting daily_flow: order_amount} day: 2026-11-19, order_count: 5, order_amount:  [1230.00-->] 1320.0000000000, message_received: 1, message_processed: 1, message_failed: 0, message_stuck: 0, request_received: 6, request_processed: 4, request_failed: 2, request_stuck: 0  row: 0x10c6147e0  session: 0x10c51e8b0  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:42,088 - logic_logger - INFO
......DailyFlow[2026-11-19] {Prune Formula: message_stuck [['message_received', 'message_processed', 'message_failed']]} day: 2026-11-19, order_count: 5, order_amount:  [1230.00-->] 1320.0000000000, message_received: 1, message_processed: 1, message_failed: 0, message_stuck: 0, request_received: 6, request_processed: 4, request_failed: 2, request_stuck: 0  row: 0x10c6147e0  session: 0x10c51e8b0  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:42,088 - logic_logger - INFO
......DailyFlow[2026-11-19] {Prune Formula: request_stuck [['request_received', 'request_processed', 'request_failed']]} day: 2026-11-19, order_count: 5, order_amount:  [1230.00-->] 1320.0000000000, message_received: 1, message_processed: 1, message_failed: 0, message_stuck: 0, request_received: 6, request_processed: 4, request_failed: 2, request_stuck: 0  row: 0x10c6147e0  session: 0x10c51e8b0  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:42,088 - logic_logger - INFO
......Customer[14] {Update - Adjusting customer: balance} id: 14, name: Bob 1795138902073, balance:  [180.0000000000-->] 270.0000000000, credit_limit: 5000.0000000000, email: None, email_opt_out: None  row: 0x10c5eb6d0  session: 0x10c51e8b0  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:42,088 - logic_logger - INFO
Logic Phase:		COMMIT LOGIC		(session=0x10c51e8b0)   										 - 2026-11-19 17:41:42,088 - logic_logger - INFO
Logic Phase:		AFTER_FLUSH LOGIC	(session=0x10c51e8b0)   										 - 2026-11-19 17:41:42,089 - logic_logger - INFO
....Order[162] {AfterFlush Event} id: 162, notes: behave test, customer_id: 14, CreatedOn: 2026-11-19, date_shipped: None, amount_total:  [180.0000000000-->] 270.0000000000, CreatedOnDay: 2026-11-19  row: 0x10c6d8d40  session: 0x10c51e8b0  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:42,089 - logic_logger - INFO

```
</details>

&nbsp;
&nbsp;

#### Scenario: Shipped Order Leaves Balance ✅ (0.03 s)
&emsp;  Scenario: Shipped Order Leaves Balance  
&emsp;&emsp;    Given Customer "Carol" with credit limit 5000  
&emsp;&emsp;    And Order is created for "Carol" with 2 Widget  
&emsp;&emsp;    When Order is shipped  
&emsp;&emsp;    Then Customer balance should be 0  

<details markdown>
<summary>Rules exercised and logic log (3 transactions)</summary>


&nbsp;
&nbsp;


**Rules Used** in Scenario: Shipped Order Leaves Balance
```
  DailyFlow  
    1. Derive DailyFlow.request_processed as Count(OrderB2bRequest Where Rule.count(derive=models.DailyFlow.request_processed, as_count_of=models.OrderB2bRequest, where=lambda row: row.is_processed == True, insert_parent=True), insert_parent)  
    2. Derive DailyFlow.request_failed as Count(OrderB2bRequest Where Rule.count(derive=models.DailyFlow.request_failed, as_count_of=models.OrderB2bRequest, where=lambda row: row.error_text is not None, insert_parent=True), insert_parent)  
    3. Derive DailyFlow.request_stuck as Formula (2): Rule.formula(derive=models.DailyFlow.request_stuc [...]  
    4. Derive DailyFlow.request_received as Count(OrderB2bRequest Where  - None, insert_parent)  
    5. Derive DailyFlow.order_amount as Sum(Order.amount_total Where  - None, insert_parent)  
    6. Derive DailyFlow.order_count as Count(Order Where  - None, insert_parent)  
  Customer  
    7. Derive Customer.balance as Sum(Order.amount_total Where Rule.sum(derive=models.Customer.balance, as_sum_of=models.Order.amount_total, where=lambda row: row.date_shipped is None))  
  Item  
    8. Derive Item.amount as Formula (1): Rule.formula(derive=models.Item.amount, as_expres [...]  
    9. Derive Item.unit_price as Copy(product.unit_price)  
  Order  
    10. RowEvent Order._send_order_to_shipping()  
    11. Derive Order.amount_total as Sum(Item.amount Where  - None)  
```
**Logic Log** in Scenario: Shipped Order Leaves Balance (3 transactions)
```
Logic Phase:		ROW LOGIC		(session=0x10c51df20) (sqlalchemy before_flush)			 - 2026-11-19 17:41:42,099 - logic_logger - INFO
..OrderB2bRequest[None] {Insert - client} id: None, CreatedOn: None, CreatedOnDay: None, payload: {"Account": "Carol 1795138902095", "Notes": "behave test", "Items": [{"Name": "Widget", "QuantityOrdered": 2}]}, is_processed: False, error_text: None  row: 0x10c55a8d0  session: 0x10c51df20  ins_upd_dlt: ins, initial: ins - 2026-11-19 17:41:42,099 - logic_logger - INFO
..OrderB2bRequest[None] {early_row_event_all_classes - handle_all did stamping} id: None, CreatedOn: 2026-11-19 17:41:42.099248, CreatedOnDay: 2026-11-19, payload: {"Account": "Carol 1795138902095", "Notes": "behave test", "Items": [{"Name": "Widget", "QuantityOrdered": 2}]}, is_processed: False, error_text: None  row: 0x10c55a8d0  session: 0x10c51df20  ins_upd_dlt: ins, initial: ins - 2026-11-19 17:41:42,099 - logic_logger - INFO
....DailyFlow[2026-11-19] {Update - Adjusting daily_flow: request_received} day: 2026-11-19, order_count: 5, order_amount: 1320.00, message_received: 1, message_processed: 1, message_failed: 0, message_stuck: 0, request_received:  [6-->] 7, request_processed: 4, request_failed: 2, request_stuck: 0  row: 0x10c6155a0  session: 0x10c51df20  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:42,099 - logic_logger - INFO
....DailyFlow[2026-11-19] {Prune Formula: message_stuck [['message_received', 'message_processed', 'message_failed']]} day: 2026-11-19, order_count: 5, order_amount: 1320.00, message_received: 1, message_processed: 1, message_failed: 0, message_stuck: 0, request_received:  [6-->] 7, request_processed: 4, request_failed: 2, request_stuck: 0  row: 0x10c6155a0  session: 0x10c51df20  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:42,099 - logic_logger - INFO
....DailyFlow[2026-11-19] {Formula request_stuck} day: 2026-11-19, order_count: 5, order_amount: 1320.00, message_received: 1, message_processed: 1, message_failed: 0, message_stuck: 0, request_received:  [6-->] 7, request_processed: 4, request_failed: 2, request_stuck:  [0-->] 1  row: 0x10c6155a0  session: 0x10c51df20  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:42,099 - logic_logger - INFO
Logic Phase:		COMMIT LOGIC		(session=0x10c51df20)   										 - 2026-11-19 17:41:42,099 - logic_logger - INFO
Logic Phase:		AFTER_FLUSH LOGIC	(session=0x10c51df20)   										 - 2026-11-19 17:41:42,100 - logic_logger - INFO


Logic Phase:		ROW LOGIC		(session=0x10c51df20) (sqlalchemy before_flush)			 - 2026-11-19 17:41:42,101 - logic_logger - INFO
..Product[2] {Update - client} id: 2, name: Widget, count_suppliers: 0, unit_price: 90.0000000000  row: 0x10c6cb690  session: 0x10c51df20  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:42,101 - logic_logger - INFO
..OrderB2bRequest[67] {Update - client} id: 67, CreatedOn: 2026-11-19 17:41:42.099248, CreatedOnDay: 2026-11-19, payload: {"Account": "Carol 1795138902095", "Notes": "behave test", "Items": [{"Name": "Widget", "QuantityOrdered": 2}]}, is_processed:  [False-->] True, error_text: None  row: 0x10c55a8d0  session: 0x10c51df20  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:42,102 - logic_logger - INFO
....DailyFlow[2026-11-19] {Update - Adjusting daily_flow: request_processed} day: 2026-11-19, order_count: 5, order_amount: 1320.00, message_received: 1, message_processed: 1, message_failed: 0, message_stuck: 0, request_received: 7, request_processed:  [4-->] 5, request_failed: 2, request_stuck: 1  row: 0x10c6155a0  session: 0x10c51df20  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:42,102 - logic_logger - INFO
....DailyFlow[2026-11-19] {Prune Formula: message_stuck [['message_received', 'message_processed', 'message_failed']]} day: 2026-11-19, order_count: 5, order_amount: 1320.00, message_received: 1, message_processed: 1, message_failed: 0, message_stuck: 0, request_received: 7, request_processed:  [4-->] 5, request_failed: 2, request_stuck: 1  row: 0x10c6155a0  session: 0x10c51df20  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:42,102 - logic_logger - INFO
....DailyFlow[2026-11-19] {Formula request_stuck} day: 2026-11-19, order_count: 5, order_amount: 1320.00, message_received: 1, message_processed: 1, message_failed: 0, message_stuck: 0, request_received: 7, request_processed:  [4-->] 5, request_failed: 2, request_stuck:  [1-->] 0  row: 0x10c6155a0  session: 0x10c51df20  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:42,102 - logic_logger - INFO
..Order[None] {Insert - client} id: None, notes: behave test, customer_id: 15, CreatedOn: None, date_shipped: None, amount_total: None, CreatedOnDay: None  row: 0x10c6d96d0  session: 0x10c51df20  ins_upd_dlt: ins, initial: ins - 2026-11-19 17:41:42,102 - logic_logger - INFO
..Order[None] {early_row_event_all_classes - handle_all did stamping} id: None, notes: behave test, customer_id: 15, CreatedOn: 2026-11-19, date_shipped: None, amount_total: None, CreatedOnDay: 2026-11-19  row: 0x10c6d96d0  session: 0x10c51df20  ins_upd_dlt: ins, initial: ins - 2026-11-19 17:41:42,102 - logic_logger - INFO
..Order[None] {server aggregate_defaults: amount_total } id: None, notes: behave test, customer_id: 15, CreatedOn: 2026-11-19, date_shipped: None, amount_total: 0, CreatedOnDay: 2026-11-19  row: 0x10c6d96d0  session: 0x10c51df20  ins_upd_dlt: ins, initial: ins - 2026-11-19 17:41:42,102 - logic_logger - INFO
....DailyFlow[2026-11-19] {Update - Adjusting daily_flow: order_count} day: 2026-11-19, order_count:  [5-->] 6, order_amount: 1320.00, message_received: 1, message_processed: 1, message_failed: 0, message_stuck: 0, request_received: 7, request_processed: 5, request_failed: 2, request_stuck: 0  row: 0x10c6155a0  session: 0x10c51df20  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:42,102 - logic_logger - INFO
....DailyFlow[2026-11-19] {Prune Formula: message_stuck [['message_received', 'message_processed', 'message_failed']]} day: 2026-11-19, order_count:  [5-->] 6, order_amount: 1320.00, message_received: 1, message_processed: 1, message_failed: 0, message_stuck: 0, request_received: 7, request_processed: 5, request_failed: 2, request_stuck: 0  row: 0x10c6155a0  session: 0x10c51df20  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:42,102 - logic_logger - INFO
....DailyFlow[2026-11-19] {Prune Formula: request_stuck [['request_received', 'request_processed', 'request_failed']]} day: 2026-11-19, order_count:  [5-->] 6, order_amount: 1320.00, message_received: 1, message_processed: 1, message_failed: 0, message_stuck: 0, request_received: 7, request_processed: 5, request_failed: 2, request_stuck: 0  row: 0x10c6155a0  session: 0x10c51df20  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:42,102 - logic_logger - INFO
..Item[None] {Insert - client} id: None, order_id: None, product_id: None, quantity: 2, amount: None, unit_price: None  row: 0x10c5d1750  session: 0x10c51df20  ins_upd_dlt: ins, initial: ins - 2026-11-19 17:41:42,102 - logic_logger - INFO
..Item[None] {copy_rules for role: product - unit_price} id: None, order_id: None, product_id: None, quantity: 2, amount: None, unit_price: 90.0000000000  row: 0x10c5d1750  session: 0x10c51df20  ins_upd_dlt: ins, initial: ins - 2026-11-19 17:41:42,102 - logic_logger - INFO
..Item[None] {Formula amount} id: None, order_id: None, product_id: None, quantity: 2, amount: 180.0000000000, unit_price: 90.0000000000  row: 0x10c5d1750  session: 0x10c51df20  ins_upd_dlt: ins, initial: ins - 2026-11-19 17:41:42,102 - logic_logger - INFO
....Order[None] {Update - Adjusting order: amount_total} id: None, notes: behave test, customer_id: 15, CreatedOn: 2026-11-19, date_shipped: None, amount_total:  [0-->] 180.0000000000, CreatedOnDay: 2026-11-19  row: 0x10c6d96d0  session: 0x10c51df20  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:42,103 - logic_logger - INFO
......DailyFlow[2026-11-19] {Update - Adjusting daily_flow: order_amount} day: 2026-11-19, order_count: 6, order_amount:  [1320.00-->] 1500.0000000000, message_received: 1, message_processed: 1, message_failed: 0, message_stuck: 0, request_received: 7, request_processed: 5, request_failed: 2, request_stuck: 0  row: 0x10c6155a0  session: 0x10c51df20  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:42,103 - logic_logger - INFO
......DailyFlow[2026-11-19] {Prune Formula: message_stuck [['message_received', 'message_processed', 'message_failed']]} day: 2026-11-19, order_count: 6, order_amount:  [1320.00-->] 1500.0000000000, message_received: 1, message_processed: 1, message_failed: 0, message_stuck: 0, request_received: 7, request_processed: 5, request_failed: 2, request_stuck: 0  row: 0x10c6155a0  session: 0x10c51df20  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:42,103 - logic_logger - INFO
......DailyFlow[2026-11-19] {Prune Formula: request_stuck [['request_received', 'request_processed', 'request_failed']]} day: 2026-11-19, order_count: 6, order_amount:  [1320.00-->] 1500.0000000000, message_received: 1, message_processed: 1, message_failed: 0, message_stuck: 0, request_received: 7, request_processed: 5, request_failed: 2, request_stuck: 0  row: 0x10c6155a0  session: 0x10c51df20  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:42,103 - logic_logger - INFO
......Customer[15] {Update - Adjusting customer: balance} id: 15, name: Carol 1795138902095, balance:  [0E-10-->] 180.0000000000, credit_limit: 5000.0000000000, email: None, email_opt_out: None  row: 0x10c5d2450  session: 0x10c51df20  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:42,103 - logic_logger - INFO
Logic Phase:		COMMIT LOGIC		(session=0x10c51df20)   										 - 2026-11-19 17:41:42,103 - logic_logger - INFO
Logic Phase:		AFTER_FLUSH LOGIC	(session=0x10c51df20)   										 - 2026-11-19 17:41:42,103 - logic_logger - INFO
..Order[163] {AfterFlush Event} id: 163, notes: behave test, customer_id: 15, CreatedOn: 2026-11-19, date_shipped: None, amount_total: 180.0000000000, CreatedOnDay: 2026-11-19  row: 0x10c6d96d0  session: 0x10c51df20  ins_upd_dlt: ins, initial: ins - 2026-11-19 17:41:42,103 - logic_logger - INFO


Logic Phase:		ROW LOGIC		(session=0x10c51e250) (sqlalchemy before_flush)			 - 2026-11-19 17:41:42,107 - logic_logger - INFO
..Order[163] {Update - client} id: 163, notes: behave test, customer_id: 15, CreatedOn: 2026-11-19, date_shipped:  [None-->] 2026-10-24 00:00:00, amount_total: 180.0000000000, CreatedOnDay: 2026-11-19  row: 0x10c6d9760  session: 0x10c51e250  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:42,107 - logic_logger - INFO
....Customer[15] {Update - Adjusting customer: balance} id: 15, name: Carol 1795138902095, balance:  [180.0000000000-->] 0E-10, credit_limit: 5000.0000000000, email: None, email_opt_out: None  row: 0x10cafc5d0  session: 0x10c51e250  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:42,107 - logic_logger - INFO
Logic Phase:		COMMIT LOGIC		(session=0x10c51e250)   										 - 2026-11-19 17:41:42,107 - logic_logger - INFO
Logic Phase:		AFTER_FLUSH LOGIC	(session=0x10c51e250)   										 - 2026-11-19 17:41:42,108 - logic_logger - INFO
..Order[163] {AfterFlush Event} id: 163, notes: behave test, customer_id: 15, CreatedOn: 2026-11-19, date_shipped:  [None-->] 2026-10-24 00:00:00, amount_total: 180.0000000000, CreatedOnDay: 2026-11-19  row: 0x10c6d9760  session: 0x10c51e250  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:42,108 - logic_logger - INFO
..Order[163] {publish_kafka_message: topic='order_shipping', key={'id': 163}} id: 163, notes: behave test, customer_id: 15, CreatedOn: 2026-11-19, date_shipped:  [None-->] 2026-10-24 00:00:00, amount_total: 180.0000000000, CreatedOnDay: 2026-11-19  row: 0x10c6d9760  session: 0x10c51e250  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:42,116 - logic_logger - INFO

```
</details>

&nbsp;
&nbsp;

#### Scenario: Order Exceeding Credit Rejected ✅ (0.01 s)
&emsp;  Scenario: Order Exceeding Credit Rejected  
&emsp;&emsp;    Given Customer "Dave" with credit limit 100  
&emsp;&emsp;    When B2B order placed for "Dave" with 2 Widget  
&emsp;&emsp;    Then Order is rejected with a credit limit message  
&emsp;&emsp;    And Customer balance should be 0  

<details markdown>
<summary>Rules exercised and logic log (2 transactions)</summary>


&nbsp;
&nbsp;


**Rules Used** in Scenario: Order Exceeding Credit Rejected
```
  DailyFlow  
    1. Derive DailyFlow.request_processed as Count(OrderB2bRequest Where Rule.count(derive=models.DailyFlow.request_processed, as_count_of=models.OrderB2bRequest, where=lambda row: row.is_processed == True, insert_parent=True), insert_parent)  
    2. Derive DailyFlow.request_failed as Count(OrderB2bRequest Where Rule.count(derive=models.DailyFlow.request_failed, as_count_of=models.OrderB2bRequest, where=lambda row: row.error_text is not None, insert_parent=True), insert_parent)  
    3. Derive DailyFlow.request_stuck as Formula (2): Rule.formula(derive=models.DailyFlow.request_stuc [...]  
    4. Derive DailyFlow.request_received as Count(OrderB2bRequest Where  - None, insert_parent)  
    5. Derive DailyFlow.order_amount as Sum(Order.amount_total Where  - None, insert_parent)  
    6. Derive DailyFlow.order_count as Count(Order Where  - None, insert_parent)  
  Customer  
    7. Constraint Function: None  
    8. Derive Customer.balance as Sum(Order.amount_total Where Rule.sum(derive=models.Customer.balance, as_sum_of=models.Order.amount_total, where=lambda row: row.date_shipped is None))  
  Item  
    9. Derive Item.amount as Formula (1): Rule.formula(derive=models.Item.amount, as_expres [...]  
    10. Derive Item.unit_price as Copy(product.unit_price)  
  Order  
    11. Derive Order.amount_total as Sum(Item.amount Where  - None)  
```
**Logic Log** in Scenario: Order Exceeding Credit Rejected (2 transactions)
```
Logic Phase:		ROW LOGIC		(session=0x10c51ff00) (sqlalchemy before_flush)			 - 2026-11-19 17:41:42,126 - logic_logger - INFO
..OrderB2bRequest[None] {Insert - client} id: None, CreatedOn: None, CreatedOnDay: None, payload: {"Account": "Dave 1795138902122", "Notes": "behave test", "Items": [{"Name": "Widget", "QuantityOrdered": 2}]}, is_processed: False, error_text: None  row: 0x10c55ae50  session: 0x10c51ff00  ins_upd_dlt: ins, initial: ins - 2026-11-19 17:41:42,126 - logic_logger - INFO
..OrderB2bRequest[None] {early_row_event_all_classes - handle_all did stamping} id: None, CreatedOn: 2026-11-19 17:41:42.126708, CreatedOnDay: 2026-11-19, payload: {"Account": "Dave 1795138902122", "Notes": "behave test", "Items": [{"Name": "Widget", "QuantityOrdered": 2}]}, is_processed: False, error_text: None  row: 0x10c55ae50  session: 0x10c51ff00  ins_upd_dlt: ins, initial: ins - 2026-11-19 17:41:42,126 - logic_logger - INFO
....DailyFlow[2026-11-19] {Update - Adjusting daily_flow: request_received} day: 2026-11-19, order_count: 6, order_amount: 1500.00, message_received: 1, message_processed: 1, message_failed: 0, message_stuck: 0, request_received:  [7-->] 8, request_processed: 5, request_failed: 2, request_stuck: 0  row: 0x10c615de0  session: 0x10c51ff00  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:42,127 - logic_logger - INFO
....DailyFlow[2026-11-19] {Prune Formula: message_stuck [['message_received', 'message_processed', 'message_failed']]} day: 2026-11-19, order_count: 6, order_amount: 1500.00, message_received: 1, message_processed: 1, message_failed: 0, message_stuck: 0, request_received:  [7-->] 8, request_processed: 5, request_failed: 2, request_stuck: 0  row: 0x10c615de0  session: 0x10c51ff00  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:42,127 - logic_logger - INFO
....DailyFlow[2026-11-19] {Formula request_stuck} day: 2026-11-19, order_count: 6, order_amount: 1500.00, message_received: 1, message_processed: 1, message_failed: 0, message_stuck: 0, request_received:  [7-->] 8, request_processed: 5, request_failed: 2, request_stuck:  [0-->] 1  row: 0x10c615de0  session: 0x10c51ff00  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:42,127 - logic_logger - INFO
Logic Phase:		COMMIT LOGIC		(session=0x10c51ff00)   										 - 2026-11-19 17:41:42,127 - logic_logger - INFO
Logic Phase:		AFTER_FLUSH LOGIC	(session=0x10c51ff00)   										 - 2026-11-19 17:41:42,127 - logic_logger - INFO


Logic Phase:		ROW LOGIC		(session=0x10c51ff00) (sqlalchemy before_flush)			 - 2026-11-19 17:41:42,129 - logic_logger - INFO
..OrderB2bRequest[68] {Update - client} id: 68, CreatedOn: 2026-11-19 17:41:42.126708, CreatedOnDay: 2026-11-19, payload: {"Account": "Dave 1795138902122", "Notes": "behave test", "Items": [{"Name": "Widget", "QuantityOrdered": 2}]}, is_processed:  [False-->] True, error_text: None  row: 0x10c55ae50  session: 0x10c51ff00  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:42,129 - logic_logger - INFO
....DailyFlow[2026-11-19] {Update - Adjusting daily_flow: request_processed} day: 2026-11-19, order_count: 6, order_amount: 1500.00, message_received: 1, message_processed: 1, message_failed: 0, message_stuck: 0, request_received: 8, request_processed:  [5-->] 6, request_failed: 2, request_stuck: 1  row: 0x10c615de0  session: 0x10c51ff00  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:42,129 - logic_logger - INFO
....DailyFlow[2026-11-19] {Prune Formula: message_stuck [['message_received', 'message_processed', 'message_failed']]} day: 2026-11-19, order_count: 6, order_amount: 1500.00, message_received: 1, message_processed: 1, message_failed: 0, message_stuck: 0, request_received: 8, request_processed:  [5-->] 6, request_failed: 2, request_stuck: 1  row: 0x10c615de0  session: 0x10c51ff00  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:42,129 - logic_logger - INFO
....DailyFlow[2026-11-19] {Formula request_stuck} day: 2026-11-19, order_count: 6, order_amount: 1500.00, message_received: 1, message_processed: 1, message_failed: 0, message_stuck: 0, request_received: 8, request_processed:  [5-->] 6, request_failed: 2, request_stuck:  [1-->] 0  row: 0x10c615de0  session: 0x10c51ff00  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:42,129 - logic_logger - INFO
..Product[2] {Update - client} id: 2, name: Widget, count_suppliers: 0, unit_price: 90.0000000000  row: 0x10cb26890  session: 0x10c51ff00  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:42,129 - logic_logger - INFO
..Order[None] {Insert - client} id: None, notes: behave test, customer_id: 16, CreatedOn: None, date_shipped: None, amount_total: None, CreatedOnDay: None  row: 0x10c6da600  session: 0x10c51ff00  ins_upd_dlt: ins, initial: ins - 2026-11-19 17:41:42,129 - logic_logger - INFO
..Order[None] {early_row_event_all_classes - handle_all did stamping} id: None, notes: behave test, customer_id: 16, CreatedOn: 2026-11-19, date_shipped: None, amount_total: None, CreatedOnDay: 2026-11-19  row: 0x10c6da600  session: 0x10c51ff00  ins_upd_dlt: ins, initial: ins - 2026-11-19 17:41:42,129 - logic_logger - INFO
..Order[None] {server aggregate_defaults: amount_total } id: None, notes: behave test, customer_id: 16, CreatedOn: 2026-11-19, date_shipped: None, amount_total: 0, CreatedOnDay: 2026-11-19  row: 0x10c6da600  session: 0x10c51ff00  ins_upd_dlt: ins, initial: ins - 2026-11-19 17:41:42,130 - logic_logger - INFO
....DailyFlow[2026-11-19] {Update - Adjusting daily_flow: order_count} day: 2026-11-19, order_count:  [6-->] 7, order_amount: 1500.00, message_received: 1, message_processed: 1, message_failed: 0, message_stuck: 0, request_received: 8, request_processed: 6, request_failed: 2, request_stuck: 0  row: 0x10c615de0  session: 0x10c51ff00  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:42,130 - logic_logger - INFO
....DailyFlow[2026-11-19] {Prune Formula: message_stuck [['message_received', 'message_processed', 'message_failed']]} day: 2026-11-19, order_count:  [6-->] 7, order_amount: 1500.00, message_received: 1, message_processed: 1, message_failed: 0, message_stuck: 0, request_received: 8, request_processed: 6, request_failed: 2, request_stuck: 0  row: 0x10c615de0  session: 0x10c51ff00  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:42,130 - logic_logger - INFO
....DailyFlow[2026-11-19] {Prune Formula: request_stuck [['request_received', 'request_processed', 'request_failed']]} day: 2026-11-19, order_count:  [6-->] 7, order_amount: 1500.00, message_received: 1, message_processed: 1, message_failed: 0, message_stuck: 0, request_received: 8, request_processed: 6, request_failed: 2, request_stuck: 0  row: 0x10c615de0  session: 0x10c51ff00  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:42,130 - logic_logger - INFO
..Item[None] {Insert - client} id: None, order_id: None, product_id: None, quantity: 2, amount: None, unit_price: None  row: 0x10c6d5150  session: 0x10c51ff00  ins_upd_dlt: ins, initial: ins - 2026-11-19 17:41:42,130 - logic_logger - INFO
..Item[None] {copy_rules for role: product - unit_price} id: None, order_id: None, product_id: None, quantity: 2, amount: None, unit_price: 90.0000000000  row: 0x10c6d5150  session: 0x10c51ff00  ins_upd_dlt: ins, initial: ins - 2026-11-19 17:41:42,130 - logic_logger - INFO
..Item[None] {Formula amount} id: None, order_id: None, product_id: None, quantity: 2, amount: 180.0000000000, unit_price: 90.0000000000  row: 0x10c6d5150  session: 0x10c51ff00  ins_upd_dlt: ins, initial: ins - 2026-11-19 17:41:42,130 - logic_logger - INFO
....Order[None] {Update - Adjusting order: amount_total} id: None, notes: behave test, customer_id: 16, CreatedOn: 2026-11-19, date_shipped: None, amount_total:  [0-->] 180.0000000000, CreatedOnDay: 2026-11-19  row: 0x10c6da600  session: 0x10c51ff00  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:42,130 - logic_logger - INFO
......DailyFlow[2026-11-19] {Update - Adjusting daily_flow: order_amount} day: 2026-11-19, order_count: 7, order_amount:  [1500.00-->] 1680.0000000000, message_received: 1, message_processed: 1, message_failed: 0, message_stuck: 0, request_received: 8, request_processed: 6, request_failed: 2, request_stuck: 0  row: 0x10c615de0  session: 0x10c51ff00  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:42,130 - logic_logger - INFO
......DailyFlow[2026-11-19] {Prune Formula: message_stuck [['message_received', 'message_processed', 'message_failed']]} day: 2026-11-19, order_count: 7, order_amount:  [1500.00-->] 1680.0000000000, message_received: 1, message_processed: 1, message_failed: 0, message_stuck: 0, request_received: 8, request_processed: 6, request_failed: 2, request_stuck: 0  row: 0x10c615de0  session: 0x10c51ff00  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:42,130 - logic_logger - INFO
......DailyFlow[2026-11-19] {Prune Formula: request_stuck [['request_received', 'request_processed', 'request_failed']]} day: 2026-11-19, order_count: 7, order_amount:  [1500.00-->] 1680.0000000000, message_received: 1, message_processed: 1, message_failed: 0, message_stuck: 0, request_received: 8, request_processed: 6, request_failed: 2, request_stuck: 0  row: 0x10c615de0  session: 0x10c51ff00  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:42,130 - logic_logger - INFO
......Customer[16] {Update - Adjusting customer: balance} id: 16, name: Dave 1795138902122, balance:  [0E-10-->] 180.0000000000, credit_limit: 100.0000000000, email: None, email_opt_out: None  row: 0x10c5d1d50  session: 0x10c51ff00  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:42,130 - logic_logger - INFO
......Customer[16] {Constraint Failure: Customer balance (180.0000000000) exceeds credit limit (100.0000000000)} id: 16, name: Dave 1795138902122, balance:  [0E-10-->] 180.0000000000, credit_limit: 100.0000000000, email: None, email_opt_out: None  row: 0x10c5d1d50  session: 0x10c51ff00  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:42,130 - logic_logger - INFO

```
</details>

&nbsp;
&nbsp;

#### Scenario: Order At Credit Limit Accepted ✅ (0.01 s)
&emsp;  Scenario: Order At Credit Limit Accepted  
&emsp;&emsp;    Given Customer "Erin" with credit limit 180  
&emsp;&emsp;    When B2B order placed for "Erin" with 2 Widget  
&emsp;&emsp;    Then Order is accepted  
&emsp;&emsp;    And Customer balance should be 180  

<details markdown>
<summary>Rules exercised and logic log (2 transactions)</summary>


&nbsp;
&nbsp;


**Rules Used** in Scenario: Order At Credit Limit Accepted
```
  DailyFlow  
    1. Derive DailyFlow.request_processed as Count(OrderB2bRequest Where Rule.count(derive=models.DailyFlow.request_processed, as_count_of=models.OrderB2bRequest, where=lambda row: row.is_processed == True, insert_parent=True), insert_parent)  
    2. Derive DailyFlow.request_failed as Count(OrderB2bRequest Where Rule.count(derive=models.DailyFlow.request_failed, as_count_of=models.OrderB2bRequest, where=lambda row: row.error_text is not None, insert_parent=True), insert_parent)  
    3. Derive DailyFlow.request_stuck as Formula (2): Rule.formula(derive=models.DailyFlow.request_stuc [...]  
    4. Derive DailyFlow.request_received as Count(OrderB2bRequest Where  - None, insert_parent)  
    5. Derive DailyFlow.order_amount as Sum(Order.amount_total Where  - None, insert_parent)  
    6. Derive DailyFlow.order_count as Count(Order Where  - None, insert_parent)  
  Customer  
    7. Derive Customer.balance as Sum(Order.amount_total Where Rule.sum(derive=models.Customer.balance, as_sum_of=models.Order.amount_total, where=lambda row: row.date_shipped is None))  
  Item  
    8. Derive Item.amount as Formula (1): Rule.formula(derive=models.Item.amount, as_expres [...]  
    9. Derive Item.unit_price as Copy(product.unit_price)  
  Order  
    10. RowEvent Order._send_order_to_shipping()  
    11. Derive Order.amount_total as Sum(Item.amount Where  - None)  
```
**Logic Log** in Scenario: Order At Credit Limit Accepted (2 transactions)
```
Logic Phase:		ROW LOGIC		(session=0x10cb6c380) (sqlalchemy before_flush)			 - 2026-11-19 17:41:42,141 - logic_logger - INFO
..OrderB2bRequest[None] {Insert - client} id: None, CreatedOn: None, CreatedOnDay: None, payload: {"Account": "Erin 1795138902137", "Notes": "behave test", "Items": [{"Name": "Widget", "QuantityOrdered": 2}]}, is_processed: False, error_text: None  row: 0x10c6d69d0  session: 0x10cb6c380  ins_upd_dlt: ins, initial: ins - 2026-11-19 17:41:42,141 - logic_logger - INFO
..OrderB2bRequest[None] {early_row_event_all_classes - handle_all did stamping} id: None, CreatedOn: 2026-11-19 17:41:42.141243, CreatedOnDay: 2026-11-19, payload: {"Account": "Erin 1795138902137", "Notes": "behave test", "Items": [{"Name": "Widget", "QuantityOrdered": 2}]}, is_processed: False, error_text: None  row: 0x10c6d69d0  session: 0x10cb6c380  ins_upd_dlt: ins, initial: ins - 2026-11-19 17:41:42,141 - logic_logger - INFO
....DailyFlow[2026-11-19] {Update - Adjusting daily_flow: request_received} day: 2026-11-19, order_count: 6, order_amount: 1500.00, message_received: 1, message_processed: 1, message_failed: 0, message_stuck: 0, request_received:  [8-->] 9, request_processed: 5, request_failed: 3, request_stuck: 0  row: 0x10c6159c0  session: 0x10cb6c380  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:42,141 - logic_logger - INFO
....DailyFlow[2026-11-19] {Prune Formula: message_stuck [['message_received', 'message_processed', 'message_failed']]} day: 2026-11-19, order_count: 6, order_amount: 1500.00, message_received: 1, message_processed: 1, message_failed: 0, message_stuck: 0, request_received:  [8-->] 9, request_processed: 5, request_failed: 3, request_stuck: 0  row: 0x10c6159c0  session: 0x10cb6c380  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:42,141 - logic_logger - INFO
....DailyFlow[2026-11-19] {Formula request_stuck} day: 2026-11-19, order_count: 6, order_amount: 1500.00, message_received: 1, message_processed: 1, message_failed: 0, message_stuck: 0, request_received:  [8-->] 9, request_processed: 5, request_failed: 3, request_stuck:  [0-->] 1  row: 0x10c6159c0  session: 0x10cb6c380  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:42,141 - logic_logger - INFO
Logic Phase:		COMMIT LOGIC		(session=0x10cb6c380)   										 - 2026-11-19 17:41:42,141 - logic_logger - INFO
Logic Phase:		AFTER_FLUSH LOGIC	(session=0x10cb6c380)   										 - 2026-11-19 17:41:42,142 - logic_logger - INFO


Logic Phase:		ROW LOGIC		(session=0x10cb6c380) (sqlalchemy before_flush)			 - 2026-11-19 17:41:42,144 - logic_logger - INFO
..OrderB2bRequest[69] {Update - client} id: 69, CreatedOn: 2026-11-19 17:41:42.141243, CreatedOnDay: 2026-11-19, payload: {"Account": "Erin 1795138902137", "Notes": "behave test", "Items": [{"Name": "Widget", "QuantityOrdered": 2}]}, is_processed:  [False-->] True, error_text: None  row: 0x10c6d69d0  session: 0x10cb6c380  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:42,144 - logic_logger - INFO
....DailyFlow[2026-11-19] {Update - Adjusting daily_flow: request_processed} day: 2026-11-19, order_count: 6, order_amount: 1500.00, message_received: 1, message_processed: 1, message_failed: 0, message_stuck: 0, request_received: 9, request_processed:  [5-->] 6, request_failed: 3, request_stuck: 1  row: 0x10c6159c0  session: 0x10cb6c380  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:42,144 - logic_logger - INFO
....DailyFlow[2026-11-19] {Prune Formula: message_stuck [['message_received', 'message_processed', 'message_failed']]} day: 2026-11-19, order_count: 6, order_amount: 1500.00, message_received: 1, message_processed: 1, message_failed: 0, message_stuck: 0, request_received: 9, request_processed:  [5-->] 6, request_failed: 3, request_stuck: 1  row: 0x10c6159c0  session: 0x10cb6c380  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:42,144 - logic_logger - INFO
....DailyFlow[2026-11-19] {Formula request_stuck} day: 2026-11-19, order_count: 6, order_amount: 1500.00, message_received: 1, message_processed: 1, message_failed: 0, message_stuck: 0, request_received: 9, request_processed:  [5-->] 6, request_failed: 3, request_stuck:  [1-->] 0  row: 0x10c6159c0  session: 0x10cb6c380  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:42,144 - logic_logger - INFO
..Product[2] {Update - client} id: 2, name: Widget, count_suppliers: 0, unit_price: 90.0000000000  row: 0x10cb26f20  session: 0x10cb6c380  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:42,144 - logic_logger - INFO
..Order[None] {Insert - client} id: None, notes: behave test, customer_id: 17, CreatedOn: None, date_shipped: None, amount_total: None, CreatedOnDay: None  row: 0x10c6da960  session: 0x10cb6c380  ins_upd_dlt: ins, initial: ins - 2026-11-19 17:41:42,144 - logic_logger - INFO
..Order[None] {early_row_event_all_classes - handle_all did stamping} id: None, notes: behave test, customer_id: 17, CreatedOn: 2026-11-19, date_shipped: None, amount_total: None, CreatedOnDay: 2026-11-19  row: 0x10c6da960  session: 0x10cb6c380  ins_upd_dlt: ins, initial: ins - 2026-11-19 17:41:42,144 - logic_logger - INFO
..Order[None] {server aggregate_defaults: amount_total } id: None, notes: behave test, customer_id: 17, CreatedOn: 2026-11-19, date_shipped: None, amount_total: 0, CreatedOnDay: 2026-11-19  row: 0x10c6da960  session: 0x10cb6c380  ins_upd_dlt: ins, initial: ins - 2026-11-19 17:41:42,144 - logic_logger - INFO
....DailyFlow[2026-11-19] {Update - Adjusting daily_flow: order_count} day: 2026-11-19, order_count:  [6-->] 7, order_amount: 1500.00, message_received: 1, message_processed: 1, message_failed: 0, message_stuck: 0, request_received: 9, request_processed: 6, request_failed: 3, request_stuck: 0  row: 0x10c6159c0  session: 0x10cb6c380  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:42,144 - logic_logger - INFO
....DailyFlow[2026-11-19] {Prune Formula: message_stuck [['message_received', 'message_processed', 'message_failed']]} day: 2026-11-19, order_count:  [6-->] 7, order_amount: 1500.00, message_received: 1, message_processed: 1, message_failed: 0, message_stuck: 0, request_received: 9, request_processed: 6, request_failed: 3, request_stuck: 0  row: 0x10c6159c0  session: 0x10cb6c380  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:42,144 - logic_logger - INFO
....DailyFlow[2026-11-19] {Prune Formula: request_stuck [['request_received', 'request_processed', 'request_failed']]} day: 2026-11-19, order_count:  [6-->] 7, order_amount: 1500.00, message_received: 1, message_processed: 1, message_failed: 0, message_stuck: 0, request_received: 9, request_processed: 6, request_failed: 3, request_stuck: 0  row: 0x10c6159c0  session: 0x10cb6c380  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:42,144 - logic_logger - INFO
..Item[None] {Insert - client} id: None, order_id: None, product_id: None, quantity: 2, amount: None, unit_price: None  row: 0x10c6d4f50  session: 0x10cb6c380  ins_upd_dlt: ins, initial: ins - 2026-11-19 17:41:42,144 - logic_logger - INFO
..Item[None] {copy_rules for role: product - unit_price} id: None, order_id: None, product_id: None, quantity: 2, amount: None, unit_price: 90.0000000000  row: 0x10c6d4f50  session: 0x10cb6c380  ins_upd_dlt: ins, initial: ins - 2026-11-19 17:41:42,145 - logic_logger - INFO
..Item[None] {Formula amount} id: None, order_id: None, product_id: None, quantity: 2, amount: 180.0000000000, unit_price: 90.0000000000  row: 0x10c6d4f50  session: 0x10cb6c380  ins_upd_dlt: ins, initial: ins - 2026-11-19 17:41:42,145 - logic_logger - INFO
....Order[None] {Update - Adjusting order: amount_total} id: None, notes: behave test, customer_id: 17, CreatedOn: 2026-11-19, date_shipped: None, amount_total:  [0-->] 180.0000000000, CreatedOnDay: 2026-11-19  row: 0x10c6da960  session: 0x10cb6c380  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:42,145 - logic_logger - INFO
......DailyFlow[2026-11-19] {Update - Adjusting daily_flow: order_amount} day: 2026-11-19, order_count: 7, order_amount:  [1500.00-->] 1680.0000000000, message_received: 1, message_processed: 1, message_failed: 0, message_stuck: 0, request_received: 9, request_processed: 6, request_failed: 3, request_stuck: 0  row: 0x10c6159c0  session: 0x10cb6c380  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:42,145 - logic_logger - INFO
......DailyFlow[2026-11-19] {Prune Formula: message_stuck [['message_received', 'message_processed', 'message_failed']]} day: 2026-11-19, order_count: 7, order_amount:  [1500.00-->] 1680.0000000000, message_received: 1, message_processed: 1, message_failed: 0, message_stuck: 0, request_received: 9, request_processed: 6, request_failed: 3, request_stuck: 0  row: 0x10c6159c0  session: 0x10cb6c380  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:42,145 - logic_logger - INFO
......DailyFlow[2026-11-19] {Prune Formula: request_stuck [['request_received', 'request_processed', 'request_failed']]} day: 2026-11-19, order_count: 7, order_amount:  [1500.00-->] 1680.0000000000, message_received: 1, message_processed: 1, message_failed: 0, message_stuck: 0, request_received: 9, request_processed: 6, request_failed: 3, request_stuck: 0  row: 0x10c6159c0  session: 0x10cb6c380  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:42,145 - logic_logger - INFO
......Customer[17] {Update - Adjusting customer: balance} id: 17, name: Erin 1795138902137, balance:  [0E-10-->] 180.0000000000, credit_limit: 180.0000000000, email: None, email_opt_out: None  row: 0x10c5e9750  session: 0x10cb6c380  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:42,145 - logic_logger - INFO
Logic Phase:		COMMIT LOGIC		(session=0x10cb6c380)   										 - 2026-11-19 17:41:42,145 - logic_logger - INFO
Logic Phase:		AFTER_FLUSH LOGIC	(session=0x10cb6c380)   										 - 2026-11-19 17:41:42,146 - logic_logger - INFO
..Order[164] {AfterFlush Event} id: 164, notes: behave test, customer_id: 17, CreatedOn: 2026-11-19, date_shipped: None, amount_total: 180.0000000000, CreatedOnDay: 2026-11-19  row: 0x10c6da960  session: 0x10cb6c380  ins_upd_dlt: ins, initial: ins - 2026-11-19 17:41:42,146 - logic_logger - INFO

```
</details>

&nbsp;
&nbsp;

#### Scenario: Unshipped Order Enters Balance ✅ (0.02 s)
&emsp;  Scenario: Unshipped Order Enters Balance  
&emsp;&emsp;    Given Customer "Fay" with credit limit 5000  
&emsp;&emsp;    And Order is created for "Fay" with 2 Widget  
&emsp;&emsp;    And Order has been shipped  
&emsp;&emsp;    When Order is unshipped  
&emsp;&emsp;    Then Customer balance should be 180  

<details markdown>
<summary>Rules exercised and logic log (4 transactions)</summary>


&nbsp;
&nbsp;


**Rules Used** in Scenario: Unshipped Order Enters Balance
```
  DailyFlow  
    1. Derive DailyFlow.request_processed as Count(OrderB2bRequest Where Rule.count(derive=models.DailyFlow.request_processed, as_count_of=models.OrderB2bRequest, where=lambda row: row.is_processed == True, insert_parent=True), insert_parent)  
    2. Derive DailyFlow.request_failed as Count(OrderB2bRequest Where Rule.count(derive=models.DailyFlow.request_failed, as_count_of=models.OrderB2bRequest, where=lambda row: row.error_text is not None, insert_parent=True), insert_parent)  
    3. Derive DailyFlow.request_stuck as Formula (2): Rule.formula(derive=models.DailyFlow.request_stuc [...]  
    4. Derive DailyFlow.request_received as Count(OrderB2bRequest Where  - None, insert_parent)  
    5. Derive DailyFlow.order_amount as Sum(Order.amount_total Where  - None, insert_parent)  
    6. Derive DailyFlow.order_count as Count(Order Where  - None, insert_parent)  
  Customer  
    7. Derive Customer.balance as Sum(Order.amount_total Where Rule.sum(derive=models.Customer.balance, as_sum_of=models.Order.amount_total, where=lambda row: row.date_shipped is None))  
  Item  
    8. Derive Item.amount as Formula (1): Rule.formula(derive=models.Item.amount, as_expres [...]  
    9. Derive Item.unit_price as Copy(product.unit_price)  
  Order  
    10. RowEvent Order._send_order_to_shipping()  
    11. Derive Order.amount_total as Sum(Item.amount Where  - None)  
```
**Logic Log** in Scenario: Unshipped Order Enters Balance (4 transactions)
```
Logic Phase:		ROW LOGIC		(session=0x10c51dd00) (sqlalchemy before_flush)			 - 2026-11-19 17:41:42,155 - logic_logger - INFO
..OrderB2bRequest[None] {Insert - client} id: None, CreatedOn: None, CreatedOnDay: None, payload: {"Account": "Fay 1795138902150", "Notes": "behave test", "Items": [{"Name": "Widget", "QuantityOrdered": 2}]}, is_processed: False, error_text: None  row: 0x10c5eb3d0  session: 0x10c51dd00  ins_upd_dlt: ins, initial: ins - 2026-11-19 17:41:42,155 - logic_logger - INFO
..OrderB2bRequest[None] {early_row_event_all_classes - handle_all did stamping} id: None, CreatedOn: 2026-11-19 17:41:42.155368, CreatedOnDay: 2026-11-19, payload: {"Account": "Fay 1795138902150", "Notes": "behave test", "Items": [{"Name": "Widget", "QuantityOrdered": 2}]}, is_processed: False, error_text: None  row: 0x10c5eb3d0  session: 0x10c51dd00  ins_upd_dlt: ins, initial: ins - 2026-11-19 17:41:42,155 - logic_logger - INFO
....DailyFlow[2026-11-19] {Update - Adjusting daily_flow: request_received} day: 2026-11-19, order_count: 7, order_amount: 1680.00, message_received: 1, message_processed: 1, message_failed: 0, message_stuck: 0, request_received:  [9-->] 10, request_processed: 6, request_failed: 3, request_stuck: 0  row: 0x10c6159c0  session: 0x10c51dd00  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:42,155 - logic_logger - INFO
....DailyFlow[2026-11-19] {Prune Formula: message_stuck [['message_received', 'message_processed', 'message_failed']]} day: 2026-11-19, order_count: 7, order_amount: 1680.00, message_received: 1, message_processed: 1, message_failed: 0, message_stuck: 0, request_received:  [9-->] 10, request_processed: 6, request_failed: 3, request_stuck: 0  row: 0x10c6159c0  session: 0x10c51dd00  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:42,155 - logic_logger - INFO
....DailyFlow[2026-11-19] {Formula request_stuck} day: 2026-11-19, order_count: 7, order_amount: 1680.00, message_received: 1, message_processed: 1, message_failed: 0, message_stuck: 0, request_received:  [9-->] 10, request_processed: 6, request_failed: 3, request_stuck:  [0-->] 1  row: 0x10c6159c0  session: 0x10c51dd00  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:42,155 - logic_logger - INFO
Logic Phase:		COMMIT LOGIC		(session=0x10c51dd00)   										 - 2026-11-19 17:41:42,155 - logic_logger - INFO
Logic Phase:		AFTER_FLUSH LOGIC	(session=0x10c51dd00)   										 - 2026-11-19 17:41:42,156 - logic_logger - INFO


Logic Phase:		ROW LOGIC		(session=0x10c51dd00) (sqlalchemy before_flush)			 - 2026-11-19 17:41:42,158 - logic_logger - INFO
..Product[2] {Update - client} id: 2, name: Widget, count_suppliers: 0, unit_price: 90.0000000000  row: 0x10cb26c80  session: 0x10c51dd00  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:42,158 - logic_logger - INFO
..OrderB2bRequest[70] {Update - client} id: 70, CreatedOn: 2026-11-19 17:41:42.155368, CreatedOnDay: 2026-11-19, payload: {"Account": "Fay 1795138902150", "Notes": "behave test", "Items": [{"Name": "Widget", "QuantityOrdered": 2}]}, is_processed:  [False-->] True, error_text: None  row: 0x10c5eb3d0  session: 0x10c51dd00  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:42,158 - logic_logger - INFO
....DailyFlow[2026-11-19] {Update - Adjusting daily_flow: request_processed} day: 2026-11-19, order_count: 7, order_amount: 1680.00, message_received: 1, message_processed: 1, message_failed: 0, message_stuck: 0, request_received: 10, request_processed:  [6-->] 7, request_failed: 3, request_stuck: 1  row: 0x10c6159c0  session: 0x10c51dd00  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:42,158 - logic_logger - INFO
....DailyFlow[2026-11-19] {Prune Formula: message_stuck [['message_received', 'message_processed', 'message_failed']]} day: 2026-11-19, order_count: 7, order_amount: 1680.00, message_received: 1, message_processed: 1, message_failed: 0, message_stuck: 0, request_received: 10, request_processed:  [6-->] 7, request_failed: 3, request_stuck: 1  row: 0x10c6159c0  session: 0x10c51dd00  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:42,158 - logic_logger - INFO
....DailyFlow[2026-11-19] {Formula request_stuck} day: 2026-11-19, order_count: 7, order_amount: 1680.00, message_received: 1, message_processed: 1, message_failed: 0, message_stuck: 0, request_received: 10, request_processed:  [6-->] 7, request_failed: 3, request_stuck:  [1-->] 0  row: 0x10c6159c0  session: 0x10c51dd00  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:42,158 - logic_logger - INFO
..Order[None] {Insert - client} id: None, notes: behave test, customer_id: 18, CreatedOn: None, date_shipped: None, amount_total: None, CreatedOnDay: None  row: 0x10c6daa80  session: 0x10c51dd00  ins_upd_dlt: ins, initial: ins - 2026-11-19 17:41:42,158 - logic_logger - INFO
..Order[None] {early_row_event_all_classes - handle_all did stamping} id: None, notes: behave test, customer_id: 18, CreatedOn: 2026-11-19, date_shipped: None, amount_total: None, CreatedOnDay: 2026-11-19  row: 0x10c6daa80  session: 0x10c51dd00  ins_upd_dlt: ins, initial: ins - 2026-11-19 17:41:42,158 - logic_logger - INFO
..Order[None] {server aggregate_defaults: amount_total } id: None, notes: behave test, customer_id: 18, CreatedOn: 2026-11-19, date_shipped: None, amount_total: 0, CreatedOnDay: 2026-11-19  row: 0x10c6daa80  session: 0x10c51dd00  ins_upd_dlt: ins, initial: ins - 2026-11-19 17:41:42,158 - logic_logger - INFO
....DailyFlow[2026-11-19] {Update - Adjusting daily_flow: order_count} day: 2026-11-19, order_count:  [7-->] 8, order_amount: 1680.00, message_received: 1, message_processed: 1, message_failed: 0, message_stuck: 0, request_received: 10, request_processed: 7, request_failed: 3, request_stuck: 0  row: 0x10c6159c0  session: 0x10c51dd00  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:42,158 - logic_logger - INFO
....DailyFlow[2026-11-19] {Prune Formula: message_stuck [['message_received', 'message_processed', 'message_failed']]} day: 2026-11-19, order_count:  [7-->] 8, order_amount: 1680.00, message_received: 1, message_processed: 1, message_failed: 0, message_stuck: 0, request_received: 10, request_processed: 7, request_failed: 3, request_stuck: 0  row: 0x10c6159c0  session: 0x10c51dd00  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:42,159 - logic_logger - INFO
....DailyFlow[2026-11-19] {Prune Formula: request_stuck [['request_received', 'request_processed', 'request_failed']]} day: 2026-11-19, order_count:  [7-->] 8, order_amount: 1680.00, message_received: 1, message_processed: 1, message_failed: 0, message_stuck: 0, request_received: 10, request_processed: 7, request_failed: 3, request_stuck: 0  row: 0x10c6159c0  session: 0x10c51dd00  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:42,159 - logic_logger - INFO
..Item[None] {Insert - client} id: None, order_id: None, product_id: None, quantity: 2, amount: None, unit_price: None  row: 0x10cafe1d0  session: 0x10c51dd00  ins_upd_dlt: ins, initial: ins - 2026-11-19 17:41:42,159 - logic_logger - INFO
..Item[None] {copy_rules for role: product - unit_price} id: None, order_id: None, product_id: None, quantity: 2, amount: None, unit_price: 90.0000000000  row: 0x10cafe1d0  session: 0x10c51dd00  ins_upd_dlt: ins, initial: ins - 2026-11-19 17:41:42,159 - logic_logger - INFO
..Item[None] {Formula amount} id: None, order_id: None, product_id: None, quantity: 2, amount: 180.0000000000, unit_price: 90.0000000000  row: 0x10cafe1d0  session: 0x10c51dd00  ins_upd_dlt: ins, initial: ins - 2026-11-19 17:41:42,159 - logic_logger - INFO
....Order[None] {Update - Adjusting order: amount_total} id: None, notes: behave test, customer_id: 18, CreatedOn: 2026-11-19, date_shipped: None, amount_total:  [0-->] 180.0000000000, CreatedOnDay: 2026-11-19  row: 0x10c6daa80  session: 0x10c51dd00  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:42,159 - logic_logger - INFO
......DailyFlow[2026-11-19] {Update - Adjusting daily_flow: order_amount} day: 2026-11-19, order_count: 8, order_amount:  [1680.00-->] 1860.0000000000, message_received: 1, message_processed: 1, message_failed: 0, message_stuck: 0, request_received: 10, request_processed: 7, request_failed: 3, request_stuck: 0  row: 0x10c6159c0  session: 0x10c51dd00  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:42,159 - logic_logger - INFO
......DailyFlow[2026-11-19] {Prune Formula: message_stuck [['message_received', 'message_processed', 'message_failed']]} day: 2026-11-19, order_count: 8, order_amount:  [1680.00-->] 1860.0000000000, message_received: 1, message_processed: 1, message_failed: 0, message_stuck: 0, request_received: 10, request_processed: 7, request_failed: 3, request_stuck: 0  row: 0x10c6159c0  session: 0x10c51dd00  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:42,159 - logic_logger - INFO
......DailyFlow[2026-11-19] {Prune Formula: request_stuck [['request_received', 'request_processed', 'request_failed']]} day: 2026-11-19, order_count: 8, order_amount:  [1680.00-->] 1860.0000000000, message_received: 1, message_processed: 1, message_failed: 0, message_stuck: 0, request_received: 10, request_processed: 7, request_failed: 3, request_stuck: 0  row: 0x10c6159c0  session: 0x10c51dd00  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:42,159 - logic_logger - INFO
......Customer[18] {Update - Adjusting customer: balance} id: 18, name: Fay 1795138902150, balance:  [0E-10-->] 180.0000000000, credit_limit: 5000.0000000000, email: None, email_opt_out: None  row: 0x10c55bf50  session: 0x10c51dd00  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:42,159 - logic_logger - INFO
Logic Phase:		COMMIT LOGIC		(session=0x10c51dd00)   										 - 2026-11-19 17:41:42,159 - logic_logger - INFO
Logic Phase:		AFTER_FLUSH LOGIC	(session=0x10c51dd00)   										 - 2026-11-19 17:41:42,160 - logic_logger - INFO
..Order[165] {AfterFlush Event} id: 165, notes: behave test, customer_id: 18, CreatedOn: 2026-11-19, date_shipped: None, amount_total: 180.0000000000, CreatedOnDay: 2026-11-19  row: 0x10c6daa80  session: 0x10c51dd00  ins_upd_dlt: ins, initial: ins - 2026-11-19 17:41:42,160 - logic_logger - INFO


Logic Phase:		ROW LOGIC		(session=0x10c51d9d0) (sqlalchemy before_flush)			 - 2026-11-19 17:41:42,162 - logic_logger - INFO
..Order[165] {Update - client} id: 165, notes: behave test, customer_id: 18, CreatedOn: 2026-11-19, date_shipped:  [None-->] 2026-10-24 00:00:00, amount_total: 180.0000000000, CreatedOnDay: 2026-11-19  row: 0x10c6da840  session: 0x10c51d9d0  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:42,163 - logic_logger - INFO
....Customer[18] {Update - Adjusting customer: balance} id: 18, name: Fay 1795138902150, balance:  [180.0000000000-->] 0E-10, credit_limit: 5000.0000000000, email: None, email_opt_out: None  row: 0x10cb4d9d0  session: 0x10c51d9d0  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:42,163 - logic_logger - INFO
Logic Phase:		COMMIT LOGIC		(session=0x10c51d9d0)   										 - 2026-11-19 17:41:42,163 - logic_logger - INFO
Logic Phase:		AFTER_FLUSH LOGIC	(session=0x10c51d9d0)   										 - 2026-11-19 17:41:42,163 - logic_logger - INFO
..Order[165] {AfterFlush Event} id: 165, notes: behave test, customer_id: 18, CreatedOn: 2026-11-19, date_shipped:  [None-->] 2026-10-24 00:00:00, amount_total: 180.0000000000, CreatedOnDay: 2026-11-19  row: 0x10c6da840  session: 0x10c51d9d0  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:42,163 - logic_logger - INFO
..Order[165] {publish_kafka_message: topic='order_shipping', key={'id': 165}} id: 165, notes: behave test, customer_id: 18, CreatedOn: 2026-11-19, date_shipped:  [None-->] 2026-10-24 00:00:00, amount_total: 180.0000000000, CreatedOnDay: 2026-11-19  row: 0x10c6da840  session: 0x10c51d9d0  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:42,165 - logic_logger - INFO


Logic Phase:		ROW LOGIC		(session=0x10c51df20) (sqlalchemy before_flush)			 - 2026-11-19 17:41:42,169 - logic_logger - INFO
..Order[165] {Update - client} id: 165, notes: behave test, customer_id: 18, CreatedOn: 2026-11-19, date_shipped:  [2026-10-24-->] None, amount_total: 180.0000000000, CreatedOnDay: 2026-11-19  row: 0x10c6da600  session: 0x10c51df20  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:42,169 - logic_logger - INFO
....Customer[18] {Update - Adjusting customer: balance} id: 18, name: Fay 1795138902150, balance:  [0E-10-->] 180.0000000000, credit_limit: 5000.0000000000, email: None, email_opt_out: None  row: 0x10cb82550  session: 0x10c51df20  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:42,169 - logic_logger - INFO
Logic Phase:		COMMIT LOGIC		(session=0x10c51df20)   										 - 2026-11-19 17:41:42,169 - logic_logger - INFO
Logic Phase:		AFTER_FLUSH LOGIC	(session=0x10c51df20)   										 - 2026-11-19 17:41:42,169 - logic_logger - INFO
..Order[165] {AfterFlush Event} id: 165, notes: behave test, customer_id: 18, CreatedOn: 2026-11-19, date_shipped:  [2026-10-24-->] None, amount_total: 180.0000000000, CreatedOnDay: 2026-11-19  row: 0x10c6da600  session: 0x10c51df20  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:42,169 - logic_logger - INFO

```
</details>

&nbsp;
&nbsp;

#### Scenario: Item Deleted Reduces Order ✅ (0.03 s)
&emsp;  Scenario: Item Deleted Reduces Order  
&emsp;&emsp;    Given Customer "Gus" with credit limit 5000  
&emsp;&emsp;    And Order is created for "Gus" with 2 Widget and 1 Gadget  
&emsp;&emsp;    When the Gadget Item is deleted  
&emsp;&emsp;    Then Order amount_total should be 180  
&emsp;&emsp;    And Customer balance should be 180  

<details markdown>
<summary>Rules exercised and logic log (3 transactions)</summary>


&nbsp;
&nbsp;


**Rules Used** in Scenario: Item Deleted Reduces Order
```
  DailyFlow  
    1. Derive DailyFlow.request_processed as Count(OrderB2bRequest Where Rule.count(derive=models.DailyFlow.request_processed, as_count_of=models.OrderB2bRequest, where=lambda row: row.is_processed == True, insert_parent=True), insert_parent)  
    2. Derive DailyFlow.request_failed as Count(OrderB2bRequest Where Rule.count(derive=models.DailyFlow.request_failed, as_count_of=models.OrderB2bRequest, where=lambda row: row.error_text is not None, insert_parent=True), insert_parent)  
    3. Derive DailyFlow.request_stuck as Formula (2): Rule.formula(derive=models.DailyFlow.request_stuc [...]  
    4. Derive DailyFlow.request_received as Count(OrderB2bRequest Where  - None, insert_parent)  
    5. Derive DailyFlow.order_amount as Sum(Order.amount_total Where  - None, insert_parent)  
    6. Derive DailyFlow.order_count as Count(Order Where  - None, insert_parent)  
  Customer  
    7. Derive Customer.balance as Sum(Order.amount_total Where Rule.sum(derive=models.Customer.balance, as_sum_of=models.Order.amount_total, where=lambda row: row.date_shipped is None))  
  Item  
    8. Derive Item.amount as Formula (1): Rule.formula(derive=models.Item.amount, as_expres [...]  
    9. Derive Item.unit_price as Copy(product.unit_price)  
  Order  
    10. RowEvent Order._send_order_to_shipping()  
    11. Derive Order.amount_total as Sum(Item.amount Where  - None)  
```
**Logic Log** in Scenario: Item Deleted Reduces Order (3 transactions)
```
Logic Phase:		ROW LOGIC		(session=0x10cb6c490) (sqlalchemy before_flush)			 - 2026-11-19 17:41:42,178 - logic_logger - INFO
..OrderB2bRequest[None] {Insert - client} id: None, CreatedOn: None, CreatedOnDay: None, payload: {"Account": "Gus 1795138902174", "Notes": "behave test", "Items": [{"Name": "Widget", "QuantityOrdered": 2}, {"Name": "Gadget", "QuantityOrdered": 1}]}, is_processed: False, error_text: None  row: 0x10cafd150  session: 0x10cb6c490  ins_upd_dlt: ins, initial: ins - 2026-11-19 17:41:42,178 - logic_logger - INFO
..OrderB2bRequest[None] {early_row_event_all_classes - handle_all did stamping} id: None, CreatedOn: 2026-11-19 17:41:42.178967, CreatedOnDay: 2026-11-19, payload: {"Account": "Gus 1795138902174", "Notes": "behave test", "Items": [{"Name": "Widget", "QuantityOrdered": 2}, {"Name": "Gadget", "QuantityOrdered": 1}]}, is_processed: False, error_text: None  row: 0x10cafd150  session: 0x10cb6c490  ins_upd_dlt: ins, initial: ins - 2026-11-19 17:41:42,178 - logic_logger - INFO
....DailyFlow[2026-11-19] {Update - Adjusting daily_flow: request_received} day: 2026-11-19, order_count: 8, order_amount: 1860.00, message_received: 1, message_processed: 1, message_failed: 0, message_stuck: 0, request_received:  [10-->] 11, request_processed: 7, request_failed: 3, request_stuck: 0  row: 0x10c615bd0  session: 0x10cb6c490  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:42,179 - logic_logger - INFO
....DailyFlow[2026-11-19] {Prune Formula: message_stuck [['message_received', 'message_processed', 'message_failed']]} day: 2026-11-19, order_count: 8, order_amount: 1860.00, message_received: 1, message_processed: 1, message_failed: 0, message_stuck: 0, request_received:  [10-->] 11, request_processed: 7, request_failed: 3, request_stuck: 0  row: 0x10c615bd0  session: 0x10cb6c490  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:42,179 - logic_logger - INFO
....DailyFlow[2026-11-19] {Formula request_stuck} day: 2026-11-19, order_count: 8, order_amount: 1860.00, message_received: 1, message_processed: 1, message_failed: 0, message_stuck: 0, request_received:  [10-->] 11, request_processed: 7, request_failed: 3, request_stuck:  [0-->] 1  row: 0x10c615bd0  session: 0x10cb6c490  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:42,179 - logic_logger - INFO
Logic Phase:		COMMIT LOGIC		(session=0x10cb6c490)   										 - 2026-11-19 17:41:42,179 - logic_logger - INFO
Logic Phase:		AFTER_FLUSH LOGIC	(session=0x10cb6c490)   										 - 2026-11-19 17:41:42,179 - logic_logger - INFO


Logic Phase:		ROW LOGIC		(session=0x10cb6c490) (sqlalchemy before_flush)			 - 2026-11-19 17:41:42,182 - logic_logger - INFO
..OrderB2bRequest[71] {Update - client} id: 71, CreatedOn: 2026-11-19 17:41:42.178967, CreatedOnDay: 2026-11-19, payload: {"Account": "Gus 1795138902174", "Notes": "behave test", "Items": [{"Name": "Widget", "QuantityOrdered": 2}, {"Name": "Gadget", "QuantityOrdered": 1}]}, is_processed:  [False-->] True, error_text: None  row: 0x10cafd150  session: 0x10cb6c490  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:42,182 - logic_logger - INFO
....DailyFlow[2026-11-19] {Update - Adjusting daily_flow: request_processed} day: 2026-11-19, order_count: 8, order_amount: 1860.00, message_received: 1, message_processed: 1, message_failed: 0, message_stuck: 0, request_received: 11, request_processed:  [7-->] 8, request_failed: 3, request_stuck: 1  row: 0x10c615bd0  session: 0x10cb6c490  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:42,182 - logic_logger - INFO
....DailyFlow[2026-11-19] {Prune Formula: message_stuck [['message_received', 'message_processed', 'message_failed']]} day: 2026-11-19, order_count: 8, order_amount: 1860.00, message_received: 1, message_processed: 1, message_failed: 0, message_stuck: 0, request_received: 11, request_processed:  [7-->] 8, request_failed: 3, request_stuck: 1  row: 0x10c615bd0  session: 0x10cb6c490  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:42,182 - logic_logger - INFO
....DailyFlow[2026-11-19] {Formula request_stuck} day: 2026-11-19, order_count: 8, order_amount: 1860.00, message_received: 1, message_processed: 1, message_failed: 0, message_stuck: 0, request_received: 11, request_processed:  [7-->] 8, request_failed: 3, request_stuck:  [1-->] 0  row: 0x10c615bd0  session: 0x10cb6c490  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:42,182 - logic_logger - INFO
..Product[1] {Update - client} id: 1, name: Gadget, count_suppliers: 0, unit_price: 150.0000000000  row: 0x10cb27150  session: 0x10cb6c490  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:42,182 - logic_logger - INFO
..Order[None] {Insert - client} id: None, notes: behave test, customer_id: 19, CreatedOn: None, date_shipped: None, amount_total: None, CreatedOnDay: None  row: 0x10c6d9490  session: 0x10cb6c490  ins_upd_dlt: ins, initial: ins - 2026-11-19 17:41:42,182 - logic_logger - INFO
..Order[None] {early_row_event_all_classes - handle_all did stamping} id: None, notes: behave test, customer_id: 19, CreatedOn: 2026-11-19, date_shipped: None, amount_total: None, CreatedOnDay: 2026-11-19  row: 0x10c6d9490  session: 0x10cb6c490  ins_upd_dlt: ins, initial: ins - 2026-11-19 17:41:42,182 - logic_logger - INFO
..Order[None] {server aggregate_defaults: amount_total } id: None, notes: behave test, customer_id: 19, CreatedOn: 2026-11-19, date_shipped: None, amount_total: 0, CreatedOnDay: 2026-11-19  row: 0x10c6d9490  session: 0x10cb6c490  ins_upd_dlt: ins, initial: ins - 2026-11-19 17:41:42,182 - logic_logger - INFO
....DailyFlow[2026-11-19] {Update - Adjusting daily_flow: order_count} day: 2026-11-19, order_count:  [8-->] 9, order_amount: 1860.00, message_received: 1, message_processed: 1, message_failed: 0, message_stuck: 0, request_received: 11, request_processed: 8, request_failed: 3, request_stuck: 0  row: 0x10c615bd0  session: 0x10cb6c490  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:42,183 - logic_logger - INFO
....DailyFlow[2026-11-19] {Prune Formula: message_stuck [['message_received', 'message_processed', 'message_failed']]} day: 2026-11-19, order_count:  [8-->] 9, order_amount: 1860.00, message_received: 1, message_processed: 1, message_failed: 0, message_stuck: 0, request_received: 11, request_processed: 8, request_failed: 3, request_stuck: 0  row: 0x10c615bd0  session: 0x10cb6c490  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:42,183 - logic_logger - INFO
....DailyFlow[2026-11-19] {Prune Formula: request_stuck [['request_received', 'request_processed', 'request_failed']]} day: 2026-11-19, order_count:  [8-->] 9, order_amount: 1860.00, message_received: 1, message_processed: 1, message_failed: 0, message_stuck: 0, request_received: 11, request_processed: 8, request_failed: 3, request_stuck: 0  row: 0x10c615bd0  session: 0x10cb6c490  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:42,183 - logic_logger - INFO
..Item[None] {Insert - client} id: None, order_id: None, product_id: 2, quantity: 2, amount: None, unit_price: None  row: 0x10c6d69d0  session: 0x10cb6c490  ins_upd_dlt: ins, initial: ins - 2026-11-19 17:41:42,183 - logic_logger - INFO
..Item[None] {copy_rules for role: product - unit_price} id: None, order_id: None, product_id: 2, quantity: 2, amount: None, unit_price: 90.0000000000  row: 0x10c6d69d0  session: 0x10cb6c490  ins_upd_dlt: ins, initial: ins - 2026-11-19 17:41:42,183 - logic_logger - INFO
..Item[None] {Formula amount} id: None, order_id: None, product_id: 2, quantity: 2, amount: 180.0000000000, unit_price: 90.0000000000  row: 0x10c6d69d0  session: 0x10cb6c490  ins_upd_dlt: ins, initial: ins - 2026-11-19 17:41:42,183 - logic_logger - INFO
....Order[None] {Update - Adjusting order: amount_total} id: None, notes: behave test, customer_id: 19, CreatedOn: 2026-11-19, date_shipped: None, amount_total:  [0-->] 180.0000000000, CreatedOnDay: 2026-11-19  row: 0x10c6d9490  session: 0x10cb6c490  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:42,183 - logic_logger - INFO
......DailyFlow[2026-11-19] {Update - Adjusting daily_flow: order_amount} day: 2026-11-19, order_count: 9, order_amount:  [1860.00-->] 2040.0000000000, message_received: 1, message_processed: 1, message_failed: 0, message_stuck: 0, request_received: 11, request_processed: 8, request_failed: 3, request_stuck: 0  row: 0x10c615bd0  session: 0x10cb6c490  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:42,183 - logic_logger - INFO
......DailyFlow[2026-11-19] {Prune Formula: message_stuck [['message_received', 'message_processed', 'message_failed']]} day: 2026-11-19, order_count: 9, order_amount:  [1860.00-->] 2040.0000000000, message_received: 1, message_processed: 1, message_failed: 0, message_stuck: 0, request_received: 11, request_processed: 8, request_failed: 3, request_stuck: 0  row: 0x10c615bd0  session: 0x10cb6c490  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:42,183 - logic_logger - INFO
......DailyFlow[2026-11-19] {Prune Formula: request_stuck [['request_received', 'request_processed', 'request_failed']]} day: 2026-11-19, order_count: 9, order_amount:  [1860.00-->] 2040.0000000000, message_received: 1, message_processed: 1, message_failed: 0, message_stuck: 0, request_received: 11, request_processed: 8, request_failed: 3, request_stuck: 0  row: 0x10c615bd0  session: 0x10cb6c490  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:42,183 - logic_logger - INFO
......Customer[19] {Update - Adjusting customer: balance} id: 19, name: Gus 1795138902174, balance:  [0E-10-->] 180.0000000000, credit_limit: 5000.0000000000, email: None, email_opt_out: None  row: 0x10c5e8950  session: 0x10cb6c490  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:42,183 - logic_logger - INFO
..Item[None] {Insert - client} id: None, order_id: None, product_id: None, quantity: 1, amount: None, unit_price: None  row: 0x10cb4f150  session: 0x10cb6c490  ins_upd_dlt: ins, initial: ins - 2026-11-19 17:41:42,183 - logic_logger - INFO
..Item[None] {copy_rules for role: product - unit_price} id: None, order_id: None, product_id: None, quantity: 1, amount: None, unit_price: 150.0000000000  row: 0x10cb4f150  session: 0x10cb6c490  ins_upd_dlt: ins, initial: ins - 2026-11-19 17:41:42,183 - logic_logger - INFO
..Item[None] {Formula amount} id: None, order_id: None, product_id: None, quantity: 1, amount: 150.0000000000, unit_price: 150.0000000000  row: 0x10cb4f150  session: 0x10cb6c490  ins_upd_dlt: ins, initial: ins - 2026-11-19 17:41:42,183 - logic_logger - INFO
....Order[None] {Update - Adjusting order: amount_total} id: None, notes: behave test, customer_id: 19, CreatedOn: 2026-11-19, date_shipped: None, amount_total:  [180.0000000000-->] 330.0000000000, CreatedOnDay: 2026-11-19  row: 0x10c6d9490  session: 0x10cb6c490  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:42,183 - logic_logger - INFO
......DailyFlow[2026-11-19] {Update - Adjusting daily_flow: order_amount} day: 2026-11-19, order_count: 9, order_amount:  [2040.0000000000-->] 2190.0000000000, message_received: 1, message_processed: 1, message_failed: 0, message_stuck: 0, request_received: 11, request_processed: 8, request_failed: 3, request_stuck: 0  row: 0x10c615bd0  session: 0x10cb6c490  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:42,183 - logic_logger - INFO
......DailyFlow[2026-11-19] {Prune Formula: message_stuck [['message_received', 'message_processed', 'message_failed']]} day: 2026-11-19, order_count: 9, order_amount:  [2040.0000000000-->] 2190.0000000000, message_received: 1, message_processed: 1, message_failed: 0, message_stuck: 0, request_received: 11, request_processed: 8, request_failed: 3, request_stuck: 0  row: 0x10c615bd0  session: 0x10cb6c490  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:42,183 - logic_logger - INFO
......DailyFlow[2026-11-19] {Prune Formula: request_stuck [['request_received', 'request_processed', 'request_failed']]} day: 2026-11-19, order_count: 9, order_amount:  [2040.0000000000-->] 2190.0000000000, message_received: 1, message_processed: 1, message_failed: 0, message_stuck: 0, request_received: 11, request_processed: 8, request_failed: 3, request_stuck: 0  row: 0x10c615bd0  session: 0x10cb6c490  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:42,184 - logic_logger - INFO
......Customer[19] {Update - Adjusting customer: balance} id: 19, name: Gus 1795138902174, balance:  [180.0000000000-->] 330.0000000000, credit_limit: 5000.0000000000, email: None, email_opt_out: None  row: 0x10c5e8950  session: 0x10cb6c490  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:42,184 - logic_logger - INFO
Logic Phase:		COMMIT LOGIC		(session=0x10cb6c490)   										 - 2026-11-19 17:41:42,184 - logic_logger - INFO
Logic Phase:		AFTER_FLUSH LOGIC	(session=0x10cb6c490)   										 - 2026-11-19 17:41:42,184 - logic_logger - INFO
..Order[166] {AfterFlush Event} id: 166, notes: behave test, customer_id: 19, CreatedOn: 2026-11-19, date_shipped: None, amount_total: 330.0000000000, CreatedOnDay: 2026-11-19  row: 0x10c6d9490  session: 0x10cb6c490  ins_upd_dlt: ins, initial: ins - 2026-11-19 17:41:42,184 - logic_logger - INFO


Logic Phase:		ROW LOGIC		(session=0x10c51df20) (sqlalchemy before_flush)			 - 2026-11-19 17:41:42,193 - logic_logger - INFO
..Item[314] {Delete - client} id: 314, order_id: 166, product_id: 1, quantity: 1, amount: 150.0000000000, unit_price: 150.0000000000  row: 0x10cb4eb50  session: 0x10c51df20  ins_upd_dlt: dlt, initial: dlt - 2026-11-19 17:41:42,193 - logic_logger - INFO
....Order[166] {Update - Adjusting order: amount_total} id: 166, notes: behave test, customer_id: 19, CreatedOn: 2026-11-19, date_shipped: None, amount_total:  [330.0000000000-->] 180.0000000000, CreatedOnDay: 2026-11-19  row: 0x10c6da600  session: 0x10c51df20  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:42,193 - logic_logger - INFO
......DailyFlow[2026-11-19] {Update - Adjusting daily_flow: order_amount} day: 2026-11-19, order_count: 9, order_amount:  [2190.00-->] 2040.0000000000, message_received: 1, message_processed: 1, message_failed: 0, message_stuck: 0, request_received: 11, request_processed: 8, request_failed: 3, request_stuck: 0  row: 0x10c615bd0  session: 0x10c51df20  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:42,193 - logic_logger - INFO
......DailyFlow[2026-11-19] {Prune Formula: message_stuck [['message_received', 'message_processed', 'message_failed']]} day: 2026-11-19, order_count: 9, order_amount:  [2190.00-->] 2040.0000000000, message_received: 1, message_processed: 1, message_failed: 0, message_stuck: 0, request_received: 11, request_processed: 8, request_failed: 3, request_stuck: 0  row: 0x10c615bd0  session: 0x10c51df20  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:42,193 - logic_logger - INFO
......DailyFlow[2026-11-19] {Prune Formula: request_stuck [['request_received', 'request_processed', 'request_failed']]} day: 2026-11-19, order_count: 9, order_amount:  [2190.00-->] 2040.0000000000, message_received: 1, message_processed: 1, message_failed: 0, message_stuck: 0, request_received: 11, request_processed: 8, request_failed: 3, request_stuck: 0  row: 0x10c615bd0  session: 0x10c51df20  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:42,193 - logic_logger - INFO
......Customer[19] {Update - Adjusting customer: balance} id: 19, name: Gus 1795138902174, balance:  [330.0000000000-->] 180.0000000000, credit_limit: 5000.0000000000, email: None, email_opt_out: None  row: 0x10c6d4cd0  session: 0x10c51df20  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:42,194 - logic_logger - INFO
Logic Phase:		COMMIT LOGIC		(session=0x10c51df20)   										 - 2026-11-19 17:41:42,194 - logic_logger - INFO
Logic Phase:		AFTER_FLUSH LOGIC	(session=0x10c51df20)   										 - 2026-11-19 17:41:42,194 - logic_logger - INFO
....Order[166] {AfterFlush Event} id: 166, notes: behave test, customer_id: 19, CreatedOn: 2026-11-19, date_shipped: None, amount_total:  [330.0000000000-->] 180.0000000000, CreatedOnDay: 2026-11-19  row: 0x10c6da600  session: 0x10c51df20  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:42,194 - logic_logger - INFO

```
</details>

&nbsp;
&nbsp;

#### Scenario: Order Deleted Leaves Balance ✅ (0.03 s)
&emsp;  Scenario: Order Deleted Leaves Balance  
&emsp;&emsp;    Given Customer "Hank" with credit limit 5000  
&emsp;&emsp;    And Order is created for "Hank" with 2 Widget  
&emsp;&emsp;    When Order is deleted  
&emsp;&emsp;    Then Customer balance should be 0  

<details markdown>
<summary>Rules exercised and logic log (3 transactions)</summary>


&nbsp;
&nbsp;


**Rules Used** in Scenario: Order Deleted Leaves Balance
```
  DailyFlow  
    1. Derive DailyFlow.request_processed as Count(OrderB2bRequest Where Rule.count(derive=models.DailyFlow.request_processed, as_count_of=models.OrderB2bRequest, where=lambda row: row.is_processed == True, insert_parent=True), insert_parent)  
    2. Derive DailyFlow.request_failed as Count(OrderB2bRequest Where Rule.count(derive=models.DailyFlow.request_failed, as_count_of=models.OrderB2bRequest, where=lambda row: row.error_text is not None, insert_parent=True), insert_parent)  
    3. Derive DailyFlow.request_stuck as Formula (2): Rule.formula(derive=models.DailyFlow.request_stuc [...]  
    4. Derive DailyFlow.request_received as Count(OrderB2bRequest Where  - None, insert_parent)  
    5. Derive DailyFlow.order_amount as Sum(Order.amount_total Where  - None, insert_parent)  
    6. Derive DailyFlow.order_count as Count(Order Where  - None, insert_parent)  
  Customer  
    7. Derive Customer.balance as Sum(Order.amount_total Where Rule.sum(derive=models.Customer.balance, as_sum_of=models.Order.amount_total, where=lambda row: row.date_shipped is None))  
  Item  
    8. Derive Item.amount as Formula (1): Rule.formula(derive=models.Item.amount, as_expres [...]  
    9. Derive Item.unit_price as Copy(product.unit_price)  
  Order  
    10. RowEvent Order._send_order_to_shipping()  
    11. Derive Order.amount_total as Sum(Item.amount Where  - None)  
```
**Logic Log** in Scenario: Order Deleted Leaves Balance (3 transactions)
```
Logic Phase:		ROW LOGIC		(session=0x10c51ff00) (sqlalchemy before_flush)			 - 2026-11-19 17:41:42,205 - logic_logger - INFO
..OrderB2bRequest[None] {Insert - client} id: None, CreatedOn: None, CreatedOnDay: None, payload: {"Account": "Hank 1795138902200", "Notes": "behave test", "Items": [{"Name": "Widget", "QuantityOrdered": 2}]}, is_processed: False, error_text: None  row: 0x10c55bf50  session: 0x10c51ff00  ins_upd_dlt: ins, initial: ins - 2026-11-19 17:41:42,205 - logic_logger - INFO
..OrderB2bRequest[None] {early_row_event_all_classes - handle_all did stamping} id: None, CreatedOn: 2026-11-19 17:41:42.205272, CreatedOnDay: 2026-11-19, payload: {"Account": "Hank 1795138902200", "Notes": "behave test", "Items": [{"Name": "Widget", "QuantityOrdered": 2}]}, is_processed: False, error_text: None  row: 0x10c55bf50  session: 0x10c51ff00  ins_upd_dlt: ins, initial: ins - 2026-11-19 17:41:42,205 - logic_logger - INFO
....DailyFlow[2026-11-19] {Update - Adjusting daily_flow: request_received} day: 2026-11-19, order_count: 9, order_amount: 2040.00, message_received: 1, message_processed: 1, message_failed: 0, message_stuck: 0, request_received:  [11-->] 12, request_processed: 8, request_failed: 3, request_stuck: 0  row: 0x10c615de0  session: 0x10c51ff00  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:42,205 - logic_logger - INFO
....DailyFlow[2026-11-19] {Prune Formula: message_stuck [['message_received', 'message_processed', 'message_failed']]} day: 2026-11-19, order_count: 9, order_amount: 2040.00, message_received: 1, message_processed: 1, message_failed: 0, message_stuck: 0, request_received:  [11-->] 12, request_processed: 8, request_failed: 3, request_stuck: 0  row: 0x10c615de0  session: 0x10c51ff00  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:42,205 - logic_logger - INFO
....DailyFlow[2026-11-19] {Formula request_stuck} day: 2026-11-19, order_count: 9, order_amount: 2040.00, message_received: 1, message_processed: 1, message_failed: 0, message_stuck: 0, request_received:  [11-->] 12, request_processed: 8, request_failed: 3, request_stuck:  [0-->] 1  row: 0x10c615de0  session: 0x10c51ff00  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:42,205 - logic_logger - INFO
Logic Phase:		COMMIT LOGIC		(session=0x10c51ff00)   										 - 2026-11-19 17:41:42,205 - logic_logger - INFO
Logic Phase:		AFTER_FLUSH LOGIC	(session=0x10c51ff00)   										 - 2026-11-19 17:41:42,206 - logic_logger - INFO


Logic Phase:		ROW LOGIC		(session=0x10c51ff00) (sqlalchemy before_flush)			 - 2026-11-19 17:41:42,208 - logic_logger - INFO
..Product[2] {Update - client} id: 2, name: Widget, count_suppliers: 0, unit_price: 90.0000000000  row: 0x10cb26e40  session: 0x10c51ff00  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:42,208 - logic_logger - INFO
..OrderB2bRequest[72] {Update - client} id: 72, CreatedOn: 2026-11-19 17:41:42.205272, CreatedOnDay: 2026-11-19, payload: {"Account": "Hank 1795138902200", "Notes": "behave test", "Items": [{"Name": "Widget", "QuantityOrdered": 2}]}, is_processed:  [False-->] True, error_text: None  row: 0x10c55bf50  session: 0x10c51ff00  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:42,208 - logic_logger - INFO
....DailyFlow[2026-11-19] {Update - Adjusting daily_flow: request_processed} day: 2026-11-19, order_count: 9, order_amount: 2040.00, message_received: 1, message_processed: 1, message_failed: 0, message_stuck: 0, request_received: 12, request_processed:  [8-->] 9, request_failed: 3, request_stuck: 1  row: 0x10c615de0  session: 0x10c51ff00  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:42,208 - logic_logger - INFO
....DailyFlow[2026-11-19] {Prune Formula: message_stuck [['message_received', 'message_processed', 'message_failed']]} day: 2026-11-19, order_count: 9, order_amount: 2040.00, message_received: 1, message_processed: 1, message_failed: 0, message_stuck: 0, request_received: 12, request_processed:  [8-->] 9, request_failed: 3, request_stuck: 1  row: 0x10c615de0  session: 0x10c51ff00  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:42,208 - logic_logger - INFO
....DailyFlow[2026-11-19] {Formula request_stuck} day: 2026-11-19, order_count: 9, order_amount: 2040.00, message_received: 1, message_processed: 1, message_failed: 0, message_stuck: 0, request_received: 12, request_processed:  [8-->] 9, request_failed: 3, request_stuck:  [1-->] 0  row: 0x10c615de0  session: 0x10c51ff00  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:42,208 - logic_logger - INFO
..Order[None] {Insert - client} id: None, notes: behave test, customer_id: 20, CreatedOn: None, date_shipped: None, amount_total: None, CreatedOnDay: None  row: 0x10c6daa80  session: 0x10c51ff00  ins_upd_dlt: ins, initial: ins - 2026-11-19 17:41:42,208 - logic_logger - INFO
..Order[None] {early_row_event_all_classes - handle_all did stamping} id: None, notes: behave test, customer_id: 20, CreatedOn: 2026-11-19, date_shipped: None, amount_total: None, CreatedOnDay: 2026-11-19  row: 0x10c6daa80  session: 0x10c51ff00  ins_upd_dlt: ins, initial: ins - 2026-11-19 17:41:42,208 - logic_logger - INFO
..Order[None] {server aggregate_defaults: amount_total } id: None, notes: behave test, customer_id: 20, CreatedOn: 2026-11-19, date_shipped: None, amount_total: 0, CreatedOnDay: 2026-11-19  row: 0x10c6daa80  session: 0x10c51ff00  ins_upd_dlt: ins, initial: ins - 2026-11-19 17:41:42,208 - logic_logger - INFO
....DailyFlow[2026-11-19] {Update - Adjusting daily_flow: order_count} day: 2026-11-19, order_count:  [9-->] 10, order_amount: 2040.00, message_received: 1, message_processed: 1, message_failed: 0, message_stuck: 0, request_received: 12, request_processed: 9, request_failed: 3, request_stuck: 0  row: 0x10c615de0  session: 0x10c51ff00  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:42,208 - logic_logger - INFO
....DailyFlow[2026-11-19] {Prune Formula: message_stuck [['message_received', 'message_processed', 'message_failed']]} day: 2026-11-19, order_count:  [9-->] 10, order_amount: 2040.00, message_received: 1, message_processed: 1, message_failed: 0, message_stuck: 0, request_received: 12, request_processed: 9, request_failed: 3, request_stuck: 0  row: 0x10c615de0  session: 0x10c51ff00  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:42,209 - logic_logger - INFO
....DailyFlow[2026-11-19] {Prune Formula: request_stuck [['request_received', 'request_processed', 'request_failed']]} day: 2026-11-19, order_count:  [9-->] 10, order_amount: 2040.00, message_received: 1, message_processed: 1, message_failed: 0, message_stuck: 0, request_received: 12, request_processed: 9, request_failed: 3, request_stuck: 0  row: 0x10c615de0  session: 0x10c51ff00  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:42,209 - logic_logger - INFO
..Item[None] {Insert - client} id: None, order_id: None, product_id: None, quantity: 2, amount: None, unit_price: None  row: 0x10c5eb8d0  session: 0x10c51ff00  ins_upd_dlt: ins, initial: ins - 2026-11-19 17:41:42,209 - logic_logger - INFO
..Item[None] {copy_rules for role: product - unit_price} id: None, order_id: None, product_id: None, quantity: 2, amount: None, unit_price: 90.0000000000  row: 0x10c5eb8d0  session: 0x10c51ff00  ins_upd_dlt: ins, initial: ins - 2026-11-19 17:41:42,209 - logic_logger - INFO
..Item[None] {Formula amount} id: None, order_id: None, product_id: None, quantity: 2, amount: 180.0000000000, unit_price: 90.0000000000  row: 0x10c5eb8d0  session: 0x10c51ff00  ins_upd_dlt: ins, initial: ins - 2026-11-19 17:41:42,209 - logic_logger - INFO
....Order[None] {Update - Adjusting order: amount_total} id: None, notes: behave test, customer_id: 20, CreatedOn: 2026-11-19, date_shipped: None, amount_total:  [0-->] 180.0000000000, CreatedOnDay: 2026-11-19  row: 0x10c6daa80  session: 0x10c51ff00  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:42,209 - logic_logger - INFO
......DailyFlow[2026-11-19] {Update - Adjusting daily_flow: order_amount} day: 2026-11-19, order_count: 10, order_amount:  [2040.00-->] 2220.0000000000, message_received: 1, message_processed: 1, message_failed: 0, message_stuck: 0, request_received: 12, request_processed: 9, request_failed: 3, request_stuck: 0  row: 0x10c615de0  session: 0x10c51ff00  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:42,209 - logic_logger - INFO
......DailyFlow[2026-11-19] {Prune Formula: message_stuck [['message_received', 'message_processed', 'message_failed']]} day: 2026-11-19, order_count: 10, order_amount:  [2040.00-->] 2220.0000000000, message_received: 1, message_processed: 1, message_failed: 0, message_stuck: 0, request_received: 12, request_processed: 9, request_failed: 3, request_stuck: 0  row: 0x10c615de0  session: 0x10c51ff00  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:42,209 - logic_logger - INFO
......DailyFlow[2026-11-19] {Prune Formula: request_stuck [['request_received', 'request_processed', 'request_failed']]} day: 2026-11-19, order_count: 10, order_amount:  [2040.00-->] 2220.0000000000, message_received: 1, message_processed: 1, message_failed: 0, message_stuck: 0, request_received: 12, request_processed: 9, request_failed: 3, request_stuck: 0  row: 0x10c615de0  session: 0x10c51ff00  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:42,209 - logic_logger - INFO
......Customer[20] {Update - Adjusting customer: balance} id: 20, name: Hank 1795138902200, balance:  [0E-10-->] 180.0000000000, credit_limit: 5000.0000000000, email: None, email_opt_out: None  row: 0x10c5d1650  session: 0x10c51ff00  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:42,209 - logic_logger - INFO
Logic Phase:		COMMIT LOGIC		(session=0x10c51ff00)   										 - 2026-11-19 17:41:42,209 - logic_logger - INFO
Logic Phase:		AFTER_FLUSH LOGIC	(session=0x10c51ff00)   										 - 2026-11-19 17:41:42,210 - logic_logger - INFO
..Order[167] {AfterFlush Event} id: 167, notes: behave test, customer_id: 20, CreatedOn: 2026-11-19, date_shipped: None, amount_total: 180.0000000000, CreatedOnDay: 2026-11-19  row: 0x10c6daa80  session: 0x10c51ff00  ins_upd_dlt: ins, initial: ins - 2026-11-19 17:41:42,210 - logic_logger - INFO


Logic Phase:		ROW LOGIC		(session=0x10cb6c270) (sqlalchemy before_flush)			 - 2026-11-19 17:41:42,213 - logic_logger - INFO
..Order[167] {Delete - client} id: 167, notes: behave test, customer_id: 20, CreatedOn: 2026-11-19, date_shipped: None, amount_total: 180.0000000000, CreatedOnDay: 2026-11-19  row: 0x10c6db0b0  session: 0x10cb6c270  ins_upd_dlt: dlt, initial: dlt - 2026-11-19 17:41:42,213 - logic_logger - INFO
....DailyFlow[2026-11-19] {Update - Adjusting daily_flow: order_count, order_amount} day: 2026-11-19, order_count:  [10-->] 9, order_amount:  [2220.00-->] 2040.0000000000, message_received: 1, message_processed: 1, message_failed: 0, message_stuck: 0, request_received: 12, request_processed: 9, request_failed: 3, request_stuck: 0  row: 0x10c615c80  session: 0x10cb6c270  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:42,213 - logic_logger - INFO
....DailyFlow[2026-11-19] {Prune Formula: message_stuck [['message_received', 'message_processed', 'message_failed']]} day: 2026-11-19, order_count:  [10-->] 9, order_amount:  [2220.00-->] 2040.0000000000, message_received: 1, message_processed: 1, message_failed: 0, message_stuck: 0, request_received: 12, request_processed: 9, request_failed: 3, request_stuck: 0  row: 0x10c615c80  session: 0x10cb6c270  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:42,214 - logic_logger - INFO
....DailyFlow[2026-11-19] {Prune Formula: request_stuck [['request_received', 'request_processed', 'request_failed']]} day: 2026-11-19, order_count:  [10-->] 9, order_amount:  [2220.00-->] 2040.0000000000, message_received: 1, message_processed: 1, message_failed: 0, message_stuck: 0, request_received: 12, request_processed: 9, request_failed: 3, request_stuck: 0  row: 0x10c615c80  session: 0x10cb6c270  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:42,214 - logic_logger - INFO
....Customer[20] {Update - Adjusting customer: balance} id: 20, name: Hank 1795138902200, balance:  [180.0000000000-->] 0E-10, credit_limit: 5000.0000000000, email: None, email_opt_out: None  row: 0x10cb818d0  session: 0x10cb6c270  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:42,214 - logic_logger - INFO
Logic Phase:		COMMIT LOGIC		(session=0x10cb6c270)   										 - 2026-11-19 17:41:42,214 - logic_logger - INFO
Logic Phase:		AFTER_FLUSH LOGIC	(session=0x10cb6c270)   										 - 2026-11-19 17:41:42,215 - logic_logger - INFO
..Order[167] {AfterFlush Event} id: 167, notes: behave test, customer_id: 20, CreatedOn: 2026-11-19, date_shipped: None, amount_total: 180.0000000000, CreatedOnDay: 2026-11-19  row: 0x10c6db0b0  session: 0x10cb6c270  ins_upd_dlt: dlt, initial: dlt - 2026-11-19 17:41:42,215 - logic_logger - INFO

```
</details>

&nbsp;
&nbsp;

#### Scenario: Order Moved To Another Customer ✅ (0.02 s)
&emsp;  Scenario: Order Moved To Another Customer  
&emsp;&emsp;    Given Customer "Ivy" with credit limit 5000  
&emsp;&emsp;    And Customer "Jack" with credit limit 5000  
&emsp;&emsp;    And Order is created for "Ivy" with 2 Widget  
&emsp;&emsp;    When Order is moved to Customer "Jack"  
&emsp;&emsp;    Then Customer "Ivy" balance should be 0  
&emsp;&emsp;    And Customer "Jack" balance should be 180  

<details markdown>
<summary>Rules exercised and logic log (3 transactions)</summary>


&nbsp;
&nbsp;


**Rules Used** in Scenario: Order Moved To Another Customer
```
  DailyFlow  
    1. Derive DailyFlow.request_processed as Count(OrderB2bRequest Where Rule.count(derive=models.DailyFlow.request_processed, as_count_of=models.OrderB2bRequest, where=lambda row: row.is_processed == True, insert_parent=True), insert_parent)  
    2. Derive DailyFlow.request_failed as Count(OrderB2bRequest Where Rule.count(derive=models.DailyFlow.request_failed, as_count_of=models.OrderB2bRequest, where=lambda row: row.error_text is not None, insert_parent=True), insert_parent)  
    3. Derive DailyFlow.request_stuck as Formula (2): Rule.formula(derive=models.DailyFlow.request_stuc [...]  
    4. Derive DailyFlow.request_received as Count(OrderB2bRequest Where  - None, insert_parent)  
    5. Derive DailyFlow.order_amount as Sum(Order.amount_total Where  - None, insert_parent)  
    6. Derive DailyFlow.order_count as Count(Order Where  - None, insert_parent)  
  Customer  
    7. Derive Customer.balance as Sum(Order.amount_total Where Rule.sum(derive=models.Customer.balance, as_sum_of=models.Order.amount_total, where=lambda row: row.date_shipped is None))  
  Item  
    8. Derive Item.amount as Formula (1): Rule.formula(derive=models.Item.amount, as_expres [...]  
    9. Derive Item.unit_price as Copy(product.unit_price)  
  Order  
    10. RowEvent Order._send_order_to_shipping()  
    11. Derive Order.amount_total as Sum(Item.amount Where  - None)  
```
**Logic Log** in Scenario: Order Moved To Another Customer (3 transactions)
```
Logic Phase:		ROW LOGIC		(session=0x10cb6c8d0) (sqlalchemy before_flush)			 - 2026-11-19 17:41:42,232 - logic_logger - INFO
..OrderB2bRequest[None] {Insert - client} id: None, CreatedOn: None, CreatedOnDay: None, payload: {"Account": "Ivy 1795138902226", "Notes": "behave test", "Items": [{"Name": "Widget", "QuantityOrdered": 2}]}, is_processed: False, error_text: None  row: 0x10cb4efd0  session: 0x10cb6c8d0  ins_upd_dlt: ins, initial: ins - 2026-11-19 17:41:42,232 - logic_logger - INFO
..OrderB2bRequest[None] {early_row_event_all_classes - handle_all did stamping} id: None, CreatedOn: 2026-11-19 17:41:42.232976, CreatedOnDay: 2026-11-19, payload: {"Account": "Ivy 1795138902226", "Notes": "behave test", "Items": [{"Name": "Widget", "QuantityOrdered": 2}]}, is_processed: False, error_text: None  row: 0x10cb4efd0  session: 0x10cb6c8d0  ins_upd_dlt: ins, initial: ins - 2026-11-19 17:41:42,233 - logic_logger - INFO
....DailyFlow[2026-11-19] {Update - Adjusting daily_flow: request_received} day: 2026-11-19, order_count: 9, order_amount: 2040.00, message_received: 1, message_processed: 1, message_failed: 0, message_stuck: 0, request_received:  [12-->] 13, request_processed: 9, request_failed: 3, request_stuck: 0  row: 0x10c615a70  session: 0x10cb6c8d0  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:42,233 - logic_logger - INFO
....DailyFlow[2026-11-19] {Prune Formula: message_stuck [['message_received', 'message_processed', 'message_failed']]} day: 2026-11-19, order_count: 9, order_amount: 2040.00, message_received: 1, message_processed: 1, message_failed: 0, message_stuck: 0, request_received:  [12-->] 13, request_processed: 9, request_failed: 3, request_stuck: 0  row: 0x10c615a70  session: 0x10cb6c8d0  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:42,233 - logic_logger - INFO
....DailyFlow[2026-11-19] {Formula request_stuck} day: 2026-11-19, order_count: 9, order_amount: 2040.00, message_received: 1, message_processed: 1, message_failed: 0, message_stuck: 0, request_received:  [12-->] 13, request_processed: 9, request_failed: 3, request_stuck:  [0-->] 1  row: 0x10c615a70  session: 0x10cb6c8d0  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:42,233 - logic_logger - INFO
Logic Phase:		COMMIT LOGIC		(session=0x10cb6c8d0)   										 - 2026-11-19 17:41:42,233 - logic_logger - INFO
Logic Phase:		AFTER_FLUSH LOGIC	(session=0x10cb6c8d0)   										 - 2026-11-19 17:41:42,233 - logic_logger - INFO


Logic Phase:		ROW LOGIC		(session=0x10cb6c8d0) (sqlalchemy before_flush)			 - 2026-11-19 17:41:42,235 - logic_logger - INFO
..OrderB2bRequest[73] {Update - client} id: 73, CreatedOn: 2026-11-19 17:41:42.232976, CreatedOnDay: 2026-11-19, payload: {"Account": "Ivy 1795138902226", "Notes": "behave test", "Items": [{"Name": "Widget", "QuantityOrdered": 2}]}, is_processed:  [False-->] True, error_text: None  row: 0x10cb4efd0  session: 0x10cb6c8d0  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:42,235 - logic_logger - INFO
....DailyFlow[2026-11-19] {Update - Adjusting daily_flow: request_processed} day: 2026-11-19, order_count: 9, order_amount: 2040.00, message_received: 1, message_processed: 1, message_failed: 0, message_stuck: 0, request_received: 13, request_processed:  [9-->] 10, request_failed: 3, request_stuck: 1  row: 0x10c615a70  session: 0x10cb6c8d0  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:42,235 - logic_logger - INFO
....DailyFlow[2026-11-19] {Prune Formula: message_stuck [['message_received', 'message_processed', 'message_failed']]} day: 2026-11-19, order_count: 9, order_amount: 2040.00, message_received: 1, message_processed: 1, message_failed: 0, message_stuck: 0, request_received: 13, request_processed:  [9-->] 10, request_failed: 3, request_stuck: 1  row: 0x10c615a70  session: 0x10cb6c8d0  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:42,235 - logic_logger - INFO
....DailyFlow[2026-11-19] {Formula request_stuck} day: 2026-11-19, order_count: 9, order_amount: 2040.00, message_received: 1, message_processed: 1, message_failed: 0, message_stuck: 0, request_received: 13, request_processed:  [9-->] 10, request_failed: 3, request_stuck:  [1-->] 0  row: 0x10c615a70  session: 0x10cb6c8d0  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:42,235 - logic_logger - INFO
..Product[2] {Update - client} id: 2, name: Widget, count_suppliers: 0, unit_price: 90.0000000000  row: 0x10cb26f90  session: 0x10cb6c8d0  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:42,235 - logic_logger - INFO
..Order[None] {Insert - client} id: None, notes: behave test, customer_id: 21, CreatedOn: None, date_shipped: None, amount_total: None, CreatedOnDay: None  row: 0x10c6db2f0  session: 0x10cb6c8d0  ins_upd_dlt: ins, initial: ins - 2026-11-19 17:41:42,236 - logic_logger - INFO
..Order[None] {early_row_event_all_classes - handle_all did stamping} id: None, notes: behave test, customer_id: 21, CreatedOn: 2026-11-19, date_shipped: None, amount_total: None, CreatedOnDay: 2026-11-19  row: 0x10c6db2f0  session: 0x10cb6c8d0  ins_upd_dlt: ins, initial: ins - 2026-11-19 17:41:42,236 - logic_logger - INFO
..Order[None] {server aggregate_defaults: amount_total } id: None, notes: behave test, customer_id: 21, CreatedOn: 2026-11-19, date_shipped: None, amount_total: 0, CreatedOnDay: 2026-11-19  row: 0x10c6db2f0  session: 0x10cb6c8d0  ins_upd_dlt: ins, initial: ins - 2026-11-19 17:41:42,236 - logic_logger - INFO
....DailyFlow[2026-11-19] {Update - Adjusting daily_flow: order_count} day: 2026-11-19, order_count:  [9-->] 10, order_amount: 2040.00, message_received: 1, message_processed: 1, message_failed: 0, message_stuck: 0, request_received: 13, request_processed: 10, request_failed: 3, request_stuck: 0  row: 0x10c615a70  session: 0x10cb6c8d0  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:42,236 - logic_logger - INFO
....DailyFlow[2026-11-19] {Prune Formula: message_stuck [['message_received', 'message_processed', 'message_failed']]} day: 2026-11-19, order_count:  [9-->] 10, order_amount: 2040.00, message_received: 1, message_processed: 1, message_failed: 0, message_stuck: 0, request_received: 13, request_processed: 10, request_failed: 3, request_stuck: 0  row: 0x10c615a70  session: 0x10cb6c8d0  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:42,236 - logic_logger - INFO
....DailyFlow[2026-11-19] {Prune Formula: request_stuck [['request_received', 'request_processed', 'request_failed']]} day: 2026-11-19, order_count:  [9-->] 10, order_amount: 2040.00, message_received: 1, message_processed: 1, message_failed: 0, message_stuck: 0, request_received: 13, request_processed: 10, request_failed: 3, request_stuck: 0  row: 0x10c615a70  session: 0x10cb6c8d0  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:42,236 - logic_logger - INFO
..Item[None] {Insert - client} id: None, order_id: None, product_id: None, quantity: 2, amount: None, unit_price: None  row: 0x10cb4f0d0  session: 0x10cb6c8d0  ins_upd_dlt: ins, initial: ins - 2026-11-19 17:41:42,236 - logic_logger - INFO
..Item[None] {copy_rules for role: product - unit_price} id: None, order_id: None, product_id: None, quantity: 2, amount: None, unit_price: 90.0000000000  row: 0x10cb4f0d0  session: 0x10cb6c8d0  ins_upd_dlt: ins, initial: ins - 2026-11-19 17:41:42,236 - logic_logger - INFO
..Item[None] {Formula amount} id: None, order_id: None, product_id: None, quantity: 2, amount: 180.0000000000, unit_price: 90.0000000000  row: 0x10cb4f0d0  session: 0x10cb6c8d0  ins_upd_dlt: ins, initial: ins - 2026-11-19 17:41:42,236 - logic_logger - INFO
....Order[None] {Update - Adjusting order: amount_total} id: None, notes: behave test, customer_id: 21, CreatedOn: 2026-11-19, date_shipped: None, amount_total:  [0-->] 180.0000000000, CreatedOnDay: 2026-11-19  row: 0x10c6db2f0  session: 0x10cb6c8d0  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:42,236 - logic_logger - INFO
......DailyFlow[2026-11-19] {Update - Adjusting daily_flow: order_amount} day: 2026-11-19, order_count: 10, order_amount:  [2040.00-->] 2220.0000000000, message_received: 1, message_processed: 1, message_failed: 0, message_stuck: 0, request_received: 13, request_processed: 10, request_failed: 3, request_stuck: 0  row: 0x10c615a70  session: 0x10cb6c8d0  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:42,236 - logic_logger - INFO
......DailyFlow[2026-11-19] {Prune Formula: message_stuck [['message_received', 'message_processed', 'message_failed']]} day: 2026-11-19, order_count: 10, order_amount:  [2040.00-->] 2220.0000000000, message_received: 1, message_processed: 1, message_failed: 0, message_stuck: 0, request_received: 13, request_processed: 10, request_failed: 3, request_stuck: 0  row: 0x10c615a70  session: 0x10cb6c8d0  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:42,236 - logic_logger - INFO
......DailyFlow[2026-11-19] {Prune Formula: request_stuck [['request_received', 'request_processed', 'request_failed']]} day: 2026-11-19, order_count: 10, order_amount:  [2040.00-->] 2220.0000000000, message_received: 1, message_processed: 1, message_failed: 0, message_stuck: 0, request_received: 13, request_processed: 10, request_failed: 3, request_stuck: 0  row: 0x10c615a70  session: 0x10cb6c8d0  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:42,236 - logic_logger - INFO
......Customer[21] {Update - Adjusting customer: balance} id: 21, name: Ivy 1795138902226, balance:  [0E-10-->] 180.0000000000, credit_limit: 5000.0000000000, email: None, email_opt_out: None  row: 0x10c6d6b50  session: 0x10cb6c8d0  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:42,236 - logic_logger - INFO
Logic Phase:		COMMIT LOGIC		(session=0x10cb6c8d0)   										 - 2026-11-19 17:41:42,236 - logic_logger - INFO
Logic Phase:		AFTER_FLUSH LOGIC	(session=0x10cb6c8d0)   										 - 2026-11-19 17:41:42,237 - logic_logger - INFO
..Order[168] {AfterFlush Event} id: 168, notes: behave test, customer_id: 21, CreatedOn: 2026-11-19, date_shipped: None, amount_total: 180.0000000000, CreatedOnDay: 2026-11-19  row: 0x10c6db2f0  session: 0x10cb6c8d0  ins_upd_dlt: ins, initial: ins - 2026-11-19 17:41:42,237 - logic_logger - INFO


Logic Phase:		ROW LOGIC		(session=0x10cb6cc00) (sqlalchemy before_flush)			 - 2026-11-19 17:41:42,239 - logic_logger - INFO
..Order[168] {Update - client} id: 168, notes: behave test, customer_id:  [21-->] 22, CreatedOn: 2026-11-19, date_shipped: None, amount_total: 180.0000000000, CreatedOnDay: 2026-11-19  row: 0x10c6db380  session: 0x10cb6cc00  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:42,240 - logic_logger - INFO
....Customer[22] {Update - Adjusting customer: balance, balance} id: 22, name: Jack 1795138902229, balance:  [0E-10-->] 180.0000000000, credit_limit: 5000.0000000000, email: None, email_opt_out: None  row: 0x10cba3150  session: 0x10cb6cc00  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:42,240 - logic_logger - INFO
....Customer[21] {Update - Adjusting Old customer} id: 21, name: Ivy 1795138902226, balance:  [180.0000000000-->] 0E-10, credit_limit: 5000.0000000000, email: None, email_opt_out: None  row: 0x10cba1550  session: 0x10cb6cc00  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:42,240 - logic_logger - INFO
Logic Phase:		COMMIT LOGIC		(session=0x10cb6cc00)   										 - 2026-11-19 17:41:42,240 - logic_logger - INFO
Logic Phase:		AFTER_FLUSH LOGIC	(session=0x10cb6cc00)   										 - 2026-11-19 17:41:42,241 - logic_logger - INFO
..Order[168] {AfterFlush Event} id: 168, notes: behave test, customer_id:  [21-->] 22, CreatedOn: 2026-11-19, date_shipped: None, amount_total: 180.0000000000, CreatedOnDay: 2026-11-19  row: 0x10c6db380  session: 0x10cb6cc00  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:42,241 - logic_logger - INFO

```
</details>

&nbsp;
&nbsp;

#### Scenario: Item Moved To Another Order ✅ (0.03 s)
&emsp;  Scenario: Item Moved To Another Order  
&emsp;&emsp;    Given Customer "Kim" with credit limit 5000  
&emsp;&emsp;    And Order is created for "Kim" with 2 Widget  
&emsp;&emsp;    And a second Order is created for "Kim" with 1 Gadget  
&emsp;&emsp;    When the Widget Item is moved to the second Order  
&emsp;&emsp;    Then Order amount_total should be 0  
&emsp;&emsp;    And second Order amount_total should be 330  
&emsp;&emsp;    And Customer balance should be 330  

<details markdown>
<summary>Rules exercised and logic log (5 transactions)</summary>


&nbsp;
&nbsp;


**Rules Used** in Scenario: Item Moved To Another Order
```
  DailyFlow  
    1. Derive DailyFlow.request_processed as Count(OrderB2bRequest Where Rule.count(derive=models.DailyFlow.request_processed, as_count_of=models.OrderB2bRequest, where=lambda row: row.is_processed == True, insert_parent=True), insert_parent)  
    2. Derive DailyFlow.request_failed as Count(OrderB2bRequest Where Rule.count(derive=models.DailyFlow.request_failed, as_count_of=models.OrderB2bRequest, where=lambda row: row.error_text is not None, insert_parent=True), insert_parent)  
    3. Derive DailyFlow.request_stuck as Formula (2): Rule.formula(derive=models.DailyFlow.request_stuc [...]  
    4. Derive DailyFlow.request_received as Count(OrderB2bRequest Where  - None, insert_parent)  
    5. Derive DailyFlow.order_amount as Sum(Order.amount_total Where  - None, insert_parent)  
    6. Derive DailyFlow.order_count as Count(Order Where  - None, insert_parent)  
  Customer  
    7. Derive Customer.balance as Sum(Order.amount_total Where Rule.sum(derive=models.Customer.balance, as_sum_of=models.Order.amount_total, where=lambda row: row.date_shipped is None))  
  Item  
    8. Derive Item.amount as Formula (1): Rule.formula(derive=models.Item.amount, as_expres [...]  
    9. Derive Item.unit_price as Copy(product.unit_price)  
  Order  
    10. RowEvent Order._send_order_to_shipping()  
    11. Derive Order.amount_total as Sum(Item.amount Where  - None)  
```
**Logic Log** in Scenario: Item Moved To Another Order (5 transactions)
```
Logic Phase:		ROW LOGIC		(session=0x10c51dd00) (sqlalchemy before_flush)			 - 2026-11-19 17:41:42,253 - logic_logger - INFO
..OrderB2bRequest[None] {Insert - client} id: None, CreatedOn: None, CreatedOnDay: None, payload: {"Account": "Kim 1795138902249", "Notes": "behave test", "Items": [{"Name": "Widget", "QuantityOrdered": 2}]}, is_processed: False, error_text: None  row: 0x10cba34d0  session: 0x10c51dd00  ins_upd_dlt: ins, initial: ins - 2026-11-19 17:41:42,253 - logic_logger - INFO
..OrderB2bRequest[None] {early_row_event_all_classes - handle_all did stamping} id: None, CreatedOn: 2026-11-19 17:41:42.253369, CreatedOnDay: 2026-11-19, payload: {"Account": "Kim 1795138902249", "Notes": "behave test", "Items": [{"Name": "Widget", "QuantityOrdered": 2}]}, is_processed: False, error_text: None  row: 0x10cba34d0  session: 0x10c51dd00  ins_upd_dlt: ins, initial: ins - 2026-11-19 17:41:42,253 - logic_logger - INFO
....DailyFlow[2026-11-19] {Update - Adjusting daily_flow: request_received} day: 2026-11-19, order_count: 10, order_amount: 2220.00, message_received: 1, message_processed: 1, message_failed: 0, message_stuck: 0, request_received:  [13-->] 14, request_processed: 10, request_failed: 3, request_stuck: 0  row: 0x10c28e2b0  session: 0x10c51dd00  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:42,253 - logic_logger - INFO
....DailyFlow[2026-11-19] {Prune Formula: message_stuck [['message_received', 'message_processed', 'message_failed']]} day: 2026-11-19, order_count: 10, order_amount: 2220.00, message_received: 1, message_processed: 1, message_failed: 0, message_stuck: 0, request_received:  [13-->] 14, request_processed: 10, request_failed: 3, request_stuck: 0  row: 0x10c28e2b0  session: 0x10c51dd00  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:42,253 - logic_logger - INFO
....DailyFlow[2026-11-19] {Formula request_stuck} day: 2026-11-19, order_count: 10, order_amount: 2220.00, message_received: 1, message_processed: 1, message_failed: 0, message_stuck: 0, request_received:  [13-->] 14, request_processed: 10, request_failed: 3, request_stuck:  [0-->] 1  row: 0x10c28e2b0  session: 0x10c51dd00  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:42,253 - logic_logger - INFO
Logic Phase:		COMMIT LOGIC		(session=0x10c51dd00)   										 - 2026-11-19 17:41:42,253 - logic_logger - INFO
Logic Phase:		AFTER_FLUSH LOGIC	(session=0x10c51dd00)   										 - 2026-11-19 17:41:42,254 - logic_logger - INFO


Logic Phase:		ROW LOGIC		(session=0x10c51dd00) (sqlalchemy before_flush)			 - 2026-11-19 17:41:42,255 - logic_logger - INFO
..Product[2] {Update - client} id: 2, name: Widget, count_suppliers: 0, unit_price: 90.0000000000  row: 0x10cb26b30  session: 0x10c51dd00  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:42,255 - logic_logger - INFO
..OrderB2bRequest[74] {Update - client} id: 74, CreatedOn: 2026-11-19 17:41:42.253369, CreatedOnDay: 2026-11-19, payload: {"Account": "Kim 1795138902249", "Notes": "behave test", "Items": [{"Name": "Widget", "QuantityOrdered": 2}]}, is_processed:  [False-->] True, error_text: None  row: 0x10cba34d0  session: 0x10c51dd00  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:42,255 - logic_logger - INFO
....DailyFlow[2026-11-19] {Update - Adjusting daily_flow: request_processed} day: 2026-11-19, order_count: 10, order_amount: 2220.00, message_received: 1, message_processed: 1, message_failed: 0, message_stuck: 0, request_received: 14, request_processed:  [10-->] 11, request_failed: 3, request_stuck: 1  row: 0x10c28e2b0  session: 0x10c51dd00  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:42,256 - logic_logger - INFO
....DailyFlow[2026-11-19] {Prune Formula: message_stuck [['message_received', 'message_processed', 'message_failed']]} day: 2026-11-19, order_count: 10, order_amount: 2220.00, message_received: 1, message_processed: 1, message_failed: 0, message_stuck: 0, request_received: 14, request_processed:  [10-->] 11, request_failed: 3, request_stuck: 1  row: 0x10c28e2b0  session: 0x10c51dd00  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:42,256 - logic_logger - INFO
....DailyFlow[2026-11-19] {Formula request_stuck} day: 2026-11-19, order_count: 10, order_amount: 2220.00, message_received: 1, message_processed: 1, message_failed: 0, message_stuck: 0, request_received: 14, request_processed:  [10-->] 11, request_failed: 3, request_stuck:  [1-->] 0  row: 0x10c28e2b0  session: 0x10c51dd00  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:42,256 - logic_logger - INFO
..Order[None] {Insert - client} id: None, notes: behave test, customer_id: 23, CreatedOn: None, date_shipped: None, amount_total: None, CreatedOnDay: None  row: 0x10c4cd880  session: 0x10c51dd00  ins_upd_dlt: ins, initial: ins - 2026-11-19 17:41:42,256 - logic_logger - INFO
..Order[None] {early_row_event_all_classes - handle_all did stamping} id: None, notes: behave test, customer_id: 23, CreatedOn: 2026-11-19, date_shipped: None, amount_total: None, CreatedOnDay: 2026-11-19  row: 0x10c4cd880  session: 0x10c51dd00  ins_upd_dlt: ins, initial: ins - 2026-11-19 17:41:42,256 - logic_logger - INFO
..Order[None] {server aggregate_defaults: amount_total } id: None, notes: behave test, customer_id: 23, CreatedOn: 2026-11-19, date_shipped: None, amount_total: 0, CreatedOnDay: 2026-11-19  row: 0x10c4cd880  session: 0x10c51dd00  ins_upd_dlt: ins, initial: ins - 2026-11-19 17:41:42,256 - logic_logger - INFO
....DailyFlow[2026-11-19] {Update - Adjusting daily_flow: order_count} day: 2026-11-19, order_count:  [10-->] 11, order_amount: 2220.00, message_received: 1, message_processed: 1, message_failed: 0, message_stuck: 0, request_received: 14, request_processed: 11, request_failed: 3, request_stuck: 0  row: 0x10c28e2b0  session: 0x10c51dd00  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:42,256 - logic_logger - INFO
....DailyFlow[2026-11-19] {Prune Formula: message_stuck [['message_received', 'message_processed', 'message_failed']]} day: 2026-11-19, order_count:  [10-->] 11, order_amount: 2220.00, message_received: 1, message_processed: 1, message_failed: 0, message_stuck: 0, request_received: 14, request_processed: 11, request_failed: 3, request_stuck: 0  row: 0x10c28e2b0  session: 0x10c51dd00  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:42,256 - logic_logger - INFO
....DailyFlow[2026-11-19] {Prune Formula: request_stuck [['request_received', 'request_processed', 'request_failed']]} day: 2026-11-19, order_count:  [10-->] 11, order_amount: 2220.00, message_received: 1, message_processed: 1, message_failed: 0, message_stuck: 0, request_received: 14, request_processed: 11, request_failed: 3, request_stuck: 0  row: 0x10c28e2b0  session: 0x10c51dd00  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:42,256 - logic_logger - INFO
..Item[None] {Insert - client} id: None, order_id: None, product_id: None, quantity: 2, amount: None, unit_price: None  row: 0x10cba1cd0  session: 0x10c51dd00  ins_upd_dlt: ins, initial: ins - 2026-11-19 17:41:42,256 - logic_logger - INFO
..Item[None] {copy_rules for role: product - unit_price} id: None, order_id: None, product_id: None, quantity: 2, amount: None, unit_price: 90.0000000000  row: 0x10cba1cd0  session: 0x10c51dd00  ins_upd_dlt: ins, initial: ins - 2026-11-19 17:41:42,256 - logic_logger - INFO
..Item[None] {Formula amount} id: None, order_id: None, product_id: None, quantity: 2, amount: 180.0000000000, unit_price: 90.0000000000  row: 0x10cba1cd0  session: 0x10c51dd00  ins_upd_dlt: ins, initial: ins - 2026-11-19 17:41:42,256 - logic_logger - INFO
....Order[None] {Update - Adjusting order: amount_total} id: None, notes: behave test, customer_id: 23, CreatedOn: 2026-11-19, date_shipped: None, amount_total:  [0-->] 180.0000000000, CreatedOnDay: 2026-11-19  row: 0x10c4cd880  session: 0x10c51dd00  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:42,256 - logic_logger - INFO
......DailyFlow[2026-11-19] {Update - Adjusting daily_flow: order_amount} day: 2026-11-19, order_count: 11, order_amount:  [2220.00-->] 2400.0000000000, message_received: 1, message_processed: 1, message_failed: 0, message_stuck: 0, request_received: 14, request_processed: 11, request_failed: 3, request_stuck: 0  row: 0x10c28e2b0  session: 0x10c51dd00  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:42,256 - logic_logger - INFO
......DailyFlow[2026-11-19] {Prune Formula: message_stuck [['message_received', 'message_processed', 'message_failed']]} day: 2026-11-19, order_count: 11, order_amount:  [2220.00-->] 2400.0000000000, message_received: 1, message_processed: 1, message_failed: 0, message_stuck: 0, request_received: 14, request_processed: 11, request_failed: 3, request_stuck: 0  row: 0x10c28e2b0  session: 0x10c51dd00  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:42,256 - logic_logger - INFO
......DailyFlow[2026-11-19] {Prune Formula: request_stuck [['request_received', 'request_processed', 'request_failed']]} day: 2026-11-19, order_count: 11, order_amount:  [2220.00-->] 2400.0000000000, message_received: 1, message_processed: 1, message_failed: 0, message_stuck: 0, request_received: 14, request_processed: 11, request_failed: 3, request_stuck: 0  row: 0x10c28e2b0  session: 0x10c51dd00  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:42,256 - logic_logger - INFO
......Customer[23] {Update - Adjusting customer: balance} id: 23, name: Kim 1795138902249, balance:  [0E-10-->] 180.0000000000, credit_limit: 5000.0000000000, email: None, email_opt_out: None  row: 0x10cba1dd0  session: 0x10c51dd00  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:42,256 - logic_logger - INFO
Logic Phase:		COMMIT LOGIC		(session=0x10c51dd00)   										 - 2026-11-19 17:41:42,257 - logic_logger - INFO
Logic Phase:		AFTER_FLUSH LOGIC	(session=0x10c51dd00)   										 - 2026-11-19 17:41:42,257 - logic_logger - INFO
..Order[169] {AfterFlush Event} id: 169, notes: behave test, customer_id: 23, CreatedOn: 2026-11-19, date_shipped: None, amount_total: 180.0000000000, CreatedOnDay: 2026-11-19  row: 0x10c4cd880  session: 0x10c51dd00  ins_upd_dlt: ins, initial: ins - 2026-11-19 17:41:42,257 - logic_logger - INFO


Logic Phase:		ROW LOGIC		(session=0x10c51df20) (sqlalchemy before_flush)			 - 2026-11-19 17:41:42,259 - logic_logger - INFO
..OrderB2bRequest[None] {Insert - client} id: None, CreatedOn: None, CreatedOnDay: None, payload: {"Account": "Kim 1795138902249", "Notes": "behave test", "Items": [{"Name": "Gadget", "QuantityOrdered": 1}]}, is_processed: False, error_text: None  row: 0x10cba29d0  session: 0x10c51df20  ins_upd_dlt: ins, initial: ins - 2026-11-19 17:41:42,259 - logic_logger - INFO
..OrderB2bRequest[None] {early_row_event_all_classes - handle_all did stamping} id: None, CreatedOn: 2026-11-19 17:41:42.259935, CreatedOnDay: 2026-11-19, payload: {"Account": "Kim 1795138902249", "Notes": "behave test", "Items": [{"Name": "Gadget", "QuantityOrdered": 1}]}, is_processed: False, error_text: None  row: 0x10cba29d0  session: 0x10c51df20  ins_upd_dlt: ins, initial: ins - 2026-11-19 17:41:42,259 - logic_logger - INFO
....DailyFlow[2026-11-19] {Update - Adjusting daily_flow: request_received} day: 2026-11-19, order_count: 11, order_amount: 2400.00, message_received: 1, message_processed: 1, message_failed: 0, message_stuck: 0, request_received:  [14-->] 15, request_processed: 11, request_failed: 3, request_stuck: 0  row: 0x10c28e4c0  session: 0x10c51df20  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:42,260 - logic_logger - INFO
....DailyFlow[2026-11-19] {Prune Formula: message_stuck [['message_received', 'message_processed', 'message_failed']]} day: 2026-11-19, order_count: 11, order_amount: 2400.00, message_received: 1, message_processed: 1, message_failed: 0, message_stuck: 0, request_received:  [14-->] 15, request_processed: 11, request_failed: 3, request_stuck: 0  row: 0x10c28e4c0  session: 0x10c51df20  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:42,260 - logic_logger - INFO
....DailyFlow[2026-11-19] {Formula request_stuck} day: 2026-11-19, order_count: 11, order_amount: 2400.00, message_received: 1, message_processed: 1, message_failed: 0, message_stuck: 0, request_received:  [14-->] 15, request_processed: 11, request_failed: 3, request_stuck:  [0-->] 1  row: 0x10c28e4c0  session: 0x10c51df20  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:42,260 - logic_logger - INFO
Logic Phase:		COMMIT LOGIC		(session=0x10c51df20)   										 - 2026-11-19 17:41:42,260 - logic_logger - INFO
Logic Phase:		AFTER_FLUSH LOGIC	(session=0x10c51df20)   										 - 2026-11-19 17:41:42,260 - logic_logger - INFO


Logic Phase:		ROW LOGIC		(session=0x10c51df20) (sqlalchemy before_flush)			 - 2026-11-19 17:41:42,262 - logic_logger - INFO
..Product[1] {Update - client} id: 1, name: Gadget, count_suppliers: 0, unit_price: 150.0000000000  row: 0x10cb26dd0  session: 0x10c51df20  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:42,262 - logic_logger - INFO
..OrderB2bRequest[75] {Update - client} id: 75, CreatedOn: 2026-11-19 17:41:42.259935, CreatedOnDay: 2026-11-19, payload: {"Account": "Kim 1795138902249", "Notes": "behave test", "Items": [{"Name": "Gadget", "QuantityOrdered": 1}]}, is_processed:  [False-->] True, error_text: None  row: 0x10cba29d0  session: 0x10c51df20  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:42,262 - logic_logger - INFO
....DailyFlow[2026-11-19] {Update - Adjusting daily_flow: request_processed} day: 2026-11-19, order_count: 11, order_amount: 2400.00, message_received: 1, message_processed: 1, message_failed: 0, message_stuck: 0, request_received: 15, request_processed:  [11-->] 12, request_failed: 3, request_stuck: 1  row: 0x10c28e4c0  session: 0x10c51df20  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:42,262 - logic_logger - INFO
....DailyFlow[2026-11-19] {Prune Formula: message_stuck [['message_received', 'message_processed', 'message_failed']]} day: 2026-11-19, order_count: 11, order_amount: 2400.00, message_received: 1, message_processed: 1, message_failed: 0, message_stuck: 0, request_received: 15, request_processed:  [11-->] 12, request_failed: 3, request_stuck: 1  row: 0x10c28e4c0  session: 0x10c51df20  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:42,262 - logic_logger - INFO
....DailyFlow[2026-11-19] {Formula request_stuck} day: 2026-11-19, order_count: 11, order_amount: 2400.00, message_received: 1, message_processed: 1, message_failed: 0, message_stuck: 0, request_received: 15, request_processed:  [11-->] 12, request_failed: 3, request_stuck:  [1-->] 0  row: 0x10c28e4c0  session: 0x10c51df20  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:42,263 - logic_logger - INFO
..Order[None] {Insert - client} id: None, notes: behave test, customer_id: 23, CreatedOn: None, date_shipped: None, amount_total: None, CreatedOnDay: None  row: 0x10c6db410  session: 0x10c51df20  ins_upd_dlt: ins, initial: ins - 2026-11-19 17:41:42,263 - logic_logger - INFO
..Order[None] {early_row_event_all_classes - handle_all did stamping} id: None, notes: behave test, customer_id: 23, CreatedOn: 2026-11-19, date_shipped: None, amount_total: None, CreatedOnDay: 2026-11-19  row: 0x10c6db410  session: 0x10c51df20  ins_upd_dlt: ins, initial: ins - 2026-11-19 17:41:42,263 - logic_logger - INFO
..Order[None] {server aggregate_defaults: amount_total } id: None, notes: behave test, customer_id: 23, CreatedOn: 2026-11-19, date_shipped: None, amount_total: 0, CreatedOnDay: 2026-11-19  row: 0x10c6db410  session: 0x10c51df20  ins_upd_dlt: ins, initial: ins - 2026-11-19 17:41:42,263 - logic_logger - INFO
....DailyFlow[2026-11-19] {Update - Adjusting daily_flow: order_count} day: 2026-11-19, order_count:  [11-->] 12, order_amount: 2400.00, message_received: 1, message_processed: 1, message_failed: 0, message_stuck: 0, request_received: 15, request_processed: 12, request_failed: 3, request_stuck: 0  row: 0x10c28e4c0  session: 0x10c51df20  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:42,263 - logic_logger - INFO
....DailyFlow[2026-11-19] {Prune Formula: message_stuck [['message_received', 'message_processed', 'message_failed']]} day: 2026-11-19, order_count:  [11-->] 12, order_amount: 2400.00, message_received: 1, message_processed: 1, message_failed: 0, message_stuck: 0, request_received: 15, request_processed: 12, request_failed: 3, request_stuck: 0  row: 0x10c28e4c0  session: 0x10c51df20  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:42,263 - logic_logger - INFO
....DailyFlow[2026-11-19] {Prune Formula: request_stuck [['request_received', 'request_processed', 'request_failed']]} day: 2026-11-19, order_count:  [11-->] 12, order_amount: 2400.00, message_received: 1, message_processed: 1, message_failed: 0, message_stuck: 0, request_received: 15, request_processed: 12, request_failed: 3, request_stuck: 0  row: 0x10c28e4c0  session: 0x10c51df20  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:42,263 - logic_logger - INFO
..Item[None] {Insert - client} id: None, order_id: None, product_id: None, quantity: 1, amount: None, unit_price: None  row: 0x10cba1bd0  session: 0x10c51df20  ins_upd_dlt: ins, initial: ins - 2026-11-19 17:41:42,263 - logic_logger - INFO
..Item[None] {copy_rules for role: product - unit_price} id: None, order_id: None, product_id: None, quantity: 1, amount: None, unit_price: 150.0000000000  row: 0x10cba1bd0  session: 0x10c51df20  ins_upd_dlt: ins, initial: ins - 2026-11-19 17:41:42,263 - logic_logger - INFO
..Item[None] {Formula amount} id: None, order_id: None, product_id: None, quantity: 1, amount: 150.0000000000, unit_price: 150.0000000000  row: 0x10cba1bd0  session: 0x10c51df20  ins_upd_dlt: ins, initial: ins - 2026-11-19 17:41:42,263 - logic_logger - INFO
....Order[None] {Update - Adjusting order: amount_total} id: None, notes: behave test, customer_id: 23, CreatedOn: 2026-11-19, date_shipped: None, amount_total:  [0-->] 150.0000000000, CreatedOnDay: 2026-11-19  row: 0x10c6db410  session: 0x10c51df20  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:42,263 - logic_logger - INFO
......DailyFlow[2026-11-19] {Update - Adjusting daily_flow: order_amount} day: 2026-11-19, order_count: 12, order_amount:  [2400.00-->] 2550.0000000000, message_received: 1, message_processed: 1, message_failed: 0, message_stuck: 0, request_received: 15, request_processed: 12, request_failed: 3, request_stuck: 0  row: 0x10c28e4c0  session: 0x10c51df20  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:42,263 - logic_logger - INFO
......DailyFlow[2026-11-19] {Prune Formula: message_stuck [['message_received', 'message_processed', 'message_failed']]} day: 2026-11-19, order_count: 12, order_amount:  [2400.00-->] 2550.0000000000, message_received: 1, message_processed: 1, message_failed: 0, message_stuck: 0, request_received: 15, request_processed: 12, request_failed: 3, request_stuck: 0  row: 0x10c28e4c0  session: 0x10c51df20  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:42,263 - logic_logger - INFO
......DailyFlow[2026-11-19] {Prune Formula: request_stuck [['request_received', 'request_processed', 'request_failed']]} day: 2026-11-19, order_count: 12, order_amount:  [2400.00-->] 2550.0000000000, message_received: 1, message_processed: 1, message_failed: 0, message_stuck: 0, request_received: 15, request_processed: 12, request_failed: 3, request_stuck: 0  row: 0x10c28e4c0  session: 0x10c51df20  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:42,263 - logic_logger - INFO
......Customer[23] {Update - Adjusting customer: balance} id: 23, name: Kim 1795138902249, balance:  [180.0000000000-->] 330.0000000000, credit_limit: 5000.0000000000, email: None, email_opt_out: None  row: 0x10cba3350  session: 0x10c51df20  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:42,263 - logic_logger - INFO
Logic Phase:		COMMIT LOGIC		(session=0x10c51df20)   										 - 2026-11-19 17:41:42,263 - logic_logger - INFO
Logic Phase:		AFTER_FLUSH LOGIC	(session=0x10c51df20)   										 - 2026-11-19 17:41:42,264 - logic_logger - INFO
..Order[170] {AfterFlush Event} id: 170, notes: behave test, customer_id: 23, CreatedOn: 2026-11-19, date_shipped: None, amount_total: 150.0000000000, CreatedOnDay: 2026-11-19  row: 0x10c6db410  session: 0x10c51df20  ins_upd_dlt: ins, initial: ins - 2026-11-19 17:41:42,264 - logic_logger - INFO


Logic Phase:		ROW LOGIC		(session=0x10c51e250) (sqlalchemy before_flush)			 - 2026-11-19 17:41:42,272 - logic_logger - INFO
..Item[317] {Update - client} id: 317, order_id:  [169-->] 170, product_id: 2, quantity: 2, amount: 180.0000000000, unit_price: 90.0000000000  row: 0x10cba3bd0  session: 0x10c51e250  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:42,272 - logic_logger - INFO
..Item[317] {Prune Formula: amount [['quantity', 'unit_price']]} id: 317, order_id:  [169-->] 170, product_id: 2, quantity: 2, amount: 180.0000000000, unit_price: 90.0000000000  row: 0x10cba3bd0  session: 0x10c51e250  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:42,272 - logic_logger - INFO
....Order[170] {Update - Adjusting order: amount_total, amount_total} id: 170, notes: behave test, customer_id: 23, CreatedOn: 2026-11-19, date_shipped: None, amount_total:  [150.0000000000-->] 330.0000000000, CreatedOnDay: 2026-11-19  row: 0x10c6daba0  session: 0x10c51e250  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:42,272 - logic_logger - INFO
......DailyFlow[2026-11-19] {Update - Adjusting daily_flow: order_amount} day: 2026-11-19, order_count: 12, order_amount:  [2550.00-->] 2730.0000000000, message_received: 1, message_processed: 1, message_failed: 0, message_stuck: 0, request_received: 15, request_processed: 12, request_failed: 3, request_stuck: 0  row: 0x10c28f1d0  session: 0x10c51e250  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:42,273 - logic_logger - INFO
......DailyFlow[2026-11-19] {Prune Formula: message_stuck [['message_received', 'message_processed', 'message_failed']]} day: 2026-11-19, order_count: 12, order_amount:  [2550.00-->] 2730.0000000000, message_received: 1, message_processed: 1, message_failed: 0, message_stuck: 0, request_received: 15, request_processed: 12, request_failed: 3, request_stuck: 0  row: 0x10c28f1d0  session: 0x10c51e250  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:42,273 - logic_logger - INFO
......DailyFlow[2026-11-19] {Prune Formula: request_stuck [['request_received', 'request_processed', 'request_failed']]} day: 2026-11-19, order_count: 12, order_amount:  [2550.00-->] 2730.0000000000, message_received: 1, message_processed: 1, message_failed: 0, message_stuck: 0, request_received: 15, request_processed: 12, request_failed: 3, request_stuck: 0  row: 0x10c28f1d0  session: 0x10c51e250  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:42,273 - logic_logger - INFO
......Customer[23] {Update - Adjusting customer: balance} id: 23, name: Kim 1795138902249, balance:  [330.0000000000-->] 510.0000000000, credit_limit: 5000.0000000000, email: None, email_opt_out: None  row: 0x10cb83450  session: 0x10c51e250  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:42,273 - logic_logger - INFO
....Order[169] {Update - Adjusting Old order} id: 169, notes: behave test, customer_id: 23, CreatedOn: 2026-11-19, date_shipped: None, amount_total:  [180.0000000000-->] 0E-10, CreatedOnDay: 2026-11-19  row: 0x10c6da8d0  session: 0x10c51e250  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:42,273 - logic_logger - INFO
......DailyFlow[2026-11-19] {Update - Adjusting daily_flow: order_amount} day: 2026-11-19, order_count: 12, order_amount:  [2730.0000000000-->] 2550.0000000000, message_received: 1, message_processed: 1, message_failed: 0, message_stuck: 0, request_received: 15, request_processed: 12, request_failed: 3, request_stuck: 0  row: 0x10c28f1d0  session: 0x10c51e250  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:42,273 - logic_logger - INFO
......DailyFlow[2026-11-19] {Prune Formula: message_stuck [['message_received', 'message_processed', 'message_failed']]} day: 2026-11-19, order_count: 12, order_amount:  [2730.0000000000-->] 2550.0000000000, message_received: 1, message_processed: 1, message_failed: 0, message_stuck: 0, request_received: 15, request_processed: 12, request_failed: 3, request_stuck: 0  row: 0x10c28f1d0  session: 0x10c51e250  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:42,273 - logic_logger - INFO
......DailyFlow[2026-11-19] {Prune Formula: request_stuck [['request_received', 'request_processed', 'request_failed']]} day: 2026-11-19, order_count: 12, order_amount:  [2730.0000000000-->] 2550.0000000000, message_received: 1, message_processed: 1, message_failed: 0, message_stuck: 0, request_received: 15, request_processed: 12, request_failed: 3, request_stuck: 0  row: 0x10c28f1d0  session: 0x10c51e250  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:42,273 - logic_logger - INFO
......Customer[23] {Update - Adjusting customer: balance} id: 23, name: Kim 1795138902249, balance:  [510.0000000000-->] 330.0000000000, credit_limit: 5000.0000000000, email: None, email_opt_out: None  row: 0x10cb83450  session: 0x10c51e250  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:42,273 - logic_logger - INFO
Logic Phase:		COMMIT LOGIC		(session=0x10c51e250)   										 - 2026-11-19 17:41:42,273 - logic_logger - INFO
Logic Phase:		AFTER_FLUSH LOGIC	(session=0x10c51e250)   										 - 2026-11-19 17:41:42,274 - logic_logger - INFO
....Order[170] {AfterFlush Event} id: 170, notes: behave test, customer_id: 23, CreatedOn: 2026-11-19, date_shipped: None, amount_total:  [150.0000000000-->] 330.0000000000, CreatedOnDay: 2026-11-19  row: 0x10c6daba0  session: 0x10c51e250  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:42,274 - logic_logger - INFO
....Order[169] {AfterFlush Event} id: 169, notes: behave test, customer_id: 23, CreatedOn: 2026-11-19, date_shipped: None, amount_total:  [180.0000000000-->] 0E-10, CreatedOnDay: 2026-11-19  row: 0x10c6da8d0  session: 0x10c51e250  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:42,274 - logic_logger - INFO

```
</details>

&nbsp;
&nbsp;

#### Scenario: Item Product Changed ✅ (0.03 s)
&emsp;  Scenario: Item Product Changed  
&emsp;&emsp;    Given Customer "Lee" with credit limit 5000  
&emsp;&emsp;    And Order is created for "Lee" with 2 Widget  
&emsp;&emsp;    When the Item product is changed to Gadget  
&emsp;&emsp;    Then Item unit_price should be 150  
&emsp;&emsp;    And Order amount_total should be 300  
&emsp;&emsp;    And Customer balance should be 300  

<details markdown>
<summary>Rules exercised and logic log (3 transactions)</summary>


&nbsp;
&nbsp;


**Rules Used** in Scenario: Item Product Changed
```
  DailyFlow  
    1. Derive DailyFlow.request_processed as Count(OrderB2bRequest Where Rule.count(derive=models.DailyFlow.request_processed, as_count_of=models.OrderB2bRequest, where=lambda row: row.is_processed == True, insert_parent=True), insert_parent)  
    2. Derive DailyFlow.request_failed as Count(OrderB2bRequest Where Rule.count(derive=models.DailyFlow.request_failed, as_count_of=models.OrderB2bRequest, where=lambda row: row.error_text is not None, insert_parent=True), insert_parent)  
    3. Derive DailyFlow.request_stuck as Formula (2): Rule.formula(derive=models.DailyFlow.request_stuc [...]  
    4. Derive DailyFlow.request_received as Count(OrderB2bRequest Where  - None, insert_parent)  
    5. Derive DailyFlow.order_amount as Sum(Order.amount_total Where  - None, insert_parent)  
    6. Derive DailyFlow.order_count as Count(Order Where  - None, insert_parent)  
  Customer  
    7. Derive Customer.balance as Sum(Order.amount_total Where Rule.sum(derive=models.Customer.balance, as_sum_of=models.Order.amount_total, where=lambda row: row.date_shipped is None))  
  Item  
    8. Derive Item.amount as Formula (1): Rule.formula(derive=models.Item.amount, as_expres [...]  
    9. Derive Item.unit_price as Copy(product.unit_price)  
  Order  
    10. RowEvent Order._send_order_to_shipping()  
    11. Derive Order.amount_total as Sum(Item.amount Where  - None)  
```
**Logic Log** in Scenario: Item Product Changed (3 transactions)
```
Logic Phase:		ROW LOGIC		(session=0x10c51ead0) (sqlalchemy before_flush)			 - 2026-11-19 17:41:42,288 - logic_logger - INFO
..OrderB2bRequest[None] {Insert - client} id: None, CreatedOn: None, CreatedOnDay: None, payload: {"Account": "Lee 1795138902283", "Notes": "behave test", "Items": [{"Name": "Widget", "QuantityOrdered": 2}]}, is_processed: False, error_text: None  row: 0x10cb810d0  session: 0x10c51ead0  ins_upd_dlt: ins, initial: ins - 2026-11-19 17:41:42,288 - logic_logger - INFO
..OrderB2bRequest[None] {early_row_event_all_classes - handle_all did stamping} id: None, CreatedOn: 2026-11-19 17:41:42.288129, CreatedOnDay: 2026-11-19, payload: {"Account": "Lee 1795138902283", "Notes": "behave test", "Items": [{"Name": "Widget", "QuantityOrdered": 2}]}, is_processed: False, error_text: None  row: 0x10cb810d0  session: 0x10c51ead0  ins_upd_dlt: ins, initial: ins - 2026-11-19 17:41:42,288 - logic_logger - INFO
....DailyFlow[2026-11-19] {Update - Adjusting daily_flow: request_received} day: 2026-11-19, order_count: 12, order_amount: 2550.00, message_received: 1, message_processed: 1, message_failed: 0, message_stuck: 0, request_received:  [15-->] 16, request_processed: 12, request_failed: 3, request_stuck: 0  row: 0x10c615d30  session: 0x10c51ead0  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:42,288 - logic_logger - INFO
....DailyFlow[2026-11-19] {Prune Formula: message_stuck [['message_received', 'message_processed', 'message_failed']]} day: 2026-11-19, order_count: 12, order_amount: 2550.00, message_received: 1, message_processed: 1, message_failed: 0, message_stuck: 0, request_received:  [15-->] 16, request_processed: 12, request_failed: 3, request_stuck: 0  row: 0x10c615d30  session: 0x10c51ead0  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:42,288 - logic_logger - INFO
....DailyFlow[2026-11-19] {Formula request_stuck} day: 2026-11-19, order_count: 12, order_amount: 2550.00, message_received: 1, message_processed: 1, message_failed: 0, message_stuck: 0, request_received:  [15-->] 16, request_processed: 12, request_failed: 3, request_stuck:  [0-->] 1  row: 0x10c615d30  session: 0x10c51ead0  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:42,288 - logic_logger - INFO
Logic Phase:		COMMIT LOGIC		(session=0x10c51ead0)   										 - 2026-11-19 17:41:42,288 - logic_logger - INFO
Logic Phase:		AFTER_FLUSH LOGIC	(session=0x10c51ead0)   										 - 2026-11-19 17:41:42,288 - logic_logger - INFO


Logic Phase:		ROW LOGIC		(session=0x10c51ead0) (sqlalchemy before_flush)			 - 2026-11-19 17:41:42,290 - logic_logger - INFO
..OrderB2bRequest[76] {Update - client} id: 76, CreatedOn: 2026-11-19 17:41:42.288129, CreatedOnDay: 2026-11-19, payload: {"Account": "Lee 1795138902283", "Notes": "behave test", "Items": [{"Name": "Widget", "QuantityOrdered": 2}]}, is_processed:  [False-->] True, error_text: None  row: 0x10cb810d0  session: 0x10c51ead0  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:42,290 - logic_logger - INFO
....DailyFlow[2026-11-19] {Update - Adjusting daily_flow: request_processed} day: 2026-11-19, order_count: 12, order_amount: 2550.00, message_received: 1, message_processed: 1, message_failed: 0, message_stuck: 0, request_received: 16, request_processed:  [12-->] 13, request_failed: 3, request_stuck: 1  row: 0x10c615d30  session: 0x10c51ead0  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:42,291 - logic_logger - INFO
....DailyFlow[2026-11-19] {Prune Formula: message_stuck [['message_received', 'message_processed', 'message_failed']]} day: 2026-11-19, order_count: 12, order_amount: 2550.00, message_received: 1, message_processed: 1, message_failed: 0, message_stuck: 0, request_received: 16, request_processed:  [12-->] 13, request_failed: 3, request_stuck: 1  row: 0x10c615d30  session: 0x10c51ead0  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:42,291 - logic_logger - INFO
....DailyFlow[2026-11-19] {Formula request_stuck} day: 2026-11-19, order_count: 12, order_amount: 2550.00, message_received: 1, message_processed: 1, message_failed: 0, message_stuck: 0, request_received: 16, request_processed:  [12-->] 13, request_failed: 3, request_stuck:  [1-->] 0  row: 0x10c615d30  session: 0x10c51ead0  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:42,291 - logic_logger - INFO
..Product[2] {Update - client} id: 2, name: Widget, count_suppliers: 0, unit_price: 90.0000000000  row: 0x10cb265f0  session: 0x10c51ead0  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:42,291 - logic_logger - INFO
..Order[None] {Insert - client} id: None, notes: behave test, customer_id: 24, CreatedOn: None, date_shipped: None, amount_total: None, CreatedOnDay: None  row: 0x10c4cdbe0  session: 0x10c51ead0  ins_upd_dlt: ins, initial: ins - 2026-11-19 17:41:42,291 - logic_logger - INFO
..Order[None] {early_row_event_all_classes - handle_all did stamping} id: None, notes: behave test, customer_id: 24, CreatedOn: 2026-11-19, date_shipped: None, amount_total: None, CreatedOnDay: 2026-11-19  row: 0x10c4cdbe0  session: 0x10c51ead0  ins_upd_dlt: ins, initial: ins - 2026-11-19 17:41:42,291 - logic_logger - INFO
..Order[None] {server aggregate_defaults: amount_total } id: None, notes: behave test, customer_id: 24, CreatedOn: 2026-11-19, date_shipped: None, amount_total: 0, CreatedOnDay: 2026-11-19  row: 0x10c4cdbe0  session: 0x10c51ead0  ins_upd_dlt: ins, initial: ins - 2026-11-19 17:41:42,291 - logic_logger - INFO
....DailyFlow[2026-11-19] {Update - Adjusting daily_flow: order_count} day: 2026-11-19, order_count:  [12-->] 13, order_amount: 2550.00, message_received: 1, message_processed: 1, message_failed: 0, message_stuck: 0, request_received: 16, request_processed: 13, request_failed: 3, request_stuck: 0  row: 0x10c615d30  session: 0x10c51ead0  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:42,291 - logic_logger - INFO
....DailyFlow[2026-11-19] {Prune Formula: message_stuck [['message_received', 'message_processed', 'message_failed']]} day: 2026-11-19, order_count:  [12-->] 13, order_amount: 2550.00, message_received: 1, message_processed: 1, message_failed: 0, message_stuck: 0, request_received: 16, request_processed: 13, request_failed: 3, request_stuck: 0  row: 0x10c615d30  session: 0x10c51ead0  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:42,291 - logic_logger - INFO
....DailyFlow[2026-11-19] {Prune Formula: request_stuck [['request_received', 'request_processed', 'request_failed']]} day: 2026-11-19, order_count:  [12-->] 13, order_amount: 2550.00, message_received: 1, message_processed: 1, message_failed: 0, message_stuck: 0, request_received: 16, request_processed: 13, request_failed: 3, request_stuck: 0  row: 0x10c615d30  session: 0x10c51ead0  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:42,291 - logic_logger - INFO
..Item[None] {Insert - client} id: None, order_id: None, product_id: None, quantity: 2, amount: None, unit_price: None  row: 0x10cb81550  session: 0x10c51ead0  ins_upd_dlt: ins, initial: ins - 2026-11-19 17:41:42,291 - logic_logger - INFO
..Item[None] {copy_rules for role: product - unit_price} id: None, order_id: None, product_id: None, quantity: 2, amount: None, unit_price: 90.0000000000  row: 0x10cb81550  session: 0x10c51ead0  ins_upd_dlt: ins, initial: ins - 2026-11-19 17:41:42,291 - logic_logger - INFO
..Item[None] {Formula amount} id: None, order_id: None, product_id: None, quantity: 2, amount: 180.0000000000, unit_price: 90.0000000000  row: 0x10cb81550  session: 0x10c51ead0  ins_upd_dlt: ins, initial: ins - 2026-11-19 17:41:42,291 - logic_logger - INFO
....Order[None] {Update - Adjusting order: amount_total} id: None, notes: behave test, customer_id: 24, CreatedOn: 2026-11-19, date_shipped: None, amount_total:  [0-->] 180.0000000000, CreatedOnDay: 2026-11-19  row: 0x10c4cdbe0  session: 0x10c51ead0  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:42,291 - logic_logger - INFO
......DailyFlow[2026-11-19] {Update - Adjusting daily_flow: order_amount} day: 2026-11-19, order_count: 13, order_amount:  [2550.00-->] 2730.0000000000, message_received: 1, message_processed: 1, message_failed: 0, message_stuck: 0, request_received: 16, request_processed: 13, request_failed: 3, request_stuck: 0  row: 0x10c615d30  session: 0x10c51ead0  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:42,291 - logic_logger - INFO
......DailyFlow[2026-11-19] {Prune Formula: message_stuck [['message_received', 'message_processed', 'message_failed']]} day: 2026-11-19, order_count: 13, order_amount:  [2550.00-->] 2730.0000000000, message_received: 1, message_processed: 1, message_failed: 0, message_stuck: 0, request_received: 16, request_processed: 13, request_failed: 3, request_stuck: 0  row: 0x10c615d30  session: 0x10c51ead0  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:42,291 - logic_logger - INFO
......DailyFlow[2026-11-19] {Prune Formula: request_stuck [['request_received', 'request_processed', 'request_failed']]} day: 2026-11-19, order_count: 13, order_amount:  [2550.00-->] 2730.0000000000, message_received: 1, message_processed: 1, message_failed: 0, message_stuck: 0, request_received: 16, request_processed: 13, request_failed: 3, request_stuck: 0  row: 0x10c615d30  session: 0x10c51ead0  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:42,292 - logic_logger - INFO
......Customer[24] {Update - Adjusting customer: balance} id: 24, name: Lee 1795138902283, balance:  [0E-10-->] 180.0000000000, credit_limit: 5000.0000000000, email: None, email_opt_out: None  row: 0x10cb81450  session: 0x10c51ead0  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:42,292 - logic_logger - INFO
Logic Phase:		COMMIT LOGIC		(session=0x10c51ead0)   										 - 2026-11-19 17:41:42,292 - logic_logger - INFO
Logic Phase:		AFTER_FLUSH LOGIC	(session=0x10c51ead0)   										 - 2026-11-19 17:41:42,292 - logic_logger - INFO
..Order[171] {AfterFlush Event} id: 171, notes: behave test, customer_id: 24, CreatedOn: 2026-11-19, date_shipped: None, amount_total: 180.0000000000, CreatedOnDay: 2026-11-19  row: 0x10c4cdbe0  session: 0x10c51ead0  ins_upd_dlt: ins, initial: ins - 2026-11-19 17:41:42,292 - logic_logger - INFO


Logic Phase:		ROW LOGIC		(session=0x10c51e7a0) (sqlalchemy before_flush)			 - 2026-11-19 17:41:42,300 - logic_logger - INFO
..Item[319] {Update - client} id: 319, order_id: 171, product_id:  [2-->] 1, quantity: 2, amount: 180.0000000000, unit_price: 90.0000000000  row: 0x10cb4f550  session: 0x10c51e7a0  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:42,300 - logic_logger - INFO
..Item[319] {copy_rules for role: product - unit_price} id: 319, order_id: 171, product_id:  [2-->] 1, quantity: 2, amount: 180.0000000000, unit_price:  [90.0000000000-->] 150.0000000000  row: 0x10cb4f550  session: 0x10c51e7a0  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:42,300 - logic_logger - INFO
..Item[319] {Formula amount} id: 319, order_id: 171, product_id:  [2-->] 1, quantity: 2, amount:  [180.0000000000-->] 300.0000000000, unit_price:  [90.0000000000-->] 150.0000000000  row: 0x10cb4f550  session: 0x10c51e7a0  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:42,300 - logic_logger - INFO
....Order[171] {Update - Adjusting order: amount_total} id: 171, notes: behave test, customer_id: 24, CreatedOn: 2026-11-19, date_shipped: None, amount_total:  [180.0000000000-->] 300.0000000000, CreatedOnDay: 2026-11-19  row: 0x10c6db2f0  session: 0x10c51e7a0  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:42,300 - logic_logger - INFO
......DailyFlow[2026-11-19] {Update - Adjusting daily_flow: order_amount} day: 2026-11-19, order_count: 13, order_amount:  [2730.00-->] 2850.0000000000, message_received: 1, message_processed: 1, message_failed: 0, message_stuck: 0, request_received: 16, request_processed: 13, request_failed: 3, request_stuck: 0  row: 0x10c615de0  session: 0x10c51e7a0  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:42,301 - logic_logger - INFO
......DailyFlow[2026-11-19] {Prune Formula: message_stuck [['message_received', 'message_processed', 'message_failed']]} day: 2026-11-19, order_count: 13, order_amount:  [2730.00-->] 2850.0000000000, message_received: 1, message_processed: 1, message_failed: 0, message_stuck: 0, request_received: 16, request_processed: 13, request_failed: 3, request_stuck: 0  row: 0x10c615de0  session: 0x10c51e7a0  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:42,301 - logic_logger - INFO
......DailyFlow[2026-11-19] {Prune Formula: request_stuck [['request_received', 'request_processed', 'request_failed']]} day: 2026-11-19, order_count: 13, order_amount:  [2730.00-->] 2850.0000000000, message_received: 1, message_processed: 1, message_failed: 0, message_stuck: 0, request_received: 16, request_processed: 13, request_failed: 3, request_stuck: 0  row: 0x10c615de0  session: 0x10c51e7a0  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:42,301 - logic_logger - INFO
......Customer[24] {Update - Adjusting customer: balance} id: 24, name: Lee 1795138902283, balance:  [180.0000000000-->] 300.0000000000, credit_limit: 5000.0000000000, email: None, email_opt_out: None  row: 0x10cba34d0  session: 0x10c51e7a0  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:42,301 - logic_logger - INFO
Logic Phase:		COMMIT LOGIC		(session=0x10c51e7a0)   										 - 2026-11-19 17:41:42,301 - logic_logger - INFO
Logic Phase:		AFTER_FLUSH LOGIC	(session=0x10c51e7a0)   										 - 2026-11-19 17:41:42,302 - logic_logger - INFO
....Order[171] {AfterFlush Event} id: 171, notes: behave test, customer_id: 24, CreatedOn: 2026-11-19, date_shipped: None, amount_total:  [180.0000000000-->] 300.0000000000, CreatedOnDay: 2026-11-19  row: 0x10c6db2f0  session: 0x10c51e7a0  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:42,302 - logic_logger - INFO

```
</details>

&nbsp;
&nbsp;

### Feature: Kafka Publish Shipping Notification  

&nbsp;
&nbsp;

#### Scenario: Shipping Notification Published ✅ (0.02 s)
&emsp;  Scenario: Shipping Notification Published  
&emsp;&emsp;    Given Customer "Gina" with credit limit 5000  
&emsp;&emsp;    And Order is created for "Gina" with 1 Widget  
&emsp;&emsp;    When Order is shipped  
&emsp;&emsp;    Then the order_shipping message is published with the order id and total  

<details markdown>
<summary>Rules exercised and logic log (3 transactions)</summary>


&nbsp;
&nbsp;


**Rules Used** in Scenario: Shipping Notification Published
```
  DailyFlow  
    1. Derive DailyFlow.request_processed as Count(OrderB2bRequest Where Rule.count(derive=models.DailyFlow.request_processed, as_count_of=models.OrderB2bRequest, where=lambda row: row.is_processed == True, insert_parent=True), insert_parent)  
    2. Derive DailyFlow.request_failed as Count(OrderB2bRequest Where Rule.count(derive=models.DailyFlow.request_failed, as_count_of=models.OrderB2bRequest, where=lambda row: row.error_text is not None, insert_parent=True), insert_parent)  
    3. Derive DailyFlow.request_stuck as Formula (2): Rule.formula(derive=models.DailyFlow.request_stuc [...]  
    4. Derive DailyFlow.request_received as Count(OrderB2bRequest Where  - None, insert_parent)  
    5. Derive DailyFlow.order_amount as Sum(Order.amount_total Where  - None, insert_parent)  
    6. Derive DailyFlow.order_count as Count(Order Where  - None, insert_parent)  
  Customer  
    7. Derive Customer.balance as Sum(Order.amount_total Where Rule.sum(derive=models.Customer.balance, as_sum_of=models.Order.amount_total, where=lambda row: row.date_shipped is None))  
  Item  
    8. Derive Item.amount as Formula (1): Rule.formula(derive=models.Item.amount, as_expres [...]  
    9. Derive Item.unit_price as Copy(product.unit_price)  
  Order  
    10. RowEvent Order._send_order_to_shipping()  
    11. Derive Order.amount_total as Sum(Item.amount Where  - None)  
```
**Logic Log** in Scenario: Shipping Notification Published (3 transactions)
```
Logic Phase:		ROW LOGIC		(session=0x10c51e470) (sqlalchemy before_flush)			 - 2026-11-19 17:41:42,316 - logic_logger - INFO
..OrderB2bRequest[None] {Insert - client} id: None, CreatedOn: None, CreatedOnDay: None, payload: {"Account": "Gina 1795138902312", "Notes": "behave test", "Items": [{"Name": "Widget", "QuantityOrdered": 1}]}, is_processed: False, error_text: None  row: 0x10cba3f50  session: 0x10c51e470  ins_upd_dlt: ins, initial: ins - 2026-11-19 17:41:42,316 - logic_logger - INFO
..OrderB2bRequest[None] {early_row_event_all_classes - handle_all did stamping} id: None, CreatedOn: 2026-11-19 17:41:42.316583, CreatedOnDay: 2026-11-19, payload: {"Account": "Gina 1795138902312", "Notes": "behave test", "Items": [{"Name": "Widget", "QuantityOrdered": 1}]}, is_processed: False, error_text: None  row: 0x10cba3f50  session: 0x10c51e470  ins_upd_dlt: ins, initial: ins - 2026-11-19 17:41:42,316 - logic_logger - INFO
....DailyFlow[2026-11-19] {Update - Adjusting daily_flow: request_received} day: 2026-11-19, order_count: 13, order_amount: 2850.00, message_received: 1, message_processed: 1, message_failed: 0, message_stuck: 0, request_received:  [16-->] 17, request_processed: 13, request_failed: 3, request_stuck: 0  row: 0x10c28fee0  session: 0x10c51e470  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:42,316 - logic_logger - INFO
....DailyFlow[2026-11-19] {Prune Formula: message_stuck [['message_received', 'message_processed', 'message_failed']]} day: 2026-11-19, order_count: 13, order_amount: 2850.00, message_received: 1, message_processed: 1, message_failed: 0, message_stuck: 0, request_received:  [16-->] 17, request_processed: 13, request_failed: 3, request_stuck: 0  row: 0x10c28fee0  session: 0x10c51e470  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:42,317 - logic_logger - INFO
....DailyFlow[2026-11-19] {Formula request_stuck} day: 2026-11-19, order_count: 13, order_amount: 2850.00, message_received: 1, message_processed: 1, message_failed: 0, message_stuck: 0, request_received:  [16-->] 17, request_processed: 13, request_failed: 3, request_stuck:  [0-->] 1  row: 0x10c28fee0  session: 0x10c51e470  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:42,317 - logic_logger - INFO
Logic Phase:		COMMIT LOGIC		(session=0x10c51e470)   										 - 2026-11-19 17:41:42,317 - logic_logger - INFO
Logic Phase:		AFTER_FLUSH LOGIC	(session=0x10c51e470)   										 - 2026-11-19 17:41:42,317 - logic_logger - INFO


Logic Phase:		ROW LOGIC		(session=0x10c51e470) (sqlalchemy before_flush)			 - 2026-11-19 17:41:42,319 - logic_logger - INFO
..Product[2] {Update - client} id: 2, name: Widget, count_suppliers: 0, unit_price: 90.0000000000  row: 0x10cb264a0  session: 0x10c51e470  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:42,319 - logic_logger - INFO
..OrderB2bRequest[77] {Update - client} id: 77, CreatedOn: 2026-11-19 17:41:42.316583, CreatedOnDay: 2026-11-19, payload: {"Account": "Gina 1795138902312", "Notes": "behave test", "Items": [{"Name": "Widget", "QuantityOrdered": 1}]}, is_processed:  [False-->] True, error_text: None  row: 0x10cba3f50  session: 0x10c51e470  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:42,319 - logic_logger - INFO
....DailyFlow[2026-11-19] {Update - Adjusting daily_flow: request_processed} day: 2026-11-19, order_count: 13, order_amount: 2850.00, message_received: 1, message_processed: 1, message_failed: 0, message_stuck: 0, request_received: 17, request_processed:  [13-->] 14, request_failed: 3, request_stuck: 1  row: 0x10c28fee0  session: 0x10c51e470  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:42,319 - logic_logger - INFO
....DailyFlow[2026-11-19] {Prune Formula: message_stuck [['message_received', 'message_processed', 'message_failed']]} day: 2026-11-19, order_count: 13, order_amount: 2850.00, message_received: 1, message_processed: 1, message_failed: 0, message_stuck: 0, request_received: 17, request_processed:  [13-->] 14, request_failed: 3, request_stuck: 1  row: 0x10c28fee0  session: 0x10c51e470  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:42,319 - logic_logger - INFO
....DailyFlow[2026-11-19] {Formula request_stuck} day: 2026-11-19, order_count: 13, order_amount: 2850.00, message_received: 1, message_processed: 1, message_failed: 0, message_stuck: 0, request_received: 17, request_processed:  [13-->] 14, request_failed: 3, request_stuck:  [1-->] 0  row: 0x10c28fee0  session: 0x10c51e470  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:42,319 - logic_logger - INFO
..Order[None] {Insert - client} id: None, notes: behave test, customer_id: 25, CreatedOn: None, date_shipped: None, amount_total: None, CreatedOnDay: None  row: 0x10c4cf140  session: 0x10c51e470  ins_upd_dlt: ins, initial: ins - 2026-11-19 17:41:42,319 - logic_logger - INFO
..Order[None] {early_row_event_all_classes - handle_all did stamping} id: None, notes: behave test, customer_id: 25, CreatedOn: 2026-11-19, date_shipped: None, amount_total: None, CreatedOnDay: 2026-11-19  row: 0x10c4cf140  session: 0x10c51e470  ins_upd_dlt: ins, initial: ins - 2026-11-19 17:41:42,319 - logic_logger - INFO
..Order[None] {server aggregate_defaults: amount_total } id: None, notes: behave test, customer_id: 25, CreatedOn: 2026-11-19, date_shipped: None, amount_total: 0, CreatedOnDay: 2026-11-19  row: 0x10c4cf140  session: 0x10c51e470  ins_upd_dlt: ins, initial: ins - 2026-11-19 17:41:42,319 - logic_logger - INFO
....DailyFlow[2026-11-19] {Update - Adjusting daily_flow: order_count} day: 2026-11-19, order_count:  [13-->] 14, order_amount: 2850.00, message_received: 1, message_processed: 1, message_failed: 0, message_stuck: 0, request_received: 17, request_processed: 14, request_failed: 3, request_stuck: 0  row: 0x10c28fee0  session: 0x10c51e470  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:42,320 - logic_logger - INFO
....DailyFlow[2026-11-19] {Prune Formula: message_stuck [['message_received', 'message_processed', 'message_failed']]} day: 2026-11-19, order_count:  [13-->] 14, order_amount: 2850.00, message_received: 1, message_processed: 1, message_failed: 0, message_stuck: 0, request_received: 17, request_processed: 14, request_failed: 3, request_stuck: 0  row: 0x10c28fee0  session: 0x10c51e470  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:42,320 - logic_logger - INFO
....DailyFlow[2026-11-19] {Prune Formula: request_stuck [['request_received', 'request_processed', 'request_failed']]} day: 2026-11-19, order_count:  [13-->] 14, order_amount: 2850.00, message_received: 1, message_processed: 1, message_failed: 0, message_stuck: 0, request_received: 17, request_processed: 14, request_failed: 3, request_stuck: 0  row: 0x10c28fee0  session: 0x10c51e470  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:42,320 - logic_logger - INFO
..Item[None] {Insert - client} id: None, order_id: None, product_id: None, quantity: 1, amount: None, unit_price: None  row: 0x10cba3550  session: 0x10c51e470  ins_upd_dlt: ins, initial: ins - 2026-11-19 17:41:42,320 - logic_logger - INFO
..Item[None] {copy_rules for role: product - unit_price} id: None, order_id: None, product_id: None, quantity: 1, amount: None, unit_price: 90.0000000000  row: 0x10cba3550  session: 0x10c51e470  ins_upd_dlt: ins, initial: ins - 2026-11-19 17:41:42,320 - logic_logger - INFO
..Item[None] {Formula amount} id: None, order_id: None, product_id: None, quantity: 1, amount: 90.0000000000, unit_price: 90.0000000000  row: 0x10cba3550  session: 0x10c51e470  ins_upd_dlt: ins, initial: ins - 2026-11-19 17:41:42,320 - logic_logger - INFO
....Order[None] {Update - Adjusting order: amount_total} id: None, notes: behave test, customer_id: 25, CreatedOn: 2026-11-19, date_shipped: None, amount_total:  [0-->] 90.0000000000, CreatedOnDay: 2026-11-19  row: 0x10c4cf140  session: 0x10c51e470  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:42,320 - logic_logger - INFO
......DailyFlow[2026-11-19] {Update - Adjusting daily_flow: order_amount} day: 2026-11-19, order_count: 14, order_amount:  [2850.00-->] 2940.0000000000, message_received: 1, message_processed: 1, message_failed: 0, message_stuck: 0, request_received: 17, request_processed: 14, request_failed: 3, request_stuck: 0  row: 0x10c28fee0  session: 0x10c51e470  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:42,320 - logic_logger - INFO
......DailyFlow[2026-11-19] {Prune Formula: message_stuck [['message_received', 'message_processed', 'message_failed']]} day: 2026-11-19, order_count: 14, order_amount:  [2850.00-->] 2940.0000000000, message_received: 1, message_processed: 1, message_failed: 0, message_stuck: 0, request_received: 17, request_processed: 14, request_failed: 3, request_stuck: 0  row: 0x10c28fee0  session: 0x10c51e470  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:42,320 - logic_logger - INFO
......DailyFlow[2026-11-19] {Prune Formula: request_stuck [['request_received', 'request_processed', 'request_failed']]} day: 2026-11-19, order_count: 14, order_amount:  [2850.00-->] 2940.0000000000, message_received: 1, message_processed: 1, message_failed: 0, message_stuck: 0, request_received: 17, request_processed: 14, request_failed: 3, request_stuck: 0  row: 0x10c28fee0  session: 0x10c51e470  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:42,320 - logic_logger - INFO
......Customer[25] {Update - Adjusting customer: balance} id: 25, name: Gina 1795138902312, balance:  [0E-10-->] 90.0000000000, credit_limit: 5000.0000000000, email: None, email_opt_out: None  row: 0x10cba38d0  session: 0x10c51e470  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:42,320 - logic_logger - INFO
Logic Phase:		COMMIT LOGIC		(session=0x10c51e470)   										 - 2026-11-19 17:41:42,320 - logic_logger - INFO
Logic Phase:		AFTER_FLUSH LOGIC	(session=0x10c51e470)   										 - 2026-11-19 17:41:42,321 - logic_logger - INFO
..Order[172] {AfterFlush Event} id: 172, notes: behave test, customer_id: 25, CreatedOn: 2026-11-19, date_shipped: None, amount_total: 90.0000000000, CreatedOnDay: 2026-11-19  row: 0x10c4cf140  session: 0x10c51e470  ins_upd_dlt: ins, initial: ins - 2026-11-19 17:41:42,321 - logic_logger - INFO


Logic Phase:		ROW LOGIC		(session=0x10c51df20) (sqlalchemy before_flush)			 - 2026-11-19 17:41:42,324 - logic_logger - INFO
..Order[172] {Update - client} id: 172, notes: behave test, customer_id: 25, CreatedOn: 2026-11-19, date_shipped:  [None-->] 2026-10-24 00:00:00, amount_total: 90.0000000000, CreatedOnDay: 2026-11-19  row: 0x10c6dae70  session: 0x10c51df20  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:42,324 - logic_logger - INFO
....Customer[25] {Update - Adjusting customer: balance} id: 25, name: Gina 1795138902312, balance:  [90.0000000000-->] 0E-10, credit_limit: 5000.0000000000, email: None, email_opt_out: None  row: 0x10cb4e150  session: 0x10c51df20  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:42,324 - logic_logger - INFO
Logic Phase:		COMMIT LOGIC		(session=0x10c51df20)   										 - 2026-11-19 17:41:42,324 - logic_logger - INFO
Logic Phase:		AFTER_FLUSH LOGIC	(session=0x10c51df20)   										 - 2026-11-19 17:41:42,324 - logic_logger - INFO
..Order[172] {AfterFlush Event} id: 172, notes: behave test, customer_id: 25, CreatedOn: 2026-11-19, date_shipped:  [None-->] 2026-10-24 00:00:00, amount_total: 90.0000000000, CreatedOnDay: 2026-11-19  row: 0x10c6dae70  session: 0x10c51df20  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:42,325 - logic_logger - INFO
..Order[172] {publish_kafka_message: topic='order_shipping', key={'id': 172}} id: 172, notes: behave test, customer_id: 25, CreatedOn: 2026-11-19, date_shipped:  [None-->] 2026-10-24 00:00:00, amount_total: 90.0000000000, CreatedOnDay: 2026-11-19  row: 0x10c6dae70  session: 0x10c51df20  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:42,327 - logic_logger - INFO

```
</details>

&nbsp;
&nbsp;

#### Scenario: Unshipped Order Not Published ✅ (0.01 s)
&emsp;  Scenario: Unshipped Order Not Published  
&emsp;&emsp;    Given Customer "Hal" with credit limit 5000  
&emsp;&emsp;    When B2B order placed for "Hal" with 1 Widget  
&emsp;&emsp;    Then no order_shipping message is published  

<details markdown>
<summary>Rules exercised and logic log (2 transactions)</summary>


&nbsp;
&nbsp;


**Rules Used** in Scenario: Unshipped Order Not Published
```
  DailyFlow  
    1. Derive DailyFlow.request_processed as Count(OrderB2bRequest Where Rule.count(derive=models.DailyFlow.request_processed, as_count_of=models.OrderB2bRequest, where=lambda row: row.is_processed == True, insert_parent=True), insert_parent)  
    2. Derive DailyFlow.request_failed as Count(OrderB2bRequest Where Rule.count(derive=models.DailyFlow.request_failed, as_count_of=models.OrderB2bRequest, where=lambda row: row.error_text is not None, insert_parent=True), insert_parent)  
    3. Derive DailyFlow.request_stuck as Formula (2): Rule.formula(derive=models.DailyFlow.request_stuc [...]  
    4. Derive DailyFlow.request_received as Count(OrderB2bRequest Where  - None, insert_parent)  
    5. Derive DailyFlow.order_amount as Sum(Order.amount_total Where  - None, insert_parent)  
    6. Derive DailyFlow.order_count as Count(Order Where  - None, insert_parent)  
  Customer  
    7. Derive Customer.balance as Sum(Order.amount_total Where Rule.sum(derive=models.Customer.balance, as_sum_of=models.Order.amount_total, where=lambda row: row.date_shipped is None))  
  Item  
    8. Derive Item.amount as Formula (1): Rule.formula(derive=models.Item.amount, as_expres [...]  
    9. Derive Item.unit_price as Copy(product.unit_price)  
  Order  
    10. RowEvent Order._send_order_to_shipping()  
    11. Derive Order.amount_total as Sum(Item.amount Where  - None)  
```
**Logic Log** in Scenario: Unshipped Order Not Published (2 transactions)
```
Logic Phase:		ROW LOGIC		(session=0x10c51d6a0) (sqlalchemy before_flush)			 - 2026-11-19 17:41:42,336 - logic_logger - INFO
..OrderB2bRequest[None] {Insert - client} id: None, CreatedOn: None, CreatedOnDay: None, payload: {"Account": "Hal 1795138902332", "Notes": "behave test", "Items": [{"Name": "Widget", "QuantityOrdered": 1}]}, is_processed: False, error_text: None  row: 0x10cba13d0  session: 0x10c51d6a0  ins_upd_dlt: ins, initial: ins - 2026-11-19 17:41:42,336 - logic_logger - INFO
..OrderB2bRequest[None] {early_row_event_all_classes - handle_all did stamping} id: None, CreatedOn: 2026-11-19 17:41:42.336507, CreatedOnDay: 2026-11-19, payload: {"Account": "Hal 1795138902332", "Notes": "behave test", "Items": [{"Name": "Widget", "QuantityOrdered": 1}]}, is_processed: False, error_text: None  row: 0x10cba13d0  session: 0x10c51d6a0  ins_upd_dlt: ins, initial: ins - 2026-11-19 17:41:42,336 - logic_logger - INFO
....DailyFlow[2026-11-19] {Update - Adjusting daily_flow: request_received} day: 2026-11-19, order_count: 14, order_amount: 2940.00, message_received: 1, message_processed: 1, message_failed: 0, message_stuck: 0, request_received:  [17-->] 18, request_processed: 14, request_failed: 3, request_stuck: 0  row: 0x10c616200  session: 0x10c51d6a0  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:42,336 - logic_logger - INFO
....DailyFlow[2026-11-19] {Prune Formula: message_stuck [['message_received', 'message_processed', 'message_failed']]} day: 2026-11-19, order_count: 14, order_amount: 2940.00, message_received: 1, message_processed: 1, message_failed: 0, message_stuck: 0, request_received:  [17-->] 18, request_processed: 14, request_failed: 3, request_stuck: 0  row: 0x10c616200  session: 0x10c51d6a0  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:42,336 - logic_logger - INFO
....DailyFlow[2026-11-19] {Formula request_stuck} day: 2026-11-19, order_count: 14, order_amount: 2940.00, message_received: 1, message_processed: 1, message_failed: 0, message_stuck: 0, request_received:  [17-->] 18, request_processed: 14, request_failed: 3, request_stuck:  [0-->] 1  row: 0x10c616200  session: 0x10c51d6a0  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:42,336 - logic_logger - INFO
Logic Phase:		COMMIT LOGIC		(session=0x10c51d6a0)   										 - 2026-11-19 17:41:42,337 - logic_logger - INFO
Logic Phase:		AFTER_FLUSH LOGIC	(session=0x10c51d6a0)   										 - 2026-11-19 17:41:42,337 - logic_logger - INFO


Logic Phase:		ROW LOGIC		(session=0x10c51d6a0) (sqlalchemy before_flush)			 - 2026-11-19 17:41:42,339 - logic_logger - INFO
..Product[2] {Update - client} id: 2, name: Widget, count_suppliers: 0, unit_price: 90.0000000000  row: 0x10cb27460  session: 0x10c51d6a0  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:42,339 - logic_logger - INFO
..OrderB2bRequest[78] {Update - client} id: 78, CreatedOn: 2026-11-19 17:41:42.336507, CreatedOnDay: 2026-11-19, payload: {"Account": "Hal 1795138902332", "Notes": "behave test", "Items": [{"Name": "Widget", "QuantityOrdered": 1}]}, is_processed:  [False-->] True, error_text: None  row: 0x10cba13d0  session: 0x10c51d6a0  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:42,339 - logic_logger - INFO
....DailyFlow[2026-11-19] {Update - Adjusting daily_flow: request_processed} day: 2026-11-19, order_count: 14, order_amount: 2940.00, message_received: 1, message_processed: 1, message_failed: 0, message_stuck: 0, request_received: 18, request_processed:  [14-->] 15, request_failed: 3, request_stuck: 1  row: 0x10c616200  session: 0x10c51d6a0  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:42,339 - logic_logger - INFO
....DailyFlow[2026-11-19] {Prune Formula: message_stuck [['message_received', 'message_processed', 'message_failed']]} day: 2026-11-19, order_count: 14, order_amount: 2940.00, message_received: 1, message_processed: 1, message_failed: 0, message_stuck: 0, request_received: 18, request_processed:  [14-->] 15, request_failed: 3, request_stuck: 1  row: 0x10c616200  session: 0x10c51d6a0  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:42,339 - logic_logger - INFO
....DailyFlow[2026-11-19] {Formula request_stuck} day: 2026-11-19, order_count: 14, order_amount: 2940.00, message_received: 1, message_processed: 1, message_failed: 0, message_stuck: 0, request_received: 18, request_processed:  [14-->] 15, request_failed: 3, request_stuck:  [1-->] 0  row: 0x10c616200  session: 0x10c51d6a0  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:42,339 - logic_logger - INFO
..Order[None] {Insert - client} id: None, notes: behave test, customer_id: 26, CreatedOn: None, date_shipped: None, amount_total: None, CreatedOnDay: None  row: 0x10c6daf00  session: 0x10c51d6a0  ins_upd_dlt: ins, initial: ins - 2026-11-19 17:41:42,339 - logic_logger - INFO
..Order[None] {early_row_event_all_classes - handle_all did stamping} id: None, notes: behave test, customer_id: 26, CreatedOn: 2026-11-19, date_shipped: None, amount_total: None, CreatedOnDay: 2026-11-19  row: 0x10c6daf00  session: 0x10c51d6a0  ins_upd_dlt: ins, initial: ins - 2026-11-19 17:41:42,339 - logic_logger - INFO
..Order[None] {server aggregate_defaults: amount_total } id: None, notes: behave test, customer_id: 26, CreatedOn: 2026-11-19, date_shipped: None, amount_total: 0, CreatedOnDay: 2026-11-19  row: 0x10c6daf00  session: 0x10c51d6a0  ins_upd_dlt: ins, initial: ins - 2026-11-19 17:41:42,339 - logic_logger - INFO
....DailyFlow[2026-11-19] {Update - Adjusting daily_flow: order_count} day: 2026-11-19, order_count:  [14-->] 15, order_amount: 2940.00, message_received: 1, message_processed: 1, message_failed: 0, message_stuck: 0, request_received: 18, request_processed: 15, request_failed: 3, request_stuck: 0  row: 0x10c616200  session: 0x10c51d6a0  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:42,339 - logic_logger - INFO
....DailyFlow[2026-11-19] {Prune Formula: message_stuck [['message_received', 'message_processed', 'message_failed']]} day: 2026-11-19, order_count:  [14-->] 15, order_amount: 2940.00, message_received: 1, message_processed: 1, message_failed: 0, message_stuck: 0, request_received: 18, request_processed: 15, request_failed: 3, request_stuck: 0  row: 0x10c616200  session: 0x10c51d6a0  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:42,340 - logic_logger - INFO
....DailyFlow[2026-11-19] {Prune Formula: request_stuck [['request_received', 'request_processed', 'request_failed']]} day: 2026-11-19, order_count:  [14-->] 15, order_amount: 2940.00, message_received: 1, message_processed: 1, message_failed: 0, message_stuck: 0, request_received: 18, request_processed: 15, request_failed: 3, request_stuck: 0  row: 0x10c616200  session: 0x10c51d6a0  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:42,340 - logic_logger - INFO
..Item[None] {Insert - client} id: None, order_id: None, product_id: None, quantity: 1, amount: None, unit_price: None  row: 0x10cba0e50  session: 0x10c51d6a0  ins_upd_dlt: ins, initial: ins - 2026-11-19 17:41:42,340 - logic_logger - INFO
..Item[None] {copy_rules for role: product - unit_price} id: None, order_id: None, product_id: None, quantity: 1, amount: None, unit_price: 90.0000000000  row: 0x10cba0e50  session: 0x10c51d6a0  ins_upd_dlt: ins, initial: ins - 2026-11-19 17:41:42,340 - logic_logger - INFO
..Item[None] {Formula amount} id: None, order_id: None, product_id: None, quantity: 1, amount: 90.0000000000, unit_price: 90.0000000000  row: 0x10cba0e50  session: 0x10c51d6a0  ins_upd_dlt: ins, initial: ins - 2026-11-19 17:41:42,340 - logic_logger - INFO
....Order[None] {Update - Adjusting order: amount_total} id: None, notes: behave test, customer_id: 26, CreatedOn: 2026-11-19, date_shipped: None, amount_total:  [0-->] 90.0000000000, CreatedOnDay: 2026-11-19  row: 0x10c6daf00  session: 0x10c51d6a0  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:42,340 - logic_logger - INFO
......DailyFlow[2026-11-19] {Update - Adjusting daily_flow: order_amount} day: 2026-11-19, order_count: 15, order_amount:  [2940.00-->] 3030.0000000000, message_received: 1, message_processed: 1, message_failed: 0, message_stuck: 0, request_received: 18, request_processed: 15, request_failed: 3, request_stuck: 0  row: 0x10c616200  session: 0x10c51d6a0  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:42,340 - logic_logger - INFO
......DailyFlow[2026-11-19] {Prune Formula: message_stuck [['message_received', 'message_processed', 'message_failed']]} day: 2026-11-19, order_count: 15, order_amount:  [2940.00-->] 3030.0000000000, message_received: 1, message_processed: 1, message_failed: 0, message_stuck: 0, request_received: 18, request_processed: 15, request_failed: 3, request_stuck: 0  row: 0x10c616200  session: 0x10c51d6a0  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:42,340 - logic_logger - INFO
......DailyFlow[2026-11-19] {Prune Formula: request_stuck [['request_received', 'request_processed', 'request_failed']]} day: 2026-11-19, order_count: 15, order_amount:  [2940.00-->] 3030.0000000000, message_received: 1, message_processed: 1, message_failed: 0, message_stuck: 0, request_received: 18, request_processed: 15, request_failed: 3, request_stuck: 0  row: 0x10c616200  session: 0x10c51d6a0  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:42,340 - logic_logger - INFO
......Customer[26] {Update - Adjusting customer: balance} id: 26, name: Hal 1795138902332, balance:  [0E-10-->] 90.0000000000, credit_limit: 5000.0000000000, email: None, email_opt_out: None  row: 0x10cba10d0  session: 0x10c51d6a0  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:42,340 - logic_logger - INFO
Logic Phase:		COMMIT LOGIC		(session=0x10c51d6a0)   										 - 2026-11-19 17:41:42,340 - logic_logger - INFO
Logic Phase:		AFTER_FLUSH LOGIC	(session=0x10c51d6a0)   										 - 2026-11-19 17:41:42,341 - logic_logger - INFO
..Order[173] {AfterFlush Event} id: 173, notes: behave test, customer_id: 26, CreatedOn: 2026-11-19, date_shipped: None, amount_total: 90.0000000000, CreatedOnDay: 2026-11-19  row: 0x10c6daf00  session: 0x10c51d6a0  ins_upd_dlt: ins, initial: ins - 2026-11-19 17:41:42,341 - logic_logger - INFO

```
</details>

&nbsp;
&nbsp;

### Feature: Kafka Subscribe Order Integration  

&nbsp;
&nbsp;

#### Scenario: Order Message Delivered ✅ (0.53 s)
&emsp;  Scenario: Order Message Delivered  
&emsp;&emsp;    Given Customer "Quinn" with credit limit 5000  
&emsp;&emsp;    When an inbound order message for "Quinn" with 1 Widget and 2 Gadget is delivered to topic order_b2b  
&emsp;&emsp;    Then the message is processed  
&emsp;&emsp;    And the Customer's newest order has 2 items totaling 390  
&emsp;&emsp;    And Customer balance should be 390  

<details markdown>
<summary>Rules exercised and logic log (3 transactions)</summary>


&nbsp;
&nbsp;


**Rules Used** in Scenario: Order Message Delivered
```
  DailyFlow  
    1. Derive DailyFlow.message_failed as Count(OrderB2bMessage Where Rule.count(derive=models.DailyFlow.message_failed, as_count_of=models.OrderB2bMessage, where=lambda row: row.error_text is not None, insert_parent=True), insert_parent)  
    2. Derive DailyFlow.message_stuck as Formula (1): Rule.formula(derive=models.DailyFlow.message_stuc [...]  
    3. Derive DailyFlow.message_received as Count(OrderB2bMessage Where  - None, insert_parent)  
    4. Derive DailyFlow.message_processed as Count(OrderB2bMessage Where Rule.count(derive=models.DailyFlow.message_processed, as_count_of=models.OrderB2bMessage, where=lambda row: row.is_processed == True, insert_parent=True), insert_parent)  
    5. Derive DailyFlow.order_amount as Sum(Order.amount_total Where  - None, insert_parent)  
    6. Derive DailyFlow.order_count as Count(Order Where  - None, insert_parent)  
  OrderB2bMessage  
    7. RowEvent OrderB2bMessage._publish_order_b2b()  
  Customer  
    8. Derive Customer.balance as Sum(Order.amount_total Where Rule.sum(derive=models.Customer.balance, as_sum_of=models.Order.amount_total, where=lambda row: row.date_shipped is None))  
  Item  
    9. Derive Item.amount as Formula (1): Rule.formula(derive=models.Item.amount, as_expres [...]  
    10. Derive Item.unit_price as Copy(product.unit_price)  
  Order  
    11. RowEvent Order._send_order_to_shipping()  
    12. Derive Order.amount_total as Sum(Item.amount Where  - None)  
```
**Logic Log** in Scenario: Order Message Delivered (3 transactions)
```
Logic Phase:		ROW LOGIC		(session=0x10c51d260) (sqlalchemy before_flush)			 - 2026-11-19 17:41:42,350 - logic_logger - INFO
..OrderB2bMessage[None] {Insert - client} id: None, received_at: 2026-11-19 17:41:42.350158, payload: {"Account": "Quinn 1795138902344", "Notes": "behave kafka test", "Items": [{"Name": "Widget", "QuantityOrdered": 1}, {"Name": "Gadget", "QuantityOrdered": 2}]}, is_processed: False, error_text: None, CreatedOn: None, CreatedOnDay: None  row: 0x10c6db020  session: 0x10c51d260  ins_upd_dlt: ins, initial: ins - 2026-11-19 17:41:42,350 - logic_logger - INFO
..OrderB2bMessage[None] {early_row_event_all_classes - handle_all did stamping} id: None, received_at: 2026-11-19 17:41:42.350158, payload: {"Account": "Quinn 1795138902344", "Notes": "behave kafka test", "Items": [{"Name": "Widget", "QuantityOrdered": 1}, {"Name": "Gadget", "QuantityOrdered": 2}]}, is_processed: False, error_text: None, CreatedOn: 2026-11-19 17:41:42.350451, CreatedOnDay: 2026-11-19  row: 0x10c6db020  session: 0x10c51d260  ins_upd_dlt: ins, initial: ins - 2026-11-19 17:41:42,350 - logic_logger - INFO
....DailyFlow[2026-11-19] {Update - Adjusting daily_flow: message_received} day: 2026-11-19, order_count: 15, order_amount: 3030.00, message_received:  [1-->] 2, message_processed: 1, message_failed: 0, message_stuck: 0, request_received: 18, request_processed: 15, request_failed: 3, request_stuck: 0  row: 0x10c28c100  session: 0x10c51d260  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:42,350 - logic_logger - INFO
....DailyFlow[2026-11-19] {Formula message_stuck} day: 2026-11-19, order_count: 15, order_amount: 3030.00, message_received:  [1-->] 2, message_processed: 1, message_failed: 0, message_stuck:  [0-->] 1, request_received: 18, request_processed: 15, request_failed: 3, request_stuck: 0  row: 0x10c28c100  session: 0x10c51d260  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:42,350 - logic_logger - INFO
....DailyFlow[2026-11-19] {Prune Formula: request_stuck [['request_received', 'request_processed', 'request_failed']]} day: 2026-11-19, order_count: 15, order_amount: 3030.00, message_received:  [1-->] 2, message_processed: 1, message_failed: 0, message_stuck:  [0-->] 1, request_received: 18, request_processed: 15, request_failed: 3, request_stuck: 0  row: 0x10c28c100  session: 0x10c51d260  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:42,351 - logic_logger - INFO
Logic Phase:		COMMIT LOGIC		(session=0x10c51d260)   										 - 2026-11-19 17:41:42,351 - logic_logger - INFO
Logic Phase:		AFTER_FLUSH LOGIC	(session=0x10c51d260)   										 - 2026-11-19 17:41:42,353 - logic_logger - INFO
..OrderB2bMessage[110] {AfterFlush Event} id: 110, received_at: 2026-11-19 17:41:42.350158, payload: {"Account": "Quinn 1795138902344", "Notes": "behave kafka test", "Items": [{"Name": "Widget", "QuantityOrdered": 1}, {"Name": "Gadget", "QuantityOrdered": 2}]}, is_processed: False, error_text: None, CreatedOn: 2026-11-19 17:41:42.350451, CreatedOnDay: 2026-11-19  row: 0x10c6db020  session: 0x10c51d260  ins_upd_dlt: ins, initial: ins - 2026-11-19 17:41:42,353 - logic_logger - INFO


Logic Phase:		ROW LOGIC		(session=0x10c51d6a0) (sqlalchemy before_flush)			 - 2026-11-19 17:41:42,359 - logic_logger - INFO
..Order[None] {Insert - client} id: None, notes: behave kafka test, customer_id: 27, CreatedOn: None, date_shipped: None, amount_total: None, CreatedOnDay: None  row: 0x10c6d9760  session: 0x10c51d6a0  ins_upd_dlt: ins, initial: ins - 2026-11-19 17:41:42,359 - logic_logger - INFO
..Order[None] {early_row_event_all_classes - handle_all did stamping} id: None, notes: behave kafka test, customer_id: 27, CreatedOn: 2026-11-19, date_shipped: None, amount_total: None, CreatedOnDay: 2026-11-19  row: 0x10c6d9760  session: 0x10c51d6a0  ins_upd_dlt: ins, initial: ins - 2026-11-19 17:41:42,359 - logic_logger - INFO
..Order[None] {server aggregate_defaults: amount_total } id: None, notes: behave kafka test, customer_id: 27, CreatedOn: 2026-11-19, date_shipped: None, amount_total: 0, CreatedOnDay: 2026-11-19  row: 0x10c6d9760  session: 0x10c51d6a0  ins_upd_dlt: ins, initial: ins - 2026-11-19 17:41:42,359 - logic_logger - INFO
....DailyFlow[2026-11-19] {Update - Adjusting daily_flow: order_count} day: 2026-11-19, order_count:  [15-->] 16, order_amount: 3030.00, message_received: 2, message_processed: 1, message_failed: 0, message_stuck: 1, request_received: 18, request_processed: 15, request_failed: 3, request_stuck: 0  row: 0x10c28e4c0  session: 0x10c51d6a0  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:42,359 - logic_logger - INFO
....DailyFlow[2026-11-19] {Prune Formula: message_stuck [['message_received', 'message_processed', 'message_failed']]} day: 2026-11-19, order_count:  [15-->] 16, order_amount: 3030.00, message_received: 2, message_processed: 1, message_failed: 0, message_stuck: 1, request_received: 18, request_processed: 15, request_failed: 3, request_stuck: 0  row: 0x10c28e4c0  session: 0x10c51d6a0  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:42,359 - logic_logger - INFO
....DailyFlow[2026-11-19] {Prune Formula: request_stuck [['request_received', 'request_processed', 'request_failed']]} day: 2026-11-19, order_count:  [15-->] 16, order_amount: 3030.00, message_received: 2, message_processed: 1, message_failed: 0, message_stuck: 1, request_received: 18, request_processed: 15, request_failed: 3, request_stuck: 0  row: 0x10c28e4c0  session: 0x10c51d6a0  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:42,359 - logic_logger - INFO
..Item[None] {Insert - client} id: None, order_id: None, product_id: 2, quantity: 1, amount: None, unit_price: None  row: 0x10cb4d3d0  session: 0x10c51d6a0  ins_upd_dlt: ins, initial: ins - 2026-11-19 17:41:42,360 - logic_logger - INFO
..Item[None] {copy_rules for role: product - unit_price} id: None, order_id: None, product_id: 2, quantity: 1, amount: None, unit_price: 90.0000000000  row: 0x10cb4d3d0  session: 0x10c51d6a0  ins_upd_dlt: ins, initial: ins - 2026-11-19 17:41:42,360 - logic_logger - INFO
..Item[None] {Formula amount} id: None, order_id: None, product_id: 2, quantity: 1, amount: 90.0000000000, unit_price: 90.0000000000  row: 0x10cb4d3d0  session: 0x10c51d6a0  ins_upd_dlt: ins, initial: ins - 2026-11-19 17:41:42,360 - logic_logger - INFO
....Order[None] {Update - Adjusting order: amount_total} id: None, notes: behave kafka test, customer_id: 27, CreatedOn: 2026-11-19, date_shipped: None, amount_total:  [0-->] 90.0000000000, CreatedOnDay: 2026-11-19  row: 0x10c6d9760  session: 0x10c51d6a0  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:42,360 - logic_logger - INFO
......DailyFlow[2026-11-19] {Update - Adjusting daily_flow: order_amount} day: 2026-11-19, order_count: 16, order_amount:  [3030.00-->] 3120.0000000000, message_received: 2, message_processed: 1, message_failed: 0, message_stuck: 1, request_received: 18, request_processed: 15, request_failed: 3, request_stuck: 0  row: 0x10c28e4c0  session: 0x10c51d6a0  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:42,360 - logic_logger - INFO
......DailyFlow[2026-11-19] {Prune Formula: message_stuck [['message_received', 'message_processed', 'message_failed']]} day: 2026-11-19, order_count: 16, order_amount:  [3030.00-->] 3120.0000000000, message_received: 2, message_processed: 1, message_failed: 0, message_stuck: 1, request_received: 18, request_processed: 15, request_failed: 3, request_stuck: 0  row: 0x10c28e4c0  session: 0x10c51d6a0  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:42,360 - logic_logger - INFO
......DailyFlow[2026-11-19] {Prune Formula: request_stuck [['request_received', 'request_processed', 'request_failed']]} day: 2026-11-19, order_count: 16, order_amount:  [3030.00-->] 3120.0000000000, message_received: 2, message_processed: 1, message_failed: 0, message_stuck: 1, request_received: 18, request_processed: 15, request_failed: 3, request_stuck: 0  row: 0x10c28e4c0  session: 0x10c51d6a0  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:42,360 - logic_logger - INFO
......Customer[27] {Update - Adjusting customer: balance} id: 27, name: Quinn 1795138902344, balance:  [0E-10-->] 90.0000000000, credit_limit: 5000.0000000000, email: None, email_opt_out: None  row: 0x10cba1fd0  session: 0x10c51d6a0  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:42,360 - logic_logger - INFO
..Item[None] {Insert - client} id: None, order_id: None, product_id: 1, quantity: 2, amount: None, unit_price: None  row: 0x10cb4e650  session: 0x10c51d6a0  ins_upd_dlt: ins, initial: ins - 2026-11-19 17:41:42,360 - logic_logger - INFO
..Item[None] {copy_rules for role: product - unit_price} id: None, order_id: None, product_id: 1, quantity: 2, amount: None, unit_price: 150.0000000000  row: 0x10cb4e650  session: 0x10c51d6a0  ins_upd_dlt: ins, initial: ins - 2026-11-19 17:41:42,361 - logic_logger - INFO
..Item[None] {Formula amount} id: None, order_id: None, product_id: 1, quantity: 2, amount: 300.0000000000, unit_price: 150.0000000000  row: 0x10cb4e650  session: 0x10c51d6a0  ins_upd_dlt: ins, initial: ins - 2026-11-19 17:41:42,361 - logic_logger - INFO
....Order[None] {Update - Adjusting order: amount_total} id: None, notes: behave kafka test, customer_id: 27, CreatedOn: 2026-11-19, date_shipped: None, amount_total:  [90.0000000000-->] 390.0000000000, CreatedOnDay: 2026-11-19  row: 0x10c6d9760  session: 0x10c51d6a0  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:42,361 - logic_logger - INFO
......DailyFlow[2026-11-19] {Update - Adjusting daily_flow: order_amount} day: 2026-11-19, order_count: 16, order_amount:  [3120.0000000000-->] 3420.0000000000, message_received: 2, message_processed: 1, message_failed: 0, message_stuck: 1, request_received: 18, request_processed: 15, request_failed: 3, request_stuck: 0  row: 0x10c28e4c0  session: 0x10c51d6a0  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:42,361 - logic_logger - INFO
......DailyFlow[2026-11-19] {Prune Formula: message_stuck [['message_received', 'message_processed', 'message_failed']]} day: 2026-11-19, order_count: 16, order_amount:  [3120.0000000000-->] 3420.0000000000, message_received: 2, message_processed: 1, message_failed: 0, message_stuck: 1, request_received: 18, request_processed: 15, request_failed: 3, request_stuck: 0  row: 0x10c28e4c0  session: 0x10c51d6a0  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:42,361 - logic_logger - INFO
......DailyFlow[2026-11-19] {Prune Formula: request_stuck [['request_received', 'request_processed', 'request_failed']]} day: 2026-11-19, order_count: 16, order_amount:  [3120.0000000000-->] 3420.0000000000, message_received: 2, message_processed: 1, message_failed: 0, message_stuck: 1, request_received: 18, request_processed: 15, request_failed: 3, request_stuck: 0  row: 0x10c28e4c0  session: 0x10c51d6a0  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:42,361 - logic_logger - INFO
......Customer[27] {Update - Adjusting customer: balance} id: 27, name: Quinn 1795138902344, balance:  [90.0000000000-->] 390.0000000000, credit_limit: 5000.0000000000, email: None, email_opt_out: None  row: 0x10cba1fd0  session: 0x10c51d6a0  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:42,361 - logic_logger - INFO
Logic Phase:		COMMIT LOGIC		(session=0x10c51d6a0)   										 - 2026-11-19 17:41:42,361 - logic_logger - INFO
Logic Phase:		AFTER_FLUSH LOGIC	(session=0x10c51d6a0)   										 - 2026-11-19 17:41:42,362 - logic_logger - INFO
..Order[174] {AfterFlush Event} id: 174, notes: behave kafka test, customer_id: 27, CreatedOn: 2026-11-19, date_shipped: None, amount_total: 390.0000000000, CreatedOnDay: 2026-11-19  row: 0x10c6d9760  session: 0x10c51d6a0  ins_upd_dlt: ins, initial: ins - 2026-11-19 17:41:42,362 - logic_logger - INFO


Logic Phase:		ROW LOGIC		(session=0x10c51d6a0) (sqlalchemy before_flush)			 - 2026-11-19 17:41:42,362 - logic_logger - INFO
..OrderB2bMessage[110] {Update - client} id: 110, received_at: 2026-11-19 17:41:42.350158, payload: {"Account": "Quinn 1795138902344", "Notes": "behave kafka test", "Items": [{"Name": "Widget", "QuantityOrdered": 1}, {"Name": "Gadget", "QuantityOrdered": 2}]}, is_processed:  [False-->] True, error_text: None, CreatedOn: 2026-11-19 17:41:42.350451, CreatedOnDay: 2026-11-19  row: 0x10c6db5c0  session: 0x10c51d6a0  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:42,363 - logic_logger - INFO
....DailyFlow[2026-11-19] {Update - Adjusting daily_flow: message_processed} day: 2026-11-19, order_count: 16, order_amount: 3420.0000000000, message_received: 2, message_processed:  [1-->] 2, message_failed: 0, message_stuck: 1, request_received: 18, request_processed: 15, request_failed: 3, request_stuck: 0  row: 0x10c28e4c0  session: 0x10c51d6a0  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:42,363 - logic_logger - INFO
....DailyFlow[2026-11-19] {Formula message_stuck} day: 2026-11-19, order_count: 16, order_amount: 3420.0000000000, message_received: 2, message_processed:  [1-->] 2, message_failed: 0, message_stuck:  [1-->] 0, request_received: 18, request_processed: 15, request_failed: 3, request_stuck: 0  row: 0x10c28e4c0  session: 0x10c51d6a0  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:42,363 - logic_logger - INFO
....DailyFlow[2026-11-19] {Prune Formula: request_stuck [['request_received', 'request_processed', 'request_failed']]} day: 2026-11-19, order_count: 16, order_amount: 3420.0000000000, message_received: 2, message_processed:  [1-->] 2, message_failed: 0, message_stuck:  [1-->] 0, request_received: 18, request_processed: 15, request_failed: 3, request_stuck: 0  row: 0x10c28e4c0  session: 0x10c51d6a0  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:42,363 - logic_logger - INFO
Logic Phase:		COMMIT LOGIC		(session=0x10c51d6a0)   										 - 2026-11-19 17:41:42,363 - logic_logger - INFO
Logic Phase:		AFTER_FLUSH LOGIC	(session=0x10c51d6a0)   										 - 2026-11-19 17:41:42,363 - logic_logger - INFO
..OrderB2bMessage[110] {AfterFlush Event} id: 110, received_at: 2026-11-19 17:41:42.350158, payload: {"Account": "Quinn 1795138902344", "Notes": "behave kafka test", "Items": [{"Name": "Widget", "QuantityOrdered": 1}, {"Name": "Gadget", "QuantityOrdered": 2}]}, is_processed:  [False-->] True, error_text: None, CreatedOn: 2026-11-19 17:41:42.350451, CreatedOnDay: 2026-11-19  row: 0x10c6db5c0  session: 0x10c51d6a0  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:42,363 - logic_logger - INFO

```
</details>

&nbsp;
&nbsp;

#### Scenario: Unknown Account Message Rejected ✅ (0.53 s)
&emsp;  Scenario: Unknown Account Message Rejected  
&emsp;&emsp;    When an inbound order message for an unknown account is delivered to topic order_b2b  
&emsp;&emsp;    Then the message is rejected with "no Customer found"  

<details markdown>
<summary>Rules exercised and logic log (2 transactions)</summary>


&nbsp;
&nbsp;


**Rules Used** in Scenario: Unknown Account Message Rejected
```
  DailyFlow  
    1. Derive DailyFlow.message_failed as Count(OrderB2bMessage Where Rule.count(derive=models.DailyFlow.message_failed, as_count_of=models.OrderB2bMessage, where=lambda row: row.error_text is not None, insert_parent=True), insert_parent)  
    2. Derive DailyFlow.message_stuck as Formula (1): Rule.formula(derive=models.DailyFlow.message_stuc [...]  
    3. Derive DailyFlow.message_received as Count(OrderB2bMessage Where  - None, insert_parent)  
    4. Derive DailyFlow.message_processed as Count(OrderB2bMessage Where Rule.count(derive=models.DailyFlow.message_processed, as_count_of=models.OrderB2bMessage, where=lambda row: row.is_processed == True, insert_parent=True), insert_parent)  
  OrderB2bMessage  
    5. RowEvent OrderB2bMessage._publish_order_b2b()  
```
**Logic Log** in Scenario: Unknown Account Message Rejected (2 transactions)
```
Logic Phase:		ROW LOGIC		(session=0x10c51d590) (sqlalchemy before_flush)			 - 2026-11-19 17:41:42,882 - logic_logger - INFO
..OrderB2bMessage[None] {Insert - client} id: None, received_at: 2026-11-19 17:41:42.882545, payload: {"Account": "Nobody 1795138902879", "Notes": "behave kafka test", "Items": [{"Name": "Widget", "QuantityOrdered": 1}]}, is_processed: False, error_text: None, CreatedOn: None, CreatedOnDay: None  row: 0x10c4cdbe0  session: 0x10c51d590  ins_upd_dlt: ins, initial: ins - 2026-11-19 17:41:42,883 - logic_logger - INFO
..OrderB2bMessage[None] {early_row_event_all_classes - handle_all did stamping} id: None, received_at: 2026-11-19 17:41:42.882545, payload: {"Account": "Nobody 1795138902879", "Notes": "behave kafka test", "Items": [{"Name": "Widget", "QuantityOrdered": 1}]}, is_processed: False, error_text: None, CreatedOn: 2026-11-19 17:41:42.883063, CreatedOnDay: 2026-11-19  row: 0x10c4cdbe0  session: 0x10c51d590  ins_upd_dlt: ins, initial: ins - 2026-11-19 17:41:42,883 - logic_logger - INFO
....DailyFlow[2026-11-19] {Update - Adjusting daily_flow: message_received} day: 2026-11-19, order_count: 16, order_amount: 3420.00, message_received:  [2-->] 3, message_processed: 2, message_failed: 0, message_stuck: 0, request_received: 18, request_processed: 15, request_failed: 3, request_stuck: 0  row: 0x10c28e570  session: 0x10c51d590  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:42,883 - logic_logger - INFO
....DailyFlow[2026-11-19] {Formula message_stuck} day: 2026-11-19, order_count: 16, order_amount: 3420.00, message_received:  [2-->] 3, message_processed: 2, message_failed: 0, message_stuck:  [0-->] 1, request_received: 18, request_processed: 15, request_failed: 3, request_stuck: 0  row: 0x10c28e570  session: 0x10c51d590  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:42,883 - logic_logger - INFO
....DailyFlow[2026-11-19] {Prune Formula: request_stuck [['request_received', 'request_processed', 'request_failed']]} day: 2026-11-19, order_count: 16, order_amount: 3420.00, message_received:  [2-->] 3, message_processed: 2, message_failed: 0, message_stuck:  [0-->] 1, request_received: 18, request_processed: 15, request_failed: 3, request_stuck: 0  row: 0x10c28e570  session: 0x10c51d590  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:42,883 - logic_logger - INFO
Logic Phase:		COMMIT LOGIC		(session=0x10c51d590)   										 - 2026-11-19 17:41:42,883 - logic_logger - INFO
Logic Phase:		AFTER_FLUSH LOGIC	(session=0x10c51d590)   										 - 2026-11-19 17:41:42,885 - logic_logger - INFO
..OrderB2bMessage[111] {AfterFlush Event} id: 111, received_at: 2026-11-19 17:41:42.882545, payload: {"Account": "Nobody 1795138902879", "Notes": "behave kafka test", "Items": [{"Name": "Widget", "QuantityOrdered": 1}]}, is_processed: False, error_text: None, CreatedOn: 2026-11-19 17:41:42.883063, CreatedOnDay: 2026-11-19  row: 0x10c4cdbe0  session: 0x10c51d590  ins_upd_dlt: ins, initial: ins - 2026-11-19 17:41:42,885 - logic_logger - INFO


Logic Phase:		ROW LOGIC		(session=0x10c51ff00) (sqlalchemy before_flush)			 - 2026-11-19 17:41:42,892 - logic_logger - INFO
..OrderB2bMessage[111] {Update - client} id: 111, received_at: 2026-11-19 17:41:42.882545, payload: {"Account": "Nobody 1795138902879", "Notes": "behave kafka test", "Items": [{"Name": "Widget", "QuantityOrdered": 1}]}, is_processed: False, error_text:  [None-->] resolve_lookups: no Customer found for fk_col='customer_id' from source fields, CreatedOn: 2026-11-19 17:41:42.883063, CreatedOnDay: 2026-11-19  row: 0x10cbf8b00  session: 0x10c51ff00  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:42,892 - logic_logger - INFO
....DailyFlow[2026-11-19] {Update - Adjusting daily_flow: message_failed} day: 2026-11-19, order_count: 16, order_amount: 3420.00, message_received: 3, message_processed: 2, message_failed:  [0-->] 1, message_stuck: 1, request_received: 18, request_processed: 15, request_failed: 3, request_stuck: 0  row: 0x10c6159c0  session: 0x10c51ff00  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:42,892 - logic_logger - INFO
....DailyFlow[2026-11-19] {Formula message_stuck} day: 2026-11-19, order_count: 16, order_amount: 3420.00, message_received: 3, message_processed: 2, message_failed:  [0-->] 1, message_stuck:  [1-->] 0, request_received: 18, request_processed: 15, request_failed: 3, request_stuck: 0  row: 0x10c6159c0  session: 0x10c51ff00  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:42,892 - logic_logger - INFO
....DailyFlow[2026-11-19] {Prune Formula: request_stuck [['request_received', 'request_processed', 'request_failed']]} day: 2026-11-19, order_count: 16, order_amount: 3420.00, message_received: 3, message_processed: 2, message_failed:  [0-->] 1, message_stuck:  [1-->] 0, request_received: 18, request_processed: 15, request_failed: 3, request_stuck: 0  row: 0x10c6159c0  session: 0x10c51ff00  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:42,892 - logic_logger - INFO
Logic Phase:		COMMIT LOGIC		(session=0x10c51ff00)   										 - 2026-11-19 17:41:42,893 - logic_logger - INFO
Logic Phase:		AFTER_FLUSH LOGIC	(session=0x10c51ff00)   										 - 2026-11-19 17:41:42,893 - logic_logger - INFO
..OrderB2bMessage[111] {AfterFlush Event} id: 111, received_at: 2026-11-19 17:41:42.882545, payload: {"Account": "Nobody 1795138902879", "Notes": "behave kafka test", "Items": [{"Name": "Widget", "QuantityOrdered": 1}]}, is_processed: False, error_text:  [None-->] resolve_lookups: no Customer found for fk_col='customer_id' from source fields, CreatedOn: 2026-11-19 17:41:42.883063, CreatedOnDay: 2026-11-19  row: 0x10cbf8b00  session: 0x10c51ff00  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:42,893 - logic_logger - INFO

```
</details>

&nbsp;
&nbsp;

#### Scenario: Rejected Message Keeps Its Error (live Kafka only) ✅ (0.53 s)
&emsp;  Scenario: Rejected Message Keeps Its Error (live Kafka only)  
&emsp;&emsp;    When an inbound order message for an unknown account is delivered live to topic order_b2b  
&emsp;&emsp;    Then the message row keeps is_processed false and its error_text  

<details markdown>
<summary>Rules exercised and logic log (2 transactions)</summary>


&nbsp;
&nbsp;


**Rules Used** in Scenario: Rejected Message Keeps Its Error (live Kafka only)
```
  DailyFlow  
    1. Derive DailyFlow.message_failed as Count(OrderB2bMessage Where Rule.count(derive=models.DailyFlow.message_failed, as_count_of=models.OrderB2bMessage, where=lambda row: row.error_text is not None, insert_parent=True), insert_parent)  
    2. Derive DailyFlow.message_stuck as Formula (1): Rule.formula(derive=models.DailyFlow.message_stuc [...]  
    3. Derive DailyFlow.message_received as Count(OrderB2bMessage Where  - None, insert_parent)  
    4. Derive DailyFlow.message_processed as Count(OrderB2bMessage Where Rule.count(derive=models.DailyFlow.message_processed, as_count_of=models.OrderB2bMessage, where=lambda row: row.is_processed == True, insert_parent=True), insert_parent)  
  OrderB2bMessage  
    5. RowEvent OrderB2bMessage._publish_order_b2b()  
```
**Logic Log** in Scenario: Rejected Message Keeps Its Error (live Kafka only) (2 transactions)
```
Logic Phase:		ROW LOGIC		(session=0x10c51df20) (sqlalchemy before_flush)			 - 2026-11-19 17:41:43,411 - logic_logger - INFO
..OrderB2bMessage[None] {Insert - client} id: None, received_at: 2026-11-19 17:41:43.411131, payload: {"Account": "Nobody 1795138903406", "Notes": "behave kafka test", "Items": [{"Name": "Widget", "QuantityOrdered": 1}]}, is_processed: False, error_text: None, CreatedOn: None, CreatedOnDay: None  row: 0x10cbf87a0  session: 0x10c51df20  ins_upd_dlt: ins, initial: ins - 2026-11-19 17:41:43,411 - logic_logger - INFO
..OrderB2bMessage[None] {early_row_event_all_classes - handle_all did stamping} id: None, received_at: 2026-11-19 17:41:43.411131, payload: {"Account": "Nobody 1795138903406", "Notes": "behave kafka test", "Items": [{"Name": "Widget", "QuantityOrdered": 1}]}, is_processed: False, error_text: None, CreatedOn: 2026-11-19 17:41:43.411861, CreatedOnDay: 2026-11-19  row: 0x10cbf87a0  session: 0x10c51df20  ins_upd_dlt: ins, initial: ins - 2026-11-19 17:41:43,411 - logic_logger - INFO
....DailyFlow[2026-11-19] {Update - Adjusting daily_flow: message_received} day: 2026-11-19, order_count: 16, order_amount: 3420.00, message_received:  [3-->] 4, message_processed: 2, message_failed: 1, message_stuck: 0, request_received: 18, request_processed: 15, request_failed: 3, request_stuck: 0  row: 0x10c615910  session: 0x10c51df20  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:43,413 - logic_logger - INFO
....DailyFlow[2026-11-19] {Formula message_stuck} day: 2026-11-19, order_count: 16, order_amount: 3420.00, message_received:  [3-->] 4, message_processed: 2, message_failed: 1, message_stuck:  [0-->] 1, request_received: 18, request_processed: 15, request_failed: 3, request_stuck: 0  row: 0x10c615910  session: 0x10c51df20  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:43,416 - logic_logger - INFO
....DailyFlow[2026-11-19] {Prune Formula: request_stuck [['request_received', 'request_processed', 'request_failed']]} day: 2026-11-19, order_count: 16, order_amount: 3420.00, message_received:  [3-->] 4, message_processed: 2, message_failed: 1, message_stuck:  [0-->] 1, request_received: 18, request_processed: 15, request_failed: 3, request_stuck: 0  row: 0x10c615910  session: 0x10c51df20  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:43,416 - logic_logger - INFO
Logic Phase:		COMMIT LOGIC		(session=0x10c51df20)   										 - 2026-11-19 17:41:43,416 - logic_logger - INFO
Logic Phase:		AFTER_FLUSH LOGIC	(session=0x10c51df20)   										 - 2026-11-19 17:41:43,419 - logic_logger - INFO
..OrderB2bMessage[112] {AfterFlush Event} id: 112, received_at: 2026-11-19 17:41:43.411131, payload: {"Account": "Nobody 1795138903406", "Notes": "behave kafka test", "Items": [{"Name": "Widget", "QuantityOrdered": 1}]}, is_processed: False, error_text: None, CreatedOn: 2026-11-19 17:41:43.411861, CreatedOnDay: 2026-11-19  row: 0x10cbf87a0  session: 0x10c51df20  ins_upd_dlt: ins, initial: ins - 2026-11-19 17:41:43,420 - logic_logger - INFO


Logic Phase:		ROW LOGIC		(session=0x10c51e7a0) (sqlalchemy before_flush)			 - 2026-11-19 17:41:43,426 - logic_logger - INFO
..OrderB2bMessage[112] {Update - client} id: 112, received_at: 2026-11-19 17:41:43.411131, payload: {"Account": "Nobody 1795138903406", "Notes": "behave kafka test", "Items": [{"Name": "Widget", "QuantityOrdered": 1}]}, is_processed: False, error_text:  [None-->] resolve_lookups: no Customer found for fk_col='customer_id' from source fields, CreatedOn: 2026-11-19 17:41:43.411861, CreatedOnDay: 2026-11-19  row: 0x10cbf8710  session: 0x10c51e7a0  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:43,426 - logic_logger - INFO
....DailyFlow[2026-11-19] {Update - Adjusting daily_flow: message_failed} day: 2026-11-19, order_count: 16, order_amount: 3420.00, message_received: 4, message_processed: 2, message_failed:  [1-->] 2, message_stuck: 1, request_received: 18, request_processed: 15, request_failed: 3, request_stuck: 0  row: 0x10c614100  session: 0x10c51e7a0  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:43,426 - logic_logger - INFO
....DailyFlow[2026-11-19] {Formula message_stuck} day: 2026-11-19, order_count: 16, order_amount: 3420.00, message_received: 4, message_processed: 2, message_failed:  [1-->] 2, message_stuck:  [1-->] 0, request_received: 18, request_processed: 15, request_failed: 3, request_stuck: 0  row: 0x10c614100  session: 0x10c51e7a0  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:43,426 - logic_logger - INFO
....DailyFlow[2026-11-19] {Prune Formula: request_stuck [['request_received', 'request_processed', 'request_failed']]} day: 2026-11-19, order_count: 16, order_amount: 3420.00, message_received: 4, message_processed: 2, message_failed:  [1-->] 2, message_stuck:  [1-->] 0, request_received: 18, request_processed: 15, request_failed: 3, request_stuck: 0  row: 0x10c614100  session: 0x10c51e7a0  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:43,426 - logic_logger - INFO
Logic Phase:		COMMIT LOGIC		(session=0x10c51e7a0)   										 - 2026-11-19 17:41:43,426 - logic_logger - INFO
Logic Phase:		AFTER_FLUSH LOGIC	(session=0x10c51e7a0)   										 - 2026-11-19 17:41:43,427 - logic_logger - INFO
..OrderB2bMessage[112] {AfterFlush Event} id: 112, received_at: 2026-11-19 17:41:43.411131, payload: {"Account": "Nobody 1795138903406", "Notes": "behave kafka test", "Items": [{"Name": "Widget", "QuantityOrdered": 1}]}, is_processed: False, error_text:  [None-->] resolve_lookups: no Customer found for fk_col='customer_id' from source fields, CreatedOn: 2026-11-19 17:41:43.411861, CreatedOnDay: 2026-11-19  row: 0x10cbf8710  session: 0x10c51e7a0  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:43,427 - logic_logger - INFO

```
</details>

&nbsp;
&nbsp;

### Feature: Order Flow Dashboard  

&nbsp;
&nbsp;

#### Scenario: Order Placed Is Dated Today ✅ (0.02 s)
&emsp;  Scenario: Order Placed Is Dated Today  
&emsp;&emsp;    Given Customer "Dana" with credit limit 5000  
&emsp;&emsp;    When B2B order placed for "Dana" with 1 Widget  
&emsp;&emsp;    Then the Order is dated today  

<details markdown>
<summary>Rules exercised and logic log (2 transactions)</summary>


&nbsp;
&nbsp;


**Rules Used** in Scenario: Order Placed Is Dated Today
```
  DailyFlow  
    1. Derive DailyFlow.request_processed as Count(OrderB2bRequest Where Rule.count(derive=models.DailyFlow.request_processed, as_count_of=models.OrderB2bRequest, where=lambda row: row.is_processed == True, insert_parent=True), insert_parent)  
    2. Derive DailyFlow.request_failed as Count(OrderB2bRequest Where Rule.count(derive=models.DailyFlow.request_failed, as_count_of=models.OrderB2bRequest, where=lambda row: row.error_text is not None, insert_parent=True), insert_parent)  
    3. Derive DailyFlow.request_stuck as Formula (2): Rule.formula(derive=models.DailyFlow.request_stuc [...]  
    4. Derive DailyFlow.request_received as Count(OrderB2bRequest Where  - None, insert_parent)  
    5. Derive DailyFlow.order_amount as Sum(Order.amount_total Where  - None, insert_parent)  
    6. Derive DailyFlow.order_count as Count(Order Where  - None, insert_parent)  
  Customer  
    7. Derive Customer.balance as Sum(Order.amount_total Where Rule.sum(derive=models.Customer.balance, as_sum_of=models.Order.amount_total, where=lambda row: row.date_shipped is None))  
  Item  
    8. Derive Item.amount as Formula (1): Rule.formula(derive=models.Item.amount, as_expres [...]  
    9. Derive Item.unit_price as Copy(product.unit_price)  
  Order  
    10. RowEvent Order._send_order_to_shipping()  
    11. Derive Order.amount_total as Sum(Item.amount Where  - None)  
```
**Logic Log** in Scenario: Order Placed Is Dated Today (2 transactions)
```
Logic Phase:		ROW LOGIC		(session=0x10c51d6a0) (sqlalchemy before_flush)			 - 2026-11-19 17:41:43,944 - logic_logger - INFO
..OrderB2bRequest[None] {Insert - client} id: None, CreatedOn: None, CreatedOnDay: None, payload: {"Account": "Dana 1795138903938", "Notes": "behave test", "Items": [{"Name": "Widget", "QuantityOrdered": 1}]}, is_processed: False, error_text: None  row: 0x10cafd4d0  session: 0x10c51d6a0  ins_upd_dlt: ins, initial: ins - 2026-11-19 17:41:43,945 - logic_logger - INFO
..OrderB2bRequest[None] {early_row_event_all_classes - handle_all did stamping} id: None, CreatedOn: 2026-11-19 17:41:43.945115, CreatedOnDay: 2026-11-19, payload: {"Account": "Dana 1795138903938", "Notes": "behave test", "Items": [{"Name": "Widget", "QuantityOrdered": 1}]}, is_processed: False, error_text: None  row: 0x10cafd4d0  session: 0x10c51d6a0  ins_upd_dlt: ins, initial: ins - 2026-11-19 17:41:43,945 - logic_logger - INFO
....DailyFlow[2026-11-19] {Update - Adjusting daily_flow: request_received} day: 2026-11-19, order_count: 16, order_amount: 3420.00, message_received: 4, message_processed: 2, message_failed: 2, message_stuck: 0, request_received:  [18-->] 19, request_processed: 15, request_failed: 3, request_stuck: 0  row: 0x10c614310  session: 0x10c51d6a0  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:43,945 - logic_logger - INFO
....DailyFlow[2026-11-19] {Prune Formula: message_stuck [['message_received', 'message_processed', 'message_failed']]} day: 2026-11-19, order_count: 16, order_amount: 3420.00, message_received: 4, message_processed: 2, message_failed: 2, message_stuck: 0, request_received:  [18-->] 19, request_processed: 15, request_failed: 3, request_stuck: 0  row: 0x10c614310  session: 0x10c51d6a0  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:43,945 - logic_logger - INFO
....DailyFlow[2026-11-19] {Formula request_stuck} day: 2026-11-19, order_count: 16, order_amount: 3420.00, message_received: 4, message_processed: 2, message_failed: 2, message_stuck: 0, request_received:  [18-->] 19, request_processed: 15, request_failed: 3, request_stuck:  [0-->] 1  row: 0x10c614310  session: 0x10c51d6a0  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:43,945 - logic_logger - INFO
Logic Phase:		COMMIT LOGIC		(session=0x10c51d6a0)   										 - 2026-11-19 17:41:43,945 - logic_logger - INFO
Logic Phase:		AFTER_FLUSH LOGIC	(session=0x10c51d6a0)   										 - 2026-11-19 17:41:43,946 - logic_logger - INFO


Logic Phase:		ROW LOGIC		(session=0x10c51d6a0) (sqlalchemy before_flush)			 - 2026-11-19 17:41:43,948 - logic_logger - INFO
..OrderB2bRequest[79] {Update - client} id: 79, CreatedOn: 2026-11-19 17:41:43.945115, CreatedOnDay: 2026-11-19, payload: {"Account": "Dana 1795138903938", "Notes": "behave test", "Items": [{"Name": "Widget", "QuantityOrdered": 1}]}, is_processed:  [False-->] True, error_text: None  row: 0x10cafd4d0  session: 0x10c51d6a0  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:43,948 - logic_logger - INFO
....DailyFlow[2026-11-19] {Update - Adjusting daily_flow: request_processed} day: 2026-11-19, order_count: 16, order_amount: 3420.00, message_received: 4, message_processed: 2, message_failed: 2, message_stuck: 0, request_received: 19, request_processed:  [15-->] 16, request_failed: 3, request_stuck: 1  row: 0x10c614310  session: 0x10c51d6a0  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:43,949 - logic_logger - INFO
....DailyFlow[2026-11-19] {Prune Formula: message_stuck [['message_received', 'message_processed', 'message_failed']]} day: 2026-11-19, order_count: 16, order_amount: 3420.00, message_received: 4, message_processed: 2, message_failed: 2, message_stuck: 0, request_received: 19, request_processed:  [15-->] 16, request_failed: 3, request_stuck: 1  row: 0x10c614310  session: 0x10c51d6a0  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:43,949 - logic_logger - INFO
....DailyFlow[2026-11-19] {Formula request_stuck} day: 2026-11-19, order_count: 16, order_amount: 3420.00, message_received: 4, message_processed: 2, message_failed: 2, message_stuck: 0, request_received: 19, request_processed:  [15-->] 16, request_failed: 3, request_stuck:  [1-->] 0  row: 0x10c614310  session: 0x10c51d6a0  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:43,949 - logic_logger - INFO
..Product[2] {Update - client} id: 2, name: Widget, count_suppliers: 0, unit_price: 90.0000000000  row: 0x10cbc11d0  session: 0x10c51d6a0  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:43,949 - logic_logger - INFO
..Order[None] {Insert - client} id: None, notes: behave test, customer_id: 28, CreatedOn: None, date_shipped: None, amount_total: None, CreatedOnDay: None  row: 0x10cbf9400  session: 0x10c51d6a0  ins_upd_dlt: ins, initial: ins - 2026-11-19 17:41:43,949 - logic_logger - INFO
..Order[None] {early_row_event_all_classes - handle_all did stamping} id: None, notes: behave test, customer_id: 28, CreatedOn: 2026-11-19, date_shipped: None, amount_total: None, CreatedOnDay: 2026-11-19  row: 0x10cbf9400  session: 0x10c51d6a0  ins_upd_dlt: ins, initial: ins - 2026-11-19 17:41:43,949 - logic_logger - INFO
..Order[None] {server aggregate_defaults: amount_total } id: None, notes: behave test, customer_id: 28, CreatedOn: 2026-11-19, date_shipped: None, amount_total: 0, CreatedOnDay: 2026-11-19  row: 0x10cbf9400  session: 0x10c51d6a0  ins_upd_dlt: ins, initial: ins - 2026-11-19 17:41:43,949 - logic_logger - INFO
....DailyFlow[2026-11-19] {Update - Adjusting daily_flow: order_count} day: 2026-11-19, order_count:  [16-->] 17, order_amount: 3420.00, message_received: 4, message_processed: 2, message_failed: 2, message_stuck: 0, request_received: 19, request_processed: 16, request_failed: 3, request_stuck: 0  row: 0x10c614310  session: 0x10c51d6a0  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:43,949 - logic_logger - INFO
....DailyFlow[2026-11-19] {Prune Formula: message_stuck [['message_received', 'message_processed', 'message_failed']]} day: 2026-11-19, order_count:  [16-->] 17, order_amount: 3420.00, message_received: 4, message_processed: 2, message_failed: 2, message_stuck: 0, request_received: 19, request_processed: 16, request_failed: 3, request_stuck: 0  row: 0x10c614310  session: 0x10c51d6a0  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:43,950 - logic_logger - INFO
....DailyFlow[2026-11-19] {Prune Formula: request_stuck [['request_received', 'request_processed', 'request_failed']]} day: 2026-11-19, order_count:  [16-->] 17, order_amount: 3420.00, message_received: 4, message_processed: 2, message_failed: 2, message_stuck: 0, request_received: 19, request_processed: 16, request_failed: 3, request_stuck: 0  row: 0x10c614310  session: 0x10c51d6a0  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:43,950 - logic_logger - INFO
..Item[None] {Insert - client} id: None, order_id: None, product_id: None, quantity: 1, amount: None, unit_price: None  row: 0x10cafd150  session: 0x10c51d6a0  ins_upd_dlt: ins, initial: ins - 2026-11-19 17:41:43,950 - logic_logger - INFO
..Item[None] {copy_rules for role: product - unit_price} id: None, order_id: None, product_id: None, quantity: 1, amount: None, unit_price: 90.0000000000  row: 0x10cafd150  session: 0x10c51d6a0  ins_upd_dlt: ins, initial: ins - 2026-11-19 17:41:43,950 - logic_logger - INFO
..Item[None] {Formula amount} id: None, order_id: None, product_id: None, quantity: 1, amount: 90.0000000000, unit_price: 90.0000000000  row: 0x10cafd150  session: 0x10c51d6a0  ins_upd_dlt: ins, initial: ins - 2026-11-19 17:41:43,950 - logic_logger - INFO
....Order[None] {Update - Adjusting order: amount_total} id: None, notes: behave test, customer_id: 28, CreatedOn: 2026-11-19, date_shipped: None, amount_total:  [0-->] 90.0000000000, CreatedOnDay: 2026-11-19  row: 0x10cbf9400  session: 0x10c51d6a0  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:43,950 - logic_logger - INFO
......DailyFlow[2026-11-19] {Update - Adjusting daily_flow: order_amount} day: 2026-11-19, order_count: 17, order_amount:  [3420.00-->] 3510.0000000000, message_received: 4, message_processed: 2, message_failed: 2, message_stuck: 0, request_received: 19, request_processed: 16, request_failed: 3, request_stuck: 0  row: 0x10c614310  session: 0x10c51d6a0  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:43,950 - logic_logger - INFO
......DailyFlow[2026-11-19] {Prune Formula: message_stuck [['message_received', 'message_processed', 'message_failed']]} day: 2026-11-19, order_count: 17, order_amount:  [3420.00-->] 3510.0000000000, message_received: 4, message_processed: 2, message_failed: 2, message_stuck: 0, request_received: 19, request_processed: 16, request_failed: 3, request_stuck: 0  row: 0x10c614310  session: 0x10c51d6a0  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:43,950 - logic_logger - INFO
......DailyFlow[2026-11-19] {Prune Formula: request_stuck [['request_received', 'request_processed', 'request_failed']]} day: 2026-11-19, order_count: 17, order_amount:  [3420.00-->] 3510.0000000000, message_received: 4, message_processed: 2, message_failed: 2, message_stuck: 0, request_received: 19, request_processed: 16, request_failed: 3, request_stuck: 0  row: 0x10c614310  session: 0x10c51d6a0  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:43,950 - logic_logger - INFO
......Customer[28] {Update - Adjusting customer: balance} id: 28, name: Dana 1795138903938, balance:  [0E-10-->] 90.0000000000, credit_limit: 5000.0000000000, email: None, email_opt_out: None  row: 0x10cba2950  session: 0x10c51d6a0  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:43,950 - logic_logger - INFO
Logic Phase:		COMMIT LOGIC		(session=0x10c51d6a0)   										 - 2026-11-19 17:41:43,950 - logic_logger - INFO
Logic Phase:		AFTER_FLUSH LOGIC	(session=0x10c51d6a0)   										 - 2026-11-19 17:41:43,952 - logic_logger - INFO
..Order[175] {AfterFlush Event} id: 175, notes: behave test, customer_id: 28, CreatedOn: 2026-11-19, date_shipped: None, amount_total: 90.0000000000, CreatedOnDay: 2026-11-19  row: 0x10cbf9400  session: 0x10c51d6a0  ins_upd_dlt: ins, initial: ins - 2026-11-19 17:41:43,952 - logic_logger - INFO

```
</details>

&nbsp;
&nbsp;

#### Scenario: Order With Its Own Date Keeps It ✅ (0.01 s)
&emsp;  Scenario: Order With Its Own Date Keeps It  
&emsp;&emsp;    Given Customer "Eli" with credit limit 5000  
&emsp;&emsp;    When an Order dated 2026-01-15 is created for "Eli" through the API  
&emsp;&emsp;    Then the Order keeps its date 2026-01-15  

<details markdown>
<summary>Rules exercised and logic log (1 transaction)</summary>


&nbsp;
&nbsp;


**Rules Used** in Scenario: Order With Its Own Date Keeps It
```
  Customer  
    1. Derive Customer.balance as Sum(Order.amount_total Where Rule.sum(derive=models.Customer.balance, as_sum_of=models.Order.amount_total, where=lambda row: row.date_shipped is None))  
  DailyFlow  
    2. Derive DailyFlow.message_stuck as Formula (1): Rule.formula(derive=models.DailyFlow.message_stuc [...]  
    3. Derive DailyFlow.request_stuck as Formula (2): Rule.formula(derive=models.DailyFlow.request_stuc [...]  
    4. Derive DailyFlow.order_amount as Sum(Order.amount_total Where  - None, insert_parent)  
    5. Derive DailyFlow.order_count as Count(Order Where  - None, insert_parent)  
  Order  
    6. RowEvent Order._send_order_to_shipping()  
```
**Logic Log** in Scenario: Order With Its Own Date Keeps It (1 transaction)
```
Logic Phase:		ROW LOGIC		(session=0x10c51dd00) (sqlalchemy before_flush)			 - 2026-11-19 17:41:43,963 - logic_logger - INFO
..Order[None] {Insert - client} id: None, notes: behave dated, customer_id: 29, CreatedOn: 2026-01-15 00:00:00, date_shipped: None, amount_total: None, CreatedOnDay: None  row: 0x10cbf9be0  session: 0x10c51dd00  ins_upd_dlt: ins, initial: ins - 2026-11-19 17:41:43,964 - logic_logger - INFO
..Order[None] {early_row_event_all_classes - handle_all did stamping} id: None, notes: behave dated, customer_id: 29, CreatedOn: 2026-01-15 00:00:00, date_shipped: None, amount_total: None, CreatedOnDay: 2026-01-15  row: 0x10cbf9be0  session: 0x10c51dd00  ins_upd_dlt: ins, initial: ins - 2026-11-19 17:41:43,964 - logic_logger - INFO
..Order[None] {server aggregate_defaults: amount_total } id: None, notes: behave dated, customer_id: 29, CreatedOn: 2026-01-15 00:00:00, date_shipped: None, amount_total: 0, CreatedOnDay: 2026-01-15  row: 0x10cbf9be0  session: 0x10c51dd00  ins_upd_dlt: ins, initial: ins - 2026-11-19 17:41:43,964 - logic_logger - INFO
..Order[None] {Insert Parent: daily_flow} id: None, notes: behave dated, customer_id: 29, CreatedOn: 2026-01-15 00:00:00, date_shipped: None, amount_total: 0, CreatedOnDay: 2026-01-15  row: 0x10cbf9be0  session: 0x10c51dd00  ins_upd_dlt: ins, initial: ins - 2026-11-19 17:41:43,964 - logic_logger - INFO
....DailyFlow[2026-01-15] {Insert - Insert Parent from Order} day:  [None-->] 2026-01-15, order_count: None, order_amount: None, message_received: None, message_processed: None, message_failed: None, message_stuck: None, request_received: None, request_processed: None, request_failed: None, request_stuck: None  row: 0x10c615b20  session: 0x10c51dd00  ins_upd_dlt: ins, initial: ins - 2026-11-19 17:41:43,964 - logic_logger - INFO
....DailyFlow[2026-01-15] {server_defaults: order_count order_amount message_received message_processed message_failed message_stuck request_received request_processed request_failed request_stuck } day:  [None-->] 2026-01-15, order_count:  [None-->] 0, order_amount:  [None-->] 0, message_received:  [None-->] 0, message_processed:  [None-->] 0, message_failed:  [None-->] 0, message_stuck:  [None-->] 0, request_received:  [None-->] 0, request_processed:  [None-->] 0, request_failed:  [None-->] 0, request_stuck:  [None-->] 0  row: 0x10c615b20  session: 0x10c51dd00  ins_upd_dlt: ins, initial: ins - 2026-11-19 17:41:43,964 - logic_logger - INFO
....DailyFlow[2026-01-15] {server aggregate_defaults: order_count order_amount message_received message_processed message_failed request_received request_processed request_failed } day:  [None-->] 2026-01-15, order_count:  [None-->] 0, order_amount:  [None-->] 0, message_received:  [None-->] 0, message_processed:  [None-->] 0, message_failed:  [None-->] 0, message_stuck:  [None-->] 0, request_received:  [None-->] 0, request_processed:  [None-->] 0, request_failed:  [None-->] 0, request_stuck:  [None-->] 0  row: 0x10c615b20  session: 0x10c51dd00  ins_upd_dlt: ins, initial: ins - 2026-11-19 17:41:43,964 - logic_logger - INFO
....DailyFlow[2026-01-15] {Update - Adjusting daily_flow: order_count} day: 2026-01-15, order_count:  [0-->] 1, order_amount: 0, message_received: 0, message_processed: 0, message_failed: 0, message_stuck: 0, request_received: 0, request_processed: 0, request_failed: 0, request_stuck: 0  row: 0x10c615b20  session: 0x10c51dd00  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:43,965 - logic_logger - INFO
....DailyFlow[2026-01-15] {Prune Formula: message_stuck [['message_received', 'message_processed', 'message_failed']]} day: 2026-01-15, order_count:  [0-->] 1, order_amount: 0, message_received: 0, message_processed: 0, message_failed: 0, message_stuck: 0, request_received: 0, request_processed: 0, request_failed: 0, request_stuck: 0  row: 0x10c615b20  session: 0x10c51dd00  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:43,965 - logic_logger - INFO
....DailyFlow[2026-01-15] {Prune Formula: request_stuck [['request_received', 'request_processed', 'request_failed']]} day: 2026-01-15, order_count:  [0-->] 1, order_amount: 0, message_received: 0, message_processed: 0, message_failed: 0, message_stuck: 0, request_received: 0, request_processed: 0, request_failed: 0, request_stuck: 0  row: 0x10c615b20  session: 0x10c51dd00  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:43,965 - logic_logger - INFO
Logic Phase:		COMMIT LOGIC		(session=0x10c51dd00)   										 - 2026-11-19 17:41:43,965 - logic_logger - INFO
Logic Phase:		AFTER_FLUSH LOGIC	(session=0x10c51dd00)   										 - 2026-11-19 17:41:43,966 - logic_logger - INFO
..Order[176] {AfterFlush Event} id: 176, notes: behave dated, customer_id: 29, CreatedOn: 2026-01-15 00:00:00, date_shipped: None, amount_total: 0, CreatedOnDay: 2026-01-15  row: 0x10cbf9be0  session: 0x10c51dd00  ins_upd_dlt: ins, initial: ins - 2026-11-19 17:41:43,966 - logic_logger - INFO

```
</details>

&nbsp;
&nbsp;

#### Scenario: New Order Counts In Daily Totals ✅ (0.02 s)
&emsp;  Scenario: New Order Counts In Daily Totals  
&emsp;&emsp;    Given Customer "Fran" with credit limit 5000  
&emsp;&emsp;    And the daily totals are read  
&emsp;&emsp;    When B2B order placed for "Fran" with 2 Widget  
&emsp;&emsp;    Then today's order_count rises by 1 and order_amount by 180  

<details markdown>
<summary>Rules exercised and logic log (2 transactions)</summary>


&nbsp;
&nbsp;


**Rules Used** in Scenario: New Order Counts In Daily Totals
```
  DailyFlow  
    1. Derive DailyFlow.request_processed as Count(OrderB2bRequest Where Rule.count(derive=models.DailyFlow.request_processed, as_count_of=models.OrderB2bRequest, where=lambda row: row.is_processed == True, insert_parent=True), insert_parent)  
    2. Derive DailyFlow.request_failed as Count(OrderB2bRequest Where Rule.count(derive=models.DailyFlow.request_failed, as_count_of=models.OrderB2bRequest, where=lambda row: row.error_text is not None, insert_parent=True), insert_parent)  
    3. Derive DailyFlow.request_stuck as Formula (2): Rule.formula(derive=models.DailyFlow.request_stuc [...]  
    4. Derive DailyFlow.request_received as Count(OrderB2bRequest Where  - None, insert_parent)  
    5. Derive DailyFlow.order_amount as Sum(Order.amount_total Where  - None, insert_parent)  
    6. Derive DailyFlow.order_count as Count(Order Where  - None, insert_parent)  
  Customer  
    7. Derive Customer.balance as Sum(Order.amount_total Where Rule.sum(derive=models.Customer.balance, as_sum_of=models.Order.amount_total, where=lambda row: row.date_shipped is None))  
  Item  
    8. Derive Item.amount as Formula (1): Rule.formula(derive=models.Item.amount, as_expres [...]  
    9. Derive Item.unit_price as Copy(product.unit_price)  
  Order  
    10. RowEvent Order._send_order_to_shipping()  
    11. Derive Order.amount_total as Sum(Item.amount Where  - None)  
```
**Logic Log** in Scenario: New Order Counts In Daily Totals (2 transactions)
```
Logic Phase:		ROW LOGIC		(session=0x10c51d040) (sqlalchemy before_flush)			 - 2026-11-19 17:41:43,978 - logic_logger - INFO
..OrderB2bRequest[None] {Insert - client} id: None, CreatedOn: None, CreatedOnDay: None, payload: {"Account": "Fran 1795138903972", "Notes": "behave test", "Items": [{"Name": "Widget", "QuantityOrdered": 2}]}, is_processed: False, error_text: None  row: 0x10c4c7dd0  session: 0x10c51d040  ins_upd_dlt: ins, initial: ins - 2026-11-19 17:41:43,978 - logic_logger - INFO
..OrderB2bRequest[None] {early_row_event_all_classes - handle_all did stamping} id: None, CreatedOn: 2026-11-19 17:41:43.978838, CreatedOnDay: 2026-11-19, payload: {"Account": "Fran 1795138903972", "Notes": "behave test", "Items": [{"Name": "Widget", "QuantityOrdered": 2}]}, is_processed: False, error_text: None  row: 0x10c4c7dd0  session: 0x10c51d040  ins_upd_dlt: ins, initial: ins - 2026-11-19 17:41:43,978 - logic_logger - INFO
....DailyFlow[2026-11-19] {Update - Adjusting daily_flow: request_received} day: 2026-11-19, order_count: 17, order_amount: 3510.00, message_received: 4, message_processed: 2, message_failed: 2, message_stuck: 0, request_received:  [19-->] 20, request_processed: 16, request_failed: 3, request_stuck: 0  row: 0x10c617070  session: 0x10c51d040  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:43,979 - logic_logger - INFO
....DailyFlow[2026-11-19] {Prune Formula: message_stuck [['message_received', 'message_processed', 'message_failed']]} day: 2026-11-19, order_count: 17, order_amount: 3510.00, message_received: 4, message_processed: 2, message_failed: 2, message_stuck: 0, request_received:  [19-->] 20, request_processed: 16, request_failed: 3, request_stuck: 0  row: 0x10c617070  session: 0x10c51d040  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:43,979 - logic_logger - INFO
....DailyFlow[2026-11-19] {Formula request_stuck} day: 2026-11-19, order_count: 17, order_amount: 3510.00, message_received: 4, message_processed: 2, message_failed: 2, message_stuck: 0, request_received:  [19-->] 20, request_processed: 16, request_failed: 3, request_stuck:  [0-->] 1  row: 0x10c617070  session: 0x10c51d040  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:43,979 - logic_logger - INFO
Logic Phase:		COMMIT LOGIC		(session=0x10c51d040)   										 - 2026-11-19 17:41:43,979 - logic_logger - INFO
Logic Phase:		AFTER_FLUSH LOGIC	(session=0x10c51d040)   										 - 2026-11-19 17:41:43,979 - logic_logger - INFO


Logic Phase:		ROW LOGIC		(session=0x10c51d040) (sqlalchemy before_flush)			 - 2026-11-19 17:41:43,981 - logic_logger - INFO
..OrderB2bRequest[80] {Update - client} id: 80, CreatedOn: 2026-11-19 17:41:43.978838, CreatedOnDay: 2026-11-19, payload: {"Account": "Fran 1795138903972", "Notes": "behave test", "Items": [{"Name": "Widget", "QuantityOrdered": 2}]}, is_processed:  [False-->] True, error_text: None  row: 0x10c4c7dd0  session: 0x10c51d040  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:43,981 - logic_logger - INFO
....DailyFlow[2026-11-19] {Update - Adjusting daily_flow: request_processed} day: 2026-11-19, order_count: 17, order_amount: 3510.00, message_received: 4, message_processed: 2, message_failed: 2, message_stuck: 0, request_received: 20, request_processed:  [16-->] 17, request_failed: 3, request_stuck: 1  row: 0x10c617070  session: 0x10c51d040  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:43,982 - logic_logger - INFO
....DailyFlow[2026-11-19] {Prune Formula: message_stuck [['message_received', 'message_processed', 'message_failed']]} day: 2026-11-19, order_count: 17, order_amount: 3510.00, message_received: 4, message_processed: 2, message_failed: 2, message_stuck: 0, request_received: 20, request_processed:  [16-->] 17, request_failed: 3, request_stuck: 1  row: 0x10c617070  session: 0x10c51d040  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:43,982 - logic_logger - INFO
....DailyFlow[2026-11-19] {Formula request_stuck} day: 2026-11-19, order_count: 17, order_amount: 3510.00, message_received: 4, message_processed: 2, message_failed: 2, message_stuck: 0, request_received: 20, request_processed:  [16-->] 17, request_failed: 3, request_stuck:  [1-->] 0  row: 0x10c617070  session: 0x10c51d040  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:43,982 - logic_logger - INFO
..Product[2] {Update - client} id: 2, name: Widget, count_suppliers: 0, unit_price: 90.0000000000  row: 0x10c5de9e0  session: 0x10c51d040  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:43,982 - logic_logger - INFO
..Order[None] {Insert - client} id: None, notes: behave test, customer_id: 30, CreatedOn: None, date_shipped: None, amount_total: None, CreatedOnDay: None  row: 0x10c6db890  session: 0x10c51d040  ins_upd_dlt: ins, initial: ins - 2026-11-19 17:41:43,982 - logic_logger - INFO
..Order[None] {early_row_event_all_classes - handle_all did stamping} id: None, notes: behave test, customer_id: 30, CreatedOn: 2026-11-19, date_shipped: None, amount_total: None, CreatedOnDay: 2026-11-19  row: 0x10c6db890  session: 0x10c51d040  ins_upd_dlt: ins, initial: ins - 2026-11-19 17:41:43,982 - logic_logger - INFO
..Order[None] {server aggregate_defaults: amount_total } id: None, notes: behave test, customer_id: 30, CreatedOn: 2026-11-19, date_shipped: None, amount_total: 0, CreatedOnDay: 2026-11-19  row: 0x10c6db890  session: 0x10c51d040  ins_upd_dlt: ins, initial: ins - 2026-11-19 17:41:43,982 - logic_logger - INFO
....DailyFlow[2026-11-19] {Update - Adjusting daily_flow: order_count} day: 2026-11-19, order_count:  [17-->] 18, order_amount: 3510.00, message_received: 4, message_processed: 2, message_failed: 2, message_stuck: 0, request_received: 20, request_processed: 17, request_failed: 3, request_stuck: 0  row: 0x10c617070  session: 0x10c51d040  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:43,982 - logic_logger - INFO
....DailyFlow[2026-11-19] {Prune Formula: message_stuck [['message_received', 'message_processed', 'message_failed']]} day: 2026-11-19, order_count:  [17-->] 18, order_amount: 3510.00, message_received: 4, message_processed: 2, message_failed: 2, message_stuck: 0, request_received: 20, request_processed: 17, request_failed: 3, request_stuck: 0  row: 0x10c617070  session: 0x10c51d040  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:43,982 - logic_logger - INFO
....DailyFlow[2026-11-19] {Prune Formula: request_stuck [['request_received', 'request_processed', 'request_failed']]} day: 2026-11-19, order_count:  [17-->] 18, order_amount: 3510.00, message_received: 4, message_processed: 2, message_failed: 2, message_stuck: 0, request_received: 20, request_processed: 17, request_failed: 3, request_stuck: 0  row: 0x10c617070  session: 0x10c51d040  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:43,982 - logic_logger - INFO
..Item[None] {Insert - client} id: None, order_id: None, product_id: None, quantity: 2, amount: None, unit_price: None  row: 0x10c4c7cd0  session: 0x10c51d040  ins_upd_dlt: ins, initial: ins - 2026-11-19 17:41:43,982 - logic_logger - INFO
..Item[None] {copy_rules for role: product - unit_price} id: None, order_id: None, product_id: None, quantity: 2, amount: None, unit_price: 90.0000000000  row: 0x10c4c7cd0  session: 0x10c51d040  ins_upd_dlt: ins, initial: ins - 2026-11-19 17:41:43,982 - logic_logger - INFO
..Item[None] {Formula amount} id: None, order_id: None, product_id: None, quantity: 2, amount: 180.0000000000, unit_price: 90.0000000000  row: 0x10c4c7cd0  session: 0x10c51d040  ins_upd_dlt: ins, initial: ins - 2026-11-19 17:41:43,982 - logic_logger - INFO
....Order[None] {Update - Adjusting order: amount_total} id: None, notes: behave test, customer_id: 30, CreatedOn: 2026-11-19, date_shipped: None, amount_total:  [0-->] 180.0000000000, CreatedOnDay: 2026-11-19  row: 0x10c6db890  session: 0x10c51d040  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:43,983 - logic_logger - INFO
......DailyFlow[2026-11-19] {Update - Adjusting daily_flow: order_amount} day: 2026-11-19, order_count: 18, order_amount:  [3510.00-->] 3690.0000000000, message_received: 4, message_processed: 2, message_failed: 2, message_stuck: 0, request_received: 20, request_processed: 17, request_failed: 3, request_stuck: 0  row: 0x10c617070  session: 0x10c51d040  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:43,983 - logic_logger - INFO
......DailyFlow[2026-11-19] {Prune Formula: message_stuck [['message_received', 'message_processed', 'message_failed']]} day: 2026-11-19, order_count: 18, order_amount:  [3510.00-->] 3690.0000000000, message_received: 4, message_processed: 2, message_failed: 2, message_stuck: 0, request_received: 20, request_processed: 17, request_failed: 3, request_stuck: 0  row: 0x10c617070  session: 0x10c51d040  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:43,983 - logic_logger - INFO
......DailyFlow[2026-11-19] {Prune Formula: request_stuck [['request_received', 'request_processed', 'request_failed']]} day: 2026-11-19, order_count: 18, order_amount:  [3510.00-->] 3690.0000000000, message_received: 4, message_processed: 2, message_failed: 2, message_stuck: 0, request_received: 20, request_processed: 17, request_failed: 3, request_stuck: 0  row: 0x10c617070  session: 0x10c51d040  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:43,983 - logic_logger - INFO
......Customer[30] {Update - Adjusting customer: balance} id: 30, name: Fran 1795138903972, balance:  [0E-10-->] 180.0000000000, credit_limit: 5000.0000000000, email: None, email_opt_out: None  row: 0x10c48b8d0  session: 0x10c51d040  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:43,983 - logic_logger - INFO
Logic Phase:		COMMIT LOGIC		(session=0x10c51d040)   										 - 2026-11-19 17:41:43,983 - logic_logger - INFO
Logic Phase:		AFTER_FLUSH LOGIC	(session=0x10c51d040)   										 - 2026-11-19 17:41:43,984 - logic_logger - INFO
..Order[177] {AfterFlush Event} id: 177, notes: behave test, customer_id: 30, CreatedOn: 2026-11-19, date_shipped: None, amount_total: 180.0000000000, CreatedOnDay: 2026-11-19  row: 0x10c6db890  session: 0x10c51d040  ins_upd_dlt: ins, initial: ins - 2026-11-19 17:41:43,984 - logic_logger - INFO

```
</details>

&nbsp;
&nbsp;

#### Scenario: Changed Item Adjusts Daily Amount ✅ (0.02 s)
&emsp;  Scenario: Changed Item Adjusts Daily Amount  
&emsp;&emsp;    Given Customer "Gale" with credit limit 5000  
&emsp;&emsp;    And Order is created for "Gale" with 2 Widget  
&emsp;&emsp;    And the daily totals are read  
&emsp;&emsp;    When Item quantity changed to 3  
&emsp;&emsp;    Then today's order_count rises by 0 and order_amount by 90  

<details markdown>
<summary>Rules exercised and logic log (3 transactions)</summary>


&nbsp;
&nbsp;


**Rules Used** in Scenario: Changed Item Adjusts Daily Amount
```
  DailyFlow  
    1. Derive DailyFlow.request_processed as Count(OrderB2bRequest Where Rule.count(derive=models.DailyFlow.request_processed, as_count_of=models.OrderB2bRequest, where=lambda row: row.is_processed == True, insert_parent=True), insert_parent)  
    2. Derive DailyFlow.request_failed as Count(OrderB2bRequest Where Rule.count(derive=models.DailyFlow.request_failed, as_count_of=models.OrderB2bRequest, where=lambda row: row.error_text is not None, insert_parent=True), insert_parent)  
    3. Derive DailyFlow.request_stuck as Formula (2): Rule.formula(derive=models.DailyFlow.request_stuc [...]  
    4. Derive DailyFlow.request_received as Count(OrderB2bRequest Where  - None, insert_parent)  
    5. Derive DailyFlow.order_amount as Sum(Order.amount_total Where  - None, insert_parent)  
    6. Derive DailyFlow.order_count as Count(Order Where  - None, insert_parent)  
  Customer  
    7. Derive Customer.balance as Sum(Order.amount_total Where Rule.sum(derive=models.Customer.balance, as_sum_of=models.Order.amount_total, where=lambda row: row.date_shipped is None))  
  Item  
    8. Derive Item.amount as Formula (1): Rule.formula(derive=models.Item.amount, as_expres [...]  
    9. Derive Item.unit_price as Copy(product.unit_price)  
  Order  
    10. RowEvent Order._send_order_to_shipping()  
    11. Derive Order.amount_total as Sum(Item.amount Where  - None)  
```
**Logic Log** in Scenario: Changed Item Adjusts Daily Amount (3 transactions)
```
Logic Phase:		ROW LOGIC		(session=0x10c51d9d0) (sqlalchemy before_flush)			 - 2026-11-19 17:41:43,992 - logic_logger - INFO
..OrderB2bRequest[None] {Insert - client} id: None, CreatedOn: None, CreatedOnDay: None, payload: {"Account": "Gale 1795138903988", "Notes": "behave test", "Items": [{"Name": "Widget", "QuantityOrdered": 2}]}, is_processed: False, error_text: None  row: 0x10c3527d0  session: 0x10c51d9d0  ins_upd_dlt: ins, initial: ins - 2026-11-19 17:41:43,992 - logic_logger - INFO
..OrderB2bRequest[None] {early_row_event_all_classes - handle_all did stamping} id: None, CreatedOn: 2026-11-19 17:41:43.992986, CreatedOnDay: 2026-11-19, payload: {"Account": "Gale 1795138903988", "Notes": "behave test", "Items": [{"Name": "Widget", "QuantityOrdered": 2}]}, is_processed: False, error_text: None  row: 0x10c3527d0  session: 0x10c51d9d0  ins_upd_dlt: ins, initial: ins - 2026-11-19 17:41:43,993 - logic_logger - INFO
....DailyFlow[2026-11-19] {Update - Adjusting daily_flow: request_received} day: 2026-11-19, order_count: 18, order_amount: 3690.00, message_received: 4, message_processed: 2, message_failed: 2, message_stuck: 0, request_received:  [20-->] 21, request_processed: 17, request_failed: 3, request_stuck: 0  row: 0x10c6157b0  session: 0x10c51d9d0  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:43,993 - logic_logger - INFO
....DailyFlow[2026-11-19] {Prune Formula: message_stuck [['message_received', 'message_processed', 'message_failed']]} day: 2026-11-19, order_count: 18, order_amount: 3690.00, message_received: 4, message_processed: 2, message_failed: 2, message_stuck: 0, request_received:  [20-->] 21, request_processed: 17, request_failed: 3, request_stuck: 0  row: 0x10c6157b0  session: 0x10c51d9d0  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:43,993 - logic_logger - INFO
....DailyFlow[2026-11-19] {Formula request_stuck} day: 2026-11-19, order_count: 18, order_amount: 3690.00, message_received: 4, message_processed: 2, message_failed: 2, message_stuck: 0, request_received:  [20-->] 21, request_processed: 17, request_failed: 3, request_stuck:  [0-->] 1  row: 0x10c6157b0  session: 0x10c51d9d0  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:43,993 - logic_logger - INFO
Logic Phase:		COMMIT LOGIC		(session=0x10c51d9d0)   										 - 2026-11-19 17:41:43,993 - logic_logger - INFO
Logic Phase:		AFTER_FLUSH LOGIC	(session=0x10c51d9d0)   										 - 2026-11-19 17:41:43,993 - logic_logger - INFO


Logic Phase:		ROW LOGIC		(session=0x10c51d9d0) (sqlalchemy before_flush)			 - 2026-11-19 17:41:43,995 - logic_logger - INFO
..OrderB2bRequest[81] {Update - client} id: 81, CreatedOn: 2026-11-19 17:41:43.992986, CreatedOnDay: 2026-11-19, payload: {"Account": "Gale 1795138903988", "Notes": "behave test", "Items": [{"Name": "Widget", "QuantityOrdered": 2}]}, is_processed:  [False-->] True, error_text: None  row: 0x10c3527d0  session: 0x10c51d9d0  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:43,995 - logic_logger - INFO
....DailyFlow[2026-11-19] {Update - Adjusting daily_flow: request_processed} day: 2026-11-19, order_count: 18, order_amount: 3690.00, message_received: 4, message_processed: 2, message_failed: 2, message_stuck: 0, request_received: 21, request_processed:  [17-->] 18, request_failed: 3, request_stuck: 1  row: 0x10c6157b0  session: 0x10c51d9d0  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:43,996 - logic_logger - INFO
....DailyFlow[2026-11-19] {Prune Formula: message_stuck [['message_received', 'message_processed', 'message_failed']]} day: 2026-11-19, order_count: 18, order_amount: 3690.00, message_received: 4, message_processed: 2, message_failed: 2, message_stuck: 0, request_received: 21, request_processed:  [17-->] 18, request_failed: 3, request_stuck: 1  row: 0x10c6157b0  session: 0x10c51d9d0  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:43,996 - logic_logger - INFO
....DailyFlow[2026-11-19] {Formula request_stuck} day: 2026-11-19, order_count: 18, order_amount: 3690.00, message_received: 4, message_processed: 2, message_failed: 2, message_stuck: 0, request_received: 21, request_processed:  [17-->] 18, request_failed: 3, request_stuck:  [1-->] 0  row: 0x10c6157b0  session: 0x10c51d9d0  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:43,996 - logic_logger - INFO
..Product[2] {Update - client} id: 2, name: Widget, count_suppliers: 0, unit_price: 90.0000000000  row: 0x10cbc17f0  session: 0x10c51d9d0  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:43,996 - logic_logger - INFO
..Order[None] {Insert - client} id: None, notes: behave test, customer_id: 31, CreatedOn: None, date_shipped: None, amount_total: None, CreatedOnDay: None  row: 0x10c6db920  session: 0x10c51d9d0  ins_upd_dlt: ins, initial: ins - 2026-11-19 17:41:43,996 - logic_logger - INFO
..Order[None] {early_row_event_all_classes - handle_all did stamping} id: None, notes: behave test, customer_id: 31, CreatedOn: 2026-11-19, date_shipped: None, amount_total: None, CreatedOnDay: 2026-11-19  row: 0x10c6db920  session: 0x10c51d9d0  ins_upd_dlt: ins, initial: ins - 2026-11-19 17:41:43,996 - logic_logger - INFO
..Order[None] {server aggregate_defaults: amount_total } id: None, notes: behave test, customer_id: 31, CreatedOn: 2026-11-19, date_shipped: None, amount_total: 0, CreatedOnDay: 2026-11-19  row: 0x10c6db920  session: 0x10c51d9d0  ins_upd_dlt: ins, initial: ins - 2026-11-19 17:41:43,996 - logic_logger - INFO
....DailyFlow[2026-11-19] {Update - Adjusting daily_flow: order_count} day: 2026-11-19, order_count:  [18-->] 19, order_amount: 3690.00, message_received: 4, message_processed: 2, message_failed: 2, message_stuck: 0, request_received: 21, request_processed: 18, request_failed: 3, request_stuck: 0  row: 0x10c6157b0  session: 0x10c51d9d0  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:43,996 - logic_logger - INFO
....DailyFlow[2026-11-19] {Prune Formula: message_stuck [['message_received', 'message_processed', 'message_failed']]} day: 2026-11-19, order_count:  [18-->] 19, order_amount: 3690.00, message_received: 4, message_processed: 2, message_failed: 2, message_stuck: 0, request_received: 21, request_processed: 18, request_failed: 3, request_stuck: 0  row: 0x10c6157b0  session: 0x10c51d9d0  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:43,996 - logic_logger - INFO
....DailyFlow[2026-11-19] {Prune Formula: request_stuck [['request_received', 'request_processed', 'request_failed']]} day: 2026-11-19, order_count:  [18-->] 19, order_amount: 3690.00, message_received: 4, message_processed: 2, message_failed: 2, message_stuck: 0, request_received: 21, request_processed: 18, request_failed: 3, request_stuck: 0  row: 0x10c6157b0  session: 0x10c51d9d0  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:43,996 - logic_logger - INFO
..Item[None] {Insert - client} id: None, order_id: None, product_id: None, quantity: 2, amount: None, unit_price: None  row: 0x10cafe650  session: 0x10c51d9d0  ins_upd_dlt: ins, initial: ins - 2026-11-19 17:41:43,996 - logic_logger - INFO
..Item[None] {copy_rules for role: product - unit_price} id: None, order_id: None, product_id: None, quantity: 2, amount: None, unit_price: 90.0000000000  row: 0x10cafe650  session: 0x10c51d9d0  ins_upd_dlt: ins, initial: ins - 2026-11-19 17:41:43,996 - logic_logger - INFO
..Item[None] {Formula amount} id: None, order_id: None, product_id: None, quantity: 2, amount: 180.0000000000, unit_price: 90.0000000000  row: 0x10cafe650  session: 0x10c51d9d0  ins_upd_dlt: ins, initial: ins - 2026-11-19 17:41:43,996 - logic_logger - INFO
....Order[None] {Update - Adjusting order: amount_total} id: None, notes: behave test, customer_id: 31, CreatedOn: 2026-11-19, date_shipped: None, amount_total:  [0-->] 180.0000000000, CreatedOnDay: 2026-11-19  row: 0x10c6db920  session: 0x10c51d9d0  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:43,997 - logic_logger - INFO
......DailyFlow[2026-11-19] {Update - Adjusting daily_flow: order_amount} day: 2026-11-19, order_count: 19, order_amount:  [3690.00-->] 3870.0000000000, message_received: 4, message_processed: 2, message_failed: 2, message_stuck: 0, request_received: 21, request_processed: 18, request_failed: 3, request_stuck: 0  row: 0x10c6157b0  session: 0x10c51d9d0  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:43,997 - logic_logger - INFO
......DailyFlow[2026-11-19] {Prune Formula: message_stuck [['message_received', 'message_processed', 'message_failed']]} day: 2026-11-19, order_count: 19, order_amount:  [3690.00-->] 3870.0000000000, message_received: 4, message_processed: 2, message_failed: 2, message_stuck: 0, request_received: 21, request_processed: 18, request_failed: 3, request_stuck: 0  row: 0x10c6157b0  session: 0x10c51d9d0  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:43,997 - logic_logger - INFO
......DailyFlow[2026-11-19] {Prune Formula: request_stuck [['request_received', 'request_processed', 'request_failed']]} day: 2026-11-19, order_count: 19, order_amount:  [3690.00-->] 3870.0000000000, message_received: 4, message_processed: 2, message_failed: 2, message_stuck: 0, request_received: 21, request_processed: 18, request_failed: 3, request_stuck: 0  row: 0x10c6157b0  session: 0x10c51d9d0  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:43,997 - logic_logger - INFO
......Customer[31] {Update - Adjusting customer: balance} id: 31, name: Gale 1795138903988, balance:  [0E-10-->] 180.0000000000, credit_limit: 5000.0000000000, email: None, email_opt_out: None  row: 0x10c6d4f50  session: 0x10c51d9d0  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:43,997 - logic_logger - INFO
Logic Phase:		COMMIT LOGIC		(session=0x10c51d9d0)   										 - 2026-11-19 17:41:43,997 - logic_logger - INFO
Logic Phase:		AFTER_FLUSH LOGIC	(session=0x10c51d9d0)   										 - 2026-11-19 17:41:43,998 - logic_logger - INFO
..Order[178] {AfterFlush Event} id: 178, notes: behave test, customer_id: 31, CreatedOn: 2026-11-19, date_shipped: None, amount_total: 180.0000000000, CreatedOnDay: 2026-11-19  row: 0x10c6db920  session: 0x10c51d9d0  ins_upd_dlt: ins, initial: ins - 2026-11-19 17:41:43,998 - logic_logger - INFO


Logic Phase:		ROW LOGIC		(session=0x10c51e9c0) (sqlalchemy before_flush)			 - 2026-11-19 17:41:44,005 - logic_logger - INFO
..Item[326] {Update - client} id: 326, order_id: 178, product_id: 2, quantity:  [2-->] 3, amount: 180.0000000000, unit_price: 90.0000000000  row: 0x10cba1650  session: 0x10c51e9c0  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:44,005 - logic_logger - INFO
..Item[326] {Formula amount} id: 326, order_id: 178, product_id: 2, quantity:  [2-->] 3, amount:  [180.0000000000-->] 270.0000000000, unit_price: 90.0000000000  row: 0x10cba1650  session: 0x10c51e9c0  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:44,005 - logic_logger - INFO
....Order[178] {Update - Adjusting order: amount_total} id: 178, notes: behave test, customer_id: 31, CreatedOn: 2026-11-19, date_shipped: None, amount_total:  [180.0000000000-->] 270.0000000000, CreatedOnDay: 2026-11-19  row: 0x10cbf97f0  session: 0x10c51e9c0  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:44,005 - logic_logger - INFO
......DailyFlow[2026-11-19] {Update - Adjusting daily_flow: order_amount} day: 2026-11-19, order_count: 19, order_amount:  [3870.00-->] 3960.0000000000, message_received: 4, message_processed: 2, message_failed: 2, message_stuck: 0, request_received: 21, request_processed: 18, request_failed: 3, request_stuck: 0  row: 0x10c616f10  session: 0x10c51e9c0  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:44,005 - logic_logger - INFO
......DailyFlow[2026-11-19] {Prune Formula: message_stuck [['message_received', 'message_processed', 'message_failed']]} day: 2026-11-19, order_count: 19, order_amount:  [3870.00-->] 3960.0000000000, message_received: 4, message_processed: 2, message_failed: 2, message_stuck: 0, request_received: 21, request_processed: 18, request_failed: 3, request_stuck: 0  row: 0x10c616f10  session: 0x10c51e9c0  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:44,005 - logic_logger - INFO
......DailyFlow[2026-11-19] {Prune Formula: request_stuck [['request_received', 'request_processed', 'request_failed']]} day: 2026-11-19, order_count: 19, order_amount:  [3870.00-->] 3960.0000000000, message_received: 4, message_processed: 2, message_failed: 2, message_stuck: 0, request_received: 21, request_processed: 18, request_failed: 3, request_stuck: 0  row: 0x10c616f10  session: 0x10c51e9c0  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:44,005 - logic_logger - INFO
......Customer[31] {Update - Adjusting customer: balance} id: 31, name: Gale 1795138903988, balance:  [180.0000000000-->] 270.0000000000, credit_limit: 5000.0000000000, email: None, email_opt_out: None  row: 0x10c49ce50  session: 0x10c51e9c0  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:44,005 - logic_logger - INFO
Logic Phase:		COMMIT LOGIC		(session=0x10c51e9c0)   										 - 2026-11-19 17:41:44,006 - logic_logger - INFO
Logic Phase:		AFTER_FLUSH LOGIC	(session=0x10c51e9c0)   										 - 2026-11-19 17:41:44,006 - logic_logger - INFO
....Order[178] {AfterFlush Event} id: 178, notes: behave test, customer_id: 31, CreatedOn: 2026-11-19, date_shipped: None, amount_total:  [180.0000000000-->] 270.0000000000, CreatedOnDay: 2026-11-19  row: 0x10cbf97f0  session: 0x10c51e9c0  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:44,006 - logic_logger - INFO

```
</details>

&nbsp;
&nbsp;

#### Scenario: Deleted Order Leaves Daily Totals ✅ (0.02 s)
&emsp;  Scenario: Deleted Order Leaves Daily Totals  
&emsp;&emsp;    Given Customer "Hank" with credit limit 5000  
&emsp;&emsp;    And Order is created for "Hank" with 2 Widget  
&emsp;&emsp;    And the daily totals are read  
&emsp;&emsp;    When Order is deleted  
&emsp;&emsp;    Then today's order_count rises by -1 and order_amount by -180  

<details markdown>
<summary>Rules exercised and logic log (3 transactions)</summary>


&nbsp;
&nbsp;


**Rules Used** in Scenario: Deleted Order Leaves Daily Totals
```
  DailyFlow  
    1. Derive DailyFlow.request_processed as Count(OrderB2bRequest Where Rule.count(derive=models.DailyFlow.request_processed, as_count_of=models.OrderB2bRequest, where=lambda row: row.is_processed == True, insert_parent=True), insert_parent)  
    2. Derive DailyFlow.request_failed as Count(OrderB2bRequest Where Rule.count(derive=models.DailyFlow.request_failed, as_count_of=models.OrderB2bRequest, where=lambda row: row.error_text is not None, insert_parent=True), insert_parent)  
    3. Derive DailyFlow.request_stuck as Formula (2): Rule.formula(derive=models.DailyFlow.request_stuc [...]  
    4. Derive DailyFlow.request_received as Count(OrderB2bRequest Where  - None, insert_parent)  
    5. Derive DailyFlow.order_amount as Sum(Order.amount_total Where  - None, insert_parent)  
    6. Derive DailyFlow.order_count as Count(Order Where  - None, insert_parent)  
  Customer  
    7. Derive Customer.balance as Sum(Order.amount_total Where Rule.sum(derive=models.Customer.balance, as_sum_of=models.Order.amount_total, where=lambda row: row.date_shipped is None))  
  Item  
    8. Derive Item.amount as Formula (1): Rule.formula(derive=models.Item.amount, as_expres [...]  
    9. Derive Item.unit_price as Copy(product.unit_price)  
  Order  
    10. RowEvent Order._send_order_to_shipping()  
    11. Derive Order.amount_total as Sum(Item.amount Where  - None)  
```
**Logic Log** in Scenario: Deleted Order Leaves Daily Totals (3 transactions)
```
Logic Phase:		ROW LOGIC		(session=0x10c51e8b0) (sqlalchemy before_flush)			 - 2026-11-19 17:41:44,014 - logic_logger - INFO
..OrderB2bRequest[None] {Insert - client} id: None, CreatedOn: None, CreatedOnDay: None, payload: {"Account": "Hank 1795138904011", "Notes": "behave test", "Items": [{"Name": "Widget", "QuantityOrdered": 2}]}, is_processed: False, error_text: None  row: 0x10c43a5d0  session: 0x10c51e8b0  ins_upd_dlt: ins, initial: ins - 2026-11-19 17:41:44,014 - logic_logger - INFO
..OrderB2bRequest[None] {early_row_event_all_classes - handle_all did stamping} id: None, CreatedOn: 2026-11-19 17:41:44.014941, CreatedOnDay: 2026-11-19, payload: {"Account": "Hank 1795138904011", "Notes": "behave test", "Items": [{"Name": "Widget", "QuantityOrdered": 2}]}, is_processed: False, error_text: None  row: 0x10c43a5d0  session: 0x10c51e8b0  ins_upd_dlt: ins, initial: ins - 2026-11-19 17:41:44,014 - logic_logger - INFO
....DailyFlow[2026-11-19] {Update - Adjusting daily_flow: request_received} day: 2026-11-19, order_count: 19, order_amount: 3960.00, message_received: 4, message_processed: 2, message_failed: 2, message_stuck: 0, request_received:  [21-->] 22, request_processed: 18, request_failed: 3, request_stuck: 0  row: 0x10c617490  session: 0x10c51e8b0  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:44,015 - logic_logger - INFO
....DailyFlow[2026-11-19] {Prune Formula: message_stuck [['message_received', 'message_processed', 'message_failed']]} day: 2026-11-19, order_count: 19, order_amount: 3960.00, message_received: 4, message_processed: 2, message_failed: 2, message_stuck: 0, request_received:  [21-->] 22, request_processed: 18, request_failed: 3, request_stuck: 0  row: 0x10c617490  session: 0x10c51e8b0  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:44,015 - logic_logger - INFO
....DailyFlow[2026-11-19] {Formula request_stuck} day: 2026-11-19, order_count: 19, order_amount: 3960.00, message_received: 4, message_processed: 2, message_failed: 2, message_stuck: 0, request_received:  [21-->] 22, request_processed: 18, request_failed: 3, request_stuck:  [0-->] 1  row: 0x10c617490  session: 0x10c51e8b0  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:44,015 - logic_logger - INFO
Logic Phase:		COMMIT LOGIC		(session=0x10c51e8b0)   										 - 2026-11-19 17:41:44,015 - logic_logger - INFO
Logic Phase:		AFTER_FLUSH LOGIC	(session=0x10c51e8b0)   										 - 2026-11-19 17:41:44,015 - logic_logger - INFO


Logic Phase:		ROW LOGIC		(session=0x10c51e8b0) (sqlalchemy before_flush)			 - 2026-11-19 17:41:44,017 - logic_logger - INFO
..Product[2] {Update - client} id: 2, name: Widget, count_suppliers: 0, unit_price: 90.0000000000  row: 0x10cbc1fd0  session: 0x10c51e8b0  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:44,017 - logic_logger - INFO
..OrderB2bRequest[82] {Update - client} id: 82, CreatedOn: 2026-11-19 17:41:44.014941, CreatedOnDay: 2026-11-19, payload: {"Account": "Hank 1795138904011", "Notes": "behave test", "Items": [{"Name": "Widget", "QuantityOrdered": 2}]}, is_processed:  [False-->] True, error_text: None  row: 0x10c43a5d0  session: 0x10c51e8b0  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:44,017 - logic_logger - INFO
....DailyFlow[2026-11-19] {Update - Adjusting daily_flow: request_processed} day: 2026-11-19, order_count: 19, order_amount: 3960.00, message_received: 4, message_processed: 2, message_failed: 2, message_stuck: 0, request_received: 22, request_processed:  [18-->] 19, request_failed: 3, request_stuck: 1  row: 0x10c617490  session: 0x10c51e8b0  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:44,017 - logic_logger - INFO
....DailyFlow[2026-11-19] {Prune Formula: message_stuck [['message_received', 'message_processed', 'message_failed']]} day: 2026-11-19, order_count: 19, order_amount: 3960.00, message_received: 4, message_processed: 2, message_failed: 2, message_stuck: 0, request_received: 22, request_processed:  [18-->] 19, request_failed: 3, request_stuck: 1  row: 0x10c617490  session: 0x10c51e8b0  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:44,018 - logic_logger - INFO
....DailyFlow[2026-11-19] {Formula request_stuck} day: 2026-11-19, order_count: 19, order_amount: 3960.00, message_received: 4, message_processed: 2, message_failed: 2, message_stuck: 0, request_received: 22, request_processed:  [18-->] 19, request_failed: 3, request_stuck:  [1-->] 0  row: 0x10c617490  session: 0x10c51e8b0  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:44,018 - logic_logger - INFO
..Order[None] {Insert - client} id: None, notes: behave test, customer_id: 32, CreatedOn: None, date_shipped: None, amount_total: None, CreatedOnDay: None  row: 0x10cbf9d90  session: 0x10c51e8b0  ins_upd_dlt: ins, initial: ins - 2026-11-19 17:41:44,018 - logic_logger - INFO
..Order[None] {early_row_event_all_classes - handle_all did stamping} id: None, notes: behave test, customer_id: 32, CreatedOn: 2026-11-19, date_shipped: None, amount_total: None, CreatedOnDay: 2026-11-19  row: 0x10cbf9d90  session: 0x10c51e8b0  ins_upd_dlt: ins, initial: ins - 2026-11-19 17:41:44,018 - logic_logger - INFO
..Order[None] {server aggregate_defaults: amount_total } id: None, notes: behave test, customer_id: 32, CreatedOn: 2026-11-19, date_shipped: None, amount_total: 0, CreatedOnDay: 2026-11-19  row: 0x10cbf9d90  session: 0x10c51e8b0  ins_upd_dlt: ins, initial: ins - 2026-11-19 17:41:44,018 - logic_logger - INFO
....DailyFlow[2026-11-19] {Update - Adjusting daily_flow: order_count} day: 2026-11-19, order_count:  [19-->] 20, order_amount: 3960.00, message_received: 4, message_processed: 2, message_failed: 2, message_stuck: 0, request_received: 22, request_processed: 19, request_failed: 3, request_stuck: 0  row: 0x10c617490  session: 0x10c51e8b0  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:44,018 - logic_logger - INFO
....DailyFlow[2026-11-19] {Prune Formula: message_stuck [['message_received', 'message_processed', 'message_failed']]} day: 2026-11-19, order_count:  [19-->] 20, order_amount: 3960.00, message_received: 4, message_processed: 2, message_failed: 2, message_stuck: 0, request_received: 22, request_processed: 19, request_failed: 3, request_stuck: 0  row: 0x10c617490  session: 0x10c51e8b0  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:44,018 - logic_logger - INFO
....DailyFlow[2026-11-19] {Prune Formula: request_stuck [['request_received', 'request_processed', 'request_failed']]} day: 2026-11-19, order_count:  [19-->] 20, order_amount: 3960.00, message_received: 4, message_processed: 2, message_failed: 2, message_stuck: 0, request_received: 22, request_processed: 19, request_failed: 3, request_stuck: 0  row: 0x10c617490  session: 0x10c51e8b0  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:44,018 - logic_logger - INFO
..Item[None] {Insert - client} id: None, order_id: None, product_id: None, quantity: 2, amount: None, unit_price: None  row: 0x10c3883d0  session: 0x10c51e8b0  ins_upd_dlt: ins, initial: ins - 2026-11-19 17:41:44,018 - logic_logger - INFO
..Item[None] {copy_rules for role: product - unit_price} id: None, order_id: None, product_id: None, quantity: 2, amount: None, unit_price: 90.0000000000  row: 0x10c3883d0  session: 0x10c51e8b0  ins_upd_dlt: ins, initial: ins - 2026-11-19 17:41:44,018 - logic_logger - INFO
..Item[None] {Formula amount} id: None, order_id: None, product_id: None, quantity: 2, amount: 180.0000000000, unit_price: 90.0000000000  row: 0x10c3883d0  session: 0x10c51e8b0  ins_upd_dlt: ins, initial: ins - 2026-11-19 17:41:44,018 - logic_logger - INFO
....Order[None] {Update - Adjusting order: amount_total} id: None, notes: behave test, customer_id: 32, CreatedOn: 2026-11-19, date_shipped: None, amount_total:  [0-->] 180.0000000000, CreatedOnDay: 2026-11-19  row: 0x10cbf9d90  session: 0x10c51e8b0  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:44,018 - logic_logger - INFO
......DailyFlow[2026-11-19] {Update - Adjusting daily_flow: order_amount} day: 2026-11-19, order_count: 20, order_amount:  [3960.00-->] 4140.0000000000, message_received: 4, message_processed: 2, message_failed: 2, message_stuck: 0, request_received: 22, request_processed: 19, request_failed: 3, request_stuck: 0  row: 0x10c617490  session: 0x10c51e8b0  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:44,018 - logic_logger - INFO
......DailyFlow[2026-11-19] {Prune Formula: message_stuck [['message_received', 'message_processed', 'message_failed']]} day: 2026-11-19, order_count: 20, order_amount:  [3960.00-->] 4140.0000000000, message_received: 4, message_processed: 2, message_failed: 2, message_stuck: 0, request_received: 22, request_processed: 19, request_failed: 3, request_stuck: 0  row: 0x10c617490  session: 0x10c51e8b0  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:44,018 - logic_logger - INFO
......DailyFlow[2026-11-19] {Prune Formula: request_stuck [['request_received', 'request_processed', 'request_failed']]} day: 2026-11-19, order_count: 20, order_amount:  [3960.00-->] 4140.0000000000, message_received: 4, message_processed: 2, message_failed: 2, message_stuck: 0, request_received: 22, request_processed: 19, request_failed: 3, request_stuck: 0  row: 0x10c617490  session: 0x10c51e8b0  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:44,018 - logic_logger - INFO
......Customer[32] {Update - Adjusting customer: balance} id: 32, name: Hank 1795138904011, balance:  [0E-10-->] 180.0000000000, credit_limit: 5000.0000000000, email: None, email_opt_out: None  row: 0x10c55bf50  session: 0x10c51e8b0  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:44,018 - logic_logger - INFO
Logic Phase:		COMMIT LOGIC		(session=0x10c51e8b0)   										 - 2026-11-19 17:41:44,019 - logic_logger - INFO
Logic Phase:		AFTER_FLUSH LOGIC	(session=0x10c51e8b0)   										 - 2026-11-19 17:41:44,019 - logic_logger - INFO
..Order[179] {AfterFlush Event} id: 179, notes: behave test, customer_id: 32, CreatedOn: 2026-11-19, date_shipped: None, amount_total: 180.0000000000, CreatedOnDay: 2026-11-19  row: 0x10cbf9d90  session: 0x10c51e8b0  ins_upd_dlt: ins, initial: ins - 2026-11-19 17:41:44,019 - logic_logger - INFO


Logic Phase:		ROW LOGIC		(session=0x10c51cd10) (sqlalchemy before_flush)			 - 2026-11-19 17:41:44,024 - logic_logger - INFO
..Order[179] {Delete - client} id: 179, notes: behave test, customer_id: 32, CreatedOn: 2026-11-19, date_shipped: None, amount_total: 180.0000000000, CreatedOnDay: 2026-11-19  row: 0x10c6db920  session: 0x10c51cd10  ins_upd_dlt: dlt, initial: dlt - 2026-11-19 17:41:44,024 - logic_logger - INFO
....DailyFlow[2026-11-19] {Update - Adjusting daily_flow: order_count, order_amount} day: 2026-11-19, order_count:  [20-->] 19, order_amount:  [4140.00-->] 3960.0000000000, message_received: 4, message_processed: 2, message_failed: 2, message_stuck: 0, request_received: 22, request_processed: 19, request_failed: 3, request_stuck: 0  row: 0x10c616af0  session: 0x10c51cd10  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:44,024 - logic_logger - INFO
....DailyFlow[2026-11-19] {Prune Formula: message_stuck [['message_received', 'message_processed', 'message_failed']]} day: 2026-11-19, order_count:  [20-->] 19, order_amount:  [4140.00-->] 3960.0000000000, message_received: 4, message_processed: 2, message_failed: 2, message_stuck: 0, request_received: 22, request_processed: 19, request_failed: 3, request_stuck: 0  row: 0x10c616af0  session: 0x10c51cd10  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:44,024 - logic_logger - INFO
....DailyFlow[2026-11-19] {Prune Formula: request_stuck [['request_received', 'request_processed', 'request_failed']]} day: 2026-11-19, order_count:  [20-->] 19, order_amount:  [4140.00-->] 3960.0000000000, message_received: 4, message_processed: 2, message_failed: 2, message_stuck: 0, request_received: 22, request_processed: 19, request_failed: 3, request_stuck: 0  row: 0x10c616af0  session: 0x10c51cd10  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:44,024 - logic_logger - INFO
....Customer[32] {Update - Adjusting customer: balance} id: 32, name: Hank 1795138904011, balance:  [180.0000000000-->] 0E-10, credit_limit: 5000.0000000000, email: None, email_opt_out: None  row: 0x10cb823d0  session: 0x10c51cd10  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:44,025 - logic_logger - INFO
Logic Phase:		COMMIT LOGIC		(session=0x10c51cd10)   										 - 2026-11-19 17:41:44,025 - logic_logger - INFO
Logic Phase:		AFTER_FLUSH LOGIC	(session=0x10c51cd10)   										 - 2026-11-19 17:41:44,025 - logic_logger - INFO
..Order[179] {AfterFlush Event} id: 179, notes: behave test, customer_id: 32, CreatedOn: 2026-11-19, date_shipped: None, amount_total: 180.0000000000, CreatedOnDay: 2026-11-19  row: 0x10c6db920  session: 0x10c51cd10  ins_upd_dlt: dlt, initial: dlt - 2026-11-19 17:41:44,025 - logic_logger - INFO

```
</details>

&nbsp;
&nbsp;

#### Scenario: Order Moved To Another Day ✅ (0.02 s)
&emsp;  Scenario: Order Moved To Another Day  
&emsp;&emsp;    Given Customer "Ivo" with credit limit 5000  
&emsp;&emsp;    And Order is created for "Ivo" with 1 Widget  
&emsp;&emsp;    And the daily totals are read  
&emsp;&emsp;    When the Order is moved to yesterday  
&emsp;&emsp;    Then today's order_count rises by -1 and order_amount by -90  
&emsp;&emsp;    And yesterday's order_count rises by 1  

<details markdown>
<summary>Rules exercised and logic log (3 transactions)</summary>


&nbsp;
&nbsp;


**Rules Used** in Scenario: Order Moved To Another Day
```
  DailyFlow  
    1. Derive DailyFlow.request_processed as Count(OrderB2bRequest Where Rule.count(derive=models.DailyFlow.request_processed, as_count_of=models.OrderB2bRequest, where=lambda row: row.is_processed == True, insert_parent=True), insert_parent)  
    2. Derive DailyFlow.request_failed as Count(OrderB2bRequest Where Rule.count(derive=models.DailyFlow.request_failed, as_count_of=models.OrderB2bRequest, where=lambda row: row.error_text is not None, insert_parent=True), insert_parent)  
    3. Derive DailyFlow.request_stuck as Formula (2): Rule.formula(derive=models.DailyFlow.request_stuc [...]  
    4. Derive DailyFlow.request_received as Count(OrderB2bRequest Where  - None, insert_parent)  
    5. Derive DailyFlow.order_amount as Sum(Order.amount_total Where  - None, insert_parent)  
    6. Derive DailyFlow.order_count as Count(Order Where  - None, insert_parent)  
  Customer  
    7. Derive Customer.balance as Sum(Order.amount_total Where Rule.sum(derive=models.Customer.balance, as_sum_of=models.Order.amount_total, where=lambda row: row.date_shipped is None))  
  Item  
    8. Derive Item.amount as Formula (1): Rule.formula(derive=models.Item.amount, as_expres [...]  
    9. Derive Item.unit_price as Copy(product.unit_price)  
  Order  
    10. RowEvent Order._send_order_to_shipping()  
    11. Derive Order.amount_total as Sum(Item.amount Where  - None)  
```
**Logic Log** in Scenario: Order Moved To Another Day (3 transactions)
```
Logic Phase:		ROW LOGIC		(session=0x10c51d7b0) (sqlalchemy before_flush)			 - 2026-11-19 17:41:44,034 - logic_logger - INFO
..OrderB2bRequest[None] {Insert - client} id: None, CreatedOn: None, CreatedOnDay: None, payload: {"Account": "Ivo 1795138904030", "Notes": "behave test", "Items": [{"Name": "Widget", "QuantityOrdered": 1}]}, is_processed: False, error_text: None  row: 0x10c558750  session: 0x10c51d7b0  ins_upd_dlt: ins, initial: ins - 2026-11-19 17:41:44,034 - logic_logger - INFO
..OrderB2bRequest[None] {early_row_event_all_classes - handle_all did stamping} id: None, CreatedOn: 2026-11-19 17:41:44.034328, CreatedOnDay: 2026-11-19, payload: {"Account": "Ivo 1795138904030", "Notes": "behave test", "Items": [{"Name": "Widget", "QuantityOrdered": 1}]}, is_processed: False, error_text: None  row: 0x10c558750  session: 0x10c51d7b0  ins_upd_dlt: ins, initial: ins - 2026-11-19 17:41:44,034 - logic_logger - INFO
....DailyFlow[2026-11-19] {Update - Adjusting daily_flow: request_received} day: 2026-11-19, order_count: 19, order_amount: 3960.00, message_received: 4, message_processed: 2, message_failed: 2, message_stuck: 0, request_received:  [22-->] 23, request_processed: 19, request_failed: 3, request_stuck: 0  row: 0x10c6175f0  session: 0x10c51d7b0  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:44,034 - logic_logger - INFO
....DailyFlow[2026-11-19] {Prune Formula: message_stuck [['message_received', 'message_processed', 'message_failed']]} day: 2026-11-19, order_count: 19, order_amount: 3960.00, message_received: 4, message_processed: 2, message_failed: 2, message_stuck: 0, request_received:  [22-->] 23, request_processed: 19, request_failed: 3, request_stuck: 0  row: 0x10c6175f0  session: 0x10c51d7b0  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:44,034 - logic_logger - INFO
....DailyFlow[2026-11-19] {Formula request_stuck} day: 2026-11-19, order_count: 19, order_amount: 3960.00, message_received: 4, message_processed: 2, message_failed: 2, message_stuck: 0, request_received:  [22-->] 23, request_processed: 19, request_failed: 3, request_stuck:  [0-->] 1  row: 0x10c6175f0  session: 0x10c51d7b0  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:44,034 - logic_logger - INFO
Logic Phase:		COMMIT LOGIC		(session=0x10c51d7b0)   										 - 2026-11-19 17:41:44,034 - logic_logger - INFO
Logic Phase:		AFTER_FLUSH LOGIC	(session=0x10c51d7b0)   										 - 2026-11-19 17:41:44,035 - logic_logger - INFO


Logic Phase:		ROW LOGIC		(session=0x10c51d7b0) (sqlalchemy before_flush)			 - 2026-11-19 17:41:44,036 - logic_logger - INFO
..OrderB2bRequest[83] {Update - client} id: 83, CreatedOn: 2026-11-19 17:41:44.034328, CreatedOnDay: 2026-11-19, payload: {"Account": "Ivo 1795138904030", "Notes": "behave test", "Items": [{"Name": "Widget", "QuantityOrdered": 1}]}, is_processed:  [False-->] True, error_text: None  row: 0x10c558750  session: 0x10c51d7b0  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:44,037 - logic_logger - INFO
....DailyFlow[2026-11-19] {Update - Adjusting daily_flow: request_processed} day: 2026-11-19, order_count: 19, order_amount: 3960.00, message_received: 4, message_processed: 2, message_failed: 2, message_stuck: 0, request_received: 23, request_processed:  [19-->] 20, request_failed: 3, request_stuck: 1  row: 0x10c6175f0  session: 0x10c51d7b0  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:44,037 - logic_logger - INFO
....DailyFlow[2026-11-19] {Prune Formula: message_stuck [['message_received', 'message_processed', 'message_failed']]} day: 2026-11-19, order_count: 19, order_amount: 3960.00, message_received: 4, message_processed: 2, message_failed: 2, message_stuck: 0, request_received: 23, request_processed:  [19-->] 20, request_failed: 3, request_stuck: 1  row: 0x10c6175f0  session: 0x10c51d7b0  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:44,037 - logic_logger - INFO
....DailyFlow[2026-11-19] {Formula request_stuck} day: 2026-11-19, order_count: 19, order_amount: 3960.00, message_received: 4, message_processed: 2, message_failed: 2, message_stuck: 0, request_received: 23, request_processed:  [19-->] 20, request_failed: 3, request_stuck:  [1-->] 0  row: 0x10c6175f0  session: 0x10c51d7b0  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:44,037 - logic_logger - INFO
..Product[2] {Update - client} id: 2, name: Widget, count_suppliers: 0, unit_price: 90.0000000000  row: 0x10cbc23c0  session: 0x10c51d7b0  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:44,037 - logic_logger - INFO
..Order[None] {Insert - client} id: None, notes: behave test, customer_id: 33, CreatedOn: None, date_shipped: None, amount_total: None, CreatedOnDay: None  row: 0x10c6db5c0  session: 0x10c51d7b0  ins_upd_dlt: ins, initial: ins - 2026-11-19 17:41:44,037 - logic_logger - INFO
..Order[None] {early_row_event_all_classes - handle_all did stamping} id: None, notes: behave test, customer_id: 33, CreatedOn: 2026-11-19, date_shipped: None, amount_total: None, CreatedOnDay: 2026-11-19  row: 0x10c6db5c0  session: 0x10c51d7b0  ins_upd_dlt: ins, initial: ins - 2026-11-19 17:41:44,037 - logic_logger - INFO
..Order[None] {server aggregate_defaults: amount_total } id: None, notes: behave test, customer_id: 33, CreatedOn: 2026-11-19, date_shipped: None, amount_total: 0, CreatedOnDay: 2026-11-19  row: 0x10c6db5c0  session: 0x10c51d7b0  ins_upd_dlt: ins, initial: ins - 2026-11-19 17:41:44,037 - logic_logger - INFO
....DailyFlow[2026-11-19] {Update - Adjusting daily_flow: order_count} day: 2026-11-19, order_count:  [19-->] 20, order_amount: 3960.00, message_received: 4, message_processed: 2, message_failed: 2, message_stuck: 0, request_received: 23, request_processed: 20, request_failed: 3, request_stuck: 0  row: 0x10c6175f0  session: 0x10c51d7b0  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:44,037 - logic_logger - INFO
....DailyFlow[2026-11-19] {Prune Formula: message_stuck [['message_received', 'message_processed', 'message_failed']]} day: 2026-11-19, order_count:  [19-->] 20, order_amount: 3960.00, message_received: 4, message_processed: 2, message_failed: 2, message_stuck: 0, request_received: 23, request_processed: 20, request_failed: 3, request_stuck: 0  row: 0x10c6175f0  session: 0x10c51d7b0  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:44,037 - logic_logger - INFO
....DailyFlow[2026-11-19] {Prune Formula: request_stuck [['request_received', 'request_processed', 'request_failed']]} day: 2026-11-19, order_count:  [19-->] 20, order_amount: 3960.00, message_received: 4, message_processed: 2, message_failed: 2, message_stuck: 0, request_received: 23, request_processed: 20, request_failed: 3, request_stuck: 0  row: 0x10c6175f0  session: 0x10c51d7b0  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:44,037 - logic_logger - INFO
..Item[None] {Insert - client} id: None, order_id: None, product_id: None, quantity: 1, amount: None, unit_price: None  row: 0x10cafc1d0  session: 0x10c51d7b0  ins_upd_dlt: ins, initial: ins - 2026-11-19 17:41:44,037 - logic_logger - INFO
..Item[None] {copy_rules for role: product - unit_price} id: None, order_id: None, product_id: None, quantity: 1, amount: None, unit_price: 90.0000000000  row: 0x10cafc1d0  session: 0x10c51d7b0  ins_upd_dlt: ins, initial: ins - 2026-11-19 17:41:44,037 - logic_logger - INFO
..Item[None] {Formula amount} id: None, order_id: None, product_id: None, quantity: 1, amount: 90.0000000000, unit_price: 90.0000000000  row: 0x10cafc1d0  session: 0x10c51d7b0  ins_upd_dlt: ins, initial: ins - 2026-11-19 17:41:44,037 - logic_logger - INFO
....Order[None] {Update - Adjusting order: amount_total} id: None, notes: behave test, customer_id: 33, CreatedOn: 2026-11-19, date_shipped: None, amount_total:  [0-->] 90.0000000000, CreatedOnDay: 2026-11-19  row: 0x10c6db5c0  session: 0x10c51d7b0  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:44,038 - logic_logger - INFO
......DailyFlow[2026-11-19] {Update - Adjusting daily_flow: order_amount} day: 2026-11-19, order_count: 20, order_amount:  [3960.00-->] 4050.0000000000, message_received: 4, message_processed: 2, message_failed: 2, message_stuck: 0, request_received: 23, request_processed: 20, request_failed: 3, request_stuck: 0  row: 0x10c6175f0  session: 0x10c51d7b0  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:44,038 - logic_logger - INFO
......DailyFlow[2026-11-19] {Prune Formula: message_stuck [['message_received', 'message_processed', 'message_failed']]} day: 2026-11-19, order_count: 20, order_amount:  [3960.00-->] 4050.0000000000, message_received: 4, message_processed: 2, message_failed: 2, message_stuck: 0, request_received: 23, request_processed: 20, request_failed: 3, request_stuck: 0  row: 0x10c6175f0  session: 0x10c51d7b0  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:44,038 - logic_logger - INFO
......DailyFlow[2026-11-19] {Prune Formula: request_stuck [['request_received', 'request_processed', 'request_failed']]} day: 2026-11-19, order_count: 20, order_amount:  [3960.00-->] 4050.0000000000, message_received: 4, message_processed: 2, message_failed: 2, message_stuck: 0, request_received: 23, request_processed: 20, request_failed: 3, request_stuck: 0  row: 0x10c6175f0  session: 0x10c51d7b0  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:44,038 - logic_logger - INFO
......Customer[33] {Update - Adjusting customer: balance} id: 33, name: Ivo 1795138904030, balance:  [0E-10-->] 90.0000000000, credit_limit: 5000.0000000000, email: None, email_opt_out: None  row: 0x10cba39d0  session: 0x10c51d7b0  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:44,038 - logic_logger - INFO
Logic Phase:		COMMIT LOGIC		(session=0x10c51d7b0)   										 - 2026-11-19 17:41:44,038 - logic_logger - INFO
Logic Phase:		AFTER_FLUSH LOGIC	(session=0x10c51d7b0)   										 - 2026-11-19 17:41:44,038 - logic_logger - INFO
..Order[180] {AfterFlush Event} id: 180, notes: behave test, customer_id: 33, CreatedOn: 2026-11-19, date_shipped: None, amount_total: 90.0000000000, CreatedOnDay: 2026-11-19  row: 0x10c6db5c0  session: 0x10c51d7b0  ins_upd_dlt: ins, initial: ins - 2026-11-19 17:41:44,038 - logic_logger - INFO


Logic Phase:		ROW LOGIC		(session=0x10c51dd00) (sqlalchemy before_flush)			 - 2026-11-19 17:41:44,043 - logic_logger - INFO
..Order[180] {Update - client} id: 180, notes: behave test, customer_id: 33, CreatedOn: 2026-11-19, date_shipped: None, amount_total: 90.0000000000, CreatedOnDay:  [2026-11-19-->] 2026-11-18  row: 0x10cbf8b00  session: 0x10c51dd00  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:44,043 - logic_logger - INFO
....DailyFlow[2026-11-18] {Update - Adjusting daily_flow: order_count, order_count, order_amount, order_amount} day: 2026-11-18, order_count:  [9-->] 10, order_amount:  [6068.00-->] 6158.0000000000, message_received: 6, message_processed: 6, message_failed: 0, message_stuck: 0, request_received: 3, request_processed: 3, request_failed: 0, request_stuck: 0  row: 0x10c616a40  session: 0x10c51dd00  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:44,043 - logic_logger - INFO
....DailyFlow[2026-11-18] {Prune Formula: message_stuck [['message_received', 'message_processed', 'message_failed']]} day: 2026-11-18, order_count:  [9-->] 10, order_amount:  [6068.00-->] 6158.0000000000, message_received: 6, message_processed: 6, message_failed: 0, message_stuck: 0, request_received: 3, request_processed: 3, request_failed: 0, request_stuck: 0  row: 0x10c616a40  session: 0x10c51dd00  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:44,043 - logic_logger - INFO
....DailyFlow[2026-11-18] {Prune Formula: request_stuck [['request_received', 'request_processed', 'request_failed']]} day: 2026-11-18, order_count:  [9-->] 10, order_amount:  [6068.00-->] 6158.0000000000, message_received: 6, message_processed: 6, message_failed: 0, message_stuck: 0, request_received: 3, request_processed: 3, request_failed: 0, request_stuck: 0  row: 0x10c616a40  session: 0x10c51dd00  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:44,043 - logic_logger - INFO
....DailyFlow[2026-11-19] {Update - Adjusting Old daily_flow} day: 2026-11-19, order_count:  [20-->] 19, order_amount:  [4050.00-->] 3960.0000000000, message_received: 4, message_processed: 2, message_failed: 2, message_stuck: 0, request_received: 23, request_processed: 20, request_failed: 3, request_stuck: 0  row: 0x10c616ba0  session: 0x10c51dd00  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:44,043 - logic_logger - INFO
....DailyFlow[2026-11-19] {Prune Formula: message_stuck [['message_received', 'message_processed', 'message_failed']]} day: 2026-11-19, order_count:  [20-->] 19, order_amount:  [4050.00-->] 3960.0000000000, message_received: 4, message_processed: 2, message_failed: 2, message_stuck: 0, request_received: 23, request_processed: 20, request_failed: 3, request_stuck: 0  row: 0x10c616ba0  session: 0x10c51dd00  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:44,043 - logic_logger - INFO
....DailyFlow[2026-11-19] {Prune Formula: request_stuck [['request_received', 'request_processed', 'request_failed']]} day: 2026-11-19, order_count:  [20-->] 19, order_amount:  [4050.00-->] 3960.0000000000, message_received: 4, message_processed: 2, message_failed: 2, message_stuck: 0, request_received: 23, request_processed: 20, request_failed: 3, request_stuck: 0  row: 0x10c616ba0  session: 0x10c51dd00  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:44,043 - logic_logger - INFO
Logic Phase:		COMMIT LOGIC		(session=0x10c51dd00)   										 - 2026-11-19 17:41:44,044 - logic_logger - INFO
Logic Phase:		AFTER_FLUSH LOGIC	(session=0x10c51dd00)   										 - 2026-11-19 17:41:44,044 - logic_logger - INFO
..Order[180] {AfterFlush Event} id: 180, notes: behave test, customer_id: 33, CreatedOn: 2026-11-19, date_shipped: None, amount_total: 90.0000000000, CreatedOnDay:  [2026-11-19-->] 2026-11-18  row: 0x10cbf8b00  session: 0x10c51dd00  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:44,044 - logic_logger - INFO

```
</details>

&nbsp;
&nbsp;

#### Scenario: Delivered Message Counts In Daily Totals ✅ (0.53 s)
&emsp;  Scenario: Delivered Message Counts In Daily Totals  
&emsp;&emsp;    Given Customer "Gil" with credit limit 5000  
&emsp;&emsp;    And the daily totals are read  
&emsp;&emsp;    When an inbound order message for "Gil" with 1 Widget and 2 Gadget is delivered to topic order_b2b  
&emsp;&emsp;    Then today's message_received and message_processed rise by 1  
&emsp;&emsp;    And today's message_stuck is unchanged  

<details markdown>
<summary>Rules exercised and logic log (3 transactions)</summary>


&nbsp;
&nbsp;


**Rules Used** in Scenario: Delivered Message Counts In Daily Totals
```
  DailyFlow  
    1. Derive DailyFlow.message_failed as Count(OrderB2bMessage Where Rule.count(derive=models.DailyFlow.message_failed, as_count_of=models.OrderB2bMessage, where=lambda row: row.error_text is not None, insert_parent=True), insert_parent)  
    2. Derive DailyFlow.message_stuck as Formula (1): Rule.formula(derive=models.DailyFlow.message_stuc [...]  
    3. Derive DailyFlow.message_received as Count(OrderB2bMessage Where  - None, insert_parent)  
    4. Derive DailyFlow.message_processed as Count(OrderB2bMessage Where Rule.count(derive=models.DailyFlow.message_processed, as_count_of=models.OrderB2bMessage, where=lambda row: row.is_processed == True, insert_parent=True), insert_parent)  
    5. Derive DailyFlow.order_amount as Sum(Order.amount_total Where  - None, insert_parent)  
    6. Derive DailyFlow.order_count as Count(Order Where  - None, insert_parent)  
  OrderB2bMessage  
    7. RowEvent OrderB2bMessage._publish_order_b2b()  
  Customer  
    8. Derive Customer.balance as Sum(Order.amount_total Where Rule.sum(derive=models.Customer.balance, as_sum_of=models.Order.amount_total, where=lambda row: row.date_shipped is None))  
  Item  
    9. Derive Item.amount as Formula (1): Rule.formula(derive=models.Item.amount, as_expres [...]  
    10. Derive Item.unit_price as Copy(product.unit_price)  
  Order  
    11. RowEvent Order._send_order_to_shipping()  
    12. Derive Order.amount_total as Sum(Item.amount Where  - None)  
```
**Logic Log** in Scenario: Delivered Message Counts In Daily Totals (3 transactions)
```
Logic Phase:		ROW LOGIC		(session=0x10c51e7a0) (sqlalchemy before_flush)			 - 2026-11-19 17:41:44,058 - logic_logger - INFO
..OrderB2bMessage[None] {Insert - client} id: None, received_at: 2026-11-19 17:41:44.058357, payload: {"Account": "Gil 1795138904051", "Notes": "behave kafka test", "Items": [{"Name": "Widget", "QuantityOrdered": 1}, {"Name": "Gadget", "QuantityOrdered": 2}]}, is_processed: False, error_text: None, CreatedOn: None, CreatedOnDay: None  row: 0x10c6d9760  session: 0x10c51e7a0  ins_upd_dlt: ins, initial: ins - 2026-11-19 17:41:44,058 - logic_logger - INFO
..OrderB2bMessage[None] {early_row_event_all_classes - handle_all did stamping} id: None, received_at: 2026-11-19 17:41:44.058357, payload: {"Account": "Gil 1795138904051", "Notes": "behave kafka test", "Items": [{"Name": "Widget", "QuantityOrdered": 1}, {"Name": "Gadget", "QuantityOrdered": 2}]}, is_processed: False, error_text: None, CreatedOn: 2026-11-19 17:41:44.058666, CreatedOnDay: 2026-11-19  row: 0x10c6d9760  session: 0x10c51e7a0  ins_upd_dlt: ins, initial: ins - 2026-11-19 17:41:44,058 - logic_logger - INFO
....DailyFlow[2026-11-19] {Update - Adjusting daily_flow: message_received} day: 2026-11-19, order_count: 19, order_amount: 3960.00, message_received:  [4-->] 5, message_processed: 2, message_failed: 2, message_stuck: 0, request_received: 23, request_processed: 20, request_failed: 3, request_stuck: 0  row: 0x10c28e570  session: 0x10c51e7a0  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:44,059 - logic_logger - INFO
....DailyFlow[2026-11-19] {Formula message_stuck} day: 2026-11-19, order_count: 19, order_amount: 3960.00, message_received:  [4-->] 5, message_processed: 2, message_failed: 2, message_stuck:  [0-->] 1, request_received: 23, request_processed: 20, request_failed: 3, request_stuck: 0  row: 0x10c28e570  session: 0x10c51e7a0  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:44,059 - logic_logger - INFO
....DailyFlow[2026-11-19] {Prune Formula: request_stuck [['request_received', 'request_processed', 'request_failed']]} day: 2026-11-19, order_count: 19, order_amount: 3960.00, message_received:  [4-->] 5, message_processed: 2, message_failed: 2, message_stuck:  [0-->] 1, request_received: 23, request_processed: 20, request_failed: 3, request_stuck: 0  row: 0x10c28e570  session: 0x10c51e7a0  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:44,059 - logic_logger - INFO
Logic Phase:		COMMIT LOGIC		(session=0x10c51e7a0)   										 - 2026-11-19 17:41:44,059 - logic_logger - INFO
Logic Phase:		AFTER_FLUSH LOGIC	(session=0x10c51e7a0)   										 - 2026-11-19 17:41:44,062 - logic_logger - INFO
..OrderB2bMessage[113] {AfterFlush Event} id: 113, received_at: 2026-11-19 17:41:44.058357, payload: {"Account": "Gil 1795138904051", "Notes": "behave kafka test", "Items": [{"Name": "Widget", "QuantityOrdered": 1}, {"Name": "Gadget", "QuantityOrdered": 2}]}, is_processed: False, error_text: None, CreatedOn: 2026-11-19 17:41:44.058666, CreatedOnDay: 2026-11-19  row: 0x10c6d9760  session: 0x10c51e7a0  ins_upd_dlt: ins, initial: ins - 2026-11-19 17:41:44,062 - logic_logger - INFO


Logic Phase:		ROW LOGIC		(session=0x10c51caf0) (sqlalchemy before_flush)			 - 2026-11-19 17:41:44,066 - logic_logger - INFO
..Order[None] {Insert - client} id: None, notes: behave kafka test, customer_id: 34, CreatedOn: None, date_shipped: None, amount_total: None, CreatedOnDay: None  row: 0x10c6db920  session: 0x10c51caf0  ins_upd_dlt: ins, initial: ins - 2026-11-19 17:41:44,066 - logic_logger - INFO
..Order[None] {early_row_event_all_classes - handle_all did stamping} id: None, notes: behave kafka test, customer_id: 34, CreatedOn: 2026-11-19, date_shipped: None, amount_total: None, CreatedOnDay: 2026-11-19  row: 0x10c6db920  session: 0x10c51caf0  ins_upd_dlt: ins, initial: ins - 2026-11-19 17:41:44,066 - logic_logger - INFO
..Order[None] {server aggregate_defaults: amount_total } id: None, notes: behave kafka test, customer_id: 34, CreatedOn: 2026-11-19, date_shipped: None, amount_total: 0, CreatedOnDay: 2026-11-19  row: 0x10c6db920  session: 0x10c51caf0  ins_upd_dlt: ins, initial: ins - 2026-11-19 17:41:44,066 - logic_logger - INFO
....DailyFlow[2026-11-19] {Update - Adjusting daily_flow: order_count} day: 2026-11-19, order_count:  [19-->] 20, order_amount: 3960.00, message_received: 5, message_processed: 2, message_failed: 2, message_stuck: 1, request_received: 23, request_processed: 20, request_failed: 3, request_stuck: 0  row: 0x10c616f10  session: 0x10c51caf0  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:44,066 - logic_logger - INFO
....DailyFlow[2026-11-19] {Prune Formula: message_stuck [['message_received', 'message_processed', 'message_failed']]} day: 2026-11-19, order_count:  [19-->] 20, order_amount: 3960.00, message_received: 5, message_processed: 2, message_failed: 2, message_stuck: 1, request_received: 23, request_processed: 20, request_failed: 3, request_stuck: 0  row: 0x10c616f10  session: 0x10c51caf0  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:44,066 - logic_logger - INFO
....DailyFlow[2026-11-19] {Prune Formula: request_stuck [['request_received', 'request_processed', 'request_failed']]} day: 2026-11-19, order_count:  [19-->] 20, order_amount: 3960.00, message_received: 5, message_processed: 2, message_failed: 2, message_stuck: 1, request_received: 23, request_processed: 20, request_failed: 3, request_stuck: 0  row: 0x10c616f10  session: 0x10c51caf0  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:44,066 - logic_logger - INFO
..Item[None] {Insert - client} id: None, order_id: None, product_id: 2, quantity: 1, amount: None, unit_price: None  row: 0x10c302dd0  session: 0x10c51caf0  ins_upd_dlt: ins, initial: ins - 2026-11-19 17:41:44,067 - logic_logger - INFO
..Item[None] {copy_rules for role: product - unit_price} id: None, order_id: None, product_id: 2, quantity: 1, amount: None, unit_price: 90.0000000000  row: 0x10c302dd0  session: 0x10c51caf0  ins_upd_dlt: ins, initial: ins - 2026-11-19 17:41:44,067 - logic_logger - INFO
..Item[None] {Formula amount} id: None, order_id: None, product_id: 2, quantity: 1, amount: 90.0000000000, unit_price: 90.0000000000  row: 0x10c302dd0  session: 0x10c51caf0  ins_upd_dlt: ins, initial: ins - 2026-11-19 17:41:44,067 - logic_logger - INFO
....Order[None] {Update - Adjusting order: amount_total} id: None, notes: behave kafka test, customer_id: 34, CreatedOn: 2026-11-19, date_shipped: None, amount_total:  [0-->] 90.0000000000, CreatedOnDay: 2026-11-19  row: 0x10c6db920  session: 0x10c51caf0  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:44,067 - logic_logger - INFO
......DailyFlow[2026-11-19] {Update - Adjusting daily_flow: order_amount} day: 2026-11-19, order_count: 20, order_amount:  [3960.00-->] 4050.0000000000, message_received: 5, message_processed: 2, message_failed: 2, message_stuck: 1, request_received: 23, request_processed: 20, request_failed: 3, request_stuck: 0  row: 0x10c616f10  session: 0x10c51caf0  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:44,067 - logic_logger - INFO
......DailyFlow[2026-11-19] {Prune Formula: message_stuck [['message_received', 'message_processed', 'message_failed']]} day: 2026-11-19, order_count: 20, order_amount:  [3960.00-->] 4050.0000000000, message_received: 5, message_processed: 2, message_failed: 2, message_stuck: 1, request_received: 23, request_processed: 20, request_failed: 3, request_stuck: 0  row: 0x10c616f10  session: 0x10c51caf0  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:44,067 - logic_logger - INFO
......DailyFlow[2026-11-19] {Prune Formula: request_stuck [['request_received', 'request_processed', 'request_failed']]} day: 2026-11-19, order_count: 20, order_amount:  [3960.00-->] 4050.0000000000, message_received: 5, message_processed: 2, message_failed: 2, message_stuck: 1, request_received: 23, request_processed: 20, request_failed: 3, request_stuck: 0  row: 0x10c616f10  session: 0x10c51caf0  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:44,067 - logic_logger - INFO
......Customer[34] {Update - Adjusting customer: balance} id: 34, name: Gil 1795138904051, balance:  [0E-10-->] 90.0000000000, credit_limit: 5000.0000000000, email: None, email_opt_out: None  row: 0x10cb83ed0  session: 0x10c51caf0  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:44,067 - logic_logger - INFO
..Item[None] {Insert - client} id: None, order_id: None, product_id: 1, quantity: 2, amount: None, unit_price: None  row: 0x10c353d50  session: 0x10c51caf0  ins_upd_dlt: ins, initial: ins - 2026-11-19 17:41:44,067 - logic_logger - INFO
..Item[None] {copy_rules for role: product - unit_price} id: None, order_id: None, product_id: 1, quantity: 2, amount: None, unit_price: 150.0000000000  row: 0x10c353d50  session: 0x10c51caf0  ins_upd_dlt: ins, initial: ins - 2026-11-19 17:41:44,067 - logic_logger - INFO
..Item[None] {Formula amount} id: None, order_id: None, product_id: 1, quantity: 2, amount: 300.0000000000, unit_price: 150.0000000000  row: 0x10c353d50  session: 0x10c51caf0  ins_upd_dlt: ins, initial: ins - 2026-11-19 17:41:44,067 - logic_logger - INFO
....Order[None] {Update - Adjusting order: amount_total} id: None, notes: behave kafka test, customer_id: 34, CreatedOn: 2026-11-19, date_shipped: None, amount_total:  [90.0000000000-->] 390.0000000000, CreatedOnDay: 2026-11-19  row: 0x10c6db920  session: 0x10c51caf0  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:44,067 - logic_logger - INFO
......DailyFlow[2026-11-19] {Update - Adjusting daily_flow: order_amount} day: 2026-11-19, order_count: 20, order_amount:  [4050.0000000000-->] 4350.0000000000, message_received: 5, message_processed: 2, message_failed: 2, message_stuck: 1, request_received: 23, request_processed: 20, request_failed: 3, request_stuck: 0  row: 0x10c616f10  session: 0x10c51caf0  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:44,068 - logic_logger - INFO
......DailyFlow[2026-11-19] {Prune Formula: message_stuck [['message_received', 'message_processed', 'message_failed']]} day: 2026-11-19, order_count: 20, order_amount:  [4050.0000000000-->] 4350.0000000000, message_received: 5, message_processed: 2, message_failed: 2, message_stuck: 1, request_received: 23, request_processed: 20, request_failed: 3, request_stuck: 0  row: 0x10c616f10  session: 0x10c51caf0  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:44,068 - logic_logger - INFO
......DailyFlow[2026-11-19] {Prune Formula: request_stuck [['request_received', 'request_processed', 'request_failed']]} day: 2026-11-19, order_count: 20, order_amount:  [4050.0000000000-->] 4350.0000000000, message_received: 5, message_processed: 2, message_failed: 2, message_stuck: 1, request_received: 23, request_processed: 20, request_failed: 3, request_stuck: 0  row: 0x10c616f10  session: 0x10c51caf0  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:44,068 - logic_logger - INFO
......Customer[34] {Update - Adjusting customer: balance} id: 34, name: Gil 1795138904051, balance:  [90.0000000000-->] 390.0000000000, credit_limit: 5000.0000000000, email: None, email_opt_out: None  row: 0x10cb83ed0  session: 0x10c51caf0  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:44,068 - logic_logger - INFO
Logic Phase:		COMMIT LOGIC		(session=0x10c51caf0)   										 - 2026-11-19 17:41:44,068 - logic_logger - INFO
Logic Phase:		AFTER_FLUSH LOGIC	(session=0x10c51caf0)   										 - 2026-11-19 17:41:44,069 - logic_logger - INFO
..Order[181] {AfterFlush Event} id: 181, notes: behave kafka test, customer_id: 34, CreatedOn: 2026-11-19, date_shipped: None, amount_total: 390.0000000000, CreatedOnDay: 2026-11-19  row: 0x10c6db920  session: 0x10c51caf0  ins_upd_dlt: ins, initial: ins - 2026-11-19 17:41:44,069 - logic_logger - INFO


Logic Phase:		ROW LOGIC		(session=0x10c51caf0) (sqlalchemy before_flush)			 - 2026-11-19 17:41:44,069 - logic_logger - INFO
..OrderB2bMessage[113] {Update - client} id: 113, received_at: 2026-11-19 17:41:44.058357, payload: {"Account": "Gil 1795138904051", "Notes": "behave kafka test", "Items": [{"Name": "Widget", "QuantityOrdered": 1}, {"Name": "Gadget", "QuantityOrdered": 2}]}, is_processed:  [False-->] True, error_text: None, CreatedOn: 2026-11-19 17:41:44.058666, CreatedOnDay: 2026-11-19  row: 0x10cbf8710  session: 0x10c51caf0  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:44,069 - logic_logger - INFO
....DailyFlow[2026-11-19] {Update - Adjusting daily_flow: message_processed} day: 2026-11-19, order_count: 20, order_amount: 4350.0000000000, message_received: 5, message_processed:  [2-->] 3, message_failed: 2, message_stuck: 1, request_received: 23, request_processed: 20, request_failed: 3, request_stuck: 0  row: 0x10c616f10  session: 0x10c51caf0  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:44,069 - logic_logger - INFO
....DailyFlow[2026-11-19] {Formula message_stuck} day: 2026-11-19, order_count: 20, order_amount: 4350.0000000000, message_received: 5, message_processed:  [2-->] 3, message_failed: 2, message_stuck:  [1-->] 0, request_received: 23, request_processed: 20, request_failed: 3, request_stuck: 0  row: 0x10c616f10  session: 0x10c51caf0  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:44,069 - logic_logger - INFO
....DailyFlow[2026-11-19] {Prune Formula: request_stuck [['request_received', 'request_processed', 'request_failed']]} day: 2026-11-19, order_count: 20, order_amount: 4350.0000000000, message_received: 5, message_processed:  [2-->] 3, message_failed: 2, message_stuck:  [1-->] 0, request_received: 23, request_processed: 20, request_failed: 3, request_stuck: 0  row: 0x10c616f10  session: 0x10c51caf0  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:44,069 - logic_logger - INFO
Logic Phase:		COMMIT LOGIC		(session=0x10c51caf0)   										 - 2026-11-19 17:41:44,069 - logic_logger - INFO
Logic Phase:		AFTER_FLUSH LOGIC	(session=0x10c51caf0)   										 - 2026-11-19 17:41:44,070 - logic_logger - INFO
..OrderB2bMessage[113] {AfterFlush Event} id: 113, received_at: 2026-11-19 17:41:44.058357, payload: {"Account": "Gil 1795138904051", "Notes": "behave kafka test", "Items": [{"Name": "Widget", "QuantityOrdered": 1}, {"Name": "Gadget", "QuantityOrdered": 2}]}, is_processed:  [False-->] True, error_text: None, CreatedOn: 2026-11-19 17:41:44.058666, CreatedOnDay: 2026-11-19  row: 0x10cbf8710  session: 0x10c51caf0  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:44,070 - logic_logger - INFO

```
</details>

&nbsp;
&nbsp;

#### Scenario: Rejected Message Counts In Daily Totals (live Kafka only) ✅ (0.53 s)
&emsp;  Scenario: Rejected Message Counts In Daily Totals (live Kafka only)  
&emsp;&emsp;    Given the daily totals are read  
&emsp;&emsp;    When an inbound order message for an unknown account is delivered live to topic order_b2b  
&emsp;&emsp;    Then today's message_received and message_failed rise by 1  

<details markdown>
<summary>Rules exercised and logic log (2 transactions)</summary>


&nbsp;
&nbsp;


**Rules Used** in Scenario: Rejected Message Counts In Daily Totals (live Kafka only)
```
  DailyFlow  
    1. Derive DailyFlow.message_failed as Count(OrderB2bMessage Where Rule.count(derive=models.DailyFlow.message_failed, as_count_of=models.OrderB2bMessage, where=lambda row: row.error_text is not None, insert_parent=True), insert_parent)  
    2. Derive DailyFlow.message_stuck as Formula (1): Rule.formula(derive=models.DailyFlow.message_stuc [...]  
    3. Derive DailyFlow.message_received as Count(OrderB2bMessage Where  - None, insert_parent)  
    4. Derive DailyFlow.message_processed as Count(OrderB2bMessage Where Rule.count(derive=models.DailyFlow.message_processed, as_count_of=models.OrderB2bMessage, where=lambda row: row.is_processed == True, insert_parent=True), insert_parent)  
  OrderB2bMessage  
    5. RowEvent OrderB2bMessage._publish_order_b2b()  
```
**Logic Log** in Scenario: Rejected Message Counts In Daily Totals (live Kafka only) (2 transactions)
```
Logic Phase:		ROW LOGIC		(session=0x10c51d8c0) (sqlalchemy before_flush)			 - 2026-11-19 17:41:44,588 - logic_logger - INFO
..OrderB2bMessage[None] {Insert - client} id: None, received_at: 2026-11-19 17:41:44.588180, payload: {"Account": "Nobody 1795138904584", "Notes": "behave kafka test", "Items": [{"Name": "Widget", "QuantityOrdered": 1}]}, is_processed: False, error_text: None, CreatedOn: None, CreatedOnDay: None  row: 0x10c6db5c0  session: 0x10c51d8c0  ins_upd_dlt: ins, initial: ins - 2026-11-19 17:41:44,588 - logic_logger - INFO
..OrderB2bMessage[None] {early_row_event_all_classes - handle_all did stamping} id: None, received_at: 2026-11-19 17:41:44.588180, payload: {"Account": "Nobody 1795138904584", "Notes": "behave kafka test", "Items": [{"Name": "Widget", "QuantityOrdered": 1}]}, is_processed: False, error_text: None, CreatedOn: 2026-11-19 17:41:44.588563, CreatedOnDay: 2026-11-19  row: 0x10c6db5c0  session: 0x10c51d8c0  ins_upd_dlt: ins, initial: ins - 2026-11-19 17:41:44,588 - logic_logger - INFO
....DailyFlow[2026-11-19] {Update - Adjusting daily_flow: message_received} day: 2026-11-19, order_count: 20, order_amount: 4350.00, message_received:  [5-->] 6, message_processed: 3, message_failed: 2, message_stuck: 0, request_received: 23, request_processed: 20, request_failed: 3, request_stuck: 0  row: 0x10c616db0  session: 0x10c51d8c0  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:44,589 - logic_logger - INFO
....DailyFlow[2026-11-19] {Formula message_stuck} day: 2026-11-19, order_count: 20, order_amount: 4350.00, message_received:  [5-->] 6, message_processed: 3, message_failed: 2, message_stuck:  [0-->] 1, request_received: 23, request_processed: 20, request_failed: 3, request_stuck: 0  row: 0x10c616db0  session: 0x10c51d8c0  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:44,589 - logic_logger - INFO
....DailyFlow[2026-11-19] {Prune Formula: request_stuck [['request_received', 'request_processed', 'request_failed']]} day: 2026-11-19, order_count: 20, order_amount: 4350.00, message_received:  [5-->] 6, message_processed: 3, message_failed: 2, message_stuck:  [0-->] 1, request_received: 23, request_processed: 20, request_failed: 3, request_stuck: 0  row: 0x10c616db0  session: 0x10c51d8c0  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:44,589 - logic_logger - INFO
Logic Phase:		COMMIT LOGIC		(session=0x10c51d8c0)   										 - 2026-11-19 17:41:44,591 - logic_logger - INFO
Logic Phase:		AFTER_FLUSH LOGIC	(session=0x10c51d8c0)   										 - 2026-11-19 17:41:44,593 - logic_logger - INFO
..OrderB2bMessage[114] {AfterFlush Event} id: 114, received_at: 2026-11-19 17:41:44.588180, payload: {"Account": "Nobody 1795138904584", "Notes": "behave kafka test", "Items": [{"Name": "Widget", "QuantityOrdered": 1}]}, is_processed: False, error_text: None, CreatedOn: 2026-11-19 17:41:44.588563, CreatedOnDay: 2026-11-19  row: 0x10c6db5c0  session: 0x10c51d8c0  ins_upd_dlt: ins, initial: ins - 2026-11-19 17:41:44,593 - logic_logger - INFO


Logic Phase:		ROW LOGIC		(session=0x10c51d370) (sqlalchemy before_flush)			 - 2026-11-19 17:41:44,598 - logic_logger - INFO
..OrderB2bMessage[114] {Update - client} id: 114, received_at: 2026-11-19 17:41:44.588180, payload: {"Account": "Nobody 1795138904584", "Notes": "behave kafka test", "Items": [{"Name": "Widget", "QuantityOrdered": 1}]}, is_processed: False, error_text:  [None-->] resolve_lookups: no Customer found for fk_col='customer_id' from source fields, CreatedOn: 2026-11-19 17:41:44.588563, CreatedOnDay: 2026-11-19  row: 0x10cbfa720  session: 0x10c51d370  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:44,599 - logic_logger - INFO
....DailyFlow[2026-11-19] {Update - Adjusting daily_flow: message_failed} day: 2026-11-19, order_count: 20, order_amount: 4350.00, message_received: 6, message_processed: 3, message_failed:  [2-->] 3, message_stuck: 1, request_received: 23, request_processed: 20, request_failed: 3, request_stuck: 0  row: 0x10c616780  session: 0x10c51d370  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:44,599 - logic_logger - INFO
....DailyFlow[2026-11-19] {Formula message_stuck} day: 2026-11-19, order_count: 20, order_amount: 4350.00, message_received: 6, message_processed: 3, message_failed:  [2-->] 3, message_stuck:  [1-->] 0, request_received: 23, request_processed: 20, request_failed: 3, request_stuck: 0  row: 0x10c616780  session: 0x10c51d370  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:44,599 - logic_logger - INFO
....DailyFlow[2026-11-19] {Prune Formula: request_stuck [['request_received', 'request_processed', 'request_failed']]} day: 2026-11-19, order_count: 20, order_amount: 4350.00, message_received: 6, message_processed: 3, message_failed:  [2-->] 3, message_stuck:  [1-->] 0, request_received: 23, request_processed: 20, request_failed: 3, request_stuck: 0  row: 0x10c616780  session: 0x10c51d370  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:44,599 - logic_logger - INFO
Logic Phase:		COMMIT LOGIC		(session=0x10c51d370)   										 - 2026-11-19 17:41:44,599 - logic_logger - INFO
Logic Phase:		AFTER_FLUSH LOGIC	(session=0x10c51d370)   										 - 2026-11-19 17:41:44,600 - logic_logger - INFO
..OrderB2bMessage[114] {AfterFlush Event} id: 114, received_at: 2026-11-19 17:41:44.588180, payload: {"Account": "Nobody 1795138904584", "Notes": "behave kafka test", "Items": [{"Name": "Widget", "QuantityOrdered": 1}]}, is_processed: False, error_text:  [None-->] resolve_lookups: no Customer found for fk_col='customer_id' from source fields, CreatedOn: 2026-11-19 17:41:44.588563, CreatedOnDay: 2026-11-19  row: 0x10cbfa720  session: 0x10c51d370  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:44,600 - logic_logger - INFO

```
</details>

&nbsp;
&nbsp;

#### Scenario: Dashboard Shows Current Data ✅ (0.03 s)
&emsp;  Scenario: Dashboard Shows Current Data  
&emsp;&emsp;    Given Customer "Hugo" with credit limit 5000  
&emsp;&emsp;    When B2B order placed for "Hugo" with 1 Widget  
&emsp;&emsp;    Then the dashboard shows the three charts with today  

<details markdown>
<summary>Rules exercised and logic log (2 transactions)</summary>


&nbsp;
&nbsp;


**Rules Used** in Scenario: Dashboard Shows Current Data
```
  DailyFlow  
    1. Derive DailyFlow.request_processed as Count(OrderB2bRequest Where Rule.count(derive=models.DailyFlow.request_processed, as_count_of=models.OrderB2bRequest, where=lambda row: row.is_processed == True, insert_parent=True), insert_parent)  
    2. Derive DailyFlow.request_failed as Count(OrderB2bRequest Where Rule.count(derive=models.DailyFlow.request_failed, as_count_of=models.OrderB2bRequest, where=lambda row: row.error_text is not None, insert_parent=True), insert_parent)  
    3. Derive DailyFlow.request_stuck as Formula (2): Rule.formula(derive=models.DailyFlow.request_stuc [...]  
    4. Derive DailyFlow.request_received as Count(OrderB2bRequest Where  - None, insert_parent)  
    5. Derive DailyFlow.order_amount as Sum(Order.amount_total Where  - None, insert_parent)  
    6. Derive DailyFlow.order_count as Count(Order Where  - None, insert_parent)  
  Customer  
    7. Derive Customer.balance as Sum(Order.amount_total Where Rule.sum(derive=models.Customer.balance, as_sum_of=models.Order.amount_total, where=lambda row: row.date_shipped is None))  
  Item  
    8. Derive Item.amount as Formula (1): Rule.formula(derive=models.Item.amount, as_expres [...]  
    9. Derive Item.unit_price as Copy(product.unit_price)  
  Order  
    10. RowEvent Order._send_order_to_shipping()  
    11. Derive Order.amount_total as Sum(Item.amount Where  - None)  
```
**Logic Log** in Scenario: Dashboard Shows Current Data (2 transactions)
```
Logic Phase:		ROW LOGIC		(session=0x10c51dd00) (sqlalchemy before_flush)			 - 2026-11-19 17:41:45,125 - logic_logger - INFO
..OrderB2bRequest[None] {Insert - client} id: None, CreatedOn: None, CreatedOnDay: None, payload: {"Account": "Hugo 1795138905117", "Notes": "behave test", "Items": [{"Name": "Widget", "QuantityOrdered": 1}]}, is_processed: False, error_text: None  row: 0x10cba10d0  session: 0x10c51dd00  ins_upd_dlt: ins, initial: ins - 2026-11-19 17:41:45,125 - logic_logger - INFO
..OrderB2bRequest[None] {early_row_event_all_classes - handle_all did stamping} id: None, CreatedOn: 2026-11-19 17:41:45.125564, CreatedOnDay: 2026-11-19, payload: {"Account": "Hugo 1795138905117", "Notes": "behave test", "Items": [{"Name": "Widget", "QuantityOrdered": 1}]}, is_processed: False, error_text: None  row: 0x10cba10d0  session: 0x10c51dd00  ins_upd_dlt: ins, initial: ins - 2026-11-19 17:41:45,125 - logic_logger - INFO
....DailyFlow[2026-11-19] {Update - Adjusting daily_flow: request_received} day: 2026-11-19, order_count: 20, order_amount: 4350.00, message_received: 6, message_processed: 3, message_failed: 3, message_stuck: 0, request_received:  [23-->] 24, request_processed: 20, request_failed: 3, request_stuck: 0  row: 0x10c616af0  session: 0x10c51dd00  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:45,126 - logic_logger - INFO
....DailyFlow[2026-11-19] {Prune Formula: message_stuck [['message_received', 'message_processed', 'message_failed']]} day: 2026-11-19, order_count: 20, order_amount: 4350.00, message_received: 6, message_processed: 3, message_failed: 3, message_stuck: 0, request_received:  [23-->] 24, request_processed: 20, request_failed: 3, request_stuck: 0  row: 0x10c616af0  session: 0x10c51dd00  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:45,126 - logic_logger - INFO
....DailyFlow[2026-11-19] {Formula request_stuck} day: 2026-11-19, order_count: 20, order_amount: 4350.00, message_received: 6, message_processed: 3, message_failed: 3, message_stuck: 0, request_received:  [23-->] 24, request_processed: 20, request_failed: 3, request_stuck:  [0-->] 1  row: 0x10c616af0  session: 0x10c51dd00  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:45,126 - logic_logger - INFO
Logic Phase:		COMMIT LOGIC		(session=0x10c51dd00)   										 - 2026-11-19 17:41:45,126 - logic_logger - INFO
Logic Phase:		AFTER_FLUSH LOGIC	(session=0x10c51dd00)   										 - 2026-11-19 17:41:45,127 - logic_logger - INFO


Logic Phase:		ROW LOGIC		(session=0x10c51dd00) (sqlalchemy before_flush)			 - 2026-11-19 17:41:45,130 - logic_logger - INFO
..OrderB2bRequest[84] {Update - client} id: 84, CreatedOn: 2026-11-19 17:41:45.125564, CreatedOnDay: 2026-11-19, payload: {"Account": "Hugo 1795138905117", "Notes": "behave test", "Items": [{"Name": "Widget", "QuantityOrdered": 1}]}, is_processed:  [False-->] True, error_text: None  row: 0x10cba10d0  session: 0x10c51dd00  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:45,130 - logic_logger - INFO
....DailyFlow[2026-11-19] {Update - Adjusting daily_flow: request_processed} day: 2026-11-19, order_count: 20, order_amount: 4350.00, message_received: 6, message_processed: 3, message_failed: 3, message_stuck: 0, request_received: 24, request_processed:  [20-->] 21, request_failed: 3, request_stuck: 1  row: 0x10c616af0  session: 0x10c51dd00  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:45,130 - logic_logger - INFO
....DailyFlow[2026-11-19] {Prune Formula: message_stuck [['message_received', 'message_processed', 'message_failed']]} day: 2026-11-19, order_count: 20, order_amount: 4350.00, message_received: 6, message_processed: 3, message_failed: 3, message_stuck: 0, request_received: 24, request_processed:  [20-->] 21, request_failed: 3, request_stuck: 1  row: 0x10c616af0  session: 0x10c51dd00  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:45,131 - logic_logger - INFO
....DailyFlow[2026-11-19] {Formula request_stuck} day: 2026-11-19, order_count: 20, order_amount: 4350.00, message_received: 6, message_processed: 3, message_failed: 3, message_stuck: 0, request_received: 24, request_processed:  [20-->] 21, request_failed: 3, request_stuck:  [1-->] 0  row: 0x10c616af0  session: 0x10c51dd00  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:45,131 - logic_logger - INFO
..Product[2] {Update - client} id: 2, name: Widget, count_suppliers: 0, unit_price: 90.0000000000  row: 0x10cbc24a0  session: 0x10c51dd00  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:45,131 - logic_logger - INFO
..Order[None] {Insert - client} id: None, notes: behave test, customer_id: 35, CreatedOn: None, date_shipped: None, amount_total: None, CreatedOnDay: None  row: 0x10c6db890  session: 0x10c51dd00  ins_upd_dlt: ins, initial: ins - 2026-11-19 17:41:45,131 - logic_logger - INFO
..Order[None] {early_row_event_all_classes - handle_all did stamping} id: None, notes: behave test, customer_id: 35, CreatedOn: 2026-11-19, date_shipped: None, amount_total: None, CreatedOnDay: 2026-11-19  row: 0x10c6db890  session: 0x10c51dd00  ins_upd_dlt: ins, initial: ins - 2026-11-19 17:41:45,131 - logic_logger - INFO
..Order[None] {server aggregate_defaults: amount_total } id: None, notes: behave test, customer_id: 35, CreatedOn: 2026-11-19, date_shipped: None, amount_total: 0, CreatedOnDay: 2026-11-19  row: 0x10c6db890  session: 0x10c51dd00  ins_upd_dlt: ins, initial: ins - 2026-11-19 17:41:45,131 - logic_logger - INFO
....DailyFlow[2026-11-19] {Update - Adjusting daily_flow: order_count} day: 2026-11-19, order_count:  [20-->] 21, order_amount: 4350.00, message_received: 6, message_processed: 3, message_failed: 3, message_stuck: 0, request_received: 24, request_processed: 21, request_failed: 3, request_stuck: 0  row: 0x10c616af0  session: 0x10c51dd00  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:45,131 - logic_logger - INFO
....DailyFlow[2026-11-19] {Prune Formula: message_stuck [['message_received', 'message_processed', 'message_failed']]} day: 2026-11-19, order_count:  [20-->] 21, order_amount: 4350.00, message_received: 6, message_processed: 3, message_failed: 3, message_stuck: 0, request_received: 24, request_processed: 21, request_failed: 3, request_stuck: 0  row: 0x10c616af0  session: 0x10c51dd00  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:45,131 - logic_logger - INFO
....DailyFlow[2026-11-19] {Prune Formula: request_stuck [['request_received', 'request_processed', 'request_failed']]} day: 2026-11-19, order_count:  [20-->] 21, order_amount: 4350.00, message_received: 6, message_processed: 3, message_failed: 3, message_stuck: 0, request_received: 24, request_processed: 21, request_failed: 3, request_stuck: 0  row: 0x10c616af0  session: 0x10c51dd00  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:45,131 - logic_logger - INFO
..Item[None] {Insert - client} id: None, order_id: None, product_id: None, quantity: 1, amount: None, unit_price: None  row: 0x10c558950  session: 0x10c51dd00  ins_upd_dlt: ins, initial: ins - 2026-11-19 17:41:45,131 - logic_logger - INFO
..Item[None] {copy_rules for role: product - unit_price} id: None, order_id: None, product_id: None, quantity: 1, amount: None, unit_price: 90.0000000000  row: 0x10c558950  session: 0x10c51dd00  ins_upd_dlt: ins, initial: ins - 2026-11-19 17:41:45,132 - logic_logger - INFO
..Item[None] {Formula amount} id: None, order_id: None, product_id: None, quantity: 1, amount: 90.0000000000, unit_price: 90.0000000000  row: 0x10c558950  session: 0x10c51dd00  ins_upd_dlt: ins, initial: ins - 2026-11-19 17:41:45,132 - logic_logger - INFO
....Order[None] {Update - Adjusting order: amount_total} id: None, notes: behave test, customer_id: 35, CreatedOn: 2026-11-19, date_shipped: None, amount_total:  [0-->] 90.0000000000, CreatedOnDay: 2026-11-19  row: 0x10c6db890  session: 0x10c51dd00  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:45,132 - logic_logger - INFO
......DailyFlow[2026-11-19] {Update - Adjusting daily_flow: order_amount} day: 2026-11-19, order_count: 21, order_amount:  [4350.00-->] 4440.0000000000, message_received: 6, message_processed: 3, message_failed: 3, message_stuck: 0, request_received: 24, request_processed: 21, request_failed: 3, request_stuck: 0  row: 0x10c616af0  session: 0x10c51dd00  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:45,132 - logic_logger - INFO
......DailyFlow[2026-11-19] {Prune Formula: message_stuck [['message_received', 'message_processed', 'message_failed']]} day: 2026-11-19, order_count: 21, order_amount:  [4350.00-->] 4440.0000000000, message_received: 6, message_processed: 3, message_failed: 3, message_stuck: 0, request_received: 24, request_processed: 21, request_failed: 3, request_stuck: 0  row: 0x10c616af0  session: 0x10c51dd00  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:45,132 - logic_logger - INFO
......DailyFlow[2026-11-19] {Prune Formula: request_stuck [['request_received', 'request_processed', 'request_failed']]} day: 2026-11-19, order_count: 21, order_amount:  [4350.00-->] 4440.0000000000, message_received: 6, message_processed: 3, message_failed: 3, message_stuck: 0, request_received: 24, request_processed: 21, request_failed: 3, request_stuck: 0  row: 0x10c616af0  session: 0x10c51dd00  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:45,132 - logic_logger - INFO
......Customer[35] {Update - Adjusting customer: balance} id: 35, name: Hugo 1795138905117, balance:  [0E-10-->] 90.0000000000, credit_limit: 5000.0000000000, email: None, email_opt_out: None  row: 0x10cafe650  session: 0x10c51dd00  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:45,132 - logic_logger - INFO
Logic Phase:		COMMIT LOGIC		(session=0x10c51dd00)   										 - 2026-11-19 17:41:45,132 - logic_logger - INFO
Logic Phase:		AFTER_FLUSH LOGIC	(session=0x10c51dd00)   										 - 2026-11-19 17:41:45,133 - logic_logger - INFO
..Order[182] {AfterFlush Event} id: 182, notes: behave test, customer_id: 35, CreatedOn: 2026-11-19, date_shipped: None, amount_total: 90.0000000000, CreatedOnDay: 2026-11-19  row: 0x10c6db890  session: 0x10c51dd00  ins_upd_dlt: ins, initial: ins - 2026-11-19 17:41:45,133 - logic_logger - INFO

```
</details>

&nbsp;
&nbsp;

### Feature: Row-Level Security  

&nbsp;
&nbsp;

#### Scenario: Sales Role Sees Limited Customers ✅ (0.06 s)
&emsp;  Scenario: Sales Role Sees Limited Customers  
&emsp;&emsp;    Given Customer "Lowlimit" with credit limit 1000  
&emsp;&emsp;    And Customer "Highlimit" with credit limit 5000  
&emsp;&emsp;    And Customer "Owing" with credit limit 1000  
&emsp;&emsp;    And Order is created for "Owing" with 1 Widget  
&emsp;&emsp;    When the sales user lists Customers  
&emsp;&emsp;    Then "Highlimit" and "Owing" are listed, and "Lowlimit" is not  
&emsp;&emsp;    And every listed Customer has credit_limit >= 3000 or balance > 0  

<details markdown>
<summary>Rules exercised and logic log (2 transactions)</summary>


&nbsp;
&nbsp;


**Rules Used** in Scenario: Sales Role Sees Limited Customers
```
  DailyFlow  
    1. Derive DailyFlow.request_processed as Count(OrderB2bRequest Where Rule.count(derive=models.DailyFlow.request_processed, as_count_of=models.OrderB2bRequest, where=lambda row: row.is_processed == True, insert_parent=True), insert_parent)  
    2. Derive DailyFlow.request_failed as Count(OrderB2bRequest Where Rule.count(derive=models.DailyFlow.request_failed, as_count_of=models.OrderB2bRequest, where=lambda row: row.error_text is not None, insert_parent=True), insert_parent)  
    3. Derive DailyFlow.request_stuck as Formula (2): Rule.formula(derive=models.DailyFlow.request_stuc [...]  
    4. Derive DailyFlow.request_received as Count(OrderB2bRequest Where  - None, insert_parent)  
    5. Derive DailyFlow.order_amount as Sum(Order.amount_total Where  - None, insert_parent)  
    6. Derive DailyFlow.order_count as Count(Order Where  - None, insert_parent)  
  Customer  
    7. Derive Customer.balance as Sum(Order.amount_total Where Rule.sum(derive=models.Customer.balance, as_sum_of=models.Order.amount_total, where=lambda row: row.date_shipped is None))  
  Item  
    8. Derive Item.amount as Formula (1): Rule.formula(derive=models.Item.amount, as_expres [...]  
    9. Derive Item.unit_price as Copy(product.unit_price)  
  Order  
    10. RowEvent Order._send_order_to_shipping()  
    11. Derive Order.amount_total as Sum(Item.amount Where  - None)  
```
**Logic Log** in Scenario: Sales Role Sees Limited Customers (2 transactions)
```
Logic Phase:		ROW LOGIC		(session=0x10c51cd10) (sqlalchemy before_flush)			 - 2026-11-19 17:41:45,158 - logic_logger - INFO
..OrderB2bRequest[None] {Insert - client} id: None, CreatedOn: None, CreatedOnDay: None, payload: {"Account": "Owing 1795138905154", "Notes": "behave test", "Items": [{"Name": "Widget", "QuantityOrdered": 1}]}, is_processed: False, error_text: None  row: 0x10c5d2ed0  session: 0x10c51cd10  ins_upd_dlt: ins, initial: ins - 2026-11-19 17:41:45,158 - logic_logger - INFO
..OrderB2bRequest[None] {early_row_event_all_classes - handle_all did stamping} id: None, CreatedOn: 2026-11-19 17:41:45.158761, CreatedOnDay: 2026-11-19, payload: {"Account": "Owing 1795138905154", "Notes": "behave test", "Items": [{"Name": "Widget", "QuantityOrdered": 1}]}, is_processed: False, error_text: None  row: 0x10c5d2ed0  session: 0x10c51cd10  ins_upd_dlt: ins, initial: ins - 2026-11-19 17:41:45,158 - logic_logger - INFO
....DailyFlow[2026-11-19] {Update - Adjusting daily_flow: request_received} day: 2026-11-19, order_count: 21, order_amount: 4440.00, message_received: 6, message_processed: 3, message_failed: 3, message_stuck: 0, request_received:  [24-->] 25, request_processed: 21, request_failed: 3, request_stuck: 0  row: 0x10c616ba0  session: 0x10c51cd10  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:45,159 - logic_logger - INFO
....DailyFlow[2026-11-19] {Prune Formula: message_stuck [['message_received', 'message_processed', 'message_failed']]} day: 2026-11-19, order_count: 21, order_amount: 4440.00, message_received: 6, message_processed: 3, message_failed: 3, message_stuck: 0, request_received:  [24-->] 25, request_processed: 21, request_failed: 3, request_stuck: 0  row: 0x10c616ba0  session: 0x10c51cd10  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:45,159 - logic_logger - INFO
....DailyFlow[2026-11-19] {Formula request_stuck} day: 2026-11-19, order_count: 21, order_amount: 4440.00, message_received: 6, message_processed: 3, message_failed: 3, message_stuck: 0, request_received:  [24-->] 25, request_processed: 21, request_failed: 3, request_stuck:  [0-->] 1  row: 0x10c616ba0  session: 0x10c51cd10  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:45,159 - logic_logger - INFO
Logic Phase:		COMMIT LOGIC		(session=0x10c51cd10)   										 - 2026-11-19 17:41:45,159 - logic_logger - INFO
Logic Phase:		AFTER_FLUSH LOGIC	(session=0x10c51cd10)   										 - 2026-11-19 17:41:45,159 - logic_logger - INFO


Logic Phase:		ROW LOGIC		(session=0x10c51cd10) (sqlalchemy before_flush)			 - 2026-11-19 17:41:45,161 - logic_logger - INFO
..OrderB2bRequest[85] {Update - client} id: 85, CreatedOn: 2026-11-19 17:41:45.158761, CreatedOnDay: 2026-11-19, payload: {"Account": "Owing 1795138905154", "Notes": "behave test", "Items": [{"Name": "Widget", "QuantityOrdered": 1}]}, is_processed:  [False-->] True, error_text: None  row: 0x10c5d2ed0  session: 0x10c51cd10  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:45,161 - logic_logger - INFO
....DailyFlow[2026-11-19] {Update - Adjusting daily_flow: request_processed} day: 2026-11-19, order_count: 21, order_amount: 4440.00, message_received: 6, message_processed: 3, message_failed: 3, message_stuck: 0, request_received: 25, request_processed:  [21-->] 22, request_failed: 3, request_stuck: 1  row: 0x10c616ba0  session: 0x10c51cd10  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:45,162 - logic_logger - INFO
....DailyFlow[2026-11-19] {Prune Formula: message_stuck [['message_received', 'message_processed', 'message_failed']]} day: 2026-11-19, order_count: 21, order_amount: 4440.00, message_received: 6, message_processed: 3, message_failed: 3, message_stuck: 0, request_received: 25, request_processed:  [21-->] 22, request_failed: 3, request_stuck: 1  row: 0x10c616ba0  session: 0x10c51cd10  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:45,162 - logic_logger - INFO
....DailyFlow[2026-11-19] {Formula request_stuck} day: 2026-11-19, order_count: 21, order_amount: 4440.00, message_received: 6, message_processed: 3, message_failed: 3, message_stuck: 0, request_received: 25, request_processed:  [21-->] 22, request_failed: 3, request_stuck:  [1-->] 0  row: 0x10c616ba0  session: 0x10c51cd10  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:45,162 - logic_logger - INFO
..Product[2] {Update - client} id: 2, name: Widget, count_suppliers: 0, unit_price: 90.0000000000  row: 0x10cbc2f20  session: 0x10c51cd10  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:45,162 - logic_logger - INFO
..Order[None] {Insert - client} id: None, notes: behave test, customer_id: 38, CreatedOn: None, date_shipped: None, amount_total: None, CreatedOnDay: None  row: 0x10cbfa600  session: 0x10c51cd10  ins_upd_dlt: ins, initial: ins - 2026-11-19 17:41:45,162 - logic_logger - INFO
..Order[None] {early_row_event_all_classes - handle_all did stamping} id: None, notes: behave test, customer_id: 38, CreatedOn: 2026-11-19, date_shipped: None, amount_total: None, CreatedOnDay: 2026-11-19  row: 0x10cbfa600  session: 0x10c51cd10  ins_upd_dlt: ins, initial: ins - 2026-11-19 17:41:45,162 - logic_logger - INFO
..Order[None] {server aggregate_defaults: amount_total } id: None, notes: behave test, customer_id: 38, CreatedOn: 2026-11-19, date_shipped: None, amount_total: 0, CreatedOnDay: 2026-11-19  row: 0x10cbfa600  session: 0x10c51cd10  ins_upd_dlt: ins, initial: ins - 2026-11-19 17:41:45,162 - logic_logger - INFO
....DailyFlow[2026-11-19] {Update - Adjusting daily_flow: order_count} day: 2026-11-19, order_count:  [21-->] 22, order_amount: 4440.00, message_received: 6, message_processed: 3, message_failed: 3, message_stuck: 0, request_received: 25, request_processed: 22, request_failed: 3, request_stuck: 0  row: 0x10c616ba0  session: 0x10c51cd10  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:45,162 - logic_logger - INFO
....DailyFlow[2026-11-19] {Prune Formula: message_stuck [['message_received', 'message_processed', 'message_failed']]} day: 2026-11-19, order_count:  [21-->] 22, order_amount: 4440.00, message_received: 6, message_processed: 3, message_failed: 3, message_stuck: 0, request_received: 25, request_processed: 22, request_failed: 3, request_stuck: 0  row: 0x10c616ba0  session: 0x10c51cd10  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:45,162 - logic_logger - INFO
....DailyFlow[2026-11-19] {Prune Formula: request_stuck [['request_received', 'request_processed', 'request_failed']]} day: 2026-11-19, order_count:  [21-->] 22, order_amount: 4440.00, message_received: 6, message_processed: 3, message_failed: 3, message_stuck: 0, request_received: 25, request_processed: 22, request_failed: 3, request_stuck: 0  row: 0x10c616ba0  session: 0x10c51cd10  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:45,162 - logic_logger - INFO
..Item[None] {Insert - client} id: None, order_id: None, product_id: None, quantity: 1, amount: None, unit_price: None  row: 0x10cb834d0  session: 0x10c51cd10  ins_upd_dlt: ins, initial: ins - 2026-11-19 17:41:45,162 - logic_logger - INFO
..Item[None] {copy_rules for role: product - unit_price} id: None, order_id: None, product_id: None, quantity: 1, amount: None, unit_price: 90.0000000000  row: 0x10cb834d0  session: 0x10c51cd10  ins_upd_dlt: ins, initial: ins - 2026-11-19 17:41:45,162 - logic_logger - INFO
..Item[None] {Formula amount} id: None, order_id: None, product_id: None, quantity: 1, amount: 90.0000000000, unit_price: 90.0000000000  row: 0x10cb834d0  session: 0x10c51cd10  ins_upd_dlt: ins, initial: ins - 2026-11-19 17:41:45,162 - logic_logger - INFO
....Order[None] {Update - Adjusting order: amount_total} id: None, notes: behave test, customer_id: 38, CreatedOn: 2026-11-19, date_shipped: None, amount_total:  [0-->] 90.0000000000, CreatedOnDay: 2026-11-19  row: 0x10cbfa600  session: 0x10c51cd10  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:45,163 - logic_logger - INFO
......DailyFlow[2026-11-19] {Update - Adjusting daily_flow: order_amount} day: 2026-11-19, order_count: 22, order_amount:  [4440.00-->] 4530.0000000000, message_received: 6, message_processed: 3, message_failed: 3, message_stuck: 0, request_received: 25, request_processed: 22, request_failed: 3, request_stuck: 0  row: 0x10c616ba0  session: 0x10c51cd10  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:45,163 - logic_logger - INFO
......DailyFlow[2026-11-19] {Prune Formula: message_stuck [['message_received', 'message_processed', 'message_failed']]} day: 2026-11-19, order_count: 22, order_amount:  [4440.00-->] 4530.0000000000, message_received: 6, message_processed: 3, message_failed: 3, message_stuck: 0, request_received: 25, request_processed: 22, request_failed: 3, request_stuck: 0  row: 0x10c616ba0  session: 0x10c51cd10  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:45,163 - logic_logger - INFO
......DailyFlow[2026-11-19] {Prune Formula: request_stuck [['request_received', 'request_processed', 'request_failed']]} day: 2026-11-19, order_count: 22, order_amount:  [4440.00-->] 4530.0000000000, message_received: 6, message_processed: 3, message_failed: 3, message_stuck: 0, request_received: 25, request_processed: 22, request_failed: 3, request_stuck: 0  row: 0x10c616ba0  session: 0x10c51cd10  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:45,163 - logic_logger - INFO
......Customer[38] {Update - Adjusting customer: balance} id: 38, name: Owing 1795138905154, balance:  [0E-10-->] 90.0000000000, credit_limit: 1000.0000000000, email: None, email_opt_out: None  row: 0x10c5eb3d0  session: 0x10c51cd10  ins_upd_dlt: upd, initial: upd - 2026-11-19 17:41:45,163 - logic_logger - INFO
Logic Phase:		COMMIT LOGIC		(session=0x10c51cd10)   										 - 2026-11-19 17:41:45,163 - logic_logger - INFO
Logic Phase:		AFTER_FLUSH LOGIC	(session=0x10c51cd10)   										 - 2026-11-19 17:41:45,164 - logic_logger - INFO
..Order[183] {AfterFlush Event} id: 183, notes: behave test, customer_id: 38, CreatedOn: 2026-11-19, date_shipped: None, amount_total: 90.0000000000, CreatedOnDay: 2026-11-19  row: 0x10cbfa600  session: 0x10c51cd10  ins_upd_dlt: ins, initial: ins - 2026-11-19 17:41:45,164 - logic_logger - INFO

```
</details>

&nbsp;&nbsp;  
/Users/val/dev/genai-logic/ApiLogicServer-dev/build_and_test/genai-logic/demo_eai/test/api_logic_server_behave/behave_run.py completed at November 19, 2026 17:41:45  
Behave run time: 3.448 s  


&nbsp;
&nbsp;

## Provenance

| | |
|---|---|
| Generated | November 19, 2026 18:04 |
| Generator | `requirements_traceability_report.py` 2.15 |
| Report text from | reports/Requirements Traceability Report Template.md (sha256 a19673a13fa0) |
| Tests last ran | November 19, 2026 17:41 |
| Project | basic_demo_eai |
| Source commit | d00612d6 (uncommitted changes) |
| Project created | November 19, 2026 17:33:29 |
| Requirement files read | `docs/requirements/check_credit/requirements.md` (sha256 58c5b552)<br>`docs/requirements/demo_eai/requirements.md` (sha256 5f955924)<br>`docs/requirements/order_b2b_consume/requirements.md` (sha256 e0565187)<br>`docs/requirements/order_flow_totals/requirements.md` (sha256 56547080)<br>`docs/requirements/order_shipping_publish/requirements.md` (sha256 fb4f0885) |
| Regenerate | `python requirements_traceability_report.py run`, from `test/api_logic_server_behave` |

_The report is derived from the project's files and the last test run; nothing in it is stored anywhere else, so regenerating it always reflects the project as it is now._

