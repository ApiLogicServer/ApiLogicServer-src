// paste this into your AI Assistant:

Create basic_demo_sales_by_month with customers, orders, items and products.

Include a notes field for orders.

On Placing Orders, Check Credit 

    1. The Customer's balance is less than the credit limit
    2. The Customer's balance is the sum of the Order amount_total where date_shipped is null
    3. The Order's amount_total is the sum of the Item amount
    4. The Item amount is the quantity * unit_price
    5. The Item unit_price is copied from the Product unit_price

Use case: App Integration

    1. Publish the Order to Kafka topic 'order_shipping' when the date_shipped becomes not None.

On Placing Orders, maintain sales totals

    1. Orders can be assigned to people who are salesreps
    2. Maintain monthly sales totals and order counts for each sales rep
