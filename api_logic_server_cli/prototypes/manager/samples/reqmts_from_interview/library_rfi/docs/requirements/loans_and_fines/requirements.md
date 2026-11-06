# Use Case: loans_and_fines

**Source:** `docs/requirements/library_rfi-transcript.md` (STEP 1b confirmed synthesis)

> A Loan runs 21 days from checkout, with one allowed renewal — blocked if the book has
> an active Hold from another member.
>
> Overdue Loans accrue a fine of $0.25/day (configurable via `sys_config.fine_rate_per_day`),
> capped at $10/book (configurable via `sys_config.fine_cap_per_book`).
>
> A Member's total unpaid fines are tracked; once unpaid fines reach $5 (configurable via
> `sys_config.fine_block_threshold`), the member is blocked from checking out additional
> books until fines are paid down.

Implemented in `logic/logic_discovery/loans_and_fines.py`.
