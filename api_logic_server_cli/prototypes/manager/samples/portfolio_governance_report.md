# GenAI-Logic Sample Projects — Portfolio Governance Report
**Generated:** 2026-05-10  
**Scoring:** Coverage Score (weighted rules / domain tables) + Integrity Score (100 - demerits)  
**Reference:** `docs/training/health_check.md` — full scoring guide and appendix

---

## Summary

| Project | Tables | Wtd Rules | Coverage | Integrity | Red Flag | Profile |
|---|---|---|---|---|---|---|
| allocate_dept_account_demo | 12 | 30 | **2.5** | **97** | — | 🟡 Strong coverage, 1 finding |
| basic_demo_ai_rules-supplier | 7 | 12 | **1.7** | **100** | — | 🟡 Thin coverage, exemplary integrity |
| basic_demo_eai | 6 | 5 | **0.8** | **100** | — | 🟠 EAI focus — rules minimal by design |
| basic_demo_sample | 4 | 5 | **1.3** | **100** | — | 🟡 Demo scaffold |
| demo_customs | 7 | 7 | **1.0** | **100** | — | 🟠 Integration focus — rules thin by design |
| demo_customs_cbsa | 5 | 39 | **7.8** | **100** | — | ✅ Exemplary — pure declarative business logic |
| nw_sample | 9 | 34 | **3.8** | **96** | — | 🟠 Rules in declare_logic.py — needs migration |
| nw_sample_nocust | 9 | 0 | **0.0** | n/a | 🚨 | ℹ️ Intentionally empty — "new from db" reference |

> **Coverage** = weighted rules / domain tables (sum/count=3, formula/copy=2, constraint=1). Target ≥ 3.0 for mature projects.  
> **Integrity** = 100 minus demerits for anti-patterns. Target ≥ 95.  
> **Red Flag** = 🚨 if ≥ 10 FK tables and zero sum/count rules — team has evidently not adopted aggregation rules.  
> Tables with ≤ 2 non-PK columns excluded as lookup/junction tables. See `docs/training/governance.md`.

**Key insight:** Coverage reflects *intent* as much as quality. `basic_demo_eai` and `demo_customs` are integration-focused — low coverage is expected, not a failure. `demo_customs_cbsa` is the reference standard for pure business logic: 7.8 coverage, 100 integrity.

---

## demo_customs_cbsa — Coverage 7.8 / Integrity 100 ✅

**Domain tables (5):** CustomsEntry, SurtaxLineItem, HsCodeRate, Province, CountryOrigin  
**Rule inventory:**

| Rule | Type | Weight |
|---|---|---|
| SurtaxLineItem.surtax_applicable | formula | 2 |
| SurtaxLineItem.base_duty_amount | formula | 2 |
| SurtaxLineItem.surtax_amount | formula | 2 |
| CustomsEntry.total_customs_value | sum | 3 |
| CustomsEntry.total_duty_amount | sum | 3 |
| CustomsEntry.total_surtax_amount | sum | 3 |
| CustomsEntry.duty_paid_value | formula | 2 |
| CustomsEntry.sales_tax_amount | formula | 2 |
| CustomsEntry.total_tax_due | formula | 2 |
| CustomsEntry.effective_date | copy | 2 |
| CustomsEntry.program_code | copy | 2 |
| CustomsEntry.pc_number | copy | 2 |
| + 3 more copies (hs_code, province, country) | copy ×3 | 2 each |
| customs_value > 0 | constraint | 1 |
| ship_date required | constraint | 1 |

**Weighted total:** 3 sums×3 + 6 formulas×2 + 8 copies×2 + 2 constraints×1 = 9+12+16+2 = **39**  
**Coverage:** 39 / 5 = **7.8** ✅

**Integrity findings:** None. `effective_date` comparison correctly uses `row.effective_date` (copied from SysConfig) — no hardcoded dates in rules. Date in docstring is verbatim requirement text, not a rule input.  
See `demo_customs_cbsa/demo_customs_cbsa_governance_report.md` for the full per-project report.

---

## allocate_dept_account_demo — Coverage 2.5 / Integrity 97

