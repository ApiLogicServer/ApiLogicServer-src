---
created: 2026-11-19T19:05:00
created_by: claude-opus-5-5 (valjhuber@gmail.com)
use_case: shipping_notification
source: docs/requirements/demo_eai/requirements.md
---

## 4. Kafka Publish — Notify shipping on dispatch

```gherkin
Feature: Kafka Publish Shipping Notification

  Scenario: Notify shipping when an order is dispatched
    Given an Order exists
    When date_shipped is set
    Then publish to Kafka topic order_shipping
    And use message_formats/order_shipping.json as the message shape
    And use by-example publish rather than key-only publish
```
