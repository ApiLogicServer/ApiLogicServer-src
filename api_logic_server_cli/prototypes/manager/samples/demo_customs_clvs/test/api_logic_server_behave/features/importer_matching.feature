Feature: Importer matching

  Scenario: Importer account matches a customer
    Given a CIMCorp shipment message from courier "04" released at "YYZ" with customs value 2500 CAD and tariff "8542310001"
    And the message names the importer account of customer "ACME IMPORTS INC"
    When the message is delivered to topic isdc
    Then the shipment has an importer party copied from customer "ACME IMPORTS INC"

  Scenario: Importer account matches no customer
    Given a CIMCorp shipment message from courier "04" released at "YYZ" with customs value 2500 CAD and tariff "8542310001"
    And the message names an importer account that no customer has
    When the message is delivered to topic isdc
    Then the shipment is persisted with 1 piece, 1 commodity and 2 parties
    And the shipment has no importer party

  Scenario: Replayed message keeps exactly one importer party
    Given a CIMCorp shipment message from courier "04" released at "YYZ" with customs value 2500 CAD and tariff "8542310001"
    And the message names the importer account of customer "ACME IMPORTS INC"
    When the message is delivered to topic isdc
    And the same message is delivered to topic isdc again
    Then the shipment has exactly 1 importer party

  Scenario: Updating the shipment does not add another importer party
    Given a CIMCorp shipment message from courier "04" released at "YYZ" with customs value 2500 CAD and tariff "8542310001"
    And the message names the importer account of customer "ACME IMPORTS INC"
    When the message is delivered to topic isdc
    And the shipment cargo description is changed
    Then the shipment has exactly 1 importer party
