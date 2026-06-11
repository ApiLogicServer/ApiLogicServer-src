---
generated: 2026-06-10
generated_by: claude-sonnet-4-6 (valjhuber@gmail.com)
tool: docs/training/health_check.md v1.4
---

## 🩺 Project Governance Report — demo_customs_surtax

## Summary

| Project | Tables | Wtd Rules | Coverage | Integrity | Red Flag | Profile |
|---|---|---|---|---|---|---|
| demo_customs_surtax | 5 | 36 | **7.2** | **94** | — | 🟡 Strong coverage, 6 findings |

> **Coverage** = weighted rules / domain tables (sum/count=3, formula/copy=2, constraint=1). Target ≥ 3.0 for mature projects.
> **Integrity** = 100 minus demerits for anti-patterns: broken dependency tracking, procedural aggregates replacing rules, events that should be rules, and schema gaps (no PK, unindexed FKs). Target ≥ 95.
> **Red Flag** = 🚨 if ≥ 10 FK tables and zero sum/count rules — team has evidently not adopted aggregation rules.
> See `docs/training/governance.md` for full scoring guide.

**Coverage Score: 7.2**  (36 weighted rules / 5 tables)   ✅ Strong
**Integrity Score: 94**  (6 demerits, 0 reviewed)
**Red Flag: none**  (3 aggregation rules, 5 FK tables)

────────────────────────────────────────
COVERAGE DETAIL

  Tables:
    CustomsEntry    — 7 rules (1 formula, 3 sum, 3 formula[no_prune])
    SurtaxLineItem  — 6 rules (2 copy, 3 formula, 1 constraint)
    CountryOrigin   — 0 rules (lookup, referenced via copy)
    Province        — 0 rules (lookup, referenced via copy)
    HsCodeRate      — 0 rules (lookup, referenced via copy)

  Rules:  3× sum, 6× formula (3 with no_prune=True), 7× copy, 1× constraint
  = 17 total rule declarations, 36 weighted

────────────────────────────────────────
INTEGRITY FINDINGS

  🟡 -1  logic/logic_discovery/cbsa_steel_surtax.py:6-19
         docstring hygiene violation — the declare_logic() docstring restates the
         requirement in the AI's own words, with an invented numbered eligibility
         list ("Surtax applies only when: ... AND ... AND ..."). This goes beyond
         the verbatim CBSA Steel Derivative Goods Surtax Order requirement text.
         → Fix: replace with the verbatim requirement text only (no paraphrase,
           no derived eligibility breakdown). If the verbatim source text isn't
           available, pull it from docs/requirements/<use_case>/requirements.md.

  🟡 -1  database/models.py: CustomsEntry.country_origin_id
         FK column 'country_origin_id' on 'customs_entry' has no covering index
         (only sqlite_autoindex_customs_entry_1, which covers entry_number, a
         unique constraint — unrelated to this FK).
         → Fix: CREATE INDEX ix_customs_entry_country_origin_id ON customs_entry(country_origin_id)

  🟡 -1  database/models.py: CustomsEntry.province_id
         FK column 'province_id' on 'customs_entry' has no covering index.
         → Fix: CREATE INDEX ix_customs_entry_province_id ON customs_entry(province_id)

  🟡 -1  database/models.py: CustomsEntry.sys_config_id
         FK column 'sys_config_id' on 'customs_entry' has no covering index.
         → Fix: CREATE INDEX ix_customs_entry_sys_config_id ON customs_entry(sys_config_id)

  🟡 -1  database/models.py: SurtaxLineItem.customs_entry_id
         FK column 'customs_entry_id' on 'surtax_line_item' has no covering index.
         This is the busiest join in the schema — every CustomsEntry rollup
         (Rule.sum total_customs_value/total_duty_amount/total_surtax_amount)
         scans surtax_line_item by this column.
         → Fix: CREATE INDEX ix_surtax_line_item_customs_entry_id ON surtax_line_item(customs_entry_id)

  🟡 -1  database/models.py: SurtaxLineItem.hs_code_id
         FK column 'hs_code_id' on 'surtax_line_item' has no covering index.
         → Fix: CREATE INDEX ix_surtax_line_item_hs_code_id ON surtax_line_item(hs_code_id)

  ✅  +0  Primary keys — all 5 mapped tables (country_origin, hs_code_rate, province,
         customs_entry, surtax_line_item) have a single-column integer PK ('id').
         No finding.

────────────────────────────────────────
6 findings need attention. Want me to fix them?

────────────────────────────────────────
NOTES (not scored, but worth tracking)

- **Missing copy-vs-formula TODO block.** `logic_bank_api.md` calls for one TODO
  comment per file at the top of `declare_logic()` flagging the copy-vs-formula
  choice for review. This file has 7 `Rule.copy` calls (rates/dates snapshotted
  from SysConfig and lookup tables) with no such comment. Not a scored demerit
  in health_check.md v1.3, but worth adding for consistency with the convention
  and to prompt a deliberate "snapshot vs live" review of each copy.

- **`country_surtax_rate` snapshot vs. live reference.** `CustomsEntry.country_surtax_rate`
  and `SurtaxLineItem.base_duty_rate`/`is_steel_derivative` are `Rule.copy` (snapshots
  at entry time) — correct per the "lock value at transaction time" default. If
  CountryOrigin/HsCodeRate rates are later corrected retroactively, existing entries
  will NOT recompute. This is almost certainly the right call for a regulatory/customs
  domain (you don't want a rate correction next month to silently re-price last
  month's filings) — flagging only so it's a documented decision, not an oversight.

- **Unindexed FKs are a "before you scale" item, not a "fix today" item.** At seed-data
  volumes (a handful of rows per table) these 5 missing indexes are invisible. They
  matter once `customs_entry`/`surtax_line_item` grow into the thousands — particularly
  `surtax_line_item.customs_entry_id`, since the 3 `Rule.sum` rollups on `CustomsEntry`
  re-scan that table on every line-item insert/update/delete. Cheap to fix now (5
  one-line `CREATE INDEX` statements + rebuild-from-database), more annoying to
  retrofit once there's data and a running system to avoid locking.

- **Other schema-level constraints (`unique=True`, `nullable`, etc.) remain out of
  scope.** STEP 2b (v1.4) added PK and FK-index checks specifically. It does NOT check
  uniqueness constraints, nullability, or check constraints on `database/models.py`
  columns. If those matter for this project, they need a separate schema review —
  see the editorial notes for one specific example (`country_code`/`hs_code` lost
  their `unique=True` vs. the reference implementation).
