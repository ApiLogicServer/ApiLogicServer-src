Feature: Employee Types

  Scenario: Salaried salary is the entered value
    Given a department with budget 1000000
    When an employee of type salaried is created with name="Sal Emp" salary=70000
    Then the employee salary is 70000

  Scenario: Salaried salary change is kept
    Given a department with budget 1000000
    And an employee of type salaried with name="Sal Change" salary=70000
    When the employee salary is changed to 72000
    Then the employee salary is 72000

  Scenario: Hourly salary is hours_worked times hourly_rate
    Given a department with budget 1000000
    When an employee of type hourly is created with name="Hour Emp" hours_worked=40 hourly_rate=25
    Then the employee salary is 1000

  Scenario: Hourly salary follows a change of hours_worked
    Given a department with budget 1000000
    And an employee of type hourly with name="Hour Hours" hours_worked=40 hourly_rate=25
    When the employee hours_worked is changed to 20
    Then the employee salary is 500

  Scenario: Hourly salary follows a change of hourly_rate
    Given a department with budget 1000000
    And an employee of type hourly with name="Hour Rate" hours_worked=40 hourly_rate=25
    When the employee hourly_rate is changed to 30
    Then the employee salary is 1200

  Scenario: Each employee type is accepted
    Given a department with budget 1000000
    When an employee of type commissioned is created with name="Type Comm" base_salary=1000
    Then the request is accepted

  Scenario: Unknown employee type is rejected
    Given a department with budget 1000000
    When an employee of type contractor is created with name="Type Bad" salary=1000
    Then the request is rejected with "must be salaried, hourly or commissioned"
