Feature: Check Credit

  Scenario: Good Order Placed
    Given Customer with balance 0 and credit 1000
    When Good Order Placed
    Then Balance is 50
    Then Customer balance does not exceed credit limit

  Scenario: Bad Order Exceeds Credit
    Given Customer with balance 900 and credit 1000
    When Order Placed with quantity 200
    Then Error raised containing "balance"
    Then Error raised containing "credit limit"

  Scenario: Alter Item Quantity to Exceed Credit
    Given Customer with balance 0 and credit 1000
    And Order with 1 item quantity 10
    When Item quantity changed to 1500
    Then Error raised containing "balance"
    Then Error raised containing "credit limit"

  Scenario: Change Product on Item
    Given Customer with balance 0 and credit 1000
    And Order with 1 item quantity 10
    When Item product changed to expensive product
    Then Balance recalculates with new price
    Then Item unit_price updated from new product

  Scenario: Change Customer on Order
    Given Two customers with balance 0
    And Order for first customer with balance 100
    When Order moved to second customer
    Then First customer balance is 0
    Then Second customer balance is 100

  Scenario: Delete Item Adjusts Balance
    Given Customer with balance 0 and credit 1000
    And Order with 2 items
    When One item is deleted
    Then Balance decreases correctly
