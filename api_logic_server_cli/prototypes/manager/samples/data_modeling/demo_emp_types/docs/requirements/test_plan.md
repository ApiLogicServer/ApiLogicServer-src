# Test Plan - demo_emp_types

One row per rule; scenario names are in the "Scenarios" column (closed out after the tests were written).
Feature names match the `Feature:` lines in each `docs/requirements/<use_case>/requirements.md`.

| Feature | Rule | Planned scenarios | Scenarios |
|---|---|---|---|
| Department Budget | `Rule.sum` Department.total_salary | create employee; change salary; delete employee; move to another department (both adjust) | Employee added to a department raises total_salary; Salary change adjusts the department total; Deleting an employee lowers total_salary; Moving an employee adjusts both departments |
| Department Budget | `Rule.constraint` total_salary <= budget | accepted at boundary; rejected over budget; manager role may exceed | Total salary equal to the budget is accepted; Total salary over the budget is rejected; manager role exemption: NOT covered (needs a signed-in user with a role; security is not enabled in this project) |
| Employee Types | `Rule.formula` salary (salaried) | entered salary kept; salary changed | Salaried salary is the entered value; Salaried salary change is kept |
| Employee Types | `Rule.formula` salary (hourly) | hours_worked change; hourly_rate change | Hourly salary is hours_worked times hourly_rate; Hourly salary follows a change of hours_worked; Hourly salary follows a change of hourly_rate |
| Employee Types | `Rule.constraint` type in (salaried, hourly, commissioned) | accepted (every type used); rejected unknown type | Each employee type is accepted (commissioned; the others are used by every other scenario); Unknown employee type is rejected |
| Hourly Employees | `Rule.formula` union_dues | with union; hours change; union dues_rate change (parent); no union = 0; union removed | Union dues are hours_worked times the union dues_rate; Union dues follow a change of hours_worked; Union dues follow a change of the union dues_rate; Hourly employee with no union pays no dues; Removing the union resets dues to zero |
| Hourly Employees | `Rule.constraint` salary <= weekly max (5000) | accepted at 5000; rejected above | Hourly salary equal to 5000 is accepted; Hourly salary above 5000 is rejected |
| Hourly Employees | `Rule.constraint` only hourly may have union_id | rejected for salaried; accepted for hourly | Only hourly employees may have a union; Hourly employee may have a union |
| Hourly Employees | `Rule.constraint` hours_worked/hourly_rate only hourly | rejected for salaried (inferred) | Hours worked are rejected for a non-hourly employee |
| Commissioned Employees | `Rule.sum` commission_total + `Rule.count` order_count | create order; change amount; delete order; move order to another employee | Order raises commission_total and order_count; Order amount change adjusts commission_total; Deleting an order lowers commission_total and order_count; Moving an order adjusts both employees; Base salary change adjusts salary |
| Commissioned Employees | `Rule.constraint` only commissioned may have Orders | rejected for salaried; accepted for commissioned | Salaried employee may not have orders; (accepted: Order raises commission_total and order_count) |
| Commissioned Employees | `Rule.constraint` base_salary only commissioned (inferred) | rejected for hourly | Hourly employee may not have base_salary |
| Military Employees | `Rule.formula` military_stipend | military yes; service_years change; leaves military (yes -> no) | Military stipend is service_years times 100; Stipend follows a change of service_years; Leaving the military removes the stipend |
| Military Employees | `Rule.formula` total_compensation | military = salary + stipend; non-military = salary | Military stipend is service_years times 100 (military); Non-military total compensation equals salary; Military total compensation follows a salary change |
| Military Employees | `Rule.constraint` military yes/no, branch list, military-only columns | invalid branch rejected; branch on non-military rejected; invalid military rejected | Unknown branch is rejected; Military columns on a non-military employee are rejected; Unknown military value is rejected |
