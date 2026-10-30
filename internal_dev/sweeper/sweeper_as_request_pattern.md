# Proposal: sweepers as Request Pattern rows (default), plain endpoint as opt-out

Status: **proposal, not yet prototyped.** Written 2026-10-29. No CE or sample has been changed.

## Background

A rule engine reacts to rows that arrive. When a requirement depends on a row that may never arrive (a no-show, a missed deadline), no rule can fire. The CE handles this under "Absence of an Event" in `docs/training/logic_bank_api.md`, and strategy (a) is a scheduled reconciliation.

The one implementation is `samples/students_courses_1` (requirements: `samples/requirements/students_courses_attendance_sweep`):
- `api/api_discovery/attendance_sweep.py`: `POST /api/attendance_sweep`, called by an **external scheduler** (an in-process timer was rejected: a clustered deployment would run it once per server instance, and the app should stay stateless).
- Authenticated by a service key (`X-Api-Key` against env `ATTENDANCE_SWEEP_API_KEY`; refuses everything if unset).
- Finds ended sessions with no `swept_at`, inserts `Attendance(status='absent')` rows as ordinary domain inserts (rules fire on commit), stamps `swept_at`, processes sessions chronologically (the streak depends on order).
- No record that a sweep ran, other than a log line.

## Proposal

Make the sweep a **Request Pattern table** (`docs/training/RequestObjectPattern.md`), the default form:

- A table such as `SweepRequest`: request fields (`class_schedule_id` nullable = all due sessions, `as_of`), response fields (`status`, `sessions_processed`, `rows_inserted`, `error_text`, `created_on`).
- A row event on insert does the sweep and fills the response fields.
- The external scheduler stays external. It inserts a request row through the normal authenticated JSON:API with a service user. The API key scheme goes away.
- The Admin App can insert a row to test a sweep by hand.

## Why

- **Record of sweeps**: who/when/what, including "0 inserted" re-runs.
- **One security model**: grants decide who may trigger a sweep.
- **One logic location**: the Request Pattern doc lists "API only" services as an anti-pattern; the current sweeper is that form.
- **Testable** by inserting a row, no HTTP special case.
- The same shape serves other batch-style work (e.g. an interest run per cycle, from the CardDemo study).

## Known problems (must be solved in the prototype)

1. **Failure record.** If the event raises, the whole transaction rolls back, including the request row. Use the EAI consume approach: record status and error text in a fresh session (`record_error_text` style).
2. **No queries or commits inside the event.** The current `sweep_session` uses `session.query` and `session.commit()`. In an event the sweep must walk relationships (course to enrollments, session to attendance) and create each row with `logic_row.new_logic_row(...)`, as the Request Pattern doc's wrapper does for one nested insert. The doc warns of nested flush errors in this area.
3. **Transaction size.** Every inserted row shares one transaction. Fine for a class roster, questionable for a large run. Needs a stated limit and a rule for what to do beyond it.
4. **Ordering and idempotency.** Keep chronological processing and the `swept_at` stamp; a repeat request must be a visible no-op.
5. **Event choice.** Response fields that nothing else reads suggest `after_flush_row_event`; inserts that must be seen by rules in the same pass suggest `early_row_event`. Decide in the prototype.

## Default and opt-out

If adopted, the CE would build the request-row form unless the requirement text opts out, e.g.: "plain endpoint, no request table", "no audit record of sweeps", "bulk sweep, process in batches", or naming an endpoint with a service key.

- ad-libs: 🟡 FYI either way ("built as Request Pattern (default); to change say 'plain endpoint'" / "plain endpoint, per requirement").
- The AI never opts out on its own. If the default cannot work (a sweep that cannot fit one transaction), it raises 🔴 and asks, as it does today for missing-row mechanisms.

## Concerns about making it the default

- The recipe has two known traps (items 1 and 2 above). A default that fails more often than the plain endpoint costs more than it gains.
- One sample is thin evidence for a default.
- **Decision rule**, to apply after the prototype: if the prototype is simple (a small relationship walk plus `new_logic_row` per row, with the failure record working), make the request row the default. If it needs contortions, keep the plain endpoint as the default and offer the request row as the option when an audit trail is wanted.

## Prototype plan

1. Scratch copy of `students_courses_1` (not the sample itself). Replace the endpoint with `SweepRequest` plus event.
2. Run the existing attendance tests; add: a re-run inserts 0; a forced failure leaves the request row with `status` and `error_text`; a sweep through the Admin App path; a larger roster to see transaction behavior.
3. Apply the decision rule above.
4. Only then change gold source: the "Absence of an Event" section of `logic_bank_api.md`, the sample, and the Docs (`org_git/Docs`), per the gold-source workflow.

## Open question

The sample's readme chose a plain endpoint deliberately (external trigger, stateless server). The CE must say which form applies when, so an AI does not choose at random.
