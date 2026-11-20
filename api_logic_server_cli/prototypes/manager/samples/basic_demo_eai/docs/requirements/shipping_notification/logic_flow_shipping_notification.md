# Logic Flow — demo_eai [shipping_notification]

> Scoped to requirement: **shipping_notification**

<table>
<tr valign="top">
<td width="65%">

![logic flow](logic_diagrams/logic_diagram_shipping_notification.svg)

</td>
<td width="35%">

### Rules

1. `Order` → `_send_order_to_shipping` (after_flush) — Order publish: sends the Order to Kafka topic order_shipping when date_shipped is set (insert with a value,

</td>
</tr>
</table>

## Requirements

```
Feature: Kafka Publish Shipping Notification

  Scenario: Notify shipping when an order is dispatched
    Given an Order exists
    When date_shipped is set
    Then publish to Kafka topic order_shipping
    And use message_formats/order_shipping.json as the message shape
    And use by-example publish rather than key-only publish

version: 1.0
created: 2026-11-19T19:00:00
created_by: claude-opus-5-5 (valjhuber@gmail.com)
```

---
_Generated 2026-11-19 18:57_
