<!--
  Copied from: RFI/docs/requirements/RFI-transcript.md (real, unedited AI Interview session)
  Trimmed: Manager-welcome boilerplate removed, AI recaps condensed to their new
  information. Every human answer and the final synthesized requirements are verbatim.
-->

# RFI — AI-as-BA Interview Transcript

**Human:** create a new project called RFI. it's a test for Requirements From Interview.

**AI:** Got it — project name `RFI`. Quick check: no domain prompt file or pasted text has come with this request, so per Method 4's fork — do you have a domain prompt ready, or would you like to discuss the system and I'll draft one with you? Since you called it "Requirements From Interview," I'm guessing you want the interview — just confirming.

---

**Human:** yes - it's about Customers, Orders, Items and Products

**AI:** Good — let's build this out conversationally, topic by topic. First: **constants**. Is there any rate, threshold, discount, or date in this system that's fixed business policy rather than something a user types in per-transaction?

---

**Human:** I don't understand, but customers keep ordering Rolls Royces they can't pay for, so we have a requirement that the balance cannot exceed the credit limit

**AI:** Good example. Two things to unpack:
- **Customer.credit_limit** — same fixed value for every customer, or does it vary per customer?
- **Customer.balance** — sounds derived from unpaid Orders (sum of order amounts not yet paid/shipped). Right, or is "balance" something else (e.g. an account balance from payments)?

And the constraint: **Customer.balance <= Customer.credit_limit** — enforced at the moment an Order is placed?

---

**Human:** each customer has their own credit limit, set by the sales rep or sales mgr

**AI:** Good — `credit_limit` is a per-customer stored value, not a global constant, so no `SysConfig` entry needed. One more thing: is there an **approval rule** on who can raise a credit limit, or how high?

---

**Human:** no, that's fine for now

**AI:** Understood — no approval ceiling, `credit_limit` is just an open per-customer field. Next topic: **FK inventory / lookups**. An Order belongs to one Customer. An Order contains multiple Items, each Item references a Product — is that the structure (Order → Items → Product)? Is Product something to browse/report on separately, or just a text description on each item?

---

**Human:** Product is a thing - we manage price, and description

**AI:** Good — Product is a real lookup entity: `id`, `name`/`description`, `price`. That confirms **Customer → Order → Item → Product** (Item is the line-item join). Two details on Item:
- Does each Item store its **own copy of unit price** (snapshot at order time), or always reference `Product.price` live? (Most systems snapshot — price changes shouldn't retroactively reprice old orders.)
- Does Item have **quantity**, and is **Item.amount = quantity × unit_price**, derived automatically?

And tying back to credit: is **Order.amount_total = sum of Item.amount**, and **Customer.balance = sum of amount_total across that customer's unpaid Orders**?

---

**Human:** sounds right

**AI:** That locks in the derivation chain:
- `Item.amount = Item.quantity * Item.unit_price` (unit_price snapshotted from Product.price at order time)
- `Order.amount_total = Sum(Item.amount)`
- `Customer.balance = Sum(Order.amount_total where unpaid)`
- Constraint: `Customer.balance <= Customer.credit_limit`

One clarifying point on "unpaid" — do Orders have a **status** (e.g. `date_shipped`, or a `paid` flag) that determines whether an order counts toward balance?

---

**Human:** paid flag

**AI:** Good, simple boolean: `Order.is_paid`. So `Customer.balance = Sum(Order.amount_total where is_paid = False)`.

Quickly, two more topics: **Request Pattern** — anything involving an AI/email/external judgment call, like "pick the best supplier"? Or is this purely: customer places order, system checks credit, done? **Type hierarchy** — different kinds of Products or Customers that share most fields but differ in a few? If both are "no," I think we have enough to draft the requirements.

---

**Human:** ok, proceed

**AI:** Both no — plain entities, no AI/judgment-call pattern, no type hierarchy. That closes out the checklist (constants, FKs, Request Pattern, type hierarchy). Let me synthesize this into a requirements narrative and read it back to you.

---

**RFI — Requirements from Interview**

Customers place Orders. Each Order contains one or more Items; each Item references a Product and captures a quantity.

**Entities:**
- **Customer**: name, credit_limit (per-customer, set manually by sales rep/manager, no ceiling), balance (derived)
- **Order**: customer_id (FK), is_paid (boolean flag), amount_total (derived)
- **Item**: order_id (FK), product_id (FK), quantity, unit_price (snapshotted from Product.price at time of order), amount (derived)
- **Product**: name/description, price

**Derivations (bottom-up):**
- `Item.amount = Item.quantity * Item.unit_price`
- `Order.amount_total = Sum(Item.amount)`
- `Customer.balance = Sum(Order.amount_total where Order.is_paid = False)`

**Constraint:**
- `Customer.balance <= Customer.credit_limit` — enforced when an Order (or its Items) would push balance over the limit. (This is the credit-limit rule that motivated the whole system — customers were ordering Rolls Royces they couldn't pay for.)

**Out of scope / explicitly declined:**
- No credit-limit approval ceiling or role-based cap
- No AI/external judgment calls (no Request Pattern)
- No type hierarchies (flat Customer/Order/Item/Product)

---

**Human:** oh, I forgot, when orders are paid, we need to send a message to shipping

**AI:** Good catch — that's an integration/messaging trigger. Pinning it down:
- Fires when **`Order.is_paid` flips from False to True**?
- What does "send a message" mean — Kafka/queue event, email, an outbox row?
- What does shipping need to know — order id, customer, line items/products/quantities?

*[Human selected via structured question: **Kafka/EAI event**]*

**AI:** Good — Kafka/EAI event on the `is_paid` False→True transition. Standard row-change event: no Request Pattern table needed (that pattern is for *inbound* AI/judgment-call direction — this is outbound notification, simpler).

**Added: Shipping notification**
- **Trigger:** `Order.is_paid` transitions False → True
- **Action:** Publish a Kafka/EAI event carrying the order (customer, order id, line items with product + quantity) for the shipping system to consume
- **Pattern:** standard row-event EAI publish (`logic/logic_discovery`), not a Request Pattern inbound table — one-way outbound notification, not a judgment call needing AI resolution

---

Everything else stands as before (Customer/Order/Item/Product, balance/credit-limit derivation and constraint). This is locked in as the domain prompt for `RFI` — the AI proceeds to create the project.
