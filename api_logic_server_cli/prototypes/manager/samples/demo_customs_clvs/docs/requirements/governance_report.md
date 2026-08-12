---
generated: 2026-08-10
generated_by: claude-sonnet-5
project: demo_customs_clvs
---

# 🩺 Project Governance Report

## Summary

| Project | Tables | Wtd Rules | Coverage | Integrity | Red Flag | Effective LOC | Profile |
|---|---|---|---|---|---|---|---|
| demo_customs_clvs | 11 | 12 | **1.09** | **89** | — | 405 | 🟠 Thin coverage, 11 findings |

> **Coverage** = weighted rules / domain tables (sum/count=3, formula/copy=2, constraint=1). Target ≥ 3.0 for mature projects.
> **Integrity** = 100 minus demerits for anti-patterns: broken dependency tracking, procedural aggregates replacing rules, events that should be rules. Target ≥ 95.
> **Red Flag** = 🚨 if ≥ 10 FK tables and zero sum/count rules — team has evidently not adopted aggregation rules.
> **Effective LOC** = project `.py` lines added/changed vs the generated scaffold (`database/models.py` excluded). See per-table breakdown below.
> See `docs/training/governance.md` for full scoring guide.

**Coverage Score: 1.09**  (12 weighted rules / 11 tables)   🟠 Thin
**Integrity Score: 89**  (11 demerits, 0 reviewed)
**Red Flag: none**  (7 tables with incoming FKs, below the 10-table trigger threshold)
**Effective LOC: 405**  (vs scaffold baseline; `database/models.py` excluded)

────────────────────────────────────────
## COVERAGE DETAIL

**Domain tables (11):** Customer, CustomsRegion, ShipmentXml, VirtualRouteLeg, ControlledRegulatedGood, CustomsOffice, Shipment, Piece, ShipmentCommodity, SpecialHandling, ShipmentParty
**Excluded — lookup (≤2 non-PK cols):** GovtDept (2 non-PK cols)
**Excluded — Sys*:** SysConfig

**Rules:** 2× count, 1× copy, 3× formula, 1× row_event (unweighted), 2× early_row_event (unweighted), 1× after_flush_row_event (unweighted)
**Weighted:** (2×3) + (1×2) + (3×2) = 6 + 2 + 6 = **12**

**Tables with zero governing rules:** CustomsRegion, VirtualRouteLeg, Piece, SpecialHandling, GovtDept (excluded but noted) — 4 of 11 domain tables have no rules referencing them at all. `VirtualRouteLeg` in particular is a 31-column table entirely untouched by any logic file — likely out of scope for CLVS eligibility, but worth confirming it isn't a silent gap.

────────────────────────────────────────
## EFFECTIVE LOC DETAIL

```
Total Effective LOC: 405   (vs scaffold baseline; database/models.py excluded)
  logic_discovery:   171
  cross-cutting:     234   (api_discovery, security, integration)
```

**Per-table (logic_discovery LOC referencing each table — overlapping by design):**
```
Shipment                 138   (clvs_eligibility.py 93 + shipment_matching.py 45)
ShipmentCommodity         93
CustomsOffice             93
ControlledRegulatedGood   93
SysConfig                 93
Customer                  45
ShipmentParty             45
ShipmentXml               33
```

**Cross-cutting breakdown:**
```
integration/kafka/kafka_subscribe_discovery/isdc.py    102   (EAI consume pipeline, Tx2 parse/persist)
integration/IsdcMapper.py                                48   (XML → domain row mapper)
api/api_discovery/isdc_kafka_consume_debug.py            36   (debug endpoint, bypasses Kafka)
security/declare_security.py                             48   (see finding below — line count matches
                                                                 baseline but content is NOT the stub;
                                                                 real Roles/DefaultRolePermission block)
```

────────────────────────────────────────
## INTEGRITY FINDINGS

🟡 -1  `logic/logic_discovery/shipment_matching.py:1-13` (file docstring)
       Docstring contains implementation notes beyond verbatim requirement text: "Create
       `logic/logic_discovery/shipment_matching.py`", "Use Rule.row_event (not
       early_row_event) — fires before_flush so the new ShipmentParty writes atomically..."
       → Fix: keep only the verbatim requirement text (the matching-logic description);
       move implementation guidance to a code comment near `Rule.row_event(...)` instead.

