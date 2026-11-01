Feature: CVLS Eligibility

  Scenario: Shipment at or below the LVS threshold is eligible
    Given a shipment imported by courier "04" with value 3000 at office "0504" with tariff "4901.99.00.91"
    When the shipment eligibility is evaluated
    Then the shipment is eligible for the CLVS Program
    And clvs_reason is blank

  Scenario: Shipment exactly at the threshold is eligible
    Given a shipment imported by courier "04" with value 3300 at office "0504" with tariff "4901.99.00.91"
    When the shipment eligibility is evaluated
    Then the shipment is eligible for the CLVS Program

  Scenario: Shipment over the threshold is not eligible
    Given a shipment imported by courier "04" with value 3300.01 at office "0504" with tariff "4901.99.00.91"
    When the shipment eligibility is evaluated
    Then the shipment is not eligible for the CLVS Program
    And clvs_reason is "value over threshold"

  Scenario: Shipment from an unauthorized courier is not eligible
    Given a shipment imported by courier "05" with value 3000 at office "0504" with tariff "4901.99.00.91"
    When the shipment eligibility is evaluated
    Then the shipment is not eligible for the CLVS Program
    And clvs_reason is "courier not authorized"

  Scenario: Shipment with controlled goods is not eligible
    Given a shipment imported by courier "04" with value 3000 at office "0504" with tariff "6110.20.00.01"
    When the shipment eligibility is evaluated
    Then the shipment is not eligible for the CLVS Program
    And clvs_reason is "controlled goods"
    And the shipment has 1 controlled commodity line

  Scenario: Shipment released at a non-designated office is not eligible
    Given a shipment imported by courier "04" with value 3000 at office "0469" with tariff "4901.99.00.91"
    When the shipment eligibility is evaluated
    Then the shipment is not eligible for the CLVS Program
    And clvs_reason is "office not designated"

  Scenario: Shipment with several failures lists every reason
    Given a shipment imported by courier "05" with value 4000 at office "0469" with tariff "4901.99.00.91"
    When the shipment eligibility is evaluated
    Then the shipment is not eligible for the CLVS Program
    And clvs_reason is "courier not authorized, value over threshold, office not designated"

  Scenario: Flagging a commodity line prohibited makes the shipment not eligible
    Given a shipment imported by courier "04" with value 3000 at office "0504" with tariff "4901.99.00.91"
    When the commodity line is flagged prohibited
    Then the shipment is not eligible for the CLVS Program
    And clvs_reason is "prohibited goods"
    And the shipment has 1 prohibited commodity line

  Scenario: Clearing the prohibited flag makes the shipment eligible again
    Given a shipment imported by courier "04" with value 3000 at office "0504" with tariff "4901.99.00.91"
    And the commodity line is flagged prohibited
    When the prohibited flag is cleared
    Then the shipment is eligible for the CLVS Program
    And the shipment has 0 prohibited commodity lines

  Scenario: Deleting the controlled commodity line makes the shipment eligible
    Given a shipment imported by courier "04" with value 3000 at office "0504" with tariff "6110.20.00.01"
    When the commodity line is deleted
    Then the shipment is eligible for the CLVS Program
    And the shipment has 0 controlled commodity lines

  Scenario: Raising the value over the threshold makes the shipment not eligible
    Given a shipment imported by courier "04" with value 3000 at office "0504" with tariff "4901.99.00.91"
    When the shipment value is changed to 4000
    Then the shipment is not eligible for the CLVS Program
    And clvs_reason is "value over threshold"

  Scenario: Lowering the value to the threshold makes the shipment eligible again
    Given a shipment imported by courier "04" with value 4000 at office "0504" with tariff "4901.99.00.91"
    When the shipment value is changed to 3300
    Then the shipment is eligible for the CLVS Program

  Scenario: Moving the clearance to a designated office makes the shipment eligible
    Given a shipment imported by courier "04" with value 3000 at office "0469" with tariff "4901.99.00.91"
    When the planned clearance office is changed to "0404"
    Then the shipment is eligible for the CLVS Program

  Scenario: Moving the clearance to a non-designated office makes the shipment not eligible
    Given a shipment imported by courier "04" with value 3000 at office "0504" with tariff "4901.99.00.91"
    When the planned clearance office is changed to "0469"
    Then the shipment is not eligible for the CLVS Program
    And clvs_reason is "office not designated"

  Scenario: Changing the courier to an authorized one makes the shipment eligible
    Given a shipment imported by courier "05" with value 3000 at office "0504" with tariff "4901.99.00.91"
    When the courier service type is changed to "04"
    Then the shipment is eligible for the CLVS Program
