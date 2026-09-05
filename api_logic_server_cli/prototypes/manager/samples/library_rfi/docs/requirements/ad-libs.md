# library_rfi — Assumptions and Judgment Calls Beyond the Confirmed Spec

The core rules (21-day loan/1 renewal/hold-blocks-renewal, $0.25/day fine capped at $10,
$5 block threshold, FIFO hold queue) were confirmed verbatim via the STEP 1b interview —
see `library_rfi-transcript.md`. Everything below is a design decision made while
translating that confirmed text into schema/rules, not itself interviewed.

- **Hold resolution on return:** the oldest waiting Hold is marked `status='ready'` (not
  auto-checked-out to that member). This was already flagged as a judgment call during
  the interview itself (see transcript) — surfaced again here because it drove a schema
  decision (a `status` column with `waiting`/`ready`/`fulfilled`/`cancelled`, rather than
  a boolean).
- **"Another member" holding the book (renewal block):** interpreted as excluding holds
  placed by the *same* member who is renewing — i.e. a member can't be blocked from
  renewing by their own hold on the same book. Not explicitly stated in the confirmed
  wording ("blocked if another member is holding the book"), but the word "another"
  supports this reading.
- **`loan_period_days` made configurable via `sys_config`:** only the fine rate was
  explicitly requested to be configurable. The 21-day loan period was extracted as a
  `sys_config` column anyway, following the standard constant-extraction convention
  (every rate/threshold/date becomes a named, runtime-configurable column rather than a
  hardcoded literal) — consistent with, not contradicting, the confirmed spec.
- **Fine amounts rounded to 2 decimal places** (currency convention) — not specified.
- **`fine_paid` is a plain client-updatable column**, not a dedicated payment
  action/endpoint — recording a payment is a normal PATCH to `Loan.fine_paid`. No
  payment-processing integration was requested or built.
- **No notification/messaging integration** (email, SMS, Kafka) for "member is notified
  to come get it" — `Hold.status='ready'` is the notification signal; no Request
  Pattern/EAI publish was added since no AI/email/Kafka signal was present in the
  requirements (confirmed not applicable, STEP 4c).
- **No limit on concurrent holds** — a member can hold multiple different books, and
  nothing prevents a member from holding a book more than once historically (old
  fulfilled/cancelled holds aren't deduplicated). Not specified either way.
- **Single Table Inheritance and Allocate patterns:** confirmed not applicable — no
  subtype phrasing ("kinds of member/book") and no "distribute amount across recipients"
  phrasing in the domain.
- **Admin app schema-rebuild swap:** `rebuild-from-database` generated
  `ui/admin/admin-merge.yaml` reflecting the new tables. Since the project had zero
  admin.yaml customizations at that point (fresh from `genai-logic create`), the merged
  file was swapped in directly as `admin.yaml` (previous version kept as
  `admin.yaml.bak`) rather than pausing to ask — there was nothing to protect.
