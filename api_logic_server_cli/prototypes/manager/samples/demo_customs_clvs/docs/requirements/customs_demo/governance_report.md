# Project Governance Report — demo_customs_clvs

Generated: 2026-05-26 (revised after fixes)

## Summary

| Project           | Tables | Wtd Rules | Coverage | Integrity | Red Flag | Profile |
|---|---|---|---|---|---|---|
| demo_customs_clvs |  11    |    12      |  **1.09** | **100**  |   —      | 🟡 Thin coverage, clean integrity |

> **Coverage** = weighted rules / domain tables (sum/count=3, formula/copy=2, constraint=1). Target ≥ 3.0 for mature projects.  
> **Integrity** = 100 minus demerits for anti-patterns: broken dependency tracking, procedural aggregates replacing rules, events that should be rules. Target ≥ 95.  
> **Red Flag** = 🚨 if ≥ 10 FK tables and zero sum/count rules.  
> See `docs/training/governance.md` for full scoring guide.

**Coverage Score: 1.09**  (12 weighted rules / 11 tables)  🟠 Thin  
**Integrity Score: 100**  (0 demerits, 1 suppressed with annotation)  
**Red Flag: none**  (2 count rules; condition requires sum_count == 0)

---

## Coverage Detail

**Tables (11):**

| Table | Rules | Notes |
|---|---|---|
| shipment | 2× count, 2× formula | Primary domain table |
| shipment_commodity | 1× formula | Child — prohibited/controlled goods |
| shipment_xml | 1× after_flush_row_event | EAI blob bridge |
| customer | 0 | Read-only — EAI reference lookup |
| customs_office | 0 | Read-only — CLVS office lookup |
| customs_region | 0 | Read-only — reference |
| controlled_regulated_goods | 0 | Read-only — HS code reference |
| piece | 0 | Child — EAI ingested only |
| shipment_party | 0 | Child — EAI + matching |
| special_handling | 0 | Child — EAI ingested only |
| virtual_route_leg | 0 | Child — EAI ingested only |

**Excluded:**
- `govt_dept` — lookup (≤ 2 non-PK columns)
- `sys_config` — system table

**Rules declared:**

| Type | Count | Weighted |
|---|---|---|
| Rule.count | 2 | 6 |
| Rule.formula | 3 | 6 |
| Rule.sum | 0 | 0 |
| Rule.copy | 0 | 0 |
| Rule.constraint | 0 | 0 |
| Rule.early_row_event | 2 | 0 |
| Rule.row_event | 1 | 0 |
| Rule.after_flush_row_event | 1 | 0 |
| **Total weighted** | | **12** |

**Coverage = 12 / 11 = 1.09**

**Context note:** 8 of 11 tables are read-only in this domain — ingested via EAI, never updated through the API. The governed tables (Shipment, ShipmentCommodity) carry the full rule load. Coverage pressure is real but concentrated; the score reflects the wide schema, not absent rules on the active tables.

---

## Integrity Findings

All findings resolved. No demerits.

### ✅ Fixed — Broken dependency tracking (was -2 × 2)
**File:** `logic/logic_discovery/clvs_eligibility.py:96,102`

`_clvs_eligible` and `_clvs_reason` now include direct `row.attr` references so LogicBank tracks the dependency on `service_type_cd`, `local_customs_value_amt`, `prohibited_commodity_count`, `controlled_item_count`, and `customs_office_id`:
```python
_ = row.service_type_cd, row.local_customs_value_amt, row.prohibited_commodity_count, row.controlled_item_count, row.customs_office_id  # LB dependency tracking
```

### ✅ Suppressed — Raw query in early_row_event (was -1)
**File:** `logic/logic_discovery/clvs_eligibility.py:62`

`@health-check: suppress` annotation added with justification — prefix HS code matching requires a full table scan; no LB-expressible WHERE clause equivalent exists.

### ✅ Fixed — Docstring hygiene (was -1)
**File:** `logic/logic_discovery/shipment_matching.py:1`

Implementation notes removed from module docstring. Now contains only the requirement statement.

---

## Hall Passes

| File | Pattern | Reason |
|---|---|---|
| `logic/logic_discovery/isdc_consume.py` | `eai-consumer-bridge` | `is_processed` guard + Kafka publish to `isdc_processed` topic |
| `logic/logic_discovery/shipment_matching.py:28` | `row-lookup` | Single `.filter().first()` — one Customer row, no iteration |
| `logic/logic_discovery/clvs_eligibility.py:34` | `row-lookup` | Single `.filter_by().first()` — one CustomsOffice row |

---

## Logic Diagram

SVG: `docs/requirements/logic_diagrams/logic_diagram.svg`  
Flow doc: `docs/requirements/logic_flow_demo_customs_clvs.md`

Open SVG by dragging into a browser, or use the VSCode SVG Preview extension.
