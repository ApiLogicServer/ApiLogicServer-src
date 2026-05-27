# Ad-Libs Report — customs_demo requirements

Generated: 2026-05-26

## Pre-Coding Analysis

### Phase 1 — Schema Impact Assessment

EAI / Kafka consume detected → `shipment_xml` blob table needed.

CLVS eligibility (Step 3) requires derived columns on parent tables:

| Table | Column | Rule | Reason |
|---|---|---|---|
| `shipment_xml` | NEW TABLE | — | EAI blob table (2-message design) |
| `shipment` | `clvs_eligible INTEGER` | `Rule.formula` | CLVS eligibility flag |
| `shipment` | `clvs_reason TEXT` | `Rule.formula` | Comma-delimited ineligibility reasons |
| `shipment` | `prohibited_commodity_count INTEGER` | `Rule.count` | Count of is_prohibited=1 commodities |
| `shipment` | `controlled_item_count INTEGER` | `Rule.count` | Count of controlled/regulated commodities |
| `shipment` | `customs_office_id INTEGER FK` | `early_row_event` | FK to customs_office for CLVS office check |
| `shipment_commodity` | `is_prohibited INTEGER` | `Rule.formula` | 1 if controlled_regulated_goods_id IS NOT NULL |

All DDL applied before any logic files were written. One rebuild-from-database run after all DDL.

### Phase 2 — CE / Pattern Assessment

**EAI Consume (Step 1):** Two-message design implemented per `docs/training/eai_subscribe.md`. 
Topics: `isdc` (Consumer 1 blob) and `isdc_processed` (Consumer 2 parse+persist).

**Replace-on-duplicate policy:** Required explicitly by requirements. Implemented via SQL DELETE 
with `PRAGMA foreign_keys = ON` so DB CASCADE removes children atomically before new insert. 
`session.merge` was explicitly avoided per CE rules.

**CLVS rules (Step 3):** Used Rule.count for child-row conditions (prohibited/controlled commodities) 
rather than session.query() inside Rule.formula. FK columns (customs_office_id, 
controlled_regulated_goods_id) set via early_row_event — cannot use Rule.formula/copy for FKs.

---

## Execution Metrics

| Artifact | Status |
|---|---|
| `integration/IsdcMapper.py` | Created |
| `integration/kafka/kafka_subscribe_discovery/isdc.py` | Created |
| `logic/logic_discovery/isdc_consume.py` | Created |
| `api/api_discovery/isdc_kafka_consume_debug.py` | Created |
| `logic/logic_discovery/shipment_matching.py` | Created |
| `logic/logic_discovery/clvs_eligibility.py` | Created |
| `test/send_isdc.py` | Created |
| `database/models.py` | Step F cascade changes applied post-rebuild |
| `database/customize_models.py` | Added SQLite FK PRAGMA event listener |
| `config/default.env` | KAFKA_SERVER + KAFKA_CONSUMER_GROUP uncommented |
| `ui/admin/admin.yaml` | ShipmentXml section added |

Test gate result: **PASS** (debug + Kafka phases)

---

## Decisions Beyond the Spec (🔴 = review required, 🟡 = FYI)

| # | Severity | Decision | Reason |
|---|---|---|---|
| 1 | 🟡 | `is_prohibited = 1` iff `controlled_regulated_goods_id IS NOT NULL` | Requirements specify both "prohibited" and "controlled/regulatory" as separate checks, but the underlying data source is the same HS code lookup table. Treated them as equivalent: any match = prohibited for CLVS purposes. If subcategory distinction is needed, a `category` column filter on `ControlledRegulatedGood` would be required. |
| 2 | 🟡 | `customs_office_id` set only on insert (early_row_event), not on update | For EAI consume use case, shipments are ingested once (or replaced wholesale). If `planned_clearance_location_cd` is ever updated via API, `customs_office_id` won't auto-refresh. To support updates, add an early_row_event that also fires on update. |
| 3 | 🟡 | XML sections `mawbAsgmt`, `mawb`, `currencies`, `virtualRouteLegs`, `extraData` skipped | No matching persistent tables in the project schema (VirtualRouteLeg exists but has no FK to Shipment). Test gate counts don't include these. If they need to be persisted, add FK column to `virtual_route_leg` and extend `IsdcMapper.TAG_ROUTING`. |
| 4 | 🔴 | `PARTY_OID_NBR=0` normalized to `None` (autoincrement PK) | Follows CE rule 4d (SOURCE-PK normalization). Both consignee and shipper carry sentinel 0 in the sample XMLs. If a legitimate non-zero value of 0 were ever used as a real PK, this would conflict. Confirm with client that 0 is always a placeholder. |
| 5 | 🟡 | `blob_id` starts at last autoincrement value if server was previously started | The `sqlite_sequence` table tracks autoincrement state. The test gate clears domain tables but not `sqlite_sequence`. Blob IDs are non-sequential across test runs. This is cosmetic only — counts are correct. |
| 6 | 🟡 | HS code lookup uses digit-normalized prefix match | `controlled_regulated_goods.hs_code` stored as "9301.10.00" (8 digits). Commodity HS from XML is "4901990091" (10 digits, no dots). Normalized by stripping non-digits; commodity must start with controlled HS prefix. If edge cases arise (e.g., HS code "1001" matching "10011000"), add a minimum match length guard. |
