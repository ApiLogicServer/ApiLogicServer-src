# Use Case: Exertion & Attendance Drop-Off Requirements

## Narrative & Scope
Patients log rehab sessions with Borg Rate of Perceived Exertion (RPE 6-20) and reported symptoms. Attendance at scheduled classes is monitored for adherence.

## Rules & Constraints
1. **High Exertion Classification**:
   - `ExerciseSession.is_high_exertion` evaluates to True when `rpe >= 15` OR (`rpe >= 13` AND `has_symptoms == True`).
2. **Absence Tracking**:
   - `Patient.consecutive_absences = count(Attendance where status == 'absent')`.
   - `Patient.total_sessions_completed = count(ExerciseSession)`.
3. **Care Team Drop-Off Alert**:
   - If a patient with prior high-exertion sessions has a `consecutive_absences` value of 2 or more, an `exertion_dropoff` alert is automatically dispatched for nurse follow-up.
