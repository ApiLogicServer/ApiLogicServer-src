# Use Case: Course Attendance & Drop-Off Requirements

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

(Verbatim excerpt of the requirement that drove `logic/logic_discovery/course_dropoff.py` -
copied from `docs/requirements/students_courses/course_dropoff/requirements.md`, the recreate
sample's bundled copy.)
