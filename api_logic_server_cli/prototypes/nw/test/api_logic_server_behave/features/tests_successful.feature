Feature: Tests Successful

  Scenario: Run Tests
     Given Database and Set of Tests
      When Run Configuration: Behave Tests
      Then No Errors

