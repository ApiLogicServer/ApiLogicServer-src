Feature: Commissioned Employees

  Scenario: Order raises commission_total and order_count
    Given a department with budget 1000000
    And an employee of type commissioned with name="Comm Add" base_salary=1000
    When an order of 500 is added for the employee
    Then the employee commission_total is 500
    And the employee order_count is 1
    And the employee salary is 1500

  Scenario: Order amount change adjusts commission_total
    Given a department with budget 1000000
    And an employee of type commissioned with name="Comm Change" base_salary=1000
    And an order of 500 is added for the employee
    When the order amount is changed to 800
    Then the employee commission_total is 800
    And the employee salary is 1800

  Scenario: Deleting an order lowers commission_total and order_count
    Given a department with budget 1000000
    And an employee of type commissioned with name="Comm Delete" base_salary=1000
    And an order of 500 is added for the employee
    When the order is deleted
    Then the employee commission_total is 0
    And the employee order_count is 0

  Scenario: Moving an order adjusts both employees
    Given a department with budget 1000000
    And an employee of type commissioned with name="Comm From" base_salary=1000
    And another employee of type commissioned with name="Comm To" base_salary=2000
    And an order of 500 is added for the employee
    When the order is moved to the other employee
    Then the employee commission_total is 0
    And the other employee commission_total is 500
    And the other employee order_count is 1

  Scenario: Base salary change adjusts salary
    Given a department with budget 1000000
    And an employee of type commissioned with name="Comm Base" base_salary=1000
    And an order of 500 is added for the employee
    When the employee base_salary is changed to 2000
    Then the employee salary is 2500

  Scenario: Salaried employee may not have orders
    Given a department with budget 1000000
    And an employee of type salaried with name="Order Sal" salary=1000
    When an order of 100 is added for the employee
    Then the request is rejected with "Only commissioned employees may have Orders"

  Scenario: Hourly employee may not have base_salary
    Given a department with budget 1000000
    When an employee of type hourly is created with name="Base Hour" hours_worked=1 hourly_rate=1 base_salary=100
    Then the request is rejected with "base_salary applies only to commissioned employees"
