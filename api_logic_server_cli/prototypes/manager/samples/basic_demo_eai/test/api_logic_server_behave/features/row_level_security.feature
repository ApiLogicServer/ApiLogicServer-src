Feature: Row-Level Security

  # Role sales (Keycloak user s1): Customers where credit_limit >= 3000 or balance > 0 (Grants are OR'd)

  Scenario: Sales Role Sees Limited Customers
    Given Customer "LowCredit" with credit limit 1000
    And Customer "HighCredit" with credit limit 3000
    And Customer "Owing" with credit limit 1000
    And Order is created for "Owing" with 1 Widget
    When Sales user queries each Customer by name
    Then Sales sees HighCredit and Owing but not LowCredit
