# Project Creation Prompt: Student Courses (Existing Database)

**Paste the block below directly into Claude Code CLI** (run from the Manager root — the
directory containing `samples/`). It is self-contained: it names the exact `genai-logic`
command, the exact database path, and what to do after the project is created.

```
Create a new project called students_courses from the existing database at
samples/requirements/students_courses/docs/requirements/students_courses/db.sqlite:

genai-logic create --project_name=students_courses --db_url=sqlite:///samples/requirements/students_courses/docs/requirements/students_courses/db.sqlite

The database has these tables — reverse-engineer LogicBank business rules for tracking
student course enrollment and attendance:

1. sys_config: Runtime system threshold for consecutive-absence alerts.
2. students: name, contact info, rollups for active_alert_count, consecutive_absences, and total_sessions_completed.
3. courses: name, instructor, max_capacity, enrolled_count.
4. class_schedules: scheduled session dates/times per course.
5. attendances: per-student, per-session status ('attended', 'excused', 'absent').
6. alerts: dispatched notifications with type, status, and student foreign key.

Then:
1. Copy samples/requirements/students_courses/docs/requirements/students_courses/ (requirements.md
   and db.sqlite) into students_courses/docs/requirements/students_courses/ (the created project
   already has a docs/requirements/ folder — just add this subfolder).
2. cd into students_courses and say "implement reqs students_courses".
3. After implementation, run the seed/test data step and start the server to confirm it
   comes up cleanly (F5 or `python api_logic_server_run.py`).
```

`genai-logic create` copies `db.sqlite` into the new project's `database/` folder — the copy
here in `docs/requirements/students_courses/` remains the untouched original/backup.

**Note:** `RECREATE_PROMPT.md` (one level up) contains this same recreation, plus evaluator
notes on what to check afterward — read those only *after* the run, since they explain what
the sample is designed to test and would bias the implementation if read first.
