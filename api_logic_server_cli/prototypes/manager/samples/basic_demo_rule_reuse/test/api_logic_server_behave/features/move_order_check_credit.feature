Feature: Move Order Check Credit

  Scenario: Moving an Order adjusts both balances
    Given Customer "Ann" with credit limit 1000
    And Customer "Bob" with credit limit 1000
    And Order "O1" is created for "Ann" with 2 Gadget
    When Order "O1" is moved to Customer "Bob"
    Then the transaction is accepted
    And Customer "Ann" balance is 0
    And Customer "Bob" balance is 300

  Scenario: Moving an Order over the new Customer's limit is rejected
    Given Customer "Ann" with credit limit 1000
    And Customer "Bob" with credit limit 200
    And Order "O1" is created for "Ann" with 2 Gadget
    When Order "O1" is moved to Customer "Bob"
    Then the transaction is rejected with "exceeds credit limit"
    And Customer "Ann" balance is 300
    And Customer "Bob" balance is 0
