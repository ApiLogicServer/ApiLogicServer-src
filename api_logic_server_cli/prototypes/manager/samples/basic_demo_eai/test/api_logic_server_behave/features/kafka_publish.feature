Feature: Kafka Publish Shipping Notification
  # Traceability: logic/logic_discovery/app_integration.py  (Req §4)
  #   Shipping an order (date_shipped set) publishes it to topic order_shipping, by example
  #   (shape: integration/kafka/kafka_publish_discovery/order_shipping.py).
  #   Needs a Kafka broker on KAFKA_SERVER for the delivery check.

  Scenario: Shipping An Order Publishes To order_shipping
    Given Customer "Echo" with balance 0 and credit limit 1000
    And Order is created for "Echo"
    And Item is created with 1 Widget
    When Order is shipped
    Then The order_shipping publish event fired
    Then A message for the order is on topic order_shipping