**Domain tables (12):** Charge, ChargeDeptAllocation, ChargeGlAllocation, Department, GlAccount, Project, DeptChargeDefinition, ProjectFundingDefinition, + 4 others  
**Rule inventory:** Rule.copy ×2, Rule.formula ×4, Rule.sum ×6, Allocate ×2, Rule.formula (definition_rules) ×2, Rule.sum ×2 = **30 weighted**  
**Coverage:** 30 / 12 = **2.5** 🟡

**Integrity findings:**

| | Finding | Points |
|---|---|---|
| 🔴 | `ai_requests/project_identification.py` — multiple `session.query()` calls inside early_row_event AI handler; iterates over results and scores keywords | -3 |
| ✅ | `charge_distribution.py` — `allocate-recipients` functions (return list for Allocate extension) | hall pass |
| ✅ | `ai_requests/project_identification.py` — OpenAI calls present | `ai-handler` hall pass applied; -3 restored |

**Integrity:** 100 - 3 = **97**

**Note:** The session.query() calls in project_identification.py are inside an ai-handler — partial hall pass. The queries are lookups feeding keyword scoring, not aggregations replacing a Rule.count. The -3 stands for the iteration pattern; the ai-handler pass covers the OpenAI calls only.

---

## basic_demo_ai_rules-supplier — Coverage 1.7 / Integrity 100

**Domain tables (7):** Customer, Order, Item, Product, Supplier, ProductSupplier, SysSupplierSelection  
**Rule inventory:** Rule.copy ×1, Rule.formula ×1, Rule.sum ×2, Rule.count ×1, Rule.constraint ×1 = **12 weighted**  
**Coverage:** 12 / 7 = **1.7** 🟡

**Integrity findings:**

| | Finding | Points |
|---|---|---|
| ✅ | `app_integration.py` — `send_row_to_kafka` call | `kafka-publish` hall pass |
| ✅ | `supplier_selection.py` — OpenAI API calls, JSON parse, fallback | `ai-handler` hall pass |
| ✅ | `check_credit.py` — `session.query` for supplier FK lookup (single `.filter_by().first()`) | `row-lookup` hall pass |

**Integrity:** 100 — no demerits. **100** ✅

---

## basic_demo_eai — Coverage 0.8 / Integrity 100

**Domain tables (6):** Customer, Order, Item, Product, OrderB2bMessage, Employee  
**Rule inventory:** Rule.copy ×1, Rule.formula ×1, Rule.sum ×1, Rule.constraint ×1 = **5 weighted** (business logic only; EAI wiring = 0)  
**Coverage:** 5 / 6 = **0.8** 🟠

Low coverage is by design — this project demonstrates EAI/Kafka integration, not domain rule density. The 4 business rules on Customer/Order/Item are correct; the EAI pipeline is the focus.

**Integrity findings:**

| | Finding | Points |
|---|---|---|
| ✅ | `order_b2b_consume.py` — `is_processed` guard + publish | `eai-consumer-bridge` hall pass |
| ✅ | `app_integration.py` — `send_row_to_kafka` | `kafka-publish` hall pass |

**Integrity:** 100 — no demerits. **100** ✅

---

## basic_demo_sample — Coverage 1.3 / Integrity 100

**Domain tables (4):** Customer, Order, Item, Product  
**Rule inventory:** Rule.copy ×1, Rule.formula ×1, Rule.sum ×2, Rule.constraint ×1 = **5 weighted** (Rule.after_flush_row_event = 0)  
**Coverage:** 5 / 4 = **1.3** 🟡

**Integrity findings:**

| | Finding | Points |
|---|---|---|
| ✅ | `app_integration.py` — `send_row_to_kafka` | `kafka-publish` hall pass |
| ✅ | `mcp_client_executor_request.py` — MCP event handler | `eai-consumer-bridge` hall pass |

**Integrity:** 100 — no demerits. **100** ✅

---

## demo_customs — Coverage 1.0 / Integrity 100

