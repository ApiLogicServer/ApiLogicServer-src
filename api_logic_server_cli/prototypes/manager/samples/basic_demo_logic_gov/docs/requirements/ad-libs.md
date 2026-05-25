# basic_demo — Ad-Libs Report

**0 items need your review. 2 FYIs — standard patterns, no action needed.**

---

### 🟢 Diagnostic Appendix

#### Pre-Coding Analysis

**Phase 1 — Schema Impact Assessment**  
Files read: `samples/prompts/genai_demo.prompt`, `database/models.py` (starter.sqlite — only SysConfig)

| Step | Signal |
|---|---|
| Check Credit (5 rules) | Rule.sum (Customer.balance, Order.amount_total) + Rule.formula (Item.amount) + Rule.copy (Item.unit_price) + Rule.constraint — all require derived columns |
| App Integration | after_flush_row_event only — no schema change |

DDL change list:

| Table | Change | Reason |
|---|---|---|
| `customer` | CREATE TABLE | Domain entity with balance (sum-derived) |
| `product` | CREATE TABLE | Lookup entity providing unit_price |
| `order` | CREATE TABLE | Header with amount_total (sum-derived), date_shipped, notes |
| `item` | CREATE TABLE | Line item with unit_price (copy-derived) and amount (formula-derived) |

**Phase 2 — CE / Pattern Assessment**  
Files read: `logic_bank_api.md`, `implement_requirements.md`, `logic_bank_patterns.md`

| Step | Rule Plan |
|---|---|
| Check Credit | Rule.copy(Item.unit_price) + Rule.formula(Item.amount) + Rule.sum(Order.amount_total) + Rule.sum(Customer.balance where date_shipped is None) + Rule.constraint(Customer.balance <= credit_limit) |
| App Integration | Rule.after_flush_row_event(Order, kafka, if date_shipped is not None) |

Anti-patterns confirmed clear:
- [x] No parent flag where Rule.count on child table is correct
- [x] No `as_expression=lambda row: my_func(row)` — all lambdas reference row.attr directly
- [x] No `session.query()` inside formula or row_event
- [x] EAI: N/A (publish only, no consume)

**Implementation Plan:**

| Step | What was planned |
|---|---|
| 1 | DDL — create customer, product, order, item tables with derived columns |
| 2 | rebuild-from-database — regenerate models.py |
| 3 | Write check_credit.py — 5 declarative rules |
| 4 | Write app_integration.py — Kafka after_flush_row_event |
| 5 | Seed data via alp_init.py — verify LogicBank fires on insert |

---

#### Execution Metrics

| Metric | Value |
|---|---|
| Strategy Used | DDL-first, then rebuild-from-database, then logic files, then seed |
| CE Files Loaded | implement_requirements.md, logic_bank_api.md, logic_bank_patterns.md |
| Schema Read First | Yes — models.py verified after rebuild before writing logic |
| Sample Data Read | N/A — no inbound message formats |
| Subagent Used | No — single pass |
| Self-Verification | Yes — alp_init.py run, logic trace confirmed all 5 rules fired |
| Lightweight Checks Used | Yes — logic trace from alp_init.py output |
| Gate Test Run Count | 1 — seed script as verification |
| Gate Test Purpose | Final verification |
| Error Correction Loops | 1 — sys.path fix on alp_init.py (missing project root on path) |
| Long-Run Diagnostics | None |

**Error Correction Loops:**

```
Loop 1:
  Symptom:   ModuleNotFoundError: No module named 'config' when running alp_init.py
  Diagnosis: sys.path.insert(0, project_root) was missing; imports ran before path was set
  Fix:       Added sys.path.insert(0, Path(__file__).parent.parent.parent) before all imports
  Time:      ~2 min
  Root cause type: CE gap (alp_init.py template did not include path fix at line 1)
```

---

### 🔴 Review Required

None — all decisions were specified or followed standard patterns.

---

### 🟡 FYI

- `logic/logic_discovery/place_order/check_credit.py:1` — `sys_config` table retained from starter.sqlite; no domain columns added (prompt had no rates/thresholds requiring SysConfig wiring)
- `database/test_data/alp_init.py:3-5` — added `sys.path.insert(0, project_root)` before imports; this fix should be in the alp_init.py template
