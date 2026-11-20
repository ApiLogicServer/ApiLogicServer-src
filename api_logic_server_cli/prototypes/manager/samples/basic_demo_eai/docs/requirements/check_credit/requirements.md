---
created: 2026-11-19T14:27:00
created_by: claude-opus-5-5 (valjhuber@gmail.com)
use_case: check_credit
---

## 1. Business Logic — Check Credit

```gherkin
Feature: Check Credit

  Scenario: Place an order
    Given a customer with a credit limit
    When an order is placed
    Then copy the price from the product
    And multiply by quantity to get the item amount
    And sum item amounts to get the order total
    And sum unpaid order totals to get the customer balance
    And reject if balance exceeds the credit limit
```
