# 🩺 demo_customs_cbsa — Project Governance Report
**Date:** 2026-05-11  
**Scoring:** Coverage Score (weighted rules / domain tables) + Integrity Score (100 - demerits)  
**Reference:** `docs/training/health_check.md`, `docs/training/governance.md`

---

## Summary

| Project | Tables | Wtd Rules | Coverage | Integrity | Red Flag | Profile |
|---|---|---|---|---|---|---|
| demo_customs_cbsa | 5 | 39 | **7.8** | **100** | — | ✅ Exemplary — pure declarative business logic |

> **Coverage** = weighted rules / domain tables (sum/count=3, formula/copy=2, constraint=1). Target ≥ 3.0 for mature projects.  
> **Integrity** = 100 minus demerits for anti-patterns: broken dependency tracking, procedural aggregates replacing rules, events that should be rules. Target ≥ 95.  
> **Red Flag** = 🚨 if ≥ 10 FK tables and zero sum/count rules — team has evidently not adopted aggregation rules.  
> See `docs/training/governance.md` for full scoring guide.

---

## Scores

| Metric | Value | Grade |
|---|---|---|
| **Coverage Score** | **7.8** (39 pts / 5 domain tables) | ✅ Strong |
| **Integrity Score** | **100** (0 demerits) | ✅ Clean |
| **Red Flag** | — none | 5 FK tables, 3 aggregation rules |

---

## Coverage Detail

**Domain tables (5):** CustomsEntry, SurtaxLineItem, CountryOrigin, HsCodeRate, Province

**Excluded — system:** sqlite_sequence  
**Excluded — Sys pattern:** SysConfig (settings table — rates/dates managed here via Rule.copy)  
**Excluded — lookup (≤2 non-PK cols):** none — all tables have ≥3 non-PK columns

**Rule inventory:**

| Rule | File | Type | Weight |
|---|---|---|---|
| CustomsEntry.total_customs_value = sum(SurtaxLineItem.customs_value) | entry_totals.py:19 | sum | 3 |
| CustomsEntry.total_duty_amount = sum(SurtaxLineItem.base_duty_amount) | entry_totals.py:20 | sum | 3 |
| CustomsEntry.total_surtax_amount = sum(SurtaxLineItem.surtax_amount) | entry_totals.py:21 | sum | 3 |
| CustomsEntry.duty_paid_value | entry_totals.py:24 | formula | 2 |
| CustomsEntry.sales_tax_amount | entry_totals.py:30 | formula | 2 |
| CustomsEntry.total_tax_due | entry_totals.py:36 | formula | 2 |
| CustomsEntry.surtax_applicable | line_amounts.py:19 | formula | 2 |
| SurtaxLineItem.base_duty_amount | line_amounts.py:23 | formula | 2 |
| SurtaxLineItem.surtax_amount | line_amounts.py:27 | formula | 2 |
| CustomsEntry.effective_date copy from SysConfig | lookup_values.py:22 | copy | 2 |
| CustomsEntry.program_code copy from SysConfig | lookup_values.py:23 | copy | 2 |
| CustomsEntry.pc_number copy from SysConfig | lookup_values.py:24 | copy | 2 |
| CustomsEntry.country_surtax_rate copy from CountryOrigin | lookup_values.py:27 | copy | 2 |
| CustomsEntry.province_tax_rate copy from Province | lookup_values.py:30 | copy | 2 |
| SurtaxLineItem.base_duty_rate copy from HsCodeRate | lookup_values.py:33 | copy | 2 |
| SurtaxLineItem.country_surtax_rate copy from CustomsEntry | lookup_values.py:36 | copy | 2 |
| SurtaxLineItem.surtax_applicable copy from CustomsEntry | lookup_values.py:37 | copy | 2 |
| SurtaxLineItem.customs_value > 0 | validation.py:16 | constraint | 1 |
| CustomsEntry.ship_date required | validation.py:20 | constraint | 1 |

**Weighted total:** 3×sum(3) + 6×formula(2) + 8×copy(2) + 2×constraint(1) = 9+12+16+2 = **39**  
**Coverage:** 39 / 5 = **7.8**

---

## Integrity Findings

None. All patterns are correct.

### What's Clean

- ✅ All formulas use inline lambdas with direct `row.attr` references — no wrapping functions
- ✅ `effective_date` comparison uses `row.effective_date` (copied from SysConfig) — no hardcoded dates in rules
- ✅ Dates in docstrings are verbatim requirement text (CBSA order reference), not rule inputs
- ✅ All logic in `logic/logic_discovery/cbsa_surtax/` — not in `declare_logic.py`
- ✅ `cbsa_surtax/__init__.py` present
- ✅ TODO comment in `lookup_values.py` correctly prompts copy vs formula review
- ✅ No events, no session.query(), no procedural code anywhere

---

## Red Flag Check

- Tables with incoming FKs: **5** — well below threshold of 10
- Rule.sum + Rule.count: **3** (3 sums on CustomsEntry)
- **No red flag**

---

## Summary

demo_customs_cbsa is the reference standard for pure declarative business logic. 39 weighted rules across 5 domain tables (7.8 coverage) with zero demerits. No procedural code, no events, no session queries — just rules. The SysConfig pattern correctly externalises all regulatory rates and dates so rules reference copied columns rather than hardcoded literals.

This project demonstrates what a compliance/regulatory domain looks like when fully governed by declarative rules. Use it as the benchmark when evaluating other projects.
