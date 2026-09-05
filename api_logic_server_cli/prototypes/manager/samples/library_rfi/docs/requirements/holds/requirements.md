# Use Case: holds

**Source:** `docs/requirements/library_rfi-transcript.md` (STEP 1b confirmed synthesis)

> If a Member wants a Book that's currently checked out, they're placed on a FIFO Hold
> queue for that Book. When the Book is returned, the oldest Hold is marked "ready for
> pickup" — the member is notified to come get it (not auto-checked-out to them).

Implemented in `logic/logic_discovery/holds.py`.
