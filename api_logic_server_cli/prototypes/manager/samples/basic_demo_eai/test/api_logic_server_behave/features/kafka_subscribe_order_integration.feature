Feature: Kafka Subscribe Order Integration

  # Topic order_b2b. The message is sent through the debug endpoint: live through the broker when one is
  # configured and answering, else simulated (the consumer's parse-and-save function, no Kafka).
  # The traceability report shows which one ran.

  Scenario: Order Message Delivered
    Given Customer "Frank" with credit limit 5000
    When an inbound order message for that customer is delivered to topic order_b2b with 2 Widget and 1 Gadget
    Then the message is processed
    And an Order for the customer has 2 items totalling 330

  Scenario: Unknown Account Message Rejected
    When an inbound order message for an unknown account is delivered to topic order_b2b
    Then the message is rejected with a reason

  Scenario: Rejected Message Keeps Its Error (live Kafka only)
    When an inbound message for an unknown account is delivered live to topic order_b2b
    Then the blob stays unprocessed with error_text
