Feature: Row-Level Security

  Scenario: Sales sees a customer with a credit limit of 3000 or more
    Given a new customer "Sec High" with credit limit 5000
    When a sales user queries the Customer list
    Then the sales user sees "Sec High"

  Scenario: Sales sees a low-limit customer who has a balance
    Given a new customer "Sec Owing" with credit limit 1000
    And a B2B order is placed for "Sec Owing" with 1 Widget
    When a sales user queries the Customer list
    Then the sales user sees "Sec Owing"

  Scenario: Sales does not see a low-limit customer with no balance
    Given a new customer "Sec Low" with credit limit 1000
    When a sales user queries the Customer list
    Then the sales user does not see "Sec Low"
    And an admin user sees "Sec Low"
