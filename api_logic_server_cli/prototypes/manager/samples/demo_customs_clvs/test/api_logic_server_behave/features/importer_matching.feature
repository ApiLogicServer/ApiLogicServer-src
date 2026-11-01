Feature: Importer matching

  Scenario: Shipment with a matching customer gets an importer party
    Given a shipment message for account 451000001 with value 2500
    When the message is delivered to topic isdc
    Then the shipment has an importer party for "ACME IMPORTS INC"

  Scenario: Shipment with no matching customer gets no importer party
    Given a shipment message for account 999000099 with value 2500
    When the message is delivered to topic isdc
    Then the shipment has no importer party
    And the shipment is persisted with 1 piece, 2 parties and 1 commodity
