---
created: 2026-11-19T14:30:00
created_by: claude-opus-5-5 (valjhuber@gmail.com)
use_case: order_b2b_consume
---

## 3. Kafka Subscribe — Inbound orders from sales channel

```gherkin
Feature: Kafka Subscribe Order Integration

  Scenario: Accept inbound orders from sales channel
    Given an inbound order message in JSON format (message_formats/order_b2b.json)
    When the message is received from Kafka topic order_b2b
    Then map Account to Customer by name
    And map Items.Name to Product by name
    And map Items.QuantityOrdered to Item.quantity
```
