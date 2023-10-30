Feature: Authorization


  Scenario: Grant
     Given NW Test Database
      When u1 GETs Categories
      Then Only 1 is returned


  Scenario: Multi-tenant
     Given NW Test Database
      When sam GETs Customers
      Then only 3 are returned


  Scenario: Global Filters
     Given NW Test Database
      When sam GETs Departments
      Then only 8 are returned


  Scenario: Global Filters With Grants
     Given NW Test Database
      When s1 GETs Customers
      Then only 1 customer is returned


  Scenario: CRUD Permissions
     Given NW Test Database
      When r1 deletes a Shipper
      Then Operation is Refused
