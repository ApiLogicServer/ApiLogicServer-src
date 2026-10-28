Feature: Row-Level Security

  Scenario: Sales role sees filtered customers
    Given a user logged in with the sales role
    When the sales user requests the Customer list
    Then every returned customer has credit_limit >= 3000 or balance > 0
    And customer "Diana" with balance 0 and credit_limit 1000 is excluded

