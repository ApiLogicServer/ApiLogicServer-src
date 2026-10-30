"""
## 2. The credit limit that applies

Feature: Credit Limit Lookup

For a customer and company, the first match wins:
1. The customer's own credit-limit row for that company, if its `credit_limit` is not zero.
2. Otherwise the customer's Customer Group's row for that company, but only if that row's `bypass_credit_limit_check` is off.
3. Otherwise the company's default `credit_limit`.

A limit of 0 or empty means no limit: no credit check is made.

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

version: 1.0
created: 2026-10-29T18:25:00
created_by: claude-opus-5-5 (valjhuber@gmail.com)
"""

from decimal import Decimal
from logic_bank.logic_bank import Rule
from logic_bank.exec_row_logic.logic_row import LogicRow
from logic_bank.util import ConstraintException
from database import models
from logic.logic_discovery.outstanding_amount import find_customer_company, _d


# ---------------------------------------------------------------- section 2 / section 4 helpers

def applicable_credit_limit(session, customer_id, company_id) -> Decimal:
    """Credit Limit Lookup: the customer's own row for the company if its limit is not zero, else the
    customer group's row for the company if its bypass flag is off, else the company default (0 = no limit)."""
    with session.no_autoflush:
        customer_row = session.query(models.CustomerCreditLimit).filter_by(customer_id=customer_id, company_id=company_id).first()
        if customer_row is not None and _d(customer_row.credit_limit) != 0:
            return _d(customer_row.credit_limit)
        customer = session.get(models.Customer, customer_id)
        if customer is not None and customer.customer_group_id is not None:
            group_row = session.query(models.CustomerGroupCreditLimit).filter_by(customer_group_id=customer.customer_group_id, company_id=company_id).first()
            if group_row is not None and group_row.bypass_credit_limit_check != 1:
                return _d(group_row.credit_limit)
        company = session.get(models.Company, company_id)
        return _d(company.credit_limit if company is not None else 0)


def bypass_flag(session, customer_id, company_id) -> bool:
    """Lookup: the customer's credit-limit row's bypass_credit_limit_check for the company (off if there is no row)."""
    bucket = find_customer_company(session, customer_id, company_id)
    return bucket is not None and (bucket.bypass_credit_limit_check or 0) > 0


def _current_user_is_credit_controller(session) -> bool:
    """True only if Accounts Settings names a credit controller role and a signed-in user holds it; no role set, or no user -> False."""
    role = models.SysConfig.current(session).credit_controller
    if not role:
        return False                                # no credit controller role set: nobody is excused
    try:
        from security.system.authorization import Security   # import here: logic loads before security
        return Security.current_user_has_role(role)
    except Exception:
        return False                                # no request / no signed-in user: not excused, the check is enforced


def check_credit(logic_row: LogicRow, customer_id, company_id, ignore_open_sales_orders: bool = False, extra_amount=0) -> bool:
    """Credit Check: rejects (ConstraintException) when the applicable limit is above 0 and outstanding
    (+ extra_amount, without open Sales Orders if ignore_open_sales_orders) is strictly greater than it,
    unless the user holds the credit controller role. Returns True when the transaction may proceed."""
    session = logic_row.session
    credit_limit = applicable_credit_limit(session, customer_id, company_id)
    if credit_limit <= 0:
        logic_row.log(f"credit check: no credit limit for customer {customer_id} / company {company_id} - no check")
        return True
    bucket = find_customer_company(session, customer_id, company_id)
    if bucket is None:
        outstanding = Decimal(0)
    elif ignore_open_sales_orders:
        outstanding = _d(bucket.outstanding_ignoring_sales_orders)
    else:
        outstanding = _d(bucket.outstanding)
    outstanding = outstanding + _d(extra_amount)
    if outstanding <= credit_limit:
        logic_row.log(f"credit check passed: outstanding {outstanding} <= limit {credit_limit}")
        return True
    if _current_user_is_credit_controller(session):
        logic_row.log(f"credit limit crossed ({outstanding} > {credit_limit}) - allowed for credit controller role")
        return True
    customer = session.get(models.Customer, customer_id)
    customer_name = customer.name if customer is not None else customer_id
    raise ConstraintException(
        f"Credit limit has been crossed for customer {customer_name} ({outstanding:.2f}/{credit_limit:.2f})")


