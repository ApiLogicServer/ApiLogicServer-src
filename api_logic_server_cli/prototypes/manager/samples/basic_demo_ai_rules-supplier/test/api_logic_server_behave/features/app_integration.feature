Feature: App Integration

  # Publish the Order to Kafka topic 'order_shipping' if the date_shipped is not None

  Scenario: Kafka - shipped order
    Given a customer with credit limit 1000
    And a product priced 10 with no suppliers
    And an order is created with 5 of the product
    When the order is shipped
    Then the logic log shows the order sent to Kafka topic "order_shipping"

  Scenario: Kafka - unshipped order
    Given a customer with credit limit 1000
    And a product priced 10 with no suppliers
    When an order is created with 5 of the product
    Then the logic log shows no message sent to Kafka topic "order_shipping"

  Scenario: Kafka - edit shipped order
    Given a customer with credit limit 1000
    And a product priced 10 with no suppliers
    And an order is created with 5 of the product
    And the order is shipped
    When the order notes are edited
    Then the logic log shows the order sent to Kafka topic "order_shipping" 1 time
