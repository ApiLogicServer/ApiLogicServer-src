# 🩺 demo_customs_clvs — Project Governance Report
**Date:** 2026-06-11
**Scoring:** Coverage Score (weighted rules / domain tables) + Integrity Score (100 - demerits) + Effective LOC
**Reference:** `docs/training/health_check.md`

---

## Summary

| Project | Tables | Wtd Rules | Coverage | Integrity | Red Flag | Effective LOC | Profile |
|---|---|---|---|---|---|---|---|
| demo_customs_clvs | 11 | 12 | **1.1** | **89** | — | **481** | 🟠 CLVS eligibility use case (counts + dependency-anchor formulas) + 2-stage Kafka EAI ingestion (isdc); large 13-table customs schema with 9 tables not yet covered by rules; FK indexes missing schema-wide |

> **Coverage** = weighted rules / domain tables (sum/count=3, formula/copy=2, constraint=1). Target ≥ 3.0 for mature projects.
> **Integrity** = 100 minus demerits for anti-patterns: broken dependency tracking, procedural aggregates replacing rules, events that should be rules. Target ≥ 95.
> **Red Flag** = 🚨 if ≥ 10 FK tables and zero sum/count rules — team has evidently not adopted aggregation rules.
> **Effective LOC** = code added beyond the generated scaffold, vs hardcoded baseline LOC per file (see `docs/training/health_check.md` v1.7).
> See `docs/training/governance.md` for full scoring guide.

---

## Scores

| Metric | Value | Grade |
|---|---|---|
| **Coverage Score** | **1.1** (12 pts / 11 domain tables) | 🟠 Thin |
| **Integrity Score** | **89** (11 points deducted) | 🟡 Fair |
| **Effective LOC** | **481** | — |

---

## Coverage Detail

**Domain tables (11):** Customer, CustomsRegion, VirtualRouteLeg, ControlledRegulatedGood, CustomsOffice, Shipment, Piece, ShipmentCommodity, SpecialHandling, ShipmentParty, ShipmentXml

**Excluded — system (1):** SysConfig (begins with "Sys" — global configuration table)
**Excluded — lookup (1):** GovtDept (2 non-PK cols: name, authority)
*(lookup threshold: ≤ 2 non-PK columns)*

**Of the 11 domain tables, 4 have no active rule wiring**: CustomsRegion (referenced only via FK relationship from CustomsOffice), VirtualRouteLeg (31 cols — explicitly skipped by `IsdcMapper._SKIP_TAGS`), Piece and SpecialHandling (populated by `IsdcMapper.parse()` but have no derived/validated columns yet). This is the primary driver of the low Coverage score — the schema is provisioned for the full CIMCorp shipment XML, but business rules so far cover only the CLVS eligibility use case + importer matching.

**Rule inventory:**

| Rule | File | Type | Weight |
|---|---|---|---|
| ShipmentCommodity.is_prohibited = 1 if controlled_regulated_goods_id is not None else 0 | clvs_eligibility.py | formula | 2 |
| Shipment.prohibited_commodity_count = count(ShipmentCommodity where is_prohibited == 1) | clvs_eligibility.py | count | 3 |
| Shipment.controlled_item_count = count(ShipmentCommodity where controlled_regulated_goods_id is not None) | clvs_eligibility.py | count | 3 |
| Shipment.clvs_eligible = 1 if no ineligibility reasons else 0 | clvs_eligibility.py | formula | 2 |
| Shipment.clvs_reason = comma-delimited ineligibility reasons | clvs_eligibility.py | formula | 2 |
| Shipment → resolve customs_office_id from planned_clearance_location_cd | clvs_eligibility.py | event (row-lookup) | 0 |
| ShipmentCommodity → resolve controlled_regulated_goods_id from harmonized_tariff_nbr (HS prefix match) | clvs_eligibility.py | event (suppressed scan) | 0 |
| Shipment insert → match importer Customer by trprt_bill_to_acct_nbr, create ShipmentParty('I') | shipment_matching.py | event (row-lookup + create) | 0 |
| ShipmentXml insert → publish payload to Kafka topic `isdc_processed` | isdc_consume.py | event (eai-consumer-bridge) | 0 |

