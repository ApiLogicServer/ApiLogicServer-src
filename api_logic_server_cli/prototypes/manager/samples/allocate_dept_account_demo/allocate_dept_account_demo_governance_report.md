# 🩺 allocate_dept_account_demo — Project Governance Report
**Date:** 2026-06-11
**Scoring:** Coverage Score (weighted rules / domain tables) + Integrity Score (100 - demerits) + Effective LOC
**Reference:** `docs/training/health_check.md`

---

## Summary

| Project | Tables | Wtd Rules | Coverage | Integrity | Red Flag | Effective LOC | Profile |
|---|---|---|---|---|---|---|---|
| allocate_dept_account_demo | 10 | 33 | **3.3** | **79** | — | **527** | 🟡 Cascade Allocate (2-level) + AI project matching, well-organized; FK indexes missing schema-wide |

> **Coverage** = weighted rules / domain tables (sum/count=3, formula/copy=2, constraint=1). Target ≥ 3.0 for mature projects.
> **Integrity** = 100 minus demerits for anti-patterns: broken dependency tracking, procedural aggregates replacing rules, events that should be rules. Target ≥ 95.
> **Red Flag** = 🚨 if ≥ 10 FK tables and zero sum/count rules — team has evidently not adopted aggregation rules.
> **Effective LOC** = code added beyond the generated scaffold, vs hardcoded baseline LOC per file (see `docs/training/health_check.md` v1.7).
> See `docs/training/governance.md` for full scoring guide.

---

## Scores

| Metric | Value | Grade |
|---|---|---|
| **Coverage Score** | **3.3** (33 pts / 10 domain tables) | 🟡 Moderate |
| **Integrity Score** | **79** (21 points deducted) | 🟠 Poor |
| **Effective LOC** | **527** | — |

---

## Coverage Detail

**Domain tables (10):** ProjectFundingDefinition, DeptChargeDefinition, GlAccount, Project, Charge, DeptChargeDefinitionLine, ProjectFundingLine, SysProjectReq, ChargeDeptAllocation, ChargeGlAllocation

**Excluded — system (1):** SysConfig (settings table)
**Excluded — lookup (2):** Contractor (2 non-PK cols: name, notes), Department (2 non-PK cols: name, notes)
*(lookup threshold: ≤ 2 non-PK columns)*

**Rule inventory:**

| Rule | File | Type | Weight |
|---|---|---|---|
| ChargeDeptAllocation.percent copied from ProjectFundingLine.percent | charge_distribution.py | copy | 2 |
| ChargeDeptAllocation.amount = charge.amount × percent / 100 | charge_distribution.py | formula | 2 |
| Charge.total_distributed_amount = sum(ChargeDeptAllocation.amount) | charge_distribution.py | sum | 3 |
| Project.total_charges = sum(Charge.amount) | charge_distribution.py | sum | 3 |
| ChargeGlAllocation.percent copied from DeptChargeDefinitionLine.percent | charge_distribution.py | copy | 2 |
| ChargeGlAllocation.amount = dept_alloc.amount × percent / 100 | charge_distribution.py | formula | 2 |
| GlAccount.total_allocated = sum(ChargeGlAllocation.amount) | charge_distribution.py | sum | 3 |
| Allocate: Charge → ChargeDeptAllocation (Level 1, percent-based cascade) | charge_distribution.py | allocate | 3 |
| Allocate: ChargeDeptAllocation → ChargeGlAllocation (Level 2, percent-based cascade) | charge_distribution.py | allocate | 3 |
| DeptChargeDefinition.total_percent = sum(DeptChargeDefinitionLine.percent) | definition_rules.py | sum | 3 |
| DeptChargeDefinition.is_active = 1 if total_percent == 100 | definition_rules.py | formula | 2 |
| ProjectFundingDefinition.total_percent = sum(ProjectFundingLine.percent) | definition_rules.py | sum | 3 |
| ProjectFundingDefinition.is_active = 1 if total_percent == 100 | definition_rules.py | formula | 2 |
| AI project identification (early_row_event, OpenAI fuzzy match) | ai_requests/project_identification.py | event | 0 |
| Charge: project must have active funding definition | charge_distribution.py | event | 0 |
| Charge: identify_project_for_charge (registers AI handler before Allocate) | charge_distribution.py | event | 0 |

