# 🩺 demo_customs — Project Governance Report
**Date:** 2026-05-11  
**Scoring:** Coverage Score (weighted rules / domain tables) + Integrity Score (100 - demerits)  
**Reference:** `docs/training/health_check.md`, `docs/training/governance.md`

---

## Summary

| Project | Tables | Wtd Rules | Coverage | Integrity | Red Flag | Profile |
|---|---|---|---|---|---|---|
| demo_customs | 7 | 7 | **1.0** | **100** | — | 🟠 Integration focus — rules thin by design |

> **Coverage** = weighted rules / domain tables (sum/count=3, formula/copy=2, constraint=1). Target ≥ 3.0 for mature projects.  
> **Integrity** = 100 minus demerits for anti-patterns: broken dependency tracking, procedural aggregates replacing rules, events that should be rules. Target ≥ 95.  
> **Red Flag** = 🚨 if ≥ 10 FK tables and zero sum/count rules — team has evidently not adopted aggregation rules.  
> See `docs/training/governance.md` for full scoring guide.

---

## Scores

| Metric | Value | Grade |
|---|---|---|
| **Coverage Score** | **1.0** (7 pts / 7 domain tables) | 🟠 Thin |
| **Integrity Score** | **100** (0 demerits) | ✅ Clean |
| **Red Flag** | — none | 2 FK tables, 1 aggregation rule |

---

## Coverage Detail

**Domain tables (7):** Shipment, Piece, ShipmentCommodity, ShipmentParty, SpecialHandling, CcpCustomer, VirtualRouteLeg

**Excluded — system:** sqlite_sequence  
**Excluded — Sys pattern:** SysConfig (settings table)  
**Excluded — infrastructure:** ShipmentXml (blob/staging table — not a domain entity)  
**Excluded — lookup (≤2 non-PK cols):** none — all tables have ≥3 non-PK columns

**Rule inventory:**

| Rule | File | Type | Weight |
|---|---|---|---|
| Shipment.prohibited_commodity_count = count(ShipmentCommodity where is_prohibited) | clvs_eligibility.py:38 | count | 3 |
| Shipment.clvs_eligible | clvs_eligibility.py:41 | formula | 2 |
| Shipment.clvs_reason | clvs_eligibility.py:42 | formula | 2 |
| ShipmentXml after_flush → publish isdc_processed | isdc_consume.py:31 | event | 0 |
| Shipment row_event → match importer | shipment_matching.py:58 | event | 0 |

**Weighted total:** 1×count(3) + 2×formula(2) = 3+4 = **7**  
**Coverage:** 7 / 7 = **1.0**

**Note on thin coverage:** This project is integration-focused — its primary value is the Kafka 2-message pipeline, XML parsing, and 7-table persistence. The 3 business rules that exist (CLVS eligibility count + 2 formulas) are correct and complete for the current requirements. Coverage is thin not because rules were avoided, but because the domain requirements are primarily structural.

---

## Integrity Findings

None. All patterns are correct.

### Hall Passes Applied

| | File | Line | Pattern |
|---|---|---|---|
| ✅ | shipment_matching.py | 30 | `row-lookup` — single `session.query().filter_by().first()` for CcpCustomer |
| ✅ | isdc_consume.py | 22 | `eai-consumer-bridge` — `is_processed` guard + publish to isdc_processed topic |

### What's Clean

- ✅ `clvs_eligibility.py` — `_clvs_reasons()` helper called from `calling=` functions; direct `row.attr` refs present
- ✅ No `session.query()` inside formula functions
- ✅ No `as_expression=lambda row: my_func(row)` wrapping
- ✅ Docstrings contain verbatim requirement text (BDD Scenario format)
- ✅ All logic in `logic/logic_discovery/` files — not in `declare_logic.py`

---

## Red Flag Check

- Tables with incoming FKs: **2** (Shipment, Piece) — well below threshold of 10
- Rule.sum + Rule.count: **1** (Rule.count on ShipmentCommodity)
- **No red flag**

---

## Summary

demo_customs is an integration showcase, not a rules showcase. Coverage of 1.0 reflects the domain — CLVS eligibility is the only business derivation; the rest is EAI plumbing. Integrity is 100 — the rules that exist are correctly implemented. No anti-patterns, no red flag.

Compare with `demo_customs_cbsa` (same customs domain, pure business logic): Coverage 7.8, Integrity 100. The contrast illustrates that the two projects serve different purposes.
