"""
If a Member wants a Book that's currently checked out, they're placed on a FIFO Hold
queue for that Book. When the Book is returned, the oldest Hold is marked "ready for
pickup" — the member is notified to come get it (not auto-checked-out to them).
"""
from logic_bank.logic_bank import Rule
from database import models
import logging

app_logger = logging.getLogger(__name__)


def declare_logic():
    Rule.count(derive=models.Book.active_loan_count, as_count_of=models.Loan,
               where=lambda row: row.return_date is None)

    Rule.count(derive=models.Book.hold_count, as_count_of=models.Hold,
               where=lambda row: row.status == 'waiting')

    Rule.formula(derive=models.Book.available,
                 as_expression=lambda row: 1 if row.active_loan_count == 0 else 0)

    Rule.constraint(validate=models.Book,
                     as_condition=lambda row: row.active_loan_count <= 1,
                     error_msg="Book is already checked out — place a Hold instead")

    def _release_hold_on_return(row, old_row, logic_row):
        """Loan event: when a Loan's return_date is first set, mark the oldest waiting
        Hold for this Book as 'ready' so that member can be notified for pickup."""
        just_returned = row.return_date is not None and (old_row is None or old_row.return_date is None)
        if just_returned:
            oldest_hold = logic_row.session.query(models.Hold) \
                .filter(models.Hold.book_id == row.book_id, models.Hold.status == 'waiting') \
                .order_by(models.Hold.requested_date, models.Hold.id) \
                .first()
            if oldest_hold is not None:
                oldest_hold.status = 'ready'

    Rule.row_event(on_class=models.Loan, calling=_release_hold_on_return)
