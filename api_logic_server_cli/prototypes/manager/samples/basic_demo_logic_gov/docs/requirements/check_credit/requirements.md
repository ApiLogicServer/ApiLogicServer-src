---
created: 2026-05-23T00:00:00
created_by: Claude (Method 4, System Creation Services)
use_case: check_credit
---

On Placing Orders, Check Credit    
    1. The Customer's balance is less than the credit limit
    2. The Customer's balance is the sum of the Order amount_total where date_shipped is null
    3. The Order's amount_total is the sum of the Item amount
    4. The Item amount is the quantity * unit_price
    5. The Item unit_price is copied from the Product unit_price
