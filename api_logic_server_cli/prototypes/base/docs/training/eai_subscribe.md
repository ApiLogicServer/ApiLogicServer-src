---
title: EAI Consume Pattern — Kafka + XML/JSON → DB
description: Two-message Kafka consume pattern with generic by-name XML/JSON mapper. Covers blob-row bridge, 3-tier mapping contract, local debug mode, and generated test data.
source: Generic training for ApiLogicServer projects with GenAI integration
usage: AI assistants read this when detecting Kafka consume, EAI, or XML/JSON-to-DB patterns in a user prompt
version: 1.1
date: April 4, 2026
related:
  - subsystem_creation.md (Kafka outbound, row_event patterns)
  - logic_bank_patterns.md (row_event, commit_row_event)
  - logic_bank_api.md (full rule API)
changelog:
    - 1.1 (April 12, 2026): Added source-PK normalization rule for placeholder external IDs (e.g. 0), plus insert-only rerun DB-reset guidance
  - 1.0 (April 4, 2026): Initial — extracted from a production customs/logistics EAI project
---

# EAI Consume Pattern — Kafka + XML/JSON → DB

=============================================================================
🌍 REAL-WORLD EXAMPLE — Why This Matters
=============================================================================

Production customs/logistics EAI consume (confidential client):
- Oracle DDL, 7 tables, 130+ columns
- Canonical XML format, published to Kafka topic
- Required: parse XML → persist Shipment + Piece + ShipmentParty + ShipmentCommodity rows

| Approach | Elapsed | Effort |
|---|---|---|
| Standard Java (8-person enterprise team) | 70 days | 560 eng-days |
| GenAI-Logic (1 engineer) | **2 days** | **2 eng-days** |

Entire pipeline — Kafka consumers, XML mapper, ORM persistence, Admin UI, REST API — in 2 days.
Phase 2 governance rules (matching, validation) added declaratively; automatically enforced on
all paths (Kafka, REST, agents) without touching the consumers.

=============================================================================
🔍 PATTERN DETECTION — READ THIS FIRST
=============================================================================

**Signal phrases — any of these = EAI Consume pattern:**
- "consume from Kafka topic", "ingest from Kafka", "Kafka listener"
- "parse XML/JSON from message", "map message to database"
- "EAI", "enterprise application integration", "message-driven consume"
- "receive shipment XML", "process incoming messages", "topic → database"
- "subscribe to topic and persist"

**STOP before building a single-transaction consume.** See the 2-message design below.

---

## 🚨 Critical Design Decision — Two-Message Pattern

**Never** save the raw payload and parse it in a single transaction.

A parse failure mid-flush **poisons the SQLAlchemy session** — you cannot commit the blob
after an exception in the same session. The workaround (3 explicit transactions + session
gymnastics) is fragile and error-prone.

**Use the 2-message design:**

```
Topic: xyz
  → Consumer 1: save raw payload to XyzMessage blob row, commit  (Tx 1 — always succeeds)
  → row_event on XyzMessage insert: publish to topic xyz_processed
  → Consumer 2: parse payload → persist domain rows, commit       (Tx 2 — parse failure isolated)
```

Benefits:
- Blob always saved — no data loss on parse errors
- Parse failures fully isolated (only Tx 2 affected)
- Back-pressure decoupling free bonus
- Kafka = durable commit boundary between ingestion and processing

---

## Generated Artifacts (4 files)

Given: **topic name**, **target model class(es)**, **format (xml or json)**

### 1. Blob table (add to schema + models.py)

```python
class XyzMessage(Base):
    __tablename__ = 'xyz_message'
    id           = Column(Integer, primary_key=True)
    received_at  = Column(DateTime, default=datetime.utcnow)  # audit: when received
    payload      = Column(Text, nullable=False)                # raw XML or JSON blob
    is_processed = Column(Boolean, default=False)             # True after Tx 2 commits
```

> **models.py imports**: ensure `from datetime import datetime` is at the top of models.py.
> The generated file already has it; if missing (e.g. after a rebuild), add it.

