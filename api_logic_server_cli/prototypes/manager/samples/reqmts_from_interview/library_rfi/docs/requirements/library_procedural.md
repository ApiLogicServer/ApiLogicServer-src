# library_rfi — Requirements as Procedural Steps

Same confirmed rules as `library_rfi-transcript.md`, restated the way a developer typically
thinks about them first: as a sequence of steps per transaction, not as invariants on data.
This is the "path-dependent" framing — compare against the declarative rules actually used
in `logic/logic_discovery/loans_and_fines.py` and `holds.py`.

---

## Checkout a book

1. Look up the Book.
2. If the Book already has an active loan (a Loan with no return_date), reject:
   "Book is already checked out — place a Hold instead."
3. Look up the Member.
4. Sum `fine_amount - fine_paid` across all of the Member's Loans to get their current
   fine_balance.
5. If fine_balance >= fine_block_threshold, reject:
   "Member is blocked from borrowing due to unpaid fines."
6. Look up loan_period_days from sys_config.
7. due_date = checkout_date + loan_period_days.
8. Insert the Loan row.

## Renew a loan

1. Look up the Loan.
2. Query for any waiting Hold on this Loan's book_id belonging to a *different* member.
3. If found, reject: "Cannot renew — this book has a waiting hold from another member."
4. Look up loan_period_days from sys_config.
5. due_date = checkout_date + 2 * loan_period_days.
6. Set renewed = 1. Save the Loan.

## Return a book

1. Look up the Loan.
2. Set return_date = today.
3. Look up fine_rate_per_day and fine_cap_per_book (or read them off the Loan if they were
   copied there at checkout).
4. days_late = return_date - due_date.
5. If days_late > 0: fine_amount = min(days_late * fine_rate_per_day, fine_cap_per_book).
   Else: fine_amount = 0.
6. fine_balance = fine_amount - fine_paid. Save the Loan.
7. Re-sum the Member's fine_balance across all their Loans.
8. Recompute the Member's blocked flag: blocked = (fine_balance >= fine_block_threshold).
   Save the Member.
9. Query for the oldest waiting Hold on this Loan's book_id, ordered by requested_date.
10. If found, set that Hold's status = 'ready'. Save it.

## Pay a fine

1. Look up the Loan.
2. fine_paid += payment amount.
3. fine_balance = fine_amount - fine_paid. Save the Loan.
4. Re-sum the Member's fine_balance across all their Loans.
5. Recompute the Member's blocked flag. Save the Member.

## Place a hold

1. Look up the Book.
2. Insert a Hold row: member_id, book_id, requested_date = today, status = 'waiting'.

---

## Where this naturally goes wrong

Four separate procedures above — checkout, return, pay fine, and (implicitly) any future
"cancel a loan" or "waive a fine" path — each need to keep `Member.fine_balance` and
`Member.blocked` correct. Nothing forces that: they're just steps a developer remembers to
add, in every procedure, every time.

- **Return a book** (step 7-8) recomputes the Member's balance/blocked — easy to write,
  because the connection ("returning affects fines") is obvious while writing that function.
- **Pay a fine** (step 4-5) needs the *identical* recompute, but the connection is less
  obvious mid-flow ("I'm just updating a payment column") — this is the step most likely to
  get skipped, silently leaving `blocked` stale until the *next* return or checkout happens
  to touch that Member.
- Add a **waive/write-off fine** feature later, or a **transfer a loan to another member**
  feature, or a **bulk fine adjustment** admin action — each is a new path that needs the
  same two lines duplicated again, and each is a new place to forget them.

This is the same shape of bug the project's A/B test found in the customer/order domain
(missing the `Order.customer_id` reassignment path, missing the `Item.product_id` re-copy
path) — not a hypothetical, a repeatable failure mode of writing logic per-transaction
instead of per-data-invariant. The declarative version doesn't enumerate these paths at
all: `Rule.sum(derive=Member.fine_balance, as_sum_of=Loan.fine_balance)` and
`Rule.formula(derive=Member.blocked, ...)` fire automatically from *any* write that changes
a Loan's fine_balance — checkout, return, payment, a future waive action — with nothing
per-path to remember or miss.
