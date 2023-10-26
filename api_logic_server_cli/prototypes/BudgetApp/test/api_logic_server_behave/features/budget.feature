# Start the server without security
Feature: Budget App

  Scenario: Budget Transaction Processing
     Given Budget Entry
      When Budget Transactions submitted
      Then Year Total reflects budget change

  Scenario: Transaction Processing
     Given Transaction Entry
      When Transactions submitted
      Then Year Total reflects actual change