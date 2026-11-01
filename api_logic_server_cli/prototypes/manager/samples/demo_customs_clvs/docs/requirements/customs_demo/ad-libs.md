## Ad-Libs Report
**9 items need your review. 9 FYIs — standard patterns, no action needed.**

---

## Walkthrough

1. **Basic data model** — customs.sqlite already modelled Shipment, Piece, ShipmentParty, ShipmentCommodity, Customer, CustomsOffice, ControlledRegulatedGood (all seeded lookups); nothing inferred.
2. **Derived/predicted schema additions** — constants → `sys_config.clvs_lvs_threshold_cad` (3300) and `clvs_service_type_cd` ('04'); FK `shipment.customs_office_id` (+ snapshot `customs_office_clvs_release`); `shipment_commodity.is_prohibited`; derived `shipment.prohibited_commodity_count`, `controlled_commodity_count`, `clvs_reason`, `clvs_eligible`; EAI blob table `shipment_xml`. Allocate junctions: none. Request Pattern: none.
3. **Create db** — DDL via sqlite3 + `rebuild-from-database` (13 tables).
4. **Run impl-req** — 2 early events, 1 row event, 1 after-flush event, 1 copy, 2 count, 2 formula (clvs_reason via `calling=`, clvs_eligible as a one-line expression over it); Kafka 2-message subscribe on topic `isdc`.
5. **Test data / testing** — no seed script needed (reference data shipped in the database; scenarios build unique shipments from the reference XML); 22 Behave scenarios.

<details markdown>
<summary>Full diagnostic detail (DDL change list, rule plan, rejected alternatives, replay log)</summary>

### 🟢 Diagnostic Appendix

#### Pre-Coding Analysis
*(written before any code — both phases completed in order)*

**Phase 1 — Schema Impact Assessment**
Files read: `requirements.md` (all steps), `message_formats/*` (reference XML, mapping CSV), `database/models.py`

| Step | Signal |
|---|---|
| Step 1 — Subscribe to Kafka and persist shipments | EAI detected → blob table `shipment_xml`; mapper from the CSV; duplicate policy |
| Step 2 — Importer matching | row_event side effect (lookup + child insert), no schema change |
| Step 3 — CVLS Eligibility | Rule.count over children (prohibited, controlled), FK to customs_office, constants → SysConfig |
| Step 4 — Live Kafka end-to-end test | config + reset/publisher scripts |

DDL change list *(run once before any coding)*:

| Table | Change | Reason |
|---|---|---|
| shipment_xml | CREATE TABLE | Step 1 — EAI blob table |
| shipment | ADD customs_office_id INTEGER REFERENCES customs_office(id) | Step 3 — "CBSA-designated customs office" is a lookup (FK, set by early event) |
| shipment | ADD customs_office_clvs_release INTEGER | Step 3 — Rule.copy from CustomsOffice.clvs_release |
| shipment | ADD prohibited_commodity_count INTEGER | Step 3 — Rule.count where= clause |
| shipment | ADD controlled_commodity_count INTEGER | Step 3 — Rule.count where= clause |
| shipment | ADD clvs_reason TEXT | Step 3 — Rule.formula output |
| shipment | ADD clvs_eligible INTEGER | Step 3 — Rule.formula output |
| shipment_commodity | ADD is_prohibited INTEGER | Step 3 — named in the requirement; read by Rule.count where= |
| sys_config | ADD clvs_lvs_threshold_cad, clvs_service_type_cd | Step 3 — constants (3300, '04') |

**Phase 2 — CE / Pattern Assessment**
Files read: `eai_subscribe.md`, `logic_bank_api.md`, `logic_bank_patterns.md` (not opened; the API file and implement_requirements.md covered the rule choices), `implement_requirements.md`, `testing.md`

| Step | Rule Plan |
|---|---|
| Step 1 | 2-message EAI, 9 artifacts; `Rule.after_flush_row_event(ShipmentXml)` bridge |
| Step 2 | `Rule.row_event(Shipment)` |
| Step 3 | `Rule.early_row_event` ×2 (office FK, controlled-goods FK), `Rule.copy`, `Rule.count` ×2, `Rule.formula` ×2 |

