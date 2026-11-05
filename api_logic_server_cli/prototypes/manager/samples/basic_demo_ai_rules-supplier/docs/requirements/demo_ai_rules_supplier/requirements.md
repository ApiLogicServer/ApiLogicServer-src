<!--
  Source: demo_ai_rules_supplier_cli/readme.md (the prompt and the passages that define the behavior); text unchanged, arranged in sections.
  Reference implementation: samples/basic_demo_ai_rules-supplier
-->

## Business Logic

```
On Placing Orders:

    Requirement Check Credit:

    1. The Customer's balance is less than the credit limit
    2. The Customer's balance is the sum of the Order amount_total where date_shipped is null
    3. The Order's amount_total is the sum of the Item amount
    4. The Item amount is the quantity * unit_price
    5. The Product count suppliers is the sum of the Product Suppliers
    6. Use AI to Set Item field unit_price by finding the optimal Product Supplier based on cost, lead time, and world conditions

    Requirement: App Integration

    1. Publish the Order to Kafka topic 'order_shipping' if the date_shipped is not None
```


## Testing

1. Update config/ai_test_context.yaml to signify Suez Canal blocked
2. Start the Server
3. Order some Egyptian Cotton Sheets (use in the Admin App, or test MCP using Copilot - paste:<br> &emsp;*On Alice's first order, include 100 Egyptian Cotton Sheets*
4. Verify the AI call - use the Admin App to view the audit trail (top of this page)
