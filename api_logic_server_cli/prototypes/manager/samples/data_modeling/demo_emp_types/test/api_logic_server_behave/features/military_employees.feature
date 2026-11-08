Feature: Military Employees

  Scenario: Military stipend is service_years times 100
    Given a department with budget 1000000
    When an employee of type salaried is created with name="Mil Emp" salary=50000 military="yes" branch="Navy" rank="Captain" service_years=8
    Then the employee military_stipend is 800
    And the employee total_compensation is 50800

  Scenario: Stipend follows a change of service_years
    Given a department with budget 1000000
    And an employee of type salaried with name="Mil Years" salary=50000 military="yes" branch="Army" rank="Major" service_years=8
    When the employee service_years is changed to 10
    Then the employee military_stipend is 1000
    And the employee total_compensation is 51000

  Scenario: Leaving the military removes the stipend
    Given a department with budget 1000000
    And an employee of type salaried with name="Mil Leave" salary=50000 military="yes" branch="Marines" rank="Sergeant" service_years=4
    When the employee leaves the military
    Then the employee military_stipend is 0
    And the employee total_compensation is 50000

  Scenario: Non-military total compensation equals salary
    Given a department with budget 1000000
    When an employee of type salaried is created with name="Civ Emp" salary=50000
    Then the employee total_compensation is 50000

  Scenario: Military total compensation follows a salary change
    Given a department with budget 1000000
    And an employee of type hourly with name="Mil Hourly" hours_worked=10 hourly_rate=10 military="yes" branch="Air Force" rank="Airman" service_years=2
    When the employee hours_worked is changed to 20
    Then the employee total_compensation is 400

  Scenario: Unknown branch is rejected
    Given a department with budget 1000000
    When an employee of type salaried is created with name="Bad Branch" salary=1000 military="yes" branch="Space Force" rank="Cadet" service_years=1
    Then the request is rejected with "must be Army, Navy"

  Scenario: Military columns on a non-military employee are rejected
    Given a department with budget 1000000
    When an employee of type salaried is created with name="Civ Branch" salary=1000 branch="Navy"
    Then the request is rejected with "apply only to military employees"

  Scenario: Unknown military value is rejected
    Given a department with budget 1000000
    When an employee of type salaried is created with name="Bad Mil" salary=1000 military="maybe"
    Then the request is rejected with "military must be yes or no"
