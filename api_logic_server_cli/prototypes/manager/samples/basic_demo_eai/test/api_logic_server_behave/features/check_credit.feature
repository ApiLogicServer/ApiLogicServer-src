Feature: Check Credit

  Scenario: Good order is priced and added to the balance
    Given a new customer "Pat" with credit limit 1000
    When a B2B order is placed for "Pat" with 2 Widget and 1 Gadget
    Then the order is accepted
    And the item prices are copied from the products
    And each item amount is quantity times unit price
    And the order total is 330
    And the balance of "Pat" is 330

  Scenario: Changing an item quantity re-derives amount, total and balance
    Given a new customer "Quinn" with credit limit 2000
    And a B2B order is placed for "Quinn" with 2 Widget and 1 Gadget
    When the quantity of the first item is changed to 5
    Then the first item amount is 450
    And the order total is 600
    And the balance of "Quinn" is 600

  Scenario: Changing an item's product re-copies the price
    Given a new customer "Ravi" with credit limit 2000
    And a B2B order is placed for "Ravi" with 2 Widget
    When the product of the first item is changed to Doodad
    Then the first item unit price is 110
    And the first item amount is 220
    And the order total is 220
    And the balance of "Ravi" is 220

  Scenario: Deleting an item reduces the order total and balance
    Given a new customer "Sam" with credit limit 2000
    And a B2B order is placed for "Sam" with 2 Widget and 1 Gadget
    When the first item is deleted
    Then the order total is 150
    And the balance of "Sam" is 150

  Scenario: Moving an item to another order adjusts both orders
    Given a new customer "Tara" with credit limit 5000
    And a B2B order is placed for "Tara" with 2 Widget and 1 Gadget
    And a second B2B order is placed for "Tara" with 1 Doodad
    When the first item of the first order is moved to the second order
    Then the first order total is 150
    And the second order total is 290
    And the balance of "Tara" is 440

  Scenario: Moving an order to another customer adjusts both balances
    Given a new customer "Uma" with credit limit 2000
    And a new customer "Vic" with credit limit 2000
    And a B2B order is placed for "Uma" with 2 Widget and 1 Gadget
    When the order is moved to customer "Vic"
    Then the balance of "Uma" is 0
    And the balance of "Vic" is 330

  Scenario: Deleting an order reduces the balance
    Given a new customer "Wen" with credit limit 2000
    And a B2B order is placed for "Wen" with 1 Gadget
    When the order is deleted
    Then the balance of "Wen" is 0

  Scenario: Shipping an order removes it from the balance
    Given a new customer "Xia" with credit limit 2000
    And a B2B order is placed for "Xia" with 2 Widget and 1 Gadget
    When the order is shipped
    Then the balance of "Xia" is 0

  Scenario: Unshipping an order adds it back to the balance
    Given a new customer "Yan" with credit limit 2000
    And a B2B order is placed for "Yan" with 2 Widget and 1 Gadget
    And the order is shipped
    When the order is unshipped
    Then the balance of "Yan" is 330

  Scenario: Order exactly at the credit limit is accepted
    Given a new customer "Zed" with credit limit 300
    When a B2B order is placed for "Zed" with 2 Gadget
    Then the order is accepted
    And the balance of "Zed" is 300

  Scenario: Order over the credit limit is rejected
    Given a new customer "Abe" with credit limit 299
    When a B2B order is placed for "Abe" with 2 Gadget
    Then the order is rejected with "exceeds credit limit"
    And the balance of "Abe" is 0

  Scenario: Raising a quantity over the credit limit is rejected
    Given a new customer "Bea" with credit limit 500
    And a B2B order is placed for "Bea" with 2 Widget and 1 Gadget
    When the quantity of the first item is changed to 10
    Then the change is rejected with "exceeds credit limit"
    And the first item amount is 180
    And the balance of "Bea" is 330
