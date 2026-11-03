# Why this requirement exists

`samples/requirements/students_courses/` is an eval fixture: it checks whether an AI
implementing `course_dropoff`'s requirements notices, unaided, that the Course Drop-Off Alert
clause depends on an `Attendance(status='absent')` row that nothing ever writes — the "Absence
of an Event" case documented in `docs/training/logic_bank_api.md`. Both live runs of that
fixture caught it correctly: the reactive streak/alert logic was built, tested, and then
deliberately left commented out, with a 🔴 Review Required entry in `course_dropoff/ad-libs.md`
listing candidate strategies instead of silently picking one.

This requirement is the follow-up: it answers that blocking question for real, so the
already-validated logic can be turned on.

## Design decisions made in discussion (not in the requirements text itself)

These were worked out conversationally before `requirements.md` was written; recorded here so
the reasoning survives independent of the spec itself.

**Which candidate strategy, and why.** Of the three options `course_dropoff/ad-libs.md` listed
— (a) scheduled reconciliation, (b) external ownership, (c) computed staleness with no
synthesized row — we chose (a): a companion sweep that diffs expected-vs-actual and explicitly
inserts the missing `absent` rows. (b) was rejected because nothing external to this project
was specified as owning that responsibility. (c) was rejected because the existing
`course_dropoff.py` logic (the streak accumulator, the alert dispatch) is already built and
validated against real `Attendance` row inserts — switching to a computed-on-demand model would
throw that away rather than complete it.

**Why an external trigger, not an in-process timer.** Assuming an enterprise deployment with
clustering: an in-process scheduler (a background thread, APScheduler-in-Flask) runs
independently per instance with no built-in coordination, so a clustered deployment would race
multiple instances against the same sweep unless a distributed lock or leader election is added.
Pushing the scheduling decision to an external, inherently-singleton mechanism (a cloud
scheduler, an API gateway cron) avoids that whole class of problem — the app server stays
stateless, and "when to sweep" is infrastructure configuration, not application code.

**Why a plain API endpoint, not the Request Pattern.** The project's `RequestObjectPattern.md`
reserves that pattern for data-driven triggers — a caller inserts a row, an event reacts. The
sweep's trigger is *time*, not a row: there is nothing domain-meaningful for an external caller
to insert except "go check now." That is a plain custom API endpoint
(`api/api_discovery/attendance_sweep.py`), calling ordinary application code, not a LogicBank
rule.

**`class_schedule_id=null` means sweep everything due.** This lets a simple, domain-ignorant
external scheduler ("call this URL every N minutes") work with zero arguments, while still
letting a caller that *does* know the schedule target one session precisely
(`class_schedule_id=47`) — same endpoint, two legitimate callers, no duplicated logic.

**`todays_date` is a testing escape hatch, not a feature.** Time-triggered logic is otherwise
nearly impossible to integration-test ("did the sweep correctly catch a session that ended 2
hours ago?") without controlling what the endpoint thinks "now" is. It must be gated behind the
same service credential as the rest of the endpoint — never a capability any caller can use to
claim a false "now" in production.

**The missing Enrollment table was not a new gap — it was already half-flagged.**
`course_dropoff/ad-libs.md`'s second 🔴 finding noted that `Course.enrolled_count` counts
Attendance records, not distinct enrolled students, because no Enrollment entity exists to count
instead. The sweep needs the same table for an unrelated reason — "who was expected at this
session" requires knowing who's enrolled, independent of whether they ever attended. Both gaps
trace back to the original narrative ("Students enroll in courses...") implying a Student↔Course
relationship that the original build never modeled as a real table — a Step 4b FK-inventory miss
that an un-asked confirmation should have caught the first time. Adding it now closes both
findings with one schema change.

## What this does NOT do

Build or configure the actual external scheduler (cloud cron / API gateway) — this requirement
only builds the endpoint such a scheduler would call. Wiring the real scheduler is a deployment
concern outside this project.
