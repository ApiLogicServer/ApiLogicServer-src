# basic_demo_rfi — interview transcript (STEP 1b, scoped to one clause)

Flagged clause: *Encourage customers to purchase 'green' products with an item discount using a configurable flat percentage.*
All other clauses of the prompt were fully specified and were not interviewed.

**Question: What makes a product "green"?**
Options: A flag on Product (e.g. `green`, yes/no) · A lookup you'd browse or report on (e.g. a Category/Certification table)

**Answered:** yes, a flag on the Product

**Question: Where does the configurable percentage live, and what is the starting value?**
Options: One global setting in `sys_config` (e.g. `green_discount_pct`) · Per product

**Answered:** global setting

**Question: How should the discount fit with the Check Credit rules (rule 4: Item.amount = quantity * unit_price; rule 3: Order.amount_total sums Item.amount)?**
Options: A. Extend rule 4 — add a derived Item.discount_amount, then Item.amount = quantity * unit_price - discount_amount; rules 3 and 5 untouched · B. Leave rule 4 alone, change rule 3 to sum a new net_amount · C. Show the discount but do not apply it to amount · D. Discount the unit_price itself (changes rule 5)

**Answered:** A

**AI synthesis, read back to user:**

> **Added by the green-products interview**
> - `Product.green` is a flag (TEXT 'yes'/'no', default 'no').
> - `sys_config.green_discount_pct` is a global flat percentage, default 10% (stored as a fraction, `0.10`), editable in the Admin UI.
> - `Item.discount_amount` is derived: `quantity * unit_price * green_discount_pct` when the item's product is green, otherwise 0.
> - **Extended rule 4:** `Item.amount = quantity * unit_price - discount_amount`. For non-green items this is identical to the original rule 4. Rules 1, 2, 3 and 5 are unchanged, so the discount flows into `Order.amount_total` and `Customer.balance` through the existing rules.
>
> Two small choices, to be logged in ad-libs.md: the item copies `green` from the Product when created, like `unit_price` (flipping a product's flag later does not re-price existing items; the rate is read from `sys_config` when the item is priced, no FK to `sys_config`); changing the percentage affects new and edited items only.

**User:** "yes"

**Note on specific numbers:** the 10% starting value was never asked for or supplied by the user. In Question 2 the AI proposed 10% as a default and the user answered only "global setting"; the value was then stated in the synthesis and accepted via "yes", not chosen from a menu.

**Note on conflict handling:** the discount touches an explicit clause (rule 4). Per STEP 1b this was surfaced as a decision (Question 3) rather than resolved silently; the user chose option A.

---

## Tool notes (process, not requirements)

- No `AskUserQuestion` dialogs were used (the user prefers plain-text questions); all answers were free text, so the Options lines list what the AI offered in the message.
