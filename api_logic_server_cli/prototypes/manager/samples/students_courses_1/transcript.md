Ready to customize your project?

implement reqs students_courses_attendance_sweep — note it also corrects course_dropoff's Clause 1 (enrolled_count), update that use case's files too

Bash

IN

ls docs/requirements docs/requirements/* logic/logic_discovery; ls docs/training

OUT

docs/requirements/project_creation_prompt.md

docs/requirements/project_creation_report.md

docs/requirements/readme-workflow.md

docs/requirements/transcript.md

docs/requirements:

course_dropoff

project_creation_prompt.md

project_creation_report.md

readme-workflow.md

students_courses

students_courses_attendance_sweep

transcript.md

docs/requirements/course_dropoff:

ad-libs.md

requirements.md

docs/requirements/students_courses:

course_dropoff

db.sqlite

project_creation_prompt.md

docs/requirements/students_courses_attendance_sweep:

README.md

requirements.md

logic/logic_discovery:

__pycache__

auto_discovery.py

course_dropoff.py

readme_logic_discovery.md

system

use_case.py

$readme.md

MCP_Copilot_Integration.md

OVERVIEW.md

README.md

RequestObjectPattern.md

__pycache__

admin_app_1_context.prompt.md

admin_app_2_functionality.prompt.md

admin_app_3_architecture.prompt.md

allocate.md

eai_subscribe.md

evaluator.md

genai_logic_patterns.md

governance.md

health_check.md

implement_requirements.md

logic_bank_api.md

logic_bank_patterns.md

logic_diagrams

logic_example.py

probabilistic_logic.md

probabilistic_logic_guide.md

probabilistic_template.py

queries_dashboards.md

react_map.prompt.md

react_tree.prompt.md

readme_training.md

sample_app.md

security.md

testing.md

Bash

IN

cat docs/requirements/students_courses_attendance_sweep/README.md docs/requirements/students_courses_attendance_sweep/requirements.md; echo ==; cat docs/requirements/course_dropoff/requirements.md docs/requirements/course_dropoff/ad-libs.md; echo =; cat logic/logic_discovery/course_dropoff.py; ls docs/requirements/students_courses/course_dropoff

OUT

Exit code 1

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

| Field               | Type                       | Default | Meaning                                                                                              |
| ------------------- | -------------------------- | ------- | ---------------------------------------------------------------------------------------------------- |
| `class_schedule_id` | integer                    | `null`  | If provided, sweep only this session. If `null`, sweep every session whose `end_time` has passed and has not yet been swept. |
| `todays_date`       | string (ISO date/datetime) | `null`  | If provided, use this as "now" instead of the real wall-clock time, for testing. If `null`, use the real current time. |

**Behavior:**

1. Determine the session(s) to process: either the single `class_schedule_id` given, or every
   `ClassSchedule` whose `end_time` is at or before "now" (real time, or `todays_date` if given)
   that has not already been swept.
1. For each session, for each `Enrollment` row on that session's course: if no `Attendance` row
   exists for that `(student_id, class_schedule_id)` pair, insert
   `Attendance(status='absent', student_id=..., class_schedule_id=...)`.
1. Each such insert is a normal domain insert — it triggers the existing (to-be-uncommented)
   `course_dropoff.py` streak/alert logic exactly as any other Attendance insert would. This
   endpoint does not duplicate or reimplement that logic; it only supplies the missing trigger.
1. **Idempotency:** calling this endpoint twice for the same session must not create duplicate
   `Attendance` rows — the "no row exists for this pair" check in step 2 is what makes a repeat
   call a no-op for sessions already fully processed.
1. **Response:** report, per session processed, how many `absent` rows were inserted (for
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

(eval):1: = not found

Read implement_requirements.md

Read implement_requirements.md (lines 1128-1377)

Bash

IN

cat docs/requirements/course_dropoff/requirements.md; echo =ADLIBS; cat docs/requirements/course_dropoff/ad-libs.md; echo =LOGIC; cat logic/logic_discovery/course_dropoff.py; ls api/api_discovery; sqlite3 database/db.sqlite .schema; sqlite3 database/db.sqlite "select * from sys_config"; cat docs/requirements/project_creation_report.md | tail -30

OUT

Exit code 1

# Use Case: Course Attendance & Drop-Off Requirements

## Narrative & Scope

Students enroll in courses with scheduled class sessions. Attendance at each scheduled session is tracked for adherence.

## Rules & Constraints

1. **Enrollment Capacity**:

   - `Course.enrolled_count = count(Attendance where status in ('attended', 'excused'))`.
   - `Course.enrolled_count <= Course.max_capacity`.
1. **Absence Tracking**:

   - `Student.consecutive_absences = count(Attendance where status == 'absent')`.
   - `Student.total_sessions_completed = count(Attendance where status == 'attended')`.
1. **Course Drop-Off Alert**:

   - If a student has a `consecutive_absences` value of 2 or more, a `course_dropoff` alert is automatically dispatched for advisor follow-up.

(Verbatim excerpt of the requirement that drove `logic/logic_discovery/course_dropoff.py` -

copied from `docs/requirements/students_courses/course_dropoff/requirements.md`, the recreate

sample's bundled copy.)

(eval):1: ====ADLIBS not found

Bash

IN

cat docs/requirements/course_dropoff/ad-libs.md; echo "#####LOGIC"; cat logic/logic_discovery/course_dropoff.py; echo "#####"; ls api/api_discovery; sqlite3 database/db.sqlite .schema; sqlite3 database/db.sqlite "select * from sys_config"; tail -30 docs/requirements/project_creation_report.md

OUT

## Ad-Libs Report

**2 items need your review. 4 FYIs — standard patterns, no action needed.**

---

## Walkthrough

1. **Basic data model** — sys_config, students, courses, class_schedules, attendances, alerts (all pre-existing, project created via `genai-logic create` from an existing `db.sqlite`).
2. **Derived/predicted schema additions** — `class_schedules.attended_count` only (bridge column for the 2-level enrolled_count aggregate). No FK to sys_config — see 🟡 FYI below on why not.
3. **Create db** — DDL via one `ALTER TABLE` + `rebuild-from-database` — 6 tables total, no new tables.
4. **Run impl-req** — rule types used: Rule.count (x3), Rule.sum (x1), Rule.constraint (x1). Clause 2's streak and clause 3's alert dispatch are NOT implemented — blocked, see 🔴 below.
5. **Test data / testing** — verified via a standalone script confirming the capacity constraint rejects an over-capacity insert. Full seed data deferred until the blocking question is resolved (seeding 'absent' rows would misrepresent the actual write path this system will use in production).

<details markdown>
<summary>Full diagnostic detail (DDL change list, rule plan, rejected alternatives, replay log)</summary>

### 🟢 Diagnostic Appendix

#### Pre-Coding Analysis

*(written before any code — both phases completed in order)*

**Phase 1 — Schema Impact Assessment**

Files read: `requirements.md` (course_dropoff, all 3 clauses), original 6-table prompt (from the user's project-creation message), `database/models.py`

| Step                                | Signal                                                                                               |
| ----------------------------------- | ---------------------------------------------------------------------------------------------------- |
| Clause 1 — Enrollment Capacity      | Rule.count/Rule.sum needed, but `Attendance` is a grandchild of `Course` (via `ClassSchedule`) — needs a 2-level bridge column |
| Clause 2 — Absence Tracking         | `total_sessions_completed`: plain Rule.count, safe. `consecutive_absences`: name implies a reset-on-attendance streak AND depends on whether 'absent' Attendance rows are ever actually written in production — see 🔴 below |
| Clause 3 — Course Drop-Off Alert    | Depends on the same 'absent'-row write-path question as clause 2 — blocked together                  |
| (Prompt item 1) SysConfig threshold | Runtime-configurable constant, but `sys_config` is a singleton settings table (one row), not a per-row lookup — `SysConfig.current(session)` (already provided in `database/customize_models.py`), not an FK |

DDL change list *(one row per change — covers ALL steps, run once before any coding)*:

| Table             | Change                                        | Reason                                                        |
| ----------------- | --------------------------------------------- | ------------------------------------------------------------- |
| `class_schedules` | ADD COLUMN `attended_count` INTEGER DEFAULT 0 | Clause 1 — bridge rollup, Course is 2 levels above Attendance |

*No other DDL — no FK to sys_config (see 🟡 FYI), and no schema added for the blocked clause 2/3 streak (deferred until the write-path question is resolved — adding `students.last_attendance_absent` now, for a rule that won't fire in production, would be schema clutter for an unconfirmed design).*

**Phase 2 — CE / Pattern Assessment**

Files read: `logic_bank_api.md` (Running Streaks, Absence of an Event, SysConfig FK+copy/formula tradeoff), `.github/copilot-instructions.md`'s System Creation Services section (SysConfig singleton vs. lookup-entity FK test)

| Step                                       | Rule Plan                                                                                            |
| ------------------------------------------ | ---------------------------------------------------------------------------------------------------- |
| Clause 1                                   | `Rule.count(ClassSchedule.attended_count)` + `Rule.sum(Course.enrolled_count)` + `Rule.constraint(enrolled_count <= max_capacity)` |
| Clause 2 (total_sessions_completed)        | `Rule.count(Student.total_sessions_completed)` (plain, safe)                                         |
| Clause 2 (consecutive_absences) + Clause 3 | **BLOCKED** — see 🔴 Review Required                                                                |

Anti-patterns confirmed clear:

- [x] No parent flag where Rule.count on child table is correct
- [x] No `as_expression=lambda row: my_func(row)` anywhere
- [x] No `session.query()` inside formula or row_event
- [x] `sys_config` correctly treated as a singleton settings table, not given a spurious FK relationship from `students`

**Implementation Plan** *(ordered steps written before any file was changed)*:

| Step | What was planned                                                                                     |
| ---- | ---------------------------------------------------------------------------------------------------- |
| 1    | Run DDL (1 ALTER TABLE statement) + `rebuild-from-database`                                          |
| 2    | Write `logic/logic_discovery/course_dropoff.py` — enrolled_count bridge, total_sessions_completed, active_alert_count; comment out + FIXME the blocked streak/alert clause |
| 3    | Verify via a standalone capacity-constraint rejection test                                           |
| 4    | Start server, confirm clean startup                                                                  |
| 5    | Write this ad-libs report with the blocking finding, before seeding any 'absent' test data           |

---

#### Execution Metrics

| Metric                  | Value                                                                                                |
| ----------------------- | ---------------------------------------------------------------------------------------------------- |
| Strategy Used           | 2-level Rule.count/sum bridge for enrolled_count; plain Rule.count for total_sessions_completed and active_alert_count; consecutive_absences streak + alert dispatch deliberately NOT implemented pending a write-path decision |
| CE Files Loaded         | `.github/copilot-instructions.md` (Executable Requirements + full project CE, via CLAUDE.md; includes this project's own prior build cited back as a governance case — see below), `docs/training/logic_bank_api.md` (full, via CLAUDE.md) |
| Schema Read First       | Yes — `database/models.py` read before any logic file written                                        |
| Sample Data Read        | N/A — no `message_formats/*`, not an EAI use case                                                    |
| Subagent Used           | No — single pass                                                                                     |
| Self-Verification       | Yes — a standalone script confirming the capacity constraint actually rejects an over-capacity insert |
| Lightweight Checks Used | Yes — sqlite3 schema checks + rule-fire log inspection                                               |
| Gate Test Run Count     | 1 (standalone constraint test)                                                                       |
| Gate Test Purpose       | Final verification                                                                                   |
| Error Correction Loops  | 0 this pass — see note below                                                                         |
| Long-Run Diagnostics    | None                                                                                                 |

**Note on this pass vs. the prior build:** an earlier build of this exact use case (different project name, `student_courses` — see the `students_courses_1` directory) implemented the streak accumulator and alert dispatch, and hit/fixed 4 real errors doing so (LB tokenizer gotcha, a self-inflicted repeat of it, `session.add()` bypassing LogicBank's rule chain, an optimistic-locking conflict during a pre-existing-row backfill). That build's own ad-libs.md correctly *identified* the "is 'absent' actually written?" ambiguity but classified it as 🟡 FYI and shipped the feature anyway — this project's own `.github/copilot-instructions.md` has since been updated (citing "student_courses, Sep 2026") to say that classification was wrong: this class of ambiguity must be 🔴 and blocking, not a footnoted assumption. Same source, same finding, corrected classification and behavior this pass. The validated accumulator/dispatch code from that build is preserved as a commented-out reference in `course_dropoff.py` rather than re-litigated from scratch, since its own correctness was already live-verified — what changed is not implementing it *now*, not doubt about whether it works.

---

### 🔴 Review Required

| Location                                                                        | Issue                                                                                                | Action                                                                                               |
| ------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------- |
| `logic/logic_discovery/course_dropoff.py` (FIXME comment, streak/alert section) | **Blocking — Absence of an Event.** Clause 2's `consecutive_absences` and Clause 3's alert dispatch both depend on an Attendance row with `status='absent'` actually being written when a student misses a session. `requirements.md` lists `'absent'` as one of three explicit per-session status values, which is suggestive of explicit roll-call (an instructor records one row per student per session, including misses) — but does NOT explicitly state this; a presence-only entry model (a row is created only when a student checks in, so a miss produces no row at all) is an equally plausible reading that the requirement text does not rule out. Per this project's own CE (Absence of an Event / STEP 8), this ambiguity is a BLOCKING finding, not a flag-and-continue one — implementing the reactive logic without resolving it would produce a feature that looks tested (hand-seeded rows exercise the streak/alert code correctly) but is structurally blind to whether it will ever fire in production. | Confirm which write path applies: **(a)** explicit roll-call — an instructor/system calls `POST /api/Attendance/` once per student per scheduled session, always, recording attended/excused/absent explicitly (if so, the existing generic JSON:API endpoint already IS the write path — no new mechanism needed, just confirmation); **(b)** presence-only entry — a row is written only when a student checks in, and a miss is inferred from a scheduled session having fewer Attendance rows than enrolled students (would need a companion process — a scheduled sweep or an event tied to `ClassSchedule.end_time` elapsing — that diffs expected vs. actual and inserts the missing `'absent'` rows; nothing does this today); **(c)** some other mechanism specific to how this system will actually be operated. Once confirmed, uncomment the reference implementation in `course_dropoff.py` (already written and its logic previously live-verified — correct streak reset/rebuild behavior and single alert dispatch on threshold crossing) and, if (b), also build the missing companion write path first. |
| `logic/logic_discovery/course_dropoff.py:33-40`                                 | `Course.enrolled_count` is implemented literally per Clause 1's own formula text: a 2-level sum of Attendance rows (attended/excused) across ALL of a course's class_schedules. This counts attendance *records*, not distinct enrolled *students* — a student attending N sessions adds N to enrolled_count, not 1. As written, enrolled_count will grow every session and can exceed `max_capacity` even with a small, genuinely-fixed roster, which conflicts with "capacity" as commonly understood. There is no separate Enrollment entity in the given schema to model distinct enrollment directly. | Confirm whether `enrolled_count`/`max_capacity` should instead track distinct students (would need a different design — e.g. an early_row_event that increments only on a student's first qualifying Attendance for that course) or whether the literal per-attendance-record definition, as given, is actually intended. |

---

### 🟡 FYI

- `logic/logic_discovery/course_dropoff.py:22-38` — 2-level `Rule.count`→`Rule.sum` chain used to bridge `Course.enrolled_count` since `Attendance` is a grandchild of `Course` via `ClassSchedule` — standard LogicBank chaining technique.
- `database/models.py` (no FK added) — the runtime-configurable alert threshold (`sys_config.consecutive_absence_threshold`) is read via `models.SysConfig.current(logic_row.session)` (already defined in `database/customize_models.py`), NOT an FK + `Rule.copy`/`Rule.formula` from `students`. `sys_config` is a singleton settings table (one row, no real cardinality) — a `students.sys_config_id` FK would model no actual relationship a schema reader could explain, even though adding it is easy and the resulting rule works. See this project's own `.github/copilot-instructions.md` System Creation Services section, which cites this exact prior mistake.
- `logic/logic_discovery/course_dropoff.py` (commented-out reference implementation) — the reset-on-attendance streak accumulator (early_row_event carrying a `last_attendance_absent` flag) is preserved from a prior, fully-tested build of this same use case, per `logic_bank_api.md`'s "Running Streaks" guidance (`consecutive_absences` needs reset behavior a plain `Rule.count` can't express) — kept commented out only because of the blocking write-path question above, not because the design itself is unverified.
- This ad-libs deliberately has NO seeded 'absent' test data yet — seeding it would implicitly pick an answer to the blocking question above (that hand-inserting rows is an adequate proxy for the real write path), which is exactly the appearance-of-completeness this project's CE now warns against.

</details>

*(end template)*

#####LOGIC

"""

Use Case: Course Attendance & Drop-Off Requirements

## Narrative & Scope

Students enroll in courses with scheduled class sessions. Attendance at each scheduled session is tracked for adherence.

## Rules & Constraints

1. **Enrollment Capacity**:

   - `Course.enrolled_count = count(Attendance where status in ('attended', 'excused'))`.
   - `Course.enrolled_count <= Course.max_capacity`.
1. **Absence Tracking**:

   - `Student.consecutive_absences = count(Attendance where status == 'absent')`.
   - `Student.total_sessions_completed = count(Attendance where status == 'attended')`.
1. **Course Drop-Off Alert**:

   - If a student has a `consecutive_absences` value of 2 or more, a `course_dropoff` alert is automatically dispatched for advisor follow-up.

version: 1.1

created: 2026-09-27T00:00:00

created_by: claude-sonnet-5 (valjhuber@gmail.com)

"""

from logic_bank.logic_bank import Rule

from database import models

def declare_logic():

    """Business logic rules for Course Attendance & Drop-Off use case."""

    # --- Clause 1: Enrollment Capacity ---

    # Attendance is a grandchild of Course (Course -> ClassSchedule -> Attendance), so the

    # count is bridged through an intermediate ClassSchedule.attended_count rollup, then

    # summed to Course.enrolled_count - the standard 2-level LogicBank chain.

    Rule.count(derive=models.ClassSchedule.attended_count, as_count_of=models.Attendance,

               where=lambda row: row.status in ('attended', 'excused'))

    Rule.sum(derive=models.Course.enrolled_count, as_sum_of=models.ClassSchedule.attended_count)

    Rule.constraint(validate=models.Course,

                     as_condition=lambda row: row.enrolled_count <= row.max_capacity,

                     error_msg="Course {row.course_name} enrolled_count ({row.enrolled_count}) "

                               "exceeds max_capacity ({row.max_capacity})")

    # --- Clause 2 (total_sessions_completed only) ---

    Rule.count(derive=models.Student.total_sessions_completed, as_count_of=models.Attendance,

               where=lambda row: row.status == 'attended')

    # --- active_alert_count rollup (named in the original schema description, item 2) ---

    Rule.count(derive=models.Student.active_alert_count, as_count_of=models.Alert,

               where=lambda row: row.status == 'active')

    # FIXME: consecutive_absences (clause 2) and the course_dropoff Alert dispatch (clause 3)

    # are NOT implemented - see docs/requirements/course_dropoff/ad-libs.md, 🔴 Review Required.

    # BLOCKED pending user confirmation of the Attendance write path for 'absent' rows

    # (explicit roll-call vs. presence-only entry) - see logic_bank_api.md's "Absence of an

    # Event" section. A validated candidate design (reset-on-attendance streak accumulator +

    # new_logic_row-based Alert dispatch, live-tested end-to-end including the capacity

    # constraint rejection path) exists and is ready to enable once that question is answered

    # - see the ad-libs entry for the full commented-out reference implementation.

    # --- Reference implementation (validated in an earlier build of this exact use case,

    # commented out here pending the write-path decision above - do not enable without also

    # adding back `students.last_attendance_absent` via ALTER TABLE + rebuild-from-database):

    #

    # def _update_absence_streak_and_alert(row, old_row, logic_row):

    #     """Attendance event: recomputes Student.consecutive_absences as a reset-on-attendance

    #     streak (the column name means a streak that resets to 0 on any non-absence - a plain

    #     Rule.count would only ever grow). Dispatches a course_dropoff Alert the moment the

    #     streak newly reaches the SysConfig-configured threshold. Scoped to newly-inserted

    #     Attendance rows only.

    #     """

    #     if not logic_row.is_inserted():

    #         return

    #     student = row.student

    #     previous_streak = student.consecutive_absences or 0

    #     is_absent = (row.status == 'absent')

    #     if is_absent:

    #         student.consecutive_absences = previous_streak + 1 if student.last_attendance_absent else 1

    #     else:

    #         student.consecutive_absences = 0

    #     student.last_attendance_absent = 1 if is_absent else 0

    #

    #     # SysConfig is a singleton settings table, not a per-row parent - use the

    #     # .current(session) accessor (database/customize_models.py), not an FK + Rule.copy.

    #     threshold = models.SysConfig.current(logic_row.session).consecutive_absence_threshold or 2

    #     if previous_streak < threshold <= student.consecutive_absences:

    #         alert_logic_row = logic_row.new_logic_row(models.Alert)

    #         alert = alert_logic_row.row

    #         alert.student_id = student.id

    #         alert.alert_type = 'course_dropoff'

    #         alert.status = 'active'

    #         alert.message = (f"{student.first_name} {student.last_name} has "

    #                          f"{student.consecutive_absences} consecutive absences")

    #         alert_logic_row.insert(reason="course_dropoff alert dispatch")

    #

    # Rule.early_row_event(on_class=models.Attendance, calling=_update_absence_streak_and_alert)

#####

__pycache__

auto_discovery.py

mcp_discovery.py

new_service.py

newer_service.py

system.py

CREATE TABLE sys_config (

    id INTEGER PRIMARY KEY AUTOINCREMENT,

    name TEXT NOT NULL UNIQUE,

    consecutive_absence_threshold INTEGER DEFAULT 2

);

CREATE TABLE sqlite_sequence(name,seq);

CREATE TABLE students (

    id INTEGER PRIMARY KEY AUTOINCREMENT,

    first_name TEXT NOT NULL,

    last_name TEXT NOT NULL,

    email TEXT,

    active_alert_count INTEGER DEFAULT 0,

    consecutive_absences INTEGER DEFAULT 0,

    total_sessions_completed INTEGER DEFAULT 0,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP

);

CREATE TABLE courses (

    id INTEGER PRIMARY KEY AUTOINCREMENT,

    course_name TEXT NOT NULL,

    instructor_name TEXT,

    max_capacity INTEGER DEFAULT 30,

    enrolled_count INTEGER DEFAULT 0

);

CREATE TABLE class_schedules (

    id INTEGER PRIMARY KEY AUTOINCREMENT,

    course_id INTEGER NOT NULL,

    session_date TEXT NOT NULL,

    start_time TEXT,

    end_time TEXT, attended_count INTEGER DEFAULT 0,

    FOREIGN KEY (course_id) REFERENCES courses(id)

);

CREATE TABLE attendances (

    id INTEGER PRIMARY KEY AUTOINCREMENT,

    student_id INTEGER NOT NULL,

    class_schedule_id INTEGER NOT NULL,

    status TEXT NOT NULL, -- 'attended', 'excused', 'absent'

    recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (student_id) REFERENCES students(id),

    FOREIGN KEY (class_schedule_id) REFERENCES class_schedules(id)

);

CREATE TABLE alerts (

    id INTEGER PRIMARY KEY AUTOINCREMENT,

    student_id INTEGER NOT NULL,

    alert_type TEXT NOT NULL, -- 'course_dropoff'

    status TEXT NOT NULL DEFAULT 'active', -- 'active', 'resolved'

    message TEXT NOT NULL,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (student_id) REFERENCES students(id)

);

1|default|2

The scaffold provides, out of the box:

* SQLAlchemy ORM models
* Admin Web App
* JSON:API endpoints, MCP Support, and Swagger docs
* LogicBank rules engine
* Framework wiring for security/RBAC, Kafka Message Integration, and AI Rules

See this project's root readme (`readme.md`, or `readme_standard.md` for

demo-named projects where a demo-specific readme replaces it) for what was

actually generated.

The scaffold is extensible: `--from_git=<git-url-or-directory>` overlays your own files

on top of base at creation time - see

[github.com/ApiLogicServer/scaffold-sample](https://github.com/ApiLogicServer/scaffold-sample)

for a minimal example you can clone and extend.

## Next steps

See `project_creation_prompt.md` in this folder for what was requested (inferred from

the create command, unless a real requirements prompt was supplied).

You can still add business logic at any time - say **"implement requirements"** (or

"impl req") to an AI assistant, or write rules directly in `logic/logic_discovery/`.

## Use Cases

*(each `impl req` run appends a link here to its `docs/requirements/<use_case>/ad-libs.md`)*

- [course_dropoff](course_dropoff/ad-libs.md) — Course Attendance & Drop-Off. Enrollment capacity and total_sessions_completed implemented; consecutive_absences streak + course_dropoff alert dispatch **deliberately not implemented** — blocked pending confirmation of the Attendance write path for missed sessions. 2 items need review, 4 FYIs.

Bash

IN

cat api/api_discovery/new_service.py | head -80; cat api/api_discovery/auto_discovery.py | head -40; grep -n "SECURITY\|API_KEY\|SERVICE" config/default.env config/config.py | head -20; grep -n "class ClassSchedule" -A25 database/models.py; sed -n 1,60p database/customize_models.py; ls database/test_data; ls ../; pip list 2>/dev/null | grep -i logicbank; ls ../venv ../../venv 2>/dev/null | head -3

OUT

from flask import request, jsonify

import logging

from api.system.api_utils import safe_log

app_logger = logging.getLogger("api_logic_server_app")

def add_service(app, api, project_dir, swagger_host: str, PORT: str, method_decorators = []):

    pass

    @app.route('/hello_service')

    def hello_service():

        """

        Illustrates:

* Use standard Flask, here for non-database endpoints.

        Test it with:

                http://localhost:5656/hello_service?user=ApiLogicServer

        """

        user = request.args.get('user')

        app_logger.info(f'{safe_log(user)}')

        return jsonify({"result": f'hello from new_service! from {user}'})import importlib

from pathlib import Path

import logging

app_logger = logging.getLogger(__name__)

def discover_services(app, api, project_dir, swagger_host: str, PORT: str):

    """

    Discover services in the services directory

    """

    import os

    method_decorators : list = []

    services = []

    services_path = Path(__file__).parent

    for root, dirs, files in os.walk(services_path):

        for file in files:

            if file.endswith(".py"):

                spec = importlib.util.spec_from_file_location("module.name", services_path.joinpath(file))

                if file.endswith("auto_discovery.py"):

                    pass

                else:

                    services.append(file)

                    each_service = importlib.util.module_from_spec(spec)

                    spec.loader.exec_module(each_service)  # runs "bare" module code (e.g., initialization)

                    each_service.add_service(app, api, project_dir, swagger_host, PORT, method_decorators)  # invoke create function

    app.logger.info(f"..discovered services: {services}")

    return

config/default.env:41:SECURITY_ENABLED = false

config/config.py:145:    if os.getenv('SQLALCHEMY_DATABASE_URI'):  # e.g. export SECURITY_ENABLED=true

config/config.py:169:    SECURITY_ENABLED = os.getenv("SECURITY_ENABLED",False)

config/config.py:170:    SECURITY_PROVIDER =  os.getenv('SECURITY_PROVIDER', 'keycloak')  # type: ignore # type: str  ← STRING here; overwritten as a class below

config/config.py:171:    if os.getenv('SECURITY_ENABLED'):  # e.g. export SECURITY_ENABLED=true

config/config.py:172:        security_export = os.getenv('SECURITY_ENABLED','false').lower().strip()  # type: ignore # type: str

config/config.py:173:        SECURITY_ENABLED = security_export not in ["false", "no"]  # NO SEC

config/config.py:174:        app_logger.debug(f'Security .. overridden from env variable SECURITY_ENABLED: {SECURITY_ENABLED}')

config/config.py:175:    if SECURITY_ENABLED:

config/config.py:176:        # *** HOW SECURITY_PROVIDER WORKS — do not reorder these lines ***

config/config.py:177:        # SECURITY_PROVIDER starts as a STRING from os.getenv() above (e.g. "keycloak" or "sql",

config/config.py:179:        # hardcoded classes, then OVERWRITES SECURITY_PROVIDER with that class reference.

config/config.py:183:        # The original design intent was that SECURITY_PROVIDER could be an arbitrary class

config/config.py:196:        SECURITY_PROVIDER = KC_Authentication_Provider if "keycloak" in str(SECURITY_PROVIDER).lower() else SQL_Authentication_Provider

config/config.py:198:    app_logger.info(f'config.py - security enabled: {SECURITY_ENABLED} using SECURITY_PROVIDER: {str(SECURITY_PROVIDER)}\n')

config/config.py:418:        return_security = self.flask_app.config["SECURITY_ENABLED"]

config/config.py:430:        self.flask_app.config["SECURITY_ENABLED"] = a

config/config.py:436:        return self.flask_app.config["SECURITY_PROVIDER"]

117:class ClassSchedule(Base):  # type: ignore

118-    __tablename__ = 'class_schedules'

119-    _s_collection_name = 'ClassSchedule'  # type: ignore

120-

121-    id = Column(Integer, primary_key=True)

122-    course_id = Column(ForeignKey('courses.id'), nullable=False)

123-    session_date = Column(Text, nullable=False)

124-    start_time = Column(Text)

125-    end_time = Column(Text)

126-    attended_count = Column(Integer, server_default=text("0"))

127-

128-    # parent relationships (access parent)

129-    course : Mapped["Course"] = relationship(back_populates=("ClassScheduleList"))

130-

131-    # child relationships (access children)

132-    AttendanceList : Mapped[List["Attendance"]] = relationship(back_populates="class_schedule")

133-

134-

135-

136-class Attendance(Base):  # type: ignore

137-    __tablename__ = 'attendances'

138-    _s_collection_name = 'Attendance'  # type: ignore

139-

140-    id = Column(Integer, primary_key=True)

141-    student_id = Column(ForeignKey('students.id'), nullable=False)

142-    class_schedule_id = Column(ForeignKey('class_schedules.id'), nullable=False)

from database import models

from safrs import jsonapi_attr

from sqlalchemy.orm import relationship, remote, foreign

import logging

app_logger = logging.getLogger(__name__)

from database.database_discovery.auto_discovery import discover_models

discover_models()

"""

If you wish to drive models from the database schema,

you can use this file to customize your schema (add relationships, derived attributes),

and preserve customizations over iterations (regenerations of models.py).

Called from models.py (classes describing schema, per introspection).

Your Code Goes Here

"""

# SysConfig.current(session) - convenience accessor for the single-row runtime-settings

# table (the starter.sqlite / System Creation Services pattern - see

# docs/training/logic_bank_api.md). SysConfig has no FK from any transactional table (it's

# a global settings row, not a per-row parent), so rule functions that need a threshold

# would otherwise each repeat `logic_row.session.query(models.SysConfig).first()` -

# duplicated code, and a common place to introduce a silent bug (a guessed fallback like

# `config.rate if config else 0.05` that never errors, just quietly uses the wrong value

# forever). Added conditionally: most projects do NOT have a SysConfig table at all, so this

# must not raise or log at import time when it's absent - only .current() itself raises,

# and only when actually called with no row present.

if hasattr(models, 'SysConfig'):

    def _sys_config_current(session):

        """Return the single SysConfig row (runtime thresholds/settings).

        Use `models.SysConfig.current(logic_row.session)` instead of repeating

        `logic_row.session.query(models.SysConfig).first()` in every rule function.

        Raises RuntimeError if the row is missing - a missing SysConfig row means every

        threshold-based rule in the system would silently use None (or a guessed

        fallback), not a recoverable condition to paper over.

        """

        config = session.query(models.SysConfig).first()

        if config is None:

            raise RuntimeError(

                "SysConfig has no row - rules that read SysConfig thresholds/settings "

                "depend on it. Seed one row before running any logic that calls "

                "SysConfig.current()."

            )

        return config

    models.SysConfig.current = staticmethod(_sys_config_current)

__pycache__

alp_init.py

readme.md

response2code.py

test_data_preamble.py

allocate_dept_account_demo

basic_demo_ai_rules-supplier

basic_demo_eai

basic_demo_existing_db

basic_demo_genai_logic

basic_demo_logic_gov

basic_demo_sales_by_month

basic_demo_sample

bd_claude_native_ai

dbs

demo_customs_clvs

demo_customs_surtax

demo_emp_types

demo_mcp_send_email

docker_samples

extend_context_engineering

library_rfi

nw_sample

nw_sample_nocust

portfolio_governance_report.md

prompts

readme_samples.md

requirements

students_courses

students_courses_1

../../venv:

bin

include

Bash

IN

for t in students courses class_schedules attendances alerts; do echo $t $(sqlite3 database/db.sqlite "select count(*) from $t"); done; lsof -i :5656 | head -3; sqlite3 database/db.sqlite "select sqlite_version()"; ls ../../venv/bin | grep -i genai; sed -n 30,60p config/default.env

OUT

students 4

courses 3

class_schedules 5

attendances 4

alerts 0

3.54.0

genai-logic

# APILOGICPROJECT_KAFKA_CONSUMER is a FULL override via from_prefixed_env(); if set,

# include all keys and keep group.id aligned with KAFKA_CONSUMER_GROUP.

# Do not set conflicting values across these two sources.

# KAFKA_SERVER = localhost:9092

# KAFKA_CONSUMER_GROUP = <project>-group1

# APILOGICPROJECT_KAFKA_CONSUMER = "{\"bootstrap.servers\": \"localhost:9092\", \"group.id\": \"<project>-group1\", \"auto.offset.reset\": \"earliest\", \"enable.auto.commit\": \"false\", \"session.timeout.ms\": \"6000\", \"heartbeat.interval.ms\": \"2000\"}"

# APILOGICPROJECT_KAFKA_PRODUCER = "{\"bootstrap.servers\": \"localhost:9092\"}"

# SQLALCHEMY_DATABASE_URI=db.sqlite

SECURITY_ENABLED = false

# if using tunnel for mcp, function, or ai_plugin

# eg, https://tunnel_url.ngrok-free.app

API_LOGIC_SERVER_TUNNEL = "TUNNEL_URL"

Bash

IN

sqlite3 database/db.sqlite "select * from students; select * from courses; select * from class_schedules; select * from attendances;"

OUT

1|Priya|Nair|priya.nair@example.edu|0|0|0|2026-09-27 18:37:39

2|Marcus|Webb|marcus.webb@example.edu|0|0|0|2026-09-27 18:37:39

3|Alice|Nguyen|alice@example.com|0|0|2|2026-09-27 00:00:00.000000

4|Carol|Diaz|carol@example.com|0|0|1|2026-09-27 00:00:00.000000

1|Intro to Statistics|Dr. Patel|30|0

2|Organic Chemistry|Dr. Nkemelu|24|0

3|Intro to Biology|Dr. Smith|50|4

1|1|2026-09-01|09:00|10:00|0

2|1|2026-09-08|09:00|10:00|0

3|1|2026-09-15|09:00|10:00|0

4|3|2026-09-01|09:00|10:00|2

5|3|2026-09-08|09:00|10:00|2

1|3|4|attended|2026-09-27 00:00:00.000000

2|3|5|attended|2026-09-27 00:00:00.000000

3|4|4|excused|2026-09-27 00:00:00.000000

4|4|5|attended|2026-09-27 00:00:00.000000

Bash

IN

cp database/db.sqlite /private/tmp/claude-502/-Users-val-dev-ApiLogicServer-ApiLogicServer-dev-build-and-test-genai-logic-samples-students-courses-1/078541fe-04bf-4204-b3e7-43565908558b/scratchpad/db.sqlite.bak && sqlite3 database/db.sqlite <<'SQL'

CREATE TABLE enrollment (

    id INTEGER PRIMARY KEY AUTOINCREMENT,

    student_id INTEGER NOT NULL REFERENCES students(id),

    course_id INTEGER NOT NULL REFERENCES courses(id),

    UNIQUE (student_id, course_id)

);

ALTER TABLE students ADD COLUMN last_attendance_absent INTEGER DEFAULT 0;

ALTER TABLE class_schedules ADD COLUMN swept_at TEXT;

ALTER TABLE class_schedules DROP COLUMN attended_count;

UPDATE courses SET enrolled_count = 0;

SQL

source ../../venv/bin/activate && genai-logic rebuild-from-database --db_url=sqlite:///database/db.sqlite 2>&1 | tail -5; grep -n "class Enrollment" -A12 database/models.py; grep -n "last_attendance_absent\|swept_at\|attended_count" database/models.py; ls ui/admin

OUT

                                        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

  File "/Users/val/dev/ApiLogicServer/ApiLogicServer-dev/build_and_test/genai-logic/venv/lib/python3.13/site-packages/api_logic_server_cli/create_from_model/api_logic_server_utils.py", line 480, in replace_string_in_file

    with open(Path(in_file), 'r', encoding="utf-8") as file:

         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

FileNotFoundError: [Errno 2] No such file or directory: '/Users/val/dev/ApiLogicServer/ApiLogicServer-dev/build_and_test/genai-logic/samples/students_courses_1/.vscode/settings.json'

139:class Enrollment(Base):  # type: ignore

140-    __tablename__ = 'enrollment'

141-    _s_collection_name = 'Enrollment'  # type: ignore

142-    __table_args__ = (

143-        UniqueConstraint('student_id', 'course_id'),

144-    )

145-

146-    id = Column(Integer, primary_key=True)

147-    student_id = Column(ForeignKey('students.id'), nullable=False)

148-    course_id = Column(ForeignKey('courses.id'), nullable=False)

149-

150-    # parent relationships (access parent)

151-    course : Mapped["Course"] = relationship(back_populates=("EnrollmentList"))

77:    last_attendance_absent = Column(Integer, server_default=text("0"))

129:    swept_at = Column(Text)

__pycache__

admin-merge.yaml

admin.yaml

admin_loader.py

authentication_admin.yaml

home.js

Bash

IN

ls -la ui/admin docs/db.dbml; grep -c Enrollment ui/admin/admin-merge.yaml ui/admin/admin.yaml docs/db.dbml; grep -n "attended_count" -r ui/admin docs/db.dbml | head

OUT

-rw-r--r--@ 1 val  staff  1578 Oct 13 16:40 docs/db.dbml

ui/admin:

total 64

drwxr-xr-x@ 8 val  staff    256 Oct 13 16:31 .

drwxr-xr-x@ 8 val  staff    256 Oct 13 16:31 ..

drwxr-xr-x@ 3 val  staff     96 Oct 13 16:31 __pycache__

-rw-r--r--@ 1 val  staff   4657 Oct 13 16:40 admin-merge.yaml

-rw-r--r--@ 1 val  staff   3731 Oct 13 16:31 admin.yaml

-rw-r--r--@ 1 val  staff  10241 Oct 13 16:31 admin_loader.py

-rw-r--r--@ 1 val  staff   2261 Oct 13 16:31 authentication_admin.yaml

-rw-r--r--@ 1 val  staff   3203 Oct 13 16:31 home.js

ui/admin/admin-merge.yaml:8

docs/db.dbml:3

ui/admin/admin.yaml:0

Bash

IN

python3 - <<'EOF'

p='docs/requirements/course_dropoff/requirements.md'

s=open(p).read()

s=s.replace("""   - `Course.enrolled_count = count(Attendance where status in ('attended', 'excused'))`.

""","""   - `Course.enrolled_count = count(Enrollment where course_id = Course.id)` — the number of distinct students enrolled in the course (corrected 2026-10-13 by `students_courses_attendance_sweep`; previously counted Attendance records, which grew every session).

""")

s=s.replace("""   - `Student.consecutive_absences = count(Attendance where status == 'absent')`.

""","""   - `Student.consecutive_absences` is a running streak of consecutive `absent` Attendance rows: it increments by 1 for each `absent` Attendance row recorded directly after an `absent` one, restarts at 1 after a non-absent row, and resets to 0 on any non-`absent` Attendance row (`attended` or `excused`). (Streak semantics written back 2026-10-13; the column name implies this, a plain count never resets.)

""")

s=s.replace("""   - If a student has a `consecutive_absences` value of 2 or more, a `course_dropoff` alert is automatically dispatched for advisor follow-up.

""","""   - If a student has a `consecutive_absences` value of 2 or more, a `course_dropoff` alert is automatically dispatched for advisor follow-up.

- The 'absent' rows this depends on are written by the Attendance Sweep (`docs/requirements/students_courses_attendance_sweep/requirements.md`); attendance rows are otherwise written only on check-in.

""")

open(p,'w').write(s)

p='logic/logic_discovery/course_dropoff.py'

s=open(p).read()

head,_=s.split('from logic_bank.logic_bank import Rule',1)

head=head.replace("""   - `Course.enrolled_count = count(Attendance where status in ('attended', 'excused'))`.

""","""   - `Course.enrolled_count = count(Enrollment where course_id = Course.id)` — the number of distinct students enrolled in the course (corrected 2026-10-13 by `students_courses_attendance_sweep`; previously counted Attendance records, which grew every session).

""").replace("""   - `Student.consecutive_absences = count(Attendance where status == 'absent')`.

""","""   - `Student.consecutive_absences` is a running streak of consecutive `absent` Attendance rows: it increments by 1 for each `absent` Attendance row recorded directly after an `absent` one, restarts at 1 after a non-absent row, and resets to 0 on any non-`absent` Attendance row (`attended` or `excused`). (Streak semantics written back 2026-10-13; the column name implies this, a plain count never resets.)

""").replace("""advisor follow-up.

""","""advisor follow-up.

- The 'absent' rows this depends on are written by the Attendance Sweep (`docs/requirements/students_courses_attendance_sweep/requirements.md`); attendance rows are otherwise written only on check-in.

""").replace("version: 1.1","version: 1.2")

body='''from logic_bank.logic_bank import Rule

from database import models

def _update_absence_streak_and_alert(row, old_row, logic_row):

    """Attendance event: recomputes Student.consecutive_absences as a reset-on-attendance

    streak (a plain Rule.count would only ever grow) and dispatches a course_dropoff Alert

    the moment the streak newly reaches the SysConfig-configured threshold. Scoped to

    newly-inserted Attendance rows only."""

    if not logic_row.is_inserted():

        return

    student = row.student

    previous_streak = student.consecutive_absences or 0

    is_absent = (row.status == 'absent')

    if is_absent:

        student.consecutive_absences = previous_streak + 1 if student.last_attendance_absent else 1

    else:

        student.consecutive_absences = 0

    student.last_attendance_absent = 1 if is_absent else 0

    # SysConfig is a singleton settings table, not a per-row parent - use .current(session)

    threshold = models.SysConfig.current(logic_row.session).consecutive_absence_threshold

    if previous_streak < threshold <= student.consecutive_absences:

        alert_logic_row = logic_row.new_logic_row(models.Alert)

        alert = alert_logic_row.row

        alert.student_id = student.id

        alert.alert_type = 'course_dropoff'

        alert.status = 'active'

        alert.message = (f"{student.first_name} {student.last_name} has "

                         f"{student.consecutive_absences} consecutive absences")

        alert_logic_row.insert(reason="course_dropoff alert dispatch")

def declare_logic():

    """Business logic rules for Course Attendance & Drop-Off use case."""

    # --- Clause 1: Enrollment Capacity ---

    Rule.count(derive=models.Course.enrolled_count, as_count_of=models.Enrollment)

    Rule.constraint(validate=models.Course,

                     as_condition=lambda row: row.enrolled_count <= row.max_capacity,

                     error_msg="Course {row.course_name} enrolled_count ({row.enrolled_count}) "

                               "exceeds max_capacity ({row.max_capacity})")

    # --- Clause 2: total_sessions_completed (consecutive_absences is the streak event below) ---

    Rule.count(derive=models.Student.total_sessions_completed, as_count_of=models.Attendance,

               where=lambda row: row.status == 'attended')

    # --- active_alert_count rollup (named in the original schema description, item 2) ---

    Rule.count(derive=models.Student.active_alert_count, as_count_of=models.Alert,

               where=lambda row: row.status == 'active')

    # --- Clauses 2 (consecutive_absences streak) + 3 (alert dispatch) ---

    Rule.early_row_event(on_class=models.Attendance, calling=_update_absence_streak_and_alert)

'''

open(p,'w').write(head+body)

EOF

mkdir -p docs/requirements/attendance_sweep && cp docs/requirements/students_courses_attendance_sweep/requirements.md docs/requirements/attendance_sweep/requirements.md

OUT

(Bash completed with no output)

4:41 PM

Status: the logic file and the course_dropoff requirements are updated. I'm now writing the sweep endpoint.

Bash

IN

cat > api/api_discovery/attendance_sweep.py <<'EOF'

import hmac

import logging

import os

from datetime import datetime

import safrs

from flask import request, jsonify

from database import models

app_logger = logging.getLogger("api_logic_server_app")

API_KEY_HEADER = "X-Api-Key"

API_KEY_ENV = "ATTENDANCE_SWEEP_API_KEY"

def _authorized() -> bool:

    """Service credential check (separate from user JWT / declare_security.py grants).

    Fails closed: if no key is configured in the environment, every call is refused."""

    expected = os.getenv(API_KEY_ENV, "")

    supplied = request.headers.get(API_KEY_HEADER, "")

    return bool(expected) and hmac.compare_digest(expected, supplied)

def _parse_when(value: str) -> datetime:

    return datetime.fromisoformat(value)

def _session_end(cs: models.ClassSchedule) -> datetime | None:

    """End of a ClassSchedule: end_time if it is a full ISO datetime, else session_date + end_time

    (time-only), else end of session_date."""

    if not cs.session_date:

        return None

    try:

        if cs.end_time:

            try:

                return datetime.fromisoformat(cs.end_time)

            except ValueError:

                return datetime.fromisoformat(f"{cs.session_date}T{cs.end_time}")

        return datetime.fromisoformat(f"{cs.session_date}T23:59:59")

    except ValueError:

        app_logger.warning(f"attendance_sweep: unparseable times on ClassSchedule {cs.id}")

        return None

def sweep_session(session, cs: models.ClassSchedule, now: datetime) -> int:

    """Insert Attendance(status='absent') for each Enrollment of cs's course with no

    Attendance row for (student, cs). A normal domain insert - LogicBank rules fire on commit."""

    present = {sid for (sid,) in session.query(models.Attendance.student_id)

               .filter(models.Attendance.class_schedule_id == cs.id)}

    enrolled = session.query(models.Enrollment).filter(models.Enrollment.course_id == cs.course_id) \

        .order_by(models.Enrollment.student_id).all()

    inserted = 0

    for enrollment in enrolled:

        if enrollment.student_id not in present:

            session.add(models.Attendance(student_id=enrollment.student_id,

                                          class_schedule_id=cs.id, status='absent'))

            inserted += 1

    cs.swept_at = now.isoformat()

    session.commit()

    return inserted

def add_service(app, api, project_dir, swagger_host: str, PORT: str, method_decorators=[]):

    @app.route('/api/attendance_sweep', methods=['POST'])

    def attendance_sweep():

        """

        Insert Attendance(status='absent') for every enrolled student with no Attendance row for

        an ended class session (the write path course_dropoff's streak/alert logic depends on).

        Called by an external scheduler. Requires header X-Api-Key matching env

        ATTENDANCE_SWEEP_API_KEY. Body (all optional):

            {"class_schedule_id": 47, "todays_date": "2026-09-08T11:00:00"}

        class_schedule_id null = every ended, not-yet-swept session; todays_date = test-only "now".

        """

        if not _authorized():

            return jsonify({"error": "invalid or missing service credential"}), 401

        body = request.get_json(silent=True) or {}

        class_schedule_id = body.get("class_schedule_id")

        try:

            now = _parse_when(body["todays_date"]) if body.get("todays_date") else datetime.now()

        except (TypeError, ValueError):

            return jsonify({"error": "todays_date must be an ISO date/datetime"}), 400

        session = safrs.DB.session

        try:

            if class_schedule_id is not None:

                cs = session.get(models.ClassSchedule, class_schedule_id)

                if cs is None:

                    return jsonify({"error": f"ClassSchedule {class_schedule_id} not found"}), 404

                candidates = [cs]

            else:

                candidates = [cs for cs in session.query(models.ClassSchedule)

                              .filter(models.ClassSchedule.swept_at.is_(None)).all()

                              if (end := _session_end(cs)) is not None and end <= now]

            # chronological order: the absence streak depends on insert order

            candidates.sort(key=lambda c: (_session_end(c) or datetime.min, c.id))

            results = [{"class_schedule_id": cs.id, "course_id": cs.course_id,

                        "absent_rows_inserted": sweep_session(session, cs, now)} for cs in candidates]

        except Exception as e:

            session.rollback()

            app_logger.exception("attendance_sweep failed")

            return jsonify({"error": "sweep failed", "details": str(e)}), 400

        app_logger.info(f"attendance_sweep: {results}")

        return jsonify({"as_of": now.isoformat(), "sessions_processed": results})

EOF

python3 - <<'EOF'

p='config/default.env'

s=open(p).read()

s=s.replace("SECURITY_ENABLED = false\n","SECURITY_ENABLED = false\n\n# Service credential for POST /api/attendance_sweep (header X-Api-Key). Unset = endpoint refuses all calls.\n# ATTENDANCE_SWEEP_API_KEY = <long random secret>\n",1)

open(p,'w').write(s)

EOF

grep -n "load_dotenv\|default.env" config/config.py api_logic_server_run.py | head

OUT

config/config.py:6:from dotenv import load_dotenv

config/config.py:49:load_dotenv(path.join(basedir, "default.env"))

Bash

IN

source ../../venv/bin/activate && (ATTENDANCE_SWEEP_API_KEY=testkey nohup python api_logic_server_run.py > /tmp/ignore.out 2>&1 &) ; sleep 8; tail -15 logs/als.log; curl -s localhost:5656/api/Course/ | head -c 300

OUT

Alert: These following are **Critical** to unlocking value for project: students_courses_1:

.. see logic.declare_logic.py       -- 

.. see security.declare_security.py -- ALERT:  *** Security Not Enabled ***

*

* Startup Instructions: Open your Browser at: http://localhost:5656   *

*

WARNING: This is a development server. Do not use it in a production deployment. Use a production WSGI server instead.

* Running on all addresses (0.0.0.0)
* Running on http://127.0.0.1:5656
* Running on http://10.0.0.154:5656

Press CTRL+C to quit

{"data":[{"attributes":{"course_name":"Intro to Statistics","enrolled_count":0,"instructor_name":"Dr. Patel","max_capacity":30},"id":"1","links":{"self":"/api/Course/1/"},"relationships":{"ClassScheduleList":{"data":[],"links":{"self":"/api/Course/1/ClassScheduleList"}},"EnrollmentList":{"data":[],"

Bash

IN

H='Content-Type: application/vnd.api+json'

for s in 3 4; do curl -s -X POST localhost:5656/api/Enrollment/ -H "$H" -d "{\"data\":{\"type\":\"Enrollment\",\"attributes\":{\"student_id\":$s,\"course_id\":3}}}" | head -c 120; echo; done

sqlite3 database/db.sqlite "select id,enrolled_count from courses"

SCR=/private/tmp/claude-502/-Users-val-dev-ApiLogicServer-ApiLogicServer-dev-build-and-test-genai-logic-samples-students-courses-1/078541fe-04bf-4204-b3e7-43565908558b/scratchpad

cp database/db.sqlite $SCR/db.seeded.sqlite

OUT

{"data":{"attributes":{"course_id":3,"student_id":3},"id":"1","links":{"self":"/api/Enrollment/1/"},"relationships":{"co

{"data":{"attributes":{"course_id":3,"student_id":4},"id":"2","links":{"self":"/api/Enrollment/2/"},"relationships":{"co

1|0

2|0

3|2

Bash

IN

H='Content-Type: application/vnd.api+json'; K='X-Api-Key: testkey'

for s in 1 2; do curl -s -o /dev/null -X POST localhost:5656/api/Enrollment/ -H "$H" -d "{\"data\":{\"type\":\"Enrollment\",\"attributes\":{\"student_id\":$s,\"course_id\":1}}}"; done

curl -s -o /dev/null -X POST localhost:5656/api/Attendance/ -H "$H" -d '{"data":{"type":"Attendance","attributes":{"student_id":2,"class_schedule_id":1,"status":"attended"}}}'

echo "--no key"; curl -s -X POST localhost:5656/api/attendance_sweep -H 'Content-Type: application/json' -d '{}' -w ' %{http_code}\n'

echo "--bad key"; curl -s -X POST localhost:5656/api/attendance_sweep -H 'X-Api-Key: nope' -d '{}' -w ' %{http_code}\n'

echo "--sweep as of 09-08 11:00"; curl -s -X POST localhost:5656/api/attendance_sweep -H "$K" -H 'Content-Type: application/json' -d '{"todays_date":"2026-09-08T11:00:00"}'

echo "--repeat"; curl -s -X POST localhost:5656/api/attendance_sweep -H "$K" -H 'Content-Type: application/json' -d '{"todays_date":"2026-09-08T11:00:00"}'

echo "--explicit id again"; curl -s -X POST localhost:5656/api/attendance_sweep -H "$K" -H 'Content-Type: application/json' -d '{"class_schedule_id":2}'

sqlite3 database/db.sqlite "select id,first_name,consecutive_absences,last_attendance_absent,total_sessions_completed,active_alert_count from students; select * from alerts; select student_id,class_schedule_id,status from attendances order by id; select id,swept_at from class_schedules"

OUT

--no key

{"error":"invalid or missing service credential"}

 401

--bad key

{"error":"invalid or missing service credential"}

 401

--sweep as of 09-08 11:00

{"as_of":"2026-09-08T11:00:00","sessions_processed":[{"absent_rows_inserted":1,"class_schedule_id":1,"course_id":1},{"absent_rows_inserted":0,"class_schedule_id":4,"course_id":3},{"absent_rows_inserted":2,"class_schedule_id":2,"course_id":1},{"absent_rows_inserted":0,"class_schedule_id":5,"course_id":3}]}

--repeat

{"as_of":"2026-09-08T11:00:00","sessions_processed":[]}

--explicit id again

{"as_of":"2026-10-13T16:41:51.592591","sessions_processed":[{"absent_rows_inserted":0,"class_schedule_id":2,"course_id":1}]}

1|Priya|2|1|0|1

2|Marcus|1|1|1|0

3|Alice|0|0|2|0

4|Carol|0|0|1|0

1|1|course_dropoff|active|Priya Nair has 2 consecutive absences|2026-10-13 00:00:00.000000

3|4|attended

3|5|attended

4|4|excused

4|5|attended

2|1|attended

1|1|absent

1|2|absent

2|2|absent

1|2026-09-08T11:00:00

2|2026-10-13T16:41:51.592591

3|

4|2026-09-08T11:00:00

5|2026-09-08T11:00:00

Bash

IN

grep -ci "error\|Traceback" logs/als.log; pkill -f "python api_logic_server_run.py"; sleep 2; lsof -i :5656 | head -2

SCR=/private/tmp/claude-502/-Users-val-dev-ApiLogicServer-ApiLogicServer-dev-build-and-test-genai-logic-samples-students-courses-1/078541fe-04bf-4204-b3e7-43565908558b/scratchpad

cp $SCR/db.seeded.sqlite database/db.sqlite; sqlite3 database/db.sqlite "select count(*) from enrollment; select count(*) from attendances; select count(*) from alerts; select id,enrolled_count from courses"; grep -n "ERROR\|Traceback" logs/als.log | head -5

OUT

0

COMMAND   PID USER   FD   TYPE             DEVICE SIZE/OFF NODE NAME

Python  68053  val    7u  IPv4 0x8f55486517b7090a      0t0  TCP *:5656 (LISTEN)

2

4

0

1|0

2|0

3|2

Bash

IN

kill 68053; sleep 2; lsof -i :5656 | head -2; ps aux | grep api_logic_server_run | grep -v grep | head

OUT

(Bash completed with no output)

4:42 PM

Status: the sweep endpoint passed my tests, and I restored the database to the seeded state. The server is stopped. I'm writing the ad-libs reports now.

Bash

IN

sqlite3 database/db.sqlite "pragma integrity_check" && cat > docs/requirements/students_courses_attendance_sweep/ad-libs.md <<'EOF'

## Ad-Libs Report

**2 items need your review. 6 FYIs — standard patterns, no action needed.**

---

## Walkthrough

1. **Basic data model** — existing 6 tables plus new `enrollment` (student_id, course_id, UNIQUE pair), per the spec's DDL.
2. **Derived/predicted schema additions** — `students.last_attendance_absent` (streak carried state for the re-enabled accumulator), `class_schedules.swept_at` (the spec's "not yet swept"), dropped the now-unused `class_schedules.attended_count` bridge. No constants → SysConfig; no Request Pattern; no Allocate.
3. **Create db** — one DDL batch + `rebuild-from-database` (7 tables). The rebuild's final step failed on a missing `.vscode/settings.json` (cosmetic); `models.py`, `docs/db.dbml` and `ui/admin/admin-merge.yaml` were all regenerated.
4. **Run impl-req** — `course_dropoff.py`: Rule.count (enrolled_count from Enrollment), Rule.constraint, Rule.count x2, plus the re-enabled `early_row_event` streak/alert. New `api/api_discovery/attendance_sweep.py` (plain endpoint, no rules).
5. **Test data / testing** — seeded Enrollment for Alice and Carol in course 3 via the API. Sweep tested against the live server (auth, sweep, idempotency, streak, alert), then the database was restored to the seeded state.

<details markdown>
<summary>Full diagnostic detail (DDL change list, rule plan, rejected alternatives, replay log)</summary>

### 🟢 Diagnostic Appendix

#### Pre-Coding Analysis

**Phase 1 — Schema Impact Assessment**

Files read: `students_courses_attendance_sweep/requirements.md` + `README.md`, `course_dropoff/requirements.md` + `ad-libs.md`, `logic/logic_discovery/course_dropoff.py`, `database/models.py`, live schema.

| Step                   | Signal                                                                               |
| ---------------------- | ------------------------------------------------------------------------------------ |
| Enrollment table       | Rule.count needed on Course (replaces 2-level Attendance bridge)                     |
| Sweep endpoint         | Plain endpoint; needs a "swept" marker; no rules                                     |
| Re-enable streak/alert | Needs `students.last_attendance_absent` (per the commented-out reference's own note) |

DDL change list:

| Table           | Change                                              | Reason                                                                                     |
| --------------- | --------------------------------------------------- | ------------------------------------------------------------------------------------------ |
| enrollment      | CREATE TABLE (UNIQUE student_id, course_id)         | Spec — Rule.count source for Course.enrolled_count; sweep's "who was expected"             |
| students        | ADD COLUMN last_attendance_absent INTEGER DEFAULT 0 | Streak accumulator state (written by the Attendance early_row_event)                       |
| class_schedules | ADD COLUMN swept_at TEXT                            | Spec step 1 "has not already been swept" (written by the sweep)                            |
| class_schedules | DROP COLUMN attended_count                          | Bridge rollup obsolete once enrolled_count counts Enrollment                               |
| courses         | UPDATE enrolled_count = 0                           | Re-baseline: delta adjustment would otherwise carry the old attendance-based value forward |

**Phase 2 — CE / Pattern Assessment**

Files read: `logic_bank_api.md` (Running Streaks, Absence of an Event, SysConfig), `.github/copilot-instructions.md`, `implement_requirements.md`.

| Step       | Rule Plan                                                                                            |
| ---------- | ---------------------------------------------------------------------------------------------------- |
| Clause 1   | `Rule.count(Course.enrolled_count, Enrollment)` + existing capacity constraint                       |
| Clause 2/3 | reset-on-attendance streak via `Rule.early_row_event` on Attendance (fold, not Rule.count); Alert via `new_logic_row` |
| Sweep      | `POST /api/attendance_sweep`, ordinary application code, commit fires the rules                      |

Anti-patterns confirmed clear:

- [x] No parent flag where Rule.count on child table is correct
- [x] No `as_expression=lambda row: my_func(row)`
- [x] No `session.query()` inside a formula (the sweep's queries are in endpoint code, not rules)
- [x] Threshold read via `SysConfig.current()`, no fallback, no FK

**Implementation Plan:** 1) DDL + rebuild. 2) Update course_dropoff requirements.md, then course_dropoff.py. 3) Write endpoint. 4) Seed enrollments, run server, test. 5) Reports.

---

#### Execution Metrics

| Metric                  | Value                                                                                               |
| ----------------------- | --------------------------------------------------------------------------------------------------- |
| Strategy Used           | Count over Enrollment; streak accumulator re-enabled; sweep as external-trigger endpoint            |
| CE Files Loaded         | `implement_requirements.md`, `logic_bank_api.md`, `.github/copilot-instructions.md` (via CLAUDE.md) |
| Schema Read First       | Yes                                                                                                 |
| Sample Data Read        | N/A (not EAI)                                                                                       |
| Subagent Used           | No — single pass                                                                                    |
| Self-Verification       | Yes — server started, endpoint tested with curl, DB inspected                                       |
| Lightweight Checks Used | Yes — curl + sqlite3 + `logs/als.log`                                                               |
| Gate Test Run Count     | 1                                                                                                   |
| Gate Test Purpose       | Final verification                                                                                  |
| Error Correction Loops  | None — implementation passed on first run                                                           |
| Long-Run Diagnostics    | None                                                                                                |

**Verification results:** no/bad key → 401. Sweep as of 2026-09-08T11:00 processed sessions in chronological order (1, 4, 2, 5), inserting 1 + 0 + 2 + 0 absent rows (Marcus had attended session 1). Priya reached streak 2 → exactly one `course_dropoff` Alert, `active_alert_count` 1; Marcus streak 1, no alert. Repeat sweep → no sessions, no new rows; explicit `class_schedule_id` re-sweep → 0 inserted.

**Closing DDL check:** `last_attendance_absent` assigned in `_update_absence_streak_and_alert`; `swept_at` assigned in `sweep_session`; every column read by a rule exists in `models.py`.

---

### 🔴 Review Required

| Location                                            | Issue                                                                                                | Action                                                                                               |
| --------------------------------------------------- | ---------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------- |
| `api/api_discovery/attendance_sweep.py:_authorized` | Service credential is a shared API key compared against env `ATTENDANCE_SWEEP_API_KEY` (header `X-Api-Key`); the spec said only "an API key or service-to-service token". Fails closed when unset. With `SECURITY_ENABLED=true` the route may also be subject to the global JWT check — not tested (security is off in this project). | Set a real secret in the deployment environment; confirm whether it should be a different mechanism (e.g. signed token); if you enable security, verify the external scheduler can reach this route. |
| `docs/requirements/course_dropoff/requirements.md`  | I wrote the streak semantics (increment / restart at 1 / reset to 0) back into Clause 2 in prose, since `consecutive_absences` implied them but the old text said `count(...)`. Also seeded Enrollment for only Alice and Carol in course 3, inferred from their existing Attendance rows; Priya and Marcus have no enrollments. | Confirm the streak wording matches intent, and add real enrollments (Priya, Marcus, and any others). |

---

### 🟡 FYI

- `database/db.sqlite` — `courses.enrolled_count` was reset to 0 before seeding Enrollment, because delta adjustment would have carried the old attendance-based value (4 for course 3) forward.
- `class_schedules.attended_count` dropped (SQLite DROP COLUMN) since no rule derives it any more; backup of the pre-change db kept in the session scratchpad only.
- `api/api_discovery/attendance_sweep.py:sweep_session` — one commit per session, sessions processed in chronological order, so the streak sees absences in order; `swept_at` is set even when 0 rows were inserted. An explicit `class_schedule_id` ignores `swept_at` and re-sweeps (still idempotent), which refreshes `swept_at`.
- `api/api_discovery/attendance_sweep.py:_session_end` — end time is `end_time` if a full ISO datetime, else `session_date` + `end_time`; naive local time, no time zones. A student enrolled after a session was swept is not retroactively marked absent for it.
- `logic/logic_discovery/course_dropoff.py:_update_absence_streak_and_alert` — streak scoped to newly inserted Attendance rows only; edits or deletes of Attendance do not recompute it. No `or 2` threshold fallback (the reference had one); `SysConfig.current()` raises if the row is missing.
- `docs/requirements/attendance_sweep/requirements.md` — verbatim copy of the full sweep requirements (the endpoint has no logic file); `ui/admin/admin-merge.yaml` was generated but `admin.yaml` was NOT replaced — awaiting your choice.

</details>
EOF
python3 - <<'EOF'
p='docs/requirements/course_dropoff/ad-libs.md'
s=open(p).read()
note="""> **UPDATE 2026-10-13 — both 🔴 findings below were resolved by `students_courses_attendance_sweep`** (see `../students_courses_attendance_sweep/ad-libs.md`): strategy (a) was chosen — an external-trigger sweep endpoint inserts the missing `absent` rows — and the streak/alert logic is now enabled in `course_dropoff.py`. `Course.enrolled_count` now counts `Enrollment` rows (new table), replacing the Attendance-based 2-level bridge (`class_schedules.attended_count`, dropped). The text below is the historical record of the original pass.

"""

open(p,'w').write(note+s)

p='docs/requirements/project_creation_report.md'

s=open(p).read().rstrip('\n')

s+="\n- [students_courses_attendance_sweep](students_courses_attendance_sweep/ad-libs.md) — Attendance Sweep endpoint + Enrollment table; resolves course_dropoff's blocked streak/alert clauses and corrects enrolled_count, 2026-10-13. 2 items need review, 6 FYIs.\n"

open(p,'w').write(s)

EOF

ls docs/requirements/*/ ; ls logic/logic_discovery/*.py

OUT

ok

docs/requirements/attendance_sweep/:

requirements.md

docs/requirements/course_dropoff/:

ad-libs.md

requirements.md

docs/requirements/students_courses/:

course_dropoff

db.sqlite

project_creation_prompt.md

docs/requirements/students_courses_attendance_sweep/:

README.md

ad-libs.md

requirements.md

logic/logic_discovery/auto_discovery.py

logic/logic_discovery/course_dropoff.py

logic/logic_discovery/use_case.py

4:42 PM

students_courses_attendance_sweep is implemented and I tested it against a live server. The server is stopped again and the database is back to its seeded state.

Schema (enrollment was in your spec; the other changes are mine, and models.py and the admin merge file are regenerated):

enrollment: new table, with a unique (student, course) pair.

students.last_attendance_absent: carries the streak state.

class_schedules.swept_at: records that a session was swept.

class_schedules.attended_count: dropped. Nothing derives it any more.

courses.enrolled_count: reset to 0 before seeding enrollments, so the old attendance-based value wasn't carried forward.

course_dropoff (Clause 1 corrected, streak and alert turned on):

Enrollment count: Course.enrolled_count now counts Enrollment rows. The capacity constraint is unchanged.

Streak and alert: the streak and course_dropoff alert logic is enabled. It uses SysConfig.current() with no fallback.

Files: course_dropoff.py and its requirements.md are updated. I also wrote the streak meaning (increment, restart at 1, reset to 0) into Clause 2's prose.

Sweep endpoint:

Endpoint and per-use-case file: POST /api/attendance_sweep is in attendance_sweep.py, with docs/requirements/attendance_sweep/requirements.md as the per-use-case copy.

Credential: it requires an X-Api-Key header matching the ATTENDANCE_SWEEP_API_KEY env var, and refuses every call if that isn't set. todays_date is behind the same key.

Processing order: it processes sessions oldest first, one commit per session.

Test results:

Auth: a missing or wrong key returns 401.

Sweep: a sweep as of 2026-09-08 11:00 inserted the right absent rows. Priya reached a streak of 2 and got exactly one alert. Marcus, who had attended session 1, stopped at a streak of 1.

Repeat: a repeat sweep inserted nothing.

Needs your attention:

Enrollments: I seeded only Alice and Carol in course 3, inferred from their existing attendance. Priya and Marcus have none.

API key: you need to set a real ATTENDANCE_SWEEP_API_KEY. I didn't test the endpoint with SECURITY_ENABLED=true.

Admin UI: ui/admin/admin-merge.yaml reflects the new schema. admin.yaml is unchanged. Want me to back it up and replace it, or will you merge by hand?

Rebuild error: rebuild-from-database failed at the end on a missing .vscode/settings.json. The models, db.dbml and merge file were all written before that.

The reports are in ad-libs.md (2 to review, 6 FYIs). I added a resolution note to course_dropoff's ad-libs.md and a line to project_creation_report.md.