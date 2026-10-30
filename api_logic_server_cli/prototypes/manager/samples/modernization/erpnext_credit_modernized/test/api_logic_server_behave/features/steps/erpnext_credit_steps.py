"""
Steps for the erpnext_credit features:
  Credit Limit Lookup, Credit Check, Credit Check On Documents, Credit Limit Maintenance
(docs/requirements/erpnext_credit/requirements.md).

Phase 1 (CRUD) tests through JSON:API, plus the one custom API (copy credit limits from group).
Every scenario creates its own uniquely named companies, groups and customers (repeatable).
Users: admin (role sa - not a credit controller), sam (role manager - the credit controller).
"""
from behave import *
import requests, test_utils, time
import re
from pathlib import Path
from decimal import Decimal

HOST = "http://localhost:5656"
API = f"{HOST}/api"
_behave_dir = Path(__file__).parent.parent.parent      # steps -> features -> api_logic_server_behave
_tokens = {}                                             # user -> (header, obtained_at)


# ------------------------------------------------------------------ helpers

def get_truncated_scenario_name(scenario_name: str) -> str:
    """Return a filesystem-safe name <= 25 chars for use as the logic log filename."""
    safe = re.sub(r'[\s()/\\]', '_', scenario_name)
    return safe[:25]


def logic_log_file(scenario_name: str) -> str:
    """Return the absolute path to the per-scenario logic log file."""
    return str(_behave_dir / "logs" / "scenario_logic_logs" / f"{scenario_name}.log")


def headers(context, user: str = None) -> dict:
    """JSON:API headers with a (cached, refreshed every 60 s) bearer token for the scenario's user."""
    user = user or context.user
    cached = _tokens.get(user)
    if cached is None or time.time() - cached[1] > 60:
        cached = (test_utils.login(user), time.time())
        _tokens[user] = cached
    result = {"Content-Type": "application/vnd.api+json"}
    result.update(cached[0])
    return result


def post(context, resource: str, attributes: dict, user: str = None):
    """POST a row; stores the response in context.response; returns the new id, or None if rejected."""
    r = requests.post(f"{API}/{resource}/", json={"data": {"type": resource, "attributes": attributes}},
                      headers=headers(context, user))
    context.response = r
    if r.status_code < 300:
        return int(r.json()["data"]["id"])
    return None


def patch(context, resource: str, row_id: int, attributes: dict, user: str = None):
    """PATCH a row; stores the response in context.response."""
    assert row_id is not None, f"no {resource} to change (it was not created)"
    r = requests.patch(f"{API}/{resource}/{row_id}/",
                       json={"data": {"type": resource, "id": str(row_id), "attributes": attributes}},
                       headers=headers(context, user))
    context.response = r
    return r


def delete(context, resource: str, row_id: int):
    """DELETE a row; stores the response in context.response."""
    assert row_id is not None, f"no {resource} to delete (it was not created)"
    r = requests.delete(f"{API}/{resource}/{row_id}/", headers=headers(context))
    context.response = r
    return r


def get_row(context, resource: str, row_id: int) -> dict:
    """GET one row's attributes."""
    r = requests.get(f"{API}/{resource}/{row_id}/", headers=headers(context, "admin"))
    assert r.status_code == 200, f"GET {resource} {row_id} failed: {r.text}"
    return r.json()["data"]["attributes"]


def bucket(context, customer: str, company: str) -> dict:
    """The CustomerCompany row (outstanding parts) for a customer and company; zeros if none exists yet."""
    params = {"filter[customer_id]": context.ids[("customer", customer)],
              "filter[company_id]": context.ids[("company", company)]}
    r = requests.get(f"{API}/CustomerCompany/", params=params, headers=headers(context, "admin"))
    assert r.status_code == 200, f"GET CustomerCompany failed: {r.text}"
    rows = r.json()["data"]
    if len(rows) == 0:
        return {}
    return rows[0]["attributes"]


def must_succeed(context, what: str):
    """Assert the last request succeeded."""
    assert context.response.status_code < 300, f"{what} failed: {context.response.status_code} {context.response.text}"


def close_to(actual, expected) -> bool:
    return abs(Decimal(str(actual or 0)) - Decimal(str(expected))) < Decimal("0.005")


def unique(context, name: str) -> str:
    return f"{name} {context.suffix}"


