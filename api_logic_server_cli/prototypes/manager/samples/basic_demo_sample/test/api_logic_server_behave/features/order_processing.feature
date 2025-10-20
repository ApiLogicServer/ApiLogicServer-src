Feature: Order Processing with Business Logic

  # Phase 2: CREATE using OrderB2B custom API
  # Phase 1: UPDATE/DELETE using CRUD for granular rule testing

  Scenario: Good Order Placed via B2B API
    Given Customer "Alice" with balance 0 and credit limit 1000
    When B2B order placed for "Alice" with 5 Widget
    Then Customer balance should be 450
    And Order amount_total should be 450
    And Order created successfully

  Scenario: Item Quantity Update Recalculates Amounts
    Given Customer "Bob" with balance 0 and credit limit 2000
    And Order exists for "Bob" with 5 Widget
    When Item quantity changed to 10
    Then Item amount should be 900
    And Order amount_total should be 900
    And Customer balance should be 900

  Scenario: Change Order Customer Adjusts Both Balances
    Given Customer "Charlie" with balance 0 and credit limit 1500
    And Customer "Diana" with balance 0 and credit limit 2000
    And Order exists for "Charlie" with 2 Gadget
    When Order customer changed to "Diana"
    Then Customer "Charlie" balance should be 0
    And Customer "Diana" balance should be 300

  Scenario: Delete Item Reduces Order Total and Customer Balance
    Given Customer "TestCustomer" with balance 0 and credit limit 3000
    And Order exists for "TestCustomer" with 3 Widget and 2 Gadget
    When First item deleted
    Then Order amount_total should be 300
    And Customer balance should be 300

  Scenario: Ship Order Excludes from Balance (WHERE exclude)
    Given Customer "ShipTest" with balance 0 and credit limit 5000
    And Order exists for "ShipTest" with 10 Widget
    When Order is shipped
    Then Customer balance should be 0

  Scenario: Unship Order Includes in Balance (WHERE include)
    Given Customer "UnshipTest" with balance 0 and credit limit 5000
    And Shipped order exists for "UnshipTest" with 5 Gadget
    When Order is unshipped
    Then Customer balance should be 750

  Scenario: Exceed Credit Limit Rejected (Constraint FAIL)
    Given Customer "LimitTest" with balance 0 and credit limit 500
    When B2B order placed for "LimitTest" with 10 Gadget
    Then Order creation should fail
    And Error message should contain "credit limit"

  Scenario: Carbon Neutral Discount Applied (Custom Logic)
    Given Customer "GreenBuyer" with balance 0 and credit limit 2000
    When B2B order placed for "GreenBuyer" with 10 carbon neutral Gadget
    Then Item amount should be 1350
    And Order amount_total should be 1350
    And Customer balance should be 1350

  Scenario: Product Unit Price Copied to Item
    Given Customer "PriceCopy" with balance 0 and credit limit 3000
    When B2B order placed for "PriceCopy" with 1 Green
    Then Item unit_price should be 109

  Scenario: Change Product Updates Unit Price (FK Change)
    Given Customer "ProductChange" with balance 0 and credit limit 5000
    And Order exists for "ProductChange" with 2 Widget
    When Item product changed to "Gadget"
    Then Item unit_price should be 150
    And Item amount should be 300
    And Order amount_total should be 300
