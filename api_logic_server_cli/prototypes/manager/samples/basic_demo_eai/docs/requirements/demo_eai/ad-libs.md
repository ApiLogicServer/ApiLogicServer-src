## Ad-Libs Report
**10 items need your review. 12 FYIs — standard patterns, no action needed.**

---

## Walkthrough

1. **Basic data model** — existing basic_demo schema (Customer, Order, Item, Product); no new domain entities needed for Check Credit.
2. **Derived/predicted schema additions** — no constants for SysConfig; no lookup FKs beyond the existing ones; no Allocate; EAI blob table `order_b2b_message`; opt-in B2B request log `order_b2b_request`; per-day totals table `daily_flow` with `CreatedOnDay` day keys (Order, message, request).
3. **Create db** — one DDL pass (3 new tables, 1 new column) + `rebuild-from-database`; models.py regenerated. `admin-merge.yaml` written, swap into `admin.yaml` awaits your approval.
4. **Run impl-req** — 5 Check Credit rules (copy, formula, 2 sums, constraint), 1 publish event (by-example mapper), 1 EAI bridge event, 10 dashboard rules (8 counts/sums with insert_parent, 2 formulas); B2B custom API; 9 EAI artifacts; 2 security Grants; dashboard routes + home.js iframe; stamping turned on.
5. **Test data / testing** — 30 days of order history seeded through the rules (`database/test_data/seed_order_flow.py`); live Kafka subscribe and publish verified; Behave: 36 scenarios planned in `test_plan.md`.

<details markdown>
<summary>Full diagnostic detail (DDL change list, rule plan, rejected alternatives, replay log)</summary>

### 🟢 Diagnostic Appendix

#### Pre-Coding Analysis
*(written before any code — both phases completed in order)*

**Phase 1 — Schema Impact Assessment**
Files read: `requirements.md` (all steps), `message_formats/*` (all files), `database/models.py`

| Step | Signal |
|---|---|
| Step 1 — Check Credit | Rule.sum / Rule.formula / Rule.copy / Rule.constraint; all columns exist (balance, amount_total, amount, unit_price) — no schema change |
| Step 2 — B2B API | Custom API + RowDictMapper; "record each request, with its outcome" → `order_b2b_request` table (opt-in request log) |
| Step 3 — Kafka Subscribe | EAI detected → blob table `order_b2b_message` (payload, is_processed, error_text) |
| Step 4 — Kafka Publish | after_flush_row_event + by-example publish mapper — no schema change |
| Step 5 — Security | Grants in declare_security.py — no schema change |
| Step 6 — Order Flow Dashboard | Per-day totals → `daily_flow` table (PK `day`), `CreatedOn` + `CreatedOnDay` (FK) on Order, message and request; stamping turned on |

DDL change list *(one row per change — covers ALL steps, run once before any coding)*:

| Table | Change | Reason |
|---|---|---|
| daily_flow | CREATE TABLE (day TEXT PK, order_count, order_amount, message_received / processed / rejected / pending, request_received / processed / rejected / pending) | Step 6 — Rule.count / Rule.sum (insert_parent) + Rule.formula (pending) |
| order | ADD COLUMN CreatedOnDay TEXT REFERENCES daily_flow(day) | Step 6 — day key, set by stamping (CreatedOn already exists) |
| order_b2b_message | CREATE TABLE (id, CreatedOn DATETIME, CreatedOnDay TEXT FK, payload TEXT NOT NULL, is_processed BOOLEAN, error_text TEXT) | Step 3 — EAI blob table; Step 6 — counted per day |
| order_b2b_request | CREATE TABLE (id, CreatedOn DATETIME, CreatedOnDay TEXT FK, payload TEXT, is_processed BOOLEAN, error_text TEXT) | Step 2 — request log; Step 6 — counted per day |

**Phase 2 — CE / Pattern Assessment**
Files read: `eai_subscribe.md`, `logic_bank_api.md`, `logic_bank_patterns.md`, `queries_dashboards.md`, `security.md`

