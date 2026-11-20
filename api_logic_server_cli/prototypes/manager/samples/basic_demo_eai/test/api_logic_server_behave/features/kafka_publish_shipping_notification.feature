Feature: Kafka Publish Shipping Notification

  # Order -> topic order_shipping when date_shipped is set (by-example message). Checked in the scenario logic log and the
  # server log (publish_kafka_message logs the message JSON whether or not a broker answers).

  Scenario: Shipping Notification Published
    Given Customer "Gina" with credit limit 5000
    And Order is created for "Gina" with 1 Widget
    When Order is shipped
    Then the order_shipping message is published with the order id and total

  Scenario: Unshipped Order Not Published
    Given Customer "Hal" with credit limit 5000
    When B2B order placed for "Hal" with 1 Widget
    Then no order_shipping message is published
