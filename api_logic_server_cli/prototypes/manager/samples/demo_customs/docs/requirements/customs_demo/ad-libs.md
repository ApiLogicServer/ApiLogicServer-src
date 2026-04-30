# Ad-Libs Report — customs_demo

**3 items need your review. 6 FYIs — standard patterns, no action needed.**

---

## 🔴 Review Required

| Location | Issue | Action |
|---|---|---|
| `logic/logic_discovery/clvs_eligibility.py` | "Authorized CLVS courier" mapped to `service_type_cd == '04'` — spec names the condition but not the field/value | Confirm `service_type_cd = '04'` is the correct CLVS service-type identifier, or replace with the correct field/value |
| `logic/logic_discovery/clvs_eligibility.py` | "CBSA-designated customs office" mapped to `dest_loc_cntry_cd == 'CA'` — spec names the condition but not the field/value | Confirm `dest_loc_cntry_cd = 'CA'` captures this condition, or replace with a lookup against a designated-offices table |
| `logic/logic_discovery/shipment_matching.py` | "High confidence columns" from `CcpCustomer → ShipmentParty` were inferred from column name matching; no explicit mapping table was provided | Review the field mapping in `_match_importer()` and confirm or adjust which CcpCustomer columns are copied to ShipmentParty |

---

## 🟡 FYI

- `integration/IsdcMapper.py` — Tier 1 auto-mapping handles ~90% of fields; `ISDC_EXCEPTIONS` dict is empty (no remaps needed for standard CIMCorp field names)
- `integration/kafka/kafka_subscribe_discovery/isdc.py` — 2-message design applied (blob Tx 1 → row_event publishes → parse Tx 2); standard pattern per eai_subscribe.md
- `integration/kafka/kafka_subscribe_discovery/isdc.py` — replace-on-duplicate policy: `session.delete(existing)` + `session.flush()` before reinsert; relies on ORM `cascade="all, delete"` set on Shipment relationships
- `logic/logic_discovery/isdc_consume.py` — `is_processed` guard added to row-event bridge to prevent spurious re-publish on the debug path (would crash Consumer 2 on UNIQUE constraint)
- `integration/kafka/kafka_subscribe_discovery/isdc.py` — SOURCE-PK normalization: `PARTY_OID_NBR == 0` → `None`; both consignee and shipper carry sentinel `0` in the reference payload
- `logic/logic_discovery/clvs_eligibility.py` — `Rule.count` used for `prohibited_commodity_count` (not `session.query`) so the count re-fires reactively on any `ShipmentCommodity.is_prohibited` change; parent ETL flag `dang_goods_cd` was intentionally not used (stale snapshot, not maintained by LogicBank)
