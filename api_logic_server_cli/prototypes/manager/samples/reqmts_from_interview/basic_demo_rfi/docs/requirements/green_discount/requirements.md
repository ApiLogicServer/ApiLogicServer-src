---
created: 2026-11-05
created_by: claude-sonnet-5-5
use_case: green_discount
---

Encourage customers to purchase 'green' products with an item discount using a configurable flat percentage.

Resolved by interview (confirmed by the user):
    Product.green is a flag (yes/no).
    sys_config.green_discount_pct is a global flat percentage, editable in the Admin UI.
    Item.discount_amount is the quantity * unit_price * green_discount_pct when the item's product is green, otherwise 0.
    The Item amount is the quantity * unit_price less the Item discount_amount (rule 4 of Check Credit, extended).
