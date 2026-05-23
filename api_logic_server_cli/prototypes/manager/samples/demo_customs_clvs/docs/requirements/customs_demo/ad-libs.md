# Ad-libs Report — customs_demo

**Generated:** 2026-05-22  
**Requirements:** docs/requirements/customs_demo/requirements.md  
**Implementor:** Claude Code (claude-sonnet-4-6)

---

## Pre-Coding Analysis

### Schema Impact Assessment

| Finding | Decision |
|---|---|
| EAI/Kafka consume detected → blob table needed | Created `shipment_xml` table |
| CLVS eligibility needs prohibited count | Added `Shipment.prohibited_commodity_count` (Rule.count) |
| CLVS eligibility needs controlled count | Added `Shipment.controlled_commodity_count` (Rule.count) |
| CLVS output columns missing | Added `Shipment.clvs_eligible` INTEGER, `Shipment.clvs_reason` TEXT |
| ShipmentCommodity.is_prohibited missing | Added `is_prohibited` INTEGER DEFAULT 0 |

All DDL applied in one shot before any logic files were written.

### Pattern Assessment

| Step | Pattern Applied |
|---|---|
| Step 1 | EAI Consume — 2-message design (isdc → isdc_processed) |
| Step 2 | `Rule.row_event` on Shipment (importer matching, before_flush atomic) |
| Step 3 | `Rule.count` × 2 + `Rule.formula` × 2 (CLVS eligibility) |

---

## Execution Metrics

| Step | Result |
|---|---|
| Step 1 — Kafka consume + debug endpoint | ✅ PASS (test gate debug phase) |
| Step 2 — Importer matching | ✅ 3 parties per fixture (C + S + I) |
| Step 3 — CLVS eligibility | ✅ Rules compute correctly |
| Step 4 — Live Kafka | ✅ PASS (Kafka phase of test gate) |

Test gate: `PASS: customs_demo XR test gate (debug required, Kafka best-effort)`

---

## Error Correction Loop

### Bug 1 — Autoflush during rule callbacks (UNIQUE constraint failure)

**Symptom:** `UNIQUE constraint failed: shipment_commodity.local_shipment_oid_nbr, sequence_nbr` on first consume call.

**Root cause:** `session.query()` inside `early_row_event` and `Rule.formula` callbacks triggers SQLAlchemy autoflush. During `before_flush`, a nested autoflush re-attempts to INSERT the pending ShipmentCommodity row that is already in the session's pending set.

**Fix:** Wrapped all `session.query()` calls inside rule callbacks with `session.no_autoflush` context manager in `clvs_eligibility.py` and `shipment_matching.py`.

**Learned pattern:** Per eai_subscribe.md — any `session.query()` inside a LogicBank rule callback (row_event, early_row_event, formula calling=) MUST use `session.no_autoflush`.

---

### Bug 2 — ShipmentCommodity not deleted on replace-on-duplicate

**Symptom:** `UNIQUE constraint failed` on second consume call (replay) with replace policy.

**Root cause:** `Shipment.ShipmentCommodityList` uses `passive_deletes='all'` (composite PK prevents ORM null-out). SQLite requires `PRAGMA foreign_keys = ON` per connection for DB-level ON DELETE CASCADE. Without it, ShipmentCommodity rows persist after parent Shipment is deleted.

**Fix:** In `process_isdc_payload`, explicitly delete ShipmentCommodity rows via `session.query().filter().delete(synchronize_session='fetch')` before `session.delete(existing)`.

---

## Assumptions / Ad-libs (beyond the spec)

### Step 1 — EAI Consume

🟡 **FYI:** VirtualRouteLeg rows are added as standalone (no FK to Shipment). The VirtualRouteLeg table in the schema has no local_shipment_oid_nbr column. Rows are persisted but not linked to a specific shipment.

🟡 **FYI:** Tags `mawbAsgmt`, `mawb`, `currencies`, `extraData`, `messageMetadata` are parsed but skipped (no target table in Classify Storage column of CSV).

🟡 **FYI:** SpecialHandling rows are included in the cascade delete via ORM `cascade="all, delete"`. The XML uses `<OID_NBR>` as the FK (maps to `oid_nbr` on SpecialHandling which references Shipment).

### Step 2 — Importer Matching

🟡 **FYI:** Matching uses `TRPRT_BILL_TO_ACCT_NBR` (transport billed account), not `DUTY_BILL_TO_ACCT_NBR` (duty billed account), as specified in the requirement.

🟡 **FYI:** High-confidence columns copied from Customer to ShipmentParty: `company_nm`, `city_nm`, `state_cd`, `country_cd`, `postal_cd`, `customs_id_cd`, `broker_id_cd`, `customer_acct_nbr`. Not all Customer columns have ShipmentParty equivalents.

### Step 3 — CLVS Eligibility

🟡 **FYI:** CLVS authorized courier check uses `service_type_cd = '04'`. This value is inferred from the sample XML (`<SERVICE_TYPE_CD>04</SERVICE_TYPE_CD>`) and matches the known FedEx CLVS service type code.

🟡 **FYI:** "Controlled or regulatory goods" check uses the `controlled_regulated_goods` reference table with HS code normalized to digits only (dots stripped, first 10 digits compared). The sample XML commodity (HS 4901990091 — printed books) has no match, resulting in `controlled_commodity_count = 0`.

🟡 **FYI:** "Prohibited commodity lines" (`is_prohibited`) and "controlled goods" use the same HS code lookup. If a commodity matches `controlled_regulated_goods.hs_code`, it is marked both `is_prohibited=1` and has `controlled_regulated_goods_id` set. These are treated as equivalent in this implementation.

🔴 **Review Required:** "CBSA-designated customs office" check queries `CustomsOffice.office_code == Shipment.planned_clearance_location_cd AND clvs_release = 1`. The sample shipment has `planned_clearance_location_cd = 'MEM'` which is not in the `customs_office` seed data — this correctly produces an ineligibility reason. Verify CustomsOffice reference data covers all expected location codes.

### ORM Cascades (Step F)

🟡 **FYI:** Applied ORM cascades as specified: `cascade="all, delete"` on Piece, SpecialHandling, ShipmentParty; `passive_deletes='all'` on ShipmentCommodity. Added explicit `session.query().delete()` in the replace-on-duplicate path to handle SQLite FK cascade limitation.