def enter_sales_order(context, amount, customer, company, docstatus: int):
    context.so_id = post(context, "SalesOrder", {
        "customer_id": context.ids[("customer", customer)], "company_id": context.ids[("company", company)],
        "grand_total": amount, "per_billed": 0, "status": "To Deliver and Bill" if docstatus == 1 else "Draft",
        "docstatus": docstatus})


def enter_delivery_note(context, customer, company, net_total, grand_total, is_return=0, per_billed=0):
    context.dn_id = post(context, "DeliveryNote", {
        "customer_id": context.ids[("customer", customer)], "company_id": context.ids[("company", company)],
        "net_total": net_total, "grand_total": grand_total, "is_return": is_return, "per_billed": per_billed,
        "status": "Draft", "docstatus": 0})
    must_succeed(context, "Delivery Note insert")


def add_delivery_line(context, qty, net_amount, sales_order_id=None):
    line_id = post(context, "DeliveryNoteItem", {
        "delivery_note_id": context.dn_id, "qty": qty, "returned_qty": 0, "net_amount": net_amount,
        "sales_order_id": sales_order_id})
    must_succeed(context, "Delivery line insert")
    return line_id


def enter_sales_invoice(context, amount, customer, company, is_return=0, is_opening=0):
    context.si_id = post(context, "SalesInvoice", {
        "customer_id": context.ids[("customer", customer)], "company_id": context.ids[("company", company)],
        "grand_total": amount, "is_return": is_return, "is_opening": is_opening, "docstatus": 0})
    must_succeed(context, "Sales Invoice insert")


def add_invoice_line(context, qty, delivery_note_item_id=None, sales_order_id=None):
    context.sil_id = post(context, "SalesInvoiceItem", {
        "sales_invoice_id": context.si_id, "qty": qty,
        "delivery_note_item_id": delivery_note_item_id, "sales_order_id": sales_order_id})
    must_succeed(context, "Invoice line insert")


# ------------------------------------------------------------------ Given

@given('a new credit scenario')
def step_new_scenario(context):
    scenario_name = get_truncated_scenario_name(context.scenario.name)
    context.scenario_name = scenario_name
    # Open the per-scenario logic log BEFORE any API call - only once per scenario.
    test_utils.prt(f'\n\n\n{scenario_name} - starting test\n\n', scenario_name)
    context.suffix = str(int(time.time() * 1000))
    context.user = "admin"
    context.ids = {}
    context.response = None
    context.so_id = context.le_id = context.dn_id = context.dnl_id = context.dnl2_id = None
    context.si_id = context.sil_id = context.je_id = None
    context.credit_limit_rows = {}


@given('a company "{company}" with default credit limit {limit:g}')
def step_company(context, company, limit):
    context.ids[("company", company)] = post(context, "Company", {"name": unique(context, company), "credit_limit": limit}, "admin")
    must_succeed(context, "Company insert")


@given('a customer group "{group}"')
def step_group(context, group):
    context.ids[("group", group)] = post(context, "CustomerGroup", {"name": unique(context, group)}, "admin")
    must_succeed(context, "Customer Group insert")


@given('a customer "{customer}" in group "{group}"')
def step_customer(context, customer, group):
    context.ids[("customer", customer)] = post(context, "Customer", {
        "name": unique(context, customer), "customer_group_id": context.ids[("group", group)]}, "admin")
    must_succeed(context, "Customer insert")


@given('group "{group}" has a credit limit of {limit:g} at "{company}" bypassing the Sales Order check')
def step_group_limit_bypass(context, group, limit, company):
    post(context, "CustomerGroupCreditLimit", {"customer_group_id": context.ids[("group", group)],
         "company_id": context.ids[("company", company)], "credit_limit": limit, "bypass_credit_limit_check": 1}, "admin")
    must_succeed(context, "Group credit limit insert")


@given('group "{group}" has a credit limit of {limit:g} at "{company}"')
def step_group_limit(context, group, limit, company):
    post(context, "CustomerGroupCreditLimit", {"customer_group_id": context.ids[("group", group)],
         "company_id": context.ids[("company", company)], "credit_limit": limit, "bypass_credit_limit_check": 0}, "admin")
    must_succeed(context, "Group credit limit insert")


@given('customer "{customer}" has a credit limit of {limit:g} at "{company}" bypassing the Sales Order check')
def step_customer_limit_bypass(context, customer, limit, company):
    row_id = post(context, "CustomerCreditLimit", {"customer_id": context.ids[("customer", customer)],
                  "company_id": context.ids[("company", company)], "credit_limit": limit, "bypass_credit_limit_check": 1}, "admin")
    must_succeed(context, "Customer credit limit insert")
    context.credit_limit_rows[(customer, company)] = row_id


