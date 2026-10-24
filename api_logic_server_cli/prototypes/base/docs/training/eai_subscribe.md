---
title: EAI Consume Pattern — Kafka + XML/JSON → DB
description: Two-message Kafka consume pattern with generic by-name XML/JSON mapper. Covers blob-row bridge, 3-tier mapping contract, local debug mode, and generated test data.
source: Generic training for ApiLogicServer projects with GenAI integration
usage: AI assistants read this when detecting Kafka consume, EAI, or XML/JSON-to-DB patterns in a user prompt
version: 1.6
date: April 4, 2026
related:
  - implement_requirements.md (Kafka outbound, row_event patterns)
  - logic_bank_patterns.md (row_event, commit_row_event)
  - logic_bank_api.md (full rule API)
changelog:
  - 1.6 (Oct 24, 2026): Found by running the pipeline against a REAL broker (the simulated tests could not):
    (1) the `_record_error_text` helper in this file's template used `safrs.DB.session` and called it "fresh" - it is
    the same session that still holds the failed Tx 2's rows, so its first query autoflushed them and raised the
    original error again; that exception then escaped the handler and FlaskKafka ended the consumer thread, so every
    later message was silently never processed. Now `EaiSubscribeMapper.record_error_text` (system code, new Session
    on the engine) is called inside its own try/except; FlaskKafka logs and continues. (2) /consume_debug moved into
    system code (`integration/system/EaiDebug.py`): the per-topic file is ~10 lines, has two modes (live through the
    broker when one answers, else simulated), a reset (purge) endpoint, a boolean env switch (`false` used to leave it
    ON: `os.getenv` returned the string "false"), and copy-paste curl commands in its docstring. (3) The bridge and
    every publish check `kafka_producer.kafka_available()` (cached): a configured-but-down broker no longer costs a 10 s
    flush per publish. (4) New "Artifact completeness check": artifacts 8 (reset script) and 9 (test publisher) were
    skipped by a no-container build because they looked container-only; the list is now a closing check.
  - 1.5 (Sep 23, 2026): Added `error_text` column to the blob table and a mandatory
    `_record_error_text()` helper, called from every consumer 2 `except` block — same
    mandatory weight as the 2-message pattern itself. Root cause: `is_processed=False`
    alone tells an operator only that a message is stuck, not why; without a text field,
    diagnosing failures meant grepping server logs and cross-referencing timestamps by
    hand (found via basic_demo_eai testing: invalid-lookup and business-rule-rejection
    failures both left blobs indistinguishable at the DB level). The helper writes in its
    own clean transaction/session scope rather than calling `session.rollback()` inline,
    per the existing § CONSUMER ROLLBACKS rule (framework relies on implicit rollbacks).
  - 1.4 (Aug 6, 2026): Added artifact #9 (test/send_xyz.py, Kafka test publisher) to the
    "Generated Artifacts" / "Minimal Generation Prompt" lists — a downstream project's
    requirements.md referenced "eai_subscribe.md artifact #9" for this file, but only 8
    artifacts were ever listed here, leaving a dangling reference. Also corrected the stale
    version header (said 1.2, changelog already at 1.3).
  - 1.3 (April 22, 2026): (a) Two "do it this way" template fixes (demo_eai rebuild caught both): Consumer 1 now sets is_processed=False explicitly; JSON mapper skeleton replaced with concrete parent+child-array pattern with child_rows.append(child_row). (b) Two high-value diagnostics: process_xyz_payload now raises TypeError immediately if parse() returns tuples instead of model rows; row-event bridge now logs when the is_processed guard fires (makes silent skip visible in logic log)
  - 1.2 (April 15, 2026): Added mandatory is_processed guard to Artifact 3 row-event bridge template; without it the debug path triggers a spurious Kafka re-publish that crashes Consumer 2 on UNIQUE constraint (bug caught by customs_demo implementation)
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
    error_text   = Column(Text, nullable=True)                 # exception message if Tx 2 failed
