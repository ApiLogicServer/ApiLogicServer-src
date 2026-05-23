# 🩺 Project Governance Report — demo_customs_clvs

**Generated:** 2026-05-22  
**Reviewer:** Claude Code (claude-sonnet-4-6)

---

## Summary

| Project | Tables | Wtd Rules | Coverage | Integrity | Red Flag | Profile |
|---|---|---|---|---|---|---|
| demo_customs_clvs | 11 | 10 | **0.91** | **96** | — | 🔴 Thin coverage (EAI project); integrity strong |

> **Coverage** = weighted rules / domain tables (sum/count=3, formula/copy=2, constraint=1). Target ≥ 3.0 for mature projects.  
> **Integrity** = 100 minus demerits for anti-patterns. Target ≥ 95.  
> **Red Flag** = 🚨 if ≥ 10 FK tables and zero sum/count rules.  

**Coverage Score: 0.91** (10 weighted rules / 11 tables) — 🔴 Weak  
**Integrity Score: 96** (4 demerits, 0 reviewed) — ✅ Strong  
**Red Flag: none** (5 FK tables, 2 aggregation rules)

> ℹ️ **Context note:** This is primarily an EAI data ingestion project. Most tables persist external CIMCorp XML without business invariants — ungoverned tables reflect correct architecture, not missing rules. CLVS eligibility logic on Shipment/ShipmentCommodity is well-governed for its scope.

---

## Coverage Detail

### Rule inventory

| File | Rules | Weighted |
|---|---|---|
| `clvs_eligibility.py` | 2× count (wt 3), 2× formula (wt 2), 1× early_row_event (wt 0) | **10** |
| `isdc_consume.py` | 1× after_flush_row_event (wt 0) | 0 |
| `shipment_matching.py` | 1× row_event (wt 0) | 0 |
| **Total** | | **10** |

Rule type breakdown: sum=0, count=2, formula=2, copy=0, constraint=0

### Table coverage

| Table | Rules | Notes |
|---|---|---|
| `Shipment` | 2 count + 2 formula | CLVS eligibility — well-governed |
| `ShipmentCommodity` | 1 early_row_event (wt 0) | HS code lookup + FK assignment |
| `ShipmentXml` | 1 after_flush_row_event (wt 0) | EAI blob bridge — infrastructure |
| `Customer` | 0 | EAI reference lookup only |
| `CustomsRegion` | 0 | Reference data |
| `ControlledRegulatedGood` | 0 | Reference data |
| `CustomsOffice` | 0 | Reference data |
| `Piece` | 0 | EAI-ingested, pass-through |
| `SpecialHandling` | 0 | EAI-ingested, pass-through |
| `ShipmentParty` | 0 | EAI-ingested + matching output |
| `VirtualRouteLeg` | 0 | EAI-ingested, standalone |

**Excluded from denominator:**
- `SysConfig` — Sys* class (system config)
- `GovtDept` — ≤ 2 non-PK columns (narrow lookup: `name`, `authority`)

**Coverage Score = 10 / 11 = 0.91** — 🔴 Weak

---

## Integrity Findings

### 🔴 Finding 1 — -2 points
**File:** `logic/logic_discovery/clvs_eligibility.py:35–37`  
**Category:** Event that should be a rule  

`_resolve_hs_controlled` (early_row_event on ShipmentCommodity) sets both `controlled_regulated_goods_id` (FK — correct for early_row_event) and `row.is_prohibited = 1` (derived flag — should be `Rule.formula`).

```python
# Current (flagged):
def _resolve_hs_controlled(row, old_row, logic_row):
    ...
    if crg:
        row.controlled_regulated_goods_id = crg.id
        row.is_prohibited = 1           # ← should be Rule.formula

# Fix: separate into Rule.formula after the early_row_event:
Rule.early_row_event(on_class=models.ShipmentCommodity, calling=_resolve_hs_controlled)
Rule.formula(derive=models.ShipmentCommodity.is_prohibited,
             as_expression=lambda row: 1 if row.controlled_regulated_goods_id is not None else 0)
# Remove the row.is_prohibited = 1 line from _resolve_hs_controlled
```

