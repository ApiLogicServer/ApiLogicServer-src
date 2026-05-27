---
title: Customs EAI
notes: gold source is docs
source: docs/Customs-readme
version: 1.2 from docsite, for readme, for readme 5/5/2026
---
<style>
  -typeset h1,
  -content__button {
    display: none;
  }
</style>

# Customs Demo

![summary](https://github.com/ApiLogicServer/Docs/blob/main/docs/images/integration/customs_demo/summary.png?raw=true)

&nbsp;

<details markdown>

<summary>Executable Requirements - Governance By Architecture, At Scale</summary>

![summary](https://github.com/ApiLogicServer/Docs/blob/main/docs/images/architecture/gov-at-scale.png?raw=true)

&nbsp;

**The Underlying Logic Architecture**

![summary](https://github.com/ApiLogicServer/Docs/blob/main/docs/images/architecture/logic-architecture-exec.png?raw=true)
<br>

</details>

&nbsp;

<details markdown>

<summary>Claude Code CLI Instructions - how to build this project</summary>

<br>

```bash title="Establish Initial State, Execute Requirements"
# A - Create the project (already done, typically from Manager)
genai-logic create  --project_name=demo_customs --db_url=sqlite:///samples/requirements/customs_demo/database/customs.sqlite

# B - activate Claude Code in the VSCode terminal
claude

# C - use the shared Manager venv (do not create a local project .venv)
! source ../venv/bin/activate

# D - load context engineering to teach claude about rules, GenAI-Logic
Please load `.github/.copilot-instructions.md`.

# E - in created project, get the requirements (win: Copy-Item -Path "..\samples\requirements\customs_demo\*" -Destination "." -Recurse -Force -Verbose 4>&1).Count)
! cp -rv ../samples/requirements/customs_demo_clvs/. . | wc -l

# F - required hardening for delete integrity (no orphans after parent delete via API):
in database/models.py, add ORM relationship cascade on Shipment child lists.
Apply as follows (NOTE: ShipmentCommodityList is a special case):

   Shipment.PieceList          → relationship(cascade="all, delete", back_populates="shipment")
   Shipment.SpecialHandlingList → relationship(cascade="all, delete", back_populates="shipment")
   Shipment.ShipmentPartyList  → relationship(cascade="all, delete", back_populates="shipment")

   Shipment.ShipmentCommodityList → relationship(passive_deletes='all', back_populates="shipment")
   # ⚠️  ShipmentCommodity has a composite PK where the FK (local_shipment_oid_nbr) is also
   # part of the PK. cascade="all, delete" causes SQLAlchemy to null-out the FK before
   # deleting — which fails for PK columns (any database, not SQLite-specific).
   # passive_deletes='all' bypasses ORM cascade and delegates to the DB-level
   # ON DELETE CASCADE on the FK column.
   # SQLite extra: also requires PRAGMA foreign_keys = ON per connection;
   # PostgreSQL/MySQL enforce FK cascades by default.
   # Note: perhaps simpler to alter db design for single-field pkey

# G - ask Coding Agent to create the system by implementing the requirements
implement requirements docs/requirements/customs_demo
```

</details>

&nbsp;

---

## Executive Summary

This is a proof of what changes when business logic is governed by architecture, not discipline — built to the scope and standards of a real enterprise integration, in 2 days.

**Delivery Speed — 2 Days, Not Months**<br>
Built in 2 days by one engineer. The scope — Kafka 2-message pipeline, XML parsing, 7-table persistence, importer matching, CLVS eligibility rules, REST API, Admin UI, and standard enterprise delivery standards — is not a toy project. A traditional team would scope this in weeks and deliver in months.

Curious what your team would estimate? Give your AI this requirements document and ask.

**Business Inputs — Not Technical Specs**<br>
Traditional delivery starts from *technical* inputs: schema DDL, API specs, field-mapping logic expressed in developer terms. This started from *business* inputs — artifacts the business team already owned.

A plain-English requirements document. An existing database schema. An XML field-mapping spreadsheet. A sample message. GenAI-Logic's Executable Requirements workflow compiled these directly into a running, governed system — no translation layer required.

Speed is not a tradeoff against governance here. Both are consequences of the same thing: declarative rules replace procedural code, so the system is both faster to build and impossible to bypass.

**Governance — No Bypass**<br>
Business rules are enforced at the commit point — every transaction, every source, automatically. Not because developers remembered. Because there is no other path.

A new developer, a new agent, a new integration: all inherit the same rules automatically. Governed by architecture, not discipline.

**Governance — At Scale**<br>
Governance by developer discipline fails at scale — routinely, and at significant cost. Rules get missed. New endpoints, new agents, new integrations don't inherit them. The larger the system, the more paths, and the more paths, the more misses.

Governance by architecture doesn't degrade. Rules enforced at the commit point run on every transaction, regardless of source — API, UI, agent, or integration added three years later. That guarantee doesn't erode as the system grows.

AI makes this available at org-wide scale. Requirements your teams already produce — plain English, Gherkin, regulation text — become the input. GenAI-Logic compiles them into enforced rules. The same workflow, every project, every team.

**Measuring Adoption — the Governance Report**<br>
Governance by architecture only holds if teams are actually using rules. GenAI-Logic includes a built-in health check (`vital signs`) that produces a **Governance Report** scoring each project on two dimensions: *Coverage* (weighted rules per domain table — are the right tables governed?) and *Integrity* (anti-pattern detection — is the rule code correct?). A portfolio leaderboard makes adoption visible across teams without reading a line of code. The same tool that enforces rules also measures whether they're being used.

> For the full story on **Executable Requirements**, [click here](https://apilogicserver.github.io/Docs/executable-requirements).  
> For **Project Governance Report**, [click here](https://apilogicserver.github.io/Docs/IDE-Health-Check).

&nbsp;

## Project Overview

You can examine the Shipment database to verify parties created by matching:

![summary](https://github.com/ApiLogicServer/Docs/blob/main/docs/images/integration/customs_demo/shipment.png?raw=true)

An enterprise integration (EAI) microservice that ingests CIMCorp/ISDC customs shipment data from a Kafka topic, parses the canonical XML format, and persists the resulting shipment records — with full REST API, Admin UI, and a declarative business logic layer ready for governance rules.

**Inputs** (in `docs/elmo_creation/`):
- Database — 7 tables, 130+ columns
- XML-to-DB field mapping (`Classify Entity Details.csv`)
- Sample message (`sample_data/MDE-CDV-HVS-WR-Rev260328.xml`)

**Outputs**:
- Working Kafka consumer pipeline: `isdc` → `ShipmentXml` → `isdc_processed` → DB tables  
- JSON:API for all tables, Admin UI, declarative logic engine
- Matching: look up the matching Customer
    - found: set `Shipment.trprt_bill_to_acct_nbr == CcpCustomer.duty_bill_to_acct_nbr` and create a `ShipmentParty` row
    - no match: log a warning, do nothing.

&nbsp;

## Basic Design - 2 transaction message processing

1. `integration/kafka/kafka_subscribe_discovery/isdc.py` - isdc
    * reads message, inserts into `ShipmentXml` (Tx 1)
    * this ensures messages are saved, even if the xml contains errors
2. `logic/logic_discovery/isdc_consume.py`
    * ShipmentXml insert → publishes raw payload to topic: `isdc_processed`
3. `integration/kafka/kafka_subscribe_discovery/isdc.py` - isdc_processed
    * parses xml → database tables (Tx 2)
4. `api/api_discovery/isdc_kafka_consume_debug.py`
    * `/consume_debug/isdc` bypasses Kafka — calls the same parser directly (no Kafka required for dev/test)
5. Matching: `logic/logic_discovery/shipment_matching.py` — `early_row_event` on Shipment insert
    * Looks up `CcpCustomer` by `duty_bill_to_acct_nbr == trprt_bill_to_acct_nbr`
    * Match found: creates a `ShipmentParty` importer row; (if no match, logs a warning)
5. CLVS: `logic/logic_discovery/clvs_eligibility.py` - computes eligibility


&nbsp;

---

## Appendices

### 2-message Pattern

**Duplicate policy** — default is `replace`: an existing `Shipment` graph is deleted (ORM cascade) and the new parsed graph inserted. Set env var `ISDC_DUPLICATE_POLICY=fail` to raise an error on duplicate `LOCAL_SHIPMENT_OID_NBR` instead.

**Design note — why 2 messages?** The original design used 1 message: receive XML, save `ShipmentXml`, parse into DB tables — all in one transaction. The 2-message design now in place was adopted after reviewing production reliability requirements.

The key advantage is **transaction isolation**. A tempting alternative to 2 messages is a try/catch in the single transaction: always save `ShipmentXml`, best-effort parse the DB tables. This breaks down in SQLAlchemy: a failed flush (e.g. parser error mid-parse) **poisons the session** — you can't commit the blob in the same session after an exception. You'd need two explicit back-to-back transactions, plus a third to write the error back to `ShipmentXml`. That's messy and fragile.

The 2-message design solves this cleanly: Kafka acts as the durable commit boundary between ingestion and processing. The blob is always saved (transaction 1), and a parse failure only affects transaction 2 — no session gymnastics, and back-pressure decoupling is a free bonus.

&nbsp;

### Replace and Match Example

```bash title="Process Shipment - no match"
curl 'http://localhost:5656/consume_debug/isdc?file=docs/requirements/customs_demo/message_formats/demo-01-no-match.xml'
```

Verify the Shipment data, then

```bash title="Process Shipment Replacement - match"
curl 'http://localhost:5656/consume_debug/isdc?file=docs/requirements/customs_demo/message_formats/demo-02-match-replace.xml'
```