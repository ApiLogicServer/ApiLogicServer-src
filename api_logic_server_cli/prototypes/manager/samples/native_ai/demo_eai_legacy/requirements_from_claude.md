# Requirements recovered from `demo_eai_legacy`

Source read: `app/` (models, logic, integration, security, api, messaging) only.
Not read: tests, `.feature` files, any existing requirements document.
Each statement says what the code does. Section 7 lists what the code does that may not be what anyone meant.

---

## 1. Check Credit (`app/logic.py`)

A customer has a credit limit and a balance.  Business rules apply to every write path (REST, B2B, Kafka), because they hook the database session, not the endpoints.

1. An Item's unit price is copied from its Product when the Item is created or its Product changes.  Later changes to the Product's price do not change existing Items.
2. An Item's amount is its quantity times its unit price.
3. An Order's total is the sum of its Items' amounts (0 when it has none).  It is recomputed when an Item is added, changed, deleted, or moved to another Order (both Orders are recomputed).
4. A Customer's balance is the sum of the totals of that Customer's **unshipped** Orders (`date_shipped` is empty).  It is recomputed when an Order is added, deleted, shipped or un-shipped, or moved to another Customer (both Customers are recomputed).
5. A change is rejected, and nothing is saved, if it leaves a Customer's balance **greater than** the credit limit.  A balance equal to the limit is allowed.  The check also runs when a Customer's credit limit is lowered.
6. An Item must refer to an existing Product, and an Order to an existing Customer; otherwise the change is rejected.
7. Deleting an Order deletes its Items and recomputes the Customer's balance.
8. Clients cannot set the derived columns (`Customer.balance`, `Order.amount_total`, `Item.amount`, `Item.unit_price`); values sent for them are ignored.

## 2. Shipping notification (`app/logic.py`, `app/messaging.py`)

1. When an Order is created with a ship date, or an existing Order's ship date is set to a (different) date, a message for topic `order_shipping` is prepared.
2. The message carries: order id, order date, customer name, order total, and for each Item its quantity, product name and unit price.
3. The message is sent only after the transaction commits.  If the transaction rolls back, no message is sent.
4. Every message is also recorded in memory and can be read at `GET /kafka_log`.  It is sent to a Kafka broker only when one is configured.
5. If the broker does not accept the message within 10 seconds, an error is logged.  The order change is not undone and the message is not retried.

## 3. B2B order intake (`app/integration.py`)

A partner sends an order as: `Account` (customer name), optional `Notes`, and `Items`, each with `Name` (product name) and `QuantityOrdered`.

1. The Account is matched to a Customer by exact name, and each item Name to a Product by exact name.  An unknown Account or product is rejected as "unprocessable" (HTTP 422).
2. The order must have at least one item, and each `QuantityOrdered` must be a positive whole number; otherwise it is rejected as a bad request (HTTP 400).
3. A valid message creates one Order for that Customer, dated today, with `Notes` kept, and one Item per line.  The credit rules in section 1 then apply, so an order that takes the Customer over the limit is rejected and nothing is saved.
4. The order and its items are saved in a single transaction.
5. Three ways in, same behavior:
   - `POST /OrderB2B` with the JSON body (returns the new Order, HTTP 201).
   - A Kafka consumer on topic `order_b2b` (group `demo_eai_native`, starts at the earliest message), running only when a broker is configured.  A message that is rejected is logged and skipped; the consumer keeps running.
   - `GET /consume_debug/<topic>?file=<path>`: reads the message from a file under the project directory and processes it the same way, with no broker needed.

## 4. Security (`app/security.py`, `app/api.py`)

1. Every request needs a bearer token from Keycloak (realm `kcals` by default).  The token's signature, issuer and expiry are verified.  A missing or invalid token gets HTTP 401.
2. Exceptions: `/health`, `/kafka_log` and `/consume_debug/<topic>` need no token.
3. A user has the `sales` role if the token carries it, or if the username is in a configured list (default `u1`).
4. A `sales` user sees only Customers with a credit limit of at least 3000 **or** a balance above 0.  This applies to list, read, update and delete; a hidden Customer behaves as not found (HTTP 404).

## 5. REST API (`app/api.py`)

1. For each of the six tables (customer, product, order, item, supplier, product_supplier): list, read one, create, update (PATCH or PUT, partial), delete.
2. List supports filtering by exact match on any column, `limit` (default 100) and `offset` (default 0), ordered by id.
3. An unknown table or row gets 404; an unknown attribute in a body or filter gets 400; a business-rule or value error gets 400.
4. Dates are exchanged as ISO strings.

## 6. Data model (`app/models.py`)

Six tables: Customer (name, balance, credit limit, email, email opt-out), Product (name, unit price, supplier count), Order (customer, notes, created date, ship date, total), Item (order, product, quantity, unit price, amount), Supplier, ProductSupplier (part number, unit cost, lead time).  An Order's Customer, an Item's Product and an Item's quantity are required.

---

## 7. Gaps, risks and questions for a human

These are things the code does that the recovered requirements above make visible.  Each needs a decision, not a guess.

1. **`Product.count_suppliers` is never maintained.**  The column exists, and nothing counts `ProductSupplier` rows into it.  Intended, or a missing rule?
2. **`/consume_debug` and `/kafka_log` bypass authentication.**  `/consume_debug` creates Orders from a file without any token, so it is a way around the security in section 4.  `/kafka_log` exposes every outbound message (customer names, totals).  Is that acceptable outside a demo?
3. **The `mode=` option of `/consume_debug` is ignored.**  It is echoed back in the response but changes nothing; a "live" request is still processed the same way.
4. **No protection against redelivered messages.**  The same partner message processed twice creates two Orders.  Nothing identifies a message as already seen.
5. **Re-dating a shipped Order sends the notification again.**  Setting `date_shipped` to a different date counts as a change.  Un-shipping sends nothing.  Is a second notification wanted?
6. **Names are not unique, but intake depends on them.**  Two Customers or Products with the same name: the first one found is used.
7. **A Customer with no credit limit breaks the credit check.**  Comparing the balance to an empty limit raises an error and the request fails with a server error, not a clean rejection.
8. **Row-level security covers only Customer.**  A `sales` user cannot see a hidden Customer, but can still read that Customer's Orders and Items, and can create, change or delete any table.  Is that intended?
9. **Roles are partly hard-coded.**  A username list stands in for a `sales` role the realm does not assign (the code comments say so).
10. **`email` and `email_opt_out` on Customer are never used.**
11. **Money is stored as floating point.**  Totals and balances can accumulate rounding error.
12. **The payload check accepts `true` as a quantity** (a boolean counts as a whole number in Python), which would be saved as 1.
13. **No locking.**  Balances are recomputed from the database inside each request; two concurrent requests for the same Customer can both pass the credit check.
