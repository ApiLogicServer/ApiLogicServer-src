## 2. Core Business Logic & Reactive Integrity Rules (`app/logic.py`)

Feature: Check Credit
Implemented via SQLAlchemy session hooks (`before_flush` and `after_flush`) so that every write path (REST CRUD, B2B endpoint, and Kafka consumer) enforces identical rules within a transaction:

1. **Product Price Snapshot**: When an `Item` is created or its `product_id` changes, `Item.unit_price` is copied from `Product.unit_price`. Subsequent changes to `Product.unit_price` do not retroactively alter existing items.
2. **Line-Item Extended Amount**: `Item.amount` is always calculated as `Item.quantity * Item.unit_price`.
3. **Order Total Rollup**: `Order.amount_total` is recalculated as the sum of `Item.amount` for all items on the order (defaulting to `0`) whenever items are added, updated, reassigned to another order, or deleted.
4. **Customer Balance Rollup (Unshipped Orders Only)**: `Customer.balance` is recalculated as the sum of `Order.amount_total` across all **unshipped** orders (`date_shipped IS NULL`) for that customer whenever affected orders or items change, an order is reassigned to a different customer, `date_shipped` is set/cleared, or an order is deleted.
5. **Credit Limit Enforcement**: Whenever a customer's `balance` is recalculated or an existing customer's `credit_limit` is updated, the system verifies `balance <= credit_limit`. If exceeded, `CreditError` is raised (`"{name}: balance {balance} exceeds credit limit {limit}"`), aborting the transaction.
6. **Referential & Cascade Rules**:
   * Creating/updating an `Item` with a non-existent `product_id` or an `Order` with a non-existent `customer_id` raises a `ValueError`.
   * Deleting an `Order` cascades deletion to all associated `Item` records.
