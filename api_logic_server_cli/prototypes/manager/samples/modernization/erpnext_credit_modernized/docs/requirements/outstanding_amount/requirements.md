# outstanding_amount

Verbatim excerpt of docs/requirements/erpnext_credit/requirements.md that drives logic/logic_discovery/outstanding_amount.py

---

## 3. Outstanding amount

For a customer and company, outstanding is the sum of three parts:
1. **Ledger balance**: the sum of `debit` minus the sum of `credit` over the customer's ledger entries for the company that are not cancelled.
2. **Open Sales Orders** (omitted when the caller says to ignore Sales Orders): for each submitted Sales Order of the customer and company that is not Closed and has `per_billed` below 100: `grand total × (100 − per_billed) / 100`.
3. **Delivered but not billed**: for each submitted Delivery Note of the customer and company that is not Closed or Stopped and has a net total above 0, and for each of its lines that has no link to a Sales Order and no link to a Sales Invoice, and whose quantity is greater than the billed quantity plus the returned quantity: `line net amount × (line quantity − billed quantity − returned quantity) / line quantity / note net total × note grand total`. Billed quantity is the quantity on submitted Sales Invoice lines that reference the delivery line, counting invoices that are not returns.
