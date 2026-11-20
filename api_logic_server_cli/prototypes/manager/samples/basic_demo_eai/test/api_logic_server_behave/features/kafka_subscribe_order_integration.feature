Feature: Kafka Subscribe Order Integration

  # Topic order_b2b, 2-message design. Delivered live through the broker when one answers, else simulated (debug endpoint).

  Scenario: Order Message Delivered
    Given Customer "Quinn" with credit limit 5000
    When an inbound order message for "Quinn" with 1 Widget and 2 Gadget is delivered to topic order_b2b
    Then the message is processed
    And the Customer's newest order has 2 items totaling 390
    And Customer balance should be 390

  Scenario: Unknown Account Message Rejected
    When an inbound order message for an unknown account is delivered to topic order_b2b
    Then the message is rejected with "no Customer found"

  Scenario: Rejected Message Keeps Its Error (live Kafka only)
    When an inbound order message for an unknown account is delivered live to topic order_b2b
    Then the message row keeps is_processed false and its error_text
