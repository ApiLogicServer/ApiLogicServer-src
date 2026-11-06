---
created: 2026-11-05
created_by: claude-sonnet-5-5
use_case: check_credit
---

On Placing Orders, Check Credit
    1. The Customer's balance is less than the credit limit
    2. The Customer's balance is the sum of the unshipped Order amount_total
    3. The Order's amount_total is the sum of the Item amount
    4. The Item amount is the quantity * unit_price
    5. The Item unit_price is copied from the Product unit_price

Extension of rule 4, from the green-products interview (confirmed by the user):
    The Item amount is the quantity * unit_price less the Item discount_amount
