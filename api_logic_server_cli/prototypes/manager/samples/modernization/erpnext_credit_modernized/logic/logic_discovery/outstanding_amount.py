"""
## 3. Outstanding amount

For a customer and company, outstanding is the sum of three parts:
1. **Ledger balance**: the sum of `debit` minus the sum of `credit` over the customer's ledger entries for the company that are not cancelled.
2. **Open Sales Orders** (omitted when the caller says to ignore Sales Orders): for each submitted Sales Order of the customer and company that is not Closed and has `per_billed` below 100: `grand total × (100 − per_billed) / 100`.
3. **Delivered but not billed**: for each submitted Delivery Note of the customer and company that is not Closed or Stopped and has a net total above 0, and for each of its lines that has no link to a Sales Order and no link to a Sales Invoice, and whose quantity is greater than the billed quantity plus the returned quantity: `line net amount × (line quantity − billed quantity − returned quantity) / line quantity / note net total × note grand total`. Billed quantity is the quantity on submitted Sales Invoice lines that reference the delivery line, counting invoices that are not returns.

version: 1.0
created: 2026-10-29T18:20:00
created_by: claude-opus-5-5 (valjhuber@gmail.com)
"""

from decimal import Decimal
from sqlalchemy import insert
from logic_bank.logic_bank import Rule
from logic_bank.exec_row_logic.logic_row import LogicRow
from database import models


def _d(value) -> Decimal:
    """Helper: None-safe Decimal conversion (callers bind row attributes to locals first)."""
    if value is None:
        return Decimal(0)
    return value if isinstance(value, Decimal) else Decimal(str(value))


def find_customer_company(session, customer_id, company_id):
    """Lookup: the CustomerCompany bucket for (customer, company) - pending in this session, or stored - else None."""
    for each in session.new:
        if isinstance(each, models.CustomerCompany) and each.customer_id == customer_id and each.company_id == company_id:
            return each
    with session.no_autoflush:
        return session.query(models.CustomerCompany).filter_by(customer_id=customer_id, company_id=company_id).first()


def _link_customer_company(row, old_row, logic_row: LogicRow):
    """LedgerEntry / SalesOrder / DeliveryNote / CustomerCreditLimit event: sets customer_company (the
    per-customer, per-company outstanding bucket) from customer_id and company_id, creating the bucket on
    first use, so the Rule.sum rules below roll this row into the right customer and company."""
    if logic_row.is_deleted():
        return
    customer_id = row.customer_id
    company_id = row.company_id
    if customer_id is None or company_id is None:
        return
    current = row.customer_company
    if current is not None and current.customer_id == customer_id and current.company_id == company_id:
        return
    session = logic_row.session
    bucket = find_customer_company(session, customer_id, company_id)
    if bucket is None:
        # insert the empty bucket directly (all roll-ups 0) so it has an id now: the engine detects a
        # change of parent (a row moved to another customer or company) by comparing foreign key values
        result = session.execute(insert(models.CustomerCompany.__table__).values(customer_id=customer_id, company_id=company_id))
        with session.no_autoflush:
            bucket = session.get(models.CustomerCompany, result.inserted_primary_key[0])
        logic_row.log(f"created CustomerCompany {bucket.id} for customer {customer_id} / company {company_id}")
    row.customer_company_id = bucket.id
    row.customer_company = bucket


def _sales_order_open_amount(row: models.SalesOrder, old_row: models.SalesOrder, logic_row: LogicRow):
    """Derive open_amount: grand_total x (100 - per_billed) / 100 for a submitted Sales Order that is not Closed and is billed below 100%, else 0."""
    docstatus = row.docstatus
    status = row.status
    grand_total = _d(row.grand_total)
    per_billed = _d(row.per_billed)
    if docstatus != 1 or status == 'Closed' or per_billed >= 100:
        return Decimal(0)
    return grand_total * (Decimal(100) - per_billed) / Decimal(100)


def _invoice_line_counts_as_billed(row: models.SalesInvoiceItem, old_row: models.SalesInvoiceItem, logic_row: LogicRow):
    """Derive counts_as_billed: 1 when the line's Sales Invoice is submitted and is not a return, else 0 (feeds the delivery line's billed quantity)."""
    docstatus = row.sales_invoice.docstatus
    is_return = row.sales_invoice.is_return
    return 1 if docstatus == 1 and is_return != 1 else 0


