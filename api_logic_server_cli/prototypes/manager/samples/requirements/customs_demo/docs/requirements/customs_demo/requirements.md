## Project Creation — Prompt Sequence

The following is a reproducible step-by-step prompt sequence to recreate this project from scratch.
Each step is a copy-pasteable prompt with a verification checkpoint before proceeding.


### Step 1 — Create project and load schema

Already done, by:

```bash
# A - Create the project
genai-logic create  --project_name=customs_demo --db_url=sqlite:///samples/requirements/customs_demo/database/customs.sqlite

# B - in created project, get and implement the requirements
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

# E - ask Copilot to create the system
implement req docs/requirements/customs_demo

```


---

### Step 2 — Subscribe to Kafka and persist shipments

```
Read `docs/training/eai_subscribe.md`, then:

Subscribe to Kafka topic `isdc`. Each message is a CIMCorp shipment XML.

Parse and persist to the database using the field mappings in
`message_formats/Classify_Entity_Details.csv`.

Use `message_formats/MDE-CDV-HVS-WR-Rev260328.xml` as the reference message.

Duplicate replay behavior (required for this project):
- Match existing shipments by `LOCAL_SHIPMENT_OID_NBR` (`Shipment.local_shipment_oid_nbr`).
- If a duplicate key is found, replace the existing shipment graph in Tx 2:
    parse first, then replace the prior shipment graph and insert parsed rows.
    Implementation is not prescribed; behavior must match the verification checks below.
- Keep this behavior configurable via env policy (`fail|replace`), default `replace` for this project.

Important mapping note (prevent PK collisions):
- In this payload, party OID fields may carry placeholder value `0` for multiple rows.
- If mapped to local primary-key columns (e.g. `ShipmentParty.shipment_party_oid_nbr`),
  normalize placeholder IDs to `None` so DB autoincrement assigns unique PK values.
```

**Verify:** `F5`, then:
```bash
curl 'http://localhost:5656/consume_debug/isdc?file=docs/requirements/customs_demo/message_formats/MDE-CDV-HVS-WR-Rev260328.xml'
```
Response should show `"success": true` with `awb_nbr`, `pieces`, `parties`, `commodities`. Check Admin UI — a ShipmentXml row and a Shipment row with children should appear.

Then run the automated test gate (server must be running on port 5656):
```bash
bash docs/requirements/customs_demo/test_gate.sh
```

Behavioral acceptance checks (must pass):
- Repeat the same Step 2 call twice using the same XML payload.
- Domain graph counts remain stable on replay (Shipment/Piece/ShipmentParty/ShipmentCommodity do not increase).
- Blob/audit ingest count increases as expected (`shipment_xml` increments).
- No orphans remain after replay or after deleting the parent Shipment through API/Admin UI.

---

### Step 3 — Phase 2: Importer matching

```
Logic discovery: Shipment matching (Phase 2).

Create `logic/logic_discovery/shipment_matching.py`.

On Shipment insert, look up the matching CcpCustomer using:
    Shipment.trprt_bill_to_acct_nbr == CcpCustomer.duty_bill_to_acct_nbr

If no match: log a warning, do nothing.
If match found: create a ShipmentParty row, matching high confidence columns
from CcpCustomer to ShipmentParty.
Use Rule.row_event (not early_row_event) — fires before_flush so the new
ShipmentParty writes atomically with the parent Shipment.
```

**Required: seed `CcpCustomer` data before verifying.** Add at least one row via the Admin UI (or a SQL INSERT) with `duty_bill_to_acct_nbr` matching the `trprt_bill_to_acct_nbr` value in your test XML.

**Verify:** Re-run the Step 2 curl. A ShipmentParty with `shipment_party_type_cd="I"` should appear in Admin UI.

---

### Step 4 — Live Kafka end-to-end test

**Required: set Kafka env vars in `config/default.env`:**
```
KAFKA_SERVER = localhost:9092
KAFKA_CONSUMER_GROUP = customs_demo-group1
```

> Without these the Kafka consumer will not activate.
> If this project was cloned or renamed, use a fresh project-unique group value instead of reusing an inherited one.

**Start Kafka, then reset and send:**
```bash
docker compose -f integration/kafka/dockercompose_start_kafka.yml up -d

# F5 to start the server

sh integration/kafka/isdc_reset.sh

python test/send_isdc.py
```

**Runtime stability checks before declaring failure:**
- Keep exactly one API server process running during the test.
- Reset Kafka topics/log between reruns with `sh integration/kafka/isdc_reset.sh`.
- If the topic appears idle, inspect consumer-group assignment before changing code.
- For replace-policy reruns, repeated same-key messages should keep domain counts stable.
- To start from a clean baseline, clear domain/blob tables:
    `sh integration/kafka/isdc_reset_db.sh`

Release gate (required):
- If any behavioral acceptance check fails, do not refactor for style/structure.
- Fix only to restore required behavior, then rerun checks.

> **`test/send_isdc.py` is generated automatically by Step 2** — `eai_subscribe.md` artifact #9.

**Verify:** Check Admin UI — ShipmentXml row, Shipment with children, and ShipmentParty with `shipment_party_type_cd="I"` should all appear without any curl.

Then run the automated test gate with Kafka enabled:
```bash
KAFKA_PHASE_REQUIRED=true bash docs/requirements/customs_demo/test_gate.sh
```
