Feature: Subscribe to Kafka and persist shipments

  Scenario: Shipment message is delivered and the shipment graph is persisted
    Given a shipment message for account 451000001 with value 2500
    When the message is delivered to topic isdc
    Then the shipment is persisted with 1 piece, 3 parties and 1 commodity
    And the message blob is marked processed

  Scenario: Replay of the same message replaces the shipment graph
    Given a shipment message for account 451000001 with value 2500
    When the message is delivered to topic isdc
    And the same message is delivered to topic isdc again
    Then the shipment is persisted with 1 piece, 3 parties and 1 commodity
    And there are 2 message blobs for the shipment

  Scenario: Replayed message with a changed value replaces the stored shipment
    Given a shipment message for account 451000001 with value 2500
    When the message is delivered to topic isdc
    And the message is delivered again with value 3100
    Then the shipment is persisted with 1 piece, 3 parties and 1 commodity
    And the stored shipment value is 3100

  Scenario: Deleting the shipment leaves no orphans
    Given a shipment message for account 451000001 with value 2500
    When the message is delivered to topic isdc
    And the shipment is deleted
    Then no pieces, parties or commodities remain for the shipment

  Scenario: A malformed message leaves an unprocessed blob with error text (live Kafka only)
    Given a malformed shipment message
    When the malformed message is delivered live to topic isdc
    Then the message blob is not processed and has error text
