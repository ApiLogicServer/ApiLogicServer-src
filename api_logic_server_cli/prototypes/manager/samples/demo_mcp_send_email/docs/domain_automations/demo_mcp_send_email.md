# MCP Send Email (Check Credit + Send Email + MCP Client)

**Created:** 2026-10-08
**Tables:** Customer, Order, Item, Product (reused, unchanged), SysEmail (new), SysMcp (new, separate `mcp` bind-key db)
**Rules:** 5 Check Credit rules (2 sum, 1 formula, 1 copy, 1 constraint) + 1 Send Email event (after_flush_row_event) + 1 generated MCP row_event (via `genai-logic genai-add-mcp-client`)

## Prompt

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

## Notes

- `basic_demo.sqlite`'s existing seed data (5 customers incl. one opted-out "Silent", 5 orders spanning shipped/unshipped and before/after 2023-07-14) already covered every test scenario — no new seed script was needed.
- MCP client implemented via the project's own `genai-logic genai-add-mcp-client` CLI command, not hand-authored — it adds a separate `mcp`-bind-key database/table (`SysMcp`, exposed at `/api/mcp-SysMcp/`), a generated logic file, and an Admin UI entry.
- Full natural-language flow verified live (no OpenAI key required — the client executor's debug mode substitutes a canned tool-context example when the query contains "email"): the example sentence from the prompt correctly found the 3 matching orders (customers 1, 3, 5) and fanned out one `SysEmail` insert per order, correctly logging "email sent" for 2 and "email skipped ... opted out" for the `Silent` customer.
