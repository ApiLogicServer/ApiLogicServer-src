## Ad-Libs Report
**4 items need your review. 7 FYIs — standard patterns, no action needed.**

---

## Walkthrough

1. **Basic data model** — customer, product, order, item, supplier, product_supplier (from `basic_demo.sqlite`).
2. **Derived/predicted schema additions** — one new table, `order_b2b_message` (Kafka blob: payload, is_processed, error_text, received_at). No SysConfig constants, no new FKs, no Allocate, no Request Pattern.
3. **Create db** — one `CREATE TABLE` + `rebuild-from-database` (8 tables).
4. **Run impl-req** — 4 sum/formula/copy rules + 1 constraint (Check Credit); 2 `after_flush_row_event`s (Kafka publish, 2-message bridge); custom API `OrderB2B`; Kafka subscribe handlers; security grants.
5. **Test data / testing** — Behave: 5 features, 12 scenarios (11 pass, 1 skipped: Row-Level Security, security disabled). Verified against a live Kafka broker.

<details markdown>
<summary>Full diagnostic detail (DDL change list, rule plan, rejected alternatives, replay log)</summary>

### 🟢 Diagnostic Appendix

#### Pre-Coding Analysis

**Phase 1 — Schema Impact Assessment**
Files read: `requirements.md`, `message_formats/*`, `database/models.py`

| Step | Signal |
|---|---|
| 1 — Check Credit | No schema change (balance, amount_total, amount, unit_price already present) |
| 2 — B2B API | No schema change |
| 3 — Kafka Subscribe | EAI consume detected — blob table needed |
| 4 — Kafka Publish | No schema change |
| 5 — Security | No schema change |

DDL change list:

| Table | Change | Reason |
|---|---|---|
| order_b2b_message | CREATE TABLE | Step 3 — EAI blob table (with `error_text`) |

**Phase 2 — CE / Pattern Assessment**
Files read: `eai_subscribe.md`, `logic_bank_api.md`, `security.md`, `testing.md`, `implement_requirements.md`

| Step | Rule Plan |
|---|---|
| 1 — Check Credit | `Rule.constraint` + `Rule.sum` x2 + `Rule.formula` + `Rule.copy` |
| 2 — B2B API | `OrderB2B` custom API + `RowDictMapper` |
| 3 — Kafka Subscribe | 2-message EAI: consumer 1 (blob), `after_flush_row_event` bridge, consumer 2 (parse), `/consume_debug` |
| 4 — Kafka Publish | `Rule.after_flush_row_event` + by-example mapper (`EaiPublishMapper.serialize_row`) |
| 5 — Security | two `Grant`s on Customer for the sales role (OR'd) |

Anti-patterns confirmed clear:
- [x] No parent flag where a child count is correct
- [x] No `as_expression=lambda row: my_func(row)`
- [x] No `session.query()` inside formula or row_event
- [x] EAI: 2-message design, `is_processed` guard, `error_text` capture

#### Execution Metrics

| Metric | Value |
|---|---|
| Strategy Used | DDL once, then logic files, EAI artifacts, API, security; verify via debug endpoint, B2B API, then live Kafka |
| CE Files Loaded | `.github/copilot-instructions.md`, `docs/training/implement_requirements.md`, `eai_subscribe.md`, `security.md`, `testing.md`, `logic_bank_api.md` (excerpts) |
| Schema Read First | Yes |
| Sample Data Read | Yes — `message_formats/*` |
| Subagent Used | No — single pass |
| Self-Verification | Yes — server started, debug endpoint, B2B API, shipping publish, live Kafka subscribe and publish |
| Gate Test Run Count | 2 (second after the `received_at` fix) |
| Gate Test Purpose | Final verification |
| Error Correction Loops | 1 |

```
Loop 1:
  Symptom:   OrderB2bMessage.received_at stayed NULL
  Diagnosis: read the blob rows after the first live Kafka message
  Fix:       set received_at=datetime.now() where the blob is created (integration/kafka/kafka_subscribe_discovery/order_b2b.py:63, :88)
  Root cause type: model omission (DDL had no default; ORM has none)
```

---

### 🔴 Review Required

| Location | Issue | Action |
|---|---|---|
| `security/declare_security.py:60-68` | Row-level grants are declared but NOT verified: Docker is unavailable here, so Keycloak could not start; security was disabled (`SECURITY_ENABLED = False` in `config/default.env`) and the Row-Level Security scenario is skipped. | Start Keycloak, run `genai-logic add-auth --provider-type=keycloak --db-url=localhost`, re-run the tests. |
| `test/api_logic_server_behave/features/steps/demo_eai_steps.py:21` | `SALES_USER = 'sales'` is a guess at the login name of a user holding the sales role. | Set it to a real user with the sales role in your Keycloak realm. |
| `security/declare_security.py:36` | `sales` role name taken from the requirement; it must match a role in your auth provider. | Confirm the role exists in Keycloak. |
| `api/api_discovery/order_b2b_service.py:67` | Failures return `[{error}, 400]` as the RPC result, so the HTTP status is 200 (standard template); callers must read the result body. | Confirm partners can tolerate this, or raise a safrs error to get a real HTTP 400. |

---

### 🟡 FYI
- `logic/logic_discovery/check_credit.py:21` — "exceeds" implemented as `balance <= credit_limit` (boundary operator convention).
- `logic/logic_discovery/check_credit.py` — no `quantity > 0` constraint added (the spec is silent).
- `integration/kafka/kafka_publish_discovery/order_shipping.py:30` — `order_date` maps to `Order.CreatedOn`, which nothing sets, so published `order_date` is `null`.
- `integration/kafka/kafka_publish_discovery/order_shipping.py:17` — message shape embedded as `SAMPLE` (mirrors `message_formats/order_shipping.json`); amounts published as JSON numbers.
- `integration/row_dict_maps/OrderB2BMapper.py:13` — `Notes` is mapped (in the sample message, not in the requirement) and is required on the B2B API; the Kafka path treats it as optional.
- `integration/kafka/kafka_subscribe_discovery/order_b2b.py` — offsets are not committed, so a server restart replays earlier messages and creates duplicate orders (dev/demo default; see `kafka_readme.md`).
- `config/default.env` — `KAFKA_SERVER = localhost:9092` and `KAFKA_CONSUMER_GROUP = demo_eai-group1` are now enabled, as requested; the broker used for verification was a local Kafka 3.7 (no Docker available) and has been stopped.

</details>