@given('customer "{customer}" has a credit limit of {limit:g} at "{company}"')
def step_customer_limit(context, customer, limit, company):
    row_id = post(context, "CustomerCreditLimit", {"customer_id": context.ids[("customer", customer)],
                  "company_id": context.ids[("company", company)], "credit_limit": limit, "bypass_credit_limit_check": 0}, "admin")
    must_succeed(context, "Customer credit limit insert")
    context.credit_limit_rows[(customer, company)] = row_id


@given('the user is "{user}"')
def step_user(context, user):
    context.user = user


# ------------------------------------------------------------------ When - Sales Orders

@when('a submitted Sales Order of {amount:g} is entered for "{customer}" at "{company}" with no credit controller role set')
def step_so_no_controller(context, amount, customer, company):
    previous = get_row(context, "SysConfig", 1).get("credit_controller")
    patch(context, "SysConfig", 1, {"credit_controller": None}, "admin")
    must_succeed(context, "clear credit controller role")
    try:
        enter_sales_order(context, amount, customer, company, 1)
        response = context.response
    finally:
        patch(context, "SysConfig", 1, {"credit_controller": previous}, "admin")
        restored = context.response
    context.response = response
    assert restored.status_code < 300, f"restoring the credit controller role failed: {restored.text}"


@when('a submitted Sales Order of {amount:g} is entered for "{customer}" at "{company}"')
def step_so_submitted(context, amount, customer, company):
    enter_sales_order(context, amount, customer, company, 1)


@when('a draft Sales Order of {amount:g} is entered for "{customer}" at "{company}"')
def step_so_draft(context, amount, customer, company):
    enter_sales_order(context, amount, customer, company, 0)


@when('the Sales Order is submitted')
def step_so_submit(context):
    patch(context, "SalesOrder", context.so_id, {"docstatus": 1, "status": "To Deliver and Bill"})


@when('the Sales Order status is changed to "{status}"')
def step_so_status(context, status):
    patch(context, "SalesOrder", context.so_id, {"status": status})


@when('the Sales Order {field} is changed to {value:g}')
def step_so_field(context, field, value):
    patch(context, "SalesOrder", context.so_id, {field: value})


@when('the Sales Order is moved to customer "{customer}"')
def step_so_move(context, customer):
    patch(context, "SalesOrder", context.so_id, {"customer_id": context.ids[("customer", customer)]})
    must_succeed(context, "Sales Order move")


@when('the Sales Order is deleted')
def step_so_delete(context):
    delete(context, "SalesOrder", context.so_id)
    must_succeed(context, "Sales Order delete")


# ------------------------------------------------------------------ When - ledger entries

@when('a ledger entry with debit {debit:g} and credit {credit:g} is posted for "{customer}" at "{company}"')
def step_ledger_entry(context, debit, credit, customer, company):
    context.le_id = post(context, "LedgerEntry", {
        "customer_id": context.ids[("customer", customer)], "company_id": context.ids[("company", company)],
        "debit": debit, "credit": credit, "is_cancelled": 0})
    must_succeed(context, "Ledger entry insert")


@when('the ledger entry debit is changed to {value:g}')
def step_ledger_debit(context, value):
    patch(context, "LedgerEntry", context.le_id, {"debit": value})
    must_succeed(context, "Ledger entry change")


@when('the ledger entry is cancelled')
def step_ledger_cancel(context):
    patch(context, "LedgerEntry", context.le_id, {"is_cancelled": 1})
    must_succeed(context, "Ledger entry cancel")


@when('the ledger entry is uncancelled')
def step_ledger_uncancel(context):
    patch(context, "LedgerEntry", context.le_id, {"is_cancelled": 0})
    must_succeed(context, "Ledger entry uncancel")


@when('the ledger entry is deleted')
def step_ledger_delete(context):
    delete(context, "LedgerEntry", context.le_id)
    must_succeed(context, "Ledger entry delete")


@when('the ledger entry is moved to customer "{customer}"')
def step_ledger_move(context, customer):
    patch(context, "LedgerEntry", context.le_id, {"customer_id": context.ids[("customer", customer)]})
    must_succeed(context, "Ledger entry move")


# ------------------------------------------------------------------ When - Delivery Notes

@when('a draft return Delivery Note is entered for "{customer}" at "{company}" with net total {net:g} and grand total {grand:g}')
def step_dn_return(context, customer, company, net, grand):
    enter_delivery_note(context, customer, company, net, grand, is_return=1)


