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
```
</details>
  
&nbsp;
&nbsp;
## Feature: Check Credit Rules  
  
&nbsp;
&nbsp;
### Scenario: Good Order - balance updated
&emsp;  Scenario: Good Order - balance updated  
&emsp;&emsp;    Given Customer with credit limit 1000  
&emsp;&emsp;    When Order is placed with 2 Chai  
&emsp;&emsp;    Then Customer balance is 36.0  
<details markdown>
<summary>Tests - and their logic - are transparent.. click to see Logic</summary>


&nbsp;
&nbsp;


**Rules Used** in Scenario: Good Order - balance updated
```
  Customer  
    1. Derive <class 'database.models.Customer'>.balance as Sum(Order.amount_total Where Rule.sum(derive=models.Customer.balance, as_sum_of=models.Order.amount_total, where=lambda row: row.date_shipped is None) - <function declare_logic.<locals>.<lambda> at 0x109311120>)  
  Item  
    2. Derive <class 'database.models.Item'>.amount as Formula (1): Rule.formula(derive=models.Item.amount, as_expres [...]  
    3. Derive <class 'database.models.Item'>.unit_price as Copy(product.unit_price)  
  Order  
    4. RowEvent Order.send_row_to_kafka()   
    5. Derive <class 'database.models.Order'>.amount_total as Sum(Item.amount Where  - None)  
```
**Logic Log** in Scenario: Good Order - balance updated
```
Logic Phase:		ROW LOGIC		(session=0x10a783460) (sqlalchemy before_flush)			 - 2026-05-23 07:42:46,218 - logic_logger - INF
..Item[None] {Insert - client} id: None, order_id: 19, product_id: 1, quantity: 2, unit_price: 18.0, amount: None  row: 0x10a797850  session: 0x10a783460  ins_upd_dlt: ins, initial: ins - 2026-05-23 07:42:46,218 - logic_logger - INF
..Item[None] {server_defaults: amount } id: None, order_id: 19, product_id: 1, quantity: 2, unit_price: 18.0, amount: 0.0  row: 0x10a797850  session: 0x10a783460  ins_upd_dlt: ins, initial: ins - 2026-05-23 07:42:46,218 - logic_logger - INF
..Item[None] {copy_rules for role: product - unit_price} id: None, order_id: 19, product_id: 1, quantity: 2, unit_price: 18.0, amount: 0.0  row: 0x10a797850  session: 0x10a783460  ins_upd_dlt: ins, initial: ins - 2026-05-23 07:42:46,219 - logic_logger - INF
..Item[None] {Formula amount} id: None, order_id: 19, product_id: 1, quantity: 2, unit_price: 18.0, amount: 36.0  row: 0x10a797850  session: 0x10a783460  ins_upd_dlt: ins, initial: ins - 2026-05-23 07:42:46,219 - logic_logger - INF
....Order[19] {Update - Adjusting order: amount_total} id: 19, customer_id: 18, date_ordered: None, date_shipped: None, notes: None, amount_total:  [0.0-->] 36.0  row: 0x10b080350  session: 0x10a783460  ins_upd_dlt: upd, initial: upd - 2026-05-23 07:42:46,219 - logic_logger - INF
......Customer[18] {Update - Adjusting customer: balance} id: 18, name: Test 1779547366209, email: None, credit_limit: 1000.0, balance:  [0.0-->] 36.0  row: 0x10b0806d0  session: 0x10a783460  ins_upd_dlt: upd, initial: upd - 2026-05-23 07:42:46,219 - logic_logger - INF
Logic Phase:		COMMIT LOGIC		(session=0x10a783460)   										 - 2026-05-23 07:42:46,219 - logic_logger - INF
Logic Phase:		AFTER_FLUSH LOGIC	(session=0x10a783460)   										 - 2026-05-23 07:42:46,220 - logic_logger - INF
....Order[19] {AfterFlush Event} id: 19, customer_id: 18, date_ordered: None, date_shipped: None, notes: None, amount_total:  [0.0-->] 36.0  row: 0x10b080350  session: 0x10a783460  ins_upd_dlt: upd, initial: upd - 2026-05-23 07:42:46,220 - logic_logger - INF
....Order[19] {Sending Order to Kafka topic 'order_shipping' [Note: **Kafka not enabled** ]} id: 19, customer_id: 18, date_ordered: None, date_shipped: None, notes: None, amount_total:  [0.0-->] 36.0  row: 0x10b080350  session: 0x10a783460  ins_upd_dlt: upd, initial: upd - 2026-05-23 07:42:46,220 - logic_logger - INF

```
</details>
  
&nbsp;
&nbsp;
### Scenario: Exceed Credit Limit - rejected
&emsp;  Scenario: Exceed Credit Limit - rejected  
&emsp;&emsp;    Given Customer with credit limit 20  
&emsp;&emsp;    When Order is placed with 2 Chai  
&emsp;&emsp;    Then Order is rejected with credit limit error  
<details markdown>
<summary>Tests - and their logic - are transparent.. click to see Logic</summary>


&nbsp;
&nbsp;


**Rules Used** in Scenario: Exceed Credit Limit - rejected
```
  Customer  
    1. Constraint Function: None   
    2. Derive <class 'database.models.Customer'>.balance as Sum(Order.amount_total Where Rule.sum(derive=models.Customer.balance, as_sum_of=models.Order.amount_total, where=lambda row: row.date_shipped is None) - <function declare_logic.<locals>.<lambda> at 0x109311120>)  
  Item  
    3. Derive <class 'database.models.Item'>.amount as Formula (1): Rule.formula(derive=models.Item.amount, as_expres [...]  
    4. Derive <class 'database.models.Item'>.unit_price as Copy(product.unit_price)  
  Order  
    5. Derive <class 'database.models.Order'>.amount_total as Sum(Item.amount Where  - None)  
```
**Logic Log** in Scenario: Exceed Credit Limit - rejected
```
Logic Phase:		ROW LOGIC		(session=0x10a783570) (sqlalchemy before_flush)			 - 2026-05-23 07:42:46,231 - logic_logger - INF
..Item[None] {Insert - client} id: None, order_id: 20, product_id: 1, quantity: 2, unit_price: 18.0, amount: None  row: 0x10b0825d0  session: 0x10a783570  ins_upd_dlt: ins, initial: ins - 2026-05-23 07:42:46,232 - logic_logger - INF
..Item[None] {server_defaults: amount } id: None, order_id: 20, product_id: 1, quantity: 2, unit_price: 18.0, amount: 0.0  row: 0x10b0825d0  session: 0x10a783570  ins_upd_dlt: ins, initial: ins - 2026-05-23 07:42:46,232 - logic_logger - INF
..Item[None] {copy_rules for role: product - unit_price} id: None, order_id: 20, product_id: 1, quantity: 2, unit_price: 18.0, amount: 0.0  row: 0x10b0825d0  session: 0x10a783570  ins_upd_dlt: ins, initial: ins - 2026-05-23 07:42:46,232 - logic_logger - INF
..Item[None] {Formula amount} id: None, order_id: 20, product_id: 1, quantity: 2, unit_price: 18.0, amount: 36.0  row: 0x10b0825d0  session: 0x10a783570  ins_upd_dlt: ins, initial: ins - 2026-05-23 07:42:46,232 - logic_logger - INF
....Order[20] {Update - Adjusting order: amount_total} id: 20, customer_id: 19, date_ordered: None, date_shipped: None, notes: None, amount_total:  [0.0-->] 36.0  row: 0x10b080d50  session: 0x10a783570  ins_upd_dlt: upd, initial: upd - 2026-05-23 07:42:46,232 - logic_logger - INF
......Customer[19] {Update - Adjusting customer: balance} id: 19, name: Test 1779547366224, email: None, credit_limit: 20.0, balance:  [0.0-->] 36.0  row: 0x10a7d3ad0  session: 0x10a783570  ins_upd_dlt: upd, initial: upd - 2026-05-23 07:42:46,233 - logic_logger - INF
......Customer[19] {Constraint Failure: Customer balance (36.0) exceeds credit limit (20.0)} id: 19, name: Test 1779547366224, email: None, credit_limit: 20.0, balance:  [0.0-->] 36.0  row: 0x10a7d3ad0  session: 0x10a783570  ins_upd_dlt: upd, initial: upd - 2026-05-23 07:42:46,233 - logic_logger - INF

```
</details>
  
&nbsp;
&nbsp;
### Scenario: Item Quantity Change - recalculates
&emsp;  Scenario: Item Quantity Change - recalculates  
&emsp;&emsp;    Given Customer with credit limit 1000  
    And Order is placed with 2 Chai  
&emsp;&emsp;    When Item quantity changed to 5  
&emsp;&emsp;    Then Item amount is 90.0  
&emsp;&emsp;    Then Order amount_total is 90.0  
<details markdown>
<summary>Tests - and their logic - are transparent.. click to see Logic</summary>


&nbsp;
&nbsp;


**Rules Used** in Scenario: Item Quantity Change - recalculates
```
  Customer  
    1. Derive <class 'database.models.Customer'>.balance as Sum(Order.amount_total Where Rule.sum(derive=models.Customer.balance, as_sum_of=models.Order.amount_total, where=lambda row: row.date_shipped is None) - <function declare_logic.<locals>.<lambda> at 0x109311120>)  
  Item  
    2. Derive <class 'database.models.Item'>.amount as Formula (1): Rule.formula(derive=models.Item.amount, as_expres [...]  
    3. Derive <class 'database.models.Item'>.unit_price as Copy(product.unit_price)  
  Order  
    4. RowEvent Order.send_row_to_kafka()   
    5. Derive <class 'database.models.Order'>.amount_total as Sum(Item.amount Where  - None)  
```
**Logic Log** in Scenario: Item Quantity Change - recalculates
```
Logic Phase:		ROW LOGIC		(session=0x10a782470) (sqlalchemy before_flush)			 - 2026-05-23 07:42:46,243 - logic_logger - INF
..Item[None] {Insert - client} id: None, order_id: 21, product_id: 1, quantity: 2, unit_price: 18.0, amount: None  row: 0x10a7d31d0  session: 0x10a782470  ins_upd_dlt: ins, initial: ins - 2026-05-23 07:42:46,243 - logic_logger - INF
..Item[None] {server_defaults: amount } id: None, order_id: 21, product_id: 1, quantity: 2, unit_price: 18.0, amount: 0.0  row: 0x10a7d31d0  session: 0x10a782470  ins_upd_dlt: ins, initial: ins - 2026-05-23 07:42:46,243 - logic_logger - INF
..Item[None] {copy_rules for role: product - unit_price} id: None, order_id: 21, product_id: 1, quantity: 2, unit_price: 18.0, amount: 0.0  row: 0x10a7d31d0  session: 0x10a782470  ins_upd_dlt: ins, initial: ins - 2026-05-23 07:42:46,244 - logic_logger - INF
..Item[None] {Formula amount} id: None, order_id: 21, product_id: 1, quantity: 2, unit_price: 18.0, amount: 36.0  row: 0x10a7d31d0  session: 0x10a782470  ins_upd_dlt: ins, initial: ins - 2026-05-23 07:42:46,244 - logic_logger - INF
....Order[21] {Update - Adjusting order: amount_total} id: 21, customer_id: 20, date_ordered: None, date_shipped: None, notes: None, amount_total:  [0.0-->] 36.0  row: 0x10a7d25d0  session: 0x10a782470  ins_upd_dlt: upd, initial: upd - 2026-05-23 07:42:46,244 - logic_logger - INF
......Customer[20] {Update - Adjusting customer: balance} id: 20, name: Test 1779547366236, email: None, credit_limit: 1000.0, balance:  [0.0-->] 36.0  row: 0x10b0836d0  session: 0x10a782470  ins_upd_dlt: upd, initial: upd - 2026-05-23 07:42:46,244 - logic_logger - INF
Logic Phase:		COMMIT LOGIC		(session=0x10a782470)   										 - 2026-05-23 07:42:46,244 - logic_logger - INF
Logic Phase:		AFTER_FLUSH LOGIC	(session=0x10a782470)   										 - 2026-05-23 07:42:46,245 - logic_logger - INF
....Order[21] {AfterFlush Event} id: 21, customer_id: 20, date_ordered: None, date_shipped: None, notes: None, amount_total:  [0.0-->] 36.0  row: 0x10a7d25d0  session: 0x10a782470  ins_upd_dlt: upd, initial: upd - 2026-05-23 07:42:46,245 - logic_logger - INF
....Order[21] {Sending Order to Kafka topic 'order_shipping' [Note: **Kafka not enabled** ]} id: 21, customer_id: 20, date_ordered: None, date_shipped: None, notes: None, amount_total:  [0.0-->] 36.0  row: 0x10a7d25d0  session: 0x10a782470  ins_upd_dlt: upd, initial: upd - 2026-05-23 07:42:46,245 - logic_logger - INF

```
</details>
  
&nbsp;
&nbsp;
### Scenario: Delete Item - reduces order total
&emsp;  Scenario: Delete Item - reduces order total  
&emsp;&emsp;    Given Customer with credit limit 1000  
    And Order is placed with 2 Chai and 1 Chang  
&emsp;&emsp;    When Item is deleted  
&emsp;&emsp;    Then Order amount_total is 19.0  
<details markdown>
<summary>Tests - and their logic - are transparent.. click to see Logic</summary>


&nbsp;
&nbsp;


**Rules Used** in Scenario: Delete Item - reduces order total
```
  Customer  
    1. Derive <class 'database.models.Customer'>.balance as Sum(Order.amount_total Where Rule.sum(derive=models.Customer.balance, as_sum_of=models.Order.amount_total, where=lambda row: row.date_shipped is None) - <function declare_logic.<locals>.<lambda> at 0x109311120>)  
  Item  
    2. Derive <class 'database.models.Item'>.amount as Formula (1): Rule.formula(derive=models.Item.amount, as_expres [...]  
    3. Derive <class 'database.models.Item'>.unit_price as Copy(product.unit_price)  
  Order  
    4. RowEvent Order.send_row_to_kafka()   
    5. Derive <class 'database.models.Order'>.amount_total as Sum(Item.amount Where  - None)  
```
**Logic Log** in Scenario: Delete Item - reduces order total
```
Logic Phase:		ROW LOGIC		(session=0x10a781e10) (sqlalchemy before_flush)			 - 2026-05-23 07:42:46,261 - logic_logger - INF
..Item[None] {Insert - client} id: None, order_id: 22, product_id: 1, quantity: 2, unit_price: 18.0, amount: None  row: 0x10b080850  session: 0x10a781e10  ins_upd_dlt: ins, initial: ins - 2026-05-23 07:42:46,261 - logic_logger - INF
..Item[None] {server_defaults: amount } id: None, order_id: 22, product_id: 1, quantity: 2, unit_price: 18.0, amount: 0.0  row: 0x10b080850  session: 0x10a781e10  ins_upd_dlt: ins, initial: ins - 2026-05-23 07:42:46,261 - logic_logger - INF
..Item[None] {copy_rules for role: product - unit_price} id: None, order_id: 22, product_id: 1, quantity: 2, unit_price: 18.0, amount: 0.0  row: 0x10b080850  session: 0x10a781e10  ins_upd_dlt: ins, initial: ins - 2026-05-23 07:42:46,262 - logic_logger - INF
..Item[None] {Formula amount} id: None, order_id: 22, product_id: 1, quantity: 2, unit_price: 18.0, amount: 36.0  row: 0x10b080850  session: 0x10a781e10  ins_upd_dlt: ins, initial: ins - 2026-05-23 07:42:46,262 - logic_logger - INF
....Order[22] {Update - Adjusting order: amount_total} id: 22, customer_id: 21, date_ordered: None, date_shipped: None, notes: None, amount_total:  [0.0-->] 36.0  row: 0x10b0838d0  session: 0x10a781e10  ins_upd_dlt: upd, initial: upd - 2026-05-23 07:42:46,262 - logic_logger - INF
......Customer[21] {Update - Adjusting customer: balance} id: 21, name: Test 1779547366254, email: None, credit_limit: 1000.0, balance:  [0.0-->] 36.0  row: 0x10b080350  session: 0x10a781e10  ins_upd_dlt: upd, initial: upd - 2026-05-23 07:42:46,262 - logic_logger - INF
Logic Phase:		COMMIT LOGIC		(session=0x10a781e10)   										 - 2026-05-23 07:42:46,262 - logic_logger - INF
Logic Phase:		AFTER_FLUSH LOGIC	(session=0x10a781e10)   										 - 2026-05-23 07:42:46,263 - logic_logger - INF
....Order[22] {AfterFlush Event} id: 22, customer_id: 21, date_ordered: None, date_shipped: None, notes: None, amount_total:  [0.0-->] 36.0  row: 0x10b0838d0  session: 0x10a781e10  ins_upd_dlt: upd, initial: upd - 2026-05-23 07:42:46,263 - logic_logger - INF
....Order[22] {Sending Order to Kafka topic 'order_shipping' [Note: **Kafka not enabled** ]} id: 22, customer_id: 21, date_ordered: None, date_shipped: None, notes: None, amount_total:  [0.0-->] 36.0  row: 0x10b0838d0  session: 0x10a781e10  ins_upd_dlt: upd, initial: upd - 2026-05-23 07:42:46,263 - logic_logger - INF

```
</details>
  
&nbsp;
&nbsp;
### Scenario: Ship Order - excluded from balance
&emsp;  Scenario: Ship Order - excluded from balance  
&emsp;&emsp;    Given Customer with credit limit 1000  
    And Order is placed with 2 Chai  
&emsp;&emsp;    When Order is shipped  
&emsp;&emsp;    Then Customer balance is 0.0  
<details markdown>
<summary>Tests - and their logic - are transparent.. click to see Logic</summary>


&nbsp;
&nbsp;


**Rules Used** in Scenario: Ship Order - excluded from balance
```
  Customer  
    1. Derive <class 'database.models.Customer'>.balance as Sum(Order.amount_total Where Rule.sum(derive=models.Customer.balance, as_sum_of=models.Order.amount_total, where=lambda row: row.date_shipped is None) - <function declare_logic.<locals>.<lambda> at 0x109311120>)  
  Item  
    2. Derive <class 'database.models.Item'>.amount as Formula (1): Rule.formula(derive=models.Item.amount, as_expres [...]  
    3. Derive <class 'database.models.Item'>.unit_price as Copy(product.unit_price)  
  Order  
    4. RowEvent Order.send_row_to_kafka()   
    5. Derive <class 'database.models.Order'>.amount_total as Sum(Item.amount Where  - None)  
```
**Logic Log** in Scenario: Ship Order - excluded from balance
```
Logic Phase:		ROW LOGIC		(session=0x10a781590) (sqlalchemy before_flush)			 - 2026-05-23 07:42:46,282 - logic_logger - INF
..Item[None] {Insert - client} id: None, order_id: 23, product_id: 1, quantity: 2, unit_price: 18.0, amount: None  row: 0x10a7d0e50  session: 0x10a781590  ins_upd_dlt: ins, initial: ins - 2026-05-23 07:42:46,282 - logic_logger - INF
..Item[None] {server_defaults: amount } id: None, order_id: 23, product_id: 1, quantity: 2, unit_price: 18.0, amount: 0.0  row: 0x10a7d0e50  session: 0x10a781590  ins_upd_dlt: ins, initial: ins - 2026-05-23 07:42:46,282 - logic_logger - INF
..Item[None] {copy_rules for role: product - unit_price} id: None, order_id: 23, product_id: 1, quantity: 2, unit_price: 18.0, amount: 0.0  row: 0x10a7d0e50  session: 0x10a781590  ins_upd_dlt: ins, initial: ins - 2026-05-23 07:42:46,283 - logic_logger - INF
..Item[None] {Formula amount} id: None, order_id: 23, product_id: 1, quantity: 2, unit_price: 18.0, amount: 36.0  row: 0x10a7d0e50  session: 0x10a781590  ins_upd_dlt: ins, initial: ins - 2026-05-23 07:42:46,283 - logic_logger - INF
....Order[23] {Update - Adjusting order: amount_total} id: 23, customer_id: 22, date_ordered: None, date_shipped: None, notes: None, amount_total:  [0.0-->] 36.0  row: 0x10a7d20d0  session: 0x10a781590  ins_upd_dlt: upd, initial: upd - 2026-05-23 07:42:46,283 - logic_logger - INF
......Customer[22] {Update - Adjusting customer: balance} id: 22, name: Test 1779547366274, email: None, credit_limit: 1000.0, balance:  [0.0-->] 36.0  row: 0x10b082b50  session: 0x10a781590  ins_upd_dlt: upd, initial: upd - 2026-05-23 07:42:46,283 - logic_logger - INF
Logic Phase:		COMMIT LOGIC		(session=0x10a781590)   										 - 2026-05-23 07:42:46,283 - logic_logger - INF
Logic Phase:		AFTER_FLUSH LOGIC	(session=0x10a781590)   										 - 2026-05-23 07:42:46,283 - logic_logger - INF
....Order[23] {AfterFlush Event} id: 23, customer_id: 22, date_ordered: None, date_shipped: None, notes: None, amount_total:  [0.0-->] 36.0  row: 0x10a7d20d0  session: 0x10a781590  ins_upd_dlt: upd, initial: upd - 2026-05-23 07:42:46,283 - logic_logger - INF
....Order[23] {Sending Order to Kafka topic 'order_shipping' [Note: **Kafka not enabled** ]} id: 23, customer_id: 22, date_ordered: None, date_shipped: None, notes: None, amount_total:  [0.0-->] 36.0  row: 0x10a7d20d0  session: 0x10a781590  ins_upd_dlt: upd, initial: upd - 2026-05-23 07:42:46,283 - logic_logger - INF

```
</details>
  
&nbsp;
&nbsp;
### Scenario: Unship Order - included in balance
&emsp;  Scenario: Unship Order - included in balance  
&emsp;&emsp;    Given Customer with credit limit 1000  
    And Shipped order is created with 2 Chai  
&emsp;&emsp;    When Order is unshipped  
&emsp;&emsp;    Then Customer balance is 36.0  
<details markdown>
<summary>Tests - and their logic - are transparent.. click to see Logic</summary>


&nbsp;
&nbsp;


**Rules Used** in Scenario: Unship Order - included in balance
```
  Customer  
    1. Derive <class 'database.models.Customer'>.balance as Sum(Order.amount_total Where Rule.sum(derive=models.Customer.balance, as_sum_of=models.Order.amount_total, where=lambda row: row.date_shipped is None) - <function declare_logic.<locals>.<lambda> at 0x109311120>)  
  Item  
    2. Derive <class 'database.models.Item'>.amount as Formula (1): Rule.formula(derive=models.Item.amount, as_expres [...]  
    3. Derive <class 'database.models.Item'>.unit_price as Copy(product.unit_price)  
  Order  
    4. RowEvent Order.send_row_to_kafka()   
    5. Derive <class 'database.models.Order'>.amount_total as Sum(Item.amount Where  - None)  
```
**Logic Log** in Scenario: Unship Order - included in balance
```
Logic Phase:		ROW LOGIC		(session=0x10a782360) (sqlalchemy before_flush)			 - 2026-05-23 07:42:46,297 - logic_logger - INF
..Item[None] {Insert - client} id: None, order_id: 24, product_id: 1, quantity: 2, unit_price: 18.0, amount: None  row: 0x10a797850  session: 0x10a782360  ins_upd_dlt: ins, initial: ins - 2026-05-23 07:42:46,297 - logic_logger - INF
..Item[None] {server_defaults: amount } id: None, order_id: 24, product_id: 1, quantity: 2, unit_price: 18.0, amount: 0.0  row: 0x10a797850  session: 0x10a782360  ins_upd_dlt: ins, initial: ins - 2026-05-23 07:42:46,297 - logic_logger - INF
..Item[None] {copy_rules for role: product - unit_price} id: None, order_id: 24, product_id: 1, quantity: 2, unit_price: 18.0, amount: 0.0  row: 0x10a797850  session: 0x10a782360  ins_upd_dlt: ins, initial: ins - 2026-05-23 07:42:46,298 - logic_logger - INF
..Item[None] {Formula amount} id: None, order_id: 24, product_id: 1, quantity: 2, unit_price: 18.0, amount: 36.0  row: 0x10a797850  session: 0x10a782360  ins_upd_dlt: ins, initial: ins - 2026-05-23 07:42:46,298 - logic_logger - INF
....Order[24] {Update - Adjusting order: amount_total} id: 24, customer_id: 23, date_ordered: None, date_shipped: None, notes: None, amount_total:  [0.0-->] 36.0  row: 0x10b0803d0  session: 0x10a782360  ins_upd_dlt: upd, initial: upd - 2026-05-23 07:42:46,298 - logic_logger - INF
......Customer[23] {Update - Adjusting customer: balance} id: 23, name: Test 1779547366290, email: None, credit_limit: 1000.0, balance:  [0.0-->] 36.0  row: 0x10b0816d0  session: 0x10a782360  ins_upd_dlt: upd, initial: upd - 2026-05-23 07:42:46,298 - logic_logger - INF
Logic Phase:		COMMIT LOGIC		(session=0x10a782360)   										 - 2026-05-23 07:42:46,299 - logic_logger - INF
Logic Phase:		AFTER_FLUSH LOGIC	(session=0x10a782360)   										 - 2026-05-23 07:42:46,299 - logic_logger - INF
....Order[24] {AfterFlush Event} id: 24, customer_id: 23, date_ordered: None, date_shipped: None, notes: None, amount_total:  [0.0-->] 36.0  row: 0x10b0803d0  session: 0x10a782360  ins_upd_dlt: upd, initial: upd - 2026-05-23 07:42:46,299 - logic_logger - INF
....Order[24] {Sending Order to Kafka topic 'order_shipping' [Note: **Kafka not enabled** ]} id: 24, customer_id: 23, date_ordered: None, date_shipped: None, notes: None, amount_total:  [0.0-->] 36.0  row: 0x10b0803d0  session: 0x10a782360  ins_upd_dlt: upd, initial: upd - 2026-05-23 07:42:46,299 - logic_logger - INF

```
</details>
  
&nbsp;&nbsp;  
/Users/val/dev/ApiLogicServer/ApiLogicServer-dev/build_and_test/genai-logic/basic_demo/test/api_logic_server_behave/behave_run.py completed at May 23, 2026 07:42:4  