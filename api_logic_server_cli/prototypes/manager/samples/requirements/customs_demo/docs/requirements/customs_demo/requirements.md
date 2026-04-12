## Project Creation — Prompt Sequence

The following is a reproducible step-by-step prompt sequence to recreate this project from scratch.
Each step is a copy-pasteable prompt with a verification checkpoint before proceeding.


### Step 1 — Create project and load schema

Already done, by:

```bash
genai-logic create  --project_name=customs_demo --db_url=sqlite:///samples/requirements/customs_demo/database/customs.sqlite

# in created project, get and implement the requirements
$ cp -r ../samples/requirements/customs_demo/. .

```


---

### Step 2 — Subscribe to Kafka and persist shipments

```
Read `docs/training/eai_subscribe.md`, then:

Subscribe to Kafka topic `isdc`. Each message is a CIMCorp shipment XML.

Parse and persist to the database using the field mappings in
`message_formats/Classify_Entity_Details.csv`.

Use `message_formats/MDE-CDV-HVS-WR-Rev260328.xml` as the reference message.
```

**Verify:** `F5`, then:
```bash
curl 'http://localhost:5656/consume_debug/isdc?file=docs/requirements/customs_demo/message_formats/MDE-CDV-HVS-WR-Rev260328.xml'
```
Response should show `"success": true` with `awb_nbr`, `pieces`, `parties`, `commodities`. Check Admin UI — a ShipmentXml row and a Shipment row with children should appear.

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

**Start Kafka, then reset and send:**
```bash
docker compose -f integration/kafka/dockercompose_start_kafka.yml up -d
# F5 to start the server

sh integration/kafka/isdc_reset.sh

python test/send_isdc.py
```

> **`test/send_isdc.py` is generated automatically by Step 2** — `eai_subscribe.md` artifact #9.

**Verify:** Check Admin UI — ShipmentXml row, Shipment with children, and ShipmentParty with `shipment_party_type_cd="I"` should all appear without any curl.
