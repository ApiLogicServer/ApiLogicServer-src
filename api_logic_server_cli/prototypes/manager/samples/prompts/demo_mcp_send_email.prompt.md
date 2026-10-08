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