`received_at` is set on insert (Tx 1). `is_processed` flips to `True` when consumer 2
commits successfully (Tx 2). On parse failure Tx 2 rolls back — blob stays `False`,
queryable for retry: `SELECT * FROM xyz_message WHERE is_processed = 0`.

### 2. Topic handler file (`integration/kafka/kafka_subscribe_discovery/xyz.py`)

Drop this file in `kafka_subscribe_discovery/` — it is auto-discovered at server start,
no edits to `kafka_consumer.py` required. Add a 2nd consumer by adding a 2nd file.

```python
# integration/kafka/kafka_subscribe_discovery/xyz.py
import json
import logging
import safrs
from database import models
from integration.system.EaiSubscribeMapper import resolve_lookups

logger = logging.getLogger('integration.kafka')

# Field mapping exceptions for xyz topic — None=skip, str=remap to that column name
XYZ_EXCEPTIONS: dict[str, str | None] = {
    # "FIELD_NAME": None,          # skip
    # "FIELD_NAME": "col_name",    # remap
}

# Lookup dicts — omit if no lookups needed (see § Lookup Resolution)
XYZ_PARENT_LOOKUPS = []   # e.g. [(models.Customer, models.Customer.Id, 'AccountId', 'CustomerId')]
XYZ_CHILD_LOOKUPS  = []   # e.g. [(models.Product, models.Product.ProductName, 'ProductName', 'ProductId')]
XYZ_CHILD_KEY = 'Items'   # key in raw JSON holding the child array


def process_xyz_payload(payload: str, session, blob_id: int = None):
    """
    Parse payload, resolve lookups, persist domain rows, mark blob processed.
    Single function called by both consumer 2 (Kafka) and /consume_debug (no-Kafka debug).

    blob_id=None (debug path): blob created inside this function in the same Tx.
    blob_id set  (Kafka path): existing blob fetched and is_processed set to True.
    """
    from integration.XyzMapper import parse
    raw = json.loads(payload)
    parent_row, detail_rows = parse(payload, exceptions=XYZ_EXCEPTIONS)
    resolve_lookups(parent_row, raw, XYZ_PARENT_LOOKUPS, session)
    for child_row, child_src in zip(detail_rows, raw.get(XYZ_CHILD_KEY, [])):
        resolve_lookups(child_row, child_src, XYZ_CHILD_LOOKUPS, session)
        parent_row.ChildList.append(child_row)
    session.add(parent_row)
    if blob_id:
        blob = session.get(models.XyzMessage, blob_id)
        if blob:
            blob.is_processed = True
    else:
        blob = models.XyzMessage(payload=payload, is_processed=True)
        session.add(blob)
    session.commit()
    return parent_row, blob


def register(bus):
    """Called by kafka_subscribe_discovery/auto_discovery.py before bus.run()."""

    @bus.handle('xyz')
    def xyz(msg, safrs_api):
        """Consumer 1: save blob, commit. row_event publishes to xyz_processed."""
        with safrs_api.app.app_context():
            session = safrs.DB.session
            blob = models.XyzMessage(payload=msg.value().decode('utf-8'))
            session.add(blob)
            session.commit()   # blob.id assigned; row_event publishes to xyz_processed

    @bus.handle('xyz_processed')
    def xyz_processed(msg, safrs_api):
        """Consumer 2: parse + persist domain rows, mark blob processed (atomic Tx 2)."""
        with safrs_api.app.app_context():
            session = safrs.DB.session
            blob_id = int(msg.key().decode('utf-8')) if msg.key() else None
            try:
                process_xyz_payload(msg.value().decode('utf-8'), session, blob_id=blob_id)
            except Exception as e:
                logger.exception(f"xyz_processed parse error")  # blob stays is_processed=False; full traceback logged
```

### 3. Row event bridge (`logic/logic_discovery/xyz_consume.py`)

