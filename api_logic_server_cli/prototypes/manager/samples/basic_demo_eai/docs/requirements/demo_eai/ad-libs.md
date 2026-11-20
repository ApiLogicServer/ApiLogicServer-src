## Ad-Libs Report
**9 items need your review. 8 FYIs — standard patterns, no action needed.**

---

## Walkthrough

1. **Basic data model** — existing `basic_demo.sqlite`: Customer, Order, Item, Product, ProductSupplier, Supplier.
2. **Derived/predicted schema additions** — totals table `daily_flow` (§6); EAI blob table `order_b2b_message` (§3); opt-in request table `order_b2b_request` (§2); `CreatedOnDay` day keys (FK to `daily_flow`) on order, message and request.
3. **Create db** — one DDL batch + one `rebuild-from-database` (10 tables); the 5 sample orders' day keys initialized through the ORM (`database/test_data/init_daily_flow.py`).
4. **Run impl-req** — sum ×2, formula, copy, constraint (§1); B2B API recording each request (§2); 2-message Kafka subscribe (§3); by-example publish (§4); 2 Customer grants (§5); stamping on + 8 `Rule.count` / `Rule.sum` with `insert_parent` and 2 `Rule.formula` into `daily_flow`, read by an uncached dashboard (§6).
5. **Test data / testing** — self-checked with no Kafka: accepted and rejected B2B requests (both recorded, rejection counted), simulated consume, daily totals and charts; self-check rows removed. Seeded 30 days (`seed_order_flow.py`, through the ORM, not the API or Kafka). Behave: 30 scenarios, 30 passed, Kafka live; a restart after the live check read no message again (offsets committed).

<details markdown>
<summary>Full diagnostic detail (DDL change list, rule plan, rejected alternatives, replay log)</summary>

### 🟢 Diagnostic Appendix

#### Pre-Coding Analysis
*(written before any code — both phases completed in order)*

**Phase 1 — Schema Impact Assessment**
Files read: `requirements.md` (all 7 sections), `message_formats/*`, `database/models.py`

| Step | Signal |
|---|---|
| §1 Check Credit | Rule.sum ×2, formula, copy, constraint; derived columns already present — no schema change |
| §2 B2B API | Custom API + RowDictMapper; "record each request, with its outcome" → opt-in request table `order_b2b_request` |
| §3 Kafka Subscribe | EAI → blob table `order_b2b_message` |
| §4 Kafka Publish | after_flush_row_event + by-example mapper — no schema change |
| §5 Security | Customer grants for role `sales` — no schema change |
| §6 Dashboard | "maintain daily totals" → totals table `daily_flow` (Rule.count / Rule.sum with insert_parent); "date each Order, message and request when it arrives" → stamping (`CreatedOn` + `CreatedOnDay`, the FK to `daily_flow`) on order, order_b2b_message, order_b2b_request |

DDL change list *(one row per change — covers ALL steps, run once before any coding)*:

| Table | Change | Reason |
|---|---|---|
| daily_flow | CREATE TABLE (day TEXT PK; order_count, order_amount; message_received / _processed / _failed / _stuck; request_received / _processed / _failed / _stuck) | §6 — Rule.count / Rule.sum / Rule.formula targets |
| order_b2b_message | CREATE TABLE (id, received_at, payload, is_processed, error_text, CreatedOn, CreatedOnDay FK daily_flow.day) | §3 — EAI blob table; §6 counted |
| order_b2b_request | CREATE TABLE (id, CreatedOn, CreatedOnDay FK daily_flow.day, payload, is_processed, error_text) | §2 — opt-in request log; §6 counted |
| order | ADD COLUMN CreatedOnDay TEXT REFERENCES daily_flow(day) | §6 — day key (CreatedOn already present, Date) |

**Phase 2 — CE / Pattern Assessment**
Files read: `eai_subscribe.md` (1.8), `queries_dashboards.md` (1.6, "Per-period totals"), `implement_requirements.md`, project CE (B2B API incl. "Opt-in: record each request", EAI Publish, Security), `logic_bank_api.md`