**Weighted total:** 5×sum(3) + 6×formula/copy(2) + 2×allocate(3) = 15 + 12 + 6 = **33**
*(5 sum: Charge.total_distributed_amount, Project.total_charges, GlAccount.total_allocated, DeptChargeDefinition.total_percent, ProjectFundingDefinition.total_percent — 6 formula/copy: 2 copy + 4 formula — 2 allocate: cascade levels 1 and 2)*
**Coverage:** 33 / 10 = **3.3**

> Allocate declarations are weighted as 3 (equivalent to `Rule.sum`) — each one replaces a
> multi-path "create and maintain child allocation rows" pattern across insert/update/delete,
> per `docs/training/allocate.md`.

---

## Integrity Findings

| | File | Line | Finding | Points |
|---|---|---|---|---|
| 🟡 | logic/logic_discovery/ | — | Missing `__init__.py` | **-1** |
| 🟡 | logic/logic_discovery/charge_distribution.py | 148, 158 | `session.query()` (×2, Project + ProjectFundingDefinition) inside `check_active_funding` row_event — not a single `row-lookup` | **-1** |
| 🟡 | database/db.sqlite | — | charge.contractor_id → contractor — no covering index | **-1** |
| 🟡 | database/db.sqlite | — | charge.project_id → project — no covering index | **-1** |
| 🟡 | database/db.sqlite | — | gl_account.department_id → department — no covering index | **-1** |
| 🟡 | database/db.sqlite | — | charge_dept_allocation.dept_charge_definition_id → dept_charge_definition — no covering index | **-1** |
| 🟡 | database/db.sqlite | — | charge_dept_allocation.department_id → department — no covering index | **-1** |
| 🟡 | database/db.sqlite | — | charge_dept_allocation.project_funding_line_id → project_funding_line — no covering index | **-1** |
| 🟡 | database/db.sqlite | — | charge_dept_allocation.charge_id → charge — no covering index | **-1** |
| 🟡 | database/db.sqlite | — | project.project_funding_definition_id → project_funding_definition — no covering index | **-1** |
| 🟡 | database/db.sqlite | — | charge_gl_allocation.gl_account_id → gl_account — no covering index | **-1** |
| 🟡 | database/db.sqlite | — | charge_gl_allocation.dept_charge_definition_line_id → dept_charge_definition_line — no covering index | **-1** |
| 🟡 | database/db.sqlite | — | charge_gl_allocation.charge_dept_allocation_id → charge_dept_allocation — no covering index | **-1** |
| 🟡 | database/db.sqlite | — | project_funding_line.dept_charge_definition_id → dept_charge_definition — no covering index | **-1** |
| 🟡 | database/db.sqlite | — | project_funding_line.department_id → department — no covering index | **-1** |
| 🟡 | database/db.sqlite | — | project_funding_line.project_funding_definition_id → project_funding_definition — no covering index | **-1** |
| 🟡 | database/db.sqlite | — | dept_charge_definition.department_id → department — no covering index | **-1** |
| 🟡 | database/db.sqlite | — | sys_project_req.matched_project_id → project — no covering index | **-1** |
| 🟡 | database/db.sqlite | — | sys_project_req.contractor_id → contractor — no covering index | **-1** |
| 🟡 | database/db.sqlite | — | dept_charge_definition_line.gl_account_id → gl_account — no covering index | **-1** |
| 🟡 | database/db.sqlite | — | dept_charge_definition_line.dept_charge_definition_id → dept_charge_definition — no covering index | **-1** |

**Integrity:** 100 - 1 - 1 - (19 × 1) = **79**

### Schema Check — Primary Keys

All 13 mapped tables have a primary key. **No findings.**

### Hall Passes Applied

| | File | Function | Pattern |
|---|---|---|---|
| ✅ | charge_distribution.py | `funding_lines_for_charge` | `allocate-recipients` — returns list, wired as `recipients=` |
| ✅ | charge_distribution.py | `charge_def_lines_for_dept_allocation` | `allocate-recipients` — returns list, wired as `recipients=` |
| ✅ | ai_requests/project_identification.py | `_identify_project` | `ai-handler` — calls OpenAI for fuzzy project matching |

### What's Clean

