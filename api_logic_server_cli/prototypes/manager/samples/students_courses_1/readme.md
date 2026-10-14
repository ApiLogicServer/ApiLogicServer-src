---
title: Students & Courses — Attendance Sweep (Resolved)
notes: sibling of samples/students_courses — same project, carried one phase further
source: samples/requirements/students_courses/ (phase 1) + samples/requirements/students_courses_attendance_sweep/ (phase 2)
version: 1.0, 10/13/2026
---
<style>
  -typeset h1,
  -content__button {
    display: none;
  }
</style>

!!! pied-piper ":bulb: TL;DR - Resolving a correctly-blocked clause: the two-phase Executable Requirements workflow, start to finish"

    Created by: copying the already-built [`samples/students_courses`](../students_courses)
    wholesale (phase 1 — no rebuild) + `implement reqs students_courses_attendance_sweep`
    (phase 2, this project only)

    * Phase 1 is identical to `samples/students_courses`: the Course Drop-Off Alert's
      streak/alert logic is correctly left unimplemented — a FIXME, not a guess — because
      nothing in the original requirement explains what writes an `Attendance(status='absent')`
      row when a student simply doesn't show up
    * Phase 2 supplies the missing design decision (an externally-triggered sweep endpoint +
      a new `Enrollment` table) and turns the FIXME into working code
    * Also surfaced a real CE gap mid-build: a re-enabled event handler's signature was copied
      untyped from the file's own commented-out reference code — fixed here, and reinforced in
      `docs/training/logic_bank_patterns.md` PATTERN 1 (gold)

    Status: Reference implementation — the first sample demonstrating a second Executable
    Requirements pass that resolves an earlier run's own blocking finding

# Students & Courses — Attendance Sweep (Resolved)

&nbsp;

You may prefer to view this guide in the browser; [click here](https://apilogicserver.github.io/Docs/Sample-Students-Courses).

&nbsp;

**This project is `samples/students_courses` carried one phase further.** It is not a
different fixture — phase 1 here is the exact same build, same requirements, same correctly-blocked
result. See [`samples/students_courses`](../students_courses) first if you haven't: that
project's own readme explains the two design gaps (streak-vs-count, absence-of-event) a
literal reading of the original requirement does not hint at, and shows the CE catching both
unaided, leaving the Course Drop-Off Alert's streak/alert logic commented out with a FIXME
rather than guessing a trigger mechanism.

This project picks up exactly where that one stops.

&nbsp;

<details markdown>

<summary>What Phase 2 Adds</summary>

<br>

`samples/students_courses`'s own `ad-libs.md` filed a 🔴 Review Required finding: the
Course Drop-Off Alert depends on an `Attendance(status='absent')` row that nothing in the
system ever writes, and listed three candidate strategies without picking one — correctly,
per the CE's "Absence of an Event" rule, since picking a trigger mechanism unprompted would
have been exactly the kind of unrequested design decision that rule exists to prevent.

`samples/requirements/students_courses_attendance_sweep/` supplies that decision: strategy
(a), a scheduled reconciliation job. Assuming an enterprise deployment with clustering, an
in-process timer was rejected in favor of an **external trigger calling a plain API
endpoint** (`POST /api/attendance_sweep`) — the app server stays stateless, and "when to
sweep" becomes infrastructure configuration, not application code. See that requirement
set's own `README.md` for the full design discussion (why external vs. in-process, why a
plain endpoint vs. the Request Pattern, why `class_schedule_id=null` means "sweep everything
due," why `todays_date` exists and is gated behind the same service credential as the rest
of the endpoint).

Implementing it also required a new `Enrollment` table — the sweep's "who was expected at
this session" question has no answer without one, and it turned out to resolve a *second*,
separately-filed finding too: `samples/students_courses`'s `ad-libs.md` had also flagged that
`Course.enrolled_count` was counting Attendance records instead of distinct enrolled
students, for lack of exactly this table. One schema addition, two findings closed.

