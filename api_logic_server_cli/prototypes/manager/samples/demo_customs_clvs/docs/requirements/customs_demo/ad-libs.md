# Ad-Libs Report — customs_demo

**Created:** 2026-06-29  
**Created by:** claude-sonnet-4-6 (valjhuber@gmail.com)

---

## Pre-Coding Analysis

### Schema Impact Assessment

All DDL changes were applied in one batch before writing any logic or mapper files.

**New tables:**
- `shipment_xml` — EAI blob table for 2-message design

**New columns on existing tables:**
- `sys_config`: `clvs_lvs_threshold REAL DEFAULT 3300.0`, `clvs_service_type_cd TEXT DEFAULT '04'`
- `shipment`: `sys_config_id INTEGER FK`, `clvs_lvs_threshold REAL`, `clvs_service_type_cd TEXT`, `customs_office_id INTEGER FK (nullable)`, `clvs_eligible INTEGER DEFAULT 0`, `clvs_reason TEXT DEFAULT ''`, `controlled_item_count INTEGER DEFAULT 0`, `prohibited_item_count INTEGER DEFAULT 0`
- `shipment_commodity`: `is_controlled INTEGER DEFAULT 0`, `is_prohibited INTEGER DEFAULT 0`

**FK inventory (Step 4b):**
- `shipment.customs_office_id` → `customs_office(id)` — nullable (CLVS office assigned by early_row_event lookup)
- `shipment.sys_config_id` → `sys_config(id)` — for Rule.copy of regulatory constants

### EAI Pattern Assessment

EAI Consume present → 2-message design applied:
- Consumer 1 (`isdc`): saves raw XML blob, commits Tx 1
- `after_flush_row_event` on `ShipmentXml`: publishes `{"id": N}` to `isdc_processed`
- Consumer 2 (`isdc_processed`): calls `process_isdc_payload()`, marks blob `is_processed=1`, commits Tx 2
- `/consume_debug/isdc` debug endpoint (gated by `APILOGICPROJECT_CONSUME_DEBUG=true`)

---

## Execution Decisions (Ad-Libs)

### 🟡 FYI — `PARTY_OID_NBR=0` normalization applied to both consignee and shipper

**Why:** The XML carries `PARTY_OID_NBR=0` for both parties. If mapped to `shipment_party_oid_nbr` (the PK), both rows would collide on the same PK value 0. Normalized to `None` via `_normalize_party_oid` custom callback so DB autoincrement assigns unique PKs.

### 🟡 FYI — `is_prohibited` derived from `hazardous_material_cd` field

**Why:** Requirements distinguish "prohibited commodity lines" from "controlled/regulatory goods". The requirements specify `ShipmentCommodity.is_prohibited = 1` but do not specify its source. Interpreted as: prohibited if `hazardous_material_cd` is non-null/non-empty on the commodity row (mapped from XML `HAZARDOUS_MATERIAL_CD` by Tier 1 auto-map). The `ControlledRegulatedGoods` lookup sets `is_controlled` only.

### 🟡 FYI — customs office matched by `PLANNED_CLEARANCE_LOCATION_CD`

**Why:** Requirements say "released at a CBSA-designated customs office". The `customs_office` table uses 4-digit CBSA port codes (e.g. `0704`). The LVS test fixture has `PLANNED_CLEARANCE_LOCATION_CD=0704` which matches. The HVS fixture has `PLANNED_CLEARANCE_LOCATION_CD=MEM` (IATA 3-letter code) which does not match any CBSA code, so those shipments have `customs_office_id=NULL` and are CLVS-ineligible. This is expected behavior for high-value shipments.

### 🟡 FYI — ControlledRegulatedGoods matched by HS code prefix (first 10 significant digits)

**Why:** Requirements say "lookup using first ten digits of the harmonized tariff number". The XML carries `harmonized_tariff_nbr` with decimal separators (e.g. `4901990091`). The match uses `hs_code LIKE prefix%` where `prefix` is the first 10 digits after stripping periods. The sample HS code 4901990091 (books) does not match any controlled goods in the seed data (which starts at 93xx for firearms).

### 🟡 FYI — `Rule.copy` used for SysConfig constants (snapshot, not live propagation)

**Why:** `clvs_lvs_threshold` and `clvs_service_type_cd` are copied from `SysConfig` at insert time. If the threshold is updated in `SysConfig`, existing `Shipment` rows retain the threshold that was current at ingest time. This is the conservative default per the CE — use Rule.formula for live propagation only if explicitly required.

### 🟡 FYI — Cascade settings re-applied after every `rebuild-from-database`

**Why:** `genai-logic rebuild-from-database` regenerates `database/models.py` and overwrites ORM relationship `cascade` settings. The Step F cascade settings (`cascade="all, delete"` on PieceList/SpecialHandlingList/ShipmentPartyList and `passive_deletes='all'` on ShipmentCommodityList) must be re-applied each time rebuild-from-database is run. This is a known limitation of the rebuild workflow.

### 🟡 FYI — `passive_deletes='all'` on ShipmentCommodityList requires PRAGMA

**Why:** `ShipmentCommodity` has a composite PK where the FK is part of the PK. `cascade="all, delete"` would null the FK before delete (failing for PK columns). `passive_deletes='all'` delegates to DB-level `ON DELETE CASCADE`. SQLite only enforces FK cascades when `PRAGMA foreign_keys = ON` is set per connection — `process_isdc_payload` does this before any `session.delete(existing_shipment)`.

### 🟡 FYI — session.query used instead of relationship for customs_office lookup in formulas

**Why:** Per CE rule: after `early_row_event` sets `customs_office_id`, the `row.customs_office` SQLAlchemy relationship attribute may not reflect the FK just set (stale within same flush). The formula `_reasons()` function uses `session.query(CustomsOffice).get(row.customs_office_id)` instead.

---

## Files Created

| File | Purpose |
|------|---------|
| `integration/IsdcMapper.py` | CIMCorp XML → SQLAlchemy model graph |
| `integration/kafka/kafka_subscribe_discovery/isdc.py` | Consumer 1+2 + `process_isdc_payload` |
| `logic/logic_discovery/isdc_consume.py` | `after_flush_row_event` bridge (blob → isdc_processed) |
| `api/api_discovery/isdc_kafka_consume_debug.py` | Debug endpoint `/consume_debug/isdc` |
| `logic/logic_discovery/shipment_matching.py` | Step 2: importer party creation |
| `logic/logic_discovery/clvs_eligibility.py` | Step 3: CLVS eligibility rules |
| `ui/admin/admin.yaml` | Added ShipmentXml section |
| `test/send_isdc.py` | Kafka test publisher |
| `docs/requirements/isdc_consume/requirements.md` | Traceability anchor |
| `docs/requirements/shipment_matching/requirements.md` | Traceability anchor |
| `docs/requirements/clvs_eligibility/requirements.md` | Traceability anchor |
