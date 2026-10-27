Feature: Kafka Publish Shipping Notification

  # Order -> topic order_shipping when date_shipped is set (by-example message).
  # Checked in the scenario logic log (a broker is not required); live delivery is verified separately.

  Scenario: Shipping Notification Published
    Given Customer "Gina" with credit limit 5000
    And Order is created for "Gina" with 1 Widget
    When Order is shipped
    Then Order is published to Kafka topic order_shipping

  Scenario: Unshipped Order Not Published
    Given Customer "Hal" with credit limit 5000
    When B2B order placed for "Hal" with 1 Widget
    Then no shipping notification is published
