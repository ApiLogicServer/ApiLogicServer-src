# Distilled Requirements (`demo_eai_legacy`)

This document captures the functional and non-functional requirements distilled directly from the `app/` source code.

---

## 1. Domain Model & Data Persistence (`app/models.py`)
The system manages six SQLite-backed entities registered in `TABLES`:
* **`Customer`**: Tracks `name`, `balance` (derived), `credit_limit`, `email`, and `email_opt_out`.
* **`Product`**: Tracks `name`, `unit_price`, and `count_suppliers`.
* **`Order`**: Belongs to a `Customer` (`customer_id` required); tracks `notes`, `CreatedOn`, `date_shipped`, and `amount_total` (derived).
* **`Item`**: Line item linking an `Order` (`order_id`) and a `Product` (`product_id` required); tracks `quantity` (required), `unit_price` (derived snapshot), and `amount` (derived).
* **`Supplier` & `ProductSupplier`**: Store supplier contact/region details and product-supplier sourcing attributes (`supplier_part_number`, `unit_cost`, `lead_time_days`). *(Note: Although `Product.count_suppliers` exists on the schema, no business rule currently updates it when `ProductSupplier` rows change.)*

---

## 2. Core Business Logic & Reactive Integrity Rules (`app/logic.py`)
Implemented via SQLAlchemy session hooks (`before_flush` and `after_flush`) so that every write path (REST CRUD, B2B endpoint, and Kafka consumer) enforces identical rules within a transaction:

1. **Product Price Snapshot**: When an `Item` is created or its `product_id` changes, `Item.unit_price` is copied from `Product.unit_price`. Subsequent changes to `Product.unit_price` do not retroactively alter existing items.
2. **Line-Item Extended Amount**: `Item.amount` is always calculated as `Item.quantity * Item.unit_price`.
3. **Order Total Rollup**: `Order.amount_total` is recalculated as the sum of `Item.amount` for all items on the order (defaulting to `0`) whenever items are added, updated, reassigned to another order, or deleted.
4. **Customer Balance Rollup (Unshipped Orders Only)**: `Customer.balance` is recalculated as the sum of `Order.amount_total` across all **unshipped** orders (`date_shipped IS NULL`) for that customer whenever affected orders or items change, an order is reassigned to a different customer, `date_shipped` is set/cleared, or an order is deleted.
5. **Credit Limit Enforcement**: Whenever a customer's `balance` is recalculated or an existing customer's `credit_limit` is updated, the system verifies `balance <= credit_limit`. If exceeded, `CreditError` is raised (`"{name}: balance {balance} exceeds credit limit {limit}"`), aborting the transaction.
6. **Referential & Cascade Rules**:
   * Creating/updating an `Item` with a non-existent `product_id` or an `Order` with a non-existent `customer_id` raises a `ValueError`.
   * Deleting an `Order` cascades deletion to all associated `Item` records.

---

## 3. Event-Driven Order Shipping Notifications (`app/logic.py`, `app/messaging.py`)
* **Shipping Trigger**: When an `Order` is created with a non-null `date_shipped` or updated so `date_shipped` transitions to a non-null date, an outbound message is queued in a session outbox.
* **Transactional Outbox Delivery**: Messages are only published in `after_commit` and discarded in `after_rollback`, preventing phantom notifications on failed transactions.
* **Payload Format**: `_shipping_message` publishes to the `order_shipping` topic with:
  ```json
  {
    "order_id": 1,
    "order_date": "YYYY-MM-DD",
    "customer_name": "...",
    "total": 123.45,
    "items": [{"quantity": 2, "product_name": "...", "unit_price": 61.725}]
  }
  ```
* **Simulated vs. Live Broker Mode**: `publish` always records messages in the in-memory `published` list (inspectable via `GET /kafka_log`) and additionally produces to a live Kafka broker when `KAFKA_SERVER` is configured.

---

## 4. B2B Order Intake & Kafka Integration (`app/integration.py`)
* **Partner Payload Transformation (`process_order_b2b`)**:
  * Accepts `{ "Account": "<customer name>", "Notes": "...", "Items": [{ "Name": "<product name>", "QuantityOrdered": <int> }] }`.
  * Resolves `Account` by `Customer.name` and each item's `Name` by `Product.name`; raises `LookupError` (mapped to HTTP `422`) if either is unknown.
  * Validates that `Items` is non-empty and every `QuantityOrdered` is a positive integer (`> 0`); raises `ValueError` (mapped to HTTP `400`) otherwise.
  * Sets `Order.CreatedOn` to `date.today()` and commits the order and items atomically (rolling back if credit check or validation fails in `consume`).
* **Multi-Channel Intake**:
  1. **Synchronous REST (`POST /OrderB2B`)**: Processes a JSON request body and returns the created order (`201 Created`).
  2. **Asynchronous Kafka Consumer (`start_consumer`)**: Background daemon thread subscribed to topic `order_b2b` (consumer group `demo_eai_native`); logs and skips poison/rejected messages so a bad payload never halts the consumer.
  3. **Brokerless Debug Endpoint (`GET /consume_debug/<topic>?file=<path>`)**: Reads a payload file located within the project directory and runs the exact same `consume` pipeline.

---

## 5. Security: Authentication & Row-Level Security (`app/security.py`)
* **Keycloak RS256 Bearer Authentication (`authenticate`)**:
  * Validates `Authorization: Bearer <token>` against the Keycloak realm's JWKS endpoint (`{KEYCLOAK_URL}/realms/{KEYCLOAK_REALM}/protocol/openid-connect/certs`, defaulting to `http://localhost:8080` and realm `kcals`).
  * Unauthenticated requests receive `401 Unauthorized`, except for open operational/test routes: `/health`, `/kafka_log`, and `/consume_debug/<topic>`.
* **Role Assignment & Row-Level Security (`row_filter`)**:
  * Roles are extracted from JWT `realm_access.roles`, and usernames listed in `SALES_USERS` (default `"u1"`) are automatically granted the `sales` role.
  * When a user has the `sales` role, all queries, single-row lookups, updates, and deletes on `Customer` are restricted to rows satisfying:
    `credit_limit >= 3000 OR balance > 0`
  * Filtered-out customers are omitted from `GET /api/customer` list responses and return `404 Not Found` on `/api/customer/<id>` operations.

---

## 6. REST API Contract (`app/api.py`)
* **Generic CRUD (`/api/<table>` & `/api/<table>/<int:id>`)**:
  * Supports `GET` (list with exact-match attribute filtering, `limit` default `100`, `offset` default `0`, ordered by `id`), `GET` by ID, `POST` (`201`), `PATCH`/`PUT` (`200`), and `DELETE` (`204`).
* **Write Protection on Derived Columns (`DERIVED`, `writable`)**:
  * Client-supplied values for `id`, `customer.balance`, `order.amount_total`, `item.amount`, and `item.unit_price` are silently ignored on create/update; unknown column names are rejected with `400 Bad Request`.
* **Error Mapping**:
  * `ValueError` and `CreditError` → `400 Bad Request`
  * Missing/invalid JWT → `401 Unauthorized`
  * Unknown table or row (including RLS-hidden rows) → `404 Not Found`
  * `LookupError` (unknown B2B `Account` or `Product`) → `422 Unprocessable Entity`

