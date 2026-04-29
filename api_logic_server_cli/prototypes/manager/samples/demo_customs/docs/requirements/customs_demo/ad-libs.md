# Ad-Libs Report — customs_demo

**1 item needs your review. 7 FYIs — standard patterns, no action needed.**

---

## 🔴 Review Required

| Location | Issue | Action |
|---|---|---|
| `integration/IsdcMapper.py` `TAG_ROUTING` | `ns2:virtualRouteLegs` rows are inserted standalone (no FK to `Shipment` in the schema). Assumed this is correct and stored them via `session.add(leg)` without parent attachment. | Verify `virtual_route_leg` table has no `local_shipment_oid_nbr` FK and standalone insert is the intended behavior. |

---

## 🟡 FYI

- `integration/IsdcMapper.py` — Sections skipped (no matching table in schema): `ns2:mawbAsgmt`, `ns2:mawb`, `ns2:currencies`, `ns2:extraData`. Standard pattern: unmapped sections are silently ignored.
- `integration/IsdcMapper.py` — `PARTY_OID_NBR=0` normalized to `None` for both consignee and shipper (both carry sentinel value `0` in the reference XML). This follows the mandatory SOURCE-PK normalization rule from `eai_subscribe.md` to prevent UNIQUE constraint failures.
- `integration/kafka/kafka_subscribe_discovery/isdc.py` — `ISDC_DUPLICATE_POLICY=replace` set as default (per requirements: "default `replace` for this project"). Controlled via env var; `fail` policy available for insert-only testing.
- `integration/kafka/kafka_subscribe_discovery/isdc.py` — Replace policy uses `session.delete(existing); session.flush()` before reinsert, relying on `ON DELETE CASCADE` on child FKs. The ORM cascade added in `database/models.py` (`cascade="all, delete"`) ensures SQLAlchemy-side cascade aligns with the DB-level cascade.
- `logic/logic_discovery/isdc_consume.py` — `is_processed` guard on the `after_flush_row_event` bridge (mandatory per `eai_subscribe.md` v1.2 — prevents spurious re-publish on the debug path).
- `logic/logic_discovery/shipment_matching.py` — Uses `Rule.row_event` (not `early_row_event`) as specified in requirements, so the new `ShipmentParty` row is written atomically with the parent `Shipment` in `before_flush`.
- `config/default.env` — `KAFKA_SERVER = localhost:9092` and `KAFKA_CONSUMER_GROUP = customs_demo-group1` uncommented for Step 3. Use a fresh group name if project is cloned.
