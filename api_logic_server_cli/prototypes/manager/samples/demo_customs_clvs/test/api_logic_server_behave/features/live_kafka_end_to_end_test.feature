Feature: Live Kafka end-to-end test

  Scenario: Message sent through Kafka creates the blob, shipment and importer party (live Kafka only)
    Given a CIMCorp shipment message from courier "04" released at "YYZ" with customs value 2500 CAD and tariff "8542310001"
    And the message names the importer account of customer "ACME IMPORTS INC"
    When the message is delivered to topic isdc live only
    Then the blob is processed without error text
    And the shipment is persisted with 1 piece, 1 commodity and 3 parties
    And the shipment has an importer party copied from customer "ACME IMPORTS INC"
