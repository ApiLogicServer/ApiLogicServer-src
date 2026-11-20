# Requirements Traceability Report

This report shows requirements, the rules created from them, and the tests created from those rules.

This project began as natural-language requirements, fleshed out by AI into a running system of business rules that are *executable documentation*. This report is how you govern the result.

A governable system is one you can **read**, **trust**, and **maintain**: each requirement is listed beside the rules that implement it (*read*); the tests and logic logs show those rules running (*trust*); re-run it after any change and it flags the gaps — an untested requirement, an untraced rule, a channel no test checks (*maintain*).

It is generated from the project's own files, nothing written by hand, so it is as current as the last run and covers the whole project, not a sample. Open **Background** (below the summary) for what the terms mean, how to read the report, and what it can and can't tell you.


**Project:** basic_demo_eai &nbsp;|&nbsp; **Generated:** November 19, 2026 19:46 &nbsp;|&nbsp; **Rules:** 18 &nbsp;|&nbsp; **Test scenarios:** 35 &nbsp;|&nbsp; **Generator:** requirements_traceability_report.py 2.15

**Last test run:** November 19, 2026 19:46, took 7.4 s (0m before this report; test results and logic logs below are from that run)


&nbsp;
&nbsp;

## At a Glance

**✅ 6 requirement(s), all implemented; 6 tested; 35 of 35 scenarios passed; last run 0m ago.**

| | |
|---|---|
| Requirements | 6 (6 implemented) |
| Tested | 6 of 6 |
| Last test run | ✅ 35 passed, 0 failed (November 19, 2026 19:46, 0m ago); took 7.4 s |
| Rules | 18 (15 declarative, 0 Python functions, 3 Python events) |
| Rules shown running in a test log | 17 of 18 |
| Security | enabled (Keycloak provider); 11 role(s), 2 row-level grant(s) |
| Messages and APIs | 2 Kafka topic(s) in, 2 out; 5 HTTP endpoint(s) |
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
| Test results (last run) | ✅ 35 passed, 0 failed; took 7.4 s |
| Scenarios with a logic log | 33 of 35 |
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
| §1 Business Logic — Check Credit | [logic/logic_discovery/check_credit.py](../../logic/logic_discovery/check_credit.py) | 5 | ✅ 12 scenario(s): 12 passed |
| §2 B2B API — Accept orders from external partners | [api/api_discovery/order_b2b_service.py](../../api/api_discovery/order_b2b_service.py) | 0 | ✅ 3 scenario(s): 3 passed |
| §3 Kafka Subscribe — Inbound orders from sales channel | [logic/logic_discovery/order_b2b_consume.py](../../logic/logic_discovery/order_b2b_consume.py)<br>[integration/kafka/kafka_subscribe_discovery/order_b2b.py](../../integration/kafka/kafka_subscribe_discovery/order_b2b.py)<br>[integration/OrderB2bKafkaMapper.py](../../integration/OrderB2bKafkaMapper.py)<br>[api/api_discovery/order_b2b_kafka_consume_debug.py](../../api/api_discovery/order_b2b_kafka_consume_debug.py) | 1 | ✅ 3 scenario(s): 3 passed |
| §4 Kafka Publish — Notify shipping on dispatch | [logic/logic_discovery/shipping_notification.py](../../logic/logic_discovery/shipping_notification.py)<br>[integration/kafka/kafka_publish_discovery/order_shipping.py](../../integration/kafka/kafka_publish_discovery/order_shipping.py) | 1 | ✅ 3 scenario(s): 3 passed |
| §5 Security | [security/declare_security.py](../../security/declare_security.py) | 0 | ✅ 3 scenario(s): 3 passed |
| §6 Operations Dashboard — Order flow | [logic/logic_discovery/order_flow_dashboard.py](../../logic/logic_discovery/order_flow_dashboard.py)<br>[api/api_discovery/dashboard_services.py](../../api/api_discovery/dashboard_services.py) | 10 | ✅ 11 scenario(s): 11 passed |


&nbsp;

### Rule coverage by tests

| Rule | Requirement | Seen in |
|---|---|---|
| `Item.unit_price = copy of Product.unit_price` | §1 Business Logic — Check Credit | 25: Partner order is mapped and the request recorded as processed; Good order is priced and added to the balance; Changing an item quantity re-derives amount, total and balance; +22 more |
| `Item.amount = quantity * unit_price` | §1 Business Logic — Check Credit | 25: Partner order is mapped and the request recorded as processed; Good order is priced and added to the balance; Changing an item quantity re-derives amount, total and balance; +22 more |
| `Order.amount_total = sum(Item.amount)` | §1 Business Logic — Check Credit | 25: Partner order is mapped and the request recorded as processed; Good order is priced and added to the balance; Changing an item quantity re-derives amount, total and balance; +22 more |
| `Customer.balance = sum(Order.amount_total) where date_shipped is None` | §1 Business Logic — Check Credit | 25: Partner order is mapped and the request recorded as processed; Good order is priced and added to the balance; Changing an item quantity re-derives amount, total and balance; +22 more |
| `Customer: balance <= credit_limit` | §1 Business Logic — Check Credit | 2: Order over the credit limit is rejected; Raising a quantity over the credit limit is rejected |
| `OrderB2bMessage.after_flush_row_event → _publish_order_b2b()` | §3 Kafka Subscribe — Inbound orders from sales channel | 6: Order message for a known customer creates the order; Order message with an unknown product is rejected; Rejected message stays on the blob with its error (live Kafka only); +3 more |
| `DailyFlow.order_count = count(Order)` | §6 Operations Dashboard — Order flow | 25: Partner order is mapped and the request recorded as processed; Good order is priced and added to the balance; Changing an item quantity re-derives amount, total and balance; +22 more |
| `DailyFlow.order_amount = sum(Order.amount_total)` | §6 Operations Dashboard — Order flow | 25: Partner order is mapped and the request recorded as processed; Good order is priced and added to the balance; Changing an item quantity re-derives amount, total and balance; +22 more |
| `DailyFlow.message_received = count(OrderB2bMessage)` | §6 Operations Dashboard — Order flow | 6: Order message for a known customer creates the order; Order message with an unknown product is rejected; Rejected message stays on the blob with its error (live Kafka only); +3 more |
| `DailyFlow.message_processed = count(OrderB2bMessage) where is_processed == True` | §6 Operations Dashboard — Order flow | 6: Order message for a known customer creates the order; Order message with an unknown product is rejected; Rejected message stays on the blob with its error (live Kafka only); +3 more |
| `DailyFlow.message_rejected = count(OrderB2bMessage) where error_text is not None` | §6 Operations Dashboard — Order flow | 6: Order message for a known customer creates the order; Order message with an unknown product is rejected; Rejected message stays on the blob with its error (live Kafka only); +3 more |
| `DailyFlow.message_pending = (message_received or 0) - (message_processed or 0) - (message_rejected or 0)` | §6 Operations Dashboard — Order flow | 6: Order message for a known customer creates the order; Order message with an unknown product is rejected; Rejected message stays on the blob with its error (live Kafka only); +3 more |
| `DailyFlow.request_received = count(OrderB2bRequest)` | §6 Operations Dashboard — Order flow | 24: Partner order is mapped and the request recorded as processed; Partner order with an unknown product is rejected and the request recorded with its error; Partner order for an unknown account is rejected; +21 more |
| `DailyFlow.request_processed = count(OrderB2bRequest) where is_processed == True` | §6 Operations Dashboard — Order flow | 24: Partner order is mapped and the request recorded as processed; Partner order with an unknown product is rejected and the request recorded with its error; Partner order for an unknown account is rejected; +21 more |
| `DailyFlow.request_rejected = count(OrderB2bRequest) where error_text is not None` | §6 Operations Dashboard — Order flow | 24: Partner order is mapped and the request recorded as processed; Partner order with an unknown product is rejected and the request recorded with its error; Partner order for an unknown account is rejected; +21 more |
| `DailyFlow.request_pending = (request_received or 0) - (request_processed or 0) - (request_rejected or 0)` | §6 Operations Dashboard — Order flow | 24: Partner order is mapped and the request recorded as processed; Partner order with an unknown product is rejected and the request recorded with its error; Partner order for an unknown account is rejected; +21 more |
| `Order.after_flush_row_event → _send_order_to_shipping()` | §4 Kafka Publish — Notify shipping on dispatch | 24: Partner order is mapped and the request recorded as processed; Good order is priced and added to the balance; Changing an item quantity re-derives amount, total and balance; +21 more |
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

Tests: ✅ 12 scenario(s): 12 passed

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
| `Item.unit_price = copy of Product.unit_price` | copy | declarative |  | [check_credit.py](../../logic/logic_discovery/check_credit.py) |
| `Item.amount = quantity * unit_price` | formula | declarative |  | [check_credit.py](../../logic/logic_discovery/check_credit.py) |
| `Order.amount_total = sum(Item.amount)` | sum | declarative |  | [check_credit.py](../../logic/logic_discovery/check_credit.py) |
| `Customer.balance = sum(Order.amount_total) where date_shipped is None` | sum | declarative |  | [check_credit.py](../../logic/logic_discovery/check_credit.py) |
| `Customer: balance <= credit_limit` | constraint | declarative | Error: Customer balance ({row.balance}) exceeds credit limit ({row.credit_limit}) | [check_credit.py](../../logic/logic_discovery/check_credit.py) |

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

Tests: ✅ 3 scenario(s): 3 passed

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
| `HTTP in: POST /api/OrderB2B/OrderB2B` | http | handler (Python) | API service OrderB2B: accepts a partner order, records the request with its outcome, and creates the Order. | [order_b2b_service.py](../../api/api_discovery/order_b2b_service.py) |

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
| `OrderB2bMessage.after_flush_row_event → _publish_order_b2b()` | after_flush_row_event | event (Python) | OrderB2bMessage event: publishes the raw blob to order_b2b_processed after Tx 1 commits, so consumer 2 can parse it in a clean Tx 2 (2-message pattern). | [order_b2b_consume.py](../../logic/logic_discovery/order_b2b_consume.py) |
| `Kafka in: order_b2b` | kafka | handler (Python) | Kafka subscribe order_b2b: consumer 1 saves the raw message as an OrderB2bMessage blob (Tx 1). | [order_b2b.py](../../integration/kafka/kafka_subscribe_discovery/order_b2b.py) |
| `Kafka in: order_b2b_processed` | kafka | handler (Python) | Kafka subscribe order_b2b_processed: consumer 2 parses the blob into Order + Items (Tx 2). | [order_b2b.py](../../integration/kafka/kafka_subscribe_discovery/order_b2b.py) |
| `OrderB2bKafkaMapper.py` | module |  | Feature: Kafka Subscribe Order Integration | [OrderB2bKafkaMapper.py](../../integration/OrderB2bKafkaMapper.py) |
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

1. `OrderB2bMessage` → `_publish_order_b2b` (after_flush) — OrderB2bMessage event: publishes the raw blob to order_b2b_processed after Tx 1 commits, so consumer 2

</td>
</tr></table>

</details>

#### §4 Kafka Publish — Notify shipping on dispatch

Tests: ✅ 3 scenario(s): 3 passed

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
| `Order.after_flush_row_event → _send_order_to_shipping()` | after_flush_row_event | event (Python) | Order publish: sends the Order to Kafka topic order_shipping when date_shipped is set (insert with a value, or an update that changes it), shaped by example from message_formats/order_shipping.json. | [shipping_notification.py](../../logic/logic_discovery/shipping_notification.py) |
| `order_shipping.py` | module |  | Feature: Kafka Publish Shipping Notification | [order_shipping.py](../../integration/kafka/kafka_publish_discovery/order_shipping.py) |

<details markdown>
<summary>Logic diagram: shipping_notification</summary>

<table><tr valign="top">
<td width="65%">

![logic diagram: shipping_notification](shipping_notification/logic_diagrams/logic_diagram_shipping_notification.svg)

</td>
<td width="35%">

**Rules**

1. `Order` → `_send_order_to_shipping` (after_flush) — Order publish: sends the Order to Kafka topic order_shipping when date_shipped is set (insert with a value,

</td>
</tr></table>

</details>

#### §5 Security

Tests: ✅ 3 scenario(s): 3 passed

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

Tests: ✅ 11 scenario(s): 11 passed

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
| `DailyFlow.order_count = count(Order)` | count | declarative |  | [order_flow_dashboard.py](../../logic/logic_discovery/order_flow_dashboard.py) |
| `DailyFlow.order_amount = sum(Order.amount_total)` | sum | declarative |  | [order_flow_dashboard.py](../../logic/logic_discovery/order_flow_dashboard.py) |
| `DailyFlow.message_received = count(OrderB2bMessage)` | count | declarative |  | [order_flow_dashboard.py](../../logic/logic_discovery/order_flow_dashboard.py) |
| `DailyFlow.message_processed = count(OrderB2bMessage) where is_processed == True` | count | declarative |  | [order_flow_dashboard.py](../../logic/logic_discovery/order_flow_dashboard.py) |
| `DailyFlow.message_rejected = count(OrderB2bMessage) where error_text is not None` | count | declarative |  | [order_flow_dashboard.py](../../logic/logic_discovery/order_flow_dashboard.py) |
| `DailyFlow.message_pending = (message_received or 0) - (message_processed or 0) - (message_rejected or 0)` | formula | declarative |  | [order_flow_dashboard.py](../../logic/logic_discovery/order_flow_dashboard.py) |
| `DailyFlow.request_received = count(OrderB2bRequest)` | count | declarative |  | [order_flow_dashboard.py](../../logic/logic_discovery/order_flow_dashboard.py) |
| `DailyFlow.request_processed = count(OrderB2bRequest) where is_processed == True` | count | declarative |  | [order_flow_dashboard.py](../../logic/logic_discovery/order_flow_dashboard.py) |
| `DailyFlow.request_rejected = count(OrderB2bRequest) where error_text is not None` | count | declarative |  | [order_flow_dashboard.py](../../logic/logic_discovery/order_flow_dashboard.py) |
| `DailyFlow.request_pending = (request_received or 0) - (request_processed or 0) - (request_rejected or 0)` | formula | declarative |  | [order_flow_dashboard.py](../../logic/logic_discovery/order_flow_dashboard.py) |
| `HTTP in: GET /dashboard` | http | handler (Python) | API service dashboard: two order-flow charts side by side, each in its own iframe. | [dashboard_services.py](../../api/api_discovery/dashboard_services.py) |
| `HTTP in: GET /chart_graphics/<path:path>` | http | handler (Python) | API service dashboard: renders one chart as HTML - on EVERY request (never cached), so data is current. | [dashboard_services.py](../../api/api_discovery/dashboard_services.py) |

<details markdown>
<summary>Logic diagram: order_flow_dashboard</summary>

<table><tr valign="top">
<td width="65%">

![logic diagram: order_flow_dashboard](order_flow_dashboard/logic_diagrams/logic_diagram_order_flow_dashboard.svg)

</td>
<td width="35%">

**Rules**

1. `message_pending = (message_received or 0) - (message_processed or 0) - (message_rejected or 0)`<br>
2. `request_pending = (request_received or 0) - (request_processed or 0) - (request_rejected or 0)`<br>
3. `order_amount = sum(amount_total)`<br>
4. `order_count = count(Order)`<br>
5. `message_received = count(OrderB2bMessage)`<br>
6. `message_processed = count(OrderB2bMessage where is_processed)`<br>
7. `message_rejected = count(OrderB2bMessage where error_text)`<br>
8. `request_received = count(OrderB2bRequest)`<br>
9. `request_processed = count(OrderB2bRequest where is_processed)`<br>
10. `request_rejected = count(OrderB2bRequest where error_text)`

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
| Item | unit_price | copy | `Item.unit_price = copy of Product.unit_price` |
| Item | amount | formula | `Item.amount = quantity * unit_price` |
| Order | amount_total | sum | `Order.amount_total = sum(Item.amount)` |
| Customer | balance | sum | `Customer.balance = sum(Order.amount_total) where date_shipped is None` |
| DailyFlow | order_count | count | `DailyFlow.order_count = count(Order)` |
| DailyFlow | order_amount | sum | `DailyFlow.order_amount = sum(Order.amount_total)` |
| DailyFlow | message_received | count | `DailyFlow.message_received = count(OrderB2bMessage)` |
| DailyFlow | message_processed | count | `DailyFlow.message_processed = count(OrderB2bMessage) where is_processed == True` |
| DailyFlow | message_rejected | count | `DailyFlow.message_rejected = count(OrderB2bMessage) where error_text is not None` |
| DailyFlow | message_pending | formula | `DailyFlow.message_pending = (message_received or 0) - (message_processed or 0) - (message_rejected or 0)` |
| DailyFlow | request_received | count | `DailyFlow.request_received = count(OrderB2bRequest)` |
| DailyFlow | request_processed | count | `DailyFlow.request_processed = count(OrderB2bRequest) where is_processed == True` |
| DailyFlow | request_rejected | count | `DailyFlow.request_rejected = count(OrderB2bRequest) where error_text is not None` |
| DailyFlow | request_pending | formula | `DailyFlow.request_pending = (request_received or 0) - (request_processed or 0) - (request_rejected or 0)` |


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
| ➡ in | Kafka | `order_b2b` | ✅ live | `order_b2b()` - Kafka subscribe order_b2b: consumer 1 saves the raw message as an OrderB2bMessage blob (Tx 1). | OrderB2bMessage | [order_b2b.json](../../integration/kafka/message_formats/order_b2b.json) | §3 Kafka Subscribe — Inbound orders from sales channel |
| ➡ in | Kafka | `order_b2b_processed` | ✅ live | `order_b2b_processed()` - Kafka subscribe order_b2b_processed: consumer 2 parses the blob into Order + Items (Tx 2). | Item, Order, OrderB2bMessage |  | §3 Kafka Subscribe — Inbound orders from sales channel |
| ⬅ out | Kafka | `order_b2b_processed` | ✅ live | OrderB2bMessage.after_flush_row_event → _publish_order_b2b() - OrderB2bMessage event: publishes the raw blob to order_b2b_processed after Tx 1 commits, so consumer 2 can parse it in a clean Tx 2 (2-message pattern). |  |  | §3 Kafka Subscribe — Inbound orders from sales channel |
| ⬅ out | Kafka | `order_shipping` | ⚠ message checked in the log, not on the topic | Order.after_flush_row_event → _send_order_to_shipping() - Order publish: sends the Order to Kafka topic order_shipping when date_shipped is set (insert with a value, or an update that changes it), shaped by example from message_formats/order_shipping.json. |  | [order_shipping.json](../../integration/kafka/message_formats/order_shipping.json) | §4 Kafka Publish — Notify shipping on dispatch |
| ➡ in | HTTP | `GET /dashboard` | ⚠ no test mentions it | `dashboard()` - API service dashboard: two order-flow charts side by side, each in its own iframe. |  |  | §6 Operations Dashboard — Order flow |
| ➡ in | HTTP | `GET /chart_graphics/<path:path>` | ⚠ no test mentions it | `chart_graphics()` - API service dashboard: renders one chart as HTML - on EVERY request (never cached), so data is current. |  |  | §6 Operations Dashboard — Order flow |
| ➡ in | HTTP | `GET /consume_debug/order_b2b` | ✅ | `register_consume_debug()` - EAI debug (development only, no authentication): sends the message in ?file= to the topic, live through Kafka or simulated |  |  | §3 Kafka Subscribe — Inbound orders from sales channel |
| ➡ in | HTTP | `POST /consume_debug/order_b2b/reset` | ⚠ no test mentions it | `register_queue_reset()` - EAI debug (development only, destructive): purges the messages in the pipeline's topics |  |  | §3 Kafka Subscribe — Inbound orders from sales channel |
| ➡ in | HTTP | `POST /api/OrderB2B/OrderB2B` | ✅ | `OrderB2B()` - API service OrderB2B: accepts a partner order, records the request with its outcome, and creates the Order. |  |  | §2 B2B API — Accept orders from external partners |

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

**✅ 35 scenario(s): 35 passed, 0 failed; took 7.4 s** (from the last run, `logs/behave.log`).

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

#### Scenario: Partner order is mapped and the request recorded as processed ✅ (0.06 s)
&emsp;  Scenario: Partner order is mapped and the request recorded as processed  
&emsp;&emsp;    Given a new customer "Partner Co" with credit limit 5000  
&emsp;&emsp;    When a B2B order is placed for "Partner Co" with 3 Widget and 2 Gadget  
&emsp;&emsp;    Then the order is accepted  
&emsp;&emsp;    And the order belongs to "Partner Co"  
&emsp;&emsp;    And the order items are 3 Widget and 2 Gadget  
&emsp;&emsp;    And the B2B request is recorded as processed  

<details markdown>
<summary>Rules exercised and logic log (2 transactions)</summary>


&nbsp;
&nbsp;


**Rules Used** in Scenario: Partner order is mapped and the request recorded as processed
```
  DailyFlow  
    1. Derive DailyFlow.request_rejected as Count(OrderB2bRequest Where Rule.count(derive=models.DailyFlow.request_rejected, as_count_of=models.OrderB2bRequest, where=lambda row: row.error_text is not None, insert_parent=True), insert_parent)  
    2. Derive DailyFlow.request_pending as Formula (2): Rule.formula(derive=models.DailyFlow.request_pend [...]  
    3. Derive DailyFlow.request_processed as Count(OrderB2bRequest Where Rule.count(derive=models.DailyFlow.request_processed, as_count_of=models.OrderB2bRequest, where=lambda row: row.is_processed == True, insert_parent=True), insert_parent)  
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
**Logic Log** in Scenario: Partner order is mapped and the request recorded as processed (2 transactions)
```
Logic Phase:		ROW LOGIC		(session=0x10e313610) (sqlalchemy before_flush)			 - 2026-11-19 19:46:01,657 - logic_logger - INFO
..OrderB2bRequest[None] {Insert - client} id: None, CreatedOn: None, CreatedOnDay: None, payload: {"Account": "Partner Co 1795146361620", "Notes": "behave test", "Items": [{"Name": "Widget", "QuantityOrdered": 3}, {"Name": "Gadget", "QuantityOrdered": 2}]}, is_processed: False, error_text: None  row: 0x10e3e6650  session: 0x10e313610  ins_upd_dlt: ins, initial: ins - 2026-11-19 19:46:01,657 - logic_logger - INFO
..OrderB2bRequest[None] {early_row_event_all_classes - handle_all did stamping} id: None, CreatedOn: 2026-11-19 19:46:01.657140, CreatedOnDay: 2026-11-19, payload: {"Account": "Partner Co 1795146361620", "Notes": "behave test", "Items": [{"Name": "Widget", "QuantityOrdered": 3}, {"Name": "Gadget", "QuantityOrdered": 2}]}, is_processed: False, error_text: None  row: 0x10e3e6650  session: 0x10e313610  ins_upd_dlt: ins, initial: ins - 2026-11-19 19:46:01,657 - logic_logger - INFO
....DailyFlow[2026-11-19] {Update - Adjusting daily_flow: request_received} day: 2026-11-19, order_count: 27, order_amount: 8010.00, message_received: 8, message_processed: 4, message_rejected: 3, message_pending: 1, request_received:  [30-->] 31, request_processed: 24, request_rejected: 5, request_pending: 1  row: 0x10e2362b0  session: 0x10e313610  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:01,657 - logic_logger - INFO
....DailyFlow[2026-11-19] {Prune Formula: message_pending [['message_received', 'message_processed', 'message_rejected']]} day: 2026-11-19, order_count: 27, order_amount: 8010.00, message_received: 8, message_processed: 4, message_rejected: 3, message_pending: 1, request_received:  [30-->] 31, request_processed: 24, request_rejected: 5, request_pending: 1  row: 0x10e2362b0  session: 0x10e313610  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:01,657 - logic_logger - INFO
....DailyFlow[2026-11-19] {Formula request_pending} day: 2026-11-19, order_count: 27, order_amount: 8010.00, message_received: 8, message_processed: 4, message_rejected: 3, message_pending: 1, request_received:  [30-->] 31, request_processed: 24, request_rejected: 5, request_pending:  [1-->] 2  row: 0x10e2362b0  session: 0x10e313610  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:01,658 - logic_logger - INFO
Logic Phase:		COMMIT LOGIC		(session=0x10e313610)   										 - 2026-11-19 19:46:01,658 - logic_logger - INFO
Logic Phase:		AFTER_FLUSH LOGIC	(session=0x10e313610)   										 - 2026-11-19 19:46:01,659 - logic_logger - INFO


Logic Phase:		ROW LOGIC		(session=0x10e313610) (sqlalchemy before_flush)			 - 2026-11-19 19:46:01,663 - logic_logger - INFO
..Product[1] {Update - client} id: 1, name: Gadget, count_suppliers: 0, unit_price: 150.0000000000  row: 0x10e5387c0  session: 0x10e313610  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:01,663 - logic_logger - INFO
..OrderB2bRequest[137] {Update - client} id: 137, CreatedOn: 2026-11-19 19:46:01.657140, CreatedOnDay: 2026-11-19, payload: {"Account": "Partner Co 1795146361620", "Notes": "behave test", "Items": [{"Name": "Widget", "QuantityOrdered": 3}, {"Name": "Gadget", "QuantityOrdered": 2}]}, is_processed:  [False-->] True, error_text: None  row: 0x10e3e6650  session: 0x10e313610  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:01,663 - logic_logger - INFO
....DailyFlow[2026-11-19] {Update - Adjusting daily_flow: request_processed} day: 2026-11-19, order_count: 27, order_amount: 8010.00, message_received: 8, message_processed: 4, message_rejected: 3, message_pending: 1, request_received: 31, request_processed:  [24-->] 25, request_rejected: 5, request_pending: 2  row: 0x10e236a40  session: 0x10e313610  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:01,664 - logic_logger - INFO
....DailyFlow[2026-11-19] {Prune Formula: message_pending [['message_received', 'message_processed', 'message_rejected']]} day: 2026-11-19, order_count: 27, order_amount: 8010.00, message_received: 8, message_processed: 4, message_rejected: 3, message_pending: 1, request_received: 31, request_processed:  [24-->] 25, request_rejected: 5, request_pending: 2  row: 0x10e236a40  session: 0x10e313610  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:01,664 - logic_logger - INFO
....DailyFlow[2026-11-19] {Formula request_pending} day: 2026-11-19, order_count: 27, order_amount: 8010.00, message_received: 8, message_processed: 4, message_rejected: 3, message_pending: 1, request_received: 31, request_processed:  [24-->] 25, request_rejected: 5, request_pending:  [2-->] 1  row: 0x10e236a40  session: 0x10e313610  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:01,664 - logic_logger - INFO
..Order[None] {Insert - client} id: None, notes: behave test, customer_id: 40, CreatedOn: None, date_shipped: None, amount_total: None, CreatedOnDay: None  row: 0x10e479e20  session: 0x10e313610  ins_upd_dlt: ins, initial: ins - 2026-11-19 19:46:01,664 - logic_logger - INFO
..Order[None] {early_row_event_all_classes - handle_all did stamping} id: None, notes: behave test, customer_id: 40, CreatedOn: 2026-11-19, date_shipped: None, amount_total: None, CreatedOnDay: 2026-11-19  row: 0x10e479e20  session: 0x10e313610  ins_upd_dlt: ins, initial: ins - 2026-11-19 19:46:01,664 - logic_logger - INFO
..Order[None] {server aggregate_defaults: amount_total } id: None, notes: behave test, customer_id: 40, CreatedOn: 2026-11-19, date_shipped: None, amount_total: 0, CreatedOnDay: 2026-11-19  row: 0x10e479e20  session: 0x10e313610  ins_upd_dlt: ins, initial: ins - 2026-11-19 19:46:01,664 - logic_logger - INFO
....DailyFlow[2026-11-19] {Update - Adjusting daily_flow: order_count} day: 2026-11-19, order_count:  [27-->] 28, order_amount: 8010.00, message_received: 8, message_processed: 4, message_rejected: 3, message_pending: 1, request_received: 31, request_processed: 25, request_rejected: 5, request_pending: 1  row: 0x10e236a40  session: 0x10e313610  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:01,665 - logic_logger - INFO
....DailyFlow[2026-11-19] {Prune Formula: message_pending [['message_received', 'message_processed', 'message_rejected']]} day: 2026-11-19, order_count:  [27-->] 28, order_amount: 8010.00, message_received: 8, message_processed: 4, message_rejected: 3, message_pending: 1, request_received: 31, request_processed: 25, request_rejected: 5, request_pending: 1  row: 0x10e236a40  session: 0x10e313610  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:01,665 - logic_logger - INFO
....DailyFlow[2026-11-19] {Prune Formula: request_pending [['request_received', 'request_processed', 'request_rejected']]} day: 2026-11-19, order_count:  [27-->] 28, order_amount: 8010.00, message_received: 8, message_processed: 4, message_rejected: 3, message_pending: 1, request_received: 31, request_processed: 25, request_rejected: 5, request_pending: 1  row: 0x10e236a40  session: 0x10e313610  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:01,665 - logic_logger - INFO
..Item[None] {Insert - client} id: None, order_id: None, product_id: 2, quantity: 3, amount: None, unit_price: None  row: 0x10e40d350  session: 0x10e313610  ins_upd_dlt: ins, initial: ins - 2026-11-19 19:46:01,665 - logic_logger - INFO
..Item[None] {copy_rules for role: product - unit_price} id: None, order_id: None, product_id: 2, quantity: 3, amount: None, unit_price: 90.0000000000  row: 0x10e40d350  session: 0x10e313610  ins_upd_dlt: ins, initial: ins - 2026-11-19 19:46:01,665 - logic_logger - INFO
..Item[None] {Formula amount} id: None, order_id: None, product_id: 2, quantity: 3, amount: 270.0000000000, unit_price: 90.0000000000  row: 0x10e40d350  session: 0x10e313610  ins_upd_dlt: ins, initial: ins - 2026-11-19 19:46:01,665 - logic_logger - INFO
....Order[None] {Update - Adjusting order: amount_total} id: None, notes: behave test, customer_id: 40, CreatedOn: 2026-11-19, date_shipped: None, amount_total:  [0-->] 270.0000000000, CreatedOnDay: 2026-11-19  row: 0x10e479e20  session: 0x10e313610  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:01,665 - logic_logger - INFO
......DailyFlow[2026-11-19] {Update - Adjusting daily_flow: order_amount} day: 2026-11-19, order_count: 28, order_amount:  [8010.00-->] 8280.0000000000, message_received: 8, message_processed: 4, message_rejected: 3, message_pending: 1, request_received: 31, request_processed: 25, request_rejected: 5, request_pending: 1  row: 0x10e236a40  session: 0x10e313610  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:01,665 - logic_logger - INFO
......DailyFlow[2026-11-19] {Prune Formula: message_pending [['message_received', 'message_processed', 'message_rejected']]} day: 2026-11-19, order_count: 28, order_amount:  [8010.00-->] 8280.0000000000, message_received: 8, message_processed: 4, message_rejected: 3, message_pending: 1, request_received: 31, request_processed: 25, request_rejected: 5, request_pending: 1  row: 0x10e236a40  session: 0x10e313610  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:01,665 - logic_logger - INFO
......DailyFlow[2026-11-19] {Prune Formula: request_pending [['request_received', 'request_processed', 'request_rejected']]} day: 2026-11-19, order_count: 28, order_amount:  [8010.00-->] 8280.0000000000, message_received: 8, message_processed: 4, message_rejected: 3, message_pending: 1, request_received: 31, request_processed: 25, request_rejected: 5, request_pending: 1  row: 0x10e236a40  session: 0x10e313610  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:01,665 - logic_logger - INFO
......Customer[40] {Update - Adjusting customer: balance} id: 40, name: Partner Co 1795146361620, balance:  [0E-10-->] 270.0000000000, credit_limit: 5000.0000000000, email: None, email_opt_out: None  row: 0x10e439550  session: 0x10e313610  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:01,665 - logic_logger - INFO
..Item[None] {Insert - client} id: None, order_id: None, product_id: None, quantity: 2, amount: None, unit_price: None  row: 0x10e3a0a50  session: 0x10e313610  ins_upd_dlt: ins, initial: ins - 2026-11-19 19:46:01,665 - logic_logger - INFO
..Item[None] {copy_rules for role: product - unit_price} id: None, order_id: None, product_id: None, quantity: 2, amount: None, unit_price: 150.0000000000  row: 0x10e3a0a50  session: 0x10e313610  ins_upd_dlt: ins, initial: ins - 2026-11-19 19:46:01,665 - logic_logger - INFO
..Item[None] {Formula amount} id: None, order_id: None, product_id: None, quantity: 2, amount: 300.0000000000, unit_price: 150.0000000000  row: 0x10e3a0a50  session: 0x10e313610  ins_upd_dlt: ins, initial: ins - 2026-11-19 19:46:01,665 - logic_logger - INFO
....Order[None] {Update - Adjusting order: amount_total} id: None, notes: behave test, customer_id: 40, CreatedOn: 2026-11-19, date_shipped: None, amount_total:  [270.0000000000-->] 570.0000000000, CreatedOnDay: 2026-11-19  row: 0x10e479e20  session: 0x10e313610  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:01,666 - logic_logger - INFO
......DailyFlow[2026-11-19] {Update - Adjusting daily_flow: order_amount} day: 2026-11-19, order_count: 28, order_amount:  [8280.0000000000-->] 8580.0000000000, message_received: 8, message_processed: 4, message_rejected: 3, message_pending: 1, request_received: 31, request_processed: 25, request_rejected: 5, request_pending: 1  row: 0x10e236a40  session: 0x10e313610  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:01,666 - logic_logger - INFO
......DailyFlow[2026-11-19] {Prune Formula: message_pending [['message_received', 'message_processed', 'message_rejected']]} day: 2026-11-19, order_count: 28, order_amount:  [8280.0000000000-->] 8580.0000000000, message_received: 8, message_processed: 4, message_rejected: 3, message_pending: 1, request_received: 31, request_processed: 25, request_rejected: 5, request_pending: 1  row: 0x10e236a40  session: 0x10e313610  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:01,666 - logic_logger - INFO
......DailyFlow[2026-11-19] {Prune Formula: request_pending [['request_received', 'request_processed', 'request_rejected']]} day: 2026-11-19, order_count: 28, order_amount:  [8280.0000000000-->] 8580.0000000000, message_received: 8, message_processed: 4, message_rejected: 3, message_pending: 1, request_received: 31, request_processed: 25, request_rejected: 5, request_pending: 1  row: 0x10e236a40  session: 0x10e313610  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:01,666 - logic_logger - INFO
......Customer[40] {Update - Adjusting customer: balance} id: 40, name: Partner Co 1795146361620, balance:  [270.0000000000-->] 570.0000000000, credit_limit: 5000.0000000000, email: None, email_opt_out: None  row: 0x10e439550  session: 0x10e313610  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:01,666 - logic_logger - INFO
Logic Phase:		COMMIT LOGIC		(session=0x10e313610)   										 - 2026-11-19 19:46:01,666 - logic_logger - INFO
Logic Phase:		AFTER_FLUSH LOGIC	(session=0x10e313610)   										 - 2026-11-19 19:46:01,667 - logic_logger - INFO
..Order[216] {AfterFlush Event} id: 216, notes: behave test, customer_id: 40, CreatedOn: 2026-11-19, date_shipped: None, amount_total: 570.0000000000, CreatedOnDay: 2026-11-19  row: 0x10e479e20  session: 0x10e313610  ins_upd_dlt: ins, initial: ins - 2026-11-19 19:46:01,667 - logic_logger - INFO

```
</details>

&nbsp;
&nbsp;

#### Scenario: Partner order with an unknown product is rejected and the request recorded with its error ✅ (0.02 s)
&emsp;  Scenario: Partner order with an unknown product is rejected and the request recorded with its error  
&emsp;&emsp;    Given a new customer "Partner Bad" with credit limit 5000  
&emsp;&emsp;    When a B2B order is placed for "Partner Bad" with 1 Sprocket  
&emsp;&emsp;    Then the order is rejected with "Lookup failed"  
&emsp;&emsp;    And the B2B request is recorded with an error  
&emsp;&emsp;    And "Partner Bad" has no orders  

<details markdown>
<summary>Rules exercised and logic log (2 transactions)</summary>


&nbsp;
&nbsp;


**Rules Used** in Scenario: Partner order with an unknown product is rejected and the request recorded with its error
```
  DailyFlow  
    1. Derive DailyFlow.request_rejected as Count(OrderB2bRequest Where Rule.count(derive=models.DailyFlow.request_rejected, as_count_of=models.OrderB2bRequest, where=lambda row: row.error_text is not None, insert_parent=True), insert_parent)  
    2. Derive DailyFlow.request_pending as Formula (2): Rule.formula(derive=models.DailyFlow.request_pend [...]  
    3. Derive DailyFlow.request_processed as Count(OrderB2bRequest Where Rule.count(derive=models.DailyFlow.request_processed, as_count_of=models.OrderB2bRequest, where=lambda row: row.is_processed == True, insert_parent=True), insert_parent)  
    4. Derive DailyFlow.request_received as Count(OrderB2bRequest Where  - None, insert_parent)  
```
**Logic Log** in Scenario: Partner order with an unknown product is rejected and the request recorded with its error (2 transactions)
```
Logic Phase:		ROW LOGIC		(session=0x10e4cde10) (sqlalchemy before_flush)			 - 2026-11-19 19:46:01,689 - logic_logger - INFO
..OrderB2bRequest[None] {Insert - client} id: None, CreatedOn: None, CreatedOnDay: None, payload: {"Account": "Partner Bad 1795146361684", "Notes": "behave test", "Items": [{"Name": "Sprocket", "QuantityOrdered": 1}]}, is_processed: False, error_text: None  row: 0x10e3edf50  session: 0x10e4cde10  ins_upd_dlt: ins, initial: ins - 2026-11-19 19:46:01,689 - logic_logger - INFO
..OrderB2bRequest[None] {early_row_event_all_classes - handle_all did stamping} id: None, CreatedOn: 2026-11-19 19:46:01.689164, CreatedOnDay: 2026-11-19, payload: {"Account": "Partner Bad 1795146361684", "Notes": "behave test", "Items": [{"Name": "Sprocket", "QuantityOrdered": 1}]}, is_processed: False, error_text: None  row: 0x10e3edf50  session: 0x10e4cde10  ins_upd_dlt: ins, initial: ins - 2026-11-19 19:46:01,689 - logic_logger - INFO
....DailyFlow[2026-11-19] {Update - Adjusting daily_flow: request_received} day: 2026-11-19, order_count: 28, order_amount: 8580.00, message_received: 8, message_processed: 4, message_rejected: 3, message_pending: 1, request_received:  [31-->] 32, request_processed: 25, request_rejected: 5, request_pending: 1  row: 0x10e235d30  session: 0x10e4cde10  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:01,689 - logic_logger - INFO
....DailyFlow[2026-11-19] {Prune Formula: message_pending [['message_received', 'message_processed', 'message_rejected']]} day: 2026-11-19, order_count: 28, order_amount: 8580.00, message_received: 8, message_processed: 4, message_rejected: 3, message_pending: 1, request_received:  [31-->] 32, request_processed: 25, request_rejected: 5, request_pending: 1  row: 0x10e235d30  session: 0x10e4cde10  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:01,689 - logic_logger - INFO
....DailyFlow[2026-11-19] {Formula request_pending} day: 2026-11-19, order_count: 28, order_amount: 8580.00, message_received: 8, message_processed: 4, message_rejected: 3, message_pending: 1, request_received:  [31-->] 32, request_processed: 25, request_rejected: 5, request_pending:  [1-->] 2  row: 0x10e235d30  session: 0x10e4cde10  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:01,689 - logic_logger - INFO
Logic Phase:		COMMIT LOGIC		(session=0x10e4cde10)   										 - 2026-11-19 19:46:01,689 - logic_logger - INFO
Logic Phase:		AFTER_FLUSH LOGIC	(session=0x10e4cde10)   										 - 2026-11-19 19:46:01,690 - logic_logger - INFO


Logic Phase:		ROW LOGIC		(session=0x10e4cde10) (sqlalchemy before_flush)			 - 2026-11-19 19:46:01,692 - logic_logger - INFO
..OrderB2bRequest[138] {Update - client} id: 138, CreatedOn: 2026-11-19 19:46:01.689164, CreatedOnDay: 2026-11-19, payload: {"Account": "Partner Bad 1795146361684", "Notes": "behave test", "Items": [{"Name": "Sprocket", "QuantityOrdered": 1}]}, is_processed: False, error_text:  [None-->] ('Lookup failed: missing parent', <Item (transient 4534092112)>, 'Product', "{'Name': 'Sprocket', 'QuantityOrdered': 1}")  row: 0x10e3edf50  session: 0x10e4cde10  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:01,692 - logic_logger - INFO
....DailyFlow[2026-11-19] {Update - Adjusting daily_flow: request_rejected} day: 2026-11-19, order_count: 28, order_amount: 8580.00, message_received: 8, message_processed: 4, message_rejected: 3, message_pending: 1, request_received: 32, request_processed: 25, request_rejected:  [5-->] 6, request_pending: 2  row: 0x10e235d30  session: 0x10e4cde10  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:01,692 - logic_logger - INFO
....DailyFlow[2026-11-19] {Prune Formula: message_pending [['message_received', 'message_processed', 'message_rejected']]} day: 2026-11-19, order_count: 28, order_amount: 8580.00, message_received: 8, message_processed: 4, message_rejected: 3, message_pending: 1, request_received: 32, request_processed: 25, request_rejected:  [5-->] 6, request_pending: 2  row: 0x10e235d30  session: 0x10e4cde10  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:01,692 - logic_logger - INFO
....DailyFlow[2026-11-19] {Formula request_pending} day: 2026-11-19, order_count: 28, order_amount: 8580.00, message_received: 8, message_processed: 4, message_rejected: 3, message_pending: 1, request_received: 32, request_processed: 25, request_rejected:  [5-->] 6, request_pending:  [2-->] 1  row: 0x10e235d30  session: 0x10e4cde10  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:01,692 - logic_logger - INFO
Logic Phase:		COMMIT LOGIC		(session=0x10e4cde10)   										 - 2026-11-19 19:46:01,692 - logic_logger - INFO
Logic Phase:		AFTER_FLUSH LOGIC	(session=0x10e4cde10)   										 - 2026-11-19 19:46:01,693 - logic_logger - INFO

```
</details>

&nbsp;
&nbsp;

#### Scenario: Partner order for an unknown account is rejected ✅ (0.01 s)
&emsp;  Scenario: Partner order for an unknown account is rejected  
&emsp;&emsp;    When a B2B order is placed for an unknown account  
&emsp;&emsp;    Then the order is rejected with "Lookup failed"  

<details markdown>
<summary>Rules exercised and logic log (2 transactions)</summary>


&nbsp;
&nbsp;


**Rules Used** in Scenario: Partner order for an unknown account is rejected
```
  DailyFlow  
    1. Derive DailyFlow.request_rejected as Count(OrderB2bRequest Where Rule.count(derive=models.DailyFlow.request_rejected, as_count_of=models.OrderB2bRequest, where=lambda row: row.error_text is not None, insert_parent=True), insert_parent)  
    2. Derive DailyFlow.request_pending as Formula (2): Rule.formula(derive=models.DailyFlow.request_pend [...]  
    3. Derive DailyFlow.request_processed as Count(OrderB2bRequest Where Rule.count(derive=models.DailyFlow.request_processed, as_count_of=models.OrderB2bRequest, where=lambda row: row.is_processed == True, insert_parent=True), insert_parent)  
    4. Derive DailyFlow.request_received as Count(OrderB2bRequest Where  - None, insert_parent)  
```
**Logic Log** in Scenario: Partner order for an unknown account is rejected (2 transactions)
```
Logic Phase:		ROW LOGIC		(session=0x10e433f00) (sqlalchemy before_flush)			 - 2026-11-19 19:46:01,708 - logic_logger - INFO
..OrderB2bRequest[None] {Insert - client} id: None, CreatedOn: None, CreatedOnDay: None, payload: {"Account": "Nobody 1795146361706", "Notes": "behave test", "Items": [{"Name": "Widget", "QuantityOrdered": 1}]}, is_processed: False, error_text: None  row: 0x10e40fb50  session: 0x10e433f00  ins_upd_dlt: ins, initial: ins - 2026-11-19 19:46:01,708 - logic_logger - INFO
..OrderB2bRequest[None] {early_row_event_all_classes - handle_all did stamping} id: None, CreatedOn: 2026-11-19 19:46:01.708519, CreatedOnDay: 2026-11-19, payload: {"Account": "Nobody 1795146361706", "Notes": "behave test", "Items": [{"Name": "Widget", "QuantityOrdered": 1}]}, is_processed: False, error_text: None  row: 0x10e40fb50  session: 0x10e433f00  ins_upd_dlt: ins, initial: ins - 2026-11-19 19:46:01,708 - logic_logger - INFO
....DailyFlow[2026-11-19] {Update - Adjusting daily_flow: request_received} day: 2026-11-19, order_count: 28, order_amount: 8580.00, message_received: 8, message_processed: 4, message_rejected: 3, message_pending: 1, request_received:  [32-->] 33, request_processed: 25, request_rejected: 6, request_pending: 1  row: 0x10e235d30  session: 0x10e433f00  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:01,708 - logic_logger - INFO
....DailyFlow[2026-11-19] {Prune Formula: message_pending [['message_received', 'message_processed', 'message_rejected']]} day: 2026-11-19, order_count: 28, order_amount: 8580.00, message_received: 8, message_processed: 4, message_rejected: 3, message_pending: 1, request_received:  [32-->] 33, request_processed: 25, request_rejected: 6, request_pending: 1  row: 0x10e235d30  session: 0x10e433f00  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:01,708 - logic_logger - INFO
....DailyFlow[2026-11-19] {Formula request_pending} day: 2026-11-19, order_count: 28, order_amount: 8580.00, message_received: 8, message_processed: 4, message_rejected: 3, message_pending: 1, request_received:  [32-->] 33, request_processed: 25, request_rejected: 6, request_pending:  [1-->] 2  row: 0x10e235d30  session: 0x10e433f00  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:01,709 - logic_logger - INFO
Logic Phase:		COMMIT LOGIC		(session=0x10e433f00)   										 - 2026-11-19 19:46:01,709 - logic_logger - INFO
Logic Phase:		AFTER_FLUSH LOGIC	(session=0x10e433f00)   										 - 2026-11-19 19:46:01,709 - logic_logger - INFO


Logic Phase:		ROW LOGIC		(session=0x10e433f00) (sqlalchemy before_flush)			 - 2026-11-19 19:46:01,710 - logic_logger - INFO
..OrderB2bRequest[139] {Update - client} id: 139, CreatedOn: 2026-11-19 19:46:01.708519, CreatedOnDay: 2026-11-19, payload: {"Account": "Nobody 1795146361706", "Notes": "behave test", "Items": [{"Name": "Widget", "QuantityOrdered": 1}]}, is_processed: False, error_text:  [None-->] ('Lookup failed: missing parent', <Order (transient 4537674800)>, 'Customer', "{'Account': 'Nobody 1795146361706', 'Notes': 'behave test', 'Items': [{'Name': 'Widget', 'QuantityOrdered': 1}]}")  row: 0x10e40fb50  session: 0x10e433f00  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:01,711 - logic_logger - INFO
....DailyFlow[2026-11-19] {Update - Adjusting daily_flow: request_rejected} day: 2026-11-19, order_count: 28, order_amount: 8580.00, message_received: 8, message_processed: 4, message_rejected: 3, message_pending: 1, request_received: 33, request_processed: 25, request_rejected:  [6-->] 7, request_pending: 2  row: 0x10e235d30  session: 0x10e433f00  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:01,711 - logic_logger - INFO
....DailyFlow[2026-11-19] {Prune Formula: message_pending [['message_received', 'message_processed', 'message_rejected']]} day: 2026-11-19, order_count: 28, order_amount: 8580.00, message_received: 8, message_processed: 4, message_rejected: 3, message_pending: 1, request_received: 33, request_processed: 25, request_rejected:  [6-->] 7, request_pending: 2  row: 0x10e235d30  session: 0x10e433f00  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:01,711 - logic_logger - INFO
....DailyFlow[2026-11-19] {Formula request_pending} day: 2026-11-19, order_count: 28, order_amount: 8580.00, message_received: 8, message_processed: 4, message_rejected: 3, message_pending: 1, request_received: 33, request_processed: 25, request_rejected:  [6-->] 7, request_pending:  [2-->] 1  row: 0x10e235d30  session: 0x10e433f00  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:01,711 - logic_logger - INFO
Logic Phase:		COMMIT LOGIC		(session=0x10e433f00)   										 - 2026-11-19 19:46:01,711 - logic_logger - INFO
Logic Phase:		AFTER_FLUSH LOGIC	(session=0x10e433f00)   										 - 2026-11-19 19:46:01,711 - logic_logger - INFO

```
</details>

&nbsp;
&nbsp;

### Feature: Check Credit  

&nbsp;
&nbsp;

#### Scenario: Good order is priced and added to the balance ✅ (0.02 s)
&emsp;  Scenario: Good order is priced and added to the balance  
&emsp;&emsp;    Given a new customer "Pat" with credit limit 1000  
&emsp;&emsp;    When a B2B order is placed for "Pat" with 2 Widget and 1 Gadget  
&emsp;&emsp;    Then the order is accepted  
&emsp;&emsp;    And the item prices are copied from the products  
&emsp;&emsp;    And each item amount is quantity times unit price  
&emsp;&emsp;    And the order total is 330  
&emsp;&emsp;    And the balance of "Pat" is 330  

<details markdown>
<summary>Rules exercised and logic log (2 transactions)</summary>


&nbsp;
&nbsp;


**Rules Used** in Scenario: Good order is priced and added to the balance
```
  DailyFlow  
    1. Derive DailyFlow.request_rejected as Count(OrderB2bRequest Where Rule.count(derive=models.DailyFlow.request_rejected, as_count_of=models.OrderB2bRequest, where=lambda row: row.error_text is not None, insert_parent=True), insert_parent)  
    2. Derive DailyFlow.request_pending as Formula (2): Rule.formula(derive=models.DailyFlow.request_pend [...]  
    3. Derive DailyFlow.request_processed as Count(OrderB2bRequest Where Rule.count(derive=models.DailyFlow.request_processed, as_count_of=models.OrderB2bRequest, where=lambda row: row.is_processed == True, insert_parent=True), insert_parent)  
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
**Logic Log** in Scenario: Good order is priced and added to the balance (2 transactions)
```
Logic Phase:		ROW LOGIC		(session=0x10e4ce030) (sqlalchemy before_flush)			 - 2026-11-19 19:46:01,721 - logic_logger - INFO
..OrderB2bRequest[None] {Insert - client} id: None, CreatedOn: None, CreatedOnDay: None, payload: {"Account": "Pat 1795146361717", "Notes": "behave test", "Items": [{"Name": "Widget", "QuantityOrdered": 2}, {"Name": "Gadget", "QuantityOrdered": 1}]}, is_processed: False, error_text: None  row: 0x10e782fd0  session: 0x10e4ce030  ins_upd_dlt: ins, initial: ins - 2026-11-19 19:46:01,721 - logic_logger - INFO
..OrderB2bRequest[None] {early_row_event_all_classes - handle_all did stamping} id: None, CreatedOn: 2026-11-19 19:46:01.721592, CreatedOnDay: 2026-11-19, payload: {"Account": "Pat 1795146361717", "Notes": "behave test", "Items": [{"Name": "Widget", "QuantityOrdered": 2}, {"Name": "Gadget", "QuantityOrdered": 1}]}, is_processed: False, error_text: None  row: 0x10e782fd0  session: 0x10e4ce030  ins_upd_dlt: ins, initial: ins - 2026-11-19 19:46:01,721 - logic_logger - INFO
....DailyFlow[2026-11-19] {Update - Adjusting daily_flow: request_received} day: 2026-11-19, order_count: 28, order_amount: 8580.00, message_received: 8, message_processed: 4, message_rejected: 3, message_pending: 1, request_received:  [33-->] 34, request_processed: 25, request_rejected: 7, request_pending: 1  row: 0x10e7c4050  session: 0x10e4ce030  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:01,721 - logic_logger - INFO
....DailyFlow[2026-11-19] {Prune Formula: message_pending [['message_received', 'message_processed', 'message_rejected']]} day: 2026-11-19, order_count: 28, order_amount: 8580.00, message_received: 8, message_processed: 4, message_rejected: 3, message_pending: 1, request_received:  [33-->] 34, request_processed: 25, request_rejected: 7, request_pending: 1  row: 0x10e7c4050  session: 0x10e4ce030  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:01,721 - logic_logger - INFO
....DailyFlow[2026-11-19] {Formula request_pending} day: 2026-11-19, order_count: 28, order_amount: 8580.00, message_received: 8, message_processed: 4, message_rejected: 3, message_pending: 1, request_received:  [33-->] 34, request_processed: 25, request_rejected: 7, request_pending:  [1-->] 2  row: 0x10e7c4050  session: 0x10e4ce030  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:01,722 - logic_logger - INFO
Logic Phase:		COMMIT LOGIC		(session=0x10e4ce030)   										 - 2026-11-19 19:46:01,722 - logic_logger - INFO
Logic Phase:		AFTER_FLUSH LOGIC	(session=0x10e4ce030)   										 - 2026-11-19 19:46:01,722 - logic_logger - INFO


Logic Phase:		ROW LOGIC		(session=0x10e4ce030) (sqlalchemy before_flush)			 - 2026-11-19 19:46:01,725 - logic_logger - INFO
..OrderB2bRequest[140] {Update - client} id: 140, CreatedOn: 2026-11-19 19:46:01.721592, CreatedOnDay: 2026-11-19, payload: {"Account": "Pat 1795146361717", "Notes": "behave test", "Items": [{"Name": "Widget", "QuantityOrdered": 2}, {"Name": "Gadget", "QuantityOrdered": 1}]}, is_processed:  [False-->] True, error_text: None  row: 0x10e782fd0  session: 0x10e4ce030  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:01,725 - logic_logger - INFO
....DailyFlow[2026-11-19] {Update - Adjusting daily_flow: request_processed} day: 2026-11-19, order_count: 28, order_amount: 8580.00, message_received: 8, message_processed: 4, message_rejected: 3, message_pending: 1, request_received: 34, request_processed:  [25-->] 26, request_rejected: 7, request_pending: 2  row: 0x10e237e30  session: 0x10e4ce030  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:01,725 - logic_logger - INFO
....DailyFlow[2026-11-19] {Prune Formula: message_pending [['message_received', 'message_processed', 'message_rejected']]} day: 2026-11-19, order_count: 28, order_amount: 8580.00, message_received: 8, message_processed: 4, message_rejected: 3, message_pending: 1, request_received: 34, request_processed:  [25-->] 26, request_rejected: 7, request_pending: 2  row: 0x10e237e30  session: 0x10e4ce030  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:01,725 - logic_logger - INFO
....DailyFlow[2026-11-19] {Formula request_pending} day: 2026-11-19, order_count: 28, order_amount: 8580.00, message_received: 8, message_processed: 4, message_rejected: 3, message_pending: 1, request_received: 34, request_processed:  [25-->] 26, request_rejected: 7, request_pending:  [2-->] 1  row: 0x10e237e30  session: 0x10e4ce030  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:01,725 - logic_logger - INFO
..Product[1] {Update - client} id: 1, name: Gadget, count_suppliers: 0, unit_price: 150.0000000000  row: 0x10e4c06e0  session: 0x10e4ce030  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:01,725 - logic_logger - INFO
..Order[None] {Insert - client} id: None, notes: behave test, customer_id: 42, CreatedOn: None, date_shipped: None, amount_total: None, CreatedOnDay: None  row: 0x10e776cc0  session: 0x10e4ce030  ins_upd_dlt: ins, initial: ins - 2026-11-19 19:46:01,725 - logic_logger - INFO
..Order[None] {early_row_event_all_classes - handle_all did stamping} id: None, notes: behave test, customer_id: 42, CreatedOn: 2026-11-19, date_shipped: None, amount_total: None, CreatedOnDay: 2026-11-19  row: 0x10e776cc0  session: 0x10e4ce030  ins_upd_dlt: ins, initial: ins - 2026-11-19 19:46:01,725 - logic_logger - INFO
..Order[None] {server aggregate_defaults: amount_total } id: None, notes: behave test, customer_id: 42, CreatedOn: 2026-11-19, date_shipped: None, amount_total: 0, CreatedOnDay: 2026-11-19  row: 0x10e776cc0  session: 0x10e4ce030  ins_upd_dlt: ins, initial: ins - 2026-11-19 19:46:01,725 - logic_logger - INFO
....DailyFlow[2026-11-19] {Update - Adjusting daily_flow: order_count} day: 2026-11-19, order_count:  [28-->] 29, order_amount: 8580.00, message_received: 8, message_processed: 4, message_rejected: 3, message_pending: 1, request_received: 34, request_processed: 26, request_rejected: 7, request_pending: 1  row: 0x10e237e30  session: 0x10e4ce030  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:01,726 - logic_logger - INFO
....DailyFlow[2026-11-19] {Prune Formula: message_pending [['message_received', 'message_processed', 'message_rejected']]} day: 2026-11-19, order_count:  [28-->] 29, order_amount: 8580.00, message_received: 8, message_processed: 4, message_rejected: 3, message_pending: 1, request_received: 34, request_processed: 26, request_rejected: 7, request_pending: 1  row: 0x10e237e30  session: 0x10e4ce030  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:01,726 - logic_logger - INFO
....DailyFlow[2026-11-19] {Prune Formula: request_pending [['request_received', 'request_processed', 'request_rejected']]} day: 2026-11-19, order_count:  [28-->] 29, order_amount: 8580.00, message_received: 8, message_processed: 4, message_rejected: 3, message_pending: 1, request_received: 34, request_processed: 26, request_rejected: 7, request_pending: 1  row: 0x10e237e30  session: 0x10e4ce030  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:01,726 - logic_logger - INFO
..Item[None] {Insert - client} id: None, order_id: None, product_id: 2, quantity: 2, amount: None, unit_price: None  row: 0x10e53d6d0  session: 0x10e4ce030  ins_upd_dlt: ins, initial: ins - 2026-11-19 19:46:01,726 - logic_logger - INFO
..Item[None] {copy_rules for role: product - unit_price} id: None, order_id: None, product_id: 2, quantity: 2, amount: None, unit_price: 90.0000000000  row: 0x10e53d6d0  session: 0x10e4ce030  ins_upd_dlt: ins, initial: ins - 2026-11-19 19:46:01,726 - logic_logger - INFO
..Item[None] {Formula amount} id: None, order_id: None, product_id: 2, quantity: 2, amount: 180.0000000000, unit_price: 90.0000000000  row: 0x10e53d6d0  session: 0x10e4ce030  ins_upd_dlt: ins, initial: ins - 2026-11-19 19:46:01,726 - logic_logger - INFO
....Order[None] {Update - Adjusting order: amount_total} id: None, notes: behave test, customer_id: 42, CreatedOn: 2026-11-19, date_shipped: None, amount_total:  [0-->] 180.0000000000, CreatedOnDay: 2026-11-19  row: 0x10e776cc0  session: 0x10e4ce030  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:01,726 - logic_logger - INFO
......DailyFlow[2026-11-19] {Update - Adjusting daily_flow: order_amount} day: 2026-11-19, order_count: 29, order_amount:  [8580.00-->] 8760.0000000000, message_received: 8, message_processed: 4, message_rejected: 3, message_pending: 1, request_received: 34, request_processed: 26, request_rejected: 7, request_pending: 1  row: 0x10e237e30  session: 0x10e4ce030  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:01,726 - logic_logger - INFO
......DailyFlow[2026-11-19] {Prune Formula: message_pending [['message_received', 'message_processed', 'message_rejected']]} day: 2026-11-19, order_count: 29, order_amount:  [8580.00-->] 8760.0000000000, message_received: 8, message_processed: 4, message_rejected: 3, message_pending: 1, request_received: 34, request_processed: 26, request_rejected: 7, request_pending: 1  row: 0x10e237e30  session: 0x10e4ce030  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:01,726 - logic_logger - INFO
......DailyFlow[2026-11-19] {Prune Formula: request_pending [['request_received', 'request_processed', 'request_rejected']]} day: 2026-11-19, order_count: 29, order_amount:  [8580.00-->] 8760.0000000000, message_received: 8, message_processed: 4, message_rejected: 3, message_pending: 1, request_received: 34, request_processed: 26, request_rejected: 7, request_pending: 1  row: 0x10e237e30  session: 0x10e4ce030  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:01,726 - logic_logger - INFO
......Customer[42] {Update - Adjusting customer: balance} id: 42, name: Pat 1795146361717, balance:  [0E-10-->] 180.0000000000, credit_limit: 1000.0000000000, email: None, email_opt_out: None  row: 0x10e574cd0  session: 0x10e4ce030  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:01,726 - logic_logger - INFO
..Item[None] {Insert - client} id: None, order_id: None, product_id: None, quantity: 1, amount: None, unit_price: None  row: 0x10e454950  session: 0x10e4ce030  ins_upd_dlt: ins, initial: ins - 2026-11-19 19:46:01,726 - logic_logger - INFO
..Item[None] {copy_rules for role: product - unit_price} id: None, order_id: None, product_id: None, quantity: 1, amount: None, unit_price: 150.0000000000  row: 0x10e454950  session: 0x10e4ce030  ins_upd_dlt: ins, initial: ins - 2026-11-19 19:46:01,726 - logic_logger - INFO
..Item[None] {Formula amount} id: None, order_id: None, product_id: None, quantity: 1, amount: 150.0000000000, unit_price: 150.0000000000  row: 0x10e454950  session: 0x10e4ce030  ins_upd_dlt: ins, initial: ins - 2026-11-19 19:46:01,726 - logic_logger - INFO
....Order[None] {Update - Adjusting order: amount_total} id: None, notes: behave test, customer_id: 42, CreatedOn: 2026-11-19, date_shipped: None, amount_total:  [180.0000000000-->] 330.0000000000, CreatedOnDay: 2026-11-19  row: 0x10e776cc0  session: 0x10e4ce030  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:01,726 - logic_logger - INFO
......DailyFlow[2026-11-19] {Update - Adjusting daily_flow: order_amount} day: 2026-11-19, order_count: 29, order_amount:  [8760.0000000000-->] 8910.0000000000, message_received: 8, message_processed: 4, message_rejected: 3, message_pending: 1, request_received: 34, request_processed: 26, request_rejected: 7, request_pending: 1  row: 0x10e237e30  session: 0x10e4ce030  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:01,726 - logic_logger - INFO
......DailyFlow[2026-11-19] {Prune Formula: message_pending [['message_received', 'message_processed', 'message_rejected']]} day: 2026-11-19, order_count: 29, order_amount:  [8760.0000000000-->] 8910.0000000000, message_received: 8, message_processed: 4, message_rejected: 3, message_pending: 1, request_received: 34, request_processed: 26, request_rejected: 7, request_pending: 1  row: 0x10e237e30  session: 0x10e4ce030  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:01,727 - logic_logger - INFO
......DailyFlow[2026-11-19] {Prune Formula: request_pending [['request_received', 'request_processed', 'request_rejected']]} day: 2026-11-19, order_count: 29, order_amount:  [8760.0000000000-->] 8910.0000000000, message_received: 8, message_processed: 4, message_rejected: 3, message_pending: 1, request_received: 34, request_processed: 26, request_rejected: 7, request_pending: 1  row: 0x10e237e30  session: 0x10e4ce030  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:01,727 - logic_logger - INFO
......Customer[42] {Update - Adjusting customer: balance} id: 42, name: Pat 1795146361717, balance:  [180.0000000000-->] 330.0000000000, credit_limit: 1000.0000000000, email: None, email_opt_out: None  row: 0x10e574cd0  session: 0x10e4ce030  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:01,727 - logic_logger - INFO
Logic Phase:		COMMIT LOGIC		(session=0x10e4ce030)   										 - 2026-11-19 19:46:01,727 - logic_logger - INFO
Logic Phase:		AFTER_FLUSH LOGIC	(session=0x10e4ce030)   										 - 2026-11-19 19:46:01,727 - logic_logger - INFO
..Order[217] {AfterFlush Event} id: 217, notes: behave test, customer_id: 42, CreatedOn: 2026-11-19, date_shipped: None, amount_total: 330.0000000000, CreatedOnDay: 2026-11-19  row: 0x10e776cc0  session: 0x10e4ce030  ins_upd_dlt: ins, initial: ins - 2026-11-19 19:46:01,728 - logic_logger - INFO

```
</details>

&nbsp;
&nbsp;

#### Scenario: Changing an item quantity re-derives amount, total and balance ✅ (0.03 s)
&emsp;  Scenario: Changing an item quantity re-derives amount, total and balance  
&emsp;&emsp;    Given a new customer "Quinn" with credit limit 2000  
&emsp;&emsp;    And a B2B order is placed for "Quinn" with 2 Widget and 1 Gadget  
&emsp;&emsp;    When the quantity of the first item is changed to 5  
&emsp;&emsp;    Then the first item amount is 450  
&emsp;&emsp;    And the order total is 600  
&emsp;&emsp;    And the balance of "Quinn" is 600  

<details markdown>
<summary>Rules exercised and logic log (3 transactions)</summary>


&nbsp;
&nbsp;


**Rules Used** in Scenario: Changing an item quantity re-derives amount, total and balance
```
  DailyFlow  
    1. Derive DailyFlow.request_rejected as Count(OrderB2bRequest Where Rule.count(derive=models.DailyFlow.request_rejected, as_count_of=models.OrderB2bRequest, where=lambda row: row.error_text is not None, insert_parent=True), insert_parent)  
    2. Derive DailyFlow.request_pending as Formula (2): Rule.formula(derive=models.DailyFlow.request_pend [...]  
    3. Derive DailyFlow.request_processed as Count(OrderB2bRequest Where Rule.count(derive=models.DailyFlow.request_processed, as_count_of=models.OrderB2bRequest, where=lambda row: row.is_processed == True, insert_parent=True), insert_parent)  
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
**Logic Log** in Scenario: Changing an item quantity re-derives amount, total and balance (3 transactions)
```
Logic Phase:		ROW LOGIC		(session=0x10e4cd480) (sqlalchemy before_flush)			 - 2026-11-19 19:46:01,746 - logic_logger - INFO
..OrderB2bRequest[None] {Insert - client} id: None, CreatedOn: None, CreatedOnDay: None, payload: {"Account": "Quinn 1795146361742", "Notes": "behave test", "Items": [{"Name": "Widget", "QuantityOrdered": 2}, {"Name": "Gadget", "QuantityOrdered": 1}]}, is_processed: False, error_text: None  row: 0x10e43bb50  session: 0x10e4cd480  ins_upd_dlt: ins, initial: ins - 2026-11-19 19:46:01,746 - logic_logger - INFO
..OrderB2bRequest[None] {early_row_event_all_classes - handle_all did stamping} id: None, CreatedOn: 2026-11-19 19:46:01.746133, CreatedOnDay: 2026-11-19, payload: {"Account": "Quinn 1795146361742", "Notes": "behave test", "Items": [{"Name": "Widget", "QuantityOrdered": 2}, {"Name": "Gadget", "QuantityOrdered": 1}]}, is_processed: False, error_text: None  row: 0x10e43bb50  session: 0x10e4cd480  ins_upd_dlt: ins, initial: ins - 2026-11-19 19:46:01,746 - logic_logger - INFO
....DailyFlow[2026-11-19] {Update - Adjusting daily_flow: request_received} day: 2026-11-19, order_count: 29, order_amount: 8910.00, message_received: 8, message_processed: 4, message_rejected: 3, message_pending: 1, request_received:  [34-->] 35, request_processed: 26, request_rejected: 7, request_pending: 1  row: 0x10e237cd0  session: 0x10e4cd480  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:01,746 - logic_logger - INFO
....DailyFlow[2026-11-19] {Prune Formula: message_pending [['message_received', 'message_processed', 'message_rejected']]} day: 2026-11-19, order_count: 29, order_amount: 8910.00, message_received: 8, message_processed: 4, message_rejected: 3, message_pending: 1, request_received:  [34-->] 35, request_processed: 26, request_rejected: 7, request_pending: 1  row: 0x10e237cd0  session: 0x10e4cd480  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:01,746 - logic_logger - INFO
....DailyFlow[2026-11-19] {Formula request_pending} day: 2026-11-19, order_count: 29, order_amount: 8910.00, message_received: 8, message_processed: 4, message_rejected: 3, message_pending: 1, request_received:  [34-->] 35, request_processed: 26, request_rejected: 7, request_pending:  [1-->] 2  row: 0x10e237cd0  session: 0x10e4cd480  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:01,746 - logic_logger - INFO
Logic Phase:		COMMIT LOGIC		(session=0x10e4cd480)   										 - 2026-11-19 19:46:01,746 - logic_logger - INFO
Logic Phase:		AFTER_FLUSH LOGIC	(session=0x10e4cd480)   										 - 2026-11-19 19:46:01,746 - logic_logger - INFO


Logic Phase:		ROW LOGIC		(session=0x10e4cd480) (sqlalchemy before_flush)			 - 2026-11-19 19:46:01,749 - logic_logger - INFO
..OrderB2bRequest[141] {Update - client} id: 141, CreatedOn: 2026-11-19 19:46:01.746133, CreatedOnDay: 2026-11-19, payload: {"Account": "Quinn 1795146361742", "Notes": "behave test", "Items": [{"Name": "Widget", "QuantityOrdered": 2}, {"Name": "Gadget", "QuantityOrdered": 1}]}, is_processed:  [False-->] True, error_text: None  row: 0x10e43bb50  session: 0x10e4cd480  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:01,749 - logic_logger - INFO
....DailyFlow[2026-11-19] {Update - Adjusting daily_flow: request_processed} day: 2026-11-19, order_count: 29, order_amount: 8910.00, message_received: 8, message_processed: 4, message_rejected: 3, message_pending: 1, request_received: 35, request_processed:  [26-->] 27, request_rejected: 7, request_pending: 2  row: 0x10e237cd0  session: 0x10e4cd480  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:01,749 - logic_logger - INFO
....DailyFlow[2026-11-19] {Prune Formula: message_pending [['message_received', 'message_processed', 'message_rejected']]} day: 2026-11-19, order_count: 29, order_amount: 8910.00, message_received: 8, message_processed: 4, message_rejected: 3, message_pending: 1, request_received: 35, request_processed:  [26-->] 27, request_rejected: 7, request_pending: 2  row: 0x10e237cd0  session: 0x10e4cd480  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:01,749 - logic_logger - INFO
....DailyFlow[2026-11-19] {Formula request_pending} day: 2026-11-19, order_count: 29, order_amount: 8910.00, message_received: 8, message_processed: 4, message_rejected: 3, message_pending: 1, request_received: 35, request_processed:  [26-->] 27, request_rejected: 7, request_pending:  [2-->] 1  row: 0x10e237cd0  session: 0x10e4cd480  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:01,749 - logic_logger - INFO
..Product[1] {Update - client} id: 1, name: Gadget, count_suppliers: 0, unit_price: 150.0000000000  row: 0x10e7f41a0  session: 0x10e4cd480  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:01,750 - logic_logger - INFO
..Order[None] {Insert - client} id: None, notes: behave test, customer_id: 43, CreatedOn: None, date_shipped: None, amount_total: None, CreatedOnDay: None  row: 0x10e7770b0  session: 0x10e4cd480  ins_upd_dlt: ins, initial: ins - 2026-11-19 19:46:01,750 - logic_logger - INFO
..Order[None] {early_row_event_all_classes - handle_all did stamping} id: None, notes: behave test, customer_id: 43, CreatedOn: 2026-11-19, date_shipped: None, amount_total: None, CreatedOnDay: 2026-11-19  row: 0x10e7770b0  session: 0x10e4cd480  ins_upd_dlt: ins, initial: ins - 2026-11-19 19:46:01,750 - logic_logger - INFO
..Order[None] {server aggregate_defaults: amount_total } id: None, notes: behave test, customer_id: 43, CreatedOn: 2026-11-19, date_shipped: None, amount_total: 0, CreatedOnDay: 2026-11-19  row: 0x10e7770b0  session: 0x10e4cd480  ins_upd_dlt: ins, initial: ins - 2026-11-19 19:46:01,750 - logic_logger - INFO
....DailyFlow[2026-11-19] {Update - Adjusting daily_flow: order_count} day: 2026-11-19, order_count:  [29-->] 30, order_amount: 8910.00, message_received: 8, message_processed: 4, message_rejected: 3, message_pending: 1, request_received: 35, request_processed: 27, request_rejected: 7, request_pending: 1  row: 0x10e237cd0  session: 0x10e4cd480  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:01,750 - logic_logger - INFO
....DailyFlow[2026-11-19] {Prune Formula: message_pending [['message_received', 'message_processed', 'message_rejected']]} day: 2026-11-19, order_count:  [29-->] 30, order_amount: 8910.00, message_received: 8, message_processed: 4, message_rejected: 3, message_pending: 1, request_received: 35, request_processed: 27, request_rejected: 7, request_pending: 1  row: 0x10e237cd0  session: 0x10e4cd480  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:01,750 - logic_logger - INFO
....DailyFlow[2026-11-19] {Prune Formula: request_pending [['request_received', 'request_processed', 'request_rejected']]} day: 2026-11-19, order_count:  [29-->] 30, order_amount: 8910.00, message_received: 8, message_processed: 4, message_rejected: 3, message_pending: 1, request_received: 35, request_processed: 27, request_rejected: 7, request_pending: 1  row: 0x10e237cd0  session: 0x10e4cd480  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:01,750 - logic_logger - INFO
..Item[None] {Insert - client} id: None, order_id: None, product_id: 2, quantity: 2, amount: None, unit_price: None  row: 0x10dfdaed0  session: 0x10e4cd480  ins_upd_dlt: ins, initial: ins - 2026-11-19 19:46:01,750 - logic_logger - INFO
..Item[None] {copy_rules for role: product - unit_price} id: None, order_id: None, product_id: 2, quantity: 2, amount: None, unit_price: 90.0000000000  row: 0x10dfdaed0  session: 0x10e4cd480  ins_upd_dlt: ins, initial: ins - 2026-11-19 19:46:01,750 - logic_logger - INFO
..Item[None] {Formula amount} id: None, order_id: None, product_id: 2, quantity: 2, amount: 180.0000000000, unit_price: 90.0000000000  row: 0x10dfdaed0  session: 0x10e4cd480  ins_upd_dlt: ins, initial: ins - 2026-11-19 19:46:01,750 - logic_logger - INFO
....Order[None] {Update - Adjusting order: amount_total} id: None, notes: behave test, customer_id: 43, CreatedOn: 2026-11-19, date_shipped: None, amount_total:  [0-->] 180.0000000000, CreatedOnDay: 2026-11-19  row: 0x10e7770b0  session: 0x10e4cd480  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:01,750 - logic_logger - INFO
......DailyFlow[2026-11-19] {Update - Adjusting daily_flow: order_amount} day: 2026-11-19, order_count: 30, order_amount:  [8910.00-->] 9090.0000000000, message_received: 8, message_processed: 4, message_rejected: 3, message_pending: 1, request_received: 35, request_processed: 27, request_rejected: 7, request_pending: 1  row: 0x10e237cd0  session: 0x10e4cd480  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:01,750 - logic_logger - INFO
......DailyFlow[2026-11-19] {Prune Formula: message_pending [['message_received', 'message_processed', 'message_rejected']]} day: 2026-11-19, order_count: 30, order_amount:  [8910.00-->] 9090.0000000000, message_received: 8, message_processed: 4, message_rejected: 3, message_pending: 1, request_received: 35, request_processed: 27, request_rejected: 7, request_pending: 1  row: 0x10e237cd0  session: 0x10e4cd480  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:01,750 - logic_logger - INFO
......DailyFlow[2026-11-19] {Prune Formula: request_pending [['request_received', 'request_processed', 'request_rejected']]} day: 2026-11-19, order_count: 30, order_amount:  [8910.00-->] 9090.0000000000, message_received: 8, message_processed: 4, message_rejected: 3, message_pending: 1, request_received: 35, request_processed: 27, request_rejected: 7, request_pending: 1  row: 0x10e237cd0  session: 0x10e4cd480  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:01,750 - logic_logger - INFO
......Customer[43] {Update - Adjusting customer: balance} id: 43, name: Quinn 1795146361742, balance:  [0E-10-->] 180.0000000000, credit_limit: 2000.0000000000, email: None, email_opt_out: None  row: 0x10e783550  session: 0x10e4cd480  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:01,750 - logic_logger - INFO
..Item[None] {Insert - client} id: None, order_id: None, product_id: None, quantity: 1, amount: None, unit_price: None  row: 0x10e53e0d0  session: 0x10e4cd480  ins_upd_dlt: ins, initial: ins - 2026-11-19 19:46:01,751 - logic_logger - INFO
..Item[None] {copy_rules for role: product - unit_price} id: None, order_id: None, product_id: None, quantity: 1, amount: None, unit_price: 150.0000000000  row: 0x10e53e0d0  session: 0x10e4cd480  ins_upd_dlt: ins, initial: ins - 2026-11-19 19:46:01,751 - logic_logger - INFO
..Item[None] {Formula amount} id: None, order_id: None, product_id: None, quantity: 1, amount: 150.0000000000, unit_price: 150.0000000000  row: 0x10e53e0d0  session: 0x10e4cd480  ins_upd_dlt: ins, initial: ins - 2026-11-19 19:46:01,751 - logic_logger - INFO
....Order[None] {Update - Adjusting order: amount_total} id: None, notes: behave test, customer_id: 43, CreatedOn: 2026-11-19, date_shipped: None, amount_total:  [180.0000000000-->] 330.0000000000, CreatedOnDay: 2026-11-19  row: 0x10e7770b0  session: 0x10e4cd480  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:01,751 - logic_logger - INFO
......DailyFlow[2026-11-19] {Update - Adjusting daily_flow: order_amount} day: 2026-11-19, order_count: 30, order_amount:  [9090.0000000000-->] 9240.0000000000, message_received: 8, message_processed: 4, message_rejected: 3, message_pending: 1, request_received: 35, request_processed: 27, request_rejected: 7, request_pending: 1  row: 0x10e237cd0  session: 0x10e4cd480  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:01,751 - logic_logger - INFO
......DailyFlow[2026-11-19] {Prune Formula: message_pending [['message_received', 'message_processed', 'message_rejected']]} day: 2026-11-19, order_count: 30, order_amount:  [9090.0000000000-->] 9240.0000000000, message_received: 8, message_processed: 4, message_rejected: 3, message_pending: 1, request_received: 35, request_processed: 27, request_rejected: 7, request_pending: 1  row: 0x10e237cd0  session: 0x10e4cd480  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:01,751 - logic_logger - INFO
......DailyFlow[2026-11-19] {Prune Formula: request_pending [['request_received', 'request_processed', 'request_rejected']]} day: 2026-11-19, order_count: 30, order_amount:  [9090.0000000000-->] 9240.0000000000, message_received: 8, message_processed: 4, message_rejected: 3, message_pending: 1, request_received: 35, request_processed: 27, request_rejected: 7, request_pending: 1  row: 0x10e237cd0  session: 0x10e4cd480  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:01,751 - logic_logger - INFO
......Customer[43] {Update - Adjusting customer: balance} id: 43, name: Quinn 1795146361742, balance:  [180.0000000000-->] 330.0000000000, credit_limit: 2000.0000000000, email: None, email_opt_out: None  row: 0x10e783550  session: 0x10e4cd480  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:01,751 - logic_logger - INFO
Logic Phase:		COMMIT LOGIC		(session=0x10e4cd480)   										 - 2026-11-19 19:46:01,751 - logic_logger - INFO
Logic Phase:		AFTER_FLUSH LOGIC	(session=0x10e4cd480)   										 - 2026-11-19 19:46:01,752 - logic_logger - INFO
..Order[218] {AfterFlush Event} id: 218, notes: behave test, customer_id: 43, CreatedOn: 2026-11-19, date_shipped: None, amount_total: 330.0000000000, CreatedOnDay: 2026-11-19  row: 0x10e7770b0  session: 0x10e4cd480  ins_upd_dlt: ins, initial: ins - 2026-11-19 19:46:01,752 - logic_logger - INFO


Logic Phase:		ROW LOGIC		(session=0x10e4cde10) (sqlalchemy before_flush)			 - 2026-11-19 19:46:01,757 - logic_logger - INFO
..Item[323] {Update - client} id: 323, order_id: 218, product_id: 2, quantity:  [2-->] 5, amount: 180.0000000000, unit_price: 90.0000000000  row: 0x10e7a7450  session: 0x10e4cde10  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:01,757 - logic_logger - INFO
..Item[323] {Formula amount} id: 323, order_id: 218, product_id: 2, quantity:  [2-->] 5, amount:  [180.0000000000-->] 450.0000000000, unit_price: 90.0000000000  row: 0x10e7a7450  session: 0x10e4cde10  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:01,757 - logic_logger - INFO
....Order[218] {Update - Adjusting order: amount_total} id: 218, notes: behave test, customer_id: 43, CreatedOn: 2026-11-19, date_shipped: None, amount_total:  [330.0000000000-->] 600.0000000000, CreatedOnDay: 2026-11-19  row: 0x10e777ad0  session: 0x10e4cde10  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:01,758 - logic_logger - INFO
......DailyFlow[2026-11-19] {Update - Adjusting daily_flow: order_amount} day: 2026-11-19, order_count: 30, order_amount:  [9240.00-->] 9510.0000000000, message_received: 8, message_processed: 4, message_rejected: 3, message_pending: 1, request_received: 35, request_processed: 27, request_rejected: 7, request_pending: 1  row: 0x10e237cd0  session: 0x10e4cde10  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:01,758 - logic_logger - INFO
......DailyFlow[2026-11-19] {Prune Formula: message_pending [['message_received', 'message_processed', 'message_rejected']]} day: 2026-11-19, order_count: 30, order_amount:  [9240.00-->] 9510.0000000000, message_received: 8, message_processed: 4, message_rejected: 3, message_pending: 1, request_received: 35, request_processed: 27, request_rejected: 7, request_pending: 1  row: 0x10e237cd0  session: 0x10e4cde10  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:01,758 - logic_logger - INFO
......DailyFlow[2026-11-19] {Prune Formula: request_pending [['request_received', 'request_processed', 'request_rejected']]} day: 2026-11-19, order_count: 30, order_amount:  [9240.00-->] 9510.0000000000, message_received: 8, message_processed: 4, message_rejected: 3, message_pending: 1, request_received: 35, request_processed: 27, request_rejected: 7, request_pending: 1  row: 0x10e237cd0  session: 0x10e4cde10  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:01,758 - logic_logger - INFO
......Customer[43] {Update - Adjusting customer: balance} id: 43, name: Quinn 1795146361742, balance:  [330.0000000000-->] 600.0000000000, credit_limit: 2000.0000000000, email: None, email_opt_out: None  row: 0x10e5740d0  session: 0x10e4cde10  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:01,759 - logic_logger - INFO
Logic Phase:		COMMIT LOGIC		(session=0x10e4cde10)   										 - 2026-11-19 19:46:01,759 - logic_logger - INFO
Logic Phase:		AFTER_FLUSH LOGIC	(session=0x10e4cde10)   										 - 2026-11-19 19:46:01,759 - logic_logger - INFO
....Order[218] {AfterFlush Event} id: 218, notes: behave test, customer_id: 43, CreatedOn: 2026-11-19, date_shipped: None, amount_total:  [330.0000000000-->] 600.0000000000, CreatedOnDay: 2026-11-19  row: 0x10e777ad0  session: 0x10e4cde10  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:01,759 - logic_logger - INFO

```
</details>

&nbsp;
&nbsp;

#### Scenario: Changing an item's product re-copies the price ✅ (0.03 s)
&emsp;  Scenario: Changing an item's product re-copies the price  
&emsp;&emsp;    Given a new customer "Ravi" with credit limit 2000  
&emsp;&emsp;    And a B2B order is placed for "Ravi" with 2 Widget  
&emsp;&emsp;    When the product of the first item is changed to Doodad  
&emsp;&emsp;    Then the first item unit price is 110  
&emsp;&emsp;    And the first item amount is 220  
&emsp;&emsp;    And the order total is 220  
&emsp;&emsp;    And the balance of "Ravi" is 220  

_No logic log for this scenario: the test does not open one, so no rules are shown for it (see "How to add more tests")._

&nbsp;
&nbsp;

#### Scenario: Deleting an item reduces the order total and balance ✅ (0.03 s)
&emsp;  Scenario: Deleting an item reduces the order total and balance  
&emsp;&emsp;    Given a new customer "Sam" with credit limit 2000  
&emsp;&emsp;    And a B2B order is placed for "Sam" with 2 Widget and 1 Gadget  
&emsp;&emsp;    When the first item is deleted  
&emsp;&emsp;    Then the order total is 150  
&emsp;&emsp;    And the balance of "Sam" is 150  

<details markdown>
<summary>Rules exercised and logic log (3 transactions)</summary>


&nbsp;
&nbsp;


**Rules Used** in Scenario: Deleting an item reduces the order total and balance
```
  DailyFlow  
    1. Derive DailyFlow.request_rejected as Count(OrderB2bRequest Where Rule.count(derive=models.DailyFlow.request_rejected, as_count_of=models.OrderB2bRequest, where=lambda row: row.error_text is not None, insert_parent=True), insert_parent)  
    2. Derive DailyFlow.request_pending as Formula (2): Rule.formula(derive=models.DailyFlow.request_pend [...]  
    3. Derive DailyFlow.request_processed as Count(OrderB2bRequest Where Rule.count(derive=models.DailyFlow.request_processed, as_count_of=models.OrderB2bRequest, where=lambda row: row.is_processed == True, insert_parent=True), insert_parent)  
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
**Logic Log** in Scenario: Deleting an item reduces the order total and balance (3 transactions)
```
Logic Phase:		ROW LOGIC		(session=0x10e4ce360) (sqlalchemy before_flush)			 - 2026-11-19 19:46:01,807 - logic_logger - INFO
..OrderB2bRequest[None] {Insert - client} id: None, CreatedOn: None, CreatedOnDay: None, payload: {"Account": "Sam 1795146361803", "Notes": "behave test", "Items": [{"Name": "Widget", "QuantityOrdered": 2}, {"Name": "Gadget", "QuantityOrdered": 1}]}, is_processed: False, error_text: None  row: 0x10e40fb50  session: 0x10e4ce360  ins_upd_dlt: ins, initial: ins - 2026-11-19 19:46:01,807 - logic_logger - INFO
..OrderB2bRequest[None] {early_row_event_all_classes - handle_all did stamping} id: None, CreatedOn: 2026-11-19 19:46:01.807154, CreatedOnDay: 2026-11-19, payload: {"Account": "Sam 1795146361803", "Notes": "behave test", "Items": [{"Name": "Widget", "QuantityOrdered": 2}, {"Name": "Gadget", "QuantityOrdered": 1}]}, is_processed: False, error_text: None  row: 0x10e40fb50  session: 0x10e4ce360  ins_upd_dlt: ins, initial: ins - 2026-11-19 19:46:01,807 - logic_logger - INFO
....DailyFlow[2026-11-19] {Update - Adjusting daily_flow: request_received} day: 2026-11-19, order_count: 31, order_amount: 9730.00, message_received: 8, message_processed: 4, message_rejected: 3, message_pending: 1, request_received:  [36-->] 37, request_processed: 28, request_rejected: 7, request_pending: 1  row: 0x10e236fc0  session: 0x10e4ce360  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:01,807 - logic_logger - INFO
....DailyFlow[2026-11-19] {Prune Formula: message_pending [['message_received', 'message_processed', 'message_rejected']]} day: 2026-11-19, order_count: 31, order_amount: 9730.00, message_received: 8, message_processed: 4, message_rejected: 3, message_pending: 1, request_received:  [36-->] 37, request_processed: 28, request_rejected: 7, request_pending: 1  row: 0x10e236fc0  session: 0x10e4ce360  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:01,807 - logic_logger - INFO
....DailyFlow[2026-11-19] {Formula request_pending} day: 2026-11-19, order_count: 31, order_amount: 9730.00, message_received: 8, message_processed: 4, message_rejected: 3, message_pending: 1, request_received:  [36-->] 37, request_processed: 28, request_rejected: 7, request_pending:  [1-->] 2  row: 0x10e236fc0  session: 0x10e4ce360  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:01,807 - logic_logger - INFO
Logic Phase:		COMMIT LOGIC		(session=0x10e4ce360)   										 - 2026-11-19 19:46:01,807 - logic_logger - INFO
Logic Phase:		AFTER_FLUSH LOGIC	(session=0x10e4ce360)   										 - 2026-11-19 19:46:01,807 - logic_logger - INFO


Logic Phase:		ROW LOGIC		(session=0x10e4ce360) (sqlalchemy before_flush)			 - 2026-11-19 19:46:01,810 - logic_logger - INFO
..OrderB2bRequest[143] {Update - client} id: 143, CreatedOn: 2026-11-19 19:46:01.807154, CreatedOnDay: 2026-11-19, payload: {"Account": "Sam 1795146361803", "Notes": "behave test", "Items": [{"Name": "Widget", "QuantityOrdered": 2}, {"Name": "Gadget", "QuantityOrdered": 1}]}, is_processed:  [False-->] True, error_text: None  row: 0x10e40fb50  session: 0x10e4ce360  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:01,810 - logic_logger - INFO
....DailyFlow[2026-11-19] {Update - Adjusting daily_flow: request_processed} day: 2026-11-19, order_count: 31, order_amount: 9730.00, message_received: 8, message_processed: 4, message_rejected: 3, message_pending: 1, request_received: 37, request_processed:  [28-->] 29, request_rejected: 7, request_pending: 2  row: 0x10e236fc0  session: 0x10e4ce360  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:01,810 - logic_logger - INFO
....DailyFlow[2026-11-19] {Prune Formula: message_pending [['message_received', 'message_processed', 'message_rejected']]} day: 2026-11-19, order_count: 31, order_amount: 9730.00, message_received: 8, message_processed: 4, message_rejected: 3, message_pending: 1, request_received: 37, request_processed:  [28-->] 29, request_rejected: 7, request_pending: 2  row: 0x10e236fc0  session: 0x10e4ce360  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:01,810 - logic_logger - INFO
....DailyFlow[2026-11-19] {Formula request_pending} day: 2026-11-19, order_count: 31, order_amount: 9730.00, message_received: 8, message_processed: 4, message_rejected: 3, message_pending: 1, request_received: 37, request_processed:  [28-->] 29, request_rejected: 7, request_pending:  [2-->] 1  row: 0x10e236fc0  session: 0x10e4ce360  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:01,810 - logic_logger - INFO
..Product[1] {Update - client} id: 1, name: Gadget, count_suppliers: 0, unit_price: 150.0000000000  row: 0x10e7f5320  session: 0x10e4ce360  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:01,810 - logic_logger - INFO
..Order[None] {Insert - client} id: None, notes: behave test, customer_id: 45, CreatedOn: None, date_shipped: None, amount_total: None, CreatedOnDay: None  row: 0x10e830320  session: 0x10e4ce360  ins_upd_dlt: ins, initial: ins - 2026-11-19 19:46:01,811 - logic_logger - INFO
..Order[None] {early_row_event_all_classes - handle_all did stamping} id: None, notes: behave test, customer_id: 45, CreatedOn: 2026-11-19, date_shipped: None, amount_total: None, CreatedOnDay: 2026-11-19  row: 0x10e830320  session: 0x10e4ce360  ins_upd_dlt: ins, initial: ins - 2026-11-19 19:46:01,811 - logic_logger - INFO
..Order[None] {server aggregate_defaults: amount_total } id: None, notes: behave test, customer_id: 45, CreatedOn: 2026-11-19, date_shipped: None, amount_total: 0, CreatedOnDay: 2026-11-19  row: 0x10e830320  session: 0x10e4ce360  ins_upd_dlt: ins, initial: ins - 2026-11-19 19:46:01,811 - logic_logger - INFO
....DailyFlow[2026-11-19] {Update - Adjusting daily_flow: order_count} day: 2026-11-19, order_count:  [31-->] 32, order_amount: 9730.00, message_received: 8, message_processed: 4, message_rejected: 3, message_pending: 1, request_received: 37, request_processed: 29, request_rejected: 7, request_pending: 1  row: 0x10e236fc0  session: 0x10e4ce360  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:01,811 - logic_logger - INFO
....DailyFlow[2026-11-19] {Prune Formula: message_pending [['message_received', 'message_processed', 'message_rejected']]} day: 2026-11-19, order_count:  [31-->] 32, order_amount: 9730.00, message_received: 8, message_processed: 4, message_rejected: 3, message_pending: 1, request_received: 37, request_processed: 29, request_rejected: 7, request_pending: 1  row: 0x10e236fc0  session: 0x10e4ce360  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:01,811 - logic_logger - INFO
....DailyFlow[2026-11-19] {Prune Formula: request_pending [['request_received', 'request_processed', 'request_rejected']]} day: 2026-11-19, order_count:  [31-->] 32, order_amount: 9730.00, message_received: 8, message_processed: 4, message_rejected: 3, message_pending: 1, request_received: 37, request_processed: 29, request_rejected: 7, request_pending: 1  row: 0x10e236fc0  session: 0x10e4ce360  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:01,811 - logic_logger - INFO
..Item[None] {Insert - client} id: None, order_id: None, product_id: 2, quantity: 2, amount: None, unit_price: None  row: 0x10e5748d0  session: 0x10e4ce360  ins_upd_dlt: ins, initial: ins - 2026-11-19 19:46:01,811 - logic_logger - INFO
..Item[None] {copy_rules for role: product - unit_price} id: None, order_id: None, product_id: 2, quantity: 2, amount: None, unit_price: 90.0000000000  row: 0x10e5748d0  session: 0x10e4ce360  ins_upd_dlt: ins, initial: ins - 2026-11-19 19:46:01,811 - logic_logger - INFO
..Item[None] {Formula amount} id: None, order_id: None, product_id: 2, quantity: 2, amount: 180.0000000000, unit_price: 90.0000000000  row: 0x10e5748d0  session: 0x10e4ce360  ins_upd_dlt: ins, initial: ins - 2026-11-19 19:46:01,811 - logic_logger - INFO
....Order[None] {Update - Adjusting order: amount_total} id: None, notes: behave test, customer_id: 45, CreatedOn: 2026-11-19, date_shipped: None, amount_total:  [0-->] 180.0000000000, CreatedOnDay: 2026-11-19  row: 0x10e830320  session: 0x10e4ce360  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:01,811 - logic_logger - INFO
......DailyFlow[2026-11-19] {Update - Adjusting daily_flow: order_amount} day: 2026-11-19, order_count: 32, order_amount:  [9730.00-->] 9910.0000000000, message_received: 8, message_processed: 4, message_rejected: 3, message_pending: 1, request_received: 37, request_processed: 29, request_rejected: 7, request_pending: 1  row: 0x10e236fc0  session: 0x10e4ce360  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:01,811 - logic_logger - INFO
......DailyFlow[2026-11-19] {Prune Formula: message_pending [['message_received', 'message_processed', 'message_rejected']]} day: 2026-11-19, order_count: 32, order_amount:  [9730.00-->] 9910.0000000000, message_received: 8, message_processed: 4, message_rejected: 3, message_pending: 1, request_received: 37, request_processed: 29, request_rejected: 7, request_pending: 1  row: 0x10e236fc0  session: 0x10e4ce360  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:01,811 - logic_logger - INFO
......DailyFlow[2026-11-19] {Prune Formula: request_pending [['request_received', 'request_processed', 'request_rejected']]} day: 2026-11-19, order_count: 32, order_amount:  [9730.00-->] 9910.0000000000, message_received: 8, message_processed: 4, message_rejected: 3, message_pending: 1, request_received: 37, request_processed: 29, request_rejected: 7, request_pending: 1  row: 0x10e236fc0  session: 0x10e4ce360  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:01,811 - logic_logger - INFO
......Customer[45] {Update - Adjusting customer: balance} id: 45, name: Sam 1795146361803, balance:  [0E-10-->] 180.0000000000, credit_limit: 2000.0000000000, email: None, email_opt_out: None  row: 0x10e7a4fd0  session: 0x10e4ce360  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:01,811 - logic_logger - INFO
..Item[None] {Insert - client} id: None, order_id: None, product_id: None, quantity: 1, amount: None, unit_price: None  row: 0x10e783150  session: 0x10e4ce360  ins_upd_dlt: ins, initial: ins - 2026-11-19 19:46:01,812 - logic_logger - INFO
..Item[None] {copy_rules for role: product - unit_price} id: None, order_id: None, product_id: None, quantity: 1, amount: None, unit_price: 150.0000000000  row: 0x10e783150  session: 0x10e4ce360  ins_upd_dlt: ins, initial: ins - 2026-11-19 19:46:01,812 - logic_logger - INFO
..Item[None] {Formula amount} id: None, order_id: None, product_id: None, quantity: 1, amount: 150.0000000000, unit_price: 150.0000000000  row: 0x10e783150  session: 0x10e4ce360  ins_upd_dlt: ins, initial: ins - 2026-11-19 19:46:01,812 - logic_logger - INFO
....Order[None] {Update - Adjusting order: amount_total} id: None, notes: behave test, customer_id: 45, CreatedOn: 2026-11-19, date_shipped: None, amount_total:  [180.0000000000-->] 330.0000000000, CreatedOnDay: 2026-11-19  row: 0x10e830320  session: 0x10e4ce360  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:01,812 - logic_logger - INFO
......DailyFlow[2026-11-19] {Update - Adjusting daily_flow: order_amount} day: 2026-11-19, order_count: 32, order_amount:  [9910.0000000000-->] 10060.0000000000, message_received: 8, message_processed: 4, message_rejected: 3, message_pending: 1, request_received: 37, request_processed: 29, request_rejected: 7, request_pending: 1  row: 0x10e236fc0  session: 0x10e4ce360  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:01,812 - logic_logger - INFO
......DailyFlow[2026-11-19] {Prune Formula: message_pending [['message_received', 'message_processed', 'message_rejected']]} day: 2026-11-19, order_count: 32, order_amount:  [9910.0000000000-->] 10060.0000000000, message_received: 8, message_processed: 4, message_rejected: 3, message_pending: 1, request_received: 37, request_processed: 29, request_rejected: 7, request_pending: 1  row: 0x10e236fc0  session: 0x10e4ce360  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:01,812 - logic_logger - INFO
......DailyFlow[2026-11-19] {Prune Formula: request_pending [['request_received', 'request_processed', 'request_rejected']]} day: 2026-11-19, order_count: 32, order_amount:  [9910.0000000000-->] 10060.0000000000, message_received: 8, message_processed: 4, message_rejected: 3, message_pending: 1, request_received: 37, request_processed: 29, request_rejected: 7, request_pending: 1  row: 0x10e236fc0  session: 0x10e4ce360  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:01,812 - logic_logger - INFO
......Customer[45] {Update - Adjusting customer: balance} id: 45, name: Sam 1795146361803, balance:  [180.0000000000-->] 330.0000000000, credit_limit: 2000.0000000000, email: None, email_opt_out: None  row: 0x10e7a4fd0  session: 0x10e4ce360  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:01,812 - logic_logger - INFO
Logic Phase:		COMMIT LOGIC		(session=0x10e4ce360)   										 - 2026-11-19 19:46:01,812 - logic_logger - INFO
Logic Phase:		AFTER_FLUSH LOGIC	(session=0x10e4ce360)   										 - 2026-11-19 19:46:01,813 - logic_logger - INFO
..Order[220] {AfterFlush Event} id: 220, notes: behave test, customer_id: 45, CreatedOn: 2026-11-19, date_shipped: None, amount_total: 330.0000000000, CreatedOnDay: 2026-11-19  row: 0x10e830320  session: 0x10e4ce360  ins_upd_dlt: ins, initial: ins - 2026-11-19 19:46:01,813 - logic_logger - INFO


Logic Phase:		ROW LOGIC		(session=0x10e433f00) (sqlalchemy before_flush)			 - 2026-11-19 19:46:01,818 - logic_logger - INFO
..Item[326] {Delete - client} id: 326, order_id: 220, product_id: 2, quantity: 2, amount: 180.0000000000, unit_price: 90.0000000000  row: 0x10e809dd0  session: 0x10e433f00  ins_upd_dlt: dlt, initial: dlt - 2026-11-19 19:46:01,818 - logic_logger - INFO
....Order[220] {Update - Adjusting order: amount_total} id: 220, notes: behave test, customer_id: 45, CreatedOn: 2026-11-19, date_shipped: None, amount_total:  [330.0000000000-->] 150.0000000000, CreatedOnDay: 2026-11-19  row: 0x10e776d50  session: 0x10e433f00  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:01,818 - logic_logger - INFO
......DailyFlow[2026-11-19] {Update - Adjusting daily_flow: order_amount} day: 2026-11-19, order_count: 32, order_amount:  [10060.00-->] 9880.0000000000, message_received: 8, message_processed: 4, message_rejected: 3, message_pending: 1, request_received: 37, request_processed: 29, request_rejected: 7, request_pending: 1  row: 0x10e235d30  session: 0x10e433f00  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:01,818 - logic_logger - INFO
......DailyFlow[2026-11-19] {Prune Formula: message_pending [['message_received', 'message_processed', 'message_rejected']]} day: 2026-11-19, order_count: 32, order_amount:  [10060.00-->] 9880.0000000000, message_received: 8, message_processed: 4, message_rejected: 3, message_pending: 1, request_received: 37, request_processed: 29, request_rejected: 7, request_pending: 1  row: 0x10e235d30  session: 0x10e433f00  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:01,819 - logic_logger - INFO
......DailyFlow[2026-11-19] {Prune Formula: request_pending [['request_received', 'request_processed', 'request_rejected']]} day: 2026-11-19, order_count: 32, order_amount:  [10060.00-->] 9880.0000000000, message_received: 8, message_processed: 4, message_rejected: 3, message_pending: 1, request_received: 37, request_processed: 29, request_rejected: 7, request_pending: 1  row: 0x10e235d30  session: 0x10e433f00  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:01,819 - logic_logger - INFO
......Customer[45] {Update - Adjusting customer: balance} id: 45, name: Sam 1795146361803, balance:  [330.0000000000-->] 150.0000000000, credit_limit: 2000.0000000000, email: None, email_opt_out: None  row: 0x10e7a6150  session: 0x10e433f00  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:01,819 - logic_logger - INFO
Logic Phase:		COMMIT LOGIC		(session=0x10e433f00)   										 - 2026-11-19 19:46:01,819 - logic_logger - INFO
Logic Phase:		AFTER_FLUSH LOGIC	(session=0x10e433f00)   										 - 2026-11-19 19:46:01,820 - logic_logger - INFO
....Order[220] {AfterFlush Event} id: 220, notes: behave test, customer_id: 45, CreatedOn: 2026-11-19, date_shipped: None, amount_total:  [330.0000000000-->] 150.0000000000, CreatedOnDay: 2026-11-19  row: 0x10e776d50  session: 0x10e433f00  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:01,820 - logic_logger - INFO

```
</details>

&nbsp;
&nbsp;

#### Scenario: Moving an item to another order adjusts both orders ✅ (0.04 s)
&emsp;  Scenario: Moving an item to another order adjusts both orders  
&emsp;&emsp;    Given a new customer "Tara" with credit limit 5000  
&emsp;&emsp;    And a B2B order is placed for "Tara" with 2 Widget and 1 Gadget  
&emsp;&emsp;    And a second B2B order is placed for "Tara" with 1 Doodad  
&emsp;&emsp;    When the first item of the first order is moved to the second order  
&emsp;&emsp;    Then the first order total is 150  
&emsp;&emsp;    And the second order total is 290  
&emsp;&emsp;    And the balance of "Tara" is 440  

<details markdown>
<summary>Rules exercised and logic log (5 transactions)</summary>


&nbsp;
&nbsp;


**Rules Used** in Scenario: Moving an item to another order adjusts both orders
```
  DailyFlow  
    1. Derive DailyFlow.request_rejected as Count(OrderB2bRequest Where Rule.count(derive=models.DailyFlow.request_rejected, as_count_of=models.OrderB2bRequest, where=lambda row: row.error_text is not None, insert_parent=True), insert_parent)  
    2. Derive DailyFlow.request_pending as Formula (2): Rule.formula(derive=models.DailyFlow.request_pend [...]  
    3. Derive DailyFlow.request_processed as Count(OrderB2bRequest Where Rule.count(derive=models.DailyFlow.request_processed, as_count_of=models.OrderB2bRequest, where=lambda row: row.is_processed == True, insert_parent=True), insert_parent)  
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
**Logic Log** in Scenario: Moving an item to another order adjusts both orders (5 transactions)
```
Logic Phase:		ROW LOGIC		(session=0x10e4ccd10) (sqlalchemy before_flush)			 - 2026-11-19 19:46:01,835 - logic_logger - INFO
..OrderB2bRequest[None] {Insert - client} id: None, CreatedOn: None, CreatedOnDay: None, payload: {"Account": "Tara 1795146361828", "Notes": "behave test", "Items": [{"Name": "Widget", "QuantityOrdered": 2}, {"Name": "Gadget", "QuantityOrdered": 1}]}, is_processed: False, error_text: None  row: 0x10e454050  session: 0x10e4ccd10  ins_upd_dlt: ins, initial: ins - 2026-11-19 19:46:01,835 - logic_logger - INFO
..OrderB2bRequest[None] {early_row_event_all_classes - handle_all did stamping} id: None, CreatedOn: 2026-11-19 19:46:01.835344, CreatedOnDay: 2026-11-19, payload: {"Account": "Tara 1795146361828", "Notes": "behave test", "Items": [{"Name": "Widget", "QuantityOrdered": 2}, {"Name": "Gadget", "QuantityOrdered": 1}]}, is_processed: False, error_text: None  row: 0x10e454050  session: 0x10e4ccd10  ins_upd_dlt: ins, initial: ins - 2026-11-19 19:46:01,835 - logic_logger - INFO
....DailyFlow[2026-11-19] {Update - Adjusting daily_flow: request_received} day: 2026-11-19, order_count: 32, order_amount: 9880.00, message_received: 8, message_processed: 4, message_rejected: 3, message_pending: 1, request_received:  [37-->] 38, request_processed: 29, request_rejected: 7, request_pending: 1  row: 0x10e236780  session: 0x10e4ccd10  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:01,835 - logic_logger - INFO
....DailyFlow[2026-11-19] {Prune Formula: message_pending [['message_received', 'message_processed', 'message_rejected']]} day: 2026-11-19, order_count: 32, order_amount: 9880.00, message_received: 8, message_processed: 4, message_rejected: 3, message_pending: 1, request_received:  [37-->] 38, request_processed: 29, request_rejected: 7, request_pending: 1  row: 0x10e236780  session: 0x10e4ccd10  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:01,836 - logic_logger - INFO
....DailyFlow[2026-11-19] {Formula request_pending} day: 2026-11-19, order_count: 32, order_amount: 9880.00, message_received: 8, message_processed: 4, message_rejected: 3, message_pending: 1, request_received:  [37-->] 38, request_processed: 29, request_rejected: 7, request_pending:  [1-->] 2  row: 0x10e236780  session: 0x10e4ccd10  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:01,836 - logic_logger - INFO
Logic Phase:		COMMIT LOGIC		(session=0x10e4ccd10)   										 - 2026-11-19 19:46:01,836 - logic_logger - INFO
Logic Phase:		AFTER_FLUSH LOGIC	(session=0x10e4ccd10)   										 - 2026-11-19 19:46:01,836 - logic_logger - INFO


Logic Phase:		ROW LOGIC		(session=0x10e4ccd10) (sqlalchemy before_flush)			 - 2026-11-19 19:46:01,839 - logic_logger - INFO
..OrderB2bRequest[144] {Update - client} id: 144, CreatedOn: 2026-11-19 19:46:01.835344, CreatedOnDay: 2026-11-19, payload: {"Account": "Tara 1795146361828", "Notes": "behave test", "Items": [{"Name": "Widget", "QuantityOrdered": 2}, {"Name": "Gadget", "QuantityOrdered": 1}]}, is_processed:  [False-->] True, error_text: None  row: 0x10e454050  session: 0x10e4ccd10  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:01,839 - logic_logger - INFO
....DailyFlow[2026-11-19] {Update - Adjusting daily_flow: request_processed} day: 2026-11-19, order_count: 32, order_amount: 9880.00, message_received: 8, message_processed: 4, message_rejected: 3, message_pending: 1, request_received: 38, request_processed:  [29-->] 30, request_rejected: 7, request_pending: 2  row: 0x10e236780  session: 0x10e4ccd10  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:01,839 - logic_logger - INFO
....DailyFlow[2026-11-19] {Prune Formula: message_pending [['message_received', 'message_processed', 'message_rejected']]} day: 2026-11-19, order_count: 32, order_amount: 9880.00, message_received: 8, message_processed: 4, message_rejected: 3, message_pending: 1, request_received: 38, request_processed:  [29-->] 30, request_rejected: 7, request_pending: 2  row: 0x10e236780  session: 0x10e4ccd10  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:01,839 - logic_logger - INFO
....DailyFlow[2026-11-19] {Formula request_pending} day: 2026-11-19, order_count: 32, order_amount: 9880.00, message_received: 8, message_processed: 4, message_rejected: 3, message_pending: 1, request_received: 38, request_processed:  [29-->] 30, request_rejected: 7, request_pending:  [2-->] 1  row: 0x10e236780  session: 0x10e4ccd10  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:01,839 - logic_logger - INFO
..Product[1] {Update - client} id: 1, name: Gadget, count_suppliers: 0, unit_price: 150.0000000000  row: 0x10e7f5160  session: 0x10e4ccd10  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:01,839 - logic_logger - INFO
..Order[None] {Insert - client} id: None, notes: behave test, customer_id: 46, CreatedOn: None, date_shipped: None, amount_total: None, CreatedOnDay: None  row: 0x10e777650  session: 0x10e4ccd10  ins_upd_dlt: ins, initial: ins - 2026-11-19 19:46:01,840 - logic_logger - INFO
..Order[None] {early_row_event_all_classes - handle_all did stamping} id: None, notes: behave test, customer_id: 46, CreatedOn: 2026-11-19, date_shipped: None, amount_total: None, CreatedOnDay: 2026-11-19  row: 0x10e777650  session: 0x10e4ccd10  ins_upd_dlt: ins, initial: ins - 2026-11-19 19:46:01,840 - logic_logger - INFO
..Order[None] {server aggregate_defaults: amount_total } id: None, notes: behave test, customer_id: 46, CreatedOn: 2026-11-19, date_shipped: None, amount_total: 0, CreatedOnDay: 2026-11-19  row: 0x10e777650  session: 0x10e4ccd10  ins_upd_dlt: ins, initial: ins - 2026-11-19 19:46:01,840 - logic_logger - INFO
....DailyFlow[2026-11-19] {Update - Adjusting daily_flow: order_count} day: 2026-11-19, order_count:  [32-->] 33, order_amount: 9880.00, message_received: 8, message_processed: 4, message_rejected: 3, message_pending: 1, request_received: 38, request_processed: 30, request_rejected: 7, request_pending: 1  row: 0x10e236780  session: 0x10e4ccd10  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:01,840 - logic_logger - INFO
....DailyFlow[2026-11-19] {Prune Formula: message_pending [['message_received', 'message_processed', 'message_rejected']]} day: 2026-11-19, order_count:  [32-->] 33, order_amount: 9880.00, message_received: 8, message_processed: 4, message_rejected: 3, message_pending: 1, request_received: 38, request_processed: 30, request_rejected: 7, request_pending: 1  row: 0x10e236780  session: 0x10e4ccd10  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:01,840 - logic_logger - INFO
....DailyFlow[2026-11-19] {Prune Formula: request_pending [['request_received', 'request_processed', 'request_rejected']]} day: 2026-11-19, order_count:  [32-->] 33, order_amount: 9880.00, message_received: 8, message_processed: 4, message_rejected: 3, message_pending: 1, request_received: 38, request_processed: 30, request_rejected: 7, request_pending: 1  row: 0x10e236780  session: 0x10e4ccd10  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:01,840 - logic_logger - INFO
..Item[None] {Insert - client} id: None, order_id: None, product_id: 2, quantity: 2, amount: None, unit_price: None  row: 0x10e808dd0  session: 0x10e4ccd10  ins_upd_dlt: ins, initial: ins - 2026-11-19 19:46:01,840 - logic_logger - INFO
..Item[None] {copy_rules for role: product - unit_price} id: None, order_id: None, product_id: 2, quantity: 2, amount: None, unit_price: 90.0000000000  row: 0x10e808dd0  session: 0x10e4ccd10  ins_upd_dlt: ins, initial: ins - 2026-11-19 19:46:01,840 - logic_logger - INFO
..Item[None] {Formula amount} id: None, order_id: None, product_id: 2, quantity: 2, amount: 180.0000000000, unit_price: 90.0000000000  row: 0x10e808dd0  session: 0x10e4ccd10  ins_upd_dlt: ins, initial: ins - 2026-11-19 19:46:01,840 - logic_logger - INFO
....Order[None] {Update - Adjusting order: amount_total} id: None, notes: behave test, customer_id: 46, CreatedOn: 2026-11-19, date_shipped: None, amount_total:  [0-->] 180.0000000000, CreatedOnDay: 2026-11-19  row: 0x10e777650  session: 0x10e4ccd10  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:01,840 - logic_logger - INFO
......DailyFlow[2026-11-19] {Update - Adjusting daily_flow: order_amount} day: 2026-11-19, order_count: 33, order_amount:  [9880.00-->] 10060.0000000000, message_received: 8, message_processed: 4, message_rejected: 3, message_pending: 1, request_received: 38, request_processed: 30, request_rejected: 7, request_pending: 1  row: 0x10e236780  session: 0x10e4ccd10  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:01,840 - logic_logger - INFO
......DailyFlow[2026-11-19] {Prune Formula: message_pending [['message_received', 'message_processed', 'message_rejected']]} day: 2026-11-19, order_count: 33, order_amount:  [9880.00-->] 10060.0000000000, message_received: 8, message_processed: 4, message_rejected: 3, message_pending: 1, request_received: 38, request_processed: 30, request_rejected: 7, request_pending: 1  row: 0x10e236780  session: 0x10e4ccd10  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:01,840 - logic_logger - INFO
......DailyFlow[2026-11-19] {Prune Formula: request_pending [['request_received', 'request_processed', 'request_rejected']]} day: 2026-11-19, order_count: 33, order_amount:  [9880.00-->] 10060.0000000000, message_received: 8, message_processed: 4, message_rejected: 3, message_pending: 1, request_received: 38, request_processed: 30, request_rejected: 7, request_pending: 1  row: 0x10e236780  session: 0x10e4ccd10  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:01,840 - logic_logger - INFO
......Customer[46] {Update - Adjusting customer: balance} id: 46, name: Tara 1795146361828, balance:  [0E-10-->] 180.0000000000, credit_limit: 5000.0000000000, email: None, email_opt_out: None  row: 0x10e8094d0  session: 0x10e4ccd10  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:01,840 - logic_logger - INFO
..Item[None] {Insert - client} id: None, order_id: None, product_id: None, quantity: 1, amount: None, unit_price: None  row: 0x10e2dd350  session: 0x10e4ccd10  ins_upd_dlt: ins, initial: ins - 2026-11-19 19:46:01,840 - logic_logger - INFO
..Item[None] {copy_rules for role: product - unit_price} id: None, order_id: None, product_id: None, quantity: 1, amount: None, unit_price: 150.0000000000  row: 0x10e2dd350  session: 0x10e4ccd10  ins_upd_dlt: ins, initial: ins - 2026-11-19 19:46:01,841 - logic_logger - INFO
..Item[None] {Formula amount} id: None, order_id: None, product_id: None, quantity: 1, amount: 150.0000000000, unit_price: 150.0000000000  row: 0x10e2dd350  session: 0x10e4ccd10  ins_upd_dlt: ins, initial: ins - 2026-11-19 19:46:01,841 - logic_logger - INFO
....Order[None] {Update - Adjusting order: amount_total} id: None, notes: behave test, customer_id: 46, CreatedOn: 2026-11-19, date_shipped: None, amount_total:  [180.0000000000-->] 330.0000000000, CreatedOnDay: 2026-11-19  row: 0x10e777650  session: 0x10e4ccd10  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:01,841 - logic_logger - INFO
......DailyFlow[2026-11-19] {Update - Adjusting daily_flow: order_amount} day: 2026-11-19, order_count: 33, order_amount:  [10060.0000000000-->] 10210.0000000000, message_received: 8, message_processed: 4, message_rejected: 3, message_pending: 1, request_received: 38, request_processed: 30, request_rejected: 7, request_pending: 1  row: 0x10e236780  session: 0x10e4ccd10  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:01,841 - logic_logger - INFO
......DailyFlow[2026-11-19] {Prune Formula: message_pending [['message_received', 'message_processed', 'message_rejected']]} day: 2026-11-19, order_count: 33, order_amount:  [10060.0000000000-->] 10210.0000000000, message_received: 8, message_processed: 4, message_rejected: 3, message_pending: 1, request_received: 38, request_processed: 30, request_rejected: 7, request_pending: 1  row: 0x10e236780  session: 0x10e4ccd10  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:01,841 - logic_logger - INFO
......DailyFlow[2026-11-19] {Prune Formula: request_pending [['request_received', 'request_processed', 'request_rejected']]} day: 2026-11-19, order_count: 33, order_amount:  [10060.0000000000-->] 10210.0000000000, message_received: 8, message_processed: 4, message_rejected: 3, message_pending: 1, request_received: 38, request_processed: 30, request_rejected: 7, request_pending: 1  row: 0x10e236780  session: 0x10e4ccd10  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:01,841 - logic_logger - INFO
......Customer[46] {Update - Adjusting customer: balance} id: 46, name: Tara 1795146361828, balance:  [180.0000000000-->] 330.0000000000, credit_limit: 5000.0000000000, email: None, email_opt_out: None  row: 0x10e8094d0  session: 0x10e4ccd10  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:01,841 - logic_logger - INFO
Logic Phase:		COMMIT LOGIC		(session=0x10e4ccd10)   										 - 2026-11-19 19:46:01,841 - logic_logger - INFO
Logic Phase:		AFTER_FLUSH LOGIC	(session=0x10e4ccd10)   										 - 2026-11-19 19:46:01,842 - logic_logger - INFO
..Order[221] {AfterFlush Event} id: 221, notes: behave test, customer_id: 46, CreatedOn: 2026-11-19, date_shipped: None, amount_total: 330.0000000000, CreatedOnDay: 2026-11-19  row: 0x10e777650  session: 0x10e4ccd10  ins_upd_dlt: ins, initial: ins - 2026-11-19 19:46:01,842 - logic_logger - INFO


Logic Phase:		ROW LOGIC		(session=0x10e4ce690) (sqlalchemy before_flush)			 - 2026-11-19 19:46:01,844 - logic_logger - INFO
..OrderB2bRequest[None] {Insert - client} id: None, CreatedOn: None, CreatedOnDay: None, payload: {"Account": "Tara 1795146361828", "Notes": "behave test", "Items": [{"Name": "Doodad", "QuantityOrdered": 1}]}, is_processed: False, error_text: None  row: 0x10e8083d0  session: 0x10e4ce690  ins_upd_dlt: ins, initial: ins - 2026-11-19 19:46:01,844 - logic_logger - INFO
..OrderB2bRequest[None] {early_row_event_all_classes - handle_all did stamping} id: None, CreatedOn: 2026-11-19 19:46:01.844916, CreatedOnDay: 2026-11-19, payload: {"Account": "Tara 1795146361828", "Notes": "behave test", "Items": [{"Name": "Doodad", "QuantityOrdered": 1}]}, is_processed: False, error_text: None  row: 0x10e8083d0  session: 0x10e4ce690  ins_upd_dlt: ins, initial: ins - 2026-11-19 19:46:01,844 - logic_logger - INFO
....DailyFlow[2026-11-19] {Update - Adjusting daily_flow: request_received} day: 2026-11-19, order_count: 33, order_amount: 10210.00, message_received: 8, message_processed: 4, message_rejected: 3, message_pending: 1, request_received:  [38-->] 39, request_processed: 30, request_rejected: 7, request_pending: 1  row: 0x10e237c20  session: 0x10e4ce690  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:01,845 - logic_logger - INFO
....DailyFlow[2026-11-19] {Prune Formula: message_pending [['message_received', 'message_processed', 'message_rejected']]} day: 2026-11-19, order_count: 33, order_amount: 10210.00, message_received: 8, message_processed: 4, message_rejected: 3, message_pending: 1, request_received:  [38-->] 39, request_processed: 30, request_rejected: 7, request_pending: 1  row: 0x10e237c20  session: 0x10e4ce690  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:01,845 - logic_logger - INFO
....DailyFlow[2026-11-19] {Formula request_pending} day: 2026-11-19, order_count: 33, order_amount: 10210.00, message_received: 8, message_processed: 4, message_rejected: 3, message_pending: 1, request_received:  [38-->] 39, request_processed: 30, request_rejected: 7, request_pending:  [1-->] 2  row: 0x10e237c20  session: 0x10e4ce690  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:01,845 - logic_logger - INFO
Logic Phase:		COMMIT LOGIC		(session=0x10e4ce690)   										 - 2026-11-19 19:46:01,845 - logic_logger - INFO
Logic Phase:		AFTER_FLUSH LOGIC	(session=0x10e4ce690)   										 - 2026-11-19 19:46:01,845 - logic_logger - INFO


Logic Phase:		ROW LOGIC		(session=0x10e4ce690) (sqlalchemy before_flush)			 - 2026-11-19 19:46:01,847 - logic_logger - INFO
..OrderB2bRequest[145] {Update - client} id: 145, CreatedOn: 2026-11-19 19:46:01.844916, CreatedOnDay: 2026-11-19, payload: {"Account": "Tara 1795146361828", "Notes": "behave test", "Items": [{"Name": "Doodad", "QuantityOrdered": 1}]}, is_processed:  [False-->] True, error_text: None  row: 0x10e8083d0  session: 0x10e4ce690  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:01,848 - logic_logger - INFO
....DailyFlow[2026-11-19] {Update - Adjusting daily_flow: request_processed} day: 2026-11-19, order_count: 33, order_amount: 10210.00, message_received: 8, message_processed: 4, message_rejected: 3, message_pending: 1, request_received: 39, request_processed:  [30-->] 31, request_rejected: 7, request_pending: 2  row: 0x10e237c20  session: 0x10e4ce690  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:01,848 - logic_logger - INFO
....DailyFlow[2026-11-19] {Prune Formula: message_pending [['message_received', 'message_processed', 'message_rejected']]} day: 2026-11-19, order_count: 33, order_amount: 10210.00, message_received: 8, message_processed: 4, message_rejected: 3, message_pending: 1, request_received: 39, request_processed:  [30-->] 31, request_rejected: 7, request_pending: 2  row: 0x10e237c20  session: 0x10e4ce690  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:01,848 - logic_logger - INFO
....DailyFlow[2026-11-19] {Formula request_pending} day: 2026-11-19, order_count: 33, order_amount: 10210.00, message_received: 8, message_processed: 4, message_rejected: 3, message_pending: 1, request_received: 39, request_processed:  [30-->] 31, request_rejected: 7, request_pending:  [2-->] 1  row: 0x10e237c20  session: 0x10e4ce690  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:01,848 - logic_logger - INFO
..Product[4] {Update - client} id: 4, name: Doodad, count_suppliers: 0, unit_price: 110.0000000000  row: 0x10e7f5860  session: 0x10e4ce690  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:01,848 - logic_logger - INFO
..Order[None] {Insert - client} id: None, notes: behave test, customer_id: 46, CreatedOn: None, date_shipped: None, amount_total: None, CreatedOnDay: None  row: 0x10e777530  session: 0x10e4ce690  ins_upd_dlt: ins, initial: ins - 2026-11-19 19:46:01,848 - logic_logger - INFO
..Order[None] {early_row_event_all_classes - handle_all did stamping} id: None, notes: behave test, customer_id: 46, CreatedOn: 2026-11-19, date_shipped: None, amount_total: None, CreatedOnDay: 2026-11-19  row: 0x10e777530  session: 0x10e4ce690  ins_upd_dlt: ins, initial: ins - 2026-11-19 19:46:01,848 - logic_logger - INFO
..Order[None] {server aggregate_defaults: amount_total } id: None, notes: behave test, customer_id: 46, CreatedOn: 2026-11-19, date_shipped: None, amount_total: 0, CreatedOnDay: 2026-11-19  row: 0x10e777530  session: 0x10e4ce690  ins_upd_dlt: ins, initial: ins - 2026-11-19 19:46:01,848 - logic_logger - INFO
....DailyFlow[2026-11-19] {Update - Adjusting daily_flow: order_count} day: 2026-11-19, order_count:  [33-->] 34, order_amount: 10210.00, message_received: 8, message_processed: 4, message_rejected: 3, message_pending: 1, request_received: 39, request_processed: 31, request_rejected: 7, request_pending: 1  row: 0x10e237c20  session: 0x10e4ce690  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:01,848 - logic_logger - INFO
....DailyFlow[2026-11-19] {Prune Formula: message_pending [['message_received', 'message_processed', 'message_rejected']]} day: 2026-11-19, order_count:  [33-->] 34, order_amount: 10210.00, message_received: 8, message_processed: 4, message_rejected: 3, message_pending: 1, request_received: 39, request_processed: 31, request_rejected: 7, request_pending: 1  row: 0x10e237c20  session: 0x10e4ce690  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:01,848 - logic_logger - INFO
....DailyFlow[2026-11-19] {Prune Formula: request_pending [['request_received', 'request_processed', 'request_rejected']]} day: 2026-11-19, order_count:  [33-->] 34, order_amount: 10210.00, message_received: 8, message_processed: 4, message_rejected: 3, message_pending: 1, request_received: 39, request_processed: 31, request_rejected: 7, request_pending: 1  row: 0x10e237c20  session: 0x10e4ce690  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:01,848 - logic_logger - INFO
..Item[None] {Insert - client} id: None, order_id: None, product_id: None, quantity: 1, amount: None, unit_price: None  row: 0x10e53e750  session: 0x10e4ce690  ins_upd_dlt: ins, initial: ins - 2026-11-19 19:46:01,848 - logic_logger - INFO
..Item[None] {copy_rules for role: product - unit_price} id: None, order_id: None, product_id: None, quantity: 1, amount: None, unit_price: 110.0000000000  row: 0x10e53e750  session: 0x10e4ce690  ins_upd_dlt: ins, initial: ins - 2026-11-19 19:46:01,848 - logic_logger - INFO
..Item[None] {Formula amount} id: None, order_id: None, product_id: None, quantity: 1, amount: 110.0000000000, unit_price: 110.0000000000  row: 0x10e53e750  session: 0x10e4ce690  ins_upd_dlt: ins, initial: ins - 2026-11-19 19:46:01,848 - logic_logger - INFO
....Order[None] {Update - Adjusting order: amount_total} id: None, notes: behave test, customer_id: 46, CreatedOn: 2026-11-19, date_shipped: None, amount_total:  [0-->] 110.0000000000, CreatedOnDay: 2026-11-19  row: 0x10e777530  session: 0x10e4ce690  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:01,849 - logic_logger - INFO
......DailyFlow[2026-11-19] {Update - Adjusting daily_flow: order_amount} day: 2026-11-19, order_count: 34, order_amount:  [10210.00-->] 10320.0000000000, message_received: 8, message_processed: 4, message_rejected: 3, message_pending: 1, request_received: 39, request_processed: 31, request_rejected: 7, request_pending: 1  row: 0x10e237c20  session: 0x10e4ce690  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:01,849 - logic_logger - INFO
......DailyFlow[2026-11-19] {Prune Formula: message_pending [['message_received', 'message_processed', 'message_rejected']]} day: 2026-11-19, order_count: 34, order_amount:  [10210.00-->] 10320.0000000000, message_received: 8, message_processed: 4, message_rejected: 3, message_pending: 1, request_received: 39, request_processed: 31, request_rejected: 7, request_pending: 1  row: 0x10e237c20  session: 0x10e4ce690  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:01,849 - logic_logger - INFO
......DailyFlow[2026-11-19] {Prune Formula: request_pending [['request_received', 'request_processed', 'request_rejected']]} day: 2026-11-19, order_count: 34, order_amount:  [10210.00-->] 10320.0000000000, message_received: 8, message_processed: 4, message_rejected: 3, message_pending: 1, request_received: 39, request_processed: 31, request_rejected: 7, request_pending: 1  row: 0x10e237c20  session: 0x10e4ce690  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:01,849 - logic_logger - INFO
......Customer[46] {Update - Adjusting customer: balance} id: 46, name: Tara 1795146361828, balance:  [330.0000000000-->] 440.0000000000, credit_limit: 5000.0000000000, email: None, email_opt_out: None  row: 0x10e7a64d0  session: 0x10e4ce690  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:01,849 - logic_logger - INFO
Logic Phase:		COMMIT LOGIC		(session=0x10e4ce690)   										 - 2026-11-19 19:46:01,849 - logic_logger - INFO
Logic Phase:		AFTER_FLUSH LOGIC	(session=0x10e4ce690)   										 - 2026-11-19 19:46:01,849 - logic_logger - INFO
..Order[222] {AfterFlush Event} id: 222, notes: behave test, customer_id: 46, CreatedOn: 2026-11-19, date_shipped: None, amount_total: 110.0000000000, CreatedOnDay: 2026-11-19  row: 0x10e777530  session: 0x10e4ce690  ins_upd_dlt: ins, initial: ins - 2026-11-19 19:46:01,850 - logic_logger - INFO


Logic Phase:		ROW LOGIC		(session=0x10e4ce8b0) (sqlalchemy before_flush)			 - 2026-11-19 19:46:01,855 - logic_logger - INFO
..Item[328] {Update - client} id: 328, order_id:  [221-->] 222, product_id: 2, quantity: 2, amount: 180.0000000000, unit_price: 90.0000000000  row: 0x10e783350  session: 0x10e4ce8b0  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:01,855 - logic_logger - INFO
..Item[328] {Prune Formula: amount [['quantity', 'unit_price']]} id: 328, order_id:  [221-->] 222, product_id: 2, quantity: 2, amount: 180.0000000000, unit_price: 90.0000000000  row: 0x10e783350  session: 0x10e4ce8b0  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:01,855 - logic_logger - INFO
....Order[222] {Update - Adjusting order: amount_total, amount_total} id: 222, notes: behave test, customer_id: 46, CreatedOn: 2026-11-19, date_shipped: None, amount_total:  [110.0000000000-->] 290.0000000000, CreatedOnDay: 2026-11-19  row: 0x10e7776e0  session: 0x10e4ce8b0  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:01,856 - logic_logger - INFO
......DailyFlow[2026-11-19] {Update - Adjusting daily_flow: order_amount} day: 2026-11-19, order_count: 34, order_amount:  [10320.00-->] 10500.0000000000, message_received: 8, message_processed: 4, message_rejected: 3, message_pending: 1, request_received: 39, request_processed: 31, request_rejected: 7, request_pending: 1  row: 0x10e236780  session: 0x10e4ce8b0  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:01,856 - logic_logger - INFO
......DailyFlow[2026-11-19] {Prune Formula: message_pending [['message_received', 'message_processed', 'message_rejected']]} day: 2026-11-19, order_count: 34, order_amount:  [10320.00-->] 10500.0000000000, message_received: 8, message_processed: 4, message_rejected: 3, message_pending: 1, request_received: 39, request_processed: 31, request_rejected: 7, request_pending: 1  row: 0x10e236780  session: 0x10e4ce8b0  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:01,856 - logic_logger - INFO
......DailyFlow[2026-11-19] {Prune Formula: request_pending [['request_received', 'request_processed', 'request_rejected']]} day: 2026-11-19, order_count: 34, order_amount:  [10320.00-->] 10500.0000000000, message_received: 8, message_processed: 4, message_rejected: 3, message_pending: 1, request_received: 39, request_processed: 31, request_rejected: 7, request_pending: 1  row: 0x10e236780  session: 0x10e4ce8b0  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:01,856 - logic_logger - INFO
......Customer[46] {Update - Adjusting customer: balance} id: 46, name: Tara 1795146361828, balance:  [440.0000000000-->] 620.0000000000, credit_limit: 5000.0000000000, email: None, email_opt_out: None  row: 0x10e7a54d0  session: 0x10e4ce8b0  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:01,857 - logic_logger - INFO
....Order[221] {Update - Adjusting Old order} id: 221, notes: behave test, customer_id: 46, CreatedOn: 2026-11-19, date_shipped: None, amount_total:  [330.0000000000-->] 150.0000000000, CreatedOnDay: 2026-11-19  row: 0x10e7770b0  session: 0x10e4ce8b0  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:01,857 - logic_logger - INFO
......DailyFlow[2026-11-19] {Update - Adjusting daily_flow: order_amount} day: 2026-11-19, order_count: 34, order_amount:  [10500.0000000000-->] 10320.0000000000, message_received: 8, message_processed: 4, message_rejected: 3, message_pending: 1, request_received: 39, request_processed: 31, request_rejected: 7, request_pending: 1  row: 0x10e236780  session: 0x10e4ce8b0  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:01,857 - logic_logger - INFO
......DailyFlow[2026-11-19] {Prune Formula: message_pending [['message_received', 'message_processed', 'message_rejected']]} day: 2026-11-19, order_count: 34, order_amount:  [10500.0000000000-->] 10320.0000000000, message_received: 8, message_processed: 4, message_rejected: 3, message_pending: 1, request_received: 39, request_processed: 31, request_rejected: 7, request_pending: 1  row: 0x10e236780  session: 0x10e4ce8b0  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:01,857 - logic_logger - INFO
......DailyFlow[2026-11-19] {Prune Formula: request_pending [['request_received', 'request_processed', 'request_rejected']]} day: 2026-11-19, order_count: 34, order_amount:  [10500.0000000000-->] 10320.0000000000, message_received: 8, message_processed: 4, message_rejected: 3, message_pending: 1, request_received: 39, request_processed: 31, request_rejected: 7, request_pending: 1  row: 0x10e236780  session: 0x10e4ce8b0  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:01,857 - logic_logger - INFO
......Customer[46] {Update - Adjusting customer: balance} id: 46, name: Tara 1795146361828, balance:  [620.0000000000-->] 440.0000000000, credit_limit: 5000.0000000000, email: None, email_opt_out: None  row: 0x10e7a54d0  session: 0x10e4ce8b0  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:01,857 - logic_logger - INFO
Logic Phase:		COMMIT LOGIC		(session=0x10e4ce8b0)   										 - 2026-11-19 19:46:01,857 - logic_logger - INFO
Logic Phase:		AFTER_FLUSH LOGIC	(session=0x10e4ce8b0)   										 - 2026-11-19 19:46:01,858 - logic_logger - INFO
....Order[222] {AfterFlush Event} id: 222, notes: behave test, customer_id: 46, CreatedOn: 2026-11-19, date_shipped: None, amount_total:  [110.0000000000-->] 290.0000000000, CreatedOnDay: 2026-11-19  row: 0x10e7776e0  session: 0x10e4ce8b0  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:01,858 - logic_logger - INFO
....Order[221] {AfterFlush Event} id: 221, notes: behave test, customer_id: 46, CreatedOn: 2026-11-19, date_shipped: None, amount_total:  [330.0000000000-->] 150.0000000000, CreatedOnDay: 2026-11-19  row: 0x10e7770b0  session: 0x10e4ce8b0  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:01,858 - logic_logger - INFO

```
</details>

&nbsp;
&nbsp;

#### Scenario: Moving an order to another customer adjusts both balances ✅ (0.03 s)
&emsp;  Scenario: Moving an order to another customer adjusts both balances  
&emsp;&emsp;    Given a new customer "Uma" with credit limit 2000  
&emsp;&emsp;    And a new customer "Vic" with credit limit 2000  
&emsp;&emsp;    And a B2B order is placed for "Uma" with 2 Widget and 1 Gadget  
&emsp;&emsp;    When the order is moved to customer "Vic"  
&emsp;&emsp;    Then the balance of "Uma" is 0  
&emsp;&emsp;    And the balance of "Vic" is 330  

<details markdown>
<summary>Rules exercised and logic log (3 transactions)</summary>


&nbsp;
&nbsp;


**Rules Used** in Scenario: Moving an order to another customer adjusts both balances
```
  DailyFlow  
    1. Derive DailyFlow.request_rejected as Count(OrderB2bRequest Where Rule.count(derive=models.DailyFlow.request_rejected, as_count_of=models.OrderB2bRequest, where=lambda row: row.error_text is not None, insert_parent=True), insert_parent)  
    2. Derive DailyFlow.request_pending as Formula (2): Rule.formula(derive=models.DailyFlow.request_pend [...]  
    3. Derive DailyFlow.request_processed as Count(OrderB2bRequest Where Rule.count(derive=models.DailyFlow.request_processed, as_count_of=models.OrderB2bRequest, where=lambda row: row.is_processed == True, insert_parent=True), insert_parent)  
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
**Logic Log** in Scenario: Moving an order to another customer adjusts both balances (3 transactions)
```
Logic Phase:		ROW LOGIC		(session=0x10f2fc490) (sqlalchemy before_flush)			 - 2026-11-19 19:46:06,984 - logic_logger - INFO
..OrderB2bRequest[None] {Insert - client} id: None, CreatedOn: None, CreatedOnDay: None, payload: {"Account": "Flow Move 1795146366980", "Notes": "behave test", "Items": [{"Name": "Gadget", "QuantityOrdered": 1}]}, is_processed: False, error_text: None  row: 0x10f2c9dd0  session: 0x10f2fc490  ins_upd_dlt: ins, initial: ins - 2026-11-19 19:46:06,985 - logic_logger - INFO
..OrderB2bRequest[None] {early_row_event_all_classes - handle_all did stamping} id: None, CreatedOn: 2026-11-19 19:46:06.985060, CreatedOnDay: 2026-11-19, payload: {"Account": "Flow Move 1795146366980", "Notes": "behave test", "Items": [{"Name": "Gadget", "QuantityOrdered": 1}]}, is_processed: False, error_text: None  row: 0x10f2c9dd0  session: 0x10f2fc490  ins_upd_dlt: ins, initial: ins - 2026-11-19 19:46:06,985 - logic_logger - INFO
....DailyFlow[2026-11-19] {Update - Adjusting daily_flow: request_received} day: 2026-11-19, order_count: 45, order_amount: 13710.00, message_received: 11, message_processed: 5, message_rejected: 5, message_pending: 1, request_received:  [52-->] 53, request_processed: 43, request_rejected: 8, request_pending: 1  row: 0x10e861650  session: 0x10f2fc490  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:06,985 - logic_logger - INFO
....DailyFlow[2026-11-19] {Prune Formula: message_pending [['message_received', 'message_processed', 'message_rejected']]} day: 2026-11-19, order_count: 45, order_amount: 13710.00, message_received: 11, message_processed: 5, message_rejected: 5, message_pending: 1, request_received:  [52-->] 53, request_processed: 43, request_rejected: 8, request_pending: 1  row: 0x10e861650  session: 0x10f2fc490  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:06,985 - logic_logger - INFO
....DailyFlow[2026-11-19] {Formula request_pending} day: 2026-11-19, order_count: 45, order_amount: 13710.00, message_received: 11, message_processed: 5, message_rejected: 5, message_pending: 1, request_received:  [52-->] 53, request_processed: 43, request_rejected: 8, request_pending:  [1-->] 2  row: 0x10e861650  session: 0x10f2fc490  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:06,985 - logic_logger - INFO
Logic Phase:		COMMIT LOGIC		(session=0x10f2fc490)   										 - 2026-11-19 19:46:06,985 - logic_logger - INFO
Logic Phase:		AFTER_FLUSH LOGIC	(session=0x10f2fc490)   										 - 2026-11-19 19:46:06,985 - logic_logger - INFO


Logic Phase:		ROW LOGIC		(session=0x10f2fc490) (sqlalchemy before_flush)			 - 2026-11-19 19:46:06,987 - logic_logger - INFO
..Product[1] {Update - client} id: 1, name: Gadget, count_suppliers: 0, unit_price: 150.0000000000  row: 0x10f35c6e0  session: 0x10f2fc490  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:06,987 - logic_logger - INFO
..OrderB2bRequest[159] {Update - client} id: 159, CreatedOn: 2026-11-19 19:46:06.985060, CreatedOnDay: 2026-11-19, payload: {"Account": "Flow Move 1795146366980", "Notes": "behave test", "Items": [{"Name": "Gadget", "QuantityOrdered": 1}]}, is_processed:  [False-->] True, error_text: None  row: 0x10f2c9dd0  session: 0x10f2fc490  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:06,987 - logic_logger - INFO
....DailyFlow[2026-11-19] {Update - Adjusting daily_flow: request_processed} day: 2026-11-19, order_count: 45, order_amount: 13710.00, message_received: 11, message_processed: 5, message_rejected: 5, message_pending: 1, request_received: 53, request_processed:  [43-->] 44, request_rejected: 8, request_pending: 2  row: 0x10e861650  session: 0x10f2fc490  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:06,988 - logic_logger - INFO
....DailyFlow[2026-11-19] {Prune Formula: message_pending [['message_received', 'message_processed', 'message_rejected']]} day: 2026-11-19, order_count: 45, order_amount: 13710.00, message_received: 11, message_processed: 5, message_rejected: 5, message_pending: 1, request_received: 53, request_processed:  [43-->] 44, request_rejected: 8, request_pending: 2  row: 0x10e861650  session: 0x10f2fc490  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:06,988 - logic_logger - INFO
....DailyFlow[2026-11-19] {Formula request_pending} day: 2026-11-19, order_count: 45, order_amount: 13710.00, message_received: 11, message_processed: 5, message_rejected: 5, message_pending: 1, request_received: 53, request_processed:  [43-->] 44, request_rejected: 8, request_pending:  [2-->] 1  row: 0x10e861650  session: 0x10f2fc490  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:06,988 - logic_logger - INFO
..Order[None] {Insert - client} id: None, notes: behave test, customer_id: 64, CreatedOn: None, date_shipped: None, amount_total: None, CreatedOnDay: None  row: 0x10f2da720  session: 0x10f2fc490  ins_upd_dlt: ins, initial: ins - 2026-11-19 19:46:06,988 - logic_logger - INFO
..Order[None] {early_row_event_all_classes - handle_all did stamping} id: None, notes: behave test, customer_id: 64, CreatedOn: 2026-11-19, date_shipped: None, amount_total: None, CreatedOnDay: 2026-11-19  row: 0x10f2da720  session: 0x10f2fc490  ins_upd_dlt: ins, initial: ins - 2026-11-19 19:46:06,988 - logic_logger - INFO
..Order[None] {server aggregate_defaults: amount_total } id: None, notes: behave test, customer_id: 64, CreatedOn: 2026-11-19, date_shipped: None, amount_total: 0, CreatedOnDay: 2026-11-19  row: 0x10f2da720  session: 0x10f2fc490  ins_upd_dlt: ins, initial: ins - 2026-11-19 19:46:06,988 - logic_logger - INFO
....DailyFlow[2026-11-19] {Update - Adjusting daily_flow: order_count} day: 2026-11-19, order_count:  [45-->] 46, order_amount: 13710.00, message_received: 11, message_processed: 5, message_rejected: 5, message_pending: 1, request_received: 53, request_processed: 44, request_rejected: 8, request_pending: 1  row: 0x10e861650  session: 0x10f2fc490  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:06,988 - logic_logger - INFO
....DailyFlow[2026-11-19] {Prune Formula: message_pending [['message_received', 'message_processed', 'message_rejected']]} day: 2026-11-19, order_count:  [45-->] 46, order_amount: 13710.00, message_received: 11, message_processed: 5, message_rejected: 5, message_pending: 1, request_received: 53, request_processed: 44, request_rejected: 8, request_pending: 1  row: 0x10e861650  session: 0x10f2fc490  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:06,988 - logic_logger - INFO
....DailyFlow[2026-11-19] {Prune Formula: request_pending [['request_received', 'request_processed', 'request_rejected']]} day: 2026-11-19, order_count:  [45-->] 46, order_amount: 13710.00, message_received: 11, message_processed: 5, message_rejected: 5, message_pending: 1, request_received: 53, request_processed: 44, request_rejected: 8, request_pending: 1  row: 0x10e861650  session: 0x10f2fc490  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:06,988 - logic_logger - INFO
..Item[None] {Insert - client} id: None, order_id: None, product_id: None, quantity: 1, amount: None, unit_price: None  row: 0x10f2c81d0  session: 0x10f2fc490  ins_upd_dlt: ins, initial: ins - 2026-11-19 19:46:06,988 - logic_logger - INFO
..Item[None] {copy_rules for role: product - unit_price} id: None, order_id: None, product_id: None, quantity: 1, amount: None, unit_price: 150.0000000000  row: 0x10f2c81d0  session: 0x10f2fc490  ins_upd_dlt: ins, initial: ins - 2026-11-19 19:46:06,988 - logic_logger - INFO
..Item[None] {Formula amount} id: None, order_id: None, product_id: None, quantity: 1, amount: 150.0000000000, unit_price: 150.0000000000  row: 0x10f2c81d0  session: 0x10f2fc490  ins_upd_dlt: ins, initial: ins - 2026-11-19 19:46:06,988 - logic_logger - INFO
....Order[None] {Update - Adjusting order: amount_total} id: None, notes: behave test, customer_id: 64, CreatedOn: 2026-11-19, date_shipped: None, amount_total:  [0-->] 150.0000000000, CreatedOnDay: 2026-11-19  row: 0x10f2da720  session: 0x10f2fc490  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:06,988 - logic_logger - INFO
......DailyFlow[2026-11-19] {Update - Adjusting daily_flow: order_amount} day: 2026-11-19, order_count: 46, order_amount:  [13710.00-->] 13860.0000000000, message_received: 11, message_processed: 5, message_rejected: 5, message_pending: 1, request_received: 53, request_processed: 44, request_rejected: 8, request_pending: 1  row: 0x10e861650  session: 0x10f2fc490  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:06,988 - logic_logger - INFO
......DailyFlow[2026-11-19] {Prune Formula: message_pending [['message_received', 'message_processed', 'message_rejected']]} day: 2026-11-19, order_count: 46, order_amount:  [13710.00-->] 13860.0000000000, message_received: 11, message_processed: 5, message_rejected: 5, message_pending: 1, request_received: 53, request_processed: 44, request_rejected: 8, request_pending: 1  row: 0x10e861650  session: 0x10f2fc490  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:06,988 - logic_logger - INFO
......DailyFlow[2026-11-19] {Prune Formula: request_pending [['request_received', 'request_processed', 'request_rejected']]} day: 2026-11-19, order_count: 46, order_amount:  [13710.00-->] 13860.0000000000, message_received: 11, message_processed: 5, message_rejected: 5, message_pending: 1, request_received: 53, request_processed: 44, request_rejected: 8, request_pending: 1  row: 0x10e861650  session: 0x10f2fc490  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:06,989 - logic_logger - INFO
......Customer[64] {Update - Adjusting customer: balance} id: 64, name: Flow Move 1795146366980, balance:  [0E-10-->] 150.0000000000, credit_limit: 5000.0000000000, email: None, email_opt_out: None  row: 0x10f2b8850  session: 0x10f2fc490  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:06,989 - logic_logger - INFO
Logic Phase:		COMMIT LOGIC		(session=0x10f2fc490)   										 - 2026-11-19 19:46:06,989 - logic_logger - INFO
Logic Phase:		AFTER_FLUSH LOGIC	(session=0x10f2fc490)   										 - 2026-11-19 19:46:06,990 - logic_logger - INFO
..Order[236] {AfterFlush Event} id: 236, notes: behave test, customer_id: 64, CreatedOn: 2026-11-19, date_shipped: None, amount_total: 150.0000000000, CreatedOnDay: 2026-11-19  row: 0x10f2da720  session: 0x10f2fc490  ins_upd_dlt: ins, initial: ins - 2026-11-19 19:46:06,990 - logic_logger - INFO


Logic Phase:		ROW LOGIC		(session=0x10e4ce250) (sqlalchemy before_flush)			 - 2026-11-19 19:46:06,996 - logic_logger - INFO
..Order[236] {Update - client} id: 236, notes: behave test, customer_id: 64, CreatedOn: 2026-11-19, date_shipped: None, amount_total: 150.0000000000, CreatedOnDay:  [2026-11-19-->] 2000-01-01  row: 0x10f2db6e0  session: 0x10e4ce250  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:06,996 - logic_logger - INFO
....DailyFlow[2000-01-01] {Update - Adjusting daily_flow: order_count, order_count, order_amount, order_amount} day: 2000-01-01, order_count:  [1-->] 2, order_amount:  [150.00-->] 300.0000000000, message_received: 0, message_processed: 0, message_rejected: 0, message_pending: 0, request_received: 0, request_processed: 0, request_rejected: 0, request_pending: 0  row: 0x10e861910  session: 0x10e4ce250  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:06,996 - logic_logger - INFO
....DailyFlow[2000-01-01] {Prune Formula: message_pending [['message_received', 'message_processed', 'message_rejected']]} day: 2000-01-01, order_count:  [1-->] 2, order_amount:  [150.00-->] 300.0000000000, message_received: 0, message_processed: 0, message_rejected: 0, message_pending: 0, request_received: 0, request_processed: 0, request_rejected: 0, request_pending: 0  row: 0x10e861910  session: 0x10e4ce250  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:06,996 - logic_logger - INFO
....DailyFlow[2000-01-01] {Prune Formula: request_pending [['request_received', 'request_processed', 'request_rejected']]} day: 2000-01-01, order_count:  [1-->] 2, order_amount:  [150.00-->] 300.0000000000, message_received: 0, message_processed: 0, message_rejected: 0, message_pending: 0, request_received: 0, request_processed: 0, request_rejected: 0, request_pending: 0  row: 0x10e861910  session: 0x10e4ce250  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:06,996 - logic_logger - INFO
....DailyFlow[2026-11-19] {Update - Adjusting Old daily_flow} day: 2026-11-19, order_count:  [46-->] 45, order_amount:  [13860.00-->] 13710.0000000000, message_received: 11, message_processed: 5, message_rejected: 5, message_pending: 1, request_received: 53, request_processed: 44, request_rejected: 8, request_pending: 1  row: 0x10e8617b0  session: 0x10e4ce250  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:06,996 - logic_logger - INFO
....DailyFlow[2026-11-19] {Prune Formula: message_pending [['message_received', 'message_processed', 'message_rejected']]} day: 2026-11-19, order_count:  [46-->] 45, order_amount:  [13860.00-->] 13710.0000000000, message_received: 11, message_processed: 5, message_rejected: 5, message_pending: 1, request_received: 53, request_processed: 44, request_rejected: 8, request_pending: 1  row: 0x10e8617b0  session: 0x10e4ce250  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:06,996 - logic_logger - INFO
....DailyFlow[2026-11-19] {Prune Formula: request_pending [['request_received', 'request_processed', 'request_rejected']]} day: 2026-11-19, order_count:  [46-->] 45, order_amount:  [13860.00-->] 13710.0000000000, message_received: 11, message_processed: 5, message_rejected: 5, message_pending: 1, request_received: 53, request_processed: 44, request_rejected: 8, request_pending: 1  row: 0x10e8617b0  session: 0x10e4ce250  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:06,996 - logic_logger - INFO
Logic Phase:		COMMIT LOGIC		(session=0x10e4ce250)   										 - 2026-11-19 19:46:06,996 - logic_logger - INFO
Logic Phase:		AFTER_FLUSH LOGIC	(session=0x10e4ce250)   										 - 2026-11-19 19:46:06,997 - logic_logger - INFO
..Order[236] {AfterFlush Event} id: 236, notes: behave test, customer_id: 64, CreatedOn: 2026-11-19, date_shipped: None, amount_total: 150.0000000000, CreatedOnDay:  [2026-11-19-->] 2000-01-01  row: 0x10f2db6e0  session: 0x10e4ce250  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:06,997 - logic_logger - INFO

```
</details>

&nbsp;
&nbsp;

#### Scenario: Deleting an order reduces the balance ✅ (0.02 s)
&emsp;  Scenario: Deleting an order reduces the balance  
&emsp;&emsp;    Given a new customer "Wen" with credit limit 2000  
&emsp;&emsp;    And a B2B order is placed for "Wen" with 1 Gadget  
&emsp;&emsp;    When the order is deleted  
&emsp;&emsp;    Then the balance of "Wen" is 0  

<details markdown>
<summary>Rules exercised and logic log (3 transactions)</summary>


&nbsp;
&nbsp;


**Rules Used** in Scenario: Deleting an order reduces the balance
```
  DailyFlow  
    1. Derive DailyFlow.request_rejected as Count(OrderB2bRequest Where Rule.count(derive=models.DailyFlow.request_rejected, as_count_of=models.OrderB2bRequest, where=lambda row: row.error_text is not None, insert_parent=True), insert_parent)  
    2. Derive DailyFlow.request_pending as Formula (2): Rule.formula(derive=models.DailyFlow.request_pend [...]  
    3. Derive DailyFlow.request_processed as Count(OrderB2bRequest Where Rule.count(derive=models.DailyFlow.request_processed, as_count_of=models.OrderB2bRequest, where=lambda row: row.is_processed == True, insert_parent=True), insert_parent)  
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
**Logic Log** in Scenario: Deleting an order reduces the balance (3 transactions)
```
Logic Phase:		ROW LOGIC		(session=0x10e4cef10) (sqlalchemy before_flush)			 - 2026-11-19 19:46:01,901 - logic_logger - INFO
..OrderB2bRequest[None] {Insert - client} id: None, CreatedOn: None, CreatedOnDay: None, payload: {"Account": "Wen 1795146361898", "Notes": "behave test", "Items": [{"Name": "Gadget", "QuantityOrdered": 1}]}, is_processed: False, error_text: None  row: 0x10e3ee9d0  session: 0x10e4cef10  ins_upd_dlt: ins, initial: ins - 2026-11-19 19:46:01,902 - logic_logger - INFO
..OrderB2bRequest[None] {early_row_event_all_classes - handle_all did stamping} id: None, CreatedOn: 2026-11-19 19:46:01.902079, CreatedOnDay: 2026-11-19, payload: {"Account": "Wen 1795146361898", "Notes": "behave test", "Items": [{"Name": "Gadget", "QuantityOrdered": 1}]}, is_processed: False, error_text: None  row: 0x10e3ee9d0  session: 0x10e4cef10  ins_upd_dlt: ins, initial: ins - 2026-11-19 19:46:01,902 - logic_logger - INFO
....DailyFlow[2026-11-19] {Update - Adjusting daily_flow: request_received} day: 2026-11-19, order_count: 35, order_amount: 10650.00, message_received: 8, message_processed: 4, message_rejected: 3, message_pending: 1, request_received:  [40-->] 41, request_processed: 32, request_rejected: 7, request_pending: 1  row: 0x10e237d80  session: 0x10e4cef10  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:01,902 - logic_logger - INFO
....DailyFlow[2026-11-19] {Prune Formula: message_pending [['message_received', 'message_processed', 'message_rejected']]} day: 2026-11-19, order_count: 35, order_amount: 10650.00, message_received: 8, message_processed: 4, message_rejected: 3, message_pending: 1, request_received:  [40-->] 41, request_processed: 32, request_rejected: 7, request_pending: 1  row: 0x10e237d80  session: 0x10e4cef10  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:01,902 - logic_logger - INFO
....DailyFlow[2026-11-19] {Formula request_pending} day: 2026-11-19, order_count: 35, order_amount: 10650.00, message_received: 8, message_processed: 4, message_rejected: 3, message_pending: 1, request_received:  [40-->] 41, request_processed: 32, request_rejected: 7, request_pending:  [1-->] 2  row: 0x10e237d80  session: 0x10e4cef10  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:01,902 - logic_logger - INFO
Logic Phase:		COMMIT LOGIC		(session=0x10e4cef10)   										 - 2026-11-19 19:46:01,902 - logic_logger - INFO
Logic Phase:		AFTER_FLUSH LOGIC	(session=0x10e4cef10)   										 - 2026-11-19 19:46:01,902 - logic_logger - INFO


Logic Phase:		ROW LOGIC		(session=0x10e4cef10) (sqlalchemy before_flush)			 - 2026-11-19 19:46:01,906 - logic_logger - INFO
..Product[1] {Update - client} id: 1, name: Gadget, count_suppliers: 0, unit_price: 150.0000000000  row: 0x10e78bb60  session: 0x10e4cef10  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:01,906 - logic_logger - INFO
..OrderB2bRequest[147] {Update - client} id: 147, CreatedOn: 2026-11-19 19:46:01.902079, CreatedOnDay: 2026-11-19, payload: {"Account": "Wen 1795146361898", "Notes": "behave test", "Items": [{"Name": "Gadget", "QuantityOrdered": 1}]}, is_processed:  [False-->] True, error_text: None  row: 0x10e3ee9d0  session: 0x10e4cef10  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:01,906 - logic_logger - INFO
....DailyFlow[2026-11-19] {Update - Adjusting daily_flow: request_processed} day: 2026-11-19, order_count: 35, order_amount: 10650.00, message_received: 8, message_processed: 4, message_rejected: 3, message_pending: 1, request_received: 41, request_processed:  [32-->] 33, request_rejected: 7, request_pending: 2  row: 0x10e237d80  session: 0x10e4cef10  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:01,906 - logic_logger - INFO
....DailyFlow[2026-11-19] {Prune Formula: message_pending [['message_received', 'message_processed', 'message_rejected']]} day: 2026-11-19, order_count: 35, order_amount: 10650.00, message_received: 8, message_processed: 4, message_rejected: 3, message_pending: 1, request_received: 41, request_processed:  [32-->] 33, request_rejected: 7, request_pending: 2  row: 0x10e237d80  session: 0x10e4cef10  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:01,906 - logic_logger - INFO
....DailyFlow[2026-11-19] {Formula request_pending} day: 2026-11-19, order_count: 35, order_amount: 10650.00, message_received: 8, message_processed: 4, message_rejected: 3, message_pending: 1, request_received: 41, request_processed:  [32-->] 33, request_rejected: 7, request_pending:  [2-->] 1  row: 0x10e237d80  session: 0x10e4cef10  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:01,906 - logic_logger - INFO
..Order[None] {Insert - client} id: None, notes: behave test, customer_id: 49, CreatedOn: None, date_shipped: None, amount_total: None, CreatedOnDay: None  row: 0x10e777da0  session: 0x10e4cef10  ins_upd_dlt: ins, initial: ins - 2026-11-19 19:46:01,906 - logic_logger - INFO
..Order[None] {early_row_event_all_classes - handle_all did stamping} id: None, notes: behave test, customer_id: 49, CreatedOn: 2026-11-19, date_shipped: None, amount_total: None, CreatedOnDay: 2026-11-19  row: 0x10e777da0  session: 0x10e4cef10  ins_upd_dlt: ins, initial: ins - 2026-11-19 19:46:01,906 - logic_logger - INFO
..Order[None] {server aggregate_defaults: amount_total } id: None, notes: behave test, customer_id: 49, CreatedOn: 2026-11-19, date_shipped: None, amount_total: 0, CreatedOnDay: 2026-11-19  row: 0x10e777da0  session: 0x10e4cef10  ins_upd_dlt: ins, initial: ins - 2026-11-19 19:46:01,906 - logic_logger - INFO
....DailyFlow[2026-11-19] {Update - Adjusting daily_flow: order_count} day: 2026-11-19, order_count:  [35-->] 36, order_amount: 10650.00, message_received: 8, message_processed: 4, message_rejected: 3, message_pending: 1, request_received: 41, request_processed: 33, request_rejected: 7, request_pending: 1  row: 0x10e237d80  session: 0x10e4cef10  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:01,906 - logic_logger - INFO
....DailyFlow[2026-11-19] {Prune Formula: message_pending [['message_received', 'message_processed', 'message_rejected']]} day: 2026-11-19, order_count:  [35-->] 36, order_amount: 10650.00, message_received: 8, message_processed: 4, message_rejected: 3, message_pending: 1, request_received: 41, request_processed: 33, request_rejected: 7, request_pending: 1  row: 0x10e237d80  session: 0x10e4cef10  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:01,906 - logic_logger - INFO
....DailyFlow[2026-11-19] {Prune Formula: request_pending [['request_received', 'request_processed', 'request_rejected']]} day: 2026-11-19, order_count:  [35-->] 36, order_amount: 10650.00, message_received: 8, message_processed: 4, message_rejected: 3, message_pending: 1, request_received: 41, request_processed: 33, request_rejected: 7, request_pending: 1  row: 0x10e237d80  session: 0x10e4cef10  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:01,906 - logic_logger - INFO
..Item[None] {Insert - client} id: None, order_id: None, product_id: None, quantity: 1, amount: None, unit_price: None  row: 0x10e7a5f50  session: 0x10e4cef10  ins_upd_dlt: ins, initial: ins - 2026-11-19 19:46:01,906 - logic_logger - INFO
..Item[None] {copy_rules for role: product - unit_price} id: None, order_id: None, product_id: None, quantity: 1, amount: None, unit_price: 150.0000000000  row: 0x10e7a5f50  session: 0x10e4cef10  ins_upd_dlt: ins, initial: ins - 2026-11-19 19:46:01,907 - logic_logger - INFO
..Item[None] {Formula amount} id: None, order_id: None, product_id: None, quantity: 1, amount: 150.0000000000, unit_price: 150.0000000000  row: 0x10e7a5f50  session: 0x10e4cef10  ins_upd_dlt: ins, initial: ins - 2026-11-19 19:46:01,907 - logic_logger - INFO
....Order[None] {Update - Adjusting order: amount_total} id: None, notes: behave test, customer_id: 49, CreatedOn: 2026-11-19, date_shipped: None, amount_total:  [0-->] 150.0000000000, CreatedOnDay: 2026-11-19  row: 0x10e777da0  session: 0x10e4cef10  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:01,907 - logic_logger - INFO
......DailyFlow[2026-11-19] {Update - Adjusting daily_flow: order_amount} day: 2026-11-19, order_count: 36, order_amount:  [10650.00-->] 10800.0000000000, message_received: 8, message_processed: 4, message_rejected: 3, message_pending: 1, request_received: 41, request_processed: 33, request_rejected: 7, request_pending: 1  row: 0x10e237d80  session: 0x10e4cef10  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:01,907 - logic_logger - INFO
......DailyFlow[2026-11-19] {Prune Formula: message_pending [['message_received', 'message_processed', 'message_rejected']]} day: 2026-11-19, order_count: 36, order_amount:  [10650.00-->] 10800.0000000000, message_received: 8, message_processed: 4, message_rejected: 3, message_pending: 1, request_received: 41, request_processed: 33, request_rejected: 7, request_pending: 1  row: 0x10e237d80  session: 0x10e4cef10  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:01,907 - logic_logger - INFO
......DailyFlow[2026-11-19] {Prune Formula: request_pending [['request_received', 'request_processed', 'request_rejected']]} day: 2026-11-19, order_count: 36, order_amount:  [10650.00-->] 10800.0000000000, message_received: 8, message_processed: 4, message_rejected: 3, message_pending: 1, request_received: 41, request_processed: 33, request_rejected: 7, request_pending: 1  row: 0x10e237d80  session: 0x10e4cef10  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:01,907 - logic_logger - INFO
......Customer[49] {Update - Adjusting customer: balance} id: 49, name: Wen 1795146361898, balance:  [0E-10-->] 150.0000000000, credit_limit: 2000.0000000000, email: None, email_opt_out: None  row: 0x10e7a5950  session: 0x10e4cef10  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:01,907 - logic_logger - INFO
Logic Phase:		COMMIT LOGIC		(session=0x10e4cef10)   										 - 2026-11-19 19:46:01,907 - logic_logger - INFO
Logic Phase:		AFTER_FLUSH LOGIC	(session=0x10e4cef10)   										 - 2026-11-19 19:46:01,907 - logic_logger - INFO
..Order[224] {AfterFlush Event} id: 224, notes: behave test, customer_id: 49, CreatedOn: 2026-11-19, date_shipped: None, amount_total: 150.0000000000, CreatedOnDay: 2026-11-19  row: 0x10e777da0  session: 0x10e4cef10  ins_upd_dlt: ins, initial: ins - 2026-11-19 19:46:01,908 - logic_logger - INFO


Logic Phase:		ROW LOGIC		(session=0x10e433df0) (sqlalchemy before_flush)			 - 2026-11-19 19:46:01,910 - logic_logger - INFO
..Order[224] {Delete - client} id: 224, notes: behave test, customer_id: 49, CreatedOn: 2026-11-19, date_shipped: None, amount_total: 150.0000000000, CreatedOnDay: 2026-11-19  row: 0x10e47bc80  session: 0x10e433df0  ins_upd_dlt: dlt, initial: dlt - 2026-11-19 19:46:01,910 - logic_logger - INFO
....DailyFlow[2026-11-19] {Update - Adjusting daily_flow: order_count, order_amount} day: 2026-11-19, order_count:  [36-->] 35, order_amount:  [10800.00-->] 10650.0000000000, message_received: 8, message_processed: 4, message_rejected: 3, message_pending: 1, request_received: 41, request_processed: 33, request_rejected: 7, request_pending: 1  row: 0x10e237c20  session: 0x10e433df0  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:01,910 - logic_logger - INFO
....DailyFlow[2026-11-19] {Prune Formula: message_pending [['message_received', 'message_processed', 'message_rejected']]} day: 2026-11-19, order_count:  [36-->] 35, order_amount:  [10800.00-->] 10650.0000000000, message_received: 8, message_processed: 4, message_rejected: 3, message_pending: 1, request_received: 41, request_processed: 33, request_rejected: 7, request_pending: 1  row: 0x10e237c20  session: 0x10e433df0  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:01,910 - logic_logger - INFO
....DailyFlow[2026-11-19] {Prune Formula: request_pending [['request_received', 'request_processed', 'request_rejected']]} day: 2026-11-19, order_count:  [36-->] 35, order_amount:  [10800.00-->] 10650.0000000000, message_received: 8, message_processed: 4, message_rejected: 3, message_pending: 1, request_received: 41, request_processed: 33, request_rejected: 7, request_pending: 1  row: 0x10e237c20  session: 0x10e433df0  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:01,910 - logic_logger - INFO
....Customer[49] {Update - Adjusting customer: balance} id: 49, name: Wen 1795146361898, balance:  [150.0000000000-->] 0E-10, credit_limit: 2000.0000000000, email: None, email_opt_out: None  row: 0x10e5747d0  session: 0x10e433df0  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:01,911 - logic_logger - INFO
Logic Phase:		COMMIT LOGIC		(session=0x10e433df0)   										 - 2026-11-19 19:46:01,911 - logic_logger - INFO
Logic Phase:		AFTER_FLUSH LOGIC	(session=0x10e433df0)   										 - 2026-11-19 19:46:01,912 - logic_logger - INFO
..Order[224] {AfterFlush Event} id: 224, notes: behave test, customer_id: 49, CreatedOn: 2026-11-19, date_shipped: None, amount_total: 150.0000000000, CreatedOnDay: 2026-11-19  row: 0x10e47bc80  session: 0x10e433df0  ins_upd_dlt: dlt, initial: dlt - 2026-11-19 19:46:01,912 - logic_logger - INFO

```
</details>

&nbsp;
&nbsp;

#### Scenario: Shipping an order removes it from the balance ✅ (0.54 s)
&emsp;  Scenario: Shipping an order removes it from the balance  
&emsp;&emsp;    Given a new customer "Xia" with credit limit 2000  
&emsp;&emsp;    And a B2B order is placed for "Xia" with 2 Widget and 1 Gadget  
&emsp;&emsp;    When the order is shipped  
&emsp;&emsp;    Then the balance of "Xia" is 0  

<details markdown>
<summary>Rules exercised and logic log (3 transactions)</summary>


&nbsp;
&nbsp;


**Rules Used** in Scenario: Shipping an order removes it from the balance
```
  DailyFlow  
    1. Derive DailyFlow.request_rejected as Count(OrderB2bRequest Where Rule.count(derive=models.DailyFlow.request_rejected, as_count_of=models.OrderB2bRequest, where=lambda row: row.error_text is not None, insert_parent=True), insert_parent)  
    2. Derive DailyFlow.request_pending as Formula (2): Rule.formula(derive=models.DailyFlow.request_pend [...]  
    3. Derive DailyFlow.request_processed as Count(OrderB2bRequest Where Rule.count(derive=models.DailyFlow.request_processed, as_count_of=models.OrderB2bRequest, where=lambda row: row.is_processed == True, insert_parent=True), insert_parent)  
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
**Logic Log** in Scenario: Shipping an order removes it from the balance (3 transactions)
```
Logic Phase:		ROW LOGIC		(session=0x10e4cd480) (sqlalchemy before_flush)			 - 2026-11-19 19:46:01,922 - logic_logger - INFO
..OrderB2bRequest[None] {Insert - client} id: None, CreatedOn: None, CreatedOnDay: None, payload: {"Account": "Xia 1795146361918", "Notes": "behave test", "Items": [{"Name": "Widget", "QuantityOrdered": 2}, {"Name": "Gadget", "QuantityOrdered": 1}]}, is_processed: False, error_text: None  row: 0x10e7829d0  session: 0x10e4cd480  ins_upd_dlt: ins, initial: ins - 2026-11-19 19:46:01,922 - logic_logger - INFO
..OrderB2bRequest[None] {early_row_event_all_classes - handle_all did stamping} id: None, CreatedOn: 2026-11-19 19:46:01.922631, CreatedOnDay: 2026-11-19, payload: {"Account": "Xia 1795146361918", "Notes": "behave test", "Items": [{"Name": "Widget", "QuantityOrdered": 2}, {"Name": "Gadget", "QuantityOrdered": 1}]}, is_processed: False, error_text: None  row: 0x10e7829d0  session: 0x10e4cd480  ins_upd_dlt: ins, initial: ins - 2026-11-19 19:46:01,922 - logic_logger - INFO
....DailyFlow[2026-11-19] {Update - Adjusting daily_flow: request_received} day: 2026-11-19, order_count: 35, order_amount: 10650.00, message_received: 8, message_processed: 4, message_rejected: 3, message_pending: 1, request_received:  [41-->] 42, request_processed: 33, request_rejected: 7, request_pending: 1  row: 0x10e236780  session: 0x10e4cd480  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:01,922 - logic_logger - INFO
....DailyFlow[2026-11-19] {Prune Formula: message_pending [['message_received', 'message_processed', 'message_rejected']]} day: 2026-11-19, order_count: 35, order_amount: 10650.00, message_received: 8, message_processed: 4, message_rejected: 3, message_pending: 1, request_received:  [41-->] 42, request_processed: 33, request_rejected: 7, request_pending: 1  row: 0x10e236780  session: 0x10e4cd480  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:01,923 - logic_logger - INFO
....DailyFlow[2026-11-19] {Formula request_pending} day: 2026-11-19, order_count: 35, order_amount: 10650.00, message_received: 8, message_processed: 4, message_rejected: 3, message_pending: 1, request_received:  [41-->] 42, request_processed: 33, request_rejected: 7, request_pending:  [1-->] 2  row: 0x10e236780  session: 0x10e4cd480  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:01,923 - logic_logger - INFO
Logic Phase:		COMMIT LOGIC		(session=0x10e4cd480)   										 - 2026-11-19 19:46:01,923 - logic_logger - INFO
Logic Phase:		AFTER_FLUSH LOGIC	(session=0x10e4cd480)   										 - 2026-11-19 19:46:01,923 - logic_logger - INFO


Logic Phase:		ROW LOGIC		(session=0x10e4cd480) (sqlalchemy before_flush)			 - 2026-11-19 19:46:01,925 - logic_logger - INFO
..OrderB2bRequest[148] {Update - client} id: 148, CreatedOn: 2026-11-19 19:46:01.922631, CreatedOnDay: 2026-11-19, payload: {"Account": "Xia 1795146361918", "Notes": "behave test", "Items": [{"Name": "Widget", "QuantityOrdered": 2}, {"Name": "Gadget", "QuantityOrdered": 1}]}, is_processed:  [False-->] True, error_text: None  row: 0x10e7829d0  session: 0x10e4cd480  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:01,925 - logic_logger - INFO
....DailyFlow[2026-11-19] {Update - Adjusting daily_flow: request_processed} day: 2026-11-19, order_count: 35, order_amount: 10650.00, message_received: 8, message_processed: 4, message_rejected: 3, message_pending: 1, request_received: 42, request_processed:  [33-->] 34, request_rejected: 7, request_pending: 2  row: 0x10e236780  session: 0x10e4cd480  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:01,926 - logic_logger - INFO
....DailyFlow[2026-11-19] {Prune Formula: message_pending [['message_received', 'message_processed', 'message_rejected']]} day: 2026-11-19, order_count: 35, order_amount: 10650.00, message_received: 8, message_processed: 4, message_rejected: 3, message_pending: 1, request_received: 42, request_processed:  [33-->] 34, request_rejected: 7, request_pending: 2  row: 0x10e236780  session: 0x10e4cd480  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:01,926 - logic_logger - INFO
....DailyFlow[2026-11-19] {Formula request_pending} day: 2026-11-19, order_count: 35, order_amount: 10650.00, message_received: 8, message_processed: 4, message_rejected: 3, message_pending: 1, request_received: 42, request_processed:  [33-->] 34, request_rejected: 7, request_pending:  [2-->] 1  row: 0x10e236780  session: 0x10e4cd480  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:01,926 - logic_logger - INFO
..Product[1] {Update - client} id: 1, name: Gadget, count_suppliers: 0, unit_price: 150.0000000000  row: 0x10e4c1b70  session: 0x10e4cd480  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:01,926 - logic_logger - INFO
..Order[None] {Insert - client} id: None, notes: behave test, customer_id: 50, CreatedOn: None, date_shipped: None, amount_total: None, CreatedOnDay: None  row: 0x10e777890  session: 0x10e4cd480  ins_upd_dlt: ins, initial: ins - 2026-11-19 19:46:01,926 - logic_logger - INFO
..Order[None] {early_row_event_all_classes - handle_all did stamping} id: None, notes: behave test, customer_id: 50, CreatedOn: 2026-11-19, date_shipped: None, amount_total: None, CreatedOnDay: 2026-11-19  row: 0x10e777890  session: 0x10e4cd480  ins_upd_dlt: ins, initial: ins - 2026-11-19 19:46:01,926 - logic_logger - INFO
..Order[None] {server aggregate_defaults: amount_total } id: None, notes: behave test, customer_id: 50, CreatedOn: 2026-11-19, date_shipped: None, amount_total: 0, CreatedOnDay: 2026-11-19  row: 0x10e777890  session: 0x10e4cd480  ins_upd_dlt: ins, initial: ins - 2026-11-19 19:46:01,926 - logic_logger - INFO
....DailyFlow[2026-11-19] {Update - Adjusting daily_flow: order_count} day: 2026-11-19, order_count:  [35-->] 36, order_amount: 10650.00, message_received: 8, message_processed: 4, message_rejected: 3, message_pending: 1, request_received: 42, request_processed: 34, request_rejected: 7, request_pending: 1  row: 0x10e236780  session: 0x10e4cd480  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:01,926 - logic_logger - INFO
....DailyFlow[2026-11-19] {Prune Formula: message_pending [['message_received', 'message_processed', 'message_rejected']]} day: 2026-11-19, order_count:  [35-->] 36, order_amount: 10650.00, message_received: 8, message_processed: 4, message_rejected: 3, message_pending: 1, request_received: 42, request_processed: 34, request_rejected: 7, request_pending: 1  row: 0x10e236780  session: 0x10e4cd480  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:01,926 - logic_logger - INFO
....DailyFlow[2026-11-19] {Prune Formula: request_pending [['request_received', 'request_processed', 'request_rejected']]} day: 2026-11-19, order_count:  [35-->] 36, order_amount: 10650.00, message_received: 8, message_processed: 4, message_rejected: 3, message_pending: 1, request_received: 42, request_processed: 34, request_rejected: 7, request_pending: 1  row: 0x10e236780  session: 0x10e4cd480  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:01,926 - logic_logger - INFO
..Item[None] {Insert - client} id: None, order_id: None, product_id: 2, quantity: 2, amount: None, unit_price: None  row: 0x10e782950  session: 0x10e4cd480  ins_upd_dlt: ins, initial: ins - 2026-11-19 19:46:01,926 - logic_logger - INFO
..Item[None] {copy_rules for role: product - unit_price} id: None, order_id: None, product_id: 2, quantity: 2, amount: None, unit_price: 90.0000000000  row: 0x10e782950  session: 0x10e4cd480  ins_upd_dlt: ins, initial: ins - 2026-11-19 19:46:01,926 - logic_logger - INFO
..Item[None] {Formula amount} id: None, order_id: None, product_id: 2, quantity: 2, amount: 180.0000000000, unit_price: 90.0000000000  row: 0x10e782950  session: 0x10e4cd480  ins_upd_dlt: ins, initial: ins - 2026-11-19 19:46:01,926 - logic_logger - INFO
....Order[None] {Update - Adjusting order: amount_total} id: None, notes: behave test, customer_id: 50, CreatedOn: 2026-11-19, date_shipped: None, amount_total:  [0-->] 180.0000000000, CreatedOnDay: 2026-11-19  row: 0x10e777890  session: 0x10e4cd480  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:01,927 - logic_logger - INFO
......DailyFlow[2026-11-19] {Update - Adjusting daily_flow: order_amount} day: 2026-11-19, order_count: 36, order_amount:  [10650.00-->] 10830.0000000000, message_received: 8, message_processed: 4, message_rejected: 3, message_pending: 1, request_received: 42, request_processed: 34, request_rejected: 7, request_pending: 1  row: 0x10e236780  session: 0x10e4cd480  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:01,927 - logic_logger - INFO
......DailyFlow[2026-11-19] {Prune Formula: message_pending [['message_received', 'message_processed', 'message_rejected']]} day: 2026-11-19, order_count: 36, order_amount:  [10650.00-->] 10830.0000000000, message_received: 8, message_processed: 4, message_rejected: 3, message_pending: 1, request_received: 42, request_processed: 34, request_rejected: 7, request_pending: 1  row: 0x10e236780  session: 0x10e4cd480  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:01,927 - logic_logger - INFO
......DailyFlow[2026-11-19] {Prune Formula: request_pending [['request_received', 'request_processed', 'request_rejected']]} day: 2026-11-19, order_count: 36, order_amount:  [10650.00-->] 10830.0000000000, message_received: 8, message_processed: 4, message_rejected: 3, message_pending: 1, request_received: 42, request_processed: 34, request_rejected: 7, request_pending: 1  row: 0x10e236780  session: 0x10e4cd480  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:01,927 - logic_logger - INFO
......Customer[50] {Update - Adjusting customer: balance} id: 50, name: Xia 1795146361918, balance:  [0E-10-->] 180.0000000000, credit_limit: 2000.0000000000, email: None, email_opt_out: None  row: 0x10e49eed0  session: 0x10e4cd480  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:01,927 - logic_logger - INFO
..Item[None] {Insert - client} id: None, order_id: None, product_id: None, quantity: 1, amount: None, unit_price: None  row: 0x10e783ed0  session: 0x10e4cd480  ins_upd_dlt: ins, initial: ins - 2026-11-19 19:46:01,927 - logic_logger - INFO
..Item[None] {copy_rules for role: product - unit_price} id: None, order_id: None, product_id: None, quantity: 1, amount: None, unit_price: 150.0000000000  row: 0x10e783ed0  session: 0x10e4cd480  ins_upd_dlt: ins, initial: ins - 2026-11-19 19:46:01,927 - logic_logger - INFO
..Item[None] {Formula amount} id: None, order_id: None, product_id: None, quantity: 1, amount: 150.0000000000, unit_price: 150.0000000000  row: 0x10e783ed0  session: 0x10e4cd480  ins_upd_dlt: ins, initial: ins - 2026-11-19 19:46:01,927 - logic_logger - INFO
....Order[None] {Update - Adjusting order: amount_total} id: None, notes: behave test, customer_id: 50, CreatedOn: 2026-11-19, date_shipped: None, amount_total:  [180.0000000000-->] 330.0000000000, CreatedOnDay: 2026-11-19  row: 0x10e777890  session: 0x10e4cd480  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:01,927 - logic_logger - INFO
......DailyFlow[2026-11-19] {Update - Adjusting daily_flow: order_amount} day: 2026-11-19, order_count: 36, order_amount:  [10830.0000000000-->] 10980.0000000000, message_received: 8, message_processed: 4, message_rejected: 3, message_pending: 1, request_received: 42, request_processed: 34, request_rejected: 7, request_pending: 1  row: 0x10e236780  session: 0x10e4cd480  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:01,927 - logic_logger - INFO
......DailyFlow[2026-11-19] {Prune Formula: message_pending [['message_received', 'message_processed', 'message_rejected']]} day: 2026-11-19, order_count: 36, order_amount:  [10830.0000000000-->] 10980.0000000000, message_received: 8, message_processed: 4, message_rejected: 3, message_pending: 1, request_received: 42, request_processed: 34, request_rejected: 7, request_pending: 1  row: 0x10e236780  session: 0x10e4cd480  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:01,927 - logic_logger - INFO
......DailyFlow[2026-11-19] {Prune Formula: request_pending [['request_received', 'request_processed', 'request_rejected']]} day: 2026-11-19, order_count: 36, order_amount:  [10830.0000000000-->] 10980.0000000000, message_received: 8, message_processed: 4, message_rejected: 3, message_pending: 1, request_received: 42, request_processed: 34, request_rejected: 7, request_pending: 1  row: 0x10e236780  session: 0x10e4cd480  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:01,927 - logic_logger - INFO
......Customer[50] {Update - Adjusting customer: balance} id: 50, name: Xia 1795146361918, balance:  [180.0000000000-->] 330.0000000000, credit_limit: 2000.0000000000, email: None, email_opt_out: None  row: 0x10e49eed0  session: 0x10e4cd480  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:01,927 - logic_logger - INFO
Logic Phase:		COMMIT LOGIC		(session=0x10e4cd480)   										 - 2026-11-19 19:46:01,927 - logic_logger - INFO
Logic Phase:		AFTER_FLUSH LOGIC	(session=0x10e4cd480)   										 - 2026-11-19 19:46:01,928 - logic_logger - INFO
..Order[225] {AfterFlush Event} id: 225, notes: behave test, customer_id: 50, CreatedOn: 2026-11-19, date_shipped: None, amount_total: 330.0000000000, CreatedOnDay: 2026-11-19  row: 0x10e777890  session: 0x10e4cd480  ins_upd_dlt: ins, initial: ins - 2026-11-19 19:46:01,928 - logic_logger - INFO


Logic Phase:		ROW LOGIC		(session=0x10e4ce580) (sqlalchemy before_flush)			 - 2026-11-19 19:46:01,932 - logic_logger - INFO
..Order[225] {Update - client} id: 225, notes: behave test, customer_id: 50, CreatedOn: 2026-11-19, date_shipped:  [None-->] 2026-11-19 00:00:00, amount_total: 330.0000000000, CreatedOnDay: 2026-11-19  row: 0x10e776d50  session: 0x10e4ce580  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:01,932 - logic_logger - INFO
....Customer[50] {Update - Adjusting customer: balance} id: 50, name: Xia 1795146361918, balance:  [330.0000000000-->] 0E-10, credit_limit: 2000.0000000000, email: None, email_opt_out: None  row: 0x10e808350  session: 0x10e4ce580  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:01,932 - logic_logger - INFO
Logic Phase:		COMMIT LOGIC		(session=0x10e4ce580)   										 - 2026-11-19 19:46:01,932 - logic_logger - INFO
Logic Phase:		AFTER_FLUSH LOGIC	(session=0x10e4ce580)   										 - 2026-11-19 19:46:01,933 - logic_logger - INFO
..Order[225] {AfterFlush Event} id: 225, notes: behave test, customer_id: 50, CreatedOn: 2026-11-19, date_shipped:  [None-->] 2026-11-19 00:00:00, amount_total: 330.0000000000, CreatedOnDay: 2026-11-19  row: 0x10e776d50  session: 0x10e4ce580  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:01,933 - logic_logger - INFO
..Order[225] {publish_kafka_message: topic='order_shipping', key={'id': 225}} id: 225, notes: behave test, customer_id: 50, CreatedOn: 2026-11-19, date_shipped:  [None-->] 2026-11-19 00:00:00, amount_total: 330.0000000000, CreatedOnDay: 2026-11-19  row: 0x10e776d50  session: 0x10e4ce580  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:01,941 - logic_logger - INFO

```
</details>

&nbsp;
&nbsp;

#### Scenario: Unshipping an order adds it back to the balance ✅ (0.56 s)
&emsp;  Scenario: Unshipping an order adds it back to the balance  
&emsp;&emsp;    Given a new customer "Yan" with credit limit 2000  
&emsp;&emsp;    And a B2B order is placed for "Yan" with 2 Widget and 1 Gadget  
&emsp;&emsp;    And the order is shipped  
&emsp;&emsp;    When the order is unshipped  
&emsp;&emsp;    Then the balance of "Yan" is 330  

<details markdown>
<summary>Rules exercised and logic log (4 transactions)</summary>


&nbsp;
&nbsp;


**Rules Used** in Scenario: Unshipping an order adds it back to the balance
```
  DailyFlow  
    1. Derive DailyFlow.request_rejected as Count(OrderB2bRequest Where Rule.count(derive=models.DailyFlow.request_rejected, as_count_of=models.OrderB2bRequest, where=lambda row: row.error_text is not None, insert_parent=True), insert_parent)  
    2. Derive DailyFlow.request_pending as Formula (2): Rule.formula(derive=models.DailyFlow.request_pend [...]  
    3. Derive DailyFlow.request_processed as Count(OrderB2bRequest Where Rule.count(derive=models.DailyFlow.request_processed, as_count_of=models.OrderB2bRequest, where=lambda row: row.is_processed == True, insert_parent=True), insert_parent)  
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
**Logic Log** in Scenario: Unshipping an order adds it back to the balance (4 transactions)
```
Logic Phase:		ROW LOGIC		(session=0x10e4cd480) (sqlalchemy before_flush)			 - 2026-11-19 19:46:02,474 - logic_logger - INFO
..OrderB2bRequest[None] {Insert - client} id: None, CreatedOn: None, CreatedOnDay: None, payload: {"Account": "Yan 1795146362465", "Notes": "behave test", "Items": [{"Name": "Widget", "QuantityOrdered": 2}, {"Name": "Gadget", "QuantityOrdered": 1}]}, is_processed: False, error_text: None  row: 0x10e456a50  session: 0x10e4cd480  ins_upd_dlt: ins, initial: ins - 2026-11-19 19:46:02,474 - logic_logger - INFO
..OrderB2bRequest[None] {early_row_event_all_classes - handle_all did stamping} id: None, CreatedOn: 2026-11-19 19:46:02.474866, CreatedOnDay: 2026-11-19, payload: {"Account": "Yan 1795146362465", "Notes": "behave test", "Items": [{"Name": "Widget", "QuantityOrdered": 2}, {"Name": "Gadget", "QuantityOrdered": 1}]}, is_processed: False, error_text: None  row: 0x10e456a50  session: 0x10e4cd480  ins_upd_dlt: ins, initial: ins - 2026-11-19 19:46:02,474 - logic_logger - INFO
....DailyFlow[2026-11-19] {Update - Adjusting daily_flow: request_received} day: 2026-11-19, order_count: 36, order_amount: 10980.00, message_received: 8, message_processed: 4, message_rejected: 3, message_pending: 1, request_received:  [42-->] 43, request_processed: 34, request_rejected: 7, request_pending: 1  row: 0x10e236780  session: 0x10e4cd480  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:02,475 - logic_logger - INFO
....DailyFlow[2026-11-19] {Prune Formula: message_pending [['message_received', 'message_processed', 'message_rejected']]} day: 2026-11-19, order_count: 36, order_amount: 10980.00, message_received: 8, message_processed: 4, message_rejected: 3, message_pending: 1, request_received:  [42-->] 43, request_processed: 34, request_rejected: 7, request_pending: 1  row: 0x10e236780  session: 0x10e4cd480  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:02,475 - logic_logger - INFO
....DailyFlow[2026-11-19] {Formula request_pending} day: 2026-11-19, order_count: 36, order_amount: 10980.00, message_received: 8, message_processed: 4, message_rejected: 3, message_pending: 1, request_received:  [42-->] 43, request_processed: 34, request_rejected: 7, request_pending:  [1-->] 2  row: 0x10e236780  session: 0x10e4cd480  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:02,475 - logic_logger - INFO
Logic Phase:		COMMIT LOGIC		(session=0x10e4cd480)   										 - 2026-11-19 19:46:02,475 - logic_logger - INFO
Logic Phase:		AFTER_FLUSH LOGIC	(session=0x10e4cd480)   										 - 2026-11-19 19:46:02,476 - logic_logger - INFO


Logic Phase:		ROW LOGIC		(session=0x10e4cd480) (sqlalchemy before_flush)			 - 2026-11-19 19:46:02,481 - logic_logger - INFO
..Product[1] {Update - client} id: 1, name: Gadget, count_suppliers: 0, unit_price: 150.0000000000  row: 0x10e4c06e0  session: 0x10e4cd480  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:02,481 - logic_logger - INFO
..OrderB2bRequest[149] {Update - client} id: 149, CreatedOn: 2026-11-19 19:46:02.474866, CreatedOnDay: 2026-11-19, payload: {"Account": "Yan 1795146362465", "Notes": "behave test", "Items": [{"Name": "Widget", "QuantityOrdered": 2}, {"Name": "Gadget", "QuantityOrdered": 1}]}, is_processed:  [False-->] True, error_text: None  row: 0x10e456a50  session: 0x10e4cd480  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:02,481 - logic_logger - INFO
....DailyFlow[2026-11-19] {Update - Adjusting daily_flow: request_processed} day: 2026-11-19, order_count: 36, order_amount: 10980.00, message_received: 8, message_processed: 4, message_rejected: 3, message_pending: 1, request_received: 43, request_processed:  [34-->] 35, request_rejected: 7, request_pending: 2  row: 0x10e236780  session: 0x10e4cd480  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:02,482 - logic_logger - INFO
....DailyFlow[2026-11-19] {Prune Formula: message_pending [['message_received', 'message_processed', 'message_rejected']]} day: 2026-11-19, order_count: 36, order_amount: 10980.00, message_received: 8, message_processed: 4, message_rejected: 3, message_pending: 1, request_received: 43, request_processed:  [34-->] 35, request_rejected: 7, request_pending: 2  row: 0x10e236780  session: 0x10e4cd480  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:02,482 - logic_logger - INFO
....DailyFlow[2026-11-19] {Formula request_pending} day: 2026-11-19, order_count: 36, order_amount: 10980.00, message_received: 8, message_processed: 4, message_rejected: 3, message_pending: 1, request_received: 43, request_processed:  [34-->] 35, request_rejected: 7, request_pending:  [2-->] 1  row: 0x10e236780  session: 0x10e4cd480  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:02,482 - logic_logger - INFO
..Order[None] {Insert - client} id: None, notes: behave test, customer_id: 51, CreatedOn: None, date_shipped: None, amount_total: None, CreatedOnDay: None  row: 0x10e776f00  session: 0x10e4cd480  ins_upd_dlt: ins, initial: ins - 2026-11-19 19:46:02,482 - logic_logger - INFO
..Order[None] {early_row_event_all_classes - handle_all did stamping} id: None, notes: behave test, customer_id: 51, CreatedOn: 2026-11-19, date_shipped: None, amount_total: None, CreatedOnDay: 2026-11-19  row: 0x10e776f00  session: 0x10e4cd480  ins_upd_dlt: ins, initial: ins - 2026-11-19 19:46:02,482 - logic_logger - INFO
..Order[None] {server aggregate_defaults: amount_total } id: None, notes: behave test, customer_id: 51, CreatedOn: 2026-11-19, date_shipped: None, amount_total: 0, CreatedOnDay: 2026-11-19  row: 0x10e776f00  session: 0x10e4cd480  ins_upd_dlt: ins, initial: ins - 2026-11-19 19:46:02,482 - logic_logger - INFO
....DailyFlow[2026-11-19] {Update - Adjusting daily_flow: order_count} day: 2026-11-19, order_count:  [36-->] 37, order_amount: 10980.00, message_received: 8, message_processed: 4, message_rejected: 3, message_pending: 1, request_received: 43, request_processed: 35, request_rejected: 7, request_pending: 1  row: 0x10e236780  session: 0x10e4cd480  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:02,482 - logic_logger - INFO
....DailyFlow[2026-11-19] {Prune Formula: message_pending [['message_received', 'message_processed', 'message_rejected']]} day: 2026-11-19, order_count:  [36-->] 37, order_amount: 10980.00, message_received: 8, message_processed: 4, message_rejected: 3, message_pending: 1, request_received: 43, request_processed: 35, request_rejected: 7, request_pending: 1  row: 0x10e236780  session: 0x10e4cd480  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:02,482 - logic_logger - INFO
....DailyFlow[2026-11-19] {Prune Formula: request_pending [['request_received', 'request_processed', 'request_rejected']]} day: 2026-11-19, order_count:  [36-->] 37, order_amount: 10980.00, message_received: 8, message_processed: 4, message_rejected: 3, message_pending: 1, request_received: 43, request_processed: 35, request_rejected: 7, request_pending: 1  row: 0x10e236780  session: 0x10e4cd480  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:02,483 - logic_logger - INFO
..Item[None] {Insert - client} id: None, order_id: None, product_id: 2, quantity: 2, amount: None, unit_price: None  row: 0x10e53fed0  session: 0x10e4cd480  ins_upd_dlt: ins, initial: ins - 2026-11-19 19:46:02,483 - logic_logger - INFO
..Item[None] {copy_rules for role: product - unit_price} id: None, order_id: None, product_id: 2, quantity: 2, amount: None, unit_price: 90.0000000000  row: 0x10e53fed0  session: 0x10e4cd480  ins_upd_dlt: ins, initial: ins - 2026-11-19 19:46:02,483 - logic_logger - INFO
..Item[None] {Formula amount} id: None, order_id: None, product_id: 2, quantity: 2, amount: 180.0000000000, unit_price: 90.0000000000  row: 0x10e53fed0  session: 0x10e4cd480  ins_upd_dlt: ins, initial: ins - 2026-11-19 19:46:02,483 - logic_logger - INFO
....Order[None] {Update - Adjusting order: amount_total} id: None, notes: behave test, customer_id: 51, CreatedOn: 2026-11-19, date_shipped: None, amount_total:  [0-->] 180.0000000000, CreatedOnDay: 2026-11-19  row: 0x10e776f00  session: 0x10e4cd480  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:02,483 - logic_logger - INFO
......DailyFlow[2026-11-19] {Update - Adjusting daily_flow: order_amount} day: 2026-11-19, order_count: 37, order_amount:  [10980.00-->] 11160.0000000000, message_received: 8, message_processed: 4, message_rejected: 3, message_pending: 1, request_received: 43, request_processed: 35, request_rejected: 7, request_pending: 1  row: 0x10e236780  session: 0x10e4cd480  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:02,483 - logic_logger - INFO
......DailyFlow[2026-11-19] {Prune Formula: message_pending [['message_received', 'message_processed', 'message_rejected']]} day: 2026-11-19, order_count: 37, order_amount:  [10980.00-->] 11160.0000000000, message_received: 8, message_processed: 4, message_rejected: 3, message_pending: 1, request_received: 43, request_processed: 35, request_rejected: 7, request_pending: 1  row: 0x10e236780  session: 0x10e4cd480  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:02,483 - logic_logger - INFO
......DailyFlow[2026-11-19] {Prune Formula: request_pending [['request_received', 'request_processed', 'request_rejected']]} day: 2026-11-19, order_count: 37, order_amount:  [10980.00-->] 11160.0000000000, message_received: 8, message_processed: 4, message_rejected: 3, message_pending: 1, request_received: 43, request_processed: 35, request_rejected: 7, request_pending: 1  row: 0x10e236780  session: 0x10e4cd480  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:02,483 - logic_logger - INFO
......Customer[51] {Update - Adjusting customer: balance} id: 51, name: Yan 1795146362465, balance:  [0E-10-->] 180.0000000000, credit_limit: 2000.0000000000, email: None, email_opt_out: None  row: 0x10e7a6ed0  session: 0x10e4cd480  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:02,483 - logic_logger - INFO
..Item[None] {Insert - client} id: None, order_id: None, product_id: None, quantity: 1, amount: None, unit_price: None  row: 0x10e80b1d0  session: 0x10e4cd480  ins_upd_dlt: ins, initial: ins - 2026-11-19 19:46:02,484 - logic_logger - INFO
..Item[None] {copy_rules for role: product - unit_price} id: None, order_id: None, product_id: None, quantity: 1, amount: None, unit_price: 150.0000000000  row: 0x10e80b1d0  session: 0x10e4cd480  ins_upd_dlt: ins, initial: ins - 2026-11-19 19:46:02,484 - logic_logger - INFO
..Item[None] {Formula amount} id: None, order_id: None, product_id: None, quantity: 1, amount: 150.0000000000, unit_price: 150.0000000000  row: 0x10e80b1d0  session: 0x10e4cd480  ins_upd_dlt: ins, initial: ins - 2026-11-19 19:46:02,484 - logic_logger - INFO
....Order[None] {Update - Adjusting order: amount_total} id: None, notes: behave test, customer_id: 51, CreatedOn: 2026-11-19, date_shipped: None, amount_total:  [180.0000000000-->] 330.0000000000, CreatedOnDay: 2026-11-19  row: 0x10e776f00  session: 0x10e4cd480  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:02,484 - logic_logger - INFO
......DailyFlow[2026-11-19] {Update - Adjusting daily_flow: order_amount} day: 2026-11-19, order_count: 37, order_amount:  [11160.0000000000-->] 11310.0000000000, message_received: 8, message_processed: 4, message_rejected: 3, message_pending: 1, request_received: 43, request_processed: 35, request_rejected: 7, request_pending: 1  row: 0x10e236780  session: 0x10e4cd480  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:02,484 - logic_logger - INFO
......DailyFlow[2026-11-19] {Prune Formula: message_pending [['message_received', 'message_processed', 'message_rejected']]} day: 2026-11-19, order_count: 37, order_amount:  [11160.0000000000-->] 11310.0000000000, message_received: 8, message_processed: 4, message_rejected: 3, message_pending: 1, request_received: 43, request_processed: 35, request_rejected: 7, request_pending: 1  row: 0x10e236780  session: 0x10e4cd480  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:02,484 - logic_logger - INFO
......DailyFlow[2026-11-19] {Prune Formula: request_pending [['request_received', 'request_processed', 'request_rejected']]} day: 2026-11-19, order_count: 37, order_amount:  [11160.0000000000-->] 11310.0000000000, message_received: 8, message_processed: 4, message_rejected: 3, message_pending: 1, request_received: 43, request_processed: 35, request_rejected: 7, request_pending: 1  row: 0x10e236780  session: 0x10e4cd480  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:02,484 - logic_logger - INFO
......Customer[51] {Update - Adjusting customer: balance} id: 51, name: Yan 1795146362465, balance:  [180.0000000000-->] 330.0000000000, credit_limit: 2000.0000000000, email: None, email_opt_out: None  row: 0x10e7a6ed0  session: 0x10e4cd480  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:02,484 - logic_logger - INFO
Logic Phase:		COMMIT LOGIC		(session=0x10e4cd480)   										 - 2026-11-19 19:46:02,484 - logic_logger - INFO
Logic Phase:		AFTER_FLUSH LOGIC	(session=0x10e4cd480)   										 - 2026-11-19 19:46:02,485 - logic_logger - INFO
..Order[226] {AfterFlush Event} id: 226, notes: behave test, customer_id: 51, CreatedOn: 2026-11-19, date_shipped: None, amount_total: 330.0000000000, CreatedOnDay: 2026-11-19  row: 0x10e776f00  session: 0x10e4cd480  ins_upd_dlt: ins, initial: ins - 2026-11-19 19:46:02,486 - logic_logger - INFO


Logic Phase:		ROW LOGIC		(session=0x10e4cee00) (sqlalchemy before_flush)			 - 2026-11-19 19:46:02,490 - logic_logger - INFO
..Order[226] {Update - client} id: 226, notes: behave test, customer_id: 51, CreatedOn: 2026-11-19, date_shipped:  [None-->] 2026-11-19 00:00:00, amount_total: 330.0000000000, CreatedOnDay: 2026-11-19  row: 0x10e777890  session: 0x10e4cee00  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:02,490 - logic_logger - INFO
....Customer[51] {Update - Adjusting customer: balance} id: 51, name: Yan 1795146362465, balance:  [330.0000000000-->] 0E-10, credit_limit: 2000.0000000000, email: None, email_opt_out: None  row: 0x10f1fc0d0  session: 0x10e4cee00  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:02,491 - logic_logger - INFO
Logic Phase:		COMMIT LOGIC		(session=0x10e4cee00)   										 - 2026-11-19 19:46:02,491 - logic_logger - INFO
Logic Phase:		AFTER_FLUSH LOGIC	(session=0x10e4cee00)   										 - 2026-11-19 19:46:02,491 - logic_logger - INFO
..Order[226] {AfterFlush Event} id: 226, notes: behave test, customer_id: 51, CreatedOn: 2026-11-19, date_shipped:  [None-->] 2026-11-19 00:00:00, amount_total: 330.0000000000, CreatedOnDay: 2026-11-19  row: 0x10e777890  session: 0x10e4cee00  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:02,491 - logic_logger - INFO
..Order[226] {publish_kafka_message: topic='order_shipping', key={'id': 226}} id: 226, notes: behave test, customer_id: 51, CreatedOn: 2026-11-19, date_shipped:  [None-->] 2026-11-19 00:00:00, amount_total: 330.0000000000, CreatedOnDay: 2026-11-19  row: 0x10e777890  session: 0x10e4cee00  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:02,494 - logic_logger - INFO


Logic Phase:		ROW LOGIC		(session=0x10e4cf570) (sqlalchemy before_flush)			 - 2026-11-19 19:46:03,010 - logic_logger - INFO
..Order[226] {Update - client} id: 226, notes: behave test, customer_id: 51, CreatedOn: 2026-11-19, date_shipped:  [2026-11-19-->] None, amount_total: 330.0000000000, CreatedOnDay: 2026-11-19  row: 0x10e7d04d0  session: 0x10e4cf570  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:03,011 - logic_logger - INFO
....Customer[51] {Update - Adjusting customer: balance} id: 51, name: Yan 1795146362465, balance:  [0E-10-->] 330.0000000000, credit_limit: 2000.0000000000, email: None, email_opt_out: None  row: 0x10f1fd650  session: 0x10e4cf570  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:03,012 - logic_logger - INFO
Logic Phase:		COMMIT LOGIC		(session=0x10e4cf570)   										 - 2026-11-19 19:46:03,012 - logic_logger - INFO
Logic Phase:		AFTER_FLUSH LOGIC	(session=0x10e4cf570)   										 - 2026-11-19 19:46:03,013 - logic_logger - INFO
..Order[226] {AfterFlush Event} id: 226, notes: behave test, customer_id: 51, CreatedOn: 2026-11-19, date_shipped:  [2026-11-19-->] None, amount_total: 330.0000000000, CreatedOnDay: 2026-11-19  row: 0x10e7d04d0  session: 0x10e4cf570  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:03,014 - logic_logger - INFO

```
</details>

&nbsp;
&nbsp;

#### Scenario: Order exactly at the credit limit is accepted ✅ (0.03 s)
&emsp;  Scenario: Order exactly at the credit limit is accepted  
&emsp;&emsp;    Given a new customer "Zed" with credit limit 300  
&emsp;&emsp;    When a B2B order is placed for "Zed" with 2 Gadget  
&emsp;&emsp;    Then the order is accepted  
&emsp;&emsp;    And the balance of "Zed" is 300  

<details markdown>
<summary>Rules exercised and logic log (2 transactions)</summary>


&nbsp;
&nbsp;


**Rules Used** in Scenario: Order exactly at the credit limit is accepted
```
  DailyFlow  
    1. Derive DailyFlow.request_rejected as Count(OrderB2bRequest Where Rule.count(derive=models.DailyFlow.request_rejected, as_count_of=models.OrderB2bRequest, where=lambda row: row.error_text is not None, insert_parent=True), insert_parent)  
    2. Derive DailyFlow.request_pending as Formula (2): Rule.formula(derive=models.DailyFlow.request_pend [...]  
    3. Derive DailyFlow.request_processed as Count(OrderB2bRequest Where Rule.count(derive=models.DailyFlow.request_processed, as_count_of=models.OrderB2bRequest, where=lambda row: row.is_processed == True, insert_parent=True), insert_parent)  
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
**Logic Log** in Scenario: Order exactly at the credit limit is accepted (2 transactions)
```
Logic Phase:		ROW LOGIC		(session=0x10e4cf790) (sqlalchemy before_flush)			 - 2026-11-19 19:46:03,038 - logic_logger - INFO
..OrderB2bRequest[None] {Insert - client} id: None, CreatedOn: None, CreatedOnDay: None, payload: {"Account": "Zed 1795146363029", "Notes": "behave test", "Items": [{"Name": "Gadget", "QuantityOrdered": 2}]}, is_processed: False, error_text: None  row: 0x10e49ddd0  session: 0x10e4cf790  ins_upd_dlt: ins, initial: ins - 2026-11-19 19:46:03,038 - logic_logger - INFO
..OrderB2bRequest[None] {early_row_event_all_classes - handle_all did stamping} id: None, CreatedOn: 2026-11-19 19:46:03.038935, CreatedOnDay: 2026-11-19, payload: {"Account": "Zed 1795146363029", "Notes": "behave test", "Items": [{"Name": "Gadget", "QuantityOrdered": 2}]}, is_processed: False, error_text: None  row: 0x10e49ddd0  session: 0x10e4cf790  ins_upd_dlt: ins, initial: ins - 2026-11-19 19:46:03,038 - logic_logger - INFO
....DailyFlow[2026-11-19] {Update - Adjusting daily_flow: request_received} day: 2026-11-19, order_count: 37, order_amount: 11310.00, message_received: 8, message_processed: 4, message_rejected: 3, message_pending: 1, request_received:  [43-->] 44, request_processed: 35, request_rejected: 7, request_pending: 1  row: 0x10e8609f0  session: 0x10e4cf790  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:03,039 - logic_logger - INFO
....DailyFlow[2026-11-19] {Prune Formula: message_pending [['message_received', 'message_processed', 'message_rejected']]} day: 2026-11-19, order_count: 37, order_amount: 11310.00, message_received: 8, message_processed: 4, message_rejected: 3, message_pending: 1, request_received:  [43-->] 44, request_processed: 35, request_rejected: 7, request_pending: 1  row: 0x10e8609f0  session: 0x10e4cf790  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:03,039 - logic_logger - INFO
....DailyFlow[2026-11-19] {Formula request_pending} day: 2026-11-19, order_count: 37, order_amount: 11310.00, message_received: 8, message_processed: 4, message_rejected: 3, message_pending: 1, request_received:  [43-->] 44, request_processed: 35, request_rejected: 7, request_pending:  [1-->] 2  row: 0x10e8609f0  session: 0x10e4cf790  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:03,039 - logic_logger - INFO
Logic Phase:		COMMIT LOGIC		(session=0x10e4cf790)   										 - 2026-11-19 19:46:03,039 - logic_logger - INFO
Logic Phase:		AFTER_FLUSH LOGIC	(session=0x10e4cf790)   										 - 2026-11-19 19:46:03,040 - logic_logger - INFO


Logic Phase:		ROW LOGIC		(session=0x10e4cf790) (sqlalchemy before_flush)			 - 2026-11-19 19:46:03,043 - logic_logger - INFO
..Product[1] {Update - client} id: 1, name: Gadget, count_suppliers: 0, unit_price: 150.0000000000  row: 0x10e7f72a0  session: 0x10e4cf790  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:03,043 - logic_logger - INFO
..OrderB2bRequest[150] {Update - client} id: 150, CreatedOn: 2026-11-19 19:46:03.038935, CreatedOnDay: 2026-11-19, payload: {"Account": "Zed 1795146363029", "Notes": "behave test", "Items": [{"Name": "Gadget", "QuantityOrdered": 2}]}, is_processed:  [False-->] True, error_text: None  row: 0x10e49ddd0  session: 0x10e4cf790  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:03,044 - logic_logger - INFO
....DailyFlow[2026-11-19] {Update - Adjusting daily_flow: request_processed} day: 2026-11-19, order_count: 37, order_amount: 11310.00, message_received: 8, message_processed: 4, message_rejected: 3, message_pending: 1, request_received: 44, request_processed:  [35-->] 36, request_rejected: 7, request_pending: 2  row: 0x10e8609f0  session: 0x10e4cf790  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:03,044 - logic_logger - INFO
....DailyFlow[2026-11-19] {Prune Formula: message_pending [['message_received', 'message_processed', 'message_rejected']]} day: 2026-11-19, order_count: 37, order_amount: 11310.00, message_received: 8, message_processed: 4, message_rejected: 3, message_pending: 1, request_received: 44, request_processed:  [35-->] 36, request_rejected: 7, request_pending: 2  row: 0x10e8609f0  session: 0x10e4cf790  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:03,044 - logic_logger - INFO
....DailyFlow[2026-11-19] {Formula request_pending} day: 2026-11-19, order_count: 37, order_amount: 11310.00, message_received: 8, message_processed: 4, message_rejected: 3, message_pending: 1, request_received: 44, request_processed:  [35-->] 36, request_rejected: 7, request_pending:  [2-->] 1  row: 0x10e8609f0  session: 0x10e4cf790  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:03,044 - logic_logger - INFO
..Order[None] {Insert - client} id: None, notes: behave test, customer_id: 52, CreatedOn: None, date_shipped: None, amount_total: None, CreatedOnDay: None  row: 0x10e7d08c0  session: 0x10e4cf790  ins_upd_dlt: ins, initial: ins - 2026-11-19 19:46:03,044 - logic_logger - INFO
..Order[None] {early_row_event_all_classes - handle_all did stamping} id: None, notes: behave test, customer_id: 52, CreatedOn: 2026-11-19, date_shipped: None, amount_total: None, CreatedOnDay: 2026-11-19  row: 0x10e7d08c0  session: 0x10e4cf790  ins_upd_dlt: ins, initial: ins - 2026-11-19 19:46:03,044 - logic_logger - INFO
..Order[None] {server aggregate_defaults: amount_total } id: None, notes: behave test, customer_id: 52, CreatedOn: 2026-11-19, date_shipped: None, amount_total: 0, CreatedOnDay: 2026-11-19  row: 0x10e7d08c0  session: 0x10e4cf790  ins_upd_dlt: ins, initial: ins - 2026-11-19 19:46:03,044 - logic_logger - INFO
....DailyFlow[2026-11-19] {Update - Adjusting daily_flow: order_count} day: 2026-11-19, order_count:  [37-->] 38, order_amount: 11310.00, message_received: 8, message_processed: 4, message_rejected: 3, message_pending: 1, request_received: 44, request_processed: 36, request_rejected: 7, request_pending: 1  row: 0x10e8609f0  session: 0x10e4cf790  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:03,045 - logic_logger - INFO
....DailyFlow[2026-11-19] {Prune Formula: message_pending [['message_received', 'message_processed', 'message_rejected']]} day: 2026-11-19, order_count:  [37-->] 38, order_amount: 11310.00, message_received: 8, message_processed: 4, message_rejected: 3, message_pending: 1, request_received: 44, request_processed: 36, request_rejected: 7, request_pending: 1  row: 0x10e8609f0  session: 0x10e4cf790  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:03,045 - logic_logger - INFO
....DailyFlow[2026-11-19] {Prune Formula: request_pending [['request_received', 'request_processed', 'request_rejected']]} day: 2026-11-19, order_count:  [37-->] 38, order_amount: 11310.00, message_received: 8, message_processed: 4, message_rejected: 3, message_pending: 1, request_received: 44, request_processed: 36, request_rejected: 7, request_pending: 1  row: 0x10e8609f0  session: 0x10e4cf790  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:03,045 - logic_logger - INFO
..Item[None] {Insert - client} id: None, order_id: None, product_id: None, quantity: 2, amount: None, unit_price: None  row: 0x10e3a2650  session: 0x10e4cf790  ins_upd_dlt: ins, initial: ins - 2026-11-19 19:46:03,045 - logic_logger - INFO
..Item[None] {copy_rules for role: product - unit_price} id: None, order_id: None, product_id: None, quantity: 2, amount: None, unit_price: 150.0000000000  row: 0x10e3a2650  session: 0x10e4cf790  ins_upd_dlt: ins, initial: ins - 2026-11-19 19:46:03,045 - logic_logger - INFO
..Item[None] {Formula amount} id: None, order_id: None, product_id: None, quantity: 2, amount: 300.0000000000, unit_price: 150.0000000000  row: 0x10e3a2650  session: 0x10e4cf790  ins_upd_dlt: ins, initial: ins - 2026-11-19 19:46:03,045 - logic_logger - INFO
....Order[None] {Update - Adjusting order: amount_total} id: None, notes: behave test, customer_id: 52, CreatedOn: 2026-11-19, date_shipped: None, amount_total:  [0-->] 300.0000000000, CreatedOnDay: 2026-11-19  row: 0x10e7d08c0  session: 0x10e4cf790  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:03,045 - logic_logger - INFO
......DailyFlow[2026-11-19] {Update - Adjusting daily_flow: order_amount} day: 2026-11-19, order_count: 38, order_amount:  [11310.00-->] 11610.0000000000, message_received: 8, message_processed: 4, message_rejected: 3, message_pending: 1, request_received: 44, request_processed: 36, request_rejected: 7, request_pending: 1  row: 0x10e8609f0  session: 0x10e4cf790  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:03,045 - logic_logger - INFO
......DailyFlow[2026-11-19] {Prune Formula: message_pending [['message_received', 'message_processed', 'message_rejected']]} day: 2026-11-19, order_count: 38, order_amount:  [11310.00-->] 11610.0000000000, message_received: 8, message_processed: 4, message_rejected: 3, message_pending: 1, request_received: 44, request_processed: 36, request_rejected: 7, request_pending: 1  row: 0x10e8609f0  session: 0x10e4cf790  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:03,045 - logic_logger - INFO
......DailyFlow[2026-11-19] {Prune Formula: request_pending [['request_received', 'request_processed', 'request_rejected']]} day: 2026-11-19, order_count: 38, order_amount:  [11310.00-->] 11610.0000000000, message_received: 8, message_processed: 4, message_rejected: 3, message_pending: 1, request_received: 44, request_processed: 36, request_rejected: 7, request_pending: 1  row: 0x10e8609f0  session: 0x10e4cf790  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:03,045 - logic_logger - INFO
......Customer[52] {Update - Adjusting customer: balance} id: 52, name: Zed 1795146363029, balance:  [0E-10-->] 300.0000000000, credit_limit: 300.0000000000, email: None, email_opt_out: None  row: 0x10e7a6950  session: 0x10e4cf790  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:03,045 - logic_logger - INFO
Logic Phase:		COMMIT LOGIC		(session=0x10e4cf790)   										 - 2026-11-19 19:46:03,046 - logic_logger - INFO
Logic Phase:		AFTER_FLUSH LOGIC	(session=0x10e4cf790)   										 - 2026-11-19 19:46:03,046 - logic_logger - INFO
..Order[227] {AfterFlush Event} id: 227, notes: behave test, customer_id: 52, CreatedOn: 2026-11-19, date_shipped: None, amount_total: 300.0000000000, CreatedOnDay: 2026-11-19  row: 0x10e7d08c0  session: 0x10e4cf790  ins_upd_dlt: ins, initial: ins - 2026-11-19 19:46:03,047 - logic_logger - INFO

```
</details>

&nbsp;
&nbsp;

#### Scenario: Order over the credit limit is rejected ✅ (0.02 s)
&emsp;  Scenario: Order over the credit limit is rejected  
&emsp;&emsp;    Given a new customer "Abe" with credit limit 299  
&emsp;&emsp;    When a B2B order is placed for "Abe" with 2 Gadget  
&emsp;&emsp;    Then the order is rejected with "exceeds credit limit"  
&emsp;&emsp;    And the balance of "Abe" is 0  

<details markdown>
<summary>Rules exercised and logic log (2 transactions)</summary>


&nbsp;
&nbsp;


**Rules Used** in Scenario: Order over the credit limit is rejected
```
  DailyFlow  
    1. Derive DailyFlow.request_rejected as Count(OrderB2bRequest Where Rule.count(derive=models.DailyFlow.request_rejected, as_count_of=models.OrderB2bRequest, where=lambda row: row.error_text is not None, insert_parent=True), insert_parent)  
    2. Derive DailyFlow.request_pending as Formula (2): Rule.formula(derive=models.DailyFlow.request_pend [...]  
    3. Derive DailyFlow.request_processed as Count(OrderB2bRequest Where Rule.count(derive=models.DailyFlow.request_processed, as_count_of=models.OrderB2bRequest, where=lambda row: row.is_processed == True, insert_parent=True), insert_parent)  
    4. Derive DailyFlow.request_received as Count(OrderB2bRequest Where  - None, insert_parent)  
    5. Derive DailyFlow.order_amount as Sum(Order.amount_total Where  - None, insert_parent)  
    6. Derive DailyFlow.order_count as Count(Order Where  - None, insert_parent)  
  Customer  
    7. Derive Customer.balance as Sum(Order.amount_total Where Rule.sum(derive=models.Customer.balance, as_sum_of=models.Order.amount_total, where=lambda row: row.date_shipped is None))  
    8. Constraint Function: None  
  Item  
    9. Derive Item.amount as Formula (1): Rule.formula(derive=models.Item.amount, as_expres [...]  
    10. Derive Item.unit_price as Copy(product.unit_price)  
  Order  
    11. Derive Order.amount_total as Sum(Item.amount Where  - None)  
```
**Logic Log** in Scenario: Order over the credit limit is rejected (2 transactions)
```
Logic Phase:		ROW LOGIC		(session=0x10e4cff00) (sqlalchemy before_flush)			 - 2026-11-19 19:46:03,060 - logic_logger - INFO
..OrderB2bRequest[None] {Insert - client} id: None, CreatedOn: None, CreatedOnDay: None, payload: {"Account": "Abe 1795146363055", "Notes": "behave test", "Items": [{"Name": "Gadget", "QuantityOrdered": 2}]}, is_processed: False, error_text: None  row: 0x10e4540d0  session: 0x10e4cff00  ins_upd_dlt: ins, initial: ins - 2026-11-19 19:46:03,060 - logic_logger - INFO
..OrderB2bRequest[None] {early_row_event_all_classes - handle_all did stamping} id: None, CreatedOn: 2026-11-19 19:46:03.061009, CreatedOnDay: 2026-11-19, payload: {"Account": "Abe 1795146363055", "Notes": "behave test", "Items": [{"Name": "Gadget", "QuantityOrdered": 2}]}, is_processed: False, error_text: None  row: 0x10e4540d0  session: 0x10e4cff00  ins_upd_dlt: ins, initial: ins - 2026-11-19 19:46:03,061 - logic_logger - INFO
....DailyFlow[2026-11-19] {Update - Adjusting daily_flow: request_received} day: 2026-11-19, order_count: 38, order_amount: 11610.00, message_received: 8, message_processed: 4, message_rejected: 3, message_pending: 1, request_received:  [44-->] 45, request_processed: 36, request_rejected: 7, request_pending: 1  row: 0x10e860940  session: 0x10e4cff00  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:03,061 - logic_logger - INFO
....DailyFlow[2026-11-19] {Prune Formula: message_pending [['message_received', 'message_processed', 'message_rejected']]} day: 2026-11-19, order_count: 38, order_amount: 11610.00, message_received: 8, message_processed: 4, message_rejected: 3, message_pending: 1, request_received:  [44-->] 45, request_processed: 36, request_rejected: 7, request_pending: 1  row: 0x10e860940  session: 0x10e4cff00  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:03,061 - logic_logger - INFO
....DailyFlow[2026-11-19] {Formula request_pending} day: 2026-11-19, order_count: 38, order_amount: 11610.00, message_received: 8, message_processed: 4, message_rejected: 3, message_pending: 1, request_received:  [44-->] 45, request_processed: 36, request_rejected: 7, request_pending:  [1-->] 2  row: 0x10e860940  session: 0x10e4cff00  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:03,061 - logic_logger - INFO
Logic Phase:		COMMIT LOGIC		(session=0x10e4cff00)   										 - 2026-11-19 19:46:03,061 - logic_logger - INFO
Logic Phase:		AFTER_FLUSH LOGIC	(session=0x10e4cff00)   										 - 2026-11-19 19:46:03,062 - logic_logger - INFO


Logic Phase:		ROW LOGIC		(session=0x10e4cff00) (sqlalchemy before_flush)			 - 2026-11-19 19:46:03,064 - logic_logger - INFO
..Product[1] {Update - client} id: 1, name: Gadget, count_suppliers: 0, unit_price: 150.0000000000  row: 0x10e4c06e0  session: 0x10e4cff00  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:03,064 - logic_logger - INFO
..OrderB2bRequest[151] {Update - client} id: 151, CreatedOn: 2026-11-19 19:46:03.061009, CreatedOnDay: 2026-11-19, payload: {"Account": "Abe 1795146363055", "Notes": "behave test", "Items": [{"Name": "Gadget", "QuantityOrdered": 2}]}, is_processed:  [False-->] True, error_text: None  row: 0x10e4540d0  session: 0x10e4cff00  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:03,064 - logic_logger - INFO
....DailyFlow[2026-11-19] {Update - Adjusting daily_flow: request_processed} day: 2026-11-19, order_count: 38, order_amount: 11610.00, message_received: 8, message_processed: 4, message_rejected: 3, message_pending: 1, request_received: 45, request_processed:  [36-->] 37, request_rejected: 7, request_pending: 2  row: 0x10e235d30  session: 0x10e4cff00  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:03,065 - logic_logger - INFO
....DailyFlow[2026-11-19] {Prune Formula: message_pending [['message_received', 'message_processed', 'message_rejected']]} day: 2026-11-19, order_count: 38, order_amount: 11610.00, message_received: 8, message_processed: 4, message_rejected: 3, message_pending: 1, request_received: 45, request_processed:  [36-->] 37, request_rejected: 7, request_pending: 2  row: 0x10e235d30  session: 0x10e4cff00  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:03,065 - logic_logger - INFO
....DailyFlow[2026-11-19] {Formula request_pending} day: 2026-11-19, order_count: 38, order_amount: 11610.00, message_received: 8, message_processed: 4, message_rejected: 3, message_pending: 1, request_received: 45, request_processed:  [36-->] 37, request_rejected: 7, request_pending:  [2-->] 1  row: 0x10e235d30  session: 0x10e4cff00  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:03,065 - logic_logger - INFO
..Order[None] {Insert - client} id: None, notes: behave test, customer_id: 53, CreatedOn: None, date_shipped: None, amount_total: None, CreatedOnDay: None  row: 0x10e7d0b00  session: 0x10e4cff00  ins_upd_dlt: ins, initial: ins - 2026-11-19 19:46:03,065 - logic_logger - INFO
..Order[None] {early_row_event_all_classes - handle_all did stamping} id: None, notes: behave test, customer_id: 53, CreatedOn: 2026-11-19, date_shipped: None, amount_total: None, CreatedOnDay: 2026-11-19  row: 0x10e7d0b00  session: 0x10e4cff00  ins_upd_dlt: ins, initial: ins - 2026-11-19 19:46:03,065 - logic_logger - INFO
..Order[None] {server aggregate_defaults: amount_total } id: None, notes: behave test, customer_id: 53, CreatedOn: 2026-11-19, date_shipped: None, amount_total: 0, CreatedOnDay: 2026-11-19  row: 0x10e7d0b00  session: 0x10e4cff00  ins_upd_dlt: ins, initial: ins - 2026-11-19 19:46:03,065 - logic_logger - INFO
....DailyFlow[2026-11-19] {Update - Adjusting daily_flow: order_count} day: 2026-11-19, order_count:  [38-->] 39, order_amount: 11610.00, message_received: 8, message_processed: 4, message_rejected: 3, message_pending: 1, request_received: 45, request_processed: 37, request_rejected: 7, request_pending: 1  row: 0x10e235d30  session: 0x10e4cff00  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:03,065 - logic_logger - INFO
....DailyFlow[2026-11-19] {Prune Formula: message_pending [['message_received', 'message_processed', 'message_rejected']]} day: 2026-11-19, order_count:  [38-->] 39, order_amount: 11610.00, message_received: 8, message_processed: 4, message_rejected: 3, message_pending: 1, request_received: 45, request_processed: 37, request_rejected: 7, request_pending: 1  row: 0x10e235d30  session: 0x10e4cff00  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:03,065 - logic_logger - INFO
....DailyFlow[2026-11-19] {Prune Formula: request_pending [['request_received', 'request_processed', 'request_rejected']]} day: 2026-11-19, order_count:  [38-->] 39, order_amount: 11610.00, message_received: 8, message_processed: 4, message_rejected: 3, message_pending: 1, request_received: 45, request_processed: 37, request_rejected: 7, request_pending: 1  row: 0x10e235d30  session: 0x10e4cff00  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:03,065 - logic_logger - INFO
..Item[None] {Insert - client} id: None, order_id: None, product_id: None, quantity: 2, amount: None, unit_price: None  row: 0x10e809850  session: 0x10e4cff00  ins_upd_dlt: ins, initial: ins - 2026-11-19 19:46:03,065 - logic_logger - INFO
..Item[None] {copy_rules for role: product - unit_price} id: None, order_id: None, product_id: None, quantity: 2, amount: None, unit_price: 150.0000000000  row: 0x10e809850  session: 0x10e4cff00  ins_upd_dlt: ins, initial: ins - 2026-11-19 19:46:03,066 - logic_logger - INFO
..Item[None] {Formula amount} id: None, order_id: None, product_id: None, quantity: 2, amount: 300.0000000000, unit_price: 150.0000000000  row: 0x10e809850  session: 0x10e4cff00  ins_upd_dlt: ins, initial: ins - 2026-11-19 19:46:03,066 - logic_logger - INFO
....Order[None] {Update - Adjusting order: amount_total} id: None, notes: behave test, customer_id: 53, CreatedOn: 2026-11-19, date_shipped: None, amount_total:  [0-->] 300.0000000000, CreatedOnDay: 2026-11-19  row: 0x10e7d0b00  session: 0x10e4cff00  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:03,066 - logic_logger - INFO
......DailyFlow[2026-11-19] {Update - Adjusting daily_flow: order_amount} day: 2026-11-19, order_count: 39, order_amount:  [11610.00-->] 11910.0000000000, message_received: 8, message_processed: 4, message_rejected: 3, message_pending: 1, request_received: 45, request_processed: 37, request_rejected: 7, request_pending: 1  row: 0x10e235d30  session: 0x10e4cff00  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:03,066 - logic_logger - INFO
......DailyFlow[2026-11-19] {Prune Formula: message_pending [['message_received', 'message_processed', 'message_rejected']]} day: 2026-11-19, order_count: 39, order_amount:  [11610.00-->] 11910.0000000000, message_received: 8, message_processed: 4, message_rejected: 3, message_pending: 1, request_received: 45, request_processed: 37, request_rejected: 7, request_pending: 1  row: 0x10e235d30  session: 0x10e4cff00  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:03,066 - logic_logger - INFO
......DailyFlow[2026-11-19] {Prune Formula: request_pending [['request_received', 'request_processed', 'request_rejected']]} day: 2026-11-19, order_count: 39, order_amount:  [11610.00-->] 11910.0000000000, message_received: 8, message_processed: 4, message_rejected: 3, message_pending: 1, request_received: 45, request_processed: 37, request_rejected: 7, request_pending: 1  row: 0x10e235d30  session: 0x10e4cff00  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:03,066 - logic_logger - INFO
......Customer[53] {Update - Adjusting customer: balance} id: 53, name: Abe 1795146363055, balance:  [0E-10-->] 300.0000000000, credit_limit: 299.0000000000, email: None, email_opt_out: None  row: 0x10e7a4ad0  session: 0x10e4cff00  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:03,066 - logic_logger - INFO
......Customer[53] {Constraint Failure: Customer balance (300.0000000000) exceeds credit limit (299.0000000000)} id: 53, name: Abe 1795146363055, balance:  [0E-10-->] 300.0000000000, credit_limit: 299.0000000000, email: None, email_opt_out: None  row: 0x10e7a4ad0  session: 0x10e4cff00  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:03,066 - logic_logger - INFO

```
</details>

&nbsp;
&nbsp;

#### Scenario: Raising a quantity over the credit limit is rejected ✅ (0.03 s)
&emsp;  Scenario: Raising a quantity over the credit limit is rejected  
&emsp;&emsp;    Given a new customer "Bea" with credit limit 500  
&emsp;&emsp;    And a B2B order is placed for "Bea" with 2 Widget and 1 Gadget  
&emsp;&emsp;    When the quantity of the first item is changed to 10  
&emsp;&emsp;    Then the change is rejected with "exceeds credit limit"  
&emsp;&emsp;    And the first item amount is 180  
&emsp;&emsp;    And the balance of "Bea" is 330  

<details markdown>
<summary>Rules exercised and logic log (3 transactions)</summary>


&nbsp;
&nbsp;


**Rules Used** in Scenario: Raising a quantity over the credit limit is rejected
```
  DailyFlow  
    1. Derive DailyFlow.request_rejected as Count(OrderB2bRequest Where Rule.count(derive=models.DailyFlow.request_rejected, as_count_of=models.OrderB2bRequest, where=lambda row: row.error_text is not None, insert_parent=True), insert_parent)  
    2. Derive DailyFlow.request_pending as Formula (2): Rule.formula(derive=models.DailyFlow.request_pend [...]  
    3. Derive DailyFlow.request_processed as Count(OrderB2bRequest Where Rule.count(derive=models.DailyFlow.request_processed, as_count_of=models.OrderB2bRequest, where=lambda row: row.is_processed == True, insert_parent=True), insert_parent)  
    4. Derive DailyFlow.request_received as Count(OrderB2bRequest Where  - None, insert_parent)  
    5. Derive DailyFlow.order_amount as Sum(Order.amount_total Where  - None, insert_parent)  
    6. Derive DailyFlow.order_count as Count(Order Where  - None, insert_parent)  
  Customer  
    7. Derive Customer.balance as Sum(Order.amount_total Where Rule.sum(derive=models.Customer.balance, as_sum_of=models.Order.amount_total, where=lambda row: row.date_shipped is None))  
    8. Constraint Function: None  
  Item  
    9. Derive Item.amount as Formula (1): Rule.formula(derive=models.Item.amount, as_expres [...]  
    10. Derive Item.unit_price as Copy(product.unit_price)  
  Order  
    11. RowEvent Order._send_order_to_shipping()  
    12. Derive Order.amount_total as Sum(Item.amount Where  - None)  
```
**Logic Log** in Scenario: Raising a quantity over the credit limit is rejected (3 transactions)
```
Logic Phase:		ROW LOGIC		(session=0x10e4cf570) (sqlalchemy before_flush)			 - 2026-11-19 19:46:03,084 - logic_logger - INFO
..OrderB2bRequest[None] {Insert - client} id: None, CreatedOn: None, CreatedOnDay: None, payload: {"Account": "Bea 1795146363079", "Notes": "behave test", "Items": [{"Name": "Widget", "QuantityOrdered": 2}, {"Name": "Gadget", "QuantityOrdered": 1}]}, is_processed: False, error_text: None  row: 0x10f20c950  session: 0x10e4cf570  ins_upd_dlt: ins, initial: ins - 2026-11-19 19:46:03,084 - logic_logger - INFO
..OrderB2bRequest[None] {early_row_event_all_classes - handle_all did stamping} id: None, CreatedOn: 2026-11-19 19:46:03.084109, CreatedOnDay: 2026-11-19, payload: {"Account": "Bea 1795146363079", "Notes": "behave test", "Items": [{"Name": "Widget", "QuantityOrdered": 2}, {"Name": "Gadget", "QuantityOrdered": 1}]}, is_processed: False, error_text: None  row: 0x10f20c950  session: 0x10e4cf570  ins_upd_dlt: ins, initial: ins - 2026-11-19 19:46:03,084 - logic_logger - INFO
....DailyFlow[2026-11-19] {Update - Adjusting daily_flow: request_received} day: 2026-11-19, order_count: 38, order_amount: 11610.00, message_received: 8, message_processed: 4, message_rejected: 3, message_pending: 1, request_received:  [45-->] 46, request_processed: 36, request_rejected: 8, request_pending: 1  row: 0x10e861700  session: 0x10e4cf570  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:03,084 - logic_logger - INFO
....DailyFlow[2026-11-19] {Prune Formula: message_pending [['message_received', 'message_processed', 'message_rejected']]} day: 2026-11-19, order_count: 38, order_amount: 11610.00, message_received: 8, message_processed: 4, message_rejected: 3, message_pending: 1, request_received:  [45-->] 46, request_processed: 36, request_rejected: 8, request_pending: 1  row: 0x10e861700  session: 0x10e4cf570  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:03,084 - logic_logger - INFO
....DailyFlow[2026-11-19] {Formula request_pending} day: 2026-11-19, order_count: 38, order_amount: 11610.00, message_received: 8, message_processed: 4, message_rejected: 3, message_pending: 1, request_received:  [45-->] 46, request_processed: 36, request_rejected: 8, request_pending:  [1-->] 2  row: 0x10e861700  session: 0x10e4cf570  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:03,084 - logic_logger - INFO
Logic Phase:		COMMIT LOGIC		(session=0x10e4cf570)   										 - 2026-11-19 19:46:03,084 - logic_logger - INFO
Logic Phase:		AFTER_FLUSH LOGIC	(session=0x10e4cf570)   										 - 2026-11-19 19:46:03,085 - logic_logger - INFO


Logic Phase:		ROW LOGIC		(session=0x10e4cf570) (sqlalchemy before_flush)			 - 2026-11-19 19:46:03,087 - logic_logger - INFO
..OrderB2bRequest[152] {Update - client} id: 152, CreatedOn: 2026-11-19 19:46:03.084109, CreatedOnDay: 2026-11-19, payload: {"Account": "Bea 1795146363079", "Notes": "behave test", "Items": [{"Name": "Widget", "QuantityOrdered": 2}, {"Name": "Gadget", "QuantityOrdered": 1}]}, is_processed:  [False-->] True, error_text: None  row: 0x10f20c950  session: 0x10e4cf570  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:03,087 - logic_logger - INFO
....DailyFlow[2026-11-19] {Update - Adjusting daily_flow: request_processed} day: 2026-11-19, order_count: 38, order_amount: 11610.00, message_received: 8, message_processed: 4, message_rejected: 3, message_pending: 1, request_received: 46, request_processed:  [36-->] 37, request_rejected: 8, request_pending: 2  row: 0x10e861700  session: 0x10e4cf570  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:03,088 - logic_logger - INFO
....DailyFlow[2026-11-19] {Prune Formula: message_pending [['message_received', 'message_processed', 'message_rejected']]} day: 2026-11-19, order_count: 38, order_amount: 11610.00, message_received: 8, message_processed: 4, message_rejected: 3, message_pending: 1, request_received: 46, request_processed:  [36-->] 37, request_rejected: 8, request_pending: 2  row: 0x10e861700  session: 0x10e4cf570  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:03,088 - logic_logger - INFO
....DailyFlow[2026-11-19] {Formula request_pending} day: 2026-11-19, order_count: 38, order_amount: 11610.00, message_received: 8, message_processed: 4, message_rejected: 3, message_pending: 1, request_received: 46, request_processed:  [36-->] 37, request_rejected: 8, request_pending:  [2-->] 1  row: 0x10e861700  session: 0x10e4cf570  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:03,088 - logic_logger - INFO
..Product[1] {Update - client} id: 1, name: Gadget, count_suppliers: 0, unit_price: 150.0000000000  row: 0x10f2ab690  session: 0x10e4cf570  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:03,088 - logic_logger - INFO
..Order[None] {Insert - client} id: None, notes: behave test, customer_id: 54, CreatedOn: None, date_shipped: None, amount_total: None, CreatedOnDay: None  row: 0x10f2a7890  session: 0x10e4cf570  ins_upd_dlt: ins, initial: ins - 2026-11-19 19:46:03,088 - logic_logger - INFO
..Order[None] {early_row_event_all_classes - handle_all did stamping} id: None, notes: behave test, customer_id: 54, CreatedOn: 2026-11-19, date_shipped: None, amount_total: None, CreatedOnDay: 2026-11-19  row: 0x10f2a7890  session: 0x10e4cf570  ins_upd_dlt: ins, initial: ins - 2026-11-19 19:46:03,088 - logic_logger - INFO
..Order[None] {server aggregate_defaults: amount_total } id: None, notes: behave test, customer_id: 54, CreatedOn: 2026-11-19, date_shipped: None, amount_total: 0, CreatedOnDay: 2026-11-19  row: 0x10f2a7890  session: 0x10e4cf570  ins_upd_dlt: ins, initial: ins - 2026-11-19 19:46:03,088 - logic_logger - INFO
....DailyFlow[2026-11-19] {Update - Adjusting daily_flow: order_count} day: 2026-11-19, order_count:  [38-->] 39, order_amount: 11610.00, message_received: 8, message_processed: 4, message_rejected: 3, message_pending: 1, request_received: 46, request_processed: 37, request_rejected: 8, request_pending: 1  row: 0x10e861700  session: 0x10e4cf570  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:03,088 - logic_logger - INFO
....DailyFlow[2026-11-19] {Prune Formula: message_pending [['message_received', 'message_processed', 'message_rejected']]} day: 2026-11-19, order_count:  [38-->] 39, order_amount: 11610.00, message_received: 8, message_processed: 4, message_rejected: 3, message_pending: 1, request_received: 46, request_processed: 37, request_rejected: 8, request_pending: 1  row: 0x10e861700  session: 0x10e4cf570  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:03,088 - logic_logger - INFO
....DailyFlow[2026-11-19] {Prune Formula: request_pending [['request_received', 'request_processed', 'request_rejected']]} day: 2026-11-19, order_count:  [38-->] 39, order_amount: 11610.00, message_received: 8, message_processed: 4, message_rejected: 3, message_pending: 1, request_received: 46, request_processed: 37, request_rejected: 8, request_pending: 1  row: 0x10e861700  session: 0x10e4cf570  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:03,088 - logic_logger - INFO
..Item[None] {Insert - client} id: None, order_id: None, product_id: 2, quantity: 2, amount: None, unit_price: None  row: 0x10e82c450  session: 0x10e4cf570  ins_upd_dlt: ins, initial: ins - 2026-11-19 19:46:03,088 - logic_logger - INFO
..Item[None] {copy_rules for role: product - unit_price} id: None, order_id: None, product_id: 2, quantity: 2, amount: None, unit_price: 90.0000000000  row: 0x10e82c450  session: 0x10e4cf570  ins_upd_dlt: ins, initial: ins - 2026-11-19 19:46:03,088 - logic_logger - INFO
..Item[None] {Formula amount} id: None, order_id: None, product_id: 2, quantity: 2, amount: 180.0000000000, unit_price: 90.0000000000  row: 0x10e82c450  session: 0x10e4cf570  ins_upd_dlt: ins, initial: ins - 2026-11-19 19:46:03,088 - logic_logger - INFO
....Order[None] {Update - Adjusting order: amount_total} id: None, notes: behave test, customer_id: 54, CreatedOn: 2026-11-19, date_shipped: None, amount_total:  [0-->] 180.0000000000, CreatedOnDay: 2026-11-19  row: 0x10f2a7890  session: 0x10e4cf570  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:03,089 - logic_logger - INFO
......DailyFlow[2026-11-19] {Update - Adjusting daily_flow: order_amount} day: 2026-11-19, order_count: 39, order_amount:  [11610.00-->] 11790.0000000000, message_received: 8, message_processed: 4, message_rejected: 3, message_pending: 1, request_received: 46, request_processed: 37, request_rejected: 8, request_pending: 1  row: 0x10e861700  session: 0x10e4cf570  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:03,089 - logic_logger - INFO
......DailyFlow[2026-11-19] {Prune Formula: message_pending [['message_received', 'message_processed', 'message_rejected']]} day: 2026-11-19, order_count: 39, order_amount:  [11610.00-->] 11790.0000000000, message_received: 8, message_processed: 4, message_rejected: 3, message_pending: 1, request_received: 46, request_processed: 37, request_rejected: 8, request_pending: 1  row: 0x10e861700  session: 0x10e4cf570  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:03,089 - logic_logger - INFO
......DailyFlow[2026-11-19] {Prune Formula: request_pending [['request_received', 'request_processed', 'request_rejected']]} day: 2026-11-19, order_count: 39, order_amount:  [11610.00-->] 11790.0000000000, message_received: 8, message_processed: 4, message_rejected: 3, message_pending: 1, request_received: 46, request_processed: 37, request_rejected: 8, request_pending: 1  row: 0x10e861700  session: 0x10e4cf570  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:03,089 - logic_logger - INFO
......Customer[54] {Update - Adjusting customer: balance} id: 54, name: Bea 1795146363079, balance:  [0E-10-->] 180.0000000000, credit_limit: 500.0000000000, email: None, email_opt_out: None  row: 0x10f1ff6d0  session: 0x10e4cf570  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:03,089 - logic_logger - INFO
..Item[None] {Insert - client} id: None, order_id: None, product_id: None, quantity: 1, amount: None, unit_price: None  row: 0x10e82d650  session: 0x10e4cf570  ins_upd_dlt: ins, initial: ins - 2026-11-19 19:46:03,089 - logic_logger - INFO
..Item[None] {copy_rules for role: product - unit_price} id: None, order_id: None, product_id: None, quantity: 1, amount: None, unit_price: 150.0000000000  row: 0x10e82d650  session: 0x10e4cf570  ins_upd_dlt: ins, initial: ins - 2026-11-19 19:46:03,089 - logic_logger - INFO
..Item[None] {Formula amount} id: None, order_id: None, product_id: None, quantity: 1, amount: 150.0000000000, unit_price: 150.0000000000  row: 0x10e82d650  session: 0x10e4cf570  ins_upd_dlt: ins, initial: ins - 2026-11-19 19:46:03,089 - logic_logger - INFO
....Order[None] {Update - Adjusting order: amount_total} id: None, notes: behave test, customer_id: 54, CreatedOn: 2026-11-19, date_shipped: None, amount_total:  [180.0000000000-->] 330.0000000000, CreatedOnDay: 2026-11-19  row: 0x10f2a7890  session: 0x10e4cf570  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:03,089 - logic_logger - INFO
......DailyFlow[2026-11-19] {Update - Adjusting daily_flow: order_amount} day: 2026-11-19, order_count: 39, order_amount:  [11790.0000000000-->] 11940.0000000000, message_received: 8, message_processed: 4, message_rejected: 3, message_pending: 1, request_received: 46, request_processed: 37, request_rejected: 8, request_pending: 1  row: 0x10e861700  session: 0x10e4cf570  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:03,089 - logic_logger - INFO
......DailyFlow[2026-11-19] {Prune Formula: message_pending [['message_received', 'message_processed', 'message_rejected']]} day: 2026-11-19, order_count: 39, order_amount:  [11790.0000000000-->] 11940.0000000000, message_received: 8, message_processed: 4, message_rejected: 3, message_pending: 1, request_received: 46, request_processed: 37, request_rejected: 8, request_pending: 1  row: 0x10e861700  session: 0x10e4cf570  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:03,089 - logic_logger - INFO
......DailyFlow[2026-11-19] {Prune Formula: request_pending [['request_received', 'request_processed', 'request_rejected']]} day: 2026-11-19, order_count: 39, order_amount:  [11790.0000000000-->] 11940.0000000000, message_received: 8, message_processed: 4, message_rejected: 3, message_pending: 1, request_received: 46, request_processed: 37, request_rejected: 8, request_pending: 1  row: 0x10e861700  session: 0x10e4cf570  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:03,089 - logic_logger - INFO
......Customer[54] {Update - Adjusting customer: balance} id: 54, name: Bea 1795146363079, balance:  [180.0000000000-->] 330.0000000000, credit_limit: 500.0000000000, email: None, email_opt_out: None  row: 0x10f1ff6d0  session: 0x10e4cf570  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:03,089 - logic_logger - INFO
Logic Phase:		COMMIT LOGIC		(session=0x10e4cf570)   										 - 2026-11-19 19:46:03,089 - logic_logger - INFO
Logic Phase:		AFTER_FLUSH LOGIC	(session=0x10e4cf570)   										 - 2026-11-19 19:46:03,090 - logic_logger - INFO
..Order[228] {AfterFlush Event} id: 228, notes: behave test, customer_id: 54, CreatedOn: 2026-11-19, date_shipped: None, amount_total: 330.0000000000, CreatedOnDay: 2026-11-19  row: 0x10f2a7890  session: 0x10e4cf570  ins_upd_dlt: ins, initial: ins - 2026-11-19 19:46:03,090 - logic_logger - INFO


Logic Phase:		ROW LOGIC		(session=0x10e4cf680) (sqlalchemy before_flush)			 - 2026-11-19 19:46:03,096 - logic_logger - INFO
..Item[339] {Update - client} id: 339, order_id: 228, product_id: 2, quantity:  [2-->] 10, amount: 180.0000000000, unit_price: 90.0000000000  row: 0x10f2b9550  session: 0x10e4cf680  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:03,096 - logic_logger - INFO
..Item[339] {Formula amount} id: 339, order_id: 228, product_id: 2, quantity:  [2-->] 10, amount:  [180.0000000000-->] 900.0000000000, unit_price: 90.0000000000  row: 0x10f2b9550  session: 0x10e4cf680  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:03,096 - logic_logger - INFO
....Order[228] {Update - Adjusting order: amount_total} id: 228, notes: behave test, customer_id: 54, CreatedOn: 2026-11-19, date_shipped: None, amount_total:  [330.0000000000-->] 1050.0000000000, CreatedOnDay: 2026-11-19  row: 0x10f2a7c80  session: 0x10e4cf680  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:03,097 - logic_logger - INFO
......DailyFlow[2026-11-19] {Update - Adjusting daily_flow: order_amount} day: 2026-11-19, order_count: 39, order_amount:  [11940.00-->] 12660.0000000000, message_received: 8, message_processed: 4, message_rejected: 3, message_pending: 1, request_received: 46, request_processed: 37, request_rejected: 8, request_pending: 1  row: 0x10e861860  session: 0x10e4cf680  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:03,097 - logic_logger - INFO
......DailyFlow[2026-11-19] {Prune Formula: message_pending [['message_received', 'message_processed', 'message_rejected']]} day: 2026-11-19, order_count: 39, order_amount:  [11940.00-->] 12660.0000000000, message_received: 8, message_processed: 4, message_rejected: 3, message_pending: 1, request_received: 46, request_processed: 37, request_rejected: 8, request_pending: 1  row: 0x10e861860  session: 0x10e4cf680  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:03,097 - logic_logger - INFO
......DailyFlow[2026-11-19] {Prune Formula: request_pending [['request_received', 'request_processed', 'request_rejected']]} day: 2026-11-19, order_count: 39, order_amount:  [11940.00-->] 12660.0000000000, message_received: 8, message_processed: 4, message_rejected: 3, message_pending: 1, request_received: 46, request_processed: 37, request_rejected: 8, request_pending: 1  row: 0x10e861860  session: 0x10e4cf680  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:03,097 - logic_logger - INFO
......Customer[54] {Update - Adjusting customer: balance} id: 54, name: Bea 1795146363079, balance:  [330.0000000000-->] 1050.0000000000, credit_limit: 500.0000000000, email: None, email_opt_out: None  row: 0x10f2ca850  session: 0x10e4cf680  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:03,097 - logic_logger - INFO
......Customer[54] {Constraint Failure: Customer balance (1050.0000000000) exceeds credit limit (500.0000000000)} id: 54, name: Bea 1795146363079, balance:  [330.0000000000-->] 1050.0000000000, credit_limit: 500.0000000000, email: None, email_opt_out: None  row: 0x10f2ca850  session: 0x10e4cf680  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:03,097 - logic_logger - INFO

```
</details>

&nbsp;
&nbsp;

### Feature: Kafka Publish Shipping Notification  

&nbsp;
&nbsp;

#### Scenario: Shipping an order publishes the shipping message ✅ (0.53 s)
&emsp;  Scenario: Shipping an order publishes the shipping message  
&emsp;&emsp;    Given a new customer "Ship Cust" with credit limit 2000  
&emsp;&emsp;    And a B2B order is placed for "Ship Cust" with 2 Widget and 1 Gadget  
&emsp;&emsp;    When the order is shipped  
&emsp;&emsp;    Then an order_shipping message is published for the order  
&emsp;&emsp;    And the message has the order_shipping shape with total 330 and 2 items  

<details markdown>
<summary>Rules exercised and logic log (3 transactions)</summary>


&nbsp;
&nbsp;


**Rules Used** in Scenario: Shipping an order publishes the shipping message
```
  DailyFlow  
    1. Derive DailyFlow.request_rejected as Count(OrderB2bRequest Where Rule.count(derive=models.DailyFlow.request_rejected, as_count_of=models.OrderB2bRequest, where=lambda row: row.error_text is not None, insert_parent=True), insert_parent)  
    2. Derive DailyFlow.request_pending as Formula (2): Rule.formula(derive=models.DailyFlow.request_pend [...]  
    3. Derive DailyFlow.request_processed as Count(OrderB2bRequest Where Rule.count(derive=models.DailyFlow.request_processed, as_count_of=models.OrderB2bRequest, where=lambda row: row.is_processed == True, insert_parent=True), insert_parent)  
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
**Logic Log** in Scenario: Shipping an order publishes the shipping message (3 transactions)
```
Logic Phase:		ROW LOGIC		(session=0x10e4cebe0) (sqlalchemy before_flush)			 - 2026-11-19 19:46:03,114 - logic_logger - INFO
..OrderB2bRequest[None] {Insert - client} id: None, CreatedOn: None, CreatedOnDay: None, payload: {"Account": "Ship Cust 1795146363109", "Notes": "behave test", "Items": [{"Name": "Widget", "QuantityOrdered": 2}, {"Name": "Gadget", "QuantityOrdered": 1}]}, is_processed: False, error_text: None  row: 0x10e49ddd0  session: 0x10e4cebe0  ins_upd_dlt: ins, initial: ins - 2026-11-19 19:46:03,114 - logic_logger - INFO
..OrderB2bRequest[None] {early_row_event_all_classes - handle_all did stamping} id: None, CreatedOn: 2026-11-19 19:46:03.114171, CreatedOnDay: 2026-11-19, payload: {"Account": "Ship Cust 1795146363109", "Notes": "behave test", "Items": [{"Name": "Widget", "QuantityOrdered": 2}, {"Name": "Gadget", "QuantityOrdered": 1}]}, is_processed: False, error_text: None  row: 0x10e49ddd0  session: 0x10e4cebe0  ins_upd_dlt: ins, initial: ins - 2026-11-19 19:46:03,114 - logic_logger - INFO
....DailyFlow[2026-11-19] {Update - Adjusting daily_flow: request_received} day: 2026-11-19, order_count: 39, order_amount: 11940.00, message_received: 8, message_processed: 4, message_rejected: 3, message_pending: 1, request_received:  [46-->] 47, request_processed: 37, request_rejected: 8, request_pending: 1  row: 0x10e237b70  session: 0x10e4cebe0  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:03,114 - logic_logger - INFO
....DailyFlow[2026-11-19] {Prune Formula: message_pending [['message_received', 'message_processed', 'message_rejected']]} day: 2026-11-19, order_count: 39, order_amount: 11940.00, message_received: 8, message_processed: 4, message_rejected: 3, message_pending: 1, request_received:  [46-->] 47, request_processed: 37, request_rejected: 8, request_pending: 1  row: 0x10e237b70  session: 0x10e4cebe0  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:03,114 - logic_logger - INFO
....DailyFlow[2026-11-19] {Formula request_pending} day: 2026-11-19, order_count: 39, order_amount: 11940.00, message_received: 8, message_processed: 4, message_rejected: 3, message_pending: 1, request_received:  [46-->] 47, request_processed: 37, request_rejected: 8, request_pending:  [1-->] 2  row: 0x10e237b70  session: 0x10e4cebe0  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:03,114 - logic_logger - INFO
Logic Phase:		COMMIT LOGIC		(session=0x10e4cebe0)   										 - 2026-11-19 19:46:03,114 - logic_logger - INFO
Logic Phase:		AFTER_FLUSH LOGIC	(session=0x10e4cebe0)   										 - 2026-11-19 19:46:03,115 - logic_logger - INFO


Logic Phase:		ROW LOGIC		(session=0x10e4cebe0) (sqlalchemy before_flush)			 - 2026-11-19 19:46:03,117 - logic_logger - INFO
..Product[1] {Update - client} id: 1, name: Gadget, count_suppliers: 0, unit_price: 150.0000000000  row: 0x10f2ab4d0  session: 0x10e4cebe0  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:03,117 - logic_logger - INFO
..OrderB2bRequest[153] {Update - client} id: 153, CreatedOn: 2026-11-19 19:46:03.114171, CreatedOnDay: 2026-11-19, payload: {"Account": "Ship Cust 1795146363109", "Notes": "behave test", "Items": [{"Name": "Widget", "QuantityOrdered": 2}, {"Name": "Gadget", "QuantityOrdered": 1}]}, is_processed:  [False-->] True, error_text: None  row: 0x10e49ddd0  session: 0x10e4cebe0  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:03,117 - logic_logger - INFO
....DailyFlow[2026-11-19] {Update - Adjusting daily_flow: request_processed} day: 2026-11-19, order_count: 39, order_amount: 11940.00, message_received: 8, message_processed: 4, message_rejected: 3, message_pending: 1, request_received: 47, request_processed:  [37-->] 38, request_rejected: 8, request_pending: 2  row: 0x10e237b70  session: 0x10e4cebe0  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:03,117 - logic_logger - INFO
....DailyFlow[2026-11-19] {Prune Formula: message_pending [['message_received', 'message_processed', 'message_rejected']]} day: 2026-11-19, order_count: 39, order_amount: 11940.00, message_received: 8, message_processed: 4, message_rejected: 3, message_pending: 1, request_received: 47, request_processed:  [37-->] 38, request_rejected: 8, request_pending: 2  row: 0x10e237b70  session: 0x10e4cebe0  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:03,118 - logic_logger - INFO
....DailyFlow[2026-11-19] {Formula request_pending} day: 2026-11-19, order_count: 39, order_amount: 11940.00, message_received: 8, message_processed: 4, message_rejected: 3, message_pending: 1, request_received: 47, request_processed:  [37-->] 38, request_rejected: 8, request_pending:  [2-->] 1  row: 0x10e237b70  session: 0x10e4cebe0  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:03,118 - logic_logger - INFO
..Order[None] {Insert - client} id: None, notes: behave test, customer_id: 55, CreatedOn: None, date_shipped: None, amount_total: None, CreatedOnDay: None  row: 0x10f2a7a40  session: 0x10e4cebe0  ins_upd_dlt: ins, initial: ins - 2026-11-19 19:46:03,118 - logic_logger - INFO
..Order[None] {early_row_event_all_classes - handle_all did stamping} id: None, notes: behave test, customer_id: 55, CreatedOn: 2026-11-19, date_shipped: None, amount_total: None, CreatedOnDay: 2026-11-19  row: 0x10f2a7a40  session: 0x10e4cebe0  ins_upd_dlt: ins, initial: ins - 2026-11-19 19:46:03,118 - logic_logger - INFO
..Order[None] {server aggregate_defaults: amount_total } id: None, notes: behave test, customer_id: 55, CreatedOn: 2026-11-19, date_shipped: None, amount_total: 0, CreatedOnDay: 2026-11-19  row: 0x10f2a7a40  session: 0x10e4cebe0  ins_upd_dlt: ins, initial: ins - 2026-11-19 19:46:03,118 - logic_logger - INFO
....DailyFlow[2026-11-19] {Update - Adjusting daily_flow: order_count} day: 2026-11-19, order_count:  [39-->] 40, order_amount: 11940.00, message_received: 8, message_processed: 4, message_rejected: 3, message_pending: 1, request_received: 47, request_processed: 38, request_rejected: 8, request_pending: 1  row: 0x10e237b70  session: 0x10e4cebe0  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:03,118 - logic_logger - INFO
....DailyFlow[2026-11-19] {Prune Formula: message_pending [['message_received', 'message_processed', 'message_rejected']]} day: 2026-11-19, order_count:  [39-->] 40, order_amount: 11940.00, message_received: 8, message_processed: 4, message_rejected: 3, message_pending: 1, request_received: 47, request_processed: 38, request_rejected: 8, request_pending: 1  row: 0x10e237b70  session: 0x10e4cebe0  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:03,118 - logic_logger - INFO
....DailyFlow[2026-11-19] {Prune Formula: request_pending [['request_received', 'request_processed', 'request_rejected']]} day: 2026-11-19, order_count:  [39-->] 40, order_amount: 11940.00, message_received: 8, message_processed: 4, message_rejected: 3, message_pending: 1, request_received: 47, request_processed: 38, request_rejected: 8, request_pending: 1  row: 0x10e237b70  session: 0x10e4cebe0  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:03,118 - logic_logger - INFO
..Item[None] {Insert - client} id: None, order_id: None, product_id: 2, quantity: 2, amount: None, unit_price: None  row: 0x10f2afed0  session: 0x10e4cebe0  ins_upd_dlt: ins, initial: ins - 2026-11-19 19:46:03,118 - logic_logger - INFO
..Item[None] {copy_rules for role: product - unit_price} id: None, order_id: None, product_id: 2, quantity: 2, amount: None, unit_price: 90.0000000000  row: 0x10f2afed0  session: 0x10e4cebe0  ins_upd_dlt: ins, initial: ins - 2026-11-19 19:46:03,118 - logic_logger - INFO
..Item[None] {Formula amount} id: None, order_id: None, product_id: 2, quantity: 2, amount: 180.0000000000, unit_price: 90.0000000000  row: 0x10f2afed0  session: 0x10e4cebe0  ins_upd_dlt: ins, initial: ins - 2026-11-19 19:46:03,118 - logic_logger - INFO
....Order[None] {Update - Adjusting order: amount_total} id: None, notes: behave test, customer_id: 55, CreatedOn: 2026-11-19, date_shipped: None, amount_total:  [0-->] 180.0000000000, CreatedOnDay: 2026-11-19  row: 0x10f2a7a40  session: 0x10e4cebe0  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:03,118 - logic_logger - INFO
......DailyFlow[2026-11-19] {Update - Adjusting daily_flow: order_amount} day: 2026-11-19, order_count: 40, order_amount:  [11940.00-->] 12120.0000000000, message_received: 8, message_processed: 4, message_rejected: 3, message_pending: 1, request_received: 47, request_processed: 38, request_rejected: 8, request_pending: 1  row: 0x10e237b70  session: 0x10e4cebe0  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:03,118 - logic_logger - INFO
......DailyFlow[2026-11-19] {Prune Formula: message_pending [['message_received', 'message_processed', 'message_rejected']]} day: 2026-11-19, order_count: 40, order_amount:  [11940.00-->] 12120.0000000000, message_received: 8, message_processed: 4, message_rejected: 3, message_pending: 1, request_received: 47, request_processed: 38, request_rejected: 8, request_pending: 1  row: 0x10e237b70  session: 0x10e4cebe0  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:03,118 - logic_logger - INFO
......DailyFlow[2026-11-19] {Prune Formula: request_pending [['request_received', 'request_processed', 'request_rejected']]} day: 2026-11-19, order_count: 40, order_amount:  [11940.00-->] 12120.0000000000, message_received: 8, message_processed: 4, message_rejected: 3, message_pending: 1, request_received: 47, request_processed: 38, request_rejected: 8, request_pending: 1  row: 0x10e237b70  session: 0x10e4cebe0  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:03,118 - logic_logger - INFO
......Customer[55] {Update - Adjusting customer: balance} id: 55, name: Ship Cust 1795146363109, balance:  [0E-10-->] 180.0000000000, credit_limit: 2000.0000000000, email: None, email_opt_out: None  row: 0x10f1ff650  session: 0x10e4cebe0  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:03,119 - logic_logger - INFO
..Item[None] {Insert - client} id: None, order_id: None, product_id: None, quantity: 1, amount: None, unit_price: None  row: 0x10f2c8dd0  session: 0x10e4cebe0  ins_upd_dlt: ins, initial: ins - 2026-11-19 19:46:03,119 - logic_logger - INFO
..Item[None] {copy_rules for role: product - unit_price} id: None, order_id: None, product_id: None, quantity: 1, amount: None, unit_price: 150.0000000000  row: 0x10f2c8dd0  session: 0x10e4cebe0  ins_upd_dlt: ins, initial: ins - 2026-11-19 19:46:03,119 - logic_logger - INFO
..Item[None] {Formula amount} id: None, order_id: None, product_id: None, quantity: 1, amount: 150.0000000000, unit_price: 150.0000000000  row: 0x10f2c8dd0  session: 0x10e4cebe0  ins_upd_dlt: ins, initial: ins - 2026-11-19 19:46:03,119 - logic_logger - INFO
....Order[None] {Update - Adjusting order: amount_total} id: None, notes: behave test, customer_id: 55, CreatedOn: 2026-11-19, date_shipped: None, amount_total:  [180.0000000000-->] 330.0000000000, CreatedOnDay: 2026-11-19  row: 0x10f2a7a40  session: 0x10e4cebe0  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:03,119 - logic_logger - INFO
......DailyFlow[2026-11-19] {Update - Adjusting daily_flow: order_amount} day: 2026-11-19, order_count: 40, order_amount:  [12120.0000000000-->] 12270.0000000000, message_received: 8, message_processed: 4, message_rejected: 3, message_pending: 1, request_received: 47, request_processed: 38, request_rejected: 8, request_pending: 1  row: 0x10e237b70  session: 0x10e4cebe0  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:03,119 - logic_logger - INFO
......DailyFlow[2026-11-19] {Prune Formula: message_pending [['message_received', 'message_processed', 'message_rejected']]} day: 2026-11-19, order_count: 40, order_amount:  [12120.0000000000-->] 12270.0000000000, message_received: 8, message_processed: 4, message_rejected: 3, message_pending: 1, request_received: 47, request_processed: 38, request_rejected: 8, request_pending: 1  row: 0x10e237b70  session: 0x10e4cebe0  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:03,119 - logic_logger - INFO
......DailyFlow[2026-11-19] {Prune Formula: request_pending [['request_received', 'request_processed', 'request_rejected']]} day: 2026-11-19, order_count: 40, order_amount:  [12120.0000000000-->] 12270.0000000000, message_received: 8, message_processed: 4, message_rejected: 3, message_pending: 1, request_received: 47, request_processed: 38, request_rejected: 8, request_pending: 1  row: 0x10e237b70  session: 0x10e4cebe0  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:03,119 - logic_logger - INFO
......Customer[55] {Update - Adjusting customer: balance} id: 55, name: Ship Cust 1795146363109, balance:  [180.0000000000-->] 330.0000000000, credit_limit: 2000.0000000000, email: None, email_opt_out: None  row: 0x10f1ff650  session: 0x10e4cebe0  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:03,119 - logic_logger - INFO
Logic Phase:		COMMIT LOGIC		(session=0x10e4cebe0)   										 - 2026-11-19 19:46:03,119 - logic_logger - INFO
Logic Phase:		AFTER_FLUSH LOGIC	(session=0x10e4cebe0)   										 - 2026-11-19 19:46:03,120 - logic_logger - INFO
..Order[229] {AfterFlush Event} id: 229, notes: behave test, customer_id: 55, CreatedOn: 2026-11-19, date_shipped: None, amount_total: 330.0000000000, CreatedOnDay: 2026-11-19  row: 0x10f2a7a40  session: 0x10e4cebe0  ins_upd_dlt: ins, initial: ins - 2026-11-19 19:46:03,120 - logic_logger - INFO


Logic Phase:		ROW LOGIC		(session=0x10e4cee00) (sqlalchemy before_flush)			 - 2026-11-19 19:46:03,123 - logic_logger - INFO
..Order[229] {Update - client} id: 229, notes: behave test, customer_id: 55, CreatedOn: 2026-11-19, date_shipped:  [None-->] 2026-11-19 00:00:00, amount_total: 330.0000000000, CreatedOnDay: 2026-11-19  row: 0x10f2a7920  session: 0x10e4cee00  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:03,123 - logic_logger - INFO
....Customer[55] {Update - Adjusting customer: balance} id: 55, name: Ship Cust 1795146363109, balance:  [330.0000000000-->] 0E-10, credit_limit: 2000.0000000000, email: None, email_opt_out: None  row: 0x10f2bad50  session: 0x10e4cee00  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:03,123 - logic_logger - INFO
Logic Phase:		COMMIT LOGIC		(session=0x10e4cee00)   										 - 2026-11-19 19:46:03,123 - logic_logger - INFO
Logic Phase:		AFTER_FLUSH LOGIC	(session=0x10e4cee00)   										 - 2026-11-19 19:46:03,123 - logic_logger - INFO
..Order[229] {AfterFlush Event} id: 229, notes: behave test, customer_id: 55, CreatedOn: 2026-11-19, date_shipped:  [None-->] 2026-11-19 00:00:00, amount_total: 330.0000000000, CreatedOnDay: 2026-11-19  row: 0x10f2a7920  session: 0x10e4cee00  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:03,123 - logic_logger - INFO
..Order[229] {publish_kafka_message: topic='order_shipping', key={'id': 229}} id: 229, notes: behave test, customer_id: 55, CreatedOn: 2026-11-19, date_shipped:  [None-->] 2026-11-19 00:00:00, amount_total: 330.0000000000, CreatedOnDay: 2026-11-19  row: 0x10f2a7920  session: 0x10e4cee00  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:03,126 - logic_logger - INFO

```
</details>

&nbsp;
&nbsp;

#### Scenario: Changing an order without shipping it publishes nothing ✅ (0.54 s)
&emsp;  Scenario: Changing an order without shipping it publishes nothing  
&emsp;&emsp;    Given a new customer "Noship Cust" with credit limit 2000  
&emsp;&emsp;    And a B2B order is placed for "Noship Cust" with 1 Gadget  
&emsp;&emsp;    When the order notes are changed  
&emsp;&emsp;    Then no order_shipping message is published for the order  

<details markdown>
<summary>Rules exercised and logic log (3 transactions)</summary>


&nbsp;
&nbsp;


**Rules Used** in Scenario: Changing an order without shipping it publishes nothing
```
  DailyFlow  
    1. Derive DailyFlow.request_rejected as Count(OrderB2bRequest Where Rule.count(derive=models.DailyFlow.request_rejected, as_count_of=models.OrderB2bRequest, where=lambda row: row.error_text is not None, insert_parent=True), insert_parent)  
    2. Derive DailyFlow.request_pending as Formula (2): Rule.formula(derive=models.DailyFlow.request_pend [...]  
    3. Derive DailyFlow.request_processed as Count(OrderB2bRequest Where Rule.count(derive=models.DailyFlow.request_processed, as_count_of=models.OrderB2bRequest, where=lambda row: row.is_processed == True, insert_parent=True), insert_parent)  
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
**Logic Log** in Scenario: Changing an order without shipping it publishes nothing (3 transactions)
```
Logic Phase:		ROW LOGIC		(session=0x10e4cfac0) (sqlalchemy before_flush)			 - 2026-11-19 19:46:03,651 - logic_logger - INFO
..OrderB2bRequest[None] {Insert - client} id: None, CreatedOn: None, CreatedOnDay: None, payload: {"Account": "Noship Cust 1795146363641", "Notes": "behave test", "Items": [{"Name": "Gadget", "QuantityOrdered": 1}]}, is_processed: False, error_text: None  row: 0x10e33d550  session: 0x10e4cfac0  ins_upd_dlt: ins, initial: ins - 2026-11-19 19:46:03,651 - logic_logger - INFO
..OrderB2bRequest[None] {early_row_event_all_classes - handle_all did stamping} id: None, CreatedOn: 2026-11-19 19:46:03.651481, CreatedOnDay: 2026-11-19, payload: {"Account": "Noship Cust 1795146363641", "Notes": "behave test", "Items": [{"Name": "Gadget", "QuantityOrdered": 1}]}, is_processed: False, error_text: None  row: 0x10e33d550  session: 0x10e4cfac0  ins_upd_dlt: ins, initial: ins - 2026-11-19 19:46:03,651 - logic_logger - INFO
....DailyFlow[2026-11-19] {Update - Adjusting daily_flow: request_received} day: 2026-11-19, order_count: 40, order_amount: 12270.00, message_received: 8, message_processed: 4, message_rejected: 3, message_pending: 1, request_received:  [47-->] 48, request_processed: 38, request_rejected: 8, request_pending: 1  row: 0x10e8620a0  session: 0x10e4cfac0  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:03,652 - logic_logger - INFO
....DailyFlow[2026-11-19] {Prune Formula: message_pending [['message_received', 'message_processed', 'message_rejected']]} day: 2026-11-19, order_count: 40, order_amount: 12270.00, message_received: 8, message_processed: 4, message_rejected: 3, message_pending: 1, request_received:  [47-->] 48, request_processed: 38, request_rejected: 8, request_pending: 1  row: 0x10e8620a0  session: 0x10e4cfac0  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:03,652 - logic_logger - INFO
....DailyFlow[2026-11-19] {Formula request_pending} day: 2026-11-19, order_count: 40, order_amount: 12270.00, message_received: 8, message_processed: 4, message_rejected: 3, message_pending: 1, request_received:  [47-->] 48, request_processed: 38, request_rejected: 8, request_pending:  [1-->] 2  row: 0x10e8620a0  session: 0x10e4cfac0  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:03,652 - logic_logger - INFO
Logic Phase:		COMMIT LOGIC		(session=0x10e4cfac0)   										 - 2026-11-19 19:46:03,652 - logic_logger - INFO
Logic Phase:		AFTER_FLUSH LOGIC	(session=0x10e4cfac0)   										 - 2026-11-19 19:46:03,653 - logic_logger - INFO


Logic Phase:		ROW LOGIC		(session=0x10e4cfac0) (sqlalchemy before_flush)			 - 2026-11-19 19:46:03,656 - logic_logger - INFO
..OrderB2bRequest[154] {Update - client} id: 154, CreatedOn: 2026-11-19 19:46:03.651481, CreatedOnDay: 2026-11-19, payload: {"Account": "Noship Cust 1795146363641", "Notes": "behave test", "Items": [{"Name": "Gadget", "QuantityOrdered": 1}]}, is_processed:  [False-->] True, error_text: None  row: 0x10e33d550  session: 0x10e4cfac0  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:03,656 - logic_logger - INFO
....DailyFlow[2026-11-19] {Update - Adjusting daily_flow: request_processed} day: 2026-11-19, order_count: 40, order_amount: 12270.00, message_received: 8, message_processed: 4, message_rejected: 3, message_pending: 1, request_received: 48, request_processed:  [38-->] 39, request_rejected: 8, request_pending: 2  row: 0x10e8620a0  session: 0x10e4cfac0  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:03,656 - logic_logger - INFO
....DailyFlow[2026-11-19] {Prune Formula: message_pending [['message_received', 'message_processed', 'message_rejected']]} day: 2026-11-19, order_count: 40, order_amount: 12270.00, message_received: 8, message_processed: 4, message_rejected: 3, message_pending: 1, request_received: 48, request_processed:  [38-->] 39, request_rejected: 8, request_pending: 2  row: 0x10e8620a0  session: 0x10e4cfac0  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:03,657 - logic_logger - INFO
....DailyFlow[2026-11-19] {Formula request_pending} day: 2026-11-19, order_count: 40, order_amount: 12270.00, message_received: 8, message_processed: 4, message_rejected: 3, message_pending: 1, request_received: 48, request_processed:  [38-->] 39, request_rejected: 8, request_pending:  [2-->] 1  row: 0x10e8620a0  session: 0x10e4cfac0  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:03,657 - logic_logger - INFO
..Product[1] {Update - client} id: 1, name: Gadget, count_suppliers: 0, unit_price: 150.0000000000  row: 0x10e78bf50  session: 0x10e4cfac0  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:03,657 - logic_logger - INFO
..Order[None] {Insert - client} id: None, notes: behave test, customer_id: 56, CreatedOn: None, date_shipped: None, amount_total: None, CreatedOnDay: None  row: 0x10f2a79b0  session: 0x10e4cfac0  ins_upd_dlt: ins, initial: ins - 2026-11-19 19:46:03,657 - logic_logger - INFO
..Order[None] {early_row_event_all_classes - handle_all did stamping} id: None, notes: behave test, customer_id: 56, CreatedOn: 2026-11-19, date_shipped: None, amount_total: None, CreatedOnDay: 2026-11-19  row: 0x10f2a79b0  session: 0x10e4cfac0  ins_upd_dlt: ins, initial: ins - 2026-11-19 19:46:03,657 - logic_logger - INFO
..Order[None] {server aggregate_defaults: amount_total } id: None, notes: behave test, customer_id: 56, CreatedOn: 2026-11-19, date_shipped: None, amount_total: 0, CreatedOnDay: 2026-11-19  row: 0x10f2a79b0  session: 0x10e4cfac0  ins_upd_dlt: ins, initial: ins - 2026-11-19 19:46:03,657 - logic_logger - INFO
....DailyFlow[2026-11-19] {Update - Adjusting daily_flow: order_count} day: 2026-11-19, order_count:  [40-->] 41, order_amount: 12270.00, message_received: 8, message_processed: 4, message_rejected: 3, message_pending: 1, request_received: 48, request_processed: 39, request_rejected: 8, request_pending: 1  row: 0x10e8620a0  session: 0x10e4cfac0  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:03,657 - logic_logger - INFO
....DailyFlow[2026-11-19] {Prune Formula: message_pending [['message_received', 'message_processed', 'message_rejected']]} day: 2026-11-19, order_count:  [40-->] 41, order_amount: 12270.00, message_received: 8, message_processed: 4, message_rejected: 3, message_pending: 1, request_received: 48, request_processed: 39, request_rejected: 8, request_pending: 1  row: 0x10e8620a0  session: 0x10e4cfac0  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:03,657 - logic_logger - INFO
....DailyFlow[2026-11-19] {Prune Formula: request_pending [['request_received', 'request_processed', 'request_rejected']]} day: 2026-11-19, order_count:  [40-->] 41, order_amount: 12270.00, message_received: 8, message_processed: 4, message_rejected: 3, message_pending: 1, request_received: 48, request_processed: 39, request_rejected: 8, request_pending: 1  row: 0x10e8620a0  session: 0x10e4cfac0  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:03,657 - logic_logger - INFO
..Item[None] {Insert - client} id: None, order_id: None, product_id: None, quantity: 1, amount: None, unit_price: None  row: 0x10e3b3250  session: 0x10e4cfac0  ins_upd_dlt: ins, initial: ins - 2026-11-19 19:46:03,658 - logic_logger - INFO
..Item[None] {copy_rules for role: product - unit_price} id: None, order_id: None, product_id: None, quantity: 1, amount: None, unit_price: 150.0000000000  row: 0x10e3b3250  session: 0x10e4cfac0  ins_upd_dlt: ins, initial: ins - 2026-11-19 19:46:03,658 - logic_logger - INFO
..Item[None] {Formula amount} id: None, order_id: None, product_id: None, quantity: 1, amount: 150.0000000000, unit_price: 150.0000000000  row: 0x10e3b3250  session: 0x10e4cfac0  ins_upd_dlt: ins, initial: ins - 2026-11-19 19:46:03,658 - logic_logger - INFO
....Order[None] {Update - Adjusting order: amount_total} id: None, notes: behave test, customer_id: 56, CreatedOn: 2026-11-19, date_shipped: None, amount_total:  [0-->] 150.0000000000, CreatedOnDay: 2026-11-19  row: 0x10f2a79b0  session: 0x10e4cfac0  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:03,658 - logic_logger - INFO
......DailyFlow[2026-11-19] {Update - Adjusting daily_flow: order_amount} day: 2026-11-19, order_count: 41, order_amount:  [12270.00-->] 12420.0000000000, message_received: 8, message_processed: 4, message_rejected: 3, message_pending: 1, request_received: 48, request_processed: 39, request_rejected: 8, request_pending: 1  row: 0x10e8620a0  session: 0x10e4cfac0  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:03,658 - logic_logger - INFO
......DailyFlow[2026-11-19] {Prune Formula: message_pending [['message_received', 'message_processed', 'message_rejected']]} day: 2026-11-19, order_count: 41, order_amount:  [12270.00-->] 12420.0000000000, message_received: 8, message_processed: 4, message_rejected: 3, message_pending: 1, request_received: 48, request_processed: 39, request_rejected: 8, request_pending: 1  row: 0x10e8620a0  session: 0x10e4cfac0  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:03,658 - logic_logger - INFO
......DailyFlow[2026-11-19] {Prune Formula: request_pending [['request_received', 'request_processed', 'request_rejected']]} day: 2026-11-19, order_count: 41, order_amount:  [12270.00-->] 12420.0000000000, message_received: 8, message_processed: 4, message_rejected: 3, message_pending: 1, request_received: 48, request_processed: 39, request_rejected: 8, request_pending: 1  row: 0x10e8620a0  session: 0x10e4cfac0  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:03,658 - logic_logger - INFO
......Customer[56] {Update - Adjusting customer: balance} id: 56, name: Noship Cust 1795146363641, balance:  [0E-10-->] 150.0000000000, credit_limit: 2000.0000000000, email: None, email_opt_out: None  row: 0x10e82c9d0  session: 0x10e4cfac0  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:03,658 - logic_logger - INFO
Logic Phase:		COMMIT LOGIC		(session=0x10e4cfac0)   										 - 2026-11-19 19:46:03,658 - logic_logger - INFO
Logic Phase:		AFTER_FLUSH LOGIC	(session=0x10e4cfac0)   										 - 2026-11-19 19:46:03,659 - logic_logger - INFO
..Order[230] {AfterFlush Event} id: 230, notes: behave test, customer_id: 56, CreatedOn: 2026-11-19, date_shipped: None, amount_total: 150.0000000000, CreatedOnDay: 2026-11-19  row: 0x10f2a79b0  session: 0x10e4cfac0  ins_upd_dlt: ins, initial: ins - 2026-11-19 19:46:03,660 - logic_logger - INFO


Logic Phase:		ROW LOGIC		(session=0x10e4cfce0) (sqlalchemy before_flush)			 - 2026-11-19 19:46:03,667 - logic_logger - INFO
..Order[230] {Update - client} id: 230, notes:  [behave test-->] edited 1795146363664, customer_id: 56, CreatedOn: 2026-11-19, date_shipped: None, amount_total: 150.0000000000, CreatedOnDay: 2026-11-19  row: 0x10f2a76e0  session: 0x10e4cfce0  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:03,667 - logic_logger - INFO
Logic Phase:		COMMIT LOGIC		(session=0x10e4cfce0)   										 - 2026-11-19 19:46:03,667 - logic_logger - INFO
Logic Phase:		AFTER_FLUSH LOGIC	(session=0x10e4cfce0)   										 - 2026-11-19 19:46:03,668 - logic_logger - INFO
..Order[230] {AfterFlush Event} id: 230, notes:  [behave test-->] edited 1795146363664, customer_id: 56, CreatedOn: 2026-11-19, date_shipped: None, amount_total: 150.0000000000, CreatedOnDay: 2026-11-19  row: 0x10f2a76e0  session: 0x10e4cfce0  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:03,668 - logic_logger - INFO

```
</details>

&nbsp;
&nbsp;

#### Scenario: Changing an already shipped order does not publish again ✅ (1.1 s)
&emsp;  Scenario: Changing an already shipped order does not publish again  
&emsp;&emsp;    Given a new customer "Reship Cust" with credit limit 2000  
&emsp;&emsp;    And a B2B order is placed for "Reship Cust" with 1 Gadget  
&emsp;&emsp;    And the order is shipped  
&emsp;&emsp;    When the order notes are changed  
&emsp;&emsp;    Then exactly one order_shipping message is published for the order  

<details markdown>
<summary>Rules exercised and logic log (4 transactions)</summary>


&nbsp;
&nbsp;


**Rules Used** in Scenario: Changing an already shipped order does not publish again
```
  DailyFlow  
    1. Derive DailyFlow.request_rejected as Count(OrderB2bRequest Where Rule.count(derive=models.DailyFlow.request_rejected, as_count_of=models.OrderB2bRequest, where=lambda row: row.error_text is not None, insert_parent=True), insert_parent)  
    2. Derive DailyFlow.request_pending as Formula (2): Rule.formula(derive=models.DailyFlow.request_pend [...]  
    3. Derive DailyFlow.request_processed as Count(OrderB2bRequest Where Rule.count(derive=models.DailyFlow.request_processed, as_count_of=models.OrderB2bRequest, where=lambda row: row.is_processed == True, insert_parent=True), insert_parent)  
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
**Logic Log** in Scenario: Changing an already shipped order does not publish again (4 transactions)
```
Logic Phase:		ROW LOGIC		(session=0x10f2fc6b0) (sqlalchemy before_flush)			 - 2026-11-19 19:46:04,190 - logic_logger - INFO
..OrderB2bRequest[None] {Insert - client} id: None, CreatedOn: None, CreatedOnDay: None, payload: {"Account": "Reship Cust 1795146364181", "Notes": "behave test", "Items": [{"Name": "Gadget", "QuantityOrdered": 1}]}, is_processed: False, error_text: None  row: 0x10f20c4d0  session: 0x10f2fc6b0  ins_upd_dlt: ins, initial: ins - 2026-11-19 19:46:04,191 - logic_logger - INFO
..OrderB2bRequest[None] {early_row_event_all_classes - handle_all did stamping} id: None, CreatedOn: 2026-11-19 19:46:04.191146, CreatedOnDay: 2026-11-19, payload: {"Account": "Reship Cust 1795146364181", "Notes": "behave test", "Items": [{"Name": "Gadget", "QuantityOrdered": 1}]}, is_processed: False, error_text: None  row: 0x10f20c4d0  session: 0x10f2fc6b0  ins_upd_dlt: ins, initial: ins - 2026-11-19 19:46:04,191 - logic_logger - INFO
....DailyFlow[2026-11-19] {Update - Adjusting daily_flow: request_received} day: 2026-11-19, order_count: 41, order_amount: 12420.00, message_received: 8, message_processed: 4, message_rejected: 3, message_pending: 1, request_received:  [48-->] 49, request_processed: 39, request_rejected: 8, request_pending: 1  row: 0x10e861ff0  session: 0x10f2fc6b0  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:04,191 - logic_logger - INFO
....DailyFlow[2026-11-19] {Prune Formula: message_pending [['message_received', 'message_processed', 'message_rejected']]} day: 2026-11-19, order_count: 41, order_amount: 12420.00, message_received: 8, message_processed: 4, message_rejected: 3, message_pending: 1, request_received:  [48-->] 49, request_processed: 39, request_rejected: 8, request_pending: 1  row: 0x10e861ff0  session: 0x10f2fc6b0  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:04,192 - logic_logger - INFO
....DailyFlow[2026-11-19] {Formula request_pending} day: 2026-11-19, order_count: 41, order_amount: 12420.00, message_received: 8, message_processed: 4, message_rejected: 3, message_pending: 1, request_received:  [48-->] 49, request_processed: 39, request_rejected: 8, request_pending:  [1-->] 2  row: 0x10e861ff0  session: 0x10f2fc6b0  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:04,192 - logic_logger - INFO
Logic Phase:		COMMIT LOGIC		(session=0x10f2fc6b0)   										 - 2026-11-19 19:46:04,192 - logic_logger - INFO
Logic Phase:		AFTER_FLUSH LOGIC	(session=0x10f2fc6b0)   										 - 2026-11-19 19:46:04,192 - logic_logger - INFO


Logic Phase:		ROW LOGIC		(session=0x10f2fc6b0) (sqlalchemy before_flush)			 - 2026-11-19 19:46:04,196 - logic_logger - INFO
..Product[1] {Update - client} id: 1, name: Gadget, count_suppliers: 0, unit_price: 150.0000000000  row: 0x10f2d42f0  session: 0x10f2fc6b0  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:04,196 - logic_logger - INFO
..OrderB2bRequest[155] {Update - client} id: 155, CreatedOn: 2026-11-19 19:46:04.191146, CreatedOnDay: 2026-11-19, payload: {"Account": "Reship Cust 1795146364181", "Notes": "behave test", "Items": [{"Name": "Gadget", "QuantityOrdered": 1}]}, is_processed:  [False-->] True, error_text: None  row: 0x10f20c4d0  session: 0x10f2fc6b0  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:04,196 - logic_logger - INFO
....DailyFlow[2026-11-19] {Update - Adjusting daily_flow: request_processed} day: 2026-11-19, order_count: 41, order_amount: 12420.00, message_received: 8, message_processed: 4, message_rejected: 3, message_pending: 1, request_received: 49, request_processed:  [39-->] 40, request_rejected: 8, request_pending: 2  row: 0x10e861ff0  session: 0x10f2fc6b0  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:04,196 - logic_logger - INFO
....DailyFlow[2026-11-19] {Prune Formula: message_pending [['message_received', 'message_processed', 'message_rejected']]} day: 2026-11-19, order_count: 41, order_amount: 12420.00, message_received: 8, message_processed: 4, message_rejected: 3, message_pending: 1, request_received: 49, request_processed:  [39-->] 40, request_rejected: 8, request_pending: 2  row: 0x10e861ff0  session: 0x10f2fc6b0  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:04,197 - logic_logger - INFO
....DailyFlow[2026-11-19] {Formula request_pending} day: 2026-11-19, order_count: 41, order_amount: 12420.00, message_received: 8, message_processed: 4, message_rejected: 3, message_pending: 1, request_received: 49, request_processed:  [39-->] 40, request_rejected: 8, request_pending:  [2-->] 1  row: 0x10e861ff0  session: 0x10f2fc6b0  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:04,197 - logic_logger - INFO
..Order[None] {Insert - client} id: None, notes: behave test, customer_id: 57, CreatedOn: None, date_shipped: None, amount_total: None, CreatedOnDay: None  row: 0x10f2a7800  session: 0x10f2fc6b0  ins_upd_dlt: ins, initial: ins - 2026-11-19 19:46:04,197 - logic_logger - INFO
..Order[None] {early_row_event_all_classes - handle_all did stamping} id: None, notes: behave test, customer_id: 57, CreatedOn: 2026-11-19, date_shipped: None, amount_total: None, CreatedOnDay: 2026-11-19  row: 0x10f2a7800  session: 0x10f2fc6b0  ins_upd_dlt: ins, initial: ins - 2026-11-19 19:46:04,197 - logic_logger - INFO
..Order[None] {server aggregate_defaults: amount_total } id: None, notes: behave test, customer_id: 57, CreatedOn: 2026-11-19, date_shipped: None, amount_total: 0, CreatedOnDay: 2026-11-19  row: 0x10f2a7800  session: 0x10f2fc6b0  ins_upd_dlt: ins, initial: ins - 2026-11-19 19:46:04,197 - logic_logger - INFO
....DailyFlow[2026-11-19] {Update - Adjusting daily_flow: order_count} day: 2026-11-19, order_count:  [41-->] 42, order_amount: 12420.00, message_received: 8, message_processed: 4, message_rejected: 3, message_pending: 1, request_received: 49, request_processed: 40, request_rejected: 8, request_pending: 1  row: 0x10e861ff0  session: 0x10f2fc6b0  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:04,197 - logic_logger - INFO
....DailyFlow[2026-11-19] {Prune Formula: message_pending [['message_received', 'message_processed', 'message_rejected']]} day: 2026-11-19, order_count:  [41-->] 42, order_amount: 12420.00, message_received: 8, message_processed: 4, message_rejected: 3, message_pending: 1, request_received: 49, request_processed: 40, request_rejected: 8, request_pending: 1  row: 0x10e861ff0  session: 0x10f2fc6b0  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:04,197 - logic_logger - INFO
....DailyFlow[2026-11-19] {Prune Formula: request_pending [['request_received', 'request_processed', 'request_rejected']]} day: 2026-11-19, order_count:  [41-->] 42, order_amount: 12420.00, message_received: 8, message_processed: 4, message_rejected: 3, message_pending: 1, request_received: 49, request_processed: 40, request_rejected: 8, request_pending: 1  row: 0x10e861ff0  session: 0x10f2fc6b0  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:04,197 - logic_logger - INFO
..Item[None] {Insert - client} id: None, order_id: None, product_id: None, quantity: 1, amount: None, unit_price: None  row: 0x10e783d50  session: 0x10f2fc6b0  ins_upd_dlt: ins, initial: ins - 2026-11-19 19:46:04,197 - logic_logger - INFO
..Item[None] {copy_rules for role: product - unit_price} id: None, order_id: None, product_id: None, quantity: 1, amount: None, unit_price: 150.0000000000  row: 0x10e783d50  session: 0x10f2fc6b0  ins_upd_dlt: ins, initial: ins - 2026-11-19 19:46:04,198 - logic_logger - INFO
..Item[None] {Formula amount} id: None, order_id: None, product_id: None, quantity: 1, amount: 150.0000000000, unit_price: 150.0000000000  row: 0x10e783d50  session: 0x10f2fc6b0  ins_upd_dlt: ins, initial: ins - 2026-11-19 19:46:04,198 - logic_logger - INFO
....Order[None] {Update - Adjusting order: amount_total} id: None, notes: behave test, customer_id: 57, CreatedOn: 2026-11-19, date_shipped: None, amount_total:  [0-->] 150.0000000000, CreatedOnDay: 2026-11-19  row: 0x10f2a7800  session: 0x10f2fc6b0  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:04,198 - logic_logger - INFO
......DailyFlow[2026-11-19] {Update - Adjusting daily_flow: order_amount} day: 2026-11-19, order_count: 42, order_amount:  [12420.00-->] 12570.0000000000, message_received: 8, message_processed: 4, message_rejected: 3, message_pending: 1, request_received: 49, request_processed: 40, request_rejected: 8, request_pending: 1  row: 0x10e861ff0  session: 0x10f2fc6b0  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:04,198 - logic_logger - INFO
......DailyFlow[2026-11-19] {Prune Formula: message_pending [['message_received', 'message_processed', 'message_rejected']]} day: 2026-11-19, order_count: 42, order_amount:  [12420.00-->] 12570.0000000000, message_received: 8, message_processed: 4, message_rejected: 3, message_pending: 1, request_received: 49, request_processed: 40, request_rejected: 8, request_pending: 1  row: 0x10e861ff0  session: 0x10f2fc6b0  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:04,198 - logic_logger - INFO
......DailyFlow[2026-11-19] {Prune Formula: request_pending [['request_received', 'request_processed', 'request_rejected']]} day: 2026-11-19, order_count: 42, order_amount:  [12420.00-->] 12570.0000000000, message_received: 8, message_processed: 4, message_rejected: 3, message_pending: 1, request_received: 49, request_processed: 40, request_rejected: 8, request_pending: 1  row: 0x10e861ff0  session: 0x10f2fc6b0  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:04,198 - logic_logger - INFO
......Customer[57] {Update - Adjusting customer: balance} id: 57, name: Reship Cust 1795146364181, balance:  [0E-10-->] 150.0000000000, credit_limit: 2000.0000000000, email: None, email_opt_out: None  row: 0x10f2c8bd0  session: 0x10f2fc6b0  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:04,198 - logic_logger - INFO
Logic Phase:		COMMIT LOGIC		(session=0x10f2fc6b0)   										 - 2026-11-19 19:46:04,198 - logic_logger - INFO
Logic Phase:		AFTER_FLUSH LOGIC	(session=0x10f2fc6b0)   										 - 2026-11-19 19:46:04,199 - logic_logger - INFO
..Order[231] {AfterFlush Event} id: 231, notes: behave test, customer_id: 57, CreatedOn: 2026-11-19, date_shipped: None, amount_total: 150.0000000000, CreatedOnDay: 2026-11-19  row: 0x10f2a7800  session: 0x10f2fc6b0  ins_upd_dlt: ins, initial: ins - 2026-11-19 19:46:04,200 - logic_logger - INFO


Logic Phase:		ROW LOGIC		(session=0x10f2fc380) (sqlalchemy before_flush)			 - 2026-11-19 19:46:04,204 - logic_logger - INFO
..Order[231] {Update - client} id: 231, notes: behave test, customer_id: 57, CreatedOn: 2026-11-19, date_shipped:  [None-->] 2026-11-19 00:00:00, amount_total: 150.0000000000, CreatedOnDay: 2026-11-19  row: 0x10f2a7530  session: 0x10f2fc380  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:04,205 - logic_logger - INFO
....Customer[57] {Update - Adjusting customer: balance} id: 57, name: Reship Cust 1795146364181, balance:  [150.0000000000-->] 0E-10, credit_limit: 2000.0000000000, email: None, email_opt_out: None  row: 0x10f30ecd0  session: 0x10f2fc380  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:04,205 - logic_logger - INFO
Logic Phase:		COMMIT LOGIC		(session=0x10f2fc380)   										 - 2026-11-19 19:46:04,205 - logic_logger - INFO
Logic Phase:		AFTER_FLUSH LOGIC	(session=0x10f2fc380)   										 - 2026-11-19 19:46:04,206 - logic_logger - INFO
..Order[231] {AfterFlush Event} id: 231, notes: behave test, customer_id: 57, CreatedOn: 2026-11-19, date_shipped:  [None-->] 2026-11-19 00:00:00, amount_total: 150.0000000000, CreatedOnDay: 2026-11-19  row: 0x10f2a7530  session: 0x10f2fc380  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:04,206 - logic_logger - INFO
..Order[231] {publish_kafka_message: topic='order_shipping', key={'id': 231}} id: 231, notes: behave test, customer_id: 57, CreatedOn: 2026-11-19, date_shipped:  [None-->] 2026-11-19 00:00:00, amount_total: 150.0000000000, CreatedOnDay: 2026-11-19  row: 0x10f2a7530  session: 0x10f2fc380  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:04,209 - logic_logger - INFO


Logic Phase:		ROW LOGIC		(session=0x10e433df0) (sqlalchemy before_flush)			 - 2026-11-19 19:46:04,720 - logic_logger - INFO
..Order[231] {Update - client} id: 231, notes:  [behave test-->] edited 1795146364717, customer_id: 57, CreatedOn: 2026-11-19, date_shipped: 2026-11-19, amount_total: 150.0000000000, CreatedOnDay: 2026-11-19  row: 0x10f2a7800  session: 0x10e433df0  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:04,720 - logic_logger - INFO
Logic Phase:		COMMIT LOGIC		(session=0x10e433df0)   										 - 2026-11-19 19:46:04,720 - logic_logger - INFO
Logic Phase:		AFTER_FLUSH LOGIC	(session=0x10e433df0)   										 - 2026-11-19 19:46:04,721 - logic_logger - INFO
..Order[231] {AfterFlush Event} id: 231, notes:  [behave test-->] edited 1795146364717, customer_id: 57, CreatedOn: 2026-11-19, date_shipped: 2026-11-19, amount_total: 150.0000000000, CreatedOnDay: 2026-11-19  row: 0x10f2a7800  session: 0x10e433df0  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:04,721 - logic_logger - INFO

```
</details>

&nbsp;
&nbsp;

### Feature: Kafka Subscribe Order Integration  

&nbsp;
&nbsp;

#### Scenario: Order message for a known customer creates the order ✅ (0.56 s)
&emsp;  Scenario: Order message for a known customer creates the order  
&emsp;&emsp;    Given a new customer "Kafka Cust" with credit limit 5000  
&emsp;&emsp;    When an order message for "Kafka Cust" with 1 Widget and 2 Gadget is delivered to topic order_b2b  
&emsp;&emsp;    Then the message is processed  
&emsp;&emsp;    And "Kafka Cust" has one order with total 390  
&emsp;&emsp;    And the order items are 1 Widget and 2 Gadget  

<details markdown>
<summary>Rules exercised and logic log (3 transactions)</summary>


&nbsp;
&nbsp;


**Rules Used** in Scenario: Order message for a known customer creates the order
```
  DailyFlow  
    1. Derive DailyFlow.message_rejected as Count(OrderB2bMessage Where Rule.count(derive=models.DailyFlow.message_rejected, as_count_of=models.OrderB2bMessage, where=lambda row: row.error_text is not None, insert_parent=True), insert_parent)  
    2. Derive DailyFlow.message_received as Count(OrderB2bMessage Where  - None, insert_parent)  
    3. Derive DailyFlow.message_pending as Formula (1): Rule.formula(derive=models.DailyFlow.message_pend [...]  
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
**Logic Log** in Scenario: Order message for a known customer creates the order (3 transactions)
```
Logic Phase:		ROW LOGIC		(session=0x10e4cee00) (sqlalchemy before_flush)			 - 2026-11-19 19:46:05,251 - logic_logger - INFO
..OrderB2bMessage[None] {Insert - client} id: None, CreatedOn: None, CreatedOnDay: None, payload: {..., is_processed: False, error_text: None  row: 0x10e53f2d0  session: 0x10e4cee00  ins_upd_dlt: ins, initial: ins - 2026-11-19 19:46:05,252 - logic_logger - INFO
..OrderB2bMessage[None] {early_row_event_all_classes - handle_all did stamping} id: None, CreatedOn: 2026-11-19 19:46:05.254975, CreatedOnDay: 2026-11-19, payload: {..., is_processed: False, error_text: None  row: 0x10e53f2d0  session: 0x10e4cee00  ins_upd_dlt: ins, initial: ins - 2026-11-19 19:46:05,255 - logic_logger - INFO
....DailyFlow[2026-11-19] {Update - Adjusting daily_flow: message_received} day: 2026-11-19, order_count: 42, order_amount: 12570.00, message_received:  [8-->] 9, message_processed: 4, message_rejected: 3, message_pending: 1, request_received: 49, request_processed: 40, request_rejected: 8, request_pending: 1  row: 0x10e861ff0  session: 0x10e4cee00  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:05,256 - logic_logger - INFO
....DailyFlow[2026-11-19] {Formula message_pending} day: 2026-11-19, order_count: 42, order_amount: 12570.00, message_received:  [8-->] 9, message_processed: 4, message_rejected: 3, message_pending:  [1-->] 2, request_received: 49, request_processed: 40, request_rejected: 8, request_pending: 1  row: 0x10e861ff0  session: 0x10e4cee00  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:05,259 - logic_logger - INFO
....DailyFlow[2026-11-19] {Prune Formula: request_pending [['request_received', 'request_processed', 'request_rejected']]} day: 2026-11-19, order_count: 42, order_amount: 12570.00, message_received:  [8-->] 9, message_processed: 4, message_rejected: 3, message_pending:  [1-->] 2, request_received: 49, request_processed: 40, request_rejected: 8, request_pending: 1  row: 0x10e861ff0  session: 0x10e4cee00  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:05,259 - logic_logger - INFO
Logic Phase:		COMMIT LOGIC		(session=0x10e4cee00)   										 - 2026-11-19 19:46:05,259 - logic_logger - INFO
Logic Phase:		AFTER_FLUSH LOGIC	(session=0x10e4cee00)   										 - 2026-11-19 19:46:05,261 - logic_logger - INFO
..OrderB2bMessage[93] {AfterFlush Event} id: 93, CreatedOn: 2026-11-19 19:46:05.254975, CreatedOnDay: 2026-11-19, payload: {..., is_processed: False, error_text: None  row: 0x10e53f2d0  session: 0x10e4cee00  ins_upd_dlt: ins, initial: ins - 2026-11-19 19:46:05,261 - logic_logger - INFO


Logic Phase:		ROW LOGIC		(session=0x10e4ce470) (sqlalchemy before_flush)			 - 2026-11-19 19:46:05,268 - logic_logger - INFO
..Order[None] {Insert - client} id: None, notes: behave kafka message, customer_id: 58, CreatedOn: None, date_shipped: None, amount_total: None, CreatedOnDay: None  row: 0x10f2d9c70  session: 0x10e4ce470  ins_upd_dlt: ins, initial: ins - 2026-11-19 19:46:05,268 - logic_logger - INFO
..Order[None] {early_row_event_all_classes - handle_all did stamping} id: None, notes: behave kafka message, customer_id: 58, CreatedOn: 2026-11-19, date_shipped: None, amount_total: None, CreatedOnDay: 2026-11-19  row: 0x10f2d9c70  session: 0x10e4ce470  ins_upd_dlt: ins, initial: ins - 2026-11-19 19:46:05,269 - logic_logger - INFO
..Order[None] {server aggregate_defaults: amount_total } id: None, notes: behave kafka message, customer_id: 58, CreatedOn: 2026-11-19, date_shipped: None, amount_total: 0, CreatedOnDay: 2026-11-19  row: 0x10f2d9c70  session: 0x10e4ce470  ins_upd_dlt: ins, initial: ins - 2026-11-19 19:46:05,269 - logic_logger - INFO
....DailyFlow[2026-11-19] {Update - Adjusting daily_flow: order_count} day: 2026-11-19, order_count:  [42-->] 43, order_amount: 12570.00, message_received: 9, message_processed: 4, message_rejected: 3, message_pending: 2, request_received: 49, request_processed: 40, request_rejected: 8, request_pending: 1  row: 0x10e8615a0  session: 0x10e4ce470  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:05,269 - logic_logger - INFO
....DailyFlow[2026-11-19] {Prune Formula: message_pending [['message_received', 'message_processed', 'message_rejected']]} day: 2026-11-19, order_count:  [42-->] 43, order_amount: 12570.00, message_received: 9, message_processed: 4, message_rejected: 3, message_pending: 2, request_received: 49, request_processed: 40, request_rejected: 8, request_pending: 1  row: 0x10e8615a0  session: 0x10e4ce470  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:05,269 - logic_logger - INFO
....DailyFlow[2026-11-19] {Prune Formula: request_pending [['request_received', 'request_processed', 'request_rejected']]} day: 2026-11-19, order_count:  [42-->] 43, order_amount: 12570.00, message_received: 9, message_processed: 4, message_rejected: 3, message_pending: 2, request_received: 49, request_processed: 40, request_rejected: 8, request_pending: 1  row: 0x10e8615a0  session: 0x10e4ce470  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:05,269 - logic_logger - INFO
..Item[None] {Insert - client} id: None, order_id: None, product_id: 2, quantity: 1, amount: None, unit_price: None  row: 0x10e2def50  session: 0x10e4ce470  ins_upd_dlt: ins, initial: ins - 2026-11-19 19:46:05,270 - logic_logger - INFO
..Item[None] {copy_rules for role: product - unit_price} id: None, order_id: None, product_id: 2, quantity: 1, amount: None, unit_price: 90.0000000000  row: 0x10e2def50  session: 0x10e4ce470  ins_upd_dlt: ins, initial: ins - 2026-11-19 19:46:05,270 - logic_logger - INFO
..Item[None] {Formula amount} id: None, order_id: None, product_id: 2, quantity: 1, amount: 90.0000000000, unit_price: 90.0000000000  row: 0x10e2def50  session: 0x10e4ce470  ins_upd_dlt: ins, initial: ins - 2026-11-19 19:46:05,270 - logic_logger - INFO
....Order[None] {Update - Adjusting order: amount_total} id: None, notes: behave kafka message, customer_id: 58, CreatedOn: 2026-11-19, date_shipped: None, amount_total:  [0-->] 90.0000000000, CreatedOnDay: 2026-11-19  row: 0x10f2d9c70  session: 0x10e4ce470  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:05,270 - logic_logger - INFO
......DailyFlow[2026-11-19] {Update - Adjusting daily_flow: order_amount} day: 2026-11-19, order_count: 43, order_amount:  [12570.00-->] 12660.0000000000, message_received: 9, message_processed: 4, message_rejected: 3, message_pending: 2, request_received: 49, request_processed: 40, request_rejected: 8, request_pending: 1  row: 0x10e8615a0  session: 0x10e4ce470  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:05,270 - logic_logger - INFO
......DailyFlow[2026-11-19] {Prune Formula: message_pending [['message_received', 'message_processed', 'message_rejected']]} day: 2026-11-19, order_count: 43, order_amount:  [12570.00-->] 12660.0000000000, message_received: 9, message_processed: 4, message_rejected: 3, message_pending: 2, request_received: 49, request_processed: 40, request_rejected: 8, request_pending: 1  row: 0x10e8615a0  session: 0x10e4ce470  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:05,271 - logic_logger - INFO
......DailyFlow[2026-11-19] {Prune Formula: request_pending [['request_received', 'request_processed', 'request_rejected']]} day: 2026-11-19, order_count: 43, order_amount:  [12570.00-->] 12660.0000000000, message_received: 9, message_processed: 4, message_rejected: 3, message_pending: 2, request_received: 49, request_processed: 40, request_rejected: 8, request_pending: 1  row: 0x10e8615a0  session: 0x10e4ce470  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:05,271 - logic_logger - INFO
......Customer[58] {Update - Adjusting customer: balance} id: 58, name: Kafka Cust 1795146365236, balance:  [0E-10-->] 90.0000000000, credit_limit: 5000.0000000000, email: None, email_opt_out: None  row: 0x10f1fd250  session: 0x10e4ce470  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:05,271 - logic_logger - INFO
..Item[None] {Insert - client} id: None, order_id: None, product_id: 1, quantity: 2, amount: None, unit_price: None  row: 0x10f20c2d0  session: 0x10e4ce470  ins_upd_dlt: ins, initial: ins - 2026-11-19 19:46:05,271 - logic_logger - INFO
..Item[None] {copy_rules for role: product - unit_price} id: None, order_id: None, product_id: 1, quantity: 2, amount: None, unit_price: 150.0000000000  row: 0x10f20c2d0  session: 0x10e4ce470  ins_upd_dlt: ins, initial: ins - 2026-11-19 19:46:05,271 - logic_logger - INFO
..Item[None] {Formula amount} id: None, order_id: None, product_id: 1, quantity: 2, amount: 300.0000000000, unit_price: 150.0000000000  row: 0x10f20c2d0  session: 0x10e4ce470  ins_upd_dlt: ins, initial: ins - 2026-11-19 19:46:05,271 - logic_logger - INFO
....Order[None] {Update - Adjusting order: amount_total} id: None, notes: behave kafka message, customer_id: 58, CreatedOn: 2026-11-19, date_shipped: None, amount_total:  [90.0000000000-->] 390.0000000000, CreatedOnDay: 2026-11-19  row: 0x10f2d9c70  session: 0x10e4ce470  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:05,271 - logic_logger - INFO
......DailyFlow[2026-11-19] {Update - Adjusting daily_flow: order_amount} day: 2026-11-19, order_count: 43, order_amount:  [12660.0000000000-->] 12960.0000000000, message_received: 9, message_processed: 4, message_rejected: 3, message_pending: 2, request_received: 49, request_processed: 40, request_rejected: 8, request_pending: 1  row: 0x10e8615a0  session: 0x10e4ce470  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:05,272 - logic_logger - INFO
......DailyFlow[2026-11-19] {Prune Formula: message_pending [['message_received', 'message_processed', 'message_rejected']]} day: 2026-11-19, order_count: 43, order_amount:  [12660.0000000000-->] 12960.0000000000, message_received: 9, message_processed: 4, message_rejected: 3, message_pending: 2, request_received: 49, request_processed: 40, request_rejected: 8, request_pending: 1  row: 0x10e8615a0  session: 0x10e4ce470  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:05,272 - logic_logger - INFO
......DailyFlow[2026-11-19] {Prune Formula: request_pending [['request_received', 'request_processed', 'request_rejected']]} day: 2026-11-19, order_count: 43, order_amount:  [12660.0000000000-->] 12960.0000000000, message_received: 9, message_processed: 4, message_rejected: 3, message_pending: 2, request_received: 49, request_processed: 40, request_rejected: 8, request_pending: 1  row: 0x10e8615a0  session: 0x10e4ce470  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:05,272 - logic_logger - INFO
......Customer[58] {Update - Adjusting customer: balance} id: 58, name: Kafka Cust 1795146365236, balance:  [90.0000000000-->] 390.0000000000, credit_limit: 5000.0000000000, email: None, email_opt_out: None  row: 0x10f1fd250  session: 0x10e4ce470  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:05,272 - logic_logger - INFO
Logic Phase:		COMMIT LOGIC		(session=0x10e4ce470)   										 - 2026-11-19 19:46:05,272 - logic_logger - INFO
Logic Phase:		AFTER_FLUSH LOGIC	(session=0x10e4ce470)   										 - 2026-11-19 19:46:05,273 - logic_logger - INFO
..Order[232] {AfterFlush Event} id: 232, notes: behave kafka message, customer_id: 58, CreatedOn: 2026-11-19, date_shipped: None, amount_total: 390.0000000000, CreatedOnDay: 2026-11-19  row: 0x10f2d9c70  session: 0x10e4ce470  ins_upd_dlt: ins, initial: ins - 2026-11-19 19:46:05,273 - logic_logger - INFO


Logic Phase:		ROW LOGIC		(session=0x10e4ce470) (sqlalchemy before_flush)			 - 2026-11-19 19:46:05,274 - logic_logger - INFO
..OrderB2bMessage[93] {Update - client} id: 93, CreatedOn: 2026-11-19 19:46:05.254975, CreatedOnDay: 2026-11-19, payload: {..., is_processed:  [False-->] True, error_text: None  row: 0x10f2b9350  session: 0x10e4ce470  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:05,274 - logic_logger - INFO
....DailyFlow[2026-11-19] {Update - Adjusting daily_flow: message_processed} day: 2026-11-19, order_count: 43, order_amount: 12960.0000000000, message_received: 9, message_processed:  [4-->] 5, message_rejected: 3, message_pending: 2, request_received: 49, request_processed: 40, request_rejected: 8, request_pending: 1  row: 0x10e8615a0  session: 0x10e4ce470  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:05,274 - logic_logger - INFO
....DailyFlow[2026-11-19] {Formula message_pending} day: 2026-11-19, order_count: 43, order_amount: 12960.0000000000, message_received: 9, message_processed:  [4-->] 5, message_rejected: 3, message_pending:  [2-->] 1, request_received: 49, request_processed: 40, request_rejected: 8, request_pending: 1  row: 0x10e8615a0  session: 0x10e4ce470  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:05,274 - logic_logger - INFO
....DailyFlow[2026-11-19] {Prune Formula: request_pending [['request_received', 'request_processed', 'request_rejected']]} day: 2026-11-19, order_count: 43, order_amount: 12960.0000000000, message_received: 9, message_processed:  [4-->] 5, message_rejected: 3, message_pending:  [2-->] 1, request_received: 49, request_processed: 40, request_rejected: 8, request_pending: 1  row: 0x10e8615a0  session: 0x10e4ce470  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:05,274 - logic_logger - INFO
Logic Phase:		COMMIT LOGIC		(session=0x10e4ce470)   										 - 2026-11-19 19:46:05,274 - logic_logger - INFO
Logic Phase:		AFTER_FLUSH LOGIC	(session=0x10e4ce470)   										 - 2026-11-19 19:46:05,275 - logic_logger - INFO
..OrderB2bMessage[93] {AfterFlush Event} id: 93, CreatedOn: 2026-11-19 19:46:05.254975, CreatedOnDay: 2026-11-19, payload: {..., is_processed:  [False-->] True, error_text: None  row: 0x10f2b9350  session: 0x10e4ce470  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:05,275 - logic_logger - INFO

```
</details>

&nbsp;
&nbsp;

#### Scenario: Order message with an unknown product is rejected ✅ (0.55 s)
&emsp;  Scenario: Order message with an unknown product is rejected  
&emsp;&emsp;    Given a new customer "Kafka Bad" with credit limit 5000  
&emsp;&emsp;    When an order message for "Kafka Bad" with 1 Sprocket is delivered to topic order_b2b  
&emsp;&emsp;    Then the message is rejected with "Product"  
&emsp;&emsp;    And "Kafka Bad" has no orders  

<details markdown>
<summary>Rules exercised and logic log (2 transactions)</summary>


&nbsp;
&nbsp;


**Rules Used** in Scenario: Order message with an unknown product is rejected
```
  DailyFlow  
    1. Derive DailyFlow.message_rejected as Count(OrderB2bMessage Where Rule.count(derive=models.DailyFlow.message_rejected, as_count_of=models.OrderB2bMessage, where=lambda row: row.error_text is not None, insert_parent=True), insert_parent)  
    2. Derive DailyFlow.message_received as Count(OrderB2bMessage Where  - None, insert_parent)  
    3. Derive DailyFlow.message_pending as Formula (1): Rule.formula(derive=models.DailyFlow.message_pend [...]  
    4. Derive DailyFlow.message_processed as Count(OrderB2bMessage Where Rule.count(derive=models.DailyFlow.message_processed, as_count_of=models.OrderB2bMessage, where=lambda row: row.is_processed == True, insert_parent=True), insert_parent)  
  OrderB2bMessage  
    5. RowEvent OrderB2bMessage._publish_order_b2b()  
```
**Logic Log** in Scenario: Order message with an unknown product is rejected (2 transactions)
```
Logic Phase:		ROW LOGIC		(session=0x10e4cf8a0) (sqlalchemy before_flush)			 - 2026-11-19 19:46:05,810 - logic_logger - INFO
..OrderB2bMessage[None] {Insert - client} id: None, CreatedOn: None, CreatedOnDay: None, payload: {..., is_processed: False, error_text: None  row: 0x10e3b3250  session: 0x10e4cf8a0  ins_upd_dlt: ins, initial: ins - 2026-11-19 19:46:05,810 - logic_logger - INFO
..OrderB2bMessage[None] {early_row_event_all_classes - handle_all did stamping} id: None, CreatedOn: 2026-11-19 19:46:05.810435, CreatedOnDay: 2026-11-19, payload: {..., is_processed: False, error_text: None  row: 0x10e3b3250  session: 0x10e4cf8a0  ins_upd_dlt: ins, initial: ins - 2026-11-19 19:46:05,810 - logic_logger - INFO
....DailyFlow[2026-11-19] {Update - Adjusting daily_flow: message_received} day: 2026-11-19, order_count: 43, order_amount: 12960.00, message_received:  [9-->] 10, message_processed: 5, message_rejected: 3, message_pending: 1, request_received: 49, request_processed: 40, request_rejected: 8, request_pending: 1  row: 0x10df795a0  session: 0x10e4cf8a0  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:05,811 - logic_logger - INFO
....DailyFlow[2026-11-19] {Formula message_pending} day: 2026-11-19, order_count: 43, order_amount: 12960.00, message_received:  [9-->] 10, message_processed: 5, message_rejected: 3, message_pending:  [1-->] 2, request_received: 49, request_processed: 40, request_rejected: 8, request_pending: 1  row: 0x10df795a0  session: 0x10e4cf8a0  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:05,811 - logic_logger - INFO
....DailyFlow[2026-11-19] {Prune Formula: request_pending [['request_received', 'request_processed', 'request_rejected']]} day: 2026-11-19, order_count: 43, order_amount: 12960.00, message_received:  [9-->] 10, message_processed: 5, message_rejected: 3, message_pending:  [1-->] 2, request_received: 49, request_processed: 40, request_rejected: 8, request_pending: 1  row: 0x10df795a0  session: 0x10e4cf8a0  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:05,811 - logic_logger - INFO
Logic Phase:		COMMIT LOGIC		(session=0x10e4cf8a0)   										 - 2026-11-19 19:46:05,812 - logic_logger - INFO
Logic Phase:		AFTER_FLUSH LOGIC	(session=0x10e4cf8a0)   										 - 2026-11-19 19:46:05,816 - logic_logger - INFO
..OrderB2bMessage[94] {AfterFlush Event} id: 94, CreatedOn: 2026-11-19 19:46:05.810435, CreatedOnDay: 2026-11-19, payload: {..., is_processed: False, error_text: None  row: 0x10e3b3250  session: 0x10e4cf8a0  ins_upd_dlt: ins, initial: ins - 2026-11-19 19:46:05,816 - logic_logger - INFO


Logic Phase:		ROW LOGIC		(session=0x10e433df0) (sqlalchemy before_flush)			 - 2026-11-19 19:46:05,822 - logic_logger - INFO
..OrderB2bMessage[94] {Update - client} id: 94, CreatedOn: 2026-11-19 19:46:05.810435, CreatedOnDay: 2026-11-19, payload: {..., is_processed: False, error_text:  [None-->] resolve_lookups: no Product found for fk_col='product_id' from source fields  row: 0x10f2c9150  session: 0x10e433df0  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:05,822 - logic_logger - INFO
....DailyFlow[2026-11-19] {Update - Adjusting daily_flow: message_rejected} day: 2026-11-19, order_count: 43, order_amount: 12960.00, message_received: 10, message_processed: 5, message_rejected:  [3-->] 4, message_pending: 2, request_received: 49, request_processed: 40, request_rejected: 8, request_pending: 1  row: 0x10e861910  session: 0x10e433df0  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:05,822 - logic_logger - INFO
....DailyFlow[2026-11-19] {Formula message_pending} day: 2026-11-19, order_count: 43, order_amount: 12960.00, message_received: 10, message_processed: 5, message_rejected:  [3-->] 4, message_pending:  [2-->] 1, request_received: 49, request_processed: 40, request_rejected: 8, request_pending: 1  row: 0x10e861910  session: 0x10e433df0  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:05,823 - logic_logger - INFO
....DailyFlow[2026-11-19] {Prune Formula: request_pending [['request_received', 'request_processed', 'request_rejected']]} day: 2026-11-19, order_count: 43, order_amount: 12960.00, message_received: 10, message_processed: 5, message_rejected:  [3-->] 4, message_pending:  [2-->] 1, request_received: 49, request_processed: 40, request_rejected: 8, request_pending: 1  row: 0x10e861910  session: 0x10e433df0  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:05,823 - logic_logger - INFO
Logic Phase:		COMMIT LOGIC		(session=0x10e433df0)   										 - 2026-11-19 19:46:05,823 - logic_logger - INFO
Logic Phase:		AFTER_FLUSH LOGIC	(session=0x10e433df0)   										 - 2026-11-19 19:46:05,823 - logic_logger - INFO
..OrderB2bMessage[94] {AfterFlush Event} id: 94, CreatedOn: 2026-11-19 19:46:05.810435, CreatedOnDay: 2026-11-19, payload: {..., is_processed: False, error_text:  [None-->] resolve_lookups: no Product found for fk_col='product_id' from source fields  row: 0x10f2c9150  session: 0x10e433df0  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:05,823 - logic_logger - INFO

```
</details>

&nbsp;
&nbsp;

#### Scenario: Rejected message stays on the blob with its error (live Kafka only) ✅ (0.55 s)
&emsp;  Scenario: Rejected message stays on the blob with its error (live Kafka only)  
&emsp;&emsp;    Given a new customer "Kafka Live Bad" with credit limit 5000  
&emsp;&emsp;    When an order message for "Kafka Live Bad" with 1 Sprocket is delivered live to topic order_b2b  
&emsp;&emsp;    Then the message blob is not processed and has error text  

<details markdown>
<summary>Rules exercised and logic log (2 transactions)</summary>


&nbsp;
&nbsp;


**Rules Used** in Scenario: Rejected message stays on the blob with its error (live Kafka only)
```
  DailyFlow  
    1. Derive DailyFlow.message_rejected as Count(OrderB2bMessage Where Rule.count(derive=models.DailyFlow.message_rejected, as_count_of=models.OrderB2bMessage, where=lambda row: row.error_text is not None, insert_parent=True), insert_parent)  
    2. Derive DailyFlow.message_received as Count(OrderB2bMessage Where  - None, insert_parent)  
    3. Derive DailyFlow.message_pending as Formula (1): Rule.formula(derive=models.DailyFlow.message_pend [...]  
    4. Derive DailyFlow.message_processed as Count(OrderB2bMessage Where Rule.count(derive=models.DailyFlow.message_processed, as_count_of=models.OrderB2bMessage, where=lambda row: row.is_processed == True, insert_parent=True), insert_parent)  
  OrderB2bMessage  
    5. RowEvent OrderB2bMessage._publish_order_b2b()  
```
**Logic Log** in Scenario: Rejected message stays on the blob with its error (live Kafka only) (2 transactions)
```
Logic Phase:		ROW LOGIC		(session=0x10e4cdf20) (sqlalchemy before_flush)			 - 2026-11-19 19:46:06,358 - logic_logger - INFO
..OrderB2bMessage[None] {Insert - client} id: None, CreatedOn: None, CreatedOnDay: None, payload: {..., is_processed: False, error_text: None  row: 0x10e2c6c50  session: 0x10e4cdf20  ins_upd_dlt: ins, initial: ins - 2026-11-19 19:46:06,358 - logic_logger - INFO
..OrderB2bMessage[None] {early_row_event_all_classes - handle_all did stamping} id: None, CreatedOn: 2026-11-19 19:46:06.358772, CreatedOnDay: 2026-11-19, payload: {..., is_processed: False, error_text: None  row: 0x10e2c6c50  session: 0x10e4cdf20  ins_upd_dlt: ins, initial: ins - 2026-11-19 19:46:06,358 - logic_logger - INFO
....DailyFlow[2026-11-19] {Update - Adjusting daily_flow: message_received} day: 2026-11-19, order_count: 43, order_amount: 12960.00, message_received:  [10-->] 11, message_processed: 5, message_rejected: 4, message_pending: 1, request_received: 49, request_processed: 40, request_rejected: 8, request_pending: 1  row: 0x10e862360  session: 0x10e4cdf20  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:06,359 - logic_logger - INFO
....DailyFlow[2026-11-19] {Formula message_pending} day: 2026-11-19, order_count: 43, order_amount: 12960.00, message_received:  [10-->] 11, message_processed: 5, message_rejected: 4, message_pending:  [1-->] 2, request_received: 49, request_processed: 40, request_rejected: 8, request_pending: 1  row: 0x10e862360  session: 0x10e4cdf20  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:06,360 - logic_logger - INFO
....DailyFlow[2026-11-19] {Prune Formula: request_pending [['request_received', 'request_processed', 'request_rejected']]} day: 2026-11-19, order_count: 43, order_amount: 12960.00, message_received:  [10-->] 11, message_processed: 5, message_rejected: 4, message_pending:  [1-->] 2, request_received: 49, request_processed: 40, request_rejected: 8, request_pending: 1  row: 0x10e862360  session: 0x10e4cdf20  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:06,362 - logic_logger - INFO
Logic Phase:		COMMIT LOGIC		(session=0x10e4cdf20)   										 - 2026-11-19 19:46:06,362 - logic_logger - INFO
Logic Phase:		AFTER_FLUSH LOGIC	(session=0x10e4cdf20)   										 - 2026-11-19 19:46:06,365 - logic_logger - INFO
..OrderB2bMessage[95] {AfterFlush Event} id: 95, CreatedOn: 2026-11-19 19:46:06.358772, CreatedOnDay: 2026-11-19, payload: {..., is_processed: False, error_text: None  row: 0x10e2c6c50  session: 0x10e4cdf20  ins_upd_dlt: ins, initial: ins - 2026-11-19 19:46:06,365 - logic_logger - INFO


Logic Phase:		ROW LOGIC		(session=0x10e433df0) (sqlalchemy before_flush)			 - 2026-11-19 19:46:06,371 - logic_logger - INFO
..OrderB2bMessage[95] {Update - client} id: 95, CreatedOn: 2026-11-19 19:46:06.358772, CreatedOnDay: 2026-11-19, payload: {..., is_processed: False, error_text:  [None-->] resolve_lookups: no Product found for fk_col='product_id' from source fields  row: 0x10f2e3b50  session: 0x10e433df0  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:06,371 - logic_logger - INFO
....DailyFlow[2026-11-19] {Update - Adjusting daily_flow: message_rejected} day: 2026-11-19, order_count: 43, order_amount: 12960.00, message_received: 11, message_processed: 5, message_rejected:  [4-->] 5, message_pending: 2, request_received: 49, request_processed: 40, request_rejected: 8, request_pending: 1  row: 0x10e861700  session: 0x10e433df0  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:06,371 - logic_logger - INFO
....DailyFlow[2026-11-19] {Formula message_pending} day: 2026-11-19, order_count: 43, order_amount: 12960.00, message_received: 11, message_processed: 5, message_rejected:  [4-->] 5, message_pending:  [2-->] 1, request_received: 49, request_processed: 40, request_rejected: 8, request_pending: 1  row: 0x10e861700  session: 0x10e433df0  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:06,371 - logic_logger - INFO
....DailyFlow[2026-11-19] {Prune Formula: request_pending [['request_received', 'request_processed', 'request_rejected']]} day: 2026-11-19, order_count: 43, order_amount: 12960.00, message_received: 11, message_processed: 5, message_rejected:  [4-->] 5, message_pending:  [2-->] 1, request_received: 49, request_processed: 40, request_rejected: 8, request_pending: 1  row: 0x10e861700  session: 0x10e433df0  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:06,371 - logic_logger - INFO
Logic Phase:		COMMIT LOGIC		(session=0x10e433df0)   										 - 2026-11-19 19:46:06,372 - logic_logger - INFO
Logic Phase:		AFTER_FLUSH LOGIC	(session=0x10e433df0)   										 - 2026-11-19 19:46:06,372 - logic_logger - INFO
..OrderB2bMessage[95] {AfterFlush Event} id: 95, CreatedOn: 2026-11-19 19:46:06.358772, CreatedOnDay: 2026-11-19, payload: {..., is_processed: False, error_text:  [None-->] resolve_lookups: no Product found for fk_col='product_id' from source fields  row: 0x10f2e3b50  session: 0x10e433df0  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:06,372 - logic_logger - INFO

```
</details>

&nbsp;
&nbsp;

### Feature: Order Flow Dashboard  

&nbsp;
&nbsp;

#### Scenario: A new order is dated today and counted in today's totals ✅ (0.03 s)
&emsp;  Scenario: A new order is dated today and counted in today's totals  
&emsp;&emsp;    Given a new customer "Flow Cust" with credit limit 5000  
&emsp;&emsp;    And today's totals are noted  
&emsp;&emsp;    When a B2B order is placed for "Flow Cust" with 2 Widget and 1 Gadget  
&emsp;&emsp;    Then the order is dated today  
&emsp;&emsp;    And today's order count rose by 1 and order amount by 330  

<details markdown>
<summary>Rules exercised and logic log (2 transactions)</summary>


&nbsp;
&nbsp;


**Rules Used** in Scenario: A new order is dated today and counted in today's totals
```
  DailyFlow  
    1. Derive DailyFlow.request_rejected as Count(OrderB2bRequest Where Rule.count(derive=models.DailyFlow.request_rejected, as_count_of=models.OrderB2bRequest, where=lambda row: row.error_text is not None, insert_parent=True), insert_parent)  
    2. Derive DailyFlow.request_pending as Formula (2): Rule.formula(derive=models.DailyFlow.request_pend [...]  
    3. Derive DailyFlow.request_processed as Count(OrderB2bRequest Where Rule.count(derive=models.DailyFlow.request_processed, as_count_of=models.OrderB2bRequest, where=lambda row: row.is_processed == True, insert_parent=True), insert_parent)  
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
**Logic Log** in Scenario: A new order is dated today and counted in today's totals (2 transactions)
```
Logic Phase:		ROW LOGIC		(session=0x10e4ce250) (sqlalchemy before_flush)			 - 2026-11-19 19:46:06,906 - logic_logger - INFO
..OrderB2bRequest[None] {Insert - client} id: None, CreatedOn: None, CreatedOnDay: None, payload: {"Account": "Flow Cust 1795146366894", "Notes": "behave test", "Items": [{"Name": "Widget", "QuantityOrdered": 2}, {"Name": "Gadget", "QuantityOrdered": 1}]}, is_processed: False, error_text: None  row: 0x10f20c250  session: 0x10e4ce250  ins_upd_dlt: ins, initial: ins - 2026-11-19 19:46:06,906 - logic_logger - INFO
..OrderB2bRequest[None] {early_row_event_all_classes - handle_all did stamping} id: None, CreatedOn: 2026-11-19 19:46:06.906554, CreatedOnDay: 2026-11-19, payload: {"Account": "Flow Cust 1795146366894", "Notes": "behave test", "Items": [{"Name": "Widget", "QuantityOrdered": 2}, {"Name": "Gadget", "QuantityOrdered": 1}]}, is_processed: False, error_text: None  row: 0x10f20c250  session: 0x10e4ce250  ins_upd_dlt: ins, initial: ins - 2026-11-19 19:46:06,906 - logic_logger - INFO
....DailyFlow[2026-11-19] {Update - Adjusting daily_flow: request_received} day: 2026-11-19, order_count: 43, order_amount: 12960.00, message_received: 11, message_processed: 5, message_rejected: 5, message_pending: 1, request_received:  [49-->] 50, request_processed: 40, request_rejected: 8, request_pending: 1  row: 0x10e8617b0  session: 0x10e4ce250  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:06,907 - logic_logger - INFO
....DailyFlow[2026-11-19] {Prune Formula: message_pending [['message_received', 'message_processed', 'message_rejected']]} day: 2026-11-19, order_count: 43, order_amount: 12960.00, message_received: 11, message_processed: 5, message_rejected: 5, message_pending: 1, request_received:  [49-->] 50, request_processed: 40, request_rejected: 8, request_pending: 1  row: 0x10e8617b0  session: 0x10e4ce250  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:06,907 - logic_logger - INFO
....DailyFlow[2026-11-19] {Formula request_pending} day: 2026-11-19, order_count: 43, order_amount: 12960.00, message_received: 11, message_processed: 5, message_rejected: 5, message_pending: 1, request_received:  [49-->] 50, request_processed: 40, request_rejected: 8, request_pending:  [1-->] 2  row: 0x10e8617b0  session: 0x10e4ce250  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:06,907 - logic_logger - INFO
Logic Phase:		COMMIT LOGIC		(session=0x10e4ce250)   										 - 2026-11-19 19:46:06,907 - logic_logger - INFO
Logic Phase:		AFTER_FLUSH LOGIC	(session=0x10e4ce250)   										 - 2026-11-19 19:46:06,907 - logic_logger - INFO


Logic Phase:		ROW LOGIC		(session=0x10e4ce250) (sqlalchemy before_flush)			 - 2026-11-19 19:46:06,911 - logic_logger - INFO
..OrderB2bRequest[156] {Update - client} id: 156, CreatedOn: 2026-11-19 19:46:06.906554, CreatedOnDay: 2026-11-19, payload: {"Account": "Flow Cust 1795146366894", "Notes": "behave test", "Items": [{"Name": "Widget", "QuantityOrdered": 2}, {"Name": "Gadget", "QuantityOrdered": 1}]}, is_processed:  [False-->] True, error_text: None  row: 0x10f20c250  session: 0x10e4ce250  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:06,911 - logic_logger - INFO
....DailyFlow[2026-11-19] {Update - Adjusting daily_flow: request_processed} day: 2026-11-19, order_count: 43, order_amount: 12960.00, message_received: 11, message_processed: 5, message_rejected: 5, message_pending: 1, request_received: 50, request_processed:  [40-->] 41, request_rejected: 8, request_pending: 2  row: 0x10e8617b0  session: 0x10e4ce250  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:06,912 - logic_logger - INFO
....DailyFlow[2026-11-19] {Prune Formula: message_pending [['message_received', 'message_processed', 'message_rejected']]} day: 2026-11-19, order_count: 43, order_amount: 12960.00, message_received: 11, message_processed: 5, message_rejected: 5, message_pending: 1, request_received: 50, request_processed:  [40-->] 41, request_rejected: 8, request_pending: 2  row: 0x10e8617b0  session: 0x10e4ce250  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:06,912 - logic_logger - INFO
....DailyFlow[2026-11-19] {Formula request_pending} day: 2026-11-19, order_count: 43, order_amount: 12960.00, message_received: 11, message_processed: 5, message_rejected: 5, message_pending: 1, request_received: 50, request_processed:  [40-->] 41, request_rejected: 8, request_pending:  [2-->] 1  row: 0x10e8617b0  session: 0x10e4ce250  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:06,912 - logic_logger - INFO
..Product[1] {Update - client} id: 1, name: Gadget, count_suppliers: 0, unit_price: 150.0000000000  row: 0x10f2f73f0  session: 0x10e4ce250  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:06,912 - logic_logger - INFO
..Order[None] {Insert - client} id: None, notes: behave test, customer_id: 61, CreatedOn: None, date_shipped: None, amount_total: None, CreatedOnDay: None  row: 0x10f2da4e0  session: 0x10e4ce250  ins_upd_dlt: ins, initial: ins - 2026-11-19 19:46:06,912 - logic_logger - INFO
..Order[None] {early_row_event_all_classes - handle_all did stamping} id: None, notes: behave test, customer_id: 61, CreatedOn: 2026-11-19, date_shipped: None, amount_total: None, CreatedOnDay: 2026-11-19  row: 0x10f2da4e0  session: 0x10e4ce250  ins_upd_dlt: ins, initial: ins - 2026-11-19 19:46:06,912 - logic_logger - INFO
..Order[None] {server aggregate_defaults: amount_total } id: None, notes: behave test, customer_id: 61, CreatedOn: 2026-11-19, date_shipped: None, amount_total: 0, CreatedOnDay: 2026-11-19  row: 0x10f2da4e0  session: 0x10e4ce250  ins_upd_dlt: ins, initial: ins - 2026-11-19 19:46:06,912 - logic_logger - INFO
....DailyFlow[2026-11-19] {Update - Adjusting daily_flow: order_count} day: 2026-11-19, order_count:  [43-->] 44, order_amount: 12960.00, message_received: 11, message_processed: 5, message_rejected: 5, message_pending: 1, request_received: 50, request_processed: 41, request_rejected: 8, request_pending: 1  row: 0x10e8617b0  session: 0x10e4ce250  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:06,912 - logic_logger - INFO
....DailyFlow[2026-11-19] {Prune Formula: message_pending [['message_received', 'message_processed', 'message_rejected']]} day: 2026-11-19, order_count:  [43-->] 44, order_amount: 12960.00, message_received: 11, message_processed: 5, message_rejected: 5, message_pending: 1, request_received: 50, request_processed: 41, request_rejected: 8, request_pending: 1  row: 0x10e8617b0  session: 0x10e4ce250  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:06,912 - logic_logger - INFO
....DailyFlow[2026-11-19] {Prune Formula: request_pending [['request_received', 'request_processed', 'request_rejected']]} day: 2026-11-19, order_count:  [43-->] 44, order_amount: 12960.00, message_received: 11, message_processed: 5, message_rejected: 5, message_pending: 1, request_received: 50, request_processed: 41, request_rejected: 8, request_pending: 1  row: 0x10e8617b0  session: 0x10e4ce250  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:06,912 - logic_logger - INFO
..Item[None] {Insert - client} id: None, order_id: None, product_id: 2, quantity: 2, amount: None, unit_price: None  row: 0x10f2ba050  session: 0x10e4ce250  ins_upd_dlt: ins, initial: ins - 2026-11-19 19:46:06,912 - logic_logger - INFO
..Item[None] {copy_rules for role: product - unit_price} id: None, order_id: None, product_id: 2, quantity: 2, amount: None, unit_price: 90.0000000000  row: 0x10f2ba050  session: 0x10e4ce250  ins_upd_dlt: ins, initial: ins - 2026-11-19 19:46:06,913 - logic_logger - INFO
..Item[None] {Formula amount} id: None, order_id: None, product_id: 2, quantity: 2, amount: 180.0000000000, unit_price: 90.0000000000  row: 0x10f2ba050  session: 0x10e4ce250  ins_upd_dlt: ins, initial: ins - 2026-11-19 19:46:06,913 - logic_logger - INFO
....Order[None] {Update - Adjusting order: amount_total} id: None, notes: behave test, customer_id: 61, CreatedOn: 2026-11-19, date_shipped: None, amount_total:  [0-->] 180.0000000000, CreatedOnDay: 2026-11-19  row: 0x10f2da4e0  session: 0x10e4ce250  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:06,913 - logic_logger - INFO
......DailyFlow[2026-11-19] {Update - Adjusting daily_flow: order_amount} day: 2026-11-19, order_count: 44, order_amount:  [12960.00-->] 13140.0000000000, message_received: 11, message_processed: 5, message_rejected: 5, message_pending: 1, request_received: 50, request_processed: 41, request_rejected: 8, request_pending: 1  row: 0x10e8617b0  session: 0x10e4ce250  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:06,913 - logic_logger - INFO
......DailyFlow[2026-11-19] {Prune Formula: message_pending [['message_received', 'message_processed', 'message_rejected']]} day: 2026-11-19, order_count: 44, order_amount:  [12960.00-->] 13140.0000000000, message_received: 11, message_processed: 5, message_rejected: 5, message_pending: 1, request_received: 50, request_processed: 41, request_rejected: 8, request_pending: 1  row: 0x10e8617b0  session: 0x10e4ce250  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:06,913 - logic_logger - INFO
......DailyFlow[2026-11-19] {Prune Formula: request_pending [['request_received', 'request_processed', 'request_rejected']]} day: 2026-11-19, order_count: 44, order_amount:  [12960.00-->] 13140.0000000000, message_received: 11, message_processed: 5, message_rejected: 5, message_pending: 1, request_received: 50, request_processed: 41, request_rejected: 8, request_pending: 1  row: 0x10e8617b0  session: 0x10e4ce250  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:06,913 - logic_logger - INFO
......Customer[61] {Update - Adjusting customer: balance} id: 61, name: Flow Cust 1795146366894, balance:  [0E-10-->] 180.0000000000, credit_limit: 5000.0000000000, email: None, email_opt_out: None  row: 0x10f2e29d0  session: 0x10e4ce250  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:06,913 - logic_logger - INFO
..Item[None] {Insert - client} id: None, order_id: None, product_id: None, quantity: 1, amount: None, unit_price: None  row: 0x10f2bb350  session: 0x10e4ce250  ins_upd_dlt: ins, initial: ins - 2026-11-19 19:46:06,913 - logic_logger - INFO
..Item[None] {copy_rules for role: product - unit_price} id: None, order_id: None, product_id: None, quantity: 1, amount: None, unit_price: 150.0000000000  row: 0x10f2bb350  session: 0x10e4ce250  ins_upd_dlt: ins, initial: ins - 2026-11-19 19:46:06,913 - logic_logger - INFO
..Item[None] {Formula amount} id: None, order_id: None, product_id: None, quantity: 1, amount: 150.0000000000, unit_price: 150.0000000000  row: 0x10f2bb350  session: 0x10e4ce250  ins_upd_dlt: ins, initial: ins - 2026-11-19 19:46:06,913 - logic_logger - INFO
....Order[None] {Update - Adjusting order: amount_total} id: None, notes: behave test, customer_id: 61, CreatedOn: 2026-11-19, date_shipped: None, amount_total:  [180.0000000000-->] 330.0000000000, CreatedOnDay: 2026-11-19  row: 0x10f2da4e0  session: 0x10e4ce250  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:06,913 - logic_logger - INFO
......DailyFlow[2026-11-19] {Update - Adjusting daily_flow: order_amount} day: 2026-11-19, order_count: 44, order_amount:  [13140.0000000000-->] 13290.0000000000, message_received: 11, message_processed: 5, message_rejected: 5, message_pending: 1, request_received: 50, request_processed: 41, request_rejected: 8, request_pending: 1  row: 0x10e8617b0  session: 0x10e4ce250  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:06,914 - logic_logger - INFO
......DailyFlow[2026-11-19] {Prune Formula: message_pending [['message_received', 'message_processed', 'message_rejected']]} day: 2026-11-19, order_count: 44, order_amount:  [13140.0000000000-->] 13290.0000000000, message_received: 11, message_processed: 5, message_rejected: 5, message_pending: 1, request_received: 50, request_processed: 41, request_rejected: 8, request_pending: 1  row: 0x10e8617b0  session: 0x10e4ce250  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:06,914 - logic_logger - INFO
......DailyFlow[2026-11-19] {Prune Formula: request_pending [['request_received', 'request_processed', 'request_rejected']]} day: 2026-11-19, order_count: 44, order_amount:  [13140.0000000000-->] 13290.0000000000, message_received: 11, message_processed: 5, message_rejected: 5, message_pending: 1, request_received: 50, request_processed: 41, request_rejected: 8, request_pending: 1  row: 0x10e8617b0  session: 0x10e4ce250  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:06,914 - logic_logger - INFO
......Customer[61] {Update - Adjusting customer: balance} id: 61, name: Flow Cust 1795146366894, balance:  [180.0000000000-->] 330.0000000000, credit_limit: 5000.0000000000, email: None, email_opt_out: None  row: 0x10f2e29d0  session: 0x10e4ce250  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:06,914 - logic_logger - INFO
Logic Phase:		COMMIT LOGIC		(session=0x10e4ce250)   										 - 2026-11-19 19:46:06,914 - logic_logger - INFO
Logic Phase:		AFTER_FLUSH LOGIC	(session=0x10e4ce250)   										 - 2026-11-19 19:46:06,915 - logic_logger - INFO
..Order[233] {AfterFlush Event} id: 233, notes: behave test, customer_id: 61, CreatedOn: 2026-11-19, date_shipped: None, amount_total: 330.0000000000, CreatedOnDay: 2026-11-19  row: 0x10f2da4e0  session: 0x10e4ce250  ins_upd_dlt: ins, initial: ins - 2026-11-19 19:46:06,915 - logic_logger - INFO

```
</details>

&nbsp;
&nbsp;

#### Scenario: Changing an order's value adjusts today's order amount ✅ (0.03 s)
&emsp;  Scenario: Changing an order's value adjusts today's order amount  
&emsp;&emsp;    Given a new customer "Flow Change" with credit limit 5000  
&emsp;&emsp;    And a B2B order is placed for "Flow Change" with 2 Widget and 1 Gadget  
&emsp;&emsp;    And today's totals are noted  
&emsp;&emsp;    When the quantity of the first item is changed to 3  
&emsp;&emsp;    Then today's order count rose by 0 and order amount by 90  

_No logic log for this scenario: the test does not open one, so no rules are shown for it (see "How to add more tests")._

&nbsp;
&nbsp;

#### Scenario: Deleting an order removes it from today's totals ✅ (0.02 s)
&emsp;  Scenario: Deleting an order removes it from today's totals  
&emsp;&emsp;    Given a new customer "Flow Delete" with credit limit 5000  
&emsp;&emsp;    And a B2B order is placed for "Flow Delete" with 1 Gadget  
&emsp;&emsp;    And today's totals are noted  
&emsp;&emsp;    When the order is deleted  
&emsp;&emsp;    Then today's order count rose by -1 and order amount by -150  

<details markdown>
<summary>Rules exercised and logic log (3 transactions)</summary>


&nbsp;
&nbsp;


**Rules Used** in Scenario: Deleting an order removes it from today's totals
```
  DailyFlow  
    1. Derive DailyFlow.request_rejected as Count(OrderB2bRequest Where Rule.count(derive=models.DailyFlow.request_rejected, as_count_of=models.OrderB2bRequest, where=lambda row: row.error_text is not None, insert_parent=True), insert_parent)  
    2. Derive DailyFlow.request_pending as Formula (2): Rule.formula(derive=models.DailyFlow.request_pend [...]  
    3. Derive DailyFlow.request_processed as Count(OrderB2bRequest Where Rule.count(derive=models.DailyFlow.request_processed, as_count_of=models.OrderB2bRequest, where=lambda row: row.is_processed == True, insert_parent=True), insert_parent)  
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
**Logic Log** in Scenario: Deleting an order removes it from today's totals (3 transactions)
```
Logic Phase:		ROW LOGIC		(session=0x10e4ce250) (sqlalchemy before_flush)			 - 2026-11-19 19:46:06,961 - logic_logger - INFO
..OrderB2bRequest[None] {Insert - client} id: None, CreatedOn: None, CreatedOnDay: None, payload: {"Account": "Flow Delete 1795146366957", "Notes": "behave test", "Items": [{"Name": "Gadget", "QuantityOrdered": 1}]}, is_processed: False, error_text: None  row: 0x10f20c2d0  session: 0x10e4ce250  ins_upd_dlt: ins, initial: ins - 2026-11-19 19:46:06,961 - logic_logger - INFO
..OrderB2bRequest[None] {early_row_event_all_classes - handle_all did stamping} id: None, CreatedOn: 2026-11-19 19:46:06.962030, CreatedOnDay: 2026-11-19, payload: {"Account": "Flow Delete 1795146366957", "Notes": "behave test", "Items": [{"Name": "Gadget", "QuantityOrdered": 1}]}, is_processed: False, error_text: None  row: 0x10f20c2d0  session: 0x10e4ce250  ins_upd_dlt: ins, initial: ins - 2026-11-19 19:46:06,962 - logic_logger - INFO
....DailyFlow[2026-11-19] {Update - Adjusting daily_flow: request_received} day: 2026-11-19, order_count: 45, order_amount: 13710.00, message_received: 11, message_processed: 5, message_rejected: 5, message_pending: 1, request_received:  [51-->] 52, request_processed: 42, request_rejected: 8, request_pending: 1  row: 0x10e8617b0  session: 0x10e4ce250  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:06,962 - logic_logger - INFO
....DailyFlow[2026-11-19] {Prune Formula: message_pending [['message_received', 'message_processed', 'message_rejected']]} day: 2026-11-19, order_count: 45, order_amount: 13710.00, message_received: 11, message_processed: 5, message_rejected: 5, message_pending: 1, request_received:  [51-->] 52, request_processed: 42, request_rejected: 8, request_pending: 1  row: 0x10e8617b0  session: 0x10e4ce250  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:06,962 - logic_logger - INFO
....DailyFlow[2026-11-19] {Formula request_pending} day: 2026-11-19, order_count: 45, order_amount: 13710.00, message_received: 11, message_processed: 5, message_rejected: 5, message_pending: 1, request_received:  [51-->] 52, request_processed: 42, request_rejected: 8, request_pending:  [1-->] 2  row: 0x10e8617b0  session: 0x10e4ce250  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:06,962 - logic_logger - INFO
Logic Phase:		COMMIT LOGIC		(session=0x10e4ce250)   										 - 2026-11-19 19:46:06,962 - logic_logger - INFO
Logic Phase:		AFTER_FLUSH LOGIC	(session=0x10e4ce250)   										 - 2026-11-19 19:46:06,963 - logic_logger - INFO


Logic Phase:		ROW LOGIC		(session=0x10e4ce250) (sqlalchemy before_flush)			 - 2026-11-19 19:46:06,964 - logic_logger - INFO
..OrderB2bRequest[158] {Update - client} id: 158, CreatedOn: 2026-11-19 19:46:06.962030, CreatedOnDay: 2026-11-19, payload: {"Account": "Flow Delete 1795146366957", "Notes": "behave test", "Items": [{"Name": "Gadget", "QuantityOrdered": 1}]}, is_processed:  [False-->] True, error_text: None  row: 0x10f20c2d0  session: 0x10e4ce250  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:06,965 - logic_logger - INFO
....DailyFlow[2026-11-19] {Update - Adjusting daily_flow: request_processed} day: 2026-11-19, order_count: 45, order_amount: 13710.00, message_received: 11, message_processed: 5, message_rejected: 5, message_pending: 1, request_received: 52, request_processed:  [42-->] 43, request_rejected: 8, request_pending: 2  row: 0x10e8617b0  session: 0x10e4ce250  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:06,965 - logic_logger - INFO
....DailyFlow[2026-11-19] {Prune Formula: message_pending [['message_received', 'message_processed', 'message_rejected']]} day: 2026-11-19, order_count: 45, order_amount: 13710.00, message_received: 11, message_processed: 5, message_rejected: 5, message_pending: 1, request_received: 52, request_processed:  [42-->] 43, request_rejected: 8, request_pending: 2  row: 0x10e8617b0  session: 0x10e4ce250  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:06,965 - logic_logger - INFO
....DailyFlow[2026-11-19] {Formula request_pending} day: 2026-11-19, order_count: 45, order_amount: 13710.00, message_received: 11, message_processed: 5, message_rejected: 5, message_pending: 1, request_received: 52, request_processed:  [42-->] 43, request_rejected: 8, request_pending:  [2-->] 1  row: 0x10e8617b0  session: 0x10e4ce250  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:06,965 - logic_logger - INFO
..Product[1] {Update - client} id: 1, name: Gadget, count_suppliers: 0, unit_price: 150.0000000000  row: 0x10f2ab4d0  session: 0x10e4ce250  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:06,965 - logic_logger - INFO
..Order[None] {Insert - client} id: None, notes: behave test, customer_id: 63, CreatedOn: None, date_shipped: None, amount_total: None, CreatedOnDay: None  row: 0x10f2db770  session: 0x10e4ce250  ins_upd_dlt: ins, initial: ins - 2026-11-19 19:46:06,965 - logic_logger - INFO
..Order[None] {early_row_event_all_classes - handle_all did stamping} id: None, notes: behave test, customer_id: 63, CreatedOn: 2026-11-19, date_shipped: None, amount_total: None, CreatedOnDay: 2026-11-19  row: 0x10f2db770  session: 0x10e4ce250  ins_upd_dlt: ins, initial: ins - 2026-11-19 19:46:06,965 - logic_logger - INFO
..Order[None] {server aggregate_defaults: amount_total } id: None, notes: behave test, customer_id: 63, CreatedOn: 2026-11-19, date_shipped: None, amount_total: 0, CreatedOnDay: 2026-11-19  row: 0x10f2db770  session: 0x10e4ce250  ins_upd_dlt: ins, initial: ins - 2026-11-19 19:46:06,965 - logic_logger - INFO
....DailyFlow[2026-11-19] {Update - Adjusting daily_flow: order_count} day: 2026-11-19, order_count:  [45-->] 46, order_amount: 13710.00, message_received: 11, message_processed: 5, message_rejected: 5, message_pending: 1, request_received: 52, request_processed: 43, request_rejected: 8, request_pending: 1  row: 0x10e8617b0  session: 0x10e4ce250  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:06,965 - logic_logger - INFO
....DailyFlow[2026-11-19] {Prune Formula: message_pending [['message_received', 'message_processed', 'message_rejected']]} day: 2026-11-19, order_count:  [45-->] 46, order_amount: 13710.00, message_received: 11, message_processed: 5, message_rejected: 5, message_pending: 1, request_received: 52, request_processed: 43, request_rejected: 8, request_pending: 1  row: 0x10e8617b0  session: 0x10e4ce250  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:06,965 - logic_logger - INFO
....DailyFlow[2026-11-19] {Prune Formula: request_pending [['request_received', 'request_processed', 'request_rejected']]} day: 2026-11-19, order_count:  [45-->] 46, order_amount: 13710.00, message_received: 11, message_processed: 5, message_rejected: 5, message_pending: 1, request_received: 52, request_processed: 43, request_rejected: 8, request_pending: 1  row: 0x10e8617b0  session: 0x10e4ce250  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:06,965 - logic_logger - INFO
..Item[None] {Insert - client} id: None, order_id: None, product_id: None, quantity: 1, amount: None, unit_price: None  row: 0x10f30f7d0  session: 0x10e4ce250  ins_upd_dlt: ins, initial: ins - 2026-11-19 19:46:06,966 - logic_logger - INFO
..Item[None] {copy_rules for role: product - unit_price} id: None, order_id: None, product_id: None, quantity: 1, amount: None, unit_price: 150.0000000000  row: 0x10f30f7d0  session: 0x10e4ce250  ins_upd_dlt: ins, initial: ins - 2026-11-19 19:46:06,966 - logic_logger - INFO
..Item[None] {Formula amount} id: None, order_id: None, product_id: None, quantity: 1, amount: 150.0000000000, unit_price: 150.0000000000  row: 0x10f30f7d0  session: 0x10e4ce250  ins_upd_dlt: ins, initial: ins - 2026-11-19 19:46:06,966 - logic_logger - INFO
....Order[None] {Update - Adjusting order: amount_total} id: None, notes: behave test, customer_id: 63, CreatedOn: 2026-11-19, date_shipped: None, amount_total:  [0-->] 150.0000000000, CreatedOnDay: 2026-11-19  row: 0x10f2db770  session: 0x10e4ce250  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:06,966 - logic_logger - INFO
......DailyFlow[2026-11-19] {Update - Adjusting daily_flow: order_amount} day: 2026-11-19, order_count: 46, order_amount:  [13710.00-->] 13860.0000000000, message_received: 11, message_processed: 5, message_rejected: 5, message_pending: 1, request_received: 52, request_processed: 43, request_rejected: 8, request_pending: 1  row: 0x10e8617b0  session: 0x10e4ce250  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:06,966 - logic_logger - INFO
......DailyFlow[2026-11-19] {Prune Formula: message_pending [['message_received', 'message_processed', 'message_rejected']]} day: 2026-11-19, order_count: 46, order_amount:  [13710.00-->] 13860.0000000000, message_received: 11, message_processed: 5, message_rejected: 5, message_pending: 1, request_received: 52, request_processed: 43, request_rejected: 8, request_pending: 1  row: 0x10e8617b0  session: 0x10e4ce250  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:06,966 - logic_logger - INFO
......DailyFlow[2026-11-19] {Prune Formula: request_pending [['request_received', 'request_processed', 'request_rejected']]} day: 2026-11-19, order_count: 46, order_amount:  [13710.00-->] 13860.0000000000, message_received: 11, message_processed: 5, message_rejected: 5, message_pending: 1, request_received: 52, request_processed: 43, request_rejected: 8, request_pending: 1  row: 0x10e8617b0  session: 0x10e4ce250  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:06,966 - logic_logger - INFO
......Customer[63] {Update - Adjusting customer: balance} id: 63, name: Flow Delete 1795146366957, balance:  [0E-10-->] 150.0000000000, credit_limit: 5000.0000000000, email: None, email_opt_out: None  row: 0x10f2e3b50  session: 0x10e4ce250  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:06,966 - logic_logger - INFO
Logic Phase:		COMMIT LOGIC		(session=0x10e4ce250)   										 - 2026-11-19 19:46:06,966 - logic_logger - INFO
Logic Phase:		AFTER_FLUSH LOGIC	(session=0x10e4ce250)   										 - 2026-11-19 19:46:06,967 - logic_logger - INFO
..Order[235] {AfterFlush Event} id: 235, notes: behave test, customer_id: 63, CreatedOn: 2026-11-19, date_shipped: None, amount_total: 150.0000000000, CreatedOnDay: 2026-11-19  row: 0x10f2db770  session: 0x10e4ce250  ins_upd_dlt: ins, initial: ins - 2026-11-19 19:46:06,967 - logic_logger - INFO


Logic Phase:		ROW LOGIC		(session=0x10e4cd480) (sqlalchemy before_flush)			 - 2026-11-19 19:46:06,972 - logic_logger - INFO
..Order[235] {Delete - client} id: 235, notes: behave test, customer_id: 63, CreatedOn: 2026-11-19, date_shipped: None, amount_total: 150.0000000000, CreatedOnDay: 2026-11-19  row: 0x10f2db6e0  session: 0x10e4cd480  ins_upd_dlt: dlt, initial: dlt - 2026-11-19 19:46:06,972 - logic_logger - INFO
....DailyFlow[2026-11-19] {Update - Adjusting daily_flow: order_count, order_amount} day: 2026-11-19, order_count:  [46-->] 45, order_amount:  [13860.00-->] 13710.0000000000, message_received: 11, message_processed: 5, message_rejected: 5, message_pending: 1, request_received: 52, request_processed: 43, request_rejected: 8, request_pending: 1  row: 0x10e861910  session: 0x10e4cd480  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:06,972 - logic_logger - INFO
....DailyFlow[2026-11-19] {Prune Formula: message_pending [['message_received', 'message_processed', 'message_rejected']]} day: 2026-11-19, order_count:  [46-->] 45, order_amount:  [13860.00-->] 13710.0000000000, message_received: 11, message_processed: 5, message_rejected: 5, message_pending: 1, request_received: 52, request_processed: 43, request_rejected: 8, request_pending: 1  row: 0x10e861910  session: 0x10e4cd480  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:06,972 - logic_logger - INFO
....DailyFlow[2026-11-19] {Prune Formula: request_pending [['request_received', 'request_processed', 'request_rejected']]} day: 2026-11-19, order_count:  [46-->] 45, order_amount:  [13860.00-->] 13710.0000000000, message_received: 11, message_processed: 5, message_rejected: 5, message_pending: 1, request_received: 52, request_processed: 43, request_rejected: 8, request_pending: 1  row: 0x10e861910  session: 0x10e4cd480  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:06,972 - logic_logger - INFO
....Customer[63] {Update - Adjusting customer: balance} id: 63, name: Flow Delete 1795146366957, balance:  [150.0000000000-->] 0E-10, credit_limit: 5000.0000000000, email: None, email_opt_out: None  row: 0x10f357ad0  session: 0x10e4cd480  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:06,972 - logic_logger - INFO
Logic Phase:		COMMIT LOGIC		(session=0x10e4cd480)   										 - 2026-11-19 19:46:06,972 - logic_logger - INFO
Logic Phase:		AFTER_FLUSH LOGIC	(session=0x10e4cd480)   										 - 2026-11-19 19:46:06,973 - logic_logger - INFO
..Order[235] {AfterFlush Event} id: 235, notes: behave test, customer_id: 63, CreatedOn: 2026-11-19, date_shipped: None, amount_total: 150.0000000000, CreatedOnDay: 2026-11-19  row: 0x10f2db6e0  session: 0x10e4cd480  ins_upd_dlt: dlt, initial: dlt - 2026-11-19 19:46:06,973 - logic_logger - INFO

```
</details>

&nbsp;
&nbsp;

#### Scenario: Moving an order to another day adjusts both days ✅ (0.03 s)
&emsp;  Scenario: Moving an order to another day adjusts both days  
&emsp;&emsp;    Given a new customer "Flow Move" with credit limit 5000  
&emsp;&emsp;    And a B2B order is placed for "Flow Move" with 1 Gadget  
&emsp;&emsp;    And today's totals are noted  
&emsp;&emsp;    And the totals of day "2000-01-01" are noted  
&emsp;&emsp;    When the order is moved to day "2000-01-01"  
&emsp;&emsp;    Then today's order count rose by -1 and order amount by -150  
&emsp;&emsp;    And day "2000-01-01" order count rose by 1 and order amount by 150  

<details markdown>
<summary>Rules exercised and logic log (3 transactions)</summary>


&nbsp;
&nbsp;


**Rules Used** in Scenario: Moving an order to another day adjusts both days
```
  DailyFlow  
    1. Derive DailyFlow.request_rejected as Count(OrderB2bRequest Where Rule.count(derive=models.DailyFlow.request_rejected, as_count_of=models.OrderB2bRequest, where=lambda row: row.error_text is not None, insert_parent=True), insert_parent)  
    2. Derive DailyFlow.request_pending as Formula (2): Rule.formula(derive=models.DailyFlow.request_pend [...]  
    3. Derive DailyFlow.request_processed as Count(OrderB2bRequest Where Rule.count(derive=models.DailyFlow.request_processed, as_count_of=models.OrderB2bRequest, where=lambda row: row.is_processed == True, insert_parent=True), insert_parent)  
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
**Logic Log** in Scenario: Moving an order to another day adjusts both days (3 transactions)
```
Logic Phase:		ROW LOGIC		(session=0x10f2fc490) (sqlalchemy before_flush)			 - 2026-11-19 19:46:06,984 - logic_logger - INFO
..OrderB2bRequest[None] {Insert - client} id: None, CreatedOn: None, CreatedOnDay: None, payload: {"Account": "Flow Move 1795146366980", "Notes": "behave test", "Items": [{"Name": "Gadget", "QuantityOrdered": 1}]}, is_processed: False, error_text: None  row: 0x10f2c9dd0  session: 0x10f2fc490  ins_upd_dlt: ins, initial: ins - 2026-11-19 19:46:06,985 - logic_logger - INFO
..OrderB2bRequest[None] {early_row_event_all_classes - handle_all did stamping} id: None, CreatedOn: 2026-11-19 19:46:06.985060, CreatedOnDay: 2026-11-19, payload: {"Account": "Flow Move 1795146366980", "Notes": "behave test", "Items": [{"Name": "Gadget", "QuantityOrdered": 1}]}, is_processed: False, error_text: None  row: 0x10f2c9dd0  session: 0x10f2fc490  ins_upd_dlt: ins, initial: ins - 2026-11-19 19:46:06,985 - logic_logger - INFO
....DailyFlow[2026-11-19] {Update - Adjusting daily_flow: request_received} day: 2026-11-19, order_count: 45, order_amount: 13710.00, message_received: 11, message_processed: 5, message_rejected: 5, message_pending: 1, request_received:  [52-->] 53, request_processed: 43, request_rejected: 8, request_pending: 1  row: 0x10e861650  session: 0x10f2fc490  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:06,985 - logic_logger - INFO
....DailyFlow[2026-11-19] {Prune Formula: message_pending [['message_received', 'message_processed', 'message_rejected']]} day: 2026-11-19, order_count: 45, order_amount: 13710.00, message_received: 11, message_processed: 5, message_rejected: 5, message_pending: 1, request_received:  [52-->] 53, request_processed: 43, request_rejected: 8, request_pending: 1  row: 0x10e861650  session: 0x10f2fc490  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:06,985 - logic_logger - INFO
....DailyFlow[2026-11-19] {Formula request_pending} day: 2026-11-19, order_count: 45, order_amount: 13710.00, message_received: 11, message_processed: 5, message_rejected: 5, message_pending: 1, request_received:  [52-->] 53, request_processed: 43, request_rejected: 8, request_pending:  [1-->] 2  row: 0x10e861650  session: 0x10f2fc490  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:06,985 - logic_logger - INFO
Logic Phase:		COMMIT LOGIC		(session=0x10f2fc490)   										 - 2026-11-19 19:46:06,985 - logic_logger - INFO
Logic Phase:		AFTER_FLUSH LOGIC	(session=0x10f2fc490)   										 - 2026-11-19 19:46:06,985 - logic_logger - INFO


Logic Phase:		ROW LOGIC		(session=0x10f2fc490) (sqlalchemy before_flush)			 - 2026-11-19 19:46:06,987 - logic_logger - INFO
..Product[1] {Update - client} id: 1, name: Gadget, count_suppliers: 0, unit_price: 150.0000000000  row: 0x10f35c6e0  session: 0x10f2fc490  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:06,987 - logic_logger - INFO
..OrderB2bRequest[159] {Update - client} id: 159, CreatedOn: 2026-11-19 19:46:06.985060, CreatedOnDay: 2026-11-19, payload: {"Account": "Flow Move 1795146366980", "Notes": "behave test", "Items": [{"Name": "Gadget", "QuantityOrdered": 1}]}, is_processed:  [False-->] True, error_text: None  row: 0x10f2c9dd0  session: 0x10f2fc490  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:06,987 - logic_logger - INFO
....DailyFlow[2026-11-19] {Update - Adjusting daily_flow: request_processed} day: 2026-11-19, order_count: 45, order_amount: 13710.00, message_received: 11, message_processed: 5, message_rejected: 5, message_pending: 1, request_received: 53, request_processed:  [43-->] 44, request_rejected: 8, request_pending: 2  row: 0x10e861650  session: 0x10f2fc490  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:06,988 - logic_logger - INFO
....DailyFlow[2026-11-19] {Prune Formula: message_pending [['message_received', 'message_processed', 'message_rejected']]} day: 2026-11-19, order_count: 45, order_amount: 13710.00, message_received: 11, message_processed: 5, message_rejected: 5, message_pending: 1, request_received: 53, request_processed:  [43-->] 44, request_rejected: 8, request_pending: 2  row: 0x10e861650  session: 0x10f2fc490  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:06,988 - logic_logger - INFO
....DailyFlow[2026-11-19] {Formula request_pending} day: 2026-11-19, order_count: 45, order_amount: 13710.00, message_received: 11, message_processed: 5, message_rejected: 5, message_pending: 1, request_received: 53, request_processed:  [43-->] 44, request_rejected: 8, request_pending:  [2-->] 1  row: 0x10e861650  session: 0x10f2fc490  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:06,988 - logic_logger - INFO
..Order[None] {Insert - client} id: None, notes: behave test, customer_id: 64, CreatedOn: None, date_shipped: None, amount_total: None, CreatedOnDay: None  row: 0x10f2da720  session: 0x10f2fc490  ins_upd_dlt: ins, initial: ins - 2026-11-19 19:46:06,988 - logic_logger - INFO
..Order[None] {early_row_event_all_classes - handle_all did stamping} id: None, notes: behave test, customer_id: 64, CreatedOn: 2026-11-19, date_shipped: None, amount_total: None, CreatedOnDay: 2026-11-19  row: 0x10f2da720  session: 0x10f2fc490  ins_upd_dlt: ins, initial: ins - 2026-11-19 19:46:06,988 - logic_logger - INFO
..Order[None] {server aggregate_defaults: amount_total } id: None, notes: behave test, customer_id: 64, CreatedOn: 2026-11-19, date_shipped: None, amount_total: 0, CreatedOnDay: 2026-11-19  row: 0x10f2da720  session: 0x10f2fc490  ins_upd_dlt: ins, initial: ins - 2026-11-19 19:46:06,988 - logic_logger - INFO
....DailyFlow[2026-11-19] {Update - Adjusting daily_flow: order_count} day: 2026-11-19, order_count:  [45-->] 46, order_amount: 13710.00, message_received: 11, message_processed: 5, message_rejected: 5, message_pending: 1, request_received: 53, request_processed: 44, request_rejected: 8, request_pending: 1  row: 0x10e861650  session: 0x10f2fc490  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:06,988 - logic_logger - INFO
....DailyFlow[2026-11-19] {Prune Formula: message_pending [['message_received', 'message_processed', 'message_rejected']]} day: 2026-11-19, order_count:  [45-->] 46, order_amount: 13710.00, message_received: 11, message_processed: 5, message_rejected: 5, message_pending: 1, request_received: 53, request_processed: 44, request_rejected: 8, request_pending: 1  row: 0x10e861650  session: 0x10f2fc490  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:06,988 - logic_logger - INFO
....DailyFlow[2026-11-19] {Prune Formula: request_pending [['request_received', 'request_processed', 'request_rejected']]} day: 2026-11-19, order_count:  [45-->] 46, order_amount: 13710.00, message_received: 11, message_processed: 5, message_rejected: 5, message_pending: 1, request_received: 53, request_processed: 44, request_rejected: 8, request_pending: 1  row: 0x10e861650  session: 0x10f2fc490  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:06,988 - logic_logger - INFO
..Item[None] {Insert - client} id: None, order_id: None, product_id: None, quantity: 1, amount: None, unit_price: None  row: 0x10f2c81d0  session: 0x10f2fc490  ins_upd_dlt: ins, initial: ins - 2026-11-19 19:46:06,988 - logic_logger - INFO
..Item[None] {copy_rules for role: product - unit_price} id: None, order_id: None, product_id: None, quantity: 1, amount: None, unit_price: 150.0000000000  row: 0x10f2c81d0  session: 0x10f2fc490  ins_upd_dlt: ins, initial: ins - 2026-11-19 19:46:06,988 - logic_logger - INFO
..Item[None] {Formula amount} id: None, order_id: None, product_id: None, quantity: 1, amount: 150.0000000000, unit_price: 150.0000000000  row: 0x10f2c81d0  session: 0x10f2fc490  ins_upd_dlt: ins, initial: ins - 2026-11-19 19:46:06,988 - logic_logger - INFO
....Order[None] {Update - Adjusting order: amount_total} id: None, notes: behave test, customer_id: 64, CreatedOn: 2026-11-19, date_shipped: None, amount_total:  [0-->] 150.0000000000, CreatedOnDay: 2026-11-19  row: 0x10f2da720  session: 0x10f2fc490  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:06,988 - logic_logger - INFO
......DailyFlow[2026-11-19] {Update - Adjusting daily_flow: order_amount} day: 2026-11-19, order_count: 46, order_amount:  [13710.00-->] 13860.0000000000, message_received: 11, message_processed: 5, message_rejected: 5, message_pending: 1, request_received: 53, request_processed: 44, request_rejected: 8, request_pending: 1  row: 0x10e861650  session: 0x10f2fc490  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:06,988 - logic_logger - INFO
......DailyFlow[2026-11-19] {Prune Formula: message_pending [['message_received', 'message_processed', 'message_rejected']]} day: 2026-11-19, order_count: 46, order_amount:  [13710.00-->] 13860.0000000000, message_received: 11, message_processed: 5, message_rejected: 5, message_pending: 1, request_received: 53, request_processed: 44, request_rejected: 8, request_pending: 1  row: 0x10e861650  session: 0x10f2fc490  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:06,988 - logic_logger - INFO
......DailyFlow[2026-11-19] {Prune Formula: request_pending [['request_received', 'request_processed', 'request_rejected']]} day: 2026-11-19, order_count: 46, order_amount:  [13710.00-->] 13860.0000000000, message_received: 11, message_processed: 5, message_rejected: 5, message_pending: 1, request_received: 53, request_processed: 44, request_rejected: 8, request_pending: 1  row: 0x10e861650  session: 0x10f2fc490  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:06,989 - logic_logger - INFO
......Customer[64] {Update - Adjusting customer: balance} id: 64, name: Flow Move 1795146366980, balance:  [0E-10-->] 150.0000000000, credit_limit: 5000.0000000000, email: None, email_opt_out: None  row: 0x10f2b8850  session: 0x10f2fc490  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:06,989 - logic_logger - INFO
Logic Phase:		COMMIT LOGIC		(session=0x10f2fc490)   										 - 2026-11-19 19:46:06,989 - logic_logger - INFO
Logic Phase:		AFTER_FLUSH LOGIC	(session=0x10f2fc490)   										 - 2026-11-19 19:46:06,990 - logic_logger - INFO
..Order[236] {AfterFlush Event} id: 236, notes: behave test, customer_id: 64, CreatedOn: 2026-11-19, date_shipped: None, amount_total: 150.0000000000, CreatedOnDay: 2026-11-19  row: 0x10f2da720  session: 0x10f2fc490  ins_upd_dlt: ins, initial: ins - 2026-11-19 19:46:06,990 - logic_logger - INFO


Logic Phase:		ROW LOGIC		(session=0x10e4ce250) (sqlalchemy before_flush)			 - 2026-11-19 19:46:06,996 - logic_logger - INFO
..Order[236] {Update - client} id: 236, notes: behave test, customer_id: 64, CreatedOn: 2026-11-19, date_shipped: None, amount_total: 150.0000000000, CreatedOnDay:  [2026-11-19-->] 2000-01-01  row: 0x10f2db6e0  session: 0x10e4ce250  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:06,996 - logic_logger - INFO
....DailyFlow[2000-01-01] {Update - Adjusting daily_flow: order_count, order_count, order_amount, order_amount} day: 2000-01-01, order_count:  [1-->] 2, order_amount:  [150.00-->] 300.0000000000, message_received: 0, message_processed: 0, message_rejected: 0, message_pending: 0, request_received: 0, request_processed: 0, request_rejected: 0, request_pending: 0  row: 0x10e861910  session: 0x10e4ce250  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:06,996 - logic_logger - INFO
....DailyFlow[2000-01-01] {Prune Formula: message_pending [['message_received', 'message_processed', 'message_rejected']]} day: 2000-01-01, order_count:  [1-->] 2, order_amount:  [150.00-->] 300.0000000000, message_received: 0, message_processed: 0, message_rejected: 0, message_pending: 0, request_received: 0, request_processed: 0, request_rejected: 0, request_pending: 0  row: 0x10e861910  session: 0x10e4ce250  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:06,996 - logic_logger - INFO
....DailyFlow[2000-01-01] {Prune Formula: request_pending [['request_received', 'request_processed', 'request_rejected']]} day: 2000-01-01, order_count:  [1-->] 2, order_amount:  [150.00-->] 300.0000000000, message_received: 0, message_processed: 0, message_rejected: 0, message_pending: 0, request_received: 0, request_processed: 0, request_rejected: 0, request_pending: 0  row: 0x10e861910  session: 0x10e4ce250  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:06,996 - logic_logger - INFO
....DailyFlow[2026-11-19] {Update - Adjusting Old daily_flow} day: 2026-11-19, order_count:  [46-->] 45, order_amount:  [13860.00-->] 13710.0000000000, message_received: 11, message_processed: 5, message_rejected: 5, message_pending: 1, request_received: 53, request_processed: 44, request_rejected: 8, request_pending: 1  row: 0x10e8617b0  session: 0x10e4ce250  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:06,996 - logic_logger - INFO
....DailyFlow[2026-11-19] {Prune Formula: message_pending [['message_received', 'message_processed', 'message_rejected']]} day: 2026-11-19, order_count:  [46-->] 45, order_amount:  [13860.00-->] 13710.0000000000, message_received: 11, message_processed: 5, message_rejected: 5, message_pending: 1, request_received: 53, request_processed: 44, request_rejected: 8, request_pending: 1  row: 0x10e8617b0  session: 0x10e4ce250  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:06,996 - logic_logger - INFO
....DailyFlow[2026-11-19] {Prune Formula: request_pending [['request_received', 'request_processed', 'request_rejected']]} day: 2026-11-19, order_count:  [46-->] 45, order_amount:  [13860.00-->] 13710.0000000000, message_received: 11, message_processed: 5, message_rejected: 5, message_pending: 1, request_received: 53, request_processed: 44, request_rejected: 8, request_pending: 1  row: 0x10e8617b0  session: 0x10e4ce250  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:06,996 - logic_logger - INFO
Logic Phase:		COMMIT LOGIC		(session=0x10e4ce250)   										 - 2026-11-19 19:46:06,996 - logic_logger - INFO
Logic Phase:		AFTER_FLUSH LOGIC	(session=0x10e4ce250)   										 - 2026-11-19 19:46:06,997 - logic_logger - INFO
..Order[236] {AfterFlush Event} id: 236, notes: behave test, customer_id: 64, CreatedOn: 2026-11-19, date_shipped: None, amount_total: 150.0000000000, CreatedOnDay:  [2026-11-19-->] 2000-01-01  row: 0x10f2db6e0  session: 0x10e4ce250  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:06,997 - logic_logger - INFO

```
</details>

&nbsp;
&nbsp;

#### Scenario: Accepted and rejected B2B requests are counted ✅ (0.03 s)
&emsp;  Scenario: Accepted and rejected B2B requests are counted  
&emsp;&emsp;    Given a new customer "Flow Req" with credit limit 5000  
&emsp;&emsp;    And today's totals are noted  
&emsp;&emsp;    When a B2B order is placed for "Flow Req" with 1 Widget  
&emsp;&emsp;    And a B2B order is placed for "Flow Req" with 1 Sprocket  
&emsp;&emsp;    Then today's requests rose by 2 received, 1 processed, 1 rejected and 0 not yet done  
&emsp;&emsp;    And the B2B request is dated today  

<details markdown>
<summary>Rules exercised and logic log (4 transactions)</summary>


&nbsp;
&nbsp;


**Rules Used** in Scenario: Accepted and rejected B2B requests are counted
```
  DailyFlow  
    1. Derive DailyFlow.request_rejected as Count(OrderB2bRequest Where Rule.count(derive=models.DailyFlow.request_rejected, as_count_of=models.OrderB2bRequest, where=lambda row: row.error_text is not None, insert_parent=True), insert_parent)  
    2. Derive DailyFlow.request_pending as Formula (2): Rule.formula(derive=models.DailyFlow.request_pend [...]  
    3. Derive DailyFlow.request_processed as Count(OrderB2bRequest Where Rule.count(derive=models.DailyFlow.request_processed, as_count_of=models.OrderB2bRequest, where=lambda row: row.is_processed == True, insert_parent=True), insert_parent)  
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
**Logic Log** in Scenario: Accepted and rejected B2B requests are counted (4 transactions)
```
Logic Phase:		ROW LOGIC		(session=0x10e4ce470) (sqlalchemy before_flush)			 - 2026-11-19 19:46:07,012 - logic_logger - INFO
..OrderB2bRequest[None] {Insert - client} id: None, CreatedOn: None, CreatedOnDay: None, payload: {"Account": "Flow Req 1795146367006", "Notes": "behave test", "Items": [{"Name": "Widget", "QuantityOrdered": 1}]}, is_processed: False, error_text: None  row: 0x10f2ca1d0  session: 0x10e4ce470  ins_upd_dlt: ins, initial: ins - 2026-11-19 19:46:07,012 - logic_logger - INFO
..OrderB2bRequest[None] {early_row_event_all_classes - handle_all did stamping} id: None, CreatedOn: 2026-11-19 19:46:07.012886, CreatedOnDay: 2026-11-19, payload: {"Account": "Flow Req 1795146367006", "Notes": "behave test", "Items": [{"Name": "Widget", "QuantityOrdered": 1}]}, is_processed: False, error_text: None  row: 0x10f2ca1d0  session: 0x10e4ce470  ins_upd_dlt: ins, initial: ins - 2026-11-19 19:46:07,012 - logic_logger - INFO
....DailyFlow[2026-11-19] {Update - Adjusting daily_flow: request_received} day: 2026-11-19, order_count: 45, order_amount: 13710.00, message_received: 11, message_processed: 5, message_rejected: 5, message_pending: 1, request_received:  [53-->] 54, request_processed: 44, request_rejected: 8, request_pending: 1  row: 0x10e861ff0  session: 0x10e4ce470  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:07,013 - logic_logger - INFO
....DailyFlow[2026-11-19] {Prune Formula: message_pending [['message_received', 'message_processed', 'message_rejected']]} day: 2026-11-19, order_count: 45, order_amount: 13710.00, message_received: 11, message_processed: 5, message_rejected: 5, message_pending: 1, request_received:  [53-->] 54, request_processed: 44, request_rejected: 8, request_pending: 1  row: 0x10e861ff0  session: 0x10e4ce470  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:07,013 - logic_logger - INFO
....DailyFlow[2026-11-19] {Formula request_pending} day: 2026-11-19, order_count: 45, order_amount: 13710.00, message_received: 11, message_processed: 5, message_rejected: 5, message_pending: 1, request_received:  [53-->] 54, request_processed: 44, request_rejected: 8, request_pending:  [1-->] 2  row: 0x10e861ff0  session: 0x10e4ce470  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:07,013 - logic_logger - INFO
Logic Phase:		COMMIT LOGIC		(session=0x10e4ce470)   										 - 2026-11-19 19:46:07,013 - logic_logger - INFO
Logic Phase:		AFTER_FLUSH LOGIC	(session=0x10e4ce470)   										 - 2026-11-19 19:46:07,013 - logic_logger - INFO


Logic Phase:		ROW LOGIC		(session=0x10e4ce470) (sqlalchemy before_flush)			 - 2026-11-19 19:46:07,015 - logic_logger - INFO
..OrderB2bRequest[160] {Update - client} id: 160, CreatedOn: 2026-11-19 19:46:07.012886, CreatedOnDay: 2026-11-19, payload: {"Account": "Flow Req 1795146367006", "Notes": "behave test", "Items": [{"Name": "Widget", "QuantityOrdered": 1}]}, is_processed:  [False-->] True, error_text: None  row: 0x10f2ca1d0  session: 0x10e4ce470  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:07,015 - logic_logger - INFO
....DailyFlow[2026-11-19] {Update - Adjusting daily_flow: request_processed} day: 2026-11-19, order_count: 45, order_amount: 13710.00, message_received: 11, message_processed: 5, message_rejected: 5, message_pending: 1, request_received: 54, request_processed:  [44-->] 45, request_rejected: 8, request_pending: 2  row: 0x10e861ff0  session: 0x10e4ce470  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:07,015 - logic_logger - INFO
....DailyFlow[2026-11-19] {Prune Formula: message_pending [['message_received', 'message_processed', 'message_rejected']]} day: 2026-11-19, order_count: 45, order_amount: 13710.00, message_received: 11, message_processed: 5, message_rejected: 5, message_pending: 1, request_received: 54, request_processed:  [44-->] 45, request_rejected: 8, request_pending: 2  row: 0x10e861ff0  session: 0x10e4ce470  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:07,015 - logic_logger - INFO
....DailyFlow[2026-11-19] {Formula request_pending} day: 2026-11-19, order_count: 45, order_amount: 13710.00, message_received: 11, message_processed: 5, message_rejected: 5, message_pending: 1, request_received: 54, request_processed:  [44-->] 45, request_rejected: 8, request_pending:  [2-->] 1  row: 0x10e861ff0  session: 0x10e4ce470  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:07,015 - logic_logger - INFO
..Product[2] {Update - client} id: 2, name: Widget, count_suppliers: 0, unit_price: 90.0000000000  row: 0x10f2f7ee0  session: 0x10e4ce470  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:07,015 - logic_logger - INFO
..Order[None] {Insert - client} id: None, notes: behave test, customer_id: 65, CreatedOn: None, date_shipped: None, amount_total: None, CreatedOnDay: None  row: 0x10f2da7b0  session: 0x10e4ce470  ins_upd_dlt: ins, initial: ins - 2026-11-19 19:46:07,016 - logic_logger - INFO
..Order[None] {early_row_event_all_classes - handle_all did stamping} id: None, notes: behave test, customer_id: 65, CreatedOn: 2026-11-19, date_shipped: None, amount_total: None, CreatedOnDay: 2026-11-19  row: 0x10f2da7b0  session: 0x10e4ce470  ins_upd_dlt: ins, initial: ins - 2026-11-19 19:46:07,016 - logic_logger - INFO
..Order[None] {server aggregate_defaults: amount_total } id: None, notes: behave test, customer_id: 65, CreatedOn: 2026-11-19, date_shipped: None, amount_total: 0, CreatedOnDay: 2026-11-19  row: 0x10f2da7b0  session: 0x10e4ce470  ins_upd_dlt: ins, initial: ins - 2026-11-19 19:46:07,016 - logic_logger - INFO
....DailyFlow[2026-11-19] {Update - Adjusting daily_flow: order_count} day: 2026-11-19, order_count:  [45-->] 46, order_amount: 13710.00, message_received: 11, message_processed: 5, message_rejected: 5, message_pending: 1, request_received: 54, request_processed: 45, request_rejected: 8, request_pending: 1  row: 0x10e861ff0  session: 0x10e4ce470  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:07,016 - logic_logger - INFO
....DailyFlow[2026-11-19] {Prune Formula: message_pending [['message_received', 'message_processed', 'message_rejected']]} day: 2026-11-19, order_count:  [45-->] 46, order_amount: 13710.00, message_received: 11, message_processed: 5, message_rejected: 5, message_pending: 1, request_received: 54, request_processed: 45, request_rejected: 8, request_pending: 1  row: 0x10e861ff0  session: 0x10e4ce470  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:07,016 - logic_logger - INFO
....DailyFlow[2026-11-19] {Prune Formula: request_pending [['request_received', 'request_processed', 'request_rejected']]} day: 2026-11-19, order_count:  [45-->] 46, order_amount: 13710.00, message_received: 11, message_processed: 5, message_rejected: 5, message_pending: 1, request_received: 54, request_processed: 45, request_rejected: 8, request_pending: 1  row: 0x10e861ff0  session: 0x10e4ce470  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:07,016 - logic_logger - INFO
..Item[None] {Insert - client} id: None, order_id: None, product_id: None, quantity: 1, amount: None, unit_price: None  row: 0x10f2baf50  session: 0x10e4ce470  ins_upd_dlt: ins, initial: ins - 2026-11-19 19:46:07,016 - logic_logger - INFO
..Item[None] {copy_rules for role: product - unit_price} id: None, order_id: None, product_id: None, quantity: 1, amount: None, unit_price: 90.0000000000  row: 0x10f2baf50  session: 0x10e4ce470  ins_upd_dlt: ins, initial: ins - 2026-11-19 19:46:07,016 - logic_logger - INFO
..Item[None] {Formula amount} id: None, order_id: None, product_id: None, quantity: 1, amount: 90.0000000000, unit_price: 90.0000000000  row: 0x10f2baf50  session: 0x10e4ce470  ins_upd_dlt: ins, initial: ins - 2026-11-19 19:46:07,016 - logic_logger - INFO
....Order[None] {Update - Adjusting order: amount_total} id: None, notes: behave test, customer_id: 65, CreatedOn: 2026-11-19, date_shipped: None, amount_total:  [0-->] 90.0000000000, CreatedOnDay: 2026-11-19  row: 0x10f2da7b0  session: 0x10e4ce470  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:07,016 - logic_logger - INFO
......DailyFlow[2026-11-19] {Update - Adjusting daily_flow: order_amount} day: 2026-11-19, order_count: 46, order_amount:  [13710.00-->] 13800.0000000000, message_received: 11, message_processed: 5, message_rejected: 5, message_pending: 1, request_received: 54, request_processed: 45, request_rejected: 8, request_pending: 1  row: 0x10e861ff0  session: 0x10e4ce470  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:07,016 - logic_logger - INFO
......DailyFlow[2026-11-19] {Prune Formula: message_pending [['message_received', 'message_processed', 'message_rejected']]} day: 2026-11-19, order_count: 46, order_amount:  [13710.00-->] 13800.0000000000, message_received: 11, message_processed: 5, message_rejected: 5, message_pending: 1, request_received: 54, request_processed: 45, request_rejected: 8, request_pending: 1  row: 0x10e861ff0  session: 0x10e4ce470  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:07,016 - logic_logger - INFO
......DailyFlow[2026-11-19] {Prune Formula: request_pending [['request_received', 'request_processed', 'request_rejected']]} day: 2026-11-19, order_count: 46, order_amount:  [13710.00-->] 13800.0000000000, message_received: 11, message_processed: 5, message_rejected: 5, message_pending: 1, request_received: 54, request_processed: 45, request_rejected: 8, request_pending: 1  row: 0x10e861ff0  session: 0x10e4ce470  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:07,016 - logic_logger - INFO
......Customer[65] {Update - Adjusting customer: balance} id: 65, name: Flow Req 1795146367006, balance:  [0E-10-->] 90.0000000000, credit_limit: 5000.0000000000, email: None, email_opt_out: None  row: 0x10f2e2dd0  session: 0x10e4ce470  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:07,016 - logic_logger - INFO
Logic Phase:		COMMIT LOGIC		(session=0x10e4ce470)   										 - 2026-11-19 19:46:07,016 - logic_logger - INFO
Logic Phase:		AFTER_FLUSH LOGIC	(session=0x10e4ce470)   										 - 2026-11-19 19:46:07,017 - logic_logger - INFO
..Order[237] {AfterFlush Event} id: 237, notes: behave test, customer_id: 65, CreatedOn: 2026-11-19, date_shipped: None, amount_total: 90.0000000000, CreatedOnDay: 2026-11-19  row: 0x10f2da7b0  session: 0x10e4ce470  ins_upd_dlt: ins, initial: ins - 2026-11-19 19:46:07,017 - logic_logger - INFO


Logic Phase:		ROW LOGIC		(session=0x10e433f00) (sqlalchemy before_flush)			 - 2026-11-19 19:46:07,019 - logic_logger - INFO
..OrderB2bRequest[None] {Insert - client} id: None, CreatedOn: None, CreatedOnDay: None, payload: {"Account": "Flow Req 1795146367006", "Notes": "behave test", "Items": [{"Name": "Sprocket", "QuantityOrdered": 1}]}, is_processed: False, error_text: None  row: 0x10f30d8d0  session: 0x10e433f00  ins_upd_dlt: ins, initial: ins - 2026-11-19 19:46:07,019 - logic_logger - INFO
..OrderB2bRequest[None] {early_row_event_all_classes - handle_all did stamping} id: None, CreatedOn: 2026-11-19 19:46:07.019728, CreatedOnDay: 2026-11-19, payload: {"Account": "Flow Req 1795146367006", "Notes": "behave test", "Items": [{"Name": "Sprocket", "QuantityOrdered": 1}]}, is_processed: False, error_text: None  row: 0x10f30d8d0  session: 0x10e433f00  ins_upd_dlt: ins, initial: ins - 2026-11-19 19:46:07,019 - logic_logger - INFO
....DailyFlow[2026-11-19] {Update - Adjusting daily_flow: request_received} day: 2026-11-19, order_count: 46, order_amount: 13800.00, message_received: 11, message_processed: 5, message_rejected: 5, message_pending: 1, request_received:  [54-->] 55, request_processed: 45, request_rejected: 8, request_pending: 1  row: 0x10e861700  session: 0x10e433f00  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:07,020 - logic_logger - INFO
....DailyFlow[2026-11-19] {Prune Formula: message_pending [['message_received', 'message_processed', 'message_rejected']]} day: 2026-11-19, order_count: 46, order_amount: 13800.00, message_received: 11, message_processed: 5, message_rejected: 5, message_pending: 1, request_received:  [54-->] 55, request_processed: 45, request_rejected: 8, request_pending: 1  row: 0x10e861700  session: 0x10e433f00  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:07,020 - logic_logger - INFO
....DailyFlow[2026-11-19] {Formula request_pending} day: 2026-11-19, order_count: 46, order_amount: 13800.00, message_received: 11, message_processed: 5, message_rejected: 5, message_pending: 1, request_received:  [54-->] 55, request_processed: 45, request_rejected: 8, request_pending:  [1-->] 2  row: 0x10e861700  session: 0x10e433f00  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:07,020 - logic_logger - INFO
Logic Phase:		COMMIT LOGIC		(session=0x10e433f00)   										 - 2026-11-19 19:46:07,020 - logic_logger - INFO
Logic Phase:		AFTER_FLUSH LOGIC	(session=0x10e433f00)   										 - 2026-11-19 19:46:07,020 - logic_logger - INFO


Logic Phase:		ROW LOGIC		(session=0x10e433f00) (sqlalchemy before_flush)			 - 2026-11-19 19:46:07,022 - logic_logger - INFO
..OrderB2bRequest[161] {Update - client} id: 161, CreatedOn: 2026-11-19 19:46:07.019728, CreatedOnDay: 2026-11-19, payload: {"Account": "Flow Req 1795146367006", "Notes": "behave test", "Items": [{"Name": "Sprocket", "QuantityOrdered": 1}]}, is_processed: False, error_text:  [None-->] ('Lookup failed: missing parent', <Item (transient 4548776272)>, 'Product', "{'Name': 'Sprocket', 'QuantityOrdered': 1}")  row: 0x10f30d8d0  session: 0x10e433f00  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:07,022 - logic_logger - INFO
....DailyFlow[2026-11-19] {Update - Adjusting daily_flow: request_rejected} day: 2026-11-19, order_count: 46, order_amount: 13800.00, message_received: 11, message_processed: 5, message_rejected: 5, message_pending: 1, request_received: 55, request_processed: 45, request_rejected:  [8-->] 9, request_pending: 2  row: 0x10e861700  session: 0x10e433f00  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:07,022 - logic_logger - INFO
....DailyFlow[2026-11-19] {Prune Formula: message_pending [['message_received', 'message_processed', 'message_rejected']]} day: 2026-11-19, order_count: 46, order_amount: 13800.00, message_received: 11, message_processed: 5, message_rejected: 5, message_pending: 1, request_received: 55, request_processed: 45, request_rejected:  [8-->] 9, request_pending: 2  row: 0x10e861700  session: 0x10e433f00  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:07,022 - logic_logger - INFO
....DailyFlow[2026-11-19] {Formula request_pending} day: 2026-11-19, order_count: 46, order_amount: 13800.00, message_received: 11, message_processed: 5, message_rejected: 5, message_pending: 1, request_received: 55, request_processed: 45, request_rejected:  [8-->] 9, request_pending:  [2-->] 1  row: 0x10e861700  session: 0x10e433f00  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:07,022 - logic_logger - INFO
Logic Phase:		COMMIT LOGIC		(session=0x10e433f00)   										 - 2026-11-19 19:46:07,022 - logic_logger - INFO
Logic Phase:		AFTER_FLUSH LOGIC	(session=0x10e433f00)   										 - 2026-11-19 19:46:07,023 - logic_logger - INFO

```
</details>

&nbsp;
&nbsp;

#### Scenario: A request set back to not processed counts as not yet done ✅ (0.02 s)
&emsp;  Scenario: A request set back to not processed counts as not yet done  
&emsp;&emsp;    Given a new customer "Flow Req Undo" with credit limit 5000  
&emsp;&emsp;    And a B2B order is placed for "Flow Req Undo" with 1 Widget  
&emsp;&emsp;    And today's totals are noted  
&emsp;&emsp;    When the B2B request is set back to not processed  
&emsp;&emsp;    Then today's requests rose by 0 received, -1 processed, 0 rejected and 1 not yet done  

<details markdown>
<summary>Rules exercised and logic log (3 transactions)</summary>


&nbsp;
&nbsp;


**Rules Used** in Scenario: A request set back to not processed counts as not yet done
```
  DailyFlow  
    1. Derive DailyFlow.request_rejected as Count(OrderB2bRequest Where Rule.count(derive=models.DailyFlow.request_rejected, as_count_of=models.OrderB2bRequest, where=lambda row: row.error_text is not None, insert_parent=True), insert_parent)  
    2. Derive DailyFlow.request_pending as Formula (2): Rule.formula(derive=models.DailyFlow.request_pend [...]  
    3. Derive DailyFlow.request_processed as Count(OrderB2bRequest Where Rule.count(derive=models.DailyFlow.request_processed, as_count_of=models.OrderB2bRequest, where=lambda row: row.is_processed == True, insert_parent=True), insert_parent)  
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
**Logic Log** in Scenario: A request set back to not processed counts as not yet done (3 transactions)
```
Logic Phase:		ROW LOGIC		(session=0x10e4cfbd0) (sqlalchemy before_flush)			 - 2026-11-19 19:46:07,039 - logic_logger - INFO
..OrderB2bRequest[None] {Insert - client} id: None, CreatedOn: None, CreatedOnDay: None, payload: {"Account": "Flow Req Undo 1795146367035", "Notes": "behave test", "Items": [{"Name": "Widget", "QuantityOrdered": 1}]}, is_processed: False, error_text: None  row: 0x10e2c68d0  session: 0x10e4cfbd0  ins_upd_dlt: ins, initial: ins - 2026-11-19 19:46:07,039 - logic_logger - INFO
..OrderB2bRequest[None] {early_row_event_all_classes - handle_all did stamping} id: None, CreatedOn: 2026-11-19 19:46:07.039655, CreatedOnDay: 2026-11-19, payload: {"Account": "Flow Req Undo 1795146367035", "Notes": "behave test", "Items": [{"Name": "Widget", "QuantityOrdered": 1}]}, is_processed: False, error_text: None  row: 0x10e2c68d0  session: 0x10e4cfbd0  ins_upd_dlt: ins, initial: ins - 2026-11-19 19:46:07,039 - logic_logger - INFO
....DailyFlow[2026-11-19] {Update - Adjusting daily_flow: request_received} day: 2026-11-19, order_count: 46, order_amount: 13800.00, message_received: 11, message_processed: 5, message_rejected: 5, message_pending: 1, request_received:  [55-->] 56, request_processed: 45, request_rejected: 9, request_pending: 1  row: 0x10e861700  session: 0x10e4cfbd0  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:07,040 - logic_logger - INFO
....DailyFlow[2026-11-19] {Prune Formula: message_pending [['message_received', 'message_processed', 'message_rejected']]} day: 2026-11-19, order_count: 46, order_amount: 13800.00, message_received: 11, message_processed: 5, message_rejected: 5, message_pending: 1, request_received:  [55-->] 56, request_processed: 45, request_rejected: 9, request_pending: 1  row: 0x10e861700  session: 0x10e4cfbd0  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:07,040 - logic_logger - INFO
....DailyFlow[2026-11-19] {Formula request_pending} day: 2026-11-19, order_count: 46, order_amount: 13800.00, message_received: 11, message_processed: 5, message_rejected: 5, message_pending: 1, request_received:  [55-->] 56, request_processed: 45, request_rejected: 9, request_pending:  [1-->] 2  row: 0x10e861700  session: 0x10e4cfbd0  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:07,040 - logic_logger - INFO
Logic Phase:		COMMIT LOGIC		(session=0x10e4cfbd0)   										 - 2026-11-19 19:46:07,040 - logic_logger - INFO
Logic Phase:		AFTER_FLUSH LOGIC	(session=0x10e4cfbd0)   										 - 2026-11-19 19:46:07,040 - logic_logger - INFO


Logic Phase:		ROW LOGIC		(session=0x10e4cfbd0) (sqlalchemy before_flush)			 - 2026-11-19 19:46:07,042 - logic_logger - INFO
..OrderB2bRequest[162] {Update - client} id: 162, CreatedOn: 2026-11-19 19:46:07.039655, CreatedOnDay: 2026-11-19, payload: {"Account": "Flow Req Undo 1795146367035", "Notes": "behave test", "Items": [{"Name": "Widget", "QuantityOrdered": 1}]}, is_processed:  [False-->] True, error_text: None  row: 0x10e2c68d0  session: 0x10e4cfbd0  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:07,042 - logic_logger - INFO
....DailyFlow[2026-11-19] {Update - Adjusting daily_flow: request_processed} day: 2026-11-19, order_count: 46, order_amount: 13800.00, message_received: 11, message_processed: 5, message_rejected: 5, message_pending: 1, request_received: 56, request_processed:  [45-->] 46, request_rejected: 9, request_pending: 2  row: 0x10e861700  session: 0x10e4cfbd0  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:07,042 - logic_logger - INFO
....DailyFlow[2026-11-19] {Prune Formula: message_pending [['message_received', 'message_processed', 'message_rejected']]} day: 2026-11-19, order_count: 46, order_amount: 13800.00, message_received: 11, message_processed: 5, message_rejected: 5, message_pending: 1, request_received: 56, request_processed:  [45-->] 46, request_rejected: 9, request_pending: 2  row: 0x10e861700  session: 0x10e4cfbd0  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:07,042 - logic_logger - INFO
....DailyFlow[2026-11-19] {Formula request_pending} day: 2026-11-19, order_count: 46, order_amount: 13800.00, message_received: 11, message_processed: 5, message_rejected: 5, message_pending: 1, request_received: 56, request_processed:  [45-->] 46, request_rejected: 9, request_pending:  [2-->] 1  row: 0x10e861700  session: 0x10e4cfbd0  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:07,042 - logic_logger - INFO
..Product[2] {Update - client} id: 2, name: Widget, count_suppliers: 0, unit_price: 90.0000000000  row: 0x10f2f6820  session: 0x10e4cfbd0  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:07,042 - logic_logger - INFO
..Order[None] {Insert - client} id: None, notes: behave test, customer_id: 66, CreatedOn: None, date_shipped: None, amount_total: None, CreatedOnDay: None  row: 0x10f2da450  session: 0x10e4cfbd0  ins_upd_dlt: ins, initial: ins - 2026-11-19 19:46:07,042 - logic_logger - INFO
..Order[None] {early_row_event_all_classes - handle_all did stamping} id: None, notes: behave test, customer_id: 66, CreatedOn: 2026-11-19, date_shipped: None, amount_total: None, CreatedOnDay: 2026-11-19  row: 0x10f2da450  session: 0x10e4cfbd0  ins_upd_dlt: ins, initial: ins - 2026-11-19 19:46:07,042 - logic_logger - INFO
..Order[None] {server aggregate_defaults: amount_total } id: None, notes: behave test, customer_id: 66, CreatedOn: 2026-11-19, date_shipped: None, amount_total: 0, CreatedOnDay: 2026-11-19  row: 0x10f2da450  session: 0x10e4cfbd0  ins_upd_dlt: ins, initial: ins - 2026-11-19 19:46:07,042 - logic_logger - INFO
....DailyFlow[2026-11-19] {Update - Adjusting daily_flow: order_count} day: 2026-11-19, order_count:  [46-->] 47, order_amount: 13800.00, message_received: 11, message_processed: 5, message_rejected: 5, message_pending: 1, request_received: 56, request_processed: 46, request_rejected: 9, request_pending: 1  row: 0x10e861700  session: 0x10e4cfbd0  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:07,042 - logic_logger - INFO
....DailyFlow[2026-11-19] {Prune Formula: message_pending [['message_received', 'message_processed', 'message_rejected']]} day: 2026-11-19, order_count:  [46-->] 47, order_amount: 13800.00, message_received: 11, message_processed: 5, message_rejected: 5, message_pending: 1, request_received: 56, request_processed: 46, request_rejected: 9, request_pending: 1  row: 0x10e861700  session: 0x10e4cfbd0  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:07,042 - logic_logger - INFO
....DailyFlow[2026-11-19] {Prune Formula: request_pending [['request_received', 'request_processed', 'request_rejected']]} day: 2026-11-19, order_count:  [46-->] 47, order_amount: 13800.00, message_received: 11, message_processed: 5, message_rejected: 5, message_pending: 1, request_received: 56, request_processed: 46, request_rejected: 9, request_pending: 1  row: 0x10e861700  session: 0x10e4cfbd0  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:07,042 - logic_logger - INFO
..Item[None] {Insert - client} id: None, order_id: None, product_id: None, quantity: 1, amount: None, unit_price: None  row: 0x10f2e2a50  session: 0x10e4cfbd0  ins_upd_dlt: ins, initial: ins - 2026-11-19 19:46:07,043 - logic_logger - INFO
..Item[None] {copy_rules for role: product - unit_price} id: None, order_id: None, product_id: None, quantity: 1, amount: None, unit_price: 90.0000000000  row: 0x10f2e2a50  session: 0x10e4cfbd0  ins_upd_dlt: ins, initial: ins - 2026-11-19 19:46:07,043 - logic_logger - INFO
..Item[None] {Formula amount} id: None, order_id: None, product_id: None, quantity: 1, amount: 90.0000000000, unit_price: 90.0000000000  row: 0x10f2e2a50  session: 0x10e4cfbd0  ins_upd_dlt: ins, initial: ins - 2026-11-19 19:46:07,043 - logic_logger - INFO
....Order[None] {Update - Adjusting order: amount_total} id: None, notes: behave test, customer_id: 66, CreatedOn: 2026-11-19, date_shipped: None, amount_total:  [0-->] 90.0000000000, CreatedOnDay: 2026-11-19  row: 0x10f2da450  session: 0x10e4cfbd0  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:07,043 - logic_logger - INFO
......DailyFlow[2026-11-19] {Update - Adjusting daily_flow: order_amount} day: 2026-11-19, order_count: 47, order_amount:  [13800.00-->] 13890.0000000000, message_received: 11, message_processed: 5, message_rejected: 5, message_pending: 1, request_received: 56, request_processed: 46, request_rejected: 9, request_pending: 1  row: 0x10e861700  session: 0x10e4cfbd0  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:07,043 - logic_logger - INFO
......DailyFlow[2026-11-19] {Prune Formula: message_pending [['message_received', 'message_processed', 'message_rejected']]} day: 2026-11-19, order_count: 47, order_amount:  [13800.00-->] 13890.0000000000, message_received: 11, message_processed: 5, message_rejected: 5, message_pending: 1, request_received: 56, request_processed: 46, request_rejected: 9, request_pending: 1  row: 0x10e861700  session: 0x10e4cfbd0  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:07,043 - logic_logger - INFO
......DailyFlow[2026-11-19] {Prune Formula: request_pending [['request_received', 'request_processed', 'request_rejected']]} day: 2026-11-19, order_count: 47, order_amount:  [13800.00-->] 13890.0000000000, message_received: 11, message_processed: 5, message_rejected: 5, message_pending: 1, request_received: 56, request_processed: 46, request_rejected: 9, request_pending: 1  row: 0x10e861700  session: 0x10e4cfbd0  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:07,043 - logic_logger - INFO
......Customer[66] {Update - Adjusting customer: balance} id: 66, name: Flow Req Undo 1795146367035, balance:  [0E-10-->] 90.0000000000, credit_limit: 5000.0000000000, email: None, email_opt_out: None  row: 0x10f2c86d0  session: 0x10e4cfbd0  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:07,043 - logic_logger - INFO
Logic Phase:		COMMIT LOGIC		(session=0x10e4cfbd0)   										 - 2026-11-19 19:46:07,043 - logic_logger - INFO
Logic Phase:		AFTER_FLUSH LOGIC	(session=0x10e4cfbd0)   										 - 2026-11-19 19:46:07,044 - logic_logger - INFO
..Order[238] {AfterFlush Event} id: 238, notes: behave test, customer_id: 66, CreatedOn: 2026-11-19, date_shipped: None, amount_total: 90.0000000000, CreatedOnDay: 2026-11-19  row: 0x10f2da450  session: 0x10e4cfbd0  ins_upd_dlt: ins, initial: ins - 2026-11-19 19:46:07,044 - logic_logger - INFO


Logic Phase:		ROW LOGIC		(session=0x10e4ce470) (sqlalchemy before_flush)			 - 2026-11-19 19:46:07,048 - logic_logger - INFO
..OrderB2bRequest[162] {Update - client} id: 162, CreatedOn: 2026-11-19 19:46:07.039655, CreatedOnDay: 2026-11-19, payload: {"Account": "Flow Req Undo 1795146367035", "Notes": "behave test", "Items": [{"Name": "Widget", "QuantityOrdered": 1}]}, is_processed:  [True-->] False, error_text: None  row: 0x10f30cc50  session: 0x10e4ce470  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:07,048 - logic_logger - INFO
....DailyFlow[2026-11-19] {Update - Adjusting daily_flow: request_processed} day: 2026-11-19, order_count: 47, order_amount: 13890.00, message_received: 11, message_processed: 5, message_rejected: 5, message_pending: 1, request_received: 56, request_processed:  [46-->] 45, request_rejected: 9, request_pending: 1  row: 0x10e8622b0  session: 0x10e4ce470  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:07,049 - logic_logger - INFO
....DailyFlow[2026-11-19] {Prune Formula: message_pending [['message_received', 'message_processed', 'message_rejected']]} day: 2026-11-19, order_count: 47, order_amount: 13890.00, message_received: 11, message_processed: 5, message_rejected: 5, message_pending: 1, request_received: 56, request_processed:  [46-->] 45, request_rejected: 9, request_pending: 1  row: 0x10e8622b0  session: 0x10e4ce470  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:07,049 - logic_logger - INFO
....DailyFlow[2026-11-19] {Formula request_pending} day: 2026-11-19, order_count: 47, order_amount: 13890.00, message_received: 11, message_processed: 5, message_rejected: 5, message_pending: 1, request_received: 56, request_processed:  [46-->] 45, request_rejected: 9, request_pending:  [1-->] 2  row: 0x10e8622b0  session: 0x10e4ce470  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:07,049 - logic_logger - INFO
Logic Phase:		COMMIT LOGIC		(session=0x10e4ce470)   										 - 2026-11-19 19:46:07,049 - logic_logger - INFO
Logic Phase:		AFTER_FLUSH LOGIC	(session=0x10e4ce470)   										 - 2026-11-19 19:46:07,049 - logic_logger - INFO

```
</details>

&nbsp;
&nbsp;

#### Scenario: An accepted message is counted ✅ (0.55 s)
&emsp;  Scenario: An accepted message is counted  
&emsp;&emsp;    Given a new customer "Flow Msg" with credit limit 5000  
&emsp;&emsp;    And today's totals are noted  
&emsp;&emsp;    When an order message for "Flow Msg" with 1 Widget and 2 Gadget is delivered to topic order_b2b  
&emsp;&emsp;    Then the message is processed  
&emsp;&emsp;    And today's messages rose by 1 received, 1 processed, 0 rejected and 0 not yet done  
&emsp;&emsp;    And the message is dated today  

<details markdown>
<summary>Rules exercised and logic log (3 transactions)</summary>


&nbsp;
&nbsp;


**Rules Used** in Scenario: An accepted message is counted
```
  DailyFlow  
    1. Derive DailyFlow.message_rejected as Count(OrderB2bMessage Where Rule.count(derive=models.DailyFlow.message_rejected, as_count_of=models.OrderB2bMessage, where=lambda row: row.error_text is not None, insert_parent=True), insert_parent)  
    2. Derive DailyFlow.message_received as Count(OrderB2bMessage Where  - None, insert_parent)  
    3. Derive DailyFlow.message_pending as Formula (1): Rule.formula(derive=models.DailyFlow.message_pend [...]  
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
**Logic Log** in Scenario: An accepted message is counted (3 transactions)
```
Logic Phase:		ROW LOGIC		(session=0x10e4cf790) (sqlalchemy before_flush)			 - 2026-11-19 19:46:07,065 - logic_logger - INFO
..OrderB2bMessage[None] {Insert - client} id: None, CreatedOn: None, CreatedOnDay: None, payload: {..., is_processed: False, error_text: None  row: 0x10f1fec50  session: 0x10e4cf790  ins_upd_dlt: ins, initial: ins - 2026-11-19 19:46:07,065 - logic_logger - INFO
..OrderB2bMessage[None] {early_row_event_all_classes - handle_all did stamping} id: None, CreatedOn: 2026-11-19 19:46:07.065839, CreatedOnDay: 2026-11-19, payload: {..., is_processed: False, error_text: None  row: 0x10f1fec50  session: 0x10e4cf790  ins_upd_dlt: ins, initial: ins - 2026-11-19 19:46:07,065 - logic_logger - INFO
....DailyFlow[2026-11-19] {Update - Adjusting daily_flow: message_received} day: 2026-11-19, order_count: 47, order_amount: 13890.00, message_received:  [11-->] 12, message_processed: 5, message_rejected: 5, message_pending: 1, request_received: 56, request_processed: 45, request_rejected: 9, request_pending: 2  row: 0x10e8620a0  session: 0x10e4cf790  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:07,066 - logic_logger - INFO
....DailyFlow[2026-11-19] {Formula message_pending} day: 2026-11-19, order_count: 47, order_amount: 13890.00, message_received:  [11-->] 12, message_processed: 5, message_rejected: 5, message_pending:  [1-->] 2, request_received: 56, request_processed: 45, request_rejected: 9, request_pending: 2  row: 0x10e8620a0  session: 0x10e4cf790  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:07,066 - logic_logger - INFO
....DailyFlow[2026-11-19] {Prune Formula: request_pending [['request_received', 'request_processed', 'request_rejected']]} day: 2026-11-19, order_count: 47, order_amount: 13890.00, message_received:  [11-->] 12, message_processed: 5, message_rejected: 5, message_pending:  [1-->] 2, request_received: 56, request_processed: 45, request_rejected: 9, request_pending: 2  row: 0x10e8620a0  session: 0x10e4cf790  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:07,066 - logic_logger - INFO
Logic Phase:		COMMIT LOGIC		(session=0x10e4cf790)   										 - 2026-11-19 19:46:07,066 - logic_logger - INFO
Logic Phase:		AFTER_FLUSH LOGIC	(session=0x10e4cf790)   										 - 2026-11-19 19:46:07,067 - logic_logger - INFO
..OrderB2bMessage[96] {AfterFlush Event} id: 96, CreatedOn: 2026-11-19 19:46:07.065839, CreatedOnDay: 2026-11-19, payload: {..., is_processed: False, error_text: None  row: 0x10f1fec50  session: 0x10e4cf790  ins_upd_dlt: ins, initial: ins - 2026-11-19 19:46:07,067 - logic_logger - INFO


Logic Phase:		ROW LOGIC		(session=0x10f2fc050) (sqlalchemy before_flush)			 - 2026-11-19 19:46:07,072 - logic_logger - INFO
..Order[None] {Insert - client} id: None, notes: behave kafka message, customer_id: 67, CreatedOn: None, date_shipped: None, amount_total: None, CreatedOnDay: None  row: 0x10f2a76e0  session: 0x10f2fc050  ins_upd_dlt: ins, initial: ins - 2026-11-19 19:46:07,072 - logic_logger - INFO
..Order[None] {early_row_event_all_classes - handle_all did stamping} id: None, notes: behave kafka message, customer_id: 67, CreatedOn: 2026-11-19, date_shipped: None, amount_total: None, CreatedOnDay: 2026-11-19  row: 0x10f2a76e0  session: 0x10f2fc050  ins_upd_dlt: ins, initial: ins - 2026-11-19 19:46:07,072 - logic_logger - INFO
..Order[None] {server aggregate_defaults: amount_total } id: None, notes: behave kafka message, customer_id: 67, CreatedOn: 2026-11-19, date_shipped: None, amount_total: 0, CreatedOnDay: 2026-11-19  row: 0x10f2a76e0  session: 0x10f2fc050  ins_upd_dlt: ins, initial: ins - 2026-11-19 19:46:07,072 - logic_logger - INFO
....DailyFlow[2026-11-19] {Update - Adjusting daily_flow: order_count} day: 2026-11-19, order_count:  [47-->] 48, order_amount: 13890.00, message_received: 12, message_processed: 5, message_rejected: 5, message_pending: 2, request_received: 56, request_processed: 45, request_rejected: 9, request_pending: 2  row: 0x10e862200  session: 0x10f2fc050  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:07,073 - logic_logger - INFO
....DailyFlow[2026-11-19] {Prune Formula: message_pending [['message_received', 'message_processed', 'message_rejected']]} day: 2026-11-19, order_count:  [47-->] 48, order_amount: 13890.00, message_received: 12, message_processed: 5, message_rejected: 5, message_pending: 2, request_received: 56, request_processed: 45, request_rejected: 9, request_pending: 2  row: 0x10e862200  session: 0x10f2fc050  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:07,073 - logic_logger - INFO
....DailyFlow[2026-11-19] {Prune Formula: request_pending [['request_received', 'request_processed', 'request_rejected']]} day: 2026-11-19, order_count:  [47-->] 48, order_amount: 13890.00, message_received: 12, message_processed: 5, message_rejected: 5, message_pending: 2, request_received: 56, request_processed: 45, request_rejected: 9, request_pending: 2  row: 0x10e862200  session: 0x10f2fc050  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:07,073 - logic_logger - INFO
..Item[None] {Insert - client} id: None, order_id: None, product_id: 2, quantity: 1, amount: None, unit_price: None  row: 0x10f20c8d0  session: 0x10f2fc050  ins_upd_dlt: ins, initial: ins - 2026-11-19 19:46:07,073 - logic_logger - INFO
..Item[None] {copy_rules for role: product - unit_price} id: None, order_id: None, product_id: 2, quantity: 1, amount: None, unit_price: 90.0000000000  row: 0x10f20c8d0  session: 0x10f2fc050  ins_upd_dlt: ins, initial: ins - 2026-11-19 19:46:07,073 - logic_logger - INFO
..Item[None] {Formula amount} id: None, order_id: None, product_id: 2, quantity: 1, amount: 90.0000000000, unit_price: 90.0000000000  row: 0x10f20c8d0  session: 0x10f2fc050  ins_upd_dlt: ins, initial: ins - 2026-11-19 19:46:07,073 - logic_logger - INFO
....Order[None] {Update - Adjusting order: amount_total} id: None, notes: behave kafka message, customer_id: 67, CreatedOn: 2026-11-19, date_shipped: None, amount_total:  [0-->] 90.0000000000, CreatedOnDay: 2026-11-19  row: 0x10f2a76e0  session: 0x10f2fc050  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:07,073 - logic_logger - INFO
......DailyFlow[2026-11-19] {Update - Adjusting daily_flow: order_amount} day: 2026-11-19, order_count: 48, order_amount:  [13890.00-->] 13980.0000000000, message_received: 12, message_processed: 5, message_rejected: 5, message_pending: 2, request_received: 56, request_processed: 45, request_rejected: 9, request_pending: 2  row: 0x10e862200  session: 0x10f2fc050  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:07,073 - logic_logger - INFO
......DailyFlow[2026-11-19] {Prune Formula: message_pending [['message_received', 'message_processed', 'message_rejected']]} day: 2026-11-19, order_count: 48, order_amount:  [13890.00-->] 13980.0000000000, message_received: 12, message_processed: 5, message_rejected: 5, message_pending: 2, request_received: 56, request_processed: 45, request_rejected: 9, request_pending: 2  row: 0x10e862200  session: 0x10f2fc050  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:07,073 - logic_logger - INFO
......DailyFlow[2026-11-19] {Prune Formula: request_pending [['request_received', 'request_processed', 'request_rejected']]} day: 2026-11-19, order_count: 48, order_amount:  [13890.00-->] 13980.0000000000, message_received: 12, message_processed: 5, message_rejected: 5, message_pending: 2, request_received: 56, request_processed: 45, request_rejected: 9, request_pending: 2  row: 0x10e862200  session: 0x10f2fc050  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:07,073 - logic_logger - INFO
......Customer[67] {Update - Adjusting customer: balance} id: 67, name: Flow Msg 1795146367057, balance:  [0E-10-->] 90.0000000000, credit_limit: 5000.0000000000, email: None, email_opt_out: None  row: 0x10f3579d0  session: 0x10f2fc050  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:07,074 - logic_logger - INFO
..Item[None] {Insert - client} id: None, order_id: None, product_id: 1, quantity: 2, amount: None, unit_price: None  row: 0x10f2e2dd0  session: 0x10f2fc050  ins_upd_dlt: ins, initial: ins - 2026-11-19 19:46:07,074 - logic_logger - INFO
..Item[None] {copy_rules for role: product - unit_price} id: None, order_id: None, product_id: 1, quantity: 2, amount: None, unit_price: 150.0000000000  row: 0x10f2e2dd0  session: 0x10f2fc050  ins_upd_dlt: ins, initial: ins - 2026-11-19 19:46:07,074 - logic_logger - INFO
..Item[None] {Formula amount} id: None, order_id: None, product_id: 1, quantity: 2, amount: 300.0000000000, unit_price: 150.0000000000  row: 0x10f2e2dd0  session: 0x10f2fc050  ins_upd_dlt: ins, initial: ins - 2026-11-19 19:46:07,074 - logic_logger - INFO
....Order[None] {Update - Adjusting order: amount_total} id: None, notes: behave kafka message, customer_id: 67, CreatedOn: 2026-11-19, date_shipped: None, amount_total:  [90.0000000000-->] 390.0000000000, CreatedOnDay: 2026-11-19  row: 0x10f2a76e0  session: 0x10f2fc050  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:07,074 - logic_logger - INFO
......DailyFlow[2026-11-19] {Update - Adjusting daily_flow: order_amount} day: 2026-11-19, order_count: 48, order_amount:  [13980.0000000000-->] 14280.0000000000, message_received: 12, message_processed: 5, message_rejected: 5, message_pending: 2, request_received: 56, request_processed: 45, request_rejected: 9, request_pending: 2  row: 0x10e862200  session: 0x10f2fc050  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:07,074 - logic_logger - INFO
......DailyFlow[2026-11-19] {Prune Formula: message_pending [['message_received', 'message_processed', 'message_rejected']]} day: 2026-11-19, order_count: 48, order_amount:  [13980.0000000000-->] 14280.0000000000, message_received: 12, message_processed: 5, message_rejected: 5, message_pending: 2, request_received: 56, request_processed: 45, request_rejected: 9, request_pending: 2  row: 0x10e862200  session: 0x10f2fc050  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:07,074 - logic_logger - INFO
......DailyFlow[2026-11-19] {Prune Formula: request_pending [['request_received', 'request_processed', 'request_rejected']]} day: 2026-11-19, order_count: 48, order_amount:  [13980.0000000000-->] 14280.0000000000, message_received: 12, message_processed: 5, message_rejected: 5, message_pending: 2, request_received: 56, request_processed: 45, request_rejected: 9, request_pending: 2  row: 0x10e862200  session: 0x10f2fc050  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:07,074 - logic_logger - INFO
......Customer[67] {Update - Adjusting customer: balance} id: 67, name: Flow Msg 1795146367057, balance:  [90.0000000000-->] 390.0000000000, credit_limit: 5000.0000000000, email: None, email_opt_out: None  row: 0x10f3579d0  session: 0x10f2fc050  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:07,074 - logic_logger - INFO
Logic Phase:		COMMIT LOGIC		(session=0x10f2fc050)   										 - 2026-11-19 19:46:07,074 - logic_logger - INFO
Logic Phase:		AFTER_FLUSH LOGIC	(session=0x10f2fc050)   										 - 2026-11-19 19:46:07,075 - logic_logger - INFO
..Order[239] {AfterFlush Event} id: 239, notes: behave kafka message, customer_id: 67, CreatedOn: 2026-11-19, date_shipped: None, amount_total: 390.0000000000, CreatedOnDay: 2026-11-19  row: 0x10f2a76e0  session: 0x10f2fc050  ins_upd_dlt: ins, initial: ins - 2026-11-19 19:46:07,075 - logic_logger - INFO


Logic Phase:		ROW LOGIC		(session=0x10f2fc050) (sqlalchemy before_flush)			 - 2026-11-19 19:46:07,075 - logic_logger - INFO
..OrderB2bMessage[96] {Update - client} id: 96, CreatedOn: 2026-11-19 19:46:07.065839, CreatedOnDay: 2026-11-19, payload: {..., is_processed:  [False-->] True, error_text: None  row: 0x10f2e2e50  session: 0x10f2fc050  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:07,075 - logic_logger - INFO
....DailyFlow[2026-11-19] {Update - Adjusting daily_flow: message_processed} day: 2026-11-19, order_count: 48, order_amount: 14280.0000000000, message_received: 12, message_processed:  [5-->] 6, message_rejected: 5, message_pending: 2, request_received: 56, request_processed: 45, request_rejected: 9, request_pending: 2  row: 0x10e862200  session: 0x10f2fc050  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:07,075 - logic_logger - INFO
....DailyFlow[2026-11-19] {Formula message_pending} day: 2026-11-19, order_count: 48, order_amount: 14280.0000000000, message_received: 12, message_processed:  [5-->] 6, message_rejected: 5, message_pending:  [2-->] 1, request_received: 56, request_processed: 45, request_rejected: 9, request_pending: 2  row: 0x10e862200  session: 0x10f2fc050  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:07,076 - logic_logger - INFO
....DailyFlow[2026-11-19] {Prune Formula: request_pending [['request_received', 'request_processed', 'request_rejected']]} day: 2026-11-19, order_count: 48, order_amount: 14280.0000000000, message_received: 12, message_processed:  [5-->] 6, message_rejected: 5, message_pending:  [2-->] 1, request_received: 56, request_processed: 45, request_rejected: 9, request_pending: 2  row: 0x10e862200  session: 0x10f2fc050  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:07,076 - logic_logger - INFO
Logic Phase:		COMMIT LOGIC		(session=0x10f2fc050)   										 - 2026-11-19 19:46:07,076 - logic_logger - INFO
Logic Phase:		AFTER_FLUSH LOGIC	(session=0x10f2fc050)   										 - 2026-11-19 19:46:07,076 - logic_logger - INFO
..OrderB2bMessage[96] {AfterFlush Event} id: 96, CreatedOn: 2026-11-19 19:46:07.065839, CreatedOnDay: 2026-11-19, payload: {..., is_processed:  [False-->] True, error_text: None  row: 0x10f2e2e50  session: 0x10f2fc050  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:07,076 - logic_logger - INFO

```
</details>

&nbsp;
&nbsp;

#### Scenario: A message set back to not processed counts as not yet done ✅ (0.56 s)
&emsp;  Scenario: A message set back to not processed counts as not yet done  
&emsp;&emsp;    Given a new customer "Flow Msg Undo" with credit limit 5000  
&emsp;&emsp;    And an order message for "Flow Msg Undo" with 1 Widget and 2 Gadget is delivered to topic order_b2b  
&emsp;&emsp;    And today's totals are noted  
&emsp;&emsp;    When the message is set back to not processed  
&emsp;&emsp;    Then today's messages rose by 0 received, -1 processed, 0 rejected and 1 not yet done  

<details markdown>
<summary>Rules exercised and logic log (4 transactions)</summary>


&nbsp;
&nbsp;


**Rules Used** in Scenario: A message set back to not processed counts as not yet done
```
  DailyFlow  
    1. Derive DailyFlow.message_rejected as Count(OrderB2bMessage Where Rule.count(derive=models.DailyFlow.message_rejected, as_count_of=models.OrderB2bMessage, where=lambda row: row.error_text is not None, insert_parent=True), insert_parent)  
    2. Derive DailyFlow.message_received as Count(OrderB2bMessage Where  - None, insert_parent)  
    3. Derive DailyFlow.message_pending as Formula (1): Rule.formula(derive=models.DailyFlow.message_pend [...]  
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
**Logic Log** in Scenario: A message set back to not processed counts as not yet done (4 transactions)
```
Logic Phase:		ROW LOGIC		(session=0x10e4cecf0) (sqlalchemy before_flush)			 - 2026-11-19 19:46:07,615 - logic_logger - INFO
..OrderB2bMessage[None] {Insert - client} id: None, CreatedOn: None, CreatedOnDay: None, payload: {..., is_processed: False, error_text: None  row: 0x10e3a2ed0  session: 0x10e4cecf0  ins_upd_dlt: ins, initial: ins - 2026-11-19 19:46:07,616 - logic_logger - INFO
..OrderB2bMessage[None] {early_row_event_all_classes - handle_all did stamping} id: None, CreatedOn: 2026-11-19 19:46:07.616210, CreatedOnDay: 2026-11-19, payload: {..., is_processed: False, error_text: None  row: 0x10e3a2ed0  session: 0x10e4cecf0  ins_upd_dlt: ins, initial: ins - 2026-11-19 19:46:07,616 - logic_logger - INFO
....DailyFlow[2026-11-19] {Update - Adjusting daily_flow: message_received} day: 2026-11-19, order_count: 48, order_amount: 14280.00, message_received:  [12-->] 13, message_processed: 6, message_rejected: 5, message_pending: 1, request_received: 56, request_processed: 45, request_rejected: 9, request_pending: 2  row: 0x10e862410  session: 0x10e4cecf0  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:07,617 - logic_logger - INFO
....DailyFlow[2026-11-19] {Formula message_pending} day: 2026-11-19, order_count: 48, order_amount: 14280.00, message_received:  [12-->] 13, message_processed: 6, message_rejected: 5, message_pending:  [1-->] 2, request_received: 56, request_processed: 45, request_rejected: 9, request_pending: 2  row: 0x10e862410  session: 0x10e4cecf0  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:07,619 - logic_logger - INFO
....DailyFlow[2026-11-19] {Prune Formula: request_pending [['request_received', 'request_processed', 'request_rejected']]} day: 2026-11-19, order_count: 48, order_amount: 14280.00, message_received:  [12-->] 13, message_processed: 6, message_rejected: 5, message_pending:  [1-->] 2, request_received: 56, request_processed: 45, request_rejected: 9, request_pending: 2  row: 0x10e862410  session: 0x10e4cecf0  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:07,619 - logic_logger - INFO
Logic Phase:		COMMIT LOGIC		(session=0x10e4cecf0)   										 - 2026-11-19 19:46:07,620 - logic_logger - INFO
Logic Phase:		AFTER_FLUSH LOGIC	(session=0x10e4cecf0)   										 - 2026-11-19 19:46:07,622 - logic_logger - INFO
..OrderB2bMessage[97] {AfterFlush Event} id: 97, CreatedOn: 2026-11-19 19:46:07.616210, CreatedOnDay: 2026-11-19, payload: {..., is_processed: False, error_text: None  row: 0x10e3a2ed0  session: 0x10e4cecf0  ins_upd_dlt: ins, initial: ins - 2026-11-19 19:46:07,622 - logic_logger - INFO


Logic Phase:		ROW LOGIC		(session=0x10e4cf570) (sqlalchemy before_flush)			 - 2026-11-19 19:46:07,628 - logic_logger - INFO
..Order[None] {Insert - client} id: None, notes: behave kafka message, customer_id: 68, CreatedOn: None, date_shipped: None, amount_total: None, CreatedOnDay: None  row: 0x10f2d9c70  session: 0x10e4cf570  ins_upd_dlt: ins, initial: ins - 2026-11-19 19:46:07,628 - logic_logger - INFO
..Order[None] {early_row_event_all_classes - handle_all did stamping} id: None, notes: behave kafka message, customer_id: 68, CreatedOn: 2026-11-19, date_shipped: None, amount_total: None, CreatedOnDay: 2026-11-19  row: 0x10f2d9c70  session: 0x10e4cf570  ins_upd_dlt: ins, initial: ins - 2026-11-19 19:46:07,628 - logic_logger - INFO
..Order[None] {server aggregate_defaults: amount_total } id: None, notes: behave kafka message, customer_id: 68, CreatedOn: 2026-11-19, date_shipped: None, amount_total: 0, CreatedOnDay: 2026-11-19  row: 0x10f2d9c70  session: 0x10e4cf570  ins_upd_dlt: ins, initial: ins - 2026-11-19 19:46:07,628 - logic_logger - INFO
....DailyFlow[2026-11-19] {Update - Adjusting daily_flow: order_count} day: 2026-11-19, order_count:  [48-->] 49, order_amount: 14280.00, message_received: 13, message_processed: 6, message_rejected: 5, message_pending: 2, request_received: 56, request_processed: 45, request_rejected: 9, request_pending: 2  row: 0x10e8619c0  session: 0x10e4cf570  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:07,629 - logic_logger - INFO
....DailyFlow[2026-11-19] {Prune Formula: message_pending [['message_received', 'message_processed', 'message_rejected']]} day: 2026-11-19, order_count:  [48-->] 49, order_amount: 14280.00, message_received: 13, message_processed: 6, message_rejected: 5, message_pending: 2, request_received: 56, request_processed: 45, request_rejected: 9, request_pending: 2  row: 0x10e8619c0  session: 0x10e4cf570  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:07,629 - logic_logger - INFO
....DailyFlow[2026-11-19] {Prune Formula: request_pending [['request_received', 'request_processed', 'request_rejected']]} day: 2026-11-19, order_count:  [48-->] 49, order_amount: 14280.00, message_received: 13, message_processed: 6, message_rejected: 5, message_pending: 2, request_received: 56, request_processed: 45, request_rejected: 9, request_pending: 2  row: 0x10e8619c0  session: 0x10e4cf570  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:07,629 - logic_logger - INFO
..Item[None] {Insert - client} id: None, order_id: None, product_id: 2, quantity: 1, amount: None, unit_price: None  row: 0x10f2c96d0  session: 0x10e4cf570  ins_upd_dlt: ins, initial: ins - 2026-11-19 19:46:07,629 - logic_logger - INFO
..Item[None] {copy_rules for role: product - unit_price} id: None, order_id: None, product_id: 2, quantity: 1, amount: None, unit_price: 90.0000000000  row: 0x10f2c96d0  session: 0x10e4cf570  ins_upd_dlt: ins, initial: ins - 2026-11-19 19:46:07,629 - logic_logger - INFO
..Item[None] {Formula amount} id: None, order_id: None, product_id: 2, quantity: 1, amount: 90.0000000000, unit_price: 90.0000000000  row: 0x10f2c96d0  session: 0x10e4cf570  ins_upd_dlt: ins, initial: ins - 2026-11-19 19:46:07,630 - logic_logger - INFO
....Order[None] {Update - Adjusting order: amount_total} id: None, notes: behave kafka message, customer_id: 68, CreatedOn: 2026-11-19, date_shipped: None, amount_total:  [0-->] 90.0000000000, CreatedOnDay: 2026-11-19  row: 0x10f2d9c70  session: 0x10e4cf570  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:07,630 - logic_logger - INFO
......DailyFlow[2026-11-19] {Update - Adjusting daily_flow: order_amount} day: 2026-11-19, order_count: 49, order_amount:  [14280.00-->] 14370.0000000000, message_received: 13, message_processed: 6, message_rejected: 5, message_pending: 2, request_received: 56, request_processed: 45, request_rejected: 9, request_pending: 2  row: 0x10e8619c0  session: 0x10e4cf570  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:07,630 - logic_logger - INFO
......DailyFlow[2026-11-19] {Prune Formula: message_pending [['message_received', 'message_processed', 'message_rejected']]} day: 2026-11-19, order_count: 49, order_amount:  [14280.00-->] 14370.0000000000, message_received: 13, message_processed: 6, message_rejected: 5, message_pending: 2, request_received: 56, request_processed: 45, request_rejected: 9, request_pending: 2  row: 0x10e8619c0  session: 0x10e4cf570  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:07,630 - logic_logger - INFO
......DailyFlow[2026-11-19] {Prune Formula: request_pending [['request_received', 'request_processed', 'request_rejected']]} day: 2026-11-19, order_count: 49, order_amount:  [14280.00-->] 14370.0000000000, message_received: 13, message_processed: 6, message_rejected: 5, message_pending: 2, request_received: 56, request_processed: 45, request_rejected: 9, request_pending: 2  row: 0x10e8619c0  session: 0x10e4cf570  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:07,630 - logic_logger - INFO
......Customer[68] {Update - Adjusting customer: balance} id: 68, name: Flow Msg Undo 1795146367604, balance:  [0E-10-->] 90.0000000000, credit_limit: 5000.0000000000, email: None, email_opt_out: None  row: 0x10f30f250  session: 0x10e4cf570  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:07,630 - logic_logger - INFO
..Item[None] {Insert - client} id: None, order_id: None, product_id: 1, quantity: 2, amount: None, unit_price: None  row: 0x10f2c86d0  session: 0x10e4cf570  ins_upd_dlt: ins, initial: ins - 2026-11-19 19:46:07,630 - logic_logger - INFO
..Item[None] {copy_rules for role: product - unit_price} id: None, order_id: None, product_id: 1, quantity: 2, amount: None, unit_price: 150.0000000000  row: 0x10f2c86d0  session: 0x10e4cf570  ins_upd_dlt: ins, initial: ins - 2026-11-19 19:46:07,631 - logic_logger - INFO
..Item[None] {Formula amount} id: None, order_id: None, product_id: 1, quantity: 2, amount: 300.0000000000, unit_price: 150.0000000000  row: 0x10f2c86d0  session: 0x10e4cf570  ins_upd_dlt: ins, initial: ins - 2026-11-19 19:46:07,631 - logic_logger - INFO
....Order[None] {Update - Adjusting order: amount_total} id: None, notes: behave kafka message, customer_id: 68, CreatedOn: 2026-11-19, date_shipped: None, amount_total:  [90.0000000000-->] 390.0000000000, CreatedOnDay: 2026-11-19  row: 0x10f2d9c70  session: 0x10e4cf570  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:07,631 - logic_logger - INFO
......DailyFlow[2026-11-19] {Update - Adjusting daily_flow: order_amount} day: 2026-11-19, order_count: 49, order_amount:  [14370.0000000000-->] 14670.0000000000, message_received: 13, message_processed: 6, message_rejected: 5, message_pending: 2, request_received: 56, request_processed: 45, request_rejected: 9, request_pending: 2  row: 0x10e8619c0  session: 0x10e4cf570  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:07,631 - logic_logger - INFO
......DailyFlow[2026-11-19] {Prune Formula: message_pending [['message_received', 'message_processed', 'message_rejected']]} day: 2026-11-19, order_count: 49, order_amount:  [14370.0000000000-->] 14670.0000000000, message_received: 13, message_processed: 6, message_rejected: 5, message_pending: 2, request_received: 56, request_processed: 45, request_rejected: 9, request_pending: 2  row: 0x10e8619c0  session: 0x10e4cf570  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:07,631 - logic_logger - INFO
......DailyFlow[2026-11-19] {Prune Formula: request_pending [['request_received', 'request_processed', 'request_rejected']]} day: 2026-11-19, order_count: 49, order_amount:  [14370.0000000000-->] 14670.0000000000, message_received: 13, message_processed: 6, message_rejected: 5, message_pending: 2, request_received: 56, request_processed: 45, request_rejected: 9, request_pending: 2  row: 0x10e8619c0  session: 0x10e4cf570  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:07,631 - logic_logger - INFO
......Customer[68] {Update - Adjusting customer: balance} id: 68, name: Flow Msg Undo 1795146367604, balance:  [90.0000000000-->] 390.0000000000, credit_limit: 5000.0000000000, email: None, email_opt_out: None  row: 0x10f30f250  session: 0x10e4cf570  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:07,631 - logic_logger - INFO
Logic Phase:		COMMIT LOGIC		(session=0x10e4cf570)   										 - 2026-11-19 19:46:07,631 - logic_logger - INFO
Logic Phase:		AFTER_FLUSH LOGIC	(session=0x10e4cf570)   										 - 2026-11-19 19:46:07,632 - logic_logger - INFO
..Order[240] {AfterFlush Event} id: 240, notes: behave kafka message, customer_id: 68, CreatedOn: 2026-11-19, date_shipped: None, amount_total: 390.0000000000, CreatedOnDay: 2026-11-19  row: 0x10f2d9c70  session: 0x10e4cf570  ins_upd_dlt: ins, initial: ins - 2026-11-19 19:46:07,632 - logic_logger - INFO


Logic Phase:		ROW LOGIC		(session=0x10e4cf570) (sqlalchemy before_flush)			 - 2026-11-19 19:46:07,633 - logic_logger - INFO
..OrderB2bMessage[97] {Update - client} id: 97, CreatedOn: 2026-11-19 19:46:07.616210, CreatedOnDay: 2026-11-19, payload: {..., is_processed:  [False-->] True, error_text: None  row: 0x10f30e450  session: 0x10e4cf570  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:07,633 - logic_logger - INFO
....DailyFlow[2026-11-19] {Update - Adjusting daily_flow: message_processed} day: 2026-11-19, order_count: 49, order_amount: 14670.0000000000, message_received: 13, message_processed:  [6-->] 7, message_rejected: 5, message_pending: 2, request_received: 56, request_processed: 45, request_rejected: 9, request_pending: 2  row: 0x10e8619c0  session: 0x10e4cf570  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:07,633 - logic_logger - INFO
....DailyFlow[2026-11-19] {Formula message_pending} day: 2026-11-19, order_count: 49, order_amount: 14670.0000000000, message_received: 13, message_processed:  [6-->] 7, message_rejected: 5, message_pending:  [2-->] 1, request_received: 56, request_processed: 45, request_rejected: 9, request_pending: 2  row: 0x10e8619c0  session: 0x10e4cf570  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:07,633 - logic_logger - INFO
....DailyFlow[2026-11-19] {Prune Formula: request_pending [['request_received', 'request_processed', 'request_rejected']]} day: 2026-11-19, order_count: 49, order_amount: 14670.0000000000, message_received: 13, message_processed:  [6-->] 7, message_rejected: 5, message_pending:  [2-->] 1, request_received: 56, request_processed: 45, request_rejected: 9, request_pending: 2  row: 0x10e8619c0  session: 0x10e4cf570  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:07,633 - logic_logger - INFO
Logic Phase:		COMMIT LOGIC		(session=0x10e4cf570)   										 - 2026-11-19 19:46:07,633 - logic_logger - INFO
Logic Phase:		AFTER_FLUSH LOGIC	(session=0x10e4cf570)   										 - 2026-11-19 19:46:07,633 - logic_logger - INFO
..OrderB2bMessage[97] {AfterFlush Event} id: 97, CreatedOn: 2026-11-19 19:46:07.616210, CreatedOnDay: 2026-11-19, payload: {..., is_processed:  [False-->] True, error_text: None  row: 0x10f30e450  session: 0x10e4cf570  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:07,634 - logic_logger - INFO


Logic Phase:		ROW LOGIC		(session=0x10e4cd480) (sqlalchemy before_flush)			 - 2026-11-19 19:46:08,148 - logic_logger - INFO
..OrderB2bMessage[97] {Update - client} id: 97, CreatedOn: 2026-11-19 19:46:07.616210, CreatedOnDay: 2026-11-19, payload: {..., is_processed:  [True-->] False, error_text: None  row: 0x10f30db50  session: 0x10e4cd480  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:08,148 - logic_logger - INFO
....DailyFlow[2026-11-19] {Update - Adjusting daily_flow: message_processed} day: 2026-11-19, order_count: 49, order_amount: 14670.00, message_received: 13, message_processed:  [7-->] 6, message_rejected: 5, message_pending: 1, request_received: 56, request_processed: 45, request_rejected: 9, request_pending: 2  row: 0x10e8622b0  session: 0x10e4cd480  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:08,149 - logic_logger - INFO
....DailyFlow[2026-11-19] {Formula message_pending} day: 2026-11-19, order_count: 49, order_amount: 14670.00, message_received: 13, message_processed:  [7-->] 6, message_rejected: 5, message_pending:  [1-->] 2, request_received: 56, request_processed: 45, request_rejected: 9, request_pending: 2  row: 0x10e8622b0  session: 0x10e4cd480  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:08,149 - logic_logger - INFO
....DailyFlow[2026-11-19] {Prune Formula: request_pending [['request_received', 'request_processed', 'request_rejected']]} day: 2026-11-19, order_count: 49, order_amount: 14670.00, message_received: 13, message_processed:  [7-->] 6, message_rejected: 5, message_pending:  [1-->] 2, request_received: 56, request_processed: 45, request_rejected: 9, request_pending: 2  row: 0x10e8622b0  session: 0x10e4cd480  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:08,149 - logic_logger - INFO
Logic Phase:		COMMIT LOGIC		(session=0x10e4cd480)   										 - 2026-11-19 19:46:08,149 - logic_logger - INFO
Logic Phase:		AFTER_FLUSH LOGIC	(session=0x10e4cd480)   										 - 2026-11-19 19:46:08,150 - logic_logger - INFO
..OrderB2bMessage[97] {AfterFlush Event} id: 97, CreatedOn: 2026-11-19 19:46:07.616210, CreatedOnDay: 2026-11-19, payload: {..., is_processed:  [True-->] False, error_text: None  row: 0x10f30db50  session: 0x10e4cd480  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:08,150 - logic_logger - INFO

```
</details>

&nbsp;
&nbsp;

#### Scenario: A rejected message is counted (live Kafka only) ✅ (0.55 s)
&emsp;  Scenario: A rejected message is counted (live Kafka only)  
&emsp;&emsp;    Given a new customer "Flow Msg Bad" with credit limit 5000  
&emsp;&emsp;    And today's totals are noted  
&emsp;&emsp;    When an order message for "Flow Msg Bad" with 1 Sprocket is delivered live to topic order_b2b  
&emsp;&emsp;    Then today's messages rose by 1 received, 0 processed, 1 rejected and 0 not yet done  

<details markdown>
<summary>Rules exercised and logic log (2 transactions)</summary>


&nbsp;
&nbsp;


**Rules Used** in Scenario: A rejected message is counted (live Kafka only)
```
  DailyFlow  
    1. Derive DailyFlow.message_rejected as Count(OrderB2bMessage Where Rule.count(derive=models.DailyFlow.message_rejected, as_count_of=models.OrderB2bMessage, where=lambda row: row.error_text is not None, insert_parent=True), insert_parent)  
    2. Derive DailyFlow.message_received as Count(OrderB2bMessage Where  - None, insert_parent)  
    3. Derive DailyFlow.message_pending as Formula (1): Rule.formula(derive=models.DailyFlow.message_pend [...]  
    4. Derive DailyFlow.message_processed as Count(OrderB2bMessage Where Rule.count(derive=models.DailyFlow.message_processed, as_count_of=models.OrderB2bMessage, where=lambda row: row.is_processed == True, insert_parent=True), insert_parent)  
  OrderB2bMessage  
    5. RowEvent OrderB2bMessage._publish_order_b2b()  
```
**Logic Log** in Scenario: A rejected message is counted (live Kafka only) (2 transactions)
```
Logic Phase:		ROW LOGIC		(session=0x10e433df0) (sqlalchemy before_flush)			 - 2026-11-19 19:46:08,177 - logic_logger - INFO
..OrderB2bMessage[None] {Insert - client} id: None, CreatedOn: None, CreatedOnDay: None, payload: {..., is_processed: False, error_text: None  row: 0x10e3a2ed0  session: 0x10e433df0  ins_upd_dlt: ins, initial: ins - 2026-11-19 19:46:08,177 - logic_logger - INFO
..OrderB2bMessage[None] {early_row_event_all_classes - handle_all did stamping} id: None, CreatedOn: 2026-11-19 19:46:08.177713, CreatedOnDay: 2026-11-19, payload: {..., is_processed: False, error_text: None  row: 0x10e3a2ed0  session: 0x10e433df0  ins_upd_dlt: ins, initial: ins - 2026-11-19 19:46:08,177 - logic_logger - INFO
....DailyFlow[2026-11-19] {Update - Adjusting daily_flow: message_received} day: 2026-11-19, order_count: 49, order_amount: 14670.00, message_received:  [13-->] 14, message_processed: 6, message_rejected: 5, message_pending: 2, request_received: 56, request_processed: 45, request_rejected: 9, request_pending: 2  row: 0x10e235d30  session: 0x10e433df0  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:08,178 - logic_logger - INFO
....DailyFlow[2026-11-19] {Formula message_pending} day: 2026-11-19, order_count: 49, order_amount: 14670.00, message_received:  [13-->] 14, message_processed: 6, message_rejected: 5, message_pending:  [2-->] 3, request_received: 56, request_processed: 45, request_rejected: 9, request_pending: 2  row: 0x10e235d30  session: 0x10e433df0  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:08,178 - logic_logger - INFO
....DailyFlow[2026-11-19] {Prune Formula: request_pending [['request_received', 'request_processed', 'request_rejected']]} day: 2026-11-19, order_count: 49, order_amount: 14670.00, message_received:  [13-->] 14, message_processed: 6, message_rejected: 5, message_pending:  [2-->] 3, request_received: 56, request_processed: 45, request_rejected: 9, request_pending: 2  row: 0x10e235d30  session: 0x10e433df0  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:08,180 - logic_logger - INFO
Logic Phase:		COMMIT LOGIC		(session=0x10e433df0)   										 - 2026-11-19 19:46:08,180 - logic_logger - INFO
Logic Phase:		AFTER_FLUSH LOGIC	(session=0x10e433df0)   										 - 2026-11-19 19:46:08,181 - logic_logger - INFO
..OrderB2bMessage[98] {AfterFlush Event} id: 98, CreatedOn: 2026-11-19 19:46:08.177713, CreatedOnDay: 2026-11-19, payload: {..., is_processed: False, error_text: None  row: 0x10e3a2ed0  session: 0x10e433df0  ins_upd_dlt: ins, initial: ins - 2026-11-19 19:46:08,181 - logic_logger - INFO


Logic Phase:		ROW LOGIC		(session=0x10e4ce250) (sqlalchemy before_flush)			 - 2026-11-19 19:46:08,186 - logic_logger - INFO
..OrderB2bMessage[98] {Update - client} id: 98, CreatedOn: 2026-11-19 19:46:08.177713, CreatedOnDay: 2026-11-19, payload: {..., is_processed: False, error_text:  [None-->] resolve_lookups: no Product found for fk_col='product_id' from source fields  row: 0x10f2ca450  session: 0x10e4ce250  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:08,186 - logic_logger - INFO
....DailyFlow[2026-11-19] {Update - Adjusting daily_flow: message_rejected} day: 2026-11-19, order_count: 49, order_amount: 14670.00, message_received: 14, message_processed: 6, message_rejected:  [5-->] 6, message_pending: 3, request_received: 56, request_processed: 45, request_rejected: 9, request_pending: 2  row: 0x10e8620a0  session: 0x10e4ce250  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:08,187 - logic_logger - INFO
....DailyFlow[2026-11-19] {Formula message_pending} day: 2026-11-19, order_count: 49, order_amount: 14670.00, message_received: 14, message_processed: 6, message_rejected:  [5-->] 6, message_pending:  [3-->] 2, request_received: 56, request_processed: 45, request_rejected: 9, request_pending: 2  row: 0x10e8620a0  session: 0x10e4ce250  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:08,187 - logic_logger - INFO
....DailyFlow[2026-11-19] {Prune Formula: request_pending [['request_received', 'request_processed', 'request_rejected']]} day: 2026-11-19, order_count: 49, order_amount: 14670.00, message_received: 14, message_processed: 6, message_rejected:  [5-->] 6, message_pending:  [3-->] 2, request_received: 56, request_processed: 45, request_rejected: 9, request_pending: 2  row: 0x10e8620a0  session: 0x10e4ce250  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:08,187 - logic_logger - INFO
Logic Phase:		COMMIT LOGIC		(session=0x10e4ce250)   										 - 2026-11-19 19:46:08,187 - logic_logger - INFO
Logic Phase:		AFTER_FLUSH LOGIC	(session=0x10e4ce250)   										 - 2026-11-19 19:46:08,187 - logic_logger - INFO
..OrderB2bMessage[98] {AfterFlush Event} id: 98, CreatedOn: 2026-11-19 19:46:08.177713, CreatedOnDay: 2026-11-19, payload: {..., is_processed: False, error_text:  [None-->] resolve_lookups: no Product found for fk_col='product_id' from source fields  row: 0x10f2ca450  session: 0x10e4ce250  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:08,187 - logic_logger - INFO

```
</details>

&nbsp;
&nbsp;

#### Scenario: The chart shows the last 30 days with quiet days as zero ✅ (0.02 s)
&emsp;  Scenario: The chart shows the last 30 days with quiet days as zero  
&emsp;&emsp;    When the order volume chart is opened  
&emsp;&emsp;    Then the chart shows 31 days ending today  
&emsp;&emsp;    And every day with no totals shows zero  

_No rules fired in this scenario's logic log._

&nbsp;
&nbsp;

#### Scenario: The chart shows current data each time it is opened ✅ (0.03 s)
&emsp;  Scenario: The chart shows current data each time it is opened  
&emsp;&emsp;    Given a new customer "Flow Chart" with credit limit 5000  
&emsp;&emsp;    And the order volume chart is opened  
&emsp;&emsp;    When a B2B order is placed for "Flow Chart" with 1 Gadget  
&emsp;&emsp;    And the order volume chart is opened again  
&emsp;&emsp;    Then the chart's value for today rose by 1 and matches today's order count  

<details markdown>
<summary>Rules exercised and logic log (2 transactions)</summary>


&nbsp;
&nbsp;


**Rules Used** in Scenario: The chart shows current data each time it is opened
```
  DailyFlow  
    1. Derive DailyFlow.request_rejected as Count(OrderB2bRequest Where Rule.count(derive=models.DailyFlow.request_rejected, as_count_of=models.OrderB2bRequest, where=lambda row: row.error_text is not None, insert_parent=True), insert_parent)  
    2. Derive DailyFlow.request_pending as Formula (2): Rule.formula(derive=models.DailyFlow.request_pend [...]  
    3. Derive DailyFlow.request_processed as Count(OrderB2bRequest Where Rule.count(derive=models.DailyFlow.request_processed, as_count_of=models.OrderB2bRequest, where=lambda row: row.is_processed == True, insert_parent=True), insert_parent)  
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
**Logic Log** in Scenario: The chart shows current data each time it is opened (2 transactions)
```
Logic Phase:		ROW LOGIC		(session=0x10e4cecf0) (sqlalchemy before_flush)			 - 2026-11-19 19:46:08,739 - logic_logger - INFO
..OrderB2bRequest[None] {Insert - client} id: None, CreatedOn: None, CreatedOnDay: None, payload: {"Account": "Flow Chart 1795146368729", "Notes": "behave test", "Items": [{"Name": "Gadget", "QuantityOrdered": 1}]}, is_processed: False, error_text: None  row: 0x10f2e3b50  session: 0x10e4cecf0  ins_upd_dlt: ins, initial: ins - 2026-11-19 19:46:08,739 - logic_logger - INFO
..OrderB2bRequest[None] {early_row_event_all_classes - handle_all did stamping} id: None, CreatedOn: 2026-11-19 19:46:08.739843, CreatedOnDay: 2026-11-19, payload: {"Account": "Flow Chart 1795146368729", "Notes": "behave test", "Items": [{"Name": "Gadget", "QuantityOrdered": 1}]}, is_processed: False, error_text: None  row: 0x10f2e3b50  session: 0x10e4cecf0  ins_upd_dlt: ins, initial: ins - 2026-11-19 19:46:08,739 - logic_logger - INFO
....DailyFlow[2026-11-19] {Update - Adjusting daily_flow: request_received} day: 2026-11-19, order_count: 49, order_amount: 14670.00, message_received: 14, message_processed: 6, message_rejected: 6, message_pending: 2, request_received:  [56-->] 57, request_processed: 45, request_rejected: 9, request_pending: 2  row: 0x10e861910  session: 0x10e4cecf0  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:08,740 - logic_logger - INFO
....DailyFlow[2026-11-19] {Prune Formula: message_pending [['message_received', 'message_processed', 'message_rejected']]} day: 2026-11-19, order_count: 49, order_amount: 14670.00, message_received: 14, message_processed: 6, message_rejected: 6, message_pending: 2, request_received:  [56-->] 57, request_processed: 45, request_rejected: 9, request_pending: 2  row: 0x10e861910  session: 0x10e4cecf0  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:08,740 - logic_logger - INFO
....DailyFlow[2026-11-19] {Formula request_pending} day: 2026-11-19, order_count: 49, order_amount: 14670.00, message_received: 14, message_processed: 6, message_rejected: 6, message_pending: 2, request_received:  [56-->] 57, request_processed: 45, request_rejected: 9, request_pending:  [2-->] 3  row: 0x10e861910  session: 0x10e4cecf0  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:08,740 - logic_logger - INFO
Logic Phase:		COMMIT LOGIC		(session=0x10e4cecf0)   										 - 2026-11-19 19:46:08,740 - logic_logger - INFO
Logic Phase:		AFTER_FLUSH LOGIC	(session=0x10e4cecf0)   										 - 2026-11-19 19:46:08,741 - logic_logger - INFO


Logic Phase:		ROW LOGIC		(session=0x10e4cecf0) (sqlalchemy before_flush)			 - 2026-11-19 19:46:08,743 - logic_logger - INFO
..Product[1] {Update - client} id: 1, name: Gadget, count_suppliers: 0, unit_price: 150.0000000000  row: 0x10f2f7150  session: 0x10e4cecf0  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:08,743 - logic_logger - INFO
..OrderB2bRequest[163] {Update - client} id: 163, CreatedOn: 2026-11-19 19:46:08.739843, CreatedOnDay: 2026-11-19, payload: {"Account": "Flow Chart 1795146368729", "Notes": "behave test", "Items": [{"Name": "Gadget", "QuantityOrdered": 1}]}, is_processed:  [False-->] True, error_text: None  row: 0x10f2e3b50  session: 0x10e4cecf0  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:08,743 - logic_logger - INFO
....DailyFlow[2026-11-19] {Update - Adjusting daily_flow: request_processed} day: 2026-11-19, order_count: 49, order_amount: 14670.00, message_received: 14, message_processed: 6, message_rejected: 6, message_pending: 2, request_received: 57, request_processed:  [45-->] 46, request_rejected: 9, request_pending: 3  row: 0x10e861910  session: 0x10e4cecf0  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:08,744 - logic_logger - INFO
....DailyFlow[2026-11-19] {Prune Formula: message_pending [['message_received', 'message_processed', 'message_rejected']]} day: 2026-11-19, order_count: 49, order_amount: 14670.00, message_received: 14, message_processed: 6, message_rejected: 6, message_pending: 2, request_received: 57, request_processed:  [45-->] 46, request_rejected: 9, request_pending: 3  row: 0x10e861910  session: 0x10e4cecf0  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:08,744 - logic_logger - INFO
....DailyFlow[2026-11-19] {Formula request_pending} day: 2026-11-19, order_count: 49, order_amount: 14670.00, message_received: 14, message_processed: 6, message_rejected: 6, message_pending: 2, request_received: 57, request_processed:  [45-->] 46, request_rejected: 9, request_pending:  [3-->] 2  row: 0x10e861910  session: 0x10e4cecf0  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:08,744 - logic_logger - INFO
..Order[None] {Insert - client} id: None, notes: behave test, customer_id: 70, CreatedOn: None, date_shipped: None, amount_total: None, CreatedOnDay: None  row: 0x10f2db650  session: 0x10e4cecf0  ins_upd_dlt: ins, initial: ins - 2026-11-19 19:46:08,744 - logic_logger - INFO
..Order[None] {early_row_event_all_classes - handle_all did stamping} id: None, notes: behave test, customer_id: 70, CreatedOn: 2026-11-19, date_shipped: None, amount_total: None, CreatedOnDay: 2026-11-19  row: 0x10f2db650  session: 0x10e4cecf0  ins_upd_dlt: ins, initial: ins - 2026-11-19 19:46:08,744 - logic_logger - INFO
..Order[None] {server aggregate_defaults: amount_total } id: None, notes: behave test, customer_id: 70, CreatedOn: 2026-11-19, date_shipped: None, amount_total: 0, CreatedOnDay: 2026-11-19  row: 0x10f2db650  session: 0x10e4cecf0  ins_upd_dlt: ins, initial: ins - 2026-11-19 19:46:08,744 - logic_logger - INFO
....DailyFlow[2026-11-19] {Update - Adjusting daily_flow: order_count} day: 2026-11-19, order_count:  [49-->] 50, order_amount: 14670.00, message_received: 14, message_processed: 6, message_rejected: 6, message_pending: 2, request_received: 57, request_processed: 46, request_rejected: 9, request_pending: 2  row: 0x10e861910  session: 0x10e4cecf0  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:08,744 - logic_logger - INFO
....DailyFlow[2026-11-19] {Prune Formula: message_pending [['message_received', 'message_processed', 'message_rejected']]} day: 2026-11-19, order_count:  [49-->] 50, order_amount: 14670.00, message_received: 14, message_processed: 6, message_rejected: 6, message_pending: 2, request_received: 57, request_processed: 46, request_rejected: 9, request_pending: 2  row: 0x10e861910  session: 0x10e4cecf0  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:08,744 - logic_logger - INFO
....DailyFlow[2026-11-19] {Prune Formula: request_pending [['request_received', 'request_processed', 'request_rejected']]} day: 2026-11-19, order_count:  [49-->] 50, order_amount: 14670.00, message_received: 14, message_processed: 6, message_rejected: 6, message_pending: 2, request_received: 57, request_processed: 46, request_rejected: 9, request_pending: 2  row: 0x10e861910  session: 0x10e4cecf0  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:08,744 - logic_logger - INFO
..Item[None] {Insert - client} id: None, order_id: None, product_id: None, quantity: 1, amount: None, unit_price: None  row: 0x10f2e36d0  session: 0x10e4cecf0  ins_upd_dlt: ins, initial: ins - 2026-11-19 19:46:08,744 - logic_logger - INFO
..Item[None] {copy_rules for role: product - unit_price} id: None, order_id: None, product_id: None, quantity: 1, amount: None, unit_price: 150.0000000000  row: 0x10f2e36d0  session: 0x10e4cecf0  ins_upd_dlt: ins, initial: ins - 2026-11-19 19:46:08,745 - logic_logger - INFO
..Item[None] {Formula amount} id: None, order_id: None, product_id: None, quantity: 1, amount: 150.0000000000, unit_price: 150.0000000000  row: 0x10f2e36d0  session: 0x10e4cecf0  ins_upd_dlt: ins, initial: ins - 2026-11-19 19:46:08,745 - logic_logger - INFO
....Order[None] {Update - Adjusting order: amount_total} id: None, notes: behave test, customer_id: 70, CreatedOn: 2026-11-19, date_shipped: None, amount_total:  [0-->] 150.0000000000, CreatedOnDay: 2026-11-19  row: 0x10f2db650  session: 0x10e4cecf0  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:08,745 - logic_logger - INFO
......DailyFlow[2026-11-19] {Update - Adjusting daily_flow: order_amount} day: 2026-11-19, order_count: 50, order_amount:  [14670.00-->] 14820.0000000000, message_received: 14, message_processed: 6, message_rejected: 6, message_pending: 2, request_received: 57, request_processed: 46, request_rejected: 9, request_pending: 2  row: 0x10e861910  session: 0x10e4cecf0  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:08,745 - logic_logger - INFO
......DailyFlow[2026-11-19] {Prune Formula: message_pending [['message_received', 'message_processed', 'message_rejected']]} day: 2026-11-19, order_count: 50, order_amount:  [14670.00-->] 14820.0000000000, message_received: 14, message_processed: 6, message_rejected: 6, message_pending: 2, request_received: 57, request_processed: 46, request_rejected: 9, request_pending: 2  row: 0x10e861910  session: 0x10e4cecf0  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:08,745 - logic_logger - INFO
......DailyFlow[2026-11-19] {Prune Formula: request_pending [['request_received', 'request_processed', 'request_rejected']]} day: 2026-11-19, order_count: 50, order_amount:  [14670.00-->] 14820.0000000000, message_received: 14, message_processed: 6, message_rejected: 6, message_pending: 2, request_received: 57, request_processed: 46, request_rejected: 9, request_pending: 2  row: 0x10e861910  session: 0x10e4cecf0  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:08,745 - logic_logger - INFO
......Customer[70] {Update - Adjusting customer: balance} id: 70, name: Flow Chart 1795146368729, balance:  [0E-10-->] 150.0000000000, credit_limit: 5000.0000000000, email: None, email_opt_out: None  row: 0x10f2ca850  session: 0x10e4cecf0  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:08,745 - logic_logger - INFO
Logic Phase:		COMMIT LOGIC		(session=0x10e4cecf0)   										 - 2026-11-19 19:46:08,745 - logic_logger - INFO
Logic Phase:		AFTER_FLUSH LOGIC	(session=0x10e4cecf0)   										 - 2026-11-19 19:46:08,746 - logic_logger - INFO
..Order[241] {AfterFlush Event} id: 241, notes: behave test, customer_id: 70, CreatedOn: 2026-11-19, date_shipped: None, amount_total: 150.0000000000, CreatedOnDay: 2026-11-19  row: 0x10f2db650  session: 0x10e4cecf0  ins_upd_dlt: ins, initial: ins - 2026-11-19 19:46:08,746 - logic_logger - INFO

```
</details>

&nbsp;
&nbsp;

### Feature: Row-Level Security  

&nbsp;
&nbsp;

#### Scenario: Sales sees a customer with a credit limit of 3000 or more ✅ (0.04 s)
&emsp;  Scenario: Sales sees a customer with a credit limit of 3000 or more  
&emsp;&emsp;    Given a new customer "Sec High" with credit limit 5000  
&emsp;&emsp;    When a sales user queries the Customer list  
&emsp;&emsp;    Then the sales user sees "Sec High"  

_No rules fired in this scenario's logic log._

&nbsp;
&nbsp;

#### Scenario: Sales sees a low-limit customer who has a balance ✅ (0.02 s)
&emsp;  Scenario: Sales sees a low-limit customer who has a balance  
&emsp;&emsp;    Given a new customer "Sec Owing" with credit limit 1000  
&emsp;&emsp;    And a B2B order is placed for "Sec Owing" with 1 Widget  
&emsp;&emsp;    When a sales user queries the Customer list  
&emsp;&emsp;    Then the sales user sees "Sec Owing"  

<details markdown>
<summary>Rules exercised and logic log (2 transactions)</summary>


&nbsp;
&nbsp;


**Rules Used** in Scenario: Sales sees a low-limit customer who has a balance
```
  DailyFlow  
    1. Derive DailyFlow.request_rejected as Count(OrderB2bRequest Where Rule.count(derive=models.DailyFlow.request_rejected, as_count_of=models.OrderB2bRequest, where=lambda row: row.error_text is not None, insert_parent=True), insert_parent)  
    2. Derive DailyFlow.request_pending as Formula (2): Rule.formula(derive=models.DailyFlow.request_pend [...]  
    3. Derive DailyFlow.request_processed as Count(OrderB2bRequest Where Rule.count(derive=models.DailyFlow.request_processed, as_count_of=models.OrderB2bRequest, where=lambda row: row.is_processed == True, insert_parent=True), insert_parent)  
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
**Logic Log** in Scenario: Sales sees a low-limit customer who has a balance (2 transactions)
```
Logic Phase:		ROW LOGIC		(session=0x10e433df0) (sqlalchemy before_flush)			 - 2026-11-19 19:46:08,804 - logic_logger - INFO
..OrderB2bRequest[None] {Insert - client} id: None, CreatedOn: None, CreatedOnDay: None, payload: {"Account": "Sec Owing 1795146368799", "Notes": "behave test", "Items": [{"Name": "Widget", "QuantityOrdered": 1}]}, is_processed: False, error_text: None  row: 0x10e809850  session: 0x10e433df0  ins_upd_dlt: ins, initial: ins - 2026-11-19 19:46:08,804 - logic_logger - INFO
..OrderB2bRequest[None] {early_row_event_all_classes - handle_all did stamping} id: None, CreatedOn: 2026-11-19 19:46:08.804356, CreatedOnDay: 2026-11-19, payload: {"Account": "Sec Owing 1795146368799", "Notes": "behave test", "Items": [{"Name": "Widget", "QuantityOrdered": 1}]}, is_processed: False, error_text: None  row: 0x10e809850  session: 0x10e433df0  ins_upd_dlt: ins, initial: ins - 2026-11-19 19:46:08,804 - logic_logger - INFO
....DailyFlow[2026-11-19] {Update - Adjusting daily_flow: request_received} day: 2026-11-19, order_count: 50, order_amount: 14820.00, message_received: 14, message_processed: 6, message_rejected: 6, message_pending: 2, request_received:  [57-->] 58, request_processed: 46, request_rejected: 9, request_pending: 2  row: 0x10e861910  session: 0x10e433df0  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:08,804 - logic_logger - INFO
....DailyFlow[2026-11-19] {Prune Formula: message_pending [['message_received', 'message_processed', 'message_rejected']]} day: 2026-11-19, order_count: 50, order_amount: 14820.00, message_received: 14, message_processed: 6, message_rejected: 6, message_pending: 2, request_received:  [57-->] 58, request_processed: 46, request_rejected: 9, request_pending: 2  row: 0x10e861910  session: 0x10e433df0  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:08,804 - logic_logger - INFO
....DailyFlow[2026-11-19] {Formula request_pending} day: 2026-11-19, order_count: 50, order_amount: 14820.00, message_received: 14, message_processed: 6, message_rejected: 6, message_pending: 2, request_received:  [57-->] 58, request_processed: 46, request_rejected: 9, request_pending:  [2-->] 3  row: 0x10e861910  session: 0x10e433df0  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:08,804 - logic_logger - INFO
Logic Phase:		COMMIT LOGIC		(session=0x10e433df0)   										 - 2026-11-19 19:46:08,804 - logic_logger - INFO
Logic Phase:		AFTER_FLUSH LOGIC	(session=0x10e433df0)   										 - 2026-11-19 19:46:08,805 - logic_logger - INFO


Logic Phase:		ROW LOGIC		(session=0x10e433df0) (sqlalchemy before_flush)			 - 2026-11-19 19:46:08,807 - logic_logger - INFO
..Product[2] {Update - client} id: 2, name: Widget, count_suppliers: 0, unit_price: 90.0000000000  row: 0x10f2f6d60  session: 0x10e433df0  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:08,807 - logic_logger - INFO
..OrderB2bRequest[164] {Update - client} id: 164, CreatedOn: 2026-11-19 19:46:08.804356, CreatedOnDay: 2026-11-19, payload: {"Account": "Sec Owing 1795146368799", "Notes": "behave test", "Items": [{"Name": "Widget", "QuantityOrdered": 1}]}, is_processed:  [False-->] True, error_text: None  row: 0x10e809850  session: 0x10e433df0  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:08,807 - logic_logger - INFO
....DailyFlow[2026-11-19] {Update - Adjusting daily_flow: request_processed} day: 2026-11-19, order_count: 50, order_amount: 14820.00, message_received: 14, message_processed: 6, message_rejected: 6, message_pending: 2, request_received: 58, request_processed:  [46-->] 47, request_rejected: 9, request_pending: 3  row: 0x10e861910  session: 0x10e433df0  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:08,807 - logic_logger - INFO
....DailyFlow[2026-11-19] {Prune Formula: message_pending [['message_received', 'message_processed', 'message_rejected']]} day: 2026-11-19, order_count: 50, order_amount: 14820.00, message_received: 14, message_processed: 6, message_rejected: 6, message_pending: 2, request_received: 58, request_processed:  [46-->] 47, request_rejected: 9, request_pending: 3  row: 0x10e861910  session: 0x10e433df0  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:08,808 - logic_logger - INFO
....DailyFlow[2026-11-19] {Formula request_pending} day: 2026-11-19, order_count: 50, order_amount: 14820.00, message_received: 14, message_processed: 6, message_rejected: 6, message_pending: 2, request_received: 58, request_processed:  [46-->] 47, request_rejected: 9, request_pending:  [3-->] 2  row: 0x10e861910  session: 0x10e433df0  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:08,808 - logic_logger - INFO
..Order[None] {Insert - client} id: None, notes: behave test, customer_id: 72, CreatedOn: None, date_shipped: None, amount_total: None, CreatedOnDay: None  row: 0x10f2d9c70  session: 0x10e433df0  ins_upd_dlt: ins, initial: ins - 2026-11-19 19:46:08,808 - logic_logger - INFO
..Order[None] {early_row_event_all_classes - handle_all did stamping} id: None, notes: behave test, customer_id: 72, CreatedOn: 2026-11-19, date_shipped: None, amount_total: None, CreatedOnDay: 2026-11-19  row: 0x10f2d9c70  session: 0x10e433df0  ins_upd_dlt: ins, initial: ins - 2026-11-19 19:46:08,808 - logic_logger - INFO
..Order[None] {server aggregate_defaults: amount_total } id: None, notes: behave test, customer_id: 72, CreatedOn: 2026-11-19, date_shipped: None, amount_total: 0, CreatedOnDay: 2026-11-19  row: 0x10f2d9c70  session: 0x10e433df0  ins_upd_dlt: ins, initial: ins - 2026-11-19 19:46:08,808 - logic_logger - INFO
....DailyFlow[2026-11-19] {Update - Adjusting daily_flow: order_count} day: 2026-11-19, order_count:  [50-->] 51, order_amount: 14820.00, message_received: 14, message_processed: 6, message_rejected: 6, message_pending: 2, request_received: 58, request_processed: 47, request_rejected: 9, request_pending: 2  row: 0x10e861910  session: 0x10e433df0  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:08,808 - logic_logger - INFO
....DailyFlow[2026-11-19] {Prune Formula: message_pending [['message_received', 'message_processed', 'message_rejected']]} day: 2026-11-19, order_count:  [50-->] 51, order_amount: 14820.00, message_received: 14, message_processed: 6, message_rejected: 6, message_pending: 2, request_received: 58, request_processed: 47, request_rejected: 9, request_pending: 2  row: 0x10e861910  session: 0x10e433df0  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:08,808 - logic_logger - INFO
....DailyFlow[2026-11-19] {Prune Formula: request_pending [['request_received', 'request_processed', 'request_rejected']]} day: 2026-11-19, order_count:  [50-->] 51, order_amount: 14820.00, message_received: 14, message_processed: 6, message_rejected: 6, message_pending: 2, request_received: 58, request_processed: 47, request_rejected: 9, request_pending: 2  row: 0x10e861910  session: 0x10e433df0  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:08,808 - logic_logger - INFO
..Item[None] {Insert - client} id: None, order_id: None, product_id: None, quantity: 1, amount: None, unit_price: None  row: 0x10e808350  session: 0x10e433df0  ins_upd_dlt: ins, initial: ins - 2026-11-19 19:46:08,808 - logic_logger - INFO
..Item[None] {copy_rules for role: product - unit_price} id: None, order_id: None, product_id: None, quantity: 1, amount: None, unit_price: 90.0000000000  row: 0x10e808350  session: 0x10e433df0  ins_upd_dlt: ins, initial: ins - 2026-11-19 19:46:08,808 - logic_logger - INFO
..Item[None] {Formula amount} id: None, order_id: None, product_id: None, quantity: 1, amount: 90.0000000000, unit_price: 90.0000000000  row: 0x10e808350  session: 0x10e433df0  ins_upd_dlt: ins, initial: ins - 2026-11-19 19:46:08,808 - logic_logger - INFO
....Order[None] {Update - Adjusting order: amount_total} id: None, notes: behave test, customer_id: 72, CreatedOn: 2026-11-19, date_shipped: None, amount_total:  [0-->] 90.0000000000, CreatedOnDay: 2026-11-19  row: 0x10f2d9c70  session: 0x10e433df0  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:08,808 - logic_logger - INFO
......DailyFlow[2026-11-19] {Update - Adjusting daily_flow: order_amount} day: 2026-11-19, order_count: 51, order_amount:  [14820.00-->] 14910.0000000000, message_received: 14, message_processed: 6, message_rejected: 6, message_pending: 2, request_received: 58, request_processed: 47, request_rejected: 9, request_pending: 2  row: 0x10e861910  session: 0x10e433df0  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:08,808 - logic_logger - INFO
......DailyFlow[2026-11-19] {Prune Formula: message_pending [['message_received', 'message_processed', 'message_rejected']]} day: 2026-11-19, order_count: 51, order_amount:  [14820.00-->] 14910.0000000000, message_received: 14, message_processed: 6, message_rejected: 6, message_pending: 2, request_received: 58, request_processed: 47, request_rejected: 9, request_pending: 2  row: 0x10e861910  session: 0x10e433df0  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:08,808 - logic_logger - INFO
......DailyFlow[2026-11-19] {Prune Formula: request_pending [['request_received', 'request_processed', 'request_rejected']]} day: 2026-11-19, order_count: 51, order_amount:  [14820.00-->] 14910.0000000000, message_received: 14, message_processed: 6, message_rejected: 6, message_pending: 2, request_received: 58, request_processed: 47, request_rejected: 9, request_pending: 2  row: 0x10e861910  session: 0x10e433df0  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:08,809 - logic_logger - INFO
......Customer[72] {Update - Adjusting customer: balance} id: 72, name: Sec Owing 1795146368799, balance:  [0E-10-->] 90.0000000000, credit_limit: 1000.0000000000, email: None, email_opt_out: None  row: 0x10f30c3d0  session: 0x10e433df0  ins_upd_dlt: upd, initial: upd - 2026-11-19 19:46:08,809 - logic_logger - INFO
Logic Phase:		COMMIT LOGIC		(session=0x10e433df0)   										 - 2026-11-19 19:46:08,809 - logic_logger - INFO
Logic Phase:		AFTER_FLUSH LOGIC	(session=0x10e433df0)   										 - 2026-11-19 19:46:08,809 - logic_logger - INFO
..Order[242] {AfterFlush Event} id: 242, notes: behave test, customer_id: 72, CreatedOn: 2026-11-19, date_shipped: None, amount_total: 90.0000000000, CreatedOnDay: 2026-11-19  row: 0x10f2d9c70  session: 0x10e433df0  ins_upd_dlt: ins, initial: ins - 2026-11-19 19:46:08,809 - logic_logger - INFO

```
</details>

&nbsp;
&nbsp;

#### Scenario: Sales does not see a low-limit customer with no balance ✅ (0.01 s)
&emsp;  Scenario: Sales does not see a low-limit customer with no balance  
&emsp;&emsp;    Given a new customer "Sec Low" with credit limit 1000  
&emsp;&emsp;    When a sales user queries the Customer list  
&emsp;&emsp;    Then the sales user does not see "Sec Low"  
&emsp;&emsp;    And an admin user sees "Sec Low"  

_No rules fired in this scenario's logic log._
&nbsp;&nbsp;  
/Users/val/dev/genai-logic/ApiLogicServer-dev/build_and_test/genai-logic/demo_eai/test/api_logic_server_behave/behave_run.py completed at November 19, 2026 19:46:08  
Behave run time: 7.398 s  


&nbsp;
&nbsp;

## Provenance

| | |
|---|---|
| Generated | November 19, 2026 19:46 |
| Generator | `requirements_traceability_report.py` 2.15 |
| Report text from | reports/Requirements Traceability Report Template.md (sha256 a19673a13fa0) |
| Tests last ran | November 19, 2026 19:46 |
| Project | basic_demo_eai |
| Source commit | 32e99ea5 (uncommitted changes) |
| Project created | November 19, 2026 18:49:15 |
| Requirement files read | `docs/requirements/check_credit/requirements.md` (sha256 3ed113d5)<br>`docs/requirements/demo_eai/requirements.md` (sha256 5f955924)<br>`docs/requirements/order_b2b_consume/requirements.md` (sha256 8aa5249b)<br>`docs/requirements/order_flow_dashboard/requirements.md` (sha256 e5d1d5fa)<br>`docs/requirements/shipping_notification/requirements.md` (sha256 ebe2f99c) |
| Regenerate | `python requirements_traceability_report.py run`, from `test/api_logic_server_behave` |

_The report is derived from the project's files and the last test run; nothing in it is stored anywhere else, so regenerating it always reflects the project as it is now._