- ✅ Cascade two-level Allocate (Charge → ChargeDeptAllocation → ChargeGlAllocation) implemented per `docs/training/allocate.md` Variant C
- ✅ Custom allocators pre-compute `percent`/`amount` before insert so downstream Rule.copy/Rule.formula and Level-2 Allocate read correct values
- ✅ All `as_expression=lambda row: ...` formulas reference `row.attr` directly — no helper-function wrapping, dependency tracking intact
- ✅ AI handler (`project_identification.py`) follows the Request Pattern (SysProjectReq with audit fields `request`, `created_on`)
- ✅ Rules organized by use case in `logic/logic_discovery/` (charge_distribution.py, definition_rules.py, ai_requests/)
- ✅ No wildcard imports in any logic_discovery file (the `from database.models import *` in `logic/load_verify_rules.py` is unmodified framework infrastructure, not project logic)
- ✅ `declare_logic.py` contains only framework boilerplate — no project rules misplaced there

---

## Action Items

| Priority | Item | Fix |
|---|---|---|
| 🟡 -1 | Missing `__init__.py` | `touch logic/logic_discovery/__init__.py` |
| 🟡 -1 | `session.query()` ×2 in `check_active_funding` row_event | Acceptable as-is (multi-table active-funding check is awkward as a single `Rule.constraint` lambda); alternatively add `@health-check: reviewed` with pattern note, or refactor to `Rule.constraint(as_condition=lambda row: row.project.project_funding_definition.is_active == 1, ...)` using parent-chain references |
| 🟡 -19 | 19 unindexed FK columns | `CREATE INDEX` on each FK column listed above — concentrated in the 3 allocation/junction tables (charge_dept_allocation, charge_gl_allocation, project_funding_line) which are the highest-write-volume tables in this schema |

---

## Effective LOC Detail

Total Effective LOC: **527** (vs hardcoded scaffold baselines; `database/models.py` excluded)

| Bucket | LOC | Detail |
|---|---|---|
| logic_discovery (new files) | 517 | charge_distribution.py=240, ai_requests/project_identification.py=235, definition_rules.py=42 (auto_discovery.py matches baseline → 0; ai_requests/__init__.py=0) |
| logic_discovery (use_case.py growth) | 10 | 32 lines vs baseline 22 (template-version scaffold variation, not hand-written logic) |

> No new files in `api/api_discovery/` or `integration/` — all Effective LOC is concentrated
> in `logic/logic_discovery/`. `security/declare_security.py` (48 lines) and
> `logic/declare_logic.py` (83 lines) are both ≤ their respective scaffold baselines → 0.

**Per-table (logic_discovery LOC referencing each table — overlapping by design):**

| Table | LOC |
|---|---|
| Charge | ~290 (charge_distribution.py + project_identification.py) |
| ChargeDeptAllocation | ~150 |
| ChargeGlAllocation | ~110 |
| Project / ProjectFundingDefinition / ProjectFundingLine | ~180 (definition_rules.py + project lookups in project_identification.py) |
| DeptChargeDefinition / DeptChargeDefinitionLine | ~70 (definition_rules.py) |
| SysProjectReq | ~100 (project_identification.py) |
| GlAccount | ~30 |

> Counts overlap because `charge_distribution.py` and `project_identification.py` each
> reference multiple tables in the cascade chain — see `docs/requirements/logic_flow_allocate_dept_account_demo.md`
> for the full per-table rule trace.

---

## Summary

allocate_dept_account_demo is a **well-organized, sophisticated cascade-allocation sample** — 13 weighted rules (33 pts) implementing a true two-level Allocate pattern (Charge → Dept → GL Account), plus an AI-driven project-matching handler using the Request Pattern. Logic is correctly split by use case (`charge_distribution.py`, `definition_rules.py`, `ai_requests/project_identification.py`), with no dependency-tracking bugs and no rules misplaced in `declare_logic.py`.

**Coverage 3.3** — moderate-to-strong; reflects substantial aggregation/allocation logic across a 10-table domain. Allocate declarations counted as sum-equivalent (weight 3) given they replace multi-path child-row creation/maintenance.
**Integrity 79** — poor, almost entirely driven by 19 unindexed FK columns across the 3 allocation/junction tables (a schema-wide `rebuild-from-database` pattern, not specific to this project's logic) plus 2 minor housekeeping items (missing `__init__.py`, dual session.query() in one constraint-style row_event).
**Effective LOC 527** — concentrated entirely in `logic/logic_discovery/`: 240 lines for the cascade Allocate implementation, 235 lines for the AI project-matching handler, and 42 lines for definition-table sum/formula rules.
