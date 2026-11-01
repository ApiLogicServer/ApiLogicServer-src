## 🩺 Project Governance Report

**Project:** demo_customs_clvs &nbsp;|&nbsp; **Generated:** November 01, 2026 &nbsp;|&nbsp; **Method:** `vital signs` (docs/training/health_check.md v1.9)

| Project | Tables | Wtd Rules | Coverage | Integrity | Red Flag | Effective LOC | Profile |
|---|---|---|---|---|---|---|---|
| demo_customs_clvs | 11 | 12 | **1.1** | **89** | — | 389 | 🟠 Thin coverage (events by design), 2 findings |

**Coverage Score: 1.1** (12 weighted rules / 11 tables: 2× count, 2× formula, 1× copy) 🟠 Thin
Most of this system's logic is Kafka integration and lookup events, which weigh 0 by design; the weighted rules are the CLVS eligibility chain.

**Integrity Score: 89** (2 findings, 0 reviewed)
**Red Flag: none**
**Effective LOC: 389** — logic_discovery 148, cross-cutting 241 (Kafka subscribe 110, mapper 50, debug API 42, model customization 39)

### Integrity findings

- 🔴 **-3** `logic/logic_discovery/clvs_eligibility.py:49` — `_clvs_reason` reads the threshold and courier code through `SysConfig.current()`. The query is invisible to the rule engine, so changing `sys_config` re-evaluates nothing. Fix: `Rule.copy` each constant onto `shipment` (FK to `sys_config`). *Also listed in `customs_demo/ad-libs.md` as a review item.*
- 🟡 **-8** eight foreign-key columns have no covering index: `shipment.customs_office_id`, `shipment_commodity.controlled_regulated_goods_id`, `shipment_party.local_shipment_oid_nbr`, `shipment_party.local_piece_oid_nbr`, `piece.local_shipment_oid_nbr`, `special_handling.oid_nbr`, `customs_office.customs_region_id`, `controlled_regulated_goods.govt_dept_id`. Fine at demo scale.

Clean: every action function has a docstring; no rules in `declare_logic.py`; no table without a primary key; hall-pass patterns used (`kafka-publish`, `eai-consumer-bridge`, `row-lookup`) fit their skeletons.

### Per-table logic LOC (overlapping by design)
Shipment 121 · ShipmentCommodity 74 · CustomsOffice 74 · ControlledRegulatedGood 74 · SysConfig 74 · Customer 47 · ShipmentParty 47 · ShipmentXml 27