| Step | Rule Plan |
|---|---|
| Step 1 — Check Credit | Rule.copy(Item.unit_price) + Rule.formula(Item.amount) + Rule.sum(Order.amount_total) + Rule.sum(Customer.balance, where date_shipped is None) + Rule.constraint(Customer) |
| Step 2 — B2B API | api_discovery/order_b2b_service.py (request row committed first, then the order) + row_dict_maps/OrderB2BMapper.py |
| Step 3 — Kafka Subscribe | 2-message EAI — 9 artifacts (blob, handlers, bridge, mapper, sample, debug, admin.yaml, reset script, test publisher) |
| Step 4 — Kafka Publish | Rule.after_flush_row_event(Order) → publish_kafka_message(mapper=order_shipping) on the date_shipped transition |
| Step 5 — Security | Grant(Customer, sales, credit_limit >= 3000) + Grant(Customer, sales, balance > 0) — grants OR'd |
| Step 6 — Dashboard | Rule.count / Rule.sum with insert_parent=True on DailyFlow, Rule.formula for each pending count; /dashboard + /chart_graphics/order_flow (rendered, never cached); home.js iframe; zero-filled 30-day window |

Anti-patterns confirmed clear:
- [x] No parent flag where Rule.count on child table is correct
- [x] No `as_expression=lambda row: my_func(row)` — using `calling=my_func`
- [x] No `session.query()` inside formula or row_event
- [x] EAI: 2-message design confirmed; mapper returns plain model rows

**Implementation Plan** *(ordered steps written before any file was changed)*:

| Step | What was planned |
|---|---|
| 1 | DDL + rebuild-from-database — daily_flow, order.CreatedOnDay, order_b2b_message, order_b2b_request |
| 2 | check_credit.py (Step 1) |
| 3 | B2B API service + RowDictMapper, with request log (Step 2) |
| 4 | Kafka subscribe: 9 EAI artifacts (Step 3) |
| 5 | shipping_notification.py + kafka_publish_discovery/order_shipping.py (Step 4) |
| 6 | declare_security.py grants (Step 5) |
| 7 | order_flow_dashboard.py rules, stamping on, dashboard_services.py, home.js (Step 6) |
| 8 | Per-use-case requirements.md, verification run, ad-libs completion |

---

#### Execution Metrics

