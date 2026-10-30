# Distilled Requirements (`erpnext_credit`)

Credit control for customers, recovered from the ERPNext source (selling, accounts and stock modules, commit 2f8c531) and amended with two behaviors found in its tests. Scope and simplifications are in section 8.

---

## 1. Data
* **Company**: has a default `credit_limit`.
* **Customer Group**: has credit-limit rows.
* **Customer**: belongs to a Customer Group; has credit-limit rows.
* **Credit-limit row** (on a Customer or a Customer Group): `company`, `credit_limit`, `bypass_credit_limit_check` (default off). A customer or group has at most one row per company; a second row for the same company is rejected.
* **Ledger entry**: customer, company, `debit`, `credit`, cancelled flag.
* **Sales Order**: customer, company, grand total, `per_billed` (percent billed), status (Draft, To Deliver and Bill, Closed, ...), submitted state.
* **Delivery Note**: customer, company, grand total, net total, status (Draft, Submitted, Closed, Stopped), return flag; lines with quantity, returned quantity, net amount, and optional links to a Sales Order and to a Sales Invoice.
* **Sales Invoice**: customer, company, return flag, opening flag; lines with quantity and optional links to a Sales Order and to a Delivery Note line.
* **Journal Entry**: company; account lines with party type, party, `debit`, `credit`.
* **Accounts Settings**: `credit_controller` (a role).

---

## 2. The credit limit that applies

Feature: Credit Limit Lookup

For a customer and company, the first match wins:
1. The customer's own credit-limit row for that company, if its `credit_limit` is not zero.
2. Otherwise the customer's Customer Group's row for that company, but only if that row's `bypass_credit_limit_check` is off.
3. Otherwise the company's default `credit_limit`.

A limit of 0 or empty means no limit: no credit check is made.

---

## 3. Outstanding amount

For a customer and company, outstanding is the sum of three parts:
1. **Ledger balance**: the sum of `debit` minus the sum of `credit` over the customer's ledger entries for the company that are not cancelled.
2. **Open Sales Orders** (omitted when the caller says to ignore Sales Orders): for each submitted Sales Order of the customer and company that is not Closed and has `per_billed` below 100: `grand total × (100 − per_billed) / 100`.
3. **Delivered but not billed**: for each submitted Delivery Note of the customer and company that is not Closed or Stopped and has a net total above 0, and for each of its lines that has no link to a Sales Order and no link to a Sales Invoice, and whose quantity is greater than the billed quantity plus the returned quantity: `line net amount × (line quantity − billed quantity − returned quantity) / line quantity / note net total × note grand total`. Billed quantity is the quantity on submitted Sales Invoice lines that reference the delivery line, counting invoices that are not returns.

---

## 4. The credit check

Feature: Credit Check

`check(customer, company, ignore_open_sales_orders, extra_amount)`:
1. Find the limit (section 2). If there is none, stop.
2. Outstanding is section 3 (omitting part 2 if `ignore_open_sales_orders`), plus `extra_amount`.
3. If the limit is above 0 and outstanding is strictly greater than the limit, the transaction is rejected with a message giving the customer, outstanding and limit. Outstanding equal to the limit is allowed.
4. A user who holds the credit controller role (Accounts Settings) is not rejected. If no credit controller role is set, nobody is excused.

---

## 5. Where the check runs

Feature: Credit Check On Documents

The customer's credit-limit row for the company is read for its `bypass_credit_limit_check` flag (off if there is no row).

* **Sales Order**: on submit, on update after submit, and when reopened from Closed. If the flag is on, no check is made. Otherwise `check(customer, company)`.
* **Delivery Note** (not a return; skipped when `per_billed` is 100): on submit.
  * Flag off: the check is made only if some line has neither a Sales Order nor a Sales Invoice link. `check(customer, company, ignore=false, extra=0)`.
  * Flag on: the check is made if some line has no Sales Invoice link. For each line with no Sales Invoice link, if the line has a Sales Order link or the note is a draft, add `line net amount / note net total × note grand total` to `extra`. If the note's net total is 0, `extra` is the note's grand total. `check(customer, company, ignore=true, extra)`.
* **Sales Invoice** (not a return, not an opening invoice): on submit. The check is made if the flag is on, or if some line has neither a Sales Order nor a Delivery Note link. `check(customer, company, ignore=flag)`.
* **Journal Entry**: on submit, for each customer that has a line with a debit above 0: `check(customer, company, ignore=flag)`.

---

## 6. Maintaining limits

Feature: Credit Limit Maintenance

* A Customer or Customer Group with two credit-limit rows for the same company is rejected.
* When a Customer's credit-limit rows change, each row with a non-zero `credit_limit` must be at least the customer's current outstanding for that company (with Sales Orders ignored when that row's flag is on). Otherwise the change is rejected. A row with a zero limit is allowed.
* **Copy from group**: an action on a Customer replaces its credit-limit rows with copies of its Customer Group's rows (company, `credit_limit`, flag).

---

## 7. Out of scope

Stated so they are not guessed at: overdue billing threshold, the preview-mode warnings, the email to credit controllers, multi-currency, cost centers, taxes and discounts (grand total is an input), stock, and how `per_billed` and document statuses are produced (they are inputs).

---

## 8. Simplifications for this rebuild

* One ledger-entry table. Submitting a Sales Invoice posts a debit for its total; a return posts a credit. A Journal Entry line for a customer posts its debit or credit. Cancelling sets the cancelled flag.
* One currency; "base" amounts equal the document amounts.
* Documents are entered with their totals; no item, price or tax calculation.
