var theRaise = parameters.percentRaise * (row.Salary/100);
row.Salary += theRaise;  // runs logic, persists change row(s) to database...
return [ {"status": "Success"}, {"raise": theRaise} ]; //  , {"row": row.toString()}  ];

/*
This works with the Employees Table:
    http://localhost:8080/rest/default/b2bderbynw/v1/nw:Employees/1/giveRaise?percentRaise=10

It also works with the EmployeesWithRaises Custom Resource, even though the Salary field as aliased.
The 'row.Salary' reference above works because the system has already performed Resource/Object Mapping.
So, row is a *table* row.  This enables you to re-use the function over many Resources.
    http://localhost:8080/rest/default/b2bderbynw/v1/EmployeesWithRaises/1/giveRaise?percentRaise=10
*/
