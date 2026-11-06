"""
A Loan runs 21 days from checkout, with one allowed renewal — blocked if the book has
an active Hold from another member.

Overdue Loans accrue a fine of $0.25/day (configurable via sys_config.fine_rate_per_day),
capped at $10/book (configurable via sys_config.fine_cap_per_book).

A Member's total unpaid fines are tracked; once unpaid fines reach $5 (configurable via
sys_config.fine_block_threshold), the member is blocked from checking out additional
books until fines are paid down.
"""
from logic_bank.logic_bank import Rule
from database import models
from datetime import datetime, timedelta
import logging

app_logger = logging.getLogger(__name__)


def declare_logic():
    # TODO: Review parent-value rules below.
    #   Rule.copy  = snapshot (value frozen at transaction time, no cascade on parent change) ← default

    # sys_config wiring: mirror configurable constants onto the transactional tables
    Rule.copy(derive=models.Member.fine_block_threshold, from_parent=models.SysConfig.fine_block_threshold)
    Rule.copy(derive=models.Loan.fine_rate_per_day, from_parent=models.SysConfig.fine_rate_per_day)
    Rule.copy(derive=models.Loan.fine_cap_per_book, from_parent=models.SysConfig.fine_cap_per_book)
    Rule.copy(derive=models.Loan.loan_period_days, from_parent=models.SysConfig.loan_period_days)

    def _loan_due_date(row, old_row, logic_row):
        """Derive Loan.due_date: checkout_date plus loan_period_days, plus another loan_period_days if renewed."""
        checkout = datetime.strptime(row.checkout_date, "%Y-%m-%d")
        periods = 2 if row.renewed == 1 else 1
        due = checkout + timedelta(days=row.loan_period_days * periods)
        return due.strftime("%Y-%m-%d")

    Rule.formula(derive=models.Loan.due_date, calling=_loan_due_date)

    def _loan_fine_amount(row, old_row, logic_row):
        """Derive Loan.fine_amount: days late (return_date - due_date) * fine_rate_per_day,
        capped at fine_cap_per_book; 0 if not yet returned or not overdue."""
        if row.return_date is None or row.due_date is None:
            return 0
        returned = datetime.strptime(row.return_date, "%Y-%m-%d")
        due = datetime.strptime(row.due_date, "%Y-%m-%d")
        days_late = (returned - due).days
        if days_late <= 0:
            return 0
        amount = round(days_late * row.fine_rate_per_day, 2)
        return min(amount, row.fine_cap_per_book)

    Rule.formula(derive=models.Loan.fine_amount, calling=_loan_fine_amount)

    Rule.formula(derive=models.Loan.fine_balance,
                 as_expression=lambda row: (row.fine_amount or 0) - (row.fine_paid or 0))

    Rule.sum(derive=models.Member.fine_balance, as_sum_of=models.Loan.fine_balance)

    Rule.formula(derive=models.Member.blocked,
                 as_expression=lambda row: 1 if row.fine_balance >= row.fine_block_threshold else 0)

    def _member_not_blocked_for_new_loan(row, old_row, logic_row):
        """Constraint: a member whose unpaid fines have reached the block threshold cannot
        check out a new book; existing loans (returns/renewals) are not retroactively blocked."""
        return not (logic_row.is_inserted() and row.member.blocked == 1)

    Rule.constraint(validate=models.Loan, calling=_member_not_blocked_for_new_loan,
                     error_msg="Member is blocked from borrowing due to unpaid fines")

    def _renewal_blocked_by_hold(row, old_row, logic_row):
        """Constraint: block renewing a Loan (renewed transitions to 1) if another member has
        a waiting Hold on this Loan's Book."""
        renewing_now = row.renewed == 1 and (old_row is None or old_row.renewed == 0)
        if not renewing_now:
            return True
        other_member_hold = logic_row.session.query(models.Hold).filter(
            models.Hold.book_id == row.book_id,
            models.Hold.status == 'waiting',
            models.Hold.member_id != row.member_id
        ).first()
        return other_member_hold is None

    Rule.constraint(validate=models.Loan, calling=_renewal_blocked_by_hold,
                     error_msg="Cannot renew — this book has a waiting hold from another member")
