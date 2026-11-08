Feature: Department Budget

  Scenario: Employee added to a department raises total_salary
    Given a department with budget 100000
    When an employee of type salaried is created with name="Add Emp" salary=40000
    Then the department total_salary is 40000

  Scenario: Salary change adjusts the department total
    Given a department with budget 100000
    And an employee of type salaried with name="Raise Emp" salary=40000
    When the employee salary is changed to 55000
    Then the department total_salary is 55000

  Scenario: Deleting an employee lowers total_salary
    Given a department with budget 100000
    And an employee of type salaried with name="Delete Emp" salary=40000
    When the employee is deleted
    Then the department total_salary is 0

  Scenario: Moving an employee adjusts both departments
    Given a department with budget 100000
    And another department with budget 100000
    And an employee of type salaried with name="Move Emp" salary=40000
    When the employee is moved to the other department
    Then the department total_salary is 0
    And the other department total_salary is 40000

  Scenario: Total salary equal to the budget is accepted
    Given a department with budget 50000
    When an employee of type salaried is created with name="Boundary Emp" salary=50000
    Then the request is accepted
    And the department total_salary is 50000

  Scenario: Total salary over the budget is rejected
    Given a department with budget 50000
    When an employee of type salaried is created with name="Over Emp" salary=50001
    Then the request is rejected with "exceeds budget"
