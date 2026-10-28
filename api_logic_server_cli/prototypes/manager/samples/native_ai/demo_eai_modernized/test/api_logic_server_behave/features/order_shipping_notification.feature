Feature: Order Shipping Notification

  Scenario: Shipping an order publishes a shipping message
    Given a new customer with credit limit 1000
    And an order is placed with 2 Widget
    When the order is shipped
    Then a shipping message is published for the order

  Scenario: An unshipped order publishes nothing
    Given a new customer with credit limit 1000
    When an order is placed with 2 Widget
    Then no shipping message is published

  Scenario: An order created already shipped publishes a shipping message
    Given a new customer with credit limit 1000
    When an order is created already shipped
    Then a shipping message is published for the order

  Scenario: Changing a shipped order does not publish again
    Given a new customer with credit limit 1000
    And an order is placed with 2 Widget
    And the order is shipped
    When the order notes are changed
    Then one shipping message was published
