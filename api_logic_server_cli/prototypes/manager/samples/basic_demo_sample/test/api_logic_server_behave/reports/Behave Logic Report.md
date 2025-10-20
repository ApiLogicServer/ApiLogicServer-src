This report combines:
* Behave log (lists Features, test Scenarios, results), with embedded
* Logic showing rules executed, and how they operated



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
 - 2025-10-20 08:59:10,304 - logic_logger - DEBU
Rule Bank[0x10893ecf0] (loaded 2025-10-20 08:49:47.292946
Mapped Class[Customer] rules
  Constraint Function: None
  Constraint Function: None
  Derive <class 'database.models.Customer'>.balance as Sum(Order.amount_total Where # Derive the customer's balance as the sum of order totals where not yet shipped
    Rule.sum(derive=Customer.balance, as_sum_of=Order.amount_total, where=lambda row: row.date_shipped is None) - <function declare_logic.<locals>.<lambda> at 0x108a1ccc0>
Mapped Class[SysEmail] rules
  RowEvent SysEmail.send_mail()
Mapped Class[Order] rules
  Derive <class 'database.models.Order'>.amount_total as Sum(Item.amount Where  - None
  RowEvent Order.send_order_to_shipping()
Mapped Class[Item] rules
  Derive <class 'database.models.Item'>.amount as Formula (1): <function
  Derive <class 'database.models.Item'>.unit_price as Copy(product.unit_price
Logic Bank - 14 rules loaded - 2025-10-20 08:59:10,305 - logic_logger - INF
Logic Bank - 14 rules loaded - 2025-10-20 08:59:10,305 - logic_logger - INF
```
</details>
  
&nbsp;
&nbsp;
## Feature: Order Processing with Business Logic  
  
&nbsp;
&nbsp;
### Scenario: Good Order Placed via B2B API
&emsp;  Scenario: Good Order Placed via B2B API  
&emsp;&emsp;    Given Customer "Alice" with balance 0 and credit limit 1000  
&emsp;&emsp;    When B2B order placed for "Alice" with 5 Widget  
&emsp;&emsp;    Then Customer balance should be 450  
    And Order amount_total should be 450  
    And Order created successfully  
<details markdown>
<summary>Tests - and their logic - are transparent.. click to see Logic</summary>


&nbsp;
&nbsp;


**Rules Used** in Scenario: Good Order Placed via B2B API
```
  Customer  
    1. Derive <class 'database.models.Customer'>.balance as Sum(Order.amount_total Where Rule.sum(derive=Customer.balance, as_sum_of=Order.amount_total, where=lambda row: row.date_shipped is None) - <function declare_logic.<locals>.<lambda> at 0x108fed080>)  
  Item  
    2. Derive <class 'database.models.Item'>.amount as Formula (1): <function>  
    3. Derive <class 'database.models.Item'>.unit_price as Copy(product.unit_price)  
  Order  
    4. Derive <class 'database.models.Order'>.amount_total as Sum(Item.amount Where  - None)  
    5. RowEvent Order.send_order_to_shipping()   
```
**Logic Log** in Scenario: Good Order Placed via B2B API
```

Good Order Placed via B2B AP
 - 2025-10-20 11:28:01,655 - logic_logger - INF

Logic Phase:		ROW LOGIC		(session=0x10a00e250) (sqlalchemy before_flush)			 - 2025-10-20 11:28:01,657 - logic_logger - INF
..Customer[164] {Update - client} id: 164, name: Alice 1760984881645, balance: 0E-10, credit_limit: 1000.0000000000, email: None, email_opt_out: None  row: 0x10a261fd0  session: 0x10a00e250  ins_upd_dlt: upd, initial: upd - 2025-10-20 11:28:01,657 - logic_logger - INF
Logic Phase:		COMMIT LOGIC		(session=0x10a00e250)   										 - 2025-10-20 11:28:01,657 - logic_logger - INF
Logic Phase:		AFTER_FLUSH LOGIC	(session=0x10a00e250)   										 - 2025-10-20 11:28:01,657 - logic_logger - INF

```
</details>
  
&nbsp;
&nbsp;
### Scenario: Item Quantity Update Recalculates Amounts
&emsp;  Scenario: Item Quantity Update Recalculates Amounts  
&emsp;&emsp;    Given Customer "Bob" with balance 0 and credit limit 2000  
    And Order exists for "Bob" with 5 Widget  
&emsp;&emsp;    When Item quantity changed to 10  
&emsp;&emsp;    Then Item amount should be 900  
    And Order amount_total should be 900  
    And Customer balance should be 900  
<details markdown>
<summary>Tests - and their logic - are transparent.. click to see Logic</summary>


&nbsp;
&nbsp;


**Rules Used** in Scenario: Item Quantity Update Recalculates Amounts
```
  Customer  
    1. Derive <class 'database.models.Customer'>.balance as Sum(Order.amount_total Where Rule.sum(derive=Customer.balance, as_sum_of=Order.amount_total, where=lambda row: row.date_shipped is None) - <function declare_logic.<locals>.<lambda> at 0x108fed080>)  
  Item  
    2. Derive <class 'database.models.Item'>.amount as Formula (1): <function>  
  Order  
    3. RowEvent Order.send_order_to_shipping()   
    4. Derive <class 'database.models.Order'>.amount_total as Sum(Item.amount Where  - None)  
```
**Logic Log** in Scenario: Item Quantity Update Recalculates Amounts
```

Item Quantity Update Recalculates Amount
 - 2025-10-20 11:28:01,686 - logic_logger - INF

Logic Phase:		ROW LOGIC		(session=0x10a00dd00) (sqlalchemy before_flush)			 - 2025-10-20 11:28:01,688 - logic_logger - INF
..Item[148] {Update - client} id: 148, order_id: 132, product_id: 2, quantity:  [5-->] 10, amount: 450.0000000000, unit_price: 90.0000000000  row: 0x10a262350  session: 0x10a00dd00  ins_upd_dlt: upd, initial: upd - 2025-10-20 11:28:01,688 - logic_logger - INF
..Item[148] {Formula amount} id: 148, order_id: 132, product_id: 2, quantity:  [5-->] 10, amount:  [450.0000000000-->] 900.0000000000, unit_price: 90.0000000000  row: 0x10a262350  session: 0x10a00dd00  ins_upd_dlt: upd, initial: upd - 2025-10-20 11:28:01,688 - logic_logger - INF
....Order[132] {Update - Adjusting order: amount_total} id: 132, notes: Test order, customer_id: 165, CreatedOn: 2025-10-20, date_shipped: None, amount_total:  [450.0000000000-->] 900.0000000000  row: 0x10a2616d0  session: 0x10a00dd00  ins_upd_dlt: upd, initial: upd - 2025-10-20 11:28:01,689 - logic_logger - INF
......Customer[165] {Update - Adjusting customer: balance} id: 165, name: Bob 1760984881672, balance:  [450.0000000000-->] 900.0000000000, credit_limit: 2000.0000000000, email: None, email_opt_out: None  row: 0x10a263ad0  session: 0x10a00dd00  ins_upd_dlt: upd, initial: upd - 2025-10-20 11:28:01,689 - logic_logger - INF
Logic Phase:		COMMIT LOGIC		(session=0x10a00dd00)   										 - 2025-10-20 11:28:01,689 - logic_logger - INF
Logic Phase:		AFTER_FLUSH LOGIC	(session=0x10a00dd00)   										 - 2025-10-20 11:28:01,689 - logic_logger - INF
....Order[132] {AfterFlush Event} id: 132, notes: Test order, customer_id: 165, CreatedOn: 2025-10-20, date_shipped: None, amount_total:  [450.0000000000-->] 900.0000000000  row: 0x10a2616d0  session: 0x10a00dd00  ins_upd_dlt: upd, initial: upd - 2025-10-20 11:28:01,690 - logic_logger - INF

```
</details>
  
&nbsp;
&nbsp;
### Scenario: Change Order Customer Adjusts Both Balances
&emsp;  Scenario: Change Order Customer Adjusts Both Balances  
&emsp;&emsp;    Given Customer "Charlie" with balance 0 and credit limit 1500  
    And Customer "Diana" with balance 0 and credit limit 2000  
    And Order exists for "Charlie" with 2 Gadget  
&emsp;&emsp;    When Order customer changed to "Diana"  
&emsp;&emsp;    Then Customer "Charlie" balance should be 0  
    And Customer "Diana" balance should be 300  
<details markdown>
<summary>Tests - and their logic - are transparent.. click to see Logic</summary>


&nbsp;
&nbsp;


**Rules Used** in Scenario: Change Order Customer Adjusts Both Balances
```
  Customer  
    1. Derive <class 'database.models.Customer'>.balance as Sum(Order.amount_total Where Rule.sum(derive=Customer.balance, as_sum_of=Order.amount_total, where=lambda row: row.date_shipped is None) - <function declare_logic.<locals>.<lambda> at 0x108fed080>)  
  Order  
    2. RowEvent Order.send_order_to_shipping()   
```
**Logic Log** in Scenario: Change Order Customer Adjusts Both Balances
```

Change Order Customer Adjusts Both Balance
 - 2025-10-20 11:28:01,723 - logic_logger - INF

Logic Phase:		ROW LOGIC		(session=0x10a00d9d0) (sqlalchemy before_flush)			 - 2025-10-20 11:28:01,725 - logic_logger - INF
..Order[133] {Update - client} id: 133, notes: Test order, customer_id:  [166-->] 167, CreatedOn: 2025-10-20, date_shipped: None, amount_total: 300.0000000000  row: 0x109ffe8d0  session: 0x10a00d9d0  ins_upd_dlt: upd, initial: upd - 2025-10-20 11:28:01,725 - logic_logger - INF
....Customer[167] {Update - Adjusting customer: balance, balance} id: 167, name: Diana 1760984881704, balance:  [0E-10-->] 300.0000000000, credit_limit: 2000.0000000000, email: None, email_opt_out: None  row: 0x10a282650  session: 0x10a00d9d0  ins_upd_dlt: upd, initial: upd - 2025-10-20 11:28:01,726 - logic_logger - INF
....Customer[166] {Update - Adjusting Old customer} id: 166, name: Charlie 1760984881701, balance:  [300.0000000000-->] 0E-10, credit_limit: 1500.0000000000, email: None, email_opt_out: None  row: 0x10a281cd0  session: 0x10a00d9d0  ins_upd_dlt: upd, initial: upd - 2025-10-20 11:28:01,726 - logic_logger - INF
Logic Phase:		COMMIT LOGIC		(session=0x10a00d9d0)   										 - 2025-10-20 11:28:01,727 - logic_logger - INF
Logic Phase:		AFTER_FLUSH LOGIC	(session=0x10a00d9d0)   										 - 2025-10-20 11:28:01,727 - logic_logger - INF
..Order[133] {AfterFlush Event} id: 133, notes: Test order, customer_id:  [166-->] 167, CreatedOn: 2025-10-20, date_shipped: None, amount_total: 300.0000000000  row: 0x109ffe8d0  session: 0x10a00d9d0  ins_upd_dlt: upd, initial: upd - 2025-10-20 11:28:01,727 - logic_logger - INF

```
</details>
  
&nbsp;
&nbsp;
### Scenario: Delete Item Reduces Order Total and Customer Balance
&emsp;  Scenario: Delete Item Reduces Order Total and Customer Balance  
&emsp;&emsp;    Given Customer "TestCustomer" with balance 0 and credit limit 3000  
    And Order exists for "TestCustomer" with 3 Widget and 2 Gadget  
&emsp;&emsp;    When First item deleted  
&emsp;&emsp;    Then Order amount_total should be 300  
    And Customer balance should be 300  
<details markdown>
<summary>Tests - and their logic - are transparent.. click to see Logic</summary>


&nbsp;
&nbsp;


**Rules Used** in Scenario: Delete Item Reduces Order Total and Customer Balance
```
  Customer  
    1. Derive <class 'database.models.Customer'>.balance as Sum(Order.amount_total Where Rule.sum(derive=Customer.balance, as_sum_of=Order.amount_total, where=lambda row: row.date_shipped is None) - <function declare_logic.<locals>.<lambda> at 0x108fed080>)  
  Order  
    2. RowEvent Order.send_order_to_shipping()   
    3. Derive <class 'database.models.Order'>.amount_total as Sum(Item.amount Where  - None)  
```
**Logic Log** in Scenario: Delete Item Reduces Order Total and Customer Balance
```

Delete Item Reduces Order Total and Customer Balanc
 - 2025-10-20 11:28:01,758 - logic_logger - INF

Logic Phase:		ROW LOGIC		(session=0x10a00ff00) (sqlalchemy before_flush)			 - 2025-10-20 11:28:01,759 - logic_logger - INF
..Item[150] {Delete - client} id: 150, order_id: 134, product_id: 2, quantity: 3, amount: 270.0000000000, unit_price: 90.0000000000  row: 0x10a262450  session: 0x10a00ff00  ins_upd_dlt: dlt, initial: dlt - 2025-10-20 11:28:01,760 - logic_logger - INF
....Order[134] {Update - Adjusting order: amount_total} id: 134, notes: Multi-item test order, customer_id: 168, CreatedOn: 2025-10-20, date_shipped: None, amount_total:  [570.0000000000-->] 300.0000000000  row: 0x10a2639d0  session: 0x10a00ff00  ins_upd_dlt: upd, initial: upd - 2025-10-20 11:28:01,760 - logic_logger - INF
......Customer[168] {Update - Adjusting customer: balance} id: 168, name: TestCustomer 1760984881739, balance:  [570.0000000000-->] 300.0000000000, credit_limit: 3000.0000000000, email: None, email_opt_out: None  row: 0x10a261e50  session: 0x10a00ff00  ins_upd_dlt: upd, initial: upd - 2025-10-20 11:28:01,760 - logic_logger - INF
Logic Phase:		COMMIT LOGIC		(session=0x10a00ff00)   										 - 2025-10-20 11:28:01,760 - logic_logger - INF
Logic Phase:		AFTER_FLUSH LOGIC	(session=0x10a00ff00)   										 - 2025-10-20 11:28:01,761 - logic_logger - INF
....Order[134] {AfterFlush Event} id: 134, notes: Multi-item test order, customer_id: 168, CreatedOn: 2025-10-20, date_shipped: None, amount_total:  [570.0000000000-->] 300.0000000000  row: 0x10a2639d0  session: 0x10a00ff00  ins_upd_dlt: upd, initial: upd - 2025-10-20 11:28:01,761 - logic_logger - INF

```
</details>
  
&nbsp;
&nbsp;
### Scenario: Ship Order Excludes from Balance (WHERE exclude)
&emsp;  Scenario: Ship Order Excludes from Balance (WHERE exclude)  
&emsp;&emsp;    Given Customer "ShipTest" with balance 0 and credit limit 5000  
    And Order exists for "ShipTest" with 10 Widget  
&emsp;&emsp;    When Order is shipped  
&emsp;&emsp;    Then Customer balance should be 0  
<details markdown>
<summary>Tests - and their logic - are transparent.. click to see Logic</summary>


&nbsp;
&nbsp;


**Rules Used** in Scenario: Ship Order Excludes from Balance (WHERE exclude)
```
  Customer  
    1. Derive <class 'database.models.Customer'>.balance as Sum(Order.amount_total Where Rule.sum(derive=Customer.balance, as_sum_of=Order.amount_total, where=lambda row: row.date_shipped is None) - <function declare_logic.<locals>.<lambda> at 0x108fed080>)  
  Order  
    2. RowEvent Order.send_order_to_shipping()   
```
**Logic Log** in Scenario: Ship Order Excludes from Balance (WHERE exclude)
```

Ship Order Excludes from Balance (WHERE exclude
 - 2025-10-20 11:28:01,785 - logic_logger - INF

Logic Phase:		ROW LOGIC		(session=0x10a00fac0) (sqlalchemy before_flush)			 - 2025-10-20 11:28:01,788 - logic_logger - INF
..Order[135] {Update - client} id: 135, notes: Test order, customer_id: 169, CreatedOn: 2025-10-20, date_shipped:  [None-->] 2025-10-20 00:00:00, amount_total: 900.0000000000  row: 0x10a067550  session: 0x10a00fac0  ins_upd_dlt: upd, initial: upd - 2025-10-20 11:28:01,788 - logic_logger - INF
....Customer[169] {Update - Adjusting customer: balance} id: 169, name: ShipTest 1760984881769, balance:  [900.0000000000-->] 0E-10, credit_limit: 5000.0000000000, email: None, email_opt_out: None  row: 0x10a2813d0  session: 0x10a00fac0  ins_upd_dlt: upd, initial: upd - 2025-10-20 11:28:01,788 - logic_logger - INF
Logic Phase:		COMMIT LOGIC		(session=0x10a00fac0)   										 - 2025-10-20 11:28:01,788 - logic_logger - INF
Logic Phase:		AFTER_FLUSH LOGIC	(session=0x10a00fac0)   										 - 2025-10-20 11:28:01,789 - logic_logger - INF
..Order[135] {AfterFlush Event} id: 135, notes: Test order, customer_id: 169, CreatedOn: 2025-10-20, date_shipped:  [None-->] 2025-10-20 00:00:00, amount_total: 900.0000000000  row: 0x10a067550  session: 0x10a00fac0  ins_upd_dlt: upd, initial: upd - 2025-10-20 11:28:01,789 - logic_logger - INF

```
</details>
  
&nbsp;
&nbsp;
### Scenario: Unship Order Includes in Balance (WHERE include)
&emsp;  Scenario: Unship Order Includes in Balance (WHERE include)  
&emsp;&emsp;    Given Customer "UnshipTest" with balance 0 and credit limit 5000  
    And Shipped order exists for "UnshipTest" with 5 Gadget  
&emsp;&emsp;    When Order is unshipped  
&emsp;&emsp;    Then Customer balance should be 750  
<details markdown>
<summary>Tests - and their logic - are transparent.. click to see Logic</summary>


&nbsp;
&nbsp;


**Rules Used** in Scenario: Unship Order Includes in Balance (WHERE include)
```
  Customer  
    1. Derive <class 'database.models.Customer'>.balance as Sum(Order.amount_total Where Rule.sum(derive=Customer.balance, as_sum_of=Order.amount_total, where=lambda row: row.date_shipped is None) - <function declare_logic.<locals>.<lambda> at 0x108fed080>)  
  Order  
    2. RowEvent Order.send_order_to_shipping()   
```
**Logic Log** in Scenario: Unship Order Includes in Balance (WHERE include)
```

Unship Order Includes in Balance (WHERE include
 - 2025-10-20 11:28:01,812 - logic_logger - INF

Logic Phase:		ROW LOGIC		(session=0x10a00f790) (sqlalchemy before_flush)			 - 2025-10-20 11:28:01,813 - logic_logger - INF
..Order[136] {Update - client} id: 136, notes: Test order, customer_id: 170, CreatedOn: 2025-10-20, date_shipped:  [2025-10-20-->] None, amount_total: 750.0000000000  row: 0x10a280cd0  session: 0x10a00f790  ins_upd_dlt: upd, initial: upd - 2025-10-20 11:28:01,813 - logic_logger - INF
....Customer[170] {Update - Adjusting customer: balance} id: 170, name: UnshipTest 1760984881794, balance:  [0E-10-->] 750.0000000000, credit_limit: 5000.0000000000, email: None, email_opt_out: None  row: 0x10a2829d0  session: 0x10a00f790  ins_upd_dlt: upd, initial: upd - 2025-10-20 11:28:01,814 - logic_logger - INF
Logic Phase:		COMMIT LOGIC		(session=0x10a00f790)   										 - 2025-10-20 11:28:01,814 - logic_logger - INF
Logic Phase:		AFTER_FLUSH LOGIC	(session=0x10a00f790)   										 - 2025-10-20 11:28:01,814 - logic_logger - INF
..Order[136] {AfterFlush Event} id: 136, notes: Test order, customer_id: 170, CreatedOn: 2025-10-20, date_shipped:  [2025-10-20-->] None, amount_total: 750.0000000000  row: 0x10a280cd0  session: 0x10a00f790  ins_upd_dlt: upd, initial: upd - 2025-10-20 11:28:01,814 - logic_logger - INF

```
</details>
  
&nbsp;
&nbsp;
### Scenario: Exceed Credit Limit Rejected (Constraint FAIL)
&emsp;  Scenario: Exceed Credit Limit Rejected (Constraint FAIL)  
&emsp;&emsp;    Given Customer "LimitTest" with balance 0 and credit limit 500  
&emsp;&emsp;    When B2B order placed for "LimitTest" with 10 Gadget  
&emsp;&emsp;    Then Order creation should fail  
    And Error message should contain "credit limit"  
<details markdown>
<summary>Tests - and their logic - are transparent.. click to see Logic</summary>


&nbsp;
&nbsp;


**Rules Used** in Scenario: Exceed Credit Limit Rejected (Constraint FAIL)
```
```
**Logic Log** in Scenario: Exceed Credit Limit Rejected (Constraint FAIL)
```

Exceed Credit Limit Rejected (Constraint FAIL
 - 2025-10-20 11:28:01,824 - logic_logger - INF

Logic Phase:		ROW LOGIC		(session=0x10a00fdf0) (sqlalchemy before_flush)			 - 2025-10-20 11:28:01,825 - logic_logger - INF
..Customer[171] {Update - client} id: 171, name: LimitTest 1760984881819, balance: 0E-10, credit_limit: 500.0000000000, email: None, email_opt_out: None  row: 0x10a262a50  session: 0x10a00fdf0  ins_upd_dlt: upd, initial: upd - 2025-10-20 11:28:01,825 - logic_logger - INF
Logic Phase:		COMMIT LOGIC		(session=0x10a00fdf0)   										 - 2025-10-20 11:28:01,826 - logic_logger - INF
Logic Phase:		AFTER_FLUSH LOGIC	(session=0x10a00fdf0)   										 - 2025-10-20 11:28:01,826 - logic_logger - INF

```
</details>
  
&nbsp;
&nbsp;
### Scenario: Carbon Neutral Discount Applied (Custom Logic)
&emsp;  Scenario: Carbon Neutral Discount Applied (Custom Logic)  
&emsp;&emsp;    Given Customer "GreenBuyer" with balance 0 and credit limit 2000  
&emsp;&emsp;    When B2B order placed for "GreenBuyer" with 10 carbon neutral Gadget  
&emsp;&emsp;    Then Item amount should be 1350  
    And Order amount_total should be 1350  
    And Customer balance should be 1350  
<details markdown>
<summary>Tests - and their logic - are transparent.. click to see Logic</summary>


&nbsp;
&nbsp;


**Rules Used** in Scenario: Carbon Neutral Discount Applied (Custom Logic)
```
  Customer  
    1. Derive <class 'database.models.Customer'>.balance as Sum(Order.amount_total Where Rule.sum(derive=Customer.balance, as_sum_of=Order.amount_total, where=lambda row: row.date_shipped is None) - <function declare_logic.<locals>.<lambda> at 0x108fed080>)  
  Item  
    2. Derive <class 'database.models.Item'>.amount as Formula (1): <function>  
    3. Derive <class 'database.models.Item'>.unit_price as Copy(product.unit_price)  
  Order  
    4. Derive <class 'database.models.Order'>.amount_total as Sum(Item.amount Where  - None)  
    5. RowEvent Order.send_order_to_shipping()   
```
**Logic Log** in Scenario: Carbon Neutral Discount Applied (Custom Logic)
```

Carbon Neutral Discount Applied (Custom Logic
 - 2025-10-20 11:28:01,834 - logic_logger - INF

Logic Phase:		ROW LOGIC		(session=0x10a00fac0) (sqlalchemy before_flush)			 - 2025-10-20 11:28:01,836 - logic_logger - INF
..Customer[172] {Update - client} id: 172, name: GreenBuyer 1760984881829, balance: 0E-10, credit_limit: 2000.0000000000, email: None, email_opt_out: None  row: 0x10a191a50  session: 0x10a00fac0  ins_upd_dlt: upd, initial: upd - 2025-10-20 11:28:01,836 - logic_logger - INF
Logic Phase:		COMMIT LOGIC		(session=0x10a00fac0)   										 - 2025-10-20 11:28:01,836 - logic_logger - INF
Logic Phase:		AFTER_FLUSH LOGIC	(session=0x10a00fac0)   										 - 2025-10-20 11:28:01,836 - logic_logger - INF

```
</details>
  
&nbsp;
&nbsp;
### Scenario: Product Unit Price Copied to Item
&emsp;  Scenario: Product Unit Price Copied to Item  
&emsp;&emsp;    Given Customer "PriceCopy" with balance 0 and credit limit 3000  
&emsp;&emsp;    When B2B order placed for "PriceCopy" with 1 Green  
&emsp;&emsp;    Then Item unit_price should be 109  
<details markdown>
<summary>Tests - and their logic - are transparent.. click to see Logic</summary>


&nbsp;
&nbsp;


**Rules Used** in Scenario: Product Unit Price Copied to Item
```
  Customer  
    1. Derive <class 'database.models.Customer'>.balance as Sum(Order.amount_total Where Rule.sum(derive=Customer.balance, as_sum_of=Order.amount_total, where=lambda row: row.date_shipped is None) - <function declare_logic.<locals>.<lambda> at 0x108fed080>)  
  Item  
    2. Derive <class 'database.models.Item'>.amount as Formula (1): <function>  
    3. Derive <class 'database.models.Item'>.unit_price as Copy(product.unit_price)  
  Order  
    4. Derive <class 'database.models.Order'>.amount_total as Sum(Item.amount Where  - None)  
    5. RowEvent Order.send_order_to_shipping()   
```
**Logic Log** in Scenario: Product Unit Price Copied to Item
```

Product Unit Price Copied to Ite
 - 2025-10-20 11:28:01,856 - logic_logger - INF

Logic Phase:		ROW LOGIC		(session=0x10a00f240) (sqlalchemy before_flush)			 - 2025-10-20 11:28:01,858 - logic_logger - INF
..Customer[173] {Update - client} id: 173, name: PriceCopy 1760984881852, balance: 0E-10, credit_limit: 3000.0000000000, email: None, email_opt_out: None  row: 0x10a2802d0  session: 0x10a00f240  ins_upd_dlt: upd, initial: upd - 2025-10-20 11:28:01,858 - logic_logger - INF
Logic Phase:		COMMIT LOGIC		(session=0x10a00f240)   										 - 2025-10-20 11:28:01,858 - logic_logger - INF
Logic Phase:		AFTER_FLUSH LOGIC	(session=0x10a00f240)   										 - 2025-10-20 11:28:01,858 - logic_logger - INF

```
</details>
  
&nbsp;
&nbsp;
### Scenario: Change Product Updates Unit Price (FK Change)
&emsp;  Scenario: Change Product Updates Unit Price (FK Change)  
&emsp;&emsp;    Given Customer "ProductChange" with balance 0 and credit limit 5000  
    And Order exists for "ProductChange" with 2 Widget  
&emsp;&emsp;    When Item product changed to "Gadget"  
&emsp;&emsp;    Then Item unit_price should be 150  
    And Item amount should be 300  
    And Order amount_total should be 300  
<details markdown>
<summary>Tests - and their logic - are transparent.. click to see Logic</summary>


&nbsp;
&nbsp;


**Rules Used** in Scenario: Change Product Updates Unit Price (FK Change)
```
  Customer  
    1. Derive <class 'database.models.Customer'>.balance as Sum(Order.amount_total Where Rule.sum(derive=Customer.balance, as_sum_of=Order.amount_total, where=lambda row: row.date_shipped is None) - <function declare_logic.<locals>.<lambda> at 0x108fed080>)  
  Item  
    2. Derive <class 'database.models.Item'>.amount as Formula (1): <function>  
    3. Derive <class 'database.models.Item'>.unit_price as Copy(product.unit_price)  
  Order  
    4. Derive <class 'database.models.Order'>.amount_total as Sum(Item.amount Where  - None)  
    5. RowEvent Order.send_order_to_shipping()   
```
**Logic Log** in Scenario: Change Product Updates Unit Price (FK Change)
```

Change Product Updates Unit Price (FK Change
 - 2025-10-20 11:28:01,882 - logic_logger - INF

Logic Phase:		ROW LOGIC		(session=0x10a00f460) (sqlalchemy before_flush)			 - 2025-10-20 11:28:01,885 - logic_logger - INF
..Item[156] {Update - client} id: 156, order_id: 139, product_id:  [2-->] 1, quantity: 2, amount: 180.0000000000, unit_price: 90.0000000000  row: 0x10a262350  session: 0x10a00f460  ins_upd_dlt: upd, initial: upd - 2025-10-20 11:28:01,885 - logic_logger - INF
..Item[156] {copy_rules for role: product - unit_price} id: 156, order_id: 139, product_id:  [2-->] 1, quantity: 2, amount: 180.0000000000, unit_price:  [90.0000000000-->] 150.0000000000  row: 0x10a262350  session: 0x10a00f460  ins_upd_dlt: upd, initial: upd - 2025-10-20 11:28:01,885 - logic_logger - INF
..Item[156] {Formula amount} id: 156, order_id: 139, product_id:  [2-->] 1, quantity: 2, amount:  [180.0000000000-->] 300.0000000000, unit_price:  [90.0000000000-->] 150.0000000000  row: 0x10a262350  session: 0x10a00f460  ins_upd_dlt: upd, initial: upd - 2025-10-20 11:28:01,885 - logic_logger - INF
....Order[139] {Update - Adjusting order: amount_total} id: 139, notes: Test order, customer_id: 174, CreatedOn: 2025-10-20, date_shipped: None, amount_total:  [180.0000000000-->] 300.0000000000  row: 0x10a261dd0  session: 0x10a00f460  ins_upd_dlt: upd, initial: upd - 2025-10-20 11:28:01,886 - logic_logger - INF
......Customer[174] {Update - Adjusting customer: balance} id: 174, name: ProductChange 1760984881868, balance:  [180.0000000000-->] 300.0000000000, credit_limit: 5000.0000000000, email: None, email_opt_out: None  row: 0x10a064250  session: 0x10a00f460  ins_upd_dlt: upd, initial: upd - 2025-10-20 11:28:01,886 - logic_logger - INF
Logic Phase:		COMMIT LOGIC		(session=0x10a00f460)   										 - 2025-10-20 11:28:01,886 - logic_logger - INF
Logic Phase:		AFTER_FLUSH LOGIC	(session=0x10a00f460)   										 - 2025-10-20 11:28:01,887 - logic_logger - INF
....Order[139] {AfterFlush Event} id: 139, notes: Test order, customer_id: 174, CreatedOn: 2025-10-20, date_shipped: None, amount_total:  [180.0000000000-->] 300.0000000000  row: 0x10a261dd0  session: 0x10a00f460  ins_upd_dlt: upd, initial: upd - 2025-10-20 11:28:01,887 - logic_logger - INF

```
</details>
  
&nbsp;&nbsp;  
/Users/val/dev/ApiLogicServer/ApiLogicServer-dev/build_and_test/ApiLogicServer/basic_demo_2/test/api_logic_server_behave/behave_run.py completed at October 20, 2025 11:28:0  