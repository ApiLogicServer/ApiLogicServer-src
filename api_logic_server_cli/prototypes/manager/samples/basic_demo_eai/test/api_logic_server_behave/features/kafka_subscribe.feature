Feature: Kafka Subscribe Order Integration
  # Traceability: integration/kafka/kafka_subscribe_discovery/order_b2b.py  (Req §3)
  #   Tested through /consume_debug/order_b2b, which runs the same parse-and-persist function
  #   as Consumer 2, without needing a message on the topic.

  Scenario: Inbound Order Message Creates The Order And Items
    Given Customer "Delta" with balance 0 and credit limit 1000
    When Inbound order message is consumed for "Delta" with 2 Widget and 1 Gadget
    Then Order is persisted from the message
    Then Order has 2 items
    Then Order amount_total is 330
    Then Customer balance is 330
    Then Message blob is marked processed