@when('a draft Delivery Note billed {percent:g} percent is entered for "{customer}" at "{company}" with net total {net:g} and grand total {grand:g}')
def step_dn_billed(context, percent, customer, company, net, grand):
    enter_delivery_note(context, customer, company, net, grand, per_billed=percent)


@when('a draft Delivery Note is entered for "{customer}" at "{company}" with net total {net:g} and grand total {grand:g}')
def step_dn(context, customer, company, net, grand):
    enter_delivery_note(context, customer, company, net, grand)


@when('a delivery line with qty {qty:g} and net amount {amount:g} linked to the Sales Order is added')
def step_dn_line_so(context, qty, amount):
    assert context.so_id is not None, "no Sales Order to link to"
    context.dnl_id = add_delivery_line(context, qty, amount, context.so_id)


@when('a delivery line with qty {qty:g} and net amount {amount:g} is added')
def step_dn_line(context, qty, amount):
    context.dnl_id = add_delivery_line(context, qty, amount)


@when('a second delivery line with qty {qty:g} and net amount {amount:g} is added')
def step_dn_line2(context, qty, amount):
    context.dnl2_id = add_delivery_line(context, qty, amount)


@when('the Delivery Note is submitted')
def step_dn_submit(context):
    patch(context, "DeliveryNote", context.dn_id, {"docstatus": 1, "status": "Submitted"})


@when('the Delivery Note status is changed to "{status}"')
def step_dn_status(context, status):
    patch(context, "DeliveryNote", context.dn_id, {"status": status})
    must_succeed(context, "Delivery Note status change")


@when('the Delivery Note is moved to customer "{customer}"')
def step_dn_move(context, customer):
    patch(context, "DeliveryNote", context.dn_id, {"customer_id": context.ids[("customer", customer)]})
    must_succeed(context, "Delivery Note move")


@when('the delivery line returned_qty is changed to {value:g}')
def step_dn_line_returned(context, value):
    patch(context, "DeliveryNoteItem", context.dnl_id, {"returned_qty": value})
    must_succeed(context, "Delivery line change")


@when('the delivery line is linked to the Sales Order')
def step_dn_line_link(context):
    patch(context, "DeliveryNoteItem", context.dnl_id, {"sales_order_id": context.so_id})
    must_succeed(context, "Delivery line link")


@when('the delivery line is deleted')
def step_dn_line_delete(context):
    delete(context, "DeliveryNoteItem", context.dnl_id)
    must_succeed(context, "Delivery line delete")


# ------------------------------------------------------------------ When - Sales Invoices

@when('a draft return Sales Invoice of {amount:g} is entered for "{customer}" at "{company}"')
def step_si_return(context, amount, customer, company):
    enter_sales_invoice(context, amount, customer, company, is_return=1)


@when('a draft opening Sales Invoice of {amount:g} is entered for "{customer}" at "{company}"')
def step_si_opening(context, amount, customer, company):
    enter_sales_invoice(context, amount, customer, company, is_opening=1)


@when('a draft Sales Invoice of {amount:g} is entered for "{customer}" at "{company}"')
def step_si(context, amount, customer, company):
    enter_sales_invoice(context, amount, customer, company)


@when('an invoice line with qty {qty:g} billing the delivery line is added')
def step_si_line_dn(context, qty):
    add_invoice_line(context, qty, delivery_note_item_id=context.dnl_id)


@when('an invoice line with qty {qty:g} billing nothing but the Sales Order is added')
def step_si_line_so(context, qty):
    add_invoice_line(context, qty, sales_order_id=context.so_id)


@when('an invoice line with qty {qty:g} is added')
def step_si_line(context, qty):
    add_invoice_line(context, qty)


@when('the Sales Invoice is submitted')
def step_si_submit(context):
    patch(context, "SalesInvoice", context.si_id, {"docstatus": 1})


@when('the Sales Invoice is cancelled')
def step_si_cancel(context):
    patch(context, "SalesInvoice", context.si_id, {"docstatus": 2})


@when('the invoice line qty is changed to {value:g}')
def step_si_line_qty(context, value):
    patch(context, "SalesInvoiceItem", context.sil_id, {"qty": value})
    must_succeed(context, "Invoice line change")


@when('the invoice line is moved to the second delivery line')
def step_si_line_move(context):
    patch(context, "SalesInvoiceItem", context.sil_id, {"delivery_note_item_id": context.dnl2_id})
    must_succeed(context, "Invoice line move")


