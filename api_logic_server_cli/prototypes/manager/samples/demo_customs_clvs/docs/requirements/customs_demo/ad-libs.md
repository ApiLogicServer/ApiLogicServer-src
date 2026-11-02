## Ad-Libs Report
**10 items need your review. 8 FYIs — standard patterns, no action needed.**

---

## Walkthrough

1. **Basic data model** — customs.sqlite as given: Shipment (with Piece, ShipmentParty, ShipmentCommodity, SpecialHandling), Customer, CustomsOffice/Region, ControlledRegulatedGood/GovtDept, VirtualRouteLeg, SysConfig.
2. **Derived/predicted schema additions** — constants to `sys_config` (`clvs_threshold_cad` 3300, `clvs_courier_service_type_cd` '04'); lookup FK `shipment.customs_office_id` (+ `customs_office.location_cd` to link the message's IATA-style location to an office); `shipment_xml` blob table; derived columns on `shipment` (`controlled_item_count`, `prohibited_commodity_count`, `clvs_reason`, `clvs_eligible`, `office_clvs_release`, copies of the two constants); `shipment_commodity.is_prohibited`; `shipment_party` address/oid columns from the field-mapping CSV. No allocate; no Request Pattern.
3. **Create db** — one DDL pass + `rebuild-from-database` (13 tables).
4. **Run impl-req** — 3 copy, 2 count, 2 formula, 2 early events, 1 row event, 1 after-flush event (the Kafka bridge), plus the 2-message Kafka subscribe pipeline (`isdc` / `isdc_processed`).
5. **Test data / testing** — no seed needed (Customer and CustomsOffice are populated); 26 Behave scenarios across 4 Features, written from `test_plan.md`.

<details markdown>
<summary>Full diagnostic detail (DDL change list, rule plan, rejected alternatives, replay log)</summary>

### 🟢 Diagnostic Appendix

#### Pre-Coding Analysis

**Phase 1 — Schema Impact Assessment**
Files read: `requirements.md` (all steps), `message_formats/*` (CSV, reference XML, the three demo XMLs, LVS/HVS samples by grep), `database/models.py`

| Step | Signal |
|---|---|
| Step 1 — Subscribe to Kafka and persist shipments | EAI consume: blob table; CSV fields not in models (party address/oid columns) |
| Step 2 — Importer matching | row_event; no schema change (Customer and ShipmentParty exist) |
| Step 3 — CVLS Eligibility | per-clause FK scan: courier (no data → SysConfig), value (SysConfig threshold), prohibited lines (Rule.count on child, `is_prohibited` column missing), controlled goods (FK exists), designated office (FK missing, location code not linkable) |
| Step 4 — Live Kafka end-to-end | env vars in `config/default.env`; reset scripts; test publisher |

DDL change list:

| Table | Change | Reason |
|---|---|---|
| shipment_xml | CREATE TABLE | Step 1 — EAI blob table |
| sys_config | ADD clvs_threshold_cad, clvs_courier_service_type_cd | Step 3 — constant extraction |
| customs_office | ADD location_cd (+ seed YYZ, YMX, YUL, YCL) | Step 3 — link message location to office |
| shipment | ADD sys_config_id (FK), clvs_threshold_cad, clvs_courier_service_type_cd | Step 3 — Rule.copy |
| shipment | ADD customs_office_id (FK), office_clvs_release | Step 3 — early_row_event sets FK, Rule.copy |
| shipment | ADD controlled_item_count, prohibited_commodity_count | Step 3 — Rule.count |
| shipment | ADD clvs_reason, clvs_eligible | Step 3 — Rule.formula |
| shipment_commodity | ADD is_prohibited | Step 3 — Rule.count where= clause (set by early_row_event) |
| shipment_party | ADD address_1, address_2, address_3, oid_nbr, oid_type_cd | Step 1 — CSV Classify storage |

**Phase 2 — CE / Pattern Assessment**
Files read: `eai_subscribe.md`, `logic_bank_api.md`, `implement_requirements.md`, `testing.md`; `logic_bank_patterns.md` was NOT read.

| Step | Rule Plan |
|---|---|
| Step 1 | 2-message EAI; ShipmentXml blob + after_flush bridge; mapper; debug/reset endpoint; reset scripts; test publisher; admin.yaml entry |
| Step 2 | Rule.row_event(Shipment) |
| Step 3 | Rule.copy x3; Rule.count x2 (where=); early_row_event x2 (Shipment: office FK; ShipmentCommodity: controlled FK + is_prohibited); Rule.formula clvs_reason (calling=) then clvs_eligible (derived from clvs_reason) |

Anti-patterns confirmed clear:
- [x] No parent flag where Rule.count on child table is correct (dang_goods_cd / oga_shipment_flg unused)
- [x] No `as_expression=lambda row: my_func(row)`; `calling=` for the multi-line formula
- [x] No `session.query()` inside a formula (queries only inside early events that set FKs)
- [x] EAI: named parse() returns plain model rows, 2-message design, record_error_text from system code

**Implementation Plan**:

| Step | What was planned |
|---|---|
| 1 | One DDL pass + rebuild-from-database |
| 2 | IsdcMapper.py, isdc.py (2 consumers + shared function), isdc_consume.py bridge, debug endpoint, scripts |
| 3 | shipment_matching.py |
| 4 | clvs_eligibility.py |
| 5 | Verify subscriptions live; diagrams; tests from test_plan.md; run; report |

---

#### Execution Metrics

| Metric | Value |
|---|---|
| Strategy Used | DDL first (single pass), then mapper/consumer, then rules; simulated smoke test, then live Kafka (Podman broker) |
| CE Files Loaded | project `.github/copilot-instructions.md`, `docs/training/logic_bank_api.md`, `implement_requirements.md`, `eai_subscribe.md`, `testing.md` (partial) |
| Schema Read First | Yes — models.py and the live schema before any logic or mapper |
| Sample Data Read | Yes — CSV and XML samples before the mapper |
| Subagent Used | No — single pass |
| Self-Verification | Yes — server started, debug endpoint tested simulated and live, logs checked |
| Lightweight Checks Used | Yes — curl + sqlite3 reads + logs/als.log per phase |
| Gate Test Run Count | 1 — final verification only (the probe calls before it were diagnostic) |
| Gate Test Purpose | Final verification |
| Error Correction Loops | 4 |
| Long-Run Diagnostics | None |

**Error Correction Loops**:

```
Loop 1:
  Symptom:   "Missing Parent: shipment" when the importer ShipmentParty was inserted from the row_event
  Diagnosis: logs/als.log: the party carried only the FK value; the Shipment was not flushed yet
  Fix:       party.shipment = row (relationship) and session.add(party) before logic_row.insert(); LogicRow.insert does not add to the session
  Time:      ~2 min
  Root cause type: CE gap (the EAI doc says attach via relationship; the Importer-matching text does not)

Loop 2:
  Symptom:   replace-on-duplicate raised "Dependency rule ... tried to blank-out primary key column shipment_commodity.local_shipment_oid_nbr"
  Diagnosis: server response of the simulated replay
  Fix:       session.expire(existing) after deleting and flushing the children, before deleting the Shipment
  Time:      ~1 min
  Root cause type: CE gap (no replace pattern in eai_subscribe.md; it only documents insert-only)

Loop 3:
  Symptom:   PATCH of Shipment / ShipmentCommodity answered 500 "'Shipment' object has no attribute 'clvs_courier_service_type_cd:'"; inserts had worked
  Diagnosis: LogicBank's dependency scanner splits the function source on whitespace; `if row.a != row.b:` leaves `row.b:` as a token. Found only because an UPDATE was tried
  Fix:       assign the comparison to a local (`courier_ok = ...`) so no row.attr token ends with a colon
  Time:      ~2 min
  Root cause type: CE gap / engine sharp edge (inserts pass; the failure appears only on update)

Loop 4:
  Symptom:   deleting a Shipment through the API left Piece, ShipmentParty and SpecialHandling rows (requirement: no orphans)
  Diagnosis: sqlite3 counts after DELETE /api/Shipment/<id>; SQLite does not enforce ON DELETE CASCADE by default
  Fix:       ORM cascade ("all, delete") on the four Shipment child relationships, in database/customize_models.py
  Time:      ~2 min
  Root cause type: missing read (the acceptance check was in requirements.md; found by running it)
```

---

### 🔴 Review Required
| Location | Issue | Action |
|---|---|---|
| `logic/logic_discovery/clvs_eligibility.py:58-60` | "Authorized CLVS courier" is not defined by the data. Assumed: `Shipment.service_type_cd` equals `SysConfig.clvs_courier_service_type_cd` ('04', the value in every sample message) | Confirm which attribute identifies an authorized courier and the allowed value(s); one value only today |
| `logic/logic_discovery/clvs_eligibility.py:29-36` | The message carries IATA-style locations (YYZ) while `customs_office.office_code` is a 4-digit code. Added `customs_office.location_cd` and seeded YYZ→0700, YMX→0504, YUL→0500, YCL→0469 (the last is a non-designated office used by the tests) | Supply the real location-to-office mapping; seed data is a guess |
| `logic/logic_discovery/clvs_eligibility.py:33` | "Released at" is taken from `final_import_clearance_loc_cd`; other candidates are `planned_clearance_location_cd` and `dest_location_cd` | Confirm the column |
| `logic/logic_discovery/clvs_eligibility.py:52` | `ShipmentCommodity.is_prohibited` has no defined source. Set to 1 when the matched controlled good's `clvs_reason` contains the word "prohibited" (5 of 184 lookup rows) | Confirm the rule, or add an explicit flag to `controlled_regulated_goods` |
| `logic/logic_discovery/clvs_eligibility.py:43-50` | Controlled-goods lookup: a lookup HS code (8 digits) matches when it is the start of the first ten digits of the line's tariff number; first match wins. A prohibited line is also a controlled line, so it adds both reasons | Confirm the match semantics and whether prohibited should count as controlled |
| `logic/logic_discovery/clvs_eligibility.py:61` | "Estimated value for duty" = `Shipment.local_customs_value_amt` (CAD); not exceeding means `<=` 3300 | Confirm the column (alternatives: `customs_value_amt`, `dest_customs_value_amt`, `cad_value_amt`) |
| `logic/logic_discovery/clvs_eligibility.py:67-68` | A shipment whose release location maps to no office fails ("release office unknown"); the spec does not say | Confirm unknown means ineligible |
| `logic/logic_discovery/clvs_eligibility.py:56-71` | Wording and order of the short reasons are invented (spec: "short reasons") | Replace with the program's reason codes if they exist |
| `logic/logic_discovery/shipment_matching.py:44-56` | "High confidence" Customer columns copied to the importer party: account, name, address 1-2, city, state, country, postal, business number, phone, broker | Confirm the set (e.g. `gst_reg`, `export_country` not copied) |
| `integration/kafka/kafka_subscribe_discovery/isdc.py:78` | `VirtualRouteLeg` has no link to Shipment in the schema ("just store"), so a replayed message adds its legs again (not replaced). `mawb`, `mawbAsgmt`, `currencies` sections are not stored at all (`integration/IsdcMapper.py:59`) | Decide whether legs need a shipment key and whether currency conversion rows are required |

---

### 🟡 FYI
- `logic/logic_discovery/clvs_eligibility.py:75-78` — threshold, courier code and office release flag are `Rule.copy` snapshots (default): a later SysConfig or office change does not re-derive existing shipments
- `integration/kafka/kafka_subscribe_discovery/isdc.py:32-35` — duplicate policy read from env `ISDC_DUPLICATE_POLICY` (`fail|replace`, default `replace`); the variable name is mine
- `integration/kafka/kafka_subscribe_discovery/isdc.py:46-57` — replace deletes the prior graph (children, then shipment, flushed) and then inserts the parsed rows, in Tx 2
- `integration/IsdcMapper.py:41-44` — placeholder party OID 0 normalized to None so autoincrement assigns the key
- `integration/IsdcMapper.py:28` — `extraData` name/value pairs mapped to Shipment columns per the CSV
- `database/customize_models.py` — ORM cascade on Shipment children so a delete leaves no orphans (survives rebuild-from-database)
- `integration/kafka/isdc_reset.sh` — falls back to Podman when Docker is not available; `isdc_reset_db.sh` also clears special_handling and virtual_route_leg
- `config/default.env` — `KAFKA_SERVER=localhost:9092`, `KAFKA_CONSUMER_GROUP=demo_customs_clvs-group1` left set; the existing local `broker1` is shared, and the reset scripts recreate topics `isdc` and `isdc_processed` on it
- `ui/admin/admin.yaml` — ShipmentXml entry added by hand; `admin-merge.yaml` (new columns for the other tables) was generated and NOT swapped in

</details>
