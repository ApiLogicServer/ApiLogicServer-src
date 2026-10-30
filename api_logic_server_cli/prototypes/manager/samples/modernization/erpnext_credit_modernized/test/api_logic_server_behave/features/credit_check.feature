Feature: Credit Check

  Background:
    Given a new credit scenario
    And a company "Acme" with default credit limit 1000
    And a customer group "Commercial"
    And a customer "Alice" in group "Commercial"
    And a customer "Bob" in group "Commercial"

  Scenario: Ledger entries roll up to the ledger balance
    When a ledger entry with debit 300 and credit 50 is posted for "Alice" at "Acme"
    Then the transaction is accepted
    And the ledger_balance for "Alice" at "Acme" is 250
    When the ledger entry debit is changed to 400
    Then the ledger_balance for "Alice" at "Acme" is 350
    And the outstanding for "Alice" at "Acme" is 350

  Scenario: Cancelled ledger entry leaves and re-enters the balance
    When a ledger entry with debit 300 and credit 0 is posted for "Alice" at "Acme"
    And the ledger entry is cancelled
    Then the ledger_balance for "Alice" at "Acme" is 0
    When the ledger entry is uncancelled
    Then the ledger_balance for "Alice" at "Acme" is 300

  Scenario: Deleted ledger entry leaves the balance
    When a ledger entry with debit 300 and credit 0 is posted for "Alice" at "Acme"
    And the ledger entry is deleted
    Then the ledger_balance for "Alice" at "Acme" is 0

  Scenario: Ledger entry moved to another customer adjusts both
    When a ledger entry with debit 300 and credit 0 is posted for "Alice" at "Acme"
    And the ledger entry is moved to customer "Bob"
    Then the ledger_balance for "Alice" at "Acme" is 0
    And the ledger_balance for "Bob" at "Acme" is 300

  Scenario: Open Sales Order amount follows per billed
    When a submitted Sales Order of 500 is entered for "Alice" at "Acme"
    Then the open_sales_order_amount for "Alice" at "Acme" is 500
    When the Sales Order per_billed is changed to 40
    Then the open_sales_order_amount for "Alice" at "Acme" is 300
    When the Sales Order per_billed is changed to 100
    Then the open_sales_order_amount for "Alice" at "Acme" is 0

  Scenario: Open Sales Order amount follows grand total
    When a submitted Sales Order of 500 is entered for "Alice" at "Acme"
    And the Sales Order grand_total is changed to 600
    Then the open_sales_order_amount for "Alice" at "Acme" is 600

  Scenario: Closed and draft Sales Orders are not open
    When a draft Sales Order of 500 is entered for "Alice" at "Acme"
    Then the open_sales_order_amount for "Alice" at "Acme" is 0
    When the Sales Order is submitted
    Then the open_sales_order_amount for "Alice" at "Acme" is 500
    When the Sales Order status is changed to "Closed"
    Then the open_sales_order_amount for "Alice" at "Acme" is 0
    When the Sales Order status is changed to "To Deliver and Bill"
    Then the open_sales_order_amount for "Alice" at "Acme" is 500

  Scenario: Sales Order deleted and moved
    When a submitted Sales Order of 500 is entered for "Alice" at "Acme"
    And the Sales Order is moved to customer "Bob"
    Then the open_sales_order_amount for "Alice" at "Acme" is 0
    And the open_sales_order_amount for "Bob" at "Acme" is 500
    When the Sales Order is deleted
    Then the open_sales_order_amount for "Bob" at "Acme" is 0

  Scenario: Delivered but not billed amount
    When a draft Delivery Note is entered for "Alice" at "Acme" with net total 100 and grand total 110
    And a delivery line with qty 10 and net amount 100 is added
    Then the unbilled_delivery_amount for "Alice" at "Acme" is 0
    When the Delivery Note is submitted
    Then the transaction is accepted
    And the unbilled_delivery_amount for "Alice" at "Acme" is 110

  Scenario: Billed and returned quantities reduce the unbilled amount
    When a draft Delivery Note is entered for "Alice" at "Acme" with net total 100 and grand total 110
    And a delivery line with qty 10 and net amount 100 is added
    And the Delivery Note is submitted
    And a draft Sales Invoice of 0 is entered for "Alice" at "Acme"
    And an invoice line with qty 4 billing the delivery line is added
    Then the delivery line billed_qty is 0
    When the Sales Invoice is submitted
    Then the delivery line billed_qty is 4
    And the unbilled_delivery_amount for "Alice" at "Acme" is 66
    When the delivery line returned_qty is changed to 2
    Then the unbilled_delivery_amount for "Alice" at "Acme" is 44
    When the invoice line qty is changed to 5
    Then the delivery line billed_qty is 5
    And the unbilled_delivery_amount for "Alice" at "Acme" is 33

  Scenario: Cancelled invoice and return invoice do not count as billed
    When a draft Delivery Note is entered for "Alice" at "Acme" with net total 100 and grand total 100
    And a delivery line with qty 10 and net amount 100 is added
    And the Delivery Note is submitted
    And a draft return Sales Invoice of 0 is entered for "Alice" at "Acme"
    And an invoice line with qty 4 billing the delivery line is added
    And the Sales Invoice is submitted
    Then the delivery line billed_qty is 0
    When a draft Sales Invoice of 0 is entered for "Alice" at "Acme"
    And an invoice line with qty 4 billing the delivery line is added
    And the Sales Invoice is submitted
    Then the delivery line billed_qty is 4
    When the Sales Invoice is cancelled
    Then the delivery line billed_qty is 0
    And the unbilled_delivery_amount for "Alice" at "Acme" is 100

  Scenario: Invoice line deleted or moved to another delivery line
    When a draft Delivery Note is entered for "Alice" at "Acme" with net total 200 and grand total 200
    And a delivery line with qty 10 and net amount 100 is added
    And a second delivery line with qty 10 and net amount 100 is added
    And the Delivery Note is submitted
    And a draft Sales Invoice of 0 is entered for "Alice" at "Acme"
    And an invoice line with qty 4 billing the delivery line is added
    And the Sales Invoice is submitted
    When the invoice line is moved to the second delivery line
    Then the delivery line billed_qty is 0
    And the second delivery line billed_qty is 4
    When the invoice line is deleted
    Then the second delivery line billed_qty is 0

  Scenario: Delivery lines linked to a Sales Order or Invoice are not unbilled
    When a submitted Sales Order of 100 is entered for "Alice" at "Acme"
    And a draft Delivery Note is entered for "Alice" at "Acme" with net total 100 and grand total 100
    And a delivery line with qty 10 and net amount 100 is added
    And the Delivery Note is submitted
    Then the unbilled_delivery_amount for "Alice" at "Acme" is 100
    When the delivery line is linked to the Sales Order
    Then the unbilled_delivery_amount for "Alice" at "Acme" is 0
    And the Delivery Note unlinked_line_count is 0

  Scenario: Closed Delivery Note and moved Delivery Note
    When a draft Delivery Note is entered for "Alice" at "Acme" with net total 100 and grand total 100
    And a delivery line with qty 10 and net amount 100 is added
    And the Delivery Note is submitted
    And the Delivery Note is moved to customer "Bob"
    Then the unbilled_delivery_amount for "Alice" at "Acme" is 0
    And the unbilled_delivery_amount for "Bob" at "Acme" is 100
    When the Delivery Note status is changed to "Closed"
    Then the unbilled_delivery_amount for "Bob" at "Acme" is 0
    When the delivery line is deleted
    And the Delivery Note status is changed to "Submitted"
    Then the unbilled_delivery_amount for "Bob" at "Acme" is 0

  Scenario: Outstanding is the sum of the three parts
    When a ledger entry with debit 100 and credit 0 is posted for "Alice" at "Acme"
    And a submitted Sales Order of 200 is entered for "Alice" at "Acme"
    And a draft Delivery Note is entered for "Alice" at "Acme" with net total 300 and grand total 300
    And a delivery line with qty 1 and net amount 300 is added
    And the Delivery Note is submitted
    Then the outstanding for "Alice" at "Acme" is 600
    And the outstanding_ignoring_sales_orders for "Alice" at "Acme" is 400

  Scenario: Outstanding equal to the limit is allowed
    When a submitted Sales Order of 1000 is entered for "Alice" at "Acme"
    Then the transaction is accepted
    And the logic log shows "credit check passed"

  Scenario: Outstanding above the limit is rejected
    When a ledger entry with debit 600 and credit 0 is posted for "Alice" at "Acme"
    And a submitted Sales Order of 401 is entered for "Alice" at "Acme"
    Then the transaction is rejected with "Credit limit has been crossed for customer"
    And the open_sales_order_amount for "Alice" at "Acme" is 0

  Scenario: Credit controller is not rejected
    Given the user is "sam"
    When a submitted Sales Order of 1500 is entered for "Alice" at "Acme"
    Then the transaction is accepted
    And the logic log shows "allowed for credit controller role"

  Scenario: Admin is not a credit controller
    Given the user is "admin"
    When a submitted Sales Order of 1500 is entered for "Alice" at "Acme"
    Then the transaction is rejected with "(1500.00/1000.00)"

  Scenario: No credit controller role set excuses nobody
    Given the user is "sam"
    When a submitted Sales Order of 1500 is entered for "Alice" at "Acme" with no credit controller role set
    Then the transaction is rejected with "(1500.00/1000.00)"
