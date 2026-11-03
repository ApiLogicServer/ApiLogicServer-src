# demo_eai_native — project summary

Non-GenAI-Logic baseline of `demo_eai`: Python, Flask, SQLAlchemy, confluent-kafka, behave. No genai-logic CLI, LogicBank, project CE, or other samples were used.

**Mode: FULL.** Docker was running with Keycloak (realm `kcals`) and a Kafka broker (`localhost:9092`), so security is Keycloak and Kafka was verified live.
Run it: `source ../venv/bin/activate && python -m app` (port 5656; set `KAFKA_SERVER=localhost:9092` for live Kafka). Tests: `behave tests/features`.

## Requirements, tests, and code

| # | Requirement (Feature / Scenario) | Test (`tests/features/`) | Result | Code |
|---|---|---|---|---|
| 1 | Check Credit / Place an order | `check_credit.feature` | passed | `app/logic.py`: `before_flush` (copy price, item amount), `after_flush` (order total, customer balance, credit check → `CreditError`) |
| 2 | B2B Order Integration / Accept order from external partner | `b2b_order_integration.feature` | passed | `app/api.py`: `order_b2b` → `app/integration.py`: `process_order_b2b` |
| 3 | Kafka Subscribe Order Integration / Accept inbound orders from sales channel | `kafka_subscribe.feature` | passed (simulated via `/consume_debug`) + live check passed | `app/integration.py`: `start_consumer` → `consume` → `process_order_b2b`; `app/api.py`: `consume_debug` |
| 4 | Kafka Publish Shipping Notification / Notify shipping when an order is dispatched | `kafka_publish.feature` | passed (message recorded in `/kafka_log`) + live check passed | `app/logic.py`: `before_flush` (detect `date_shipped`), `_shipping_message`, `after_commit`; `app/messaging.py`: `publish` |
| 5 | Row-Level Security / Sales role sees limited customers | `row_level_security.feature` | passed | `app/security.py`: `row_filter`; applied in `app/api.py`: `query` (list, get, update, delete) |
| – | REST API (JSON, filter by attribute, create/update/delete) | exercised by 1 and 5 | passed | `app/api.py`: `list_rows`, `get_row`, `create_row`, `update_row`, `delete_row` |
| – | Security (Keycloak) | all scenarios use real Keycloak tokens | passed | `app/security.py`: `authenticate`; `app/api.py`: `authenticate` |

**Tests: 5 scenarios passed, 0 failed, 0 skipped** (25 steps).
Live Kafka (`scripts/verify_kafka.py`, topics reset first): sample message on `order_b2b` produced order 6 (total 390); shipping it published the by-example message on `order_shipping`. PASS.

## Judgment calls beyond the requirements

- **"Unpaid" = `date_shipped IS NULL`** (the basic_demo convention); shipping an order removes it from the balance.
- **Logic hooks the SQLAlchemy session** (`before_flush`/`after_flush`), so it applies to REST, OrderB2B and Kafka alike. Totals are recomputed with SQL aggregates rather than adjusted incrementally. Without a rule engine, every change path had to be handled by hand: item insert/update/delete, item moved between orders, order moved between customers, order shipped, order deleted, credit limit lowered.
- **Derived columns are read-only** over REST (`customer.balance`, `order.amount_total`, `item.amount`, `item.unit_price`); the price is copied from the product when an item is created or its product changes.
- **No `sales` user exists in the `kcals` realm**, and I did not change Keycloak. A user is treated as sales if the token has a `sales` role or the username is in `SALES_USERS` (default `u1`). Tests use `u1`. Other users are unrestricted.
- **Row filter applies to by-id access and writes too**, not only the list; a hidden customer returns 404.
- **Deleting an order deletes its items.** SQLite foreign keys are not enforced, as in the source database.
- **Shipping message is published after commit** and only when `date_shipped` changes from empty to set (or an order is inserted already shipped). A failed delivery is logged; it does not roll back the order. Delivery is not transactional with the database.
- **OrderB2B errors:** unknown Account or product → 422; bad quantity or empty Items → 400; credit exceeded → 400. Order `CreatedOn` is today.
- **`/consume_debug`, `/health`, `/kafka_log` are unauthenticated**, to match the documented curl. `/consume_debug` can create orders and only reads files under the project directory. Not for production.
- **Consumer uses `auto.offset.reset=earliest`**, so topics are reset before verification, as instructed.
- **Seed data is not corrected.** Some existing items disagree with current product prices (for example item 4); only touched rows are recomputed.
- **Only the Keycloak branch was built**; the SQL users/roles fallback was not needed and does not exist.
- **Gap:** `docs/requirements` has no traceability report, diagrams or ad-libs file; this summary is the only trace.

## Lines of code written (excluding tests)

Non-blank, non-comment lines (physical lines in parentheses):

| File | Lines |
|---|---|
| `app/api.py` | 125 (152) |
| `app/logic.py` | 98 (115) |
| `app/models.py` | 50 (65) |
| `app/integration.py` | 52 (63) |
| `app/security.py` | 32 (44) |
| `app/messaging.py` | 21 (29) |
| `app/__main__.py` | 5 (7) |
| **App total** | **383 (475)** |
| `scripts/verify_kafka.py` (live Kafka check) | 72 (85) |
| **Total excluding tests** | **455 (560)** |

## Elapsed time per step (`date +%H:%M:%S`)

Start 11:33:41. Code authoring took three tool calls, so the build steps share one interval.

| Step | Start | End | Notes |
|---|---|---|---|
| Container check, read requirements and schema | 11:33:41 | 11:33:49 | Docker, Keycloak, broker found; FULL mode |
| Create project, copy db and requirements | 11:33:49 | 11:33:49 | |
| Inspect Keycloak realm, users, roles | 11:33:49 | ~11:34 | no `sales` user found |
| REST API, business logic, B2B/Kafka, security (written together) | ~11:34 | 11:36:04 | first server start and smoke test passed |
| Smoke test (REST, row filter, OrderB2B, consume_debug, publish) | 11:36:04 | 11:36:10 | |
| Verify Kafka subscriptions (live) | 11:36:25 | 11:37:29 | 1:04, of which about 55 s was two failed attempts: a leftover server held port 5656, then a `wait()` bug |
| Create tests | ~11:37:29 | 11:37:58 | |
| Run tests | 11:37:58 | 11:37:59 | 5/5 passed |
| Write this summary | 11:38:07 | 11:38:26 | |

**Total: 4 min 45 s (11:33:41 to 11:38:26).**
