# Session Transcript — demo_mcp_send_email

Note: this is a plain activity transcript, not an RFI (`<name>-transcript.md`) Q&A
transcript. No Socratic interview (Method 4 STEP 1a/1b) ran in this session — the
prompt below was already complete, so execution went straight to STEP 2 onward.

## User request (verbatim)

> Create demo_mcp_send_email per samples/prompts/demo_mcp_send_email.prompt.md

## Prompt file content (`samples/prompts/demo_mcp_send_email.prompt.md`)

```
// paste this into your AI Assistant (Method 4):

Create demo_mcp_send_email from samples/dbs/basic_demo.sqlite.

Check Credit
    1. The Customer's balance is less than the credit limit
    2. The Customer's balance is the sum of the unshipped Order amount_total
    3. The Order's amount_total is the sum of the Item amount
    4. The Item amount is the quantity * unit_price
    5. The Item unit_price is copied from the Product unit_price

Send Email
    Add a SysEmail table (child of customer) with message, subject and CreatedOn.
    When a SysEmail is created, log "email sent", unless the customer has opted out.

Add the MCP client, so I can enter requests like this in the Admin App (SysMcp):
    List the orders date_shipped is null and CreatedOn before 2023-07-14,
    and send a discount email (subject: 'Discount Offer') to the customer for each one.
```

(Line 1 is a `//` human-reader comment per Manager CE STEP 0 — read for context, not acted on.)

## What was done, in order

1. Confirmed no `demo_mcp_send_email/` collision at the Manager root.
2. `genai-logic create --project-name=demo_mcp_send_email --db_url=sqlite:///samples/dbs/basic_demo.sqlite`
   — used `basic_demo.sqlite` directly (not the Method-4 default `starter.sqlite`) because the
   prompt named it explicitly, and it already has the Customer/Order/Item/Product schema the
   Check Credit clause needs.
3. Read the project CE (`.github/copilot-instructions.md`, full file) and the auto-loaded
   `docs/training/logic_bank_api.md` (via the project's `CLAUDE.md` @-include).
4. Inspected `basic_demo.sqlite`'s existing schema — confirmed `Customer.balance`,
   `credit_limit`, `email`, `email_opt_out`; `Order.CreatedOn`, `date_shipped`,
   `amount_total`; `Item.quantity`, `amount`, `unit_price`; `Product.unit_price` all already
   present. No DDL needed for Check Credit.
5. Added `SysEmail` via raw DDL (child of Customer: `id`, `customer_id` FK, `subject`,
   `message`, `CreatedOn`), then `genai-logic rebuild-from-database`.
6. Rebuilt `admin.yaml` from the generated `admin-merge.yaml` (backed up original to
   `admin.yaml.bak` first — no prior customizations existed to lose).
7. Ran `genai-logic genai-add-mcp-client` — added the `SysMcp` table (its own bound
   mini-database, `database/mcp_db.sqlite`) plus the generic MCP client executor and Admin
   UI wiring. No custom MCP code was written; the generated
   `logic/logic_discovery/mcp_client_executor_request.py` and `/.well-known/mcp.json`
   discovery doc already handle natural-language → API translation generically.
8. Wrote `logic/logic_discovery/check_credit.py` (5 rules: constraint, sum, sum, formula, copy).
9. Wrote `logic/logic_discovery/send_email.py` (`Rule.commit_row_event`, logs "email sent"
   unless `Customer.email_opt_out`).
10. Wrote per-use-case `docs/requirements/check_credit/requirements.md` and
    `docs/requirements/send_email/requirements.md` (verbatim excerpts).
11. Started the server and verified live, then cleaned up all test data:
    - Check Credit constraint: lowering `credit_limit` below current `balance` → rejected
      (code 2001).
    - Full cascade: inserted Order + Item (2 × Widget) → `unit_price` copied, `amount` =
      180.0, `Order.amount_total` = 180.0, `Customer.balance` incremented by 180.0 (delta
      adjustment); deleted both, balance correctly decremented back.
    - Send Email: opted-in customer → "email sent to Alice - Subject: Discount Offer";
      opted-out customer → "email blocked for Bob - customer opted out".
    - MCP end-to-end: POSTed the exact natural-language request from the prompt to
      `/api/mcp-SysMcp/` — the executor correctly found matching unshipped/old orders and
      sent a `SysEmail` to each customer, skipping the opted-out one.
    - All test rows deleted / flags reset afterward; seed database left in its original state.
12. Wrote `docs/requirements/project_creation_prompt.md` (verbatim prompt, overwriting the
    `create`-inferred one-liner), enriched `docs/requirements/project_creation_report.md`
    (creation commands, schema decisions, CE files read, Use Cases links), wrote
    `docs/requirements/ad-libs.md`, and filled in the `readme_standard.md` project summary
    (this is a `demo_`-named project, so `readme_standard.md` — not `readme.md` — carries the
    `PROJECT_SUMMARY_PLACEHOLDER`).
13. Started the server one final time to confirm a clean startup (13 rules activated, all
    resources exposed, HTTP 200 on `/api/Customer/`), then stopped it.

## Outcome

All three use cases (Check Credit, Send Email, MCP client) implemented and verified live,
with no 🔴 Review Required findings from the STEP 8 behavioral verification pass. Full
detail (ad-libs, verification log) is in `docs/requirements/ad-libs.md`.