def _delivery_line_unbilled_amount(row: models.DeliveryNoteItem, old_row: models.DeliveryNoteItem, logic_row: LogicRow):
    """Derive unbilled_amount: for a line with no Sales Order and no Sales Invoice link whose qty exceeds billed + returned qty,
    net_amount x (qty - billed - returned) / qty / note net_total x note grand_total; else 0."""
    sales_order_id = row.sales_order_id
    sales_invoice_id = row.sales_invoice_id
    qty = _d(row.qty)
    billed_qty = _d(row.billed_qty)
    returned_qty = _d(row.returned_qty)
    net_amount = _d(row.net_amount)
    note_net_total = _d(row.delivery_note.net_total)
    note_grand_total = _d(row.delivery_note.grand_total)
    if sales_order_id is not None or sales_invoice_id is not None:
        return Decimal(0)
    if qty <= billed_qty + returned_qty or qty == 0 or note_net_total <= 0:
        return Decimal(0)
    return net_amount * (qty - billed_qty - returned_qty) / qty / note_net_total * note_grand_total


def _delivery_note_unbilled_amount(row: models.DeliveryNote, old_row: models.DeliveryNote, logic_row: LogicRow):
    """Derive unbilled_amount: the sum of the lines' unbilled amounts for a submitted Delivery Note that is not Closed or Stopped and has net_total above 0, else 0."""
    docstatus = row.docstatus
    status = row.status
    net_total = _d(row.net_total)
    unbilled_line_total = _d(row.unbilled_line_total)
    if docstatus != 1 or status in ('Closed', 'Stopped') or net_total <= 0:
        return Decimal(0)
    return unbilled_line_total


def declare_logic():
    """Outstanding amount per customer and company (section 3)."""

    for each_class in [models.LedgerEntry, models.SalesOrder, models.DeliveryNote, models.CustomerCreditLimit]:
        Rule.early_row_event(on_class=each_class, calling=_link_customer_company)

    # Part 1 - ledger balance
    Rule.formula(derive=models.LedgerEntry.amount, as_expression=lambda row: (row.debit or 0) - (row.credit or 0))
    Rule.sum(derive=models.CustomerCompany.ledger_balance, as_sum_of=models.LedgerEntry.amount, where=lambda row: row.is_cancelled != 1)

    # Part 2 - open Sales Orders
    Rule.formula(derive=models.SalesOrder.open_amount, calling=_sales_order_open_amount)
    Rule.sum(derive=models.CustomerCompany.open_sales_order_amount, as_sum_of=models.SalesOrder.open_amount)

    # Part 3 - delivered but not billed
    Rule.formula(derive=models.SalesInvoiceItem.counts_as_billed, calling=_invoice_line_counts_as_billed)
    Rule.sum(derive=models.DeliveryNoteItem.billed_qty, as_sum_of=models.SalesInvoiceItem.qty, where=lambda row: row.counts_as_billed == 1)
    Rule.formula(derive=models.DeliveryNoteItem.unbilled_amount, calling=_delivery_line_unbilled_amount)
    Rule.sum(derive=models.DeliveryNote.unbilled_line_total, as_sum_of=models.DeliveryNoteItem.unbilled_amount)
    Rule.formula(derive=models.DeliveryNote.unbilled_amount, calling=_delivery_note_unbilled_amount)
    Rule.sum(derive=models.CustomerCompany.unbilled_delivery_amount, as_sum_of=models.DeliveryNote.unbilled_amount)

    # Outstanding = part 1 + part 2 + part 3 (and without part 2, for callers that ignore Sales Orders)
    Rule.formula(derive=models.CustomerCompany.outstanding, as_expression=lambda row: (row.ledger_balance or 0) + (row.open_sales_order_amount or 0) + (row.unbilled_delivery_amount or 0))
    Rule.formula(derive=models.CustomerCompany.outstanding_ignoring_sales_orders, as_expression=lambda row: (row.ledger_balance or 0) + (row.unbilled_delivery_amount or 0))