**Domain tables (7):** Shipment, ShipmentCommodity, ShipmentParty, CcpCustomer, Piece, SpecialHandling, VirtualRouteLeg  
*(ShipmentXml excluded — blob/staging infrastructure table; SysConfig excluded — Sys pattern)*  
**Rule inventory:** Rule.count ×1, Rule.formula ×2 = **7 weighted** (events = 0)  
**Coverage:** 7 / 7 = **1.0** 🟠

Low coverage reflects integration focus — ISDC XML consume + CLVS eligibility + shipment matching. The rules that exist are correct and well-structured.

**Integrity findings:** None. All patterns correct.

| | Finding | Points |
|---|---|---|
| ✅ | `shipment_matching.py` — single `session.query().filter_by().first()` | `row-lookup` hall pass |
| ✅ | `isdc_consume.py` — `is_processed` guard + publish | `eai-consumer-bridge` hall pass |

**Integrity:** 100

See `demo_customs/demo_customs_governance_report.md` for the full per-project report.

---

## nw_sample — Coverage 3.8 / Integrity 96

**Domain tables (9):** CategoryTableNameTest, Customer, Department, Employee, EmployeeAudit, Order, OrderDetail, Product, Supplier  
*(7 lookup/junction tables excluded: CustomerDemographic(1), Location(1), Region(1), Union(1), EmployeeTerritory(2), Shipper(2), Territory(2))*  
**Rule inventory (in `logic/declare_logic.py`):** Rule.sum ×3, Rule.count ×3, Rule.formula ×4, Rule.copy ×1, Rule.constraint ×3 (declare_logic.py) + Rule.constraint ×3 (simple_constraints.py) = **34 weighted**  
**Coverage:** 34 / 9 = **3.8** 🟡

Rules are substantial and correct — this predates the discovery pattern. All 24 rules live in `declare_logic.py` rather than `logic/logic_discovery/` files. The logic files (`simple_constraints.py`, `integration.py`) exist but contain only integration examples and stubs.

**Integrity findings:**

| | Finding | Points |
|---|---|---|
| 🔴 | `logic/declare_logic.py` — 24 rules declared here instead of logic_discovery/ files | -2 |
| ✅ | `integration.py` — `send_kafka_message` calls | `kafka-publish` hall pass |
| ✅ | `integration.py` — n8n webhook calls | `kafka-publish` hall pass (external I/O) |
| 🟡 | `integration.py` — two `Rule.after_flush_row_event` on same class (Customer) | -2 |
| 🟡 | `integration.py` — `from database.models import *` wildcard import | -1 |
| 🟡 | `simple_constraints.py` — docstring advisory note, not requirement text | -1 |
| ✅ | `simple_constraints.py:30` — single `.filter_by().first()` lookup | `row-lookup` hall pass |

**Integrity:** 100 - 2 - 2 - 1 - 1 = **96**

**Fix:** Migrate rules from `declare_logic.py` into `logic/logic_discovery/` files grouped by use case (check_credit, product_rules, employee_audit, etc.). `declare_logic.py` becomes a stub calling `pass`.

---

## nw_sample_nocust — Coverage n/a / Integrity n/a ℹ️

Intentionally empty — no business rules by design. This is the reference "new from database" project: what you get immediately after `genai-logic create`, before any customization. Not scored; exists to show the baseline.

---

## Action Items

| Priority | Project | Finding | Fix |
|---|---|---|---|
| 🔴 -3 | allocate_dept_account_demo | `project_identification.py` — session.query iteration in AI handler | Consider Rule.count + formula for scoring; keep AI call for matching |
| 🔴 -3 | demo_customs | `shipment_matching.py` — session.query iterates CcpCustomer rows | Refactor to single lookup or Rule.count |
| 🟡 advisory | demo_customs | `clvs_eligibility.py` — row.attr refs hidden in helper | Reference `row.prohibited_commodity_count` directly in `_clvs_eligible` |
| 🟡 -2 | nw_sample | `integration.py` — two events on same Customer class | Consolidate into one event handler |
| 🟡 -1 | nw_sample | `integration.py` — wildcard import | Replace with explicit imports |
| 🟡 -1 | nw_sample | `simple_constraints.py` — docstring note | Remove or move to comment |
