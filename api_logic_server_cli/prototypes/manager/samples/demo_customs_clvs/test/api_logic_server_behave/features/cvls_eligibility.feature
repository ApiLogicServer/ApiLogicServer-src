Feature: CVLS Eligibility

  Scenario: Shipment at or below the LVS threshold is eligible
    Given a CIMCorp shipment message from courier "04" released at "YYZ" with customs value 2500 CAD and tariff "8542310001"
    When the message is delivered to topic isdc
    Then the shipment is eligible for the CLVS Program
    And the clvs_reason is blank

  Scenario: Shipment exactly at the threshold is eligible
    Given a CIMCorp shipment message from courier "04" released at "YYZ" with customs value 3300 CAD and tariff "8542310001"
    When the message is delivered to topic isdc
    Then the shipment is eligible for the CLVS Program

  Scenario: Shipment just above the threshold is not eligible
    Given a CIMCorp shipment message from courier "04" released at "YYZ" with customs value 3300.01 CAD and tariff "8542310001"
    When the message is delivered to topic isdc
    Then the shipment is not eligible for the CLVS Program
    And the clvs_reason is "value exceeds CAD threshold"

  Scenario: Shipment from an unauthorized courier is not eligible
    Given a CIMCorp shipment message from courier "05" released at "YYZ" with customs value 2500 CAD and tariff "8542310001"
    When the message is delivered to topic isdc
    Then the shipment is not eligible for the CLVS Program
    And the clvs_reason is "not an authorized CLVS courier"

  Scenario: Controlled goods line makes the shipment not eligible
    Given a CIMCorp shipment message from courier "04" released at "YYZ" with customs value 2500 CAD and tariff "0207.14.00.10"
    When the message is delivered to topic isdc
    Then the shipment is not eligible for the CLVS Program
    And the clvs_reason is "controlled or regulated goods"

  Scenario: Prohibited commodity line makes the shipment not eligible
    Given a CIMCorp shipment message from courier "04" released at "YYZ" with customs value 2500 CAD and tariff "9301.10.00.00"
    When the message is delivered to topic isdc
    Then the shipment is not eligible for the CLVS Program
    And the clvs_reason is "prohibited commodity, controlled or regulated goods"

  Scenario: Release at an office that is not CLVS-designated is not eligible
    Given a CIMCorp shipment message from courier "04" released at "YCL" with customs value 2500 CAD and tariff "8542310001"
    When the message is delivered to topic isdc
    Then the shipment is not eligible for the CLVS Program
    And the clvs_reason is "release office not CLVS-designated"

  Scenario: Release at an unknown office is not eligible
    Given a CIMCorp shipment message from courier "04" released at "ZZZ" with customs value 2500 CAD and tariff "8542310001"
    When the message is delivered to topic isdc
    Then the shipment is not eligible for the CLVS Program
    And the clvs_reason is "release office unknown"

  Scenario: Several failed checks are listed together
    Given a CIMCorp shipment message from courier "05" released at "YCL" with customs value 5000 CAD and tariff "9301.10.00.00"
    When the message is delivered to topic isdc
    Then the shipment is not eligible for the CLVS Program
    And the clvs_reason is "not an authorized CLVS courier, value exceeds CAD threshold, prohibited commodity, controlled or regulated goods, release office not CLVS-designated"

  Scenario: Lowering the value makes the shipment eligible
    Given a CIMCorp shipment message from courier "04" released at "YYZ" with customs value 5000 CAD and tariff "8542310001"
    When the message is delivered to topic isdc
    And the shipment customs value is changed to 2000
    Then the shipment is eligible for the CLVS Program
    And the clvs_reason is blank

  Scenario: Raising the value above the threshold makes the shipment not eligible
    Given a CIMCorp shipment message from courier "04" released at "YYZ" with customs value 2500 CAD and tariff "8542310001"
    When the message is delivered to topic isdc
    And the shipment customs value is changed to 4000
    Then the shipment is not eligible for the CLVS Program
    And the clvs_reason is "value exceeds CAD threshold"

  Scenario: Changing a commodity to a controlled tariff makes the shipment not eligible
    Given a CIMCorp shipment message from courier "04" released at "YYZ" with customs value 2500 CAD and tariff "8542310001"
    When the message is delivered to topic isdc
    And the first commodity tariff is changed to "0207.14.00.10"
    Then the shipment is not eligible for the CLVS Program
    And the shipment has 1 controlled line and 0 prohibited lines

  Scenario: Changing the controlled commodity back makes the shipment eligible
    Given a CIMCorp shipment message from courier "04" released at "YYZ" with customs value 2500 CAD and tariff "0207.14.00.10"
    When the message is delivered to topic isdc
    And the first commodity tariff is changed to "8542310001"
    Then the shipment is eligible for the CLVS Program
    And the shipment has 0 controlled lines and 0 prohibited lines

  Scenario: Adding a prohibited commodity line makes the shipment not eligible
    Given a CIMCorp shipment message from courier "04" released at "YYZ" with customs value 2500 CAD and tariff "8542310001"
    When the message is delivered to topic isdc
    And a second commodity line with tariff "9301.10.00.00" is added
    Then the shipment is not eligible for the CLVS Program
    And the shipment has 1 controlled line and 1 prohibited lines

  Scenario: Deleting the controlled commodity line makes the shipment eligible
    Given a CIMCorp shipment message from courier "04" released at "YYZ" with customs value 2500 CAD and tariff "8542310001"
    When the message is delivered to topic isdc
    And a second commodity line with tariff "0207.14.00.10" is added
    And the second commodity line is deleted
    Then the shipment is eligible for the CLVS Program
    And the shipment has 0 controlled lines and 0 prohibited lines

  Scenario: Moving the release location to a non-designated office makes the shipment not eligible
    Given a CIMCorp shipment message from courier "04" released at "YYZ" with customs value 2500 CAD and tariff "8542310001"
    When the message is delivered to topic isdc
    And the shipment release location is changed to "YCL"
    Then the shipment is not eligible for the CLVS Program
    And the clvs_reason is "release office not CLVS-designated"
