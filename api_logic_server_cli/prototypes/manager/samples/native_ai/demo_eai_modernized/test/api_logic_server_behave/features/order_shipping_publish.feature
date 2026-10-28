Feature: Kafka Publish Shipping Notification

  Scenario: Kafka Publish order_shipping on ship
    Given a customer with credit_limit 5000 and an unshipped order of 2 items at unit_price 150
    When the order date_shipped is updated to "2026-10-27" to trigger order_shipping
    Then the order_shipping message is published with order_id, customer_name, total, and items

