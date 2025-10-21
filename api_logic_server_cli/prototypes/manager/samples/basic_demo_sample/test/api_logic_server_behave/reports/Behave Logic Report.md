This report shows test results with embedded logic execution traces.

**For complete documentation on using Behave:** See [Behave.md](https://apilogicserver.github.io/Docs/Behave/)

**About This Project:**

_**TODO:** [Describe your project here - what it does, key features tested, etc.]_

&nbsp;

This report combines:

* Behave log (lists Features, test Scenarios, results), with embedded
* Logic showing rules executed, and how they operated

---

# Behave Logic Report
&nbsp;
&nbsp;
## Feature: About Sample  
  
&nbsp;
&nbsp;
### Scenario: Transaction Processing                           # features/about.feature:8

&emsp;  Scenario: Transaction Processing  
&emsp;&emsp;    **Given** Sample Database  
&emsp;&emsp;    **When** Transactions are submitted  
&emsp;&emsp;    **Then** Enforce business policies with Logic (rules + code)  
  
&nbsp;
&nbsp;
## Feature: Order Processing with Business Logic  
  
&nbsp;
&nbsp;
### Scenario: Good Order Placed                                   # features/order_processing.feature:3

&emsp;  Scenario: Good Order Placed  
&emsp;&emsp;    **Given** Customer "Alice" with balance 0 and credit limit 1000  
&emsp;&emsp;    **When** B2B order placed for "Alice" with 5 Widget  
&emsp;&emsp;    **Then** Customer "Alice" balance should be 450  
&emsp;&emsp;    **And** Order amount_total should be 450  
&emsp;&emsp;    **And** Item amount should be 450  
  
&nbsp;
&nbsp;
### Scenario: Increase Item Quantity                            # features/order_processing.feature:10

&emsp;  Scenario: Increase Item Quantity  
&emsp;&emsp;    **Given** Customer "Bob" with balance 0 and credit limit 2000  
&emsp;&emsp;    **And** Order exists for "Bob" with 5 Widget  
&emsp;&emsp;    **When** Item quantity changed to 10  
&emsp;&emsp;    **Then** Item amount should be 900  
&emsp;&emsp;    **And** Order amount_total should be 900  
&emsp;&emsp;    **And** Customer "Bob" balance should be 900  
  
&nbsp;
&nbsp;
### Scenario: Carbon Neutral Discount Applied                        # features/order_processing.feature:18

&emsp;  Scenario: Carbon Neutral Discount Applied  
&emsp;&emsp;    **Given** Customer "Carol" with balance 0 and credit limit 2000  
&emsp;&emsp;    **When** B2B order placed for "Carol" with 10 carbon neutral Green  
&emsp;&emsp;    **Then** Item amount should be 981  
&emsp;&emsp;    **And** Order amount_total should be 981  
&emsp;&emsp;    **And** Customer "Carol" balance should be 981  
<details markdown>
<summary>Tests - and their logic - are transparent.. click to see Logic</summary>


&nbsp;
&nbsp;


**Rules Used** in Scenario: Carbon Neutral Discount Applied            # features/order_processing.feature:18
```
  Customer  
    1. Derive <class 'database.models.Customer'>.balance as Sum(Order.amount_total Where Rule.sum(derive=Customer.balance, as_sum_of=Order.amount_total, where=lambda row: row.date_shipped is None) - <function declare_logic.<locals>.<lambda> at 0x10c5f8cc0>)  
  Item  
    2. Derive <class 'database.models.Item'>.amount as Formula (1): <function>  
    3. Derive <class 'database.models.Item'>.unit_price as Copy(product.unit_price)  
  Order  
    4. Derive <class 'database.models.Order'>.amount_total as Sum(Item.amount Where  - None)  
    5. RowEvent Order.send_order_to_shipping()   
```
**Logic Log** in Scenario: Carbon Neutral Discount Applied            # features/order_processing.feature:18
```

Carbon Neutral Discount Applie
 - 2025-10-20 19:17:14,919 - logic_logger - INF

Logic Phase:		ROW LOGIC		(session=0x10d61bbd0) (sqlalchemy before_flush)			 - 2025-10-20 19:17:14,921 - logic_logger - INF
..Customer[43] {Update - client} id: 43, name: Carol 1761013034915, balance: 0E-10, credit_limit: 2000.0000000000, email: None, email_opt_out: None  row: 0x10d6e4250  session: 0x10d61bbd0  ins_upd_dlt: upd, initial: upd - 2025-10-20 19:17:14,921 - logic_logger - INF
Logic Phase:		COMMIT LOGIC		(session=0x10d61bbd0)   										 - 2025-10-20 19:17:14,921 - logic_logger - INF
Logic Phase:		AFTER_FLUSH LOGIC	(session=0x10d61bbd0)   										 - 2025-10-20 19:17:14,921 - logic_logger - INF

```
</details>
  
&nbsp;
&nbsp;
### Scenario: Change Order Customer                              # features/order_processing.feature:25

&emsp;  Scenario: Change Order Customer  
&emsp;&emsp;    **Given** Customer "Dave" with balance 0 and credit limit 1500  
&emsp;&emsp;    **And** Customer "Eve" with balance 0 and credit limit 1500  
&emsp;&emsp;    **And** Order exists for "Dave" with 5 Widget  
&emsp;&emsp;    **When** Order customer changed to "Eve"  
&emsp;&emsp;    **Then** Customer "Dave" balance should be 0  
&emsp;&emsp;    **And** Customer "Eve" balance should be 450  
  
&nbsp;
&nbsp;
### Scenario: Delete Item Reduces Totals                          # features/order_processing.feature:33

&emsp;  Scenario: Delete Item Reduces Totals  
&emsp;&emsp;    **Given** Customer "Frank" with balance 0 and credit limit 1500  
&emsp;&emsp;    **And** Order exists for "Frank" with 3 Widget and 2 Gadget  
&emsp;&emsp;    **When** First item deleted  
&emsp;&emsp;    **Then** Order amount_total should be 300  
&emsp;&emsp;    **And** Customer "Frank" balance should be 300  
<details markdown>
<summary>Tests - and their logic - are transparent.. click to see Logic</summary>


&nbsp;
&nbsp;


**Rules Used** in Scenario: Delete Item Reduces Totals             # features/order_processing.feature:33
```
  Customer  
    1. Derive <class 'database.models.Customer'>.balance as Sum(Order.amount_total Where Rule.sum(derive=Customer.balance, as_sum_of=Order.amount_total, where=lambda row: row.date_shipped is None) - <function declare_logic.<locals>.<lambda> at 0x10c5f8cc0>)  
  Item  
    2. Derive <class 'database.models.Item'>.amount as Formula (1): <function>  
    3. Derive <class 'database.models.Item'>.unit_price as Copy(product.unit_price)  
  Order  
    4. Derive <class 'database.models.Order'>.amount_total as Sum(Item.amount Where  - None)  
    5. RowEvent Order.send_order_to_shipping()   
```
**Logic Log** in Scenario: Delete Item Reduces Totals             # features/order_processing.feature:33
```

Delete Item Reduces Total
 - 2025-10-20 19:17:14,965 - logic_logger - INF

Logic Phase:		ROW LOGIC		(session=0x10d618af0) (sqlalchemy before_flush)			 - 2025-10-20 19:17:14,967 - logic_logger - INF
..Customer[46] {Update - client} id: 46, name: Frank 1761013034961, balance: 0E-10, credit_limit: 1500.0000000000, email: None, email_opt_out: None  row: 0x10d8836d0  session: 0x10d618af0  ins_upd_dlt: upd, initial: upd - 2025-10-20 19:17:14,967 - logic_logger - INF
Logic Phase:		COMMIT LOGIC		(session=0x10d618af0)   										 - 2025-10-20 19:17:14,967 - logic_logger - INF
Logic Phase:		AFTER_FLUSH LOGIC	(session=0x10d618af0)   										 - 2025-10-20 19:17:14,967 - logic_logger - INF

```
</details>
  
&nbsp;
&nbsp;
### Scenario: Ship Order Excludes from Balance                    # features/order_processing.feature:40

&emsp;  Scenario: Ship Order Excludes from Balance  
&emsp;&emsp;    **Given** Customer "Grace" with balance 0 and credit limit 1000  
&emsp;&emsp;    **And** Order exists for "Grace" with 5 Widget  
&emsp;&emsp;    **When** Order shipped  
&emsp;&emsp;    **Then** Customer "Grace" balance should be 0  
<details markdown>
<summary>Tests - and their logic - are transparent.. click to see Logic</summary>


&nbsp;
&nbsp;


**Rules Used** in Scenario: Ship Order Excludes from Balance          # features/order_processing.feature:40
```
  Customer  
    1. Derive <class 'database.models.Customer'>.balance as Sum(Order.amount_total Where Rule.sum(derive=Customer.balance, as_sum_of=Order.amount_total, where=lambda row: row.date_shipped is None) - <function declare_logic.<locals>.<lambda> at 0x10c5f8cc0>)  
  Item  
    2. Derive <class 'database.models.Item'>.amount as Formula (1): <function>  
    3. Derive <class 'database.models.Item'>.unit_price as Copy(product.unit_price)  
  Order  
    4. Derive <class 'database.models.Order'>.amount_total as Sum(Item.amount Where  - None)  
    5. RowEvent Order.send_order_to_shipping()   
```
**Logic Log** in Scenario: Ship Order Excludes from Balance          # features/order_processing.feature:40
```

Ship Order Excludes from Balanc
 - 2025-10-20 19:17:14,989 - logic_logger - INF

Logic Phase:		ROW LOGIC		(session=0x10d618e20) (sqlalchemy before_flush)			 - 2025-10-20 19:17:14,991 - logic_logger - INF
..Customer[47] {Update - client} id: 47, name: Grace 1761013034985, balance: 0E-10, credit_limit: 1000.0000000000, email: None, email_opt_out: None  row: 0x10d6e4ed0  session: 0x10d618e20  ins_upd_dlt: upd, initial: upd - 2025-10-20 19:17:14,991 - logic_logger - INF
Logic Phase:		COMMIT LOGIC		(session=0x10d618e20)   										 - 2025-10-20 19:17:14,991 - logic_logger - INF
Logic Phase:		AFTER_FLUSH LOGIC	(session=0x10d618e20)   										 - 2025-10-20 19:17:14,991 - logic_logger - INF

```
</details>
  
&nbsp;
&nbsp;
### Scenario: Unship Order Includes in Balance                    # features/order_processing.feature:46

&emsp;  Scenario: Unship Order Includes in Balance  
&emsp;&emsp;    **Given** Customer "Henry" with balance 0 and credit limit 1000  
&emsp;&emsp;    **And** Shipped order exists for "Henry" with 5 Widget  
&emsp;&emsp;    **When** Order unshipped  
&emsp;&emsp;    **Then** Customer "Henry" balance should be 450  
<details markdown>
<summary>Tests - and their logic - are transparent.. click to see Logic</summary>


&nbsp;
&nbsp;


**Rules Used** in Scenario: Unship Order Includes in Balance          # features/order_processing.feature:46
```
  Customer  
    1. Derive <class 'database.models.Customer'>.balance as Sum(Order.amount_total Where Rule.sum(derive=Customer.balance, as_sum_of=Order.amount_total, where=lambda row: row.date_shipped is None) - <function declare_logic.<locals>.<lambda> at 0x10c5f8cc0>)  
  Order  
    2. RowEvent Order.send_order_to_shipping()   
```
**Logic Log** in Scenario: Unship Order Includes in Balance          # features/order_processing.feature:46
```

Unship Order Includes in Balanc
 - 2025-10-20 19:17:15,013 - logic_logger - INF

Logic Phase:		ROW LOGIC		(session=0x10d61a7a0) (sqlalchemy before_flush)			 - 2025-10-20 19:17:15,015 - logic_logger - INF
..Customer[48] {Update - client} id: 48, name: Henry 1761013035008, balance: 0E-10, credit_limit: 1000.0000000000, email: None, email_opt_out: None  row: 0x10d8a12d0  session: 0x10d61a7a0  ins_upd_dlt: upd, initial: upd - 2025-10-20 19:17:15,015 - logic_logger - INF
Logic Phase:		COMMIT LOGIC		(session=0x10d61a7a0)   										 - 2025-10-20 19:17:15,015 - logic_logger - INF
Logic Phase:		AFTER_FLUSH LOGIC	(session=0x10d61a7a0)   										 - 2025-10-20 19:17:15,015 - logic_logger - INF

```
</details>
  
&nbsp;
&nbsp;
### Scenario: Exceed Credit Limit                               # features/order_processing.feature:52

&emsp;  Scenario: Exceed Credit Limit  
&emsp;&emsp;    **Given** Customer "Ivan" with balance 0 and credit limit 100  
&emsp;&emsp;    **When** B2B order placed for "Ivan" with 5 Widget  
&emsp;&emsp;    **Then** Order creation should fail  
&emsp;&emsp;    **And** Error message should contain "credit limit"  
  
&nbsp;
&nbsp;
### Scenario: Change Product ID Re-copies Price                  # features/order_processing.feature:58

&emsp;  Scenario: Change Product ID Re-copies Price  
&emsp;&emsp;    **Given** Customer "Jane" with balance 0 and credit limit 2000  
&emsp;&emsp;    **And** Order exists for "Jane" with 5 Widget  
&emsp;&emsp;    **When** Item product changed to "Gadget"  
&emsp;&emsp;    **Then** Item unit_price should be 150  
&emsp;&emsp;    **And** Item amount should be 750  
&emsp;&emsp;    **And** Order amount_total should be 750  
&emsp;&emsp;    **And** Customer "Jane" balance should be 750  
<details markdown>
<summary>Tests - and their logic - are transparent.. click to see Logic</summary>


&nbsp;
&nbsp;


**Rules Used** in Scenario: Change Product ID Re-copies Price         # features/order_processing.feature:58
```
  Customer  
    1. Derive <class 'database.models.Customer'>.balance as Sum(Order.amount_total Where Rule.sum(derive=Customer.balance, as_sum_of=Order.amount_total, where=lambda row: row.date_shipped is None) - <function declare_logic.<locals>.<lambda> at 0x10c5f8cc0>)  
  Item  
    2. Derive <class 'database.models.Item'>.amount as Formula (1): <function>  
    3. Derive <class 'database.models.Item'>.unit_price as Copy(product.unit_price)  
  Order  
    4. Derive <class 'database.models.Order'>.amount_total as Sum(Item.amount Where  - None)  
    5. RowEvent Order.send_order_to_shipping()   
```
**Logic Log** in Scenario: Change Product ID Re-copies Price         # features/order_processing.feature:58
```

Change Product ID Re-copies Pric
 - 2025-10-20 19:17:15,051 - logic_logger - INF

Logic Phase:		ROW LOGIC		(session=0x10d61bac0) (sqlalchemy before_flush)			 - 2025-10-20 19:17:15,052 - logic_logger - INF
..Customer[50] {Update - client} id: 50, name: Jane 1761013035046, balance: 0E-10, credit_limit: 2000.0000000000, email: None, email_opt_out: None  row: 0x10d8a1250  session: 0x10d61bac0  ins_upd_dlt: upd, initial: upd - 2025-10-20 19:17:15,052 - logic_logger - INF
Logic Phase:		COMMIT LOGIC		(session=0x10d61bac0)   										 - 2025-10-20 19:17:15,052 - logic_logger - INF
Logic Phase:		AFTER_FLUSH LOGIC	(session=0x10d61bac0)   										 - 2025-10-20 19:17:15,053 - logic_logger - INF

```
</details>
  
&nbsp;
&nbsp;
### Scenario: Multi-Item Order Total                               # features/order_processing.feature:67

&emsp;  Scenario: Multi-Item Order Total  
&emsp;&emsp;    **Given** Customer "Kevin" with balance 0 and credit limit 2000  
&emsp;&emsp;    **When** B2B order placed for "Kevin" with 3 Widget and 2 Gadget  
&emsp;&emsp;    **Then** Order amount_total should be 570  
&emsp;&emsp;    **And** Customer "Kevin" balance should be 570  
  
&nbsp;&nbsp;  
/Users/val/dev/ApiLogicServer/ApiLogicServer-dev/build_and_test/ApiLogicServer/basic_demo/test/api_logic_server_behave/behave_run.py completed at October 20, 2025 19:17:1  