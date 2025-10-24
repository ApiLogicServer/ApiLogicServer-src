## Basic Demo Sample

This is a basic demonstration project created from a simple natural language prompt using API Logic Server's GenAI capabilities.

### Data Model

![Basic Demo Data Model](https://apilogicserver.github.io/Docs/images/basic_demo/basic_demo_data_model.jpeg)

### Creation Prompt

This project was created from the following natural language prompt:

```
Create a system with customers, orders, items and products.

Include a notes field for orders.

Use case: Check Credit    
    1. The Customer's balance is less than the credit limit
    2. The Customer's balance is the sum of the Order amount_total where date_shipped is null
    3. The Order's amount_total is the sum of the Item amount
    4. The Item amount is the quantity * unit_price
    5. The Item unit_price is copied from the Product unit_price

Use case: App Integration
    1. Send the Order to Kafka topic 'order_shipping' if the date_shipped is not None.
```

The sample Scenarios below were chosen to illustrate the basic patterns of using rules. Open the disclosure box ("Tests - and their logic...") to see the implementation and notes.

The following report was created during test suite execution.

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
 - 2025-10-24 08:44:43,762 - logic_logger - DEBU
Rule Bank[0x10927aba0] (loaded 2025-10-22 20:22:19.960861
Mapped Class[Customer] rules
  Constraint Function: None
  Constraint Function: None
  Derive <class 'database.models.Customer'>.balance as Sum(Order.amount_total Where Rule.sum(derive=Customer.balance, as_sum_of=Order.amount_total, where=lambda row: row.date_shipped is None) - <function declare_logic.<locals>.<lambda> at 0x109355260>
Mapped Class[SysEmail] rules
  RowEvent SysEmail.send_mail()
Mapped Class[Order] rules
  Derive <class 'database.models.Order'>.amount_total as Sum(Item.amount Where  - None
  RowEvent Order.send_order_to_shipping()
Mapped Class[Item] rules
  Derive <class 'database.models.Item'>.amount as Formula (1): <function
  Derive <class 'database.models.Item'>.unit_price as Copy(product.unit_price
Logic Bank - 13 rules loaded - 2025-10-24 08:44:43,771 - logic_logger - INF
Logic Bank - 13 rules loaded - 2025-10-24 08:44:43,771 - logic_logger - INF

Logic Phase:		ROW LOGIC		(session=0x10a3778a0) (sqlalchemy before_flush)			 - 2025-10-24 08:44:43,794 - logic_logger - INF
..Customer[None] {Insert - client} id: None, name: Alice 1761320683776, balance: 0, credit_limit: 5000, email: None, email_opt_out: None  row: 0x10a56d050  session: 0x10a3778a0  ins_upd_dlt: ins, initial: ins - 2025-10-24 08:44:43,796 - logic_logger - INF
..Customer[None] {server aggregate_defaults: balance } id: None, name: Alice 1761320683776, balance: 0, credit_limit: 5000, email: None, email_opt_out: None  row: 0x10a56d050  session: 0x10a3778a0  ins_upd_dlt: ins, initial: ins - 2025-10-24 08:44:43,796 - logic_logger - INF
Logic Phase:		COMMIT LOGIC		(session=0x10a3778a0)   										 - 2025-10-24 08:44:43,796 - logic_logger - INF
Logic Phase:		AFTER_FLUSH LOGIC	(session=0x10a3778a0)   										 - 2025-10-24 08:44:43,803 - logic_logger - INF

```
</details>
  
&nbsp;
&nbsp;
## Feature: Order Processing with Business Logic  
  
&nbsp;
&nbsp;
### Scenario: Good Order Placed via B2B API
&emsp;  Scenario: Good Order Placed via B2B API  
&emsp;&emsp;    Given Customer "Alice" with balance 0 and credit limit 5000  
&emsp;&emsp;    When B2B order placed for "Alice" with 5 Widget  
&emsp;&emsp;    Then Customer balance should be 450  
    And Order amount_total should be 450  
    And Item amount should be 450  
    And Item unit_price should be 90  
<details markdown>
<summary>Tests - and their logic - are transparent.. click to see Logic</summary>


&nbsp;
&nbsp;


**Rules Used** in Scenario: Good Order Placed via B2B API
```
  Customer  
    1. Derive <class 'database.models.Customer'>.balance as Sum(Order.amount_total Where Rule.sum(derive=Customer.balance, as_sum_of=Order.amount_total, where=lambda row: row.date_shipped is None) - <function declare_logic.<locals>.<lambda> at 0x109355260>)  
  Item  
    2. Derive <class 'database.models.Item'>.unit_price as Copy(product.unit_price)  
    3. Derive <class 'database.models.Item'>.amount as Formula (1): <function>  
  Order  
    4. Derive <class 'database.models.Order'>.amount_total as Sum(Item.amount Where  - None)  
    5. RowEvent Order.send_order_to_shipping()   
```
**Logic Log** in Scenario: Good Order Placed via B2B API
```

Good Order Placed via B2B AP
 - 2025-10-24 08:44:43,812 - logic_logger - INF

Logic Phase:		ROW LOGIC		(session=0x10a377ac0) (sqlalchemy before_flush)			 - 2025-10-24 08:44:43,816 - logic_logger - INF
..Customer[28] {Update - client} id: 28, name: Alice 1761320683776, balance: 0E-10, credit_limit: 5000.0000000000, email: None, email_opt_out: None  row: 0x10a56d4d0  session: 0x10a377ac0  ins_upd_dlt: upd, initial: upd - 2025-10-24 08:44:43,817 - logic_logger - INF
Logic Phase:		COMMIT LOGIC		(session=0x10a377ac0)   										 - 2025-10-24 08:44:43,817 - logic_logger - INF
Logic Phase:		AFTER_FLUSH LOGIC	(session=0x10a377ac0)   										 - 2025-10-24 08:44:43,817 - logic_logger - INF

```
</details>
  
&nbsp;
&nbsp;
### Scenario: Multi-Item Order via B2B API
&emsp;  Scenario: Multi-Item Order via B2B API  
&emsp;&emsp;    Given Customer "Bob" with balance 0 and credit limit 3000  
&emsp;&emsp;    When B2B order placed for "Bob" with 3 Widget and 2 Gadget  
&emsp;&emsp;    Then Customer balance should be 570  
    And Order amount_total should be 570  
<details markdown>
<summary>Tests - and their logic - are transparent.. click to see Logic</summary>


&nbsp;
&nbsp;


**Rules Used** in Scenario: Multi-Item Order via B2B API
```
  Customer  
    1. Derive <class 'database.models.Customer'>.balance as Sum(Order.amount_total Where Rule.sum(derive=Customer.balance, as_sum_of=Order.amount_total, where=lambda row: row.date_shipped is None) - <function declare_logic.<locals>.<lambda> at 0x109355260>)  
  Item  
    2. Derive <class 'database.models.Item'>.unit_price as Copy(product.unit_price)  
    3. Derive <class 'database.models.Item'>.amount as Formula (1): <function>  
  Order  
    4. Derive <class 'database.models.Order'>.amount_total as Sum(Item.amount Where  - None)  
    5. RowEvent Order.send_order_to_shipping()   
```
**Logic Log** in Scenario: Multi-Item Order via B2B API
```

Multi-Item Order via B2B AP
 - 2025-10-24 08:44:43,839 - logic_logger - INF

Logic Phase:		ROW LOGIC		(session=0x10a574e20) (sqlalchemy before_flush)			 - 2025-10-24 08:44:43,841 - logic_logger - INF
..Customer[29] {Update - client} id: 29, name: Bob 1761320683835, balance: 0E-10, credit_limit: 3000.0000000000, email: None, email_opt_out: None  row: 0x10a56c850  session: 0x10a574e20  ins_upd_dlt: upd, initial: upd - 2025-10-24 08:44:43,841 - logic_logger - INF
Logic Phase:		COMMIT LOGIC		(session=0x10a574e20)   										 - 2025-10-24 08:44:43,841 - logic_logger - INF
Logic Phase:		AFTER_FLUSH LOGIC	(session=0x10a574e20)   										 - 2025-10-24 08:44:43,842 - logic_logger - INF

```
</details>
  
&nbsp;
&nbsp;
### Scenario: Carbon Neutral Discount Applied
&emsp;  Scenario: Carbon Neutral Discount Applied  
&emsp;&emsp;    Given Customer "Diana" with balance 0 and credit limit 5000  
&emsp;&emsp;    When B2B order placed for "Diana" with 10 carbon neutral Gadget  
&emsp;&emsp;    Then Customer balance should be 1350  
    And Item amount should be 1350  
<details markdown>
<summary>Tests - and their logic - are transparent.. click to see Logic</summary>


&nbsp;
&nbsp;


**Rules Used** in Scenario: Carbon Neutral Discount Applied
```
  Customer  
    1. Derive <class 'database.models.Customer'>.balance as Sum(Order.amount_total Where Rule.sum(derive=Customer.balance, as_sum_of=Order.amount_total, where=lambda row: row.date_shipped is None) - <function declare_logic.<locals>.<lambda> at 0x109355260>)  
  Item  
    2. Derive <class 'database.models.Item'>.unit_price as Copy(product.unit_price)  
    3. Derive <class 'database.models.Item'>.amount as Formula (1): <function>  
  Order  
    4. Derive <class 'database.models.Order'>.amount_total as Sum(Item.amount Where  - None)  
    5. RowEvent Order.send_order_to_shipping()   
```
**Logic Log** in Scenario: Carbon Neutral Discount Applied
```

Carbon Neutral Discount Applie
 - 2025-10-24 08:44:43,859 - logic_logger - INF

Logic Phase:		ROW LOGIC		(session=0x10a377240) (sqlalchemy before_flush)			 - 2025-10-24 08:44:43,861 - logic_logger - INF
..Customer[30] {Update - client} id: 30, name: Diana 1761320683854, balance: 0E-10, credit_limit: 5000.0000000000, email: None, email_opt_out: None  row: 0x10a44ba50  session: 0x10a377240  ins_upd_dlt: upd, initial: upd - 2025-10-24 08:44:43,861 - logic_logger - INF
Logic Phase:		COMMIT LOGIC		(session=0x10a377240)   										 - 2025-10-24 08:44:43,861 - logic_logger - INF
Logic Phase:		AFTER_FLUSH LOGIC	(session=0x10a377240)   										 - 2025-10-24 08:44:43,861 - logic_logger - INF

```
</details>
  
&nbsp;
&nbsp;
### Scenario: Item Quantity Change
&emsp;  Scenario: Item Quantity Change  
&emsp;&emsp;    Given Customer "Charlie" with balance 0 and credit limit 2000  
    And Order is created for "Charlie" with 5 Widget  
&emsp;&emsp;    When Item quantity changed to 10  
&emsp;&emsp;    Then Item amount should be 900  
    And Order amount_total should be 900  
    And Customer balance should be 900  
<details markdown>
<summary>Tests - and their logic - are transparent.. click to see Logic</summary>


&nbsp;
&nbsp;


**Rules Used** in Scenario: Item Quantity Change
```
  Customer  
    1. Derive <class 'database.models.Customer'>.balance as Sum(Order.amount_total Where Rule.sum(derive=Customer.balance, as_sum_of=Order.amount_total, where=lambda row: row.date_shipped is None) - <function declare_logic.<locals>.<lambda> at 0x109355260>)  
  Item  
    2. Derive <class 'database.models.Item'>.amount as Formula (1): <function>  
  Order  
    3. RowEvent Order.send_order_to_shipping()   
    4. Derive <class 'database.models.Order'>.amount_total as Sum(Item.amount Where  - None)  
```
**Logic Log** in Scenario: Item Quantity Change
```

Item Quantity Chang
 - 2025-10-24 08:44:43,889 - logic_logger - INF

Logic Phase:		ROW LOGIC		(session=0x10a376470) (sqlalchemy before_flush)			 - 2025-10-24 08:44:43,891 - logic_logger - INF
..Item[32] {Update - client} id: 32, order_id: 27, product_id: 2, quantity:  [5-->] 10, amount: 450.0000000000, unit_price: 90.0000000000  row: 0x10a56e150  session: 0x10a376470  ins_upd_dlt: upd, initial: upd - 2025-10-24 08:44:43,891 - logic_logger - INF
..Item[32] {Formula amount} id: 32, order_id: 27, product_id: 2, quantity:  [5-->] 10, amount:  [450.0000000000-->] 900.0000000000, unit_price: 90.0000000000  row: 0x10a56e150  session: 0x10a376470  ins_upd_dlt: upd, initial: upd - 2025-10-24 08:44:43,891 - logic_logger - INF
....Order[27] {Update - Adjusting order: amount_total} id: 27, notes: Test order - Item Quantity Change, customer_id: 31, CreatedOn: 2025-10-24, date_shipped: None, amount_total:  [450.0000000000-->] 900.0000000000  row: 0x10a56ded0  session: 0x10a376470  ins_upd_dlt: upd, initial: upd - 2025-10-24 08:44:43,891 - logic_logger - INF
......Customer[31] {Update - Adjusting customer: balance} id: 31, name: Charlie 1761320683872, balance:  [450.0000000000-->] 900.0000000000, credit_limit: 2000.0000000000, email: None, email_opt_out: None  row: 0x10a56ed50  session: 0x10a376470  ins_upd_dlt: upd, initial: upd - 2025-10-24 08:44:43,892 - logic_logger - INF
Logic Phase:		COMMIT LOGIC		(session=0x10a376470)   										 - 2025-10-24 08:44:43,892 - logic_logger - INF
Logic Phase:		AFTER_FLUSH LOGIC	(session=0x10a376470)   										 - 2025-10-24 08:44:43,892 - logic_logger - INF
....Order[27] {AfterFlush Event} id: 27, notes: Test order - Item Quantity Change, customer_id: 31, CreatedOn: 2025-10-24, date_shipped: None, amount_total:  [450.0000000000-->] 900.0000000000  row: 0x10a56ded0  session: 0x10a376470  ins_upd_dlt: upd, initial: upd - 2025-10-24 08:44:43,892 - logic_logger - INF

```
</details>
  
&nbsp;
&nbsp;
### Scenario: Change Product in Item
&emsp;  Scenario: Change Product in Item  
&emsp;&emsp;    Given Customer "Alice" with balance 0 and credit limit 5000  
    And Order is created for "Alice" with 5 Widget  
&emsp;&emsp;    When Item product changed to "Gadget"  
&emsp;&emsp;    Then Item unit_price should be 150  
    And Item amount should be 750  
    And Order amount_total should be 750  
    And Customer balance should be 750  
<details markdown>
<summary>Tests - and their logic - are transparent.. click to see Logic</summary>


&nbsp;
&nbsp;


**Rules Used** in Scenario: Change Product in Item
```
  Customer  
    1. Derive <class 'database.models.Customer'>.balance as Sum(Order.amount_total Where Rule.sum(derive=Customer.balance, as_sum_of=Order.amount_total, where=lambda row: row.date_shipped is None) - <function declare_logic.<locals>.<lambda> at 0x109355260>)  
  Item  
    2. Derive <class 'database.models.Item'>.unit_price as Copy(product.unit_price)  
    3. Derive <class 'database.models.Item'>.amount as Formula (1): <function>  
  Order  
    4. Derive <class 'database.models.Order'>.amount_total as Sum(Item.amount Where  - None)  
    5. RowEvent Order.send_order_to_shipping()   
```
**Logic Log** in Scenario: Change Product in Item
```

Change Product in Ite
 - 2025-10-24 08:44:43,917 - logic_logger - INF

Logic Phase:		ROW LOGIC		(session=0x10a376140) (sqlalchemy before_flush)			 - 2025-10-24 08:44:43,920 - logic_logger - INF
..Item[33] {Update - client} id: 33, order_id: 28, product_id:  [2-->] 1, quantity: 5, amount: 450.0000000000, unit_price: 90.0000000000  row: 0x10a44a4d0  session: 0x10a376140  ins_upd_dlt: upd, initial: upd - 2025-10-24 08:44:43,921 - logic_logger - INF
..Item[33] {copy_rules for role: product - unit_price} id: 33, order_id: 28, product_id:  [2-->] 1, quantity: 5, amount: 450.0000000000, unit_price:  [90.0000000000-->] 150.0000000000  row: 0x10a44a4d0  session: 0x10a376140  ins_upd_dlt: upd, initial: upd - 2025-10-24 08:44:43,921 - logic_logger - INF
..Item[33] {Formula amount} id: 33, order_id: 28, product_id:  [2-->] 1, quantity: 5, amount:  [450.0000000000-->] 750.0000000000, unit_price:  [90.0000000000-->] 150.0000000000  row: 0x10a44a4d0  session: 0x10a376140  ins_upd_dlt: upd, initial: upd - 2025-10-24 08:44:43,921 - logic_logger - INF
....Order[28] {Update - Adjusting order: amount_total} id: 28, notes: Test order - Change Product in Item, customer_id: 32, CreatedOn: 2025-10-24, date_shipped: None, amount_total:  [450.0000000000-->] 750.0000000000  row: 0x10a44bb50  session: 0x10a376140  ins_upd_dlt: upd, initial: upd - 2025-10-24 08:44:43,921 - logic_logger - INF
......Customer[32] {Update - Adjusting customer: balance} id: 32, name: Alice 1761320683899, balance:  [450.0000000000-->] 750.0000000000, credit_limit: 5000.0000000000, email: None, email_opt_out: None  row: 0x10a44be50  session: 0x10a376140  ins_upd_dlt: upd, initial: upd - 2025-10-24 08:44:43,921 - logic_logger - INF
Logic Phase:		COMMIT LOGIC		(session=0x10a376140)   										 - 2025-10-24 08:44:43,922 - logic_logger - INF
Logic Phase:		AFTER_FLUSH LOGIC	(session=0x10a376140)   										 - 2025-10-24 08:44:43,922 - logic_logger - INF
....Order[28] {AfterFlush Event} id: 28, notes: Test order - Change Product in Item, customer_id: 32, CreatedOn: 2025-10-24, date_shipped: None, amount_total:  [450.0000000000-->] 750.0000000000  row: 0x10a44bb50  session: 0x10a376140  ins_upd_dlt: upd, initial: upd - 2025-10-24 08:44:43,922 - logic_logger - INF

```
</details>
  
&nbsp;
&nbsp;
### Scenario: Delete Item Reduces Order
&emsp;  Scenario: Delete Item Reduces Order  
&emsp;&emsp;    Given Customer "Bob" with balance 0 and credit limit 3000  
    And Order is created for "Bob" with 3 Widget and 2 Gadget  
&emsp;&emsp;    When First item is deleted  
&emsp;&emsp;    Then Order amount_total should be 300  
    And Customer balance should be 300  
<details markdown>
<summary>Tests - and their logic - are transparent.. click to see Logic</summary>


&nbsp;
&nbsp;


**Rules Used** in Scenario: Delete Item Reduces Order
```
  Customer  
    1. Derive <class 'database.models.Customer'>.balance as Sum(Order.amount_total Where Rule.sum(derive=Customer.balance, as_sum_of=Order.amount_total, where=lambda row: row.date_shipped is None) - <function declare_logic.<locals>.<lambda> at 0x109355260>)  
  Order  
    2. RowEvent Order.send_order_to_shipping()   
    3. Derive <class 'database.models.Order'>.amount_total as Sum(Item.amount Where  - None)  
```
**Logic Log** in Scenario: Delete Item Reduces Order
```

Delete Item Reduces Orde
 - 2025-10-24 08:44:43,951 - logic_logger - INF

Logic Phase:		ROW LOGIC		(session=0x10a377df0) (sqlalchemy before_flush)			 - 2025-10-24 08:44:43,952 - logic_logger - INF
..Item[34] {Delete - client} id: 34, order_id: 29, product_id: 2, quantity: 3, amount: 270.0000000000, unit_price: 90.0000000000  row: 0x10a448650  session: 0x10a377df0  ins_upd_dlt: dlt, initial: dlt - 2025-10-24 08:44:43,952 - logic_logger - INF
....Order[29] {Update - Adjusting order: amount_total} id: 29, notes: Test order - Delete Item Reduces Order, customer_id: 33, CreatedOn: 2025-10-24, date_shipped: None, amount_total:  [570.0000000000-->] 300.0000000000  row: 0x10a44b3d0  session: 0x10a377df0  ins_upd_dlt: upd, initial: upd - 2025-10-24 08:44:43,952 - logic_logger - INF
......Customer[33] {Update - Adjusting customer: balance} id: 33, name: Bob 1761320683930, balance:  [570.0000000000-->] 300.0000000000, credit_limit: 3000.0000000000, email: None, email_opt_out: None  row: 0x10a3cbcd0  session: 0x10a377df0  ins_upd_dlt: upd, initial: upd - 2025-10-24 08:44:43,953 - logic_logger - INF
Logic Phase:		COMMIT LOGIC		(session=0x10a377df0)   										 - 2025-10-24 08:44:43,953 - logic_logger - INF
Logic Phase:		AFTER_FLUSH LOGIC	(session=0x10a377df0)   										 - 2025-10-24 08:44:43,953 - logic_logger - INF
....Order[29] {AfterFlush Event} id: 29, notes: Test order - Delete Item Reduces Order, customer_id: 33, CreatedOn: 2025-10-24, date_shipped: None, amount_total:  [570.0000000000-->] 300.0000000000  row: 0x10a44b3d0  session: 0x10a377df0  ins_upd_dlt: upd, initial: upd - 2025-10-24 08:44:43,953 - logic_logger - INF

```
</details>
  
&nbsp;
&nbsp;
### Scenario: Change Order Customer
&emsp;  Scenario: Change Order Customer  
&emsp;&emsp;    Given Customer "Alice" with balance 0 and credit limit 5000  
    And Customer "Bob" with balance 0 and credit limit 3000  
    And Order is created for "Alice" with 5 Widget  
&emsp;&emsp;    When Order customer changed to "Bob"  
&emsp;&emsp;    Then Customer "Alice" balance should be 0  
    And Customer "Bob" balance should be 450  
<details markdown>
<summary>Tests - and their logic - are transparent.. click to see Logic</summary>


&nbsp;
&nbsp;


**Rules Used** in Scenario: Change Order Customer
```
  Customer  
    1. Derive <class 'database.models.Customer'>.balance as Sum(Order.amount_total Where Rule.sum(derive=Customer.balance, as_sum_of=Order.amount_total, where=lambda row: row.date_shipped is None) - <function declare_logic.<locals>.<lambda> at 0x109355260>)  
  Order  
    2. RowEvent Order.send_order_to_shipping()   
```
**Logic Log** in Scenario: Change Order Customer
```

Change Order Custome
 - 2025-10-24 08:44:43,976 - logic_logger - INF

Logic Phase:		ROW LOGIC		(session=0x10a376f10) (sqlalchemy before_flush)			 - 2025-10-24 08:44:43,978 - logic_logger - INF
..Order[30] {Update - client} id: 30, notes: Test order - Change Order Customer, customer_id:  [34-->] 35, CreatedOn: 2025-10-24, date_shipped: None, amount_total: 450.0000000000  row: 0x10a4490d0  session: 0x10a376f10  ins_upd_dlt: upd, initial: upd - 2025-10-24 08:44:43,978 - logic_logger - INF
....Customer[35] {Update - Adjusting customer: balance, balance} id: 35, name: Bob 1761320683960, balance:  [0E-10-->] 450.0000000000, credit_limit: 3000.0000000000, email: None, email_opt_out: None  row: 0x10a44a7d0  session: 0x10a376f10  ins_upd_dlt: upd, initial: upd - 2025-10-24 08:44:43,978 - logic_logger - INF
....Customer[34] {Update - Adjusting Old customer} id: 34, name: Alice 1761320683958, balance:  [450.0000000000-->] 0E-10, credit_limit: 5000.0000000000, email: None, email_opt_out: None  row: 0x10a44bad0  session: 0x10a376f10  ins_upd_dlt: upd, initial: upd - 2025-10-24 08:44:43,979 - logic_logger - INF
Logic Phase:		COMMIT LOGIC		(session=0x10a376f10)   										 - 2025-10-24 08:44:43,979 - logic_logger - INF
Logic Phase:		AFTER_FLUSH LOGIC	(session=0x10a376f10)   										 - 2025-10-24 08:44:43,979 - logic_logger - INF
..Order[30] {AfterFlush Event} id: 30, notes: Test order - Change Order Customer, customer_id:  [34-->] 35, CreatedOn: 2025-10-24, date_shipped: None, amount_total: 450.0000000000  row: 0x10a4490d0  session: 0x10a376f10  ins_upd_dlt: upd, initial: upd - 2025-10-24 08:44:43,979 - logic_logger - INF

```
</details>
  
&nbsp;
&nbsp;
### Scenario: Ship Order Excludes from Balance
&emsp;  Scenario: Ship Order Excludes from Balance  
&emsp;&emsp;    Given Customer "Charlie" with balance 0 and credit limit 2000  
    And Order is created for "Charlie" with 2 Widget  
&emsp;&emsp;    When Order is shipped  
&emsp;&emsp;    Then Customer balance should be 0  
    And Order amount_total should be 180  
<details markdown>
<summary>Tests - and their logic - are transparent.. click to see Logic</summary>


&nbsp;
&nbsp;


**Rules Used** in Scenario: Ship Order Excludes from Balance
```
  Customer  
    1. Derive <class 'database.models.Customer'>.balance as Sum(Order.amount_total Where Rule.sum(derive=Customer.balance, as_sum_of=Order.amount_total, where=lambda row: row.date_shipped is None) - <function declare_logic.<locals>.<lambda> at 0x109355260>)  
  Order  
    2. RowEvent Order.send_order_to_shipping()   
```
**Logic Log** in Scenario: Ship Order Excludes from Balance
```

Ship Order Excludes from Balanc
 - 2025-10-24 08:44:43,999 - logic_logger - INF

Logic Phase:		ROW LOGIC		(session=0x10a377ac0) (sqlalchemy before_flush)			 - 2025-10-24 08:44:44,001 - logic_logger - INF
..Order[31] {Update - client} id: 31, notes: Test order - Ship Order Excludes from Balance, customer_id: 36, CreatedOn: 2025-10-24, date_shipped:  [None-->] 2025-10-22 00:00:00, amount_total: 180.0000000000  row: 0x10a44ac50  session: 0x10a377ac0  ins_upd_dlt: upd, initial: upd - 2025-10-24 08:44:44,001 - logic_logger - INF
....Customer[36] {Update - Adjusting customer: balance} id: 36, name: Charlie 1761320683984, balance:  [180.0000000000-->] 0E-10, credit_limit: 2000.0000000000, email: None, email_opt_out: None  row: 0x10a3cb050  session: 0x10a377ac0  ins_upd_dlt: upd, initial: upd - 2025-10-24 08:44:44,002 - logic_logger - INF
Logic Phase:		COMMIT LOGIC		(session=0x10a377ac0)   										 - 2025-10-24 08:44:44,002 - logic_logger - INF
Logic Phase:		AFTER_FLUSH LOGIC	(session=0x10a377ac0)   										 - 2025-10-24 08:44:44,002 - logic_logger - INF
..Order[31] {AfterFlush Event} id: 31, notes: Test order - Ship Order Excludes from Balance, customer_id: 36, CreatedOn: 2025-10-24, date_shipped:  [None-->] 2025-10-22 00:00:00, amount_total: 180.0000000000  row: 0x10a44ac50  session: 0x10a377ac0  ins_upd_dlt: upd, initial: upd - 2025-10-24 08:44:44,002 - logic_logger - INF

```
</details>
  
&nbsp;
&nbsp;
### Scenario: Unship Order Includes in Balance
&emsp;  Scenario: Unship Order Includes in Balance  
&emsp;&emsp;    Given Customer "Diana" with balance 0 and credit limit 5000  
    And Shipped order is created for "Diana" with 3 Gadget  
&emsp;&emsp;    When Order is unshipped  
&emsp;&emsp;    Then Customer balance should be 450  
    And Order amount_total should be 450  
<details markdown>
<summary>Tests - and their logic - are transparent.. click to see Logic</summary>


&nbsp;
&nbsp;


**Rules Used** in Scenario: Unship Order Includes in Balance
```
  Customer  
    1. Derive <class 'database.models.Customer'>.balance as Sum(Order.amount_total Where Rule.sum(derive=Customer.balance, as_sum_of=Order.amount_total, where=lambda row: row.date_shipped is None) - <function declare_logic.<locals>.<lambda> at 0x109355260>)  
  Order  
    2. RowEvent Order.send_order_to_shipping()   
```
**Logic Log** in Scenario: Unship Order Includes in Balance
```

Unship Order Includes in Balanc
 - 2025-10-24 08:44:44,023 - logic_logger - INF

Logic Phase:		ROW LOGIC		(session=0x10a377240) (sqlalchemy before_flush)			 - 2025-10-24 08:44:44,025 - logic_logger - INF
..Order[32] {Update - client} id: 32, notes: Test shipped order - Unship Order Includes in Balance, customer_id: 37, CreatedOn: 2025-10-24, date_shipped:  [2025-10-22-->] None, amount_total: 450.0000000000  row: 0x10a3c9850  session: 0x10a377240  ins_upd_dlt: upd, initial: upd - 2025-10-24 08:44:44,025 - logic_logger - INF
....Customer[37] {Update - Adjusting customer: balance} id: 37, name: Diana 1761320684007, balance:  [0E-10-->] 450.0000000000, credit_limit: 5000.0000000000, email: None, email_opt_out: None  row: 0x10a3c8950  session: 0x10a377240  ins_upd_dlt: upd, initial: upd - 2025-10-24 08:44:44,026 - logic_logger - INF
Logic Phase:		COMMIT LOGIC		(session=0x10a377240)   										 - 2025-10-24 08:44:44,026 - logic_logger - INF
Logic Phase:		AFTER_FLUSH LOGIC	(session=0x10a377240)   										 - 2025-10-24 08:44:44,026 - logic_logger - INF
..Order[32] {AfterFlush Event} id: 32, notes: Test shipped order - Unship Order Includes in Balance, customer_id: 37, CreatedOn: 2025-10-24, date_shipped:  [2025-10-22-->] None, amount_total: 450.0000000000  row: 0x10a3c9850  session: 0x10a377240  ins_upd_dlt: upd, initial: upd - 2025-10-24 08:44:44,026 - logic_logger - INF

```
</details>
  
&nbsp;
&nbsp;
### Scenario: Exceed Credit Limit Rejected
&emsp;  Scenario: Exceed Credit Limit Rejected  
&emsp;&emsp;    Given Customer "Silent" with balance 0 and credit limit 1000  
&emsp;&emsp;    When B2B order placed for "Silent" with 20 Widget  
&emsp;&emsp;    Then Order should be rejected  
    And Error message should contain "exceeds credit limit"  
<details markdown>
<summary>Tests - and their logic - are transparent.. click to see Logic</summary>


&nbsp;
&nbsp;


**Rules Used** in Scenario: Exceed Credit Limit Rejected
```
  Customer  
    1. Derive <class 'database.models.Customer'>.balance as Sum(Order.amount_total Where Rule.sum(derive=Customer.balance, as_sum_of=Order.amount_total, where=lambda row: row.date_shipped is None) - <function declare_logic.<locals>.<lambda> at 0x109355260>)  
    2. Constraint Function: None   
  Item  
    3. Derive <class 'database.models.Item'>.unit_price as Copy(product.unit_price)  
    4. Derive <class 'database.models.Item'>.amount as Formula (1): <function>  
  Order  
    5. Derive <class 'database.models.Order'>.amount_total as Sum(Item.amount Where  - None)  
```
**Logic Log** in Scenario: Exceed Credit Limit Rejected
```

Exceed Credit Limit Rejecte
 - 2025-10-24 08:44:44,036 - logic_logger - INF

Logic Phase:		ROW LOGIC		(session=0x10a377130) (sqlalchemy before_flush)			 - 2025-10-24 08:44:44,038 - logic_logger - INF
..Customer[38] {Update - client} id: 38, name: Silent 1761320684031, balance: 0E-10, credit_limit: 1000.0000000000, email: None, email_opt_out: None  row: 0x10a48c950  session: 0x10a377130  ins_upd_dlt: upd, initial: upd - 2025-10-24 08:44:44,038 - logic_logger - INF
Logic Phase:		COMMIT LOGIC		(session=0x10a377130)   										 - 2025-10-24 08:44:44,038 - logic_logger - INF
Logic Phase:		AFTER_FLUSH LOGIC	(session=0x10a377130)   										 - 2025-10-24 08:44:44,038 - logic_logger - INF

```
</details>
  
&nbsp;&nbsp;  
/Users/val/dev/ApiLogicServer/ApiLogicServer-dev/build_and_test/ApiLogicServer/basic_demo/test/api_logic_server_behave/behave_run.py completed at October 24, 2025 08:44:4  