**Weighted total:** 2×count(3) + 3×formula(2) = 6 + 6 = **12**
**Coverage:** 12 / 11 = **1.1**

---

## Integrity Findings

| | File | Finding | Points |
|---|---|---|---|
| 🟡 | logic/logic_discovery/ | Missing `__init__.py` (root level) | **-1** |
| 🟡 | logic/logic_discovery/shipment_matching.py:14 | `_match_importer` (calling= function, wired via `Rule.row_event`) has no docstring | **-1** |
| 🟡 | logic/logic_discovery/isdc_consume.py:12 | `_publish_isdc` (calling= function, wired via `Rule.after_flush_row_event`) has no docstring | **-1** |
| 🟡 | database/db.sqlite | controlled_regulated_goods.govt_dept_id → govt_dept — no covering index | **-1** |
| 🟡 | database/db.sqlite | customs_office.customs_region_id → customs_region — no covering index | **-1** |
| 🟡 | database/db.sqlite | shipment.customs_office_id → customs_office — no covering index | **-1** |
| 🟡 | database/db.sqlite | piece.local_shipment_oid_nbr → shipment — no covering index | **-1** |
| 🟡 | database/db.sqlite | shipment_commodity.controlled_regulated_goods_id → controlled_regulated_goods — no covering index | **-1** |
| 🟡 | database/db.sqlite | special_handling.oid_nbr → shipment — no covering index | **-1** |
| 🟡 | database/db.sqlite | shipment_party.local_piece_oid_nbr → piece — no covering index | **-1** |
| 🟡 | database/db.sqlite | shipment_party.local_shipment_oid_nbr → shipment — no covering index | **-1** |

**Integrity:** 100 - 1 - 1 - 1 - (8 × 1) = **89**

### Schema Check — Primary Keys

All 13 tables (customer, customs_region, govt_dept, shipment_xml, sys_config, virtual_route_leg, controlled_regulated_goods, customs_office, shipment, piece, shipment_commodity, special_handling, shipment_party) have a primary key (`shipment_commodity` has a composite PK: `local_shipment_oid_nbr, sequence_nbr`; `shipment`, `piece`, `shipment_party` use natural-key PKs from the CIMCorp feed). **No findings.**

### Suppressed Findings (honored, not counted)

| | File | Finding | Annotation |
|---|---|---|---|
| ⚪ | logic/logic_discovery/clvs_eligibility.py:62 | `_set_controlled_goods` — `session.query(models.ControlledRegulatedGood).all()` inside `early_row_event`, then iterates to find an HS-code prefix match | `# @health-check: suppress — prefix HS match requires full table scan; no LB-expressible WHERE equivalent` |

### Hall Passes Applied

| | File | Function | Pattern |
|---|---|---|---|
| ✅ | logic/logic_discovery/clvs_eligibility.py:34 | `_set_customs_office` (early_row_event on Shipment) | `row-lookup` — single-row `.filter_by(office_code=...).first()` to resolve `customs_office_id` FK from `planned_clearance_location_cd` |
| ✅ | logic/logic_discovery/shipment_matching.py:21 | `_match_importer` (row_event on Shipment) | `row-lookup` — single-row `.filter(...).first()` to resolve importer Customer by `trprt_bill_to_acct_nbr`, then creates a `ShipmentParty('I')` child row |
| ✅ | logic/logic_discovery/isdc_consume.py:18-27 | `_publish_isdc` (after_flush_row_event on ShipmentXml) | `eai-consumer-bridge` — publishes raw payload to Kafka topic `isdc_processed`, guarded by `kafka_producer.producer is None` check, with docstring at module level |

### What's Clean

