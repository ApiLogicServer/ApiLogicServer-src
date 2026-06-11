# 🩺 basic_demo_sample — Project Governance Report
**Date:** 2026-06-11
**Scoring:** Coverage Score (weighted rules / domain tables) + Integrity Score (100 - demerits) + Effective LOC
**Reference:** `docs/training/health_check.md`

---

## Summary

| Project | Tables | Wtd Rules | Coverage | Integrity | Red Flag | Effective LOC | Profile |
|---|---|---|---|---|---|---|---|
| basic_demo_sample | 3 | 11 | **3.7** | **90** | — | **307** | 🟡 Canonical check-credit chain + MCP/B2B integration extras; one broken event handler (`OrderShipping` undefined); FK indexes missing schema-wide |

> **Coverage** = weighted rules / domain tables (sum/count=3, formula/copy=2, constraint=1). Target ≥ 3.0 for mature projects.
> **Integrity** = 100 minus demerits for anti-patterns: broken dependency tracking, procedural aggregates replacing rules, events that should be rules. Target ≥ 95.
> **Red Flag** = 🚨 if ≥ 10 FK tables and zero sum/count rules — team has evidently not adopted aggregation rules.
> **Effective LOC** = code added beyond the generated scaffold, vs hardcoded baseline LOC per file (see `docs/training/health_check.md` v1.7).
> See `docs/training/governance.md` for full scoring guide.

---

## Scores

| Metric | Value | Grade |
|---|---|---|
| **Coverage Score** | **3.7** (11 pts / 3 domain tables) | 🟡 Moderate-to-Strong |
| **Integrity Score** | **90** (10 points deducted) | 🟡 Fair |
| **Effective LOC** | **307** | — |

---

## Coverage Detail

**Domain tables (3):** Customer, Order, Item

**Excluded — system (2):** SysEmail (begins with "Sys" — email request/log table, no active rule wiring found), SysMcp (begins with "Sys" — MCP request table, separate `__bind_key__='mcp'` database)
**Excluded — lookup (1):** Product (2 non-PK cols: name, unit_price — referenced as `Rule.copy` source only)
*(lookup threshold: ≤ 2 non-PK columns)*

**Rule inventory:**

| Rule | File | Type | Weight |
|---|---|---|---|
| Customer.balance ≤ credit_limit | check_credit.py | constraint | 1 |
| Customer.balance = sum(Order.amount_total where date_shipped is null) | check_credit.py | sum | 3 |
| Order.amount_total = sum(Item.amount) | check_credit.py | sum | 3 |
| Item.amount = quantity × unit_price | check_credit.py | formula | 2 |
| Item.unit_price copied from Product.unit_price | check_credit.py | copy | 2 |
| Order → Kafka topic `order_shipping` if date_shipped is not None | app_integration.py | event | 0 |
| Order → Kafka "Sending Order to Shipping" via `send_order_to_shipping` (after_flush_row_event, on every insert) | declare_logic.py | event | 0 |
| SysMcp insert → MCP client executor (Request Pattern) | mcp_client_executor_request.py | event | 0 |

**Weighted total:** 2×sum(3) + 1×formula(2) + 1×copy(2) + 1×constraint(1) = 6 + 2 + 2 + 1 = **11**
**Coverage:** 11 / 3 = **3.7**

---

## Integrity Findings

| | File | Finding | Points |
|---|---|---|---|
| 🟡 | logic/logic_discovery/ | Missing `__init__.py` (root level) | **-1** |
| 🟡 | logic/logic_discovery/place_order/ | Missing `__init__.py` | **-1** |
| 🔴 | logic/declare_logic.py:61 | `send_order_to_shipping` references `OrderShipping` (RowDictMapper) which is never imported or defined — `NameError` on every Order insert that reaches this handler | **-2** |
| 🟠 | logic/declare_logic.py:47-66 | `send_order_to_shipping` event handler (33 lines) placed in `declare_logic.py` instead of a `logic/logic_discovery/` use-case file | **-2** |
| 🟡 | database/db.sqlite | item.product_id → product — no covering index | **-1** |
| 🟡 | database/db.sqlite | item.order_id → order — no covering index | **-1** |
| 🟡 | database/db.sqlite | order.customer_id → customer — no covering index | **-1** |
| 🟡 | database/db.sqlite | sysemail.customer_id → customer — no covering index | **-1** |

