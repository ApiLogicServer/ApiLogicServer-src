# Logic Flow — demo_eai_modernized [order_shipping_publish]

> Scoped to requirement: **order_shipping_publish**

<table>
<tr valign="top">
<td width="65%">

![logic flow](logic_diagrams/logic_diagram_order_shipping_publish.svg)

</td>
<td width="35%">

### Rules

1. `Order` → `send_order_to_shipping` (after_flush) — Order publish: sends the Order to Kafka topic order_shipping when date_shipped is set and differs from its prior value (old_row is None on insert), using the by-example message in message_formats/order_shipping.json.

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
```

---
_Generated 2026-10-27 18:09_
