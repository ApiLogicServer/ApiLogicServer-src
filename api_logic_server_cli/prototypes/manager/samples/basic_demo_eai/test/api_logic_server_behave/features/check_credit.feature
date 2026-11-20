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

  Scenario: Order At Credit Limit Accepted
    Given Customer "Erin" with credit limit 180
    When B2B order placed for "Erin" with 2 Widget
    Then Order is accepted
    And Customer balance should be 180

  Scenario: Unshipped Order Enters Balance
    Given Customer "Fay" with credit limit 5000
    And Order is created for "Fay" with 2 Widget
    And Order has been shipped
    When Order is unshipped
    Then Customer balance should be 180

  Scenario: Item Deleted Reduces Order
    Given Customer "Gus" with credit limit 5000
    And Order is created for "Gus" with 2 Widget and 1 Gadget
    When the Gadget Item is deleted
    Then Order amount_total should be 180
    And Customer balance should be 180

  Scenario: Order Deleted Leaves Balance
    Given Customer "Hank" with credit limit 5000
    And Order is created for "Hank" with 2 Widget
    When Order is deleted
    Then Customer balance should be 0

  Scenario: Order Moved To Another Customer
    Given Customer "Ivy" with credit limit 5000
    And Customer "Jack" with credit limit 5000
    And Order is created for "Ivy" with 2 Widget
    When Order is moved to Customer "Jack"
    Then Customer "Ivy" balance should be 0
    And Customer "Jack" balance should be 180

  Scenario: Item Moved To Another Order
    Given Customer "Kim" with credit limit 5000
    And Order is created for "Kim" with 2 Widget
    And a second Order is created for "Kim" with 1 Gadget
    When the Widget Item is moved to the second Order
    Then Order amount_total should be 0
    And second Order amount_total should be 330
    And Customer balance should be 330

  Scenario: Item Product Changed
    Given Customer "Lee" with credit limit 5000
    And Order is created for "Lee" with 2 Widget
    When the Item product is changed to Gadget
    Then Item unit_price should be 150
    And Order amount_total should be 300
    And Customer balance should be 300
