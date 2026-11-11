Feature: Check Credit

  Scenario: Good Order with AI supplier selection
    Given a customer with credit limit 5000
    When an order is placed with 2 Egyptian Cotton Sheets
    Then the item unit_price is one of the product's supplier costs
    And an audit row exists linked to the item with a chosen supplier of that product
    And the order amount_total is quantity times unit_price
    And the customer balance equals the order amount_total

  Scenario: Item Quantity Change
    Given a customer with credit limit 5000
    And an order is placed with 2 Egyptian Cotton Sheets
    When the item quantity is changed to 3
    Then the order amount_total is quantity times unit_price
    And the customer balance equals the order amount_total

  Scenario: Delete Item
    Given a customer with credit limit 5000
    And an order is placed with 2 Egyptian Cotton Sheets
    When the item is deleted
    Then the order amount_total is 0
    And the customer balance is 0

  Scenario: Move Item to Another Order
    Given a customer with credit limit 5000
    And an order is placed with 2 Egyptian Cotton Sheets
    And a second order for a second customer exists
    When the item is moved to the second order
    Then the first order amount_total is 0 and the first customer balance is 0
    And the second customer balance equals the item amount

  Scenario: Ship Order Leaves Balance
    Given a customer with credit limit 5000
    And an order is placed with 2 Egyptian Cotton Sheets
    When the order is shipped
    Then the customer balance is 0

  Scenario: Unship Order Enters Balance
    Given a customer with credit limit 5000
    And an order is placed with 2 Egyptian Cotton Sheets
    And the order is shipped
    When the order is unshipped
    Then the customer balance equals the order amount_total

  Scenario: Credit Limit Boundary Accepted
    Given a customer whose credit limit equals the cost of 2 Egyptian Cotton Sheets
    When an order is placed with 2 Egyptian Cotton Sheets
    Then the order is accepted

  Scenario: Exceed Credit Rejected
    Given a customer with credit limit 1
    When an order is placed with 2 Egyptian Cotton Sheets
    Then the item is rejected with "exceeds credit limit"

  Scenario: Product Without Suppliers Uses Product Price
    Given a customer with credit limit 5000
    When an order is placed with 2 Widget
    Then the item unit_price equals the Widget product price
    And no audit row exists for the item

  Scenario: Supplier Count Adjusts
    Given a new product with no suppliers
    When a supplier is added to the new product
    Then the product count_suppliers is 1
    And when the product supplier is deleted the product count_suppliers is 0