🟡 -1  `logic/logic_discovery/isdc_consume.py:1-7` (file docstring)
       Docstring contains implementation notes: "row-event bridge", "(Tx 1, from Consumer 1
       or /consume_debug)", "See integration/kafka/kafka_subscribe_discovery/isdc.py".
       → Fix: keep only verbatim requirement text; move pipeline cross-references to a
       code comment.

🟡 -1  `customs_office.customs_region_id`
       FK column has no covering index.
       → Fix: `CREATE INDEX ix_customs_office_customs_region_id ON customs_office(customs_region_id);`

🟡 -1  `shipment.sys_config_id`
       FK column has no covering index.
       → Fix: `CREATE INDEX ix_shipment_sys_config_id ON shipment(sys_config_id);`

🟡 -1  `shipment.customs_office_id`
       FK column has no covering index. Read on every `clvs_reason` derivation
       (`_clvs_reason` queries `CustomsOffice` by this FK on every Shipment write).
       → Fix: `CREATE INDEX ix_shipment_customs_office_id ON shipment(customs_office_id);`

🟡 -1  `piece.local_shipment_oid_nbr`
       FK column has no covering index.
       → Fix: `CREATE INDEX ix_piece_local_shipment_oid_nbr ON piece(local_shipment_oid_nbr);`

🟡 -1  `shipment_commodity.controlled_regulated_goods_id`
       FK column has no covering index. Read on every `Rule.count` (`controlled_item_count`)
       recalculation.
       → Fix: `CREATE INDEX ix_shipment_commodity_controlled_regulated_goods_id ON shipment_commodity(controlled_regulated_goods_id);`

🟡 -1  `special_handling.oid_nbr`
       FK column has no covering index.
       → Fix: `CREATE INDEX ix_special_handling_oid_nbr ON special_handling(oid_nbr);`

🟡 -1  `shipment_party.local_piece_oid_nbr`
       FK column has no covering index.
       → Fix: `CREATE INDEX ix_shipment_party_local_piece_oid_nbr ON shipment_party(local_piece_oid_nbr);`

🟡 -1  `shipment_party.local_shipment_oid_nbr`
       FK column has no covering index.
       → Fix: `CREATE INDEX ix_shipment_party_local_shipment_oid_nbr ON shipment_party(local_shipment_oid_nbr);`

🟡 -1  `controlled_regulated_goods.govt_dept_id`
       FK column has no covering index.
       → Fix: `CREATE INDEX ix_controlled_regulated_goods_govt_dept_id ON controlled_regulated_goods(govt_dept_id);`

────────────────────────────────────────
## CLEAN — no demerit, verified

✅ `logic/logic_discovery/clvs_eligibility.py` — file docstring is verbatim requirement
   text only (Given/And/When/Then scenario), no implementation notes. All 4 `calling=`
   functions have proper docstrings. `_clvs_reason` (the reasons-list formula) references
   every `row.attr` directly in its own body — **zero dependency-anchor tuples, zero helper
   delegation** — this is the corrected 1-level pattern from the Aug 10 CE fix
   (logic_bank_api.md "ONE VALUE PER FORMULA" / "DETAIL VALUE + DERIVED FLAG"), verified
   working on this exact file.

✅ All 4 `session.query()` calls across the project (`_set_customs_office`,
   `_set_controlled_good`, `_clvs_reason`'s office re-lookup, `_match_importer`) are
   single-row `.filter().first()` / `.get()` lookups — matches the `row-lookup` Hall Pass,
   no demerit.

✅ `_publish_isdc` matches the `eai-consumer-bridge` Hall Pass (checks `is_processed`
   guard, publishes to topic) — no demerit.

✅ All 11 mapped tables have a single-column primary key — no structural PK defects.

✅ No rules declared in `logic/declare_logic.py` outside the discovery pattern.

✅ No missing `__init__.py` in logic discovery subdirectories.

────────────────────────────────────────
## ⚠️ Methodology note (not a scored finding)

`security/declare_security.py` is **48 lines**, exactly matching its baseline (48) —
by the letter of the Effective LOC rule this scores 0. But the file's actual content is
**not** the generated stub: it declares 10 real roles and `DefaultRolePermission` grants.
The line-count-only comparison happened to coincide with the baseline length here and
under-reports this file's real customization. Recommend treating this as **48 effective
LOC** (counted in the cross-cutting total above) rather than 0, and flagging this as a
methodology gap worth raising for `health_check.md` v1.9: a future revision should diff
content, not just compare line counts, at least for files short enough to diff cheaply.

────────────────────────────────────────
11 findings need attention (10 fixable in ≤1 line each; 2 are docstring rewrites).
Want me to fix them?
