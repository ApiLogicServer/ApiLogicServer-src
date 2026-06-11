# 🩺 demo_customs_surtax — Project Governance Report
**Date:** 2026-06-11
**Scoring:** Coverage Score (weighted rules / domain tables) + Integrity Score (100 - demerits) + Effective LOC
**Reference:** `docs/training/health_check.md`

---

## Summary

| Project | Tables | Wtd Rules | Coverage | Integrity | Red Flag | Effective LOC | Profile |
|---|---|---|---|---|---|---|---|
| demo_customs_surtax | 5 | 38 | **7.6** | **94** | — | **93** | ✅ CBSA Steel Derivative Goods Surtax Order — single dense logic file (18 rules) covering both transactional tables; FK indexes missing schema-wide |

> **Coverage** = weighted rules / domain tables (sum/count=3, formula/copy=2, constraint=1). Target ≥ 3.0 for mature projects.
> **Integrity** = 100 minus demerits for anti-patterns: broken dependency tracking, procedural aggregates replacing rules, events that should be rules. Target ≥ 95.
> **Red Flag** = 🚨 if ≥ 10 FK tables and zero sum/count rules — team has evidently not adopted aggregation rules.
> **Effective LOC** = code added beyond the generated scaffold, vs hardcoded baseline LOC per file (see `docs/training/health_check.md` v1.7).
> See `docs/training/governance.md` for full scoring guide.

---

## Scores

| Metric | Value | Grade |
|---|---|---|
| **Coverage Score** | **7.6** (38 pts / 5 domain tables) | ✅ Strong |
| **Integrity Score** | **94** (6 points deducted) | 🟡 Fair |
| **Effective LOC** | **93** | — |

---

## Coverage Detail

**Domain tables (5):** CountryOrigin, HsCodeRate, Province, CustomsEntry, SurtaxLineItem

