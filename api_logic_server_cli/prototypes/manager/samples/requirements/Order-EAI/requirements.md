<!--
  samples/requirements/Order-EAI/requirements.md
  Version: 1.0 (Apr 9, 2026)
  Executable Requirements spec — say "implement reqs Order-EAI" to run
-->

# Order-EAI Requirements

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

## 2. B2B API — Accept orders from external partners

```gherkin
Feature: B2B Order Integration

  Scenario: Accept order from external partner
    Given an inbound B2B order in partner format (message_formats/order_b2b.json)
    When the order is received via a Custom API endpoint named OrderB2B
    Then map Account to Customer by name
    And map Items.Name to Product by name
    And map Items.QuantityOrdered to Item.quantity
    And create the order with all Check Credit rules enforced
```

## 3. Kafka Subscribe — Inbound orders from sales channel

Subscribe to topic `order_b2b` (JSON).  
Message format: `message_formats/order_b2b.json`  
Use the 2-message pattern (save blob first, parse in second transaction).  
Apply the same field mappings as the B2B API above.

## 4. Kafka Publish — Notify shipping on dispatch

When `date_shipped` is set on an Order, publish to topic `order_shipping`.  
Message format: `message_formats/order_shipping.json`  
Use by-example publish (shaped message, not key-only).

## 5. Acceptance

```bash
# No Kafka required — test via consume_debug endpoint:
curl 'http://localhost:5656/consume_debug/order_b2b?file=integration/kafka/message_formats/order_b2b.json'

# Verify:
sqlite3 database/db.sqlite "SELECT * FROM order_b2b_message; SELECT * FROM 'order'; SELECT * FROM item;"
```
