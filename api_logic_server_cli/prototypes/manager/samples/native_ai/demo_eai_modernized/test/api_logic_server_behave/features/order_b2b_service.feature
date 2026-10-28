Feature: B2B Order Integration

  Scenario: B2B Valid Order via OrderB2B
    Given a B2B customer with credit_limit 5000
    When a B2B order payload is posted to OrderB2B for 2 Gadget and 1 Widget
    Then the OrderB2B response status is 200
    And the B2B customer balance increases by 390

  Scenario: B2B Exceed Credit via OrderB2B
    Given a B2B customer with credit_limit 200
    When a B2B order payload is posted to OrderB2B for 2 Gadget and 1 Widget
    Then the OrderB2B response status is 400