| Metric | Value |
|---|---|
| Strategy Used | Read all requirements + CE first; one DDL pass; rules for every derivation (incl. dashboard totals); 2-message EAI; thin API services |
| CE Files Loaded | implement_requirements.md, eai_subscribe.md, logic_bank_api.md, logic_bank_patterns.md, queries_dashboards.md, security.md, testing.md |
| Schema Read First | Yes — models.py read before any logic or mapper |
| Sample Data Read | Yes — message_formats/* read before the mappers |
| Subagent Used | No — single pass |
| Self-Verification | Yes — server started; B2B accept/reject, simulated + live Kafka, sales grant, shipping publish shape, DailyFlow totals vs. orders checked |
| Lightweight Checks Used | Yes — curl + sqlite3 reads + logs/als.log |
| Gate Test Run Count | 1 (final verification: "run the tests") |
| Gate Test Purpose | Final verification |
| Error Correction Loops | None — implementation passed on first run |
| Long-Run Diagnostics | None |

**Error Correction Loops:** None — implementation passed on first run.

---

### 🔴 Review Required
| Location | Issue | Action |
|---|---|---|
| `logic/logic_discovery/check_credit.py:31` | "unpaid order totals" is not defined; implemented as orders with `date_shipped` null (the basic_demo convention: shipping settles the order). | Confirm "unpaid" = "not shipped", or name the column that records payment. |
| `logic/logic_discovery/check_credit.py:32` | "exceeds the credit limit" implemented as reject when balance > limit (an order exactly at the limit is accepted). | Confirm the boundary. |
| `logic/logic_discovery/check_credit.py` | Not added: `quantity > 0` on Item, `unit_price > 0` on Product (domain-floor constraints the spec does not state). A zero or negative quantity is accepted today. | Say so if you want them. |
| `logic/logic_discovery/shipping_notification.py:26` | "When date_shipped is set" read as the transition: publish on insert with a value, or when the value changes (a different ship date re-publishes); other edits of a shipped order do not. | Confirm; say if a changed ship date should not re-publish. |
| `integration/kafka/kafka_publish_discovery/order_shipping.py:27` | Message field `order_date` mapped to `Order.CreatedOn` (the order's arrival date; there is no other order date). | Confirm. |
| `integration/kafka/kafka_subscribe_discovery/order_b2b.py:68` | Duplicate policy: insert-only, but the message carries no partner order id, so a replayed message creates a second order. Offsets are committed, so a restart does not replay. | Add a partner order key if duplicates must be rejected. |
| `api/api_discovery/dashboard_services.py:24` | "the last 30 days" charted as today plus the 30 days before it (31 bars), so the seeded history and today both show. | Confirm the window. |
| `logic/logic_discovery/order_flow_dashboard.py:37` | "not yet done" = received − processed − rejected (a message or request that arrived but has neither finished nor failed). | Confirm the definition. |
| `api/api_discovery/dashboard_services.py:85-94` | `/dashboard` and `/chart_graphics/*` are plain Flask routes with no authentication (as in the CE template): the daily totals are readable by anyone who can reach the server. | Decide whether the charts need a login. |
| `database/models.py` | Deleting an Order through the API does not delete its Items (no cascade declared): the items stay with `order_id` null. Not in the requirements; seen while writing the delete scenarios. | Say if deleting an order should delete (or forbid deleting) its items. |

---

### 🟡 FYI
- `logic/logic_discovery/check_credit.py:28` — `Rule.copy` for the item price (snapshot at entry, the requirement says "copy").
- `api/api_discovery/order_b2b_service.py:59` — request log per the CE opt-in pattern: request committed first (Tx 1), then the order; a rejection is rolled back and `error_text` written on the governed session; the partner gets HTTP 400.
- `integration/kafka/kafka_subscribe_discovery/order_b2b.py` — 2-message EAI design; all 9 artifacts present (blob table, handlers, bridge `logic/logic_discovery/order_b2b_consume.py`, mapper `integration/OrderB2bKafkaMapper.py`, sample `message_formats/order_b2b.json`, debug `api/api_discovery/order_b2b_kafka_consume_debug.py`, admin entry in `ui/admin/admin-merge.yaml`, `integration/kafka/order_b2b_reset.sh`, `test/send_order_b2b.py`).
- `database/models.py` — the blob's arrival time is `CreatedOn` (stamped), used instead of the template's `received_at`, so one column serves both the EAI audit and the day key.
- `logic/logic_discovery/system/all_classes_stamping.py:60` — stamping turned on (dashboard: "date each Order, message and request when it arrives"). `CreatedOn` is kept when supplied (seed, imports); no `CreatedBy` columns exist, so no user stamp is written.
- `logic/logic_discovery/order_flow_dashboard.py` — daily totals are rules (`insert_parent=True` creates a day's bucket on its first row), so they adjust incrementally and appear in the diagrams, tests and report.
- `logic/logic_discovery/order_flow_dashboard.py:26` — retention TODO: never purge counted rows (a delete changes history).
- `api/api_discovery/dashboard_services.py` — quiet days are filled with zeros when the chart is read (no rule can create a row for a day when nothing happened); charts render on every request (no cache), so data is current.
- `logic/logic_discovery/order_flow_dashboard.py` — rejected orders roll back, so `order_count` counts accepted orders only; rejected *messages* and *requests* are counted. A message rejected in **simulated** mode leaves no blob, so it is not counted (live mode counts it).
- `security/declare_security.py:61-70` — two Grants on Customer for `sales` (OR'd); Keycloak user `s1` has the sales role.
- `database/test_data/seed_order_flow.py` — the history is seeded through the rules using the live mappers; historical orders are inserted already shipped (so balances keep their current values); one day 9 days ago has 5 of 6 messages rejected (unknown account, unknown product, over the credit limit); 3 and 2 days ago have no activity. The 5 orders that predate the dashboard got their day key by an update through the rules.
- `ui/admin/admin-merge.yaml` — the three new tables (DailyFlow, OrderB2bMessage with payload as textarea, OrderB2bRequest); the to-one `daily_flow` tab groups were removed (the FK is null on older orders). Replacing `admin.yaml` with it awaits your approval.

</details>
