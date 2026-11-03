"""
Use Case: Course Attendance & Drop-Off Requirements

## Narrative & Scope
Students enroll in courses with scheduled class sessions. Attendance at each scheduled session is tracked for adherence.

## Rules & Constraints
1. **Enrollment Capacity**:
   - `Course.enrolled_count = count(Attendance where status in ('attended', 'excused'))`.
   - `Course.enrolled_count <= Course.max_capacity`.
2. **Absence Tracking**:
   - `Student.consecutive_absences = count(Attendance where status == 'absent')`.
   - `Student.total_sessions_completed = count(Attendance where status == 'attended')`.
3. **Course Drop-Off Alert**:
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
