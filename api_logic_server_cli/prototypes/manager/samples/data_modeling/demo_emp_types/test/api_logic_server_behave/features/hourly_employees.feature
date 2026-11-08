Feature: Hourly Employees

  Scenario: Union dues are hours_worked times the union dues_rate
    Given a department with budget 1000000
    And a union with dues rate 2.5
    When an employee of type hourly is created with name="Dues Emp" hours_worked=40 hourly_rate=25 union_id=@union
    Then the employee union_dues is 100

  Scenario: Union dues follow a change of hours_worked
    Given a department with budget 1000000
    And a union with dues rate 2.5
    And an employee of type hourly with name="Dues Hours" hours_worked=40 hourly_rate=25 union_id=@union
    When the employee hours_worked is changed to 10
    Then the employee union_dues is 25

  Scenario: Union dues follow a change of the union dues_rate
    Given a department with budget 1000000
    And a union with dues rate 2.5
    And an employee of type hourly with name="Dues Rate" hours_worked=40 hourly_rate=25 union_id=@union
    When the union dues_rate is changed to 5
    Then the employee union_dues is 200

  Scenario: Hourly employee with no union pays no dues
    Given a department with budget 1000000
    When an employee of type hourly is created with name="No Union" hours_worked=40 hourly_rate=25
    Then the employee union_dues is 0

  Scenario: Removing the union resets dues to zero
    Given a department with budget 1000000
    And a union with dues rate 2.5
    And an employee of type hourly with name="Leave Union" hours_worked=40 hourly_rate=25 union_id=@union
    When the employee union_id is changed to null
    Then the employee union_dues is 0

  Scenario: Hourly salary equal to 5000 is accepted
    Given a department with budget 1000000
    When an employee of type hourly is created with name="Cap Emp" hours_worked=100 hourly_rate=50
    Then the request is accepted
    And the employee salary is 5000

  Scenario: Hourly salary above 5000 is rejected
    Given a department with budget 1000000
    When an employee of type hourly is created with name="Cap Over" hours_worked=100 hourly_rate=50.01
    Then the request is rejected with "Hourly salary"

  Scenario: Only hourly employees may have a union
    Given a department with budget 1000000
    And a union with dues rate 2.5
    When an employee of type salaried is created with name="Union Sal" salary=1000 union_id=@union
    Then the request is rejected with "Only hourly employees may have a union_id"

  Scenario: Hourly employee may have a union
    Given a department with budget 1000000
    And a union with dues rate 2.5
    When an employee of type hourly is created with name="Union Hour" hours_worked=1 hourly_rate=1 union_id=@union
    Then the request is accepted

  Scenario: Hours worked are rejected for a non-hourly employee
    Given a department with budget 1000000
    When an employee of type salaried is created with name="Hours Sal" salary=1000 hours_worked=5
    Then the request is rejected with "apply only to hourly employees"
