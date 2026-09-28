---
title: Students & Courses
notes: gold source is samples/requirements/students_courses
source: samples/requirements/students_courses/README.md
version: 1.1 for readme, 9/27/2026 - updated after CE v3.47 fix verified live
---
<style>
  -typeset h1,
  -content__button {
    display: none;
  }
</style>

!!! pied-piper ":bulb: TL;DR - CE regression test: two subtle rule-design gaps a literal reading of the requirement won't reveal"

    Created by: › genai-logic create --project_name=students_courses --db_url=sqlite:///samples/requirements/students_courses/docs/requirements/students_courses/db.sqlite

    * Governed Business System: course enrollment capacity + attendance drop-off alerting
    * Deliberately unhinted requirement text — tests whether the CE catches two design gaps unaided
    * Governed by `docs/training/logic_bank_api.md`'s "Running Streaks" and "Absence of an Event" sections — this project is the case that motivated them

    Status: Reference implementation / CE regression fixture

# Students & Courses

&nbsp;

<details markdown>

<summary>What This Sample Checks</summary>

<br>

This is a small, deliberately synthetic fixture (no real people, no external data) built to
test one specific thing: whether an AI implementing business rules from a requirement notices
two subtle problems that its own literal wording doesn't hint at.

**1. Streak vs. count.** `docs/requirements/course_dropoff/requirements.md` states:
`Student.consecutive_absences = count(Attendance where status == 'absent')`. Read literally,
that's a plain `Rule.count` — a lifetime, ever-growing total that never resets. But the
column's own name, "consecutive_absences," is a claim about an unbroken *current* run — a
student absent twice early in the semester who has attended every class since should read 0
today, not "≥2 forever." A plain `Rule.count` cannot express reset-on-attendance; it needs a
fold/accumulator instead.

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

</details>

&nbsp;

<details markdown>

<summary>Candidate Strategies for the Missing Trigger (reference only — not to be chosen unprompted)</summary>

<br>

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

</details>

&nbsp;

<details markdown>

<summary>Claude Code CLI Instructions - how to build this project</summary>

<br>

This simulates a common real-world case: a BA team hands over a requirements folder
(`samples/requirements/students_courses`) — synthetic db, requirements.md, README — against
which a fresh project is created and implemented, blind.

```bash title="Establish Initial State, Execute Requirements"
# A - Create the project
genai-logic create --project_name=students_courses --db_url=sqlite:///samples/requirements/students_courses/docs/requirements/students_courses/db.sqlite

# B - activate Claude Code in the VSCode terminal
claude

# C - use the shared Manager venv (do not create a local project .venv)
! source ../venv/bin/activate

# D - load context engineering to teach claude about rules, GenAI-Logic
Please load `.github/.copilot-instructions.md`.

# E - in created project, get the requirements
! cp -rv ../samples/requirements/students_courses/docs/requirements/students_courses/. docs/requirements/students_courses/ | wc -l

# F - ask Coding Agent to create the system by implementing the requirements
implement reqs students_courses
```

See `RECREATE_PROMPT.md` (in `samples/requirements/students_courses/`) for the single-paste
version of this sequence, plus evaluator notes on what to check afterward — read those only
*after* the run, since they explain what the sample is designed to test and would bias the
implementation if read first.

</details>

&nbsp;

<details markdown>

<summary>Provenance</summary>

<br>

Validated three times: twice in the original health_fit form (a blind-test agent, then a
direct build), and once more here in its final students_courses form — a first run that
exposed a real CE gap (an absence-of-event finding correctly identified, then wrongly filed
as an FYI instead of a blocking review item), followed by a second run, same model, against
the corrected CE (v3.47), which classified it correctly and left the feature unimplemented
with a FIXME as required. This students/courses version restates the same fixture in a domain
with no permission or provenance dependencies, so it can be freely reused, published, and
re-run without waiting on anyone else's consent.

Gold source for this sample's requirements is `samples/requirements/students_courses/` —
edits to the sample belong there, not in this generated project.

</details>
