Feature: Check Credit

  Scenario: Order placed within the credit limit
    Given a new customer with credit limit 1000
    When an order is placed with 2 Widget
    Then the item amount is 180
    And the order total is 180
    And the customer balance is 180
    And Logic adjusts the customer balance from the order total

  Scenario: Item quantity change flows to the order total and balance
    Given a new customer with credit limit 1000
    And an order is placed with 2 Widget
    When the item quantity is changed to 5
    Then the item amount is 450
    And the order total is 450
    And the customer balance is 450

  Scenario: Shipping an order removes it from the balance
    Given a new customer with credit limit 1000
    And an order is placed with 2 Widget
    When the order is shipped
    Then the customer balance is 0

  Scenario: Moving an order to another customer moves the balance
    Given a new customer with credit limit 1000
    And a second customer with credit limit 1000
    And an order is placed with 2 Widget
    When the order is moved to the second customer
    Then the customer balance is 0
    And the second customer balance is 180

  Scenario: Order over the credit limit is rejected
    Given a new customer with credit limit 100
    When an order is placed with 2 Widget
    Then the request is rejected with "exceeds credit limit"
    And the customer balance is 0

  Scenario: Balance equal to the credit limit is accepted
    Given a new customer with credit limit 180
    When an order is placed with 2 Widget
    Then the request is accepted
    And the customer balance is 180

  Scenario: Lowering the credit limit below the balance is rejected
    Given a new customer with credit limit 1000
    And an order is placed with 2 Widget
    When the credit limit is changed to 100
    Then the request is rejected with "exceeds credit limit"

  Scenario: Product price change does not alter existing items
    Given a new customer with credit limit 1000
    And a new product priced 50
    And an order is placed with 2 of the new product
    When the product price is changed to 80
    Then the item unit price is 50
    And the item amount is 100

  Scenario: Deleting an order deletes its items
    Given a new customer with credit limit 1000
    And an order is placed with 2 Widget
    When the order is deleted
    Then the order has no items
    And the customer balance is 0

  Scenario: Item for an unknown product is rejected
    Given a new customer with credit limit 1000
    And an empty order
    When an item is added for product id 999999
    Then the request is rejected with "Missing Parent"