```

> **models.py imports**: ensure `from datetime import datetime` is at the top of models.py.
> The generated file already has it; if missing (e.g. after a rebuild), add it.

`received_at` is set on insert (Tx 1). `is_processed` flips to `True` when consumer 2
commits successfully (Tx 2). On parse failure Tx 2 rolls back — blob stays `False`,
queryable for retry: `SELECT * FROM xyz_message WHERE is_processed = 0`.

> 🚨 **`error_text` is mandatory — as mandatory as the 2-message pattern itself.**
> A failed Tx 2 must never fail *silently* onto the blob row. (It is written by `EaiSubscribeMapper.record_error_text`, system code.) `is_processed = False` alone
> tells an operator only that *something* is stuck — not why, and not whether row #17 failed
> for a different reason than row #23. Without `error_text`, diagnosing a backlog of failed
> messages means grepping server logs and cross-referencing timestamps by hand; with it, the
> failure reason is queryable alongside the blob: `SELECT id, error_text FROM xyz_message
> WHERE is_processed = 0`. See § Generated Artifacts, Consumer 2, for where this is set.

### 2. Topic handler file (`integration/kafka/kafka_subscribe_discovery/xyz.py`)

Drop this file in `kafka_subscribe_discovery/` — it is auto-discovered at server start,
no edits to `kafka_consumer.py` required. Add a 2nd consumer by adding a 2nd file.

```python
# integration/kafka/kafka_subscribe_discovery/xyz.py
import json
import logging
import safrs
from database import models
from integration.system.EaiSubscribeMapper import resolve_lookups, record_error_text   # system helper, see Consumer 2

logger = logging.getLogger('integration.kafka')

# Lookup dicts and exceptions live here, co-located with the consumer that owns them.

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
    parent_row, detail_rows = parse(payload)
    # Guard: parse() must return plain model rows, not (row, src_dict) tuples
    if detail_rows and not hasattr(detail_rows[0], '__tablename__'):
        raise TypeError(f"parse() must return list[model_instance]; got {type(detail_rows[0]).__name__} — check XyzMapper.parse() return value")
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
            blob = models.XyzMessage(payload=msg.value().decode('utf-8'), is_processed=False)
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
                logger.exception(f"xyz_processed parse error (blob_id={blob_id})")  # full traceback logged
                # 🚨 mandatory — record failure on the blob row itself, not just the log (see § error_text).
                # Call the SYSTEM helper (new Session on the engine); never write your own on safrs.DB.session:
                # that session still holds the failed Tx 2's rows, so it would raise the same error again.
                if blob_id:
                    try:
                        record_error_text(models.XyzMessage, blob_id, str(e))
                    except Exception:   # never let error-recording end the consumer
                        logger.exception(f"could not record error_text for blob_id={blob_id}")
```

### 3. Row event bridge (`logic/logic_discovery/xyz_consume.py`)

```python
def _publish_xyz(row: models.XyzMessage, old_row, logic_row: LogicRow):
    """XyzMessage event: publishes the raw blob to xyz_processed after Tx 1 commits, so
    Consumer 2 can parse it in a clean Tx 2 (2-message pattern)."""
    if not logic_row.is_inserted() or not row.payload:
        return
    if row.is_processed:
        # debug path: process_xyz_payload() already ran Tx 2 inline (blob created with is_processed=True)
        # do NOT re-publish — Consumer 2 would attempt a duplicate insert and crash on UNIQUE constraint
        logic_row.log(f"_publish_xyz: skipping re-publish — blob.id={row.id} already is_processed=True (debug path)")
        return
    import integration.kafka.kafka_producer as kafka_producer
    if not kafka_producer.kafka_available():
        # Kafka not configured, or the broker does not answer — /consume_debug simulates Tx 2 directly; nothing to do here
        logic_row.log("_publish_xyz: Kafka not configured or broker not reachable — skipping publish")
        return
    kafka_producer.producer.produce(topic='xyz_processed', key=str(row.id), value=row.payload.encode('utf-8'))
    kafka_producer.producer.flush(timeout=10)

def declare_logic():
    Rule.after_flush_row_event(on_class=models.XyzMessage, calling=_publish_xyz)
