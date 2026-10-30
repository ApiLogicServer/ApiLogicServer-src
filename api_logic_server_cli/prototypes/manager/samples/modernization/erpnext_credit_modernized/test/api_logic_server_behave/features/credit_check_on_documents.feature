Feature: Credit Check On Documents

  Background:
    Given a new credit scenario
    And a company "Acme" with default credit limit 1000
    And a customer group "Commercial"
    And a customer "Alice" in group "Commercial"

  Scenario: Sales Order with the bypass flag is not checked
    Given customer "Alice" has a credit limit of 1000 at "Acme" bypassing the Sales Order check
    When a submitted Sales Order of 5000 is entered for "Alice" at "Acme"
    Then the transaction is accepted
    And the logic log shows "credit check bypassed at Sales Order"

  Scenario: Draft Sales Order is checked on submit
    When a draft Sales Order of 1500 is entered for "Alice" at "Acme"
    Then the transaction is accepted
    When the Sales Order is submitted
    Then the transaction is rejected with "(1500.00/1000.00)"

  Scenario: Sales Order is checked on update after submit
    When a submitted Sales Order of 900 is entered for "Alice" at "Acme"
    And the Sales Order grand_total is changed to 1100
    Then the transaction is rejected with "(1100.00/1000.00)"

  Scenario: Sales Order is checked when reopened from Closed
    When a submitted Sales Order of 900 is entered for "Alice" at "Acme"
    And the Sales Order status is changed to "Closed"
    And a ledger entry with debit 500 and credit 0 is posted for "Alice" at "Acme"
    When the Sales Order status is changed to "To Deliver and Bill"
    Then the transaction is rejected with "(1400.00/1000.00)"

  Scenario: Delivery Note without the flag is checked when a line is unlinked
    When a draft Delivery Note is entered for "Alice" at "Acme" with net total 1200 and grand total 1200
    And a delivery line with qty 1 and net amount 1200 is added
    And the Delivery Note is submitted
    Then the transaction is rejected with "(1200.00/1000.00)"

  Scenario: Delivery Note without the flag and with only linked lines is not checked
    When a ledger entry with debit 1200 and credit 0 is posted for "Alice" at "Acme"
    And a draft Sales Order of 0 is entered for "Alice" at "Acme"
    And a draft Delivery Note is entered for "Alice" at "Acme" with net total 100 and grand total 100
    And a delivery line with qty 1 and net amount 100 linked to the Sales Order is added
    And the Delivery Note is submitted
    Then the transaction is accepted
    And the Delivery Note unlinked_line_count is 0

  Scenario: Delivery Note with the flag adds Sales Order linked lines as extra
    Given customer "Alice" has a credit limit of 1000 at "Acme" bypassing the Sales Order check
    When a submitted Sales Order of 900 is entered for "Alice" at "Acme"
    And a draft Delivery Note is entered for "Alice" at "Acme" with net total 900 and grand total 900
    And a delivery line with qty 1 and net amount 900 linked to the Sales Order is added
    Then the Delivery Note so_linked_uninvoiced_share is 900
    When the Delivery Note is submitted
    Then the transaction is accepted
    And the Delivery Note bypass_extra_amount is 900

  Scenario: Delivery Note with the flag is rejected when ledger plus extra exceeds the limit
    Given customer "Alice" has a credit limit of 1000 at "Acme" bypassing the Sales Order check
    When a ledger entry with debit 200 and credit 0 is posted for "Alice" at "Acme"
    And a submitted Sales Order of 900 is entered for "Alice" at "Acme"
    And a draft Delivery Note is entered for "Alice" at "Acme" with net total 900 and grand total 900
    And a delivery line with qty 1 and net amount 900 linked to the Sales Order is added
    And the Delivery Note is submitted
    Then the transaction is rejected with "(1100.00/1000.00)"

  Scenario: Delivery Note with the flag and zero net total uses the grand total as extra
    Given customer "Alice" has a credit limit of 1000 at "Acme" bypassing the Sales Order check
    When a draft Delivery Note is entered for "Alice" at "Acme" with net total 0 and grand total 1100
    And a delivery line with qty 1 and net amount 0 is added
    Then the Delivery Note bypass_extra_amount is 1100
    When the Delivery Note is submitted
    Then the transaction is rejected with "(1100.00/1000.00)"

  Scenario: Return and fully billed Delivery Notes are not checked
    When a draft return Delivery Note is entered for "Alice" at "Acme" with net total 1200 and grand total 1200
    And a delivery line with qty 1 and net amount 1200 is added
    And the Delivery Note is submitted
    Then the transaction is accepted
    When a draft Delivery Note billed 100 percent is entered for "Alice" at "Acme" with net total 300 and grand total 300
    And a delivery line with qty 1 and net amount 300 is added
    And the Delivery Note is submitted
    Then the transaction is accepted

  Scenario: Sales Invoice submit posts a debit and is checked
    When a draft Sales Invoice of 600 is entered for "Alice" at "Acme"
    And an invoice line with qty 1 is added
    And the Sales Invoice is submitted
    Then the transaction is accepted
    And the ledger_balance for "Alice" at "Acme" is 600
    When a draft Sales Invoice of 401 is entered for "Alice" at "Acme"
    And an invoice line with qty 1 is added
    And the Sales Invoice is submitted
    Then the transaction is rejected with "(1001.00/1000.00)"
    And the ledger_balance for "Alice" at "Acme" is 600

  Scenario: Sales Invoice billing a delivery line without the flag is not checked
    When a ledger entry with debit 1200 and credit 0 is posted for "Alice" at "Acme"
    And a draft Delivery Note is entered for "Alice" at "Acme" with net total 100 and grand total 100
    And a delivery line with qty 1 and net amount 100 is added
    And a draft Sales Invoice of 100 is entered for "Alice" at "Acme"
    And an invoice line with qty 1 billing the delivery line is added
    And the Sales Invoice is submitted
    Then the transaction is accepted
    And the ledger_balance for "Alice" at "Acme" is 1300

  Scenario: Sales Invoice with the flag is checked ignoring Sales Orders
    Given customer "Alice" has a credit limit of 1000 at "Acme" bypassing the Sales Order check
    When a submitted Sales Order of 5000 is entered for "Alice" at "Acme"
    And a draft Sales Invoice of 900 is entered for "Alice" at "Acme"
    And an invoice line with qty 1 billing nothing but the Sales Order is added
    And the Sales Invoice is submitted
    Then the transaction is accepted
    When a draft Sales Invoice of 101 is entered for "Alice" at "Acme"
    And an invoice line with qty 1 billing nothing but the Sales Order is added
    And the Sales Invoice is submitted
    Then the transaction is rejected with "(1001.00/1000.00)"

  Scenario: Return and opening Sales Invoices are not checked
    When a ledger entry with debit 1200 and credit 0 is posted for "Alice" at "Acme"
    And a draft return Sales Invoice of 100 is entered for "Alice" at "Acme"
    And an invoice line with qty 1 is added
    And the Sales Invoice is submitted
    Then the transaction is accepted
    And the ledger_balance for "Alice" at "Acme" is 1100
    When a draft opening Sales Invoice of 100 is entered for "Alice" at "Acme"
    And an invoice line with qty 1 is added
    And the Sales Invoice is submitted
    Then the transaction is accepted
    And the ledger_balance for "Alice" at "Acme" is 1200

  Scenario: Cancelled Sales Invoice sets its ledger entry cancelled
    When a draft Sales Invoice of 600 is entered for "Alice" at "Acme"
    And an invoice line with qty 1 is added
    And the Sales Invoice is submitted
    And the Sales Invoice is cancelled
    Then the transaction is accepted
    And the ledger_balance for "Alice" at "Acme" is 0

  Scenario: Journal Entry with a customer debit is checked
    When a draft Journal Entry at "Acme" with a customer line for "Alice" with debit 700 and credit 0 is entered
    And the Journal Entry is submitted
    Then the transaction is accepted
    And the ledger_balance for "Alice" at "Acme" is 700
    When a draft Journal Entry at "Acme" with a customer line for "Alice" with debit 301 and credit 0 is entered
    And the Journal Entry is submitted
    Then the transaction is rejected with "(1001.00/1000.00)"

  Scenario: Journal Entry with only a customer credit is not checked
    When a ledger entry with debit 1500 and credit 0 is posted for "Alice" at "Acme"
    And a draft Journal Entry at "Acme" with a customer line for "Alice" with debit 0 and credit 200 is entered
    And the Journal Entry is submitted
    Then the transaction is accepted
    And the ledger_balance for "Alice" at "Acme" is 1300
    When the Journal Entry is cancelled
    Then the ledger_balance for "Alice" at "Acme" is 1500
