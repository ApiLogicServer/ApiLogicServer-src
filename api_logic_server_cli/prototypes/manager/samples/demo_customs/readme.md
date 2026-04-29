---
title: Customs EAI
notes: gold source is docs
source: docs/Customs-readme
version: 1.1 from docsite, for readme, for readme 4/15/2026
---
<style>
  -typeset h1,
  -content__button {
    display: none;
  }
</style>

# Customs Demo

**Bootstrap Copilot by pasting the following into the chat:**
```
Please load `.github/.copilot-instructions.md`.
```

&nbsp;

## Executive Summary

This system ingests customs shipment data from a Kafka message broker, matches shipments to known importers, and persists a complete, governed shipment record — with full REST API, audit trail, and Admin UI included. 

**Delivery Speed**<br>
It was built in 2 days by one engineer using GenAI-Logic's Executable 
Requirements workflow: a plain-English requirements document was compiled into a running, 
governed system. The primary inputs were an existing database schema, an XML field-mapping 
spreadsheet, and a sample message.

A comparable conventional project covers significant scope: Kafka pipeline, XML parsing, 7-table persistence, importer matching, REST API, Admin UI, and standard enterprise delivery. Curious what that would take to build traditionally? Give your AI this requirements document and ask for an estimate — then compare.

**Governance**<br>
The deeper value is not speed alone. Business rules are enforced by architecture on every 
path — API, UI, agent, or new endpoint — without developer discipline required. A new 
developer, a new agent, a new integration: all inherit the same rules automatically. Governed 
by architecture, not discipline.

> For the full story on **Executable Requirements**, [click here](https://apilogicserver.github.io/Docs/executable-requirements).

&nbsp;

## Project Overview

This system is a prototype for a rewrite of the following, using Kafka instead of JMS, and sqlite:

![summary](https://github.com/ApiLogicServer/Docs/blob/main/docs/images/integration/customs_demo/summary_flow.png?raw=true)

![summary](https://github.com/ApiLogicServer/Docs/blob/main/docs/images/integration/customs_demo/shipment.png?raw=true)

An enterprise integration (EAI) microservice that ingests CIMCorp/ISDC customs shipment data from a Kafka topic, parses the canonical XML format, and persists the resulting shipment records — with full REST API, Admin UI, and a declarative business logic layer ready for governance rules.

**Inputs** (in `docs/elmo_creation/`):
- Database — 7 tables, 130+ columns
- XML-to-DB field mapping (`Classify Entity Details.csv`)
- Sample message (`sample_data/MDE-CDV-HVS-WR-Rev260328.xml`)

**Outputs**:
- Working Kafka consumer pipeline: `isdc` → `ShipmentXml` → `isdc_processed` → DB tables  
- JSON:API for all tables, Admin UI, declarative logic engine
- Matching: look up the matching CcpCustomer
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
    * Match found: creates a `ShipmentParty` importer row; no match: logs a warning

&nbsp;

## Creation Instructions

This context of this project is to add processing for an existing database.  This recreates that state, and then uses **Executable Requirements** (Step E - for more information,  to create the functionality.

```bash title="Establish Initial State, Execute Requirements"
# A - Create the project (already done)
genai-logic create  --project_name=demo_customs --db_url=sqlite:///samples/requirements/customs_demo/database/customs.sqlite

# B - in created project, get the requirements
$ cp -r ../samples/requirements/customs_demo/. .

# C - use the shared Manager venv (do not create a local project .venv)
source ../venv/bin/activate

# D - required hardening for delete integrity (no orphans after parent delete via API):
in database/models.py, add ORM relationship cascade on Shipment child lists
(pattern: relationship(cascade="all, delete", back_populates="...")).
Apply to:
   Shipment.PieceList
   Shipment.ShipmentCommodityList
   Shipment.SpecialHandlingList
   Shipment.ShipmentPartyList

# E - ask Copilot to create the system by implementing the requirements
implement req docs/requirements/customs_demo
```

&nbsp;

# Appendices

## 2-message Pattern

**Duplicate policy** — default is `replace`: an existing `Shipment` graph is deleted (ORM cascade) and the new parsed graph inserted. Set env var `ISDC_DUPLICATE_POLICY=fail` to raise an error on duplicate `LOCAL_SHIPMENT_OID_NBR` instead.

**Design note — why 2 messages?** The original design used 1 message: receive XML, save `ShipmentXml`, parse into DB tables — all in one transaction. The 2-message design now in place was adopted after reviewing production reliability requirements.

The key advantage is **transaction isolation**. A tempting alternative to 2 messages is a try/catch in the single transaction: always save `ShipmentXml`, best-effort parse the DB tables. This breaks down in SQLAlchemy: a failed flush (e.g. parser error mid-parse) **poisons the session** — you can't commit the blob in the same session after an exception. You'd need two explicit back-to-back transactions, plus a third to write the error back to `ShipmentXml`. That's messy and fragile.

The 2-message design solves this cleanly: Kafka acts as the durable commit boundary between ingestion and processing. The blob is always saved (transaction 1), and a parse failure only affects transaction 2 — no session gymnastics, and back-pressure decoupling is a free bonus.

&nbsp;

## Replace and Match Example

```bash title="Process Shipment - no match"
curl 'http://localhost:5656/consume_debug/isdc?file=docs/requirements/customs_demo/message_formats/demo-01-no-match.xml'
```

Verify the Shipment data, then

```bash title="Process Shipment Replacement - match"
curl 'http://localhost:5656/consume_debug/isdc?file=docs/requirements/customs_demo/message_formats/demo-02-match-replace.xml'
```