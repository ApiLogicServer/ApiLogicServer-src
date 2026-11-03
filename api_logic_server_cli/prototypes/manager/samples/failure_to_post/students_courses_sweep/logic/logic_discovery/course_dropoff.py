"""
Use Case: Course Attendance & Drop-Off Requirements

## Narrative & Scope
Students enroll in courses with scheduled class sessions. Attendance at each scheduled session is tracked for adherence.

## Rules & Constraints
1. **Enrollment Capacity**:
   - `Course.enrolled_count = count(Enrollment where course_id = Course.id)` — the number of distinct students enrolled in the course (corrected 2026-10-13 by `students_courses_attendance_sweep`; previously counted Attendance records, which grew every session).
   - `Course.enrolled_count <= Course.max_capacity`.
2. **Absence Tracking**:
   - `Student.consecutive_absences` is a running streak of consecutive `absent` Attendance rows: it increments by 1 for each `absent` Attendance row recorded directly after an `absent` one, restarts at 1 after a non-absent row, and resets to 0 on any non-`absent` Attendance row (`attended` or `excused`). (Streak semantics written back 2026-10-13; the column name implies this, a plain count never resets.)
   - `Student.total_sessions_completed = count(Attendance where status == 'attended')`.
3. **Course Drop-Off Alert**:
   - If a student has a `consecutive_absences` value of 2 or more, a `course_dropoff` alert is automatically dispatched for advisor follow-up.
   - The 'absent' rows this depends on are written by the Attendance Sweep (`docs/requirements/students_courses_attendance_sweep/requirements.md`); attendance rows are otherwise written only on check-in.

version: 1.2
created: 2026-09-27T00:00:00
created_by: claude-sonnet-5 (valjhuber@gmail.com)
"""

from logic_bank.logic_bank import Rule
from logic_bank.exec_row_logic.logic_row import LogicRow
from database import models


def _update_absence_streak_and_alert(row: models.Attendance, old_row: models.Attendance, logic_row: LogicRow):
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
