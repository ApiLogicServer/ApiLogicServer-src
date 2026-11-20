Feature: Row-Level Security

  # Role sales (Keycloak user s1): Customer grants credit_limit >= 3000 OR balance > 0.

  Scenario: Sales Role Sees Limited Customers
    Given Customer "Lowlimit" with credit limit 1000
    And Customer "Highlimit" with credit limit 5000
    And Customer "Owing" with credit limit 1000
    And Order is created for "Owing" with 1 Widget
    When the sales user lists Customers
    Then "Highlimit" and "Owing" are listed, and "Lowlimit" is not
    And every listed Customer has credit_limit >= 3000 or balance > 0
