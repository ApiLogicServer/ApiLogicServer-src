Feature: Check Credit
  # Traceability: logic/logic_discovery/check_credit.py  (Req §1)
  #   1. Customer.balance <= credit_limit
  #   2. Customer.balance = sum(Order.amount_total where date_shipped is null)
  #   3. Order.amount_total = sum(Item.amount)
  #   4. Item.amount = quantity * unit_price
  #   5. Item.unit_price copied from Product.unit_price
  # Product prices (verified in database/db.sqlite): Widget 90, Gadget 150

  Scenario: Create Order Rolls Up To Customer Balance
    Given Customer "Alice" with balance 0 and credit limit 1000
    And Order is created for "Alice"
    When Item is created with 5 Widget
    Then Item unit_price is 90
    Then Item amount is 450
    Then Order amount_total is 450
    Then Customer balance is 450

  Scenario: Update Item Quantity Recalculates Amounts
    Given Customer "Bob" with balance 0 and credit limit 1000
    And Order is created for "Bob"
    And Item is created with 2 Widget
    When Item quantity is changed to 6
    Then Item amount is 540
    Then Order amount_total is 540
    Then Customer balance is 540

  Scenario: Update Item Product Recopies Unit Price
    Given Customer "Carol" with balance 0 and credit limit 1000
    And Order is created for "Carol"
    And Item is created with 3 Widget
    When Item product is changed to Gadget
    Then Item unit_price is 150
    Then Item amount is 450
    Then Order amount_total is 450
    Then Customer balance is 450

  Scenario: Delete Item Reduces Order And Balance
    Given Customer "Dave" with balance 0 and credit limit 1000
    And Order is created for "Dave"
    And Item is created with 4 Widget
    When Item is deleted
    Then Order amount_total is 0
    Then Customer balance is 0

  Scenario: Change Order Customer Adjusts Both Balances
    Given Customer "Erin" with balance 0 and credit limit 1000
    And Customer "Frank" with balance 0 and credit limit 1000
    And Order is created for "Erin"
    And Item is created with 5 Widget
    When Order customer is changed to "Frank"
    Then Customer "Erin" balance is 0
    Then Customer "Frank" balance is 450

  Scenario: Ship Order Excludes From Balance
    Given Customer "Grace" with balance 0 and credit limit 1000
    And Order is created for "Grace"
    And Item is created with 5 Widget
    When Order is shipped
    Then Customer balance is 0

  Scenario: Unship Order Includes In Balance
    Given Customer "Heidi" with balance 0 and credit limit 1000
    And Order is created for "Heidi"
    And Item is created with 5 Widget
    And Order is shipped
    When Order is unshipped
    Then Customer balance is 450

  Scenario: Order Within Credit Limit Is Accepted
    Given Customer "Ivan" with balance 0 and credit limit 1000
    And Order is created for "Ivan"
    When Item is created with 10 Widget
    Then Order creation succeeded
    Then Customer balance is 900

  Scenario: Order Exceeding Credit Limit Is Rejected
    Given Customer "Judy" with balance 0 and credit limit 40
    And Order is created for "Judy"
    When Item is created with 5 Widget
    Then Item creation is rejected
    Then Customer balance is 0