```python
def _publish_xyz(row: models.XyzMessage, old_row, logic_row: LogicRow):
    if not logic_row.is_inserted() or not row.payload:
        return
    import integration.kafka.kafka_producer as kafka_producer
    if kafka_producer.producer is None:
        # Kafka not configured — /consume_debug does Tx 2 directly; nothing to do here
        logic_row.log("_publish_xyz: Kafka not configured — skipping publish")
        return
    kafka_producer.producer.produce(topic='xyz_processed', key=str(row.id), value=row.payload.encode('utf-8'))
    kafka_producer.producer.flush(timeout=10)

def declare_logic():
    Rule.after_flush_row_event(on_class=models.XyzMessage, calling=_publish_xyz)
```

> **Do not import producer by value.**
> `from integration.kafka.kafka_producer import producer` captures a stale snapshot (often `None`
> before startup wiring finishes). Always import the module and read `kafka_producer.producer`
> at call time inside the row-event function.

> **Why `after_flush_row_event`, not `row_event`?** `row_event` fires during `before_flush` — before SQLite/Postgres assigns the autoincrement `id`. Publishing `key=str(row.id)` at that point sends the string `'None'`, causing Consumer 2 to crash on `int(key)`. `after_flush_row_event` fires after the flush assigns the id, so the key is always a valid integer. Additionally, any new rows added to the session mid-flush (inside `row_event`) miss the fresh LogicBank rule pass — Copy and Formula rules will not fire for those rows. Tx 2 (consumer 2 or `/consume_debug`) commits independently in a clean `before_flush`, so all rules fire correctly.

### 4. Mapper (`integration/XyzMapper.py`) — see 3-tier contract below

---

## 3-Tier Mapping Contract

The mapper uses a progressive escalation model — use the simplest tier that handles the field:

### Tier 1 — Automatic (zero configuration)
`lowercase(field_name)` → column name, set via `setattr` only if column exists on model.
For XML: `field_name` = element local-name. For JSON: `field_name` = dict key.
Handles the majority of fields in any well-named schema. Free, no exceptions dict needed.

### Tier 2 — Declarative exceptions dict
Defined in `kafka_consumer.py` alongside the listener that owns it — one dict per topic.
Passed into `parse()` as an argument; the mapper forwards it to `populate_row()`.
With multiple consumers each listener has its own dict — no conflicts.

```python
# in kafka_consumer.py — co-located with the listener
XYZ_EXCEPTIONS: dict[str, str | None] = {
    "FIELD_NAME": None,          # None  = skip this field entirely
    "FIELD_NAME": "col_name",    # str   = remap to this column name
}
```

### Tier 3 — Custom callback (escape hatch for complex logic)
```python
def custom_mapping(row: models.XyzParent, element, logic_row=None):
    """
    Called after Tier 1 + Tier 2 mapping completes.
    Add complex derivations, cross-field logic, or lookups here.
    """
    # ADD CUSTOM MAPPING LOGIC HERE
    pass
```
Pass to `populate_row(..., custom=custom_mapping)` for full control without framework fighting.

### Lookup Resolution — Name → FK (post-parse, optional)

When an incoming field carries a *name* that must be resolved to a FK via a DB query,
call `resolve_lookups()` **after** `parse()`. This keeps `parse()` pure (no DB session
required) and places all mapping config — exceptions *and* lookups — declaratively in
the topic handler file alongside the listener that owns them.

**Lookup tuple formats:**

Single-field (most common): `(lookup_model, lookup_col, source_field, fk_col)`

| field | meaning | example |
|---|---|---|
| `lookup_model` | model class to query | `models.Customer` |
| `lookup_col` | column to filter by — unique, **need not be PK** | `models.Customer.Id` |
| `source_field` | key/tag name in the incoming payload | `'AccountId'` |
| `fk_col` | FK attribute to set on the target row | `'CustomerId'` |

Compound-field (when uniqueness requires multiple columns): `(lookup_model, [(col, source_field), ...], fk_col)`

