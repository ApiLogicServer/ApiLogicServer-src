Feature: Credit Limit Maintenance

  Background:
    Given a new credit scenario
    And a company "Acme" with default credit limit 0
    And a customer group "Commercial"
    And a customer "Alice" in group "Commercial"

  Scenario: Second customer row for the same company is rejected
    Given customer "Alice" has a credit limit of 1000 at "Acme"
    When a second credit limit of 2000 at "Acme" is added for customer "Alice"
    Then the transaction is rejected with "already has a credit-limit row"

  Scenario: Second group row for the same company is rejected
    Given group "Commercial" has a credit limit of 1000 at "Acme"
    When a second credit limit of 2000 at "Acme" is added for group "Commercial"
    Then the transaction is rejected with "already has a credit-limit row"

  Scenario: Limit below outstanding is rejected
    Given customer "Alice" has a credit limit of 0 at "Acme"
    When a ledger entry with debit 800 and credit 0 is posted for "Alice" at "Acme"
    And customer "Alice" credit limit at "Acme" is changed to 799
    Then the transaction is rejected with "below its current outstanding amount 800.00"

  Scenario: Limit equal to outstanding is allowed
    Given customer "Alice" has a credit limit of 0 at "Acme"
    When a ledger entry with debit 800 and credit 0 is posted for "Alice" at "Acme"
    And customer "Alice" credit limit at "Acme" is changed to 800
    Then the transaction is accepted
    And the customer_credit_limit for "Alice" at "Acme" is 800

  Scenario: Zero limit is allowed whatever the outstanding
    Given customer "Alice" has a credit limit of 900 at "Acme"
    When a ledger entry with debit 800 and credit 0 is posted for "Alice" at "Acme"
    And customer "Alice" credit limit at "Acme" is changed to 0
    Then the transaction is accepted

  Scenario: Row with the flag ignores Sales Orders
    Given customer "Alice" has a credit limit of 0 at "Acme" bypassing the Sales Order check
    When a ledger entry with debit 300 and credit 0 is posted for "Alice" at "Acme"
    And a submitted Sales Order of 2000 is entered for "Alice" at "Acme"
    And customer "Alice" credit limit at "Acme" is changed to 300
    Then the transaction is accepted
    And the bypass_credit_limit_check for "Alice" at "Acme" is 1

  Scenario: Row without the flag counts Sales Orders
    Given customer "Alice" has a credit limit of 0 at "Acme"
    When a ledger entry with debit 300 and credit 0 is posted for "Alice" at "Acme"
    And a submitted Sales Order of 2000 is entered for "Alice" at "Acme"
    And customer "Alice" credit limit at "Acme" is changed to 300
    Then the transaction is rejected with "below its current outstanding amount 2300.00"

  Scenario: Copy from group replaces the customer rows
    Given a company "Beta" with default credit limit 0
    And customer "Alice" has a credit limit of 100 at "Acme"
    And group "Commercial" has a credit limit of 5000 at "Acme"
    And group "Commercial" has a credit limit of 7000 at "Beta" bypassing the Sales Order check
    When credit limits are copied from the group for customer "Alice"
    Then the transaction is accepted
    And the customer_credit_limit for "Alice" at "Acme" is 5000
    And the customer_credit_limit for "Alice" at "Beta" is 7000
    And the bypass_credit_limit_check for "Alice" at "Beta" is 1

  Scenario: Copy from group is rejected when a copied limit is below outstanding
    Given group "Commercial" has a credit limit of 500 at "Acme"
    When a ledger entry with debit 800 and credit 0 is posted for "Alice" at "Acme"
    And credit limits are copied from the group for customer "Alice"
    Then the transaction is rejected with "below its current outstanding amount"
