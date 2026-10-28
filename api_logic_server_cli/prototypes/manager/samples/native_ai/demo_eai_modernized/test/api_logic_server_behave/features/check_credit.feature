Feature: Check Credit

  Scenario: Good Order within credit limit
    Given a customer with credit_limit 1000 and balance 0
    When an unshipped order is placed with 2 items of unit_price 150
    Then the item amount is 300
    And the order amount_total is 300
    And the customer balance is 300

  Scenario: Alter Item Quantity
    Given a customer with credit_limit 1000 and an unshipped order of 2 items at unit_price 150
    When the item quantity is updated to 4
    Then the item amount is 600
    And the order amount_total is 600
    And the customer balance is 600

  Scenario: Change Order Customer
    Given two customers with credit_limit 1000 and an order of 300 on the first customer
    When the order is reassigned to the second customer
    Then the first customer balance is 0
    And the second customer balance is 300

  Scenario: Delete Order Item
    Given a customer with credit_limit 1000 and an unshipped order of 2 items at unit_price 150
    When the item is deleted
    Then the order amount_total is 0
    And the customer balance is 0

  Scenario: Ship Order updates balance
    Given a customer with credit_limit 1000 and an unshipped order of 2 items at unit_price 150
    When the order date_shipped is set to "2026-10-27"
    Then the customer balance is 0

  Scenario: Unship Order updates balance
    Given a customer with credit_limit 1000 and a shipped order of 2 items at unit_price 150
    When the order date_shipped is cleared
    Then the customer balance is 300

  Scenario: Exceed Credit Limit fails
    Given a customer with credit_limit 1000 and balance 0
    When an unshipped order is placed with 10 items of unit_price 150
    Then the transaction is rejected with credit limit constraint

