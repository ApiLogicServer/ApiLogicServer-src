Create basic_demo_rule_reuse from samples/dbs/basic_demo.sqlite

Include a notes field for orders.

On Placing Orders, Check Credit    
    1. The Customer's balance is less than the credit limit
    2. The Customer's balance is the sum of the unshipped Order amount_total
    3. The Order's amount_total is the sum of the Item amount
    4. The Item amount is the quantity * unit_price
    5. The Item unit_price is copied from the Product unit_price

Use case: App Integration
    1. Publish the Order to Kafka topic 'order_shipping' when the date_shipped becomes not None.

On Moving Orders to a different Customer, Check Credit
    1. Recompute the customers balances as the sum of the unhipped order totals
    2. The Customer's balance must not exceed the credit limit
    Uses: Customer.balance (Check Credit), Customer.credit_limit_check (Check Credit)
