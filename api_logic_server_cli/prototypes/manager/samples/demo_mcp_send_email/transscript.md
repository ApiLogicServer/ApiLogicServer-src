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

1. Add a SysEmail table (child of customer) with message, subject and CreatedOn.
2. When a SysEmail is created, log "email sent", unless the customer has opted out.

Add the MCP client, so I can enter requests like this in the Admin App (SysMcp):

* *List the orders date_shipped is null and CreatedOn before 2023-07-14, and send a discount email (subject: 'Discount Offer') to the customer for each one.*
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
8. Wrote `logic/logic_discovery/check_credit.py` (5 rules: sum, sum, formula, copy, constraint).
9. Wrote `logic/logic_discovery/send_email.py` — `Rule.after_flush_row_event` guarded with
   `logic_row.is_inserted()`, logging "email sent"/"email skipped" unless
   `Customer.email_opt_out`. (Deliberately NOT `Rule.commit_row_event`, which this project's
   own CE "Adding events" example shows: `commit_row_event` has no insert guard, so it would
   re-log on a later *update* to an existing `SysEmail` row — the requirement says "when a
   SysEmail is **created**," i.e. insert only.)
10. Wrote per-use-case `docs/requirements/check_credit/requirements.md`,
    `docs/requirements/send_email/requirements.md`, and (though no custom logic file was
    authored for it) `docs/requirements/mcp_client/requirements.md` for traceability.
11. Started the server and verified live:
    - Check Credit constraint: lowering `credit_limit` below current `balance` → rejected
      (code 2001).
    - Full cascade: inserted Order + Item (2 × Widget) → `unit_price` copied, `amount` =
      180.0, `Order.amount_total` = 180.0, `Customer.balance` incremented by 180.0 (delta
      adjustment); deleted both, balance correctly decremented back.
    - Send Email: opted-in customers → "email sent to {name} - Subject: {subject}";
      opted-out customer ("Silent") → "email skipped - Silent opted out".
    - MCP end-to-end: POSTed the exact natural-language request from the prompt to
      `/api/mcp-SysMcp/` — the executor correctly found matching unshipped/old orders and
      sent a `SysEmail` to each customer, skipping the opted-out one.
    - ⚠️ Correction made in review (see below): two ad-hoc test `SysEmail` rows (ids 1-2,
      from earlier manual testing before the final 3-row verification pass) were **not**
      actually deleted despite the session's own ad-libs claiming "all test rows deleted
      afterward." Found and removed during the separate review pass, not during this
      build itself — see Outcome below.
12. Wrote `docs/requirements/project_creation_prompt.md` (verbatim prompt, overwriting the
    `create`-inferred one-liner), enriched `docs/requirements/project_creation_report.md`
    (creation commands, schema decisions, CE files read, Use Cases links), and wrote
    `docs/requirements/ad-libs.md`.
13. Started the server one final time to confirm a clean startup, then stopped it.

## Review and gold-promotion pass (separate session)

A later session compared this build against the then-current reference implementation
(`samples/demo_mcp_send_email`, itself sourced from this same gold location) and wrote
`docs/requirements/assessment.md`. That review found:
- This build's `send_email.py` (step 9 above) is more correct than the prior reference's
  `Rule.commit_row_event` version, for the insert-only reason given above.
- Two defects not in the authored logic: a stray terminal-transcript capture left in a
  wrongly-nested `demo_mcp_send_email/demo_mcp_send_email/` directory (removed), and two
  leftover test `SysEmail` rows contradicting the ad-libs' "cleaned up" claim (step 11 above
  — removed). `readme.md` (always live-fetched from the Docs repo, not authored by either
  session) also had a transient mkdocs-conversion defect; replaced with the known-good copy.
- `readme_standard.md`'s "📋 Project Summary" section had reverted to the unfilled
  `PROJECT_SUMMARY_PLACEHOLDER` — Manager CE STEP 5c2 was skipped this run. Restored to a
  real summary during the same review pass.

With those corrections applied, this build was promoted to replace the gold-source sample at
`org_git/ApiLogicServer-src/api_logic_server_cli/prototypes/manager/samples/demo_mcp_send_email/`.

## Outcome

All three use cases (Check Credit, Send Email, MCP client) implemented and verified live,
with no 🔴 Review Required findings from the STEP 8 behavioral verification pass. Full
detail (ad-libs, verification log) is in `docs/requirements/ad-libs.md`; comparison detail
is in `docs/requirements/assessment.md`.
