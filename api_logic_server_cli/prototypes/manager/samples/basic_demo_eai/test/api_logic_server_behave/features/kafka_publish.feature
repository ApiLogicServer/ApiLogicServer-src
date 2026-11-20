Feature: Kafka Publish Shipping Notification

  Scenario: Shipping an order publishes the shipping message
    Given a new customer "Ship Cust" with credit limit 2000
    And a B2B order is placed for "Ship Cust" with 2 Widget and 1 Gadget
    When the order is shipped
    Then an order_shipping message is published for the order
    And the message has the order_shipping shape with total 330 and 2 items

  Scenario: Changing an order without shipping it publishes nothing
    Given a new customer "Noship Cust" with credit limit 2000
    And a B2B order is placed for "Noship Cust" with 1 Gadget
    When the order notes are changed
    Then no order_shipping message is published for the order

  Scenario: Changing an already shipped order does not publish again
    Given a new customer "Reship Cust" with credit limit 2000
    And a B2B order is placed for "Reship Cust" with 1 Gadget
    And the order is shipped
    When the order notes are changed
    Then exactly one order_shipping message is published for the order