@when('the invoice line is deleted')
def step_si_line_delete(context):
    delete(context, "SalesInvoiceItem", context.sil_id)
    must_succeed(context, "Invoice line delete")


# ------------------------------------------------------------------ When - Journal Entries

@when('a draft Journal Entry at "{company}" with a customer line for "{customer}" with debit {debit:g} and credit {credit:g} is entered')
def step_je(context, company, customer, debit, credit):
    context.je_id = post(context, "JournalEntry", {"company_id": context.ids[("company", company)], "docstatus": 0})
    must_succeed(context, "Journal Entry insert")
    post(context, "JournalEntryAccount", {"journal_entry_id": context.je_id, "party_type": "Customer",
         "customer_id": context.ids[("customer", customer)], "debit": debit, "credit": credit})
    must_succeed(context, "Journal Entry line insert")


@when('the Journal Entry is submitted')
def step_je_submit(context):
    patch(context, "JournalEntry", context.je_id, {"docstatus": 1})


@when('the Journal Entry is cancelled')
def step_je_cancel(context):
    patch(context, "JournalEntry", context.je_id, {"docstatus": 2})
    must_succeed(context, "Journal Entry cancel")


# ------------------------------------------------------------------ When - credit limit maintenance

@when('a second credit limit of {limit:g} at "{company}" is added for customer "{customer}"')
def step_second_customer_row(context, limit, company, customer):
    post(context, "CustomerCreditLimit", {"customer_id": context.ids[("customer", customer)],
         "company_id": context.ids[("company", company)], "credit_limit": limit, "bypass_credit_limit_check": 0}, "admin")


@when('a second credit limit of {limit:g} at "{company}" is added for group "{group}"')
def step_second_group_row(context, limit, company, group):
    post(context, "CustomerGroupCreditLimit", {"customer_group_id": context.ids[("group", group)],
         "company_id": context.ids[("company", company)], "credit_limit": limit, "bypass_credit_limit_check": 0}, "admin")


@when('customer "{customer}" credit limit at "{company}" is changed to {limit:g}')
def step_change_customer_limit(context, customer, company, limit):
    patch(context, "CustomerCreditLimit", context.credit_limit_rows[(customer, company)], {"credit_limit": limit}, "admin")


@when('credit limits are copied from the group for customer "{customer}"')
def step_copy_from_group(context, customer):
    header = headers(context, "admin")
    header["Content-Type"] = "application/json"
    context.response = requests.post(f"{HOST}/copy_credit_limits_from_group",
                                     json={"customer_id": context.ids[("customer", customer)]}, headers=header)


# ------------------------------------------------------------------ Then

@then('the transaction is accepted')
def step_accepted(context):
    r = context.response
    assert r.status_code < 300, f"expected the transaction to be accepted, got {r.status_code}: {r.text}"


@then('the transaction is rejected with "{text}"')
def step_rejected(context, text):
    r = context.response
    assert r.status_code >= 400, f"expected a rejection containing '{text}', got {r.status_code}: {r.text}"
    assert text in r.text, f"rejection message does not contain '{text}': {r.text}"


@then('the delivery line billed_qty is {value:g}')
def step_dn_line_billed(context, value):
    actual = get_row(context, "DeliveryNoteItem", context.dnl_id)["billed_qty"]
    assert close_to(actual, value), f"delivery line billed_qty: expected {value}, got {actual}"


@then('the second delivery line billed_qty is {value:g}')
def step_dn_line2_billed(context, value):
    actual = get_row(context, "DeliveryNoteItem", context.dnl2_id)["billed_qty"]
    assert close_to(actual, value), f"second delivery line billed_qty: expected {value}, got {actual}"


@then('the Delivery Note {field} is {value:g}')
def step_dn_field(context, field, value):
    actual = get_row(context, "DeliveryNote", context.dn_id)[field]
    assert close_to(actual, value), f"Delivery Note {field}: expected {value}, got {actual}"


@then('the {field} for "{customer}" at "{company}" is {value:g}')
def step_bucket_field(context, field, customer, company, value):
    actual = bucket(context, customer, company).get(field, 0)
    assert close_to(actual, value), f"{field} for {customer} at {company}: expected {value}, got {actual}"


@then('the logic log shows "{text}"')
def step_logic_log(context, text):
    log_file = logic_log_file(context.scenario_name)
    assert test_utils.does_file_contain(text, log_file), f"Logic Log missing '{text}' in {log_file}"