```python
# Example: Employee identified by LastName + FirstName together
(models.Employee,
 [(models.Employee.LastName, 'Surname'), (models.Employee.FirstName, 'Given')],
 'EmployeeId')
```

**In the topic handler file (`kafka_subscribe_discovery/xyz.py`):**
```python
from integration.system.EaiSubscribeMapper import resolve_lookups

# Parent-level lookups — applied to parent_row
XYZ_PARENT_LOOKUPS = [
    (models.Customer, models.Customer.name, 'Account', 'customer_id'),
    # add more as needed
]

# Child-level lookups — applied to each row in extras
XYZ_CHILD_LOOKUPS = [
    (models.Product, models.Product.ProductName, 'Name', 'product_id'),
]
XYZ_CHILD_KEY = 'Items'   # key in raw payload that holds the child array
```

**Enhanced consumer 2 (with lookups):**
```python
    @bus.handle('xyz_processed')
    def xyz_processed(msg, safrs_api):
        with safrs_api.app.app_context():
            session = safrs.DB.session
            from integration.XyzMapper import parse
            import json
            blob_id = int(msg.key().decode('utf-8')) if msg.key() else None
            try:
                payload = msg.value().decode('utf-8')
                parent_row, extras = parse(payload, exceptions=XYZ_EXCEPTIONS)
                raw = json.loads(payload)           # cheap second parse for lookup values
                resolve_lookups(parent_row, raw, XYZ_PARENT_LOOKUPS, session)
                for child_row, child_src in zip(extras, raw.get(XYZ_CHILD_KEY, [])):
                    resolve_lookups(child_row, child_src, XYZ_CHILD_LOOKUPS, session)
                    parent_row.ChildList.append(child_row)  # 🚨 attach via relationship — NOT session.add(child_row); see note below
                session.add(parent_row)  # 🚨 NEVER session.merge — see note below
                if blob_id:
                    blob = session.get(models.XyzMessage, blob_id)
                    if blob:
                        blob.is_processed = True
                session.commit()
            except Exception as e:
                logger.exception(f"xyz_processed parse error")  # blob stays is_processed=False; full traceback logged
```

> **XML payloads:** replace `json.loads(payload)` with `ET.fromstring(payload)`.
> `resolve_lookups` accepts both `dict` and `ET.Element` as `source`.

> 🚨 **NEVER use `session.merge` for incoming messages.** `session.merge` upserts — if the
> PK is already in the SQLAlchemy identity map (e.g. Kafka offset replayed on restart), it fires
> as an UPDATE. LogicBank then re-triggers change propagation to all children on every subsequent
> `session.flush()`, creating an unbounded duplicate-row loop. Always use `session.add(parent_row)`
> with children pre-attached to relationship lists — LogicBank sees each row as a clean insert
> and rules fire exactly once.

> 🚨 **Always attach child rows via the parent relationship, not `session.add(child)` with only FK set.**
> This is a mandatory rule, not a style preference.
> `parent_row.ChildList.append(child_row)` causes SQLAlchemy to set the FK automatically and
> LogicBank to see the insert in proper parent-child context. A standalone `session.add(child_row)`
> with only a raw FK column set can trigger a "Missing Parent" constraint error during flush,
> even when the FK value itself is correct.
> This applies equally in `row_event` / matching / enrichment callbacks that create derived child rows during Tx 2.

> 🚨 **Normalize placeholder external IDs before assigning local PK columns.**
> Partner payloads frequently carry sentinel IDs (`0`, empty string) in fields that look like IDs
> but are not globally unique in your local table. If such a field maps to a local PK, treat
> sentinel/non-unique values as *not provided*:
> - set the PK attribute to `None`
> - let DB autoincrement assign the local primary key
>
> Real failure case: both consignee and shipper carried `PARTY_OID_NBR=0`; mapping that value
> directly into `shipment_party_oid_nbr` caused `UNIQUE constraint failed` and rolled back Tx 2.
>
> Example normalization:
> ```python
> populate_row(party_row, section, exceptions=XYZ_EXCEPTIONS)
> if party_row.shipment_party_oid_nbr in (0, None):
>     party_row.shipment_party_oid_nbr = None
> ```

