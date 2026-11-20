Feature: B2B Order Integration

  Scenario: Partner order is mapped and the request recorded as processed
    Given a new customer "Partner Co" with credit limit 5000
    When a B2B order is placed for "Partner Co" with 3 Widget and 2 Gadget
    Then the order is accepted
    And the order belongs to "Partner Co"
    And the order items are 3 Widget and 2 Gadget
    And the B2B request is recorded as processed

  Scenario: Partner order with an unknown product is rejected and the request recorded with its error
    Given a new customer "Partner Bad" with credit limit 5000
    When a B2B order is placed for "Partner Bad" with 1 Sprocket
    Then the order is rejected with "Lookup failed"
    And the B2B request is recorded with an error
    And "Partner Bad" has no orders

  Scenario: Partner order for an unknown account is rejected
    When a B2B order is placed for an unknown account
    Then the order is rejected with "Lookup failed"
