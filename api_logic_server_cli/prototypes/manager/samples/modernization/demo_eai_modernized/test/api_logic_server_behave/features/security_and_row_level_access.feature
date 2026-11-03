Feature: Security and Row Level Access

  Scenario: A request without a token is refused
    When customers are listed without a token
    Then the security request answers 401

  Scenario: Sales sees only customers with credit limit 3000 or more, or a balance
    Given customers with credit limit 1000, credit limit 3000, and credit limit 1000 with a balance
    When customers are listed by the sales user
    Then the sales list includes the credit limit 3000 customer
    And the sales list includes the customer with a balance
    And the sales list excludes the credit limit 1000 customer

  Scenario: A customer outside the sales filter is not found
    Given customers with credit limit 1000, credit limit 3000, and credit limit 1000 with a balance
    When the credit limit 1000 customer is requested by the sales user
    Then the security request answers 404

  Scenario: A customer outside the sales filter cannot be updated by sales
    Given customers with credit limit 1000, credit limit 3000, and credit limit 1000 with a balance
    When the credit limit 1000 customer is updated by the sales user
    Then the security request answers 404

  Scenario: A manager sees every customer
    Given customers with credit limit 1000, credit limit 3000, and credit limit 1000 with a balance
    When customers are listed by the admin user
    Then the admin list includes the credit limit 1000 customer