- ✅ `_clvs_eligible` and `_clvs_reason` correctly use the dependency-anchor pattern (`_ = row.attr1, row.attr2, ...`) before delegating to the shared `_reasons()` helper — exactly the documented workaround for LogicBank's static dependency scanner
- ✅ `Shipment.prohibited_commodity_count` and `Shipment.controlled_item_count` are proper `Rule.count` columns — `clvs_eligible`/`clvs_reason` react automatically to any `ShipmentCommodity` insert/update/delete, not a stale procedural snapshot
- ✅ `ShipmentCommodity.is_prohibited` is a simple, reactive `Rule.formula` (not a session-query side effect)
- ✅ `_set_customs_office` and `_set_controlled_goods` both have docstrings and correctly use `early_row_event` (not formula) for FK resolution
- ✅ The `@health-check: suppress` annotation on `_set_controlled_goods` is correctly applied — the HS-code prefix match genuinely has no LB-expressible `where=` equivalent (requires per-row string-prefix comparison across all `ControlledRegulatedGood` rows)
- ✅ `logic/declare_logic.py` (91 lines) is byte-identical to the `basic_demo_logic_gov` baseline — 0 net new lines, no rules misplaced outside `logic_discovery/`
- ✅ No wildcard imports outside `logic/load_verify_rules.py` (unmodified framework infrastructure)
- ✅ Two-stage Kafka EAI design (`isdc` → blob → `isdc_processed` → parsed domain rows) cleanly separates raw ingestion (Tx 1) from business-rule-governed parsing (Tx 2), and `isdc_kafka_consume_debug.py` provides a Kafka-free debug path using the same `process_isdc_payload()` function

---

## Action Items

| Priority | Item | Fix |
|---|---|---|
| 🟡 -1 | Missing `__init__.py` at `logic/logic_discovery/` | `touch logic/logic_discovery/__init__.py` |
| 🟡 -2 | `_match_importer` and `_publish_isdc` lack docstrings | Add one-line docstrings: `"""Match importer Customer by account number and create ShipmentParty."""` / `"""Publish ShipmentXml payload to Kafka topic isdc_processed."""` |
| 🟡 -8 | 8 unindexed FK columns | `CREATE INDEX` on each FK column listed above (controlled_regulated_goods.govt_dept_id, customs_office.customs_region_id, shipment.customs_office_id, piece.local_shipment_oid_nbr, shipment_commodity.controlled_regulated_goods_id, special_handling.oid_nbr, shipment_party.local_piece_oid_nbr, shipment_party.local_shipment_oid_nbr) |
| 🟠 (Coverage) | 4 of 11 domain tables (CustomsRegion, VirtualRouteLeg, Piece, SpecialHandling) have no derived/validated columns | Not a defect — schema is provisioned ahead of rules for the full CIMCorp feed. Future use cases (e.g., piece-level weight/dimension validation, special-handling-driven routing) would raise Coverage |

---

## Effective LOC Detail

Total Effective LOC: **481** (vs hardcoded scaffold baselines; `database/models.py` excluded)

| Bucket | LOC | Detail |
|---|---|---|
| logic_discovery/clvs_eligibility.py (new file) | 133 | CLVS eligibility use case: 2 early_row_events (FK resolution), 1 formula, 2 count rules, 2 dependency-anchored formulas |
| logic_discovery/shipment_matching.py (new file) | 45 | Importer-matching row_event: Customer lookup by account number → creates ShipmentParty |
| logic_discovery/isdc_consume.py (new file) | 31 | after_flush_row_event: ShipmentXml insert → publish to Kafka topic `isdc_processed` |
| integration/IsdcMapper.py (new file) | 107 | CIMCorp Shipment XML → Shipment/Piece/ShipmentParty/ShipmentCommodity/SpecialHandling mapper |
| integration/kafka/kafka_subscribe_discovery/isdc.py (new file) | 121 | 2-stage Kafka consumer: `isdc` (raw blob) + `isdc_processed` (parse + persist), with REPLACE/FAIL duplicate policy |
| api/api_discovery/isdc_kafka_consume_debug.py (new file) | 44 | `/consume_debug/isdc` debug endpoint — same parse path without Kafka |

> Baseline reference: `basic_demo_logic_gov` (closest same-generation sibling — `logic/declare_logic.py`=91 lines,
> byte-identical, 0 net new). All standard scaffold files (`api/api_discovery/{new_service,newer_service,
> ontimize_api,system,mcp_discovery,auto_discovery}.py`, `integration/n8n/n8n_producer.py`,
> `integration/kafka/kafka_subscribe_discovery/auto_discovery.py`, `integration/system/*`,
> `integration/mcp/mcp_client_executor.py`) diff identically against `basic_demo_logic_gov` — 0 net new.
> `logic/logic_discovery/use_case.py` (22 lines, empty template) and `auto_discovery.py` (51 lines,
> standard discovery loop) also match the framework pattern — 0 net new.
> All 481 Effective LOC is concentrated in 6 new files implementing the CLVS eligibility use case
> and the 2-stage Kafka EAI ingestion pipeline for CIMCorp shipment XML.

