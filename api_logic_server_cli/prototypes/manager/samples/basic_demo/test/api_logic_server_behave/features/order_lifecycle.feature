Feature: Order Lifecycle

  Scenario: Set Order Shipped Excludes from Balance
    Given Customer with balance 0 and credit 1000
    And Order with balance 100
    When Order is shipped
    Then Balance is 0
    Then Order excluded from balance aggregate

  Scenario: Reset Shipped Includes in Balance
    Given Customer with balance 0 and credit 1000
    And Order with balance 100 marked shipped
    When Order unshipped
    Then Balance is 100
    Then Order included in balance aggregate

  Scenario: Delete Order Adjusts Balance
    Given Customer with balance 0 and credit 1000
    And Order with balance 150
    When Order is deleted
    Then Balance is 0
    Then Customer has no orders
