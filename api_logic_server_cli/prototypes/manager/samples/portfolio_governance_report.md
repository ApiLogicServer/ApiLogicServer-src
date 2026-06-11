# GenAI-Logic Sample Projects — Portfolio Governance Report
**Generated:** 2026-06-11
**Scoring:** Coverage Score (weighted rules / domain tables) + Integrity Score (100 - demerits) + Effective LOC
**Reference:** `docs/training/health_check.md` v1.7 — full scoring guide and appendix

---

## Summary

| Project | Tables | Wtd Rules | Coverage | Integrity | Red Flag | Effective LOC | Profile |
|---|---|---|---|---|---|---|---|
| allocate_dept_account_demo | 10 | 33 | **3.3** | **79** | — | **527** | 🟡 Cascade Allocate (2-level) + AI project matching, well-organized; FK indexes missing schema-wide |
| basic_demo_ai_rules-supplier | 6 | 12 | **2.0** | **93** | — | **337** | 🟢 AI-driven supplier selection (Request Pattern) + check-credit chain, well-organized; FK indexes missing schema-wide |
| basic_demo_eai | 7 | 11 | **1.6** | **94** | — | **454** | 🟢 Clean — rules in logic_discovery, EAI consume/publish wired correctly; FK indexes missing (schema-wide) |
| basic_demo_logic_gov | 3 | 11 | **3.7** | **96** | — | **0** | 🟢 Canonical check-credit reference (5 rules), minimal/clean; FK indexes missing schema-wide |
| basic_demo_sample | 3 | 11 | **3.7** | **90** | — | **307** | 🟡 Canonical check-credit chain + MCP/B2B integration extras; one broken event handler (`OrderShipping` undefined); FK indexes missing schema-wide |
| demo_customs_clvs | 11 | 12 | **1.1** | **89** | — | **481** | 🟠 CLVS eligibility use case (counts + dependency-anchor formulas) + 2-stage Kafka EAI ingestion (isdc); large 13-table customs schema with 9 tables not yet covered by rules; FK indexes missing schema-wide |
| demo_customs_surtax | 5 | 38 | **7.6** | **94** | — | **93** | ✅ CBSA Steel Derivative Goods Surtax Order — single dense logic file (18 rules) covering both transactional tables; FK indexes missing schema-wide |
| nw_sample | 9 | 34 | **3.8** | **83** | — | **782** | 🟠 Rules in declare_logic.py — needs migration; FK indexes missing schema-wide |
| nw_sample_nocust | 16 | 0 | **0.0** | **87** | 🚨 | **0** | ℹ️ Intentionally empty — "new from db" reference; FK indexes missing (schema-wide) |

> **Coverage** = weighted rules / domain tables (sum/count=3, formula/copy=2, constraint=1). Target ≥ 3.0 for mature projects.
> **Integrity** = 100 minus demerits for anti-patterns. Target ≥ 95.
> **Red Flag** = 🚨 if ≥ 10 FK tables and zero sum/count rules — team has evidently not adopted aggregation rules.
> **Effective LOC** = code added beyond the generated scaffold, vs hardcoded baseline LOC per file (see `docs/training/health_check.md` v1.7). Document-only metric — no grade thresholds.
> Tables with ≤ 2 non-PK columns excluded as lookup/junction tables. See `docs/training/governance.md`.

**Key insight:** Coverage reflects *intent* as much as quality. `basic_demo_eai`, `nw_sample_nocust`, and `demo_customs_clvs` are integration- or schema-provisioning-focused — low coverage is expected, not a failure. `demo_customs_surtax` is the reference standard for pure dense business logic: 7.6 coverage on a single 93-line file, 94 integrity. `basic_demo_logic_gov` is the canonical minimal check-credit reference (3.7 coverage, 96 integrity, 0 Effective LOC — the unmodified scaffold baseline used to diff every other project in the portfolio).

Across all 9 projects, the single most common Integrity finding is **unindexed FK columns** — every project shows this finding, scaled to schema size (1 in `basic_demo_logic_gov` up to 8 in `demo_customs_clvs`). This is the highest-leverage portfolio-wide fix: a one-time `CREATE INDEX` pass on every FK column would raise every project's Integrity score by its FK-index deduction alone.

---

## demo_customs_surtax — Coverage 7.6 / Integrity 94 / Effective LOC 93 ✅

**Domain tables (5):** CustomsEntry, SurtaxLineItem, HsCodeRate, Province, CountryOrigin
**Rule inventory:** 7 `Rule.copy` + 7 `Rule.formula` (3 with `no_prune=True`) + 3 `Rule.sum` + 1 `Rule.constraint` = **38 weighted**
**Coverage:** 38 / 5 = **7.6** ✅

**Integrity findings:** -1 missing `logic_discovery/__init__.py`, -5 unindexed FK columns (5 FKs across CustomsEntry/SurtaxLineItem). No correctness bugs — `no_prune=True` and live parent-reference formulas are both used correctly with explanatory comments.