**Per-table (logic LOC referencing each table — overlapping by design):**

| Table | LOC | Files |
|---|---|---|
| Shipment | ~450 | clvs_eligibility.py (FK resolution, eligibility formulas, count rules), shipment_matching.py (importer match trigger), IsdcMapper.py + isdc.py + isdc_kafka_consume_debug.py (parse target, duplicate-replace, debug response fields) |
| ShipmentCommodity | ~240 | clvs_eligibility.py (is_prohibited formula, controlled-goods FK resolution, count rules), IsdcMapper.py (commodity parsing) |
| ShipmentParty | ~152 | shipment_matching.py (creates importer party), IsdcMapper.py (consignee/shipper parsing + PARTY_OID_NBR normalization) |
| ShipmentXml | ~152 | isdc_consume.py (publish event), isdc.py (blob persistence, both consumers) |
| CustomsOffice | ~133 | clvs_eligibility.py (`_set_customs_office` FK resolution + clvs_release check) |
| ControlledRegulatedGood | ~133 | clvs_eligibility.py (`_set_controlled_goods` HS-prefix match) |
| Customer | ~45 | shipment_matching.py (`_match_importer` lookup by account number) |
| Piece | ~107 | IsdcMapper.py (piece parsing, first-piece tracking for piece-level party FK) |
| SpecialHandling | ~107 | IsdcMapper.py (specialHandlingCodes parsing) |

> Counts overlap because `IsdcMapper.py` populates 5 tables in one file, and `clvs_eligibility.py`
> declares 7 rules across Shipment, ShipmentCommodity, CustomsOffice, and ControlledRegulatedGood.

---

## Summary

demo_customs_clvs implements the **CLVS (Courier Low Value Shipment) eligibility use case** for Canada Customs, plus a **2-stage Kafka EAI ingestion pipeline** that parses CIMCorp shipment XML into a 13-table customs domain model.

**Coverage 1.1** — thin, but for a structural reason rather than a quality problem: the 13-table schema (144 columns on `Shipment` alone) is provisioned for the full CIMCorp feed, while business rules so far cover only CLVS eligibility (5 weighted rules: 1 formula + 2 counts + 2 dependency-anchored formulas = 12 pts) plus 4 zero-weight integration events. 4 of 11 domain tables (CustomsRegion, VirtualRouteLeg, Piece, SpecialHandling) have no derived/validated columns yet — they are populated by the EAI mapper but not yet governed by declarative rules.

**Integrity 89** — fair; no correctness bugs found. The 11-point deduction is entirely organizational/advisory: a missing `logic_discovery/__init__.py`, two `calling=` functions without docstrings (`_match_importer`, `_publish_isdc`), and the same class of unindexed-FK findings seen across the portfolio (8 here, reflecting the larger schema). The project correctly applies the `@health-check: suppress` annotation on the one genuinely unavoidable full-table-scan (`_set_controlled_goods`'s HS-code prefix match), and both `_clvs_eligible`/`_clvs_reason` correctly use the dependency-anchor pattern — these are the two patterns most often gotten wrong elsewhere, and both are correct here.

**Effective LOC 481** — all of it concentrated in 6 new files: the CLVS eligibility use case (`clvs_eligibility.py`, 133 lines; `shipment_matching.py`, 45 lines), and the Kafka EAI ingestion pipeline (`isdc_consume.py` 31, `IsdcMapper.py` 107, `kafka_subscribe_discovery/isdc.py` 121, `isdc_kafka_consume_debug.py` 44). Every other file in the project — including all `api/api_discovery/` scaffolding, `integration/system/*`, `integration/mcp/*`, `integration/n8n/*`, and `logic/declare_logic.py` — is byte-identical to the `basic_demo_logic_gov` baseline.