> **Idempotency / replay (insert-only default):** If a `xyz_processed` message is replayed
> (consumer restart, offset reset), Tx 2 can attempt to insert domain rows that already exist.
> The default policy is **insert-only**:
> - Reject duplicates with an explicit error (do not mutate existing domain rows)
> - Keep blob rows for audit/retry (`is_processed` indicates successful Tx 2)
> - Never use `session.merge` or delete-and-reinsert as an idempotency mechanism
> If a project truly needs upsert semantics, it must be explicitly specified and tested.

---

### Generated mapper skeleton

**XML format** (`ET.fromstring` + element children):
```python
# integration/XyzMapper.py
import xml.etree.ElementTree as ET
from database import models
from integration.system.EaiSubscribeMapper import populate_row, _local

TAG_ROUTING = {
    "xyz":    (models.XyzParent, {}),           # section tag → (ModelClass, overrides)
    "child":  (models.XyzChild,  {"type_cd": "C"}),
    # ADD additional section tags here
}

def parse(payload: str, exceptions: dict = None) -> tuple:
    """Returns (parent_row, extras_list). exceptions passed in from kafka_consumer."""
    root = ET.fromstring(payload)
    parent = models.XyzParent()
    extras = []
    for section in root:
        tag = _local(section.tag)           # strip XML namespace
        if tag not in TAG_ROUTING:
            continue
        model_class, overrides = TAG_ROUTING[tag]
        row = model_class()
        populate_row(row, section, exceptions=exceptions, overrides=overrides)
        # attach to parent or extras as appropriate
    return parent, extras
```

**JSON format** (`json.loads` + dict keys):
```python
# integration/XyzMapper.py  (JSON variant)
import json
from database import models
from integration.system.EaiSubscribeMapper import populate_row_from_dict

TAG_ROUTING = {
    "xyz":    (models.XyzParent, {}),
    "child":  (models.XyzChild,  {"type_cd": "C"}),
}

def parse(payload: str, exceptions: dict = None) -> tuple:
    """Returns (parent_row, extras_list). exceptions passed in from kafka_consumer."""
    data = json.loads(payload)
    parent = models.XyzParent()
    extras = []
    for key, value in data.items():
        if key not in TAG_ROUTING:
            continue
        model_class, overrides = TAG_ROUTING[key]
        row = model_class()
        populate_row_from_dict(row, value, exceptions=exceptions, overrides=overrides)
        # attach to parent or extras as appropriate
    return parent, extras
```

---

## Sample Data Generation (when no sample message exists)

If no sample XML/JSON is available, generate one from the model schema:

```
Generate a minimal sample XML for models [XyzParent, XyzChild] with:
- One parent element with all columns populated (string→"example", int→1,
  date→"2026-01-01", decimal→"0.00")
- One child element nested under the parent
- Save to docs/sample_data/sample_xyz.xml
```

The AI reads `models.py`, introspects column names and types via `sa_inspect`, and generates
representative values. The sample is used as the `/consume_debug/<topic>` input — no live Kafka required.

---

## Local Debug Mode (no Kafka required)

**Do not use a standalone Python script.** Direct `session.add()` outside the Flask app
bypasses LogicBank — SQLAlchemy event listeners are only registered when the server starts.
Rules will not fire.

**Do not parse inside the `row_event` bridge.** The `row_event` fires during `before_flush`.
Adding new rows (Order, OrderDetail) to the session at that point means they miss the fresh
`before_flush` pass where LogicBank evaluates Copy and Formula rules — those columns stay NULL.

**Correct approach: create `api/api_discovery/xyz_kafka_consume_debug.py`** — one file per topic, following the standard `api_discovery` pattern (auto-discovered at startup, filename makes the topic obvious).

