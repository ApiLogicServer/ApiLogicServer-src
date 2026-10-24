## Ad-Libs Report
**3 items need your review. 11 FYIs — standard patterns, no action needed.**

---

## Walkthrough

1. **Basic data model** — customer, product, order, item, supplier, product_supplier (from `basic_demo.sqlite`).
2. **Derived/predicted schema additions** — one new table, `order_b2b_message` (Kafka blob: payload, is_processed, error_text, received_at). No SysConfig constants, no new FKs, no Allocate, no Request Pattern.
3. **Create db** — one `CREATE TABLE` + `rebuild-from-database` (7 tables).
4. **Run impl-req** — 4 sum/formula/copy rules + 1 constraint (Check Credit); 1 `after_flush_row_event` for the Kafka publish and 1 for the 2-message bridge; custom API `OrderB2B`; Kafka subscribe handlers; `/consume_debug`; two sales grants.
5. **Test data / testing** — Behave: 5 features, 12 scenarios. Simulated run (no broker): 11 pass, 1 skipped (the live-only scenario). Live run against a throwaway Podman broker: 12 pass, 0 skipped. Row-Level Security ran against the SQL authentication provider. Keycloak was not used.

<details markdown>
<summary>Full diagnostic detail (DDL change list, rule plan, rejected alternatives, replay log)</summary>

### 🟢 Diagnostic Appendix

#### Pre-Coding Analysis
*(Deviation: this section was written after the code, not before it.)*

**Phase 1 — Schema Impact Assessment**
Files read: `requirements.md` (all steps), `message_formats/*` (both files), `database/models.py`

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
| order_b2b_message | CREATE TABLE (id, received_at, payload, is_processed, error_text) | Step 3 — EAI blob table |

**Phase 2 — CE / Pattern Assessment**
Files read: `eai_subscribe.md`, `logic_bank_api.md`, `security.md`, `testing.md` (parts), `implement_requirements.md` (parts)

| Step | Rule Plan |
|---|---|
| 1 — Check Credit | `Rule.constraint` + `Rule.sum` x2 + `Rule.formula` + `Rule.copy` |
| 2 — B2B API | `OrderB2B` custom API + `RowDictMapper` |
| 3 — Kafka Subscribe | 2-message EAI: Consumer 1 (blob), `after_flush_row_event` bridge, Consumer 2 (parse), `/consume_debug` |
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
| Strategy Used | DDL once, then logic files, EAI artifacts, API, security; verify via login, B2B API, debug endpoint, publish log |
| CE Files Loaded | `.github/copilot-instructions.md`, `docs/training/logic_bank_api.md`, `eai_subscribe.md`, `security.md`, `testing.md` (parts), `implement_requirements.md` (parts) |
| Schema Read First | Yes |
| Sample Data Read | Yes — `message_formats/*` |
| Subagent Used | No — single pass |
| Self-Verification | Yes — server started, SQL-provider login, B2B API, debug endpoint, shipping publish via log |
| Gate Test Run Count | 6 (a test-path bug; the first live run, which found the consumer bug; then simulated and live final runs) |
| Gate Test Purpose | Final verification |
| Error Correction Loops | 3 |
| Mode | Default: no containers (`KAFKA_SERVER` unset, `--provider-type=sql`). Also run live with `KAFKA_SERVER=localhost:9192` (throwaway broker, removed afterwards) |

