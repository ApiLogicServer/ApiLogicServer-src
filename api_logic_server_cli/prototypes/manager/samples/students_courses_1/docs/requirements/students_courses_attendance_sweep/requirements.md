---
created: 2026-10-13
created_by: claude-sonnet-5 (valjhuber@gmail.com)
use_case: attendance_sweep
---

# Use Case: Attendance Sweep (resolves the blocked Course Drop-Off clause)

## Context

`docs/requirements/course_dropoff/ad-libs.md` filed a 🔴 Review Required finding: Clause 2's
`consecutive_absences` and Clause 3's alert dispatch depend on an `Attendance(status='absent')`
row being written when a student misses a session — but nothing in the system ever writes one.
This is the "Absence of an Event" case: no rule can fire on a row that never arrives.

This requirement resolves that gap by choosing strategy (b) from that ad-lib's candidate list:
Attendance rows are written **only on check-in** (presence-only entry — no row at all means no
show). A companion process, triggered externally, diffs expected-vs-actual attendance once a
session ends and explicitly inserts the missing `absent` rows. Once those rows exist, the
already-implemented (currently commented-out) streak/alert logic in `course_dropoff.py` can be
enabled unchanged — this requirement only builds the missing write path.

## Design decision: external trigger, not an in-process timer

Assume an enterprise deployment with clustering (multiple API server instances behind a load
balancer). An in-process timer (e.g. a background thread or APScheduler job inside the Flask
app) would run independently in every clustered instance, with no coordination — each instance
would attempt the same sweep, producing duplicate-insert races, unless a distributed lock or
leader-election mechanism is added. That's unnecessary complexity for what is fundamentally a
scheduling decision, not application logic.

Instead: an **external scheduler** (a cloud scheduler/cron, or an API gateway timer) calls a
plain HTTP endpoint on its own schedule. The app server stays stateless; "when to sweep" lives
outside the cluster entirely.

## New schema: Enrollment

Neither this requirement nor the original introduces this need — it already existed. The
original narrative ("Students enroll in courses with scheduled class sessions") implies a
Student↔Course relationship that was never modeled; `Course.enrolled_count` was instead
implemented as a rollup of Attendance records, which `course_dropoff/ad-libs.md`'s second 🔴
finding already flagged as wrong (it counts attendance records, not distinct enrolled students).
The Attendance Sweep needs the same missing table for an unrelated reason — determining who was
*expected* at a session requires knowing who's enrolled, independent of whether they ever
attended. Add it once; it resolves both findings.

```sql
CREATE TABLE enrollment (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id INTEGER NOT NULL REFERENCES students(id),
    course_id INTEGER NOT NULL REFERENCES courses(id)
);
```

`Course.enrolled_count` should be re-derived as `Rule.count(Enrollment where course_id = ...)` —
a plain count of distinct enrolled students — replacing the existing 2-level
Attendance-rollup-based derivation. This is a correction to Clause 1 of `course_dropoff`, not a
new clause; update `course_dropoff.py` and its `requirements.md` accordingly when this is
implemented, per the CE's supported "editing an existing requirements.md" workflow.

## New endpoint: Attendance Sweep

`POST /api/attendance_sweep`

**Purpose:** for each `ClassSchedule` that has ended, find every enrolled student who has no
`Attendance` row for that session, and insert `Attendance(status='absent')` for each one.

**Request body (all fields optional):**

| Field | Type | Default | Meaning |
|---|---|---|---|
| `class_schedule_id` | integer | `null` | If provided, sweep only this session. If `null`, sweep every session whose `end_time` has passed and has not yet been swept. |
| `todays_date` | string (ISO date/datetime) | `null` | If provided, use this as "now" instead of the real wall-clock time, for testing. If `null`, use the real current time. |

**Behavior:**

1. Determine the session(s) to process: either the single `class_schedule_id` given, or every
   `ClassSchedule` whose `end_time` is at or before "now" (real time, or `todays_date` if given)
   that has not already been swept.
2. For each session, for each `Enrollment` row on that session's course: if no `Attendance` row
   exists for that `(student_id, class_schedule_id)` pair, insert
   `Attendance(status='absent', student_id=..., class_schedule_id=...)`.
3. Each such insert is a normal domain insert — it triggers the existing (to-be-uncommented)
   `course_dropoff.py` streak/alert logic exactly as any other Attendance insert would. This
   endpoint does not duplicate or reimplement that logic; it only supplies the missing trigger.
4. **Idempotency:** calling this endpoint twice for the same session must not create duplicate
   `Attendance` rows — the "no row exists for this pair" check in step 2 is what makes a repeat
   call a no-op for sessions already fully processed.
5. **Response:** report, per session processed, how many `absent` rows were inserted (for
   auditability — this is the only trace of "the sweep ran" when there was nothing to do).

**Security:** this endpoint can write data and cascade alerts; it is not a regular user-facing
operation. It must require its own service credential (an API key or service-to-service token),
separate from the normal user JWT login flow and from `security/declare_security.py`'s
role-based grants — the caller is an external scheduler, not a logged-in user.

**`todays_date` restriction:** this parameter exists solely to make the endpoint's time-dependent
behavior testable. It must not be usable to fabricate a false "now" in a production call from an
untrusted caller — gate it behind the same service credential required for the endpoint at all,
not expose it as a general-purpose capability.

## Not in scope for this requirement

- The external scheduler itself (the cloud cron / API gateway config that calls this endpoint)
  is outside this project — this requirement only builds the endpoint it calls.
- Re-enabling the commented-out streak/alert logic in `course_dropoff.py` is a one-line change
  (uncomment + add back `students.last_attendance_absent` via the DDL already described in that
  file's comment) — include it as part of implementing this requirement, since the write path it
  was waiting on now exists.
