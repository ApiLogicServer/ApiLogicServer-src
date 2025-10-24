Feature: Order Processing with Business Logic

  # Tests all declarative rules:
  # 1. Customer.balance = sum(Order.amount_total) WHERE date_shipped is None
  # 2. Order.amount_total = sum(Item.amount)
  # 3. Item.amount = quantity * unit_price (with 10% carbon neutral discount for qty >= 10)
  # 4. Item.unit_price copied from Product.unit_price
  # 5. Customer.balance <= credit_limit constraint
  # 6. Kafka integration when order shipped

  Scenario: Good Order Placed via B2B API
    Given Customer "Alice" with balance 0 and credit limit 5000
    When B2B order placed for "Alice" with 5 Widget
    Then Customer balance should be 450
    And Order amount_total should be 450
    And Item amount should be 450
    And Item unit_price should be 90

  Scenario: Multi-Item Order via B2B API
    Given Customer "Bob" with balance 0 and credit limit 3000
    When B2B order placed for "Bob" with 3 Widget and 2 Gadget
    Then Customer balance should be 570
    And Order amount_total should be 570

  Scenario: Carbon Neutral Discount Applied
    Given Customer "Diana" with balance 0 and credit limit 5000
    When B2B order placed for "Diana" with 10 carbon neutral Gadget
    Then Customer balance should be 1350
    And Item amount should be 1350
    
  Scenario: Item Quantity Change
    Given Customer "Charlie" with balance 0 and credit limit 2000
    And Order is created for "Charlie" with 5 Widget
    When Item quantity changed to 10
    Then Item amount should be 900
    And Order amount_total should be 900
    And Customer balance should be 900

  Scenario: Change Product in Item
    Given Customer "Alice" with balance 0 and credit limit 5000
    And Order is created for "Alice" with 5 Widget
    When Item product changed to "Gadget"
    Then Item unit_price should be 150
    And Item amount should be 750
    And Order amount_total should be 750
    And Customer balance should be 750

  Scenario: Delete Item Reduces Order
    Given Customer "Bob" with balance 0 and credit limit 3000
    And Order is created for "Bob" with 3 Widget and 2 Gadget
    When First item is deleted
    Then Order amount_total should be 300
    And Customer balance should be 300

  Scenario: Change Order Customer
    Given Customer "Alice" with balance 0 and credit limit 5000
    And Customer "Bob" with balance 0 and credit limit 3000
    And Order is created for "Alice" with 5 Widget
    When Order customer changed to "Bob"
    Then Customer "Alice" balance should be 0
    And Customer "Bob" balance should be 450

  Scenario: Ship Order Excludes from Balance
    Given Customer "Charlie" with balance 0 and credit limit 2000
    And Order is created for "Charlie" with 2 Widget
    When Order is shipped
    Then Customer balance should be 0
    And Order amount_total should be 180

  Scenario: Unship Order Includes in Balance
    Given Customer "Diana" with balance 0 and credit limit 5000
    And Shipped order is created for "Diana" with 3 Gadget
    When Order is unshipped
    Then Customer balance should be 450
    And Order amount_total should be 450

  Scenario: Exceed Credit Limit Rejected
    Given Customer "Silent" with balance 0 and credit limit 1000
    When B2B order placed for "Silent" with 20 Widget
    Then Order should be rejected
    And Error message should contain "exceeds credit limit"