Anti-patterns confirmed clear:
- [x] No parent flag where Rule.count on child table is correct (`dang_goods_cd`, `oga_shipment_flg` are not used)
- [x] No `as_expression=lambda row: my_func(row)` — `calling=` used for the multi-line formula
- [x] No `session.query()` inside a formula (SysConfig.current and the reference-table lookups are in events / the documented accessor)
- [x] EAI: mapper returns plain model rows; 2-message design; `is_processed` guard in the bridge

**Implementation Plan**:

| Step | What was planned |
|---|---|
| 1 | DDL + rebuild-from-database |
| 2 | IsdcMapper.py, isdc.py (2 consumers + shared process function) |
| 3 | isdc_consume.py bridge, debug/reset API, reset scripts, send_isdc.py |
| 4 | clvs_eligibility.py, shipment_matching.py |
| 5 | Verify: simulated, then live |

---

#### Execution Metrics

| Metric | Value |
|---|---|
| Strategy Used | Domain graph persisted by a mapper; eligibility as count + two formulas; matching as a row_event |
| CE Files Loaded | project `.github/copilot-instructions.md` (3.57), `docs/training/logic_bank_api.md`, `implement_requirements.md`, `eai_subscribe.md`, `testing.md` |
| Schema Read First | Yes — schema and sample XML read before any mapper or logic |
| Sample Data Read | Yes — `message_formats/*` read before the mapper |
| Subagent Used | No — single pass |
| Self-Verification | Yes — server started, simulated and live sends checked, `shipment` rows read back |
| Lightweight Checks Used | Yes — curl + sqlite3 per phase |
| Gate Test Run Count | `test_gate.sh`: 3 (as supplied: failed on timing; patched copy: passed; updated gate: passed); Behave: 3 runs |
| Gate Test Purpose | Final verification (the first run diagnosed the gate, not the code) |
| Error Correction Loops | 1 |

**Error Correction Loops**:

```
Loop 1:
  Symptom:   Behave "Deleting the shipment leaves no orphans" failed: DELETE /api/Shipment/<id> answered 500
             ("tried to blank-out primary key column 'shipment_commodity.local_shipment_oid_nbr'")
  Diagnosis: read the Assertion Failed line in logs/behave.log
  Fix:       delete cascade on Shipment's four child relationships (database/customize_models.py)
  Time:      ~1 min
  Root cause type: missing read (the requirement's "no orphans after deleting the parent" check was not tried before the tests)
```

---