```python
# api/api_discovery/xyz_kafka_consume_debug.py
import logging, os
from pathlib import Path
import safrs
from flask import request, jsonify

app_logger = logging.getLogger("api_logic_server_app")

def add_service(app, api, project_dir, swagger_host: str, PORT: str, method_decorators=[]):
    if not os.getenv('APILOGICPROJECT_CONSUME_DEBUG'):
        return

    @app.route('/consume_debug/xyz')
    def consume_debug_xyz():
        """Debug the xyz consume pipeline without Kafka.
        Enable with: export APILOGICPROJECT_CONSUME_DEBUG=true
        curl 'http://localhost:5656/consume_debug/xyz?file=docs/sample_data/sample_xyz.json'
        """
        file_path = request.args.get('file')
        if not file_path:
            return jsonify({"success": False, "message": "Missing ?file= parameter"})
        from integration.kafka.kafka_subscribe_discovery.xyz import process_xyz_payload
        try:
            payload = Path(file_path).read_text()
            _, blob = process_xyz_payload(payload, safrs.DB.session)
            return jsonify({"success": True, "topic": "xyz", "blob_id": blob.id, "file": file_path})
        except Exception as e:
            app_logger.error(f"consume_debug/xyz: {e}")
            return jsonify({"success": False, "topic": "xyz", "error": str(e)}), 500
```

The endpoint calls `process_xyz_payload()` — the same function consumer 2 uses — so debug and
production paths are identical. LogicBank fires Copy + Formula + Sum rules correctly because
the commit happens in a fresh transaction (not inside a `row_event` `before_flush`).

**Development workflow:**

*No-Kafka debug (fastest — start here):*
1. Generate sample JSON from schema (if none exists)
2. `APILOGICPROJECT_CONSUME_DEBUG=true` is set in `config/default.env` by default
3. Start server: `python api_logic_server_run.py`
4. `curl 'http://localhost:5656/consume_debug/xyz?file=docs/sample_data/sample_xyz.json'`
5. Verify DB — confirm FK columns non-null (lookups worked) and computed columns non-null (LogicBank rules fired)

*Live Kafka:*
6. Start Kafka (idempotent — safe if already running): `docker compose -f integration/kafka/dockercompose_start_kafka.yml up -d`
7. In `config/default.env`, add/uncomment `APILOGICPROJECT_KAFKA_CONSUMER` and `APILOGICPROJECT_KAFKA_PRODUCER`.
    Use the **full 6-key form** — the 2-key shortcut omits settings that cause silent consume failures:
    ```
    KAFKA_SERVER = localhost:9092
    KAFKA_CONSUMER_GROUP = <project>-group1
    APILOGICPROJECT_KAFKA_CONSUMER = "{\"bootstrap.servers\": \"localhost:9092\", \"group.id\": \"<project>-group1\", \"auto.offset.reset\": \"earliest\", \"enable.auto.commit\": \"false\", \"session.timeout.ms\": \"6000\", \"heartbeat.interval.ms\": \"2000\"}"
    APILOGICPROJECT_KAFKA_PRODUCER = "{\"bootstrap.servers\": \"localhost:9092\"}"
    ```
    Use a project-specific value for `<project>` (example: `customs_demo`).
    > **Why `session.timeout.ms: 6000`?** The default (45 s) means stale consumer sessions from a
    > prior server run hold the partition assignment for up to 45 s after the process dies. During
    > that window the new server's consumer polls but receives nothing (no active member).
    > Set `session.timeout.ms` low (≥ `heartbeat.interval.ms × 3`) so the partition is re-assigned
    > quickly. `6000 / 2000` (3 × multiplier) is the safe minimum.
    >
    > **Why `auto.offset.reset: earliest`?** Without it, confluent-kafka defaults to `latest` — the
    > consumer only sees messages published *after* it first subscribes. Any message published before
    > subscribe completes is silently skipped.
    >
    > **`APILOGICPROJECT_KAFKA_CONSUMER` overrides `Config.KAFKA_CONSUMER`** via Flask's
    > `from_prefixed_env()`. For local tests, prefer only `KAFKA_SERVER` + `KAFKA_CONSUMER_GROUP`.
    > If you explicitly set `APILOGICPROJECT_KAFKA_CONSUMER`, you own all keys; omitting any key
    > loses its default value.
