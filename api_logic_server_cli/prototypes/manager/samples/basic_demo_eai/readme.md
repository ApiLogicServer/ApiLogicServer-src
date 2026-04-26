---
title: Sample_Basic_EAI
do_process_code_block_titles: True
version: 1.8 from docsite, for readme, for readme 4/21/2026 - message_formats auto-included in prototype, xr
source: docs/Sample-Basic-EAI
Propagation: see api_logic_server_cli/clone_and_overlay_prototypes/create_readme.py
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

    These prompts are **Executable Requirements** — AI can build a *running system* you can use to confirm the requirements, and kick-start development.  As you will observe in the `requirements` (loaded later, below), this project includes

    * **Core Creation Services:** JSON:API, Admin App, standard project (customize in your IDE), standard container deployment
    * **Executable Requirements:** NL creation of multi-table logic, custom APIs, EAI Subscribers and Publishers, and Role Based Access Control

    > This is the same system used in [Executable Requirements](https://apilogicserver.github.io/Docs/Exec-Reqmts), which focuses on how these prompts serve as the living spec — readable by business and IT, executable by AI.

&nbsp;

## Overview


<br>

**🤖 Bootstrap Copilot by pasting the following into the chat:**
```bash title="🤖 Bootstrap Copilot by pasting the following into the chat"
Please load `.github/.copilot-instructions.md`
```


> **Important:** be sure CoPilot is in "Agent" Mode.  "Ask" will not work.  Also, we get consistently good results with `Claude Sonnet 4.6`.

&nbsp;

**Executable Requirements - a new option for your organization**


**Establish Initial State, Execute Requirements:**
```bash title="Establish Initial State, Execute Requirements"
# A - Create project from existing database
genai-logic create --project_name=demo_eai --db_url=sqlite:///samples/dbs/basic_demo.sqlite

# B - in created project, get these requirements
$ cp -r ../samples/requirements/demo_eai/ .

# C - optionally, configure security
$ (cd devops/keycloak; docker compose up -d)
$ genai-logic add-auth --provider-type=keycloak --db-url=localhost

# D - create system from requirements
implement requirements docs/requirements/demo_eai
```

The prompts on this page are the requirements for this system. Execute the steps above to build it.  Thse requirements are not just a description of the system - AI can execute them, directly.

This is a real project: your IDE, your Python, your source control. The prompts create it in minutes — but you own it fully and iterate from there. Change a rule; the engine determines execution order automatically. Add an endpoint; the rules are already there waiting for it.

This suggests a different way to think about requirements gathering. Instead of Word documents that describe a system and then drift from it, requirements can be structured prompts — precise enough for AI to execute, readable enough for business and IT to agree on. The spec and the running system are the same artifact.


&nbsp;

**Enterprise Application Integration - System Requirements**

This app illustrates using IntegrationServices for B2B push-style integrations with APIs, and internal integration with messages.  

&nbsp;

![demp_kafka](https://github.com/ApiLogicServer/Docs/blob/main/docs/images/integration/demo_kafka.png?raw=true)

The **demo_kafka API Logic Server** provides APIs *and logic*:

1. **Order Logic:** enforcing database integrity and application Integration (alert shipping)

2. A **Custom API**, to match an agreed-upon format for B2B partners

3. **Standard APIs** for ad-hoc integration, user interfaces, etc

The **Shipping API Logic Server** listens on kafka, and processes the message.<br><br>

<br>

## 1. Create From Existing DB

<br>

<details markdown>

<summary> Create the Customer, Orders and Product Project [typically already done using Manager]</summary>

<br>


**In the Manager: Create a project from an existing database (probably already done):**
```bash title="In the Manager: Create a project from an existing database (probably already done)"
Create a database project named basic_demo_vibe from samples/dbs/basic_demo.sqlite
```

<br>

<details markdown>

<summary> Your project includes a data model diagram</summary>

<br>

![basic_demo_data_model](https://github.com/ApiLogicServer/Docs/blob/main/docs/images/basic_demo/basic_demo_data_model.jpeg?raw=true)

</details markdown>

&nbsp;

### 1a. Project Opens: Run

The project should automatically open a new window in VSCode. <br>

**🤖 Again, bootstrap Copilot by pasting the following into the chat:**
``` bash title='🤖 Again, bootstrap Copilot by pasting the following into the chat'
Please load `.github/.copilot-instructions.md`.
```

Run it as follows:

1. **Start the Server:** F5 
2. **Start the Admin App:** browse to [http://localhost:5656/](http://localhost:5656/).  The Admin App screen shown below should appear in your Browser.
3. **Verify as shown below**

<details markdown>

<summary>API: filtering, sorting, pagination, optimistic locking,related data access... see Swagger </summary>

Your API is MCP enabled, and ready for custom app dev.  For more information, [click here](https://apilogicserver.github.io/Docs/API-Self-Serve).

![swagger](https://github.com/ApiLogicServer/Docs/blob/main/docs/images/basic_demo/api-swagger.jpeg?raw=true)
</details>

<br>

<details markdown>

<summary>Admin App: multi-page, multi-table, automatic joins, lookups, cascade add - collaboration-ready</summary>

For more information, [click here](https://apilogicserver.github.io/Docs/Admin-Tour).

The Admin App is ready for **[business user agile collaboration](https://apilogicserver.github.io/Docs/Tech-AI/),** and back office data maintenance.  This complements custom UIs created with the API.

Explore the app - click Customer Alice, and see their Orders, and Items.  

![admin-app-initial](https://github.com/ApiLogicServer/Docs/blob/main/docs/images/basic_demo/admin-app-initial.jpeg?raw=true)
</details>

</details>


<br><br>

## 2. Declare Business Logic

Logic (multi-table derivations and constraints) is a significant portion of a system, typically nearly half.  GenAI-Logic provides **spreadsheet-like rules** that dramatically simplify and accelerate logic development.

Rules are declared in Copilot using Natural Language, or directly in Python with IDE code completion.  The screen below shows the 5 rules for **Check Credit Logic.**

**1. Stop the Server** (Red Stop button, or Shift-F5 -- see Appendix)

**2. Add Business Logic**

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

![Nat Lang Logic](https://github.com/ApiLogicServer/Docs/blob/main/docs/images/sample-ai/copilot/copilot-logic-vibe.png?raw=true)

<br>

## 3. Message Formats — Already Included

AI generates integrations **by example** — provide a sample message shape and it auto-maps obvious field names silently, lists exceptions you specify, and blocks server start on anything unresolvable.  They double as test fixtures.

The project already includes sample message formats in `integration/kafka/message_formats/`:

- `order_b2b.json` — inbound B2B order format
- `order_shipping.json` — outbound shipping notification format

> See [Integration EAI](Integration-EAI#ai-based-creation) for how AI uses these.

> **Tip — mappings belong here too.**  If you have complex or non-obvious field mappings, save them alongside the format file — in any structure that's clear to you and AI: a CSV, a plain-text table, extra comments in the JSON.  AI will read whatever you reference in the prompt.  Keeping mappings here (rather than embedded in the prompt) means they're versioned, reusable, and self-documenting.

&nbsp;

<br>

## 4. Custom API - B2B Orders

To fit our system into the Value Chain,
we need a **Custom API** to accept orders from B2B partners, and forward paid orders to shipping via Kafka.

**Create the Custom B2B API Endpoint:**
``` bash title="Create the Custom B2B API Endpoint"
Create a B2B order API called 'OrderB2B' that accepts orders from external partners.

The external message format is in `integration/kafka/message_formats/order_b2b.json`.

Field mappings:
- 'Account' → lookup Customer by name, set customer_id
- 'Notes' → order notes
- 'Items' array → Item rows: 'Name' → lookup Product, 'QuantityOrdered' → item quantity

The API should create complete orders.
```

The Kafka logic was created earlier, so we are ready to test — see Section 6.

<br>

## 5. EAI Subscribe — Inbound Kafka Message

The format file was already saved in Section 3.  Now prompt AI, referencing it:

**Subscribe to sales message - Kafka Enterprise Application Integration:**
```text title="Subscribe to sales message - Kafka Enterprise Application Integration"
Subscribe to Kafka topic `order_b2b` (JSON format).

The message format is in `integration/kafka/message_formats/order_b2b.json`.

Target tables: Order, Item (from models.py).

Field mappings:
- `Account` → look up Customer by Customer.name, set Order.customer_id
- `Notes` → Order.notes
- `Items` array → Item rows: `Name` → look up Product by Product.name, set Item.product_id; `QuantityOrdered` → Item.quantity
```


&nbsp;
**ppings here but not in Section 7?**
&nbsp;
    These mappings are **FK lookups** — `Account` isn't a column, it's a search key to find the right `Customer` row.  AI can't infer that from field names alone.  For publish (Section 7), the mappings are purely name-matching between the format file and `models.py` — something AI can do itself.

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

Parse failures leave `is_processed = False` on the blob row — queryable and retryable.

**Key Files**

See the module docstring in [integration/kafka/kafka_subscribe_discovery/order_b2b.py](../integration/kafka/kafka_subscribe_discovery/order_b2b.py) for design details, field mapping, and test instructions. Supporting files:

| File | Role |
|------|------|
| `logic/logic_discovery/place_order/order_b2b_consume.py` | `row_event` bridge — publishes blob to `order_b2b_processed` (no inline parse) |
| `integration/OrderB2bMapper.py` | JSON → Order + Items (3-tier mapping contract) |
| `api/api_discovery/order_b2b_kafka_consume_debug.py` | `/consume_debug/order_b2b` — test without Kafka |
| `integration/kafka/message_formats/order_b2b.json` | Message format spec / test fixture |
| `test/order_b2b_reset.sh` | Reset Kafka topics + log between runs |

**Quick Test (no Kafka needed)**

```bash
curl 'http://localhost:5656/consume_debug/order_b2b?file=integration/kafka/message_formats/order_b2b.json'
```

</details>

<br>

## 6. Test

Observe that the API and message listener use the same underlying logic.

`integration/kafka/kafka_subscribe_discovery/order_b2b.py` illustrates unit testing:

**Test stand-alone, and with Kafka:**
```bash title="Test stand-alone, and with Kafka"
Debug / test (no Kafka required):
  APILOGICPROJECT_CONSUME_DEBUG=true is set in config/default.env
  1. Start server: python api_logic_server_run.py
  2. curl 'http://localhost:5656/consume_debug/order_b2b?file=integration/kafka/message_formats/order_b2b.json'
  3. Verify DB: sqlite3 database/db.sqlite "SELECT * FROM order_b2b_message; SELECT * FROM 'order'; SELECT * FROM item;"

Live Kafka:
  1. docker compose -f integration/kafka/dockercompose_start_kafka.yml up -d
  2. Enable KAFKA_CONSUMER + KAFKA_PRODUCER in config/default.env
  3. bash integration/kafka/order_b2b_reset.sh       # recreates topics + clears log
  4. Start server; publish sample JSON to order_b2b topic
```


<br>

## 7. Publish — Outbound Kafka Messages (By-Example)

In Section 2, the logic prompt already generated a **key-only** publish rule: when `date_shipped` is set, it sends `{"id": 42}` — a notification that tells the consumer to call back for the current data.

Now let's upgrade that to **by-example**: a shaped message that carries all the data the consumer needs, so it never has to call back.  AI will replace the key-only rule in `app_integration.py` with the mapper-based version.  The outbound format was saved in Section 3 — just reference it:

**Prompt for by-example publish:**
```text title="Prompt for by-example publish"
Upgrade the order_shipping publish to by-example.

The desired outbound message format is in `integration/kafka/message_formats/order_shipping.json`.
```


&nbsp;
**pings needed in the prompt**
&nbsp;
    AI reads the format file and `models.py` and maps by name.  Direct matches are silent; uncertain ones get `# TODO: verify` in `FIELD_EXCEPTIONS`; anything unresolvable is added to `_unresolved` and **blocks server start** — reported to you in chat immediately.  Only add exceptions to the prompt if you want to override AI's inference.

For full details and generated code examples, see [Integration EAI — Publish](Integration-EAI#publish--outbound-kafka-messages).