```

> 🚨 **`is_processed` guard is mandatory in the row-event bridge.**
> The debug path (`/consume_debug/xyz`) calls `process_xyz_payload()` directly and creates the blob
> with `is_processed=True` in the same Tx. Without the guard, `after_flush_row_event` fires anyway,
> publishes to `xyz_processed`, and Consumer 2 attempts a duplicate insert — crashing on a UNIQUE
> constraint. The test gate passes despite this because the crash is caught by Consumer 2's `except`
> block, but the bug is real and reproducible in production.
> The Kafka path creates the blob with `is_processed` unset (falsy), so the guard does not suppress
> legitimate publishes.

> **Do not import producer by value.**
> `from integration.kafka.kafka_producer import producer` captures a stale snapshot (often `None`
> before startup wiring finishes). Always import the module and call `kafka_producer.kafka_available()` (or read
> `kafka_producer.producer`) at call time inside the row-event function. `kafka_available()` is False without a producer and,
> with one, asks the broker at most every 30 s: a down broker then costs one short wait, not a 10 s `flush` per message.

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
# Exceptions dicts for XML topics go in the consumer file, co-located with the listener.
# For JSON topics with a dedicated mapper, define _PARENT_EXCEPTIONS / _CHILD_EXCEPTIONS
# in XyzMapper.py and use them directly (no need to pass via parse()).
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

# Child-level lookups — applied to each row in children
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
                parent_row, children = parse(payload, )
                raw = json.loads(payload)           # cheap second parse for lookup values
                resolve_lookups(parent_row, raw, XYZ_PARENT_LOOKUPS, session)
                for child_row, child_src in zip(children, raw.get(XYZ_CHILD_KEY, [])):
                    resolve_lookups(child_row, child_src, XYZ_CHILD_LOOKUPS, session)
                    parent_row.ChildList.append(child_row)  # 🚨 attach via relationship — NOT session.add(child_row); see note below
                session.add(parent_row)  # 🚨 NEVER session.merge — see note below
                if blob_id:
                    blob = session.get(models.XyzMessage, blob_id)
                    if blob:
                        blob.is_processed = True
                session.commit()
            except Exception as e:
                logger.exception(f"xyz_processed parse error (blob_id={blob_id})")  # full traceback logged
                # 🚨 mandatory — record failure on the blob row itself, not just the log (see § error_text).
                # Call the SYSTEM helper (new Session on the engine); never write your own on safrs.DB.session:
                # that session still holds the failed Tx 2's rows, so it would raise the same error again.
                if blob_id:
                    try:
                        record_error_text(models.XyzMessage, blob_id, str(e))
                    except Exception:   # never let error-recording end the consumer
                        logger.exception(f"could not record error_text for blob_id={blob_id}")
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
> populate_row(party_row, section, )
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
    """Returns (parent_row, list[model_instance]) — plain model rows, NOT (row, src_dict) tuples."""
    root = ET.fromstring(payload)
    parent = models.XyzParent()
    children = []
    for section in root:
        tag = _local(section.tag)           # strip XML namespace
        if tag not in TAG_ROUTING:
            continue
        model_class, overrides = TAG_ROUTING[tag]
        row = model_class()
        populate_row(row, section, exceptions=exceptions, overrides=overrides)
        children.append(row)   # ← plain model instance; caller zips with raw payload for lookups
    return parent, children
```

> **`parse()` return contract:** always return `(parent_row, list[model_instance])` — plain model rows,
> never `(row, src_dict)` tuples. The caller (`process_xyz_payload`) zips the children list with the
> raw payload's child array to call `resolve_lookups()` per child.

