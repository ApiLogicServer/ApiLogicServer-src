# Logic Flow — demo_eai_modernized [order_shipping]

> Scoped to requirement: **order_shipping**

<table>
<tr valign="top">
<td width="65%">

![logic flow](logic_diagrams/logic_diagram_order_shipping.svg)

</td>
<td width="35%">

### Rules

1. `Order` → `send_order_shipping` (after_flush) — Order event: publish to topic order_shipping when date_shipped is set on insert or changes to a non-null date

</td>
</tr>
</table>

## Requirements

```
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
```

---
_Generated 2026-10-27 21:53_
