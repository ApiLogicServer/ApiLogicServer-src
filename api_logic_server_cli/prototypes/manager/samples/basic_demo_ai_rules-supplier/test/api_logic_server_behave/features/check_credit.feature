Feature: Check Credit

  # The Customer's balance is less than the credit limit; balance = sum of unshipped Order amount_total;
  # Order amount_total = sum of Item amount; Item amount = quantity * unit_price;
  # Product count suppliers = count of Product Suppliers; Item unit_price chosen by AI among the product's suppliers.

  Scenario: Credit - within limit
    Given a customer with credit limit 1000
    And a product priced 10 with no suppliers
    When an order is created with 5 of the product
    Then the customer balance is 50
    And the order amount total is 50
    And the item amount is 50

  Scenario: Credit - at the limit
    Given a customer with credit limit 100
    And a product priced 10 with no suppliers
    When an order is created with 10 of the product
    Then the customer balance is 100

  Scenario: Credit - over the limit
    Given a customer with credit limit 100
    And a product priced 10 with no suppliers
    When an order is created with 11 of the product
    Then the item is rejected with a message containing "exceeds credit limit"
    And the customer balance is 0

  Scenario: Balance - ship and unship
    Given a customer with credit limit 1000
    And a product priced 10 with no suppliers
    And an order is created with 5 of the product
    When the order is shipped
    Then the customer balance is 0
    When the order is un-shipped
    Then the customer balance is 50

  Scenario: Balance - move order
    Given a customer with credit limit 1000
    And a second customer with credit limit 1000
    And a product priced 10 with no suppliers
    And an order is created with 5 of the product
    When the order is moved to the second customer
    Then the customer balance is 0
    And the second customer balance is 50

  Scenario: Balance - delete order
    Given a customer with credit limit 1000
    And a product priced 10 with no suppliers
    And an order is created with 5 of the product
    When the order and its item are deleted
    Then the customer balance is 0

  Scenario: Item - change quantity
    Given a customer with credit limit 1000
    And a product priced 10 with no suppliers
    And an order is created with 5 of the product
    When the item quantity is changed to 8
    Then the item amount is 80
    And the order amount total is 80
    And the customer balance is 80

  Scenario: Item - delete
    Given a customer with credit limit 1000
    And a product priced 10 with no suppliers
    And an order is created with 5 of the product
    And a second item is added with 2 of the product
    When the item is deleted
    Then the order amount total is 20
    And the customer balance is 20

  Scenario: Item - move to order
    Given a customer with credit limit 1000
    And a product priced 10 with no suppliers
    And an order is created with 5 of the product
    And a second order is created with 2 of the product
    When the item is moved to the second order
    Then the order amount total is 0
    And the second order amount total is 70
    And the customer balance is 70

  Scenario: Item - change product
    Given a customer with credit limit 1000
    And a product priced 10 with no suppliers
    And a second product priced 30 with no suppliers
    And an order is created with 5 of the product
    When the item product is changed to the second product
    Then the item unit price is 30
    And the item amount is 150

  Scenario: Suppliers - add and remove
    Given a customer with credit limit 1000
    And a product priced 10 with no suppliers
    When a supplier is added to the product costing 7
    Then the product supplier count is 1
    When a second supplier is added to the product costing 9
    Then the product supplier count is 2
    When the first supplier is removed from the product
    Then the product supplier count is 1

  Scenario: Suppliers - move
    Given a customer with credit limit 1000
    And a product priced 10 with no suppliers
    And a second product priced 20 with no suppliers
    And a supplier is added to the product costing 7
    When the product supplier is moved to the second product
    Then the product supplier count is 0
    And the second product supplier count is 1

  Scenario: AI - no suppliers
    Given a customer with credit limit 1000
    And a product priced 10 with no suppliers
    When an order is created with 5 of the product
    Then the item unit price is 10
    And no AI audit row exists for the item

  Scenario: AI - chooses a supplier
    Given a customer with credit limit 1000
    And a product priced 50 with suppliers costing 7 and 9
    When an order is created with 5 of the product
    Then the AI chose one of the product suppliers and an audit row exists
    And the item amount is the quantity times the chosen price
    And the customer balance is the item amount

  Scenario: AI - product change
    Given a customer with credit limit 1000
    And a product priced 10 with no suppliers
    And a second product priced 50 with suppliers costing 7 and 9
    And an order is created with 5 of the product
    When the item product is changed to the second product
    Then the AI chose one of the product suppliers and an audit row exists
