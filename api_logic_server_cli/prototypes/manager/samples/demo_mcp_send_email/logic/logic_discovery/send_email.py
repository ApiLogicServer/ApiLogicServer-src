"""
Send Email

1. Add a SysEmail table (child of customer) with message, subject and CreatedOn.
2. When a SysEmail is created, log "email sent", unless the customer has opted out.

version: 1.0
created: 2026-10-08T00:00:00
created_by: claude-sonnet-5 (valjhuber@gmail.com)
"""

from logic_bank.logic_bank import Rule
from database import models


def declare_logic():
    """Business logic rules for Send Email use case."""

    def _send_email_if_not_opted_out(row: models.SysEmail, old_row, logic_row):
        """SysEmail event: logs "email sent" on insert, unless the customer has opted out."""
        if not logic_row.is_inserted():
            return
        if row.customer.email_opt_out:
            logic_row.log(f"email skipped - {row.customer.name} opted out")
            return
        logic_row.log(f"email sent - to: {row.customer.email}, subject: {row.subject}")

    Rule.after_flush_row_event(on_class=models.SysEmail, calling=_send_email_if_not_opted_out)
