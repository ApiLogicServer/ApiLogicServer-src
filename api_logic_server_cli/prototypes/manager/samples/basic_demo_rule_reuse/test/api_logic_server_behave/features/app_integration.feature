Feature: App Integration

  Scenario: Shipping an Order publishes it
    Given Customer "Ann" with credit limit 1000
    And Order "O1" is created for "Ann" with 1 Widget
    When Order "O1" is shipped
    Then Order "O1" is published to topic "order_shipping" 1 time

  Scenario: Editing an unshipped Order does not publish
    Given Customer "Ann" with credit limit 1000
    And Order "O1" is created for "Ann" with 1 Widget
    When Order "O1" notes are changed
    Then Order "O1" is published to topic "order_shipping" 0 times

  Scenario: Editing a shipped Order does not publish again
    Given Customer "Ann" with credit limit 1000
    And Order "O1" is created for "Ann" with 1 Widget
    And Order "O1" is shipped
    When Order "O1" notes are changed
    Then Order "O1" is published to topic "order_shipping" 1 time