# ---------------------------------------------------------------- section 5: where the check runs

def _sales_order_credit_check(row: models.SalesOrder, old_row: models.SalesOrder, logic_row: LogicRow):
    """Derive (constraint) Sales Order credit check: a submitted, not Closed Sales Order - on submit, update after submit
    or reopen from Closed - is checked with check(customer, company) unless the customer's row bypasses the check."""
    docstatus = row.docstatus
    status = row.status
    customer_id = row.customer_id
    company_id = row.company_id
    _ = row.grand_total, row.per_billed, row.open_amount      # dependency anchor: an update after submit re-checks
    if logic_row.is_deleted() or docstatus != 1 or status == 'Closed':
        return True
    if bypass_flag(logic_row.session, customer_id, company_id):
        logic_row.log("credit check bypassed at Sales Order (customer credit-limit row flag)")
        return True
    return check_credit(logic_row, customer_id, company_id, False, 0)


def _delivery_note_credit_check(row: models.DeliveryNote, old_row: models.DeliveryNote, logic_row: LogicRow):
    """Derive (constraint) Delivery Note credit check on submit (not a return, per_billed below 100): flag off - checked if a
    line has no SO and no SI link; flag on - checked if a line has no SI link, ignoring Sales Orders, plus bypass_extra_amount."""
    docstatus = row.docstatus
    is_return = row.is_return
    per_billed = _d(row.per_billed)
    unlinked_line_count = row.unlinked_line_count
    no_invoice_line_count = row.no_invoice_line_count
    bypass_extra_amount = row.bypass_extra_amount
    customer_id = row.customer_id
    company_id = row.company_id
    submitting = docstatus == 1 and (logic_row.is_inserted() or old_row.docstatus != 1)
    if logic_row.is_deleted() or not submitting or is_return == 1 or per_billed >= 100:
        return True
    if not bypass_flag(logic_row.session, customer_id, company_id):
        if (unlinked_line_count or 0) == 0:
            return True
        return check_credit(logic_row, customer_id, company_id, False, 0)
    if (no_invoice_line_count or 0) == 0:
        return True
    return check_credit(logic_row, customer_id, company_id, True, bypass_extra_amount)


def _delivery_line_grand_total_share(row: models.DeliveryNoteItem, old_row: models.DeliveryNoteItem, logic_row: LogicRow):
    """Derive grand_total_share: line net_amount / note net_total x note grand_total (0 when the note's net_total is 0)."""
    net_amount = _d(row.net_amount)
    note_net_total = _d(row.delivery_note.net_total)
    note_grand_total = _d(row.delivery_note.grand_total)
    if note_net_total == 0:
        return Decimal(0)
    return net_amount / note_net_total * note_grand_total


def _delivery_note_bypass_extra_amount(row: models.DeliveryNote, old_row: models.DeliveryNote, logic_row: LogicRow):
    """Derive bypass_extra_amount: the note's grand_total if its net_total is 0; else the grand-total share of lines with no
    Sales Invoice link that have a Sales Order link - or of every such line while the note is a draft."""
    docstatus = row.docstatus
    net_total = _d(row.net_total)
    grand_total = _d(row.grand_total)
    uninvoiced_share = _d(row.uninvoiced_share)
    so_linked_uninvoiced_share = _d(row.so_linked_uninvoiced_share)
    if net_total == 0:
        return grand_total
    return uninvoiced_share if docstatus == 0 else so_linked_uninvoiced_share