### 🔴 Review Required
| Location | Issue | Action |
|---|---|---|
| `logic/logic_discovery/clvs_eligibility.py:54` | "authorized CLVS courier" has no table in the database. Interpreted as `Shipment.service_type_cd` equal to `sys_config.clvs_service_type_cd` ('04', the value in every sample message). | Confirm the code, or tell me where the list of authorized couriers lives. |
| `logic/logic_discovery/clvs_eligibility.py:56` | "estimated value for duty" mapped to `local_customs_value_amt` (the CAD value); a missing value counts as over the threshold ("value over threshold"). Threshold 3300 is `sys_config.clvs_lvs_threshold_cad`. | Confirm the column, and the treatment of a missing value. |
| `logic/logic_discovery/clvs_eligibility.py:71` | `ShipmentCommodity.is_prohibited` is only counted. Nothing sets it: not the Kafka message, not a lookup. Messages arriving through Kafka therefore never carry a prohibited line; it is set only through the API / Admin UI. | Say how a line becomes prohibited (a rule table, a message field). |
| `logic/logic_discovery/clvs_eligibility.py:33-44` | Controlled-goods lookup: a `controlled_regulated_goods.hs_code` (8 digits, dotted) matches when it is a prefix of the first ten digits of the commodity's tariff number (dots removed). A tariff number with fewer than 8 digits never matches. | Confirm the prefix rule. |
| `logic/logic_discovery/clvs_eligibility.py:23-30` | "CBSA-designated customs office" resolved from `Shipment.planned_clearance_location_cd` = `customs_office.office_code`. An unknown code (the demo samples use `MEM`) is "office not designated". The message also carries other location fields (`final_import_clearance_loc_cd`, `dest_location_cd`). | Confirm which field holds the release office. |
| `logic/logic_discovery/shipment_matching.py:38-42` | "High confidence columns" chosen: company_nm←name, city_nm←city, state_cd←state, postal_cd←postal, country_cd←country, customer_acct_nbr←duty_bill_to_acct_nbr, contact_phone_nbr←phone_nbr, business_nbr←business_nbr, broker_id_cd←broker_cd. Customer address lines and GST registration have no ShipmentParty column. | Confirm the column list. |
| `integration/kafka/kafka_subscribe_discovery/isdc.py:48-67` | Replace policy: the old graph (shipment, pieces, parties, commodities, special handling) is deleted and flushed, then the new rows are inserted, all in Tx 2; the env switch name `ISDC_DUPLICATE_POLICY` (`fail` or `replace`, default `replace`) is mine. | Confirm the switch name; confirm `fail` should leave the blob unprocessed with `error_text`. |
| `integration/IsdcMapper.py:14-20` | Only shipment, consignee/shipper, piece and commodities are stored (the CSV's "Classify Storage - USE" columns). Not stored: `mawbAsgmt`, `mawb`, `currencies`, `specialHandlingCodes`, `virtualRouteLegs` (the CSV says "just store", but the table has no link to a shipment, so a replay would duplicate it), `extraData`. | Say which of these must be kept. |

| `logic/logic_discovery/clvs_eligibility.py:49` | **Found on re-read, not requested.** `_clvs_reason` reads the threshold and the courier code through `SysConfig.current()`. That query is invisible to the rule engine: changing `sys_config` does not re-evaluate existing shipments. The project guide's preferred shape is `Rule.copy` of each constant onto `shipment` (FK to `sys_config`), which is tracked. Kept the simpler form for the demo. | Decide: keep (constants rarely change) or switch to `Rule.copy`. The vital-signs check scores this -3. |

---

### 🟡 FYI
- `logic/logic_discovery/clvs_eligibility.py:74` — `clvs_eligible` is a one-line expression over `clvs_reason` (blank = eligible), so the two cannot disagree.
- `logic/logic_discovery/clvs_eligibility.py:70` — `customs_office_clvs_release` is a snapshot copy of the office flag (Rule.copy): a later change to a customs office does not re-evaluate existing shipments.
- `logic/logic_discovery/clvs_eligibility.py:52-64` — reasons are short fixed phrases: "courier not authorized", "value over threshold", "prohibited goods", "controlled goods", "office not designated", joined by ", " in that order.
- `database/customize_models.py` — deleting a Shipment deletes its pieces, parties, commodities and special handling rows (needed because the commodity key includes the shipment key).
- `config/default.env:34-35` — Kafka enabled for the live tests: `KAFKA_SERVER = localhost:9092`, `KAFKA_CONSUMER_GROUP = demo_customs_clvs-group1`.
- `integration/IsdcMapper.py:23-26` — party placeholder id 0 is cleared so the database assigns the key; no domain-floor constraints (for example on values) were added.
- `docs/requirements/customs_demo/message_formats/*` — sample outcomes under these rules: HVS fixtures not eligible (value 5000 over 3300 and office `MEM` is not a CBSA code); LVS-1 not eligible (controlled goods: HS 6110.20.00, cotton jerseys); LVS-2 eligible with blank reason. All three are correct rejections or acceptances, not false positives.
- `docs/requirements/customs_demo/test_gate.sh` — the supplied gate asserted counts immediately after sending, which fails when Kafka is configured because the debug endpoint is then live (asynchronous). Changed to poll (`wait_for_counts`); the gate now passes end to end with `KAFKA_PHASE_REQUIRED=true`.
- `database/db.sqlite` — 8 foreign-key columns have no covering index (7 came with `customs.sqlite`, `shipment.customs_office_id` is new). Fine at demo scale; flagged by the vital-signs check (-1 each).

</details>