```
Loop 1:
  Symptom:   published total and unit_price were JSON strings ("390.0000000000"), not numbers as in the message shape
  Diagnosis: read the published JSON line in logs/als.log
  Fix:       integration/kafka/kafka_publish_discovery/order_shipping.py converts Decimal to float (_numbers)
  Root cause type: CE gap — EaiPublishMapper._serialize_value handles dates, not Decimal
Loop 2:
  Symptom:   3 Kafka subscribe scenarios failed with "No such file or directory"
  Diagnosis: read logs/behave.log
  Fix:       the test wrote the message file relative to its own cwd; it now writes under the project root
  Root cause type: model error (test path)
Loop 3 (found only by the live Kafka run):
  Symptom:   after the first rejected message (credit limit), no later message was processed and no error_text was recorded
  Diagnosis: logs/als.log: _record_error_text re-raised the credit-limit error; FlaskKafka._run_handlers then exited the consumer thread (sys.exit)
  Fix:       _record_error_text writes in a NEW Session(safrs.DB.engine), and the handler no longer lets an error-recording failure escape
  Root cause type: CE gap — eai_subscribe.md's template uses safrs.DB.session (the same session, still holding the failed rows) and calls it "fresh"
```

---

### 🔴 Review Required

| Location | Issue | Action |
|---|---|---|
| `api/api_discovery/order_b2b_kafka_consume_debug.py:76` | `/consume_debug/order_b2b` has no authentication even when `SECURITY_ENABLED=True` (the tests call it without a token), is on by default (`APILOGICPROJECT_CONSUME_DEBUG = true`), reads a server-side file path from the query string, creates orders, and in live mode publishes to the broker. | Set `APILOGICPROJECT_CONSUME_DEBUG = false` outside development (the guard now treats false/0 as off), or require auth on the route. |
| `integration/kafka/kafka_publish_discovery/order_shipping.py:31` | `order_date` is mapped to `Order.CreatedOn`, a guess; the spec does not say where it comes from. Nothing else sets `CreatedOn`, so the B2B API and the Kafka mapper set it to today's date (`api/api_discovery/order_b2b_service.py:57`, `integration/OrderB2bMapper.py:39`). | Confirm the source of `order_date`; orders created elsewhere still have a null `CreatedOn`. |

---

### 🟡 FYI
- `api/api_discovery/order_b2b_kafka_consume_debug.py:61` — `/consume_debug/order_b2b` has two modes (`mode=auto|simulated|live`): live publishes to topic `order_b2b` and returns when the broker acknowledges (processing is asynchronous); simulated runs the parse-and-save function directly. The response says which ran.
- `test/api_logic_server_behave/features/steps/demo_eai_steps.py:207` — Kafka Subscribe scenarios call the endpoint in `auto` mode and record the mode used per scenario (`logs/delivery_modes.json`); one scenario (rejected message keeps its `error_text`) is live-only and skips without a broker.
- `integration/kafka/kafka_subscribe_discovery/order_b2b.py:72` — live subscribe, error recording and the shipping publish to topic `order_shipping` were verified against a throwaway Podman broker (9 messages read back from the topic); the checks are repeatable with `test/send_order_b2b.py` and `integration/kafka/order_b2b_reset.sh` (generated, as the CE lists).
- `logic/logic_discovery/check_credit.py:25` — "exceeds the credit limit" implemented as `balance <= credit_limit` (boundary-operator convention).
- `logic/logic_discovery/check_credit.py:26` — "unpaid order totals" implemented as orders where `date_shipped is None`; the schema has no paid flag.
- `logic/logic_discovery/check_credit.py` — no `quantity > 0` constraint added (the spec is silent).
- `security/declare_security.py:61` — security uses the SQL authentication provider (no container); the `sales` role and user `s1` come from the project's pre-built auth database, and the tests log in as `s1`.
- `security/declare_security.py:61` — the sales role is read-only (`DefaultRolePermission`); the spec gives only the row filter.
- `api/api_discovery/order_b2b_service.py:67` — failures raise `safrs.ValidationError`, so the API returns HTTP 400 with the message (credit limit, unknown account or product).
- `integration/OrderB2bMapper.py:23` — `Notes` is mapped to `Order.notes` (in the sample message, not in the requirement).
- `ui/admin/admin.yaml:90` — the `OrderB2bMessage` resource was copied in from `admin-merge.yaml` by hand (payload as textarea); `admin.yaml` was not replaced.
- `test/api_logic_server_behave/features/` — the template's `about.feature` and `steps/about.py` placeholders were removed.

</details>
