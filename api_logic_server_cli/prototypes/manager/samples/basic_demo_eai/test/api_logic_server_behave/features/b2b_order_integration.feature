Feature: B2B Order Integration

  # OrderB2B custom API: partner format -> Order + Items (Customer and Product looked up by name); the Check Credit rules govern the rows.

  Scenario: Partner Order Accepted
    Given Customer "Pat" with credit limit 5000
    When B2B order placed for "Pat" with 1 Widget and 2 Gadget
    Then the partner order is accepted with 2 items
    And Order amount_total should be 390
    And Customer balance should be 390

  Scenario: Unknown Account Rejected
    When B2B order placed for unknown account "Nobody"
    Then the order is rejected for an unknown customer

  Scenario: Accepted Request Is Recorded
    Given Customer "Pia" with credit limit 5000
    And the daily totals are read
    When B2B order placed for "Pia" with 1 Widget
    Then the B2B request is recorded as processed
    And today's request_received and request_processed rise by 1

  Scenario: Rejected Request Is Recorded
    Given Customer "Rex" with credit limit 100
    And the daily totals are read
    When B2B order placed for "Rex" with 2 Widget
    Then the B2B request is recorded with the error "exceeds credit limit"
    And today's request_received and request_failed rise by 1
