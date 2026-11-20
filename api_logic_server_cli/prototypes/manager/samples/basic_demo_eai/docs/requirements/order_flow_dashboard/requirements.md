---
created: 2026-11-19T19:05:00
created_by: claude-opus-5-5 (valjhuber@gmail.com)
use_case: order_flow_dashboard
source: docs/requirements/demo_eai/requirements.md
---

## 6. Operations Dashboard — Order flow

```gherkin
Feature: Order Flow Dashboard

  Scenario: Show that orders are flowing
    Given orders arrive through the B2B API and the Kafka topic order_b2b
    When an operator opens the Admin App home page
    Then maintain daily totals of orders (count and total amount), and of order_b2b messages and B2B requests
         (received, processed, rejected, and not yet done)
    And chart the daily totals for the last 30 days, showing a day with no activity as zero
    And date each Order, message and request when it arrives
    And show current data each time the page is opened
```
