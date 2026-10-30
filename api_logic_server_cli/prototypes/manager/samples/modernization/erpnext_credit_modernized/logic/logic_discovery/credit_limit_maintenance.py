"""
## 6. Maintaining limits

Feature: Credit Limit Maintenance

* A Customer or Customer Group with two credit-limit rows for the same company is rejected.
* When a Customer's credit-limit rows change, each row with a non-zero `credit_limit` must be at least the customer's current outstanding for that company (with Sales Orders ignored when that row's flag is on). Otherwise the change is rejected. A row with a zero limit is allowed.
* **Copy from group**: an action on a Customer replaces its credit-limit rows with copies of its Customer Group's rows (company, `credit_limit`, flag).

version: 1.0
created: 2026-10-29T18:32:00
created_by: claude-opus-5-5 (valjhuber@gmail.com)
"""

from logic_bank.logic_bank import Rule
from logic_bank.exec_row_logic.logic_row import LogicRow
from logic_bank.util import ConstraintException
from database import models
from logic.logic_discovery.outstanding_amount import find_customer_company, _d


def _no_other_row(session, model_class, parent_column: str, parent_id, company_id, own_id) -> bool:
    """Helper: True if no other (non-deleted) credit-limit row of model_class has this parent and company."""
    with session.no_autoflush:
        others = session.query(model_class).filter(getattr(model_class, parent_column) == parent_id, model_class.company_id == company_id).all()
    for each in others:
        if each.id != own_id and each not in session.deleted:
            return False
    return True


def _customer_row_unique(row: models.CustomerCreditLimit, old_row: models.CustomerCreditLimit, logic_row: LogicRow):
    """Derive (constraint) CustomerCreditLimit uniqueness: a customer has at most one credit-limit row per company."""
    customer_id = row.customer_id
    company_id = row.company_id
    if logic_row.is_deleted():
        return True
    return _no_other_row(logic_row.session, models.CustomerCreditLimit, "customer_id", customer_id, company_id, row.id)


def _group_row_unique(row: models.CustomerGroupCreditLimit, old_row: models.CustomerGroupCreditLimit, logic_row: LogicRow):
    """Derive (constraint) CustomerGroupCreditLimit uniqueness: a customer group has at most one credit-limit row per company."""
    customer_group_id = row.customer_group_id
    company_id = row.company_id
    if logic_row.is_deleted():
        return True
    return _no_other_row(logic_row.session, models.CustomerGroupCreditLimit, "customer_group_id", customer_group_id, company_id, row.id)


def _limit_covers_outstanding(row: models.CustomerCreditLimit, old_row: models.CustomerCreditLimit, logic_row: LogicRow):
    """Derive (constraint) CustomerCreditLimit maintenance: when the row is inserted or its limit, flag, customer or company
    changes, a non-zero credit_limit must be at least the customer's current outstanding for the company (Sales Orders
    ignored when the row's flag is on); a zero limit is allowed."""
    credit_limit = _d(row.credit_limit)
    bypass = row.bypass_credit_limit_check
    customer_id = row.customer_id
    company_id = row.company_id
    if logic_row.is_deleted():
        return True
    changed = logic_row.is_inserted() or credit_limit != _d(old_row.credit_limit) or bypass != old_row.bypass_credit_limit_check \
        or customer_id != old_row.customer_id or company_id != old_row.company_id
    if not changed or credit_limit == 0:
        return True
    bucket = find_customer_company(logic_row.session, customer_id, company_id)
    if bucket is None:
        return True
    outstanding = _d(bucket.outstanding_ignoring_sales_orders) if bypass == 1 else _d(bucket.outstanding)
    if credit_limit >= outstanding:
        return True
    customer = logic_row.session.get(models.Customer, customer_id)
    customer_name = customer.name if customer is not None else customer_id
    raise ConstraintException(
        f"New credit limit {credit_limit:.2f} for customer {customer_name} is below its current outstanding amount {outstanding:.2f}")


def declare_logic():
    """Credit limit maintenance (section 6). The copy-from-group action is api/api_discovery/copy_credit_limits_from_group.py."""

    Rule.constraint(validate=models.CustomerCreditLimit, calling=_customer_row_unique, error_msg="Customer {row.customer_id} already has a credit-limit row for company {row.company_id}")
    Rule.constraint(validate=models.CustomerGroupCreditLimit, calling=_group_row_unique, error_msg="Customer Group {row.customer_group_id} already has a credit-limit row for company {row.company_id}")
    Rule.constraint(validate=models.CustomerCreditLimit, calling=_limit_covers_outstanding, error_msg="Credit limit is below the current outstanding amount")

    # the customer's own row, rolled up to its (customer, company) bucket - at most one row per company,
    # so the sums are the row's values (read by the credit check and the Sales Order bypass)
    Rule.sum(derive=models.CustomerCompany.customer_credit_limit, as_sum_of=models.CustomerCreditLimit.credit_limit)
    Rule.sum(derive=models.CustomerCompany.bypass_credit_limit_check, as_sum_of=models.CustomerCreditLimit.bypass_credit_limit_check)