**Excluded — system (1):** SysConfig (begins with "Sys" — global configuration table; supplies the order's regulatory constants: `effective_date`, `program_code`, `pc_number`)

*(lookup threshold: ≤ 2 non-PK columns — CountryOrigin (4 non-PK cols), HsCodeRate (4 non-PK cols), and Province (3 non-PK cols) all exceed the threshold and are counted as domain tables; each is also the `from_parent` source of an active `Rule.copy`)*

**All 5 domain tables have active rule wiring** — every table participates in at least one `Rule.copy`, `Rule.formula`, `Rule.sum`, or `Rule.constraint`. This is the primary driver of the high Coverage score: the entire 18-rule order calculation (surtax applicability, duty, provincial sales tax, totals) is implemented in a single declarative file with no gaps.

**Rule inventory:**

| Rule | File | Type | Weight |
|---|---|---|---|
| CustomsEntry.effective_date = copy from SysConfig.effective_date | cbsa_steel_surtax.py | copy | 2 |
| CustomsEntry.program_code = copy from SysConfig.program_code | cbsa_steel_surtax.py | copy | 2 |
| CustomsEntry.pc_number = copy from SysConfig.pc_number | cbsa_steel_surtax.py | copy | 2 |
| CustomsEntry.country_surtax_rate = copy from CountryOrigin.surtax_rate | cbsa_steel_surtax.py | copy | 2 |
| CustomsEntry.province_tax_rate = copy from Province.tax_rate | cbsa_steel_surtax.py | copy | 2 |
| CustomsEntry.surtax_applicable = 1 if ship_date ≥ effective_date and country_surtax_rate > 0 else 0 | cbsa_steel_surtax.py | formula | 2 |
| CustomsEntry.total_customs_value = sum(SurtaxLineItem.customs_value) | cbsa_steel_surtax.py | sum | 3 |
| CustomsEntry.total_duty_amount = sum(SurtaxLineItem.base_duty_amount) | cbsa_steel_surtax.py | sum | 3 |
| CustomsEntry.total_surtax_amount = sum(SurtaxLineItem.surtax_amount) | cbsa_steel_surtax.py | sum | 3 |
| CustomsEntry.duty_paid_value = total_customs_value + total_duty_amount + total_surtax_amount (no_prune) | cbsa_steel_surtax.py | formula | 2 |
| CustomsEntry.sales_tax_amount = duty_paid_value × province_tax_rate (no_prune) | cbsa_steel_surtax.py | formula | 2 |
| CustomsEntry.total_tax_due = total_duty_amount + total_surtax_amount + sales_tax_amount (no_prune) | cbsa_steel_surtax.py | formula | 2 |
| SurtaxLineItem.base_duty_rate = copy from HsCodeRate.base_duty_rate | cbsa_steel_surtax.py | copy | 2 |
| SurtaxLineItem.is_steel_derivative = copy from HsCodeRate.is_steel_derivative | cbsa_steel_surtax.py | copy | 2 |
| SurtaxLineItem.surtax_applicable = 1 if entry.surtax_applicable and is_steel_derivative else 0 | cbsa_steel_surtax.py | formula | 2 |
| SurtaxLineItem.base_duty_amount = customs_value × base_duty_rate | cbsa_steel_surtax.py | formula | 2 |
| SurtaxLineItem.surtax_amount = customs_value × entry.country_surtax_rate (if surtax_applicable) | cbsa_steel_surtax.py | formula | 2 |
| SurtaxLineItem: customs_value > 0 | cbsa_steel_surtax.py | constraint | 1 |

**Weighted total:** 7×copy(2) + 7×formula(2) + 3×sum(3) + 1×constraint(1) = 14 + 14 + 9 + 1 = **38**
**Coverage:** 38 / 5 = **7.6**

---

## Integrity Findings

| | File | Finding | Points |
|---|---|---|---|
| 🟡 | logic/logic_discovery/ | Missing `__init__.py` (root level) | **-1** |
| 🟡 | database/db.sqlite | customs_entry.sys_config_id → sys_config — no covering index | **-1** |
| 🟡 | database/db.sqlite | customs_entry.province_id → province — no covering index | **-1** |
| 🟡 | database/db.sqlite | customs_entry.country_origin_id → country_origin — no covering index | **-1** |
| 🟡 | database/db.sqlite | surtax_line_item.hs_code_id → hs_code_rate — no covering index | **-1** |
| 🟡 | database/db.sqlite | surtax_line_item.customs_entry_id → customs_entry — no covering index | **-1** |

**Integrity:** 100 - 1 - (5 × 1) = **94**

### Schema Check — Primary Keys

All 6 tables (country_origin, hs_code_rate, province, sys_config, customs_entry, surtax_line_item) have a primary key (`id INTEGER PRIMARY KEY AUTOINCREMENT`). **No findings.**

### Suppressed Findings (honored, not counted)

None — `cbsa_steel_surtax.py` contains no `@health-check` annotations.

### Hall Passes Applied

None — `cbsa_steel_surtax.py` contains zero `calling=` functions, zero events, and zero `session.query()` calls. All 18 rules are purely declarative (`Rule.copy` / `Rule.sum` / `Rule.formula` / `Rule.constraint`).

### What's Clean

- ✅ The entire order (CBSA Steel Derivative Goods Surtax Order, PC 2025-0917) is implemented as 18 purely declarative rules — no procedural code, no events, no `session.query()`
- ✅ All regulatory constants (`effective_date`, `program_code`, `pc_number`) and lookup rates (`country_surtax_rate`, `province_tax_rate`, `base_duty_rate`, `is_steel_derivative`) are `Rule.copy` snapshots from `SysConfig`/`CountryOrigin`/`Province`/`HsCodeRate` — zero hardcoded literals in any formula lambda
- ✅ `duty_paid_value`, `sales_tax_amount`, and `total_tax_due` each correctly use `no_prune=True` with an inline comment explaining why — they depend on `Rule.sum` columns adjusted via child-insert delta, which LogicBank's pruning would otherwise skip re-deriving from
- ✅ `SurtaxLineItem.surtax_applicable` and `SurtaxLineItem.surtax_amount` correctly use live parent-reference formulas (`row.customs_entry.surtax_applicable`, `row.customs_entry.country_surtax_rate`) rather than stale copies, since both depend on entry-level fields that can change after the line item is first created
- ✅ `logic/declare_logic.py` (91 lines) and `logic/logic_discovery/auto_discovery.py` are byte-identical to the `basic_demo_logic_gov` baseline — 0 net new lines, no rules misplaced outside `logic_discovery/`
- ✅ No wildcard imports outside `logic/load_verify_rules.py` (unmodified framework infrastructure)
- ✅ All 6 sqlite table names (country_origin, customs_entry, hs_code_rate, province, surtax_line_item, sys_config) map cleanly to their model class names — no naming mismatches

---

## Action Items

| Priority | Item | Fix |
|---|---|---|
| 🟡 -1 | Missing `__init__.py` at `logic/logic_discovery/` | `touch logic/logic_discovery/__init__.py` |
| 🟡 -5 | 5 unindexed FK columns | `CREATE INDEX` on each FK column listed above (customs_entry.sys_config_id, customs_entry.province_id, customs_entry.country_origin_id, surtax_line_item.hs_code_id, surtax_line_item.customs_entry_id) |

---

## Effective LOC Detail

Total Effective LOC: **93** (vs hardcoded scaffold baselines; `database/models.py` excluded)

| Bucket | LOC | Detail |
|---|---|---|
| logic_discovery/cbsa_steel_surtax.py (new file) | 93 | Full surtax order implementation: 7 copy rules (constants + lookup snapshots), 7 formula rules (3 with `no_prune=True`), 3 sum rules, 1 constraint |

> Baseline reference: `basic_demo_logic_gov` (cross-family reference — no `basic_demo`-family sibling exists for
> `demo_customs_surtax`; `logic/declare_logic.py`=91 lines, byte-identical, 0 net new).
> `logic/logic_discovery/auto_discovery.py` also byte-identical against the same baseline — 0 net new.
> `logic/logic_discovery/use_case.py` (22 lines, empty template) matches the framework pattern — 0 net new.
> `api/api_discovery/*` and `integration/*` contain only standard scaffold files (no project-specific
> additions) — 0 net new.
> All 93 Effective LOC is concentrated in the single new file implementing the CBSA Steel Derivative
> Goods Surtax Order.

**Per-table (logic LOC referencing each table — overlapping by design):**

| Table | LOC | Files |
|---|---|---|
| CustomsEntry | ~60 | cbsa_steel_surtax.py (5 copy rules, 4 formula rules, 3 sum rules — surtax applicability, rollups, duty-paid value, sales tax, total tax due) |
| SurtaxLineItem | ~33 | cbsa_steel_surtax.py (2 copy rules, 3 formula rules, 1 constraint — HS code snapshots, line-level surtax applicability and amounts, customs-value guard) |

> Counts overlap because both tables are declared together in the single `cbsa_steel_surtax.py` file,
> with `SurtaxLineItem.surtax_applicable`/`surtax_amount` reading live from their parent `CustomsEntry`.

---

## Summary

demo_customs_surtax implements the **CBSA Steel Derivative Goods Surtax Order** (PC Number 2025-0917, program code 25267A) — a focused, single-use-case customs project with a 6-table schema (5 domain tables + SysConfig).

**Coverage 7.6** — strong, the highest in the portfolio. Unlike larger customs projects with schemas provisioned ahead of rules, every domain table here is densely covered: 18 declarative rules implement the complete order calculation chain (eligibility → duty → surtax → provincial tax → total) across just 2 transactional tables plus 3 lookup/rate tables, all wired via `Rule.copy`/`Rule.sum`/`Rule.formula`/`Rule.constraint` with zero hardcoded literals.

**Integrity 94** — fair; no correctness bugs found. The 6-point deduction is entirely the standard portfolio-wide pattern: a missing `logic_discovery/__init__.py` (-1) and 5 unindexed FK columns (-5). The project correctly applies the `no_prune=True` pattern (with explanatory comments) for formulas that depend on adjusted `Rule.sum` columns, and correctly uses live parent-reference formulas (not stale copies) for line-item fields that depend on entry-level state that can change after creation.

---

*Generated per `docs/training/health_check.md` v1.7 — Project Health Check / Vital Signs.*
