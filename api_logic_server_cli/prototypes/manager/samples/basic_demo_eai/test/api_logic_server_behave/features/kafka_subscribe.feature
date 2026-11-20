Feature: Kafka Subscribe Order Integration

  Scenario: Order message for a known customer creates the order
    Given a new customer "Kafka Cust" with credit limit 5000
    When an order message for "Kafka Cust" with 1 Widget and 2 Gadget is delivered to topic order_b2b
    Then the message is processed
    And "Kafka Cust" has one order with total 390
    And the order items are 1 Widget and 2 Gadget

  Scenario: Order message with an unknown product is rejected
    Given a new customer "Kafka Bad" with credit limit 5000
    When an order message for "Kafka Bad" with 1 Sprocket is delivered to topic order_b2b
    Then the message is rejected with "Product"
    And "Kafka Bad" has no orders

  Scenario: Rejected message stays on the blob with its error (live Kafka only)
    Given a new customer "Kafka Live Bad" with credit limit 5000
    When an order message for "Kafka Live Bad" with 1 Sprocket is delivered live to topic order_b2b
    Then the message blob is not processed and has error text
