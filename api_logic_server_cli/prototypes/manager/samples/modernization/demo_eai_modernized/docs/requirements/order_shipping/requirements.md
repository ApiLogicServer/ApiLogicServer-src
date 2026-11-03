## 3. Event-Driven Order Shipping Notifications (`app/logic.py`, `app/messaging.py`)

Feature: Order Shipping Notification
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
