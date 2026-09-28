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

| Step | Signal |
|---|---|
| Clause 1 — Enrollment Capacity | Rule.count/Rule.sum needed, but `Attendance` is a grandchild of `Course` (via `ClassSchedule`) — needs a 2-level bridge column |
| Clause 2 — Absence Tracking | `total_sessions_completed`: plain Rule.count, safe. `consecutive_absences`: name implies a reset-on-attendance streak AND depends on whether 'absent' Attendance rows are ever actually written in production — see 🔴 below |
| Clause 3 — Course Drop-Off Alert | Depends on the same 'absent'-row write-path question as clause 2 — blocked together |
| (Prompt item 1) SysConfig threshold | Runtime-configurable constant, but `sys_config` is a singleton settings table (one row), not a per-row lookup — `SysConfig.current(session)` (already provided in `database/customize_models.py`), not an FK |

DDL change list *(one row per change — covers ALL steps, run once before any coding)*:

| Table | Change | Reason |
|---|---|---|
| `class_schedules` | ADD COLUMN `attended_count` INTEGER DEFAULT 0 | Clause 1 — bridge rollup, Course is 2 levels above Attendance |

*No other DDL — no FK to sys_config (see 🟡 FYI), and no schema added for the blocked clause 2/3 streak (deferred until the write-path question is resolved — adding `students.last_attendance_absent` now, for a rule that won't fire in production, would be schema clutter for an unconfirmed design).*

**Phase 2 — CE / Pattern Assessment**
Files read: `logic_bank_api.md` (Running Streaks, Absence of an Event, SysConfig FK+copy/formula tradeoff), `.github/copilot-instructions.md`'s System Creation Services section (SysConfig singleton vs. lookup-entity FK test)

| Step | Rule Plan |
|---|---|
| Clause 1 | `Rule.count(ClassSchedule.attended_count)` + `Rule.sum(Course.enrolled_count)` + `Rule.constraint(enrolled_count <= max_capacity)` |
| Clause 2 (total_sessions_completed) | `Rule.count(Student.total_sessions_completed)` (plain, safe) |
| Clause 2 (consecutive_absences) + Clause 3 | **BLOCKED** — see 🔴 Review Required |

Anti-patterns confirmed clear:
- [x] No parent flag where Rule.count on child table is correct
- [x] No `as_expression=lambda row: my_func(row)` anywhere
- [x] No `session.query()` inside formula or row_event
- [x] `sys_config` correctly treated as a singleton settings table, not given a spurious FK relationship from `students`

**Implementation Plan** *(ordered steps written before any file was changed)*:

| Step | What was planned |
|---|---|
| 1 | Run DDL (1 ALTER TABLE statement) + `rebuild-from-database` |
| 2 | Write `logic/logic_discovery/course_dropoff.py` — enrolled_count bridge, total_sessions_completed, active_alert_count; comment out + FIXME the blocked streak/alert clause |
| 3 | Verify via a standalone capacity-constraint rejection test |
| 4 | Start server, confirm clean startup |
| 5 | Write this ad-libs report with the blocking finding, before seeding any 'absent' test data |

---

#### Execution Metrics

| Metric | Value |
|---|---|
| Strategy Used | 2-level Rule.count/sum bridge for enrolled_count; plain Rule.count for total_sessions_completed and active_alert_count; consecutive_absences streak + alert dispatch deliberately NOT implemented pending a write-path decision |
| CE Files Loaded | `.github/copilot-instructions.md` (Executable Requirements + full project CE, via CLAUDE.md; includes this project's own prior build cited back as a governance case — see below), `docs/training/logic_bank_api.md` (full, via CLAUDE.md) |
| Schema Read First | Yes — `database/models.py` read before any logic file written |
| Sample Data Read | N/A — no `message_formats/*`, not an EAI use case |
| Subagent Used | No — single pass |
| Self-Verification | Yes — a standalone script confirming the capacity constraint actually rejects an over-capacity insert |
| Lightweight Checks Used | Yes — sqlite3 schema checks + rule-fire log inspection |
| Gate Test Run Count | 1 (standalone constraint test) |
| Gate Test Purpose | Final verification |
| Error Correction Loops | 0 this pass — see note below |
| Long-Run Diagnostics | None |

**Note on this pass vs. the prior build:** an earlier build of this exact use case (different project name, `student_courses` — see the `students_courses_1` directory) implemented the streak accumulator and alert dispatch, and hit/fixed 4 real errors doing so (LB tokenizer gotcha, a self-inflicted repeat of it, `session.add()` bypassing LogicBank's rule chain, an optimistic-locking conflict during a pre-existing-row backfill). That build's own ad-libs.md correctly *identified* the "is 'absent' actually written?" ambiguity but classified it as 🟡 FYI and shipped the feature anyway — this project's own `.github/copilot-instructions.md` has since been updated (citing "student_courses, Sep 2026") to say that classification was wrong: this class of ambiguity must be 🔴 and blocking, not a footnoted assumption. Same source, same finding, corrected classification and behavior this pass. The validated accumulator/dispatch code from that build is preserved as a commented-out reference in `course_dropoff.py` rather than re-litigated from scratch, since its own correctness was already live-verified — what changed is not implementing it *now*, not doubt about whether it works.

---

### 🔴 Review Required
| Location | Issue | Action |
|---|---|---|
| `logic/logic_discovery/course_dropoff.py` (FIXME comment, streak/alert section) | **Blocking — Absence of an Event.** Clause 2's `consecutive_absences` and Clause 3's alert dispatch both depend on an Attendance row with `status='absent'` actually being written when a student misses a session. `requirements.md` lists `'absent'` as one of three explicit per-session status values, which is suggestive of explicit roll-call (an instructor records one row per student per session, including misses) — but does NOT explicitly state this; a presence-only entry model (a row is created only when a student checks in, so a miss produces no row at all) is an equally plausible reading that the requirement text does not rule out. Per this project's own CE (Absence of an Event / STEP 8), this ambiguity is a BLOCKING finding, not a flag-and-continue one — implementing the reactive logic without resolving it would produce a feature that looks tested (hand-seeded rows exercise the streak/alert code correctly) but is structurally blind to whether it will ever fire in production. | Confirm which write path applies: **(a)** explicit roll-call — an instructor/system calls `POST /api/Attendance/` once per student per scheduled session, always, recording attended/excused/absent explicitly (if so, the existing generic JSON:API endpoint already IS the write path — no new mechanism needed, just confirmation); **(b)** presence-only entry — a row is written only when a student checks in, and a miss is inferred from a scheduled session having fewer Attendance rows than enrolled students (would need a companion process — a scheduled sweep or an event tied to `ClassSchedule.end_time` elapsing — that diffs expected vs. actual and inserts the missing `'absent'` rows; nothing does this today); **(c)** some other mechanism specific to how this system will actually be operated. Once confirmed, uncomment the reference implementation in `course_dropoff.py` (already written and its logic previously live-verified — correct streak reset/rebuild behavior and single alert dispatch on threshold crossing) and, if (b), also build the missing companion write path first. |
| `logic/logic_discovery/course_dropoff.py:33-40` | `Course.enrolled_count` is implemented literally per Clause 1's own formula text: a 2-level sum of Attendance rows (attended/excused) across ALL of a course's class_schedules. This counts attendance *records*, not distinct enrolled *students* — a student attending N sessions adds N to enrolled_count, not 1. As written, enrolled_count will grow every session and can exceed `max_capacity` even with a small, genuinely-fixed roster, which conflicts with "capacity" as commonly understood. There is no separate Enrollment entity in the given schema to model distinct enrollment directly. | Confirm whether `enrolled_count`/`max_capacity` should instead track distinct students (would need a different design — e.g. an early_row_event that increments only on a student's first qualifying Attendance for that course) or whether the literal per-attendance-record definition, as given, is actually intended. |

---

### 🟡 FYI
- `logic/logic_discovery/course_dropoff.py:22-38` — 2-level `Rule.count`→`Rule.sum` chain used to bridge `Course.enrolled_count` since `Attendance` is a grandchild of `Course` via `ClassSchedule` — standard LogicBank chaining technique.
- `database/models.py` (no FK added) — the runtime-configurable alert threshold (`sys_config.consecutive_absence_threshold`) is read via `models.SysConfig.current(logic_row.session)` (already defined in `database/customize_models.py`), NOT an FK + `Rule.copy`/`Rule.formula` from `students`. `sys_config` is a singleton settings table (one row, no real cardinality) — a `students.sys_config_id` FK would model no actual relationship a schema reader could explain, even though adding it is easy and the resulting rule works. See this project's own `.github/copilot-instructions.md` System Creation Services section, which cites this exact prior mistake.
- `logic/logic_discovery/course_dropoff.py` (commented-out reference implementation) — the reset-on-attendance streak accumulator (early_row_event carrying a `last_attendance_absent` flag) is preserved from a prior, fully-tested build of this same use case, per `logic_bank_api.md`'s "Running Streaks" guidance (`consecutive_absences` needs reset behavior a plain `Rule.count` can't express) — kept commented out only because of the blocking write-path question above, not because the design itself is unverified.
- This ad-libs deliberately has NO seeded 'absent' test data yet — seeding it would implicitly pick an answer to the blocking question above (that hand-inserting rows is an adequate proxy for the real write path), which is exactly the appearance-of-completeness this project's CE now warns against.

</details>

*(end template)*
