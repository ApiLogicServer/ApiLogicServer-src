# Ad-Libs — demo_mcp_send_email

Every assumption or guess made beyond the literal prompt spec (`project_creation_prompt.md`).

## Creation Steps

Commands actually run, in order:

```bash
genai-logic create --project-name=demo_mcp_send_email --db_url=sqlite:///samples/dbs/basic_demo.sqlite
sqlite3 demo_mcp_send_email/database/db.sqlite "CREATE TABLE sys_email (...)"
cd demo_mcp_send_email && genai-logic rebuild-from-database --db_url=sqlite:///database/db.sqlite
# admin.yaml <- admin-merge.yaml (backup to admin.yaml.bak; no prior customizations existed)
genai-logic genai-add-mcp-client
# wrote logic/logic_discovery/check_credit.py
# wrote logic/logic_discovery/send_email.py
cd .. && python api_logic_server_run.py   # verification only, then stopped
```

## Ad-Libs

1. **Source database, not `starter.sqlite`.** The prompt explicitly said "Create
   demo_mcp_send_email from samples/dbs/basic_demo.sqlite" — `basic_demo.sqlite` already
   contains the exact Customer/Order/Item/Product schema the Check Credit clause needs
   (balance, credit_limit, amount_total, date_shipped, unit_price). Used that db_url directly
   in `genai-logic create` instead of the Method-4 default `starter.sqlite`, per the prompt's
   explicit instruction. No `SysConfig`/`sys_config` table exists in this project as a result —
   there were no rate/threshold constants in the prompt to warrant one.

2. **`SysEmail` schema beyond the 3 named columns.** The prompt named only `message`,
   `subject`, `CreatedOn` plus "(child of customer)". Added the implied `id` primary key and
   `customer_id` FK (required for "child of customer" and for the event's `row.customer`
   lookup). `Customer.email_opt_out` already existed in `basic_demo.sqlite` — not an ad-lib,
   just confirmed present rather than added.

3. **Event wiring.** "When a SysEmail is created, log 'email sent'" — implemented as
   `Rule.commit_row_event` (fires after commit), matching this project's own CE worked example
   for this exact scenario (`.github/copilot-instructions.md`, "Adding events" section). The log
   message text ("email sent to {name} - Subject: {subject}" / "email blocked for {name} -
   customer opted out") is not specified verbatim by the prompt; wrote it to literally contain
   "email sent" (clause's exact phrase) for the opted-in case.

4. **Boundary operator on Check Credit clause 1** ("balance is less than the credit limit") —
   implemented as `<=` per this CE's standing BOUNDARY-OPERATOR CONVENTION (`docs/training/
   logic_bank_api.md`): ordinary "less than X" phrasing defaults to `<=` unless the prompt
   states the boundary is excluded, which it does not here. Verified live: credit_limit set
   to exactly the current balance is accepted; only balance > credit_limit is rejected.

5. **MCP natural-language resolution not implemented here — already generic.** The third
   use case ("Add the MCP client...") only required running `genai-logic genai-add-mcp-client`
   (adds `SysMcp` table + Admin UI + the generic `mcp_client_executor`). No custom logic was
   written to interpret "List the orders... and send a discount email..." — the generated
   `logic/logic_discovery/mcp_client_executor_request.py` already wires any `SysMcp` insert to
   the generic executor, and the project's `/.well-known/mcp.json` discovery doc's `learning`
   field already contains the fan-out + "only if 'email' is in the query, POST to SysEmail"
   instructions as boilerplate (not specific to this project). Verified end-to-end live
   (see below) — this worked with zero additional code.

## Verification performed (live, via running server; test data cleaned up afterward)

- Check Credit constraint: PATCH `Customer.credit_limit` below current `balance` → rejected
  (code 2001, "balance (...) exceeds credit limit (...)").
- Check Credit cascade: inserted Order + Item (qty 2 × Widget, unit_price 90) → `Item.unit_price`
  copied (90.0), `Item.amount` = 180.0, `Order.amount_total` = 180.0, `Customer.balance`
  incremented by 180.0 (delta-adjusted, not recomputed) — all four clauses confirmed, then
  rolled back by deleting the Item/Order (balance correctly decremented back).
- Send Email: POST `SysEmail` for an opted-in customer → log line "email sent to Alice -
  Subject: Discount Offer"; for an opted-out customer → "email blocked for Bob - customer
  opted out". `Customer.email_opt_out` toggled via PATCH for the test, then reset to its
  original seed value.
- MCP end-to-end: POST to `/api/mcp-SysMcp/` with the exact natural-language request from the
  prompt ("List the orders date_shipped is null and CreatedOn before 2023-07-14, and send a
  discount email (subject: 'Discount Offer') to the customer for each one.") → the executor
  found the matching unshipped/old orders and POSTed a `SysEmail` per customer, correctly
  skipping the opted-out customer ("Silent"). All test rows deleted afterward.

No 🔴 Review Required findings — no clause depends on a row that might never be written (no
"absence of event" case here); every clause maps to a real Rule.* call whose live behavior
matches the requirement's own wording.
