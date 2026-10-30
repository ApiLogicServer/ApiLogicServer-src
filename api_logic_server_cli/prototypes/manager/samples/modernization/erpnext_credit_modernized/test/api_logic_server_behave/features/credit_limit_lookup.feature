Feature: Credit Limit Lookup

  Background:
    Given a new credit scenario
    And a company "Acme" with default credit limit 5000
    And a customer group "Commercial"
    And a customer "Alice" in group "Commercial"

  Scenario: Customer own row wins over group and company
    Given group "Commercial" has a credit limit of 3000 at "Acme"
    And customer "Alice" has a credit limit of 1000 at "Acme"
    When a submitted Sales Order of 1000 is entered for "Alice" at "Acme"
    Then the transaction is accepted
    When a submitted Sales Order of 1 is entered for "Alice" at "Acme"
    Then the transaction is rejected with "(1001.00/1000.00)"

  Scenario: Customer row with zero limit falls to group row
    Given group "Commercial" has a credit limit of 3000 at "Acme"
    And customer "Alice" has a credit limit of 0 at "Acme"
    When a submitted Sales Order of 3001 is entered for "Alice" at "Acme"
    Then the transaction is rejected with "(3001.00/3000.00)"

  Scenario: Group row that bypasses the check falls to company default
    Given group "Commercial" has a credit limit of 3000 at "Acme" bypassing the Sales Order check
    When a submitted Sales Order of 4000 is entered for "Alice" at "Acme"
    Then the transaction is accepted
    When a submitted Sales Order of 1001 is entered for "Alice" at "Acme"
    Then the transaction is rejected with "(5001.00/5000.00)"

  Scenario: No credit-limit rows uses company default
    When a submitted Sales Order of 5001 is entered for "Alice" at "Acme"
    Then the transaction is rejected with "(5001.00/5000.00)"

  Scenario: Zero limit everywhere means no credit check
    Given a company "Zero" with default credit limit 0
    When a submitted Sales Order of 1000000 is entered for "Alice" at "Zero"
    Then the transaction is accepted
    And the logic log shows "no credit limit"

  Scenario: Group row with zero limit means no limit
    Given group "Commercial" has a credit limit of 0 at "Acme"
    When a submitted Sales Order of 9000 is entered for "Alice" at "Acme"
    Then the transaction is accepted
