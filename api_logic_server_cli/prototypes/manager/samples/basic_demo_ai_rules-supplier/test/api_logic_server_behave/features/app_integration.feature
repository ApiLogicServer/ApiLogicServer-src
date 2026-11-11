Feature: App Integration

  Scenario: Shipping an Order Publishes to Kafka
    Given a customer with credit limit 5000
    And an order is placed with 2 Egyptian Cotton Sheets
    And the scenario logic log is started for "Order Publishes on Ship"
    When the order is shipped
    Then the logic log shows a publish to topic order_shipping

  Scenario: Unshipped Order Does Not Publish
    Given a customer with credit limit 5000
    And the scenario logic log is started for "Order Not Shipped No Publish"
    When an order is placed with 2 Egyptian Cotton Sheets
    Then the logic log shows no publish to topic order_shipping
