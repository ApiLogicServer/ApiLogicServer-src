Feature: Kafka Subscribe Order Integration

  Scenario: Kafka Consume Valid order_b2b
    Given a fresh customer for order_b2b with credit_limit 5000
    When a valid order_b2b message is delivered for that customer
    Then the OrderB2bMessage row is recorded with is_processed True
    And an Order is created for that customer with amount_total 390

  Scenario: Kafka Consume Bad order_b2b (live Kafka only)
    Given a fresh customer for order_b2b with credit_limit 100
    When an over-limit order_b2b message is delivered via live Kafka for that customer
    Then the OrderB2bMessage row is recorded with is_processed False and error_text

