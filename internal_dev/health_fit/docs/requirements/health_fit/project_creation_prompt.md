# Project Creation Prompt: HeartFit Companion (Existing Database)

**Existing-db variant**: unlike `customs_demo_clvs` (EAI/Kafka, schema arrives via message
parsing) or `demo_eai` (schema in DDL text), this sample ships a real, populated
`db.sqlite` — the actual database from a working cardiac-rehab monitoring app. Create the
project by pointing `--db_url=` directly at it:

```bash
genai-logic create --project_name=health_fit --db_url=sqlite:///docs/requirements/health_fit/db.sqlite
```

`genai-logic create` copies this db.sqlite into the new project's `database/` folder — the
copy here in `docs/requirements/health_fit/` remains the untouched original/backup.

Create heartfit_companion with database tables and LogicBank business rules reverse-engineered from HeartFit Companion:

1. SysConfig: Runtime system thresholds for vital boundaries, exertion limits, and absence alerts.
2. Patient: User ID, name, contact info, rollups for active_alert_count, consecutive_absences, and total_sessions_completed.
3. Devices: Paired medical and wearable devices (Pixel Watch, Apple Watch, Omron BP).
4. VitalReading: Patient vitals (BP, HR, Glucose, Weight, source), constraints, derived is_alert_trigger.
5. Alert: Triggered notifications with severity, status, and patient foreign key.
6. ExerciseSession: Duration, Borg RPE, symptoms, derived is_high_exertion.
7. ClassSchedule & Attendance: Schedule times, capacities, attendance tracking, and care team drop-off reactive alerts.
8. SecurityAuditLog: Audit trails for PHI actions and critical clinical alerts.
