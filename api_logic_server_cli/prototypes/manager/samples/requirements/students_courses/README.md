# Why this sample exists

This is a small, deliberately synthetic fixture (no real people, no external data) built to
test one specific thing: whether an AI implementing business rules from a requirement notices
two subtle problems that its own literal wording doesn't hint at.

## The two things this sample checks

**1. Streak vs. count.** `course_dropoff/requirements.md` states:
`Student.consecutive_absences = count(Attendance where status == 'absent')`. Read literally,
that's a plain `Rule.count` — a lifetime, ever-growing total that never resets. But the
column's own name, "consecutive_absences," is a claim about an unbroken *current* run — a
student absent twice early in the semester who has attended every class since should read 0
today, not "≥2 forever." A plain `Rule.count` cannot express reset-on-attendance; it needs a
fold/accumulator instead. This case is what motivated the "Running Streaks (Consecutive
Counts)" section now in `docs/training/logic_bank_api.md`.

**2. Absence of an event.** Nothing in the requirement — or anywhere else in the schema —
ever explains what writes an `Attendance(status='absent')` row when a student simply doesn't
show up. A missed class isn't an update to react to; it's a non-event. No LogicBank rule
(or any rule engine) can fire on a row that never arrives. This is a structural gap, not a
modeling oversight: the "Course Drop-Off Alert" clause depends on a trigger mechanism that
doesn't exist yet, and picking one on the AI's own initiative — or worse, building and testing
the alert logic against hand-seeded rows as if the trigger question were already settled —
would create the appearance of a finished, verified feature that has never actually been
exercised against how the row would arrive in real use.

The correct behavior, per the CE's "Absence of an Event" rule: don't guess a trigger
mechanism, and don't implement the reactive alert logic either. Flag the gap, list candidate
strategies in `ad-libs.md`, and stop — leaving every other clause in the requirement
implemented normally.

## Candidate strategies for the missing trigger (for reference — not to be chosen unprompted)

- **(a) Scheduled reconciliation** — a job or an event tied to some other action (e.g.
  "close out this session") that diffs expected-vs-checked-in students once a session ends,
  and explicitly inserts the missing `Attendance(status='absent')` rows.
- **(b) External ownership** — a front-desk or LMS check-in system is solely responsible for
  writing the negative-fact row; this project's rules only react to it once written.
- **(c) Computed staleness, no synthesized row at all** — have the child (Attendance) post its
  own `last_attended_date` onto the parent (`Student.last_attendance_date`) via a normal
  reactive rule, then derive "sessions missed" on demand (in a rule or report) by comparing
  that date against the expected schedule. Nothing needs to be inserted for the non-occurrence
  itself; the gap is computed, not stored.

## How to use this sample

See `RECREATE_PROMPT.md` for a 1-button paste-into-Claude-Code-CLI recreation, including
evaluator notes on what to check afterward (read those only *after* the run — they're written
so as not to hint at the answer to the AI doing the implementing).

## Provenance

Validated twice already in the original health_fit form — once via a blind-test agent with no
memory of this investigation, once via a direct build — both runs reproducing the same two
bugs and the same correct blocking behavior. This students/courses version restates the same
fixture in a domain with no permission or provenance dependencies.