Once the write path existed, the previously-commented-out streak accumulator and
`course_dropoff` Alert dispatch in `logic/logic_discovery/course_dropoff.py` were re-enabled
— not verbatim, though: the original commented-out reference had a silent `threshold or 2`
fallback if the `SysConfig` row was ever missing, and that fallback was dropped when
re-enabling it, so `SysConfig.current()` now raises instead of silently guessing a default.
The core streak/alert logic itself was already correct from phase 1; only this one
silent-fallback issue needed a deliberate fix on the way back in.

</details>

&nbsp;

<details markdown>

<summary>A Real CE Gap, Found Mid-Build</summary>

<br>

Re-enabling the commented-out event handler kept its signature as originally written:
`def _update_absence_streak_and_alert(row, old_row, logic_row)` — untyped. This project's
own CE (`docs/training/logic_bank_patterns.md` PATTERN 1) already shows the typed form
(`row: models.MyTable, old_row: models.MyTable, logic_row: LogicRow`) as the required
signature — but copying from the file's own existing (untyped) reference code won out over
the already-loaded pattern. Caught by the developer reviewing the diff, not by the
authoring pass itself.

Fixed here, and reinforced in gold `logic_bank_patterns.md` PATTERN 1 with an explicit
warning: copying a signature from existing code in the same file is not an exemption from
this pattern, citing this exact case. See `docs/requirements/transcript.md`'s closing
appendix for the full write-up.

</details>

&nbsp;

<details markdown>

<summary>Candidate Strategies for the Missing Trigger (as originally listed in `samples/students_courses` — (a) is the one this project implements)</summary>

<br>

- **(a) Scheduled reconciliation** *(implemented here, as `POST /api/attendance_sweep`)* — a
  job or an event tied to some other action (e.g. "close out this session") that diffs
  expected-vs-checked-in students once a session ends, and explicitly inserts the missing
  `Attendance(status='absent')` rows.
- **(b) External ownership** — a front-desk or LMS check-in system is solely responsible for
  writing the negative-fact row; this project's rules only react to it once written.
- **(c) Computed staleness, no synthesized row at all** — have the child (Attendance) post its
  own `last_attended_date` onto the parent (`Student.last_attendance_date`) via a normal
  reactive rule, then derive "sessions missed" on demand (in a rule or report) by comparing
  that date against the expected schedule. Nothing needs to be inserted for the non-occurrence
  itself; the gap is computed, not stored.

</details>

&nbsp;

<details markdown>

<summary>Claude Code CLI Instructions - how to build this project</summary>

<br>

Phase 1 was not rebuilt from scratch — `samples/students_courses` (already built, already
showing the correctly-blocked result) was copied wholesale to `samples/students_courses_1`.
Phase 2 was then applied on top of that copy:

```bash title="Phase 1 - copy the already-built, already-blocked project"
cp -r samples/students_courses samples/students_courses_1
```

```bash title="Phase 2 - copy in the second requirement set, then implement it"
cd samples/students_courses_1
cp -r ../requirements/students_courses_attendance_sweep docs/requirements/
```

Then, to the assistant:

```
implement reqs students_courses_attendance_sweep — note it also corrects course_dropoff's
Clause 1 (enrolled_count), update that use case's files too
```

The explicit nudge matters: `students_courses_attendance_sweep/requirements.md` states the
`enrolled_count` correction belongs to `course_dropoff`, not to itself, but "implement reqs
students_courses_attendance_sweep" naturally scopes an assistant's attention to that use
case's own files — easy to read right past the cross-use-case instruction without saying it
out loud.

</details>

&nbsp;

<details markdown>

<summary>Provenance</summary>

<br>

Phase 1 provenance is shared with `samples/students_courses` — see that project's readme.
Phase 2 was built and verified live in this project only: server started, the sweep endpoint
exercised via curl (auth required/absent, idempotency on repeat calls, correct chronological
ordering so the streak accumulator sees absences in sequence), streak and Alert dispatch
confirmed firing on the resulting `Attendance` inserts, then test data reset to a clean
seeded state.

Gold source for phase 1's requirements is `samples/requirements/students_courses/`; for
phase 2, `samples/requirements/students_courses_attendance_sweep/`. Edits to either
requirement set belong there, not in this generated project.

</details>
