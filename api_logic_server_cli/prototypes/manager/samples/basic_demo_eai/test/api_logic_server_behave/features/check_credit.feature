Feature: Check Credit

  # Rules: Customer.balance <= credit_limit; Customer.balance = sum of unshipped Order.amount_total;
  #        Order.amount_total = sum(Item.amount); Item.amount = quantity * unit_price; Item.unit_price copied from Product

  Scenario: Good Order Placed
    Given Customer "Alice" with credit limit 5000
    When B2B order placed for "Alice" with 2 Widget
    Then Customer balance should be 180
    And Order amount_total should be 180

  Scenario: Item Quantity Changed
    Given Customer "Bob" with credit limit 5000
    And Order is created for "Bob" with 2 Widget
    When Item quantity changed to 3
    Then Customer balance should be 270

  Scenario: Shipped Order Leaves Balance
    Given Customer "Carol" with credit limit 5000
    And Order is created for "Carol" with 2 Widget
    When Order is shipped
    Then Customer balance should be 0

  Scenario: Order Exceeding Credit Rejected
    Given Customer "Dave" with credit limit 100
    When B2B order placed for "Dave" with 2 Widget
    Then Order is rejected with a credit limit message
    And Customer balance should be 0
