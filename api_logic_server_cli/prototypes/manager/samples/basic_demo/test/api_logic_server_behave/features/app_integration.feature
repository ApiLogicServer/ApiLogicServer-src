Feature: App Integration

  Scenario: Kafka Message on Ship
     Given Test customer with unshipped order
      When Order date_shipped set to today
      Then Kafka message sent to order_shipping topic

  Scenario: No Kafka Message When Unshipped
     Given Test customer with shipped order
      When Order date_shipped set to None
      Then No Kafka message sent
