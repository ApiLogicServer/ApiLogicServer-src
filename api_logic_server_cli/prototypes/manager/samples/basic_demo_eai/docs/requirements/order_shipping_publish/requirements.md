---
created: 2026-10-24T15:10:00
created_by: claude-sonnet-5-5 (valjhuber@gmail.com)
use_case: order_shipping_publish
---

Feature: Kafka Publish Shipping Notification

  Scenario: Notify shipping when an order is dispatched
    Given an Order exists
    When date_shipped is set
    Then publish to Kafka topic order_shipping
    And use message_formats/order_shipping.json as the message shape
    And use by-example publish rather than key-only publish
