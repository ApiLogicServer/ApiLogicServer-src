# Behave Creates Executable Test Suite, Documentation

You can optionally use the Behave test framework to:

1. **Create and Run an Executable Test Suite:** in your IDE, create test definitions (similar to what is shown in the report below), and Python code to execute tests.  You can then execute your test suite with 1 command.

2. **Requirements and Test Documentation:** as shown below, you can then create a wiki report that documents your requirements, and the tests (**Scenarios**) that confirm their proper operation.

   * **Logic Documentation:** the report integrates your logic, including a logic report showing your logic (rules and Python), and a Logic Log that shows exactly how the rules executed.  Logic Doc can further contribute to Agile Collaboration.

<figure><img src="https://raw.githubusercontent.com/ApiLogicServer/Docs/main/docs/images/behave/behave-summary.png"  height="600"></figure>



[Behave](https://behave.readthedocs.io/en/stable/tutorial.html) is a framework for defining and executing tests.  It is based on [TDD (Test Driven Development)](http://dannorth.net/introducing-bdd/), an Agile approach for defining system requirements as executable tests.

&nbsp;&nbsp;

# Using Behave

<figure><img src="https://raw.githubusercontent.com/ApiLogicServer/Docs/main/docs/images/behave/TDD-ide.png?raw=true"></figure>

Behave is pre-installed with API Logic Server.  Use it as shown above:

1. Create `.feature` files to define ***Scenarios*** (aka tests) for ***Features*** (aka Stories)

2. Code `.py` files to implement Scenario tests

3. Run Test Suite: Launch Configuration `Behave Run`.  This runs all your Scenarios, and produces a summary report of your Features and the test results.

4. Report: Launch Configuration `Behave Report` to create the wiki file shown at the top of this page.

These steps are further defined, below.  Explore the samples in the sample project.

&nbsp;&nbsp;

## 1. Create `.feature` file to define Scenario

Feature (aka Story) files are designed to promote IT / business user collaboration.  

&nbsp;&nbsp;

## 2. Code `.py` file to implement test

Implement your tests in Python.  Here, the tests are largely _read existing data_, _run transaction_, and _test results_, using the API.  You can obtain the URLs from the swagger.

Key points:

* Link your scenario / implementations with annotations, as shown for _Order Placed with excessive quantity_.

* Include the `test_utils.prt()` call; be sure to use specify the scenario name as the 2nd argument.  This is what drives the name of the Logic Log file, discussed below.

* Optionally, include a Python docstring on your `when` implementation as shown above, delimited by `"""` strings (see _"Familiar logic pattern"_ in the screen shot, above). If provided, this will be written into the wiki report.

* Important: the system assumes the following line identifies the scenario_name; be sure to include it.

&nbsp;&nbsp;

## 3. Run Test Suite: Launch Configuration `Behave Run`

You can now execute your Test Suite.  Run the `Behave Run` Launch Configuration, and Behave will run all of the tests, producing the outputs (`behave.log` and `<scenario.logs>` shown above.

* Windows users will need to run `Windows Behave Run`

* You can run just 1 scenario using `Behave Scenario`

* You can set breakpoints in your tests

The server must be running for these tests.  Use the Launch Configuration `ApiLogicServer`, or `python api_logic_server_run.py`.  The latter does not run the debugger, which you may find more convenient since changes to your test code won't restart the server.

&nbsp;&nbsp;

## 4. Report: Launch Configuration `Behave Report'

Run this to create the wiki reports from the logs in step 3.


&nbsp;
&nbsp;


# Behave Logic Report
&nbsp;
&nbsp;
## Feature: About Sample  
  
&nbsp;
&nbsp;
### Scenario: Transaction Processing
&emsp;  Scenario: Transaction Processing  
&emsp;&emsp;    Given Sample Database  
&emsp;&emsp;    When Transactions are submitted  
&emsp;&emsp;    Then Enforce business policies with Logic (rules + code)  
<details markdown>
<summary>Tests - and their logic - are transparent.. click to see Logic</summary>


&nbsp;
&nbsp;


**Rules Used** in Scenario: Transaction Processing
```
  Category  
    1. Constraint Function: <function declare_logic.<locals>.valid_category_description at 0x10b83fba0>   
  
```
**Logic Log** in Scenario: Transaction Processing
```

The following rules have been activate
 - 2024-07-12 14:57:05,237 - logic_logger - DEBU
Rule Bank[0x10a431ca0] (loaded 2024-07-12 14:56:46.929015
Mapped Class[Customer] rules
  Constraint Function: None
  Constraint Function: None
  Derive Customer.Balance as Sum(Order.AmountTotal Where <function declare_logic.<locals>.<lambda> at 0x10b83fd80>
  RowEvent Customer.customer_defaults()
  Derive Customer.UnpaidOrderCount as Count(<class 'database.models.Order'> Where <function declare_logic.<locals>.<lambda> at 0x10b9596c0>
  Derive Customer.OrderCount as Count(<class 'database.models.Order'> Where None
Mapped Class[Employee] rules
  Constraint Function: None
  Constraint Function: <function declare_logic.<locals>.raise_over_20_percent at 0x10b959940>
  Copy to: EmployeeAudi
Mapped Class[Category] rules
  Constraint Function: <function declare_logic.<locals>.valid_category_description at 0x10b83fba0>
Mapped Class[Order] rules
  Derive Order.AmountTotal as Sum(OrderDetail.Amount Where None
  RowEvent Order.send_order_to_shipping()
  RowEvent Order.congratulate_sales_rep()
  RowEvent Order.do_not_ship_empty_orders()
  Constraint Function: <function declare_logic.<locals>.ship_ready_orders_only at 0x10b9591c0>
  RowEvent Order.order_defaults()
  Derive Order.OrderDetailCount as Count(<class 'database.models.OrderDetail'> Where None
  RowEvent Order.clone_order()
  Derive Order.OrderDate as Formula (1): as_expression=lambda row: datetime.datetime.now()
Mapped Class[OrderDetail] rules
  Derive OrderDetail.Amount as Formula (1): as_expression=lambda row: row.UnitPrice * row.Qua [...
  Derive OrderDetail.UnitPrice as Copy(Product.UnitPrice
  RowEvent OrderDetail.order_detail_defaults()
  Derive OrderDetail.ShippedDate as Formula (2): row.Order.ShippedDat
Mapped Class[Product] rules
  Derive Product.UnitsInStock as Formula (1): <function
  Derive Product.UnitsShipped as Sum(OrderDetail.Quantity Where <function declare_logic.<locals>.<lambda> at 0x10b959580>
Logic Bank - 32 rules loaded - 2024-07-12 14:57:05,243 - logic_logger - INF
Logic Bank - 32 rules loaded - 2024-07-12 14:57:05,243 - logic_logger - INF

Logic Phase:		ROW LOGIC		(session=0x10dbbc710) (sqlalchemy before_flush)			 - 2024-07-12 14:57:06,076 - logic_logger - INF
..Shipper[1] {Delete - client} Id: 1, CompanyName: Speedy Express, Phone: (503) 555-9831  row: 0x10dbbce30  session: 0x10dbbc710  ins_upd_dlt: dlt - 2024-07-12 14:57:06,077 - logic_logger - INF

Logic Phase:		ROW LOGIC		(session=0x10dcac9e0) (sqlalchemy before_flush)			 - 2024-07-12 14:57:06,151 - logic_logger - INF
..Category[1] {Update - client} Id: 1, CategoryName: Beverages, Description:  [Soft drinks, coffees, teas, beers, and ales-->] x, Client_id: 1  row: 0x10dcad6a0  session: 0x10dcac9e0  ins_upd_dlt: upd - 2024-07-12 14:57:06,151 - logic_logger - INF
..Category[1] {Constraint Failure: Description cannot be 'x'} Id: 1, CategoryName: Beverages, Description:  [Soft drinks, coffees, teas, beers, and ales-->] x, Client_id: 1  row: 0x10dcad6a0  session: 0x10dcac9e0  ins_upd_dlt: upd - 2024-07-12 14:57:06,152 - logic_logger - INF

```
</details>
  
&nbsp;
&nbsp;
## Feature: Application Integration  
  
&nbsp;
&nbsp;
### Scenario: GET Customer
&emsp;  Scenario: GET Customer  
&emsp;&emsp;    Given Customer Account: VINET  
&emsp;&emsp;    When GET Orders API  
&emsp;&emsp;    Then VINET retrieved  
  
&nbsp;
&nbsp;
### Scenario: GET Department
&emsp;  Scenario: GET Department  
&emsp;&emsp;    Given Department 2  
&emsp;&emsp;    When GET Department with SubDepartments API  
&emsp;&emsp;    Then SubDepartments returned  
  
&nbsp;
&nbsp;
## Feature: Authorization  
  
&nbsp;
&nbsp;
### Scenario: Grant
&emsp;  Scenario: Grant  
&emsp;&emsp;    Given NW Test Database  
&emsp;&emsp;    When u1 GETs Categories  
&emsp;&emsp;    Then Only 1 is returned  
  
&nbsp;
&nbsp;
### Scenario: Multi-tenant
&emsp;  Scenario: Multi-tenant  
&emsp;&emsp;    Given NW Test Database  
&emsp;&emsp;    When sam GETs Customers  
&emsp;&emsp;    Then only 3 are returned  
  
&nbsp;
&nbsp;
### Scenario: Global Filters
&emsp;  Scenario: Global Filters  
&emsp;&emsp;    Given NW Test Database  
&emsp;&emsp;    When sam GETs Departments  
&emsp;&emsp;    Then only 8 are returned  
  
&nbsp;
&nbsp;
### Scenario: Global Filters With Grants
&emsp;  Scenario: Global Filters With Grants  
&emsp;&emsp;    Given NW Test Database  
&emsp;&emsp;    When s1 GETs Customers  
&emsp;&emsp;    Then only 1 customer is returned  
  
&nbsp;
&nbsp;
### Scenario: CRUD Permissions
&emsp;  Scenario: CRUD Permissions  
&emsp;&emsp;    Given NW Test Database  
&emsp;&emsp;    When r1 deletes a Shipper  
&emsp;&emsp;    Then Operation is Refused  
  
&nbsp;
&nbsp;
## Feature: Optimistic Locking  
  
&nbsp;
&nbsp;
### Scenario: Get Category
&emsp;  Scenario: Get Category  
&emsp;&emsp;    Given Category: 1  
&emsp;&emsp;    When Get Cat1  
&emsp;&emsp;    Then Expected Cat1 Checksum  
  
&nbsp;
&nbsp;
### Scenario: Valid Checksum
&emsp;  Scenario: Valid Checksum  
&emsp;&emsp;    Given Category: 1  
&emsp;&emsp;    When Patch Valid Checksum  
&emsp;&emsp;    Then Valid Checksum, Invalid Description  
  
&nbsp;
&nbsp;
### Scenario: Missing Checksum
&emsp;  Scenario: Missing Checksum  
&emsp;&emsp;    Given Category: 1  
&emsp;&emsp;    When Patch Missing Checksum  
&emsp;&emsp;    Then Valid Checksum, Invalid Description  
  
&nbsp;
&nbsp;
### Scenario: Invalid Checksum
&emsp;  Scenario: Invalid Checksum  
&emsp;&emsp;    Given Category: 1  
&emsp;&emsp;    When Patch Invalid Checksum  
&emsp;&emsp;    Then Invalid Checksum  
  
&nbsp;
&nbsp;
## Feature: Place Order  
  
&nbsp;
&nbsp;
### Scenario: Order Made Not Ready
&emsp;  Scenario: Order Made Not Ready  
&emsp;&emsp;    Given Customer Account: ALFKI  
&emsp;&emsp;    When Ready Flag is Reset  
&emsp;&emsp;    Then Logic Decreases Balance  
<details markdown>
<summary>Tests - and their logic - are transparent.. click to see Logic</summary>


&nbsp;
&nbsp;


**Logic Doc** for scenario: Order Made Not Ready
   
We reset `Order.Ready`.

This removes the order from contingent derivations (e.g., the `Customer.Balance`),
and constraints.

> **Key Takeaway:** adjustment from change in qualification condition



&nbsp;
&nbsp;


**Rules Used** in Scenario: Order Made Not Ready
```
  Customer  
    1. RowEvent Customer.customer_defaults()   
    2. Derive Customer.UnpaidOrderCount as Count(<class 'database.models.Order'> Where <function declare_logic.<locals>.<lambda> at 0x10b9596c0>)  
    3. Derive Customer.OrderCount as Count(<class 'database.models.Order'> Where None)  
    4. Derive Customer.Balance as Sum(Order.AmountTotal Where <function declare_logic.<locals>.<lambda> at 0x10b83fd80>)  
  Order  
    5. RowEvent Order.do_not_ship_empty_orders()   
    6. RowEvent Order.send_order_to_shipping()   
    7. RowEvent Order.congratulate_sales_rep()   
    8. RowEvent Order.clone_order()   
    9. RowEvent Order.order_defaults()   
  
```
**Logic Log** in Scenario: Order Made Not Ready
```

Logic Phase:		ROW LOGIC		(session=0x10d963020) (sqlalchemy before_flush)			 - 2024-07-12 14:57:06,406 - logic_logger - INF
..Order[11011] {Update - client} Id: 11011, CustomerId: ALFKI, EmployeeId: 3, OrderDate: 2014-04-09, RequiredDate: 2014-05-07, ShippedDate: None, ShipVia: 1, Freight: 1.2100000000, ShipName: Alfred's Futterkiste, ShipAddress: Obere Str. 57, ShipCity: Berlin, ShipRegion: Western Europe, ShipZip: 12209, ShipCountry: Germany, AmountTotal: 960.00, Country: None, City: None, Ready:  [True-->] False, OrderDetailCount: 2, CloneFromOrder: None  row: 0x10db4e060  session: 0x10d963020  ins_upd_dlt: upd - 2024-07-12 14:57:06,407 - logic_logger - INF
..Order[11011] {Prune Formula: OrderDate [[]]} Id: 11011, CustomerId: ALFKI, EmployeeId: 3, OrderDate: 2014-04-09, RequiredDate: 2014-05-07, ShippedDate: None, ShipVia: 1, Freight: 1.2100000000, ShipName: Alfred's Futterkiste, ShipAddress: Obere Str. 57, ShipCity: Berlin, ShipRegion: Western Europe, ShipZip: 12209, ShipCountry: Germany, AmountTotal: 960.00, Country: None, City: None, Ready:  [True-->] False, OrderDetailCount: 2, CloneFromOrder: None  row: 0x10db4e060  session: 0x10d963020  ins_upd_dlt: upd - 2024-07-12 14:57:06,408 - logic_logger - INF
....Customer[ALFKI] {Update - Adjusting Customer: Balance} Id: ALFKI, CompanyName: Alfreds Futterkiste, ContactName: Maria Anders, ContactTitle: Sales Representative, Address: Obere Str. 57A, City: Berlin, Region: Western Europe, PostalCode: 12209, Country: Germany, Phone: 030-0074321, Fax: 030-0076545, Balance:  [2102.0000000000-->] 1142.0000000000, CreditLimit: 2300.0000000000, OrderCount: 15, UnpaidOrderCount: 10, Client_id: 1  row: 0x10dcaf890  session: 0x10d963020  ins_upd_dlt: upd - 2024-07-12 14:57:06,412 - logic_logger - INF
Logic Phase:		COMMIT LOGIC		(session=0x10d963020)   										 - 2024-07-12 14:57:06,416 - logic_logger - INF
..Order[11011] {Commit Event} Id: 11011, CustomerId: ALFKI, EmployeeId: 3, OrderDate: 2014-04-09, RequiredDate: 2014-05-07, ShippedDate: None, ShipVia: 1, Freight: 1.2100000000, ShipName: Alfred's Futterkiste, ShipAddress: Obere Str. 57, ShipCity: Berlin, ShipRegion: Western Europe, ShipZip: 12209, ShipCountry: Germany, AmountTotal: 960.00, Country: None, City: None, Ready:  [True-->] False, OrderDetailCount: 2, CloneFromOrder: None  row: 0x10db4e060  session: 0x10d963020  ins_upd_dlt: upd - 2024-07-12 14:57:06,416 - logic_logger - INF
..Order[11011] {Commit Event} Id: 11011, CustomerId: ALFKI, EmployeeId: 3, OrderDate: 2014-04-09, RequiredDate: 2014-05-07, ShippedDate: None, ShipVia: 1, Freight: 1.2100000000, ShipName: Alfred's Futterkiste, ShipAddress: Obere Str. 57, ShipCity: Berlin, ShipRegion: Western Europe, ShipZip: 12209, ShipCountry: Germany, AmountTotal: 960.00, Country: None, City: None, Ready:  [True-->] False, OrderDetailCount: 2, CloneFromOrder: None  row: 0x10db4e060  session: 0x10d963020  ins_upd_dlt: upd - 2024-07-12 14:57:06,417 - logic_logger - INF
Logic Phase:		AFTER_FLUSH LOGIC	(session=0x10d963020)   										 - 2024-07-12 14:57:06,422 - logic_logger - INF
..Order[11011] {AfterFlush Event} Id: 11011, CustomerId: ALFKI, EmployeeId: 3, OrderDate: 2014-04-09, RequiredDate: 2014-05-07, ShippedDate: None, ShipVia: 1, Freight: 1.2100000000, ShipName: Alfred's Futterkiste, ShipAddress: Obere Str. 57, ShipCity: Berlin, ShipRegion: Western Europe, ShipZip: 12209, ShipCountry: Germany, AmountTotal: 960.00, Country: None, City: None, Ready:  [True-->] False, OrderDetailCount: 2, CloneFromOrder: None  row: 0x10db4e060  session: 0x10d963020  ins_upd_dlt: upd - 2024-07-12 14:57:06,423 - logic_logger - INF

```
</details>
  
&nbsp;
&nbsp;
### Scenario: Order Made Ready
&emsp;  Scenario: Order Made Ready  
&emsp;&emsp;    Given Customer Account: ALFKI  
&emsp;&emsp;    When Ready Flag is Set  
&emsp;&emsp;    Then Logic Increases Balance  
<details markdown>
<summary>Tests - and their logic - are transparent.. click to see Logic</summary>


&nbsp;
&nbsp;


**Logic Doc** for scenario: Order Made Ready
   
This illustrates the _ready flag_ pattern:
1. Add a ready flag to the Order
2. Make logic contingent on the ready flag:
    * Customer.Balance is increased only if the Order is ready
    * Empty Orders are not rejected

This enables the user to submit multiple transactions (add order details, alter them etc),
before making the order ready (like a checkout).

Until then, Customer's Balance adjustments, or empty orders constraints do not fire.

> **Key Takeaway:** the ready flag defers constraints/derivations until the user is ready.

> **Key Takeaway:** adjustment from change in qualification condition



&nbsp;
&nbsp;


**Rules Used** in Scenario: Order Made Ready
```
  Customer  
    1. RowEvent Customer.customer_defaults()   
    2. Derive Customer.UnpaidOrderCount as Count(<class 'database.models.Order'> Where <function declare_logic.<locals>.<lambda> at 0x10b9596c0>)  
    3. Derive Customer.OrderCount as Count(<class 'database.models.Order'> Where None)  
    4. Derive Customer.Balance as Sum(Order.AmountTotal Where <function declare_logic.<locals>.<lambda> at 0x10b83fd80>)  
  Order  
    5. RowEvent Order.do_not_ship_empty_orders()   
    6. RowEvent Order.send_order_to_shipping()   
    7. RowEvent Order.congratulate_sales_rep()   
    8. RowEvent Order.clone_order()   
    9. RowEvent Order.order_defaults()   
  
```
**Logic Log** in Scenario: Order Made Ready
```

Logic Phase:		ROW LOGIC		(session=0x10dd240b0) (sqlalchemy before_flush)			 - 2024-07-12 14:57:06,786 - logic_logger - INF
..Order[11011] {Update - client} Id: 11011, CustomerId: ALFKI, EmployeeId: 3, OrderDate: 2014-04-09, RequiredDate: 2014-05-07, ShippedDate: None, ShipVia: 1, Freight: 1.2100000000, ShipName: Alfred's Futterkiste, ShipAddress: Obere Str. 57, ShipCity: Berlin, ShipRegion: Western Europe, ShipZip: 12209, ShipCountry: Germany, AmountTotal: 960.00, Country: None, City: None, Ready:  [False-->] True, OrderDetailCount: 2, CloneFromOrder: None  row: 0x10dd27740  session: 0x10dd240b0  ins_upd_dlt: upd - 2024-07-12 14:57:06,787 - logic_logger - INF
..Order[11011] {Prune Formula: OrderDate [[]]} Id: 11011, CustomerId: ALFKI, EmployeeId: 3, OrderDate: 2014-04-09, RequiredDate: 2014-05-07, ShippedDate: None, ShipVia: 1, Freight: 1.2100000000, ShipName: Alfred's Futterkiste, ShipAddress: Obere Str. 57, ShipCity: Berlin, ShipRegion: Western Europe, ShipZip: 12209, ShipCountry: Germany, AmountTotal: 960.00, Country: None, City: None, Ready:  [False-->] True, OrderDetailCount: 2, CloneFromOrder: None  row: 0x10dd27740  session: 0x10dd240b0  ins_upd_dlt: upd - 2024-07-12 14:57:06,788 - logic_logger - INF
....Customer[ALFKI] {Update - Adjusting Customer: Balance} Id: ALFKI, CompanyName: Alfreds Futterkiste, ContactName: Maria Anders, ContactTitle: Sales Representative, Address: Obere Str. 57A, City: Berlin, Region: Western Europe, PostalCode: 12209, Country: Germany, Phone: 030-0074321, Fax: 030-0076545, Balance:  [1142.0000000000-->] 2102.0000000000, CreditLimit: 2300.0000000000, OrderCount: 15, UnpaidOrderCount: 10, Client_id: 1  row: 0x10dcae1b0  session: 0x10dd240b0  ins_upd_dlt: upd - 2024-07-12 14:57:06,790 - logic_logger - INF
Logic Phase:		COMMIT LOGIC		(session=0x10dd240b0)   										 - 2024-07-12 14:57:06,794 - logic_logger - INF
..Order[11011] {Commit Event} Id: 11011, CustomerId: ALFKI, EmployeeId: 3, OrderDate: 2014-04-09, RequiredDate: 2014-05-07, ShippedDate: None, ShipVia: 1, Freight: 1.2100000000, ShipName: Alfred's Futterkiste, ShipAddress: Obere Str. 57, ShipCity: Berlin, ShipRegion: Western Europe, ShipZip: 12209, ShipCountry: Germany, AmountTotal: 960.00, Country: None, City: None, Ready:  [False-->] True, OrderDetailCount: 2, CloneFromOrder: None  row: 0x10dd27740  session: 0x10dd240b0  ins_upd_dlt: upd - 2024-07-12 14:57:06,794 - logic_logger - INF
..Order[11011] {Commit Event} Id: 11011, CustomerId: ALFKI, EmployeeId: 3, OrderDate: 2014-04-09, RequiredDate: 2014-05-07, ShippedDate: None, ShipVia: 1, Freight: 1.2100000000, ShipName: Alfred's Futterkiste, ShipAddress: Obere Str. 57, ShipCity: Berlin, ShipRegion: Western Europe, ShipZip: 12209, ShipCountry: Germany, AmountTotal: 960.00, Country: None, City: None, Ready:  [False-->] True, OrderDetailCount: 2, CloneFromOrder: None  row: 0x10dd27740  session: 0x10dd240b0  ins_upd_dlt: upd - 2024-07-12 14:57:06,794 - logic_logger - INF
Logic Phase:		AFTER_FLUSH LOGIC	(session=0x10dd240b0)   										 - 2024-07-12 14:57:06,796 - logic_logger - INF
..Order[11011] {AfterFlush Event} Id: 11011, CustomerId: ALFKI, EmployeeId: 3, OrderDate: 2014-04-09, RequiredDate: 2014-05-07, ShippedDate: None, ShipVia: 1, Freight: 1.2100000000, ShipName: Alfred's Futterkiste, ShipAddress: Obere Str. 57, ShipCity: Berlin, ShipRegion: Western Europe, ShipZip: 12209, ShipCountry: Germany, AmountTotal: 960.00, Country: None, City: None, Ready:  [False-->] True, OrderDetailCount: 2, CloneFromOrder: None  row: 0x10dd27740  session: 0x10dd240b0  ins_upd_dlt: upd - 2024-07-12 14:57:06,797 - logic_logger - INF
..Order[11011] {Sending Order to Shipping << not activated >>} Id: 11011, CustomerId: ALFKI, EmployeeId: 3, OrderDate: 2014-04-09, RequiredDate: 2014-05-07, ShippedDate: None, ShipVia: 1, Freight: 1.2100000000, ShipName: Alfred's Futterkiste, ShipAddress: Obere Str. 57, ShipCity: Berlin, ShipRegion: Western Europe, ShipZip: 12209, ShipCountry: Germany, AmountTotal: 960.00, Country: None, City: None, Ready:  [False-->] True, OrderDetailCount: 2, CloneFromOrder: None  row: 0x10dd27740  session: 0x10dd240b0  ins_upd_dlt: upd - 2024-07-12 14:57:06,806 - logic_logger - INF

```
</details>
  
&nbsp;
&nbsp;
### Scenario: Good Order Custom Service
&emsp;  Scenario: Good Order Custom Service  
&emsp;&emsp;    Given Customer Account: ALFKI  
&emsp;&emsp;    When Good Order Placed  
&emsp;&emsp;    Then Logic adjusts Balance (demo: chain up)  
&emsp;&emsp;    Then Logic adjusts Products Reordered  
&emsp;&emsp;    Then Logic sends email to salesrep  
&emsp;&emsp;    Then Logic sends kafka message  
&emsp;&emsp;    Then Logic adjusts aggregates down on delete order  
<details markdown>
<summary>Tests - and their logic - are transparent.. click to see Logic</summary>


&nbsp;
&nbsp;


**Logic Doc** for scenario: Good Order Custom Service
   
Familiar logic patterns:

* Constrain a derived result (Check Credit)
* Chain up, to adjust parent sum/count aggregates (AmountTotal, Balance)
* Events for Lib Access (Kafka, email messages)

Logic Design ("Cocktail Napkin Design")

* Customer.Balance <= CreditLimit
* Customer.Balance = Sum(Order.AmountTotal where unshipped)
* Order.AmountTotal = Sum(OrderDetail.Amount)
* OrderDetail.Amount = Quantity * UnitPrice
* OrderDetail.UnitPrice = copy from Product

We place an Order with an Order Detail.  It's one transaction.

Note how the `Order.AmountTotal` and `Customer.Balance` are *adjusted* as Order Details are processed.
Similarly, the `Product.UnitsShipped` is adjusted, and used to recompute `UnitsInStock`

<figure><img src="https://github.com/valhuber/ApiLogicServer/wiki/images/behave/declare-logic.png?raw=true"></figure>

> **Key Takeaway:** sum/count aggregates (e.g., `Customer.Balance`) automate ***chain up*** multi-table transactions.

**Events - Extensible Logic**

Inspect the log for __Hi, Andrew - Congratulate Nancy on their new order__. 

The `congratulate_sales_rep` event illustrates logic 
[Extensibility](https://apilogicserver.github.io/Docs/Logic/#extensibility-python-events) 
- using Python to provide logic not covered by rules, 
like non-database operations such as sending email or messages.

<figure><img src="https://github.com/valhuber/ApiLogicServer/wiki/images/behave/send-email.png?raw=true"></figure>

There are actually multiple kinds of events:

* *Before* row logic
* *After* row logic
* On *commit,* after all row logic has completed (as here), so that your code "sees" the full logic results

Events are passed the `row` and `old_row`, as well as `logic_row` which enables you to test the actual operation, chaining nest level, etc.

You can set breakpoints in events, and inspect these.

#als: Behave Test, Invoking API from Python



&nbsp;
&nbsp;


**Rules Used** in Scenario: Good Order Custom Service
```
  Customer  
    1. RowEvent Customer.customer_defaults()   
    2. Derive Customer.UnpaidOrderCount as Count(<class 'database.models.Order'> Where <function declare_logic.<locals>.<lambda> at 0x10b9596c0>)  
    3. Derive Customer.Balance as Sum(Order.AmountTotal Where <function declare_logic.<locals>.<lambda> at 0x10b83fd80>)  
    4. Derive Customer.OrderCount as Count(<class 'database.models.Order'> Where None)  
  Order  
    5. RowEvent Order.do_not_ship_empty_orders()   
    6. Derive Order.AmountTotal as Sum(OrderDetail.Amount Where None)  
    7. RowEvent Order.congratulate_sales_rep()   
    8. RowEvent Order.send_order_to_shipping()   
    9. RowEvent Order.clone_order()   
    10. Derive Order.OrderDetailCount as Count(<class 'database.models.OrderDetail'> Where None)  
    11. Derive Order.OrderDate as Formula (1): as_expression=lambda row: datetime.datetime.now())  
    12. RowEvent Order.order_defaults()   
  OrderDetail  
    13. Derive OrderDetail.Amount as Formula (1): as_expression=lambda row: row.UnitPrice * row.Qua [...]  
    14. Derive OrderDetail.ShippedDate as Formula (2): row.Order.ShippedDate  
    15. RowEvent OrderDetail.order_detail_defaults()   
    16. Derive OrderDetail.UnitPrice as Copy(Product.UnitPrice)  
  Product  
    17. Derive Product.UnitsInStock as Formula (1): <function>  
    18. Derive Product.UnitsShipped as Sum(OrderDetail.Quantity Where <function declare_logic.<locals>.<lambda> at 0x10b959580>)  
  
```
**Logic Log** in Scenario: Good Order Custom Service
```

Logic Phase:		ROW LOGIC		(session=0x10dd24320) (sqlalchemy before_flush)			 - 2024-07-12 14:57:07,152 - logic_logger - INF
..Order[None] {Insert - client} Id: None, CustomerId: ALFKI, EmployeeId: 1, OrderDate: None, RequiredDate: None, ShippedDate: None, ShipVia: None, Freight: 11, ShipName: None, ShipAddress: None, ShipCity: None, ShipRegion: None, ShipZip: None, ShipCountry: None, AmountTotal: None, Country: None, City: None, Ready: True, OrderDetailCount: None, CloneFromOrder: None  row: 0x10dd25520  session: 0x10dd24320  ins_upd_dlt: ins - 2024-07-12 14:57:07,153 - logic_logger - INF
..Order[None] {server_defaults: OrderDetailCount -- skipped: Ready[BOOLEAN (not handled)] } Id: None, CustomerId: ALFKI, EmployeeId: 1, OrderDate: None, RequiredDate: None, ShippedDate: None, ShipVia: None, Freight: 11, ShipName: None, ShipAddress: None, ShipCity: None, ShipRegion: None, ShipZip: None, ShipCountry: None, AmountTotal: None, Country: None, City: None, Ready: True, OrderDetailCount: 0, CloneFromOrder: None  row: 0x10dd25520  session: 0x10dd24320  ins_upd_dlt: ins - 2024-07-12 14:57:07,154 - logic_logger - INF
..Order[None] {Formula OrderDate} Id: None, CustomerId: ALFKI, EmployeeId: 1, OrderDate: 2024-07-12 14:57:07.162349, RequiredDate: None, ShippedDate: None, ShipVia: None, Freight: 11, ShipName: None, ShipAddress: None, ShipCity: None, ShipRegion: None, ShipZip: None, ShipCountry: None, AmountTotal: 0, Country: None, City: None, Ready: True, OrderDetailCount: 0, CloneFromOrder: None  row: 0x10dd25520  session: 0x10dd24320  ins_upd_dlt: ins - 2024-07-12 14:57:07,162 - logic_logger - INF
....Customer[ALFKI] {Update - Adjusting Customer: UnpaidOrderCount, OrderCount} Id: ALFKI, CompanyName: Alfreds Futterkiste, ContactName: Maria Anders, ContactTitle: Sales Representative, Address: Obere Str. 57A, City: Berlin, Region: Western Europe, PostalCode: 12209, Country: Germany, Phone: 030-0074321, Fax: 030-0076545, Balance: 2102.0000000000, CreditLimit: 2300.0000000000, OrderCount:  [15-->] 16, UnpaidOrderCount:  [10-->] 11, Client_id: 1  row: 0x10dbbcd10  session: 0x10dd24320  ins_upd_dlt: upd - 2024-07-12 14:57:07,163 - logic_logger - INF
..OrderDetail[None] {Insert - client} Id: None, OrderId: None, ProductId: 1, UnitPrice: None, Quantity: 1, Discount: 0, Amount: None, ShippedDate: None  row: 0x10db4eea0  session: 0x10dd24320  ins_upd_dlt: ins - 2024-07-12 14:57:07,166 - logic_logger - INF
..OrderDetail[None] {copy_rules for role: Product - UnitPrice} Id: None, OrderId: None, ProductId: 1, UnitPrice: 18.0000000000, Quantity: 1, Discount: 0, Amount: None, ShippedDate: None  row: 0x10db4eea0  session: 0x10dd24320  ins_upd_dlt: ins - 2024-07-12 14:57:07,169 - logic_logger - INF
..OrderDetail[None] {Formula Amount} Id: None, OrderId: None, ProductId: 1, UnitPrice: 18.0000000000, Quantity: 1, Discount: 0, Amount: 18.0000000000, ShippedDate: None  row: 0x10db4eea0  session: 0x10dd24320  ins_upd_dlt: ins - 2024-07-12 14:57:07,170 - logic_logger - INF
....Order[None] {Update - Adjusting Order: AmountTotal, OrderDetailCount} Id: None, CustomerId: ALFKI, EmployeeId: 1, OrderDate: 2024-07-12 14:57:07.162349, RequiredDate: None, ShippedDate: None, ShipVia: None, Freight: 11, ShipName: None, ShipAddress: None, ShipCity: None, ShipRegion: None, ShipZip: None, ShipCountry: None, AmountTotal:  [0-->] 18.0000000000, Country: None, City: None, Ready: True, OrderDetailCount:  [0-->] 1, CloneFromOrder: None  row: 0x10dd25520  session: 0x10dd24320  ins_upd_dlt: upd - 2024-07-12 14:57:07,171 - logic_logger - INF
....Order[None] {Prune Formula: OrderDate [[]]} Id: None, CustomerId: ALFKI, EmployeeId: 1, OrderDate: 2024-07-12 14:57:07.162349, RequiredDate: None, ShippedDate: None, ShipVia: None, Freight: 11, ShipName: None, ShipAddress: None, ShipCity: None, ShipRegion: None, ShipZip: None, ShipCountry: None, AmountTotal:  [0-->] 18.0000000000, Country: None, City: None, Ready: True, OrderDetailCount:  [0-->] 1, CloneFromOrder: None  row: 0x10dd25520  session: 0x10dd24320  ins_upd_dlt: upd - 2024-07-12 14:57:07,172 - logic_logger - INF
......Customer[ALFKI] {Update - Adjusting Customer: Balance} Id: ALFKI, CompanyName: Alfreds Futterkiste, ContactName: Maria Anders, ContactTitle: Sales Representative, Address: Obere Str. 57A, City: Berlin, Region: Western Europe, PostalCode: 12209, Country: Germany, Phone: 030-0074321, Fax: 030-0076545, Balance:  [2102.0000000000-->] 2120.0000000000, CreditLimit: 2300.0000000000, OrderCount: 16, UnpaidOrderCount: 11, Client_id: 1  row: 0x10dbbcd10  session: 0x10dd24320  ins_upd_dlt: upd - 2024-07-12 14:57:07,172 - logic_logger - INF
....Product[1] {Update - Adjusting Product: UnitsShipped} Id: 1, ProductName: Chai, SupplierId: 1, CategoryId: 1, QuantityPerUnit: 10 boxes x 20 bags, UnitPrice: 18.0000000000, UnitsInStock: 39, UnitsOnOrder: 0, ReorderLevel: 10, Discontinued: 0, UnitsShipped:  [0-->] 1  row: 0x10dd268d0  session: 0x10dd24320  ins_upd_dlt: upd - 2024-07-12 14:57:07,176 - logic_logger - INF
....Product[1] {Formula UnitsInStock} Id: 1, ProductName: Chai, SupplierId: 1, CategoryId: 1, QuantityPerUnit: 10 boxes x 20 bags, UnitPrice: 18.0000000000, UnitsInStock:  [39-->] 38, UnitsOnOrder: 0, ReorderLevel: 10, Discontinued: 0, UnitsShipped:  [0-->] 1  row: 0x10dd268d0  session: 0x10dd24320  ins_upd_dlt: upd - 2024-07-12 14:57:07,176 - logic_logger - INF
..OrderDetail[None] {Insert - client} Id: None, OrderId: None, ProductId: 2, UnitPrice: None, Quantity: 2, Discount: 0, Amount: None, ShippedDate: None  row: 0x10dbbfd70  session: 0x10dd24320  ins_upd_dlt: ins - 2024-07-12 14:57:07,177 - logic_logger - INF
..OrderDetail[None] {copy_rules for role: Product - UnitPrice} Id: None, OrderId: None, ProductId: 2, UnitPrice: 19.0000000000, Quantity: 2, Discount: 0, Amount: None, ShippedDate: None  row: 0x10dbbfd70  session: 0x10dd24320  ins_upd_dlt: ins - 2024-07-12 14:57:07,179 - logic_logger - INF
..OrderDetail[None] {Formula Amount} Id: None, OrderId: None, ProductId: 2, UnitPrice: 19.0000000000, Quantity: 2, Discount: 0, Amount: 38.0000000000, ShippedDate: None  row: 0x10dbbfd70  session: 0x10dd24320  ins_upd_dlt: ins - 2024-07-12 14:57:07,180 - logic_logger - INF
....Order[None] {Update - Adjusting Order: AmountTotal, OrderDetailCount} Id: None, CustomerId: ALFKI, EmployeeId: 1, OrderDate: 2024-07-12 14:57:07.162349, RequiredDate: None, ShippedDate: None, ShipVia: None, Freight: 11, ShipName: None, ShipAddress: None, ShipCity: None, ShipRegion: None, ShipZip: None, ShipCountry: None, AmountTotal:  [18.0000000000-->] 56.0000000000, Country: None, City: None, Ready: True, OrderDetailCount:  [1-->] 2, CloneFromOrder: None  row: 0x10dd25520  session: 0x10dd24320  ins_upd_dlt: upd - 2024-07-12 14:57:07,181 - logic_logger - INF
....Order[None] {Prune Formula: OrderDate [[]]} Id: None, CustomerId: ALFKI, EmployeeId: 1, OrderDate: 2024-07-12 14:57:07.162349, RequiredDate: None, ShippedDate: None, ShipVia: None, Freight: 11, ShipName: None, ShipAddress: None, ShipCity: None, ShipRegion: None, ShipZip: None, ShipCountry: None, AmountTotal:  [18.0000000000-->] 56.0000000000, Country: None, City: None, Ready: True, OrderDetailCount:  [1-->] 2, CloneFromOrder: None  row: 0x10dd25520  session: 0x10dd24320  ins_upd_dlt: upd - 2024-07-12 14:57:07,182 - logic_logger - INF
......Customer[ALFKI] {Update - Adjusting Customer: Balance} Id: ALFKI, CompanyName: Alfreds Futterkiste, ContactName: Maria Anders, ContactTitle: Sales Representative, Address: Obere Str. 57A, City: Berlin, Region: Western Europe, PostalCode: 12209, Country: Germany, Phone: 030-0074321, Fax: 030-0076545, Balance:  [2120.0000000000-->] 2158.0000000000, CreditLimit: 2300.0000000000, OrderCount: 16, UnpaidOrderCount: 11, Client_id: 1  row: 0x10dbbcd10  session: 0x10dd24320  ins_upd_dlt: upd - 2024-07-12 14:57:07,182 - logic_logger - INF
....Product[2] {Update - Adjusting Product: UnitsShipped} Id: 2, ProductName: Chang, SupplierId: 1, CategoryId: 1, QuantityPerUnit: 24 - 12 oz bottles, UnitPrice: 19.0000000000, UnitsInStock: 17, UnitsOnOrder: 40, ReorderLevel: 25, Discontinued: 0, UnitsShipped:  [0-->] 2  row: 0x10dcad370  session: 0x10dd24320  ins_upd_dlt: upd - 2024-07-12 14:57:07,186 - logic_logger - INF
....Product[2] {Formula UnitsInStock} Id: 2, ProductName: Chang, SupplierId: 1, CategoryId: 1, QuantityPerUnit: 24 - 12 oz bottles, UnitPrice: 19.0000000000, UnitsInStock:  [17-->] 15, UnitsOnOrder: 40, ReorderLevel: 25, Discontinued: 0, UnitsShipped:  [0-->] 2  row: 0x10dcad370  session: 0x10dd24320  ins_upd_dlt: upd - 2024-07-12 14:57:07,186 - logic_logger - INF
Logic Phase:		COMMIT LOGIC		(session=0x10dd24320)   										 - 2024-07-12 14:57:07,187 - logic_logger - INF
..Order[None] {Commit Event} Id: None, CustomerId: ALFKI, EmployeeId: 1, OrderDate: 2024-07-12 14:57:07.162349, RequiredDate: None, ShippedDate: None, ShipVia: None, Freight: 11, ShipName: None, ShipAddress: None, ShipCity: None, ShipRegion: None, ShipZip: None, ShipCountry: None, AmountTotal: 56.0000000000, Country: None, City: None, Ready: True, OrderDetailCount: 2, CloneFromOrder: None  row: 0x10dd25520  session: 0x10dd24320  ins_upd_dlt: ins - 2024-07-12 14:57:07,188 - logic_logger - INF
..Order[None] {Hi, Andrew - Congratulate Nancy on their new order} Id: None, CustomerId: ALFKI, EmployeeId: 1, OrderDate: 2024-07-12 14:57:07.162349, RequiredDate: None, ShippedDate: None, ShipVia: None, Freight: 11, ShipName: None, ShipAddress: None, ShipCity: None, ShipRegion: None, ShipZip: None, ShipCountry: None, AmountTotal: 56.0000000000, Country: None, City: None, Ready: True, OrderDetailCount: 2, CloneFromOrder: None  row: 0x10dd25520  session: 0x10dd24320  ins_upd_dlt: ins - 2024-07-12 14:57:07,190 - logic_logger - INF
..Order[None] {Illustrate database access} Id: None, CustomerId: ALFKI, EmployeeId: 1, OrderDate: 2024-07-12 14:57:07.162349, RequiredDate: None, ShippedDate: None, ShipVia: None, Freight: 11, ShipName: None, ShipAddress: None, ShipCity: None, ShipRegion: None, ShipZip: None, ShipCountry: None, AmountTotal: 56.0000000000, Country: None, City: None, Ready: True, OrderDetailCount: 2, CloneFromOrder: None  row: 0x10dd25520  session: 0x10dd24320  ins_upd_dlt: ins - 2024-07-12 14:57:07,192 - logic_logger - INF
..Order[None] {Commit Event} Id: None, CustomerId: ALFKI, EmployeeId: 1, OrderDate: 2024-07-12 14:57:07.162349, RequiredDate: None, ShippedDate: None, ShipVia: None, Freight: 11, ShipName: None, ShipAddress: None, ShipCity: None, ShipRegion: None, ShipZip: None, ShipCountry: None, AmountTotal: 56.0000000000, Country: None, City: None, Ready: True, OrderDetailCount: 2, CloneFromOrder: None  row: 0x10dd25520  session: 0x10dd24320  ins_upd_dlt: ins - 2024-07-12 14:57:07,193 - logic_logger - INF
Logic Phase:		AFTER_FLUSH LOGIC	(session=0x10dd24320)   										 - 2024-07-12 14:57:07,206 - logic_logger - INF
..Order[11078] {AfterFlush Event} Id: 11078, CustomerId: ALFKI, EmployeeId: 1, OrderDate: 2024-07-12 14:57:07.162349, RequiredDate: None, ShippedDate: None, ShipVia: None, Freight: 11, ShipName: None, ShipAddress: None, ShipCity: None, ShipRegion: None, ShipZip: None, ShipCountry: None, AmountTotal: 56.0000000000, Country: None, City: None, Ready: True, OrderDetailCount: 2, CloneFromOrder: None  row: 0x10dd25520  session: 0x10dd24320  ins_upd_dlt: ins - 2024-07-12 14:57:07,207 - logic_logger - INF
..Order[11078] {Sending Order to Shipping << not activated >>} Id: 11078, CustomerId: ALFKI, EmployeeId: 1, OrderDate: 2024-07-12 14:57:07.162349, RequiredDate: None, ShippedDate: None, ShipVia: None, Freight: 11, ShipName: None, ShipAddress: None, ShipCity: None, ShipRegion: None, ShipZip: None, ShipCountry: None, AmountTotal: 56.0000000000, Country: None, City: None, Ready: True, OrderDetailCount: 2, CloneFromOrder: None  row: 0x10dd25520  session: 0x10dd24320  ins_upd_dlt: ins - 2024-07-12 14:57:07,211 - logic_logger - INF

```
</details>
  
&nbsp;
&nbsp;
### Scenario: Bad Ship of Empty Order
&emsp;  Scenario: Bad Ship of Empty Order  
&emsp;&emsp;    Given Customer Account: ALFKI  
&emsp;&emsp;    When Order Shipped with no Items  
&emsp;&emsp;    Then Rejected per Do Not Ship Empty Orders  
<details markdown>
<summary>Tests - and their logic - are transparent.. click to see Logic</summary>


&nbsp;
&nbsp;


**Logic Doc** for scenario: Bad Ship of Empty Order
   
Reuse the rules for Good Order...

Familiar logic patterns:

* Constrain a derived result
* Counts as existence checks

Logic Design ("Cocktail Napkin Design")

* Constraint: do_not_ship_empty_orders()
* Order.OrderDetailCount = count(OrderDetail)



&nbsp;
&nbsp;


**Rules Used** in Scenario: Bad Ship of Empty Order
```
```
**Logic Log** in Scenario: Bad Ship of Empty Order
```

Logic Phase:		ROW LOGIC		(session=0x10dbbd370) (sqlalchemy before_flush)			 - 2024-07-12 14:57:07,836 - logic_logger - INF
..Order[None] {Insert - client} Id: None, CustomerId: ALFKI, EmployeeId: 1, OrderDate: None, RequiredDate: None, ShippedDate: 2013-10-13, ShipVia: None, Freight: 10, ShipName: None, ShipAddress: None, ShipCity: None, ShipRegion: None, ShipZip: None, ShipCountry: None, AmountTotal: None, Country: None, City: None, Ready: True, OrderDetailCount: None, CloneFromOrder: None  row: 0x10dd409b0  session: 0x10dbbd370  ins_upd_dlt: ins - 2024-07-12 14:57:07,837 - logic_logger - INF
..Order[None] {server_defaults: OrderDetailCount -- skipped: Ready[BOOLEAN (not handled)] } Id: None, CustomerId: ALFKI, EmployeeId: 1, OrderDate: None, RequiredDate: None, ShippedDate: 2013-10-13, ShipVia: None, Freight: 10, ShipName: None, ShipAddress: None, ShipCity: None, ShipRegion: None, ShipZip: None, ShipCountry: None, AmountTotal: None, Country: None, City: None, Ready: True, OrderDetailCount: 0, CloneFromOrder: None  row: 0x10dd409b0  session: 0x10dbbd370  ins_upd_dlt: ins - 2024-07-12 14:57:07,837 - logic_logger - INF
..Order[None] {Formula OrderDate} Id: None, CustomerId: ALFKI, EmployeeId: 1, OrderDate: 2024-07-12 14:57:07.841810, RequiredDate: None, ShippedDate: 2013-10-13, ShipVia: None, Freight: 10, ShipName: None, ShipAddress: None, ShipCity: None, ShipRegion: None, ShipZip: None, ShipCountry: None, AmountTotal: 0, Country: None, City: None, Ready: True, OrderDetailCount: 0, CloneFromOrder: None  row: 0x10dd409b0  session: 0x10dbbd370  ins_upd_dlt: ins - 2024-07-12 14:57:07,842 - logic_logger - INF
....Customer[ALFKI] {Update - Adjusting Customer: OrderCount} Id: ALFKI, CompanyName: Alfreds Futterkiste, ContactName: Maria Anders, ContactTitle: Sales Representative, Address: Obere Str. 57A, City: Berlin, Region: Western Europe, PostalCode: 12209, Country: Germany, Phone: 030-0074321, Fax: 030-0076545, Balance: 2102.0000000000, CreditLimit: 2300.0000000000, OrderCount:  [15-->] 16, UnpaidOrderCount: 10, Client_id: 1  row: 0x10dd276e0  session: 0x10dbbd370  ins_upd_dlt: upd - 2024-07-12 14:57:07,842 - logic_logger - INF
Logic Phase:		COMMIT LOGIC		(session=0x10dbbd370)   										 - 2024-07-12 14:57:07,845 - logic_logger - INF
..Order[None] {Commit Event} Id: None, CustomerId: ALFKI, EmployeeId: 1, OrderDate: 2024-07-12 14:57:07.841810, RequiredDate: None, ShippedDate: 2013-10-13, ShipVia: None, Freight: 10, ShipName: None, ShipAddress: None, ShipCity: None, ShipRegion: None, ShipZip: None, ShipCountry: None, AmountTotal: 0, Country: None, City: None, Ready: True, OrderDetailCount: 0, CloneFromOrder: None  row: 0x10dd409b0  session: 0x10dbbd370  ins_upd_dlt: ins - 2024-07-12 14:57:07,846 - logic_logger - INF
..Order[None] {Hi, Andrew - Congratulate Nancy on their new order} Id: None, CustomerId: ALFKI, EmployeeId: 1, OrderDate: 2024-07-12 14:57:07.841810, RequiredDate: None, ShippedDate: 2013-10-13, ShipVia: None, Freight: 10, ShipName: None, ShipAddress: None, ShipCity: None, ShipRegion: None, ShipZip: None, ShipCountry: None, AmountTotal: 0, Country: None, City: None, Ready: True, OrderDetailCount: 0, CloneFromOrder: None  row: 0x10dd409b0  session: 0x10dbbd370  ins_upd_dlt: ins - 2024-07-12 14:57:07,847 - logic_logger - INF
..Order[None] {Illustrate database access} Id: None, CustomerId: ALFKI, EmployeeId: 1, OrderDate: 2024-07-12 14:57:07.841810, RequiredDate: None, ShippedDate: 2013-10-13, ShipVia: None, Freight: 10, ShipName: None, ShipAddress: None, ShipCity: None, ShipRegion: None, ShipZip: None, ShipCountry: None, AmountTotal: 0, Country: None, City: None, Ready: True, OrderDetailCount: 0, CloneFromOrder: None  row: 0x10dd409b0  session: 0x10dbbd370  ins_upd_dlt: ins - 2024-07-12 14:57:07,848 - logic_logger - INF
..Order[None] {Commit Event} Id: None, CustomerId: ALFKI, EmployeeId: 1, OrderDate: 2024-07-12 14:57:07.841810, RequiredDate: None, ShippedDate: 2013-10-13, ShipVia: None, Freight: 10, ShipName: None, ShipAddress: None, ShipCity: None, ShipRegion: None, ShipZip: None, ShipCountry: None, AmountTotal: 0, Country: None, City: None, Ready: True, OrderDetailCount: 0, CloneFromOrder: None  row: 0x10dd409b0  session: 0x10dbbd370  ins_upd_dlt: ins - 2024-07-12 14:57:07,849 - logic_logger - INF
```
</details>
  
&nbsp;
&nbsp;
### Scenario: Bad Order Custom Service
&emsp;  Scenario: Bad Order Custom Service  
&emsp;&emsp;    Given Customer Account: ALFKI  
&emsp;&emsp;    When Order Placed with excessive quantity  
&emsp;&emsp;    Then Rejected per Check Credit  
<details markdown>
<summary>Tests - and their logic - are transparent.. click to see Logic</summary>


&nbsp;
&nbsp;


**Logic Doc** for scenario: Bad Order Custom Service
   
Reuse the rules for Good Order...

Familiar logic patterns:

* Constrain a derived result
* Chain up, to adjust parent sum/count aggregates

Logic Design ("Cocktail Napkin Design")

* Customer.Balance <= CreditLimit
* Customer.Balance = Sum(Order.AmountTotal where unshipped)
* Order.AmountTotal = Sum(OrderDetail.Amount)
* OrderDetail.Amount = Quantity * UnitPrice
* OrderDetail.UnitPrice = copy from Product



&nbsp;
&nbsp;


**Rules Used** in Scenario: Bad Order Custom Service
```
  Customer  
    1. RowEvent Customer.customer_defaults()   
    2. Derive Customer.UnpaidOrderCount as Count(<class 'database.models.Order'> Where <function declare_logic.<locals>.<lambda> at 0x10b9596c0>)  
    3. Constraint Function: None   
    4. Derive Customer.Balance as Sum(Order.AmountTotal Where <function declare_logic.<locals>.<lambda> at 0x10b83fd80>)  
    5. Derive Customer.OrderCount as Count(<class 'database.models.Order'> Where None)  
  Order  
    6. Derive Order.AmountTotal as Sum(OrderDetail.Amount Where None)  
    7. RowEvent Order.clone_order()   
    8. Derive Order.OrderDetailCount as Count(<class 'database.models.OrderDetail'> Where None)  
    9. Derive Order.OrderDate as Formula (1): as_expression=lambda row: datetime.datetime.now())  
    10. RowEvent Order.order_defaults()   
  OrderDetail  
    11. Derive OrderDetail.Amount as Formula (1): as_expression=lambda row: row.UnitPrice * row.Qua [...]  
    12. Derive OrderDetail.ShippedDate as Formula (2): row.Order.ShippedDate  
    13. RowEvent OrderDetail.order_detail_defaults()   
    14. Derive OrderDetail.UnitPrice as Copy(Product.UnitPrice)  
  Product  
    15. Derive Product.UnitsInStock as Formula (1): <function>  
    16. Derive Product.UnitsShipped as Sum(OrderDetail.Quantity Where <function declare_logic.<locals>.<lambda> at 0x10b959580>)  
```
**Logic Log** in Scenario: Bad Order Custom Service
```

Logic Phase:		ROW LOGIC		(session=0x10dd260c0) (sqlalchemy before_flush)			 - 2024-07-12 14:57:08,015 - logic_logger - INF
..Order[None] {Insert - client} Id: None, CustomerId: ALFKI, EmployeeId: 1, OrderDate: None, RequiredDate: None, ShippedDate: None, ShipVia: None, Freight: 10, ShipName: None, ShipAddress: None, ShipCity: None, ShipRegion: None, ShipZip: None, ShipCountry: None, AmountTotal: None, Country: None, City: None, Ready: True, OrderDetailCount: None, CloneFromOrder: None  row: 0x10dd27680  session: 0x10dd260c0  ins_upd_dlt: ins - 2024-07-12 14:57:08,016 - logic_logger - INF
..Order[None] {server_defaults: OrderDetailCount -- skipped: Ready[BOOLEAN (not handled)] } Id: None, CustomerId: ALFKI, EmployeeId: 1, OrderDate: None, RequiredDate: None, ShippedDate: None, ShipVia: None, Freight: 10, ShipName: None, ShipAddress: None, ShipCity: None, ShipRegion: None, ShipZip: None, ShipCountry: None, AmountTotal: None, Country: None, City: None, Ready: True, OrderDetailCount: 0, CloneFromOrder: None  row: 0x10dd27680  session: 0x10dd260c0  ins_upd_dlt: ins - 2024-07-12 14:57:08,016 - logic_logger - INF
..Order[None] {Formula OrderDate} Id: None, CustomerId: ALFKI, EmployeeId: 1, OrderDate: 2024-07-12 14:57:08.020499, RequiredDate: None, ShippedDate: None, ShipVia: None, Freight: 10, ShipName: None, ShipAddress: None, ShipCity: None, ShipRegion: None, ShipZip: None, ShipCountry: None, AmountTotal: 0, Country: None, City: None, Ready: True, OrderDetailCount: 0, CloneFromOrder: None  row: 0x10dd27680  session: 0x10dd260c0  ins_upd_dlt: ins - 2024-07-12 14:57:08,020 - logic_logger - INF
....Customer[ALFKI] {Update - Adjusting Customer: UnpaidOrderCount, OrderCount} Id: ALFKI, CompanyName: Alfreds Futterkiste, ContactName: Maria Anders, ContactTitle: Sales Representative, Address: Obere Str. 57A, City: Berlin, Region: Western Europe, PostalCode: 12209, Country: Germany, Phone: 030-0074321, Fax: 030-0076545, Balance: 2102.0000000000, CreditLimit: 2300.0000000000, OrderCount:  [15-->] 16, UnpaidOrderCount:  [10-->] 11, Client_id: 1  row: 0x10dd76a20  session: 0x10dd260c0  ins_upd_dlt: upd - 2024-07-12 14:57:08,021 - logic_logger - INF
..OrderDetail[None] {Insert - client} Id: None, OrderId: None, ProductId: 2, UnitPrice: None, Quantity: 2, Discount: 0, Amount: None, ShippedDate: None  row: 0x10dd76180  session: 0x10dd260c0  ins_upd_dlt: ins - 2024-07-12 14:57:08,024 - logic_logger - INF
..OrderDetail[None] {copy_rules for role: Product - UnitPrice} Id: None, OrderId: None, ProductId: 2, UnitPrice: 19.0000000000, Quantity: 2, Discount: 0, Amount: None, ShippedDate: None  row: 0x10dd76180  session: 0x10dd260c0  ins_upd_dlt: ins - 2024-07-12 14:57:08,027 - logic_logger - INF
..OrderDetail[None] {Formula Amount} Id: None, OrderId: None, ProductId: 2, UnitPrice: 19.0000000000, Quantity: 2, Discount: 0, Amount: 38.0000000000, ShippedDate: None  row: 0x10dd76180  session: 0x10dd260c0  ins_upd_dlt: ins - 2024-07-12 14:57:08,028 - logic_logger - INF
....Order[None] {Update - Adjusting Order: AmountTotal, OrderDetailCount} Id: None, CustomerId: ALFKI, EmployeeId: 1, OrderDate: 2024-07-12 14:57:08.020499, RequiredDate: None, ShippedDate: None, ShipVia: None, Freight: 10, ShipName: None, ShipAddress: None, ShipCity: None, ShipRegion: None, ShipZip: None, ShipCountry: None, AmountTotal:  [0-->] 38.0000000000, Country: None, City: None, Ready: True, OrderDetailCount:  [0-->] 1, CloneFromOrder: None  row: 0x10dd27680  session: 0x10dd260c0  ins_upd_dlt: upd - 2024-07-12 14:57:08,029 - logic_logger - INF
....Order[None] {Prune Formula: OrderDate [[]]} Id: None, CustomerId: ALFKI, EmployeeId: 1, OrderDate: 2024-07-12 14:57:08.020499, RequiredDate: None, ShippedDate: None, ShipVia: None, Freight: 10, ShipName: None, ShipAddress: None, ShipCity: None, ShipRegion: None, ShipZip: None, ShipCountry: None, AmountTotal:  [0-->] 38.0000000000, Country: None, City: None, Ready: True, OrderDetailCount:  [0-->] 1, CloneFromOrder: None  row: 0x10dd27680  session: 0x10dd260c0  ins_upd_dlt: upd - 2024-07-12 14:57:08,030 - logic_logger - INF
......Customer[ALFKI] {Update - Adjusting Customer: Balance} Id: ALFKI, CompanyName: Alfreds Futterkiste, ContactName: Maria Anders, ContactTitle: Sales Representative, Address: Obere Str. 57A, City: Berlin, Region: Western Europe, PostalCode: 12209, Country: Germany, Phone: 030-0074321, Fax: 030-0076545, Balance:  [2102.0000000000-->] 2140.0000000000, CreditLimit: 2300.0000000000, OrderCount: 16, UnpaidOrderCount: 11, Client_id: 1  row: 0x10dd76a20  session: 0x10dd260c0  ins_upd_dlt: upd - 2024-07-12 14:57:08,031 - logic_logger - INF
....Product[2] {Update - Adjusting Product: UnitsShipped} Id: 2, ProductName: Chang, SupplierId: 1, CategoryId: 1, QuantityPerUnit: 24 - 12 oz bottles, UnitPrice: 19.0000000000, UnitsInStock: 17, UnitsOnOrder: 40, ReorderLevel: 25, Discontinued: 0, UnitsShipped:  [0-->] 2  row: 0x10dd772c0  session: 0x10dd260c0  ins_upd_dlt: upd - 2024-07-12 14:57:08,035 - logic_logger - INF
....Product[2] {Formula UnitsInStock} Id: 2, ProductName: Chang, SupplierId: 1, CategoryId: 1, QuantityPerUnit: 24 - 12 oz bottles, UnitPrice: 19.0000000000, UnitsInStock:  [17-->] 15, UnitsOnOrder: 40, ReorderLevel: 25, Discontinued: 0, UnitsShipped:  [0-->] 2  row: 0x10dd772c0  session: 0x10dd260c0  ins_upd_dlt: upd - 2024-07-12 14:57:08,035 - logic_logger - INF
..OrderDetail[None] {Insert - client} Id: None, OrderId: None, ProductId: 1, UnitPrice: None, Quantity: 1111, Discount: 0, Amount: None, ShippedDate: None  row: 0x10dd76270  session: 0x10dd260c0  ins_upd_dlt: ins - 2024-07-12 14:57:08,036 - logic_logger - INF
..OrderDetail[None] {copy_rules for role: Product - UnitPrice} Id: None, OrderId: None, ProductId: 1, UnitPrice: 18.0000000000, Quantity: 1111, Discount: 0, Amount: None, ShippedDate: None  row: 0x10dd76270  session: 0x10dd260c0  ins_upd_dlt: ins - 2024-07-12 14:57:08,038 - logic_logger - INF
..OrderDetail[None] {Formula Amount} Id: None, OrderId: None, ProductId: 1, UnitPrice: 18.0000000000, Quantity: 1111, Discount: 0, Amount: 19998.0000000000, ShippedDate: None  row: 0x10dd76270  session: 0x10dd260c0  ins_upd_dlt: ins - 2024-07-12 14:57:08,038 - logic_logger - INF
....Order[None] {Update - Adjusting Order: AmountTotal, OrderDetailCount} Id: None, CustomerId: ALFKI, EmployeeId: 1, OrderDate: 2024-07-12 14:57:08.020499, RequiredDate: None, ShippedDate: None, ShipVia: None, Freight: 10, ShipName: None, ShipAddress: None, ShipCity: None, ShipRegion: None, ShipZip: None, ShipCountry: None, AmountTotal:  [38.0000000000-->] 20036.0000000000, Country: None, City: None, Ready: True, OrderDetailCount:  [1-->] 2, CloneFromOrder: None  row: 0x10dd27680  session: 0x10dd260c0  ins_upd_dlt: upd - 2024-07-12 14:57:08,039 - logic_logger - INF
....Order[None] {Prune Formula: OrderDate [[]]} Id: None, CustomerId: ALFKI, EmployeeId: 1, OrderDate: 2024-07-12 14:57:08.020499, RequiredDate: None, ShippedDate: None, ShipVia: None, Freight: 10, ShipName: None, ShipAddress: None, ShipCity: None, ShipRegion: None, ShipZip: None, ShipCountry: None, AmountTotal:  [38.0000000000-->] 20036.0000000000, Country: None, City: None, Ready: True, OrderDetailCount:  [1-->] 2, CloneFromOrder: None  row: 0x10dd27680  session: 0x10dd260c0  ins_upd_dlt: upd - 2024-07-12 14:57:08,040 - logic_logger - INF
......Customer[ALFKI] {Update - Adjusting Customer: Balance} Id: ALFKI, CompanyName: Alfreds Futterkiste, ContactName: Maria Anders, ContactTitle: Sales Representative, Address: Obere Str. 57A, City: Berlin, Region: Western Europe, PostalCode: 12209, Country: Germany, Phone: 030-0074321, Fax: 030-0076545, Balance:  [2140.0000000000-->] 22138.0000000000, CreditLimit: 2300.0000000000, OrderCount: 16, UnpaidOrderCount: 11, Client_id: 1  row: 0x10dd76a20  session: 0x10dd260c0  ins_upd_dlt: upd - 2024-07-12 14:57:08,041 - logic_logger - INF
......Customer[ALFKI] {Constraint Failure: balance (22138.00) exceeds credit (2300.00)} Id: ALFKI, CompanyName: Alfreds Futterkiste, ContactName: Maria Anders, ContactTitle: Sales Representative, Address: Obere Str. 57A, City: Berlin, Region: Western Europe, PostalCode: 12209, Country: Germany, Phone: 030-0074321, Fax: 030-0076545, Balance:  [2140.0000000000-->] 22138.0000000000, CreditLimit: 2300.0000000000, OrderCount: 16, UnpaidOrderCount: 11, Client_id: 1  row: 0x10dd76a20  session: 0x10dd260c0  ins_upd_dlt: upd - 2024-07-12 14:57:08,042 - logic_logger - INF

```
</details>
  
&nbsp;
&nbsp;
### Scenario: Alter Item Qty to exceed credit
&emsp;  Scenario: Alter Item Qty to exceed credit  
&emsp;&emsp;    Given Customer Account: ALFKI  
&emsp;&emsp;    When Order Detail Quantity altered very high  
&emsp;&emsp;    Then Rejected per Check Credit  
<details markdown>
<summary>Tests - and their logic - are transparent.. click to see Logic</summary>


&nbsp;
&nbsp;


**Logic Doc** for scenario: Alter Item Qty to exceed credit
   
Same constraint as above.

> **Key Takeaway:** Automatic Reuse (_design one, solve many_)


&nbsp;
&nbsp;


**Rules Used** in Scenario: Alter Item Qty to exceed credit
```
  Customer  
    1. RowEvent Customer.customer_defaults()   
    2. Derive Customer.UnpaidOrderCount as Count(<class 'database.models.Order'> Where <function declare_logic.<locals>.<lambda> at 0x10b9596c0>)  
    3. Constraint Function: None   
    4. Derive Customer.Balance as Sum(Order.AmountTotal Where <function declare_logic.<locals>.<lambda> at 0x10b83fd80>)  
    5. Derive Customer.OrderCount as Count(<class 'database.models.Order'> Where None)  
  Order  
    6. Derive Order.AmountTotal as Sum(OrderDetail.Amount Where None)  
    7. Derive Order.OrderDetailCount as Count(<class 'database.models.OrderDetail'> Where None)  
    8. RowEvent Order.order_defaults()   
  OrderDetail  
    9. RowEvent OrderDetail.order_detail_defaults()   
    10. Derive OrderDetail.Amount as Formula (1): as_expression=lambda row: row.UnitPrice * row.Qua [...]  
```
**Logic Log** in Scenario: Alter Item Qty to exceed credit
```

Logic Phase:		ROW LOGIC		(session=0x10df71280) (sqlalchemy before_flush)			 - 2024-07-12 14:57:08,230 - logic_logger - INF
..OrderDetail[1040] {Update - client} Id: 1040, OrderId: 10643, ProductId: 28, UnitPrice: 45.6000000000, Quantity:  [15-->] 1110, Discount: 0.25, Amount: 684.0000000000, ShippedDate: None  row: 0x10dd76000  session: 0x10df71280  ins_upd_dlt: upd - 2024-07-12 14:57:08,231 - logic_logger - INF
..OrderDetail[1040] {Formula Amount} Id: 1040, OrderId: 10643, ProductId: 28, UnitPrice: 45.6000000000, Quantity:  [15-->] 1110, Discount: 0.25, Amount:  [684.0000000000-->] 50616.0000000000, ShippedDate: None  row: 0x10dd76000  session: 0x10df71280  ins_upd_dlt: upd - 2024-07-12 14:57:08,232 - logic_logger - INF
..OrderDetail[1040] {Prune Formula: ShippedDate [['Order.ShippedDate']]} Id: 1040, OrderId: 10643, ProductId: 28, UnitPrice: 45.6000000000, Quantity:  [15-->] 1110, Discount: 0.25, Amount:  [684.0000000000-->] 50616.0000000000, ShippedDate: None  row: 0x10dd76000  session: 0x10df71280  ins_upd_dlt: upd - 2024-07-12 14:57:08,232 - logic_logger - INF
....Order[10643] {Update - Adjusting Order: AmountTotal} Id: 10643, CustomerId: ALFKI, EmployeeId: 6, OrderDate: 2013-08-25, RequiredDate: 2013-09-22, ShippedDate: None, ShipVia: 1, Freight: 29.4600000000, ShipName: Alfreds Futterkiste, ShipAddress: Obere Str. 57, ShipCity: Berlin, ShipRegion: Western Europe, ShipZip: 12209, ShipCountry: Germany, AmountTotal:  [1086.00-->] 51018.0000000000, Country: None, City: None, Ready: True, OrderDetailCount: 3, CloneFromOrder: None  row: 0x10df718b0  session: 0x10df71280  ins_upd_dlt: upd - 2024-07-12 14:57:08,235 - logic_logger - INF
....Order[10643] {Prune Formula: OrderDate [[]]} Id: 10643, CustomerId: ALFKI, EmployeeId: 6, OrderDate: 2013-08-25, RequiredDate: 2013-09-22, ShippedDate: None, ShipVia: 1, Freight: 29.4600000000, ShipName: Alfreds Futterkiste, ShipAddress: Obere Str. 57, ShipCity: Berlin, ShipRegion: Western Europe, ShipZip: 12209, ShipCountry: Germany, AmountTotal:  [1086.00-->] 51018.0000000000, Country: None, City: None, Ready: True, OrderDetailCount: 3, CloneFromOrder: None  row: 0x10df718b0  session: 0x10df71280  ins_upd_dlt: upd - 2024-07-12 14:57:08,236 - logic_logger - INF
......Customer[ALFKI] {Update - Adjusting Customer: Balance} Id: ALFKI, CompanyName: Alfreds Futterkiste, ContactName: Maria Anders, ContactTitle: Sales Representative, Address: Obere Str. 57A, City: Berlin, Region: Western Europe, PostalCode: 12209, Country: Germany, Phone: 030-0074321, Fax: 030-0076545, Balance:  [2102.0000000000-->] 52034.0000000000, CreditLimit: 2300.0000000000, OrderCount: 15, UnpaidOrderCount: 10, Client_id: 1  row: 0x10df71760  session: 0x10df71280  ins_upd_dlt: upd - 2024-07-12 14:57:08,238 - logic_logger - INF
......Customer[ALFKI] {Constraint Failure: balance (52034.00) exceeds credit (2300.00)} Id: ALFKI, CompanyName: Alfreds Futterkiste, ContactName: Maria Anders, ContactTitle: Sales Representative, Address: Obere Str. 57A, City: Berlin, Region: Western Europe, PostalCode: 12209, Country: Germany, Phone: 030-0074321, Fax: 030-0076545, Balance:  [2102.0000000000-->] 52034.0000000000, CreditLimit: 2300.0000000000, OrderCount: 15, UnpaidOrderCount: 10, Client_id: 1  row: 0x10df71760  session: 0x10df71280  ins_upd_dlt: upd - 2024-07-12 14:57:08,239 - logic_logger - INF

```
</details>
  
&nbsp;
&nbsp;
### Scenario: Alter Required Date - adjust logic pruned
&emsp;  Scenario: Alter Required Date - adjust logic pruned  
&emsp;&emsp;    Given Customer Account: ALFKI  
&emsp;&emsp;    When Order RequiredDate altered (2013-10-13)  
&emsp;&emsp;    Then Balance not adjusted  
<details markdown>
<summary>Tests - and their logic - are transparent.. click to see Logic</summary>


&nbsp;
&nbsp;


**Logic Doc** for scenario: Alter Required Date - adjust logic pruned
   
We set `Order.RequiredDate`.

This is a normal update.  Nothing depends on the columns altered, so this has no effect on the related Customer, Order Details or Products.  Contrast this to the *Cascade Update Test* and the *Custom Service* test, where logic chaining affects related rows.  Only the commit event fires.

> **Key Takeaway:** rule pruning automatically avoids unnecessary SQL overhead.



&nbsp;
&nbsp;


**Rules Used** in Scenario: Alter Required Date - adjust logic pruned
```
  Customer  
    1. Derive Customer.UnpaidOrderCount as Count(<class 'database.models.Order'> Where <function declare_logic.<locals>.<lambda> at 0x10b9596c0>)  
    2. Derive Customer.OrderCount as Count(<class 'database.models.Order'> Where None)  
    3. Derive Customer.Balance as Sum(Order.AmountTotal Where <function declare_logic.<locals>.<lambda> at 0x10b83fd80>)  
  Order  
    4. RowEvent Order.do_not_ship_empty_orders()   
    5. RowEvent Order.send_order_to_shipping()   
    6. RowEvent Order.congratulate_sales_rep()   
    7. RowEvent Order.clone_order()   
    8. RowEvent Order.order_defaults()   
  
```
**Logic Log** in Scenario: Alter Required Date - adjust logic pruned
```

Logic Phase:		ROW LOGIC		(session=0x10df73920) (sqlalchemy before_flush)			 - 2024-07-12 14:57:08,435 - logic_logger - INF
..Order[10643] {Update - client} Id: 10643, CustomerId: ALFKI, EmployeeId: 6, OrderDate: 2013-08-25, RequiredDate:  [2013-09-22-->] 2013-10-13 00:00:00, ShippedDate: None, ShipVia: 1, Freight: 29.4600000000, ShipName: Alfreds Futterkiste, ShipAddress: Obere Str. 57, ShipCity: Berlin, ShipRegion: Western Europe, ShipZip: 12209, ShipCountry: Germany, AmountTotal: 1086.00, Country: None, City: None, Ready: True, OrderDetailCount: 3, CloneFromOrder: None  row: 0x10df71f70  session: 0x10df73920  ins_upd_dlt: upd - 2024-07-12 14:57:08,436 - logic_logger - INF
..Order[10643] {Prune Formula: OrderDate [[]]} Id: 10643, CustomerId: ALFKI, EmployeeId: 6, OrderDate: 2013-08-25, RequiredDate:  [2013-09-22-->] 2013-10-13 00:00:00, ShippedDate: None, ShipVia: 1, Freight: 29.4600000000, ShipName: Alfreds Futterkiste, ShipAddress: Obere Str. 57, ShipCity: Berlin, ShipRegion: Western Europe, ShipZip: 12209, ShipCountry: Germany, AmountTotal: 1086.00, Country: None, City: None, Ready: True, OrderDetailCount: 3, CloneFromOrder: None  row: 0x10df71f70  session: 0x10df73920  ins_upd_dlt: upd - 2024-07-12 14:57:08,437 - logic_logger - INF
Logic Phase:		COMMIT LOGIC		(session=0x10df73920)   										 - 2024-07-12 14:57:08,439 - logic_logger - INF
..Order[10643] {Commit Event} Id: 10643, CustomerId: ALFKI, EmployeeId: 6, OrderDate: 2013-08-25, RequiredDate:  [2013-09-22-->] 2013-10-13 00:00:00, ShippedDate: None, ShipVia: 1, Freight: 29.4600000000, ShipName: Alfreds Futterkiste, ShipAddress: Obere Str. 57, ShipCity: Berlin, ShipRegion: Western Europe, ShipZip: 12209, ShipCountry: Germany, AmountTotal: 1086.00, Country: None, City: None, Ready: True, OrderDetailCount: 3, CloneFromOrder: None  row: 0x10df71f70  session: 0x10df73920  ins_upd_dlt: upd - 2024-07-12 14:57:08,439 - logic_logger - INF
..Order[10643] {Commit Event} Id: 10643, CustomerId: ALFKI, EmployeeId: 6, OrderDate: 2013-08-25, RequiredDate:  [2013-09-22-->] 2013-10-13 00:00:00, ShippedDate: None, ShipVia: 1, Freight: 29.4600000000, ShipName: Alfreds Futterkiste, ShipAddress: Obere Str. 57, ShipCity: Berlin, ShipRegion: Western Europe, ShipZip: 12209, ShipCountry: Germany, AmountTotal: 1086.00, Country: None, City: None, Ready: True, OrderDetailCount: 3, CloneFromOrder: None  row: 0x10df71f70  session: 0x10df73920  ins_upd_dlt: upd - 2024-07-12 14:57:08,440 - logic_logger - INF
Logic Phase:		AFTER_FLUSH LOGIC	(session=0x10df73920)   										 - 2024-07-12 14:57:08,442 - logic_logger - INF
..Order[10643] {AfterFlush Event} Id: 10643, CustomerId: ALFKI, EmployeeId: 6, OrderDate: 2013-08-25, RequiredDate:  [2013-09-22-->] 2013-10-13 00:00:00, ShippedDate: None, ShipVia: 1, Freight: 29.4600000000, ShipName: Alfreds Futterkiste, ShipAddress: Obere Str. 57, ShipCity: Berlin, ShipRegion: Western Europe, ShipZip: 12209, ShipCountry: Germany, AmountTotal: 1086.00, Country: None, City: None, Ready: True, OrderDetailCount: 3, CloneFromOrder: None  row: 0x10df71f70  session: 0x10df73920  ins_upd_dlt: upd - 2024-07-12 14:57:08,442 - logic_logger - INF

```
</details>
  
&nbsp;
&nbsp;
### Scenario: Set Shipped - adjust logic reuse
&emsp;  Scenario: Set Shipped - adjust logic reuse  
&emsp;&emsp;    Given Customer Account: ALFKI  
&emsp;&emsp;    When Order ShippedDate altered (2013-10-13)  
&emsp;&emsp;    Then Balance reduced 1086  
<details markdown>
<summary>Tests - and their logic - are transparent.. click to see Logic</summary>


&nbsp;
&nbsp;


**Logic Doc** for scenario: Set Shipped - adjust logic reuse
   

Logic Patterns:

* Chain Down

Logic Design ("Cocktail Napkin Design")

* Formula: OrderDetail.ShippedDate = Order.ShippedDate

We set `Order.ShippedDate`.

This cascades to the Order Details, per the `derive=models.OrderDetail.ShippedDate` rule.

This chains to adjust the `Product.UnitsShipped` and recomputes `UnitsInStock`, as above

<figure><img src="https://github.com/valhuber/ApiLogicServer/wiki/images/behave/order-shipped-date.png?raw=true"></figure>


> **Key Takeaway:** parent references (e.g., `OrderDetail.ShippedDate`) automate ***chain-down*** multi-table transactions.

> **Key Takeaway:** Automatic Reuse (_design one, solve many_)



&nbsp;
&nbsp;


**Rules Used** in Scenario: Set Shipped - adjust logic reuse
```
  Customer  
    1. RowEvent Customer.customer_defaults()   
    2. Derive Customer.UnpaidOrderCount as Count(<class 'database.models.Order'> Where <function declare_logic.<locals>.<lambda> at 0x10b9596c0>)  
    3. Derive Customer.OrderCount as Count(<class 'database.models.Order'> Where None)  
    4. Derive Customer.Balance as Sum(Order.AmountTotal Where <function declare_logic.<locals>.<lambda> at 0x10b83fd80>)  
  Order  
    5. RowEvent Order.do_not_ship_empty_orders()   
    6. RowEvent Order.send_order_to_shipping()   
    7. RowEvent Order.congratulate_sales_rep()   
    8. RowEvent Order.clone_order()   
    9. RowEvent Order.order_defaults()   
  
```
**Logic Log** in Scenario: Set Shipped - adjust logic reuse
```

Logic Phase:		ROW LOGIC		(session=0x10dd240e0) (sqlalchemy before_flush)			 - 2024-07-12 14:57:08,810 - logic_logger - INF
..Order[10643] {Update - client} Id: 10643, CustomerId: ALFKI, EmployeeId: 6, OrderDate: 2013-08-25, RequiredDate: 2013-10-13, ShippedDate:  [None-->] 2013-10-13, ShipVia: 1, Freight: 29.4600000000, ShipName: Alfreds Futterkiste, ShipAddress: Obere Str. 57, ShipCity: Berlin, ShipRegion: Western Europe, ShipZip: 12209, ShipCountry: Germany, AmountTotal: 1086.00, Country: None, City: None, Ready: True, OrderDetailCount: 3, CloneFromOrder: None  row: 0x10dd75280  session: 0x10dd240e0  ins_upd_dlt: upd - 2024-07-12 14:57:08,810 - logic_logger - INF
..Order[10643] {Prune Formula: OrderDate [[]]} Id: 10643, CustomerId: ALFKI, EmployeeId: 6, OrderDate: 2013-08-25, RequiredDate: 2013-10-13, ShippedDate:  [None-->] 2013-10-13, ShipVia: 1, Freight: 29.4600000000, ShipName: Alfreds Futterkiste, ShipAddress: Obere Str. 57, ShipCity: Berlin, ShipRegion: Western Europe, ShipZip: 12209, ShipCountry: Germany, AmountTotal: 1086.00, Country: None, City: None, Ready: True, OrderDetailCount: 3, CloneFromOrder: None  row: 0x10dd75280  session: 0x10dd240e0  ins_upd_dlt: upd - 2024-07-12 14:57:08,811 - logic_logger - INF
....Customer[ALFKI] {Update - Adjusting Customer: Balance, UnpaidOrderCount} Id: ALFKI, CompanyName: Alfreds Futterkiste, ContactName: Maria Anders, ContactTitle: Sales Representative, Address: Obere Str. 57A, City: Berlin, Region: Western Europe, PostalCode: 12209, Country: Germany, Phone: 030-0074321, Fax: 030-0076545, Balance:  [2102.0000000000-->] 1016.0000000000, CreditLimit: 2300.0000000000, OrderCount: 15, UnpaidOrderCount:  [10-->] 9, Client_id: 1  row: 0x10db76ab0  session: 0x10dd240e0  ins_upd_dlt: upd - 2024-07-12 14:57:08,813 - logic_logger - INF
Logic Phase:		COMMIT LOGIC		(session=0x10dd240e0)   										 - 2024-07-12 14:57:08,817 - logic_logger - INF
..Order[10643] {Commit Event} Id: 10643, CustomerId: ALFKI, EmployeeId: 6, OrderDate: 2013-08-25, RequiredDate: 2013-10-13, ShippedDate:  [None-->] 2013-10-13, ShipVia: 1, Freight: 29.4600000000, ShipName: Alfreds Futterkiste, ShipAddress: Obere Str. 57, ShipCity: Berlin, ShipRegion: Western Europe, ShipZip: 12209, ShipCountry: Germany, AmountTotal: 1086.00, Country: None, City: None, Ready: True, OrderDetailCount: 3, CloneFromOrder: None  row: 0x10dd75280  session: 0x10dd240e0  ins_upd_dlt: upd - 2024-07-12 14:57:08,818 - logic_logger - INF
..Order[10643] {Commit Event} Id: 10643, CustomerId: ALFKI, EmployeeId: 6, OrderDate: 2013-08-25, RequiredDate: 2013-10-13, ShippedDate:  [None-->] 2013-10-13, ShipVia: 1, Freight: 29.4600000000, ShipName: Alfreds Futterkiste, ShipAddress: Obere Str. 57, ShipCity: Berlin, ShipRegion: Western Europe, ShipZip: 12209, ShipCountry: Germany, AmountTotal: 1086.00, Country: None, City: None, Ready: True, OrderDetailCount: 3, CloneFromOrder: None  row: 0x10dd75280  session: 0x10dd240e0  ins_upd_dlt: upd - 2024-07-12 14:57:08,818 - logic_logger - INF
Logic Phase:		AFTER_FLUSH LOGIC	(session=0x10dd240e0)   										 - 2024-07-12 14:57:08,822 - logic_logger - INF
..Order[10643] {AfterFlush Event} Id: 10643, CustomerId: ALFKI, EmployeeId: 6, OrderDate: 2013-08-25, RequiredDate: 2013-10-13, ShippedDate:  [None-->] 2013-10-13, ShipVia: 1, Freight: 29.4600000000, ShipName: Alfreds Futterkiste, ShipAddress: Obere Str. 57, ShipCity: Berlin, ShipRegion: Western Europe, ShipZip: 12209, ShipCountry: Germany, AmountTotal: 1086.00, Country: None, City: None, Ready: True, OrderDetailCount: 3, CloneFromOrder: None  row: 0x10dd75280  session: 0x10dd240e0  ins_upd_dlt: upd - 2024-07-12 14:57:08,822 - logic_logger - INF

```
</details>
  
&nbsp;
&nbsp;
### Scenario: Reset Shipped - adjust logic reuse
&emsp;  Scenario: Reset Shipped - adjust logic reuse  
&emsp;&emsp;    Given Shipped Order  
&emsp;&emsp;    When Order ShippedDate set to None  
&emsp;&emsp;    Then Logic adjusts Balance by -1086  
<details markdown>
<summary>Tests - and their logic - are transparent.. click to see Logic</summary>


&nbsp;
&nbsp;


**Logic Doc** for scenario: Reset Shipped - adjust logic reuse
   
Same logic as above.

> **Key Takeaway:** Automatic Reuse (_design one, solve many_)


&nbsp;
&nbsp;


**Rules Used** in Scenario: Reset Shipped - adjust logic reuse
```
  Customer  
    1. RowEvent Customer.customer_defaults()   
    2. Derive Customer.UnpaidOrderCount as Count(<class 'database.models.Order'> Where <function declare_logic.<locals>.<lambda> at 0x10b9596c0>)  
    3. Derive Customer.OrderCount as Count(<class 'database.models.Order'> Where None)  
    4. Derive Customer.Balance as Sum(Order.AmountTotal Where <function declare_logic.<locals>.<lambda> at 0x10b83fd80>)  
  Order  
    5. RowEvent Order.do_not_ship_empty_orders()   
    6. RowEvent Order.send_order_to_shipping()   
    7. RowEvent Order.congratulate_sales_rep()   
    8. RowEvent Order.clone_order()   
    9. RowEvent Order.order_defaults()   
  
```
**Logic Log** in Scenario: Reset Shipped - adjust logic reuse
```

Logic Phase:		ROW LOGIC		(session=0x10df9e6c0) (sqlalchemy before_flush)			 - 2024-07-12 14:57:09,181 - logic_logger - INF
..Order[10643] {Update - client} Id: 10643, CustomerId: ALFKI, EmployeeId: 6, OrderDate: 2013-08-25, RequiredDate: 2013-10-13, ShippedDate:  [2013-10-13-->] None, ShipVia: 1, Freight: 29.4600000000, ShipName: Alfreds Futterkiste, ShipAddress: Obere Str. 57, ShipCity: Berlin, ShipRegion: Western Europe, ShipZip: 12209, ShipCountry: Germany, AmountTotal: 1086.00, Country: None, City: None, Ready: True, OrderDetailCount: 3, CloneFromOrder: None  row: 0x10df70b30  session: 0x10df9e6c0  ins_upd_dlt: upd - 2024-07-12 14:57:09,182 - logic_logger - INF
..Order[10643] {Prune Formula: OrderDate [[]]} Id: 10643, CustomerId: ALFKI, EmployeeId: 6, OrderDate: 2013-08-25, RequiredDate: 2013-10-13, ShippedDate:  [2013-10-13-->] None, ShipVia: 1, Freight: 29.4600000000, ShipName: Alfreds Futterkiste, ShipAddress: Obere Str. 57, ShipCity: Berlin, ShipRegion: Western Europe, ShipZip: 12209, ShipCountry: Germany, AmountTotal: 1086.00, Country: None, City: None, Ready: True, OrderDetailCount: 3, CloneFromOrder: None  row: 0x10df70b30  session: 0x10df9e6c0  ins_upd_dlt: upd - 2024-07-12 14:57:09,183 - logic_logger - INF
....Customer[ALFKI] {Update - Adjusting Customer: Balance, UnpaidOrderCount} Id: ALFKI, CompanyName: Alfreds Futterkiste, ContactName: Maria Anders, ContactTitle: Sales Representative, Address: Obere Str. 57A, City: Berlin, Region: Western Europe, PostalCode: 12209, Country: Germany, Phone: 030-0074321, Fax: 030-0076545, Balance:  [1016.0000000000-->] 2102.0000000000, CreditLimit: 2300.0000000000, OrderCount: 15, UnpaidOrderCount:  [9-->] 10, Client_id: 1  row: 0x10df9cd70  session: 0x10df9e6c0  ins_upd_dlt: upd - 2024-07-12 14:57:09,185 - logic_logger - INF
Logic Phase:		COMMIT LOGIC		(session=0x10df9e6c0)   										 - 2024-07-12 14:57:09,189 - logic_logger - INF
..Order[10643] {Commit Event} Id: 10643, CustomerId: ALFKI, EmployeeId: 6, OrderDate: 2013-08-25, RequiredDate: 2013-10-13, ShippedDate:  [2013-10-13-->] None, ShipVia: 1, Freight: 29.4600000000, ShipName: Alfreds Futterkiste, ShipAddress: Obere Str. 57, ShipCity: Berlin, ShipRegion: Western Europe, ShipZip: 12209, ShipCountry: Germany, AmountTotal: 1086.00, Country: None, City: None, Ready: True, OrderDetailCount: 3, CloneFromOrder: None  row: 0x10df70b30  session: 0x10df9e6c0  ins_upd_dlt: upd - 2024-07-12 14:57:09,189 - logic_logger - INF
..Order[10643] {Commit Event} Id: 10643, CustomerId: ALFKI, EmployeeId: 6, OrderDate: 2013-08-25, RequiredDate: 2013-10-13, ShippedDate:  [2013-10-13-->] None, ShipVia: 1, Freight: 29.4600000000, ShipName: Alfreds Futterkiste, ShipAddress: Obere Str. 57, ShipCity: Berlin, ShipRegion: Western Europe, ShipZip: 12209, ShipCountry: Germany, AmountTotal: 1086.00, Country: None, City: None, Ready: True, OrderDetailCount: 3, CloneFromOrder: None  row: 0x10df70b30  session: 0x10df9e6c0  ins_upd_dlt: upd - 2024-07-12 14:57:09,190 - logic_logger - INF
Logic Phase:		AFTER_FLUSH LOGIC	(session=0x10df9e6c0)   										 - 2024-07-12 14:57:09,192 - logic_logger - INF
..Order[10643] {AfterFlush Event} Id: 10643, CustomerId: ALFKI, EmployeeId: 6, OrderDate: 2013-08-25, RequiredDate: 2013-10-13, ShippedDate:  [2013-10-13-->] None, ShipVia: 1, Freight: 29.4600000000, ShipName: Alfreds Futterkiste, ShipAddress: Obere Str. 57, ShipCity: Berlin, ShipRegion: Western Europe, ShipZip: 12209, ShipCountry: Germany, AmountTotal: 1086.00, Country: None, City: None, Ready: True, OrderDetailCount: 3, CloneFromOrder: None  row: 0x10df70b30  session: 0x10df9e6c0  ins_upd_dlt: upd - 2024-07-12 14:57:09,192 - logic_logger - INF

```
</details>
  
&nbsp;
&nbsp;
### Scenario: Clone Existing Order
&emsp;  Scenario: Clone Existing Order  
&emsp;&emsp;    Given Shipped Order  
&emsp;&emsp;    When Cloning Existing Order  
&emsp;&emsp;    Then Logic Copies ClonedFrom OrderDetails  
<details markdown>
<summary>Tests - and their logic - are transparent.. click to see Logic</summary>


&nbsp;
&nbsp;


**Logic Doc** for scenario: Clone Existing Order
   
We create an order, setting CloneFromOrder.

This copies the CloneFromOrder OrderDetails to our new Order.

The copy operation is automated using `logic_row.copy_children()`:

1. `place_order.feature` defines the test

2. `place_order.py` implements the test.  It uses the API to Post an Order, setting `CloneFromOrder` to trigger the copy logic

3. `declare_logic.py` implements the logic, by invoking `logic_row.copy_children()`.  `which` defines which children to copy, here just `OrderDetailList`

<figure><img src="https://github.com/valhuber/ApiLogicServer/wiki/images/behave/clone-order.png?raw=true"></figure>

`CopyChildren` For more information, [see here](https://github.com/valhuber/LogicBank/wiki/Copy-Children)

    Useful in row event handlers to copy multiple children types to self from copy_from children.

    child-spec := < ‘child-list-name’ | < ‘child-list-name = parent-list-name’ >
    child-list-spec := [child-spec | (child-spec, child-list-spec)]

    Eg. RowEvent on Order
        which = ["OrderDetailList"]
        logic_row.copy_children(copy_from=row.parent, which_children=which)

    Eg, test/copy_children:
        child_list_spec = [
            ("MileStoneList",
                ["DeliverableList"]  # for each Milestone, get the Deliverables
            ),
            "StaffList"
        ]

> **Key Takeaway:** copy_children provides a deep-copy service.



&nbsp;
&nbsp;


**Rules Used** in Scenario: Clone Existing Order
```
  Customer  
    1. RowEvent Customer.customer_defaults()   
    2. Derive Customer.UnpaidOrderCount as Count(<class 'database.models.Order'> Where <function declare_logic.<locals>.<lambda> at 0x10b9596c0>)  
    3. Constraint Function: None   
    4. Derive Customer.Balance as Sum(Order.AmountTotal Where <function declare_logic.<locals>.<lambda> at 0x10b83fd80>)  
    5. Derive Customer.OrderCount as Count(<class 'database.models.Order'> Where None)  
  Order  
    6. Derive Order.AmountTotal as Sum(OrderDetail.Amount Where None)  
    7. RowEvent Order.clone_order()   
    8. Derive Order.OrderDetailCount as Count(<class 'database.models.OrderDetail'> Where None)  
    9. Derive Order.OrderDate as Formula (1): as_expression=lambda row: datetime.datetime.now())  
    10. RowEvent Order.order_defaults()   
  OrderDetail  
    11. Derive OrderDetail.Amount as Formula (1): as_expression=lambda row: row.UnitPrice * row.Qua [...]  
    12. Derive OrderDetail.ShippedDate as Formula (2): row.Order.ShippedDate  
    13. RowEvent OrderDetail.order_detail_defaults()   
    14. Derive OrderDetail.UnitPrice as Copy(Product.UnitPrice)  
```
**Logic Log** in Scenario: Clone Existing Order
```

Logic Phase:		ROW LOGIC		(session=0x10df9d8b0) (sqlalchemy before_flush)			 - 2024-07-12 14:57:09,533 - logic_logger - INF
..Order[None] {Insert - client} Id: None, CustomerId: ALFKI, EmployeeId: 1, OrderDate: None, RequiredDate: None, ShippedDate: None, ShipVia: None, Freight: 11, ShipName: None, ShipAddress: None, ShipCity: None, ShipRegion: None, ShipZip: None, ShipCountry: None, AmountTotal: None, Country: None, City: None, Ready: True, OrderDetailCount: None, CloneFromOrder: 10643  row: 0x10dfbaff0  session: 0x10df9d8b0  ins_upd_dlt: ins - 2024-07-12 14:57:09,534 - logic_logger - INF
..Order[None] {server_defaults: OrderDetailCount -- skipped: Ready[BOOLEAN (not handled)] } Id: None, CustomerId: ALFKI, EmployeeId: 1, OrderDate: None, RequiredDate: None, ShippedDate: None, ShipVia: None, Freight: 11, ShipName: None, ShipAddress: None, ShipCity: None, ShipRegion: None, ShipZip: None, ShipCountry: None, AmountTotal: None, Country: None, City: None, Ready: True, OrderDetailCount: 0, CloneFromOrder: 10643  row: 0x10dfbaff0  session: 0x10df9d8b0  ins_upd_dlt: ins - 2024-07-12 14:57:09,534 - logic_logger - INF
..Order[None] {Formula OrderDate} Id: None, CustomerId: ALFKI, EmployeeId: 1, OrderDate: 2024-07-12 14:57:09.541507, RequiredDate: None, ShippedDate: None, ShipVia: None, Freight: 11, ShipName: None, ShipAddress: None, ShipCity: None, ShipRegion: None, ShipZip: None, ShipCountry: None, AmountTotal: 0, Country: None, City: None, Ready: True, OrderDetailCount: 0, CloneFromOrder: 10643  row: 0x10dfbaff0  session: 0x10df9d8b0  ins_upd_dlt: ins - 2024-07-12 14:57:09,541 - logic_logger - INF
....Customer[ALFKI] {Update - Adjusting Customer: UnpaidOrderCount, OrderCount} Id: ALFKI, CompanyName: Alfreds Futterkiste, ContactName: Maria Anders, ContactTitle: Sales Representative, Address: Obere Str. 57A, City: Berlin, Region: Western Europe, PostalCode: 12209, Country: Germany, Phone: 030-0074321, Fax: 030-0076545, Balance: 2102.0000000000, CreditLimit: 2300.0000000000, OrderCount:  [15-->] 16, UnpaidOrderCount:  [10-->] 11, Client_id: 1  row: 0x10df9fe60  session: 0x10df9d8b0  ins_upd_dlt: upd - 2024-07-12 14:57:09,542 - logic_logger - INF
..Order[None] {Begin copy_children} Id: None, CustomerId: ALFKI, EmployeeId: 1, OrderDate: 2024-07-12 14:57:09.541507, RequiredDate: None, ShippedDate: None, ShipVia: None, Freight: 11, ShipName: None, ShipAddress: None, ShipCity: None, ShipRegion: None, ShipZip: None, ShipCountry: None, AmountTotal: 0, Country: None, City: None, Ready: True, OrderDetailCount: 0, CloneFromOrder: 10643  row: 0x10dfbaff0  session: 0x10df9d8b0  ins_upd_dlt: ins - 2024-07-12 14:57:09,545 - logic_logger - INF
....OrderDetail[None] {Insert - Copy Children OrderDetailList} Id: None, OrderId: None, ProductId:  [None-->] 28, UnitPrice: None, Quantity:  [None-->] 15, Discount:  [None-->] 0.25, Amount: None, ShippedDate: None  row: 0x10df9da90  session: 0x10df9d8b0  ins_upd_dlt: ins - 2024-07-12 14:57:09,547 - logic_logger - INF
....OrderDetail[None] {copy_rules for role: Product - UnitPrice} Id: None, OrderId: None, ProductId:  [None-->] 28, UnitPrice:  [None-->] 45.6000000000, Quantity:  [None-->] 15, Discount:  [None-->] 0.25, Amount: None, ShippedDate: None  row: 0x10df9da90  session: 0x10df9d8b0  ins_upd_dlt: ins - 2024-07-12 14:57:09,549 - logic_logger - INF
....OrderDetail[None] {Formula Amount} Id: None, OrderId: None, ProductId:  [None-->] 28, UnitPrice:  [None-->] 45.6000000000, Quantity:  [None-->] 15, Discount:  [None-->] 0.25, Amount:  [None-->] 684.0000000000, ShippedDate: None  row: 0x10df9da90  session: 0x10df9d8b0  ins_upd_dlt: ins - 2024-07-12 14:57:09,550 - logic_logger - INF
......Order[None] {Update - Adjusting Order: AmountTotal, OrderDetailCount} Id: None, CustomerId: ALFKI, EmployeeId: 1, OrderDate: 2024-07-12 14:57:09.541507, RequiredDate: None, ShippedDate: None, ShipVia: None, Freight: 11, ShipName: None, ShipAddress: None, ShipCity: None, ShipRegion: None, ShipZip: None, ShipCountry: None, AmountTotal:  [0-->] 684.0000000000, Country: None, City: None, Ready: True, OrderDetailCount:  [0-->] 1, CloneFromOrder: 10643  row: 0x10dfbaff0  session: 0x10df9d8b0  ins_upd_dlt: upd - 2024-07-12 14:57:09,551 - logic_logger - INF
......Order[None] {Prune Formula: OrderDate [[]]} Id: None, CustomerId: ALFKI, EmployeeId: 1, OrderDate: 2024-07-12 14:57:09.541507, RequiredDate: None, ShippedDate: None, ShipVia: None, Freight: 11, ShipName: None, ShipAddress: None, ShipCity: None, ShipRegion: None, ShipZip: None, ShipCountry: None, AmountTotal:  [0-->] 684.0000000000, Country: None, City: None, Ready: True, OrderDetailCount:  [0-->] 1, CloneFromOrder: 10643  row: 0x10dfbaff0  session: 0x10df9d8b0  ins_upd_dlt: upd - 2024-07-12 14:57:09,551 - logic_logger - INF
........Customer[ALFKI] {Update - Adjusting Customer: Balance} Id: ALFKI, CompanyName: Alfreds Futterkiste, ContactName: Maria Anders, ContactTitle: Sales Representative, Address: Obere Str. 57A, City: Berlin, Region: Western Europe, PostalCode: 12209, Country: Germany, Phone: 030-0074321, Fax: 030-0076545, Balance:  [2102.0000000000-->] 2786.0000000000, CreditLimit: 2300.0000000000, OrderCount: 16, UnpaidOrderCount: 11, Client_id: 1  row: 0x10df9fe60  session: 0x10df9d8b0  ins_upd_dlt: upd - 2024-07-12 14:57:09,552 - logic_logger - INF
........Customer[ALFKI] {Constraint Failure: balance (2786.00) exceeds credit (2300.00)} Id: ALFKI, CompanyName: Alfreds Futterkiste, ContactName: Maria Anders, ContactTitle: Sales Representative, Address: Obere Str. 57A, City: Berlin, Region: Western Europe, PostalCode: 12209, Country: Germany, Phone: 030-0074321, Fax: 030-0076545, Balance:  [2102.0000000000-->] 2786.0000000000, CreditLimit: 2300.0000000000, OrderCount: 16, UnpaidOrderCount: 11, Client_id: 1  row: 0x10df9fe60  session: 0x10df9d8b0  ins_upd_dlt: upd - 2024-07-12 14:57:09,553 - logic_logger - INF

```
</details>
  
&nbsp;
&nbsp;
## Feature: Salary Change  
  
&nbsp;
&nbsp;
### Scenario: Audit Salary Change
&emsp;  Scenario: Audit Salary Change  
&emsp;&emsp;    Given Employee 5 (Buchanan) - Salary 95k  
&emsp;&emsp;    When Patch Salary to 200k  
&emsp;&emsp;    Then Salary_audit row created  
<details markdown>
<summary>Tests - and their logic - are transparent.. click to see Logic</summary>


&nbsp;
&nbsp;


**Logic Doc** for scenario: Audit Salary Change
   
Logic Patterns:

* Auditing

Logic Design ("Cocktail Napkin Design")

* copy_row(copy_to=models.EmployeeAudit...)

Observe the logic log to see that it creates audit rows:

1. **Discouraged:** you can implement auditing with events.  But auditing is a common pattern, and this can lead to repetitive, tedious code
2. **Preferred:** approaches use [extensible rules](https://github.com/valhuber/LogicBank/wiki/Rule-Extensibility#generic-event-handlers).

Generic event handlers can also reduce redundant code, illustrated in the time/date stamping `handle_all` logic.

This is due to the `copy_row` rule.  Contrast this to the *tedious* `audit_by_event` alternative:

<figure><img src="https://github.com/valhuber/ApiLogicServer/wiki/images/behave/salary_change.png?raw=true"></figure>

> **Key Takeaway:** use **extensible own rule types** to automate pattern you identify; events can result in tedious amounts of code.



&nbsp;
&nbsp;


**Rules Used** in Scenario: Audit Salary Change
```
  
```
**Logic Log** in Scenario: Audit Salary Change
```

Logic Phase:		ROW LOGIC		(session=0x10dfbbdd0) (sqlalchemy before_flush)			 - 2024-07-12 14:57:09,599 - logic_logger - INF
..Employee[5] {Update - client} Id: 5, LastName: Buchanan, FirstName: Steven, Title: Sales Manager, TitleOfCourtesy: Mr., BirthDate: 1987-03-04, HireDate: 2025-10-17, Address: 14 Garrett Hill, City: London, Region: British Isles, PostalCode: SW1 8JR, Country: UK, HomePhone: (71) 555-4848, Extension: 3453, Notes: Steven Buchanan graduated from St. Andrews University, Scotland, with a BSC degree in 1976.  Upon joining the company as a sales representative in 1992, he spent 6 months in an orientation program at the Seattle office and then returned to his permanent post in London.  He was promoted to sales manager in March 1993.  Mr. Buchanan has completed the courses 'Successful Telemarketing' and 'International Sales Management.'  He is fluent in French., ReportsTo: 2, PhotoPath: http://localhost:5656/ui/images/Employee/buchanan.jpg, EmployeeType: Commissioned, Salary:  [95000.0000000000-->] 200000, WorksForDepartmentId: 3, OnLoanDepartmentId: None, UnionId: None, Dues: None  row: 0x10dfbb710  session: 0x10dfbbdd0  ins_upd_dlt: upd - 2024-07-12 14:57:09,600 - logic_logger - INF
..Employee[5] {BEGIN Copy to: EmployeeAudit} Id: 5, LastName: Buchanan, FirstName: Steven, Title: Sales Manager, TitleOfCourtesy: Mr., BirthDate: 1987-03-04, HireDate: 2025-10-17, Address: 14 Garrett Hill, City: London, Region: British Isles, PostalCode: SW1 8JR, Country: UK, HomePhone: (71) 555-4848, Extension: 3453, Notes: Steven Buchanan graduated from St. Andrews University, Scotland, with a BSC degree in 1976.  Upon joining the company as a sales representative in 1992, he spent 6 months in an orientation program at the Seattle office and then returned to his permanent post in London.  He was promoted to sales manager in March 1993.  Mr. Buchanan has completed the courses 'Successful Telemarketing' and 'International Sales Management.'  He is fluent in French., ReportsTo: 2, PhotoPath: http://localhost:5656/ui/images/Employee/buchanan.jpg, EmployeeType: Commissioned, Salary:  [95000.0000000000-->] 200000, WorksForDepartmentId: 3, OnLoanDepartmentId: None, UnionId: None, Dues: None  row: 0x10dfbb710  session: 0x10dfbbdd0  ins_upd_dlt: upd - 2024-07-12 14:57:09,604 - logic_logger - INF
....EmployeeAudit[None] {Insert - Copy EmployeeAudit} Id: None, Title: Sales Manager, Salary: 200000, LastName: Buchanan, FirstName: Steven, EmployeeId: None, CreatedOn: None, UpdatedOn: None, CreatedBy: None, UpdatedBy: None  row: 0x10dfba1b0  session: 0x10dfbbdd0  ins_upd_dlt: ins - 2024-07-12 14:57:09,605 - logic_logger - INF
....EmployeeAudit[None] {early_row_event_all_classes - handle_all did stamping} Id: None, Title: Sales Manager, Salary: 200000, LastName: Buchanan, FirstName: Steven, EmployeeId: None, CreatedOn: 2024-07-12 14:57:09.606065, UpdatedOn: None, CreatedBy: aneu, UpdatedBy: None  row: 0x10dfba1b0  session: 0x10dfbbdd0  ins_upd_dlt: ins - 2024-07-12 14:57:09,606 - logic_logger - INF
Logic Phase:		COMMIT LOGIC		(session=0x10dfbbdd0)   										 - 2024-07-12 14:57:09,607 - logic_logger - INF
Logic Phase:		AFTER_FLUSH LOGIC	(session=0x10dfbbdd0)   										 - 2024-07-12 14:57:09,612 - logic_logger - INF

```
</details>
  
&nbsp;
&nbsp;
### Scenario: Manage ProperSalary
&emsp;  Scenario: Manage ProperSalary  
&emsp;&emsp;    Given Employee 5 (Buchanan) - Salary 95k  
&emsp;&emsp;    When Retrieve Employee Row  
&emsp;&emsp;    Then Verify Contains ProperSalary  
<details markdown>
<summary>Tests - and their logic - are transparent.. click to see Logic</summary>


&nbsp;
&nbsp;


**Logic Doc** for scenario: Manage ProperSalary
   
Observe the use of `old_row
`
> **Key Takeaway:** State Transition Logic enabled per `old_row`



&nbsp;
&nbsp;


**Rules Used** in Scenario: Manage ProperSalary
```
```
**Logic Log** in Scenario: Manage ProperSalary
```
```
</details>
  
&nbsp;
&nbsp;
### Scenario: Raise Must be Meaningful
&emsp;  Scenario: Raise Must be Meaningful  
&emsp;&emsp;    Given Employee 5 (Buchanan) - Salary 95k  
&emsp;&emsp;    When Patch Salary to 96k  
&emsp;&emsp;    Then Reject - Raise too small  
<details markdown>
<summary>Tests - and their logic - are transparent.. click to see Logic</summary>


&nbsp;
&nbsp;


**Logic Doc** for scenario: Raise Must be Meaningful
   
Logic Patterns:

* State Transition Logic

Logic Design ("Cocktail Napkin Design")

* Rule.constraint(validate=Employee, calling=raise_over_20_percent...)

Observe the use of `old_row
`
> **Key Takeaway:** State Transition Logic enabled per `old_row`



&nbsp;
&nbsp;


**Rules Used** in Scenario: Raise Must be Meaningful
```
  Employee  
    1. Constraint Function: <function declare_logic.<locals>.raise_over_20_percent at 0x10b959940>   
```
**Logic Log** in Scenario: Raise Must be Meaningful
```

Logic Phase:		ROW LOGIC		(session=0x10dfd4b60) (sqlalchemy before_flush)			 - 2024-07-12 14:57:09,907 - logic_logger - INF
..Employee[5] {Update - client} Id: 5, LastName: Buchanan, FirstName: Steven, Title: Sales Manager, TitleOfCourtesy: Mr., BirthDate: 1987-03-04, HireDate: 2025-10-17, Address: 14 Garrett Hill, City: London, Region: British Isles, PostalCode: SW1 8JR, Country: UK, HomePhone: (71) 555-4848, Extension: 3453, Notes: Steven Buchanan graduated from St. Andrews University, Scotland, with a BSC degree in 1976.  Upon joining the company as a sales representative in 1992, he spent 6 months in an orientation program at the Seattle office and then returned to his permanent post in London.  He was promoted to sales manager in March 1993.  Mr. Buchanan has completed the courses 'Successful Telemarketing' and 'International Sales Management.'  He is fluent in French., ReportsTo: 2, PhotoPath: http://localhost:5656/ui/images/Employee/buchanan.jpg, EmployeeType: Commissioned, Salary:  [95000.0000000000-->] 96000, WorksForDepartmentId: 3, OnLoanDepartmentId: None, UnionId: None, Dues: None  row: 0x10dd75790  session: 0x10dfd4b60  ins_upd_dlt: upd - 2024-07-12 14:57:09,908 - logic_logger - INF
..Employee[5] {Constraint Failure: Buchanan needs a more meaningful raise} Id: 5, LastName: Buchanan, FirstName: Steven, Title: Sales Manager, TitleOfCourtesy: Mr., BirthDate: 1987-03-04, HireDate: 2025-10-17, Address: 14 Garrett Hill, City: London, Region: British Isles, PostalCode: SW1 8JR, Country: UK, HomePhone: (71) 555-4848, Extension: 3453, Notes: Steven Buchanan graduated from St. Andrews University, Scotland, with a BSC degree in 1976.  Upon joining the company as a sales representative in 1992, he spent 6 months in an orientation program at the Seattle office and then returned to his permanent post in London.  He was promoted to sales manager in March 1993.  Mr. Buchanan has completed the courses 'Successful Telemarketing' and 'International Sales Management.'  He is fluent in French., ReportsTo: 2, PhotoPath: http://localhost:5656/ui/images/Employee/buchanan.jpg, EmployeeType: Commissioned, Salary:  [95000.0000000000-->] 96000, WorksForDepartmentId: 3, OnLoanDepartmentId: None, UnionId: None, Dues: None  row: 0x10dd75790  session: 0x10dfd4b60  ins_upd_dlt: upd - 2024-07-12 14:57:09,909 - logic_logger - INF

```
</details>
  
&nbsp;
&nbsp;
## Feature: Tests Successful  
  
&nbsp;
&nbsp;
### Scenario: Run Tests
&emsp;  Scenario: Run Tests  
&emsp;&emsp;    Given Database and Set of Tests  
&emsp;&emsp;    When Run Configuration: Behave Tests  
&emsp;&emsp;    Then No Errors  
  
&nbsp;&nbsp;  
Completed at July 12, 2024 14:57:0  