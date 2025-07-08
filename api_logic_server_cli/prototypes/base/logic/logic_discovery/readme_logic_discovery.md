You might provide the following prompt to CoPilot:

```text
Use case: Check Credit    
    1. The Customer's balance is less than the credit limit
    2. The Customer's balance is the sum of the Order amount_total where date_shipped is null
    3. The Order's amount_total is the sum of the Item amount
    4. The Item amount is the quantity * unit_price
    5. The Item unit_price is copied from the Product unit_price

Use case: App Integration
    1. Send the Order to Kafka topic 'order_shipping' if the date_shipped is not None.
```

Basic process:
1. Create a file such as `logic/logic_discovery/check_credit.py` (e.g., copy from `use_case.py`).
2. Paste the prompt above into CoPilot - use `docs/training` to generate logic
3. Paste the generated logic into `logic/logic_discovery/check_credit.py`

Resultant logic:
```python
    if os.environ.get("WG_PROJECT"):
        # Inside WG: Load rules from docs/expprt/export.json
        load_verify_rules()
    else:
        # Outside WG: load declare_logic function
        from logic.logic_discovery.auto_discovery import discover_logic
        discover_logic()

    # Logic from GenAI: (or, use your IDE w/ code completion)
    from database.models import Product, Order, Item, Customer, SysEmail

    # Ensure the customer's balance is less than their credit limit
    Rule.constraint(validate=Customer, as_condition=lambda row: row.balance <= row.credit_limit, error_msg="Customer balance ({row.balance}) exceeds credit limit ({row.credit_limit})")

    # Derive the customer's balance as the sum of order totals where not yet shipped.
    Rule.sum(derive=Customer.balance, as_sum_of=Order.amount_total, where=lambda row: row.date_shipped is None)

    # Derive the order's total amount from the sum of item amounts.
    Rule.sum(derive=Order.amount_total, as_sum_of=Item.amount)

    # Calculate item amount based on quantity and unit price.
    Rule.formula(derive=Item.amount, as_expression=lambda row: row.quantity * row.unit_price)

    # Copy unit price from product to item.
    Rule.copy(derive=Item.unit_price, from_parent=Product.unit_price)

    # Send order details to Kafka if order is shipped.
    Rule.after_flush_row_event(on_class=Order, calling=kafka_producer.send_row_to_kafka, if_condition=lambda row: row.date_shipped is not None, with_args={'topic': 'order_shipping'})

    # End Logic from GenAI
```