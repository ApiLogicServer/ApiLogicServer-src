---
title: Sample_Basic_EAI
do_process_code_block_titles: True
version: 1.14 from docsite, for readme, for readme 10/24/2026 - one closing message (what to review, where the report is) instead of a mid-run "Built" line that runs did not print; (1.13: Build It is the adaptive clean script (sentences, no shell lines; degrades instead of stopping); (1.12: "This sample" instead of the project name (the same readme is fetched for demo_eai); (1.11: the no-container script is an opt-out of Docker/Podman, not only for machines without them; (1.10: 10/24/2026 - no-container script (Docker/Podman optional); (1.9: 10/20/2026 - no bootstrap prompt; Build It adds diagrams, tests, run tests, Behave Logic Report. (1.8: message_formats auto-included in prototype, xr))
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
**Key Takeways - TL;DR - Kafka Integration: Async Messaging**
&nbsp;

    APIs are useful to application integration, but do not deal with the reality that the receiving system might be down.

    Message Brokers like Kafka address this with guaranteed ***async delivery*** of messages.  The Broker stores the message, delivering it (possibly later) when the the receiver is up.

    Message Brokers also support multi-cast: you ***publish*** a message to a "topic", and other systems ***subscribe***.  This is often casually described as "pub/sub".

    This sample presumes you are familiar with basic GenAI-Logic services, as illustrated in the Basic Demo tutorial.

    **The flow this page walks through:** *Executable Requirements* (the spec is a prompt your AI executes, so the requirements build the system) → *tests* (AI writes Behave tests from the rules, and runs them) → *documentation* (a Requirements Traceability Report traces each requirement to its rules, tests and the logic that actually ran). Requirements, system, tests and docs stay connected, and each step is one sentence to your AI assistant — see [Build It](#build-it).

    > This is the same system used in [Executable Requirements](https://apilogicserver.github.io/Docs/Exec-Reqmts), which focuses on how these prompts serve as the living spec — readable by business and IT, executable by AI.

&nbsp;

## Overview

This app illustrates using IntegrationServices for B2B push-style integrations with APIs, and internal integration with messages.

&nbsp;

![demo-eai](https://raw.githubusercontent.com/ApiLogicServer/Docs/main/docs/images/integration/demo-eai.png)

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

&nbsp;

## Setup

**No Kafka installed? No Docker?** Not required for any of this. The Kafka client
library installs with the project either way; you only need an actual broker
running if you want to see live message delivery (Section 6, Step 6 — optional).
Everything else — building, running, Check Credit, the Custom API, and even the
Kafka Subscribe/Publish logic itself — works and is fully testable without one.
If/when you do want live Kafka, the project includes everything to stand one up —
see `integration/kafka/kafka_readme.md`'s **Live Kafka Test** section
(`docker compose -f integration/kafka/dockercompose_start_kafka.yml up -d`, Podman
alternative included).

&nbsp;

**Just want to run it, skip building?** The Manager already has a pre-built
`basic_demo_eai` — jump straight to [Section 1, Run and Verify](#1-run-and-verify).
Everyone — whether you just built it or you're using the pre-built copy — starts
there.

&nbsp;

## Build It

One sentence creates the project; one sentence executes **every** requirement below
(Check Credit, B2B API, Kafka Subscribe, Kafka Publish, Security) — steps A-C are the
**entire build**, not the first of several. Steps D-H (Kafka check, diagrams, tests, report) are
optional extras that verify and document it. Here is the whole procedure, then what each step means:

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

// D - Verify Kafka
verify message subscriptions (all topics)

// E - Logic Diagrams
create logic diagram for each requirement (skip if graphviz is not available)

// F - Create Tests
create tests from rules, using default names

// G - Run Tests
run the tests

// H - Traceability Report
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


&nbsp;

### What the steps mean

| Step | What it does |
|---|---|
| **0 - Environment** | Your assistant checks for Docker or Podman. With neither running it says so up front and continues in degraded mode (SQL security, Kafka tested through the debug endpoint). |
| **A - Create Project** | Creates a working, MCP-enabled API and Admin App from the existing database (and the `genai-logic` CLI to manage it). No logic yet. |
| **B - Security** | Keycloak when a container runtime is running, else the SQL authentication provider that ships in the project, so the row-level security requirement (§5) is enforced either way. You are told which was used. |
| **C - Implement Requirements** | The build: the requirements (5 Gherkin features, plus the message formats) are copied into the project, and your AI assistant writes the rules, the Custom API, the Kafka subscribe and publish, and the security declarations. It also writes `ad-libs.md`, the judgment calls it made, for you to review (the closing message points you at it). Sections 2-5b and 7 below tour what it produced. |
| **D - Verify Kafka** | With a broker running: enables live Kafka, resets the topics first (messages left by earlier runs would otherwise be replayed), sends the sample message, and confirms a processed blob and a new order. With no broker it verifies the simulated path and says so. |
| **E - Logic Diagrams** | Draws the rule chain for each requirement as an SVG; the report shows each one under its requirement. Skipped with a one-line note if graphviz is missing. |
| **F - Create Tests** | Writes Behave scenarios from the rules. "Default names" means each Feature is named exactly as its requirement, so the report can show, per requirement, which tests exercised it. |
| **G - Run Tests** | Starts the server if needed, runs the scenarios against the live API, records the logic log for each, and stops the server it started. |
| **H - Traceability Report** | Writes the report, `demo_eai/docs/requirements/Requirements Traceability Report.md`. **Open it** (VS Code: open the file, then Cmd/Ctrl+Shift+V for the rendered preview): requirements traced to rules, tests and logic. |

* Steps D-H are each optional, and H works without the others (run it right after C for everything except test results).
* The *Row-Level Security* scenarios are exercised in both modes: step B turns security on with Keycloak or with the SQL provider.
* A scenario that reads a message back from the `order_shipping` topic needs a live broker (Section 6, Step 6); every other scenario runs with no Kafka.
* The full requirements spec that step C executes is
  [docs/requirements/demo_eai/requirements.md](https://github.com/ApiLogicServer/ApiLogicServer-src/blob/main/api_logic_server_cli/prototypes/manager/samples/requirements/demo_eai/docs/requirements/demo_eai/requirements.md).
  **Sections 2-5b and 7 below are a tour of what step C built** — each maps back to the requirement that produced it. They are not additional steps to run.

This is a real project: your IDE, your Python, your source control. The prompt creates it in minutes — but you own it fully and iterate from there. Change a rule; the engine determines execution order automatically. Add an endpoint; the rules are already there waiting for it.

This suggests a different way to think about requirements gathering. Instead of Word documents that describe a system and then drift from it, requirements can be structured prompts — precise enough for AI to execute, readable enough for business and IT to agree on. The spec and the running system are the same artifact.

&nbsp;

## 1. Run and Verify

1. **Start the Server:** F5 (or `python api_logic_server_run.py`)
2. **Start the Admin App:** browse to [http://localhost:5656/](http://localhost:5656/).  The Admin App screen shown below should appear in your Browser.
3. **Verify as shown below**

<details markdown>

<summary> Your project includes a data model diagram</summary>

<br>

![basic_demo_data_model](https://raw.githubusercontent.com/ApiLogicServer/Docs/main/docs/images/basic_demo/basic_demo_data_model.jpeg)

</details markdown>

&nbsp;

<details markdown>

<summary>API: filtering, sorting, pagination, optimistic locking,related data access... see Swagger </summary>

Your API is MCP enabled, and ready for custom app dev.  For more information, [click here](https://apilogicserver.github.io/Docs/API-Self-Serve).

![swagger](https://raw.githubusercontent.com/ApiLogicServer/Docs/main/docs/images/basic_demo/api-swagger.jpeg)
</details>

<br>

<details markdown>

<summary>Admin App: multi-page, multi-table, automatic joins, lookups, cascade add - collaboration-ready</summary>

For more information, [click here](https://apilogicserver.github.io/Docs/Admin-Tour).

The Admin App is ready for **[business user agile collaboration](https://apilogicserver.github.io/Docs/Tech-AI/),** and back office data maintenance.  This complements custom UIs created with the API.

Explore the app - click Customer Alice, and see their Orders, and Items.  

![admin-app-initial](https://raw.githubusercontent.com/ApiLogicServer/Docs/main/docs/images/basic_demo/admin-app-initial.jpeg)
</details>

Now go to [Section 6, How to Test](#6-how-to-test) to exercise the EAI features
(Check Credit, Kafka Subscribe, Kafka Publish) — or continue reading below for a
tour of how each requirement became the running system you just verified.

<br>

## 2. Requirement §1 — Check Credit Logic

Logic (multi-table derivations and constraints) is a significant portion of a system, typically nearly half.  GenAI-Logic provides **spreadsheet-like rules** that dramatically simplify and accelerate logic development.

`implement requirements` turned this Gherkin feature (requirements §1) into the 5 rules below — no procedural code to write or maintain:

**Check Credit Logic (instead of 220 lines of code):**
```bash title="Check Credit Logic (instead of 220 lines of code)"
On Placing Orders, Check Credit    
    1. The Customer's balance is less than the credit limit
    2. The Customer's balance is the sum of the Order amount_total where date_shipped is null
    3. The Order's amount_total is the sum of the Item amount
    4. The Item amount is the quantity * unit_price
    5. The Item unit_price is copied from the Product unit_price

Use case: App Integration
    1. Send the Order to Kafka topic 'order_shipping' if the date_shipped is not None.
```

![Nat Lang Logic](https://raw.githubusercontent.com/ApiLogicServer/Docs/main/docs/images/sample-ai/copilot/copilot-logic-vibe.png)

> **These rules are declared once, on the data — not once per entry point.** LogicBank hooks
> the database commit itself, so Check Credit fires on *every* write path that touches an
> Order or Item: the Admin App, the standard JSON:API, the `OrderB2B` custom API (Section 4),
> and the Kafka subscriber (Section 5) — all four call the same rules, automatically. Nothing
> downstream has to (or even can) re-request "enforce Check Credit here too" — that's not a
> phrase you'll find in this project's requirements.

<br>

## 3. Message Formats — Already Included

AI generates integrations **by example** — provide a sample message shape and it auto-maps obvious field names silently, lists exceptions you specify, and blocks server start on anything unresolvable.  They double as test fixtures.

`implement requirements` already produced these in `integration/kafka/message_formats/`
(referenced by requirements §2-4):

- `order_b2b.json` — inbound B2B order format
- `order_shipping.json` — outbound shipping notification format

> See [Integration EAI](Integration-EAI#ai-based-creation) for how AI uses these.

> **Tip — mappings belong here too.**  If you have complex or non-obvious field mappings, save them alongside the format file — in any structure that's clear to you and AI: a CSV, a plain-text table, extra comments in the JSON.  AI will read whatever you reference in the prompt.  Keeping mappings here (rather than embedded in the prompt) means they're versioned, reusable, and self-documenting.

&nbsp;

<br>

## 4. Requirement §2 — Custom API for B2B Orders

To fit our system into the Value Chain, requirements §2 asked for a **Custom API**
to accept orders from B2B partners. `implement requirements` built the endpoint below
from this Gherkin feature:

**Requirement §2 — B2B Order Integration:**
``` bash title="Requirement §2 — B2B Order Integration"
Feature: B2B Order Integration

  Scenario: Accept order from external partner
    Given an inbound B2B order in partner format (message_formats/order_b2b.json)
    When the order is received via a Custom API endpoint named OrderB2B
    Then map Account to Customer by name
    And map Items.Name to Product by name
    And map Items.QuantityOrdered to Item.quantity
```

Result: `POST /api/OrderB2B` — see Section 6 to test it. Note there's no clause here
about enforcing Check Credit — see Section 2's callout for why not.

<br>

## 5. Requirement §3 — EAI Subscribe (Inbound Kafka Message)

requirements §3 asked for the same B2B order shape, but arriving via Kafka instead
of a direct API call — reusing the message format from Section 3:

**Requirement §3 — Kafka Subscribe Order Integration:**
```text title="Requirement §3 — Kafka Subscribe Order Integration"
Feature: Kafka Subscribe Order Integration

  Scenario: Accept inbound orders from sales channel
    Given an inbound order message in JSON format (message_formats/order_b2b.json)
    When the message is received from Kafka topic order_b2b
    Then map Account to Customer by name
    And map Items.Name to Product by name
    And map Items.QuantityOrdered to Item.quantity
```

> **Notice what this requirement does *not* say.** It doesn't mention the 2-message
> pattern, a blob table, error capture, or Check Credit — none of that is a decision
> left to whoever writes the requirement. The EAI-consume Context Engineering treats
> the 2-message pattern (raw payload saved first, parsed second) as mandatory for
> every Kafka subscriber it builds — "single-transaction consumers cause data loss"
> — and, just as mandatory, requires that a failed parse/lookup/constraint records
> *why* on the blob row (`error_text`), not only in a server log. Both are structural
> guarantees of how this platform builds Kafka subscribers, not something this
> requirement asked for. See **What Got Built** below for what that produces.

&nbsp;

## 5a. Lookups

These mappings include **FK lookups** — `Account` isn't a column, it's a search key to find the right `Customer` row.  AI can't infer that from field names alone.  For publish (Section 7), the mappings are purely name-matching between the format file and `models.py` — something AI can do itself.

&nbsp;

<details markdown>

<summary>What Got Built?  The 2-Message Pattern</summary>

**Two-Message Pattern**

A single-transaction consumer loses data if parsing fails mid-flush — the raw payload is gone. Instead:

```
topic: order_b2b
  → Consumer 1:  save raw JSON blob → OrderB2bMessage  (Tx 1 — always commits)
  → row_event:   blob insert → publish to order_b2b_processed
  → Consumer 2:  parse → Order + Items, resolve FKs, LogicBank rules  (Tx 2)
```

Parse or business-rule failures leave `is_processed = False` on the blob row —
queryable and retryable — **and** write the failure reason to `error_text` on that
same row, so you can tell *why* a message is stuck without cross-referencing server
logs: `SELECT id, error_text FROM order_b2b_message WHERE is_processed = 0`. Neither
of these — the 2-message split or the error capture — is something this project's
requirements asked for; both are how this platform builds every Kafka subscriber.

**Key Files**

See the module docstring in [integration/kafka/kafka_subscribe_discovery/order_b2b.py](../integration/kafka/kafka_subscribe_discovery/order_b2b.py) for design details, field mapping, and test instructions. Supporting files:

| File | Role |
|------|------|
| `logic/logic_discovery/order_b2b_consume.py` | `row_event` bridge — publishes blob to `order_b2b_processed` (no inline parse) |
| `integration/OrderB2bMapper.py` | JSON → Order + Items (3-tier mapping contract) |
| `api/api_discovery/order_b2b_consume_debug.py` | `/consume_debug/order_b2b` — test without Kafka |
| `integration/kafka/message_formats/order_b2b.json` | Message format spec / test fixture |
| `integration/kafka/order_b2b_reset.sh` | Reset Kafka topics + log between runs |

**Quick Test (no Kafka needed)**

```bash
curl 'http://localhost:5656/consume_debug/order_b2b?file=integration/kafka/message_formats/order_b2b.json'
```

</details>

<br>

## 5b. Requirement §5 — Security

requirements also includes a row-level security requirement, applied the same way
as any other:

**Requirement §5 — Row-Level Security:**
```text title="Requirement §5 — Row-Level Security"
Feature: Row-Level Security
  Scenario: Sales role sees limited customers
    Given a user with the sales role
    When querying the Customer list
    Then only return customers where credit_limit >= 3000 or balance > 0
```

This is why the requirements above included an *optional* `add-auth` step — security
only activates once auth is configured; skip it and the rest of the system still runs.

<br>

## 6. How to Test

> **Kafka is optional during development.** The server doesn't require a broker to
> start or run — this is deliberate, so you can build and test the full system with
> zero infrastructure.
>
> * **Subscribe side:** exercised with no broker at all via the `consume_debug`
>   endpoint (`APILOGICPROJECT_CONSUME_DEBUG=true`, on by default) — same code path
>   as live Kafka, just triggered by a curl instead of a topic message.
> * **Publish side:** if no broker is reachable at `localhost:9092`, the publish
>   call still completes the underlying transaction — it buffers the message, waits
>   up to ~10s for the broker, then logs a delivery failure. Nothing crashes; that
>   PATCH will just feel a little slow. That's the timeout you're seeing, not a bug.
>
> Bring up Kafka only when you want to verify the wire-level integration (Step 6
> below).

**1. Start the server:** F5 (or `python api_logic_server_run.py`)

**2. Admin App:** browse to [http://localhost:5656/](http://localhost:5656/) — click
Customer Alice, see Orders and Items.

**3. Check Credit — no Kafka needed:**
**Check Credit — no Kafka needed:**
```bash title="Check Credit — no Kafka needed"
# Good order
curl -X POST http://localhost:5656/api/OrderB2B \
  -H "Content-Type: application/json" \
  -d '{"Account":"Alice","Notes":"test","Items":[{"Name":"Widget","QuantityOrdered":1}]}'

# Over-limit order — expect 400, "balance exceeds credit limit"
curl -X POST http://localhost:5656/api/OrderB2B \
  -H "Content-Type: application/json" \
  -d '{"Account":"Alice","Notes":"over limit","Items":[{"Name":"Widget","QuantityOrdered":50}]}'
```

**4. Kafka Subscribe — no live Kafka needed:**
**Kafka Subscribe — no live Kafka needed:**
```bash title="Kafka Subscribe — no live Kafka needed"
curl "http://localhost:5656/consume_debug/order_b2b?file=integration/kafka/message_formats/order_b2b.json"
```
Verify: `sqlite3 database/db.sqlite "SELECT * FROM 'order' ORDER BY id DESC LIMIT 1; SELECT * FROM item ORDER BY id DESC LIMIT 3;"`

**5. Kafka Publish:** PATCH an order's `date_shipped` (e.g. via the Admin App, or
the API) and watch the log — `publish_kafka_message: delivered to topic
'order_shipping'` if a broker is up, or a delivery-failure log after ~10s if not
(see callout above — expected either way).

**6. (Optional) Live Kafka, end-to-end:**

  1. Start Docker: `docker compose -f integration/kafka/dockercompose_start_kafka.yml up -d`
     (Podman instead of Docker? Use `podman compose` — same file, unchanged. See [DevOps-Podman](https://apilogicserver.github.io/Docs/DevOps-Podman).)
  2. Reset topics: `bash integration/kafka/order_b2b_reset.sh`
  3. Restart the server (after Docker/Podman is up, so it picks up Kafka env vars and subscribes to topics)
  4. Publish a real message to `order_b2b` and confirm it's consumed — same
     verification query as Step 4.


<br>

## 7. Requirement §4 — Publish (By-Example, Outbound Kafka)

A **key-only** publish rule sends just `{"id": 42}` — a notification that tells the
consumer to call back for current data. requirements §4 asked for more: a
**by-example** publish that carries the full shape the consumer needs, so it never
has to call back. `implement requirements` built this directly — no separate
"upgrade" step:

**Requirement §4 — Kafka Publish Shipping Notification:**
```text title="Requirement §4 — Kafka Publish Shipping Notification"
Feature: Kafka Publish Shipping Notification

  Scenario: Notify shipping when an order is dispatched
    Given an Order exists
    When date_shipped is set
    Then publish to Kafka topic order_shipping
    And use message_formats/order_shipping.json as the message shape
    And use by-example publish rather than key-only publish
```

AI reads the format file and `models.py` and maps by name.  Direct matches are silent; uncertain ones get `# TODO: verify` in `FIELD_EXCEPTIONS`; anything unresolvable is added to `_unresolved` and **blocks server start** — reported to you in chat immediately.

For full details and generated code examples, see [Integration EAI — Publish](Integration-EAI#publish--outbound-kafka-messages).
