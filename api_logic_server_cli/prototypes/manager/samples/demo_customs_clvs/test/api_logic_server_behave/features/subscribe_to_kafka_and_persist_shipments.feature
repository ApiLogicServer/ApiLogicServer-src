Feature: Subscribe to Kafka and persist shipments

  Scenario: Shipment message is persisted with its graph
    Given a CIMCorp shipment message from courier "04" released at "YYZ" with customs value 2500 CAD and tariff "8542310001"
    When the message is delivered to topic isdc
    Then the shipment is persisted with 1 piece, 1 commodity and 2 parties
    And the two parties have distinct keys

  Scenario: Replayed shipment message replaces the graph
    Given a CIMCorp shipment message from courier "04" released at "YYZ" with customs value 2500 CAD and tariff "8542310001"
    When the message is delivered to topic isdc
    And the same message is delivered to topic isdc again
    Then the shipment is persisted with 1 piece, 1 commodity and 2 parties
    And the blob count for the shipment went up by one per delivery

  Scenario: Deleting the shipment leaves no orphans
    Given a CIMCorp shipment message from courier "04" released at "YYZ" with customs value 2500 CAD and tariff "8542310001"
    When the message is delivered to topic isdc
    And the shipment is deleted through the API
    Then no piece, commodity, party or special handling rows remain for the shipment

  Scenario: Malformed message leaves an unprocessed blob with error text (live Kafka only)
    Given a malformed shipment message
    When the message is delivered to topic isdc live only
    Then the blob stays unprocessed with error text
