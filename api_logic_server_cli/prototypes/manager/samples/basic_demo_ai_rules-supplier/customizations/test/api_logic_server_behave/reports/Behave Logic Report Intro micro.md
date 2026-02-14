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
