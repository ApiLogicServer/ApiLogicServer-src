# library_rfi — STEP 1b Partial Interview Transcript

**Trigger:** Prompt was otherwise complete (project name + entities given) but explicitly
requested an interview on: "how loans and fines should work, and what should happen when
a member wants a book that's already checked out."

**Original prompt (see `project_creation_prompt.md` for verbatim copy):**
> Create a system called library_rfi for a small public library — tracking members, books,
> and loans.
>
> Interview me to work out the rules: how loans and fines should work, and what should
> happen when a member wants a book that's already checked out.

(The prompt's first line, `// paste this into your AI Assistant:`, is a STEP 0 human-facing
comment and was not acted on.)

---

## Q&A

**Question: Loan period**
Options: 21 days, 1 renewal · 14 days, 2 renewals · No renewals · Other (I'll specify)

**Answered:** 21 days, 1 renewal

**Question: Fines**
Options: Flat rate/day, capped · Flat rate/day, no cap · Grace period then flat rate ·
No fines · *(list continued past what was captured)*

**Answered:** Flat rate/day, capped

**Question: Borrow limit**
Options: Yes — block above a fine threshold · Yes — block on any unpaid fine ·
No — fines don't restrict borrowing

**Answered:** Yes — block above a fine threshold

**Question: Checked-out**
Options: Hold/reservation queue, FIFO · Reject, no waitlist · Hold queue + notification action

**Answered:** Hold/reservation queue, FIFO

**Note on specific numbers:** the options above establish *policy shape* (capped vs.
uncapped, threshold-based vs. any-unpaid-fine, FIFO hold vs. reject), not literal dollar
figures. Only the $0.25/day fine rate has a directly traceable source — answered inline in
plain text (see Tool notes) after the first `AskUserQuestion` batch failed. The $10 fine
cap and $5 block threshold do not appear in any option list captured; they were proposed by
the AI in the synthesis below and accepted via "looks good - proceed," not selected from a
menu. Flagged here rather than left implicit, since `ad-libs.md` describes all four figures
as "confirmed verbatim via the STEP 1b interview" — true for the policy shape and the fine
rate, an overstatement for the cap and threshold amounts specifically.

**AI synthesis, read back to user:**

> Library system (`library_rfi`) tracking Members, Books, and Loans.
>
> - A Loan runs 21 days from checkout, with one allowed renewal — blocked if the book has
>   an active Hold from another member.
> - Overdue Loans accrue a fine of $0.25/day (configurable via `sys_config.fine_rate_per_day`),
>   capped at $10/book (configurable via `sys_config.fine_cap_per_book`).
> - A Member's total unpaid fines are tracked; once unpaid fines reach $5 (configurable via
>   `sys_config.fine_block_threshold`), the member is blocked from checking out additional
>   books until fines are paid down.
> - If a Member wants a Book that's currently checked out, they're placed on a FIFO Hold
>   queue for that Book. When the Book is returned, the oldest Hold is marked "ready for
>   pickup" — the member is notified to come get it (not auto-checked-out to them).

**User:** "looks good - proceed"

---

## Tool notes (process, not requirements)

- First `AskUserQuestion` batch (fine cap / block threshold / renewal-vs-hold, 4 questions)
  failed `InputValidationError` — three "Other" catch-all options were missing the required
  `label` field. Fixed by adding explicit `"label": "Other"`.
- The corrected retry failed again with `AbortError: Tool permission stream closed before
  response received` — no answer captured. The user then answered the fine-rate question
  inline in plain text: **"0.25/day, but it must be configurable."** The remaining three
  questions (fine cap, block threshold, renewal-vs-hold) were then re-asked in a fresh,
  successful `AskUserQuestion` call.
