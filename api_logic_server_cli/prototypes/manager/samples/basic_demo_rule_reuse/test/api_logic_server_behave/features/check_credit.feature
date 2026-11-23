Feature: Check Credit

  Scenario: Order with Item is created
    Given Customer "Ann" with credit limit 1000
    When Order "O1" is created for "Ann" with 2 Gadget
    Then Item of Order "O1" has unit_price 150 and amount 300
    And Order "O1" amount_total is 300
    And Customer "Ann" balance is 300

  Scenario: Item quantity is changed
    Given Customer "Ann" with credit limit 1000
    And Order "O1" is created for "Ann" with 2 Gadget
    When Item of Order "O1" quantity is changed to 3
    Then Item of Order "O1" has unit_price 150 and amount 450
    And Order "O1" amount_total is 450
    And Customer "Ann" balance is 450

  Scenario: Item product is changed
    Given Customer "Ann" with credit limit 1000
    And Order "O1" is created for "Ann" with 2 Gadget
    When Item of Order "O1" product is changed to Widget
    Then Item of Order "O1" has unit_price 90 and amount 180
    And Order "O1" amount_total is 180
    And Customer "Ann" balance is 180

  Scenario: Item is deleted
    Given Customer "Ann" with credit limit 1000
    And Order "O1" is created for "Ann" with 2 Gadget
    When Item of Order "O1" is deleted
    Then Order "O1" amount_total is 0
    And Customer "Ann" balance is 0

  Scenario: Item is moved to another Order
    Given Customer "Ann" with credit limit 1000
    And Order "O1" is created for "Ann" with 2 Gadget
    And Order "O2" is created for "Ann" with 1 Widget
    When Item of Order "O1" is moved to Order "O2"
    Then Order "O1" amount_total is 0
    And Order "O2" amount_total is 390
    And Customer "Ann" balance is 390

  Scenario: Order is deleted
    Given Customer "Ann" with credit limit 1000
    And Order "O1" is created for "Ann" with 2 Gadget
    And Order "O2" is created for "Ann" with 1 Widget
    When Order "O1" is deleted
    Then Customer "Ann" balance is 90

  Scenario: Shipped Order leaves the balance
    Given Customer "Ann" with credit limit 1000
    And Order "O1" is created for "Ann" with 2 Gadget
    When Order "O1" is shipped
    Then Customer "Ann" balance is 0

  Scenario: Unshipped Order re-enters the balance
    Given Customer "Ann" with credit limit 1000
    And Order "O1" is created for "Ann" with 2 Gadget
    And Order "O1" is shipped
    When Order "O1" is unshipped
    Then Customer "Ann" balance is 300

  Scenario: Order within the credit limit is accepted
    Given Customer "Ann" with credit limit 1000
    When Order "O1" is created for "Ann" with 3 Gadget
    Then the transaction is accepted
    And Customer "Ann" balance is 450

  Scenario: Order exactly at the credit limit is accepted
    Given Customer "Ann" with credit limit 300
    When Order "O1" is created for "Ann" with 2 Gadget
    Then the transaction is accepted
    And Customer "Ann" balance is 300

  Scenario: Order over the credit limit is rejected
    Given Customer "Ann" with credit limit 200
    When Order "O1" is created for "Ann" with 2 Gadget
    Then the transaction is rejected with "exceeds credit limit"
    And Customer "Ann" balance is 0