**Integrity:** 100 - 1 - 1 - 2 - 2 - (4 × 1) = **90**

### Schema Check — Primary Keys

All 5 mapped tables (customer, order, item, product, sysemail) have a primary key. `sys_mcp` (separate `mcp` bind, `database/mcp_models.py`) also has a primary key (`id`). **No findings.**

### Hall Passes Applied

| | File | Function | Pattern |
|---|---|---|---|
| ✅ | place_order/app_integration.py | `kafka_producer.send_row_to_kafka` (after_flush_row_event) | `kafka-publish` — built-in framework function, conditional on `date_shipped` |
| ✅ | logic/logic_discovery/mcp_client_executor_request.py | `mcp_client_executor_event` (row_event on SysMcp) | `eai-consumer-bridge` / Request Pattern — has docstring, calls `mcp_client_executor.mcp_client_executor(row.request)` |

### What's Clean

- ✅ No `session.query()` anywhere in `logic/logic_discovery/`
- ✅ No wildcard imports in `logic/logic_discovery/` files (the `from database.models import *` in `logic/load_verify_rules.py` is unmodified framework infrastructure)
- ✅ All formula/copy lambdas reference `row.attr` directly — dependency tracking intact for the check-credit chain
- ✅ `mcp_client_executor_request.py` correctly implements the Request Pattern: `Rule.row_event(on_class=SysMcp, calling=mcp_client_executor_event)`, with full docstring including a curl test example
- ✅ `check_credit.py` (31 lines) and `app_integration.py` (23 lines) implement the same 5+1 rule chain as `basic_demo_logic_gov`, with fuller docstrings (procedural-vs-declarative comparison commentary)
- ✅ B2B integration (`order_b2b_service.py` + `OrderB2BMapper.py`) and MCP exposure (`mcp_expose_api_models.py`) follow documented framework patterns for custom API discovery

---

## Action Items

| Priority | Item | Fix |
|---|---|---|
| 🔴 -2 | `OrderShipping` undefined in `logic/declare_logic.py:61` — `send_order_to_shipping` will raise `NameError` on the first Order insert | Either import the `OrderShipping` RowDictMapper (if one exists/is intended) or remove this Python-customization-example block — the equivalent `Rule.after_flush_row_event(... kafka_producer.send_row_to_kafka ...)` already exists in `app_integration.py` |
| 🟠 -2 | `send_order_to_shipping` event handler lives in `declare_logic.py` instead of `logic/logic_discovery/place_order/` | Move to a `logic_discovery` use-case file once the `OrderShipping` issue above is resolved |
| 🟡 -2 | Missing `__init__.py` at `logic/logic_discovery/` root and `logic/logic_discovery/place_order/` | `touch` both files |
| 🟡 -4 | 4 unindexed FK columns | `CREATE INDEX` on each FK column listed above (item.product_id, item.order_id, order.customer_id, sysemail.customer_id) |

---

## Effective LOC Detail

Total Effective LOC: **307** (vs hardcoded scaffold baselines; `database/models.py` excluded)

| Bucket | LOC | Detail |
|---|---|---|
| logic/declare_logic.py (Python customization example) | 33 | `send_order_to_shipping` handler + wiring (lines 34-66) — net new vs `basic_demo_logic_gov` baseline (91 lines) |
| logic_discovery/mcp_client_executor_request.py (new file) | 50 | Request Pattern handler for SysMcp |
| database/mcp_models.py (new file) | 58 | Separate-bind `SysMcp` model (`__bind_key__='mcp'`) |
| api/api_discovery/order_b2b_service.py (new file) | 60 | B2B order-creation endpoint |
| api/api_discovery/mcp_expose_api_models.py (new file) | 52 | MCP model-exposure endpoint |
| integration/row_dict_maps/OrderB2BMapper.py (new file) | 54 | B2B → internal Order/Item field mapping |