**JSON format** (flat parent dict + child array — most common case):
```python
# integration/XyzMapper.py  (JSON variant)
import json
from database import models
from integration.system.EaiSubscribeMapper import populate_row_from_dict

# Exceptions for parent-level fields — None=skip (handled by resolve_lookups or child array)
_PARENT_EXCEPTIONS = {
    "Account": None,   # name→FK resolved by resolve_lookups
    "Items":   None,   # child array — processed separately below
}

# Exceptions for child-level fields — None=skip, str=remap to model column name
_CHILD_EXCEPTIONS = {
    "Name":           None,          # name→FK resolved by resolve_lookups
    "QuantityOrdered": "quantity",   # remap to model column
}


def parse(payload: str, exceptions: dict = None) -> tuple:
    """Returns (parent_row, list[model_instance]) — plain model rows, NOT (row, src_dict) tuples."""
    data = json.loads(payload)

    parent_row = models.XyzParent()
    populate_row_from_dict(parent_row, data, exceptions=_PARENT_EXCEPTIONS)

    child_rows = []
    for item_dict in data.get('XyzChildKey', []):   # replace XyzChildKey with actual JSON key
        child_row = models.XyzChild()
        populate_row_from_dict(child_row, item_dict, exceptions=_CHILD_EXCEPTIONS)
        child_rows.append(child_row)   # ← plain model instance; caller zips for lookups

    return parent_row, child_rows
```

> **`parse()` return contract:** always return `(parent_row, dict[str, list[model_instance]])` — plain
> model rows. Never return `(row, src_dict)` tuples. The caller (`process_xyz_payload`) zips
> `child_rows` with `raw.get(XYZ_CHILD_KEY, [])` to call `resolve_lookups()` per child.

> **Exceptions stay in the mapper, not in the caller.** Define `_PARENT_EXCEPTIONS` and
> `_CHILD_EXCEPTIONS` in the mapper file, not in the consumer. The `exceptions` parameter
> on `parse()` exists for the generic XML case; for JSON with a dedicated mapper, just
> use the module-level `_*_EXCEPTIONS` dicts directly.

> **Date column values:** `populate_row()` / `populate_row_from_dict()` set column values via `setattr`.
> For `date`-typed columns the value must be a Python `datetime.date` object.
> In any custom value-conversion function, use `datetime.strptime(text, '%Y-%m-%d').date()` — not a raw ISO string.

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

## Debug endpoints: send a message, reset the queue (live Kafka or simulated)

**Do not use a standalone Python script** to feed the pipeline. Direct `session.add()` outside the Flask app
bypasses LogicBank — SQLAlchemy event listeners are only registered when the server starts. Rules will not fire.

**Do not parse inside the `row_event` bridge.** It fires during `before_flush`; rows added then miss the fresh
`before_flush` pass where LogicBank evaluates Copy and Formula rules, so those columns stay NULL.

**Use the system engine, `integration/system/EaiDebug.py`.** Generate ONE thin file per pipeline,
`api/api_discovery/xyz_kafka_consume_debug.py`; the engine does the modes, the broker check, the live publish and the
reset. The generated file holds only what is specific to the pipeline, and its docstring carries the copy-paste curl
commands (write the real file path and port, so the user can paste them as they are):

```python
# api/api_discovery/xyz_kafka_consume_debug.py
"""
Feature: <the requirement's Feature name, as in requirements.md>   <- the Scenario text follows, verbatim

API service xyz debug: test the xyz subscribe pipeline by hand or from tests, with or without a broker.
Thin file: the engine is integration/system/EaiDebug.py.  Development only: no authentication, and the reset is
destructive.  Enabled by APILOGICPROJECT_CONSUME_DEBUG = true (config/default.env); false turns both off.

Send the sample message - live through Kafka when a broker is configured and answering, else simulated (no Kafka):

    curl "http://localhost:5656/consume_debug/xyz?file=docs/sample_data/sample_xyz.json"

Force a mode (live answers 409 if Kafka is not available):

    curl "http://localhost:5656/consume_debug/xyz?file=docs/sample_data/sample_xyz.json&mode=simulated"
    curl "http://localhost:5656/consume_debug/xyz?file=docs/sample_data/sample_xyz.json&mode=live"

Live is asynchronous (the reply is the broker's acknowledgement).  See the outcome in logs/als.log, or the blob table:

    TOKEN=$(curl -s -X POST http://localhost:5656/api/auth/login -H 'Content-Type: application/json' -d '{"username":"admin","password":"p"}' | python3 -c "import sys,json; print(json.load(sys.stdin)['access_token'])")
    curl "http://localhost:5656/api/XyzMessage/?sort=-id&page%5Blimit%5D=1" -H "Authorization: Bearer $TOKEN"

Purge the messages in topics xyz and xyz_processed (the topics and consumers stay; nothing to do without a broker):

    curl -X POST "http://localhost:5656/consume_debug/xyz/reset"
"""
from integration.system.EaiDebug import register_consume_debug, register_queue_reset

SAMPLE_FILE = "docs/sample_data/sample_xyz.json"


def _simulate(payload: str, session) -> dict:
    """xyz debug: runs the live consumer's parse-and-save function directly (no Kafka); returns the outcome."""
    from integration.kafka.kafka_subscribe_discovery.xyz import process_xyz_payload
    parent_row, blob = process_xyz_payload(payload, session)
    return {"blob_id": blob.id, "parent_id": parent_row.id}


def add_service(app, api, project_dir, swagger_host: str, PORT: str, method_decorators=[]):
    """API service xyz debug: registers /consume_debug/xyz and its reset (only when debug is enabled)."""
    register_consume_debug(app, topic="xyz", simulate=_simulate, port=PORT, sample_file=SAMPLE_FILE,
                           outcome_hint="GET /api/XyzMessage/?sort=-id&page[limit]=1 (is_processed, error_text)")
    register_queue_reset(app, name="xyz", topics=["xyz", "xyz_processed"], port=PORT)
```

