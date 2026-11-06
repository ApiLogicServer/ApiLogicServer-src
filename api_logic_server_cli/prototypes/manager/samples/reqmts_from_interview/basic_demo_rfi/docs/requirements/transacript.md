
Noted: a global green_discount_pct in sys_config. You didn't give a starting value, so I'll default it to 10% and log it as an ad-lib you can change in the Admin UI.

Question 3: How should the discount fit with your Check Credit rules?

Your rules say Item.amount = quantity * unit_price (rule 4), and Order.amount_total sums Item.amount (rule 3). A discount that reaches the customer's balance has to change one of them. Here are the options:

A. Extend rule 4, keeping its meaning for non-green items. Add a derived Item.discount_amount (quantity * unit_price * pct for green items, else 0). Then Item.amount = quantity * unit_price - discount_amount. Rules 3 and 5 are untouched. Non-green items behave exactly as before, and each discount is visible on the item. I recommend this one.
B. Leave rule 4 alone, and change rule 3 to sum a new net_amount. This leaves amount as the undiscounted price, but it rewrites rule 3.
C. Show the discount, but don't apply it to amount. Rules 3 and 4 stay as written. The customer's balance and credit check would not reflect the discount, so I doubt this is what you want.
D. Discount the unit_price itself. This changes rule 5 from "copied from Product" to "copied, then reduced."
Which do you want? Whichever you pick will be recorded as a decision about your explicit clause, not as an assumption.

9:15 PM
9s
•
Claude Sonnet 5.5 (claude-sonnet-5-5) • 2.8 credits
A

9:17 PM
Here is the interview result, merged into your prompt. Your explicit clauses are unchanged except rule 4, which is extended the way you chose in Question 3.

Added by the green-products interview

Product.green is a flag (TEXT 'yes'/'no', default 'no').
sys_config.green_discount_pct is a global flat percentage, default 10% (stored as a fraction, 0.10), editable in the Admin UI.
Item.discount_amount is derived: quantity * unit_price * green_discount_pct when the item's product is green, otherwise 0.
Extended rule 4: Item.amount = quantity * unit_price - discount_amount. For non-green items this is identical to your original rule 4. Rules 1, 2, 3 and 5 are unchanged, so the discount flows into Order.amount_total and Customer.balance through your existing rules.
I'd also make two small choices, and I'll log both in ad-libs.md rather than ask:

Snapshot: the item copies green from the Product when it's created, like unit_price. Flipping a product's flag later won't re-price existing items. The rate is read from sys_config when the item is priced, with no FK to sys_config.
Rate change: changing the percentage affects new and edited items only, not existing ones.
Does this read right? If you say yes, I'll write the transcript and continue to the schema and logic.