**Effective LOC:** 93 — entirely in `logic_discovery/cbsa_steel_surtax.py` (new file). `declare_logic.py`, `auto_discovery.py`, `use_case.py` all 0 net new vs `basic_demo_logic_gov` baseline.

See `demo_customs_surtax/demo_customs_surtax_governance_report.md` for the full per-project report.

---

## allocate_dept_account_demo — Coverage 3.3 / Integrity 79 / Effective LOC 527

**Domain tables (10):** Charge, ChargeDeptAllocation, ChargeGlAllocation, Department, GlAccount, Project, DeptChargeDefinition, ProjectFundingDefinition, + 2 others
**Rule inventory:** Rule.copy ×2, Rule.formula ×4, Rule.sum ×6, Allocate ×2, Rule.formula (definition_rules) ×2, Rule.sum ×2 = **33 weighted**
**Coverage:** 33 / 10 = **3.3** 🟡

**Integrity findings:** Largest deduction in the portfolio (-21): missing `__init__.py` (-1), `session.query()` ×2 inside `check_active_funding` row_event (-1), and 19 unindexed FK columns (-19, the largest FK-index gap in the portfolio — 16-table schema). Hall passes correctly applied for `allocate-recipients` (×2) and `ai-handler` (project_identification.py).

**Effective LOC:** 527 — cascade Allocate (2-level: Charge → Dept → GL) + AI project-matching logic.

See `allocate_dept_account_demo/allocate_dept_account_demo_governance_report.md` for the full per-project report.

---

## basic_demo_ai_rules-supplier — Coverage 2.0 / Integrity 93 / Effective LOC 337

**Domain tables (6):** Customer, Order, Item, Product, Supplier, ProductSupplier
*(SysSupplierSelection excluded — Sys pattern)*
**Rule inventory:** Rule.copy ×1, Rule.formula ×1, Rule.sum ×2, Rule.count ×1, Rule.constraint ×1 = **12 weighted**
**Coverage:** 12 / 6 = **2.0** 🟡

**Integrity findings:** -7 total — unindexed FK columns plus minor advisories. Hall passes applied: `kafka-publish` (app_integration.py), `ai-handler` (supplier_selection.py), `row-lookup` (check_credit.py).

**Effective LOC:** 337 — AI-driven supplier selection (Request Pattern: SysSupplierReq) + check-credit chain.

See `basic_demo_ai_rules-supplier/basic_demo_ai_rules-supplier_governance_report.md` for the full per-project report.

---

## basic_demo_eai — Coverage 1.6 / Integrity 94 / Effective LOC 454

**Domain tables (7):** Customer, Order, Item, Product, OrderB2bMessage, Employee, + 1 other
**Rule inventory:** Rule.copy ×1, Rule.formula ×1, Rule.sum ×1, Rule.constraint ×1 + EAI wiring = **11 weighted**
**Coverage:** 11 / 7 = **1.6** 🟢

Low-moderate coverage is by design — this project demonstrates EAI/Kafka integration, not domain rule density.

**Integrity findings:** -6 — unindexed FK columns (schema-wide). Hall passes applied: `eai-consumer-bridge` (order_b2b_consume.py), `kafka-publish` (app_integration.py).

**Effective LOC:** 454 — EAI consume/publish pipeline wired correctly on top of the 4 core business rules.

See `basic_demo_eai/basic_demo_eai_governance_report.md` for the full per-project report.

---

## basic_demo_logic_gov — Coverage 3.7 / Integrity 96 / Effective LOC 0 🟢

**Domain tables (3):** Customer, Order, Item
**Rule inventory:** Rule.copy ×1, Rule.formula ×1, Rule.sum ×2, Rule.constraint ×1 = **11 weighted** (canonical check-credit, 5 rules)
**Coverage:** 11 / 3 = **3.7** 🟢

**Integrity findings:** -4 — unindexed FK columns only. No organizational or bug findings — this is the cleanest project in the portfolio.

**Effective LOC:** 0 — this project **is** the baseline. `logic/declare_logic.py` (91 lines) and `logic/logic_discovery/auto_discovery.py` are the reference files every other project's Effective LOC is diffed against.

See `basic_demo_logic_gov/basic_demo_logic_gov_governance_report.md` for the full per-project report.

---

## basic_demo_sample — Coverage 3.7 / Integrity 90 / Effective LOC 307

**Domain tables (3):** Customer, Order, Item
**Rule inventory:** Rule.copy ×1, Rule.formula ×1, Rule.sum ×2, Rule.constraint ×1 = **11 weighted** (Rule.after_flush_row_event = 0)
**Coverage:** 11 / 3 = **3.7** 🟡

**Integrity findings:** -10, including one **correctness bug**: a `Rule.after_flush_row_event` references an undefined `OrderShipping` handler. Hall passes applied: `kafka-publish` (app_integration.py), `eai-consumer-bridge` (mcp_client_executor_request.py).

**Effective LOC:** 307 — canonical check-credit chain plus MCP/B2B integration extras.