def _sales_invoice_credit_check(row: models.SalesInvoice, old_row: models.SalesInvoice, logic_row: LogicRow):
    """Derive (constraint) Sales Invoice credit check on submit (not a return, not opening): checked if the flag is on or a line
    has neither a Sales Order nor a Delivery Note link, with check(customer, company, ignore=flag)."""
    docstatus = row.docstatus
    is_return = row.is_return
    is_opening = row.is_opening
    unlinked_line_count = row.unlinked_line_count
    customer_id = row.customer_id
    company_id = row.company_id
    submitting = docstatus == 1 and (logic_row.is_inserted() or old_row.docstatus != 1)
    if logic_row.is_deleted() or not submitting or is_return == 1 or is_opening == 1:
        return True
    flag = bypass_flag(logic_row.session, customer_id, company_id)
    if not flag and (unlinked_line_count or 0) == 0:
        return True
    return check_credit(logic_row, customer_id, company_id, flag, 0)


def _journal_entry_credit_check(row: models.JournalEntry, old_row: models.JournalEntry, logic_row: LogicRow):
    """Derive (constraint) Journal Entry credit check on submit: for each customer with a line debit above 0,
    check(customer, company, ignore=flag)."""
    docstatus = row.docstatus
    company_id = row.company_id
    submitting = docstatus == 1 and (logic_row.is_inserted() or old_row.docstatus != 1)
    if logic_row.is_deleted() or not submitting:
        return True
    journal_entry_id = row.id
    customers = []
    with logic_row.session.no_autoflush:
        lines = logic_row.session.query(models.JournalEntryAccount).filter_by(journal_entry_id=journal_entry_id).all()
    for each_line in lines:
        if each_line.party_type == 'Customer' and each_line.customer_id is not None and _d(each_line.debit) > 0:
            if each_line.customer_id not in customers:
                customers.append(each_line.customer_id)
    for each_customer_id in customers:
        flag = bypass_flag(logic_row.session, each_customer_id, company_id)
        check_credit(logic_row, each_customer_id, company_id, flag, 0)
    return True


def declare_logic():
    """Credit limit lookup (section 2), credit check (section 4) and where it runs (section 5)."""

    # Delivery Note line counts and the flag-on extra amount
    Rule.count(derive=models.DeliveryNote.unlinked_line_count, as_count_of=models.DeliveryNoteItem, where=lambda row: row.sales_order_id is None and row.sales_invoice_id is None)
    Rule.count(derive=models.DeliveryNote.no_invoice_line_count, as_count_of=models.DeliveryNoteItem, where=lambda row: row.sales_invoice_id is None)
    Rule.formula(derive=models.DeliveryNoteItem.grand_total_share, calling=_delivery_line_grand_total_share)
    Rule.sum(derive=models.DeliveryNote.uninvoiced_share, as_sum_of=models.DeliveryNoteItem.grand_total_share, where=lambda row: row.sales_invoice_id is None)
    Rule.sum(derive=models.DeliveryNote.so_linked_uninvoiced_share, as_sum_of=models.DeliveryNoteItem.grand_total_share, where=lambda row: row.sales_invoice_id is None and row.sales_order_id is not None)
    Rule.formula(derive=models.DeliveryNote.bypass_extra_amount, calling=_delivery_note_bypass_extra_amount)

    # Sales Invoice lines with neither a Sales Order nor a Delivery Note link
    Rule.count(derive=models.SalesInvoice.unlinked_line_count, as_count_of=models.SalesInvoiceItem, where=lambda row: row.sales_order_id is None and row.delivery_note_item_id is None)

    # The check, per document - a commit constraint, so it sees outstanding after this transaction's
    # postings and roll-ups have settled (e.g. an invoice's own debit and the delivery lines it bills)
    Rule.commit_constraint(validate=models.SalesOrder, calling=_sales_order_credit_check, error_msg="Credit limit check failed for Sales Order {row.id}")
    Rule.commit_constraint(validate=models.DeliveryNote, calling=_delivery_note_credit_check, error_msg="Credit limit check failed for Delivery Note {row.id}")
    Rule.commit_constraint(validate=models.SalesInvoice, calling=_sales_invoice_credit_check, error_msg="Credit limit check failed for Sales Invoice {row.id}")
    Rule.commit_constraint(validate=models.JournalEntry, calling=_journal_entry_credit_check, error_msg="Credit limit check failed for Journal Entry {row.id}")
