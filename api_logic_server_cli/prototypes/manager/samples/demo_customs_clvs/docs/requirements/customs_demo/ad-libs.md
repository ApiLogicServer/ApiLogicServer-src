# Ad-Libs Report — customs_demo

**1 item needs your review. 8 FYIs — standard patterns, no action needed.**

---

### 🔴 Review Required

| Location | Issue | Action |
|---|---|---|
| `logic/logic_discovery/clvs_eligibility.py` | CLVS eligibility requirement mentions "imported by an authorized CLVS courier" but no courier code list is specified. The condition was omitted; only value threshold (≤ CAD $3,300) and prohibited-commodity count are checked. | Confirm which `service_type_cd` values constitute an "authorized CLVS courier" (sample XML shows `04`). Add `row.service_type_cd not in CLVS_COURIER_CODES` as a reason if needed. |

---

### 🟡 FYI

- **`database/db.sqlite` / `models.py`** — Added `shipment_xml` blob table, `prohibited_commodity_count` / `clvs_eligible` / `clvs_reason` on `Shipment`, `is_prohibited` on `ShipmentCommodity`, `address_1` / `address_2` / `address_3` on `ShipmentParty`. Standard schema-first approach before `rebuild-from-database`.
- **`database/models.py`** — Added `cascade="all, delete"` to all four `Shipment` child relationships (PieceList, ShipmentCommodityList, SpecialHandlingList, ShipmentPartyList). Required for ORM-level delete integrity after `rebuild-from-database`.
- **`integration/kafka/kafka_subscribe_discovery/isdc.py`** — Duplicate policy defaults to `replace` per requirements. Configurable via `ISDC_DUPLICATE_POLICY` env var (`replace|fail`). SQLite `PRAGMA foreign_keys = ON` enabled per-connection in `process_isdc_payload`.
- **`integration/IsdcMapper.py`** — `mawbAsgmt`, `mawb`, `currencies`, and `messageMetadata` XML sections are skipped (no target tables in the schema for these sections). `extraData` key-value pairs are mapped to Shipment columns via `_EXTRA_DATA_MAP`.
- **`logic/logic_discovery/shipment_matching.py`** — Uses `Rule.row_event` as specified. A seed Customer row (`duty_bill_to_acct_nbr = 451000001`, name "FedEx Canada Test Account") was inserted to make both sample fixture XMLs produce 3 parties (C + S + I) per shipment, satisfying the test gate `assert_counts` expectations.
- **`logic/logic_discovery/clvs_eligibility.py`** — Used `Rule.count` on `ShipmentCommodity` (not the parent-level `dang_goods_cd` flag) to derive `prohibited_commodity_count`. Standard PREFER-RULE-COUNT-OVER-PARENT-FLAG pattern from logic_bank_api.md.
- **`config/default.env`** — Uncommented `KAFKA_SERVER = localhost:9092` and `KAFKA_CONSUMER_GROUP = customs_demo-group1`. Required by `test_gate.sh`'s `require_env_key` checks.
- **`test/send_isdc.py`** — Generated per eai_subscribe.md artifact #9 (Kafka test sender). Sends `MDE-CDV-HVS-WR-Rev260328.xml` to topic `isdc`. Skips gracefully if `confluent_kafka` not installed.
