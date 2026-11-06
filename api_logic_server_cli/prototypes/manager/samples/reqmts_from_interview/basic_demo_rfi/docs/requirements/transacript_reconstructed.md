# Session Transcript (reconstructed) — basic_demo_rfi green-products interview

> **Provenance.** Reconstructed from two files, not from a session log:
> - `transacript.md` — a raw paste that starts mid-interview (the tail of the Question 2 reply, Question 3, the answer "A", and the synthesis). Its wording is reproduced verbatim below, including the timestamps and model line the paste carried.
> - `basic_demo_rfi-transcript.md` — the AI-written Q&A record. It supplies Question 1, the first half of Question 2, and the final "yes". Those parts are marked *(from basic_demo_rfi-transcript.md)* and are paraphrased, not verbatim.
>
> Nothing else was added. The paste has no Question 1, no user message for Question 2 beyond what the Q&A record shows, and no closing "yes", so those turns are summaries.

**Scope.** STEP 1b: a scoped interview on a single flagged clause of an otherwise complete prompt.
Flagged clause: *Encourage customers to purchase 'green' products with an item discount using a configurable flat percentage.*
All other clauses were fully specified and were not interviewed.

---

## At a glance

| # | Topic | Options offered | User's answer | Outcome |
|---|---|---|---|---|
| 1 | What makes a product "green"? | Flag on Product · lookup table (Category/Certification) | "yes, a flag on the Product" | `Product.green`, TEXT `'yes'`/`'no'`, default `'no'` |
| 2 | Where does the percentage live? | One global `sys_config` setting · per product | "global setting" | `sys_config.green_discount_pct`, default `0.10` (**AI-proposed**, not user-supplied) |
| 3 | How does the discount fit Check Credit? | A · B · C · D | **A** | Extend rule 4 with a derived `Item.discount_amount` |

Result: the user confirmed the merged text with "yes", and the build continued to schema and logic.

---

## Question 1 — What makes a product "green"? *(from basic_demo_rfi-transcript.md)*

**Assistant** offered:
- A flag on Product (for example `green`, yes/no)
- A lookup you would browse or report on (for example a Category/Certification table)

**User:** "yes, a flag on the Product"

---

## Question 2 — Where does the percentage live, and what is the starting value?

*(The question itself is from basic_demo_rfi-transcript.md. The start of the AI's reply to the answer is not in the paste.)*

**Assistant** offered:
- One global setting in `sys_config` (for example `green_discount_pct`)
- Per product

**User:** "global setting"

**Assistant** (verbatim, from the paste):

> Noted: a global green_discount_pct in sys_config. You didn't give a starting value, so I'll default it to 10% and log it as an ad-lib you can change in the Admin UI.

> **Reviewer note.** The 10% was never chosen by the user. The AI proposed it here, and the user accepted it only by confirming the synthesis at the end. It is an ad-lib, not a requirement.

---

## Question 3 — How should the discount fit with your Check Credit rules?

**Assistant** (verbatim, from the paste):

> Your rules say Item.amount = quantity * unit_price (rule 4), and Order.amount_total sums Item.amount (rule 3). A discount that reaches the customer's balance has to change one of them. Here are the options:
>
> **A.** Extend rule 4, keeping its meaning for non-green items. Add a derived Item.discount_amount (quantity * unit_price * pct for green items, else 0). Then Item.amount = quantity * unit_price - discount_amount. Rules 3 and 5 are untouched. Non-green items behave exactly as before, and each discount is visible on the item. I recommend this one.
>
> **B.** Leave rule 4 alone, and change rule 3 to sum a new net_amount. This leaves amount as the undiscounted price, but it rewrites rule 3.
>
> **C.** Show the discount, but don't apply it to amount. Rules 3 and 4 stay as written. The customer's balance and credit check would not reflect the discount, so I doubt this is what you want.
>
> **D.** Discount the unit_price itself. This changes rule 5 from "copied from Product" to "copied, then reduced."
>
> Which do you want? Whichever you pick will be recorded as a decision about your explicit clause, not as an assumption.

*9:15 PM · Claude Sonnet 5.5 (claude-sonnet-5-5)*

**User:** "A" *(9:17 PM)*

> **Why this question was asked.** The discount touches an explicit clause (rule 4). STEP 1b says an interview answer must not silently change what an already-specified clause does, so the conflict was put to the user as a decision about that clause. The user chose A, which keeps rule 4's meaning for non-green items.

---

## Synthesis read back to the user

**Assistant** (verbatim, from the paste):

> Here is the interview result, merged into your prompt. Your explicit clauses are unchanged except rule 4, which is extended the way you chose in Question 3.
>
> **Added by the green-products interview**
> - `Product.green` is a flag (TEXT 'yes'/'no', default 'no').
> - `sys_config.green_discount_pct` is a global flat percentage, default 10% (stored as a fraction, 0.10), editable in the Admin UI.
> - `Item.discount_amount` is derived: `quantity * unit_price * green_discount_pct` when the item's product is green, otherwise 0.
> - **Extended rule 4:** `Item.amount = quantity * unit_price - discount_amount`. For non-green items this is identical to your original rule 4. Rules 1, 2, 3 and 5 are unchanged, so the discount flows into `Order.amount_total` and `Customer.balance` through your existing rules.
>
> I'd also make two small choices, and I'll log both in ad-libs.md rather than ask:
> - **Snapshot:** the item copies `green` from the Product when it's created, like `unit_price`. Flipping a product's flag later won't re-price existing items. The rate is read from `sys_config` when the item is priced, with no FK to `sys_config`.
> - **Rate change:** changing the percentage affects new and edited items only, not existing ones.
>
> Does this read right? If you say yes, I'll write the transcript and continue to the schema and logic.

**User:** "yes" *(from basic_demo_rfi-transcript.md; not in the paste)*

---

## What this produced

| Decision | Source | Where it lands |
|---|---|---|
| `Product.green` TEXT yes/no | User (Q1) | schema |
| Global `sys_config.green_discount_pct` | User (Q2) | schema |
| Default value 10% | **AI proposal**, accepted via "yes" | ad-libs.md |
| Extend rule 4 via `Item.discount_amount` | User (Q3, option A) | logic; rule 4 text amended |
| `green` snapshotted onto the Item at creation | **AI choice**, accepted via "yes" | ad-libs.md |
| Rate change affects new and edited items only | **AI choice**, accepted via "yes" | ad-libs.md |

---

## Tool notes (process, not requirements)

- No `AskUserQuestion` dialogs were used; the user prefers plain-text questions. All answers were free text, so the options above are what the assistant listed in its message.
- The paste carries UI residue (`9:15 PM`, `9s`, `2.8 credits`). Only the timestamps and the model name are kept above.
