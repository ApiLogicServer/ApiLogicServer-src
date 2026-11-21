---
title: Sample_Basic_EAI
do_process_code_block_titles: True
version: 1.17 from docsite, for readme, for readme 11/20/2026 - reorganized around the Architects Brief - Executable Requirements, Governed (see / read and trust / prove, business flow), Enterprise-class infrastructure; TL;DR states what it is, how it is created, what to learn; Kafka is one element of the infrastructure; Build It matches create_script.txt (Admin App, clean-up steps); B2B test curl logs in and uses the current endpoint; (1.16: 11/20/2026 - "Is the business flowing?" TL;DR; section 8 recast as rules, not a reporting stack; (1.15: 11/19/2026 - requirement 6, Operations Dashboard (order flow), and the seeded order history it charts; (1.14: for readme 10/24/2026 - one closing message (what to review, where the report is) instead of a mid-run "Built" line that runs did not print; (1.13: Build It is the adaptive clean script (sentences, no shell lines; degrades instead of stopping); (1.12: "This sample" instead of the project name (the same readme is fetched for demo_eai); (1.11: the no-container script is an opt-out of Docker/Podman, not only for machines without them; (1.10: 10/24/2026 - no-container script (Docker/Podman optional); (1.9: 10/20/2026 - no bootstrap prompt; Build It adds diagrams, tests, run tests, Behave Logic Report. (1.8: message_formats auto-included in prototype, xr))
source: docs/Sample-Basic-EAI
Propagation: see api_logic_server_cli/sample_mgr/create_readme.py
---
<style>
  -typeset h1,
  -content__button {
    display: none;
  }
</style>


&nbsp;
**Key Takeways - TL;DR - One System, Built From Requirements**
&nbsp;

    **What it is:** an order system. Partners send orders through a B2B API and a Kafka topic; rules enforce credit limits; shipping is notified by Kafka; the sales role sees only its customers; and the home page shows that orders are flowing.

    **How it's created:** you paste a short script into your AI assistant. It creates the project, implements six requirements (Gherkin), then writes and runs the tests and a traceability report. About 20 minutes, nothing written by hand.

    **What to learn from it** - the [Architects Brief](https://apilogicserver.github.io/Docs/Tech-Architects), shown in one system:

    1. **Executable Requirements:** the requirements build the system ([Section 1](#1-executable-requirements-how-it-gets-built)).
    2. **It runs:** a smoke test: an order through the API, a message through Kafka, and the dashboard ([Section 2](#2-it-runs-a-smoke-test)).
    3. **Governed:** what you can now govern ([Section 3](#3-governed-show-me)):
        * **Read and trust the rules:** Check Credit is five rules, not ~220 lines of code, and they govern every path (API, Kafka, Admin App), with no bypass.
        * **Prove it:** the traceability report shows each requirement, its rules, its tests, and the logic that ran.
        * **See the guesses:** `ad-libs.md` lists every judgment call the AI made.
    4. **Enterprise-class infrastructure:** a B2B API, Kafka subscribe and publish, and row-level security, from the same requirements ([Section 4](#4-enterprise-class-infrastructure-from-the-same-requirements)).
    5. **Due diligence:** build it yourself ([Section 5](#5-due-diligence-build-it-yourself)).

&nbsp;

![demo-eai](https://raw.githubusercontent.com/ApiLogicServer/Docs/main/docs/images/integration/demo-eai.png)

**This sample** is a single GenAI-Logic server providing APIs *and logic*: it both subscribes and publishes, so there's no second project to stand up.

&nbsp;

---

## 1. Executable Requirements: how it gets built

The requirements are the spec, and the spec builds the system. Six Gherkin features, readable by business and IT,
executed by your AI assistant:

![create_script](https://raw.githubusercontent.com/ApiLogicServer/Docs/main/docs/images/integration/demo_eai/create_script.png)

The requirements are shown at right above, truncated. **To see the entire file, [click here](https://github.com/ApiLogicServer/ApiLogicServer-src/blob/main/api_logic_server_cli/prototypes/manager/samples/requirements/demo_eai/docs/requirements/demo_eai/requirements.md).**
This example uses Gherkin `md` files; you can also use your existing methodologies.

| § | Requirement | Demonstrates |
|---|---|---|
| 1 | Check Credit | Rules, not code ([3a](#3a-rules-you-can-read-in-a-real-project)) |
| 2 | B2B API: accept orders from partners, and record each request with its outcome | Custom API ([4a](#4a-b2b-api-requirement-2)) |
| 3 | Kafka Subscribe: orders from the sales channel | Messaging, inbound ([4b](#4b-kafka-subscribe-requirement-3)) |
| 4 | Kafka Publish: notify shipping on dispatch | Messaging, outbound ([4c](#4c-kafka-publish-requirement-4)) |
| 5 | Row-Level Security | Security ([4d](#4d-security-requirement-5)) |
| 6 | Operations Dashboard: is the business flowing? | Rules, for the business ([3d](#3d-is-the-business-flowing-daily-totals-as-rules)) |

**One script executes them.** You paste a short script into your AI assistant: it creates the project and implements
all six requirements in one step, then writes and runs the tests and the report. About 20 minutes, nothing written by
hand. The next sections show it running, and what you get; [Section 5](#5-due-diligence-build-it-yourself) is the procedure.

&nbsp;

---

## 2. It runs: a smoke test

Output from a real run of the built system (Keycloak and a Kafka broker running), not instructions. To repeat it
yourself, see [Try it yourself](#try-it-yourself).

### 2a. The API: place an order, and the rules check credit

A partner order through the B2B API rolls up into the customer's balance; an order that would exceed the credit limit is rejected, and the balance is unchanged:

**B2B API: rollup and credit check:**
```text title="B2B API: rollup and credit check"
Alice before:   balance 1050, credit_limit 5000

POST /api/OrderB2B/OrderB2B   1 Widget, 2 Gadget
  → {"customer": "Alice", "items_count": 2, "message": "B2B Order created successfully", "order_id": 273}
Alice after:    balance 1440                     (+390: 1 × 90 + 2 × 150)

POST /api/OrderB2B/OrderB2B   50 Widget
  → HTTP 400  "Customer balance (5940) exceeds credit limit (5000)"
Alice after:    balance 1440                     (unchanged: the order was rolled back)
```

&nbsp;

### 2b. A message: an order arrives by Kafka

The debug service sends the sample order message through the broker; the
consumer saves it, parses it, and creates the order, with the same rules:

**Kafka: the sample order message, live:**
```text title="Kafka: the sample order message, live"
GET /consume_debug/order_b2b?file=docs/requirements/demo_eai/message_formats/order_b2b.json
  → {"mode": "live", "topic": "order_b2b", "published": true, "success": true, ...}

a few seconds later:
  OrderB2bMessage 106:  is_processed = true, error_text = none
  Order 274:            "Kafka order from sales", amount_total 390
```

Note the order of events: the message was **saved first** (message 106), then parsed in a **separate transaction**
into Order 274. Had parsing or the credit check failed, the message would still be there, with the reason. See
[4b](#4b-kafka-subscribe-requirement-3).

&nbsp;

### 2c. The dashboard: is the business flowing?

![order flow dashboard: daily totals maintained by rules](https://raw.githubusercontent.com/ApiLogicServer/Docs/main/docs/images/integration/demo_eai/bus_order_flow/Bus-governance.png)

The left chart is orders per day (count and amount). The right chart is, per day, the `order_b2b` Kafka messages and
the B2B API requests: processed, rejected, and not yet done. The seeded history shows what an operator looks for: a
**bad-data day** (messages keep arriving, but most are rejected) and the **flow stopping** (two days with no activity),
then recovery.

The totals behind it are **rules, not a reporting stack**: built by your AI assistant from requirement §6, and kept
current in the same transaction as every order and message. See [3d](#3d-is-the-business-flowing-daily-totals-as-rules).

&nbsp;

---

## 3. Governed: show me

The Brief claims you can read and trust what AI built, prove it implements what you asked, and see what it guessed.
Each is something you can open in the built project, and each ties back to the requirements above.

&nbsp;

### 3a. Rules you can read, in a real project

Logic (multi-table derivations and constraints) is a significant portion of a system, typically nearly half.

**Read:** the requirement on the left became the rules on the right: one rule per line of the
requirement, at the same level, so nothing gets lost in translation. Five rules, instead of about 220 lines of
procedural code ([the A/B test](https://github.com/ApiLogicServer/basic_demo/blob/main/logic/procedural/declarative-vs-procedural-comparison.md)).

![requirements become rules](https://raw.githubusercontent.com/ApiLogicServer/Docs/main/docs/images/integration/demo_eai/rules_code.png)

**A real project:** the explorer on the left of that picture is an ordinary Python project (Flask, SQLAlchemy,
your IDE, your debugger, your git). The rules are plain Python files. Nothing proprietary runs it, and containers are
optional: Kafka and Keycloak are used when they are running, and simulated or replaced (SQL security) when not.

**Trust:** these rules are declared once, on the data, not once per entry point. The rules engine hooks the database
commit itself, so Check Credit fires on *every* write path that touches an Order or Item: the Admin App, the standard
JSON:API, the `OrderB2B` custom API ([4a](#4a-b2b-api-requirement-2)), and the Kafka subscriber
([4b](#4b-kafka-subscribe-requirement-3)). Nothing downstream has to (or even can) ask for "enforce Check Credit here
too"; that is not a phrase you'll find in this project's requirements.

&nbsp;

### 3b. Prove it: tests and the traceability report

The build wrote Behave tests from the rules: one Feature per requirement, covering each change path the rules imply (for
a sum: insert, update, delete, and moving a row to another parent; for a constraint: accepted, at the boundary, and
rejected), ran them against the live API, and built the
[Requirements Traceability Report](https://github.com/ApiLogicServer/ApiLogicServer-src/blob/main/api_logic_server_cli/prototypes/manager/samples/basic_demo_eai/docs/requirements/Requirements%20Traceability%20Report.md)
from that run: for each requirement, the rules that implement it, the tests that exercise it, and the logs of those
rules firing.

That is the record you can hand a reviewer: each requirement, beside the rules and the evidence that they ran.

![traceability report: requirement, tests, rules](https://raw.githubusercontent.com/ApiLogicServer/Docs/main/docs/images/integration/demo_eai/reqmts_rules.png)

<details markdown>

<summary>What a scenario shows: the rules that ran, and the engine's log</summary>

<br>

For each scenario, the report shows the rules that ran and the engine's own log of them running:

![traceability report: a scenario, the rules used, and the logic log](https://raw.githubusercontent.com/ApiLogicServer/Docs/main/docs/images/integration/demo_eai/reqmts_rules_exec.png)

</details>

&nbsp;

### 3c. See the guesses: ad-libs

Requirements are never complete. The AI fills the gaps, and every judgment call it made goes into
[`docs/requirements/demo_eai/ad-libs.md`](https://github.com/ApiLogicServer/ApiLogicServer-src/blob/main/api_logic_server_cli/prototypes/manager/samples/basic_demo_eai/docs/requirements/demo_eai/ad-libs.md),
in two tiers:

* **🔴 Review required:** a decision you should confirm. For example, "unpaid order totals" was read as
  `date_shipped is None`: confirm it, or name the column that marks an order paid. Each item names the file and line,
  and the action to take.
* **🟡 FYI:** standard patterns applied, no action needed.

Where there is no safe default, the AI does not guess: it stops and leaves a `FIXME`.
The closing message of the build points you at this file. Read it first: it is the shortest path to what you might
disagree with.

&nbsp;

### 3d. Is the business flowing? Daily totals as rules

Requirement §6 asks: *is the business flowing?* Orders arriving, being processed, and not piling up as rejects. The
usual answer is a reporting stack: queries or a scheduled job feed a metrics store, and a dashboard reads it. This
sample answers with **more rules**, generated from the requirement below, not hand-coded. The daily totals are
derived like any other value, so the dashboard ([2c](#2c-the-dashboard-is-the-business-flowing)) only reads them.

**Why rules, not a reporting stack:**

| | Reporting stack (queries, jobs, metrics store) | Rules (this sample) |
|---|---|---|
| **When the totals change** | On a schedule, or by re-querying each time the page opens | In the transaction that changes the data |
| **Which writes are counted** | Whatever the query or job reads | Every write path: B2B API, Kafka, Admin App, and any path added later |
| **Cost per change** | Re-scans the rows | Adjusts the day's total by the change (one row, no scan) |
| **Can it drift?** | A copy can lag or diverge from the data | No: same engine and same commit as the customer balances |
| **What you write** | Queries, jobs, a pipeline to run them | Ten one-line rules |

The flow numbers get the same guarantee as the balances: an order that commits is counted, and one that rolls back is
not, on every path.

**Show them anywhere.** The Admin App charts are one consumer of the totals, not the product. `DailyFlow` is a
standard API resource (`/api/DailyFlow`), with the same security, filtering and sorting as every table. Grafana,
Power BI or a custom (Vibe) UI can show the same numbers, and an alert can watch them. *We maintain the numbers; show
them anywhere.*

<details markdown>

<summary>The requirement</summary>

<br>

![requirement §6](https://raw.githubusercontent.com/ApiLogicServer/Docs/main/docs/images/integration/demo_eai/bus_order_flow/order_flow_totals_reqs.png)

Requirement §2 adds one clause the dashboard depends on: *record each request, with its outcome*, so a rejected
B2B request leaves a row to count, not just an HTTP 400.

</details>

<details markdown>

<summary>The rules: daily totals, maintained by the engine (note use of insert_parent)</summary>

<br>

The `insert_parent` argument directs the engine to create parents on sum/count adjustment.

![daily totals rules](https://raw.githubusercontent.com/ApiLogicServer/Docs/main/docs/images/integration/demo_eai/bus_order_flow/order_flow_totals_rules.png)

The totals are not computed when the page opens; they are **rules**, kept current on every transaction, like any
other derived value:

* **One row per day** (`DailyFlow`), keyed by the day each Order, message and request arrived (`CreatedOnDay`, set by
  date stamping).
* **`insert_parent=True`**: the first arrival of a day creates that day's row; every later one adjusts it. Nothing
  pre-creates days.
* **Counts and sums** of each kind of arrival, with `where=` for processed and rejected; **not yet done** is a
  formula: received − processed − rejected.
* **Every write path counts**: the B2B API, the Kafka consumers and the Admin App all go through the same rules.
  A failed message or request records its reason (`error_text`) through the same governed session, so the rules
  count the rejection.

The page only reads `DailyFlow` (`api/api_discovery/dashboard_services.py`), fills a day with no row as zero (so the
chart can show the flow stopping), and renders on every request, not cached.

</details>

<details markdown>

<summary>The logic diagram</summary>

<br>

![daily totals logic diagram](https://raw.githubusercontent.com/ApiLogicServer/Docs/main/docs/images/integration/demo_eai/bus_order_flow/order_flow_totals_dgm.png)

From the Requirements Traceability Report: each arrow is a numbered rule, from the arriving rows (Order,
OrderB2bMessage, OrderB2bRequest) to the day's totals.

</details>

<details markdown>

<summary>The page: how the totals reach the screen</summary>

<br>

![dashboard implementation](https://raw.githubusercontent.com/ApiLogicServer/Docs/main/docs/images/integration/demo_eai/bus_order_flow/order_flow_totals_impl.png)

The rules are the easy part; getting the totals onto the home page takes five hops:

1. **`ui/admin/home.js`**: the Admin App home page is a fixed HTML string, so it holds one `<iframe>` pointing at `/dashboard`.
2. **`/dashboard`** returns one iframe per chart.
3. **`/chart_graphics/<name>`** calls that chart's function, listed in `CHARTS`.
4. **The chart function** (for example `order_volume_query()`) reads the `DailyFlow` rows, fills quiet days with zeros, and returns a plain dict.
5. **`ui/templates/multi_series_chart.jinja`** writes the dict into a page that draws it with Chart.js.

Hops 2-4 are in `api/api_discovery/dashboard_services.py`. To add a chart, add a function and a `CHARTS` entry;
`home.js` does not change. The project's `api/api_discovery/dashboard_services_readme.md` explains why each hop
exists, the dict the template expects, and what to add for production (a login).

</details>

For how to ask your AI assistant for queries and dashboards in your own project, see
[Admin Customization - AI Assistant](Admin-Customization#ai-assistant).

&nbsp;

---

## 4. Enterprise-class infrastructure, from the same requirements

The same `implement requirements` step built the integration: a custom API for partners, Kafka in both directions, and
row-level security. Each is governed by the rules above, with no extra requirement asking for it.

**Enterprise-class, not demo-class.** None of these practices is in the requirements; the context engineering applies
them to every integration it builds:

| | Best practice | Why it matters |
|---|---|---|
| **Kafka subscribe** | Save the raw message first (its own transaction), then parse it in a second | A bad message is never lost: it stays, with the reason (`error_text`), queryable and retryable |
| | Commit consumer offsets | A server restart does not read old messages again (no duplicate orders) |
| | A debug service per topic | Send a test message, live or simulated, and empty the queue: from a curl |
| **B2B API** | Record each request, with its outcome | A rejected request leaves a row: it is counted, and it can be investigated |
| **Kafka publish** | Map the message by example; unresolved fields stop the server from starting | A wrong message shape is found at startup, not by the consumer |
| **All of them** | Every order, from any source, goes through the same rules | Check Credit holds on every path; nothing to re-implement per integration |
| **Security** | Keycloak, or the SQL provider when no container runs | The same row-level grants, either way |

<details markdown>

<summary>New to message brokers? Kafka in brief</summary>

<br>

APIs are useful for application integration, but do not deal with the reality that the receiving system might be down.

Message Brokers like Kafka address this with guaranteed ***async delivery*** of messages. The Broker stores the message, delivering it (possibly later) when the receiver is up.

Message Brokers also support multi-cast: you ***publish*** a message to a "topic", and other systems ***subscribe***. This is often casually described as "pub/sub".

**No Kafka installed? No Docker?** Not required for any of this. The Kafka client library installs with the project either way; you only need an actual broker running to see live message delivery. Building, running, Check Credit, the Custom API, and the Kafka subscribe and publish logic itself all work, and are fully testable, without one. For live Kafka setup and verification, see [DevOps Quick Start](https://apilogicserver.github.io/Docs/DevOps-Quick-Start).

</details>

&nbsp;

### 4a. B2B API (requirement §2)

To fit our system into the Value Chain, requirement §2 asked for a **Custom API** to accept orders from B2B partners.
`implement requirements` built the endpoint from this Gherkin feature:

**Requirement §2 - B2B Order Integration:**
``` bash title="Requirement §2 - B2B Order Integration"
Feature: B2B Order Integration

  Scenario: Accept order from external partner
    Given an inbound B2B order in partner format (message_formats/order_b2b.json)
    When the order is received via a Custom API endpoint named OrderB2B
    Then map Account to Customer by name
    And map Items.Name to Product by name
    And map Items.QuantityOrdered to Item.quantity
    And record each request, with its outcome, for the order flow dashboard
```

Result: `POST /api/OrderB2B/OrderB2B` (see [Try it yourself](#try-it-yourself)). Each
request is recorded with its outcome, so a rejection is counted on the dashboard. Note there's no clause here about
enforcing Check Credit: see [3a](#3a-rules-you-can-read-in-a-real-project) for why not.

**Message formats, by example.** AI generates integrations **by example**: provide a sample message shape and it
auto-maps obvious field names silently, lists exceptions you specify, and blocks server start on anything
unresolvable. The formats are part of the requirements (`docs/requirements/demo_eai/message_formats/`) and double as
test fixtures:

- `order_b2b.json`: the inbound B2B order format (requirements §2 and §3)
- `order_shipping.json`: the outbound shipping notification format (requirement §4)

> See [Integration EAI](Integration-EAI#ai-based-creation) for how AI uses these.

> **Tip - mappings belong here too.** If you have complex or non-obvious field mappings, save them alongside the format file, in any structure that's clear to you and AI: a CSV, a plain-text table, extra comments in the JSON. AI will read whatever you reference in the prompt. Keeping mappings here (rather than embedded in the prompt) means they're versioned, reusable, and self-documenting.

**Lookups.** These mappings include **FK lookups**: `Account` isn't a column, it's a search key to find the right
`Customer` row. AI can't infer that from field names alone, so the requirement states it. For publish
([4c](#4c-kafka-publish-requirement-4)), the mappings are purely name-matching between the format file and
`models.py`, something AI can do itself.

&nbsp;

### 4b. Kafka Subscribe (requirement §3)

Requirement §3 asked for the same B2B order shape, arriving via Kafka instead of a direct API call:

**Requirement §3 - Kafka Subscribe Order Integration:**
```text title="Requirement §3 - Kafka Subscribe Order Integration"
Feature: Kafka Subscribe Order Integration

  Scenario: Accept inbound orders from sales channel
    Given an inbound order message in JSON format (message_formats/order_b2b.json)
    When the message is received from Kafka topic order_b2b
    Then map Account to Customer by name
    And map Items.Name to Product by name
    And map Items.QuantityOrdered to Item.quantity
```

> **Notice what this requirement does *not* say.** It doesn't mention the 2-message pattern, a blob table, error
> capture, or Check Credit: none of that is a decision left to whoever writes the requirement. The EAI-consume Context
> Engineering treats the 2-message pattern (raw payload saved first, parsed second) as mandatory for every Kafka
> subscriber it builds, and, just as mandatory, requires that a failed parse, lookup or constraint records *why* on the
> blob row (`error_text`), not only in a server log. Both are structural guarantees of how this platform builds Kafka
> subscribers, not something this requirement asked for.

The build also wrote a **debug service** for the topic, a curl that sends the sample message through the pipeline,
live or simulated: see [Try it yourself](#try-it-yourself), step 4.

<details markdown>

<summary>What got built: the 2-message pattern</summary>

<br>

A single-transaction consumer loses data if parsing fails mid-flush: the raw payload is gone. Instead:

```
topic: order_b2b
  → Consumer 1:  save raw JSON blob → OrderB2bMessage  (Tx 1 - always commits)
  → row_event:   blob insert → publish to order_b2b_processed
  → Consumer 2:  parse → Order + Items, resolve FKs, rules  (Tx 2)
```

Parse or business-rule failures leave `is_processed = False` on the blob row, queryable and retryable, **and** write
the failure reason to `error_text` on that same row, so you can tell *why* a message is stuck without
cross-referencing server logs: `SELECT id, error_text FROM order_b2b_message WHERE is_processed = 0`. The rules count
these rejections on the dashboard ([3d](#3d-is-the-business-flowing-daily-totals-as-rules)).

**Key Files**

See the module docstring in `integration/kafka/kafka_subscribe_discovery/order_b2b.py` for design details, field mapping, and test instructions. Supporting files:

| File | Role |
|------|------|
| `logic/logic_discovery/order_b2b_consume.py` | `row_event` bridge: publishes the blob to `order_b2b_processed` (no inline parse) |
| `integration/OrderB2bKafkaMapper.py` | JSON → Order + Items |
| `api/api_discovery/order_b2b_kafka_consume_debug.py` | The debug service: `/consume_debug/order_b2b` sends the sample, live or simulated; `/reset` empties the queue |
| `docs/requirements/demo_eai/message_formats/order_b2b.json` | Message format spec / test fixture |
| `integration/kafka/order_b2b_reset.sh` | Reset the Kafka topics between runs |

The AI chooses the file names during the build, so a build of your own may name these files differently; the
requirement and the module docstrings tie them together.

</details>

> **Live Kafka and restarts:** the consumer commits its offsets, so a restart does not read old messages again
> (`APILOGICPROJECT_KAFKA_COMMIT_OFFSETS`, on by default; see `config/default.env`). The create script empties the
> topics after the tests, so the test messages are not replayed into a later demo.

&nbsp;

### 4c. Kafka Publish (requirement §4)

A **key-only** publish rule sends just `{"id": 42}`: a notification that tells the consumer to call back for current
data. Requirement §4 asked for more: a **by-example** publish that carries the full shape the consumer needs, so it
never has to call back. `implement requirements` built this directly, with no separate "upgrade" step:

**Requirement §4 - Kafka Publish Shipping Notification:**
```text title="Requirement §4 - Kafka Publish Shipping Notification"
Feature: Kafka Publish Shipping Notification

  Scenario: Notify shipping when an order is dispatched
    Given an Order exists
    When date_shipped is set
    Then publish to Kafka topic order_shipping
    And use message_formats/order_shipping.json as the message shape
    And use by-example publish rather than key-only publish
```

AI reads the format file and `models.py` and maps by name. Direct matches are silent; uncertain ones get `# TODO: verify` in `FIELD_EXCEPTIONS`; anything unresolvable is added to `_unresolved` and **blocks server start**, reported to you in chat immediately.

For full details and generated code examples, see [Integration EAI - Publish](Integration-EAI#publish-outbound-messages).

&nbsp;

### 4d. Security (requirement §5)

Requirement §5 is a row-level security requirement, implemented the same way as any other:

**Requirement §5 - Row-Level Security:**
```text title="Requirement §5 - Row-Level Security"
Feature: Row-Level Security
  Scenario: Sales role sees limited customers
    Given a user with the sales role
    When querying the Customer list
    Then only return customers where credit_limit >= 3000 or balance > 0
```

Step B turned security on: Keycloak when a container runtime is running, else the SQL authentication provider. The
requirement became two grants on Customer for the `sales` role, in `security/declare_security.py`. The tests log in
as a sales user and check that only the matching customers come back, in either mode.

&nbsp;

---

&nbsp;

*Real code, rules you can read, tests that prove them, enterprise-class integration, and a report for the people who
approve it.* Convinced? [Section 5](#5-due-diligence-build-it-yourself) builds it.

&nbsp;

---

## 5. Due diligence: build it yourself

Everything above came from one script and six requirements. To check it on your machine, build it:

**Just want to run it, skip building?** The Manager already has a pre-built `basic_demo_eai`: jump straight to
[Run and Verify](#run-and-verify).

&nbsp;

### Build It

One sentence creates the project; one sentence executes **every** requirement (step C). Steps A-C are the
**entire build**, not the first of several. The steps after C bring the Admin App up to date, seed history for the
dashboard, and verify and document the system (Kafka check, diagrams, tests, report). Here is the whole procedure, then
what each step means:

> **Important:** be sure your AI assistant is in "Agent" mode ("Ask" will not work). No bootstrap prompt is needed: the Manager's context loads automatically when you open it in your AI assistant.

**The entire procedure: every line is a sentence to your AI assistant, none is a shell command:**
```text title="The entire procedure: every line is a sentence to your AI assistant, none is a shell command"
// 0 - Environment
Check for Docker or Podman. If neither is running, continue in degraded mode (SQL security, simulated Kafka) and tell me so up front.

// A - Create Project
create project demo_eai from samples/dbs/basic_demo.sqlite

// B - Security
add security (degrade to SQL if Keycloak is not available)

// C - Implement Requirements
implement requirements samples/requirements/demo_eai/docs/requirements/demo_eai

// C1 - Admin App
update the Admin App to show the new tables: replace ui/admin/admin.yaml with admin-merge.yaml (keep a backup), and show the message and request payloads as text areas

// C2 - Seed order history
seed order history for the dashboard: the 30 days before today, through the rules (not SQL), with weekday and weekend volumes (orders arriving as B2B requests and as Kafka messages), one day with mostly rejected messages, and no activity 3 and 2 days ago

// D - Verify Kafka
verify message subscriptions (all topics)

// E - Logic Diagrams
create logic diagram for each requirement (skip if graphviz is not available)

// F - Create Tests
create tests from rules, using default names

// G - Run Tests
run the tests

// H - Clean up
empty the Kafka topics, so a server restart does not read the test messages again (skip if no broker is running)

// I - Traceability Report
run the requirements traceability report
When the report is done, print this verbatim: "Next: scan these two files: logic/logic_discovery/check_credit.py (the rules) and docs/requirements/demo_eai/ad-libs (the judgment calls the AI made). Then open the report: demo_eai/docs/requirements/Requirements Traceability Report (in VS Code: open the file, then Cmd/Ctrl+Shift+V for the rendered preview)."
```

**Running it:** start your AI assistant (Claude Code, for example) in the Manager folder and paste the block, or paste [`create_script.txt`](https://github.com/ApiLogicServer/ApiLogicServer-src/blob/main/api_logic_server_cli/prototypes/manager/samples/requirements/demo_eai/create_script.txt), which is the same script, with [each step explained](https://github.com/ApiLogicServer/ApiLogicServer-src/blob/main/api_logic_server_cli/prototypes/manager/samples/requirements/demo_eai/create_script_annotated.txt). Lines starting with `//` are notes for you; the assistant ignores them. The first steps run from the Manager root; later ones (tests, report) use triggers that live in the created project's context (`demo_eai/.github/copilot-instructions.md`). If the assistant does not recognise one, open `demo_eai` as the workspace.

**Using Podman instead of Docker?** Nothing to change: the script uses `podman compose` when only Podman is running. One-time setup: see
[DevOps-Podman](https://apilogicserver.github.io/Docs/DevOps-Podman).

**No Docker or Podman?** The script notices, tells you up front, and carries on in degraded mode (it does not stop). To choose that mode even when a runtime is installed, paste [`create_script_no_container.txt`](https://github.com/ApiLogicServer/ApiLogicServer-src/blob/main/api_logic_server_cli/prototypes/manager/samples/requirements/demo_eai/create_script_no_container.txt) instead: the same script with a different first line. Degraded mode builds the same system from the same requirements, with two differences:

* **Security** uses the SQL authentication provider (no Keycloak), and Row-Level Security is still tested.
* **Kafka** runs in fallback mode (`KAFKA_SERVER` unset). Subscribe is tested through the debug endpoint,
  `/consume_debug/order_b2b`, which runs the same parse-and-save function the live consumer uses; the report labels
  those scenarios *simulated*. Live Kafka delivery is not verified in this mode. Start a broker and set `KAFKA_SERVER`
  and `KAFKA_CONSUMER_GROUP`, and the same endpoint publishes through the broker and the same tests run live.

<details markdown>

<summary>What the steps mean</summary>

<br>

| Step | What it does |
|---|---|
| **0 - Environment** | Your assistant checks for Docker or Podman. With neither running it says so up front and continues in degraded mode (SQL security, Kafka tested through the debug endpoint). |
| **A - Create Project** | Creates a working, MCP-enabled API and Admin App from the existing database (and the `genai-logic` CLI to manage it). No logic yet. |
| **B - Security** | Keycloak when a container runtime is running, else the SQL authentication provider that ships in the project, so the row-level security requirement (§5) is enforced either way. You are told which was used. |
| **C - Implement Requirements** | The build: the requirements (6 Gherkin features, plus the message formats) are copied into the project, and your AI assistant writes the rules, the Custom API, the Kafka subscribe and publish, the security declarations, and the dashboard. It also writes `ad-libs.md`, the judgment calls it made, for you to review (the closing message points you at it). Sections 2 and 3 below tour what it produced. |
| **C1 - Admin App** | The build added tables (the daily totals, the messages, the requests). The schema rebuild wrote them to `admin-merge.yaml` and left `admin.yaml` alone, since it may hold your edits; this project has none, so it is replaced. |
| **C2 - Seed Order History** | Gives the dashboard 30 days of history to chart ([3d](#3d-is-the-business-flowing-daily-totals-as-rules)). A script run inside the app writes the orders, messages and requests through the ORM with the rules active, so every amount, total and balance is derived and the credit limit checked. It does **not** go through the B2B API or Kafka: those are exercised by the tests (step F). Deterministic: a rebuild draws the same picture. |
| **D - Verify Kafka** | With a broker running: enables live Kafka, resets the topics first (messages left by earlier runs would otherwise be read again), sends the sample message, and confirms a processed blob and a new order. With no broker it verifies the simulated path and says so. |
| **E - Logic Diagrams** | Draws the rule chain for each requirement as an SVG; the report shows each one under its requirement. Skipped with a one-line note if graphviz is missing. |
| **F - Create Tests** | Writes Behave scenarios from the rules. "Default names" means each Feature is named exactly as its requirement, so the report can show, per requirement, which tests exercised it. |
| **G - Run Tests** | Starts the server if needed, runs the scenarios against the live API, records the logic log for each, and stops the server it started. |
| **H - Clean up** | Empties the Kafka topics, so a later restart of the demo does not read the test messages again. |
| **I - Traceability Report** | Writes the report, `demo_eai/docs/requirements/Requirements Traceability Report.md`. **Open it** (VS Code: open the file, then Cmd/Ctrl+Shift+V for the rendered preview): requirements traced to rules, tests and logic. |

* Steps D-I are each optional, and I works without the others (run it right after C for everything except test results).
* The *Row-Level Security* scenarios are exercised in both modes: step B turns security on with Keycloak or with the SQL provider.
* A scenario that reads a message back from the `order_shipping` topic needs a live broker; every other scenario runs with no Kafka.

</details>

This is a real project: your IDE, your Python, your source control. The prompt creates it in minutes, but you own it fully and iterate from there. Change a rule; the engine determines execution order automatically. Add an endpoint; the rules are already there waiting for it.

This suggests a different way to think about requirements gathering. Instead of Word documents that describe a system and then drift from it, requirements can be structured prompts: precise enough for AI to execute, readable enough for business and IT to agree on. The spec and the running system are the same artifact.

&nbsp;

### Run and Verify

1. **Start the Server:** F5 (or `python api_logic_server_run.py`)
2. **Start the Admin App:** browse to [http://localhost:5656/](http://localhost:5656/). The Admin App, with the dashboard at the top of its home page, should appear in your browser.
3. **Verify as shown below**

<details markdown>

<summary> Your project includes a data model diagram</summary>

<br>

![basic_demo_data_model](https://raw.githubusercontent.com/ApiLogicServer/Docs/main/docs/images/basic_demo/basic_demo_data_model.jpeg)

</details markdown>

&nbsp;

<details markdown>

<summary>API: filtering, sorting, pagination, optimistic locking, related data access... see Swagger </summary>

Your API is MCP enabled, and ready for custom app dev. For more information, [click here](https://apilogicserver.github.io/Docs/API-Self-Serve).

![swagger](https://raw.githubusercontent.com/ApiLogicServer/Docs/main/docs/images/basic_demo/api-swagger.jpeg)
</details>

<br>

<details markdown>

<summary>Admin App: multi-page, multi-table, automatic joins, lookups, cascade add - collaboration-ready</summary>

For more information, [click here](https://apilogicserver.github.io/Docs/Admin-Tour).

The Admin App is ready for **[business user agile collaboration](https://apilogicserver.github.io/Docs/Tech-AI/),** and back office data maintenance. This complements custom UIs created with the API.

Explore the app - click Customer Alice, and see their Orders, and Items.

![admin-app-initial](https://raw.githubusercontent.com/ApiLogicServer/Docs/main/docs/images/basic_demo/admin-app-initial.jpeg)
</details>

To exercise the main paths by hand, see [Try it yourself](#try-it-yourself).

&nbsp;

### Try it yourself

> **Kafka is optional during development.** The server doesn't require a broker to start or run, so you can build and
> test the full system with no infrastructure.
>
> * **Subscribe side:** exercised with no broker at all via the `consume_debug` endpoint (`APILOGICPROJECT_CONSUME_DEBUG=true`, on by default): the same code path as live Kafka, triggered by a curl instead of a topic message.
> * **Publish side:** if no broker is reachable at `localhost:9092`, the publish call still completes the underlying transaction: it buffers the message, waits up to ~10s for the broker, then logs a delivery failure. That PATCH will just feel a little slow.

**1. Start the server:** F5 (or `python api_logic_server_run.py`)

**2. Admin App:** browse to [http://localhost:5656/](http://localhost:5656/): click Customer Alice, see Orders and Items.

**3. Check Credit through the B2B API:**
**Check Credit - no Kafka needed:**
```bash title="Check Credit - no Kafka needed"
# Log in (security is on): user admin, password p
TOKEN=$(curl -s -X POST http://localhost:5656/api/auth/login -H 'Content-Type: application/json' \
  -d '{"username":"admin","password":"p"}' | python3 -c "import sys,json; print(json.load(sys.stdin)['access_token'])")

# Good order
curl -X POST http://localhost:5656/api/OrderB2B/OrderB2B \
  -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/vnd.api+json" \
  -d '{"meta":{"method":"OrderB2B","args":{"data":{"Account":"Alice","Notes":"test","Items":[{"Name":"Widget","QuantityOrdered":1}]}}}}'

# Over-limit order: expect 400, "Customer balance (...) exceeds credit limit (...)"
curl -X POST http://localhost:5656/api/OrderB2B/OrderB2B \
  -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/vnd.api+json" \
  -d '{"meta":{"method":"OrderB2B","args":{"data":{"Account":"Alice","Notes":"over limit","Items":[{"Name":"Widget","QuantityOrdered":50}]}}}}'
```

The table endpoints (`/api/Customer` and the others) require the token. Custom APIs such as `OrderB2B` do not, by
default, to keep development and demos simple: for production, require a login on them too.

**4. Kafka Subscribe, with the built-in debug service:**

> **Built for developers: a debug service for every pipeline.** For each Kafka topic it subscribes to, the build also
> writes a small debug service (`api/api_discovery/order_b2b_kafka_consume_debug.py`): a curl that sends the sample
> message through the whole pipeline (parse, lookups, rules, rows). It runs **live** through Kafka when a broker
> answers, and **simulated** (the consumer's own parse-and-save function, no broker) when not, and the reply says which
> ran. Another curl empties the queue, so a test starts clean. They are how you check the system is alive in seconds,
> and the generated tests use them too. Development only: no login, and `APILOGICPROJECT_CONSUME_DEBUG = false` in
> `config/default.env` turns them off.

**Kafka Subscribe - with or without a broker:**
```bash title="Kafka Subscribe - with or without a broker"
# Send the sample order message (live if a broker answers, else simulated; the reply says which)
curl "http://localhost:5656/consume_debug/order_b2b?file=docs/requirements/demo_eai/message_formats/order_b2b.json"

# Or force a mode (live answers 409 if Kafka is not available)
curl "http://localhost:5656/consume_debug/order_b2b?file=docs/requirements/demo_eai/message_formats/order_b2b.json&mode=simulated"

# Empty the queue (topics order_b2b and order_b2b_processed)
curl -X POST "http://localhost:5656/consume_debug/order_b2b/reset"
```
Verify: `sqlite3 database/db.sqlite "SELECT * FROM 'order' ORDER BY id DESC LIMIT 1; SELECT * FROM item ORDER BY id DESC LIMIT 3;"`

**5. Kafka Publish:** PATCH an order's `date_shipped` (e.g. via the Admin App, or the API) and watch the log:
`publish_kafka_message: delivered to topic 'order_shipping'` if a broker is up, or a delivery-failure log after ~10s if
not (expected either way).

**6. (Optional) Live Kafka, end-to-end:**

  1. Start Kafka. If the `broker1` container already exists (`podman ps -a`, from the Manager README's *Containers* section), just make sure it is running and skip the compose file: it would fail on the name. Otherwise: `docker compose -f integration/kafka/dockercompose_start_kafka.yml up -d`
     (Podman instead of Docker? Use `podman compose`, same file, unchanged. See [DevOps-Podman](https://apilogicserver.github.io/Docs/DevOps-Podman).)
  2. Set `KAFKA_SERVER` and `KAFKA_CONSUMER_GROUP` in `config/default.env` (step D of the build does this when a broker is running), and restart the server.
  3. Empty the queue, then send the sample message live, with the step 4 curls: the reset, then `&mode=live`.
     Live is asynchronous: the reply is the broker's acknowledgement, and the new order appears a few seconds later
     (same verification query as step 4).

&nbsp;

---

## Notes

**Where the dashboard history comes from: step C2, and what it is not.** A new project has only today's test data, so
the charts would be one spike at the right edge. Step C2 seeds the 30 days before today
(`database/test_data/seed_order_flow.py`). The seed writes through the ORM inside the app with the rules active:
every item price and amount, order total, customer balance and daily total is derived by the rules, and the credit
limit is checked. It is **not** delivered through the B2B API or Kafka: the seeded messages and requests are written
already processed (or rejected, with an error text the seed supplies). The tests (step F) exercise the real API and the
real topic. The seed is deterministic (fixed random seed, dates relative to today) and refuses to run twice.

**Retention:** order, message and request rows are never purged. The totals count them, so deleting rows would lower
past days' totals. The logic file carries a TODO with the options.

**Iterating:** this is a real project. To change a requirement, edit it in `docs/requirements/demo_eai/requirements.md`
and say *implement reqs demo_eai* again: the AI changes only the rules that the edit affects. See
[Executable Requirements](Exec-Reqmts#requirements-iteration).
