Feature: Order Processing with Business Logic

  # This feature tests the complete order processing business logic including:
  # 1. Customer.balance = sum(Order.amount_total where date_shipped is null)
  # 2. Order.amount_total = sum(Item.amount)
  # 3. Item.amount = quantity * unit_price (with 10% carbon neutral discount)
  # 4. Item.unit_price copied from Product.unit_price
  # 5. Customer.balance <= credit_limit constraint
  # 6. WHERE clause testing (shipped/unshipped orders)
  
  # Phase 2: Uses OrderB2B custom API for CREATE operations
  # Phase 1: Uses CRUD API for UPDATE/DELETE operations (granular testing)

  Scenario: Good Order Placed
    Given Customer "Bob" with balance 0 and credit limit 3000
     When B2B order placed for "Bob" with 2 Widget
     Then Order created successfully
      And Customer balance should be 180
      And Order amount_total should be 180

  Scenario: Alter Item Quantity Increases Balance
    Given Customer "Diana" with balance 0 and credit limit 1000
      And Order exists for "Diana" with 1 Gadget quantity 1
     When Item quantity changed to 3
     Then Item amount should be 450
      And Order amount_total should be 450
      And Customer balance should be 450

  Scenario: Delete Item Decreases Balance
    Given Customer "Charlie" with balance 0 and credit limit 5000
      And Order exists for "Charlie" with 2 Widget quantity 1
     When Second item is deleted
     Then Order amount_total should be 90
      And Customer balance should be 90

  Scenario: Change Item Product Updates Amounts
    Given Customer "Bob" with balance 0 and credit limit 3000
      And Order exists for "Bob" with 1 Widget quantity 2
     When Item product changed from Widget to Gadget
     Then Item unit_price should be 150
      And Item amount should be 300
      And Order amount_total should be 300
      And Customer balance should be 300

  Scenario: Change Order Customer Adjusts Both Balances
    Given Customer "Alice" with balance 0 and credit limit 5000
      And Customer "Bob" with balance 0 and credit limit 3000
      And Order exists for "Alice" with 1 Widget quantity 2
     When Order customer changed from "Alice" to "Bob"
     Then Customer "Alice" balance should be 0
      And Customer "Bob" balance should be 180

  Scenario: Ship Order Excludes From Balance
    Given Customer "Diana" with balance 0 and credit limit 1000
      And Order exists for "Diana" with 2 Gadget quantity 1
     When Order is shipped
     Then Customer balance should be 0
      And Order amount_total should be 300

  Scenario: Unship Order Includes In Balance
    Given Customer "Bob" with balance 0 and credit limit 3000
      And Shipped order exists for "Bob" with 1 Widget quantity 1
     When Order is unshipped
     Then Customer balance should be 90
      And Order amount_total should be 90

  Scenario: Exceed Credit Limit Rejected
    Given Customer "Diana" with balance 0 and credit limit 1000
     When B2B order placed for "Diana" with 7 Gadget
     Then Order should be rejected
      And Error message should contain "exceeds credit limit"

  Scenario: Carbon Neutral Discount Applied
    Given Customer "Bob" with balance 0 and credit limit 3000
      And Product "Widget" is carbon neutral
     When B2B order placed for "Bob" with 10 carbon neutral Widget
     Then Item amount should be 810
      And Order amount_total should be 810
      And Customer balance should be 810

  Scenario: Multiple Items Order Processing
    Given Customer "Bob" with balance 0 and credit limit 3000
     When B2B order placed for "Bob" with multiple items:
       | Product    | Quantity |
       | Widget     | 1        |
       | Gadget     | 2        |
       | Green      | 1        |
     Then Order created successfully
      And Order should have 3 items
      And Customer balance should be 499
