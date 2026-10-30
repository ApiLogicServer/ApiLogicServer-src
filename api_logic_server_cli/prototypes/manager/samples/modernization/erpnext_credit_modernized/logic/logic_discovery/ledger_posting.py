"""
## 8. Simplifications for this rebuild

* One ledger-entry table. Submitting a Sales Invoice posts a debit for its total; a return posts a credit. A Journal Entry line for a customer posts its debit or credit. Cancelling sets the cancelled flag.
* One currency; "base" amounts equal the document amounts.
* Documents are entered with their totals; no item, price or tax calculation.

version: 1.0
created: 2026-10-29T18:30:00
created_by: claude-opus-5-5 (valjhuber@gmail.com)
"""

from decimal import Decimal
from logic_bank.logic_bank import Rule
from logic_bank.exec_row_logic.logic_row import LogicRow
from database import models
from logic.logic_discovery.outstanding_amount import _d


def _transition(row, old_row, logic_row: LogicRow):
    """Helper: (submitted_now, cancelled_now) for a document's docstatus change in this transaction."""
    new_status = row.docstatus
    old_status = None if logic_row.is_inserted() else old_row.docstatus
    submitted_now = new_status == 1 and old_status != 1
    cancelled_now = new_status == 2 and old_status == 1
    return submitted_now, cancelled_now


def _cancel_entries(entries, logic_row: LogicRow, reason: str):
    """Helper: sets is_cancelled on each ledger entry, with logic (the ledger balance roll-up adjusts)."""
    for each_entry in entries:
        if each_entry.is_cancelled == 1:
            continue
        entry_logic_row = logic_row.user_row_update(row=each_entry, ins_upd_dlt="upd")
        each_entry.is_cancelled = 1
        entry_logic_row.update(reason=reason)


def _post_sales_invoice(row: models.SalesInvoice, old_row: models.SalesInvoice, logic_row: LogicRow):
    """SalesInvoice event: on submit posts one LedgerEntry for the customer and company - a debit of grand_total, or a credit
    for a return - and on cancel sets is_cancelled on the entries it posted (early, so the posting is in outstanding before the credit check)."""
    if logic_row.is_deleted():
        return
    submitted_now, cancelled_now = _transition(row, old_row, logic_row)
    if submitted_now:
        amount = abs(_d(row.grand_total))
        entry_logic_row = logic_row.new_logic_row(models.LedgerEntry)
        entry = entry_logic_row.row
        entry.customer_id = row.customer_id
        entry.company_id = row.company_id
        entry.debit = Decimal(0) if row.is_return == 1 else amount
        entry.credit = amount if row.is_return == 1 else Decimal(0)
        entry.is_cancelled = 0
        entry.sales_invoice = row
        entry_logic_row.insert(reason="Sales Invoice submitted")
    elif cancelled_now:
        _cancel_entries(list(row.LedgerEntryList), logic_row, "Sales Invoice cancelled")


def _post_journal_entry(row: models.JournalEntry, old_row: models.JournalEntry, logic_row: LogicRow):
    """JournalEntry event: on submit posts one LedgerEntry per customer line (party_type Customer) with the line's debit and
    credit, and on cancel sets is_cancelled on the entries those lines posted."""
    if logic_row.is_deleted():
        return
    submitted_now, cancelled_now = _transition(row, old_row, logic_row)
    if not (submitted_now or cancelled_now):
        return
    for each_line in list(row.JournalEntryAccountList):
        if each_line.party_type != 'Customer' or each_line.customer_id is None:
            continue
        if submitted_now:
            entry_logic_row = logic_row.new_logic_row(models.LedgerEntry)
            entry = entry_logic_row.row
            entry.customer_id = each_line.customer_id
            entry.company_id = row.company_id
            entry.debit = _d(each_line.debit)
            entry.credit = _d(each_line.credit)
            entry.is_cancelled = 0
            entry.journal_entry_account = each_line
            entry_logic_row.insert(reason="Journal Entry submitted")
        else:
            _cancel_entries(list(each_line.LedgerEntryList), logic_row, "Journal Entry cancelled")


def declare_logic():
    """Ledger postings from Sales Invoices and Journal Entries (section 8)."""
    Rule.early_row_event(on_class=models.SalesInvoice, calling=_post_sales_invoice)
    Rule.early_row_event(on_class=models.JournalEntry, calling=_post_journal_entry)