8. Run `bash integration/kafka/xyz_reset.sh` — creates topics + clears log
9. For insert-only pipelines, clear domain tables between repeat test runs (optional helper: `integration/kafka/xyz_reset_db.sh`) so replay duplicates do not masquerade as parser failures.
10. Start server (or restart if already running before reset)
11. Publish sample message — use `jq -c .` to compact JSON to a single line (kafka-console-producer sends one Kafka message per input line):
    ```bash
    jq -c . docs/sample_data/sample_xyz.json | \
    ⚠️ XML payloads: `kafka-console-producer` also treats each input line as a separate message.
    If publishing XML through console-producer, first collapse to a single line (or use a producer script/library) to avoid flooding the topic with partial XML fragments.
      docker exec -i broker1 /opt/kafka/bin/kafka-console-producer.sh \
      --bootstrap-server localhost:9092 --topic xyz
    ```
    ⚠️ **Python docstring rule:** When embedding this command in a module docstring, write it as a
    **single line** — no `\` continuation. `\` inside a Python docstring becomes `\\` in source,
    which is not a shell line continuation and breaks copy-paste from the editor.
    ```
    jq -c . docs/sample_data/sample_xyz.json | docker exec -i broker1 /opt/kafka/bin/kafka-console-producer.sh --bootstrap-server localhost:9092 --topic xyz
    ```
    Edit a key field (e.g. Account) to a different valid value between runs so each run creates a distinct row. Verify DB as above.

**Cardinality sanity check:**
- After one successful run, validate expected parent/child counts derived from the sample payload and any declarative enrichment/matching rules.
- Put exact counts in the project requirements or regression test for that pipeline; do not hardcode domain-specific counts in generic training.
- Add a regression test that asserts duplicate payloads are rejected under insert-only policy.

---

## Kafka Reset Script (`integration/kafka/xyz_reset.sh`)

Generate one reset script per topic — named after the topic, lives in `integration/kafka/` (not auto-discovered).
The script resets Kafka topics and the log file only; it does **not** clear the DB.

```bash
#!/usr/bin/env bash
# integration/kafka/xyz_reset.sh — reset Kafka topics and log for the xyz pipeline.
# Run from project root: bash integration/kafka/xyz_reset.sh

set -e

# Truncate log
if [ -f logs/als.log ]; then > logs/als.log && echo "Log cleared."; fi

# Delete + recreate topics so consumer offsets start fresh
docker exec broker1 /opt/kafka/bin/kafka-topics.sh --bootstrap-server localhost:9092 --topic xyz --delete --if-exists || true
docker exec broker1 /opt/kafka/bin/kafka-topics.sh --bootstrap-server localhost:9092 --topic xyz_processed --delete --if-exists || true
sleep 2
docker exec broker1 /opt/kafka/bin/kafka-topics.sh --create --bootstrap-server localhost:9092 --replication-factor 1 --partitions 1 --topic xyz
docker exec broker1 /opt/kafka/bin/kafka-topics.sh --create --bootstrap-server localhost:9092 --replication-factor 1 --partitions 1 --topic xyz_processed
echo "Kafka topics reset."