**What the endpoints do** (details in the `EaiDebug.py` docstring):

| Call | Behavior |
|---|---|
| `GET /consume_debug/xyz?file=...` (`mode=auto`, the default) | **Live** when a producer AND a consumer are configured (`KAFKA_SERVER`, `KAFKA_CONSUMER_GROUP`) and the broker answers: publishes the file to topic `xyz` and returns when the broker acknowledges (partition, offset), like any sender. Otherwise **simulated**. The response always has `"mode"`. |
| `...&mode=simulated` | No Kafka: runs `process_xyz_payload()` directly in one transaction (the same function Consumer 2 uses) and returns the outcome (`blob_id`, ...) or the error. |
| `...&mode=live` | Live only; `409` with the reason if Kafka is not available. |
| `POST /consume_debug/xyz/reset` | Purges the messages in the pipeline's topics (to the high watermark; the topics, consumers and offsets stay, so a running consumer is unaffected and a restart replays nothing). Without a broker: `200` and "nothing to purge". |

**Live is asynchronous.** The endpoint does not wait for Consumer 1, the bridge and Consumer 2: look at `logs/als.log`
or query the blob table (`is_processed`, `error_text`). Tests do their own short polling (see `testing.md`).

**The simulated path is not the live path.** It creates the blob already `is_processed = True` in the same transaction as the
domain rows, so a rejected message leaves NO blob; live, the blob stays with `is_processed = 0` and `error_text`.
Consumer 1, the bridge and Consumer 2 never run when simulated. Say so wherever simulated results are shown.

**Development workflow:**

*No Kafka (fastest — start here):*
1. Generate sample JSON from the schema (if none exists).
2. `APILOGICPROJECT_CONSUME_DEBUG = true` is in `config/default.env` by default.
3. Start the server: `python api_logic_server_run.py`
4. Paste the curl command from the debug file's docstring (or the one in the server log at startup).
5. Verify the DB — FK columns non-null (lookups worked), computed columns non-null (LogicBank rules fired).

*Live Kafka:*
6. Start Kafka (idempotent): `docker compose -f integration/kafka/dockercompose_start_kafka.yml up -d` (Podman: `podman compose`).
7. Set `KAFKA_SERVER` and a project-unique `KAFKA_CONSUMER_GROUP` in `config/default.env` (or as environment variables). The
   server must be (re)started AFTER Kafka is up. The default consumer settings are enough for local tests; if you set
   `APILOGICPROJECT_KAFKA_CONSUMER` yourself you own all keys (use the full form):
    ```
    KAFKA_SERVER = localhost:9092
    KAFKA_CONSUMER_GROUP = <project>-group1
    APILOGICPROJECT_KAFKA_CONSUMER = "{\"bootstrap.servers\": \"localhost:9092\", \"group.id\": \"<project>-group1\", \"auto.offset.reset\": \"earliest\", \"enable.auto.commit\": \"false\", \"session.timeout.ms\": \"6000\", \"heartbeat.interval.ms\": \"2000\"}"
    ```
    > **Why `session.timeout.ms: 6000`?** The default (45 s) means a stale consumer session from a prior server run holds
    > the partition assignment for up to 45 s after the process dies; the new consumer polls but receives nothing.
    > **Why `auto.offset.reset: earliest`?** Without it the consumer only sees messages published after it subscribes.
