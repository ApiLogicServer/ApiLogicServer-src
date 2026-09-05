# library_rfi — Requirements as Gherkin (BDD)

Same confirmed rules as `library_rfi-transcript.md`, restated as Given/When/Then scenarios
— the format Behave tests are written in (`test/api_logic_server_behave/features/`).

---

```gherkin
Feature: Loan checkout and renewal

  Scenario: A new loan gets a due date one loan period out
    Given the library's loan_period_days is 21
    And a Book with no active Loan
    When a Member checks out the Book
    Then the Loan's due_date is 21 days after checkout_date

  Scenario: Renewing a loan doubles the loan period
    Given a Loan that has not yet been renewed
    And no other Member holds a waiting Hold on the Book
    When the Member renews the Loan
    Then the Loan's due_date is 42 days after checkout_date

  Scenario: A renewal is blocked if another member is holding the book
    Given a Loan for a Book
    And another Member has a waiting Hold on that Book
    When the Loan's Member attempts to renew
    Then the renewal is rejected with "Cannot renew — this book has a waiting hold from another member"

  Scenario: A member's own hold does not block their own renewal
    Given a Loan for a Book
    And the same Member also holds a waiting Hold on that Book
    When the Member attempts to renew
    Then the renewal is accepted

  Scenario: A book that is already checked out cannot be checked out again
    Given a Book with an active Loan (no return_date)
    When a different Member attempts to check out the same Book
    Then the checkout is rejected with "Book is already checked out — place a Hold instead"


Feature: Fines

  Scenario: Returning a book on or before the due date accrues no fine
    Given a Loan whose due_date has not yet passed
    When the Member returns the Book
    Then the Loan's fine_amount is 0

  Scenario: Returning a book late accrues a per-day fine
    Given a Loan whose due_date has passed
    And the library's fine_rate_per_day is 0.25
    When the Member returns the Book 5 days late
    Then the Loan's fine_amount is 1.25

  Scenario: Fines are capped per book
    Given a Loan that is far enough overdue that days_late * fine_rate_per_day would
      exceed fine_cap_per_book
    When the Member returns the Book
    Then the Loan's fine_amount equals fine_cap_per_book, not the uncapped amount

  Scenario: A member's fine balance is the total of all their unpaid loan fines
    Given a Member with two overdue, unpaid Loans of fine_amount 2.00 and 3.00
    Then the Member's fine_balance is 5.00

  Scenario: A member is blocked once unpaid fines reach the threshold
    Given a Member whose fine_balance has reached fine_block_threshold (5.00)
    When the Member attempts to check out a new Book
    Then the checkout is rejected with "Member is blocked from borrowing due to unpaid fines"

  Scenario: A blocked member's existing loans are not retroactively invalidated
    Given a Member with an existing Loan, currently in good standing
    When a later, unrelated Loan pushes the Member's fine_balance over fine_block_threshold
    Then the earlier, already-existing Loan remains valid and unaffected

  Scenario: Paying down fines unblocks the member
    Given a blocked Member (fine_balance >= fine_block_threshold)
    When enough fine_paid is recorded to bring fine_balance below fine_block_threshold
    Then the Member is no longer blocked


Feature: Holds

  Scenario: A returned book releases the oldest waiting hold
    Given a Book with two waiting Holds, requested in order: Hold A then Hold B
    When a Loan for that Book has its return_date set
    Then Hold A's status becomes "ready"
    And Hold B's status remains "waiting"

  Scenario: Returning a book with no waiting holds changes nothing
    Given a Book with no waiting Holds
    When a Loan for that Book has its return_date set
    Then no Hold is affected

  Scenario: A book with an active loan is not available
    Given a Book with an active Loan
    Then the Book's available flag is 0

  Scenario: A book with no active loan is available
    Given a Book with no active Loan
    Then the Book's available flag is 1
```
