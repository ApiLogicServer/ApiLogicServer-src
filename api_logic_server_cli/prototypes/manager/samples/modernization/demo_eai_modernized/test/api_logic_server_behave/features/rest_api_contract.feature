Feature: REST API Contract

  Scenario: A client value for a derived column is ignored on create
    When a customer is created with a balance of 9999
    Then the new customer balance is 0

  Scenario: A client value for a derived column is ignored on update
    Given a new customer with credit limit 1000
    And an order is placed with 2 Widget
    When the customer balance is patched to 777
    Then the request is accepted
    And the customer balance is 180

  Scenario: A client value for a derived item column is ignored on update
    Given a new customer with credit limit 1000
    And an order is placed with 2 Widget
    When the item amount is patched to 1
    Then the request is accepted
    And the item amount is 180

  Scenario: An unknown column is rejected
    When a customer is created with an unknown column
    Then the request is rejected with "Unknown column"

  Scenario: An order for a missing customer is rejected
    When an order is created for customer id 999999
    Then the request is rejected with "Missing Parent"

  Scenario: An unknown table is not found
    When the unknown table is requested
    Then the request answers 404