> Baseline reference: `basic_demo_logic_gov` (closest same-generation sibling — `security/declare_security.py`=48,
> `logic/logic_discovery/use_case.py`=32/30 and `auto_discovery.py`=51 match within whitespace/comment-only diffs,
> `logic/declare_logic.py`=91 lines). `check_credit.py` (31) and `app_integration.py` (23) implement the
> **same 5+1 rules** as `basic_demo_logic_gov`'s 23+14-line versions — 0 net new (same restatement
> precedent as `basic_demo_logic_gov`'s report). All other Effective LOC is concentrated in:
> (a) the new `send_order_to_shipping` Python-customization block in `declare_logic.py`, and
> (b) five new files supporting MCP client-executor (Request Pattern) and B2B order integration —
> none of which exist in `basic_demo_logic_gov`, `allocate_dept_account_demo`, or `nw_sample`.

**Per-table (logic LOC referencing each table — overlapping by design):**

| Table | LOC |
|---|---|
| Customer | ~31 (check_credit.py — balance sum/constraint) |
| Order | ~120 (check_credit.py amount_total sum + app_integration.py Kafka event + declare_logic.py send_order_to_shipping + order_b2b_service.py + OrderB2BMapper.py) |
| Item | ~31 (check_credit.py — amount formula + unit_price copy; OrderB2BMapper.py Item mapping) |
| Product | ~31 (check_credit.py — unit_price copy source; OrderB2BMapper.py Product lookup) |
| SysMcp | ~108 (mcp_client_executor_request.py + mcp_models.py + mcp_expose_api_models.py) |

> Counts overlap because `check_credit.py` declares 5 rules across multiple tables in one file,
> and `OrderB2BMapper.py` touches Order, Item, Customer, and Product.

---

## Summary

basic_demo_sample is the **richest member of the basic_demo family** — it carries the canonical 5-rule check-credit chain (11 pts: balance constraint, two sum rules, one formula, one copy) plus three integration extensions: a Kafka `order_shipping` event (`app_integration.py`), an MCP client-executor Request Pattern handler (`mcp_client_executor_request.py` + separate-bind `mcp_models.py`), and a B2B order-creation API (`order_b2b_service.py` + `OrderB2BMapper.py`).

**Coverage 3.7** — moderate-to-strong for the 3-table check-credit domain (Customer, Order, Item); Product is correctly excluded as a 2-column lookup, and SysEmail/SysMcp are correctly excluded as system/request tables.

**Integrity 90** — fair; driven by a real bug: `logic/declare_logic.py:61` references `OrderShipping`, a `RowDictMapper` class that is never imported or defined anywhere in the project. The `send_order_to_shipping` handler wired via `Rule.after_flush_row_event(on_class=models.Order, calling=send_order_to_shipping)` will raise `NameError` the first time it executes (on every Order insert — there is no `if_condition` guard). This appears to be unfinished "Python Customization Example" code, explicitly commented as a *replacement* for the working `Rule.after_flush_row_event(... kafka_producer.send_row_to_kafka ...)` rule that is *also* still present (and functional) in `app_integration.py`. Combined with the same 4 unindexed FK columns and 2 missing `__init__.py` files seen across the basic_demo family, this drops Integrity from the family's typical 93-96 to 90.

**Effective LOC 307** — the 5+1 check-credit rules restate `basic_demo_logic_gov`'s baseline (0 net new, same as that report). The 307 lines are: 33 lines of new (but broken) Kafka-customization code in `declare_logic.py`, plus 274 lines across 5 new files (`mcp_client_executor_request.py`, `mcp_models.py`, `order_b2b_service.py`, `mcp_expose_api_models.py`, `OrderB2BMapper.py`) implementing MCP Request Pattern and B2B integration — none of which appear in any sibling basic_demo project.
