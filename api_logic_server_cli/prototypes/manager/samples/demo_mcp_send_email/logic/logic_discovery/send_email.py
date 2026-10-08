"""
Send Email

Add a SysEmail table (child of customer) with message, subject and CreatedOn.
When a SysEmail is created, log "email sent", unless the customer has opted out.

version: 1.0
created: 2026-10-07
created_by: claude-sonnet-5 (valjhuber@gmail.com)
"""

from logic_bank.logic_bank import Rule
from database import models


def _sys_email_after_commit(row: models.SysEmail, old_row: models.SysEmail, logic_row):
    """SysEmail event: logs 'email sent' after a SysEmail is committed, unless the
    customer has opted out (Customer.email_opt_out)."""
    if not row.customer.email_opt_out:
        logic_row.log(f"email sent to {row.customer.name} - Subject: {row.subject}")
    else:
        logic_row.log(f"email blocked for {row.customer.name} - customer opted out")


def declare_logic():
    """Business logic rules for Send Email use case."""

    Rule.commit_row_event(on_class=models.SysEmail, calling=_sys_email_after_commit)
