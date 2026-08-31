<!--
  Copied from: basic_demo_rfi/docs/requirements/RFI-transcript.md (real, unedited AI Interview session)
-->

# RFI Transcript — basic_demo_rfi

**User:**

```
Create a system called basic_demo_rfi, with customers, orders, items and products.

Include a notes field for orders.

On Placing Orders, Check Credit
    1. The Customer's balance is less than the credit limit
    2. The Customer's balance is the sum of the Order amount_total where date_shipped is null
    3. The Order's amount_total is the sum of the Item amount
    4. The Item amount is the quantity * unit_price
    5. The Item unit_price is copied from the Product unit_price

Use case: App Integration
    1. Publish the Order to Kafka topic 'order_shipping' when the date_shipped becomes not None.

Also, interview me to work out this general intent:
Encourage customers to purchase 'green' products with an item discount using a configurable flat percentage.
```

**AI:** To work this out, three questions:
1. How should we flag a product as 'green'? A simple boolean (`is_green`) is the obvious choice — does that work, or did you have a different classification in mind (e.g. a category/tag)?
2. Where should the discount apply — reduce `Item.unit_price` directly, or leave `unit_price` as the pure copy from `Product.unit_price` and apply the discount only inside the `Item.amount` formula?
3. The prompt says "a configurable flat percentage" — should this rate live in `sys_config` (alongside the other constants), so it can be changed without a code deploy?

**User:** 1 - is_green is fine, 2 - reduce item.unit_price, 3 - yes, externalize the discount into the sys_config table

**AI (synthesis, read back for confirmation):** Product.is_green (boolean) flags green products. When placing an order, Item.unit_price for green products is reduced by SysConfig.green_discount_pct — a configurable flat percentage stored in sys_config, copied onto the Item at order time (not recalculated later if the config changes).

**User:** proceed