| Step | Rule Plan |
|---|---|
| §1 | constraint + sum ×2 + formula + copy |
| §2 | OrderB2B service: request row committed first (Tx 1), processed in Tx 2; failure → rollback, error_text on the governed session, HTTP 400 |
| §3 | 2-message EAI, 9 artifacts; failures recorded by `record_error_text` (governed session) |
| §4 | after_flush_row_event + `publish_kafka_message(mapper=order_shipping)` |
| §5 | 2 Grants (OR'd) + read-only permission for sales |
| §6 | stamping on (`enable_stamping := True`); `Rule.count` / `Rule.sum` with `insert_parent=True` into `daily_flow` (orders: count, sum amount_total; messages and requests: received, processed `where is_processed`, failed `where error_text is not None`); `Rule.formula` stuck = received − processed − failed; dashboard reads `daily_flow`, fills 30 calendar days with zeros, not cached |

Anti-patterns confirmed clear:
- [x] No parent flag where Rule.count on child table is correct
- [x] No `as_expression=lambda row: my_func(row)`
- [x] No `session.query()` inside formula or row_event (the totals are rules; the dashboard only reads them)
- [x] EAI: 2-message design; every write the counts depend on goes through `safrs.DB.session`

**Implementation Plan**:

| Step | What was planned |
|---|---|
| 1 | DDL (4 changes) + rebuild-from-database once; backfill `CreatedOnDay` for the 5 sample orders through the ORM |
| 2 | check_credit.py; B2B API with request log; Kafka subscribe artifacts; publish; grants |
| 3 | stamping on; order_flow_totals.py (daily_flow rules); dashboard reads daily_flow |
| 4 | Self-check, ad-libs, STEP 8 |

---

#### Execution Metrics

| Metric | Value |
|---|---|
| Strategy Used | Rules for §1 and the §6 daily totals (stamping keys + insert_parent); system EAI engines for §2-§4; grants for §5 |
| CE Files Loaded | project CE 3.71, `eai_subscribe.md` 1.8, `queries_dashboards.md` 1.6, `implement_requirements.md`, `logic_bank_api.md` |
| Schema Read First | Yes |
| Sample Data Read | Yes |
| Subagent Used | No — single pass (unchanged §1, §3, §4 files carried over from demo_eai_1) |
| Self-Verification | Yes — server started, curl, logs |
| Lightweight Checks Used | Yes |
| Gate Test Run Count | 1 |
| Gate Test Purpose | Final verification |
| Error Correction Loops | 1 |
| Long-Run Diagnostics | None |

**Error Correction Loops**:

```
Loop 1:
  Symptom:   initializing the sample orders' CreatedOnDay raised "Unable to Adjust Missing Adopting Parent: daily_flow"
  Diagnosis: LogicBank 1.34.04 honors insert_parent on INSERT only; an UPDATE that moves a row to a day with no
             DailyFlow row fails (aggregate.py adjust_from_updated_reparented_child)
  Fix:       init_daily_flow.py creates the missing day rows first, then sets the keys
  Time:      ~2 min
  Root cause type: engine gap (see 🔴)
```

---

### 🔴 Review Required
| Location | Issue | Action |
|---|---|---|
| `logic/logic_discovery/order_flow_totals.py:30-41` | **Engine gap:** `insert_parent` creates a day row on insert only. Changing an existing row's `CreatedOnDay` to a day that has no `daily_flow` row fails ("Unable to Adjust Missing Adopting Parent"). Normal flow never does this (day keys are set on insert); a backfill or a date correction would. | LogicBank fix: honor insert_parent on reparent. Until then, create the day row first (as `database/test_data/init_daily_flow.py` does). |
| `logic/logic_discovery/check_credit.py:30` | "unpaid order totals" implemented as `date_shipped is None`. | Confirm, or name the column that marks an order paid. |
| `logic/logic_discovery/check_credit.py:29` | A customer with no credit limit passes the constraint. | Confirm, or reject orders for customers with no limit. |
| `integration/row_dict_maps/OrderB2BMapper.py:18` | The B2B API requires `Notes` (RowDictMapper rejects a request without it); the rejection is now recorded and counted. | Confirm Notes is required, or make it optional. |
| `integration/kafka/kafka_subscribe_discovery/order_b2b.py:46` | A message carries no order key, so a re-sent message creates a second Order. Offsets are now committed, so a restart no longer re-reads messages; a partner re-send still duplicates. | Add a partner order id if duplicates must be rejected. |
| `logic/logic_discovery/order_shipping_publish.py:25` | "When date_shipped is set" read as a transition (a changed ship date publishes again). | Confirm. |
| `logic/logic_discovery/order_flow_totals.py:28` | "rejected" = failed (`error_text` set), for messages and requests; a simulated (debug) rejection leaves no message row, so it is not counted. | Confirm. |
| `logic/logic_discovery/system/all_classes_stamping.py` | "Date each Order, message and request when it arrives": stamping turned on; `CreatedOn` set only when empty (a supplied date is kept), `CreatedOnDay` derived from it. | Confirm keeping supplied dates. |
| `logic/logic_discovery/check_credit.py:32` | Domain-floor constraints not added: `Item.quantity > 0`, `unit_price > 0`. | Say so if you want them. |

---

### 🟡 FYI
- `logic/logic_discovery/check_credit.py:29` — "exceeds" implemented as `balance <= credit_limit` (equal allowed).
- `logic/logic_discovery/check_credit.py:33` — `Rule.copy` (snapshot) for `Item.unit_price`.
- `api/api_discovery/order_b2b_service.py` — request row committed first (Tx 1); on failure, rollback, `error_text` on the governed session, HTTP 400 (project CE, "Opt-in: record each request").
- `integration/kafka/kafka_subscribe_discovery/order_b2b.py` — 2-message design; failures recorded by `record_error_text` through the governed session, so `message_failed` is maintained.
- `logic/logic_discovery/order_flow_totals.py:20` and `api/api_discovery/order_b2b_service.py:22` — retention TODOs: rows are never purged (a delete would lower the totals).
- `api/api_discovery/dashboard_services.py` — reads `daily_flow`, fills 30 calendar days with zeros, rendered on every request (not cached).
- `security/declare_security.py` — two Customer grants for `sales` (OR'd) + read-only permission; the dashboard routes have no login (production item).
- `ui/admin/admin.yaml` — DailyFlow, OrderB2bMessage, OrderB2bRequest added from admin-merge.yaml (payloads as textarea); admin-merge.yaml not swapped in.

</details>
