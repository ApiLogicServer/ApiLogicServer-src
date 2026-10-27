## Ad-Libs Report
**3 items need your review. 8 FYIs — standard patterns, no action needed.**

---

## Walkthrough

1. **Basic data model** — customer, product, order, item (plus supplier / product_supplier) from `basic_demo.sqlite`; every column Check Credit, B2B and publish need already exists.
2. **Derived/predicted schema additions** — one EAI blob table, `order_b2b_message` (payload, is_processed, error_text, received_at). No SysConfig constants, no new FKs, no Allocate junctions, no Request Pattern columns.
3. **Create db** — one `CREATE TABLE` + `rebuild-from-database`.
4. **Run impl-req** — 5 credit rules (constraint, 2 sum, formula, copy); `OrderB2B` custom API + RowDictMapper; 2-message Kafka subscribe on `order_b2b` with the thin `EaiDebug` endpoints; by-example `order_shipping` publish; 2 sales Grants.
5. **Test data / testing** — existing basic_demo seed data used. Behave: 6 features, 13 scenarios, 46 steps passed, 0 skipped (5 requirement Features + the stock `about` placeholder). Kafka was live for all three subscribe scenarios (broker localhost:9092). Live check before the tests: sample `order_b2b.json` sent live as the first request after a cold server start -> blob `is_processed=1`, Order #8 for Alice (2 items, 390); shipping it published the `order_shipping` shape to the topic (read back from the broker, amounts as numbers).

<details markdown>
<summary>Full diagnostic detail (DDL change list, rule plan, rejected alternatives, replay log)</summary>

### 🟢 Diagnostic Appendix

#### Pre-Coding Analysis
*(written before any code - both phases completed in order)*

**Phase 1 - Schema Impact Assessment**
Files read: `requirements.md` (all steps), `message_formats/*` (all files), `database/models.py` (tables: customer, product, order, item, supplier, product_supplier)

| Step | Signal |
|---|---|
| Step 1 - Check Credit | Rule.sum x2, Rule.formula, Rule.copy, Rule.constraint. Target columns already exist (`Customer.balance`, `Order.amount_total`, `Item.amount`, `Item.unit_price`) |
| Step 2 - B2B Order Integration | Custom API `OrderB2B` + RowDictMapper (Account -> Customer.name, Items.Name -> Product.name). No schema change |
| Step 3 - Kafka Subscribe | EAI consume detected: blob table needed (2-message design) |
| Step 4 - Kafka Publish | after_flush_row_event on Order + by-example publish mapper. No schema change |
| Step 5 - Security | Grant x2 on Customer for role `sales`. No schema change |

DDL change list *(covers ALL steps, run once before any coding)*:

| Table | Change | Reason |
|---|---|---|
| order_b2b_message | CREATE TABLE (id, received_at, payload, is_processed, error_text) | Step 3 - EAI blob table (2-message pattern) |

No SysConfig constants, no new FKs, no Allocate junction, no Request Pattern columns.

**Phase 2 - CE / Pattern Assessment**
Rule plan: Step 1: constraint + 2 sum + formula + copy. Step 2: api_discovery service + RowDictMapper (error path per the CE 3.52 template). Step 3: 2-message EAI with the thin EaiDebug file, reset script, test publisher. Step 4: after_flush_row_event + by-example mapper. Step 5: two Grants for `sales`.

Anti-patterns confirmed clear: no parent flag where a child count is right; no `as_expression=lambda row: f(row)`; no `session.query()` in a formula; EAI has the `is_processed` guard, `record_error_text`, and `kafka_available()` in the bridge.

**Implementation Plan**: (1) DDL + rebuild; (2) check_credit + per-use-case requirements.md; (3) OrderB2B API + mapper; (4) Kafka subscribe artifacts 1-9; (5) Kafka publish; (6) security grants; (7) start server, smoke check each requirement.

---

#### Execution Metrics

| Metric | Value |
|---|---|
| Strategy Used | Single DDL pass (blob table), then one file set per Feature |
| CE Files Loaded | project CE v3.52 (B2B template section); training files read earlier in the same session, not re-read: `eai_subscribe.md`, `implement_requirements.md`, `security.md`, `testing.md`, `logic_bank_patterns.md`, `logic_bank_api.md` |
| Schema Read First | Yes |
| Sample Data Read | Yes |
| Subagent Used | No - single pass |
| Self-Verification | Yes - server started; security, B2B (good and rejected) and the debug endpoint exercised |
| Gate Test Run Count | 1 (final verification only) |
| Gate Test Purpose | Final verification |
| Error Correction Loops | None - implementation passed on first run |

---

### 🔴 Review Required
| Location | Issue | Action |
|---|---|---|
| `logic/logic_discovery/check_credit.py:26` | "unpaid" order totals are interpreted as `date_shipped is None` (shipping settles the balance), the basic_demo convention. The spec does not define "unpaid". | Confirm the definition of unpaid. |
| `logic/logic_discovery/check_credit.py` | No `quantity > 0` / `unit_price > 0` constraints. The CE contradicts itself: `implement_requirements.md` says always add them ("spec = floor"), the same file's rule 8 says never add logic the spec does not state. The spec was followed. | Say so if you want them. |
| `integration/kafka/kafka_publish_discovery/order_shipping.py:34` | `order_date` is mapped to `Order.CreatedOn`, but date stamping is off by default (`all_classes_stamping.py`), so the published `order_date` is null for most orders. | Decide the source of `order_date` (enable stamping, or use another column). |

---

### 🟡 FYI
- `logic/logic_discovery/check_credit.py:24` - "exceeds the credit limit" implemented as `balance <= credit_limit` (balance equal to the limit is allowed); null-safe when either value is null.
- `database/models.py` - `OrderB2bMessage` blob table; `received_at` has a DB default (`CURRENT_TIMESTAMP`) and Consumer 1 also sets it explicitly.
- `logic/logic_discovery/order_b2b_consume.py:30` - the bridge uses `after_flush_row_event` with the `is_processed` guard and `kafka_available()`.
- `integration/kafka/kafka_subscribe_discovery/order_b2b.py` - second topic `order_b2b_processed` from the 2-message design; Consumer 2 records failures with `record_error_text`.
- `logic/logic_discovery/order_shipping_publish.py:30` - publishes only on the transition to shipped (insert with date_shipped set, or update from null).
- `api/api_discovery/order_b2b_service.py` - follows the CE template: a rejected order raises `safrs.ValidationError` (HTTP 400).
- `ui/admin/admin.yaml` - `OrderB2bMessage` section added directly (payload as textarea); `admin-merge.yaml` was NOT swapped over `admin.yaml`.
- `integration/kafka/order_b2b_reset.sh` - deletes/recreates `order_b2b` and `order_b2b_processed` only; `order_shipping` is created if missing, never deleted. The debug endpoints are unauthenticated and on by default (`APILOGICPROJECT_CONSUME_DEBUG = true`); development and demo only.

</details>