**Why it matters:** If `controlled_regulated_goods_id` is set via the API or Admin UI (not through the EAI path), `is_prohibited` will not update automatically. The formula makes the derivation reactive on all write paths.

---

### 🟡 Finding 2 — -1 point
**File:** `logic/logic_discovery/shipment_matching.py:11`  
**Category:** Docstring hygiene — implementation note beyond requirement text

Line 11: `"Use Rule.row_event (not early_row_event) — fires before_flush so the new ShipmentParty writes atomically with the parent Shipment."`

This specifies which rule type to use and why — implementation guidance, not requirement text. On the next AI iteration, this causes the model to code to the implementation note rather than the requirement.

**Fix:** Remove that line. The docstring should contain only the verbatim requirement text from `requirements.md`.

---

### 🟡 Finding 3 — -1 point
**File:** `logic/logic_discovery/isdc_consume.py:9`  
**Category:** Missing docstring on `calling=` function

`_publish_isdc` is wired via `Rule.after_flush_row_event(calling=_publish_isdc)` but has no docstring. The first docstring line appears in logic flow diagrams — without it, diagrams show only the function name with no indication of what it does.

```python
# Current (flagged):
def _publish_isdc(row: models.ShipmentXml, old_row, logic_row: LogicRow):
    if not logic_row.is_inserted() or not row.payload:
        return

# Fix:
def _publish_isdc(row: models.ShipmentXml, old_row, logic_row: LogicRow):
    """Publish ShipmentXml payload to isdc_processed topic after blob commit (Kafka bridge)."""
    if not logic_row.is_inserted() or not row.payload:
        return
```

---

## Hall Passes Applied (no demerit)

| Location | Pattern | Reason |
|---|---|---|
| `clvs_eligibility.py:29–34` | `row-lookup` | `session.query(ControlledRegulatedGood).filter().first()` — single-row reference lookup, `no_autoflush` guard |
| `clvs_eligibility.py:52–60` | `row-lookup` | `session.query(CustomsOffice).filter().first()` — single-row CLVS office designation check, `no_autoflush` guard |
| `shipment_matching.py:29–34` | `row-lookup` | `session.query(Customer).filter().first()` — single-row importer match, `no_autoflush` guard |
| `isdc_consume.py` | `eai-consumer-bridge` | Publishes to Kafka topic; checks `is_processed` guard before publishing |

---

## Red Flag Check

- Tables with incoming FKs: 5 (Shipment, CustomsRegion, GovtDept, ControlledRegulatedGood, Piece)
- Total `Rule.sum` + `Rule.count`: 2
- Threshold: ≥ 10 FK tables AND 0 aggregation rules

**Result: ✅ No red flag** (5 < 10, and 2 aggregation rules present)

---

## Dependency Tracking Note (not a demerit — style advisory)

`_clvs_reason` and `_clvs_eligible` use a tuple-assignment trick to force LB dependency visibility:

```python
_ = row.service_type_cd, row.local_customs_value_amt, row.prohibited_commodity_count, \
    row.controlled_commodity_count, row.planned_clearance_location_cd
return ", ".join(_clvs_reasons(row, logic_row.session))
```

This is technically correct — LB scans the function body and finds all `row.attr` references in the tuple expression. The pattern works but is unusual. A future refactor could inline the logic directly into each function body to make the dependencies unambiguous without the hack.

---

## Summary

**3 findings need attention:**

1. 🔴 **Fix recommended** — `clvs_eligibility.py:37` — add `Rule.formula` for `is_prohibited`; remove from early_row_event
2. 🟡 **Easy fix** — `shipment_matching.py:11` — remove implementation note from docstring
3. 🟡 **Easy fix** — `isdc_consume.py:9` — add one-line docstring to `_publish_isdc`

Want me to apply any of these fixes?
