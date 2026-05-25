Feature: Check Credit Rules

  Scenario: Good Order - balance updated
    Given Customer with credit limit 1000
    When Order is placed with 2 Chai
    Then Customer balance is 36.0

  Scenario: Exceed Credit Limit - rejected
    Given Customer with credit limit 20
    When Order is placed with 2 Chai
    Then Order is rejected with credit limit error

  Scenario: Item Quantity Change - recalculates
    Given Customer with credit limit 1000
    And Order is placed with 2 Chai
    When Item quantity changed to 5
    Then Item amount is 90.0
    Then Order amount_total is 90.0

  Scenario: Delete Item - reduces order total
    Given Customer with credit limit 1000
    And Order is placed with 2 Chai and 1 Chang
    When Item is deleted
    Then Order amount_total is 19.0

  Scenario: Ship Order - excluded from balance
    Given Customer with credit limit 1000
    And Order is placed with 2 Chai
    When Order is shipped
    Then Customer balance is 0.0

  Scenario: Unship Order - included in balance
    Given Customer with credit limit 1000
    And Shipped order is created with 2 Chai
    When Order is unshipped
    Then Customer balance is 36.0
