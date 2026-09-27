# Use Case: Rehab Class Scheduling Requirements

## Narrative & Scope
Instructors and cardiac rehab coordinators manage rehab classes, schedule slots, and patient enrollments.

## Rules & Constraints
1. **Time Ordering**:
   - `ClassSchedule.start_time < ClassSchedule.end_time`.
2. **Capacity Enforcement**:
   - `ClassSchedule.enrolled_count = count(Attendance where status in ['attended', 'excused'])`.
   - `ClassSchedule.enrolled_count <= ClassSchedule.max_capacity`.
