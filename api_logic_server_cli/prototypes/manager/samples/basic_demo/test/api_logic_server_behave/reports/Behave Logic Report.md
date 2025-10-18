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
```
**Logic Log** in Scenario: Transaction Processing
```

The following rules have been activate
 - 2025-10-17 20:02:27,797 - logic_logger - DEBU
Rule Bank[0x10a632cf0] (loaded 2025-10-17 20:00:14.506411
Mapped Class[Customer] rules
  Constraint Function: None
  Constraint Function: None
  Derive <class 'database.models.Customer'>.balance as Sum(Order.amount_total Where Rule.sum(derive=Customer.balance, as_sum_of=Order.amount_total, where=lambda row: row.date_shipped is None) - <function declare_logic.<locals>.<lambda> at 0x10a750ea0>
Mapped Class[SysEmail] rules
  RowEvent SysEmail.send_mail()
Mapped Class[Order] rules
  Derive <class 'database.models.Order'>.amount_total as Sum(Item.amount Where  - None
  RowEvent Order.send_row_to_kafka()
Mapped Class[Item] rules
  Derive <class 'database.models.Item'>.amount as Formula (1): Rule.formula(derive=Item.amount, as_expression=la [...
  Derive <class 'database.models.Item'>.unit_price as Copy(product.unit_price
Logic Bank - 13 rules loaded - 2025-10-17 20:02:27,798 - logic_logger - INF
Logic Bank - 13 rules loaded - 2025-10-17 20:02:27,798 - logic_logger - INF

Logic Phase:		ROW LOGIC		(session=0x10b6825d0) (sqlalchemy before_flush)			 - 2025-10-17 20:02:27,802 - logic_logger - INF
..Customer[None] {Insert - client} id: None, name: Test Customer 1760756547799, balance: None, credit_limit: 1000, email: None, email_opt_out: False  row: 0x10b708d50  session: 0x10b6825d0  ins_upd_dlt: ins, initial: ins - 2025-10-17 20:02:27,803 - logic_logger - INF
..Customer[None] {server aggregate_defaults: balance } id: None, name: Test Customer 1760756547799, balance: 0, credit_limit: 1000, email: None, email_opt_out: False  row: 0x10b708d50  session: 0x10b6825d0  ins_upd_dlt: ins, initial: ins - 2025-10-17 20:02:27,803 - logic_logger - INF
Logic Phase:		COMMIT LOGIC		(session=0x10b6825d0)   										 - 2025-10-17 20:02:27,803 - logic_logger - INF
Logic Phase:		AFTER_FLUSH LOGIC	(session=0x10b6825d0)   										 - 2025-10-17 20:02:27,804 - logic_logger - INF

```
</details>
  
&nbsp;
&nbsp;
## Feature: Check Credit  
  
&nbsp;
&nbsp;
### Scenario: Good Order Placed
&emsp;  Scenario: Good Order Placed  
&emsp;&emsp;    Given Customer with balance 0 and credit 1000  
&emsp;&emsp;    When Good Order Placed  
&emsp;&emsp;    Then Balance is 50  
&emsp;&emsp;    Then Customer balance does not exceed credit limit  
<details markdown>
<summary>Tests - and their logic - are transparent.. click to see Logic</summary>


&nbsp;
&nbsp;


**Logic Doc** for scenario: Good Order Placed
   
Place an order with quantity that fits within credit limit.

This tests the complete dependency chain:
- Item.unit_price copied from Product.unit_price (Rule.copy)
- Item.amount = quantity * unit_price (Rule.formula)
- Order.amount_total = Sum(Item.amount) (Rule.sum)
- Customer.balance = Sum(Order.amount_total where not shipped) (Rule.sum with WHERE)
- Customer.balance <= credit_limit (Rule.constraint)

> **Key Takeaway:** One transaction triggers multiple chained rules automatically


&nbsp;
&nbsp;


**Rules Used** in Scenario: Good Order Placed
```
  Customer  
    1. Derive <class 'database.models.Customer'>.balance as Sum(Order.amount_total Where Rule.sum(derive=Customer.balance, as_sum_of=Order.amount_total, where=lambda row: row.date_shipped is None) - <function declare_logic.<locals>.<lambda> at 0x10a750ea0>)  
  Item  
    2. Derive <class 'database.models.Item'>.amount as Formula (1): Rule.formula(derive=Item.amount, as_expression=la [...]  
    3. Derive <class 'database.models.Item'>.unit_price as Copy(product.unit_price)  
  Order  
    4. Derive <class 'database.models.Order'>.amount_total as Sum(Item.amount Where  - None)  
    5. RowEvent Order.send_row_to_kafka()   
```
**Logic Log** in Scenario: Good Order Placed
```

Good Order Place
 - 2025-10-17 20:02:27,808 - logic_logger - INF

Logic Phase:		ROW LOGIC		(session=0x10b681450) (sqlalchemy before_flush)			 - 2025-10-17 20:02:27,810 - logic_logger - INF
..Product[None] {Insert - client} id: None, name: Widget, unit_price: 5  row: 0x10b03a970  session: 0x10b681450  ins_upd_dlt: ins, initial: ins - 2025-10-17 20:02:27,810 - logic_logger - INF
Logic Phase:		COMMIT LOGIC		(session=0x10b681450)   										 - 2025-10-17 20:02:27,810 - logic_logger - INF
Logic Phase:		AFTER_FLUSH LOGIC	(session=0x10b681450)   										 - 2025-10-17 20:02:27,811 - logic_logger - INF

```
</details>
  
&nbsp;
&nbsp;
### Scenario: Bad Order Exceeds Credit
&emsp;  Scenario: Bad Order Exceeds Credit  
&emsp;&emsp;    Given Customer with balance 900 and credit 1000  
&emsp;&emsp;    When Order Placed with quantity 200  
&emsp;&emsp;    Then Error raised containing "balance"  
&emsp;&emsp;    Then Error raised containing "credit limit"  
<details markdown>
<summary>Tests - and their logic - are transparent.. click to see Logic</summary>


&nbsp;
&nbsp;


**Logic Doc** for scenario: Bad Order Exceeds Credit
   
Attempt to place order that exceeds credit limit.

This tests the constraint rule:
- Customer.balance would exceed credit_limit
- Transaction should be rejected

> **Key Takeaway:** Constraints prevent invalid data automatically


&nbsp;
&nbsp;


**Rules Used** in Scenario: Bad Order Exceeds Credit
```
  Customer  
    1. Derive <class 'database.models.Customer'>.balance as Sum(Order.amount_total Where Rule.sum(derive=Customer.balance, as_sum_of=Order.amount_total, where=lambda row: row.date_shipped is None) - <function declare_logic.<locals>.<lambda> at 0x10a750ea0>)  
  Item  
    2. Derive <class 'database.models.Item'>.amount as Formula (1): Rule.formula(derive=Item.amount, as_expression=la [...]  
    3. Derive <class 'database.models.Item'>.unit_price as Copy(product.unit_price)  
  Order  
    4. Derive <class 'database.models.Order'>.amount_total as Sum(Item.amount Where  - None)  
    5. RowEvent Order.send_row_to_kafka()   
```
**Logic Log** in Scenario: Bad Order Exceeds Credit
```

Bad Order Exceeds Credi
 - 2025-10-17 20:02:27,851 - logic_logger - INF

Logic Phase:		ROW LOGIC		(session=0x10b0a48d0) (sqlalchemy before_flush)			 - 2025-10-17 20:02:27,852 - logic_logger - INF
..Product[None] {Insert - client} id: None, name: Expensive Widget, unit_price: 1  row: 0x10b03acf0  session: 0x10b0a48d0  ins_upd_dlt: ins, initial: ins - 2025-10-17 20:02:27,853 - logic_logger - INF
Logic Phase:		COMMIT LOGIC		(session=0x10b0a48d0)   										 - 2025-10-17 20:02:27,853 - logic_logger - INF
Logic Phase:		AFTER_FLUSH LOGIC	(session=0x10b0a48d0)   										 - 2025-10-17 20:02:27,853 - logic_logger - INF

```
</details>
  
&nbsp;
&nbsp;
### Scenario: Alter Item Quantity to Exceed Credit
&emsp;  Scenario: Alter Item Quantity to Exceed Credit  
&emsp;&emsp;    Given Customer with balance 0 and credit 1000  
    And Order with 1 item quantity 10  
&emsp;&emsp;    When Item quantity changed to 1500  
&emsp;&emsp;    Then Error raised containing "balance"  
&emsp;&emsp;    Then Error raised containing "credit limit"  
<details markdown>
<summary>Tests - and their logic - are transparent.. click to see Logic</summary>


&nbsp;
&nbsp;


**Logic Doc** for scenario: Alter Item Quantity to Exceed Credit
   
Alter existing item quantity to exceed credit limit.

This tests:
- PATCH operation triggers recalculation
- Constraint checked on update (not just insert)

> **Key Takeaway:** Rules enforce constraints on all operations


&nbsp;
&nbsp;


**Rules Used** in Scenario: Alter Item Quantity to Exceed Credit
```
  Customer  
    1. Derive <class 'database.models.Customer'>.balance as Sum(Order.amount_total Where Rule.sum(derive=Customer.balance, as_sum_of=Order.amount_total, where=lambda row: row.date_shipped is None) - <function declare_logic.<locals>.<lambda> at 0x10a750ea0>)  
  Item  
    2. Derive <class 'database.models.Item'>.amount as Formula (1): Rule.formula(derive=Item.amount, as_expression=la [...]  
    3. Derive <class 'database.models.Item'>.unit_price as Copy(product.unit_price)  
  Order  
    4. Derive <class 'database.models.Order'>.amount_total as Sum(Item.amount Where  - None)  
    5. RowEvent Order.send_row_to_kafka()   
```
**Logic Log** in Scenario: Alter Item Quantity to Exceed Credit
```

Alter Item Quantity to Exceed Credi
 - 2025-10-17 20:02:27,884 - logic_logger - INF

Logic Phase:		ROW LOGIC		(session=0x10b71a470) (sqlalchemy before_flush)			 - 2025-10-17 20:02:27,885 - logic_logger - INF
..Item[8] {Update - client} id: 8, order_id: 9, product_id: 9, quantity:  [10-->] 1500, amount: 50.0000000000, unit_price: 5.0000000000  row: 0x10b893a50  session: 0x10b71a470  ins_upd_dlt: upd, initial: upd - 2025-10-17 20:02:27,886 - logic_logger - INF
..Item[8] {Formula amount} id: 8, order_id: 9, product_id: 9, quantity:  [10-->] 1500, amount:  [50.0000000000-->] 7500.0000000000, unit_price: 5.0000000000  row: 0x10b893a50  session: 0x10b71a470  ins_upd_dlt: upd, initial: upd - 2025-10-17 20:02:27,886 - logic_logger - INF
....Order[9] {Update - Adjusting order: amount_total} id: 9, notes: Test order, customer_id: 8, CreatedOn: 2025-10-17, date_shipped: None, amount_total:  [50.0000000000-->] 7500.0000000000  row: 0x10b8b8550  session: 0x10b71a470  ins_upd_dlt: upd, initial: upd - 2025-10-17 20:02:27,886 - logic_logger - INF
......Customer[8] {Update - Adjusting customer: balance} id: 8, name: Test Customer 1760756547867, balance:  [50.0000000000-->] 7500.0000000000, credit_limit: 1000.0000000000, email: None, email_opt_out: False  row: 0x10b8b9150  session: 0x10b71a470  ins_upd_dlt: upd, initial: upd - 2025-10-17 20:02:27,887 - logic_logger - INF
......Customer[8] {Constraint Failure: Customer balance (7500.0000000000) exceeds credit limit (1000.0000000000)} id: 8, name: Test Customer 1760756547867, balance:  [50.0000000000-->] 7500.0000000000, credit_limit: 1000.0000000000, email: None, email_opt_out: False  row: 0x10b8b9150  session: 0x10b71a470  ins_upd_dlt: upd, initial: upd - 2025-10-17 20:02:27,887 - logic_logger - INF

```
</details>
  
&nbsp;
&nbsp;
### Scenario: Change Product on Item
&emsp;  Scenario: Change Product on Item  
&emsp;&emsp;    Given Customer with balance 0 and credit 1000  
    And Order with 1 item quantity 10  
&emsp;&emsp;    When Item product changed to expensive product  
&emsp;&emsp;    Then Balance recalculates with new price  
&emsp;&emsp;    Then Item unit_price updated from new product  
<details markdown>
<summary>Tests - and their logic - are transparent.. click to see Logic</summary>


&nbsp;
&nbsp;


**Logic Doc** for scenario: Change Product on Item
   
Change product_id on item to test copy rule re-execution.

This tests:
- Item.unit_price re-copies from new Product
- Item.amount recalculates with new unit_price
- Order.amount_total updates
- Customer.balance updates

> **Key Takeaway:** Foreign key changes trigger complete rule chain


&nbsp;
&nbsp;


**Rules Used** in Scenario: Change Product on Item
```
  Customer  
    1. Derive <class 'database.models.Customer'>.balance as Sum(Order.amount_total Where Rule.sum(derive=Customer.balance, as_sum_of=Order.amount_total, where=lambda row: row.date_shipped is None) - <function declare_logic.<locals>.<lambda> at 0x10a750ea0>)  
  Item  
    2. Derive <class 'database.models.Item'>.amount as Formula (1): Rule.formula(derive=Item.amount, as_expression=la [...]  
    3. Derive <class 'database.models.Item'>.unit_price as Copy(product.unit_price)  
  Order  
    4. Derive <class 'database.models.Order'>.amount_total as Sum(Item.amount Where  - None)  
    5. RowEvent Order.send_row_to_kafka()   
```
**Logic Log** in Scenario: Change Product on Item
```

Change Product on Ite
 - 2025-10-17 20:02:27,907 - logic_logger - INF

Logic Phase:		ROW LOGIC		(session=0x10b719e10) (sqlalchemy before_flush)			 - 2025-10-17 20:02:27,908 - logic_logger - INF
..Product[None] {Insert - client} id: None, name: Expensive Product, unit_price: 15  row: 0x10b88f930  session: 0x10b719e10  ins_upd_dlt: ins, initial: ins - 2025-10-17 20:02:27,908 - logic_logger - INF
Logic Phase:		COMMIT LOGIC		(session=0x10b719e10)   										 - 2025-10-17 20:02:27,908 - logic_logger - INF
Logic Phase:		AFTER_FLUSH LOGIC	(session=0x10b719e10)   										 - 2025-10-17 20:02:27,908 - logic_logger - INF

```
</details>
  
&nbsp;
&nbsp;
### Scenario: Change Customer on Order
&emsp;  Scenario: Change Customer on Order  
&emsp;&emsp;    Given Two customers with balance 0  
    And Order for first customer with balance 100  
&emsp;&emsp;    When Order moved to second customer  
&emsp;&emsp;    Then First customer balance is 0  
&emsp;&emsp;    Then Second customer balance is 100  
<details markdown>
<summary>Tests - and their logic - are transparent.. click to see Logic</summary>


&nbsp;
&nbsp;


**Logic Doc** for scenario: Change Customer on Order
   
Change customer_id on order to test both parent adjustments.

This tests THE CRITICAL BUG that procedural code misses:
- Original customer balance decreases
- New customer balance increases
- Rules engine handles BOTH automatically

> **Key Takeaway:** Declarative rules adjust both old and new parents


&nbsp;
&nbsp;


**Rules Used** in Scenario: Change Customer on Order
```
  Customer  
    1. Derive <class 'database.models.Customer'>.balance as Sum(Order.amount_total Where Rule.sum(derive=Customer.balance, as_sum_of=Order.amount_total, where=lambda row: row.date_shipped is None) - <function declare_logic.<locals>.<lambda> at 0x10a750ea0>)  
  Item  
    2. Derive <class 'database.models.Item'>.amount as Formula (1): Rule.formula(derive=Item.amount, as_expression=la [...]  
    3. Derive <class 'database.models.Item'>.unit_price as Copy(product.unit_price)  
  Order  
    4. Derive <class 'database.models.Order'>.amount_total as Sum(Item.amount Where  - None)  
    5. RowEvent Order.send_row_to_kafka()   
```
**Logic Log** in Scenario: Change Customer on Order
```

Change Customer on Orde
 - 2025-10-17 20:02:27,938 - logic_logger - INF

Logic Phase:		ROW LOGIC		(session=0x10b71a690) (sqlalchemy before_flush)			 - 2025-10-17 20:02:27,939 - logic_logger - INF
..Order[11] {Update - client} id: 11, notes: Order to transfer, customer_id:  [10-->] 11, CreatedOn: 2025-10-17, date_shipped: None, amount_total: 100.0000000000  row: 0x10b8932d0  session: 0x10b71a690  ins_upd_dlt: upd, initial: upd - 2025-10-17 20:02:27,939 - logic_logger - INF
....Customer[11] {Update - Adjusting customer: balance, balance} id: 11, name: Test Customer 2 1760756547919, balance:  [0E-10-->] 100.0000000000, credit_limit: 1000.0000000000, email: None, email_opt_out: False  row: 0x10b76ab50  session: 0x10b71a690  ins_upd_dlt: upd, initial: upd - 2025-10-17 20:02:27,940 - logic_logger - INF
....Customer[10] {Update - Adjusting Old customer} id: 10, name: Test Customer 1 1760756547919, balance:  [100.0000000000-->] 0E-10, credit_limit: 1000.0000000000, email: None, email_opt_out: False  row: 0x10b7699d0  session: 0x10b71a690  ins_upd_dlt: upd, initial: upd - 2025-10-17 20:02:27,940 - logic_logger - INF
Logic Phase:		COMMIT LOGIC		(session=0x10b71a690)   										 - 2025-10-17 20:02:27,940 - logic_logger - INF
Logic Phase:		AFTER_FLUSH LOGIC	(session=0x10b71a690)   										 - 2025-10-17 20:02:27,941 - logic_logger - INF
..Order[11] {AfterFlush Event} id: 11, notes: Order to transfer, customer_id:  [10-->] 11, CreatedOn: 2025-10-17, date_shipped: None, amount_total: 100.0000000000  row: 0x10b8932d0  session: 0x10b71a690  ins_upd_dlt: upd, initial: upd - 2025-10-17 20:02:27,941 - logic_logger - INF
..Order[11] {Sending Order to Kafka topic 'order_shipping' [Note: **Kafka not enabled** ]} id: 11, notes: Order to transfer, customer_id:  [10-->] 11, CreatedOn: 2025-10-17, date_shipped: None, amount_total: 100.0000000000  row: 0x10b8932d0  session: 0x10b71a690  ins_upd_dlt: upd, initial: upd - 2025-10-17 20:02:27,941 - logic_logger - INF

```
</details>
  
&nbsp;
&nbsp;
### Scenario: Delete Item Adjusts Balance
&emsp;  Scenario: Delete Item Adjusts Balance  
&emsp;&emsp;    Given Customer with balance 0 and credit 1000  
    And Order with 2 items  
&emsp;&emsp;    When One item is deleted  
&emsp;&emsp;    Then Balance decreases correctly  
<details markdown>
<summary>Tests - and their logic - are transparent.. click to see Logic</summary>


&nbsp;
&nbsp;


**Logic Doc** for scenario: Delete Item Adjusts Balance
   
Delete item to test aggregate adjustment downward.

This tests DELETE operation (often forgotten):
- Item deleted
- Order.amount_total decreases
- Customer.balance decreases

> **Key Takeaway:** DELETE operations adjust aggregates downward automatically


&nbsp;
&nbsp;


**Rules Used** in Scenario: Delete Item Adjusts Balance
```
  Customer  
    1. Derive <class 'database.models.Customer'>.balance as Sum(Order.amount_total Where Rule.sum(derive=Customer.balance, as_sum_of=Order.amount_total, where=lambda row: row.date_shipped is None) - <function declare_logic.<locals>.<lambda> at 0x10a750ea0>)  
  Item  
    2. Derive <class 'database.models.Item'>.amount as Formula (1): Rule.formula(derive=Item.amount, as_expression=la [...]  
    3. Derive <class 'database.models.Item'>.unit_price as Copy(product.unit_price)  
  Order  
    4. Derive <class 'database.models.Order'>.amount_total as Sum(Item.amount Where  - None)  
    5. RowEvent Order.send_row_to_kafka()   
```
**Logic Log** in Scenario: Delete Item Adjusts Balance
```

Delete Item Adjusts Balanc
 - 2025-10-17 20:02:27,970 - logic_logger - INF

Logic Phase:		ROW LOGIC		(session=0x10b0a48d0) (sqlalchemy before_flush)			 - 2025-10-17 20:02:27,971 - logic_logger - INF
..Item[11] {Delete - client} id: 11, order_id: 12, product_id: 13, quantity: 5, amount: 50.0000000000, unit_price: 10.0000000000  row: 0x10b76a7d0  session: 0x10b0a48d0  ins_upd_dlt: dlt, initial: dlt - 2025-10-17 20:02:27,971 - logic_logger - INF
....Order[12] {Update - Adjusting order: amount_total} id: 12, notes: Order with 2 items, customer_id: 12, CreatedOn: 2025-10-17, date_shipped: None, amount_total:  [110.0000000000-->] 60.0000000000  row: 0x10b8b9550  session: 0x10b0a48d0  ins_upd_dlt: upd, initial: upd - 2025-10-17 20:02:27,972 - logic_logger - INF
......Customer[12] {Update - Adjusting customer: balance} id: 12, name: Test Customer 1760756547946, balance:  [110.0000000000-->] 60.0000000000, credit_limit: 1000.0000000000, email: None, email_opt_out: False  row: 0x10b8b82d0  session: 0x10b0a48d0  ins_upd_dlt: upd, initial: upd - 2025-10-17 20:02:27,972 - logic_logger - INF
Logic Phase:		COMMIT LOGIC		(session=0x10b0a48d0)   										 - 2025-10-17 20:02:27,972 - logic_logger - INF
Logic Phase:		AFTER_FLUSH LOGIC	(session=0x10b0a48d0)   										 - 2025-10-17 20:02:27,973 - logic_logger - INF
....Order[12] {AfterFlush Event} id: 12, notes: Order with 2 items, customer_id: 12, CreatedOn: 2025-10-17, date_shipped: None, amount_total:  [110.0000000000-->] 60.0000000000  row: 0x10b8b9550  session: 0x10b0a48d0  ins_upd_dlt: upd, initial: upd - 2025-10-17 20:02:27,973 - logic_logger - INF
....Order[12] {Sending Order to Kafka topic 'order_shipping' [Note: **Kafka not enabled** ]} id: 12, notes: Order with 2 items, customer_id: 12, CreatedOn: 2025-10-17, date_shipped: None, amount_total:  [110.0000000000-->] 60.0000000000  row: 0x10b8b9550  session: 0x10b0a48d0  ins_upd_dlt: upd, initial: upd - 2025-10-17 20:02:27,973 - logic_logger - INF

```
</details>
  
&nbsp;
&nbsp;
## Feature: Order Lifecycle  
  
&nbsp;
&nbsp;
### Scenario: Set Order Shipped Excludes from Balance
&emsp;  Scenario: Set Order Shipped Excludes from Balance  
&emsp;&emsp;    Given Customer with balance 0 and credit 1000  
    And Order with balance 100  
&emsp;&emsp;    When Order is shipped  
&emsp;&emsp;    Then Balance is 0  
&emsp;&emsp;    Then Order excluded from balance aggregate  
<details markdown>
<summary>Tests - and their logic - are transparent.. click to see Logic</summary>


&nbsp;
&nbsp;


**Logic Doc** for scenario: Set Order Shipped Excludes from Balance
   
Set date_shipped on order to exclude from balance.

This tests WHERE clause exclusion:
- Before: date_shipped = None → included in Customer.balance
- After: date_shipped = today → excluded from Customer.balance

> **Key Takeaway:** WHERE clause conditions work bidirectionally


&nbsp;
&nbsp;


**Rules Used** in Scenario: Set Order Shipped Excludes from Balance
```
  Customer  
    1. Derive <class 'database.models.Customer'>.balance as Sum(Order.amount_total Where Rule.sum(derive=Customer.balance, as_sum_of=Order.amount_total, where=lambda row: row.date_shipped is None) - <function declare_logic.<locals>.<lambda> at 0x10a750ea0>)  
  Order  
    2. RowEvent Order.send_row_to_kafka()   
```
**Logic Log** in Scenario: Set Order Shipped Excludes from Balance
```

Set Order Shipped Excludes from Balanc
 - 2025-10-17 20:02:27,992 - logic_logger - INF

Logic Phase:		ROW LOGIC		(session=0x10b719040) (sqlalchemy before_flush)			 - 2025-10-17 20:02:27,994 - logic_logger - INF
..Order[13] {Update - client} id: 13, notes: Lifecycle order, customer_id: 13, CreatedOn: 2025-10-17, date_shipped:  [None-->] 2024-01-15 00:00:00, amount_total: 100.0000000000  row: 0x10b768fd0  session: 0x10b719040  ins_upd_dlt: upd, initial: upd - 2025-10-17 20:02:27,995 - logic_logger - INF
....Customer[13] {Update - Adjusting customer: balance} id: 13, name: Test Customer 1760756547976, balance:  [100.0000000000-->] 0E-10, credit_limit: 1000.0000000000, email: None, email_opt_out: False  row: 0x10b8b9750  session: 0x10b719040  ins_upd_dlt: upd, initial: upd - 2025-10-17 20:02:27,995 - logic_logger - INF
Logic Phase:		COMMIT LOGIC		(session=0x10b719040)   										 - 2025-10-17 20:02:27,995 - logic_logger - INF
Logic Phase:		AFTER_FLUSH LOGIC	(session=0x10b719040)   										 - 2025-10-17 20:02:27,996 - logic_logger - INF
..Order[13] {AfterFlush Event} id: 13, notes: Lifecycle order, customer_id: 13, CreatedOn: 2025-10-17, date_shipped:  [None-->] 2024-01-15 00:00:00, amount_total: 100.0000000000  row: 0x10b768fd0  session: 0x10b719040  ins_upd_dlt: upd, initial: upd - 2025-10-17 20:02:27,996 - logic_logger - INF
..Order[13] {Sending Order to Kafka topic 'order_shipping' [Note: **Kafka not enabled** ]} id: 13, notes: Lifecycle order, customer_id: 13, CreatedOn: 2025-10-17, date_shipped:  [None-->] 2024-01-15 00:00:00, amount_total: 100.0000000000  row: 0x10b768fd0  session: 0x10b719040  ins_upd_dlt: upd, initial: upd - 2025-10-17 20:02:27,996 - logic_logger - INF

```
</details>
  
&nbsp;
&nbsp;
### Scenario: Reset Shipped Includes in Balance
&emsp;  Scenario: Reset Shipped Includes in Balance  
&emsp;&emsp;    Given Customer with balance 0 and credit 1000  
    And Order with balance 100 marked shipped  
&emsp;&emsp;    When Order unshipped  
&emsp;&emsp;    Then Balance is 100  
&emsp;&emsp;    Then Order included in balance aggregate  
<details markdown>
<summary>Tests - and their logic - are transparent.. click to see Logic</summary>


&nbsp;
&nbsp;


**Logic Doc** for scenario: Reset Shipped Includes in Balance
   
Reset date_shipped to None to include order in balance.

This tests WHERE clause inclusion (reverse direction):
- Before: date_shipped = "2024-01-15" → excluded from balance
- After: date_shipped = None → included in balance

> **Key Takeaway:** WHERE clauses work both directions (not just one-way)


&nbsp;
&nbsp;


**Rules Used** in Scenario: Reset Shipped Includes in Balance
```
  Customer  
    1. Derive <class 'database.models.Customer'>.balance as Sum(Order.amount_total Where Rule.sum(derive=Customer.balance, as_sum_of=Order.amount_total, where=lambda row: row.date_shipped is None) - <function declare_logic.<locals>.<lambda> at 0x10a750ea0>)  
  Item  
    2. Derive <class 'database.models.Item'>.amount as Formula (1): Rule.formula(derive=Item.amount, as_expression=la [...]  
    3. Derive <class 'database.models.Item'>.unit_price as Copy(product.unit_price)  
  Order  
    4. Derive <class 'database.models.Order'>.amount_total as Sum(Item.amount Where  - None)  
    5. RowEvent Order.send_row_to_kafka()   
```
**Logic Log** in Scenario: Reset Shipped Includes in Balance
```

Reset Shipped Includes in Balanc
 - 2025-10-17 20:02:28,020 - logic_logger - INF

Logic Phase:		ROW LOGIC		(session=0x10b71a580) (sqlalchemy before_flush)			 - 2025-10-17 20:02:28,022 - logic_logger - INF
..Order[14] {Update - client} id: 14, notes: Shipped order, customer_id: 14, CreatedOn: 2025-10-17, date_shipped:  [2024-01-15-->] None, amount_total: 100.0000000000  row: 0x10b8b8650  session: 0x10b71a580  ins_upd_dlt: upd, initial: upd - 2025-10-17 20:02:28,022 - logic_logger - INF
....Customer[14] {Update - Adjusting customer: balance} id: 14, name: Test Customer 1760756548001, balance:  [0E-10-->] 100.0000000000, credit_limit: 1000.0000000000, email: None, email_opt_out: False  row: 0x10b8ba150  session: 0x10b71a580  ins_upd_dlt: upd, initial: upd - 2025-10-17 20:02:28,022 - logic_logger - INF
Logic Phase:		COMMIT LOGIC		(session=0x10b71a580)   										 - 2025-10-17 20:02:28,022 - logic_logger - INF
Logic Phase:		AFTER_FLUSH LOGIC	(session=0x10b71a580)   										 - 2025-10-17 20:02:28,023 - logic_logger - INF
..Order[14] {AfterFlush Event} id: 14, notes: Shipped order, customer_id: 14, CreatedOn: 2025-10-17, date_shipped:  [2024-01-15-->] None, amount_total: 100.0000000000  row: 0x10b8b8650  session: 0x10b71a580  ins_upd_dlt: upd, initial: upd - 2025-10-17 20:02:28,023 - logic_logger - INF
..Order[14] {Sending Order to Kafka topic 'order_shipping' [Note: **Kafka not enabled** ]} id: 14, notes: Shipped order, customer_id: 14, CreatedOn: 2025-10-17, date_shipped:  [2024-01-15-->] None, amount_total: 100.0000000000  row: 0x10b8b8650  session: 0x10b71a580  ins_upd_dlt: upd, initial: upd - 2025-10-17 20:02:28,023 - logic_logger - INF

```
</details>
  
&nbsp;
&nbsp;
### Scenario: Delete Order Adjusts Balance
&emsp;  Scenario: Delete Order Adjusts Balance  
&emsp;&emsp;    Given Customer with balance 0 and credit 1000  
    And Order with balance 150  
&emsp;&emsp;    When Order is deleted  
&emsp;&emsp;    Then Balance is 0  
&emsp;&emsp;    Then Customer has no orders  
<details markdown>
<summary>Tests - and their logic - are transparent.. click to see Logic</summary>


&nbsp;
&nbsp;


**Logic Doc** for scenario: Delete Order Adjusts Balance
   
Delete entire order to test aggregate adjustment.

This tests DELETE operation:
- Order deleted
- Customer.balance updated (order removed from sum)

> **Key Takeaway:** DELETE operations adjust aggregates automatically


&nbsp;
&nbsp;


**Rules Used** in Scenario: Delete Order Adjusts Balance
```
  Customer  
    1. Derive <class 'database.models.Customer'>.balance as Sum(Order.amount_total Where Rule.sum(derive=Customer.balance, as_sum_of=Order.amount_total, where=lambda row: row.date_shipped is None) - <function declare_logic.<locals>.<lambda> at 0x10a750ea0>)  
  Order  
    2. RowEvent Order.send_row_to_kafka()   
```
**Logic Log** in Scenario: Delete Order Adjusts Balance
```

Delete Order Adjusts Balanc
 - 2025-10-17 20:02:28,044 - logic_logger - INF

Logic Phase:		ROW LOGIC		(session=0x10b71a690) (sqlalchemy before_flush)			 - 2025-10-17 20:02:28,045 - logic_logger - INF
..Order[15] {Delete - client} id: 15, notes: Lifecycle order, customer_id: 15, CreatedOn: 2025-10-17, date_shipped: None, amount_total: 150.0000000000  row: 0x10b8930d0  session: 0x10b71a690  ins_upd_dlt: dlt, initial: dlt - 2025-10-17 20:02:28,045 - logic_logger - INF
....Customer[15] {Update - Adjusting customer: balance} id: 15, name: Test Customer 1760756548028, balance:  [150.0000000000-->] 0E-10, credit_limit: 1000.0000000000, email: None, email_opt_out: False  row: 0x10b7690d0  session: 0x10b71a690  ins_upd_dlt: upd, initial: upd - 2025-10-17 20:02:28,046 - logic_logger - INF
Logic Phase:		COMMIT LOGIC		(session=0x10b71a690)   										 - 2025-10-17 20:02:28,046 - logic_logger - INF
Logic Phase:		AFTER_FLUSH LOGIC	(session=0x10b71a690)   										 - 2025-10-17 20:02:28,047 - logic_logger - INF
..Order[15] {AfterFlush Event} id: 15, notes: Lifecycle order, customer_id: 15, CreatedOn: 2025-10-17, date_shipped: None, amount_total: 150.0000000000  row: 0x10b8930d0  session: 0x10b71a690  ins_upd_dlt: dlt, initial: dlt - 2025-10-17 20:02:28,047 - logic_logger - INF
..Order[15] {Sending Order to Kafka topic 'order_shipping' [Note: **Kafka not enabled** ]} id: 15, notes: Lifecycle order, customer_id: 15, CreatedOn: 2025-10-17, date_shipped: None, amount_total: 150.0000000000  row: 0x10b8930d0  session: 0x10b71a690  ins_upd_dlt: dlt, initial: dlt - 2025-10-17 20:02:28,047 - logic_logger - INF

```
</details>
  
&nbsp;&nbsp;  
/Users/val/dev/ApiLogicServer/ApiLogicServer-dev/build_and_test/ApiLogicServer/basic_demo/test/api_logic_server_behave/behave_run.py completed at October 17, 2025 20:02:2  