# Logic Flow — samples/basic_demo_sales_by_month [place_order]

> Scoped to requirement: **place_order**

<table>
<tr valign="top">
<td width="65%">

![logic flow](logic_diagrams/logic_diagram_place_order.svg)

</td>
<td width="35%">

### Rules

1. `unit_price = copy(unit_price)`<br>
2. `amount = quantity * unit_price`<br>
3. `amount_total = sum(amount)`<br>
4. `balance = sum(amount_total where date_shipped)`<br>
5. `total_amount = sum(amount_total)`<br>
6. `order_count = count(Order)`<br>
7. constraint: `Customer`<br>
8. `Order` → `send_order_to_kafka` (after_flush) — Order event: publish to Kafka topic 'order_shipping' when date_shipped becomes not None

</td>
</tr>
</table>

## Requirements

```
Use case: App Integration
    1. Publish the Order to Kafka topic 'order_shipping' when the date_shipped becomes not None.
```

```
On Placing Orders, Check Credit
    1. The Customer's balance is less than the credit limit
    2. The Customer's balance is the sum of the Order amount_total where date_shipped is null
    3. The Order's amount_total is the sum of the Item amount
    4. The Item amount is the quantity * unit_price
    5. The Item unit_price is copied from the Product unit_price
```

```
On Placing Orders, maintain sales totals
    1. Orders can be assigned to people who are salesreps
    2. Maintain monthly sales totals and order counts for each sales rep
```

---
_Generated 2026-09-10 18:08_