8. Create the topics once: `bash integration/kafka/xyz_reset.sh` (needs the broker container), or let the first publish create them.
9. Send: the same curl as above (it now goes live). Start from an empty queue with the reset endpoint, not by restarting.
10. For insert-only pipelines, clear the domain tables between repeat runs, or use fresh keys (the tests use fresh, timestamped customers).

**Cardinality sanity check:** after one successful run, validate the expected parent/child counts derived from the sample
payload and any declarative enrichment/matching rules; put the exact counts in the project's requirements or regression
test, and add a regression test that duplicate payloads are rejected under insert-only policy.

---

## Kafka Reset Script (`integration/kafka/xyz_reset.sh`)

> 🚨 **This file is mandatory — always generate it.** The live-Kafka workflow step references
> `bash integration/kafka/xyz_reset.sh` by name. If the script is missing, Kafka tests cannot
> be repeated cleanly (stale offsets + stale log contaminate subsequent runs).

Generate one reset script per topic — named after the topic, lives in `integration/kafka/`
(not auto-discovered). This location and the reset-helper convention are documented in
`integration/kafka/kafka_readme.md` — see the **Reset Helpers** section there.
The script resets Kafka topics and the log file only; it does **not** clear the DB.

```bash
#!/usr/bin/env bash
# integration/kafka/xyz_reset.sh — reset Kafka topics and log for the xyz pipeline.
# Run from project root: bash integration/kafka/xyz_reset.sh
#
# WARNING: deletes and recreates topics xyz and xyz_processed on the broker, losing their messages (and any other
#          project using the same topic names on that broker). To purge messages WITHOUT deleting the topics, use
#          the debug endpoint instead: curl -X POST http://localhost:5656/consume_debug/xyz/reset
# Broker container: BROKER_CONTAINER (default broker1); bootstrap server inside it: BROKER_BOOTSTRAP (default localhost:9092).

set -e

# Docker or Podman — whichever is installed. Same broker container either way
# (dockercompose_start_kafka.yml works unchanged under `podman compose`), so this
# script must not hardcode `docker exec` — that fails outright on a Podman-only
# machine (no `docker` binary at all, not just a different runtime under the hood).
CONTAINER_CLI=$(command -v docker >/dev/null 2>&1 && echo docker || echo podman)
BROKER_CONTAINER=${BROKER_CONTAINER:-broker1}
BROKER_BOOTSTRAP=${BROKER_BOOTSTRAP:-localhost:9092}
TOPICS="$CONTAINER_CLI exec $BROKER_CONTAINER /opt/kafka/bin/kafka-topics.sh --bootstrap-server $BROKER_BOOTSTRAP"

# Truncate log
if [ -f logs/als.log ]; then > logs/als.log && echo "Log cleared."; fi

# Delete + recreate topics so consumer offsets start fresh
$TOPICS --topic xyz --delete --if-exists || true
$TOPICS --topic xyz_processed --delete --if-exists || true
sleep 2
$TOPICS --create --replication-factor 1 --partitions 1 --topic xyz
$TOPICS --create --replication-factor 1 --partitions 1 --topic xyz_processed
echo "Kafka topics reset."

# ---------------------------------------------------------------------------
# Useful inspection commands (run manually — substitute `podman` for `docker` if
# that's what's installed):
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
1. XyzMessage blob table (add to database/db.sqlite and models.py) — including `error_text`
   (nullable text column; see § error_text — mandatory, not optional)
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
   - every consumer 2 `except` block calls `record_error_text(...)` from `integration.system.EaiSubscribeMapper`
     (system code — do NOT write your own on `safrs.DB.session`), inside its own try/except; mandatory, not optional
   - handlers for topics `xyz` and `xyz_processed` (consumer 2 calls `process_xyz_payload`)
3. logic/logic_discovery/xyz_consume.py — row_event bridge; only publishes to Kafka, no inline parse (see § Debug endpoints)
4. integration/XyzMapper.py — 3-tier mapper (by-name + FIELD_EXCEPTIONS stub + custom callback stub)
5. docs/sample_data/sample_xyz.xml — minimal sample message
6. api/api_discovery/xyz_kafka_consume_debug.py — ONE thin file per topic (see § Debug endpoints): calls `register_consume_debug` and `register_queue_reset` from `integration/system/EaiDebug.py`; its docstring carries copy-paste curl commands (send: auto / simulated / live; reset)
7. ui/admin/admin.yaml — add XyzMessage section; set payload field as `type: textarea`
8. integration/kafka/xyz_reset.sh — **required, do not skip, even when no container runtime is available** (it is just a file; it runs when a broker container exists) — bash script to delete+recreate Kafka topics and truncate log (see § Kafka Reset Script below for the template); the live-Kafka workflow references it by name
9. test/send_xyz.py — **required, do not skip, even with no broker** (pure Python; the debug endpoint's live mode is the usual way to send, this is the standalone tool) — Kafka test publisher used for the live-Kafka verification step; use
   `confluent_kafka.Producer` directly (never `subprocess` + `kafka-console-producer`, which
   sends one message per input line and mangles multi-line XML/JSON payloads — see
   § TEST PUBLISHERS above). Reads the topic name and a sample payload file, publishes one
   message, and reports delivery via a `Producer.produce(..., callback=...)` + `flush()`.

**Artifact completeness check (mandatory closing step, like the other before-you're-done scans).** Before reporting the
pipeline done, confirm each of these exists on disk — list them, do not assume. A build with no container runtime
still needs ALL of them (they are files, not containers):

| # | Artifact | Path |
|---|---|---|
| 1 | Blob table in `database/models.py` (with `received_at` set by the code that inserts, `error_text`) | `database/models.py` |
| 2 | Topic handlers (Consumer 1 + Consumer 2, `process_xyz_payload`) | `integration/kafka/kafka_subscribe_discovery/xyz.py` |
| 3 | Row-event bridge (checks `kafka_available()`) | `logic/logic_discovery/xyz_consume.py` |
| 4 | Mapper | `integration/XyzMapper.py` |
| 5 | Sample message | `docs/sample_data/` or `docs/requirements/<name>/message_formats/` |
| 6 | Debug + reset endpoints (thin file, curl docstring) | `api/api_discovery/xyz_kafka_consume_debug.py` |
| 7 | Admin UI entry for the blob table | `ui/admin/admin.yaml` |
| 8 | Reset script | `integration/kafka/xyz_reset.sh` |
| 9 | Test publisher | `test/send_xyz.py` |

Also confirm the docstring of #6 has the curl commands with the real file path and port.

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
- Child rows are returned as a flat list from `parse()` — the caller zips them with the raw payload's child array for lookup resolution.

> **CONSUMER ROLLBACKS:** NEVER call `session.rollback()` in a Kafka consumer's `except` block. The framework relies on implicit rollbacks; adding one manually masks errors and poisons the session.

> **DEBUG ENDPOINT GUARD:** the endpoints are registered only when `APILOGICPROJECT_CONSUME_DEBUG` is true / 1 / yes / on (`EaiDebug.debug_enabled()`); `false`, `0` or unset leaves them unregistered. Never test it with `if not os.getenv(...)`: that returns the string `"false"`, which is truthy, so `false` would leave the endpoint ON. They have no authentication and the reset is destructive: development and demo only; set the variable to `false` anywhere else.

> **TEST PUBLISHERS:** Test scripts that send messages to Kafka MUST use `confluent_kafka.Producer` directly. Do NOT use `subprocess.run` calling `docker exec kafka-console-producer` — it is fragile and sends one message per input line, which breaks multi-line payloads.

> **NO RE-PARSING:** Never call `ET.fromstring(payload)` or `json.loads(payload)` inside a Kafka consumer listener. All parsing must go through `XyzMapper.parse()` — the mapper is the only place parsing occurs.