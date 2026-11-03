Feature: Order B2B Intake

  Scenario: Partner order through the REST API is created
    Given a new customer with credit limit 1000
    When a partner order for the customer with 1 Widget and 2 Gadget is posted
    Then the partner request answers 201
    And the partner order total is 390
    And the customer balance is 390

  Scenario: Partner order for an unknown account is refused
    Given a new customer with credit limit 1000
    When a partner order for account "No Such Account" with 1 Widget is posted
    Then the partner request answers 422

  Scenario: Partner order for an unknown product is refused
    Given a new customer with credit limit 1000
    When a partner order for the customer with 1 "No Such Product" is posted
    Then the partner request answers 422

  Scenario: Partner order with no items is refused
    Given a new customer with credit limit 1000
    When a partner order for the customer with no items is posted
    Then the partner request answers 400

  Scenario: Partner order with a zero quantity is refused
    Given a new customer with credit limit 1000
    When a partner order for the customer with 0 Widget is posted
    Then the partner request answers 400

  Scenario: Partner order over the credit limit is refused
    Given a new customer with credit limit 100
    When a partner order for the customer with 1 Widget and 2 Gadget is posted
    Then the partner request answers 400
    And the partner error mentions "exceeds credit limit"
    And the customer balance is 0

  Scenario: Partner order without a token is refused
    Given a new customer with credit limit 1000
    When a partner order for the customer with 1 Widget is posted without a token
    Then the partner request answers 401

  Scenario: Inbound order message is persisted as an order
    Given a new customer with credit limit 1000
    When an inbound order message for the customer is delivered to topic order_b2b
    Then the inbound message is processed
    And the customer balance is 390

  Scenario: Inbound order message for an unknown account is rejected
    Given a new customer with credit limit 1000
    When an inbound order message for an unknown account is delivered to topic order_b2b
    Then the inbound message is rejected with "no Customer"

  Scenario: A rejected inbound order message stays on its blob with the reason (live Kafka only)
    Given a new customer with credit limit 100
    When an inbound order message for the customer is delivered live to topic order_b2b
    Then the inbound message blob is unprocessed and has error_text "exceeds credit limit"