# ---------------------------------------------------------------------------
# Useful inspection commands (run manually):
# ---------------------------------------------------------------------------
# List all topics:
#   docker exec broker1 /opt/kafka/bin/kafka-topics.sh --bootstrap-server localhost:9092 --list
#
# Read topic contents from the beginning:
#   docker exec broker1 /opt/kafka/bin/kafka-console-consumer.sh \
#     --bootstrap-server localhost:9092 --topic xyz --from-beginning --group fresh-group-1
#
#   NOTE: increment the group number (fresh-group-1, fresh-group-2, ...) each time —
#   Kafka tracks the last-read offset per consumer group, so reusing a group name
#   skips messages already seen by that group.
#
#   Clone/rename guidance:
#   For copied projects, set KAFKA_CONSUMER_GROUP in config/default.env to a
#   project-unique name. Reusing an inherited group across multiple running
#   services can trigger rebalancing and inconsistent test results.
#
#   Runtime stability check:
#   Keep exactly one API server process during consume tests. Multiple app
#   instances in the same group may fight over partitions.
#
# Re-run without full reset:
#   Edit docs/sample_data/sample_xyz.json and change a key field (e.g. AccountId)
#   to a different valid value before each publish so each run creates a distinct row.
```

---

## Minimal Generation Prompt

```
Create an EAI consume pipeline for Kafka topic `xyz` (XML format).
Target tables: [list model classes from models.py].
If no sample message exists, generate one from the schema.

Generate:
1. XyzMessage blob table (add to database/db.sqlite and models.py)
2. integration/kafka/kafka_subscribe_discovery/xyz.py — topic handler file with:
   - module docstring containing: (a) Basic Design — numbered list of files + what each one does (see example below), (b) the creating prompt used to generate it, (c) debug test instructions and test file locations, (d) how to enable Kafka via config/default.env including `bash integration/kafka/xyz_reset.sh` to reset topics + log between runs
   - Basic Design example:
     ```
     Basic Design:
       1. integration/kafka/kafka_subscribe_discovery/xyz.py  - xyz
            reads message, inserts raw payload into XyzMessage blob (Tx 1)
       2. logic/logic_discovery/xyz_consume.py
            insert → publishes payload to topic: xyz_processed
       3. integration/kafka/kafka_subscribe_discovery/xyz.py  - xyz_processed
            parses payload → domain rows (lookups + LogicBank rules) (Tx 2)
       4. api/api_discovery/xyz_kafka_consume_debug.py
            /consume_debug/xyz bypasses Kafka, calls same parse function directly
     ```
   - `register(bus)`, XYZ_EXCEPTIONS dict, XYZ_PARENT_LOOKUPS / XYZ_CHILD_LOOKUPS / XYZ_CHILD_KEY (if any field needs name→FK resolution; see § Lookup Resolution)
   - `process_xyz_payload(payload, session, blob_id=None)` shared function
   - handlers for topics `xyz` and `xyz_processed` (consumer 2 calls `process_xyz_payload`)
3. logic/logic_discovery/xyz_consume.py — row_event bridge; only publishes to Kafka, no inline parse (see § Local Debug Mode)
4. integration/XyzMapper.py — 3-tier mapper (by-name + FIELD_EXCEPTIONS stub + custom callback stub)
5. docs/sample_data/sample_xyz.xml — minimal sample message
6. api/api_discovery/xyz_kafka_consume_debug.py — one file per topic, auto-discovered by api_discovery; calls `process_xyz_payload()` directly (env-var gated, no Kafka required)
7. ui/admin/admin.yaml — add XyzMessage section; set payload field as `type: textarea`
8. integration/kafka/xyz_reset.sh — bash script to delete+recreate Kafka topics and truncate log (see § Kafka Reset Script)

Example admin.yaml entry for the blob table:
```yaml
  XyzMessage:
    attributes:
    - label: ' id*'
      name: id
      search: true
      sort: true
    - name: received_at
      type: DATETIME
    - name: is_processed
    - name: payload
      type: textarea
    type: XyzMessage
    user_key: id
```

---

## Multi-Table XML: TAG_ROUTING from Sample Message

For XML payloads with multiple section tags mapping to different tables:
- If **sample XML exists**: read section tag local-names, match to model classes by name,
  generate `TAG_ROUTING` automatically
- If **no sample XML**: generate sample first (see above), then generate `TAG_ROUTING`
- Child rows with no FK to parent go in `extras` list (returned separately from `parse()`)