See `basic_demo_sample/basic_demo_sample_governance_report.md` for the full per-project report.

---

## demo_customs_clvs — Coverage 1.1 / Integrity 89 / Effective LOC 481

**Domain tables (11):** Customer, CustomsRegion, VirtualRouteLeg, ControlledRegulatedGood, CustomsOffice, Shipment, Piece, ShipmentCommodity, SpecialHandling, ShipmentParty, ShipmentXml
*(SysConfig excluded — Sys pattern; GovtDept excluded — lookup, 2 non-PK cols)*
**Rule inventory:** Rule.count ×2, Rule.formula ×2 = **12 weighted** (4 zero-weight integration events)
**Coverage:** 12 / 11 = **1.1** 🟠

Low coverage reflects a structural reality, not a quality problem: the 13-table schema (144 columns on `Shipment` alone) is provisioned for the full CIMCorp feed, while business rules so far cover only the CLVS eligibility use case + importer matching. 4 of 11 domain tables have no derived/validated columns yet.

**Integrity findings:** -11 — missing `__init__.py`, two `calling=` functions without docstrings, 8 unindexed FK columns. One `@health-check: suppress` annotation correctly honored for an unavoidable full-table HS-code prefix scan.

**Effective LOC:** 481 — CLVS eligibility use case + 2-stage Kafka EAI ingestion pipeline (isdc).

See `demo_customs_clvs/demo_customs_clvs_governance_report.md` for the full per-project report.

---

## nw_sample — Coverage 3.8 / Integrity 83 / Effective LOC 782

**Domain tables (9):** CategoryTableNameTest, Customer, Department, Employee, EmployeeAudit, Order, OrderDetail, Product, Supplier
*(7 lookup/junction tables excluded: CustomerDemographic, Location, Region, Union, EmployeeTerritory, Shipper, Territory)*
**Rule inventory (in `logic/declare_logic.py`):** Rule.sum ×3, Rule.count ×3, Rule.formula ×4, Rule.copy ×1, Rule.constraint ×3 (declare_logic.py) + Rule.constraint ×3 (simple_constraints.py) = **34 weighted**
**Coverage:** 34 / 9 = **3.8** 🟠

Rules are substantial and correct — this predates the discovery pattern. All 24 rules live in `declare_logic.py` rather than `logic/logic_discovery/` files.

**Integrity findings:** -17 — rules in declare_logic.py (-2), two `Rule.after_flush_row_event` on same class (-2), wildcard import (-1), docstring advisory (-1), plus unindexed FK columns (schema-wide). Hall passes applied: `kafka-publish` ×2 (integration.py), `row-lookup` (simple_constraints.py).

**Effective LOC:** 782 — largest in the portfolio, reflecting the pre-discovery rule organization plus integration extras.

**Fix:** Migrate rules from `declare_logic.py` into `logic/logic_discovery/` files grouped by use case (check_credit, product_rules, employee_audit, etc.). `declare_logic.py` becomes a stub calling `pass`.

See `nw_sample/nw_sample_governance_report.md` for the full per-project report.

---

## nw_sample_nocust — Coverage 0.0 / Integrity 87 / Effective LOC 0 🚨

Intentionally empty — no business rules by design. This is the reference "new from database" project: what you get immediately after `genai-logic create`, before any customization.

**Red Flag 🚨:** 16 tables, zero sum/count rules — expected for this project's purpose (not a defect).

**Integrity findings:** -13 — unindexed FK columns across the 16-table schema (no rules to offset).

**Effective LOC:** 0 — unmodified scaffold.

See `nw_sample_nocust/nw_sample_nocust_governance_report.md` for the full per-project report.

---

## Action Items

| Priority | Project | Finding | Fix |
|---|---|---|---|
| 🔴 -21 | allocate_dept_account_demo | Largest Integrity deduction in portfolio — see full report for itemized findings | Review `allocate_dept_account_demo_governance_report.md` Action Items |
| 🔴 -10 | basic_demo_sample | `Rule.after_flush_row_event` references undefined `OrderShipping` handler — correctness bug | Define `OrderShipping` handler or remove the dangling event registration |
| 🟠 -17 | nw_sample | 24 rules declared in `declare_logic.py` instead of `logic/logic_discovery/` | Migrate into use-case-named files (check_credit, product_rules, employee_audit, etc.); `declare_logic.py` becomes a stub |
| 🟠 -11 | demo_customs_clvs | Missing `__init__.py`, 2 undocumented `calling=` functions, 8 unindexed FKs | `touch logic/logic_discovery/__init__.py`; add one-line docstrings; `CREATE INDEX` on each FK |
| 🟡 portfolio-wide | All 9 projects | Unindexed FK columns — present in every project, the most common single finding | One-time `CREATE INDEX` pass on every FK column across all 9 sample databases |
| 🟡 -1 | nw_sample | `integration.py` — wildcard import (`from database.models import *`) | Replace with explicit imports |
| 🟡 -1 | nw_sample | `simple_constraints.py` — docstring advisory note | Remove or move to comment |
