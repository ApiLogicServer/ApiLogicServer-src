Feature: Authorization


  Scenario: Grant
     Given NW Test Database
      When u1 GETs Categories
      Then Only 1 is returned


  Scenario: Multi-tenant
     Given NW Test Database
      When sam GETs Customers
      Then only 2 are returned


  Scenario: Global Filters
     Given NW Test Database
      When sam GETs Departments
      Then only 8 are returned


  Scenario: CRUD Permissions
     Given NW Test Database
      When r1 deletes a Shipper
      Then Operation is Refused
