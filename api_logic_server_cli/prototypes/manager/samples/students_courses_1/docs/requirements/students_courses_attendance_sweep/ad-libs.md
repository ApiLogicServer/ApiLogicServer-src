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

| Step | Signal |
|---|---|
| Enrollment table | Rule.count needed on Course (replaces 2-level Attendance bridge) |
| Sweep endpoint | Plain endpoint; needs a "swept" marker; no rules |
| Re-enable streak/alert | Needs `students.last_attendance_absent` (per the commented-out reference's own note) |

DDL change list:

| Table | Change | Reason |
|---|---|---|
| enrollment | CREATE TABLE (UNIQUE student_id, course_id) | Spec — Rule.count source for Course.enrolled_count; sweep's "who was expected" |
| students | ADD COLUMN last_attendance_absent INTEGER DEFAULT 0 | Streak accumulator state (written by the Attendance early_row_event) |
| class_schedules | ADD COLUMN swept_at TEXT | Spec step 1 "has not already been swept" (written by the sweep) |
| class_schedules | DROP COLUMN attended_count | Bridge rollup obsolete once enrolled_count counts Enrollment |
| courses | UPDATE enrolled_count = 0 | Re-baseline: delta adjustment would otherwise carry the old attendance-based value forward |

**Phase 2 — CE / Pattern Assessment**
Files read: `logic_bank_api.md` (Running Streaks, Absence of an Event, SysConfig), `.github/copilot-instructions.md`, `implement_requirements.md`.

| Step | Rule Plan |
|---|---|
| Clause 1 | `Rule.count(Course.enrolled_count, Enrollment)` + existing capacity constraint |
| Clause 2/3 | reset-on-attendance streak via `Rule.early_row_event` on Attendance (fold, not Rule.count); Alert via `new_logic_row` |
| Sweep | `POST /api/attendance_sweep`, ordinary application code, commit fires the rules |

Anti-patterns confirmed clear:
- [x] No parent flag where Rule.count on child table is correct
- [x] No `as_expression=lambda row: my_func(row)`
- [x] No `session.query()` inside a formula (the sweep's queries are in endpoint code, not rules)
- [x] Threshold read via `SysConfig.current()`, no fallback, no FK

**Implementation Plan:** 1) DDL + rebuild. 2) Update course_dropoff requirements.md, then course_dropoff.py. 3) Write endpoint. 4) Seed enrollments, run server, test. 5) Reports.

---

#### Execution Metrics

| Metric | Value |
|---|---|
| Strategy Used | Count over Enrollment; streak accumulator re-enabled; sweep as external-trigger endpoint |
| CE Files Loaded | `implement_requirements.md`, `logic_bank_api.md`, `.github/copilot-instructions.md` (via CLAUDE.md) |
| Schema Read First | Yes |
| Sample Data Read | N/A (not EAI) |
| Subagent Used | No — single pass |
| Self-Verification | Yes — server started, endpoint tested with curl, DB inspected |
| Lightweight Checks Used | Yes — curl + sqlite3 + `logs/als.log` |
| Gate Test Run Count | 1 |
| Gate Test Purpose | Final verification |
| Error Correction Loops | None — implementation passed on first run |
| Long-Run Diagnostics | None |

**Verification results:** no/bad key → 401. Sweep as of 2026-09-08T11:00 processed sessions in chronological order (1, 4, 2, 5), inserting 1 + 0 + 2 + 0 absent rows (Marcus had attended session 1). Priya reached streak 2 → exactly one `course_dropoff` Alert, `active_alert_count` 1; Marcus streak 1, no alert. Repeat sweep → no sessions, no new rows; explicit `class_schedule_id` re-sweep → 0 inserted.

**Closing DDL check:** `last_attendance_absent` assigned in `_update_absence_streak_and_alert`; `swept_at` assigned in `sweep_session`; every column read by a rule exists in `models.py`.

---

### 🔴 Review Required
| Location | Issue | Action |
|---|---|---|
| `api/api_discovery/attendance_sweep.py:_authorized` | Service credential is a shared API key compared against env `ATTENDANCE_SWEEP_API_KEY` (header `X-Api-Key`); the spec said only "an API key or service-to-service token". Fails closed when unset. With `SECURITY_ENABLED=true` the route may also be subject to the global JWT check — not tested (security is off in this project). | Set a real secret in the deployment environment; confirm whether it should be a different mechanism (e.g. signed token); if you enable security, verify the external scheduler can reach this route. |
| `docs/requirements/course_dropoff/requirements.md` | I wrote the streak semantics (increment / restart at 1 / reset to 0) back into Clause 2 in prose, since `consecutive_absences` implied them but the old text said `count(...)`. Also seeded Enrollment for only Alice and Carol in course 3, inferred from their existing Attendance rows; Priya and Marcus have no enrollments. | Confirm the streak wording matches intent, and add real enrollments (Priya, Marcus, and any others). |

---

### 🟡 FYI
- `database/db.sqlite` — `courses.enrolled_count` was reset to 0 before seeding Enrollment, because delta adjustment would have carried the old attendance-based value (4 for course 3) forward.
- `class_schedules.attended_count` dropped (SQLite DROP COLUMN) since no rule derives it any more; backup of the pre-change db kept in the session scratchpad only.
- `api/api_discovery/attendance_sweep.py:sweep_session` — one commit per session, sessions processed in chronological order, so the streak sees absences in order; `swept_at` is set even when 0 rows were inserted. An explicit `class_schedule_id` ignores `swept_at` and re-sweeps (still idempotent), which refreshes `swept_at`.
- `api/api_discovery/attendance_sweep.py:_session_end` — end time is `end_time` if a full ISO datetime, else `session_date` + `end_time`; naive local time, no time zones. A student enrolled after a session was swept is not retroactively marked absent for it.
- `logic/logic_discovery/course_dropoff.py:_update_absence_streak_and_alert` — streak scoped to newly inserted Attendance rows only; edits or deletes of Attendance do not recompute it. No `or 2` threshold fallback (the reference had one); `SysConfig.current()` raises if the row is missing.
- `docs/requirements/attendance_sweep/requirements.md` — verbatim copy of the full sweep requirements (the endpoint has no logic file); `ui/admin/admin-merge.yaml` was generated but `admin.yaml` was NOT replaced — awaiting your choice.

</details>
